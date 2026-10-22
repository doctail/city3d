# Acqua a fasi di Siviglia -> DATA/landphases.json + DATA/land.json corretto + edifici spostati dopo la bonifica.
# Il render (build_render.py, blocco "terra a fasi") toglie ogni area di landphases dalla terra di base e la ridisegna
# come lastra di terra visibile solo nella finestra [from, to): fuori dalla finestra si vede l'acqua sotto.
#   - acqua di oggi che prima era terra: from=-9999, to=anno di scavo (Tablada 1926, Vega de Triana 1948, Cartuja 1975)
#   - acqua di ieri che oggi e' terra: from=anno di bonifica, to=9999 (gomito delle Delicias 1950, laguna 1574)
#   - tapon di Chapina: terra solo 1950-1992
# Poligoni e fonti in data_sevilla_src/water_src.json. Uso: python water_sevilla.py DATA_DIR (dopo osm_extra e hist_sevilla)
import json, os, sys
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.prepared import prep

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else 'data'
S = json.load(open(os.path.join(HERE, 'data_sevilla_src', 'water_src.json')))
PH = [('codo', 1950, 9999, 'urban'), ('laguna', 1574, 9999, 'park'), ('tablada', -9999, 1926, 'field'),
      ('west_triana', -9999, 1948, 'field'), ('west_cartuja', -9999, 1975, 'field'), ('chapina', 1950, 1992, 'urban'),
      # collegamento Chapina -> canale ovest (foto aerea IGN 1956): acqua 1948-1990, terra prima e dopo (riempito per l'Expo)
      ('conn_1948', -9999, 1948, 'field'), ('conn_1948', 1990, 9999, 'urban')]
out = []
for k, f, t, c in PH:
    for r in S[k]: out.append({'r': r, 'from': f, 'to': t, 'c': c, 'name': k})
json.dump(out, open(f'{DATA}/landphases.json', 'w'))

# acqua storica che oggi e' terra: va tolta dalla terra di base (la lastra a fasi la copre solo dopo la bonifica)
wet_then = unary_union([Polygon(r).buffer(0) for k in ('codo', 'laguna', 'osm_gap', 'conn_1948') for r in S[k]])   # osm_gap: tratto di darsena senza acqua in OSM
land = json.load(open(f'{DATA}/land.json')); new = []
for r in land:
    g = (Polygon(r['ext'], r.get('holes', [])) if isinstance(r, dict) else Polygon(r)).buffer(0).difference(wet_then)
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon' and q.area > 50:
            new.append({'ext': [list(p) for p in q.exterior.coords[:-1]], 'holes': [[list(p) for p in h.coords[:-1]] for h in q.interiors]})
json.dump(new, open(f'{DATA}/land.json', 'w'))

# niente edifici sull'acqua: finestre in cui ogni area e' ACQUA (complemento delle finestre di terra in PH)
WATER = {'codo': [(-9999, 1950)], 'laguna': [(-9999, 1574)], 'tablada': [(1926, 9999)], 'west_triana': [(1948, 9999)],
         'west_cartuja': [(1975, 9999)], 'chapina': [(-9999, 1950), (1992, 9999)], 'conn_1948': [(1948, 1990)]}
zones = [(prep(Polygon(r).buffer(0)), WATER[k]) for k in WATER for r in S[k]]
def fix(items, is_hist):
    keep = []; moved = 0
    for b in items:
        try: c = Polygon(b['r']).centroid
        except Exception: continue
        ok = True
        for z, wins in zones:
            if not z.contains(c): continue
            for wa, wb in wins:
                d = b.get('d', 99999)
                if b['y'] >= wb or d <= wa: continue           # nessuna sovrapposizione con l'acqua
                if b['y'] < wa and is_hist: b['d'] = wa - 0.5; continue   # demolito quando arriva l'acqua
                if wb < 9999 and (b['y'] + 0 < wb): b['y'] = wb + 2; moved += 1   # costruito dopo la bonifica
                else: ok = False                               # sempre acqua dopo: non puo' esserci
            if is_hist and b['d'] <= b['y']: ok = False
        if ok: keep.append(b)
    return keep, moved
B, m1 = fix(json.load(open(f'{DATA}/buildings.json')), False); json.dump(B, open(f'{DATA}/buildings.json', 'w'))
H, m2 = fix(json.load(open(f'{DATA}/hist.json')), True); json.dump(H, open(f'{DATA}/hist.json', 'w'))
print(f'[water_sevilla] fasi {len(out)}, terra {len(new)} poligoni, edifici spostati {m1}, predecessori corretti {m2}', flush=True)
