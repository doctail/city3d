# Controllo PRIMA del render (Parigi, 29 ott 2026: preview fermo con 61.772 blocchi). Conta gli oggetti della citta' come li
# fa build_render (anno di nascita a BIN anni, demolizione a DBIN anni, fascia di quota dem_band) e simula tutti i fotogrammi
# della regia: ogni oggetto che cambia (scala o visibilita') costa ~12 ms sulla GPU (RTX 5080, misurato 23 ott).
# Esce con codice 2 se il costo dei soli cambi supera il budget (city json "budget_cambi_h", di base 1,0 ore).
# Uso: python3 tools/costo_cambi.py city_<citta>.json DATA schedule_<citta>.json
import json, math, sys
import numpy as np
CFG = json.load(open(sys.argv[1])); DATA = sys.argv[2]; S = json.load(open(sys.argv[3]))
BIN = 4.0; DBIN = float(CFG.get('dbin', BIN)); BAND = float(CFG.get('dem_band', 3.0))
RH = int(CFG.get('rewind_hold', 1)); GS = int(CFG.get('grow_step', 1)); DMIN = float(CFG.get('dur_min', 0.4))
MS = float(CFG.get('ms_per_cambio', 12.0)); BUDGET = float(CFG.get('budget_cambi_h', 1.0))
B = json.load(open(f'{DATA}/buildings.json'))
try: H = json.load(open(f'{DATA}/hist.json'))
except FileNotFoundError: H = []
try:
    z = np.load(f'{DATA}/dem.npz'); D = z['D']; x0, y0, c = float(z['x0']), float(z['y0']), float(z['cell'])
    def dmin(r):
        a = np.array(r); ix = np.clip(((a[:, 0] - x0) / c).astype(int), 0, D.shape[1] - 1); iy = np.clip(((a[:, 1] - y0) / c).astype(int), 0, D.shape[0] - 1)
        return float(D[iy, ix].min())
except FileNotFoundError:
    def dmin(r): return 0.0
keys = set()
for o in B + H:
    d = o.get('d', 99999); y1 = o.get('y1', 0)
    keys.add((int(o['y']) if y1 else int(o['y'] // BIN), int(d // DBIN) if d < 9000 else 99999, int(BAND * math.floor(dmin(o['r']) / BAND)), int(y1)))
ch = [(k[0] if k[3] else k[0] * BIN, k[1] * DBIN if k[1] != 99999 else 1e9) for k in keys]
b0 = np.array([a for a, _ in ch], float); d0 = np.array([b for _, b in ch], float)
FPS = 24; NF = int(round(S['duration'] * FPS)); Yp = np.array(S['years'])
YF = np.interp(np.arange(NF) / FPS, Yp[:, 0], Yp[:, 1])
DF = np.array([max(DMIN, min(25.0, abs(YF[min(NF - 1, i + 6)] - YF[max(0, i - 6)]) / (12 / FPS) * 0.6)) for i in range(NF)])
prev = None; tot = 0; mx = 0
for i in range(NF):
    f = i
    if RH > 1 and i > 0 and YF[i] < YF[i - 1] - 1e-6: f = i - (i % RH)
    elif GS > 1: f = i - (i % GS)
    y, dd = YF[f], DF[f]
    t = np.clip((y - b0) / dd, 0, 1); g = np.where(t >= 1, 1, t + 0.18 * np.sin(np.pi * t))
    k = (y - d0) / dd; g = np.round(np.where(k >= 1, 0, np.where(k > 0, g * (1 - k), g)), 4)
    if prev is not None: n = int((g != prev).sum()); tot += n; mx = max(mx, n)
    prev = g
h = tot * MS / 1000 / 3600
print(f'[costo] oggetti citta\' {len(ch)}, cambi in tutto il video {tot}, max in un fotogramma {mx} (~{mx * MS / 1000:.0f} s), '
      f'costo dei soli cambi ~{h:.2f} h (budget {BUDGET} h)', flush=True)
if h > BUDGET:
    print('[costo] ERRORE: troppi oggetti che cambiano: il render costerebbe troppo. Fermo qui (nessun render).', flush=True); sys.exit(2)
