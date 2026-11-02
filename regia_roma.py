# Regia di Roma (2 nov 2026), stile Latos + soste sui monumenti. Anni negativi = a.C. Niente notte.
# Durata ~4:30. Musica da agganciare al montaggio (le ancore qui sono per contenuto, non per traccia).
# Uso: python regia_roma.py data_roma -> schedule_roma.json, regia_roma.txt, regia_roma.png
import json, math, sys, os
import numpy as np

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data_roma'
FPS = 24
DUR = 272.0
NIGHT_T = DUR
B_START = DUR
OFF = 800
LM = json.load(open(f'{DATA}/landmarks.json'))
def lmc(name):
    ps = [p for p in LM['parts'] if p['name'].startswith(name)]
    xs = [p.get('cx', sum(q[0] for q in p.get('r', [[0, 0]])) / max(1, len(p.get('r', [1])))) for p in ps]
    ys = [p.get('cy', sum(q[1] for q in p.get('r', [[0, 0]])) / max(1, len(p.get('r', [1])))) for p in ps]
    return (float(np.median(xs)), float(np.median(ys))), max(p.get('z1', p.get('z0', 0) + p.get('hz', 0)) for p in ps)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hist_roma import L as LL, PALATINE, CAPITOL
FIRE_PTS = {'palatine': (PALATINE[0] - 60, PALATINE[1] + 60), 'center': (300, -600), 'bend': (-900, 300), 'walls': (600, -400)}

# ---------- ancore (t, anno) ----------
FIXED = [(0.0, 2026.0), (3.0, 2026.0), (8.0, -753.0),
         (70.0, -30.0),        # fine della repubblica
         (118.0, 271.0),       # mura Aureliane
         (150.0, 560.0),       # dopo la guerra gotica: la citta' e' vuota
         (172.0, 1100.0),
         (210.0, 1667.0),      # Roma barocca
         (238.0, 1871.0),      # capitale d'Italia
         (264.0, 2026.0), (DUR, 2026.0)]
# soste: (anno inizio, anno fine, durata s, testo, (monumento o punto, distanza, elev, az0, az1, mm))
SOSTE = [
    (-753.0, -735.0, 6.0, 'Romulus founds Rome (753 BC)', ('palatine', 300, 32, 195, 235, 35)),
    (-509.0, -504.0, 4.0, 'Temple of Jupiter (509 BC)', ('Temple of Jupiter', 300, 24, 205, 232, 35)),
    (-378.0, -372.0, 4.5, 'The Servian Wall (378 BC)', ('Servian Wall', 2300, 30, 195, 215, 35)),
    (-329.0, -322.0, 3.5, 'Circus Maximus (329 BC)', ('Circus Maximus', 520, 22, 150, 178, 35)),
    (-46.0, -26.0, 5.0, 'Caesar and Augustus rebuild Rome', ('Circus Maximus', 900, 26, 175, 205, 35)),
    (-13.5, -11.0, 3.0, 'Theatre of Marcellus (13 BC)', ('Theatre of Marcellus', 260, 24, 200, 228, 35)),
    (71.5, 80.5, 6.0, 'The Colosseum (AD 72-80)', ('Colosseum', 340, 26, 195, 230, 35)),
    (112.5, 113.5, 3.0, "Trajan's Column (113)", ("Trajan's Column", 200, 20, 200, 225, 35)),
    (117.5, 126.0, 5.0, 'The Pantheon (125)', ('Pantheon', 230, 24, 205, 235, 35)),
    (134.5, 138.0, 3.5, "Hadrian's Mausoleum (135)", ("Castel Sant'Angelo", 300, 24, 160, 190, 35)),
    (211.5, 216.5, 4.0, 'Baths of Caracalla (216)', ('Baths of Caracalla', 520, 26, 200, 228, 35)),
    (271.0, 276.0, 6.0, 'The Aurelian Walls (271)', ('walls', 4300, 32, 190, 212, 35)),
    (325.5, 330.0, 4.0, "Old St Peter's (326)", ("Old St Peter's", 380, 24, 150, 180, 35)),
    (410.0, 410.8, 4.0, 'Alaric sacks Rome (410)', ('center', 3000, 34, 200, 214, 35)),
    (537.0, 560.0, 7.0, 'The aqueducts are cut (537)', ('center', 3600, 38, 205, 225, 35)),
    (1349.0, 1349.6, 4.0, 'Earthquake: the Colosseum falls (1349)', ('Colosseum', 330, 26, 160, 190, 35)),
    (1505.5, 1547.0, 4.0, "New St Peter's (1506)", ("St Peter's Basilica", 800, 24, 140, 170, 35)),
    (1584.5, 1593.0, 5.0, "Michelangelo's dome (1590)", ("St Peter's Basilica", 700, 22, 170, 200, 35)),
    (1655.5, 1667.0, 4.0, "Bernini's colonnade (1667)", ("St Peter's Square", 520, 30, 120, 150, 35)),
    (1870.6, 1871.4, 4.0, 'Rome, capital of Italy (1871)', ('center', 3300, 34, 205, 222, 35)),
    (1884.5, 1911.0, 5.0, 'The Vittoriano (1885-1911)', ('Vittoriano', 380, 22, 195, 225, 35)),
    (1952.5, 1960.5, 3.5, 'Rome Olympics (1960)', ('Stadio Olimpico', 650, 26, 170, 200, 35)),
]

