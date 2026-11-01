# Effetti sonori sintetici per Costantinopoli 1453 (nessun file esterno, nessuna licenza): cannoni, impatti, macerie, vento,
# catena, navi trascinate, campane d'allarme, assalto. Mix sotto la voce. Uso: python sfx.py  -> audio/cpl_mix.wav, audio/cpl_sfx.wav
import numpy as np, os, json
from scipy import signal
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, 'audio')
SR = 44100; DUR = 64.8; N = int(SR * DUR); rng = np.random.default_rng(5)
out = np.zeros((N, 2), np.float32)
def env(n, att, dec):
    t = np.arange(n) / SR; return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t / dec)
def lp(x, f): b, a = signal.butter(2, f / (SR / 2), 'low'); return signal.lfilter(b, a, x)
def bp(x, f0, f1): b, a = signal.butter(2, [f0 / (SR / 2), f1 / (SR / 2)], 'band'); return signal.lfilter(b, a, x)
def add(t0, x, gain=1.0, pan=0.0):
    i = int(t0 * SR); x = x[: max(0, N - i)]
    if i < 0 or len(x) == 0: return
    out[i:i + len(x), 0] += x * gain * (1 - max(0, pan)); out[i:i + len(x), 1] += x * gain * (1 + min(0, pan))
def boom(dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (48 * np.exp(-t * 3) + 28) * t) * env(n, 0.004, 0.45)
    crack = lp(rng.standard_normal(n), 2500) * env(n, 0.001, 0.08)
    rumble = lp(rng.standard_normal(n), 180) * env(n, 0.02, 1.1)
    return 0.9 * thump + 0.5 * crack + 1.6 * rumble
def impact(dur=3.5):
    n = int(dur * SR); hit = lp(rng.standard_normal(n), 3500) * env(n, 0.001, 0.12)
    rub = np.zeros(n)
    for k in range(70):                                                                   # pietre che cadono
        i = int(rng.uniform(0.05, 2.6) * SR); m = int(0.06 * SR)
        if i + m < n: rub[i:i + m] += bp(rng.standard_normal(m), 300, 2500) * env(m, 0.001, 0.02) * rng.uniform(0.1, 0.5)
    low = lp(rng.standard_normal(n), 120) * env(n, 0.01, 0.9)
    return 0.8 * hit + rub + 1.2 * low
def bells(dur=4.5, f=392.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for k in range(0, int(dur / 0.75)):
        i = int(k * 0.75 * SR); m = n - i; tt = t[:m]
        part = sum(a * np.sin(2 * np.pi * f * r * tt) for r, a in ((0.5, 0.5), (1.0, 1.0), (1.19, 0.6), (1.5, 0.4), (2.0, 0.3), (2.74, 0.2))) * np.exp(-tt / 1.4)
        x[i:] += part * (0.8 if k % 2 else 1.0)
    return x * 0.12
def creak(dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = lp(rng.standard_normal(n), 90) * 0.6
    for k in range(int(dur * 1.6)):
        i = int(rng.uniform(0, dur - 0.5) * SR); m = int(0.35 * SR); tt = np.arange(m) / SR
        f = rng.uniform(140, 260); x[i:i + m] += np.sin(2 * np.pi * (f + 60 * np.sin(2 * np.pi * 9 * tt)) * tt) * env(m, 0.05, 0.12) * 0.25
    return x * np.minimum(1, np.minimum(t / 0.6, (dur - t) / 0.6))
def chain(dur=1.8):
    n = int(dur * SR); x = np.zeros(n)
    for k in range(14):
        i = int(k * dur / 14 * SR); m = int(0.08 * SR)
        if i + m < n: x[i:i + m] += bp(rng.standard_normal(m), 1800, 6000) * env(m, 0.0005, 0.03)
    return x * 0.5
def roar(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 250, 1400) * (0.4 + 0.6 * np.minimum(1, t / 1.2)) * np.minimum(1, (dur - t) / 1.0)
    return x * 0.5
def whoosh(dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); y = np.zeros(n); f0 = 300
    for i0 in range(0, n, 2048):
        seg = x[i0:i0 + 2048]; f = 200 + 1600 * np.sin(np.pi * i0 / n); y[i0:i0 + 2048] = bp(seg, f * 0.7, f * 1.3)
    return y * np.sin(np.pi * t / dur) * 0.35
# vento di fondo (giorno) e notte piu' cupa
n = N; t = np.arange(n) / SR
wind = lp(rng.standard_normal(n), 400) * (0.05 + 0.03 * np.sin(2 * np.pi * t / 7.0)); out[:, 0] += wind; out[:, 1] += np.roll(wind, 900)
for s in (5.25, 28.55, 33.25, 52.8):
    add(s, boom(), 0.9, -0.2); add(s + 0.8, impact(), 0.75, 0.2)
add(7.4, whoosh(), 0.8); add(10.9, whoosh(1.2), 0.5); add(50.4, whoosh(1.4), 0.6)
add(38.0, chain(), 0.9, 0.3)
add(42.4, creak(5.4), 1.0)
add(50.9, bells(5.0, 392), 1.0, -0.4); add(51.3, bells(4.5, 311), 0.8, 0.4)
add(53.4, roar(4.6), 0.8)
for k in range(10): add(rng.uniform(51, 56), impact(2.0) * 0.3, 0.4, rng.uniform(-0.6, 0.6))   # colpi lontani nell'assalto
peak = np.abs(out).max(); out = out / peak * 0.5
wavfile.write(os.path.join(A, 'cpl_sfx.wav'), SR, (out * 32767).astype(np.int16))
sr, v = wavfile.read(os.path.join(A, 'cpl_voce.wav')); v = v.astype(np.float32) / 32768
if v.ndim == 1: v = np.stack([v, v], 1)
mix = np.zeros_like(out); mix[: len(v)] += v[:N]
# ducking: effetti abbassati quando parla la voce
venv = np.abs(mix[:, 0]); k = int(0.25 * SR); venv = np.convolve(venv, np.ones(k) / k, 'same'); duck = 1 - 0.55 * np.clip(venv / (venv.max() * 0.25), 0, 1)
mix += out * 0.55 * duck[:, None]
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
wavfile.write(os.path.join(A, 'cpl_mix.wav'), SR, (mix * 32767).astype(np.int16))
print('ok', len(mix) / SR)
