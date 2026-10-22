# Ponti di Siviglia modellati uno a uno (NON il metodo di Copenaghen: niente tavole piatte da linee stradali).
# Per ogni ponte: asse e larghezza dal contorno OSM man_made=bridge; impalcato continuo a travi ("beam") che segue un
# profilo con rampe; pile alla distanza giusta; struttura tipica (archi sotto o sopra l'impalcato, stralli, torri).
# Ground = 0, acqua a water_z (-1,5). Anni e misure: fonti in PROSSIMA_SIVIGLIA.md sezione 9 ([V] verificato, [L] stimato).
# Uscita: DATA/landmarks.json (aggiunge le parti dei ponti a quelle gia' presenti, rimpiazzando i ponti precedenti).
# Uso: python bridges_sevilla.py DATA_DIR city_sevilla.json osm_export.geojson
import json, math, os, sys
from shapely.geometry import shape, Polygon, LineString, Point, box
from shapely.ops import unary_union, transform

DATA, CFG, SRC = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
WZ = CFG.get('water_z', -1.5)
def loc(g): return transform(lambda x, y, z=None: ((x - LON0) * KX, (y - LAT0) * KY), g)
F = json.load(open(SRC))['features']
WATER = unary_union([loc(shape(f['geometry'])).buffer(0) for f in F
                     if f['properties'].get('natural') == 'water' or f['properties'].get('waterway') == 'riverbank'])
OUTL = {}
for f in F:
    p = f['properties']
    if p.get('man_made') == 'bridge' and p.get('name') and f['geometry']['type'] == 'Polygon':
        OUTL.setdefault(p['name'], []).append(loc(shape(f['geometry'])).buffer(0))

CONC, ASPH, WHITE, IRON, STONE, WOOD = '#d8d3c7', '#77746e', '#f2f2ee', '#8e9a9b', '#c9b894', '#7a5a3a'
parts, labels = [], []
def P(**k):
    if 'p0' in k: k['cx'] = (k['p0'][0] + k['p1'][0]) / 2; k['cy'] = (k['p0'][1] + k['p1'][1]) / 2
    parts.append(k)
def beam(name, p0, p1, w, h, c, y, d=None, a=0.05, top=None):
    k = dict(name=name, t='beam', p0=[round(v, 2) for v in p0], p1=[round(v, 2) for v in p1], w=w, h=h, c=c, a=a, y=y)
    if d: k['d'] = d
    if top: k['top'] = top
    P(**k)
