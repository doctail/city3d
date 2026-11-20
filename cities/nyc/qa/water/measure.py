"""measure.py [DATA_DIR] [out.json]: buildings 'in water' per year (centroid / footprint fraction not on land of that year).
Land(y) = land.json closed (land_close) minus all landphases + phases with from<=y<to (as build_render.py)."""
import json, sys, os, numpy as np, shapely
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
D = sys.argv[1] if len(sys.argv) > 1 else R + '/data_nyc'
YRS = [1609, 1650, 1700, 1750, 1800, 1850, 1900]
LC = json.load(open(R + '/city_nyc.json')).get('land_close', 45)
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(D + '/landphases.json'))
base = land.difference(unary_union([Polygon(p['r']).buffer(0) for p in PH]))
H = json.load(open(D + '/hist.json'))
cent = []; polys = []
for b in H:
    p = Polygon(b['r']).buffer(0); polys.append(p)
y0 = np.array([b['y'] for b in H]); d0 = np.array([b.get('d', 9999) for b in H])
cx = np.array([p.centroid.x for p in polys]); cy = np.array([p.centroid.y for p in polys])
res = {}; mask_by_year = {}
for y in YRS:
    l = unary_union([base] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
    alive = np.where((y0 <= y) & (d0 > y))[0]
    inl = shapely.contains_xy(l, cx[alive], cy[alive])
    wet = alive[~inl]
    # footprint: share of area on land
    fr = []
    for i in wet[:20000]:
        a = polys[i]; fr.append(a.intersection(l).area / max(a.area, 1e-6))
    fr = np.array(fr)
    # near-land (within 30 m of land) = shore sliver, vs open water
    far = [i for i in wet if polys[i].distance(l) > 30]
    res[y] = {'alive': int(len(alive)), 'centroid_in_water': int(len(wet)), 'water_>30m_from_land': len(far),
              'zones': {}}
    z = {}
    for i in wet: z[H[i].get('zone', '?')] = z.get(H[i].get('zone', '?'), 0) + 1
    res[y]['zones'] = dict(sorted(z.items(), key=lambda kv: -kv[1])[:6])
    kit = {}
    for i in wet: kit[str(H[i].get('kit', '?'))] = kit.get(str(H[i].get('kit', '?')), 0) + 1
    res[y]['kit'] = kit
    mask_by_year[y] = [int(i) for i in wet]
    print(y, {k: v for k, v in res[y].items()}, flush=True)
json.dump(res, open(sys.argv[2] if len(sys.argv) > 2 else R + '/cities/nyc/qa/water/measure_before.json', 'w'), indent=1)
json.dump(mask_by_year, open(os.environ.get("WET_OUT", "/tmp/claude-0/wet_idx.json"), "w"))
