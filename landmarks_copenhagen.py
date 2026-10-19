# Monumenti di Copenaghen modellati a fasi (fondazioni -> corpo -> tetto/guglia/cupola) per build_render.py.
# Impronte da OSM (osm_buildings.geojson del pod), forme semplici ma riconoscibili, anni di costruzione per parte.
# Uscita: DATA/landmarks.json {"parts": [...], "clear": [anelli], "labels": [...], "harbours": [...], "fires": [...], "lights": [...]}
# Tipi di parte (tutte con "y" = anno in cui compare, "d" opzionale = anno in cui sparisce, "c" colore, "a" alfa del colore:
#   1 = muro con finestre, 0.05 = pietra/rame senza finestre, 0.5 = vetro):
#   prism {r, z0, z1} · hip {r, z0, z1, rh} (tetto a padiglione sul rettangolo minimo) · cyl {cx, cy, rad, z0, z1, seg}
#   cone {cx, cy, r0, r1, z0, z1, seg} · dome {cx, cy, rad, z0, hz} · helix {cx, cy, r0, r1, z0, z1, turns, w, n_strands}
#   wedge {r, z0, za, zb, ax}: tetto inclinato lungo l'asse lungo (CopenHill)
# Anni da verificare prima delle schede a schermo (sono le date note dei cantieri).
# Uso: python landmarks_copenhagen.py RAW_DIR DATA_DIR city_copenhagen.json
import json, math, sys, os
import numpy as np, geopandas as gpd, shapely
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely import affinity

RAW, DATA, CFG = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def loc(g): return shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY])
b = gpd.read_file(f'{RAW}/osm_buildings.geojson')
FP = {o: loc(g) for o, g in zip(b['osm'], b.geometry)}
def fp(osm):
    g = FP[osm]
    if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
    return g.buffer(0)
def ring(g, simp=0.5):
    g = g.simplify(simp)
    if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda q: q.area)
    return [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]

BRICK, BRICK2, COPPER, STONE, SAND, GOLD = '#a5432f', '#8f3a2a', '#5fa08a', '#cfc8b8', '#d9c7a0', '#d8a640'
parts, clear, labels, lights = [], [], [], []
def P(**k): parts.append(k)
def lab(name, x, y, z, y_from): labels.append({'name': name, 'x': round(x, 1), 'y': round(y, 1), 'z': z, 'from': y_from})
def mrr_axis(g):
    c = list(g.minimum_rotated_rectangle.exterior.coords)
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    return (e1 if math.hypot(*e1) >= math.hypot(*e2) else e2)

# ---------- 1. Castello di Absalon -> castello di Copenaghen -> tre Christiansborg ----------
cb = fp('w25992657'); cbc = cb.centroid; clear.append(ring(cb.buffer(4)))
ab = Point(*L(55.6765, 12.5797))   # Slotsholmen, rovine sotto il palazzo di oggi
P(name='Absalon castle', t='cyl', cx=ab.x, cy=ab.y, rad=34, z0=0, z1=7, seg=14, c=STONE, a=0.05, y=1167.0, d=1369.5)
P(name='Absalon castle', t='prism', r=ring(box(ab.x - 6, ab.y - 6, ab.x + 6, ab.y + 6)), z0=0, z1=22, c=STONE, a=0.05, y=1168.0, d=1369.5)
P(name='Absalon castle', t='cone', cx=ab.x, cy=ab.y, r0=8.5, r1=0.5, z0=22, z1=30, seg=4, c=BRICK2, a=0.05, y=1168.5, d=1369.5)
inner = affinity.scale(cb, 0.55, 0.55)
P(name='Copenhagen Castle', t='prism', r=ring(inner), z0=0, z1=16, c=SAND, a=1, y=1376, d=1731.3)
P(name='Copenhagen Castle', t='hip', r=ring(inner), z0=16, z1=16, rh=8, c=BRICK2, a=0.05, y=1378, d=1731.3)
P(name='Copenhagen Castle', t='cyl', cx=inner.centroid.x + 25, cy=inner.centroid.y, rad=6, z0=0, z1=34, seg=10, c=SAND, a=0.05, y=1380, d=1731.3)
P(name='Copenhagen Castle', t='cone', cx=inner.centroid.x + 25, cy=inner.centroid.y, r0=6.5, r1=0.3, z0=34, z1=58, seg=10, c=COPPER, a=0.05, y=1590, d=1731.3)   # Blaataarn
cb_body = cb.buffer(-3)
for gen, (y0, d) in enumerate([(1733, 1794.15), (1803, 1884.75)]):   # Christiansborg I (barocco) e II (classicista)
    col = SAND if gen == 0 else '#e0ddd2'
    P(name=f'Christiansborg {gen + 1}', t='prism', r=ring(cb_body.buffer(-2)), z0=0, z1=4, c=col, a=0.05, y=y0, d=d)
    P(name=f'Christiansborg {gen + 1}', t='prism', r=ring(cb_body.buffer(-2)), z0=4, z1=24, c=col, a=1, y=y0 + 4, d=d)
    P(name=f'Christiansborg {gen + 1}', t='prism', r=ring(cb_body.buffer(-5)), z0=24, z1=30, c=COPPER if gen == 0 else '#6a6d6a', a=0.05, top=COPPER if gen == 0 else '#6a6d6a', y=y0 + 9, d=d)
