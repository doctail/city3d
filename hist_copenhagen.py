# Strato storico di Copenaghen: edifici "predecessori" demoliti e sostituiti da quelli di oggi, piu' i tre grandi incendi
# (20-23 ott 1728, 5-7 giu 1795, bombardamento inglese 2-5 set 1807). Il BBR ha solo gli edifici di oggi: prima del 1728
# restano 167 edifici reali, quindi la citta' fino al 1850 e' quasi tutta ricostruita. Tutto approssimato e illustrativo.
# Origine (0, 0) = Raadhuspladsen. Metri: x est, y nord. Punti da lat/lon (KX = 62.720 m/grado, KY = 110.540 m/grado).
# Taratura (19 ott 2026): 10o percentile degli anni BBR per cella di 1 km: centro 1730-1767, anello 1-3 km 1865-1900,
# 3-6 km 1905-1940, periferia 1950-1980, Amager 1895-1940.
# Uso: python hist_copenhagen.py DATA_DIR  -> DATA/hist.json [{"r", "h", "y", "d"}], DATA/fires.json, DATA/reclaim.json
import json, math, random, sys, os
from shapely.geometry import Polygon, Point
from shapely.prepared import prep

def interp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a)
    return pts[-1][1]

# citta' dentro i bastioni (circa 1700-1852): mura medievali a ovest (Vester/Noerre Voldgade), bastioni di Christian IV
# a nord (Oersted Park, Botanisk Have, Oestre Anlaeg) fino al Kastellet; Christianshavn e Holmen oltre il porto.
WALL_P = Polygon([(60, -350), (30, 150), (150, 600), (250, 950), (350, 1250), (750, 1450), (1300, 1650), (1700, 1800),
                  (2000, 1500), (2700, 1200), (2800, 400), (2500, -150), (2300, -650), (1700, -1150), (1050, -800), (700, -450)])
WALL = prep(WALL_P)
CASTLE = (735, 0)            # castello di Absalon su Slotsholmen (1167), oggi Christiansborg
def zone_year(x, y):
    """Anno di urbanizzazione dentro le mura, per zona."""
    if math.hypot(x - CASTLE[0], y - CASTLE[1]) < 90: return 1167
    if y < -150 and x > 950:                                         # Christianshavn (dal 1618)
        return interp(math.hypot(x - 1550, y + 450) / 1000, [(0, 1620), (0.4, 1650), (0.8, 1690), (1.2, 1720)])
    if x > 2000 and y > -150:                                        # Holmen, base navale su terra di riporto (1690-1760)
        return interp(math.hypot(x - 2100, y - 700) / 1000, [(0, 1690), (0.5, 1730), (1.0, 1760)])
    above_gothersgade = (y - 850) > (x - 250) * (420 - 850) / (1110 - 250)   # linea Noerreport -> Kongens Nytorv
    if above_gothersgade:
        if x > 1100 and y > 550:                                     # Frederiksstaden (1749-1775)
            return interp(math.hypot(x - 1560, y - 870) / 1000, [(0, 1750), (0.3, 1760), (0.6, 1775)])
        if y < 560 and x > 1050: return interp((x - 1050) / 1000, [(0, 1670), (0.6, 1700)])   # Nyhavn (scavato 1671-73)
        return interp(math.hypot(x - 1236, y - 1315) / 1000 * 0.6 + math.hypot(x - 571, y - 1072) / 1000 * 0.4,
                      [(0, 1612), (0.3, 1640), (0.6, 1680), (0.9, 1720)])   # Ny-Koebenhavn: Rosenborg, Nyboder
    # citta' medievale attorno a Gammeltorv / Hoejbro
    return interp(math.hypot(x - 450, y - 200) / 1000, [(0, 1185), (0.25, 1250), (0.45, 1330), (0.65, 1450), (0.9, 1560), (1.2, 1620)])

