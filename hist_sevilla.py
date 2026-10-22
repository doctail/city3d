# Strato storico di Siviglia (dal 1248). Il Catasto ha l'anno dell'ULTIMA ricostruzione/riforma: nel centro murato solo
# 16 edifici su 8.530 hanno un anno prima del 1850. Quindi:
#  1) fix_years(): nelle zone storiche (mura, Triana, Arenal, arrabales) gli edifici bassi (<= 4 piani) prendono l'anno
#     di urbanizzazione della zona (sono il tessuto storico rifatto, non edifici nuovi): niente "centro che nasce nel '900".
#     Quelli alti / grandi blocchi tengono l'anno del Catasto e ricevono un predecessore (build() di hist_nyc).
#  2) urban_year(x, y): zone storiche a mano + fronte urbano moderno dal Catasto (10o percentile per cella di 300 m,
#     urban_grid_sevilla.json).
#  3) LOST: edifici scomparsi in piazze aperte demolendo (Plaza Nueva, Encarnacion), con anno di demolizione.
# Fonti e date in PROSSIMA_SIVIGLIA.md. Tutto approssimato e dichiarato come ricostruzione nella descrizione.
# Origine (0, 0) = Giralda. Metri: x est, y nord.
# Uso: python hist_sevilla.py DATA_DIR   (DATA/buildings.json viene corretto in place, poi DATA/hist.json)
import json, math, os, random, sys
from shapely.geometry import Polygon, Point, box
from shapely.prepared import prep

HERE = os.path.dirname(os.path.abspath(__file__))
LAT0, LON0 = 37.386194, -5.992417
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)

def interp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a)
    return pts[-1][1]

_W = json.load(open(os.path.join(HERE, 'data_sevilla_src', 'walls_1248.json')))['ring']
WALL_P = Polygon(_W); WALL = prep(WALL_P)
# laguna de la Feria (oggi Alameda de Hercules): acqua fino al 1574, attorno case dal 1574 [V]
ALAMEDA_P = box(-175, 1060, -40, 1660)
ALAMEDA = prep(ALAMEDA_P.buffer(70))
# Arenal: tra le mura e il fiume, porto delle Indie (Casa de Contratacion 1503): urbanizzato 1490-1600
ARENAL_P = Polygon([(-268, -332), (-184, -43), (-361, 111), (-560, 365), (-660, 640), (-760, 600), (-700, 300),
                    (-520, 60), (-400, -250), (-352, -417)])
ARENAL = prep(ARENAL_P)
TRIANA_CASTLE = L(37.38660, -6.00248)        # castello di San Jorge (oggi mercato di Triana)
ARRABALES = [(L(37.38250, -5.98130), [(0, 1290), (0.15, 1400), (0.35, 1560), (0.5, 1650)]),   # San Bernardo
             (L(37.40580, -5.98860), [(0, 1520), (0.2, 1560), (0.45, 1700)]),                 # Macarena (Cinco Llagas 1546)
             (L(37.39000, -5.98250), [(0, 1480), (0.25, 1600), (0.4, 1720)]),                 # San Roque (Puerta de Carmona)
             (L(37.39700, -5.98200), [(0, 1500), (0.2, 1620), (0.35, 1740)])]                 # extramuros Puerta del Sol/Osario
_G = json.load(open(os.path.join(HERE, 'urban_grid_sevilla.json'))); _GC = _G['cell']; _GP = _G['p10']

def wob(x, y): return 6 * math.sin(x / 170.0) + 5 * math.sin(y / 230.0 + x / 410.0)

