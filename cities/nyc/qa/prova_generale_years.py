"""prova_generale_years.py [out.json]: controllo automatico NYC su 1609-2026 (passo 1 anno fino al 1950, poi 5).
Terra(y) come build_render.py: land.json chiuso (land_close) meno tutte le landphases + fasi con from<=y<to (buffer 1,5 m).
 1. edifici in acqua (buildings.json + hist.json, baricentro fuori dalla terra dell'anno; 'lontani' = > 30 m dalla terra)
 2. variazione di area terra/acqua tra anni consecutivi (differenza simmetrica), in tutto il campo e sulle rive di Manhattan (Manhattan + 1500 m)
 3. componenti di terra staccate < 0,05 km2 (nell'area Manhattan + 8 km) non vicine (150 m) a una fase 'yb_pier'
"""
import json, sys, os, numpy as np, shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
D = os.environ.get('NYC_DATA', R + '/data_nyc'); OUT = sys.argv[1] if len(sys.argv) > 1 else R + '/cities/nyc/qa/prova_generale_years.json'
YEARS = list(range(1609, 1951)) + list(range(1955, 2027, 5)) + [2026]
YEARS = sorted(set(YEARS))
LC = json.load(open(R + '/city_nyc.json')).get('land_close', 45)
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(D + '/landphases.json'))
PHP = [Polygon(p['r']).buffer(0) for p in PH]
base = land.difference(unary_union(PHP))
PHB = [q.buffer(1.5, join_style=2) for q in PHP]
BOR = json.load(open(D + '/boroughs.json'))
MAN = unary_union([Polygon(r).buffer(0) for r in BOR['Manhattan']]).buffer(0)
ZONE = MAN.buffer(1500); WIN = MAN.buffer(8000)
PIERS = unary_union([PHP[i] for i, p in enumerate(PH) if p.get('yb_pier')]).buffer(150)
cache = {}
def active(y): return tuple(i for i, p in enumerate(PH) if p['from'] <= y < p['to'])
def land_at(y):
    k = active(y)
    if k not in cache: cache[k] = unary_union([base] + [PHB[i] for i in k])
    return k, cache[k]
# edifici
B = json.load(open(D + '/buildings.json')); H = json.load(open(D + '/hist.json'))
def arr(L):
    cx = np.array([sum(p[0] for p in b['r']) / len(b['r']) for b in L]); cy = np.array([sum(p[1] for p in b['r']) / len(b['r']) for b in L])
    return cx, cy, np.array([b['y'] for b in L], float), np.array([b.get('d', 99999) for b in L], float)
cx1, cy1, y1, d1 = arr(B); cx2, cy2, y2, d2 = arr(H)
cx = np.concatenate([cx1, cx2]); cy = np.concatenate([cy1, cy2]); y0 = np.concatenate([y1, y2]); d0 = np.concatenate([d1, d2])
src = np.concatenate([np.zeros(len(B), int), np.ones(len(H), int)])
res = {}; prev_k = None; prev_land = None; inl = np.zeros(len(cx), bool); prevY = 0
for Y in YEARS:
    k, L = land_at(Y); r = {}
    alive = (y0 <= Y) & (d0 > Y)
    if k != prev_k: ev = np.where(alive)[0]
    else: ev = np.where(alive & (y0 > prevY))[0]
    if len(ev): inl[ev] = shapely.contains_xy(L, cx[ev], cy[ev])
    wet = np.where(alive & ~inl)[0]
    far = [i for i in wet if shapely.distance(shapely.points(cx[i], cy[i]), L) > 30]
    r['alive'] = int(alive.sum()); r['centroid_in_water'] = int(len(wet)); r['water_gt30m'] = len(far)
    r['wet_hist'] = int(src[wet].sum()); r['wet_cur'] = int(len(wet) - src[wet].sum())
    # area
    r['land_km2_win'] = round(L.intersection(WIN).area / 1e6, 4); r['manhattan_zone_km2'] = round(L.intersection(ZONE).area / 1e6, 4)
    if prev_land is not None:
        if k != prev_k:
            sd = L.symmetric_difference(prev_land)
            r['d_all_m2'] = round(sd.area); r['d_zone_m2'] = round(sd.intersection(ZONE).area)
            r['started'] = [i for i in k if i not in prev_k]; r['ended'] = [i for i in prev_k if i not in k]
        else: r['d_all_m2'] = 0; r['d_zone_m2'] = 0
    # componenti piccole
    if k != prev_k:
        comps = [g for g in getattr(L, 'geoms', [L]) if g.geom_type == 'Polygon']
        small = [g for g in comps if g.area < 50000 and g.centroid.within(WIN) and not g.centroid.within(PIERS)]
        r['small'] = [[round(g.centroid.x), round(g.centroid.y), round(g.area)] for g in small]
        r['ncomp_win'] = sum(1 for g in comps if g.centroid.within(WIN))
    else: r['small'] = res[prevY]['small']; r['ncomp_win'] = res[prevY]['ncomp_win']
    res[Y] = r; prev_k = k; prev_land = L; prevY = Y
    print(Y, {a: b for a, b in r.items() if a not in ('small', 'started', 'ended')}, len(r['small']), r.get('started', ''), r.get('ended', ''), flush=True)
json.dump({'years': YEARS, 'res': {str(y): v for y, v in res.items()}, 'phases': [{k_: p[k_] for k_ in ('from', 'to', 'c')} | {'pier': bool(p.get('yb_pier')), 'area': round(PHP[i].area), 'cx': round(PHP[i].centroid.x), 'cy': round(PHP[i].centroid.y)} for i, p in enumerate(PH)]}, open(OUT, 'w'))
