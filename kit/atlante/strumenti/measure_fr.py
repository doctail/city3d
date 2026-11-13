import sys, csv, math, json, re, io
sys.path.insert(0, '/tmp/claude-0/-home-user/f79f9b62-91b7-5c36-b63d-4d8dc6aaeafb/scratchpad/bdnb')
from rangeio import open_zip
csv.field_size_limit(10**9)
M = '2026-02-b'
BASE = 'https://open-data.s3.fr-par.scw.cloud/bdnb_millesime_%s/millesime_%s_dep%s/open_data_millesime_%s_dep%s_csv.zip'
CITY_OF = {}
for c in ['69123'] + ['6938%d' % i for i in range(1,10)]: CITY_OF[c] = 'Lione'
for c in ['13055'] + ['13%03d' % i for i in range(201,217)]: CITY_OF[c] = 'Marsiglia'
CITY_OF['33063'] = 'Bordeaux'; CITY_OF['31555'] = 'Tolosa'; CITY_OF['44109'] = 'Nantes'
CITY_OF['67482'] = 'Strasburgo'; CITY_OF['59350'] = 'Lille'; CITY_OF['06088'] = 'Nizza'; CITY_OF['34172'] = 'Montpellier'
CITIES = {  # commune: (nom, dep, lat, lon) centro = punto di riferimento approssimato
 '69123': ('Lione', '69', 45.7676, 4.8355),
 '13055': ('Marsiglia', '13', 43.2950, 5.3742),
 '33063': ('Bordeaux', '33', 44.8378, -0.5792),
 '31555': ('Tolosa', '31', 43.6045, 1.4440),
 '44109': ('Nantes', '44', 47.2151, -1.5566),
 '67482': ('Strasburgo', '67', 48.5818, 7.7510),
 '59350': ('Lille', '59', 50.6370, 3.0635),
 '06088': ('Nizza', '06', 43.6955, 7.2735),
 '34172': ('Montpellier', '34', 43.6085, 3.8800),
}
def lam93(lat, lon):
    a = 6378137.0; f = 1/298.257222101; e2 = 2*f - f*f; e = math.sqrt(e2)
    lat0, lon0, lat1, lat2, x0, y0 = 46.5, 3.0, 44.0, 49.0, 700000.0, 6600000.0
    r = math.radians
    def m(p): return math.cos(p)/math.sqrt(1-e2*math.sin(p)**2)
    def t(p): return math.tan(math.pi/4 - p/2)/((1-e*math.sin(p))/(1+e*math.sin(p)))**(e/2)
    p1, p2, p0 = r(lat1), r(lat2), r(lat0)
    n = (math.log(m(p1)) - math.log(m(p2)))/(math.log(t(p1)) - math.log(t(p2)))
    F = m(p1)/(n*t(p1)**n); rho0 = a*F*t(p0)**n
    rho = a*F*t(r(lat))**n; th = n*r(lon-lon0)
    return x0 + rho*math.sin(th), y0 + rho0 - rho*math.cos(th)
def centroid(wkt):
    nums = [(float(a), float(b)) for a, b in re.findall(r"(-?\d+\.?\d*) (-?\d+\.?\d*)", wkt)]
    if not nums: return None
    return sum(x for x,_ in nums)/len(nums), sum(y for _,y in nums)/len(nums)
def run(dep):
    url = BASE % (M, M, dep, M, dep)
    z, size = open_zip(url)
    # 1) batiment_groupe: id -> commune, centroide L93
    groups = {}   # id -> (commune, x, y)
    with z.open('csv/batiment_groupe.csv') as f:
        rd = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'), delimiter=';', quotechar='"')
        for r in rd:
            c = r['code_commune_insee']
            if c not in CITY_OF: continue
            cen = centroid(r['geom_groupe'])
            groups[r['batiment_groupe_id']] = (CITY_OF[c], cen, c)
    print(dep, 'groupi nei comuni target:', len(groups), flush=True)
    # 2) ffo_bat: annee_construction
    ann = {}
    with z.open('csv/batiment_groupe_ffo_bat.csv') as f:
        rd = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'), delimiter=';', quotechar='"')
        for r in rd:
            if r['batiment_groupe_id'] in groups:
                ann[r['batiment_groupe_id']] = r['annee_construction']
    return groups, ann
if __name__ == '__main__':
    d = sys.argv[1]
    groups, ann = run(d)
    rows = []
    for gid, (city, cen, code) in groups.items():
        a = ann.get(gid, '')
        y = int(a) if a and a.lstrip('-').isdigit() else None
        rows.append({'city': city, 'code': code, 'year': y, 'x': cen[0] if cen else None, 'y': cen[1] if cen else None, 'raw': a})
    json.dump(rows, open('/tmp/claude-0/-home-user/f79f9b62-91b7-5c36-b63d-4d8dc6aaeafb/scratchpad/bdnb/rows_dep%s.json' % d, 'w'))
    print('ok', d, len(rows), flush=True)
