# Danimarca, passo 1 (sul pod): dall'estratto OSM (Geofabrik) prende, entro radius_m + 3 km dal centro:
#  - impronte degli edifici con i tag utili (building, building:levels, height, start_date, name, historic, ...)
#  - acqua, parchi (come osm_pbf.py) e linea di costa (natural=coastline: il mare in OSM NON e' un poligono)
# Uso: python osm_dk_raw.py file.osm.pbf city_copenhagen.json prefisso_uscita   -> <prefisso>_buildings.geojson, <prefisso>_env.geojson
import json, math, sys
import osmium, shapely.wkb
from shapely.geometry import box, mapping

SRC, CFG, PRE = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; R = CFG.get('radius_m', 9000) + 3000
DLA = R / 110540; DLO = R / (math.cos(math.radians(LAT0)) * 111320)
BB = box(LON0 - DLO, LAT0 - DLA, LON0 + DLO, LAT0 + DLA)
WKB = osmium.geom.WKBFactory()
BKEYS = ('building', 'building:levels', 'building:part', 'height', 'roof:shape', 'roof:levels', 'start_date', 'construction_date',
         'name', 'historic', 'amenity', 'tourism', 'man_made', 'leisure', 'ref:bygningsnr', 'osak:identifier', 'wikidata')
blds, env, roads = [], [], []
RKEYS = ('highway', 'railway', 'bridge', 'bridge:structure', 'bridge:name', 'layer', 'name', 'lanes', 'width', 'start_date', 'man_made', 'tunnel')

def env_area(t):
    return (t.get('natural') in ('water', 'wetland') or t.get('waterway') == 'riverbank' or t.get('landuse') in ('basin', 'reservoir', 'forest', 'grass', 'cemetery')
            or t.get('leisure') in ('park', 'garden') or t.get('natural') == 'wood')

class H(osmium.SimpleHandler):
    def area(self, a):
        t = a.tags; isb = 'building' in t or 'building:part' in t
        if not isb and not env_area(t): return
        try: g = shapely.wkb.loads(WKB.create_multipolygon(a), hex=True)
        except Exception: return
        if not g.intersects(BB): return
        if isb:
            p = {k: t.get(k) for k in BKEYS if t.get(k)}
            p['osm'] = ('w' if a.from_way() else 'r') + str(a.orig_id())
            blds.append({'type': 'Feature', 'properties': p, 'geometry': mapping(g)})
        else:
            p = {k: t.get(k) for k in ('natural', 'waterway', 'leisure', 'landuse', 'name') if t.get(k)}
            env.append({'type': 'Feature', 'properties': p, 'geometry': mapping(g.intersection(BB))})
    def way(self, w):
        t = w.tags
        if (t.get('highway') or t.get('railway') in ('rail', 'light_rail', 'subway')) and t.get('tunnel') != 'yes' \
                and t.get('highway') not in ('footway', 'path', 'steps', 'corridor', 'elevator', 'bus_stop', 'platform', 'proposed', 'construction') \
                or (t.get('man_made') == 'bridge'):
            try: g = shapely.wkb.loads(WKB.create_linestring(w), hex=True)
            except Exception: g = None
            if g is not None and g.intersects(BB):
                p = {k: t.get(k) for k in RKEYS if t.get(k)}; p['osm'] = 'w' + str(w.id)
                roads.append({'type': 'Feature', 'properties': p, 'geometry': mapping(g)})
            if not t.get('natural'): return
        if t.get('natural') != 'coastline' and t.get('waterway') not in ('river', 'canal'): return
        try: g = shapely.wkb.loads(WKB.create_linestring(w), hex=True)
        except Exception: return
        if not g.intersects(BB.buffer(0.05)): return   # costa: un po' oltre il riquadro, serve per chiudere i poligoni
        p = {k: t.get(k) for k in ('natural', 'waterway', 'name') if t.get(k)}
        env.append({'type': 'Feature', 'properties': p, 'geometry': mapping(g)})

H().apply_file(SRC, locations=True, idx='flex_mem')
json.dump({'type': 'FeatureCollection', 'features': blds}, open(PRE + '_buildings.geojson', 'w'))
json.dump({'type': 'FeatureCollection', 'features': env}, open(PRE + '_env.geojson', 'w'))
json.dump({'type': 'FeatureCollection', 'features': roads}, open(PRE + '_roads.geojson', 'w'))
print('[osm_dk_raw] strade:', len(roads), '| ponti:', sum(1 for f in roads if f['properties'].get('bridge') or f['properties'].get('man_made') == 'bridge'), flush=True)
n = {}
for f in env:
    p = f['properties']; k = p.get('natural') or p.get('leisure') or p.get('landuse') or p.get('waterway'); n[k] = n.get(k, 0) + 1
print('[osm_dk_raw] edifici:', len(blds), '| ambiente:', n, flush=True)
print('[osm_dk_raw] con start_date:', sum(1 for f in blds if 'start_date' in f['properties']),
      '| con livelli:', sum(1 for f in blds if 'building:levels' in f['properties']),
      '| con altezza:', sum(1 for f in blds if 'height' in f['properties']), flush=True)
