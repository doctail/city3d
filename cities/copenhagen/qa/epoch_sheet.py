"""Foglio di fotogrammi per epoca (CPU/bpy, 480x270, 4 campioni): due inquadrature fisse (citta' da sud-est, porto da nord-est) x anni chiave.
Uso: KIT_BPY=... python cities/copenhagen/qa/epoch_sheet.py [OUT_DIR]   -> OUT_DIR/ep_<anno>_<cam>.jpg + sheet.jpg"""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from kit import geo, qa
from PIL import Image, ImageDraw
slug = 'copenhagen'; story = geo.load_story(slug); D = geo.data_dir(story)
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'epoch'))
os.makedirs(out, exist_ok=True)
YEARS = [1185, 1500, 1650, 1728.7, 1729.4, 1795.3, 1796.0, 1807.6, 1808.2, 1850, 1900, 1950, 2026]
CAMS = {'citta': ([3300.0, -3200.0, 1500.0], [0.0, 250.0, 0.0], 32.0), 'porto': ([3600.0, 2300.0, 1100.0], [1400.0, 100.0, 0.0], 32.0)}
only = [a for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(CAMS)
shots = [{'label': f'{c} {y}', 'year': y, 'pos': CAMS[c][0], 'tgt': CAMS[c][1], 'lens': CAMS[c][2]} for c in only for y in YEARS]
R = qa.Report(); ok = qa.render_frames(story, D, os.path.join(geo.ROOT, 'city_copenhagen.json'), None, out, R, shots=shots, sheet=False)
print(len(ok), 'frames')
for s, f in ok:
    n = os.path.join(out, 'ep_%s_%s.jpg' % (s['label'].split()[0], ('%.1f' % s['year']).rstrip('0').rstrip('.')))
    os.replace(f, n)
for r in R.rows: print(r[:3])
