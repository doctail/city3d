"""Follower City - COZY v2.  N follower = N edifici in un paese immerso nella campagna.

Uso (pip bpy):   python cozy_city.py --followers 111 --out cozy2_111.png
Opzioni: --res 540 960  --samples 24  --seed 7  --gpu  --save-blend file.blend
v2: camera bassa che sale con N (camera(N) continua), fondale di campi/colline/cielo golden hour,
    edifici protagonisti (graticcio, mattoni, botteghe, torre dell'orologio...), nessuna isola/vasca.
Deterministico: un lotto (cella) ha sempre lo stesso aspetto; N sceglie solo quanti lotti, in ordine
dal centro, sono costruiti. I vecchi lotti non cambiano mai quando N cresce.
"""
import sys, math, random, time, argparse, zlib
import bpy, bmesh
from mathutils import Vector, Euler

C = 1.2           # lato cella (lotto)
ROAD_EVERY = 4    # strada ogni 4 celle: isolati 3x3 (8 case + cortile centrale)
FH = 0.46         # altezza piano


def lin(c):
    return tuple(x ** 2.2 for x in c)


WALLS = [(0.97, 0.90, 0.74), (0.95, 0.70, 0.55), (0.74, 0.82, 0.62), (0.66, 0.78, 0.88),
         (0.99, 0.86, 0.50), (0.94, 0.66, 0.66), (0.62, 0.84, 0.76), (0.97, 0.76, 0.45)]
ROOFS = [(0.74, 0.32, 0.22), (0.52, 0.31, 0.22), (0.36, 0.46, 0.62), (0.40, 0.58, 0.42),
         (0.84, 0.46, 0.25), (0.58, 0.34, 0.46), (0.30, 0.55, 0.58)]
SHUT = [(0.35, 0.58, 0.42), (0.30, 0.52, 0.74), (0.80, 0.28, 0.25), (0.93, 0.70, 0.25), (0.25, 0.62, 0.62), (0.92, 0.55, 0.62)]
AWN = [((0.86, 0.28, 0.26), (0.99, 0.93, 0.82)), ((0.30, 0.62, 0.42), (0.99, 0.93, 0.82)),
       ((0.30, 0.50, 0.78), (0.99, 0.93, 0.82)), ((0.95, 0.60, 0.20), (0.99, 0.93, 0.82)),
       ((0.92, 0.52, 0.64), (0.99, 0.93, 0.82)), ((0.96, 0.78, 0.25), (0.99, 0.95, 0.88))]
DOORS = [(0.55, 0.28, 0.20), (0.30, 0.50, 0.55), (0.78, 0.30, 0.25), (0.40, 0.58, 0.38), (0.92, 0.68, 0.25)]
FLOW = [(0.95, 0.30, 0.38), (0.99, 0.85, 0.30), (0.99, 0.97, 0.92), (0.72, 0.50, 0.90), (0.98, 0.58, 0.72)]
LEAVES = [(0.48, 0.66, 0.36), (0.38, 0.58, 0.38), (0.60, 0.72, 0.38), (0.93, 0.62, 0.66), (0.92, 0.55, 0.26),
          (0.33, 0.52, 0.42)]
SHIRTS = [(0.88, 0.32, 0.30), (0.30, 0.52, 0.80), (0.96, 0.78, 0.28), (0.36, 0.66, 0.46), (0.92, 0.56, 0.72), (0.98, 0.95, 0.88)]
SKIN = [(0.97, 0.78, 0.64), (0.82, 0.60, 0.44), (0.62, 0.44, 0.32)]

_mats = {}


def mat(name, rgb, rough=0.75, emit=None, strength=0.0, extra=None):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*lin(rgb), 1)
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*lin(emit), 1)
        bsdf.inputs["Emission Strength"].default_value = strength
    if extra:
        extra(nt, bsdf)
    _mats[name] = m
    return m


def tex_brick(scale, c1, c2, mortar, mw, bump, wall=False, w=0.5, h=0.25):
    """mattoni. wall=True: coordinate (x+y, z) -> funziona su tutte e 4 le pareti verticali."""
    def f(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale, scale, scale)
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.offset = 0.5
        br.inputs["Color1"].default_value = (*lin(c1), 1)
        br.inputs["Color2"].default_value = (*lin(c2), 1)
        br.inputs["Mortar"].default_value = (*lin(mortar), 1)
        br.inputs["Mortar Size"].default_value = mw
        br.inputs["Brick Width"].default_value = w
        br.inputs["Row Height"].default_value = h
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        if wall:
            sp = nt.nodes.new("ShaderNodeSeparateXYZ")
            ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'
            cb = nt.nodes.new("ShaderNodeCombineXYZ")
            nt.links.new(tc.outputs["Object"], sp.inputs["Vector"])
            nt.links.new(sp.outputs["X"], ad.inputs[0]); nt.links.new(sp.outputs["Y"], ad.inputs[1])
            nt.links.new(ad.outputs["Value"], cb.inputs["X"]); nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
            nt.links.new(cb.outputs["Vector"], mp.inputs["Vector"])
        else:
            nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
        nt.links.new(br.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return f


def tex_noise_color(scale, ca, cb):
    def f(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = 3
        cr = nt.nodes.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].color = (*lin(ca), 1)
        cr.color_ramp.elements[1].color = (*lin(cb), 1)
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    return f


# ---------------------------------------------------------------- mesh builder
class MB:
    def __init__(self):
        self.bm = bmesh.new()
        self.slots = []

    def slot(self, m):
        if m not in self.slots:
            self.slots.append(m)
        return self.slots.index(m)

    def part(self, verts, faces, m, bevel=0.0):
        """solido chiuso (liste verts/faces; m = materiale o lista per faccia)."""
        if bevel <= 0:
            vs = [self.bm.verts.new(v) for v in verts]
            for k, f in enumerate(faces):
                mm = m[k] if isinstance(m, (list, tuple)) else m
                fc = self.bm.faces.new([vs[i] for i in f])
                fc.material_index = self.slot(mm)
            # normali: orienta verso l'esterno (poche facce: ricalcolo locale)
            fs = [fc for fc in set(f for v in vs for f in v.link_faces)]
            bmesh.ops.recalc_face_normals(self.bm, faces=fs)
            return
        pb = bmesh.new()
        vs = [pb.verts.new(v) for v in verts]
        for k, f in enumerate(faces):
            fc = pb.faces.new([vs[i] for i in f])
            mm = m[k] if isinstance(m, (list, tuple)) else m
            fc.material_index = self.slot(mm)
        bmesh.ops.recalc_face_normals(pb, faces=pb.faces)
        bmesh.ops.bevel(pb, geom=list(pb.edges), offset=bevel, segments=2, affect='EDGES')
        mp = {v: self.bm.verts.new(v.co) for v in pb.verts}
        for f in pb.faces:
            nf = self.bm.faces.new([mp[v] for v in f.verts])
            nf.material_index = f.material_index
        pb.free()

    def box(self, x0, y0, z0, x1, y1, z1, m, bevel=0.0):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if z1 < z0: z0, z1 = z1, z0
        if bevel <= 0:
            i = self.slot(m)
            bm = self.bm
            v = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                           (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
            for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                bm.faces.new([v[k] for k in f]).material_index = i
            return
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        self.part(v, f, m, bevel)

    def bar(self, p0, p1, t1, t2, m, ref=(0, -1, 0)):
        """trave orientata p0->p1, sezione t1 x t2 (t1 lungo ref x asse)."""
        p0, p1 = Vector(p0), Vector(p1)
        d = (p1 - p0).normalized()
        s1 = d.cross(Vector(ref))
        if s1.length < 1e-4:
            s1 = d.cross(Vector((0, 0, 1)))
        s1 = s1.normalized() * (t1 / 2)
        s2 = d.cross(s1).normalized() * (t2 / 2)
        v = []
        for p in (p0, p1):
            for a, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                v.append(tuple(p + s1 * a + s2 * b_))
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        self.part(v, f, m)

    def cyl(self, cx, cy, z0, z1, r, m, n=10, r2=None, bevel=0.0, axis='z'):
        r2 = r if r2 is None else r2
        v = []
        for rad, zz in ((r, z0), (r2, z1)):
            for k in range(n):
                a = 2 * math.pi * k / n
                px, py = rad * math.cos(a), rad * math.sin(a)
                if axis == 'z':
                    v.append((cx + px, cy + py, zz))
                elif axis == 'y':      # asse lungo y (z0..z1 = y0..y1), cx = x, cy = z
                    v.append((cx + px, zz, cy + py))
                else:                  # asse lungo x, cx = y, cy = z
                    v.append((zz, cx + px, cy + py))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m, bevel)

    def sphere(self, cx, cy, cz, r, m, sub=1, sz=1.0, sx=1.0, sy=1.0):
        pb = bmesh.new()
        bmesh.ops.create_icosphere(pb, subdivisions=sub, radius=r)
        mp = {}
        for v in pb.verts:
            mp[v] = self.bm.verts.new((v.co.x * sx + cx, v.co.y * sy + cy, v.co.z * sz + cz))
        i = self.slot(m)
        for f in pb.faces:
            self.bm.faces.new([mp[v] for v in f.verts]).material_index = i
        pb.free()

    def cone(self, cx, cy, z0, z1, r, m, n=8):
        v = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z0) for k in range(n)]
        v.append((cx, cy, z1))
        f = [tuple(range(n - 1, -1, -1))] + [(k, (k + 1) % n, n) for k in range(n)]
        self.part(v, f, m)

    def build(self, name, smooth=False):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        for f in self.bm.faces:
            f.smooth = smooth
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.slots:
            me.materials.append(m)
        return me


# ---------------------------------------------------------------- materiali condivisi
def M_wall(i): return mat(f"wall{i}", WALLS[i], 0.85)
def M_roof(i):
    r = ROOFS[i]
    lighter = tuple(min(1, x * 1.14) for x in r)
    dark = tuple(x * 0.6 for x in r)
    return mat(f"roof{i}", r, 0.7, extra=tex_brick(14, r, lighter, dark, 0.06, 0.6))
def M_brick(i):
    cols = [((0.80, 0.42, 0.32), (0.72, 0.35, 0.27)), ((0.88, 0.60, 0.42), (0.80, 0.52, 0.36))][i]
    return mat(f"brickw{i}", cols[0], 0.85, extra=tex_brick(9, cols[0], cols[1], (0.95, 0.88, 0.76), 0.05, 0.5, True))
def M_shut(i): return mat(f"shut{i}", SHUT[i], 0.7)
def M_awn(i, k): return mat(f"awn{i}_{k}", AWN[i][k], 0.8)
def M_door(i): return mat(f"door{i}", DOORS[i], 0.6)
def M_flow(i): return mat(f"flw{i}", FLOW[i], 0.6)
M_TRIM = lambda: mat("trim", (0.99, 0.95, 0.86), 0.7)
M_TIMBER = lambda: mat("timber", (0.42, 0.26, 0.17), 0.8)
M_STONEW = lambda: mat("stonew", (0.90, 0.80, 0.64), 0.8)
M_WIN = lambda: mat("win", (1.0, 0.80, 0.42), 0.5, emit=(1.0, 0.68, 0.24), strength=6.5)
M_WIN2 = lambda: mat("win2", (0.95, 0.74, 0.45), 0.5, emit=(1.0, 0.62, 0.25), strength=2.2)
M_BRK = lambda: mat("chim", (0.68, 0.34, 0.25), 0.8)
M_TRUNK = lambda: mat("trunk", (0.45, 0.30, 0.20), 0.9)
def M_leaf(i): return mat(f"leaf{i}", LEAVES[i], 0.85)
M_STONE = lambda: mat("stone", (0.90, 0.80, 0.66), 0.7)
M_LAMP = lambda: mat("lamp", (1, 0.85, 0.5), 0.4, emit=(1.0, 0.72, 0.30), strength=12.0)
M_IRON = lambda: mat("iron", (0.32, 0.22, 0.20), 0.5)
M_WATERFX = lambda: mat("fountainw", (0.45, 0.78, 0.82), 0.1)
M_SMOKE = lambda: mat("smoke", (1.0, 0.94, 0.88), 0.9)
M_GOLD = lambda: mat("gold", (0.95, 0.76, 0.32), 0.8)
M_HAY = lambda: mat("hay", (0.96, 0.80, 0.38), 0.9)
M_WHITE = lambda: mat("white", (0.99, 0.96, 0.90), 0.8)
M_DARK = lambda: mat("darkb", (0.30, 0.20, 0.16), 0.6)
M_RED = lambda: mat("barnred", (0.78, 0.28, 0.22), 0.8)
M_CLOTH = lambda i: mat(f"cloth{i}", SHIRTS[i % len(SHIRTS)], 0.9)


