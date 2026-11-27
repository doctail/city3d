"""Parigi: completa story.json history (walls, fires, gutting, water) da dati reali.
Uso: python3 cities/parigi/build_history.py WIKI_DIR   (WIKI_DIR = testi Wikipedia scaricati, *.txt, vedi WIKI)
Geometrie: pack legacy data_parigi_src (ALPAGE: landphases.json, landmarks.json parti mura/incendi, wall_p.json). Non modifica il pack.
Ogni citazione e' verificata come sottostringa del testo scaricato (assert)."""
import gzip, json, math, os, re, sys
from shapely.geometry import Polygon, LineString, MultiPoint
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SP = os.path.join(ROOT, 'cities', 'parigi', 'story.json')
SRC = os.path.join(ROOT, 'data_parigi_src')
WD = sys.argv[1]
s = json.load(open(SP))
LAT0, LON0 = s['city']['lat0'], s['city']['lon0']
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def ll(x, y): return [round(LAT0 + y / KY, 6), round(LON0 + x / KX, 6)]
def gz(n): return json.load(gzip.open(os.path.join(SRC, n)))

# ---------------------------------------------------------------- fonti nuove (Wikipedia EN, citazione verificata)
WIKI = {  # chiave -> (file testo, titolo pagina, url)
    'cw': ('Walls_of_Paris.txt', 'City walls of Paris', 'City_walls_of_Paris'),
    'pa': ('Wall_of_Philip_II_Augustus.txt', 'Wall of Philip II Augustus', 'Wall_of_Philip_II_Augustus'),
    'c5': ('Wall_of_Charles_V.txt', 'Wall of Charles V', 'Wall_of_Charles_V'),
    'fg': ('Wall_of_the_Farmers_General.txt', 'Wall of the Fermiers generaux', 'Wall_of_the_Fermiers_g%C3%A9n%C3%A9raux'),
    'th': ('Thiers_wall.txt', 'Thiers wall', 'Thiers_wall'),
    'hr': ("Haussmann_s_renovation_of_Paris.txt", "Haussmann's renovation of Paris", "Haussmann%27s_renovation_of_Paris"),
    'sg': ('Boulevard_Saint_Germain.txt', 'Boulevard Saint-Germain', 'Boulevard_Saint-Germain'),
    'bh': ('Boulevard_Haussmann.txt', 'Boulevard Haussmann', 'Boulevard_Haussmann'),
    'op': ('Avenue_de_l_Op%C3%A9ra.txt'.replace('%C3%A9', 'é'), "Avenue de l'Opera", "Avenue_de_l%27Op%C3%A9ra"),
    'is': ('Île_Saint_Louis.txt', 'Ile Saint-Louis', '%C3%8Ele_Saint-Louis'),
    'il': ('Île_Louviers.txt', 'Ile Louviers', '%C3%8Ele_Louviers'),
    'cm': ('Canal_Saint_Martin.txt', 'Canal Saint-Martin', 'Canal_Saint-Martin'),
    'co': ('Canal_de_l_Ourcq.txt', "Canal de l'Ourcq", "Canal_de_l%27Ourcq"),
    'cd': ('Canal_Saint_Denis.txt', 'Canal Saint-Denis', 'Canal_Saint-Denis'),
    'bv': ('Bassin_de_la_Villette.txt', 'Bassin de la Villette', 'Bassin_de_la_Villette'),
    'nd': ('Notre_Dame_de_Paris_fire.txt', 'Notre-Dame fire', 'Notre-Dame_fire'),
    'tu': ('Tuileries_Palace.txt', 'Tuileries Palace', 'Tuileries_Palace'),
    'hv': ('Hôtel_de_Ville__Paris.txt', 'Hotel de Ville, Paris', 'H%C3%B4tel_de_Ville,_Paris'),
}
TXT = {k: open(os.path.join(WD, v[0])).read() for k, v in WIKI.items()}
nid = max(int(k[1:]) for k in s['sources'] if re.fullmatch(r'W\d+', k)) + 1
NEW = {}
def src(key, quote):
    """Aggiunge (o riusa) una fonte: la citazione deve essere sottostringa del testo scaricato."""
    global nid
    assert quote in TXT[key], f'citazione non trovata in {key}: {quote[:70]}'
    for k, v in s['sources'].items():
        if v.get('quote') == quote and WIKI[key][2] in v['url']: return k
    i = f'W{nid:03d}'; nid += 1
    s['sources'][i] = {'url': 'https://en.wikipedia.org/wiki/' + WIKI[key][2], 'title': 'Wikipedia (EN): ' + WIKI[key][1], 'quote': quote}
    NEW[i] = quote
    return i

