"""Foglio di fotogrammi veri (R15) di Marsiglia: ~24 inquadrature su tutta la linea del tempo, 960x540, CPU locale.
Uso: [flock /tmp/claude-0/render.lock] python cities/marseille/qa/sheet.py [out_dir]   (python con bpy; una sola costruzione scena)
Le inquadrature del tempo usano la camera del volo reale (schedule_marseille.json) all'istante in cui il contatore raggiunge l'anno; le speciali (Lacydon, Joliette) sono fisse."""
import json, os, sys, subprocess, time
import numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, R)
from kit import qa, geo
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'cities/marseille/qa/sheet')
os.makedirs(out, exist_ok=True)
sc = json.load(open(R + '/schedule_marseille.json')); D = R + '/data_marseille'
Y = np.array(sc['years'], float); ts, ys = Y[:, 0], Y[:, 1]
def t_of(year): return float(np.interp(year, ys, ts))   # years crescente
TL = [-600, -540, -400, -200, -49, 100, 400, 800, 1100, 1300, 1500, 1650, 1720, 1800, 1850, 1900, 1942.5, 1943.5, 1960, 2000, 2026]
shots = []
for y in TL:
    p, tg, ln = qa._cam_at(sc, t_of(y)); shots.append({'label': f'volo {y:g}', 'year': y, 'pos': p, 'tgt': tg, 'lens': ln})
shots += [{'label': 'Lacydon -500', 'year': -500, 'pos': [-520, -760, 380], 'tgt': [10, 90, 0], 'lens': 32},
          {'label': 'Lacydon 1300', 'year': 1300, 'pos': [-520, -760, 380], 'tgt': [10, 90, 0], 'lens': 32},
          {'label': 'Joliette 1800', 'year': 1800, 'pos': [-2300, -300, 1200], 'tgt': [-1000, 1900, 0], 'lens': 32},
          {'label': 'Joliette 1900', 'year': 1900, 'pos': [-2300, -300, 1200], 'tgt': [-1000, 1900, 0], 'lens': 32}]
for sh_ in json.load(open(R + '/cities/marseille/story.json'))['city']['cover']['shots']:
    if sh_['tag'] in ('massalia_b', 'now_day'): c_ = sh_['cam']; shots.append({'label': 'COVER ' + sh_['tag'], 'year': sh_['year'], 'pos': c_[:3], 'tgt': c_[3:], 'lens': sh_.get('lens', 35)})
HOLD = 16; FPS = 24
years, cam, only = [], [], []
for i, s in enumerate(shots):
    f0 = i * HOLD + 1; fm = f0 + HOLD // 2
    years += [[(f0 - 1) / FPS, s['year']], [(f0 + HOLD - 2) / FPS, s['year']]]
    cam.append([(fm - 1) / FPS, [round(v, 1) for v in s['pos']], [round(v, 1) for v in s['tgt']], round(s['lens'], 1)]); only.append(fm)
qs = {'duration': len(shots) * HOLD / FPS, 'lens': 35, 'years': years, 'cam': cam}
sp = os.path.join(out, 'schedule_sheet.json'); json.dump(qs, open(sp, 'w'))
fr = os.path.join(out, 'frames'); os.makedirs(fr, exist_ok=True)
for f in os.listdir(fr): os.remove(os.path.join(fr, f))
cmd = [qa._bpy_python(), R + '/build_render.py', '--', D, fr, '--frames', '1', str(len(shots) * HOLD), '--only', ','.join(map(str, only)), '--res', '1920', '1080', '--samples', '16', '--denoiser', 'none', '--device', 'CPU', '--schedule', sp, '--city', R + '/city_marseille.json']
t = time.time()
with open(out + '/render.log', 'w') as lf: subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=R)
print('render', round(time.time() - t), 's', len(shots), 'fotogrammi')
from PIL import Image, ImageDraw
W, H = 640, 360; cols = 4; rows = -(-len(shots) // cols)
sh = Image.new('RGB', (cols * W, rows * (H + 20)), (20, 20, 20)); dr = ImageDraw.Draw(sh)
for i, (s, fm) in enumerate(zip(shots, only)):
    f = f'{fr}/{fm:04d}.jpg'
    if not os.path.exists(f): continue
    x, y = (i % cols) * W, (i // cols) * (H + 20); sh.paste(Image.open(f).convert('RGB').resize((W, H)), (x, y + 20)); dr.text((x + 5, y + 4), s['label'], fill=(240, 240, 240))
sh.save(out + '/sheet.jpg', quality=88)
json.dump([[s['label'], fm] for s, fm in zip(shots, only)], open(out + '/index.json', 'w'))
