# Roma: zone storiche (contorni approssimati, stile Latos: leggibilita' prima dell'esattezza) e citta' antica/medievale
# come predecessori sulle impronte di oggi (hist.json, chiavi r, h, y, d come gli altri hist_*.py).
# Anni negativi = a.C.
import json, math, os, sys, random
from shapely.geometry import Polygon, Point
from shapely.prepared import prep

LAT0, LON0 = 41.8960, 12.4823
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def P(pts): return Polygon([L(a, b) for a, b in pts]).buffer(0)

PALATINE = L(41.8892, 12.4875); CAPITOL = L(41.8933, 12.4828)
# mura Aureliane (271-275 d.C.), porte principali, chiuse attraverso il Tevere e il Gianicolo
AURELIAN = [(41.9105, 12.4733), (41.9115, 12.4764), (41.9110, 12.4815), (41.9093, 12.4882), (41.9093, 12.5016), (41.9068, 12.5070),
            (41.9040, 12.5098), (41.8985, 12.5128), (41.8915, 12.5156), (41.8875, 12.5130), (41.8846, 12.5098), (41.8790, 12.5010),
            (41.8735, 12.5016), (41.8720, 12.4935), (41.8763, 12.4813), (41.8790, 12.4740), (41.8815, 12.4730), (41.8840, 12.4600),
            (41.8925, 12.4655), (41.8975, 12.4690), (41.9040, 12.4700)]
AUR_P = P(AURELIAN); AUR = prep(AUR_P)
# mura Serviane (IV sec. a.C.): Quirinale, Viminale, Esquilino, Celio (in parte), Aventino, Campidoglio
SERVIAN = [(41.8985, 12.4810), (41.9030, 12.4900), (41.9040, 12.4975), (41.9005, 12.5030), (41.8955, 12.5020), (41.8905, 12.4985),
           (41.8850, 12.4945), (41.8800, 12.4870), (41.8815, 12.4790), (41.8875, 12.4775), (41.8930, 12.4800)]
SER_P = P(SERVIAN); SER = prep(SER_P)
# abitato medievale: ansa del Tevere (Campo Marzio), Trastevere, Borgo; piu' Trevi/Monti fino a S. Maria Maggiore
ABITATO = [P([(41.9105, 12.4745), (41.9050, 12.4800), (41.9010, 12.4850), (41.8990, 12.4930), (41.8975, 12.4985), (41.8945, 12.4950),
              (41.8930, 12.4860), (41.8905, 12.4815), (41.8880, 12.4785), (41.8905, 12.4755), (41.8965, 12.4705), (41.9015, 12.4695),
              (41.9070, 12.4715)]),
           P([(41.8935, 12.4665), (41.8935, 12.4720), (41.8870, 12.4770), (41.8835, 12.4735), (41.8860, 12.4665)]),
           P([(41.9045, 12.4570), (41.9030, 12.4665), (41.9000, 12.4665), (41.9005, 12.4570)])]
ABI = [prep(a) for a in ABITATO]
def in_abitato(x, y): return any(a.contains(Point(x, y)) for a in ABI)
# zone senza edifici di oggi da usare come citta' antica (Circo Massimo, Fori, Palatino: li fanno i monumenti)
OPEN = [P([(41.8875, 12.4815), (41.8870, 12.4875), (41.8850, 12.4880), (41.8853, 12.4818)])]   # Circo Massimo
def in_water_or_ancient_park(x, y): return any(o.contains(Point(x, y)) for o in OPEN)

CONSOLARI = {'Via Appia Antica': -312, 'Via Appia Pignatelli': -312, 'Via Flaminia': -220, 'Via Salaria': -500, 'Via Aurelia Antica': -241,
             'Via Latina': -350, 'Via Prenestina': -400, 'Via Tiburtina': -286, 'Via Ostiense': -400, 'Via Nomentana': -400,
             'Via Cassia': -154, 'Via Casilina': -350, 'Via Labicana': -350, 'Via Portuense': -300, 'Via Ardeatina': -300}

def d_from(pt, x, y): return math.hypot(x - pt[0], y - pt[1])

def ancient_year(x, y, rnd):
    # prima urbanizzazione antica (None = mai citta' antica)
    p = Point(x, y)
    dp = min(d_from(PALATINE, x, y), d_from(CAPITOL, x, y))
    if dp < 450: return -753 + dp / 450 * 70 + rnd.uniform(0, 12)
    if SER.contains(p): return -620 + min(dp, 1500) / 1500 * 300 + rnd.uniform(-30, 60)
    if AUR.contains(p):
        # Campo Marzio e Trastevere dalla tarda repubblica, il resto entro le mura Aureliane nel primo impero
        return -200 + min(dp, 3000) / 3000 * 260 + rnd.uniform(-40, 60)
    dw = AUR_P.exterior.distance(p)
    if dw < 700 and rnd.random() < 0.55 * (1 - dw / 700): return 60 + dw / 700 * 120 + rnd.uniform(0, 60)   # sobborghi lungo le vie
    return None