P(name='Christiansborg', t='prism', r=ring(cb_body), z0=0, z1=5, c='#b8b2a6', a=0.05, y=1907)
P(name='Christiansborg', t='prism', r=ring(cb_body), z0=5, z1=27, c='#b8b2a6', a=1, y=1912)
P(name='Christiansborg', t='prism', r=ring(cb_body.buffer(-4)), z0=27, z1=33, c=COPPER, a=0.05, top=COPPER, y=1920)
tx, ty = L(55.6759, 12.5794)       # torre di Christiansborg (106 m, la piu' alta della citta')
P(name='Christiansborg tower', t='prism', r=ring(box(tx - 7, ty - 7, tx + 7, ty + 7)), z0=0, z1=66, c='#b8b2a6', a=1, y=1918)
P(name='Christiansborg tower', t='cone', cx=tx, cy=ty, r0=7.5, r1=4.5, z0=66, z1=82, seg=8, c=COPPER, a=0.05, y=1924)
P(name='Christiansborg tower', t='cone', cx=tx, cy=ty, r0=3.2, r1=0.3, z0=82, z1=106, seg=8, c=COPPER, a=0.05, y=1927)
lab('Christiansborg', tx, ty, 106, 1928)
fires = [{'name': 'Christiansborg fire 1794', 'y': 1794.15, 'y1': 1794.16, 'houses': 0, 'flames': 40, 'smoke': 10, 'poly': ring(cb.buffer(6))},
         {'name': 'Christiansborg fire 1884', 'y': 1884.75, 'y1': 1884.76, 'houses': 0, 'flames': 40, 'smoke': 10, 'poly': ring(cb.buffer(6))}]

# ---------- 2. Boersen (1619-1625): edificio lungo con la guglia dei quattro draghi ----------
bo = fp('w25466204'); clear.append(ring(bo.buffer(3))); boc = bo.centroid
P(name='Boersen', t='prism', r=ring(bo), z0=0, z1=3, c=STONE, a=0.05, y=1619.0)
P(name='Boersen', t='prism', r=ring(bo), z0=3, z1=13, c=BRICK, a=1, y=1620.5)
P(name='Boersen', t='hip', r=ring(bo), z0=13, z1=13, rh=8, c=COPPER, a=0.05, y=1622.5)
P(name='Boersen dragon spire', t='prism', r=ring(box(boc.x - 3.5, boc.y - 3.5, boc.x + 3.5, boc.y + 3.5)), z0=18, z1=24, c=COPPER, a=0.05, y=1624.0)
P(name='Boersen dragon spire', t='helix', cx=boc.x, cy=boc.y, r0=2.6, r1=0.15, z0=24, z1=56, turns=3.5, w=1.1, n_strands=4, c=COPPER, a=0.05, y=1625.0)
lab('Børsen', boc.x, boc.y, 56, 1625)

