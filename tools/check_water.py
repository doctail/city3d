# Controllo dell'acqua anno per anno, con la stessa logica di build_render.py:
# terra = land.json chiusa (land_close) meno le aree a fasi, piu' le lastre a fasi visibili in quell'anno; acqua = il resto.
# Per ogni anno conta i pezzi d'acqua > 5 ha nel riquadro e dice se il fiume principale (punto a nord e punto a sud) e' un pezzo unico.
# Uso: python tools/check_water.py DATA_DIR city_X.json anno1,anno2,... nordX,nordY sudX,sudY [png]
import json, sys
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
D, C = sys.argv[1], json.load(open(sys.argv[2])); YRS = [float(v) for v in sys.argv[3].split(',')]
N = Point(*map(float, sys.argv[4].split(','))); S = Point(*map(float, sys.argv[5].split(',')))
LC = C.get('land_close', 45)
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(f'{D}/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(f'{D}/landphases.json'))
for p in PH: land = land.difference(Polygon(p['r']).buffer(0))
BOX = box(min(N.x, S.x) - 6000, S.y - 500, max(N.x, S.x) + 6000, N.y + 500)
bad = 0; out = []
for y in YRS:
    l = unary_union([land] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
    w = BOX.difference(l)
    parts = [q for q in getattr(w, 'geoms', [w]) if q.area > 5e4]
    main = [q for q in parts if q.buffer(1).contains(N) or q.distance(N) < 1]
    ok = bool(main) and (main[0].distance(S) < 1)
    bad += not ok
    out.append((y, ok, len(parts)))
    print(f'{int(y):5d}  fiume nord-sud unico: {"SI" if ok else "NO <<<"}   pezzi d\'acqua > 5 ha: {len(parts)}')
    if len(sys.argv) > 6:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(4, 6), dpi=60); ax = fig.gca()
        for q in parts: ax.fill(*q.exterior.xy, color='#2a7fd0' if q in main else '#e04040')
        ax.plot(N.x, N.y, 'k^'); ax.plot(S.x, S.y, 'kv'); ax.set_aspect('equal'); ax.set_title(str(int(y))); ax.set_xticks([]); ax.set_yticks([])
        fig.savefig(f'{sys.argv[6]}_{int(y)}.png', bbox_inches='tight'); plt.close(fig)
print('PROBLEMI:', bad)
