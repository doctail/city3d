"""Traffico navale per Year Built (OPZIONALE, spento di default).

Puro Python (niente bpy): legge la sezione `traffic` (story.json o un file a parte), costruisce corsie su acqua,
una flotta di navi deterministica e ne calcola posizione/rotta/scala per (tempo del video, anno).
Usato da `kit/ships_bpy.py` (modelli e oggetti Blender) e da `python -m kit.traffic_kit <slug>` (controllo corsie sulla terra).

Tempo: la posizione di una nave dipende da t = fotogramma / FPS (secondi di VIDEO), NON dall'anno: la mappa anni->fotogrammi
(`year_at`) decide solo QUALI navi esistono (densita' per anno) e la loro scala (dissolvenza di apparizione).
Nessun dato di nave e' una "fonte storica": e' decorazione dichiarata (vedi `note` in traffic).
"""
import json, math, random, os, sys

MIN_LEN = 40.0   # m: sotto questa taglia una nave non si legge alla distanza del drone (obiettivo 32 mm, ~1.400 m)


def _xy(lat, lon, lat0, lon0):
    return ((lon - lon0) * math.cos(math.radians(lat0)) * 111320.0, (lat - lat0) * 110540.0)


def _interp(pts, v):
    if not pts: return 0.0
    if v <= pts[0][0]: return float(pts[0][1])
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a) if b > a else float(yb)
    return float(pts[-1][1])


