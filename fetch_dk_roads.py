# Copenaghen: strade e ponti da OSM (osm_roads.geojson del pod) -> DATA/roads.json e DATA/bridges.json per build_render.py
# Strade: nastri piatti chiari sul suolo (Cornerstone: strade chiare, isolati scuri), anno = urbanizzazione della zona.
# Ponti: solo i tratti che attraversano l'acqua (land.json), impalcato rialzato; anni veri per i ponti principali.
# Uso: python fetch_dk_roads.py RAW_DIR DATA_DIR city_copenhagen.json
import json, math, sys, os
import numpy as np, geopandas as gpd, shapely
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union
from shapely.prepared import prep
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAW, DATA, CFG = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 9000)
hist = __import__(CFG['hist']); urban_year = hist.urban_year
def log(*a): print('[roads]', *a, flush=True)
def loc(g): return shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY])

# anno di costruzione (primo ponte nel punto) [Likely] da verificare prima di metterli a schermo
BRIDGE_YEAR = {'Knippelsbro': 1620, 'Langebro': 1690, 'Lille Langebro': 2019, 'Inderhavnsbroen': 2016, 'Cirkelbroen': 2015,
               'Bryggebroen': 2006, 'Teglværksbroen': 2010, 'Bryghusbroen': 2019, 'Dronning Louises Bro': 1887,
               'Sjællandsbroen': 1959, 'Kalvebod Bølge': 2013, 'Marmorbroen': 1745, 'Højbro': 1300, 'Holmens Bro': 1680,
               'Børsbroen': 1640, 'Slotsholmsgade': 1650, 'Knippelsbrogade': 1620, 'Metro M1': 2002, 'Metro M2': 2002,
               'Øresundsbanen': 1999, 'Cykelslangen': 2014, 'Ørestads Boulevard': 1997, 'Kalvebod Brygge': 1990}
# passerelle iconiche che in OSM mancano o non hanno il tag ponte: (lat, lon) inizio, fine, larghezza m, anno
EXTRA = [('Inderhavnsbroen', (55.67975, 12.59325), (55.67830, 12.59600), 9, 2016),
         ('Bryggebroen', (55.66420, 12.56390), (55.66560, 12.56980), 7, 2006)]
# anno dagli edifici reali vicini alle sponde (25o percentile entro 200 m): i ponti moderni nei quartieri nuovi
_b = json.load(open(f'{DATA}/buildings.json'))
_bxy = np.array([[sum(p_[0] for p_ in o['r']) / len(o['r']), sum(p_[1] for p_ in o['r']) / len(o['r'])] for o in _b])
_by = np.array([o['y'] for o in _b])
from scipy.spatial import cKDTree
_bt = cKDTree(_bxy)
def near_year(x, y):
    ii = _bt.query_ball_point([x, y], 200)
    return float(np.percentile(_by[ii], 25)) if len(ii) >= 5 else 0
W = {'motorway': 22, 'trunk': 18, 'primary': 16, 'secondary': 13, 'tertiary': 10, 'residential': 7, 'living_street': 6,
     'unclassified': 7, 'pedestrian': 7, 'motorway_link': 9, 'primary_link': 9, 'secondary_link': 8, 'tertiary_link': 7,
     'cycleway': 4, 'service': 5, 'track': 4}
STREET = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'living_street', 'unclassified', 'pedestrian',
          'motorway_link', 'primary_link', 'secondary_link', 'tertiary_link'}

r = gpd.read_file(f'{RAW}/osm_roads.geojson')
r['geometry'] = [loc(g) for g in r.geometry]
land = json.load(open(f'{DATA}/land.json'))
LG = unary_union([Polygon(q['ext'], q.get('holes', [])).buffer(0) for q in land]); LP = prep(LG)
water_core = LG.envelope.buffer(0).difference(LG)   # acqua (mare, porto, canali, laghi)

roads, bridges = [], []
for g, hw, rw, br, mm, nm, bn in zip(r.geometry, r.highway, r.railway, r.bridge, r.man_made, r['name'], r.get('bridge:name', r['name'])):
    if g is None or g.is_empty: continue
    c = g.centroid
    if c.x ** 2 + c.y ** 2 > R ** 2: continue
    israil = isinstance(rw, str) and rw in ('rail', 'light_rail', 'subway')
    w = 8 if israil else W.get(hw, 0)
    if not w: continue
    if isinstance(br, str) and br not in ('no',) or mm == 'bridge':
        wet = g.intersection(water_core)
        if wet.is_empty or wet.length < 8: continue          # cavalcavia su strade/ferrovie: niente
        name = bn if isinstance(bn, str) else nm if isinstance(nm, str) else ''
        y = BRIDGE_YEAR.get(name)
        if y is None:
            ends = [g.coords[0], g.coords[-1]]
            y = max(max(urban_year(*e) for e in ends) + 3, min(near_year(*e) for e in ends))
            if israil: y = max(y, 1847)
        if mm == 'bridge' and g.is_ring:   # contorno del ponte disegnato in OSM: e' gia' l'impalcato
            q = Polygon(g.coords).buffer(0)
            if q.area > 30: bridges.append({'r': [[round(x, 1), round(yv, 1)] for x, yv in list(q.exterior.coords)[:-1]], 'y': int(y), 'name': name, 'w': 0, 'rail': 0})
            continue
        span = g.intersection(wet.buffer(12)) if not wet.is_empty else g   # tratto sull'acqua + 12 m di attacco a terra
        for seg in (span.geoms if hasattr(span, 'geoms') else [span]):
            if seg.length < 6: continue
            poly = seg.buffer(w / 2, cap_style=2, join_style=2)
            for q in (poly.geoms if hasattr(poly, 'geoms') else [poly]):
                bridges.append({'r': [[round(x, 1), round(yv, 1)] for x, yv in list(q.exterior.coords)[:-1]], 'y': int(y),
                                'name': name, 'w': w, 'rail': int(israil)})
        continue
    if hw not in STREET and not israil: continue
    y = urban_year(c.x, c.y) + 2
    if israil: y = max(y, 1847)
    poly = g.buffer(w / 2, cap_style=2, join_style=2).intersection(LG)
    for q in (poly.geoms if hasattr(poly, 'geoms') else [poly]):
        if isinstance(q, Polygon) and q.area > 20:
            roads.append({'r': [[round(x, 1), round(yv, 1)] for x, yv in list(q.simplify(0.8).exterior.coords)[:-1]], 'y': int(y), 'rail': int(israil)})
for name, a_, b_, w, y in EXTRA:
    ln = LineString([((a_[1] - LON0) * KX, (a_[0] - LAT0) * KY), ((b_[1] - LON0) * KX, (b_[0] - LAT0) * KY)])
    q = ln.buffer(w / 2, cap_style=2)
    bridges.append({'r': [[round(x, 1), round(yv, 1)] for x, yv in list(q.exterior.coords)[:-1]], 'y': y, 'name': name, 'w': w, 'rail': 0})
json.dump(roads, open(f'{DATA}/roads.json', 'w')); json.dump(bridges, open(f'{DATA}/bridges.json', 'w'))
log('strade', len(roads), '| ponti sull\'acqua', len(bridges))
named = {}
for b in bridges:
    if b['name']: named[b['name']] = b['y']
log('ponti con nome:', dict(sorted(named.items(), key=lambda kv: kv[1])))
