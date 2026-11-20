"""Follower City - COZY v3: MINIATURA DA TAVOLO in MACRO (case di argilla/feltro, DOF reale).

Uso (pip bpy):  python cozy_city.py --followers 111 --out cozy3_111.png
Opzioni: --res 540 960 --samples 40 --seed 7 --save-blend f.blend
N follower = N casette in un cluster organico (fillotassi + jitter, strade serpeggianti di terra/ciottoli)
sulla cima di una collina fissa. Camera bassa, 70-85 mm, f-stop basso (DOF forte), sale con N (camera_for).
Deterministico: il lotto i ha SEMPRE posizione/tipo/colori uguali; N sceglie solo quanti lotti (0..N-1).
"""
import sys, math, random, time, argparse, zlib
import bpy, bmesh
from mathutils import Vector

GA = math.pi * (3 - math.sqrt(5))
A_SP = 1.75                 # spaziatura fillotassi
HILL_H, HILL_S = 30.0, 36.0  # collina fissa (indipendente da N)


def lin(c):
    return tuple(x ** 2.2 for x in c)


TER, TERF = 2.6, 0.65


def hill(r):
    """collina a terrazze (fissa, indipendente da N)."""
    z = HILL_H * math.exp(-(r / HILL_S) ** 2)
    t = (HILL_H - z) / TER
    k = math.floor(t)
    f = t - k
    u = min(1.0, max(0.0, (f - (1 - TERF)) / TERF))
    u = u * u * (3 - 2 * u)
    return HILL_H - TER * (k + u)


# ---------------------------------------------------------------- palette
WALLS = [(0.98, 0.88, 0.70), (0.96, 0.72, 0.58), (0.80, 0.86, 0.66), (0.70, 0.82, 0.90), (0.95, 0.80, 0.80),
         (0.99, 0.93, 0.78), (0.88, 0.76, 0.62)]
ROOFS = [(0.78, 0.36, 0.26), (0.62, 0.30, 0.22), (0.40, 0.50, 0.62), (0.45, 0.60, 0.42), (0.86, 0.50, 0.28)]
SHUT = [(0.35, 0.58, 0.42), (0.30, 0.52, 0.74), (0.82, 0.32, 0.28), (0.95, 0.72, 0.28), (0.28, 0.62, 0.62)]
FLOW = [(0.95, 0.30, 0.38), (0.99, 0.85, 0.30), (0.99, 0.97, 0.92), (0.72, 0.50, 0.90), (0.98, 0.58, 0.72)]
_mats = {}


def mat(name, rgb, rough=0.8, emit=None, strength=0.0, bump=0.25, scale=55.0, sss=0.18, tex='noise', var=0.06):
    """argilla/feltro: variazione di colore + grana (bump) + SSS morbido."""
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    try:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (0.6, 0.3, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.08
    except Exception:
        pass
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*lin(emit), 1)
        bsdf.inputs["Emission Strength"].default_value = strength
    base = lin(rgb)
    if tex == 'none':
        bsdf.inputs["Base Color"].default_value = (*base, 1)
        return _mats.setdefault(name, m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 6
    nz.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[6].default_value = (*[c * (1 - var * 2.5) for c in base], 1)
    mx.inputs[7].default_value = (*[min(1, c * (1 + var * 2.5)) for c in base], 1)
    nt.links.new(nz.outputs["Fac"], mx.inputs[0])
    nt.links.new(mx.outputs[2], bsdf.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.02
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    _mats[name] = m
    return m


def M(name, rgb, **kw):
    return mat(name, rgb, **kw)


def m_wall(i): return M(f"wall{i}", WALLS[i % len(WALLS)], rough=0.9, bump=0.35, scale=70, var=0.05)
def m_roof(i): return M(f"roof{i}", ROOFS[i % len(ROOFS)], rough=0.7, bump=0.2, scale=40, var=0.09)
def m_shut(i): return M(f"shut{i}", SHUT[i % len(SHUT)], rough=0.6, bump=0.15)
def m_flow(i): return M(f"flw{i}", FLOW[i % len(FLOW)], rough=0.6, tex='none')
def m_trim(): return M("trim", (0.99, 0.94, 0.84), rough=0.7)
def m_wood(): return M("wood", (0.50, 0.32, 0.20), rough=0.8, bump=0.4, scale=30)
def m_dark(): return M("darkwood", (0.30, 0.19, 0.14), rough=0.75, bump=0.3)
def m_stone(): return M("stone", (0.74, 0.68, 0.60), rough=0.9, bump=0.5, scale=22, var=0.1)
def m_thatch(k): return M(f"thatch{k}", [(0.90, 0.72, 0.36), (0.82, 0.62, 0.30), (0.95, 0.80, 0.46)][k % 3], rough=0.95, bump=0.8, scale=90, var=0.12)
def m_moss(): return M("moss", (0.42, 0.62, 0.30), rough=0.95, bump=0.6, scale=45, var=0.1)
def m_leaf(i): return M(f"leaf{i}", [(0.45, 0.65, 0.30), (0.36, 0.57, 0.30), (0.58, 0.72, 0.32), (0.92, 0.60, 0.50)][i % 4], rough=0.9, bump=0.5, scale=35)
def m_win(): return M("win", (1.0, 0.82, 0.45), rough=0.4, emit=(1.0, 0.66, 0.22), strength=9.0, tex='none')
def m_lamp(): return M("lamp", (1, 0.85, 0.5), rough=0.4, emit=(1.0, 0.70, 0.28), strength=25.0, tex='none')
def m_smoke(): return M("smoke", (0.97, 0.93, 0.90), rough=1.0, bump=0.2, scale=20)
def m_red(): return M("barnred", (0.74, 0.26, 0.20), rough=0.85, bump=0.4)
def m_hay(): return M("hay", (0.93, 0.76, 0.36), rough=0.95, bump=0.7, scale=60)
def m_trunk(): return M("trunk", (0.45, 0.30, 0.20), rough=0.9, bump=0.5)
def m_white(): return M("white", (0.99, 0.96, 0.90), rough=0.85)
def m_awn(k): return M(f"awn{k}", [(0.86, 0.30, 0.28), (0.30, 0.60, 0.45)][k % 2], rough=0.8, bump=0.3, scale=100)


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
        pb = bmesh.new()
        vs = [pb.verts.new(v) for v in verts]
        for f in faces:
            pb.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(pb, faces=pb.faces)
        if bevel > 0:
            bmesh.ops.bevel(pb, geom=list(pb.edges), offset=bevel, segments=2, affect='EDGES')
        idx = self.slot(m)
        mp = {v: self.bm.verts.new(v.co) for v in pb.verts}
        for f in pb.faces:
            self.bm.faces.new([mp[v] for v in f.verts]).material_index = idx
        pb.free()

    def box(self, x0, y0, z0, x1, y1, z1, m, bevel=0.0):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.part(v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, bevel)

    def lbox(self, fr, u0, u1, z0, z1, o0, o1, m, bevel=0.0):
        O, T, Nn = fr
        Z = Vector((0, 0, 1))
        v = []
        for z in (z0, z1):
            pass
        pts = []
        for (u, z, o) in ((u0, z0, o0), (u1, z0, o0), (u1, z0, o1), (u0, z0, o1),
                          (u0, z1, o0), (u1, z1, o0), (u1, z1, o1), (u0, z1, o1)):
            pts.append(tuple(O + T * u + Z * z + Nn * o))
        self.part(pts, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, bevel)

    def lcyl(self, fr, u, z, o0, o1, r, m, n=12, bevel=0.0):
        O, T, Nn = fr
        Z = Vector((0, 0, 1))
        v = []
        for o in (o0, o1):
            for k in range(n):
                a = 2 * math.pi * k / n
                v.append(tuple(O + T * (u + r * math.cos(a)) + Z * (z + r * math.sin(a)) + Nn * o))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m, bevel)

    def cyl(self, cx, cy, z0, z1, r, m, n=14, r2=None, bevel=0.0):
        r2 = r if r2 is None else r2
        v = []
        for rad, zz in ((r, z0), (r2, z1)):
            for k in range(n):
                a = 2 * math.pi * k / n
                v.append((cx + rad * math.cos(a), cy + rad * math.sin(a), zz))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m, bevel)

    def bar(self, p0, p1, t1, t2, m, ref=(1, 0, 0), bevel=0.0):
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
        self.part(v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, bevel)

    def sphere(self, cx, cy, cz, r, m, sub=2, sx=1.0, sy=1.0, sz=1.0):
        pb = bmesh.new()
        bmesh.ops.create_icosphere(pb, subdivisions=sub, radius=r)
        idx = self.slot(m)
        mp = {v: self.bm.verts.new((v.co.x * sx + cx, v.co.y * sy + cy, v.co.z * sz + cz)) for v in pb.verts}
        for f in pb.faces:
            self.bm.faces.new([mp[v] for v in f.verts]).material_index = idx
        pb.free()

    def cone(self, cx, cy, z0, z1, r, m, n=12, bevel=0.0):
        v = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z0) for k in range(n)]
        v.append((cx, cy, z1))
        self.part(v, [tuple(range(n - 1, -1, -1))] + [(k, (k + 1) % n, n) for k in range(n)], m, bevel)

    def warp(self, amp, seed):
        """pareti non dritte: deformazione morbida e deterministica (sag + onde a bassa frequenza)."""
        r = random.Random(seed)
        p = [r.uniform(0, 6.28) for _ in range(8)]
        for v in self.bm.verts:
            x, y, z = v.co
            v.co.x += amp * (math.sin(z * 2.6 + p[0] + y * 1.3) + 0.6 * math.sin(y * 3.1 + p[1]))
            v.co.y += amp * (math.sin(z * 2.2 + p[2] + x * 1.1) + 0.6 * math.sin(x * 2.7 + p[3]))
            v.co.z += amp * 0.5 * math.sin(x * 2.0 + p[4]) * math.sin(y * 2.3 + p[5]) * (z / 1.5)

    def build(self, name, smooth=True):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        for f in self.bm.faces:
            f.smooth = smooth
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.slots:
            me.materials.append(m)
        return me


