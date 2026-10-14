# Strato storico di New York: gli edifici "predecessori" demoliti e sostituiti da quelli di oggi.
# Idea: ogni lotto oggi costruito era gia' urbanizzato da un certo anno (fronte di urbanizzazione storico).
# Se l'edificio attuale e' molto piu' recente, sullo stesso lotto c'erano case dell'epoca: nascono con il fronte
# e spariscono quando arriva l'edificio moderno. Uscita: <dir>/hist.json [{"r", "h", "y", "d"}]
import json, math, random, sys
from shapely.geometry import Polygon, Point, box
from shapely import affinity

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data'
os_ = __import__('os'); os_.environ.setdefault('CITY_DATA', DATA)
LAT0, LON0 = 40.758, -73.985
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
lat = lambda y: LAT0 + y / KY; lon = lambda x: LON0 + x / KX

def interp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a)
    return pts[-1][1]

# Manhattan: anno di urbanizzazione in funzione della latitudine (dalle mappe storiche: Castello 1660, Ratzer 1767,
# Taylor-Roberts 1797, Commissioners 1811, Colton 1836, Dripps 1852, Bromley 1879, Sanborn 1890-1910). Approssimato.
MAN = [(40.7025, 1626), (40.7065, 1660), (40.7105, 1720), (40.7140, 1767), (40.7190, 1797), (40.7250, 1820),
       (40.7330, 1836), (40.7450, 1852), (40.7600, 1865), (40.7800, 1879), (40.8000, 1890), (40.8250, 1902), (40.8500, 1912), (40.8800, 1925)]
# Brooklyn e Queens occidentale: distanza (km) dall'approdo del traghetto di Fulton (1814 il primo a vapore)
FERRY = (40.7036, -73.9945)
BK = [(0.0, 1800), (1.0, 1825), (2.0, 1845), (3.5, 1860), (5.0, 1875), (6.5, 1890), (8.0, 1905), (10.0, 1920)]

import os
_MAN = None
def _man_poly():
    global _MAN
    if _MAN is None:
        _MAN = False
        for d in ('data', os.environ.get('CITY_DATA', '')):
            f = os.path.join(d, 'boroughs.json')
            if d and os.path.exists(f):
                from shapely.ops import unary_union
                from shapely.prepared import prep
                bj = json.load(open(f)); k = [n for n in bj if n.lower() == 'manhattan']
                if k: _MAN = prep(unary_union([Polygon(r).buffer(0) for r in bj[k[0]]]).buffer(60))
    return _MAN
def urban_year(x, y):
    la, lo = lat(y), lon(x); mp = _man_poly()
    if mp: manhattan = mp.contains(Point(x, y)) and la > 40.6995   # escluse Governors e Liberty Island
    else: manhattan = lo < -73.975 + (la - 40.70) * 0.6 and lo > -74.025 and la > 40.70   # ripiego approssimato
    wob = 9 * math.sin(x / 170.0) + 7 * math.sin(y / 230.0 + x / 410.0)   # fronte irregolare, non una linea dritta
    if manhattan: return interp(la, MAN) + wob
    d = math.hypot((la - FERRY[0]) * 111.0, (lo - FERRY[1]) * 84.3)
    return interp(d, BK) + wob

def era_height(u, rnd):
    if u < 1800: return rnd.uniform(6.5, 10)       # case di legno e mattoni, 2-3 piani
    if u < 1850: return rnd.uniform(9, 14)         # case a schiera federali e greek revival, 3-4 piani
    if u < 1890: return rnd.uniform(12, 19)        # brownstone e tenement, 4-5 piani
    return rnd.uniform(15, 24)                     # tenement "new law", 5-7 piani

def split(poly, cell=14.0):
    # lotti grandi: divisi in case di larghezza tipica newyorkese (25 piedi ~ 7.6 m) lungo l'orientamento del lotto
    if poly.area < 450: return [poly]
    mrr = poly.minimum_rotated_rectangle; c = list(mrr.exterior.coords)
    ang = math.degrees(math.atan2(c[1][1] - c[0][1], c[1][0] - c[0][0]))
    p0 = affinity.rotate(poly, -ang, origin=poly.centroid); x0, y0, x1, y1 = p0.bounds; out = []
    w, d = 7.6, cell * 1.6
    yy = y0
    while yy < y1:
        xx = x0
        while xx < x1:
            q = p0.intersection(box(xx + 0.3, yy + 0.3, xx + w - 0.3, yy + d - 0.3))
            if not q.is_empty and q.area > 20:
                for g in (q.geoms if hasattr(q, 'geoms') else [q]):
                    if isinstance(g, Polygon) and g.area > 20: out.append(affinity.rotate(g, ang, origin=poly.centroid))
            xx += w
        yy += d
    return out or [poly]

def build(DATA, urban_year, era_height=era_height, seed=11):
    blds = json.load(open(f'{DATA}/buildings.json')); rnd = random.Random(seed); out = []
    for b in blds:
        try: p = Polygon(b['r'])
        except Exception: continue
        if not p.is_valid or p.area < 15: continue
        c = p.centroid; u = urban_year(c.x, c.y) + rnd.uniform(-6, 10)
        if b['y'] < u + 25: continue   # l'edificio di oggi e' tra i primi del lotto: nessun predecessore
        for q in split(p):
            born = u + rnd.uniform(0, 12); died = b['y'] - rnd.uniform(0.3, 2.0)
            if died - born < 8: continue
            ring = [[round(x, 2), round(yv, 2)] for x, yv in list(q.exterior.coords)[:-1]]
            # seconda generazione: le case pre-1830 sostituite da edifici dell'800 prima dell'edificio attuale
            if born < 1830 and died > 1885:
                swap = rnd.uniform(max(born + 25, 1835), 1875)
                out.append({'r': ring, 'h': round(era_height(born, rnd), 1), 'y': int(born), 'd': round(swap - 0.5, 1)})
                out.append({'r': ring, 'h': round(era_height(swap, rnd), 1), 'y': int(swap), 'd': round(died, 1)})
            else:
                out.append({'r': ring, 'h': round(era_height(born, rnd), 1), 'y': int(born), 'd': round(died, 1)})
    json.dump(out, open(f'{DATA}/hist.json', 'w'))
    print(f'[hist] {len(out)} predecessori da {len(blds)} edifici attuali', flush=True)

if __name__ == '__main__':
    build(DATA, urban_year)
