# Costruisce la città in Blender e renderizza i fotogrammi. Crescita per anno di costruzione via Geometry Nodes.
# Uso: python build_render.py -- DATA_DIR OUT_DIR [--frames A B] [--res W H] [--samples N] [--gpu] [--fps F] [--years Y0 Y1]
import bpy, bmesh, math, json, sys, os, time, random
from mathutils import Vector
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

a = sys.argv[sys.argv.index('--') + 1:]
DATA, OUT = a[0], a[1]
import json as _j, os as _o
# configurazione citta' (default: New York, come prima). Vedi city_nyc.json / city_madrid.json
CITY = {'name': 'nyc', 'lat0': 40.758, 'lon0': -73.985, 'grid_deg': 29, 'hist': 'hist_nyc', 'core_box': [-9000, -9500, 9000, 16000],
        'forest_box': [-7500, -9500, 5500, 9000], 'parks': [[-900, 900, 1700, 5300, 1858]], 'roads': [],
        'outer': {'centers': [[40.737, -74.030], [40.714, -74.034]], 'curve': [[0, 1835], [1.5, 1860], [3, 1885], [5, 1905], [8, 1925], [12, 1950], [20, 1965]], 'max': 1970}}
if '--city' in a: CITY.update(_j.load(open(a[a.index('--city') + 1])))
def opt(name, n=1, default=None):
    if name in a: i = a.index(name); return a[i + 1:i + 1 + n] if n > 1 else a[i + 1]
    return default
