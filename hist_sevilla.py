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

GIRALDA = (-12.2, -0.3, (0.995, 0.097))   # centro e asse della torre (dall'incavo nel Catasto della Cattedrale)
def _sq(cx, cy, half, ux, uy):
    vx, vy = -uy, ux
    return [[round(cx + sx * half * ux + sy * half * vx, 2), round(cy + sx * half * uy + sy * half * vy, 2)] for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]

def _ring_wedges(outer, inner, n=36):
    """anello (outer - inner) diviso in n spicchi dal centro dell'arena: prismi semplici (il render non fa buchi)."""
    from shapely.geometry import Polygon as P_
    c = inner.centroid; R = 400; out = []
    ring = outer.difference(inner)
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        tri = P_([(c.x, c.y), (c.x + R * math.cos(a0), c.y + R * math.sin(a0)), (c.x + R * math.cos((a0 + a1) / 2), c.y + R * math.sin((a0 + a1) / 2)),
                  (c.x + R * math.cos(a1), c.y + R * math.sin(a1))])
        g = ring.intersection(tri)
        for q in getattr(g, 'geoms', [g]):
            if q.geom_type == 'Polygon' and q.area > 2: out.append([[round(x, 2), round(y, 2)] for x, y in list(q.exterior.coords)[:-1]])
    return out

def icons(DATA):
    """Landmark a stadi (regola di Fabio, 22 ott): solo se la scheda ha almeno 3 fasi datate e la forma cambia in modo
    visibile; tra uno stadio e l'altro la forma resta ferma. Siviglia: Maestranza e Giralda. Piazze nuove (PLAZAS).
    Le impronte vanno in clear_other: il render toglie gli edifici del Catasto (e i predecessori) che ci cadono dentro."""
    path = f'{DATA}/landmarks.json'
    LM = json.load(open(path)) if os.path.exists(path) else {'parts': [], 'labels': [], 'clear': []}
    LM['parts'] = [p for p in LM['parts'] if not (p.get('plaza') or p.get('icon'))]
    LM['labels'] = [l for l in LM.get('labels', []) if not l.get('icon')]
    clear = []
    def part(**k):
        k.setdefault('a', 0.05); k['icon'] = 1
        if 'r' in k: k['cx'] = round(sum(q[0] for q in k['r']) / len(k['r']), 2); k['cy'] = round(sum(q[1] for q in k['r']) / len(k['r']), 2)
        LM['parts'].append(k)
    # piazze nuove (lastricato a strisce)
    for poly, y0, y1, n, col, name in PLAZAS:
        x0, ya, x1, yb = poly.bounds
        for i in range(n):
            r = [[x0 + (x1 - x0) * i / n, ya], [x0 + (x1 - x0) * (i + 1) / n, ya], [x0 + (x1 - x0) * (i + 1) / n, yb], [x0 + (x1 - x0) * i / n, yb]]
            part(name=name, t='prism', r=[[round(v, 2) for v in q] for q in r], z0=0.0, z1=0.3, c=col, y=round(y0 + (y1 - y0) * i / max(1, n - 1), 2))
    blds = json.load(open(f'{DATA}/buildings.json'))
    # --- Maestranza: 1761 anello basso in pietra; 1785 anello piu' alto (fasi 1761-66 e 1781-85); 1881 recinto completo
    #     e gradinate (fasi 1845-1881) [V realmaestranza.com, scheda]. Impronta = edificio del Catasto (anno 1900 = rilievo,
    #     non costruzione: non si usa). Arena: cerchio di 63 m al centro [L diametro].
    mx, my = L(37.38611, -5.99868)
    fp = max([b for b in blds if math.hypot(b['r'][0][0] - mx, b['r'][0][1] - my) < 70 and Polygon(b['r']).area > 5000],
             key=lambda b: Polygon(b['r']).area)
    outer = Polygon(fp['r']).buffer(0); arena = outer.centroid.buffer(31.5, quad_segs=12)
    for y0, d, inset, h in ((1761, 1785, 16.0, 6.0), (1785, 1881, 8.0, 9.5), (1881, None, 0.0, 13.4)):
        o_ = outer.buffer(-inset, join_style=2) if inset else outer
        for r in _ring_wedges(o_, arena):
            k = dict(name='Maestranza', t='prism', r=r, z0=0.0, z1=h, c='#f1ece0', top='#b4613f', y=y0)
            if d: k['d'] = d
            part(**k)
    clear.append([list(q) for q in list(outer.exterior.coords)[:-1]])
    LM['labels'].append({'name': 'Maestranza Bullring', 'x': round(outer.centroid.x, 1), 'y': round(outer.centroid.y, 1), 'z': 16, 'from': 1761, 'icon': 1})
    # --- Giralda (origine = Giralda): 1248 minareto almohade (fusto 13,6 m x 50,51 m + secondo corpo 6,83 m x 14,39 m +
    #     yamur con le sfere, completato 1198); 1356 il terremoto fa cadere le sfere; 1400 croce e campana; 1568 campanile di
    #     Hernan Ruiz (1558-68) fino a ~96 m + Giraldillo ~4 m [V Wikipedia en "Giralda"; altezze dei corpi del campanile L].
    # posizione: il Catasto della Cattedrale ha l'incavo quadrato di 13,6 m della torre, centrato 12 m a ovest
    # dell'origine (lat0/lon0 e' approssimata); lati ruotati di ~5,6 gradi.
    gx, gy = GIRALDA[0], GIRALDA[1]; ux, uy = GIRALDA[2]
    BR, WH = '#c98d63', '#ece2cc'
    part(name='Giralda', t='prism', r=_sq(gx, gy, 6.8, ux, uy), z0=0.0, z1=50.5, c=BR, y=1100)
    part(name='Giralda', t='prism', r=_sq(gx, gy, 3.42, ux, uy), z0=50.5, z1=64.9, c=BR, y=1100, d=1568)
    for i, (rad, z) in enumerate(((1.6, 66.5), (1.25, 69.2), (0.95, 71.4), (0.7, 73.0))):   # yamur: 4 sfere dorate
        part(name='Giralda', t='cyl', cx=gx, cy=gy, rad=rad, z0=z - rad, z1=z + rad, seg=10, c='#d9a93a', y=1100, d=1356)
    part(name='Giralda', t='cyl', cx=gx, cy=gy, rad=0.25, z0=64.9, z1=73.5, seg=6, c='#5a5048', y=1100, d=1356)
    part(name='Giralda', t='cyl', cx=gx, cy=gy, rad=0.9, z0=64.9, z1=67.5, seg=8, c='#6d5a3a', y=1400, d=1568)   # campana
    part(name='Giralda', t='cyl', cx=gx, cy=gy, rad=0.2, z0=67.5, z1=71.0, seg=6, c='#5a5048', y=1400, d=1568)   # croce
    for z0, z1, half, col in ((50.5, 68.0, 6.6, WH), (68.0, 76.0, 4.8, WH), (76.0, 83.0, 3.9, WH)):
        part(name='Giralda', t='prism', r=_sq(gx, gy, half, ux, uy), z0=z0, z1=z1, c=col, y=1568)
    part(name='Giralda', t='cyl', cx=gx, cy=gy, rad=3.0, z0=83.0, z1=89.5, seg=16, c=WH, y=1568)
    part(name='Giralda', t='cyl', cx=gx, cy=gy, rad=2.0, z0=89.5, z1=94.0, seg=16, c=WH, y=1568)
    part(name='Giralda', t='cone', cx=gx, cy=gy, r0=1.4, r1=0.3, z0=94.0, z1=96.0, seg=12, c='#b9a36a', y=1568)
    part(name='Giralda', t='prism', r=_sq(gx, gy, 0.9, ux, uy), z0=96.0, z1=100.0, c='#4e4a45', y=1568)   # Giraldillo
    clear.append(_sq(gx, gy, 7.5, ux, uy))
    LM['labels'].append({'name': 'Giralda', 'x': gx, 'y': gy, 'z': 102, 'from': 1248, 'icon': 1})
    LM['clear_other'] = clear
    LM.setdefault('clear', [])
    LM['clear'] = [c for c in LM['clear'] if c not in LM.get('clear_other_prev', [])] + clear
    LM['clear_other_prev'] = clear
    json.dump(LM, open(path, 'w'))
    print(f'[hist_sevilla] icone: Maestranza 3 stadi (1761, 1785, 1881), Giralda 4 stadi (1248, 1356, 1400, 1568); piazze {len(PLAZAS)}', flush=True)

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
# REGOLA (Fabio, 22 ott, vale per tutte le citta'): un landmark con data documentata nella scheda sovrascrive l'anno del
# Catasto (che e' l'ultimo rilievo/riforma, non la costruzione). Cantieri lunghi (>~20 anni) = comparsa unica all'inizio.
# Stadi solo per Maestranza e Giralda (icons()); tutti gli altri: comparsa unica nell'anno di inizio costruzione.
ICON_YEARS = [(37.39176, -5.97535, 200, 20000, 1991, None, 'Santa Justa'),
              (37.37722, -5.98694, 250, 10000, 1914, None, 'Plaza de Espana (cantiere 1914-1929)'),
              (37.39318, -5.99178, 80, 3000, 2005, None, 'Metropol Parasol, base (cantiere 2005-2011)')]
