# Sfondo lontano VERO per qualsiasi citta' (Fabio, 29 ott: "tutte le citta' sembrano della stessa regione, una accanto all'altra").
# Oltre il raggio del modello (8-11 km) la terra era una pianura generica uguale ovunque. Qui si scaricano, per +-R km attorno
# al centro, tre strati aperti e si ricampionano sulla griglia locale (metri, origine lat0/lon0, come tutto il resto):
#   - rilievo: Copernicus GLO-30 DSM (AWS, licenza Copernicus, libero)                      -> D (m), cella 90 m
#   - copertura del suolo 2021: ESA WorldCover 10 m v200 (AWS, CC BY 4.0)                     -> LC (classi ESA), cella 40 m
#   - urbanizzato per epoca 1975/1990/2000/2015/2020: JRC GHSL GHS-BUILT-S R2023A 100 m (CC BY 4.0) -> BY (primo anno con
#     superficie costruita >= 15% della cella; 9999 = mai), cella 100 m
# Uscita: OUT/far_<citta>.npz (da caricare in chat; il resto lo fa far_<citta> in chat e build_render lo legge da DATA/far.npz).
# Uso sul pod (CPU basta, ~10 min):  python3 tools/fetch_far.py city_<citta>.json /workspace/raw_<citta> [R_km=40]
import json, math, os, sys, subprocess, zipfile, io
def pip(*p): subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--break-system-packages', *p], check=False)
try: import rasterio, pyproj, numpy as np, requests
except ImportError: pip('rasterio', 'pyproj', 'numpy', 'requests'); import rasterio, pyproj, numpy as np, requests
from rasterio.windows import from_bounds
CFG = json.load(open(sys.argv[1])); OUT = sys.argv[2]; RKM = float(sys.argv[3]) if len(sys.argv) > 3 else 40.0
name = os.path.basename(sys.argv[1])[5:-5]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = RKM * 1000; os.makedirs(OUT, exist_ok=True); TMP = os.path.join(OUT, 'far_tmp'); os.makedirs(TMP, exist_ok=True)
def log(*a): print('[far]', *a, flush=True)
def get(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return dst
    log('scarico', url)
    with requests.get(url, stream=True, timeout=120, headers={'User-Agent': 'city3d'}) as r:
        if r.status_code != 200: log('  ERRORE', r.status_code); return None
        with open(dst + '.part', 'wb') as f:
            for ch in r.iter_content(1 << 20): f.write(ch)
    os.rename(dst + '.part', dst); return dst
dlat, dlon = R / KY, R / KX
la0, la1, lo0, lo1 = LAT0 - dlat, LAT0 + dlat, LON0 - dlon, LON0 + dlon
def grid(cell):
    xs = np.arange(-R, R + 1, cell); X, Y = np.meshgrid(xs, xs[::-1])   # riga 0 = nord
    return X, Y, LON0 + X / KX, LAT0 + Y / KY
def sample(paths, LON, LAT, crs_tf=None, nodata=0, resamp_mean=False):
    out = np.full(LON.shape, nodata, dtype=np.float32)
    for p in paths:
        with rasterio.open(p) as ds:
            if crs_tf is not None: xx, yy = crs_tf.transform(LON, LAT)
            else: xx, yy = LON, LAT
            rows, cols = ds.index(xx.ravel(), yy.ravel())
            rows = np.asarray(rows).reshape(LON.shape); cols = np.asarray(cols).reshape(LON.shape)
            ok = (rows >= 0) & (rows < ds.height) & (cols >= 0) & (cols < ds.width)
            if not ok.any(): continue
            r0, r1, c0, c1 = rows[ok].min(), rows[ok].max() + 1, cols[ok].min(), cols[ok].max() + 1
            a = ds.read(1, window=rasterio.windows.Window(c0, r0, c1 - c0, r1 - r0))
            out[ok] = a[rows[ok] - r0, cols[ok] - c0]
    return out
res = {'x0': -R, 'y0': R, 'R': R, 'lat0': LAT0, 'lon0': LON0}
# 1) rilievo
tiles = []
for la in range(math.floor(la0), math.floor(la1) + 1):
    for lo in range(math.floor(lo0), math.floor(lo1) + 1):
        ns = f"{'N' if la >= 0 else 'S'}{abs(la):02d}"; ew = f"{'E' if lo >= 0 else 'W'}{abs(lo):03d}"
        n = f'Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM'
        p = get(f'https://copernicus-dem-30m.s3.amazonaws.com/{n}/{n}.tif', os.path.join(TMP, n + '.tif'))
        if p: tiles.append(p)
X, Y, LON, LAT = grid(90.0)
res['D'] = sample(tiles, LON, LAT, nodata=0).astype(np.float32); res['D_cell'] = 90.0
log('rilievo', res['D'].shape, 'min', res['D'].min(), 'max', res['D'].max())
# 2) copertura del suolo ESA WorldCover 2021 (tile 3x3 gradi, angolo SW multiplo di 3)
wc = []
for la in range(3 * math.floor(la0 / 3), 3 * math.floor(la1 / 3) + 1, 3):
    for lo in range(3 * math.floor(lo0 / 3), 3 * math.floor(lo1 / 3) + 1, 3):
        t = f"{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}"
        p = get(f'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{t}_Map.tif', os.path.join(TMP, f'wc_{t}.tif'))
        if p: wc.append(p)
X, Y, LON, LAT = grid(40.0)
res['LC'] = sample(wc, LON, LAT, nodata=0).astype(np.uint8); res['LC_cell'] = 40.0
log('copertura', {int(k): int(v) for k, v in zip(*np.unique(res['LC'], return_counts=True))})
# 3) GHSL urbanizzato per epoca (Mollweide 54009, tile da 1000 km: R = riga da nord, C = colonna da ovest)
moll = pyproj.Transformer.from_crs('EPSG:4326', 'ESRI:54009', always_xy=True)
X, Y, LON, LAT = grid(100.0)
mx, my = moll.transform(np.array([lo0, lo1, lo0, lo1]), np.array([la0, la0, la1, la1]))
tl = sorted({(int((9000000 - y) // 1e6) + 1, int((x + 18041000) // 1e6) + 1) for x, y in zip(mx, my)})
BY = np.full(LON.shape, 9999, np.int16); res['BY_epochs'] = []
for ep in (1975, 1990, 2000, 2015, 2020):
    ps = []
    for (r_, c_) in tl:
        base = f'GHS_BUILT_S_E{ep}_GLOBE_R2023A_54009_100_V1_0_R{r_}_C{c_}'
        z = get(f'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E{ep}_GLOBE_R2023A_54009_100/V1-0/tiles/{base}.zip', os.path.join(TMP, base + '.zip'))
        if not z: continue
        with zipfile.ZipFile(z) as zf:
            tif = [n for n in zf.namelist() if n.endswith('.tif')][0]; zf.extract(tif, TMP); ps.append(os.path.join(TMP, tif))
    if not ps: log('GHSL', ep, 'MANCANTE'); continue
    S = sample(ps, LON, LAT, crs_tf=moll, nodata=0)       # m2 costruiti nella cella da 100x100 m
    BY = np.where((BY == 9999) & (S >= 1500), ep, BY); res['BY_epochs'].append(ep)
    log('GHSL', ep, 'celle costruite', int((S >= 1500).sum()))
res['BY'] = BY; res['BY_cell'] = 100.0
np.savez_compressed(os.path.join(OUT, f'far_{name}.npz'), **res)
log('FATTO', os.path.join(OUT, f'far_{name}.npz'), round(os.path.getsize(os.path.join(OUT, f'far_{name}.npz')) / 1e6, 1), 'MB')
