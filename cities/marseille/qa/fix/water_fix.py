"""Marseille water_fix.py (da cities/nyc/qa/fix/water_fix.py): costa storica a fasi (story history.water -> DATA/landphases.json).
Un edificio (hist.json predecessori E buildings.json attuali) con meno del 50% della pianta su terra nel suo anno di nascita viene ritardato
al primo anno in cui sotto di lui c'e' terra; se la terra non arriva finche' e' vivo, e' scartato (y=99998, d=99999: resta nella lista, gli indici
e i numeri casuali degli altri edifici non cambiano). Idempotente ('yb_water', 'y_orig'). Lanciato da restore_after_build.sh dopo ogni `kit build marseille`.
Uso: water_fix.py [--write]   (DATA = data_marseille)"""
import json, sys, os, numpy as np, shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); D = os.environ.get('YB_DATA') or R + '/data_marseille'   # YB_DATA: il gate (pod parity) lo punta a una cartella temporanea
FRAC = 0.5
LC = json.load(open(R + '/city_marseille.json')).get('land_close', 45)
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(D + '/landphases.json'))
base = land.difference(unary_union([Polygon(p['r']).buffer(0) for p in PH]))
def land_at(y): return unary_union([base] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
cuts = sorted({0.0} | {p[k] for p in PH for k in ('from', 'to') if 0 < p[k] < 9000} | {-9999.0})
cuts = sorted(set(cuts) | {-9999.0})
L = {c: land_at(c) for c in cuts}
def ci(y): return max(i for i, c in enumerate(cuts) if c <= y)
rep = {}
def run(name, B, has_d):
    polys = np.array([Polygon(b['r']).buffer(0) for b in B], dtype=object)
    y0 = np.array([b.get('y_orig', b['y']) if b.get('yb_water') else b['y'] for b in B], float)
    d0 = np.array([(b.get('d') if b.get('d') is not None else 99999) for b in B], float) if has_d else np.full(len(B), 99999.0)
    done = np.array([bool(b.get('yb_water')) for b in B]); pending = ~done & (y0 < 9000)
    new_y = y0.copy(); dropped = np.zeros(len(B), bool)
    def frac_on(g, idx):
        out = np.ones(len(idx)); ins = shapely.contains(g, polys[idx])
        for j in np.where(~ins)[0]:
            p = polys[idx[j]]; out[j] = p.intersection(g).area / max(p.area, 1e-6)
        return out
    todo = np.where(pending)[0]; si = np.array([ci(y0[i]) for i in todo])
    for i0 in sorted(set(si)):
        idx = todo[si == i0]; cand = idx[frac_on(L[cuts[i0]], idx) < FRAC]
        for k in range(i0 + 1, len(cuts)):
            if not len(cand): break
            t = cuts[k]; keep = d0[cand] > t; dropped[cand[~keep]] = True; cand = cand[keep]
            if not len(cand): break
            good = frac_on(L[t], cand) >= FRAC; new_y[cand[good]] = t; cand = cand[~good]
        dropped[cand[d0[cand] < 9000]] = True   # mai terra mentre vive: scartato solo se ha una fine; se arriva fino ad oggi e' gia' cosi' nei dati moderni (resta com'e')
    chg = np.where((new_y != y0) | dropped)[0]
    rep[name] = {'changed': int(len(chg)), 'delayed': int(((new_y != y0) & ~dropped).sum()), 'dropped': int(dropped.sum())}
    print(name, rep[name])
    if '--write' in sys.argv:
        for i in chg:
            b = B[i]; b['y_orig'] = float(y0[i]); b['yb_water'] = 'dropped' if dropped[i] else 'delayed'
            if dropped[i]: b['d_orig'] = b.get('d'); b['y'] = 99998.0; b['d'] = 99999.0
            else: b['y'] = float(new_y[i])
    return chg
H = json.load(open(D + '/hist.json')); B = json.load(open(D + '/buildings.json'))
run('hist', H, True); run('buildings', B, False)
if '--write' in sys.argv:
    json.dump(H, open(D + '/hist.json', 'w')); json.dump(B, open(D + '/buildings.json', 'w')); print('written hist.json, buildings.json')
json.dump(rep, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'water_fix_report.json'), 'w'))
