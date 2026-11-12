"""Eventi del montaggio (generalizza montaggio/eventi_roma.py): didascalie a tempo dall'anno, soste dalla regia, Subscribe.

Legge story (montaggio.events, montaggio.subscribe_t, regia.open.title_t, regia.soste[*].sub), lo schedule e gli anni
per fotogramma: montaggio/years_<slug>.json se c'e' (dal render), altrimenti ricavati dallo schedule (year_at), cosi'
il montaggio puo' partire PRIMA del render.
Scrive montaggio/eventi_<slug>.json: {didascalie:[{t_in,t_out,date,title,line,sober}], soste:[{t_in,t_out,title,sub}], subscribe_t}
Chiavi facoltative (pacing story, vedi STORY_SCHEMA.md; assenti = file identico a prima): cards[{t_in,t_out,date,title,lines,src}],
chapters[{t_in,t_out,num,title}], recap{t_in,t_out,text}, cta{t_in,t_out,text}, sources_card{t_in,t_out,items,no_ai}.
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


def roman(n):
    out = ''
    for v, r in ((10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')):
        while n >= v: out += r; n -= v
    return out


def story_extras(story, S, Y, after=9.5):
    """Cartelli, capitoli, recap, CTA e fonti del montaggio "story". S = schedule, Y = {frame: anno}. {} se la story non usa le chiavi."""
    MO = story.get('montaggio', {}) or {}
    mc = sorted(MO.get('cards') or [], key=lambda c: c['y']); ch_in = list(MO.get('chapters') or [])
    plan = S.get('end_plan') or {}
    if not (mc or ch_in or plan.get('recap') or plan.get('cta') or plan.get('sources')): return {}
    fr = sorted((int(k), v) for k, v in Y.items())

    def t_of(year):
        for f, y in fr:
            t = (f - 1) / FPS
            if t >= after and y >= year: return t
        return None
    out = {}; sc = S.get('cards') or []
    cards = []   # (y, card)
    for c in mc:
        m = next((x for x in sc if x['title'] == c['title'] and abs(x['y'] - c['y']) < 1e-6), None)
        if m: t0, t1 = m['t_in'], m['t_out']
        else:
            t0 = t_of(c['y'])
            if t0 is None: continue
            t1 = t0 + float(c.get('hold_s', 5.0))
        if t1 > S['duration'] - 1: continue
        cards.append((c['y'], {'t_in': round(t0, 2), 't_out': round(t1, 2), 'date': c.get('date') or yfmt(c['y']), 'title': c['title'],
                               'lines': list(c.get('lines', []))[:2], 'sober': bool(c.get('sober', False))}))
        if c.get('chapter'): ch_in.append({'y': c['y'], 'title': c['chapter']})
    if cards: out['cards'] = [c for _, c in cards]
    chs = []
    for n, ch in enumerate(sorted(ch_in, key=lambda c: c['y']), 1):
        nxt = next((c for y, c in cards if y >= ch['y']), None)
        tc = nxt['t_in'] if nxt else t_of(ch['y'])
        if tc is None: continue
        prev = max([c['t_out'] for _, c in cards if c['t_out'] <= tc - 0.01] or [after])
        a = min(max(tc - 2.8, prev), tc - 1.2)
        chs.append({'t_in': round(a, 2), 't_out': round(tc if nxt else a + 2.8, 2), 'num': roman(n), 'title': ch['title']})
    if chs: out['chapters'] = chs
    rc = MO.get('recap')
    if plan.get('recap'):
        a, b = plan['recap']
        txt = (rc.get('text') if isinstance(rc, dict) else None) or f"{int(round(story['city']['end_year'] - story['city']['start_year'])):,} years from one spot in {int(round(b - a))} seconds"
        out['recap'] = {'t_in': a, 't_out': b, 'text': txt}
    if plan.get('cta') and MO.get('cta'): out['cta'] = {'t_in': plan['cta'][0], 't_out': plan['cta'][1], 'text': MO['cta']}
    if plan.get('sources'):
        scd = MO.get('sources_card') if isinstance(MO.get('sources_card'), dict) else {}
        items = [re.sub(r'\s+', ' ', v.get('title', k)).strip() for k, v in (story.get('sources') or {}).items()]
        items = [(x if len(x) <= 78 else x[:75] + '...') for x in items][:int(scd.get('max', 14))]
        out['sources_card'] = {'t_in': plan['sources'][0], 't_out': plan['sources'][1], 'items': scd.get('items') or items,
                               'no_ai': scd.get('no_ai', 'NO AI: every frame is rendered from open data')}
    return out


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
    res.update(story_extras(story, S, Y, after))
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
