# Sfondo lontano: far_<citta>.npz (tools/fetch_far.py, dal pod) -> DATA/far.png + DATA/far.json, letti da build_render
# (land_mat 'fields': oltre far_r0 il colore del suolo viene dalla copertura vera, non dalla campagna generica).
#   far.png  R = classe (codice sotto), G = anno in cui la cella diventa costruita ((anno-1600)/430*254, 255 = mai), B = 0
#   classi: 1 bosco, 2 arbusti, 3 prato, 4 campi, 5 costruito, 6 nudo/cava, 7 acqua, 8 zona umida (0 = nessun dato -> campi)
# Anno del costruito: GHSL dal 1975 (dato). Prima del 1975 non esiste un dato globale: per le celle gia' costruite nel 1975
#   l'anno viene dalla griglia di urbanizzazione della citta' (urban_grid.npz, dove c'e') altrimenti da una regola per
#   distanza dal centro [Guessing] dichiarata in far.json ("pre1975"): prima cintura prima, cinture esterne dopo.
#   I nuclei storici (piccole chiazze costruite isolate nel 1975, < far_core_m2) sono villaggi: anno antico (core_year).
# Uso: python tools/far_prep.py city_<citta>.json DATA far_<citta>.npz       (o --fake: prova senza dati del pod, da OSM)
import json, math, os, sys
import numpy as np
from scipy import ndimage as nd
from PIL import Image
CFG = json.load(open(sys.argv[1])); DATA = sys.argv[2]; SRC = sys.argv[3]
F = CFG.get('far', {})
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
ESA = {10: 1, 20: 2, 30: 3, 40: 4, 50: 5, 60: 6, 70: 6, 80: 7, 90: 8, 95: 8, 100: 3}
def log(*a): print('[far_prep]', *a, flush=True)
if SRC == '--fake':
    # PROVA del materiale: copertura da OSM (solo dove c'e' l'estratto) e anni per distanza. Non va nel video.
    import gzip, geopandas as gpd, shapely
    from shapely import contains_xy
    R = 40000.0; cell = 40.0
    xs = np.arange(-R, R + 1, cell); X, Y = np.meshgrid(xs, xs[::-1])
    LC = np.full(X.shape, 40, np.uint8)
    e = gpd.read_file(gzip.open(sys.argv[4]))
    e = e[e.geom_type.isin(['Polygon', 'MultiPolygon'])]
    def loc(g): return shapely.transform(g, lambda a: np.c_[(a[:, 0] - LON0) * KX, (a[:, 1] - LAT0) * KY])
    for cls, m in ((10, e['landuse'].isin(['forest']) | e['natural'].isin(['wood'])), (30, e['landuse'].isin(['grass', 'meadow']) | e['leisure'].isin(['park'])),
                   (50, e['landuse'].isin(['residential', 'industrial', 'commercial', 'retail'])), (80, e['natural'].isin(['water']))):
        g = shapely.union_all([loc(q).buffer(0) for q in e[m].geometry]).simplify(20)
        LC[contains_xy(g, X, Y)] = cls; log('fake', cls, int((LC == cls).sum()))
    D = np.hypot(X, Y)
    nz = nd.gaussian_filter(np.random.default_rng(1).normal(0, 1, D.shape), 30); nz /= nz.std()
    LC[(LC == 40) & (nz > np.interp(D, [9000, 15000, 30000], [-1.5, -0.2, 1.2]))] = 50     # banlieue finta per la prova
    BY = np.where(LC == 50, np.where(D < 20000, 1975, 2000), 9999).astype(np.int16)
    z = {'LC': LC, 'LC_cell': cell, 'BY': BY, 'BY_cell': cell, 'R': R, 'x0': -R, 'y0': R}
else:
    z = dict(np.load(SRC))
R = float(z['R']); lc_cell = float(z['LC_cell']); LC = z['LC']
n = LC.shape[0]; xs = -R + np.arange(n) * lc_cell; X, Y = np.meshgrid(xs, R - np.arange(n) * lc_cell)
cls = np.zeros(LC.shape, np.uint8)
for k, v in ESA.items(): cls[LC == k] = v
# anno del costruito sulla griglia della copertura
BY = z['BY'].astype(np.float32); by_cell = float(z['BY_cell'])
iy = np.clip(((R - Y) / by_cell).astype(int), 0, BY.shape[0] - 1); ix = np.clip(((X + R) / by_cell).astype(int), 0, BY.shape[1] - 1)
by = BY[iy, ix]
built = (cls == 5) | (by < 9000)
by = np.where(built & (by >= 9000), 2021, by)            # costruito per WorldCover ma non per GHSL: dopo il 2020
pre = by <= 1975
dist = np.hypot(X, Y)
P = F.get('pre1975', [[0, 1860], [8000, 1880], [14000, 1925], [22000, 1955], [35000, 1968], [60000, 1972]])   # [Guessing] per distanza
pd_ = np.interp(dist, [p[0] for p in P], [p[1] for p in P])
rng = np.random.default_rng(7); pd_ = pd_ + nd.gaussian_filter(rng.normal(0, 1, dist.shape), 25) * 60   # fronti irregolari, non anelli
# nuclei storici: chiazze costruite isolate gia' nel 1975, piccole -> villaggi antichi
lab, nl = nd.label(pre & built)
area = nd.sum(np.ones_like(lab), lab, index=np.arange(1, nl + 1)) * lc_cell * lc_cell
small = np.isin(lab, 1 + np.flatnonzero(area < F.get('far_core_m2', 400000)))
core = np.zeros(dist.shape, bool)
if nl:   # centro delle chiazze grandi = nucleo antico (le citta' vicine: Versailles, Saint-Denis...): 300 m attorno al centroide
    cms = nd.center_of_mass(pre & built, lab, index=np.arange(1, nl + 1))
    for (cy, cx), a in zip(cms, area):
        if a > 150000:
            cy, cx = int(cy), int(cx); r = int(300 / lc_cell); core[max(0, cy - r):cy + r, max(0, cx - r):cx + r] = True
by = np.where(pre & built, np.minimum(pd_, 1974), by)
by = np.where(pre & built & (small | core), F.get('core_year', 1500), by)
# dentro il modello la crescita la fanno gli edifici veri: qui conta solo fuori (build_render sfuma da far_r0)
G = np.where(built, np.clip((by - 1600) / 430 * 254, 0, 254), 255).astype(np.uint8)
img = np.dstack([cls * 16, G, np.zeros_like(G)]).astype(np.uint8)
Image.fromarray(img, 'RGB').save(f'{DATA}/far.png', optimize=True)
json.dump({'box': [-R, -R, R, R], 'cell': lc_cell, 'pre1975': '[Guessing] anni prima del 1975 per distanza: ' + json.dumps(P),
           'fonti': 'ESA WorldCover 2021 (CC BY 4.0), JRC GHSL GHS-BUILT-S R2023A (CC BY 4.0)' if SRC != '--fake' else 'PROVA da OSM'}, open(f'{DATA}/far.json', 'w'))
log('far.png', img.shape, 'costruito', round(built.mean() * 100, 1), '%; nuclei antichi', int((pre & built & (small | core)).sum()))
