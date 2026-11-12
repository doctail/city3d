"""Galleria di controllo dei preset di kit/landmarks_kit.py.

Una sola scena (tutti i preset affiancati su un terreno vuoto con un fiume) e piu' inquadrature in un solo lancio di
build_render.py: lo schedule ha una chiave camera per fotogramma (fotogrammi distanti 48 per tenere fermo l'anno).
Uso (dalla radice del repo):
  /home/user/bl/bin/python -m kit.tests.landmarks_gallery [OUT_DIR] [--shots 1,2,..] [--res 480 270]
DATA sintetica in /home/user/smoke/lm_data; immagini piccole in kit/tests/gallery/<nome>.jpg.
"""
import json, math, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from kit import landmarks_kit as K   # noqa: E402

DATA = '/home/user/smoke/lm_data'
PY = '/home/user/bl/bin/python'
CITY = os.path.join(HERE, 'fixtures', 'city_lmtest.json')
GAL = os.path.join(HERE, 'gallery')
PH = [{'y': 1900, 'y1': 1910}]


def lm(name, kind_, xy, **params):
    d = {'name': name, 'kind': kind_, 'xy': list(xy), 'phases': PH}
    for k in ('footprint', 'line_xy', 'demolished'):
        if k in params: d[k] = params.pop(k)
    d['params'] = params
    return d


LANDMARKS = [
    # fila A: torri (y = 240)
    lm('Square tower', 'tower_square', (-270, 240), h=34),
    lm('Square tower crenel', 'tower_square', (-240, 240), h=26, roof='crenel', belfry=False, c='stone'),
    lm('Round tower', 'tower_round', (-210, 240)),
    lm('Lighthouse', 'lighthouse', (-180, 240)),
    lm('Gothic bell tower', 'bell_tower', (-145, 240), style='gothic'),
    lm('Baroque bell tower', 'bell_tower', (-110, 240), style='baroque'),
    lm('Micalet-like tower', 'bell_tower', (-72, 240), style='flat'),
    lm('Romanesque tower', 'bell_tower', (-38, 240), style='romanesque'),
    lm('Castle', 'castle', (40, 240)),
    lm('Dome tower', 'tower_round', (110, 240), top='dome', belfry=True, c='brick'),
    # fila B: chiese e palazzi (y = 120)
    lm('Cathedral', 'cathedral', (-215, 120), footprint='auto', tower_ref='Cathedral tower', facade_towers=0),
    lm('Cathedral tower', 'bell_tower', (-262, 92), style='flat'),
    lm('Church', 'church', (-120, 120)),
    lm('Domed church', 'church_dome', (-50, 120)),
    lm('Gate', 'gate_towers', (30, 120)),
    lm('Gate D', 'gate_towers', (90, 120), tower_plan='D', gap=10, h=26),
    lm('Palace', 'palace_courtyard', (175, 120), corner_towers=True),
    # fila C: (y = 0)
    lm('Market', 'hall_market', (-230, 0)),
    lm('Station', 'station', (-115, 0), l=90, w=70),
    lm('Bullring', 'bullring', (5, 0), r_out=45),
    lm('Skyscraper', 'skyscraper', (95, 10), h=120, crown='spire'),
    lm('Round skyscraper', 'skyscraper', (135, -20), h=90, plan='round', crown='mast', c='glass2'),
    lm('Catastro building', 'generic_footprint', (205, 5), footprint='auto', roof='gable'),
    lm('Flat building', 'generic_footprint', (260, 0), roof='parapet', h=12, c='ochre'),
    # fiume (y -190..-125): mura sulla riva nord, ponte
    lm('City wall', 'wall_segment', (-180, -105), line_xy=[[-300, -105], [-160, -112], [-60, -100]], towers_every_m=40),
    lm('Stone bridge', 'bridge_arches', (0, -157), line_xy=[[0, -112], [0, -203]], n=5),
    # parco (y = -240)
    lm('Kiosk', 'park_structure', (-260, -245), kind='kiosk'),
    lm('Greenhouse', 'park_structure', (-215, -245), kind='greenhouse'),
    lm('Fountain', 'park_structure', (-170, -245), kind='fountain'),
    lm('Obelisk', 'park_structure', (-140, -245), kind='obelisk'),
    lm('Statue', 'park_structure', (-115, -245), kind='statue'),
    lm('Ferris wheel', 'park_structure', (-70, -245), kind='wheel'),
    lm('Pagoda', 'park_structure', (-30, -245), kind='pagoda'),
    lm('Pergola', 'park_structure', (10, -245), kind='pergola'),
    # fila D: moderni (y = -360)
    lm('Stadium', 'stadium', (-200, -390)),
    lm('Eye', 'modern_shell', (20, -330), shape='eye', ang=0),
    lm('Science museum', 'modern_shell', (40, -440), shape='ribs', l=180),
    lm('Opera', 'modern_shell', (230, -350), shape='helmet', ang=90),
    lm('Arches', 'modern_shell', (230, -470), shape='arches', l=120),
    # fila E: cattedrale senza impronta, due torri e cupola
    lm('Cathedral B', 'cathedral', (-180, -600), crossing='dome', tower_top='spire'),
    lm('Round gate', 'gate_towers', (-60, -600), tower_plan='round', h=24),
]

