# Pittsburgh: ALTEZZE VERE dei footprint da LiDAR USGS 3DEP (bucket pubblico usgs-lidar-public, progetto PA_WesternPA_2_2019, EPT/laszip, EPSG:3857, z in m).
# Metodo: scarica i nodi EPT entro RAGGIO m dal Point (fino a MAXDEPTH), suolo = classe 2 (min per cella 1 m, interpolato lineare sotto gli edifici), superficie =
# quota massima per cella tra i punti non-rumore (esclude classi 7, 9 acqua, 17 ponte, 18). Altezza footprint = percentile 98 della superficie dentro il poligono
# meno il suolo mediano (h98; hmed = mediana, piu' robusta nei blocchi fusi). Gli edifici sono classe 1 (il progetto non classifica la classe 6).
# Uso:  python fetch_pgh_lidar.py RAW_DIR OUT.csv [RAGGIO_m=1000] [MAXDEPTH=11]   (RAW_DIR con fp.csv; OUT: outline_id,h98,hmed,gz,ncell,nok)
# Misurato: R=1000 m, profondita' 11 -> 33 M punti, 30 s di download (16 thread) + ~2 min di calcolo; a profondita' 10 sono ~11 M punti. Fuori dal centro non lanciato.
import io, json, math, os, subprocess, sys, concurrent.futures as cf
import numpy as np, pandas as pd, shapely
RAW, OUT = sys.argv[1:3]; RAD = float(sys.argv[3]) if len(sys.argv) > 3 else 1000.0; MAXD = int(sys.argv[4]) if len(sys.argv) > 4 else 11
BASE = 'https://usgs-lidar-public.s3.amazonaws.com/'; PROJ = 'PA_WesternPA_2_2019'
LAT0, LON0 = 40.4406, -80.0
def get(u):
    for _ in range(4):
        r = subprocess.run(['curl', '-sS', '-f', '-m', '120', u], capture_output=True)
        if r.returncode == 0: return r.stdout
    return None
def main():
    import laspy
    from pyproj import Transformer
    from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
    from skimage.draw import polygon as skpoly
    x0, y0 = Transformer.from_crs(4326, 3857, always_xy=True).transform(LON0, LAT0); s = RAD / math.cos(math.radians(LAT0)); bb = (x0 - s, y0 - s, x0 + s, y0 + s)
    ept = json.loads(get(BASE + PROJ + '/ept.json')); Bd = ept['bounds']; pages = {}; res = {}
    def hpage(k):
        d = get(BASE + PROJ + '/ept-hierarchy/%d-%d-%d-%d.json' % k); return json.loads(d) if d else {}
    def box(d, x, y):
        n = 2 ** d; w = (Bd[3] - Bd[0]) / n; h = (Bd[4] - Bd[1]) / n; return Bd[0] + x * w, Bd[1] + y * h, Bd[0] + (x + 1) * w, Bd[1] + (y + 1) * h
    pages.update(hpage((0, 0, 0, 0)))
    def walk(d, x, y, z):
        b = box(d, x, y)
        if b[2] < bb[0] or b[0] > bb[2] or b[3] < bb[1] or b[1] > bb[3] or d > MAXD: return
        k = '%d-%d-%d-%d' % (d, x, y, z); n = pages.get(k)
        if n is None: return
        if n == -1: pages.update(hpage((d, x, y, z))); n = pages.get(k)
        if n and n > 0: res[k] = n
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1): walk(d + 1, 2 * x + dx, 2 * y + dy, 2 * z + dz)
    walk(0, 0, 0, 0); print('[lidar] nodi', len(res), 'punti', sum(res.values()), flush=True)
    def rd(k):
        d = get(BASE + PROJ + '/ept-data/%s.laz' % k)
        if d is None: return None
        l = laspy.read(io.BytesIO(d)); x = np.asarray(l.x); y = np.asarray(l.y); m = (x >= bb[0]) & (x <= bb[2]) & (y >= bb[1]) & (y <= bb[3])
        return np.c_[x[m] - bb[0], y[m] - bb[1], np.asarray(l.z)[m]].astype(np.float32), np.asarray(l.classification)[m]
    X = []; C = []
    with cf.ThreadPoolExecutor(16) as ex:
        for r in ex.map(rd, list(res)):
            if r is not None: X.append(r[0]); C.append(r[1])
    X = np.concatenate(X); C = np.concatenate(C); W = int(bb[2] - bb[0]) + 1; Hh = int(bb[3] - bb[1]) + 1
    ix = np.clip(X[:, 0].astype(int), 0, W - 1); iy = np.clip(X[:, 1].astype(int), 0, Hh - 1); zz = X[:, 2]
    def rast(mask, desc):
        a = np.full((Hh, W), np.nan, np.float32); v = zz[mask]; o = np.argsort(-v if desc else v); a.ravel()[(iy[mask] * W + ix[mask])[o]] = v[o]; return a
    g = rast(C == 2, True); gm = np.isnan(g); ii, jj = np.where(~gm); k = np.random.RandomState(0).choice(len(ii), min(len(ii), 600000), replace=False)
    lin = LinearNDInterpolator(np.c_[ii, jj][k], g[~gm][k]); nn = NearestNDInterpolator(np.c_[ii, jj][k], g[~gm][k]); gy, gx = np.mgrid[0:Hh:2, 0:W:2]
    G = lin(gy.ravel(), gx.ravel()).reshape(gy.shape); bad = np.isnan(G); G[bad] = nn(gy.ravel()[bad.ravel()], gx.ravel()[bad.ravel()]); G = np.kron(G, np.ones((2, 2), np.float32))[:Hh, :W]
    S = rast(~np.isin(C, [7, 9, 17, 18]), False)
    fp = pd.read_csv(os.path.join(RAW, 'fp.csv'), usecols=['outline_id', 'x', 'y', 'status', 'geometry'])
    lon, lat = Transformer.from_crs(2272, 4326, always_xy=True).transform(fp.x.values, fp.y.values)
    fp = fp[(np.hypot((lon - LON0) * math.cos(math.radians(LAT0)) * 111320, (lat - LAT0) * 110540) <= RAD - 30) & (fp.status != 'demolished')]
    t = Transformer.from_crs(2272, 3857, always_xy=True); rows = []
    for oid, wk in zip(fp.outline_id.values, fp.geometry.values):
        g_ = shapely.from_wkt(wk); vs = []; gs = []
        for p in (g_.geoms if g_.geom_type == 'MultiPolygon' else [g_]):
            c = np.asarray(p.exterior.coords); px, py = t.transform(c[:, 0], c[:, 1]); rr, cc = skpoly(py - bb[1], px - bb[0], shape=S.shape)
            vs.append(S[rr, cc]); gs.append(G[rr, cc])
        v = np.concatenate(vs); gg = np.concatenate(gs); ok = ~np.isnan(v)
        if ok.sum() < 4: rows.append((oid, np.nan, np.nan, np.nan, len(v), int(ok.sum()))); continue
        rows.append((oid, round(float(np.percentile(v[ok], 98) - np.median(gg)), 1), round(float(np.median(v[ok]) - np.median(gg)), 1), round(float(np.median(gg)), 1), len(v), int(ok.sum())))
    pd.DataFrame(rows, columns=['outline_id', 'h98', 'hmed', 'gz', 'ncell', 'nok']).to_csv(OUT, index=False); print('[lidar] footprint', len(rows), '->', OUT)
if __name__ == '__main__': main()
