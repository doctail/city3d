# Marsiglia, passo 2 (locale, gratis): JSON grezzi di osm_marseille.py + DEM Copernicus -> DATA/land.json, roads.json, dem.npz, landmarks.json
# Uso: python prep_marseille_osm.py RAW_OSM_DIR DEM_DIR DATA_DIR [land|roads|dem|landmarks|all]
# Stesso flusso di Lione/Parigi: land (osm_extra.py: terra con buchi {ext, holes}; qui il mare viene dalla linea di costa),
# roads (fetch_dk_roads.py: nastri chiari, un quadrilatero per segmento, unione per anno e triangolazione; anno = urbanizzazione
# misurata sugli edifici di DATA/buildings.json), dem (dem_parigi.py: DSM -> apertura morfologica, quota rispetto al mare, rampa a 0 sulla riva).
import json, math, os, sys, collections, re
import numpy as np, shapely
from shapely.geometry import Polygon, LineString, Point, box, shape, MultiPolygon
from shapely.ops import unary_union, polygonize, transform
from shapely.prepared import prep
from shapely.strtree import STRtree
from scipy.spatial import cKDTree
RAW, DEMD, DATA = sys.argv[1:4]; WHAT = sys.argv[4] if len(sys.argv) > 4 else 'all'
LAT0, LON0 = 43.2953, 5.3745; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = 9000.0; LAND_HALF = 40000.0
def log(*a): print('[marseille_osm]', *a, flush=True)
def P(lon, lat): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def loc(g): return transform(lambda x, y, z=None: ((np.asarray(x) - LON0) * KX, (np.asarray(y) - LAT0) * KY), g)
def L(f): return json.load(open(os.path.join(RAW, f)))
def rings(geom, simp=2.0, amin=50):
    out = []
    for q in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        if isinstance(q, Polygon) and q.area > amin:
            q = q.simplify(simp)
            out.append({'ext': [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]],
                        'holes': [[[round(x, 1), round(y, 1)] for x, y in list(h.coords)[:-1]] for h in q.interiors if Polygon(h).area > 200]})
    return out

