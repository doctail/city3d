# Francia (Parigi), passo 1 sul pod CPU: edifici della BDNB (Base de Données Nationale des Bâtiments, open data per dipartimento)
# -> ritaglio entro clip_radius_m dal centro, anno/livelli/altezza per edificio, COPERTURA PER ARRONDISSEMENT.
# Uso:
#   python fetch_fr_raw.py urls city_parigi.json                 -> stampa gli URL dei GPKG dei dipartimenti (API data.gouv)
#   python fetch_fr_raw.py clip city_parigi.json OUTDIR a.gpkg [b.gpkg ...]
#        -> OUTDIR/bdnb.geojson.gz (WGS84; id, insee, y, lev, h, src), OUTDIR/copertura.csv, OUTDIR/schema.txt, OUTDIR/anni.txt
# La BDNB lega ogni "batiment_groupe" all'anno dei Fichiers fonciers (ffo_bat) e all'altezza della BD TOPO (bdtopo_bat).
# I nomi delle tabelle/colonne cambiano tra millesimi: si cercano per candidati e, se mancano, si scrive schema.txt e ci si ferma.
# Il codice INSEE dei 20 arrondissement e' 75101..75120: la copertura per arrondissement viene da li', senza confini a parte.
import gzip, json, math, os, sys, collections

MODE, CFG = sys.argv[1], json.load(open(sys.argv[2]))
LAT0, LON0 = CFG['lat0'], CFG['lon0']
R = CFG.get('clip_radius_m', CFG.get('radius_m', 9000))
def log(*a): print('[fetch_fr]', *a, file=sys.stderr, flush=True)   # stderr: stdout e' SOLO per gli URL

if MODE == 'urls':
    # Le estrazioni per dipartimento NON sono tra le risorse data.gouv (li' c'e' solo la Francia intera, 48 GB):
    # stanno su https://bdnb.io/download/. Si leggono tutti i link della pagina (anche dentro script/JSON) e si tengono
    # quelli che contengono il dipartimento e "gpkg"; per ogni dipartimento il piu' recente (ordine alfabetico = millesimo).
    import re, requests
    deps = [str(d) for d in CFG['bdnb_deps']]
    pages = CFG.get('bdnb_pages', ['https://bdnb.io/download/'])
    links = set()
    for p in pages:
        try:
            t = requests.get(p, timeout=60, headers={'User-Agent': 'Mozilla/5.0 city3d'}).text
        except Exception as e:
            log('pagina non letta:', p, e); continue
        open('/workspace/bdnb_download_page.html', 'w').write(t)
        for u in re.findall(r'https?://[^\s"\'<>()\\]+', t.replace('\\/', '/')): links.add(u.rstrip('.,;'))
        for u in re.findall(r'(?:href|src)=["\']([^"\']+)', t):
            if not u.startswith('http'): u = requests.compat.urljoin(p, u)
            links.add(u)
    log('link trovati nella pagina:', len(links))
    out = []
    for d in deps:
        pat = re.compile(rf'(dep|departement|dpt)[_\-]?0?{d}(?!\d)', re.I)
        c = sorted((u for u in links if pat.search(u) and 'gpkg' in u.lower()), key=lambda u: u.rsplit('/', 1)[-1])
        if not c: log('NESSUN link GPKG per il dipartimento', d); continue
        log(f'dip. {d}: {c[-1]}'); out.append(c[-1])
    if len(out) < len(deps):
        log('Pagina salvata in /workspace/bdnb_download_page.html. Link con "gpkg":',
            *sorted(u for u in links if 'gpkg' in u.lower())[:20])
        sys.exit(1)
    print('\n'.join(out)); sys.exit(0)

import numpy as np, pyogrio, shapely
from pyproj import Transformer
OUT = sys.argv[3]; SRC = sys.argv[4:]
os.makedirs(OUT, exist_ok=True)
YC = ('ffo_bat_annee_construction', 'annee_construction', 'annee_construction_ffo')
Y2 = ('dpe_mix_arrete_annee_construction_dpe', 'rnc_l_annee_construction', 'dpe_ter_annee_construction_dpe', 'rpls_l_annee_construction')   # ripiego, segnato src
LC = ('ffo_bat_nb_niveau', 'nb_niveau', 'nb_niveau_ffo')
HC = ('bdtopo_bat_hauteur_mean', 'hauteur_mean', 'hauteur', 'hauteur_moyenne')
ID = 'batiment_groupe_id'
# colonne in piu' (vista compile, millesimo 2026-02-b): altezza massima (torri), monumento storico vicino, usi e materiali
EXTRA = {'hmax': 'bdtopo_bat_max_hauteur', 'mer': 'merimee_nom_batiment_historique_plus_proche', 'merd': 'merimee_distance_batiment_historique_plus_proche',
         'use': 'usage_principal_bdnb_open', 'use1': 'bdtopo_bat_l_usage_1', 'roof': 'ffo_bat_mat_toit_txt', 'wall': 'ffo_bat_mat_mur_txt', 'nlog': 'ffo_bat_nb_log'}

