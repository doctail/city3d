# Costantinopoli 1453 su terreno vero (Copernicus GLO-30 N40+N41 E028, Sentinel-2 cloudless 2016 EOX CC BY 4.0).
# Mura teodosiane modellate (fossato, muro esterno, terrazza, muro interno, torri, merli), cannone di Orban con colpo e impatto,
# breccia che si apre e si ripara di notte, catena del Corno d'Oro, flotta, navi trascinate sulla collina di Galata, assalto finale.
# Uso: python cpl.py <secondo> <out.png> [w h spp]       (24 fps; tempi = audio/cpl_tempi.json)
import sys, os, math, json, random
import numpy as np, tifffile, bpy, mathutils as mu
from scipy import ndimage
from bpy_extras.object_utils import world_to_camera_view

SEC = float(sys.argv[1]); OUT = sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 540; H = int(sys.argv[4]) if len(sys.argv) > 4 else 960
SPP = int(sys.argv[5]) if len(sys.argv) > 5 else 16
D = os.environ.get('DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') + '/')

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def win(a, b, r=0.4): return ease((SEC - a) / r) * (1 - ease((SEC - b) / r))
def lerp(a, b, k): return a + (b - a) * k

# ---------------- sistema di riferimento: 1 unita' = 10 m, rilievo x1.6, oggetti costruiti x2 in altezza per leggibilita'
LAT0, LON0 = 41.0215, 28.9262                       # Porta di San Romano (Topkapi), dove sta il cannone [Likely]
KX = 111320 * math.cos(math.radians(LAT0)); KY = 110950
SC, EX, OEX = 10.0, 1.6, 2.0
SEA = 0.8                                           # metri: sotto e' acqua
def xy(lat, lon): return ((lon - LON0) * KX / SC, (lat - LAT0) * KY / SC)
def ll(x, y): return (LAT0 + y * SC / KY, LON0 + x * SC / KX)

# ---------------- DEM: due tile 1x1 grado unite, edifici moderni tolti (mediana + gauss), mare a 0
DEMF = os.path.join(D, 'dem_smooth.npy')
if os.path.exists(DEMF): dem = np.load(DEMF)
else:
    a41 = tifffile.TiffFile(D + 'Copernicus_DSM_COG_10_N41_00_E028_00_DEM.tif').pages[0].asarray()
    a40 = tifffile.TiffFile(D + 'Copernicus_DSM_COG_10_N40_00_E028_00_DEM.tif').pages[0].asarray()
    full = np.vstack([a41, a40]).astype(np.float32)          # righe: lat 42 -> 40
    r0, r1 = int((42 - 41.10) * 3600), int((42 - 40.95) * 3600); c0, c1 = int(0.82 * 3600), int(1.08 * 3600)
    sub = full[r0:r1, c0:c1]
    sub = ndimage.median_filter(sub, size=7); sub = ndimage.gaussian_filter(sub, 1.6)
    full[r0:r1, c0:c1] = sub; dem = full; np.save(DEMF, dem)
NR = dem.shape[0]
def elev_np(lat, lon):
    r = (42 - lat) * 3600; c = (lon - 28) * 3600
    r0 = np.clip(np.floor(r).astype(int), 0, NR - 2); c0 = np.clip(np.floor(c).astype(int), 0, dem.shape[1] - 2); fr = r - r0; fc = c - c0
    e = dem[r0, c0] * (1 - fr) * (1 - fc) + dem[r0 + 1, c0] * fr * (1 - fc) + dem[r0, c0 + 1] * (1 - fr) * fc + dem[r0 + 1, c0 + 1] * fr * fc
    return np.maximum(e, 0)
def elev(lat, lon): return float(elev_np(np.array([lat]), np.array([lon]))[0])
def zof(lat, lon): return elev(lat, lon) / SC * EX
def zxy(x, y): return zof(*ll(x, y))
ZSEA = SEA / SC * EX

bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene

# ---------------- luce del racconto: notte (riparazioni, assalto), alba, giorno
NIGHT = max(win(35.0, 37.9, 0.6), win(50.8, 56.2, 0.8))
DAWN = win(55.6, 59.0, 1.2)
TODAY = 0.0

# ---------------- terreno vettoriale (veloce anche a 1400x1000)
LATA, LATB, LONA, LONB = 40.962, 41.092, 28.835, 29.065
NX, NY = int(os.environ.get('TNX', 1300)), int(os.environ.get('TNY', 950))
lons = np.linspace(LONA, LONB, NX); lats = np.linspace(LATA, LATB, NY)
LO, LA = np.meshgrid(lons, lats)
Z = elev_np(LA, LO) / SC * EX
X = (LO - LON0) * KX / SC; Y = (LA - LAT0) * KY / SC
Z14 = 2 ** 14; TX0, TY0, TX1, TY1 = 9503, 6136, 9516, 6147
U = ((LO + 180) / 360 * Z14 - TX0) / (TX1 - TX0)
YT = (1 - np.log(np.tan(np.radians(LA)) + 1 / np.cos(np.radians(LA))) / np.pi) / 2 * Z14
V = 1 - (YT - TY0) / (TY1 - TY0)
me = bpy.data.meshes.new('terrain')
nv = NX * NY; me.vertices.add(nv); me.vertices.foreach_set('co', np.stack([X, Y, Z], -1).ravel().astype(np.float32))
ii, jj = np.meshgrid(np.arange(NX - 1), np.arange(NY - 1)); a = (jj * NX + ii).ravel()
quads = np.stack([a, a + 1, a + NX + 1, a + NX], -1).ravel()
nq = len(a); me.loops.add(nq * 4); me.polygons.add(nq)
me.loops.foreach_set('vertex_index', quads.astype(np.int32))
me.polygons.foreach_set('loop_start', (np.arange(nq) * 4).astype(np.int32)); me.polygons.foreach_set('loop_total', np.full(nq, 4, np.int32))
me.polygons.foreach_set('use_smooth', np.ones(nq, bool))
me.update(calc_edges=True)
uvl = me.uv_layers.new(); uvs = np.stack([U.ravel(), V.ravel()], -1)[quads]
uvl.data.foreach_set('uv', uvs.ravel().astype(np.float32))
mt = bpy.data.materials.new('terrain'); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes['Principled BSDF']
L = nt.links
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(D + 'satellite_z14.jpg'); tx.interpolation = 'Cubic'
hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 0.45; hsv.inputs['Value'].default_value = 0.62
L.new(tx.outputs['Color'], hsv.inputs['Color'])
geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs['Vector'])
# campagna del 1453: colori di campi e macchia da rumore, al posto della citta' moderna
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.035; nz.inputs['Detail'].default_value = 6
L.new(geo.outputs['Position'], nz.inputs['Vector'])
fr = nt.nodes.new('ShaderNodeValToRGB'); E = fr.color_ramp.elements
E[0].position = 0.35; E[0].color = (0.10, 0.12, 0.06, 1); E[1].position = 0.70; E[1].color = (0.24, 0.22, 0.13, 1)
e2 = E.new(0.52); e2.color = (0.15, 0.17, 0.08, 1)
L.new(nz.outputs['Fac'], fr.inputs['Fac'])
nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 1.4; nz2.inputs['Detail'].default_value = 8
L.new(geo.outputs['Position'], nz2.inputs['Vector'])
mx0 = nt.nodes.new('ShaderNodeMix'); mx0.data_type = 'RGBA'; mx0.blend_type = 'MULTIPLY'; mx0.inputs['Factor'].default_value = 0.35
L.new(fr.outputs['Color'], mx0.inputs['A']); L.new(nz2.outputs['Color'], mx0.inputs['B'])
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['Factor'].default_value = 0.62
L.new(mx0.outputs['Result'], mix.inputs['A']); L.new(hsv.outputs['Color'], mix.inputs['B'])
bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25; L.new(nz2.outputs['Fac'], bump.inputs['Height'])
L.new(bump.outputs['Normal'], b.inputs['Normal'])
L.new(mix.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.95
me.materials.append(mt); ter = bpy.data.objects.new('terrain', me); sc.collection.objects.link(ter)

# ---------------- acqua con onde leggere e riflesso del cielo
def water(name, z, size=4000):
    m = bpy.data.meshes.new(name); m.from_pydata([(-size, -size, z), (size, -size, z), (size, size, z), (-size, size, z)], [], [(0, 1, 2, 3)])
    mm = bpy.data.materials.new(name); mm.use_nodes = True; n = mm.node_tree; bb = n.nodes['Principled BSDF']
    bb.inputs['Base Color'].default_value = (0.01, 0.035, 0.06, 1); bb.inputs['Roughness'].default_value = 0.32
    w = n.nodes.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value = 0.6; w.inputs['Distortion'].default_value = 6
    bm = n.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.08
    n.links.new(w.outputs['Fac'], bm.inputs['Height']); n.links.new(bm.outputs['Normal'], bb.inputs['Normal'])
    m.materials.append(mm); o = bpy.data.objects.new(name, m); sc.collection.objects.link(o); return o
water('sea', ZSEA)

# ---------------- accumulatori di geometria per materiale
GEO = {}
def poly(m, pts, faces):
    Vv, Ff = GEO.setdefault(m, ([], [])); o = len(Vv); Vv.extend(pts); Ff.extend([[o + i for i in f] for f in faces])
BOXF = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
def obox(m, c, ang, sx, sy, z0, z1):
    ca, sa = math.cos(ang), math.sin(ang); P = []
    for z in (z0, z1):
        for dx, dy in ((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)):
            P.append((c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca, z))
    poly(m, P, BOXF)
def cyl(m, c, r0, r1, z0, z1, seg=8, cap=True):
    P = [(c[0] + r0 * math.cos(2 * math.pi * i / seg), c[1] + r0 * math.sin(2 * math.pi * i / seg), z0) for i in range(seg)]
    P += [(c[0] + r1 * math.cos(2 * math.pi * i / seg), c[1] + r1 * math.sin(2 * math.pi * i / seg), z1) for i in range(seg)]
    F = [[i, (i + 1) % seg, seg + (i + 1) % seg, seg + i] for i in range(seg)]
    if cap: F += [list(range(seg))[::-1], list(range(seg, 2 * seg))]
    poly(m, P, F)
def tube(m, p0, p1, r, seg=8):
    """cilindro tra due punti 3D qualsiasi"""
    p0 = mu.Vector(p0); p1 = mu.Vector(p1); d = (p1 - p0); q = d.to_track_quat('Z', 'Y')
    P = []
    for p, in ((p0,), (p1,)):
        for i in range(seg):
            v = q @ mu.Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), 0)); P.append(tuple(p + v))
    poly(m, P, [[i, (i + 1) % seg, seg + (i + 1) % seg, seg + i] for i in range(seg)] + [list(range(seg))[::-1], list(range(seg, 2 * seg))])
