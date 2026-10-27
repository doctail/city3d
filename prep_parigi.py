# Parigi, passo 2 (in chat, gratis): dai dati grezzi dei pod (data_fr.sh, data_fr2.sh) al formato di build_render.py.
# Uso: python prep_parigi.py RAW_DIR DATA_DIR city_parigi.json
#   RAW_DIR: osm_buildings.geojson.gz, osm_env.geojson.gz (data_fr.sh), extra/bdnb.geojson.gz (data_fr2.sh, con hmax e tetti)
# Uscita: DATA/buildings.json [{"r", "h", "y", "k", "i"?, "rf"?, "src"?}], DATA/land.json, DATA/parks.json, DATA/prep_stats.json
# Forme: impronte OSM (piu' fini dei gruppi BDNB: 283.000 contro 177.000 nel raggio). Attributi: il gruppo BDNB che contiene
# il punto interno dell'impronta (anno dei Fichiers fonciers, altezza BD TOPO, materiale del tetto).
# Anni tondi: il catasto mette 1900, 1930... quando non sa (a Parigi il 55% degli anni e' multiplo di 10 contro il 10% atteso):
# si distribuiscono a caso nel loro intorno (+-5 anni per i multipli di 10, +-20 per i multipli di 50 prima del 1850), altrimenti
# nel video la citta' cresce a ondate ogni 10 anni. L'anno originale resta in "y0" solo se cambiato (per i controlli).
import json, math, os, random, re, sys, gzip
import numpy as np, pandas as pd, geopandas as gpd, shapely
from scipy.spatial import cKDTree
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union

RAW, DATA, CFG = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
os.makedirs(DATA, exist_ok=True)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 8000); MINAREA = CFG.get('min_area_m2', 12)
ZONES = [((z['lon'] - LON0) * KX, (z['lat'] - LAT0) * KY, z['r_m']) for z in CFG.get('extra_zones', [])]
def log(*a): print('[prep_parigi]', *a, flush=True)
def loc(g): return shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY])
def inside(x, y):
    m = x * x + y * y < R * R
    for zx, zy, zr in ZONES: m = m | ((x - zx) ** 2 + (y - zy) ** 2 < zr * zr)
    return m
def rd(p): return gpd.read_file(gzip.open(p)) if p.endswith('.gz') else gpd.read_file(p)
rnd = random.Random(3)

# ---------- impronte OSM ----------
b = rd(f'{RAW}/osm_buildings.geojson.gz')
b = b[b['building'].notna() | b.get('building:part', pd.Series(index=b.index)).notna()].copy()
b = b[b['building'].notna()].copy()            # le building:part (pezzi di tetto) duplicherebbero l'impronta
b['geometry'] = [loc(g) for g in b.geometry]; b = b.set_geometry('geometry').set_crs(None, allow_override=True)
c = b.geometry.representative_point(); b = b[inside(c.x.values, c.y.values)].copy()
b['area'] = b.geometry.area; b = b[b['area'] >= MINAREA].reset_index(drop=True)
ICONS_OUT = CFG.get('icons_out', ['Tour Eiffel'])          # strutture che non sono edifici o che si modellano a mano
nm = b['name'].fillna('') if 'name' in b else pd.Series('', index=b.index)
drop = nm.isin(ICONS_OUT); log('tolte (icone modellate a parte):', int(drop.sum()), sorted(set(nm[drop])))
b = b[~drop].reset_index(drop=True)
log('impronte OSM nel raggio', len(b))

