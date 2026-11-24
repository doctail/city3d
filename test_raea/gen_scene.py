#!/usr/bin/env python3
"""Test A/B (Blender vs raea): costruisce la scena raea di New York dai STESSI dati di build_render.py.

Legge  data_nyc_src/{buildings,land,landphases,parks}.json.gz  e  schedule_nyc.json
Scrive raea/scene.gen.ts  (dati: fotogrammi 1..N con anno, durata di crescita e camera; blocchi di edifici
(cella spaziale x intervallo di anni x classe colore) come triangoli; terra, fasi di terra, parchi).

Mappa coordinate: Blender (x, y, z su) -> raea/Bevy (x, z, -y), una rotazione propria (niente specchio).
Dipendenze: numpy, mapbox_earcut (pip install numpy mapbox_earcut). Niente shapely.

Uso: python3 gen_scene.py [--frames 480] [--out raea/scene.gen.ts] [--stats out/scena_stats.json]
                          [--buildings FILE.json[.gz]] [--min-area 12] [--cell 600] [--ybin 5] [--no-cull]
"""
import argparse, gzip, json, math, os, sys, time
import numpy as np
import mapbox_earcut as earcut

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument('--frames', type=int, default=480)
ap.add_argument('--out', default=os.path.join(HERE, 'raea', 'scene.gen.ts'))
ap.add_argument('--stats', default=os.path.join(HERE, 'out', 'scena_stats.json'))
ap.add_argument('--buildings', default=os.path.join(ROOT, 'data_nyc_src', 'buildings.json.gz'))
ap.add_argument('--schedule', default=os.path.join(ROOT, 'schedule_nyc.json'))
ap.add_argument('--min-area', type=float, default=12.0)   # stesso valore di city_nyc.json "min_area_m2"
ap.add_argument('--cell', type=float, default=1500.0)
ap.add_argument('--ybin', type=float, default=8.0)
ap.add_argument('--margin', type=float, default=0.06)     # margine del taglio fuori inquadratura (frazione)
ap.add_argument('--no-cull', action='store_true')
A = ap.parse_args()
FPS = 24
t0 = time.time()
def log(*x): print('[gen_scene]', *x, f'({time.time()-t0:.1f}s)', flush=True)
def jload(p): return json.load(gzip.open(p) if p.endswith('.gz') else open(p))

S = jload(A.schedule); NF = A.frames
CITY = jload(os.path.join(ROOT, 'city_nyc.json'))
WATER_Z = float(CITY.get('water_z', -1.5)); DUR_MIN = float(CITY.get('dur_min', 0.4))

# ---- anni, durata di crescita, camera per fotogramma: la stessa logica di build_render.py (year_at, _dur, CAMKEYS) ----
def lerp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a_, ya), (b_, yb) in zip(pts, pts[1:]):
        if v <= b_: return ya + (yb - ya) * (v - a_) / (b_ - a_)
    return pts[-1][1]
