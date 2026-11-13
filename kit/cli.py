"""Kit Year Built: un comando per ogni passo di una citta'.

Uso (dalla radice del repo, con il python che ha shapely/numpy/scipy/PIL; bpy solo per qa --render):
    /home/user/bl/bin/python -m kit <comando> <slug> [opzioni]

Comandi
  init <slug>        crea cities/<slug>/story.json dal modello (non sovrascrive) e cities/<slug>/qa/
  data <slug>        controlla la cartella DATA e indica lo script di acquisizione per city.data_source
  build <slug>       hist stub + hist -> landmarks -> city json -> regia -> eventi/labs (se i moduli ci sono)
  qa <slug> [--render]   controlli automatici (kit/qa.py), report in cities/<slug>/qa/REPORT.md
  pack <slug>        comprime DATA in data_<slug>_src/*.gz (come le altre citta': run.sh li scompatta sul pod)
  montaggio <slug> [--A a.mp3 --B b.mp3] [--overlay]   montaggio/kit_city.py, sfx_kit.py (se ci sono i brani), ov_kit.sh
  all <slug> [--render]  data -> build -> qa -> pack
Ogni passo stampa tempo ed esito; ci si ferma al primo FAIL (codice di uscita 1).
"""
import gzip, json, os, shutil, subprocess, sys, time

from . import geo

PY = sys.executable
ACQ = {   # city.data_source -> come ottenere DATA (gli script esistenti scrivono buildings.json ecc.)
    'catastro': ['python fetch_es.py DATA city_<slug>.json [A.ES.SDGC.BU.<cod>.zip]   (Catastro INSPIRE: edifici con anno; '
                 'chiave catastro_zip nel city json / story.city)',
                 'roads.json obbligatorio: estrai le highway OSM come fetch_dk_roads.py (nastri gia\' poligonali, y = urbanizzazione)'],
    'bbr': ['python fetch_dk_raw.py / osm_dk_raw.py <pbf> city_<slug>.json raw/osm   (impronte OSM)',
            'python fetch_dk.py RAW DATA city_<slug>.json   (BBR: anno per edificio)',
            'python fetch_dk_roads.py RAW DATA city_<slug>.json   (roads.json)'],
    'bag': ['python fetch_nl.py DATA city_<slug>.json [3dbag-lod13.parquet]   (BAG/3DBAG: anno + altezza)',
            'roads.json obbligatorio: highway OSM come fetch_dk_roads.py'],
    'osm': ['python osm_dk_raw.py <file.osm.pbf> city_<slug>.json raw/osm   (impronte + ambiente da Geofabrik)',
            'anni per zona: script prep come prep_roma.py (ISTAT) o urban_grid; roads.json come fetch_dk_roads.py'],
    'custom': ['DATA preparata a mano: buildings.json, roads.json, land.json, dem.npz (schemi: city3d_kit_spec.md §4)'],
}
NEED = ['buildings.json', 'roads.json', 'land.json', 'dem.npz']
PACK_SKIP = {'hist.json', 'urban_kit.json', 'landmarks_walls.json', 'buildings_catastro_raw.json', 'land_v3.ok'}

MODEL = {
    "version": 1,
    "city": {"slug": "", "name": "", "country": "", "lat0": 0.0, "lon0": 0.0, "radius_m": 9000,
             "start_year": 1200, "end_year": 2026, "title": "EVOLUTION OF <CITY> | 3D City Timelapse (<YEAR>–NOW) | No AI",
             "data_source": "catastro", "style_preset": "mediterranean",
             "population": [], "pop_src": [], "eras": []},
    "sources": {},
    "history": {"zones": [], "walls": [], "gutting": [], "lost": [], "fires": [], "water": [], "bridges": []},
    "landmarks": [],
    "regia": {"camera": "drone", "music": "waking_monument", "duration": 300.0, "night": True, "open": {"year": 2026, "rewind_to": 1200},
              "soste": [], "rmin": 0.5, "rmax": 8.0},
    "montaggio": {"open": [], "title": [], "end": [], "events": []},
}


class Fail(Exception):
    pass


