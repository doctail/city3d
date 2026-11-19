import json,re,sys
D=__import__('os').path.dirname(__import__('os').path.abspath(__file__))
import importlib.util
st=json.load(open(D+'/../story.json'))
# map id -> file from build script
src=open(D+'/build_story.py').read()
files=dict(re.findall(r"'(S\d+)': \('[^']*', '[^']*', '([^']+)'\)",src)) if False else None
import ast
m=re.search(r"SRC = (\{.*?\n\})",src,re.S)
SRC=ast.literal_eval(m.group(1))
norm=lambda t: re.sub(r'\s+',' ',t).strip()
bad=0;n=0
for sid,s in st['sources'].items():
    tx=norm(open(D+'/sources_fetched/'+SRC[sid][2]).read())
    for q in s['quote'].split(' … '):
        n+=1
        if norm(q) not in tx: bad+=1; print('MISSING',sid,q[:80])
print('quotes',n,'bad',bad)
ids=set(st['sources'])
def walk(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in('src','pop_src','pop_point_src') :
                for i in (v if isinstance(v,list) else [v]):
                    if i not in ids: print('UNKNOWN SRC',path,i)
            else: walk(v,path+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+f'[{i}]')
walk(st)
print('cards w/o src',[c['title'] for c in st['montaggio']['cards'] if not c.get('src')])
