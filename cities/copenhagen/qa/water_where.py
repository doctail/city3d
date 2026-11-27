import json,sys,numpy as np,collections
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
D='data_copenhagen'; C=json.load(open('city_copenhagen.json')); LC=C.get('land_close',45); Y=float(sys.argv[1]); which=sys.argv[2]
P=lambda r:(Polygon(r['ext'],r.get('holes',[])) if isinstance(r,dict) else Polygon(r)).buffer(0)
land0=unary_union([P(r) for r in json.load(open(f'{D}/land.json'))]).buffer(LC,join_style=2).buffer(-LC,join_style=2)
PH=json.load(open(f'{D}/landphases.json')); base=land0
for p in PH: base=base.difference(Polygon(p['r']).buffer(0))
l=unary_union([base]+[Polygon(p['r']).buffer(0).buffer(1.5,join_style=2) for p in PH if p['from']<=Y<p['to']])
L=json.load(open(f'{D}/'+('hist.json' if which=='h' else 'buildings.json')))
out=[]
for b in L:
    if b['y']>Y or b.get('d',1e9)<=Y: continue
    r=np.array(b['r']); x,y=r[:,0].mean(),r[:,1].mean()
    if abs(x)<9000 and abs(y)<9000 and not contains_xy(l,x,y): out.append((x,y,b.get('zone',b.get('k',''))))
print(len(out)); c=collections.Counter((round(x/500)*500,round(y/500)*500,z[:22]) for x,y,z in out)
for k,v in c.most_common(12): print(k,v)
