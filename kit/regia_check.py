"""QA di regia (regola 26/11/2026): tempo morto e camera ferma con anno che avanza. Uso: python -m kit.regia_check <slug>"""
import json, sys, math
def yat(Y, t):
    for (a, ya), (b, yb) in zip(Y, Y[1:]):
        if a <= t <= b: return ya + (yb - ya) * (t - a) / max(b - a, 1e-9)
    return Y[-1][1] if t > Y[-1][0] else Y[0][1]
def check(sc, dead=10.0, still=8.0, dy=10.0, tgt=150.0, pos=300.0, hover_ok=0.0, path=False):
    # opt-in (default invariato). hover_ok > 0: una finestra che contiene >= hover_ok s di HOVER dichiarato (sosta: camera parcheggiata di proposito, anno fermo) non conta come 'ferma'.
    # path=True: sguardo/posizione misurati come ESCURSIONE MASSIMA nella finestra (ogni 1 s), non solo fra gli estremi (un panning che torna al punto di partenza non e' 'fermo')
    dur = sc['duration']; end0 = (sc.get('end_plan') or {}).get('cta') or [dur - 12, dur]
    T = dur if not end0 else end0[0]
    act = [(c['t_in'], c['t_out']) for c in sc['cards']] + [(s[0], s[1]) for s in sc['soste']]
    act = sorted(act); gaps = []; cur = float(sc.get('title_t', 0)) + 3
    for a, b in act:
        if a - cur > dead: gaps.append((cur, a))
        cur = max(cur, b)
    if T - cur > dead: gaps.append((cur, T))
    cam = sc['cam']; Y = sc['years']; ts = [c[0] for c in cam]
    import bisect
    def at(t): return cam[min(bisect.bisect_left(ts, t), len(cam) - 1)]
    stills = []; t = 0.0
    while t + still <= T:
        a, b = at(t), at(t + still)
        d_t = math.dist(a[2], b[2]); d_p = math.dist(a[1], b[1])
        if path: ws = [at(t + k) for k in range(0, int(still) + 1)]; d_t = max(math.dist(a[2], w[2]) for w in ws); d_p = max(math.dist(a[1], w[1]) for w in ws)
        dY = abs(yat(Y, t + still) - yat(Y, t))
        hv = sum(max(0.0, min(b_, t + still) - max(a_, t)) for a_, b_ in [(x[0], x[1]) for x in sc['soste']]) if hover_ok > 0 else 0.0
        if d_t < tgt and d_p < pos and dY > dy and not (hover_ok > 0 and hv >= hover_ok): stills.append((t, t + still, dY))
        t += 1.0
    m = []
    for s in stills:
        if m and s[0] <= m[-1][1]: m[-1] = (m[-1][0], s[1], max(m[-1][2], s[2]))
        else: m.append(s)
    return gaps, m
if __name__ == '__main__':
    for slug in [a for a in sys.argv[1:] if not a.startswith('--')]:
        sc = json.load(open(f'schedule_{slug}.json')); g, m = check(sc, hover_ok=2.0 if '--aware' in sys.argv else 0.0, path='--aware' in sys.argv)
        print(f"{slug}: tempo morto >10 s: {len(g)} " + ', '.join(f"{a:.0f}-{b:.0f}" for a, b in g))
        print(f"{slug}: camera ferma >8 s con anno +10: {len(m)} " + ', '.join(f"{a:.0f}-{b:.0f}s (+{y:.0f}a)" for a, b, y in m))
