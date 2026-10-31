# Scarica i dati delle Termopili in ./data: Copernicus GLO-30 (N38 E022) + Sentinel-2 cloudless 2016 (EOX, CC BY 4.0), zoom 14.
import os, time, urllib.request
def get(url, f):
    for k in range(5):
        try: urllib.request.urlretrieve(url, f + '.part'); os.replace(f + '.part', f); return
        except Exception as e: print('riprovo', url, e, flush=True); time.sleep(3 * (k + 1))
    raise SystemExit('ERRORE: download fallito ' + url)
from PIL import Image
os.makedirs('data/tiles', exist_ok=True)
dem = 'data/Copernicus_DSM_COG_10_N38_00_E022_00_DEM.tif'
if not os.path.exists(dem):
    get('https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N38_00_E022_00_DEM/Copernicus_DSM_COG_10_N38_00_E022_00_DEM.tif', dem)
im = Image.new('RGB', (18 * 256, 17 * 256))
for i, x in enumerate(range(9209, 9227)):
    for j, y in enumerate(range(6265, 6282)):
        f = f'data/tiles/{y}_{x}.jpg'
        if not os.path.exists(f): get(f'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/14/{y}/{x}.jpg', f)
        im.paste(Image.open(f), (i * 256, j * 256))
im.save('data/satellite_z14.jpg', quality=94); print('dati pronti')
