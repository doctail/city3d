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
        if 'p0' in k: k['cx'] = round((k['p0'][0] + k['p1'][0]) / 2, 2); k['cy'] = round((k['p0'][1] + k['p1'][1]) / 2, 2)
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
    # --- Moschea almohade (aljama, 1172-1182) fino al 1434: sala di preghiera bassa (~11 m) sull'impronta della Cattedrale e
    #     cortile aperto (sahn = attuale Patio de los Naranjos, parte nord dell'impronta) con portici bassi; la Giralda
    #     resta attaccata all'angolo. Nel 1434 lascia il posto alla Cattedrale (comparsa unica, Catasto). Prima del 1434 sul
    #     sito non ci sono case: i predecessori generati dentro l'impronta vengono tolti (decisione di Fabio, 23 ott).
    cat = max([b for b in blds if math.hypot(b['r'][0][0], b['r'][0][1]) < 150 and Polygon(b['r']).area > 10000], key=lambda b: Polygon(b['r']).area)
    cpoly = Polygon(cat['r']).buffer(0)
    hall = cpoly.intersection(box(-400, -400, 400, 5)); patio = cpoly.intersection(box(-400, 5, 400, 400))
    for g_ in getattr(hall, 'geoms', [hall]):
        if g_.geom_type == 'Polygon' and g_.area > 50:
            part(name='Mosque', t='prism', r=[[round(x, 2), round(y, 2)] for x, y in list(g_.exterior.coords)[:-1]], z0=0.0, z1=11.0, c='#d9c39b', top='#b5794f', y=1100, d=1434)
    court = patio.buffer(-8, join_style=2)
    for r_ in _ring_wedges(patio, court, n=20):
        part(name='Mosque', t='prism', r=r_, z0=0.0, z1=7.0, c='#d9c39b', top='#b5794f', y=1100, d=1434)
    # cortile (sahn, oggi Patio de los Naranjos): pavimento chiaro e file di aranci ogni ~7 m
    for g_ in getattr(court, 'geoms', [court]):
        if g_.geom_type != 'Polygon' or g_.area < 100: continue
        part(name='Mosque', t='prism', r=[[round(x, 2), round(y, 2)] for x, y in list(g_.exterior.coords)[:-1]], z0=0.0, z1=0.35, c='#ddd3bf', top='#ddd3bf', y=1100, d=1434)
        inner = g_.buffer(-3.5); x0_, y0_, x1_, y1_ = inner.bounds; nt_ = 0
        yy = y0_ + 3
        while yy < y1_:
            xx = x0_ + 3
            while xx < x1_:
                if inner.contains(Point(xx, yy)):
                    part(name='Mosque', t='cyl', cx=round(xx, 2), cy=round(yy, 2), rad=0.25, z0=0.35, z1=2.2, seg=5, c='#5a4632', y=1100, d=1434)
                    part(name='Mosque', t='dome', cx=round(xx, 2), cy=round(yy, 2), rad=2.3, z0=1.8, hz=3.0, c='#4d6a30', y=1100, d=1434); nt_ += 1
                xx += 7.0
            yy += 7.0
        print(f'[hist_sevilla] cortile della moschea: {nt_} aranci', flush=True)
    hist = json.load(open(f'{DATA}/hist.json')); n0 = len(hist)
    hist = [h for h in hist if not cpoly.contains(Polygon(h['r']).centroid)]
    json.dump(hist, open(f'{DATA}/hist.json', 'w'))
    LM['labels'].append({'name': 'Great Mosque', 'x': round(cpoly.centroid.x, 1), 'y': round(cpoly.centroid.y, 1), 'z': 14, 'from': 1248, 'to': 1434, 'icon': 1})
    print(f'[hist_sevilla] moschea 1100-1434; tolti {n0 - len(hist)} predecessori dal sito della Cattedrale', flush=True)
    # --- Torre del Oro (37.38242, -5.99623): dodecagono; primo corpo 1220-21 e secondo corpo (XIV sec.) in una comparsa unica;
    #     il cilindro superiore del 1760 compare nel 1760 (eccezione alla regola: con la comparsa unica la lanterna del 1760
    #     sarebbe nell'apertura del 1248). Misure [L]: diametro ~15 m, altezza totale ~36 m.
    tx_, ty_ = L(37.38242, -5.99623)
    def dodec(r, rot=0.0): return [[round(tx_ + r * math.cos(rot + 2 * math.pi * k / 12), 2), round(ty_ + r * math.sin(rot + 2 * math.pi * k / 12), 2)] for k in range(12)]
    GOLD = '#d8b77a'
    part(name='Torre del Oro', t='prism', r=dodec(7.4), z0=0.0, z1=16.5, c=GOLD, y=1220)
    part(name='Torre del Oro', t='prism', r=dodec(4.5), z0=16.5, z1=25.0, c=GOLD, y=1220)
    part(name='Torre del Oro', t='cyl', cx=tx_, cy=ty_, rad=2.6, z0=25.0, z1=33.0, seg=16, c='#e3c98f', y=1760)
    part(name='Torre del Oro', t='dome', cx=tx_, cy=ty_, rad=2.6, z0=33.0, hz=3.4, c='#c9a24a', y=1760)
    clear.append(dodec(8.5))
    LM['labels'].append({'name': 'Torre del Oro', 'x': round(tx_, 1), 'y': round(ty_, 1), 'z': 38, 'from': 1248, 'icon': 1})
    # --- mura almohadi (anello del 1248, walls_1248.json): cortina in tapial ~9 m e torri quadrate ~13 m ogni ~60 m [L];
    #     demolizione 1858-1873 (keyframe della scheda) a tratti sparsi: tratti di 2-4 segmenti (~120-240 m), ognuno con un
    #     anno a caso nell'intervallo, non in ordine lungo l'anello (decisione di Fabio, 23 ott 12:27). Restano: tratto della
    #     Macarena (al posto dell'edificio del Catasto "1023", bianco e alto 16,5 m) e mura dell'Alcazar [V].
    from shapely.geometry import LineString as _WL
    ring_ = list(WALL_P.exterior.coords); _wr = random.Random(1858); _left = 0; _yd = 1858.0
    ax_, ay_ = L(37.38310, -5.99030)
    def _keep(x, y): return (270 < x < 640 and y > 1530) or math.hypot(x - ax_, y - ay_) < 260
    TAP, TOW = '#c3a77c', '#b99d72'
    for (x0, y0), (x1, y1) in zip(ring_, ring_[1:]):
        sl_ = math.hypot(x1 - x0, y1 - y0); n_ = max(1, round(sl_ / 60)); ux, uy = (x1 - x0) / sl_, (y1 - y0) / sl_
        for k in range(n_):
            ta, tb = k / n_, (k + 1) / n_
            pa = (x0 + (x1 - x0) * ta, y0 + (y1 - y0) * ta); pb = (x0 + (x1 - x0) * tb, y0 + (y1 - y0) * tb)
            mxp, myp = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
            if _left <= 0: _left = _wr.randint(2, 4); _yd = round(_wr.uniform(1858, 1873), 2)
            _left -= 1
            dw = {} if _keep(mxp, myp) else {'d': _yd}
            seg_ = _WL([pa, pb]).buffer(1.6, cap_style=2)
            part(name='City walls', t='prism', r=[[round(x, 2), round(y, 2)] for x, y in list(seg_.exterior.coords)[:-1]], z0=0.0, z1=9.0, c=TAP, top=TAP, y=1100, **dw)
            part(name='City walls', t='prism', r=_sq(pa[0], pa[1], 4.0, ux, uy), z0=0.0, z1=13.0, c=TOW, top=TOW, y=1100, **dw)
            if dw:   # al posto del muro demolito la ronda: nastro di strada chiara largo 18 m (Fabio, 23 ott), quota 0,11 (libera)
                rd_ = _WL([pa, pb]).buffer(9.0, cap_style=2)
                part(name='Ronda', t='prism', r=[[round(x, 2), round(y, 2)] for x, y in list(rd_.exterior.coords)[:-1]], z0=0.0, z1=0.11, c='#d8d0bf', top='#d8d0bf', y=dw['d'])
    # --- Metropol Parasol (cantiere 2005-2011, keyframe della scheda): la base del Catasto compare nel 2005, il parasole nel
    #     2011. Misure [L]: ~150 x 70 m, alto ~26 m, sei "funghi". Posizione e orientamento [L]: il rettangolo 150 x 70 che
    #     non tocca edifici attorno alla base (asse nord-sud, centro 10-40 m a sud della base: 12 m2 di sovrapposizione).
    mpx, mpy = 56.0, 762.0; WOOD = '#e3cf9e'
    for k_, (s_, o_) in enumerate(((-55, 12), (-33, -12), (-11, 12), (11, -12), (33, 12), (55, -12))):
        cxm, cym = mpx + o_, mpy + s_
        part(name='Metropol Parasol', t='cyl', cx=cxm, cy=cym, rad=4.5, z0=0.0, z1=21.0, seg=10, c=WOOD, y=2010.5)
        cap_ = [[round(cxm + 17 * math.cos(2 * math.pi * j / 14), 2), round(cym + 14 * math.sin(2 * math.pi * j / 14), 2)] for j in range(14)]
        part(name='Metropol Parasol', t='prism', r=cap_, z0=21.0, z1=26.0, c=WOOD, top=WOOD, y=2010.5)
    LM['labels'].append({'name': 'Metropol Parasol', 'x': mpx, 'y': mpy, 'z': 32, 'from': 2011, 'icon': 1})
    for b_ in blds:   # il tratto della Macarena del Catasto (anno 1023, bianco, 16,5 m) lascia il posto alle mura modellate
        if b_.get('y') == 1023 and b_.get('h', 0) > 15:
            cx_, cy_ = sum(p_[0] for p_ in b_['r']) / len(b_['r']), sum(p_[1] for p_ in b_['r']) / len(b_['r'])
            clear.append(_sq(cx_, cy_, 3.0, 1.0, 0.0))
    LM['labels'].append({'name': 'City walls', 'x': 455.0, 'y': 1700.0, 'z': 16, 'from': 1248, 'to': 1873, 'icon': 1})
    # --- navi nel porto dell'Arenal (decisione di Fabio, 23 ott): poche (4) dal 1248, porto pieno (14) dal 1503 al 1717
    #     (Casa de Contratacion a Siviglia), poi di nuovo 4. Sagome leggibili: scafo scuro di legno ~29 m con prua a punta,
    #     castello di poppa e di prua, 3 alberi (trinchetto, maestro, mezzana) con vele chiare; parallele alla riva dell'Arenal,
    #     alcune ruotate. Posizioni sulla riva est del fiume tra la Torre del Oro e il ponte di barche [L].
    import gzip
    from shapely.geometry import shape as _shape, LineString as _LS
    from shapely.ops import unary_union as _uu
    F = json.load(gzip.open(os.path.join(HERE, 'data_sevilla_src', 'osm_export.geojson.gz')))['features']
    def _loc(g):
        from shapely.ops import transform as _tr
        return _tr(lambda x, y, z=None: ((x - LON0) * KX, (y - LAT0) * KY), g)
    W = _uu([_loc(_shape(f['geometry'])).buffer(0) for f in F if f['properties'].get('natural') == 'water' or f['properties'].get('waterway') == 'riverbank'])
    WZ = -1.5; bank = []
    for yy in range(-780, -20, 20):
        seg = _LS([(-1400, yy), (100, yy)]).intersection(W)
        segs = [q for q in getattr(seg, 'geoms', [seg]) if q.length > 60 and q.bounds[2] > -800]
        if segs: bank.append((max(segs, key=lambda g_: g_.bounds[2]).bounds[2], yy))
    def ship(cx, cy, ux, uy, y0, d0, s=1.0):
        vx, vy = -uy, ux
        def P(u, v): return [round(cx + (u * ux + v * vx) * s, 2), round(cy + (u * uy + v * vy) * s, 2)]
        def box_(u0, u1, v0, v1): return [P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)]
        kw = dict(y=y0) if d0 is None else dict(y=y0, d=d0)
        hull = [P(-13, -3.4), P(6, -4.0), P(11, -2.6), P(15, 0), P(11, 2.6), P(6, 4.0), P(-13, 3.4), P(-14.5, 0)]
        part(name='Ship', t='prism', r=hull, z0=WZ - 1.0, z1=WZ + 3.8 * s, c='#3e2a1b', top='#6e5236', **kw)
        part(name='Ship', t='prism', r=box_(-13.5, -6, -3.2, 3.2), z0=WZ + 3.8 * s, z1=WZ + 7.2 * s, c='#4a3322', top='#6e5236', **kw)
        part(name='Ship', t='prism', r=box_(7, 11, -2.6, 2.6), z0=WZ + 3.8 * s, z1=WZ + 6.0 * s, c='#4a3322', top='#6e5236', **kw)
        for mu, mh, sw, tw in ((6.0, 20, 10, 7), (-1.0, 25, 12, 8), (-8.5, 16, 6, 0)):
            mx_, my_ = P(mu, 0)
            part(name='Ship', t='cyl', cx=mx_, cy=my_, rad=0.35 * s, z0=WZ + 3.8 * s, z1=WZ + (3.8 + mh) * s, seg=6, c='#2f2116', **kw)
            # vele quadre con i pennoni bracciati di ~30 gradi: leggibili sia di fianco sia di prua
            def sail(w_):
                th = math.radians(30); out_ = []
                for du, dv in ((-0.2, -w_ / 2), (0.2, -w_ / 2), (0.2, w_ / 2), (-0.2, w_ / 2)):
                    out_.append(P(mu + 0.6 + du * math.cos(th) - dv * math.sin(th), du * math.sin(th) + dv * math.cos(th)))
                return out_
            part(name='Ship', t='prism', r=sail(sw), z0=WZ + 7.5 * s, z1=WZ + (7.5 + mh * 0.45) * s, c='#e9dfc6', top='#e9dfc6', **kw)
            if tw: part(name='Ship', t='prism', r=sail(tw), z0=WZ + (8.5 + mh * 0.45) * s, z1=WZ + (3.8 + mh - 1.2) * s, c='#e9dfc6', top='#e9dfc6', **kw)
    slots = []
    for i in range(1, len(bank) - 1, max(1, len(bank) // 15)):
        (xa, ya), (xb, yb) = bank[i - 1], bank[i + 1]; dx, dy = xb - xa, yb - ya; n_ = math.hypot(dx, dy); ux, uy = dx / n_, dy / n_
        slots.append((bank[i][0], bank[i][1], ux, uy))
    slots = slots[:14]; ships = 0
    for k, (bx, by, ux, uy) in enumerate(slots):
        lane = k % 2; vx, vy = uy, -ux                       # verso il centro del fiume (la riva est e' a destra della corrente)
        if vx > 0: vx, vy = -vx, -vy
        cx_, cy_ = bx + vx * (16 + 26 * lane), by + vy * (16 + 26 * lane)
        rot = math.radians((-18, 0, 12, 0, -8, 22, 0)[k % 7]); rx, ry = ux * math.cos(rot) - uy * math.sin(rot), ux * math.sin(rot) + uy * math.cos(rot)
        base = k in (1, 5, 9, 12)                             # 4 navi sempre; le altre 10 solo 1503-1717
        ship(cx_, cy_, rx, ry, 1240 if base else 1503, None if base else 1717, 1.0 - 0.12 * (k % 3 == 2))
        ships += 1
    print(f'[hist_sevilla] navi nel porto: {ships} (4 sempre, {ships - 4} dal 1503 al 1717)', flush=True)
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
# recinto dell'Expo 92 sulla Cartuja (rettangolo tra la darsena e la Corta, dal ponte del Cachorro al viadotto dell'Alamillo) [L]
EXPO_SITE = box(-1650, 1250, -350, 2950)
def fix_icons(DATA):
    blds = json.load(open(f'{DATA}/buildings.json'))
    for la, lo, rad, amin, yr, y1, name in ICON_YEARS:
        x, y = L(la, lo)
        for b in blds:
            if math.hypot(b['r'][0][0] - x, b['r'][0][1] - y) < rad and Polygon(b['r']).area > amin:
                print(f'[hist_sevilla] {name}: {b["y"]} -> {yr}' + (f'-{y1}' if y1 else ''), flush=True); b['y'] = yr
                if y1: b['y1'] = y1
    # Expo 92 (decisione di Fabio, 23 ott): gli edifici del recinto con anno del Catasto 1993-2000 sono padiglioni rimasti
    # (riconvertiti dopo l'Expo): tornano al cantiere. Costruiti 1989-92 e finiti per l'apertura (20 aprile 1992) [V]:
    # anno 1990, cosi' nel fotogramma 1992 sono gia' in piedi (con anno 1992 la crescita nel 1992 e' zero).
    nx_ = 0
    for b in blds:
        if 1992 <= b['y'] <= 2000 and EXPO_SITE.contains(Polygon(b['r']).centroid): b['y'] = 1990; nx_ += 1
    print(f'[hist_sevilla] Expo 92: {nx_} edifici del recinto riportati al 1990', flush=True)
    cat = max([b for b in blds if math.hypot(b['r'][0][0], b['r'][0][1]) < 150 and Polygon(b['r']).area > 10000],
              key=lambda b: Polygon(b['r']).area)
    g = Polygon(cat["r"]).buffer(0).difference(Polygon(_sq(GIRALDA[0], GIRALDA[1], 7.3, *GIRALDA[2])))
    g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    print(f'[hist_sevilla] Cattedrale: {cat["y"]} -> {CATHEDRAL[0]}, {cat["h"]} m -> {CATHEDRAL[1]} m', flush=True)
    cat['r'] = [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]; cat['y'], cat['h'] = CATHEDRAL
    cat['lm'] = True; cat['wall'] = '#d9cba9'; cat['roof'] = '#bfb293'   # pietra, non la tavolozza casuale delle case
    # Torre Sevilla: nel Catasto 121,9 m (piani x 3,1 m); altezza vera ~180 m [L, Wikipedia]; anno del repo 2015 (scheda: NON VERIFICATO)
    for b in blds:
        if b['y'] == 2015 and b['h'] > 100: print(f'[hist_sevilla] Torre Sevilla: {b["h"]} m -> 180 m', flush=True); b['h'] = 180.0
    json.dump(blds, open(f'{DATA}/buildings.json', 'w'))

def expo(DATA):
    """Expo 92 (decisione di Fabio, 23 ott 12:27): niente padiglioni inventati. Nessuna pianta del recinto scaricabile
    da qui (la sandbox non raggiunge Wikimedia/OSM): restano solo gli edifici sopravvissuti del Catasto (anno 1990),
    in colori neutri (bianco e grigio chiaro), e il Lago de Espana (contorno OSM, natural=water/lake). Toglie i
    padiglioni delle prove precedenti da hist.json."""
    hist = json.load(open(f'{DATA}/hist.json')); n0 = len(hist)
    hist = [h for h in hist if h.get('name') != 'pabellon Expo 92']
    json.dump(hist, open(f'{DATA}/hist.json', 'w'))
    blds = json.load(open(f'{DATA}/buildings.json')); rnd = random.Random(92); nx_ = 0
    for b in blds:
        if b['y'] == 1990 and EXPO_SITE.contains(Polygon(b['r']).centroid):
            b['lm'] = True; b['wall'], b['roof'] = rnd.choice([('#f2f0ea', '#dcdad5'), ('#e6e5e1', '#cfcdc8'), ('#ecebe6', '#d6d4cf')]); nx_ += 1
    json.dump(blds, open(f'{DATA}/buildings.json', 'w'))
    print(f'[hist_sevilla] Expo 92: {nx_} edifici sopravvissuti in colori neutri; tolti {n0 - len(hist)} padiglioni inventati', flush=True)

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
    expo(DATA)
    icons(DATA)
