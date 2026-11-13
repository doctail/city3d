import re,sys,os,time,urllib.request,urllib.parse
B="https://geodienste.hamburg.de/HH_WFS_INSPIRE_Gebaeude_2D_ALKIS"
N=406415; PG=3000
OUT="/home/user/hh_raw"
part,parts=int(sys.argv[1]),int(sys.argv[2])
pat_id=re.compile(r'gml:id="(Building_[^"]+)"')
pat_pos=re.compile(r'<gml:posList[^>]*>([^<]*)</gml:posList>')
for pg in range(part,(N+PG-1)//PG,parts):
    fn=f"{OUT}/p{pg:03d}.tsv"
    if os.path.exists(fn): continue
    q=urllib.parse.urlencode({"SERVICE":"WFS","VERSION":"2.0.0","REQUEST":"GetFeature","TYPENAMES":"bu-core2d:Building","COUNT":PG,"STARTINDEX":pg*PG})
    for att in range(4):
        try:
            t=urllib.request.urlopen(B+"?"+q,timeout=170).read().decode("utf8"); break
        except Exception as e:
            time.sleep(5*(att+1)); t=None
    if t is None: print("FAIL",pg,flush=True); continue
    rows=[]
    for b in t.split("<wfs:member>")[1:]:
        i=pat_id.search(b); 
        y=""
        if "dateOfConstruction" in b:
            m=re.search(r'<bu-base:end>([^<]*)</bu-base:end>',b.split("dateOfConstruction",1)[1])
            if m: y=m.group(1)
        p=pat_pos.search(b)
        rows.append(f"{i.group(1) if i else ''}\t{y}\t{p.group(1).strip() if p else ''}")
    open(fn+".tmp","w").write("\n".join(rows)+"\n"); os.rename(fn+".tmp",fn)
    print("ok",pg,len(rows),flush=True)
