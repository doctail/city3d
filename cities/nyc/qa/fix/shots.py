"""usage: shots.py NAME shotsfile.json [--city city_nyc.json] [extra build_render args]
shotsfile: list of {label, year, pos, tgt, lens}. One scene build, one frame per shot (HOLD blocks). Output: fix/frames_NAME/<label>.jpg"""
import sys, os, json, subprocess, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
name, sf = sys.argv[1], sys.argv[2]
rest = sys.argv[3:]
city = ROOT + '/city_nyc.json'
if '--city' in rest:
    i = rest.index('--city'); city = rest[i + 1]; del rest[i:i + 2]
FULL = os.environ.get('YB_FULL') == '1'   # YB_FULL=1: whole city, 1920x1080, no crop (scene-cost measurement)
shots = json.load(open(sf)); HOLD = 16; FPS = 24
years, cam, only = [], [], []
for i, s in enumerate(shots):
    f0 = i * HOLD + 1; fm = f0 + HOLD // 2
    years += [[(f0 - 1) / FPS, s['year']], [(f0 + HOLD - 2) / FPS, s['year']]]
    cam.append([(fm - 1) / FPS, s['pos'], s['tgt'], s['lens']]); only.append(fm)
here = os.path.dirname(os.path.abspath(__file__)); out = f'{here}/frames_{name}'
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
sp = f'{here}/sched_{name}.json'
json.dump({'duration': len(shots) * HOLD / FPS, 'lens': 35, 'years': years, 'cam': cam}, open(sp, 'w'))
cmd = ['nice', '-n', '10', os.environ.get('YB_PY', '/tmp/claude-0/blvenv/bin/python'), ROOT + '/build_render.py', '--', os.environ.get('NYC_DATA', ROOT + '/data_nyc'), out, '--frames', '1', str(len(shots) * HOLD),
       '--only', ','.join(map(str, only)), '--res', *(['1920', '1080'] if FULL else ['1280', '720']), '--samples', os.environ.get('YB_SPP', '16'), '--device', 'CPU', '--schedule', sp, '--city', city] + ([] if FULL else ['--crop', '-6500', '-10500', '2500', '-1500']) + rest
print(' '.join(cmd), flush=True)
subprocess.run(cmd, stdout=open(f'{out}/log.txt', 'w'), stderr=subprocess.STDOUT, cwd=ROOT)
for s, fm in zip(shots, only):
    p = f'{out}/{fm:04d}.jpg'
    if os.path.exists(p): os.rename(p, f'{out}/{s["label"]}.jpg')
print(open(f'{out}/log.txt').read().splitlines()[-3:])
