# Marsiglia, dati edifici (locale, gratis): da raw BDNB (fetch_fr_raw.py clip, anche raggio largo) a DATA/buildings.json + misure.
# Uso: python prep_marseille.py RAW/bdnb.geojson.gz DATA_DIR [raggio_pack_m=9000]
# Formato come Lione: {r (anello locale m, aperto), h, y, i (id gruppo BDNB, ripetuto per le parti), k (INSEE), hs}.
# Anni mancanti: mediana dei 6 piu vicini con anno entro 150 m, +-2 anni a caso (poi vicino piu prossimo entro 400 m, poi mediana generale); y_est elencati in buildings_y0_prov.json.
import gzip, json, math, os, sys, collections
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import shape
SRC, DATA = sys.argv[1], sys.argv[2]; RP = float(sys.argv[3]) if len(sys.argv) > 3 else 9000.0
LAT0, LON0 = 43.2953, 5.3745; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
ARR = {str(c) for c in range(13201, 13217)}
F = json.load(gzip.open(SRC))['features']
rows = []   # (id, insee, y, h, lev, polys[list of rings], cx, cy)
for f in F:
    p = f['properties']; g = shape(f['geometry']); c = g.centroid
    cx, cy = (c.x - LON0) * KX, (c.y - LAT0) * KY
    ys = p['y'] if p['y'] and 1000 <= p['y'] <= 2026 else None
    rows.append((p['id'], str(p['insee']), ys, p['h'], p['lev'], list(g.geoms) if g.geom_type == 'MultiPolygon' else [g], cx, cy))
# ---- de-arrotondamento (stesso metodo di prep_parigi.py: gli anni tondi della BDNB sono segnaposto, nel video la citta' cresce a ondate) ----
# Parigi: multipli di 10 -> +-5 a caso; multipli di 50 prima del 1850 -> +-20. Marsiglia: il picco 1900 e' 14.192 gruppi su 30 km
# (9.627 entro 9 km) contro ~150 per anno vicino: con +-5 resterebbe un'onda di ~1.000 per anno. Quindi la finestra +-20 vale per i
# multipli di 50 prima del 1850 E per ogni multiplo di 50 il cui conteggio supera 20 volte la mediana degli anni vicini non tondi.
import random
rnd = random.Random(3)
_cnt = collections.Counter(r[2] for r in rows if r[2])
def _spike(v): 
    nb = [_cnt.get(v + d, 0) for d in (-4, -3, -2, -1, 1, 2, 3, 4)]
    return v % 50 == 0 and _cnt.get(v, 0) > 20 * max(1.0, float(np.median(nb)))
SPIKES = sorted(v for v in _cnt if _spike(v))
def spread(v):
    if v % 50 == 0 and (v < 1850 or v in SPIKES): return max(1000, min(2026, v + rnd.randint(-20, 20)))
    if v % 10 == 0: return min(2026, v + rnd.randint(-5, 4))
    return v
PRE9 = collections.Counter(r[2] for r in rows if r[2] and r[6] ** 2 + r[7] ** 2 <= RP ** 2)
PRE_ALL = collections.Counter(_cnt)
n_round = sum(1 for r in rows if r[2] and r[2] % 10 == 0)
rows = [(r[0], r[1], spread(r[2]) if r[2] else None) + r[3:] for r in rows]
print(f'[de-arrotondamento] multipli di 10: {n_round} gruppi ({n_round / max(1, sum(1 for r in rows if r[2])):.0%} dei noti); picchi +-20: {SPIKES}', flush=True)
def stats(sel, label):
    n = len(sel); a = sum(1 for r in sel if r[2]); 
    return {'zona': label, 'gruppi': n, 'con_anno': a, 'quota_anno': round(a / n, 4) if n else None, 'senza_anno': n - a, 'quota_senza': round(1 - a / n, 4) if n else None}
arr = [r for r in rows if r[1] in ARR]
M = {'comune_13201_13216': stats(arr, 'tutti i 16 arrondissement (BDNB, raggio 30 km dal Vieux-Port)'),
     'entro_1500m_VieuxPort': stats([r for r in rows if r[6] ** 2 + r[7] ** 2 <= 1500 ** 2], 'entro 1,5 km dal Vieux-Port (tutti i codici)'),
     'entro_9km': stats([r for r in rows if r[6] ** 2 + r[7] ** 2 <= RP ** 2], f'entro {RP/1000:.0f} km (pacchetto)'),
     'insee_nel_raggio30': dict(collections.Counter(r[1] for r in rows).most_common(40))}
per = {}
for k in sorted(ARR):
    s = [r for r in rows if r[1] == k]; per[k] = stats(s, k)
