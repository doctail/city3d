# Rilievo di Parigi -> DATA/dem.npz {D (spostamento verticale in metri), x0, y0, cell}, usato da build_render.py.
# Sorgente: Copernicus GLO-30 DSM, tile N48 E002 (raw_parigi). E' un modello di SUPERFICIE (tetti, alberi): a Parigi il
# costruito e' continuo, quindi si toglie con un'apertura morfologica larga (600 m in citta', 250 m nei boschi/campi)
# e una lisciatura; quota riferita alla Senna (0). Poi, come Siviglia: letti d'acqua di ogni epoca riempiti, rampa a zero
# vicino all'acqua (sponde al livello dei quai), piatto sotto FLAT, esagerazione EXAG sopra (Montmartre ~100 m sulla Senna).
# Uso: python dem_parigi.py RAW_DIR DATA_DIR
import json, math, os, sys
import numpy as np, tifffile
from scipy import ndimage as nd
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
HERE = os.path.dirname(os.path.abspath(__file__))
RAW, DATA = sys.argv[1], sys.argv[2]
CFG = json.load(open(os.path.join(HERE, 'city_parigi.json')))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
FLAT, EXAG, TAPER = CFG.get('dem_flat', 3.0), CFG.get('dem_exag', 1.6), CFG.get('dem_taper', 100.0)
import glob, re
# sfondo vero (29 ott): fino a dem_half (40 km) se ci sono le tile vicine (tools/fetch_far.py le scarica in raw_<citta>/far_tmp);
# senza, solo la tile del centro e 12 km come prima
TILES = {}
for f in glob.glob(f'{RAW}/**/Copernicus_DSM_COG_10_*_DEM.tif', recursive=True):
    m = re.search(r'_([NS])(\d+)_00_([EW])(\d+)_00_DEM', f)
    TILES[((1 if m[1] == 'N' else -1) * int(m[2]), (1 if m[3] == 'E' else -1) * int(m[4]))] = f
HALF = CFG.get('dem_half', 40000) if len(TILES) > 1 else 12000
C = 30.0 if HALF <= 12000 else CFG.get('dem_cell_far', 30.0)
xs = np.arange(-HALF, HALF + 1, C); ys = np.arange(-HALF, HALF + 1, C); GX, GY = np.meshgrid(xs, ys)
lon = LON0 + GX / KX; lat = LAT0 + GY / KY
S = np.zeros(GX.shape)
for (la, lo), f in TILES.items():
    t = tifffile.imread(f).astype(np.float64); ny0, nx0 = t.shape          # 1 grado, nord in alto, pixel-is-point
    m = (lat >= la) & (lat < la + 1) & (lon >= lo) & (lon < lo + 1)
    if m.any(): S[m] = nd.map_coordinates(t, [(la + 1 - lat[m]) * (ny0 - 1), (lon[m] - lo) * (nx0 - 1)], order=1)
print(f'[dem] tile {len(TILES)}, semi-lato {HALF / 1000:.0f} km, cella {C:.0f} m', flush=True)
# via edifici e alberi: apertura (minimo poi massimo) larga, poi lisciatura
OPEN = CFG.get('dem_open_m', 270.0)
G = nd.grey_opening(S, size=(int(OPEN / C), int(OPEN / C)))
G = nd.gaussian_filter(G, 4)
land = json.load(open(f'{DATA}/land.json'))
LG = unary_union([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in land])
ph = json.load(open(f'{DATA}/landphases.json')) if os.path.exists(f'{DATA}/landphases.json') else []
water_now = ~contains_xy(LG, GX, GY)
water_any = water_now | contains_xy(unary_union([Polygon(p['r']).buffer(0) for p in ph]) if ph else Polygon(), GX, GY)
seine = float(np.median(S[water_now & (np.hypot(GX, GY) < 4000)]))   # livello della Senna in centro
R = G - seine
lab_, n_ = nd.label(water_any)
sz = nd.sum(np.ones_like(lab_), lab_, index=np.arange(1, n_ + 1)) * C * C
big = np.isin(lab_, 1 + np.where(sz > 40000)[0])          # solo Senna, Marna e canali: i laghetti dei parchi in collina restano in quota
wet = nd.binary_dilation(big, iterations=1)
idx = nd.distance_transform_edt(wet, return_distances=False, return_indices=True)
Rf = R[tuple(idx)]; Rf = np.where(wet, nd.gaussian_filter(Rf, 2), R)
small = water_any & ~big; Rf = np.where(small, nd.grey_closing(Rf, size=5), Rf)   # laghetti: quota delle sponde
dist = nd.distance_transform_edt(~wet) * C
taper = np.clip(dist / TAPER, 0, 1); taper = taper * taper * (3 - 2 * taper)
eb = HALF - np.maximum(np.abs(GX), np.abs(GY)); edge = np.clip(eb / 2500.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
D = EXAG * np.maximum(Rf - FLAT, 0.0) * taper * edge
np.savez_compressed(f'{DATA}/dem.npz', D=D.astype(np.float32), x0=float(xs[0]), y0=float(ys[0]), cell=C)
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
for nm, (la, lo) in {'Notre-Dame': (48.8530, 2.3499), 'Sacre-Coeur (Montmartre)': (48.8867, 2.3431), 'Belleville (Parc)': (48.8710, 2.3850),
                     'Pantheon (Sainte-Genevieve)': (48.8462, 2.3464), 'Trocadero (Chaillot)': (48.8616, 2.2893), 'Buttes-Chaumont': (48.8809, 2.3828),
                     'Butte-aux-Cailles': (48.8270, 2.3500), 'Opera': (48.8720, 2.3316), 'Mont Valerien': (48.8710, 2.2160)}.items():
    x, y = L(la, lo); i = int((y + HALF) / C); j = int((x + HALF) / C)
    print(f'[dem] {nm:30s} quota sulla Senna {R[i, j]:6.1f} m -> spostamento {D[i, j]:6.1f} m')
print(f'[dem] Senna a {seine:.1f} m (DSM); massimo spostamento {D.max():.0f} m; griglia {len(xs)}x{len(ys)} da {C:.0f} m')
