"""Camera "drone" (regia.camera = "drone"): un unico volo continuo, senza stacchi.

Idea: la camera e' un drone. Tra un bersaglio e l'altro plana alla quota di crociera (bassa sulla citta' antica, piu' alta quando
la citta' e' cresciuta); per ogni bersaglio entra da lontano, VELOCE e BASSA (quota 600-900 m -> 80-200 m sul bersaglio, fino a ~250 m/s),
con la prua nel verso di marcia, poi rallenta (20-40 m/s) e gli gira attorno per un arco di 40-90 gradi; poi sale e riparte sul tratto
successivo. Le soste tengono le loro finestre di tempo ESATTE: il drone ARRIVA al bersaglio all'inizio della sosta (t0) e riparte verso
il prossimo in modo da arrivare all'inizio della sua sosta (se il tratto e' lungo, parte negli ultimi secondi della sosta precedente).

Costruzione (tutto in funzione del tempo, a 24 Hz):
  1. riferimento: per ogni bersaglio un'orbita (arco tangente all'ingresso) e per ogni tratto una curva di Hermite X -> A -> E
     (uscita, inizio approccio, ingresso), percorsa con un profilo di velocita' liscio (da v orbita a picco a v orbita);
     la quota e' "metri sul terreno" (DEM) con nodi: uscita -> crociera -> inizio approccio -> orbita;
  2. posizione = riferimento filtrato (gaussiana, sigma crescente finche' velocita', accelerazione e jerk restano nei limiti);
     la gaussiana discreta e' C-infinito: la curva finale e' C2 con limiti verificati numericamente (e da kit/qa.py);
  3. mai sotto il terreno + margine e mai dentro un edificio: la quota minima (DEM + max altezza edifici vivi in quell'anno nelle
     celle vicine + margine) viene alzata con un "deficit" lisciato e iterato, poi la posizione e' filtrata di nuovo;
  4. il punto guardato e' un'altra curva: mescola (pesi lisciati) il bersaglio e un punto "in anticipo" lungo la rotta
     (la posizione fra 3 s, sul terreno), poi gaussiana: guarda avanti, si gira sul bersaglio solo in approccio. Roll sempre zero
     (build_render usa TRACK_TO con up Z).
"""
import json, math, os
import numpy as np
from scipy.ndimage import gaussian_filter1d, maximum_filter1d, maximum_filter
from scipy.interpolate import PchipInterpolator

FPS = 24
DEFAULTS = dict(vmax=250.0, amax=120.0, jmax=200.0, clear=30.0,   # limiti (m/s, m/s^2, m/s^3) e margine sopra terreno/tetti (m)
                v_orbit=30.0, v_orbit_max=45.0, v_leg=105.0, v_avg_cap=165.0,   # orbita (target, tetto); media di tratto desiderata e massima
                arc_min=40.0, arc_max=90.0,                      # arco attorno al bersaglio (gradi)
                open_dist=2000.0, open_alt=1400.0, open_speed=40.0,
                lead_s=3.0, sigma=0.7, sigma_look=0.9)


def cfg_of(R):
    c = dict(DEFAULTS); c.update({k: float(v) for k, v in ((R.get('drone') or {}).items()) if k in DEFAULTS}); return c


def gsmooth(a, sig_samples, order=0):
    """Filtro gaussiano con riflessione DISPARI ai bordi (conserva la pendenza: il drone parte e finisce in moto, senza falsi transitori)."""
    a = np.asarray(a, float); pad = int(min(len(a) - 1, 5 * sig_samples + 2))
    ap = np.pad(a, ((pad, pad),) + ((0, 0),) * (a.ndim - 1), mode='reflect', reflect_type='odd')
    return gaussian_filter1d(ap, sig_samples, axis=0, order=order)[pad:len(ap) - pad]


def smooth01(x):
    x = np.clip(x, 0.0, 1.0); return x * x * (3 - 2 * x)


