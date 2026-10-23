# Regia di Siviglia (23 ott 2026). Durata 5:26.6 = 7.839 fotogrammi (decisione di Fabio). UN SOLO PIANO SEQUENZA
# (SPEC_CAMERA_DRONE): nessuno stacco, obiettivo fisso 35 mm, la camera "zooma" muovendosi. Camera SEMPRE in volo,
# inclinata, quota 300-1.000 m sopra il suolo (decisione di Fabio, 23 ott), di preferenza a sud-ovest del bersaglio, cioe'
# sopra il fiume (e col sole alle spalle). Niente sosta della camera sulla Cartuja nel 1992 (solo cartello) e niente punto
# drone sulla laguna 1574-78 (decisioni di Fabio, 23 ott). Mura 1858-73: solo cartello, nessuna sosta (prova 1865 e 1862:
# dall'alto le mura alte 9 m tra case della stessa altezza non si leggono).
# VELOCITA' DEL TEMPO: come Copenaghen: il tempo libero va agli anni in proporzione agli edifici che nascono o muoiono
# (limiti 0,5-8 anni/s); le soste rallentano sugli eventi con un'inquadratura vicina.
# Musica: non ancora scelta -> nessuna ancora musicale; la notte parte a NIGHT_T.
# Uso: python regia_sevilla.py DATA -> schedule_sevilla.json, schedule_sevilla_night.json, regia_sevilla.png,
#      regia_sevilla.txt (soste, eventi, quote), eventi_sevilla.json (cartelli per l'overlay Remotion)
import json, math, sys
import numpy as np
from scipy.interpolate import PchipInterpolator

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data_sevilla'
FPS = 24; NFR = 7839; DUR = NFR / FPS          # 326.625 s
NIGHT_T = DUR - 36.0                           # ultimi ~36 s di notte (dusk.py: tramonto nei primi 10 s)
LENS = 35
LAT0, LON0 = 37.386194, -5.992417
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
LM = json.load(open(f'{DATA}/landmarks.json'))
def lmc(name):
    ps = [p for p in LM['parts'] if p['name'] == name]
    xs = [p.get('cx', 0) for p in ps]; ys = [p.get('cy', 0) for p in ps]
    return float(np.median(xs)), float(np.median(ys))
