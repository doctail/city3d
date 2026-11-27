"""Colori VERI del suolo per una citta': mediane per copertura (ESA WorldCover) da una scena Sentinel-2 L2A TCI.

Globale e senza chiavi: usa solo S3 pubblico (listing + range request COG), niente STAC (host spesso bloccati).
  - Sentinel-2 L2A COG:  https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/<zona>/<banda>/<quadrato>/<anno>/<mese>/<scena>/{TCI,SCL}.tif
    (la nuvolosita' sta in <scena>.json, proprieta' eo:cloud_cover)
  - ESA WorldCover 2021: https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_<N39W081>_Map.tif
Uso:  python -m kit.colour_kit <slug> [--season summer|winter] [--years 2024,2025] [--scenes 3]
Con --tint scrive cities/<slug>/ground_tint.png/.json (tinta di terra sfocata, city.look.ground_tint).
Scrive cities/<slug>/palette.json (+ palette_report in stdout). La story la attiva con  city.look.palette = "cities/<slug>/palette.json"
(vedi kit/city_json.py); senza quella chiave nulla cambia.
Richiede rasterio e numpy (non servono dentro Blender).
"""
import json, math, os, re, sys, urllib.request, urllib.parse
import numpy as np

from . import geo

S2 = 'https://sentinel-cogs.s3.us-west-2.amazonaws.com'
WC = 'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map'
SEASONS = {'summer': [6, 7, 8, 9], 'winter': [12, 1, 2]}
WC_CLASSES = {10: 'tree', 20: 'shrub', 30: 'grass', 40: 'crop', 50: 'built', 60: 'bare', 80: 'water', 90: 'wetland'}
SCL_OK = (4, 5, 6)     # vegetazione, suolo nudo, acqua (esclusi nuvole 8-10, ombre 3, buio 2, neve 11, non classificato 7)


def _get(url, timeout=40):
    with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as r:
        return r.read()


