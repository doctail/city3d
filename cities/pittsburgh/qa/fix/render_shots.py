"""render_shots.py SHOTS.json OUTDIR [W H SAMPLES] [--crop x0 y0 x1 y1]: local bpy CPU frames, one process.
SHOTS.json: [{"name": "x", "year": 1936.208, "pos": [x,y,z], "tgt": [x,y,z], "lens": 35}, ...]  (blocks of 16 still frames as kit/qa.py)
usage (repo root): flock /tmp/claude-0/render.lock /home/user/bl/bin/python cities/pittsburgh/qa/fix/render_shots.py shots.json out 960 540 16 [--crop ...]"""
import json, os, subprocess, sys, time
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')); os.chdir(R)
a = sys.argv[1:]; crop = None
if '--crop' in a: i = a.index('--crop'); crop = a[i + 1:i + 5]; a = a[:i]
shots = json.load(open(a[0])); OUT = os.path.abspath(a[1]); W, H, S = (a[2:5] + ['960', '540', '16'][len(a[2:5]):])
os.makedirs(OUT, exist_ok=True); fr = OUT + '/raw'; os.makedirs(fr, exist_ok=True)
for f in os.listdir(fr): os.remove(fr + '/' + f)
FPS = 24; HOLD = 16; years, cam, only = [], [], []
for i, s in enumerate(shots):
    f0 = i * HOLD + 1; fm = f0 + HOLD // 2
    years += [[(f0 - 1) / FPS, s['year']], [(f0 + HOLD - 2) / FPS, s['year']]]
    cam.append([(fm - 1) / FPS, s['pos'], s['tgt'], s.get('lens', 35.0)]); only.append(fm)
sp = OUT + '/schedule.json'; json.dump({'duration': len(shots) * HOLD / FPS, 'lens': 35, 'years': years, 'cam': cam}, open(sp, 'w'))
cmd = [sys.executable, 'build_render.py', '--', 'data_pittsburgh', fr, '--frames', '1', str(len(shots) * HOLD), '--only', ','.join(map(str, only)), '--res', W, H, '--samples', S, '--denoiser', 'none', '--device', 'CPU', '--schedule', sp, '--city', 'city_pittsburgh.json']
if crop: cmd += ['--crop'] + crop
t = time.time()
with open(OUT + '/render.log', 'w') as lf: p = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
print('exit', p.returncode, '%.0f s for %d frames' % (time.time() - t, len(shots)))
from PIL import Image
for s, fm in zip(shots, only):
    f = f'{fr}/{fm:04d}.jpg'
    if not os.path.exists(f): f = f'{fr}/{fm:04d}.png'
    if os.path.exists(f): Image.open(f).convert('RGB').save(f"{OUT}/{s['name']}.jpg", quality=88)
    else: print('missing', s['name'])
