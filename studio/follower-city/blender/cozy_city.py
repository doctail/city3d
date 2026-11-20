"""Follower City - diorama COZY.  N follower = N palazzi su un'isola che cresce ad anelli.

Uso (Blender):   blender -b -P cozy_city.py -- --followers 111 --out cozy_111.png
Uso (pip bpy):   python cozy_city.py --followers 111 --out cozy_111.png
Opzioni: --res 540 960  --samples 32  --seed 7  --gpu (OptiX/CUDA se presente)  --save-blend file.blend
Deterministico: un lotto (cella) ha sempre lo stesso aspetto; N sceglie solo quanti lotti, in ordine
dal centro, sono costruiti. I vecchi lotti non cambiano mai quando N cresce.
"""
import sys, math, random, time, argparse, colorsys
import bpy, bmesh
from mathutils import Vector, Euler

C = 1.2          # lato cella (lotto)
ROAD_EVERY = 4   # strada ogni 4 celle: isolati 3x3
RING0, RING_STEP = 5.0, 2.4   # raggi anello: 5.0, 7.4, 9.8 ...

# ---------------------------------------------------------------- colori
def lin(c):
    return tuple(x ** 2.2 for x in c)

WALLS = [(0.96, 0.88, 0.72), (0.90, 0.60, 0.46), (0.72, 0.80, 0.64), (0.62, 0.74, 0.84),
         (0.98, 0.82, 0.50), (0.93, 0.74, 0.70)]
ROOFS = [(0.74, 0.32, 0.22), (0.50, 0.30, 0.22), (0.36, 0.46, 0.60), (0.40, 0.56, 0.42), (0.82, 0.45, 0.25)]
LEAVES = [(0.48, 0.66, 0.36), (0.38, 0.58, 0.38), (0.60, 0.72, 0.38), (0.93, 0.62, 0.66), (0.92, 0.55, 0.26),
          (0.33, 0.52, 0.42)]

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

def tex_brick(scale, c1, c2, mortar, mw, bump, coord="Object", sx=1.0, sy=1.0, off=0.5, w=0.5, h=0.25):
    def f(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale * sx, scale * sy, scale)
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.offset = off
        br.inputs["Color1"].default_value = (*lin(c1), 1)
        br.inputs["Color2"].default_value = (*lin(c2), 1)
        br.inputs["Mortar"].default_value = (*lin(mortar), 1)
        br.inputs["Mortar Size"].default_value = mw
        br.inputs["Brick Width"].default_value = w
        br.inputs["Row Height"].default_value = h
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(tc.outputs[coord], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
        nt.links.new(br.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return f

def tex_noise_color(scale, ca, cb, coord="Object"):
    def f(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = 3
        cr = nt.nodes.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].color = (*lin(ca), 1)
        cr.color_ramp.elements[1].color = (*lin(cb), 1)
        nt.links.new(tc.outputs[coord], nz.inputs["Vector"])
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
        """aggiunge un solido (liste verts/faces; m = materiale o lista per faccia)."""
        pb = bmesh.new()
        vs = [pb.verts.new(v) for v in verts]
        for k, f in enumerate(faces):
            fc = pb.faces.new([vs[i] for i in f])
            mm = m[k] if isinstance(m, (list, tuple)) else m
            fc.material_index = self.slot(mm)
        bmesh.ops.recalc_face_normals(pb, faces=pb.faces)
        if bevel > 0:
            bmesh.ops.bevel(pb, geom=list(pb.edges), offset=bevel, segments=2, affect='EDGES')
        mp = {}
        for v in pb.verts:
            mp[v] = self.bm.verts.new(v.co)
        for f in pb.faces:
            nf = self.bm.faces.new([mp[v] for v in f.verts])
            nf.material_index = f.material_index
            nf.smooth = False
        pb.free()

    def box(self, x0, y0, z0, x1, y1, z1, m, bevel=0.0):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        self.part(v, f, m, bevel)

    def cyl(self, cx, cy, z0, z1, r, m, n=10, r2=None, bevel=0.0):
        r2 = r if r2 is None else r2
        v = []
        for k in range(n):
            a = 2 * math.pi * k / n
            v.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
        for k in range(n):
            a = 2 * math.pi * k / n
            v.append((cx + r2 * math.cos(a), cy + r2 * math.sin(a), z1))
        f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for k in range(n):
            f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
        self.part(v, f, m, bevel)

    def sphere(self, cx, cy, cz, r, m, sub=2, sz=1.0):
        pb = bmesh.new()
        bmesh.ops.create_icosphere(pb, subdivisions=sub, radius=r)
        for v in pb.verts:
            v.co.z *= sz
            v.co += Vector((cx, cy, cz))
        mp = {v: self.bm.verts.new(v.co) for v in pb.verts}
        i = self.slot(m)
        for f in pb.faces:
            nf = self.bm.faces.new([mp[v] for v in f.verts])
            nf.material_index = i
            nf.smooth = False
        pb.free()

    def cone(self, cx, cy, z0, z1, r, m, n=8):
        v = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z0) for k in range(n)]
        v.append((cx, cy, z1))
        f = [tuple(range(n - 1, -1, -1))] + [(k, (k + 1) % n, n) for k in range(n)]
        self.part(v, f, m)

    def build(self, name):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.slots:
            me.materials.append(m)
        return me

