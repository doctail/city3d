"""Test del pacing "story" (regia_kit), camera continua, recap e chiavi grafiche (eventi_kit) su dati Valencia. Uso: python kit/tests/test_story_mode.py [outdir]"""
import copy, json, os, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, ROOT)
from kit import regia_kit, eventi_kit   # noqa: E402


def merge(a, b):
    for k, v in b.items():
        if k.startswith('_'): continue
        a[k] = merge(a.get(k, {}), v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return a


def story():
    st = regia_kit.load_story(os.path.join(ROOT, 'cities', 'valencia', 'story.json'))
    return merge(st, json.load(open(os.path.join(HERE, 'fixtures', 'story_valencia_cards.json'))))


def test_story_pacing(out=None):
    out = out or tempfile.mkdtemp(); st = story()
    r = regia_kit.run(st, out_dir=out, regia_dir=out, quiet=True)
    S = json.load(open(os.path.join(out, 'schedule_valencia.json')))
    assert S['pacing'] == 'story' and len(S['cards']) == 5 and len(S['soste']) == 2 and abs(S['duration'] - 150) < 1e-6
    Y = np.array(S['years']); yr = lambda t: float(np.interp(t, Y[:, 0], Y[:, 1]))
    # contatore a 0,2 anni/s su ogni cartello e soste, corsa <= 25 anni/s altrove
    for c in S['cards']:
        rate = (yr(c['t_out'] - 0.1) - yr(c['t_in'] + 0.1)) / (c['t_out'] - c['t_in'] - 0.2)
        assert abs(rate - 0.2) < 0.02, (c['title'], rate)
    ts = np.arange(0, S['duration'], 0.1); rt = np.gradient(np.array([yr(t) for t in ts]), ts)
    hold = np.zeros(len(ts), bool)
    for c in S['cards']: hold |= (ts > c['t_in'] - 0.25) & (ts < c['t_out'] + 0.25)
    for a, b, *_ in S['soste']: hold |= (ts > a - 0.25) & (ts < b + 0.25)
    rc = S['end_plan']['recap']; hold |= (ts < S['title_t'] + 4.5) | (ts > rc[0] - 0.6)
    assert np.abs(rt[~hold]).max() <= 25.5, np.abs(rt[~hold]).max()
    assert yr(rc[0] + 0.5) < 1300 and abs(yr(rc[1]) - 2026) < 1 and yr(rc[0] - 0.1) == 2026
    # camera continua: nessuno stacco (spostamento massimo tra chiavi a 0,25 s ragionevole) e recap fisso
    C = np.array([c[1] for c in S['cam']]); step = np.linalg.norm(np.diff(C, axis=0), axis=1)
    assert step.max() < 1600, step.max()
    ch = [c for c in S['cam'] if c[0] >= rc[0] + 0.5]
    assert max(np.ptp(np.array([c[1] for c in ch]), axis=0)) < 1
    return r, S


def test_default_unchanged():
    st = story(); st['regia'].pop('pacing'); st['regia'].pop('camera'); st['regia']['duration'] = 511.5; st['regia']['music'] = 'waking_monument'
    for k in ('cards', 'chapters', 'recap', 'cta', 'sources_card'): st['montaggio'].pop(k)
    r = regia_kit.run(st, write=False, quiet=True)
    assert 'pacing' not in r['sched'] and 'cards' not in r['sched'] and 'end_plan' not in r['sched']


def test_eventi(out=None):
    out = out or tempfile.mkdtemp(); st = story()
    regia_kit.run(st, out_dir=out, regia_dir=out, quiet=True)
    ev = eventi_kit.run(st, schedule=os.path.join(out, 'schedule_valencia.json'), out=os.path.join(out, 'eventi.json'), quiet=True)
    assert len(ev['cards']) == 5 and [c['num'] for c in ev['chapters']] == ['I', 'II'] and ev['recap'] and ev['cta'] and ev['sources_card']['items']
    assert ev['cards'][0]['date'] == '1238'
    return ev


if __name__ == '__main__':
    o = sys.argv[1] if len(sys.argv) > 1 else None
    r, S = test_story_pacing(o); test_default_unchanged(); test_eventi(o)
    print('OK', len(S['cards']), 'cartelli;', len(r['warnings']), 'avvisi:', *r['warnings'][:6], sep='\n  ')
