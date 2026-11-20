"""monu.py: crops (480x320) around each landmark label visible in the hover frames of frames_final -> /tmp/claude-0/monu.jpg"""
import json,numpy as np
from PIL import Image,ImageDraw
sh={s['label']:s for s in json.load(open('cams_final.json'))}
L=json.load(open('frames_final/labels.json'))
want={'h00_1609':[],'h01_1627':['Fort Amsterdam'],'h04_1698':['Trinity Church'],'h05_1720':['Fraunces Tavern'],'h06_1767':["St. Paul's Chapel"],'h08_1789':['City Hall / Federal Hall'],'h09_1811':['Castle Clinton'],'h11_1883':[],'h12_1931':['Empire State Building','Chrysler Building'],'h13_1972':[],'h14_2015':[]}
def proj(s,p):
    pos=np.array(s['pos']);t=np.array(s['tgt']);f=s['lens']/36*1920
    fw=t-pos;fw/=np.linalg.norm(fw);r=np.cross(fw,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,fw)
    d=np.array(p)-pos;z=d@fw
    return 960+f*(d@r)/z,540-f*(d@u)/z,z
tiles=[]
for lab,names in want.items():
    s=sh[lab];y=s['year']
    for l in L:
        if l['name'] in names and l['from']<=y+3 and l.get('to',9999)>y:
            x,yy,z=proj(s,[l['x'],l['y'],l['z']])
            print(lab,l['name'],round(x),round(yy),round(z))
            im=Image.open(f'frames_final/{lab}.jpg').convert('RGB');R=300
            c=im.crop((int(x-R),int(yy-R*0.65),int(x+R),int(yy+R*0.65))).resize((600,390));ImageDraw.Draw(c).text((4,4),lab+' '+l['name'],fill=(255,255,0));tiles.append(c)
W=Image.new('RGB',(1200,390*((len(tiles)+1)//2)))
for i,t in enumerate(tiles):W.paste(t,((i%2)*600,(i//2)*390))
W.save('/tmp/claude-0/monu.jpg',quality=88)
