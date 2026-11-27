# Toglie da DATA/buildings.json gli edifici con meno di MIN_FRAC (10%) dell'impronta su terra (pile di ponte, strutture sul fiume).
# Terra = land.json chiusa (land_close) piu' tutte le lastre di landphases (isole). Idempotente; salva buildings_prefiltro.json.gz la prima volta.
# Uso: python tools/filtra_edifici_acqua.py DATA_DIR city_X.json [--count anno1,anno2,...]   (--count: solo conteggio centroidi su acqua)
import json, sys, os, gzip, shutil
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import contains_xy
MIN_FRAC = 0.10
D, C = sys.argv[1], json.load(open(sys.argv[2])); LC = C.get('land_close', 45)
def P(r): return Polygon(r).buffer(0)
land0 = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(f'{D}/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(f'{D}/landphases.json')) if os.path.exists(f'{D}/landphases.json') else []
if '--count' in sys.argv:
    ys = [float(v) for v in sys.argv[sys.argv.index('--count') + 1].split(',')]
    B = json.load(open(f'{D}/buildings.json')) + json.load(open(f'{D}/hist.json'))
    base = land0
    for p in PH: base = base.difference(P(p['r']))
    C_ = np.array([np.mean(b['r'], 0) for b in B]); Y0 = np.array([b['y'] for b in B]); Y1 = np.array([b.get('d') if b.get('d') is not None else 9999 for b in B], float)
    for y in ys:
        l = unary_union([base] + [P(p['r']).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
        al = (Y0 <= y) & (Y1 > y)
        w = al & ~contains_xy(l, C_[:, 0], C_[:, 1])
        print(f'{int(y):5d} vivi {int(al.sum()):6d} centroidi su acqua {int(w.sum())}')
    sys.exit()
land = unary_union([land0] + [P(p['r']) for p in PH])
bk = f'{D}/buildings_prefiltro.json.gz'; fn = f'{D}/buildings.json'
if not os.path.exists(bk):
    with open(fn, 'rb') as f, gzip.open(bk, 'wb') as g: shutil.copyfileobj(f, g)
B = json.load(gzip.open(bk)); polys = [P(b['r']) for b in B]
keep = [b for b, p in zip(B, polys) if p.area > 0 and p.intersection(land).area / p.area >= MIN_FRAC]
json.dump(keep, open(fn, 'w'))
print(f'[filtra] edifici {len(B)} -> {len(keep)} (tolti {len(B) - len(keep)} con <{int(MIN_FRAC * 100)}% su terra)')