def pick(cols, cand):
    for c in cand:
        if c in cols: return c
    return None

schema = open(os.path.join(OUT, 'schema.txt'), 'w')
feats = []
for path in SRC:
    layers = [l[0] for l in pyogrio.list_layers(path)]
    cols = {l: list(pyogrio.read_info(path, layer=l)['fields']) for l in layers}
    for l in layers: schema.write(f'{os.path.basename(path)} | {l}: {", ".join(cols[l])}\n')
    def polys(l):
        # il tipo dichiarato puo' essere generico ("Unknown"/"Geometry"): si guarda il primo oggetto vero
        info = pyogrio.read_info(path, layer=l)
        if not info.get('geometry_type'): return False
        try:
            d = pyogrio.read_dataframe(path, layer=l, max_features=5)
            t = ' '.join(str(x) for x in d.geometry.geom_type.dropna().unique()).lower()
        except Exception as e:
            log('  strato', l, 'non leggibile:', e); return False
        log(f'  strato {l}: dichiarato {info.get("geometry_type")}, reale {t or "vuoto"}')
        return 'polygon' in t
    # strato degli edifici: prima la vista "compile" (millesimi 2025+: anno, livelli, altezza tutti li'), poi le altre
    pref = ('batiment_groupe_compile', 'batiment_groupe', 'batiment_construction')
    geo = next((l for l in pref if l in layers and polys(l)), None) \
        or next((l for l in layers if 'batiment' in l and not l.startswith('rel_') and polys(l)), None)
    ffo = next((l for l in layers if l.endswith('ffo_bat')), None)
    bdt = next((l for l in layers if l.endswith('bdtopo_bat') and not l.startswith('rel_')), None)
    if not geo:
        log(os.path.basename(path), '| nessuno strato di edifici (poligoni): saltato'); continue
    crs = pyogrio.read_info(path, layer=geo)['crs']
    log(os.path.basename(path), '| geometria:', geo, crs, pyogrio.read_info(path, layer=geo).get('geometry_type'),
        '| anno:', pick(cols[geo], YC) or ffo, '| altezza:', pick(cols[geo], HC) or bdt)
    to_loc = Transformer.from_crs('EPSG:4326', crs, always_xy=True)
    to_ll = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
    CX, CY = to_loc.transform(LON0, LAT0)
    keep = [c for c in (ID, 'code_commune_insee', 'libelle_commune_insee') if c in cols[geo]]
    keep += [c for c in (pick(cols[geo], YC), pick(cols[geo], LC), pick(cols[geo], HC)) if c]
    keep += [c for c in Y2 if c in cols[geo]]
    keep += [c for c in EXTRA.values() if c in cols[geo]]
    if ID not in cols[geo]: ID = 'batiment_construction_id'
    g = pyogrio.read_dataframe(path, layer=geo, columns=keep, bbox=(CX - R, CY - R, CX + R, CY + R))
    c = shapely.centroid(g.geometry.values)
    g = g[((shapely.get_x(c) - CX) ** 2 + (shapely.get_y(c) - CY) ** 2) < R * R]
    log('  edifici nel raggio:', len(g))
    ids = set(g[ID])
    def table(layer, cands):
        # -> {id: {nome_logico: valore}} per le colonne trovate (una riga per id: si tiene la prima)
        if not layer: return {}
        cs = {k: pick(cols[layer], c) for k, c in cands.items()}; cs = {k: v for k, v in cs.items() if v}
        if not cs: return {}
        t = pyogrio.read_dataframe(path, layer=layer, columns=[ID] + list(cs.values()), read_geometry=False)
        t = t[t[ID].isin(ids)].drop_duplicates(ID)
        return {i: {k: t_[v] for k, v in cs.items()} for i, t_ in zip(t[ID], t.to_dict('records'))}
    ext = table(ffo, {'y': YC, 'lev': LC})
    for i, d in table(bdt, {'h': HC}).items(): ext.setdefault(i, {}).update(d)
    gcols = {k: pick(cols[geo], c) for k, c in (('y', YC), ('lev', LC), ('h', HC))}
    blank = lambda v: v is None or (isinstance(v, float) and v != v)
    for row, geom in zip(g.itertuples(index=False), g.geometry.values):
        r = row._asdict(); i = r.get(ID); e = ext.get(i, {})
        val = {k: (r.get(c) if c else None) for k, c in gcols.items()}
        for k in val:
            if blank(val[k]): val[k] = e.get(k)
        y, lev, h = val['y'], val['lev'], val['h']
        def num(v):
            try:
                v = float(v); return None if v != v else v
            except (TypeError, ValueError): return None
        y, lev, h = num(y), num(lev), num(h)
        src = 'ffo' if y and 1000 <= y <= 2026 else None
        if not src:   # ripiego: DPE / registro copropriete' / RPLS (anni dichiarati, a volte liste "1930,1931")
            for c in Y2:
                v = r.get(c)
                if v is None: continue
                import re as _re
                m = _re.search(r'(1[0-9]{3}|20[0-2][0-9])', str(v))
                if m: y = int(m.group(1)); src = c.split('_')[0]; break
            else: y = None
        geom = shapely.transform(geom, lambda xy: np.c_[to_ll.transform(xy[:, 0], xy[:, 1])])
        feats.append({'type': 'Feature', 'geometry': shapely.geometry.mapping(geom),
                      'properties': {'id': i, 'insee': r.get('code_commune_insee'), 'y': int(y) if y else None, 'src': src,
                                     **{k: (None if blank(r.get(c)) else (round(float(r[c]), 1) if k in ('hmax', 'merd') else r[c])) for k, c in EXTRA.items() if c in r},
                                     'lev': int(lev) if lev is not None else None, 'h': round(h, 1) if h else None}})