def frames(w, d):
    X, Y = Vector((1, 0, 0)), Vector((0, 1, 0))
    return {'F': (Vector((0, -d / 2, 0)), X, -Y), 'B': (Vector((0, d / 2, 0)), -X, Y),
            'R': (Vector((w / 2, 0, 0)), Y, X), 'L': (Vector((-w / 2, 0, 0)), -Y, -X)}


# ---------------------------------------------------------------- dettagli
def window(b, fr, u, z, ww, wh, sh, rg, flowers=True, shutters=True, arch=False):
    t = m_trim()
    b.lbox(fr, u - ww / 2 - 0.05, u + ww / 2 + 0.05, z - wh / 2 - 0.05, z + wh / 2 + 0.05, -0.02, 0.05, m_wood(), 0.03)
    b.lbox(fr, u - ww / 2, u + ww / 2, z - wh / 2, z + wh / 2, 0.0, 0.07, m_win(), 0.015)
    if arch:
        b.lcyl(fr, u, z + wh / 2, 0.0, 0.07, ww / 2, m_win(), 10)
    b.lbox(fr, u - 0.012, u + 0.012, z - wh / 2, z + wh / 2, 0.06, 0.095, m_wood())
    b.lbox(fr, u - ww / 2, u + ww / 2, z - 0.012, z + 0.012, 0.06, 0.095, m_wood())
    b.lbox(fr, u - ww / 2 - 0.08, u + ww / 2 + 0.08, z - wh / 2 - 0.09, z - wh / 2 - 0.03, 0.0, 0.14, t, 0.02)
    if shutters:
        for sd in (-1, 1):
            uc = u + sd * (ww / 2 + 0.17)
            b.lbox(fr, uc - 0.1, uc + 0.1, z - wh / 2 - 0.03, z + wh / 2 + 0.03, 0.0, 0.05, m_shut(sh), 0.02)
    if flowers:
        b.lbox(fr, u - ww / 2 - 0.06, u + ww / 2 + 0.06, z - wh / 2 - 0.2, z - wh / 2 - 0.05, 0.02, 0.17, m_wood(), 0.02)
        for k in range(5):
            uu = u - ww / 2 + (k + 0.5) * ww / 5
            O, T, Nn = fr
            p = O + T * uu + Vector((0, 0, 1)) * (z - wh / 2 - 0.12) + Nn * 0.1
            b.sphere(p.x, p.y, p.z, 0.07 + 0.015 * rg.random(), m_flow(rg.randrange(5)) if k % 2 else m_leaf(rg.randrange(3)), 1)


def door(b, fr, u, wd, hd, dc, rg, pot=True):
    O, T, Nn = fr
    b.lbox(fr, u - wd / 2 - 0.07, u + wd / 2 + 0.07, 0.0, hd + 0.0, -0.02, 0.06, m_trim(), 0.03)
    b.lcyl(fr, u, hd, -0.02, 0.06, wd / 2 + 0.07, m_trim(), 12)
    b.lbox(fr, u - wd / 2, u + wd / 2, 0.0, hd, 0.0, 0.08, m_shut(dc), 0.02)
    b.lcyl(fr, u, hd, 0.0, 0.08, wd / 2, m_shut(dc), 12)
    p = O + T * (u + wd * 0.28) + Vector((0, 0, 0.3)) + Nn * 0.1
    b.sphere(p.x, p.y, p.z, 0.028, m_lamp(), 1)
    b.lbox(fr, u - wd / 2 - 0.2, u + wd / 2 + 0.2, -0.0, 0.07, 0.0, 0.42, m_stone(), 0.03)       # gradino tondo
    if pot:
        uu = u + wd / 2 + 0.28
        p = O + T * uu + Nn * 0.2
        b.cyl(p.x, p.y, 0.0, 0.17, 0.09, m_red(), 10, r2=0.11, bevel=0.02)
        for k in range(3):
            q = p + Vector((rg.uniform(-0.04, 0.04), rg.uniform(-0.04, 0.04), 0.2 + 0.05 * k))
            b.sphere(q.x, q.y, q.z, 0.07, m_flow(rg.randrange(5)) if k else m_leaf(0), 1)


def sign(b, fr, u, z, rg, txt=0):
    O, T, Nn = fr
    p = O + T * u + Nn * 0.02
    b.lbox(fr, u - 0.01, u + 0.01, z + 0.1, z + 0.12, 0.02, 0.42, m_dark())
    b.lbox(fr, u - 0.19, u + 0.19, z - 0.16, z + 0.08, 0.38, 0.43, m_wood(), 0.03)
    b.lcyl(fr, u, z - 0.04, 0.43, 0.47, 0.09, m_hay() if txt % 2 == 0 else m_red(), 10)


