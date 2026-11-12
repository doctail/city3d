"""Strato storico generico del kit: da cities/<slug>/story.json + DATA (buildings.json pronto) genera
DATA/hist.json (predecessori), landphases.json (history.water), fires.json (history.fires), bridges.json
(history.bridges uniti a quelli esistenti), roads.json (strade dei gutting), landmarks_walls.json (mura come parti
'prism') e urban_kit.json (griglia 120 m per urban_year).

Per build_render espone urban_year(x, y) e WALL_P (pigri: niente lavoro pesante e niente sys.argv all'import).
Story: variabile d'ambiente CITY3D_STORY, altrimenti dal city json passato con --city (chiave 'story' o 'name').

Uso:  python -m kit.hist_kit build <slug|story.json> [DATA]
      python -m kit.hist_kit make-stub <slug>
      python hist_<slug>.py DATA          (stub generato: chiama main())
"""
import collections, json, math, os, random, sys

from shapely.geometry import LineString, Point, Polygon, box
from shapely.prepared import prep
from shapely import affinity
from shapely.ops import unary_union
from shapely.strtree import STRtree

from .geo import ROOT, Proj, data_dir, load_story

CELL = 120.0          # griglia di urban_year fuori dalle zone (stessa cella di CELLMIN in build_render)
FCELL = 60.0          # griglia fine del primo edificio/predecessore vivo (regola: suolo urbano solo con le case)
LANE_W = 12.0         # nastri stradali piu' stretti di cosi' nelle zone = vicoli antichi: compaiono con la zona
COUNTRY = 9999.0      # campagna: mai citta'
STAT_YEARS = (1500, 1800, 1900)


# ---------------------------------------------------------------- utilita'

def _poly(ring):
    p = Polygon(ring)
    return p if p.is_valid else p.buffer(0)


def _ring_out(g, nd=2):
    """Anello [[x,y],…] aperto (formato DATA) da un Polygon shapely."""
    return [[round(x, nd), round(y, nd)] for x, y in list(g.exterior.coords)[:-1]]


def _polys(g):
    return [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and not q.is_empty]


def _height(spec, year, rnd, default=(6.0, 10.0)):
    """era_height: [lo, hi] oppure [[anno, lo, hi], …] (vale l'ultima riga con anno <= year)."""
    spec = spec or default
    if isinstance(spec[0], (list, tuple)):
        row = spec[0]
        for r in spec:
            if r[0] <= year: row = r
        lo, hi = row[1], row[2]
    else:
        lo, hi = spec[0], spec[1]
    return round(rnd.uniform(lo, hi), 1)


def split(poly, w=7.6, d=22.4):
    """Lottizzazione delle impronte grandi (come hist_nyc.split, che pero' legge sys.argv all'import)."""
    if poly.area < 450: return [poly]
    c = list(poly.minimum_rotated_rectangle.exterior.coords)
    ang = math.degrees(math.atan2(c[1][1] - c[0][1], c[1][0] - c[0][0]))
    p0 = affinity.rotate(poly, -ang, origin=poly.centroid); x0, y0, x1, y1 = p0.bounds; out = []
    yy = y0
    while yy < y1:
        xx = x0
        while xx < x1:
            q = p0.intersection(box(xx + 0.3, yy + 0.3, xx + w - 0.3, yy + d - 0.3))
            out += [affinity.rotate(g, ang, origin=poly.centroid) for g in _polys(q) if g.area > 20]
            xx += w
        yy += d
    return out or [poly]


# ---------------------------------------------------------------- contesto (story in metri locali)

