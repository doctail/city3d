# Monumenti, mura e campanili di Parigi modellati a fasi per build_render.py -> DATA/landmarks.json
# Formato come landmarks_copenhagen.py: {"parts": [...], "clear": [anelli], "labels": [...], "fires": [...]}
# Parti: prism {r,z0,z1} · hip {r,z0,z1,rh} · cyl {cx,cy,rad,z0,z1,seg} · cone {cx,cy,r0,r1,z0,z1,seg} · dome {cx,cy,rad,z0,hz} · beam {p0,p1,w,h}
# Ogni parte: "y" = anno in cui compare (cresce dalla base), "d" = anno in cui sparisce. ID della scheda nei commenti:
#   E = monumenti (parigi/validazione), B = mura. Righe DA MEMORIA mai BRUSCO (regola 5): fasi graduali o eventi come cartelli.
# Fonti dati: ALPAGE (Enceintes, Tours_portes, Eglises, Bastille: date DD/DF dei ricercatori), impronte OSM per i monumenti di oggi.
# Misure [Likely]: altezze note dei monumenti (Notre-Dame torri 69 m, guglia 96 m; Invalides 107 m; Pantheon 83 m; Sacre-Coeur 83 m;
#   Arc de Triomphe 50 x 45 x 22 m; Tour Eiffel 300 m + asta = 312 m nel 1889). Forme semplificate ma riconoscibili da 300-1000 m.
# Uso: python landmarks_parigi.py RAW_DIR DATA_DIR
import json, math, os, random, sys, gzip, re
import numpy as np, geopandas as gpd, shapely
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
import shapely.ops
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from tools.alpage import Alpage

RAW, DATA = sys.argv[1], sys.argv[2]
CFG = json.load(open(os.path.join(HERE, 'city_parigi.json')))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def L(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def loc(g): return shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY])
def log(*a): print('[landmarks_parigi]', *a, flush=True)
rnd = random.Random(21)

STONE, STONE2, SLATE, ZINC, COPPER, GOLD, LEAD, BRONZE, WHITE, GLASS, BRICK = \
    '#d9cdb2', '#cbbd9e', '#59606b', '#7d8590', '#6f9c8a', '#c9a24a', '#6c7178', '#6b5a43', '#efece4', '#7fa3bf', '#a5604a'
WALLC, WALLC2 = '#bfb094', '#a99a7e'
parts, clear, labels, fires = [], [], [], []
def P(**k):
    if k.get('t') == 'beam' and 'cx' not in k: k['cx'] = (k['p0'][0] + k['p1'][0]) / 2; k['cy'] = (k['p0'][1] + k['p1'][1]) / 2
    k = {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in k.items()}
    parts.append(k)
