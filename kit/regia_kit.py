"""Regia automatica generica (generalizza regia_copenhagen.py).

Input
  story.json  regia.{duration, night, open, soste, rmin, rmax, music, anchors, anchors_auto, b_start, night_t,
                     night_shots, wide_every, az}
  DATA        landmarks.json (bersagli per prefisso del nome, come lmc()), buildings.json + hist.json (attivita' per
              anno ed estensione della citta'), fires.json / landmarks.fires (bersagli "fire:<nome>")
  musica      kit/music/<regia.music>.json (modello: b_start, night_t, slots con ruoli hook/drop/release/climax/...)

Bersagli di una sosta ("target")
  "<prefisso>"            parti di landmarks.json il cui nome inizia col prefisso (mediana dei centri, altezza max)
  "fire:<nome>"           incendio di fires.json / landmarks.fires / story.history.fires (centro del poligono)
  "area:[lat,lon,raggio]" un cerchio sulla mappa
  "water:<nome>"          fase di story.history.water (anche senza prefisso, se nessun landmark ha quel nome): rettangolo che la contiene
  (le inquadrature "wide" hanno un tetto: estensione del bersaglio + margine, al massimo WIDE_MAX = 3500 m)
  "xy:[x,y(,raggio)]"     punto in metri locali (estensione, utile per fixture e casi speciali)

Sosta: {"y0","y1","dur","caption":"Titolo (data)","target","shot":"close|medium|wide|top","fx","force"?,"role"?,
        "az"?: gradi o [az0, az1], "cam"?: {"d","el","az":[a0,a1],"mm"}}
  - "force" (0-10) o, se manca, dalla "fx" (boom/fire/battle/quake = 8, crowd/firework = 6, ...); conta per le ancore.
  - "role": aggancia la sosta a quel ruolo musicale (es. "climax").

Ancore musicali (FIXED)
  Automatiche: le soste piu' forti vanno sui punti forti della musica (programmazione dinamica che rispetta l'ordine
  cronologico e i limiti di velocita' rmin/rmax). La sosta del climax e' posta in modo da coprire il cambio di traccia.
  Override: regia.anchors = [{"t": 184.0 | "drop" | "A:184" | "B:25", "year": 1852.0} oppure {"t": ..., "sosta":
  "<inizio della didascalia>"}]; regia.anchors_auto=false disattiva le automatiche.

Pacing "story" (regia.pacing, default "buildings" = comportamento storico)
  Il contatore SI FERMA su ogni cartello (story.montaggio.cards[{y,title,lines,hold_s=5,target?,shot?}], e le soste contano come
  cartelli) a HOLD_RATE = 0,2 anni/s e CORRE tra un cartello e l'altro (tetto SPRINT_CAP = 25 anni/s). Niente ancore musicali,
  night=false di default; dopo il titolo c'e' una pausa regia.open.story_lead (3,4 s). Il budget di tempo e' regia.duration.
  regia.camera = "continuous": un solo piano sequenza (PCHIP) per i waypoint dei bersagli di cartelli/soste, senza stacchi.
  montaggio.recap {seconds}: negli ultimi secondi (prima di CTA + fonti) un punto di vista alto fisso, anni start->end.
  Lo schedule guadagna: cards[{t_in,t_out,y,title,lines,chapter,src}], title_t, end_plan{recap,cta,sources}, pacing.

Output
  schedule_<slug>.json, schedule_<slug>_night.json (radice del repo, o --out), cities/<slug>/regia.txt e regia.png.

Uso: python kit/regia_kit.py <slug | story.json> [--data DIR] [--out DIR] [--regia-dir DIR] [--music NAME|file.json]
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit.geo import ROOT, load_story, Proj, data_dir as story_data_dir   # noqa: E402

FPS = 24
HOLD_RATE = 0.2       # anni/s sui cartelli (pacing story)
SPRINT_CAP = 25.0     # anni/s massimi tra i cartelli (pacing story)
FX_FORCE = {'boom': 8, 'fire': 8, 'battle': 8, 'quake': 8, 'crash': 7, 'crowd': 6, 'firework': 6, 'rocket': 6, 'peal': 5,
            'bell': 5, 'horn': 5, 'water': 4, 'hammer': 4, 'whoosh': 4, 'ding': 3, 'click': 3, 'city_hum': 3}
DISASTER_FX = {'boom', 'fire', 'battle', 'quake', 'crash'}
DISASTER_WORDS = ('FIRE', 'BOMB', 'burns', 'siege', 'Siege', 'sack', 'Sack', 'earthquake', 'Earthquake', 'flood', 'Flood',
                  'razes', 'destroy', 'war', 'War', 'plague', 'Plague', 'blitz', 'Blitz')
SHOT = {   # moltiplicatore di distanza, elevazione (gradi)
    'close': (0.72, 20), 'medium': (1.0, 24), 'wide': (1.65, 30), 'top': (1.25, 62)}
STRONG = 6.0          # forza minima di un "evento forte"
WIDE_MAX = 3500.0     # m: distanza massima di un'inquadratura 'wide' (oltre, la citta' non si legge)


def ease(u):
    return u * u * (3 - 2 * u)


def fmt_t(t):
    return f'{int(t // 60)}:{t % 60:04.1f}'


# ======================================================================================================== dati
class Data:
    def __init__(self, story, ddir):
        self.story, self.dir = story, ddir
        self.proj = Proj.of(story)
        p = os.path.join(ddir, 'landmarks.json')
        self.LM = json.load(open(p)) if os.path.exists(p) else {'parts': []}
        fires = []
        p = os.path.join(ddir, 'fires.json')
        if os.path.exists(p): fires += json.load(open(p))
        fires += self.LM.get('fires', []) or []
        for f in (story.get('history', {}) or {}).get('fires', []) or []:
            if f.get('ring'): fires.append({'name': f['name'], 'y': f.get('y'), 'poly': self.proj.ring(f['ring'])})
        self.fires = fires
        B = json.load(open(os.path.join(ddir, 'buildings.json')))
        hp = os.path.join(ddir, 'hist.json')
        H = json.load(open(hp)) if os.path.exists(hp) else []
        self.has_hist = os.path.exists(hp)
        y = np.array([o['y'] for o in B] + [o['y'] for o in H], float)
        d = np.array([9999.0] * len(B) + [o.get('d', 9999) for o in H], float)
        self.cx = np.array([sum(q[0] for q in o['r']) / len(o['r']) for o in B + H])
        self.cy = np.array([sum(q[1] for q in o['r']) / len(o['r']) for o in B + H])
        self.by, self.bd = y, d
        ymin = min(float(np.nanmin(y)) if len(y) else 0, float(story['city'].get('start_year', 0)))
        self.OFF = int(max(0, -math.floor(ymin))) + 10
        act = np.zeros(2030 + self.OFF)
        yi = np.floor(y).astype(int) + self.OFF
        np.add.at(act, np.clip(yi, 0, len(act) - 1), 1.0)
        dd = d[d < 2027]
        np.add.at(act, np.clip(np.floor(dd).astype(int) + self.OFF, 0, len(act) - 1), 0.6)
        self.act = np.convolve(act, np.ones(5) / 5, 'same')     # lisciata su 5 anni (anni tondi dei catasti)
        del B, H

    def act_at(self, years):
        return self.act[np.clip(np.asarray(years, int) + self.OFF, 0, len(self.act) - 1)]

    def lmc(self, name):
        ps = [p for p in self.LM['parts'] if p['name'].startswith(name)]
        if not ps: return None

        def ctr(p):
            if 'cx' in p: return p['cx'], p['cy']
            r = p.get('r') or ([p['p0'], p['p1']] if 'p0' in p else [[0, 0]])
            return sum(q[0] for q in r) / len(r), sum(q[1] for q in r) / len(r)
        cs = np.array([ctr(p) for p in ps])
        x, y = float(np.median(cs[:, 0])), float(np.median(cs[:, 1]))
        h = max(p.get('z1', p.get('z0', 0) + p.get('hz', 0)) for p in ps)
        pts = []
        for p in ps:
            if 'r' in p and isinstance(p['r'], list): pts += [q[:2] for q in p['r']]
            elif 'cx' in p:
                rr = p.get('rad', p.get('r0', 5)); pts += [[p['cx'] - rr, p['cy'] - rr], [p['cx'] + rr, p['cy'] + rr]]
            elif 'p0' in p: pts += [p['p0'][:2], p['p1'][:2]]
        pts = np.array(pts) if pts else cs
        R = float(np.percentile(np.hypot(pts[:, 0] - x, pts[:, 1] - y), 85))
        born = min(p.get('y', 9999) for p in ps)
        return {'x': x, 'y': y, 'z': min(40.0, h * 0.35), 'h': float(h), 'R': R, 'born': born, 'kind': 'landmark', 'name': name}

    def target(self, spec):
        """Bersaglio -> {x,y,z,h,R} o None."""
        if spec is None: return None
        if isinstance(spec, str) and spec.startswith('fire:'):
            nm = spec[5:].strip().lower()
            fs = [f for f in self.fires if f.get('name', '').lower() == nm] or \
                 [f for f in self.fires if f.get('name', '').lower().startswith(nm)] or \
                 [f for f in self.fires if nm in f.get('name', '').lower()]
            if not fs: return None
            P = np.array(fs[0].get('poly') or fs[0].get('r'))
            x, y = float(P[:, 0].mean()), float(P[:, 1].mean())
            R = float(np.percentile(np.hypot(P[:, 0] - x, P[:, 1] - y), 85))
            return {'x': x, 'y': y, 'z': 0.0, 'h': 0.0, 'R': R, 'kind': 'fire', 'name': fs[0]['name']}
        if isinstance(spec, str) and spec.startswith(('area:', 'xy:')):
            v = json.loads(spec.split(':', 1)[1])
            if spec.startswith('area:'):
                x, y = self.proj.L(v[0], v[1]); r = float(v[2]) if len(v) > 2 else 300.0
            else:
                x, y = float(v[0]), float(v[1]); r = float(v[2]) if len(v) > 2 else 300.0
            return {'x': x, 'y': y, 'z': 0.0, 'h': 0.0, 'R': r, 'kind': 'area', 'name': spec}
        if isinstance(spec, (list, tuple)) and len(spec) >= 2:     # [lat, lon, raggio]
            return self.target('area:' + json.dumps(list(spec)))
        if isinstance(spec, str) and spec.startswith('water:'):
            return self.water(spec[6:].strip())
        return self.lmc(spec) or (self.water(spec) if isinstance(spec, str) else None)

    def water(self, name):
        """Fase d'acqua/terra di story.history.water per nome (prefisso): centro e raggio dal rettangolo che la contiene."""
        nm = name.lower()
        ws = [w for w in (self.story.get('history', {}) or {}).get('water', []) or [] if w.get('ring')]
        ws = [w for w in ws if w.get('name', '').lower().startswith(nm)] or [w for w in ws if nm in w.get('name', '').lower()]
        if not ws: return None
        P = np.array([q for w in ws for q in self.proj.ring(w['ring'])])
        (x0, y0), (x1, y1) = P.min(0), P.max(0)
        return {'x': float(x0 + x1) / 2, 'y': float(y0 + y1) / 2, 'z': 0.0, 'h': 0.0, 'R': float(math.hypot(x1 - x0, y1 - y0)) / 2,
                'kind': 'water', 'name': ws[0].get('name', name)}

    def extent(self, y, focus=None):
        m = (self.by <= y) & (self.bd > y)
        if m.sum() < 30:
            return ((focus[0], focus[1]) if focus else (0.0, 0.0)), 120.0
        mx, my = float(np.median(self.cx[m])), float(np.median(self.cy[m]))
        r = float(np.percentile(np.hypot(self.cx[m] - mx, self.cy[m] - my), 85))
        if r < 400 and focus is not None:   # primi secoli: nel quadro sia il borgo sia il punto di fondazione
            d_ = math.hypot(mx - focus[0], my - focus[1])
            if d_ < 3000:
                mx, my = (mx + focus[0]) / 2, (my + focus[1]) / 2; r = max(r, d_ / 2 + 60)
        return (mx, my), float(max(140.0, r))