class Ctx:
    def __init__(self, story):
        self.story = story; self.P = Proj.of(story)
        c = story['city']; H = story.get('history', {}) or {}
        self.start = float(c.get('start_year', 0)); self.H = H
        self.zones = []
        for i, z in enumerate(H.get('zones', []) or []):
            poly = _poly(self.P.ring(z['ring']))
            b0, b1 = (z.get('born') or [self.start, self.start])[:2]
            seed = self.P.L(*z['seed']) if z.get('seed') else None
            dmax = max(math.hypot(x - seed[0], y - seed[1]) for x, y in poly.exterior.coords) if seed else 1.0
            self.zones.append(dict(name=z.get('name', f'zone{i}'), poly=poly, pp=prep(poly), b0=float(b0), b1=float(b1),
                                   seed=seed, dmax=max(dmax, 1.0), eh=z.get('era_height')))
        self.zones.sort(key=lambda z: z['b0'])      # la piu' antica per prima: vale lei
        # WALL_P = la cinta 'ring' piu' antica (built[0] minimo), non la prima elencata
        rings = sorted((w for w in H.get('walls', []) or [] if w.get('ring')), key=lambda w: (w.get('built') or [9999])[0])
        self.wall_p = _poly(self.P.ring(rings[0]['ring'])) if rings else None
        self._grid = None     # 10o percentile per cella di 120 m
        self._first = None    # primo anno di nascita per cella di 60 m

    def first_near(self, x, y):
        """Primo anno in cui c'e' un edificio (attuale o predecessore) entro ~60 m (celle 3x3 da 60 m); None se nessuno."""
        ix, iy = int(x // FCELL), int(y // FCELL)
        v = [self._first[k] for k in ((ix + a, iy + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) if k in self._first]
        return min(v) if v else None

    def urban(self, x, y):
        """Anno in cui il punto diventa citta': nella zona piu' antica = rampa nel punto, mai prima della prima casa
        entro ~60 m (nessuna casa vicina = campagna); fuori dalle zone = 10o percentile della cella di 120 m."""
        z = self.zone_at(x, y)
        if z:
            f = self.first_near(x, y)
            return COUNTRY if f is None else max(self.ramp(z, x, y), f)
        return float(self._grid.get((int(x // CELL), int(y // CELL)), COUNTRY))

    def zone_at(self, x, y):
        p = Point(x, y)
        for z in self.zones:
            if z['pp'].contains(p): return z
        return None

    @staticmethod
    def ramp(z, x, y):
        """Anno di nascita deterministico nella zona: rampa dal seed verso il bordo, b0 se uniforme."""
        if z['seed'] is None: return z['b0']
        f = min(1.0, math.hypot(x - z['seed'][0], y - z['seed'][1]) / z['dmax'])
        return z['b0'] + (z['b1'] - z['b0']) * f


_CTX = {}


def _story_file():
    p = os.environ.get('CITY3D_STORY')
    if p:
        p = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if os.path.exists(p): return p
    av = sys.argv
    if '--city' in av and av.index('--city') + 1 < len(av):        # dentro Blender: city json di build_render
        cj = av[av.index('--city') + 1]
        try:
            C = json.load(open(cj if os.path.isabs(cj) else os.path.join(ROOT, cj)))
        except Exception:
            return None
        if C.get('story'): return C['story'] if os.path.isabs(C['story']) else os.path.join(ROOT, C['story'])
        for k in (C.get('name'), (C.get('hist') or '').replace('hist_', '')):
            if k and os.path.exists(os.path.join(ROOT, 'cities', k, 'story.json')): return os.path.join(ROOT, 'cities', k, 'story.json')
    return None


def _ctx():
    f = _story_file()
    if not f or not os.path.exists(f): return None
    if f not in _CTX: _CTX[f] = Ctx(load_story(f))
    return _CTX[f]


def reset():
    _CTX.clear()


def _data_for(ctx):
    """Cartella DATA per la griglia: CITY3D_DATA, CITY_DATA, primo argomento dopo '--' (Blender), data_dir della story."""
    cand = [os.environ.get('CITY3D_DATA'), os.environ.get('CITY_DATA')]
    if '--' in sys.argv and sys.argv.index('--') + 1 < len(sys.argv): cand.append(sys.argv[sys.argv.index('--') + 1])
    cand.append(data_dir(ctx.story))
    for d in cand:
        if d and os.path.exists(os.path.join(d, 'urban_kit.json')): return d
    return None


# ---------------------------------------------------------------- API per build_render

def urban_year(x, y):
    """Anno in cui il punto diventa citta': zona piu' antica che lo contiene, altrimenti primo edificio della cella
    di 120 m (10o percentile, da urban_kit.json), altrimenti 9999 (campagna)."""
    c = _ctx()
    if c is None: return COUNTRY
    if c._grid is None:
        d = _data_for(c); c._grid, c._first = {}, {}
        if d:
            with open(os.path.join(d, 'urban_kit.json')) as f: g = json.load(f)
            c._grid = {tuple(map(int, k.split(','))): v for k, v in g['p'].items()}
            c._first = {tuple(map(int, k.split(','))): v for k, v in g.get('first', {}).items()}
    return c.urban(x, y)


def __getattr__(name):
    if name == 'WALL_P':          # prima cinta 'ring' delle walls, in metri locali (None se non c'e')
        c = _ctx()
        return c.wall_p if c else None
    raise AttributeError(name)


# ---------------------------------------------------------------- generatori

def _births(ctx, z, x, y, rnd):
    """Nascita di un predecessore nella zona: rampa (o uniforme) + rumore; se prima dell'inizio, gia' in piedi."""
    u = ctx.ramp(z, x, y) + rnd.uniform(-4, 8) if z['seed'] else rnd.uniform(z['b0'], z['b1'])
    u = min(max(u, z['b0']), max(z['b1'], z['b0']))
    if u <= ctx.start: u = min(u, ctx.start - rnd.uniform(1, 6))
    return u


def zones_pass(ctx, blds, rnd):
    out = []
    for b in blds:
        try: p = _poly(b['r'])
        except Exception: continue
        if p.is_empty or p.area < 15: continue
        c = p.centroid; z = ctx.zone_at(c.x, c.y)
        if not z: continue
        u = _births(ctx, z, c.x, c.y, rnd)
        if b['y'] <= u + 25: continue          # l'edificio di oggi e' tra i primi del lotto
        for q in (g for part in _polys(p) for g in split(part)):
            born = u + rnd.uniform(0, 3) if u > ctx.start else u
            died = b['y'] - rnd.uniform(0.3, 1.5)
            if died - born < 8: continue
            out.append({'r': _ring_out(q), 'h': _height(z['eh'], born, rnd), 'y': round(born, 2), 'd': round(died, 2),
                        'zone': z['name'], 'kit': 'zone'})
    return out


def _lots(void, ang, origin, rnd):
    """Isolati a doppia fila di lotti 8-15 m con vicoli (3-3,5 m) nel vuoto, orientati come l'area."""
    v = affinity.rotate(void, -ang, origin=origin); x0, y0, x1, y1 = v.bounds; out = []
    yy = y0
    while yy < y1:
        dep = rnd.uniform(9, 13)                           # profondita' di una fila; due file schiena contro schiena
        for row in (0, 1):
            ya = yy + row * dep; xx = x0; n = 0; cut = rnd.randint(5, 8)
            while xx < x1:
                w = rnd.uniform(8, 15)
                q = v.intersection(box(xx + 0.25, ya + 0.25, xx + w - 0.25, ya + dep - 0.25))
                out += [affinity.rotate(g, ang, origin=origin) for g in _polys(q) if g.area > 25]
                xx += w; n += 1
                if n % cut == 0: xx += 3.0                 # vicolo trasversale
        yy += 2 * dep + 3.5                                # vicolo longitudinale
    return out


def gutting_pass(ctx, blds, tree, rnd):
    out = []; filled = {}
    for g in ctx.H.get('gutting', []) or []:
        G = _poly(ctx.P.ring(g['ring'])); f0, until = float(g['from']), float(g['until'])
        near = [blds[i] for i in tree.query(G)]
        occ = unary_union([_poly(b['r']).buffer(1.0) for b in near]) if near else Polygon()
        void = G.difference(occ).buffer(-1.0).buffer(0.5)
        c = list(G.minimum_rotated_rectangle.exterior.coords)
        e = max(((c[i], c[i + 1]) for i in range(2)), key=lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
        ang = math.degrees(math.atan2(e[1][1] - e[0][1], e[1][0] - e[0][0]))
        n = 0
        for q in _lots(void, ang, G.centroid, rnd) if not void.is_empty else []:
            cc = q.centroid; z = ctx.zone_at(cc.x, cc.y)
            f1 = max(f0, ctx.ramp(z, cc.x, cc.y)) if z else f0      # mai prima della zona che le contiene
            born = f1 + rnd.uniform(0, 10) if f1 > ctx.start else min(f1, ctx.start - rnd.uniform(1, 6))
            died = until - rnd.uniform(0.2, 1.5)
            if died - born < 8: continue
            out.append({'r': _ring_out(q), 'h': _height(z['eh'] if z else None, born, rnd), 'y': round(born, 2), 'd': round(died, 2),
                        'zone': g.get('name', 'gutting'), 'kit': 'gut'})
            n += 1
        filled[g.get('name', 'gutting')] = n
    return out, filled


def clear_pass(ctx, D, hist, rnd):
    """Impronte dei monumenti con clear a tempo {"r", "y"} (landmarks.json, kit/landmarks_kit.py): prima del monumento
    il sito e' tessuto della zona. Toglie i predecessori di zona con centroide dentro e riempie l'impronta di lotti nati
    con la zona e morti a y (build_render toglie comunque tutto cio' che e' dentro da y)."""
    f = os.path.join(D, 'landmarks.json')
    if not os.path.exists(f): return hist, 0
    with open(f) as fh: L = json.load(fh)
    T = [c for c in (L.get('clear') or []) if isinstance(c, dict)] if isinstance(L, dict) else []
    n = 0
    for c in T:
        R = _poly(c['r']); RP = prep(R); yc = float(c['y']); cc = R.centroid; z = ctx.zone_at(cc.x, cc.y)
        if not z or z['b0'] >= yc - 8: continue
        hist = [h for h in hist if not (h.get('kit') == 'zone' and RP.contains(_poly(h['r']).centroid))]
        (x0, y0), (x1, y1) = list(R.minimum_rotated_rectangle.exterior.coords)[:2]; ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        for q in _lots(R.buffer(-0.5), ang, cc, rnd):
            born = _births(ctx, z, q.centroid.x, q.centroid.y, rnd); died = yc - rnd.uniform(0.1, 0.5)
            if died - born < 8: continue
            hist.append({'r': _ring_out(q), 'h': _height(z['eh'], born, rnd), 'y': round(born, 2), 'd': round(died, 2),
                         'zone': z['name'], 'kit': 'clear'}); n += 1
    return hist, n


def lost_pass(ctx):
    out = []
    for l in ctx.H.get('lost', []) or []:
        q = _poly(ctx.P.ring(l['ring']))
        for g in _polys(q):
            out.append({'r': _ring_out(g), 'h': float(l.get('h', 12)), 'y': float(l['from']), 'd': float(l['to']),
                        'name': l.get('name', 'lost'), 'kit': 'lost'})
    return out


def fires_pass(ctx, blds, hist, rnd):
    """Incendi distruttivi: chi e' nato prima di y nel ring muore nella finestra [y, y1] (a ondata dall'origine se c'e')
    e rinasce dopo y1 + rebuild_years. Edifici attuali: copia in hist fino al fuoco, anno attuale spostato (y_kit0 = originale)."""
    burned = {}
    for f in sorted(ctx.H.get('fires', []) or [], key=lambda f: f['y']):
        if not f.get('destroy'): continue
        F = _poly(ctx.P.ring(f['ring'])); FP = prep(F); y, y1 = float(f['y']), float(f.get('y1', f['y']))
        reb = y1 + float(f.get('rebuild_years', 3))
        org = ctx.P.L(*f['origin']) if f.get('origin') else None
        dmax = max(math.hypot(x - org[0], yy - org[1]) for x, yy in F.exterior.coords) if org else 1.0

        def death(cx, cy):
            fr = min(1.0, math.hypot(cx - org[0], cy - org[1]) / dmax) if org else rnd.random()
            return round(y + (y1 - y) * fr, 4)
        n = 0
        for h in list(hist):
            if not (h['y'] < y < h.get('d', 99999)): continue
            c = _poly(h['r']).centroid
            if not FP.contains(c): continue
            d0 = h.get('d', 99999); h['d'] = death(c.x, c.y); n += 1
            r0 = reb + rnd.uniform(0, 4)
            if d0 - r0 >= 5:
                hist.append(dict(h, y=round(r0, 2), d=d0, h=_height(None, r0, rnd, (h['h'] * 0.9, h['h'] * 1.15)), kit='fire'))
        for b in blds:
            if b.get('lm') or not b['y'] < y: continue
            try: c = _poly(b['r']).centroid
            except Exception: continue
            if not FP.contains(c): continue
            hist.append({'r': b['r'], 'h': b['h'], 'y': b['y'], 'd': death(c.x, c.y), 'kit': 'fire'})
            b.setdefault('y_kit0', b['y']); b['y'] = round(reb + rnd.uniform(0, 4), 2); n += 1
        burned[f.get('name', 'fire')] = n
    return burned


def walls_parts(ctx, rnd):
    """Mura come parti 'prism' (cortina + torri) per landmarks.json; costruzione progressiva lungo il tracciato,
    demolizione a tratti di 2-4 segmenti (anno a caso nell'intervallo), tratti 'keep' senza 'd'."""
    parts = []
    for w in ctx.H.get('walls', []) or []:
        pts = ctx.P.ring(w.get('ring') or w['line'])
        if w.get('ring') and pts[0] != pts[-1]: pts = pts + [pts[0]]
        b0, b1 = (w.get('built') or [ctx.start, ctx.start])[:2]
        dem = w.get('demolished'); dem = None if dem is None else (dem if isinstance(dem, (list, tuple)) else [dem, dem + 2])
        keep = [(*ctx.P.L(k[0], k[1]), k[2]) for k in w.get('keep', []) or []]
        H, W, ev = float(w.get('height', 10)), float(w.get('width', 4)), float(w.get('towers_every_m') or 0)
        col, tcol = w.get('color', '#c3a77c'), w.get('tower_color', '#b99d72')
        step = ev if ev > 0 else 60.0
        tot = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])) or 1.0
        s = 0.0; left = 0; yd = None; name = w.get('name', 'City walls')
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 0.5: continue
            n = max(1, round(L / step)); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            for k in range(n):
                pa = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                pb = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
                yb = round(b0 + (b1 - b0) * (s + L * (k + 0.5) / n) / tot, 2)
                if dem and left <= 0: left = rnd.randint(2, 4); yd = round(rnd.uniform(*dem), 2)
                left -= 1
                kept = any(math.hypot(mx - kx, my - ky) <= kr for kx, ky, kr in keep)
                extra = {'d': yd} if (dem and not kept) else {}
                seg = LineString([pa, pb]).buffer(W / 2, cap_style=2)
                parts.append(dict(name=name, t='prism', r=_ring_out(seg), z0=0.0, z1=H, c=col, top=col, a=0.05, y=yb,
                                  cx=round(mx, 2), cy=round(my, 2), wall=1, **extra))
                if ev > 0:
                    hs = max(W, 3.5); vx, vy = -uy, ux
                    sq = [[round(pa[0] + sx * hs * ux + sy * hs * vx, 2), round(pa[1] + sx * hs * uy + sy * hs * vy, 2)]
                          for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                    kt = any(math.hypot(pa[0] - kx, pa[1] - ky) <= kr for kx, ky, kr in keep)
                    parts.append(dict(name=name, t='prism', r=sq, z0=0.0, z1=H + 4, c=tcol, top=tcol, a=0.05, y=yb,
                                      cx=round(pa[0], 2), cy=round(pa[1], 2), wall=1, tower=1, **({'d': yd} if (dem and not kt) else {})))
            s += L
    return parts


def _backup(D, name):
    """Copia originale <name>_orig.json la prima volta; restituisce i dati originali (idempotenza)."""
    f, o = os.path.join(D, name + '.json'), os.path.join(D, name + '_orig.json')
    if not os.path.exists(o):
        if not os.path.exists(f): return []
        with open(f) as a, open(o, 'w') as b: b.write(a.read())
    return json.load(open(o))


def roads_pass(ctx, D):
    """Strade: nei gutting compaiono a 'until'; nelle zone i vicoli (larghezza < LANE_W) compaiono con la zona
    (max(rampa, prima casa vicina)) se l'anno attuale e' piu' tardo. I viali larghi non vengono anticipati."""
    G = [(prep(_poly(ctx.P.ring(g['ring']))), _poly(ctx.P.ring(g['ring'])), float(g['until'])) for g in ctx.H.get('gutting', []) or []]
    if not (G or ctx.zones) or not (os.path.exists(os.path.join(D, 'roads.json')) or os.path.exists(os.path.join(D, 'roads_orig.json'))):
        return (0, 0)
    roads = _backup(D, 'roads'); n = m = 0
    for r in roads:
        try: q = _poly(r['r'])
        except Exception: continue
        if q.is_empty: continue
        c = q.centroid; gut = False
        for gp, gpoly, until in G:
            if gp.contains(c) or (q.area > 0 and q.intersection(gpoly).area > 0.3 * q.area):
                gut = True
                if r['y'] < until: r['y'] = until; n += 1
        if gut or r.get('rail') or q.length <= 0 or 2 * q.area / q.length >= LANE_W: continue
        z = ctx.zone_at(c.x, c.y)
        if not z: continue
        f = ctx.first_near(c.x, c.y)
        y = max(ctx.ramp(z, c.x, c.y), f if f is not None else z['b1'])
        if y < r['y']: r['y'] = round(y, 1); m += 1
    with open(os.path.join(D, 'roads.json'), 'w') as f: json.dump(roads, f)
    return (n, m)


def bridges_pass(ctx, D):
    B = ctx.H.get('bridges', []) or []
    if not B: return (0, 0)
    br = _backup(D, 'bridges'); upd = add = 0
    for s in B:
        q = LineString(ctx.P.ring(s['line'])).buffer(float(s.get('w', 10)) / 2, cap_style=2)
        nm = (s.get('name') or '').strip().casefold(); hit = False
        for e in br:
            same = nm and (e.get('name') or '').strip().casefold() == nm
            if not same:
                try: p = _poly(e['r'])
                except Exception: continue
                same = p.area > 0 and p.intersection(q).area > 0.3 * min(p.area, q.area)
            if same:
                e['y'] = s['y']; e['d'] = s.get('d'); e['kit'] = 1; e['name'] = e.get('name') or s.get('name', ''); hit = True; upd += 1
        if not hit:
            br.append({'r': _ring_out(q), 'y': s['y'], 'd': s.get('d'), 'name': s.get('name', ''), 'kit': 1}); add += 1
    json.dump(br, open(os.path.join(D, 'bridges.json'), 'w'))
    return (upd, add)


def _grid(blds, hist):
    """urban_kit.json: 'p' = 10o percentile degli anni di nascita per cella di 120 m; 'first' = primo anno per cella di 60 m
    (attuali con l'anno originale prima dei fuochi + predecessori)."""
    cells = collections.defaultdict(list); first = {}
    for b in list(blds) + list(hist):
        try: x, y = b['r'][0]
        except Exception: continue
        yb = min(b['y'], b.get('y_kit0', b['y']))
        cells[(int(x // CELL), int(y // CELL))].append(yb)
        k = (int(x // FCELL), int(y // FCELL)); first[k] = min(first.get(k, 99999), yb)
    out = {}
    for k, v in cells.items():
        v.sort(); out[f'{k[0]},{k[1]}'] = round(v[min(len(v) - 1, int(len(v) * 0.1))], 1)
    return {'cell': CELL, 'p': out, 'fcell': FCELL, 'first': {f'{a},{b}': round(v, 1) for (a, b), v in first.items()}}


def _load_grid(ctx, g):
    ctx._grid = {tuple(map(int, k.split(','))): v for k, v in g['p'].items()}
    ctx._first = {tuple(map(int, k.split(','))): v for k, v in g['first'].items()}


def landphases(ctx, objs=()):
    """history.water -> landphases. Le lastre 'urban' (suolo di citta') non possono precedere le case: la lastra diventa
    'urban' solo sotto le impronte (alone ~10 m, chiuso a ~16 m) degli edifici nati fino a quel decennio, 'field' altrove.
    Una lastra 'urban' (o 'site') senza case (< 2/ha) e' un cantiere: c 'site' (terra nuda ocra) per tutta la finestra."""
    out = []
    cen = [(_poly(o['r']).centroid, o['y']) for o in objs if len(o.get('r', [])) >= 3] if objs else []
    for w in ctx.H.get('water', []) or []:
        a, b, c = w.get('from', -9999), w.get('to', 99999), w.get('c', 'field')
        ring = ctx.P.ring(w['ring']); nm = w.get('name', '')
        if c not in ('urban', 'site'):
            out.append({'r': ring, 'from': a, 'to': b, 'c': c, 'name': nm}); continue
        poly = _poly(ring).buffer(0); x0, y0, x1, y1 = poly.bounds
        ins = [(pt, y) for pt, y in cen if x0 <= pt.x <= x1 and y0 <= pt.y <= y1 and poly.contains(pt)]
        if c == 'site' or len(ins) < 2.0 * poly.area / 1e4:
            out.append({'r': ring, 'from': a, 'to': b, 'c': 'site', 'name': nm}); continue
        by = collections.defaultdict(list)
        for pt, y in ins: by[math.ceil(y / 10) * 10].append(pt.buffer(10, quad_segs=2))
        cum = Polygon()
        for u in sorted(by):
            g = unary_union(by[u]).buffer(6, quad_segs=2).buffer(-6, quad_segs=2)
            new = g.difference(cum).intersection(poly); cum = cum.union(g)
            for p_ in _polys(new):
                if p_.area < 20: continue
                t = max(a, u)
                if t > a: out.append({'r': _ring_out(p_, 1), 'from': a, 'to': min(t, b), 'c': 'field', 'name': nm})
                if t < b: out.append({'r': _ring_out(p_, 1), 'from': t, 'to': b, 'c': 'urban', 'name': nm})
        rest = poly.difference(cum.buffer(0.5))
        for p_ in _polys(rest):
            if p_.area >= 20: out.append({'r': _ring_out(p_, 1), 'from': a, 'to': b, 'c': 'field', 'name': nm})
    return out


# ---------------------------------------------------------------- pipeline

def build(story, D=None, seed=11, quiet=False):
    story = load_story(story) if isinstance(story, str) else story
    D = D or data_dir(story); ctx = Ctx(story); H = ctx.H
    blds = json.load(open(os.path.join(D, 'buildings.json')))
    touched = False
    for b in blds:                       # idempotenza: annulla gli spostamenti dei fuochi del giro precedente
        if 'y_kit0' in b: b['y'] = b.pop('y_kit0'); touched = True
    good = [b for b in blds if len(b.get('r', [])) >= 3]
    tree = STRtree([_poly(b['r']) for b in good])
    hist = zones_pass(ctx, good, random.Random(seed))
    gut, filled = gutting_pass(ctx, good, tree, random.Random(seed + 1))
    hist += gut + lost_pass(ctx)
    hist, ncl = clear_pass(ctx, D, hist, random.Random(seed + 4))
    burned = fires_pass(ctx, good, hist, random.Random(seed + 2))
    if any('y_kit0' in b for b in blds) or touched:
        json.dump(blds, open(os.path.join(D, 'buildings.json'), 'w'))
    json.dump(hist, open(os.path.join(D, 'hist.json'), 'w'))
    grid = _grid(good, hist); _load_grid(ctx, grid)
    json.dump(grid, open(os.path.join(D, 'urban_kit.json'), 'w'))
    if H.get('water'):
        ph = landphases(ctx, good + hist)
        if os.path.exists(os.path.join(D, 'landphases.json')): _backup(D, 'landphases')
        json.dump(ph, open(os.path.join(D, 'landphases.json'), 'w'))
    if H.get('fires'):
        fj = []
        for f in H['fires']:
            e = {'name': f.get('name', 'fire'), 'poly': ctx.P.ring(f['ring']), 'y': f['y'], 'y1': f.get('y1', f['y'] + 0.01),
                 'flames': f.get('flames', 40), 'smoke': min(9, f.get('smoke', 6)), 'houses': burned.get(f.get('name', 'fire'), 0)}
            if f.get('origin'): e['origin'] = list(ctx.P.L(*f['origin']))
            fj.append(e)
        json.dump(fj, open(os.path.join(D, 'fires.json'), 'w'))
    nroads = roads_pass(ctx, D)
    nbr = bridges_pass(ctx, D)
    walls = walls_parts(ctx, random.Random(seed + 3))
    json.dump(walls, open(os.path.join(D, 'landmarks_walls.json'), 'w'))
    # statistiche
    allb = blds + hist
    alive = {Y: sum(1 for b in allb if b['y'] <= Y < b.get('d', 99999)) for Y in (ctx.start,) + STAT_YEARS}
    st = {'predecessors': len(hist),
          'by_century': dict(sorted(collections.Counter(int(h['y'] // 100 * 100) for h in hist).items())),
          'by_zone': dict(collections.Counter(h.get('zone', h.get('name', '?')) for h in hist)),
          'by_kind': dict(collections.Counter(h['kit'] for h in hist)),
          'gutting_filled': filled, 'monument_sites_filled': ncl, 'roads_gutting_lanes': list(nroads), 'landphases': len(ph) if H.get('water') else None, 'bridges_updated_added': list(nbr), 'fires_destroyed': burned,
          'wall_parts': len(walls), 'alive': {str(int(k)): v for k, v in alive.items()}}
    json.dump(st, open(os.path.join(D, 'hist_kit_stats.json'), 'w'), indent=1)
    if not quiet:
        print(f"[hist_kit] {story['city']['slug']}: {len(hist)} predecessori da {len(blds)} edifici attuali", flush=True)
        for k in ('by_century', 'by_zone', 'by_kind', 'gutting_filled', 'monument_sites_filled', 'fires_destroyed'):
            print(f'[hist_kit] {k}: {st[k]}', flush=True)
        print(f"[hist_kit] strade gutting/vicoli anticipati {nroads}, landphases {st['landphases']}, ponti aggiornati/aggiunti {nbr}, parti mura {len(walls)}", flush=True)
        print('[hist_kit] edifici vivi: ' + ', '.join(f'{k}: {v}' for k, v in st['alive'].items()), flush=True)
    return st


# ---------------------------------------------------------------- stub e CLI

STUB = """# Generato da kit/hist_kit.py (make-stub): modulo hist di {slug} per build_render e run.sh.
import os
os.environ.setdefault('CITY3D_STORY', '{rel}')
from kit.hist_kit import urban_year, WALL_P

if __name__ == '__main__':
    from kit.hist_kit import main
    main()
"""


def make_stub(slug, root=ROOT):
    rel = f'cities/{slug}/story.json'
    p = os.path.join(root, f'hist_{slug}.py')
    with open(p, 'w') as f: f.write(STUB.format(slug=slug, rel=rel))
    return p


def main(argv=None):
    av = list(sys.argv[1:] if argv is None else argv)
    if av and av[0] == 'make-stub':
        p = make_stub(av[1]); print('[hist_kit] scritto', p); return
    if av and av[0] == 'build':
        build(av[1], av[2] if len(av) > 2 else None); return
    f = _story_file()                     # stub: python hist_<slug>.py DATA
    if not f: sys.exit('[hist_kit] nessuna story: imposta CITY3D_STORY')
    build(f, av[0] if av else None)


if __name__ == '__main__':
    main()
