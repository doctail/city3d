"""Misura le due tracce del modello musicale "waking_monument" e scrive kit/music/waking_monument.json.

Traccia A = "Waking to Reality" (Unicorn Heads), dal secondo 0 del video.
Traccia B = "Monument" (TrackTribe), da B_START. Il cambio traccia si nasconde nell'evento piu' forte (climax).

Misura (stessa convenzione dei commenti di regia_copenhagen.py):
  - livello RMS in dB su finestre di 0,1 s; livello "1 s" = energia media della finestra di 1 s;
  - SALTO al tempo t = livello(t, t+1) - livello(t-1, t)  (finestre di 1 s);
  - punti forti = salti |dB| >= soglia, a distanza >= 4 s l'uno dall'altro;
  - CAMBIO STRUTTURALE (peso del punto) = livello medio 4 s dopo - 4 s prima;
  - fine/sfumatura: ultimo calo forte prima del silenzio finale.
Poi controlla le ancore scritte nei commenti di regia_copenhagen.py (tempo +-1,5 s, stesso segno).

Uso: python kit/music/analyze.py [A.mp3 B.mp3] [--out kit/music/waking_monument.json]
     (senza argomenti cerca le tracce nelle cartelle di upload note o in kit/music/*.mp3)
"""
import glob, json, os, re, shutil, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SR = 8000
HOP = 0.1


def ffmpeg_bin():
    for c in (shutil.which('ffmpeg'), '/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux'):
        if c and os.path.exists(c):
            return c
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit('ffmpeg non trovato (sistema, /opt/pw-browsers/ffmpeg-1011 o imageio-ffmpeg)')


