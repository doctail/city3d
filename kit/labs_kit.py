"""Finestre delle etichette sui monumenti (generalizza montaggio/labs_roma.py).

Regole (come Roma): prima comparsa di un monumento (6 s, se nel quadro ed entro 150 anni dalla nascita), etichette
durante le soste, panoramica finale; solo se il monumento esiste ed e' nel quadro per >40% della finestra; max 4 insieme.
Monumenti: landmarks.json "labels" ({name,x,y,z,from,to}) della DATA, altrimenti story.landmarks con label=true.
Sosta -> etichette: regia.soste[*].labels se c'e', altrimenti l'etichetta piu' vicina al bersaglio (entro 250 m).
Posizioni sullo schermo: montaggio/labels_<slug>.json (labels_cam.py, bpy) se c'e'; altrimenti proiezione numpy
della camera dello schedule (pinhole 36 mm, interpolazione lineare delle chiavi): basta per decidere le finestre
prima del render. Scrive montaggio/labs_<slug>.json: {labs:[[t0,t1,[nomi]]], end:{nome:anno_fine}}.
Uso: python kit/labs_kit.py <slug | story.json> [--schedule F] [--eventi F] [--labels F] [--data DIR] [--out F]
     [--lm-out F]  (scrive anche il dict {nome:[x,y,h,anno]} da dare a labels_cam.py)
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit.geo import ROOT, load_story, Proj, data_dir as story_data_dir   # noqa: E402

FPS = 24; W, H = 1920, 1080


def label_points(story, ddir):
    """{nome: {x,y,z,from,to}}"""
    p = os.path.join(ddir, 'landmarks.json')
    LM = json.load(open(p)) if os.path.exists(p) else {'parts': []}
    out = {}
    for l in LM.get('labels', []) or []:
        out[l['name']] = {'x': l['x'], 'y': l['y'], 'z': l.get('z', 20), 'from': l.get('from', -9999), 'to': l.get('to', 9999)}
    if not out:
        pr = Proj.of(story)
        for l in story.get('landmarks', []):
            if not l.get('label'): continue
            ps = [q for q in LM['parts'] if q['name'].startswith(l['name'])]
            if ps:
                xs = [q.get('cx', np.mean([v[0] for v in q.get('r', [[0, 0]])])) for q in ps]
                ys = [q.get('cy', np.mean([v[1] for v in q.get('r', [[0, 0]])])) for q in ps]
                x, y = float(np.median(xs)), float(np.median(ys)); z = max(q.get('z1', q.get('z0', 0) + q.get('hz', 0)) for q in ps)
                y0 = min(q.get('y', 9999) for q in ps)
            else:
                x, y = pr.L(*l['at']); z = 20.0; y0 = (l.get('phases') or [{'y': -9999}])[0]['y']
            out[l['name']] = {'x': x, 'y': y, 'z': z, 'from': y0, 'to': l.get('end', 9999)}
    return out, LM


class Projector:
    """Proiezione dei punti con la camera dello schedule (bersaglio TRACK_TO, su = Z, sensore 36 mm orizzontale)."""

    def __init__(self, sched):
        C = sched['cam']
        self.T = np.array([c[0] for c in C]); self.P = np.array([c[1] for c in C], float); self.G = np.array([c[2] for c in C], float)
        self.MM = np.array([c[3] if len(c) > 3 else sched.get('lens', 35) for c in C], float)

    def __call__(self, t, pt):
        # chiavi a fotogramma: f = round(t*FPS)+1 -> uso t quantizzato come build_render
        cp = np.array([np.interp(t, self.T, self.P[:, k]) for k in range(3)])
        tg = np.array([np.interp(t, self.T, self.G[:, k]) for k in range(3)])
        mm = float(np.interp(t, self.T, self.MM))
        fwd = tg - cp; fwd /= np.linalg.norm(fwd) + 1e-9
        right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right) + 1e-9
        up = np.cross(right, fwd)
        v = np.asarray(pt, float) - cp
        z = float(v @ fwd)
        if z <= 0: return (0.0, 0.0, -1.0)
        f = mm / 36.0 * W
        return (W / 2 + f * float(v @ right) / z, H / 2 - f * float(v @ up) / z, z)


def run(story, schedule=None, eventi=None, labels=None, data_dir=None, out=None, lm_out=None, quiet=False):
    if isinstance(story, str): story = load_story(story)
    slug = story['city']['slug']; R = story.get('regia', {}) or {}
    S = json.load(open(schedule or os.path.join(ROOT, f'schedule_{slug}.json')))
    EV = json.load(open(eventi or os.path.join(ROOT, 'montaggio', f'eventi_{slug}.json')))
    Y = np.array(S['years'], float); DUR = S['duration']
    yr = lambda t: float(np.interp(t, Y[:, 0], Y[:, 1]))
    pts, LM = label_points(story, data_dir or story_data_dir(story))
    END = {n: v['to'] for n, v in pts.items() if v['to'] < 9999}
    if lm_out:
        json.dump({n: [v['x'], v['y'], v['z'], v['from']] for n, v in pts.items()}, open(lm_out, 'w'), ensure_ascii=False)
    lp = labels or os.path.join(ROOT, 'montaggio', f'labels_{slug}.json')
    if os.path.exists(lp):
        LB = json.load(open(lp)); F0 = LB['F0']; lmp = LB['lm']; src = lp

        def pos(n, t):
            if n not in lmp: return None
            i = int(t * FPS) + 1 - F0
            return lmp[n]['p'][i] if 0 <= i < len(lmp[n]['p']) else None
    else:
        PJ = Projector(S); src = 'proiezione dallo schedule'

        def pos(n, t):
            v = pts[n]; return PJ(round(t * FPS) / FPS, (v['x'], v['y'], v['z']))
    title_t = float((R.get('open') or {}).get('title_t', 9.5))

    def vis(n, t):
        p = pos(n, t)
        if p is None: return False
        x, y, z = p; y_ = yr(t)
        return z > 0 and 70 < x < 1850 and 180 < y < 900 and pts[n]['from'] <= y_ < END.get(n, 9999)
    wins = []
    for n in pts:
        for t in np.arange(title_t + 1.9, DUR - 1, 0.25):
            if vis(n, t) and yr(t) - pts[n]['from'] < 150: wins.append([round(float(t), 2), round(float(t) + 6, 2), [n]]); break
    # soste -> etichette
    def ctr(prefix):
        ps = [q for q in LM.get('parts', []) if q['name'].startswith(prefix)]
        if not ps: return None
        xs = [q.get('cx', np.mean([v[0] for v in q.get('r', [[0, 0]])])) for q in ps]
        ys = [q.get('cy', np.mean([v[1] for v in q.get('r', [[0, 0]])])) for q in ps]
        return float(np.median(xs)), float(np.median(ys))
    by_cap = {s['caption']: s for s in R.get('soste', [])}
    for t0, t1, y0, y1, cap in S['soste']:
        s = by_cap.get(cap, {}); names = s.get('labels')
        if names is None:
            tg = s.get('target', '')
            c = ctr(tg) if isinstance(tg, str) and not tg.startswith(('fire:', 'area:', 'xy:')) else None
            names = []
            if c:
                best = min(pts, key=lambda n: math.hypot(pts[n]['x'] - c[0], pts[n]['y'] - c[1]), default=None)
                if best and math.hypot(pts[best]['x'] - c[0], pts[best]['y'] - c[1]) < 250: names = [best]
        if names: wins.append([t0, t1, names])
    # cartelli del pacing story (schedule.cards): stesse regole delle soste, bersaglio = card.target / card.labels
    mcards = (story.get('montaggio', {}) or {}).get('cards') or []
    for c in S.get('cards', []) or []:
        mc = next((m for m in mcards if m['title'] == c['title'] and abs(m['y'] - c['y']) < 1e-6), {})
        names = mc.get('labels')
        if names is None:
            tg = mc.get('target', ''); names = []
            cc = ctr(tg) if isinstance(tg, str) and tg and not tg.startswith(('fire:', 'area:', 'xy:', 'water:')) else None
            if cc:
                best = min(pts, key=lambda n: math.hypot(pts[n]['x'] - cc[0], pts[n]['y'] - cc[1]), default=None)
                if best and math.hypot(pts[best]['x'] - cc[0], pts[best]['y'] - cc[1]) < 250: names = [best]
        if names: wins.append([c['t_in'], c['t_out'], names])
    fin = sorted(pts, key=lambda n: -pts[n]['z'])
    wins.append([round(DUR - 13, 2), round(DUR - 1.5, 2), fin[:8]])
    ok = []
    for a, b, ns in sorted(wins, key=lambda w: (w[0], w[1])):
        ns2 = [n for n in ns if n in pts and np.mean([vis(n, t) for t in np.arange(a, b, 0.5)]) > 0.4]
        ns2 = [n for n in ns2 if not any(a < w[1] and b > w[0] and n in w[2] for w in ok)]
        busy = sum(len(w[2]) for w in ok if a < w[1] and b > w[0])
        ns2 = ns2[:max(0, 4 - busy)]
        if ns2: ok.append([a, b, ns2])
    res = {'labs': ok, 'end': END}
    out = out or os.path.join(ROOT, 'montaggio', f'labs_{slug}.json')
    json.dump(res, open(out, 'w'), ensure_ascii=False)
    if not quiet:
        print(f'posizioni da: {src}')
        for w in ok: print(f'{int(w[0] // 60)}:{w[0] % 60:04.1f}  {round(yr(w[0]))}  {w[2]}')
        print('->', out)
    return res


def main(argv):
    if not argv: print(__doc__); return 1
    o = {argv[i][2:]: argv[i + 1] for i in range(1, len(argv) - 1) if argv[i].startswith('--')}
    run(argv[0], schedule=o.get('schedule'), eventi=o.get('eventi'), labels=o.get('labels'), data_dir=o.get('data'),
        out=o.get('out'), lm_out=o.get('lm-out'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