# inquadrature: nome -> (centro, ampiezza da inquadrare in m, azimut della camera in gradi da est, elevazione, anno)
VIEWS = [
    ('towers_a', (-215, 240, 18), 105, -95, 22, 2026),
    ('towers_b', (-75, 240, 18), 105, -95, 22, 2026),
    ('castle', (70, 240, 10), 110, -70, 35, 2026),
    ('cathedral', (-235, 112, 15), 115, -60, 32, 2026),
    ('churches', (-85, 120, 10), 110, -100, 32, 2026),
    ('gates', (60, 120, 10), 95, 85, 24, 2026),
    ('palace', (175, 120, 10), 95, -60, 40, 2026),
    ('civic', (-170, 0, 10), 190, -95, 38, 2026),
    ('arena_sky', (115, 0, 20), 220, -110, 32, 2026),
    ('river', (-120, -150, 5), 270, -60, 28, 2026),
    ('bridge', (0, -158, 4), 120, -20, 18, 2026),
    ('cathedral_b', (-140, -600, 15), 170, -70, 30, 2026),
    ('park', (-125, -245, 5), 165, 75, 32, 2026),
    ('modern', (110, -400, 5), 340, -80, 38, 2026),
    ('stadium', (-200, -390, 5), 270, -100, 40, 2026),
    ('phases_1903', (-235, 112, 15), 115, -60, 32, 1903.6),
    ('phases_1906', (-235, 112, 15), 115, -60, 32, 1906.0),
    ('phases_1909', (-235, 112, 15), 115, -60, 32, 1909.0),
]
LENS = 50.0


def shot(name, c, ext, az, el, yr):
    hf = 2 * math.atan(18 / LENS); d = ext / 2 / math.tan(hf / 2) * 1.08
    a, e = math.radians(az), math.radians(el)
    p = (c[0] + d * math.cos(e) * math.cos(a), c[1] + d * math.cos(e) * math.sin(a), c[2] + d * math.sin(e))
    return (name, tuple(round(v, 1) for v in p), c, LENS, yr)


SHOTS = [shot(*v) for v in VIEWS]


