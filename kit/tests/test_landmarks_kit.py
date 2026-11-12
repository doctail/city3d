"""Test di kit/landmarks_kit.py:  /home/user/bl/bin/python -m pytest kit/tests/test_landmarks_kit.py -q
(oppure senza pytest: /home/user/bl/bin/python -m kit.tests.test_landmarks_kit)"""
import json, math, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from shapely.geometry import Polygon, Point   # noqa: E402
from kit import landmarks_kit as K   # noqa: E402

PH = [{'y': 1500, 'y1': 1520}]
TYPES = {'prism', 'wedge', 'hip', 'cyl', 'cone', 'dome', 'beam', 'helix'}


def variants():
    """Ogni preset (una volta per funzione) + varianti di stile importanti."""
    seen, out = set(), []
    for k, fn in K.PRESETS.items():
        if fn in seen: continue
        seen.add(fn); out.append((k, {}))
    out += [('bell_tower', {'style': s}) for s in ('baroque', 'romanesque', 'flat')]
    out += [('bell_tower', {'style': 'gothic', 'plan': 'octagon'})]
    out += [('tower_round', {'top': t}) for t in ('dome', 'crenel', 'flat', 'lantern')]
    out += [('tower_square', {'roof': t}) for t in ('spire', 'dome', 'onion', 'crenel', 'flat')]
    out += [('cathedral', {'crossing': c}) for c in ('dome', 'spire', 'none')]
    out += [('church_dome', {'plan': p}) for p in ('octagon', 'round')]
    out += [('gate_towers', {'tower_plan': p}) for p in ('D', 'round', 'square')]
    out += [('modern_shell', {'shape': s}) for s in ('ribs', 'helmet', 'arches', 'dome')]
    out += [('park_structure', {'kind': k}) for k in ('greenhouse', 'fountain', 'obelisk', 'statue', 'wheel', 'pagoda', 'pergola')]
    out += [('generic_footprint', {'roof': r}) for r in ('flat', 'parapet', 'gable', 'dome')]
    out += [('bullring', {'style': 'roman'}), ('skyscraper', {'plan': 'round', 'crown': 'pyramid'}), ('palace_courtyard', {'corner_towers': True}),
            ('wall_segment', {'tower': 'round', 'tower_top': 'pyramid'}), ('castle', {'cones': True})]
    return out


def build(kind, params, **extra):
    lm = dict({'name': f'{kind}', 'kind': kind, 'xy': [10.0, -20.0], 'phases': PH, 'params': dict(params, ang=17)}, **extra)
    return K.build_landmark(lm)


def check_part(p):
    t = p['t']; assert t in TYPES, t
    assert isinstance(p['c'], str) and p['c'].startswith('#') and len(p['c']) == 7, p['c']
    assert 0 < p.get('a', 1) <= 1
    for k, v in p.items():
        if isinstance(v, float): assert math.isfinite(v), (k, v)
    if 'r' in p:
        r = p['r']; assert len(r) >= 3
        g = Polygon(r); assert g.is_valid, ('anello non valido', r); assert g.area >= 0.3, ('anello degenere', g.area)
        assert len({tuple(q) for q in r}) == len(r), 'vertici ripetuti'
    if t == 'prism': assert p['z1'] > p['z0']
    if t in ('cyl', 'cone', 'helix'): assert p['z1'] > p['z0']
    if t == 'cyl': assert p['rad'] > 0
    if t == 'cone': assert p['r0'] > 0 and p['r1'] > 0
    if t == 'hip': assert p['rh'] > 0
    if t == 'dome': assert p['rad'] > 0 and p['hz'] > 0
    if t == 'wedge': assert p['zb'] >= p['za'] >= p['z0'] and math.hypot(*p['ax']) > 0.5
    if t == 'beam': assert math.dist(p['p0'], p['p1']) > 0.01 and p['w'] > 0 and p['h'] > 0
    assert '_f' not in p and '_g' not in p
    assert p['y'] >= PH[0]['y'] - 1e-6 and p['y'] <= PH[0]['y1'] + 1e-6
    if 'd' in p: assert p['d'] > p['y']


def test_shapes_valid():
    for kind, prm in variants():
        parts, clear, lab = build(kind, prm)
        assert parts, kind
        for p in parts: check_part(p)
        for r in clear: assert Polygon(r).is_valid
        assert lab and lab['z'] > 0 and abs(lab['from'] - min(p['y'] for p in parts)) < 0.01


