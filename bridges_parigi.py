# Ponti di Parigi modellati uno a uno (metodo di Siviglia: contorno OSM man_made=bridge -> asse, impalcato a travi, pile, archi).
# Date: scheda G (parigi/validazione), ID nei commenti. Righe DA MEMORIA mai BRUSCO: comparsa graduale in 1-2 anni.
# Case sui ponti (Pont Notre-Dame, au Change, Saint-Michel, Marie): demolite tra 1786 e 1808 [Likely, non in scheda: graduale].
# Ponti fuori dalla scheda (comuni vicini): anno da Wikidata (costruzione/apertura con lo stesso nome), altrimenti
# urbanizzazione delle due sponde + 3 (come Copenaghen). Stile per tipo: 'stone' archi in pietra, 'iron' archi metallici sotto
# l'impalcato, 'beam' travata moderna, 'foot' passerella.
# Uscita: aggiunge le parti a DATA/landmarks.json (dopo landmarks_parigi.py). Uso: python bridges_parigi.py RAW_DIR DATA_DIR
import json, math, os, sys, gzip, re, random
import numpy as np, shapely
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
RAW, DATA = sys.argv[1], sys.argv[2]
os.environ['CITY_DATA'] = DATA
import hist_parigi as H
CFG = json.load(open(os.path.join(HERE, 'city_parigi.json')))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
WZ = CFG.get('water_z', -3.5)
def log(*a): print('[bridges_parigi]', *a, flush=True)
rnd = random.Random(9)

land = json.load(open(f'{DATA}/land.json'))
LG = unary_union([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in land])
WATER = shapely.box(-12000, -12000, 12000, 12000).difference(LG)
F = json.load(gzip.open(f'{RAW}/osm_roads.geojson.gz', 'rt'))['features']
OUTL = []
for f in F:
    p = f['properties']
    if p.get('man_made') != 'bridge': continue
    c = np.array(f['geometry']['coordinates'])
    if len(c) < 4: continue
    g = Polygon(np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY]).buffer(0)
    if g.area < 150 or g.centroid.x ** 2 + g.centroid.y ** 2 > 9000 ** 2: continue
    if g.intersection(WATER).area / g.area < 0.25: continue
    OUTL.append((p.get('name') or p.get('bridge:name') or '', g))
log('contorni sopra l\'acqua:', len(OUTL))

STONE, IRON, CONC, ASPH, RAIL, WOOD, GOLDS = '#d6cbb2', '#4d5859', '#cfcac0', '#6f6b66', '#3f4446', '#7a5a3a', '#b89a52'
parts = []
def P(**k): parts.append({kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in k.items()})
def beam(name, p0, p1, w, h, c, y, d=None):
    k = dict(name=name, t='beam', p0=[round(v, 2) for v in p0], p1=[round(v, 2) for v in p1], w=w, h=h, c=c, a=0.05, y=y)
    k['cx'] = (p0[0] + p1[0]) / 2; k['cy'] = (p0[1] + p1[1]) / 2
    if d: k['d'] = d
    P(**k)
