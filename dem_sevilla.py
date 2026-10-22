# Rilievo di Siviglia -> DATA/dem.npz {D (spostamento verticale in metri), x0, y0, cell}, usato da build_render.py.
# Sorgente: data_sevilla_src/dem_rel.npz = Copernicus GLO-30 DSM (tile N37 W006 e W007), ripulito da edifici e alberi
# (apertura 150 m in campagna, 600 m in citta'), riferito al livello del fiume (0).
# Il DEM e' di OGGI: i canali del '900 sarebbero avvallamenti gia' nel 1248 (come la Gran Via a Madrid). Quindi:
#  1) tutti i letti d'acqua di ogni epoca vengono RIEMPITI con il terreno circostante;
#  2) vicino a qualsiasi acqua (di qualunque anno) il rilievo va a zero in 120 m: sponde al livello dell'acqua, niente
#     terreno sospeso sopra il fiume;
#  3) la piana resta piatta fino a 6 m (vega e citta'); sopra, esagerazione x2 (Aljarafe, Los Alcores, terrazzi a nord).
# Uso: python dem_sevilla.py DATA_DIR city_sevilla.json osm_export.geojson
import json, math, os, sys
import numpy as np
from scipy import ndimage as nd
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union, transform
from shapely import contains_xy

HERE = os.path.dirname(os.path.abspath(__file__))
DATA, CFG, SRC = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
FLAT, EXAG, TAPER = CFG.get('dem_flat', 6.0), CFG.get('dem_exag', 2.0), CFG.get('dem_taper', 120.0)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
d = np.load(os.path.join(HERE, 'data_sevilla_src', 'dem_rel.npz')); R = d['R'].astype(float); X0, Y0, C = float(d['x0']), float(d['y0']), float(d['cell'])
ny, nx = R.shape; gx, gy = np.meshgrid(X0 + C * np.arange(nx), Y0 + C * np.arange(ny))
F = json.load(open(SRC))['features']
today = unary_union([transform(lambda x, y, z=None: ((x - LON0) * KX, (y - LAT0) * KY), shape(f['geometry'])).buffer(0)
                     for f in F if f['properties'].get('natural') == 'water' or f['properties'].get('waterway') == 'riverbank'])
WS = json.load(open(os.path.join(HERE, 'data_sevilla_src', 'water_src.json')))
hist = unary_union([Polygon(r).buffer(0) for k, v in WS.items() if not k.startswith('_') for r in v])
today = unary_union([q for q in getattr(today, 'geoms', [today]) if q.area > 20000])   # niente fontane e vasche ornamentali (Alcazar)
anywater = unary_union([today, hist])
wet = contains_xy(anywater.buffer(15), gx, gy)
# 1) riempimento: ogni cella d'acqua prende il valore della cella asciutta piu' vicina, poi lisciatura
idx = nd.distance_transform_edt(wet, return_distances=False, return_indices=True)
Rf = R[tuple(idx)]; Rf = np.where(wet, nd.gaussian_filter(Rf, 3), R)
# 2) rampa verso lo zero vicino a qualsiasi acqua
dist = nd.distance_transform_edt(~wet) * C
taper = np.clip(dist / TAPER, 0, 1); taper = taper * taper * (3 - 2 * taper)
# 3) piana piatta, esagerazione sopra
# 4) bordo dei dati: rilievo a zero negli ultimi 2,5 km (fuori dal DEM le celle del terreno sono grandi e piatte:
#    un salto sul bordo apriva fessure nere tra celle fini e grandi)
eb = np.minimum.reduce([gx - X0, (X0 + C * (nx - 1)) - gx, gy - Y0, (Y0 + C * (ny - 1)) - gy])
edge = np.clip(eb / CFG.get('dem_edge', 2500.0), 0, 1); edge = edge * edge * (3 - 2 * edge)
D = EXAG * np.maximum(Rf - FLAT, 0.0) * taper * edge
np.savez_compressed(f'{DATA}/dem.npz', D=D.astype(np.float32), x0=X0, y0=Y0, cell=C)
for nm, (x, y) in {'Giralda': (0, 0), 'Plaza Nueva': (-340, 250), 'Nervion': (2000, -500), 'Triana': (-1500, 0),
                   'Aljarafe (Castilleja)': (-7500, 600), 'Los Alcores': (16000, 0), 'canale Cartuja nel suo letto': (-1400, 2000)}.items():
    i = int((y - Y0) / C); j = int((x - X0) / C); print(f'[dem] {nm:30s} spostamento {D[i, j]:6.1f} m')
print(f'[dem] massimo {D.max():.0f} m; griglia {nx}x{ny} da {C:.0f} m')
