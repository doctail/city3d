# Regia di Copenaghen (19 ott 2026). Musica: A = "Waking to Reality" (Unicorn Heads, 4:32) dal secondo 0;
# B = "Monument" (TrackTribe, 4:11) da B_START. Il cambio di traccia e' nascosto nel bombardamento del 1807.
# Misure (salti di volume su 1 s): A +7,1 dB 0:30.8, +6,6 dB 0:53.8, CALO -7,3 dB 3:04 (incendio 1728), RIPRESA +7,5 dB 3:35
# (Frederiksstaden 1749), sfuma da 4:05 (bombardamento 1807). B: parte piano, +4,4 dB 0:25 (1852, cadono le mura),
# +4,5 dB 0:53.5, piccolo calo 2:02-2:11 (1940-45), cala 3:20.5 (finale notturno), fine 4:11.
# VELOCITA' DEL TEMPO AUTOMATICA: tra due ancore musicali il tempo libero (tolte le soste) va agli anni in proporzione agli
# edifici che nascono o muoiono quell'anno (veri + storici): edifici nuovi al secondo circa costanti. Limiti 0,5-8 anni/s.
# SOSTE: monumenti (4-6 s, il cantiere compresso in fasi) e incendi; ognuna con la sua inquadratura vicina.
# CAMERA: inquadrature con stacchi netti; dentro ognuna orbita + avvicinamento (parallasse). Sempre a sud/sud-ovest del
# bersaglio salvo eccezioni (col sole da sud-ovest il controsole rende tutto marrone).
# Uso: python regia_copenhagen.py data_copenhagen  -> schedule_copenhagen.json, schedule_copenhagen_night.json,
#      regia_copenhagen.png (grafico anni/secondo + soste), regia_copenhagen.txt (elenco soste ed eventi)
import json, math, sys, os
import numpy as np

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data_copenhagen'
FPS = 24
B_START = 260.0                     # secondo del video in cui parte "Monument"
DUR = B_START + 251.5               # fine di "Monument": 8:31.5
NIGHT_T = B_START + 200.5           # 3:20.5 di B: la musica cala, si passa alla notte
LM = json.load(open(f'{DATA}/landmarks.json'))
def lmc(name):   # centro e altezza di un monumento dalle sue parti
    ps = [p for p in LM['parts'] if p['name'].startswith(name)]
    xs = [p.get('cx', sum(q[0] for q in p.get('r', [[0, 0]])) / max(1, len(p.get('r', [1])))) for p in ps]
    ys = [p.get('cy', sum(q[1] for q in p.get('r', [[0, 0]])) / max(1, len(p.get('r', [1])))) for p in ps]
    return (float(np.median(xs)), float(np.median(ys))), max(p.get('z1', p.get('z0', 0) + p.get('hz', 0)) for p in ps)

# ---------- ancore musicali (t, anno) ----------
FIXED = [(0.0, 2026.0), (3.0, 2026.0), (9.5, 1167.0),           # oggi, riavvolgimento, titolo sul 1167
         (184.0, 1728.79),                                       # A 3:04 calo: incendio del 20 ottobre 1728
         (215.0, 1749.3),                                        # A 3:35 ripresa: Frederiksstaden
         (248.0, 1807.66),                                       # A sfuma: bombardamento (ponte tra le tracce)
         (B_START + 25.0, 1852.0),                               # B 0:25: cadono le mura
         (B_START + 122.25, 1940.25),                            # B 2:02: occupazione (9 aprile 1940)
         (B_START + 131.25, 1945.5),                             # B 2:11: liberazione
         (NIGHT_T, 2026.0)]