# ---------- attivita' per anno ----------
B = json.load(open(f'{DATA}/buildings.json')); H = json.load(open(f'{DATA}/hist.json'))
act = np.zeros(2030 + OFF)
for o in B: act[int(math.floor(o['y'])) + OFF] += 1
for o in H:
    act[int(math.floor(o['y'])) + OFF] += 1
    if o.get('d', 9999) < 2027: act[int(math.floor(o['d'])) + OFF] += 0.6
act = np.convolve(act, np.ones(5) / 5, 'same')    # lisciata su 5 anni (anni tondi del BBR)

RMIN, RMAX = 2.0, 45.0   # anni/s fuori dalle soste
def alloc(y0, y1, T):
    """Distribuisce T secondi sugli anni [y0, y1) in proporzione all'attivita', con 1/RMAX <= s/anno <= 1/RMIN."""
    ys = np.arange(math.floor(y0), math.ceil(y1))
    if len(ys) == 0 or y1 - y0 < 1e-6: return [(y0, 0.0), (y1, T)]
    frac = np.array([min(y1, y + 1) - max(y0, y) for y in ys])
    w = (act[ys + OFF] + 3.0) ** 0.85 * frac
    lo, hi = frac / RMAX, frac / RMIN
    s = np.clip(w / w.sum() * T, lo, hi)
    for _ in range(60):       # riempimento a livelli rispettando i limiti
        err = T - s.sum()
        if abs(err) < 1e-6: break
        free = (s > lo + 1e-9) & (s < hi - 1e-9) if err != 0 else None
        free = (s < hi - 1e-9) if err > 0 else (s > lo + 1e-9)
        if not free.any(): break
        s[free] += err * w[free] / w[free].sum(); s = np.clip(s, lo, hi)
    if abs(T - s.sum()) > 0.05: s *= T / s.sum()     # limiti impossibili: si scala (lo dice il controllo)
    pts = [(y0, 0.0)]; acc = 0.0
    for y, sv in zip(ys, s):
        acc += sv; pts.append((min(y1, y + 1), acc))
    return pts

# ---------- linea del tempo ----------
YEARS = []   # (t, anno)
SOSTA_T = []
for (ta, ya), (tb, yb) in zip(FIXED, FIXED[1:]):
    if yb < ya or tb - ta < 0.01 or (ya == yb):   # riavvolgimento o pausa: lineare (ease)
        for k in range(0, 21):
            u = k / 20; u2 = u * u * (3 - 2 * u); YEARS.append((ta + (tb - ta) * u, ya + (yb - ya) * u2))
        continue
    ss = [s for s in SOSTE if ya <= s[0] < yb]
    T_free = (tb - ta) - sum(s[2] for s in ss)
    free_len = (yb - ya) - sum(s[1] - s[0] for s in ss)
    # pezzi liberi tra le soste: tempo in proporzione all'attivita' complessiva del pezzo
    pieces = []; cur = ya
    for s in ss: pieces.append((cur, s[0])); cur = s[1]
    pieces.append((cur, yb))
    # tempo dei pezzi: distribuzione congiunta con i limiti 0,5-8 anni/s (prima si divideva e poi si limitava: anni '30 a 0,33)
    yrs, own = [], []
    for i, (p0, p1) in enumerate(pieces):
        for y in np.arange(math.floor(p0), math.ceil(p1)):
            fr_ = min(p1, y + 1) - max(p0, y)
            if fr_ > 1e-6: yrs.append((int(y), fr_)); own.append(i)
    w = np.array([(act[y + OFF] + 3.0) ** 0.85 * f for y, f in yrs]); fr = np.array([f for _, f in yrs])
    lo, hi = fr / RMAX, fr / RMIN; sv = np.clip(w / w.sum() * T_free, lo, hi)
    for _ in range(80):
        err = T_free - sv.sum()
        if abs(err) < 1e-6: break
        free = (sv < hi - 1e-9) if err > 0 else (sv > lo + 1e-9)
        if not free.any(): break
        sv[free] += err * w[free] / w[free].sum(); sv = np.clip(sv, lo, hi)
    if abs(T_free - sv.sum()) > 0.05: print(f'  [!] limiti impossibili tra {ya} e {yb}: scala {T_free / sv.sum():.2f}'); sv *= T_free / sv.sum()
    Ts = [float(sv[np.array(own) == i].sum()) for i in range(len(pieces))]
    t = ta
    for i, (p0, p1) in enumerate(pieces):
        for yv, dt in alloc(p0, p1, Ts[i]) if p1 > p0 else [(p0, 0.0)]:
            YEARS.append((t + dt, yv))
        t += Ts[i]
        if i < len(ss):
            s = ss[i]; SOSTA_T.append((t, t + s[2], s))
            for k in range(1, 11):
                u = k / 10; YEARS.append((t + s[2] * u, s[0] + (s[1] - s[0]) * u))
            t += s[2]