# ----------------------------------------------------------------------------------------------------------- terreno e ostacoli
def load_dem(ddir):
    p = os.path.join(ddir, 'dem.npz')
    if not os.path.exists(p): return lambda x, y: np.zeros_like(np.asarray(x, float))
    z = np.load(p); D = z['D'].astype(np.float64); gx0, gy0, gc = float(z['x0']), float(z['y0']), float(z['cell'])

    def dem_at(xa, ya):    # stesso campionatore bilineare di build_render.py
        fx = np.clip((np.asarray(xa, float) - gx0) / gc, 0, D.shape[1] - 1.001); fy = np.clip((np.asarray(ya, float) - gy0) / gc, 0, D.shape[0] - 1.001)
        ix = fx.astype(int); iy = fy.astype(int); tx = fx - ix; ty = fy - iy
        return D[iy, ix] * (1 - tx) * (1 - ty) + D[iy, ix + 1] * tx * (1 - ty) + D[iy + 1, ix] * (1 - tx) * ty + D[iy + 1, ix + 1] * tx * ty
    return dem_at


class Obstacles:
    """Quota massima (DEM + altezza) degli edifici vivi a un dato anno, a celle di 50 m (massimo sul vicinato 3x3: raggio >= 50 m)."""
    def __init__(self, ddir, dem, cell=50.0, ybin=25.0):
        self.cell, self.ybin, self.dem = cell, ybin, dem
        items = []   # (x0, x1, y0, y1, top, y_birth, y_death)
        for fn in ('buildings.json', 'hist.json'):
            p = os.path.join(ddir, fn)
            if not os.path.exists(p): continue
            for b in json.load(open(p)):
                r = np.asarray(b['r'], float)
                if len(r) == 0: continue
                cx, cy = float(r[:, 0].mean()), float(r[:, 1].mean())
                items.append((r[:, 0].min(), r[:, 0].max(), r[:, 1].min(), r[:, 1].max(), float(dem(cx, cy)) + float(b.get('h', 8.0)), float(b.get('y', 0)), float(b.get('d', 9999))))
        p = os.path.join(ddir, 'landmarks.json')
        if os.path.exists(p):
            for q in json.load(open(p)).get('parts', []):
                top = q.get('z1', q.get('z0', 0) + q.get('hz', 0) if 'hz' in q else q.get('h', None))
                if top is None: continue
                if 'r' in q and isinstance(q['r'], list): r = np.asarray(q['r'], float)[:, :2]; bb = (r[:, 0].min(), r[:, 0].max(), r[:, 1].min(), r[:, 1].max())
                elif 'cx' in q: rr = q.get('rad', q.get('r0', 5)); bb = (q['cx'] - rr, q['cx'] + rr, q['cy'] - rr, q['cy'] + rr)
                elif 'p0' in q: bb = (min(q['p0'][0], q['p1'][0]), max(q['p0'][0], q['p1'][0]), min(q['p0'][1], q['p1'][1]), max(q['p0'][1], q['p1'][1]))
                else: continue
                cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
                items.append((*bb, float(dem(cx, cy)) + float(top), float(q.get('y', 0)), 9999.0))
        A = np.array(items, float) if items else np.zeros((0, 7))
        self.empty = len(A) == 0
        if self.empty: return
        self.x0, self.y0 = float(A[:, 0].min()) - cell, float(A[:, 2].min()) - cell
        nx = int((A[:, 1].max() - self.x0) / cell) + 3; ny = int((A[:, 3].max() - self.y0) / cell) + 3
        self.shape = (ny, nx)
        ymin = float(max(A[:, 5].min(), -3000)); self.b0 = math.floor(ymin / ybin) * ybin
        nb = int((2030 - self.b0) / ybin) + 1
        ix0 = ((A[:, 0] - self.x0) / cell).astype(int); ix1 = ((A[:, 1] - self.x0) / cell).astype(int)
        iy0 = ((A[:, 2] - self.y0) / cell).astype(int); iy1 = ((A[:, 3] - self.y0) / cell).astype(int)
        self.G = np.full((nb, ny, nx), -1e4, np.float32)
        for k in range(nb):
            yr = self.b0 + k * ybin
            for i in np.nonzero((A[:, 5] <= yr) & (A[:, 6] > yr))[0]:
                g = self.G[k, iy0[i]:iy1[i] + 1, ix0[i]:ix1[i] + 1]; np.maximum(g, A[i, 4], out=g)
            self.G[k] = maximum_filter(self.G[k], size=3)

    def top(self, x, y, year):
        """Quota (assoluta) del tetto piu' alto vicino a (x, y) all'anno dato; -1e4 se niente. Vettoriale (year scalare o array)."""
        x = np.asarray(x, float); out = np.full(x.shape, -1e4)
        if self.empty: return out
        ix = ((x - self.x0) / self.cell).astype(int); iy = ((np.asarray(y, float) - self.y0) / self.cell).astype(int)
        ok = (ix >= 0) & (ix < self.shape[1]) & (iy >= 0) & (iy < self.shape[0])
        k = np.clip(np.round((np.broadcast_to(np.asarray(year, float), x.shape) - self.b0) / self.ybin).astype(int), 0, self.G.shape[0] - 1)
        out[ok] = self.G[k[ok], iy[ok], ix[ok]]
        return out