def sphere(m, c, r, seg=8, ring=5):
    P = [(c[0], c[1], c[2] - r)]
    for j in range(1, ring):
        ph = -math.pi / 2 + math.pi * j / ring
        for i in range(seg):
            P.append((c[0] + r * math.cos(ph) * math.cos(2 * math.pi * i / seg), c[1] + r * math.cos(ph) * math.sin(2 * math.pi * i / seg), c[2] + r * math.sin(ph)))
    P.append((c[0], c[1], c[2] + r)); F = []
    for i in range(seg): F.append([0, 1 + (i + 1) % seg, 1 + i])
    for j in range(ring - 2):
        for i in range(seg):
            a_ = 1 + j * seg + i; b_ = 1 + j * seg + (i + 1) % seg; F.append([a_, b_, b_ + seg, a_ + seg])
    top = len(P) - 1; base = 1 + (ring - 2) * seg
    for i in range(seg): F.append([base + i, base + (i + 1) % seg, top])
    poly(m, P, F)
def ribbon(m, pts, w=1.0, lift=0.6, upto=1.0, arrow=False, dash=0.0, onwater=True):
    """nastro (lat, lon) drappeggiato su terreno/acqua"""
    P = []
    for k in range(len(pts) - 1):
        (la0, lo0), (la1, lo1) = pts[k], pts[k + 1]
        for s in range(16):
            t = s / 16; la, lo = la0 + (la1 - la0) * t, lo0 + (lo1 - lo0) * t; x, y = xy(la, lo)
            P.append((x, y, max(zof(la, lo), ZSEA if onwater else 0) + lift))
    la, lo = pts[-1]; x, y = xy(la, lo); P.append((x, y, max(zof(la, lo), ZSEA) + lift))
    Lc = [0.0]
    for k in range(1, len(P)): Lc.append(Lc[-1] + math.dist(P[k][:2], P[k - 1][:2]))
    Q = [(p, l) for p, l in zip(P, Lc) if l <= Lc[-1] * upto]
    if len(Q) < 3: return
    for k in range(len(Q) - 1):
        (a_, la_), (b_, _) = Q[k], Q[k + 1]
        if dash and int(la_ / dash) % 2: continue
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]; l_ = math.hypot(dx, dy) or 1; nx_, ny_ = -dy / l_ * w / 2, dx / l_ * w / 2
        poly(m, [(a_[0] + nx_, a_[1] + ny_, a_[2]), (b_[0] + nx_, b_[1] + ny_, b_[2]), (b_[0] - nx_, b_[1] - ny_, b_[2]), (a_[0] - nx_, a_[1] - ny_, a_[2])], [[0, 1, 2, 3]])
    if arrow:
        a_, b_ = Q[-2][0], Q[-1][0]; dx, dy = b_[0] - a_[0], b_[1] - a_[1]; l_ = math.hypot(dx, dy) or 1; ux, uy = dx / l_, dy / l_
        poly(m, [(b_[0] - uy * w * 2, b_[1] + ux * w * 2, b_[2]), (b_[0] + ux * w * 5, b_[1] + uy * w * 5, b_[2]), (b_[0] + uy * w * 2, b_[1] - ux * w * 2, b_[2])], [[0, 1, 2]])

class Path:
    def __init__(s, pts, ll_=True):
        s.P = [mu.Vector(xy(*p)) if ll_ else mu.Vector(p) for p in pts]; s.C = [0.0]
        for k in range(1, len(s.P)): s.C.append(s.C[-1] + (s.P[k] - s.P[k - 1]).length)
        s.L = s.C[-1]
    def at(s, d):
        d = max(0.0, min(s.L, d))
        for k in range(1, len(s.P)):
            if d <= s.C[k] or k == len(s.P) - 1:
                f = (d - s.C[k - 1]) / max(1e-6, s.C[k] - s.C[k - 1]); v = s.P[k] - s.P[k - 1]; p = s.P[k - 1] + v * f
                return p.x, p.y, math.atan2(v.y, v.x)

# ================= LE MURA TEODOSIANE =================
# tracciato [Likely, +-100 m]: Porta Aurea (40.9928, 28.9225), IV porta militare (41.0191, 28.9243), mura delle Blacherne (41.0370, 28.9392), Ayvansaray
WALL_LL = [(40.9918, 28.9228), (40.9928, 28.9225), (40.9965, 28.9203), (41.0013, 28.9176), (41.0080, 28.9164), (41.0150, 28.9200),
           (41.0191, 28.9243), (41.0215, 28.9262), (41.0255, 28.9298), (41.0295, 28.9338), (41.0336, 28.9388), (41.0370, 28.9395), (41.0388, 28.9428)]