F0, F1 = map(int, opt('--frames', 2, ['1', '240'])); RW, RH = map(int, opt('--res', 2, ['1920', '1080']))
SAMPLES = int(opt('--samples', 1, '32')); FPS = int(opt('--fps', 1, '24')); GPU = '--gpu' in a
Y0, Y1 = map(float, opt('--years', 2, ['1700', '2026']))
LIGHT = opt('--light', 1, 'night' if '--night' in a else 'day')   # day | sunset | twilight | night: passate di luce separate, fuse al montaggio
if LIGHT in ('night', 'twilight') and '--night' not in a: a.append('--night')
NIGHT = '--night' in a   # passata notturna separata (materiali fissi: niente risincronizzazione), dissolvenza al montaggio
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
ST = CITY.get('style', {})   # colori per citta' (Copenaghen: stile leggibile); senza chiave = come prima
HAZE = tuple(ST.get('haze', (0.70, 0.77, 0.86))); HAZE_K = float(opt('--haze', 1, str(CITY.get('haze_k', 32000))))   # piu' alto = meno foschia
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
    wmask = mm('MULTIPLY', mm('MULTIPLY', win, None, one_minus_g.outputs[0]), None, mm('GREATER_THAN', al, 0.1))
    c1 = N.new('ShaderNodeMix'); c1.data_type = 'RGBA'; L(wmask, c1.inputs['Factor']); L(ca.outputs['Color'], c1.inputs[6]); c1.inputs[7].default_value = (*srgb(ST.get('window', '#121418')), 1)
    c2 = N.new('ShaderNodeMix'); c2.data_type = 'RGBA'; L(mm('MULTIPLY', band, None, glass), c2.inputs['Factor']); L(c1.outputs[2], c2.inputs[6]); c2.inputs[7].default_value = (0.55, 0.57, 0.58, 1)
    L(c2.outputs[2], b.inputs['Base Color'])
    if NIGHT:   # finestre accese a caso (una per cella finestra), toni caldi; vetrate dei grattacieli piu' rade
        cu = mm('FLOOR', mm('DIVIDE', u, 3.1)); cz = mm('FLOOR', mm('DIVIDE', sp.outputs['Z'], 3.6))
        # caso per finestra: fract(sin(a*12.99 + b*78.23 + c*37.72) * 43758.55) (il White Noise di Blender con coordinate intere
        # dava quasi sempre valori alti: tutte le finestre accese)
        def H_(a_, b_, c_=None):   # caso deterministico da 2-3 numeri interi
            v_ = mm('ADD', mm('MULTIPLY', a_, 12.9898), None, mm('MULTIPLY', b_, 78.233))
            if c_ is not None: v_ = mm('ADD', v_, None, mm('MULTIPLY', c_, 37.719))
            return mm('FRACT', mm('MULTIPLY', mm('SINE', mm('MODULO', v_, 6283.1853)), 43758.5453))
        # luci raggruppate come nella realta': palazzo (cella di 30 m) acceso o quasi spento, poi il piano, poi la finestra
        bx_ = mm('FLOOR', mm('DIVIDE', sp.outputs['X'], 30.0)); by_ = mm('FLOOR', mm('DIVIDE', sp.outputs['Y'], 30.0))
        hb = H_(bx_, by_); hf = H_(bx_, by_, cz); hv = H_(cu, cz, bx_)
        on_b = mm('GREATER_THAN', hb, ST.get('night_bld_off', 0.35))           # 35% dei palazzi spenti
        on_f = mm('GREATER_THAN', hf, ST.get('night_floor_off', 0.45))         # piani accesi a blocchi
        on_w = mm('GREATER_THAN', hv, ST.get('night_win_off', 0.22))           # nel piano acceso quasi tutte le finestre
        lit = mm('MULTIPLY', mm('MULTIPLY', on_b, None, on_f), None, on_w)
        gl_lit = mm('MULTIPLY', mm('MULTIPLY', glass, None, mm('MULTIPLY', on_f, None, on_b)), None, mm('MULTIPLY', mz, None, mu))
        em_k = mm('ADD', mm('MULTIPLY', wmask, None, lit), None, gl_lit)
        wc_ = N.new('ShaderNodeMix'); wc_.data_type = 'RGBA'; L(hf, wc_.inputs['Factor'])
        wc_.inputs[6].default_value = (1.0, 0.42, 0.12, 1); wc_.inputs[7].default_value = (1.0, 0.70, 0.35, 1)
        L(wc_.outputs[2], b.inputs['Emission Color']); L(mm('MULTIPLY', em_k, ST.get('night_win', 6.0)), b.inputs['Emission Strength'])
    rg = N.new('ShaderNodeMapRange'); L(mm('MAXIMUM', wmask, None, glass), rg.inputs['Value']); rg.inputs['To Min'].default_value = 0.85; rg.inputs['To Max'].default_value = (0.95 if NIGHT else 0.12)   # di notte niente riflessi: le finestre spente restano scure
    L(rg.outputs[0], b.inputs['Roughness'])
    mt = N.new('ShaderNodeMapRange'); L(glass, mt.inputs['Value']); mt.inputs['To Min'].default_value = 0.0; mt.inputs['To Max'].default_value = (0.0 if NIGHT else 0.35); L(mt.outputs[0], b.inputs['Metallic'])
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
    FC = CITY.get('field_colors', ['#6a7f45', '#7c8a4f', '#5f7840', '#9a9465', '#8f8f5c'])   # 5 toni dei campi (config citta')
    cr.elements[0].color = (*srgb(FC[0]), 1); cr.elements[1].position = 0.8; cr.elements[1].color = (*srgb(FC[4]), 1)
    for pos_, colh in [(0.2, FC[1]), (0.4, FC[2]), (0.6, FC[3])]:
        e_ = cr.elements.new(pos_); e_.color = (*srgb(colh), 1)
    fm_ = N.new('ShaderNodeMix'); fm_.data_type = 'RGBA'
    fk = N.new('ShaderNodeMapRange'); L(nz.outputs['Fac'], fk.inputs['Value']); fk.inputs['From Min'].default_value = 0.70; fk.inputs['From Max'].default_value = 0.74
    L(fk.outputs[0], fm_.inputs['Factor']); L(fields.outputs[0], fm_.inputs[6]); fm_.inputs[7].default_value = (*srgb(ST.get('hedge', '#33492a')), 1)
    fields = type('o', (), {'outputs': [fm_.outputs[2]]})()
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L(k.outputs[0], mx.inputs['Factor']); L(fields.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (*srgb('#3e3d3c'), 1)
    # tessuto urbano visto dall'alto: tetti a celle piccole (toni spenti), strade dritte parallele alla griglia di Manhattan,
    # un po' di verde nei cortili, quartieri con tinte diverse. Basso contrasto: e' sfondo, non deve sembrare un pavimento.
    vr = N.new('ShaderNodeVectorRotate'); vr.rotation_type = 'Z_AXIS'; vr.inputs['Angle'].default_value = math.radians(CITY['grid_deg']); L(tc.outputs['Object'], vr.inputs['Vector'])
    rv = N.new('ShaderNodeTexVoronoi'); rv.inputs['Scale'].default_value = 0.045; rv.inputs['Randomness'].default_value = 0.85; L(vr.outputs[0], rv.inputs['Vector'])
    rr = N.new('ShaderNodeValToRGB'); L(rv.outputs['Color'], rr.inputs[0]); rcr = rr.color_ramp; rcr.interpolation = 'CONSTANT'
    UC = ST.get('urban', ['#6e655c', '#7d7064', '#5d5853', '#857565', '#77706a', '#6b5148'])
    rcr.elements[0].color = (*srgb(UC[0]), 1); rcr.elements[1].position = 0.84; rcr.elements[1].color = (*srgb(UC[5]), 1)
    for p_, c_ in zip([0.17, 0.34, 0.5, 0.67], UC[1:5]):
        e_ = rcr.elements.new(p_); e_.color = (*srgb(c_), 1)
    bk = N.new('ShaderNodeTexBrick'); L(vr.outputs[0], bk.inputs['Vector']); bk.inputs['Scale'].default_value = 0.0105; bk.offset = 0.0
    bk.inputs['Color1'].default_value = (1, 1, 1, 1); bk.inputs['Color2'].default_value = (1, 1, 1, 1); bk.inputs['Mortar'].default_value = (0.42, 0.42, 0.42, 1)
    bk.inputs['Mortar Size'].default_value = 0.03; bk.inputs['Mortar Smooth'].default_value = 0.3; bk.inputs['Brick Width'].default_value = 0.85; bk.inputs['Row Height'].default_value = 2.4
    sm = N.new('ShaderNodeMix'); sm.data_type = 'RGBA'; sm.blend_type = 'MULTIPLY'; sm.inputs['Factor'].default_value = 1.0; L(rr.outputs[0], sm.inputs[6]); L(bk.outputs['Color'], sm.inputs[7])
    gn = N.new('ShaderNodeTexNoise'); gn.inputs['Scale'].default_value = 0.03; gn.inputs['Detail'].default_value = 3; L(tc.outputs['Object'], gn.inputs['Vector'])
    gk = N.new('ShaderNodeMapRange'); L(gn.outputs['Fac'], gk.inputs['Value']); gk.inputs['From Min'].default_value = 0.6; gk.inputs['From Max'].default_value = 0.66; gk.inputs['To Max'].default_value = 0.7
    gm = N.new('ShaderNodeMix'); gm.data_type = 'RGBA'; L(gk.outputs[0], gm.inputs['Factor']); L(sm.outputs[2], gm.inputs[6]); gm.inputs[7].default_value = (*srgb(ST.get('urban_green', '#4d5b3c')), 1)
    dn = N.new('ShaderNodeTexNoise'); dn.inputs['Scale'].default_value = 0.0025; dn.inputs['Detail'].default_value = 4; L(tc.outputs['Object'], dn.inputs['Vector'])
    dr = N.new('ShaderNodeValToRGB'); L(dn.outputs['Fac'], dr.inputs[0]); dr.color_ramp.elements[0].position = 0.3; dr.color_ramp.elements[0].color = (*srgb(ST.get('urban_dark', '#a8a49c')), 1)
    dr.color_ramp.elements[1].position = 0.7; dr.color_ramp.elements[1].color = (*srgb('#ece0d2'), 1)
    um = N.new('ShaderNodeMix'); um.data_type = 'RGBA'; um.blend_type = 'MULTIPLY'; um.inputs['Factor'].default_value = 1.0
    L(gm.outputs[2], um.inputs[6]); L(dr.outputs[0], um.inputs[7])
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
LM = json.load(open(f'{DATA}/landmarks.json')) if os.path.exists(f'{DATA}/landmarks.json') else None
if LM:   # monumenti modellati: gli edifici (veri e storici) dentro le loro impronte spariscono
    from shapely.prepared import prep as _prep
    _clr = _prep(unary_union([Polygon(r_).buffer(0) for r_ in LM['clear']]))
    _n0 = len(blds)
    blds = [b_ for b_ in blds if not _clr.contains(Point(sum(p_[0] for p_ in b_['r']) / len(b_['r']), sum(p_[1] for p_ in b_['r']) / len(b_['r'])))]
    log('monumenti:', len(LM['parts']), 'parti; tolti', _n0 - len(blds), 'edifici nelle impronte')
if '--crop' in a:   # prove locali con poca memoria: solo gli edifici dentro un rettangolo (metri)
    cx0, cy0, cx1, cy1 = map(float, opt('--crop', 4)); blds = [b_ for b_ in blds if cx0 < b_['r'][0][0] < cx1 and cy0 < b_['r'][0][1] < cy1]
    hist = [h_ for h_ in hist if cx0 < h_['r'][0][0] < cx1 and cy0 < h_['r'][0][1] < cy1]; log('ritaglio', len(blds))
OLDROOF = ST.get('old_roof', ['#7a4a35', '#6b4a3a', '#8a5a40', '#5e4636', '#94664a'])
rnd = random.Random(3)
LOW = ST.get('low') or ['#9a3f2e', '#8c4632', '#a8553b', '#7d3b2c', '#b5654a', '#6b4434', '#c79f74', '#d8c7a4', '#a04a38', '#8a5236']
MID = ST.get('mid') or ['#d6c3a0', '#c9a77e', '#b5876a', '#e0d2b5', '#a9604a', '#bfae8c', '#cdb48c']
GLASS = ST.get('glass') or ['#4f7fa8', '#5c89b0', '#3f6d93', '#6f98b8', '#4a7798', '#7fa6c2']
ROOF = ST.get('roof') or ['#6b6862', '#8a8478', '#5a5752', '#9c968a', '#6f7a5e', '#b3aca0', '#7d6f62']
BIN = float(opt('--bin', 1, '4'))
CHUNKS = []; polys = []; polys_y = []
def add_bld(bm, col, vyear, vdie, b):
    ring = [tuple(p) for p in b['r']]
    try: poly = Polygon(ring)
    except Exception: return
    if not poly.is_valid or poly.area < 6: return
    if not poly.exterior.is_ccw: ring = ring[::-1]
    old = b.get('old', False)
    if not old: polys.append(poly); polys_y.append(b['y'])
    h = max(3.0, b['h']); y = b['y']; dd = b.get('d', 99999)
    gl = h > ST.get('glass_h', 90) and y > 1955 and poly.area > ST.get('glass_min_area', 0)   # ciminiere e antenne: niente vetro
    pal = GLASS if gl else MID if h > 35 else LOW
    rpal = ROOF
    if ST.get('era_split'):   # stile leggibile: prima dell'anno di taglio muri caldi e tetti in coppi, dopo muri chiari e tetti grigi
        es = ST['era_split']; old_ = y < es
        if b.get('lm'): pal, rpal = [b['wall']], [b['roof']]
        elif gl: rpal = ST.get('roof_new', ROOF)
        elif old_: pal, rpal = ST['wall_old'], ST['roof_old']
        else: pal, rpal = (ST.get('wall_anc', ST['wall_new']) if b.get('k') == 'anc' else ST['wall_new']), ST['roof_new']
    wc = srgb(rnd.choice(pal)); rc = srgb(rnd.choice(rpal)); wa = 0.5 if gl else 1.0
    vb = [bm.verts.new((x, yy, 0)) for x, yy in ring]; vt = [bm.verts.new((x, yy, h)) for x, yy in ring]
    vyear += [y] * (2 * len(ring)); vdie += [dd] * (2 * len(ring))
    pitched = (old and y < 1840) or (ST.get('pitched_until') and y < ST['pitched_until'] and poly.area < ST.get('pitched_max_area', 600) and not b.get('lm'))
    if pitched:   # case antiche: tetto a falde (piramide sul centroide)
        rc2 = srgb(rnd.choice(ST['roof_old'] if ST.get('era_split') else OLDROOF)); cx, cy = poly.centroid.x, poly.centroid.y
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
if '--year' in a:   # copertine: anno fisso per tutti i fotogrammi (con --cam e --only)
    _YFIX = float(opt('--year')); year_at = lambda f: _YFIX
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
        bm_.normal_update(); _down = [f_ for f_ in bm_.faces if f_.normal.z < 0]   # anelli in senso orario: normale verso il basso = macchia nera
        if _down: bmesh.ops.reverse_faces(bm_, faces=_down)
        o_ = obj(f'{name}_{k_}', bm_, m); objs.append(o_)
        VIS.append((o_, kind, k_ * binw if k_ != 99999 else 99999))
    return objs
# ---------- terra e acqua ----------
land = json.load(open(f'{DATA}/land.json')) if os.path.exists(f'{DATA}/land.json') else []
if land: lgeom = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in land if len(r) >= 1]).buffer(CITY.get('land_close', 45), join_style=2).buffer(-CITY.get('land_close', 45), join_style=2)   # chiude le fessure tra contee (Copenaghen: 1 m, i canali sono stretti)
else: lgeom = unary_union([p.buffer(75, join_style=2) for p in polys]).buffer(-62, join_style=2)
RECLAIM = json.load(open(f'{DATA}/reclaim.json')) if os.path.exists(f'{DATA}/reclaim.json') else []
_rec_items = []
for rc_ in RECLAIM:
    q_ = lgeom.intersection(Polygon(rc_['r']).buffer(0))
    if q_.is_empty: continue
    lgeom = lgeom.difference(Polygon(rc_['r']).buffer(0))
    for g_ in (q_.geoms if hasattr(q_, 'geoms') else [q_]):
        if isinstance(g_, Polygon) and g_.area > 50: _rec_items.append((list(g_.simplify(2).exterior.coords)[:-1], rc_['y']))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    urban_year = __import__(CITY['hist']).urban_year
