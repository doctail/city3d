# Monumenti di Roma, stile Latos: forme semplici ma riconoscibili, anni di costruzione per fase.
# Formato come landmarks_copenhagen.py: DATA/landmarks.json {"parts", "clear", "labels"}. Anni negativi = a.C.
# Uso: python landmarks_roma.py DATA_DIR
import json, math, sys
from shapely.geometry import Polygon, Point, box, LineString
from shapely import affinity
from shapely.ops import unary_union
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from hist_roma import L, AURELIAN, SERVIAN

DATA = sys.argv[1]
parts, clear, labels = [], [], []
TRAV, MARBLE, BRICK, TILE, LEAD, SAND, WHITE, GREEN = '#e6d6b0', '#efe8d8', '#b8653f', '#b5482e', '#8a8f94', '#d9c79a', '#f4f1ea', '#6d8f45'
def Pt(**k): parts.append(k)
def ring(g): return [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
def lab(name, x, y, z, y0, y1=None):
    labels.append({'name': name, 'x': round(x, 1), 'y': round(y, 1), 'z': z, 'from': y0, **({'to': y1} if y1 is not None else {})})
def rect(cx, cy, w, h, ang=0): return affinity.rotate(box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), ang, origin=(cx, cy))
def block(name, cx, cy, w, h, z0, z1, c, y, d=None, ang=0, a=0.05, roof=None, rh=0):
    g = rect(cx, cy, w, h, ang)
    Pt(name=name, t='prism', r=ring(g), z0=z0, z1=z1, c=c, a=a, y=y, **({'d': d} if d is not None else {}))
    if roof: Pt(name=name, t='hip', r=ring(g), z0=z1, z1=z1, rh=rh, c=roof, a=0.05, y=y + 1, **({'d': d} if d is not None else {}))
    return g
def ellring(name, cx, cy, a1, b1, a2, b2, z0, z1, c, y, d=None, ang=0, n=48, keep=None, dsel=None):
    # anello ellittico vuoto fatto di settori (il prisma unico non ha buchi)
    out = []
    for i in range(n):
        t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        tm = (t0 + t1) / 2
        if keep and not keep(tm): continue
        pts = [(a1 * math.cos(t0), b1 * math.sin(t0)), (a1 * math.cos(t1), b1 * math.sin(t1)), (a2 * math.cos(t1), b2 * math.sin(t1)), (a2 * math.cos(t0), b2 * math.sin(t0))]
        g = affinity.translate(affinity.rotate(Polygon(pts), ang, origin=(0, 0)), cx, cy)
        dd = dsel(tm) if dsel else d
        Pt(name=name, t='prism', r=ring(g), z0=z0, z1=z1, c=c, a=0.05, y=y, **({'d': dd} if dd is not None else {}))
        out.append(g)
    return out
_LAND = None
def _on_land(x, y):
    global _LAND
    if _LAND is None:
        _LAND = unary_union([Polygon(q['ext'], q.get('holes', [])).buffer(0) for q in json.load(open(f'{DATA}/land.json'))])
    return _LAND.contains(Point(x, y))
def wall(name, pts, z0, z1, c, y, d=None, w=4.0):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if not all(_on_land(xa + (xb - xa) * t, ya + (yb - ya) * t) for t in (0.1, 0.5, 0.9)): continue
        g = LineString([(xa, ya), (xb, yb)]).buffer(w / 2, cap_style=2)
        Pt(name=name, t='prism', r=ring(g), z0=z0, z1=z1, c=c, a=0.05, y=y, **({'d': d} if d is not None else {}))

# ---------- Colosseo (70-80 d.C.; terremoto del 1349: crolla il lato sud dell'anello esterno) ----------
cx, cy = L(41.8902, 12.4922); A = 13
clear.append(ring(affinity.rotate(affinity.scale(Point(cx, cy).buffer(1, 24), 100, 84), A, origin=(cx, cy))))
Pt(name='Colosseum', t='prism', r=ring(affinity.rotate(affinity.scale(Point(cx, cy).buffer(1, 24), 40, 22), A, origin=(cx, cy))), z0=0, z1=1, c=SAND, a=0.05, y=72)
south = lambda t: math.sin(t) < -0.35
ellring('Colosseum', cx, cy, 94, 78, 40, 24, 0, 14, TRAV, 72, ang=A)
ellring('Colosseum', cx, cy, 94, 78, 52, 36, 14, 32, TRAV, 75, ang=A)
ellring('Colosseum', cx, cy, 94, 78, 70, 54, 32, 48, TRAV, 79, ang=A, dsel=lambda t: 1349.2 if south(t) else None)
lab('Colosseum', cx, cy, 52, 72)