# ---------- soste: (anno inizio, anno fine, durata s, nome, inquadratura) ----------
# inquadratura: (monumento o punto, distanza m, elevazione gradi, azimut camera inizio, azimut fine, obiettivo mm)
SOSTE = [
    (1167.0, 1169.0, 6.0, 'Absalon builds his castle (1167)', ('Absalon castle', 260, 24, 205, 235, 35)),
    (1369.3, 1381.0, 5.0, 'Hanseatic League razes the castle (1369)', ('Copenhagen Castle', 330, 26, 190, 220, 35)),
    (1606.0, 1612.5, 5.0, 'Rosenborg Castle (1606)', ('Rosenborg', 260, 24, 200, 235, 35)),
    (1618.8, 1625.6, 6.0, 'Børsen and its dragon spire (1619-25)', ('Boersen', 240, 22, 150, 185, 35)),
    (1636.8, 1642.6, 5.0, 'The Round Tower (1637-42)', ('Rundetaarn', 200, 26, 190, 225, 35)),
    (1670.8, 1683.0, 5.0, 'Nyhavn is dug (1671-73)', ('Nyhavn', 330, 24, 120, 150, 35)),
    (1728.79, 1729.05, 10.0, 'GREAT FIRE OF 1728', ('fire1728', 900, 30, 185, 205, 35)),
    (1735.5, 1745.5, 4.0, 'Christiansborg I (1733-45)', ('Christiansborg 1', 380, 24, 200, 225, 35)),
    (1749.3, 1752.3, 4.5, "Our Saviour's spiral spire (1749-52)", ("Our Saviour's spire", 230, 18, 205, 235, 35)),
    (1752.3, 1760.5, 6.0, 'Frederiksstaden: Amalienborg (1750-60)', ('Amalienborg', 420, 26, 215, 245, 35)),
    (1794.14, 1794.40, 3.5, 'Christiansborg burns (1794)', ('Christiansborg 1', 450, 26, 200, 220, 35)),
    (1795.42, 1795.70, 4.0, 'FIRE OF 1795', ('fire1795', 800, 30, 190, 210, 35)),
    (1807.66, 1807.95, 14.0, 'BRITISH BOMBARDMENT (1807)', ('fire1807', 1000, 30, 180, 215, 35)),
    (1809.5, 1820.0, 5.0, 'Christiansborg rises again', ('Christiansborg 2', 420, 24, 195, 225, 35)),
    (1842.8, 1845.0, 4.0, 'Tivoli opens (1843)', ('Tivoli', 330, 28, 200, 230, 35)),
    (1876.5, 1883.5, 4.0, 'Marble Church rebuilt (1874)', ('Marble Church', 300, 22, 205, 235, 35)),
    (1884.74, 1885.0, 3.5, 'Christiansborg burns again (1884)', ('Christiansborg 2', 450, 26, 200, 220, 35)),
    (1886.5, 1891.6, 4.0, 'The great dome (1894)', ('Marble Church', 260, 20, 235, 255, 35)),
    (1893.5, 1905.5, 5.0, 'City Hall (1892-1905)', ('City Hall', 330, 22, 195, 225, 35)),
    (1917.5, 1928.5, 5.0, 'Christiansborg III and its tower (1907-28)', ('Christiansborg tower', 420, 20, 190, 225, 35)),
    (1929.0, 1934.5, 5.0, 'Grundtvig Church (1921-40)', ('Grundtvig Church', 300, 18, 215, 245, 35)),
    (1958.2, 1960.4, 4.5, "SAS Royal, the city's first skyscraper (1960)", ('SAS Royal Hotel', 330, 20, 200, 235, 35)),
    (1995.8, 2000.6, 5.0, 'The Øresund Bridge (2000)', ('Oresund Bridge', 5200, 14, 250, 265, 35)),
    (2000.8, 2004.6, 4.0, 'The Opera House (2005)', ('Opera House', 520, 20, 215, 240, 35)),
    (2004.8, 2008.3, 4.0, 'Royal Playhouse (2008)', ('Royal Playhouse', 360, 20, 200, 230, 35)),
    (2013.3, 2019.3, 5.0, 'CopenHill (2019)', ('CopenHill', 520, 22, 255, 285, 35)),
]
FIRE_PTS = {'fire1728': (330, 420), 'fire1795': (600, 230), 'fire1807': (350, 600)}

# ---------- attivita' per anno ----------
B = json.load(open(f'{DATA}/buildings.json')); H = json.load(open(f'{DATA}/hist.json'))
act = np.zeros(2030)
for o in B: act[int(o['y'])] += 1
for o in H:
    act[int(o['y'])] += 1
    if o.get('d', 9999) < 2027: act[int(o['d'])] += 0.6
act = np.convolve(act, np.ones(5) / 5, 'same')    # lisciata su 5 anni (anni tondi del BBR)

