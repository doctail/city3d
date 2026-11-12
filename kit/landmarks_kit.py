"""Kit Year Built: monumenti parametrici (preset) -> DATA/landmarks.json per build_render.py.

Ogni preset e' una funzione  preset(ctx) -> Builder  che produce parti nel formato di build_render.py
(prism / wedge / hip / cyl / cone / dome / beam / helix, vedi city3d_kit_spec.md 4.14). Ogni parte porta due
campi interni che diventano anni:
  _f  frazione 0..1 della sequenza di cantiere (0 fondazioni, ~0.5 corpo, ~0.9 tetto/guglia)
  _g  gruppo (found, body, nave, roof, tower, spire, dome, ...): una fase della story puo' prendersi certi gruppi.
Fasi (story.landmarks[i].phases): [{"y": 1262, "y1": 1300}, {"y": 1418, "y1": 1424, "groups": ["spire"]}, ...]
  - le fasi SENZA "groups" si dividono in ordine la sequenza _f (fase k = frazioni [k/n, (k+1)/n));
  - le fasi CON "groups" prendono solo quei gruppi (la loro _f rinormalizzata nella fase);
  - "d" in una fase con groups = quei gruppi spariscono in quell'anno (es. guglia crollata).
Demolizione: "demolished": anno | [y, y1]  -> le parti spariscono dall'alto verso il basso tra y e y1.
Impronta: "footprint": "auto" = edificio di DATA/buildings.json che contiene "at" (o il piu' vicino entro 30 m);
  orientamento dal rettangolo minimo; l'impronta va in "clear" (l'edificio del catasto sparisce).
  Opzioni: "fp_merge": m (unisce le particelle catastali vicine entro m metri, raggio fp_radius=80 m da "at").
CLI:  python -m kit.landmarks_kit build <slug|story.json> [DATA]   -> DATA/landmarks.json + montaggio/landmarks_<slug>.json
      python -m kit.landmarks_kit list                              -> preset disponibili
Catalogo dei preset e parametri: kit/presets_landmarks.md
"""
import json, math, os, sys
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union, substring
from shapely import affinity

try:
    from . import geo
except ImportError:   # eseguito come file
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from kit import geo

# ------------------------------------------------------------------ palette
PAL = {
    'stone': '#ddd0b2', 'stone2': '#cbbd9e', 'limestone': '#e8d9b4', 'sand': '#e3c99a', 'granite': '#b9b4ab',
    'brick': '#b9573a', 'brick2': '#9c4530', 'plaster': '#f0e4c8', 'ochre': '#e4b55a', 'cream': '#f3e9d2',
    'white': '#f4f2ea', 'calatrava': '#f6f6f2', 'concrete': '#cfccc4',
    'tile': '#c0583a', 'terracotta': '#c86c45', 'slate': '#59606b', 'lead': '#7d8590', 'copper': '#5fa08a',
    'gold': '#e0aa3e', 'bluetile': '#2f6fb3', 'greentile': '#3f9a6a',
    'glass': '#7fb2d0', 'glass2': '#5f93b5', 'steel': '#c4c9cf', 'iron': '#4f5a62', 'dark': '#3a3f45',
    'green': '#6d8f45', 'grass': '#6db346', 'arena': '#d9b46e', 'red': '#b8322a', 'wood': '#7a5232',
    'water': '#4aa3c4', 'seat': '#c0392b',
}
A_STONE, A_WIN, A_GLASS = 0.05, 1.0, 0.5
STYLE_ROOF = {'mediterranean': {'roof': 'terracotta', 'dome': 'bluetile', 'spire': 'stone'},
              'nordic': {'roof': 'copper', 'dome': 'copper', 'spire': 'copper'},
              'central': {'roof': 'slate', 'dome': 'lead', 'spire': 'slate'},
              'atlantic': {'roof': 'tile', 'dome': 'lead', 'spire': 'stone'}}
DEFAULT_SPAN = 0.6       # anni di cantiere se una fase non ha y1 (le parti compaiono comunque in sequenza)
FP_SEARCH_M = 30.0
MAX_FP = {k: 22.0 for k in ('tower_square', 'tower', 'tower_round', 'bell_tower', 'campanile', 'lighthouse')}   # lato max dell'impronta usabile


def col(x, default='stone'):
    x = x or default
    return PAL.get(x, x)


def _r2(v): return round(float(v), 2)


def ring(g, simp=0.15):
    """Polygon -> ring [[x,y],...] (senza chiusura); MultiPolygon -> il pezzo piu' grande; None se degenere."""
    if g is None or g.is_empty: return None
    if not g.is_valid: g = g.buffer(0)
    if g.geom_type == 'MultiPolygon' or g.geom_type == 'GeometryCollection':
        ps = [q for q in getattr(g, 'geoms', []) if q.geom_type == 'Polygon']
        if not ps: return None
        g = max(ps, key=lambda q: q.area)
    if g.geom_type != 'Polygon': return None
    g = g.simplify(simp) if simp else g
    if g.is_empty or g.area < 0.3: return None
    r = [[_r2(x), _r2(y)] for x, y in list(g.exterior.coords)[:-1]]
    out = []
    for p in r:
        if not out or p != out[-1]: out.append(p)
    if len(out) > 1 and out[0] == out[-1]: out.pop()
    if len(out) < 3 or not Polygon(out).is_valid or Polygon(out).area < 0.3: return None
    return out


def _polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    return [q for q in getattr(g, 'geoms', []) if q.geom_type == 'Polygon']


# ------------------------------------------------------------------ riferimento locale
class Frame:
    """Centro (cx, cy), asse u (angolo ang in gradi da est, antiorario) e v = u ruotato di +90."""

    def __init__(self, cx, cy, ang=0.0, L=None, W=None):
        self.cx, self.cy, self.ang = float(cx), float(cy), float(ang)
        a = math.radians(self.ang); self.u = (math.cos(a), math.sin(a)); self.v = (-self.u[1], self.u[0])
        self.L, self.W = L, W

    def at(self, s, t=0.0): return (self.cx + self.u[0] * s + self.v[0] * t, self.cy + self.u[1] * s + self.v[1] * t)

    def rect(self, s0, s1, t0, t1):
        return Polygon([self.at(s0, t0), self.at(s1, t0), self.at(s1, t1), self.at(s0, t1)])

    def poly(self, st): return Polygon([self.at(s, t) for s, t in st])

    def ngon(self, s, t, r, n, rot=0.0):   # poligono regolare ruotato col riferimento
        return self.poly([(s + r * math.cos(math.radians(rot) + 2 * math.pi * i / n), t + r * math.sin(math.radians(rot) + 2 * math.pi * i / n)) for i in range(n)])

    def ell(self, s, t, a, b, n=32, a0=0.0, a1=2 * math.pi):
        return self.poly([(s + a * math.cos(a0 + (a1 - a0) * i / n), t + b * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-9 else 1))])

    def p3(self, s, t, z): x, y = self.at(s, t); return [_r2(x), _r2(y), _r2(z)]

    def dirv(self, ds, dt): return (self.u[0] * ds + self.v[0] * dt, self.u[1] * ds + self.v[1] * dt)


def npoly(x, y, r, n, phase=0.0):
    """Poligono regolare allineato agli assi del mondo (primo vertice ad angolo 0: coincide con cyl/cone a n lati)."""
    return Polygon([(x + r * math.cos(phase + 2 * math.pi * i / n), y + r * math.sin(phase + 2 * math.pi * i / n)) for i in range(n)])


def frame_of(g, ang=None, flip=False):
    """Riferimento dal rettangolo minimo: u = asse lungo (verso est se possibile), L lunghezza, W larghezza."""
    m = g.minimum_rotated_rectangle; c = list(m.exterior.coords)[:4]
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    if math.hypot(*e1) < math.hypot(*e2): e1, e2 = e2, e1
    L, W = math.hypot(*e1), math.hypot(*e2)
    a = math.degrees(math.atan2(e1[1], e1[0]))
    if math.cos(math.radians(a)) < -1e-6 or (abs(math.cos(math.radians(a))) <= 1e-6 and math.sin(math.radians(a)) < 0): a += 180
    if ang is not None: a = float(ang)
    if flip: a += 180
    return Frame(m.centroid.x, m.centroid.y, a % 360, L, W)


# ------------------------------------------------------------------ costruttore di parti
class Builder:
    def __init__(self, ctx=None):
        self.parts, self.ctx = [], ctx

    def _add(self, f, g, **k):
        if k.get('a') == A_WIN and self.ctx is not None and not self.ctx.windows: k['a'] = A_STONE   # pietra: niente griglia di finestre
        k['_f'] = max(0.0, min(1.0, float(f))); k['_g'] = g; self.parts.append(k); return k

    def prism(self, geom, z0, z1, c, a=A_STONE, f=0.0, g='body', top=None, simp=0.15):
        r = ring(geom, simp) if not isinstance(geom, list) else geom
        if r is None or z1 - z0 < 0.05: return None
        k = dict(t='prism', r=r, z0=_r2(z0), z1=_r2(z1), c=col(c), a=a)
        if top: k['top'] = col(top)
        return self._add(f, g, **k)

    def wedge(self, geom, z0, za, zb, ax, c, top, a=A_STONE, f=0.0, g='roof'):
        r = ring(geom, 0.05)
        n = math.hypot(*ax)
        if r is None or n < 1e-9: return None
        ax = (ax[0] / n, ax[1] / n)
        return self._add(f, g, t='wedge', r=r, z0=_r2(z0), za=_r2(za), zb=_r2(zb), ax=[round(ax[0], 4), round(ax[1], 4)], c=col(c), top=col(top), a=a)

    def hip(self, geom, z0, rh, c, f=0.0, g='roof', a=A_STONE):
        r = ring(geom, 0.05)
        if r is None or rh < 0.05: return None
        return self._add(f, g, t='hip', r=r, z0=_r2(z0), z1=_r2(z0), rh=_r2(rh), c=col(c), a=a)

    def gable(self, F, s0, s1, t0, t1, z0, rh, c, roof, f=0.0, g='roof', a=A_STONE, along='u'):
        """Tetto a due falde: due wedge; along='u' colmo parallelo a u, 'v' colmo parallelo a v. Timpani chiusi (colore c)."""
        if along == 'u':
            tm = (t0 + t1) / 2
            self.wedge(F.rect(s0, s1, t0, tm), z0, z0, z0 + rh, F.v, c, roof, a, f, g)
            self.wedge(F.rect(s0, s1, tm, t1), z0, z0, z0 + rh, (-F.v[0], -F.v[1]), c, roof, a, f, g)
        else:
            sm = (s0 + s1) / 2
            self.wedge(F.rect(s0, sm, t0, t1), z0, z0, z0 + rh, F.u, c, roof, a, f, g)
            self.wedge(F.rect(sm, s1, t0, t1), z0, z0, z0 + rh, (-F.u[0], -F.u[1]), c, roof, a, f, g)

    def cyl(self, x, y, rad, z0, z1, c, a=A_STONE, f=0.0, g='body', seg=12):
        if z1 - z0 < 0.05 or rad <= 0: return None
        return self._add(f, g, t='cyl', cx=_r2(x), cy=_r2(y), rad=_r2(rad), z0=_r2(z0), z1=_r2(z1), seg=int(seg), c=col(c), a=a)

    def cone(self, x, y, r0, r1, z0, z1, c, a=A_STONE, f=0.0, g='roof', seg=12):
        if z1 - z0 < 0.05 or r0 <= 0: return None
        return self._add(f, g, t='cone', cx=_r2(x), cy=_r2(y), r0=_r2(r0), r1=_r2(max(r1, 0.05)), z0=_r2(z0), z1=_r2(z1), seg=int(seg), c=col(c), a=a)

    def dome(self, x, y, rad, z0, hz, c, a=A_STONE, f=0.0, g='dome'):
        if rad <= 0 or hz <= 0.05: return None
        return self._add(f, g, t='dome', cx=_r2(x), cy=_r2(y), rad=_r2(rad), z0=_r2(z0), hz=_r2(hz), c=col(c), a=a)

    def beam(self, p0, p1, w, h, c, a=A_STONE, f=0.0, g='body', noshadow=False):
        if math.dist(p0, p1) < 0.05: return None
        k = dict(t='beam', p0=[_r2(v) for v in p0], p1=[_r2(v) for v in p1], w=_r2(w), h=_r2(h), c=col(c), a=a,
                 cx=_r2((p0[0] + p1[0]) / 2), cy=_r2((p0[1] + p1[1]) / 2))
        if noshadow: k['noshadow'] = True
        return self._add(f, g, **k)

    def helix(self, x, y, r0, r1, z0, z1, turns, w, n, c, a=A_STONE, f=0.0, g='spire'):
        return self._add(f, g, t='helix', cx=_r2(x), cy=_r2(y), r0=_r2(r0), r1=_r2(r1), z0=_r2(z0), z1=_r2(z1), turns=turns, w=_r2(w), n_strands=int(n), c=col(c), a=a)

    def merlons(self, geom, z, c, f=0.9, g='merlons', mh=1.3, mw=1.1, gap=1.1, depth=0.9, maxn=40):
        """Merli lungo il bordo di un poligono (piccoli prismi orientati sul lato, verso l'interno)."""
        if geom is None or geom.is_empty: return
        ext = list(geom.exterior.coords); per = geom.exterior.length
        step = max(mw + gap, per / maxn)
        cw = Polygon(ext).exterior.is_ccw
        for (xa, ya), (xb, yb) in zip(ext, ext[1:]):
            L = math.hypot(xb - xa, yb - ya)
            if L < mw: continue
            ux, uy = (xb - xa) / L, (yb - ya) / L; nx, ny = (-uy, ux) if cw else (uy, -ux)   # normale verso l'interno
            n = max(1, int(L / step))
            for i in range(n):
                s = (i + 0.5) * L / n
                cx, cy = xa + ux * s + nx * depth / 2, ya + uy * s + ny * depth / 2
                q = Polygon([(cx - ux * mw / 2 - nx * depth / 2, cy - uy * mw / 2 - ny * depth / 2), (cx + ux * mw / 2 - nx * depth / 2, cy + uy * mw / 2 - ny * depth / 2),
                             (cx + ux * mw / 2 + nx * depth / 2, cy + uy * mw / 2 + ny * depth / 2), (cx - ux * mw / 2 + nx * depth / 2, cy - uy * mw / 2 + ny * depth / 2)])
                self.prism(q, z, z + mh, c, A_STONE, f, g, simp=0)

    def sectors(self, F, a1, b1, a2, b2, z0, z1, c, a=A_STONE, f=0.0, g='body', n=24, keep=None, top=None, fstep=0.0):
        """Anello ellittico a settori (il prisma non ha buchi): esterno a1,b1, interno a2,b2 (nel riferimento F)."""
        out = []
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n; tm = (t0 + t1) / 2
            if keep and not keep(tm): continue
            q = F.poly([(a1 * math.cos(t0), b1 * math.sin(t0)), (a1 * math.cos(t1), b1 * math.sin(t1)),
                        (a2 * math.cos(t1), b2 * math.sin(t1)), (a2 * math.cos(t0), b2 * math.sin(t0))])
            out.append(self.prism(q, z0, z1, c, a, f + fstep * i / n, g, top=top, simp=0))
        return out


