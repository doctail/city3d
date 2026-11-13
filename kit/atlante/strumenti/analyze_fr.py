import sys, json, glob, collections, math
sys.path.insert(0, '/tmp/claude-0/-home-user/f79f9b62-91b7-5c36-b63d-4d8dc6aaeafb/scratchpad/bdnb')
from measure_fr import lam93, CITY_OF
REF = {'Lione': (45.7676, 4.8355), 'Marsiglia': (43.2950, 5.3742), 'Bordeaux': (44.8378, -0.5792),
       'Tolosa': (43.6045, 1.4440), 'Nantes': (47.2151, -1.5566), 'Strasburgo': (48.5818, 7.7510),
       'Lille': (50.6370, 3.0635), 'Nizza': (43.6955, 7.2735), 'Montpellier': (43.6085, 3.8800)}
rows = []
for f in sorted(glob.glob('rows_dep*.json')):
    rows += json.load(open(f))
print('righe totali', len(rows))
def century(y):
    if y is None: return 'missing'
    if y < 1800: return '<1800'
    if y < 1900: return '1800s'
    if y < 2000: return '1900s'
    return '2000+'
def valid(y): return y is not None and 1400 <= y <= 2026
out = {}
for city, (lat, lon) in REF.items():
    rx, ry = lam93(lat, lon)
    rs = [r for r in rows if r['city'] == city]
    for label, sub in [('comune', rs), ('centro1km', [r for r in rs if r['x'] is not None and math.hypot(r['x']-rx, r['y']-ry) <= 1000])]:
        n = len(sub)
        withy = [r for r in sub if valid(r['year'])]
        raw_nonnull = [r for r in sub if r['raw'] not in ('', None)]
        cc = collections.Counter(century(r['year']) if valid(r['year']) else 'missing' for r in sub)
        out[(city, label)] = dict(n=n, pct=round(100*len(withy)/n, 1) if n else None,
                                   raw=len(raw_nonnull), cent=dict(cc))
        print(f"{city:12s} {label:10s} n={n:7d} anno_valido={len(withy):7d} ({out[(city,label)]['pct']}%) raw_nonnull={len(raw_nonnull)} ", {k: cc[k] for k in ['<1800','1800s','1900s','2000+','missing'] if k in cc})
json.dump({f'{k[0]}|{k[1]}': v for k, v in out.items()}, open('summary_fr.json', 'w'), indent=1)
