#!/usr/bin/env python3
"""Kit Year Built: effetti sonori sintetici + mix musica A/B + loudnorm -14 LUFS -> m4a. Generalizza sfx_roma.py.
Uso (dalla radice del repo):
  python3 montaggio/sfx_kit.py <slug> --A waking.mp3 [--B monument.mp3] [--story cities/<slug>/story.json] [--schedule schedule_<slug>.json]
                               [--eventi montaggio/eventi_<slug>.json] [--out out] [--test SECONDI]
Uscite: out/<slug>_audio.m4a (video lungo) e out/<slug>_short_audio.m4a (Short, durata short.n/24 s). Con --test N: solo i primi N secondi,
out/<slug>_audio_test.m4a.

Piazzamento: da story.regia.soste[*].fx (accoppiate alle soste di eventi_<slug>.json per didascalia "Titolo (data)", altrimenti per indice) e da
story.montaggio.events[*].fx (accoppiate per titolo alle didascalie). fx = "hammer" | {"fx":"hammer","dt":0.8,"gain":0.08,"n":6,...} | [lista di questi].
Nomi: hammer crowd fire bell boom water battle quake horn peal crash firework rocket alarm hum whoosh (parametri: vedi FX qui sotto).
Fissi: hum iniziale, whoosh del riavvolgimento (da years), boom all'arrivo, click+ding al Subscribe, hum+rintocchi finali (o hum+fuochi se notte).
Musica: A da 0; a schedule.b_start (o regia.music_cuts) passa a B, con il taglio coperto dalla sosta piu' vicina (boom/crash di copertura);
regia.music_cuts.a_return_sosta (o automatico se B e' troppo corta) riporta A. Mix -> ffmpeg loudnorm a due passaggi (I=-14, TP=-1.5) -> AAC 192k.
"""
import numpy as np, wave, json, sys, os, re, shutil, subprocess, argparse, inspect, tempfile
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
rng = np.random.default_rng(11)

# ======== sintesi (copiata da sfx_roma.py, identica) ========
def env(n, a, r):
    e = np.ones(n); a = min(a, n // 2); r = min(r, n // 2)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] = np.linspace(1, 0, r)
    return e
def lowpass(x, fc):   # filtro a un polo, vettoriale a blocchi (abbastanza per effetti)
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * fc / SR); return lfilter([1 - a], [1, -a], x)
def highpass(x, fc): return x - lowpass(x, fc)
def reverb(x, taps=((0.031, .5), (0.047, .38), (0.071, .3), (0.113, .22), (0.167, .15), (0.251, .1))):
    y = np.concatenate([x, np.zeros(int(0.3 * SR))])
    for d, g in taps: k = int(d * SR); y[k:k + len(x)] += g * x
    return y
def norm(x, peak=1.0): return x / (np.abs(x).max() + 1e-9) * peak
def bell(dur=6.0, f0=392.0):
    t = np.arange(int(dur * SR)) / SR; y = np.zeros_like(t)
    for r, g, d in ((0.5, .6, 3.5), (1.0, 1.0, 2.5), (1.19, .5, 1.8), (1.5, .35, 1.4), (2.0, .3, 1.0), (2.74, .2, .7), (3.76, .12, .5)):
        y += g * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / d)
    return reverb(y * env(len(t), 80, 4000))
def alarm_bells(dur=8.0):   # campane a martello (allarme incendio): colpi rapidi e irregolari
    out = np.zeros(int(dur * SR) + SR * 4); t = 0.0
    while t < dur:
        b = bell(2.5, rng.choice([523.0, 587.0, 494.0])); i = int(t * SR); out[i:i + len(b)] += 0.6 * b[:len(out) - i]; t += rng.uniform(0.35, 0.6)
    return out
def fire(dur=8.0, intensity=1.0):   # fuoco: rombo basso + crepitii
    n = int(dur * SR); t = np.arange(n) / SR
    roar = lowpass(rng.standard_normal(n), 260) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t + 1)) * 3
    cr = np.zeros(n)
    for _ in range(int(60 * dur * intensity)):
        i = rng.integers(0, n - 2000); L = rng.integers(80, 900); cr[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.3, 1.0)
    return (roar + highpass(cr, 1500) * 0.8) * env(n, int(1.2 * SR), int(2.0 * SR))