def load(path):
    raw = subprocess.run([ffmpeg_bin(), '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def envelope(x):
    h = int(SR * HOP); n = len(x) // h
    e = (x[:n * h].reshape(n, h).astype(np.float64) ** 2).mean(1)
    return e   # energia per finestra di 0,1 s


def db(e):
    return 10 * np.log10(np.maximum(e, 1e-10))


def level(e, t0, t1):
    a, b = max(0, int(round(t0 / HOP))), min(len(e), int(round(t1 / HOP)))
    return float(db(e[a:b].mean())) if b > a else -100.0


def analyze(path, thr=3.0, sep=4.0):
    x = load(path); e = envelope(x); dur = len(x) / SR
    k = int(round(1.0 / HOP))
    c = np.convolve(e, np.ones(k) / k, 'valid')      # c[i] = media su [i, i+k)
    L1 = db(c)
    jumps = np.full(len(e), 0.0)
    for i in range(k, len(L1)):
        jumps[i] = L1[i] - L1[i - k]
    order = np.argsort(-np.abs(jumps)); used = []
    for i in order:
        if abs(jumps[i]) < thr: break
        t = i * HOP
        if t < 0.5 or t > dur - 0.5: continue
        if any(abs(t - u) < sep for u in used): continue
        used.append(t)
    med = float(np.median(db(e)[int(5 / HOP):int((dur - 5) / HOP)]))
    pts = []
    for t in sorted(used):
        j = float(jumps[int(round(t / HOP))])
        struct = level(e, t, t + 4) - level(e, t - 4, t)
        pts.append({'t': round(t, 1), 'db': round(j, 1), 'struct_db': round(struct, 1),
                    'kind': 'rise' if j > 0 else 'drop', 'level_after': round(level(e, t, t + 4), 1)})
    # silenzio finale e inizio della musica
    L = db(e)
    end_music = dur
    for i in range(len(L) - 1, 0, -1):
        if L[i] > med - 25: end_music = (i + 1) * HOP; break
    start_music = next((i * HOP for i in range(len(L)) if L[i] > med - 12), 0.0)
    curve = [[s, round(level(e, s, s + 5), 1)] for s in range(0, int(dur), 5)]
    # inizio della sfumatura finale: primo t (passo 0,5 s) negli ultimi 40 s in cui i 5 s prima stanno >= 6 dB sopra i 3 s
    # che iniziano 2 s dopo
    fade_out = None
    for t in np.arange(max(5.0, dur - 40), dur - 8, 0.5):
        if level(e, t - 5, t) - level(e, t + 2, t + 5) >= 6:
            fade_out = round(float(t), 1); break
    return {'fade_out': fade_out, 'file': os.path.basename(path), 'duration': round(dur, 2), 'median_db': round(med, 1),
            'start_music': round(start_music, 1), 'end_music': round(end_music, 1), 'points': pts, 'level_5s': curve}


# ---------- ancore dichiarate in regia_copenhagen.py ----------
def parse_comment_anchors(path=os.path.join(ROOT, 'regia_copenhagen.py')):
    """Legge le righe di commento iniziali: '<A|B>: ... +7,1 dB 0:30.8 ...' -> [(traccia, t, dB o None, testo)]."""
    txt = ''.join(l for l in open(path, encoding='utf-8').readlines()[:8] if l.startswith('#'))
    txt = txt.replace('\n#', ' ')
    out = []
    # Frammenti dopo "A " / "B:" fino alla traccia successiva
    segs = re.split(r'(?<![\w])(?=(?:A|B)(?:\s*:|\s+\+))', txt)
    cur = None
    for s in segs:
        m = re.match(r'(A|B)\s*:?', s)
        if m and s.strip().startswith(('A ', 'A:', 'B ', 'B:')):
            cur = m.group(1)
        if cur is None: continue
        for mm in re.finditer(r'([+-]\d+,\d)\s*dB\s*(\d+):(\d+(?:\.\d+)?)', s):
            out.append((cur, int(mm.group(2)) * 60 + float(mm.group(3)), float(mm.group(1).replace(',', '.')), mm.group(0)))
        for mm in re.finditer(r'CALO\s*([+-]\d+,\d)\s*dB\s*(\d+):(\d+(?:\.\d+)?)', s):
            pass  # gia' preso dal pattern precedente
        for mm in re.finditer(r'(sfuma da|cala|fine|piccolo calo)\s*(\d+):(\d+(?:\.\d+)?)', s):
            out.append((cur, int(mm.group(2)) * 60 + float(mm.group(3)), None, mm.group(0)))
    return out


def verify(anchors, A, B, tol=1.5):
    res = []
    for trk, t, dbv, txt in anchors:
        M = A if trk == 'A' else B
        cands = [p for p in M['points'] if abs(p['t'] - t) <= tol and (dbv is None or (p['db'] > 0) == (dbv > 0))]
        if not cands and ('fine' in txt) and abs(M['end_music'] - t) <= 2.0:
            res.append({'track': trk, 't': t, 'claimed': txt, 'measured_t': M['end_music'], 'ok': True, 'note': 'fine musica'}); continue
        if not cands and ('sfuma' in txt) and M.get('fade_out') is not None and abs(M['fade_out'] - t) <= 3.0:
            res.append({'track': trk, 't': t, 'claimed': txt, 'measured_t': M['fade_out'], 'ok': True, 'note': 'inizio sfumatura'}); continue
        p = min(cands, key=lambda p: abs(p['t'] - t)) if cands else None
        res.append({'track': trk, 't': t, 'claimed': txt, 'measured_t': p['t'] if p else None,
                     'measured_db': p['db'] if p else None, 'ok': bool(p)})
    return res


def build_model(A, B):
    """Modello musicale: B_START consigliato, punti forti in tempo di VIDEO, ruoli."""
    # B_START: ultimo calo forte di A (la coda si spegne) meno 1 s, arrotondato a 0,5 s
    finals = [p for p in A['points'] if p['db'] <= -8 and p['t'] > A['duration'] - 30]
    a_tail = finals[0]['t'] if finals else A['end_music']
    b_start = round((a_tail - 1.0) * 2) / 2
    # sfumatura di A: primo calo >= 6 dB tra due livelli a 5 s consecutivi negli ultimi 40 s, prima della coda
    a_fade = A['fade_out'] if A['fade_out'] and A['fade_out'] < a_tail - 5 else b_start - 12
    inner = [p for p in A['points'] if 20 < p['t'] < a_fade - 5]
    drop = min((p for p in inner if p['kind'] == 'drop'), key=lambda p: p['struct_db'], default=None)
    release = max((p for p in inner if p['kind'] == 'rise' and drop and p['t'] > drop['t']), key=lambda p: p['struct_db'], default=None)
    def plateaus(pts, t0, t1, mindb):
        # salite che portano la musica a un livello nuovo (piu' alto di tutti i precedenti)
        out, top = [], -999.0
        for p in pts:
            if p['t'] <= t0: top = max(top, p['level_after']); continue
            if p['t'] >= t1: break
            if p['kind'] == 'rise' and p['db'] >= mindb and p['level_after'] > top + 0.5: out.append(p)
            top = max(top, p['level_after'])
        return out
    hooks = plateaus(A['points'], 20, 70, 5.0)
    b_in = [p for p in B['points'] if 10 < p['t'] < B['duration'] - 30]
    b_rises = plateaus(B['points'], 10, 70, 4.0)[:2]
    # piccolo calo di B a meta' (coppia di cali entro 12 s, tra 90 e 160 s)
    b_dips = [p for p in b_in if p['kind'] == 'drop' and 90 < p['t'] < 160]
    # notte: calo di B dopo i 190 s, prima della coda
    night = next((p for p in b_in if p['kind'] == 'drop' and 190 < p['t'] < B['duration'] - 30 and p['db'] <= -4), None)
    duration = round((b_start + B['duration']) * 2) / 2
    slots = []
    def slot(role, t, w, prefer, src, note=''):
        slots.append({'role': role, 't': round(float(t), 2), 'weight': w, 'prefer': prefer, 'src': src, 'note': note})
    if hooks: slot('hook', hooks[0]['t'], 4, 'any', f"A {hooks[0]['t']} {hooks[0]['db']:+} dB", 'gancio: prima salita forte')
    if len(hooks) > 1: slot('hook2', hooks[1]['t'], 3, 'any', f"A {hooks[1]['t']} {hooks[1]['db']:+} dB", 'seconda salita')
    if drop: slot('drop', drop['t'], 8, 'disaster', f"A {drop['t']} {drop['db']:+} dB", 'calo: incendio/catastrofe')
    if release: slot('release', release['t'], 6, 'build', f"A {release['t']} {release['db']:+} dB", 'ripresa dopo il calo: rinascita, grande cantiere')
    slot('climax', a_fade + 3.0, 10, 'disaster', f'A sfuma da {a_fade}; B parte a {b_start}',
         "evento piu' forte: copre il cambio di traccia (deve durare oltre b_start)")
    for i, p in enumerate(b_rises):
        slot(f'b_rise{i + 1}', b_start + p['t'], 5 - i, 'any', f"B {p['t']} {p['db']:+} dB", 'salita di B')
    if b_dips:
        slot('b_dip', b_start + b_dips[0]['t'], 3, 'disaster', f"B {b_dips[0]['t']} {b_dips[0]['db']:+} dB",
             'piccolo calo (guerra/crisi)')
        if len(b_dips) > 1:
            slot('b_dip_end', b_start + b_dips[1]['t'], 2, 'any', f"B {b_dips[1]['t']} {b_dips[1]['db']:+} dB", 'fine del piccolo calo')
    if night: slot('night', round((b_start + night['t']) * 2) / 2, 0, 'night', f"B {night['t']} {night['db']:+} dB", 'calo finale: notte')
    slots.sort(key=lambda s: s['t'])
    return {'b_start': b_start, 'duration': duration, 'a_fade': a_fade, 'a_tail': a_tail,
            'night_t': round((b_start + night['t']) * 2) / 2 if night else None, 'night_b': night['t'] if night else None,
            'slots': slots}


def find_tracks(args):
    if len(args) >= 2: return args[0], args[1]
    pats = ['/root/.claude/uploads/*/*Waking_to_Reality*.mp3', os.path.join(HERE, '*Waking*.mp3')]
    pb = ['/root/.claude/uploads/*/*Monument*.mp3', os.path.join(HERE, '*Monument*.mp3')]
    a = next((g for p in pats for g in glob.glob(p)), None); b = next((g for p in pb for g in glob.glob(p)), None)
    if not a or not b: raise SystemExit('tracce non trovate: python kit/music/analyze.py A.mp3 B.mp3')
    return a, b


def main(argv):
    out = os.path.join(HERE, 'waking_monument.json')
    if '--out' in argv:
        i = argv.index('--out'); out = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    pa, pb = find_tracks(argv)
    A, B = analyze(pa), analyze(pb)
    model = build_model(A, B)
    checks = verify(parse_comment_anchors(), A, B)
    roles = {s['role']: s['t'] for s in model['slots']}
    doc = {
        '_doc': ('Modello musicale Year Built: A "Waking to Reality" (Unicorn Heads) dal secondo 0, B "Monument" (TrackTribe) '
                 'da b_start. Tempi delle slots = secondi di VIDEO (B gia\' spostata di b_start). Generato da kit/music/analyze.py: '
                 'salti di volume = livello 1 s dopo - 1 s prima; struct_db = 4 s dopo - 4 s prima. Ruoli: hook (gancio), '
                 'climax (evento piu\' forte, copre il cambio di traccia), release (ripresa dopo il calo), drop (calo), night (calo finale).'),
        'name': 'waking_monument',
        'tracks': {'A': {k: A[k] for k in ('file', 'duration', 'median_db', 'start_music', 'end_music', 'fade_out', 'points', 'level_5s')},
                   'B': {k: B[k] for k in ('file', 'duration', 'median_db', 'start_music', 'end_music', 'fade_out', 'points', 'level_5s')}},
        'b_start': model['b_start'], 'duration': model['duration'], 'a_fade': model['a_fade'],
        'night_b': model['night_b'], 'night_t': model['night_t'],
        'roles': roles,
        'slots': model['slots'],
        'checks_copenhagen': checks,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(doc, open(out, 'w'), ensure_ascii=False, indent=1)
    print(f"A {A['duration']} s  B {B['duration']} s  b_start consigliato {model['b_start']}  durata {model['duration']}  notte {model['night_t']}")
    for s in model['slots']:
        print(f"  {s['role']:10s} {int(s['t'] // 60)}:{s['t'] % 60:04.1f}  ({s['src']})  {s['note']}")
    print('Ancore dei commenti di regia_copenhagen.py:')
    for c in checks:
        print(f"  {'OK ' if c['ok'] else 'NO '} {c['track']} {c['claimed']:28s} misura {c.get('measured_t')} {c.get('measured_db') or ''}")
    print('->', out)
    return doc


if __name__ == '__main__':
    main(sys.argv[1:])