def ring(g, simp=0.4):
    g = g.simplify(simp)
    if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda q: q.area)
    return [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
def lab(name, x, y, z, y_from, y_to=9999): labels.append({'name': name, 'x': round(x, 1), 'y': round(y, 1), 'z': z, 'from': y_from, 'to': y_to})
def clear_poly(g):   # pezzi convessi (rispetta i cortili interni: le case storiche dei cortili non spariscono)
    for t in shapely.constrained_delaunay_triangles(g.buffer(0)).geoms:
        if t.area > 1: clear.append([[round(x, 2), round(y, 2)] for x, y in list(t.exterior.coords)[:-1]])
def frame(g):
    """asse lungo dell'impronta: centro, versore u (asse lungo), lunghezza, larghezza"""
    m = g.minimum_rotated_rectangle; c = list(m.exterior.coords)[:4]
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    if math.hypot(*e1) < math.hypot(*e2): e1, e2 = e2, e1
    Ln, Wd = math.hypot(*e1), math.hypot(*e2)
    return (m.centroid.x, m.centroid.y), (e1[0] / Ln, e1[1] / Ln), Ln, Wd
def at(c, u, s, t):   # punto a distanza s lungo u e t di traverso
    return (c[0] + u[0] * s - u[1] * t, c[1] + u[1] * s + u[0] * t)
def rect(c, u, s0, s1, t0, t1): return [list(at(c, u, s0, t0)), list(at(c, u, s1, t0)), list(at(c, u, s1, t1)), list(at(c, u, s0, t1))]
def gradual(n, y0, y1):   # n anni crescenti tra y0 e y1
    return [y0 + (y1 - y0) * (i + 0.5) / n for i in range(n)]

# ---------- impronte OSM per nome ----------
b = gpd.read_file(gzip.open(f'{RAW}/osm_buildings.geojson.gz'))
b = b[b['name'].notna()].copy(); b['geometry'] = [loc(g) for g in b.geometry]
def fp(name, near=None, maxd=400):
    s = b[b['name'] == name]
    if near is not None: s = s[[g.centroid.distance(Point(near)) < maxd for g in s.geometry]]
    if not len(s): log('MANCA impronta:', name); return None
    g = max(s.geometry, key=lambda q: q.area)
    if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
    return g.buffer(0)
A = Alpage(os.path.join(RAW, 'alpage'), CFG)

# =====================================================================================================
# 1. MURA (ALPAGE Enceintes + Tours_portes; scheda B)
# =====================================================================================================
enc = A.layer('Enceintes')
WALLS = {   # (altezza, colore, costruzione da-a, demolizione da-a, id scheda)
    'Philippe-Auguste': (8.0, WALLC, (1190, 1215), None, 'B001/B002 costruzione (fonte); B013/B014 smantellamento graduale (memoria)'),
    'Charles-V': (7.0, WALLC2, (1356, 1383), (1670, 1700), 'B003 (fonte); B004 graduale (memoria)'),
    'Fossés jaunes': (6.0, '#9c9474', (1566, 1643), (1670, 1700), 'B005 (fonte); B006 graduale (memoria)'),
    'Fermiers généraux': (3.5, '#d4c9b0', (1784, 1790), (1860, 1861), 'B007 (fonte); B008 memoria -> graduale 1860-1861'),
}
# barriere di Ledoux che restano (Rotonde de la Villette, Trone, Enfer, Monceau)
KEEP_BARR = [L(48.8836, 2.3697), L(48.8484, 2.3958), L(48.8339, 2.3324), L(48.8797, 2.3091)]
nwall = 0
for g, lib in zip(enc.geometry.values, enc['Libelle'].astype(str)):
    if lib not in WALLS: continue
    hgt, col, (c0, c1), dem, src = WALLS[lib]
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        if q.geom_type != 'Polygon' or q.area < 20: continue
        # le cinte con fossato (Charles V, Fosses jaunes) sono fasce larghe: si disegna il terrapieno basso + il muro sul bordo interno
        pieces = [q]
        if q.area > 20000:   # fascia larga: a pezzi lungo il bordo (ognuno con il suo anno: costruzione e demolizione graduali)
            bnd = q.exterior; n_ = max(2, int(bnd.length / 120))
            pieces = []
            for i in range(n_):
                seg = shapely.ops.substring(bnd, bnd.length * i / n_, bnd.length * (i + 1) / n_)
                pc = seg.buffer(14, cap_style=2).intersection(q)
                if not pc.is_empty and pc.area > 30: pieces.append(pc)
        elif q.length > 300 and q.area < 20000:   # cinta stretta e lunga (Filippo Augusto): tratti di ~100 m
            mrr_c, u_, Ln, Wd = frame(q); n_ = max(1, int(Ln / 100))
            pieces = [q.intersection(Polygon(rect(mrr_c, u_, -Ln / 2 + Ln * i / n_ - 1, -Ln / 2 + Ln * (i + 1) / n_ + 1, -Wd, Wd))) for i in range(n_)] if Ln > 2 * Wd else [q]
        for pc in pieces:
            for pp in (pc.geoms if hasattr(pc, 'geoms') else [pc]):
                if pp.geom_type != 'Polygon' or pp.area < 15: continue
                cx_, cy_ = pp.centroid.x, pp.centroid.y
                y_ = c0 + (c1 - c0) * rnd.random()
                if lib == 'Philippe-Auguste':
                    rg = cy_ < -100                                  # riva sinistra: B002 fino al 1215 e smantellamento fino al 1800 (B014)
                    y_ = 1190 + ((1215 if rg else 1210) - 1190) * rnd.random()
                    d_ = rnd.uniform(1500, 1800 if rg else 1700)
                elif lib == 'Fermiers généraux':
                    keep = any(math.hypot(cx_ - kx, cy_ - ky) < 60 for kx, ky in KEEP_BARR)
                    d_ = 9999 if keep else rnd.uniform(1860, 1861)
                    if pp.area > 250: hgt_b = 11.0 if not keep else 14.0   # padiglioni delle barriere (Ledoux)
                else:
                    d_ = rnd.uniform(*dem)
                h_ = (hgt_b if lib == 'Fermiers généraux' and pp.area > 250 else hgt)
                P(name=f'wall_{lib[:8]}', t='prism', r=ring(pp, 0.6), z0=0.0, z1=h_, c=col, a=0.05, y=round(y_, 1), d=round(d_, 1))
                nwall += 1
log('mura: pezzi', nwall)
# torri e porte (Tours_portes): DD1 costruzione, DF1 demolizione (ALPAGE)
tp = A.layer('Tours_portes'); ntp = 0
for g, enc_, fct, dd, df in zip(tp.geometry.values, tp['enceinte'].astype(str), tp['fonction'].astype(str), tp['DD1'], tp['DF1']):
    if g is None or g.geom_type != 'Point': continue
    dd = float(dd) if dd == dd and dd else (1190 if 'Philippe' in enc_ else 1356)
    df = float(df) if df == df and df else 1700
    if 'BAS EMPIRE' in enc_: continue
    porte = 'orte' in fct
    rad = 7.0 if porte else 4.5; h = 18.0 if porte else 14.0
    if 'Charles' in enc_: rad += 1; h += 2
    P(name='tower', t='cyl', cx=g.x, cy=g.y, rad=rad, z0=0.0, z1=h, seg=10, c=WALLC, a=0.05, y=dd, d=df)
    P(name='tower_roof', t='cone', cx=g.x, cy=g.y, r0=rad + 0.6, r1=0.3, z0=h, z1=h + rad * 1.4, seg=10, c=SLATE, a=0.05, y=dd + 1, d=df)
    ntp += 1
log('torri e porte:', ntp)
# Cinta di Thiers (B009 costruzione 1841-1844, B010 demolizione 1919-1929, fonte): non e' in ALPAGE. Tracciato [Likely]:
# il muro correva ~70 m fuori dai Boulevards des Marechaux (la strada militare interna). Muro 10 m + fossato.
MAR = re.compile(r'^Boulevard (Mass[ée]na|Kellermann|Jourdan|Brune|Lefebvre|Victor|Murat|Suchet|Lannes|Gouvion-Saint-Cyr|Berthier|Bessi[èe]res|Ney|Macdonald|S[ée]rurier|Mortier|Davout|Soult|Poniatowski|Exelmans|Amiral Bruix|du G[ée]n[ée]ral Martial Valin|du G[ée]n[ée]ral Jean Simon|Ga[ée]tan|de la Somme|d.Indochine|Dode de la Brunerie)')
rr = gpd.read_file(gzip.open(f'{RAW}/osm_roads.geojson.gz')); rr = rr[rr['name'].fillna('').str.match(MAR)].copy()
rr['geometry'] = [loc(g) for g in rr.geometry]
mar = unary_union(list(rr.geometry))
nth = 0
for ln in (mar.geoms if hasattr(mar, 'geoms') else [mar]):
    if ln.length < 40: continue
    cs = list(ln.simplify(5).coords)
    for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
        dl = math.hypot(x1 - x0, y1 - y0)
        if dl < 15: continue
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2; ux, uy = (x1 - x0) / dl, (y1 - y0) / dl
        nx, ny = -uy, ux
        if nx * mx + ny * my < 0: nx, ny = -nx, -ny                  # normale verso l'esterno (lontano dal centro)
        o0, o1 = 65, 80                                              # muro tra 65 e 80 m fuori dal boulevard
        q = [[x0 + nx * o0, y0 + ny * o0], [x1 + nx * o0, y1 + ny * o0], [x1 + nx * o1, y1 + ny * o1], [x0 + nx * o1, y0 + ny * o1]]
        a_ = (math.degrees(math.atan2(my, mx)) + 360) % 360
        P(name='wall_Thiers', t='prism', r=[[round(v, 1) for v in p_] for p_ in q], z0=0.0, z1=10.0, c='#a39a86', a=0.05,
          y=round(1841 + 3 * a_ / 360, 2), d=round(1919 + 10 * ((a_ + 180) % 360) / 360, 2))
        nth += 1
log('cinta di Thiers: tratti', nth)

# =====================================================================================================
# 2. CAMPANILI delle chiese (ALPAGE Eglises: DD1 fondazione, DF1 fine). Notre-Dame e Sainte-Chapelle a parte.
# =====================================================================================================
eg = A.layer('Eglises'); ncamp = 0
SKIP = re.compile(r'Notre[- ]Dame de Paris|Sainte[- ]Chapelle|^Notre Dame$', re.I)
for g, tit, dd, df, st in zip(eg.geometry.values, eg['Titulature'].astype(str), eg['DD1'], eg['DF1'], eg['Statut'].astype(str)):
    if g is None or g.geom_type != 'Point' or SKIP.search(tit): continue
    dd = float(dd) if dd == dd else 0; df = float(df) if df == df else 0
    if dd <= 0: continue
    if df <= dd: df = 9999.0
    par = 'paroiss' in st.lower() or 'abbat' in st.lower() or 'collégiale' in st.lower() or 'collegiale' in st.lower()
    if not par and 'couvent' not in st.lower() and 'chapelle' not in st.lower(): continue
    y0 = max(dd, 1100.0)
    if df < 1190: continue
    h = rnd.uniform(28, 40) if par else rnd.uniform(18, 24); sp = rnd.uniform(14, 24) if par else rnd.uniform(6, 10)
    r_ = 4.5 if par else 3.0
    P(name='belfry', t='prism', r=[[g.x - r_, g.y - r_], [g.x + r_, g.y - r_], [g.x + r_, g.y + r_], [g.x - r_, g.y + r_]], z0=0.0, z1=h, c=STONE2, a=0.05, y=y0, d=df)
    P(name='spire', t='cone', cx=g.x, cy=g.y, r0=r_ * 1.05, r1=0.2, z0=h, z1=h + sp, seg=8, c=SLATE, a=0.05, y=y0 + 2, d=df)
    ncamp += 1
log('campanili:', ncamp)

# =====================================================================================================
# 3. ICONE (scheda E)
# =====================================================================================================
def nave(g, z1, ridge, col, roof, y, d=9999, name='nave'):
    P(name=name, t='prism', r=ring(g), z0=0.0, z1=z1, c=col, a=0.05, y=y, d=d)
    P(name=name + '_roof', t='hip', r=ring(g), z0=z1, z1=z1, rh=ridge - z1, c=roof, a=0.05, y=y + 0.5, d=d)

# --- Notre-Dame (E021 1190-1345 graduale, fonte; E022 guglia 1859; E023 incendio 15 apr 2019; E024 guglia 2023, riapertura 2024) ---
g = fp('Cathédrale Notre-Dame de Paris')
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g)
    if at(c, u, Ln / 2, 0)[0] < at(c, u, -Ln / 2, 0)[0]: u = (-u[0], -u[1])     # u punta a est (abside); la facciata e' a ovest
    # coro (a est) gia' in piedi nel 1190 (consacrato 1182); navata 1190-1230; facciata e torri 1200-1250 (dentro E021)
    choir = g.intersection(Polygon(rect(c, u, 0, Ln, -Wd, Wd)))
    navep = g.intersection(Polygon(rect(c, u, -Ln / 2 + 14, 0, -Wd, Wd)))
    nave(choir, 33.0, 43.0, STONE, LEAD, 1190.0, 2019.29, 'nd_choir')
    for i, yy in enumerate(gradual(3, 1190, 1230)):
        sl = navep.intersection(Polygon(rect(c, u, -(i + 1) * (Ln / 2 - 14) / 3, -i * (Ln / 2 - 14) / 3, -Wd, Wd)))
        if not sl.is_empty: nave(sl, 33.0, 43.0, STONE, LEAD, round(yy, 1), 2019.29, f'nd_nave{i}')
    # tetto ricostruito dopo l'incendio (E024: 2023-2024): stesse forme, piombo nuovo
    P(name='nd_roof_new', t='hip', r=ring(choir), z0=33.0, z1=33.0, rh=10.0, c=LEAD, a=0.05, y=2023.9)
    P(name='nd_roof_new2', t='hip', r=ring(navep), z0=33.0, z1=33.0, rh=10.0, c=LEAD, a=0.05, y=2023.9)
    for sgn in (-1, 1):   # due torri della facciata ovest (69 m)
        tc = at(c, u, -Ln / 2 + 8, sgn * 12)
        sq = [[tc[0] + dx, tc[1] + dy] for dx, dy in ((-8, -8), (8, -8), (8, 8), (-8, 8))]
        sq = [list(at(tc, u, sx, sy)) for sx, sy in ((-8, -7), (8, -7), (8, 7), (-8, 7))]
        P(name='nd_tower_base', t='prism', r=sq, z0=0.0, z1=43.0, c=STONE, a=0.05, y=1215.0)
        P(name='nd_tower_top', t='prism', r=sq, z0=43.0, z1=69.0, c=STONE, a=0.05, y=1240.0 + (5 if sgn > 0 else 0))
    P(name='nd_facade', t='prism', r=[list(at(c, u, s, t)) for s, t in ((-Ln / 2, -20), (-Ln / 2 + 14, -20), (-Ln / 2 + 14, 20), (-Ln / 2, 20))], z0=0.0, z1=46.0, c=STONE, a=0.05, y=1225.0)
    sp = at(c, u, Ln * 0.12, 0)   # guglia sulla crociera: 1859 (E022) -> crollo 15 apr 2019 (E023) -> 2023 (E024)
    P(name='nd_spire', t='cone', cx=sp[0], cy=sp[1], r0=4.0, r1=0.15, z0=43.0, z1=96.0, seg=8, c=LEAD, a=0.05, y=1859.0, d=2019.29)
    P(name='nd_spire_new', t='cone', cx=sp[0], cy=sp[1], r0=4.0, r1=0.15, z0=43.0, z1=96.0, seg=8, c=LEAD, a=0.05, y=2023.92)
    fires.append({'name': 'Notre-Dame fire', 'y': 2019.288, 'y1': 2019.292, 'poly': [list(at(c, u, s, t)) for s, t in ((-20, -12), (Ln / 2 - 5, -12), (Ln / 2 - 5, 12), (-20, 12))], 'flames': 40, 'smoke': 6})
    lab('Notre-Dame', sp[0], sp[1], 96, 1190)