def ivy(b, fr, wl, hgt, rg, n=26):
    O, T, Nn = fr
    u0 = rg.uniform(-wl * 0.4, wl * 0.4)
    for k in range(n):
        u = u0 + rg.uniform(-0.28, 0.28) * (1 + 0.8 * k / n)
        z = hgt * (k / n) ** 0.9 * 1.0 + rg.uniform(0, 0.1)
        p = O + T * u + Vector((0, 0, z)) + Nn * 0.04
        b.sphere(p.x, p.y, p.z, rg.uniform(0.07, 0.14), m_leaf(rg.randrange(2)), 1, sz=0.8)
        if rg.random() < 0.18:
            b.sphere(p.x + Nn.x * 0.05, p.y + Nn.y * 0.05, p.z, 0.04, m_flow(rg.randrange(5)), 1)


def chimney(b, x, y, zt, rg, smoke=True):
    lean = rg.uniform(-0.05, 0.05)
    b.box(x - 0.15, y - 0.15, zt - 0.2, x + 0.15, y + 0.15, zt + 0.45, m_stone(), 0.04)
    b.box(x - 0.19 + lean, y - 0.19, zt + 0.4, x + 0.19 + lean, y + 0.19, zt + 0.52, m_stone(), 0.03)
    if smoke:
        for k in range(4):
            r = 0.06 + 0.03 * k
            b.sphere(x + lean + 0.08 * k + 0.05 * math.sin(k * 2), y + 0.03 * k, zt + 0.7 + 0.2 * k, r, m_smoke(), 2)


def roof_gable(b, w, d, zt, rh, rm, kind, rg, oe=0.16, ov=0.22, rows=7):
    """tetto a due falde (colmo lungo x), spesso e morbido, con scaglie/paglia."""
    hs = d / 2 + ov
    for sg in (-1, 1):
        e = Vector((0, sg * hs, zt - 0.04))
        r_ = Vector((0, 0, zt + rh))
        n_ = Vector((0, -sg * rh, hs)).normalized() * -1   # normale esterna approssimata
        n_ = (r_ - e).cross(Vector((1, 0, 0)))
        if n_.z < 0:
            n_ = -n_
        n_.normalize()
        base_m = rm
        b.bar(e - n_ * 0.07, r_ - n_ * 0.07 + Vector((0, 0, 0.02)), 0.12, w + 2 * oe, base_m, bevel=0.04)
        ln = (r_ - e).length
        for j in range(rows):
            t0 = j / rows
            t1 = min(1.0, t0 + 1.6 / rows)
            for c in range(max(3, int((w + 2 * oe) / 0.2))):
                cw = (w + 2 * oe) / max(3, int((w + 2 * oe) / 0.2))
                xc = -(w + 2 * oe) / 2 + cw * (c + 0.5 + (0.5 if j % 2 else 0.0))
                if abs(xc) > (w + 2 * oe) / 2 - 0.02:
                    continue
                jit = rg.uniform(-0.02, 0.03)
                mm = rm
                if kind == 'thatch':
                    mm = m_thatch(rg.randrange(3)); t1 = min(1.0, t0 + 2.4 / rows) + jit
                p0 = e + (r_ - e) * t0 + n_ * 0.015
                p1 = e + (r_ - e) * t1 + n_ * 0.07
                p0.x = p1.x = xc
                b.bar(p0, p1, 0.04 if kind != 'thatch' else 0.06, cw * (0.97 if kind != 'thatch' else 1.1), mm,
                      bevel=0.02 if kind != 'thatch' else 0.015)
                if kind == 'moss' and rg.random() < 0.22:
                    q = (p0 + p1) / 2 + n_ * 0.05
                    b.sphere(q.x, q.y, q.z, rg.uniform(0.07, 0.14), m_moss(), 1, sz=0.5)
    # gronda tonda sul colmo
    b.lbox((Vector((0, 0, zt + rh)), Vector((1, 0, 0)), Vector((0, -1, 0))), -(w / 2 + oe), (w / 2 + oe), -0.07, 0.09, -0.12, 0.07,
           m_thatch(0) if kind == 'thatch' else rm, 0.045)
    if kind == 'moss':
        for k in range(7):
            b.sphere(rg.uniform(-w / 2, w / 2), rg.uniform(-0.15, 0.15), zt + rh + 0.06, rg.uniform(0.09, 0.15), m_moss(), 1, sz=0.6)


def gable_fill(b, w, d, zt, rh, wm):
    for sx in (-1, 1):
        x0 = sx * (w / 2 - 0.03)
        v = [(x0, -d / 2, zt), (x0, d / 2, zt), (x0, 0, zt + rh * 0.92)]
        v2 = [(x0 - sx * 0.12, -d / 2, zt), (x0 - sx * 0.12, d / 2, zt), (x0 - sx * 0.12, 0, zt + rh * 0.92)]
        b.part(v + v2, [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], wm, 0.02)