# ------------------------------------------------------------------ contesto di un monumento
class Ctx:
    def __init__(self, name, F, p, fp=None, line=None, bh=None, style=None):
        self.name, self.F, self.p, self.fp, self.line, self.bh = name, F, dict(p or {}), fp, line, bh
        self.style = STYLE_ROOF.get(style or '', STYLE_ROOF['mediterranean'])
        self.windows = True   # deciso da build_landmark (stone_default)

    def g(self, k, d=None):
        v = self.p.get(k)
        return d if v is None else v

    def dims(self, L, W):
        """Lunghezza e larghezza: params (l/w) > impronta (rettangolo minimo) > default."""
        s = float(self.g('scale', 1.0))
        Lp = self.g('l', self.g('length')); Wp = self.g('w', self.g('width'))
        if Lp is None: Lp = self.F.L if (self.fp is not None and self.F.L) else L * s
        if Wp is None: Wp = self.F.W if (self.fp is not None and self.F.W) else W * s
        return float(Lp), float(Wp)

    def roof(self, k='roof_c', what='roof'): return self.g(k, self.style[what])


# ================================================================== PRESET
PRESETS = {}
# preset in pietra: senza finestre "da ufficio" (a=0.05) salvo params.windows; palazzi/chiese a cupola/edifici dal 1800 con finestre
STONE_KINDS = {'tower_square', 'tower', 'tower_round', 'bell_tower', 'campanile', 'cathedral', 'church', 'gate_towers', 'gate',
               'castle', 'wall_segment', 'walls', 'bridge_arches', 'bridge'}
STONE_BEFORE = {'palace_courtyard': 1800, 'palace': 1800, 'church_dome': 1800, 'central_church': 1800, 'bullring': 1800,
                'arena': 1800, 'amphitheatre': 1800, 'generic_footprint': 1800, 'footprint': 1800, 'building': 1800}


def openings(B, F, x, y, w, z0, z1, f, g='body', n=1, ow=None, c='dark', faces=4):
    """Aperture scure (bifore, feritoie) sulle facce di una torre quadrata di lato w centrata in (x, y) del riferimento F."""
    ow = ow or max(0.6, w * 0.16)
    for k in range(faces):
        a = math.pi / 2 * k; ds, dt = math.cos(a), math.sin(a)
        for j in range(n):
            o = (j - (n - 1) / 2) * w / max(n, 1) * 0.9
            cs, ct = x + ds * (w / 2) - dt * o, y + dt * (w / 2) + ds * o
            q = F.rect(cs - abs(ds) * 0.2 - abs(dt) * ow / 2, cs + abs(ds) * 0.2 + abs(dt) * ow / 2,
                       ct - abs(dt) * 0.2 - abs(ds) * ow / 2, ct + abs(dt) * 0.2 + abs(ds) * ow / 2)
            B.prism(q, z0, z1, c, A_STONE, f, g, simp=0)


def openings_ring(B, x, y, r, z0, z1, f, g='body', n=4, ow=1.0, c='dark'):
    """Aperture scure su una pianta circolare/ottagonale (raggio r), n direzioni."""
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        B.prism(npoly(x + r * math.cos(a), y + r * math.sin(a), ow / 2, 4, a + math.pi / 4), z0, z1, c, A_STONE, f, g, simp=0)


def preset(name, *aliases):
    def deco(fn):
        PRESETS[name] = fn
        for a in aliases: PRESETS[a] = fn
        fn.preset_name = name
        return fn
    return deco


def _tower_top(B, F, x, y, w, z, top, c, rc, f, plan='square', g='roof', spire_h=None):
    """Copertura di una torre: pyramid | spire | dome | onion | flat | crenel | lantern | cage."""
    sq = F.rect(x - w / 2, x + w / 2, y - w / 2, y + w / 2) if plan == 'square' else None
    wx, wy = F.at(x, y)
    if top == 'pyramid' and sq is None:
        B.cyl(wx, wy, w / 2 + 0.5, z, z + 0.8, 'stone', f=f - 0.03, g=g, seg=12); B.cone(wx, wy, w / 2 + 0.7, 0.2, z + 0.8, z + 0.8 + w * 0.8, rc, f=f, g=g, seg=12)
        return z + 0.8 + w * 0.8
    if top == 'pyramid':
        B.prism(sq.buffer(0.5, join_style=2), z, z + 0.8, 'stone', f=f - 0.03, g=g); B.hip(sq.buffer(0.6, join_style=2), z + 0.8, w * 0.75, rc, f, g)
        return z + 0.8 + w * 0.75
    if top == 'spire':
        h = spire_h or w * 2.6
        B.prism(sq.buffer(0.5, join_style=2), z, z + 0.8, 'stone', f=f - 0.03, g=g) if sq else B.cyl(wx, wy, w / 2 + 0.5, z, z + 0.8, 'stone', f=f - 0.03, g=g, seg=8)
        B.cone(wx, wy, w * 0.5, 0.15, z + 0.8, z + 0.8 + h, rc, f=f, g='spire', seg=8)
        for sx in (-1, 1):   # pinnacoli
            for sy in (-1, 1):
                px, py = F.at(x + sx * w * 0.42, y + sy * w * 0.42)
                B.cone(px, py, w * 0.09, 0.05, z + 0.8, z + 0.8 + w * 0.7, 'stone', f=f, g='spire', seg=4)
        return z + 0.8 + h
    if top in ('dome', 'onion'):
        r = w * 0.48
        B.cyl(wx, wy, r * 0.95, z, z + w * 0.35, c, A_STONE, f - 0.03, g, seg=16)
        hz = r * (1.5 if top == 'onion' else 0.95)
        B.dome(wx, wy, r, z + w * 0.35, hz, rc, f=f, g='dome')
        z2 = z + w * 0.35 + hz
        B.cyl(wx, wy, r * 0.22, z2 - 0.4, z2 + r * 0.5, c, A_WIN, f + 0.02, 'lantern', seg=8)
        B.cone(wx, wy, r * 0.3, 0.05, z2 + r * 0.5, z2 + r * 1.3, rc, f=f + 0.04, g='lantern', seg=8)
        return z2 + r * 1.3
    if top == 'cage':   # piccola cella aperta (campana) su terrazza: 4 pilastrini + tettuccio
        r = w * 0.18
        for sx in (-1, 1):
            for sy in (-1, 1):
                px, py = F.at(x + sx * r, y + sy * r)
                B.cyl(px, py, 0.35, z, z + 4.0, 'iron', A_STONE, f, 'top', seg=4)
        B.cone(wx, wy, r * 1.7, 0.1, z + 4.0, z + 6.0, 'iron', f=f + 0.02, g='top', seg=8)
        return z + 6.0
    if top == 'lantern':   # faro / lanterna vetrata
        r = w * 0.32
        B.cyl(wx, wy, w * 0.55, z, z + 0.7, 'iron', f=f - 0.03, g=g, seg=16)
        B.cyl(wx, wy, r, z + 0.7, z + 3.5, 'glass', A_GLASS, f, 'top', seg=12)
        B.dome(wx, wy, r * 1.05, z + 3.5, r * 0.9, rc, f=f + 0.02, g='top')
        return z + 3.5 + r * 0.9
    # flat / crenel
    if sq is not None:
        B.prism(sq.buffer(0.6, join_style=2), z, z + 1.0, c, f=f - 0.03, g=g)
        if top == 'crenel': B.merlons(sq.buffer(0.6, join_style=2), z + 1.0, c, f=f, g='merlons', maxn=16)
    else:
        B.cyl(wx, wy, w / 2 + 0.6, z, z + 1.0, c, f=f - 0.03, g=g, seg=16)
        if top == 'crenel':
            n = max(6, min(16, int(math.pi * w / 2.4)))
            for i in range(n):
                a = 2 * math.pi * (i + 0.5) / n; R = w / 2 + 0.1
                B.prism(npoly(wx + R * math.cos(a), wy + R * math.sin(a), 0.75, 4, a + math.pi / 4), z + 1.0, z + 2.3, c, f=f, g='merlons', simp=0)
    return z + (2.3 if top == 'crenel' else 1.0)


@preset('tower_square', 'tower')
def tower_square(ctx):
    """Torre quadrata: zoccolo, fusto in 3 rocchi, cella campanaria (finestre), copertura (roof)."""
    B, F = Builder(ctx), ctx.F
    w = float(ctx.g('w', min(F.L, F.W) if ctx.fp is not None else 10.0)); h = float(ctx.g('h', 40.0))
    c, rc, top = ctx.g('c', 'brick'), col(ctx.roof()), ctx.g('roof', 'pyramid')
    belfry = ctx.g('belfry', True)
    sq = F.rect(-w / 2, w / 2, -w / 2, w / 2)
    B.prism(sq.buffer(0.7, join_style=2), 0, 2.5, 'stone2', f=0.0, g='found')
    zb = h * (0.8 if belfry else 1.0); n = 3
    for i in range(n): B.prism(sq, 2.5 + (zb - 2.5) * i / n, 2.5 + (zb - 2.5) * (i + 1) / n, c, A_STONE, 0.15 + 0.17 * i, 'body')
    if belfry:
        B.prism(sq, zb, h, c, A_WIN, 0.68, 'belfry')
        if not ctx.windows: openings(B, F, 0, 0, w, zb + 1.2, h - 1.2, 0.7, 'belfry', n=2)
    _tower_top(B, F, 0, 0, w, h, top, c, rc, 0.88)
    return B


@preset('tower_round')
def tower_round(ctx):
    """Torre cilindrica: top = cone | dome | crenel | flat | lantern; belfry (anello finestrato) opzionale."""
    B, F = Builder(ctx), ctx.F
    rad = float(ctx.g('rad', (min(F.L, F.W) / 2) if ctx.fp is not None else 6.0)); h = float(ctx.g('h', 30.0))
    c, rc, top = ctx.g('c', 'stone'), col(ctx.roof()), ctx.g('top', 'cone'); seg = int(ctx.g('seg', 16))
    x, y = F.cx, F.cy
    B.cyl(x, y, rad + 0.8, 0, 2.0, 'stone2', f=0.0, g='found', seg=seg)
    belfry = ctx.g('belfry', False); zb = h * (0.84 if belfry else 1.0)
    for i in range(3): B.cyl(x, y, rad, 2.0 + (zb - 2) * i / 3, 2.0 + (zb - 2) * (i + 1) / 3, c, A_STONE, 0.15 + 0.17 * i, 'body', seg)
    if belfry:
        B.cyl(x, y, rad, zb, h, c, A_WIN, 0.68, 'belfry', seg)
        if not ctx.windows: openings_ring(B, x, y, rad, zb + 1, h - 1, 0.7, 'belfry', n=4, ow=rad * 0.35)
    if top == 'cone':
        B.cyl(x, y, rad + 0.5, h, h + 0.8, 'stone', f=0.82, g='roof', seg=seg)
        B.cone(x, y, rad + 0.7, 0.2, h + 0.8, h + 0.8 + rad * float(ctx.g('cone_k', 1.8)), rc, f=0.9, g='roof', seg=seg)
    elif top == 'dome':
        B.cyl(x, y, rad + 0.4, h, h + 0.8, 'stone', f=0.82, g='roof', seg=seg); B.dome(x, y, rad, h + 0.8, rad * 0.9, rc, f=0.9)
    else:
        _tower_top(B, Frame(x, y, F.ang), 0, 0, rad * 2, h, top, c, rc, 0.88, plan='round')
    return B


@preset('lighthouse')
def lighthouse(ctx):
    """Faro: torre cilindrica rastremata a fasce, ballatoio e lanterna vetrata."""
    B, F = Builder(ctx), ctx.F
    rad = float(ctx.g('rad', 4.5)); h = float(ctx.g('h', 32.0)); c, c2 = ctx.g('c', 'white'), ctx.g('band_c', 'red')
    x, y = F.cx, F.cy
    B.cyl(x, y, rad + 3, 0, 3.0, 'stone2', f=0.0, g='found', seg=12)
    n = 4
    for i in range(n):
        z0, z1 = 3 + (h - 3) * i / n, 3 + (h - 3) * (i + 1) / n
        B.cone(x, y, rad * (1 - 0.25 * i / n), rad * (1 - 0.25 * (i + 1) / n), z0, z1, c if i % 2 == 0 else c2, A_STONE, 0.15 + 0.15 * i, 'body', seg=14)
    _tower_top(B, Frame(x, y, F.ang), 0, 0, rad * 1.6, h, 'lantern', c, col('red'), 0.85, plan='round')
    return B


