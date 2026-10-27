# Lettura dei layer ALPAGE (GeoPackage, Lambert 93) nelle coordinate locali della citta' (metri, x est, y nord, origine city_<citta>.json).
# Uso: from tools.alpage import Alpage; A = Alpage('raw_parigi/alpage', cfg); g = A.layer('Ilots_1791')  -> GeoDataFrame locale, geometrie valide
import glob, math, os
import numpy as np, geopandas as gpd, shapely

class Alpage:
    def __init__(self, root, cfg):
        self.root = root; self.lat0, self.lon0 = cfg['lat0'], cfg['lon0']
        self.kx = math.cos(math.radians(self.lat0)) * 111320; self.ky = 110540; self._c = {}
    def path(self, name):
        f = glob.glob(os.path.join(self.root, '**', name + '.gpkg'), recursive=True)
        if not f: raise FileNotFoundError(name)
        return f[0]
    def layer(self, name):
        if name in self._c: return self._c[name]
        g = gpd.read_file(self.path(name))
        if g.crs is None or (g.crs.to_epsg() or 2154) != 4326: g = g.set_crs(2154, allow_override=True).to_crs(4326)
        g['geometry'] = [None if x is None else shapely.make_valid(shapely.transform(x, lambda c: np.c_[(c[:, 0] - self.lon0) * self.kx, (c[:, 1] - self.lat0) * self.ky])) for x in g.geometry]
        g = g[g.geometry.notna() & ~g.geometry.is_empty].set_geometry('geometry').set_crs(None, allow_override=True)
        self._c[name] = g; return g
