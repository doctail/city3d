# Strato storico di Parigi, costruito dai DATI (non da curve inventate) dove ci sono:
#  - ALPAGE (ODbL): isolati 1300, 1380 (uso del suolo), 1553, 1652, 1741 (con tipologia Urbain/Intermediaire/Rural), 1791,
#    Vasserot 1810-1836 (40.356 edifici reali, isolati, idrografia); Senna 1380, 1791, 1830.
#  - BDNB/OSM (edifici di oggi, prep_parigi.py), vie di Parigi (decreti di apertura), scheda di validazione (parigi/validazione).
# Uscite in DATA: hist.json (predecessori: edifici di Vasserot e case dei villaggi, [{"r","h","y","d","old"}]),
#   landphases.json (acqua che va e viene), urban_grid.npz (anno di urbanizzazione su griglia: lo legge urban_year()),
#   hist_stats.json (conteggi e fonti per i controlli), buildings.json aggiornato (solo anni stimati piu' vecchi della zona).
# Origine (0, 0) = Notre-Dame (city_parigi.json). Metri: x est, y nord.
# Uso: python hist_parigi.py DATA_DIR [RAW_DIR=raw_parigi]
import json, math, os, random, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, 'city_parigi.json')))
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def ll(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def log(*a): print('[hist_parigi]', *a, flush=True)

# ---------------- griglie dell'anno di urbanizzazione ----------------
# interna: 10 m sul Parigi di Vasserot (fino al muro dei Fermiers generaux); esterna: 100 m su tutto il raggio
GI = dict(x0=-6000.0, y0=-4000.0, c=10.0, nx=1150, ny=900)
GO = dict(x0=-12000.0, y0=-12000.0, c=100.0, nx=240, ny=240)
_U = None
def _find_grid():
    cand = [os.environ.get('CITY_DATA', '')]
    if '--' in sys.argv: cand.insert(0, sys.argv[sys.argv.index('--') + 1])
    cand += [a_ for a_ in sys.argv[1:2] if not a_.startswith('-')] + ['data_parigi', os.path.join(HERE, 'data_parigi')]
    for d in cand:
        f = os.path.join(d, 'urban_grid.npz') if d else ''
        if f and os.path.exists(f): return f
    return None
def urban_year(x, y):
    """Anno in cui il punto diventa citta' (9999 = campagna fino alla fine). Letto da DATA/urban_grid.npz."""
    global _U
    if _U is None:
        f = _find_grid()
        if not f: return 9999
        z = np.load(f); _U = (z['inner'], z['outer'])
    ui, uo = _U
    i = int((x - GI['x0']) // GI['c']); j = int((y - GI['y0']) // GI['c'])
    if 0 <= i < GI['nx'] and 0 <= j < GI['ny'] and ui[j, i] < 9000: v = float(ui[j, i])
    else:
        i = int((x - GO['x0']) // GO['c']); j = int((y - GO['y0']) // GO['c'])
        v = float(uo[j, i]) if 0 <= i < GO['nx'] and 0 <= j < GO['ny'] else 9999.0
    return v + (2.5 * math.sin(x / 170.0) + 2.0 * math.sin(y / 230.0 + x / 410.0) if v < 9000 else 0)

# nuclei antichi esistenti nel 1190 (anno di partenza): Cite', Greve, Saint-Germain-des-Pres, Sainte-Genevieve, Saint-Marcel.
# [Likely] posizioni da lat/lon dei monumenti; raggio = nucleo gia' costruito; oltre, crescita fino al 1300 (isolati ALPAGE 1300)
CORES = [(ll(48.8540, 2.3470), 450, 1000, 'Cite'), (ll(48.8566, 2.3522), 380, 1120, 'Greve / Saint-Gervais'),
         (ll(48.8540, 2.3337), 220, 1120, 'Saint-Germain-des-Pres'), (ll(48.8462, 2.3479), 200, 1150, 'Sainte-Genevieve'),
         (ll(48.8375, 2.3583), 220, 1150, 'Saint-Marcel'), (ll(48.8660, 2.3540), 160, 1150, 'Saint-Martin-des-Champs')]
# villaggi fuori dal muro dei Fermiers generaux (annessi nel 1860) e dei comuni vicini: nucleo antico, poi il fronte BDNB.
VILLAGES = [('Montmartre', 48.8867, 2.3404, 1150), ('Belleville', 48.8722, 2.3767, 1500), ('Menilmontant', 48.8665, 2.3895, 1650),
            ('Charonne', 48.8555, 2.4005, 1300), ('Bercy', 48.8355, 2.3830, 1650), ('Vaugirard', 48.8404, 2.2995, 1300),
            ('Grenelle', 48.8478, 2.2916, 1830), ('Passy', 48.8575, 2.2815, 1400), ('Auteuil', 48.8475, 2.2696, 1200),
            ('Batignolles', 48.8844, 2.3204, 1830), ('La Chapelle', 48.8885, 2.3605, 1300), ('La Villette', 48.8885, 2.3740, 1400),
            ('Petit-Montrouge', 48.8306, 2.3265, 1600), ('Maison-Blanche', 48.8225, 2.3540, 1700), ('Neuilly', 48.8850, 2.2680, 1600),
            ('Boulogne', 48.8397, 2.2399, 1350), ('Clichy', 48.9040, 2.3060, 1300), ('Levallois', 48.8950, 2.2870, 1850),
            ('Issy', 48.8240, 2.2700, 1200), ('Vanves', 48.8220, 2.2900, 1300), ('Montrouge', 48.8163, 2.3162, 1300),
            ('Ivry', 48.8156, 2.3849, 1300), ('Charenton', 48.8217, 2.4129, 1400), ('Saint-Mande', 48.8423, 2.4186, 1500),
            ('Vincennes', 48.8474, 2.4392, 1400), ('Montreuil', 48.8638, 2.4485, 1300), ('Bagnolet', 48.8690, 2.4180, 1300),
            ('Pantin', 48.8944, 2.4093, 1300), ('Aubervilliers', 48.9146, 2.3821, 1300), ('Saint-Ouen', 48.9123, 2.3346, 1300),
            ('Puteaux', 48.8846, 2.2389, 1300), ('Courbevoie', 48.8973, 2.2524, 1300), ('Suresnes', 48.8710, 2.2290, 1200),
            ('Saint-Denis', 48.9356, 2.3539, 1100), ('Gentilly', 48.8130, 2.3440, 1300), ('Le Pre-Saint-Gervais', 48.8850, 2.4040, 1500)]

def _epochs(A, shapely):
    """[(anno, codici per poligono)] codice 3 urbano, 2 intermedio, 1 rurale/campi. Strade tra isolati urbani: buffer 8 m."""
    E = []
    g = A.layer('Ilots_1300')
    code = np.where(g['IN_OUT1300'].astype(str).str.startswith('dans'), 3, 2); code[g['REGION'].astype(str).str.contains('non bat')] = 1
    E.append((1300, g.geometry.values, code))
    g = A.layer('1380_usages_sol'); lg = g['LEGENDE'].astype(str)
    code = np.where(lg.str.contains('Champs|terrains vagues|Hydro|Enceinte'), 1, 3); code[lg.str.contains('Hydro|Enceinte')] = 0
    E.append((1380, g.geometry.values, code))
    for y, n in ((1553, 'Ilots_1553'), (1652, 'Ilots_1652'), (1741, 'Ilots_1741')):
        g = A.layer(n); t = g['typologie_'].astype(str)
        E.append((y, g.geometry.values, np.where(t.str.startswith('Urb'), 3, np.where(t.str.startswith('Int'), 2, 1))))
    g = A.layer('Ilots_1791'); E.append((1791, g.geometry.values, np.full(len(g), 2)))
    return E

def build_grids(DATA, A, blds, shapely, nd):
    from shapely import contains_xy
    xs = GI['x0'] + (np.arange(GI['nx']) + 0.5) * GI['c']; ys = GI['y0'] + (np.arange(GI['ny']) + 0.5) * GI['c']
    X, Y = np.meshgrid(xs, ys)
    first_u = np.full(X.shape, 9999.0); prev = np.full(X.shape, 1190.0); known = np.zeros(X.shape, bool)
    first_i = np.full(X.shape, 9999.0)   # prima epoca in cui l'isolato e' almeno 'intermedio' (in parte costruito)
    stats = {}
    E = _epochs(A, shapely)
    # Vasserot come ultima epoca: densita' del costruito in 40 m (edifici reali) -> urbano se > 25%
    vb = A.layer('Vasserot_1_Bati'); vb = vb[vb['BATI'].fillna('').astype(str).isin(['1', '3'])]   # BATI 2 = cortili e giardini (non costruito)
    vu = shapely.union_all(vb.geometry.buffer(0).values)
    vin = contains_xy(vu, X, Y).astype(float)
    k = int(40 / GI['c']); dens = nd.uniform_filter(vin, size=2 * k + 1)
    vil = shapely.union_all(A.layer('Vasserot_1_Ilots').geometry.buffer(0).values)
    v_ext = contains_xy(vil.buffer(30), X, Y)
    E.append((1825, None, None))
    for (yr, geoms, code) in E:
        if geoms is not None:
            ext = shapely.union_all([g_.buffer(0) for g_ in geoms]).convex_hull
            inext = contains_xy(ext, X, Y)
            lvl = np.zeros(X.shape, np.int8)
            for c_ in (1, 2, 3):
                sel = [g_.buffer(8 if c_ == 3 else 0) for g_, cc in zip(geoms, code) if cc == c_]
                if not sel: continue
                m = contains_xy(shapely.union_all(sel), X, Y)
                lvl[m] = np.maximum(lvl[m], c_)
        else:   # Vasserot
            inext = v_ext; lvl = np.where(dens > 0.25, 3, np.where(v_ext, 2, 0)).astype(np.int8)
        if yr not in (1791, 1825): first_i = np.where((lvl >= 2) & (first_i > 9000) & inext, yr, first_i)
        newu = (lvl == 3) & (first_u > 9000) & inext
        # dentro l'intervallo [prev, yr]: prima i punti vicini alla citta' gia' esistente (crescita verso l'esterno)
        old = first_u < 9000
        if old.any():
            dist = nd.distance_transform_edt(~old) * GI['c']
        else:
            dist = np.full(X.shape, 600.0)
        f = np.clip(dist / 700.0, 0, 1) * 0.85 + 0.15 * nd.gaussian_filter(np.random.default_rng(yr).random(X.shape), 6) * 2
        f = np.clip(f, 0, 1)
        first_u[newu] = (prev + (yr - prev) * f)[newu]
        if yr != 1791:   # il 1791 non ha la tipologia: dice che l'isolato esiste, non che e' rurale
            prev = np.where(inext & (lvl < 3) & (lvl > 0), yr, prev)          # ultimo anno in cui il punto e' sicuramente non urbano
        stats[str(yr)] = {'nuove_celle_urbane_km2': round(float(newu.sum()) * GI['c'] ** 2 / 1e6, 2)}
        log(f'epoca {yr}: +{stats[str(yr)]["nuove_celle_urbane_km2"]} km2 urbani')
    # prima del 1300: dai nuclei antichi verso l'esterno (solo celle urbane nel 1300)
    u1300 = first_u <= 1300.5
    yc = np.full(X.shape, 1300.0)
    for (cx, cy), r, y0, _ in CORES:
        d = np.hypot(X - cx, Y - cy)
        yc = np.minimum(yc, np.where(d <= r, y0, np.minimum(1300, max(y0, 1190) + (d - r) / 1000 * 110)))
    first_u[u1300] = np.minimum(first_u[u1300], yc[u1300])
    first_u = np.where(first_u < 9000, np.maximum(first_u, 1000), 9999)

    # esterna: fronte dagli anni BDNB (15o percentile per cella di 300 m) + villaggi
    xo = GO['x0'] + (np.arange(GO['nx']) + 0.5) * GO['c']; yo = GO['y0'] + (np.arange(GO['ny']) + 0.5) * GO['c']
    XO, YO = np.meshgrid(xo, yo)
    bx = np.array([sum(p[0] for p in b['r']) / len(b['r']) for b in blds]); by = np.array([sum(p[1] for p in b['r']) / len(b['r']) for b in blds])
    byr = np.array([b['y'] for b in blds], float); est = np.array([bool(b.get('i')) for b in blds])
    ok = ~est
    ii = ((bx[ok] - GO['x0']) // 300).astype(int); jj = ((by[ok] - GO['y0']) // 300).astype(int); yy = byr[ok]
    n3 = int(GO['nx'] * GO['c'] / 300)
    front3 = np.full((n3, n3), 9999.0)
    from collections import defaultdict
    bucket = defaultdict(list)
    for a_, b_, c_ in zip(ii, jj, yy):
        if 0 <= a_ < n3 and 0 <= b_ < n3: bucket[(b_, a_)].append(c_)
    for (b_, a_), v in bucket.items():
        if len(v) >= 4: front3[b_, a_] = np.percentile(v, 15)
    front3 = np.where(front3 < 9000, np.maximum(front3, 1790), 9999)
    fr = np.kron(front3, np.ones((3, 3)))[:GO['ny'], :GO['nx']]
    fr_s = nd.median_filter(np.where(fr < 9000, fr, np.nan), size=5, mode='nearest') if False else nd.grey_closing(fr, size=3)
    outer = np.minimum(fr, fr_s)
    # villaggi: nucleo di ~120 m e crescita lenta fino al 1820 entro ~320 m; contorno irregolare (rumore), non cerchi
    rng_ = np.random.default_rng(7); noise = nd.gaussian_filter(rng_.random(XO.shape), 1.2); noise = (noise - noise.mean()) / (noise.std() + 1e-9)
    for name, la, lo, y0 in VILLAGES:
        cx, cy = ll(la, lo); d = np.hypot(XO - cx, YO - cy) * (1 + 0.28 * noise)
        vy = np.where(d < 120, y0 + d / 120 * 40, np.where(d < 320, y0 + 40 + (d - 120) / 200 * max(0, 1820 - y0 - 40), 9999))
        outer = np.minimum(outer, vy)
    # dentro la griglia interna vale l'interna; dove l'interna e' campagna (9999) vale l'esterna
    np.savez_compressed(f'{DATA}/urban_grid.npz', inner=first_u.astype(np.float32), outer=outer.astype(np.float32), inner_i=first_i.astype(np.float32))
    global _U; _U = None
    return stats

_FI = None
def first_i_at(DATA, x, y):
    global _FI
    if _FI is None: _FI = np.load(f'{DATA}/urban_grid.npz')['inner_i']
    i = int((x - GI['x0']) // GI['c']); j = int((y - GI['y0']) // GI['c'])
    return float(_FI[j, i]) if 0 <= i < GI['nx'] and 0 <= j < GI['ny'] else 9999.0

# ---------------- date delle strade (decreti) ----------------
def street_years(RAW, shapely):
    v = json.load(open(f'{RAW}/extra/paris_voies.geojson'))['features']
    geoms, yrs = [], []
    for f in v:
        p = f['properties']; t = (p.get('ouverture') or '') + ' ' + (p.get('historique') or '')
        m = re.search(r'(perc[ée]e?s?|ouverte?s?)\s+(en|de)\s+(1[6-9]\d\d)', t, re.I)
        if m: y = int(m.group(3))
        else:
            d = [int(x) for x in re.findall(r'D[ée]cret du [^()]{0,40}?(1[6-9]\d\d|20[0-2]\d)\s*\(UP\)', t)]
            if not d: continue
            y = min(d) + 2
        try: g = shapely.geometry.shape(f['geometry'])
        except Exception: continue
        geoms.append(shapely.transform(g, lambda c: np.c_[(c[:, 0] - LON0) * KX, (c[:, 1] - LAT0) * KY]).buffer(0)); yrs.append(y)
    return geoms, yrs

def era_height(u, bati, rnd):
    if bati == '3': return rnd.uniform(16, 24)    # edifici pubblici di Vasserot (chiese, halles, collegi)
    if u < 1500: return rnd.uniform(8, 11)        # case a graticcio, 2-3 piani
    if u < 1650: return rnd.uniform(10, 14)
    if u < 1780: return rnd.uniform(12, 16)       # 4 piani
    return rnd.uniform(14, 18)                    # 5 piani, prima di Haussmann

def build(DATA, RAW='raw_parigi', seed=11):
    import shapely, shapely.geometry
    from shapely.strtree import STRtree
    from scipy import ndimage as nd
    sys.path.insert(0, HERE)
    from tools.alpage import Alpage
    from hist_nyc import split
    A = Alpage(os.path.join(RAW, 'alpage'), CFG)
    blds = json.load(open(f'{DATA}/buildings.json'))
    stats = {'epoche': build_grids(DATA, A, blds, shapely, nd)}
    rnd = random.Random(seed)

    # --- anni di oggi stimati e piu' vecchi della zona: alzati all'anno di urbanizzazione (niente case nei campi) ---
    bumped = 0
    for b in blds:
        if not (b.get('i') or b.get('y0') or b['y'] < 1850): continue
        cx = sum(p[0] for p in b['r']) / len(b['r']); cy = sum(p[1] for p in b['r']) / len(b['r'])
        u = urban_year(cx, cy)
        if u < 9000 and b['y'] < u - 5 and (b.get('i') or b.get('y0')):
            b['y'] = int(u + rnd.uniform(0, 8)); bumped += 1
    stats['anni_stimati_alzati'] = bumped

    # --- predecessori reali: Vasserot 1810-1836 ---
    tp = [shapely.Polygon(b['r']).buffer(0) for b in blds]; tree = STRtree(tp); ty = np.array([b['y'] for b in blds])
    sg, sy = street_years(RAW, shapely); stree = STRtree(sg) if sg else None
    vb = A.layer('Vasserot_1_Bati')
    vb = vb[vb['BATI'].fillna('').astype(str).isin(['1', '3']) & (vb.area < 15000)]   # BATI 2 = cortili e giardini; >1,5 ha = recinti
    out = []; c_surv = c_repl = c_street = c_def = 0
    for g, bati, dc in zip(vb.geometry.values, vb['BATI'].fillna('').astype(str), vb['DATE_COYEC'].fillna('').astype(str)):
        for p in (g.geoms if hasattr(g, 'geoms') else [g]):
            if p.geom_type != 'Polygon' or p.area < 8: continue
            c = p.representative_point()
            survey = int(re.findall(r'(18[0-3]\d)', dc)[0]) if re.findall(r'(18[0-3]\d)', dc) else 1825
            u = urban_year(c.x, c.y)
            s = (u + rnd.uniform(0, 10)) if u < 9000 else rnd.uniform(1795, survey)
            fi = first_i_at(DATA, c.x, c.y)
            if fi < s - 10 and rnd.random() < 0.5: s = fi - rnd.uniform(0, 40)   # isolato 'intermedio' in un'epoca precedente: meta' delle case c'era gia'
            s = min(s, survey - rnd.uniform(0, 3))
            # chi lo sostituisce: edifici di oggi che ne coprono almeno il 25%
            hits = [i for i in tree.query(p) if tp[i].intersects(p)]
            cov = [(i, tp[i].intersection(p).area / p.area) for i in hits]
            cov = [(i, f) for i, f in cov if f > 0.25]
            if cov:
                yT = min(ty[i] for i, _ in cov)
                if yT <= survey + 5: c_surv += 1; continue      # e' lo stesso edificio di oggi (o il suo diretto erede): niente doppione
                d = yT - rnd.uniform(0.3, 1.5); c_repl += 1
            else:
                d = None
                if stree is not None:
                    sh = [sy[i] for i in stree.query(c) if sg[i].contains(c)]
                    if sh: d = min(sh) - rnd.uniform(0, 1.5); c_street += 1
                if d is None: d = rnd.uniform(1852, 1870); c_def += 1   # demolizioni del Secondo Impero senza data puntuale
            if d - s < 3: continue
            ring = [[round(x, 2), round(y, 2)] for x, y in list(p.simplify(0.3).exterior.coords)[:-1]]
            if len(ring) < 3: continue
            if s < 1600 and d > 1760 and bati != '3':      # seconda generazione: la casa medievale rifatta in pietra (XVII-XVIII sec.)
                sw = rnd.uniform(max(s + 60, 1640), 1790)
                out.append({'r': ring, 'h': round(era_height(s, bati, rnd), 1), 'y': round(s, 1), 'd': round(sw - 0.5, 1), 'old': True})
                out.append({'r': ring, 'h': round(era_height(sw, bati, rnd), 1), 'y': round(sw, 1), 'd': round(d, 2), 'old': True})
            else:
                out.append({'r': ring, 'h': round(era_height(s, bati, rnd), 1), 'y': round(s, 1), 'd': round(d, 2), 'old': True})
    stats['vasserot'] = {'sopravvissuti_oggi': c_surv, 'sostituiti_da_edifici_di_oggi': c_repl, 'demoliti_per_strada_datata': c_street,
                         'demoliti_data_generica_1852_1870': c_def, 'predecessori': len(out)}
    log('Vasserot:', stats['vasserot'])

    # --- villaggi e periferia (fuori da Vasserot): predecessori generici come a Copenaghen ---
    vext = shapely.union_all(A.layer('Vasserot_1_Ilots').geometry.buffer(0).values).buffer(40)
    from shapely.prepared import prep
    vext_p = prep(vext); n0 = len(out)
    for b, p in zip(blds, tp):
        if p.area < 15: continue
        c = p.representative_point()
        if vext_p.contains(c): continue
        u = urban_year(c.x, c.y) + rnd.uniform(-4, 10)
        if u > 9000 or b['y'] < u + 35 or p.area < 30: continue
        for q in (split(p) if p.area > 600 else [p]):
            ring = [[round(x, 2), round(yv, 2)] for x, yv in list(q.exterior.coords)[:-1]]
            start = u + rnd.uniform(0, 12); died = b['y'] - rnd.uniform(0.3, 2.0)
            if died - start < 8: continue
            if start < 1800 and rnd.random() < 0.5: start = rnd.uniform(max(start, 1790), 1840)   # meta' delle case del villaggio arriva tardi
            out.append({'r': ring, 'h': round(rnd.uniform(6, 10) if start < 1850 else rnd.uniform(8, 14), 1), 'y': round(start, 1), 'd': round(died, 2), 'old': start < 1860})
    stats['villaggi_periferia_predecessori'] = len(out) - n0
    log('predecessori fuori da Vasserot:', len(out) - n0)
    json.dump(out, open(f'{DATA}/hist.json', 'w'))
    json.dump(blds, open(f'{DATA}/buildings.json', 'w'))

    # --- acqua a fasi ---
    stats['acqua'] = water_phases(DATA, A, shapely, nd)
    json.dump(stats, open(f'{DATA}/hist_stats.json', 'w'), indent=1)
    log(f'FATTO: {len(out)} predecessori, anni stimati alzati {bumped}')

# elementi d'acqua della scheda (sezione A) con un punto di riferimento: le zone che cambiano vicino al punto prendono le sue date.
# GRADUALE = la zona cambia a strisce nell'intervallo; le righe DA MEMORIA non sono mai BRUSCO (regola 5 della regia).
WATER_KEYS = [  # (id scheda, lat, lon, raggio m, da, a, tipo: 'fill' acqua->terra | 'dig' terra->acqua)
    ('A001', 48.8517, 2.3567, 350, 1614, 1655, 'fill'),    # isolotti Notre-Dame e aux Vaches uniti (GRADUALE, memoria)
    ('A002', 48.8497, 2.3640, 350, 1843, 1843, 'fill'),    # Ile Louviers unita alla riva destra (BRUSCO, fonte)
    ('A012', 48.8490, 2.3685, 300, 1806, 1811, 'dig'),     # Bassin de l'Arsenal (memoria 1806 -> GRADUALE fino a A003)
    ('A007', 48.8710, 2.3650, 900, 1822, 1825, 'dig'),     # Canal Saint-Martin (CONFLITTO: GRADUALE 1822-1825, decisione regia)
    ('A011', 48.8880, 2.3740, 500, 1808, 1813, 'dig'),     # Bassin de la Villette (memoria 1808 -> GRADUALE fino a A003 1813)
    ('A003', 48.8930, 2.3900, 1500, 1813, 1813, 'dig'),    # Canal de l'Ourcq fino a La Villette (BRUSCO, fonte)
    ('A005', 48.9000, 2.3660, 2500, 1821, 1821, 'dig'),    # Canal Saint-Denis (BRUSCO, fonte)
    ('A013', 48.8620, 2.3700, 700, 1860, 1862, 'fill'),    # copertura sotto bd Richard-Lenoir (GRADUALE, fonte)
    ('A014', 48.8680, 2.3660, 300, 1906, 1906, 'fill'),    # copertura bd Jules Ferry (BRUSCO, fonte)
]
def water_phases(DATA, A, shapely, nd):
    from shapely import contains_xy
    from shapely.geometry import Polygon
    land = json.load(open(f'{DATA}/land.json'))
    L = shapely.union_all([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in land])
    c = 5.0; x0, y0, x1, y1 = -5600, -3100, 5600, 4000
    xs = np.arange(x0, x1, c) + c / 2; ys = np.arange(y0, y1, c) + c / 2; X, Y = np.meshgrid(xs, ys)
    now_w = ~contains_xy(L, X, Y)
    eps = []
    frames = {1380: 'Ilots_1380', 1791: 'Ilots_1791', 1825: 'Vasserot_1_Ilots'}
    for yr, n in ((1380, '1380_hydro'), (1791, 'Hydro_1791'), (1825, 'Vasserot_2_Hydro')):
        g = A.layer(n)
        W = shapely.union_all(g.geometry.buffer(0).values)
        # parte coperta davvero dalla carta: isolati della stessa epoca (convesso) ristretti di 150 m, piu' il fiume vicino
        fr = shapely.union_all(A.layer(frames[yr]).geometry.buffer(0).values).convex_hull.buffer(-150)
        ext = fr.intersection(W.buffer(250))
        eps.append((yr, contains_xy(W, X, Y), contains_xy(ext, X, Y)))
    k = int(10 / c)
    def clean(m):   # via le strisce da georeferenziazione (larghezza < 20 m)
        return nd.binary_dilation(nd.binary_erosion(m, iterations=k), iterations=k)
    regions = []
    for kind in ('fill', 'dig'):
        # fill: era acqua in un'epoca e oggi e' terra; dig: era terra (dentro l'estensione) e oggi e' acqua
        last = np.full(X.shape, -1.0); nxt = np.full(X.shape, 2026.0); m_any = np.zeros(X.shape, bool)
        for yr, w, ext in eps:
            cond = (w & ~now_w) if kind == 'fill' else (ext & ~w & now_w)
            m_any |= cond; last = np.where(cond, yr, last)
        for yr, w, ext in eps:   # prima epoca DOPO l'ultima in cui c'era lo stato vecchio, in cui lo stato e' gia' quello di oggi
            cond_new = ext & ((~w & ~now_w) if kind == 'fill' else (w & now_w))
            nxt = np.where(cond_new & (yr > last) & (nxt == 2026), yr, nxt)
        m = clean(m_any)
        lab, n = nd.label(m)
        for i in range(1, n + 1):
            mm = lab == i
            if mm.sum() * c * c < 2500: continue
            if kind == 'dig' and mm.sum() * c * c < 20000:
                ring_ = nd.binary_dilation(mm, iterations=int(15 / c)) & ~mm
                if now_w[ring_].mean() > 0.6: continue   # striscia d'acqua di oggi circondata da acqua: e' un ponte disegnato sulla carta
            ys_, xs_ = np.nonzero(mm)
            a0 = float(np.median(last[mm][last[mm] > 0])) if (last[mm] > 0).any() else 1380
            a1 = float(np.median(nxt[mm]))
            regions.append((kind, mm, a0, a1))
    # mappa delle regioni -> poligoni (contorni della maschera)
    from shapely import box as sbox
    out = []; info = []
    for kind, mm, a0, a1 in regions:
        ys_, xs_ = np.nonzero(mm)
        cells = [sbox(xs[i] - c / 2, ys[j] - c / 2, xs[i] + c / 2, ys[j] + c / 2) for j, i in zip(ys_, xs_)]
        poly = shapely.union_all(cells).simplify(2.0)
        cx, cy = poly.centroid.x, poly.centroid.y
        key = None
        for k_ in WATER_KEYS:
            kx, ky = ll(k_[1], k_[2])
            if k_[6] == kind and math.hypot(cx - kx, cy - ky) < k_[3]: key = k_; break
        if key: f0, f1, src = key[4], key[5], key[0]
        else: f0, f1, src = a0, a1, 'DATI ALPAGE (intervallo tra epoche)'
        f0, f1 = min(f0, f1), max(f0, f1)
        if f1 > 2025 and not key: f1 = 1900          # cambi tra Vasserot e oggi senza data: quai del XIX secolo (A015, 1800-1900 GRADUALE)
        for q in (poly.geoms if hasattr(poly, 'geoms') else [poly]):
            if q.geom_type != 'Polygon' or q.area < 800: continue
            r = [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]]
            yr_change = round(f0 + (f1 - f0) * random.Random(int(cx)).random(), 1) if f1 > f0 else f0
            if kind == 'fill': out.append({'r': r, 'from': yr_change, 'to': 9999, 'c': 'urban', 'src': src})   # terra dal riempimento
            else: out.append({'r': r, 'from': -9999, 'to': yr_change, 'c': 'field', 'src': src})            # terra fino allo scavo
            info.append({'tipo': kind, 'area_m2': round(q.area), 'centro': [round(cx), round(cy)], 'anni': [f0, f1], 'cambio': yr_change, 'fonte': src})
    json.dump(out, open(f'{DATA}/landphases.json', 'w'))
    log('acqua a fasi:', len(out), 'zone;', sum(1 for i in info if i['fonte'].startswith('A')), 'con data della scheda')
    return info

if __name__ == '__main__':
    sys.path.insert(0, HERE)
    build(sys.argv[1] if len(sys.argv) > 1 else 'data_parigi', sys.argv[2] if len(sys.argv) > 2 else 'raw_parigi')
