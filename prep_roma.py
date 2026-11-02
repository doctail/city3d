# Roma, dati per build_render.py (in chat, dal pacchetto dati_roma_slim.tgz del pod).
# Edifici di oggi da OSM; anno di costruzione per sezione di censimento ISTAT 2011 (E8..E16: numero di edifici per epoca),
# estratto a caso con le proporzioni della sezione; "prima del 1919" diviso per zona storica (hist_roma.pre1919_year).
# Uscite in DATA: buildings.json, roads.json, land.json, parks.json, dem.npz
# Uso: python prep_roma.py SLIM_DIR DATA_DIR city_roma.json
import json, math, sys, os, random, csv, glob
import numpy as np, shapefile, pyproj, rasterio
from shapely.geometry import shape, Polygon, Point, box, LineString
from shapely.ops import unary_union, transform as stransform
from shapely.strtree import STRtree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hist_roma as H

SRC, DATA, CFG = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
os.makedirs(DATA, exist_ok=True)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 9000)
def loc_xy(lon, lat): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def loc(g): return stransform(lambda x, y, z=None: ((np.asarray(x) - LON0) * KX, (np.asarray(y) - LAT0) * KY), g)
rnd = random.Random(7)
CLIP = box(-R, -R, R, R)

# ---------- ISTAT: sezioni con epoche ----------
EP = [('E8', 1600, 1918), ('E9', 1919, 1945), ('E10', 1946, 1960), ('E11', 1961, 1970), ('E12', 1971, 1980),
      ('E13', 1981, 1990), ('E14', 1991, 2000), ('E15', 2001, 2005), ('E16', 2006, 2011)]
cnt = {}
f = glob.glob(f'{SRC}/istat_dati/Sezioni*/R12_indicatori_2011_sezioni.csv')[0]
for row in csv.DictReader(open(f, encoding='latin-1'), delimiter=';'):
    try: v = [int(row[k] or 0) for k, _, _ in EP]
    except ValueError: continue
    if sum(v): cnt[int(row['SEZ2011'])] = v
utm = pyproj.Transformer.from_crs(32632, 4326, always_xy=True)
shp = shapefile.Reader(glob.glob(f'{SRC}/istat_basi/*/*.shp')[0])
fi = [f_[0] for f_ in shp.fields[1:]].index('SEZ2011')
sez_g, sez_v = [], []
bb_lon = (LON0 - (R + 2000) / KX, LON0 + (R + 2000) / KX); bb_lat = (LAT0 - (R + 2000) / KY, LAT0 + (R + 2000) / KY)
for sr in shp.iterShapeRecords():
    sid = int(sr.record[fi])
    if sid not in cnt: continue
    x0, y0, x1, y1 = sr.shape.bbox
    lo, la = utm.transform((x0 + x1) / 2, (y0 + y1) / 2)
    if not (bb_lon[0] < lo < bb_lon[1] and bb_lat[0] < la < bb_lat[1]): continue
    g = shape(sr.shape.__geo_interface__)
    g = stransform(lambda x, y, z=None: loc_xy(*utm.transform(x, y)), g).buffer(0)
    if g.is_empty: continue
    sez_g.append(g); sez_v.append(cnt[sid])
tree = STRtree(sez_g)
print('[prep] sezioni ISTAT', len(sez_g), flush=True)

def year_for(c):
    idx = tree.query(c, predicate='within') if hasattr(tree, 'query') else []
    if len(idx) == 0:
        idx = tree.query(c.buffer(80))
        if len(idx) == 0: return None
    v = sez_v[int(idx[0])]; tot = sum(v); u = rnd.random() * tot
    for (k, a, b), n in zip(EP, v):
        if u < n: break
        u -= n
    if k == 'E8': return H.pre1919_year(c.x, c.y, rnd)
    return rnd.uniform(a, b + 0.99)