# --- Sainte-Chapelle (E028 1241-1248, memoria: graduale) ---
g = fp('Sainte-Chapelle', near=(-359, 267))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g)
    for i, yy in enumerate(gradual(2, 1241, 1248)):
        sl = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 2, -Ln / 2 + (i + 1) * Ln / 2, -Wd, Wd)))
        if not sl.is_empty: nave(sl, 30.0, 42.0, STONE, SLATE, round(yy, 1), name=f'sc{i}')
    P(name='sc_spire', t='cone', cx=c[0], cy=c[1], r0=2.0, r1=0.1, z0=42.0, z1=75.0, seg=8, c=GOLD, a=0.05, y=1248.0)
    lab('Sainte-Chapelle', c[0], c[1], 75, 1248)

# --- Louvre (E001 forteresse 1190-1202; E002 aile Lescot 1546-1555; E003 Cour Carree 1546-1670 memoria; E033 Grande Galerie 1595-1610;
#     E034 Colonnade 1667-1674 memoria; E035 aile Rohan 1806-1811; E038 Nouveau Louvre 1852-1863; E017 Pyramide 1985-1989 memoria) ---
g = fp('Palais du Louvre', near=(-1031, 890))
if g is not None:
    clear_poly(g)
    # Cour Carree: rettangolo a est (x > -880 circa); la fortezza medievale occupava il quarto sud-ovest della Cour Carree
    cc_box = box(-880, 700, -620, 960)
    cour = g.intersection(cc_box)
    # fortezza (E001): quadrato ~72 x 78 m con donjon centrale; sostituita gradualmente dalla Cour Carree (E002/E003)
    fx, fy = -760, 800
    fort = Polygon([(fx - 36, fy - 39), (fx + 36, fy - 39), (fx + 36, fy + 39), (fx - 36, fy + 39)])
    inner = fort.buffer(-9)
    for i, yy in enumerate(gradual(4, 1190, 1202)):
        sl = fort.difference(inner).intersection(Polygon([(fx, fy), (fx + 200 * math.cos(math.pi / 2 * i), fy + 200 * math.sin(math.pi / 2 * i)),
                                                          (fx + 200 * math.cos(math.pi / 2 * (i + 1)), fy + 200 * math.sin(math.pi / 2 * (i + 1)))]).buffer(0))
        for q in (sl.geoms if hasattr(sl, 'geoms') else [sl]):
            if q.geom_type == 'Polygon' and q.area > 20: P(name='louvre_fort', t='prism', r=ring(q), z0=0.0, z1=14.0, c=WALLC, a=0.05, y=round(yy, 1), d=round(1546 + 100 * i / 4, 1))
    for k, (dx, dy) in enumerate(((-36, -39), (36, -39), (36, 39), (-36, 39))):
        P(name='louvre_fort_t', t='cyl', cx=fx + dx, cy=fy + dy, rad=5.0, z0=0.0, z1=20.0, seg=10, c=WALLC, a=0.05, y=1195.0, d=1546.0 + 30 * k)
    P(name='louvre_donjon', t='cyl', cx=fx, cy=fy, rad=7.5, z0=0.0, z1=31.0, seg=14, c=WALLC, a=0.05, y=1192.0, d=1546.0)   # [Likely] la Grosse Tour sparisce prima del 1546 (1528): resta alla prima ala per la scheda
    P(name='louvre_donjon_r', t='cone', cx=fx, cy=fy, r0=8.2, r1=0.3, z0=31.0, z1=41.0, seg=14, c=SLATE, a=0.05, y=1193.0, d=1546.0)
    # Cour Carree: ala Lescot (ovest) 1546-1555, poi gli altri lati fino al 1670 (memoria: graduale), Colonnade 1667-1674
    sides = [('lescot', box(-880, 700, -840, 960), 1546, 1555), ('sud', box(-880, 700, -620, 740), 1560, 1600),
             ('nord', box(-880, 920, -620, 960), 1600, 1650), ('colonnade', box(-660, 700, -620, 960), 1667, 1674)]
    for nm, bx_, a0, a1 in sides:
        q = cour.intersection(bx_)
        for k, yy in enumerate(gradual(2, a0, a1)):
            qq = q.intersection(bx_.buffer(0) if k == 0 else bx_)
            if qq.is_empty: continue
            nave(qq, 24.0, 33.0, STONE, SLATE, round(yy, 1), name=f'louvre_{nm}')
            break
    # Grande Galerie lungo la Senna (E033 1595-1610): la parte sud a ovest della Cour Carree
    gal = g.intersection(box(-1460, 590, -880, 700)).union(g.intersection(box(-1460, 590, -1300, 760)))
    for i, yy in enumerate(gradual(4, 1595, 1610)):
        q = gal.intersection(box(-880 - (i + 1) * 145, 560, -880 - i * 145, 780))
        if not q.is_empty: nave(q, 22.0, 31.0, STONE, SLATE, round(yy, 1), name=f'louvre_gal{i}')
    # ala nord lungo Rivoli: aile Rohan (E035 1806-1811, parte ovest) e Nouveau Louvre (E038 1852-1863: tutto il resto, cortili Napoleon)
    north = g.difference(cour).difference(gal)
    rohan = north.intersection(box(-1460, 1000, -1250, 1200))
    newl = north.difference(rohan)
    for i, yy in enumerate(gradual(2, 1806, 1811)):
        q = rohan.intersection(box(-1460 + i * 105, 900, -1460 + (i + 1) * 105, 1250))
        if not q.is_empty: nave(q, 22.0, 31.0, STONE, SLATE, round(yy, 1), name=f'louvre_rohan{i}')
    for i, yy in enumerate(gradual(5, 1852, 1863)):
        q = newl.intersection(box(-1460 + i * 170, 600, -1460 + (i + 1) * 170, 1250))
        if not q.is_empty: nave(q, 23.0, 33.0, STONE, SLATE, round(yy, 1), name=f'louvre_new{i}')
    # Pyramide (E017 1985-1989, memoria: graduale)
    gp = fp('Pyramide du Louvre', near=(-1031, 889))
    if gp is not None:
        pc = gp.centroid
        P(name='pyramid', t='cone', cx=pc.x, cy=pc.y, r0=24.5, r1=0.2, z0=0.0, z1=21.6, seg=4, c=GLASS, a=0.5, y=1987.0)
    lab('Louvre', -760, 830, 35, 1190)
    # Tuileries (E019 1564-1860 memoria graduale; E020 incendio 1871 -> demolizione 1883, fonte): tra Pavillon de Flore e de Marsan
    pts_w = [p_ for p_ in g.exterior.coords if p_[0] < -1380]
    if pts_w:
        s_end = min(pts_w, key=lambda p_: p_[1]); n_end = max(pts_w, key=lambda p_: p_[1])
        dx_, dy_ = n_end[0] - s_end[0], n_end[1] - s_end[1]; ln_ = math.hypot(dx_, dy_); ux_, uy_ = dx_ / ln_, dy_ / ln_; nx_, ny_ = uy_, -ux_   # normale verso ovest
        if nx_ > 0: nx_, ny_ = -nx_, -ny_
        for i, yy in enumerate(gradual(5, 1564, 1860)):
            s0, s1 = ln_ * i / 5, ln_ * (i + 1) / 5
            q = [[s_end[0] + ux_ * s0, s_end[1] + uy_ * s0], [s_end[0] + ux_ * s1, s_end[1] + uy_ * s1],
                 [s_end[0] + ux_ * s1 + nx_ * 28, s_end[1] + uy_ * s1 + ny_ * 28], [s_end[0] + ux_ * s0 + nx_ * 28, s_end[1] + uy_ * s0 + ny_ * 28]]
            P(name='tuileries', t='prism', r=q, z0=0.0, z1=24.0, c=STONE, a=0.05, y=round(yy, 1), d=round(1871.4 + 12 * (i + 1) / 6, 1))   # rovine fino alla demolizione (1883)
            P(name='tuileries_roof', t='hip', r=q, z0=24.0, z1=24.0, rh=10.0, c=SLATE, a=0.05, y=round(yy + 1, 1), d=1871.4)          # il tetto brucia nel 1871 (E020)
        mid = (s_end[0] + ux_ * ln_ / 2 + nx_ * 14, s_end[1] + uy_ * ln_ / 2 + ny_ * 14)
        P(name='tuileries_dome', t='prism', r=[[mid[0] - 18, mid[1] - 18], [mid[0] + 18, mid[1] - 18], [mid[0] + 18, mid[1] + 18], [mid[0] - 18, mid[1] + 18]], z0=0.0, z1=34.0, c=STONE, a=0.05, y=1660.0, d=1883.0)
        P(name='tuileries_dome_r', t='cone', cx=mid[0], cy=mid[1], r0=17.0, r1=3.0, z0=34.0, z1=52.0, seg=4, c=SLATE, a=0.05, y=1662.0, d=1871.4)
        fires.append({'name': 'Tuileries fire (Commune)', 'y': 1871.39, 'y1': 1871.40, 'poly': [list(s_end), list(n_end), [n_end[0] + nx_ * 28, n_end[1] + ny_ * 28], [s_end[0] + nx_ * 28, s_end[1] + ny_ * 28]], 'flames': 60, 'smoke': 8})
        lab('Tuileries Palace', mid[0], mid[1], 52, 1564, 1883)

