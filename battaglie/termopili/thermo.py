# Termopili 480 a.C. su terreno vero (Copernicus GLO-30 + Sentinel-2 cloudless 2016, EOX, CC BY 4.0).
# v4 (1 nov): Short completo legato ai secondi della voce (tempi_voce_termopili.md). Stile scuro, camera sempre alta.
# Uso: /tmp/bl/bin/python thermo.py <secondo> <out.png> [w h spp]     (24 fps: secondo = fotogramma / 24)
import sys, math, json, os
import numpy as np, tifffile, bpy, mathutils as mu
from bpy_extras.object_utils import world_to_camera_view

SEC = float(sys.argv[1]); OUT = sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 540; H = int(sys.argv[4]) if len(sys.argv) > 4 else 960
SPP = int(sys.argv[5]) if len(sys.argv) > 5 else 16
D = os.environ.get('DATA', '/home/claude/thermo/termopili/')
LON0, LAT0 = 22.5361, 38.7966                      # porta di mezzo (muro dei Focesi)
KX = 111320 * math.cos(math.radians(LAT0)); KY = 110950
SC, EX = 10.0, 1.6                                 # 1 unita' = 10 m; rilievo esagerato 1,6x
LONA, LONB, LATA, LATB = 22.40, 22.68, 38.70, 38.88
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def win(a, b, ramp=0.4): return ease((SEC - a) / ramp) * (1 - ease((SEC - b) / ramp))   # 0->1->0 tra a e b
TODAY = ease((SEC - 59.2) / 1.8)                   # scena 10: il mare antico si ritira fino alla costa di oggi
SEA = 10.0 * (1 - TODAY) + 0.5 * TODAY             # mare "antico" [Guessing]: allaga la piana sotto i 10 m
ZSEA = SEA / SC * EX

def xy(lat, lon): return ((lon - LON0) * KX / SC, (lat - LAT0) * KY / SC)
def ll(x, y): return (LAT0 + y * SC / KY, LON0 + x * SC / KX)
dem = tifffile.TiffFile(D + 'Copernicus_DSM_COG_10_N38_00_E022_00_DEM.tif').pages[0].asarray()
def elev(lat, lon):
    r = (39 - lat) * 3600; c = (lon - 22) * 3600
    r0, c0 = int(r), int(c); fr, fc = r - r0, c - c0
    return (dem[r0, c0] * (1 - fr) * (1 - fc) + dem[r0 + 1, c0] * fr * (1 - fc) + dem[r0, c0 + 1] * (1 - fr) * fc + dem[r0 + 1, c0 + 1] * fr * fc)
def zof(lat, lon): return max(elev(lat, lon), 0) / SC * EX
def zxy(x, y): return zof(*ll(x, y))
Z14 = 2 ** 14; TX0, TY0, TX1, TY1 = 9209, 6265, 9227, 6282
def uv(lat, lon):
    x = (lon + 180) / 360 * Z14; y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * Z14
    return ((x - TX0) / (TX1 - TX0), 1 - (y - TY0) / (TY1 - TY0))

bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
NIGHT = ease((SEC - 36.9) / 1.6) * (1 - ease((SEC - 47.4) / 2.0))   # notte del 2 giorno (scene 6-7), poi alba

# ---------------- terreno (rilievo con ombre radenti, satellite come tinta, curve di livello leggere)
NX, NY = 760, 540
V, F, UV = [], [], []
lats = np.linspace(LATA, LATB, NY); lons = np.linspace(LONA, LONB, NX)
for la in lats:
    for lo in lons:
        x, y = xy(la, lo); V.append((x, y, zof(la, lo))); UV.append(uv(la, lo))
for j in range(NY - 1):
    for i in range(NX - 1):
        a = j * NX + i; F.append((a, a + 1, a + NX + 1, a + NX))
me = bpy.data.meshes.new('terrain'); me.from_pydata(V, [], F); me.update()
uvl = me.uv_layers.new()
for p in me.polygons:
    p.use_smooth = True
    for li in p.loop_indices: uvl.data[li].uv = UV[me.loops[li].vertex_index]