# ----------------------------------------------------------------------------------------------------------- geometria
def _unit(v):
    n = math.hypot(v[0], v[1]); return (v[0] / n, v[1] / n) if n > 1e-9 else (0.0, 1.0)


def _rot(v, a):
    c, s = math.cos(a), math.sin(a); return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def _angdiff(a, b):
    return abs(math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]))


def _hermite(p0, p1, m0, m1, n=300):
    u = np.linspace(0, 1, n)[:, None]
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return h00 * np.asarray(p0) + h10 * np.asarray(m0) + h01 * np.asarray(p1) + h11 * np.asarray(m1)


def _leg_curve(X, tX, E, dE, app_len):
    """Curva di tratto: X (tangente tX) -> [A = E - app_len*dE] -> E (tangente dE). Ritorna punti (N,2) e lunghezze cumulate."""
    X, E = np.array(X, float), np.array(E, float)
    pts = [X]; tans = [np.array(tX)]
    if app_len > 30:
        pts.append(E - app_len * np.array(dE)); tans.append(np.array(dE))
    pts.append(E); tans.append(np.array(dE))
    seg = []
    for i in range(len(pts) - 1):
        ch = float(np.hypot(*(pts[i + 1] - pts[i]))) + 1e-6
        seg.append(_hermite(pts[i], pts[i + 1], tans[i] * ch, tans[i + 1] * ch)[:-1 if i < len(pts) - 2 else None])
    P = np.vstack(seg); s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    return P, s


def _s5(x):
    x = np.clip(x, 0.0, 1.0); return x ** 3 * (10 - 15 * x + 6 * x * x)


def _speed_profile(Tf, L, v0, v1, ts):
    """Progresso s(t) su [0, Tf]: velocita' nel TEMPO v(t) = lineare(v0, v1) + A * trapezio liscio (salita quintica 30%, discesa 40%:
    picco nella seconda meta'); A si ricava in forma chiusa dalla lunghezza L. Ritorna (s(ts), velocita' di picco)."""
    tau = np.linspace(0, 1, 2001); bump = _s5(tau / 0.30) * _s5((1.0 - tau) / 0.40); base = v0 + (v1 - v0) * tau
    A = (L / Tf - np.trapezoid(base, tau)) / np.trapezoid(bump, tau)
    v = np.maximum(base + A * bump, 3.0)
    S = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(tau))]) * Tf
    k = L / S[-1]; S *= k
    return np.interp(np.clip(ts / Tf, 0, 1), tau, S), float(v.max() * k)


# ----------------------------------------------------------------------------------------------------------- il volo
CARVE = 0.75     # frazione massima della sosta precedente che il drone puo' usare per ripartire verso la successiva