# --- Arc de Triomphe du Carrousel (E030 1806-1809, memoria) ---
g = fp('Arc de Triomphe du Carrousel', near=(-1247, 968))
if g is not None:
    clear_poly(g); P(name='carrousel', t='prism', r=ring(g), z0=0.0, z1=19.0, c='#d6b8a0', a=0.05, y=1807.5)

# --- Hotel de Ville (E025 1533-1628 fonte; E026 incendio 1871 memoria -> cartello + fuoco; E027 ricostruzione 1873-1882 fonte) ---
hdv = None
for gg, nn in zip(b.geometry, b['name']):
    if 'hôtel de ville' in nn.lower() and gg.centroid.distance(Point(L(48.8564, 2.3524))) < 120: hdv = gg.buffer(0); break
if hdv is not None:
    if hdv.geom_type == 'MultiPolygon': hdv = max(hdv.geoms, key=lambda q: q.area)
    clear_poly(hdv); c, u, Ln, Wd = frame(hdv)
    old = hdv.buffer(-12)   # l'edificio rinascimentale era piu' piccolo
    for i, yy in enumerate(gradual(3, 1533, 1628)):
        q = old.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty: nave(q, 20.0, 30.0, STONE, SLATE, round(yy, 1), d=1871.39, name=f'hdv_old{i}')
    P(name='hdv_old_belfry', t='prism', r=rect(c, u, -6, 6, -6, 6), z0=0.0, z1=42.0, c=STONE, a=0.05, y=1610.0, d=1871.39)
    for i, yy in enumerate(gradual(4, 1873, 1882)):
        q = hdv.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 4, -Ln / 2 + (i + 1) * Ln / 4, -Wd, Wd)))
        if not q.is_empty: nave(q, 22.0, 33.0, STONE, SLATE, round(yy, 1), name=f'hdv{i}')
    P(name='hdv_belfry', t='prism', r=rect(c, u, -6, 6, -6, 6), z0=0.0, z1=48.0, c=STONE, a=0.05, y=1882.0)
    fires.append({'name': 'Hotel de Ville fire (Commune)', 'y': 1871.39, 'y1': 1871.40, 'poly': ring(old), 'flames': 45, 'smoke': 6})
    lab('Hôtel de Ville', c[0], c[1], 48, 1533)