# ---------------------------------------------------------------- tipi di casa (8)
def mk_house(tp, var, seed):
    rg = random.Random(seed * 131 + tp * 17 + var)
    b = MB()
    ci = (tp * 2 + var * 3) % 7
    ri = (tp + var * 2) % 5
    sh = (tp + var) % 5
    dc = (tp + var * 2) % 5
    if tp == 7:
        return mill(b, rg, var)
    spec = {
        0: dict(w=2.3, d=1.7, fl=1, kind='tile', hs=0.62, rh=1.0, feat=('awning', 'sign', 'chimney')),     # panetteria
        1: dict(w=1.7, d=1.5, fl=2, kind='tile', hs=0.66, rh=0.85, feat=('chimney', 'timber', 'ivy')),       # casa a graticcio alta
        2: dict(w=2.1, d=1.6, fl=1, kind='thatch', hs=0.66, rh=1.0, feat=('chimney', 'ivy')),                # cottage paglia
        3: dict(w=1.9, d=1.7, fl=1, kind='moss', hs=0.7, rh=0.95, feat=('chimney', 'stonewall')),            # pietra muschio
        4: dict(w=1.8, d=1.55, fl=1, kind='tile', hs=0.66, rh=0.9, feat=('chimney', 'ivy', 'dormer')),       # rampicanti
        5: dict(w=2.0, d=1.5, fl=1, kind='tile', hs=0.62, rh=0.8, feat=('awning', 'sign', 'lantern')),       # bottega
        6: dict(w=2.4, d=1.9, fl=1, kind='tile', hs=0.9, rh=1.15, feat=('barn',)),                           # fienile
    }[tp]
    w = spec['w'] * rg.uniform(0.95, 1.1); d = spec['d'] * rg.uniform(0.95, 1.08)
    hs = spec['hs']; fl = spec['fl']; H = hs * fl + (0.05 if fl > 1 else 0)
    feat = spec['feat']
    wm = m_red() if 'barn' in feat else (m_stone() if 'stonewall' in feat else m_wall(ci))
    rm = m_red() if False else m_roof(ri + (3 if 'barn' in feat else 0))
    if spec['kind'] == 'thatch':
        rm = m_thatch(var)
    elif spec['kind'] == 'moss':
        rm = m_roof(2)
    fr = frames(w, d)
    # base di pietra (fondazione sotto il terreno) + muri tondi
    b.box(-w / 2 - 0.06, -d / 2 - 0.06, -2.2, w / 2 + 0.06, d / 2 + 0.06, 0.12, m_stone(), 0.05)
    b.box(-w / 2, -d / 2, 0.05, w / 2, d / 2, hs, wm, 0.11)
    if fl == 2:
        o = 0.1
        b.box(-w / 2 - o, -d / 2 - o, hs - 0.02, w / 2 + o, d / 2 + o, H + hs - 0.05 + 0.0, wm, 0.1)
        H = hs * 2
    # graticcio
    if 'timber' in feat:
        for xs in (-0.38, 0.0, 0.38):
            b.lbox(fr['F'], xs * w - 0.03, xs * w + 0.03, hs + 0.05, hs * 2 - 0.05, 0.1, 0.14, m_dark(), 0.015)
        b.lbox(fr['F'], -w / 2 - 0.05, w / 2 + 0.05, hs - 0.08, hs + 0.04, 0.1, 0.15, m_dark(), 0.02)
        b.lbox(fr['F'], -w / 2 - 0.05, w / 2 + 0.05, hs * 2 - 0.1, hs * 2, 0.1, 0.15, m_dark(), 0.02)
    # tetto
    zt = H - 0.02
    gable_fill(b, w, d, zt, spec['rh'], wm if 'barn' not in feat else m_red())
    roof_gable(b, w, d, zt, spec['rh'], rm, spec['kind'], rg, rows=7 if fl == 1 else 6)
    # lato porta F
    wl = fr['F']
    if 'barn' in feat:
        b.lbox(wl, -0.5, 0.5, 0.0, 0.8, 0.0, 0.07, m_dark(), 0.03)
        b.lbox(wl, -0.5, 0.0, 0.0, 0.8, 0.07, 0.1, m_wood(), 0.02)
        b.lbox(wl, 0.0, 0.5, 0.0, 0.8, 0.07, 0.1, m_wood(), 0.02)
        window(b, wl, -0.85, 1.1, 0.3, 0.3, sh, rg, False, True)
        window(b, wl, 0.85, 1.1, 0.3, 0.3, sh, rg, False, True)
        window(b, fr['R'], 0.0, 0.55, 0.45, 0.4, sh, rg, True, True)
        # balle di fieno
        for k in range(3):
            b.cyl(w / 2 + 0.35 + 0.3 * k, -d / 2 + 0.1 + 0.15 * k, 0.0, 0.45, 0.27, m_hay(), 12, bevel=0.05)
    else:
        du = rg.choice((-1, 1)) * 0.28 * w if fl == 1 else -0.28 * w
        door(b, wl, du, 0.32, 0.5, dc, rg)
        ws = [x for x in (-0.3 * w * (1 if du > 0 else -1) * -1,)]
        wu = -du * 1.35 if abs(du) > 0.1 else 0.5
        window(b, wl, wu, 0.38, 0.36, 0.44, sh, rg, True, True)
        if fl == 2:
            window(b, wl, -0.28 * w, hs + 0.38, 0.36, 0.44, sh, rg, True, True)
            window(b, wl, 0.28 * w, hs + 0.38, 0.36, 0.44, sh, rg, True, True)
        for s in ('R', 'L'):
            window(b, fr[s], rg.uniform(-0.2, 0.2), 0.42 if fl == 1 else hs + 0.4, 0.3, 0.4, sh, rg, rg.random() < 0.6, False)
        window(b, fr['B'], 0.0, 0.42, 0.3, 0.4, sh, rg, False, False)
    if 'awning' in feat:
        bo = wl[0] + Vector((0, 0, 0))
        for k in range(8):
            uu = -0.6 + k * 0.15
            b.lbox(wl, uu, uu + 0.15, 0.68 + 0.04 * (k % 2), 0.95, 0.0, 0.5, m_awn(0) if k % 2 == 0 else m_white(), 0.03)
        b.lbox(wl, -0.6, 0.6, 0.64, 0.74, 0.45, 0.5, m_awn(0), 0.02)
    if 'sign' in feat:
        sign(b, fr['F'], 0.95 if tp == 0 else -0.95, 0.75, rg, tp)
    if 'lantern' in feat:
        O, T, Nn = fr['F']
        for sd in (-1, 1):
            p = O + T * (sd * (w * 0.46)) + Nn * 0.32 + Vector((0, 0, 0.8))
            b.cyl(p.x, p.y, 0.0, 0.78, 0.025, m_dark(), 6)
            b.sphere(p.x, p.y, p.z + 0.04, 0.085, m_lamp(), 1)
    if 'ivy' in feat:
        ivy(b, fr[rg.choice('RLF')], d, H + 0.05, rg)
        if rg.random() < 0.7:
            ivy(b, fr['R'], d, H, rg)
    if 'dormer' in feat:
        zq = zt + spec['rh'] * 0.35
        O = Vector((rg.uniform(-0.3, 0.3), -d / 2 * 0.45, zq))
        b.box(O.x - 0.28, O.y - 0.14, zq - 0.06, O.x + 0.28, O.y + 0.2, zq + 0.34, wm, 0.06)
        window(b, (Vector((O.x, O.y - 0.14, zq - 0.06)), Vector((1, 0, 0)), Vector((0, -1, 0))), 0, 0.18, 0.26, 0.3, sh, rg, False, False)
        b.bar((O.x, O.y - 0.2, zq + 0.34), (O.x, O.y + 0.35, zq + 0.55), 0.06, 0.7, rm, bevel=0.02)
    if 'chimney' in feat:
        chimney(b, w * rg.uniform(0.15, 0.32) * rg.choice((-1, 1)), -d * 0.1, zt + spec['rh'] * 0.55, rg)
    b.warp(0.012 + 0.008 * var, seed * 7 + tp)
    return b.build(f"house{tp}_{var}")


def mill(b, rg, var):
    wm = m_wall(5)
    b.cyl(0, 0, -0.9, 0.2, 1.0, m_stone(), 16, bevel=0.05)
    b.cyl(0, 0, 0.1, 2.5, 0.85, wm, 16, r2=0.58, bevel=0.06)
    b.cone(0, 0, 2.4, 3.5, 0.78, m_roof(0), 16, bevel=0.04)
    b.sphere(0, 0, 3.58, 0.1, m_wood(), 1)
    fr = frames(1.7, 1.7)
    door(b, (Vector((0, -0.85, 0)), Vector((1, 0, 0)), Vector((0, -1, 0))), 0, 0.34, 0.55, 2, rg)
    for z, rr in ((1.2, 0.74), (1.9, 0.64)):
        window(b, (Vector((0, -rr, 0)), Vector((1, 0, 0)), Vector((0, -1, 0))), 0, z, 0.3, 0.36, 1, rg, False, True)
    # pale
    hub = Vector((0, -0.72, 2.2))
    ang0 = rg.uniform(0.2, 0.7)
    for k in range(4):
        a = ang0 + k * math.pi / 2
        dv = Vector((math.cos(a), 0, math.sin(a)))
        b.bar(hub - Vector((0, 0.1, 0)), hub + dv * 1.7 - Vector((0, 0.1, 0)), 0.05, 0.08, m_dark(), ref=(0, 1, 0), bevel=0.01)
        pv = Vector((-dv.z, 0, dv.x))
        for s in range(2):
            c = hub + dv * (0.7 + 0.8 * s) + pv * 0.18 - Vector((0, 0.14, 0))
            b.bar(c - dv * 0.3, c + dv * 0.3, 0.025, 0.3, m_white(), ref=(0, 1, 0), bevel=0.01)
    b.sphere(hub.x, hub.y - 0.1, hub.z, 0.12, m_wood(), 1)
    b.warp(0.012, 3 + var)
    return b.build(f"house7_{var}")


