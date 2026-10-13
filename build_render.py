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

def mat(name, col=None, rough=0.9, attr=None, haze=True):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    if attr:
        n = m.node_tree.nodes.new('ShaderNodeAttribute'); n.attribute_name = attr; m.node_tree.links.new(n.outputs['Color'], b.inputs['Base Color'])
    else: b.inputs['Base Color'].default_value = (*col, 1)
    return hazeify(m) if haze else m
HAZE = (0.70, 0.77, 0.86); HAZE_K = float(opt('--haze', 1, '32000'))
def hazeify(m):
    nt = m.node_tree; N = nt.nodes; L = nt.links.new; outn = N['Material Output']; sh = outn.inputs['Surface'].links[0].from_socket
    cd = N.new('ShaderNodeCameraData'); e1 = N.new('ShaderNodeMath'); e1.operation = 'DIVIDE'; e1.inputs[1].default_value = -HAZE_K
    L(cd.outputs['View Distance'], e1.inputs[0]); ex = N.new('ShaderNodeMath'); ex.operation = 'EXPONENT'; L(e1.outputs[0], ex.inputs[0])
    f = N.new('ShaderNodeMath'); f.operation = 'SUBTRACT'; f.inputs[0].default_value = 1.0; L(ex.outputs[0], f.inputs[1])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*HAZE, 1); em.inputs['Strength'].default_value = 1.0
    mx = N.new('ShaderNodeMixShader'); L(f.outputs[0], mx.inputs[0]); L(sh, mx.inputs[1]); L(em.outputs[0], mx.inputs[2]); L(mx.outputs[0], outn.inputs['Surface'])
    return m
