# Regia di Parigi (27 ott 2026; 29 ott: 9:30 = 13.680 fotogrammi, capitoli ogni 15-20 s). UN SOLO PIANO SEQUENZA (SPEC_CAMERA_DRONE):
# obiettivo fisso 35 mm, la camera "zooma" muovendosi, quota 300-1.000 m sopra il suolo, mai a terra. Prime crescite entro 20 s
# (1190: Notre-Dame, Louvre e mura di Filippo Augusto salgono subito), parte densa entro ~1:00 (il 1550). Soste SOLO dove gli
# edifici cambiano davanti alla camera (regola della regia). Anni dalla scheda di validazione (ID nei commenti).
# VELOCITA' DEL TEMPO: come Siviglia (tempo proporzionale agli edifici che nascono o muoiono, limiti 0,5-8 anni/s; prima del
# 1840 fino a 12 anni/s). Notte negli ultimi ~40 s (finestre accese, lampioni lungo le strade: roads.json).
# Uso: python regia_parigi.py DATA -> schedule_parigi.json, schedule_parigi_night.json, regia_parigi.png, regia_parigi.txt,
#      eventi_parigi.json (cartelli per l'overlay Remotion)
import json, math, sys
import numpy as np
from scipy.interpolate import PchipInterpolator

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data_parigi'
FPS = 24; NFR = 9360; DUR = NFR / FPS           # 390 s = 6:30 (correzione regia 29 ott: durata dal contenuto, 5:30-7:00, tetto 4 $)
NIGHT_T = DUR - 40.0
LENS = 35
LAT0, LON0 = 48.85297, 2.34993
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
LM = json.load(open(f'{DATA}/landmarks.json'))
def lab(name):
    for l_ in LM['labels']:
        if l_['name'] == name: return (l_['x'], l_['y'])
    raise KeyError(name)
