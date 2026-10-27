# Parigi, secondo giro sul pod CPU: fonti storiche e di dettaglio. Ogni fonte e' indipendente: se fallisce lo scrive
# in OUT/fonti.log e passa alla successiva (niente stop). Uscita in OUT/ (poi data_fr2.sh fa il tgz).
#  1. Vasserot 1810-1836 vettorializzato (ALPAGE, ODbL) da Stanford: tutti i layer trovati cercando "Vasserot"
#  2. alberi di Parigi (opendata.paris.fr, ~200.000 alberi) e arrondissement (confini)
#  3. vie di Parigi con storico (denominations-emprises-voies-actuelles: date di apertura/classamento)
#  4. monumenti storici (Merimee, data.culture.gouv.fr) dentro il raggio
#  5. Wikidata: edifici di Parigi con data di costruzione (P571) e di demolizione (P576), con coordinate
#  6. mappe storiche per il confronto della Fase 3 (Wikimedia Commons: Turgot 1739, Vasserot, Haussmann ~1870)
# Uso: python fetch_fr_hist.py city_parigi.json OUTDIR
import json, math, os, re, sys, time, traceback
import requests

CFG, OUT = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(OUT, exist_ok=True)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; R = CFG.get('clip_radius_m', 11000)
S = requests.Session(); S.headers['User-Agent'] = 'city3d/1.0 (research timelapse; github.com/doctail/city3d)'
LOG = open(os.path.join(OUT, 'fonti.log'), 'a')
def log(*a):
    m = ' '.join(str(x) for x in a); print('[hist]', m, flush=True); LOG.write(m + '\n'); LOG.flush()

def get(url, dst, **kw):
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return dst
    with S.get(url, stream=True, timeout=kw.pop('timeout', 600), **kw) as r:
        r.raise_for_status()
        with open(dst + '.part', 'wb') as f:
            for ch in r.iter_content(1 << 20): f.write(ch)
    os.replace(dst + '.part', dst); return dst

def step(name):
    def deco(fn):
        t = time.time()
        try: fn(); log(f'OK   {name} ({time.time() - t:.0f} s)')
        except Exception as e:
            log(f'FAIL {name}: {e!r}'); LOG.write(traceback.format_exc() + '\n')
        return fn
    return deco

@step('Vasserot (Stanford)')
def vasserot():
    d = os.path.join(OUT, 'vasserot'); os.makedirs(d, exist_ok=True)
    ids = {'qr091wq2775', 'bz020fp6123', 'pn650tp5621', 'kk239hv5615', 'db591kz1574'}
    for q in ('vasserot', 'alpage paris'):   # cerca altri layer (edifici, isolati, strade) nel catalogo EarthWorks
        for u in (f'https://earthworks.stanford.edu/?q={q}&per_page=100', f'https://earthworks.stanford.edu/catalog.json?q={q}&per_page=100'):
            try:
                t = S.get(u, timeout=60).text; ids |= set(re.findall(r'stanford-([a-z]{2}\d{3}[a-z]{2}\d{4})', t))
            except Exception as e: log('  ricerca EarthWorks non riuscita:', u, e)
    log('  layer candidati:', len(ids), sorted(ids))
    for i in sorted(ids):
        try:
            x = S.get(f'https://purl.stanford.edu/{i}.xml', timeout=60).text
            title = (re.search(r'<title>([^<]+)</title>', x) or re.search(r'<dc:title>([^<]+)', x) or [None, '?'])[1]
            if 'vasserot' not in title.lower() and 'alpage' not in x.lower() and 'paris' not in title.lower():
                log(f'  {i}: "{title}" non e\' Parigi, salto'); continue
            files = sorted(set(re.findall(r'<file[^>]*\sid="([^"]+)"', x)))
            files = [f for f in files if f.lower().endswith(('.zip', '.json', '.geojson', '.xml'))] or ['data.zip']
            for f in files:
                get(f'https://stacks.stanford.edu/file/druid:{i}/{f}', os.path.join(d, f'{i}__{f}'))
            log(f'  {i}: "{title}" -> {files}')
        except Exception as e: log(f'  {i}: errore {e!r}')

