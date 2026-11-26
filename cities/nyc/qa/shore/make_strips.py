"""make_strips.py [--write]: replaces the two single-step shore infills of cities/nyc/story.json (history.water + history.zones)
with a gradual advance of the shoreline (N strips per shore). Idempotent: strips are rebuilt from the ORIGINAL hand-drawn rings kept below.
Shore line at step t = inner line A (Pearl St / Greenwich St) + t * (outer line B - A), both resampled by arc length, t modulated smoothly
along the shore (+-0.35 step) so the front is not a straight parallel line; t=0 is A and t=1 is B exactly, so the union of the strips is the old ring.
Years / modulation are [Guessing] (no source fetched)."""
import json, math, sys, os
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); SJ = R + '/cities/nyc/story.json'
EAST = dict(name='East-shore infill (Pearl Street to South Street)',
            A=[(40.702, -74.0128), (40.7078, -74.004), (40.7105, -74.0015), (40.7122, -74.0008)],            # Pearl Street line (inner)
            B=[(40.7005, -74.012), (40.7062, -74.0027), (40.7092, -74.0), (40.7115, -73.9992)],               # South Street line (final)
            years=[1690, 1705, 1720, 1735, 1750, 1765, 1780, 1800], extend=True,
            note='1609 shoreline ran along Pearl Street; owners were allowed to extend lots into the river from 1686 [Likely, NOT fetched]; the water lots (Water, Front, South Street) were filled bit by bit: step {k}/{n}, front interpolated between the Pearl Street line and the final line, years evenly spread 1690-1800 [Guessing, NOT fetched]')
WEST = dict(name='West-shore infill (Greenwich Street to West Street)',
            A=[(40.704, -74.016), (40.712, -74.014), (40.716, -74.0125)],                                      # Greenwich Street line (inner)
            B=[(40.704, -74.016), (40.7045, -74.018), (40.7085, -74.0178), (40.7125, -74.0168), (40.7165, -74.015)],   # West Street line (final)
            years=[1790, 1795, 1801, 1807, 1813, 1819, 1825, 1830],
            note='[Guessing] Hudson water lots filled bit by bit c. 1790-1830, NOT fetched: step {k}/{n}, front interpolated between the Greenwich Street line and the final line')
ERA = [[1609, 6.5, 10], [1800, 9, 14], [1850, 12, 19], [1890, 15, 24]]
M = 24   # samples along the shore

def resamp(pts, m):
    d = [0.0]
    for (a, b), (c, e) in zip(pts, pts[1:]): d.append(d[-1] + math.hypot((c - a) * 84300, (e - b) * 110540))   # lat/lon -> m, cos(40.7)*111320
    out = []
    for i in range(m):
        s = d[-1] * i / (m - 1); j = max(k for k in range(len(d) - 1) if d[k] <= s + 1e-9); f = (s - d[j]) / max(d[j + 1] - d[j], 1e-9)
        out.append((pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])))
    return out

def front(A, B, t, k, n, tag):
    ph = 1.7 * tag + 0.9 * k
    out = []
    for i, (a, b) in enumerate(zip(A, B)):
        u = i / (len(A) - 1)
        tt = t if k in (0, n) else t + 0.35 / n * (0.6 * math.sin(2 * math.pi * 1.5 * u + ph) + 0.4 * math.sin(2 * math.pi * 3.3 * u + 2 * ph))
        out.append((a[0] + tt * (b[0] - a[0]), a[1] + tt * (b[1] - a[1])))
    return out

KX, KY = 84300.0, 110540.0
def modern_land():
    """data_nyc land.json closed like build_render (land_close) minus the modern pier spikes (landphases yb_pier, from 1850), in lat/lon-meters about (40.7, -74.0)."""
    D = os.environ.get('NYC_DATA', R + '/data_nyc'); st = json.load(open(SJ))['city']
    from kit.geo import Proj; P = Proj(st['lat0'], st['lon0'])
    LC = json.load(open(R + '/city_nyc.json')).get('land_close', 45)
    land = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in json.load(open(D + '/land.json'))]).buffer(LC, join_style=2).buffer(-LC, join_style=2)
    ph = json.load(open(D + '/landphases.json')); sp = [Polygon(x['r']).buffer(0) for x in ph if x.get('yb_pier') == 'spike']
    if sp: land = land.difference(unary_union(sp))
    return P, land

