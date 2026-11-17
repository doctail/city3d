"""Genera city_<slug>.json COMPLETO da cities/<slug>/story.json + style_preset (kit/presets.py).

Nessuna chiave resta al default NYC di build_render.py (lat0/lon0, grid_deg, hist, core_box, forest_box,
parks, roads, outer sono sempre scritte). Valida il risultato (chiavi, tipi, colori, box).

Uso:  python -m kit.city_json <slug> [--out city_<slug>.json] [--force] [--check-only]
Override opzionali nella story: city.look (palette reale + luce, vedi kit/colour_kit.py), city.style (dict che si fonde sullo stile del preset),
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



BUILDING_PALETTES = {
    # citta' industriale USA (Pittsburgh): mattone rosso-bruno, pietra grigia, tan; tetti in asfalto scuro; torri grigio/vetro azzurro. Niente giallo.
    'us_industrial': {   # v3 (correzione luminanza owner): mattone brunastro attenuato, pietra grigio-tan, tetti grigio medio, torri grigio chiaro/vetro blu-grigio
        'wall_old': ['#c3988b', '#cdcbc6', '#d3c7b5', '#b5897d'],
        'wall_new': ['#c5958b', '#b98c7e', '#d7d5ce', '#d8cebb', '#c7c5c0', '#cea597'],
        'wall_anc': ['#d7d5ce', '#c7c5c0', '#dadad5'],
        'wall_eras': [[1915, ['#c5958b', '#b98c7e', '#ac8479', '#cea597', '#bb9589', '#c7c5c0', '#d8cebb', '#c5958b']],
                      [1950, ['#cea597', '#bb9084', '#d8cebb', '#cfc8ba', '#c7c5c0', '#c5958b', '#dad9c4', '#ac8479']],
                      [9999, ['#d9d5c8', '#d0cdc2', '#dad9c4', '#c1bfba', '#c49a8d', '#dad7cd', '#cdc8bc', '#c7c5c0']]],
        'roof_old': ['#949498', '#a19d9a', '#948b86', '#85858a'], 'roof_new': ['#949498', '#a19d9a', '#85858a', '#aca8a3', '#948b86', '#bababe', '#88888c'],
        'wall_tall': ['#b4bac2', '#a3aab3', '#bfc3c7', '#c8c8c4', '#9199a3', '#b0b5ba'], 'roof_tall': ['#8e949c', '#9ca2a9'], 'tall_h': 35,
        'glass': ['#8fb0c6', '#9cbbd0', '#86a8c0'],
    },
}
def _rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def _hex(c): return '#%02x%02x%02x' % tuple(int(round(max(0, min(255, v)))) for v in c)
def _sat1(h, s, tol):
    r, g, b = _rgb(h); y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    r2, g2, b2 = (y + (v - y) * s for v in (r, g, b))
    if r > 0 and b > 0 and b2 > 0:   # il rapporto R/B resta entro tol dall'originale (niente ritorno al giallo)
        q = (r2 / b2) / (r / b); q = max(1 - tol, min(1 + tol, q)); r2 = b2 * (r / b) * q
    return _hex((r2, g2, b2))
def _saturate(st, cfg, s, tol, keys):
    for k, v in list(st.items()):
        if k not in keys: continue   # solo i colori del suolo della palette: edifici, cielo, luce restano com'erano
        if isinstance(v, str) and v[:1] == '#' and len(v) == 7: st[k] = _sat1(v, s, tol)
        elif isinstance(v, list) and v and all(isinstance(x, str) and x[:1] == '#' for x in v): st[k] = [_sat1(x, s, tol) for x in v]
    if cfg.get('field_colors'): cfg['field_colors'] = [_sat1(x, s, tol) for x in cfg['field_colors']]


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
    st = dict(style)
    # look reale (opzionale): city.look = {palette: "cities/<slug>/palette.json" (da kit/colour_kit.py), sun_color: [r,g,b], sky_horizon: [r,g,b] lineare, exposure, sun_energy, sky_light}
    # Senza city.look il json generato e' identico a prima.
    lk = c.get('look') or {}
    if lk.get('palette'):
        pal = json.load(open(os.path.join(geo.ROOT, lk['palette'])))['render']
        st.update(pal.get('style', {})); cfg.update(pal.get('top', {}))
    for k in ('sun_color', 'sun_energy', 'sky_light', 'sky_horizon', 'sky_tint'):
        if k in lk: st[k] = lk[k]
    if 'exposure' in lk: cfg['exposure'] = lk['exposure']
    for k in ('sky_ramp', 'sky_gain'):
        if k in lk: st[k] = lk[k]
    for k in ('sun_el', 'sun_rot'):
        if k in lk: cfg[k] = lk[k]
    # iterazione 2 (tutte opzionali, solo con city.look): saturation (x su luma, con rapporto R/B tenuto entro rb_tol dall'originale),
    # water_gain/water_shift (acqua piu' chiara e oliva), street_gain (strade = mediana 'built' x gain), view_look/view_transform, ground_tint
    if lk.get('saturation'): _saturate(st, cfg, float(lk['saturation']), float(lk.get('rb_tol', 0.045)), set(json.load(open(os.path.join(geo.ROOT, lk['palette'])))['render'].get('style', {})) if lk.get('palette') else set())
    if lk.get('water_gain') or lk.get('water_shift'):
        w0 = _rgb(st.get('water', '#3b4541')); w1 = _rgb(st.get('water2', st.get('water', '#485250')))
        g, sh = float(lk.get('water_gain', 1.0)), lk.get('water_shift', [0, 0, 0])
        st['water'] = _hex([w0[i] * g + sh[i] for i in range(3)]); st['water2'] = _hex([w1[i] * g + sh[i] for i in range(3)])
    if lk.get('water_color'):   # city.look.water_color: [colore, colore2] esadecimali dell'acqua (solo il materiale acqua); senza chiave nulla cambia
        _wc = lk['water_color']; st['water'] = _wc[0]; st['water2'] = _wc[1] if len(_wc) > 1 else _wc[0]
    if lk.get('street_gain') and st.get('urban'):
        st['street'] = _hex([v * float(lk['street_gain']) for v in _rgb(st['urban'][2])])
        if 'street_earth' not in st: st['street_earth'] = st['street']
    if lk.get('building_palette'):   # iterazione 3: tavolozza edifici per citta' (nome in BUILDING_PALETTES o dict di chiavi di stile); solo con city.look
        bp_ = lk['building_palette']; st.update(BUILDING_PALETTES[bp_] if isinstance(bp_, str) else bp_)
    if lk.get('water_coat'): st['water_coat'] = lk['water_coat']
    if lk.get('water_glint'): st['water_glint'] = lk['water_glint']   # Pittsburgh: rugosita' minima di acqua e coat (sole speculare = macchia bianca); senza chiave nulla cambia
    if lk.get('view_look'): cfg['look'] = lk['view_look']
    if lk.get('view_transform'): cfg['view_transform'] = lk['view_transform']
    if lk.get('ground_tint'):
        cfg['ground_tint'] = json.load(open(os.path.join(geo.ROOT, 'cities', slug, 'ground_tint.json')))
    st.update(c.get('style', {}))
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
