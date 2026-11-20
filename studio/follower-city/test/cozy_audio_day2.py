"""Audio Day 2 (solo numpy): letto lo-fi come nel test + pop/thud per ogni palazzo + tick contatore + chime finale.
Tempi dei pop da timeline_day2.py (stessi frame del render). Uso: python3 cozy_audio_day2.py out.wav"""
import numpy as np, wave, sys
from timeline_day2 import *
BED_GAIN = [(0, 0), (0.4, 0.9), (DUR - 1.2, 0.9), (DUR, 0.0)]

SR = 44100
rng = np.random.default_rng(7)
N = int(SR * DUR)
T = np.arange(N) / SR
out = np.zeros(N)
bed = np.zeros(N)

def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain

def env_exp(n, tau):
    return np.exp(-np.arange(n) / SR / tau)

def fft_filter(x, curve):
    X = np.fft.rfft(x); F = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * curve(F), len(x))

def hp(x, fc): return fft_filter(x, lambda F: 1 / (1 + (fc / np.maximum(F, 1)) ** 4))
def lp(x, fc): return fft_filter(x, lambda F: 1 / (1 + (F / fc) ** 4))
def bp(x, lo, hi): return lp(hp(x, lo), hi)

# ---------- effetti ----------
def thud(level=1.0):
    n = int(SR * 0.45); t = np.arange(n) / SR
    f = 55 + 95 * np.exp(-t / 0.05)                      # sweep 150 -> 55 Hz
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    crack = hp(rng.standard_normal(n), 3500) * np.exp(-t / 0.012) * 0.5
    dust = lp(rng.standard_normal(n), 900) * np.exp(-t / 0.12) * 0.25 * (1 - np.exp(-t / 0.02))
    return np.tanh(1.6 * (body + crack + dust)) * 0.62 * level

def sub_hit(level=1.0):
    n = int(SR * 0.5); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 50 * t) * np.exp(-t / 0.16)
    c = hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.006) * 0.3
    return (s + c) * 0.55 * level

def tick(level=1.0, pitch=1.0):
    n = int(SR * 0.05); t = np.arange(n) / SR
    ping = np.sin(2 * np.pi * 991 * pitch * t) * np.exp(-t / 0.012)
    click = bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t / 0.002)
    return (ping * 0.6 + click * 0.8) * 0.5 * level

def hook_click(level=1.0):
    n = int(SR * 0.03); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 3900 * t) * np.exp(-t / 0.004)) * 0.35 * level

def chime(level=1.0):
    n = int(SR * 1.6); t = np.arange(n) / SR
    s = np.zeros(n)
    for f, a, tau in [(1318.5, 1, 0.55), (1975.5, 0.7, 0.45), (2637, 0.25, 0.25), (3951, 0.12, 0.15)]:
        s += a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
    s *= (1 - np.exp(-t / 0.002))
    return s * 0.35 * level

def sparkle(dur=1.1, level=1.0):
    n = int(SR * dur); s = np.zeros(n)
    for _ in range(16):
        t0 = rng.uniform(0, dur * 0.55); f = rng.uniform(3000, 5200)
        m = int(SR * 0.35); tt = np.arange(m) / SR
        g = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.07) * rng.uniform(0.3, 1.0)
        i = int(t0 * SR); s[i:i + m] += g[: n - i]
    s *= np.linspace(1, 0.4, n)
    return s * 0.12 * level

def bubble(level=1.0, f=659.3):   # UI morbido per CTA
    n = int(SR * 0.35); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t * (1 + 0.15 * np.exp(-t / 0.04))) * np.exp(-t / 0.09)
    return s * 0.25 * level

# ---------- letto musicale lo-fi, 85 BPM, Mi maggiore ----------
BPM = 85; beat = 60 / BPM; bar = 4 * beat
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [  # (note MIDI del pad, arpeggio)
    ([52, 56, 59, 63], [64, 68, 71, 75]),   # Emaj9
    ([45, 52, 56, 59], [69, 64, 68, 71]),   # Amaj7
    ([49, 56, 59, 64], [68, 73, 71, 64]),   # C#m7
    ([47, 54, 59, 63], [66, 71, 63, 66]),   # B
]
def pad_note(f, dur):
    n = int(SR * (dur + 0.8)); t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.004, 0.0, 0.004):
        for h in range(1, 7):
            s += np.sin(2 * np.pi * f * (1 + det) * h * t + rng.uniform(0, 6.28)) / h ** 1.6
    a = np.minimum(1, t / 0.5) * np.minimum(1, np.maximum(0, (dur + 0.8 - t)) / 0.7)
    return s * a / 6
def pluck(f):
    n = int(SR * 1.0); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t / (0.35 / h ** 0.8)) / h for h in range(1, 6))
    return s * (1 - np.exp(-t / 0.003)) * 0.5
t0 = 0.0; k = 0
while t0 < DUR + bar:
    pads, arp = chords[k % 4]
    for m in pads: add(bed, pad_note(mid(m), bar), t0, 0.5)
    for j in range(8):                       # ottavi, swing leggero
        tj = t0 + j * beat / 2 + (0.035 if j % 2 else 0)
        add(bed, pluck(mid(arp[j % 4])), tj, 0.28 * (1.0 if j % 2 == 0 else 0.6))
    t0 += bar; k += 1
warp = T + 0.0018 * np.sin(2 * np.pi * 0.55 * T) + 0.0007 * np.sin(2 * np.pi * 3.1 * T)   # wobble nastro
bed = np.interp(warp, T, bed)
bed = lp(bed, 3200)
bed += lp(hp(rng.standard_normal(N) * (rng.random(N) > 0.9995), 800), 6000) * 0.02          # crepitio vinile
bed = bed / np.sqrt(np.mean(bed ** 2)) * 0.11          # RMS ~ -19 dBFS prima della normalizzazione (letto basso ma udibile)
bed *= np.interp(T, *zip(*BED_GAIN))

# ---------- effetti: un pop+thud per palazzo, sincronizzati col frame d'impatto ----------
def pop(level=1.0, f=520.0):
    n = int(SR * 0.22); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(f * (1 + 1.4 * np.exp(-t / 0.03))) / SR) * np.exp(-t / 0.05)
    return s * 0.35 * level

for i, tt in enumerate(T_IMPACT):
    k = i / (N_NEW - 1)
    add(out, thud(1.0 - 0.45 * k), tt, 1.0)                    # thud piu' leggero nella raffica
    add(out, pop(0.9, 480 * 2 ** (i / 12.0)), tt - 0.045, 1.0)  # "pop" di salita poco prima dell'impatto, intonazione crescente
    add(out, tick(0.9, 1.0 + 0.02 * i), tt + 1 / FPS, 1.0)      # tick contatore sul frame in cui cambia il numero
add(out, chime(), T_CHIME, 1.0)
add(out, sparkle(1.0, 0.8), T_CHIME + 0.05, 1.0)

mix = bed + out
mix *= np.minimum(1, (DUR - T) / 0.9)                   # fade finale
mix = np.tanh(mix * 1.0)
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'cozy_day2_audio_raw.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('audio ok', DUR, 's')