def era_h(y, t):
    if t.get('height'):
        try: return float(str(t['height']).split()[0].replace(',', '.'))
        except ValueError: pass
    if t.get('building:levels'):
        try: return float(t['building:levels']) * 3.3 + 1.5
        except ValueError: pass
    if y < 1870: return rnd.uniform(11, 17)
    if y < 1919: return rnd.uniform(15, 21)
    if y < 1960: return rnd.uniform(16, 24)
    if y < 1990: return rnd.uniform(18, 28)
    return rnd.uniform(12, 22)

# ---------- edifici ----------
B = json.load(open(f'{SRC}/osm_buildings.geojson'))['features']
out = []; nnone = 0
for ft in B:
    t = ft['properties']
    if t.get('building') in ('roof', 'construction', 'ruins') or 'building:part' in t: continue
    g = loc(shape(ft['geometry']))
    if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
    if g.geom_type != 'Polygon' or g.area < CFG.get('min_area_m2', 12) or not CLIP.contains(g.centroid): continue
    g = g.simplify(0.6)
    c = g.centroid
    if H.in_water_or_ancient_park(c.x, c.y): continue
    y = year_for(c)
    if y is None: y = H.outside_year(c.x, c.y, rnd); nnone += 1
    ring = [[round(x, 2), round(yy, 2)] for x, yy in list(g.exterior.coords)[:-1]]
    if len(ring) < 3: continue
    out.append({'r': ring, 'h': round(min(era_h(y, t), 120), 1), 'y': round(y, 2)})