# ======================================================================================================== musica
def load_music(name):
    if name is None: return None
    p = name if str(name).endswith('.json') else os.path.join(ROOT, 'kit', 'music', f'{name}.json')
    if not os.path.exists(p): return None
    return json.load(open(p))


def sosta_force(s):
    if 'force' in s: return float(s['force'])
    f = FX_FORCE.get(s.get('fx', ''), 4.0)
    return float(f + max(0.0, min(2.0, (s['dur'] - 6.0) * 0.25)))


def sosta_is_disaster(s):
    return (s.get('fx') in DISASTER_FX or str(s.get('target', '')).startswith('fire:')
            or any(w in s.get('caption', '') for w in DISASTER_WORDS))


# ======================================================================================================== timeline
class Timeline:
    def __init__(self, data, rmin, rmax, warn):
        self.D, self.rmin, self.rmax, self.warn = data, rmin, rmax, warn

    def alloc(self, y0, y1, T):
        ys = np.arange(math.floor(y0), math.ceil(y1))
        if len(ys) == 0 or y1 - y0 < 1e-6: return [(y0, 0.0), (y1, T)]
        frac = np.array([min(y1, y + 1) - max(y0, y) for y in ys])
        w = (self.D.act_at(ys) + 3.0) ** 0.85 * frac
        lo, hi = frac / self.rmax, frac / self.rmin
        s = np.clip(w / w.sum() * T, lo, hi)
        for _ in range(60):
            err = T - s.sum()
            if abs(err) < 1e-6: break
            free = (s < hi - 1e-9) if err > 0 else (s > lo + 1e-9)
            if not free.any(): break
            s[free] += err * w[free] / w[free].sum(); s = np.clip(s, lo, hi)
        if abs(T - s.sum()) > 0.05: s *= T / s.sum()
        pts = [(y0, 0.0)]; acc = 0.0
        for y, sv in zip(ys, s):
            acc += sv; pts.append((min(y1, y + 1), acc))
        return pts

    def build(self, FIXED, SOSTE, tail):
        """FIXED [(t, anno)], SOSTE ordinate per y0 (dict). Ritorna YEARS [(t, anno)], SOSTA_T [(t0, t1, sosta)]."""
        YEARS, SOSTA_T = [], []
        for (ta, ya), (tb, yb) in zip(FIXED, FIXED[1:]):
            if yb < ya or tb - ta < 0.01 or ya == yb:
                for k in range(0, 21):
                    u = k / 20; YEARS.append((ta + (tb - ta) * u, ya + (yb - ya) * ease(u)))
                continue
            ss = [s for s in SOSTE if ya <= s['y0'] < yb]
            T_free = (tb - ta) - sum(s['dur'] for s in ss)
            pieces = []; cur = ya
            for s in ss: pieces.append((cur, s['y0'])); cur = s['y1']
            pieces.append((cur, yb))
            yrs, own = [], []
            for i, (p0, p1) in enumerate(pieces):
                for y in np.arange(math.floor(p0), math.ceil(p1)):
                    fr_ = min(p1, y + 1) - max(p0, y)
                    if fr_ > 1e-6: yrs.append((int(y), fr_)); own.append(i)
            if T_free < 0:
                self.warn(f'soste piu\' lunghe dello spazio tra le ancore {fmt_t(ta)} ({ya:.1f}) e {fmt_t(tb)} ({yb:.1f}): '
                          f'{-T_free:.1f} s di troppo')
                T_free = 0.0
            if yrs:
                w = np.array([(self.D.act_at([y])[0] + 3.0) ** 0.85 * f for y, f in yrs]); fr = np.array([f for _, f in yrs])
                lo, hi = fr / self.rmax, fr / self.rmin; sv = np.clip(w / w.sum() * T_free, lo, hi)
                for _ in range(80):
                    err = T_free - sv.sum()
                    if abs(err) < 1e-6: break
                    free = (sv < hi - 1e-9) if err > 0 else (sv > lo + 1e-9)
                    if not free.any(): break
                    sv[free] += err * w[free] / w[free].sum(); sv = np.clip(sv, lo, hi)
                if abs(T_free - sv.sum()) > 0.05:
                    k = T_free / max(1e-9, sv.sum())
                    self.warn(f'velocita\' fuori limiti tra {fmt_t(ta)} ({ya:.1f}) e {fmt_t(tb)} ({yb:.1f}): '
                              f'servirebbero {sum(f for _, f in yrs) / max(T_free, 1e-9):.2f} anni/s (limiti {self.rmin}-{self.rmax}), scala {k:.2f}')
                    sv = sv * k
                Ts = [float(sv[np.array(own) == i].sum()) for i in range(len(pieces))]
            else:
                Ts = [0.0] * len(pieces)
                if T_free > 0.05 and len(ss):   # niente anni liberi: il tempo avanzato va alle soste (nessun buco)
                    self.warn(f'{T_free:.1f} s senza anni liberi tra {fmt_t(ta)} e {fmt_t(tb)}: allungo l\'ultima sosta')
                    ss[-1] = dict(ss[-1], dur=ss[-1]['dur'] + T_free)
            t = ta
            for i, (p0, p1) in enumerate(pieces):
                for yv, dt in (self.alloc(p0, p1, Ts[i]) if p1 > p0 else [(p0, 0.0)]):
                    YEARS.append((t + dt, yv))
                t += Ts[i]
                if i < len(ss):
                    s = ss[i]; SOSTA_T.append((t, t + s['dur'], s))
                    for k in range(1, 11):
                        u = k / 10; YEARS.append((t + s['dur'] * u, s['y0'] + (s['y1'] - s['y0']) * u))
                    t += s['dur']
        YEARS += tail
        YEARS = sorted({round(float(t), 3): (round(float(t), 3), round(float(y), 4)) for t, y in YEARS}.values())
        return YEARS, SOSTA_T


