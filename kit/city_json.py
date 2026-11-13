"""Genera city_<slug>.json COMPLETO da cities/<slug>/story.json + style_preset (kit/presets.py).

Nessuna chiave resta al default NYC di build_render.py (lat0/lon0, grid_deg, hist, core_box, forest_box,
parks, roads, outer sono sempre scritte). Valida il risultato (chiavi, tipi, colori, box).

Uso:  python -m kit.city_json <slug> [--out city_<slug>.json] [--force] [--check-only]
Override opzionali nella story: city.style (dict che si fonde sullo stile del preset),
city.city_overrides (dict di chiavi top-level), city.cover (come in city_roma.json), city.shorts.
"""
import json, math, os, re, sys

from . import geo, presets

GEN_MARK = 'kit/city_json.py'
NYC_DEFAULT_KEYS = ['lat0', 'lon0', 'grid_deg', 'hist', 'core_box', 'forest_box', 'parks', 'roads', 'outer']
PASSTHROUGH = ['osm_pbf', 'catastro_zip', 'bbr_zip', 'bag_url', 'istat_basi', 'istat_dati', 'dem_tiles', 'dem_base', 'dem_exag',
               'min_area_m2', 'land_half_m', 'clip_radius_m']
HEX = re.compile(r'^#[0-9a-fA-F]{6}$')
FPS = 24


def _zone_extent(story, P, kinds=('zones', 'walls', 'gutting')):
    """Centro ed estensione (m) del centro storico: unione delle zone/mura della story; ripiego = 1500 m attorno all'origine."""
    pts = []
    H = story.get('history', {})
    for k in kinds:
        for z in H.get(k, []):
            for key in ('ring', 'line'):
                if z.get(key): pts += P.ring(z[key])
    if not pts:
        return 0.0, 0.0, 1500.0
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    e = max(400.0, max(max(xs) - min(xs), max(ys) - min(ys)) / 2)
    return cx, cy, e


def build_city(story):
    c = story['city']; slug = c['slug']
    P = geo.Proj.of(story)
    top, style = presets.preset(c.get('style_preset', 'mediterranean'))
    R = float(c.get('radius_m', 9000))
    span = float(c.get('end_year', 2026)) - float(c.get('start_year', 1200))
    cfg = {
        'name': slug,
        '_doc': f"{c.get('name', slug)} ({c.get('country', '')}). Generato da {GEN_MARK} da cities/{slug}/story.json "
                f"(preset '{c.get('style_preset', 'mediterranean')}'). Non modificare a mano: cambia la story e rigenera.",
        '_generated_by': GEN_MARK,
        'lat0': float(c['lat0']), 'lon0': float(c['lon0']), 'radius_m': R,
        'hist': f'hist_{slug}',
        'story': f'cities/{slug}/story.json',   # letto da kit/hist_kit.py dentro Blender (--city)
        # celle fini su tutto il raggio dati; niente base boschi (box nullo come Copenaghen/Siviglia/Parigi)
        'core_box': [-R, -R, R, R], 'forest_box': [0, 0, 1, 1],
        'parks': [], 'roads': [],
        # 'outer' esiste solo per NYC (boroughs.json): struttura valida ma neutra (mai urbano)
        'outer': {'centers': [[float(c['lat0']), float(c['lon0'])]], 'curve': [[0, 9999], [1, 9999]], 'max': 9999},
    }
    cfg.update(top)
    # blocchi di nascita/demolizione: con storie lunghe blocchi piu' larghi (Roma: 2.800 anni -> bin 10, dbin 50)
    if span > 1500: cfg['bin'], cfg['dbin'] = 10, 50
    elif span > 900: cfg['bin'], cfg['dbin'] = 6, 16
    for k in PASSTHROUGH:
        if k in c: cfg[k] = c[k]
    st = dict(style); st.update(c.get('style', {}))
    if 'night_off' in st and 'night_bld_off' not in c.get('style', {}):   # chiave vecchia nella story: si traduce nel nome letto
        st['night_bld_off'] = st.pop('night_off')
    st.pop('night_off', None)
    cfg['style'] = st
    # copertina: obliqua da sud sul centro storico, anni di inizio e fine (notte sull'ultimo se la regia ha la notte)
    cx, cy, e = _zone_extent(story, P)
    rg = story.get('regia', {})
    cfg['cover'] = c.get('cover') or {
        'cam': [round(cx - 0.35 * e), round(cy - 2.2 * e), round(1.1 * e), round(cx), round(cy + 0.1 * e), 0],
        'lens': 35, 'years': [int(c.get('start_year', 1200)), int(c.get('end_year', 2026))],
        'night_years': [int(c.get('end_year', 2026))] if rg.get('night') else []}
    # Shorts: con regia propria se il kit l'ha scritta, altrimenti tratto del lungo accelerato a ~30 s
    if c.get('shorts'):
        cfg['shorts'] = c['shorts']
    else:
        own = os.path.join(geo.ROOT, f'schedule_{slug}_shortA.json')
        if os.path.exists(own):
            nf = int(json.load(open(own))['duration'] * FPS)
            cfg['shorts'] = [['A', 1, nf, 1, f'schedule_{slug}_shortA.json', 2]]
        else:
            _d = rg.get('duration', 300)
            nf = int((float(_d) if isinstance(_d, (int, float)) and _d else 300.0) * FPS)   # 'auto'/assente: il lungo accelerato a ~30 s parte da 300 s nominali
            cfg['shorts'] = [['A', 1, nf, max(1, math.ceil(nf / (30 * FPS)))]]
    cfg.update(c.get('city_overrides', {}))
    return cfg