json.dump(out, open(f'{DATA}/buildings.json', 'w'))
ys = np.array([b['y'] for b in out])
print('[prep] edifici', len(out), 'senza sezione', nnone, 'per secolo:', {int(k): int(v) for k, v in zip(*np.unique((ys // 100) * 100, return_counts=True))}, flush=True)

# ---------- acqua, terra, parchi ----------
E = json.load(open(f'{SRC}/osm_env.geojson'))['features']
water, parks = [], []
for ft in E:
    p = ft['properties']; g = loc(shape(ft['geometry'])).buffer(0)
    if g.is_empty: continue
    if p.get('natural') == 'water' or p.get('waterway') == 'riverbank' or p.get('landuse') in ('basin', 'reservoir'):
        if g.area > 400: water.append(g)
    elif p.get('leisure') in ('park', 'garden') and g.area > 3000: parks.append(g)
W = unary_union(water).intersection(box(-R - 3000, -R - 3000, R + 3000, R + 3000))
HALF = CFG.get('land_half_m', 40000)
landg = box(-HALF, -HALF, HALF, HALF).difference(W)
land = []
for q in getattr(landg, 'geoms', [landg]):
    if q.geom_type != 'Polygon' or q.area < 100: continue
    q = q.simplify(1.0)
    land.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]],
                 'holes': [[[round(x, 1), round(y, 1)] for x, y in list(h.coords)[:-1]] for h in q.interiors if Polygon(h).area > 100]})
json.dump(land, open(f'{DATA}/land.json', 'w'))
pk = []
for g in parks:
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon' and q.area > 3000: pk.append([[round(x, 1), round(y, 1)] for x, y in list(q.simplify(2).exterior.coords)[:-1]])
json.dump(pk, open(f'{DATA}/parks.json', 'w'))
print('[prep] acqua', len(water), 'terra', len(land), 'parchi', len(pk), flush=True)

# ---------- strade: anno = primo edificio vicino (cella 120 m), vie consolari dall'anno di costruzione ----------
CELL = 120; cmin = {}
for b in out:
    k = (int(b['r'][0][0] // CELL), int(b['r'][0][1] // CELL)); cmin[k] = min(cmin.get(k, 9999), b['y'])
CONSOLARI = H.CONSOLARI
WID = {'motorway': 16, 'trunk': 14, 'primary': 11, 'secondary': 9, 'tertiary': 7.5, 'residential': 5.5, 'unclassified': 5,
       'living_street': 4, 'pedestrian': 5, 'service': 3.5, 'motorway_link': 7, 'trunk_link': 7, 'primary_link': 7, 'secondary_link': 6, 'tertiary_link': 6}
RD = json.load(open(f'{SRC}/osm_roads.geojson'))['features']
roads = []
KEEP = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'living_street', 'pedestrian',
        'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'service'}
for ft in RD:
    p = ft['properties']; hw = p.get('highway'); rail = 1 if p.get('railway') else 0
    if not rail and hw not in KEEP: continue
    if hw == 'service' and rnd.random() < 0.7: continue
    g = loc(shape(ft['geometry']))
    if g.geom_type != 'LineString' or not CLIP.intersects(g): continue
    g = g.simplify(1.5); pts = [[round(x, 1), round(y, 1)] for x, y in g.coords]
    w = 6.0 if rail else WID.get(hw, 5.0)
    nm = (p.get('name') or '')
    y = None
    for key, yc in CONSOLARI.items():
        if key in nm: y = yc; break
    if y is None:
        ks = [cmin.get((int(x // CELL) + dx, int(yy // CELL) + dy), 9999) for x, yy in pts[::max(1, len(pts) // 4)] for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        y = min(ks)
        if y >= 9999: y = 1960 if hw in ('motorway', 'trunk', 'primary', 'motorway_link', 'trunk_link') else 9999
        if rail: y = max(y, 1856)
    if y >= 9999: continue
    # nastri (poligoni) a tratti di ~250 m: build_render vuole anelli
    n_ = max(1, int(g.length // 250) + 1)
    for i in range(n_):
        seg = __import__('shapely').ops.substring(g, i * g.length / n_, (i + 1) * g.length / n_)
        if seg.length < 1: continue
        q = seg.buffer(w / 2, cap_style=2, join_style=2).simplify(0.5)
        if q.geom_type != 'Polygon' or q.area < 4 or q.intersects(W): continue   # niente strade sull'acqua (ponti: no)
        roads.append({'r': [[round(x, 1), round(yy, 1)] for x, yy in list(q.exterior.coords)[:-1]], 'y': round(y, 1), 'rail': rail})
json.dump(roads, open(f'{DATA}/roads.json', 'w'))
print('[prep] strade', len(roads), flush=True)

# ---------- rilievo: Copernicus 30 m, relativo al Tevere (~13 m), esagerato x1,6 ----------
tif = glob.glob(f'{SRC}/dem/*.tif')[0]
C = 30.0; X0 = Y0 = -(R + 3000); n = int(2 * (R + 3000) / C) + 1
gx, gy = np.meshgrid(X0 + np.arange(n) * C, Y0 + np.arange(n) * C)
lon = LON0 + gx / KX; lat = LAT0 + gy / KY
with rasterio.open(tif) as ds:
    inv = ~ds.transform; cc_, rr_ = inv * (lon.ravel(), lat.ravel())
    A = ds.read(1); rr = np.clip(np.floor(rr_).astype(int), 0, A.shape[0] - 1); cc = np.clip(np.floor(cc_).astype(int), 0, A.shape[1] - 1)
    Z = A[rr, cc].reshape(gx.shape).astype(np.float64)
from scipy import ndimage
Z = ndimage.gaussian_filter(Z, 1.2)
base = CFG.get('dem_base', 14.0); EXAG = CFG.get('dem_exag', 1.6)
D = EXAG * np.maximum(Z - base, 0)
# niente rilievo sopra l'acqua e vicino al bordo del mondo
from shapely import contains_xy
wet = contains_xy(W, gx, gy); D[wet] = 0
D = ndimage.gaussian_filter(D, 0.8)
np.savez_compressed(f'{DATA}/dem.npz', D=D.astype(np.float32), x0=X0, y0=Y0, cell=C)
print('[prep] rilievo max %.0f m (esagerato)' % D.max(), flush=True)
