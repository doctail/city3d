# Effetti sonori sintetici + mix delle due tracce per Parigi (29 ott 2026). Funzioni come sfx_sevilla.py / sfx_copenhagen.py.
# Uso: python3 sfx_parigi.py schedule_parigi.json WAKING.mp3 MONUMENT.mp3 eventi_parigi.json  -> parigi_mix.wav
import numpy as np, wave, json, sys
SR = 44100
SCHED = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'schedule_parigi.json'))
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

# ---- tempi presi dalla regia (eventi_parigi.json): se la regia cambia, gli effetti la seguono ----
EV = json.load(open(sys.argv[4] if len(sys.argv) > 4 else 'eventi_parigi.json'))
def T(key, kind='any'):
    for c in (EV['soste'] if kind != 'cap' else []) + (EV['didascalie'] if kind != 'sosta' else []):
        if key.lower() in c['title'].lower(): return c['t_in']
    print('  [effetto saltato: manca]', key); return None
def at(key, clip, dt, gain, kind='any'):
    t_ = T(key, kind)
    if t_ is not None: place(clip, t_ + dt, gain)
NIGHT_T = SCHED['night_t']
place(city_hum(3.4), 0.0, 0.10)                                  # Parigi oggi
place(whoosh(6.6), 3.0, 0.22)                                    # riavvolgimento 2026 -> 1190
place(boom(3.0, 90), 9.3, 0.22)                                  # arrivo nel 1190
at('Philippe Augustus', hammer(7), 1.5, 0.09, 'sosta'); at('Philippe Augustus', hammer(6), 4.2, 0.08, 'sosta')   # le mura
t_ = T('Notre-Dame rises', 'cap'); peal(t_ + 0.4, gain=0.14) if t_ else None                                       # Notre-Dame
at('Black Death', bell(5.0, 196.0), 0.3, 0.16, 'cap'); at('Black Death', bell(5.0, 196.0), 3.0, 0.12, 'cap')    # 1348: rintocchi lenti
at('Charles V', hammer(7), 1.0, 0.09, 'sosta')
at('Pont Neuf', hammer(6), 1.2, 0.08, 'sosta'); at('Pont Neuf', water(4.0), 0.5, 0.08, 'sosta')
t_ = T('Les Invalides', 'sosta'); peal(t_ + 2.0, notes=(523.0, 440.0, 392.0), gain=0.10, rounds=1) if t_ else None
# 14 luglio 1789: cannoni e crolli; COPRONO il cambio di traccia A -> B (CUT1)
CUT1 = T('Bastille falls', 'sosta')
for k, d in enumerate((-1.0, -0.3, 0.2, 0.9, 1.8, 3.0)): place(boom(2.6, 70 + 15 * k), CUT1 + d, 0.30 - 0.02 * k)
place(crash(2.6), CUT1 + 2.2, 0.18); place(crash(2.2), CUT1 + 3.6, 0.14)
at('Canal Saint-Martin is dug', water(6.0), 0.5, 0.14, 'sosta')
t_ = T('Haussmann', 'sosta')                                     # sventramenti: crolli e cantieri; dentro, la Comune (maggio 1871)
if t_:
    for k, d in enumerate((0.8, 2.0, 3.1, 4.6, 6.0)): place(crash(2.4), t_ + d, 0.16 - 0.015 * k)
    place(hammer(8), t_ + 1.4, 0.08); place(hammer(7), t_ + 5.0, 0.08)
    place(alarm_bells(6.0), t_ + 9.0, 0.11); place(fire(6.0, 1.0), t_ + 9.4, 0.20)   # Comune: Tuileries e Hotel de Ville bruciano
place(click(), EV['subscribe_t'], 0.20); place(ding(), EV['subscribe_t'] + 0.08, 0.08)   # Subscribe
t_ = T('Eiffel Tower rises', 'sosta')                            # chiodatura della torre
if t_:
    for d in (0.6, 2.2, 3.8): place(hammer(9, 0.28), t_ + d, 0.08)