dem = np.load(f'{DATA}/dem.npz'); DEM, DX0, DY0, DC = dem['D'], float(dem['x0']), float(dem['y0']), float(dem['cell'])
def ground(x, y):
    i, j = int((y - DY0) // DC), int((x - DX0) // DC)
    if 0 <= i < DEM.shape[0] and 0 <= j < DEM.shape[1]: return float(DEM[i, j])
    return 0.0
def ground_max(x, y, r=400):
    return max(ground(x + dx, y + dy) for dx in (-r, 0, r) for dy in (-r, 0, r))

ND = lab('Notre-Dame'); LOUVRE = lab('Louvre'); BASTILLE = lab('Bastille'); INVAL = lab('Les Invalides'); EIFFEL = lab('Eiffel Tower')
TUIL = lab('Tuileries Palace'); OPERA = lab('Palais Garnier'); SACRE = lab('Sacré-Cœur'); MONTP = lab('Tour Montparnasse')
PONTNEUF = L(48.8572, 2.3413); ETOILE = lab('Arc de Triomphe'); DEFENSE = lab('La Défense')

# ---------- ancore (t, anno) ----------
FIXED = [(0.0, 2026.0), (3.0, 2026.0), (9.5, 1190.0), (NIGHT_T, 2026.0)]
SOSTE_SKIP = '_skip_'
# ---------- soste: (anno inizio, anno fine, durata s, cartello, bersaglio (x, y, z), quota camera m, azimut inizio, fine[, inclinazione])
#   azimut = da dove guarda la camera (0 = da nord, 180 = da sud, 225 = da sud-ovest, sopra la Senna col sole alle spalle)
SOSTE = [
    (1190.0, 1215.0, 8.0, 'Philippe Augustus walls the city (1190-1215)', (ND[0] - 150, ND[1] + 200, 20), 420, 236, 206),   # B001/B002, E001, E021
    (1356.0, 1383.0, 6.0, 'Charles V: a new wall and the Bastille (1356-1383)', (BASTILLE[0] - 500, BASTILLE[1] + 300, 15), 480, 200, 172),   # B003, E010
    (1578.0, 1612.0, 6.5, 'Pont Neuf and the Grande Galerie (1578-1612)', (PONTNEUF[0] - 150, PONTNEUF[1] + 150, 10), 400, 222, 196),   # G005, E033, E012
    (1670.0, 1706.0, 6.0, 'Les Invalides and its golden dome (1670-1706)', (*INVAL, 40), 420, 196, 170),   # E006, E036
    (1784.0, 1791.0, 5.5, 'The Bastille falls (1789)', (*BASTILLE, 15), 400, 214, 188),   # E011, B007
    (1820.0, 1826.0, 5.0, 'Canal Saint-Martin is dug (1822-1825)', (*L(48.8705, 2.3655), 0), 430, 206, 182),   # A006/A007 (graduale 1822-1825)
    (1852.0, 1872.0, 13.0, "Haussmann cuts through old Paris (1853-1870)", (-900, 900, 10), 470, 200, 160),   # F004, C001-C008, E038, E009; dentro: la Comune (maggio 1871, F005/E020): un'unica sosta, prima il tempo tornava fermo 16 s sul 1871
    (1886.5, 1889.6, 6.0, 'The Eiffel Tower rises (1887-1889)', (*EIFFEL, 120), 520, 226, 196, 22),   # E004
    (1966.0, 1977.5, 6.0, 'Tour Montparnasse and Centre Pompidou (1969-1977)', (MONTP[0] + 300, MONTP[1] + 400, 60), 560, 212, 188),   # E016, E015
    (2018.9, 2024.95, 6.0, 'Notre-Dame: fire and rebirth (2019-2024)', (*ND, 40), 380, 232, 204),   # E023, E024
]
SOSTE = [s_ for s_ in SOSTE if s_[3] != '_skip_']
STOP_SUB = {'The Bastille falls (1789)': '14 July 1789', 'The Commune: Tuileries and Hôtel de Ville burn (1871)': 'May 1871',
            'Notre-Dame: fire and rebirth (2019-2024)': '15 April 2019 – 7 December 2024'}
SUBSCRIBE_T = round(DUR * 0.48, 1)   # a meta video (era 255 s su 8:30)
CAPS_NIGHT = [(NIGHT_T + 9.0, '1889', 'Eiffel Tower', 'Built in 26 months for the World Fair; meant to stand 20 years.'),
              (NIGHT_T + 22.0, '1190 → 2026', '836 years of Paris', 'From an island city to 2 million people.')]
# ---------- didascalie continue: (anno, data, titolo, una riga) — dalla scheda di validazione (ID) ----------
CAPS = [
    (1190.5, '1190', 'A wall for Paris', 'Philippe Augustus orders a stone wall before leaving on crusade.'),      # B001
    (1196.0, '1190s', 'Notre-Dame rises', 'The choir is done; the nave goes up next.'),                            # E021
    (1202.0, '1202', 'The Louvre fortress', 'A castle guards the wall where it meets the Seine.'),                  # E001
    (1215.0, '1215', 'The Left Bank wall closes', 'About 253 hectares inside the walls.'),                          # B002
    (1240.0, 'c. 1240', '50,000 Parisians', 'Already one of the largest cities in Europe (estimate).'),            # D002
    (1248.0, '1248', 'Sainte-Chapelle', 'A royal chapel built to hold the Crown of Thorns.'),                       # E028
    (1290.0, 'c. 1290', '~120,000 people', 'Estimate; Paris is the biggest city in Western Europe.'),               # D003
    (1345.0, 'c. 1345', 'Notre-Dame completed', 'Almost two centuries after the first stone.'),                     # E021
    (1350.0, '1348', 'The Black Death', 'Paris loses a large share of its people (estimates vary).'),             # D005
    (1370.0, '1370', 'The Bastille', 'A fortress guards the new eastern gate.'),                                    # E010
    (1383.0, '1383', 'The Charles V wall', 'The Right Bank city doubles behind a new wall.'),                        # B003
    (1413.0, '1413', 'Pont Notre-Dame', 'A bridge lined with houses.'),                                             # G060
    (1490.0, 'c. 1490', 'Back to 200,000', 'The city recovers after the Hundred Years War (estimate).'),          # D007
    (1533.0, '1533', 'A new Hôtel de Ville', 'Work begins on the Renaissance city hall.'),                          # E025
    (1546.0, '1546', 'A Renaissance Louvre', 'The medieval castle starts to become a palace.'),                     # E002
    (1564.0, '1564', 'The Tuileries Palace', "Catherine de' Medici builds a palace west of the Louvre."),          # E019
    (1607.0, '1607', 'Pont Neuf opens', 'The first Paris bridge without houses on it.'),                            # G005
    (1612.0, '1612', 'Place Royale', 'Today Place des Vosges.'),                                                    # C014
    (1640.0, 'c. 1640', '450,000 people', 'Estimate.'),                                                             # D010
    (1655.0, '1614–1655', 'Île Saint-Louis', 'Two islets are joined and built over.'),                              # A001
    (1674.0, '1667–1674', 'The Louvre Colonnade', 'A classical façade facing the city.'),                           # E034
    (1676.0, '1670s', 'The walls come down', 'Old ramparts become the first Grands Boulevards.'),                  # B004, B006
    (1690.0, 'c. 1690', '500,000 Parisians', 'Estimate.'),                                                      # D011
    (1706.0, '1706', 'The Invalides dome is gilded', 'Mansart\'s dome: 107 m.'),                                 # E036
    (1720.0, '1686–1720', 'Place Vendôme', 'A royal square of matching façades.'),                                 # C015
    (1740.0, 'c. 1740', '550,000 Parisians', 'Estimate.'),                                                      # D012
    (1755.0, '1755', 'Place Louis XV', 'Today Place de la Concorde.'),                                          # E014
    (1758.0, '1758', 'Sainte-Geneviève', 'The church that will become the Panthéon.'),                             # E007
    (1786.5, '1786–1788', 'Houses cleared off the bridges', 'Pont Notre-Dame and Pont au Change lose their houses.'),   # G001 (case: [Likely])
    (1790.0, '1784–1790', 'The Farmers-General wall', 'A customs wall around the whole city.'),                     # B007
    (1801.0, '1801', '547,756 Parisians', 'First census.'),                                                         # D014
    (1805.0, '1802–1810', 'The Grand Châtelet is demolished', 'The medieval fortress at the heart of the Right Bank.'),   # E037
    (1806.0, '1806', 'Arc de Triomphe', 'Napoleon orders a triumphal arch at the Étoile.'),                         # E005
    (1813.0, '15 Aug 1813', 'Canal de l\'Ourcq', 'Fresh water reaches La Villette.'),                           # A003
    (1825.0, '1822–1825', 'Canal Saint-Martin', 'A canal brings water and barges into Paris.'),                     # A006/A007
    (1836.0, '1836', 'The Arc is finished', 'Thirty years after the first stone.'),                                 # E005
    (1843.0, '1843', 'Île Louviers disappears', 'Its river arm is filled; the island joins the Right Bank.'),    # A002
    (1844.0, '1841–1844', 'The Thiers wall', 'A 33 km fortification around Paris.'),                                # B009
    (1846.0, '1846', 'Over 1 million', '1,053,897 Parisians.'),                                                     # D021
    (1853.0, '1853', 'Haussmann begins', 'Boulevards are cut straight through the old city.'),                      # F004
    (1858.0, '5 Apr 1858', 'Boulevard de Sébastopol', 'Inaugurated through the heart of the Right Bank.'),          # C003
    (1860.0, '1860', '20 arrondissements', 'Paris annexes its suburbs.'),                                           # B011
    (1857.0, '1852–1870', 'Les Halles', 'Baltard\'s iron and glass market pavilions.'),                          # C016
    (1863.0, '1852–1863', 'The New Louvre', 'The Louvre finally joins the Tuileries.'),                             # E038
    (1871.4, 'May 1871', 'The Commune', 'The Tuileries and the Hôtel de Ville are set on fire.'),                   # F005, E020
    (1875.0, '1875', 'Palais Garnier', 'The opera house opens.'),                                                   # E009
    (1882.0, '1882', 'A new Hôtel de Ville', 'Rebuilt on the same site.'),                                          # E027
    (1883.0, '1883', 'Tuileries demolished', 'The burnt palace is cleared away.'),                                  # E020
    (1889.3, '6 May 1889', 'Eiffel Tower opens', '300 m: the tallest structure in the world.'),                     # E004
    (1900.0, '1900', 'World Fair and the first Métro line', 'Grand Palais, Pont Alexandre III, Line 1.'),          # F006, F003, E018, G012
    (1896.0, '1896–1900', 'Pont Alexandre III', 'A single steel arch over the Seine.'),                          # G012
    (1910.0, 'Jan 1910', 'The great flood', 'The Seine rises more than 8 m.'),                                      # F007
    (1914.0, '1914', 'Sacré-Cœur completed', 'Consecrated only in 1919, after the war.'),                           # E008
    (1921.0, '1921', '2.9 million Parisians', 'The all-time peak.'),                                                # D035
    (1929.0, '1919–1929', 'The Thiers wall is razed', 'Its belt becomes housing and, later, the Périphérique.'),    # B010
    (1931.0, '1931', '2,891,020 Parisians', 'Census.'),                                                          # D037
    (1946.0, '1946', '2,725,374 Parisians', 'The first census after the war.'),                               # D039
    (1954.0, '1954', '2,850,189 Parisians', 'Census.'),                                                          # D040
    (1968.0, '1968', '2,590,771 Parisians', 'Families leave for the suburbs.'),                                 # D042
    (1958.0, '1958', 'La Défense', 'A business district rises west of Paris.'),
    (1971.5, '1971–1973', 'Les Halles demolished', 'Baltard\'s pavilions are torn down.'),                       # C017
    (1973.0, '1973', 'Tour Montparnasse', '210 m: a tower Paris will never repeat inside the city.'),               # E016
    (1973.5, '1973', 'Boulevard Périphérique', 'The ring road is completed.'),                                      # B012
    (1977.0, '1977', 'Centre Pompidou', 'Pipes and escalators on the outside.'),                                    # E015
    (1989.0, '1989', 'The Louvre Pyramid', 'And the Grande Arche at La Défense.'),                                  # E017
    (1999.0, '1999', '2,125,246 Parisians', 'The smallest population in a century.'),                         # D046
    (2011.0, '2011', '2,249,975 Parisians', 'A brief rebound.'),                                                  # D048
    (2019.3, '15 Apr 2019', 'Notre-Dame burns', 'The spire and the roof are lost.'),                                # E023
    (2024.9, '7 Dec 2024', 'Notre-Dame reopens', 'The spire is back.'),                                             # E024
    (2025.0, '2025', 'Paris today', '2,065,560 people inside the city.'),                                           # D051
    # 29 ott: capitoli ogni 15-20 s (AGGIORNAMENTI_REGIA): righe ad affidabilita' alta della scheda non ancora usate
    (1630.0, '1566–1643', 'The Fossés Jaunes', 'A new rampart pushes the Right Bank west.'),                       # B005
    (1635.0, '1614–1635', 'Pont Marie', 'Christophe Marie links Île Saint-Louis to the Right Bank.'),               # G007
    (1626.0, '1626', 'Pont au Double', 'The first bridge on the site (1626).'),                                    # G046
    (1791.0, '1787–1791', 'Pont de la Concorde', 'A new bridge to Place Louis XV.'),                               # G011
    (1811.0, '1806–1811', 'The Rohan wing', 'The Louvre grows along the new Rue de Rivoli.'),                      # E035
    (1821.0, '1821', 'Canal Saint-Denis', 'The canal is completed (1821).'),                             # A005
    (1822.0, '1822', 'The Ourcq canal is complete', 'From Mareuil to Paris.'),                                     # A004
    (1827.0, '1825–1827', 'Pont de Grenelle', 'The first bridge on the site opens on 1 May 1827.'),                # G045
    (1828.0, '1828', 'Three new crossings', 'Arcole footbridge and Pont de l\'Archevêché.'),                       # G043, G052
    (1833.0, '29 Jul 1833', 'Pont Louis-Philippe', 'The king lays the first stone.'),                              # G044
    (1834.0, '1831–1834', 'Pont du Carrousel', 'A bridge straight into the Louvre.'),                              # G042
    (1856.0, '1854–1856', 'Pont des Invalides', 'The suspension bridge is replaced in stone.'),                    # G033
    (1859.6, '15 Aug 1859', 'A new spire for Notre-Dame', 'Viollet-le-Duc\'s spire is inaugurated.'),             # E022
    (1860.5, '1856–1860', 'Pont au Change', 'Rebuilt as it stands today.'),                                        # G004
    (1862.0, '1860–1862', 'The canal goes underground', 'Boulevard Richard-Lenoir is built on top.'),              # A013, C019
    (1876.0, '1864–1876', 'Avenue de l\'Opéra', 'Cut straight from the Louvre to the Opéra.'),                    # C006
    (1904.0, '1904', 'Pont de Bercy', 'Widened 5.5 m to carry the Métro.'),                                        # G024
    (1906.5, '1906', 'Voûte du Temple', 'Another stretch of the canal is covered.'),                               # A014
    (1926.0, '1857–1926', 'Boulevard Haussmann', 'Finished 69 years after it began.'),                             # C007
    (1939.0, '1935–1939', 'A new Pont du Carrousel', 'The current bridge opens.'),                                 # G032
    (1996.0, '1993–1996', 'Pont Charles-de-Gaulle', 'Built between 1993 and 1996.'),      # G019
    (2006.0, '2006', 'Passerelle Simone-de-Beauvoir', 'Inaugurated in 2006.'),                                     # G020
]

# ---------- attivita' per anno ----------
B = json.load(open(f'{DATA}/buildings.json')); H = json.load(open(f'{DATA}/hist.json'))
act = np.zeros(2030)
for o in B: act[min(2029, max(0, int(o['y'])))] += 1
for o in H:
    act[min(2029, max(0, int(o['y'])))] += 1
    if o.get('d', 9999) < 2027: act[int(o['d'])] += 0.6
act = np.convolve(act, np.ones(5) / 5, 'same')
RMIN, RMAX = 0.5, 8.0
RMAX_OLD, OLD_END = 12.0, 1840   # prima del 1840 (citta' chiusa nelle mura) fino a 12 anni/s
FASTS = [(1890, 1960, 1.2), (1975, 2030, 1.0)]   # il Novecento e gli ultimi decenni non devono trascinarsi

def spread(pieces, T):
    """tempo T sui pezzi di anni, in proporzione all'attivita' con 1/RMAX <= s/anno <= 1/RMIN"""
    yrs, own = [], []
    for i, (p0, p1) in enumerate(pieces):
        for y in np.arange(math.floor(p0), math.ceil(p1)):
            fr_ = min(p1, y + 1) - max(p0, y)
            if fr_ > 1e-6: yrs.append((int(y), fr_)); own.append(i)
    w = np.array([(act[y] + 3.0) ** 0.85 * f for y, f in yrs]); fr = np.array([f for _, f in yrs])
    rmx = np.array([16.0 if y < 1500 else (RMAX_OLD if y < OLD_END else RMAX) for y, _ in yrs]); rmn = np.array([next((f_[2] for f_ in FASTS if f_[0] <= y < f_[1]), RMIN) for y, _ in yrs]); lo, hi = fr / rmx, fr / rmn; sv = np.clip(w / w.sum() * T, lo, hi)
    for _ in range(80):
        err = T - sv.sum()
        if abs(err) < 1e-6: break
        free = (sv < hi - 1e-9) if err > 0 else (sv > lo + 1e-9)
        if not free.any(): break
        sv[free] += err * w[free] / w[free].sum(); sv = np.clip(sv, lo, hi)
    if abs(T - sv.sum()) > 0.05: print(f'  [!] limiti impossibili: scala {T / sv.sum():.2f}'); sv *= T / sv.sum()
    out = [[] for _ in pieces]; acc = [0.0] * len(pieces)
    for (y, f), o, s in zip(yrs, own, sv):
        acc[o] += s; out[o].append((min(pieces[o][1], y + 1), acc[o]))
    return out, acc

def campos(tg, alt, el, az):   # camera a quota alt sopra il suolo, sguardo inclinato di el gradi, da azimut az
    d = (alt + ground(tg[0], tg[1]) - tg[2]) / math.tan(math.radians(el))
    a = math.radians(az); return [tg[0] + d * math.sin(a), tg[1] + d * math.cos(a), alt + ground(tg[0], tg[1])]
def stop_cams(s):   # posizione della camera all'arrivo e all'uscita di una sosta
    tg, alt, a0, a1 = s[4], s[5], s[6], s[7]; el = s[8] if len(s) > 8 else (24 if alt < 600 else 26)
    return np.array(campos(tg, alt * 1.12, el + 2, a0)), np.array(campos(tg, alt * 1.05, el, a1))
VMAX = 115.0   # m/s tra due soste: tempo minimo del trasferimento (prima 400-740 m/s tra soste vicine nel tempo)
YEARS = []; SOSTA_T = []
for (ta, ya), (tb, yb) in zip(FIXED, FIXED[1:]):
    if yb <= ya:   # riavvolgimento o pausa
        for k in range(21):
            u = k / 20; YEARS.append((ta + (tb - ta) * u, ya + (yb - ya) * u * u * (3 - 2 * u)))
        continue
    ss = [s for s in SOSTE if ya <= s[0] < yb]
    pieces = []; cur = ya
    for s in ss: pieces.append((cur, s[0])); cur = s[1]
    pieces.append((cur, yb))
    pts, Ts = spread([p for p in pieces], (tb - ta) - sum(s[2] for s in ss))
    need = [0.0] + [float(np.linalg.norm(stop_cams(ss[i - 1])[1] - stop_cams(ss[i])[0])) / VMAX + 1.0 for i in range(1, len(ss))] + [0.0]
    Ts = list(Ts); Tall = sum(Ts)
    for _ in range(10):   # i trasferimenti troppo corti si allungano, gli altri pezzi si accorciano in proporzione
        fix = [i for i in range(len(Ts)) if Ts[i] < need[i] - 1e-6]
        if not fix: break
        for i in fix: Ts[i] = need[i]
        free_ = [i for i in range(len(Ts)) if Ts[i] > need[i] + 1e-6]
        k_ = (Tall - sum(Ts[i] for i in range(len(Ts)) if i not in free_)) / sum(Ts[i] for i in free_)
        for i in free_: Ts[i] *= k_
    old_ = [pts[i][-1][1] if pts[i] else 0.0 for i in range(len(pts))]
    pts = [[(yv, dt * (Ts[i] / old_[i] if old_[i] > 0 else 1.0)) for yv, dt in pts[i]] for i in range(len(pts))]
    t = ta
    for i, (p0, p1) in enumerate(pieces):
        YEARS.append((t, p0))
        for yv, dt in pts[i]: YEARS.append((t + dt, yv))
        t += Ts[i]
        if i < len(ss):
            s = ss[i]; SOSTA_T.append((t, t + s[2], s))
            for k in range(1, 11):
                u = k / 10; YEARS.append((t + s[2] * u, s[0] + (s[1] - s[0]) * u))
            t += s[2]
YEARS.append((DUR, 2026.0))
YEARS = sorted({round(float(t), 3): (round(float(t), 3), round(float(y), 4)) for t, y in YEARS}.values())
def year_at(t):
    if t <= YEARS[0][0]: return YEARS[0][1]
    for (a, ya), (b, yb) in zip(YEARS, YEARS[1:]):
        if t <= b: return ya + (yb - ya) * (t - a) / max(1e-9, b - a)
    return YEARS[-1][1]
def t_of_year(y):
    for (a, ya), (b, yb) in zip(YEARS, YEARS[1:]):
        if a >= 9.5 and ya <= y <= yb and yb > ya: return a + (b - a) * (y - ya) / (yb - ya)
    return None

# ---------- estensione della citta' per anno (vista larga) ----------
cx = np.array([sum(p[0] for p in o['r']) / len(o['r']) for o in B + H]); cy = np.array([sum(p[1] for p in o['r']) / len(o['r']) for o in B + H])
by = np.array([o['y'] for o in B + H]); bd = np.array([o.get('d', 9999) for o in B + H])
def extent(y):
    m = (by <= y) & (bd > y)
    mx, my = np.median(cx[m]), np.median(cy[m]); r = np.percentile(np.hypot(cx[m] - mx, cy[m] - my), 80)
    return (float(mx), float(my)), float(r)

# ---------- punti di passaggio della camera (t, posizione, bersaglio) ----------
WP = []
# apertura: Parigi di oggi da 1.000 m a sud-ovest sopra la Senna (Eiffel e centro nello stesso quadro); nel riavvolgimento
# scende verso l'Ile de la Cite del 1190
WP.append((0.0, campos((-1200, 600, 0), 560, 20, 228), (-1200, 600, 0)))   # 30 ott: apertura piu' bassa e vicina (da 1.000 m la citta' sembrava piatta)
WP.append((3.0, campos((-900, 450, 0), 560, 21, 230), (-900, 450, 0)))
WP.append((9.0, campos((ND[0] - 150, ND[1] + 200, 20), 470, 16, 236), (ND[0] - 150, ND[1] + 200, 20)))
for t0, t1, s in SOSTA_T:
    tg, alt, a0, a1 = s[4], s[5], s[6], s[7]
    el = s[8] if len(s) > 8 else (24 if alt < 600 else 26)
    WP.append((t0, campos(tg, alt * 1.12, el + 2, a0), list(tg)))          # arrivo poco piu' alto, poi scende piano
    WP.append(((t0 + t1) / 2, campos(tg, alt, el, (a0 + a1) / 2), list(tg)))
    WP.append((t1, campos(tg, alt * 1.05, el, a1), list(tg)))
# tratti larghi tra le soste: la citta' di quell'anno, da 750-1.000 m, deriva lenta
ws = sorted([w[0] for w in WP])
gaps = [(a, b) for a, b in zip([9.0] + [s[1] for s in SOSTA_T], [s[0] for s in SOSTA_T] + [NIGHT_T]) if b - a > 12.0]
for k, (a, b) in enumerate(gaps):
    n = max(1, int((b - a) // 14))
    for j in range(n):
        tm = a + (b - a) * (j + 0.5) / n; (mx, my), r = extent(year_at(tm))
        nxt = next((s_ for s_ in SOSTA_T if s_[0] >= b - 1e-6), None)      # la vista larga scivola verso la sosta successiva
        u_ = (j + 0.5) / n * 0.6
        ntg = nxt[2][4] if nxt else (-1000, 600, 0)
        tg = ((mx - 120) * (1 - u_) + ntg[0] * u_, my * (1 - u_) + ntg[1] * u_, 0)
        alt = float(np.clip(450 + 0.32 * r, 600, 760 if 150 < tm < 285 else 1000));   # 2:30-4:45: mai a lungo sopra 800 m (Fabio)
        az = (nxt[2][6] if nxt else 220) + (8 if (k + j) % 2 else -8)
        cw = np.array(campos(tg, alt, 21 if alt > 850 else 24, az))
        # la camera larga sta tra l'uscita della sosta precedente e l'arrivo della successiva (niente deviazioni di km
        # in pochi secondi: con la sola vista larga la camera arrivava a 400+ m/s)
        f_ = (j + 0.5) / n
        pc = np.array(max([w for w in WP if w[0] <= a + 1e-6], key=lambda w: w[0])[1])
        nc = np.array(min([w for w in WP if w[0] >= b - 1e-6], key=lambda w: w[0])[1]) if nxt else cw
        cw = cw * 0.3 + pc * 0.7 * (1 - f_) + nc * 0.7 * f_
        WP.append((tm, cw.tolist(), list(tg)))
# notte: dalla Senna verso la Tour Eiffel e il centro illuminati, poi sale e si allontana
WP.append((NIGHT_T, campos((ND[0] - 200, ND[1] + 150, 20), 520, 20, 230), [ND[0] - 200, ND[1] + 150, 20]))
WP.append((NIGHT_T + 18, campos((EIFFEL[0] + 300, EIFFEL[1] + 200, 80), 560, 18, 220), [EIFFEL[0] + 300, EIFFEL[1] + 200, 80]))
WP.append((NIGHT_T + 30, campos((-1800, 700, 0), 760, 19, 214), [-1800, 700, 0]))
WP.append((DUR, campos((-600, 500, 0), 680, 22, 210), [-600, 500, 0]))   # finale notturno piu' basso
WP.sort(key=lambda w: w[0])
# punti troppo vicini nel tempo (< 1,2 s): si tiene il primo
clean = []
for w in WP:
    if clean and w[0] - clean[-1][0] < 1.2: continue
    clean.append(w)
WP = clean
T = np.array([w[0] for w in WP]); P = np.array([w[1] for w in WP]); G = np.array([w[2] for w in WP])
fp, fg = PchipInterpolator(T, P, axis=0), PchipInterpolator(T, G, axis=0)   # PCHIP: niente rimbalzi sotto la quota minima
cam = []; alts = []
for tt in np.arange(0.0, DUR + 1e-6, 0.25):
    p = fp(tt).tolist(); g = fg(tt).tolist()
    gm = max(ground(p[0], p[1]), ground_max(p[0], p[1]) - 60)
    p[2] = float(np.clip(p[2], gm + 300, gm + 1000))                       # regola di Fabio: 300-1.000 m sopra il suolo
    alts.append(p[2] - ground(p[0], p[1]))
    cam.append([round(float(tt), 3), [round(v, 1) for v in p], [round(v, 1) for v in g], LENS])

# ---------- movimento camera (stesso indice delle SPEC: >= 12) ----------
cp = np.array([c[1] for c in cam]); cg = np.array([c[2] for c in cam]); dt = 0.25
vel = np.linalg.norm(np.diff(cp, axis=0), axis=1) / dt
dirs = (cg - cp) / np.linalg.norm(cg - cp, axis=1)[:, None]
ang = np.degrees(np.arccos(np.clip((dirs[1:] * dirs[:-1]).sum(1), -1, 1))) / dt
MOVE = float(np.median(ang) * 4 + np.median(vel) / 25)

sched = {'_doc': 'Siviglia, regia automatica (regia_parigi.py): un piano sequenza, 35 mm, camera 300-1.000 m sopra il suolo.',
         'duration': DUR, 'lens': LENS, 'years': [[t, y] for t, y in YEARS], 'cam': cam, 'night_t': NIGHT_T,
         'soste': [[round(t0, 2), round(t1, 2), s[0], s[1], s[3]] for t0, t1, s in SOSTA_T]}
json.dump(sched, open('schedule_parigi.json', 'w'))
json.dump(dict(sched, years=[[0, 2026], [DUR, 2026]]), open('schedule_parigi_night.json', 'w'))
soste_ev = [{'t_in': round(t0, 2), 't_out': round(t1, 2), 'title': s[3], 'sub': STOP_SUB.get(s[3], '')} for t0, t1, s in SOSTA_T]
# didascalie: una ogni 10-15 s, almeno 4 s a schermo; si sceglie nel pool la piu' vicina al suo anno, spostandola al massimo 6 s
pool = sorted([(t_of_year(y), d, ti, li) for y, d, ti, li in CAPS if t_of_year(y) is not None and t_of_year(y) < DUR - 6])
def rate_at(t): return abs(year_at(t + 0.5) - year_at(t - 0.5))
def maxlag(t): return 2.0 if rate_at(t) > 3.0 else 8.0
caps = []; last = 10.5 - 10.0
used = set()
while True:
    lo_, hi_ = last + 10.0, last + 15.0
    cand = [c for c in pool if c[2] not in used and lo_ - maxlag(c[0]) <= c[0] <= hi_]
    if not cand:
        nxt_ = [c for c in pool if c[2] not in used and c[0] > hi_]
        if not nxt_: break
        cand = [nxt_[0]]
    c = min(cand, key=lambda c: abs(max(c[0], lo_) - (lo_ + 2.0)))
    t_ = max(c[0], lo_ if caps else 10.5); used.add(c[2])
    caps.append({'t_in': round(t_, 2), 'date': c[1], 'title': c[2], 'line': c[3], 'shift_s': round(t_ - c[0], 1), 'rate': round(rate_at(c[0]), 1)})
    last = t_
for t_, d_, ti_, li_ in CAPS_NIGHT:   # notte: anno fermo, una ogni 10-15 s dopo l'ultima
    t_ = min(max(t_, caps[-1]['t_in'] + 10.0), caps[-1]['t_in'] + 13.0)
    if t_ < DUR - 6: caps.append({'t_in': round(t_, 2), 'date': d_, 'title': ti_, 'line': li_, 'shift_s': 0.0, 'rate': 0.0})
for i, c in enumerate(caps):
    c['t_out'] = round(min(caps[i + 1]['t_in'] - 0.5 if i + 1 < len(caps) else DUR, c['t_in'] + 8.0), 2)
ev = {'soste': soste_ev, 'didascalie': caps, 'subscribe_t': SUBSCRIBE_T}
json.dump(ev, open('eventi_parigi.json', 'w'), ensure_ascii=False, indent=0)
gaps_ = np.diff([c['t_in'] for c in caps]); dur_ = [c['t_out'] - c['t_in'] for c in caps]

# ---------- controllo ----------
ts = np.arange(0, DUR, 0.25); yv = np.array([year_at(t) for t in ts]); rate = np.gradient(yv, ts)
lines = [f'Durata {int(DUR // 60)}:{DUR % 60:04.1f}  fotogrammi {NFR}  piano sequenza (0 stacchi)  obiettivo {LENS} mm  punti camera {len(WP)}',
         f'Quota camera sopra il suolo: min {min(alts):.0f} m, max {max(alts):.0f} m, mediana {np.median(alts):.0f} m',
         f'Velocita camera: mediana {np.median(vel):.0f} m/s, max {vel.max():.0f} m/s; rotazione sguardo mediana {np.median(ang):.1f} gradi/s',
         f'Prima crescita (anno 1215 raggiunto): {t_of_year(1215):.1f} s; 1550 (citta densa): {t_of_year(1550):.1f} s', '', 'SOSTE (video -> anni):']
for t0, t1, s in SOSTA_T: lines.append(f'  {int(t0 // 60)}:{t0 % 60:04.1f}-{int(t1 // 60)}:{t1 % 60:04.1f}  {s[0]:.0f}->{s[1]:.0f}  {s[3]}')
lines += ['', f'DIDASCALIE: {len(caps)}, distanza {gaps_.min():.1f}-{gaps_.max():.1f} s, a schermo {min(dur_):.1f}-{max(dur_):.1f} s, spostamento max {max(c["shift_s"] for c in caps):.1f} s; Subscribe a {SUBSCRIBE_T:.0f} s']
lines += [f'  {int(c["t_in"] // 60)}:{c["t_in"] % 60:04.1f}  {c["date"]:<12} {c["title"]}' for c in caps]
hi8 = [(t, a_) for t, a_ in zip(np.arange(len(alts)) * 0.25, alts) if 150 <= t <= 285]
run_, best_ = 0.0, 0.0
for t, a_ in hi8:
    run_ = run_ + 0.25 if a_ > 800 else 0.0; best_ = max(best_, run_)
lines += ['', f'2:30-4:45: tratto piu lungo sopra 800 m = {best_:.1f} s (limite 20 s)']
lines += ['', 'ANNO OGNI 20 s:'] + [f'  {int(t // 60)}:{int(t % 60):02d}  {year_at(t):7.1f}  ({abs(rate[int(t * 4)]):.2f} anni/s)' for t in range(0, int(DUR), 20)]
fr = abs(rate[(ts > 12) & (ts < NIGHT_T)])
lines += ['', f'Velocita del tempo fuori dalle soste: mediana {np.median(fr):.2f} anni/s, max {fr.max():.1f} anni/s']
# capitoli YouTube (descrizione): uno ogni 15-20 s, scelti tra i cartelli; preferiti quelli con un numero (fatto verificabile)
import re as _re
def _lab(c): return c['title'] if not c['date'] or c['date'] in c['title'] else f"{c['date']} – {c['title']}"
# soste sempre capitoli (i momenti forti), poi si riempiono i buchi > 20 s con i cartelli (preferiti quelli con numeri),
# distanza minima 12,5 s (YouTube vuole >= 10 s)
chap = [(0.0, 'Paris today')] + [(e_['t_in'], e_['title']) for e_ in soste_ev] + [(NIGHT_T, 'Paris by night')]
_pool = [c for c in caps if c['t_in'] < NIGHT_T - 12.5]; _dead = set()
for _ in range(200):
    chap.sort(); gaps = [(chap[k + 1][0] - chap[k][0], k) for k in range(len(chap) - 1) if round(chap[k][0], 2) not in _dead]
    if not gaps: break
    g, k = max(gaps)
    if g <= 20.0: break
    a_, b_ = chap[k][0] + 10.5, chap[k + 1][0] - 10.5
    cand = [c for c in _pool if a_ <= c['t_in'] <= b_]
    if not cand: _dead.add(round(chap[k][0], 2)); continue   # buco senza cartelli possibili: resta
    mid = (chap[k][0] + chap[k + 1][0]) / 2 if g < 40 else chap[k][0] + 16.0
    c = max(cand, key=lambda c: (bool(_re.search(r'\d', c['title'] + c['line'])), -abs(c['t_in'] - mid)))
    chap.append((c['t_in'], _lab(c))); _pool.remove(c)
chap = sorted((t_, ti) for t_, ti in chap if ti)

_ct = [f'{int(t // 60)}:{int(t % 60):02d} {ti}' for t, ti in chap]
open('capitoli_parigi.txt', 'w').write('\n'.join(_ct) + '\n')
lines += ['', f'CAPITOLI ({len(chap)}, intervallo medio {np.mean(np.diff([t for t, _ in chap])):.1f} s, massimo {max(np.diff([t for t, _ in chap])):.1f} s):'] + ['  ' + x for x in _ct]
open('regia_parigi.txt', 'w').write('\n'.join(lines)); print('\n'.join(lines))
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 8), dpi=80, sharex=True)
    ax1.plot(ts / 60, yv, color='#1f6f8b', lw=2); ax1.set_ylabel('anno'); ax1.grid(alpha=0.3)
    ax2.plot(ts / 60, np.clip(abs(rate), 0, 12), color='#c0392b', lw=1.5); ax2.set_ylabel('anni/s'); ax2.grid(alpha=0.3)
    ax3.plot(np.arange(len(alts)) * 0.25 / 60, alts, color='#555', lw=1.5); ax3.set_ylabel('quota camera m'); ax3.axhline(300, ls='--', c='grey'); ax3.axhline(1000, ls='--', c='grey'); ax3.set_xlabel('minuti'); ax3.grid(alpha=0.3)
    for t0, t1, s in SOSTA_T:
        for ax in (ax1, ax2, ax3): ax.axvspan(t0 / 60, t1 / 60, color='#27ae60', alpha=0.25)
        ax1.text(t0 / 60, year_at(t0) + 20, s[3].split('(')[0][:24], fontsize=7, rotation=50)
    for ax in (ax1, ax2, ax3): ax.axvspan(NIGHT_T / 60, DUR / 60, color='#2c3e50', alpha=0.2)
    ax1.set_title('Parigi: anni nel video (verde = soste, scuro = notte) e quota della camera')
    plt.tight_layout(); plt.savefig('regia_parigi.png')
except Exception as e: print('grafico non fatto:', e)
