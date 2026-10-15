# Olanda: edifici dal 3DBAG (TU Delft) -> formato di build_render.py
# Uso: python fetch_nl.py DATA_DIR city_rotterdam.json [3dbag-lod13.parquet]
#   senza file lo scarica (747 MB) da source.coop: va fatto dal pod, dal sandbox e' bloccato.
# Fonte: 3dbag-lod13.parquet (GeoParquet, EPSG:7415 = RD New + NAP), una riga per parte di edificio.
#   bouwjaar = anno di costruzione originale (9999 = sconosciuto); height = altezza della parte sul terreno (70 percentile del tetto).
# Uscita: DATA/buildings.json [{"r": [[x,y],...], "h": m, "y": anno}], DATA/land.json (quadrato; l'acqua la ritaglia osm_extra.py)
import json, math, os, sys
import numpy as np

URL = 'https://data.source.coop/cholmes/portolan-nl/tudelft/3dbag/3dbag-lod13.parquet'
DATA, CFG = sys.argv[1], json.load(open(sys.argv[2])); SRC = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(DATA, exist_ok=True)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 9000)
MINAREA = CFG.get('min_area_m2', 12)   # sotto: casette da giardino, cabine
def log(*a): print('[fetch_nl]', *a, flush=True)

def download(dst):
    import requests
    log('scarico', URL)
    with requests.get(URL, stream=True, timeout=600, headers={'User-Agent': 'city3d/1.0'}) as r:
        r.raise_for_status(); n = 0
        with open(dst + '.part', 'wb') as f:
            for ch in r.iter_content(1 << 22):
                f.write(ch); n += len(ch)
                if n % (100 << 20) < (1 << 22): log(f'  {n >> 20} MB')
    os.replace(dst + '.part', dst)

if not SRC:
    SRC = '/workspace/3dbag-lod13.parquet'
    if not os.path.exists(SRC): download(SRC)

import pyarrow.parquet as pq
import shapely
from pyproj import Transformer
to_rd = Transformer.from_crs('EPSG:4326', 'EPSG:28992', always_xy=True)
to_ll = Transformer.from_crs('EPSG:28992', 'EPSG:4326', always_xy=True)
CX, CY = to_rd.transform(LON0, LAT0)
log(f'centro RD {CX:.0f} {CY:.0f}, raggio {R} m')

pf = pq.ParquetFile(SRC)
names = pf.schema_arrow.names
GEO = next(c for c in ('geom', 'geometry', 'wkb_geometry') if c in names)
YR = next(c for c in ('bouwjaar', 'oorspronkelijkbouwjaar') if c in names)
HT = next(c for c in ('height', 'b3_h_70p') if c in names)
BB = 'bbox' if 'bbox' in names else None
log('colonne:', GEO, YR, HT, BB or '(niente bbox: filtro dalla geometria)', '| gruppi:', pf.num_row_groups)

out = []; noyear = 0; seen = 0
for gi in range(pf.num_row_groups):
    cols = [GEO, YR, HT] + ([BB] if BB else [])
    t = pf.read_row_group(gi, columns=cols)
    seen += t.num_rows
    if BB:   # scarta subito i gruppi lontani
        bb = t.column(BB).combine_chunks()
        x0 = np.asarray(bb.field('xmin')); y0 = np.asarray(bb.field('ymin'))
        keep = (np.abs(x0 - CX) < R + 500) & (np.abs(y0 - CY) < R + 500)
        if not keep.any(): continue
        t = t.filter(keep)
    g = shapely.from_wkb(np.asarray(t.column(GEO).to_pylist(), dtype=object))
    c = shapely.centroid(g); cx = shapely.get_x(c); cy = shapely.get_y(c)
    sel = (cx - CX) ** 2 + (cy - CY) ** 2 < R * R
    if not sel.any(): continue
    g = g[sel]; yr = np.asarray(t.column(YR).to_numpy(zero_copy_only=False))[sel]
    ht = np.asarray(t.column(HT).to_numpy(zero_copy_only=False), dtype=float)[sel]
    for geom, y, h in zip(g, yr, ht):
        if geom is None or geom.is_empty: continue
        if geom.geom_type == 'MultiPolygon': geom = max(geom.geoms, key=lambda p: p.area)
        if geom.area < MINAREA: continue
        xs, ys = np.asarray(geom.exterior.coords)[:-1, :2].T
        lo, la = to_ll.transform(xs, ys)
        ring = [[round((o - LON0) * KX, 2), round((a - LAT0) * KY, 2)] for o, a in zip(lo, la)]
        if len(ring) < 3: continue
        y = int(y) if y is not None and not (isinstance(y, float) and math.isnan(y)) else 0
        if y < 1000 or y > 2026: y = 0; noyear += 1
        h = 0.0 if h is None or math.isnan(h) else float(h)
        out.append({'r': ring, 'h': round(h, 1), 'y': y})
    if gi % 20 == 0: log(f'gruppo {gi}/{pf.num_row_groups}: lette {seen} righe, tenute {len(out)}')
log('parti di edificio:', len(out), '| senza anno:', noyear)

import random
rnd = random.Random(5)
for b in out:
    if not b['h'] or b['h'] < 3: b['h'] = round(rnd.uniform(6, 12), 1)
    if not b['y']: b['y'] = int(rnd.uniform(1950, 1990))
json.dump(out, open(f'{DATA}/buildings.json', 'w'))
L = CFG.get('land_half_m', 20000)
json.dump([[[-L, -L], [L, -L], [L, L], [-L, L]]], open(f'{DATA}/land.json', 'w')); open(f'{DATA}/land_v3.ok', 'w').write('ok')
ys = sorted(b['y'] for b in out); hs = sorted(b['h'] for b in out)
log(f'FATTO: {len(out)} parti, anni {ys[0]}..{ys[-1]}, mediana {ys[len(ys)//2]}, altezza max {hs[-1]} m')
for a, b in ((1000, 1600), (1600, 1800), (1800, 1900), (1900, 1940), (1940, 1950), (1950, 1980), (1980, 2027)):
    log(f'  {a}-{b - 1}: {sum(1 for v in ys if a <= v < b)}')