class Lane:
    def __init__(self, name, d, lat0, lon0):
        self.name = name
        self.pts = [_xy(p[0], p[1], lat0, lon0) for p in d['line']]
        self.cum = [0.0]
        for p, q in zip(self.pts, self.pts[1:]): self.cum.append(self.cum[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        self.L = self.cum[-1]; self.width = float(d.get('width', 200)); self.y0 = d.get('from'); self.y1 = d.get('to')

    def at(self, s):
        """(x, y, direzione unitaria) alla distanza s lungo la corsia."""
        s = min(max(s, 0.0), self.L)
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.cum[m] <= s: lo = m
            else: hi = m
        p, q = self.pts[lo], self.pts[lo + 1]; seg = max(self.cum[lo + 1] - self.cum[lo], 1e-9); u = (s - self.cum[lo]) / seg
        return p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u, ((q[0] - p[0]) / seg, (q[1] - p[1]) / seg)


class Ship:
    __slots__ = ('cls', 'model', 'idx', 'lane', 'rev', 'off', 'len', 'v', 'phase', 'mode', 'special', 'dropped')


class Traffic:
    def __init__(self, cfg, lat0, lon0, land_at=None, seed=None, force=None, crowd=False):
        self.cfg = cfg; self.ts = float(cfg.get('time_scale', 1.0)); self.report = []
        self.lanes = {k: Lane(k, v, lat0, lon0) for k, v in cfg['lanes'].items()}
        rnd = random.Random(seed if seed is not None else cfg.get('seed', 7))
        self.ships = []; self.dens = {}
        for cname, c in cfg['classes'].items():
            dens = [list(p) for p in c['density']]; self.dens[cname] = dens
            pool = int(math.ceil(max(p[1] for p in dens))); pool = min(pool, int(c.get('max', pool)))
            lanes = [self.lanes[n] for n in c['lanes']]
            for i in range(pool):
                s = Ship(); s.cls = cname; s.model = c['model']; s.idx = i; s.lane = lanes[i % len(lanes)]
                s.rev = (i // len(lanes)) % 2 == 1; s.mode = c.get('mode', 'loop')
                s.len = max(MIN_LEN, rnd.uniform(*c['len'])); s.v = rnd.uniform(*c['speed']) * self.ts
                s.off = rnd.uniform(-0.5, 0.5) * s.lane.width * 0.7; s.phase = rnd.random(); s.special = None; s.dropped = False
                self.ships.append(s)
        for sp in cfg.get('specials', []):   # navi nominate: posizione scelta a un tempo di riferimento
            s = Ship(); s.cls = '_special'; s.model = sp['model']; s.idx = 0; s.lane = self.lanes[sp['lane']]; s.rev = bool(sp.get('rev', False))
            s.mode = 'loop'; s.len = max(MIN_LEN, float(sp['len'])); s.v = float(sp['speed']) * self.ts; s.off = float(sp.get('off', 0.0)); s.dropped = False
            x, y = _xy(sp['at'][0], sp['at'][1], lat0, lon0)
            best = min(range(0, int(s.lane.L), 10), key=lambda d: (s.lane.at(d)[0] - x) ** 2 + (s.lane.at(d)[1] - y) ** 2)
            u = best / s.lane.L
            s.phase = ((1 - u) if s.rev else u) - s.v * float(sp.get('t_ref', 0.0)) / s.lane.L
            s.special = (sp['y0'], sp['y1'], sp.get('name', 'special')); self.ships.append(s)
        self.keepouts = []   # [(t0, t1, x, y)] intorno ai monumenti nelle soste
        if land_at: self.check_land(land_at)
        if force is not None: self.force(force, crowd)

    # --- posizione ---
    def pos(self, s, t):
        u = s.phase + s.v * t / s.lane.L
        if s.mode == 'pingpong':
            u = u % 2.0; u = 2.0 - u if u > 1.0 else u; fwd = (s.phase + s.v * t / s.lane.L) % 2.0 <= 1.0
        else:
            u = u % 1.0; fwd = True
        if s.rev: u = 1.0 - u; fwd = not fwd
        x, y, (dx, dy) = s.lane.at(u * s.lane.L)
        if not fwd: dx, dy = -dx, -dy
        return x - dy * s.off, y + dx * s.off, math.atan2(dy, dx)

    def n_at(self, cname, y): return _interp(self.dens[cname], y)

    def fade(self, s, y):
        """0..1: la nave i-esima compare quando la densita' supera i (dissolvenza di scala sull'ultimo 1)."""
        if s.special: return 1.0 if s.special[0] <= y < s.special[1] else 0.0
        f = min(1.0, max(0.0, self.n_at(s.cls, y) - s.idx))
        if s.lane.y0 is not None and y < s.lane.y0: return 0.0
        if s.lane.y1 is not None and y >= s.lane.y1: return 0.0
        return f

    # --- controllo terra ---
    def check_land(self, land_at):
        """Per ogni nave: i punti del suo percorso (ogni ~40 m, +- mezza lunghezza) non entrano nella terra degli anni in cui esiste.
        Se l'offset laterale urta, si prova la linea centrale; se urta ancora, la nave e' scartata e finisce nel report."""
        from shapely.geometry import Point
        cache = {}
        def land(y):
            k = round(y / 5.0) * 5.0
            if k not in cache: cache[k] = land_at(k)
            return cache[k]
        for s in self.ships:
            if s.special: years = [(s.special[0] + s.special[1]) / 2.0]
            else: years = [p[0] for p in self.dens[s.cls] if p[1] > s.idx]
            if not years: continue
            def hits(off):
                for y in years:
                    g = land(y); n = max(8, int(s.lane.L / 40.0))
                    for k in range(n + 1):
                        x, yy, (dx, dy) = s.lane.at(k * s.lane.L / n)
                        if g.distance(Point(x - dy * off, yy + dx * off)) < max(s.len * 0.5, 40.0): return y
                return None
            bad = hits(s.off)
            if bad is not None and s.off != 0.0:
                bad = hits(0.0)
                if bad is None: s.off = 0.0
            if bad is not None:
                s.dropped = True; self.report.append(f'{s.cls}#{s.idx} corsia {s.lane.name}: tocca la terra del {bad:.0f}')
        self.ships = [s for s in self.ships if not s.dropped]

    def force(self, n, crowd=False):
        """Solo prove di costo: n navi su tutte le corsie, modelli a rotazione, sempre visibili.
        crowd=True: tutte vicino al Battery (hudson ultimo tratto, inizio di bay e east_river), lente: il caso peggiore con tutte in inquadratura."""
        models = sorted({s.model for s in self.ships}) or ['steam']; lanes = list(self.lanes.values()); rnd = random.Random(11); out = []
        if crowd: lanes = [self.lanes['hudson'], self.lanes['bay'], self.lanes['east_river']]; win = {'hudson': (0.6, 1.0), 'bay': (0.0, 0.1), 'east_river': (0.0, 0.3)}
        for i in range(n):
            s = Ship(); s.cls = '_force'; s.model = models[i % len(models)]; s.idx = i; s.lane = lanes[i % len(lanes)]; s.rev = (i // len(lanes)) % 2 == 1
            s.mode = 'loop'; s.len = rnd.uniform(45, 110); s.v = rnd.uniform(3, 9) * self.ts; s.off = rnd.uniform(-0.3, 0.3) * s.lane.width
            s.phase = rnd.random(); s.special = (-1e9, 1e9, 'force'); s.dropped = False
            if crowd: a_, b_ = win[s.lane.name]; s.phase = a_ + rnd.random() * (b_ - a_); s.v = rnd.uniform(0.3, 1.0); s.rev = False
            out.append(s)
        self.ships = out

    def keepout_scale(self, s, x, y, t):
        """Spegne (scala) le navi vicine al monumento durante la sosta e nel corridoio camera -> bersaglio."""
        k = 1.0
        for (t0, t1, tx, ty, cx, cy, r) in self.keepouts:
            if not (t0 - 1.5 <= t <= t1 + 1.5): continue
            d = math.hypot(x - tx, y - ty)
            vx, vy = tx - cx, ty - cy; L2 = vx * vx + vy * vy
            if L2 > 1:
                u = min(1.0, max(0.0, ((x - cx) * vx + (y - cy) * vy) / L2)); dc = math.hypot(x - (cx + u * vx), y - (cy + u * vy)); d = min(d, dc * 1.6)
            k = min(k, min(1.0, max(0.0, (d - r * 0.6) / (r * 0.8))))
        return k


def load_cfg(path):
    d = json.load(open(path)); return d.get('traffic', d)


def land_fn(data_dir):
    """land(y): terra del DATA (land.json meno le fasi, piu' le fasi attive nell'anno), come costruita da build_render.py."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    land = json.load(open(f'{data_dir}/land.json'))
    base = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in land if len(r) >= 1])
    ph = json.load(open(f'{data_dir}/landphases.json')) if os.path.exists(f'{data_dir}/landphases.json') else []
    polys = [(p['from'], p['to'], Polygon(p['r']).buffer(0)) for p in ph]
    cut = unary_union([q for _, _, q in polys]) if polys else None
    base = base.difference(cut) if cut is not None else base
    def at(y):
        act = [q for a, b, q in polys if a <= y < b]
        return unary_union([base] + act) if act else base
    return at


if __name__ == '__main__':   # python -m kit.traffic_kit <traffic.json> <data_dir> <lat0> <lon0>
    cfg = load_cfg(sys.argv[1]); T = Traffic(cfg, float(sys.argv[3]), float(sys.argv[4]), land_fn(sys.argv[2]))
    print(len(T.ships), 'navi;', len(T.report), 'scartate'); [print(' ', r) for r in T.report[:40]]