LP = gz('landphases.json.gz')
LM = gz('landmarks.json.gz')
def simp(poly, tol=1.0):
    p = poly.buffer(0).simplify(tol)
    return p

def ring_ll(poly, tol=1.0):
    p = simp(poly, tol)
    if p.geom_type == 'MultiPolygon': p = max(p.geoms, key=lambda g: g.area)
    return [ll(x, y) for x, y in list(p.exterior.coords)[:-1]]

# ================================================================== MURA
def parts_of(name): return [p for p in LM['parts'] if p['name'] == name]
def ctr(p): g = Polygon(p['r']); return (g.centroid.x, g.centroid.y)
def order_angle(pts, c=(0, 0)):
    return sorted(pts, key=lambda q: math.atan2(q[1] - c[1], q[0] - c[0]))
def chain(pts, start):
    pts = list(pts); out = [min(pts, key=lambda q: math.hypot(q[0] - start[0], q[1] - start[1]))]; pts.remove(out[0])
    while pts:
        q = min(pts, key=lambda a: math.hypot(a[0] - out[-1][0], a[1] - out[-1][1])); pts.remove(q); out.append(q)
    return out
def movavg(pts, k):
    return [(sum(p[0] for p in pts[max(0, i - k):i + k + 1]) / len(pts[max(0, i - k):i + k + 1]), sum(p[1] for p in pts[max(0, i - k):i + k + 1]) / len(pts[max(0, i - k):i + k + 1])) for i in range(len(pts))]
def smooth_line(pts, tol):
    return list(LineString(pts).simplify(tol).coords)

walls = []
# Filippo Augusto: perimetro ALPAGE in DATA/wall_p.json (la stessa cinta che il render usa per gli orti)
wp = gz('wall_p.json.gz')
a1 = src('pa', 'The walls were fortified from 1190 to 1213, built under the command of Philip Augustus who also contributed to the cost of building the wall.')
a2 = src('pa', 'In 1533, Francis I demolished the Right Bank gates and authorised the leasing of the land enclosed by the wall without authorising the demolition of the wall itself.')
a3 = src('pa', 'The last remaining gates, unsuited to ever-increasing traffic, were razed in the 1680s when the wall became completely invisible.')
walls.append({'name': 'Philip Augustus wall', 'ring': [ll(x, y) for x, y in wp], 'built': [1190, 1213], 'demolished': [1533, 1685],
              'height': 8, 'width': 2.5, 'towers_every_m': 60, 'src': [a1, a2, a3], 'conf': 'medium',
              'note': 'Tracciato = perimetro ALPAGE (Enceintes) del pack legacy (DATA/wall_p.json, 20 vertici, lo stesso che il render usa per gli orti attorno alla citta\'). Date costruzione: Wikipedia. Smantellamento a tratti: 1533 (porte della Rive Droite) - anni 1680 (ultime porte); le parti legacy hanno d fra 1505 e 1780 (ALPAGE, memoria).'})

# Carlo V: solo riva destra; linea = media dei due bordi della fascia ALPAGE (muro + fossato), per bin angolare di 1 grado attorno a ND
PAr = Polygon(wp)
cv = [ctr(p) for p in parts_of('wall_Charles-')]
from shapely.geometry import Point
cv = [q for q in cv if PAr.exterior.distance(Point(q)) > 60]
bins = {}
for x, y in cv:
    b = round(math.degrees(math.atan2(y - 250, x - 100)) / 3)
    if -8 <= b <= 56: bins.setdefault(b, []).append((x, y))      # solo l'arco di riva destra (da ~ -24 a ~ +168 gradi)