# ---------------------------------------------------------------- pareti (frame 2D su una facciata)
class Wall:
    def __init__(self, kind, w, d):
        self.k = kind
        self.len = w if kind in "FB" else d
        self.off = d / 2 if kind in "FB" else w / 2

    def xy(self, u, o):
        k = self.k
        if k == 'F': return (u, -self.off - o)
        if k == 'B': return (-u, self.off + o)
        if k == 'L': return (-self.off - o, -u)
        return (self.off + o, u)

    def box(self, b, u0, u1, z0, z1, o0, o1, m, bevel=0.0):
        xa, ya = self.xy(u0, o0)
        xb, yb = self.xy(u1, o1)
        b.box(xa, ya, z0, xb, yb, z1, m, bevel)

    def prism(self, b, u0, u1, prof, m):
        """profilo [(o,z),...] estruso lungo u."""
        v = []
        for u in (u0, u1):
            for o, z in prof:
                x, y = self.xy(u, o)
                v.append((x, y, z))
        n = len(prof)
        f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        b.part(v, f, m)


def window(b, wl, u, zc, S, rg, kind='sq', eo=0.0, shut=True, flowers=True):
    ww, wh = (0.15, 0.21) if kind == 'sq' else (0.13, 0.28)
    trim = M_TRIM()
    lit = M_WIN() if rg.random() < 0.8 else M_WIN2()
    wl.box(b, u - ww / 2 - 0.022, u + ww / 2 + 0.022, zc - wh / 2 - 0.022, zc + wh / 2 + 0.022, eo, eo + 0.02, trim)
    wl.box(b, u - ww / 2, u + ww / 2, zc - wh / 2, zc + wh / 2, eo, eo + 0.03, lit)
    wl.box(b, u - 0.008, u + 0.008, zc - wh / 2, zc + wh / 2, eo + 0.03, eo + 0.04, trim)
    wl.box(b, u - ww / 2, u + ww / 2, zc - 0.008, zc + 0.008, eo + 0.03, eo + 0.04, trim)
    wl.box(b, u - ww / 2 - 0.04, u + ww / 2 + 0.04, zc - wh / 2 - 0.045, zc - wh / 2 - 0.018, eo, eo + 0.055, trim)
    if shut:
        sm = M_shut(S['shut'])
        for s in (-1, 1):
            uu = u + s * (ww / 2 + 0.022 + 0.04)
            wl.box(b, uu - 0.04, uu + 0.04, zc - wh / 2 - 0.02, zc + wh / 2 + 0.02, eo, eo + 0.028, sm)
            wl.box(b, uu - 0.03, uu + 0.03, zc - 0.004, zc + 0.004, eo + 0.028, eo + 0.034, trim)   # stecca
    if flowers:
        wl.box(b, u - 0.105, u + 0.105, zc - wh / 2 - 0.095, zc - wh / 2 - 0.04, eo, eo + 0.085, M_TIMBER())
        wl.box(b, u - 0.1, u + 0.1, zc - wh / 2 - 0.04, zc - wh / 2 + 0.0, eo + 0.01, eo + 0.075, M_leaf(0))
        fm = M_flow(rg.randrange(len(FLOW)))
        for q in range(4):
            uu = u - 0.075 + q * 0.05
            wl.box(b, uu - 0.017, uu + 0.017, zc - wh / 2 - 0.005, zc - wh / 2 + 0.032, eo + 0.03, eo + 0.065, fm)


def door(b, wl, u, S, rg, eo=0.0, w=0.19, h=0.30, glass=True):
    dm = M_door(S['door'])
    trim = M_TRIM()
    wl.box(b, u - w / 2 - 0.025, u + w / 2 + 0.025, 0.0, h + 0.025, eo, eo + 0.02, trim)
    wl.box(b, u - w / 2, u + w / 2, 0.0, h, eo, eo + 0.035, dm, 0.008)
    if glass:
        wl.box(b, u - 0.045, u + 0.045, h - 0.1, h - 0.03, eo + 0.035, eo + 0.045, M_WIN())
    wl.box(b, u + w / 2 - 0.045, u + w / 2 - 0.03, 0.13, 0.145, eo + 0.035, eo + 0.06, M_GOLD())   # maniglia
    # gradini
    for q in range(3):
        wl.box(b, u - w / 2 - 0.06, u + w / 2 + 0.06, 0.0, 0.035 * (3 - q), eo, eo + 0.05 + 0.05 * (q + 1), M_STONE())
    # tettuccio
    wl.prism(b, u - w / 2 - 0.07, u + w / 2 + 0.07, [(eo, h + 0.06), (eo + 0.14, h + 0.0), (eo + 0.14, h - 0.03), (eo, h + 0.03)], M_roof(S['roof']))
    # lanterna
    wl.box(b, u + w / 2 + 0.06, u + w / 2 + 0.1, h - 0.06, h - 0.02, eo, eo + 0.05, M_LAMP())


def awning(b, wl, u0, u1, z, S, eo=0.0, depth=0.20, drop=0.09, nstripes=None):
    w = u1 - u0
    n = nstripes or max(4, int(w / 0.07))
    sw = w / n
    for q in range(n):
        m = M_awn(S['awn'], q % 2)
        a, c = u0 + q * sw, u0 + (q + 1) * sw
        wl.prism(b, a, c, [(eo, z), (eo + depth, z - drop), (eo + depth, z - drop - 0.014), (eo, z - 0.014)], m)
        wl.box(b, a, c, z - drop - 0.035, z - drop, eo + depth - 0.004, eo + depth + 0.006, m)   # balza
    wl.box(b, u0 - 0.01, u0 + 0.008, z - drop - 0.02, z, eo, eo + depth, M_IRON())
    wl.box(b, u1 - 0.008, u1 + 0.01, z - drop - 0.02, z, eo, eo + depth, M_IRON())


def sign_board(b, wl, u, z, wlen, S, rg, eo=0.0, kind=None):
    pm = M_shut(rg.randrange(len(SHUT)))
    wl.box(b, u - wlen / 2, u + wlen / 2, z, z + 0.1, eo, eo + 0.03, pm, 0.006)
    wl.box(b, u - wlen / 2 - 0.012, u + wlen / 2 + 0.012, z - 0.012, z + 0.112, eo, eo + 0.018, M_TRIM())
    if kind == 'bread':
        wl.box(b, u - 0.09, u + 0.09, z + 0.025, z + 0.075, eo + 0.03, eo + 0.05, M_GOLD(), 0.012)
        for q in range(3):
            wl.box(b, u - 0.06 + q * 0.05, u - 0.045 + q * 0.05, z + 0.04, z + 0.06, eo + 0.05, eo + 0.056, M_BRK())
    else:   # lettere finte
        nL = rg.randint(4, 6)
        step = (wlen - 0.1) / nL
        for q in range(nL):
            uu = u - wlen / 2 + 0.06 + q * step
            hh = rg.choice([0.05, 0.06])
            wl.box(b, uu, uu + step * 0.6, z + 0.05 - hh / 2, z + 0.05 + hh / 2, eo + 0.03, eo + 0.045, M_TRIM())


def balcony(b, wl, uc, zb, S, eo=0.0, hw=0.25, dep=0.17):
    iron = M_IRON()
    wl.box(b, uc - hw - 0.015, uc + hw + 0.015, zb - 0.035, zb, eo, eo + dep, M_STONE(), 0.006)
    wl.box(b, uc - hw, uc + hw, zb + 0.105, zb + 0.122, eo + dep - 0.02, eo + dep - 0.004, iron)
    for s in (-1, 1):
        wl.box(b, uc + s * hw - 0.008, uc + s * hw + 0.008, zb + 0.105, zb + 0.122, eo, eo + dep, iron)
        wl.box(b, uc + s * hw - 0.008, uc + s * hw + 0.008, zb, zb + 0.122, eo + dep - 0.02, eo + dep - 0.004, iron)
    for q in range(1, 6):
        uu = uc - hw + q * (2 * hw / 6)
        wl.box(b, uu - 0.005, uu + 0.005, zb, zb + 0.108, eo + dep - 0.014, eo + dep - 0.008, iron)
    # vaso di fiori sul balcone
    wl.box(b, uc - 0.07, uc + 0.07, zb, zb + 0.05, eo + dep - 0.1, eo + dep - 0.03, M_TIMBER())
    fm = M_flow(S['flow'])
    for q in range(3):
        wl.box(b, uc - 0.06 + q * 0.05, uc - 0.03 + q * 0.05, zb + 0.05, zb + 0.095, eo + dep - 0.09, eo + dep - 0.045, fm)


def laundry(b, wl, u0, u1, z, rg, eo=0.0):
    b.__class__  # noqa
    wl.box(b, u0, u1, z, z + 0.006, eo + 0.05, eo + 0.056, M_IRON())
    for s in (u0, u1):
        wl.box(b, s - 0.008, s + 0.008, z - 0.08, z + 0.02, eo, eo + 0.06, M_TIMBER())
    n = 4
    step = (u1 - u0) / (n + 1)
    for q in range(n):
        uu = u0 + step * (q + 1)
        hh = rg.choice([0.07, 0.10])
        ww = rg.choice([0.05, 0.07])
        wl.box(b, uu - ww / 2, uu + ww / 2, z - hh, z, eo + 0.05, eo + 0.058, M_CLOTH(rg.randrange(6)))


def chimney(b, x, y, zt, zh, S, rg, smoke=True):
    b.box(x - 0.07, y - 0.07, zt - 0.05, x + 0.07, y + 0.07, zh, M_BRK(), 0.008)
    b.box(x - 0.09, y - 0.09, zh - 0.05, x + 0.09, y + 0.09, zh + 0.012, M_TRIM(), 0.008)
    if smoke:
        for k, (dz, r) in enumerate([(0.12, 0.055), (0.24, 0.075), (0.38, 0.095)]):
            b.sphere(x + 0.03 * k, y + 0.01 * k, zh + dz, r, M_SMOKE(), 1)


def roof_gable(b, w, d, zt, rh, o, rm, endm, along='x'):
    """tetto a due falde. along='x': colmo lungo x. along='y': colmo lungo y (frontone sul fronte)."""
    if along == 'x':
        x0, x1, y0, y1 = -w / 2 - o, w / 2 + o, -d / 2 - o, d / 2 + o
        v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (x0, 0, zt + rh), (x1, 0, zt + rh)]
        f = [(0, 3, 2, 1), (0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)]
        b.part(v, f, [endm, rm, rm, endm, endm], 0.016)
    else:
        x0, x1, y0, y1 = -w / 2 - o, w / 2 + o, -d / 2 - o, d / 2 + o
        v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (0, y0, zt + rh), (0, y1, zt + rh)]
        f = [(0, 3, 2, 1), (0, 4, 1), (3, 2, 5), (0, 3, 5, 4), (1, 4, 5, 2)]
        b.part(v, f, [endm, endm, endm, rm, rm], 0.016)