# ---------- Circo Massimo (-329 legno/pietra bassa, Cesare -46 grande; ultime corse 549) ----------
cx, cy = L(41.8861, 12.4851); A = -32
out_ = affinity.rotate(box(cx - 300, cy - 70, cx + 230, cy + 70).union(Point(cx + 230, cy).buffer(70)), A, origin=(cx, cy))
inn_ = affinity.rotate(box(cx - 270, cy - 40, cx + 230, cy + 40).union(Point(cx + 230, cy).buffer(40)), A, origin=(cx, cy))
clear.append(ring(out_.buffer(10)))
cav = out_.difference(inn_)
n = 40; L0 = 300 + 300
for i in range(n):
    sl = affinity.rotate(box(cx - 310 + i * L0 / n, cy - 80, cx - 310 + (i + 1) * L0 / n, cy + 80), A, origin=(cx, cy))
    q = cav.intersection(sl)
    for g in getattr(q, 'geoms', [q]):
        if g.geom_type == 'Polygon' and g.area > 5:
            Pt(name='Circus Maximus', t='prism', r=ring(g), z0=0, z1=6, c=SAND, a=0.05, y=-329, d=-46)
            Pt(name='Circus Maximus', t='prism', r=ring(g), z0=0, z1=18, c=TRAV, a=0.05, y=-46, d=1145)
            Pt(name='Circus Maximus', t='prism', r=ring(g), z0=0, z1=3, c=SAND, a=0.05, y=1145)
Pt(name='Circus Maximus', t='prism', r=ring(affinity.rotate(box(cx - 200, cy - 4, cx + 150, cy + 4), A, origin=(cx, cy))), z0=0, z1=3, c=MARBLE, a=0.05, y=-46, d=1145)
Pt(name='Obelisk', t='cone', cx=cx - 20, cy=cy, r0=1.6, r1=0.4, z0=3, z1=27, seg=4, c=MARBLE, a=0.05, y=-10, d=1587)
lab('Circus Maximus', cx, cy, 22, -329)

# ---------- Campidoglio e Foro ----------
cx, cy = L(41.8925, 12.4818)
g = block('Temple of Jupiter', cx, cy, 62, 53, 0, 6, TRAV, -509, d=455, ang=-10); clear.append(ring(g.buffer(5)))
block('Temple of Jupiter', cx, cy, 58, 49, 6, 26, MARBLE, -507, d=455, ang=-10, roof=TILE, rh=9)
lab('Temple of Jupiter', cx, cy, 36, -509, 455)
for nm, la, lo, w, h, y0, d in [('Temple of Saturn', 41.8925, 12.4843, 22, 40, -497, 1200), ('Basilica Julia', 41.8921, 12.4849, 101, 49, -46, 410),
                                ('Temple of Castor', 41.8917, 12.4857, 32, 50, -484, 900), ('Curia', 41.8930, 12.4853, 27, 21, -44, None),
                                ('Temple of Venus and Rome', 41.8908, 12.4900, 66, 145, 135, 850)]:
    x, y = L(la, lo); g = block(nm, x, y, w, h, 0, 18, MARBLE, y0, d=d, ang=-35, roof=TILE, rh=6); clear.append(ring(g.buffer(3)))