def year_at(f): return lerp((f - 1) / FPS, S['years'])
def dur(f):
    q = max(1, FPS // 4); rate = abs(year_at(f + q) - year_at(max(1, f - q))) / (2 * q / FPS)
    return max(DUR_MIN, min(25.0, rate * 0.6))
camkeys = {int(round(k[0] * FPS)) + 1: (k[1], k[2], float(k[3]) if len(k) > 3 else float(S.get('lens', 30))) for k in S['cam']}
assert all(f in camkeys for f in range(1, NF + 1)), 'chiavi camera mancanti nel tratto richiesto'
def B2R(p): return [round(p[0], 2), round(p[2], 2), round(-p[1], 2)]   # Blender -> raea
YEARS = [round(year_at(f), 4) for f in range(1, NF + 1)]
DURS = [round(dur(f), 4) for f in range(1, NF + 1)]
CAM = [B2R(camkeys[f][0]) + B2R(camkeys[f][1]) + [camkeys[f][2]] for f in range(1, NF + 1)]
log('fotogrammi', NF, 'anni', YEARS[0], '->', min(YEARS), 'durata scena', NF / FPS, 's')

# ---- taglio fuori inquadratura (proiezione del baricentro in ogni 3o fotogramma + ultimo) ----
def frustum_mask(cx, cy, rad, h):
    keep = np.zeros(len(cx), bool); asp = 16 / 9
    for i in list(range(0, NF, 3)) + [NF - 1]:
        p = np.array(camkeys[i + 1][0]); tg = np.array(camkeys[i + 1][1]); lens = camkeys[i + 1][2]
        fw = tg - p; fw /= np.linalg.norm(fw); rt = np.cross(fw, [0, 0, 1]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw)
        kx = 18.0 / lens; ky = kx / asp
        for zz in (0.0, 1.0):   # base e tetto
            P = np.c_[cx, cy, h * zz] - p; d = P @ fw; ok = d > 1.0
            dd = np.where(ok, d, 1.0); nx = (P @ rt) / dd / kx; ny = (P @ up) / dd / ky
            mx = 1 + A.margin + rad / dd / kx
            keep |= ok & (np.abs(nx) < mx) & (np.abs(ny) < 1 + A.margin + rad / dd / ky)
    return keep

# ---- edifici ----
B = jload(A.buildings); n_all = len(B)
rings = []; hs = []; ys = []
for b in B:
    r = b['r']
    if len(r) > 1 and r[0] == r[-1]: r = r[:-1]
    if len(r) < 3: continue
    rings.append(np.asarray(r, float)); hs.append(max(3.0, float(b['h']))); ys.append(float(b['y']))
def area(r): x, y = r[:, 0], r[:, 1]; return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
ar = np.array([area(r) for r in rings]); ok = np.abs(ar) >= max(6.0, A.min_area)   # build_render scarta area < 6; city json min_area_m2
rings = [r for r, k in zip(rings, ok) if k]; hs = np.array(hs)[ok]; ys = np.array(ys)[ok]; ar = ar[ok]
cx = np.array([r[:, 0].mean() for r in rings]); cy = np.array([r[:, 1].mean() for r in rings])
rad = np.array([np.hypot(r[:, 0] - m, r[:, 1] - n).max() for r, m, n in zip(rings, cx, cy)])
keep = np.ones(len(rings), bool) if A.no_cull else frustum_mask(cx, cy, rad, hs)
n_valid, n_view = len(rings), int(keep.sum())
log('edifici totali', n_all, 'validi', n_valid, 'in inquadratura (almeno un fotogramma)', n_view)

# ---- classi colore (stile city_nyc.json: muri caldi prima del 1850, chiari dopo, vetro per le torri) ----
CLASSES = [('old', '#d9cdb1'), ('old2', '#c8b896'), ('new', '#e2d7bf'), ('new2', '#cfc3a6'), ('mid', '#b9b2a4'), ('mid2', '#a8a399'), ('glass', '#8fa9b8'), ('glass2', '#9ab3c0')]
def cls_of(y, h, a, i):
    t = i % 2
    if h > 70 and y > 1955 and a > 400: return 6 + t
    if y < 1850: return 0 + t
    if h > 35: return 4 + t
    return 2 + t

def tri_building(ring, h):
    """triangoli (coordinate raea) di un prisma: pareti + tetto piatto; anello antiorario"""
    if area(ring) < 0: ring = ring[::-1]
    n = len(ring); out = []
    for i in range(n):
        (x0, y0), (x1, y1) = ring[i], ring[(i + 1) % n]
        b0 = (x0, 0.0, -y0); b1 = (x1, 0.0, -y1); t0_ = (x0, h, -y0); t1 = (x1, h, -y1)
        out += [b0, b1, t1, b0, t1, t0_]
    idx = earcut.triangulate_float64(ring, np.array([n], dtype=np.uint32))
    for a_, b_, c_ in idx.reshape(-1, 3):
        pa, pb, pc = ring[a_], ring[b_], ring[c_]
        if (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]) < 0: b_, c_ = c_, b_
        for k in (a_, b_, c_): out.append((ring[k][0], h, -ring[k][1]))
    return out