mt = bpy.data.materials.new('terrain'); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes['Principled BSDF']
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(D + 'satellite_z14.jpg'); tx.interpolation = 'Cubic'
hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 1.15; hsv.inputs['Value'].default_value = 0.62
nt.links.new(tx.outputs['Color'], hsv.inputs['Color'])
geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0; mr.inputs['From Max'].default_value = 170
nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
ramp = nt.nodes.new('ShaderNodeValToRGB'); E = ramp.color_ramp.elements
E[0].position = 0.0; E[0].color = (0.10, 0.11, 0.07, 1); E[1].position = 1.0; E[1].color = (0.32, 0.31, 0.29, 1)
e2 = E.new(0.35); e2.color = (0.13, 0.15, 0.12, 1)
nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MIX'; mix.inputs['Factor'].default_value = 0.85
nt.links.new(ramp.outputs['Color'], mix.inputs['A']); nt.links.new(hsv.outputs['Color'], mix.inputs['B'])
mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = 1.0 / (100.0 / SC * EX)
nt.links.new(sep.outputs['Z'], mth.inputs[0])
frc = nt.nodes.new('ShaderNodeMath'); frc.operation = 'FRACT'; nt.links.new(mth.outputs[0], frc.inputs[0])
pp = nt.nodes.new('ShaderNodeMath'); pp.operation = 'PINGPONG'; pp.inputs[1].default_value = 0.5; nt.links.new(frc.outputs[0], pp.inputs[0])
ln = nt.nodes.new('ShaderNodeMath'); ln.operation = 'LESS_THAN'; ln.inputs[1].default_value = 0.012; nt.links.new(pp.outputs[0], ln.inputs[0])
hm = nt.nodes.new('ShaderNodeMath'); hm.operation = 'GREATER_THAN'; hm.inputs[1].default_value = 3.0; nt.links.new(sep.outputs['Z'], hm.inputs[0])
lm = nt.nodes.new('ShaderNodeMath'); lm.operation = 'MULTIPLY'; nt.links.new(ln.outputs[0], lm.inputs[0]); nt.links.new(hm.outputs[0], lm.inputs[1])
lm2 = nt.nodes.new('ShaderNodeMath'); lm2.operation = 'MULTIPLY'; lm2.inputs[1].default_value = 0.10; nt.links.new(lm.outputs[0], lm2.inputs[0])
mix2 = nt.nodes.new('ShaderNodeMix'); mix2.data_type = 'RGBA'; mix2.inputs['B'].default_value = (0.85, 0.80, 0.65, 1)
nt.links.new(lm2.outputs[0], mix2.inputs['Factor']); nt.links.new(mix.outputs['Result'], mix2.inputs['A'])
nt.links.new(mix2.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.95
me.materials.append(mt); ter = bpy.data.objects.new('terrain', me); sc.collection.objects.link(ter)

# ---------------- mare antico
def plane(name, z, col, rough=0.25, size=4000):
    m = bpy.data.meshes.new(name); m.from_pydata([(-size, -size, z), (size, -size, z), (size, size, z), (-size, size, z)], [], [(0, 1, 2, 3)])
    mm = bpy.data.materials.new(name); mm.use_nodes = True; bb = mm.node_tree.nodes['Principled BSDF']
    bb.inputs['Base Color'].default_value = col; bb.inputs['Roughness'].default_value = rough
    m.materials.append(mm); o = bpy.data.objects.new(name, m); sc.collection.objects.link(o); return o
plane('sea', ZSEA, (0.006, 0.018, 0.035, 1))

# ---------------- geometria accumulata per materiale
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

def block(m, cx, cy, ang, L, Wd, h=3.0, cell=1.25, gap=0.22, edge=True):
    """Esercito come blocco compatto: griglia fitta di colonne che seguono il terreno.
    ang = direzione di marcia; L lungo la marcia, Wd di fronte.
    Ogni fila si adatta alla striscia di terra: se il mare la taglia, la fila si stringe e scivola verso terra
    (il blocco resta pieno e sembra comprimersi nel passo, invece di bucarsi)."""
    ca, sa = math.cos(ang), math.sin(ang)
    nl = max(1, int(L / cell)); s = cell / 2 - gap / 2
    pts = []; rows = []
    for i in range(nl):
        u = (i - (nl - 1) / 2) * cell
        # campiona di traverso su 2x la larghezza, tieni il tratto di terra contiguo piu' vicino al centro
        vs = [k * 0.5 for k in range(int(-Wd * 2), int(Wd * 2) + 1)]
        land = [zxy(cx + u * ca - v * sa, cy + u * sa + v * ca) > ZSEA + 0.4 for v in vs]
        if not any(land): continue
        c0 = min((abs(v), k) for k, v in enumerate(vs) if land[k])[1]
        lo_ = hi_ = c0
        while lo_ > 0 and land[lo_ - 1]: lo_ -= 1
        while hi_ < len(vs) - 1 and land[hi_ + 1]: hi_ += 1
        a_, b_ = vs[lo_] + 0.8, vs[hi_] - 0.8
        w_ = min(Wd, b_ - a_)
        if w_ < cell: continue
        mid = max(a_ + w_ / 2, min(b_ - w_ / 2, 0.0))
        rows.append((i, u, mid, w_))
    for r, (i, u, mid, w_) in enumerate(rows):
        nw = max(1, int(w_ / cell))
        for j in range(nw):
            v = mid + (j - (nw - 1) / 2) * cell
            x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
            z = zxy(x, y)
            mm = m + 'E' if edge and (r in (0, len(rows) - 1) or j in (0, nw - 1)) else m
            obox(mm, (x, y), ang, s, s, z - 0.5, z + h); pts.append((x, y, z))
    if not pts: return None
    P = np.array(pts); return tuple(P.mean(0))

def glow(m, cx, cy, ang, a_, b_, n=28, lift=0.3):
    ca, sa = math.cos(ang), math.sin(ang); ring = []
    for i in range(n):
        t = 2 * math.pi * i / n; dx, dy = a_ * math.cos(t), b_ * math.sin(t)
        x, y = cx + dx * ca - dy * sa, cy + dx * sa + dy * ca
        ring.append((x, y, max(zxy(x, y), ZSEA) + lift))
    poly(m, [(cx, cy, max(zxy(cx, cy), ZSEA) + lift)] + ring, [[0, 1 + i, 1 + (i + 1) % n] for i in range(n)])

def ribbon(m, pts_ll, w=1.2, lift=0.8, upto=1.0, arrow=True, dash=0.0):
    """freccia che segue il terreno, disegnata fino alla frazione 'upto'; dash>0 = tratteggiata"""
    P = []
    for k in range(len(pts_ll) - 1):
        (la0, lo0), (la1, lo1) = pts_ll[k], pts_ll[k + 1]
        for s in range(24):
            t = s / 24; la = la0 + (la1 - la0) * t; lo = lo0 + (lo1 - lo0) * t
            x, y = xy(la, lo); P.append((x, y, max(zof(la, lo), ZSEA) + lift))
    la, lo = pts_ll[-1]; x, y = xy(la, lo); P.append((x, y, max(zof(la, lo), ZSEA) + lift))
    Lc = [0.0]
    for k in range(1, len(P)): Lc.append(Lc[-1] + math.dist(P[k][:2], P[k - 1][:2]))
    lim = Lc[-1] * upto
    Q = [(p, l) for p, l in zip(P, Lc) if l <= lim]
    if len(Q) < 3: return
    for k in range(len(Q) - 1):
        (a_, la_), (b_, _) = Q[k], Q[k + 1]
        if dash and int(la_ / dash) % 2: continue
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]; l_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / l_ * w / 2, dx / l_ * w / 2
        poly(m, [(a_[0] + nx, a_[1] + ny, a_[2]), (b_[0] + nx, b_[1] + ny, b_[2]), (b_[0] - nx, b_[1] - ny, b_[2]), (a_[0] - nx, a_[1] - ny, a_[2])], [[0, 1, 2, 3]])
    if arrow:
        a_, b_ = Q[-2][0], Q[-1][0]; dx, dy = b_[0] - a_[0], b_[1] - a_[1]; l_ = math.hypot(dx, dy) or 1; ux, uy = dx / l_, dy / l_
        tip = (b_[0] + ux * 5 * w, b_[1] + uy * 5 * w, b_[2])
        poly(m, [(b_[0] - uy * w * 2.0, b_[1] + ux * w * 2.0, b_[2]), tip, (b_[0] + uy * w * 2.0, b_[1] - ux * w * 2.0, b_[2])], [[0, 1, 2]])