# --- Bastille (E010 1370-1383 memoria graduale; E011 demolizione 1789-1790 fonte) da ALPAGE ---
bs = A.layer('Bastille')
for i, (q, dd) in enumerate(zip(bs.geometry.values, bs['DD1'])):
    for qq in (q.geoms if hasattr(q, 'geoms') else [q]):
        if qq.geom_type != 'Polygon' or qq.area < 10: continue
        y_ = 1370 + 13 * (i + 0.5) / len(bs)
        big = qq.area > 1000
        P(name='bastille', t='prism', r=ring(qq), z0=0.0, z1=(8.0 if big else 24.0), c=WALLC2, a=0.05, y=round(y_, 1), d=round(1789.54 + 0.9 * i / len(bs), 2))
bu = unary_union(list(bs.geometry.values)); bc = bu.centroid
if not bu.is_empty:
    core = bu.minimum_rotated_rectangle.buffer(-6)
    cc_ = list(core.exterior.coords)[:4]
    for k in range(8):   # otto torri sul recinto (forma nota)
        a_, b_ = cc_[k // 2], cc_[(k // 2 + 1) % 4]; f_ = 0.0 if k % 2 == 0 else 0.5
        tx, ty = a_[0] + (b_[0] - a_[0]) * f_, a_[1] + (b_[1] - a_[1]) * f_
        P(name='bastille_t', t='cyl', cx=tx, cy=ty, rad=6.0, z0=0.0, z1=24.0, seg=12, c=WALLC2, a=0.05, y=round(1370 + 13 * k / 8, 1), d=round(1789.54 + 0.9 * k / 8, 2))
    lab('Bastille', bc.x, bc.y, 24, 1370, 1790)

# --- Grand Chatelet (E037 demolizione 1802-1810, fonte); esisteva gia' nel 1190 ---
cx_, cy_ = L(48.8577, 2.3473)
P(name='chatelet', t='prism', r=[[cx_ - 30, cy_ - 22], [cx_ + 30, cy_ - 22], [cx_ + 30, cy_ + 22], [cx_ - 30, cy_ + 22]], z0=0.0, z1=18.0, c=WALLC2, a=0.05, y=1130.0, d=1806.0)
for k, (dx, dy) in enumerate(((-30, -22), (30, -22), (30, 22), (-30, 22))):
    P(name='chatelet_t', t='cyl', cx=cx_ + dx, cy=cy_ + dy, rad=6.5, z0=0.0, z1=26.0, seg=12, c=WALLC2, a=0.05, y=1130.0, d=round(1802 + 8 * k / 4, 1))
lab('Grand Châtelet', cx_, cy_, 26, 1190, 1810)

# --- Invalides (E006 complesso 1670-1676; E036 Dome 1677-1706, fonte) ---
g = fp('Hôtel des Invalides', near=(-2731, 326)); gd = fp('Église du Dôme', near=(-2739, 228))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g)
    for i, yy in enumerate(gradual(4, 1670, 1676)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 4, -Ln / 2 + (i + 1) * Ln / 4, -Wd, Wd)))
        if not q.is_empty and gd is not None: q = q.difference(gd.buffer(4))
        if not q.is_empty: nave(q, 18.0, 26.0, STONE, SLATE, round(yy, 1), name=f'inv{i}')
