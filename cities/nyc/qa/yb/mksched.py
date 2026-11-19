import sys, json, numpy as np
sys.path.insert(0, '/home/user/doctail/city3d')
from kit import qa
sc = json.load(open('/home/user/doctail/city3d/schedule_nyc.json'))
Yp = np.array(sc['years'], float)
which = sys.argv[1]
# (label, t, year override)
A = [('hover1 1609', 22.0, None), ('flight 1618', 37.0, None), ('1625 approach', 43.0, 1625.0), ('hover Fraunces 1719', 96.0, None),
     ('hover StPauls 1766', 113.0, None), ('flight 1847', 240.0, None), ('flight 1920s', 467.0, None), ('hover last OneWTC 2014', 664.0, None),
     ('thumb 1609', 22.0, 1609.0), ('thumb 1625', 22.0, 1625.0), ('thumb NOW', 22.0, 2026.0)]
Bs = [('hover Woolworth 1913', 440.0, None), ('hover last OneWTC 2014', 664.0, None), ('hover Twin Towers 1973', 594.0, None)]
shots = A if which == 'A' else Bs
HOLD = 16; FPS = 24; years = []; cam = []; only = []; meta = []
for i, (lab, t, yo) in enumerate(shots):
    f0 = i * HOLD + 1; fm = f0 + HOLD // 2
    y = yo if yo is not None else qa._year_at(t, Yp)
    p, tg, ln = qa._cam_at(sc, t)
    years += [[(f0 - 1) / FPS, y], [(f0 + HOLD - 2) / FPS, y]]
    cam.append([(fm - 1) / FPS, [round(float(v), 1) for v in p], [round(float(v), 1) for v in tg], round(float(ln), 1)])
    only.append(fm); meta.append([lab, t, float(y), fm])
out = {'_doc': 'nyc yb-qa shots', 'duration': len(shots) * HOLD / FPS, 'lens': 32, 'years': years, 'cam': cam}
json.dump(out, open(f'/tmp/claude-0/work/sched_{which}.json', 'w'), indent=1)
json.dump(meta, open(f'/tmp/claude-0/work/meta_{which}.json', 'w'))
print(','.join(map(str, only)), meta)
