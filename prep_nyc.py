# New York, dati edifici: da fetch_nyc.py --no-fill (buildings.json grezzo, y=0 = mancante) a DATA/buildings.json + misure.
# Uso: python prep_nyc.py RAW_DIR DATA_DIR
# Stesso metodo di prep_marseille.py / prep_parigi.py: de-arrotondamento (x10 +-5, x50<1850 e picchi x50 +-20) e anni mancanti =
# mediana dei 6 vicini piu prossimi con anno entro 150 m (+-2 a caso; poi vicino piu prossimo entro 400 m, poi mediana generale).
import json, os, sys, shutil, random, collections
import numpy as np
from scipy.spatial import cKDTree
RAW, DATA = sys.argv[1], sys.argv[2]
os.makedirs(DATA, exist_ok=True)
B = json.load(open(os.path.join(RAW, 'buildings.json')))
for f in ('land.json', 'boroughs.json', 'parks.json'):
    if os.path.exists(os.path.join(RAW, f)) and os.path.abspath(RAW) != os.path.abspath(DATA): shutil.copy(os.path.join(RAW, f), DATA)
def cen(r): a = np.array(r); return a[:, 0].mean(), a[:, 1].mean()
C = np.array([cen(b['r']) for b in B])
Y = np.array([b['y'] if 1000 <= b['y'] <= 2026 else 0 for b in B])
H = np.array([b['h'] for b in B])
M = {'edifici': len(B), 'con_anno': int((Y > 0).sum()), 'quota_anno': round(float((Y > 0).mean()), 4), 'anno0_o_mancante': int((Y == 0).sum()),
     'anno_grezzo_fuori_1000_2026_non_zero': int(sum(1 for b in B if b['y'] and not 1000 <= b['y'] <= 2026)),
     'con_altezza': int((H > 0).sum()), 'quota_altezza': round(float((H > 0).mean()), 4), 'altezza_max_m': round(float(H.max()), 1)}
