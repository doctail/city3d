"""Follower City - COZY v5: CENTRO STORICO basso (2-3 piani) che cresce da UN palazzo; camera alta 20-30 gradi, tutto visibile.

Uso (pip bpy):  python cozy_city.py --followers 111 --out cozy5_111.png
Opzioni: --res 540 960 --samples 40 --seed 7 --save-blend f.blend
Citta' a isolati ortogonali: un viale (x=0, asse y) con isolati ai due lati; ogni follower = un lotto (palazzo).
Ordine dei lotti FISSO (distanza dal centro): il lotto i ha sempre posizione/stile/colori uguali, N sceglie quanti.
v5: camera alta (22->30 gradi) che si allontana con N (camera_for), DOF leggero; centro storico basso, altezza cresce con la distanza dal centro;
terreno = prato/orti, colline verdi; N=1: un solo palazzo con lotto di selciato, pezzo di strada, lampione, albero; niente fumo.
"""
import sys, math, random, time, argparse, zlib
import bpy, bmesh
from mathutils import Vector, Matrix

PX, PY = 25.0, 37.0          # passo isolati: x (viale largo 9), y (traversa larga 7)
BLK_D, BLK_L = 8.0, 30.0     # profondita' lotto, lunghezza lato isolato
SW = 2.0                     # marciapiede viale
FH, FH0 = 3.2, 3.7           # altezza piano, piano terra


def lin(c):
    return tuple(x ** 2.2 for x in c)


def rgs(seed, *key):
    return random.Random(zlib.crc32((str(seed) + ":" + ":".join(map(str, key))).encode()))


# ---------------------------------------------------------------- materiali
_mats = {}


def _principled(name, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    return m, nt, b


def _spec(b, v):
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = v
            return


def flat(name, rgb, rough=0.8, emit=None, strength=0.0, metal=0.0):
    if name in _mats:
        return _mats[name]
    m, nt, b = _principled(name, rough)
    b.inputs["Base Color"].default_value = (*lin(rgb), 1)
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(emit), 1)
        b.inputs["Emission Strength"].default_value = strength
    _mats[name] = m
    return m


def brick(name, c1, c2, mortar, bw=0.5, bh=0.18, scale=1.0, rough=0.85, bump=0.5, off=0.5, msz=0.012, fine=True):
    """mattoni/tegole/pietra: texture mattoni procedurale su UV (1 uv = 1 m), bump sottile."""
    if name in _mats:
        return _mats[name]
    m, nt, b = _principled(name, rough)
    uv = nt.nodes.new("ShaderNodeUVMap")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = off
    br.inputs["Scale"].default_value = scale
    br.inputs["Color1"].default_value = (*lin(c1), 1)
    br.inputs["Color2"].default_value = (*lin(c2), 1)
    br.inputs["Mortar"].default_value = (*lin(mortar), 1)
    br.inputs["Mortar Size"].default_value = msz
    br.inputs["Mortar Smooth"].default_value = 0.1
    br.inputs["Bias"].default_value = 0.0
    br.inputs["Brick Width"].default_value = bw
    br.inputs["Row Height"].default_value = bh
    nt.links.new(uv.outputs["UV"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.02
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    _mats[name] = m
    return m


def plaster(name, rgb, rough=0.88, var=0.04):
    if name in _mats:
        return _mats[name]
    m, nt, b = _principled(name, rough)
    uv = nt.nodes.new("ShaderNodeUVMap")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 18.0
    nz.inputs["Detail"].default_value = 8
    nt.links.new(uv.outputs["UV"], nz.inputs["Vector"])
    base = lin(rgb)
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[6].default_value = (*[c * (1 - var * 2) for c in base], 1)
    mx.inputs[7].default_value = (*[min(1, c * (1 + var * 2)) for c in base], 1)
    nt.links.new(nz.outputs["Fac"], mx.inputs[0])
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    bp.inputs["Distance"].default_value = 0.01
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    _mats[name] = m
    return m


BRICKS = [((0.66, 0.30, 0.22), (0.58, 0.25, 0.19)), ((0.55, 0.26, 0.20), (0.48, 0.21, 0.16)),
          ((0.72, 0.40, 0.28), (0.64, 0.34, 0.24)), ((0.46, 0.30, 0.26), (0.40, 0.25, 0.22)),
          ((0.78, 0.60, 0.42), (0.70, 0.52, 0.36))]
PLASTERS = [(0.95, 0.86, 0.68), (0.93, 0.70, 0.60), (0.78, 0.84, 0.70), (0.72, 0.82, 0.88), (0.94, 0.78, 0.76),
            (0.97, 0.92, 0.80), (0.90, 0.74, 0.50), (0.76, 0.80, 0.78)]
STONES = [(0.84, 0.78, 0.66), (0.78, 0.70, 0.58), (0.88, 0.84, 0.74)]
ROOFC = [((0.30, 0.34, 0.40), (0.26, 0.30, 0.36)), ((0.60, 0.30, 0.22), (0.54, 0.26, 0.19)),
         ((0.36, 0.40, 0.44), (0.30, 0.34, 0.38))]
DOORS = [(0.16, 0.32, 0.26), (0.14, 0.24, 0.42), (0.58, 0.16, 0.16), (0.20, 0.20, 0.22), (0.82, 0.60, 0.20)]
AWNC = [(0.80, 0.22, 0.22), (0.22, 0.46, 0.34), (0.18, 0.30, 0.52), (0.88, 0.62, 0.20)]
COATS = [(0.8, 0.25, 0.22), (0.25, 0.45, 0.7), (0.9, 0.75, 0.3), (0.3, 0.55, 0.4), (0.9, 0.9, 0.85), (0.5, 0.3, 0.6)]
FLOW = [(0.95, 0.30, 0.38), (0.99, 0.85, 0.30), (0.99, 0.97, 0.92), (0.72, 0.50, 0.90), (0.98, 0.58, 0.72)]


def m_wall(k):
    if k < 100:
        c1, c2 = BRICKS[k % len(BRICKS)]
        return brick(f"brick{k}", c1, c2, (0.80, 0.74, 0.64), bw=0.42, bh=0.16, scale=1.0, bump=0.45)
    return plaster(f"plast{k}", PLASTERS[(k - 100) % len(PLASTERS)])


def m_stone(i=0):
    c = STONES[i % 3]
    return brick(f"stone{i % 3}", c, tuple(x * 0.93 for x in c), tuple(x * 0.8 for x in c), bw=1.1, bh=0.55, bump=0.3, msz=0.02, off=0.5)


def m_roof(i):
    c1, c2 = ROOFC[i % 3]
    return brick(f"roof{i % 3}", c1, c2, tuple(x * 0.45 for x in c1), bw=0.28, bh=0.22, scale=1.0, bump=0.8, msz=0.03, rough=0.6)


def m_trim(): return plaster("trim", (0.97, 0.94, 0.88), rough=0.7, var=0.01)
def m_iron(): return flat("iron", (0.10, 0.10, 0.11), rough=0.5, metal=0.6)
def m_zinc(): return flat("zinc", (0.42, 0.46, 0.50), rough=0.5, metal=0.4)
def m_door(i): return flat(f"door{i % 5}", DOORS[i % 5], rough=0.55)
def m_wood(): return flat("wood", (0.40, 0.26, 0.17), rough=0.7)
def m_dark(): return flat("darkw", (0.22, 0.15, 0.12), rough=0.7)
def m_awn(i): return flat(f"awn{i % 4}", AWNC[i % 4], rough=0.8)
def m_cream(): return flat("cream", (0.96, 0.92, 0.84), rough=0.8)
def m_leaf(i): return flat(f"leaf{i % 3}", [(0.30, 0.46, 0.24), (0.38, 0.52, 0.26), (0.26, 0.40, 0.24)][i % 3], rough=0.85)
def m_trunk(): return flat("trunk", (0.34, 0.24, 0.17), rough=0.9)
def m_flow(i): return flat(f"flw{i % 5}", FLOW[i % 5], rough=0.6)
def m_coat(i): return flat(f"coat{i % 6}", COATS[i % 6], rough=0.8)
def m_skin(): return flat("skin", (0.92, 0.72, 0.58), rough=0.8)
def m_copper(): return flat("copper", (0.30, 0.55, 0.48), rough=0.45, metal=0.5)
def m_water(): return flat("water", (0.40, 0.62, 0.66), rough=0.05)
def m_pot(): return flat("pot", (0.70, 0.38, 0.26), rough=0.8)
def m_sign(i): return flat(f"sign{i % 4}", [(0.14, 0.28, 0.24), (0.55, 0.14, 0.16), (0.14, 0.22, 0.40), (0.30, 0.18, 0.12)][i % 4], rough=0.6)
def m_lettr(): return flat("lettr", (0.98, 0.88, 0.62), rough=0.5, emit=(1.0, 0.80, 0.40), strength=1.5)
def m_lamp(): return flat("lamp", (1, 0.85, 0.5), rough=0.4, emit=(1.0, 0.72, 0.30), strength=40.0)
def m_win_lit(): return flat("winlit", (1.0, 0.82, 0.45), rough=0.3, emit=(1.0, 0.68, 0.26), strength=4.2)
def m_shop_lit(): return flat("shoplit", (1.0, 0.86, 0.55), rough=0.3, emit=(1.0, 0.72, 0.32), strength=7.0)
def m_win_dark():
    if "windark" in _mats:
        return _mats["windark"]
    m = flat("windark", (0.05, 0.07, 0.09), rough=0.06)
    _spec(m.node_tree.nodes["Principled BSDF"], 1.0)
    return m


def m_asphalt():
    return brick("cobble", (0.50, 0.48, 0.46), (0.44, 0.42, 0.41), (0.27, 0.26, 0.25), bw=0.22, bh=0.14, scale=1.0, bump=1.2, msz=0.02, off=0.5, rough=0.8)


def m_paving():
    return brick("paving", (0.76, 0.69, 0.60), (0.70, 0.63, 0.55), (0.55, 0.50, 0.44), bw=0.6, bh=0.3, bump=0.4, msz=0.015, rough=0.85)


def m_curb(): return flat("curb", (0.70, 0.66, 0.60), rough=0.8)
def m_rail(): return flat("rails", (0.28, 0.27, 0.27), rough=0.4, metal=0.7)


# ---------------------------------------------------------------- mesh builder
class MB:
    def __init__(self, T=None):
        self.bm = bmesh.new()
        self.slots = []
        self.T = T
        self.uvl = self.bm.loops.layers.uv.verify()

    def slot(self, m):
        if m not in self.slots:
            self.slots.append(m)
        return self.slots.index(m)

    def _add(self, pb, idx, smooth):
        T = self.T
        mp = {v: self.bm.verts.new(T @ v.co if T else v.co) for v in pb.verts}
        for f in pb.faces:
            nf = self.bm.faces.new([mp[v] for v in f.verts])
            nf.material_index = idx
            nf.smooth = smooth
            n = f.normal
            if T:
                n = T.to_3x3() @ n
            ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
            for l in nf.loops:
                p = l.vert.co
                if az > 0.72:
                    l[self.uvl].uv = (p.x, p.y)
                elif ax > ay:
                    l[self.uvl].uv = (p.y, p.z)
                else:
                    l[self.uvl].uv = (p.x, p.z)

    def part(self, verts, faces, m, bevel=0.0, smooth=False):
        pb = bmesh.new()
        vs = [pb.verts.new(v) for v in verts]
        for f in faces:
            pb.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(pb, faces=pb.faces)
        if bevel > 0:
            bmesh.ops.bevel(pb, geom=list(pb.edges), offset=bevel, segments=1, affect='EDGES')
            pb.normal_update()
        self._add(pb, self.slot(m), smooth)
        pb.free()

    def box(self, x0, y0, z0, x1, y1, z1, m, bevel=0.0):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.part(v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, bevel)

    def prism(self, poly, y0, y1, m):
        """poligono (x,z) estruso lungo y."""
        n = len(poly)
        v = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
        f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m)

    def slab(self, p, th, m):
        """quadrilatero p[0..3] con spessore th lungo la normale."""
        a, b, c, d = [Vector(q) for q in p]
        nrm = (b - a).cross(d - a).normalized() * th
        v = [tuple(q) for q in (a, b, c, d)] + [tuple(q + nrm) for q in (a, b, c, d)]
        self.part(v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m)

    def cyl(self, cx, cy, z0, z1, r, m, n=12, r2=None, smooth=True):
        r2 = r if r2 is None else r2
        v = []
        for rad, zz in ((r, z0), (r2, z1)):
            for k in range(n):
                a = 2 * math.pi * k / n
                v.append((cx + rad * math.cos(a), cy + rad * math.sin(a), zz))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m, smooth=smooth)

    def cylx(self, x0, x1, cy, cz, r, m, n=12):
        """cilindro lungo x (ruote orientate lungo l'asse)."""
        v = []
        for xx in (x0, x1):
            for k in range(n):
                a = 2 * math.pi * k / n
                v.append((xx, cy + r * math.cos(a), cz + r * math.sin(a)))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m, smooth=True)

    def cone(self, cx, cy, z0, z1, r, m, n=12):
        v = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z0) for k in range(n)]
        v.append((cx, cy, z1))
        self.part(v, [tuple(range(n - 1, -1, -1))] + [(k, (k + 1) % n, n) for k in range(n)], m, smooth=False)

    def sphere(self, cx, cy, cz, r, m, sub=2, sz=1.0):
        pb = bmesh.new()
        bmesh.ops.create_icosphere(pb, subdivisions=sub, radius=r)
        for v in pb.verts:
            v.co.z *= sz
            v.co += Vector((cx, cy, cz))
        pb.normal_update()
        self._add(pb, self.slot(m), True)
        pb.free()

    def frustum(self, x0, x1, ya0, ya1, z0, yb0, yb1, z1, m):
        v = [(x0, ya0, z0), (x1, ya0, z0), (x1, ya1, z0), (x0, ya1, z0),
             (x0, yb0, z1), (x1, yb0, z1), (x1, yb1, z1), (x0, yb1, z1)]
        self.part(v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m)

    def build(self, name):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.slots:
            me.materials.append(m)
        return me


