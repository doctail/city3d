# Effetti sonori sintetici + mix delle due tracce per Roma (4 nov 2026). Funzioni copiate da sfx_parigi.py.
# Uso: python3 sfx_roma.py schedule_roma.json WAKING.mp3 MONUMENT.mp3 eventi_roma.json  -> roma_mix.wav
import numpy as np, wave, json, sys
SR = 44100
SCHED = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'schedule_roma.json'))
DUR = SCHED['duration']; rng = np.random.default_rng(11)
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
def peal(t0, notes=(392.0, 330.0, 294.0, 262.0), gap=0.75, rounds=2, gain=0.16):   # rintocchi a scala (campanile)
    k = 0
    for r in range(rounds):
        for f in notes: place(bell(4.0, f), t0 + k * gap, gain * (1 - 0.06 * k / len(notes))); k += 1

L = int((DUR + 3) * SR); fx = np.zeros(L)
def place(clip, t0, gain, peak=1.0):
    c = norm(np.asarray(clip, float), peak) * gain; i = int(t0 * SR); m = min(len(c), L - i)
    if m > 0: fx[i:i + m] += c[:m]

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

L = int((DUR + 3) * SR); fx = np.zeros(L)
def place(clip, t0, gain, peak=1.0):
    c = norm(np.asarray(clip, float), peak) * gain; i = int(t0 * SR); m = min(len(c), L - i)
    if m > 0: fx[i:i + m] += c[:m]
def peal(t0, notes=(392.0, 330.0, 294.0, 262.0), gap=0.75, rounds=2, gain=0.16):
    k = 0
    for r in range(rounds):
        for f in notes: place(bell(4.0, f), t0 + k * gap, gain * (1 - 0.06 * k / len(notes))); k += 1
EV = json.load(open(sys.argv[4] if len(sys.argv) > 4 else 'eventi_roma.json'))
def T(key, kind='any'):
    for c in (EV['soste'] if kind != 'cap' else []) + (EV['didascalie'] if kind != 'sosta' else []):
        if key.lower() in (c['title'] + ' ' + c.get('sub', '')).lower(): return c['t_in']
    print('  [effetto saltato: manca]', key); return None
def at(key, clip, dt, gain, kind='any'):
    t_ = T(key, kind)
    if t_ is not None: place(clip, t_ + dt, gain)
place(city_hum(3.2), 0.0, 0.10)                                  # Roma oggi
place(whoosh(5.2), 3.0, 0.22)                                    # riavvolgimento 2026 -> 753 a.C.
place(boom(3.0, 90), 8.0, 0.20)                                  # arrivo nel 753 a.C.
at('Romulus', hammer(5, 0.6), 4.0, 0.06, 'sosta')
at('Temple of Jupiter', hammer(6), 0.8, 0.08, 'sosta')
at('Gauls', battle(4.0), 0.2, 0.20, 'cap')
at('Servian Wall', hammer(7), 0.8, 0.09, 'sosta')
at('Circus Maximus', crowd(3.5), 0.3, 0.12, 'sosta')
at('Caesar and Augustus', hammer(8), 0.8, 0.08, 'sosta')
at('Great Fire', fire(6.0, 1.2), 0.2, 0.20, 'cap')
t_ = T('The Colosseum', 'sosta')
if t_: place(hammer(9, 0.32), t_ + 0.4, 0.09); place(crowd(5.0), t_ + 3.6, 0.16)   # cantiere, poi l'inaugurazione dell'80
at('Pantheon', hammer(6), 1.0, 0.08, 'sosta')
place(click(), EV['subscribe_t'], 0.20); place(ding(), EV['subscribe_t'] + 0.08, 0.08)
t_ = T('Aurelian Walls', 'sosta')
if t_:
    for d in (0.5, 2.2, 3.9): place(hammer(7), t_ + d, 0.08)
# 410: Alarico. COPRE il cambio di traccia A -> B (CUT1)
CUT1 = T('Alaric', 'sosta')
place(battle(4.0), CUT1 - 0.4, 0.26); place(crash(2.6), CUT1 + 1.6, 0.18); place(boom(3.0, 70), CUT1 - 0.6, 0.18)
at('end of the Western Empire', horn(3.0, 82.0), 0.2, 0.12, 'cap')
t_ = T('aqueducts', 'sosta')                                     # la citta' si svuota: acqua che si ferma, crolli lontani
if t_:
    place(water(3.0), t_ + 0.2, 0.10)
    for k, d in enumerate((2.0, 3.6, 5.2)): place(crash(2.2), t_ + d, 0.10 - 0.02 * k)
