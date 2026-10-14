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
def land_mat(mode='fields'):
    m = bpy.data.materials.new('land_' + mode); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.95
    yv = N.new('ShaderNodeValue'); LAND_YEAR.append(yv)
    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'uy'; at.attribute_type = 'GEOMETRY'
    d = N.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; L(yv.outputs[0], d.inputs[0]); L(at.outputs['Fac'], d.inputs[1])
    k = N.new('ShaderNodeMapRange'); L(d.outputs[0], k.inputs['Value']); k.inputs['From Min'].default_value = -5; k.inputs['From Max'].default_value = 5
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.004; nz.inputs['Detail'].default_value = 3
    tc = N.new('ShaderNodeTexCoord'); L(tc.outputs['Object'], nz.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.distance = 'CHEBYCHEV'; vo.inputs['Scale'].default_value = 0.006; L(tc.outputs['Object'], vo.inputs['Vector'])
    fields = N.new('ShaderNodeValToRGB'); L(vo.outputs['Color'] if 'Color' in vo.outputs else vo.outputs[1], fields.inputs[0])
    cr = fields.color_ramp; cr.interpolation = 'CONSTANT'
    cr.elements[0].color = (*srgb('#6a7f45'), 1); cr.elements[1].position = 0.8; cr.elements[1].color = (*srgb('#8f8f5c'), 1)
    for pos_, colh in [(0.2, '#7c8a4f'), (0.4, '#5f7840'), (0.6, '#9a9465')]:
        e_ = cr.elements.new(pos_); e_.color = (*srgb(colh), 1)
    fm_ = N.new('ShaderNodeMix'); fm_.data_type = 'RGBA'
    fk = N.new('ShaderNodeMapRange'); L(nz.outputs['Fac'], fk.inputs['Value']); fk.inputs['From Min'].default_value = 0.70; fk.inputs['From Max'].default_value = 0.74
    L(fk.outputs[0], fm_.inputs['Factor']); L(fields.outputs[0], fm_.inputs[6]); fm_.inputs[7].default_value = (*srgb('#33492a'), 1)
    fields = type('o', (), {'outputs': [fm_.outputs[2]]})()
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L(k.outputs[0], mx.inputs['Factor']); L(fields.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (*srgb('#3e3d3c'), 1)
    # tessuto urbano: isolati deformati (non una griglia perfetta), piu' scuri, quartieri con tinte diverse
    wn = N.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 0.0012; wn.inputs['Detail'].default_value = 2; L(tc.outputs['Object'], wn.inputs['Vector'])
    wc = N.new('ShaderNodeVectorMath'); wc.operation = 'SUBTRACT'; L(wn.outputs['Color'], wc.inputs[0]); wc.inputs[1].default_value = (0.5, 0.5, 0.5)
    ws = N.new('ShaderNodeVectorMath'); ws.operation = 'SCALE'; L(wc.outputs[0], ws.inputs[0]); ws.inputs['Scale'].default_value = 420.0
    wv = N.new('ShaderNodeVectorMath'); wv.operation = 'ADD'; L(tc.outputs['Object'], wv.inputs[0]); L(ws.outputs[0], wv.inputs[1])
    bk = N.new('ShaderNodeTexBrick'); L(wv.outputs[0], bk.inputs['Vector']); bk.inputs['Scale'].default_value = 0.012
    bk.inputs['Color1'].default_value = (*srgb('#6b6158'), 1); bk.inputs['Color2'].default_value = (*srgb('#5a5049'), 1); bk.inputs['Mortar'].default_value = (*srgb('#2f2e2d'), 1)
    bk.inputs['Mortar Size'].default_value = 0.07; bk.inputs['Brick Width'].default_value = 1.1; bk.inputs['Row Height'].default_value = 0.7; bk.offset = 0.37; bk.inputs['Bias'].default_value = 0.0
    dn = N.new('ShaderNodeTexNoise'); dn.inputs['Scale'].default_value = 0.0025; dn.inputs['Detail'].default_value = 4; L(tc.outputs['Object'], dn.inputs['Vector'])
    dr = N.new('ShaderNodeValToRGB'); L(dn.outputs['Fac'], dr.inputs[0]); dr.color_ramp.elements[0].position = 0.3; dr.color_ramp.elements[0].color = (*srgb('#8c8880'), 1)
    dr.color_ramp.elements[1].position = 0.7; dr.color_ramp.elements[1].color = (*srgb('#e6d6c4'), 1)
    um = N.new('ShaderNodeMix'); um.data_type = 'RGBA'; um.blend_type = 'MULTIPLY'; um.inputs['Factor'].default_value = 1.0
    L(bk.outputs['Color'], um.inputs[6]); L(dr.outputs[0], um.inputs[7])
    L(um.outputs[2], mx.inputs[7])
    L(fields.outputs[0] if mode == 'fields' else um.outputs[2], b.inputs['Base Color'])
    return hazeify(m)
LAND_YEAR = []
def obj(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(m); return o

# ---------- edifici ----------
blds = json.load(open(f'{DATA}/buildings.json')); log('edifici', len(blds))
hist = json.load(open(f'{DATA}/hist.json')) if os.path.exists(f'{DATA}/hist.json') else []
for hb in hist: hb['old'] = True
log('predecessori storici', len(hist)); blds = blds + hist
if '--crop' in a:   # prove locali con poca memoria: solo gli edifici dentro un rettangolo (metri)
    cx0, cy0, cx1, cy1 = map(float, opt('--crop', 4)); blds = [b_ for b_ in blds if cx0 < b_['r'][0][0] < cx1 and cy0 < b_['r'][0][1] < cy1]
    hist = [h_ for h_ in hist if cx0 < h_['r'][0][0] < cx1 and cy0 < h_['r'][0][1] < cy1]; log('ritaglio', len(blds))
OLDROOF = ['#7a4a35', '#6b4a3a', '#8a5a40', '#5e4636', '#94664a']
rnd = random.Random(3)
LOW = ['#9a3f2e', '#8c4632', '#a8553b', '#7d3b2c', '#b5654a', '#6b4434', '#c79f74', '#d8c7a4', '#a04a38', '#8a5236']
MID = ['#d6c3a0', '#c9a77e', '#b5876a', '#e0d2b5', '#a9604a', '#bfae8c', '#cdb48c']
GLASS = ['#4f7fa8', '#5c89b0', '#3f6d93', '#6f98b8', '#4a7798', '#7fa6c2']
ROOF = ['#6b6862', '#8a8478', '#5a5752', '#9c968a', '#6f7a5e', '#b3aca0', '#7d6f62']
BIN = float(opt('--bin', 1, '4'))
CHUNKS = []; polys = []
def add_bld(bm, col, vyear, vdie, b):
    ring = [tuple(p) for p in b['r']]
    try: poly = Polygon(ring)
    except Exception: return
    if not poly.is_valid or poly.area < 6: return
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
CM = city_mat()
def ckey(b_):
    dd_ = b_.get('d', 99999); return (int(b_['y'] // BIN), int(dd_ // BIN) if dd_ < 9000 else 99999)
blds.sort(key=ckey)
cur = None; nv = 0
def flush(cur):
    k_, bm_, col_, vy_, vd_ = cur
    if not len(bm_.faces): bm_.free(); return 0
    o_ = obj(f'city_{k_[0]}_{k_[1]}', bm_, CM); m_ = o_.data; m_.color_attributes.active_color_name = 'col'
    m_.attributes.new('yb', 'FLOAT', 'POINT').data.foreach_set('value', vy_); m_.attributes.new('yd', 'FLOAT', 'POINT').data.foreach_set('value', vd_)
    CHUNKS.append({'obj': o_, 'b0': k_[0] * BIN, 'b1': (k_[0] + 1) * BIN, 'd0': (k_[1] * BIN if k_[1] != 99999 else None), 'd1': ((k_[1] + 1) * BIN if k_[1] != 99999 else None)})
    return len(m_.vertices)
for b in blds:
    k_ = ckey(b)
    if cur is None or cur[0] != k_:
        if cur: nv += flush(cur)
        bm_ = bmesh.new(); cur = (k_, bm_, bm_.loops.layers.color.new('col'), [], [])
    add_bld(cur[1], cur[2], cur[3], cur[4], b)
if cur: nv += flush(cur)
log('città in', len(CHUNKS), 'blocchi per anno,', nv, 'vertici')

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
# crescita: ogni blocco (stesso anno di nascita e di demolizione) sale scalando l'oggetto in altezza: Cycles riusa la geometria

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
YEAR_NODES = []
def key_years():
    return
    for nd_ in YEAR_NODES:
        if nd_.outputs[0].is_property_set('default_value') and getattr(nd_, '_keyed', False): continue
        for f in list(range(F0, F1 + 1, 4)) + [F1]:
            nd_.outputs[0].default_value = year_at(f); nd_.outputs[0].keyframe_insert('default_value', frame=f)
key_years()
# durata della crescita in anni = ~0.6 s di video al ritmo corrente (lento negli anni lenti, veloce nei rapidi)
json.dump({str(f): year_at(f) for f in range(F0, F1 + 1)}, open(f'{OUT}/years.json', 'w'))


# oggetti statici divisi per anno: compaiono ('appear') o spariscono ('vanish') con hide_render a chiave (niente ricalcolo per fotogramma)
VIS = []
def chunked(name, items, z, m, kind, binw=3.0):
    groups = {}
    for ring, yv in items: groups.setdefault(int(yv // binw) if yv < 9000 else 99999, []).append(ring)
    objs = []
    for k_, rings in sorted(groups.items()):
        bm_ = bmesh.new()
        for r_ in rings:
            try: bm_.faces.new([bm_.verts.new((x, y, z)) for x, y in r_])
            except ValueError: pass
        if not len(bm_.faces): bm_.free(); continue
        bmesh.ops.triangulate(bm_, faces=bm_.faces)
        o_ = obj(f'{name}_{k_}', bm_, m); objs.append(o_)
        VIS.append((o_, kind, k_ * binw if k_ != 99999 else 99999))
    return objs
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
def nj_year(x, y):
    # fuori dai distretti NYC (New Jersey, Westchester...): urbanizzazione per distanza da Hoboken / Jersey City
    la = 40.758 + y / 110540; lo = -73.985 + x / (math.cos(math.radians(40.758)) * 111320)
    d = min(math.hypot((la - 40.737) * 111.0, (lo + 74.030) * 84.3), math.hypot((la - 40.714) * 111.0, (lo + 74.034) * 84.3))
    pts = [(0, 1835), (1.5, 1860), (3, 1885), (5, 1905), (8, 1925), (12, 1950), (20, 1965)]
    for (a_, ya), (b_, yb) in zip(pts, pts[1:]):
        if d <= b_: return ya + (yb - ya) * (d - a_) / (b_ - a_)
    return 1970
pl = prep(lgeom); bm = bmesh.new(); uyl = []
bmm = bmesh.new(); muy = []
try:
    _shore = lgeom.boundary.buffer(170); _shp = prep(_shore)
except Exception: _shore = None
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
                if BOR and not BOR.intersects(c): uy = nj_year(xx + CELL / 2, yy + CELL / 2)
                for g_ in (q.geoms if hasattr(q, 'geoms') else [q]):
                    if isinstance(g_, Polygon) and g_.area > 1:
                        try: bm.faces.new([bm.verts.new((x, y, 0)) for x, y in list(g_.exterior.coords)[:-1]]); uyl.append(uy)
                        except ValueError: pass
                if CELL < 500 and _shore is not None and _shp.intersects(c) and uy < 9000:
                    mq = q.intersection(_shore)
                    for g_ in (mq.geoms if hasattr(mq, 'geoms') else [mq]):
                        if isinstance(g_, Polygon) and g_.area > 50:
                            try:
                                vs_ = [bmm.verts.new((x, y, 0.08)) for x, y in list(g_.exterior.coords)[:-1]]; bmm.faces.new(vs_); muy.extend([uy] * len(vs_))
                            except ValueError: pass
            xx += CELL
        yy += CELL
cells(core.bounds, 120.0, False)
cells(lgeom.bounds, 1500.0, True)
MARSH = None
if len(bmm.faces):
    mm_ = bpy.data.materials.new('marsh'); mm_.use_nodes = True; mn = mm_.node_tree.nodes; ml = mm_.node_tree.links.new; mb = mn['Principled BSDF']
    mtc = mn.new('ShaderNodeTexCoord'); mv = mn.new('ShaderNodeTexVoronoi'); mv.feature = 'DISTANCE_TO_EDGE'; mv.inputs['Scale'].default_value = 0.03; ml(mtc.outputs['Object'], mv.inputs['Vector'])
    mr = mn.new('ShaderNodeMapRange'); ml(mv.outputs['Distance'], mr.inputs['Value']); mr.inputs['From Min'].default_value = 0.02; mr.inputs['From Max'].default_value = 0.06
    mmx = mn.new('ShaderNodeMix'); mmx.data_type = 'RGBA'; ml(mr.outputs[0], mmx.inputs['Factor']); mmx.inputs[6].default_value = (*srgb('#2a3a3c'), 1); mmx.inputs[7].default_value = (*srgb('#7d8452'), 1)
    ml(mmx.outputs[2], mb.inputs['Base Color']); mb.inputs['Roughness'].default_value = 0.6
    _mt = obj('marsh_tmp', bmm, hazeify(mm_)); _mv = _mt.data.vertices
    _mit = []; _vi = 0
    for p_ in _mt.data.polygons: _mit.append(([tuple(_mv[i].co[:2]) for i in p_.vertices], muy[p_.vertices[0]]))
    MARSH = chunked('marsh', _mit, 0.08, _mt.data.materials[0], 'vanish'); bpy.data.objects.remove(_mt, do_unlink=True)
else: bmm.free()
lo_ = obj('land_tmp', bm, land_mat())
_lit = [([tuple(lo_.data.vertices[i].co[:2]) for i in p_.vertices], u_) for p_, u_ in zip(lo_.data.polygons, uyl)]
LAND_F = chunked('land_f', _lit, 0.0, land_mat('fields'), 'vanish'); LAND_U = chunked('land_u', _lit, 0.0, land_mat('urban'), 'appear')
log('terra in', len(LAND_F) + len(LAND_U), 'blocchi')
# copia delle celle vicine (zona citta') come base dei boschi: attributo per vertice = anno di urbanizzazione
# base dei boschi SOLO nella zona inquadrata (celle fini): fuori, decine di km di campagna = milioni di alberi inutili
FB = list(map(float, opt('--forest-box', 4, ['-7500', '-9500', '5500', '9000'])))
_fit = []
for p_, u_ in zip(lo_.data.polygons, uyl):
    cx_, cy_ = p_.center.x, p_.center.y
    if not (FB[0] < cx_ < FB[2] and FB[1] < cy_ < FB[3]) or p_.area > 20000: continue
    _fit.append(([tuple(lo_.data.vertices[i].co[:2]) for i in p_.vertices], u_))
FOREST = chunked('forest', _fit, 0.0, mat('fbase', srgb('#4f7136'), 1.0), 'vanish')
log('boschi', len(_fit), 'celle in', len(FOREST), 'blocchi')
bpy.data.objects.remove(lo_, do_unlink=True)
ROADS_LL = [
  [(40.7045,-74.0135),(40.7128,-74.0072),(40.7195,-74.0021),(40.7290,-73.9965),(40.7359,-73.9911),(40.7411,-73.9897),(40.7500,-73.9877),(40.7580,-73.9855),(40.7681,-73.9819),(40.7870,-73.9754),(40.8000,-73.9680),(40.8160,-73.9590),(40.8340,-73.9450),(40.8550,-73.9330),(40.8750,-73.9100)],
  [(40.7128,-74.0060),(40.7150,-73.9960),(40.7240,-73.9920),(40.7300,-73.9910),(40.7410,-73.9870),(40.7590,-73.9700),(40.7800,-73.9520),(40.7950,-73.9450),(40.8050,-73.9380),(40.8200,-73.9300)],
  [(40.7036,-73.9945),(40.6920,-73.9870),(40.6860,-73.9750),(40.6800,-73.9500),(40.6750,-73.9200),(40.6780,-73.8900)],
  [(40.6920,-73.9870),(40.6650,-73.9620),(40.6400,-73.9600),(40.6200,-73.9550)],
  [(40.7140,-74.0330),(40.7300,-74.0500),(40.7450,-74.0600),(40.7650,-74.0450),(40.7900,-74.0200),(40.8200,-73.9950)],
  [(40.7400,-73.9500),(40.7550,-73.9200),(40.7650,-73.8900),(40.7600,-73.8500)]]
_LAT0, _LON0 = 40.758, -73.985; _KX = math.cos(math.radians(_LAT0)) * 111320; _KY = 110540
from shapely.geometry import LineString
_rg = unary_union([LineString([((lo - _LON0) * _KX, (la - _LAT0) * _KY) for la, lo in r]).buffer(5, cap_style=1) for r in ROADS_LL])
if not lgeom.is_empty: _rg = _rg.intersection(lgeom)
bm = bmesh.new()
for g_ in (_rg.geoms if hasattr(_rg, 'geoms') else [_rg]):
    if isinstance(g_, Polygon) and not g_.is_empty:
        try: bm.faces.new([bm.verts.new((x, y, 0.18)) for x, y in list(g_.exterior.coords)[:-1]])
        except ValueError: pass
bmesh.ops.triangulate(bm, faces=bm.faces)
obj('roads', bm, mat('road', srgb('#c2b38f'), 0.95))
# isolati: impronte degli edifici allargate di qualche metro, piu' chiare (marciapiedi, cortili)
def rings_of(g): return [list(p.exterior.coords)[:-1] for p in (g.geoms if hasattr(g, 'geoms') else [g]) if not p.is_empty]
blocks = []
CH = 600
cells = {}
for p in polys:
    c0 = p.centroid; cells.setdefault((int(c0.x // CH), int(c0.y // CH)), []).append(p.buffer(5, join_style=2))
for k, ps in cells.items(): blocks += rings_of(unary_union(ps).simplify(1.0))
_bit = []
for r in blocks:
    by = urban_year(*Polygon(r).centroid.coords[0]) if (urban_year and hist) else 0
    _bit.append((r, by))
BO = chunked('blocks', _bit, 0.12, mat('blocks', srgb('#b4ab9c'), 0.9), 'appear')
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
fg = hg.copy(); fg.name = 'hide_after'
_a = [n for n in fg.nodes if n.bl_idname == 'GeometryNodeInputNamedAttribute'][0]; _a.inputs['Name'].default_value = 'fy'
_c = [n for n in fg.nodes if n.bl_idname == 'ShaderNodeMath' and n.operation == 'LESS_THAN'][0]; _c.operation = 'GREATER_THAN'
YEAR_NODES.append([n for n in fg.nodes if n.bl_idname == 'ShaderNodeValue'][0])
key_years()
log('isolati', len(blocks))
# parchi con alberi (data/parks.json opzionale: lista di anelli)
parks = json.load(open(f'{DATA}/parks.json')) if os.path.exists(f'{DATA}/parks.json') else []
if '--crop' in a: parks = [r for r in parks if cx0 < r[0][0] < cx1 and cy0 < r[0][1] < cy1]
if parks:
    _pit = []
    for r in parks:
        c_ = Polygon(r).centroid; py_ = urban_year(c_.x, c_.y) if (urban_year and hist) else 0
        if -900 < c_.x < 1700 and 900 < c_.y < 5300: py_ = max(py_, 1858)   # Central Park
        _pit.append(([tuple(v) for v in r], py_))
    PO = chunked('parks', _pit, 0.25, mat('grass', srgb('#5d7a3a'), 1.0), 'appear')
    tm = mat('tree', srgb('#3d5c2a'), 0.9)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1); tree = bpy.context.object; tree.name = 'tree'; tree.data.materials.append(tm)
    tree.scale = (1, 1, 1.2); tree.hide_render = True; tree.hide_viewport = True
    tg_ = bpy.data.node_groups.new('trees', 'GeometryNodeTree')
    tg_.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); tg_.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    TN = tg_.nodes; TL = tg_.links.new; i_ = TN.new('NodeGroupInput'); o_ = TN.new('NodeGroupOutput')
    dp = TN.new('GeometryNodeDistributePointsOnFaces'); dp.inputs['Density'].default_value = float(opt('--parkdens', 1, '0.012')); TL(i_.outputs[0], dp.inputs['Mesh'])
    oi = TN.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = tree
    rv = TN.new('FunctionNodeRandomValue'); rv.data_type = 'FLOAT'
    fl = [x for x in rv.inputs if x.type == 'VALUE' and x.name in ('Min', 'Max')]; fl[0].default_value = 3.5; fl[1].default_value = 6.5
    rvo = [x for x in rv.outputs if x.type == 'VALUE'][0]
    ip = TN.new('GeometryNodeInstanceOnPoints'); TL(dp.outputs['Points'], ip.inputs['Points']); TL(oi.outputs['Geometry'], ip.inputs['Instance']); TL(rvo, ip.inputs['Scale'])
    tr_ = TN.new('GeometryNodeTranslateInstances'); tr_.inputs['Translation'].default_value = (0, 0, 4); TL(ip.outputs[0], tr_.inputs['Instances'])
    jg = TN.new('GeometryNodeJoinGeometry'); TL(tr_.outputs[0], jg.inputs[0]); TL(i_.outputs[0], jg.inputs[0])
    rz_ = TN.new('GeometryNodeRealizeInstances'); TL(jg.outputs[0], rz_.inputs[0]); TL(rz_.outputs[0], o_.inputs[0])
    for o_ in PO: o_.modifiers.new('trees', 'NODES').node_group = tg_
    log('parchi', len(parks))
TREES = tg_ if parks else None
if TREES and FOREST:
    t3 = TREES.copy(); d3 = [n for n in t3.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0]; d3.inputs['Density'].default_value = float(opt('--forest', 1, '0.0015'))
    # radure e campi: selezione con rumore (circa meta' boschi, meta' campi)
    N3 = t3.nodes; L3 = t3.links.new; nz3 = N3.new('ShaderNodeTexNoise'); nz3.inputs['Scale'].default_value = 0.0009
    ps3 = N3.new('GeometryNodeInputPosition'); L3(ps3.outputs[0], nz3.inputs['Vector'])
    gt3 = N3.new('ShaderNodeMath'); gt3.operation = 'GREATER_THAN'; gt3.inputs[1].default_value = 0.5; L3(nz3.outputs['Fac'], gt3.inputs[0])
    L3(gt3.outputs[0], d3.inputs['Selection'])
    jg3 = [n for n in N3 if n.bl_idname == 'GeometryNodeJoinGeometry'][0]
    for l_ in list(t3.links):
        if l_.to_node == jg3 and l_.from_node.bl_idname == 'NodeGroupInput': t3.links.remove(l_)
    for o_ in FOREST: o_.modifiers.new('trees', 'NODES').node_group = t3
if TREES:
    t2 = TREES.copy(); [n for n in t2.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0].inputs['Density'].default_value = 0.0018
    for o_ in BO: o_.modifiers.new('trees', 'NODES').node_group = t2
# alberi "cotti" in geometria statica: spostare un oggetto con istanze generate al volo costringe Cycles a rifare tutto
_dg = bpy.context.evaluated_depsgraph_get(); nb = 0
for o_ in list(bpy.data.objects):
    if o_.type == 'MESH' and any(m_.name == 'trees' for m_ in o_.modifiers):
        me_ = bpy.data.meshes.new_from_object(o_.evaluated_get(_dg), preserve_all_data_layers=True, depsgraph=_dg)
        o_.modifiers.clear(); old_me = o_.data; o_.data = me_; bpy.data.meshes.remove(old_me); nb += len(me_.vertices)
log('alberi cotti:', nb, 'vertici')
# acqua: piccole onde in rilievo, riflessi
bm = bmesh.new(); s = 400000
bm.faces.new([bm.verts.new(v) for v in [(-s, -s, -2), (s, -s, -2), (s, s, -2), (-s, s, -2)]])
wm = mat('water', srgb('#24363c'), 0.08, haze=False); nt = wm.node_tree
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
WN = w.node_tree.nodes; WL = w.node_tree.links.new; bg = WN['Background']
WL(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.35
bg2 = WN.new('ShaderNodeBackground'); bg2.inputs['Color'].default_value = (*HAZE, 1); bg2.inputs['Strength'].default_value = 1.0
# cielo visto dalla camera: sfumato (foschia all'orizzonte -> azzurro in alto), alone caldo verso il sole, nuvole sottili
def sky_grad():
    tc_ = WN.new('ShaderNodeTexCoord'); nd = WN.new('ShaderNodeVectorMath'); nd.operation = 'NORMALIZE'; WL(tc_.outputs['Generated'], nd.inputs[0])
    sp = WN.new('ShaderNodeSeparateXYZ'); WL(nd.outputs[0], sp.inputs[0])
    rp = WN.new('ShaderNodeValToRGB'); WL(sp.outputs['Z'], rp.inputs[0]); cr_ = rp.color_ramp; cr_.interpolation = 'EASE'
    cr_.elements[0].position = 0.0; cr_.elements[0].color = (*HAZE, 1)
    cr_.elements[1].position = 0.5; cr_.elements[1].color = (0.08, 0.20, 0.52, 1)
    for p_, c_ in [(0.035, (0.86, 0.78, 0.70)), (0.10, (0.50, 0.62, 0.84)), (0.25, (0.20, 0.36, 0.70))]:
        e_ = cr_.elements.new(p_); e_.color = (*c_, 1)
    a_, c2 = math.radians(90 - SUNEL), math.radians(230)
    sv = (math.sin(a_) * math.sin(c2), -math.sin(a_) * math.cos(c2), math.cos(a_))
    dt = WN.new('ShaderNodeVectorMath'); dt.operation = 'DOT_PRODUCT'; WL(nd.outputs[0], dt.inputs[0]); dt.inputs[1].default_value = sv
    mx0 = WN.new('ShaderNodeMath'); mx0.operation = 'MAXIMUM'; WL(dt.outputs['Value'], mx0.inputs[0]); mx0.inputs[1].default_value = 0.0
    p1 = WN.new('ShaderNodeMath'); p1.operation = 'POWER'; WL(mx0.outputs[0], p1.inputs[0]); p1.inputs[1].default_value = 6.0
    p2 = WN.new('ShaderNodeMath'); p2.operation = 'POWER'; WL(mx0.outputs[0], p2.inputs[0]); p2.inputs[1].default_value = 80.0
    g1 = WN.new('ShaderNodeMath'); g1.operation = 'MULTIPLY_ADD'; WL(p1.outputs[0], g1.inputs[0]); g1.inputs[1].default_value = 0.9; WL(p2.outputs[0], g1.inputs[2])
    ad = WN.new('ShaderNodeMix'); ad.data_type = 'RGBA'; ad.blend_type = 'ADD'; ad.clamp_result = False
    WL(g1.outputs[0], ad.inputs['Factor']); WL(rp.outputs[0], ad.inputs[6]); ad.inputs[7].default_value = (1.0, 0.72, 0.45, 1)
    # nuvole: rumore proiettato su un piano alto (prospettiva verso l'orizzonte), solo sopra l'orizzonte
    zb = WN.new('ShaderNodeMath'); zb.operation = 'ADD'; WL(sp.outputs['Z'], zb.inputs[0]); zb.inputs[1].default_value = 0.06
    pr = WN.new('ShaderNodeVectorMath'); pr.operation = 'DIVIDE'; WL(nd.outputs[0], pr.inputs[0])
    cz = WN.new('ShaderNodeCombineXYZ'); WL(zb.outputs[0], cz.inputs[0]); WL(zb.outputs[0], cz.inputs[1]); cz.inputs[2].default_value = 1.0; WL(cz.outputs[0], pr.inputs[1])
    stv = WN.new('ShaderNodeVectorMath'); stv.operation = 'MULTIPLY'; WL(pr.outputs[0], stv.inputs[0]); stv.inputs[1].default_value = (1.0, 2.2, 0.0)
    nzc = WN.new('ShaderNodeTexNoise'); nzc.inputs['Scale'].default_value = 0.9; nzc.inputs['Detail'].default_value = 7; nzc.inputs['Roughness'].default_value = 0.6; WL(stv.outputs[0], nzc.inputs['Vector'])
    cm = WN.new('ShaderNodeMapRange'); WL(nzc.outputs['Fac'], cm.inputs['Value']); cm.inputs['From Min'].default_value = 0.50; cm.inputs['From Max'].default_value = 0.66
    hz = WN.new('ShaderNodeMapRange'); WL(sp.outputs['Z'], hz.inputs['Value']); hz.inputs['From Min'].default_value = 0.015; hz.inputs['From Max'].default_value = 0.14
    cmul = WN.new('ShaderNodeMath'); cmul.operation = 'MULTIPLY'; WL(cm.outputs[0], cmul.inputs[0]); WL(hz.outputs[0], cmul.inputs[1])
    cmul2 = WN.new('ShaderNodeMath'); cmul2.operation = 'MULTIPLY'; WL(cmul.outputs[0], cmul2.inputs[0]); cmul2.inputs[1].default_value = 0.9
    cl = WN.new('ShaderNodeMix'); cl.data_type = 'RGBA'; WL(cmul2.outputs[0], cl.inputs['Factor']); WL(ad.outputs[2], cl.inputs[6]); cl.inputs[7].default_value = (1.25, 1.05, 0.90, 1)
    WL(cl.outputs[2], bg2.inputs['Color'])
if '--flat-sky' not in a: sky_grad()
lp = WN.new('ShaderNodeLightPath'); mxw = WN.new('ShaderNodeMixShader'); WL(lp.outputs['Is Camera Ray'], mxw.inputs[0]); WL(bg.outputs[0], mxw.inputs[1]); WL(bg2.outputs[0], mxw.inputs[2])
WL(mxw.outputs[0], WN['World Output'].inputs['Surface'])
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.4; sun.angle = math.radians(1.0); sun.color = (1, 0.84, 0.66)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(90 - SUNEL), 0, math.radians(230))
cam = bpy.data.cameras.new('cam'); cam.lens = float(opt('--lens', 1, str(SCHED.get('lens', 30)) if SCHED else '30')); cam.clip_end = 200000
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
tg = bpy.data.objects.new('target', None); sc.collection.objects.link(tg)
c = co.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
# lenta orbita da sud-ovest sopra il porto, puntando sulla parte bassa di Manhattan e poi verso Midtown
LENSK = [(int(round(k_[0] * FPS)) + 1, float(k_[3]) if len(k_) > 3 else cam.lens) for k_ in SCHED['cam']] if SCHED else []
def lens_at(f):   # obiettivo per fotogramma (4o elemento opzionale delle chiavi camera), interpolato dolce
    if not LENSK or '--lens' in a: return cam.lens
    if f <= LENSK[0][0]: return LENSK[0][1]
    for (fa, la), (fb, lb) in zip(LENSK, LENSK[1:]):
        if f <= fb: u = (f - fa) / max(1, fb - fa); u = u * u * (3 - 2 * u); return la + (lb - la) * u
    return LENSK[-1][1]
CAMKEYS = [(int(round(k_[0] * FPS)) + 1, k_[1], k_[2]) for k_ in SCHED['cam']] if SCHED else [(F0, (-5200, -11500, 2300), (-1200, -4800, 0)), (F1, (-6200, -9600, 2900), (-300, -2600, 0))]
for f, p, t in CAMKEYS:
    if '--cam' in a: v = list(map(float, opt('--cam', 6))); p, t = v[:3], v[3:]
    co.location = p; co.keyframe_insert('location', frame=f); tg.location = t; tg.keyframe_insert('location', frame=f)


# ---------- visibilita' per fotogramma: solo cio' che cambia viene ricalcolato ----------
def _dur(f):
    q = max(1, FPS // 4); rate = abs(year_at(f + q) - year_at(max(1, f - q))) / (2 * q / FPS); return max(0.4, min(25.0, rate * 0.6))
YF = {f: year_at(f) for f in range(F0, F1 + 1)}; DF = {f: _dur(f) for f in range(F0, F1 + 1)}
def growth(ch, f):
    y_, d_ = YF[f], DF[f]
    t = (y_ - ch['b0']) / d_
    if t <= 0: return 0.0
    g = 1.0 if t >= 1 else t + 0.18 * math.sin(math.pi * t)
    if ch['d0'] is not None:
        k = (y_ - ch['d0']) / d_
        if k >= 1: return 0.0
        if k > 0: g *= (1 - k)
    return g
log('blocchi:', len(CHUNKS), 'città,', len(VIS), 'statici')
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1; sc.cycles.transmission_bounces = 0; sc.cycles.volume_bounces = 0
sc.cycles.transparent_max_bounces = 2; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
sc.render.image_settings.compression = 10
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
# BVH dinamico: Cycles non 'cuoce' le trasformazioni nelle mesh, quindi spostare/scalare un oggetto grande non ricostruisce la sua geometria
if opt('--bvh', 1, 'dynamic') == 'dynamic': sc.cycles.debug_bvh_type = 'DYNAMIC_BVH'
# la foschia e' un'emissione finta: fuori dal campionamento delle luci, altrimenti ogni oggetto che compare/sparisce ricostruisce l'albero delle luci
for m_ in bpy.data.materials:
    try: m_.cycles.emission_sampling = 'NONE'
    except Exception: pass
sc.render.use_overwrite = False; sc.render.use_placeholder = True   # ripartenza: salta i fotogrammi gia' fatti
sc.frame_step = int(opt('--step', 1, '1'))
log('render', F0, '->', F1, f'{RW}x{RH}', SAMPLES, 'campioni')
tr = time.time()
_tf = [time.time()]
def _post(scene, *_):
    now = time.time(); print(f'[build] fotogramma {scene.frame_current}: {now - _tf[0]:.1f}s', flush=True); _tf[0] = now

for idb in list(bpy.data.materials) + list(bpy.data.worlds) + list(bpy.data.node_groups) + [o for o in bpy.data.objects if o.type == 'MESH']:
    try: idb.animation_data_clear()
    except Exception: pass
    nt_ = getattr(idb, 'node_tree', None)
    if nt_: nt_.animation_data_clear()
VISSET = {}
def setvis(o_, hidden):
    # niente hide_render (cambia la scena per Cycles e la ricostruisce): gli oggetti nascosti scendono sotto terra
    if VISSET.get(o_.name) != hidden:
        o_.location.z = -5000.0 if hidden else 0.0; VISSET[o_.name] = hidden
done = 0
for f in range(F0, F1 + 1, sc.frame_step):
    path = os.path.join(OUT, f'{f:04d}.png')
    if os.path.exists(path) and os.path.getsize(path) > 0: continue
    t_ = time.time(); sc.frame_set(f); y_ = YF[f]
    _l = lens_at(f)
    if abs(cam.lens - _l) > 1e-3: cam.lens = _l
    for ch in CHUNKS:
        g_ = growth(ch, f); setvis(ch['obj'], g_ < 0.002)
        if g_ >= 0.002 and abs(ch['obj'].scale.z - g_) > 1e-4: ch['obj'].scale.z = g_
    for o_, kind, thr in VIS: setvis(o_, (y_ < thr) if kind == 'appear' else (y_ >= thr))
    sc.render.filepath = path; bpy.ops.render.render(write_still=True); done += 1
    print(f'[build] fotogramma {f}: {time.time() - t_:.1f}s (anno {y_:.0f})', flush=True)
n = max(1, done); log(f'FATTO {done} fotogrammi, {(time.time()-tr)/n:.2f}s a fotogramma')
