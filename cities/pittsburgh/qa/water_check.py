"""water_check.py: Pittsburgh buildings (buildings.json + hist.json) whose centroid is outside the land polygon, per year.
Land = data_pittsburgh/land.json closed with land_close (same as build_render.py); history.water is empty, so the shore is the MODERN one (declared limit).
usage (repo root): python3 cities/pittsburgh/qa/water_check.py"""
import json, numpy as np, shapely, os
from shapely.geometry import Polygon
from shapely.ops import unary_union
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')); D = R + '/data_pittsburgh'
LC = json.load(open(R + '/city_pittsburgh.json')).get('land_close', 15)
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
rows = []
for f in ('buildings', 'hist'):
    for b in json.load(open(f'{D}/{f}.json')):
        if len(b.get('r', [])) < 3: continue
        rows.append((np.mean([p[0] for p in b['r']]), np.mean([p[1] for p in b['r']]), b['y'], b.get('d', 99999), f))
cx = np.array([r[0] for r in rows]); cy = np.array([r[1] for r in rows]); y0 = np.array([r[2] for r in rows]); d0 = np.array([r[3] for r in rows]); src = np.array([r[4] for r in rows])
wet = ~shapely.contains_xy(land, cx, cy)
print('year  alive  centroid_on_water (buildings.json / hist.json)')
for y in (1780, 1800, 1850, 1900, 1936, 1950, 2000, 2023):
    a = (y0 <= y) & (d0 > y)
    print(y, int(a.sum()), int((a & wet).sum()), '(%d / %d)' % (int((a & wet & (src == 'buildings')).sum()), int((a & wet & (src == 'hist')).sum())))