def boxp(name, cx, cy, ax, along, across, z0, z1, c, y, d=None, a=0.05):
    ux, uy = ax; vx, vy = -uy, ux; hl, hw = along / 2, across / 2
    r = [[cx + sx * hl * ux + sy * hw * vx, cy + sx * hl * uy + sy * hw * vy] for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    k = dict(name=name, t='prism', r=[[round(x, 2), round(yv, 2)] for x, yv in r], z0=z0, z1=z1, c=c, a=a, y=y)
    if d: k['d'] = d
    P(**k)

def frame(g, flip=False):
    """asse del ponte: direzione dalla parte del contorno SOPRA L'ACQUA (che per forza attraversa il fiume; il rettangolo
    del contorno intero seguiva le rampe lungo le banchine: Delicias veniva parallelo al fiume). Lunghezza = estensione
    del contorno intero lungo quell'asse; larghezza = area bagnata / lunghezza bagnata."""
    w = g.intersection(WATER)
    base = w if (not w.is_empty and w.area > 0.15 * g.area) else g
    m = base.minimum_rotated_rectangle; c4 = list(m.exterior.coords)[:4]
    e1 = (c4[1][0] - c4[0][0], c4[1][1] - c4[0][1]); e2 = (c4[2][0] - c4[1][0], c4[2][1] - c4[1][1])
    if math.hypot(*e1) < math.hypot(*e2): e1, e2 = e2, e1
    Lb = math.hypot(*e1); ax = (e1[0] / Lb, e1[1] / Lb)
    if flip: ax = (-ax[0], -ax[1])
    b0 = m.centroid
    # estensione lungo l'asse centrale, solo dove l'asse sta dentro il contorno (con i punti estremi del contorno
    # l'impalcato dritto sbordava sulle case accanto, es. Triana)
    cl = LineString([(b0.x - ax[0] * 3000, b0.y - ax[1] * 3000), (b0.x + ax[0] * 3000, b0.y + ax[1] * 3000)]).intersection(g.buffer(1))
    segs = [q for q in getattr(cl, 'geoms', [cl]) if not q.is_empty and q.distance(b0) < 2] or [q for q in getattr(cl, 'geoms', [cl]) if not q.is_empty]
    ss = [(x - b0.x) * ax[0] + (y - b0.y) * ax[1] for q in segs[:1] for x, y in q.coords]
    s0, s1 = min(ss), max(ss); L = s1 - s0; c = (b0.x + ax[0] * (s0 + s1) / 2, b0.y + ax[1] * (s0 + s1) / 2)
    W = max(6.0, min(base.area / Lb, math.hypot(*e2)))
    return c, ax, L, W

def wet_interval(c, ax, L, water=WATER):
    ln = LineString([(c[0] - ax[0] * L / 2, c[1] - ax[1] * L / 2), (c[0] + ax[0] * L / 2, c[1] + ax[1] * L / 2)])
    w = ln.intersection(water)
    if w.is_empty: return None
    ss = []
    for q in getattr(w, 'geoms', [w]):
        for x, y in q.coords: ss.append((x - c[0]) * ax[0] + (y - c[1]) * ax[1])
    return min(ss), max(ss)

def bridge(name, c, ax, L, W, H, y, d=None, spans=3, kind='beam', col=CONC, pier_col=CONC, wet=None, ramp=10.0, thick=1.6, rail=WHITE):
    """impalcato + pile; ritorna funzione z(s) e intervallo bagnato"""
    wet = wet or wet_interval(c, ax, L) or (-L / 4, L / 4)
    s_a, s_b = -L / 2, L / 2
    rA = max(12.0, min(H * ramp, wet[0] - s_a)); rB = max(12.0, min(H * ramp, s_b - wet[1]))
    def z(s): return 0.3 + (H - 0.3) * max(0.0, min(1.0, (s - s_a) / rA, (s_b - s) / rB))
    def pt(s, off=0.0, dz=0.0): return (c[0] + ax[0] * s - ax[1] * off, c[1] + ax[1] * s + ax[0] * off, z(s) + dz)
    # impalcato: travi da ~15 m che seguono il profilo (continuo, una sola superficie, niente tavole sovrapposte)
    n = max(2, int(L / 15)); ss = [s_a + (s_b - s_a) * i / n for i in range(n + 1)]
    for s0, s1 in zip(ss, ss[1:]):
        p0 = pt(s0, dz=-thick / 2); p1 = pt(s1, dz=-thick / 2)
        beam(name, p0, p1, W, thick, col, y, d)
        # carreggiata (piu' scura, 6 cm sopra: niente superfici complanari) e parapetti sui due bordi
        beam(name, pt(s0, dz=0.06), pt(s1, dz=0.06), max(2.0, W - 3.0), 0.12, ASPH, y, d)
        for off in (-W / 2 + 0.25, W / 2 - 0.25):
            beam(name, pt(s0, off, 0.6), pt(s1, off, 0.6), 0.35, 1.2, rail, y, d)
    # pile: nell'acqua 'spans' campate uguali; sui viadotti a terra una pila ogni 40 m dove l'impalcato e' alto
    piers = [wet[0] + (wet[1] - wet[0]) * k / spans for k in range(1, spans)] if spans > 1 else []
    s = s_a + 40
    while s < s_b - 30:
        if not (wet[0] - 20 < s < wet[1] + 20) and z(s) > 4: piers.append(s)
        s += 40
    for s in piers:
        x, yy, zt = pt(s)
        boxp(name, x, yy, ax, 3.5 if spans > 1 else 2.5, W * 0.8, WZ - 1.5, zt - thick, pier_col, y, d)
    # spalle sulle sponde
    for s in wet:
        x, yy, zt = pt(s); boxp(name, x, yy, ax, 5, W + 1, WZ - 1.5, max(0.5, zt - thick), pier_col, y, d)
    return z, pt, wet, piers

def arches_below(name, pt, z, wet, piers, W, y, col, ribs=4, rise_frac=0.85, d=None, w=0.7, h=1.3):
    sup = [wet[0]] + sorted(piers) + [wet[1]]
    for a_, b_ in zip(sup, sup[1:]):
        span = b_ - a_
        for k in range(ribs):
            off = -W / 2 + 1 + (W - 2) * k / max(1, ribs - 1)
            prev = None
            for i in range(13):
                s = a_ + span * i / 12; t = (s - a_) / span
                zc = WZ + 0.5 + (z(s) - 1.8 - (WZ + 0.5)) * (1 - (2 * t - 1) ** 2) ** 0.5 * rise_frac + 0.0
                x, yy, _ = pt(s, off); p = (x, yy, zc)
                if prev: beam(name, prev, p, w, h, col, y, d)
                prev = p

def arch_above(name, pt, s0, s1, off, rise, y, col, w=1.4, h=1.8, hangers=10, d=None):
    prev = None
    for i in range(17):
        s = s0 + (s1 - s0) * i / 16; t = (s - s0) / (s1 - s0)
        x, yy, zd = pt(s, off); p = (x, yy, zd + rise * 4 * t * (1 - t))
        if prev: beam(name, prev, p, w, h, col, y, d)
        prev = p
    for i in range(1, hangers):
        s = s0 + (s1 - s0) * i / hangers; t = (s - s0) / (s1 - s0)
        x, yy, zd = pt(s, off); beam(name, (x, yy, zd), (x, yy, zd + rise * 4 * t * (1 - t)), 0.25, 0.25, col, y, d)

def get(name, i=0, flip=False):
    g = OUTL[name][i]; return g, frame(g, flip)

# ---------------- i ponti ----------------
# Puente de barcas (1171-1852) [V]: 13 barche con tavolato, dove oggi c'e' il ponte di Triana [L posizione]
g, (c, ax, L, W) = get('Puente de Isabel II')
wet = wet_interval(c, ax, L); n = 13
for i in range(n):
    s = wet[0] + 8 + (wet[1] - wet[0] - 16) * i / (n - 1); x, yy = c[0] + ax[0] * s, c[1] + ax[1] * s
    boxp('Pontoon bridge', x, yy, (-ax[1], ax[0]), 16, 5, WZ - 0.6, WZ + 0.9, WOOD, 1000, 1852.1)
pa = (c[0] + ax[0] * (wet[0] - 6), c[1] + ax[1] * (wet[0] - 6), WZ + 1.3); pb = (c[0] + ax[0] * (wet[1] + 6), c[1] + ax[1] * (wet[1] + 6), WZ + 1.3)
beam('Pontoon bridge', pa, pb, 5.5, 0.4, '#a07a4f', 1000, 1852.1)
labels.append({'name': 'Pontoon Bridge (1171)', 'x': round(c[0], 1), 'y': round(c[1], 1), 'z': 3, 'from': 1248, 'to': 1852})

# Puente de Isabel II / Triana (1845-1852) [V]: 3 archi in ghisa, pile di pietra, 149 m
z, pt, wet, piers = bridge('Triana Bridge', c, ax, L, W, 6.5, 1852, spans=3, col='#cfc9bb', pier_col=STONE, rail=IRON)
arches_below('Triana Bridge', pt, z, wet, piers, W, 1852, IRON, ribs=5)
labels.append({'name': 'Triana Bridge', 'x': round(c[0], 1), 'y': round(c[1], 1), 'z': 8, 'from': 1852})

# Puente de San Telmo (1931) [V]: archi laterali in cemento; tratto centrale levatoio fino al 1964-65
g, (c, ax, L, W) = get('Puente de San Telmo')
z, pt, wet, piers = bridge('San Telmo Bridge', c, ax, L, W, 7.0, 1931, spans=3, pier_col=CONC)
arches_below('San Telmo Bridge', pt, z, wet, piers, W, 1931, '#cbc5b8', ribs=3, w=1.2, h=1.6)

# Puente de los Remedios (1968) [V]: trave, 3 campate, 29 m
g, (c, ax, L, W) = get('Puente de los Remedios')
bridge('Los Remedios Bridge', c, ax, L, W, 7.5, 1968, spans=3)

# Puente de las Delicias (1991) [L: le fonti dicono 1990 o 1992]: levatoio, quattro torrette di manovra
g, (c, ax, L, W) = get('Puente de las Delicias')
W = min(W, 24.0)   # 37 m misurati sull'acqua = tratto levatoio; le rampe sono piu' strette (sbordava sugli edifici del porto)
z, pt, wet, piers = bridge('Delicias Bridge', c, ax, L, W, 6.0, 1991, spans=3)
mid = (wet[0] + wet[1]) / 2
for ds in (-28, 28):
    for off in (-W / 2 - 2, W / 2 + 2):
        x, yy, zt = pt(mid + ds, off); boxp('Delicias Bridge', x, yy, ax, 6, 5, WZ - 1, zt + 12, CONC, 1991)

# Puente del Cristo de la Expiracion / Cachorro (1991) [V]: due archi d'acciaio ribassati, 130 m, sul letto asciutto di Chapina
g, (c, ax, L, W) = get('Puente del Cristo de la Expiración')
z, pt, wet, piers = bridge('Cachorro Bridge', c, ax, L, W, 7.0, 1991, spans=1)
sm = (wet[0] + wet[1]) / 2
for off in (-W / 2 + 1, W / 2 - 1): arch_above('Cachorro Bridge', pt, sm - 65, sm + 65, off, 14, 1991, WHITE)

# Pasarela de la Cartuja (1992) [L]: passerella pedonale
g, (c, ax, L, W) = get('Pasarela de la Cartuja')
bridge('Cartuja Footbridge', c, ax, L, min(W, 10), 6.0, 1992, spans=3, thick=1.2)

# Puente de la Barqueta (1992) [V]: arco sospeso centrale (piano di mezzeria) che a ogni estremo si apre in due gambe
g, (c, ax, L, W) = get('Puente de la Barqueta')
z, pt, wet, piers = bridge('Barqueta Bridge', c, ax, L, W, 7.0, 1992, spans=1)
sm = (wet[0] + wet[1]) / 2; half = min(84, (wet[1] - wet[0]) / 2 + 10)
arch_above('Barqueta Bridge', pt, sm - half + 25, sm + half - 25, 0, 30, 1992, WHITE, w=2.0, h=2.4, hangers=12)
for se, si in ((sm - half, sm - half + 25), (sm + half, sm + half - 25)):
    t = 25 / (2 * half - 50); ztop = 30 * 4 * (25 / (2 * half - 50)) * (1 - 25 / (2 * half - 50)) * 0 + 0
    for off in (-W / 2 + 1, W / 2 - 1):
        x0, y0, z0 = pt(se, off); x1, y1, z1 = pt(si, 0); beam('Barqueta Bridge', (x0, y0, z0), (x1, y1, z1 + 1.0), 1.6, 1.8, WHITE, 1992)
labels.append({'name': 'Barqueta Bridge', 'x': round(c[0], 1), 'y': round(c[1], 1), 'z': 38, 'from': 1992})

# Puente del Alamillo (1992) [V: campata 200 m, pilone 140 m inclinato 32 gradi, 13 coppie di stralli, senza stralli posteriori]
# pilone sulla sponda della Cartuja (ovest) [L: "inclinato verso l'isola della Cartuja"]
g, (c, ax, L, W) = get('Puente del Alamillo')
if ax[0] > 0: ax = (-ax[0], -ax[1])            # asse da est (citta') a ovest (Cartuja): s cresce verso ovest
z, pt, wet, piers = bridge('Alamillo Bridge', c, ax, L, W, 7.0, 1992, spans=1, col=WHITE)
sb = wet[1] + 8                                 # piede del pilone appena oltre la sponda ovest
bx, by, bz = pt(sb); tilt = math.radians(32); Hp = 140
top = (bx + ax[0] * math.tan(tilt) * Hp, by + ax[1] * math.tan(tilt) * Hp, Hp)
for i in range(3):   # pilone rastremato in tre tronchi
    f0, f1 = i / 3, (i + 1) / 3
    q0 = (bx + (top[0] - bx) * f0, by + (top[1] - by) * f0, bz + (top[2] - bz) * f0); q1 = (bx + (top[0] - bx) * f1, by + (top[1] - by) * f1, bz + (top[2] - bz) * f1)
    beam('Alamillo Bridge', q0, q1, 7 - 1.6 * i, 12 - 3 * i, WHITE, 1992)
for k in range(13):
    f = 0.35 + 0.6 * k / 12
    a_ = (bx + (top[0] - bx) * f, by + (top[1] - by) * f, bz + (top[2] - bz) * f)
    s = sb - 12 - (200 - 20) * (k + 1) / 13; x, yy, zd = pt(s, 0)
    beam('Alamillo Bridge', a_, (x, yy, zd + 0.5), 0.45, 0.45, WHITE, 1992)
labels.append({'name': 'Alamillo Bridge', 'x': round(top[0], 1), 'y': round(top[1], 1), 'z': 140, 'from': 1992})

# Puente del Centenario (1991) [V: campata 265 m, lunghezza 565 m, altezza massima 102 m]: impalcato alto per le navi,
# due piloni a portale, stralli a ventaglio su due piani
g, (c, ax, L, W) = get('Puente del Centenario')
z, pt, wet, piers = bridge('Centenario Bridge', c, ax, L, min(W, 24), 45.0, 1991, spans=1, ramp=14)
sm = (wet[0] + wet[1]) / 2
for s_p in (sm - 132.5, sm + 132.5):
    x, yy, zd = pt(s_p)
    for off in (-12.5, 12.5):
        lx, ly, _ = pt(s_p, off); beam('Centenario Bridge', (lx, ly, WZ - 1), (lx, ly, 102), 4.5, 6, CONC, 1991)
    l0 = pt(s_p, -12.5); l1 = pt(s_p, 12.5)
    beam('Centenario Bridge', (l0[0], l0[1], zd - 2), (l1[0], l1[1], zd - 2), 3, 3, CONC, 1991)
    beam('Centenario Bridge', (l0[0], l0[1], 100), (l1[0], l1[1], 100), 3, 3, CONC, 1991)
    for side in (-1, 1):
        for k in range(10):
            zt = 62 + 37 * k / 9; s_d = s_p + side * (14 + 110 * (k + 1) / 10)
            for off in (-12.5, 12.5):
                ax_, ay_, _ = pt(s_p, off); dx_, dy_, dz_ = pt(s_d, off)
                beam('Centenario Bridge', (ax_, ay_, zt), (dx_, dy_, dz_ + 0.5), 0.4, 0.4, WHITE, 1991)
labels.append({'name': 'Centenario Bridge', 'x': round(c[0], 1), 'y': round(c[1], 1), 'z': 105, 'from': 1991})

# Ponti a trave sul canale ovest: Rey Juan Carlos I (1981, OSM start_date) [L], Reina Sofia (1991) [V], Patrocinio (1982) [L]
for nm, yy_, H in (('Puente Rey Juan Carlos I', 1981, 8.0), ('Puente Reina Sofía', 1991, 8.0)):
    g, (c, ax, L, W) = get(nm); bridge(nm.replace('Puente ', '') + ' Bridge', c, ax, L, min(W, 30), H, yy_, spans=4)
for i in range(len(OUTL['Puente del Patrocinio'])):
    g, (c, ax, L, W) = get('Puente del Patrocinio', i); bridge('Patrocinio Bridge', c, ax, L, W, 6.5, 1982, spans=4)

# Puente de Alfonso XIII (1926-1998) [V date; L posizione]: levatoio a travata metallica sul canale di Tablada,
# in fondo all'avenida de la Raza. OSM ha la posizione ATTUALE (rimontato a terra): qui la posizione storica sul canale.
g, (c0, ax0, L0, W0) = get('Puente de Alfonso XIII')
yb = c0[1]; ln = LineString([(c0[0] - 800, yb), (c0[0] + 800, yb)]).intersection(WATER)
qs = [q for q in getattr(ln, 'geoms', [ln]) if not q.is_empty]
if qs:
    q = min(qs, key=lambda q: abs(q.centroid.x - c0[0])); xa, xb = q.bounds[0], q.bounds[2]
    c = ((xa + xb) / 2, yb); ax = (1.0, 0.0); L = (xb - xa) + 60; W = 14
    z, pt, wet, piers = bridge('Alfonso XIII Bridge', c, ax, L, W, 6.0, 1926, d=1998.5, spans=3, col='#b9b3a6')
    for off in (-W / 2, W / 2):    # travate laterali: corrente superiore + diagonali
        s0, s1 = wet[0], wet[1]; prev = None
        for i in range(9):
            s = s0 + (s1 - s0) * i / 8; x, yy, zd = pt(s, off); p = (x, yy, zd + 5)
            if prev: beam('Alfonso XIII Bridge', prev, p, 0.6, 0.6, '#6f7a7c', 1926, 1998.5)
            beam('Alfonso XIII Bridge', (x, yy, zd), p, 0.4, 0.4, '#6f7a7c', 1926, 1998.5)
            prev = p
    print(f'[ponti] Alfonso XIII sul canale tra x {xa:.0f} e {xb:.0f} a y {yb:.0f}')

# ---------------- uscita ----------------
path = f'{DATA}/landmarks.json'
LM = json.load(open(path)) if os.path.exists(path) else {'parts': [], 'clear': [], 'labels': []}
LM['parts'] = [p for p in LM['parts'] if not p.get('bridge')] + [dict(p, bridge=1) for p in parts]
LM['labels'] = [l for l in LM.get('labels', []) if not l.get('bridge')] + [dict(l, bridge=1) for l in labels]
LM.setdefault('clear', [])
# niente edifici dentro i contorni dei ponti (a Triana una casa storica stava in mezzo alla rampa)
_bc = [[[round(x, 1), round(y, 1)] for x, y in list(g.buffer(2).exterior.coords)[:-1]]
       for nm in ('Puente de Isabel II', 'Puente de San Telmo', 'Puente de los Remedios', 'Puente de las Delicias',
                  'Puente del Cristo de la Expiración', 'Pasarela de la Cartuja', 'Puente de la Barqueta', 'Puente del Alamillo',
                  'Puente del Centenario', 'Puente Rey Juan Carlos I', 'Puente Reina Sofía', 'Puente del Patrocinio') for g in OUTL[nm]]
LM['clear'] = LM.get('clear_other', []) + _bc   # clear_other: impronte dei monumenti (script delle icone); i ponti si rigenerano ogni volta
json.dump(LM, open(path, 'w'))
print(f'[ponti] {len(parts)} parti, {len(set(p["name"] for p in parts))} ponti')