def validate(cfg):
    """Lista di errori (vuota = ok)."""
    err = []
    for k in NYC_DEFAULT_KEYS + ['style', 'bin', 'dbin', 'cover', 'shorts', 'radius_m']:
        if k not in cfg: err.append(f'manca la chiave {k} (resterebbe il default NYC)')
    for k in ('lat0', 'lon0', 'grid_deg', 'bin', 'dbin', 'radius_m'):
        if k in cfg and not isinstance(cfg[k], (int, float)): err.append(f'{k} non numerico')
    if 'lat0' in cfg and not (-90 < cfg['lat0'] < 90): err.append('lat0 fuori range')
    if 'lon0' in cfg and not (-180 < cfg['lon0'] < 180): err.append('lon0 fuori range')
    if abs(cfg.get('lat0', 0) - 40.758) < 1e-3 and abs(cfg.get('lon0', 0) + 73.985) < 1e-3 and cfg.get('name') != 'nyc':
        err.append('lat0/lon0 sono quelli di New York')
    for k in ('core_box', 'forest_box'):
        b = cfg.get(k)
        if not (isinstance(b, list) and len(b) == 4 and b[0] < b[2] and b[1] < b[3]): err.append(f'{k} non valido: {b}')
    if not isinstance(cfg.get('parks'), list): err.append('parks deve essere una lista')
    if cfg.get('hist') == 'hist_nyc' and cfg.get('name') != 'nyc': err.append("hist e' ancora hist_nyc")
    o = cfg.get('outer', {})
    if not all(k in o for k in ('centers', 'curve', 'max')): err.append('outer incompleto')
    st = cfg.get('style', {})
    for k in presets.STYLE_REQUIRED:
        if k not in st: err.append(f'style.{k} mancante')
    for k, v in st.items():
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if isinstance(x, str) and x.startswith('#') and not HEX.match(x): err.append(f'style.{k}: colore non valido {x}')
    cv = cfg.get('cover', {})
    if not (isinstance(cv.get('cam'), list) and len(cv['cam']) == 6 and cv.get('years')): err.append('cover incompleto (cam[6], years)')
    for s in cfg.get('shorts', []):
        if not (isinstance(s, list) and 4 <= len(s) <= 6): err.append(f'voce shorts non valida: {s}')
    if cfg.get('bin', 0) <= 0 or cfg.get('dbin', 0) <= 0: err.append('bin/dbin devono essere > 0')
    return err


def write(slug, out=None, force=False):
    story = geo.load_story(slug)
    cfg = build_city(story)
    err = validate(cfg)
    if err:
        raise ValueError('city json non valido:\n  ' + '\n  '.join(err))
    out = out or os.path.join(geo.ROOT, f'city_{slug}.json')
    if os.path.exists(out) and not force:
        old = json.load(open(out))
        if old.get('_generated_by') != GEN_MARK:
            raise FileExistsError(f'{out} esiste ed e\' scritto a mano: non lo sovrascrivo (usa --force)')
    with open(out, 'w') as f:
        json.dump(cfg, f, indent=1, ensure_ascii=False)
    return out, cfg


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a: print(__doc__); return 1
    slug = a[0]; out = a[a.index('--out') + 1] if '--out' in a else None
    if '--check-only' in a:
        p = out or os.path.join(geo.ROOT, f'city_{slug}.json')
        err = validate(json.load(open(p)))
        print('OK' if not err else '\n'.join(err)); return 0 if not err else 1
    p, cfg = write(slug, out, '--force' in a)
    print(f'[city_json] scritto {p}: preset {cfg["style"] and "ok"}, bin {cfg["bin"]}/{cfg["dbin"]}, core_box {cfg["core_box"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
