"""Navi nella scena Blender (solo con --ships in build_render.py; senza il flag questo modulo non viene nemmeno importato).

Un mesh per modello, condiviso da tutti gli oggetti (istanze: Cycles tiene UNA geometria). Una nave = un oggetto con posizione,
rotazione z e scala uniforme per fotogramma. Le navi non attive scendono a z = -5000 (come gli edifici: niente hide_render).
Modelli: lunghezza 1 lungo +X (poppa -0.5, prua +0.5), y = larghezza, z = 0 e' la linea di galleggiamento.
"""
import math, bpy, bmesh
from mathutils import Matrix, Vector

# colori per modello: (scafo, sovrastruttura/vele, fumaioli/accento)
PALETTE = {
    'sail':  ('#4a3524', '#e7ddc4', '#2b2118'),   # legno scuro, vele crema
    'steam': ('#17181a', '#e9e9e4', '#16171a'),   # scafo nero, ponte bianco, fumaiolo nero
    'liner': ('#15171b', '#f1f0ea', '#b5301f'),   # transatlantico: nero/bianco, fumaioli rossi
    'ferry': ('#a3241b', '#ecebe4', '#1b1b1d'),   # traghetto rosso, cabina bianca
    'tug':   ('#202226', '#c9c6bd', '#b5301f'),   # rimorchiatore nero, camino rosso
}


def _srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def _box(bm, x0, x1, y0, y1, z0, z1, mi, rot=0.0, cx=None, cy=None):
    """Parallelepipedo; con rot (rad, attorno a z) ruotato attorno al suo centro (vele a riva: visibili anche di fianco)."""
    cx = (x0 + x1) / 2 if cx is None else cx; cy = (y0 + y1) / 2 if cy is None else cy
    c, s = math.cos(rot), math.sin(rot)
    def P(x, y, z): return bm.verts.new((cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c, z))
    v = [P(x0, y0, z0), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0), P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        fc = bm.faces.new([v[i] for i in f]); fc.material_index = mi


def _cyl(bm, x, y, z0, z1, r, mi, n=8):
    a = [bm.verts.new((x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n), z0)) for k in range(n)]
    b = [bm.verts.new((x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n), z1)) for k in range(n)]
    for k in range(n): bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])).material_index = mi
    bm.faces.new(b[::-1]).material_index = mi


def _hull(bm, hb, free, mi, double_ended=False, stern=0.8):
    """Scafo: contorno dall'alto, estruso da z = -0.04 a z = free. Prua a punta a +X (e a -X se double_ended)."""
    if double_ended: out = [(-0.5, 0.0), (-0.36, hb), (0.36, hb), (0.5, 0.0), (0.36, -hb), (-0.36, -hb)]
    else: out = [(-0.5, -hb * stern), (0.14, -hb), (0.5, 0.0), (0.14, hb), (-0.5, hb * stern)]
    lo = [bm.verts.new((x, y, -0.04)) for x, y in out]; hi = [bm.verts.new((x, y, free)) for x, y in out]
    n = len(out)
    for k in range(n): bm.faces.new((lo[k], lo[(k + 1) % n], hi[(k + 1) % n], hi[k])).material_index = mi
    bm.faces.new(hi).material_index = mi
    return free