line = [(sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v)) for b, v in sorted(bins.items(), reverse=True)]
line = movavg(line, 2)
# da ovest (angolo alto) a est/sud
c1 = src('c5', 'The wall of Charles V, built from 1356 to 1383 is one of the city walls of Paris built on orders granted by Charles V of France.')
c2 = src('c5', 'The wall, as well as its extension built by Louis XIII on the west side was destroyed in 1670, on orders of Louis XIV after his victories in the Netherlands and Germany.')
walls.append({'name': 'Charles V wall (right bank)', 'line': [ll(x, y) for x, y in smooth_line(line, 6)], 'built': [1356, 1383], 'demolished': [1670, 1700],
              'height': 7, 'width': 2.5, 'towers_every_m': 60, 'src': [c1, c2], 'conf': 'medium',
              'note': 'Linea = asse della fascia ALPAGE (muro + fossato) del pack legacy, solo riva destra (sulla riva sinistra Carlo V riusa Filippo Augusto). 1670 = ordine di Luigi XIV (Wikipedia); lo smantellamento a tratti 1670-1700 viene dalle parti legacy (ALPAGE/memoria).'})

# Luigi XIII = "yellow ditches wall" (City walls of Paris); nel pack legacy si chiama "Fossati gialli" (parti con anni 1566-1643: qui valgono le date di Wikipedia)
fj = [ctr(p) for p in parts_of('wall_Fossés j')]
fjl = movavg(chain(fj, (-2000, 1150)), 6)
l1 = src('cw', 'The Louis XIII Wall, also known as the "yellow ditches wall", was designed by Jacques Lemercier and built between 1633 and 1636.')
l2 = src('cw', 'Many historical walls were eventually destroyed (as in 1670, when Louis XIV ordered the demolition of the Louis XIII Wall)')
walls.append({'name': 'Louis XIII wall (yellow ditches)', 'line': [ll(x, y) for x, y in smooth_line(fjl, 6)], 'built': [1633, 1636], 'demolished': [1670, 1700],
              'height': 6, 'width': 2.5, 'src': [l1, l2], 'conf': 'medium',
              'note': 'Linea = asse dei tratti ALPAGE "Fossés jaunes" del pack legacy (le parti legacy hanno costruzione 1566-1643, qui vale Wikipedia 1633-1636). Solo la parte occidentale della riva destra.'})

# Fermiers generaux: anello = centroidi dei tratti ALPAGE ordinati per angolo attorno a ND
fgp = order_angle([ctr(p) for p in parts_of('wall_Fermiers')])
fg_poly = Polygon(fgp)
f1 = src('fg', 'Built between 1784 and 1791, the 24 km (15 mi) wall crossed the districts')
f2 = src('fg', 'The wall, having become obsolete from a fiscal point of view, was demolished in less than a month in January 1860.')
f3 = src('fg', 'although elements of some of its barrières or custom houses remain')
KEEP = [(48.8836, 2.3697), (48.8484, 2.3958), (48.8339, 2.3324), (48.8797, 2.3091)]   # Rotonde de la Villette, Trone, Enfer, Monceau (hist_parigi/landmarks_parigi KEEP_BARR)
walls.append({'name': 'Farmers-General wall', 'ring': [ll(x, y) for x, y in smooth_line(fgp + [fgp[0]], 8)[:-1]], 'built': [1784, 1791], 'demolished': [1860, 1861],
              'height': 3.5, 'width': 1.5, 'src': [f1, f2, f3], 'conf': 'medium', 'keep': [[a, b, 60] for a, b in KEEP],
              'note': 'Anello = tratti ALPAGE (Enceintes) del pack legacy ordinati per angolo (semplificato a 8 m). keep = barriere di Ledoux che restano (Rotonde de la Villette, Trone, Enfer, Monceau), le stesse del modulo legacy. Demolizione: gennaio 1860 per Wikipedia, "primi anni 1860" nella stessa pagina.'})