class Path:
    """polilinea (lat, lon) percorribile per lunghezza d'arco (unita')"""
    def __init__(s, pts):
        s.P = [mu.Vector(xy(*p)) for p in pts]; s.C = [0.0]
        for k in range(1, len(s.P)): s.C.append(s.C[-1] + (s.P[k] - s.P[k - 1]).length)
        s.L = s.C[-1]
    def at(s, d):
        d = max(0.0, min(s.L, d))
        for k in range(1, len(s.P)):
            if d <= s.C[k] or k == len(s.P) - 1:
                f = (d - s.C[k - 1]) / max(1e-6, s.C[k] - s.C[k - 1]); v = s.P[k] - s.P[k - 1]
                p = s.P[k - 1] + v * f; return p.x, p.y, math.atan2(v.y, v.x)

# ---------------- storia (secondi = tempi della voce)
GREEK = (38.7968, 22.5368)
KOLONOS = (38.7962, 22.5405)                        # poggio dell'ultima resistenza: posizione indicativa [Guessing]
ARMY = 1 - ease((SEC - 59.2) / 0.8)                 # scena 10: eserciti e territori spariscono per il "TODAY"

# muro dei Focesi; si accende quando Leonida lo ricostruisce (scena 4)
WALLGLOW = win(22.3, 26.6, 0.6)
for k in range(14):
    la = 38.7950 + 0.00032 * k; x, y = xy(la, 22.5392)
    if zof(la, 22.5392) > ZSEA + 0.2 and ARMY > 0: obox('wall', (x, y), math.radians(92), 0.5, 1.6, zof(la, 22.5392) - 0.5, zof(la, 22.5392) + 2.2 + 1.5 * WALLGLOW)

