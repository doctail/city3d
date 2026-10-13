# Costruisce la città in Blender e renderizza i fotogrammi. Crescita per anno di costruzione via Geometry Nodes.
# Uso: python build_render.py -- DATA_DIR OUT_DIR [--frames A B] [--res W H] [--samples N] [--gpu] [--fps F] [--years Y0 Y1]
import bpy, bmesh, math, json, sys, os, time, random
from mathutils import Vector
from shapely.geometry import Polygon
from shapely.ops import unary_union

a = sys.argv[sys.argv.index('--') + 1:]
DATA, OUT = a[0], a[1]
def opt(name, n=1, default=None):
    if name in a: i = a.index(name); return a[i + 1:i + 1 + n] if n > 1 else a[i + 1]
    return default
F0, F1 = map(int, opt('--frames', 2, ['1', '240'])); RW, RH = map(int, opt('--res', 2, ['1920', '1080']))
SAMPLES = int(opt('--samples', 1, '32')); FPS = int(opt('--fps', 1, '24')); GPU = '--gpu' in a
Y0, Y1 = map(float, opt('--years', 2, ['1700', '2026']))
os.makedirs(OUT, exist_ok=True); t0 = time.time()
def log(*x): print('[build]', *x, f'({time.time()-t0:.0f}s)', flush=True)

def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
sc.render.fps = FPS; sc.frame_start = F0; sc.frame_end = F1

