# Pittsburgh (USA), dati di base LOCALI e gratis: WPRDC (Allegheny County) + USGS 3DEP -> DATA/*.json (poi `python -m kit pack pittsburgh`).
# Niente OSM (Geofabrik/Overpass bloccati): edifici = footprints WPRDC + particelle (anno), strade = Allegheny County street centerlines,
# acqua = Allegheny County major rivers + hydrology areas, quota = USGS 3DEP 1 arc-second suolo nudo (prd-tnm.s3.amazonaws.com; il DSM Copernicus include le torri), nessun parco (serve OSM o un altro dataset).
# Uso:  python fetch_pgh.py RAW_DIR DATA_DIR [download|buildings|land|roads|dem|landmarks|all|flood [stage_ft]]
#   RAW_DIR contiene fp.csv (footprints), pa.csv (assessments), streets.geojson, rivers.geojson, hydro_areas.geojson, dem/*.tif
#   `download` scarica quello che manca (host data.wprdc.org e prd-tnm.s3.amazonaws.com).
# Centro: il Point (40.4406, -80.0), raggio pacchetto 9 km. Locale in metri come il kit: KX = cos(lat0)*111320, KY = 110540.
# Python 3.13 + numpy scipy shapely pyproj tifffile (uv venv). Formato identico a data_marseille_src (buildings {r,h,y,i,k,hs}, roads triangoli {r,y,rail},
# land [{ext,holes}], dem.npz {D,x0,y0,cell}, landmarks.json scheletro). Stampa un riepilogo (conteggi, copertura anni, anni tondi prima/dopo, anni a 0).
import collections, glob, json, math, os, random, re, subprocess, sys, urllib.request
import numpy as np
RAW, DATA = sys.argv[1:3]; WHAT = sys.argv[3] if len(sys.argv) > 3 else 'all'
LAT0, LON0 = 40.4406, -80.0; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = 9000.0; LAND_HALF = 40000.0; HALF, C = 20000.0, 30.0   # DEM: griglia 1334x1334 da 30 m come Lione/Marsiglia
FT = 0.3048006096012192   # ftUS -> m (footprints EPSG:2272, centerlines EPSG:2272)
URL = {
    'fp.csv': 'https://data.wprdc.org/dataset/926d9afe-ea94-4211-9623-d9ad52fd0778/resource/3f73160f-d957-4e1c-8953-4009dd592033/download/data.csv',
    'pa.csv': 'https://data.wprdc.org/dataset/2b3df818-601e-4f06-b150-643557229491/resource/9a1c60bd-f9f7-4aba-aeb7-af8c3aaa44e5/download/assessments.csv',
    'streets.geojson': 'https://data.wprdc.org/dataset/34f6668d-130d-4e10-b49b-598c43b83d27/resource/3a5d16aa-f7fe-46c4-9944-aa101f98f4b0/download/data.geojson',
    'rivers.geojson': 'https://data.wprdc.org/dataset/d285f358-154e-4115-b2e2-520ccf48a2f1/resource/a749cade-9d56-442b-837f-4a93daa8b62a/download/data.geojson',
    'hydro_areas.geojson': 'https://data.wprdc.org/dataset/f063ae36-6c90-4c3c-aafe-102a876d0d44/resource/74aebbef-0df1-441b-9b4b-54cf7c38f567/download/hydrology_areas.geojson',
}
DEMT = ['n41w081', 'n41w080']   # il DEM (+-20 km) sta in queste due tessere USGS 3DEP 1 arc-second (lat 40-41, lon -81..-79)
def log(*a): print('[pgh]', *a, flush=True)
def rp(*p): return os.path.join(RAW, *p)
def L(lon, lat): return ((np.asarray(lon) - LON0) * KX, (np.asarray(lat) - LAT0) * KY)

def download():
    os.makedirs(rp('dem'), exist_ok=True)
    for f, u in URL.items():
        if not os.path.exists(rp(f)): log('scarico', f); urllib.request.urlretrieve(u, rp(f))
    for t in DEMT:
        f = rp('dem', f'USGS_1_{t}.tif')
        if not os.path.exists(f): log('scarico DEM 3DEP', t); urllib.request.urlretrieve(f'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/{t}/USGS_1_{t}.tif', f)