@preset('bell_tower', 'campanile')
def bell_tower(ctx):
    """Campanile. style: gothic (fusto a cornici, cella, guglia ottagonale con pinnacoli) | baroque (piani rastremati,
    cupolino a cipolla) | romanesque (piramide bassa, bifore) | flat (terrazza merlata con celletta, tipo Micalet).
    plan: square | octagon."""
    B, F = Builder(ctx), ctx.F
    style = ctx.g('style', 'gothic'); plan = ctx.g('plan', 'octagon' if (style == 'flat' or ctx.g('octagonal')) else 'square')
    w = float(ctx.g('w', min(F.L, F.W) if ctx.fp is not None else (12.0 if style == 'flat' else 9.0)))
    h = float(ctx.g('h', {'gothic': 50.0, 'baroque': 42.0, 'romanesque': 32.0, 'flat': 51.0}.get(style, 45.0)))
    c = ctx.g('c', {'gothic': 'limestone', 'baroque': 'brick', 'romanesque': 'stone', 'flat': 'limestone'}.get(style, 'stone'))
    rc = col(ctx.g('roof_c', {'gothic': ctx.style['spire'], 'baroque': ctx.style['dome'], 'romanesque': ctx.style['roof'], 'flat': 'iron'}.get(style)))
    x, y = F.cx, F.cy

    def shaft(z0, z1, ww, a, f, g='body'):
        if plan == 'octagon': B.prism(npoly(x, y, ww / 2 / math.cos(math.pi / 8), 8), z0, z1, c, a, f, g, simp=0)
        else: B.prism(F.rect(-ww / 2, ww / 2, -ww / 2, ww / 2), z0, z1, c, a, f, g, simp=0)

    def course(z, ww, f):   # cornice marcapiano
        if plan == 'octagon': B.prism(npoly(x, y, (ww / 2 + 0.5) / math.cos(math.pi / 8), 8), z, z + 0.7, 'stone', A_STONE, f, 'body', simp=0)
        else: B.prism(F.rect(-ww / 2 - 0.5, ww / 2 + 0.5, -ww / 2 - 0.5, ww / 2 + 0.5), z, z + 0.7, 'stone', A_STONE, f, 'body', simp=0)

    shaft(0, 2.0, w + 1.2, A_STONE, 0.0, 'found')
    if style == 'baroque':
        stages = [(2.0, h * 0.55, w, A_STONE), (h * 0.55, h * 0.78, w * 0.86, A_WIN), (h * 0.78, h, w * 0.72, A_WIN)]
        for i, (z0, z1, ww, a) in enumerate(stages):
            shaft(z0, z1, ww, a, 0.12 + 0.22 * i); course(z1, ww, 0.2 + 0.22 * i)
            if i >= 1 and not ctx.windows: openings(B, F, 0, 0, ww, z0 + 1.5, z1 - 1.2, 0.14 + 0.22 * i, n=1, ow=ww * 0.3)
            if i >= 1:   # vasi/pinnacoli agli angoli
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        px, py = F.at(sx * ww * 0.45, sy * ww * 0.45); B.cone(px, py, 0.6, 0.1, z1 + 0.7, z1 + 2.8, 'stone', f=0.24 + 0.22 * i, g='body', seg=6)
        _tower_top(B, F, 0, 0, w * 0.72, h + 0.7, 'onion', c, rc, 0.88, plan='round')
        return B
    zb = h * 0.78
    n = 3
    for i in range(n):
        z0, z1 = 2.0 + (zb - 2) * i / n, 2.0 + (zb - 2) * (i + 1) / n
        shaft(z0, z1, w, A_STONE, 0.12 + 0.17 * i); course(z1, w, 0.13 + 0.17 * i)
    shaft(zb + 0.7, h, w, A_WIN, 0.66, 'belfry')
    if not ctx.windows:
        if plan == 'octagon': openings_ring(B, x, y, w / 2 + 0.1, zb + 2, h - 1.2, 0.68, 'belfry', n=8, ow=w * 0.16)
        else: openings(B, F, 0, 0, w, zb + 2, h - 1.2, 0.68, 'belfry', n=2)
    if style == 'gothic':
        if plan == 'octagon':
            B.prism(npoly(x, y, (w / 2 + 0.6) / math.cos(math.pi / 8), 8), h, h + 0.8, 'stone', A_STONE, 0.8, 'roof', simp=0)
            B.cone(x, y, w * 0.5, 0.15, h + 0.8, h + 0.8 + w * 2.6, rc, f=0.92, g='spire', seg=8)
        else: _tower_top(B, F, 0, 0, w, h, 'spire', c, rc, 0.9)
    elif style == 'romanesque':
        _tower_top(B, F, 0, 0, w, h, 'pyramid', c, rc, 0.9)
    else:   # flat: terrazza merlata + celletta della campana
        if plan == 'octagon':
            g8 = npoly(x, y, (w / 2 + 0.6) / math.cos(math.pi / 8), 8)
            B.prism(g8, h, h + 1.2, c, A_STONE, 0.82, 'roof', simp=0); B.merlons(g8, h + 1.2, c, f=0.86, maxn=24)
        else: _tower_top(B, F, 0, 0, w, h, 'crenel', c, rc, 0.86)
        _tower_top(B, F, 0, 0, w, h + 1.2, 'cage', c, rc, 0.94)
    return B


def _semi(F, s, t, r, n=10, side=1):
    """Mezzo disco centrato (s, t) verso +u (side=1) o -u, come poligono."""
    pts = [(s + side * r * math.cos(math.pi / 2 - math.pi * i / n), t + r * math.sin(math.pi / 2 - math.pi * i / n)) for i in range(n + 1)]
    return F.poly(pts)


@preset('cathedral')
def cathedral(ctx):
    """Cattedrale a croce latina: u punta all'abside (est). Fondazioni, abside e coro, transetto, navata (da est a ovest),
    tetti, tiburio sulla crociera (crossing: lantern | dome | spire | none), facciata, torri di facciata (facade_towers 0/1/2).
    Con footprint: le navate laterali seguono l'impronta del catasto, navata alta e transetto sono rettangoli nel suo asse.
    tower_ref = nome del campanile separato (un altro landmark della story): la sua area viene tolta dall'impronta."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(90.0, 40.0)
    nh, ah = float(ctx.g('nave_h', 26.0)), float(ctx.g('aisle_h', 15.0)); nw = float(ctx.g('nave_w', W * 0.4))
    c, rc = ctx.g('c', 'limestone'), col(ctx.roof()); dc = col(ctx.g('dome_c', ctx.style['dome']))
    apse = ctx.g('apse', True); transept = ctx.g('transept', True); crossing = ctx.g('crossing', 'lantern')
    ntow = int(ctx.g('facade_towers', 2)); rh = nw * 0.42
    Ra = nw / 2 + 1 if apse else 0.0
    s_w, s_e = -L / 2, L / 2 - (W / 2 * 0.85 if apse else 0)   # corpo rettangolare (facciata a s_w)
    s_c = s_e - float(ctx.g('crossing_from_end', max(nw * 0.8, (s_e - s_w) * 0.18))) if transept else None
    body = ctx.fp if ctx.fp is not None else F.rect(s_w, s_e, -W / 2, W / 2)
    if ctx.fp is not None and ctx.g('_tower_cut') is not None: body = body.difference(ctx.g('_tower_cut'))
    B.prism(body.buffer(0.8, join_style=2), 0, 1.2, 'stone2', f=0.0, g='found')
    # abside (prima: si costruiva dal coro) -- deambulatorio basso + abside alta con tetto conico
    if apse:
        B.prism(_semi(F, s_e, 0, W / 2 * 0.85, 12), 0, ah, c, A_STONE, 0.08, 'apse', top=rc)
        B.prism(_semi(F, s_e, 0, nw / 2 + 0.5, 10), ah, nh - 1, c, A_WIN, 0.14, 'apse')
        ax_, ay_ = F.at(s_e, 0); B.cone(ax_, ay_, nw / 2 + 1.0, 0.3, nh - 1, nh - 1 + rh * 0.95, rc, f=0.2, g='roof', seg=16)
    # navate laterali (basse) a fette da est a ovest
    n = int(ctx.g('slices', 4))
    edges = [s_e - (s_e - s_w) * i / n for i in range(n + 1)]
    for i in range(n):
        sl = body.intersection(F.rect(edges[i + 1], edges[i], -W, W))
        for q in _polys(sl): B.prism(q, 0, ah, c, A_STONE, 0.12 + 0.1 * i, 'nave', top=rc)
    # navata alta + tetto a due falde, stesse fette
    for i in range(n):
        s0, s1 = edges[i + 1], edges[i]
        B.prism(F.rect(s0, s1, -nw / 2, nw / 2), ah - 0.5, nh, c, A_WIN, 0.16 + 0.1 * i, 'nave', simp=0)
        B.gable(F, s0, s1, -nw / 2 - 0.4, nw / 2 + 0.4, nh, rh, c, rc, 0.22 + 0.1 * i, 'roof')
        for sgn in (-1, 1):   # contrafforti sul muro esterno delle navate (pilastro + pinnacolo) e finestre ogivali della navata alta
            sm = s1 if i == 0 else (s0 + s1) / 2
            seg_ = body.intersection(LineString([F.at(sm, 0), F.at(sm, sgn * (W + 20))]))
            _pts = [c_ for g_ in getattr(seg_, 'geoms', [seg_]) if not g_.is_empty and hasattr(g_, 'coords') for c_ in g_.coords]
            te = max((abs((px - F.cx) * F.v[0] + (py - F.cy) * F.v[1]) for px, py in _pts), default=W / 2)
            pc = (sm, sgn * (te + 1.0))
            B.prism(F.rect(pc[0] - 1.0, pc[0] + 1.0, pc[1] - 1.4, pc[1] + 1.4), 0, ah + 3, c, A_STONE, 0.14 + 0.1 * i, 'nave', simp=0)
            px_, py_ = F.at(*pc); B.cone(px_, py_, 1.3, 0.1, ah + 3, ah + 7.5, c, A_STONE, 0.2 + 0.1 * i, 'nave', seg=4)
            if not ctx.windows:
                wx_ = (s0 + s1) / 2
                B.prism(F.rect(wx_ - 1.1, wx_ + 1.1, sgn * (nw / 2) - 0.2, sgn * (nw / 2) + 0.2), ah + 2, nh - 2.5, 'dark', A_STONE, 0.17 + 0.1 * i, 'nave', simp=0)
    # transetto (bracci oltre la navata solo senza impronta)
    if transept:
        ext = 0.0 if ctx.fp is not None else W * 0.18
        tw = nw
        if not ctx.windows:   # rosoni dei bracci del transetto
            for sg in (-1, 1):
                te_ = sg * (W / 2 + ext); rr_ = nw * 0.14
                B.prism(F.rect(s_c - rr_, s_c + rr_, te_ - 0.2 * sg - 0.01, te_ + 0.25 * sg), nh * 0.62 - rr_, nh * 0.62 + rr_, 'dark', A_STONE, 0.14, 'transept', simp=0)
        B.prism(F.rect(s_c - tw / 2, s_c + tw / 2, -W / 2 - ext, W / 2 + ext), 0, nh, c, A_WIN, 0.12, 'transept', simp=0)
        B.gable(F, s_c - tw / 2 - 0.4, s_c + tw / 2 + 0.4, -W / 2 - ext, W / 2 + ext, nh, rh, c, rc, 0.21, 'roof', along='v')
        cx_, cy_ = F.at(s_c, 0)
        if crossing == 'lantern':   # tiburio ottagonale finestrato
            r8 = nw * 0.5 / math.cos(math.pi / 8)
            B.prism(npoly(cx_, cy_, r8, 8), nh, nh + rh + nw * 0.45, c, A_WIN, 0.62, 'crossing', simp=0)
            B.prism(npoly(cx_, cy_, r8 + 0.5, 8), nh + rh + nw * 0.45, nh + rh + nw * 0.45 + 0.8, 'stone', A_STONE, 0.66, 'crossing', simp=0)
            B.cone(cx_, cy_, r8 + 0.3, 0.3, nh + rh + nw * 0.45 + 0.8, nh + rh + nw * 0.45 + 0.8 + nw * 0.32, rc, f=0.7, g='crossing', seg=8)
        elif crossing == 'dome':
            rd = nw * 0.5
            B.cyl(cx_, cy_, rd, nh, nh + rh + nw * 0.35, c, A_WIN, 0.62, 'crossing', seg=20)
            B.dome(cx_, cy_, rd, nh + rh + nw * 0.35, rd * 0.95, dc, f=0.7, g='crossing')
            zt = nh + rh + nw * 0.35 + rd * 0.95
            B.cyl(cx_, cy_, rd * 0.18, zt - 0.5, zt + rd * 0.45, c, A_WIN, 0.74, 'crossing', seg=8)
            B.cone(cx_, cy_, rd * 0.22, 0.05, zt + rd * 0.45, zt + rd * 0.9, dc, f=0.76, g='crossing', seg=8)
        elif crossing == 'spire':
            B.cone(cx_, cy_, nw * 0.22, 0.12, nh + rh * 0.7, nh + rh + nw * 2.2, rc, f=0.72, g='crossing', seg=8)
    # facciata: schermo a timpano piu' alto della navata
    fz = nh + rh + 3
    fwid = nw / 2 + (2.5 if ntow == 2 else 1.5)
    B.prism(F.rect(s_w, s_w + 3.0, -fwid, fwid), 0, nh, c, A_STONE, 0.6, 'facade', simp=0)
    B.wedge(F.rect(s_w, s_w + 3.0, -fwid, 0), nh, nh, fz, F.v, c, c, A_STONE, 0.64, 'facade')
    B.wedge(F.rect(s_w, s_w + 3.0, 0, fwid), nh, nh, fz, (-F.v[0], -F.v[1]), c, c, A_STONE, 0.64, 'facade')
    rr_ = nw * 0.14   # rosone e portale scuri, nel piano della facciata
    B.prism(F.rect(s_w - 0.25, s_w + 0.2, -rr_, rr_), nh * 0.62 - rr_, nh * 0.62 + rr_, 'dark', A_STONE, 0.66, 'facade', simp=0)
    B.prism(F.rect(s_w - 0.25, s_w + 0.2, -nw * 0.12, nw * 0.12), 0.01, nh * 0.32, 'dark', A_STONE, 0.66, 'facade', simp=0)
    # torri di facciata
    if ntow:
        tw_ = max(7.0, (W - nw) / 2 * 0.95); th = float(ctx.g('tower_h', nh * 1.7))
        ts = [(-1,), (1,)] if ntow == 2 else [(-1,)]
        for (sg,) in ts:
            tt = sg * (nw / 2 + tw_ / 2 + 0.5)
            sq = F.rect(s_w + 0.2, s_w + 0.2 + tw_, tt - tw_ / 2, tt + tw_ / 2)
            B.prism(sq, 0, th * 0.55, c, A_STONE, 0.7, 'towers', simp=0)
            B.prism(sq, th * 0.55, th, c, A_WIN, 0.78, 'towers', simp=0)
            _tower_top(B, F, s_w + 0.2 + tw_ / 2, tt, tw_, th, ctx.g('tower_top', 'spire' if ctx.style['spire'] != 'stone' else 'pyramid'), c, rc, 0.9)
    return B


@preset('church')
def church(ctx):
    """Chiesa parrocchiale: cattedrale ridotta (navata unica alta, niente transetto, una torre in facciata)."""
    p = dict(dict(transept=False, facade_towers=1, crossing='none', nave_h=16.0, aisle_h=9.0), **ctx.p)
    if ctx.fp is None: p.setdefault('l', 45.0); p.setdefault('w', 18.0)
    p.setdefault('nave_w', (p.get('w') or ctx.F.W or 18.0) * 0.55); p.setdefault('tower_h', 30.0); p.setdefault('slices', 2)
    c2 = Ctx(ctx.name, ctx.F, p, ctx.fp, ctx.line, ctx.bh); c2.style, c2.windows = ctx.style, ctx.windows
    return cathedral(c2)


@preset('church_dome', 'central_church')
def church_dome(ctx):
    """Chiesa a pianta centrale: plan cross (croce greca con timpani) | octagon | round; tamburo finestrato, cupola, lanterna, palla."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(40.0, 40.0); w = float(ctx.g('size', min(L, W)))
    plan = ctx.g('plan', 'cross'); bh = float(ctx.g('base_h', 16.0))
    c, rc, dc = ctx.g('c', 'plaster'), col(ctx.roof()), col(ctx.g('dome_c', ctx.style['dome']))
    rd = float(ctx.g('drum_r', w * 0.24)); dh = float(ctx.g('drum_h', rd * 0.9)); hz = float(ctx.g('dome_hz', rd * 1.05))
    x, y = F.cx, F.cy
    if plan == 'cross':
        aw = w * 0.42
        B.prism(F.rect(-w / 2, w / 2, -w / 2, w / 2).buffer(0.6, join_style=2), 0, 1.0, 'stone2', f=0.0, g='found', simp=0)
        B.prism(F.rect(-aw / 2 - 2, aw / 2 + 2, -aw / 2 - 2, aw / 2 + 2), 0, bh, c, A_WIN, 0.15, 'body', simp=0)
        B.prism(F.rect(-w / 2, w / 2, -aw / 2, aw / 2), 0, bh, c, A_WIN, 0.2, 'body', simp=0)
        B.prism(F.rect(-aw / 2, aw / 2, -w / 2, w / 2), 0, bh, c, A_WIN, 0.25, 'body', simp=0)
        for q in (F.rect(-w / 2, -aw / 2, -w / 2, -aw / 2), F.rect(aw / 2, w / 2, -w / 2, -aw / 2), F.rect(-w / 2, -aw / 2, aw / 2, w / 2), F.rect(aw / 2, w / 2, aw / 2, w / 2)):
            B.prism(q, 0, bh * 0.6, c, A_WIN, 0.3, 'body', top=rc, simp=0)   # cappelle d'angolo basse
        B.gable(F, -w / 2, w / 2, -aw / 2, aw / 2, bh, aw * 0.3, c, rc, 0.4)
        B.gable(F, -aw / 2, aw / 2, -w / 2, w / 2, bh, aw * 0.3, c, rc, 0.42, along='v')
        z0 = bh + aw * 0.3
    else:
        n = 8 if plan == 'octagon' else 24
        R = w / 2 / (math.cos(math.pi / 8) if n == 8 else 1)
        B.prism(npoly(x, y, R + 0.8, n), 0, 1.0, 'stone2', f=0.0, g='found', simp=0)
        B.prism(npoly(x, y, R, n), 1.0, bh, c, A_WIN, 0.2, 'body', simp=0)
        B.cone(x, y, R + 0.4, rd + 0.5, bh, bh + (R - rd) * 0.35, rc, f=0.4, g='roof', seg=n)
        z0 = bh + (R - rd) * 0.35
    B.cyl(x, y, rd, z0 - 1.0, z0 + dh, c, A_WIN, 0.55, 'drum', seg=20)
    if not ctx.windows: openings_ring(B, x, y, rd + 0.05, z0 + dh * 0.25, z0 + dh * 0.8, 0.57, 'drum', n=8, ow=rd * 0.22)
    B.cyl(x, y, rd + 0.5, z0 + dh, z0 + dh + 0.8, 'stone', A_STONE, 0.6, 'drum', seg=20)
    B.dome(x, y, rd, z0 + dh + 0.8, hz, dc, f=0.72, g='dome')
    zt = z0 + dh + 0.8 + hz
    B.cyl(x, y, rd * 0.2, zt - 0.6, zt + rd * 0.5, c, A_WIN, 0.84, 'lantern', seg=8)
    B.dome(x, y, rd * 0.24, zt + rd * 0.5, rd * 0.25, dc, f=0.88, g='lantern')
    B.cone(x, y, rd * 0.06, 0.05, zt + rd * 0.72, zt + rd * 1.05, 'gold', f=0.92, g='lantern', seg=6)
    return B