WP = Path(WALL_LL)
SBR = WP.C[7]                                       # distanza lungo il muro della breccia (San Romano)
def wall_frame(d):
    """punto sul tracciato + direzione verso l'esterno (ovest)"""
    x, y, a = WP.at(d); ox, oy = -math.sin(a), math.cos(a)   # normale verso l'esterno (ovest): sinistra del verso sud->nord
    return x, y, a, ox, oy
# danni alla breccia: si apre col cannone, di notte si ripara con legname, all'ultimo cade
HIT1 = ease((SEC - 6.05) / 0.25); HIT2 = ease((SEC - 29.35) / 0.25); HIT3 = ease((SEC - 34.05) / 0.25)
dmg_open = max(0.25 * HIT1 * (1 - ease((SEC - 8.0) / 1.0)), 0.45 * HIT2, 0.85 * HIT3)        # il gancio mostra un colpo, poi si torna a muro intatto
dmg_open *= 1 - 0.7 * ease((SEC - 35.6) / 1.8)                                                # riparazione notturna
FALL = ease((SEC - 53.6) / 1.0)
dmg = max(dmg_open, FALL)
STOCK = ease((SEC - 35.8) / 1.6) * (1 - FALL)                                                # palizzata di legno nella breccia
BW = 6.0                                                                                       # mezza larghezza della breccia (unita')
def wall_height(d, h):
    k = max(0.0, 1 - abs(d - SBR) / BW); return h * (1 - dmg * min(1, k * 1.6))