# Greci: blocco al muro; scena 8 la maggior parte se ne va verso est, il resto ripiega sul poggio (scene 8-9)
leave = ease((SEC - 48.0) / 3.0); tohill = ease((SEC - 50.5) / 3.5)
gx, gy = xy(*GREEK); kx, ky = xy(*KOLONOS)
gc = None
if ARMY > 0:
    cx_, cy_ = gx + (kx - gx) * tohill, gy + (ky - gy) * tohill
    gc = block('greek', cx_, cy_, math.radians(180), 8.0 - 2.0 * tohill, 34.0 - 22.0 * leave, h=3.4)
    if 0 < leave < 1:                               # chi parte: blocco che si allontana verso est lungo la strada
        ex, ey = xy(38.7962, 22.5405 + 0.025 * leave)
        block('greekL', ex, ey, 0.0, 16.0 * (1 - 0.6 * leave), 8.0, h=2.2)

# Persiani: colonna lungo la strada costiera da Trachis; la testa segue le fasi della battaglia
ROAD = Path([(38.8000, 22.462), (38.8030, 22.488), (38.8012, 22.505), (38.7990, 22.520), (38.7972, 22.5345), (38.7962, 22.545), (38.7958, 22.562)])
CLASH = ROAD.C[4] - 3.5
def lerp(a, b, k): return a + (b - a) * k
HK = [(0.0, 60), (5.7, 95), (21.5, CLASH - 40), (27.0, CLASH - 40), (29.2, CLASH), (31.0, CLASH - 12), (32.0, CLASH - 34), (34.8, CLASH - 34), (36.0, CLASH),
      (37.2, CLASH - 12), (51.0, CLASH - 12), (55.0, CLASH), (57.1, CLASH), (59.2, CLASH + 70)]
for (t0, h0), (t1, h1) in zip(HK, HK[1:]):
    if SEC <= t1: head = lerp(h0, h1, ease((SEC - t0) / (t1 - t0))); break
