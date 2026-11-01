# Dati di Costantinopoli in ./data: Copernicus GLO-30 N40+N41 E028 + Sentinel-2 cloudless 2016 (EOX, CC BY 4.0), zoom 14, tile x 9503-9515, y 6136-6146.
import os, time, urllib.request
from PIL import Image
def get(url, f):
    for k in range(5):
        try: urllib.request.urlretrieve(url, f + '.part'); os.replace(f + '.part', f); return
        except Exception as e: print('riprovo', url, e, flush=True); time.sleep(3 * (k + 1))
    raise SystemExit('ERRORE: download fallito ' + url)
os.makedirs('data/tiles', exist_ok=True)
for la in (40, 41):
    n = f'Copernicus_DSM_COG_10_N{la}_00_E028_00_DEM'; f = f'data/{n}.tif'
    if not os.path.exists(f): get(f'https://copernicus-dem-30m.s3.amazonaws.com/{n}/{n}.tif', f)
im = Image.new('RGB', (13 * 256, 11 * 256))
for i, x in enumerate(range(9503, 9516)):
    for j, y in enumerate(range(6136, 6147)):
        f = f'data/tiles/{y}_{x}.jpg'
        if not os.path.exists(f): get(f'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/14/{y}/{x}.jpg', f)
        im.paste(Image.open(f), (i * 256, j * 256))
im.save('data/satellite_z14.jpg', quality=94); print('dati pronti')