def extend_B(A, B, u_max=0.7, maxd=90.0):
    """Moves each point of the outer line B outwards over the thin strip of modern land that lies just outside it (the old ring left a land strip outside a
    water 'moat' in 1609-1700). Only a strip thinner than maxd is taken; beyond u_max (big land of the NE end) B is kept."""
    P, land = modern_land(); out = []; ext = []
    for i, (a, b) in enumerate(zip(A, B)):
        ax, ay = P.L(*a); bx, by = P.L(*b); d = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / d, (by - ay) / d
        fl = [land.contains(Point(bx + ux * k * 2, by + uy * k * 2)) for k in range(int(maxd / 2) + 1)]
        e = 0.0
        if i / (len(A) - 1) <= u_max and any(fl):
            f = fl.index(True); g = f
            while g + 1 < len(fl) and fl[g + 1]: g += 1
            if g + 1 < len(fl): e = g * 2 + 1.0
        ext.append(e)
    ext = [sum(ext[max(0, i - 3):i + 4]) / len(ext[max(0, i - 3):i + 4]) for i in range(len(ext))]
    for (a, b), (e, ) in zip(zip(A, B), [(e,) for e in ext]):
        ax, ay = P.L(*a); bx, by = P.L(*b); d = math.hypot(bx - ax, by - ay)
        out.append(P.inv(bx + (bx - ax) / d * e, by + (by - ay) / d * e))
    return out, P, land

def strips(S, tag):
    n = len(S['years']); A = resamp(S['A'], M); B = resamp(S['B'], M); W = []; Z = []
    clip = None
    if S.get('extend'):
        B, P, land = extend_B(A, B); orig = Polygon([P.L(*p)[:2] for p in S['A'] + S['B'][::-1]]).buffer(0)
        clip = unary_union([orig, land])   # the strips may only claim modern land (or the old ring): no land invented in today's water
    for k in range(1, n + 1):
        lo = front(A, B, (k - 1) / n, k - 1, n, tag); hi = front(A, B, k / n, k, n, tag)
        pts = lo + hi[::-1]
        if clip is not None:
            g = Polygon([P.L(*p) for p in pts]).buffer(0).intersection(clip)
            g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area) if g.geom_type != 'Polygon' else g
            pts = [P.inv(x, y) for x, y in g.simplify(0.5).exterior.coords][:-1]
        ring = [list(map(lambda v: round(v, 6), p)) for p in pts]
        if not Polygon(ring).is_valid:
            q = Polygon(ring).buffer(0); q = max(getattr(q, 'geoms', [q]), key=lambda z: z.area); ring = [list(c) for c in q.exterior.coords][:-1]
        assert Polygon(ring).is_valid and Polygon(ring).area > 0, (S['name'], k)
        nm = f"{S['name']} step {k}/{n}"; y = float(S['years'][k - 1]); note = S['note'].format(k=k, n=n)
        W.append({'name': nm, 'ring': ring, 'from': y, 'to': 99999, 'c': 'urban', 'seal': True, 'src': [], 'conf': 'low', 'note': note})
        Z.append({'name': nm, 'ring': ring, 'born': [y + 1, y + 13], 'seed': None, 'era_height': ERA, 'src': [], 'conf': 'low',
                  'note': 'predecessors on filled land are born after the fill of their own step (+1..13 y); [Guessing]'})
    return W, Z

if __name__ == '__main__':
    sys.path.insert(0, R)
    st = json.load(open(SJ)); H = st['history']
    keep = lambda L: [x for x in L if not (x['name'].startswith(EAST['name']) or x['name'].startswith(WEST['name']))]
    wi = next(i for i, x in enumerate(H['water']) if x['name'].startswith(EAST['name'])); zi = next(i for i, x in enumerate(H['zones']) if x['name'].startswith(EAST['name']))
    W = []; Z = []
    for tag, S in enumerate((EAST, WEST)):
        w, z = strips(S, tag); W += w; Z += z
    H['water'] = keep(H['water'])[:0] + W + keep(H['water']); H['zones'] = Z + keep(H['zones'])
    print('water', len(H['water']), 'zones', len(H['zones']))
    if '--write' in sys.argv:
        json.dump(st, open(SJ, 'w'), indent=1, ensure_ascii=False); print('written story.json')