def end_plan_of(story, story_mode):
    """Secondi di recap / CTA / carta delle fonti in coda al video (pacing story). Stessa regola per regia_kit e kit_city."""
    MO = story.get('montaggio', {}) or {}
    rc = MO.get('recap'); recap = float(rc.get('seconds', 20) if isinstance(rc, dict) else (20 if rc else 0)) if rc else 0.0
    cta = 4.5 if MO.get('cta') else 0.0
    sc = MO.get('sources_card')
    on = bool(sc) if sc is not None else story_mode
    src = float(sc.get('seconds', 8.0) if isinstance(sc, dict) else 8.0) if on else 0.0
    return recap, cta, src


def build_story(SOSTE, FIXED, title_t, y_start, end_t, tail, lead, warn):
    """Pacing story: rewind fino a y_start, pausa 'lead', poi per ogni voce (cartello o sosta, per anno) corsa + sosta a 0,2 anni/s.
    Ritorna YEARS, SOSTA_T come Timeline.build. La velocita' di corsa e' ricavata dal tempo libero (tetto 25 anni/s, con avviso)."""
    YEARS, SOSTA_T = [], []
    for (ta, ya), (tb, yb) in zip(FIXED[:2], FIXED[1:3]):
        for k in range(0, 21):
            u = k / 20; YEARS.append((ta + (tb - ta) * u, ya + (yb - ya) * ease(u)))
    t0 = title_t + lead; YEARS.append((t0, y_start))
    items = []; cur = y_start
    for s in SOSTE:
        y0 = max(float(s['y0']), cur); y1 = max(y0 + (float(s['y1']) - float(s['y0'])), y0 + HOLD_RATE * s['dur'])   # anche le soste scorrono almeno a 0,2 anni/s
        items.append((y0, y1, s)); cur = y1
    hold_t = sum(s['dur'] for _, _, s in items)
    free = end_t - t0 - hold_t
    total = sum(max(0.0, y0 - c) for (y0, _, _), c in zip(items, [y_start] + [i[1] for i in items[:-1]])) + max(0.0, 2026.0 - cur)
    if free <= 0.5:
        warn(f'pacing story: i cartelli ({hold_t:.0f} s) riempiono il tempo ({end_t - t0:.0f} s): alza regia.duration o togli cartelli')
        free = max(0.5, free)
    rate = total / free
    if rate > SPRINT_CAP * 1.001:
        warn(f'pacing story: la corsa tra i cartelli servirebbe {rate:.1f} anni/s (tetto {SPRINT_CAP:g}): alza regia.duration o accorcia hold_s')
    t = t0; cur = y_start
    for y0, y1, s in items:
        if y0 - cur > 1e-6:
            dt = (y0 - cur) / rate; YEARS += [(t, cur), (t + dt, y0)]; t += dt
        s['y0'], s['y1'] = y0, y1
        SOSTA_T.append((t, t + s['dur'], s))
        YEARS += [(t, y0), (t + s['dur'], y1)]; t += s['dur']; cur = y1
    if 2026.0 - cur > 1e-6:
        dt = (2026.0 - cur) / rate; YEARS += [(t, cur), (t + dt, 2026.0)]; t += dt
    YEARS.append((max(t, end_t), 2026.0))
    YEARS += tail
    YEARS = sorted({round(float(a), 3): (round(float(a), 3), round(float(b), 4)) for a, b in YEARS}.values())
    return YEARS, SOSTA_T