dem = np.load(f'{DATA}/dem.npz'); DEM, DX0, DY0, DC = dem['D'], float(dem['x0']), float(dem['y0']), float(dem['cell'])
def ground(x, y):
    i, j = int((y - DY0) // DC), int((x - DX0) // DC)
    if 0 <= i < DEM.shape[0] and 0 <= j < DEM.shape[1]: return float(DEM[i, j])
    return 0.0
def ground_max(x, y, r=400):   # rilievo massimo attorno (la camera non deve sfiorare l'Aljarafe)
    return max(ground(x + dx, y + dy) for dx in (-r, 0, r) for dy in (-r, 0, r))

GIRALDA = (-12.2, -0.3); TORRE_ORO = lmc('Torre del Oro'); MAESTRANZA = lmc('Maestranza'); TRIANA = lmc('Triana Bridge')
PL_ESPANA = L(37.37720, -5.98690)

# ---------- ancore (t, anno) ----------
FIXED = [(0.0, 2026.0), (3.0, 2026.0), (9.5, 1248.0), (NIGHT_T, 2026.0)]
# ---------- soste: (anno inizio, anno fine, durata s, cartello, bersaglio (x, y, z), quota camera m, azimut inizio, fine)
#   azimut = da dove guarda la camera (0 = da nord, 180 = da sud, 225 = da sud-ovest, sopra il fiume)
SOSTE = [
    (1248.0, 1250.0, 7.0, 'Seville under Castile (1248)', (-150, -60, 20), 380, 236, 212),
    (1430.0, 1437.0, 5.0, 'The Great Mosque gives way to the Cathedral (1434)', (*GIRALDA, 30), 360, 218, 196),
    (1564.0, 1571.0, 4.5, 'The Giralda gets its Renaissance belfry (1568)', (*GIRALDA, 50), 330, 200, 176),
    (1758.0, 1790.0, 5.0, 'The Maestranza bullring rises (1761-1785)', (*MAESTRANZA, 8), 340, 232, 205),
    (1843.0, 1854.0, 4.5, 'Isabel II Bridge replaces the boat bridge (1845-1852)', (*TRIANA, 5), 330, 196, 172),
    (1912.0, 1930.0, 5.5, 'Plaza de España for the 1929 Expo (1914-1929)', (*PL_ESPANA, 10), 420, 238, 210),
    (1973.0, 1983.0, 5.0, 'The river is moved west: Corta de la Cartuja (1975-1982)', (-1000, 1900, 0), 680, 206, 190),
]
# ---------- cartelli senza sosta (anno, testo): l'overlay li mostra all'istante del loro anno ----------
EVENTS = [
    (1248.9, 'Ferdinand III enters Seville (23 Nov 1248)'), (1252.0, 'Ferdinand III dies in Seville (1252)'), (1356.0, 'Earthquake topples the Giralda\'s golden spheres (1356)'),
    (1400.0, 'A cross and bell crown the Giralda (c. 1400)'), (1481.0, 'Castile\'s first Inquisition tribunal sits in Triana Castle (1481)'), (1503.0, 'Casa de Contratación: Seville controls the trade with the Americas (1503)'),
    (1574.0, 'The Feria lagoon is drained (1574-1578)'), (1578.0, 'Alameda de Hércules opens (1578)'),
    (1519.6, 'Magellan\'s fleet sails from Seville (1519)'), (1600.0, 'Seville nears 120,000 people (c. 1600)'), (1649.0, 'The Great Plague of 1649'), (1717.0, 'The Casa de Contratación moves to Cádiz (1717)'),
    (1728.0, 'Royal Tobacco Factory begun (1728)'), (1755.9, 'Lisbon earthquake shakes Seville (1755)'),
    (1760.0, 'Torre del Oro gets its upper lantern (1760)'), (1810.1, 'French troops occupy Seville (1810-1812)'), (1836.0, 'Disentailment empties the convents (1836)'), (1811.0, 'Encarnación convent demolished (1811)'),
    (1848.0, 'Plaza Nueva is laid out (1848-1857)'), (1858.0, 'The medieval walls come down (1858-1873)'), (1881.0, 'The Maestranza is completed (1881)'),
    (1909.0, 'Alfonso XIII Canal is dug (1909-1926)'), (1929.35, 'Ibero-American Exposition opens (9 May 1929)'), (1936.5, 'Spanish Civil War (1936-1939)'),
    (1948.0, 'Chapina arm is closed (1948-1950)'), (1961.9, 'Tamarguillo flood (25 Nov 1961)'),
    (1991.0, 'Santa Justa station opens (1991)'), (1992.0, 'Expo 92 · 20 April – 12 October 1992'),
    (2005.0, 'Metropol Parasol (2005-2011)'),
]

# ---------- attivita' per anno ----------
B = json.load(open(f'{DATA}/buildings.json')); H = json.load(open(f'{DATA}/hist.json'))
act = np.zeros(2030)
for o in B: act[min(2029, max(0, int(o['y'])))] += 1
for o in H:
    act[min(2029, max(0, int(o['y'])))] += 1
    if o.get('d', 9999) < 2027: act[int(o['d'])] += 0.6
act = np.convolve(act, np.ones(5) / 5, 'same')
RMIN, RMAX = 0.5, 8.0
RMAX_OLD, OLD_END = 12.0, 1840   # prima del 1840 (citta' chiusa nelle mura) fino a 12 anni/s

def spread(pieces, T):
    """tempo T sui pezzi di anni, in proporzione all'attivita' con 1/RMAX <= s/anno <= 1/RMIN"""
    yrs, own = [], []
    for i, (p0, p1) in enumerate(pieces):
        for y in np.arange(math.floor(p0), math.ceil(p1)):
            fr_ = min(p1, y + 1) - max(p0, y)
            if fr_ > 1e-6: yrs.append((int(y), fr_)); own.append(i)
    w = np.array([(act[y] + 3.0) ** 0.85 * f for y, f in yrs]); fr = np.array([f for _, f in yrs])
    rmx = np.array([RMAX_OLD if y < OLD_END else RMAX for y, _ in yrs]); lo, hi = fr / rmx, fr / RMIN; sv = np.clip(w / w.sum() * T, lo, hi)
    for _ in range(80):
        err = T - sv.sum()
        if abs(err) < 1e-6: break
        free = (sv < hi - 1e-9) if err > 0 else (sv > lo + 1e-9)
        if not free.any(): break
        sv[free] += err * w[free] / w[free].sum(); sv = np.clip(sv, lo, hi)
    if abs(T - sv.sum()) > 0.05: print(f'  [!] limiti impossibili: scala {T / sv.sum():.2f}'); sv *= T / sv.sum()
    out = [[] for _ in pieces]; acc = [0.0] * len(pieces)
    for (y, f), o, s in zip(yrs, own, sv):
        acc[o] += s; out[o].append((min(pieces[o][1], y + 1), acc[o]))
    return out, acc

YEARS = []; SOSTA_T = []
for (ta, ya), (tb, yb) in zip(FIXED, FIXED[1:]):
    if yb <= ya:   # riavvolgimento o pausa
        for k in range(21):
            u = k / 20; YEARS.append((ta + (tb - ta) * u, ya + (yb - ya) * u * u * (3 - 2 * u)))
        continue
    ss = [s for s in SOSTE if ya <= s[0] < yb]
    pieces = []; cur = ya
    for s in ss: pieces.append((cur, s[0])); cur = s[1]
    pieces.append((cur, yb))
    pts, Ts = spread([p for p in pieces], (tb - ta) - sum(s[2] for s in ss))
    t = ta
    for i, (p0, p1) in enumerate(pieces):
        YEARS.append((t, p0))
        for yv, dt in pts[i]: YEARS.append((t + dt, yv))
        t += Ts[i]
        if i < len(ss):
            s = ss[i]; SOSTA_T.append((t, t + s[2], s))
            for k in range(1, 11):
                u = k / 10; YEARS.append((t + s[2] * u, s[0] + (s[1] - s[0]) * u))
            t += s[2]
YEARS.append((DUR, 2026.0))
YEARS = sorted({round(float(t), 3): (round(float(t), 3), round(float(y), 4)) for t, y in YEARS}.values())
def year_at(t):
    if t <= YEARS[0][0]: return YEARS[0][1]
    for (a, ya), (b, yb) in zip(YEARS, YEARS[1:]):
        if t <= b: return ya + (yb - ya) * (t - a) / max(1e-9, b - a)
    return YEARS[-1][1]
def t_of_year(y):
    for (a, ya), (b, yb) in zip(YEARS, YEARS[1:]):
        if a >= 9.5 and ya <= y <= yb and yb > ya: return a + (b - a) * (y - ya) / (yb - ya)
    return None

# ---------- estensione della citta' per anno (vista larga) ----------
cx = np.array([sum(p[0] for p in o['r']) / len(o['r']) for o in B + H]); cy = np.array([sum(p[1] for p in o['r']) / len(o['r']) for o in B + H])
by = np.array([o['y'] for o in B + H]); bd = np.array([o.get('d', 9999) for o in B + H])
def extent(y):
    m = (by <= y) & (bd > y)
    mx, my = np.median(cx[m]), np.median(cy[m]); r = np.percentile(np.hypot(cx[m] - mx, cy[m] - my), 80)
    return (float(mx), float(my)), float(r)

# ---------- punti di passaggio della camera (t, posizione, bersaglio) ----------
def campos(tg, alt, el, az):   # camera a quota alt sopra il suolo, sguardo inclinato di el gradi, da azimut az
    d = (alt + ground(tg[0], tg[1]) - tg[2]) / math.tan(math.radians(el))
    a = math.radians(az); return [tg[0] + d * math.sin(a), tg[1] + d * math.cos(a), alt + ground(tg[0], tg[1])]
WP = []
# apertura: Siviglia di oggi da 1.000 m a sud-ovest sopra il fiume; nel riavvolgimento scende verso il porto del 1248
WP.append((0.0, campos((-300, 300, 0), 1000, 17, 214), (-300, 300, 0)))
WP.append((3.0, campos((-280, 150, 0), 960, 18, 218), (-280, 150, 0)))
WP.append((9.0, campos((-200, -80, 15), 470, 15.5, 228), (-200, -80, 15)))
for t0, t1, s in SOSTA_T:
    tg, alt, a0, a1 = s[4], s[5], s[6], s[7]
    el = 24 if alt < 600 else 26
    WP.append((t0, campos(tg, alt * 1.12, el + 2, a0), list(tg)))          # arrivo poco piu' alto, poi scende piano
    WP.append(((t0 + t1) / 2, campos(tg, alt, el, (a0 + a1) / 2), list(tg)))
    WP.append((t1, campos(tg, alt * 1.05, el, a1), list(tg)))
# tratti larghi tra le soste: la citta' di quell'anno, da 750-1.000 m, deriva lenta
ws = sorted([w[0] for w in WP])
gaps = [(a, b) for a, b in zip([9.0] + [s[1] for s in SOSTA_T], [s[0] for s in SOSTA_T] + [NIGHT_T]) if b - a > 12.0]
for k, (a, b) in enumerate(gaps):
    n = max(1, int((b - a) // 14))
    for j in range(n):
        tm = a + (b - a) * (j + 0.5) / n; (mx, my), r = extent(year_at(tm))
        nxt = next((s_ for s_ in SOSTA_T if s_[0] >= b - 1e-6), None)      # la vista larga scivola verso la sosta successiva
        u_ = (j + 0.5) / n * 0.6
        ntg = nxt[2][4] if nxt else (-250, 600, 0)
        tg = ((mx - 120) * (1 - u_) + ntg[0] * u_, my * (1 - u_) + ntg[1] * u_, 0)
        alt = float(np.clip(450 + 0.32 * r, 600, 1000)); az = (nxt[2][6] if nxt else 214) + (8 if (k + j) % 2 else -8)
        cw = np.array(campos(tg, alt, 21 if alt > 850 else 24, az))
        # la camera larga sta tra l'uscita della sosta precedente e l'arrivo della successiva (niente deviazioni di km
        # in pochi secondi: con la sola vista larga la camera arrivava a 400+ m/s)
        f_ = (j + 0.5) / n
        pc = np.array(max([w for w in WP if w[0] <= a + 1e-6], key=lambda w: w[0])[1])
        nc = np.array(min([w for w in WP if w[0] >= b - 1e-6], key=lambda w: w[0])[1]) if nxt else cw
        cw = cw * 0.4 + pc * 0.6 * (1 - f_) + nc * 0.6 * f_
        WP.append((tm, cw.tolist(), list(tg)))
# notte: sopra il fiume verso il centro e i ponti illuminati del nord (Barqueta, Alamillo), poi si allontana salendo
WP.append((NIGHT_T, campos((-250, 600, 0), 820, 20, 210), [-250, 600, 0]))
WP.append((NIGHT_T + 14, campos((-450, 1500, 10), 560, 17, 196), [-450, 1500, 10]))
WP.append((NIGHT_T + 26, campos((-400, 1300, 0), 700, 18, 214), [-400, 1300, 0]))
WP.append((DUR, campos((-200, 900, 0), 1000, 21, 222), [-200, 900, 0]))
WP.sort(key=lambda w: w[0])
# punti troppo vicini nel tempo (< 1,2 s): si tiene il primo
clean = []
for w in WP:
    if clean and w[0] - clean[-1][0] < 1.2: continue
    clean.append(w)
WP = clean
T = np.array([w[0] for w in WP]); P = np.array([w[1] for w in WP]); G = np.array([w[2] for w in WP])
fp, fg = PchipInterpolator(T, P, axis=0), PchipInterpolator(T, G, axis=0)   # PCHIP: niente rimbalzi sotto la quota minima
cam = []; alts = []
for tt in np.arange(0.0, DUR + 1e-6, 0.25):
    p = fp(tt).tolist(); g = fg(tt).tolist()
    gm = max(ground(p[0], p[1]), ground_max(p[0], p[1]) - 60)
    p[2] = float(np.clip(p[2], gm + 300, gm + 1000))                       # regola di Fabio: 300-1.000 m sopra il suolo
    alts.append(p[2] - ground(p[0], p[1]))
    cam.append([round(float(tt), 3), [round(v, 1) for v in p], [round(v, 1) for v in g], LENS])

# ---------- movimento camera (stesso indice delle SPEC: >= 12) ----------
cp = np.array([c[1] for c in cam]); cg = np.array([c[2] for c in cam]); dt = 0.25
vel = np.linalg.norm(np.diff(cp, axis=0), axis=1) / dt
dirs = (cg - cp) / np.linalg.norm(cg - cp, axis=1)[:, None]
ang = np.degrees(np.arccos(np.clip((dirs[1:] * dirs[:-1]).sum(1), -1, 1))) / dt
MOVE = float(np.median(ang) * 4 + np.median(vel) / 25)

sched = {'_doc': 'Siviglia, regia automatica (regia_sevilla.py): un piano sequenza, 35 mm, camera 300-1.000 m sopra il suolo.',
         'duration': DUR, 'lens': LENS, 'years': [[t, y] for t, y in YEARS], 'cam': cam, 'night_t': NIGHT_T,
         'soste': [[round(t0, 2), round(t1, 2), s[0], s[1], s[3]] for t0, t1, s in SOSTA_T]}
json.dump(sched, open('schedule_sevilla.json', 'w'))
json.dump(dict(sched, years=[[0, 2026], [DUR, 2026]]), open('schedule_sevilla_night.json', 'w'))
ev = [{'t': round(t0, 2), 'year': s[0], 'text': s[3], 'sosta': True} for t0, t1, s in SOSTA_T]
ev += [{'t': round(t_of_year(y), 2), 'year': y, 'text': x, 'sosta': False} for y, x in EVENTS if t_of_year(y) is not None]
ev.sort(key=lambda e: e['t'])
json.dump(ev, open('eventi_sevilla.json', 'w'), ensure_ascii=False, indent=0)

# ---------- controllo ----------
ts = np.arange(0, DUR, 0.25); yv = np.array([year_at(t) for t in ts]); rate = np.gradient(yv, ts)
lines = [f'Durata {int(DUR // 60)}:{DUR % 60:04.1f}  fotogrammi {NFR}  piano sequenza (0 stacchi)  obiettivo {LENS} mm  punti camera {len(WP)}',
         f'Quota camera sopra il suolo: min {min(alts):.0f} m, max {max(alts):.0f} m, mediana {np.median(alts):.0f} m',
         f'Velocita camera: mediana {np.median(vel):.0f} m/s, max {vel.max():.0f} m/s; rotazione sguardo mediana {np.median(ang):.1f} gradi/s',
         f'Prima fase di crescita vera (anno > 1300): {t_of_year(1300):.1f} s', '', 'SOSTE (video -> anni):']
for t0, t1, s in SOSTA_T: lines.append(f'  {int(t0 // 60)}:{t0 % 60:04.1f}-{int(t1 // 60)}:{t1 % 60:04.1f}  {s[0]:.0f}->{s[1]:.0f}  {s[3]}')
lines += ['', 'CARTELLI (video):'] + [f'  {int(e["t"] // 60)}:{e["t"] % 60:04.1f}  {e["text"]}' for e in ev]
gp = np.diff([9.5] + [e['t'] for e in ev] + [NIGHT_T])
lines += [f'  pausa massima tra due cartelli: {gp.max():.1f} s (dopo {ev[int(np.argmax(gp)) - 1]["text"] if np.argmax(gp) else "apertura"})']
lines += ['', 'ANNO OGNI 20 s:'] + [f'  {int(t // 60)}:{int(t % 60):02d}  {year_at(t):7.1f}  ({abs(rate[int(t * 4)]):.2f} anni/s)' for t in range(0, int(DUR), 20)]
fr = abs(rate[(ts > 12) & (ts < NIGHT_T)])
lines += ['', f'Velocita del tempo fuori dalle soste: mediana {np.median(fr):.2f} anni/s, max {fr.max():.1f} anni/s']
open('regia_sevilla.txt', 'w').write('\n'.join(lines)); print('\n'.join(lines))
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 8), dpi=80, sharex=True)
    ax1.plot(ts / 60, yv, color='#1f6f8b', lw=2); ax1.set_ylabel('anno'); ax1.grid(alpha=0.3)
    ax2.plot(ts / 60, np.clip(abs(rate), 0, 12), color='#c0392b', lw=1.5); ax2.set_ylabel('anni/s'); ax2.grid(alpha=0.3)
    ax3.plot(np.arange(len(alts)) * 0.25 / 60, alts, color='#555', lw=1.5); ax3.set_ylabel('quota camera m'); ax3.axhline(300, ls='--', c='grey'); ax3.axhline(1000, ls='--', c='grey'); ax3.set_xlabel('minuti'); ax3.grid(alpha=0.3)
    for t0, t1, s in SOSTA_T:
        for ax in (ax1, ax2, ax3): ax.axvspan(t0 / 60, t1 / 60, color='#27ae60', alpha=0.25)
        ax1.text(t0 / 60, year_at(t0) + 20, s[3].split('(')[0][:24], fontsize=7, rotation=50)
    for ax in (ax1, ax2, ax3): ax.axvspan(NIGHT_T / 60, DUR / 60, color='#2c3e50', alpha=0.2)
    ax1.set_title('Siviglia: anni nel video (verde = soste, scuro = notte) e quota della camera')
    plt.tight_layout(); plt.savefig('regia_sevilla.png')
except Exception as e: print('grafico non fatto:', e)