# villaggi fuori dalle mura (centro, curva km -> anno)
VILLAGES = [((-2000, -200), [(0, 1660), (0.3, 1760), (0.6, 1850)]),    # Frederiksberg (Ny Amager 1651, castello 1703)
            ((-3280, -1558), [(0, 1250), (0.25, 1700), (0.5, 1890)]),  # Valby
            ((-4597, 3196), [(0, 1200), (0.25, 1700), (0.5, 1905)]),   # Broenshoej
            ((1990, -1448), [(0, 1620), (0.3, 1800), (0.5, 1875)]),    # Sundbyvester (Amager)
            ((4430, -4654), [(0, 1700), (0.3, 1850), (0.6, 1910)])]    # Kastrup
MAIN_FRONT = [(0, 1853), (0.5, 1864), (1.0, 1874), (1.5, 1885), (2.0, 1897), (3.0, 1911), (4.0, 1923), (5.0, 1931), (6.0, 1940), (7.0, 1950), (9.0, 1962), (12, 1975)]
AMAGER_FRONT = [(0, 1868), (1.0, 1893), (2.0, 1908), (3.0, 1922), (4.0, 1931), (6.0, 1945), (9.0, 1962)]

_AMAGER = None
def _amager():
    global _AMAGER
    if _AMAGER is None:
        _AMAGER = False
        cand = [os.environ.get('CITY_DATA', ''), 'data_copenhagen']
        if '--' in sys.argv: cand.insert(0, sys.argv[sys.argv.index('--') + 1])
        cand += [a_ for a_ in sys.argv[1:2] if not a_.startswith('-')]
        for d in cand:
            f = os.path.join(d, 'land.json') if d else ''
            if f and os.path.exists(f):
                ref = Point(3000, -3500)
                for r in json.load(open(f)):
                    q = Polygon(r['ext'], r.get('holes', [])).buffer(0)
                    if q.contains(ref): _AMAGER = prep(q); break
                break
    return _AMAGER
def amager(x, y):
    a_ = _amager()
    return a_.contains(Point(x, y)) if a_ else (x > 900 and y < -1100)

def urban_year(x, y):
    p = Point(x, y)
    if WALL.contains(p): best = zone_year(x, y)
    else:
        if amager(x, y): best = interp(math.hypot(x - 1500, y + 900) / 1000, AMAGER_FRONT)
        else: best = interp(WALL_P.exterior.distance(p) / 1000, MAIN_FRONT)   # fuori dalle mura: niente citta' prima del 1852
        for (cx, cy), cv in VILLAGES:
            d = math.hypot(x - cx, y - cy) / 1000
            if d <= cv[-1][0]: best = min(best, interp(d, cv))
    wob = 5 * math.sin(x / 170.0) + 4 * math.sin(y / 230.0 + x / 410.0)
    return best + wob

# ---------- incendi ----------
# anni frazionari = giorno dell'evento. Contorni approssimati dalle mappe storiche dei danni.
FIRES = [
    {'name': 'Great Fire of 1728', 'y': 1728.80, 'y1': 1728.81, 'houses': 1670,
     'poly': [(40, 0), (60, 350), (180, 800), (330, 780), (520, 620), (600, 420), (540, 230), (380, 100), (200, 30)]},
    {'name': 'Fire of 1795', 'y': 1795.43, 'y1': 1795.44, 'houses': 940,
     'poly': [(250, 80), (330, 330), (560, 420), (800, 360), (950, 250), (900, 80), (650, 40), (450, 40)]},
    {'name': 'Bombardment of 1807', 'y': 1807.67, 'y1': 1807.68, 'houses': 300,
     'poly': [(120, 300), (170, 800), (400, 900), (560, 700), (520, 450), (330, 300)]},
]
for f_ in FIRES: f_['_p'] = prep(Polygon(f_['poly']))