if gd is not None:
    clear_poly(gd); dc = gd.centroid
    nave(gd, 28.0, 30.0, STONE, SLATE, 1680.0, name='dome_body')
    P(name='dome_drum', t='cyl', cx=dc.x, cy=dc.y, rad=15.5, z0=28.0, z1=52.0, seg=24, c=STONE, a=0.05, y=1690.0)
    P(name='dome_cupola', t='dome', cx=dc.x, cy=dc.y, rad=15.5, z0=52.0, hz=22.0, c=GOLD, a=0.05, y=1700.0)
    P(name='dome_lantern', t='cyl', cx=dc.x, cy=dc.y, rad=3.2, z0=74.0, z1=92.0, seg=12, c=GOLD, a=0.05, y=1704.0)
    P(name='dome_spire', t='cone', cx=dc.x, cy=dc.y, r0=1.6, r1=0.1, z0=92.0, z1=107.0, seg=8, c=GOLD, a=0.05, y=1706.0)
    lab('Les Invalides', dc.x, dc.y, 107, 1677)

# --- Pantheon (E007 1758-1791, memoria: graduale) ---
g = fp('Panthéon', near=(-280, -748))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g); pc = g.centroid
    for i, yy in enumerate(gradual(3, 1758, 1775)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty: nave(q, 28.0, 33.0, STONE, SLATE, round(yy, 1), name=f'panth{i}')
    P(name='panth_drum', t='cyl', cx=pc.x, cy=pc.y, rad=17.0, z0=33.0, z1=58.0, seg=24, c=STONE, a=0.05, y=1780.0)
    P(name='panth_dome', t='dome', cx=pc.x, cy=pc.y, rad=15.0, z0=58.0, hz=17.0, c=LEAD, a=0.05, y=1786.0)
    P(name='panth_lantern', t='cyl', cx=pc.x, cy=pc.y, rad=3.0, z0=75.0, z1=83.0, seg=12, c=STONE, a=0.05, y=1790.0)
    lab('Panthéon', pc.x, pc.y, 83, 1758)

# --- Sacre-Coeur (E008 1875-1914, memoria: graduale), pietra bianchissima ---
g = fp('Basilique du Sacré-Cœur', near=(-506, 3737))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g); pc = g.centroid
    for i, yy in enumerate(gradual(3, 1875, 1895)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty: nave(q, 30.0, 36.0, WHITE, WHITE, round(yy, 1), name=f'sc_body{i}')
    P(name='sc_drum', t='cyl', cx=pc.x, cy=pc.y, rad=10.0, z0=36.0, z1=55.0, seg=20, c=WHITE, a=0.05, y=1898.0)
    P(name='sc_dome', t='dome', cx=pc.x, cy=pc.y, rad=10.0, z0=55.0, hz=20.0, c=WHITE, a=0.05, y=1900.0)
    P(name='sc_lantern', t='cyl', cx=pc.x, cy=pc.y, rad=2.4, z0=75.0, z1=83.0, seg=12, c=WHITE, a=0.05, y=1902.0)
    for sgn in (-1, 1):
        dc_ = at(c, u, -Ln * 0.2, sgn * Wd * 0.32)
        P(name='sc_small', t='dome', cx=dc_[0], cy=dc_[1], rad=4.5, z0=36.0, hz=9.0, c=WHITE, a=0.05, y=1900.0)
    cp = at(c, u, Ln / 2 - 6, 0)
    P(name='sc_campanile', t='prism', r=[[cp[0] - 5, cp[1] - 5], [cp[0] + 5, cp[1] - 5], [cp[0] + 5, cp[1] + 5], [cp[0] - 5, cp[1] + 5]], z0=0.0, z1=72.0, c=WHITE, a=0.05, y=1908.0)
    P(name='sc_campanile_top', t='dome', cx=cp[0], cy=cp[1], rad=4.0, z0=72.0, hz=12.0, c=WHITE, a=0.05, y=1912.0)
    lab('Sacré-Cœur', pc.x, pc.y, 83, 1875)

# --- Palais Garnier (E009 1861-1875, fonte) ---
g = fp('Opéra Garnier', near=(-1334, 2105))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g); pc = g.centroid
    for i, yy in enumerate(gradual(3, 1861, 1872)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty: nave(q, 28.0, 32.0, STONE, COPPER, round(yy, 1), name=f'opera{i}')
    dc_ = at(c, u, 0, 0); P(name='opera_dome', t='dome', cx=dc_[0], cy=dc_[1], rad=16.0, z0=32.0, hz=12.0, c=COPPER, a=0.05, y=1873.0)
    # torre scenica (verso nord) con frontone: prisma alto 56 m
    st_ = rect(c, u, Ln * 0.12, Ln * 0.36, -Wd * 0.28, Wd * 0.28)
    P(name='opera_stage', t='prism', r=st_, z0=0.0, z1=45.0, c=STONE, a=0.05, y=1874.0)
    P(name='opera_stage_roof', t='hip', r=st_, z0=45.0, z1=45.0, rh=11.0, c=COPPER, a=0.05, y=1875.0)
    lab('Palais Garnier', dc_[0], dc_[1], 56, 1861)

# --- Arc de Triomphe de l'Etoile (E005 1806-1836, fonte) ---
g = fp('Arc de Triomphe', near=(-4021, 2300))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g)
    hs = [(1806, 1812, 0.0, 12.0), (1812, 1830, 12.0, 32.0), (1830, 1836, 32.0, 50.0)]   # fondazioni, fornici, attico
    for k, (a0, a1, z0, z1) in enumerate(hs):
        P(name=f'arc{k}', t='prism', r=rect(c, u, -Ln / 2, Ln / 2, -Wd / 2, Wd / 2), z0=z0, z1=z1, c='#e3d9c3', a=0.05, y=round((a0 + a1) / 2, 1))
    lab('Arc de Triomphe', c[0], c[1], 50, 1806)