def mgrs_tile(lat, lon):
    """(zona, banda, quadrato 100 km) del tile Sentinel-2 che contiene il punto."""
    from pyproj import Transformer
    zone = int((lon + 180) // 6) + 1
    epsg = (32600 if lat >= 0 else 32700) + zone
    e, n = Transformer.from_crs('EPSG:4326', f'EPSG:{epsg}', always_xy=True).transform(lon, lat)
    band = 'CDEFGHJKLMNPQRSTUVWX'[min(19, int((lat + 80) // 8))]
    cols = ['ABCDEFGH', 'JKLMNPQR', 'STUVWXYZ'][(zone - 1) % 3]
    rows = 'ABCDEFGHJKLMNPQRSTUV'
    ci = cols[int(e // 100000) - 1]
    ri = rows[(int(n // 100000) + (5 if zone % 2 == 0 else 0)) % 20]
    return zone, band, ci + ri, epsg


def list_scenes(zone, band, sq, years, months):
    out = []
    for y in years:
        for m in months:
            pre = f'sentinel-s2-l2a-cogs/{zone}/{band}/{sq}/{y}/{m}/'
            try:
                x = _get(f'{S2}/?list-type=2&delimiter=/&prefix={urllib.parse.quote(pre)}').decode()
            except Exception as e:
                print('[colour] listing fallito', pre, e); continue
            out += [pre + s + '/' for s in re.findall(r'<Prefix>' + re.escape(pre) + r'([^/<]+)/</Prefix>', x)]
    return out


def cloud_cover(prefix):
    try:
        j = json.loads(_get(f'{S2}/{prefix}{prefix.rstrip("/").split("/")[-1]}.json', 30))
        return float(j['properties']['eo:cloud_cover'])
    except Exception:
        return None


def pick_scenes(zone, band, sq, years, months, n):
    sc = list_scenes(zone, band, sq, years, months)
    print(f'[colour] {len(sc)} scene {zone}{band}{sq} in {years} mesi {months}; leggo la nuvolosita\'...', flush=True)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(12) as ex: cc = list(ex.map(cloud_cover, sc))
    good = sorted([(c, s) for c, s in zip(cc, sc) if c is not None and c < 15.0])
    # una scena per mese-anno al massimo (varieta' stagionale), la piu' limpida
    seen, pick = set(), []
    for c, s in good:
        k = '/'.join(s.split('/')[5:7])   # anno/mese
        if k in seen: continue
        seen.add(k); pick.append((c, s))
        if len(pick) >= n: break
    return pick


def read_scene(prefix, bbox_ll, cap=None):
    """TCI e SCL ritagliati sulla bbox (lon0, lat0, lon1, lat1), sulla griglia 10 m. Ritorna rgb uint8 (3,H,W), scl (H,W), transform, crs."""
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.warp import transform_bounds
    from rasterio.enums import Resampling
    with rasterio.open(f'{S2}/{prefix}TCI.tif') as d:
        b = transform_bounds('EPSG:4326', d.crs, *bbox_ll)
        win = from_bounds(*b, transform=d.transform).round_offsets().round_lengths()
        rgb = d.read([1, 2, 3], window=win, boundless=True, fill_value=0)
        tr = d.window_transform(win); crs = d.crs
    with rasterio.open(f'{S2}/{prefix}SCL.tif') as s:
        scl = s.read(1, window=from_bounds(*b, transform=s.transform), out_shape=rgb.shape[1:], resampling=Resampling.nearest, boundless=True, fill_value=0)
    return rgb, scl, tr, crs


def read_worldcover(lat, lon, tr, crs, shape):
    import rasterio
    from rasterio.warp import reproject, Resampling
    la, lo = int(math.floor(lat / 3) * 3), int(math.floor(lon / 3) * 3)
    tid = f"{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}"
    dst = np.zeros(shape, np.uint8)
    with rasterio.open(f'{WC}/ESA_WorldCover_10m_2021_v200_{tid}_Map.tif') as d:
        from rasterio.warp import transform_bounds
        h, w = shape
        left, top = tr * (0, 0); right, bot = tr * (w, h)
        b = transform_bounds(crs, d.crs, left, bot, right, top)
        from rasterio.windows import from_bounds
        win = from_bounds(*b, transform=d.transform).round_offsets().round_lengths()
        win = rasterio.windows.Window(win.col_off - 2, win.row_off - 2, win.width + 4, win.height + 4)
        src = d.read(1, window=win, boundless=True, fill_value=0)
        reproject(src, dst, src_transform=d.window_transform(win), src_crs=d.crs, dst_transform=tr, dst_crs=crs, resampling=Resampling.nearest)
    return dst


def tci_to_srgb(rgb):
    """TCI = riflettanza*10000 scalata su 0-3558 -> 0-255 (lineare). Per il render serve l'albedo in sRGB: si ricodifica."""
    lin = np.clip(rgb.astype(np.float32) / 255.0 * 0.3558, 0, 1)
    return 255.0 * np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)


def hexc(rgb): return '#%02x%02x%02x' % tuple(int(round(v)) for v in rgb)


def lum(c): return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def class_stats(pix):
    """pix (N,3) uint8. Mediana per canale + 5 toni (percentili di luminanza 15..85) per le rampe."""
    pix = pix.astype(np.float32)
    med = np.median(pix, axis=0)
    L = pix @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    ramp = []
    for q in (15, 32, 50, 68, 85):
        t = np.percentile(L, q); idx = np.argsort(np.abs(L - t))[:max(30, len(L) // 50)]
        ramp.append(np.median(pix[idx], axis=0))
    return med, ramp


def derive(slug, season='summer', years=(2024, 2025), nscenes=3):
    st = json.load(open(os.path.join(geo.ROOT, 'cities', slug, 'story.json')))
    c = st['city']; lat, lon, R = float(c['lat0']), float(c['lon0']), float(c.get('radius_m', 9000))
    dlat = R / 111320.0; dlon = R / (111320.0 * math.cos(math.radians(lat)))
    bbox = (lon - dlon, lat - dlat, lon + dlon, lat + dlat)
    zone, band, sq, epsg = mgrs_tile(lat, lon)
    picks = pick_scenes(zone, band, sq, list(years), SEASONS[season], nscenes + 6)   # + riserva: scene con la bbox fuori dalla striscia (nodata) si saltano
    if not picks: raise SystemExit('nessuna scena Sentinel-2 L2A con nuvole < 15% trovata')
    acc = {}
    used = []
    for cc, pre in picks:
        if len(used) >= nscenes: break
        rgb, scl, tr, crs = read_scene(pre, bbox)
        if (rgb.sum(0) > 0).mean() < 0.5: print(f'[colour] scena {pre.rstrip("/").split("/")[-1]} saltata: copre meno del 50% della bbox'); continue
        wc = read_worldcover(lat, lon, tr, crs, scl.shape)
        ok = np.isin(scl, SCL_OK) & (rgb.sum(0) > 0)
        rgb = tci_to_srgb(rgb)
        for code, name in WC_CLASSES.items():
            m = ok & (wc == code)
            if m.sum() > 200: acc.setdefault(name, []).append(rgb[:, m].T)
        g = ok & np.isin(wc, (10, 20, 30, 40, 60))   # tutto il suolo non costruito e non acqua: e' quello che il render chiama "campi"
        if g.sum() > 200: acc.setdefault('ground', []).append(rgb[:, g].T)
        used.append({'scene': pre.rstrip('/').split('/')[-1], 'cloud': cc, 'valid_px': int(ok.sum())})
        print(f'[colour] {used[-1]}', flush=True)
    stats = {}
    for name, parts in acc.items():
        pix = np.concatenate(parts); med, ramp = class_stats(pix)
        stats[name] = {'median': hexc(med), 'rgb': [round(float(v), 1) for v in med], 'ramp5': [hexc(r) for r in ramp], 'n': int(len(pix))}
    return {'_doc': f'Colori veri per copertura WorldCover 2021 da Sentinel-2 L2A TCI, {season}. Generato da kit/colour_kit.py. Non modificare a mano.',
            'season': season, 'scenes': used, 'bbox_ll': [round(v, 5) for v in bbox], 'classes': stats}


def to_render(pal, ground_dark=0.0):
    """Mappa le classi sulle chiavi di stile/top lette da build_render.py. Solo chiavi del suolo: edifici, cielo e luce non cambiano."""
    C = pal['classes']
    def g(n, fb=None): return (C.get(n) or C.get(fb) or {}).get('median')
    def r(n, fb=None): return (C.get(n) or C.get(fb) or {}).get('ramp5')
    style, top = {}, {}
    if r('ground', 'crop'): top['field_colors'] = r('ground', 'crop')   # il suolo aperto della citta' (colline boscose comprese)
    if g('grass', 'crop'): style['grass'] = g('grass', 'crop'); style['park_ground'] = g('grass', 'crop'); style['urban_green'] = g('grass', 'crop')
    if g('tree'): style['tree'] = g('tree'); style['forest_base'] = g('tree'); style['hedge'] = g('tree')
    if g('water'):
        style['water'] = g('water'); w = C['water']['ramp5']; style['water2'] = w[3]
    if g('bare'): style['reclaim'] = g('bare'); style['street_earth'] = g('bare')
    if r('built'):
        style['urban'] = [r('built')[i] for i in (0, 1, 2, 3, 4)] + [r('built')[2]]
        style['urban_dark'] = r('built')[1]; style['blocks'] = r('built')[1]
    return {'style': style, 'top': top}


def bake_tint(slug, season='summer', years=(2024, 2025), half=12000.0, cell=15.0, sigma_m=45.0, lum_keep=0.4):
    """Tinta di terra a bassa frequenza: albedo Sentinel-2 (solo suolo non costruito/non acqua) / mediana del suolo, sfocata (sigma_m),
    ricampionata su griglia locale in metri. Scrive cities/<slug>/ground_tint.png (+ .json con il box) per city.look.ground_tint.
    Pixel = tinta/2 (0..255 lineare, 128 = neutro); la luminanza e' ridotta (lum_keep) perche' l'ombreggiatura del rilievo e' gia' nel render."""
    from PIL import Image
    from scipy.ndimage import gaussian_filter
    from pyproj import Transformer
    st = json.load(open(os.path.join(geo.ROOT, 'cities', slug, 'story.json'))); c = st['city']; lat, lon = float(c['lat0']), float(c['lon0'])
    P = geo.Proj(lat, lon)
    dlat = (half + 500) / 111320.0; dlon = (half + 500) / (111320.0 * math.cos(math.radians(lat)))
    bbox = (lon - dlon, lat - dlat, lon + dlon, lat + dlat)
    zone, band, sq, epsg = mgrs_tile(lat, lon)
    for pick in pick_scenes(zone, band, sq, list(years), SEASONS[season], 6):   # prima scena che copre >= 50% della bbox (come la palette)
        rgb, scl, tr, crs = read_scene(pick[1], bbox)
        if (rgb.sum(0) > 0).mean() >= 0.5: break
    wc = read_worldcover(lat, lon, tr, crs, scl.shape)
    ok = np.isin(scl, SCL_OK) & (rgb.sum(0) > 0) & np.isin(wc, (10, 20, 30, 40, 60))
    alb = tci_to_srgb(rgb).astype(np.float32)
    sig = sigma_m / 10.0
    w = gaussian_filter(ok.astype(np.float32), sig)
    ch = [gaussian_filter(np.where(ok, alb[i], 0).astype(np.float32), sig) / np.maximum(w, 1e-3) for i in range(3)]
    med = np.array([np.median(alb[i][ok]) for i in range(3)], np.float32)
    n = int(2 * half / cell); xs = -half + (np.arange(n) + .5) * cell; ys = half - (np.arange(n) + .5) * cell   # riga 0 = nord
    X, Y = np.meshgrid(xs, ys); la, lo = P.inv(X, Y)
    e, nn = Transformer.from_crs('EPSG:4326', crs, always_xy=True).transform(lo, la)
    ci = np.clip(((e - tr.c) / tr.a).astype(int), 0, ok.shape[1] - 1); ri = np.clip(((nn - tr.f) / tr.e).astype(int), 0, ok.shape[0] - 1)
    ratio = np.stack([ch[i][ri, ci] / med[i] for i in range(3)], -1); wt = w[ri, ci]
    ratio = np.where(wt[..., None] > 0.15, ratio, 1.0)
    lm = ratio.mean(-1, keepdims=True); tint = (ratio / lm) * (1 + lum_keep * (lm - 1))
    tint = np.clip(tint, 0.7, 1.35)
    out = os.path.join(geo.ROOT, 'cities', slug)
    Image.fromarray(np.clip(tint / 2 * 255, 0, 255).astype(np.uint8)).save(os.path.join(out, 'ground_tint.png'))
    json.dump({'png': f'cities/{slug}/ground_tint.png', 'box': [-half, -half, half, half], 'scene': pick[1].rstrip('/').split('/')[-1]}, open(os.path.join(out, 'ground_tint.json'), 'w'))
    print('[colour] ground_tint', n, 'x', n, 'tint min/max', tint.min(0).min(0).round(2), tint.max(0).max(0).round(2), 'mean', tint.reshape(-1, 3).mean(0).round(3))


def main(argv):
    slug = argv[0]
    if '--tint' in argv: return bake_tint(slug)
    season = argv[argv.index('--season') + 1] if '--season' in argv else 'summer'
    years = tuple(int(v) for v in argv[argv.index('--years') + 1].split(',')) if '--years' in argv else (2024, 2025)
    n = int(argv[argv.index('--scenes') + 1]) if '--scenes' in argv else 3
    pal = derive(slug, season, years, n)
    pal['render'] = to_render(pal)
    out = os.path.join(geo.ROOT, 'cities', slug, 'palette.json' if season == 'summer' else f'palette_{season}.json')
    json.dump(pal, open(out, 'w'), indent=1)
    for k, v in pal['classes'].items(): print(f'  {k:8s} {v["median"]}  n={v["n"]}')
    print('[colour] scritto', out)


if __name__ == '__main__':
    main(sys.argv[1:])
