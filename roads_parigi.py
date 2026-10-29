# Parigi: strade e ferrovie da OSM -> DATA/roads.json per build_render.py (nastri chiari sul suolo, comparsa per anno).
# Regole (REGIA.md, "corridoi vuoti"; brief Parigi Fase 1):
#  - strada esistente nel 1830 o in zona di nuova urbanizzazione: anno = urbanizzazione della zona (hist_parigi.urban_year) + 2
#  - strada APERTA SVENTRANDO (il tratto passa dentro un isolato di Vasserot 1810-1836, lontano dalle vie di allora): compare
#    quando spariscono le case di Vasserot che attraversa (stessa data dei predecessori di hist.json: niente corridoi vuoti e
#    niente strade sopra le case). Senza case: decreto della via (paris_voies, come hist_parigi.street_years), poi 1852-1870.
#  - ferrovie: dal 1837 (Paris-Saint-Germain) / urbanizzazione; Petite Ceinture e linee: max(urbanizzazione, 1840)
#  - Boulevard Peripherique: GRADUALE 1960 -> 1973 per angolo (scheda B012 e' DA MEMORIA: mai BRUSCO); altre autostrade 1965 [Guessing]
#  - ponti: NON qui (bridges_parigi.py, scheda G). I tratti di strada sull'acqua sono saltati.
# Uso: python roads_parigi.py RAW_DIR DATA_DIR      (dopo prep_parigi.py e hist_parigi.py)
import json, math, os, re, sys, gzip, random
import numpy as np, geopandas as gpd, shapely
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import hist_parigi as H
from tools.alpage import Alpage

RAW, DATA = sys.argv[1], sys.argv[2]
CFG = json.load(open(os.path.join(HERE, 'city_parigi.json')))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 8000)
ZONES = [((z['lon'] - LON0) * KX, (z['lat'] - LAT0) * KY, z['r_m']) for z in CFG.get('extra_zones', [])]
def log(*a): print('[roads_parigi]', *a, flush=True)
def loc(g): return shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY])
def inside(x, y): return x * x + y * y < R * R or any((x - zx) ** 2 + (y - zy) ** 2 < zr * zr for zx, zy, zr in ZONES)
os.environ['CITY_DATA'] = DATA

W = {'motorway': 24, 'trunk': 18, 'primary': 16, 'secondary': 13, 'tertiary': 10, 'residential': 8, 'living_street': 6,
     'unclassified': 7, 'pedestrian': 8, 'motorway_link': 9, 'trunk_link': 9, 'primary_link': 9, 'secondary_link': 8, 'tertiary_link': 7}
r = gpd.read_file(gzip.open(f'{RAW}/osm_roads.geojson.gz'))
r['geometry'] = [loc(g) for g in r.geometry]
land = json.load(open(f'{DATA}/land.json'))
LG = unary_union([Polygon(q['ext'], q.get('holes', [])).buffer(0) for q in land]); LP = prep(LG)

A = Alpage(os.path.join(RAW, 'alpage'), CFG)
VIL = prep(unary_union(A.layer('Vasserot_1_Ilots').geometry.buffer(0).values).buffer(-2))   # isolati del 1830 (case, cortili, giardini)
VV = unary_union(A.layer('Vasserot_1_Voies').geometry.values).buffer(6); VVp = prep(VV)       # vie del 1830 (+6 m)
OUT91 = unary_union(A.layer('Ilots_1791').geometry.buffer(0).values).convex_hull.buffer(100); O91 = prep(OUT91)
# fuori dalla Parigi del 1791 le vie di oggi che attraversano i villaggi comparivano come strisce bianche isolate nei campi (prova
# 1600, 28 ott): le vie dei villaggi non entrano prima del XVIII secolo; le grandi strade (primary/secondary/trunk) dal 1700.
# [Guessing] dichiarato: soglie di regia, non date per singola via.
OUT_MAJOR, OUT_MINOR = 1700, 1780
hist = json.load(open(f'{DATA}/hist.json'))
# vie legate alle case (prova 1850/1880, 29 ott): nei faubourg la zona risultava urbanizzata decenni prima delle case vere e le
# vie comparivano come una griglia vuota. Una via di zona non compare prima della casa piu' vecchia entro 30 m (meno 3 anni).
_bl = json.load(open(f'{DATA}/buildings.json'))
_cx = np.array([np.mean([p[0] for p in o['r']]) for o in _bl + hist]); _cy = np.array([np.mean([p[1] for p in o['r']]) for o in _bl + hist])
_by = np.array([o['y'] for o in _bl + hist], float); del _bl
from scipy.spatial import cKDTree as _KD
_kd = _KD(np.c_[_cx, _cy])
def first_house(x0, y0, x1, y1):
    ii = set()
    for t in (0.0, 0.5, 1.0): ii.update(_kd.query_ball_point((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t), 30 + 0.5 * math.hypot(x1 - x0, y1 - y0) * (t == 0.5)))
    return float(_by[list(ii)].min()) if ii else None