def zone(x, y):
    """(anno, nome zona) per le zone storiche; None fuori."""
    p = Point(x, y)
    if WALL.contains(p):
        if ALAMEDA.contains(p): return 1574 + abs(wob(x, y)) * 2, 'alameda'
        # orti a nord (San Gil, Macarena, Omnium Sanctorum): riempiti tra XIII e XVI secolo
        # 1225: con le variazioni casuali di build() (+10 e +12 anni) tutto il tessuto e' gia' in piedi nel 1248
        return (interp(y, [(1150, 1225), (1450, 1300), (1750, 1480)]) if y > 1150 else 1225), 'mura'
    if ARENAL.contains(p): return interp(math.hypot(x + 300, y - 50) / 1000, [(0, 1490), (0.3, 1530), (0.6, 1600)]), 'arenal'
    d = math.hypot(x - TRIANA_CASTLE[0], y - TRIANA_CASTLE[1]) / 1000
    if d < 0.9 and x < -700:
        return interp(d, [(0, 1225), (0.2, 1300), (0.45, 1500), (0.7, 1620), (0.9, 1780)]), 'triana'
    for (cx, cy), crv in ARRABALES:
        d = math.hypot(x - cx, y - cy) / 1000
        if d < crv[-1][0]: return interp(d, crv), 'arrabal'
    return None

def front(x, y):
    k = f'{int(x // _GC)},{int(y // _GC)}'
    v = _GP.get(k)
    if v is None: return 2100.0
    return max(1860.0, v - 4)

def urban_year(x, y):
    z = zone(x, y)
    if z: return z[0] + (wob(x, y) if z[1] != 'mura' or y > 1150 else 0)
    return front(x, y) + wob(x, y)

def pred_year(x, y):
    """Per i predecessori: solo zone storiche e periferie antiche (fronte < 1940). I quartieri del 1950-1990
    sono nati su campi: nessuna casa demolita prima."""
    if zone(x, y): return urban_year(x, y)
    f = front(x, y)
    return f + wob(x, y) if f < 1940 else 3000.0

def era_height(u, rnd):
    if u < 1700: return rnd.uniform(6.5, 9.5)      # casa a patio, 2 piani
    if u < 1850: return rnd.uniform(8, 11)         # 2-3 piani
    if u < 1920: return rnd.uniform(10, 14)        # 3-4 piani (regionalismo)
    return rnd.uniform(12, 19)

# edifici scomparsi in spazi oggi vuoti (anello in m locali, anno di comparsa, anno di demolizione) [V date, L contorni]
_PN = L(37.38915, -5.99585); _EN = L(37.39318, -5.99178)
# Plaza Nueva: convento di San Francisco 1270-1840 (repo, confermato da Fabio 22 ott); la piazza si urbanizza 1848 -> 1857
#  (PLAZAS: lastricato a strisce, scritto in landmarks.json come parti). Encarnacion: convento demolito nel 1811
#  (scheda), mercato 1842 (repo) - 1973 (repo).
LOST = [(box(_PN[0] - 45, _PN[1] - 60, _PN[0] + 45, _PN[1] + 60), 1270, 1840.5, 13.0, 'convento San Francisco'),
        (box(_EN[0] - 75, _EN[1] - 35, _EN[0] + 75, _EN[1] + 35), 1248, 1811.5, 9.0, 'isolato Encarnacion'),
        (box(_EN[0] - 60, _EN[1] - 28, _EN[0] + 60, _EN[1] + 28), 1842, 1973.5, 7.0, 'mercato Encarnacion')]
# piazze nuove: (rettangolo, anno inizio, anno fine, strisce, colore). Lastricato 0-0,3 m (quota libera, sopra isolati 0,12 e parchi 0,25)
PLAZAS = [(box(_PN[0] - 45, _PN[1] - 60, _PN[0] + 45, _PN[1] + 60), 1848, 1857, 6, '#d6ccb6', 'Plaza Nueva')]

