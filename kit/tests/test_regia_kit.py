"""Regressione della regia del kit su Copenaghen (fixture ricostruita da SOSTE e FIXED di regia_copenhagen.py).

Prepara la DATA se manca: scompatta data_copenhagen_src/*.gz in data_copenhagen/ e lancia hist_copenhagen.py.
Confronta con schedule_copenhagen.json: durata, soste (+-2 s), anni/secondo, camera; poi la variante con ancore
AUTOMATICHE e shot preset (senza cam/anchors della fixture) per vedere quanto si discosta.
Uso: python kit/tests/test_regia_kit.py   (o pytest kit/tests/test_regia_kit.py)
"""
import copy, gzip, json, os, shutil, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from kit import regia_kit, eventi_kit, labs_kit   # noqa: E402

FIX = os.path.join(HERE, 'fixtures', 'copenhagen_story.json')
DATA = os.path.join(ROOT, 'data_copenhagen')
REF = os.path.join(ROOT, 'schedule_copenhagen.json')


def prepare_data():
    os.makedirs(DATA, exist_ok=True)
    src = os.path.join(ROOT, 'data_copenhagen_src')
    for f in os.listdir(src):
        if f.endswith('.gz') and not os.path.exists(os.path.join(DATA, f[:-3])):
            with gzip.open(os.path.join(src, f)) as a, open(os.path.join(DATA, f[:-3]), 'wb') as b: shutil.copyfileobj(a, b)
    if not os.path.exists(os.path.join(DATA, 'hist.json')):
        subprocess.run([sys.executable, 'hist_copenhagen.py', 'data_copenhagen'], cwd=ROOT, check=True)


def rate_curve(years, dur):
    Y = np.array(years, float); ts = np.arange(12, dur - 52, 0.25)
    yv = np.interp(ts, Y[:, 0], Y[:, 1]); return ts, yv, np.gradient(yv, ts)


def compare(new, ref, tol=2.0):
    rep = {'duration': (new['duration'], ref['duration']), 'n_soste': (len(new['soste']), len(ref['soste']))}
    by = {s[4]: s for s in ref['soste']}
    dt = []
    for s in new['soste']:
        r = by.get(s[4])
        if r: dt.append((s[4], s[0] - r[0], s[1] - r[1]))
    rep['soste_dt'] = dt
    rep['soste_fuori_tol'] = [d for d in dt if abs(d[1]) > tol or abs(d[2]) > tol]
    ts, y1, r1 = rate_curve(new['years'], new['duration']); _, y2, r2 = rate_curve(ref['years'], ref['duration'])
    rep['anno_max_diff'] = float(np.abs(y1 - y2).max())
    rep['rate_mediana'] = (float(np.median(np.abs(r1))), float(np.median(np.abs(r2))))
    rep['rate_mae'] = float(np.mean(np.abs(np.abs(r1) - np.abs(r2))))
    C1 = np.array([c[1] for c in new['cam']]); C2 = np.array([c[1] for c in ref['cam']])
    T1 = np.array([c[0] for c in new['cam']]); T2 = np.array([c[0] for c in ref['cam']])
    tt = np.arange(0, ref['duration'], 0.5)
    p1 = np.stack([np.interp(tt, T1, C1[:, k]) for k in range(3)], 1); p2 = np.stack([np.interp(tt, T2, C2[:, k]) for k in range(3)], 1)
    rep['cam_keys'] = (len(new['cam']), len(ref['cam']))
    rep['cam_dist_mediana_m'] = float(np.median(np.linalg.norm(p1 - p2, axis=1)))
    rep['night'] = (new.get('night_t'), ref.get('night_t'), new.get('b_start'), ref.get('b_start'))
    return rep


def run_fixture(story, out):
    return regia_kit.run(story, data_dir=DATA, out_dir=out, regia_dir=out, quiet=True)


def test_copenhagen_fixture():
    prepare_data()
    ref = json.load(open(REF)); out = tempfile.mkdtemp()
    r = run_fixture(regia_kit.load_story(FIX), out)
    new = json.load(open(os.path.join(out, 'schedule_copenhagen.json')))
    rep = compare(new, ref)
    assert abs(new['duration'] - ref['duration']) < 1e-6
    assert rep['n_soste'][0] == rep['n_soste'][1]
    assert not rep['soste_fuori_tol'], rep['soste_fuori_tol']
    assert rep['anno_max_diff'] < 5.0
    assert os.path.exists(os.path.join(out, 'schedule_copenhagen_night.json'))
    return rep, r


def test_copenhagen_auto():
    """Stessa story senza ancore manuali ne' cam: ancore automatiche dal modello musicale e shot preset."""
    prepare_data()
    st = regia_kit.load_story(FIX); st = copy.deepcopy(st)
    R = st['regia']
    for k in ('anchors', 'open_shots', 'night_shots', 'night_t', 'b_start'): R.pop(k, None)
    R['anchors_auto'] = True
    for s in R['soste']: s.pop('cam', None)
    out = tempfile.mkdtemp()
    r = run_fixture(st, out)
    new = json.load(open(os.path.join(out, 'schedule_copenhagen.json')))
    rep = compare(new, json.load(open(REF)))
    assert abs(new['duration'] - 511.5) < 1e-6
    roles = {a[2]: (a[0], a[3]) for a in r['anchors']}
    return rep, r, roles


def test_montaggio():
    prepare_data()
    out = tempfile.mkdtemp()
    st = regia_kit.load_story(FIX)
    run_fixture(st, out)
    ev = eventi_kit.run(st, schedule=os.path.join(out, 'schedule_copenhagen.json'), out=os.path.join(out, 'eventi.json'), quiet=True)
    assert len(ev['soste']) == 26 and ev['didascalie']
    lb = labs_kit.run(st, schedule=os.path.join(out, 'schedule_copenhagen.json'), eventi=os.path.join(out, 'eventi.json'),
                      data_dir=DATA, out=os.path.join(out, 'labs.json'), quiet=True)
    assert lb['labs'] and 'end' in lb
    return ev, lb


def _print(rep):
    for k, v in rep.items():
        if k == 'soste_dt':
            big = sorted(v, key=lambda d: -max(abs(d[1]), abs(d[2])))[:5]
            print(f'  soste dt (peggiori): ' + '; '.join(f'{c[:28]} {a:+.2f}/{b:+.2f}' for c, a, b in big))
        else:
            print(f'  {k}: {v}')


if __name__ == '__main__':
    rep, r = test_copenhagen_fixture()
    print('FIXTURE (soste+FIXED di regia_copenhagen.py) vs schedule_copenhagen.json:'); _print(rep)
    print('  avvisi:', r['warnings'])
    rep, r, roles = test_copenhagen_auto()
    print('AUTO (ancore dal modello musicale, shot preset):'); _print(rep)
    for a in sorted(r['anchors']): print(f'  ancora {regia_kit.fmt_t(a[0])} {a[1]:.2f} {a[2]}: {a[3]}')
    print('  avvisi:', r['warnings'])
    ev, lb = test_montaggio()
    print(f"MONTAGGIO: {len(ev['didascalie'])} didascalie, {len(ev['soste'])} soste, subscribe {ev['subscribe_t']}, {len(lb['labs'])} finestre etichette")
    print('OK')