else: head = HK[-1][1]
bunch = ease((SEC - 22.0) / 6.0)                    # davanti al passo la colonna si accorcia (ingorgo)
pc = []
if ARMY > 0:
    for i in range(5):
        d = head - 18 - i * (46 - 26 * bunch)
        if d < 0: continue
        x, y, a = ROAD.at(d)
        c = block('pers', x, y, a, 30 - 6 * bunch * (i == 0), 11.0 + 2 * bunch)
        if c: pc.append(c)
ribbon('red', [(38.8000, 22.462), (38.8030, 22.488), (38.8012, 22.505), (38.7990, 22.520), (38.7975, 22.531)], 2.2, 1.6, upto=ease((SEC - 0.5) / 20.0)) if ARMY > 0.5 and SEC < 37 else None

# scena 5: gli Immortali attaccano di giorno dalla testa della colonna e vengono respinti
IMMDAY = win(31.6, 35.0, 0.6)
imd = None
if IMMDAY > 0.02:
    dI = lerp(CLASH - 22, CLASH - 1, ease((SEC - 31.8) / 1.6)) - 10 * ease((SEC - 33.6) / 1.2)
    x, y, a = ROAD.at(dI); imd = block('imm', x, y, a, 14.0 * IMMDAY, 10.0, h=3.2)

# scintille agli urti
SPK = max(win(28.6, 30.8, 0.3), win(32.9, 34.6, 0.3), win(35.5, 36.9, 0.3), win(53.8, 57.0, 0.4) * 0.8)
FLASH = SPK * (0.6 + 0.4 * math.sin(SEC * 31))
if FLASH > 0.02 and ARMY > 0:
    import random; rr = random.Random(int(SEC * 24))
    fx, fy, fa = ROAD.at(CLASH + 2.0) if SEC < 50 else (kx, ky, 0.0)
    for s_ in range(26):
        v = rr.uniform(-15, 15); u = rr.uniform(-1.5, 1.5); x = fx + u * math.cos(fa) - v * math.sin(fa); y = fy + u * math.sin(fa) + v * math.cos(fa)
        if SEC >= 50: ang_ = rr.uniform(0, 6.28); x, y = kx + 9 * math.cos(ang_), ky + 9 * math.sin(ang_)
        z = zxy(x, y)
        if z > ZSEA: obox('flash', (x, y), rr.uniform(0, 3), 0.35, 0.35, z + 3.0, z + 3.0 + rr.uniform(1.0, 4.0) * SPK)

# scene 6-7: il sentiero di Anopea (indicativo [Guessing]) e gli Immortali di notte; scena 8 scendono alle spalle dei Greci
ANOP = [(38.793, 22.470), (38.780, 22.478), (38.766, 22.500), (38.760, 22.530), (38.768, 22.556), (38.782, 22.572), (38.793, 22.568)]
AP = Path(ANOP)
if ARMY > 0.5: ribbon('red2', ANOP, 2.4, 3.0, upto=ease((SEC - 38.4) / 4.4), dash=6.0)
ik = ease((SEC - 43.0) / 4.3)
ic = None
if 43.0 <= SEC and ARMY > 0:
    x, y, a = AP.at(10 + (AP.L - 22) * ik)
    back = ease((SEC - 48.5) / 5.5)                  # all'alba scendono sulla strada e chiudono verso il poggio
    if back > 0:
        tx_, ty_ = xy(38.7962, 22.5470); x, y = lerp(x, tx_, back), lerp(y, ty_, back); a = lerp(a, math.pi, back)
    ic = block('imm', x, y, a, 24.0, 10.0, h=3.2)

# ---------------- territori pieni (stile One Map): zone colorate drappeggiate sul rilievo
def seg_dist(px, py, P):
    best = 1e9
    for k in range(1, len(P)):
        ax, ay = P[k - 1]; bx, by = P[k]; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return best