kn = Y[Y > 0]; M['anno_min'] = int(kn.min()); M['anno_mediana'] = int(np.median(kn))
M['piu_vecchi'] = sorted(int(v) for v in kn)[:8]
cnt = collections.Counter(int(v) for v in kn)
M['anni_piu_frequenti'] = cnt.most_common(10)
M['multipli_di_10_quota'] = round(float(np.mean(kn % 10 == 0)), 4)
M['decenni'] = dict(sorted(collections.Counter(int(v) // 10 * 10 for v in kn).items()))
rnd = random.Random(3)
# NYC: i picchi non sono solo x50 (1899: 10.023, 1901: 6.992, 1910: 14.109, 1920, 1931 contro ~300-2.500 per anno vicino): estensione del
# metodo Marsiglia a QUALSIASI anno il cui conteggio supera 4x la mediana dei vicini (+-4): finestra +-20 se >20x, +-8 se >4x.
def ratio(v): nb = [cnt.get(v + d, 0) for d in (-4, -3, -2, -1, 1, 2, 3, 4)]; return cnt.get(v, 0) / max(1.0, float(np.median(nb)))
SP = {v: (20 if ratio(v) > 20 else 8) for v in cnt if ratio(v) > 4 and cnt[v] > 1000}
def spread(v):
    if v in SP: return max(1000, min(2026, v + rnd.randint(-SP[v], SP[v])))
    if v % 50 == 0 and v < 1850: return max(1000, min(2026, v + rnd.randint(-20, 20)))
    if v % 10 == 0: return min(2026, v + rnd.randint(-5, 4))
    return v
M['picchi_spalmati'] = {int(k): v for k, v in sorted(SP.items())}
M['gruppi_1895_1905_prima'] = {y: cnt.get(y, 0) for y in range(1895, 1906)}
Y2 = np.array([spread(int(v)) if v else 0 for v in Y])
cnt2 = collections.Counter(int(v) for v in Y2 if v)
M['gruppi_1895_1905_dopo'] = {y: cnt2.get(y, 0) for y in range(1895, 1906)}
M['anni_piu_frequenti_dopo'] = cnt2.most_common(8); M['max_rapporto_dopo_vs_vicini'] = round(max(cnt2[v] / max(1.0, float(np.median([cnt2.get(v + d, 0) for d in (-4, -3, -2, -1, 1, 2, 3, 4)]))) for v in cnt2 if cnt2[v] > 1000), 2)
M['multipli_di_10_quota_dopo'] = round(float(np.mean(Y2[Y2 > 0] % 10 == 0)), 4)
# anni mancanti
k = Y2 > 0; tree = cKDTree(C[k]); ky = Y2[k]; gm = int(np.median(ky)); how = collections.Counter(); est = []
for i in np.where(~k)[0]:
    d, ix = tree.query(C[i], k=6, distance_upper_bound=150); d = np.atleast_1d(d); ix = np.atleast_1d(ix)
    ok = ix[d < np.inf]
    if len(ok): Y2[i] = min(2026, int(round(float(np.median(ky[ok]))) + rnd.randint(-2, 2))); how['k6_150m'] += 1
    else:
        d1, i1 = tree.query(C[i], distance_upper_bound=400)
        if i1 < len(ky): Y2[i] = min(2026, int(ky[i1]) + rnd.randint(-2, 2)); how['nn_400m'] += 1
        else: Y2[i] = gm + rnd.randint(0, 4); how['default'] += 1
    est.append(int(i))
M['stimati'] = dict(how); M['y0_dopo_stima'] = int((Y2 <= 0).sum()); M['y_min_dopo'] = int(Y2.min())
# altezze mancanti: mediana dei 6 vicini con altezza (stesso criterio), il resto 9 m
hk = H > 0; ht = cKDTree(C[hk]); hv = H[hk]; H2 = H.copy(); hh = collections.Counter()
for i in np.where(~hk)[0]:
    d, ix = ht.query(C[i], k=6, distance_upper_bound=150); d = np.atleast_1d(d); ix = np.atleast_1d(ix); ok = ix[d < np.inf]
    if len(ok): H2[i] = round(float(np.median(hv[ok])), 1); hh['k6'] += 1
    else: H2[i] = 9.0; hh['default9m'] += 1
M['altezze_stimate'] = dict(hh)
out = [{'r': b['r'], 'h': float(H2[i]), 'y': int(Y2[i])} for i, b in enumerate(B)]
json.dump(out, open(os.path.join(DATA, 'buildings.json'), 'w'), separators=(',', ':'))
json.dump({'note': 'anni stimati dai 6 vicini (mediana, 150 m, +-2)', 'estimated_indices': est, 'sources': dict(how)}, open(os.path.join(DATA, 'buildings_y0_prov.json'), 'w'))
# quartieri (confini distretti da boroughs.json): copertura per borough
try:
    from shapely.geometry import Polygon, Point
    from shapely.strtree import STRtree
    bor = json.load(open(os.path.join(RAW, 'boroughs.json'))); polys = []; names = []
    for n, rs in bor.items():
        for r in rs: polys.append(Polygon(r)); names.append(n)
    tr = STRtree(polys); bc = collections.Counter(); bk = collections.Counter()
    for i, (x, y) in enumerate(C):
        hit = [names[j] for j in tr.query(Point(x, y), predicate='intersects')]
        n = hit[0] if hit else 'fuori_distretti_NYC'; bc[n] += 1; bk[n] += int(Y[i] > 0)
    M['per_distretto'] = {n: {'edifici': bc[n], 'con_anno': bk[n], 'quota': round(bk[n] / bc[n], 4)} for n in bc}
except Exception as e: M['per_distretto'] = f'errore {e}'
json.dump(M, open(os.path.join(DATA, 'misure_nyc.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(M, ensure_ascii=False)[:3500])