def roof_hip(b, w, d, zt, rh, o, rm, endm):
    x0, x1, y0, y1 = -w / 2 - o, w / 2 + o, -d / 2 - o, d / 2 + o
    l = max(0.0, (w - d) / 2)
    if l < 0.02:
        v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (0, 0, zt + rh)]
        f = [(0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    else:
        v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (-l, 0, zt + rh), (l, 0, zt + rh)]
        f = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)]
    b.part(v, f, rm, 0.014)


def dormer(b, xc, yf, zr, S, rg, w=0.26):
    """abbaino sul tetto: fronte (-y) a yf, base sul tetto a quota zr."""
    wallm = M_wall(S['wall'])
    z1 = zr + 0.24
    b.box(xc - w / 2, yf, zr - 0.06, xc + w / 2, yf + 0.3, z1, wallm, 0.008)
    wl = Wall('F', 0, 0)
    # finestra sul fronte dell'abbaino
    b.box(xc - 0.065, yf - 0.03, zr + 0.03, xc + 0.065, yf, z1 - 0.045, M_WIN())
    b.box(xc - 0.075, yf - 0.012, zr + 0.022, xc + 0.075, yf, z1 - 0.036, M_TRIM())
    b.box(xc - 0.005, yf - 0.036, zr + 0.03, xc + 0.005, yf - 0.03, z1 - 0.045, M_TRIM())
    ov = 0.05
    v = [(xc - w / 2 - ov, yf - ov, z1), (xc + w / 2 + ov, yf - ov, z1), (xc + w / 2 + ov, yf + 0.3, z1), (xc - w / 2 - ov, yf + 0.3, z1),
         (xc, yf - ov, z1 + 0.14), (xc, yf + 0.3, z1 + 0.14)]
    f = [(0, 3, 2, 1), (0, 4, 1), (3, 2, 5), (0, 3, 5, 4), (1, 4, 5, 2)]
    b.part(v, f, [M_TRIM(), M_TRIM(), M_TRIM(), M_roof(S['roof2']), M_roof(S['roof2'])], 0.01)


# ---------------------------------------------------------------- edifici
_mesh_cache = {}


def house_mesh(st):
    key = ("h",) + tuple(sorted(st.items()))
    if key in _mesh_cache:
        return _mesh_cache[key]
    rg = random.Random(zlib.crc32(repr(key).encode()))
    style, w, d, fl = st['style'], st['w'], st['d'], st['fl']
    S = dict(wall=st['wi'], roof=st['ri'], roof2=st['ri'], shut=st['sh'], door=st['dr'], awn=st['aw'], flow=st['fw'])
    b = MB()
    trim, timber, stone = M_TRIM(), M_TIMBER(), M_STONE()
    shop = style in ('shop', 'bakery')
    gfh = 0.54 if shop else (0.50 if style == 'brick' else FH)
    heights = [gfh] + [FH] * (fl - 1)
    zt = sum(heights)
    jet = 0.07 if style == 'timber' else 0.0
    wallm = M_wall(S['wall'])
    brick = M_brick(st['bk']) if style == 'brick' else None
    # ----- corpo, piano per piano
    z0 = 0.0
    for k, hk in enumerate(heights):
        z1 = z0 + hk
        if style == 'brick':
            wm = brick if k < fl - 1 or fl <= 3 else wallm
        elif shop and k == 0:
            wm = M_wall((S['wall'] + 3) % len(WALLS))
        elif style == 'cottage' and k == 0:
            wm = wallm
        else:
            wm = wallm
        fo = jet if k >= 1 else 0.0
        b.box(-w / 2, -d / 2 - fo, z0, w / 2, d / 2, z1, wm, 0.012)
        if k < fl - 1:
            b.box(-w / 2 - 0.018, -d / 2 - fo - 0.018, z1 - 0.022, w / 2 + 0.018, d / 2 + 0.018, z1 + 0.014, trim, 0.006)
        z0 = z1
    b.box(-w / 2 - 0.02, -d / 2 - 0.02, 0, w / 2 + 0.02, d / 2 + 0.02, 0.07, stone, 0.01)   # zoccolo
    if style in ('brick', 'tall', 'shop', 'bakery'):   # cantonali chiari
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.box(sx * w / 2 - 0.022 + 0 * sx, sy * d / 2 - 0.022, 0, sx * w / 2 + 0.022, sy * d / 2 + 0.022, zt, trim) if False else None
    # ----- tetto
    rkind = st['roof']
    rh = st['rh']
    o = 0.08
    rm = M_roof(S['roof'])
    if rkind == 'gy':      # frontone
        roof_gable(b, w, d, zt, rh, o, rm, M_wall(S['wall']) if style != 'tall' else trim, 'y')
        # modanatura sul bordo spiovente
        for s in (-1, 1):
            b.bar((s * (w / 2 + o), -d / 2 - o - 0.012, zt), (0, -d / 2 - o - 0.012, zt + rh), 0.045, 0.02, trim, ref=(0, 1, 0))
        # finestra del sottotetto
        gw = Wall('F', w, d)
        window(b, gw, 0.0, zt + rh * 0.34, S, rg, 'sq', eo=o + 0.0, shut=True, flowers=False)
        if style == 'tall':   # gradoni olandesi
            yy = -d / 2 - o - 0.02
            for q, (ww_, hh_) in enumerate([(w * 0.46, rh * 0.82), (w * 0.72, rh * 0.5), (w + 2 * o - 0.02, rh * 0.2)]):
                b.box(-ww_ / 2, yy, zt, ww_ / 2, yy + 0.05, zt + hh_, M_wall(S['wall']), 0.008)
                b.box(-ww_ / 2 - 0.012, yy - 0.006, zt + hh_ - 0.004, ww_ / 2 + 0.012, yy + 0.056, zt + hh_ + 0.022, trim, 0.005)
    elif rkind == 'gx':
        roof_gable(b, w, d, zt, rh, o, rm, trim, 'x')
        nd = 1 if w < 1.0 else 2
        for q in range(nd):
            xc = (0 if nd == 1 else (-1 if q == 0 else 1) * w * 0.24)
            yf = -d / 2 - o + (o + d / 2) * 0.42 - 0.12
            zr = zt + rh * (1 - (abs(yf) / (d / 2 + o)))
            if rg.random() < 0.8 or style == 'tall':
                dormer(b, xc, yf, zr, S, rg)
    else:   # hip
        roof_hip(b, w, d, zt, rh, o, rm, trim)
        if fl >= 2 and rg.random() < 0.6:
            yf = -d / 2 - o + (o + d / 2) * 0.46 - 0.12
            zr = zt + rh * (1 - (abs(yf) / (d / 2 + o)))
            dormer(b, 0.0, yf, zr, S, rg)
    # ----- facciate
    F, Bk, Lw, Rw = Wall('F', w, d), Wall('B', w, d), Wall('L', w, d), Wall('R', w, d)
    ud = st['ud']   # posizione porta sul fronte
    zs = [0.0]
    for hk in heights: zs.append(zs[-1] + hk)
    nx = max(1, int(round(w / 0.40)))
    for k in range(fl):
        zc = zs[k] + heights[k] * 0.56 + (0.02 if k == 0 else 0)
        fo = jet if k >= 1 else 0.0
        for wl, ln, nn in ((F, w, nx), (Bk, w, nx)):
            for i in range(nn):
                u = (i - (nn - 1) / 2) * (ln / nn)
                if wl is F and k == 0 and abs(u - ud) < 0.22:
                    continue
                if shop and wl is F and k == 0:
                    continue
                if wl is F and k >= 1 and st.get('bal') and k == 1 and abs(u) < 0.2:
                    continue
                kind = 'tall' if (style in ('tall', 'brick') and k >= 1 and rg.random() < 0.4) else 'sq'
                if wl is F and k == 0 and style == 'timber':
                    pass
                window(b, wl, u, zc if kind == 'sq' else zc + 0.02, S, rg, kind, eo=fo if wl is F else 0.0,
                       shut=(rg.random() < 0.85), flowers=(rg.random() < 0.45 and kind == 'sq'))
        ny = max(1, int(round(d / 0.52)))
        for wl in (Lw, Rw):
            for j in range(ny):
                u = (j - (ny - 1) / 2) * (d / ny)
                window(b, wl, u, zc, S, rg, 'sq', shut=False, flowers=(rg.random() < 0.2))
    # porta e pianterreno negozio
    if shop:
        zbot, ztop = 0.11, 0.40
        side = 1 if ud >= 0 else -1
        ua, ub = (-w / 2 + 0.07, ud - side * 0.0) if side > 0 else (ud, w / 2 - 0.07)
        # vetrina
        if side > 0:
            u0, u1 = -w / 2 + 0.09, ud - 0.17
        else:
            u0, u1 = ud + 0.17, w / 2 - 0.09
        F.box(b, u0 - 0.02, u1 + 0.02, zbot - 0.02, ztop + 0.02, 0, 0.02, trim)
        F.box(b, u0, u1, zbot, ztop, 0, 0.03, M_WIN())
        nm = max(2, int((u1 - u0) / 0.12))
        for q in range(1, nm):
            uu = u0 + q * (u1 - u0) / nm
            F.box(b, uu - 0.006, uu + 0.006, zbot, ztop, 0.03, 0.04, trim)
        F.box(b, u0 - 0.02, u1 + 0.02, zbot - 0.06, zbot - 0.015, 0, 0.05, M_shut(S['shut']))   # davanzale/ base vetrina
        for q in range(3):    # merce in vetrina
            uu = u0 + (q + 0.5) * (u1 - u0) / 3
            F.box(b, uu - 0.03, uu + 0.03, zbot, zbot + 0.05, 0.03, 0.09, M_flow(rg.randrange(5)) if style == 'shop' else M_GOLD(), 0.01)
        door(b, F, ud, S, rg, 0.0, 0.19, 0.34)
        awning(b, F, u0 - 0.03, u1 + 0.03, 0.47, S, 0.0, 0.21, 0.09)
        sign_board(b, F, 0.0 if rg.random() < 0.5 else (u0 + u1) / 2, 0.48 + 0.012, min(0.6, w - 0.2), S, rg, 0.0, 'bread' if style == 'bakery' else None)
        # vasi, botti, cassette sul marciapiede
        pu = u1 + 0.06 if side > 0 else u0 - 0.06
        b.cyl(pu if False else F.xy(pu, 0.14)[0], F.xy(pu, 0.14)[1], 0, 0.1, 0.055, M_door(rg.randrange(5)), 8, r2=0.045)
        b.sphere(F.xy(pu, 0.14)[0], F.xy(pu, 0.14)[1], 0.14, 0.07, M_leaf(rg.randrange(3)), 1)
        b.cyl(F.xy(-ud * 0.8, 0.2)[0], F.xy(-ud * 0.8, 0.2)[1], 0, 0.14, 0.065, timber, 8)
        if style == 'bakery':
            for q in range(3):   # panini sul bancone
                F.box(b, -0.2 + q * 0.07, -0.15 + q * 0.07, 0.30, 0.325, 0.2, 0.25, M_GOLD(), 0.01) if False else None
    else:
        door(b, F, ud, S, rg, 0.0)
    # timbering (graticcio) su fronte e lati
    if style == 'timber':
        for wl, ln in ((F, w), (Bk, w), (Lw, d), (Rw, d)):
            fo = jet if wl is F else 0.0
            for k in range(1, fl):
                za, zb = zs[k], zs[k + 1]
                for i in range(int(round(ln / 0.4)) + 1):
                    u = -ln / 2 + 0.03 + i * (ln - 0.06) / int(round(ln / 0.4))
                    wl.box(b, u - 0.017, u + 0.017, za + 0.02, zb - 0.01, fo, fo + 0.026, timber)
                wl.box(b, -ln / 2, ln / 2, za, za + 0.04, fo, fo + 0.03, timber)
                if k < fl:
                    wl.box(b, -ln / 2, ln / 2, zb - 0.045, zb, fo, fo + 0.03, timber)
                # diagonali ai lati dei pannelli
                for s in (-1, 1):
                    b.bar(wl.xy(s * (ln / 2 - 0.03), fo + 0.016) + (za + 0.04,), wl.xy(s * (ln / 2 - 0.15), fo + 0.016) + (zb - 0.05,),
                          0.026, 0.02, timber, ref=(0, 0, 1)) if False else None
        # travi del piano terra solo ai cantonali
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.box(sx * w / 2 - 0.02, sy * d / 2 - 0.02, 0.0, sx * w / 2 + 0.02, sy * d / 2 + 0.02, zs[1], timber)
    # balcone
    if st.get('bal') and fl >= 2 and style != 'cottage':
        balcony(b, F, 0.0, zs[1] + 0.02, S, jet if style == 'timber' else 0.0)
        F.box(b, -0.075, 0.075, zs[1] + 0.03, zs[1] + 0.30, jet, jet + 0.03, M_door(S['door'])) if style != 'timber' else None
        F.box(b, -0.06, 0.06, zs[1] + 0.05, zs[1] + 0.28, jet + 0.03, jet + 0.04, M_WIN())
    # insegna perpendicolare (bandiera) e panni stesi
    if st.get('laundry') and fl >= 2:
        laundry(b, Rw, -d / 2 + 0.12, d / 2 - 0.12, zs[2] - 0.12, rg, 0.0)
    if st.get('flag'):
        F.box(b, w / 2 - 0.1, w / 2 - 0.09, zs[1] + 0.05, zs[1] + 0.5, 0.0, 0.01, M_IRON()) if False else None
    # camini
    if st['chim'] and rkind != 'hip' or st['chim'] and style == 'bakery':
        cx = w * 0.27 * st['chs']
        zh = zt + rh * 0.9 + 0.1
        chimney(b, cx, 0.0 if rkind == 'gx' else d * 0.12, zt, zh, S, rg, smoke=st['smoke'])
    elif st['chim']:
        chimney(b, w * 0.2 * st['chs'], 0.0, zt, zt + rh * 0.75 + 0.1, S, rg, smoke=st['smoke'])
    me = b.build("house")
    _mesh_cache[key] = me
    return me