hx, hy, _ = ROAD.at(min(head, CLASH)); FRONT = ll(hx, hy)[1] + 0.0004          # longitudine del fronte persiano
GFRONT = GREEK[1] - 0.0007
APxy = [xy(*p) for p in ANOP]
anop_done = ease((SEC - 38.4) / 4.4) * ARMY
ncut = max(2, int(2 + (len(APxy) - 2) * anop_done))
surround = ease((SEC - 45.9) / 1.5)                  # i Persiani chiudono alle spalle
pocket = ease((SEC - 50.5) / 4.0)                    # la sacca greca si riduce al poggio
won = ease((SEC - 57.1) / 1.6)                       # Serse prende il passo: tutto rosso
def owner(la, lo):
    x, y = xy(la, lo); e = elev(la, lo)
    if anop_done > 0 and la < 38.796 and seg_dist(x, y, APxy[:ncut]) < 9: return 'p'
    if not (38.783 < la < 38.815) or e > 220: return None
    if won > 0 and lo < 22.53 + 0.03 * won and 38.790 < la < 38.806: return 'p'
    kd = math.hypot(x - kx, y - ky)
    if pocket > 0:
        if kd < 9 + 14 * (1 - pocket) and won < 1: return 'g'
        if 38.790 < la < 38.803 and GFRONT - 0.01 < lo < 22.556: return 'p' if pocket > 0.3 else None
    if surround > 0 and 38.790 < la < 38.803 and 22.547 < lo < 22.547 + 0.012 * surround: return 'p'   # chiusura solo nel corridoio
    if lo < min(FRONT, GFRONT) and (pocket < 0.3 or la > 38.7905): return 'p'
    if GFRONT < lo < 22.5435 and 38.7925 < la < 38.8015: return 'g'                    # sacca greca: solo dietro il muro
    return None
def drape(step_la=0.00025, step_lo=0.0003, lift=0.9):
    la0, la1, lo0, lo1 = 38.755, 38.815, 22.42, 22.605
    nla = int((la1 - la0) / step_la); nlo = int((lo1 - lo0) / step_lo)
    for i in range(nla):
        for j in range(nlo):
            la = la0 + (i + 0.5) * step_la; lo = lo0 + (j + 0.5) * step_lo
            w = owner(la, lo)
            if not w or elev(la, lo) < SEA: continue
            c = [(la0 + i * step_la, lo0 + j * step_lo), (la0 + i * step_la, lo0 + (j + 1) * step_lo),
                 (la0 + (i + 1) * step_la, lo0 + (j + 1) * step_lo), (la0 + (i + 1) * step_la, lo0 + j * step_lo)]
            P = [(*xy(a_, b_), max(zof(a_, b_), ZSEA) + lift) for a_, b_ in c]
            poly('terrP' if w == 'p' else 'terrG', P, [[0, 1, 2, 3]])
if ARMY > 0: drape()
fl = min(FRONT, GFRONT)
_fl = [(la, fl) for la in np.linspace(38.790, 38.806, 40) if elev(la, fl) > SEA + 1 and elev(la, fl) < 220]
if len(_fl) > 2 and ARMY > 0 and SEC < 50: ribbon('frontline', [_fl[0], _fl[-1]], 0.9, 2.0, arrow=False)
# scena 9: anello tratteggiato luminoso attorno al poggio
RING = win(54.3, 59.0, 0.5)
if RING > 0.02:
    for k in range(36):
        if k % 2: continue
        a0, a1 = 2 * math.pi * k / 36, 2 * math.pi * (k + 1) / 36; r = 13
        p0 = ll(kx + r * math.cos(a0), ky + r * math.sin(a0)); p1 = ll(kx + r * math.cos(a1), ky + r * math.sin(a1))
        ribbon('ring', [p0, p1], 0.9, 3.0, arrow=False)