def boxp(name, cx, cy, ax, along, across, z0, z1, c, y, d=None):
    ux, uy = ax; vx, vy = -uy, ux; hl, hw = along / 2, across / 2
    r = [[cx + sx * hl * ux + sy * hw * vx, cy + sx * hl * uy + sy * hw * vy] for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    k = dict(name=name, t='prism', r=[[round(x, 2), round(yv, 2)] for x, yv in r], z0=z0, z1=z1, c=c, a=0.05, y=y)
    if d: k['d'] = d
    P(**k)

def frame(g):
    w = g.intersection(WATER)
    base = w if (not w.is_empty and w.area > 0.15 * g.area) else g
    m = base.minimum_rotated_rectangle; c4 = list(m.exterior.coords)[:4]
    e1 = (c4[1][0] - c4[0][0], c4[1][1] - c4[0][1]); e2 = (c4[2][0] - c4[1][0], c4[2][1] - c4[1][1])
    # l'asse del ponte attraversa l'acqua: tra i due lati del rettangolo, quello la cui linea centrale ha piu' terra ai due capi
    def score(e):
        Lb = math.hypot(*e); ax = (e[0] / Lb, e[1] / Lb); b0 = m.centroid
        ends = [Point(b0.x + ax[0] * s * (Lb / 2 + 25), b0.y + ax[1] * s * (Lb / 2 + 25)) for s in (-1, 1)]
        return sum(LG.contains(q) for q in ends) + 0.001 * Lb
    if score(e2) > score(e1): e1, e2 = e2, e1
    Lb = math.hypot(*e1); ax = (e1[0] / Lb, e1[1] / Lb); b0 = m.centroid
    cl = LineString([(b0.x - ax[0] * 3000, b0.y - ax[1] * 3000), (b0.x + ax[0] * 3000, b0.y + ax[1] * 3000)]).intersection(g.buffer(1))
    segs = [q for q in getattr(cl, 'geoms', [cl]) if not q.is_empty]
    ss = [(x - b0.x) * ax[0] + (y - b0.y) * ax[1] for q in segs for x, y in q.coords] or [-Lb / 2, Lb / 2]
    s0, s1 = min(ss), max(ss); L = s1 - s0; c = (b0.x + ax[0] * (s0 + s1) / 2, b0.y + ax[1] * (s0 + s1) / 2)
    W = max(5.0, min(base.area / max(Lb, 1), math.hypot(*e2)))
    return c, ax, L, W
def wet_interval(c, ax, L):
    ln = LineString([(c[0] - ax[0] * L / 2, c[1] - ax[1] * L / 2), (c[0] + ax[0] * L / 2, c[1] + ax[1] * L / 2)])
    w = ln.intersection(WATER)
    if w.is_empty: return (-L / 3, L / 3)
    ss = [(x - c[0]) * ax[0] + (y - c[1]) * ax[1] for q in getattr(w, 'geoms', [w]) for x, y in q.coords]
    return min(ss), max(ss)

def bridge(name, g, y, d=None, style='stone', spans=3, col=None, H=1.6, houses=None, grad=None):
    c, ax, L, W = frame(g); wet = wet_interval(c, ax, L)
    col = col or {'stone': STONE, 'iron': IRON, 'beam': CONC, 'foot': IRON}[style]
    if style == 'foot': W = min(W, 12.0)
    s_a, s_b = -L / 2, L / 2
    def z(s): return 0.3 + (H - 0.3) * max(0.0, min(1.0, (s - s_a) / 18.0, (s_b - s) / 18.0))
    def pt(s, off=0.0, dz=0.0): return (c[0] + ax[0] * s - ax[1] * off, c[1] + ax[1] * s + ax[0] * off, z(s) + dz)
    n = max(2, int(L / 14)); ss = [s_a + (s_b - s_a) * i / n for i in range(n + 1)]
    def yy_at(s):   # costruzione graduale dalle due sponde verso il centro (Pont Neuf 1578-1607)
        if not grad: return y
        f = 1 - abs(s) / (L / 2)
        return round(grad[0] + (grad[1] - grad[0]) * f, 1)
    thick = 1.4 if style != 'foot' else 0.9
    for s0, s1 in zip(ss, ss[1:]):
        yb = yy_at((s0 + s1) / 2)
        beam(name, pt(s0, dz=-thick / 2), pt(s1, dz=-thick / 2), W, thick, col, yb, d)
        if style != 'foot': beam(name, pt(s0, dz=0.05), pt(s1, dz=0.05), max(2.0, W - 4.0), 0.1, ASPH, yb, d)
        for off in (-W / 2 + 0.25, W / 2 - 0.25): beam(name, pt(s0, off, 0.55), pt(s1, off, 0.55), 0.4 if style == 'stone' else 0.2, 1.1, col if style == 'stone' else RAIL, yb, d)
    piers = [wet[0] + (wet[1] - wet[0]) * k / spans for k in range(1, spans)] if spans > 1 else []
    for s in piers:
        x, yv, zt = pt(s); boxp(name, x, yv, ax, 4.5 if style == 'stone' else 3.0, W + (1.5 if style == 'stone' else 0), WZ - 1.0, zt - thick, STONE if style != 'beam' else CONC, yy_at(s), d)
    for s in wet:
        x, yv, zt = pt(s); boxp(name, x, yv, ax, 6, W + 1, WZ - 1.0, max(0.3, zt - thick), STONE, yy_at(s), d)
    # archi sotto l'impalcato (pietra: volte piene; ferro: costoloni sottili)
    if style in ('stone', 'iron') or (style == 'foot' and spans > 1):
        sup = [wet[0]] + piers + [wet[1]]
        ribs = 5 if style == 'stone' else 4
        for a_, b_ in zip(sup, sup[1:]):
            span = b_ - a_
            for k in range(ribs):
                off = -W / 2 + 0.8 + (W - 1.6) * k / (ribs - 1)
                prev = None
                for i in range(11):
                    s = a_ + span * i / 10; t = (s - a_) / span
                    zc = WZ + 0.3 + (z(s) - thick - (WZ + 0.3)) * max(0.0, 1 - (2 * t - 1) ** 2) ** 0.5 * 0.92
                    x, yv, _ = pt(s, off); p = (x, yv, zc)
                    if prev: beam(name, prev, p, 1.2 if style == 'stone' else 0.5, 1.4 if style == 'stone' else 0.9, col, yy_at(s), d)
                    prev = p
    if houses:   # case sui due lati dell'impalcato: (anno, demolizione da-a)
        hy, (h0, h1) = houses
        k = 0; s = wet[0] + 4
        while s < wet[1] - 4:
            for sgn in (-1, 1):
                x, yv, zt = pt(s, sgn * (W / 2 + 3.5))
                boxp(name + ' houses', x, yv, ax, 6.0, 7.0, zt - 0.5, zt + rnd.uniform(10, 14), rnd.choice(['#c9b393', '#bda585', '#d3c2a2', '#a88f6e']),
                     hy + rnd.uniform(0, 3), round(h0 + (h1 - h0) * rnd.random(), 2))
                k += 1
            s += 6.5
    return c

def norm(n): return re.sub(r'[^a-z]', '', n.lower().replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ô', 'o').replace('â', 'a'))
# nome normalizzato -> lista di fasi: (anno, demolizione, stile, campate, extra)
# extra: houses=(anno, (dem0, dem1)) ; grad=(a0, a1) ; col
B = {
 'pontneuf': [(1578, None, 'stone', 6, {'grad': (1578, 1607)})],                                      # G005/E029 (fonte)
 'pontnotredame': [(1412.5, 1854, 'stone', 4, {'col': WOOD, 'houses': (1512, (1786, 1788))}),         # G060 (memoria: graduale 1412-1413), G001 case 1510-1512 (fonte)
                   (1854, None, 'stone', 3, {})],                                                      # G002 (fonte)
 'pontauchange': [(1190, 1856, 'stone', 5, {'houses': (1647, (1786, 1788))}),                          # Grand-Pont medievale (stato 1190); G003 1647 (memoria)
                  (1856, None, 'stone', 3, {'grad': (1856, 1860)})],                                    # G004 (fonte)
 'petitpontcardinallustiger': [(1190, 1852, 'stone', 2, {}), (1852.5, None, 'stone', 1, {})],         # stato 1190; G037 (memoria)
 'pontsaintmichel': [(1377.5, 1857, 'stone', 4, {'houses': (1378, (1807, 1809))}), (1857, None, 'stone', 3, {'grad': (1857, 1860)})],   # G063, G008 (memoria)
 'pontmarie': [(1614, None, 'stone', 5, {'grad': (1614, 1635), 'houses': (1635, (1786, 1788))})],     # G007 (fonte)
 'pontdelatournelle': [(1369.5, 1656, 'stone', 4, {'col': WOOD}), (1655.5, 1928, 'stone', 6, {}), (1928, None, 'stone', 1, {'grad': (1928, 1930)})],   # G062, G038, G029 (memoria)
 'pontroyal': [(1685, None, 'stone', 5, {'grad': (1685, 1689)})],                                     # G006 (memoria)
 'pontdesarts': [(1802, None, 'foot', 7, {'grad': (1802, 1804)})],                                     # G009/G010 (memoria)
 'pontdelaconcorde': [(1787, None, 'stone', 5, {'grad': (1787, 1791)})],                               # G011 (fonte)
 'pontalexandreiii': [(1896, None, 'iron', 1, {'grad': (1896, 1900), 'col': '#5d625a'})],              # G012 (fonte)
 'pontdebirhakeim': [(1903, None, 'iron', 3, {'grad': (1903, 1905)})],                                 # G013 (memoria)
 'pontdiena': [(1808, None, 'stone', 5, {'grad': (1808, 1814)})],                                      # G014 (memoria)
 'pontdelalma': [(1854, 1972, 'stone', 3, {'grad': (1854, 1856)}), (1972, None, 'iron', 1, {'grad': (1970, 1974)})],   # G015, G016 (memoria)
 'pontmirabeau': [(1893, None, 'iron', 3, {'grad': (1893, 1896)})],                                    # G017 (memoria)
 'pontaval': [(1967.5, None, 'beam', 4, {})],                                                          # G018 (fonte)
 'pontcharlesdegaulle': [(1993, None, 'beam', 2, {'grad': (1993, 1996)})],                             # G019 (fonte)
 'passerellesimonedebeauvoir': [(2004, None, 'foot', 1, {'grad': (2004, 2006)})],                      # G020 (fonte)
 'pontamont': [(1968, None, 'beam', 4, {'grad': (1968, 1969)})],                                       # G021 (memoria: graduale)
 'pontnational': [(1852, None, 'stone', 5, {'grad': (1852, 1853)})],                                   # G039 (fonte); G022 allargamento 1936-1944
 'pontdetolbiac': [(1881, None, 'stone', 5, {'grad': (1881, 1882)})],                                  # G023 (memoria: graduale)
 'pontdebercy': [(1832, 1864, 'iron', 2, {'col': '#6a6a62'}), (1864, None, 'stone', 5, {})],           # G040, G041 (fonte)
 'pontdugarigliano': [(1963, None, 'beam', 3, {'grad': (1963, 1966)})],                                # G025 (memoria)
 'pontdesully': [(1874, None, 'iron', 3, {'grad': (1874, 1876)})],                                     # G026 (memoria)
 'pontlouisphilippe': [(1833, 1860, 'iron', 2, {}), (1860, None, 'stone', 3, {'grad': (1860, 1862)})],  # G044 (fonte), G030 (memoria)
 'pontdarcole': [(1828, 1854, 'foot', 1, {}), (1854, None, 'iron', 1, {'grad': (1854, 1856)})],         # G043 (fonte), G031 (memoria)
 'pontducarrousel': [(1831, 1935, 'iron', 3, {'grad': (1831, 1834)}), (1935, None, 'stone', 3, {'grad': (1935, 1939)})],   # G042, G032 (fonte)
 'pontdesinvalides': [(1829, 1854, 'iron', 1, {}), (1854, None, 'stone', 4, {'grad': (1854, 1856)})],  # G049, G033 (fonte)
 'passerelleleopoldsedarsenghor': [(1858, 1961, 'iron', 3, {'grad': (1858, 1861)}), (1961, 1992, 'foot', 1, {'grad': (1961, 1962)}), (1997, None, 'foot', 1, {'grad': (1997, 1999)})],   # G065 (memoria), G066, G034 (fonte)
 'pontdegrenellecadetsdesaumur': [(1825, 1966, 'iron', 3, {'grad': (1825, 1827)}), (1966, None, 'beam', 3, {'grad': (1966, 1968)})],   # G045 (fonte), G035 (memoria)
 'pontrouelle': [(1899, None, 'iron', 4, {'grad': (1899, 1900)})],                                     # G036 (memoria: graduale)
 'pontaudouble': [(1626, 1883, 'stone', 2, {}), (1883, None, 'iron', 1, {})],                          # G046, G047 (fonte)
 'pontdausterlitz': [(1802, 1854, 'iron', 5, {'grad': (1802, 1807)}), (1854, None, 'stone', 5, {'grad': (1854, 1855)})],   # G050, G051 (memoria)
 'pontdelarcheveche': [(1828, None, 'stone', 3, {})],                                                  # G052 (fonte)
 'pontsaintlouis': [(1630, 1861, 'stone', 3, {'col': WOOD, 'grad': (1630, 1634)}), (1861, 1970, 'iron', 1, {'grad': (1860, 1861)}), (1970, None, 'iron', 1, {'grad': (1970, 1974)})],   # G053, G054, G055 (memoria)
 'passerelledebilly': [(1900, None, 'foot', 1, {})],                                                    # G056/G057 (G057 memoria: stesso aspetto)
}
WD = {}
for nm_f in ('wikidata_costruzione.json', 'wikidata_apertura.json'):
    p_ = f'{RAW}/extra/{nm_f}'
    if not os.path.exists(p_): continue
    for r_ in json.load(open(p_))['results']['bindings']:
        m_ = re.match(r'(\d{4})', r_['date']['value'])
        if m_ and 1100 < int(m_.group(1)) <= 2026: WD.setdefault(norm(r_['itemLabel']['value']), int(m_.group(1)))

done, cnt = set(), {'scheda': 0, 'wikidata': 0, 'urban': 0}
labels = []
for name, g in sorted(OUTL, key=lambda t: -t[1].area):
    key = norm(name)
    if key in B:
        if key in done and key not in ('pontneuf', 'pontdesully'): continue   # pezzi doppi; Pont Neuf e Sully sono in due parti (isola in mezzo)
        for (y, d, style, spans, ex) in B[key]:
            c = bridge(name, g, y, d, style, spans, col=ex.get('col'), houses=ex.get('houses'), grad=ex.get('grad'))
        if key not in done: labels.append({'name': name.split(' - ')[0], 'x': round(c[0], 1), 'y': round(c[1], 1), 'z': 12, 'from': B[key][0][0], 'to': 9999})
        done.add(key); cnt['scheda'] += 1; continue
    y = WD.get(key)
    if y: cnt['wikidata'] += 1
    else:
        c, ax, L, W = frame(g)
        ends = [(c[0] - ax[0] * L / 2, c[1] - ax[1] * L / 2), (c[0] + ax[0] * L / 2, c[1] + ax[1] * L / 2)]
        u = [H.urban_year(*e) for e in ends]; y = min(2000, max(u) + 3) if max(u) < 9000 else 1900
        if 'metro' in key or 'viaduc' in key: y = max(y, 1905)
        cnt['urban'] += 1
    style = 'beam' if y > 1940 else ('iron' if y > 1840 else 'stone')
    if 'passerelle' in key: style = 'foot'
    bridge(name or 'bridge', g, float(y), None, style, 3 if g.area > 2500 else 1)
miss = sorted(set(B) - done)
log('ponti:', cnt, '| scheda senza contorno OSM:', miss)
LM = json.load(open(f'{DATA}/landmarks.json'))
LM['parts'] = [p_ for p_ in LM['parts'] if not p_.get('_bridge')] + [dict(p_, _bridge=1) for p_ in parts]
LM['labels'] = [l_ for l_ in LM.get('labels', []) if not l_.get('_bridge')] + [dict(l_, _bridge=1) for l_ in labels]
json.dump(LM, open(f'{DATA}/landmarks.json', 'w'))
log('FATTO parti dei ponti:', len(parts), '| totale parti monumenti:', len(LM['parts']))
