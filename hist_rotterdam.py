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

LAT0, LON0 = 51.9221, 4.4795   # origine (0, 0) = Stadhuis sulla Coolsingel; Laurenskerk ~(536, 22). Metri: x est, y nord.
# Punti storici convertiti da latitudine/longitudine (15 ott 2026), non stimati a occhio.
BOMB_D = 1940.37               # 14 maggio 1940

def interp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a)
    return pts[-1][1]

# (centro x, y in metri; curva distanza km -> anno; vale anche a sud del fiume?)
TOWNS = [
    ((500, -100),   [(0, 1290), (1.0, 1855), (1.7, 1868), (2.4, 1885), (3.3, 1905),
                     (4.3, 1925), (5.5, 1950), (7.5, 1968), (10, 1990)], False),
    ((-5530, -560), [(0, 1300), (0.35, 1450), (0.6, 1650), (0.9, 1860), (2.2, 1915), (3.5, 1950)], False),   # Schiedam
    ((-2260, -1720), [(0, 1400), (0.3, 1620), (0.8, 1875), (1.5, 1900)], False),                # Delfshaven
    ((-3710, 2370), [(0, 1500), (0.35, 1720), (1.0, 1930), (2.0, 1960)], False),                # Overschie
    ((-310, -3880), [(0, 1500), (0.35, 1720), (1.0, 1905), (2.0, 1930)], True),                # Charlois
    ((1300, -2200), [(0, 1872), (1.0, 1893), (2.0, 1908), (3.5, 1925), (5.0, 1950), (7, 1970)], True),  # Feijenoord / Kop van Zuid
]
# Riva sud: la Maas divide la terra (land.json da OSM) in masse separate; "sud" = la massa che contiene Charlois.
# Niente citta' a sud prima del 1870 (salvo il villaggio di Charlois).
import os
_SOUTH = None
def _south_poly():
    global _SOUTH
    if _SOUTH is None:
        _SOUTH = False; cand = []
        if '--' in sys.argv: cand.append(sys.argv[sys.argv.index('--') + 1])
        cand += [a_ for a_ in sys.argv[1:2] if not a_.startswith('-')] + [os.environ.get('CITY_DATA', ''), 'data_rotterdam']
        for d in cand:
            f = os.path.join(d, 'land.json') if d else ''
            if f and os.path.exists(f):
                ref = Point(-310, -3880)
                for r in json.load(open(f)):
                    q = Polygon(r['ext'], r.get('holes', [])).buffer(0)
                    if q.contains(ref): _SOUTH = prep(q); break
                break
        if not _SOUTH: print('[hist_rotterdam] land.json non trovato: riva sud approssimata', flush=True)
    return _SOUTH
def south(x, y):
    sp = _south_poly()
    return sp.contains(Point(x, y)) if sp else y < -2000

# Il "triangolo" storico di Rotterdam (Coolsingel a ovest, Goudsesingel a nord-est, Maas a sud): la citta' ne resta
# dentro fino al Waterproject (1854). A nord della Hoogstraat la citta' medievale; a sud la Waterstad (1590-1640).
TRI = prep(Polygon([(80, -1000), (-50, -300), (-290, 300), (1240, -290), (1300, -720), (700, -1050)]))   # Leuvehaven, Coolsingel, Hofplein, Oostpoort, Oude Haven, Boompjes
def tri_year(x, y):
    if y > -120 - 0.08 * (x - 500):   # a nord della Hoogstraat (passa davanti alla Laurenskerk)
        return interp(math.hypot(x - 560, y + 60) / 1000.0, [(0, 1290), (0.35, 1350), (0.6, 1420), (0.9, 1480)])
    return interp(math.hypot(x - 450, y + 600) / 1000.0, [(0, 1595), (0.4, 1625), (0.8, 1650)])

def urban_year(x, y):
    s = south(x, y); best = 9999
    if not s and TRI.contains(Point(x, y)): best = tri_year(x, y)
    for i, ((cx, cy), curve, ok_south) in enumerate(TOWNS):
        if s and not ok_south: continue
        d = math.hypot(x - cx, y - cy) / 1000.0
        if d > curve[-1][0] + 0.5: continue        # oltre la curva: questo nucleo non arriva (prima tutto il mondo diventava citta')
        v = interp(d, curve)
        if i == 0: v = max(v, 1855)                # Rotterdam fuori dal triangolo: campagna fino al Waterproject (1855)
        best = min(best, v)
    wob = 8 * math.sin(x / 170.0) + 6 * math.sin(y / 230.0 + x / 410.0)
    return best + wob

# Zona distrutta il 14 maggio 1940 (centro storico: dalla Coolsingel all'Oostplein, dall'Hofplein e dalla stazione
# Delftse Poort fino ai Boompjes e alla Waterstad). Contorno approssimato dalle mappe dei danni.
BOMB = prep(Polygon([(-620, 710), (35, 820), (1065, 490), (1440, -120), (1130, -785), (380, -950), (-380, -895), (-650, -230)]))   # ~3 km2
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