def make_data():
    os.makedirs(DATA, exist_ok=True)
    north = [[-700, -125], [700, -125], [700, 700], [-700, 700]]
    south = [[-700, -800], [700, -800], [700, -190], [-700, -190]]
    json.dump([{'ext': north, 'holes': []}, {'ext': south, 'holes': []}], open(f'{DATA}/land.json', 'w'))
    def rot(cx, cy, w, h, a):
        a = math.radians(a); out = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x, y = sx * w / 2, sy * h / 2
            out.append([round(cx + x * math.cos(a) - y * math.sin(a), 2), round(cy + x * math.sin(a) + y * math.cos(a), 2)])
        return out
    blds = [
        {'r': rot(-215, 120, 84, 38, 8), 'h': 20.0, 'y': 1850},                     # catasto della cattedrale (sparisce)
        {'r': [[190, -10], [225, -10], [225, 20], [208, 20], [208, 8], [190, 8]], 'h': 14.0, 'y': 1950},   # L: generic_footprint auto
        {'r': rot(300, 60, 20, 14, 0), 'h': 9.0, 'y': 1900},                        # casa normale (resta)
    ]
    json.dump(blds, open(f'{DATA}/buildings.json', 'w'))
    json.dump([], open(f'{DATA}/roads.json', 'w'))
    story = {'version': 1, 'city': {'slug': 'lmtest', 'name': 'Landmark test', 'lat0': 39.4753, 'lon0': -0.3758,
                                    'style_preset': 'mediterranean', 'start_year': 1800, 'end_year': 2026},
             'sources': {}, 'landmarks': LANDMARKS}
    sp = os.path.join(DATA, 'story.json'); json.dump(story, open(sp, 'w'), indent=1)
    out = K.build(sp, DATA, montage=False)
    return out


def make_city():
    if os.path.exists(CITY): return
    from kit import presets
    top, st = presets.preset('mediterranean')
    top.update({'name': 'lmtest', 'lat0': 39.4753, 'lon0': -0.3758, 'core_box': [-1200, -1200, 1200, 1200],
                'forest_box': [0, 0, 1, 1], 'parks': [], 'roads': [], 'hist': 'kit_no_hist', 'land_half_m': 2000,
                'land_from_buildings': False, 'block_trees': 0.0, 'park_trees': 0.0, 'merge_parts': True, 'style': st})
    json.dump(top, open(CITY, 'w'), indent=1)


def main(argv):
    out = argv[0] if argv and not argv[0].startswith('--') else '/home/user/smoke/lm_gallery'
    shots = SHOTS
    if '--shots' in argv: keep = argv[argv.index('--shots') + 1].split(','); shots = [s for s in SHOTS if s[0] in keep]
    res = argv[argv.index('--res') + 1:argv.index('--res') + 3] if '--res' in argv else ['480', '270']
    make_city(); make_data()
    # schedule: un fotogramma ogni 48 (2 s) per inquadratura, anno fermo attorno a ogni fotogramma
    cam, years, frames = [], [], []
    for i, (nm, p, t, lens, yr) in enumerate(shots):
        f = 1 + 48 * i; ts = (f - 1) / 24
        cam.append([ts, list(p), list(t), lens]); frames.append(f)
        years += [[max(0, ts - 0.9), yr], [ts + 0.9, yr]]
    sched = {'duration': 48 * len(shots) / 24 + 1, 'years': years, 'cam': cam, 'lens': 30}
    sp = os.path.join(DATA, 'schedule_gallery.json'); json.dump(sched, open(sp, 'w'))
    if os.path.isdir(out): shutil.rmtree(out)
    cmd = [PY, os.path.join(ROOT, 'build_render.py'), '--', DATA, out, '--frames', '1', str(frames[-1]), '--only', ','.join(map(str, frames)),
           '--res', *res, '--samples', '4', '--device', 'CPU', '--denoiser', 'none', '--schedule', sp, '--city', CITY]
    print(' '.join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-3000:], r.stderr[-3000:]); return r.returncode
    os.makedirs(GAL, exist_ok=True)
    for f, s in zip(frames, shots):
        src = os.path.join(out, f'{f:04d}.jpg')
        if os.path.exists(src): shutil.copy(src, os.path.join(GAL, f'{s[0]}.jpg'))
    print('galleria:', GAL, [s[0] for s in shots])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