# Thiers: tratti a ~70 m fuori dai Boulevards des Marechaux (modulo legacy, tracciato [Likely])
def radial_ring(pts, step=1.0, win=9, tol=250):
    """Anello a raggio mediano per bin angolare, scartando i bin che si discostano dalla mediana mobile (tratti di altre vie)."""
    import statistics
    nb = int(360 / step); R = [None] * nb
    for x, y in pts:
        b = int(((math.degrees(math.atan2(y, x)) + 360) % 360) / step) % nb
        (R[b] if R[b] else R.__setitem__(b, [])).append(math.hypot(x, y)) if R[b] else R.__setitem__(b, [math.hypot(x, y)])
    med = [statistics.median(r) if r else None for r in R]
    out = []
    for b in range(nb):
        if med[b] is None: continue
        nbh = [med[(b + k) % nb] for k in range(-win, win + 1) if med[(b + k) % nb] is not None]
        m = statistics.median(nbh)
        if abs(med[b] - m) <= tol: out.append((b, med[b]))
    return [(r * math.cos(math.radians((b + 0.5) * step)), r * math.sin(math.radians((b + 0.5) * step))) for b, r in out]
thp = radial_ring([ctr(p) for p in parts_of('wall_Thiers')])
t1 = src('th', 'It was an enclosure constructed between 1841 and 1846 and was proposed by the French prime minister Adolphe Thiers but was actually implemented by his successor, Marshal Soult.')
t2 = src('th', 'On 19 April 1919, there was a vote on the laws to permit the demolition of the enceinte fortifications.')
walls.append({'name': 'Thiers wall', 'ring': [ll(x, y) for x, y in smooth_line(thp + [thp[0]], 10)[:-1]], 'built': [1841, 1846], 'demolished': [1919, 1929],
              'height': 10, 'width': 4, 'src': [t1, t2], 'conf': 'medium',
              'note': 'Anello = tratti del modulo legacy (muro ~65-80 m fuori dai Boulevards des Marechaux, OSM; tracciato [Likely] e non ALPAGE) ordinati per angolo. Demolizione 1919-1929: voto 19 aprile 1919 (Wikipedia) e legacy B010.'})

# ================================================================== INCENDI (poligoni reali dal pack legacy, foglia = impronta del monumento)
FR = {f['name']: f for f in LM['fires']}
fires = []
q = src('nd', 'On 15 April 2019, at 18:18 CEST, a structural fire broke out in the roof space of Notre-Dame de Paris')
f = FR['Notre-Dame fire']
fires.append({'name': 'Notre-Dame fire', 'ring': [ll(x, y) for x, y in f['poly']], 'y': 2019.288, 'y1': 2019.292, 'destroy': False, 'flames': 40, 'smoke': 6, 'src': [q], 'conf': 'high',
              'note': 'Solo fuoco e fumo (il tetto e la guglia sono fasi del monumento). Poligono = copertura sopra la navata, dal modulo legacy.'})
q = src('tu', 'On 23 May 1871, during the suppression of the Paris Commune, 12 men under the orders of the Commune\'s former chief military commander Jules Bergeret set the Tuileries on fire using petroleum, liquid tar, and turpentine.')
f = FR['Tuileries fire (Commune)']
fires.append({'name': 'Tuileries fire (Commune)', 'ring': [ll(x, y) for x, y in f['poly']], 'y': 1871.39, 'y1': 1871.40, 'destroy': False, 'flames': 60, 'smoke': 8, 'src': [q], 'conf': 'high',
              'note': '23 maggio 1871 = 1871.39. Demolizione 1883 gestita da landmarks.demolished.'})
q = src('hv', 'On 23 and 24 May 1871, when defeat became increasingly imminent and the French army approached the building, the Communards set fire to the Hôtel de Ville')
f = FR['Hotel de Ville fire (Commune)']
fires.append({'name': 'Hotel de Ville fire (Commune)', 'ring': [ll(x, y) for x, y in f['poly']], 'y': 1871.39, 'y1': 1871.40, 'destroy': False, 'flames': 45, 'smoke': 6, 'src': [q], 'conf': 'high',
              'note': '23-24 maggio 1871; ricostruzione 1873-1882 = fasi del monumento.'})

