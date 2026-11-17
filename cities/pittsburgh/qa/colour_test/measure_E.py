"""D_measure-style numbers for a nadir frame: per WorldCover class render median vs Sentinel-2 albedo (palette.json), R/B, luminance, clipping.
Uso: python measure_E.py <frame.jpg> [altitude_m=9500]   (nadir at (0,0,alt), lens 35, 960x540, north up). Needs rasterio (pghenv)."""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
import rasterio
from rasterio.windows import from_bounds
from kit import geo
ROOT = geo.ROOT
os.environ.setdefault('CURL_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
story = json.load(open(f'{ROOT}/cities/pittsburgh/story.json')); P = geo.Proj.of(story)
pal = json.load(open(f'{ROOT}/cities/pittsburgh/palette.json'))['classes']
f = sys.argv[1]; alt = float(sys.argv[2]) if len(sys.argv) > 2 else 9500.0
W_m = 2 * alt * 18 / 35; H_m = W_m * 540 / 960
la0, lo0 = P.inv(-W_m / 2 - 200, -H_m / 2 - 200); la1, lo1 = P.inv(W_m / 2 + 200, H_m / 2 + 200)
with rasterio.open('https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N39W081_Map.tif') as d:
    w = from_bounds(lo0, la0, lo1, la1, d.transform).round_offsets().round_lengths(); wc = d.read(1, window=w); tr = d.window_transform(w)
im = np.asarray(Image.open(f).convert('RGB')).astype(np.float32); h, wd, _ = im.shape
jj, ii = np.mgrid[0:h, 0:wd]; x = ((ii + .5) / wd - .5) * W_m; y = (.5 - (jj + .5) / h) * H_m
la = P.lat0 + y / P.KY; lo = P.lon0 + x / P.KX
c = ((lo - tr.c) / tr.a).astype(int); r = ((la - tr.f) / tr.e).astype(int)
cls = wc[np.clip(r, 0, wc.shape[0] - 1), np.clip(c, 0, wc.shape[1] - 1)]
L = lambda v: 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
print(os.path.basename(f), 'alt', alt, 'mean all', im.reshape(-1, 3).mean(0).round(1), ' clipped(>=250 any ch) %.2f%%' % (100 * (im.max(-1) >= 250).mean()))
groups = {'ground': (10, 20, 30, 40, 60), 'tree': (10,), 'grass': (30,), 'built': (50,), 'water': (80,)}
for name, codes in groups.items():
    m = np.isin(cls, codes)
    if m.sum() < 300: continue
    real = np.array(pal[name]['rgb']); me = np.median(im[m], 0)
    print(f'  {name:6s} render {me.round(0)} L={L(me):5.1f} R/B={me[0]/me[2]:.3f} | S2 {real.round(0)} L={L(real):5.1f} R/B={real[0]/real[2]:.3f} | dR/B {100*(me[0]/me[2]/(real[0]/real[2])-1):+.0f}% dL {100*(L(me)/L(real)-1):+.0f}%  n={int(m.sum())}')