# ---------------------------------------------------------------- elementi di facciata (coord locali: fronte y=0, x centro)
def window(b, x, zb, ww, wh, lit, trim, flowers=0, shut=None, arch=False):
    g = m_win_lit() if lit else m_win_dark()
    b.box(x - ww / 2, -0.05, zb, x + ww / 2, 0.0, zb + wh, g)
    b.box(x - ww / 2 - 0.09, -0.16, zb - 0.10, x + ww / 2 + 0.09, 0.0, zb, trim)                    # davanzale
    b.box(x - ww / 2 - 0.10, -0.10, zb + wh, x + ww / 2 + 0.10, 0.0, zb + wh + 0.13, trim)          # architrave
    for s in (-1, 1):
        b.box(x + s * ww / 2 - 0.04 + (0.04 if s > 0 else 0.0), -0.09, zb, x + s * (ww / 2 + 0.08) , 0.0, zb + wh, trim)
    b.box(x - 0.02, -0.08, zb, x + 0.02, -0.04, zb + wh, trim)                                    # montante
    b.box(x - ww / 2, -0.08, zb + wh * 0.66, x + ww / 2, -0.04, zb + wh * 0.66 + 0.04, trim)      # traversa
    if shut is not None:
        for s in (-1, 1):
            b.box(x + s * (ww / 2 + 0.12) - 0.2 * (1 if s > 0 else 0) - 0.2 * (0 if s > 0 else 1) + (0 if s > 0 else 0),
                  -0.1, zb, x + s * (ww / 2 + 0.12) + (0.0), 0.0, zb + wh, m_door(shut))
    if flowers:
        b.box(x - ww / 2 - 0.05, -0.34, zb - 0.32, x + ww / 2 + 0.05, -0.1, zb - 0.1, m_wood())
        for q in range(4):
            b.sphere(x - ww / 2 + 0.12 + q * (ww - 0.2) / 3, -0.24, zb - 0.02, 0.09, m_flow(flowers + q), sub=1)
        b.box(x - ww / 2, -0.30, zb - 0.1, x + ww / 2, -0.12, zb - 0.02, m_leaf(flowers))


def balcony(b, x, zb, ww, trim):
    hw = ww / 2 + 0.28
    b.box(x - hw, -0.62, zb - 0.10, x + hw, 0.0, zb + 0.02, m_stone(1))
    b.box(x - hw, -0.62, zb + 0.98, x + hw, -0.58, zb + 1.02, m_iron())
    b.box(x - hw, -0.62, zb + 0.04, x + hw, -0.58, zb + 0.08, m_iron())
    for s in (-1, 1):
        b.box(x + s * hw - 0.02, -0.62, zb, x + s * hw + 0.02, 0.0, zb + 1.0, m_iron())
    npk = int(hw * 2 / 0.16)
    for q in range(npk + 1):
        xx = x - hw + q * (2 * hw) / npk
        b.box(xx - 0.012, -0.61, zb + 0.06, xx + 0.012, -0.59, zb + 1.0, m_iron())


def door(b, x, dm, trim, stoop=0.0):
    dw, dh = 1.15, 2.45
    z0 = stoop
    b.box(x - dw / 2 - 0.14, -0.16, z0, x + dw / 2 + 0.14, 0.0, z0 + dh + 0.18, trim)
    b.box(x - dw / 2, -0.20, z0, x + dw / 2, -0.12, z0 + dh, m_door(dm))
    b.box(x - dw / 2 + 0.2, -0.215, z0 + 1.3, x + dw / 2 - 0.2, -0.19, z0 + dh - 0.2, m_win_lit())
    b.box(x + dw / 2 - 0.2, -0.24, z0 + 1.0, x + dw / 2 - 0.14, -0.2, z0 + 1.1, m_lamp() if False else flat("brass", (0.8, 0.6, 0.2), rough=0.3, metal=0.8))
    if stoop > 0:
        steps = int(stoop / 0.2)
        for q in range(steps):
            b.box(x - dw / 2 - 0.3, -0.55 - (steps - q) * 0.28, 0, x + dw / 2 + 0.3, -0.27 - (steps - q) * 0.28 + 0.28, stoop - q * 0.2, m_stone(0))
        b.box(x - dw / 2 - 0.3, -0.62, 0, x + dw / 2 + 0.3, 0.0, stoop, m_stone(0))


def awning(b, x0, x1, zt, proj, drop, k, rg):
    ns = max(6, int((x1 - x0) / 0.32))
    wst = (x1 - x0) / ns
    for q in range(ns):
        xa, xb = x0 + q * wst, x0 + (q + 1) * wst
        mm = m_awn(k) if q % 2 == 0 else m_cream()
        b.slab([(xa, 0.02, zt), (xb, 0.02, zt), (xb, -proj, zt - drop), (xa, -proj, zt - drop)], 0.025, mm)
        b.box(xa, -proj - 0.01, zt - drop - 0.18, xb, -proj + 0.02, zt - drop, mm)       # frangia


