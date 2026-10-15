# Acqua e parchi da un estratto OSM .pbf (Geofabrik), senza Overpass.
# Uso: python osm_pbf.py file.osm.pbf city_X.json uscita.geojson
# Tiene: natural=water, waterway=riverbank, landuse=basin/reservoir, leisure=park (aree, anche multipoligoni)
#        waterway=river/canal (linee). Solo entro radius_m + 3 km dal centro. Uscita: GeoJSON per osm_extra.py.
import json, math, sys
import osmium, shapely.wkb
from shapely.geometry import box, mapping

SRC, CFG, OUT = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; R = CFG.get('radius_m', 9000) + 3000
DLA = R / 110540; DLO = R / (math.cos(math.radians(LAT0)) * 111320)
BB = box(LON0 - DLO, LAT0 - DLA, LON0 + DLO, LAT0 + DLA)
WKB = osmium.geom.WKBFactory()
feats = []

def area_ok(t):
    return (t.get('natural') == 'water' or t.get('waterway') == 'riverbank' or t.get('landuse') in ('basin', 'reservoir')
            or t.get('leisure') == 'park')

def props(t):
    p = {k: t.get(k) for k in ('natural', 'waterway', 'leisure', 'landuse', 'name') if t.get(k)}
    if p.get('landuse') in ('basin', 'reservoir'): p['natural'] = 'water'
    if p.get('waterway') == 'riverbank': p['natural'] = 'water'
    return p

class H(osmium.SimpleHandler):
    def area(self, a):
        if not area_ok(a.tags): return
        try: g = shapely.wkb.loads(WKB.create_multipolygon(a), hex=True)
        except Exception: return
        if not g.intersects(BB): return
        g = g.intersection(BB)
        if g.is_empty: return
        feats.append({'type': 'Feature', 'properties': props(a.tags), 'geometry': mapping(g)})
    def way(self, w):
        if w.tags.get('waterway') not in ('river', 'canal'): return
        try: g = shapely.wkb.loads(WKB.create_linestring(w), hex=True)
        except Exception: return
        if not g.intersects(BB): return
        feats.append({'type': 'Feature', 'properties': props(w.tags), 'geometry': mapping(g.intersection(BB))})

H().apply_file(SRC, locations=True, idx='flex_mem')
json.dump({'type': 'FeatureCollection', 'features': feats}, open(OUT, 'w'))
n = {}
for f in feats:
    k = f['properties'].get('leisure') or f['properties'].get('natural') or f['properties'].get('waterway'); n[k] = n.get(k, 0) + 1
print('[osm_pbf] elementi:', len(feats), n, flush=True)