COL = dict(greek=(0.06, 0.30, 1.0, 1), greekE=(0.35, 0.65, 1.0, 1), greekZ=(0.10, 0.35, 1.0, 1),
           pers=(0.85, 0.06, 0.03, 1), persE=(1.0, 0.28, 0.12, 1), persZ=(0.9, 0.06, 0.03, 1),
           imm=(1.0, 0.45, 0.06, 1), immE=(1.0, 0.80, 0.45, 1), immZ=(1.0, 0.45, 0.06, 1),
           red=(1.0, 0.12, 0.08, 1), red2=(1.0, 0.45, 0.10, 1), terrP=(0.85, 0.08, 0.04, 1), terrG=(0.10, 0.35, 1.0, 1), frontline=(1.0, 0.85, 0.4, 1), ring=(1.0, 0.85, 0.2, 1), greekL=(0.35, 0.55, 0.9, 1), greekLE=(0.55, 0.7, 1.0, 1), wall=(0.75, 0.68, 0.52, 1), flash=(1.0, 0.85, 0.55, 1))
EM = dict(greek=0.9, greekE=1.4, greekZ=0.7, pers=0.75, persE=1.2, persZ=0.6, imm=1.1, immE=1.6, immZ=0.7,
          red=1.6, red2=2.0, terrP=0.25, terrG=0.25, frontline=1.2, flash=6.0 * FLASH, ring=3.0 * RING, wall=0.25 + 2.5 * WALLGLOW, greekL=0.5 * (1 - leave), greekLE=0.8 * (1 - leave))
for m, (Vv, Ff) in GEO.items():
    mm = bpy.data.meshes.new(m); mm.from_pydata(Vv, [], Ff); mm.update()
    mt = bpy.data.materials.new(m); mt.use_nodes = True; bb = mt.node_tree.nodes['Principled BSDF']
    bb.inputs['Base Color'].default_value = COL[m]; bb.inputs['Emission Color'].default_value = COL[m]; bb.inputs['Emission Strength'].default_value = EM.get(m, 0.0)
    bb.inputs['Roughness'].default_value = 0.6
    if m.endswith('Z'): bb.inputs['Alpha'].default_value = 0.22
    if m.startswith('terr'): bb.inputs['Alpha'].default_value = 0.20 * ARMY
    mm.materials.append(mt); o = bpy.data.objects.new(m, mm); sc.collection.objects.link(o)

# ---------------- luce e cielo (sempre scuro; di notte piu' blu e piu' buio)
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.035 * (1 - NIGHT) + 0.012 * NIGHT, 0.045 * (1 - NIGHT) + 0.02 * NIGHT, 0.07 * (1 - NIGHT) + 0.05 * NIGHT, 1)
bg.inputs['Strength'].default_value = 0.6 * (1 - NIGHT) + 0.5 * NIGHT
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.5 * (1 - NIGHT) + 2.4 * NIGHT; sun.angle = math.radians(1.0)
sun.color = (1.0 - 0.45 * NIGHT, 1.0 - 0.25 * NIGHT, 1.0)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(72), 0, math.radians(125 + 40 * NIGHT))

# ---------------- camera: sempre alta (mai sotto ~140 unita' sopra il terreno), Catmull-Rom tra le chiavi
KEYS = [  # secondo, camera (lat, lon, z), bersaglio (lat, lon, z), lente. Sempre alta.
    (0.0,  (38.8005, 22.592, 270), (38.7990, 22.503, 0), 30),     # 1 gancio: corridoio da est
    (5.7,  (38.8005, 22.588, 285), (38.7995, 22.500, 0), 30),
    (11.0, (38.8070, 22.584, 380), (38.8010, 22.478, 0), 28),     # 2 si alza e mostra la piana di Trachis
    (16.0, (38.8000, 22.578, 235), (38.7988, 22.515, 0), 30),     # 3 spinta verso la strozzatura
    (22.5, (38.7995, 22.568, 190), (38.7975, 22.530, 0), 32),     # 4 il muro
    (28.0, (38.7990, 22.566, 175), (38.7985, 22.522, 0), 32),     # 5 gli urti
    (36.0, (38.7988, 22.564, 178), (38.7983, 22.524, 0), 32),
    (40.0, (38.7820, 22.590, 330), (38.7820, 22.522, 25), 27),    # 6 notte: si alza a sud-est, il sentiero
    (47.0, (38.7520, 22.618, 470), (38.7810, 22.540, 25), 24),    # 7 gli Immortali alle spalle
    (51.5, (38.7700, 22.585, 300), (38.7930, 22.540, 5), 28),     # 8 si stringe sulla sacca
    (55.5, (38.7820, 22.566, 185), (38.7962, 22.5395, 5), 32),    # 9 il poggio
    (58.0, (38.7840, 22.570, 210), (38.7962, 22.538, 5), 31),
    (62.7, (38.7700, 22.610, 470), (38.8080, 22.530, 0), 25),     # 10 TODAY: si allarga sulla costa di oggi
]
def cr(p0, p1, p2, p3, t):
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
def cam_at(t):
    ks = [(k[0], mu.Vector((*xy(*k[1][:2]), k[1][2])), mu.Vector((*xy(*k[2][:2]), k[2][2])), k[3]) for k in KEYS]
    for i in range(len(ks) - 1):
        if t <= ks[i + 1][0] or i == len(ks) - 2: break
    t0, t1 = ks[i][0], ks[i + 1][0]; f = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
    g = lambda j: ks[max(0, min(len(ks) - 1, j))]
    pos = cr(g(i - 1)[1], g(i)[1], g(i + 1)[1], g(i + 2)[1], f)
    tgt = cr(g(i - 1)[2], g(i)[2], g(i + 1)[2], g(i + 2)[2], f)
    lens = g(i)[3] + (g(i + 1)[3] - g(i)[3]) * f
    return pos, tgt, lens