def plazas(DATA):
    path = f'{DATA}/landmarks.json'
    LM = json.load(open(path)) if os.path.exists(path) else {'parts': [], 'labels': [], 'clear': []}
    LM['parts'] = [p for p in LM['parts'] if not p.get('plaza')]
    for poly, y0, y1, n, col, name in PLAZAS:
        x0, ya, x1, yb = poly.bounds
        for i in range(n):
            r = [[x0 + (x1 - x0) * i / n, ya], [x0 + (x1 - x0) * (i + 1) / n, ya], [x0 + (x1 - x0) * (i + 1) / n, yb], [x0 + (x1 - x0) * i / n, yb]]
            LM['parts'].append({'name': name, 't': 'prism', 'r': [[round(v, 2) for v in q] for q in r], 'z0': 0.0, 'z1': 0.3,
                                'c': col, 'a': 0.05, 'y': round(y0 + (y1 - y0) * i / max(1, n - 1), 2), 'plaza': 1,
                                'cx': round(sum(q[0] for q in r) / 4, 2), 'cy': round(sum(q[1] for q in r) / 4, 2)})
    LM.setdefault('labels', []); LM.setdefault('clear', [])
    json.dump(LM, open(path, 'w'))
    print(f'[hist_sevilla] piazze: {len(PLAZAS)}', flush=True)

def fix_years(DATA, seed=21):
    blds = json.load(open(f'{DATA}/buildings.json')); rnd = random.Random(seed); n = 0
    for b in blds:
        try: c = Polygon(b['r']).centroid
        except Exception: continue
        z = zone(c.x, c.y)
        if not z or b['h'] > 13.5 or b['y'] >= 1990: continue
        u = z[0] + rnd.uniform(0, 8)
        if b['y'] > u: b['y'] = int(u); n += 1
    json.dump(blds, open(f'{DATA}/buildings.json', 'w'))
    print(f'[hist_sevilla] anni corretti nelle zone storiche: {n} edifici', flush=True)

# edifici simbolo con l'anno del Catasto sbagliato (= ultima riforma), date della scheda di Fabio:
# (lat, lon, raggio m, area minima m2, anno inizio, anno fine o None, nome). Con anno fine il palazzo cresce lento
# per tutto il cantiere (build_render: 'y1').
ICON_YEARS = [(37.39176, -5.97535, 200, 20000, 1991, None, 'Santa Justa'),
              (37.37722, -5.98694, 250, 10000, 1914, 1929, 'Plaza de Espana'),
              (37.39318, -5.99178, 80, 3000, 2005, 2011, 'Metropol Parasol (base)')]
def fix_icons(DATA):
    blds = json.load(open(f'{DATA}/buildings.json'))
    for la, lo, rad, amin, yr, y1, name in ICON_YEARS:
        x, y = L(la, lo)
        for b in blds:
            if math.hypot(b['r'][0][0] - x, b['r'][0][1] - y) < rad and Polygon(b['r']).area > amin:
                print(f'[hist_sevilla] {name}: {b["y"]} -> {yr}' + (f'-{y1}' if y1 else ''), flush=True); b['y'] = yr
                if y1: b['y1'] = y1
    json.dump(blds, open(f'{DATA}/buildings.json', 'w'))

def lost(DATA):
    hist = json.load(open(f'{DATA}/hist.json')); rnd = random.Random(3)
    for poly, y0, d, h, name in LOST:
        ring = [[round(x, 2), round(yv, 2)] for x, yv in list(poly.exterior.coords)[:-1]]
        hist.append({'r': ring, 'h': h, 'y': y0, 'd': d, 'name': name})
    json.dump(hist, open(f'{DATA}/hist.json', 'w'))
    print(f'[hist_sevilla] aggiunti {len(LOST)} edifici scomparsi', flush=True)

if __name__ == '__main__':
    DATA = sys.argv[1] if len(sys.argv) > 1 else 'data'
    sys.path.insert(0, HERE)
    from hist_nyc import build
    if not os.path.exists(f'{DATA}/years_fixed.ok'):
        fix_years(DATA); open(f'{DATA}/years_fixed.ok', 'w').write('ok')
    fix_icons(DATA)
    build(DATA, pred_year, era_height=era_height)
    lost(DATA)
    plazas(DATA)
