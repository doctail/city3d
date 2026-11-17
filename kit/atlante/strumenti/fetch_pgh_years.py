# Pittsburgh: anni di costruzione ESTERNI per il centro (Golden Triangle), dove il catasto (assessments) non ha YEARBLT (CLASS C/G: ~1-3%).
# Fonti gratis e raggiungibili dal sandbox (verificato 2026-11-17): Wikipedia (CC BY-SA) "List of tallest buildings in Pittsburgh" (nome, coord, altezza, piani, anno)
# + Wikidata SPARQL (CC0): edifici entro 1,6 km dal Point con inception P571 / opening P1619. Coordinate Wikidata spesso approssimate (NRHP): il match nel
# fetch_pgh.py e' punto-in-poligono, altrimenti il footprint piu' vicino entro 12 m.
# Uso:  python fetch_pgh_years.py OUT.csv      -> colonne: src,name,lat,lon,year,height_m,floors,wikidata
# Poi:  PGH_EXT_YEARS=OUT.csv python fetch_pgh.py RAW DATA buildings   (default = invariato, senza la variabile)
import csv, json, re, subprocess, sys, urllib.parse
UA = 'yb-research/1.0'
def curl(args):
    r = subprocess.run(['curl', '-sS', '-f', '-m', '120', '-A', UA] + args, capture_output=True, text=True)
    if r.returncode: raise SystemExit('curl fallito: ' + r.stderr[:200])
    return r.stdout
def tall():
    u = 'https://en.wikipedia.org/w/api.php?action=parse&page=List_of_tallest_buildings_in_Pittsburgh&prop=wikitext&format=json&formatversion=2'
    w = json.loads(curl([u]))['parse']['wikitext']; out = []
    for sec in w.split('\n|-')[1:]:
        m = re.search(r'\{\{[Cc]oord\|([-\d.]+)\|([-\d.]+)', sec)
        if not m: continue
        cells = [c.strip() for c in re.split(r'\n\|(?!\|)', sec)]
        nm = re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', ' '.join(cells[2:3]))
        h = re.search(r'\{\{convert\|([\d.]+)\|(m|ft)', sec); hm = float(h.group(1)) * (0.3048 if h.group(2) == 'ft' else 1) if h else ''
        fl = re.search(r'\n\|\s*(\d{1,3})\s*\n\|\s*(\d{4})\s*\n', sec[m.end():])
        if fl: out.append(['wiki_tall', (nm.group(2) or nm.group(1)) if nm else '', m.group(1), m.group(2), fl.group(2), round(hm, 1) if hm != '' else '', fl.group(1), ''])
    return out
def wikidata(radius_km=1.6):
    q = ('SELECT ?i ?l ?c ?inc ?op ?h ?fl WHERE { SERVICE wikibase:around { ?i wdt:P625 ?c . bd:serviceParam wikibase:center "Point(-80.0 40.4406)"^^geo:wktLiteral . '
         'bd:serviceParam wikibase:radius "%s" . } ?i wdt:P31/wdt:P279* wd:Q41176 . OPTIONAL{?i wdt:P571 ?inc} OPTIONAL{?i wdt:P1619 ?op} OPTIONAL{?i wdt:P2048 ?h} '
         'OPTIONAL{?i wdt:P1101 ?fl} ?i rdfs:label ?l FILTER(LANG(?l)="en") }' % radius_km)
    j = json.loads(curl(['-G', '-H', 'Accept: application/sparql-results+json', 'https://query.wikidata.org/sparql', '--data-urlencode', 'query=' + q]))
    out = {}
    for r in j['results']['bindings']:
        g = lambda k: r[k]['value'] if k in r else ''
        y = (g('inc') or g('op'))[:4]
        m = re.search(r'Point\(([-\d.]+) ([-\d.]+)\)', g('c'))
        if not (y.isdigit() and m): continue
        out[g('i').split('/')[-1]] = ['wikidata', g('l'), m.group(2), m.group(1), y, g('h'), g('fl'), g('i').split('/')[-1]]
    return list(out.values())
if __name__ == '__main__':
    rows = tall() + wikidata()
    with open(sys.argv[1], 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['src', 'name', 'lat', 'lon', 'year', 'height_m', 'floors', 'wikidata']); w.writerows(rows)
    print(f'{len(rows)} righe ({sum(r[0] == "wiki_tall" for r in rows)} wiki_tall, {sum(r[0] == "wikidata" for r in rows)} wikidata) -> {sys.argv[1]}')