def plan_orbits(stays, start_xy, holds, cfg):
    """Per ogni tappa: punto di ingresso E (tangente alla prua), arco, punto di uscita X e prua d'uscita (scelti per puntare alla tappa dopo)."""
    Xp = (start_xy[0], start_xy[1]); orbs = []; n = len(stays)
    for k, s in enumerate(stays):
        T = (s['x'], s['y']); din = _unit((T[0] - Xp[0], T[1] - Xp[1]))
        hold = max(holds[k], 0.5)
        nxt = (stays[k + 1]['x'], stays[k + 1]['y']) if k < n - 1 else None
        if s.get('static'):
            E = (s['static'][0], s['static'][1]); o = dict(E=E, X=E, th0=0.0, sgn=0, arc=0.0, v=0.0, tX=din, din=din)
        else:
            rho = s['rho']; arc_pref = float(np.clip(cfg['v_orbit'] * hold / rho, math.radians(cfg['arc_min']), math.radians(cfg['arc_max'])))
            hi = min(math.radians(cfg['arc_max']), cfg['v_orbit_max'] * hold / rho); lo = min(math.radians(cfg['arc_min']), hi)
            best = None
            for sgn in (1, -1):
                nvec = (din[1], -din[0]) if sgn == 1 else (-din[1], din[0])      # E = T + rho*n: tangente = din
                for arc in (np.linspace(lo, hi, 6) if hi > lo + 1e-6 else [hi]):
                    th0 = math.atan2(nvec[1], nvec[0]); th1 = th0 + sgn * arc
                    X = (T[0] + rho * math.cos(th1), T[1] + rho * math.sin(th1))
                    tX = _rot(din, sgn * arc)
                    err = _angdiff(tX, _unit((nxt[0] - X[0], nxt[1] - X[1]))) if nxt else (0.0 if sgn == 1 else 0.1)
                    err += 0.15 * abs(arc - min(max(arc_pref, lo), hi))
                    if best is None or err < best[0]: best = (err, sgn, arc, th0, X, tX)
            _, sgn, arc, th0, X, tX = best
            E = (T[0] + rho * math.cos(th0), T[1] + rho * math.sin(th0))
            o = dict(E=E, X=X, th0=th0, sgn=sgn, arc=arc, v=(rho * arc / hold), tX=tX, din=din)
        orbs.append(o); Xp = o['X']
    return orbs


def _dp_select(stays, cfg):
    """Sottoinsieme di tappe di peso massimo (sosta con bersaglio 10 > cartello con bersaglio 4 > cartello senza 1) tale che ogni tratto
    fra tappe consecutive sia percorribile (lunghezza stimata / (pausa + CARVE * sosta precedente) <= v_avg_cap). L'ultima tappa resta sempre."""
    n = len(stays); W = [1000.0 if x.get('prio', 1) >= 9 else {2: 10.0, 1: 4.0, 0: 1.0}.get(x.get('prio', 1), 4.0) + 0.05 * (x['t1'] - x['t0']) for x in stays]

    def ok(a, b):
        L = 1.1 * math.hypot(max(60.0, math.hypot(b['x'] - a['x'], b['y'] - a['y'])) + 0.35 * (a['rho'] + b['rho']), 1.6 * (_alt_of(b) - _alt_of(a, True)))
        return L / max(0.5, (b['t0'] - a['t1']) + CARVE * (a['t1'] - a['t0'])) <= cfg['v_avg_cap']
    dp = [W[j] for j in range(n)]; prv = [-1] * n
    for j in range(n):
        for i in range(j):
            if ok(stays[i], stays[j]) and dp[i] + W[j] > dp[j]: dp[j] = dp[i] + W[j]; prv[j] = i
    # catena migliore che termina nell'ultima tappa; le tappe prima della prima scelta sono tolte
    j = n - 1; keep = []
    while j >= 0: keep.append(j); j = prv[j]
    return [stays[k] for k in reversed(keep)]


def prune(stays, cfg, start_xy):
    """Toglie le tappe che nessun volo credibile raggiunge: se il tratto verso una tappa richiederebbe una media > v_avg_cap anche usando
    CARVE della sosta precedente, si toglie la tappa di priorita' minore (cartello senza bersaglio < cartello con bersaglio < sosta).
    Le soste tolte restano nella story (tempi e didascalie invariati): il drone le sorvola in crociera. Ritorna (tappe, tolte)."""
    st = _dp_select(stays, cfg); dropped = [x for x in stays if x not in st]
    while True:
        orbs = plan_orbits(st, start_xy, [x['t1'] - x['t0'] for x in st], cfg)
        worst = None
        for i in range(1, len(st)):
            a, b = st[i - 1], st[i]
            Tm = max(0.5, (b['t0'] - a['t1']) + CARVE * (a['t1'] - a['t0']))
            req = _leg_len(a, orbs[i - 1], b, orbs[i]) / Tm
            if req > cfg['v_avg_cap'] and (worst is None or req > worst[0]): worst = (req, i)
        if worst is None: return st, dropped
        i = worst[1]; a, b = st[i - 1], st[i]
        cand = [x for x in (a, b) if x.get('prio', 1) < 9]
        if not cand: return st, dropped
        drop = min(cand, key=lambda x: (x.get('prio', 1), x['t1'] - x['t0'], -x['t0']))
        st.remove(drop); dropped.append(drop)