chunks = {}
ids = np.nonzero(keep)[0]
for j, i in enumerate(ids):
    key = (int(cx[i] // A.cell), int(cy[i] // A.cell), int(ys[i] // A.ybin), cls_of(ys[i], hs[i], ar[i], int(abs(ar[i])) + j))
    try: tri = tri_building(rings[i], float(hs[i]))
    except Exception: continue
    chunks.setdefault(key, []).append(tri)
log('blocchi', len(chunks))
CH = []; ntri = 0
for (gx, gy, yb, c), tris in sorted(chunks.items(), key=lambda kv: (kv[0][2], kv[0][0], kv[0][1], kv[0][3])):
    flat = [round(v, 2) for t in tris for p in t for v in p]
    ntri += len(flat) // 9
    CH.append({'b0': yb * A.ybin, 'c': c, 'n': len(tris), 'p': flat})

# ---- terra, fasi di terra, parchi (solo cio' che tocca la zona vista, bbox dei fabbricati in vista + 4 km) ----
if n_view:
    bx0, bx1 = float(cx[keep].min()) - 4000, float(cx[keep].max()) + 4000; by0, by1 = float(cy[keep].min()) - 4000, float(cy[keep].max()) + 4000
else: bx0 = bx1 = by0 = by1 = 0
camxy = np.array([[camkeys[f][0][0], camkeys[f][0][1]] for f in camkeys]); bx0 = min(bx0, camxy[:, 0].min() - 4000); bx1 = max(bx1, camxy[:, 0].max() + 4000)
by0 = min(by0, camxy[:, 1].min() - 4000); by1 = max(by1, camxy[:, 1].max() + 4000)
def touches(r): return not (r[:, 0].max() < bx0 or r[:, 0].min() > bx1 or r[:, 1].max() < by0 or r[:, 1].min() > by1)
def flat_poly(r, y):
    r = np.asarray(r, float)
    if len(r) > 1 and (r[0] == r[-1]).all(): r = r[:-1]
    if len(r) < 3: return []
    if area(r) < 0: r = r[::-1]
    idx = earcut.triangulate_float64(r, np.array([len(r)], dtype=np.uint32)); out = []
    for a_, b_, c_ in idx.reshape(-1, 3):
        pa, pb, pc = r[a_], r[b_], r[c_]
        if (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]) < 0: b_, c_ = c_, b_
        for k in (a_, b_, c_): out += [round(r[k][0], 1), y, round(-r[k][1], 1)]
    return out
D = os.path.join(ROOT, 'data_nyc_src')
land = []
for r in jload(os.path.join(D, 'land.json.gz')):
    r = np.asarray(r, float)
    if len(r) >= 3 and touches(r): land += flat_poly(r, 0.0)
phases = {}
for ph in jload(os.path.join(D, 'landphases.json.gz')):
    r = np.asarray(ph['r'], float)
    if len(r) >= 3 and touches(r): phases.setdefault((float(ph['from']), float(ph['to'])), []).extend(flat_poly(r, 0.04))
PH = [{'from': k[0], 'to': min(k[1], 99999.0), 'p': v} for k, v in sorted(phases.items()) if v]
parks = []
for r in jload(os.path.join(D, 'parks.json.gz')):
    r = np.asarray(r, float)
    if len(r) >= 3 and touches(r): parks += flat_poly(r, 0.08)
log('terra triangoli', len(land) // 9, 'fasi', len(PH), 'parchi triangoli', len(parks) // 9)

data = {'frames': NF, 'fps': FPS, 'years': YEARS, 'durs': DURS, 'cam': CAM, 'waterY': WATER_Z, 'classes': [c for _, c in CLASSES],
        'chunks': CH, 'land': land, 'phases': PH, 'parks': parks}
os.makedirs(os.path.dirname(A.out), exist_ok=True)
with open(A.out, 'w') as f:
    f.write('// GENERATO da test_raea/gen_scene.py: non modificare a mano.\n')
    f.write('export type Chunk = { b0: number; c: number; n: number; p: number[] };\n')
    f.write('export type Phase = { from: number; to: number; p: number[] };\n')
    f.write('export type SceneData = { frames: number; fps: number; years: number[]; durs: number[]; cam: number[][]; waterY: number; classes: string[]; chunks: Chunk[]; land: number[]; phases: Phase[]; parks: number[] };\n')
    f.write('export const DATA: SceneData = ')
    json.dump(data, f, separators=(',', ':')); f.write(';\n')
mb = os.path.getsize(A.out) / 1e6
yr_min = min(YEARS)
vis = {str(y): int(((ys[keep] <= y)).sum()) for y in (1650, 1750, 1800, 1850, 1900, 1950, 2000, 2026)}
stats = {'edifici_totali_file': n_all, 'edifici_validi': n_valid, 'edifici_in_inquadratura_nei_20s': n_view, 'edifici_vivi_per_anno_in_inquadratura': vis,
         'anno_primo_fotogramma': YEARS[0], 'anno_ultimo_fotogramma': YEARS[-1], 'anno_minimo': yr_min,
         'fotogrammi_con_almeno_un_edificio': int(sum(1 for y in YEARS if (ys[keep] <= y).any())),
         'blocchi': len(CH), 'triangoli_edifici': ntri, 'triangoli_terra': len(land) // 9, 'fasi_terra': len(PH), 'triangoli_parchi': len(parks) // 9,
         'file_mb': round(mb, 1), 'secondi': round(time.time() - t0, 1), 'parametri': {'cell': A.cell, 'ybin': A.ybin, 'min_area': A.min_area, 'cull': not A.no_cull}}
os.makedirs(os.path.dirname(A.stats), exist_ok=True); json.dump(stats, open(A.stats, 'w'), indent=1)
log('scritto', A.out, f'{mb:.1f} MB'); print(json.dumps(stats))