# ---------- attributi BDNB ----------
d = rd(f'{RAW}/extra/bdnb.geojson.gz')
d['geometry'] = [loc(g) for g in d.geometry]; d = d.set_geometry('geometry').set_crs(None, allow_override=True)
dc = d.geometry.representative_point(); d = d[inside(dc.x.values, dc.y.values) | True].copy()
pts = gpd.GeoDataFrame(index=b.index, geometry=b.geometry.representative_point())
j = gpd.sjoin(pts, d[['geometry', 'y', 'src', 'h', 'hmax', 'lev', 'roof', 'use', 'use1', 'insee']], how='left', predicate='within')
j = j[~j.index.duplicated()]
miss = j['index_right'].isna()
if miss.any():   # punto interno fuori da ogni gruppo (impronte OSM un po' spostate): gruppo piu' vicino entro 6 m
    jn = gpd.sjoin_nearest(pts[miss], d[['geometry', 'y', 'src', 'h', 'hmax', 'lev', 'roof', 'use', 'use1', 'insee']], how='left', max_distance=6)
    jn = jn[~jn.index.duplicated()]; j.loc[jn.index, jn.columns] = jn
for k in ('y', 'src', 'h', 'hmax', 'lev', 'roof', 'use', 'use1', 'insee'): b[k] = j[k].reindex(b.index)
log('impronte con gruppo BDNB', int(b['insee'].notna().sum()), '| con anno BDNB', int(pd.to_numeric(b['y'], errors='coerce').between(1000, 2026).sum()))

# ---------- anno ----------
def sd(v):
    m = re.search(r'(1[0-9]{3}|20[0-2][0-9])', str(v)) if v is not None and v == v else None
    return float(m.group(1)) if m else np.nan
yr = pd.to_numeric(b['y'], errors='coerce'); yr[(yr < 1000) | (yr > 2026)] = np.nan
osm_sd = b['start_date'].map(sd) if 'start_date' in b else pd.Series(np.nan, index=b.index)
fill = yr.isna() & osm_sd.notna(); yr[fill] = osm_sd[fill]; b.loc[fill, 'src'] = 'osm'
log('anni da OSM start_date', int(fill.sum()))
y0 = yr.copy()
def spread(v):
    if v != v: return v
    v = int(v)
    if v < 1850 and v % 50 == 0: return v + rnd.randint(-20, 20)
    if v % 10 == 0: return min(2026, v + rnd.randint(-5, 4))
    return v
rounded = yr.notna() & (yr % 10 == 0)
yr = yr.map(spread)
log(f'anni tondi distribuiti: {int(rounded.sum())} ({rounded.sum() / max(1, yr.notna().sum()):.0%} di quelli noti)')
cc = b.geometry.representative_point(); xy = np.c_[cc.x, cc.y]
known = yr.notna().values
tr = cKDTree(xy[known]); kv = yr.values[known]
mi = np.where(~known)[0]
if len(mi):
    _, ii = tr.query(xy[mi], k=6); yr.iloc[mi] = np.median(kv[ii], axis=1).round()
b['yr'] = yr.astype(int); b['imp'] = ~known
log('anni stimati dai vicini', len(mi))

# ---------- altezza ----------
def num(v):
    try: return float(str(v).replace(',', '.').split(';')[0].replace('m', '').strip())
    except Exception: return np.nan