# ---------- 3. Rundetaarn (1637-1642) e chiesa della Trinita' ----------
rt = fp('w1011492033'); rtc = rt.centroid; clear.append(ring(rt.buffer(2)))
P(name='Rundetaarn', t='cyl', cx=rtc.x, cy=rtc.y, rad=7.7, z0=0, z1=12, seg=20, c=BRICK, a=0.05, y=1637.0)
P(name='Rundetaarn', t='cyl', cx=rtc.x, cy=rtc.y, rad=7.7, z0=12, z1=34.8, seg=20, c=BRICK, a=0.05, y=1639.5)
P(name='Rundetaarn', t='dome', cx=rtc.x, cy=rtc.y, rad=4.2, z0=34.8, hz=4.5, c='#d7d7cf', a=0.05, y=1642.0)
tk = fp('w45902028'); clear.append(ring(tk.buffer(2)))
P(name='Trinitatis', t='prism', r=ring(tk), z0=0, z1=17, c=BRICK, a=1, y=1640.0)
P(name='Trinitatis', t='hip', r=ring(tk), z0=17, z1=17, rh=9, c=COPPER, a=0.05, y=1650.0)
lab('Rundetårn', rtc.x, rtc.y, 40, 1642)

# ---------- 4. Rosenborg (1606-1624) ----------
ro = fp('w25524592'); roc = ro.centroid; clear.append(ring(ro.buffer(3)))
ax = mrr_axis(ro); n_ = math.hypot(*ax); ux, uy = ax[0] / n_, ax[1] / n_
P(name='Rosenborg', t='prism', r=ring(ro), z0=0, z1=3, c=STONE, a=0.05, y=1606.0)
P(name='Rosenborg', t='prism', r=ring(ro), z0=3, z1=16, c=BRICK, a=1, y=1607.0)
P(name='Rosenborg', t='hip', r=ring(ro), z0=16, z1=16, rh=9, c=COPPER, a=0.05, y=1610.0)
for k, (off, hh, sp) in enumerate([(-0.5, 30, 52), (0.0, 22, 34), (0.5, 24, 36)]):   # torre principale e torrette con guglie
    L_ = n_ * off; cx_, cy_ = roc.x + ux * L_ + (-uy) * 9, roc.y + uy * L_ + ux * 9
    P(name='Rosenborg tower', t='prism', r=ring(box(cx_ - 3.5, cy_ - 3.5, cx_ + 3.5, cy_ + 3.5)), z0=0, z1=hh, c=BRICK, a=1, y=1613 + 3 * k)
    P(name='Rosenborg tower', t='cone', cx=cx_, cy=cy_, r0=3.6, r1=0.2, z0=hh, z1=sp, seg=8, c=COPPER, a=0.05, y=1616 + 3 * k)
lab('Rosenborg Castle', roc.x, roc.y, 52, 1624)

# ---------- 5. Marmorkirken: iniziata 1749, ferma (rovina) dal 1770, cupola finita 1894 ----------
mk = fp('w25524833'); mkc = mk.centroid; clear.append(ring(mk.buffer(3)))
R_ = math.sqrt(mk.area / math.pi)
P(name='Marble Church', t='cyl', cx=mkc.x, cy=mkc.y, rad=R_, z0=0, z1=4, seg=28, c='#dcd9cf', a=0.05, y=1749.5)
P(name='Marble Church', t='cyl', cx=mkc.x, cy=mkc.y, rad=R_, z0=4, z1=13, seg=28, c='#dcd9cf', a=0.05, y=1754.0)   # la rovina del 1770-1874
P(name='Marble Church', t='cyl', cx=mkc.x, cy=mkc.y, rad=R_, z0=13, z1=30, seg=28, c='#dcd9cf', a=1, y=1877.0)
P(name='Marble Church', t='cyl', cx=mkc.x, cy=mkc.y, rad=R_ * 0.68, z0=30, z1=40, seg=24, c='#dcd9cf', a=1, y=1882.0)
P(name='Marble Church', t='dome', cx=mkc.x, cy=mkc.y, rad=R_ * 0.68, z0=40, hz=24, c=COPPER, a=0.05, y=1887.0)
P(name='Marble Church', t='cyl', cx=mkc.x, cy=mkc.y, rad=3.2, z0=63, z1=71, seg=10, c=COPPER, a=0.05, y=1891.0)
P(name='Marble Church', t='cone', cx=mkc.x, cy=mkc.y, r0=1.6, r1=0.1, z0=71, z1=77, seg=8, c=GOLD, a=0.05, y=1893.0)
lab('Marble Church', mkc.x, mkc.y, 77, 1894)

