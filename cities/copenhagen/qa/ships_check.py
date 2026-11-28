"""Navi vs terra ed edifici per anno (Copenaghen). Uso: python cities/copenhagen/qa/ships_check.py DATA 1185,1650,... 
Per ogni anno: navi visibili (fade>0), distanza minima dei punti della corsia (offset incluso, ogni 40 m) da terra(anno) e dagli edifici vivi (buildings.json + hist.json y<=Y<d).
Il vincolo di build (check_land) e' len/2 (min 40 m) dalla terra; qui in piu' edifici: distanza dal poligono >= 15 m."""
import json, sys, os, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree
from kit import traffic_kit as T
D = sys.argv[1]; YRS = [float(v) for v in sys.argv[2].split(',')]
C = json.load(open('city_copenhagen.json')); cfg = T.load_cfg('cities/copenhagen/traffic.json')
land = T.land_fn(D); tr = T.Traffic(cfg, float(C['lat0']), float(C['lon0']), land)
B = json.load(open(f'{D}/buildings.json')); H = json.load(open(f'{D}/hist.json'))
print(len(tr.ships), 'navi dopo check_land;', len(tr.report), 'scartate')
for y in YRS:
    alive = [Polygon(b['r']).buffer(0) for b in B if b['y'] <= y] + [Polygon(b['r']).buffer(0) for b in H if b['y'] <= y < b.get('d', 1e9)]
    tree = STRtree(alive); g = land(y); vis = [s for s in tr.ships if tr.fade(s, y) > 0]
    worst_l = worst_b = 1e9; bad = []
    for s in vis:
        n = max(8, int(s.lane.L / 40.0)); ml = mb = 1e9
        for k in range(n + 1):
            x, yy, (dx, dy) = s.lane.at(k * s.lane.L / n); p = Point(x - dy * s.off, yy + dx * s.off)
            ml = min(ml, g.distance(p))
            idx = tree.query(p.buffer(300)); mb = min([mb] + [alive[i].distance(p) for i in idx])
        worst_l = min(worst_l, ml); worst_b = min(worst_b, mb)
        if ml < 1 or mb < 15: bad.append((s.cls, s.idx, s.lane.name, round(ml), round(mb)))
    print(f'{y:7.1f}  navi {len(vis):3d}  distanza min da terra {worst_l:6.0f} m  da edifici {worst_b:6.0f} m  violazioni {len(bad)} {bad[:4]}')