# ================================================================== GUTTING Haussmann (capi/vertici della strada [lat, lon] + larghezza; stima ~ +-40 m)
Q_PHASE = src('hr', 'directed by his prefect of Seine, Georges-Eugène Haussmann, between 1853 and 1870.')
Q_2ND = src('hr', 'His second phase, approved by the Emperor and parliament in 1858 and begun in 1859, was much more ambitious.')
Q_RIV = src('hr', 'The Rue de Rivoli was completed, and the new hotel opened in March 1855, in time to welcome guests to the Exposition.')
Q_SEB = src('hr', 'In 1855, work began on the north–south axis, beginning with the Boulevard de Strasbourg and Boulevard Sébastopol')
Q_MIC = src('hr', 'On the left bank, the north–south axis was continued by Boulevard Saint-Michel, which was cut in a straight line from the Seine to the Observatory')
Q_SG = src('hr', '1877: completion of the boulevard Saint-Germain')
Q_OP = src('hr', "1877: completion of the avenue de l'Opéra")
Q_OP2 = src('op', "The Avenue de l'Opéra (French pronunciation: [avny d(ə) lɔpeʁa]) was created from 1864 to 1879 as part of Haussmann's renovation of Paris.")
Q_BH = src('bh', 'However, the boulevard was not completed until well after his death.')
START = s['city']['start_year']
def street(name, pts, w, until, srcs, conf, note):
    ln = LineString([L(*p) for p in pts])
    return {'name': name, 'ring': ring_ll(ln.buffer(w, cap_style=2, join_style=2), 0.8), 'from': START, 'until': until, 'src': srcs, 'conf': conf,
            'note': note + ' Linea ricavata dai capi/vertici della strada (coordinate [lat, lon] stimate da riferimenti Wikipedia/Wikidata), non da OSM (Overpass non raggiungibile): errore atteso ~40 m, da controllare nel confronto locale. "from" = anno di partenza (tessuto antico gia\' presente).'}
gut = [
    street('Rue de Rivoli extension (Louvre-Rue Saint-Antoine)', [(48.8603, 2.3402), (48.8588, 2.3455), (48.8566, 2.3510), (48.8556, 2.3535), (48.8553, 2.3597)], 12, 1855.2, [Q_PHASE, Q_RIV], 'medium',
           'Rivoli completata al Louvre-Hotel de Ville-Rue Saint-Antoine; hotel inaugurato marzo 1855 (until 1855.2).'),
    street('Boulevard de Strasbourg and Sebastopol', [(48.8584, 2.3470), (48.8640, 2.3505), (48.8696, 2.3544), (48.8740, 2.3565), (48.8766, 2.3588)], 15, 1859.0, [Q_SEB, Q_2ND], 'low',
           'until 1859 = stima: lavori iniziati nel 1855 (Wikipedia), prima fase conclusa prima dell\'inizio della seconda (1859). Boulevard de Sebastopol lungo 1,3 km (Wikipedia).'),
    street('Boulevard Saint-Michel', [(48.8535, 2.3441), (48.8509, 2.3430), (48.8462, 2.3406), (48.8432, 2.3397)], 15, 1860.0, [Q_MIC, Q_2ND], 'low',
           'until 1860 = stima (prima fase, assi nord-sud; ribattezzato Saint-Michel nel 1867 secondo Wikipedia).'),
    street('Boulevard Saint-Germain', [(48.8503, 2.3570), (48.8500, 2.3485), (48.8508, 2.3441), (48.8521, 2.3388), (48.8531, 2.3345), (48.8549, 2.3275), (48.8573, 2.3238), (48.8605, 2.3195)], 15, 1877.0, [Q_PHASE, Q_SG], 'medium',
           'Completato nel 1877 (Wikipedia); aperto a sezioni dal 1855 [stima], qui un solo until.'),
    street('Boulevard Haussmann', [(48.8716, 2.3386), (48.8731, 2.3331), (48.8738, 2.3283), (48.8745, 2.3212), (48.8747, 2.3130), (48.8752, 2.3050)], 18, 1870.0, [Q_PHASE, Q_BH], 'low',
           'until 1870 = stima per il tratto principale; il raccordo ai Boulevards des Italiens e\' solo del 1926 (Wikipedia: completato molto dopo la sua morte).'),
    street("Avenue de l'Opera", [(48.8633, 2.3365), (48.8672, 2.3340), (48.8707, 2.3318)], 15, 1877.0, [Q_OP, Q_OP2], 'medium',
           "Avenue creata 1864-1879 (Wikipedia, pagina dell'avenue); completamento 1877 (Haussmann's renovation of Paris)."),
]

