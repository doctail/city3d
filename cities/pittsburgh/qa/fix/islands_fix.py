"""islands_fix.py [--write]: Pittsburgh land.json has no river islands (Herr's/Washington's Landing, Brunot, Neville): 150 real buildings
(buildings.json) and 108 'Strip District and Lawrenceville' predecessors stand in the river hole. Rule (no invention): each cluster of >= MIN
modern buildings whose centroid is outside the land gets an island = union of their footprints buffered 35 m and closed (60 m), i.e. the island
exists where real buildings stand on it (+-50 m shore, declared limit). The island is land in every year (these islands are natural).
Idempotent: entries marked 'yb_island' are replaced. Run on data_pittsburgh BEFORE `python -m kit pack pittsburgh` and before the hist build.
usage (repo root): python3 cities/pittsburgh/qa/fix/islands_fix.py --write"""
import json, os, sys, numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scipy.cluster.hierarchy import fcluster, linkage
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); D = R + '/data_pittsburgh'
MIN = 10; LC = json.load(open(R + '/city_pittsburgh.json')).get('land_close', 15)
L = [r for r in json.load(open(D + '/land.json')) if not (isinstance(r, dict) and r.get('yb_island'))]
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in L]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
B = [b for b in json.load(open(D + '/buildings.json')) if len(b.get('r', [])) >= 3]
P = [Polygon(b['r']).buffer(0) for b in B]
wet = [p for p in P if not land.contains(p.centroid)]
pts = np.array([[p.centroid.x, p.centroid.y] for p in wet]); cl = fcluster(linkage(pts, 'single'), 400, 'distance')
add = []
for c in sorted(set(cl)):
    g = [p for p, k in zip(wet, cl) if k == c]
    if len(g) < MIN: continue
    isl = unary_union([p.buffer(35) for p in g]).buffer(30, join_style=1).buffer(-30, join_style=1).simplify(2.0)
    for q in (isl.geoms if hasattr(isl, 'geoms') else [isl]):
        add.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]], 'yb_island': True})
    print('island: %d buildings, area %.0f m2, centre (%.0f, %.0f)' % (len(g), isl.area, isl.centroid.x, isl.centroid.y))
print('islands added', len(add))
if '--write' in sys.argv:
    json.dump(L + add, open(D + '/land.json', 'w')); print('written land.json')
