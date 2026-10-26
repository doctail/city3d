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
def log(*a): print('[fetch_fr]', *a, flush=True)

if MODE == 'urls':
    import requests
    deps = [str(d) for d in CFG['bdnb_deps']]
    api = 'https://www.data.gouv.fr/api/1/datasets/'
    res = []
    for slug in CFG.get('bdnb_datasets', ['base-de-donnees-nationale-des-batiments']):
        try:
            j = requests.get(api + slug + '/', timeout=60).json(); res += j.get('resources', [])
        except Exception as e: log('dataset', slug, 'non letto:', e)
    if not res:   # ripiego: ricerca
        j = requests.get(api, params={'q': 'BDNB open data', 'page_size': 10}, timeout=60).json()
        for d in j.get('data', []): res += d.get('resources', [])
    for d in deps:
        c = [r for r in res if f'dep{d}' in (r.get('url', '') + r.get('title', '')).lower().replace('_', '')
             and 'gpkg' in (r.get('url', '') + r.get('title', '') + r.get('format', '')).lower()]
        c.sort(key=lambda r: r.get('last_modified') or '', reverse=True)
        if not c: log('NESSUN GPKG per il dipartimento', d); continue
        print(c[0]['url'])
    sys.exit(0)

import numpy as np, pyogrio, shapely
from pyproj import Transformer
OUT = sys.argv[3]; SRC = sys.argv[4:]
os.makedirs(OUT, exist_ok=True)
YC = ('annee_construction', 'ffo_bat_annee_construction', 'annee_construction_ffo')
LC = ('nb_niveau', 'ffo_bat_nb_niveau', 'nb_niveau_ffo')
HC = ('hauteur_mean', 'bdtopo_bat_hauteur_mean', 'hauteur', 'hauteur_moyenne')
ID = 'batiment_groupe_id'

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
    geo = next((l for l in layers if l == 'batiment_groupe'), None) or next((l for l in layers if 'batiment_groupe' in l and pyogrio.read_info(path, layer=l)['geometry_type']), None)
    ffo = next((l for l in layers if 'ffo_bat' in l), None)
    bdt = next((l for l in layers if 'bdtopo_bat' in l), None)
    crs = pyogrio.read_info(path, layer=geo)['crs'] if geo else None
    log(os.path.basename(path), '| geometria:', geo, crs, '| anno:', ffo, '| altezza:', bdt)
    if not geo: log('ERRORE: nessuno strato con geometria; vedi schema.txt'); sys.exit(2)
    to_loc = Transformer.from_crs('EPSG:4326', crs, always_xy=True)
    to_ll = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
    CX, CY = to_loc.transform(LON0, LAT0)
    keep = [c for c in (ID, 'code_commune_insee', 'libelle_commune_insee') if c in cols[geo]]
    keep += [c for c in (pick(cols[geo], YC), pick(cols[geo], LC), pick(cols[geo], HC)) if c]
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
        geom = shapely.transform(geom, lambda xy: np.c_[to_ll.transform(xy[:, 0], xy[:, 1])])
        feats.append({'type': 'Feature', 'geometry': shapely.geometry.mapping(geom),
                      'properties': {'id': i, 'insee': r.get('code_commune_insee'), 'y': int(y) if y else None,
                                     'lev': int(lev) if lev is not None else None, 'h': round(h, 1) if h else None}})
schema.close()
with gzip.open(os.path.join(OUT, 'bdnb.geojson.gz'), 'wt') as f:
    json.dump({'type': 'FeatureCollection', 'features': feats}, f)

# --- copertura: anno valido = 1000..2026 ---
ok = lambda y: y is not None and 1000 <= y <= 2026
per = collections.defaultdict(lambda: [0, 0])
for f in feats:
    p = f['properties']; k = str(p['insee'] or '?'); per[k][0] += 1; per[k][1] += ok(p['y'])
soglia = CFG.get('coverage_min', 0.70)
with open(os.path.join(OUT, 'copertura.csv'), 'w') as f:
    f.write('insee,zona,edifici,con_anno,quota,sotto_soglia\n')
    for k in sorted(per):
        n, a = per[k]; z = f'{int(k) - 75100}e arr.' if k.startswith('751') and len(k) == 5 else 'fuori Parigi'
        f.write(f'{k},{z},{n},{a},{a / n:.3f},{"SI" if a / n < soglia else ""}\n')
par = {k: v for k, v in per.items() if k.startswith('751')}
log('arrondissement trovati:', len(par), '/ 20')
for k in sorted(par):
    n, a = par[k]; log(f'  {int(k) - 75100:2d}e: {a}/{n} = {a / n:.0%}' + ('   <-- SOTTO IL 70%' if a / n < soglia else ''))
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