# ---------- 6. Amalienborg (1750-1760): quattro palazzi uguali attorno alla piazza ottagonale ----------
pal = ['w106105298', 'w106105466', 'w25524645', 'w106228713']   # Christian VII (Moltke), IX, VIII, Frederik VIII
cs = []
for k, o in enumerate(pal):
    g = fp(o); clear.append(ring(g.buffer(2))); cs.append(g.centroid)
    P(name='Amalienborg', t='prism', r=ring(g), z0=0, z1=3, c=SAND, a=0.05, y=1750 + 2 * k)
    P(name='Amalienborg', t='prism', r=ring(g), z0=3, z1=17, c='#d4c4a0', a=1, y=1751 + 2 * k)
    P(name='Amalienborg', t='hip', r=ring(g), z0=17, z1=17, rh=8, c='#55625c', a=0.05, y=1752.5 + 2 * k)
ax_, ay_ = sum(c.x for c in cs) / 4, sum(c.y for c in cs) / 4
P(name='Amalienborg statue', t='prism', r=ring(box(ax_ - 2.5, ay_ - 4.5, ax_ + 2.5, ay_ + 4.5)), z0=0, z1=6, c=STONE, a=0.05, y=1768)
P(name='Amalienborg statue', t='prism', r=ring(box(ax_ - 1.2, ay_ - 2.5, ax_ + 1.2, ay_ + 2.5)), z0=6, z1=11, c='#4f7f6c', a=0.05, y=1771)
lab('Amalienborg Palace', ax_, ay_, 20, 1760)

# ---------- 7. Vor Frelsers Kirke (1682-1696), guglia con la scala a spirale esterna (1749-1752) ----------
vf = fp('w25607908'); clear.append(ring(vf.buffer(2)))
vt = fp('w290040529'); vtc = vt.centroid; clear.append(ring(vt.buffer(2)))
P(name="Our Saviour's Church", t='prism', r=ring(vf.difference(vt.buffer(1)) if vf.difference(vt.buffer(1)).geom_type == 'Polygon' else vf), z0=0, z1=18, c=BRICK, a=1, y=1682.0)
P(name="Our Saviour's Church", t='hip', r=ring(vf), z0=18, z1=18, rh=10, c='#4b4a48', a=0.05, y=1690.0)
P(name="Our Saviour's Church", t='prism', r=ring(box(vtc.x - 5.2, vtc.y - 5.2, vtc.x + 5.2, vtc.y + 5.2)), z0=0, z1=46, c=BRICK, a=1, y=1694.0)
P(name="Our Saviour's spire", t='cone', cx=vtc.x, cy=vtc.y, r0=3.4, r1=0.25, z0=46, z1=88, seg=8, c='#2f2e2c', a=0.05, y=1749.5)
P(name="Our Saviour's spire", t='helix', cx=vtc.x, cy=vtc.y, r0=4.1, r1=0.6, z0=47, z1=86, turns=4, w=1.5, n_strands=1, c=GOLD, a=0.05, y=1751.0)
P(name="Our Saviour's spire", t='dome', cx=vtc.x, cy=vtc.y, rad=1.4, z0=88, hz=1.8, c=GOLD, a=0.05, y=1752.0)
lab("Church of Our Saviour", vtc.x, vtc.y, 90, 1752)