def boom(dur=2.8, low=120):
    n = int(dur * SR); t = np.arange(n) / SR
    y = lowpass(rng.standard_normal(n), low) * np.exp(-t / 0.55) * 6 + np.sin(2 * np.pi * 38 * t) * np.exp(-t / 0.35) * 0.6
    return reverb(y * env(n, 60, 4000))

def rocket(dur=1.6):   # razzo Congreve: fischio che scende + soffio
    n = int(dur * SR); t = np.arange(n) / SR; f = 1800 - 1100 * t / dur
    whistle = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25; hiss = highpass(rng.standard_normal(n), 2500) * 0.5
    return (whistle + hiss) * env(n, int(0.3 * SR), int(0.15 * SR))
def whoosh(dur=2.4, up=False):   # riavvolgimento
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); y = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        u = i / n; fc = 300 + 5000 * (u if up else 1 - u) ** 2; y[i:i + blk] = lowpass(x[i:i + blk], fc)
    return y * np.sin(np.pi * t / dur) ** 1.5
def hammer(n_hits=6, gap=0.42):   # cantiere: colpi secchi di martello e scalpello
    out = np.zeros(int((n_hits * gap + 1.5) * SR))
    for k in range(n_hits):
        L = int(0.12 * SR); h = rng.standard_normal(L) * np.exp(-np.arange(L) / (0.012 * SR)); h = highpass(h, 900) + 0.6 * np.sin(2 * np.pi * rng.uniform(1800, 2600) * np.arange(L) / SR) * np.exp(-np.arange(L) / (0.03 * SR))
        i = int((k * gap + rng.uniform(-0.05, 0.05)) * SR); i = max(0, i); out[i:i + L] += h * rng.uniform(0.6, 1.0)
    return reverb(out, ((0.05, .3), (0.11, .2), (0.19, .12)))
def horn(dur=3.2, f=110.0):
    t = np.arange(int(dur * SR)) / SR; vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR; y = sum(np.sin(k * ph) / k ** 1.2 for k in range(1, 12))
    return reverb(lowpass(y, 900) * env(len(t), int(.25 * SR), int(.8 * SR)))
def firework():   # razzo che sale + scoppio + crepitio
    up = rocket(1.0) * 0.6; bang = boom(1.6, 700) * 0.8; L = int(1.4 * SR); cr = np.zeros(L)
    for _ in range(140):
        i = rng.integers(0, L - 400); cr[i:i + 300] += rng.standard_normal(300) * np.exp(-np.arange(300) / 60)
    out = np.zeros(len(up) + len(bang) + L); out[:len(up)] += up; out[len(up):len(up) + len(bang)] += bang; out[len(up) + int(0.15 * SR):len(up) + int(0.15 * SR) + L] += highpass(cr, 2000) * 0.5
    return out
def city_hum(dur):   # notte: brusio urbano lontano
    n = int(dur * SR); return lowpass(rng.standard_normal(n), 180) * 1.5 * env(n, 3 * SR, 3 * SR)


def water(dur=5.0):   # acqua che scorre (taglio del fiume, tappo di Chapina)
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    y = lowpass(x, 700) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * t)) + highpass(lowpass(x, 3000), 900) * 0.35
    return y * env(n, int(0.8 * SR), int(1.5 * SR))
def crash(dur=2.6):   # crollo: colpo sordo + calcinacci
    n = int(dur * SR); t = np.arange(n) / SR; deb = np.zeros(n)
    for _ in range(120):
        i = rng.integers(int(0.1 * SR), n - 3000); L_ = rng.integers(200, 2500); deb[i:i + L_] += rng.standard_normal(L_) * np.exp(-np.arange(L_) / (L_ / 5)) * rng.uniform(0.2, 1.0) * np.exp(-t[i] / 1.2)
    return reverb(boom(dur, 160)[:n] * 0.9 + highpass(deb, 700) * 0.5)