def mk_tree(kind, seed):
    rg = random.Random(seed)
    b = MB()
    if kind == 0:   # albero tondo da favola
        h = rg.uniform(1.1, 1.5)
        b.cyl(0, 0, -0.2, h, 0.13, m_trunk(), 8, r2=0.09, bevel=0.01)
        for k in range(6):
            b.sphere(rg.uniform(-0.45, 0.45), rg.uniform(-0.4, 0.4), h + rg.uniform(0.2, 0.75), rg.uniform(0.45, 0.65), m_leaf(rg.randrange(3) if k else 0), 2)
    elif kind == 1:  # cespuglio con fiori
        for k in range(5):
            b.sphere(rg.uniform(-0.25, 0.25), rg.uniform(-0.25, 0.25), 0.12 + rg.uniform(0, 0.15), rg.uniform(0.22, 0.34), m_leaf(rg.randrange(2)), 2)
        for k in range(8):
            b.sphere(rg.uniform(-0.4, 0.4), rg.uniform(-0.4, 0.4), rg.uniform(0.15, 0.4), 0.045, m_flow(rg.randrange(5)), 1)
    elif kind == 2:  # covone
        b.cyl(0, 0, -0.1, 0.55, 0.38, m_hay(), 12, r2=0.3, bevel=0.04)
        b.sphere(0, 0, 0.58, 0.31, m_hay(), 2, sz=0.8)
    elif kind == 3:  # lampione
        b.cyl(0, 0, -0.2, 1.0, 0.03, m_dark(), 6)
        b.sphere(0, 0, 1.08, 0.1, m_lamp(), 2)
        b.cone(0, 0, 1.15, 1.3, 0.13, m_dark(), 6)
    elif kind == 4:  # ciuffo d'erba
        for k in range(22):
            a = rg.uniform(0, 6.28); r = rg.uniform(0.0, 0.14); hh = rg.uniform(0.3, 0.7)
            lean = rg.uniform(0.08, 0.28)
            x0, y0 = r * math.cos(a), r * math.sin(a)
            b.part([(x0 - 0.025, y0, 0), (x0 + 0.025, y0, 0), (x0, y0 + 0.02, 0),
                    (x0 + 0.01 + lean * math.cos(a + 1), y0 + lean * math.sin(a + 1), hh)],
                   [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)], m_leaf(rg.randrange(3)))
    elif kind == 5:  # fiore di campo
        for k in range(4):
            a = rg.uniform(0, 6.28); r = rg.uniform(0.0, 0.1); hh = rg.uniform(0.35, 0.6)
            b.bar((r * math.cos(a), r * math.sin(a), 0), (r * math.cos(a) * 1.2, r * math.sin(a) * 1.2, hh), 0.014, 0.014, m_leaf(1))
            fm = m_flow(rg.randrange(5))
            b.sphere(r * math.cos(a) * 1.2, r * math.sin(a) * 1.2, hh + 0.02, 0.055, fm, 1)
            b.sphere(r * math.cos(a) * 1.2, r * math.sin(a) * 1.2, hh + 0.05, 0.02, m_hay(), 1)
    elif kind == 6:  # spiga di grano
        for k in range(10):
            a = rg.uniform(0, 6.28); r = rg.uniform(0, 0.1); hh = rg.uniform(0.5, 0.8)
            tx, ty = r * math.cos(a) + rg.uniform(-0.05, 0.05), r * math.sin(a) + rg.uniform(-0.05, 0.05)
            b.bar((r * math.cos(a), r * math.sin(a), 0), (tx, ty, hh), 0.012, 0.012, m_hay())
            b.sphere(tx, ty, hh + 0.05, 0.03, m_hay(), 1, sz=2.4)
    elif kind == 7:  # staccionata (3 doghe)
        for k in range(3):
            x = (k - 1) * 0.34
            b.box(x - 0.04, -0.02, -0.1, x + 0.04, 0.02, 0.38, m_wood(), 0.012)
        b.box(-0.5, -0.04, 0.12, 0.5, 0.0, 0.17, m_wood(), 0.01)
    elif kind == 8:  # pozzo
        b.cyl(0, 0, -0.1, 0.4, 0.38, m_stone(), 12, bevel=0.04)
        b.cyl(0, 0, 0.38, 0.41, 0.3, m_M_water(), 12)
        for sx in (-1, 1):
            b.box(sx * 0.4 - 0.03, -0.03, 0.3, sx * 0.4 + 0.03, 0.03, 1.0, m_wood())
        b.bar((-0.5, 0, 1.0), (0, 0, 1.3), 0.05, 0.9, m_roof(0), ref=(0, 1, 0), bevel=0.02)
        b.bar((0, 0, 1.3), (0.5, 0, 1.0), 0.05, 0.9, m_roof(0), ref=(0, 1, 0), bevel=0.02)
    return b.build(f"prop{kind}_{seed}")


def m_M_water():
    return M("water", (0.45, 0.72, 0.8), rough=0.1, tex='none')


# ---------------------------------------------------------------- disposizione
def lot(i, seed):
    """lotto i: posizione, rotazione, tipo, variante, scala. Deterministico, indipendente da N."""
    rg = random.Random(seed * 100003 + i)
    r = A_SP * math.sqrt(i + 0.7)
    a = i * GA
    jit = 0.28 if i > 0 else 0.0
    x = r * math.cos(a) + rg.uniform(-jit, jit) * A_SP
    y = r * math.sin(a) + rg.uniform(-jit, jit) * A_SP
    special = [0, 1, 2, 3, 4, 5, 6, 1, 2, 4, 3, 5, 2, 7]
    if i < len(special):
        tp = special[i]
    else:
        tp = rg.choices(range(8), weights=[1.2, 2, 2.2, 1.8, 2, 1.4, 1, 0.12])[0]
    return dict(i=i, x=x, y=y, tp=tp, var=rg.randrange(3), sc=rg.uniform(0.92, 1.18) * (1.1 if i < 3 else 1.0),
                jrot=rg.uniform(-0.5, 0.5), rg=rg)


def parent_of(i, lots):
    if i == 0:
        return None
    best, bd = 0, 1e9
    for k in range(max(0, i - 60), i):
        d = (lots[k]['x'] - lots[i]['x']) ** 2 + (lots[k]['y'] - lots[i]['y']) ** 2
        if d < bd:
            best, bd = k, d
    return best


def camera_for(N):
    """camera(N) continua: bassa e macro per N piccolo, sale e si allontana con N (max ~25 gradi).
    Ritorna (pos, target, lens, fstop, focus_dist)."""
    Rc = A_SP * math.sqrt(N + 0.7)
    lens = 70.0 + 15.0 * math.exp(-N / 220.0)
    Wv = 1.05 * Rc + 1.9
    d = Wv * lens / 20.25
    pitch = math.radians(2.0 + 7.0 * (1 - math.exp(-N / 300.0)))
    az = math.radians(-90 - 14)
    zc = hill(Rc * 0.55)
    ty = 0.1 * Rc
    tz = zc + 0.9 + 0.1 * Rc + 0.45 * (hill(Rc * 0.3) - zc)
    h = tz + d * math.tan(pitch)
    pos = (d * math.cos(az), d * math.sin(az) + ty, h)
    tgt = (0.0, ty, tz)
    # focus sul bordo anteriore del cluster
    fd = d - 0.5 * Rc
    fstop = 0.4 * (1 - 0.25 * N / (N + 300.0))    # DOF forte (sensore 36mm): piu' aperto = piu' sfocato
    return pos, tgt, lens, fstop, fd, d