@preset('gate_towers', 'gate')
def gate_towers(ctx):
    """Porta urbica a due torri: u = direzione delle mura, il passaggio e' lungo v (+v = fuori città).
    tower_plan: polygon (esagonali, tipo Serranos) | D (semicircolari verso fuori, tipo Quart) | round | square.
    Corpo centrale con arco (arch_w, arch_h), merli su torri e corpo."""
    B, F = Builder(ctx), ctx.F
    tp = ctx.g('tower_plan', 'polygon'); r = float(ctx.g('tower_r', 8.0)); h = float(ctx.g('h', 30.0))
    bh = float(ctx.g('body_h', h - 4)); gap = float(ctx.g('gap', 14.0)); dep = float(ctx.g('depth', 16.0))
    aw, ah = float(ctx.g('arch_w', 6.0)), float(ctx.g('arch_h', 11.0)); c = ctx.g('c', 'limestone'); mer = ctx.g('merlons', True)
    shapes = []
    for sg in (-1, 1):
        s = sg * (gap / 2 + r * 0.85)
        if tp == 'D':
            g_ = F.rect(s - r, s + r, -dep / 2, dep / 2 - r * 0.2).union(F.ngon(s, dep / 2 - r * 0.2, r, 20))
        elif tp == 'round':
            g_ = F.ngon(s, dep * 0.12, r, 16)
        elif tp == 'square':
            g_ = F.rect(s - r, s + r, -dep / 2, dep / 2 + 2)
        else:
            g_ = F.ngon(s, dep / 2, r, 6, rot=90).union(F.rect(s - r * 0.86, s + r * 0.86, -dep / 2, dep / 2))
        shapes.append(g_)
        B.prism(g_.buffer(0.8, join_style=2), 0, 2.5, 'stone2', f=0.0, g='found')
        B.prism(g_, 2.5, h * 0.5, c, A_STONE, 0.15, 'towers')
        B.prism(g_, h * 0.5, h, c, A_STONE, 0.4, 'towers')
        B.prism(g_.buffer(0.6, join_style=2), h, h + 1.0, c, A_STONE, 0.75, 'top')
        if mer: B.merlons(g_.buffer(0.6, join_style=2), h + 1.0, c, f=0.9, maxn=22)
        for zz in (h * 0.45, h * 0.75):   # feritoie verso fuori
            ox, oy = F.at(s, (dep / 2 if tp in ('polygon', 'D') else dep * 0.12) + r * (0.8 if tp != 'D' else 0.8) - 0.1)
            B.prism(npoly(ox, oy, 0.55, 4, math.radians(F.ang) + math.pi / 4), zz, zz + 3.0, 'dark', A_STONE, 0.45, 'towers', simp=0)
    # corpo centrale: due spalle + architrave sopra l'arco
    gi = gap / 2 + 0.1
    B.prism(F.rect(-gi, -aw / 2, -dep / 2, dep / 2), 0, bh, c, A_STONE, 0.3, 'body', simp=0)
    B.prism(F.rect(aw / 2, gi, -dep / 2, dep / 2), 0, bh, c, A_STONE, 0.3, 'body', simp=0)
    B.prism(F.rect(-aw / 2, aw / 2, -dep / 2, dep / 2), ah, bh, c, A_STONE, 0.5, 'body', simp=0)
    for k in range(4):   # arco a sesto acuto: conci a gradini sotto l'architrave
        a0 = math.pi * k / 4; a1 = math.pi * (k + 1) / 4
        sx0, sx1 = -aw / 2 * math.cos(a0), -aw / 2 * math.cos(a1)
        zz = ah - aw / 2 * (1 - math.sin((a0 + a1) / 2)) * 0.9
        if sx1 - sx0 > 0.2: B.prism(F.rect(sx0, sx1, -dep / 2, dep / 2), zz, ah, c, A_STONE, 0.52, 'body', simp=0)
        if sx1 - sx0 > 0.2: B.prism(F.rect(-sx1, -sx0, -dep / 2, dep / 2), zz, ah, c, A_STONE, 0.52, 'body', simp=0)
    B.prism(F.rect(-gi, gi, -dep / 2 - 0.5, dep / 2 + 0.5), bh, bh + 1.0, c, A_STONE, 0.78, 'top', simp=0)
    if mer: B.merlons(F.rect(-gi, gi, -dep / 2 - 0.5, dep / 2 + 0.5), bh + 1.0, c, f=0.9, maxn=16)
    B.beam(F.p3(-aw / 2 - 0.3, dep / 2 + 0.3, ah * 0.5), F.p3(aw / 2 + 0.3, dep / 2 + 0.3, ah * 0.5), 0.1, ah, 'dark', A_STONE, 0.55, 'body')   # porta scura
    return B


def _line_of(ctx, default_len=120.0):
    if ctx.line and len(ctx.line) >= 2: return LineString(ctx.line)
    F = ctx.F; Ln = float(ctx.g('length', default_len))
    return LineString([F.at(-Ln / 2, 0), F.at(Ln / 2, 0)])