def _alt_of(s, exit_=False):
    return float(s['static'][2]) if s.get('static') else s['alt'] * (1.12 if exit_ else 1.0)


def _leg_len(a, oa, b, ob):
    """Lunghezza stimata (3D) del tratto dall'uscita della tappa a all'ingresso della b."""
    dxy = max(60.0, math.hypot(ob['E'][0] - oa['X'][0], ob['E'][1] - oa['X'][1])); dz = _alt_of(b) - _alt_of(a, True)
    return 1.1 * math.hypot(dxy, 1.6 * dz)


def timing(stays, orbs, start, DUR, cfg):
    """t_dep[k] = istante in cui il drone lascia la tappa k; Tf[k] = durata del tratto che porta alla tappa k (Tf[0]: dall'inizio)."""
    n = len(stays); t_dep = [0.0] * n; Tf = [0.0] * (n + 1); Tf[0] = stays[0]['t0']
    for k in range(n):
        if k == n - 1: t_dep[k] = max(DUR + 1.0, stays[k]['t0'] + 1.0); break
        a, b = stays[k], stays[k + 1]
        Lc = _leg_len(a, orbs[k], b, orbs[k + 1])
        gap = b['t0'] - a['t1']; need = max(3.0, Lc / cfg['v_leg'])
        Tk = min(max(gap, need), gap + CARVE * (a['t1'] - a['t0']), b['t0'] - a['t0'] - 2.0)
        Tf[k + 1] = Tk; t_dep[k] = b['t0'] - Tk
    return t_dep, Tf