def ancient_death(x, y, a, rnd):
    p = Point(x, y)
    if in_abitato(x, y): return rnd.uniform(650, 1000)            # rinnovato in medievale sullo stesso lotto
    if not AUR.contains(p): return rnd.uniform(270, 460)           # sobborghi fuori le mura: abbandonati per primi
    dp = min(d_from(PALATINE, x, y), d_from(CAPITOL, x, y))
    # la citta' si svuota: sacco 410, guerra gotica 537-552, poi rovine e vigne (abitato disabitato)
    return rnd.uniform(415, 545) + (1 - min(dp, 3000) / 3000) * rnd.uniform(0, 70)

def pre1919_year(x, y, rnd):
    p = Point(x, y)
    if in_abitato(x, y): return rnd.choice([rnd.uniform(1100, 1500), rnd.uniform(1450, 1700), rnd.uniform(1550, 1860)])
    if AUR.contains(p): return rnd.uniform(1871, 1915)              # Roma capitale: Esquilino, Monti, Ludovisi, Celio
    return rnd.uniform(1885, 1918)                                   # Prati, Flaminio, San Lorenzo, Testaccio, Nomentano

def outside_year(x, y, rnd): return rnd.uniform(1950, 2005)

def urban_year(x, y):
    # suolo urbano (non usato nello stile Latos: suolo sempre verde)
    return 9999

def era_height(y, rnd, x=0, yy=0):
    if y < -300: return rnd.uniform(4, 7)
    if y < 450:
        dp = min(d_from(PALATINE, x, yy), d_from(CAPITOL, x, yy))
        return rnd.uniform(9, 16) if dp < 2200 else rnd.uniform(5, 9)   # insulae al centro, domus fuori
    if y < 1300: return rnd.uniform(7, 12)
    return rnd.uniform(10, 16)

def build(DATA, seed=21):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hist_nyc import split
    blds = json.load(open(f'{DATA}/buildings.json')); rnd = random.Random(seed); out = []
    for b in blds:
        try: poly = Polygon(b['r'])
        except Exception: continue
        if not poly.is_valid or poly.area < 15: continue
        c = poly.centroid
        a = ancient_year(c.x, c.y, rnd)
        pieces = split(poly) if poly.area > 450 else [poly]
        for q in pieces:
            ring = [[round(x, 2), round(yv, 2)] for x, yv in list(q.exterior.coords)[:-1]]
            if a is not None:
                d = min(ancient_death(c.x, c.y, a, rnd), b['y'] - 0.5)
                if d - a > 20:
                    out.append({'r': ring, 'h': round(era_height(a, rnd, c.x, c.y), 1), 'y': round(a, 1), 'd': round(d, 1), 'k': 'anc'})
                if in_abitato(c.x, c.y) and b['y'] > d + 60:   # medievale/rinascimentale sullo stesso lotto fino all'edificio di oggi
                    m0 = d + rnd.uniform(0, 30)
                    out.append({'r': ring, 'h': round(era_height(m0, rnd), 1), 'y': round(m0, 1), 'd': round(b['y'] - 0.3, 1)})
    # capanne di Romolo: Palatino, Campidoglio e valle del Foro non hanno edifici di oggi (area archeologica)
    import math as _m
    for cen, n, rad in ((PALATINE, 160, 260), (CAPITOL, 70, 160), (L(41.8960, 12.4895), 90, 300)):
        for i in range(n):
            a_ = rnd.uniform(0, 2 * _m.pi); r_ = rad * _m.sqrt(rnd.random()); x0 = cen[0] + r_ * _m.cos(a_); y0 = cen[1] + r_ * _m.sin(a_)
            w, h_, an = rnd.uniform(7, 10), rnd.uniform(5, 7), rnd.uniform(0, _m.pi)
            pts = [(-w / 2, -h_ / 2), (w / 2, -h_ / 2), (w / 2, h_ / 2), (-w / 2, h_ / 2)]
            ring = [[round(x0 + px * _m.cos(an) - py * _m.sin(an), 2), round(y0 + px * _m.sin(an) + py * _m.cos(an), 2)] for px, py in pts]
            y_ = -753 + (r_ / rad) * 28 + rnd.uniform(0, 8) + (40 if cen is not PALATINE else 0)
            out.append({'r': ring, 'h': round(rnd.uniform(3.5, 5), 1), 'y': round(y_, 1), 'd': round(rnd.uniform(-480, -300), 1), 'k': 'anc'})
    json.dump(out, open(f'{DATA}/hist.json', 'w'))
    import collections
    cc = collections.Counter(int(h['y'] // 100 * 100) for h in out)
    print(f'[hist] {len(out)} predecessori da {len(blds)} edifici; per secolo di nascita:', dict(sorted(cc.items())), flush=True)

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'data_roma')