def clock_tower_mesh(S0=0):
    key = ("clock",)
    if key in _mesh_cache:
        return _mesh_cache[key]
    b = MB()
    S = dict(wall=4, roof=0, roof2=0, shut=0, door=0, awn=0, flow=0)
    rg = random.Random(5)
    trim, stone = M_TRIM(), M_STONE()
    brick = M_brick(1)
    w = 0.82
    hs = [0.62, 0.5, 0.5, 0.5]
    z0 = 0.0
    for k, h in enumerate(hs):
        b.box(-w / 2, -w / 2, z0, w / 2, w / 2, z0 + h, brick if k else stone, 0.012)
        b.box(-w / 2 - 0.02, -w / 2 - 0.02, z0 + h - 0.025, w / 2 + 0.02, w / 2 + 0.02, z0 + h + 0.012, trim, 0.006)
        z0 += h
    zt = z0
    # finestrelle e portone
    for wl in (Wall('F', w, w), Wall('B', w, w), Wall('L', w, w), Wall('R', w, w)):
        for k in (1, 2):
            window(b, wl, 0.0, sum(hs[:k]) + hs[k] * 0.55, S, rg, 'tall', shut=True, flowers=False)
    F = Wall('F', w, w)
    door(b, F, 0.0, S, rg, 0.0, 0.24, 0.38)
    # orologio sulle 4 facce (ultimo piano)
    zc = sum(hs[:3]) + hs[3] * 0.5
    for wl, ax in ((Wall('F', w, w), 'y'), (Wall('B', w, w), 'y'), (Wall('L', w, w), 'x'), (Wall('R', w, w), 'x')):
        x, y = wl.xy(0.0, 0.0)
        sgn = -1 if wl.k in 'FL' else 1
        if ax == 'y':
            b.cyl(x, zc, y + sgn * 0.0, y + sgn * 0.035, 0.17, trim, 16, axis='y')
            b.cyl(x, zc, y + sgn * 0.035, y + sgn * 0.05, 0.145, M_WHITE(), 16, axis='y')
            b.box(x - 0.008, y + sgn * 0.05, zc, x + 0.008, y + sgn * 0.058, zc + 0.12, M_DARK())
            b.box(x, y + sgn * 0.05, zc - 0.008, x + 0.085, y + sgn * 0.058, zc + 0.008, M_DARK())
        else:
            b.cyl(y, zc, x + sgn * 0.0, x + sgn * 0.035, 0.17, trim, 16, axis='x')
            b.cyl(y, zc, x + sgn * 0.035, x + sgn * 0.05, 0.145, M_WHITE(), 16, axis='x')
            b.box(x + sgn * 0.05, y - 0.008, zc, x + sgn * 0.058, y + 0.008, zc + 0.12, M_DARK())
            b.box(x + sgn * 0.05, y, zc - 0.008, x + sgn * 0.058, y + 0.085, zc + 0.008, M_DARK())
    # cella campanaria: 4 pilastri + campana
    bh = 0.34
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box(sx * 0.33 - 0.04, sy * 0.33 - 0.04, zt, sx * 0.33 + 0.04, sy * 0.33 + 0.04, zt + bh, stone, 0.006)
    b.box(-w / 2 - 0.03, -w / 2 - 0.03, zt, w / 2 + 0.03, w / 2 + 0.03, zt + 0.03, trim, 0.006)
    b.sphere(0, 0, zt + 0.2, 0.09, M_GOLD(), 1, 1.2)
    b.box(-w / 2 - 0.06, -w / 2 - 0.06, zt + bh, w / 2 + 0.06, w / 2 + 0.06, zt + bh + 0.04, trim, 0.006)
    # guglia
    zs_ = zt + bh + 0.04
    v = [(-w / 2 - 0.1, -w / 2 - 0.1, zs_), (w / 2 + 0.1, -w / 2 - 0.1, zs_), (w / 2 + 0.1, w / 2 + 0.1, zs_), (-w / 2 - 0.1, w / 2 + 0.1, zs_), (0, 0, zs_ + 0.7)]
    f = [(0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    b.part(v, f, M_roof(0), 0.012)
    b.cyl(0, 0, zs_ + 0.7, zs_ + 0.98, 0.012, M_GOLD(), 6)
    b.sphere(0, 0, zs_ + 0.98, 0.035, M_GOLD(), 1)
    b.box(0.0, -0.005, zs_ + 0.9, 0.16, 0.005, zs_ + 0.97, M_RED())     # bandierina
    me = b.build("clock")
    _mesh_cache[key] = me
    return me


def tree_mesh(kind, ci):
    key = ("t", kind, ci)
    if key in _mesh_cache:
        return _mesh_cache[key]
    b = MB()
    leaf, trunk = M_leaf(ci), M_TRUNK()
    if kind == "round":
        b.cyl(0, 0, 0, 0.35, 0.06, trunk, 6)
        b.sphere(0, 0, 0.62, 0.34, leaf, 2, 1.1)
    elif kind == "double":
        b.cyl(0, 0, 0, 0.45, 0.07, trunk, 6)
        b.sphere(0, 0, 0.62, 0.38, leaf, 2, 1.0)
        b.sphere(0.05, 0.03, 1.0, 0.27, leaf, 2, 1.0)
    elif kind == "pine":
        b.cyl(0, 0, 0, 0.25, 0.06, trunk, 6)
        for r, z in [(0.34, 0.2), (0.27, 0.45), (0.2, 0.7)]:
            b.cone(0, 0, z, z + 0.38, r, leaf, 8)
    elif kind == "poplar":
        b.cyl(0, 0, 0, 0.3, 0.05, trunk, 6)
        b.sphere(0, 0, 0.9, 0.24, leaf, 2, 2.4)
    elif kind == "round_big":
        b.cyl(0, 0, 0, 0.5, 0.09, trunk, 6)
        b.sphere(0, 0, 0.95, 0.55, leaf, 2, 1.0)
        b.sphere(0.25, 0.1, 0.8, 0.32, leaf, 1, 1.0)
    else:
        b.sphere(0, 0, 0.12, 0.22, leaf, 1, 0.8)
        b.sphere(0.17, 0.05, 0.1, 0.15, leaf, 1, 0.8)
    me = b.build("tree")
    _mesh_cache[key] = me
    return me


def prop_mesh(kind, ci=0):
    key = ("p", kind, ci)
    if key in _mesh_cache:
        return _mesh_cache[key]
    b = MB()
    rg = random.Random(ci * 17 + 3)
    if kind == "lamp":
        b.cyl(0, 0, 0, 0.1, 0.06, M_IRON(), 6)
        b.cyl(0, 0, 0, 0.75, 0.022, M_IRON(), 6)
        b.sphere(0, 0, 0.82, 0.07, M_LAMP(), 1)
    elif kind == "person":
        b.cyl(0, 0, 0.0, 0.1, 0.045, M_CLOTH(ci), 6, r2=0.03)
        b.cyl(0, 0, 0.1, 0.14, 0.03, M_CLOTH(ci), 6)
        b.sphere(0, 0, 0.17, 0.034, mat(f"skin{ci % 3}", SKIN[ci % 3], 0.8), 1)
        if ci % 2 == 0:
            b.cyl(0, 0, 0.19, 0.2, 0.05, M_flow(ci % 5), 6)
    elif kind == "cart":
        b.box(-0.2, -0.1, 0.1, 0.2, 0.1, 0.14, M_TIMBER())
        for s in (-1, 1):
            b.box(-0.2, s * 0.1 - 0.008, 0.14, 0.2, s * 0.1 + 0.008, 0.22, M_TIMBER())
            b.cyl(0.0 + s * 0.12, 0.075, -0.115, -0.1, 0.075, M_DARK(), 10, axis='y')
            b.cyl(0.0 + s * 0.12, 0.075, 0.1, 0.115, 0.075, M_DARK(), 10, axis='y')
        b.sphere(0, 0, 0.17, 0.13, M_HAY() if ci % 2 == 0 else M_leaf(0), 1, 0.7, 1.2, 0.9)
        b.box(0.2, -0.015, 0.1, 0.4, 0.015, 0.12, M_TIMBER())
    elif kind == "barrel":
        b.cyl(0, 0, 0, 0.14, 0.065, M_TIMBER(), 8, r2=0.065)
    elif kind == "bale":
        b.cyl(0, 0.28, -0.22, 0.22, 0.28, M_HAY(), 12, axis='y')
        b.cyl(0, 0.28, -0.23, -0.21, 0.29, M_GOLD(), 12, axis='y')
        b.cyl(0, 0.28, 0.21, 0.23, 0.29, M_GOLD(), 12, axis='y')
    elif kind == "stack":
        b.cyl(0, 0, 0, 0.25, 0.28, M_HAY(), 8, r2=0.28)
        b.cone(0, 0, 0.25, 0.85, 0.28, M_HAY(), 8)
    elif kind == "sheep":
        wm = M_WHITE()
        b.sphere(0, 0, 0.17, 0.14, wm, 1, 0.85, 1.25, 1.0)
        b.sphere(0.17, 0, 0.2, 0.065, mat("sheephead", (0.35, 0.26, 0.2), 0.8), 1)
        for sx in (-0.07, 0.08):
            for sy in (-0.05, 0.05):
                b.cyl(sx, sy, 0, 0.08, 0.016, mat("sheephead", (0.35, 0.26, 0.2), 0.8), 5)
    elif kind == "barn":
        bw, bd, bh = 1.7, 1.1, 0.8
        b.box(-bw / 2, -bd / 2, 0, bw / 2, bd / 2, bh, M_RED(), 0.02)
        roof_gable(b, bw, bd, bh, 0.55, 0.1, mat("barnroof", (0.52, 0.31, 0.24), 0.8), M_RED(), 'x')
        b.box(-0.25, -bd / 2 - 0.02, 0, 0.25, -bd / 2, 0.62, M_TRIM(), 0.01)
        b.box(-0.21, -bd / 2 - 0.03, 0.0, 0.21, -bd / 2 - 0.01, 0.58, M_RED())
        b.bar((-0.21, -bd / 2 - 0.035, 0.0), (0.21, -bd / 2 - 0.035, 0.58), 0.04, 0.012, M_TRIM(), ref=(0, -1, 0))
        b.bar((0.21, -bd / 2 - 0.035, 0.0), (-0.21, -bd / 2 - 0.035, 0.58), 0.04, 0.012, M_TRIM(), ref=(0, -1, 0))
        b.box(-bw / 2 - 0.02, -bd / 2 - 0.01, 0, -bw / 2 + 0.04, -bd / 2 + 0.03, bh, M_TRIM())
        b.box(bw / 2 - 0.04, -bd / 2 - 0.01, 0, bw / 2 + 0.02, -bd / 2 + 0.03, bh, M_TRIM())
        b.box(-0.06, -bd / 2 - 0.02, 0.72, 0.06, -bd / 2 - 0.01, 0.84, M_TRIM())   # finestrella fienile
        b.cyl(0.95, 0.35, 0, 1.0, 0.24, M_STONEW(), 10, r2=0.24)                    # silo
        b.sphere(0.95, 0.35, 1.0, 0.24, mat("silotop", (0.78, 0.40, 0.30), 0.7), 2, 0.7)
    elif kind == "mill":
        b.cyl(0, 0, 0, 1.5, 0.52, M_STONEW(), 10, r2=0.34, bevel=0.0)
        b.box(-0.12, -0.52, 0, 0.12, -0.4, 0.4, M_door(0), 0.01)
        b.cone(0, 0, 1.5, 2.05, 0.46, M_roof(0), 10)
        hub = (0, -0.5, 1.55)
        b.sphere(0, -0.42, 1.55, 0.09, M_TIMBER(), 1)
        for q in range(4):
            a = math.radians(20 + q * 90)
            tip = (hub[0] + 1.35 * math.cos(a), hub[1] - 0.06, hub[2] + 1.35 * math.sin(a))
            b.bar(hub, tip, 0.03, 0.03, M_TIMBER(), ref=(0, -1, 0))
            # tela
            p0 = Vector((0.16 * math.cos(a), hub[1] - 0.07, hub[2] + 0.16 * math.sin(a)))
            p1 = Vector((1.3 * math.cos(a), hub[1] - 0.07, hub[2] + 1.3 * math.sin(a)))
            off = Vector((-math.sin(a), 0, math.cos(a))) * 0.17
            c0, c1 = Vector((p0.x, p0.y, p0.z)), Vector((p1.x, p1.y, p1.z))
            v = [tuple(c0 + off * 0.3), tuple(c1 + off * 0.3), tuple(c1 + off * 1.0), tuple(c0 + off * 1.0)]
            v2 = [(x, y - 0.012, z) for x, y, z in v]
            b.part(v + v2, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], M_TRIM())
    elif kind == "well":
        b.cyl(0, 0, 0, 0.18, 0.2, M_STONE(), 10, bevel=0.01)
        b.cyl(0, 0, 0.15, 0.19, 0.15, M_WATERFX(), 10)
        for s in (-1, 1):
            b.box(s * 0.2 - 0.015, -0.015, 0.18, s * 0.2 + 0.015, 0.015, 0.5, M_TIMBER())
        roof_gable(b, 0.5, 0.3, 0.5, 0.18, 0.03, M_roof(0), M_TRIM(), 'x')
    elif kind == "veg":
        b.box(-0.45, -0.35, 0, 0.45, 0.35, 0.025, mat("soil", (0.60, 0.40, 0.28), 0.95))
        for q in range(4):
            y = -0.27 + q * 0.18
            b.box(-0.4, y - 0.04, 0.025, 0.4, y + 0.04, 0.07, mat("rowg", [(0.42, 0.64, 0.32), (0.55, 0.72, 0.34), (0.86, 0.5, 0.3), (0.70, 0.78, 0.40)][q % 4], 0.9), 0.01)
    elif kind == "court":
        b.cyl(0, 0, 0, 0.02, 0.5, mat("courtg", (0.60, 0.74, 0.40), 0.9), 12)
        b.cyl(0.0, -0.1, 0, 0.35, 0.05, M_TRUNK(), 6)
        b.sphere(0, -0.1, 0.65, 0.32, M_leaf(ci % 6), 2, 1.05)
    elif kind == "fountain":
        st, wt = M_STONE(), M_WATERFX()
        b.cyl(0, 0, 0, 0.22, 0.62, st, 16, bevel=0.02)
        b.cyl(0, 0, 0.18, 0.25, 0.52, wt, 16)
        b.cyl(0, 0, 0.2, 0.55, 0.09, st, 8)
        b.cyl(0, 0, 0.5, 0.58, 0.28, st, 12, bevel=0.015)
        b.cyl(0, 0, 0.56, 0.62, 0.24, wt, 12)
    elif kind == "fence":
        for q in range(4):
            x = -0.45 + q * 0.3
            b.box(x - 0.02, -0.02, 0, x + 0.02, 0.02, 0.2, M_TRIM(), 0.004)
        b.box(-0.47, -0.012, 0.06, 0.47, 0.012, 0.085, M_TRIM())
        b.box(-0.47, -0.012, 0.13, 0.47, 0.012, 0.155, M_TRIM())
        for q in range(9):
            x = -0.42 + q * 0.105
            b.box(x - 0.014, -0.006, 0.0, x + 0.014, 0.006, 0.17, M_TRIM())
    elif kind == "flowers":
        g = M_leaf(0)
        fm = M_flow(ci % 5)
        b.sphere(0, 0, 0.04, 0.16, g, 1, 0.5)
        for k in range(5):
            b.sphere(rg.uniform(-0.15, 0.15), rg.uniform(-0.15, 0.15), 0.11, 0.035, fm, 1)
    me = b.build(kind)
    _mesh_cache[key] = me
    return me


# ---------------------------------------------------------------- scena
def hrand(seed, i, j, salt=0):
    return random.Random((seed * 1000003 + i * 7919 + j * 104729 + salt * 1299709) & 0xFFFFFFFF)


def is_road(i, j):
    return i % ROAD_EVERY == 0 or j % ROAD_EVERY == 0


def is_court(i, j):
    return i % ROAD_EVERY == 2 and j % ROAD_EVERY == 2


def is_park(seed, i, j):
    return False


SPECIAL = {(1, 1): 'clock', (-1, -1): 'bakery', (-1, 1): 'shop', (1, -1): 'tall'}


def facing(seed, i, j):
    """rotazione z: la porta (-y locale) guarda la strada. Preferisce fronti visibili dalla camera (-y / -x)."""
    ci, cj = i % ROAD_EVERY, j % ROAD_EVERY
    rg = hrand(seed, i, j, 9)
    W, E, S_, N_ = -math.pi / 2, math.pi / 2, 0.0, math.pi
    if ci == 2 and cj == 2:
        return S_
    if ci == 2:               # fila di mezzo in x: sud o nord
        return S_ if (cj == 1 or cj == 3) else S_
    if cj == 2:
        return W if (ci == 1 or rg.random() < 0.5) else E
    # angoli
    if cj == 3:               # fila alta: mai verso nord (si vedrebbe il retro)
        return W if ci == 1 else (E if rg.random() < 0.6 else S_)
    return S_ if rg.random() < 0.65 else (W if ci == 1 else E)


def make_style(rg, dn, special=None):
    if special:
        style = special
    else:
        r = rg.random()
        shop_p = 0.26 if dn < 0.55 else 0.10
        if r < 0.22: style = 'timber'
        elif r < 0.22 + 0.20: style = 'brick'
        elif r < 0.42 + shop_p: style = 'shop'
        elif r < 0.42 + shop_p + 0.18: style = 'tall'
        else: style = 'cottage'
    tall = max(0.0, 1.0 - dn)
    if style == 'timber':
        fl = rg.choice([2, 3, 3]) + (1 if rg.random() < 0.15 * tall else 0)
        roof = rg.choice(['gy', 'gx', 'gy'])
    elif style == 'brick':
        fl = rg.choice([3, 3, 4]) + (1 if rg.random() < 0.4 * tall else 0)
        roof = rg.choice(['gx', 'hip', 'gx'])
    elif style in ('shop', 'bakery'):
        fl = rg.choice([2, 3, 3]) + (1 if rg.random() < 0.3 * tall else 0)
        roof = rg.choice(['gx', 'gy', 'hip'])
    elif style == 'tall':
        fl = rg.choice([4, 4, 5]) if tall > 0.3 else rg.choice([3, 4])
        roof = 'gy'
    else:
        fl = rg.choice([2, 2, 3]) if tall > 0.4 else rg.choice([1, 2, 2])
        roof = rg.choice(['hip', 'gx'])
    w = rg.choice([0.84, 0.92, 1.0, 1.08]) if style != 'tall' else rg.choice([0.78, 0.84, 0.9])
    d = rg.choice([0.78, 0.86, 0.94])
    if style in ('shop', 'bakery'):
        w = max(w, 0.96)
    rh = {'gy': 0.46 if style != 'tall' else 0.55, 'gx': 0.40, 'hip': 0.40}[roof]
    if roof == 'gy':
        rh = min(rh, w * 0.5 + 0.05)
    ud = 0.0 if style not in ('shop', 'bakery') else (w / 2 - 0.2) * rg.choice([-1, 1])
    chim = rg.random() < (0.85 if style == 'bakery' else 0.6)
    return dict(style=style, w=w, d=d, fl=fl, wi=rg.randrange(len(WALLS)), ri=rg.randrange(len(ROOFS)), sh=rg.randrange(len(SHUT)),
                dr=rg.randrange(len(DOORS)), aw=rg.randrange(len(AWN)), fw=rg.randrange(len(FLOW)), bk=rg.randrange(2),
                roof=roof, rh=round(rh, 2), ud=round(ud, 2), chim=chim, chs=rg.choice([-1, 1]),
                smoke=(rg.random() < 0.55 or style == 'bakery'),
                bal=(style in ('brick', 'tall', 'shop') and fl >= 3 and rg.random() < 0.5),
                laundry=(rg.random() < 0.3))


def link(obj, coll):
    coll.objects.link(obj)
    return obj


def hill_h(x, y, R):
    """altezza del terreno: piatta in citta', colline morbide fuori (deterministica in x,y,R)."""
    r = math.hypot(x, y)
    r0 = R + 14.0
    t = min(1.0, max(0.0, (r - r0) / 55.0))
    t = t * t * (3 - 2 * t)
    base = (3.0 * math.sin(x * 0.021 + 0.7) * math.cos(y * 0.017 + 1.3) + 2.2 * math.sin(x * 0.043 - y * 0.037 + 2.1)
            + 1.2 * math.cos(y * 0.06 + x * 0.02) + 12.0 + 14.0 * (0.5 + 0.5 * math.sin(x * 0.011 + y * 0.013 + 0.4)))
    ridge = 22.0 * math.exp(-((y - 300.0) / 110.0) ** 2) * (0.65 + 0.35 * math.sin(x * 0.012 + 1.0))
    return t * (base + ridge)


def camera_for(N):
    """camera(N) continua: bassa e vicina per N piccolo, piu' alta e lontana al crescere di N.
    Ritorna (pos, target, lens_mm)."""
    s = math.sqrt(max(N, 1.0)) + 2.0
    az = math.radians(-90 - 15)
    h = 1.25 + 0.04 * s ** 1.42                        # quota camera: altezza d'occhio -> sale con N
    dist = 0.97 * math.sqrt(max(N, 1.0)) + 1.9 + h / 0.81 + 1.0 + 1.6 * math.exp(-N / 120.0)   # fuori dal paese: in primo piano i campi
    ty = 0.05 * s
    pitch = math.radians(3.0 + 6.0 * (1 - math.exp(-N / 220.0)))   # inclinazione verso il basso
    pos = (dist * math.cos(az), dist * math.sin(az) + ty, h)
    tz = h - dist * math.tan(pitch)
    tgt = (0.0, ty, tz)
    lens = 44.0 + 16.0 * math.exp(-N / 90.0)
    return pos, tgt, lens


def build_scene(N, seed, res, samples, gpu=False):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    coll = sc.collection
    rho = int(math.sqrt(N * 2.4 / math.pi)) + 6
    cells = []
    for i in range(-rho, rho + 1):
        for j in range(-rho, rho + 1):
            if is_road(i, j) or is_court(i, j):
                continue
            jit = 0.0 if (i, j) in SPECIAL else hrand(seed, i, j, 1).random()
            cells.append((math.hypot(i, j) * C + jit * C * 0.55, i, j))
    cells.sort()
    lots = cells[:N]
    chosen = {(i, j) for _, i, j in lots}
    maxd = max(math.hypot(i, j) * C for _, i, j in lots) + 0.9 if lots else 3
    R = maxd + 1.0          # bordo del paese
    cpos, ctgt, clens = camera_for(N)

    # ----- terreno: un unico mesh a campi, colline, nebbia d'aria
    ext = 620.0
    nseg = 190
    bt = bmesh.new()
    grid = []
    for a in range(nseg + 1):
        u = -1 + 2 * a / nseg
        grid.append(ext * math.copysign(abs(u) ** 1.9, u))
    verts = {}
    for a, x in enumerate(grid):
        for c_, y in enumerate(grid):
            verts[(a, c_)] = bt.verts.new((x, y, hill_h(x, y, R) - 0.0))
    for a in range(nseg):
        for c_ in range(nseg):
            bt.faces.new((verts[(a, c_)], verts[(a + 1, c_)], verts[(a + 1, c_ + 1)], verts[(a, c_ + 1)]))
    bt.normal_update()
    me_t = bpy.data.meshes.new("terrain")
    for f in bt.faces:
        f.smooth = True
    bt.to_mesh(me_t)
    bt.free()
    fm_ = field_material(R, cpos)
    me_t.materials.append(fm_)
    link(bpy.data.objects.new("terrain", me_t), coll)

    # ----- strade: cobble in citta', sterrato fuori
    cobble = mat("cobble", (0.93, 0.80, 0.62), 0.85,
                 extra=tex_brick(5.0, (0.93, 0.80, 0.62), (0.86, 0.72, 0.55), (0.66, 0.52, 0.40), 0.07, 0.5))
    dirt = mat("dirt", (0.86, 0.66, 0.42), 0.95, extra=tex_noise_color(1.2, (0.80, 0.60, 0.38), (0.90, 0.72, 0.48)))
    rb = MB()
    rr_ = int(R / C) + 2
    hw = 0.36 * C
    for i in range(-rr_, rr_ + 1):
        for j in range(-rr_, rr_ + 1):
            if not is_road(i, j) or math.hypot(i, j) * C > R - 0.4:
                continue
            x, y = i * C, j * C
            if i % ROAD_EVERY == 0:
                rb.box(x - hw, y - C / 2 + 0.005, 0.0, x + hw, y + C / 2 - 0.005, 0.045, cobble, 0.012)
                if j % ROAD_EVERY == 0:
                    rb.box(x - C / 2 + 0.005, y - hw, 0.0, x - hw - 0.002, y + hw, 0.045, cobble, 0.012)
                    rb.box(x + hw + 0.002, y - hw, 0.0, x + C / 2 - 0.005, y + hw, 0.045, cobble, 0.012)
            else:
                rb.box(x - C / 2 + 0.005, y - hw, 0.0, x + C / 2 - 0.005, y + hw, 0.045, cobble, 0.012)
    # sterrato verso la campagna lungo gli assi
    for s_ in (-1, 1):
        rb.box(-0.4, s_ * (R - 0.6), 0.0, 0.4, s_ * (R + 24), 0.03, dirt, 0.01)
        rb.box(s_ * (R - 0.6), -0.4, 0.0, s_ * (R + 24), 0.4, 0.03, dirt, 0.01)
    link(bpy.data.objects.new("roads", rb.build("roads")), coll)

    cnt = dict(house=0, tree=0, prop=0, person=0)

    cdist = math.hypot(cpos[0], cpos[1])

    def near_cam(x, y, k=0.0, base=4.0):
        return math.hypot(x - cpos[0], y - cpos[1]) < base + k * cdist

    def inst(name, me, x, y, z=0.0, rz=0.0, s=1.0):
        ob = bpy.data.objects.new(name, me)
        ob.location = (x, y, z)
        ob.rotation_euler = (0, 0, rz)
        ob.scale = (s, s, s)
        return link(ob, coll)

    # ----- case
    for _, i, j in lots:
        rg = hrand(seed, i, j, 2)
        dn = math.hypot(i, j) * C / max(R, 1)
        rot = facing(seed, i, j)
        sp = SPECIAL.get((i, j))
        if sp == 'clock':
            inst("clock", clock_tower_mesh(), i * C, j * C, 0.0, rot, 1.0)
        else:
            st = make_style(rg, dn, sp)
            me = house_mesh(st)
            # sposta verso la strada che guarda
            sh = 0.1
            dx = {-math.pi / 2: -sh, math.pi / 2: sh}.get(rot, 0.0)
            dy = {0.0: -sh, math.pi: sh}.get(rot, 0.0)
            inst("house", me, i * C + dx + rg.uniform(-0.03, 0.03), j * C + dy + rg.uniform(-0.03, 0.03), 0.0, rot + rg.uniform(-0.03, 0.03), 1.0)
        cnt["house"] += 1
    # cortili e celle non costruite dentro il paese
    for i in range(-rr_, rr_ + 1):
        for j in range(-rr_, rr_ + 1):
            if is_road(i, j) or (i, j) in chosen:
                continue
            if math.hypot(i, j) * C > R - 0.9:
                continue
            rg = hrand(seed, i, j, 3)
            x, y = i * C + rg.uniform(-0.12, 0.12), j * C + rg.uniform(-0.12, 0.12)
            if is_court(i, j):
                r = rg.random()
                if r < 0.4:
                    inst("court", prop_mesh("court", rg.randrange(6)), x, y, 0.0, rg.random() * 6, 1.1)
                elif r < 0.6:
                    inst("well", prop_mesh("well"), x, y, 0.0, rg.random() * 6, 1.0)
                    inst("tree", tree_mesh("round", rg.randrange(6)), x + 0.5, y + 0.3, 0.0, rg.random() * 6, 1.0)
                else:
                    inst("veg", prop_mesh("veg"), x, y, 0.0, rg.choice([0, math.pi / 2]), 1.0)
                    inst("bush", tree_mesh("bush", rg.randrange(3)), x + 0.5, y - 0.5, 0.0, rg.random() * 6, 1.0)
                cnt["tree"] += 1
                continue
            r = rg.random()
            if near_cam(x, y, 0.0, 2.2):
                continue
            if r < 0.5:
                kind = rg.choice(["round", "double", "pine", "round"])
                ci = rg.randrange(len(LEAVES)) if kind != "pine" else rg.choice([1, 5])
                inst("tree", tree_mesh(kind, ci), x, y, 0.0, rg.random() * 6, rg.uniform(1.0, 1.4))
            elif r < 0.75:
                inst("veg", prop_mesh("veg"), x, y, 0.0, rg.choice([0, math.pi / 2]), 1.0)
            else:
                for q in range(3):
                    inst("flw", prop_mesh("flowers", rg.randrange(5)), x + rg.uniform(-.5, .5), y + rg.uniform(-.5, .5), 0.0, rg.random() * 6, rg.uniform(1, 1.6))
            cnt["tree"] += 1
    # alberelli lungo le strade, lampioni, persone, carretti
    for i in range(-rr_, rr_ + 1):
        for j in range(-rr_, rr_ + 1):
            if not is_road(i, j) or math.hypot(i, j) * C > R - 0.7:
                continue
            rg = hrand(seed, i, j, 5)
            x, y = i * C, j * C
            along_x = (j % ROAD_EVERY == 0)     # strada orizzontale
            cross = (i % ROAD_EVERY == 0 and j % ROAD_EVERY == 0)
            if cross:
                if (i, j) != (0, 0):
                    inst("lamp", prop_mesh("lamp"), x + 0.46, y + 0.46, 0.04)
                    cnt["prop"] += 1
                continue
            if rg.random() < 0.45:
                sx = (0, rg.choice([-1, 1]) * 0.47) if not along_x else (rg.choice([-1, 1]) * 0.47, 0)
                if along_x:
                    inst("lamp", prop_mesh("lamp"), x + rg.uniform(-.3, .3), y + sx[1] + rg.choice([-1, 1]) * 0.47, 0.04)
                else:
                    inst("lamp", prop_mesh("lamp"), x + rg.choice([-1, 1]) * 0.47, y + rg.uniform(-.3, .3), 0.04)
                cnt["prop"] += 1
            for q in range(2):
                if rg.random() < 0.5:
                    pp = (x + rg.uniform(-.35, .35), y + rg.uniform(-.5, .5)) if not along_x else (x + rg.uniform(-.5, .5), y + rg.uniform(-.35, .35))
                    inst("person", prop_mesh("person", rg.randrange(6)), pp[0], pp[1], 0.04, rg.random() * 6, 1.0)
                    cnt["person"] += 1
            if rg.random() < 0.12:
                inst("cart", prop_mesh("cart", rg.randrange(2)), x + (rg.uniform(-.4, .4) if along_x else 0.1), y + (0.1 if along_x else rg.uniform(-.4, .4)),
                     0.04, 0.0 if along_x else math.pi / 2)
                cnt["prop"] += 1
            if rg.random() < 0.18:
                inst("barrel", prop_mesh("barrel"), x + rg.choice([-1, 1]) * 0.45 * (0 if along_x else 1) + (rg.uniform(-.4, .4) if along_x else 0),
                     y + (rg.choice([-1, 1]) * 0.45 if along_x else rg.uniform(-.4, .4)), 0.04)
    fo = inst("fountain", prop_mesh("fountain"), 0, 0, 0.045, 0.0, 0.8)
    # alberi di bordo del paese: filare irregolare
    nb = int(2 * math.pi * R / 1.4)
    for q in range(nb):
        rg = hrand(seed, q, 99, 4)
        a = 2 * math.pi * q / nb + rg.uniform(-0.1, 0.1)
        rr = R + rg.uniform(-0.2, 0.9)
        if rg.random() < 0.55 and not near_cam(rr * math.cos(a), rr * math.sin(a), 0.4):
            kind = rg.choice(["round", "pine", "bush", "round_big"])
            ci = rg.randrange(len(LEAVES)) if kind != "pine" else rg.choice([1, 5])
            inst("tree", tree_mesh(kind, ci), rr * math.cos(a), rr * math.sin(a), 0.0, rg.random() * 6, rg.uniform(0.9, 1.3))
            cnt["tree"] += 1
    # cintura del paese: siepi, staccionata, fiori, balle (piccoli: ok anche vicino alla camera)
    nb2 = int(2 * math.pi * (R + 1.0) / 0.95)
    for q in range(nb2):
        rg = hrand(seed, q, 77, 6)
        a = 2 * math.pi * q / nb2
        rr = R + rg.uniform(0.0, 1.0)
        x, y = rr * math.cos(a), rr * math.sin(a)
        if abs(x) < 1.0 or abs(y) < 1.0:
            continue
        r_ = rg.random()
        if r_ < 0.35:
            if math.hypot(x - cpos[0], y - cpos[1]) > 3.0:
                inst("bush", tree_mesh("bush", rg.randrange(3)), x, y, 0.0, rg.random() * 6, rg.uniform(1.1, 1.6))
        elif r_ < 0.65:
            inst("fence", prop_mesh("fence"), x, y, 0.0, a + math.pi / 2, 1.0)
        elif r_ < 0.9:
            for k_ in range(3):
                inst("flw", prop_mesh("flowers", rg.randrange(5)), x + rg.uniform(-.4, .4), y + rg.uniform(-.4, .4), 0.0, rg.random() * 6, rg.uniform(1.2, 1.8))
        else:
            inst("bale", prop_mesh("bale"), x, y, 0.0, rg.uniform(0, 3), 0.7)
    # ----- campagna: fienili, mulino, balle, pecore, alberi (cella 7x7, hash su coordinate: stabile)
    G = 4.6
    gx = int((R + 135) / G) + 1
    wind_done = False
    for ix in range(-gx, gx + 1):
        for iy in range(-gx, gx + 1):
            rg = hrand(seed, ix, iy, 21)
            x = (ix + rg.uniform(0.1, 0.9)) * G
            y = (iy + rg.uniform(0.1, 0.9)) * G
            r = math.hypot(x, y)
            if r < R + 2.2 or r > R + 135:
                continue
            if r < R + 26 and (abs(x) < 1.6 or abs(y) < 1.6):
                continue
            if near_cam(x, y, 0.12):
                continue
            if r > R + 45 and rg.random() < 0.6:
                continue
            z = hill_h(x, y, R) - 0.03
            p = rg.random()
            sc_ = 1.0 + max(0.0, (r - R) / 120.0) * 1.6      # lontano piu' grande: si legge sulla collina
            if p < 0.035:
                inst("barn", prop_mesh("barn"), x, y, z, rg.choice([0, math.pi / 2, math.pi, -math.pi / 2]) + rg.uniform(-.2, .2), 1.0 * sc_ ** 0.5)
            elif p < 0.075:
                for q in range(rg.randint(2, 4)):
                    inst("bale", prop_mesh("bale"), x + rg.uniform(-1.4, 1.4), y + rg.uniform(-1.4, 1.4), z, rg.uniform(0, 3), 0.8 * sc_ ** 0.5)
            elif p < 0.11:
                inst("stack", prop_mesh("stack"), x, y, z, 0, 1.0 * sc_ ** 0.5)
            elif p < 0.15:
                for q in range(rg.randint(3, 6)):
                    inst("sheep", prop_mesh("sheep"), x + rg.uniform(-1.8, 1.8), y + rg.uniform(-1.8, 1.8), z, rg.uniform(0, 6.28), 1.0)
            elif p < 0.19:
                kind = "poplar"
                for q in range(rg.randint(3, 6)):
                    inst("poplar", tree_mesh("poplar", rg.choice([0, 1, 2])), x + q * 1.0, y + rg.uniform(-.2, .2), z, rg.random() * 6, 1.6 * sc_ ** 0.5)
            elif p < 0.62:
                for q in range(rg.randint(1, 2)):
                    kind = rg.choice(["round", "round_big", "double", "pine"])
                    ci = rg.randrange(len(LEAVES)) if kind != "pine" else rg.choice([1, 5])
                    inst("tree", tree_mesh(kind, ci), x + rg.uniform(-1.8, 1.8), y + rg.uniform(-1.8, 1.8), z, rg.random() * 6, rg.uniform(1.1, 1.9) * sc_ ** 0.5)
                    cnt["tree"] += 1
    # mulino: landmark sul retro-destra del paese (sulla collina bassa)
    wx, wy = (R + 14) * math.cos(math.radians(62)), (R + 14) * math.sin(math.radians(62))
    inst("mill", prop_mesh("mill"), wx, wy, hill_h(wx, wy, R) - 0.03, 0.0, 1.7)
    # casale con fienile a sinistra
    fx, fy = (R + 11) * math.cos(math.radians(125)), (R + 11) * math.sin(math.radians(125))
    inst("barn", prop_mesh("barn"), fx, fy, hill_h(fx, fy, R) - 0.03, 0.4, 1.5)
    st = make_style(random.Random(77), 0.9, 'cottage')
    inst("farm", house_mesh(dict(st, fl=2, roof='gx', rh=0.4)), fx + 3.4, fy - 1.2, hill_h(fx, fy, R) - 0.03, -0.3, 1.4)

    # ----- luci: sole dorato basso da dietro-sinistra della camera + cielo caldo
    sun = bpy.data.lights.new("sun", 'SUN')
    sun.energy = 4.6
    sun.color = (1.0, 0.78, 0.52)
    sun.angle = math.radians(5)
    so = link(bpy.data.objects.new("sun", sun), coll)
    so.rotation_euler = Euler((math.radians(66), 0, math.radians(-38)), 'XYZ')
    sky_world(sc)

    # ----- camera
    target = bpy.data.objects.new("target", None); link(target, coll)
    target.location = ctgt
    cam = bpy.data.cameras.new("cam")
    cam.lens = clens
    cam.sensor_fit = 'HORIZONTAL'
    cam.sensor_width = 36
    cam.clip_end = 3000
    cam.shift_y = 0.05 * math.exp(-N / 150.0)     # N piccolo: meno prato in primo piano, case piu' in basso/grandi
    co = link(bpy.data.objects.new("cam", cam), coll)
    co.location = cpos
    tr = co.constraints.new('TRACK_TO'); tr.target = target
    tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    sc.camera = co
    r = sc.render
    r.engine = 'CYCLES'
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    cy = sc.cycles
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.04
    cy.use_denoising = True
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    cy.max_bounces = 4
    cy.diffuse_bounces = 2
    cy.glossy_bounces = 1
    cy.transmission_bounces = 1
    cy.sample_clamp_indirect = 6
    cy.device = 'CPU'
    if gpu:
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            for t in ('OPTIX', 'CUDA', 'HIP', 'METAL'):
                try:
                    prefs.compute_device_type = t
                    prefs.get_devices()
                    if any(d.type == t for d in prefs.devices):
                        for d in prefs.devices:
                            d.use = True
                        cy.device = 'GPU'
                        break
                except Exception:
                    continue
        except Exception:
            pass
    for vt, lk in (('AgX', 'AgX - Medium High Contrast'), ('AgX', 'Medium High Contrast')):
        try:
            sc.view_settings.view_transform = vt
            sc.view_settings.look = lk
            break
        except Exception:
            pass
    sc.view_settings.exposure = 0.0
    print(f"[cozy2] N={N} R={R:.1f} lotti={len(lots)} {cnt} cam={tuple(round(v, 1) for v in cpos)} build={time.time()-t0:.1f}s")
    return sc


# ---------------------------------------------------------------- cielo e campi (shader)
HORIZON = (1.0, 0.80, 0.42)


def sky_world(sc):
    w = bpy.data.worlds.new("w"); sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    cr = nt.nodes.new("ShaderNodeValToRGB")
    ce = cr.color_ramp.elements
    ce[0].position = 0.50; ce[0].color = (*lin((1.0, 0.82, 0.42)), 1)
    e1 = ce.new(0.58); e1.color = (*lin((1.0, 0.66, 0.38)), 1)
    e2 = ce.new(0.74); e2.color = (*lin((0.98, 0.58, 0.46)), 1)
    ce[3].position = 0.92; ce[3].color = (*lin((0.90, 0.52, 0.62)), 1)
    # direzione normalizzata: Z = elevazione
    nm = nt.nodes.new("ShaderNodeVectorMath"); nm.operation = 'NORMALIZE'
    gm = nt.nodes.new("ShaderNodeNewGeometry")
    nt.links.new(gm.outputs["Incoming"], nm.inputs[0])
    nt.links.new(nm.outputs["Vector"], sp.inputs["Vector"])
    ng = nt.nodes.new("ShaderNodeMath"); ng.operation = 'MULTIPLY'; ng.inputs[1].default_value = -0.5
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'; ad.inputs[1].default_value = 0.5
    nt.links.new(sp.outputs["Z"], ng.inputs[0])       # Incoming punta verso l'osservatore: Z invertita
    nt.links.new(ng.outputs["Value"], ad.inputs[0])
    nt.links.new(ad.outputs["Value"], cr.inputs["Fac"])
    # nuvole morbide rosate
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.2
    nz.inputs["Detail"].default_value = 4
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 3.2)
    nt.links.new(nm.outputs["Vector"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    cl = nt.nodes.new("ShaderNodeMapRange")
    cl.inputs["From Min"].default_value = 0.50
    cl.inputs["From Max"].default_value = 0.68
    nt.links.new(nz.outputs["Fac"], cl.inputs["Value"])
    # le nuvole svaniscono verso l'orizzonte e lo zenit
    el = nt.nodes.new("ShaderNodeMapRange")
    el.inputs["From Min"].default_value = 0.52
    el.inputs["From Max"].default_value = 0.62
    nt.links.new(ad.outputs["Value"], el.inputs["Value"])
    ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY'
    nt.links.new(cl.outputs["Result"], ml.inputs[0]); nt.links.new(el.outputs["Result"], ml.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[7].default_value = (*lin((1.0, 0.88, 0.56)), 1)
    nt.links.new(ml.outputs["Value"], mx.inputs[0])
    nt.links.new(cr.outputs["Color"], mx.inputs[6])
    nt.links.new(mx.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0


def field_material(R, cpos):
    m = bpy.data.materials.new("fields")
    m.use_nodes = True
    nt = m.node_tree
    N_ = nt.nodes
    L = nt.links
    bsdf = N_["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.92
    out = N_["Material Output"]
    tc = N_.new("ShaderNodeTexCoord")
    sp = N_.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sp.inputs["Vector"])
    cb = N_.new("ShaderNodeCombineXYZ")
    L.new(sp.outputs["X"], cb.inputs["X"]); L.new(sp.outputs["Y"], cb.inputs["Y"])
    # deformazione dei confini
    wn = N_.new("ShaderNodeTexNoise"); wn.inputs["Scale"].default_value = 0.045; wn.inputs["Detail"].default_value = 2
    L.new(cb.outputs["Vector"], wn.inputs["Vector"])
    wv = N_.new("ShaderNodeVectorMath"); wv.operation = 'SCALE'; wv.inputs["Scale"].default_value = 14.0
    wc = N_.new("ShaderNodeVectorMath"); wc.operation = 'SUBTRACT'; wc.inputs[1].default_value = (0.5, 0.5, 0.5)
    L.new(wn.outputs["Color"], wc.inputs[0]); L.new(wc.outputs["Vector"], wv.inputs[0])
    wa = N_.new("ShaderNodeVectorMath"); wa.operation = 'ADD'
    L.new(cb.outputs["Vector"], wa.inputs[0]); L.new(wv.outputs["Vector"], wa.inputs[1])
    vc = N_.new("ShaderNodeTexVoronoi"); vc.feature = 'F1'; vc.voronoi_dimensions = '2D'
    vc.inputs["Scale"].default_value = 0.07; vc.inputs["Randomness"].default_value = 0.9
    ve = N_.new("ShaderNodeTexVoronoi"); ve.feature = 'DISTANCE_TO_EDGE'; ve.voronoi_dimensions = '2D'
    ve.inputs["Scale"].default_value = 0.07; ve.inputs["Randomness"].default_value = 0.9
    L.new(wa.outputs["Vector"], vc.inputs["Vector"]); L.new(wa.outputs["Vector"], ve.inputs["Vector"])
    sc_ = N_.new("ShaderNodeSeparateColor")
    L.new(vc.outputs["Color"], sc_.inputs["Color"])
    # palette per campo (R)
    pal = [(0.93, 0.74, 0.30), (0.97, 0.84, 0.46), (0.56, 0.73, 0.34), (0.42, 0.63, 0.32), (0.74, 0.50, 0.32),
           (0.88, 0.68, 0.30), (0.66, 0.78, 0.38), (0.96, 0.80, 0.40), (0.50, 0.68, 0.34), (0.80, 0.56, 0.34), (0.66, 0.56, 0.78), (0.60, 0.74, 0.36)]
    strip = [0.95, 0.85, 0.70, 0.85, 0.95, 0.85, 0.70, 0.85, 0.75, 0.95, 0.85, 0.65]

    def const_ramp(vals, rgb):
        cr = N_.new("ShaderNodeValToRGB")
        cr.color_ramp.interpolation = 'CONSTANT'
        e = cr.color_ramp.elements
        n = len(vals)
        while len(e) < n:
            e.new(0.5)
        for k in range(n):
            e[k].position = k / n + 1e-4
            e[k].color = (*lin(vals[k]), 1) if rgb else (vals[k], vals[k], vals[k], 1)
        e[0].position = 0.0
        return cr
    cp = const_ramp(pal, True)
    cs = const_ramp(strip, False)
    L.new(sc_.outputs["Red"], cp.inputs["Fac"]); L.new(sc_.outputs["Red"], cs.inputs["Fac"])
    gp = N_.new("ShaderNodeNewGeometry")
    cv = N_.new("ShaderNodeVectorMath"); cv.operation = 'DISTANCE'
    cv.inputs[1].default_value = tuple(cpos)
    L.new(gp.outputs["Position"], cv.inputs[0])
    # strisce: angolo per campo (G), periodo (B)
    th = N_.new("ShaderNodeMath"); th.operation = 'MULTIPLY'; th.inputs[1].default_value = 3.14159
    L.new(sc_.outputs["Green"], th.inputs[0])
    co_ = N_.new("ShaderNodeMath"); co_.operation = 'COSINE'; si_ = N_.new("ShaderNodeMath"); si_.operation = 'SINE'
    L.new(th.outputs["Value"], co_.inputs[0]); L.new(th.outputs["Value"], si_.inputs[0])
    mx_ = N_.new("ShaderNodeMath"); mx_.operation = 'MULTIPLY'
    my_ = N_.new("ShaderNodeMath"); my_.operation = 'MULTIPLY'
    L.new(sp.outputs["X"], mx_.inputs[0]); L.new(co_.outputs["Value"], mx_.inputs[1])
    L.new(sp.outputs["Y"], my_.inputs[0]); L.new(si_.outputs["Value"], my_.inputs[1])
    ax = N_.new("ShaderNodeMath"); ax.operation = 'ADD'
    L.new(mx_.outputs["Value"], ax.inputs[0]); L.new(my_.outputs["Value"], ax.inputs[1])
    pe = N_.new("ShaderNodeMath"); pe.operation = 'MULTIPLY'; pe.inputs[1].default_value = 0.9
    pa = N_.new("ShaderNodeMath"); pa.operation = 'ADD'; pa.inputs[1].default_value = 0.95
    L.new(sc_.outputs["Blue"], pe.inputs[0]); L.new(pe.outputs["Value"], pa.inputs[0])
    kk = N_.new("ShaderNodeMath"); kk.operation = 'DIVIDE'; kk.inputs[0].default_value = 6.2832
    L.new(pa.outputs["Value"], kk.inputs[1])
    ar = N_.new("ShaderNodeMath"); ar.operation = 'MULTIPLY'
    L.new(ax.outputs["Value"], ar.inputs[0]); L.new(kk.outputs["Value"], ar.inputs[1])
    sn = N_.new("ShaderNodeMath"); sn.operation = 'SINE'
    L.new(ar.outputs["Value"], sn.inputs[0])
    # strato fine (vicino alla camera): periodo 0.35-0.7, dissolve con la distanza
    pe2 = N_.new("ShaderNodeMath"); pe2.operation = 'MULTIPLY'; pe2.inputs[1].default_value = 0.4
    pa2 = N_.new("ShaderNodeMath"); pa2.operation = 'ADD'; pa2.inputs[1].default_value = 0.55
    L.new(sc_.outputs["Blue"], pe2.inputs[0]); L.new(pe2.outputs["Value"], pa2.inputs[0])
    kk2 = N_.new("ShaderNodeMath"); kk2.operation = 'DIVIDE'; kk2.inputs[0].default_value = 6.2832
    L.new(pa2.outputs["Value"], kk2.inputs[1])
    ar2 = N_.new("ShaderNodeMath"); ar2.operation = 'MULTIPLY'
    L.new(ax.outputs["Value"], ar2.inputs[0]); L.new(kk2.outputs["Value"], ar2.inputs[1])
    sn2 = N_.new("ShaderNodeMath"); sn2.operation = 'SINE'
    L.new(ar2.outputs["Value"], sn2.inputs[0])
    wmix = N_.new("ShaderNodeMapRange"); wmix.inputs["From Min"].default_value = 6.0; wmix.inputs["From Max"].default_value = 26.0
    wmix.inputs["To Min"].default_value = 0.0; wmix.inputs["To Max"].default_value = 1.0
    L.new(cv.outputs["Value"], wmix.inputs["Value"])       # 0 vicino (fine) .. 1 lontano (largo)
    sm = N_.new("ShaderNodeMix"); sm.data_type = 'FLOAT'
    L.new(wmix.outputs["Result"], sm.inputs[0]); L.new(sn2.outputs["Value"], sm.inputs[2]); L.new(sn.outputs["Value"], sm.inputs[3])
    sh = N_.new("ShaderNodeMapRange"); sh.inputs["From Min"].default_value = -1; sh.inputs["From Max"].default_value = 1
    L.new(sm.outputs[0], sh.inputs["Value"])
    fac = N_.new("ShaderNodeMath"); fac.operation = 'MULTIPLY'
    L.new(sh.outputs["Result"], fac.inputs[0]); L.new(cs.outputs["Color"], fac.inputs[1])
    # colore campo * striscia
    mxc = N_.new("ShaderNodeMix"); mxc.data_type = 'RGBA'; mxc.blend_type = 'MULTIPLY'
    mxc.inputs[7].default_value = (0.50, 0.44, 0.40, 1)
    L.new(fac.outputs["Value"], mxc.inputs[0]); L.new(cp.outputs["Color"], mxc.inputs[6])
    # siepi sui bordi dei campi
    ed = N_.new("ShaderNodeMapRange"); ed.inputs["From Min"].default_value = 0.006; ed.inputs["From Max"].default_value = 0.02
    ed.inputs["To Min"].default_value = 1.0; ed.inputs["To Max"].default_value = 0.0
    L.new(ve.outputs["Distance"], ed.inputs["Value"])
    mh = N_.new("ShaderNodeMix"); mh.data_type = 'RGBA'
    mh.inputs[7].default_value = (*lin((0.32, 0.50, 0.28)), 1)
    L.new(ed.outputs["Result"], mh.inputs[0]); L.new(mxc.outputs[2], mh.inputs[6])
    # prato del paese
    gz = N_.new("ShaderNodeTexNoise"); gz.inputs["Scale"].default_value = 0.8; gz.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], gz.inputs["Vector"])
    gr = N_.new("ShaderNodeValToRGB")
    gr.color_ramp.elements[0].color = (*lin((0.50, 0.68, 0.33)), 1)
    gr.color_ramp.elements[1].color = (*lin((0.66, 0.78, 0.40)), 1)
    L.new(gz.outputs["Fac"], gr.inputs["Fac"])
    ln = N_.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'
    L.new(cb.outputs["Vector"], ln.inputs[0])
    nj = N_.new("ShaderNodeMath"); nj.operation = 'MULTIPLY'; nj.inputs[1].default_value = 1.2
    L.new(wn.outputs["Fac"], nj.inputs[0])
    nsum = N_.new("ShaderNodeMath"); nsum.operation = 'ADD'
    L.new(ln.outputs["Value"], nsum.inputs[0]); L.new(nj.outputs["Value"], nsum.inputs[1])
    tm = N_.new("ShaderNodeMapRange")
    tm.inputs["From Min"].default_value = R - 0.5; tm.inputs["From Max"].default_value = R + 0.5
    tm.inputs["To Min"].default_value = 1.0; tm.inputs["To Max"].default_value = 0.0
    L.new(nsum.outputs["Value"], tm.inputs["Value"])
    mt = N_.new("ShaderNodeMix"); mt.data_type = 'RGBA'
    L.new(tm.outputs["Result"], mt.inputs[0]); L.new(mh.outputs[2], mt.inputs[6]); L.new(gr.outputs["Color"], mt.inputs[7])
    L.new(mt.outputs[2], bsdf.inputs["Base Color"])
    # solchi (bump dalle strisce) solo nei campi
    bp = N_.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.05
    L.new(fac.outputs["Value"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    # foschia d'aria: verso il colore dell'orizzonte con la distanza dalla camera
    ds = N_.new("ShaderNodeMath"); ds.operation = 'DIVIDE'; ds.inputs[1].default_value = 240.0
    L.new(cv.outputs["Value"], ds.inputs[0])
    dp = N_.new("ShaderNodeMath"); dp.operation = 'POWER'; dp.inputs[1].default_value = 1.6
    L.new(ds.outputs["Value"], dp.inputs[0])
    ng_ = N_.new("ShaderNodeMath"); ng_.operation = 'MULTIPLY'; ng_.inputs[1].default_value = -1.0
    L.new(dp.outputs["Value"], ng_.inputs[0])
    ex = N_.new("ShaderNodeMath"); ex.operation = 'EXPONENT'
    L.new(ng_.outputs["Value"], ex.inputs[0])
    hz = N_.new("ShaderNodeMath"); hz.operation = 'SUBTRACT'; hz.inputs[0].default_value = 1.0
    L.new(ex.outputs["Value"], hz.inputs[1])
    em = N_.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*lin(HORIZON), 1); em.inputs["Strength"].default_value = 1.0
    mxs = N_.new("ShaderNodeMixShader")
    L.new(hz.outputs["Value"], mxs.inputs[0]); L.new(bsdf.outputs["BSDF"], mxs.inputs[1]); L.new(em.outputs["Emission"], mxs.inputs[2])
    L.new(mxs.outputs["Shader"], out.inputs["Surface"])
    return m


def grade(path, sat=1.10, contrast=1.04):
    """leggero grading finale (saturazione/contrasto) - il tone mapping OCIO non c'e' in bpy pip."""
    try:
        import numpy as np
        from PIL import Image
        im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
        g = im.mean(axis=2, keepdims=True)
        im = np.clip(g + (im - g) * sat, 0, 1)
        im = np.clip((im - 0.5) * contrast + 0.5, 0, 1)
        Image.fromarray((im * 255 + 0.5).astype(np.uint8)).save(path)
    except Exception as e:
        print("[cozy2] grade saltato:", e)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--followers", type=int, default=111)
    ap.add_argument("--out", default="cozy2.png")
    ap.add_argument("--res", type=int, nargs=2, default=[540, 960])
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--save-blend", default="")
    a = ap.parse_args(argv)
    sc = build_scene(a.followers, a.seed, tuple(a.res), a.samples, a.gpu)
    sc.render.filepath = a.out
    if a.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=a.save_blend)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"[cozy2] render {time.time()-t:.1f}s -> {a.out}")
    grade(a.out)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(argv)
