# Parchi e acqua da un export OpenStreetMap (GeoJSON di overpass-turbo, o JSON "out geom" di Overpass)
# Uso: python osm_extra.py DATA_DIR city_X.json export.geojson
# Uscita: DATA/parks.json (anelli locali) e DATA/land.json ritagliato dall'acqua (fiumi come linee allargate).
import json, math, sys
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, box
from shapely.ops import unary_union
DATA, CFG, SRC = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def P(lon, lat): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def loc(g):
    from shapely.ops import transform
    return transform(lambda x, y, z=None: ((x - LON0) * KX, (y - LAT0) * KY), g)
src = json.load(open(SRC))
feats = src.get('features')
if feats is None:   # formato Overpass "out geom"
    feats = []
    for e in src['elements']:
        if e.get('type') == 'way' and e.get('geometry'):
            co = [(p['lon'], p['lat']) for p in e['geometry']]
            geom = {'type': 'Polygon', 'coordinates': [co]} if co[0] == co[-1] and len(co) > 3 else {'type': 'LineString', 'coordinates': co}
            feats.append({'geometry': geom, 'properties': e.get('tags', {})})
        elif e.get('type') == 'relation' and e.get('members'):   # multipoligoni (es. Nieuwe Maas): ricuci i pezzi "outer"
            from shapely.ops import polygonize, unary_union as _uu
            ls = [LineString([(p['lon'], p['lat']) for p in m['geometry']]) for m in e['members']
                  if m.get('type') == 'way' and m.get('role', 'outer') in ('outer', '') and len(m.get('geometry') or []) > 1]
            polys = list(polygonize(_uu(ls))) if ls else []
            if polys: feats.append({'geometry': _uu(polys).__geo_interface__, 'properties': e.get('tags', {})})
parks, water = [], []
RIVW = CFG.get('river_width', {})   # larghezza (m) dei fiumi disegnati solo come linea
for f in feats:
    p = f.get('properties') or {}; g = f.get('geometry')
    if not g: continue
    try: s = loc(shape(g))
    except Exception: continue
    if p.get('leisure') == 'park' and s.geom_type in ('Polygon', 'MultiPolygon') and s.area > 3000: parks.append(s.buffer(0))
    elif p.get('natural') == 'water' and s.geom_type in ('Polygon', 'MultiPolygon') and s.area > 2500: water.append(s.buffer(0))
    elif p.get('waterway') == 'riverbank' and s.geom_type in ('Polygon', 'MultiPolygon') and s.area > 2500: water.append(s.buffer(0))
    elif p.get('waterway') in ('river', 'canal') and s.geom_type == 'LineString':
        if p.get('waterway') == 'canal' and CFG.get('skip_canals'): continue   # Siviglia: canali d'irrigazione del '900 = righe nere dall'anno zero
        w = RIVW.get(p.get('name', ''), 22 if p.get('waterway') == 'river' else 10); water.append(s.buffer(w / 2, cap_style=2))
L = CFG.get('land_half_m', 30000)
land = box(-L, -L, L, L)
if water: land = land.difference(unary_union(water).buffer(1))
def rings(geom, simp=1.5):
    out = []
    for q in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        if isinstance(q, Polygon) and q.area > 50:
            out.append([[round(x, 1), round(y, 1)] for x, y in list(q.simplify(simp).exterior.coords)[:-1]])
    return out
pr = []
for g in parks: pr += rings(g)
json.dump(pr, open(f'{DATA}/parks.json', 'w'))
# terra con i buchi (laghi, anse del fiume): {"ext": anello, "holes": [anelli]}
lr = []
for q in (land.geoms if hasattr(land, 'geoms') else [land]):
    if isinstance(q, Polygon) and q.area > 50:
        q = q.simplify(2.0)
        lr.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]],
                   'holes': [[[round(x, 1), round(y, 1)] for x, y in list(h.coords)[:-1]] for h in q.interiors if Polygon(h).area > 200]})
json.dump(lr, open(f'{DATA}/land.json', 'w')); open(f'{DATA}/land_v3.ok', 'w').write('ok')
print(f'[osm] parchi {len(pr)}, acque {len(water)}, terra {len(lr)} poligoni', flush=True)