# ================================================================== WATER (poligoni ALPAGE del pack legacy, landphases.json)
def lp_poly(i): return Polygon(LP[i]['r']).buffer(0)
def lp_field_to(lo, hi, xr, yr):
    out = []
    for i, p in enumerate(LP):
        if p['from'] != -9999 or not (lo <= p['to'] <= hi) or p['c'] != 'field': continue
        g = Polygon(p['r']).buffer(0)
        if g.is_empty: continue
        cx, cy = g.centroid.x, g.centroid.y
        if xr[0] <= cx <= xr[1] and yr[0] <= cy <= yr[1] and math.hypot(cx, cy) < 8000: out.append(i)
    return out
water = []
def add_water(name, idx, frm, to, srcs, conf, note, c='field'):
    for k, i in enumerate(idx):
        g = lp_poly(i)
        if g.area < 30: continue
        for part in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
            if part.area < 30: continue
            e = {'name': f'{name} [ALPAGE #{i}]', 'ring': ring_ll(part, 1.5), 'c': c, 'src': srcs, 'conf': conf, 'note': note}
            if frm is not None: e['from'] = frm
            if to is not None: e['to'] = to
            water.append(e)

# A002 Ile Louviers: bracci riempiti (ALPAGE urban dal 1843)
q = src('il', 'Never built up, it was connected with the north bank of the river in 1843.')
add_water('Ile Louviers arm (Mail) filled', [8, 9], 1843, None, [q], 'high', 'Wikipedia: unita alla riva destra nel 1843 (altrove nella stessa pagina: ramo riempito entro il 1847). Poligoni = fasi ALPAGE del pack legacy (landphases.json #8, #9).')
# A013 / A014 volte del canale
q = src('cm', 'Nearly half its length (2,069 metres (2,263 yd)), between the Rue du Faubourg du Temple and the Place de la Bastille, was covered in the mid-19th century to create wide boulevards and public spaces on the surface.')
add_water('Canal Saint-Martin vaulted (Richard-Lenoir)', [121], 1862, None, [q], 'medium', '"Mid-19th century" (Wikipedia); 1862 = fine della copertura 1860-1862 (mairie du 10e, non riletta in pagina scaricata). Poligono ALPAGE #121.')
add_water('Canal Saint-Martin vaulted (Temple vault)', [62], 1906, None, [], 'low', 'stima: voute du Temple 1906 (A014 scheda, non verificata su pagina scaricata). Poligono ALPAGE #62.')
# A012 Bassin de l'Arsenal (to 1806 stima)
add_water("Bassin de l'Arsenal (dug)", [23, 25, 31, 32, 33, 187, 188, 218, 219, 220], None, 1806, [], 'low',
          'stima: anno 1806 da scheda A012 (indicativo, non trovato in pagina scaricata); i poligoni ALPAGE (#23,25,31,32,33,187,188,218-220) hanno fine 1807-1809.')
