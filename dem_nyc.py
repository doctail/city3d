# Rilievo di New York -> DATA/dem.npz {D, x0, y0, cell}. Come build_dem di prep_marseille_osm.py (Copernicus GLO-30 DSM, griglia 1334x1334 da 30 m, semi-lato 20 km,
# apertura morfologica DEM_OPEN, quota sul mare, rampa a 0 sulla riva, esagerazione 1,6). Uso: python dem_nyc.py DEM_DIR DATA_DIR  (DEM_OPEN default 600 m: FiDi: 54 m di DSM residuo a 600, 125 a 300; Washington Heights scende da 63 a 10 m)
import glob, json, math, os, re, sys
import numpy as np, tifffile
from scipy import ndimage as nd
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
DEMD, DATA = sys.argv[1:3]
LAT0, LON0 = 40.758, -73.985; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
HALF, C = 20000.0, 30.0; FLAT, EXAG, TAPER = 3.0, 1.6, 100.0
def log(*a): print('[dem_nyc]', *a, flush=True)
TILES = {}
for f in glob.glob(f'{DEMD}/Copernicus_DSM_COG_10_*_DEM.tif'):
    m = re.search(r'_([NS])(\d+)_00_([EW])(\d+)_00_DEM', f); TILES[((1 if m[1] == 'N' else -1) * int(m[2]), (1 if m[3] == 'E' else -1) * int(m[4]))] = f
xs = np.arange(-HALF, HALF + 1, C); ys = np.arange(-HALF, HALF + 1, C); GX, GY = np.meshgrid(xs, ys); lon = LON0 + GX / KX; lat = LAT0 + GY / KY
S = np.zeros(GX.shape)
for (la, lo), f in TILES.items():
    t = tifffile.imread(f).astype(np.float64); ny0, nx0 = t.shape; m = (lat >= la) & (lat < la + 1) & (lon >= lo) & (lon < lo + 1)
    if m.any(): S[m] = nd.map_coordinates(t, [(la + 1 - lat[m]) * (ny0 - 1), (lon[m] - lo) * (nx0 - 1)], order=1)
log('tile', sorted(TILES), 'celle senza dati (0):', int((S == 0).sum()))
OPEN = float(os.environ.get('DEM_OPEN', 600.0))
G = nd.gaussian_filter(nd.grey_opening(S, size=(int(OPEN / C), int(OPEN / C))), 4)
lr = json.load(open(os.path.join(DATA, 'land.json')))
LG = unary_union([(Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0) for r in lr])
water = ~contains_xy(LG, GX, GY)
sea = float(np.median(S[water & (np.hypot(GX, GY) < 6000)]))
Rr = np.where(water, 0.0, np.maximum(G - sea, 0.0)); wet = nd.binary_dilation(water, iterations=1)
taper = np.clip(nd.distance_transform_edt(~wet) * C / TAPER, 0, 1); taper = taper * taper * (3 - 2 * taper)
eb = HALF - np.maximum(np.abs(GX), np.abs(GY)); edge = np.clip(eb / 2500.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
D = EXAG * np.maximum(Rr - FLAT, 0.0) * taper * edge
np.savez_compressed(os.path.join(DATA, 'dem.npz'), D=D.astype(np.float32), x0=float(xs[0]), y0=float(ys[0]), cell=C)
log(f'dem.npz {len(xs)}x{len(ys)} cella {C:.0f} m, mare {sea:.1f} m, D max {D.max():.0f} m, medio {D.mean():.1f} m')
for nm, (la, lo) in {'Midtown (Empire State)': (40.7484, -73.9857), 'Financial District': (40.7075, -74.0089), 'Washington Heights (Fort Tryon)': (40.8615, -73.9319), 'Central Park Belvedere': (40.7794, -73.9693), 'Downtown Brooklyn': (40.6929, -73.9856), 'Jersey City Palisades': (40.7500, -74.0450)}.items():
    x = (lo - LON0) * KX; y = (la - LAT0) * KY; i = int((y + HALF) / C); j = int((x + HALF) / C); log(f'  {nm:32s} DSM {S[i, j]:6.1f}  opened {G[i, j]:6.1f}  D {D[i, j]:5.1f}')