# --- Tour Eiffel (E004 1887-1889, fonte): gambe 1887, primo piano 1888, cima 1889 ---
ex, ey = L(48.85837, 2.29448)
base, legs = 62.0, []
for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
    P(name='eiffel_leg', t='beam', p0=[ex + sx * base, ey + sy * base, 0.0], p1=[ex + sx * 23, ey + sy * 23, 57.6], w=15.0, h=15.0, c=BRONZE, a=0.5, y=1887.3)
    P(name='eiffel_leg2', t='beam', p0=[ex + sx * 23, ey + sy * 23, 57.6], p1=[ex + sx * 12, ey + sy * 12, 115.7], w=9.0, h=9.0, c=BRONZE, a=0.5, y=1888.2)
P(name='eiffel_p1', t='prism', r=[[ex - 33, ey - 33], [ex + 33, ey - 33], [ex + 33, ey + 33], [ex - 33, ey + 33]], z0=53.0, z1=60.0, c=BRONZE, a=0.05, y=1887.9)
P(name='eiffel_p2', t='prism', r=[[ex - 16, ey - 16], [ex + 16, ey - 16], [ex + 16, ey + 16], [ex - 16, ey + 16]], z0=112.0, z1=117.0, c=BRONZE, a=0.05, y=1888.5)
P(name='eiffel_upper', t='cone', cx=ex, cy=ey, r0=15.0, r1=4.5, z0=117.0, z1=270.0, seg=4, c=BRONZE, a=0.5, y=1888.9)
P(name='eiffel_top', t='cone', cx=ex, cy=ey, r0=4.5, r1=2.0, z0=270.0, z1=286.0, seg=4, c=BRONZE, a=0.05, y=1889.1)
P(name='eiffel_mast', t='cyl', cx=ex, cy=ey, rad=0.9, z0=286.0, z1=312.0, seg=6, c=BRONZE, a=0.05, y=1889.2)
lab('Eiffel Tower', ex, ey, 312, 1887)