def build_walls():
    step = 0.45; n = int(WP.L / step)
    OFF = dict(moat=4.2, outer=2.0, inner=-0.6)
    for i in range(n):
        d0, d1 = i * step, (i + 1) * step
        x0, y0, a0, ox0, oy0 = wall_frame(d0); x1, y1, a1, ox1, oy1 = wall_frame(d1)
        g0, g1 = zxy(x0, y0), zxy(x1, y1)
        if g0 < ZSEA + 0.1 and g1 < ZSEA + 0.1: continue
        # fossato: striscia d'acqua incassata e argine
        for (off, th, h, mat, crenel) in ((OFF['outer'], 0.22, 0.9 * OEX, 'stoneO', True), (OFF['inner'], 0.42, 1.2 * OEX, 'stone', True)):
            hh0, hh1 = wall_height(d0, h), wall_height(d1, h)
            c00 = (x0 + ox0 * (off - th), y0 + oy0 * (off - th)); c01 = (x0 + ox0 * (off + th), y0 + oy0 * (off + th))
            c10 = (x1 + ox1 * (off - th), y1 + oy1 * (off - th)); c11 = (x1 + ox1 * (off + th), y1 + oy1 * (off + th))
            P = [(*c00, g0 - 0.4), (*c01, g0 - 0.4), (*c11, g1 - 0.4), (*c10, g1 - 0.4), (*c00, g0 + hh0), (*c01, g0 + hh0), (*c11, g1 + hh1), (*c10, g1 + hh1)]
            poly(mat, P, [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
            if crenel and i % 2 == 0 and hh0 > h * 0.8:                              # merli
                cx, cy = x0 + ox0 * (off + th * 0.7), y0 + oy0 * (off + th * 0.7)
                obox(mat, (cx, cy), a0, 0.13, 0.07, g0 + hh0, g0 + hh0 + 0.16 * OEX)
        # fossato
        mo, mw = OFF['moat'], 1.0
        P = [(x0 + ox0 * (mo - mw), y0 + oy0 * (mo - mw), g0 - 0.15), (x0 + ox0 * (mo + mw), y0 + oy0 * (mo + mw), g0 - 0.15),
             (x1 + ox1 * (mo + mw), y1 + oy1 * (mo + mw), g1 - 0.15), (x1 + ox1 * (mo - mw), y1 + oy1 * (mo - mw), g1 - 0.15)]
        poly('moat', P, [[0, 1, 2, 3]])
        P = [(x0 + ox0 * (mo - mw - 0.12), y0 + oy0 * (mo - mw - 0.12), g0 - 0.3), (x0 + ox0 * (mo - mw - 0.12), y0 + oy0 * (mo - mw - 0.12), g0 + 0.25),
             (x1 + ox1 * (mo - mw - 0.12), y1 + oy1 * (mo - mw - 0.12), g1 + 0.25), (x1 + ox1 * (mo - mw - 0.12), y1 + oy1 * (mo - mw - 0.12), g1 - 0.3)]
        poly('stoneO', P, [[0, 1, 2, 3]])                                             # parapetto del fossato
    # torri: 96 sul muro interno (ogni ~7 unita'), torri del muro esterno sfalsate
    k = 0; d = 1.5
    while d < WP.L - 1:
        x, y, a, ox, oy = wall_frame(d); g = zxy(x, y)
        if g > ZSEA + 0.2:
            h = wall_height(d, 2.0 * OEX)
            cx, cy = x + ox * (OFF['inner'] - 0.4), y + oy * (OFF['inner'] - 0.4)
            if k % 2: cyl('stone', (cx, cy), 0.95, 0.9, g - 0.4, g + h, seg=8)
            else: obox('stone', (cx, cy), a, 0.9, 0.9, g - 0.4, g + h)
            if h > 2.0 * OEX * 0.85:
                obox('roof', (cx, cy), a, 0.95, 0.95, g + h, g + h + 0.12)
                for q in range(4):                                                   # merli in cima alla torre
                    qa = a + q * math.pi / 2; obox('stone', (cx + 0.75 * math.cos(qa), cy + 0.75 * math.sin(qa)), qa, 0.14, 0.14, g + h + 0.12, g + h + 0.4)
            ex_, ey_ = x + ox * (OFF['outer'] - 0.35), y + oy * (OFF['outer'] - 0.35)
            dd = d + 3.5; x2, y2, a2, ox2, oy2 = wall_frame(min(dd, WP.L)); g2 = zxy(x2, y2)
            if g2 > ZSEA + 0.2 and dd < WP.L - 1:
                h2 = wall_height(dd, 1.3 * OEX); obox('stoneO', (x2 + ox2 * (OFF['outer'] + 0.35), y2 + oy2 * (OFF['outer'] + 0.35)), a2, 0.55, 0.55, g2 - 0.3, g2 + h2)
            k += 1
        d += 7.0
    return k
NTOW = build_walls()

# macerie e palizzata nella breccia
rr = random.Random(7)
if dmg > 0.05:
    for i in range(int(90 * dmg)):
        d = SBR + rr.uniform(-BW, BW); x, y, a, ox, oy = wall_frame(d); off = rr.uniform(-3.5, 1.5); g = zxy(x + ox * off, y + oy * off)
        s_ = rr.uniform(0.12, 0.45); obox('rubble', (x + ox * off, y + oy * off), rr.uniform(0, 3), s_, s_ * 0.8, g - 0.1, g + s_ * rr.uniform(0.6, 1.4))
if STOCK > 0.02:
    for i in range(int(26 * STOCK)):
        d = SBR - BW * 0.8 + i * 0.36; x, y, a, ox, oy = wall_frame(d); g = zxy(x, y)
        cx, cy = x - ox * 0.2, y - oy * 0.2; tube('wood', (cx, cy, g - 0.2), (cx + ox * 0.15, cy + oy * 0.15, g + 1.5 * OEX * STOCK), 0.09, 6)
    for k in range(3):
        x0_, y0_, _, ox, oy = wall_frame(SBR - BW * 0.8); x1_, y1_, _, _, _ = wall_frame(SBR + BW * 0.6)
        zz = zxy(x0_, y0_) + (0.6 + 0.8 * k) * STOCK * OEX
        tube('wood', (x0_ + ox * 0.55, y0_ + oy * 0.55, zz), (x1_ + ox * 0.55, y1_ + oy * 0.55, zz), 0.07, 5)

# ================= IL CANNONE DI ORBAN, di fronte alla porta di San Romano =================
xb, yb, ab, oxb, oyb = wall_frame(SBR)
CAN = (xb + oxb * 55, yb + oyb * 55)                 # ~550 m fuori dalle mura [Guessing sulla distanza esatta]
gc = zxy(*CAN); aim = math.atan2(yb - CAN[1], xb - CAN[0])
def build_cannon(recoil=0.0):
    ca, sa = math.cos(aim), math.sin(aim); bx, by = CAN[0] - ca * recoil, CAN[1] - sa * recoil
    L_, r_ = 1.8 * OEX * 0.5, 0.42                    # 9 m, bocca ~1 m (x2 di leggibilita')
    p0 = (bx - ca * L_ / 2, by - sa * L_ / 2, gc + 0.55); p1 = (bx + ca * L_ / 2, by + sa * L_ / 2, gc + 0.7)
    tube('bronze', p0, p1, r_, 14)
    tube('bronze', (p0[0] - ca * 0.6, p0[1] - sa * 0.6, p0[2] - 0.03), p0, r_ * 0.75, 12)       # camera di scoppio
    for t in (0.15, 0.5, 0.85):                                                                     # anelli
        q = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t)
        tube('bronzeD', (q[0] - ca * 0.05, q[1] - sa * 0.05, q[2]), (q[0] + ca * 0.05, q[1] + sa * 0.05, q[2]), r_ * 1.08, 14)
    obox('wood', (bx, by), aim, L_ * 0.7, 0.75, gc - 0.1, gc + 0.3)                                 # letto di travi
    for k in range(5):
        tube('wood', (bx - ca * (L_ * 0.6 + 0.2) - sa * (0.9 - 0.45 * k), by - sa * (L_ * 0.6 + 0.2) + ca * (0.9 - 0.45 * k), gc + 0.05),
             (bx - ca * (L_ * 0.6 + 0.2) - sa * (0.9 - 0.45 * k), by - sa * (L_ * 0.6 + 0.2) + ca * (0.9 - 0.45 * k), gc + 0.9), 0.08, 6)
    for k in range(-4, 5):                                                                          # gabbioni davanti
        cx, cy = CAN[0] + ca * 2.2 - sa * k * 0.45, CAN[1] + sa * 2.2 + ca * k * 0.45; cyl('wicker', (cx, cy), 0.22, 0.22, gc - 0.1, gc + 0.55, 8)
    return p1
SHOTS = [5.25, 28.55, 33.25, 52.8]                    # secondi dello sparo (impatto ~0,8 s dopo)
recoil = sum(0.5 * math.exp(-(SEC - s) * 3) for s in SHOTS if SEC >= s)
MUZ = build_cannon(min(recoil, 0.6))
# polveri, palle di pietra, tende e uomini attorno
for k in range(6): sphere('stoneball', (CAN[0] - 2.5 + (k % 3) * 0.5, CAN[1] + 1.6 + (k // 3) * 0.5, gc + 0.25), 0.22, 8, 5)

def shot_fx(t0):
    dt = SEC - t0
    if dt < -0.05 or dt > 4.0: return
    tgt = (xb + oxb * 0.5, yb + oyb * 0.5, zxy(xb, yb) + 1.6)
    FL = 0.8
    if 0 <= dt <= 0.25: sphere('flash', MUZ, 0.4 + 1.6 * dt, 10, 6)                                   # lampo di bocca
    if 0 <= dt <= FL:                                                                                  # palla e scia
        k = dt / FL; p = [lerp(MUZ[i], tgt[i], k) for i in range(3)]; p[2] += 4.0 * math.sin(math.pi * k)
        sphere('ball', tuple(p), 0.3, 8, 5)
        for j in range(1, 10):
            kk = max(0, k - j * 0.02); q = [lerp(MUZ[i], tgt[i], kk) for i in range(3)]; q[2] += 4.0 * math.sin(math.pi * kk)
            sphere('trail', tuple(q), 0.22 * (1 - j / 10), 6, 4)
    if dt >= 0:                                                                                        # fumo di bocca
        rs = random.Random(int(t0 * 100))
        for j in range(14):
            u = min(dt, 3.5); dirx = math.cos(aim) * (0.6 + rs.random()) * u * 1.6 - math.sin(aim) * rs.uniform(-1, 1) * u
            diry = math.sin(aim) * (0.6 + rs.random()) * u * 1.6 + math.cos(aim) * rs.uniform(-1, 1) * u
            sphere('smoke', (MUZ[0] + dirx + 1.2 * u, MUZ[1] + diry - 1.0 * u, MUZ[2] + 0.3 + u * rs.uniform(0.8, 1.8)), 0.35 + u * rs.uniform(0.3, 0.55), 8, 5)
    di = dt - FL
    if di >= 0:                                                                                        # impatto: lampo, schegge, polvere
        rs = random.Random(int(t0 * 77))
        if di < 0.18: sphere('flash', tgt, 0.6 + 2.5 * di, 10, 6)
        for j in range(40):
            vx, vy, vz = rs.uniform(-1, 1) * 4 + oxb * 3, rs.uniform(-1, 1) * 4 + oyb * 3, rs.uniform(2, 7)
            t = min(di, 1.6); p = (tgt[0] + vx * t, tgt[1] + vy * t, tgt[2] + vz * t - 4.9 * t * t * 1.4)
            gz = zxy(p[0], p[1])
            if p[2] < gz: p = (p[0], p[1], gz + 0.05)
            s_ = rs.uniform(0.06, 0.18); obox('rubble', p[:2], rs.uniform(0, 3), s_, s_, p[2], p[2] + s_ * 1.5)
        for j in range(16):
            u = min(di, 3.5)
            sphere('dust', (tgt[0] + rs.uniform(-1, 1) * (1 + u * 1.5), tgt[1] + rs.uniform(-1, 1) * (1 + u * 1.5), tgt[2] - 0.8 + u * rs.uniform(0.3, 1.1)),
                   0.4 + u * rs.uniform(0.35, 0.7), 8, 5)
for s in SHOTS: shot_fx(s)

# ================= ESERCITI =================
def block(m, cx, cy, ang, L_, Wd, h=0.6, cell=0.55, gap=0.12):
    ca, sa = math.cos(ang), math.sin(ang); nl, nw = max(1, int(L_ / cell)), max(1, int(Wd / cell)); s = cell / 2 - gap / 2
    pts = []
    for i in range(nl):
        for j in range(nw):
            u = (i - (nl - 1) / 2) * cell; v = (j - (nw - 1) / 2) * cell; x, y = cx + u * ca - v * sa, cy + u * sa + v * ca; z = zxy(x, y)
            if z < ZSEA + 0.1: continue
            mm = m + 'E' if (i in (0, nl - 1) or j in (0, nw - 1)) else m
            obox(mm, (x, y), ang, s, s, z - 0.2, z + h); pts.append((x, y, z))
    return tuple(np.array(pts).mean(0)) if pts else None
# accampamento e reggimenti ottomani lungo tutto il fronte (scena 4 in poi), tende davanti al cannone
ARMY = ease((SEC - 19.3) / 1.6)
ASSAULT = ease((SEC - 51.2) / 2.4); FLOOD = ease((SEC - 54.4) / 3.5)
ott = []
if ARMY > 0.01 or SEC < 5.0:
    rs = random.Random(3)
    for k in range(18):
        d = 6 + k * (WP.L - 12) / 17; x, y, a, ox, oy = wall_frame(d)
        dist = lerp(38, 18, ASSAULT * max(0.0, 1 - abs(d - SBR) / 60))
        dist = lerp(dist, 6, ASSAULT * max(0.0, 1 - abs(d - SBR) / 25))
        if SEC < 5.0: dist = 85
        nrow = 2 if abs(d - SBR) > 30 else 4
        for r in range(nrow):
            cx, cy = x + ox * (dist + r * 3.2), y + oy * (dist + r * 3.2)
            if 35.0 < SEC < 38.0 and abs(d - SBR) < 25: continue
            c = block('ott', cx, cy, a, 7.5 * min(1, ARMY + (SEC < 5.0)), 1.8)
            if c and r == 0: ott.append(c)
    for k in range(70):                                                                                # tende dell'accampamento
        u = rs.uniform(-40, 40); v = rs.uniform(70, 110); x = xb + oxb * v - oyb * u * 0 + (-math.sin(ab)) * 0
        cx, cy = xb + oxb * v + math.cos(ab) * u, yb + oyb * v + math.sin(ab) * u; g = zxy(cx, cy)
        if g > ZSEA + 0.1: cyl('tent' if k % 9 else 'tentR', (cx, cy), 0.55, 0.02, g, g + 0.9, 8)
    MEHMED = (xb + oxb * 92, yb + oyb * 92); gM = zxy(*MEHMED)
    cyl('tentR', MEHMED, 1.6, 0.05, gM, gM + 2.2, 12); tube('wood', (MEHMED[0], MEHMED[1], gM), (MEHMED[0], MEHMED[1], gM + 3.6), 0.05, 5)
    poly('banner', [(MEHMED[0], MEHMED[1], gM + 3.6), (MEHMED[0] + 1.0, MEHMED[1], gM + 3.4), (MEHMED[0], MEHMED[1], gM + 3.1)], [[0, 1, 2]])
else: MEHMED = (xb + oxb * 92, yb + oyb * 92)
# difensori: puntini blu sul cammino di ronda del muro interno (scena 4), si radunano alla breccia (scene 10-11)
DEF = ease((SEC - 22.6) / 1.2) * (1 - FLOOD)
defs = []
if DEF > 0.02:
    for k in range(int(140 * DEF)):
        d = 2 + k * (WP.L - 4) / 140
        if FALL > 0: d = lerp(d, SBR + (k % 20 - 10) * 0.5, ASSAULT)
        x, y, a, ox, oy = wall_frame(d); g = zxy(x, y); h = wall_height(d, 1.2 * OEX)
        cx, cy = x - ox * 0.6, y - oy * 0.6; cyl('def', (cx, cy), 0.13, 0.11, g + h, g + h + 0.36, 6); defs.append((cx, cy, g + h + 0.4))
# ondata finale attraverso la breccia: blocchi rossi che entrano in citta'
if FLOOD > 0:
    for k in range(6):
        t = min(1, FLOOD * 1.3 - k * 0.08)
        if t <= 0: continue
        dist = lerp(8, -12 - k * 3, t); cx, cy = xb + oxb * dist + math.cos(ab) * (k - 2.5) * 2.2, yb + oyb * dist + math.sin(ab) * (k - 2.5) * 2.2
        block('ott', cx, cy, ab, 3.5, 2.2)

# ================= IL CORNO D'ORO: catena, flotte, navi sulla collina =================
CH0, CH1 = (41.0168, 28.9806), (41.0228, 28.9752)    # torre di Eugenio -> Galata (Kastellion) [Likely]
CHG = win(37.8, 47.6, 0.5)
def build_chain():
    x0, y0 = xy(*CH0); x1, y1 = xy(*CH1); n = int(math.hypot(x1 - x0, y1 - y0) / 0.9)
    for i in range(n + 1):
        t = i / n; x, y = lerp(x0, x1, t), lerp(y0, y1, t); z = ZSEA + 0.15
        cyl('float', (x, y), 0.45, 0.45, z - 0.1, z + 0.3, 10)
        if i < n:
            xn, yn = lerp(x0, x1, (i + 1) / n), lerp(y0, y1, (i + 1) / n)
            tube('chain' if CHG < 0.05 else 'chainG', (x, y, z + 0.2), (xn, yn, z + 0.2), 0.16, 6)
    for p in (CH0, CH1):
        x, y = xy(*p); g = max(zof(*p), ZSEA); cyl('stone', (x, y), 1.4, 1.3, g - 0.5, g + 4.2, 10)
build_chain()
def galley(m, x, y, ang, z, pitch=0.0, Ls=4.2, sail=True):
    """galea: scafo affusolato, ponte, remi, albero e vela latina"""
    ca, sa = math.cos(ang), math.sin(ang)
    def T(u, v, w): return (x + u * ca - v * sa, y + u * sa + v * ca, z + w + u * math.sin(pitch))
    sec_ = [(-Ls / 2, 0.15, 0.55), (-Ls / 3, 0.42, 0.4), (0, 0.5, 0.35), (Ls / 3, 0.38, 0.38), (Ls / 2 + 0.4, 0.04, 0.6)]
    P = []
    for u, hw, hz in sec_: P += [T(u, -hw, hz), T(u, hw, hz), T(u, hw * 0.6, -0.05), T(u, -hw * 0.6, -0.05)]
    F = []
    for i in range(len(sec_) - 1):
        o = i * 4
        for j in range(4): F.append([o + j, o + (j + 1) % 4, o + 4 + (j + 1) % 4, o + 4 + j])
    F.append([3, 2, 1, 0]); F.append([len(P) - 4, len(P) - 3, len(P) - 2, len(P) - 1])
    poly('hull' if m == 'ott' else 'hullB', P, F)
    poly('deck', [T(-Ls / 2.2, -0.36, 0.38), T(Ls / 2.6, -0.36, 0.37), T(Ls / 2.6, 0.36, 0.37), T(-Ls / 2.2, 0.36, 0.38)], [[0, 1, 2, 3]])
    for k in range(7):                                                                                  # remi
        u = -Ls / 3 + k * Ls / 9.5
        for sgn in (-1, 1): tube('wood', T(u, sgn * 0.45, 0.32), T(u - 0.15, sgn * 1.15, -0.05 if pitch == 0 else 0.1), 0.025, 4)
    tube('wood', T(0.2, 0, 0.35), T(0.2, 0, 2.4), 0.05, 5)
    if sail:
        poly('sailR' if m == 'ott' else 'sailW', [T(-0.9, 0.05, 2.5), T(1.6, 0.05, 1.0), T(-0.6, 0.05, 0.6)], [[0, 1, 2]])
        poly('pennant', [T(0.2, 0, 2.4), T(-0.4, 0, 2.3), T(0.2, 0, 2.15)], [[0, 1, 2]])
# flotta ottomana nel Bosforo, ferma davanti alla catena (scena 7)
SHOWFLEET = 37.5 <= SEC < 51.0 or SEC >= 57.0
if SHOWFLEET:
    fx0, fy0 = xy(41.0262, 28.9905)
    for i in range(16):
        r_, c_ = divmod(i, 4); galley('ott', fx0 + c_ * 2.6 - r_ * 0.8, fy0 + r_ * 3.0, math.radians(215), ZSEA)
    bx0, by0 = xy(41.0245, 28.9650)                                                                       # navi cristiane dietro la catena
    for i in range(6): galley('chr', bx0 + i * 2.2, by0 - i * 1.4, math.radians(30), ZSEA, Ls=5.0)
# le navi trascinate: Bosforo (Tophane) -> su verso Taksim -> giu' nella valle di Kasimpasa -> Corno d'Oro
HAUL_LL = [(41.0268, 28.9862), (41.0300, 28.9860), (41.0340, 28.9858), (41.0372, 28.9842), (41.0378, 28.9800), (41.0362, 28.9745), (41.0340, 28.9705), (41.0322, 28.9672)]
HP = Path(HAUL_LL)
TRACK = ease((SEC - 40.4) / 1.6) * (1 if SEC < 51 or SEC > 57 else 1)
if TRACK > 0.02 and SEC < 59.0:
    ribbon('track', HAUL_LL, 2.2, 0.1, upto=TRACK, onwater=False)
    n = int(HP.L / 0.8)
    for i in range(int(n * TRACK)):
        x, y, a = HP.at(i * 0.8); g = zxy(x, y)
        if g > ZSEA: tube('log', (x - math.sin(a) * 0.9, y + math.cos(a) * 0.9, g + 0.12), (x + math.sin(a) * 0.9, y - math.cos(a) * 0.9, g + 0.12), 0.08, 5)
HAUL = ease((SEC - 42.4) / 5.2)
haul_lead = None
if 42.0 <= SEC and SEC < 59.0:
    NS = 9
    for i in range(NS):
        d = (HAUL * 1.15 - i * 0.075) * HP.L
        if d < -2: continue
        if d > HP.L:                                                                                       # in acqua nel Corno d'Oro
            ex, ey = xy(*HAUL_LL[-1]); k = (d - HP.L); galley('ott', ex - 1.5 - k * 0.3 - (i % 3) * 2.4, ey - 1.0 - (i // 3) * 2.2, math.radians(215), ZSEA); continue
        x, y, a = HP.at(max(d, 0)); g = zxy(x, y)
        x2, y2, _ = HP.at(min(HP.L, max(d, 0) + 1.0)); g2 = zxy(x2, y2); pitch = math.atan2(g2 - g, 1.0)
        galley('ott', x, y, a, max(g, ZSEA) + 0.25, pitch, Ls=5.5)
        if haul_lead is None: haul_lead = (x, y, g + 2.5)
# dopo il 22 aprile: galee ottomane dentro il Corno d'Oro
if 47.5 <= SEC < 59.0:
    ex, ey = xy(41.0300, 28.9640)
    for i in range(10): galley('ott', ex - (i % 5) * 2.4, ey - (i // 5) * 2.6 - 1.5, math.radians(215), ZSEA)

# ================= FRECCE DI ATTACCO (scena 9) e territorio caduto (finale) =================
ARR = win(47.7, 51.0, 0.4)
if ARR > 0.02:
    u = ease((SEC - 47.7) / 1.4)
    for k in range(7):
        d = 5 + k * (WP.L - 10) / 6; x, y, a, ox, oy = wall_frame(d); p0 = ll(x + ox * 45, y + oy * 45); p1 = ll(x + ox * 6, y + oy * 6)
        ribbon('arrow', [p0, p1], 1.6, 2.5, upto=u, arrow=True)
    ribbon('arrow', [(41.0310, 28.9600), (41.0262, 28.9560)], 1.6, 1.0, upto=u, arrow=True)                  # dal Corno d'Oro
    ribbon('arrow', [(41.0130, 28.9960), (41.0175, 28.9862)], 1.6, 1.0, upto=u, arrow=True)                  # dal Bosforo
    ribbon('arrow', [(40.9900, 28.9500), (40.9985, 28.9500)], 1.6, 1.0, upto=u, arrow=True)                  # dal Marmara
# la citta' cade: zona rossa che si allarga dalla breccia dentro le mura
if FLOOD > 0.02 and SEC < 63:
    R_ = 8 + 220 * FLOOD
    for i in range(48):
        a0, a1 = 2 * math.pi * i / 48, 2 * math.pi * (i + 1) / 48
        pts = []
        for rr_ in np.linspace(0, R_, 12):
            pass
    # disco a spicchi drappeggiato, solo sul lato citta' (est del muro)
    for i in range(64):
        for j in range(18):
            a0 = 2 * math.pi * i / 64; a1 = 2 * math.pi * (i + 1) / 64; r0_, r1_ = R_ * j / 18, R_ * (j + 1) / 18
            cs = [(xb + r * math.cos(t), yb + r * math.sin(t)) for r, t in ((r0_, a0), (r1_, a0), (r1_, a1), (r0_, a1))]
            mid = (sum(c[0] for c in cs) / 4, sum(c[1] for c in cs) / 4)
            if (mid[0] - xb) * oxb + (mid[1] - yb) * oyb > 2: continue                                      # niente fuori dalle mura
            zs = [zxy(*c) for c in cs]
            if min(zs) < ZSEA: continue
            poly('fallen', [(c[0], c[1], z + 0.8) for c, z in zip(cs, zs)], [[0, 1, 2, 3]])

# ================= FUOCHI NOTTURNI (torce sulle mura, fuochi del campo) =================
FIRE = NIGHT
if FIRE > 0.05:
    rs = random.Random(int(SEC * 12))
    for k in range(40):
        d = 3 + k * (WP.L - 6) / 40; x, y, a, ox, oy = wall_frame(d); g = zxy(x, y) + wall_height(d, 1.2 * OEX) + 0.3
        sphere('torch', (x - ox * 0.6, y - oy * 0.6, g + 0.1 * rs.random()), 0.16, 6, 4)
    if ARMY > 0:
        for k in range(60):
            u = rs.uniform(-60, 60); v = rs.uniform(25, 110); cx, cy = xb + oxb * v + math.cos(ab) * u, yb + oyb * v + math.sin(ab) * u; g = zxy(cx, cy)
            if g > ZSEA: sphere('campfire', (cx, cy, g + 0.2), 0.22 + 0.06 * rs.random(), 6, 4)
    if FALL > 0:
        for k in range(30):
            cx, cy = xb + rs.uniform(-30, 30) - oxb * rs.uniform(5, 60) * FLOOD, yb + rs.uniform(-30, 30) - oyb * rs.uniform(5, 60) * FLOOD; g = zxy(cx, cy)
            if g > ZSEA:
                sphere('flame', (cx, cy, g + 0.25), 0.3 + 0.15 * rs.random(), 7, 4)
                if k % 3 == 0: sphere('smoke', (cx, cy, g + 2.5 + 2 * rs.random()), 1.6 + rs.random(), 8, 5)

# ================= MATERIALI =================
COL = dict(stone=(0.62, 0.55, 0.45), stoneO=(0.55, 0.49, 0.40), roof=(0.40, 0.18, 0.12), moat=(0.02, 0.05, 0.08), rubble=(0.50, 0.44, 0.36),
           wood=(0.32, 0.20, 0.10), log=(0.40, 0.26, 0.12), track=(0.30, 0.22, 0.12), bronze=(0.55, 0.38, 0.14), bronzeD=(0.35, 0.22, 0.08),
           wicker=(0.45, 0.35, 0.18), stoneball=(0.6, 0.6, 0.58), flash=(1.0, 0.75, 0.35), ball=(1.0, 0.55, 0.2), trail=(1.0, 0.45, 0.12),
           smoke=(0.55, 0.53, 0.50), dust=(0.58, 0.52, 0.44), ott=(0.55, 0.05, 0.03), ottE=(0.85, 0.15, 0.08), tent=(0.85, 0.80, 0.70),
           tentR=(0.80, 0.10, 0.06), banner=(0.9, 0.1, 0.05), defn=(0.1, 0.3, 1.0), hull=(0.30, 0.16, 0.08), hullB=(0.22, 0.20, 0.30),
           deck=(0.45, 0.33, 0.18), sailR=(0.85, 0.15, 0.10), sailW=(0.90, 0.88, 0.80), pennant=(0.9, 0.1, 0.05), float=(0.35, 0.22, 0.10),
           chain=(0.15, 0.15, 0.16), chainG=(1.0, 0.75, 0.3), arrow=(1.0, 0.12, 0.08), fallen=(0.85, 0.08, 0.04), torch=(1.0, 0.6, 0.2),
           campfire=(1.0, 0.45, 0.12), flame=(1.0, 0.35, 0.05))
COL['def'] = (0.15, 0.40, 1.0)
EM = dict(flash=14.0, ball=12.0, trail=8.0, ott=0.25, ottE=0.6, defn=1.2, chainG=6.0 * CHG, arrow=3.0, fallen=0.15, torch=10.0, campfire=6.0, flame=9.0,
          tentR=0.15, sailR=0.25, banner=0.6)
EM['def'] = 2.0
ALPHA = dict(smoke=0.55, dust=0.65, fallen=0.18, track=0.95)
for m, (Vv, Ff) in GEO.items():
    mm = bpy.data.meshes.new(m); mm.from_pydata(Vv, [], Ff); mm.update()
    mt_ = bpy.data.materials.new(m); mt_.use_nodes = True; bb = mt_.node_tree.nodes['Principled BSDF']; c = COL.get(m, (0.5, 0.5, 0.5)) + (1,)
    bb.inputs['Base Color'].default_value = c; bb.inputs['Roughness'].default_value = 0.35 if m.startswith('bronze') else 0.8
    if m.startswith('bronze'): bb.inputs['Metallic'].default_value = 0.85
    if m in EM: bb.inputs['Emission Color'].default_value = c; bb.inputs['Emission Strength'].default_value = EM[m]
    if m in ALPHA: bb.inputs['Alpha'].default_value = ALPHA[m]
    if m in ('smoke', 'dust'):
        n = mt_.node_tree; out = n.nodes['Material Output']; n.links.remove(out.inputs['Surface'].links[0])
        vol = n.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value = c; vol.inputs['Density'].default_value = 0.9 if m == 'smoke' else 1.2
        n.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    if m in ('stone', 'stoneO'):                                                                          # pietra a corsi di mattoni (fasce rosse)
        n = mt_.node_tree; gg = n.nodes.new('ShaderNodeNewGeometry'); sz = n.nodes.new('ShaderNodeSeparateXYZ'); n.links.new(gg.outputs['Position'], sz.inputs['Vector'])
        mlt = n.nodes.new('ShaderNodeMath'); mlt.operation = 'MULTIPLY'; mlt.inputs[1].default_value = 2.2; n.links.new(sz.outputs['Z'], mlt.inputs[0])
        frc = n.nodes.new('ShaderNodeMath'); frc.operation = 'FRACT'; n.links.new(mlt.outputs[0], frc.inputs[0])
        lt = n.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.22; n.links.new(frc.outputs[0], lt.inputs[0])
        mx = n.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs['A'].default_value = c; mx.inputs['B'].default_value = (0.45, 0.20, 0.13, 1)
        n.links.new(lt.outputs[0], mx.inputs['Factor']); n.links.new(mx.outputs['Result'], bb.inputs['Base Color'])
    mm.materials.append(mt_); o = bpy.data.objects.new(m, mm); sc.collection.objects.link(o)

# ================= CIELO, SOLE, LUCI =================
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True; wn = world.node_tree; bg = wn.nodes['Background']
sky = wn.nodes.new('ShaderNodeTexSky')
try: sky.sky_type = 'MULTIPLE_SCATTERING'
except Exception: pass
SUN_EL = lerp(14, 4, DAWN)                                       # ora dorata; all'alba sole quasi all'orizzonte
try: sky.sun_elevation = math.radians(SUN_EL); sky.sun_rotation = math.radians(lerp(235, 100, DAWN)); sky.sun_disc = False; sky.air_density = 1.0; sky.dust_density = 1.0
except Exception: pass
nightc = wn.nodes.new('ShaderNodeRGB'); nightc.outputs[0].default_value = (0.03, 0.05, 0.12, 1)
mixw = wn.nodes.new('ShaderNodeMix'); mixw.data_type = 'RGBA'; mixw.inputs['Factor'].default_value = NIGHT
wn.links.new(sky.outputs['Color'], mixw.inputs['A']); wn.links.new(nightc.outputs[0], mixw.inputs['B']); wn.links.new(mixw.outputs['Result'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = lerp(0.22, 1.0, NIGHT)
sun = bpy.data.lights.new('sun', 'SUN'); sun.angle = math.radians(1.2)
sun.energy = lerp(5.0, 1.3, NIGHT)
sun.color = tuple(lerp(c1, c2, NIGHT) for c1, c2 in zip((1.0, 0.82, 0.62), (0.55, 0.68, 1.0)))
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(90 - lerp(SUN_EL, 35, NIGHT)), 0, math.radians(lerp(235, 100, DAWN) + 90))
if FIRE > 0.05 and FALL > 0:                                                                              # bagliore dell'incendio
    pl = bpy.data.lights.new('glow', 'POINT'); pl.energy = 2.5e5 * FALL * NIGHT; pl.color = (1.0, 0.45, 0.15); pl.shadow_soft_size = 30
    po = bpy.data.objects.new('glow', pl); sc.collection.objects.link(po); po.location = (xb - oxb * 25, yb - oyb * 25, zxy(xb, yb) + 40)
if STOCK > 0.05 and NIGHT > 0.3:                                                                          # fuochi dei lavori notturni nella breccia
    for k_ in range(3):
        pl = bpy.data.lights.new('work', 'POINT'); pl.energy = 9000 * STOCK; pl.color = (1.0, 0.55, 0.25); pl.shadow_soft_size = 2
        po = bpy.data.objects.new('work', pl); sc.collection.objects.link(po); xw, yw, _, _, _ = wall_frame(SBR - 4 + 4 * k_); po.location = (xw - oxb * 3, yw - oyb * 3, zxy(xw, yw) + 3)
        sphere('campfire', (xw - oxb * 3, yw - oyb * 3, zxy(xw, yw) + 0.3), 0.35, 7, 4)
for s in SHOTS:                                                                                           # luce del lampo
    dt = SEC - s
    if 0 <= dt < 0.25:
        pl = bpy.data.lights.new('mflash', 'POINT'); pl.energy = 4.0e5 * (1 - dt / 0.25); pl.color = (1.0, 0.7, 0.35)
        po = bpy.data.objects.new('mflash', pl); sc.collection.objects.link(po); po.location = (MUZ[0], MUZ[1], MUZ[2] + 2)

# ================= CAMERA (chiavi in secondi, Catmull-Rom) =================
def P_(dx, dy, dz): return (xb + dx, yb + dy, zxy(xb, yb) + dz)                     # comodita': coordinate relative alla breccia
def A_(dist_out, along, dz):
    """punto a 'dist_out' unita' fuori dalle mura (positivo = ovest) e 'along' lungo il muro (positivo = nord)"""
    px, py = xb + oxb * dist_out + math.cos(ab) * along, yb + oyb * dist_out + math.sin(ab) * along
    return (px, py, max(zxy(px, py), ZSEA) + dz)
hx, hy = xy(41.0340, 28.9790); hz = zof(41.0340, 28.9790)
chx, chy = xy(41.0198, 28.9779)
KEYS = [
    (0.0,  A_(14, -40, 9),  A_(0, -10, 3), 24),           # 1: radente lungo le mura all'alba
    (3.3,  A_(18, -14, 8),  A_(2, 2, 3), 24),
    (4.1,  A_(63, 7, 3.5),  A_(55, 0, 1.2), 24),          # il cannone, basso e vicino
    (5.25, A_(62, 6, 3.8),  A_(53, 0, 1.4), 26),          # sparo
    (6.1,  A_(30, 7, 6),    A_(1, 0, 2.5), 24),           # insegue la palla fino al muro
    (7.6,  A_(22, 5, 9),    A_(0, 0, 2), 24),
    (11.0, A_(150, -60, 260), A_(-140, 30, 0), 26),       # 2: si alza, la penisola e l'acqua su tre lati
    (13.6, A_(60, -60, 110), A_(0, -10, 0), 26),          # 3: scende sulle mura, i tre strati
    (18.5, A_(14, 20, 14),  A_(0, 0, 2), 24),
    (22.5, A_(120, -10, 120), A_(0, 0, 0), 24),           # 4: gli eserciti
    (26.3, A_(70, 30, 60),  A_(10, 0, 0), 26),
    (27.8, A_(63, 6, 3.6),  A_(55, 0, 1.2), 24),            # 5: il cannone da vicino
    (29.6, A_(40, 18, 14),  A_(0, 0, 3), 24),
    (32.5, A_(66, -9, 4.0), A_(55, 0, 1.2), 26),
    (34.6, A_(38, -18, 13), A_(0, 0, 2), 24),
    (36.8, A_(-26, 18, 30), A_(2, 0, 1.0), 22),           # 6: notte, dall'interno verso la palizzata
    (39.4, (chx - 26, chy - 14, ZSEA + 9), (chx + 18, chy + 22, ZSEA + 1), 22),   # 7: la catena, radente sull'acqua, flotta dietro
    (43.5, (hx + 30, hy - 45, hz + 55), (hx, hy, hz), 24),# 8: le navi sulla collina
    (47.4, (hx - 25, hy - 40, hz + 50), (hx - 30, hy - 5, hz), 24),
    (50.7, A_(-60, 30, 330), A_(-90, 10, 0), 24),         # 9: attacco da ogni lato
    (53.2, A_(30, -45, 45), A_(0, 0, 2), 24),             # 10: la breccia cade, notte
    (57.8, A_(-35, 25, 38), A_(0, 0, 2), 26),             # 11: Costantino nella breccia
    (59.6, A_(40, -30, 130), A_(-40, 10, 0), 24),
    (64.8, A_(160, -80, 300), A_(-120, 20, 0), 24),       # 12: finale largo, la citta' rossa
]
def cr(p0, p1, p2, p3, t): return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
def cam_at(t):
    ks = [(k[0], mu.Vector(k[1]), mu.Vector(k[2]), k[3]) for k in KEYS]
    for i in range(len(ks) - 1):
        if t <= ks[i + 1][0] or i == len(ks) - 2: break
    f = max(0.0, min(1.0, (t - ks[i][0]) / (ks[i + 1][0] - ks[i][0]))); f = f * f * (3 - 2 * f) * 0.5 + f * 0.5
    g = lambda j: ks[max(0, min(len(ks) - 1, j))]
    pos = cr(g(i - 1)[1], g(i)[1], g(i + 1)[1], g(i + 2)[1], f); tgt = cr(g(i - 1)[2], g(i)[2], g(i + 1)[2], g(i + 2)[2], f)
    return pos, tgt, g(i)[3] + (g(i + 1)[3] - g(i)[3]) * f
cam_pos, tgt, lens = cam_at(SEC)
if haul_lead is not None:
    wgt = win(42.4, 47.6, 0.9); x_, y_, a_ = HP.at(max(0.0, min(HP.L, HAUL * 1.15 * HP.L)))
    lead = mu.Vector((x_, y_, zxy(x_, y_) + 1.0)); side = mu.Vector((math.cos(a_ - 2.2), math.sin(a_ - 2.2), 0))
    cam_pos = cam_pos.lerp(lead + side * 16 + mu.Vector((0, 0, 9)), wgt); tgt = tgt.lerp(lead + mu.Vector((math.cos(a_), math.sin(a_), 0)) * 4, wgt)
gz = zxy(cam_pos.x, cam_pos.y)
if cam_pos.z < gz + 4: cam_pos.z = gz + 4                                          # mai sotto il terreno
for s in SHOTS:                                                                    # scossa di camera all'impatto
    dt = SEC - s - 0.8
    if 0 <= dt < 0.5: cam_pos.z += 0.25 * math.sin(dt * 90) * (1 - dt / 0.5); cam_pos.x += 0.2 * math.cos(dt * 70) * (1 - dt / 0.5)
cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_end = 20000; cd.clip_start = 0.5
co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co
co.location = cam_pos; co.rotation_euler = (tgt - cam_pos).to_track_quat('-Z', 'Y').to_euler()
# foschia di distanza (nebbia volumetrica economica: niente, uso il colore del mondo + mist pass non necessario)

# ================= RENDER =================
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
if os.environ.get('THREADS'): sc.render.threads_mode = 'FIXED'; sc.render.threads = int(os.environ['THREADS'])
DEV = os.environ.get('DEVICE', 'CPU')
if DEV in ('OPTIX', 'CUDA'):
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = DEV; pr.get_devices()
    for d_ in pr.devices: d_.use = d_.type == DEV
    if not any(d_.use and d_.type == DEV for d_ in pr.devices): print('[cpl] ERRORE: nessuna GPU ' + DEV, flush=True); sys.exit(3)
    sc.cycles.device = 'GPU'
sc.cycles.samples = SPP; sc.cycles.use_denoising = True
if DEV == 'OPTIX': sc.cycles.denoiser = 'OPTIX'
sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 8; sc.cycles.volume_bounces = 0; sc.cycles.volume_step_rate = 4.0
sc.render.resolution_x = W; sc.render.resolution_y = H
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)

# ================= POSIZIONI A SCHERMO PER L'INFOGRAFICA =================
sc.view_layers[0].update()
def proj(p): v = world_to_camera_view(sc, co, mu.Vector(p)); return (v.x, 1 - v.y, v.z)
pos = {}
x_, y_, a_, ox_, oy_ = wall_frame(SBR - 14); g_ = zxy(x_, y_)
pos['MOAT'] = proj((x_ + ox_ * 4.2, y_ + oy_ * 4.2, g_)); pos['OUTER'] = proj((x_ + ox_ * 2.0, y_ + oy_ * 2.0, g_ + 1.8)); pos['INNER'] = proj((x_ - ox_ * 0.6, y_ - oy_ * 0.6, g_ + 2.4))
pos['BREACH'] = proj((xb, yb, zxy(xb, yb) + 2.5)); pos['CANNON'] = proj((CAN[0], CAN[1], gc + 1.5))
pos['MEHMED'] = proj((MEHMED[0], MEHMED[1], zxy(*MEHMED) + 3.0)); pos['CHAIN'] = proj((chx, chy, ZSEA + 1))
for k_, (la, lo) in {'GOLDEN HORN': (41.0270, 28.9600), 'BOSPHORUS': (41.0280, 29.0080), 'MARMARA': (40.9940, 28.9600), 'GALATA': (41.0350, 28.9790),
                     'CITY': (41.0120, 28.9550)}.items():
    x, y = xy(la, lo); pos[k_] = proj((x, y, max(zof(la, lo), ZSEA) + 1))
if haul_lead: pos['SHIPS'] = proj(haul_lead)
if ott: pos['OTTOMANS'] = proj(ott[len(ott) // 2])
json.dump(pos, open(OUT + '.json', 'w'))
print('OK', OUT, 'torri', NTOW)