at('Earthquake', quake(5.0), 0.0, 0.26, 'sosta')
at('Sack of Rome', battle(4.0), 0.2, 0.18, 'cap')
at("New St Peter", hammer(8), 0.6, 0.08, 'sosta')
t_ = T("Michelangelo's dome", 'sosta')
if t_: peal(t_ + 2.4, gain=0.14, rounds=1)
t_ = T("Bernini", 'sosta')
if t_: peal(t_ + 1.0, notes=(523.0, 440.0, 392.0), gain=0.10, rounds=1)
# 1870-71 Porta Pia: cannoni. COPRE il cambio di traccia B -> A (CUT2)
CUT2 = T('capital of Italy', 'sosta')
for k, d in enumerate((-0.9, -0.3, 0.3, 1.0, 1.9)): place(boom(2.6, 70 + 15 * k), CUT2 + d, 0.28 - 0.03 * k)
at('Vittoriano', hammer(7), 0.8, 0.08, 'sosta')
t_ = T('Liberation', 'cap')
if t_: peal(t_ + 0.3, gain=0.13, rounds=1)
at('Olympics', crowd(3.5), 0.2, 0.14, 'sosta')
place(city_hum(10.0), DUR - 10.0, 0.08)
peal(DUR - 7.0, notes=(330.0, 262.0), gain=0.07, rounds=1)

# ---- musica: A = Waking to Reality (4:32), B = Monument (4:11). A 0 -> CUT1 (Alarico, 410), B dal suo secondo 5 CUT1 -> CUT2
# (Porta Pia, 1870), A di nuovo allineata alla fine. Con una sola traccia (B assente): A dall'inizio alla fine (dura quanto il video).
import subprocess, os
def mp3(p):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<i2').reshape(-1, 2).astype(float) / 32768
A_ = mp3(sys.argv[2]); B_ = mp3(sys.argv[3]) if len(sys.argv) > 3 and os.path.exists(sys.argv[3]) else None
N_ = int(DUR * SR); mus = np.zeros((N_, 2))
def seg(src, a_off, t0, t1, fin, fout, gain=1.0):
    i0, i1 = int(t0 * SR), min(int(t1 * SR), N_); s_ = src[int(a_off * SR):int(a_off * SR) + (i1 - i0)]; n_ = len(s_)
    g = np.ones(n_); fi, fo = int(fin * SR), int(fout * SR)
    if fi: g[:fi] = np.linspace(0, 1, fi) ** 0.7
    if fo: g[-fo:] = np.minimum(g[-fo:], np.linspace(1, 0, fo) ** 1.4)
    mus[i0:i0 + n_] += s_ * (g * gain)[:, None]
LA = len(A_) / SR
if B_ is None:
    seg(A_, 0.0, 0.0, DUR, 0.0, 3.0)
else:
    LB = len(B_) / SR; A2 = LA - (DUR - CUT2) - 0.5
    assert CUT2 - CUT1 + 5.0 <= LB - 1.0, f'B troppo corta: servono {CUT2 - CUT1:.1f} s'
    seg(A_, 0.0, 0.0, CUT1 + 0.6, 0.0, 1.4)
    seg(B_, 5.0, CUT1, CUT2 + 1.6, 0.25, 1.6, gain=0.62)
    seg(A_, max(0.0, A2), CUT2, DUR, 0.12, 3.0)
st = mus * 0.82 + np.stack([fx[:N_], fx[:N_]], 1)
with wave.open('roma_mix.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())
print(f'ok mix: CUT1 {CUT1:.1f} CUT2 {CUT2:.1f} durata {DUR:.0f}; picco', round(float(np.abs(st).max()), 3))

# ---- audio dello Short (28 s): B dal suo secondo 5 se c'e', altrimenti A dal secondo 60; dissolvenza in 1,5 s ----
src, off = (B_, 5.0) if B_ is not None else (A_, 60.0)
n = int(28 * SR); sh = src[int(off * SR):int(off * SR) + n].copy(); g = np.ones(len(sh)); g[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR)); g[:int(0.1 * SR)] = np.linspace(0, 1, int(0.1 * SR))
sh = sh * g[:, None] * 0.85
with wave.open('roma_short.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(sh, -1, 1) * 32767).astype('<i2').tobytes())
print('ok short: roma_short.wav')