def click():   # clic del mouse (Subscribe)
    n = int(0.06 * SR); y = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.004 * SR)); return highpass(y, 2000)
def ding(f0=1320.0):
    t = np.arange(int(1.2 * SR)) / SR; return (np.sin(2 * np.pi * f0 * t) + 0.4 * np.sin(2 * np.pi * f0 * 2.01 * t)) * np.exp(-t / 0.35)
def crowd(dur=5.0):   # folla dell'arena: boato che sale e scende
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    y = (lowpass(x, 1400) - lowpass(x, 250)) * (0.55 + 0.45 * np.sin(np.pi * t / dur) ** 0.7) * (1 + 0.2 * np.sin(2 * np.pi * 1.7 * t))
    return reverb(y * env(n, int(0.6 * SR), int(1.4 * SR)) * 3)
def quake(dur=5.0):   # terremoto: rombo profondo che cresce + crolli
    n = int(dur * SR); t = np.arange(n) / SR
    r = lowpass(rng.standard_normal(n), 70) * (np.minimum(1, t / 1.5)) * (1 + 0.5 * np.sin(2 * np.pi * 3.1 * t)) * 8
    out = r * env(n, int(0.2 * SR), int(1.5 * SR)); c = crash(2.6); i = int(1.8 * SR); out[i:i + len(c)] += c[:n - i] * 0.6
    return out
def battle(dur=4.0):   # assalto: corni + fuoco + crolli
    out = np.zeros(int((dur + 2) * SR)); h = horn(2.6, 98.0); out[:len(h)] += h * 0.5
    f = fire(dur, 0.8); out[int(0.8 * SR):int(0.8 * SR) + len(f)] += f * 0.6
    c = crash(2.4); i = int(1.6 * SR); out[i:i + len(c)] += c * 0.4
    return out

# ======== piazzamento generico ========
FX = {   # nome: (funzione, dt di default dall'inizio della sosta, gain, parametri di default)
    'hammer': (hammer, 0.8, 0.08, {'n_hits': 6}), 'crowd': (crowd, 0.3, 0.14, {'dur': 4.0}), 'fire': (fire, 0.2, 0.20, {'dur': 6.0, 'intensity': 1.2}),
    'bell': (bell, 0.3, 0.16, {}), 'boom': (boom, 0.0, 0.22, {'dur': 3.0, 'low': 90}), 'water': (water, 0.2, 0.10, {'dur': 4.0}),
    'battle': (battle, 0.2, 0.22, {'dur': 4.0}), 'quake': (quake, 0.0, 0.26, {'dur': 5.0}), 'horn': (horn, 0.2, 0.12, {'dur': 3.0, 'f': 82.0}),
    'peal': (None, 1.0, 0.12, {}), 'crash': (crash, 0.3, 0.16, {}), 'firework': (firework, 0.3, 0.16, {}), 'rocket': (rocket, 0.0, 0.20, {}),
    'alarm': (alarm_bells, 0.0, 0.13, {'dur': 6.0}), 'hum': (city_hum, 0.0, 0.08, {'dur': 6.0}), 'whoosh': (whoosh, 0.0, 0.22, {'dur': 3.0}),
}
ALIAS = {'n': 'n_hits', 'hits': 'n_hits', 'gap': 'gap', 'intensity': 'intensity', 'freq': 'f0'}
LOUD = {'battle', 'boom', 'quake', 'fire', 'crash', 'firework'}   # fx che coprono da soli un taglio musicale