oh = b['height'].map(num) if 'height' in b else pd.Series(np.nan, index=b.index)
ol = b['building:levels'].map(num) if 'building:levels' in b else pd.Series(np.nan, index=b.index)
hm = pd.to_numeric(b['h'], errors='coerce'); hx = pd.to_numeric(b['hmax'], errors='coerce'); lv = pd.to_numeric(b['lev'], errors='coerce')
# torri: la media del gruppo schiaccia la torre sul basamento (Montparnasse 98 m di media, 207 di massimo). Se l'impronta
# OSM e' piccola rispetto al gruppo o il massimo supera molto la media, si usa il massimo (solo per la parte alta, riconosciuta da OSM height).
h = oh.copy()
tower = h.isna() & hx.notna() & (hx > 45) & (hx > 1.5 * hm.fillna(0))
gid = j['index_right'].reindex(b.index)
big = b['area'].groupby(gid).transform('max')
tower = tower & (b['area'] >= big - 0.5)          # solo l'impronta piu' grande del gruppo e' la torre; i corpi bassi tengono la media
h[tower] = hx[tower]
h = h.where(h.notna(), hm)
h = h.where(h.notna() & (h > 2), ol * 3.1 + 2.0)
h = h.where(h.notna() & (h > 2), lv * 3.1 + 2.0)
h = h.where(h.notna(), np.where(b['area'] < 40, 4.0, 15.0))
b['hh'] = h.clip(3, CFG.get('max_h', 330))
# edifici alti (>50 m): anno e altezza da Wikidata se c'e' una scheda con data di costruzione entro 60 m (Montparnasse: BDNB 1947, vero 1973)
wf = f'{RAW}/extra/wikidata_costruzione.json'
if os.path.exists(wf):
    W_ = json.load(open(wf))['results']['bindings']; wx, wy, wyr, wh, wn = [], [], [], [], []
    for r_ in W_:
        m_ = re.match(r'Point\(([-0-9.]+) ([-0-9.]+)\)', r_['coord']['value']); yy_ = re.match(r'(\d{4})', r_['date']['value'])
        if not (m_ and yy_): continue
        wx.append((float(m_.group(1)) - LON0) * KX); wy.append((float(m_.group(2)) - LAT0) * KY); wyr.append(int(yy_.group(1)))
        wh.append(num(r_['h']['value']) if 'h' in r_ else np.nan); wn.append(r_['itemLabel']['value'])
    wt = cKDTree(np.c_[wx, wy]); tall = np.where(b['hh'].values > 50)[0]; nfix = []
    for i_ in tall:
        dd_, k_ = wt.query(xy[i_], k=8, distance_upper_bound=60)
        TOWERISH = re.compile(r'^(tour|tours|immeuble|gratte|résidence|grande arche|arche|cœur défense|coeur défense)', re.I)
        best = [kk for dd2, kk in zip(dd_, k_) if dd2 < 60 and ((wh[kk] == wh[kk] and wh[kk] > 40) or TOWERISH.match(wn[kk]))]
        if not best: continue
        kk = best[0]
        if 1850 < wyr[kk] <= 2026 and abs(wyr[kk] - b.at[i_, 'yr']) > 3:
            nfix.append((wn[kk], int(b.at[i_, 'yr']), wyr[kk])); b.at[i_, 'yr'] = wyr[kk]
        if wh[kk] == wh[kk] and wh[kk] > b.at[i_, 'hh'] + 10 and wh[kk] < 330: b.at[i_, 'hh'] = wh[kk]
    log('edifici alti corretti con Wikidata:', len(nfix), nfix[:15])
log('torri dal massimo BD TOPO', int(tower.sum()), '| altezza max', round(float(b.hh.max()), 1))

def kind(u, u1, tag, a):
    s = f'{u} {u1} {tag}'.lower()
    if a < 30 or any(k in s for k in ('annexe', 'garage', 'shed', 'hut', 'roof', 'kiosk')): return 'anc'
    if any(k in s for k in ('industri', 'warehouse', 'entrepot', 'agricole')): return 'ind'
    if any(k in s for k in ('tertiaire', 'commerc', 'religi', 'enseign', 'sant', 'sport', 'public', 'church', 'school', 'office', 'cathedral', 'civic')): return 'pub'
    return 'res'
def rooft(v):
    s = str(v).upper()
    if 'ZINC' in s or 'ARDOISE' in s: return 'z'      # tetti in zinco e ardesia: mansarde parigine
    if 'TUILE' in s: return 't'
    if 'BETON' in s: return 'b'
    return None

