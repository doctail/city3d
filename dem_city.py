# Rilievo di una citta' -> DATA/dem.npz {D, x0, y0, cell}: generalizzazione di dem_nyc.py (Copernicus GLO-30 DSM, griglia 1334x1334 da 30 m, semi-lato 20 km,
# apertura morfologica DEM_OPEN, quota rispetto al datum, rampa a 0 sulla riva, esagerazione 1,6). Il DSM contiene gli edifici: l'apertura li toglie.
# Datum: mediana del DSM sulle celle d'acqua (land.json) entro 6 km se sono >= 300 (mare/fiume largo); altrimenti 2o percentile del DSM aperto entro 12 km (citta' di entroterra).
# Uso: python dem_city.py CITY_JSON DEM_DIR DATA_DIR   (DEM_OPEN default 600 m, DEM_CHECK="nome:lat:lon;..." per stampare il residuo nei punti)
import glob, json, math, os, re, sys
import numpy as np, tifffile
from scipy import ndimage as nd
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
CFG = json.load(open(sys.argv[1])); DEMD, DATA = sys.argv[2:4]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
HALF, C = 20000.0, 30.0; FLAT, EXAG, TAPER = 3.0, 1.6, 100.0
def log(*a): print('[dem_city]', *a, flush=True)
TILES = {}
for f in glob.glob(f'{DEMD}/Copernicus_DSM_COG_10_*_DEM.tif'):
    m = re.search(r'_([NS])(\d+)_00_([EW])(\d+)_00_DEM', f); TILES[((1 if m[1] == 'N' else -1) * int(m[2]), (1 if m[3] == 'E' else -1) * int(m[4]))] = f
xs = np.arange(-HALF, HALF + 1, C); ys = np.arange(-HALF, HALF + 1, C); GX, GY = np.meshgrid(xs, ys); lon = LON0 + GX / KX; lat = LAT0 + GY / KY
S = np.zeros(GX.shape)
for (la, lo), f in TILES.items():
    t = tifffile.imread(f).astype(np.float64); ny0, nx0 = t.shape; m = (lat >= la) & (lat < la + 1) & (lon >= lo) & (lon < lo + 1)
    if m.any(): S[m] = nd.map_coordinates(t, [(la + 1 - lat[m]) * (ny0 - 1), (lon[m] - lo) * (nx0 - 1)], order=1)
log('tile', sorted(TILES), 'celle senza dati (0):', int((S == 0).sum()), 'DSM min/max', float(S.min()), float(S.max()))
OPEN = float(os.environ.get('DEM_OPEN', 600.0))
G = nd.gaussian_filter(nd.grey_opening(S, size=(int(OPEN / C), int(OPEN / C))), 4)
lr = json.load(open(os.path.join(DATA, 'land.json')))
LG = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in lr])
water = ~contains_xy(LG, GX, GY); wsel = water & (np.hypot(GX, GY) < 6000)
if wsel.sum() >= 300: datum = float(np.median(S[wsel])); how = f'mediana DSM su {int(wsel.sum())} celle d acqua entro 6 km'
else: datum = float(np.percentile(G[np.hypot(GX, GY) < 12000], 2)); how = f'inland: 2o percentile del DSM aperto entro 12 km (acqua nel disco: {int(wsel.sum())} celle)'
if 'inland' in how or os.environ.get('DEM_PERCH'):   # entroterra (DEM_PERCH=1): laghetti sospesi (Retiro, Casa de Campo) restano terreno; a zero solo l'acqua a quota del fondovalle (< 15 m sul datum)
    water = water & ((G - datum) < 15.0)
Rr = np.where(water, 0.0, np.maximum(G - datum, 0.0)); wet = nd.binary_dilation(water, iterations=1)
taper = np.clip(nd.distance_transform_edt(~wet) * C / TAPER, 0, 1); taper = taper * taper * (3 - 2 * taper)
eb = HALF - np.maximum(np.abs(GX), np.abs(GY)); edge = np.clip(eb / 2500.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
D = EXAG * np.maximum(Rr - FLAT, 0.0) * taper * edge
np.savez_compressed(os.path.join(DATA, 'dem.npz'), D=D.astype(np.float32), x0=float(xs[0]), y0=float(ys[0]), cell=C)
log(f'dem.npz {len(xs)}x{len(ys)} cella {C:.0f} m, DEM_OPEN {OPEN:.0f}, datum {datum:.1f} m ({how}), D max {D.max():.0f} m, medio {D.mean():.1f} m')
for it in filter(None, os.environ.get('DEM_CHECK', '').split(';')):
    nm, la, lo = it.split(':'); x = (float(lo) - LON0) * KX; y = (float(la) - LAT0) * KY; i = int(round((y + HALF) / C)); j = int(round((x + HALF) / C))
    ring = D[max(i - 40, 0):i + 41, max(j - 40, 0):j + 41]
    log(f'  {nm:28s} DSM {S[i, j]:6.1f}  opened {G[i, j]:6.1f}  D {D[i, j]:5.1f} (mediana D entro 1,2 km {np.median(ring):.1f}, residuo {D[i, j] - np.median(ring):+.1f})')