# ---------- 8. Nyhavn: canale scavato 1671-1673 (terra -> acqua), velieri ----------
land = json.load(open(f'{DATA}/land.json'))
LG = unary_union([Polygon(q['ext'], q.get('holes', [])).buffer(0) for q in land])
nyx0, nyy0 = L(55.6795, 12.5862); nyx1, nyy1 = L(55.6803, 12.5946)
nybox = box(min(nyx0, nyx1) - 5, min(nyy0, nyy1) - 60, max(nyx0, nyx1) + 5, max(nyy0, nyy1) + 60)
nyw = nybox.difference(LG).intersection(nybox)
nyw = max(nyw.geoms, key=lambda q: q.area) if hasattr(nyw, 'geoms') else nyw
harbours = [{'r': ring(nyw, 1.0), 'y': 1671.5, 'name': 'Nyhavn'}] if nyw.area > 2000 else []
ln = LineString([(nyx0, nyy0), (nyx1, nyy1)])
for k in range(7):
    p_ = ln.interpolate(0.12 + 0.11 * k, normalized=True); side = 1 if k % 2 else -1
    dx, dy = (nyx1 - nyx0), (nyy1 - nyy0); dn = math.hypot(dx, dy); ux2, uy2 = dx / dn, dy / dn
    cx_, cy_ = p_.x + (-uy2) * 7 * side, p_.y + ux2 * 7 * side
    hull = Polygon([(cx_ - ux2 * 11 - uy2 * 2.5, cy_ - uy2 * 11 + ux2 * 2.5), (cx_ + ux2 * 11 - uy2 * 2.5, cy_ + uy2 * 11 + ux2 * 2.5),
                    (cx_ + ux2 * 13, cy_ + uy2 * 13), (cx_ + ux2 * 11 + uy2 * 2.5, cy_ + uy2 * 11 - ux2 * 2.5), (cx_ - ux2 * 11 + uy2 * 2.5, cy_ - uy2 * 11 - ux2 * 2.5)])
    P(name='Nyhavn ships', t='prism', r=ring(hull, 0.1), z0=-1.5, z1=1.8, c='#4a3428', a=0.05, y=1676 + 3 * k, zbase=-1.5)
    for m_ in (-4, 4):
        P(name='Nyhavn ships', t='cyl', cx=cx_ + ux2 * m_, cy=cy_ + uy2 * m_, rad=0.35, z0=1.8, z1=22 - abs(m_), seg=5, c='#3a2a20', a=0.05, y=1677 + 3 * k)
lab('Nyhavn', (nyx0 + nyx1) / 2, (nyy0 + nyy1) / 2, 12, 1673)

# ---------- 9. Tivoli (1843): pagoda, Nimb, montagne russe, Star Flyer; luci di notte ----------
tv_c = Point(*L(55.6737, 12.5681))
tv_area = Point(tv_c.x - 20, tv_c.y).buffer(150).intersection(box(tv_c.x - 190, tv_c.y - 140, tv_c.x + 140, tv_c.y + 130))
px_, py_ = tv_c.x - 25, tv_c.y + 15
for k in range(4):   # pagoda (1900): quattro piani con tetti rossi
    s_ = 6.5 - 1.2 * k
    P(name='Tivoli pagoda', t='prism', r=ring(box(px_ - s_ * 0.7, py_ - s_ * 0.7, px_ + s_ * 0.7, py_ + s_ * 0.7)), z0=4.5 * k, z1=4.5 * k + 3.2, c='#e8d9b0', a=0.05, y=1900.0 + 0.3 * k)
    P(name='Tivoli pagoda', t='cone', cx=px_, cy=py_, r0=s_, r1=s_ * 0.45, z0=4.5 * k + 3.2, z1=4.5 * k + 4.5, seg=4, c='#c0392b', a=0.05, y=1900.2 + 0.3 * k)
nb = fp('w27169240'); nbc = nb.centroid
for dx_, dy_ in ((-18, -8), (18, -8), (0, 10)):   # cupole moresche del Nimb (1909)
    P(name='Nimb', t='dome', cx=nbc.x + dx_, cy=nbc.y + dy_, rad=3.2, z0=17, hz=5.5, c='#ece4d4', a=0.05, y=1909.0)