RMIN, RMAX = 0.5, 8.0   # anni/s fuori dalle soste
def alloc(y0, y1, T):
    """Distribuisce T secondi sugli anni [y0, y1) in proporzione all'attivita', con 1/RMAX <= s/anno <= 1/RMIN."""
    ys = np.arange(math.floor(y0), math.ceil(y1))
    if len(ys) == 0 or y1 - y0 < 1e-6: return [(y0, 0.0), (y1, T)]
    frac = np.array([min(y1, y + 1) - max(y0, y) for y in ys])
    w = (act[ys] + 3.0) ** 0.85 * frac
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
    w = np.array([(act[y] + 3.0) ** 0.85 * f for y, f in yrs]); fr = np.array([f for _, f in yrs])
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
YEARS.append((NIGHT_T, 2026.0)); YEARS.append((DUR, 2026.0))
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
    if m.sum() < 30: return (735.0, 0.0), 120.0   # quasi niente: stretti sul castello
    mx, my = np.median(cx[m]), np.median(cy[m]); r = np.percentile(np.hypot(cx[m] - mx, cy[m] - my), 85)
    if r < 400:   # primi secoli: nel quadro sia il villaggio sia il castello di Absalon (735, 0)
        d_ = math.hypot(mx - 735, my); mx, my = (mx + 735) / 2, my / 2; r = max(r, d_ / 2 + 60)
    return (float(mx), float(my)), float(max(140.0, r))   # citta' piccola = camera vicina (anteprima: castello minuscolo a 0:20)

# ---------- inquadrature ----------
def campos(tx, ty, tz, d, el, az):
    e, a = math.radians(el), math.radians(az)
    return (tx + d * math.cos(e) * math.sin(a), ty + d * math.cos(e) * math.cos(a), tz + d * math.sin(e))
SHOTS = []   # (t0, t1, target(x,y,z), d0, d1, el0, el1, az0, az1, mm)
def target_of(name):
    if name in FIRE_PTS: return (*FIRE_PTS[name], 0.0), 0
    (x, y), h = lmc(name); return (x, y, min(40.0, h * 0.35)), h