OD = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/{}/exports/geojson'
@step('alberi di Parigi')
def arbres(): get(OD.format('les-arbres'), os.path.join(OUT, 'paris_arbres.geojson'), timeout=1800)
@step('arrondissement')
def arr(): get(OD.format('arrondissements'), os.path.join(OUT, 'paris_arrondissements.geojson'))
@step('vie con storico')
def voies():
    get(OD.format('denominations-emprises-voies-actuelles'), os.path.join(OUT, 'paris_voies.geojson'), timeout=1800)
    get('https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/denominations-des-voies-actuelles/exports/csv?delimiter=%3B',
        os.path.join(OUT, 'paris_voies_storico.csv'))

@step('Merimee (monumenti storici)')
def merimee():
    base = 'https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/'
    for ds in ('liste-des-immeubles-proteges-au-titre-des-monuments-historiques', 'base-merimee'):
        for dep in ('Paris', 'Hauts-de-Seine', 'Seine-Saint-Denis', 'Val-de-Marne'):
            u = base + ds + '/exports/json?refine=departement_en_lettres:' + requests.utils.quote(dep)
            try: get(u, os.path.join(OUT, f'merimee_{ds[:12]}_{dep[:5]}.json'))
            except Exception as e: log('  ', ds, dep, e)

WQ = 'https://query.wikidata.org/sparql'
def sparql(q, dst):
    r = S.get(WQ, params={'query': q, 'format': 'json'}, timeout=300); r.raise_for_status()
    open(dst, 'w').write(r.text); return len(r.json()['results']['bindings'])
@step('Wikidata')
def wikidata():
    # tutto cio' che ha coordinate entro R dal centro e una data (ricerca per raggio: piu' leggera di P131*)
    km = round(R / 1000 + 0.5, 1)
    for nome, prop in (('costruzione', 'P571'), ('demolizione', 'P576'), ('apertura', 'P1619')):
        q = f'''SELECT ?item ?itemLabel ?coord ?date ?h ?type ?typeLabel WHERE {{
          SERVICE wikibase:around {{ ?item wdt:P625 ?coord. bd:serviceParam wikibase:center "Point({LON0} {LAT0})"^^geo:wktLiteral; wikibase:radius "{km}". }}
          ?item wdt:{prop} ?date.
          OPTIONAL {{ ?item wdt:P2048 ?h }} OPTIONAL {{ ?item wdt:P31 ?type }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en". }} }}'''
        n = sparql(q, os.path.join(OUT, f'wikidata_{nome}.json')); log(f'  {nome} ({prop}): {n} righe')

@step('mappe storiche (Commons)')
def mappe():
    d = os.path.join(OUT, 'mappe'); os.makedirs(d, exist_ok=True)
    api = 'https://commons.wikimedia.org/w/api.php'
    for term in ('Plan de Turgot 1739', 'Atlas Vasserot', 'Plan de Paris 1870 Haussmann', 'Plan de Paris Verniquet', 'Plan de Paris 1550 Truschet Hoyau'):
        r = S.get(api, params={'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': term, 'gsrnamespace': 6,
                               'gsrlimit': 6, 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'iiurlwidth': 4000}, timeout=60).json()
        for p in (r.get('query', {}).get('pages', {}) or {}).values():
            ii = (p.get('imageinfo') or [{}])[0]; u = ii.get('thumburl') or ii.get('url')
            if not u or ii.get('width', 0) < 1500: continue
            lic = (ii.get('extmetadata', {}).get('LicenseShortName') or {}).get('value', '?')
            fn = re.sub(r'[^A-Za-z0-9._-]+', '_', p['title'].replace('File:', ''))[:90]
            get(u, os.path.join(d, fn)); log(f'  {term}: {p["title"]} ({ii.get("width")}px, {lic})')

LOG.close()