def fly(stays, DUR, year_at, dem, obst, cruise_fn, start, cfg):
    """stays: [{t0,t1,x,y,tzo,d,el,kind('bld'|'area'|'city'),static(opz.: (x,y,z assoluta)) }] in ordine di tempo.
    start: (x, y, quota m sul terreno, velocita' iniziale) del drone a t=0. Ritorna (ts, P(N,3), L(N,3), info)."""
    ts = np.arange(0.0, DUR + 1e-9, 1.0 / FPS)
    # --- dimensioni dell'orbita
    for s in stays:
        el = math.radians(s['el']); d = float(s['d'])
        if s['kind'] == 'bld':
            alt = float(np.clip(d * math.sin(el), 80, 200)); dz = alt - float(s.get('tzo', 0.0)); rho = math.sqrt(max(d * d - dz * dz, (0.5 * d) ** 2))
        else:   # aree e citta': stessa elevazione di vista, quota limitata (a 3500 m la citta' si legge ancora, oltre no)
            rho = min(d * math.cos(el), cfg.get('rho_max', 600.0)); alt = float(np.clip(math.sqrt(max(d * d - rho * rho, 1.0)), 150, 3500))
        s['alt'] = alt; s['rho'] = rho
    stays, dropped = prune(stays, cfg, start[:2]); n = len(stays)
    # --- tempi: il drone arriva a t0; riparte in tempo per arrivare a t0 del prossimo
    orbs = plan_orbits(stays, start[:2], [st_['t1'] - st_['t0'] for st_ in stays], cfg)
    t_dep, Tf = timing(stays, orbs, start, DUR, cfg)
    # --- geometria: due passate (la durata dell'orbita dipende dal tratto, che dipende dall'orbita)
    for _ in range(2):
        orbs = plan_orbits(stays, start[:2], [(t_dep[k] - stays[k]['t0']) if k < n - 1 else (DUR - stays[k]['t0']) for k in range(n)], cfg)
        t_dep, Tf = timing(stays, orbs, start, DUR, cfg)
    orbs = plan_orbits(stays, start[:2], [(t_dep[k] - stays[k]['t0']) if k < n - 1 else (DUR - stays[k]['t0']) for k in range(n)], cfg)
    # --- campiona il riferimento
    Pref = np.zeros((len(ts), 3)); AGL = np.zeros(len(ts)); tdep_prev = 0.0; Xprev = (start[0], start[1]); tprev = None; vprev = start[3]; aprev = start[2]
    yrs = np.array([year_at(t) for t in ts])
    leg_info = []
    for k, s in enumerate(stays):
        o = orbs[k]; ta, tb = tdep_prev, s['t0']
        m = (ts >= ta - 1e-9) & (ts < tb)
        Lcurve_start = Xprev
        din = o['din']; tX0 = tprev if tprev is not None else din
        chord = math.hypot(o['E'][0] - Xprev[0], o['E'][1] - Xprev[1])
        app = float(np.clip(0.45 * chord, 0, 1600)) if chord > 450 else 0.0
        C, cs = _leg_curve(Xprev, tX0, o['E'], din, app); Lc = float(cs[-1])
        zc = float(cruise_fn(year_at(0.5 * (ta + tb)))); a_E = s['alt'] if not s.get('static') else float(s['static'][2])
        a_X = aprev
        zc_e = max(min(zc, max(a_X, a_E) + 0.30 * Lc), min(a_X, a_E))
        zA = float(np.clip(1.4 * zc, 450, 900)); zA_e = max(min(zA, a_E + 0.45 * app), a_E) if app > 0 else a_E
        s2 = Lc - app; s1 = min(0.3 * max(s2, 0), 900.0)
        nodes_s = [0.0]; nodes_z = [a_X]
        if s2 - s1 > 40 and s1 > 40: nodes_s.append(s1); nodes_z.append(zc_e)
        if app > 0: nodes_s.append(s2); nodes_z.append(max(zA_e, a_E))
        nodes_s.append(Lc); nodes_z.append(a_E)
        zf = PchipInterpolator(nodes_s, nodes_z)
        v_end = o['v'] if not s.get('static') else 0.0
        sp, vpk = _speed_profile(max(tb - ta, 0.5), Lc, vprev, v_end, ts[m] - ta)
        Pref[m, 0] = np.interp(sp, cs, C[:, 0]); Pref[m, 1] = np.interp(sp, cs, C[:, 1]); AGL[m] = zf(sp)
        leg_info.append(dict(k=k, t_a=ta, t_b=tb, L=Lc, app=app, vpk=vpk, v0=vprev, v1=v_end))
        # orbita
        te = t_dep[k] if k < n - 1 else DUR + 1.0
        m = (ts >= tb - 1e-9) & (ts < te if k < n - 1 else ts <= DUR + 1e-9)
        hold_k = (te - tb) if k < n - 1 else (DUR - tb)
        u = np.clip((ts[m] - tb) / max(hold_k, 1e-6), 0.0, 1.0)
        if s.get('static'):
            Pref[m, 0], Pref[m, 1], AGL[m] = o['E'][0], o['E'][1], a_E
        else:
            th = o['th0'] + o['sgn'] * o['arc'] * u
            Pref[m, 0] = s['x'] + s['rho'] * np.cos(th); Pref[m, 1] = s['y'] + s['rho'] * np.sin(th)
            AGL[m] = s['alt'] * (1.0 + 0.12 * smooth01(u))
        Xprev, tprev, vprev = o['X'], o['tX'], v_end
        aprev = s['alt'] * 1.12 if not s.get('static') else a_E
        tdep_prev = t_dep[k] if k < n - 1 else DUR
    # --- tratto 0 prima del primo ingresso: gia' incluso (ta = 0). Quota assoluta
    Pref[:, 2] = AGL + dem(Pref[:, 0], Pref[:, 1])
    # --- filtro + limiti + sfondamenti
    best = None
    for sig in (cfg['sigma'], 0.85, 1.0, 1.2):     # sigma piccolo: l'arrivo resta puntuale; i limiti si rispettano col progetto dei tempi (prune, CARVE)
        P = gsmooth(Pref, sig * FPS)
        for _ in range(14):
            fl = np.maximum(dem(P[:, 0], P[:, 1]), obst.top(P[:, 0], P[:, 1], yrs)) + cfg['clear']
            deficit = np.maximum(0.0, fl - P[:, 2])
            if deficit.max() < 0.5: break
            spread = gaussian_filter1d(maximum_filter1d(deficit, size=int(2.5 * FPS)), 1.0 * FPS, mode='nearest')
            Pref[:, 2] += np.maximum(spread, deficit * 0.0) * 1.05 + 0.5 * (deficit > 0.5)
            P = gsmooth(Pref, sig * FPS)
        v, a, j = kin(P)
        ok = v.max() <= cfg['vmax'] * 1.02 and a.max() <= cfg['amax'] and j.max() <= cfg['jmax']
        score = max(a.max() / cfg['amax'], j.max() / cfg['jmax'])
        if best is None or score < best[0]: best = (score, sig, P)
        if ok: best = (score, sig, P); break
    _, sig, P = best
    # --- punto guardato
    V = np.gradient(P, 1.0 / FPS, axis=0); hd = V[:, :2] / np.maximum(np.hypot(V[:, 0], V[:, 1]), 1e-6)[:, None]
    tau = int(cfg['lead_s'] * FPS); idx = np.clip(np.arange(len(ts)) + tau, 0, len(ts) - 1)
    Q = P[idx].copy(); dq = Q[:, :2] - P[:, :2]; ln = np.hypot(dq[:, 0], dq[:, 1])
    short = ln < 150.0; Q[short, :2] = P[short, :2] + hd[short] * 150.0
    Q[:, 2] = dem(Q[:, 0], Q[:, 1])
    W = np.zeros(len(ts)); LT = np.zeros((len(ts), 3))
    for k, s in enumerate(stays):
        te = t_dep[k] if k < n - 1 else DUR + 5.0
        r_in = min(3.5, 0.7 * Tf[k]); r_out = min(2.5, 0.6 * Tf[k + 1]) if k < n - 1 else 0.0
        w = smooth01((ts - (s['t0'] - r_in)) / max(r_in, 1e-3)) * (1.0 - smooth01((ts - te) / max(r_out, 1e-3)))
        tz = dem(s['x'], s['y']) + float(s.get('tzo', 0.0))
        LT += w[:, None] * np.array([s['x'], s['y'], tz]); W += w
    Wc = np.minimum(W, 1.0); L = LT / np.maximum(W, 1.0)[:, None] + (1.0 - Wc)[:, None] * Q
    L = gsmooth(L, cfg['sigma_look'] * FPS)
    info = dict(sigma=sig, stays=stays, dropped=dropped, legs=leg_info, t_dep=t_dep, Tf=Tf, orbits=[dict(sgn=o['sgn'], arc_deg=math.degrees(o['arc']), v=o['v']) for o in orbs])
    return ts, P, L, info