P(name='Tivoli roller coaster', t='cone', cx=tv_c.x + 55, cy=tv_c.y - 70, r0=24, r1=10, z0=0, z1=18, seg=7, c='#8b7d6b', a=0.05, y=1914.0)
P(name='Tivoli Star Flyer', t='cyl', cx=tv_c.x + 70, cy=tv_c.y + 40, rad=1.4, z0=0, z1=80, seg=8, c='#d9dde2', a=0.05, y=2006.0)
lab('Tivoli Gardens', tv_c.x, tv_c.y, 30, 1843)
rng = np.random.default_rng(3)
for k in range(900):   # lampadine di Tivoli: solo nella passata notturna (vedi build_render, "lights")
    while True:
        x_, y_ = rng.uniform(*tv_area.bounds[0::2]), rng.uniform(*tv_area.bounds[1::2])
        if tv_area.contains(Point(x_, y_)): break
    lights.append([round(x_, 1), round(y_, 1), round(float(rng.uniform(3, 9)), 1), int(rng.integers(0, 4))])
lights_year = 1843

# ---------- 10. Raadhus (1892-1905) e torre di 105,6 m ----------
rh = fp('r52142'); clear.append(ring(rh.buffer(3)))
tw = fp('w1011067074'); twc = tw.centroid
P(name='City Hall', t='prism', r=ring(rh), z0=0, z1=4, c=STONE, a=0.05, y=1892.0)
P(name='City Hall', t='prism', r=ring(rh), z0=4, z1=27, c=BRICK, a=1, y=1894.0)
P(name='City Hall', t='prism', r=ring(rh.buffer(-3)), z0=27, z1=32, c=COPPER, a=0.05, top=COPPER, y=1897.0)
P(name='City Hall tower', t='prism', r=ring(box(twc.x - 4.5, twc.y - 4.5, twc.x + 4.5, twc.y + 4.5)), z0=0, z1=64, c=BRICK, a=1, y=1900.0)
P(name='City Hall tower', t='cone', cx=twc.x, cy=twc.y, r0=4.8, r1=0.3, z0=64, z1=105.6, seg=8, c=COPPER, a=0.05, y=1904.0)
lab('City Hall', twc.x, twc.y, 106, 1905)

# ---------- 11. Operaen (2001-2004): tetto enorme a sbalzo verso il porto ----------
op = fp('w1088494374'); opc = op.centroid; clear.append(ring(op.buffer(3)))
P(name='Opera House', t='prism', r=ring(op), z0=0, z1=4, c='#cfccc4', a=0.05, y=2001.0)
P(name='Opera House', t='prism', r=ring(op.buffer(-4)), z0=4, z1=24, c='#d9d6cf', a=1, y=2002.5)
P(name='Opera House', t='prism', r=ring(box(opc.x - 18, opc.y - 14, opc.x + 18, opc.y + 14)), z0=24, z1=44, c='#4a4c50', a=0.05, y=2003.0)
# tetto: rettangolo minimo allungato di 32 m verso Amalienborg (asse del palazzo, a sud-ovest)
to_am = (ax_ - opc.x, ay_ - opc.y); dn_ = math.hypot(*to_am); ux3, uy3 = to_am[0] / dn_, to_am[1] / dn_
roof = op.minimum_rotated_rectangle.union(affinity.translate(op.minimum_rotated_rectangle, ux3 * 32, uy3 * 32)).convex_hull
P(name='Opera House', t='prism', r=ring(roof, 1.0), z0=32, z1=35, c='#ededea', a=0.05, y=2004.0)
lab('Opera House', opc.x, opc.y, 44, 2005)

# ---------- 12. Skuespilhuset (2005-2008) ----------
sk = fp('w25701472'); skc = sk.centroid; clear.append(ring(sk.buffer(3)))
P(name='Royal Playhouse', t='prism', r=ring(sk), z0=0, z1=13, c='#3d322d', a=1, y=2005.0)
P(name='Royal Playhouse', t='prism', r=ring(sk.buffer(-5)), z0=13, z1=19, c='#9bb3ba', a=0.5, y=2006.5)
P(name='Royal Playhouse', t='prism', r=ring(box(skc.x - 12, skc.y - 12, skc.x + 12, skc.y + 12)), z0=0, z1=36, c='#4a3f3a', a=0.05, y=2007.0)
lab('Royal Playhouse', skc.x, skc.y, 36, 2008)