def fx_list(spec):
    if spec is None: return []
    if isinstance(spec, (str, dict)): spec = [spec]
    return [{'fx': s} if isinstance(s, str) else dict(s) for s in spec]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug'); ap.add_argument('--A', default=os.environ.get('KIT_MUSIC_A')); ap.add_argument('--B', default=os.environ.get('KIT_MUSIC_B'))
    ap.add_argument('--story'); ap.add_argument('--schedule'); ap.add_argument('--eventi'); ap.add_argument('--out', default=os.path.join(ROOT, 'out'))
    ap.add_argument('--test', type=float, help='solo i primi N secondi (prova)'); ap.add_argument('--b-offset', type=float, default=5.0, help='secondo di B da cui parte')
    a = ap.parse_args(); slug = a.slug
    if not a.A or not os.path.exists(a.A): sys.exit('ERRORE: serve --A traccia.mp3 (o KIT_MUSIC_A)')
    pick = lambda *ps: next((p for p in ps if p and os.path.exists(p)), None)
    story_p = pick(a.story, f'{ROOT}/cities/{slug}/story.json'); sched_p = pick(a.schedule, f'{ROOT}/schedule_{slug}.json', f'{ROOT}/cities/{slug}/schedule_{slug}.json')
    ev_p = pick(a.eventi, f'{HERE}/eventi_{slug}.json'); years_p = pick(f'{HERE}/years_{slug}.json')
    if not (story_p and sched_p and ev_p): sys.exit(f'ERRORE: mancano story/schedule/eventi (trovati: {story_p}, {sched_p}, {ev_p})')
    story = json.load(open(story_p, encoding='utf-8')); S = json.load(open(sched_p, encoding='utf-8')); EV = json.load(open(ev_p, encoding='utf-8'))
    FULL = S['duration']; DUR = min(FULL, a.test) if a.test else FULL
    soste = S['soste']; rt = soste[0][0]; Y1 = story['city']['end_year']
    rs = 3.0
    if years_p:
        Y = json.load(open(years_p)); rs = next((((int(f) - 1) / 24) for f, y in sorted(Y.items(), key=lambda kv: int(kv[0])) if abs(y - Y1) > 1.0), 3.0)
    L = int((DUR + 3) * SR); fx = np.zeros(L); log = []

    def place(clip, t0, gain, peak=1.0):
        c = norm(np.asarray(clip, float), peak) * gain; i = int(t0 * SR)
        if i < 0 or i >= L: return
        m = min(len(c), L - i); fx[i:i + m] += c[:m]

    def peal(t0, notes=(392.0, 330.0, 294.0, 262.0), gap=0.75, rounds=2, gain=0.16):   # rintocchi a scala (campanile)
        k = 0
        for r in range(rounds):
            for f in notes: place(bell(4.0, f), t0 + k * gap, gain * (1 - 0.06 * k / len(notes))); k += 1

    def put(spec, t_base, tag=''):
        for sp in fx_list(spec):
            name = sp.pop('fx', None)
            if name not in FX: print(f'  [fx sconosciuto "{name}" in {tag}: saltato]'); continue
            fn, dt0, g0, kw0 = FX[name]; dt = sp.pop('dt', dt0); gain = sp.pop('gain', g0); t0 = t_base + dt
            if t0 >= DUR: continue
            if name == 'peal':
                kw = {k: (tuple(float(x) for x in v) if k == 'notes' else v) for k, v in sp.items() if k in ('notes', 'gap', 'rounds')}; peal(t0, gain=gain, **kw)
            else:
                kw = dict(kw0); par = inspect.signature(fn).parameters
                for k, v in sp.items():
                    k = ALIAS.get(k, k)
                    if k in par: kw[k] = v
                place(fn(**kw), t0, gain)
            log.append((round(t0, 1), name, tag))

    # ---- tempi delle soste (eventi json) accoppiati alle soste della story ----
    ev_by_cap = {f"{c['title']} ({c['sub']})" if c.get('sub') else c['title']: c for c in EV['soste']}
    sos_story = story.get('regia', {}).get('soste', [])
    times = []   # (t_in, t_out, titolo) per ogni sosta della story
    for i, s_ in enumerate(sos_story):
        c = ev_by_cap.get(s_.get('caption'))
        if c: times.append((c['t_in'], c['t_out'], s_['caption']))
        elif i < len(soste): times.append((soste[i][0], soste[i][1], s_.get('caption', f'#{i}')))
        else: times.append((None, None, s_.get('caption', f'#{i}'))); print(f'  [sosta {i} "{s_.get("caption")}" senza tempo]')
    # ---- fissi ----
    place(city_hum(3.2), 0.0, 0.10)                                  # citta' oggi
    place(whoosh(min(8.0, rt - rs + 0.2)), rs, 0.22)                 # riavvolgimento
    place(boom(3.0, 90), rt, 0.20)                                   # arrivo all'anno di partenza
    sub_t = EV.get('subscribe_t')
    if sub_t is not None: place(click(), sub_t, 0.20); place(ding(), sub_t + 0.08, 0.08)
    for (t0, t1, cap), s_ in zip(times, sos_story):
        if t0 is not None and s_.get('fx'): put(s_['fx'], t0, cap)
    for e in story.get('montaggio', {}).get('events', []):
        if not e.get('fx'): continue
        d = next((c for c in EV['didascalie'] if c['title'] == e['title']), None)
        if d: put(e['fx'], d['t_in'], 'didascalia ' + e['title'])
        else: print(f'  [didascalia "{e["title"]}" non trovata: fx saltato]')
    night_t = S.get('night_t')
    if night_t and night_t < FULL - 5:
        place(city_hum(FULL - night_t), night_t, 0.10)
        for d in (8.0, 10.6, 12.1, 15.5, 18.2, 19.0, 23.0):
            if night_t + d < FULL - 3: place(firework(), night_t + d, 0.16 * rng.uniform(0.7, 1.0))
    else:
        place(city_hum(10.0), FULL - 10.0, 0.08); peal(FULL - 7.0, notes=(330.0, 262.0), gain=0.07, rounds=1)

    # ---- musica: tagli A -> B (-> A), coperti dalla sosta piu' vicina ----
    def near(t):   # sosta piu' vicina a t (distanza dall'intervallo), -> inizio sosta
        c = [(0 if t0 <= t <= t1 else min(abs(t - t0), abs(t - t1)), t0) for t0, t1, _ in times if t0 is not None]
        return min(c)[1] if c else t
    def by_name(key):
        for t0, t1, cap in times:
            if t0 is not None and key.lower() in cap.lower(): return t0
        sys.exit(f'ERRORE: sosta "{key}" (regia.music_cuts) non trovata')
    mc = story.get('regia', {}).get('music_cuts', {})
    def mp3(p):
        raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', p, '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        return np.frombuffer(raw, '<i2').reshape(-1, 2).astype(float) / 32768
    A_ = mp3(a.A); B_ = mp3(a.B) if a.B and os.path.exists(a.B) else None
    N_ = int(DUR * SR); mus = np.zeros((N_, 2))
    def seg(src, a_off, t0, t1, fin, fout, gain=1.0):
        i0, i1 = int(t0 * SR), min(int(t1 * SR), N_)
        if i1 <= i0: return
        s_ = src[int(a_off * SR):int(a_off * SR) + (i1 - i0)]; n_ = len(s_); g = np.ones(n_); fi, fo = min(int(fin * SR), n_), min(int(fo_ := fout * SR), n_)
        if fi: g[:fi] = np.linspace(0, 1, fi) ** 0.7
        if fo: g[-fo:] = np.minimum(g[-fo:], np.linspace(1, 0, fo) ** 1.4)
        mus[i0:i0 + n_] += s_ * (g * gain)[:, None]
    LA = len(A_) / SR; cut1 = cut2 = None
    if B_ is not None and times:
        cut1 = by_name(mc['b_start_sosta']) if mc.get('b_start_sosta') else (near(S['b_start']) if S.get('b_start') else near(FULL * 0.5))
        LB = len(B_) / SR; need = FULL - cut1 + a.b_offset
        if mc.get('a_return_sosta'): cut2 = by_name(mc['a_return_sosta'])
        elif need > LB - 1.0:   # B finisce prima del video: torna A all'ultima sosta utile
            ok = [t0 for t0, _, _ in times if t0 is not None and t0 > cut1 + 20 and t0 - cut1 + 1.6 + a.b_offset <= LB - 1.0]
            cut2 = max(ok) if ok else None
        if cut2 is not None and cut2 - cut1 + 1.6 + a.b_offset > LB - 1.0: sys.exit(f'ERRORE: B troppo corta: servono {cut2 - cut1 + 1.6:.1f} s dopo {a.b_offset}s')
    FF_TXT = f'tagli musicali: A->B {cut1}, B->A {cut2}' if cut1 else 'musica: solo A'
    if cut1 is None or cut1 >= DUR:
        seg(A_, 0.0, 0.0, DUR, 0.0, 3.0)
    else:
        seg(A_, 0.0, 0.0, cut1 + 0.6, 0.0, 1.4)
        end_b = (cut2 + 1.6) if cut2 else DUR
        seg(B_, a.b_offset, cut1, end_b, 0.25, 1.6 if cut2 else 3.0, gain=0.62)
        if cut2 is not None and cut2 < DUR: seg(A_, max(0.0, LA - (FULL - cut2) - 0.5), cut2, DUR, 0.12, 3.0)
        for c_, name in ((cut1, 'A->B'), (cut2, 'B->A')):   # copertura del taglio: boom se la sosta non ha gia' un fx forte
            if c_ is None: continue
            sp = next((s_ for (t0, _, _), s_ in zip(times, sos_story) if t0 == c_), {})
            if not ({x['fx'] if isinstance(x, dict) else x for x in fx_list(sp.get('fx'))} & LOUD):
                place(boom(3.0, 80), c_ - 0.6, 0.20); place(crash(2.6), c_ + 1.4, 0.14); log.append((round(c_, 1), 'copertura ' + name, ''))
    st = mus * 0.82 + np.stack([fx[:N_], fx[:N_]], 1)

    # ---- scrittura + loudnorm a due passaggi ----
    os.makedirs(a.out, exist_ok=True); tmp = tempfile.mkdtemp()
    def finish(arr, name):
        w = os.path.join(tmp, name + '.wav')
        with wave.open(w, 'w') as f:
            f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(arr, -1, 1) * 32767).astype('<i2').tobytes())
        tgt = 'I=-14:TP=-1.5:LRA=11'
        r = subprocess.run([FFMPEG, '-hide_banner', '-i', w, '-af', f'loudnorm={tgt}:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        af = f"loudnorm={tgt}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
        o = os.path.join(a.out, name + '.m4a')
        subprocess.run([FFMPEG, '-loglevel', 'error', '-y', '-i', w, '-af', af, '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', o], check=True)
        r2 = subprocess.run([FFMPEG, '-hide_banner', '-i', o, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
        m2 = json.loads(r2.stderr[r2.stderr.rindex('{'):r2.stderr.rindex('}') + 1])
        print(f'ok {o}: {len(arr) / SR:.1f} s, misurato {float(m["input_i"]):.1f} LUFS -> {float(m2["input_i"]):.1f} LUFS, picco vero {float(m2["input_tp"]):.1f} dBTP'); return o
    print(f'{slug}: {len(log)} effetti, {FF_TXT}, durata {DUR:.1f}s, picco mix {float(np.abs(st).max()):.2f}')
    for t_, n_, tag in sorted(log): print(f'   {int(t_ // 60)}:{t_ % 60:04.1f}  {n_:<10} {tag}')
    finish(st, f'{slug}_audio' + ('_test' if a.test else ''))
    # ---- audio dello Short: B dal secondo b_offset se c'e', altrimenti A dal secondo 60; dissolvenza finale 1,5 s ----
    cfg_p = f'{HERE}/public/kit_{slug}.json'; sdur = (json.load(open(cfg_p))['short']['n'] / 24) if os.path.exists(cfg_p) else 28.0
    src, off = (B_, a.b_offset) if B_ is not None else (A_, 60.0)
    n = int(sdur * SR); sh = src[int(off * SR):int(off * SR) + n].copy(); g = np.ones(len(sh)); fo = min(int(1.5 * SR), len(sh)); g[-fo:] = np.linspace(1, 0, fo); g[:int(0.1 * SR)] = np.linspace(0, 1, int(0.1 * SR))
    finish(sh * g[:, None] * 0.85, f'{slug}_short_audio' + ('_test' if a.test else ''))
    shutil.rmtree(tmp, ignore_errors=True)


FFMPEG = shutil.which('ffmpeg') or next(iter(sorted(__import__('glob').glob('/opt/pw-browsers/ffmpeg-*/ffmpeg-linux'))), 'ffmpeg')
if __name__ == '__main__': main()