def link(obj, coll):
    coll.objects.link(obj)
    return obj


def polar_ground(R, rings=110, segs=160, hfun=None):
    bm = bmesh.new()
    rs = [0.0] + [R * ((k / rings) ** 2.2) for k in range(1, rings + 1)]
    grid = []
    for ri, r in enumerate(rs):
        row = []
        for s in range(segs if ri else 1):
            a = 2 * math.pi * s / segs
            x, y = r * math.cos(a), r * math.sin(a)
            row.append(bm.verts.new((x, y, hfun(x, y, r, a))))
        grid.append(row)
    for ri in range(1, len(rs)):
        for s in range(segs):
            s2 = (s + 1) % segs
            if ri == 1:
                bm.faces.new([grid[0][0], grid[1][s], grid[1][s2]])
            else:
                bm.faces.new([grid[ri - 1][s], grid[ri][s], grid[ri][s2], grid[ri - 1][s2]])
    me = bpy.data.meshes.new("ground")
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


PAD = {'c': (0, 0, 0), 'k': 0.0}


def ground_h(x, y, r, a):
    h = hill(r)
    if PAD['k'] > 0.02:
        cx, cy = PAD['c'][0], PAD['c'][1]
        L = math.hypot(cx, cy); ux, uy = cx / L, cy / L
        t = x * ux + y * uy; lat = -x * uy + y * ux
        sv = min(1.0, max(0.0, (t - PAD['Rc'] * 0.6) / (PAD['d'] * 1.05 - PAD['Rc'] * 0.6)))
        sv = sv * sv * (3 - 2 * sv)
        ph = PAD['zv'] + (PAD['gz'] - PAD['zv']) * sv
        wl = math.exp(-(lat / (0.6 * PAD['d'])) ** 2) * PAD['k']
        if t > 0:
            h += wl * max(0.0, ph - h)
    far = min(1.0, max(0.0, (r - 110) / 330.0)); far = far * far * (3 - 2 * far)
    ang = 1.0 + 0.5 * math.sin(a * 2.0 + 1.0) + 0.35 * math.sin(a * 5.0 + 2.0)
    h += far * (24 * ang + 6 * math.sin(r * 0.03))
    h += 0.18 * math.sin(x * 0.9 + y * 0.7) * math.sin(y * 1.1 - x * 0.4) * min(1.0, r / 4.0) * (1 if r < 90 else 0.0)
    return h


def gz(x, y):
    return ground_h(x, y, math.hypot(x, y), math.atan2(y, x))