# --- Grand Palais (E018 1897-1900, memoria: graduale): navata di vetro ---
g = fp('Grand Palais', near=(-2751, 1458))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g)
    for i, yy in enumerate(gradual(3, 1897, 1900)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty:
            P(name=f'gp{i}', t='prism', r=ring(q), z0=0.0, z1=20.0, c=STONE, a=0.05, y=round(yy, 1))
            P(name=f'gp_glass{i}', t='hip', r=ring(q), z0=20.0, z1=20.0, rh=25.0, c=GLASS, a=0.5, y=round(yy + 0.3, 1))
    lab('Grand Palais', c[0], c[1], 45, 1897)

# --- Centre Pompidou (E015 1971-1977, memoria: graduale) ---
g = fp('Centre Georges Pompidou', near=(184, 836))
if g is not None:
    clear_poly(g); c, u, Ln, Wd = frame(g)
    for i, yy in enumerate(gradual(3, 1971, 1977)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty: P(name=f'pomp{i}', t='prism', r=ring(q), z0=0.0, z1=42.0, c='#5d7fa3', a=0.5, y=round(yy, 1))
    lab('Centre Pompidou', c[0], c[1], 42, 1971)

# --- Gare du Nord (E031 1861-1864 memoria), Gare de Lyon (E032 1895-1900 memoria) con torre dell'orologio 67 m ---
for nm, near, a0, a1, tower in (('Gare du Nord', (398, 3043), 1861, 1864, None), ('Gare de Lyon', (1815, -940), 1895, 1900, 67.0)):
    g = fp(nm, near=near)
    if g is None: continue
    clear_poly(g); c, u, Ln, Wd = frame(g)
    for i, yy in enumerate(gradual(3, a0, a1)):
        q = g.intersection(Polygon(rect(c, u, -Ln / 2 + i * Ln / 3, -Ln / 2 + (i + 1) * Ln / 3, -Wd, Wd)))
        if not q.is_empty: nave(q, 22.0, 32.0, STONE, ZINC, round(yy, 1), name=nm[:8])
    if tower:
        tc = list(g.exterior.coords); tp_ = max(tc, key=lambda p_: p_[0] - p_[1])
        P(name='lyon_clock', t='prism', r=[[tp_[0] - 9, tp_[1]], [tp_[0], tp_[1]], [tp_[0], tp_[1] + 9], [tp_[0] - 9, tp_[1] + 9]], z0=0.0, z1=tower - 8, c=STONE, a=0.05, y=a1 - 0.5)
        P(name='lyon_clock_r', t='hip', r=[[tp_[0] - 9, tp_[1]], [tp_[0], tp_[1]], [tp_[0], tp_[1] + 9], [tp_[0] - 9, tp_[1] + 9]], z0=tower - 8, z1=tower - 8, rh=8.0, c=SLATE, a=0.05, y=a1)
    lab(nm, c[0], c[1], 35 if not tower else tower, a0)

# --- Tour Montparnasse (E016 1969-1973, fonte): sale in 4 tranche ---
g = fp('Tour Montparnasse', near=(-2047, -1200))
if g is not None:
    clear_poly(g)
    for i, yy in enumerate(gradual(4, 1969, 1973)):
        P(name=f'montp{i}', t='prism', r=ring(g), z0=210.0 * i / 4, z1=210.0 * (i + 1) / 4, c='#3a3f47', a=0.5, y=round(yy, 1))
    lab('Tour Montparnasse', g.centroid.x, g.centroid.y, 210, 1969)

# --- La Defense: Grande Arche (Wikidata 1989), dagli edifici di oggi solo etichetta ---
g = fp('Grande Arche de la Défense', near=(-8354, 4377))
if g is not None: lab('La Défense', g.centroid.x, g.centroid.y, 110, 1958)

# =====================================================================================================
# 4. QUAI in pietra lungo Senna e canali dentro Parigi (il render non disegna pareti tra terra e acqua)
#    anno: quai ALPAGE 1312-1789 (DD1) se entro 40 m, altrimenti A015 (1800-1900 GRADUALE, memoria) lungo il fiume
# =====================================================================================================
WZ = CFG.get('water_z', -3.0)
landj = json.load(open(f'{DATA}/land.json'))
LG = unary_union([Polygon(r_['ext'], r_.get('holes', [])).buffer(0) for r_ in landj])
WAT = box(-8500, -8500, 8500, 8500).difference(LG)
big = unary_union([q for q in (WAT.geoms if hasattr(WAT, 'geoms') else [WAT]) if q.area > 30000])
qa = A.layer('Quais_1312_1789')
def _yr(v):
    try: return float(v.year) if hasattr(v, 'year') else (float(v) if v == v and v else 1600.0)
    except Exception: return 1600.0
qlines = [(g_, _yr(dd)) for g_, dd in zip(qa.geometry.values, qa['DD1'])]
from shapely.strtree import STRtree
qtree = STRtree([g_ for g_, _ in qlines])
nq = 0
inside_paris = Point(0, 0).buffer(6800)
for poly in (big.geoms if hasattr(big, 'geoms') else [big]):
    for rg in [poly.exterior] + list(poly.interiors):
        cs = list(rg.simplify(3).coords)
        for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
            dl = math.hypot(x1 - x0, y1 - y0)
            if dl < 4: continue
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if not inside_paris.contains(Point(mx, my)): continue
            nx, ny = -(y1 - y0) / dl, (x1 - x0) / dl
            if not LG.contains(Point(mx + nx * 3, my + ny * 3)): nx, ny = -nx, -ny          # verso terra
            q = [[x0, y0], [x1, y1], [x1 + nx * 2.0, y1 + ny * 2.0], [x0 + nx * 2.0, y0 + ny * 2.0]]
            near = [qlines[i][1] for i in qtree.query(Point(mx, my).buffer(40))]
            y_ = min(near) if near else 1800 + 100 * ((math.degrees(math.atan2(my, mx)) + 180) % 360) / 360
            P(name='quay', t='prism', r=[[round(a_, 1), round(b_, 1)] for a_, b_ in q], z0=WZ - 0.6, z1=0.12, c='#cbbfa3', a=0.05, y=round(y_, 1))
            nq += 1
log('quai: segmenti', nq)

json.dump({'parts': parts, 'clear': clear, 'labels': labels, 'fires': fires}, open(f'{DATA}/landmarks.json', 'w'))
log(f'FATTO: {len(parts)} parti, {len(clear)} pezzi di impronta da sgombrare, {len(labels)} etichette, {len(fires)} incendi')
