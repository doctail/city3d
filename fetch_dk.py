# Danimarca, passo 2 (in chat, gratis): dai dati grezzi del pod (data_dk.sh) al formato di build_render.py.
# Uso: python fetch_dk.py RAW_DIR DATA_DIR city_copenhagen.json
#   RAW_DIR: bbr_building.geojson (punti BBR INSPIRE), osm_buildings.geojson, osm_env.geojson
# Uscita: DATA/buildings.json [{"r", "h", "y", "k"}]  (k = tipo: res/anc/pub/ind, per i colori)
#         DATA/land.json (terra = lato sinistro della costa OSM, meno laghi e canali), DATA/parks.json
# Anno di un'impronta: punto BBR "principale" dentro l'impronta (non accessorio, superficie maggiore); senza punto o con anno
# sconosciuto (BBR 1000): mediana dei 6 vicini con anno. Altezza: OSM height > OSM livelli > piani BBR > tipo.
import json, math, sys, re
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union, polygonize, linemerge

RAW, DATA, CFG = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
import os; os.makedirs(DATA, exist_ok=True)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 9000); MINAREA = CFG.get('min_area_m2', 12)
def log(*a): print('[fetch_dk]', *a, flush=True)
def loc(g): return shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY])

# ---------- punti BBR ----------
cols = ['dateOfConstruction_dateOfEvent_anyPoint', 'conditionOfConstruction', 'currentUse', 'numberOfFloorsAboveGround', 'officialArea']
import pyogrio
p = pyogrio.read_dataframe(f'{RAW}/bbr_building.geojson', columns=cols)
p = p[p.conditionOfConstruction.isin(['functional', 'underConstruction'])].copy()
p['x'] = (p.geometry.x - LON0) * KX; p['y'] = (p.geometry.y - LAT0) * KY
p = p[(p.x ** 2 + p.y ** 2) < (R + 300) ** 2]
p['yr'] = pd.to_numeric(p.dateOfConstruction_dateOfEvent_anyPoint.astype(str).str[:4], errors='coerce')
p.loc[(p.yr <= 1000) | (p.yr > 2026), 'yr'] = np.nan
p['fl'] = pd.to_numeric(p.numberOfFloorsAboveGround, errors='coerce').fillna(0)
p['ar'] = pd.to_numeric(p.officialArea, errors='coerce').fillna(0)
p['anc'] = p.currentUse.isin(['ancillary', 'agriculture'])
log('punti BBR', len(p))

# ---------- impronte OSM ----------
b = gpd.read_file(f'{RAW}/osm_buildings.geojson')
b = b[b['building'].notna()].copy()
b['geometry'] = [loc(g) for g in b.geometry]; b = b.set_geometry('geometry').set_crs(None, allow_override=True)
c = b.geometry.centroid; b = b[(c.x ** 2 + c.y ** 2) < R ** 2].copy()
b['area'] = b.geometry.area; b = b[b['area'] >= MINAREA].copy()
b = b.reset_index(drop=True)
log('impronte', len(b))

pts = gpd.GeoDataFrame(p.drop(columns='geometry'), geometry=gpd.points_from_xy(p.x, p.y))
j = gpd.sjoin_nearest(pts, b[['geometry']], how='inner', max_distance=8, distance_col='d')
# punto principale: non accessorio prima, poi superficie maggiore, poi anno noto
j['rank'] = (~j.anc).astype(int) * 1e9 + j.ar + j.yr.notna() * 1e-3
main = j.sort_values('rank', ascending=False).drop_duplicates('index_right').set_index('index_right')
b['yr'] = main.yr.reindex(b.index)
b['fl'] = j[~j.anc].groupby('index_right').fl.max().reindex(b.index)
b['use'] = main.currentUse.reindex(b.index)
log('impronte con anno BBR', int(b.yr.notna().sum()))

# OSM start_date dove manca
def sd(v):
    m = re.search(r'(1[0-9]{3}|20[0-2][0-9])', str(v)) if v else None
    return float(m.group(1)) if m else np.nan
osm_sd = b['start_date'].map(sd) if 'start_date' in b else pd.Series(np.nan, index=b.index)
fill = b.yr.isna() & osm_sd.notna(); b.loc[fill, 'yr'] = osm_sd[fill]; log('anni da OSM start_date', int(fill.sum()))
# vicini
from scipy.spatial import cKDTree
cc = b.geometry.centroid; xy = np.c_[cc.x, cc.y]
known = b.yr.notna().values
tr = cKDTree(xy[known]); kv = b.yr.values[known]
miss = np.where(~known)[0]
_, ii = tr.query(xy[miss], k=6)
b.loc[b.index[miss], 'yr'] = np.median(kv[ii], axis=1).round()
b['imp'] = ~known
log('anni stimati dai vicini', len(miss))

# altezza
def num(v):
    try: return float(str(v).replace(',', '.').split(';')[0].replace('m', '').strip())
    except Exception: return np.nan
oh = b['height'].map(num) if 'height' in b else np.nan
ol = b['building:levels'].map(num) if 'building:levels' in b else np.nan
h = pd.Series(oh, index=b.index)
h = h.where(h.notna(), pd.Series(ol, index=b.index) * 3.2 + 1.5)
h = h.where(h.notna() & (h > 0), b.fl.where(b.fl > 0) * 3.1 + 1.5)
small = b['area'] < 40
h = h.where(h.notna(), np.where(small, 3.0, 8.0))
h = h.clip(3, CFG.get('max_h', 160))
b['h'] = h