@preset('wall_segment', 'walls')
def wall_segment(ctx):
    """Tratto di mura lungo una linea (story: "line": [[lat,lon],...], oppure at+ang+length): cortina a tratti di
    chunk_m (costruzione progressiva lungo la linea), cammino di ronda (parapetto esterno), torri ogni towers_every_m
    (tower: square | round) con beccatelli e copertura (tower_top: crenel | pyramid | flat)."""
    B = Builder(ctx)
    ln = _line_of(ctx); Ltot = ln.length
    h, w = float(ctx.g('h', 10.0)), float(ctx.g('w', 3.5)); c = ctx.g('c', 'stone')
    ev = float(ctx.g('towers_every_m', 45.0)); tw = float(ctx.g('tower_w', 8.0)); th = float(ctx.g('tower_h', h + 5))
    tt = ctx.g('tower', 'square'); ttop = ctx.g('tower_top', 'crenel'); chunk = float(ctx.g('chunk_m', 40.0))
    n = max(1, int(round(Ltot / chunk)))
    for i in range(n):
        seg = substring(ln, Ltot * i / n, Ltot * (i + 1) / n)
        f = 0.05 + 0.75 * (i + 0.5) / n
        B.prism(seg.buffer(w / 2, cap_style=2, join_style=2), 0, h, c, A_STONE, f, 'wall')
        par = seg.parallel_offset(w / 2 - 0.35, 'left') if seg.length > 1 else None
        if par is not None and not par.is_empty and par.length > 1:
            B.prism(par.buffer(0.35, cap_style=2), h, h + 1.3, c, A_STONE, f + 0.02, 'wall')
    if ev > 0:
        k = 0
        for i in range(int(Ltot // ev) + 1):
            p = ln.interpolate(min(Ltot, i * ev)); s = min(Ltot, i * ev)
            a = substring(ln, max(0, s - 1), min(Ltot, s + 1)); (xa, ya), (xb, yb) = a.coords[0], a.coords[-1]
            ang = math.degrees(math.atan2(yb - ya, xb - xa)); Ft = Frame(p.x, p.y, ang)
            f = 0.08 + 0.75 * s / max(Ltot, 1)
            if tt == 'round':
                B.cyl(p.x, p.y, tw / 2, 0, th, c, A_STONE, f, 'towers', seg=12)
                _tower_top(B, Ft, 0, 0, tw, th, ttop, c, col(ctx.roof()), f + 0.1, plan='round', g='towers')
            else:
                sq = Ft.rect(-tw / 2, tw / 2, -tw / 2 + w / 2, tw / 2 + w / 2 + 1.5)
                B.prism(sq, 0, th, c, A_STONE, f, 'towers', simp=0)
                Fs = Frame(*Ft.at(0, w / 2 + 0.75), ang)
                _tower_top(B, Fs, 0, 0, tw, th, ttop, c, col(ctx.roof()), f + 0.1, g='towers')
            k += 1
    return B


@preset('bridge_arches', 'bridge')
def bridge_arches(ctx):
    """Ponte ad archi lungo una linea ("line" di 2+ punti o at+ang+length): pile con rostri (dal fondo, zbase<0),
    archi ribassati a conci (fette), impalcato, parapetti. n = numero di archi (default lunghezza/span_m)."""
    B = Builder(ctx)
    ln = _line_of(ctx, 140.0); Lt = ln.length
    w = float(ctx.g('w', 12.0)); Z = float(ctx.g('deck_z', 9.0)); zw = float(ctx.g('z_water', -2.0))
    n = int(ctx.g('n', max(1, round(Lt / float(ctx.g('span_m', 22.0)))))); pw = float(ctx.g('pier_w', 4.0))
    c = ctx.g('c', 'stone'); k = int(ctx.g('voussoirs', 7)); dt = float(ctx.g('deck_t', 1.6))
    sp = Lt / n; rise = float(ctx.g('rise', min(sp / 2 - pw / 2, Z - dt - 1.2) * 0.85))
    spring = Z - dt - rise

    def frame_at(s):
        a = substring(ln, max(0, s - 0.5), min(Lt, s + 0.5)); (xa, ya), (xb, yb) = a.coords[0], a.coords[-1]
        p = ln.interpolate(s); return Frame(p.x, p.y, math.degrees(math.atan2(yb - ya, xb - xa)))

    # spalle
    for s, sg in ((0.0, 1), (Lt, -1)):
        Fs = frame_at(min(max(s, 0.5), Lt - 0.5))
        B.prism(Fs.rect(-pw if sg < 0 else 0, pw if sg > 0 else 0, -w / 2 - 0.5, w / 2 + 0.5), zw, Z, c, A_STONE, 0.0 if sg > 0 else 0.05, 'piers')
    # pile con rostri (esagono allungato di traverso)
    for i in range(1, n):
        s = sp * i; Fp = frame_at(s)
        q = Fp.poly([(-pw / 2, -w / 2), (0, -w / 2 - pw * 0.9), (pw / 2, -w / 2), (pw / 2, w / 2), (0, w / 2 + pw * 0.9), (-pw / 2, w / 2)])
        B.prism(q, zw, spring + 0.3, c, A_STONE, 0.05 + 0.4 * i / n, 'piers')
        B.prism(q.buffer(0.3, join_style=2), spring + 0.3, spring + 0.9, 'stone2', A_STONE, 0.08 + 0.4 * i / n, 'piers')
    # archi: fette da intradosso (curva) a impalcato
    for j in range(n):
        s0 = sp * j + (pw / 2 if j > 0 else pw); s1 = sp * (j + 1) - (pw / 2 if j < n - 1 else pw); L_ = s1 - s0
        for m in range(k):
            a0, a1 = s0 + L_ * m / k, s0 + L_ * (m + 1) / k; xm = ((a0 + a1) / 2 - s0) / L_ * 2 - 1
            zi = spring + rise * math.sqrt(max(0.0, 1 - xm * xm))
            seg = substring(ln, a0, a1)
            B.prism(seg.buffer(w / 2, cap_style=2, join_style=2), zi, Z - dt + 0.01, c, A_STONE, 0.4 + 0.4 * j / n, 'arches')
        # spalletta sopra le pile
    for j in range(n + 1):
        s = sp * j; a0, a1 = max(0, s - pw / 2 - 0.01), min(Lt, s + pw / 2 + 0.01)
        if a1 - a0 > 0.2: B.prism(substring(ln, a0, a1).buffer(w / 2, cap_style=2, join_style=2), spring + 0.9 if 0 < j < n else zw, Z - dt + 0.01, c, A_STONE, 0.42 + 0.4 * j / max(n, 1), 'arches')
    # impalcato e parapetti
    B.prism(ln.buffer(w / 2 + 0.3, cap_style=2, join_style=2), Z - dt, Z, ctx.g('deck_c', 'stone2'), A_STONE, 0.86, 'deck', top=ctx.g('road_c', '#b9b2a4'))
    for side in ('left', 'right'):
        e = ln.parallel_offset(w / 2, side)
        if not e.is_empty: B.prism(e.buffer(0.35, cap_style=2, join_style=2), Z, Z + 1.1, c, A_STONE, 0.93, 'deck')
    return B


@preset('palace_courtyard', 'palace')
def palace_courtyard(ctx):
    """Palazzo a corte: quattro ali (wing_w) attorno a un cortile, tetti a padiglione, portale centrale sul lato -v,
    torri d'angolo opzionali (corner_towers). Con footprint: ali nel riferimento dell'impronta, ritagliate su di essa."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(70.0, 50.0); ww = float(ctx.g('wing_w', min(14.0, W * 0.3))); h = float(ctx.g('h', 16.0))
    c, rc = ctx.g('c', 'plaster'), col(ctx.roof())
    clip = ctx.fp.buffer(1.0) if ctx.fp is not None else None
    wings = [F.rect(-L / 2, L / 2, -W / 2, -W / 2 + ww), F.rect(-L / 2, L / 2, W / 2 - ww, W / 2),
             F.rect(-L / 2, -L / 2 + ww, -W / 2 + ww, W / 2 - ww), F.rect(L / 2 - ww, L / 2, -W / 2 + ww, W / 2 - ww)]
    B.prism(F.rect(-L / 2, L / 2, -W / 2, W / 2).buffer(0.6, join_style=2), 0, 1.2, 'stone2', f=0.0, g='found', simp=0)
    for i, q in enumerate(wings):
        if clip is not None: q = q.intersection(clip)
        B.prism(q, 1.2, h, c, A_WIN, 0.15 + 0.12 * i, 'body')
        B.prism(q.buffer(0.4, join_style=2), h, h + 0.6, 'stone', A_STONE, 0.2 + 0.12 * i, 'body')
        for qq in _polys(q): B.hip(qq.buffer(0.4, join_style=2), h + 0.6, min(ww, 14) * 0.38, rc, 0.7 + 0.04 * i)
    if not ctx.windows:   # palazzo antico: poche finestre scure al piano nobile (lati lunghi) invece della griglia
        for sg in (-1, 1):
            nwin = max(2, min(7, int(L / 9)))
            for j in range(nwin):
                sx_ = -L / 2 + L * (j + 0.5) / nwin
                B.prism(F.rect(sx_ - 1.0, sx_ + 1.0, sg * W / 2 - 0.25, sg * W / 2 + 0.25), h * 0.5, h * 0.5 + 3.2, 'dark', A_STONE, 0.3, 'body', simp=0)
        for sg in (-1, 1):
            nwin = max(2, min(5, int(W / 9)))
            for j in range(nwin):
                tx_ = -W / 2 + W * (j + 0.5) / nwin
                B.prism(F.rect(sg * L / 2 - 0.25, sg * L / 2 + 0.25, tx_ - 1.0, tx_ + 1.0), h * 0.5, h * 0.5 + 3.2, 'dark', A_STONE, 0.3, 'body', simp=0)
    pw = min(L * 0.22, 16.0)   # portale
    B.prism(F.rect(-pw / 2, pw / 2, -W / 2 - 1.2, -W / 2 + ww), 0, h + 4, ctx.g('portal_c', 'stone'), A_STONE, 0.6, 'portal', simp=0)
    B.gable(F, -pw / 2, pw / 2, -W / 2 - 1.2, -W / 2 + ww, h + 4, 2.6, ctx.g('portal_c', 'stone'), rc, 0.8, 'roof', along='v')
    if ctx.g('corner_towers', False):
        tw = ww * 1.1
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx_, cy_ = sx * (L / 2 - tw / 2 + 1), sy * (W / 2 - tw / 2 + 1)
                B.prism(F.rect(cx_ - tw / 2, cx_ + tw / 2, cy_ - tw / 2, cy_ + tw / 2), 0, h + 7, c, A_WIN, 0.65, 'towers', simp=0)
                _tower_top(B, F, cx_, cy_, tw, h + 7, ctx.g('tower_top', 'pyramid'), c, rc, 0.9)
    if ctx.g('fountain', True):
        x, y = F.cx, F.cy; B.cyl(x, y, min(L, W) * 0.08, 0, 0.8, 'stone', A_STONE, 0.9, 'court', seg=12)
    return B


@preset('hall_market', 'market')
def hall_market(ctx):
    """Mercato coperto: corpo in mattone/ferro con finestre, falde vetrate a botte (n_vaults colmi lungo v),
    cupola principale con lanterna e cupolette agli angoli (domes)."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(90.0, 60.0); h = float(ctx.g('h', 11.0)); nv = int(ctx.g('n_vaults', 5))
    c, gc, dc = ctx.g('c', 'ochre'), ctx.g('glass_c', 'glass'), col(ctx.g('dome_c', ctx.style['dome']))
    body = ctx.fp if ctx.fp is not None else F.rect(-L / 2, L / 2, -W / 2, W / 2)
    B.prism(body.buffer(0.5, join_style=2), 0, 1.0, 'stone2', f=0.0, g='found')
    B.prism(body, 1.0, h, c, A_WIN, 0.2, 'body')
    for i in range(nv):   # falde vetrate: colmo lungo v, una dietro l'altra lungo u
        s0, s1 = -L / 2 + L * i / nv, -L / 2 + L * (i + 1) / nv
        B.gable(F, s0 + 0.4, s1 - 0.4, -W / 2 + 1.5, W / 2 - 1.5, h, (s1 - s0) * 0.3, c, gc, 0.4 + 0.05 * i, 'roof', a=A_GLASS, along='u')
    rd = min(L, W) * float(ctx.g('dome_k', 0.16))
    x, y = F.cx, F.cy; zr = h + (L / nv) * 0.3
    B.cyl(x, y, rd, h, zr + rd * 0.5, c, A_WIN, 0.7, 'dome', seg=16)
    B.dome(x, y, rd, zr + rd * 0.5, rd * 0.9, dc, f=0.8, g='dome')
    zt = zr + rd * 1.4
    B.cyl(x, y, rd * 0.22, zt - 0.4, zt + rd * 0.35, gc, A_GLASS, 0.88, 'dome', seg=8)
    B.cone(x, y, rd * 0.28, 0.05, zt + rd * 0.35, zt + rd * 0.85, dc, f=0.92, g='dome', seg=8)
    if ctx.g('domes', True):
        for sx in (-1, 1):
            for sy in (-1, 1):
                px, py = F.at(sx * (L / 2 - 4), sy * (W / 2 - 4))
                B.cyl(px, py, 3.6, h, h + 4.0, c, A_WIN, 0.75, 'domes', seg=12)
                B.dome(px, py, 3.6, h + 4.0, 3.4, dc, f=0.85, g='domes')
                B.cone(px, py, 0.5, 0.05, h + 7.2, h + 9.5, 'gold', f=0.9, g='domes', seg=6)
    return B


def _vault(B, F, s0, s1, t0, t1, z0, rise, c, top, a, f, g, k=6):
    """Volta a botte con asse lungo v (profilo in s): k wedge a falde con curvatura circolare."""
    S = s1 - s0; prev = z0
    for i in range(k):
        a0, a1 = s0 + S * i / k, s0 + S * (i + 1) / k
        x0, x1 = (a0 - s0) / S * 2 - 1, (a1 - s0) / S * 2 - 1
        z_0 = z0 + rise * math.sqrt(max(0, 1 - x0 * x0)); z_1 = z0 + rise * math.sqrt(max(0, 1 - x1 * x1))
        za, zb = (z_0, z_1) if z_1 >= z_0 else (z_1, z_0)
        ax = F.u if z_1 >= z_0 else (-F.u[0], -F.u[1])
        if abs(z_1 - z_0) < 0.05: B.prism(F.rect(a0, a1, t0, t1), z0, max(z_0, z_1), c, a, f, g, top=top, simp=0)
        else: B.wedge(F.rect(a0, a1, t0, t1), z0, za, zb, ax, c, top, a, f, g)


@preset('station', 'train_station')
def station(ctx):
    """Stazione di testa: corpo di facciata sul lato -v (finestre, padiglione centrale, torrette d'angolo con cupolini),
    tettoia dei binari dietro a botte vetrata in ferro (shed: true)."""
    B, F = Builder(ctx), ctx.F
    L, D = ctx.dims(110.0, 120.0); fd = float(ctx.g('facade_d', 16.0)); h = float(ctx.g('h', 17.0))
    c, rc = ctx.g('c', 'cream'), col(ctx.roof()); ac = ctx.g('accent_c', 'brick'); dc = col(ctx.g('dome_c', ctx.style['dome']))
    t0 = -D / 2
    B.prism(F.rect(-L / 2, L / 2, t0, t0 + fd).buffer(0.5, join_style=2), 0, 1.0, 'stone2', f=0.0, g='found', simp=0)
    B.prism(F.rect(-L / 2, L / 2, t0, t0 + fd), 1.0, h, c, A_WIN, 0.2, 'body', simp=0)
    B.prism(F.rect(-L / 2, L / 2, t0 - 0.3, t0 + fd + 0.3), h, h + 0.8, ac, A_STONE, 0.3, 'body', simp=0)
    B.hip(F.rect(-L / 2, L / 2, t0, t0 + fd), h + 0.8, fd * 0.3, rc, 0.5)
    pw = L * 0.22   # padiglione centrale
    B.prism(F.rect(-pw / 2, pw / 2, t0 - 1.5, t0 + fd), 0, h + 7, ac, A_WIN, 0.4, 'body', simp=0)
    B.hip(F.rect(-pw / 2, pw / 2, t0 - 1.5, t0 + fd), h + 7, 4.5, rc, 0.6)
    tw = 9.0
    for sg in (-1, 1):
        s = sg * (L / 2 - tw / 2)
        B.prism(F.rect(s - tw / 2, s + tw / 2, t0 - 1, t0 - 1 + tw), 0, h + 9, ac, A_WIN, 0.45, 'towers', simp=0)
        _tower_top(B, F, s, t0 - 1 + tw / 2, tw, h + 9, ctx.g('tower_top', 'dome'), ac, dc, 0.75, g='towers')
    if ctx.g('shed', True):
        ss = L * 0.42; sd0, sd1 = t0 + fd, D / 2
        B.prism(F.rect(-ss, -ss + 2, sd0, sd1), 0, 9, ac, A_WIN, 0.55, 'shed', simp=0)
        B.prism(F.rect(ss - 2, ss, sd0, sd1), 0, 9, ac, A_WIN, 0.55, 'shed', simp=0)
        _vault(B, F, -ss, ss, sd0, sd1, 9, ss * 0.42, ctx.g('shed_c', 'steel'), ctx.g('shed_glass', 'glass'), A_GLASS, 0.7, 'shed', k=8)
    return B


@preset('bullring', 'arena', 'amphitheatre')
def bullring(ctx):
    """Arena/plaza de toros/anfiteatro: anello esterno ad arcate (finestre), gradoni interni a tre livelli, barriera,
    ruedo di sabbia. plan: round (r_out) | ellipse (a_out, b_out). Roman: style='roman' (pietra, piu' alto)."""
    B, F = Builder(ctx), ctx.F
    roman = ctx.g('style') == 'roman'
    if ctx.g('plan', 'ellipse' if roman else 'round') == 'ellipse':
        A, Bb = float(ctx.g('a_out', 94.0 if roman else 60.0)), float(ctx.g('b_out', 78.0 if roman else 48.0))
    else:
        r = float(ctx.g('r_out', (min(F.L, F.W) / 2) if ctx.fp is not None else 52.0)); A = Bb = r
    ra = float(ctx.g('arena_k', 0.5))   # raggio del ruedo / raggio esterno
    h = float(ctx.g('h', 48.0 if roman else 17.0)); c = ctx.g('c', 'limestone' if roman else 'cream'); tc = ctx.g('tier_c', 'stone' if roman else 'plaster')
    n = int(ctx.g('n', 32)); wr = float(ctx.g('ring_w', 7.0))
    aA, aB = A * ra, Bb * ra
    B.prism(F.ell(0, 0, aA + 2, aB + 2, 32), 0, 0.25, ctx.g('arena_c', 'arena'), A_STONE, 0.0, 'found', simp=0)
    B.sectors(F, A, Bb, A - wr, Bb - wr, 0, h, c, A_WIN, 0.3, 'ring', n, top=ctx.g('ring_top', ctx.roof()), fstep=0.55)
    ri = [(A - wr, Bb - wr)]
    steps = int(ctx.g('tiers', 3))
    for k in range(steps):   # gradoni: piu' alti verso l'esterno
        o = ri[-1]; t = (k + 1) / steps
        inn = (aA + 2 + (A - wr - aA - 2) * (1 - t), aB + 2 + (Bb - wr - aB - 2) * (1 - t))
        zt = (h - 2) * (steps - k) / (steps + 0.6)
        B.sectors(F, o[0], o[1], inn[0], inn[1], 0, zt, tc, A_STONE, 0.45 + 0.1 * k, 'tiers', n, top=tc)
        ri.append(inn)
    B.sectors(F, aA + 2, aB + 2, aA + 1.2, aB + 1.2, 0, 1.6, ctx.g('barrier_c', 'red'), A_STONE, 0.8, 'barrier', 24)
    return B


@preset('stadium')
def stadium(ctx):
    """Stadio: tribune inclinate a settori (wedge radiali, basse verso il campo), anello esterno, pensilina (roof),
    campo verde rettangolare. a_out/b_out semiassi esterni."""
    B, F = Builder(ctx), ctx.F
    A0, B0 = (F.L / 2, F.W / 2) if ctx.fp is not None else (115.0, 88.0)
    A, Bb = float(ctx.g('a_out', A0)), float(ctx.g('b_out', B0)); h = float(ctx.g('h', 26.0))
    fa, fb = float(ctx.g('a_field', A * 0.58)), float(ctx.g('b_field', Bb * 0.5)); n = int(ctx.g('n', 32))
    sc_, wc = ctx.g('seat_c', 'seat'), ctx.g('c', 'concrete')
    B.prism(F.ell(0, 0, fa + 3, fb + 3, 32), 0, 0.2, 'grass', A_STONE, 0.0, 'found', simp=0)
    B.prism(F.rect(-fa * 0.82, fa * 0.82, -fb * 0.62, fb * 0.62), 0.2, 0.3, '#5fa83c', A_STONE, 0.02, 'found', simp=0)
    for i in range(n):
        t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n; tm = (t0 + t1) / 2
        q = F.poly([((A - 3) * math.cos(t0), (Bb - 3) * math.sin(t0)), ((A - 3) * math.cos(t1), (Bb - 3) * math.sin(t1)),
                    ((fa + 3) * math.cos(t1), (fb + 3) * math.sin(t1)), ((fa + 3) * math.cos(t0), (fb + 3) * math.sin(t0))])
        ax = F.dirv(math.cos(tm) / A, math.sin(tm) / Bb)
        B.wedge(q, 0, 2.0, h - 2, ax, wc, sc_ if i % 2 == 0 else ctx.g('seat_c2', sc_), A_STONE, 0.2 + 0.4 * i / n, 'stands')
    B.sectors(F, A, Bb, A - 3, Bb - 3, 0, h + 6, wc, A_WIN, 0.15, 'ring', n, fstep=0.4)
    if ctx.g('roof', True):
        rd = float(ctx.g('roof_d', (A - fa) * 0.55))
        B.sectors(F, A + 1, Bb + 1, A - rd, Bb - rd, h + 6, h + 7.2, ctx.g('roof_c', 'white'), A_STONE, 0.85, 'roof', n, fstep=0.1)
    return B


@preset('skyscraper', 'tower_glass')
def skyscraper(ctx):
    """Grattacielo: basamento (finestre), fusto di vetro in tre tronchi con arretramenti (setbacks [[frac_h, scala]]),
    coronamento (crown: flat | spire | mast | pyramid). plan: rect | round."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(32.0, 32.0); h = float(ctx.g('h', 150.0)); ph = float(ctx.g('podium_h', 12.0))
    gc, pc = ctx.g('c', 'glass'), ctx.g('podium_c', 'concrete'); plan = ctx.g('plan', 'rect')
    sb = ctx.g('setbacks', [[0.72, 0.82]])
    base = ctx.fp if (ctx.fp is not None and plan == 'rect') else (F.ell(0, 0, L / 2, W / 2, 20) if plan == 'round' else F.rect(-L / 2, L / 2, -W / 2, W / 2))
    B.prism(base.buffer(3, join_style=2), 0, ph, pc, A_WIN, 0.05, 'podium')
    levels = [(0.0, 1.0)] + [tuple(x) for x in sb]
    zs = [ph] + [ph + (h - ph) * fr for fr, _ in levels[1:]] + [h]
    ctr = base.centroid
    for i, (_, k) in enumerate(levels):
        g_ = affinity.scale(base, k, k, origin=ctr)
        z0, z1 = zs[i], zs[i + 1]; m = 3 if i == 0 else 1
        for j in range(m):
            B.prism(g_, z0 + (z1 - z0) * j / m, z0 + (z1 - z0) * (j + 1) / m, gc, A_GLASS, 0.15 + 0.6 * (i * 3 + j) / (len(levels) * 3 + 1), 'shaft', top=ctx.g('top_c', 'steel'))
    crown = ctx.g('crown', 'flat'); x, y = ctr.x, ctr.y; kk = levels[-1][1]; rr = min(L, W) / 2 * kk
    B.prism(affinity.scale(base, kk * 0.9, kk * 0.9, origin=ctr), h, h + 4, ctx.g('top_c', 'steel'), A_STONE, 0.85, 'crown')
    if crown == 'spire': B.cone(x, y, rr * 0.35, 0.1, h + 4, h + 4 + h * 0.25, 'steel', f=0.95, g='crown', seg=8)
    elif crown == 'mast': B.cyl(x, y, 0.8, h + 4, h + 4 + h * 0.18, 'steel', f=0.95, g='crown', seg=6)
    elif crown == 'pyramid': B.hip(affinity.scale(base, kk * 0.9, kk * 0.9, origin=ctr), h + 4, rr * 1.2, 'steel', 0.95, 'crown')
    return B


def _arc_beams(B, F, s, half, H, w, hh, c, f, g, k=8, z0=0.0, along='v'):
    """Arco (semiellisse) di travi nel piano s=cost (along='v': attraverso) da t=-half a +half, altezza H."""
    pts = []
    for i in range(k + 1):
        th = math.pi * i / k
        tt = -half * math.cos(th); zz = z0 + H * math.sin(th)
        pts.append(F.p3(s, tt, zz) if along == 'v' else F.p3(tt, s, zz))
    for p0, p1 in zip(pts, pts[1:]): B.beam(p0, p1, w, hh, c, A_STONE, f, g)


@preset('modern_shell', 'calatrava')
def modern_shell(ctx):
    """Architettura organica bianca (stile Calatrava) da primitive: shape =
    eye (Hemisfèric: guscio a costole su base ellittica vetrata + 'pupilla'), ribs (Museu de les Ciències: costole ad A
    ripetute su corpo vetrato), helmet (Palau de les Arts: corpo a lente + lama curva sopra), arches (Umbracle: serie di
    archi), dome (cupola vetrata su anello). L lungo u, W attraverso, h altezza."""
    B, F = Builder(ctx), ctx.F
    shape = ctx.g('shape', 'eye'); wc, gc = ctx.g('c', 'calatrava'), ctx.g('glass_c', 'glass')
    if shape == 'eye':
        L, W = ctx.dims(110.0, 55.0); H = float(ctx.g('h', 24.0)); nr = int(ctx.g('ribs', 11))
        B.prism(F.ell(0, 0, L / 2 + 14, W / 2 + 14, 40), -0.2, 0.25, ctx.g('pool_c', 'water'), A_STONE, 0.0, 'found', simp=0)
        lay = 5
        for i in range(lay):   # guscio: lente a strati sottili (vetro azzurro)
            z0 = H * i / lay; z1 = H * (i + 1) / lay; k = math.sqrt(max(0.0, 1 - (z0 / H) ** 2))
            B.prism(F.ell(0, 0, L / 2 * k * 0.98, W / 2 * k * 0.98, 32), z0, z1, gc, A_GLASS, 0.2 + 0.08 * i, 'shell', simp=0, top=gc)
        for j in range(nr):   # costole bianche trasversali
            s = -L / 2 + L * (j + 0.5) / nr; k = math.sqrt(max(0.0, 1 - (2 * s / L) ** 2))
            _arc_beams(B, F, s, W / 2 * k + 0.6, H * k + 0.6, 1.6, 1.8, wc, 0.7 + 0.15 * j / nr, 'ribs', k=8)
        _arc_beams(B, F, 0, L / 2 + 0.8, H + 1.2, 2.2, 1.4, wc, 0.9, 'ribs', k=10, along='u')
        B.dome(F.cx, F.cy, W * 0.14, H * 0.6, W * 0.16, 'white', f=0.95, g='ribs')
        return B
    if shape == 'ribs':
        L, W = ctx.dims(220.0, 40.0); H = float(ctx.g('h', 36.0)); nr = int(ctx.g('ribs', 14))
        B.prism(F.rect(-L / 2, L / 2, -W / 2 + 4, W / 2 - 4), 0, H * 0.8, gc, A_GLASS, 0.2, 'body', simp=0, top=wc)
        B.prism(F.rect(-L / 2 - 2, L / 2 + 2, -W / 2 + 2, W / 2 - 2), H * 0.8, H * 0.86, wc, A_STONE, 0.5, 'body', simp=0)
        for j in range(nr + 1):
            s = -L / 2 + L * j / nr; f = 0.3 + 0.5 * j / nr
            for sg in (-1, 1):   # costole ad albero: gamba inclinata verso l'esterno e ramo sul tetto
                B.beam(F.p3(s, sg * (W / 2 - 3), 0), F.p3(s, sg * (W / 2 + 2), H * 0.55), 1.6, 1.6, wc, A_STONE, f, 'ribs')
                B.beam(F.p3(s, sg * (W / 2 + 2), H * 0.55), F.p3(s, sg * (W / 2 - 4), H), 1.4, 1.4, wc, A_STONE, f + 0.03, 'ribs')
            B.beam(F.p3(s, -(W / 2 - 4), H), F.p3(s, W / 2 - 4, H), 1.2, 1.2, wc, A_STONE, f + 0.05, 'ribs')
        return B
    if shape == 'helmet':
        L, W = ctx.dims(160.0, 80.0); H = float(ctx.g('h', 60.0))
        lay = 6
        for i in range(lay):
            z0 = H * 0.7 * i / lay; z1 = H * 0.7 * (i + 1) / lay; zm = (z0 + z1) / 2 / (H * 0.7)
            k = math.sqrt(max(0.05, 1 - (2 * zm - 0.3) ** 2)) if zm > 0.15 else 0.8 + zm
            B.prism(F.ell(0, 0, L / 2 * k * 0.8, W / 2 * k, 32), z0, z1, wc, A_STONE if i % 2 else A_WIN, 0.1 + 0.08 * i, 'body', simp=0)
        B.prism(F.ell(-L * 0.05, 0, L * 0.32, W * 0.3, 24), 0, H * 0.45, gc, A_GLASS, 0.2, 'body', simp=0)
        pts = []
        for i in range(11):   # lama: arco che parte basso davanti e scavalca il corpo
            th = math.pi * 0.95 * i / 10
            pts.append(F.p3(-L * 0.6 * math.cos(th) + L * 0.05, 0, H * 0.25 + H * 0.75 * math.sin(th) * (1 - 0.15 * i / 10)))
        for j, (p0, p1) in enumerate(zip(pts, pts[1:])): B.beam(p0, p1, W * 0.22, 2.5, wc, A_STONE, 0.75 + 0.02 * j, 'blade')
        return B
    if shape == 'arches':
        L, W = ctx.dims(160.0, 30.0); H = float(ctx.g('h', 18.0)); n = int(ctx.g('ribs', 14))
        B.prism(F.rect(-L / 2, L / 2, -W / 2, W / 2), 0, 0.6, wc, A_STONE, 0.0, 'found', simp=0)
        for j in range(n + 1):
            s = -L / 2 + L * j / n
            _arc_beams(B, F, s, W / 2, H, 0.9, 0.9, wc, 0.2 + 0.7 * j / n, 'ribs', k=8, z0=0.6)
        for sg in (-1, 1): B.beam(F.p3(-L / 2, sg * W * 0.38, H * 0.92), F.p3(L / 2, sg * W * 0.38, H * 0.92), 0.6, 0.6, wc, A_STONE, 0.95, 'ribs')
        return B
    # dome
    L, W = ctx.dims(60.0, 60.0); r = min(L, W) / 2; H = float(ctx.g('h', 10.0))
    B.cyl(F.cx, F.cy, r, 0, H, wc, A_WIN, 0.2, 'body', seg=24)
    B.dome(F.cx, F.cy, r, H, r * 0.6, gc, A_GLASS, 0.6, 'dome')
    return B


@preset('park_structure', 'park')
def park_structure(ctx):
    """Arredo di parco: kind = kiosk (chiosco della musica) | greenhouse (serra) | fountain | obelisk | statue |
    wheel (ruota panoramica) | pagoda | pergola."""
    B, F = Builder(ctx), ctx.F
    kind = ctx.g('kind', 'kiosk'); x, y = F.cx, F.cy; c = ctx.g('c', None)
    if kind == 'kiosk':
        r = float(ctx.g('r', 7.0))
        B.prism(npoly(x, y, r + 0.6, 8), 0, 1.4, 'stone', A_STONE, 0.0, 'found', simp=0)
        for i in range(8):
            a = 2 * math.pi * i / 8; B.cyl(x + r * math.cos(a), y + r * math.sin(a), 0.3, 1.4, 6.0, col(c, 'white'), A_STONE, 0.3, 'body', seg=6)
        B.cone(x, y, r + 1.0, 0.3, 6.0, 9.0, col(ctx.g('roof_c', 'greentile')), f=0.7, seg=8)
        B.cone(x, y, 0.4, 0.05, 9.0, 10.5, 'gold', f=0.85, seg=6)
    elif kind == 'greenhouse':
        L, W = ctx.dims(40.0, 16.0); h = float(ctx.g('h', 6.0))
        B.prism(F.rect(-L / 2, L / 2, -W / 2, W / 2), 0, 0.8, 'stone', A_STONE, 0.0, 'found', simp=0)
        B.prism(F.rect(-L / 2, L / 2, -W / 2, W / 2), 0.8, h, 'glass', A_GLASS, 0.3, 'body', simp=0, top='glass')
        B.gable(F, -L / 2, L / 2, -W / 2, W / 2, h, W * 0.35, 'white', 'glass', 0.6, a=A_GLASS)
        B.prism(F.ngon(L / 2, 0, W * 0.42, 12, 0), 0.8, h + W * 0.25, 'glass', A_GLASS, 0.5, 'body', simp=0)
        B.dome(*F.at(L / 2, 0), W * 0.42, h + W * 0.25, W * 0.4, 'glass', A_GLASS, 0.8)
    elif kind == 'fountain':
        r = float(ctx.g('r', 9.0))
        B.cyl(x, y, r, 0, 0.9, 'stone', A_STONE, 0.0, 'found', seg=20)
        B.cyl(x, y, r - 0.7, 0.9, 0.95, 'water', A_STONE, 0.3, 'body', seg=20)
        B.cyl(x, y, 1.0, 0.9, 3.5, 'stone', A_STONE, 0.5, 'body', seg=8)
        B.cone(x, y, 1.0, 3.2, 3.5, 4.3, 'stone', f=0.7, seg=12)
        B.cone(x, y, 0.4, 0.05, 4.3, 7.0, 'water', f=0.9, seg=8)
    elif kind == 'obelisk':
        h = float(ctx.g('h', 24.0))
        B.prism(F.rect(-3, 3, -3, 3), 0, 3, 'stone2', A_STONE, 0.0, 'found', simp=0)
        B.prism(F.rect(-1.6, 1.6, -1.6, 1.6), 3, h * 0.92, col(c, 'granite'), A_STONE, 0.4, 'body', simp=0)
        B.hip(F.rect(-1.6, 1.6, -1.6, 1.6), h * 0.92, h * 0.08 + 1.5, 'gold', 0.9)
    elif kind == 'statue':
        h = float(ctx.g('h', 12.0))
        B.prism(F.rect(-2.5, 2.5, -2.5, 2.5), 0, h * 0.55, 'stone', A_STONE, 0.0, 'found', simp=0)
        B.cyl(x, y, 1.0, h * 0.55, h * 0.9, col(c, 'copper'), A_STONE, 0.6, 'body', seg=8)
        B.dome(x, y, 0.7, h * 0.9, 1.0, col(c, 'copper'), f=0.8, g='body')
    elif kind == 'wheel':
        R = float(ctx.g('r', 20.0)); zc = R + 3; n = 16
        pts = [F.p3(R * math.cos(2 * math.pi * i / n), 0, zc + R * math.sin(2 * math.pi * i / n)) for i in range(n)]
        for sg in (-1, 1):   # gambe ad A
            B.beam(F.p3(-R * 0.45, sg * 3, 0), F.p3(0, sg * 1.2, zc), 1.2, 1.2, 'steel', A_STONE, 0.1, 'legs')
            B.beam(F.p3(R * 0.45, sg * 3, 0), F.p3(0, sg * 1.2, zc), 1.2, 1.2, 'steel', A_STONE, 0.15, 'legs')
        for i in range(n):
            fz = 0.4 + 0.4 * (max(pts[i][2], pts[(i + 1) % n][2]) - (zc - R)) / (2 * R)   # il cerchio si chiude dall'alto
            B.beam(pts[i], pts[(i + 1) % n], 0.9, 0.9, col(c, 'white'), A_STONE, fz, 'rim')
            if i % 2 == 0: B.beam(F.p3(0, 0, zc), pts[i], 0.3, 0.3, 'steel', A_STONE, 0.4, 'rim', noshadow=True)
            if i % 2 == 0: B.prism(npoly(pts[i][0], pts[i][1], 1.3, 4, math.radians(F.ang) + math.pi / 4), pts[i][2] - 2.4, pts[i][2] - 0.6, ['red', 'ochre', 'bluetile', 'greentile'][i // 2 % 4], A_WIN, 0.85, 'cabins', simp=0)
    elif kind == 'pagoda':
        for k in range(4):
            s_ = 6.5 - 1.2 * k
            B.prism(F.rect(-s_ * 0.7, s_ * 0.7, -s_ * 0.7, s_ * 0.7), 4.5 * k, 4.5 * k + 3.2, 'cream', A_STONE, 0.1 + 0.2 * k, 'body', simp=0)
            B.hip(F.rect(-s_, s_, -s_, s_), 4.5 * k + 3.2, 1.3 + (2.0 if k == 3 else 0), 'red', 0.2 + 0.2 * k, 'roof')
    else:   # pergola
        L, W = ctx.dims(30.0, 8.0)
        for i in range(7):
            s = -L / 2 + L * i / 6
            for sg in (-1, 1): B.cyl(*F.at(s, sg * W / 2), 0.25, 0, 3.2, 'white', A_STONE, 0.2 + 0.1 * i, 'body', seg=6)
            B.beam(F.p3(s, -W / 2 - 0.5, 3.3), F.p3(s, W / 2 + 0.5, 3.3), 0.3, 0.3, 'wood', A_STONE, 0.5 + 0.05 * i, 'roof')
        for sg in (-1, 1): B.beam(F.p3(-L / 2, sg * W / 2, 3.5), F.p3(L / 2, sg * W / 2, 3.5), 0.3, 0.3, 'wood', A_STONE, 0.9, 'roof')
    return B


@preset('generic_footprint', 'footprint', 'building')
def generic_footprint(ctx):
    """Estrusione dell'impronta (catasto o w x l) all'altezza h (default: h del catasto), tetto
    roof = flat | parapet | gable (due falde lungo l'asse lungo) | hip | dome."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(30.0, 18.0)
    g_ = ctx.fp if ctx.fp is not None else F.rect(-L / 2, L / 2, -W / 2, W / 2)
    h = float(ctx.g('h', ctx.bh if ctx.bh else 15.0)); c, rc = ctx.g('c', 'plaster'), col(ctx.roof())
    roof = ctx.g('roof', 'hip'); a = float(ctx.g('a', A_WIN))
    B.prism(g_, 0, min(1.0, h * 0.1), 'stone2', A_STONE, 0.0, 'found')
    B.prism(g_, min(1.0, h * 0.1), h, c, a, 0.3, 'body', top=rc if roof in ('flat', 'parapet') else None)
    rh = float(ctx.g('roof_h', min(W, 20) * 0.35))
    if roof == 'parapet':
        B.prism(g_.buffer(0.3, join_style=2), h, h + 1.0, c, A_STONE, 0.7, 'roof')
        inner = g_.buffer(-0.6, join_style=2)
        B.prism(inner, h, h + 0.3, rc, A_STONE, 0.75, 'roof')
    elif roof == 'hip':
        if ctx.fp is None or ctx.fp.area / ctx.fp.minimum_rotated_rectangle.area > 0.8: B.hip(g_, h, rh, rc, 0.8)
        else:   # impronta irregolare: padiglioni per fette lungo l'asse
            for q in _split(g_, F, 4): B.hip(q, h, min(rh, _frame_w(q) * 0.35), rc, 0.8)
    elif roof == 'gable':
        tm = 0.0
        for q, ax in ((g_.intersection(F.rect(-1e4, 1e4, -1e4, tm)), F.v), (g_.intersection(F.rect(-1e4, 1e4, tm, 1e4)), (-F.v[0], -F.v[1]))):
            for qq in _polys(q): B.wedge(qq, h, h, h + rh, ax, c, rc, a, 0.8, 'roof')
    elif roof == 'dome':
        ctr = g_.centroid; r = min(L, W) * 0.35
        B.cyl(ctr.x, ctr.y, r, h, h + r * 0.3, c, A_WIN, 0.75, 'roof', seg=16); B.dome(ctr.x, ctr.y, r, h + r * 0.3, r * 0.8, col(ctx.g('dome_c', ctx.style['dome'])), f=0.85)
    return B


def _frame_w(q):
    return frame_of(q).W


def _split(g_, F, n):
    L = F.L or 100
    out = []
    for i in range(n):
        q = g_.intersection(F.rect(-L / 2 - 1 + (L + 2) * i / n, -L / 2 - 1 + (L + 2) * (i + 1) / n, -1e4, 1e4))
        out += [p for p in _polys(q) if p.area > 4]
    return out


@preset('castle')
def castle(ctx):
    """Castello: recinto quadrato merlato con torri tonde agli angoli e mastio quadrato al centro."""
    B, F = Builder(ctx), ctx.F
    L, W = ctx.dims(60.0, 50.0); h = float(ctx.g('h', 11.0)); c = ctx.g('c', 'stone'); rc = col(ctx.roof())
    wt = 3.0
    B.prism(F.rect(-L / 2, L / 2, -W / 2, W / 2).buffer(1.0, join_style=2), 0, 1.0, 'stone2', A_STONE, 0.0, 'found', simp=0)
    sides = [F.rect(-L / 2, L / 2, -W / 2, -W / 2 + wt), F.rect(-L / 2, L / 2, W / 2 - wt, W / 2), F.rect(-L / 2, -L / 2 + wt, -W / 2, W / 2), F.rect(L / 2 - wt, L / 2, -W / 2, W / 2)]
    for i, q in enumerate(sides):
        B.prism(q, 1.0, h, c, A_STONE, 0.1 + 0.08 * i, 'walls', simp=0); B.merlons(q, h, c, f=0.6, maxn=10)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = F.at(sx * L / 2, sy * W / 2)
            B.cyl(px, py, 4.5, 0, h + 5, c, A_STONE, 0.3, 'towers', seg=12)
            _tower_top(B, Frame(px, py, F.ang), 0, 0, 9, h + 5, ctx.g('tower_top', 'cone' if ctx.g('cones') else 'crenel'), c, rc, 0.7, plan='round', g='towers')
    kw = min(L, W) * 0.32; kh = float(ctx.g('keep_h', h * 2.6))
    B.prism(F.rect(-kw / 2, kw / 2, -kw / 2, kw / 2), 0, kh, c, A_STONE, 0.45, 'keep', simp=0)
    openings(B, F, 0, 0, kw, kh * 0.6, kh * 0.6 + 3.5, 0.5, 'keep', n=2, ow=0.9)
    _tower_top(B, F, 0, 0, kw, kh, ctx.g('keep_top', 'crenel'), c, rc, 0.85, g='keep')
    return B


# ================================================================== anni, impronte, assemblaggio
def _phases(lm):
    ph = lm.get('phases')
    if not ph:
        if lm.get('built') is not None:
            b = lm['built']; b = b if isinstance(b, (list, tuple)) else [b]; ph = [{'y': b[0], 'y1': b[1] if len(b) > 1 else None}]
        elif lm.get('y') is not None: ph = [{'y': lm['y'], 'y1': lm.get('y1')}]
        else: raise ValueError(f"{lm.get('name')}: mancano 'phases' (o 'built')")
    out = []
    for q in ph:
        y = float(q['y']); y1 = q.get('y1'); y1 = y + DEFAULT_SPAN if y1 is None else float(y1)
        if y1 < y: raise ValueError(f"{lm.get('name')}: fase con y1 < y ({y}, {y1})")
        gr = q.get('groups') or q.get('parts')
        out.append({'y': y, 'y1': max(y1, y + 1e-3), 'groups': set(gr) if gr else None, 'd': q.get('d')})
    return out


def _demol(lm):
    d = lm.get('demolished', lm.get('d'))
    if d is None: return None
    if isinstance(d, dict): return float(d['y']), float(d.get('y1', d['y']))
    if isinstance(d, (list, tuple)): return float(d[0]), float(d[-1])
    return float(d), float(d)


def assign_years(parts, lm):
    """_f/_g -> y (e d). Ritorna le parti con 'y' (e 'd'), senza i campi interni."""
    ph = _phases(lm); dem = _demol(lm)
    default = sorted([q for q in ph if not q['groups']], key=lambda q: q['y'])
    claimed = {g: q for q in ph if q['groups'] for g in q['groups']}
    if not default: default = [ph[0]] if not claimed else []
    rng = {}
    for p in parts:
        if p['_g'] in claimed: r = rng.setdefault(p['_g'], [1.0, 0.0]); r[0] = min(r[0], p['_f']); r[1] = max(r[1], p['_f'])
    fmax = max([p['_f'] for p in parts] or [1.0]) or 1.0
    out = []
    for p in parts:
        q = dict(p); f = q.pop('_f'); g = q.pop('_g')
        if g in claimed:
            c = claimed[g]; r = rng[g]; ff = 0.0 if r[1] - r[0] < 1e-9 else (f - r[0]) / (r[1] - r[0])
            y = c['y'] + (c['y1'] - c['y']) * ff
            if c.get('d') is not None: q['d'] = float(c['d'])
        else:
            if not default: c = ph[0]; y = c['y'] + (c['y1'] - c['y']) * f
            else:
                n = len(default); fn = min(f / fmax, 1.0); k = min(n - 1, int(fn * n)); ff = fn * n - k
                c = default[k]; y = c['y'] + (c['y1'] - c['y']) * ff
        q['y'] = round(y, 3)
        if dem and 'd' not in q:
            q['d'] = round(dem[0] + (dem[1] - dem[0]) * (1 - f / fmax), 3)
        if 'd' in q and q['d'] <= q['y'] + 0.01:
            print(f"[landmarks_kit] ATTENZIONE {lm.get('name')}: demolizione {q['d']} prima della costruzione {q['y']}: corretta", file=sys.stderr)
            q['d'] = round(q['y'] + 0.05, 3)
        out.append(q)
    return out


def part_top(p):
    t = p['t']
    if t in ('prism', 'cyl', 'cone', 'helix'): return p['z1']
    if t == 'hip': return p['z0'] + p['rh']
    if t == 'wedge': return max(p['za'], p['zb'])
    if t == 'dome': return p['z0'] + p['hz']
    if t == 'beam': return max(p['p0'][2], p['p1'][2]) + p['h'] / 2
    return 0.0


def part_shape(p):
    """Impronta 2D di una parte (per clear e test)."""
    t = p['t']
    if 'r' in p: return Polygon(p['r'])
    if t in ('cyl', 'dome'): return Point(p['cx'], p['cy']).buffer(p['rad'], 8)
    if t == 'cone': return Point(p['cx'], p['cy']).buffer(max(p['r0'], p['r1']), 8)
    if t == 'helix': return Point(p['cx'], p['cy']).buffer(max(p['r0'], p['r1']) + p['w'], 8)
    if t == 'beam': return LineString([p['p0'][:2], p['p1'][:2]]).buffer(max(p['w'] / 2, 0.2), cap_style=2) if math.dist(p['p0'][:2], p['p1'][:2]) > 0.01 else Point(p['p0'][:2]).buffer(p['w'] / 2)
    return None


class Footprints:
    """Indice delle impronte di DATA/buildings.json (lazy)."""

    def __init__(self, data):
        self.data, self._t = data, None

    def _load(self):
        if self._t is not None: return
        from shapely.strtree import STRtree
        p = os.path.join(self.data, 'buildings.json') if self.data else None
        self.b = json.load(open(p)) if (p and os.path.exists(p)) else []
        self.g = []
        for b in self.b:
            try:
                q = Polygon(b['r']); q = q if q.is_valid else q.buffer(0)
            except Exception: q = Point(0, 0).buffer(0.01)
            self.g.append(q)
        self._t = STRtree(self.g) if self.g else None

    def find(self, x, y, maxd=FP_SEARCH_M, merge=None, radius=80.0):
        self._load()
        if self._t is None: return None, None
        pt = Point(x, y); idx = None
        cand = self._t.query(pt.buffer(maxd))
        inside = [i for i in cand if self.g[i].contains(pt)]
        if inside: idx = max(inside, key=lambda i: self.g[i].area)
        else:
            cand = [i for i in cand if self.g[i].distance(pt) <= maxd]
            if cand: idx = min(cand, key=lambda i: self.g[i].distance(pt))
        if idx is None: return None, None
        g = self.g[idx]; got = {int(idx)}
        if merge:
            area = pt.buffer(radius); grow = True
            while grow:
                grow = False
                for j in self._t.query(g.buffer(merge)):
                    j = int(j)
                    if j in got or not self.g[j].intersects(area) or self.g[j].distance(g) > merge: continue
                    got.add(j); g = unary_union([g, self.g[j]]).buffer(merge / 2, join_style=2).buffer(-merge / 2, join_style=2); grow = True
            if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
        hs = [self.b[i].get('h') for i in got if self.b[i].get('h')]
        return g, (max(hs) if hs else None)


def build_landmark(lm, P=None, fps=None, style=None, others=None):
    """Un monumento della story -> (parts, clear_rings, label|None). P = geo.Proj; fps = Footprints."""
    kind = lm.get('kind', 'generic_footprint')
    if kind not in PRESETS: raise ValueError(f"{lm.get('name')}: preset sconosciuto '{kind}' (vedi kit/presets_landmarks.md)")
    name = lm.get('name', kind); prm = dict(lm.get('params') or {})
    def L(ll): return P.L(ll[0], ll[1]) if P else tuple(ll)
    if lm.get('xy') is not None: x, y = map(float, lm['xy'])
    elif lm.get('at') is not None: x, y = L(lm['at'])
    else: x = y = None
    line = None
    if lm.get('line_xy'): line = [tuple(map(float, p)) for p in lm['line_xy']]
    elif lm.get('line'): line = [L(p) for p in lm['line']]
    elif prm.get('line'): line = [L(p) for p in prm['line']]   # alias: linea dentro params
    if lm.get('ring'): line = [L(p) for p in lm['ring']]; line = line + [line[0]]
    if x is None and line: c = LineString(line).interpolate(0.5, normalized=True); x, y = c.x, c.y
    if x is None: raise ValueError(f"{name}: manca 'at' (o 'line')")
    fp = None; bh = None; fpspec = lm.get('footprint')
    if fpspec == 'auto':
        if fps is not None:
            fp, bh = fps.find(x, y, float(prm.get('fp_search', FP_SEARCH_M)), prm.get('fp_merge'), float(prm.get('fp_radius', 80.0)))
        if fp is None: print(f"[landmarks_kit] {name}: nessuna impronta entro {FP_SEARCH_M:.0f} m da 'at': uso le misure dei params", file=sys.stderr)
    elif isinstance(fpspec, list) and len(fpspec) >= 3:
        fp = Polygon([L(p) for p in fpspec]).buffer(0)
    if fp is not None and fp.is_empty: fp = None
    mx = float(prm.get('max_fp', MAX_FP.get(kind, 1e9)))
    if fp is not None and min(frame_of(fp).L, frame_of(fp).W) > mx:   # torre su una particella grande: impronta ignorata
        print(f"[landmarks_kit] {name}: impronta del catasto troppo larga per '{kind}' ({min(frame_of(fp).L, frame_of(fp).W):.0f} m > {mx:.0f}): "
              f"uso 'at' e le misure dei params", file=sys.stderr)
        fp = None; bh = None
    if fp is not None: F = frame_of(fp, prm.get('ang'), prm.get('flip', False))
    else: F = Frame(x, y, float(prm.get('ang', 0.0)) + (180 if prm.get('flip') else 0))
    if line and fp is None: F.L, F.W = LineString(line).length, None
    # cattedrale con campanile separato: la sua area esce dall'impronta
    tref = prm.get('tower_ref')
    if tref and others:
        o = next((q for q in others if q.get('name') == tref), None)
        if o is not None:
            ox, oy = (map(float, o['xy']) if o.get('xy') is not None else L(o['at']))
            prm['_tower_cut'] = Point(ox, oy).buffer(float(prm.get('tower_cut_r', 9.0)))
    ctx = Ctx(name, F, prm, fp, line, bh, style)
    y_first = min(q['y'] for q in _phases(lm))
    win = prm.get('windows')
    if win is None: win = not (kind in STONE_KINDS or (kind in STONE_BEFORE and y_first < STONE_BEFORE[kind]))
    ctx.windows = bool(win)
    B = PRESETS[kind](ctx)
    parts = assign_years(B.parts, lm)
    for p in parts: p['name'] = name
    parts = [dict(sorted(p.items())) for p in parts]
    top = max(part_top(p) for p in parts) if parts else 0.0
    # clear: impronta (o ingombro delle parti) per gli edifici; di default no per mura/ponti e monumenti demoliti
    clear = []
    cl = lm.get('clear', None)
    if cl is None: cl = kind not in ('wall_segment', 'walls', 'bridge_arches', 'bridge') and _demol(lm) is None and not prm.get('no_clear')
    if cl:
        if fp is not None: g = fp.buffer(1.0)
        else:
            shp = [s for s in (part_shape(p) for p in parts) if s is not None and not s.is_empty]
            g = unary_union(shp).convex_hull.buffer(2.0) if shp else None
        r = ring(g, 0.3) if g is not None else None
        if r: clear.append(r)
    label = None
    if lm.get('label', True):
        ys = [p['y'] for p in parts]; ds = [p['d'] for p in parts if 'd' in p]
        lx, ly = (fp.centroid.x, fp.centroid.y) if fp is not None and kind in ('generic_footprint', 'footprint', 'building') else (x, y)
        tp = max(parts, key=part_top) if parts else None
        if tp is not None and kind in ('cathedral', 'church', 'church_dome', 'central_church', 'bell_tower', 'campanile'):
            s = part_shape(tp); lx, ly = (s.centroid.x, s.centroid.y) if s is not None else (lx, ly)
        label = {'name': lm.get('label_name', name), 'x': round(lx, 1), 'y': round(ly, 1), 'z': round(top, 1), 'from': round(min(ys), 2) if ys else None}
        if ds and len(ds) == len(parts): label['to'] = round(max(ds), 2)
        if lm.get('icon'): label['icon'] = lm['icon']
    return parts, clear, label


def build_all(story, data=None):
    """story (dict) -> dict landmarks.json (senza mura). data = cartella DATA per le impronte 'auto'."""
    P = geo.Proj.of(story) if story.get('city', {}).get('lat0') is not None else None
    fps = Footprints(data)
    style = story.get('city', {}).get('style_preset')
    parts, clear, labels = [], [], []
    lms = story.get('landmarks') or []
    for lm in lms:
        p, c, l = build_landmark(lm, P, fps, style, lms)
        parts += p; clear += c
        if l: labels.append(l)
    return {'parts': parts, 'clear': clear, 'labels': labels}


def merge_walls(out, data):
    """Unisce DATA/landmarks_walls.json (scritto da kit/hist_kit.py): lista di parti o dict {parts, clear, labels, ...}."""
    p = os.path.join(data, 'landmarks_walls.json')
    if not os.path.exists(p): return 0
    w = json.load(open(p))
    if isinstance(w, list): w = {'parts': w}
    n = 0
    for k, v in w.items():
        if isinstance(v, list): out.setdefault(k, []); out[k] = out[k] + v; n += len(v) if k == 'parts' else 0
        elif k not in out: out[k] = v
    return n


def montage_labels(labels):
    """{nome: [x, y, h, anno]} per montaggio/labels_cam.py."""
    m = {}
    for l in labels:
        if l.get('from') is None: continue
        m[l['name']] = [l['x'], l['y'], l['z'], int(math.floor(l['from']))]
    return m


def build(slug_or_path, data=None, montage=True, quiet=False):
    story = geo.load_story(slug_or_path)
    D = data or geo.data_dir(story)
    os.makedirs(D, exist_ok=True)
    out = build_all(story, D)
    nwall = merge_walls(out, D)
    lp = os.path.join(D, 'landmarks.json')
    if os.path.exists(lp):   # una volta sola: copia del landmarks.json non scritto dal kit
        try: old = json.load(open(lp))
        except Exception: old = {}
        if isinstance(old, dict) and '_kit' not in old and not os.path.exists(os.path.join(D, 'landmarks_legacy.json')):
            with open(lp) as a, open(os.path.join(D, 'landmarks_legacy.json'), 'w') as b: b.write(a.read())
    slug = story['city'].get('slug', 'city')
    out['_kit'] = {'slug': slug, 'landmarks': len(story.get('landmarks') or []), 'wall_parts': nwall}
    with open(lp, 'w') as f: json.dump(out, f, separators=(',', ':'))
    mp = None
    if montage:
        mp = os.path.join(geo.ROOT, 'montaggio', f'landmarks_{slug}.json')
        with open(mp, 'w') as f: json.dump(montage_labels(out['labels']), f, indent=0, ensure_ascii=False)
    if not quiet:
        print(f"[landmarks_kit] {slug}: {len(story.get('landmarks') or [])} monumenti, {len(out['parts'])} parti "
              f"({nwall} delle mura), clear {len(out['clear'])}, etichette {len(out['labels'])} -> {lp}" + (f" + {mp}" if mp else ''))
    return out


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return 0
    if a[0] == 'list':
        seen = {}
        for k, fn in PRESETS.items(): seen.setdefault(fn, []).append(k)
        for fn, ks in seen.items(): print(f"{ks[0]:18s} {'(' + ', '.join(ks[1:]) + ')' if ks[1:] else '':28s} {(fn.__doc__ or '').strip().splitlines()[0]}")
        return 0
    if a[0] == 'build' and len(a) >= 2:
        build(a[1], a[2] if len(a) > 2 else None); return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main())