M['per_arrondissement'] = per
yy = [r[2] for r in arr if r[2]]
M['decenni_comune'] = dict(sorted(collections.Counter((y // 10) * 10 for y in yy).items()))
for L in (1800, 1900, 1943): M[f'con_anno_<{L}_comune'] = sum(1 for y in yy if y < L)
y9 = [r[2] for r in rows if r[2] and r[6] ** 2 + r[7] ** 2 <= RP ** 2]
for L in (1800, 1900, 1943): M[f'con_anno_<{L}_pack9km'] = sum(1 for y in y9 if y < L)
M['anni_piu_frequenti_comune'] = collections.Counter(yy).most_common(8)
# ---- pacchetto entro RP: stima anni ----
pk = [r for r in rows if r[6] ** 2 + r[7] ** 2 <= RP ** 2]
known = [r for r in rows if r[2]]            # i vicini si cercano su tutto il raster (anche oltre RP), solo con anno vero
kxy = np.array([(r[6], r[7]) for r in known]); ky = np.array([r[2] for r in known]); tree = cKDTree(kxy)
est = {}; how = collections.Counter(); genmed = int(np.median(ky) // 5 * 5)
for r in pk:
    if r[2]: continue
    d, ix = tree.query((r[6], r[7]), k=6, distance_upper_bound=150)
    ok = [i for dd, i in zip(np.atleast_1d(d), np.atleast_1d(ix)) if i < len(known)]
    if ok: y = min(2026, int(round(float(np.median(ky[ok]))) + rnd.randint(-2, 2))); how['k6_150m'] += 1   # niente arrotondamento al lustro: creava onde ogni 5 anni
    else:
        d1, i1 = tree.query((r[6], r[7]), distance_upper_bound=400)
        if i1 < len(known): y = min(2026, int(ky[i1]) + rnd.randint(-2, 2)); how['nn_400m'] += 1
        else: y = genmed + rnd.randint(0, 4); how['default'] += 1
    est[r[0]] = y
B = []; estidx = []
for r in pk:
    y = r[2] or est[r[0]]
    h, hs = (r[3], 'bdtopo') if r[3] else ((r[4] * 3.0, 'lev') if r[4] else (6.0, None))
    for g in r[5]:
        ring = [[round((x - LON0) * KX, 2), round((yv - LAT0) * KY, 2)] for x, yv in list(g.exterior.coords)[:-1]]
        if len(ring) < 3: continue
        if not r[2]: estidx.append(len(B))
        B.append({'r': ring, 'h': round(float(h), 1), 'y': int(y), 'i': r[0], 'k': r[1], 'hs': hs})
os.makedirs(DATA, exist_ok=True)
json.dump(B, open(os.path.join(DATA, 'buildings.json'), 'w'), separators=(',', ':'))
M['pack'] = {'parti_poligono': len(B), 'gruppi': len(pk), 'gruppi_stimati': len(est), 'come': dict(how), 'y0_dopo_stima': sum(1 for b in B if b['y'] <= 0), 'y_min': min(b['y'] for b in B), 'y_<1200': sum(1 for b in B if b['y'] < 1200)}
# dove sono stimati: per arrondissement e per cella 1 km
byk = collections.Counter(r[1] for r in pk if not r[2]); M['pack']['stimati_per_insee'] = dict(byk.most_common(20))
cells = collections.Counter((int(r[6] // 1000), int(r[7] // 1000)) for r in pk if not r[2]); M['pack']['celle_1km_top'] = [[list(k), v] for k, v in cells.most_common(8)]
M['de_arrotondamento'] = {'metodo': 'prep_parigi.spread: x10 +-5, x50<1850 +-20, picchi x50 (>20x vicini) +-20', 'picchi_x50': SPIKES, 'multipli_di_10_gruppi': n_round}
_post9 = collections.Counter(r[2] for r in pk if r[2])      # anni veri dopo de-arrotondamento (gruppi entro RP, senza stimati)
M['de_arrotondamento']['gruppi_per_anno_1895_1905_prima_9km'] = {y: PRE9.get(y, 0) for y in range(1895, 1906)}
M['de_arrotondamento']['gruppi_per_anno_1895_1905_dopo_9km'] = {y: _post9.get(y, 0) for y in range(1895, 1906)}
M['de_arrotondamento']['gruppi_per_anno_1895_1905_dopo_incl_stimati_9km'] = {y: sum(1 for r in pk if (r[2] or est[r[0]]) == y) for y in range(1895, 1906)}
json.dump({'note': 'anni stimati dai vicini (mediana dei 6 piu vicini entro 150 m, +-2 anni) per i gruppi BDNB senza annee_construction', 'estimated_indices': estidx, 'sources': dict(how)}, open(os.path.join(DATA, 'buildings_y0_prov.json'), 'w'))
json.dump(M, open(os.path.join(DATA, 'misure_bdnb.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: M[k] for k in ('comune_13201_13216', 'entro_1500m_VieuxPort', 'entro_9km', 'decenni_comune', 'pack')}, ensure_ascii=False)[:3500])
print({k: v for k, v in M.items() if k.startswith('con_anno')})
