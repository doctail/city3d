"""piers.py [--write]: find modern pier spikes (thin land) and slips (thin water notches) in land.json; write landphases entries
(spikes: visible only from 1850; slips filled with 'field' land until 1850). Idempotent: removes earlier 'yb_pier' entries first."""
import json, sys
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
D = '/home/user/doctail/city3d/data_nyc'
land = json.load(open(f'{D}/land.json'))
lg = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in land]).buffer(15, join_style=2).buffer(-15, join_style=2)
R_SPIKE, R_SLIP = 70, 60
reg = box(-9500, -12500, 5500, 2500)
opened = lg.buffer(-R_SPIKE, join_style=2).buffer(R_SPIKE, join_style=2)
spikes = lg.difference(opened).intersection(reg)
closed = lg.buffer(R_SLIP, join_style=2).buffer(-R_SLIP, join_style=2)
slips = closed.difference(lg).intersection(reg)
def parts(g, amin): return [p for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Polygon' and p.area > amin]
sp = parts(spikes, 400); sl = parts(slips, 400)
print('spikes', len(sp), round(sum(p.area for p in sp)), 'slips', len(sl), round(sum(p.area for p in sl)))
if '--write' in sys.argv:
    ph = [x for x in json.load(open(f'{D}/landphases.json')) if not x.get('yb_pier')]
    r = lambda p: [[round(x, 1), round(y, 1)] for x, y in list(p.simplify(1).exterior.coords)[:-1]]
    for p in sp: ph.append({'r': r(p), 'from': 1850, 'to': 99999, 'c': 'urban', 'yb_pier': 'spike'})
    for p in sl: ph.append({'r': r(p), 'from': 0, 'to': 1850, 'c': 'field', 'yb_pier': 'slip'})
    json.dump(ph, open(f'{D}/landphases.json', 'w'))
    print('written', len(ph))
else:
    from PIL import Image, ImageDraw
    s = 0.12; x0, y0, x1, y1 = -6500, -10500, 2500, -1500
    im = Image.new('RGB', (int((x1 - x0) * s), int((y1 - y0) * s)), (60, 120, 150)); d = ImageDraw.Draw(im)
    T = lambda p: [((x - x0) * s, (y1 - y) * s) for x, y in p.exterior.coords]
    for p in getattr(lg, 'geoms', [lg]): d.polygon(T(p), fill=(190, 190, 120))
    for p in sp: d.polygon(T(p), fill=(220, 40, 40))
    for p in sl: d.polygon(T(p), fill=(255, 255, 255))
    im.save('/tmp/piers.png')