out = []; st = {'rf': {}, 'src': {}}
for g, y, y_, hh, u, u1, tag, a, imp, rf, s_ in zip(b.geometry, b.yr, y0, b.hh, b['use'], b['use1'], b['building'], b['area'], b.imp, b['roof'], b['src']):
    if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
    g = g.simplify(0.3)
    if g.is_empty or g.area < MINAREA or g.geom_type != 'Polygon': continue
    ring = [[round(x, 2), round(yy, 2)] for x, yy in list(g.exterior.coords)[:-1]]
    if len(ring) < 3: continue
    o = {'r': ring, 'h': round(float(hh), 1), 'y': int(y), 'k': kind(u, u1, tag, a)}
    if imp: o['i'] = 1
    r_ = rooft(rf)
    if r_: o['rf'] = r_
    if y_ == y_ and int(y_) != int(y): o['y0'] = int(y_)
    st['rf'][r_] = st['rf'].get(r_, 0) + 1; st['src'][str(s_)] = st['src'].get(str(s_), 0) + 1
    out.append(o)
json.dump(out, open(f'{DATA}/buildings.json', 'w'))
ys = np.array([o['y'] for o in out]); hs = np.array([o['h'] for o in out])
log(f'FATTO edifici: {len(out)}, anni {ys.min()}..{ys.max()}, mediana {int(np.median(ys))}, altezza max {hs.max()} m')
st['n'] = len(out); st['per_periodo'] = {}
for a_, b_ in ((1000, 1600), (1600, 1790), (1790, 1850), (1850, 1870), (1870, 1914), (1914, 1945), (1945, 1975), (1975, 2027)):
    n_ = int(((ys >= a_) & (ys < b_)).sum()); st['per_periodo'][f'{a_}-{b_ - 1}'] = n_; log(f'  {a_}-{b_ - 1}: {n_}')
log('tetti', st['rf'], '| fonte anno', st['src'])

# ---------- terra, acqua, parchi ----------
e = rd(f'{RAW}/osm_env.geojson.gz')
e['geometry'] = [loc(g) for g in e.geometry]
Lh = CFG.get('land_half_m', 40000)
water = []
for g, pr in zip(e.geometry, e.itertuples()):
    nat = getattr(pr, 'natural', None); ww = getattr(pr, 'waterway', None); lu = getattr(pr, 'landuse', None)
    if g is None or g.is_empty: continue
    if g.geom_type in ('Polygon', 'MultiPolygon') and (nat == 'water' or ww == 'riverbank' or lu in ('basin', 'reservoir')) and g.area > 800:
        water.append(g.buffer(0))
    elif ww == 'canal' and g.geom_type in ('LineString', 'MultiLineString'): water.append(g.buffer(6, cap_style=2))
W = unary_union(water).buffer(0.5) if water else Polygon()
land = box(-Lh, -Lh, Lh, Lh).difference(W)
lr = []
for q in (land.geoms if hasattr(land, 'geoms') else [land]):
    if isinstance(q, Polygon) and q.area > 400:
        q = q.simplify(1.5)
        lr.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]],
                   'holes': [[[round(x, 1), round(y, 1)] for x, y in list(hh.coords)[:-1]] for hh in q.interiors if Polygon(hh).area > 300]})
json.dump(lr, open(f'{DATA}/land.json', 'w')); open(f'{DATA}/land_v3.ok', 'w').write('ok')
log('terra', len(lr), 'poligoni; acqua', len(water), 'oggetti, area', round(W.area / 1e6, 2), 'km2')
pk = []; nk = {}
for g, pr in zip(e.geometry, e.itertuples()):
    vals = [getattr(pr, k_, None) for k_ in ('leisure', 'landuse', 'natural')]
    t = next((v for v in vals if isinstance(v, str)), None)
    if t in ('park', 'garden', 'forest', 'wood', 'cemetery', 'grass') and g is not None and g.geom_type in ('Polygon', 'MultiPolygon') \
            and g.area > (3000 if t != 'grass' else 15000):
        for q in (g.geoms if hasattr(g, 'geoms') else [g]):
            q = q.simplify(1.5); pk.append([[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]]); nk[t] = nk.get(t, 0) + 1
json.dump(pk, open(f'{DATA}/parks.json', 'w')); log('parchi', len(pk), nk)
json.dump(st, open(f'{DATA}/prep_stats.json', 'w'), indent=1)
