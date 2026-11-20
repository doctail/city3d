import json, sys, os, numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from PIL import Image, ImageDraw
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); D = R + '/data_nyc'
y = float(sys.argv[1]); out = sys.argv[2]
LC = 45
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(D + '/landphases.json'))
base = land.difference(unary_union([Polygon(p['r']).buffer(0) for p in PH]))
l = unary_union([base] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
H = json.load(open(D + '/hist.json'))
wet = set(json.load(open('/tmp/claude-0/wet_idx.json'))[str(int(y))])
box = tuple(float(v) for v in os.environ.get('BOX', '-3500,-8500,1500,-3500').split(',')); sc = float(os.environ.get('SC', 0.25))
im = Image.new('RGB', (int((box[2]-box[0])*sc), int((box[3]-box[1])*sc)), (74, 144, 200)); d = ImageDraw.Draw(im)
T = lambda pts: [((x-box[0])*sc, (box[3]-yy)*sc) for x, yy in pts]
for g in getattr(l, 'geoms', [l]): d.polygon(T(g.exterior.coords), fill=(216, 208, 168))
for i, b in enumerate(H):
    if b['y'] <= y < b.get('d', 9999):
        r = b['r']
        if box[0] < r[0][0] < box[2] and box[1] < r[0][1] < box[3]: d.polygon(T(r), fill=(220, 30, 30) if i in wet else (70, 70, 70))
im.save(out)
