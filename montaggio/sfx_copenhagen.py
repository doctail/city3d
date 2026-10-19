# Effetti sonori sintetici per Copenaghen (niente librerie esterne), a TEMPO sui secondi della regia (schedule_copenhagen.json).
# Volumi bassi: stanno SOTTO la musica. Uscita: sfx_copenhagen.wav (stereo, 44,1 kHz, durata del video).
import numpy as np, wave, json, sys
SR = 44100
SCHED = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'schedule_copenhagen.json'))
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

L = int((DUR + 3) * SR); fx = np.zeros(L)
def place(clip, t0, gain, peak=1.0):
    c = norm(np.asarray(clip, float), peak) * gain; i = int(t0 * SR); m = min(len(c), L - i)
    if m > 0: fx[i:i + m] += c[:m]

place(whoosh(6.2), 3.0, 0.20)                                   # riavvolgimento 2026 -> 1167
place(boom(3.0, 90), 9.3, 0.22)                                  # arrivo nel 1167
place(bell(), 31.0, 0.18)                                        # 1254 diritti di citta'
for k, t0 in enumerate((62.0, 62.7, 63.6)): place(boom(2.0, 200), t0, 0.16 - 0.03 * k)   # 1369 la Lega anseatica abbatte il castello
place(bell(f0=330), 79.2, 0.18); place(bell(f0=392), 80.4, 0.13)                   # 1443 capitale
place(hammer(8), 104.0, 0.10); place(hammer(6), 111.0, 0.10); place(hammer(7), 119.5, 0.10)   # Rosenborg, Boersen, Rundetaarn
for k, t0 in enumerate((134.2, 134.9, 135.3, 136.4, 137.0, 137.9)): place(boom(2.2, 380), t0, 0.20 - 0.015 * k)   # 1659 assalto svedese
place(horn(), 147.0, 0.14)                                       # Nyhavn: nave
for k in range(4): place(bell(4.0, 262.0), 169.0 + 1.6 * k, 0.10)   # 1711 peste: rintocchi lenti (sobria)
place(alarm_bells(7.0), 184.2, 0.13); place(fire(10.5, 1.0), 184.0, 0.30)          # 20 ottobre 1728
place(hammer(6), 207.5, 0.09)                                    # Christiansborg I
place(bell(f0=440), 215.5, 0.16)                                 # guglia di Vor Frelsers
place(fire(3.8, 0.7), 234.9, 0.20)                               # 1794 brucia Christiansborg
place(fire(4.5, 1.0), 238.8, 0.26); place(alarm_bells(3.5), 239.2, 0.10)           # giugno 1795
# 2-5 settembre 1807: la musica A sfuma, restano cannoni, razzi, fuoco, campane (copre il cambio di traccia)
place(fire(15.0, 1.4), 248.0, 0.42)
for k, t0 in enumerate(np.arange(248.3, 261.0, 0.9) + rng.uniform(-0.2, 0.2, 15)):
    place(boom(2.4, rng.uniform(200, 420)), float(t0), 0.55 * rng.uniform(0.6, 1.0))
    if k % 2 == 0: place(rocket(), float(t0) - 1.3, 0.22)
place(alarm_bells(5.0), 257.0, 0.18)
place(hammer(6), 263.0, 0.08); place(hammer(8), 331.5, 0.09); place(hammer(6), 360.5, 0.08); place(hammer(6), 453.0, 0.08)   # cantieri
place(fire(3.4, 0.7), 318.5, 0.18)                               # 1884 brucia di nuovo
place(bell(f0=349), 325.0, 0.15)                                 # la cupola della Marmorkirken
place(city_hum(DUR - 458.0), 458.0, 0.10)                        # tramonto e notte: brusio della citta'
for t0 in (466.0, 468.6, 470.1, 473.5, 476.2, 477.0, 481.0):     # fuochi d'artificio sul Tivoli
    place(firework(), t0, 0.16 * rng.uniform(0.7, 1.0))
st = np.stack([fx[:int(DUR * SR)], fx[:int(DUR * SR)]], 1)
with wave.open('sfx_copenhagen.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())
print('ok, picco', round(float(np.abs(fx).max()), 3), 'durata', DUR)