def kin(P, dt=1.0 / FPS):
    """Velocita', accelerazione e jerk (moduli) di una traiettoria campionata: Savitzky-Golay (finestra 21 campioni = 0,9 s, polinomio di
    grado 4: esatto sui polinomi, non perde nulla sul DC e non amplifica l'arrotondamento delle chiavi a 0,01 m)."""
    from scipy.signal import savgol_filter
    D = lambda k: np.linalg.norm(savgol_filter(np.asarray(P, float), 21, 4, deriv=k, delta=dt, axis=0, mode='interp'), axis=1)
    return D(1), D(2), D(3)


def stats_of(ts, P, L, dem, obst, year_at):
    v, a, j = kin(P, float(ts[1] - ts[0]))
    yrs = np.array([year_at(t) for t in ts])
    ground = dem(P[:, 0], P[:, 1]); roof = obst.top(P[:, 0], P[:, 1], yrs)
    clr = P[:, 2] - np.maximum(ground, roof)
    return dict(vmax=float(v.max()), amax=float(a.max()), jmax=float(j.max()), clear_min=float(clr.min()), clear_ground_min=float((P[:, 2] - ground).min()))


def cam_keys(ts, P, L, mm=35):
    return [[round(float(t), 3), [round(float(p[0]), 2), round(float(p[1]), 2), round(float(p[2]), 2)],
             [round(float(q[0]), 2), round(float(q[1]), 2), round(float(q[2]), 2)], mm] for t, p, q in zip(ts, P, L)]