# Cattedrale: comparsa unica 1434 (scheda). Il Catasto la da' come un blocco unico alto 63 m (rilievo 1940) che inglobava
# la Giralda: altezza riportata alla navata [L ~40 m] e impronta della Giralda tolta.
CATHEDRAL = (1434, 40.0)
def fix_icons(DATA):
    blds = json.load(open(f'{DATA}/buildings.json'))
    for la, lo, rad, amin, yr, y1, name in ICON_YEARS:
        x, y = L(la, lo)
        for b in blds:
            if math.hypot(b['r'][0][0] - x, b['r'][0][1] - y) < rad and Polygon(b['r']).area > amin:
                print(f'[hist_sevilla] {name}: {b["y"]} -> {yr}' + (f'-{y1}' if y1 else ''), flush=True); b['y'] = yr
                if y1: b['y1'] = y1
    cat = max([b for b in blds if math.hypot(b['r'][0][0], b['r'][0][1]) < 150 and Polygon(b['r']).area > 10000],
              key=lambda b: Polygon(b['r']).area)
    g = Polygon(cat["r"]).buffer(0).difference(Polygon(_sq(GIRALDA[0], GIRALDA[1], 7.3, *GIRALDA[2])))
    g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    print(f'[hist_sevilla] Cattedrale: {cat["y"]} -> {CATHEDRAL[0]}, {cat["h"]} m -> {CATHEDRAL[1]} m', flush=True)
    cat['r'] = [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]; cat['y'], cat['h'] = CATHEDRAL
    cat['lm'] = True; cat['wall'] = '#d9cba9'; cat['roof'] = '#bfb293'   # pietra, non la tavolozza casuale delle case
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
    icons(DATA)
