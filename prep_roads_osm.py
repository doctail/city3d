# Strade (e ferrovie) di una citta' da un estratto OSM .pbf (download.openstreetmap.fr, regionale) -> DATA/roads.json
# Stesso formato e stesso metodo di fetch_dk_roads.py (Copenaghen): nastri per segmento, anno = hist_<citta>.urban_year + 2 (ferrovie >= 1847),
# unione per anno + triangolazione vincolata. Solo segmenti con il punto medio su terra (land.json); niente tunnel; ponti/cavalcavia restano nastri
# se su terra (i ponti sull'acqua sono bridges.json, a parte). Strade senza nessun edificio entro 400 m: scartate (tranne motorway/trunk e ferrovie),
# cosi' fuori dall'area del catasto non appaiono strade senza case. Anno > 2026 (nessuna urbanizzazione prevista): scartata.
# Uso: python prep_roads_osm.py city_X.json file.osm.pbf DATA_DIR   (DATA_DIR con buildings.json e land.json; CITY_DATA=DATA_DIR per hist_rotterdam)
import json, math, os, sys, collections
import numpy as np, shapely, osmium
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.prepared import prep
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CFG, PBF, DATA = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
os.environ.setdefault('CITY_DATA', DATA)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 9000) + 1500
hist = __import__(CFG['hist']); urban_year = hist.urban_year
def log(*a): print('[roads_osm]', *a, flush=True)
W = {'motorway': 22, 'trunk': 18, 'primary': 16, 'secondary': 13, 'tertiary': 10, 'residential': 7, 'living_street': 6, 'unclassified': 7,
     'pedestrian': 7, 'motorway_link': 9, 'trunk_link': 9, 'primary_link': 9, 'secondary_link': 8, 'tertiary_link': 7}
RAIL = {'rail': 8, 'light_rail': 6}
lr = json.load(open(os.path.join(DATA, 'land.json')))
LG = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in lr]); LP = prep(LG)
B = json.load(open(os.path.join(DATA, 'buildings.json')))
bxy = np.array([[sum(p[0] for p in o['r']) / len(o['r']), sum(p[1] for p in o['r']) / len(o['r'])] for o in B]); bt = cKDTree(bxy)
raw = []; stat = collections.Counter()
fp = osmium.FileProcessor(PBF, osmium.osm.NODE | osmium.osm.WAY).with_locations().with_filter(osmium.filter.KeyFilter('highway', 'railway'))
for w in fp:
    if not hasattr(w, 'nodes'): continue
    t = w.tags; hw = t.get('highway'); rw = t.get('railway')
    if t.get('tunnel') not in (None, 'no') or t.get('layer', '0').lstrip('-').isdigit() and int(t.get('layer', '0')) < 0: stat['tunnel'] += 1; continue
    if hw in W: wd, rail = W[hw], 0
    elif rw in RAIL and t.get('service') is None: wd, rail = RAIL[rw], 1
    else: stat['tipo_saltato'] += 1; continue
    try: tw = float((str(t.get('width', '')).split() or [''])[0].replace(',', '.'))
    except ValueError: tw = 0
    if tw and not rail: wd = min(30.0, max(4.0, tw))
    try: pts = [((n.lon - LON0) * KX, (n.lat - LAT0) * KY) for n in w.nodes]
    except osmium.InvalidLocationError: stat['nodi_mancanti'] += 1; continue
    if len(pts) < 2 or all(abs(x) > R or abs(y) > R for x, y in pts): stat['fuori_area'] += 1; continue
    raw.append((pts, wd, rail, hw or rw))
log('way letti', len(raw), dict(stat))
quads = collections.defaultdict(list); st2 = collections.Counter()
for pts, wd, rail, typ in raw:
    g = LineString(pts)
    if not g.is_valid or g.length < 2: continue
    c = g.interpolate(0.5, normalized=True); y = urban_year(c.x, c.y) + 2
    if rail: y = max(y, 1847)
    if y > 2026: st2['anno_oltre_2026'] += 1; continue
    if not rail and typ not in ('motorway', 'trunk', 'motorway_link', 'trunk_link') and not bt.query_ball_point([c.x, c.y], 400): st2['senza_edifici_400m'] += 1; continue
    y = int(max(y, 1100)); cs = list(g.simplify(1.0).coords)
    for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
        dl = math.hypot(x1 - x0, y1 - y0)
        if dl < 1: continue
        ux, uy = (x1 - x0) / dl, (y1 - y0) / dl; e = wd / 2; nx, ny = -uy * e, ux * e
        ax, ay = x0 - ux * e * 0.5, y0 - uy * e * 0.5; bx, by = x1 + ux * e * 0.5, y1 + uy * e * 0.5
        if abs(x0 + x1) / 2 > R or abs(y0 + y1) / 2 > R: continue   # fuori dal riquadro radius_m + 1,5 km
        if not LP.contains(Point((x0 + x1) / 2, (y0 + y1) / 2)): st2['mezzeria_in_acqua'] += 1; continue
        quads[(y, rail)].append(Polygon([(ax + nx, ay + ny), (ax - nx, ay - ny), (bx - nx, by - ny), (bx + nx, by + ny)]))
log('scarti', dict(st2), 'gruppi anno', len(quads))
roads = []; done = Polygon()
for (y, rl), ps in sorted(quads.items()):
    u = unary_union(ps).simplify(0.3).difference(done); done = done.union(u)
    for q in (u.geoms if hasattr(u, 'geoms') else [u]):
        if not isinstance(q, Polygon) or q.area < 5: continue
        for tr in shapely.constrained_delaunay_triangles(q).geoms:
            if tr.area > 0.05: roads.append({'r': [[round(x, 2), round(v, 2)] for x, v in list(tr.exterior.coords)[:-1]], 'y': int(y), 'rail': rl})
json.dump(roads, open(os.path.join(DATA, 'roads.json'), 'w'), separators=(',', ':'))
yy = [r['y'] for r in roads]; xs = [p[0] for r in roads for p in r['r']]; ys = [p[1] for r in roads for p in r['r']]
log(f'roads.json: {len(roads)} triangoli ({sum(r["rail"] for r in roads)} ferrovia); anni {min(yy)}..{max(yy)} mediana {int(np.median(yy))}; bbox x {min(xs):.0f}..{max(xs):.0f} y {min(ys):.0f}..{max(ys):.0f}; {os.path.getsize(os.path.join(DATA, "roads.json")) / 1e6:.1f} MB')