for nm in ('Basilica Julia', 'Temple of Venus and Rome'): pass
x, y = L(41.8919, 12.4884); g = block('Basilica of Maxentius', x, y, 100, 65, 0, 35, BRICK, 308, d=847); clear.append(ring(g.buffer(4)))
block('Basilica of Maxentius', x, y, 100, 30, 0, 25, BRICK, 847)
lab('Basilica of Maxentius', x, y, 40, 308)
x, y = L(41.8883, 12.4868); g = block('Imperial Palace', x, y, 170, 120, 0, 26, BRICK, 92, d=600, ang=-30); clear.append(ring(g.buffer(5)))
block('Imperial Palace', x, y, 140, 90, 0, 8, BRICK, 600, ang=-30)
lab('Palatine Palace', x, y, 30, 92, 600)
x, y = L(41.8892, 12.4875); lab('Palatine Hill', x, y, 20, -753, 92)
x, y = L(41.8958, 12.4843); Pt(name="Trajan's Column", t='cyl', cx=x, cy=y, rad=2.2, z0=0, z1=38, seg=10, c=MARBLE, a=0.05, y=113)
lab("Trajan's Column", x, y, 40, 113)
x, y = L(41.8955, 12.4858); g = block("Trajan's Market", x, y, 120, 50, 0, 22, BRICK, 107, ang=-40); clear.append(ring(g.buffer(3)))

# ---------- Campo Marzio ----------
x, y = L(41.8986, 12.4769)
block('Pantheon of Agrippa', x, y + 15, 40, 25, 0, 20, MARBLE, -27, d=110, roof=TILE, rh=7)
Pt(name='Pantheon', t='cyl', cx=x, cy=y - 10, rad=29, z0=0, z1=30, seg=28, c=TRAV, a=0.05, y=118)
Pt(name='Pantheon', t='dome', cx=x, cy=y - 10, rad=29, z0=30, hz=17, c=LEAD, a=0.05, y=125)
block('Pantheon', x, y + 27, 34, 16, 0, 24, MARBLE, 120, roof=TILE, rh=6)
clear.append(ring(Point(x, y).buffer(48)))
lab('Pantheon', x, y - 10, 50, 118)
x, y = L(41.8919, 12.4799)
th = ellring('Theatre of Marcellus', x, y, 65, 65, 32, 32, 0, 32, TRAV, -13, ang=0, keep=lambda t: math.sin(t) > 0.05)
clear.append(ring(Point(x, y).buffer(68)))
lab('Theatre of Marcellus', x, y + 40, 36, -13)
x, y = L(41.9060, 12.4763)
Pt(name='Mausoleum of Augustus', t='cyl', cx=x, cy=y, rad=44, z0=0, z1=12, seg=32, c=TRAV, a=0.05, y=-28)
Pt(name='Mausoleum of Augustus', t='cone', cx=x, cy=y, r0=40, r1=12, z0=12, z1=40, seg=32, c=GREEN, a=0.05, y=-26, d=410)
clear.append(ring(Point(x, y).buffer(48)))
lab('Mausoleum of Augustus', x, y, 44, -28)

# ---------- Mausoleo di Adriano -> Castel Sant'Angelo ----------
x, y = L(41.9031, 12.4663)
block('Castel Sant\'Angelo', x, y, 84, 84, 0, 15, TRAV, 135)
Pt(name="Castel Sant'Angelo", t='cyl', cx=x, cy=y, rad=32, z0=15, z1=33, seg=28, c=TRAV, a=0.05, y=137)
Pt(name="Castel Sant'Angelo", t='cyl', cx=x, cy=y, rad=14, z0=33, z1=46, seg=16, c=BRICK, a=0.05, y=1500)
clear.append(ring(Point(x, y).buffer(65)))
lab("Hadrian's Mausoleum", x, y, 40, 135, 590); lab("Castel Sant'Angelo", x, y, 50, 590)

# ---------- Terme ----------
x, y = L(41.8790, 12.4925); g = block('Baths of Caracalla', x, y, 220, 114, 0, 38, BRICK, 212, d=537, ang=-38); clear.append(ring(g.buffer(6)))
block('Baths of Caracalla', x, y, 200, 100, 0, 16, BRICK, 537, ang=-38)
lab('Baths of Caracalla', x, y, 42, 212)
x, y = L(41.9030, 12.4980); g = block('Baths of Diocletian', x, y, 240, 150, 0, 30, BRICK, 298, d=537, ang=-45); clear.append(ring(g.buffer(6)))
block('Baths of Diocletian', x, y, 110, 60, 0, 28, BRICK, 537, ang=-45)
lab('Baths of Diocletian', x, y, 34, 298)