def continuous_cam(wps, t_end, dt=0.25):
    """Piano sequenza: waypoint (t, (tx,ty,tz), d, el, az, mm) -> chiavi camera [t, pos, tgt, mm] con PCHIP (come regia_sevilla.py)."""
    from scipy.interpolate import PchipInterpolator
    W = []
    for w in sorted(wps, key=lambda w: w[0]):
        if not W or w[0] > W[-1][0] + 0.2: W.append(w)
    T = np.array([w[0] for w in W]); P, G, M = [], [], []
    for _, tg, d, el, az, mm in W:
        e, a = math.radians(el), math.radians(az)
        P.append((tg[0] + d * math.cos(e) * math.sin(a), tg[1] + d * math.cos(e) * math.cos(a), tg[2] + d * math.sin(e)))
        G.append(tuple(tg)); M.append(mm)
    fp, fg, fm = PchipInterpolator(T, np.array(P), axis=0), PchipInterpolator(T, np.array(G), axis=0), PchipInterpolator(T, np.array(M))
    out = []
    for tt in list(np.arange(T[0], T[-1], dt)) + [T[-1]]:
        out.append([round(float(tt), 3), [round(float(v), 1) for v in fp(tt)], [round(float(v), 1) for v in fg(tt)], round(float(fm(tt)), 1)])
    return out


def make_year_at(YEARS):
    T = np.array([a for a, _ in YEARS]); Y = np.array([b for _, b in YEARS])

    def year_at(t):
        return float(np.interp(t, T, Y))
    return year_at


# ======================================================================================================== ancore
def parse_t(v, music, b_start):
    """Tempo di un'ancora: numero, ruolo musicale, "A:184.0" o "B:25.0"."""
    if isinstance(v, (int, float)): return float(v)
    v = str(v).strip()
    if v[:2] in ('A:', 'a:'): return float(v[2:])
    if v[:2] in ('B:', 'b:'): return b_start + float(v[2:])
    if music:
        for s in music.get('slots', []):
            if s['role'] == v: return float(s['t'])
    try: return float(v)
    except ValueError: return None


def climax_t(t, dur, b_start):
    """La sosta del climax inizia sulla sfumatura di A e finisce ~2 s dopo l'ingresso di B (copre il cambio)."""
    if not b_start: return t
    return min(b_start - 1.0, max(t - 3.0, b_start + 2.0 - dur))


def find_sosta(SOSTE, key):
    k = str(key).lower()
    for s in SOSTE:
        if s['caption'].lower().startswith(k): return s
    for s in SOSTE:
        if k in s['caption'].lower(): return s
    return None


def auto_anchors(slots, cands, fixed, t_start, y_start, t_end, y_end, rmin, rmax, b_start):
    """Sceglie per ogni slot musicale al piu' una candidata (sosta) rispettando l'ordine cronologico e i limiti di
    velocita' tra ancore consecutive. fixed = ancore obbligatorie [(t, anno)]. Ritorna [(t, anno, slot, sosta)]."""
    # durata soste tra due anni: serve alla verifica di fattibilita'
    def seg_ok(ta, ya, tb, yb):
        if tb <= ta or yb <= ya: return -1e6
        ss = [c for c in cands if ya <= c['y0'] < yb]
        T = (tb - ta) - sum(c['dur'] for c in ss)
        Y = (yb - ya) - sum(min(c['y1'], yb) - c['y0'] for c in ss)
        if T < 0.5: return -1e6
        if Y <= 0: return -1e6 if T > 2 else 0.0
        r = Y / T
        if r > rmax * 1.001 or r < rmin * 0.999: return -1e6
        return -1.5 * abs(math.log(r / glob_r))
    tot_T = (t_end - t_start) - sum(c['dur'] for c in cands)
    tot_Y = (y_end - y_start) - sum(c['y1'] - c['y0'] for c in cands)
    glob_r = max(1e-3, tot_Y / max(1.0, tot_T))
    fmax = max((c['_force'] for c in cands if not c.get('_pinned')), default=0.0)
    # elementi del cammino in ordine di tempo
    elems = [('fix', t, y, None) for t, y in fixed] + [('slot', s['t'], None, s) for s in slots]
    elems.sort(key=lambda e: e[1])
    # stati: (t, y, ...) -> (punteggio, cammino)
    states = {(t_start, y_start): (0.0, [])}
    for kind, t, y, slot in elems:
        new = {}
        if kind == 'fix':
            for (ta, ya), (sc, path) in states.items():
                v = sc + seg_ok(ta, ya, t, y)
                if (t, y) not in new or v > new[(t, y)][0]: new[(t, y)] = (v, path)
            states = new; continue
        new = dict(states)   # lo slot si puo' saltare
        for (ta, ya), (sc, path) in states.items():
            for c in cands:
                if c.get('_pinned'): continue
                tt = t
                if slot['role'] == 'climax':   # il climax deve coprire il cambio di traccia
                    tt = climax_t(t, c['dur'], b_start)
                if c['y0'] <= ya or tt <= ta: continue
                if slot['role'] == 'climax' and c['_force'] < fmax - 1.0: continue   # il climax e' l'evento piu' forte
                aff = 0.8; f = c['_force']
                if slot['prefer'] == 'disaster': aff = 1.0 if c['_dis'] else 0.3
                elif slot['prefer'] == 'build':   # rinascita: un grande cantiere vale come un evento forte
                    aff = 1.0 if not c['_dis'] else 0.4; f = max(f, 6.0) if not c['_dis'] else f
                if slot['role'] == 'climax' and b_start and tt + c['dur'] < b_start + 0.5: aff *= 0.4
                gain = slot['weight'] * f * aff
                if f < 4.5: gain *= 0.3
                pen = seg_ok(ta, ya, tt, c['y0'])
                if pen <= -1e5: continue
                v = sc + gain + pen
                key = (tt, c['y0'])
                if key not in new or v > new[key][0]: new[key] = (v, path + [(tt, c['y0'], slot, c)])
        states = new
    best = None
    for (ta, ya), (sc, path) in states.items():
        v = sc + seg_ok(ta, ya, t_end, y_end)
        if best is None or v > best[0]: best = (v, path)
    return best[1] if best else []


