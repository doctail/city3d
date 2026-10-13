# Scarica i dati di New York e li converte nel formato semplice usato da build_render.py
# Uscita: <dir>/buildings.json  [{"r": [[x,y],...], "h": metri, "y": anno}]   <dir>/land.json  [[[x,y],...], ...]
# Fonti: NYC Open Data (Building Footprints: altezza + anno di costruzione; Borough Boundaries con linea di costa).
# Ripiego: OpenStreetMap via Overpass.
import json, math, os, sys, time, random
import requests
from shapely.geometry import shape, Polygon, MultiPolygon, box
from shapely.ops import unary_union

OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data'
os.makedirs(OUT, exist_ok=True)
# area: Manhattan intera + bordo di Brooklyn e Jersey City sull'acqua
S, W, N, E = 40.680, -74.045, 40.882, -73.905
LAT0, LON0 = 40.758, -73.985
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def P(lon, lat): return [round((lon - LON0) * KX, 2), round((lat - LAT0) * KY, 2)]
def log(*a): print('[fetch]', *a, flush=True)
H = {'User-Agent': 'city3d-timelapse/1.0'}

def catalog(q):
    r = requests.get('https://api.us.socrata.com/api/catalog/v1', params={'domains': 'data.cityofnewyork.us', 'search_context': 'data.cityofnewyork.us', 'q': q, 'only': 'dataset', 'limit': 20}, headers=H, timeout=60)
    r.raise_for_status(); return r.json()['results']

def pick(cols, *cands):
    for c in cands:
        for k in cols:
            if k.lower() == c: return k
    for c in cands:
        for k in cols:
            if c in k.lower(): return k
    return None

def rings(geom):
    g = shape(geom)
    polys = g.geoms if isinstance(g, MultiPolygon) else [g]
    return [p for p in polys if isinstance(p, Polygon) and not p.is_empty]

def nyc_buildings():
    res = catalog('building footprints')
    ds = None
    for r in res:
        cols = r['resource'].get('columns_field_name', [])
        if pick(cols, 'cnstrct_yr', 'construction_year') and pick(cols, 'heightroof', 'height_roof'):
            ds = r; break
    if not ds: raise RuntimeError('dataset footprints non trovato')
    rid = ds['resource']['id']; cols = ds['resource']['columns_field_name']
    gcol = pick(cols, 'the_geom', 'geom', 'geometry'); hcol = pick(cols, 'heightroof', 'height_roof'); ycol = pick(cols, 'cnstrct_yr', 'construction_year')
    log('dataset', rid, ds['resource']['name'], '| colonne:', gcol, hcol, ycol)
    out, off, LIM = [], 0, 50000
    while True:
        q = {'$where': f'within_box({gcol}, {N}, {W}, {S}, {E})', '$limit': LIM, '$offset': off, '$order': ':id', '$select': f'{gcol},{hcol},{ycol}'}
        for t in range(4):
            try:
                r = requests.get(f'https://data.cityofnewyork.us/resource/{rid}.geojson', params=q, headers=H, timeout=300); r.raise_for_status(); break
            except Exception as e:
                log('retry', t, e); time.sleep(5 + t * 10)
        else: raise RuntimeError('download footprints fallito')
        fs = r.json()['features']
        for f in fs:
            p = f['properties']
            try: h = float(p.get(hcol) or 0) * 0.3048
            except ValueError: h = 0
            try: y = int(float(p.get(ycol) or 0))
            except ValueError: y = 0
            if not f.get('geometry'): continue
            for poly in rings(f['geometry']):
                ext = [P(*c) for c in list(poly.exterior.coords)[:-1]]
                if len(ext) >= 3: out.append({'r': ext, 'h': round(h, 1), 'y': y})
        log('scaricati', off + len(fs))
        if len(fs) < LIM: break
        off += LIM
    return out

def nyc_boroughs():
    # confini dei 5 distretti, gia' ritagliati sulla linea di costa (NYC Open Data). Ritorna {nome: [Polygon lon/lat]}
    for r in catalog('borough boundaries'):
        nm = r['resource']['name'].lower()
        if 'borough boundaries' in nm and 'water' not in nm:
            rid = r['resource']['id']; log('confini', rid, r['resource']['name'])
            g = requests.get(f'https://data.cityofnewyork.us/resource/{rid}.geojson', params={'$limit': 50}, headers=H, timeout=300); g.raise_for_status()
            area = box(W - 0.05, S - 0.03, E + 0.05, N + 0.03); out = {}
            for f in g.json()['features']:
                p_ = f['properties']; name = (p_.get('boroname') or p_.get('boro_name') or p_.get('BoroName') or '?')
                for p in rings(f['geometry']):
                    p = p.intersection(area)
                    for q in (p.geoms if hasattr(p, 'geoms') else [p]):
                        if isinstance(q, Polygon) and q.area > 0: out.setdefault(name, []).append(q)
            if out: return out
    raise RuntimeError('confini non trovati')