def step(name, fn, *a):
    t = time.time(); print(f'\n=== {name} ===', flush=True)
    try:
        r = fn(*a)
    except Fail as e:
        print(f'=== {name}: FAIL ({time.time() - t:.0f} s) — {e}', flush=True); raise
    except Exception as e:
        print(f'=== {name}: FAIL ({time.time() - t:.0f} s) — {type(e).__name__}: {e}', flush=True); raise Fail(str(e))
    print(f'=== {name}: {r or "OK"} ({time.time() - t:.0f} s)', flush=True)
    return r


def sh(cmd, env=None):
    print('  $', ' '.join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=geo.ROOT, env=dict(os.environ, **(env or {})))
    if p.returncode != 0: raise Fail(f'comando uscito con {p.returncode}: {" ".join(cmd[:4])}')


def _mod_exists(m):
    return os.path.exists(os.path.join(geo.ROOT, *m.split('.')) + '.py')


# ------------------------------------------------------------------------------------------------ comandi
def cmd_init(slug, opts):
    d = os.path.join(geo.ROOT, 'cities', slug); os.makedirs(os.path.join(d, 'qa'), exist_ok=True)
    p = os.path.join(d, 'story.json')
    if os.path.exists(p): return f'{os.path.relpath(p, geo.ROOT)} esiste gia\' (non toccato)'
    m = json.loads(json.dumps(MODEL)); m['city']['slug'] = slug; m['city']['name'] = slug.capitalize()
    json.dump(m, open(p, 'w'), indent=1, ensure_ascii=False)
    return f'scritto {os.path.relpath(p, geo.ROOT)}: compilalo seguendo kit/STORY_SCHEMA.md'


def cmd_data(slug, opts):
    st = geo.load_story(slug); D = opts.get('data') or geo.data_dir(st); src = st['city'].get('data_source', 'custom')
    print(f'  DATA = {os.path.relpath(D, geo.ROOT)}  (data_source: {src})')
    for line in ACQ.get(src, ACQ['custom']): print('  -', line.replace('<slug>', slug))
    gz = os.path.join(geo.ROOT, f'data_{slug}_src')
    if not os.path.isdir(D) and os.path.isdir(gz):
        print(f'  DATA assente: la ricostruisco da {os.path.basename(gz)}'); os.makedirs(D, exist_ok=True)
        for f in os.listdir(gz):
            if f.endswith('.gz') and not os.path.exists(os.path.join(D, f[:-3])):
                with gzip.open(os.path.join(gz, f)) as i, open(os.path.join(D, f[:-3]), 'wb') as o: shutil.copyfileobj(i, o)
    miss = [f for f in NEED if not os.path.exists(os.path.join(D, f))]
    hard = [f for f in miss if f in ('buildings.json', 'roads.json')]
    if hard: raise Fail('mancano ' + ', '.join(hard) + ' in DATA: lancia gli script qui sopra (roads.json e\' obbligatorio)')
    return 'OK' + (f' (mancano anche {", ".join(miss)}: WARN)' if miss else '')


def cmd_build(slug, opts):
    st = geo.load_story(slug); D = opts.get('data') or geo.data_dir(st)
    if not os.path.isdir(D): raise Fail(f'DATA {D} assente: python -m kit data {slug}')
    stub = os.path.join(geo.ROOT, f'hist_{slug}.py')
    step('build 1/5 hist (stub + predecessori)', lambda: (
        os.path.exists(stub) or sh([PY, '-m', 'kit.hist_kit', 'make-stub', slug]),
        sh([PY, '-m', 'kit.hist_kit', 'build', slug, D]))[-1])
    if _mod_exists('kit.landmarks_kit'): step('build 2/5 landmarks', sh, [PY, '-m', 'kit.landmarks_kit', 'build', slug, D])
    elif st.get('landmarks'): raise Fail('kit/landmarks_kit.py non c\'e\' e la story ha landmarks')
    from . import city_json
    step('build 3/5 city json', lambda: city_json.write(slug, force=opts.get('force') is not None)[0])
    if not _mod_exists('kit.regia_kit'): raise Fail('kit/regia_kit.py non c\'e\'')
    step('build 4/5 regia', sh, [PY, '-m', 'kit.regia_kit', slug, '--data', D])
    city_json.write(slug)   # rigenera: shorts con regia propria se la regia l'ha scritta
    for m, args in (('kit.eventi_kit', [slug]), ('kit.labs_kit', [slug])):
        if _mod_exists(m): step(f'build 5/5 {m.split(".")[1]}', sh, [PY, '-m', m] + args)
        else: print(f'  ({m} non presente: passo saltato)')
    return 'OK'