# ======================================================================================================== regia
def run(story, data_dir=None, out_dir=None, regia_dir=None, music=None, quiet=False, write=True):
    if isinstance(story, str): story = load_story(story)
    city = story['city']; slug = city['slug']; R = story.get('regia', {}) or {}
    warnings = []

    def warn(m):
        warnings.append(m)
        if not quiet: print('  [!]', m)
    ddir = data_dir or story_data_dir(story)
    D = Data(story, ddir)
    if not D.has_hist: warn(f'{ddir}/hist.json mancante: attivita\' solo dagli edifici attuali')
    M = load_music(music or R.get('music'))
    if (music or R.get('music')) and M is None: warn(f"modello musicale {music or R.get('music')} non trovato")
    rmin, rmax = float(R.get('rmin', 0.5)), float(R.get('rmax', 8.0))
    pacing = R.get('pacing', 'buildings'); story_mode = pacing == 'story'
    if pacing not in ('buildings', 'story'): warn(f"regia.pacing sconosciuto: {pacing!r} (buildings|story)")
    cont = R.get('camera') == 'continuous'
    MO_ = story.get('montaggio', {}) or {}
    recap_s, cta_s, src_s = end_plan_of(story, story_mode)
    if recap_s and not story_mode: warn('montaggio.recap richiede regia.pacing="story": ignorato'); recap_s = 0.0
    night = bool(R.get('night', False if story_mode else True))
    op = R.get('open', {}) or {}
    y_open = float(op.get('year', 2026)); y_start = float(op.get('rewind_to', city.get('start_year')))
    hold = float(op.get('hold', 3.0)); title_t = float(op.get('title_t', 9.5))
    if title_t > 9.5: warn(f'titolo all\'anno di partenza a {title_t} s (> 9,5 s)')
    b_start = R.get('b_start', M.get('b_start') if M else None)
    dur_m = M.get('duration') if M else None
    DUR = float(R.get('duration') or dur_m or 300.0)
    if M and b_start is not None and 'b_start' not in R and dur_m and DUR < dur_m - 0.5:
        b_start = DUR - (dur_m - M['b_start'])     # durata piu' corta: si accorcia A, il finale di B resta intero
        warn(f'durata {DUR} < modello {dur_m}: b_start spostato a {b_start:.1f} (le ancore di A dopo {b_start - 12:.0f} s cadono)')
    if M and dur_m and DUR > dur_m + 0.5: warn(f'durata {DUR} oltre la musica ({dur_m} s)')
    shift = (b_start - M['b_start']) if (M and b_start is not None) else 0.0
    slots = []
    if M:
        for s in M['slots']:
            t = s['t'] + (shift if s['t'] >= M['b_start'] - 15 else 0.0)
            if s['t'] < M['b_start'] - 15 and b_start is not None and t > b_start - 12: continue
            slots.append(dict(s, t=t))
    if night:
        night_t = float(R.get('night_t') or next((s['t'] for s in slots if s['role'] == 'night'), DUR - 50))
    else:
        night_t = None
    if story_mode:
        end_t = (night_t if night else DUR - recap_s - float(R.get('end_hold', (cta_s + src_s) or 4.0)))
    else:
        end_t = night_t if night else DUR - float(R.get('end_hold', 8.0))

    # ---------- soste ----------
    SOSTE = []
    for i, s in enumerate(R.get('soste', [])):
        s = dict(s); s.setdefault('dur', 5.0); s.setdefault('y1', s['y0']); s['_i'] = i
        s['y0'], s['y1'], s['dur'] = float(s['y0']), float(s['y1']), float(s['dur'])
        if not (y_start <= s['y0'] < 2026.0):
            warn(f"sosta fuori dagli anni del video, tolta: {s['caption']} ({s['y0']})"); continue
        tg = D.target(s.get('target'))
        if tg is None:
            warn(f"sosta senza bersaglio: {s['caption']} -> target {s.get('target')!r} non trovato (uso la citta' dell'anno)")
        s['_tg'] = tg; s['_force'] = sosta_force(s); s['_dis'] = sosta_is_disaster(s)
        SOSTE.append(s)
    if story_mode:
        for i, c in enumerate(MO_.get('cards', []) or []):
            y = float(c['y'])
            if not (y_start <= y < 2026.0): warn(f"cartello fuori dagli anni del video, tolto: {c.get('title')} ({y})"); continue
            h = float(c.get('hold_s', 5.0))
            SOSTE.append({'y0': y, 'y1': y + HOLD_RATE * h, 'dur': h, 'caption': c['title'], '_i': 10000 + i, '_force': 0.0, '_dis': False,
                          '_card': True, '_tg': D.target(c.get('target')) if c.get('target') else None, 'shot': c.get('shot', 'medium'),
                          '_c': c})
    SOSTE.sort(key=lambda s: (s['y0'], s['_i']))
    for a, b in zip(SOSTE, SOSTE[1:]):
        if b['y0'] < a['y1'] - 1e-6 and not story_mode:
            warn(f"soste sovrapposte negli anni: '{a['caption']}' ({a['y0']}-{a['y1']}) e '{b['caption']}' ({b['y0']}-{b['y1']})")
    focus = None
    for s in SOSTE:
        if s['_tg'] is not None: focus = (s['_tg']['x'], s['_tg']['y']); break

    # ---------- ancore ----------
    fixed, used_roles, anchor_log = [], set(), []
    for a in ([] if story_mode else (R.get('anchors', []) or [])):
        t = parse_t(a.get('t'), {'slots': slots}, b_start or DUR)
        if t is None: warn(f'ancora con tempo non valido: {a}'); continue
        if 'sosta' in a:
            s = find_sosta(SOSTE, a['sosta'])
            if s is None: warn(f"ancora: sosta '{a['sosta']}' non trovata"); continue
            if isinstance(a.get('t'), str) and a['t'] == 'climax' and b_start:
                t = climax_t(t, s['dur'], b_start)
            s['_pinned'] = True; y = s['y0']; lab = f"sosta '{s['caption']}'"
        else:
            y = float(a['year']); lab = a.get('note', 'anno')
        if isinstance(a.get('t'), str): used_roles.add(a['t'])
        fixed.append((t, y)); anchor_log.append((t, y, a.get('t') if isinstance(a.get('t'), str) else 'manuale', lab))
    for s in SOSTE:
        if s.get('role') and not s.get('_pinned') and not story_mode:
            t = parse_t(s['role'], {'slots': slots}, b_start or DUR)
            if t is None: warn(f"ruolo '{s['role']}' sconosciuto per '{s['caption']}'"); continue
            if s['role'] == 'climax' and b_start: t = climax_t(t, s['dur'], b_start)
            s['_pinned'] = True; used_roles.add(s['role']); fixed.append((t, s['y0']))
            anchor_log.append((t, s['y0'], s['role'], f"sosta '{s['caption']}'"))
    if R.get('anchors_auto', True) and slots and not story_mode:
        free_slots = [s for s in slots if s['role'] not in used_roles and s['role'] != 'night'
                      and title_t + 4 < s['t'] < end_t - 4 and all(abs(s['t'] - t) > 6 for t, _ in fixed)]
        cands = [s for s in SOSTE if s['y0'] > y_start + 1e-6]
        # eventi del montaggio con "force": ancore d'anno (nessuna sosta), es. le mura che cadono sulla salita di B
        evc = []
        for e in (story.get('montaggio', {}) or {}).get('events', []) or []:
            if 'force' in e and y_start < float(e['y']) < 2026:
                evc.append({'y0': float(e['y']), 'y1': float(e['y']), 'dur': 0.0, 'caption': 'evento: ' + e.get('title', ''),
                            '_force': float(e['force']), '_event': True,
                            '_dis': bool(e.get('sober')) or any(w in e.get('title', '') for w in DISASTER_WORDS)})
        cands = sorted(cands + evc, key=lambda c: c['y0'])
        path = auto_anchors(free_slots, cands, sorted(fixed), title_t, y_start, end_t, 2026.0, rmin, rmax, b_start)
        for t, y, slot, s in path:
            fixed.append((t, y)); s['_pinned'] = True
            anchor_log.append((t, y, slot['role'] + ' (auto)', f"sosta '{s['caption']}' forza {s['_force']:.1f}"))
    fixed = sorted(fixed)
    FIXED = [(0.0, y_open), (hold, y_open), (title_t, y_start)] + [f for f in fixed if title_t < f[0] < end_t] + [(end_t, 2026.0)]
    for (ta, ya), (tb, yb) in zip(FIXED[2:], FIXED[3:]):
        if yb < ya: warn(f'ancore non in ordine: {fmt_t(ta)} {ya} -> {fmt_t(tb)} {yb}')
    tail = [(end_t, 2026.0), (DUR, 2026.0)]
    if story_mode and recap_s:   # il recap riparte da y_start e rifa' tutti gli anni da un punto fisso
        tail = [(end_t, 2026.0), (end_t + 0.04, y_start)] + [(end_t + 0.04 + (recap_s - 0.04) * k / 20, y_start + (2026.0 - y_start) * ease(k / 20))
                                                              for k in range(1, 21)] + [(DUR, 2026.0)]
    if story_mode:
        YEARS, SOSTA_T = build_story(SOSTE, FIXED, title_t, y_start, end_t, tail, float(op.get('story_lead', 3.4)), warn)
    else:
        TL = Timeline(D, rmin, rmax, warn)
        YEARS, SOSTA_T = TL.build(FIXED, SOSTE, tail)
    year_at = make_year_at(YEARS)

    # ---------- camera ----------
    def campos(tx, ty, tz, d, el, az):
        e, a = math.radians(el), math.radians(az)
        return (tx + d * math.cos(e) * math.sin(a), ty + d * math.cos(e) * math.cos(a), tz + d * math.sin(e))
    az_def = R.get('az', 205.0)
    az_def = float(az_def[0] if isinstance(az_def, list) else az_def)
    SHOTS = []
    (m26x, m26y), r26 = D.extent(2026.0)
    fx_, fy_ = focus if focus else (m26x, m26y)
    o = R.get('open_shots')
    if o:
        for sh in o: SHOTS.append(tuple(sh[:2]) + (tuple(sh[2]),) + tuple(sh[3:]))
    else:
        d_open = float(op.get('d', max(3000.0, 1.25 * r26 + 1000)))
        oc = ((m26x + fx_) / 2, (m26y + fy_) / 2, 0.0)
        SHOTS.append((0.0, hold, oc, d_open, d_open * 0.92, 34, 32, az_def - 5, az_def + 1, 35))
        SHOTS.append((hold, title_t, (fx_ * 0.9 + oc[0] * 0.1, fy_ * 0.9 + oc[1] * 0.1, 0.0), d_open * 0.92, 1500, 32, 26, az_def + 1, az_def + 9, 35))
        SHOTS.append((title_t, title_t + 2.5, (fx_, fy_, 10.0), 1500, 420, 26, 24, az_def + 9, az_def, 35))
    open_end = SHOTS[-1][1]
    every = float(R.get('wide_every', 16.0))
    alt = 0; prev_end = open_end
    for (t0, t1, s) in ([] if cont else SOSTA_T):
        if t0 < open_end: t0 = open_end
        if t1 <= t0 + 0.5: continue
        if t0 - prev_end > 3.0:
            gap0, gap1 = prev_end, t0
            n_sub = max(1, int((gap1 - gap0) // every))
            for k in range(n_sub):
                a_, b_ = gap0 + (gap1 - gap0) * k / n_sub, gap0 + (gap1 - gap0) * (k + 1) / n_sub
                (mx, my), r = D.extent(year_at(b_), focus); alt += 1
                d = 1.0 * r + (450 if r > 700 else 180); el = 30 if alt % 2 else 22
                az0 = (az_def - 40, az_def - 5, az_def + 25, az_def - 20)[alt % 4]
                SHOTS.append((a_, b_, (mx, my, 0.0), d * 1.25, d * 0.70, el + 4, el - 4, az0, az0 + (38 if alt % 2 else -38), 35))
        tg = s['_tg']
        if tg is None:
            (mx, my), r = D.extent(s['y1'], focus); tg = {'x': mx, 'y': my, 'z': 0.0, 'h': 0.0, 'R': r}
        cam = s.get('cam') or {}
        mul, el_def = SHOT.get(s.get('shot', 'medium'), SHOT['medium'])
        d = float(cam.get('d', mul * (180.0 + 1.3 * max(tg['R'], 0.6 * tg['h'], 40.0))))
        if s.get('shot') == 'wide' and 'd' not in cam:   # 12 nov (Valencia, Plan Sur): area di 6 km -> camera a 13 km, citta' illeggibile.
            # tetto: estensione del bersaglio + margine, e al massimo WIDE_MAX all'inizio del carrello (d*1.25)
            d = min(d, max(600.0, 1.15 * tg['R'] + 400.0), WIDE_MAX / 1.25)
        el = float(cam.get('el', el_def))
        az = cam.get('az', s.get('az', az_def))
        az0, az1 = (float(az[0]), float(az[1])) if isinstance(az, list) else (float(az), float(az) + 30.0)
        mm = float(cam.get('mm', 35))
        SHOTS.append((t0, t1, (tg['x'], tg['y'], tg['z']), d * 1.25, d * 0.75, el + 4, el, az0 - 6, az1 + 6, mm))
        prev_end = t1
    cam_end = end_t if (story_mode and recap_s) else DUR
    if cont:
        pass
    elif night:
        if night_t - prev_end > 3:
            n_sub = max(1, int((night_t - prev_end) // 15))
            for k in range(n_sub):
                a_, b_ = prev_end + (night_t - prev_end) * k / n_sub, prev_end + (night_t - prev_end) * (k + 1) / n_sub
                alt += 1; d = 0.8 * r26 + 700; el = (24, 18, 30)[alt % 3]; az0 = (az_def - 30, az_def + 10, az_def + 35)[alt % 3]
                SHOTS.append((a_, b_, ((m26x + fx_) / 2, (m26y + fy_) / 2, 0.0), d * 1.2, d * 0.75, el + 3, el - 3, az0, az0 + 36, 35))
        L = DUR - night_t
        ns = R.get('night_shots')
        if ns:   # [{"target", "dur"?, "d":[d0,d1], "el":[e0,e1], "az":[a0,a1]}]
            t = night_t
            for i, n in enumerate(ns):
                t1 = DUR if i == len(ns) - 1 else t + float(n.get('dur', L / len(ns)))
                tg = D.target(n['target'])
                if tg is None: warn(f"bersaglio notturno non trovato: {n['target']}"); tg = {'x': m26x, 'y': m26y, 'z': 0.0}
                d0, d1 = n.get('d', [900, 500]); e0, e1 = n.get('el', [24, 16]); a0, a1 = n.get('az', [az_def - 20, az_def + 30])
                SHOTS.append((t, t1, (tg['x'], tg['y'], tg['z']), d0, d1, e0, e1, a0, a1, 35)); t = t1
        else:   # alto monumento vicino al centro (tramonto), punto di fondazione, la citta' che si allontana
            best = None
            for s in SOSTE:
                tg = s['_tg']
                if tg and tg.get('kind') == 'landmark' and math.hypot(tg['x'] - m26x, tg['y'] - m26y) < max(1500, r26 / 2):
                    if best is None or tg['h'] > best['h']: best = tg
            best = best or {'x': fx_, 'y': fy_, 'z': 10.0, 'h': 40.0, 'R': 100.0}
            d1 = 180.0 + 1.3 * max(best['R'], 0.6 * best['h'])
            t_a, t_b = night_t + 0.37 * L, night_t + 0.69 * L
            SHOTS.append((night_t, t_a, (best['x'], best['y'], best['z']), d1 * 2.0, d1, 26, 17, az_def - 20, az_def + 45, 35))
            SHOTS.append((t_a, t_b, (fx_, fy_, 10.0), 1000, 520, 18, 12, az_def - 85, az_def - 20, 35))
            SHOTS.append((t_b, DUR, ((m26x + fx_) / 2, (m26y + fy_) / 2, 0.0), 3000, max(6200, 1.3 * r26), 22, 32, az_def - 15, az_def + 30, 35))
    elif cam_end - prev_end > 3:
        n_sub = max(1, int((cam_end - prev_end) // 9))
        for k in range(n_sub):
            a_, b_ = prev_end + (cam_end - prev_end) * k / n_sub, prev_end + (cam_end - prev_end) * (k + 1) / n_sub
            last = k == n_sub - 1; alt += 1
            d0 = 0.8 * r26 + 700
            SHOTS.append((a_, b_, ((m26x + fx_) / 2, (m26y + fy_) / 2, 0.0), d0 if not last else d0 * 1.2,
                          d0 * 0.75 if not last else max(6000, 1.3 * r26), 28, 22 if not last else 34, az_def - 5, az_def + 30, 35))
    d_rc = max(5000.0, 1.8 * r26)
    recap_shot = (end_t, DUR, (m26x, m26y, 0.0), d_rc, d_rc, 52, 52, az_def, az_def, 35)   # punto di vista alto e FISSO
    if story_mode and recap_s and not cont: SHOTS.append(recap_shot)
    SHOTS.sort(key=lambda s: s[0])
    cam = []
    if cont:
        wps = [(0.0, SHOTS[0][2], SHOTS[0][3], SHOTS[0][5], SHOTS[0][7], 35), (title_t + 0.5, (fx_, fy_, 10.0), 1800.0, 28, az_def + 9, 35)]
        for j, (t0, t1, s) in enumerate(SOSTA_T):
            if t1 <= title_t + 1.0: continue
            tg = s['_tg']
            if tg is None:
                (mx, my), r = D.extent(s['y1'], focus); tg = {'x': mx, 'y': my, 'z': 0.0, 'h': 0.0, 'R': r}
                d = 1.0 * r + (450 if r > 700 else 180); el = 30.0
            else:
                mul, el = SHOT.get(s.get('shot', 'medium'), SHOT['medium'])
                d = mul * (180.0 + 1.3 * max(tg['R'], 0.6 * tg['h'], 40.0))
                if s.get('shot') == 'wide': d = min(d, max(600.0, 1.15 * tg['R'] + 400.0), WIDE_MAX / 1.25)
            az0 = az_def - 20 + 20 * (j % 3)
            if wps and t0 - wps[-1][0] > 2.5:   # durante la corsa la camera si apre sull'estensione della citta' di quell'anno
                tm = (wps[-1][0] + t0) / 2; (mx, my), r = D.extent(year_at(tm), focus)
                wps.append((tm, (mx, my, 0.0), 1.0 * r + 450 + 0.3 * d, 33, az0 - 12, 35))
            wps.append((t0 + 0.3, (tg['x'], tg['y'], tg['z']), d * 1.1, el + 3, az0, 35))
            wps.append((t1 - 0.3, (tg['x'], tg['y'], tg['z']), d * 0.85, el, az0 + 18, 35))
        if story_mode and recap_s:
            wps += [(end_t, recap_shot[2], d_rc, 52, az_def, 35), (DUR, recap_shot[2], d_rc, 52, az_def, 35)]
        else:
            wps.append((DUR, ((m26x + fx_) / 2, (m26y + fy_) / 2, 0.0), max(6000.0, 1.3 * r26), 34, az_def + 20, 35))
        cam = continuous_cam(wps, DUR)
    for i, (t0, t1, tg, d0, d1, e0, e1, a0, a1, mm) in enumerate([] if cont else SHOTS):
        n = max(2, int((t1 - t0) / 0.5))
        for k in range(n + 1):
            u = k / n; ue = ease(u) * 0.5 + u * 0.5
            tt = t0 + (t1 - t0) * u
            if k == 0 and i > 0: tt = t0 + 1.0 / FPS      # stacco netto
            p = campos(*tg, d0 + (d1 - d0) * ue, e0 + (e1 - e0) * ue, a0 + (a1 - a0) * ue)
            cam.append([round(tt, 3), [round(v, 1) for v in p], [round(float(v), 1) for v in tg], mm])
    cam.sort(key=lambda c: c[0])
    name = city.get('name', slug)
    sched = {'_doc': f'{name}, regia automatica (kit/regia_kit.py).' + (f" Musica {M['name']}, B da {b_start:.1f} s." if M else ''),
             'duration': DUR, 'lens': 35, 'years': [[t, y] for t, y in YEARS], 'cam': cam}
    if night: sched['night_t'] = night_t
    if b_start is not None: sched['b_start'] = b_start
    sched['soste'] = [[round(t0, 2), round(t1, 2), s['y0'], s['y1'], s['caption']] for t0, t1, s in SOSTA_T if not s.get('_card')]
    if story_mode:
        sched['pacing'] = 'story'; sched['title_t'] = title_t
        sched['cards'] = [{'t_in': round(t0, 2), 't_out': round(t1, 2), 'y': s['_c']['y'], 'title': s['_c']['title'], 'lines': s['_c'].get('lines', []),
                           'chapter': s['_c'].get('chapter'), 'src': s['_c'].get('src')} for t0, t1, s in SOSTA_T if s.get('_card')]
        sched['end_plan'] = {'recap': [round(end_t, 2), round(end_t + recap_s, 2)] if recap_s else None,
                             'cta': [round(DUR - src_s - cta_s, 2), round(DUR - src_s, 2)] if cta_s else None,
                             'sources': [round(DUR - src_s, 2), DUR] if src_s else None}

    # ---------- controlli ----------
    ts = np.arange(0, DUR, 0.25); yv = np.array([year_at(t) for t in ts]); rate = np.gradient(yv, ts)
    in_stop = np.zeros(len(ts), bool)
    for t0, t1, s in SOSTA_T: in_stop |= (ts >= t0 - 0.3) & (ts <= t1 + 0.3)
    anch = np.zeros(len(ts), bool)
    for t, _ in FIXED: anch |= abs(ts - t) < 0.6
    free = (ts > title_t + 0.5) & (ts < end_t - 0.5) & ~in_stop & ~anch
    bad = free & ((np.abs(rate) > rmax * 1.08) | (np.abs(rate) < rmin * 0.9))
    if bad.any() and not story_mode:
        runs, start = [], None
        for i, b in enumerate(bad):
            if b and start is None: start = i
            if (not b or i == len(bad) - 1) and start is not None:
                if i - start >= 4: runs.append((ts[start], ts[i]))
                start = None
        for a_, b_ in runs[:8]:
            m = (ts >= a_) & (ts <= b_)
            warn(f'velocita\' fuori limiti {fmt_t(a_)}-{fmt_t(b_)}: {np.abs(rate[m]).min():.2f}-{np.abs(rate[m]).max():.2f} anni/s (limiti {rmin}-{rmax})')
    strong = [(t0, s) for t0, t1, s in SOSTA_T if s['_force'] >= STRONG]
    if story_mode: pass
    elif not strong: warn('nessun evento forte (forza >= 6) tra le soste')
    elif strong[0][0] > 45: warn(f"primo evento forte dopo 45 s: '{strong[0][1]['caption']}' a {fmt_t(strong[0][0])}")
    for (a0, a1, sa), (b0, b1, sb) in zip(SOSTA_T, SOSTA_T[1:]):
        if b0 < a1 - 0.05: warn(f"soste sovrapposte nel video: '{sa['caption']}' e '{sb['caption']}' ({fmt_t(b0)} < {fmt_t(a1)})")
    day = end_t - title_t; tot = sum(t1 - t0 for t0, t1, _ in SOSTA_T)
    if tot > 0.4 * day and not story_mode: warn(f'soste {tot:.0f} s = {100 * tot / day:.0f}% del giorno (> 40%)')
    if b_start is not None and M and not story_mode:
        cover = [s for t0, t1, s in SOSTA_T if t0 <= b_start <= t1]
        if not cover: warn(f'nessuna sosta copre il cambio di traccia a {fmt_t(b_start)}')

    # ---------- testo e grafico ----------
    lines = [f'{name}: regia automatica (kit/regia_kit.py)',
             f'Durata {int(DUR // 60)}:{DUR % 60:04.1f}  fotogrammi {int(round(DUR * FPS))}  inquadrature {len(SHOTS)}  stacco medio ogni {DUR / len(SHOTS):.1f} s',
             f"Musica: {M['name'] if M else '-'}  b_start {b_start}  notte {night_t}", '', 'ANCORE (video -> anno):']
    for t, y in FIXED:
        lab = next((f'{r_}: {l_}' for t_, y_, r_, l_ in anchor_log if abs(t_ - t) < 1e-6 and abs(y_ - y) < 1e-6), '')
        lines.append(f'  {fmt_t(t):>7}  {y:8.2f}  {lab}')
    lines += ['', 'SOSTE (video -> anni):']
    for t0, t1, s in SOSTA_T:
        lines.append(f"  {fmt_t(t0)}-{fmt_t(t1)}  {s['y0']:.1f}->{s['y1']:.1f}  {s['caption']}  [forza {s['_force']:.1f}"
                     f"{', ' + s.get('fx') if s.get('fx') else ''}]")
    evs = (story.get('montaggio', {}) or {}).get('events', [])
    if evs:
        lines += ['', 'EVENTI (didascalie):']
        T_ = np.array([a for a, _ in YEARS]); Y_ = np.array([b for _, b in YEARS])
        for e in evs:
            ok = np.where((T_ >= title_t) & (Y_ >= e['y']))[0]
            lines.append(f"  {fmt_t(T_[ok[0]]) if len(ok) else '  --  '}  {e['y']}  {e.get('title', '')}")
    lines += ['', 'ANNO OGNI 30 s:'] + [f'  {int(t // 60)}:{int(t % 60):02d}  {year_at(t):7.1f}  ({abs(rate[min(len(rate) - 1, int(t * 4))]):.2f} anni/s)'
                                       for t in range(0, int(DUR), 30)]
    fr = np.abs(rate[free]) if free.any() else np.array([0.0])
    lines += ['', f'Velocita fuori dalle soste: mediana {np.median(fr):.2f} anni/s, max {fr.max():.1f} anni/s',
              f'Soste: {len(SOSTA_T)}, {tot:.0f} s ({100 * tot / max(1, day):.0f}% del giorno)']
    lines += ['', 'AVVISI:'] + ([f'  - {w}' for w in warnings] or ['  nessuno'])
    out = {'sched': sched, 'warnings': warnings, 'soste_t': SOSTA_T, 'fixed': FIXED, 'anchors': anchor_log,
           'year_at': year_at, 'text': '\n'.join(lines), 'shots': SHOTS}
    if not write: return out
    out_dir = out_dir or ROOT
    regia_dir = regia_dir or (out_dir if out_dir != ROOT else os.path.join(ROOT, 'cities', slug))
    os.makedirs(out_dir, exist_ok=True); os.makedirs(regia_dir, exist_ok=True)
    json.dump(sched, open(os.path.join(out_dir, f'schedule_{slug}.json'), 'w'))
    if night:
        json.dump(dict(sched, years=[[0, 2026], [DUR, 2026]]), open(os.path.join(out_dir, f'schedule_{slug}_night.json'), 'w'))
    open(os.path.join(regia_dir, 'regia.txt'), 'w').write(out['text'] + '\n')
    if not quiet: print(out['text'])
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7.5), dpi=90, sharex=True)
        ax1.plot(ts / 60, yv, color='#1f6f8b', lw=2); ax1.set_ylabel('anno'); ax1.grid(alpha=0.3)
        ax2.plot(ts / 60, np.clip(abs(rate), 0, rmax * 1.5), color='#c0392b', lw=1.5); ax2.set_ylabel('anni al secondo')
        ax2.set_xlabel('minuti di video'); ax2.grid(alpha=0.3)
        ax2.axhline(rmax, color='grey', ls='--', lw=0.8); ax2.axhline(rmin, color='grey', ls='--', lw=0.8)
        span = max(1.0, 2026 - y_start)
        for t0, t1, s in SOSTA_T:
            for ax in (ax1, ax2): ax.axvspan(t0 / 60, t1 / 60, color='#f39c12' if s['_dis'] else '#27ae60', alpha=0.25)
            ax1.text(t0 / 60, year_at(t0) + span * 0.02, s['caption'].split('(')[0][:22], fontsize=7, rotation=60)
        if M:
            for sl in slots:
                ax2.axvline(sl['t'] / 60, color='#8e44ad', lw=0.6, ls=':')
                ax2.text(sl['t'] / 60, rmax * 1.3, sl['role'], fontsize=7, color='#8e44ad', rotation=90, va='top')
        for ax in (ax1, ax2):
            if b_start is not None: ax.axvline(b_start / 60, color='purple', lw=1)
            if night: ax.axvspan(night_t / 60, DUR / 60, color='#2c3e50', alpha=0.2)
        for t, y in FIXED[2:]: ax1.plot([t / 60], [y], 'o', color='#8e44ad', ms=4)
        ax1.set_title(f'{name}: anni nel video (verde = soste, arancio = catastrofi, viola = cambio traccia, punti = ancore)')
        plt.tight_layout(); plt.savefig(os.path.join(regia_dir, 'regia.png')); plt.close(fig)
    except Exception as e:
        warn(f'grafico non fatto: {e}')
    return out


def year_at_schedule(sched):
    """year_at(t) dallo schedule (interpolazione lineare, come build_render)."""
    Y = np.array(sched['years'], float)
    return lambda t: float(np.interp(t, Y[:, 0], Y[:, 1]))


def main(argv):
    if not argv: print(__doc__); return 1
    opts = {}; pos = []
    i = 0
    while i < len(argv):
        if argv[i].startswith('--'): opts[argv[i][2:]] = argv[i + 1]; i += 2
        else: pos.append(argv[i]); i += 1
    r = run(pos[0], data_dir=opts.get('data'), out_dir=opts.get('out'), regia_dir=opts.get('regia-dir'), music=opts.get('music'))
    print(f"\n{len(r['warnings'])} avvisi")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
