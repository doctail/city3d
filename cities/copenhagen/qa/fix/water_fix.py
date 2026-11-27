"""water_fix.py [--write]: Copenhagen predecessor buildings (hist.json) that stand on water in their own year (hist.json footprints are modern shapes dated by zone).
Land(y) = land.json closed (land_close) minus all landphases + phases with from<=y<to (same as build_render.py).
Rule (no invention): a building whose footprint is < 50% on land at its start year is delayed to the first year the land exists under it
(infill / pond filling / pier phases); if the land never exists while it is alive, it is dropped (d = y, never visible; indices stay stable).
Idempotent: touched entries get 'yb_water'; original start in 'y_orig'. Run after piers.py (restore_after_build.sh does)."""
import json, sys, os, numpy as np, shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); D = os.environ.get('YB_DATA') or R + '/data_copenhagen'
FRAC = 0.5; YMAX = 2027.0
LC = json.load(open(R + '/city_copenhagen.json')).get('land_close', 45)
land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
PH = json.load(open(D + '/landphases.json'))
base = land.difference(unary_union([Polygon(p['r']).buffer(0) for p in PH]))
def land_at(y): return unary_union([base] + [Polygon(p['r']).buffer(0).buffer(1.5, join_style=2) for p in PH if p['from'] <= y < p['to']])
bounds = sorted({p[k] for p in PH for k in ('from', 'to') if 0 < p[k] < 9000})
H = json.load(open(D + '/hist.json'))
polys = np.array([Polygon(b['r']).buffer(0) for b in H], dtype=object)
y0 = np.array([b.get('y_orig', b['y']) if b.get('yb_water') else b['y'] for b in H], float); d0 = np.array([b.get('d', 99999) for b in H], float)
if any(b.get('yb_water') for b in H): print('note: already-processed entries are kept as they are')
done = np.array([bool(b.get('yb_water')) for b in H])
# state per building: first year with land under it (>= y0), or None
new_y = y0.copy(); dropped = np.zeros(len(H), bool)
pending = ~done & (y0 < 9000)
cuts = sorted(set([0.0] + bounds))   # land is constant on [cuts[i], cuts[i+1])
L = {}
for c in cuts: L[c] = land_at(c)
def frac_on(g, idx):
    inside = shapely.contains(g, polys[idx])
    out = np.ones(len(idx))
    for j in np.where(~inside)[0]:
        p = polys[idx[j]]; out[j] = p.intersection(g).area / max(p.area, 1e-6)
    return out
# interval index of a year
def ci(y): return max(i for i, c in enumerate(cuts) if c <= y)
todo = np.where(pending)[0]
# group by start interval
start_i = np.array([ci(y0[i]) for i in todo])
for i0 in sorted(set(start_i)):
    idx = todo[start_i == i0]
    ok = frac_on(L[cuts[i0]], idx) >= FRAC
    bad = idx[~ok]
    cand = bad
    for k in range(i0 + 1, len(cuts)):
        if not len(cand): break
        t = cuts[k]
        keep = d0[cand] > t   # still alive at t
        gone = cand[~keep]; dropped[gone] = True
        cand = cand[keep]
        if not len(cand): break
        good = frac_on(L[t], cand) >= FRAC
        new_y[cand[good]] = t; cand = cand[~good]
    dropped[cand] = True   # never land while alive
late = pending & (((new_y != y0) & (new_y > YMAX)) | (dropped & (d0 > YMAX)))   # land arrives (or never does) after the port era: keep frames past YMAX untouched
new_y[late] = np.maximum(y0[late], YMAX); dropped[late] = False   # such a building appears at YMAX (as the unfixed data would show it later)
chg = np.where((new_y != y0) | dropped)[0]
print('changed', len(chg), 'delayed', int(((new_y != y0) & ~dropped).sum()), 'dropped', int(dropped.sum()))
span = [(float(y0[i]), float(d0[i] if dropped[i] else new_y[i])) for i in chg]   # for dropped: the years it would have been visible
lo = min(a for a, b in span) if span else None; hi = max(b for a, b in span) if span else None
print('years touched: from', lo, 'to', hi)
by = {}
for i in chg:
    key = int(y0[i] // 10 * 10); by[key] = by.get(key, 0) + 1
print('by decade of original start', dict(sorted(by.items())))
json.dump({'changed': int(len(chg)), 'dropped': int(dropped.sum()), 'span': span}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'water', 'water_fix_report.json'), 'w'))
if '--write' in sys.argv:
    for i in chg:
        b = H[i]; b['y_orig'] = float(y0[i]); b['yb_water'] = 'dropped' if dropped[i] else 'delayed'
        if dropped[i]: b['d_orig'] = b.get('d'); b['y'] = 99998.0; b['d'] = 99999.0   # never visible but still in the list (build_render drops entries with d <= y, which would shift the per-building RNG of every other building)
        else: b['y'] = float(new_y[i])
    json.dump(H, open(D + '/hist.json', 'w'))
    print('written hist.json')