hp = [Polygon(h_['r']).buffer(0) for h_ in hist]; hd = np.array([h_.get('d', 99999) for h_ in hist]); htree = STRtree(hp)
sg, sy = H.street_years(RAW, shapely); stree = STRtree(sg)
rnd = random.Random(5)
_default_cut = {}
def cut_year(seg, mid, name):
    """anno di apertura di un tratto aperto sventrando: ultima demolizione delle case di Vasserot che attraversa"""
    b = seg.buffer(3)
    ds = [hd[i] for i in htree.query(b) if hd[i] < 1990 and hp[i].intersects(b)]
    if ds: return max(ds) + 0.3, 'case'
    sh = [sy[i] for i in stree.query(mid) if sg[i].contains(mid)]
    if sh: return min(sh), 'decreto'
    k = name or f'{int(mid.x // 300)}_{int(mid.y // 300)}'
    if k not in _default_cut: _default_cut[k] = rnd.uniform(1852, 1870)
    return _default_cut[k], 'generico'

PERI_A0 = None
def peri_year(x, y):   # Peripherique: GRADUALE 1960 -> 1973 lungo l'anello (inizio a sud, Porte de la Plaine ~1960)
    a = (math.degrees(math.atan2(y, x)) + 90) % 360
    return 1960 + 13 * a / 360

roads = []; cnt = {'urban': 0, 'case': 0, 'decreto': 0, 'generico': 0, 'rail': 0, 'peri': 0, 'auto': 0}
for g, hw, rw, br, tn, nm in zip(r.geometry, r['highway'], r['railway'], r['bridge'], r['tunnel'], r['name']):
    if g is None or g.is_empty or g.geom_type != 'LineString': continue
    if isinstance(tn, str) and tn not in ('no',): continue
    if isinstance(br, str) and br not in ('no',): continue          # ponti e cavalcavia: bridges_parigi.py
    israil = isinstance(rw, str) and rw in ('rail', 'light_rail', 'tram', 'narrow_gauge')
    w = 9 if israil else W.get(hw if isinstance(hw, str) else '', 0)
    if not w: continue
    name = nm if isinstance(nm, str) else ''
    cs = list(g.simplify(1.0).coords)
    for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
        dl = math.hypot(x1 - x0, y1 - y0)
        if dl < 1: continue
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if not inside(mx, my): continue
        mid = Point(mx, my)
        if not LP.contains(mid): continue
        u = H.urban_year(mx, my)
        if israil: y = max(u + 2, 1840) if u < 9000 else 1860; cnt['rail'] += 1
        elif hw in ('motorway', 'motorway_link', 'trunk', 'trunk_link') and 'riph' in name: y = peri_year(mx, my); cnt['peri'] += 1
        elif hw in ('motorway', 'motorway_link', 'trunk', 'trunk_link') and u > 1900: y = max(u + 2, 1965); cnt['auto'] += 1
        elif VIL.contains(mid) and not VVp.contains(mid):
            y, how = cut_year(LineString([(x0, y0), (x1, y1)]), mid, name); cnt[how] += 1
        else:
            y = (u + 2) if u < 9000 else 1890; cnt['urban'] += 1
            fh = first_house(x0, y0, x1, y1)
            if fh is not None and fh - 3 > y: y = fh - 3; cnt['casa'] = cnt.get('casa', 0) + 1
            if not O91.contains(mid):
                y = max(y, OUT_MAJOR if hw in ('primary', 'secondary', 'trunk') else OUT_MINOR + 20 * rnd.random())
        ux, uy = (x1 - x0) / dl, (y1 - y0) / dl; e = w / 2; nx, ny = -uy * e, ux * e
        ax_, ay_ = x0 - ux * e * 0.5, y0 - uy * e * 0.5; bx_, by_ = x1 + ux * e * 0.5, y1 + uy * e * 0.5
        q = [(ax_ + nx, ay_ + ny), (ax_ - nx, ay_ - ny), (bx_ - nx, by_ - ny), (bx_ + nx, by_ + ny)]
        roads.append({'r': [[round(x, 1), round(yv, 1)] for x, yv in q], 'y': round(float(y), 1), 'rail': int(israil)})
log('segmenti:', len(roads), cnt)

# unione per anno intero e triangolazione vincolata (come Copenaghen: niente facce sovrapposte sullo stesso piano)
from collections import defaultdict
grp = defaultdict(list)
for r_ in roads: grp[(int(r_['y']), r_['rail'])].append(Polygon(r_['r']))
out = []; done_ = Polygon()
for (y_, rl), ps in sorted(grp.items()):
    u = unary_union(ps).simplify(0.3).difference(done_); done_ = done_.union(u)
    for q in (u.geoms if hasattr(u, 'geoms') else [u]):
        if not isinstance(q, Polygon) or q.area < 5: continue
        for t in shapely.constrained_delaunay_triangles(q).geoms:
            if t.area > 0.05: out.append({'r': [[round(x, 2), round(yv, 2)] for x, yv in list(t.exterior.coords)[:-1]], 'y': int(y_), 'rail': rl})
json.dump(out, open(f'{DATA}/roads.json', 'w'))
ys = np.array([o['y'] for o in out])
log('FATTO triangoli', len(out), '| per periodo:', {f'{a}-{b - 1}': int(((ys >= a) & (ys < b)).sum()) for a, b in ((1000, 1500), (1500, 1800), (1800, 1850), (1850, 1871), (1871, 1914), (1914, 1960), (1960, 2027))})
json.dump(cnt, open(f'{DATA}/roads_stats.json', 'w'))
