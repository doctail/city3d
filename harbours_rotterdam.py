# Bacini portuali di Rotterdam con l'anno di scavo: prima di quell'anno sono terra (polder o golena), dopo acqua.
# Senza questo, nel 1340 si vedrebbero gia' Waalhaven, Maashaven ecc. (scavati 1870-1960).
# Metodo: acqua = quadrato meno terra (land.json); canale del fiume = acqua vicina alla linea mediana della Nieuwe Maas
# disegnata in OSM (waterway=river: Nieuwe Maas, Scheur, Oude Maas...); bacini = acqua fuori dal canale, nelle zone del
# porto, con anno per zona. Anni approssimati. Le strisce sottili lungo le rive (fiume piu' largo del canale) restano acqua.
# Uso: python harbours_rotterdam.py DATA_DIR city_rotterdam.json osm_rotterdam.json -> DATA/harbours.json [{"r", "y"}]
import json, sys
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
import math

DATA, CFG, OSM = sys.argv[1], json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
L = CFG.get('land_half_m', 20000)
land = unary_union([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in json.load(open(f'{DATA}/land.json'))])
water = box(-L, -L, L, L).difference(land)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
RIV = ('Nieuwe Maas', 'Scheur', 'Oude Maas', 'Noord', 'Lek', 'Hollandsche IJssel', 'Nieuwe Waterweg')
lines = [LineString([((x - LON0) * KX, (y - LAT0) * KY) for x, y in f['geometry']['coordinates']])
         for f in OSM['features'] if f['properties'].get('waterway') == 'river' and f['properties'].get('name') in RIV
         and f['geometry']['type'] == 'LineString']
channel = unary_union(lines).buffer(CFG.get('channel_half_m', 320))
basins = water.difference(channel)

# zone: (x0, y0, x1, y1, anno di scavo). La prima zona che contiene il centroide vince.
ZONES = [
    (-1000, -1150, 1000, -250, None),     # porti antichi del centro (Leuvehaven, Oude Haven, Wijnhaven, Haringvliet): restano
    (800, -2100, 2700, -800, 1875),       # Feijenoord: Binnenhaven, Spoorweghaven, Koningshaven (1873-1880)
    (-1600, -3200, 800, -1500, 1898),     # Rijnhaven (1895), Maashaven (1905), Katendrecht
    (-2500, -2300, -500, -1500, 1900),    # Parkhaven, Sint Jobshaven, Schiehaven, Coolhaven
    (-4800, -2600, -2500, -1200, 1918),   # Vierhavens (1914), Merwehaven (1932), IJsselhaven, Lekhaven
    (-5000, -4600, -1600, -2500, 1918),   # Waalhaven (1907-1930)
    (-6600, -5600, -3800, -2900, 1958),   # Eemhaven e bacini del dopoguerra
    (-7600, -2700, -5000, -1500, 1905),   # Schiedam: Wilhelminahaven e altri
    (-8600, -2500, -6500, -1400, 1928),   # Vulcaanhaven, Wiltonhaven
    (-11000, -5000, -7000, -3000, 1936),  # Pernis: petroleumhavens
]
out = []; tot = {}
for g in (basins.geoms if hasattr(basins, 'geoms') else [basins]):
    if not isinstance(g, Polygon) or g.area < 12000: continue   # sotto 1,2 ha: canali e fossi, restano acqua
    if g.area / g.length < 30: continue                          # striscia sottile lungo la riva: e' fiume
    c = g.centroid; yr = 'none'
    for x0, y0, x1, y1, y_ in ZONES:
        if x0 < c.x < x1 and y0 < c.y < y1: yr = y_; break
    if yr in ('none', None): continue
    out.append({'r': [[round(x, 1), round(y, 1)] for x, y in list(g.simplify(2.0).exterior.coords)[:-1]], 'y': yr})
    tot[yr] = tot.get(yr, 0) + g.area / 1e4
json.dump(out, open(f'{DATA}/harbours.json', 'w'))
print('[harbours]', len(out), 'bacini;', ', '.join(f'{k}: {v:.0f} ha' for k, v in sorted(tot.items())), flush=True)