def _base_of(p):
    if p['t'] == 'beam': return min(p['p0'][2], p['p1'][2]) - p['h'] / 2
    return p.get('z0', 0.0)


def test_supports_before_parts():
    """Quote crescenti: una parte che poggia su un'altra (centro dentro la sua impronta, base alla quota della sua cima)
    non compare prima di essa; la cima del monumento compare per ultima o quasi."""
    for kind, prm in variants():
        parts, _, _ = build(kind, prm)
        sh = [(p, K.part_shape(p)) for p in parts]
        for q in parts:
            qc = K.part_shape(q).centroid; zb = _base_of(q)
            if zb <= 0.5: continue
            for p, s in sh:
                if p is q or p['t'] == 'beam': continue
                if s.contains(qc) and abs(K.part_top(p) - zb) < 0.05 and K.part_top(p) > _base_of(p) + 0.5:
                    assert q['y'] >= p['y'] - 1e-6, (kind, prm, 'parte a', zb, 'prima del supporto', p['t'], p['y'], q['y'])
        top = max(parts, key=K.part_top)
        if kind not in ('wall_segment', 'bridge_arches'):   # opere lineari: costruite lungo il tracciato
            zt = K.part_top(top); top = max((p for p in parts if K.part_top(p) >= zt - 0.5), key=lambda p: p['y'])
            assert top['y'] >= sorted(p['y'] for p in parts)[len(parts) // 2], (kind, prm, 'la cima compare troppo presto')
        found = [p for p in parts if _base_of(p) <= 0.01]
        assert min(p['y'] for p in found) == min(p['y'] for p in parts), (kind, 'le fondazioni non sono le prime')


def test_phases_ordered_and_groups():
    lm = {'name': 'C', 'kind': 'cathedral', 'xy': [0, 0], 'params': {},
          'phases': [{'y': 1300, 'y1': 1340}, {'y': 1262, 'y1': 1290}, {'y': 1420, 'y1': 1425, 'groups': ['crossing']}]}
    parts, _, lab = K.build_landmark(lm)
    ys = [p['y'] for p in parts]
    assert min(ys) == 1262 and lab['from'] == 1262
    cr = [p for p in parts if p['y'] >= 1420]
    assert cr and all(1420 <= p['y'] <= 1425 for p in cr)
    rest = [p for p in parts if p['y'] < 1420]
    assert all(1262 <= p['y'] <= 1340 for p in rest)
    # fasi multiple senza groups: la seconda (in ordine di anno) prende la seconda meta' della sequenza
    assert any(1300 <= y <= 1340 for y in ys) and any(1262 <= y <= 1290 for y in ys)
    # senza y1: le parti compaiono comunque in sequenza (fondazioni prima della guglia)
    parts, _, _ = K.build_landmark({'name': 'T', 'kind': 'bell_tower', 'xy': [0, 0], 'phases': [{'y': 1400}]})
    assert min(p['y'] for p in parts) == 1400 and max(p['y'] for p in parts) > 1400


def test_demolition():
    parts, clear, lab = K.build_landmark({'name': 'G', 'kind': 'gate_towers', 'xy': [0, 0], 'phases': PH, 'demolished': [1865, 1868]})
    assert all('d' in p and 1865 <= p['d'] <= 1868 for p in parts)
    top = max(parts, key=K.part_top); base = min(parts, key=lambda p: p['y'])
    assert top['d'] <= base['d']          # dall'alto verso il basso
    assert clear == [] and lab['to'] == max(p['d'] for p in parts)
    parts, _, _ = K.build_landmark({'name': 'S', 'kind': 'cathedral', 'xy': [0, 0],
                                    'phases': [{'y': 1200, 'y1': 1250}, {'y': 1859, 'y1': 1860, 'groups': ['crossing'], 'd': 2019.3}],
                                    'params': {'crossing': 'spire'}})
    sp = [p for p in parts if p['y'] >= 1859]
    assert sp and all(p['d'] == 2019.3 for p in sp) and all('d' not in p for p in parts if p['y'] < 1859)


def _data_dir():
    d = tempfile.mkdtemp(prefix='lmkit_')
    blds = [{'r': [[-40, -15], [40, -15], [40, 15], [-40, 15]], 'h': 22.0, 'y': 1800},
            {'r': [[100, 100], [110, 100], [110, 110], [100, 110]], 'h': 9.0, 'y': 1900},
            {'r': [[110.5, 100], [120, 100], [120, 110], [110.5, 110]], 'h': 12.0, 'y': 1900}]
    json.dump(blds, open(os.path.join(d, 'buildings.json'), 'w'))
    return d


def test_footprint_auto_and_clear():
    d = _data_dir(); fps = K.Footprints(d)
    lm = {'name': 'Cat', 'kind': 'cathedral', 'xy': [5, 3], 'footprint': 'auto', 'phases': PH}
    parts, clear, _ = K.build_landmark(lm, None, fps)
    assert len(clear) == 1 and Polygon(clear[0]).contains(Point(0, 0)) and Polygon(clear[0]).area > 80 * 30
    xs = [q[0] for p in parts if 'r' in p for q in p['r']]
    assert min(xs) > -48 and max(xs) < 75     # dentro l'impronta (+ abside), asse lungo est-ovest
    # vicino (entro 30 m) e fp_merge (due particelle catastali)
    g, h = fps.find(105, 125)
    assert g is not None and abs(g.area - 100) < 1
    g, h = fps.find(105, 105, merge=1.0)
    assert g.area > 190 and h == 12.0
    g, h = fps.find(500, 500)
    assert g is None
    # generic_footprint usa l'altezza del catasto
    parts, clear, lab = K.build_landmark({'name': 'B', 'kind': 'generic_footprint', 'xy': [0, 0], 'footprint': 'auto', 'phases': PH, 'params': {'roof': 'flat'}}, None, fps)
    assert abs(max(p['z1'] for p in parts if p['t'] == 'prism') - 22.0) < 0.01


def test_cli_build_idempotent():
    d = _data_dir()
    story = {'version': 1, 'city': {'slug': 'kit_test_tmp', 'lat0': 39.4753, 'lon0': -0.3758, 'style_preset': 'mediterranean'},
             'landmarks': [{'name': 'Cathedral', 'kind': 'cathedral', 'at': [39.4753, -0.3758], 'footprint': 'auto', 'params': {'tower_ref': 'Micalet'},
                            'phases': [{'y': 1262, 'y1': 1300}]},
                           {'name': 'Micalet', 'kind': 'bell_tower', 'at': [39.4752, -0.3762], 'params': {'style': 'flat'}, 'phases': [{'y': 1381, 'y1': 1429}]},
                           {'name': 'Bridge', 'kind': 'bridge_arches', 'line': [[39.4780, -0.3770], [39.4790, -0.3770]], 'phases': [{'y': 1591, 'y1': 1596}]}]}
    sp = os.path.join(d, 'story.json'); json.dump(story, open(sp, 'w'))
    json.dump([{'name': 'Wall', 't': 'prism', 'r': [[0, 0], [5, 0], [5, 5]], 'z0': 0, 'z1': 8, 'c': '#cccccc', 'y': 1356}],
              open(os.path.join(d, 'landmarks_walls.json'), 'w'))
    json.dump({'parts': [], 'clear': [], 'labels': []}, open(os.path.join(d, 'landmarks.json'), 'w'))
    K.build(sp, d, montage=False, quiet=True)
    a = open(os.path.join(d, 'landmarks.json')).read()
    K.build(sp, d, montage=False, quiet=True)
    assert a == open(os.path.join(d, 'landmarks.json')).read()
    out = json.loads(a)
    assert os.path.exists(os.path.join(d, 'landmarks_legacy.json'))
    assert any(p['name'] == 'Wall' for p in out['parts']) and out['_kit']['wall_parts'] == 1
    assert {l['name'] for l in out['labels']} == {'Cathedral', 'Micalet', 'Bridge'}
    assert len(out['clear']) == 2      # cattedrale + campanile; il ponte non toglie edifici
    m = K.montage_labels(out['labels'])
    assert m['Micalet'][3] == 1381 and len(m['Micalet']) == 4 and m['Micalet'][2] > 50


if __name__ == '__main__':
    n = 0
    for k, f in list(globals().items()):
        if k.startswith('test_') and callable(f): f(); n += 1; print('ok', k)
    print(n, 'test passati')
