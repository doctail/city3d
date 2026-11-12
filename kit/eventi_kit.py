"""Eventi del montaggio (generalizza montaggio/eventi_roma.py): didascalie a tempo dall'anno, soste dalla regia, Subscribe.

Legge story (montaggio.events, montaggio.subscribe_t, regia.open.title_t, regia.soste[*].sub), lo schedule e gli anni
per fotogramma: montaggio/years_<slug>.json se c'e' (dal render), altrimenti ricavati dallo schedule (year_at), cosi'
il montaggio puo' partire PRIMA del render.
Scrive montaggio/eventi_<slug>.json: {didascalie:[{t_in,t_out,date,title,line,sober}], soste:[{t_in,t_out,title,sub}], subscribe_t}
Uso: python kit/eventi_kit.py <slug | story.json> [--schedule F] [--years F] [--out F]
"""
import json, os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit.geo import ROOT, load_story   # noqa: E402

FPS = 24


def years_from_schedule(sched):
    """{"1": anno, ..., "N": anno} come years.json del render: anno al fotogramma f = years(t=(f-1)/FPS)."""
    Y = np.array(sched['years'], float); N = int(round(sched['duration'] * FPS))
    t = (np.arange(1, N + 1) - 1) / FPS
    return {str(f): round(float(v), 4) for f, v in zip(range(1, N + 1), np.interp(t, Y[:, 0], Y[:, 1]))}


def load_years(slug, sched, path=None):
    p = path or os.path.join(ROOT, 'montaggio', f'years_{slug}.json')
    if os.path.exists(p): return json.load(open(p)), p
    return years_from_schedule(sched), 'schedule'


def yfmt(y):
    y = int(round(y)) if abs(y - round(y)) < 0.01 else int(y)
    return f'{-y} BC' if y < 0 else (f'AD {y}' if y < 1000 else str(y))


def split_caption(txt):
    m = re.match(r'(.*?)\s*\(([^)]*)\)\s*$', txt)
    return (m.group(1), m.group(2)) if m else (txt, '')


def run(story, schedule=None, years=None, out=None, quiet=False):
    if isinstance(story, str): story = load_story(story)
    slug = story['city']['slug']; MO = story.get('montaggio', {}) or {}; R = story.get('regia', {}) or {}
    S = json.load(open(schedule or os.path.join(ROOT, f'schedule_{slug}.json')))
    Y, ysrc = load_years(slug, S, years)
    fr = sorted((int(k), v) for k, v in Y.items())
    after = float((R.get('open') or {}).get('title_t', 9.5))

    def t_of(year):
        for f, y in fr:
            t = (f - 1) / FPS
            if t >= after and y >= year: return t
        return None
    subs = {s['caption']: s['sub'] for s in R.get('soste', []) if s.get('sub')}
    soste = []
    for t0, t1, y0, y1, txt in S['soste']:
        title, sub = split_caption(txt)
        soste.append({'t_in': t0, 't_out': t1, 'title': title, 'sub': subs.get(txt, sub)})
    did, last = [], 0.0
    for e in sorted(MO.get('events', []), key=lambda e: e['y']):
        t = t_of(e['y'])
        if t is None:
            if not quiet: print(f"  [!] evento fuori dal video: {e['y']} {e.get('title')}")
            continue
        t = max(t, last + 0.4)
        li = e.get('line', '')
        dur = float(e.get('dur', 4.6 if len(li) < 60 else 5.4))
        if t + dur > S['duration'] - 1: continue
        did.append({'t_in': round(t, 2), 't_out': round(t + dur, 2), 'date': e.get('date') or yfmt(e['y']),
                    'title': e.get('title', ''), 'line': li, 'sober': bool(e.get('sober', False))})
        last = t + dur
    sub_t = MO.get('subscribe_t')
    if sub_t is None:   # primo momento dopo 90 s senza cartelli ne' soste per 6 s
        busy = [(d['t_in'], d['t_out']) for d in did] + [(s['t_in'], s['t_out']) for s in soste]
        sub_t = 90.0
        for t in np.arange(90.0, S['duration'] - 20, 0.5):
            if not any(a < t + 6 and b > t for a, b in busy): sub_t = float(t); break
    res = {'didascalie': did, 'soste': soste, 'subscribe_t': float(sub_t), '_years': ysrc}
    out = out or os.path.join(ROOT, 'montaggio', f'eventi_{slug}.json')
    json.dump({k: v for k, v in res.items() if not k.startswith('_')}, open(out, 'w'), ensure_ascii=False, indent=1)
    if not quiet:
        print(f'anni da: {ysrc}')
        for d in did: print(f"{int(d['t_in'] // 60)}:{d['t_in'] % 60:04.1f}  {d['date']:>8}  {d['title']}")
        print(f"{len(soste)} soste, subscribe a {sub_t} s -> {out}")
    return res


def main(argv):
    if not argv: print(__doc__); return 1
    o = {argv[i][2:]: argv[i + 1] for i in range(1, len(argv) - 1) if argv[i].startswith('--')}
    run(argv[0], schedule=o.get('schedule'), years=o.get('years'), out=o.get('out'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