YEARS.append((DUR, 2026.0))
YEARS = sorted({round(float(t), 3): (round(float(t), 3), round(float(y), 4)) for t, y in YEARS}.values())
# monotonia nel tempo (riavvolgimento a parte)
def year_at(t):
    if t <= YEARS[0][0]: return YEARS[0][1]
    for (a, ya), (b, yb) in zip(YEARS, YEARS[1:]):
        if t <= b: return ya + (yb - ya) * (t - a) / max(1e-9, b - a)
    return YEARS[-1][1]

# ---------- estensione della citta' per anno (per le inquadrature larghe) ----------
cx = np.array([sum(p[0] for p in o['r']) / len(o['r']) for o in B + H]); cy = np.array([sum(p[1] for p in o['r']) / len(o['r']) for o in B + H])
by = np.array([o['y'] for o in B + H]); bd = np.array([o.get('d', 9999) for o in B + H])
def extent(y):
    m = (by <= y) & (bd > y)
    if m.sum() < 30: return FIRE_PTS['palatine'], 200.0
    mx, my = np.median(cx[m]), np.median(cy[m]); r = np.percentile(np.hypot(cx[m] - mx, cy[m] - my), 85)
    return (float(mx), float(my)), float(max(220.0, r))   # citta' piccola = camera vicina (anteprima: castello minuscolo a 0:20)

# ---------- inquadrature ----------
def campos(tx, ty, tz, d, el, az):
    e, a = math.radians(el), math.radians(az)
    return (tx + d * math.cos(e) * math.sin(a), ty + d * math.cos(e) * math.cos(a), tz + d * math.sin(e))
SHOTS = []   # (t0, t1, target(x,y,z), d0, d1, el0, el1, az0, az1, mm)
def target_of(name):
    if name in FIRE_PTS: return (*FIRE_PTS[name], 0.0), 0
    (x, y), h = lmc(name); return (x, y, min(40.0, h * 0.35)), h
