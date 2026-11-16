# Marsiglia, quartiere Saint-Jean prima del 1943: isolati della pianta tedesca 1940 -> DATA/hist_blocks.json (letto da kit/hist_kit.py blocks_pass).
# Uso: python prep_marseille_sj.py DATA_DIR      (locale, gratis). Ritaglia i 347 isolati di prova sull'anello history.fires 'Saint-Jean quarter 1943'
# e sulla terra attuale (land.json); nessun edificio fuori anello. Anni di nascita: triangolare 1650-1925 moda 1800 (quartiere antico, [Guessing]);
# altezze 10-16 m (3-5 piani, [Guessing]); morte: il fuoco 'destroy' della story la anticipa nella finestra del dinamitaggio.
import json, os, sys
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union, transform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import geo
DATA = sys.argv[1]; ROOT = geo.ROOT; ERO = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0   # margine (m) lasciato libero lungo strade/banchine nel riempimento
st = geo.load_story('marseille'); P = geo.Proj.of(st)
fire = [f for f in st['history']['fires'] if f.get('destroy')][0]
RING = Polygon(P.ring(fire['ring'])).buffer(0)
land = unary_union([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in json.load(open(os.path.join(DATA, 'land.json')))])
G = json.load(open(os.path.join(ROOT, 'cities/marseille/mappe/saintjean_isolati_test_1940.geojson')))
out = []; tot = 0.0
for f in G['features']:
    g = transform(lambda x, y, z=None: (P.L(y, x)[0], P.L(y, x)[1]), shape(f['geometry'])).buffer(0)
    q = g.intersection(RING).intersection(land)
    for part in (q.geoms if hasattr(q, 'geoms') else [q]):
        if part.geom_type == 'Polygon' and part.area > 40:
            part = part.simplify(0.4); tot += part.area
            out.append({'name': 'Saint-Jean blocks (1940 plan)', 'id': f['properties']['id'], 'r': [[round(x, 2), round(y, 2)] for x, y in list(part.exterior.coords)[:-1]],
                        'born': [1650, 1925, 1800], 'h': [10.0, 16.0], 'd': round(fire['y1'] + 0.07, 3), 'avoid_at': fire['y']})
# Riempimento (GENERATO, non dalla pianta): il campione di 347 isolati esclude i blocchi fusi > 20.000 m2 e ne lascia fuori altri; la terra nell'anello
# non coperta dagli isolati ne' dalle strade (roads.json attive nel 1943) viene lottizzata alla stessa densita' (margine ERO m da strade/banchine).
rd = unary_union([Polygon(r['r']).buffer(0) for r in json.load(open(os.path.join(DATA, 'roads.json'))) if r['y'] <= fire['y'] and Polygon(r['r']).intersects(RING)])
used = unary_union([Polygon(o['r']).buffer(0) for o in out]).buffer(1.0)
inf = RING.intersection(land).difference(used).difference(rd.buffer(1.0)).buffer(-ERO).buffer(ERO * 0.5)
n0 = len(out); ainf = 0.0
for part in (inf.geoms if hasattr(inf, 'geoms') else [inf]):
    if part.geom_type == 'Polygon' and part.area > 120:
        part = part.simplify(0.4); ainf += part.area
        out.append({'name': 'Saint-Jean infill (generated)', 'r': [[round(x, 2), round(y, 2)] for x, y in list(part.exterior.coords)[:-1]],
                    'born': [1650, 1925, 1800], 'h': [10.0, 16.0], 'd': round(fire['y1'] + 0.07, 3), 'avoid_at': fire['y']})
print(f'riempimento generato: {len(out) - n0} aree, {ainf / 1e4:.2f} ha (margine {ERO} m)')
json.dump(out, open(os.path.join(DATA, 'hist_blocks.json'), 'w'), separators=(',', ':'))
print(f'hist_blocks.json: {len(out)} isolati, {tot / 1e4:.2f} ha dentro l\'anello ({RING.area / 1e4:.1f} ha)')