def city_mat():
    m = bpy.data.materials.new('city'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']
    def M(op, x=None, y=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        if x is not None: n.inputs[1].default_value = x
        return n
    def mm(op, a, x=None, b_=None):
        n = M(op, x); L(a, n.inputs[0])
        if b_ is not None: L(b_, n.inputs[1])
        return n.outputs[0]
    ca = N.new('ShaderNodeVertexColor'); ca.layer_name = 'col'
    geo = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeSeparateXYZ'); L(geo.outputs['Position'], sp.inputs[0])
    sn = N.new('ShaderNodeSeparateXYZ'); L(geo.outputs['Normal'], sn.inputs[0])
    anx = mm('ABSOLUTE', sn.outputs['X']); any_ = mm('ABSOLUTE', sn.outputs['Y']); anz = mm('ABSOLUTE', sn.outputs['Z'])
    wall = mm('LESS_THAN', anz, 0.5)
    u = mm('ADD', mm('MULTIPLY', sp.outputs['X'], None, any_), None, mm('MULTIPLY', sp.outputs['Y'], None, anx))
    fu = mm('FRACT', mm('DIVIDE', u, 3.1)); fz = mm('FRACT', mm('DIVIDE', sp.outputs['Z'], 3.6))
    mu = mm('MULTIPLY', mm('GREATER_THAN', fu, 0.24), None, mm('LESS_THAN', fu, 0.76))
    mz = mm('MULTIPLY', mm('GREATER_THAN', fz, 0.30), None, mm('LESS_THAN', fz, 0.80))
    up = mm('GREATER_THAN', sp.outputs['Z'], 3.2)
    win = mm('MULTIPLY', mm('MULTIPLY', mu, None, mz), None, mm('MULTIPLY', wall, None, up))
    al = ca.outputs['Alpha']; glass = mm('MULTIPLY', mm('GREATER_THAN', al, 0.25), None, mm('LESS_THAN', al, 0.75))
    band = mm('MULTIPLY', mm('LESS_THAN', fz, 0.18), None, wall)  # marcapiano sui grattacieli
    one_minus_g = M('SUBTRACT'); one_minus_g.inputs[0].default_value = 1.0; L(glass, one_minus_g.inputs[1])
    wmask = mm('MULTIPLY', win, None, one_minus_g.outputs[0])
    c1 = N.new('ShaderNodeMix'); c1.data_type = 'RGBA'; L(wmask, c1.inputs['Factor']); L(ca.outputs['Color'], c1.inputs[6]); c1.inputs[7].default_value = (0.07, 0.08, 0.10, 1)
    c2 = N.new('ShaderNodeMix'); c2.data_type = 'RGBA'; L(mm('MULTIPLY', band, None, glass), c2.inputs['Factor']); L(c1.outputs[2], c2.inputs[6]); c2.inputs[7].default_value = (0.55, 0.57, 0.58, 1)
    L(c2.outputs[2], b.inputs['Base Color'])
    rg = N.new('ShaderNodeMapRange'); L(mm('MAXIMUM', wmask, None, glass), rg.inputs['Value']); rg.inputs['To Min'].default_value = 0.85; rg.inputs['To Max'].default_value = 0.12
    L(rg.outputs[0], b.inputs['Roughness'])
    mt = N.new('ShaderNodeMapRange'); L(glass, mt.inputs['Value']); mt.inputs['To Min'].default_value = 0.0; mt.inputs['To Max'].default_value = 0.35; L(mt.outputs[0], b.inputs['Metallic'])
    return hazeify(m)
def land_mat():
    m = bpy.data.materials.new('land'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.95
    yv = N.new('ShaderNodeValue'); LAND_YEAR.append(yv)
    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'uy'; at.attribute_type = 'GEOMETRY'
    d = N.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; L(yv.outputs[0], d.inputs[0]); L(at.outputs['Fac'], d.inputs[1])
    k = N.new('ShaderNodeMapRange'); L(d.outputs[0], k.inputs['Value']); k.inputs['From Min'].default_value = -5; k.inputs['From Max'].default_value = 5
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.004; nz.inputs['Detail'].default_value = 3
    tc = N.new('ShaderNodeTexCoord'); L(tc.outputs['Object'], nz.inputs['Vector'])
    fields = N.new('ShaderNodeValToRGB'); L(nz.outputs['Fac'], fields.inputs[0])
    fields.color_ramp.elements[0].color = (*srgb('#55703a'), 1); fields.color_ramp.elements[1].color = (*srgb('#8a8a4e'), 1)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L(k.outputs[0], mx.inputs['Factor']); L(fields.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (*srgb('#3e3d3c'), 1)
    L(mx.outputs[2], b.inputs['Base Color'])
    return hazeify(m)
LAND_YEAR = []
def obj(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(m); return o

# ---------- edifici ----------
blds = json.load(open(f'{DATA}/buildings.json')); log('edifici', len(blds))
hist = json.load(open(f'{DATA}/hist.json')) if os.path.exists(f'{DATA}/hist.json') else []
for hb in hist: hb['old'] = True
log('predecessori storici', len(hist)); blds = blds + hist
OLDROOF = ['#7a4a35', '#6b4a3a', '#8a5a40', '#5e4636', '#94664a']
rnd = random.Random(3)
LOW = ['#9a3f2e', '#8c4632', '#a8553b', '#7d3b2c', '#b5654a', '#6b4434', '#c79f74', '#d8c7a4', '#a04a38', '#8a5236']
MID = ['#d6c3a0', '#c9a77e', '#b5876a', '#e0d2b5', '#a9604a', '#bfae8c', '#cdb48c']
GLASS = ['#4f7fa8', '#5c89b0', '#3f6d93', '#6f98b8', '#4a7798', '#7fa6c2']
ROOF = ['#6b6862', '#8a8478', '#5a5752', '#9c968a', '#6f7a5e', '#b3aca0', '#7d6f62']
bm = bmesh.new(); col = bm.loops.layers.color.new('col'); vyear = []; vdie = []; polys = []
for b in blds:
    ring = [tuple(p) for p in b['r']]
    try: poly = Polygon(ring)
    except Exception: continue
    if not poly.is_valid or poly.area < 6: continue
    if not poly.exterior.is_ccw: ring = ring[::-1]
    old = b.get('old', False)
    if not old: polys.append(poly)
    h = max(3.0, b['h']); y = b['y']; dd = b.get('d', 99999)
    gl = h > 90 and y > 1955
    pal = GLASS if gl else MID if h > 35 else LOW
    wc = srgb(rnd.choice(pal)); rc = srgb(rnd.choice(ROOF)); wa = 0.5 if gl else 1.0
    vb = [bm.verts.new((x, yy, 0)) for x, yy in ring]; vt = [bm.verts.new((x, yy, h)) for x, yy in ring]
    vyear += [y] * (2 * len(ring)); vdie += [dd] * (2 * len(ring))
    if old and y < 1840:   # case antiche: tetto a falde (piramide sul centroide)
        rc2 = srgb(rnd.choice(OLDROOF)); cx, cy = poly.centroid.x, poly.centroid.y
        ap = bm.verts.new((cx, cy, h + min(6.0, math.sqrt(poly.area) * 0.45))); vyear.append(y); vdie.append(dd)
        for i in range(len(ring)):
            try:
                f = bm.faces.new((vt[i], vt[(i + 1) % len(ring)], ap))
                for l in f.loops: l[col] = (*rc2, 0.0)
            except ValueError: pass
    else:
        try:
            f = bm.faces.new(vt)
            for l in f.loops: l[col] = (*rc, 0.0)
        except ValueError: pass
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        try:
            f = bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
            for l in f.loops: l[col] = (*wc, wa)
        except ValueError: pass
city = obj('city', bm, city_mat())
me = city.data; me.color_attributes.active_color_name = 'col'
at = me.attributes.new('yb', 'FLOAT', 'POINT'); at.data.foreach_set('value', vyear)
ad = me.attributes.new('yd', 'FLOAT', 'POINT'); ad.data.foreach_set('value', vdie)
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
nd = N.new('GeometryNodeInputNamedAttribute'); nd.data_type = 'FLOAT'; nd.inputs['Name'].default_value = 'yd'
sd = M('SUBTRACT'); L(yr.outputs[0], sd.inputs[0]); L(nd.outputs['Attribute'], sd.inputs[1])
dv = M('DIVIDE'); L(sd.outputs[0], dv.inputs[0]); L(DUR.outputs[0], dv.inputs[1]); dc = N.new('ShaderNodeClamp'); L(dv.outputs[0], dc.inputs['Value'])
keep = M('SUBTRACT'); keep.inputs[0].default_value = 1.0; L(dc.outputs[0], keep.inputs[1])
g2 = M('MULTIPLY'); L(g.outputs[0], g2.inputs[0]); L(keep.outputs[0], g2.inputs[1]); g = g2
alive = M('MULTIPLY'); L(cl.outputs[0], alive.inputs[0]); L(keep.outputs[0], alive.inputs[1])
pos = N.new('GeometryNodeInputPosition'); sep = N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0], sep.inputs[0])
mz = M('MULTIPLY'); L(sep.outputs['Z'], mz.inputs[0]); L(g.outputs[0], mz.inputs[1])
cmb = N.new('ShaderNodeCombineXYZ'); L(sep.outputs['X'], cmb.inputs['X']); L(sep.outputs['Y'], cmb.inputs['Y']); L(mz.outputs[0], cmb.inputs['Z'])
sp = N.new('GeometryNodeSetPosition'); L(gi.outputs[0], sp.inputs['Geometry']); L(cmb.outputs[0], sp.inputs['Position'])
lt = M('LESS_THAN', 0.002); L(alive.outputs[0], lt.inputs[0])
dg = N.new('GeometryNodeDeleteGeometry'); dg.domain = 'POINT'; L(sp.outputs[0], dg.inputs['Geometry']); L(lt.outputs[0], dg.inputs['Selection'])
L(dg.outputs[0], go.inputs[0])
mod = city.modifiers.new('grow', 'NODES'); mod.node_group = ng

# anno per fotogramma: lento all'inizio, veloce nel Novecento (curva morbida)
SCHED = json.load(open(opt('--schedule'))) if opt('--schedule') else None
def _lerp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a_, ya), (b_, yb_) in zip(pts, pts[1:]):
        if v <= b_: return ya + (yb_ - ya) * (v - a_) / (b_ - a_)
    return pts[-1][1]
def year_at(f):
    if SCHED: return _lerp((f - 1) / FPS, SCHED['years'])
    t = (f - F0) / max(1, F1 - F0); return Y0 + (Y1 - Y0) * (t ** 0.8)
YEAR_NODES = [yr]
def key_years():
    for nd_ in YEAR_NODES:
        if nd_.outputs[0].is_property_set('default_value') and getattr(nd_, '_keyed', False): continue
        for f in list(range(F0, F1 + 1, 4)) + [F1]:
            nd_.outputs[0].default_value = year_at(f); nd_.outputs[0].keyframe_insert('default_value', frame=f)
key_years()
# durata della crescita in anni = ~0.6 s di video al ritmo corrente (lento negli anni lenti, veloce nei rapidi)
for f in list(range(F0, F1 + 1, 4)) + [F1]:
    q = max(1, FPS // 4); rate = abs(year_at(f + q) - year_at(max(1, f - q))) / (2 * q / FPS)
    DUR.outputs[0].default_value = max(0.4, min(25.0, rate * 0.6)); DUR.outputs[0].keyframe_insert('default_value', frame=f)
json.dump({str(f): year_at(f) for f in range(F0, F1 + 1)}, open(f'{OUT}/years.json', 'w'))

# ---------- terra e acqua ----------
land = json.load(open(f'{DATA}/land.json')) if os.path.exists(f'{DATA}/land.json') else []
if land: lgeom = unary_union([Polygon(r).buffer(0) for r in land if len(r) >= 3])
else: lgeom = unary_union([p.buffer(75, join_style=2) for p in polys]).buffer(-62, join_style=2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from hist_nyc import urban_year
except Exception: urban_year = None
from shapely.prepared import prep
# terra a celle di 120 m: ogni cella sa da che anno e' citta' (prima e' campagna verde, poi asfalto)
BOR = None
if os.path.exists(f'{DATA}/boroughs.json'):
    _bj = json.load(open(f'{DATA}/boroughs.json')); BOR = prep(unary_union([Polygon(r).buffer(0) for v in _bj.values() for r in v]).buffer(30))
pl = prep(lgeom); bm = bmesh.new(); uyl = []
from shapely.geometry import box as sbox
core = sbox(-9000, -9500, 9000, 16000)          # zona citta': celle fini; fuori celle grandi (campagna lontana)
def cells(bounds, CELL, skip_core):
    x0, y0, x1, y1 = bounds; yy = y0
    while yy < y1:
        xx = x0
        while xx < x1:
            c = sbox(xx, yy, xx + CELL, yy + CELL)
            if (not skip_core or not core.contains(c)) and pl.intersects(c):
                q = c if pl.contains(c) else lgeom.intersection(c)
                uy = urban_year(xx + CELL / 2, yy + CELL / 2) if (urban_year and hist) else 0
                if BOR and not BOR.intersects(c): uy = 9999
                for g_ in (q.geoms if hasattr(q, 'geoms') else [q]):
                    if isinstance(g_, Polygon) and g_.area > 1:
                        try: bm.faces.new([bm.verts.new((x, y, 0)) for x, y in list(g_.exterior.coords)[:-1]]); uyl.append(uy)
                        except ValueError: pass
            xx += CELL
        yy += CELL
cells(core.bounds, 120.0, False)
cells(lgeom.bounds, 1500.0, True)
lo_ = obj('land', bm, land_mat()); lo_.data.attributes.new('uy', 'FLOAT', 'FACE').data.foreach_set('value', uyl)
# isolati: impronte degli edifici allargate di qualche metro, piu' chiare (marciapiedi, cortili)
def rings_of(g): return [list(p.exterior.coords)[:-1] for p in (g.geoms if hasattr(g, 'geoms') else [g]) if not p.is_empty]
blocks = []
CH = 600
cells = {}
for p in polys:
    c0 = p.centroid; cells.setdefault((int(c0.x // CH), int(c0.y // CH)), []).append(p.buffer(5, join_style=2))
for k, ps in cells.items(): blocks += rings_of(unary_union(ps).simplify(1.0))
bm = bmesh.new(); byear = []
for r in blocks:
    by = urban_year(*Polygon(r).centroid.coords[0]) if (urban_year and hist) else 0
    try:
        vs = [bm.verts.new((x, y, 0.12)) for x, y in r]; bm.faces.new(vs); byear += [by] * len(vs)
    except ValueError:
        for v in vs: bm.verts.remove(v)
bmesh.ops.triangulate(bm, faces=bm.faces)
bo = obj('blocks', bm, mat('blocks', srgb('#b4ab9c'), 0.9))
bo.data.attributes.new('yb', 'FLOAT', 'POINT').data.foreach_set('value', byear)
# isolati non ancora urbanizzati: spostati sotto terra (indici stabili, cosi' gli alberi non saltano)
hg = bpy.data.node_groups.new('hide', 'GeometryNodeTree')
hg.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); hg.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
HN = hg.nodes; HL = hg.links.new; hi = HN.new('NodeGroupInput'); ho = HN.new('NodeGroupOutput')
hy = HN.new('ShaderNodeValue'); YEAR_NODES.append(hy); YEAR_NODES.extend(LAND_YEAR)
ha = HN.new('GeometryNodeInputNamedAttribute'); ha.data_type = 'FLOAT'; ha.inputs['Name'].default_value = 'yb'
hc = HN.new('ShaderNodeMath'); hc.operation = 'LESS_THAN'; HL(hy.outputs[0], hc.inputs[0]); HL(ha.outputs['Attribute'], hc.inputs[1])
hm = HN.new('ShaderNodeMath'); hm.operation = 'MULTIPLY'; hm.inputs[1].default_value = -1000; HL(hc.outputs[0], hm.inputs[0])
hx = HN.new('ShaderNodeCombineXYZ'); HL(hm.outputs[0], hx.inputs['Z'])
hs = HN.new('GeometryNodeSetPosition'); HL(hi.outputs[0], hs.inputs['Geometry']); HL(hx.outputs[0], hs.inputs['Offset']); HL(hs.outputs[0], ho.inputs[0])
bo.modifiers.new('hide', 'NODES').node_group = hg
key_years()
log('isolati', len(blocks))
# parchi con alberi (data/parks.json opzionale: lista di anelli)
parks = json.load(open(f'{DATA}/parks.json')) if os.path.exists(f'{DATA}/parks.json') else []
if parks:
    bm = bmesh.new()
    for r in parks:
        try: bm.faces.new([bm.verts.new((x, y, 0.25)) for x, y in r])
        except ValueError: pass
    bmesh.ops.triangulate(bm, faces=bm.faces)
    po = obj('parks', bm, mat('grass', srgb('#5d7a3a'), 1.0))
    pyl = []
    for r in parks:
        c_ = Polygon(r).centroid; py_ = urban_year(c_.x, c_.y) if (urban_year and hist) else 0
        if -900 < c_.x < 1700 and 900 < c_.y < 5300: py_ = max(py_, 1858)   # Central Park
        pyl += [py_] * len(r)
    if len(pyl) == len(po.data.vertices): po.data.attributes.new('yb', 'FLOAT', 'POINT').data.foreach_set('value', pyl)
    po.modifiers.new('hide', 'NODES').node_group = hg
    tm = mat('tree', srgb('#3d5c2a'), 0.9)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1); tree = bpy.context.object; tree.name = 'tree'; tree.data.materials.append(tm)
    tree.scale = (1, 1, 1.2); tree.hide_render = True; tree.hide_viewport = True
    tg_ = bpy.data.node_groups.new('trees', 'GeometryNodeTree')
    tg_.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); tg_.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    TN = tg_.nodes; TL = tg_.links.new; i_ = TN.new('NodeGroupInput'); o_ = TN.new('NodeGroupOutput')
    dp = TN.new('GeometryNodeDistributePointsOnFaces'); dp.inputs['Density'].default_value = 0.012; TL(i_.outputs[0], dp.inputs['Mesh'])
    oi = TN.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = tree
    rv = TN.new('FunctionNodeRandomValue'); rv.data_type = 'FLOAT'
    fl = [x for x in rv.inputs if x.type == 'VALUE' and x.name in ('Min', 'Max')]; fl[0].default_value = 3.5; fl[1].default_value = 6.5
    rvo = [x for x in rv.outputs if x.type == 'VALUE'][0]
    ip = TN.new('GeometryNodeInstanceOnPoints'); TL(dp.outputs['Points'], ip.inputs['Points']); TL(oi.outputs['Geometry'], ip.inputs['Instance']); TL(rvo, ip.inputs['Scale'])
    tr_ = TN.new('GeometryNodeTranslateInstances'); tr_.inputs['Translation'].default_value = (0, 0, 4); TL(ip.outputs[0], tr_.inputs['Instances'])
    jg = TN.new('GeometryNodeJoinGeometry'); TL(tr_.outputs[0], jg.inputs[0]); TL(i_.outputs[0], jg.inputs[0]); TL(jg.outputs[0], o_.inputs[0])
    po.modifiers.new('trees', 'NODES').node_group = tg_
    log('parchi', len(parks))
TREES = tg_ if parks else None
if TREES:
    t2 = TREES.copy(); [n for n in t2.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0].inputs['Density'].default_value = 0.0018
    bo.modifiers.new('trees', 'NODES').node_group = t2
# acqua: piccole onde in rilievo, riflessi
bm = bmesh.new(); s = 400000
bm.faces.new([bm.verts.new(v) for v in [(-s, -s, -2), (s, -s, -2), (s, s, -2), (-s, s, -2)]])
wm = mat('water', srgb('#1f5a6e'), 0.06, haze=False); nt = wm.node_tree
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.08; nz.inputs['Detail'].default_value = 6
bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08; nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], nz.inputs['Vector'])
nt.links.new(bp.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
obj('water', bm, hazeify(wm))
log('terra', len(land), 'poligoni')

# ---------- luce, cielo, camera ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new('ShaderNodeTexSky')
try: sky.sky_type = 'NISHITA'
except Exception: pass
SUNEL = float(opt('--sun', 1, '17')); sky.sun_elevation = math.radians(SUNEL); sky.sun_rotation = math.radians(230)
w.node_tree.links.new(sky.outputs['Color'], w.node_tree.nodes['Background'].inputs['Color']); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.4; sun.angle = math.radians(1.0); sun.color = (1, 0.84, 0.66)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(90 - SUNEL), 0, math.radians(230))
cam = bpy.data.cameras.new('cam'); cam.lens = float(opt('--lens', 1, str(SCHED.get('lens', 30)) if SCHED else '30')); cam.clip_end = 200000
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
tg = bpy.data.objects.new('target', None); sc.collection.objects.link(tg)
c = co.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
# lenta orbita da sud-ovest sopra il porto, puntando sulla parte bassa di Manhattan e poi verso Midtown
CAMKEYS = [(int(round(t_ * FPS)) + 1, p_, q_) for t_, p_, q_ in SCHED['cam']] if SCHED else [(F0, (-5200, -11500, 2300), (-1200, -4800, 0)), (F1, (-6200, -9600, 2900), (-300, -2600, 0))]
for f, p, t in CAMKEYS:
    if '--cam' in a: v = list(map(float, opt('--cam', 6))); p, t = v[:3], v[3:]
    co.location = p; co.keyframe_insert('location', frame=f); tg.location = t; tg.keyframe_insert('location', frame=f)

sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
DEV = opt('--device', 1, 'OPTIX' if GPU else 'CPU')
if DEV in ('OPTIX', 'CUDA'):
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = DEV; pr.get_devices()
    for d in pr.devices: d.use = d.type == DEV
    sc.cycles.device = 'GPU'; log('GPU', DEV, [d.name for d in pr.devices if d.use])
else: log('CPU')
sc.render.resolution_x = RW; sc.render.resolution_y = RH
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'; sc.view_settings.exposure = -0.4
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = os.path.join(OUT, '')
sc.render.use_persistent_data = True
sc.render.use_overwrite = False; sc.render.use_placeholder = True   # ripartenza: salta i fotogrammi gia' fatti
sc.frame_step = int(opt('--step', 1, '1'))
log('render', F0, '->', F1, f'{RW}x{RH}', SAMPLES, 'campioni')
tr = time.time()
bpy.ops.render.render(animation=True)
n = len(range(F0, F1 + 1, sc.frame_step)); log(f'FATTO {n} fotogrammi, {(time.time()-tr)/n:.2f}s a fotogramma')