# apertura: 2026 dall'alto sul porto, riavvolgimento scendendo verso Slotsholmen
SHOTS.append((0.0, 3.0, (0, -500, 0), 9000, 8400, 36, 34, 200, 206, 35))
SHOTS.append((3.0, 8.0, (*FIRE_PTS['palatine'], 0), 8400, 900, 34, 26, 206, 214, 35))
alt = 0
prev_end = 8.0
for (t0, t1, s) in SOSTA_T:
    if t0 < 8.0: t0 = 8.0
    # tratto largo prima della sosta (se c'e' tempo): la citta' intera di quell'anno, orbita lenta
    if t0 - prev_end > 3.0:
        gap0, gap1 = prev_end, t0
        n_sub = max(1, int((gap1 - gap0) // 16))     # uno stacco ogni ~16 s
        for k in range(n_sub):
            a_, b_ = gap0 + (gap1 - gap0) * k / n_sub, gap0 + (gap1 - gap0) * (k + 1) / n_sub
            (mx, my), r = extent(year_at(b_)); alt += 1
            d = 1.15 * r + (500 if r > 700 else 260); el = 30 if alt % 2 else 22; az0 = (165, 200, 230, 185)[alt % 4]
            SHOTS.append((a_, b_, (mx, my, 0), d * 1.25, d * 0.70, el + 4, el - 4, az0, az0 + (38 if alt % 2 else -38), 35))
    name, d, el, az0, az1, mm = s[4]
    tgt, h = target_of(name)
    SHOTS.append((t0, t1, tgt, d * 1.25, d * 0.75, el + 4, el, az0 - 6, az1 + 6, mm))
    prev_end = t1
if DUR - prev_end > 3:
    n_sub = max(1, int((DUR - prev_end) // 9))
    fin = [((300, -600, 0), 4200, 3000, 30, 24, 200, 236), ((-600, 400, 0), 1700, 1100, 18, 14, 150, 185), ((0, -300, 0), 3000, 9000, 26, 36, 205, 222)]
    for k in range(n_sub):
        a_, b_ = prev_end + (DUR - prev_end) * k / n_sub, prev_end + (DUR - prev_end) * (k + 1) / n_sub
        tg, d0, d1, e0, e1, a0, a1 = fin[min(k, 2) if k < n_sub - 1 else 2]
        SHOTS.append((a_, b_, tg, d0, d1, e0, e1, a0, a1, 35))
SHOTS.sort(key=lambda s: s[0])

def ease(u): return u * u * (3 - 2 * u)
cam = []
for i, (t0, t1, tg, d0, d1, e0, e1, a0, a1, mm) in enumerate(SHOTS):
    n = max(2, int((t1 - t0) / 0.5))
    for k in range(n + 1):
        u = k / n; ue = ease(u) * 0.5 + u * 0.5
        tt = t0 + (t1 - t0) * u
        if k == 0 and i > 0: tt = t0 + 1.0 / FPS      # stacco netto: la chiave precedente chiude a t0
        p = campos(*tg, d0 + (d1 - d0) * ue, e0 + (e1 - e0) * ue, a0 + (a1 - a0) * ue)
        cam.append([round(tt, 3), [round(v, 1) for v in p], [round(v, 1) for v in tg], mm])
cam.sort(key=lambda c: c[0])
sched = {'_doc': 'Roma, regia automatica (regia_roma.py). Niente notte.',
         'duration': DUR, 'lens': 35, 'years': [[t, y] for t, y in YEARS], 'cam': cam,
         'soste': [[round(t0, 2), round(t1, 2), s[0], s[1], s[3]] for t0, t1, s in SOSTA_T]}
json.dump(sched, open('schedule_roma.json', 'w'))

# ---------- controllo: grafico e elenco ----------
ts = np.arange(0, DUR, 0.25); yv = np.array([year_at(t) for t in ts]); rate = np.gradient(yv, ts)
lines = [f'Durata {int(DUR // 60)}:{DUR % 60:04.1f}  fotogrammi {int(DUR * FPS)}  inquadrature {len(SHOTS)}  stacco medio ogni {DUR / len(SHOTS):.1f} s', '',
         'SOSTE (video -> anni):']
for t0, t1, s in SOSTA_T: lines.append(f'  {int(t0 // 60)}:{t0 % 60:04.1f}-{int(t1 // 60)}:{t1 % 60:04.1f}  {s[0]:.1f}->{s[1]:.1f}  {s[3]}')
lines += ['', 'ANNO OGNI 30 s:'] + [f'  {int(t // 60)}:{int(t % 60):02d}  {year_at(t):7.1f}  ({abs(rate[int(t * 4)]):.2f} anni/s)' for t in range(0, int(DUR), 30)]
fr = abs(rate[(ts > 8) & (ts < DUR - 2)])
lines += ['', f'Velocita fuori dalle soste: mediana {np.median(fr):.2f} anni/s, max {fr.max():.1f} anni/s']
open('regia_roma.txt', 'w').write('\n'.join(lines)); print('\n'.join(lines))
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7.5), dpi=90, sharex=True)
    ax1.plot(ts / 60, yv, color='#1f6f8b', lw=2); ax1.set_ylabel('anno'); ax1.grid(alpha=0.3)
    ax2.plot(ts / 60, np.clip(abs(rate), 0, 60), color='#c0392b', lw=1.5); ax2.set_ylabel('anni al secondo'); ax2.set_xlabel('minuti di video'); ax2.grid(alpha=0.3)
    ax2.axhline(RMAX, color='grey', ls='--', lw=0.8)
    for t0, t1, s in SOSTA_T:
        for ax in (ax1, ax2): ax.axvspan(t0 / 60, t1 / 60, color='#f39c12' if 'FIRE' in s[3] or 'BOMB' in s[3] or 'burns' in s[3] else '#27ae60', alpha=0.25)
        ax1.text(t0 / 60, year_at(t0) + 15, s[3].split('(')[0][:22], fontsize=7, rotation=60)
    for ax in (ax1, ax2):
        pass
    
    ax1.set_title('Roma: anni nel video (verde = soste monumenti, arancio = incendi, viola = cambio traccia)')
    plt.tight_layout(); plt.savefig('regia_roma.png')
except Exception as e: print('grafico non fatto:', e)