# ---------------------------------------------------------------- materiali condivisi
def M_wall(i): return mat(f"wall{i}", WALLS[i], 0.8)
def M_roof(i):
    r = ROOFS[i]
    lighter = tuple(min(1, x * 1.12) for x in r)
    dark = tuple(x * 0.62 for x in r)
    return mat(f"roof{i}", r, 0.7, extra=tex_brick(14, r, lighter, dark, 0.06, 0.6, "Object", 1, 1, 0.5, 0.5, 0.25))
M_TRIM = lambda: mat("trim", (0.99, 0.95, 0.85), 0.7)
M_DOOR = lambda: mat("door", (0.42, 0.26, 0.18), 0.6)
M_WIN = lambda: mat("win", (1.0, 0.78, 0.40), 0.5, emit=(1.0, 0.66, 0.22), strength=7.0)
M_WIN2 = lambda: mat("win2", (1.0, 0.7, 0.35), 0.5, emit=(1.0, 0.55, 0.2), strength=4.5)
M_BRICK = lambda: mat("chim", (0.62, 0.32, 0.24), 0.8)
M_TRUNK = lambda: mat("trunk", (0.45, 0.30, 0.20), 0.9)
def M_leaf(i): return mat(f"leaf{i}", LEAVES[i], 0.85)
M_STONE = lambda: mat("stone", (0.78, 0.72, 0.64), 0.7)
M_LAMP = lambda: mat("lamp", (1, 0.85, 0.5), 0.4, emit=(1.0, 0.72, 0.30), strength=12.0)
M_IRON = lambda: mat("iron", (0.22, 0.2, 0.2), 0.5)
M_WATERFX = lambda: mat("fountainw", (0.45, 0.78, 0.82), 0.1)
FLOWERS = [(0.98, 0.45, 0.55), (0.99, 0.85, 0.35), (0.98, 0.98, 0.95), (0.7, 0.5, 0.9)]

# ---------------------------------------------------------------- edifici
_mesh_cache = {}