except Exception as e_: urban_year = None; print('[build] storia non disponibile:', e_, flush=True)
from shapely.prepared import prep
# terra a celle di 120 m: ogni cella sa da che anno e' citta' (prima e' campagna verde, poi asfalto)
BOR = None
if os.path.exists(f'{DATA}/boroughs.json'):
    _bj = json.load(open(f'{DATA}/boroughs.json')); BOR = prep(unary_union([Polygon(r).buffer(0) for v in _bj.values() for r in v]).buffer(30))
def nj_year(x, y):
    # fuori dai confini della citta' (per NYC: New Jersey): urbanizzazione per distanza dai centri di 'outer' nella config
    o_ = CITY['outer']; la = CITY['lat0'] + y / 110540; lo = CITY['lon0'] + x / (math.cos(math.radians(CITY['lat0'])) * 111320)
    d = min(math.hypot((la - c_[0]) * 111.0, (lo - c_[1]) * 111.32 * math.cos(math.radians(c_[0]))) for c_ in o_['centers'])
    pts = o_['curve']
    for (a_, ya), (b_, yb) in zip(pts, pts[1:]):
        if d <= b_: return ya + (yb - ya) * (d - a_) / (b_ - a_)
    return o_['max']
pl = prep(lgeom); bm = bmesh.new(); uyl = []
bmm = bmesh.new(); muy = []
try:
    _shore = lgeom.boundary.buffer(170) if CITY.get('marsh', True) else None; _shp = prep(_shore) if _shore is not None else None   # marsh=false: niente fascia di palude sulle rive (Rotterdam: sembrava lastricato)