def shopfront(b, w, kind, rg, k):
    """vetrina: cornice scura, vetro illuminato, porta, insegna, tenda a righe, tavolini."""
    fc = m_sign(k)
    hw = w / 2
    b.box(-hw, -0.20, 0.0, hw, 0.0, 0.35, m_stone(2))                                             # zoccolo
    b.box(-hw, -0.20, 3.35, hw, 0.0, FH0, fc)                                                      # fascia insegna
    for s in (-1, 1):
        b.box(s * hw - (0.25 if s > 0 else -0.25) * 1.0, -0.20, 0.35, s * hw, 0.0, 3.35, fc)       # pilastri
    dx = hw - 1.0 if rg.random() < 0.5 else -hw + 1.0
    gx0, gx1 = (-hw + 0.25, hw - 1.6) if dx > 0 else (-hw + 1.6, hw - 0.25)
    b.box(gx0, -0.26, 0.5, gx1, -0.20, 2.7, m_shop_lit())
    nm = max(2, int((gx1 - gx0) / 0.9))
    for q in range(nm + 1):
        xx = gx0 + q * (gx1 - gx0) / nm
        b.box(xx - 0.025, -0.30, 0.5, xx + 0.025, -0.24, 2.7, fc)
    for zz in (0.5, 2.65):
        b.box(gx0, -0.30, zz, gx1, -0.24, zz + 0.06, fc)
    b.box(gx0, -0.30, 1.05, gx1, -0.22, 1.10, m_dark())                                            # ripiano
    for q in range(int((gx1 - gx0) / 0.45)):
        c = (rg.choice([m_flow(q), m_awn(q), m_cream()]) if kind != 1 else m_flow(q))
        b.box(gx0 + 0.15 + q * 0.45, -0.38, 1.10, gx0 + 0.45 + q * 0.45, -0.28, 1.10 + rg.uniform(0.12, 0.3), c)
    b.box(dx - 0.5, -0.24, 0.0, dx + 0.5, -0.18, 2.5, m_door(k + 1))
    b.box(dx - 0.35, -0.26, 1.0, dx + 0.35, -0.24, 2.3, m_shop_lit())
    # lettere (strisce chiare) sulla fascia
    cx = -hw + 0.5
    while cx < hw - 0.8:
        ln = rg.uniform(0.12, 0.34)
        b.box(cx, -0.215, 3.45, cx + ln, -0.20, 3.62, m_lettr())
        cx += ln + 0.09
    # tenda
    awning(b, -hw + 0.1, hw - 0.1, 3.3, 1.35, 0.55, k, rg)
    # insegna a bandiera
    sx = hw - 0.05 if rg.random() < 0.5 else -hw + 0.05
    b.box(sx - 0.02, -0.80, 3.5, sx + 0.02, -0.18, 3.55, m_iron())
    b.box(sx - 0.03, -0.84, 2.95, sx + 0.03, -0.30, 3.5, m_sign(k + 2))
    b.box(sx - 0.035, -0.80, 3.1, sx + 0.035, -0.34, 3.2, m_lettr())
    # tavolini fuori (caffe') / cassette fiori
    if kind == 0:
        for q, tx in enumerate((-hw * 0.35, hw * 0.35)):
            b.cyl(tx, -1.75, 0.72, 0.76, 0.32, m_dark(), n=10)
            b.cyl(tx, -1.75, 0.0, 0.72, 0.04, m_iron(), n=6)
            for ch in (-1, 1):
                b.box(tx + ch * 0.5 - 0.17, -1.75 - 0.17, 0.44, tx + ch * 0.5 + 0.17, -1.75 + 0.17, 0.48, m_awn(k))
                b.box(tx + ch * 0.5 - 0.17, -1.75 + (0.15 if ch > 0 else -0.17) - 0.01 * 0, 0.48, tx + ch * 0.5 + 0.17, -1.75 + (0.17 if ch > 0 else -0.15), 0.9, m_awn(k))
                b.box(tx + ch * 0.5 - 0.15, -1.75 - 0.15, 0.0, tx + ch * 0.5 - 0.12, -1.75 - 0.12, 0.44, m_iron())
                b.box(tx + ch * 0.5 + 0.12, -1.75 + 0.12, 0.0, tx + ch * 0.5 + 0.15, -1.75 + 0.15, 0.44, m_iron())
    elif kind == 2:
        for q in range(3):
            fx = -hw * 0.6 + q * hw * 0.55
            b.box(fx - 0.25, -1.05, 0, fx + 0.25, -0.65, 0.55, m_wood())
            for s_ in range(6):
                b.sphere(fx - 0.18 + (s_ % 3) * 0.18, -0.95 + (s_ // 3) * 0.18, 0.62, 0.1, m_flow(q + s_), sub=1)


def chimney(b, x, y, zt, rg, wall):
    b.box(x - 0.35, y - 0.3, zt - 0.5, x + 0.35, y + 0.3, zt + 1.3, wall)
    b.box(x - 0.42, y - 0.37, zt + 1.3, x + 0.42, y + 0.37, zt + 1.42, m_trim())
    b.box(x - 0.18, y - 0.14, zt + 1.42, x + 0.18, y + 0.14, zt + 1.75, m_pot())


def dormer(b, x, z0, ys, wid, lit, roofm, trim):
    """abbaino su falda: ys = y della falda a quota z0."""
    b.box(x - wid / 2, ys - 0.6, z0, x + wid / 2, ys + 0.7, z0 + 1.4, trim)
    b.box(x - wid / 2 + 0.12, ys - 0.64, z0 + 0.15, x + wid / 2 - 0.12, ys - 0.6, z0 + 1.2, m_win_lit() if lit else m_win_dark())
    b.box(x - 0.02, ys - 0.68, z0 + 0.15, x + 0.02, ys - 0.62, z0 + 1.2, trim)
    p = [(x - wid / 2 - 0.15, z0 + 1.4), (x + wid / 2 + 0.15, z0 + 1.4), (x, z0 + 2.1)]
    b.prism(p, ys - 0.7, ys + 0.8, roofm)
    b.box(x - wid / 2 - 0.18, ys - 0.72, z0 + 1.35, x + wid / 2 + 0.18, ys - 0.60, z0 + 1.42, trim)


# ---------------------------------------------------------------- palazzo
def mk_building(P):
    """P: style, w, n, wall, roof, shop, corner, door, seed -> mesh locale (fronte y=0)."""
    rg = rgs(P['seed'], 'b', P['style'], P['w'], P['n'], P['wall'], P['roof'], P['shop'], P['corner'], P['gab'])
    b = MB()
    w, n, st = P['w'], P['n'], P['style']
    hw = w / 2
    d = BLK_D
    H = FH0 + FH * (n - 1)
    wall = m_wall(P['wall'])
    trim = m_trim()
    stone = m_stone(P['wall'])
    roofm = m_roof(P['roof'])
    shop = P['shop'] >= 0
    brickwall = P['wall'] < 100
    # ---- corpo (poligono facciata)
    outline = [(-hw, 0), (hw, 0), (hw, H), (-hw, H)]
    gab = P['gab']
    if st == 0:                                                 # Amsterdam: timpano a gradoni / a campana
        if gab == 0:
            pts = [(hw, H)]
            zz = H
            xx = hw
            for s in range(4):
                pts.append((xx, zz + 0.45)); xx -= hw * 0.2; pts.append((xx, zz + 0.45)); zz += 0.45
            top = zz
            pts.append((0, top + 0.55))
            pts2 = [(-px, pz) for px, pz in reversed(pts)]
            outline = [(-hw, 0), (hw, 0)] + pts + pts2[1:] if False else [(-hw, 0), (hw, 0)] + pts + [(-p[0], p[1]) for p in reversed(pts[:-1])]
        else:
            pts = []
            for q in range(0, 13):
                t = q / 12.0
                px = hw * (1 - 0.82 * math.sin(t * math.pi / 2) ** 1.5) if t < 0.5 else hw * (0.55 - 0.55 * ((t - 0.5) * 2) ** 0.8) + 0.0
                pts.append((px, H + 2.4 * t))
            half = [(hw, H)] + [(min(hw, max(0.0, hw * (1.0 - 0.5 * t - 0.5 * t * t))), H + 2.2 * t) for t in [q / 10 for q in range(1, 11)]]
            outline = [(-hw, 0), (hw, 0)] + half + [(-p[0], p[1]) for p in reversed(half[:-1])]
    b.prism(outline, 0, d, wall)
    # fascia basamento in pietra
    if not shop:
        b.box(-hw - 0.02, -0.08, 0, hw + 0.02, 0.0, 0.9, stone)
    # cordoli di piano
    if st in (1, 2, 3, 5):
        for f in range(1, n):
            z = FH0 + FH * (f - 1) - 0.1 if f > 0 else 0
            b.box(-hw - 0.03, -0.08, z, hw + 0.03, 0.0, z + 0.12, trim if not brickwall else stone)
    elif st == 0:
        for f in range(1, n):
            z = FH0 + FH * (f - 1) + 1.0
            b.box(-hw - 0.02, -0.04, z, hw + 0.02, 0.0, z + 0.08, trim)
    # ---- finestre
    nb = max(2, int(round(w / 1.85)))
    ww = 0.95 if w < 5.2 else 1.05
    xs = [-hw + (q + 0.5) * w / nb for q in range(nb)]
    shut = rg.randrange(5) if (st in (2,) and rg.random() < 0.35) else None
    bal_floor = 1 if (st in (1, 2, 5) and n >= 3) else (2 if st == 2 else -1)
    for f in range(1, n):
        zb = FH0 + FH * (f - 1) + 0.55
        hh = 1.95 if f != bal_floor else 2.3
        for q, x in enumerate(xs):
            lit = rg.random() < 0.62
            fl = rg.randrange(5) + 1 if (rg.random() < 0.18 and f != bal_floor) else 0
            window(b, x, zb, ww, hh, lit, trim, flowers=fl, shut=shut)
        if f == bal_floor and st in (1, 2, 5):
            balcony(b, xs[len(xs) // 2], zb, ww, trim)
            if len(xs) >= 3 and w > 5.4:
                balcony(b, xs[0], zb, ww, trim) if rg.random() < 0.5 else None
    # ---- piano terra
    dm = P['door']
    if shop:
        shopfront(b, w, P['shop'], rg, P['door'])
    else:
        dx = xs[0] if len(xs) == 2 else xs[len(xs) // 2 - 1 if len(xs) > 2 else 0]
        stoop = 1.1 if st == 1 else 0.0
        door(b, dx, dm, trim, stoop)
        for x in xs:
            if abs(x - dx) > 0.9:
                window(b, x, 0.95 + stoop * 0.5, ww, 1.8, rg.random() < 0.7, trim, flowers=(rg.randrange(5) + 1 if rg.random() < 0.3 else 0))
    # ---- finestre sulle pareti laterali (solo palazzi isolati, es. il primo)
    if P.get('sidewin'):
        for sgn in (1, -1):
            b.T = Matrix.Translation((sgn * hw, 0, 0)) @ Matrix.Rotation(sgn * math.pi / 2, 4, 'Z')
            for f in range(0, n):
                zb = 0.95 if f == 0 else FH0 + FH * (f - 1) + 0.55
                for u in (1.9, 4.0, 6.1):
                    window(b, sgn * u, zb, 0.95, 1.8 if f == 0 else 1.95, rg.random() < 0.55, trim, flowers=(rg.randrange(5) + 1 if rg.random() < 0.2 else 0))
            b.T = None
    # ---- tetto
    zr = H
    if st == 0:
        top = H + (2.4 if gab else 2.0)
        for s in (-1, 1):
            b.box(s * hw - 0.06, -0.14, H - 0.1, s * hw + 0.06, 0.12, top, trim) if False else None
        b.box(-hw - 0.05, -0.18, H - 0.05, hw + 0.05, 0.0, H + 0.08, trim)
        b.box(-0.03, -0.12, H + 0.0, 0.03, 0.02, H + 0.0, trim) if False else None
        # carrucola (trave) in cima
        b.box(-0.05, -0.80, top - 0.1, 0.05, 0.0, top - 0.02, m_dark())
        b.box(-0.06, -0.86, top - 0.2, 0.06, -0.70, top - 0.05, m_iron())
        # falde (visibili dall'alto)
        rh = 2.6
        b.slab([(-hw, 0.1, top - 0.3), (hw, 0.1, top - 0.3), (hw, d / 2, top + rh * 0.5), (-hw, d / 2, top + rh * 0.5)], 0.08, roofm)
        b.slab([(-hw, d / 2, top + rh * 0.5), (hw, d / 2, top + rh * 0.5), (hw, d, top - 0.3), (-hw, d, top - 0.3)], 0.08, roofm)
        chimney(b, rg.uniform(-hw * 0.5, hw * 0.5), d * 0.7, top + 0.8, rg, wall)
    elif st == 1:                                               # brownstone: cornice a mensole + tetto piano
        b.box(-hw - 0.05, -0.52, H, hw + 0.05, d + 0.05, H + 0.35, stone)
        b.box(-hw - 0.03, -0.62, H + 0.35, hw + 0.03, d + 0.03, H + 0.5, trim)
        nbk = int(w / 0.5)
        for q in range(nbk):
            xx = -hw + 0.25 + q * w / nbk
            b.box(xx - 0.09, -0.5, H - 0.45, xx + 0.09, 0.0, H, stone)
        b.box(-hw, -0.1, H + 0.5, hw, d, H + 0.56, m_zinc())
        chimney(b, rg.uniform(-hw * 0.5, hw * 0.5), d * 0.6, H + 0.5, rg, wall)
    elif st in (2, 5):                                          # mansarda con abbaini
        b.box(-hw - 0.04, -0.46, H, hw + 0.04, 0.0, H + 0.28, trim)
        b.box(-hw - 0.02, -0.5, H + 0.28, hw + 0.02, -0.0, H + 0.36, stone)
        rh, ins = 2.6, 1.5
        b.frustum(-hw, hw, 0.0, d, H + 0.3, ins, d - ins, H + 0.3 + rh, roofm)
        b.box(-hw + 0.02, ins, H + 0.3 + rh, hw - 0.02, d - ins, H + 0.3 + rh + 0.12, m_zinc())
        zs = H + 0.3 + 0.35
        ysf = ins * (0.35 / rh)
        for x in xs:
            dormer(b, x, zs, ysf, 1.15, rg.random() < 0.6, roofm, trim)
        chimney(b, rg.uniform(-hw * 0.5, hw * 0.5), d * 0.55, H + 0.3 + rh, rg, wall)
        chimney(b, rg.uniform(-hw * 0.5, hw * 0.5), d * 0.62, H + 0.3 + rh, rg, wall)
    else:                                                       # st 3 (e negozi): tetto a due falde parallele alla strada
        ov = 0.35
        rh = 2.2 + 0.2 * rg.random()
        b.box(-hw - 0.04, -0.4, H, hw + 0.04, 0.0, H + 0.22, trim)
        p0 = [(-hw - 0.02, -ov, H + 0.2), (-hw - 0.02, d / 2, H + 0.2 + rh), (-hw - 0.02, d + ov, H + 0.2)]
        # falde: due lastre inclinate in (y,z)
        b.slab([(-hw, -ov, H + 0.18), (hw, -ov, H + 0.18), (hw, d / 2, H + 0.2 + rh), (-hw, d / 2, H + 0.2 + rh)], 0.1, roofm)
        b.slab([(-hw, d / 2, H + 0.2 + rh), (hw, d / 2, H + 0.2 + rh), (hw, d + ov, H + 0.18), (-hw, d + ov, H + 0.18)], 0.1, roofm)
        for s in (-1, 1):
            b.prism([(0, H + 0.2 + rh), (-0.0, H + 0.2 + rh)], 0, 0, wall) if False else None
        # timpani laterali (frontoni)
        for s in (-1, 1):
            xx = s * hw
            b.prism([(xx, H), (xx + s * 0.0 + 0.001, H)], 0, 0, wall) if False else None
        yz = (-ov + (d / 2 + ov) * 0.0)
        if w > 4.8:
            for x in xs[::2]:
                dormer(b, x, H + 0.2 + 0.5, (0.5 / rh) * d / 2 - ov * 0.0, 1.1, rg.random() < 0.6, roofm, trim)
        chimney(b, rg.uniform(-hw * 0.5, hw * 0.5), d * 0.55, H + 0.2 + rh * 0.8, rg, wall)
    # ---- torretta d'angolo
    if P['corner'] != 0:
        cs = P['corner']
        cx = cs * hw
        r = 1.15
        z0 = FH0 + FH * 0.9
        zt = H + (0.3 if st in (2, 5) else 0.0) + 0.9
        b.cyl(cx, 0.0, z0 + 0.2, zt, r, wall, n=12)
        b.cyl(cx, 0.0, z0 - 0.9, z0 + 0.2, 0.55, wall, n=12, r2=r)               # beccatello
        b.cyl(cx, 0.0, zt, zt + 0.25, r + 0.18, trim, n=12)
        b.cone(cx, 0.0, zt + 0.25, zt + 3.4, r + 0.25, m_roof(P['roof'] + 1), n=12)
        b.sphere(cx, 0.0, zt + 3.55, 0.12, m_lamp(), sub=1)
        for zz in (z0 + 0.7, z0 + FH * 0.95 if n > 3 else z0 + 0.7):
            if zz + 1.6 > zt:
                continue
            b.box(cx - 0.4, -r - 0.06, zz, cx + 0.4, -r + 0.12, zz + 1.5, m_win_lit() if rg.random() < 0.6 else m_win_dark())
            b.box(cx - 0.46, -r - 0.1, zz + 1.5, cx + 0.46, -r + 0.12, zz + 1.62, trim)
            sx = cx + cs * r
            b.box(min(sx - 0.06, sx + 0.12 * cs), -0.4, zz, max(sx - 0.06, sx + 0.12 * cs) + 0.0, 0.4, zz + 1.5, m_win_lit() if rg.random() < 0.6 else m_win_dark())
    return b


def mk_tower(P):
    """edificio con torre dell'orologio (landmark)."""
    rg = rgs(P['seed'], 'tower')
    b = MB()
    w = P['w']; hw = w / 2; d = BLK_D
    wall = m_wall(101); stone = m_stone(0); trim = m_trim()
    H = FH0 + FH * 2
    b.prism([(-hw, 0), (hw, 0), (hw, H), (-hw, H)], 0, d, m_wall(0))
    b.box(-hw - 0.05, -0.12, 0, hw + 0.05, 0.0, 1.0, stone)
    # portico ad archi
    for q in range(3):
        x = -hw + (q + 0.5) * w / 3
        b.box(x - 0.9, -0.3, 0, x + 0.9, 0.0, 2.9, m_stone(2)); b.box(x - 0.65, -0.34, 0, x + 0.65, -0.2, 2.5, m_shop_lit() if q != 1 else m_door(0))
    for f in (1, 2):
        zb = FH0 + FH * (f - 1) + 0.4
        for q in range(4):
            x = -hw + (q + 0.5) * w / 4
            window(b, x, zb, 1.0, 2.0, rg.random() < 0.6, trim)
    b.box(-hw - 0.1, -0.6, H, hw + 0.1, d, H + 0.3, stone)
    b.frustum(-hw, hw, 0.0, d, H + 0.3, 1.0, d - 1.0, H + 2.6, m_roof(0))
    tw = 3.6
    zt = H + 2.0
    th = zt + 12
    b.prism([(-tw / 2, zt - 2.1), (tw / 2, zt - 2.1), (tw / 2, th), (-tw / 2, th)], 1.4, 1.4 + tw, m_wall(2))
    b.box(-tw / 2 - 0.15, 1.25, th - 0.5, tw / 2 + 0.15, 1.55 + tw, th + 0.3, stone)
    for q, (xs_, ys_, rot) in enumerate(((0, 1.4 - 0.08, 0), (0, 1.4 + tw + 0.08, 0))):
        b.cyl(0, 0, 0, 0, 0.01, trim, n=3) if False else None
    zc = th - 3.6
    # quadrante frontale (verso -y) e lati
    b.cylx(-0.0, 0.0, 0, 0, 0.0, trim, n=3) if False else None
    for yy in (1.4 - 0.12, 1.4 + tw + 0.12):
        pass
    # disco frontale: cilindro con asse y costruito a mano
    n = 20
    r = 1.2
    for (y0, y1) in ((1.4 - 0.12, 1.4 - 0.0),):
        v = []
        for yy in (y0, y1):
            for k in range(n):
                a = 2 * math.pi * k / n
                v.append((r * math.cos(a), yy, zc + r * math.sin(a)))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        b.part(v, f, m_cream())
        b.box(-0.04, y0 - 0.02, zc, 0.04, y0 + 0.03, zc + 0.95, m_iron())
        b.box(0.0, y0 - 0.02, zc - 0.04, 0.7, y0 + 0.03, zc + 0.04, m_iron())
    b.box(-tw / 2 + 0.6, 1.4 - 0.1, zc - 3.0, tw / 2 - 0.6, 1.4 - 0.0, zc - 1.6, m_win_lit())
    b.frustum(-tw / 2 - 0.4, tw / 2 + 0.4, 1.0, 1.8 + tw, th + 0.3, 1.4 + tw / 2 - 0.1, 1.4 + tw / 2 + 0.1, th + 6.0, m_copper())
    b.sphere(0, 1.4 + tw / 2, th + 6.3, 0.2, flat("gold", (0.95, 0.75, 0.30), rough=0.3, metal=0.8), sub=1)
    return b


def mk_church(P):
    rg = rgs(P['seed'], 'church')
    b = MB()
    w = P['w']; hw = w / 2; d = BLK_D
    stone = m_stone(2); trim = m_trim()
    wl = m_stone(1)
    H = 11.0
    bw = hw - 2.4
    b.prism([(-hw, 0), (bw + 0.4, 0), (bw + 0.4, H), (0, H + 3.2), (-hw, H)], 0, d, wl)
    tx0, tx1 = bw + 0.6, hw
    b.prism([(tx0, 0), (tx1, 0), (tx1, 21), (tx0, 21)], 0, 3.4, wl)
    b.frustum(tx0 - 0.2, tx1 + 0.2, -0.2, 3.6, 21, 1.4, 2.0, 30, m_copper())
    b.box(tx0 + 0.3, -0.05, 15.5, tx1 - 0.3, 0.1, 19.0, m_win_dark())
    b.cyl((tx0 + tx1) / 2, -0.2, 17.8, 18.0, 0.7, m_cream(), n=16) if False else None
    # portale + rosone + guglia
    cxp = (-hw + bw + 0.4) / 2
    b.box(cxp - 1.2, -0.3, 0, cxp + 1.2, 0.0, 4.0, trim)
    b.box(cxp - 0.9, -0.34, 0, cxp + 0.9, -0.2, 3.4, m_door(2))
    b.box(cxp - 0.9, -0.34, 3.4, cxp + 0.9, -0.2, 3.6, m_shop_lit())
    n = 18
    r = 1.1
    v = []
    for yy in (-0.12, 0.0):
        for k in range(n):
            a = 2 * math.pi * k / n
            v.append((cxp + r * math.cos(a), yy, 7.6 + r * math.sin(a)))
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    b.part(v, f, m_win_lit())
    for q in range(3):
        b.box(cxp - 0.5 + q * 0.5 - 0.3, -0.12, 2.2 + 0.0, cxp - 0.5 + q * 0.5 + 0.3, 0.0, 2.8, m_win_lit()) if False else None
    b.box(-hw + 0.5, -0.1, 4.0, bw - 0.1, 0.0, 6.5, m_win_lit()) if False else None
    for x in (cxp - 2.0, cxp + 2.0):
        b.box(x - 0.4, -0.1, 4.2, x + 0.4, 0.0, 7.0, m_win_lit())
    rr = m_roof(0)
    b.slab([(-hw, -0.4, H - 0.1), (bw + 0.5, -0.4, H - 0.1), (bw + 0.5, d / 2, H + 3.3), (-hw, d / 2, H + 3.3)], 0.1, rr) if False else None
    b.slab([(-hw, 0.0, H + 0.0), (bw + 0.4, 0.0, H + 0.0), (bw + 0.4, d + 4, H + 0.0), (-hw, d + 4, H + 0.0)], 0.1, rr) if False else None
    return b


# ---------------------------------------------------------------- props di strada
def prop_lamp(b, x, y, z=0.0, face=0.0):
    b.cyl(x, y, z, z + 0.25, 0.14, m_iron(), n=8)
    b.cyl(x, y, z + 0.25, z + 3.9, 0.04, m_iron(), n=6)
    b.box(x - 0.14, y - 0.14, z + 3.9, x + 0.14, y + 0.14, z + 4.1, m_lamp())
    b.cone(x, y, z + 4.1, z + 4.35, 0.2, m_iron(), n=6)


def prop_tree(b, x, y, rg, z=0.0, big=1.0):
    """albero con chioma irregolare: blob di forma/colore diversi, asimmetrica, rami principali."""
    h = rg.uniform(2.6, 3.4) * (0.6 + 0.4 * big)
    lean = rg.uniform(-0.25, 0.25)
    b.cyl(x, y, z, z + h, 0.10 * big, m_trunk(), n=7, r2=0.05 * big)
    k = rg.randrange(3)
    bias = rg.uniform(0, 6.28)
    nb = rg.randrange(7, 12)
    for q in range(nb):
        a = bias + rg.gauss(0, 1.5)
        rr_ = rg.uniform(0.1, 1.3) * big
        zz = h * 0.85 + rg.uniform(-0.3, 1.9) * big - 0.5 * rr_
        rad = rg.uniform(0.40, 0.95) * big * (1.0 - 0.25 * max(0.0, zz - h) / (1.9 * big))
        b.sphere(x + lean * (zz - h) + rr_ * math.cos(a), y + rr_ * math.sin(a), z + zz, rad, m_leaf(k + rg.randrange(3)),
                 sub=1, sz=rg.uniform(0.65, 1.05))
    if rg.random() < 0.7:                                       # ramo-chioma bassa che rompe la sagoma
        a = rg.uniform(0, 6.28)
        b.sphere(x + 0.9 * math.cos(a) * big, y + 0.9 * math.sin(a) * big, z + h * 0.7, 0.42 * big, m_leaf(k + 1), sub=1, sz=0.7)


def prop_bench(b, x, y, along='y'):
    # panca con asse lungo y (marciapiede), schienale verso x+
    b.box(x - 0.25, y - 0.7, 0.42, x + 0.25, y + 0.7, 0.47, m_wood())
    b.box(x + 0.22, y - 0.7, 0.47, x + 0.27, y + 0.7, 0.95, m_wood())
    for yy in (-0.6, 0.6):
        b.box(x - 0.22, y + yy - 0.03, 0.0, x + 0.22, y + yy + 0.03, 0.42, m_iron())


def prop_planter(b, x, y, rg):
    b.box(x - 0.45, y - 0.3, 0.0, x + 0.45, y + 0.3, 0.5, m_pot())
    b.box(x - 0.42, y - 0.27, 0.5, x + 0.42, y + 0.27, 0.58, m_leaf(0))
    for q in range(7):
        b.sphere(x + rg.uniform(-0.36, 0.36), y + rg.uniform(-0.2, 0.2), 0.7 + rg.uniform(0, 0.12), rg.uniform(0.09, 0.14), m_flow(rg.randrange(5)), sub=1)


def prop_person(b, x, y, rg, z=0.0):
    c = rg.randrange(6)
    b.cyl(x, y, z, z + 0.85, 0.11, flat("trou", (0.22, 0.22, 0.28), rough=0.8), n=8, r2=0.1)
    b.cyl(x, y, z + 0.85, z + 1.45, 0.17, m_coat(c), n=8, r2=0.14)
    b.sphere(x, y, z + 1.6, 0.115, m_skin(), sub=1)
    b.cyl(x, y, z + 1.66, z + 1.72, 0.125, m_dark() if c % 2 else m_coat(c + 2), n=8)


def prop_bike(b, x, y, rg, z=0.0):
    # bicicletta lungo y
    for yy in (-0.42, 0.42):
        b.cylx(x - 0.015, x + 0.015, y + yy, z + 0.34, 0.34, m_iron(), n=14)
        b.cylx(x - 0.01, x + 0.01, y + yy, z + 0.34, 0.26, m_win_dark(), n=14) if False else None
    b.box(x - 0.015, y - 0.42, z + 0.34, x + 0.015, y + 0.0, z + 0.62, m_awn(rg.randrange(4)))
    b.box(x - 0.015, y - 0.0, z + 0.34, x + 0.015, y + 0.42, z + 0.40, m_awn(rg.randrange(4)))
    b.box(x - 0.015, y - 0.1, z + 0.60, x + 0.015, y + 0.18, z + 0.65, m_iron())
    b.box(x - 0.2, y - 0.46, z + 0.78, x + 0.2, y - 0.43, z + 0.81, m_iron())
    b.box(x - 0.17, y - 0.5, z + 0.62, x + 0.17, y - 0.2, z + 0.7, m_wood())          # cestino


def prop_fountain(b, x, y):
    b.cyl(x, y, 0.0, 0.7, 3.0, m_stone(0), n=24, smooth=False)
    b.cyl(x, y, 0.7, 0.74, 2.7, m_water(), n=24)
    b.cyl(x, y, 0.74, 2.2, 0.32, m_stone(0), n=12)
    b.cyl(x, y, 2.0, 2.15, 1.2, m_stone(0), n=16)
    b.cyl(x, y, 2.15, 2.19, 1.05, m_water(), n=16)
    b.cyl(x, y, 2.19, 3.2, 0.12, m_stone(0), n=8)
    b.sphere(x, y, 3.3, 0.18, m_water(), sub=2)
    for k in range(4):
        a = k * math.pi / 2
        b.sphere(x + 0.7 * math.cos(a), y + 0.7 * math.sin(a), 2.4, 0.07, m_water(), sub=1)


def prop_tram(b, y, x=0.95):
    L, W, Hh = 12.0, 2.3, 3.4
    b.box(x - W / 2, y - L / 2, 0.45, x + W / 2, y + L / 2, Hh, flat("tram", (0.88, 0.76, 0.34), rough=0.45))
    b.box(x - W / 2 - 0.01, y - L / 2, 1.0, x + W / 2 + 0.01, y + L / 2, 1.18, m_awn(0))
    b.box(x - W / 2, y - L / 2, 0.15, x + W / 2, y + L / 2, 0.5, m_iron())
    b.box(x - W / 2 - 0.02, y - L / 2 + 0.2, 1.6, x + W / 2 + 0.02, y + L / 2 - 0.2, 2.7, m_win_lit())
    for q in range(9):
        yy = y - L / 2 + 0.2 + q * (L - 0.4) / 8
        b.box(x - W / 2 - 0.04, yy - 0.04, 1.6, x + W / 2 + 0.04, yy + 0.04, 2.7, m_iron())
    b.box(x - W / 2 + 0.2, y - L / 2 - 0.02, 1.6, x + W / 2 - 0.2, y - L / 2 + 0.0, 2.7, m_win_lit())
    b.box(x - 0.6, y - 0.1, Hh, x + 0.6, y + 0.1, Hh + 0.2, m_iron())
    b.box(x - 0.02, y - 0.02, Hh + 0.2, x + 0.02, y + 4.0, Hh + 1.2, m_iron())


def prop_cart(b, x, y, rg):
    b.box(x - 0.55, y - 1.1, 0.55, x + 0.55, y + 1.1, 0.75, m_wood())
    for s in (-1, 1):
        b.box(x + s * 0.55 - 0.03, y - 1.1, 0.75, x + s * 0.55 + 0.03, y + 1.1, 1.15, m_wood())
        b.cylx(x + s * 0.6 - 0.04, x + s * 0.6 + 0.04, y, 0.5, 0.5, m_dark(), n=14)
    for q in range(5):
        b.sphere(x + rg.uniform(-0.3, 0.3), y + rg.uniform(-0.8, 0.8), 0.85, rg.uniform(0.18, 0.26), m_flow(q), sub=1)
    b.box(x - 0.05, y - 2.6, 0.45, x + 0.05, y - 1.1, 0.5, m_wood())


# ---------------------------------------------------------------- lotti e citta'
LANDMARKS = {(0, -1, 'W', 3): 'tower', (-1, 1, 'E', 3): 'church'}


def all_slots(seed):
    """tutti i lotti possibili della griglia, ordinati per distanza dal centro: lotto i fisso, N prende i primi N."""
    out = []
    for c in range(-6, 6):
        for r in range(-5, 6):
            cx, cy = PX * c + PX / 2, PY * r
            for side in ('W', 'E'):
                rg = rgs(seed, 'side', c, r, side)
                y = cy - BLK_L / 2
                idx = 0
                while y < cy + BLK_L / 2 - 3.6:
                    w = rg.choice([5.4, 5.8, 6.2, 6.6, 7.0])
                    lm = LANDMARKS.get((c, r, side, idx))
                    if lm:
                        w = 8.4 if lm == 'tower' else 9.0
                    if y + w > cy + BLK_L / 2 - 3.0:
                        w = cy + BLK_L / 2 - y
                        if w < 3.8 and out and False:
                            pass
                    xf = cx - BLK_D if side == 'W' else cx + BLK_D
                    out.append(dict(c=c, r=r, side=side, idx=idx, y0=y, w=w, yc=y + w / 2, xf=xf, lm=lm,
                                    first=(idx == 0), last=False))
                    y += w
                    idx += 1
                out[-1]['last'] = True
    for s in out:
        s['dist'] = math.hypot(s['xf'], (s['yc'] - 2.0) * 0.8) + 0.01 * s['idx'] + 0.0001 * s['c'] + 0.00001 * s['r']
        if s['side'] == 'E':
            s['dist'] += 0.002
    out.sort(key=lambda s: s['dist'])
    for k, s in enumerate(out):
        s['rank'] = k
    return out


def lot_params(s, seed):
    rg = rgs(seed, 'lot', s['c'], s['r'], s['side'], s['idx'])
    avenue = abs(s['xf']) < 6
    d = s['dist']
    # centro storico basso (2-3 piani); l'altezza cresce solo con la distanza dal centro
    if d < 45:
        n = rg.choice([2, 3, 3])
    elif d < 90:
        n = rg.choice([3, 3, 4])
    elif d < 150:
        n = rg.choice([3, 4, 4, 5])
    else:
        n = rg.choice([4, 5, 5, 6])
    brickc = rg.random() < 0.5
    wall = rg.randrange(5) if brickc else 100 + rg.randrange(8)
    shop = rg.randrange(3) if rg.random() < (0.75 if avenue else 0.3) else -1
    if s['w'] < 5.0 and rg.random() < 0.55:
        style = 0
    else:
        style = rg.choice([1, 2, 2, 3, 3, 0] if not brickc else [0, 0, 1, 3, 2])
    if s['lm']:
        style = 9
    corner = 0
    if (s['first'] or s['last']) and not s['lm'] and s['w'] > 4.3:
        if rg.random() < 0.5 and s['w'] > 4.9:
            north = s['last']
            cs = (1 if north else -1) * (1 if s['side'] == 'E' else -1)
            corner = cs
            style = 2 if style == 0 else style
            n = max(n, 3)
    P = dict(style=style, w=round(s['w'] * 4) / 4, n=n, wall=wall, roof=rg.randrange(3), shop=shop,
             corner=corner, door=rg.randrange(5), gab=rg.randrange(2), seed=seed)
    if s.get('rank') == 0 and not s['lm']:                      # il primo palazzo: negozietto cozy a 3 piani
        P.update(HERO)
    return P


HERO = dict(sidewin=1, style=2, n=3, wall=106, roof=1, shop=0, corner=0, door=2, gab=1)


# ---------------------------------------------------------------- terreno
def hill_h(x, y):
    ex = max(0.0, abs(x) - 150) / 260.0
    ey = max(0.0, abs(y) - 150) / 260.0
    e = min(1.0, math.hypot(ex, ey))
    e = e * e * (3 - 2 * e)
    n = (math.sin(x * 0.0065 + 1.3) * math.cos(y * 0.0049 + 0.4) + 0.6 * math.sin(x * 0.0123 + y * 0.0087) + 0.3 * math.sin(y * 0.021 - x * 0.013))
    return e * (70 + 45 * n) * (1.0 if y > 0 else 0.7) + (e * 25 if e > 0 else 0)


def big_ground(coll):
    xs = []
    nn = 150
    for k in range(-nn, nn + 1):
        t = k / nn
        xs.append(math.copysign(abs(t) ** 2.0, t) * 2500)
    bm = bmesh.new()
    rows = []
    for y in xs:
        row = []
        for x in xs:
            row.append(bm.verts.new((x, y, hill_h(x, y))))
        rows.append(row)
    for j in range(len(xs) - 1):
        for i in range(len(xs) - 1):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    me = bpy.data.meshes.new("ground")
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me); bm.free()
    me.materials.append(field_material())
    return link(bpy.data.objects.new("ground", me), coll)


def field_material():
    """prato curato: verdi variati + toppe di orto/campo a strisce, foschia calda in lontananza."""
    m = bpy.data.materials.new("field"); m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.95
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.02; n1.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], n1.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    ce = cr.color_ramp.elements
    ce[0].position = 0.35; ce[0].color = (*lin((0.30, 0.50, 0.22)), 1)
    ce[1].position = 0.62; ce[1].color = (*lin((0.50, 0.66, 0.28)), 1)
    nt.links.new(n1.outputs["Fac"], cr.inputs["Fac"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.9; n2.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], n2.inputs["Vector"])
    mx0 = nt.nodes.new("ShaderNodeMix"); mx0.data_type = 'RGBA'; mx0.inputs[0].default_value = 0.22
    nt.links.new(cr.outputs["Color"], mx0.inputs[6])
    mx0.inputs[7].default_value = (*lin((0.26, 0.42, 0.18)), 1)
    nt.links.new(n2.outputs["Fac"], mx0.inputs[0])
    # strisce di coltivazione (campi) a toppe, colori verde/verde-oliva (mai deserto giallo)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.35; wv.inputs["Distortion"].default_value = 0.6
    wv.wave_profile = 'SAW'
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    n3 = nt.nodes.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 0.008
    nt.links.new(tc.outputs["Object"], n3.inputs["Vector"])
    patch = nt.nodes.new("ShaderNodeMapRange"); patch.inputs["From Min"].default_value = 0.52; patch.inputs["From Max"].default_value = 0.58
    nt.links.new(n3.outputs["Fac"], patch.inputs["Value"])
    mxs = nt.nodes.new("ShaderNodeMix"); mxs.data_type = 'RGBA'
    mxs.inputs[6].default_value = (*lin((0.40, 0.58, 0.24)), 1)
    mxs.inputs[7].default_value = (*lin((0.56, 0.66, 0.30)), 1)
    nt.links.new(wv.outputs["Fac"], mxs.inputs[0])
    mxp = nt.nodes.new("ShaderNodeMix"); mxp.data_type = 'RGBA'
    nt.links.new(patch.outputs["Result"], mxp.inputs[0])
    nt.links.new(mx0.outputs[2], mxp.inputs[6]); nt.links.new(mxs.outputs[2], mxp.inputs[7])
    cd = nt.nodes.new("ShaderNodeCameraData")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 100.0; mr.inputs["From Max"].default_value = 1100.0; mr.inputs["To Max"].default_value = 0.4
    nt.links.new(cd.outputs["View Distance"], mr.inputs["Value"])
    hz = nt.nodes.new("ShaderNodeMix"); hz.data_type = 'RGBA'
    hz.inputs[7].default_value = (*lin((0.56, 0.70, 0.52)), 1)
    nt.links.new(mr.outputs["Result"], hz.inputs[0]); nt.links.new(mxp.outputs[2], hz.inputs[6])
    nt.links.new(hz.outputs[2], b.inputs["Base Color"])
    return m


def link(obj, coll):
    coll.objects.link(obj)
    return obj


def flat_quad_mesh(rects, z, m, name):
    """rettangoli (x0,y0,x1,y1) a quota z in una mesh unica con UV mondo."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    for (x0, y0, x1, y1) in rects:
        vs = [bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)), bm.verts.new((x1, y1, z)), bm.verts.new((x0, y1, z))]
        f = bm.faces.new(vs)
        for l in f.loops:
            l[uvl].uv = (l.vert.co.x, l.vert.co.y)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(m)
    return me


def camera_for(N, seed=7):
    """camera(N) continua, ALTA: 22 gradi (N=1) -> 30 gradi (N grande), prospettiva naturale, si allontana lentamente con N.
    N=1 inquadra il primo palazzo; poi il centro dell'inquadratura va sul centro dell'abitato.
    Ritorna (pos, target, lens, fstop, focus_dist)."""
    s0 = all_slots(seed)[0]
    sg = -1 if s0['side'] == 'W' else 1
    k = math.exp(-(N - 1) / 14.0)                                # peso del primo palazzo
    ext = 4.6 * math.sqrt(N)                                      # raggio dell'abitato (m)
    tx = (s0['xf'] - sg * 4.0) * k
    ty = s0['yc'] * k + 0.20 * ext * (1 - k) + 1.0
    tz = 4.6 + 0.012 * ext
    width = 17.0 + 5.0 * math.sqrt(N)                             # larghezza visibile al target (m)
    lens = 24.0 + 6.0 * (1 - math.exp(-N / 300.0))
    hfov = 2 * math.atan(12.0 * (9.0 / 16.0) / lens)   # sensor_fit VERTICAL usa sensor_height=24
    dist = width / (2 * math.tan(hfov / 2))
    el = math.radians(20.0 + 9.0 * (1 - math.exp(-N / 120.0)))
    az = math.radians(24.0 + 36.0 * math.exp(-(N - 1) / 6.0))
    sx = sg * (0.35 + 0.65 * k)                            # lato da cui si guarda: davanti alla facciata del primo palazzo
    pos = (tx + sx * dist * math.cos(el) * math.sin(az), ty - dist * math.cos(el) * math.cos(az), tz + dist * math.sin(el))
    tgt = (tx, ty, tz)
    fstop = 4.2
    return pos, tgt, lens, fstop, dist


# ---------------------------------------------------------------- scena
def build_scene(N, seed, res, samples):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    coll = sc.collection
    pos, tgt, lens, fstop, fdist = camera_for(N, seed)
    slots = all_slots(seed)[:N]
    big_ground(coll)

    # ---- strade: solo dove c'e' l'abitato (pezzo di viale + traverse tra lotti usati); il resto e' prato/orto
    ys0 = min(s['y0'] for s in slots)
    ys1 = max(s['y0'] + s['w'] for s in slots)
    rd0, rd1 = ys0 - 9.0, ys1 + 9.0
    road, paving = [(-2.5, rd0, 2.5, rd1)], [(-4.5, rd0, -2.5, rd1), (2.5, rd0, 4.5, rd1)]
    used = {(s['c'], s['r']) for s in slots}
    # strade laterali: x = PX*k dove affacciano lotti (W affaccia su xf-4.5, E su xf+4.5)
    side_roads = {}
    for s in slots:
        xr = round(s['xf'] - 4.5 if s['side'] == 'W' else s['xf'] + 4.5)
        if abs(xr) > 6:
            side_roads.setdefault(xr, []).append(s)
    for xr, lst in side_roads.items():
        a0 = min(q['y0'] for q in lst) - 3.0
        a1 = max(q['y0'] + q['w'] for q in lst) + 3.0
        road.append((xr - 2.5, a0, xr + 2.5, a1))
        paving.append((xr - 4.5, a0, xr - 2.5, a1)); paving.append((xr + 2.5, a0, xr + 4.5, a1))
    # traverse: solo tra lotti usati (fra due righe di isolati)
    xa = min(s['xf'] for s in slots) - 6.0
    xb = max(s['xf'] for s in slots) + 6.0
    for r in sorted({r for c, r in used}):
        ycen = PY * r + PY / 2
        above = [s for s in slots if s['yc'] > ycen + 2]
        below = [s for s in slots if s['yc'] < ycen - 2]
        if above and below and ycen > ys0 and ycen < ys1:
            road.append((xa, ycen - 2.0, xb, ycen + 2.0))
            for (ya, yb) in ((ycen - 3.5, ycen - 2.0), (ycen + 2.0, ycen + 3.5)):
                paving.append((xa, ya, -4.5, yb)); paving.append((4.5, ya, xb, yb))
    link(bpy.data.objects.new("road", flat_quad_mesh(road[:1], 0.02, m_asphalt(), "road")), coll)
    link(bpy.data.objects.new("paving2", flat_quad_mesh(paving, 0.14, m_paving(), "paving2")), coll)
    if len(road) > 1:
        link(bpy.data.objects.new("road2", flat_quad_mesh(road[1:], 0.03, m_asphalt(), "road2")), coll)
    # sentiero di terra battuta che prosegue nel prato, alle due estremita' del viale
    dirt = [(-1.3, rd1, 1.3, rd1 + 260.0), (-1.3, rd0 - 60.0, 1.3, rd0)]
    link(bpy.data.objects.new("track", flat_quad_mesh(dirt, 0.015, flat("dirt", (0.62, 0.50, 0.34), rough=0.95), "track")), coll)
    # lotti di selciato (piazzetta) + marciapiedi: ogni lotto ha il suo basamento in pietra, con un margine
    sb = MB()
    for s in slots:
        x0 = s['xf']
        if s['side'] == 'W':
            sb.box(x0 - SW, s['y0'] - 2.4, 0.0, x0 + BLK_D + 0.6, s['y0'] + s['w'] + 2.4, 0.14, m_paving())
        else:
            sb.box(x0 - BLK_D - 0.6, s['y0'] - 2.4, 0.0, x0 + SW, s['y0'] + s['w'] + 2.4, 0.14, m_paving())
    link(bpy.data.objects.new("sidewalks", sb.build("sidewalks")), coll)
    # rotaie del tram (solo quando c'e' il tram)
    if N >= 45:
        rb = MB()
        for xx in (0.95 - 0.72, 0.95 + 0.72):
            rb.box(xx - 0.03, rd0, 0.02, xx + 0.03, rd1, 0.07, m_rail())
        link(bpy.data.objects.new("rails", rb.build("rails")), coll)

    # ---- palazzi (mesh in cache, istanze)
    cache = {}
    cnt = 0
    PM = MB()
    for i, s in enumerate(slots):
        P = lot_params(s, seed)
        key = tuple(sorted(P.items())) + (s['lm'],)
        if key not in cache:
            if s['lm'] == 'tower':
                P2 = dict(P, w=8.4)
                cache[key] = mk_tower(P2).build("tower")
            elif s['lm'] == 'church':
                cache[key] = mk_church(dict(P, w=9.0)).build("church")
            else:
                cache[key] = mk_building(P).build(f"b{len(cache)}")
        o = link(bpy.data.objects.new(f"lot{i}", cache[key]), coll)
        rot = -math.pi / 2 if s['side'] == 'W' else math.pi / 2
        # centro frontale del lotto
        o.rotation_euler = (0, 0, rot)
        if s['side'] == 'W':
            o.location = (s['xf'], s['yc'], 0.14)
        else:
            o.location = (s['xf'], s['yc'], 0.14)
        o.matrix_world  # noqa
        cnt += 1
        # ---- props del lotto (nel mondo)
        rg = rgs(seed, 'prop', i)
        yc = s['yc']
        sg = -1 if s['side'] == 'W' else 1
        xcurb = s['xf'] + sg * (SW - 0.35)
        if i % 2 == 0:
            prop_lamp(PM, xcurb, s['y0'] + 0.5, 0.14)
        if i % 3 == 1:
            prop_tree(PM, xcurb, yc + rg.uniform(-0.5, 0.5), rg, 0.14)
        r_ = rg.random()
        xb = s['xf'] + sg * 0.7
        if r_ < 0.18 and s['w'] > 4.5:
            prop_bike(PM, s['xf'] + sg * 0.55, yc + rg.uniform(-0.6, 0.6), rg, 0.14)
        elif r_ < 0.34:
            prop_planter(PM, s['xf'] + sg * 0.5, yc + rg.uniform(-1.2, 1.2), rg)
        if rg.random() < 0.4:
            prop_person(PM, s['xf'] + sg * rg.uniform(0.9, 1.6), yc + rg.uniform(-2, 2), rg, 0.14)
        if rg.random() < 0.08:
            prop_bench(PM, s['xf'] + sg * 1.4, yc, 'y')
    # N=1: il primo palazzo ha lampione + albero + panca + vasi garantiti (piazzetta); poi i lotti seguono le regole fisse
    s0 = slots[0]
    sg0 = -1 if s0['side'] == 'W' else 1
    fr = rgs(seed, 'hero')
    prop_tree(PM, s0['xf'] + sg0 * (SW - 0.6), s0['y0'] - 1.7, fr, 0.14, big=1.15)
    prop_lamp(PM, s0['xf'] + sg0 * (SW - 0.35), s0['y0'] + s0['w'] + 0.6, 0.14)
    prop_bench(PM, s0['xf'] + sg0 * 1.3, s0['y0'] + s0['w'] + 3.0 if False else s0['y0'] - 2.4, 'y') if False else None
    prop_planter(PM, s0['xf'] + sg0 * 0.5, s0['y0'] + s0['w'] + 0.2, fr)
    # alberi sparsi nel prato attorno all'abitato (posizioni fisse, scartati se cadono sull'abitato)
    for q in range(90):
        tr_r = rgs(seed, 'meadow-trees', q)
        a_ = tr_r.uniform(0, 6.283); r_ = 30 + 160 * tr_r.random() ** 0.8
        tx_, ty_ = r_ * math.cos(a_) * 1.2, r_ * math.sin(a_) * 1.6
        if abs(tx_) < 8:
            tx_ += 14 if tx_ >= 0 else -14
        keep = all(abs(tx_ - q2['xf']) > 14 or not (q2['y0'] - 8 < ty_ < q2['y0'] + q2['w'] + 8) for q2 in slots)
        if keep and not any(abs(tx_ - q2['xf']) < 22 and abs(ty_ - q2['yc']) < 22 for q2 in slots):
            prop_tree(PM, tx_, ty_, tr_r, 0.0, big=tr_r.uniform(1.0, 1.9))
    if N >= 22:
        prop_cart(PM, 1.9, pos[1] + 20 + 0.2 * N ** 0.5 * 3, rgs(seed, 'cart'))
    if N >= 45:
        prop_tram(PM, 22.0 + 0.0, 0.95)
    if N >= 60:
        prop_fountain(PM, 0.0, PY / 2)
        for q in range(4):
            a = q * math.pi / 2 + 0.4
            prop_person(PM, 4.8 * math.cos(a), PY / 2 + 4.2 * math.sin(a), rgs(seed, 'pf', q), 0.0)
    if N >= 150:
        prop_cart(PM, -1.5, 60.0, rgs(seed, 'cart2'))
    link(bpy.data.objects.new("props", PM.build("props")), coll)
    if N >= 60:
        pb = MB()
        pb.cyl(0, PY / 2, 0.0, 0.03, 5.0, m_paving(), n=32, smooth=False)
        link(bpy.data.objects.new("plaza", pb.build("plaza")), coll)

    # ---- bokeh luminoso di sfondo: lanterne lontane (nessun fumo)
    # ---- luci: sole basso dorato (rim da dietro-destra) + fill caldo
    sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 4.6; sun.angle = math.radians(3.0)
    sun.color = (1.0, 0.72, 0.42)
    so = link(bpy.data.objects.new("sun", sun), coll)
    so.rotation_euler = (math.radians(72), 0, math.radians(-232))    # da dietro-destra, bassa
    fill = bpy.data.lights.new("fill", 'AREA')
    kk = max(1.0, (-pos[1]) / 30.0)
    fill.energy = 1200 * kk * kk; fill.size = 30 * kk
    fill.color = (1.0, 0.84, 0.70)
    fo = link(bpy.data.objects.new("fill", fill), coll)
    fo.location = (-30 * kk, pos[1] - 10 * kk, pos[2] + 14 * kk)
    tg = link(bpy.data.objects.new("tg", None), coll); tg.location = (0, tgt[1], 5)
    tr = fo.constraints.new('TRACK_TO'); tr.target = tg; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    sky_world(sc)

    # ---- camera con DOF
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens; cam.sensor_width = 36; cam.sensor_fit = 'VERTICAL'
    cam.clip_end = 8000; cam.clip_start = 0.3
    cam.dof.use_dof = True; cam.dof.aperture_fstop = fstop
    cam.dof.focus_distance = fdist
    co = link(bpy.data.objects.new("cam", cam), coll)
    co.location = pos
    tgo = link(bpy.data.objects.new("ctgt", None), coll); tgo.location = tgt
    tr = co.constraints.new('TRACK_TO'); tr.target = tgo; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    sc.camera = co
    r = sc.render; r.engine = 'CYCLES'; r.resolution_x, r.resolution_y = res; r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    cy = sc.cycles; cy.samples = samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03
    cy.use_denoising = True
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    cy.max_bounces = 5; cy.diffuse_bounces = 3; cy.glossy_bounces = 3; cy.transmission_bounces = 1
    cy.sample_clamp_indirect = 6; cy.device = 'CPU'
    for vt, lk in (('AgX', 'AgX - Medium High Contrast'), ('AgX', 'Medium High Contrast')):
        try:
            sc.view_settings.view_transform = vt; sc.view_settings.look = lk; break
        except Exception:
            pass
    print(f"[cozy5] N={N} lotti={cnt} mesh={len(cache)} cam={tuple(round(v, 1) for v in pos)} f/{fstop:.2f} {lens:.0f}mm build={time.time()-t0:.1f}s")
    return sc


def sky_world(sc):
    w = bpy.data.worlds.new("w"); sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nm = nt.nodes.new("ShaderNodeVectorMath"); nm.operation = 'NORMALIZE'
    nt.links.new(tc.outputs["Generated"], nm.inputs[0])
    nt.links.new(nm.outputs["Vector"], sp.inputs["Vector"])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY_ADD'
    ad.inputs[1].default_value = 0.5; ad.inputs[2].default_value = 0.5
    nt.links.new(sp.outputs["Z"], ad.inputs[0])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    ce = cr.color_ramp.elements
    ce[0].position = 0.50; ce[0].color = (*lin((1.0, 0.80, 0.50)), 1)
    e1 = ce.new(0.55); e1.color = (*lin((1.0, 0.76, 0.56)), 1)
    e2 = ce.new(0.66); e2.color = (*lin((0.80, 0.80, 0.84)), 1)
    ce[3].position = 0.85; ce[3].color = (*lin((0.46, 0.64, 0.88)), 1)
    nt.links.new(ad.outputs["Value"], cr.inputs["Fac"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 5
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 3.5)
    nt.links.new(nm.outputs["Vector"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    cl = nt.nodes.new("ShaderNodeMapRange"); cl.inputs["From Min"].default_value = 0.42; cl.inputs["From Max"].default_value = 0.62
    nt.links.new(nz.outputs["Fac"], cl.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[7].default_value = (*lin((1.0, 0.86, 0.68)), 1)
    nt.links.new(cl.outputs["Result"], mx.inputs[0]); nt.links.new(cr.outputs["Color"], mx.inputs[6])
    nt.links.new(mx.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.5


def grade(path, sat=1.08, contrast=1.04):
    try:
        import numpy as np
        from PIL import Image
        im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
        g = im.mean(axis=2, keepdims=True)
        im = np.clip(g + (im - g) * sat, 0, 1)
        im = np.clip((im - 0.5) * contrast + 0.5, 0, 1)
        Image.fromarray((im * 255 + 0.5).astype(np.uint8)).save(path)
    except Exception as e:
        print("[cozy5] grade saltato:", e)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--followers", type=int, default=111)
    ap.add_argument("--out", default="cozy4.png")
    ap.add_argument("--res", type=int, nargs=2, default=[540, 960])
    ap.add_argument("--samples", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--save-blend", default="")
    a = ap.parse_args(argv)
    sc = build_scene(a.followers, a.seed, tuple(a.res), a.samples)
    sc.render.filepath = a.out
    if a.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=a.save_blend)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"[cozy5] render {time.time()-t:.1f}s -> {a.out}")
    grade(a.out)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(argv)