def house_mesh(arch, wi, ri):
    key = ("h", tuple(sorted(arch.items())), wi, ri)
    if key in _mesh_cache:
        return _mesh_cache[key]
    w, d, fl, fh = arch["w"], arch["d"], arch["floors"], 0.40
    zt = fl * fh
    b = MB()
    wall, roof, trim, brick = M_wall(wi), M_roof(ri), M_TRIM(), M_BRICK()
    win = M_WIN() if arch["lit"] else M_WIN2()
    b.box(-w / 2, -d / 2, 0, w / 2, d / 2, zt, wall, 0.03)
    # zoccolo
    b.box(-w / 2 - 0.02, -d / 2 - 0.02, 0, w / 2 + 0.02, d / 2 + 0.02, 0.07, trim, 0.012)
    o = 0.08
    rh = arch["rh"]
    if arch["roof"] == "gable":
        x0, x1, y0, y1 = -w / 2 - o, w / 2 + o, -d / 2 - o, d / 2 + o
        v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (x0, 0, zt + rh), (x1, 0, zt + rh)]
        f = [(0, 3, 2, 1), (0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)]
        b.part(v, f, [trim, roof, roof, trim, trim], 0.018)
        ridge = rh
    else:  # hip
        x0, x1, y0, y1 = -w / 2 - o, w / 2 + o, -d / 2 - o, d / 2 + o
        l = max(0.0, (w - d) / 2)
        if l < 0.02:
            v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (0, 0, zt + rh)]
            f = [(0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        else:
            v = [(x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt), (-l, 0, zt + rh), (l, 0, zt + rh)]
            f = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)]
        b.part(v, f, roof, 0.015)
        ridge = rh
    # finestre (fronte/retro y e lati x)
    nx = max(1, int(round(w / 0.42)))
    ny = max(1, int(round(d / 0.5)))
    ww, wh = 0.15, 0.21
    for k in range(fl):
        zc = k * fh + fh * 0.56 + (0.03 if k == 0 else 0)
        for i in range(nx):
            x = (i - (nx - 1) / 2) * (w / nx)
            for s in (-1, 1):
                if k == 0 and s == -1 and abs(x) < 0.2 and arch["door"]:
                    continue
                y = s * d / 2
                b.box(x - ww / 2 - 0.025, y - 0.012 * 2 if s < 0 else y, zc - wh / 2 - 0.025,
                      x + ww / 2 + 0.025, y if s < 0 else y + 0.024, zc + wh / 2 + 0.025, trim)
                b.box(x - ww / 2, y - 0.034 if s < 0 else y, zc - wh / 2,
                      x + ww / 2, y if s < 0 else y + 0.034, zc + wh / 2, win)
        for j in range(ny):
            y = (j - (ny - 1) / 2) * (d / ny)
            for s in (-1, 1):
                x = s * w / 2
                b.box(x - 0.034 if s < 0 else x, y - ww / 2, zc - wh / 2,
                      x if s < 0 else x + 0.034, y + ww / 2, zc + wh / 2, win)
    if arch["door"]:
        b.box(-0.09, -d / 2 - 0.03, 0.05, 0.09, -d / 2, 0.30, M_DOOR(), 0.01)
        b.box(-0.17, -d / 2 - 0.12, 0.33, 0.17, -d / 2 + 0.01, 0.37, roof, 0.01)   # tettuccio porta
    if arch["chimney"]:
        cx = w * 0.25 * arch["chs"]
        b.box(cx - 0.07, -0.07, zt, cx + 0.07, 0.07, zt + rh + 0.12, brick, 0.01)
        b.box(cx - 0.09, -0.09, zt + rh + 0.10, cx + 0.09, 0.09, zt + rh + 0.16, trim, 0.01)
    me = b.build("house")
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
        for k, (r, z) in enumerate([(0.34, 0.2), (0.27, 0.45), (0.2, 0.7)]):
            b.cone(0, 0, z, z + 0.38, r, leaf, 8)
    else:  # bush
        b.sphere(0, 0, 0.12, 0.22, leaf, 1, 0.8)
        b.sphere(0.17, 0.05, 0.1, 0.15, leaf, 1, 0.8)
    me = b.build("tree")
    _mesh_cache[key] = me
    return me

def flower_mesh(ci):
    key = ("f", ci)
    if key in _mesh_cache:
        return _mesh_cache[key]
    b = MB()
    g = M_leaf(0)
    fm = mat(f"flw{ci}", FLOWERS[ci], 0.6)
    rr = random.Random(ci)
    b.sphere(0, 0, 0.04, 0.16, g, 1, 0.5)
    for k in range(5):
        b.sphere(rr.uniform(-0.15, 0.15), rr.uniform(-0.15, 0.15), 0.11, 0.035, fm, 1)
    me = b.build("flw")
    _mesh_cache[key] = me
    return me

def lamp_mesh():
    key = ("lamp",)
    if key in _mesh_cache:
        return _mesh_cache[key]
    b = MB()
    b.cyl(0, 0, 0, 0.1, 0.06, M_IRON(), 6)
    b.cyl(0, 0, 0, 0.75, 0.022, M_IRON(), 6)
    b.sphere(0, 0, 0.82, 0.07, M_LAMP(), 1)
    me = b.build("lamp")
    _mesh_cache[key] = me
    return me

def fountain_mesh():
    b = MB()
    st, wt = M_STONE(), M_WATERFX()
    b.cyl(0, 0, 0, 0.22, 0.62, st, 16, bevel=0.02)
    b.cyl(0, 0, 0.18, 0.25, 0.52, wt, 16)
    b.cyl(0, 0, 0.2, 0.55, 0.09, st, 8)
    b.cyl(0, 0, 0.5, 0.58, 0.28, st, 12, bevel=0.015)
    b.cyl(0, 0, 0.56, 0.62, 0.24, wt, 12)
    return b.build("fountain")