def cmd_qa(slug, opts):
    from . import qa
    R = qa.run(slug, data=opts.get('data'), render='render' in opts)
    w = R.worst()
    if w == 'FAIL':
        bad = [f'{r[0]}) {r[2]}' for r in R.rows if r[1] == 'FAIL']
        raise Fail(f'{len(bad)} controlli FAIL: ' + '; '.join(bad[:6]) + f' — cities/{slug}/qa/REPORT.md')
    return w


def cmd_pack(slug, opts):
    st = geo.load_story(slug); D = opts.get('data') or geo.data_dir(st)
    out = os.path.join(geo.ROOT, f'data_{slug}_src'); os.makedirs(out, exist_ok=True)
    n, tot, big = 0, 0, []
    for f in sorted(os.listdir(D)):
        p = os.path.join(D, f)
        if f in PACK_SKIP or f.endswith('_stats.json') or '.bak' in f or not (f.endswith('.json') or f.endswith('.npz')) or not os.path.isfile(p): continue
        g = os.path.join(out, f + '.gz')
        if os.path.exists(g) and os.path.getmtime(g) >= os.path.getmtime(p): tot += os.path.getsize(g); n += 1; continue
        with open(p, 'rb') as i, gzip.GzipFile(g, 'wb', compresslevel=9, mtime=0) as o: shutil.copyfileobj(i, o)
        s = os.path.getsize(g); tot += s; n += 1
        if s > 95e6: big.append(f)
        print(f'  {f} -> {os.path.relpath(g, geo.ROOT)} ({s / 1e6:.1f} MB)')
    if big: raise Fail('file oltre 95 MB (limite GitHub 100 MB): ' + ', '.join(big))
    return f'{n} file, {tot / 1e6:.1f} MB in {os.path.relpath(out, geo.ROOT)} (hist.json si rigenera sul pod)'


def cmd_montaggio(slug, opts):
    m = os.path.join(geo.ROOT, 'montaggio')
    step('montaggio 1/3 kit_city', sh, [PY, os.path.join(m, 'kit_city.py'), slug])
    if opts.get('A'):
        a = [PY, os.path.join(m, 'sfx_kit.py'), slug, '--A', opts['A']] + (['--B', opts['B']] if opts.get('B') else [])
        step('montaggio 2/3 audio (sfx_kit)', sh, a)
    else: print('  audio saltato: passa --A waking.mp3 [--B monument.mp3]')
    if 'overlay' in opts: step('montaggio 3/3 overlay (ov_kit.sh)', sh, ['bash', os.path.join(m, 'ov_kit.sh'), slug, 'long'])
    else: print(f'  overlay: bash montaggio/ov_kit.sh {slug} long  (lungo: aggiungi --overlay)')
    return 'OK'


def cmd_all(slug, opts):
    for n, f in (('data', cmd_data), ('build', cmd_build), ('qa', cmd_qa), ('pack', cmd_pack)): step(n, f, slug, opts)
    return 'OK'


CMDS = {'init': cmd_init, 'data': cmd_data, 'build': cmd_build, 'qa': cmd_qa, 'pack': cmd_pack, 'montaggio': cmd_montaggio, 'all': cmd_all}


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) < 2 or a[0] not in CMDS: print(__doc__); return 2
    opts = {}; i = 2
    while i < len(a):
        k = a[i].lstrip('-')
        if i + 1 < len(a) and not a[i + 1].startswith('--'): opts[k] = a[i + 1]; i += 2
        else: opts[k] = True; i += 1
    T = time.time()
    try:
        step(f'{a[0]} {a[1]}', CMDS[a[0]], a[1], opts)
    except Fail:
        print(f'\nFERMO al primo FAIL ({time.time() - T:.0f} s)'); return 1
    print(f'\nFATTO in {time.time() - T:.0f} s'); return 0