def nj_land_geom():
    # New Jersey: contee Census MENO le acque (Hudson, baie) dai file TIGER AREAWATER di ogni contea
    import io, zipfile, shapefile
    def shp(url, base):
        z = requests.get(url, headers=H, timeout=300); z.raise_for_status(); zf = zipfile.ZipFile(io.BytesIO(z.content))
        return shapefile.Reader(shp=io.BytesIO(zf.read(base + '.shp')), dbf=io.BytesIO(zf.read(base + '.dbf')))
    rd = shp('https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip', 'cb_2023_us_county_500k')
    area = box(W - 0.40, S - 0.25, E + 0.40, N + 0.25); land = []; geoids = []   # ampio: i bordi spariscono nella foschia
    for sr in rd.iterShapeRecords():
        rec = sr.record.as_dict()
        if rec.get('STATEFP') not in ('34', '36'): continue
        g = shape(sr.shape.__geo_interface__)
        if g.intersects(area): land.append(g.intersection(area)); geoids.append(rec['GEOID'])
    land = unary_union(land); water = []
    for gid in geoids:
        try:
            w = shp(f'https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_{gid}_areawater.zip', f'tl_2023_{gid}_areawater')
            for sr in w.iterShapes():
                g = shape(sr.__geo_interface__)
                if g.intersects(area) and g.area > 1e-7: water.append(g.buffer(0))
            log('acque contea', gid, len(water))
        except Exception as e: log('acque', gid, e)
    if water: land = land.difference(unary_union(water))
    return land

def to_rings(geom, simp=0.00003):
    out = []
    for q in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        if isinstance(q, Polygon) and q.area > 2e-8: out.append([P(*c) for c in list(q.simplify(simp).exterior.coords)[:-1]])
    return out

def build_land():
    bor = nyc_boroughs()
    json.dump({k: to_rings(unary_union(v)) for k, v in bor.items()}, open(f'{OUT}/boroughs.json', 'w'))
    parts = [unary_union(v) for v in bor.values()]
    try: parts.append(nj_land_geom()); log('New Jersey e contee vicine aggiunti')
    except Exception as e: log('New Jersey non disponibile:', e)
    land = to_rings(unary_union(parts)); json.dump(land, open(f'{OUT}/land.json', 'w')); open(f'{OUT}/land_v3.ok', 'w').write('ok')
    log('terra:', len(land), 'poligoni; distretti:', list(bor.keys())); return land

def nyc_parks():
    for r in catalog('parks properties'):
        nm = r['resource']['name'].lower()
        if 'parks properties' in nm:
            rid = r['resource']['id']; log('parchi', rid, r['resource']['name'])
            g = requests.get(f'https://data.cityofnewyork.us/resource/{rid}.geojson', params={'$limit': 20000}, headers=H, timeout=300); g.raise_for_status()
            area = box(W, S, E, N); out = []
            for f in g.json()['features']:
                if not f.get('geometry'): continue
                for p in rings(f['geometry']):
                    p = p.intersection(area)
                    for q in (p.geoms if hasattr(p, 'geoms') else [p]):
                        if isinstance(q, Polygon) and q.area > 2e-8: out.append([P(*c) for c in list(q.simplify(0.00002).exterior.coords)[:-1]])
            return out
    return []

def osm_buildings():
    q = f'[out:json][timeout:600];(way["building"]({S},{W},{N},{E}););out geom;'
    for srv in ['https://overpass.private.coffee/api/interpreter', 'https://overpass.kumi.systems/api/interpreter', 'https://overpass-api.de/api/interpreter']:
        try:
            r = requests.post(srv, data={'data': q}, headers=H, timeout=900); r.raise_for_status(); els = r.json()['elements']; break
        except Exception as e: log('overpass', srv, e)
    else: raise RuntimeError('overpass fallito')
    out = []
    for e in els:
        g = e.get('geometry'); t = e.get('tags', {})
        if not g or len(g) < 4: continue
        try: h = float(str(t.get('height', '0')).split(';')[0].replace('m', ''))
        except ValueError: h = 0
        if not h and t.get('building:levels'):
            try: h = float(t['building:levels']) * 3.4
            except ValueError: pass
        try: y = int(str(t.get('start_date', '0'))[:4])
        except ValueError: y = 0
        out.append({'r': [P(p['lon'], p['lat']) for p in g[:-1]], 'h': round(h, 1), 'y': y})
    return out

def fill_missing(blds):
    # anno mancante: stima prudente dall'altezza (i dati del Comune lo hanno quasi sempre)
    rnd = random.Random(5); miss = 0
    for b in blds:
        if not b['h'] or b['h'] < 3: b['h'] = round(rnd.uniform(9, 18), 1)
        if not b['y'] or b['y'] < 1600 or b['y'] > 2026:
            miss += 1; h = b['h']
            b['y'] = int(rnd.uniform(1990, 2020) if h > 150 else rnd.uniform(1920, 1975) if h > 60 else rnd.uniform(1870, 1930))
    log('anni stimati per', miss, 'edifici su', len(blds))

if __name__ == '__main__':
    t0 = time.time()
    if '--land-only' in sys.argv:
        build_land(); log(f'FATTO terra {time.time()-t0:.0f}s'); sys.exit(0)
    try: blds = nyc_buildings(); src = 'NYC Open Data'
    except Exception as e:
        log('NYC Open Data non disponibile:', e, '-> OpenStreetMap'); blds = osm_buildings(); src = 'OpenStreetMap'
    fill_missing(blds)
    json.dump(blds, open(f'{OUT}/buildings.json', 'w'))
    try: land = build_land()
    except Exception as e: log('confini non disponibili:', e, '-> inviluppo edifici'); land = []; json.dump(land, open(f'{OUT}/land.json', 'w'))
    try: parks = nyc_parks(); json.dump(parks, open(f'{OUT}/parks.json', 'w')); log('parchi', len(parks))
    except Exception as e: log('parchi non disponibili:', e)
    ys = sorted(b['y'] for b in blds)
    log(f'FATTO: {len(blds)} edifici da {src}, {len(land)} poligoni di terra, anni {ys[0]}..{ys[-1]}, mediana {ys[len(ys)//2]}, {time.time()-t0:.0f}s')
