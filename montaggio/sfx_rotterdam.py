# Effetti sonori sintetici per Rotterdam (niente librerie esterne): campana 1340, sirena di nave 1872,
# sirena antiaerea + esplosioni lontane 14 maggio 1940. Volumi bassi: stanno SOTTO la musica.
import numpy as np, wave
SR = 44100
def env(n, a, r):  # attacco/rilascio lineari in campioni
    e = np.ones(n); a = min(a, n // 2); r = min(r, n // 2); e[:a] = np.linspace(0, 1, a); e[-r:] = np.linspace(1, 0, r); return e
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); acc = 0.0
    for i, v in enumerate(x): acc = (1 - a) * v + a * acc; y[i] = acc
    return y
def reverb(x, taps=((0.031, .5), (0.047, .38), (0.071, .3), (0.113, .22), (0.167, .15), (0.251, .1))):
    y = x.copy()
    for d, g in taps: k = int(d * SR); y[k:] += g * x[:-k]
    return y
def bell(dur=6.0, f0=392.0):
    t = np.arange(int(dur * SR)) / SR; y = np.zeros_like(t)
    for r, g, d in ((0.5, .6, 3.5), (1.0, 1.0, 2.5), (1.19, .5, 1.8), (1.5, .35, 1.4), (2.0, .3, 1.0), (2.74, .2, .7), (3.76, .12, .5)):
        y += g * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / d)
    return reverb(y * env(len(t), 80, 4000))
def horn(dur=3.2, f=82.0):
    t = np.arange(int(dur * SR)) / SR; vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR; y = sum(np.sin(k * ph) / k ** 1.2 for k in range(1, 12))
    return reverb(lowpass(y, 900) * env(len(t), int(.25 * SR), int(.8 * SR)))
def siren(dur=9.0):
    t = np.arange(int(dur * SR)) / SR; f = 380 + 260 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 4.5))
    ph = 2 * np.pi * np.cumsum(f) / SR; y = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    return reverb(lowpass(y, 1400), ((0.09, .45), (0.17, .35), (0.29, .25), (0.43, .15))) * env(len(t), int(1.5 * SR), int(2 * SR))
def boom(dur=2.8, seed=0):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    y = lowpass(rng.standard_normal(n), 120) * np.exp(-t / 0.55) * 6 + np.sin(2 * np.pi * 38 * t) * np.exp(-t / 0.35) * 0.6
    return reverb(y * env(n, 60, 4000))
def norm(x, peak): return x / (np.abs(x).max() + 1e-9) * peak
def place(track, clip, t0, gain):
    i = int(t0 * SR); track[i:i + len(clip)] += gain * clip[:max(0, len(track) - i)]
L = int(327 * SR); fx = np.zeros(L)
place(fx, norm(bell(), 1), 16.0, 0.22); place(fx, norm(bell(f0=330), 1), 17.6, 0.16)      # 1340: campane
place(fx, norm(horn(), 1), 87.4, 0.20)                                                  # 1872: nave sul nuovo canale
place(fx, norm(siren(), 1), 199.5, 0.13)                                                # 1940: sirena lontana prima del calo
for i, t0 in enumerate((207.3, 207.9, 208.4, 209.2, 209.7, 210.5, 211.3)):              # esplosioni lontane nel calo
    place(fx, norm(boom(seed=i), 1), t0, 0.30 - 0.025 * i)
st = np.stack([fx, fx], 1)
with wave.open('sfx_rotterdam.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())
print('ok', round(np.abs(fx).max(), 3))
