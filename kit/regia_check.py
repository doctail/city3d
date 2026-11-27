"""QA di regia (regola 26/11/2026): tempo morto e camera ferma con anno che avanza. Uso: python -m kit.regia_check <slug>"""
import json, sys, math
def yat(Y, t):
    for (a, ya), (b, yb) in zip(Y, Y[1:]):
        if a <= t <= b: return ya + (yb - ya) * (t - a) / max(b - a, 1e-9)
    return Y[-1][1] if t > Y[-1][0] else Y[0][1]
def check(sc, dead=10.0, still=8.0, dy=10.0, tgt=150.0, pos=300.0):
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
    flags = []; t = 0.0
    while t + still <= T:
        a, b = at(t), at(t + still)
        flags.append((t, math.dist(a[2], b[2]) < tgt and math.dist(a[1], b[1]) < pos)); t += 1.0
    m = []; cur = None
    for t, f in flags:   # tratti fermi contigui: l'anno si somma sull'intero tratto (fix 27/11: prima finestra di 8 s, mancava NYC-like)
        if f:
            if cur and t <= cur[1]: cur[1] = t + still
            else: cur = [t, t + still]; m.append(cur)
    m = [(a, b, abs(yat(Y, b) - yat(Y, a))) for a, b in m if b - a > still and abs(yat(Y, b) - yat(Y, a)) > dy]
    return gaps, m
if __name__ == '__main__':
    for slug in sys.argv[1:]:
        sc = json.load(open(f'schedule_{slug}.json')); g, m = check(sc)
        print(f"{slug}: tempo morto >10 s: {len(g)} " + ', '.join(f"{a:.0f}-{b:.0f}" for a, b in g))
        print(f"{slug}: camera ferma >8 s con anno +10: {len(m)} " + ', '.join(f"{a:.0f}-{b:.0f}s (+{y:.0f}a)" for a, b, y in m))