# ---------------------------------------------------------------- scena
def hrand(seed, i, j, salt=0):
    return random.Random((seed * 1000003 + i * 7919 + j * 104729 + salt * 1299709) & 0xFFFFFFFF)

def is_road(i, j):
    return i % ROAD_EVERY == 0 or j % ROAD_EVERY == 0

def is_park(seed, i, j):
    bi, bj = (i - 1) // ROAD_EVERY, (j - 1) // ROAD_EVERY
    if abs(bi) <= 1 and abs(bj) <= 1:
        return False
    return hrand(seed, bi, bj, 11).random() < 0.13

def link(obj, coll):
    coll.objects.link(obj)
    return obj

def make_arch(rg, dist_norm):
    """dist_norm 0 (centro) .. 1 (bordo): case piu alte al centro."""
    tall = max(0.0, 1.0 - dist_norm)
    r = rg.random()
    if r < 0.14 + 0.25 * tall:
        arch = dict(w=round(rg.uniform(0.62, 0.78), 2), d=round(rg.uniform(0.62, 0.78), 2), floors=rg.choice([3, 4] if tall > .4 else [3]),
                    roof="hip", rh=0.5)
    elif r < 0.45 + 0.1 * tall:
        arch = dict(w=round(rg.uniform(0.85, 1.15), 2), d=round(rg.uniform(0.75, 0.95), 2), floors=rg.choice([2, 3]),
                    roof="gable", rh=0.38)
    elif r < 0.62:
        arch = dict(w=round(rg.uniform(0.95, 1.2), 2), d=round(rg.uniform(0.8, 1.0), 2), floors=2, roof="hip", rh=0.36)
    else:
        arch = dict(w=round(rg.uniform(0.8, 1.05), 2), d=round(rg.uniform(0.7, 0.9), 2), floors=1, roof="gable", rh=0.34)
    arch.update(lit=rg.random() < 0.75, door=True, chimney=(arch["roof"] == "gable" and rg.random() < 0.7),
                chs=rg.choice([-1, 1]))
    return arch

