"""Edifici vivi con il centroide sull'acqua, per anno (regola 20/11: 0, salvo moli storici). Stessa logica di tools/check_water.py:
terra(Y) = land.json chiusa (land_close) - tutte le lastre di landphases + le lastre visibili a Y. Edifici = buildings.json (y) + hist.json (y <= Y < d, y_orig/yb_water gia' a 99998).
Uso: python cities/copenhagen/qa/water_count.py DATA city_copenhagen.json 1185,1500,... [--list N]"""
import json, sys, numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
D, C = sys.argv[1], json.load(open(sys.argv[2])); YRS = [float(v) for v in sys.argv[3].split(',')]
LC = C.get('land_close', 45)
P = lambda r: (Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0)
land0 = unary_union([P(r) for r in json.load(open(f'{D}/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(f'{D}/landphases.json'))
base = land0
for p in PH: base = base.difference(Polygon(p['r']).buffer(0))
B = json.load(open(f'{D}/buildings.json')); H = json.load(open(f'{D}/hist.json'))
def cen(L): return np.array([np.mean(np.array(b['r'])[:, 0]) for b in L]), np.array([np.mean(np.array(b['r'])[:, 1]) for b in L])
bx, by = cen(B); hx, hy = cen(H)
by_ = np.array([b['y'] for b in B], float); hy_ = np.array([b['y'] for b in H], float); hd_ = np.array([b.get('d', 1e9) for b in H], float)
core = lambda x, y: (np.abs(x) < 9000) & (np.abs(y) < 9000)
print('anno  vivi  su_acqua  (nel core 18x18 km)')
tot = 0
for y in YRS:
    l = unary_union([base] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
    mb = (by_ <= y) & core(bx, by); mh = (hy_ <= y) & (y < hd_) & core(hx, hy)
    wb = mb & ~contains_xy(l, bx, by); wh = mh & ~contains_xy(l, hx, hy)
    n = int(wb.sum() + wh.sum()); tot += n
    print(f'{int(y):5d} {int(mb.sum() + mh.sum()):6d} {n:6d}  (reali {int(wb.sum())}, predecessori {int(wh.sum())})')
    if '--list' in sys.argv and n:
        i = np.where(wb)[0][:5]; j = np.where(wh)[0][:5]
        print('   es.', [(round(bx[k]), round(by[k])) for k in i], [(round(hx[k]), round(hy[k]), H[k].get('zone', '')[:20]) for k in j])
print('TOTALE', tot)
