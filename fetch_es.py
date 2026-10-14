# Spagna: edifici dal Catasto (INSPIRE BU) -> formato di build_render.py
# Uso: python fetch_es.py DATA_DIR city_madrid.json [file.zip]
#   senza zip lo scarica da cfg['catastro_zip'] (dal pod; dal sandbox il sito e' bloccato)
# Uscita: DATA/buildings.json [{"r": [[x,y],...], "h": m, "y": anno}], DATA/land.json (quadrato attorno al centro)
# Anno: bu-core2d:dateOfConstruction/end (fine costruzione). Altezza: piani fuori terra (max delle building part) x 3,1 m + 1.
import io, json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET

DATA, CFG = sys.argv[1], json.load(open(sys.argv[2])); ZIP = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(DATA, exist_ok=True)
LAT0, LON0 = CFG['lat0'], CFG['lon0']; KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
R = CFG.get('radius_m', 14000)   # tieni solo gli edifici entro questo raggio dal centro
def log(*a): print('[fetch_es]', *a, flush=True)

from pyproj import Transformer
TR = {}
def to_local(xs, ys, epsg):
    if epsg not in TR: TR[epsg] = Transformer.from_crs(f'EPSG:{epsg}', 'EPSG:4326', always_xy=True)
    lo, la = TR[epsg].transform(xs, ys)
    return [[round((o - LON0) * KX, 2), round((a - LAT0) * KY, 2)] for o, a in zip(lo, la)]

def open_zip():
    if ZIP: return zipfile.ZipFile(ZIP)
    import requests
    url = CFG['catastro_zip']; log('scarico', url)
    r = requests.get(url, timeout=600, headers={'User-Agent': 'city3d/1.0'}); r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def local(tag): return tag.rsplit('}', 1)[-1]
def iter_features(zf, suffix, want):
    name = [n for n in zf.namelist() if n.lower().endswith(suffix)][0]; log('leggo', name)
    with zf.open(name) as f:
        for ev, el in ET.iterparse(f, events=('end',)):
            if local(el.tag) == want: yield el; el.clear()

def parse_geom(el):
    # primo anello esterno; srsName -> EPSG
    pl = None; epsg = 25830
    for e in el.iter():
        t = local(e.tag)
        if 'srsName' in e.attrib:
            m = re.search(r'(\d{4,5})$', e.attrib['srsName']); epsg = int(m.group(1)) if m else epsg
        if t == 'posList' and pl is None: pl = e.text
        if t == 'interior': break
    if not pl: return None, epsg
    v = list(map(float, pl.split())); return (v[0::2], v[1::2]), epsg

zf = open_zip()
floors = {}
for el in iter_features(zf, 'buildingpart.gml', 'BuildingPart'):
    gid = el.attrib.get('{http://www.opengis.net/gml/3.2}id', '')
    bid = gid.split('_part')[0].replace('ES.SDGC.BU.', '').strip()
    n = 0
    for e in el.iter():
        if local(e.tag) == 'numberOfFloorsAboveGround' and e.text:
            try: n = int(float(e.text))
            except ValueError: pass
    floors[bid] = max(floors.get(bid, 0), n)
log('parti con piani:', len(floors))

out = []; noyear = 0
for el in iter_features(zf, 'building.gml', 'Building'):
    gid = el.attrib.get('{http://www.opengis.net/gml/3.2}id', '').replace('ES.SDGC.BU.', '').strip()
    y = 0
    for e in el.iter():
        if local(e.tag) == 'end' and e.text and e.text[:4].isdigit(): y = int(e.text[:4]); break
    g, epsg = parse_geom(el)
    if not g or len(g[0]) < 4: continue
    ring = to_local(g[0][:-1], g[1][:-1], epsg)
    cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring)
    if cx * cx + cy * cy > R * R: continue
    f_ = floors.get(gid, 0)
    if not y or y < 1000 or y > 2026:
        noyear += 1; y = 0
        if not f_: continue   # senza anno e senza piani: tettoie, ruderi, piccole costruzioni
    out.append({'r': ring, 'h': round(f_ * 3.1 + 1.0, 1) if f_ else 0, 'y': y})
log('edifici:', len(out), '| senza anno:', noyear)

# anni o altezze mancanti: stima prudente (come fetch_nyc.fill_missing)
import random
rnd = random.Random(5)
for b in out:
    if not b['h'] or b['h'] < 3: b['h'] = round(rnd.uniform(6, 12), 1)
    if not b['y']: b['y'] = int(rnd.uniform(1950, 1990))
json.dump(out, open(f'{DATA}/buildings.json', 'w'))
L = CFG.get('land_half_m', 30000)
json.dump([[[-L, -L], [L, -L], [L, L], [-L, L]]], open(f'{DATA}/land.json', 'w')); open(f'{DATA}/land_v3.ok', 'w').write('ok')
ys = sorted(b['y'] for b in out)
log(f'FATTO: {len(out)} edifici, anni {ys[0]}..{ys[-1]}, mediana {ys[len(ys)//2]}')