def kind(u, a):
    u = str(u)
    if u in ('ancillary', 'agriculture') or a < 40: return 'anc'
    if u in ('industrial', 'trade'): return 'ind'
    if u in ('publicServices', 'office', 'commerceAndServices', 'residenceForCommunities'): return 'pub'
    return 'res'
out = []
for g, y, hh, u, a, imp in zip(b.geometry, b.yr, b.h, b.use, b['area'], b.imp):
    if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
    g = g.simplify(0.4)
    if g.is_empty or g.area < MINAREA: continue
    ring = [[round(x, 2), round(yy, 2)] for x, yy in list(g.exterior.coords)[:-1]]
    if len(ring) < 3: continue
    o = {'r': ring, 'h': round(float(hh), 1), 'y': int(y), 'k': kind(u, a)}
    if imp: o['i'] = 1
    out.append(o)
json.dump(out, open(f'{DATA}/buildings.json', 'w'))
ys = np.array([o['y'] for o in out]); hs = np.array([o['h'] for o in out])
log(f'FATTO edifici: {len(out)}, anni {ys.min()}..{ys.max()}, mediana {int(np.median(ys))}, altezza max {hs.max()} m')
for a_, b_ in ((1000, 1728), (1728, 1807), (1807, 1850), (1850, 1900), (1900, 1945), (1945, 1980), (1980, 2027)):
    log(f'  {a_}-{b_ - 1}: {int(((ys >= a_) & (ys < b_)).sum())}')

# ---------- terra: lato sinistro della costa (convenzione OSM), dentro la finestra nota ----------
e = gpd.read_file(f'{RAW}/osm_env.geojson')
e['geometry'] = [loc(g) for g in e.geometry]
coast = [g for g, n in zip(e.geometry, e.natural) if n == 'coastline']
cb = unary_union(coast).bounds
W = box(cb[0] + 200, cb[1] + 200, cb[2] - 200, cb[3] - 200)   # finestra dove la costa e' completa
merged = linemerge(unary_union(coast))
lines = list(merged.geoms) if hasattr(merged, 'geoms') else [merged]
faces = list(polygonize(unary_union(lines + [W.exterior]).intersection(W).union(W.exterior)))
vote = np.zeros(len(faces))
from shapely.strtree import STRtree
st = STRtree(faces)
for ln in lines:
    cs = np.asarray(ln.coords)
    for i in range(0, len(cs) - 1, 3):
        (x0, y0), (x1, y1) = cs[i], cs[i + 1]; L_ = math.hypot(x1 - x0, y1 - y0)
        if L_ < 1: continue
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2; nx, ny = -(y1 - y0) / L_, (x1 - x0) / L_   # normale a sinistra
        for s, d in ((1, 3.0), (-1, 3.0)):
            q = Point(mx + s * nx * d, my + s * ny * d)
            for fi in st.query(q, predicate='within'): vote[fi] += s
land_in = unary_union([f for f, v in zip(faces, vote) if v > 0])
log('facce costa', len(faces), 'terra', sum(1 for v in vote if v > 0))
# fuori finestra: Selandia a ovest (terra), Oresund a est (mare), costa svedese ~ x>26 km (terra all'orizzonte)
Lh = CFG.get('land_half_m', 60000)
outside = box(-Lh, -Lh, Lh, Lh).difference(W)
west = box(-Lh, -Lh, cb[0] + 3000, Lh)   # [Likely] a ovest della finestra solo terra
sweden = box(26500, -Lh, Lh, Lh)
land = unary_union([land_in, outside.intersection(unary_union([west, sweden]))])
# laghi, canali, fiumi interni
water = []
for g, pr in zip(e.geometry, e.itertuples()):
    nat = getattr(pr, 'natural', None); ww = getattr(pr, 'waterway', None); lu = getattr(pr, 'landuse', None)
    if g.geom_type in ('Polygon', 'MultiPolygon') and (nat == 'water' or lu in ('basin', 'reservoir')) and g.area > 1500: water.append(g.buffer(0))
    elif ww == 'canal' and g.geom_type == 'LineString': water.append(g.buffer(5, cap_style=2))
if water: land = land.difference(unary_union(water).buffer(0.5))
lr = []
for q in (land.geoms if hasattr(land, 'geoms') else [land]):
    if isinstance(q, Polygon) and q.area > 400:
        q = q.simplify(2.0)
        lr.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]],
                   'holes': [[[round(x, 1), round(y, 1)] for x, y in list(hh.coords)[:-1]] for hh in q.interiors if Polygon(hh).area > 300]})
json.dump(lr, open(f'{DATA}/land.json', 'w')); open(f'{DATA}/land_v3.ok', 'w').write('ok')
log('terra', len(lr), 'poligoni, acque interne', len(water))
# parchi
pk = []
for g, pr in zip(e.geometry, e.itertuples()):
    if getattr(pr, 'leisure', None) == 'park' and g.geom_type in ('Polygon', 'MultiPolygon') and g.area > 3000:
        for q in (g.geoms if hasattr(g, 'geoms') else [g]):
            q = q.simplify(1.5); pk.append([[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]])
json.dump(pk, open(f'{DATA}/parks.json', 'w')); log('parchi', len(pk))
