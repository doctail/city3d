# Marsiglia: estratto OSM PACA (.pbf, download.openstreetmap.fr) -> JSON grezzi (lat/lon) per prep_marseille_osm.py.
# Uso: python osm_marseille.py PACA.osm.pbf OUT_DIR       (locale, gratis, ~5-8 min)
# Uscita OUT_DIR/: roads_raw.json (highway/railway, entro 11 km), coast_raw.json (natural=coastline, entro 45 km),
#   water_raw.json (acqua e fiumi, entro 12 km), parks_raw.json, monuments_raw.json (nomi dei monumenti della story).
import json, math, re, sys, os
import osmium, shapely.wkb
from shapely.geometry import box, mapping
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
LAT0, LON0 = 43.2953, 5.3745; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def bb(r): return box(LON0 - r / KX, LAT0 - r / KY, LON0 + r / KX, LAT0 + r / KY)
B_ROAD, B_COAST, B_WATER, B_PARK = bb(11000), bb(45000), bb(25000), bb(12000)
WKB = osmium.geom.WKBFactory()
ROAD_HW = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'living_street', 'unclassified', 'pedestrian',
           'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'service', 'cycleway', 'track', 'footway', 'steps'}
MON = re.compile(r"Notre-Dame de la Garde|Sainte-Marie-Majeure|Cath[eé]drale de la Major|Fort Saint-Jean|Fort Saint-Nicolas|Palais Longchamp|"
                 r"Vieille Charit[eé]|H[oô]tel de [Vv]ille|H[oô]tel-Dieu|Palais de la Bourse|Bourse de Marseille|Arc de Triomphe|Porte d'Aix|"
                 r"Gare (de )?(Marseille[- ])?Saint-Charles|Ch[aâ]teau d'If|Cit[eé] Radieuse|MuCEM|Mus[eé]e des Civilisations|Stade V[eé]lodrome|"
                 r"CMA CGM|La Marseillaise|Transbordeur|Pont transbordeur|Abbaye Saint-Victor|Basilique Saint-Victor|Saint-Vincent-de-Paul|"
                 r"Les Accoules|Pharo|Palais du Pharo|Villa M[eé]diterran[eé]e|Fort d'Entrecasteaux|Panier|Cours Julien|Op[eé]ra de Marseille|"
                 r"Place Castellane|Porte Royale|Hospice de la Charit[eé]|Phare de Planier|Château Borély|Parc Borély|Ch[aâ]teau Borely|Notre-Dame du Mont|"
                 r"Hôtel du D[eé]partement|Alcazar|Nouvelle Cath[eé]drale|Ancienne cath[eé]drale|Chapelle .*Vieille Charit[eé]|Pont Transbordeur|"
                 r"Dieu|CMA|C\.M\.A|Tour CMA|V[eé]lodrome|Orange V|InterContinental|[IÎ]le d'If|Archipel du Frioul|H[oô]pital Caroline|Tour du Fanal|Tour Sainte-Marie|Fort du Pharo|Fort d'Entrecasteaux|Palais de Justice", re.I)
roads, coast, water, parks, mons = [], [], [], [], []
def ctr(g): c = g.representative_point() if g.geom_type != 'Point' else g; return [round(c.x, 6), round(c.y, 6)]
class H(osmium.SimpleHandler):
    def way(self, w):
        t = w.tags
        try:
            if t.get('natural') == 'coastline':
                g = shapely.wkb.loads(WKB.create_linestring(w), hex=True)
                if g.intersects(B_COAST): coast.append([[round(x, 6), round(y, 6)] for x, y in g.coords])
                return
            hw, rw = t.get('highway'), t.get('railway')
            if (hw in ROAD_HW) or rw in ('rail', 'light_rail', 'subway', 'tram'):
                g = shapely.wkb.loads(WKB.create_linestring(w), hex=True)
                if g.intersects(B_ROAD):
                    roads.append({'g': [[round(x, 6), round(y, 6)] for x, y in g.coords], 'hw': hw, 'rw': rw, 'br': t.get('bridge'), 'tn': t.get('tunnel'),
                                  'n': t.get('name'), 'sd': t.get('start_date'), 'lay': t.get('layer'), 'mm': t.get('man_made')})
                return
            if t.get('waterway') in ('river', 'canal', 'stream') :
                g = shapely.wkb.loads(WKB.create_linestring(w), hex=True)
                if g.intersects(B_WATER): water.append({'line': [[round(x, 6), round(y, 6)] for x, y in g.coords], 'ww': t.get('waterway'), 'n': t.get('name'), 'tn': t.get('tunnel')})
        except Exception: pass
    def node(self, n):
        nm = n.tags.get('name') or ''
        if nm and MON.search(nm) and B_ROAD.contains(shapely.geometry.Point(n.location.lon, n.location.lat)):
            mons.append({'name': nm, 'kind': 'node', 'pt': [n.location.lon, n.location.lat], 'tags': {k: n.tags.get(k) for k in ('historic', 'tourism', 'building', 'amenity', 'man_made', 'start_date', 'height', 'wikidata') if n.tags.get(k)}})
    def area(self, a):
        t = a.tags
        nm = t.get('name') or ''
        isw = t.get('natural') == 'water' or t.get('waterway') == 'riverbank' or t.get('landuse') in ('basin', 'reservoir') or t.get('natural') == 'bay'
        ispark = t.get('leisure') == 'park'
        ism = bool(nm and MON.search(nm))
        if not (isw or ispark or ism): return
        try: g = shapely.wkb.loads(WKB.create_multipolygon(a), hex=True)
        except Exception: return
        if isw and g.intersects(B_WATER): water.append({'poly': mapping(g.intersection(B_WATER)), 'n': nm, 'nat': t.get('natural'), 'wt': t.get('water')})
        if ispark and g.intersects(B_PARK): parks.append({'poly': mapping(g.intersection(B_PARK)), 'n': nm})
        if ism and B_ROAD.contains(g.representative_point()):
            mons.append({'name': nm, 'kind': 'area', 'pt': ctr(g), 'poly': mapping(g), 'tags': {k: t.get(k) for k in ('historic', 'tourism', 'building', 'amenity', 'man_made', 'start_date', 'height', 'building:levels', 'wikidata') if t.get(k)}})
import shapely.geometry
mons = []
H().apply_file(SRC, locations=True, idx='flex_mem')
for nm, d in (('roads_raw', roads), ('coast_raw', coast), ('water_raw', water), ('parks_raw', parks), ('monuments_raw', mons)):
    json.dump(d, open(os.path.join(OUT, nm + '.json'), 'w'))
    print(nm, len(d), flush=True)