def mat(name, col=None, rough=0.9, attr=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    if attr:
        n = m.node_tree.nodes.new('ShaderNodeAttribute'); n.attribute_name = attr; m.node_tree.links.new(n.outputs['Color'], b.inputs['Base Color'])
    else: b.inputs['Base Color'].default_value = (*col, 1)
    return m
def obj(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(m); return o

# ---------- edifici ----------
blds = json.load(open(f'{DATA}/buildings.json')); log('edifici', len(blds))
rnd = random.Random(3)
LOW = ['#b98d6e', '#a8765a', '#c9b49a', '#d8cdb8', '#9c6b52', '#bfae95', '#cfc3ad', '#a36a50']
MID = ['#c8c2b6', '#b5ada0', '#d6d0c4', '#a59d90', '#bdb2a0', '#9e9486']
GLASS = ['#7f97a8', '#6f8798', '#93a7b5', '#8a9aa4', '#a3b0b8', '#5f7686']
bm = bmesh.new(); col = bm.loops.layers.color.new('col'); vyear = []; polys = []
for b in blds:
    ring = [tuple(p) for p in b['r']]
    try: poly = Polygon(ring)
    except Exception: continue
    if not poly.is_valid or poly.area < 6: continue
    if not poly.exterior.is_ccw: ring = ring[::-1]
    polys.append(poly); h = max(3.0, b['h']); y = b['y']
    pal = GLASS if (h > 110 and y > 1950) else MID if h > 40 else LOW
    wc = srgb(rnd.choice(pal)); rc = tuple(v * 0.78 for v in wc)
    vb = [bm.verts.new((x, yy, 0)) for x, yy in ring]; vt = [bm.verts.new((x, yy, h)) for x, yy in ring]
    vyear += [y] * (2 * len(ring))
    try:
        f = bm.faces.new(vt)
        for l in f.loops: l[col] = (*rc, 1)
    except ValueError: pass
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        try:
            f = bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
            for l in f.loops: l[col] = (*wc, 1)
        except ValueError: pass
city = obj('city', bm, mat('city', rough=0.55, attr='col'))
me = city.data; me.color_attributes.active_color_name = 'col'
at = me.attributes.new('yb', 'FLOAT', 'POINT'); at.data.foreach_set('value', vyear)
log('mesh città', len(me.vertices), 'vertici')

# ---------- crescita: Geometry Nodes ----------
ng = bpy.data.node_groups.new('grow', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
N = ng.nodes; L = ng.links.new
gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
yr = N.new('ShaderNodeValue'); yr.name = 'YEAR'
na = N.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'; na.inputs['Name'].default_value = 'yb'
def M(op, x=None, yv=None):
    n = N.new('ShaderNodeMath'); n.operation = op
    if x is not None: n.inputs[1].default_value = x
    if yv is not None: n.inputs[2].default_value = yv
    return n
sub = M('SUBTRACT'); L(yr.outputs[0], sub.inputs[0]); L(na.outputs['Attribute'], sub.inputs[1])
DUR = N.new('ShaderNodeValue'); DUR.name = 'DUR'; DUR.outputs[0].default_value = 8.0
div = M('DIVIDE'); L(sub.outputs[0], div.inputs[0]); L(DUR.outputs[0], div.inputs[1])
cl = N.new('ShaderNodeClamp'); L(div.outputs[0], cl.inputs['Value'])
# g + 0.18*sin(pi*g): piccolo rimbalzo sopra l'altezza finale a metà crescita
mpi = M('MULTIPLY', math.pi); L(cl.outputs[0], mpi.inputs[0]); sn = M('SINE'); L(mpi.outputs[0], sn.inputs[0])
k = M('MULTIPLY', 0.18); L(sn.outputs[0], k.inputs[0]); g = M('ADD'); L(cl.outputs[0], g.inputs[0]); L(k.outputs[0], g.inputs[1])
pos = N.new('GeometryNodeInputPosition'); sep = N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0], sep.inputs[0])
mz = M('MULTIPLY'); L(sep.outputs['Z'], mz.inputs[0]); L(g.outputs[0], mz.inputs[1])
cmb = N.new('ShaderNodeCombineXYZ'); L(sep.outputs['X'], cmb.inputs['X']); L(sep.outputs['Y'], cmb.inputs['Y']); L(mz.outputs[0], cmb.inputs['Z'])
sp = N.new('GeometryNodeSetPosition'); L(gi.outputs[0], sp.inputs['Geometry']); L(cmb.outputs[0], sp.inputs['Position'])
lt = M('LESS_THAN', 0.002); L(cl.outputs[0], lt.inputs[0])
dg = N.new('GeometryNodeDeleteGeometry'); dg.domain = 'POINT'; L(sp.outputs[0], dg.inputs['Geometry']); L(lt.outputs[0], dg.inputs['Selection'])
L(dg.outputs[0], go.inputs[0])
mod = city.modifiers.new('grow', 'NODES'); mod.node_group = ng

# anno per fotogramma: lento all'inizio, veloce nel Novecento (curva morbida)
def year_at(f):
    t = (f - F0) / max(1, F1 - F0); return Y0 + (Y1 - Y0) * (t ** 0.8)
for f in range(F0, F1 + 1, 4):
    yr.outputs[0].default_value = year_at(f); yr.outputs[0].keyframe_insert('default_value', frame=f)
yr.outputs[0].default_value = year_at(F1); yr.outputs[0].keyframe_insert('default_value', frame=F1)
json.dump({str(f): year_at(f) for f in range(F0, F1 + 1)}, open(f'{OUT}/years.json', 'w'))

# ---------- terra e acqua ----------
land = json.load(open(f'{DATA}/land.json')) if os.path.exists(f'{DATA}/land.json') else []
bm = bmesh.new()
if land:
    for ring in land:
        try: bm.faces.new([bm.verts.new((x, y, 0)) for x, y in ring])
        except ValueError: pass
else:
    u = unary_union([p.buffer(75, join_style=2) for p in polys]).buffer(-62, join_style=2)
    for gg in (u.geoms if hasattr(u, 'geoms') else [u]):
        try: bm.faces.new([bm.verts.new((x, y, 0)) for x, y in list(gg.exterior.coords)[:-1]])
        except ValueError: pass
bmesh.ops.triangulate(bm, faces=bm.faces)
obj('land', bm, mat('land', srgb('#8e8a80'), 0.95))
bm = bmesh.new(); s = 120000
bm.faces.new([bm.verts.new(v) for v in [(-s, -s, -2), (s, -s, -2), (s, s, -2), (-s, s, -2)]])
obj('water', bm, mat('water', srgb('#2c5866'), 0.1))
log('terra', len(land), 'poligoni')

# ---------- luce, cielo, camera ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new('ShaderNodeTexSky')
try: sky.sky_type = 'NISHITA'
except Exception: pass
sky.sun_elevation = math.radians(24); sky.sun_rotation = math.radians(230)
w.node_tree.links.new(sky.outputs['Color'], w.node_tree.nodes['Background'].inputs['Color']); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.0; sun.angle = math.radians(1.2); sun.color = (1, 0.9, 0.78)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(66), 0, math.radians(230))
cam = bpy.data.cameras.new('cam'); cam.lens = 30; cam.clip_end = 200000
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
tg = bpy.data.objects.new('target', None); sc.collection.objects.link(tg)
c = co.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
# lenta orbita da sud-ovest sopra il porto, puntando sulla parte bassa di Manhattan e poi verso Midtown
for f, p, t in [(F0, (-5200, -11500, 2300), (-1200, -4800, 0)), (F1, (-6200, -9600, 2900), (-300, -2600, 0))]:
    co.location = p; co.keyframe_insert('location', frame=f); tg.location = t; tg.keyframe_insert('location', frame=f)

sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
if GPU:
    pr = bpy.context.preferences.addons['cycles'].preferences
    for dt in ('OPTIX', 'CUDA'):
        try:
            pr.compute_device_type = dt; pr.get_devices()
            devs = [d for d in pr.devices if d.type == dt]
            if devs:
                for d in pr.devices: d.use = d.type == dt
                sc.cycles.device = 'GPU'; log('GPU', dt, [d.name for d in devs]); break
        except Exception as e: log('device', dt, e)
    else: log('ATTENZIONE: nessuna GPU trovata, uso CPU')
sc.render.resolution_x = RW; sc.render.resolution_y = RH
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'; sc.view_settings.exposure = -0.7
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = os.path.join(OUT, '')
sc.render.use_persistent_data = True
sc.frame_step = int(opt('--step', 1, '1'))
log('render', F0, '->', F1, f'{RW}x{RH}', SAMPLES, 'campioni')
tr = time.time()
bpy.ops.render.render(animation=True)
n = len(range(F0, F1 + 1, sc.frame_step)); log(f'FATTO {n} fotogrammi, {(time.time()-tr)/n:.2f}s a fotogramma')