def to_local_2272(xy):
    global _T2272
    if _T2272 is None:
        from pyproj import Transformer
        _T2272 = Transformer.from_crs(2272, 4326, always_xy=True)
    lon, lat = _T2272.transform(xy[:, 0], xy[:, 1]); return np.c_[L(lon, lat)]

# ------------------------------------------------------------------------------------------------ edifici
def build_buildings():
    import pandas as pd, shapely
    from shapely.geometry import Polygon
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    rnd = random.Random(3)
    pa = pd.read_csv(rp('pa.csv'), usecols=['PARID', 'YEARBLT', 'CLASS', 'USEDESC', 'COUNTYBUILDING', 'STORIES', 'MUNICODE'], dtype={'PARID': str})
    pa = pa.drop_duplicates('PARID').set_index('PARID')
    fp = pd.read_csv(rp('fp.csv'), usecols=['PIN', 'x', 'y', 'status', 'area', 'geometry'])
    n_raw = len(fp); st0 = fp.status.value_counts().to_dict()
    tr = Transformer.from_crs(2272, 4326, always_xy=True); lon, lat = tr.transform(fp.x.values, fp.y.values)
    cx, cy = L(lon, lat); fp['cx'], fp['cy'] = cx, cy; fp['d'] = np.hypot(cx, cy)
    fp = fp[(fp.d <= R) & (fp.status != 'demolished')].reset_index(drop=True)   # demolished = non esiste piu': niente (anno di demolizione ignoto)
    log(f'footprints: {n_raw} grezzi {st0}; entro {R / 1000:.0f} km senza demolished: {len(fp)}')
    geoms = shapely.from_wkt(fp.geometry.values); fp = fp.drop(columns='geometry')
    J = pa.reindex(fp.PIN.values); fp['ys'] = J.YEARBLT.values; fp['cls'] = J.CLASS.values; fp['cb'] = J.COUNTYBUILDING.values
    fp['st'] = J.STORIES.values; fp['mun'] = J.MUNICODE.values; fp['use'] = J.USEDESC.values
    fp['ys'] = np.where((fp.ys >= 1750) & (fp.ys <= 2026), fp.ys, np.nan)
    # ---- de-arrotondamento a livello di PARTICELLA (i garage della particella restano coevi). Anni tondi = segnaposto ("circa").
    pin = fp.groupby('PIN').agg(y=('ys', 'first'), d=('d', 'min'))
    pin['y'] = pin.y.where(pin.y.notna()); known = pin.y.dropna().astype(int)
    cnt = collections.Counter(known.values); n_known = len(known)
    def med_nb(v): return float(np.median([cnt.get(v + d, 0) for d in (-4, -3, -2, -1, 1, 2, 3, 4)]))
    share10_before = float(np.mean(known.values % 10 == 0)); share50_before = float(np.mean(known.values % 50 == 0)); top_before = cnt.most_common(6)
    p_spread, win = {}, {}
    for v in cnt:
        if v % 10: continue
        nb = max(1.0, med_nb(v)); ex = max(0.0, cnt[v] - 1.3 * nb)       # solo l'ECCESSO sul livello dei vicini e' segnaposto: l'anno resta per gli altri
        if ex <= 0: continue
        p_spread[v] = ex / cnt[v]; win[v] = 20 if (v % 50 == 0 and (v < 1850 or cnt[v] > 20 * nb)) else 5
    newy = {}
    for pid, v in known.items():
        v = int(v)
        if v in p_spread and rnd.random() < p_spread[v]:
            w = win[v]; v = max(1750, min(2026, v + rnd.randint(-w, w)))
        newy[pid] = v
    known2 = pd.Series(newy); cnt2 = collections.Counter(known2.values)
    share10_after = float(np.mean(known2.values % 10 == 0)); share50_after = float(np.mean(known2.values % 50 == 0))
    log(f'anni tondi (particelle con anno: {n_known}): multipli di 10 {share10_before:.1%} -> {share10_after:.1%}; multipli di 50 {share50_before:.1%} -> {share50_after:.1%}; '
        f'picchi prima {top_before}, dopo {cnt2.most_common(4)}')
    fp['y'] = fp.PIN.map(known2)
    # ---- anni mancanti: mediana dei 6 vicini con anno entro 150 m (+-2 a caso, niente lustro: crea onde), poi vicino piu' prossimo entro 400 m, poi mediana generale
    has = fp.y.notna().values; kxy = np.c_[fp.cx.values[has], fp.cy.values[has]]; ky = fp.y.values[has].astype(float); tree = cKDTree(kxy)
    genmed = int(np.median(ky)); est = np.zeros(len(fp), bool); how = collections.Counter()
    ys = fp.y.values.copy()
    for i in np.where(~has)[0]:
        p = (fp.cx.values[i], fp.cy.values[i]); d, ix = tree.query(p, k=6, distance_upper_bound=150); ok = [j for dd, j in zip(np.atleast_1d(d), np.atleast_1d(ix)) if j < len(ky)]
        if ok: v = int(round(float(np.median(ky[ok])))) + rnd.randint(-2, 2); how['k6_150m'] += 1
        else:
            d1, i1 = tree.query(p, distance_upper_bound=400)
            if i1 < len(ky): v = int(ky[i1]) + rnd.randint(-2, 2); how['nn_400m'] += 1
            else: v = genmed + rnd.randint(0, 4); how['default_median'] += 1
        ys[i] = max(1750, min(2026, v)); est[i] = True
    fp['y'] = ys.astype(int)
    # ---- altezza: piani del catasto (STORIES x 3.2 m) se c'e'; altrimenti stima dal valore catastale dell'edificio per m2 di impronta della particella
    # (US$ per m2 / 600 = piani, 1-14, [Guessing]: i dati aperti non hanno altezze; il centro e' fatto di isolati fusi senza anno ne' piani).
    tot_area = fp.groupby('PIN').area.transform('sum') * FT * FT      # la colonna `area` dei footprints e' in piedi quadrati
    flo = (fp.cb.fillna(0) / np.maximum(tot_area, 1) / 600.0).clip(1, 14)
    h = np.where(fp.st.notna(), fp.st.fillna(0) * 3.2 + 1.0, np.where(fp.cb.fillna(0) > 0, flo * 3.6, 6.0)); hs = np.where(fp.st.notna(), 'stories', np.where(fp.cb.fillna(0) > 0, 'value_est', 'default'))
    h = np.clip(h, 3.0, 90.0)
    # ---- poligoni locali (m), anello aperto, semplificati 0,25 m
    B = []; estidx = []; skipped = 0
    for i, g in enumerate(geoms):
        if g is None: skipped += 1; continue
        for q in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
            if q.geom_type != 'Polygon' or q.area * FT * FT < 20: skipped += 1; continue
            co = np.asarray(q.exterior.coords)[:-1, :2]
            if len(co) < 3: continue
            ring = to_local_2272(co); pg = Polygon(ring)
            if not pg.is_valid: pg = pg.buffer(0)
            if pg.is_empty or pg.geom_type != 'Polygon': skipped += 1; continue
            pg = pg.simplify(0.25)
            if pg.is_empty or pg.geom_type != 'Polygon': continue
            rr = [[round(float(x), 2), round(float(y), 2)] for x, y in list(pg.exterior.coords)[:-1]]
            if len(rr) < 3: continue
            if est[i]: estidx.append(len(B))
            B.append({'r': rr, 'h': round(float(h[i]), 1), 'y': int(fp.y.values[i]), 'i': str(fp.PIN.values[i]), 'k': str(int(fp.mun.values[i])) if fp.mun.notna().values[i] else '', 'hs': str(hs[i])})
    os.makedirs(DATA, exist_ok=True)
    json.dump(B, open(os.path.join(DATA, 'buildings.json'), 'w'), separators=(',', ':'))
    json.dump({'note': 'anni stimati dai vicini (mediana dei 6 piu vicini entro 150 m, +-2 anni) per le impronte la cui particella non ha YEARBLT (commerciale/pubblico/industriale: i dati aperti non li hanno)',
               'estimated_indices': estidx, 'sources': dict(how)}, open(os.path.join(DATA, 'buildings_y0_prov.json'), 'w'))
    # ---- misure
    fp['has'] = ~est; fp['ring'] = pd.cut(fp.d, [0, 500, 1000, 2000, 4000, 9000.1])
    cov_ring = fp.groupby('ring', observed=True).agg(n=('has', 'size'), cov=('has', 'mean')).round(3)
    cov_cls = fp.groupby('cls', dropna=False).agg(n=('has', 'size'), cov=('has', 'mean')).round(3).sort_values('n', ascending=False).head(6)
    yy = np.array([b['y'] for b in B]); M = {
        'footprints_raw': n_raw, 'entro_9km_senza_demolished': len(fp), 'poligoni_scritti': len(B), 'scartati': skipped, 'impronte_con_anno_vero': int(has.sum()), 'quota_con_anno_vero': round(float(has.mean()), 4),
        'quota_area_con_anno_vero': round(float((fp.area * has).sum() / fp.area.sum()), 4), 'stimate': int(est.sum()), 'come': dict(how),
        'tondi_x10_prima_dopo': [round(share10_before, 4), round(share10_after, 4)], 'tondi_x50_prima_dopo': [round(share50_before, 4), round(share50_after, 4)],
        'picchi_prima': top_before, 'picchi_dopo': cnt2.most_common(6), 'y0_o_meno': int((yy <= 0).sum()), 'y_min': int(yy.min()), 'y_max': int(yy.max()), 'y_<1850': int((yy < 1850).sum()),
        'copertura_per_anello_m': {str(k): v for k, v in cov_ring.to_dict('index').items()}, 'copertura_per_CLASS': cov_cls.to_dict('index'),
        'altezze_fonte': dict(collections.Counter(b['hs'] for b in B)), 'decenni': dict(sorted(collections.Counter((int(y) // 10) * 10 for y in yy).items()))}
    json.dump(M, open(os.path.join(DATA, 'misure_pgh.json'), 'w'), indent=1, ensure_ascii=False, default=str)
    log('RIEPILOGO edifici:', json.dumps({k: M[k] for k in ('poligoni_scritti', 'quota_con_anno_vero', 'quota_area_con_anno_vero', 'stimate', 'come', 'tondi_x10_prima_dopo', 'tondi_x50_prima_dopo', 'y0_o_meno', 'y_min', 'y_<1850', 'altezze_fonte')}, default=str))
    log('copertura anno vero per anello (m dal Point):', {str(k): (int(v['n']), v['cov']) for k, v in cov_ring.to_dict('index').items()})
    log('copertura per CLASS:', {k: (int(v['n']), v['cov']) for k, v in cov_cls.to_dict('index').items()})
    return B

# ------------------------------------------------------------------------------------------------ acqua + terra
def water_union():
    import shapely
    from shapely.geometry import shape, box
    from shapely.ops import unary_union
    from pyproj import Transformer
    t = Transformer.from_crs(3857, 4326, always_xy=True)
    def loc(g, src):
        return shapely.transform(g, lambda c: np.c_[L(*(t.transform(c[:, 0], c[:, 1]) if src == 3857 else (c[:, 0], c[:, 1])))])
    W = []
    for f in json.load(open(rp('rivers.geojson')))['features']:
        g = shape(f['geometry'])
        if g.is_valid or True: W.append(loc(g, 3857).buffer(0))
    for f in json.load(open(rp('hydro_areas.geojson')))['features']:
        if not f.get('geometry'): continue
        g = shape(f['geometry']); s = loc(g, 4326).buffer(0)
        if s.area > 2500: W.append(s)
    return unary_union(W).buffer(0)

def rings(geom, simp=2.0, amin=50):
    from shapely.geometry import Polygon
    out = []
    for q in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        if isinstance(q, Polygon) and q.area > amin:
            q = q.simplify(simp)
            out.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]],
                        'holes': [[[round(x, 1), round(y, 1)] for x, y in list(h.coords)[:-1]] for h in q.interiors if Polygon(h).area > 200]})
    return out

def build_land():
    from shapely.geometry import box, Point
    from shapely.prepared import prep
    W = water_union(); LAND = box(-LAND_HALF, -LAND_HALF, LAND_HALF, LAND_HALF).difference(W)
    lr = rings(LAND); os.makedirs(DATA, exist_ok=True)
    json.dump(lr, open(os.path.join(DATA, 'land.json'), 'w')); json.dump([], open(os.path.join(DATA, 'parks.json'), 'w'))
    LP = prep(LAND)
    def P(lat, lon): return Point(*[float(v) for v in L(lon, lat)])
    for k, (la, lo) in {'The Point (acqua o riva)': (40.4416, -80.0108), 'Allegheny River (acqua)': (40.4500, -79.9800), 'Monongahela (acqua)': (40.4330, -79.9900),
                        'Ohio River (acqua)': (40.4650, -80.0900), 'Market Square (terra)': (40.4408, -80.0030), 'Mt Washington (terra)': (40.4385, -80.0105), 'Oakland (terra)': (40.4440, -79.9530)}.items():
        log(f'  {k:28s} -> {"TERRA" if LP.contains(P(la, lo)) else "ACQUA"}')
    log(f'land.json: {len(lr)} poligoni, {sum(len(r["holes"]) for r in lr)} buchi (acqua = rivers + hydrology areas WPRDC); parks.json VUOTO (nessun dataset parchi senza OSM)')
    return LAND

# ------------------------------------------------------------------------------------------------ strade (+ ponti stimati)
FCC_W = {'A11': 22, 'A12': 22, 'A21': 16, 'A31': 13, 'A32': 13, 'A33': 13, 'A43': 9, 'A63A': 9, 'A63B': 9, 'A41': 7, 'A42': 7, 'A61': 7, 'A62': 7, 'A63': 9, 'A64': 7}   # CFCC: A11 interstate, A21 primaria, A31 secondaria, A41 locale, A63 rampa; A7x (vicoli, strade private, scale) saltati
def build_roads(LAND=None):
    import shapely
    from collections import defaultdict
    from shapely.geometry import Polygon, LineString, Point, box
    from shapely.ops import unary_union
    from shapely.prepared import prep
    from scipy.spatial import cKDTree
    if LAND is None:
        LAND = unary_union([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in json.load(open(os.path.join(DATA, 'land.json')))])
    LP = prep(LAND); WATER = box(-R - 300, -R - 300, R + 300, R + 300).difference(LAND); WP = prep(WATER)
    B = json.load(open(os.path.join(DATA, 'buildings.json')))
    bxy = np.array([[sum(p[0] for p in o['r']) / len(o['r']), sum(p[1] for p in o['r']) / len(o['r'])] for o in B]); by = np.array([o['y'] for o in B], float); bt = cKDTree(bxy)
    def urban_year(x, y):
        for rad, mn in ((120, 3), (300, 3)):
            ii = bt.query_ball_point([x, y], rad)
            if len(ii) >= mn: return float(np.percentile(by[ii], 20))
        d, i = bt.query([x, y], distance_upper_bound=700)
        return float(by[i]) if i < len(by) else None
    from pyproj import Transformer
    tr = Transformer.from_crs(2272, 4326, always_xy=True)
    rd, br, stat = [], [], collections.Counter()
    for f in json.load(open(rp('streets.geojson')))['features']:
        fc = f['properties'].get('FCC') or f['properties'].get('FEATURE_KE'); w = FCC_W.get(fc, 0)
        if not w: stat['saltata_' + str(fc)] += 1; continue
        gg = f['geometry']; lines = gg['coordinates'] if gg['type'] == 'MultiLineString' else [gg['coordinates']]
        for ln in lines:
            a = np.asarray(ln)[:, :2]; lon, lat = tr.transform(a[:, 0], a[:, 1]); x, y = L(lon, lat)
            if np.hypot(x.mean(), y.mean()) > R + 100: continue
            g = LineString(np.c_[x, y]); ys = []
            for fr in (0.2, 0.5, 0.8):
                p = g.interpolate(fr, normalized=True); v = urban_year(p.x, p.y)
                if v is not None: ys.append(v)
            if not ys: stat['senza_edifici_700m'] += 1; continue
            yr = int(np.median(ys)) + 2; stat['anno_da_edifici'] += 1
            rd.append((g, w, int(max(yr, 1750)) // 2 * 2, 0))
    log('segmenti-via', len(rd), dict(stat))
    quads = defaultdict(list); bquads = []
    for g, w, y, israil in rd:
        cs = list(g.simplify(1.0).coords)
        for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
            dl = math.hypot(x1 - x0, y1 - y0)
            if dl < 1: continue
            ux, uy = (x1 - x0) / dl, (y1 - y0) / dl; e = w / 2; nx, ny = -uy * e, ux * e
            ax_, ay_ = x0 - ux * e * 0.5, y0 - uy * e * 0.5; bx_, by_ = x1 + ux * e * 0.5, y1 + uy * e * 0.5
            q = Polygon([(ax_ + nx, ay_ + ny), (ax_ - nx, ay_ - ny), (bx_ - nx, by_ - ny), (bx_ + nx, by_ + ny)]); mid = Point((x0 + x1) / 2, (y0 + y1) / 2)
            if LP.contains(mid): quads[(y, israil)].append(q)
            elif WP.contains(mid): bquads.append((q, y, w))     # tratto sull'acqua = ponte (impalcato)
    roads = []; TILE = 1500.0; keys = sorted(quads); U = {k: unary_union(quads[k]).simplify(0.3) for k in keys}
    nt = int(math.ceil(2 * (R + 200) / TILE)); x0 = -(R + 200)
    for ix in range(nt):
        for iy in range(nt):
            tb = box(x0 + ix * TILE, x0 + iy * TILE, x0 + (ix + 1) * TILE, x0 + (iy + 1) * TILE); done_ = Polygon()
            for k in keys:
                u = U[k]
                if not u.intersects(tb): continue
                u = u.intersection(tb)
                if done_.area: u = u.difference(done_)
                done_ = unary_union([done_, u]) if not u.is_empty else done_
                for q in (u.geoms if hasattr(u, 'geoms') else [u]):
                    if not isinstance(q, Polygon) or q.area < 5: continue
                    for t in shapely.constrained_delaunay_triangles(q).geoms:
                        if t.area > 0.05: roads.append({'r': [[round(x, 2), round(yv, 2)] for x, yv in list(t.exterior.coords)[:-1]], 'y': int(k[0]), 'rail': k[1]})
    json.dump(roads, open(os.path.join(DATA, 'roads.json'), 'w'), separators=(',', ':'))
    # ponti: segmenti stradali sull'acqua, anno = urbanizzazione del punto e' una STIMA (nessuna fonte aperta con l'anno dei ponti): ponti veri vanno nella story (history.bridges)
    brj = []
    for q, y, w in bquads:
        if q.area > 30: brj.append({'r': [[round(x, 2), round(yv, 2)] for x, yv in list(q.exterior.coords)[:-1]], 'y': max(int(y), 1880), 'name': '', 'year_method': 'urbanization_estimate', 'source': 'wprdc_centerline_over_water'})
    json.dump(brj, open(os.path.join(DATA, 'bridges.json'), 'w'), separators=(',', ':'))
    yy = [r['y'] for r in roads]
    log(f'roads.json: {len(roads)} triangoli da {len(rd)} segmenti; anni {min(yy)}..{max(yy)} mediana {int(np.median(yy))}; bridges.json: {len(brj)} impalcati stimati (anno = stima)')

# ------------------------------------------------------------------------------------------------ DEM
def load_dem_grid():
    import tifffile
    from scipy import ndimage as nd
    xs = np.arange(-HALF, HALF + 1, C); ys = np.arange(-HALF, HALF + 1, C); GX, GY = np.meshgrid(xs, ys)
    lon = LON0 + GX / KX; lat = LAT0 + GY / KY; S = np.full(GX.shape, np.nan)
    # USGS 3DEP 1 arc-second (SUOLO NUDO da lidar, NAVD88, ~30 m): il DSM Copernicus include le torri del Golden Triangle (mediana +20 m sul fiume al centro:
    # le acque di piena non lo vedrebbero mai). Tessere USGS_1_n41w080/n41w081 (lat 40-41, lon -81..-79), tiepoint = angolo alto-sinistro del pixel.
    for f in sorted(glob.glob(rp('dem', 'USGS_1_n*w*.tif'))):
        tf = tifffile.TiffFile(f); pg = tf.pages[0]; t = pg.asarray().astype(np.float64); t[t < -9000] = np.nan
        tp = pg.tags['ModelTiepointTag'].value; sc = pg.tags['ModelPixelScaleTag'].value; ny0, nx0 = t.shape
        fi = (tp[4] - lat) / sc[1] - 0.5; fj = (lon - tp[3]) / sc[0] - 0.5
        m = (fi >= 0) & (fi <= ny0 - 1) & (fj >= 0) & (fj <= nx0 - 1)
        if m.any():
            t0 = np.nan_to_num(t, nan=-9999.0); v = nd.map_coordinates(t0, [fi[m], fj[m]], order=1); v[v < -9000] = np.nan; S[m] = v
        log(f'dem: {os.path.basename(f)} usata per {int(m.sum())} celle')
    S = np.where(np.isnan(S), np.nanmedian(S), S)
    log(f'dem: semi-lato {HALF / 1000:.0f} km, cella {C:.0f} m; quota min/max {S.min():.0f}/{S.max():.0f} m (NAVD88)')
    return xs, ys, GX, GY, S

def build_dem():
    import tifffile
    from scipy import ndimage as nd
    from shapely.geometry import Polygon
    from shapely import contains_xy
    from shapely.ops import unary_union
    FLAT, EXAG, TAPER = 3.0, 1.6, 100.0
    xs, ys, GX, GY, S = load_dem_grid()
    OPEN = float(os.environ.get('DEM_OPEN', 0.0))    # suolo nudo: nessuna apertura morfologica (Marsiglia, DSM: 150 m)
    G = nd.grey_opening(S, size=(int(OPEN / C), int(OPEN / C))) if OPEN >= 2 * C else S.copy(); G = nd.gaussian_filter(G, float(os.environ.get('DEM_SIGMA', 1.5)))
    lr = json.load(open(os.path.join(DATA, 'land.json')))
    LG = unary_union([Polygon(r_['ext'], r_.get('holes', [])).buffer(0) for r_ in lr]); water_now = ~contains_xy(LG, GX, GY)
    sel = water_now & (np.hypot(GX, GY) < 6000)
    sea = float(np.median(S[sel])) if sel.any() else float(S.min())      # = livello normale dei fiumi (pool): DSM Copernicus appiattisce l'acqua
    Rr = np.where(water_now, 0.0, np.maximum(G - sea, 0.0))
    wet = nd.binary_dilation(water_now, iterations=1); dist = nd.distance_transform_edt(~wet) * C
    taper = np.clip(dist / TAPER, 0, 1); taper = taper * taper * (3 - 2 * taper)
    eb = HALF - np.maximum(np.abs(GX), np.abs(GY)); edge = np.clip(eb / 2500.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
    D = EXAG * np.maximum(Rr - FLAT, 0.0) * taper * edge
    np.savez_compressed(os.path.join(DATA, 'dem.npz'), D=D.astype(np.float32), x0=float(xs[0]), y0=float(ys[0]), cell=C)
    log(f'dem.npz: griglia {len(xs)}x{len(ys)}, livello fiumi (DSM) {sea:.1f} m = {sea / FT:.0f} ft, spostamento max {D.max():.0f} m')
    for nm, (la, lo) in {'The Point': (40.4416, -80.0108), 'Market Square': (40.4408, -80.0030), 'PPG Place': (40.4413, -80.0036), 'Penn/Liberty': (40.4440, -79.9990),
                         'Station Square': (40.4333, -80.0039), 'Mt Washington (Grandview)': (40.4381, -80.0114), 'Cathedral of Learning': (40.4444, -79.9533)}.items():
        x, y = L(lo, la); i = int((y + HALF) / C); j = int((x + HALF) / C)
        log(f'  {nm:26s} DSM {S[i, j]:6.1f} m, sul fiume {S[i, j] - sea:+6.1f} m, spostamento kit {D[i, j]:6.1f} m')

# ------------------------------------------------------------------------------------------------ piena (1936): estensione dal DEM
def build_flood(stage_ft=46.0, gauge_zero_ft=692.0, pool_ft=710.0, radius=5000.0):
    """Zona allagata da una piena con livello `stage_ft` al misuratore del Point (quota = gauge_zero_ft + stage_ft, NGVD/NAVD88 ~ uguali qui) sul DEM suolo nudo:
    celle sotto il livello CONNESSE ai fiumi. Scrive DATA/flood_rings.json (anelli [lat, lon] per `history.floods`) e stampa le statistiche."""
    from scipy import ndimage as nd
    from shapely.geometry import Polygon, box, MultiPolygon
    from shapely import contains_xy
    from shapely.ops import unary_union
    xs, ys, GX, GY, S = load_dem_grid()
    lr = json.load(open(os.path.join(DATA, 'land.json'))); LG = unary_union([Polygon(r_['ext'], r_.get('holes', [])).buffer(0) for r_ in lr]); water = ~contains_xy(LG, GX, GY)
    sel = water & (np.hypot(GX, GY) < 6000); pool_dem = float(np.median(S[sel])); crest_abs = (gauge_zero_ft + stage_ft) * FT
    rise = crest_abs - pool_ft * FT          # metri sopra il livello normale dei fiumi (pool Emsworth 710 ft)
    G = nd.gaussian_filter(S, 1.0); H = G - pool_dem; wet = (H < rise) | water
    lab, n = nd.label(wet); keep = np.unique(lab[water & (np.hypot(GX, GY) < 3000)]); keep = keep[keep > 0]
    flood = np.isin(lab, keep) & ~water & (np.hypot(GX, GY) <= radius)
    depth = np.where(flood, rise - H, 0.0)
    log(f'piena: stage {stage_ft:.0f} ft -> quota {crest_abs:.2f} m ({gauge_zero_ft + stage_ft:.0f} ft); pool DEM {pool_dem:.2f} m ({pool_dem / FT:.0f} ft; documentato {pool_ft:.0f} ft); salita sul normale {rise:.2f} m ({rise / FT:.0f} ft)')
    log(f'  allagato entro {radius / 1000:.0f} km: {flood.sum() * C * C / 1e6:.2f} km2, profondita media {depth[flood].mean():.1f} m, p90 {np.percentile(depth[flood], 90):.1f} m, max {depth.max():.1f} m')
    tri = Polygon([((lo - LON0) * KX, (la - LAT0) * KY) for la, lo in [(40.4416, -80.0108), (40.4478, -79.9938), (40.4366, -79.9948)]]); inT = contains_xy(tri, GX, GY) & ~water
    log(f'  Golden Triangle (poligono approssimato): allagato {float(flood[inT].mean()):.0%} delle celle di terra, profondita media {depth[inT & flood].mean():.1f} m')
    cells = unary_union([box(x - C / 2, y - C / 2, x + C / 2, y + C / 2) for x, y in zip(GX[flood], GY[flood])]).buffer(1).buffer(-1)
    out = []
    for q in (cells.geoms if hasattr(cells, 'geoms') else [cells]):
        if q.area < 20000: continue
        q = q.simplify(12.0); ring = [[round(LAT0 + y / KY, 5), round(LON0 + x / KX, 5)] for x, y in list(q.exterior.coords)[:-1]]
        out.append({'ring': ring, 'area_ha': round(q.area / 1e4, 1), 'mean_depth_m': round(float(depth[contains_xy(q, GX, GY) & flood].mean()), 2)})
    json.dump({'stage_ft': stage_ft, 'rise_m': round(rise, 2), 'crest_abs_m': round(crest_abs, 2), 'pool_dem_m': round(pool_dem, 2), 'rings': out}, open(os.path.join(DATA, 'flood_rings.json'), 'w'))
    log(f'flood_rings.json: {len(out)} anelli (>2 ha), {sum(o["area_ha"] for o in out):.0f} ha')

def build_landmarks():
    # Scheletro nello schema del kit: `python -m kit build pittsburgh` lo sovrascrive dai preset della story (yb-modeler li definisce).
    json.dump({'parts': [], 'clear': [], 'labels': [], '_kit': {'slug': 'pittsburgh', 'source': 'scheletro vuoto (fetch_pgh.py): nessun dato OSM per i candidati monumento', 'landmarks': 0}},
              open(os.path.join(DATA, 'landmarks.json'), 'w'), ensure_ascii=False)
    log('landmarks.json: scheletro vuoto')

os.makedirs(DATA, exist_ok=True)
if WHAT in ('download',) or (WHAT == 'all' and not all(os.path.exists(rp(f)) for f in URL)): download()
LND = None
if WHAT in ('buildings', 'all'): build_buildings()
if WHAT in ('land', 'all'): LND = build_land()
if WHAT in ('roads', 'all'): build_roads(LND)
if WHAT in ('dem', 'all'): build_dem()
if WHAT in ('landmarks', 'all'): build_landmarks()
if WHAT == 'flood': build_flood(float(sys.argv[4]) if len(sys.argv) > 4 else 46.0)