def ground_material(k):
    m = bpy.data.materials.new("ground"); m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.95
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.35; n1.inputs["Detail"].default_value = 3
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 40; n2.inputs["Detail"].default_value = 5
    nt.links.new(tc.outputs["Object"], n1.inputs["Vector"]); nt.links.new(tc.outputs["Object"], n2.inputs["Vector"])
    n3 = nt.nodes.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 0.03; n3.inputs["Detail"].default_value = 2
    nt.links.new(tc.outputs["Object"], n3.inputs["Vector"])
    pr = nt.nodes.new("ShaderNodeMapRange"); pr.inputs["From Min"].default_value = 0.46; pr.inputs["From Max"].default_value = 0.54
    nt.links.new(n3.outputs["Fac"], pr.inputs["Value"])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'
    nt.links.new(tc.outputs["Object"], ln.inputs[0])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["From Min"].default_value = 30; rr.inputs["From Max"].default_value = 80
    nt.links.new(ln.outputs["Value"], rr.inputs["Value"])
    wf = nt.nodes.new("ShaderNodeMath"); wf.operation = 'MULTIPLY'
    nt.links.new(pr.outputs["Result"], wf.inputs[0]); nt.links.new(rr.outputs["Result"], wf.inputs[1])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    ce = cr.color_ramp.elements
    ce[0].position = 0.38; ce[0].color = (*lin((0.38, 0.58, 0.26)), 1)
    ce[1].position = 0.62; ce[1].color = (*lin((0.66, 0.74, 0.30)), 1)
    nt.links.new(n1.outputs["Fac"], cr.inputs["Fac"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(wf.outputs["Value"], mx.inputs[0])
    nt.links.new(cr.outputs["Color"], mx.inputs[6])
    mx.inputs[7].default_value = (*lin((0.88, 0.70, 0.30)), 1)
    # foschia dorata con la distanza dalla camera
    cd = nt.nodes.new("ShaderNodeCameraData")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 90.0 * k; mr.inputs["From Max"].default_value = 900.0 * k
    mr.inputs["To Max"].default_value = 0.85
    nt.links.new(cd.outputs["View Distance"], mr.inputs["Value"])
    hz = nt.nodes.new("ShaderNodeMix"); hz.data_type = 'RGBA'
    hz.inputs[7].default_value = (*lin((1.0, 0.78, 0.45)), 1)
    nt.links.new(mr.outputs["Result"], hz.inputs[0])
    nt.links.new(mx.outputs[2], hz.inputs[6])
    gn = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(gn.outputs["Normal"], sn.inputs["Vector"])
    sr = nt.nodes.new("ShaderNodeMapRange"); sr.inputs["From Min"].default_value = 0.93; sr.inputs["From Max"].default_value = 0.6
    nt.links.new(sn.outputs["Z"], sr.inputs["Value"])
    st = nt.nodes.new("ShaderNodeMix"); st.data_type = 'RGBA'; st.inputs[7].default_value = (*lin((0.70, 0.62, 0.52)), 1)
    nt.links.new(sr.outputs["Result"], st.inputs[0]); nt.links.new(hz.outputs[2], st.inputs[6])
    nt.links.new(st.outputs[2], bsdf.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; bp.inputs["Distance"].default_value = 0.05
    nt.links.new(n2.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def path_material():
    m = bpy.data.materials.new("path"); m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.9
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 7.0
    vo.feature = 'DISTANCE_TO_EDGE'
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*lin((0.55, 0.40, 0.28)), 1)
    cr.color_ramp.elements[1].color = (*lin((0.80, 0.66, 0.46)), 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.9; bp.inputs["Distance"].default_value = 0.04
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Max"].default_value = 0.12
    nt.links.new(vo.outputs["Distance"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def wheat_material():
    m = bpy.data.materials.new("wheat"); m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.9
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 5
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*lin((0.80, 0.60, 0.22)), 1)
    cr.color_ramp.elements[1].color = (*lin((0.98, 0.84, 0.44)), 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; bp.inputs["Distance"].default_value = 0.03
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def build_scene(N, seed, res, samples):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    coll = sc.collection
    pos, tgt, lens, fstop, fdist, cdist = camera_for(N)
    k = max(1.0, cdist / 28.0)          # fattore di scala degli elementi di scenografia (primo piano)
    lots = [lot(i, seed) for i in range(N)]
    Rv = max(math.hypot(l['x'], l['y']) for l in lots) + 2.2

    # ---- terreno + colline lontane
    PAD['c'] = pos; PAD['d'] = cdist; PAD['Rc'] = A_SP * math.sqrt(N + 0.7); PAD['zv'] = hill(PAD['Rc'] * 0.6)
    PAD['gz'] = pos[2] - 1.5; PAD['k'] = math.exp(-N / 200.0)
    gm = polar_ground(1600, 800, 360, ground_h)
    go = link(bpy.data.objects.new("ground", gm), coll)
    go.data.materials.append(ground_material(k))

    # ---- case (mesh condivise: 8 tipi x 3 varianti; istanze)
    cache = {}
    def house_mesh(tp, var):
        if (tp, var) not in cache:
            cache[(tp, var)] = mk_house(tp, var, seed)
        return cache[(tp, var)]
    props = {}
    def prop(kind, s):
        key = (kind, s)
        if key not in props:
            props[key] = mk_tree(kind, seed * 31 + s)
        return props[key]
    pm = path_material()
    pb = bmesh.new()
    cnt = 0
    for l in lots:
        i = l['i']
        z = min(gz(l['x'] + dx, l['y'] + dy) for dx, dy in ((0, 0), (0.9, 0.9), (-0.9, 0.9), (0.9, -0.9), (-0.9, -0.9)))
        par = parent_of(i, lots)
        # orientamento: la porta guarda il genitore (lungo la strada), con rumore
        if par is None:
            face = -math.pi / 2 + 0.4
        else:
            face = math.atan2(lots[par]['y'] - l['y'], lots[par]['x'] - l['x'])
        # la casa e' costruita con la porta verso -y => rot = face + 90 deg
        rot = face + math.pi / 2 + l['jrot'] * 0.5
        o = link(bpy.data.objects.new(f"h{i}", house_mesh(l['tp'], l['var'])), coll)
        s = l['sc']
        o.location = (l['x'], l['y'], z)
        o.rotation_euler = (0, 0, rot)
        o.scale = (s, s * l['rg'].uniform(0.92, 1.06), s * l['rg'].uniform(0.95, 1.08))
        cnt += 1
        # strada serpeggiante verso il genitore (ribbon sul terreno)
        if par is not None:
            p0 = Vector((l['x'], l['y'])); p1 = Vector((lots[par]['x'], lots[par]['y']))
            dv = p1 - p0
            ln = dv.length
            nrm = Vector((-dv.y, dv.x)).normalized()
            wd = 0.28 + 0.06 * l['rg'].random()
            ph = l['rg'].uniform(0, 6.28)
            seg = max(6, int(ln / 0.25))
            prev = None
            for q in range(seg + 1):
                t = q / seg
                c = p0 + dv * t + nrm * (0.22 * math.sin(t * 5.2 + ph) * math.sin(math.pi * t) ** 0.5)
                a_, b_ = c + nrm * wd, c - nrm * wd
                row = []
                for pp in (a_, b_):
                    zz = gz(pp.x, pp.y) + 0.035
                    row.append(pb.verts.new((pp.x, pp.y, zz)))
                if prev:
                    pb.faces.new([prev[0], prev[1], row[1], row[0]])
                prev = row
        # steccato e fiori / cespugli attorno alla casa (decor deterministica)
        rg = l['rg']
        for _ in range(rg.choice((1, 2, 2, 3))):
            kind = rg.choice((1, 1, 4, 4, 5, 5, 6, 2, 7)) if l['i'] > 1 else rg.choice((1, 4, 5, 5, 7))
            a = rg.uniform(0, 6.28); rr = rg.uniform(1.0, 1.55) * s
            px, py = l['x'] + rr * math.cos(a), l['y'] + rr * math.sin(a)
            oo = link(bpy.data.objects.new("d", prop(kind, rg.randrange(3))), coll)
            oo.location = (px, py, gz(px, py))
            oo.rotation_euler = (0, 0, rg.uniform(0, 6.28))
            sc_ = rg.uniform(0.9, 1.4)
            oo.scale = (sc_, sc_, sc_)
        if rg.random() < 0.55:
            a = rg.uniform(0, 6.28); rr = rg.uniform(1.3, 1.7) * s
            px, py = l['x'] + rr * math.cos(a), l['y'] + rr * math.sin(a)
            oo = link(bpy.data.objects.new("t", prop(0 if rg.random() < 0.7 else 3, rg.randrange(3))), coll)
            oo.location = (px, py, gz(px, py))
            oo.scale = (s * 0.9,) * 3 if oo.data.name.startswith("prop0") else (1.0, 1.0, 1.0)
    pme = bpy.data.meshes.new("paths"); pb.to_mesh(pme); pb.free()
    for p in pme.polygons: p.use_smooth = True
    po = link(bpy.data.objects.new("paths", pme), coll); po.data.materials.append(pm)
    # pozzo al centro-fronte
    wo = link(bpy.data.objects.new("well", prop(8, 0)), coll)
    wo.location = (2.2, -2.4, gz(2.2, -2.4)); wo.scale = (1.3,) * 3

    # ---- anello di campi di grano attorno al paese (strisce curve)
    wmat = wheat_material()
    rg = random.Random(seed + 5)
    wb = bmesh.new()
    nstrips = 9
    strips = []
    for si in range(nstrips):
        r0 = Rv + 4.2 + si * 2.0 * (1 + 0.04 * Rv ** 0.5)
        wdt = 1.05 * (1 + 0.04 * Rv ** 0.5)
        a0 = rg.uniform(0, 6.28); arc = rg.uniform(1.8, 3.4)
        strips.append((a0, arc, r0, wdt))
        segs = 70
        prev = None
        for q in range(segs + 1):
            a = a0 + arc * q / segs
            row = []
            for ro, ridge in ((r0, 0.0), (r0 + wdt * 0.5, 0.22), (r0 + wdt, 0.0)):
                x, y = ro * math.cos(a), ro * math.sin(a)
                row.append(wb.verts.new((x, y, gz(x, y) + 0.05 + ridge * (1 + 0.3 * math.sin(a * 60)))))
            if prev:
                for c in range(2):
                    wb.faces.new([prev[c], prev[c + 1], row[c + 1], row[c]])
            prev = row
    wme = bpy.data.meshes.new("wheat"); wb.to_mesh(wme); wb.free()
    for p in wme.polygons: p.use_smooth = True
    wo = link(bpy.data.objects.new("wheat", wme), coll); wo.data.materials.append(wmat)
    for (a0, arc, r0, wdt) in strips:
        ns = int(arc * (r0 + wdt / 2) / (0.42 * (1 + 0.05 * Rv ** 0.5)))
        for q in range(ns):
            a = a0 + arc * rg.random(); r = r0 + wdt * rg.uniform(0.08, 0.92)
            x, y = r * math.cos(a), r * math.sin(a)
            oo = link(bpy.data.objects.new("ws", prop(6, rg.randrange(3))), coll)
            oo.location = (x, y, gz(x, y) + 0.1)
            sx = rg.uniform(0.9, 1.3) * (1 + 0.12 * Rv ** 0.5)
            oo.scale = (sx,) * 3
            oo.rotation_euler = (0, 0, rg.uniform(0, 6.28))
    # spighe di grano e fiori sparsi lungo le strisce + primo piano
    for _ in range(int(60 + 1 * Rv)):
        a = rg.uniform(0, 6.28); r = rg.uniform(Rv + 3.0, Rv + 24)
        x, y = r * math.cos(a), r * math.sin(a)
        oo = link(bpy.data.objects.new("w", prop(rg.choice((6, 6, 5, 4)), rg.randrange(3))), coll)
        oo.location = (x, y, gz(x, y))
        sx = rg.uniform(0.9, 1.5) * (1 + 0.15 * Rv ** 0.5)
        oo.scale = (sx,) * 3
        oo.rotation_euler = (0, 0, rg.uniform(0, 6.28))
    # primo piano: erba e fiori vicino alla camera, sfocati (scalati con la distanza camera)
    cx, cy, cz = pos
    fwd = Vector((tgt[0] - cx, tgt[1] - cy)).normalized()
    side = Vector((-fwd.y, fwd.x))
    for q in range(int(50 + 15 * k)):
        dd = rg.uniform(0.35, 0.72) * cdist
        lat = rg.uniform(-0.2, 0.2) * dd * 0.9
        p = Vector((cx, cy)) + fwd * dd + side * lat
        oo = link(bpy.data.objects.new("fg", prop(rg.choice((4, 4, 4, 5, 5, 6)), rg.randrange(3))), coll)
        oo.location = (p.x, p.y, ground_h(p.x, p.y, math.hypot(p.x, p.y), 0))
        ss = (0.35 + 0.6 * dd / cdist) * k * rg.uniform(0.7, 1.3)
        oo.scale = (ss,) * 3
        oo.rotation_euler = (0, 0, rg.uniform(0, 6.28))
    # alberi lontani e boschetti (bokeh verde), puntini luminosi dorati (bokeh)
    for q in range(int(40 + 25 * k)):
        a = rg.uniform(0, 6.28); r = rg.uniform(Rv + 14, Rv + 90 * k)
        x, y = r * math.cos(a), r * math.sin(a)
        if y < -r * 0.3 and r < cdist * 0.9:
            continue
        oo = link(bpy.data.objects.new("tr", prop(0, rg.randrange(3))), coll)
        oo.location = (x, y, ground_h(x, y, math.hypot(x, y), a))
        ss = rg.uniform(1.6, 3.0) * (0.6 + 0.25 * k)
        oo.scale = (ss,) * 3
    sp = link(bpy.data.objects.new("bokeh", bpy.data.meshes.new("bk")), coll)
    bb = bmesh.new()
    bk = M("bokeh", (1.0, 0.82, 0.45), rough=0.5, emit=(1.0, 0.74, 0.30), strength=4.5, tex='none')
    for q in range(260):
        a = math.radians(rg.uniform(35, 145)) if rg.random() < 0.9 else rg.uniform(0, 6.28)
        r = rg.uniform(Rv + 22, Rv + 70 * k + 30)
        x, y = r * math.cos(a), r * math.sin(a)
        z = gz(x, y) + rg.uniform(0.8, 14) * k
        pb2 = bmesh.new(); bmesh.ops.create_icosphere(pb2, subdivisions=1, radius=rg.uniform(0.06, 0.16) * k)
        for v in pb2.verts:
            bb.verts.new(v.co + Vector((x, y, z)))
        pb2.free()
    # (le sfere vengono unite: facce ricostruite per gruppi di 12 vertici = icosfera sub1)
    bb.verts.ensure_lookup_table()
    # semplice: usa istanze di una sola sfera al posto della mesh unita
    bb.free(); coll.objects.unlink(sp)
    sph = bmesh.new(); bmesh.ops.create_icosphere(sph, subdivisions=3, radius=1.0)
    sme = bpy.data.meshes.new("bks"); sph.to_mesh(sme); sph.free(); sme.materials.append(bk)
    for p_ in sme.polygons: p_.use_smooth = True
    for q in range(150):
        a = math.radians(rg.uniform(40, 140)) if rg.random() < 0.9 else rg.uniform(0, 6.28)
        r = rg.uniform(Rv + 14, Rv + 45 * k ** 0.8 + 14)
        x, y = r * math.cos(a), r * math.sin(a)
        oo = link(bpy.data.objects.new("bk", sme), coll)
        oo.location = (x, y, hill(Rv * 0.3) + rg.uniform(0.5, 9.0) * k ** 0.8)
        ss = rg.uniform(0.1, 0.32) * k ** 0.7
        oo.scale = (ss,) * 3

    # ---- luci: sole basso caldo dietro/lato (rim), fill morbido davanti
    sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 4.2; sun.angle = math.radians(3.5)
    sun.color = (1.0, 0.72, 0.42)
    so = link(bpy.data.objects.new("sun", sun), coll)
    so.rotation_euler = (math.radians(80), 0, math.radians(180 + 38 - 14 + 90 - 90 - 10))   # da dietro a destra, bassa
    so.rotation_euler = (math.radians(78), 0, math.radians(-14 + 140))
    fill = bpy.data.lights.new("fill", 'AREA'); fill.energy = 900 * k * k; fill.size = 25 * k
    fill.color = (1.0, 0.82, 0.68)
    fo = link(bpy.data.objects.new("fill", fill), coll)
    fo.location = (pos[0] * 0.5 - 8 * k, pos[1] * 0.6, pos[2] + 7 * k)
    tr = fo.constraints.new('TRACK_TO'); tg = link(bpy.data.objects.new("tg", None), coll); tg.location = (0, 0, gz(0, 0) + 1)
    tr.target = tg; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    sky_world(sc, k)

    # ---- camera con DOF vera
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens; cam.sensor_width = 36; cam.sensor_fit = 'VERTICAL'
    cam.clip_end = 6000; cam.clip_start = 0.5
    cam.dof.use_dof = True; cam.dof.aperture_fstop = fstop
    cam.dof.focus_distance = fdist
    cam.dof.aperture_blades = 0
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
    cy.max_bounces = 5; cy.diffuse_bounces = 3; cy.glossy_bounces = 2; cy.transmission_bounces = 1
    cy.sample_clamp_indirect = 5; cy.device = 'CPU'
    for vt, lk in (('AgX', 'AgX - Medium High Contrast'), ('AgX', 'Medium High Contrast')):
        try:
            sc.view_settings.view_transform = vt; sc.view_settings.look = lk; break
        except Exception:
            pass
    print(f"[cozy3] N={N} Rv={Rv:.1f} case={cnt} cam={tuple(round(v, 1) for v in pos)} d={cdist:.0f} f/{fstop:.2f} build={time.time()-t0:.1f}s")
    return sc


def sky_world(sc, k):
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
    ce[0].position = 0.50; ce[0].color = (*lin((1.0, 0.80, 0.46)), 1)
    e1 = ce.new(0.54); e1.color = (*lin((1.0, 0.74, 0.52)), 1)
    e2 = ce.new(0.62); e2.color = (*lin((0.78, 0.78, 0.82)), 1)
    ce[3].position = 0.80; ce[3].color = (*lin((0.46, 0.64, 0.86)), 1)
    nt.links.new(ad.outputs["Value"], cr.inputs["Fac"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 5
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 3.5)
    nt.links.new(nm.outputs["Vector"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    cl = nt.nodes.new("ShaderNodeMapRange"); cl.inputs["From Min"].default_value = 0.42; cl.inputs["From Max"].default_value = 0.62
    nt.links.new(nz.outputs["Fac"], cl.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[7].default_value = (*lin((1.0, 0.86, 0.66)), 1)
    nt.links.new(cl.outputs["Result"], mx.inputs[0]); nt.links.new(cr.outputs["Color"], mx.inputs[6])
    nt.links.new(mx.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.1


def grade(path, sat=1.12, contrast=1.04):
    try:
        import numpy as np
        from PIL import Image
        im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
        g = im.mean(axis=2, keepdims=True)
        im = np.clip(g + (im - g) * sat, 0, 1)
        im = np.clip((im - 0.5) * contrast + 0.5, 0, 1)
        Image.fromarray((im * 255 + 0.5).astype(np.uint8)).save(path)
    except Exception as e:
        print("[cozy3] grade saltato:", e)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--followers", type=int, default=111)
    ap.add_argument("--out", default="cozy3.png")
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
    print(f"[cozy3] render {time.time()-t:.1f}s -> {a.out}")
    grade(a.out)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(argv)
