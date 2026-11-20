"""Confronto colori: media RGB del render (fotogramma nadir) per copertura WorldCover vs mediana reale Sentinel-2 (palette.json, albedo sRGB).
Uso: python measure.py <nadir.jpg> [<nadir2.jpg> ...]   (cam nadir (0,-1,9500), lens 35, 960x540, nord in alto)
Cielo: media della fascia alta (10%) di un fotogramma obliquo: python measure.py --sky <frame.jpg>"""
import sys, os, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import rasterio
from rasterio.windows import from_bounds
from kit import geo
ROOT = geo.ROOT
story = json.load(open(f'{ROOT}/cities/pittsburgh/story.json')); P = geo.Proj.of(story)
pal = json.load(open(f'{ROOT}/cities/pittsburgh/palette.json'))
WCN = {10: 'tree', 20: 'shrub', 30: 'grass', 40: 'crop', 50: 'built', 60: 'bare', 80: 'water'}
os.environ.setdefault('CURL_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
W_m = 2 * 9500 * 18 / 35; H_m = W_m * 540 / 960
def wc_grid():
    la0, lo0 = P.inv(-W_m / 2 - 200, -H_m / 2 - 200); la1, lo1 = P.inv(W_m / 2 + 200, H_m / 2 + 200)
    with rasterio.open('https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N39W081_Map.tif') as d:
        w = from_bounds(lo0, la0, lo1, la1, d.transform).round_offsets().round_lengths(); a = d.read(1, window=w); tr = d.window_transform(w)
    return a, tr
def main(files):
    wc, tr = wc_grid(); rows = []
    for f in files:
        im = np.asarray(Image.open(f).convert('RGB')).astype(np.float32); h, w, _ = im.shape
        jj, ii = np.mgrid[0:h, 0:w]; x = ((ii + .5) / w - .5) * W_m; y = (.5 - (jj + .5) / h) * H_m
        la = P.lat0 + y / P.KY; lo = P.lon0 + x / P.KX
        c = ((lo - tr.c) / tr.a).astype(int); r = ((la - tr.f) / tr.e).astype(int)
        cls = wc[np.clip(r, 0, wc.shape[0] - 1), np.clip(c, 0, wc.shape[1] - 1)]
        print(os.path.basename(f), 'mean all', im.reshape(-1, 3).mean(0).round(1))
        for code, name in WCN.items():
            m = cls == code
            if m.sum() < 500: continue
            real = pal['classes'].get(name, {}).get('rgb'); me = np.median(im[m], 0)
            print(f'  {name:6s} render median {me.round(0)}  real(S2 albedo-sRGB) {np.round(real,0) if real else None}  ratio R/G/B-norm render {np.round(me/me.mean(),2)} real {np.round(np.array(real)/np.mean(real),2) if real else None}  n={int(m.sum())}')
if __name__ == '__main__':
    if sys.argv[1] == '--sky':
        im = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.float32); b = im[:int(im.shape[0] * .06)]
        print('sky band top 6%: mean', b.reshape(-1, 3).mean(0).round(0), ' horizon band 6-12%:', im[int(im.shape[0]*.06):int(im.shape[0]*.12)].reshape(-1,3).mean(0).round(0))
    else: main(sys.argv[1:])
