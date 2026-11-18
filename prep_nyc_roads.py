# New York, strade con anno (locale, gratis): NYC Centerline (data_nyc_src/roads_centerline.json.gz) -> DATA/roads.json
# Stesso metodo di prep_marseille_osm.build_roads: quadrilatero per segmento, anno = 20o percentile degli anni degli edifici (DATA/buildings.json)
# entro 120 m (>=3), poi 300 m, poi il piu' vicino entro 700 m, +2; unione per anno (bin 2 anni) e triangolazione per tessere da 1,5 km.
# Uso: python prep_nyc_roads.py DATA_DIR   (DATA_DIR con buildings.json, land.json, roads_centerline.json.gz)
import json, math, os, sys, gzip, collections
import numpy as np, shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely.prepared import prep
from scipy.spatial import cKDTree
DATA = sys.argv[1]
def log(*a): print('[nyc_roads]', *a, flush=True)
lr = json.load(open(os.path.join(DATA, 'land.json')))
LAND = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in lr]); LP = prep(LAND)
B = json.load(open(os.path.join(DATA, 'buildings.json')))
bxy = np.array([[sum(p[0] for p in o['r']) / len(o['r']), sum(p[1] for p in o['r']) / len(o['r'])] for o in B]); by = np.array([o['y'] for o in B], float); bt = cKDTree(bxy)
def urban_year(x, y):
    for rad, mn in ((120, 3), (300, 3)):
        ii = bt.query_ball_point([x, y], rad)
        if len(ii) >= mn: return float(np.percentile(by[ii], 20))
    d, i = bt.query([x, y], distance_upper_bound=700)
    return float(by[i]) if i < len(by) else None
# rw_type NYC: 1 strada, 2 autostrada, 3 ponte (a parte: bridges.json), 4 tunnel, 6 sentiero, 7 scalinata, 9 rampa, 10 vicolo, 14 traghetto
raw = json.load(gzip.open(os.path.join(DATA, 'roads_centerline.json.gz'))); rd = []; stat = collections.Counter()
for r in raw:
    t = r['t']
    if t not in ('1', '2', '9'): stat['tipo_' + str(t) + '_saltato'] += 1; continue
    try: sw = float(r.get('w') or 0) * 0.3048
    except ValueError: sw = 0
    w = 20 if t == '2' else 9 if t == '9' else min(24, max(7, sw * 0.7)) if sw else 10
    if len(r['p']) < 2: continue
    g = LineString(r['p']); ys = []
    for fr in (0.2, 0.5, 0.8):
        p = g.interpolate(fr, normalized=True); v = urban_year(p.x, p.y)
        if v is not None: ys.append(v)
    if ys: y = int(np.median(ys)) + 2; stat['anno_da_edifici'] += 1
    elif t == '2': y = 1950; stat['autostrada_default_1950_Guessing'] += 1
    else: stat['senza_edifici_700m_saltato'] += 1; continue
    rd.append((g, w, min(2026, int(max(y, 1600)) // 2 * 2)))
log('segmenti', len(rd), dict(stat))
quads = collections.defaultdict(list)
for g, w, y in rd:
    cs = list(g.simplify(1.0).coords)
    for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
        dl = math.hypot(x1 - x0, y1 - y0)
        if dl < 1: continue
        ux, uy = (x1 - x0) / dl, (y1 - y0) / dl; e = w / 2; nx, ny = -uy * e, ux * e
        ax, ay = x0 - ux * e * 0.5, y0 - uy * e * 0.5; bx, bY = x1 + ux * e * 0.5, y1 + uy * e * 0.5
        if not LP.contains(Point((x0 + x1) / 2, (y0 + y1) / 2)): continue
        quads[y].append(Polygon([(ax + nx, ay + ny), (ax - nx, ay - ny), (bx - nx, bY - ny), (bx + nx, bY + ny)]))
TILE = 1500.0; keys = sorted(quads); U = {k: unary_union(quads[k]).simplify(0.3) for k in keys}
xs = [b[0] for b in bxy]; ys_ = [b[1] for b in bxy]; X0, Y0 = min(xs) - 500, min(ys_) - 500
nx_ = int(math.ceil((max(xs) + 500 - X0) / TILE)); ny_ = int(math.ceil((max(ys_) + 500 - Y0) / TILE)); roads = []
for ix in range(nx_):
    for iy in range(ny_):
        tb = box(X0 + ix * TILE, Y0 + iy * TILE, X0 + (ix + 1) * TILE, Y0 + (iy + 1) * TILE); done = Polygon()
        for k in keys:
            u = U[k]
            if not u.intersects(tb): continue
            u = u.intersection(tb)
            if done.area: u = u.difference(done)
            done = unary_union([done, u]) if not u.is_empty else done
            for q in (u.geoms if hasattr(u, 'geoms') else [u]):
                if not isinstance(q, Polygon) or q.area < 5: continue
                for tr in shapely.constrained_delaunay_triangles(q).geoms:
                    if tr.area > 0.05: roads.append({'r': [[round(x, 2), round(v, 2)] for x, v in list(tr.exterior.coords)[:-1]], 'y': int(k), 'rail': 0})
json.dump(roads, open(os.path.join(DATA, 'roads.json'), 'w'), separators=(',', ':'))
yy = [r['y'] for r in roads]
log(f'roads.json: {len(roads)} triangoli da {len(rd)} segmenti; anni {min(yy)}..{max(yy)}; mediana {int(np.median(yy))}')
