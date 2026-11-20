"""measure_islands.py: land area (acres) of the harbor islands per year from data_nyc (land.json closed minus landphases + active phases, as build_render.py).
Governors 1700 must be ~69 acres (172 today - 103 fill, S60) and ONE compact polygon (0 holes); Ellis 1700 ~3 acres; Roosevelt ~148 acres at every year."""
import json, os, sys
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); D = R + '/data_nyc'
LC = 15
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(D + '/landphases.json'))
base = land.difference(unary_union([Polygon(p['r']).buffer(0) for p in PH]))
ISL = {'Governors': box(-3600, -8350, -2200, -7100), 'Ellis': box(-5000, -6850, -4400, -6300), 'Liberty': box(-5300, -7700, -4850, -7390), }
rv = [g for g in land.geoms if 1e5 < g.area < 1e6 and g.intersects(box(1900, -1950, 3900, 1700))]   # Roosevelt/Blackwell's: the 148-acre component of land.json
if rv: ISL['Roosevelt'] = rv[0].buffer(40)
out = {}
for y in (1650, 1700, 1850, 1900, 1911, 1913, 2020):
    l = unary_union([base] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
    row = {}
    for k, bx in ISL.items():
        g = l.intersection(bx); ps = [p for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Polygon' and p.area > 500]
        row[k] = {'acres': round(sum(p.area for p in ps) / 4047, 1), 'parts': len(ps), 'holes': sum(len(p.interiors) for p in ps)}
    out[y] = row; print(y, {k: (v['acres'], v['parts'], v['holes']) for k, v in row.items()})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measure_islands_%s.json' % (sys.argv[1] if len(sys.argv) > 1 else 'dopo')), 'w'), indent=1)