except Exception: _shore = None
from shapely.geometry import box as sbox
core = sbox(*CITY['core_box'])          # zona citta': celle fini; fuori celle grandi (campagna lontana)
def cells(bounds, CELL, skip_core):
    x0, y0, x1, y1 = bounds; yy = y0
    while yy < y1:
        xx = x0
        while xx < x1:
            c = sbox(xx, yy, xx + CELL, yy + CELL)
            if skip_core and c.intersects(core): c = c.difference(core)   # niente sovrapposizioni con le celle fini (era una riga scura)
            if not c.is_empty and c.area > 1 and pl.intersects(c):
                q = c if pl.contains(c) else lgeom.intersection(c)
                uy = urban_year(xx + CELL / 2, yy + CELL / 2) if (urban_year and hist) else 0
                if CELLMIN is not None and CELL < 500:   # terreno urbano dal primo edificio vero della cella (niente quadretti vuoti)
                    uy = CELLMIN.get((int((xx - core.bounds[0]) // CELL), int((yy - core.bounds[1]) // CELL)), 9999)
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
CELLMIN = None
if CITY.get('land_from_buildings'):
    CELLMIN = {}
    for b_ in blds:
        x_ = sum(p_[0] for p_ in b_['r']) / len(b_['r']); y_ = sum(p_[1] for p_ in b_['r']) / len(b_['r'])
        k_ = (int((x_ - core.bounds[0]) // 120.0), int((y_ - core.bounds[1]) // 120.0))
        if b_['y'] < CELLMIN.get(k_, 99999): CELLMIN[k_] = b_['y'] - 2
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
if _rec_items: REC = chunked('reclaim', _rec_items, 0.01, mat('reclaim', srgb(ST.get('reclaim', '#b9b09c')), 0.95), 'appear', binw=1.0); log('terra di riporto', len(_rec_items))
# strade (DATA/roads.json [{"r", "y"}]): nastri chiari sul suolo, sotto gli isolati
if os.path.exists(f'{DATA}/roads.json'):
    _rd = json.load(open(f'{DATA}/roads.json'))
    if '--crop' in a: _rd = [r_ for r_ in _rd if cx0 < r_['r'][0][0] < cx1 and cy0 < r_['r'][0][1] < cy1]
    _sm = mat('street', srgb(ST.get('street', '#e3dac6')), 0.95)
    if NIGHT:
        _sb = _sm.node_tree.nodes['Principled BSDF']; _sb.inputs['Emission Color'].default_value = (1.0, 0.62, 0.32, 1); _sb.inputs['Emission Strength'].default_value = ST.get('night_street', 0.25)
    chunked('streets', [(r_['r'], r_['y']) for r_ in _rd if not r_.get('rail')], 0.10, _sm, 'appear')
    chunked('rails', [(r_['r'], r_['y']) for r_ in _rd if r_.get('rail')], 0.10, mat('rail', srgb(ST.get('rail', '#8a8378')), 0.9), 'appear')
    log('strade', len(_rd))
# ponti (DATA/bridges.json [{"r", "y"}]): impalcato rialzato sull'acqua, fianchi scuri
def slabs(name, items, z0, z1, m_top, m_side, binw=2.0):
    groups = {}
    for ring, yv in items: groups.setdefault(int(yv // binw), []).append(ring)
    for k_, rings in sorted(groups.items()):
        bm_ = bmesh.new()
        for r_ in rings:
            try:
                pg = Polygon(r_)
                if not pg.is_valid or pg.area < 5: continue
                rr = list(pg.exterior.coords)[:-1]
                if not pg.exterior.is_ccw: rr = rr[::-1]
                vb = [bm_.verts.new((x, y, z0)) for x, y in rr]; vt = [bm_.verts.new((x, y, z1)) for x, y in rr]
                f_ = bm_.faces.new(vt); f_.material_index = 0
                for i in range(len(rr)):
                    j = (i + 1) % len(rr); f_ = bm_.faces.new((vb[i], vb[j], vt[j], vt[i])); f_.material_index = 1
            except (ValueError, Exception): pass
        if not len(bm_.faces): bm_.free(); continue
        o_ = obj(f'{name}_{k_}', bm_, m_top); o_.data.materials.append(m_side)
        VIS.append((o_, 'appear', k_ * binw))
if os.path.exists(f'{DATA}/bridges.json'):
    _br = json.load(open(f'{DATA}/bridges.json'))
    if '--crop' in a: _br = [r_ for r_ in _br if cx0 < r_['r'][0][0] < cx1 and cy0 < r_['r'][0][1] < cy1]
    slabs('bridge', [(r_['r'], r_['y']) for r_ in _br], 1.6, 3.4, mat('bdeck', srgb(ST.get('bridge_deck', '#d9d4c8')), 0.9), mat('bside', srgb(ST.get('bridge_side', '#5d5850')), 0.9))
    log('ponti', len(_br))
# incendi (DATA/fires.json): bagliore a terra, fiamme, fumo; ognuno visibile solo nella sua finestra di anni
if os.path.exists(f'{DATA}/fires.json') or (LM and LM.get('fires')):
    _fr = json.load(open(f'{DATA}/fires.json')) if os.path.exists(f'{DATA}/fires.json') else []; frnd = random.Random(7)
    _fr += (LM or {}).get('fires', [])
    for fi_ in _fr: fi_['smoke'] = min(int(fi_.get('smoke', 9)), 9)   # poche colonne: con 16-26 sembravano palline sparse
    def emat(name, col, k):
        m_ = bpy.data.materials.new(name); m_.use_nodes = True; nt_ = m_.node_tree; N_ = nt_.nodes
        for n_ in list(N_):
            if n_.type != 'OUTPUT_MATERIAL': N_.remove(n_)
        e_ = N_.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (*col, 1); e_.inputs['Strength'].default_value = k
        nt_.links.new(e_.outputs[0], N_['Material Output'].inputs['Surface']); return m_
    m_glow = emat('fire_glow', (1.0, 0.32, 0.06), 4.0); m_flame = emat('fire_flame', (1.0, 0.55, 0.12), 12.0)
    m_smoke = mat('smoke', srgb(ST.get('smoke', '#5f5954')), 1.0); _pb = m_smoke.node_tree.nodes['Principled BSDF']; _pb.inputs['Alpha'].default_value = ST.get('smoke_alpha', 0.7)
    try: m_smoke.surface_render_method = 'BLENDED'
    except Exception: pass
    for fi_ in _fr:
        pg = Polygon(fi_['poly']); y0_, y1_ = fi_['y'], fi_['y1']
        bm_ = bmesh.new()
        try: bm_.faces.new([bm_.verts.new((x, y, 0.6)) for x, y in list(pg.exterior.coords)[:-1]])
        except ValueError: pass
        bmesh.ops.triangulate(bm_, faces=bm_.faces); o_ = obj(f'glow_{int(y0_)}', bm_, m_glow); VIS.append((o_, 'window', (y0_ - 0.0004, y1_ + 0.15)))
        x0_, yy0_, x1_, yy1_ = pg.bounds
        def rpts(n):
            out_ = []
            while len(out_) < n:
                pt = (frnd.uniform(x0_, x1_), frnd.uniform(yy0_, yy1_))
                if pg.contains(Point(*pt)): out_.append(pt)
            return out_
        bm_ = bmesh.new()
        for (px, py) in rpts(int(fi_.get('flames', 70))):
            r_ = frnd.uniform(5, 11); h_ = frnd.uniform(14, 34)
            bmesh.ops.create_cone(bm_, cap_ends=True, segments=6, radius1=r_, radius2=0.5, depth=h_, matrix=__import__('mathutils').Matrix.Translation((px, py, 8 + h_ / 2)))
        o_ = obj(f'flames_{int(y0_)}', bm_, m_flame); VIS.append((o_, 'window', (y0_, y1_ + 0.125)))
        bm_ = bmesh.new()
        for (px, py) in rpts(int(fi_.get('smoke', 26))):
            dx, dy = frnd.uniform(0.3, 0.6), frnd.uniform(-0.2, 0.2)   # il vento spinge il fumo
            for k2 in range(4):
                z_ = 55 + k2 * 38; rr_ = frnd.uniform(6, 11) * (1 + 0.45 * k2)   # meta' di prima: coprivano mezza inquadratura
                bmesh.ops.create_icosphere(bm_, subdivisions=2, radius=rr_, matrix=__import__('mathutils').Matrix.Translation((px + dx * z_, py + dy * z_, z_)))
        for f_ in bm_.faces: f_.smooth = True
        o_ = obj(f'smoke_{int(y0_)}', bm_, m_smoke); VIS.append((o_, 'window', (y0_ + 0.004, y1_ + 0.25)))
    log('incendi', len(_fr))
# bacini portuali scavati dopo l'inizio del video (DATA/harbours.json [{"r", "y"}]): terra verde fino all'anno di scavo, poi acqua
if os.path.exists(f'{DATA}/harbours.json') or (LM and LM.get('harbours')):
    _hb = (json.load(open(f'{DATA}/harbours.json')) if os.path.exists(f'{DATA}/harbours.json') else []) + ((LM or {}).get('harbours') or [])
    _hit = []
    for h_ in _hb:
        try: q_ = Polygon(h_['r']).buffer(0)
        except Exception: continue
        bh_ = bmesh.new()
        try: bh_.faces.new([bh_.verts.new((x, y, 0)) for x, y in list(q_.exterior.coords)[:-1]])
        except ValueError: bh_.free(); continue
        bmesh.ops.triangulate(bh_, faces=bh_.faces); _ht = bpy.data.meshes.new('htmp'); bh_.to_mesh(_ht); bh_.free()
        for p_ in _ht.polygons: _hit.append(([tuple(_ht.vertices[i].co[:2]) for i in p_.vertices], h_['y']))
        bpy.data.meshes.remove(_ht)
    # z 0,03: dove la terra chiusa (buffer 45 m) copre i bacini stretti, due piani coincidenti davano macchie nere
    HARB = chunked('harbour', _hit, 0.03, mat('hfield', srgb(CITY.get('field_colors', ['#6a7f45'])[0]), 1.0), 'vanish')
    log('bacini portuali', len(_hb), 'in', len(HARB), 'blocchi')
# copia delle celle vicine (zona citta') come base dei boschi: attributo per vertice = anno di urbanizzazione
# base dei boschi SOLO nella zona inquadrata (celle fini): fuori, decine di km di campagna = milioni di alberi inutili
FB = list(map(float, opt('--forest-box', 4, [str(v) for v in CITY['forest_box']])))
_fit = []
for p_, u_ in zip(lo_.data.polygons, uyl):
    cx_, cy_ = p_.center.x, p_.center.y
    if not (FB[0] < cx_ < FB[2] and FB[1] < cy_ < FB[3]) or p_.area > 20000: continue
    _fit.append(([tuple(lo_.data.vertices[i].co[:2]) for i in p_.vertices], u_))
FOREST = chunked('forest', _fit, 0.0, mat('fbase', srgb(ST.get('forest_base', '#4f7136')), 1.0), 'vanish')
log('boschi', len(_fit), 'celle in', len(FOREST), 'blocchi')
bpy.data.objects.remove(lo_, do_unlink=True)
ROADS_LL = CITY['roads']   # strade disegnate a mano (lat, lon); spente di default
_LAT0, _LON0 = CITY['lat0'], CITY['lon0']; _KX = math.cos(math.radians(_LAT0)) * 111320; _KY = 110540
from shapely.geometry import LineString
_rg = unary_union([LineString([((lo - _LON0) * _KX, (la - _LAT0) * _KY) for la, lo in r]).buffer(5, cap_style=1) for r in ROADS_LL])
if not lgeom.is_empty: _rg = _rg.intersection(lgeom)
bm = bmesh.new()
for g_ in (_rg.geoms if hasattr(_rg, 'geoms') else [_rg]):
    if isinstance(g_, Polygon) and not g_.is_empty:
        try: bm.faces.new([bm.verts.new((x, y, 0.18)) for x, y in list(g_.exterior.coords)[:-1]])
        except ValueError: pass
bmesh.ops.triangulate(bm, faces=bm.faces)
if '--roads' in a: obj('roads', bm, mat('road', srgb('#c2b38f'), 0.95))   # strade disegnate a mano: spente di default (sembravano righe dritte finte)
else: bm.free()
# isolati: impronte degli edifici allargate di qualche metro, piu' chiare (marciapiedi, cortili)
def rings_of(g): return [list(p.exterior.coords)[:-1] for p in (g.geoms if hasattr(g, 'geoms') else [g]) if not p.is_empty]
blocks = []
CH = 600
cells = {}
for p in polys:
    c0 = p.centroid; cells.setdefault((int(c0.x // CH), int(c0.y // CH)), []).append(p.buffer(5, join_style=2))
for k, ps in cells.items(): blocks += rings_of(unary_union(ps).simplify(1.0))
_bit = []
from shapely.strtree import STRtree as _STR
_ptree = _STR(polys)
for r in blocks:
    by = urban_year(*Polygon(r).centroid.coords[0]) if (urban_year and hist) else 0
    if CITY.get('blocks_by_building'):   # l'isolato compare col suo edificio vero piu' vecchio (non con la zona: lastre grigie nel medioevo)
        _ii = _ptree.query(Polygon(r))
        if len(_ii): by = max(by, min(polys_y[i_] for i_ in _ii))
    _bit.append((r, by))
BO = chunked('blocks', _bit, 0.12, mat('blocks', srgb(ST.get('blocks', '#b4ab9c')), 0.9), 'appear')
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
        for x0_, y0_, x1_, y1_, yr_ in CITY['parks']:   # parchi storici con anno noto (NYC: Central Park 1858)
            if x0_ < c_.x < x1_ and y0_ < c_.y < y1_: py_ = max(py_, yr_)
        _pit.append(([tuple(v) for v in r], py_))
    PO = chunked('parks', _pit, 0.25, mat('grass', srgb(ST.get('grass', '#5d7a3a')), 1.0), 'appear')
    tm = mat('tree', srgb(ST.get('tree', '#3d5c2a')), 0.9)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1); tree = bpy.context.object; tree.name = 'tree'; tree.data.materials.append(tm)
    tree.scale = (1, 1, 1.2); tree.hide_render = True; tree.hide_viewport = True
    tg_ = bpy.data.node_groups.new('trees', 'GeometryNodeTree')
    tg_.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); tg_.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    TN = tg_.nodes; TL = tg_.links.new; i_ = TN.new('NodeGroupInput'); o_ = TN.new('NodeGroupOutput')
    dp = TN.new('GeometryNodeDistributePointsOnFaces'); dp.inputs['Density'].default_value = float(opt('--parkdens', 1, str(CITY.get('park_trees', 0.012)))); TL(i_.outputs[0], dp.inputs['Mesh'])
    oi = TN.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = tree
    rv = TN.new('FunctionNodeRandomValue'); rv.data_type = 'FLOAT'
    fl = [x for x in rv.inputs if x.type == 'VALUE' and x.name in ('Min', 'Max')]; fl[0].default_value = CITY.get('tree_scale', [3.5, 6.5])[0]; fl[1].default_value = CITY.get('tree_scale', [3.5, 6.5])[1]
    rvo = [x for x in rv.outputs if x.type == 'VALUE'][0]
    ip = TN.new('GeometryNodeInstanceOnPoints'); TL(dp.outputs['Points'], ip.inputs['Points']); TL(oi.outputs['Geometry'], ip.inputs['Instance']); TL(rvo, ip.inputs['Scale'])
    tr_ = TN.new('GeometryNodeTranslateInstances'); tr_.inputs['Translation'].default_value = (0, 0, CITY.get('tree_lift', 4)); TL(ip.outputs[0], tr_.inputs['Instances'])
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
    t2 = TREES.copy(); [n for n in t2.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0].inputs['Density'].default_value = float(CITY.get('block_trees', 0.0018))
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
WZ = float(CITY.get('water_z', -2))   # canali stretti: l'acqua riflette il sotto della terra (macchie nere) se e' troppo bassa
bm.faces.new([bm.verts.new(v) for v in [(-s, -s, WZ), (s, -s, WZ), (s, s, WZ), (-s, s, WZ)]])
wm = mat('water', srgb(ST.get('water', '#24363c')), ST.get('water_rough', 0.08), haze=False); nt = wm.node_tree
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = ST.get('wave_scale', 0.08); nz.inputs['Detail'].default_value = 6
bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = ST.get('wave_strength', 0.08); nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], nz.inputs['Vector'])
nt.links.new(bp.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
if ST.get('water2'):   # due toni d'acqua a chiazze grandi (correnti, fondali): l'acqua non e' piu' una tinta piatta
    _wn = nt.nodes.new('ShaderNodeTexNoise'); _wn.inputs['Scale'].default_value = 0.0012; _wn.inputs['Detail'].default_value = 3; nt.links.new(tc.outputs['Object'], _wn.inputs['Vector'])
    _wr = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(_wn.outputs['Fac'], _wr.inputs[0])
    _wr.color_ramp.elements[0].position = 0.35; _wr.color_ramp.elements[0].color = (*srgb(ST['water']), 1)
    _wr.color_ramp.elements[1].position = 0.7; _wr.color_ramp.elements[1].color = (*srgb(ST['water2']), 1)
    nt.links.new(_wr.outputs[0], nt.nodes['Principled BSDF'].inputs['Base Color'])
obj('water', bm, hazeify(wm))
log('terra', len(land), 'poligoni')

# ---------- monumenti: parti che crescono dalla loro base, ognuna col suo anno ----------
PARTS = []
def _lmesh(pt):
    bm_ = bmesh.new(); col_ = bm_.loops.layers.color.new('col'); t_ = pt['t']
    zb = pt.get('zbase', pt.get('z0', 0.0))
    cc = (*srgb(pt['c']), pt.get('a', 1.0)); ct = (*srgb(pt.get('top', pt['c'])), 0.0)
    def face(vs, c_):
        try:
            f_ = bm_.faces.new(vs)
            for l_ in f_.loops: l_[col_] = c_
        except ValueError: pass
    def V(x, y, z): return bm_.verts.new((x, y, z - zb))
    def ring_ccw(r_):
        pg = Polygon(r_); rr = list(pg.exterior.coords)[:-1]
        return rr if pg.exterior.is_ccw else rr[::-1]
    def tube(rings_):   # anelli successivi (stesso numero di punti) uniti da quadrilateri
        for ra, rb in zip(rings_, rings_[1:]):
            n_ = len(ra)
            for i in range(n_): face((ra[i], ra[(i + 1) % n_], rb[(i + 1) % n_], rb[i]), cc)
    if t_ == 'prism':
        rr = ring_ccw(pt['r']); vb = [V(x, y, pt['z0']) for x, y in rr]; vt = [V(x, y, pt['z1']) for x, y in rr]
        face(vt, ct if 'top' in pt else (*cc[:3], 0.0)); tube([vb, vt])
    elif t_ == 'wedge':
        rr = ring_ccw(pt['r']); ax_, ay_ = pt['ax']; n_ = math.hypot(ax_, ay_); ax_, ay_ = ax_ / n_, ay_ / n_
        ss = [x * ax_ + y * ay_ for x, y in rr]; s0, s1 = min(ss), max(ss)
        vb = [V(x, y, pt['z0']) for x, y in rr]
        vt = [V(x, y, pt['za'] + (pt['zb'] - pt['za']) * (sv - s0) / (s1 - s0)) for (x, y), sv in zip(rr, ss)]
        face(vt, ct); tube([vb, vt])
    elif t_ == 'hip':
        mrr = Polygon(pt['r']).minimum_rotated_rectangle; c4 = list(mrr.exterior.coords)[:4]
        e1 = (c4[1][0] - c4[0][0], c4[1][1] - c4[0][1]); e2 = (c4[2][0] - c4[1][0], c4[2][1] - c4[1][1])
        if math.hypot(*e1) < math.hypot(*e2): c4 = c4[1:] + c4[:1]; e1, e2 = e2, e1
        Lw = math.hypot(*e1); Ww = math.hypot(*e2); u_ = (e1[0] / Lw, e1[1] / Lw); inset = min(Ww / 2, Lw / 2 - 0.1)
        cx_ = sum(p_[0] for p_ in c4) / 4; cy_ = sum(p_[1] for p_ in c4) / 4; z0_ = pt['z0']; zr = z0_ + pt['rh']
        r1 = V(cx_ - u_[0] * (Lw / 2 - inset), cy_ - u_[1] * (Lw / 2 - inset), zr); r2 = V(cx_ + u_[0] * (Lw / 2 - inset), cy_ + u_[1] * (Lw / 2 - inset), zr)
        if not Polygon(c4).exterior.is_ccw: c4 = c4[::-1]
        vc = [V(x, y, z0_) for x, y in c4]
        # assegna ogni lato al vertice del colmo piu' vicino: due trapezi e due triangoli
        def near(v_): return r1 if (v_.co.x - r1.co.x) ** 2 + (v_.co.y - r1.co.y) ** 2 < (v_.co.x - r2.co.x) ** 2 + (v_.co.y - r2.co.y) ** 2 else r2
        for i in range(4):
            a_, b_ = vc[i], vc[(i + 1) % 4]; na, nb = near(a_), near(b_)
            face((a_, b_, nb) if na is nb else (a_, b_, nb, na), cc)
    elif t_ in ('cyl', 'cone'):
        seg = int(pt.get('seg', 12)); r0 = pt.get('rad', pt.get('r0')); r1 = pt.get('rad', pt.get('r1'))
        ra = [V(pt['cx'] + r0 * math.cos(2 * math.pi * i / seg), pt['cy'] + r0 * math.sin(2 * math.pi * i / seg), pt['z0']) for i in range(seg)]
        rb = [V(pt['cx'] + r1 * math.cos(2 * math.pi * i / seg), pt['cy'] + r1 * math.sin(2 * math.pi * i / seg), pt['z1']) for i in range(seg)]
        tube([ra, rb]); face(rb, (*cc[:3], 0.0))
    elif t_ == 'dome':
        seg = 20; rings_ = []
        for k in range(7):
            th = (math.pi / 2) * k / 6; rr_ = pt['rad'] * math.cos(th) + 1e-3; zz = pt['z0'] + pt['hz'] * math.sin(th)
            rings_.append([V(pt['cx'] + rr_ * math.cos(2 * math.pi * i / seg), pt['cy'] + rr_ * math.sin(2 * math.pi * i / seg), zz) for i in range(seg)])
        tube(rings_)
    elif t_ == 'helix':
        n_s = int(pt.get('n_strands', 1)); steps = 90; w2 = pt['w'] / 2
        for sd in range(n_s):
            rings_ = []
            for k in range(steps + 1):
                u_ = k / steps; ang = 2 * math.pi * pt['turns'] * u_ + 2 * math.pi * sd / n_s
                rr_ = pt['r0'] + (pt['r1'] - pt['r0']) * u_; zz = pt['z0'] + (pt['z1'] - pt['z0']) * u_
                cxk, cyk = pt['cx'] + rr_ * math.cos(ang), pt['cy'] + rr_ * math.sin(ang)
                rx, ry = math.cos(ang), math.sin(ang); tx_, ty_ = -ry, rx
                rings_.append([V(cxk - rx * w2, cyk - ry * w2, zz - w2), V(cxk + rx * w2, cyk + ry * w2, zz - w2),
                               V(cxk + rx * w2, cyk + ry * w2, zz + w2), V(cxk - rx * w2, cyk - ry * w2, zz + w2)])
            tube(rings_)
    bm_.normal_update()
    o_ = obj(f"lm_{pt['name']}_{len(PARTS)}", bm_, CM); o_.data.color_attributes.active_color_name = 'col'
    o_.location.z = zb; o_.scale.z = 0.0
    return o_, zb
if LM:
    _lp = LM['parts']
    if '--crop' in a: _lp = [p_ for p_ in _lp if cx0 < (p_['r'][0][0] if 'r' in p_ else p_['cx']) < cx1 and cy0 < (p_['r'][0][1] if 'r' in p_ else p_['cy']) < cy1]
    for pt in _lp:
        o_, zb = _lmesh(pt)
        PARTS.append({'obj': o_, 'z0': zb, 'b0': pt['y'], 'b1': pt['y'], 'd0': pt.get('d'), 'd1': pt.get('d')})
    log('monumenti costruiti:', len(PARTS), 'parti')
    if NIGHT and LM.get('lights'):   # lampadine di Tivoli: solo di notte
        _lc = [(1.0, 0.85, 0.55), (1.0, 0.25, 0.20), (0.35, 1.0, 0.45), (0.45, 0.65, 1.0)]
        _lmats = []
        for i_, c_ in enumerate(_lc):
            m_ = bpy.data.materials.new(f'bulb{i_}'); m_.use_nodes = True; N_ = m_.node_tree.nodes
            for n_ in list(N_):
                if n_.type != 'OUTPUT_MATERIAL': N_.remove(n_)
            e_ = N_.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (*c_, 1); e_.inputs['Strength'].default_value = ST.get('bulb', 18.0)
            m_.node_tree.links.new(e_.outputs[0], N_['Material Output'].inputs['Surface']); _lmats.append(m_)
        for i_ in range(4):
            bm_ = bmesh.new()
            for x_, y_, z_, k_ in LM['lights']:
                if k_ == i_: bmesh.ops.create_cube(bm_, size=0.9, matrix=__import__('mathutils').Matrix.Translation((x_, y_, z_)))
            o_ = obj(f'bulbs{i_}', bm_, _lmats[i_]); VIS.append((o_, 'appear', LM.get('lights_year', 1843)))
    json.dump(LM.get('labels', []), open(f'{OUT}/labels.json', 'w'))
# ---------- luce, cielo, camera ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new('ShaderNodeTexSky')
try: sky.sky_type = 'NISHITA'
except Exception: pass
SUNEL = float(opt('--sun', 1, '17'))
if LIGHT == 'sunset': SUNEL = ST.get('sunset_el', 3.0)   # sole basso: ombre lunghe, luce arancio
_dummy = 0; sky.sun_elevation = math.radians(SUNEL); sky.sun_rotation = math.radians(230)
WN = w.node_tree.nodes; WL = w.node_tree.links.new; bg = WN['Background']
WL(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = ST.get('sky_light', 0.35)
bg2 = WN.new('ShaderNodeBackground'); bg2.inputs['Color'].default_value = (*HAZE, 1); bg2.inputs['Strength'].default_value = 1.0
# cielo visto dalla camera: sfumato (foschia all'orizzonte -> azzurro in alto), alone caldo verso il sole, nuvole sottili
def sky_grad():
    tc_ = WN.new('ShaderNodeTexCoord'); nd = WN.new('ShaderNodeVectorMath'); nd.operation = 'NORMALIZE'; WL(tc_.outputs['Generated'], nd.inputs[0])
    sp = WN.new('ShaderNodeSeparateXYZ'); WL(nd.outputs[0], sp.inputs[0])
    rp = WN.new('ShaderNodeValToRGB'); WL(sp.outputs['Z'], rp.inputs[0]); cr_ = rp.color_ramp; cr_.interpolation = 'EASE'
    _SK = {'sunset': [(1.0, 0.55, 0.28), (0.12, 0.14, 0.32), (1.0, 0.62, 0.38), (0.78, 0.52, 0.55), (0.32, 0.30, 0.52)]}.get(LIGHT,
           [HAZE, (0.08, 0.20, 0.52), (0.86, 0.78, 0.70), (0.50, 0.62, 0.84), (0.20, 0.36, 0.70)])
    cr_.elements[0].position = 0.0; cr_.elements[0].color = (*_SK[0], 1)
    cr_.elements[1].position = 0.5; cr_.elements[1].color = (*_SK[1], 1)
    for p_, c_ in [(0.035, _SK[2]), (0.10, _SK[3]), (0.25, _SK[4])]:
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
if '--flat-sky' not in a and not NIGHT: sky_grad()
if NIGHT:
    bg.inputs['Strength'].default_value = ST.get('night_sky', 0.02); bg2.inputs['Color'].default_value = (*srgb(ST.get('night_sky_col', '#0b1426')), 1); bg2.inputs['Strength'].default_value = 1.0
    if LIGHT == 'twilight':   # crepuscolo: cielo blu profondo ancora luminoso, luci gia' accese
        bg.inputs['Strength'].default_value = ST.get('twilight_sky', 0.12); bg2.inputs['Color'].default_value = (*srgb(ST.get('twilight_sky_col', '#2c3e6b')), 1)
lp = WN.new('ShaderNodeLightPath'); mxw = WN.new('ShaderNodeMixShader')
if ST.get('sky_in_reflections'):   # l'acqua e i vetri riflettono il cielo sfumato con le nuvole (prima: cielo piatto, acqua spenta)
    _cg = WN.new('ShaderNodeMath'); _cg.operation = 'MAXIMUM'; WL(lp.outputs['Is Camera Ray'], _cg.inputs[0]); WL(lp.outputs['Is Glossy Ray'], _cg.inputs[1]); WL(_cg.outputs[0], mxw.inputs[0])
else: WL(lp.outputs['Is Camera Ray'], mxw.inputs[0])
WL(bg.outputs[0], mxw.inputs[1]); WL(bg2.outputs[0], mxw.inputs[2])
WL(mxw.outputs[0], WN['World Output'].inputs['Surface'])
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = ST.get('sun_energy', 4.4); sun.angle = math.radians(1.0); sun.color = (1, 0.84, 0.66)
if NIGHT: sun.energy = ST.get('moon', 0.35); sun.color = (0.55, 0.65, 1.0)
if LIGHT == 'twilight': sun.energy = ST.get('twilight_sun', 0.6); sun.color = (0.62, 0.62, 0.95)
if LIGHT == 'sunset': sun.energy = ST.get('sunset_sun', 4.2); sun.color = (1.0, 0.52, 0.24)
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
    q = max(1, FPS // 4); rate = abs(year_at(f + q) - year_at(max(1, f - q))) / (2 * q / FPS); return max(float(CITY.get('dur_min', 0.4)), min(25.0, rate * 0.6))
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
DEV = opt('--device', 1, 'OPTIX' if GPU else 'CPU')
if DEV in ('OPTIX', 'CUDA'):
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = DEV; pr.get_devices()
    for d in pr.devices: d.use = d.type == DEV
    sc.cycles.device = 'GPU'; log('GPU', DEV, [d.name for d in pr.devices if d.use])
    if not any(d.use and d.type == DEV for d in pr.devices):   # 19 ott 2026: la GPU del pod non rispondeva e Blender ripiegava in silenzio sul processore (8 s/fotogramma)
        print('[build] ERRORE: nessuna GPU ' + DEV + ' disponibile. Mi fermo invece di renderizzare col processore. Termina il pod e aprine un altro.', flush=True); sys.exit(3)
else: log('CPU')
DN = opt('--denoiser', 1, 'auto')   # auto: OptiX su GPU OptiX (si avvia in fretta), altrimenti OIDN; none: niente denoiser
if DN == 'none': sc.cycles.use_denoising = False
else:
    try: sc.cycles.denoiser = 'OPTIX' if (DN == 'optix' or (DN == 'auto' and DEV == 'OPTIX')) else 'OPENIMAGEDENOISE'
    except Exception as e_: log('denoiser', e_)
log('denoiser', sc.cycles.denoiser if sc.cycles.use_denoising else 'nessuno')
sc.render.resolution_x = RW; sc.render.resolution_y = RH
sc.view_settings.view_transform = CITY.get('view_transform', 'AgX'); sc.view_settings.look = CITY.get('look', 'AgX - Punchy'); sc.view_settings.exposure = float(CITY.get('exposure', -0.4))
sc.view_settings.exposure += float(ST.get('exp_' + LIGHT, 0.0))   # compensazione per passata di luce
# saturazione: si aggiunge al montaggio (ffmpeg eq=saturation), non qui
EXT = opt('--ext', 1, 'jpg')   # jpg 95: ~0,7 MB a 1080p (png ~3-8 MB: 7839 fotogrammi riempiono il disco)
_is = sc.render.image_settings; _is.file_format = 'JPEG' if EXT == 'jpg' else 'PNG'; _is.color_mode = 'RGB'
if EXT == 'jpg': _is.quality = 95
else: _is.compression = 15
sc.render.filepath = os.path.join(OUT, '')
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
NW = 5 if F1 > 9999 else 4   # oltre 9999 fotogrammi: nomi a 5 cifre (con 4 l'ordine alfabetico mescolava i fotogrammi)
done = 0
_ONLY = [int(v) for v in opt('--only', 1, '').split(',') if v] if '--only' in a else None   # prove: solo questi fotogrammi (es. 133,3241)
for f in (_ONLY or range(F0, F1 + 1, sc.frame_step)):
    path = os.path.join(OUT, f'{f:0{NW}d}.{EXT}')
    if any(os.path.exists(q_) and os.path.getsize(q_) > 0 for q_ in (os.path.join(OUT, f'{f:0{NW}d}.jpg'), os.path.join(OUT, f'{f:0{NW}d}.png'))): continue
    t_ = time.time(); sc.frame_set(f); y_ = YF[f]
    _l = lens_at(f)
    if abs(cam.lens - _l) > 1e-3: cam.lens = _l
    for ch in CHUNKS:
        g_ = growth(ch, f); setvis(ch['obj'], g_ < 0.002)
        if g_ >= 0.002 and abs(ch['obj'].scale.z - g_) > 1e-4: ch['obj'].scale.z = g_
    for pt in PARTS:
        g_ = growth(pt, f); o_ = pt['obj']; hid = g_ < 0.002
        if VISSET.get(o_.name) != hid: o_.location.z = -5000.0 if hid else pt['z0']; VISSET[o_.name] = hid
        if not hid and abs(o_.scale.z - g_) > 1e-4: o_.scale.z = g_
    for o_, kind, thr in VIS: setvis(o_, (y_ < thr) if kind == 'appear' else (y_ >= thr) if kind == 'vanish' else not (thr[0] <= y_ < thr[1]))
    sc.render.filepath = path; bpy.ops.render.render(write_still=True); done += 1
    print(f'[build] fotogramma {f}: {time.time() - t_:.1f}s (anno {y_:.0f})', flush=True)
n = max(1, done); log(f'FATTO {done} fotogrammi, {(time.time()-tr)/n:.2f}s a fotogramma')