def build_scene(N, seed, res, samples, gpu=False):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    coll = sc.collection
    # ----- lotti
    rho = int(math.sqrt(N * 2.9 / math.pi)) + 6
    cells = []
    for i in range(-rho, rho + 1):
        for j in range(-rho, rho + 1):
            if is_road(i, j) or is_park(seed, i, j):
                continue
            jit = hrand(seed, i, j, 1).random()
            cells.append((math.hypot(i, j) * C + jit * C * 1.6, i, j))
    cells.sort()
    lots = cells[:N]
    chosen = {(i, j) for _, i, j in lots}
    maxd = max(math.hypot(i, j) * C for _, i, j in lots) + 0.9 if lots else 3
    k = 0
    while RING0 + RING_STEP * k < maxd + 1.4:
        k += 1
    R = RING0 + RING_STEP * k
    Rt = R + 2.0     # vasca d'acqua
    # ----- materiali terreno
    grass = mat("grass", (0.58, 0.72, 0.36), 0.9, extra=tex_noise_color(0.7, (0.50, 0.66, 0.32), (0.66, 0.78, 0.40), "Object"))
    sand = mat("sand", (0.93, 0.82, 0.60), 0.95)
    cobble = mat("cobble", (0.93, 0.80, 0.62), 0.85,
                 extra=tex_brick(5.0, (0.93, 0.80, 0.62), (0.86, 0.72, 0.55), (0.66, 0.52, 0.40), 0.07, 0.5, "Object", 1, 1, 0.5, 0.5, 0.25))
    earth = mat("earth", (0.62, 0.43, 0.30), 0.95)
    tray = mat("tray", (0.97, 0.90, 0.78), 0.45)

    def water_ext(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.6
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.08
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    water = mat("water", (0.30, 0.66, 0.70), 0.12, extra=water_ext)

    def shallow_ext(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        gr = nt.nodes.new("ShaderNodeTexGradient")
        gr.gradient_type = 'SPHERICAL'
        cr = nt.nodes.new("ShaderNodeValToRGB")
        Rs = R + 2.2
        e = cr.color_ramp.elements
        e[0].position = 0.0; e[0].color = (*lin((0.30, 0.66, 0.70)), 1)
        e[1].position = 1.0 - (R + 0.1) / Rs; e[1].color = (*lin((0.78, 0.95, 0.88)), 1)
        e2 = e.new(1.0 - (R + 0.9) / Rs); e2.color = (*lin((0.52, 0.84, 0.82)), 1)
        nt.links.new(tc.outputs["Object"], gr.inputs["Vector"])
        nt.links.new(gr.outputs["Fac"], cr.inputs["Fac"])
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    shallow = mat("shallow", (0.6, 0.9, 0.85), 0.15, extra=shallow_ext)

    def disc(name, r, z0, z1, m, n=96, bevel=0.0, side=None):
        b = MB()
        b.cyl(0, 0, z0, z1, r, m, n, bevel=bevel)
        if side:   # materiale laterale diverso: ridefinisci per faccia
            pass
        ob = bpy.data.objects.new(name, b.build(name))
        return link(ob, coll)

    # tray (vasca) con bordo crema
    b = MB()
    b.cyl(0, 0, -1.0, -0.4, Rt + 0.35, tray, 96)
    ring_n = 96
    rv, rf = [], []
    for q in range(ring_n):
        a = 2 * math.pi * q / ring_n
        for rad, z in ((Rt + 0.4, -1.0), (Rt + 0.4, 0.05), (Rt - 0.05, 0.05), (Rt - 0.05, -0.4)):
            rv.append((rad * math.cos(a), rad * math.sin(a), z))
    for q in range(ring_n):
        q2 = (q + 1) % ring_n
        for s_ in range(4):
            s2 = (s_ + 1) % 4
            rf.append((q * 4 + s_, q2 * 4 + s_, q2 * 4 + s2, q * 4 + s2))
    b.part(rv, rf, tray, 0.025)
    link(bpy.data.objects.new("tray", b.build("tray")), coll)
    disc("water", Rt - 0.05, -0.3, -0.28, water, 96)
    sh = disc("shallow", 1.0, -0.2, -0.19, shallow, 96)
    sh.scale = (R + 2.2, R + 2.2, 1)
    # isola: terra + spiaggia + prato
    b = MB()
    b.cyl(0, 0, -0.6, 0.0, R + 0.55, earth, 80, r2=R + 0.45, bevel=0.03)
    b.cyl(0, 0, -0.01, 0.02, R + 0.6, sand, 80, bevel=0.02)
    link(bpy.data.objects.new("island", b.build("island")), coll)
    disc("grass", R, 0.0, 0.06, grass, 80, bevel=0.02)
    # strade: un solo mesh
    rb = MB()
    rm = cobble
    rr_ = int(R / C) + 2
    for i in range(-rr_, rr_ + 1):
        for j in range(-rr_, rr_ + 1):
            if not is_road(i, j):
                continue
            if math.hypot(i, j) * C > R - 0.55:
                continue
            x, y = i * C, j * C
            hw = 0.36 * C
            if i % ROAD_EVERY == 0:
                rb.box(x - hw, y - C / 2 + 0.005, 0.04, x + hw, y + C / 2 - 0.005, 0.085, rm, 0.012)
                if j % ROAD_EVERY == 0:   # incrocio: solo i due bracci laterali
                    rb.box(x - C / 2 + 0.005, y - hw, 0.04, x - hw - 0.002, y + hw, 0.085, rm, 0.012)
                    rb.box(x + hw + 0.002, y - hw, 0.04, x + C / 2 - 0.005, y + hw, 0.085, rm, 0.012)
            else:
                rb.box(x - C / 2 + 0.005, y - hw, 0.04, x + C / 2 - 0.005, y + hw, 0.085, rm, 0.012)
    link(bpy.data.objects.new("roads", rb.build("roads")), coll)
    # ----- edifici e decori
    cnt = dict(house=0, tree=0, lamp=0)
    def inst(name, me, x, y, z=0.04, rz=0.0, s=1.0):
        ob = bpy.data.objects.new(name, me)
        ob.location = (x, y, z)
        ob.rotation_euler = (0, 0, rz)
        ob.scale = (s, s, s)
        return link(ob, coll)
    for _, i, j in lots:
        rg = hrand(seed, i, j, 2)
        dn = math.hypot(i, j) * C / max(R, 1)
        arch = make_arch(rg, dn)
        wi = rg.randrange(len(WALLS)); ri = rg.randrange(len(ROOFS))
        me = house_mesh(arch, wi, ri)
        rot = rg.choice([0, 1, 2, 3]) * math.pi / 2
        # la porta (-y) guarda la strada piu vicina
        ci_, cj_ = i % ROAD_EVERY, j % ROAD_EVERY
        rot = rg.choice([0, math.pi / 2, math.pi, -math.pi / 2])
        rot += rg.uniform(-0.05, 0.05)
        inst("house", me, i * C + rg.uniform(-0.04, 0.04), j * C + rg.uniform(-0.04, 0.04), 0.05, rot, 0.97)
        cnt["house"] += 1
        # alberello/cespuglio accanto
        if rg.random() < 0.35:
            side = rg.choice([-1, 1])
            inst("bush", tree_mesh("bush", rg.randrange(3)), i * C + side * 0.5, j * C + rg.uniform(-.5, .5), 0.05, rg.random() * 6, rg.uniform(0.8, 1.1))
            cnt["tree"] += 1
    # riempimento: celle non costruite dentro l'isola
    for i in range(-rr_, rr_ + 1):
        for j in range(-rr_, rr_ + 1):
            if is_road(i, j) or (i, j) in chosen:
                continue
            if math.hypot(i, j) * C > R - 0.75:
                continue
            rg = hrand(seed, i, j, 3)
            r = rg.random()
            if is_park(seed, i, j):
                r = r * 0.55 if r < 0.7 else 0.9
            x, y = i * C + rg.uniform(-0.3, 0.3), j * C + rg.uniform(-0.3, 0.3)
            if r < 0.34:
                kind = rg.choice(["round", "double", "pine", "round"])
                ci = rg.randrange(len(LEAVES)) if kind != "pine" else rg.choice([1, 5])
                inst("tree", tree_mesh(kind, ci), x, y, 0.05, rg.random() * 6, rg.uniform(1.0, 1.5))
                cnt["tree"] += 1
                if rg.random() < 0.5:
                    inst("bush", tree_mesh("bush", rg.randrange(3)), x + rg.uniform(-.5, .5), y + rg.uniform(-.5, .5), 0.05, rg.random() * 6)
            elif r < 0.52:
                inst("bush", tree_mesh("bush", rg.randrange(3)), x, y, 0.05, rg.random() * 6, rg.uniform(1.0, 1.4))
                cnt["tree"] += 1
            elif r < 0.75:
                for q in range(3):
                    inst("flw", flower_mesh(rg.randrange(4)), x + rg.uniform(-.5, .5), y + rg.uniform(-.5, .5), 0.05, rg.random() * 6, rg.uniform(1, 1.6))
    # alberi di bordo (orlo del prato)
    nb = int(2 * math.pi * R / 1.6)
    for q in range(nb):
        rg = hrand(seed, q, 99, 4)
        a = 2 * math.pi * q / nb + rg.uniform(-0.1, 0.1)
        rr = R - rg.uniform(0.35, 0.7)
        kind = rg.choice(["round", "pine", "bush", "bush"])
        ci = rg.randrange(len(LEAVES)) if kind != "pine" else rg.choice([1, 5])
        inst("tree", tree_mesh(kind, ci), rr * math.cos(a), rr * math.sin(a), 0.05, rg.random() * 6, rg.uniform(0.9, 1.4))
        cnt["tree"] += 1
    # lampioni agli incroci e a meta' isolato
    lm = lamp_mesh()
    for i in range(-rr_, rr_ + 1):
        for j in range(-rr_, rr_ + 1):
            if not is_road(i, j) or math.hypot(i, j) * C > R - 1.0:
                continue
            at_x = (i % ROAD_EVERY == 0 and j % ROAD_EVERY == 0)
            mid = (i % ROAD_EVERY == 0 and j % ROAD_EVERY == 2) or (j % ROAD_EVERY == 0 and i % ROAD_EVERY == 2)
            if at_x and (i, j) != (0, 0):
                inst("lamp", lm, i * C + 0.45, j * C + 0.45, 0.085)
                cnt["lamp"] += 1
            elif mid and hrand(seed, i, j, 5).random() < 0.6:
                if i % ROAD_EVERY == 0:
                    inst("lamp", lm, i * C + 0.45, j * C, 0.085)
                else:
                    inst("lamp", lm, i * C, j * C + 0.45, 0.085)
                cnt["lamp"] += 1
    fo = link(bpy.data.objects.new("fountain", fountain_mesh()), coll); fo.location = (0, 0, 0.085); fo.scale = (0.8, 0.8, 0.8)

    # ----- terra (tavolo caldo) per ombre
    def ground_ext(nt, bsdf):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        vl = nt.nodes.new("ShaderNodeVectorMath"); vl.operation = 'LENGTH'
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = Rt * 3.2
        cr = nt.nodes.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].color = (*lin((1.0, 0.86, 0.68)), 1)
        cr.color_ramp.elements[1].color = (*lin((0.92, 0.58, 0.50)), 1)
        nt.links.new(tc.outputs["Object"], vl.inputs[0])
        nt.links.new(vl.outputs["Value"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], cr.inputs["Fac"])
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    gm = mat("ground", (1, .8, .6), 1.0, extra=ground_ext)
    b = MB()
    b.cyl(0, 0, -1.02, -1.0, 400, gm, 64)
    link(bpy.data.objects.new("ground", b.build("ground")), coll)

    # ----- luci: sole dorato + cielo caldo
    sun = bpy.data.lights.new("sun", 'SUN')
    sun.energy = 4.2
    sun.color = (1.0, 0.74, 0.46)
    sun.angle = math.radians(6)
    so = link(bpy.data.objects.new("sun", sun), coll)
    so.rotation_euler = Euler((math.radians(60), 0, math.radians(-118)), 'XYZ')
    w = bpy.data.worlds.new("w"); sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    cr = nt.nodes.new("ShaderNodeValToRGB")
    ce = cr.color_ramp.elements
    ce[0].position = 0.45; ce[0].color = (*lin((1.0, 0.78, 0.58)), 1)
    ce[1].position = 0.85; ce[1].color = (*lin((0.78, 0.66, 0.80)), 1)
    nt.links.new(tc.outputs["Generated"], sp.inputs["Vector"])
    nt.links.new(sp.outputs["Z"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.9

    # ----- camera
    target = bpy.data.objects.new("target", None); link(target, coll)
    target.location = (0, 0, 0.3)
    cam = bpy.data.cameras.new("cam")
    cam.lens = 55
    cam.sensor_fit = 'HORIZONTAL'
    cam.sensor_width = 36
    co = link(bpy.data.objects.new("cam", cam), coll)
    pitch, az = math.radians(40), math.radians(-90 - 18)
    hf = 2 * math.atan(18 / cam.lens)
    dist = (Rt + 0.5) / math.tan(hf / 2) * 1.03
    co.location = (dist * math.cos(pitch) * math.cos(az), dist * math.cos(pitch) * math.sin(az), dist * math.sin(pitch) + 0.3)
    tr = co.constraints.new('TRACK_TO'); tr.target = target
    tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    cam.shift_y = -0.06
    cam.dof.use_dof = True
    cam.dof.focus_object = target
    # tilt-shift finto: l'apertura scala con la distanza (blur costante in pixel)
    cam.dof.aperture_fstop = max(0.5, 2.6 * 40.0 / dist * 0.6) if False else 1.8 * (dist / 40.0) ** 1.0
    sc.camera = co
    # ----- render
    r = sc.render
    r.engine = 'CYCLES'
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    cy = sc.cycles
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.03
    cy.use_denoising = True
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    cy.max_bounces = 5
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 2
    cy.transmission_bounces = 2
    cy.sample_clamp_indirect = 8
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
    sc.render.threads_mode = 'AUTO'
    for vt, lk in (('AgX', 'AgX - Medium High Contrast'), ('AgX', 'Medium High Contrast')):
        try:
            sc.view_settings.view_transform = vt
            sc.view_settings.look = lk
            break
        except Exception:
            pass
    sc.view_settings.exposure = 0.0
    print(f"[cozy] N={N} R={R:.1f} lotti={len(lots)} {cnt} build={time.time()-t0:.1f}s")
    return sc

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--followers", type=int, default=111)
    ap.add_argument("--out", default="cozy.png")
    ap.add_argument("--res", type=int, nargs=2, default=[540, 960])
    ap.add_argument("--samples", type=int, default=32)
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
    print(f"[cozy] render {time.time()-t:.1f}s -> {a.out}")

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(argv)
