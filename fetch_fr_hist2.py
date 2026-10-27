# Parigi, terzo giro (pod CPU, ~5 min): i DATI di Vasserot (il secondo giro aveva preso solo i metadati XML) e Merimee.
# Uso: python fetch_fr_hist2.py OUTDIR      -> OUTDIR/vasserot/*.zip, OUTDIR/merimee/*, OUTDIR/fonti3.log
import os, re, sys, zipfile, requests
OUT = sys.argv[1]; os.makedirs(OUT + '/vasserot', exist_ok=True); os.makedirs(OUT + '/merimee', exist_ok=True)
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0 city3d/1.0 (research timelapse)'
LOG = open(OUT + '/fonti3.log', 'a')
def log(*a):
    m = ' '.join(str(x) for x in a); print('[hist2]', m, flush=True); LOG.write(m + '\n'); LOG.flush()
def try_get(url, dst, need_zip=False):
    try:
        r = S.get(url, timeout=600, allow_redirects=True)
        if r.status_code != 200 or len(r.content) < 2000 or r.content[:15].lower().startswith((b'<!doctype', b'<html')):
            log(f'   no {r.status_code} {len(r.content)} B  {url}'); return False
        open(dst, 'wb').write(r.content)
        if need_zip and not zipfile.is_zipfile(dst): os.remove(dst); log('   non zip', url); return False
        log(f'   OK {len(r.content) >> 10} KB  {url}'); return True
    except Exception as e: log('   errore', url, e); return False

V = {'kk239hv5615': 'BATI', 'bz020fp6123': 'Vasserot_Ilots', 'db591kz1574': 'VASSEROT_VOIES',
     'qr091wq2775': 'Vasserots_parcelles2_v', 'pn650tp5621': 'Num_Voies_Vasserot'}
got = {}
for i, base in V.items():
    dst = f'{OUT}/vasserot/{i}__{base}.zip'
    cands = [f'https://stacks.stanford.edu/file/druid:{i}/data.zip', f'https://stacks.stanford.edu/file/druid:{i}/{base}.zip',
             f'https://stacks.stanford.edu/file/{i}/data.zip', f'https://earthworks.stanford.edu/download/file/stanford-{i}-shapefile.zip',
             f'https://earthworks.stanford.edu/download/stanford-{i}?type=shapefile']
    log(i, base)
    got[i] = any(try_get(u, dst, need_zip=True) for u in cands)
if not got.get('kk239hv5615'):   # ripiego: sito ALPAGE (Huma-Num)
    for p in ('http://alpage.huma-num.fr/en/resources/gis-data', 'https://alpage.huma-num.fr/en/resources/gis-data',
              'http://alpage.huma-num.fr/fr/ressources/donnees-sig', 'https://alpage.huma-num.fr/documents/'):
        try: t = S.get(p, timeout=60).text
        except Exception as e: log('ALPAGE non raggiungibile', p, e); continue
        links = set(re.findall(r'href=["\']([^"\']+\.zip)', t, re.I))
        log('ALPAGE', p, 'zip trovati:', len(links), sorted(links)[:30])
        for u in links:
            if re.search(r'bati|vasserot|vass|ilot|voie|parcel|alpage|sig', u, re.I):
                u = requests.compat.urljoin(p, u); try_get(u, f'{OUT}/vasserot/alpage__{os.path.basename(u)}', need_zip=True)
# Merimee: risorse del dataset su data.gouv (il portale culture ha cambiato indirizzo)
try:
    j = S.get('https://www.data.gouv.fr/api/1/datasets/', params={'q': 'immeubles protégés monuments historiques', 'page_size': 8}, timeout=60).json()
    for d in j.get('data', []):
        log('dataset:', d.get('title'), '|', d.get('organization', {}) and d['organization'].get('name'))
        for r in d.get('resources', []):
            f = (r.get('format') or '').lower(); u = r.get('url', '')
            if f in ('csv', 'json', 'geojson') and ('merimee' in (d.get('title', '') + u).lower() or 'monuments historiques' in d.get('title', '').lower()):
                try_get(u, f'{OUT}/merimee/{re.sub(r"[^A-Za-z0-9._-]+", "_", r.get("title") or "res")[:60]}.{f}')
except Exception as e: log('Merimee: errore', e)
log('RIEPILOGO Vasserot:', {V[k]: ('OK' if v else 'MANCA') for k, v in got.items()})