# A011 Bassin de la Villette: riempito d'acqua 2 dicembre 1808
q = src('bv', 'It was filled with water on 2 December 1808.')
add_water('Bassin de la Villette (dug)', [155], None, 1808.92, [q], 'high', '2 dicembre 1808 = 1808.92 (Wikipedia). Poligono ALPAGE #155 (le fasi ALPAGE hanno fine 1812.6).')
# A007 Canal Saint-Martin (scavo; Wikipedia: opera ordinata 1802, lavori fino al 1825)
q = src('cm', 'Construction of the canal was ordered by Napoleon I in 1802 and construction took place until 1825, funded by a new tax on wine.')
add_water('Canal Saint-Martin (dug)', [36, 37, 61, 75, 120, 189, 190], None, 1822, [q], 'medium', 'to 1822 = inizio cantiere (scheda A006/A007, prima pietra 3 maggio 1822); Wikipedia: lavori fino al 1825. Poligoni ALPAGE (fine 1822.5-1824.3).')
# A003 Canal de l'Ourcq (a La Villette, 15 agosto 1813)
q = src('co', 'The bassin de la Villette was filled with water on 2 December 1808, and on 15 August 1813 the first boat traveled through the canal.')
idx = [i for i in lp_field_to(1810.0, 1813.1, (1000, 9000), (3000, 9000)) if i != 155]
add_water("Canal de l'Ourcq (dug)", idx, None, 1813.62, [q], 'high', '15 agosto 1813 = 1813.62 (Wikipedia). Poligoni ALPAGE del pack legacy (fine 1810.7-1813).')
# A005 Canal Saint-Denis (maggio 1821)
q = src('cd', 'In May 1821, the canal opened, having expended less than its allotted budget.')
idx = lp_field_to(1820.9, 1821.1, (-3000, 5000), (4700, 9500))
add_water('Canal Saint-Denis (dug)', idx, None, 1821.4, [q], 'high', 'maggio 1821 = 1821.4 (Wikipedia). Poligoni ALPAGE del pack legacy (fine 1821.0), entro il raggio della citta\'.')
# A001 Ile Saint-Louis: canale tra Ile Notre-Dame e Ile aux Vaches (nessun poligono ALPAGE nel pack): striscia stimata
q = src('is', 'The canal dividing the island was filled, plots laid out and imposing residences built.')
q0 = src('is', 'In 1360 it was cut in half by a canal, at about the current Rue Poulettiere')
axis = LineString([L(48.8527, 2.3566), L(48.8511, 2.3568)])
water.insert(0, {'name': 'Ile Saint-Louis channel (Notre-Dame / aux Vaches) filled', 'ring': ring_ll(axis.buffer(11, cap_style=2), 0.5), 'c': 'field', 'from': 1655, 'src': [q0, q], 'conf': 'low',
                 'note': 'stima: striscia 22 m che attraversa l\'isola all\'altezza di Rue Poulletier (Wikipedia: "at about the current Rue Poulettiere"); nessun poligono ALPAGE/OSM nel pack. Anno 1655 convenzionale (scheda A001; Wikipedia: canale riempito dopo il 1616).'})

# ================================================================== scrittura
H = s['history']
H['walls'] = walls; H['fires'] = fires; H['gutting'] = gut; H['water'] = water
# doppione ponti: Pont Neuf e Pont Alexandre III restano come monumenti (bridge_arches con la loro linea e fasi); via da history.bridges
rm = [b['name'] for b in H['bridges'] if b['name'] in ('Pont Neuf', 'Pont Alexandre III')]
H['bridges'] = [b for b in H['bridges'] if b['name'] not in rm]
for lm in s['landmarks']:
    if lm['name'] in rm: lm['note'] = (lm.get('note', '') + ' [history.bridges: voce rimossa per evitare il doppio impalcato; qui anche il ponte dopo l\'apertura: nessun "d".]').strip()
for k in ('_haussmann_note',):
    s.pop(k, None)
s['_legacy_gaps'] = [g for g in s.get('_legacy_gaps', []) if g.get('path') not in ('history.water',) and g.get('field') != 'walls/gutting/lost/fires']
json.dump(s, open(SP, 'w'), indent=1, ensure_ascii=False)
print('walls', len(walls), 'fires', len(fires), 'gutting', len(gut), 'water', len(water), 'new sources', len(NEW), 'removed bridges', rm)