schema.close()
with gzip.open(os.path.join(OUT, 'bdnb.geojson.gz'), 'wt') as f:
    json.dump({'type': 'FeatureCollection', 'features': feats}, f)

# --- copertura: anno valido = 1000..2026 ---
ok = lambda y: y is not None and 1000 <= y <= 2026
per = collections.defaultdict(lambda: [0, 0, 0])
for f in feats:
    p = f['properties']; k = str(p['insee'] or '?'); per[k][0] += 1; per[k][1] += ok(p['y']); per[k][2] += p.get('src') == 'ffo'
soglia = CFG.get('coverage_min', 0.70)
with open(os.path.join(OUT, 'copertura.csv'), 'w') as f:
    f.write('insee,zona,edifici,con_anno,quota,solo_fichiers_fonciers,sotto_soglia\n')
    for k in sorted(per):
        n, a, a1 = per[k]; z = f'{int(k) - 75100}e arr.' if k.startswith('751') and len(k) == 5 else 'fuori Parigi'
        f.write(f'{k},{z},{n},{a},{a / n:.3f},{a1 / n:.3f},{"SI" if a / n < soglia else ""}\n')
par = {k: v for k, v in per.items() if k.startswith('751')}
log('arrondissement trovati:', len(par), '/ 20')
for k in sorted(par):
    n, a, a1 = par[k]; log(f'  {int(k) - 75100:2d}e: {a}/{n} = {a / n:.0%} (solo Fichiers fonciers {a1 / n:.0%})' + ('   <-- SOTTO IL 70%' if a / n < soglia else ''))
# anni "sospetti": valori ripetuti in modo anomalo (anni di default dei Fichiers fonciers)
ys = [f['properties']['y'] for f in feats if ok(f['properties']['y'])]
cnt = collections.Counter(ys)
with open(os.path.join(OUT, 'anni.txt'), 'w') as f:
    f.write(f'edifici {len(feats)}, con anno {len(ys)}\n')
    for a, b in ((1000, 1700), (1700, 1800), (1800, 1850), (1850, 1870), (1870, 1914), (1914, 1940), (1940, 1968), (1968, 2000), (2000, 2027)):
        f.write(f'{a}-{b - 1}: {sum(1 for v in ys if a <= v < b)}\n')
    f.write('anni piu\' frequenti (se uno solo pesa >10% e\' probabilmente un valore di default):\n')
    for y, n in cnt.most_common(12): f.write(f'  {y}: {n} ({n / max(1, len(ys)):.1%})\n')
log('FATTO:', len(feats), 'edifici; copertura in copertura.csv, distribuzione anni in anni.txt')