# ------------------------------------------------------------------------------------------------ land
def build_land():
    from shapely.ops import unary_union, linemerge
    BOX = box(-LAND_HALF, -LAND_HALF, LAND_HALF, LAND_HALF)
    segs = []   # tratti di costa (m locali), con il verso OSM (terra a sinistra)
    for co in L('coast_raw.json'):
        ln = loc(LineString(co))
        c = ln.intersection(BOX)
        for g in (c.geoms if hasattr(c, 'geoms') else [c]):
            if isinstance(g, LineString) and g.length > 1: segs.append(g)
    log('tratti di costa', len(segs))
    lines = unary_union(segs + [BOX.exterior])
    polys = list(polygonize(lines))
    # classifica ogni poligono: punto a sinistra di un tratto di costa che sta sul suo bordo
    segpts = []   # (midpoint, normale sinistra)
    for g in segs:
        cs = list(g.coords)
        for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
            dl = math.hypot(x1 - x0, y1 - y0)
            if dl < 0.5: continue
            segpts.append(((x0 + x1) / 2, (y0 + y1) / 2, -(y1 - y0) / dl, (x1 - x0) / dl))
    tree = cKDTree([(a[0], a[1]) for a in segpts])
    land = []
    for pg in polys:
        votes = 0; tot = 0
        bd = pg.exterior
        n = max(8, int(bd.length // 400))
        for k in range(min(n, 40)):
            pt = bd.interpolate((k + 0.5) / min(n, 40), normalized=True)
            d, i = tree.query((pt.x, pt.y))
            if d > 1.0: continue          # tratto del bordo del box, non costa
            a = segpts[i]; q = Point(a[0] + 3 * a[2], a[1] + 3 * a[3])
            votes += 1 if pg.contains(q) else -1; tot += 1
        if tot and votes > 0: land.append(pg)
    log('poligoni', len(polys), '| terra', len(land))
    LAND = unary_union(land).buffer(0)
    # acqua interna (laghi, stagni, Huveaune) tolta dalla terra
    wat = []
    for w in L('water_raw.json'):
        if 'poly' in w:
            s = loc(shape(w['poly']))
            if s.geom_type in ('Polygon', 'MultiPolygon') and s.area > 2500: wat.append(s.buffer(0).simplify(1.0))
        elif w.get('ww') == 'river' and not w.get('tn'):
            s = loc(LineString(w['line'])); wat.append(s.buffer(11, cap_style=2))
    log('acque interne', len(wat), '(poligoni >2500 m2 + fiumi)')
    W = unary_union(wat).buffer(1) if wat else Polygon(); log('unione acque fatta')
    LANDW = LAND.difference(W)
    lr = rings(LANDW)
    json.dump(lr, open(os.path.join(DATA, 'land.json'), 'w')); open(os.path.join(DATA, 'land_v3.ok'), 'w').write('ok')
    # parchi (come osm_extra.py)
    pr = []
    for p_ in L('parks_raw.json'):
        s = loc(shape(p_['poly'])).buffer(0)
        if s.area > 3000: pr += [r_['ext'] for r_ in rings(s, 1.5)]
    json.dump(pr, open(os.path.join(DATA, 'parks.json'), 'w'))
    # prove: centro (Vieux-Port: acqua), Notre-Dame de la Garde (terra), Frioul, If
    chk = {'Vieux-Port (acqua)': (43.2950, 5.3720), 'Notre-Dame de la Garde (terra)': (43.2840, 5.3713), 'Ile Pomegues/Frioul (terra)': (43.2745, 5.3030),
           'Chateau d\'If (terra)': (43.2799, 5.3256), 'mare aperto sud-ovest (acqua)': (43.20, 5.30), 'Etang di Berre (acqua)': (43.45, 5.12)}
    LP = prep(LANDW)
    for k, (la, lo) in chk.items(): log(f'  {k:38s} -> {"TERRA" if LP.contains(Point(P(lo, la))) else "ACQUA"}')
    log(f'land.json: {len(lr)} poligoni, {sum(len(r_["holes"]) for r_ in lr)} buchi; parks.json {len(pr)}')
    return LANDW

# ------------------------------------------------------------------------------------------------ roads
W_ = {'motorway': 22, 'trunk': 18, 'primary': 16, 'secondary': 13, 'tertiary': 10, 'residential': 7, 'living_street': 6, 'unclassified': 7,
      'pedestrian': 7, 'motorway_link': 9, 'trunk_link': 9, 'primary_link': 9, 'secondary_link': 8, 'tertiary_link': 7}
def build_roads(LANDW=None):
    from collections import defaultdict
    if LANDW is None:
        lr = json.load(open(os.path.join(DATA, 'land.json')))
        LANDW = unary_union([Polygon(r_['ext'], r_.get('holes', [])).buffer(0) for r_ in lr])
    LP = prep(LANDW)
    B = json.load(open(os.path.join(DATA, 'buildings.json')))
    bxy = np.array([[sum(p[0] for p in o['r']) / len(o['r']), sum(p[1] for p in o['r']) / len(o['r'])] for o in B]); by = np.array([o['y'] for o in B], float)
    bt = cKDTree(bxy)
    cache = {}
    def urban_year(x, y):
        # 20o percentile degli anni degli edifici entro 120 m (almeno 3), poi entro 300 m, poi il piu' vicino entro 700 m
        for rad, mn in ((120, 3), (300, 3)):
            ii = bt.query_ball_point([x, y], rad)
            if len(ii) >= mn: return float(np.percentile(by[ii], 20)), rad
        d, i = bt.query([x, y], distance_upper_bound=700)
        return (float(by[i]), 700) if i < len(by) else (None, None)
    raw = L('roads_raw.json'); rd, stat = [], collections.Counter()
    for r in raw:
        hw, rw = r['hw'], r['rw']
        israil = rw in ('rail', 'light_rail')
        w = 8 if israil else W_.get(hw, 0)
        if not w: continue
        if r.get('tn') in ('yes', 'culvert', 'building_passage', 'flooded'): stat['tunnel_saltati'] += 1; continue
        g = loc(LineString(r['g']))
        c = g.centroid
        if c.x ** 2 + c.y ** 2 > (R + 100) ** 2: continue
        # anno: urbanizzazione misurata (media su 3 punti del tratto)
        ys = []
        for fr in (0.2, 0.5, 0.8):
            p = g.interpolate(fr, normalized=True); v, rad = urban_year(p.x, p.y)
            if v is not None: ys.append(v)
        if ys: y = int(np.median(ys)) + 2; stat['anno_da_edifici'] += 1
        elif hw in ('motorway', 'trunk', 'motorway_link', 'trunk_link') : y = 1975; stat['anno_default_1975_Guessing'] += 1
        else: continue            # niente edifici entro 700 m: strada di campagna/collina, non si disegna
        m = re.search(r'(1[2-9]\d\d|20[0-2]\d)', str(r.get('sd') or ''))
        if m: y = max(min(y, int(m.group(1)) + 2), 1200) if int(m.group(1)) < y else y   # start_date OSM: solo per anticipare, mai posticipare oltre l'urbanizzazione
        if israil: y = max(y, 1848); stat['ferrovie'] += 1      # Avignone-Marsiglia 1848 (Gare Saint-Charles)
        rd.append((g, w, int(max(y, 1200)) // 2 * 2, int(israil)))
    log('segmenti-via', len(rd), dict(stat))
    quads = defaultdict(list)
    for g, w, y, israil in rd:
        cs = list(g.simplify(1.0).coords)
        for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
            dl = math.hypot(x1 - x0, y1 - y0)
            if dl < 1: continue
            ux, uy = (x1 - x0) / dl, (y1 - y0) / dl; e = w / 2; nx, ny = -uy * e, ux * e
            ax_, ay_ = x0 - ux * e * 0.5, y0 - uy * e * 0.5; bx_, by_ = x1 + ux * e * 0.5, y1 + uy * e * 0.5
            q = [(ax_ + nx, ay_ + ny), (ax_ - nx, ay_ - ny), (bx_ - nx, by_ - ny), (bx_ + nx, by_ + ny)]
            if not LP.contains(Point((x0 + x1) / 2, (y0 + y1) / 2)): continue
            quads[(y, israil)].append(Polygon(q))
    # unione per anno (i ponti sopra il porto/il mare sono esclusi dal test "terra"; i ponti veri vanno in bridges.json se servono)
    roads = []; nT = 0
    # unione per gruppo (anno a bin di 2 anni, ferrovia a parte) e, per ogni tessera da 1,5 km, ogni gruppo esclude l'area gia' coperta dai gruppi
    # precedenti della stessa tessera (niente facce sovrapposte sullo stesso piano: si facevano ombra). Per tessere: l'esclusione globale era
    # troppo lenta (18+ min).
    TILE = 1500.0; keys = sorted(quads); U = {}
    for k in keys: U[k] = unary_union(quads[k]).simplify(0.3)
    nt = int(math.ceil(2 * (R + 200) / TILE)); x0 = -(R + 200)
    for ix in range(nt):
        for iy in range(nt):
            tb = box(x0 + ix * TILE, x0 + iy * TILE, x0 + (ix + 1) * TILE, x0 + (iy + 1) * TILE); done_ = Polygon()
            for k in keys:
                u = U[k]
                if not u.intersects(tb): continue
                u = u.intersection(tb)
                if done_.area: u = u.difference(done_)
                done_ = unary_union([done_, u]) if not u.is_empty else done_
                for q in (u.geoms if hasattr(u, 'geoms') else [u]):
                    if not isinstance(q, Polygon) or q.area < 5: continue
                    for t in shapely.constrained_delaunay_triangles(q).geoms:
                        if t.area > 0.05: roads.append({'r': [[round(x, 2), round(yv, 2)] for x, yv in list(t.exterior.coords)[:-1]], 'y': int(k[0]), 'rail': k[1]}); nT += 1
    json.dump(roads, open(os.path.join(DATA, 'roads.json'), 'w'), separators=(',', ':'))
    yy = [r_['y'] for r_ in roads]
    log(f'roads.json: {len(roads)} triangoli da {len(rd)} segmenti-via OSM; anni {min(yy)}..{max(yy)}; mediana {int(np.median(yy))}; ferrovia {sum(r_["rail"] for r_ in roads)}')
    return len(rd), len(roads)

# ------------------------------------------------------------------------------------------------ dem
def build_dem():
    import tifffile, glob
    from scipy import ndimage as nd
    from shapely import contains_xy
    HALF, C = 20000.0, 30.0            # come Lione: griglia 1334x1334 da 30 m
    FLAT, EXAG, TAPER = 3.0, 1.6, 100.0   # default del kit (dem_parigi.py)
    TILES = {}
    for f in glob.glob(f'{DEMD}/Copernicus_DSM_COG_10_*_DEM.tif'):
        m = re.search(r'_([NS])(\d+)_00_([EW])(\d+)_00_DEM', f)
        if os.path.getsize(f) < 10000: continue
        TILES[((1 if m[1] == 'N' else -1) * int(m[2]), (1 if m[3] == 'E' else -1) * int(m[4]))] = f
    xs = np.arange(-HALF, HALF + 1, C); ys = np.arange(-HALF, HALF + 1, C); GX, GY = np.meshgrid(xs, ys)
    lon = LON0 + GX / KX; lat = LAT0 + GY / KY
    S = np.zeros(GX.shape)       # mare = tile mancante = 0
    for (la, lo), f in TILES.items():
        t = tifffile.imread(f).astype(np.float64); ny0, nx0 = t.shape
        m = (lat >= la) & (lat < la + 1) & (lon >= lo) & (lon < lo + 1)
        if m.any(): S[m] = nd.map_coordinates(t, [(la + 1 - lat[m]) * (ny0 - 1), (lon[m] - lo) * (nx0 - 1)], order=1)
    log(f'dem: tile {sorted(TILES)}, semi-lato {HALF / 1000:.0f} km, cella {C:.0f} m')
    OPEN = float(os.environ.get("DEM_OPEN", 150.0))   # Parigi 270 m (citta piatta e continua); Marsiglia ha colline di roccia strette: 270 m dimezzava Notre-Dame de la Garde
    G = nd.grey_opening(S, size=(int(OPEN / C), int(OPEN / C))); G = nd.gaussian_filter(G, 4)
    lr = json.load(open(os.path.join(DATA, 'land.json')))
    LG = unary_union([Polygon(r_['ext'], r_.get('holes', [])).buffer(0) for r_ in lr])
    water_now = ~contains_xy(LG, GX, GY)
    sea = float(np.median(S[water_now & (np.hypot(GX, GY) < 6000)])) if (water_now & (np.hypot(GX, GY) < 6000)).any() else 0.0
    Rr = np.where(water_now, 0.0, np.maximum(G - sea, 0.0))
    wet = nd.binary_dilation(water_now, iterations=1)
    dist = nd.distance_transform_edt(~wet) * C
    taper = np.clip(dist / TAPER, 0, 1); taper = taper * taper * (3 - 2 * taper)
    eb = HALF - np.maximum(np.abs(GX), np.abs(GY)); edge = np.clip(eb / 2500.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
    D = EXAG * np.maximum(Rr - FLAT, 0.0) * taper * edge
    np.savez_compressed(os.path.join(DATA, 'dem.npz'), D=D.astype(np.float32), x0=float(xs[0]), y0=float(ys[0]), cell=C)
    log(f'dem.npz: griglia {len(xs)}x{len(ys)} da {C:.0f} m, livello mare {sea:.1f} m (DSM), spostamento massimo {D.max():.0f} m, medio {D.mean():.1f} m')
    for nm, (la, lo) in {'Notre-Dame de la Garde': (43.2840, 5.3713), 'Palais Longchamp': (43.3042, 5.3955), 'Vieux-Port (Hotel de Ville)': (43.2965, 5.3738),
                         'Le Panier (Vieille Charite)': (43.3005, 5.3680), 'Gare Saint-Charles': (43.3032, 5.3805), 'Marseilleveyre (433 m)': (43.2144, 5.3589),
                         'Velodrome': (43.2699, 5.3959)}.items():
        x, y = P(lo, la); i = int((y + HALF) / C); j = int((x + HALF) / C)
        log(f'  {nm:32s} DSM {S[i, j]:6.1f} m  spostamento {D[i, j]:6.1f} m')

# ------------------------------------------------------------------------------------------------ landmarks
# Candidati monumento da OSM (nome, coordinate, impronta, altezza). landmarks.json "vero" (parti 3D) lo costruisce `python -m kit build`
# dai preset della story: qui si scrive uno scheletro nel suo schema ({parts: [], clear: [], labels, _kit}) con le coordinate reali.
WANT = [  # (chiave, nome da mostrare, regex del nome OSM, tipo preferito)
    ('notre_dame_garde', 'Notre-Dame de la Garde', r'^Basilique Notre-Dame de la Garde$', 'area'),
    ('major', 'Cathedrale de la Major', r'^Cath[eé]drale de la Major$', 'area'),
    ('fort_saint_jean', 'Fort Saint-Jean', r'^Fort Saint-Jean$', 'area'),
    ('fort_saint_nicolas', 'Fort Saint-Nicolas', r'^Fort Saint-Nicolas$', 'area'),
    ('palais_longchamp', 'Palais Longchamp', r'^Palais Longchamp$', 'area'),
    ('vieille_charite', 'Vieille Charite', r'^(Chapelle de la )?Vieille Charit[eé]$|^Centre de la Vieille Charit[eé]$', 'area'),
    ('hotel_de_ville', 'Hotel de Ville', r'^H[oô]tel de ville de Marseille$', 'area'),
    ('hotel_dieu', 'Hotel-Dieu', r'Hôtel-Dieu|Hotel-Dieu|Hôtel Dieu|Grand H[oô]tel-Dieu|InterContinental', 'area'),
    ('bourse', 'Palais de la Bourse', r'^Palais de la Bourse$', 'area'),
    ('porte_d_aix', "Arc de Triomphe / Porte d'Aix", r"^Porte d'Aix$", 'area'),
    ('gare_saint_charles', 'Gare Saint-Charles', r'^Gare de Marseille-Saint-Charles$', 'area'),
    ('chateau_d_if', "Chateau d'If", r"^Château d'If$", 'area'),
    ('cite_radieuse', 'Cite Radieuse (Unite d\'Habitation)', r'Unité d\'Habitation', 'area'),
    ('mucem', 'MuCEM (J4)', r"^Musée des Civilisations de l'Europe et de la Méditerranée$", 'area'),
    ('velodrome', 'Stade Velodrome', r'V[eé]lodrome', 'area'),
    ('cma_cgm', 'Tour CMA CGM', r'CMA', 'area'),
    ('la_marseillaise', 'Tour La Marseillaise', r'^Tour La Marseillaise$', 'area'),
    ('pharo', 'Palais du Pharo', r'^Palais du Pharo$', 'area'),
    ('saint_victor', 'Abbaye Saint-Victor', r'^Basilique Saint-Victor$', 'area'),
    ('opera', 'Opera de Marseille', r'^Opéra de Marseille$', 'area'),
    ('palais_justice', 'Palais de Justice', r'^Palais de justice$', 'area'),
    ('villa_mediterranee', 'Villa Mediterranee', r'^Villa Méditerranée$', 'area'),
    ('transbordeur', 'Pont transbordeur (detruit 1944)', r'ransbordeur', 'node'),
]
def build_landmarks():
    M = L('monuments_raw.json'); out = []; labels = []; miss = []
    for key, show, rx, kind in WANT:
        c = [m for m in M if re.search(rx, m['name'], re.I)]
        ca = [m for m in c if m['kind'] == 'area']; cn = [m for m in c if m['kind'] == 'node']
        pool = ca or cn
        if key in ('hotel_dieu', 'cma_cgm', 'velodrome') and ca:   # preferisci l'impronta piu' grande
            pool = sorted(ca, key=lambda m: -(loc(shape(m['poly'])).area))
        if key == 'fort_saint_nicolas' and ca: pool = sorted(ca, key=lambda m: -(loc(shape(m['poly'])).area))
        if not pool: miss.append(key); continue
        m = pool[0]; x, y = P(*m['pt'])
        area = round(loc(shape(m['poly'])).area, 0) if 'poly' in m else None
        t = m['tags']; hh = None
        try: hh = float(str(t.get('height', '')).replace(',', '.')) if t.get('height') else None
        except Exception: pass
        rec = {'key': key, 'name': show, 'osm_name': m['name'], 'lat': round(m['pt'][1], 6), 'lon': round(m['pt'][0], 6), 'x': round(x, 1), 'y': round(y, 1),
               'dist_vieux_port_m': round(math.hypot(x, y)), 'osm_kind': m['kind'], 'footprint_m2': area, 'height_osm_m': hh, 'start_date_osm': t.get('start_date'), 'wikidata': t.get('wikidata'), 'tags': t}
        out.append(rec); labels.append({'name': show, 'x': round(x, 1), 'y': round(y, 1)})
    json.dump(out, open(os.path.join(DATA, 'landmarks_osm.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump({'parts': [], 'clear': [], 'labels': labels, '_kit': {'slug': 'marseille', 'source': 'osm candidates (prep_marseille_osm.py): SCHELETRO senza parti 3D, `python -m kit build marseille` lo sovrascrive dai preset della story', 'landmarks': 0}},
              open(os.path.join(DATA, 'landmarks.json'), 'w'), ensure_ascii=False)
    log(f'landmarks_osm.json: {len(out)} monumenti con coordinate; mancanti in OSM: {miss}')
    for r in out: log(f'  {r["key"]:20s} ({r["lat"]:.5f},{r["lon"]:.5f}) x={r["x"]:8.1f} y={r["y"]:8.1f} fp={r["footprint_m2"]} h={r["height_osm_m"]} [{r["osm_kind"]}]')

os.makedirs(DATA, exist_ok=True)
LW = None
if WHAT in ('land', 'all'): LW = build_land()
if WHAT in ('roads', 'all'): build_roads(LW)
if WHAT in ('dem', 'all'): build_dem()
if WHAT in ('landmarks', 'all'): build_landmarks()
