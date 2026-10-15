# Strato storico di Rotterdam: edifici "predecessori" demoliti e sostituiti da quelli di oggi, piu' il bombardamento
# del 14 maggio 1940, che rase al suolo il centro (circa 2,6 km2). Il BAG contiene solo gli edifici esistenti oggi:
# il centro distrutto non c'e' nei dati, va ricostruito. Tutto approssimato e illustrativo.
# Fronte di urbanizzazione: piu' nuclei (citta' sulla Rotte 1270-1340; Schiedam; Delfshaven 1389; villaggi di Overschie
# e Charlois). La riva sud (Feijenoord, Kop van Zuid) si urbanizza solo dal 1870 (porti di Pincoffs, ponti 1878).
# Calibrato sui dati: 10o percentile degli anni del BAG per cella di 1 km.
# Uso: python hist_rotterdam.py DATA_DIR  -> DATA/hist.json [{"r", "h", "y", "d"}]
import json, math, random, sys
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
from hist_nyc import split

LAT0, LON0 = 51.9221, 4.4795   # Laurenskerk = (0, 0), metri: x verso est, y verso nord
BOMB_D = 1940.37               # 14 maggio 1940

def interp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a)
    return pts[-1][1]

# (centro x, y in metri; curva distanza km -> anno; vale anche a sud del fiume?)
TOWNS = [
    ((0, 0),        [(0, 1290), (1.0, 1855), (1.7, 1868), (2.4, 1885), (3.3, 1905),
                     (4.3, 1925), (5.5, 1950), (7.5, 1968), (10, 1990)], False),
    ((-5600, -650), [(0, 1300), (0.35, 1450), (0.6, 1650), (0.9, 1860), (2.2, 1915), (3.5, 1950)], False),   # Schiedam
    ((-3350, -1650), [(0, 1400), (0.3, 1620), (0.8, 1875), (1.5, 1900)], False),                # Delfshaven
    ((-4000, 2200), [(0, 1500), (0.35, 1720), (1.0, 1930), (2.0, 1960)], False),                # Overschie
    ((-1000, -4000), [(0, 1500), (0.35, 1720), (1.0, 1905), (2.0, 1930)], True),                # Charlois
    ((1500, -1900), [(0, 1872), (1.0, 1893), (2.0, 1908), (3.5, 1925), (5.0, 1950), (7, 1970)], True),  # Feijenoord / Kop van Zuid
]
# Linea mediana della Nieuwe Maas (dalla mappa OSM): a sud di questa linea niente citta' prima del 1870
RIVER = [(-12000, -2950), (-7500, -2700), (-5000, -2600), (-3000, -2300), (-1500, -1800), (0, -1300), (1000, -1400),
         (2500, -1100), (3500, -1550), (5000, -1500), (6500, -1300), (7500, -1100), (9000, -700), (12000, 0)]
def south(x, y): return y < interp(x, RIVER)

# Il "triangolo" storico di Rotterdam (Coolsingel a ovest, Goudsesingel a nord-est, Maas a sud): la citta' ne resta
# dentro fino al Waterproject (1854). A nord della Hoogstraat la citta' medievale; a sud la Waterstad (1590-1640).
TRI = prep(Polygon([(-760, -980), (-720, 620), (-480, 700), (880, -40), (1000, -460), (300, -1020)]))
def tri_year(x, y):
    if y > -160 + 0.12 * x:   # a nord della Hoogstraat
        return interp(math.hypot(x - 100, y + 50) / 1000.0, [(0, 1290), (0.35, 1350), (0.6, 1420), (0.9, 1480)])
    return interp(math.hypot(x + 150, y + 450) / 1000.0, [(0, 1595), (0.5, 1625), (0.9, 1650)])

def urban_year(x, y):
    s = south(x, y); best = 9999
    if not s and TRI.contains(Point(x, y)): best = tri_year(x, y)
    for (cx, cy), curve, ok_south in TOWNS:
        if s and not ok_south: continue
        v = interp(math.hypot(x - cx, y - cy) / 1000.0, curve)
        if (cx, cy) == (0, 0): v = max(v, 1855)   # fuori dal triangolo: campagna fino al 1855
        best = min(best, v)
    wob = 8 * math.sin(x / 170.0) + 6 * math.sin(y / 230.0 + x / 410.0)
    return best + wob

# Zona distrutta il 14 maggio 1940 (centro storico: dalla Coolsingel all'Oostplein, dall'Hofplein e dalla stazione
# Delftse Poort fino ai Boompjes e alla Waterstad). Contorno approssimato dalle mappe dei danni.
BOMB = prep(Polygon([(-1050, -800), (-1150, 250), (-1100, 1050), (-550, 1100), (0, 800), (600, 600), (1250, 350),
                     (1350, -250), (900, -700), (200, -950), (-550, -1000)]))
def bombed(x, y): return BOMB.contains(Point(x, y))

def era_height(u, rnd):
    if u < 1700: return rnd.uniform(7, 11)      # case a capanna, 2-3 piani
    if u < 1850: return rnd.uniform(9, 13)      # case di mercanti, magazzini bassi
    if u < 1900: return rnd.uniform(11, 16)     # case a schiera dell'800, 3-4 piani
    return rnd.uniform(12, 18)                  # isolati 1900-1939, 4 piani

def build(DATA, seed=11):
    blds = json.load(open(f'{DATA}/buildings.json')); rnd = random.Random(seed); out = []; nb = 0
    for b in blds:
        try: p = Polygon(b['r'])
        except Exception: continue
        if not p.is_valid or p.area < 15: continue
        c = p.centroid; u = urban_year(c.x, c.y) + rnd.uniform(-6, 10)
        bz = bombed(c.x, c.y) and b['y'] > 1940 and u < 1935
        if not bz and b['y'] < u + 25: continue   # l'edificio di oggi e' tra i primi del lotto: nessun predecessore
        for q in split(p):
            born = u + rnd.uniform(0, 12)
            died = (BOMB_D + rnd.uniform(0, 0.01)) if bz else b['y'] - rnd.uniform(0.3, 2.0)
            if died - born < 8: continue
            ring = [[round(x, 2), round(yv, 2)] for x, yv in list(q.exterior.coords)[:-1]]
            if born < 1800 and died > 1870:   # seconda generazione: case antiche rifatte nell'800
                swap = rnd.uniform(max(born + 30, 1820), 1880)
                out.append({'r': ring, 'h': round(era_height(born, rnd), 1), 'y': int(born), 'd': round(swap - 0.5, 1)})
                out.append({'r': ring, 'h': round(era_height(swap, rnd), 1), 'y': int(swap), 'd': round(died, 2)})
            else:
                out.append({'r': ring, 'h': round(era_height(born, rnd), 1), 'y': int(born), 'd': round(died, 2)})
            if bz: nb += 1
    json.dump(out, open(f'{DATA}/hist.json', 'w'))
    print(f'[hist] {len(out)} predecessori da {len(blds)} edifici attuali; {nb} distrutti nel 1940', flush=True)

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'data')
