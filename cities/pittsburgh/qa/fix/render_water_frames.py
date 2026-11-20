"""render_water_frames.py [res_w res_h samples]: local CPU frames (bpy) of the Point and the Strip in 1800,1850,1900,1936,1950,2023.
One build_render process, shots are still blocks of 16 frames (as kit/qa.py). Output cities/pittsburgh/qa/water_frames/<name>.jpg + sheet.
usage (repo root): /home/user/bl/bin/python cities/pittsburgh/qa/fix/render_water_frames.py 960 540 16"""
import json, os, subprocess, sys, time
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); os.chdir(R)
W, H, S = (int(v) for v in (sys.argv[1:4] if len(sys.argv) > 3 else (960, 540, 16)))
OUT = R + '/cities/pittsburgh/qa/water_frames'; os.makedirs(OUT, exist_ok=True)
FPS = 24; HOLD = 16
AREAS = {'point': ((-850.0, 120.0, 0.0), (900.0, -350.0, 520.0)), 'strip': ((1850.0, 2450.0, 0.0), (700.0, -600.0, 520.0))}
YEARS = [1800, 1850, 1900, 1936, 1950, 2023]
if len(sys.argv) > 4: YEARS = [int(v) for v in sys.argv[4].split(',')]
shots = [(a, y) for a in AREAS for y in YEARS]
years, cam, only = [], [], []
for i, (a, y) in enumerate(shots):
    f0 = i * HOLD + 1; fm = f0 + HOLD // 2; tg, off = AREAS[a]
    years += [[(f0 - 1) / FPS, y], [(f0 + HOLD - 2) / FPS, y]]
    cam.append([(fm - 1) / FPS, [tg[0] + off[0], tg[1] + off[1], off[2]], list(tg), 35.0]); only.append(fm)
sp = OUT + '/schedule_water.json'; json.dump({'duration': len(shots) * HOLD / FPS, 'lens': 35, 'years': years, 'cam': cam}, open(sp, 'w'), indent=1)
fr = OUT + '/raw'; os.makedirs(fr, exist_ok=True)
for f in os.listdir(fr): os.remove(fr + '/' + f)
cmd = [sys.executable, 'build_render.py', '--', 'data_pittsburgh', fr, '--frames', '1', str(len(shots) * HOLD), '--only', ','.join(map(str, only)), '--res', str(W), str(H), '--samples', str(S), '--denoiser', 'none', '--device', 'CPU', '--schedule', sp, '--city', 'city_pittsburgh.json']
t = time.time()
with open(OUT + '/render.log', 'w') as lf: p = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
print('exit', p.returncode, '%.0f s' % (time.time() - t))
from PIL import Image
for (a, y), fm in zip(shots, only):
    f = f'{fr}/{fm:04d}.jpg'
    if not os.path.exists(f): f = f'{fr}/{fm:04d}.png'
    if os.path.exists(f): Image.open(f).convert('RGB').save(f'{OUT}/{a}_{y}.jpg', quality=88)
    else: print('missing', a, y)