# ---------- 13. CopenHill / Amager Bakke (2013-2019): pista da sci sul tetto inclinato, ciminiera ----------
ch = fp('w429610236'); chc = ch.centroid; clear.append(ring(ch.buffer(3)))
cax = mrr_axis(ch)
P(name='CopenHill', t='prism', r=ring(ch), z0=0, z1=6, c='#9fa09c', a=0.05, y=2013.5)
P(name='CopenHill', t='wedge', r=ring(ch), z0=6, za=22, zb=85, ax=list(cax), c='#a9aaa6', a=1, top='#6db346', y=2015.5)
P(name='CopenHill', t='cyl', cx=chc.x + cax[0] * 0.3, cy=chc.y + cax[1] * 0.3, rad=3.5, z0=0, z1=124, seg=10, c='#b8b8b4', a=0.05, y=2017.0)
lab('CopenHill', chc.x, chc.y, 90, 2019)

# ---------- 14. Ponte dell'Oeresund (1995-2000): strallato, piloni di 204 m; Peberholm ----------
# [Guessing] coordinate del tratto strallato: da verificare su una mappa prima dell'inquadratura dedicata
A = L(55.5790, 12.7700); B = L(55.5648, 12.9050); mid = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
dx, dy = B[0] - A[0], B[1] - A[1]; dn = math.hypot(dx, dy); ux4, uy4 = dx / dn, dy / dn
def along(s): return (A[0] + ux4 * s, A[1] + uy4 * s)
def deck_z(s):   # sale a 57 m al centro del tratto strallato
    c = dn / 2; return 12 + 45 * max(0.0, 1 - abs(s - c) / (dn * 0.45)) ** 1.2
seg_n = 40
for i in range(seg_n):
    s0, s1 = dn * i / seg_n, dn * (i + 1) / seg_n; p0, p1 = along(s0), along(s1)
    z_ = (deck_z(s0) + deck_z(s1)) / 2
    poly = LineString([p0, p1]).buffer(12, cap_style=2)
    P(name='Oresund Bridge', t='prism', r=ring(poly, 0.2), z0=z_ - 3, z1=z_, c='#d6d6d0', a=0.05, y=1997.5 + 1.5 * abs(i - seg_n / 2) / (seg_n / 2), zbase=z_ - 3)
    if i % 3 == 0:
        pc = along((s0 + s1) / 2)
        P(name='Oresund Bridge', t='cyl', cx=pc[0], cy=pc[1], rad=3, z0=-1.5, z1=z_ - 3, seg=6, c='#bdbdb6', a=0.05, y=1996.5)
for off in (-245, 245):   # due piloni, ognuno con due gambe
    pc = along(dn / 2 + off)
    for side in (-1, 1):
        P(name='Oresund Bridge', t='prism', r=ring(box(pc[0] - uy4 * 14 * side - 3, pc[1] + ux4 * 14 * side - 3, pc[0] - uy4 * 14 * side + 3, pc[1] + ux4 * 14 * side + 3)),
          z0=0, z1=204, c='#c9c9c3', a=0.05, y=1998.0)
lab('Øresund Bridge', mid[0], mid[1], 204, 2000)

# ---------- etichette senza modello ----------
lab('The Little Mermaid', *L(55.6929, 12.5993), 2, 1913)
json.dump({'parts': parts, 'clear': clear, 'labels': labels, 'harbours': harbours, 'fires': fires,
           'lights': lights, 'lights_year': lights_year}, open(f'{DATA}/landmarks.json', 'w'))
print(f'[landmarks] parti {len(parts)}, impronte da liberare {len(clear)}, etichette {len(labels)}, Nyhavn {"si" if harbours else "NO"}, luci {len(lights)}')