cam_pos, tgt, lens = cam_at(SEC)
cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_end = 20000
co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co
co.location = cam_pos; co.rotation_euler = (tgt - cam_pos).to_track_quat('-Z', 'Y').to_euler()

if os.environ.get('THREADS'): sc.render.threads_mode = 'FIXED'; sc.render.threads = int(os.environ['THREADS'])
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
DEV = os.environ.get('DEVICE', 'CPU')                 # sul pod: OPTIX o CUDA (da gputest.py)
if DEV in ('OPTIX', 'CUDA'):
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = DEV; pr.get_devices()
    for d_ in pr.devices: d_.use = d_.type == DEV
    if not any(d_.use and d_.type == DEV for d_ in pr.devices):
        print('[thermo] ERRORE: nessuna GPU ' + DEV + '. Mi fermo invece di usare il processore.', flush=True); sys.exit(3)
    sc.cycles.device = 'GPU'
sc.cycles.samples = SPP; sc.cycles.use_denoising = True
if DEV == 'OPTIX': sc.cycles.denoiser = 'OPTIX'
sc.render.resolution_x = W; sc.render.resolution_y = H
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)

# ---------------- posizioni a schermo per l'infografica
sc.view_layers[0].update()
def proj(x, y, z):
    v = world_to_camera_view(sc, co, mu.Vector((x, y, z))); return (v.x, 1 - v.y, v.z)
pos = {}
for k_, ((la, lo), dz) in {'THE HOT GATES': ((38.7948, 22.541), 2), 'MALIAN GULF': ((38.8075, 22.552), 0),
                           'ANOPAEA PATH': ((38.762, 22.515), 3), 'KALLIDROMO': ((38.780, 22.548), 20)}.items():
    x, y = xy(la, lo); pos[k_] = proj(x, y, zof(la, lo) + dz)
if gc: pos['GREEKS'] = proj(gc[0], gc[1], gc[2] + 4)
if pc: pos['PERSIANS'] = proj(pc[0][0], pc[0][1], pc[0][2] + 4); pos['XERXES'] = proj(pc[-1][0], pc[-1][1], pc[-1][2] + 4)
if ic: pos['IMMORTALS'] = proj(ic[0], ic[1], ic[2] + 4)
if imd: pos['IMMDAY'] = proj(imd[0], imd[1], imd[2] + 4)
pos['KOLONOS'] = proj(kx, ky, zxy(kx, ky) + 4); pos['WALL'] = proj(*xy(38.7972, 22.5392), zof(38.7972, 22.5392) + 3)
for k_, (la, lo) in {'COAST480': (38.8060, 22.556), 'COASTTODAY': (38.8300, 22.548)}.items(): x, y = xy(la, lo); pos[k_] = proj(x, y, 1.0)
json.dump(pos, open(OUT + '.json', 'w'))
print('OK', OUT)
