# Danimarca, passo 1 (sul pod): ritaglia i punti BBR INSPIRE attorno al centro e li salva GREZZI (tutte le colonne).
# L'unione con le impronte, gli anni e lo strato storico si fanno dopo in chat (gratis).
# Uso: python fetch_dk_raw.py DK_INSPIRE_BBR.zip city_copenhagen.json uscita.geojson
import json, math, os, sys, zipfile, glob
import pyogrio
from pyproj import Transformer

SRC, CFG, OUT = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
LAT0, LON0 = CFG['lat0'], CFG['lon0']; R = CFG.get('radius_m', 9000) + 1000
def log(*a): print('[fetch_dk_raw]', *a, flush=True)

# 1) trova il GeoPackage (dentro lo zip, anche annidato)
work = os.path.splitext(SRC)[0] + '_x'
if SRC.lower().endswith('.zip'):
    if not glob.glob(work + '/**/*.gpkg', recursive=True):
        log('estraggo', SRC); zipfile.ZipFile(SRC).extractall(work)
    for z in glob.glob(work + '/**/*.zip', recursive=True):
        zipfile.ZipFile(z).extractall(z[:-4]); os.remove(z)
    gp = sorted(glob.glob(work + '/**/*.gpkg', recursive=True), key=os.path.getsize, reverse=True)
else:
    gp = [SRC]
if not gp: log('NESSUN .gpkg trovato. Contenuto:', os.listdir(work)); sys.exit(1)
GP = gp[0]; log('file:', GP, f'{os.path.getsize(GP) >> 20} MB')

# 2) elenca i layer e le colonne (serve per scrivere l'unione in chat)
layers = pyogrio.list_layers(GP)
log('layer:', [(str(n), str(t)) for n, t in layers])
info_all = {}
for name, gtype in layers:
    inf = pyogrio.read_info(GP, layer=name)
    info_all[str(name)] = {'geom': str(gtype), 'crs': str(inf['crs']), 'n': int(inf['features']), 'fields': [str(f) for f in inf['fields']]}
    log(' ', name, gtype, inf['crs'], inf['features'], 'righe')
    log('   campi:', list(inf['fields']))

# 3) ritaglia ogni layer con geometria entro R dal centro; i layer senza geometria si salvano interi se piccoli
outdir = os.path.dirname(os.path.abspath(OUT)); stem = os.path.splitext(os.path.basename(OUT))[0]
for name, gtype in layers:
    name = str(name); inf = info_all[name]
    if gtype is None or str(gtype) in ('None', ''):
        if inf['n'] < 300000:
            df = pyogrio.read_dataframe(GP, layer=name, read_geometry=False)
            df.to_csv(f'{outdir}/{stem}_{name}.csv.gz', index=False)
            log('  tabella', name, len(df), 'righe salvate')
        else:
            log('  tabella', name, 'troppo grande, saltata (', inf['n'], ')')
        continue
    crs = inf['crs']
    tr = Transformer.from_crs('EPSG:4326', crs, always_xy=True)
    dla = R / 110540; dlo = R / (math.cos(math.radians(LAT0)) * 111320)
    xs, ys = tr.transform([LON0 - dlo, LON0 + dlo, LON0 - dlo, LON0 + dlo], [LAT0 - dla, LAT0 - dla, LAT0 + dla, LAT0 + dla])
    bbox = (min(xs), min(ys), max(xs), max(ys))
    df = pyogrio.read_dataframe(GP, layer=name, bbox=bbox)
    if df.crs is not None and str(df.crs) != 'EPSG:4326': df = df.to_crs('EPSG:4326')
    path = OUT if len(layers) == 1 else f'{outdir}/{stem}_{name}.geojson'
    for c in df.columns:   # date/oggetti -> testo, cosi' il GeoJSON si scrive sempre
        if c != 'geometry' and str(df[c].dtype) not in ('int64', 'float64', 'int32', 'float32', 'bool'):
            df[c] = df[c].astype(str)
    pyogrio.write_dataframe(df, path, driver='GeoJSON')
    log(f'  {name}: {len(df)} elementi nel riquadro -> {path}')
    # anteprima anni, se c'e' una colonna che sembra l'anno di costruzione
    yc = [c for c in df.columns if 'cons' in c.lower() or 'opf' in c.lower() or 'year' in c.lower() or 'aar' in c.lower()]
    for c in yc[:3]:
        v = df[c].astype(str).str[:4]; v = v[v.str.isdigit()].astype(int)
        if len(v):
            bins = [(0, 1001), (1001, 1700), (1700, 1800), (1800, 1850), (1850, 1900), (1900, 1945), (1945, 1980), (1980, 2027)]
            log(f'   anni da {c}:', {f'{a}-{b - 1}': int(((v >= a) & (v < b)).sum()) for a, b in bins})
json.dump(info_all, open(f'{outdir}/{stem}_schema.json', 'w'), indent=1)
log('FATTO')
