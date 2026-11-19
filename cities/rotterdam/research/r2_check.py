import json,math,re
st=json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'../story.json')))
LAT0,LON0=51.9221,4.4795;KX=math.cos(math.radians(LAT0))*111320;KY=110540
L=lambda la,lo:((lo-LON0)*KX,(la-LAT0)*KY)
lm={l['name']:l for l in st['landmarks']}
fires={f['name']:f for f in st['history']['fires']}
def pos(t):
    if t.startswith('area:'):
        a=[float(v) for v in t[5:].strip('[]').split(',')];return L(a[0],a[1])
    if t.startswith('fire:'):
        r=fires[t[5:]]['ring'];xs=[L(*p) for p in r];return (sum(x for x,_ in xs)/len(xs),sum(y for _,y in xs)/len(xs))
    return L(*lm[t]['at'])
S=st['regia']['soste'];print('n soste',len(S))
for i,s in enumerate(S):
    t=s['target']
    if t in lm:
        ph=lm[t]['phases'];mid=(s['y0']+s['y1'])/2;first=min(p['y'] for p in ph)
        print('  monument',t,'built from',first,'hover mid',round(mid,1),'OK' if first<=mid else 'LATE')
print('legs (dist/150 s estimate; peak speed higher, so flight is a bit shorter):')
for a,b in zip(S,S[1:]):
    pa,pb=pos(a['target']),pos(b['target']);d=math.hypot(pa[0]-pb[0],pa[1]-pb[1]);t=max(3.5,d/150)
    dy=b['y0']-a['y1'];r=dy/t
    flag='  <-- R2 SUSPECT' if t>=12 and r<0.4 else ''
    if t>=9 or flag: print(f"  {a['y1']:.1f}->{b['y0']:.1f} {d:5.0f} m t~{t:4.1f}s dy={dy:6.1f} rate~{r:5.2f} y/s{flag}")