at('Eiffel Tower opens', firework(), 0.4, 0.12, 'cap'); at('Eiffel Tower opens', firework(), 1.3, 0.10, 'cap')
at('World Fair', firework(), 0.4, 0.10, 'cap')
at('great flood', water(7.0), 0.3, 0.16, 'cap')
# Montparnasse e Les Halles demolite (1966-1977): crolli e cantiere; COPRONO il cambio di traccia B -> A (CUT2)
CUT2 = T('Tour Montparnasse and Centre Pompidou', 'sosta')
for k, d in enumerate((-0.8, -0.2, 0.4, 1.3, 2.4)): place(crash(2.6), CUT2 + d, 0.26 - 0.03 * k)
place(hammer(8), CUT2 + 2.0, 0.09); place(boom(3.0, 60), CUT2 - 0.5, 0.16)
t_ = T('Notre-Dame burns', 'cap') or T('Notre-Dame: fire', 'sosta')   # 15 aprile 2019
if t_: place(fire(7.0, 1.2), t_ + 0.2, 0.22); place(alarm_bells(5.0), t_ + 0.6, 0.10)
t_ = T('Notre-Dame reopens', 'cap')
if t_: peal(t_ + 0.3, gain=0.15, rounds=2)                       # 7 dicembre 2024: le campane tornano
place(city_hum(DUR - NIGHT_T), NIGHT_T, 0.10)                    # notte
peal(NIGHT_T + 14.0, notes=(330.0, 262.0), gain=0.08, rounds=2)  # campane lontane

# ---- musica: A = Waking to Reality (Unicorn Heads, 4:32), B = Monument (TrackTribe, 4:11): 8:44 di musica per 9:30 ----
# A 0 -> CUT1 (Bastiglia, ~3:58): il quasi silenzio iniziale di A sul medioevo, il suo calo (3:06-3:36) sul Settecento lento,
#   la ripresa (3:36) porta alla Bastiglia | B dal suo secondo 5 (sezione piena) CUT1 -> CUT2 (Montparnasse, ~7:57): Haussmann,
#   Comune e Tour Eiffel nella parte piena di B | A di nuovo, allineata alla fine: il suo calo cade sugli anni 1990-2010, la
#   ripresa su Notre-Dame 2019 e la notte, il finale di A chiude il video (come Siviglia).
import subprocess
def mp3(p):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<i2').reshape(-1, 2).astype(float) / 32768
A_, B_ = mp3(sys.argv[2]), mp3(sys.argv[3]); N_ = int(DUR * SR); mus = np.zeros((N_, 2))
def seg(src, a_off, t0, t1, fin, fout, gain=1.0):
    i0, i1 = int(t0 * SR), min(int(t1 * SR), N_); s_ = src[int(a_off * SR):int(a_off * SR) + (i1 - i0)]; n_ = len(s_)
    g = np.ones(n_); fi, fo = int(fin * SR), int(fout * SR)
    if fi: g[:fi] = np.linspace(0, 1, fi) ** 0.7
    if fo: g[-fo:] = np.minimum(g[-fo:], np.linspace(1, 0, fo) ** 1.4)
    mus[i0:i0 + n_] += s_ * (g * gain)[:, None]
LA, LB = len(A_) / SR, len(B_) / SR
A2 = LA - (DUR - CUT2) - 0.5                                     # A riparte in modo da finire col video
assert CUT2 - CUT1 + 5.0 <= LB - 1.0, f'B troppo corta: servono {CUT2 - CUT1:.1f} s, ce ne sono {LB - 6:.1f}'
seg(A_, 0.0, 0.0, CUT1 + 0.6, 0.0, 1.4)
seg(B_, 5.0, CUT1, CUT2 + 1.6, 0.25, 1.6, gain=0.62)   # Monument e' ~5 dB piu' forte di Waking to Reality
seg(A_, A2, CUT2, DUR, 0.12, 3.0)
st = mus * 0.82 + np.stack([fx[:N_], fx[:N_]], 1)
with wave.open('parigi_mix.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())
print(f'ok mix: A 0-{CUT1:.1f} | B(5 s) {CUT1:.1f}-{CUT2:.1f} | A({A2:.1f} s) {CUT2:.1f}-{DUR:.0f}; picco', round(float(np.abs(st).max()), 3))