# apertura: 2026 dall'alto sul porto, riavvolgimento scendendo verso Slotsholmen
SHOTS.append((0.0, 3.0, (900, 300, 0), 7800, 7200, 34, 32, 200, 206, 35))
SHOTS.append((3.0, 9.5, (760, 50, 0), 7200, 1500, 32, 26, 206, 214, 35))
SHOTS.append((9.5, 12.0, (735, 0, 10), 1500, 420, 26, 24, 214, 205, 35))
alt = 0
prev_end = 12.0
for (t0, t1, s) in SOSTA_T:
    if t0 < 12.0: t0 = 12.0
    # tratto largo prima della sosta (se c'e' tempo): la citta' intera di quell'anno, orbita lenta
    if t0 - prev_end > 3.0:
        gap0, gap1 = prev_end, t0
        n_sub = max(1, int((gap1 - gap0) // 16))     # uno stacco ogni ~16 s
        for k in range(n_sub):
            a_, b_ = gap0 + (gap1 - gap0) * k / n_sub, gap0 + (gap1 - gap0) * (k + 1) / n_sub
            (mx, my), r = extent(year_at(b_)); alt += 1
            d = 1.0 * r + (450 if r > 700 else 180); el = 30 if alt % 2 else 22; az0 = (165, 200, 230, 185)[alt % 4]
            SHOTS.append((a_, b_, (mx, my, 0), d * 1.25, d * 0.70, el + 4, el - 4, az0, az0 + (38 if alt % 2 else -38), 35))
    name, d, el, az0, az1, mm = s[4]
    tgt, h = target_of(name)
    SHOTS.append((t0, t1, tgt, d * 1.25, d * 0.75, el + 4, el, az0 - 6, az1 + 6, mm))
    prev_end = t1
# dopo l'ultima sosta: tratto largo fino alla notte, poi tre inquadrature notturne
if NIGHT_T - prev_end > 3:
    n_sub = max(1, int((NIGHT_T - prev_end) // 15))
    for k in range(n_sub):
        a_, b_ = prev_end + (NIGHT_T - prev_end) * k / n_sub, prev_end + (NIGHT_T - prev_end) * (k + 1) / n_sub
        (mx, my), r = extent(2026); alt += 1
        d = 0.8 * r + 700; el = (24, 18, 30)[alt % 3]; az0 = (175, 215, 240)[alt % 3]
        SHOTS.append((a_, b_, (mx * 0.5 + 900, my * 0.5 + 200, 0), d * 1.2, d * 0.75, el + 3, el - 3, az0, az0 + 36, 35))
# notte: la prima inquadratura (Tivoli) ospita il tramonto (dusk.py: 0-5 s tramonto, 5-10 s crepuscolo): orbita lenta e ampia
NIGHT_SHOTS = [(NIGHT_T, NIGHT_T + 19, target_of('Tivoli')[0], 640, 330, 26, 17, 185, 250, 35),
               (NIGHT_T + 19, NIGHT_T + 35, (1500, 420, 10), 1000, 520, 18, 12, 120, 185, 35),     # Nyhavn, Opera, porto
               (NIGHT_T + 35, DUR, (700, 200, 0), 3000, 6200, 22, 32, 190, 235, 35)]                # ultima: la citta' intera si allontana
SHOTS += NIGHT_SHOTS
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
sched = {'_doc': 'Copenaghen, regia automatica (regia_copenhagen.py). Musica A Waking to Reality 0-4:32, B Monument da 4:20.',
         'duration': DUR, 'lens': 35, 'years': [[t, y] for t, y in YEARS], 'cam': cam,
         'night_t': NIGHT_T, 'b_start': B_START,
         'soste': [[round(t0, 2), round(t1, 2), s[0], s[1], s[3]] for t0, t1, s in SOSTA_T]}
json.dump(sched, open('schedule_copenhagen.json', 'w'))
# notte: stessa camera, anno fermo al 2026, solo dalla notte in poi (passata separata --night)
json.dump(dict(sched, years=[[0, 2026], [DUR, 2026]]), open('schedule_copenhagen_night.json', 'w'))

# ---------- controllo: grafico e elenco ----------
ts = np.arange(0, DUR, 0.25); yv = np.array([year_at(t) for t in ts]); rate = np.gradient(yv, ts)
lines = [f'Durata {int(DUR // 60)}:{DUR % 60:04.1f}  fotogrammi {int(DUR * FPS)}  inquadrature {len(SHOTS)}  stacco medio ogni {DUR / len(SHOTS):.1f} s', '',
         'SOSTE (video -> anni):']
for t0, t1, s in SOSTA_T: lines.append(f'  {int(t0 // 60)}:{t0 % 60:04.1f}-{int(t1 // 60)}:{t1 % 60:04.1f}  {s[0]:.1f}->{s[1]:.1f}  {s[3]}')
lines += ['', 'ANNO OGNI 30 s:'] + [f'  {int(t // 60)}:{int(t % 60):02d}  {year_at(t):7.1f}  ({abs(rate[int(t * 4)]):.2f} anni/s)' for t in range(0, int(DUR), 30)]
fr = abs(rate[(ts > 12) & (ts < NIGHT_T)])
lines += ['', f'Velocita fuori dalle soste: mediana {np.median(fr):.2f} anni/s, max {fr.max():.1f} anni/s']
open('regia_copenhagen.txt', 'w').write('\n'.join(lines)); print('\n'.join(lines))
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7.5), dpi=90, sharex=True)
    ax1.plot(ts / 60, yv, color='#1f6f8b', lw=2); ax1.set_ylabel('anno'); ax1.grid(alpha=0.3)
    ax2.plot(ts / 60, np.clip(abs(rate), 0, 12), color='#c0392b', lw=1.5); ax2.set_ylabel('anni al secondo'); ax2.set_xlabel('minuti di video'); ax2.grid(alpha=0.3)
    ax2.axhline(8, color='grey', ls='--', lw=0.8); ax2.axhline(0.5, color='grey', ls='--', lw=0.8)
    for t0, t1, s in SOSTA_T:
        for ax in (ax1, ax2): ax.axvspan(t0 / 60, t1 / 60, color='#f39c12' if 'FIRE' in s[3] or 'BOMB' in s[3] or 'burns' in s[3] else '#27ae60', alpha=0.25)
        ax1.text(t0 / 60, year_at(t0) + 15, s[3].split('(')[0][:22], fontsize=7, rotation=60)
    for ax in (ax1, ax2):
        ax.axvline(B_START / 60, color='purple', lw=1); ax.axvspan(NIGHT_T / 60, DUR / 60, color='#2c3e50', alpha=0.2)
    ax1.text(B_START / 60 + 0.03, 1200, 'B: Monument', color='purple', fontsize=9); ax1.text(NIGHT_T / 60 + 0.05, 1200, 'notte', fontsize=9)
    ax1.set_title('Copenaghen: anni nel video (verde = soste monumenti, arancio = incendi, viola = cambio traccia)')
    plt.tight_layout(); plt.savefig('regia_copenhagen.png')
except Exception as e: print('grafico non fatto:', e)