# ---------- San Pietro: antica basilica (326-1506), nuova (1506-1626), cupola 1590, colonnato 1656-67 ----------
x, y = L(41.9022, 12.4539)
block("Old St Peter's", x, y, 120, 64, 0, 32, BRICK, 326, d=1506, roof=TILE, rh=12)
lab("Old St Peter's", x, y, 46, 326, 1506)
# croce latina: navata lunga verso est (facciata a est), transetto, cupola sull'incrocio
block("St Peter's Basilica", x - 5, y, 186, 58, 0, 46, TRAV, 1506, roof=LEAD, rh=6)
block("St Peter's Basilica", x - 55, y, 70, 137, 0, 46, TRAV, 1546, roof=LEAD, rh=6)
block("St Peter's Basilica", x + 85, y, 12, 115, 0, 48, TRAV, 1612)
Pt(name="St Peter's Basilica", t='cyl', cx=x - 55, cy=y, rad=26, z0=46, z1=78, seg=28, c=TRAV, a=0.05, y=1585)
Pt(name="St Peter's Basilica", t='dome', cx=x - 55, cy=y, rad=24, z0=78, hz=40, c=LEAD, a=0.05, y=1590)
Pt(name="St Peter's Basilica", t='cone', cx=x - 55, cy=y, r0=5, r1=0.5, z0=117, z1=136, seg=12, c=LEAD, a=0.05, y=1592)
clear.append(ring(rect(x, y, 200, 150).buffer(8)))
lab("St Peter's Basilica", x - 55, y, 140, 1506)
px, py = L(41.9022, 12.4573)
ellring("St Peter's Square", px, py, 120, 98, 104, 82, 0, 18, TRAV, 1660, n=56, keep=lambda t: abs(math.sin(t)) > 0.45)
lab("St Peter's Square", px, py, 22, 1660)

# ---------- mura ----------
aur = [L(a, b) for a, b in AURELIAN] + [L(*AURELIAN[0])]
wall('Aurelian Walls', aur, 0, 8, BRICK, 271, w=4)
wall('Aurelian Walls', aur, 8, 16, BRICK, 401, w=4)
ser = [L(a, b) for a, b in SERVIAN] + [L(*SERVIAN[0])]
wall('Servian Wall', ser, 0, 10, TRAV, -378, d=300, w=4)
x, y = L(41.9093, 12.5016); lab('Aurelian Walls', x, y, 20, 271)
x, y = L(41.9030, 12.4900); lab('Servian Wall', x, y, 16, -378, 300)

# ---------- Roma moderna ----------
x, y = L(41.8946, 12.4831); g = block('Vittoriano', x, y, 135, 70, 0, 20, WHITE, 1885); clear.append(ring(g.buffer(6)))
block('Vittoriano', x, y - 10, 115, 30, 20, 70, WHITE, 1905)
lab('Vittoriano', x, y, 75, 1885)
x, y = L(41.9341, 12.4547)
ellring('Stadio Olimpico', x, y, 140, 100, 95, 55, 0, 25, '#d8d8d4', 1953, ang=0)
clear.append(ring(affinity.scale(Point(x, y).buffer(1, 24), 145, 105)))
lab('Stadio Olimpico', x, y, 30, 1953)
x, y = L(41.8364, 12.4659); g = block('Square Colosseum (EUR)', x, y, 52, 52, 0, 68, WHITE, 1938); clear.append(ring(g.buffer(4)))
lab('EUR', x, y, 72, 1938)
x, y = L(41.9009, 12.5013); g = block('Termini Station', x, y, 230, 50, 0, 16, '#d8d4c8', 1950, ang=-55); clear.append(ring(g.buffer(4)))
lab('Termini Station', x, y, 20, 1950)

json.dump({'parts': parts, 'clear': clear, 'labels': labels}, open(f'{DATA}/landmarks.json', 'w'))
print('[landmarks] parti', len(parts), 'impronte libere', len(clear), 'etichette', len(labels))