def build_model(kind):
    bm = bmesh.new(); H, S, A = 0, 1, 2
    if kind == 'sail':
        _hull(bm, 0.075, 0.035, H, stern=0.85)
        for mx, hgt in ((-0.22, 0.20), (0.0, 0.26), (0.2, 0.22)):   # tre alberi: vela bassa + gabbia, ruotate di 28 gradi
            _cyl(bm, mx, 0, 0.03, 0.03 + hgt, 0.004, A, 5)
            _box(bm, mx - 0.012, mx + 0.012, -0.075, 0.075, 0.05, 0.05 + hgt * 0.5, S, math.radians(28))
            _box(bm, mx - 0.010, mx + 0.010, -0.055, 0.055, 0.05 + hgt * 0.55, 0.03 + hgt * 0.95, S, math.radians(28))
        _box(bm, 0.36, 0.52, -0.004, 0.004, 0.035, 0.05, A)   # bompresso
    elif kind == 'steam':
        _hull(bm, 0.065, 0.04, H)
        _box(bm, -0.30, 0.12, -0.042, 0.042, 0.04, 0.085, S)   # sovrastruttura
        _box(bm, 0.12, 0.2, -0.03, 0.03, 0.04, 0.065, S)
        _cyl(bm, -0.06, 0, 0.085, 0.17, 0.022, A, 8); _cyl(bm, -0.19, 0, 0.085, 0.16, 0.02, A, 8)
        _cyl(bm, 0.28, 0, 0.04, 0.14, 0.004, A, 5)
    elif kind == 'liner':
        _hull(bm, 0.055, 0.05, H, stern=0.9)
        _box(bm, -0.36, 0.22, -0.042, 0.042, 0.05, 0.095, S); _box(bm, -0.3, 0.1, -0.034, 0.034, 0.095, 0.125, S)
        for fx in (-0.2, -0.07, 0.06): _cyl(bm, fx, 0, 0.125, 0.2, 0.017, A, 8)
        _cyl(bm, 0.3, 0, 0.05, 0.15, 0.004, A, 5)
    elif kind == 'ferry':
        _hull(bm, 0.09, 0.04, H, double_ended=True)
        _box(bm, -0.34, 0.34, -0.075, 0.075, 0.04, 0.09, S); _box(bm, -0.22, 0.22, -0.06, 0.06, 0.09, 0.125, S)
        _cyl(bm, 0.0, 0, 0.125, 0.19, 0.018, A, 8)
    elif kind == 'tug':
        _hull(bm, 0.13, 0.05, H, stern=0.9)
        _box(bm, -0.22, 0.08, -0.1, 0.1, 0.05, 0.13, S); _cyl(bm, -0.1, 0, 0.13, 0.22, 0.028, A, 8)
    else: raise ValueError(kind)
    # scia: cuneo piatto dietro la poppa, trasparenza dal vertice (colore 'col': 1 alla poppa -> 0 in fondo)
    lay = bm.loops.layers.color.new('col')
    w0 = bm.verts.new((-0.5, 0.0, 0.006)); wa = bm.verts.new((-1.3, 0.12, 0.006)); wb = bm.verts.new((-1.3, -0.12, 0.006)); wm = bm.verts.new((-0.5, 0.0, 0.006))
    f = bm.faces.new((w0, wb, wa)); f.material_index = 3
    for l in f.loops:
        v = l.vert; l[lay] = (1, 1, 1, 0.32) if v.co.x > -0.6 else (1, 1, 1, 0.0)
    return bm


class ShipsBpy:
    def __init__(self, sc, traffic, mat_fn, water_z, linked_all=True):
        self.sc = sc; self.T = traffic; self.wz = water_z; self.objs = []; self.hidden = {}
        self.coll = bpy.data.collections.new('ships'); sc.collection.children.link(self.coll)
        meshes = {}
        for k in sorted({s.model for s in traffic.ships}):
            h, sl, ac = PALETTE[k]
            mats = [mat_fn(f'ship_{k}_hull', _srgb(h), 0.55), mat_fn(f'ship_{k}_sup', _srgb(sl), 0.7), mat_fn(f'ship_{k}_acc', _srgb(ac), 0.6)]
            wm = bpy.data.materials.new(f'ship_{k}_wake'); wm.use_nodes = True; nt = wm.node_tree; b = nt.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value = (0.86, 0.92, 0.93, 1); b.inputs['Roughness'].default_value = 0.9
            at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'col'; at.attribute_type = 'GEOMETRY'
            nt.links.new(at.outputs['Alpha'], b.inputs['Alpha'])
            bm = build_model(k); me = bpy.data.meshes.new(f'ship_{k}'); bm.to_mesh(me); bm.free()
            for m in mats + [wm]: me.materials.append(m)
            meshes[k] = me
        for i, s in enumerate(traffic.ships):
            o = bpy.data.objects.new(f'ship_{i}', meshes[s.model]); self.coll.objects.link(o); o.location = (0, 0, -5000.0)
            self.objs.append(o); self.hidden[o.name] = True

    def set_count(self, n):
        """Solo prove di costo: collega alla scena le prime n navi e scollega le altre (davvero fuori dalla scena)."""
        for i, o in enumerate(self.objs):
            lk = o.name in self.coll.objects
            if i < n and not lk: self.coll.objects.link(o)
            elif i >= n and lk: self.coll.objects.unlink(o)

    def update(self, f, fps, year, t_override=None):
        t = f / fps if t_override is None else t_override; T = self.T
        for s, o in zip(T.ships, self.objs):
            if o.name not in self.coll.objects: continue
            k = T.fade(s, year)
            if k > 0.002:
                x, y, hd = T.pos(s, t); k = min(k, T.keepout_scale(s, x, y, t)) if T.keepouts else k
            if k <= 0.002:
                if not self.hidden[o.name]: o.location.z = -5000.0; self.hidden[o.name] = True
                continue
            o.location = (x, y, self.wz); o.rotation_euler.z = hd; sc_ = s.len * k; o.scale = (sc_, sc_, sc_); self.hidden[o.name] = False