# terra di riporto: prima dell'anno e' mare (bacini e moli del porto moderno). Contorni approssimati.
RECLAIM = [
    {'name': 'Holmen', 'y': 1700, 'poly': [(2050, 300), (2900, 300), (2950, 1250), (2200, 1350)]},
    {'name': 'Refshaleoeen', 'y': 1872, 'poly': [(2950, 1000), (4200, 1500), (4200, 2400), (3000, 1900)]},
    {'name': 'Nordhavn', 'y': 1895, 'poly': [(2400, 2600), (4200, 2700), (4500, 4600), (2600, 4300)]},
    {'name': 'Sydhavn', 'y': 1905, 'poly': [(-600, -3600), (300, -2500), (600, -3200), (-200, -4300)]},
    {'name': 'Islands Brygge', 'y': 1905, 'poly': [(560, -1250), (780, -1150), (850, -2450), (640, -2550)]},
]

def era_height(u, rnd):
    if u < 1600: return rnd.uniform(7, 10)      # case a graticcio, 2 piani
    if u < 1730: return rnd.uniform(9, 12)      # case di mercanti, 3 piani
    if u < 1850: return rnd.uniform(11, 15)     # case del '700 ricostruite dopo gli incendi, 4 piani
    if u < 1900: return rnd.uniform(14, 18)     # quartieri dei ponti, 5 piani
    return rnd.uniform(14, 19)

def build(DATA, seed=11):
    from hist_nyc import split
    blds = json.load(open(f'{DATA}/buildings.json')); rnd = random.Random(seed); out = []
    burned = {f_['name']: 0 for f_ in FIRES}
    for b in blds:
        try: p = Polygon(b['r'])
        except Exception: continue
        if not p.is_valid or p.area < 15: continue
        c = p.centroid; u = urban_year(c.x, c.y) + rnd.uniform(-4, 10)
        fires = [f_ for f_ in FIRES if f_['_p'].contains(c) and u < f_['y'] - 3 and b['y'] > f_['y']]
        if not fires and b['y'] < u + 25: continue      # l'edificio di oggi e' tra i primi del lotto: nessun predecessore
        for q in split(p):
            ring = [[round(x, 2), round(yv, 2)] for x, yv in list(q.exterior.coords)[:-1]]
            start = u + rnd.uniform(0, 12)
            for f_ in fires:
                if f_['y'] - start > 2:
                    out.append({'r': ring, 'h': round(era_height(start, rnd), 1), 'y': round(start, 1), 'd': round(f_['y'] + rnd.uniform(0, 0.008), 3)})
                    burned[f_['name']] += 1
                start = f_['y'] + rnd.uniform(0.6, 9)    # ricostruzione accelerata dopo l'incendio
            died = b['y'] - rnd.uniform(0.3, 2.0)
            if died - start < 8: continue
            if start < 1800 and died > 1880:             # seconda generazione: case antiche rifatte nell'800
                swap = rnd.uniform(max(start + 30, 1820), 1880)
                out.append({'r': ring, 'h': round(era_height(start, rnd), 1), 'y': round(start, 1), 'd': round(swap - 0.5, 1)})
                out.append({'r': ring, 'h': round(era_height(swap, rnd), 1), 'y': round(swap, 1), 'd': round(died, 2)})
            else:
                out.append({'r': ring, 'h': round(era_height(start, rnd), 1), 'y': round(start, 1), 'd': round(died, 2)})
    json.dump(out, open(f'{DATA}/hist.json', 'w'))
    json.dump([{k: v for k, v in f_.items() if k != '_p'} for f_ in FIRES], open(f'{DATA}/fires.json', 'w'))
    json.dump([{'r': r['poly'], 'y': r['y'], 'name': r['name']} for r in RECLAIM], open(f'{DATA}/reclaim.json', 'w'))
    print(f'[hist] {len(out)} predecessori da {len(blds)} edifici attuali; bruciati: {burned}', flush=True)

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    build(sys.argv[1] if len(sys.argv) > 1 else 'data_copenhagen')
