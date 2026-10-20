# Audio dei 3 Shorts di Copenaghen (musica + effetti sintetici), stessi strumenti di sfx_copenhagen.py.
# Uso: python sfx_copenhagen_shorts.py A_n.wav B_n.wav  -> copenhagen_shortA.m4a, _shortB.m4a, _shortC.m4a (via ffmpeg)
import numpy as np, sys, wave, subprocess, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sfx_copenhagen.py')).read()
src = src.split('\nL = int((DUR')[0].replace("SCHED = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'schedule_copenhagen.json'))", "SCHED = {'duration': 30}")
exec(src)
def music(path, off, dur):
    w = wave.open(path); sr = w.getframerate(); ch = w.getnchannels(); w.setpos(int(off * sr))
    x = np.frombuffer(w.readframes(int(dur * sr)), '<i2').astype(float).reshape(-1, ch) / 32768
    return x.mean(1) if sr == SR else np.interp(np.arange(int(dur * SR)) / SR, np.arange(len(x)) / sr, x.mean(1))
def short(name, track, off, dur, events, mgain=0.8, duck=()):
    m = music(track, off, dur) * mgain; n = len(m); t = np.arange(n) / SR
    g = np.ones(n)
    for a, b, k in duck: g[(t >= a) & (t < b)] = k
    from scipy.ndimage import uniform_filter1d; g = uniform_filter1d(g, int(0.5 * SR))
    fx = np.zeros(n + 6 * SR)
    for clip, t0, gain in events:
        c = norm(np.asarray(clip, float)) * gain; i = int(t0 * SR); fx[i:i + len(c)] += c[:len(fx) - i]
    y = m * g + fx[:n]; e = np.ones(n); e[:int(0.15 * SR)] = np.linspace(0, 1, int(0.15 * SR)); e[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR)); y *= e
    st = np.clip(np.stack([y, y], 1), -1, 1)
    with wave.open(f'_s{name}.wav', 'w') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'_s{name}.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', f'copenhagen_short{name}.m4a'], check=True)
    os.remove(f'_s{name}.wav'); print(name, 'ok', dur)
A, B = sys.argv[1], sys.argv[2]
# A: tutta la storia sul finale forte di "Waking to Reality" (216-244 s); nessun effetto
short('A', A, 216.0, 28.0, [])
# B: incendio 1728 a 4,5 s, nel calo del brano (come nel lungo, 184 s); musica abbassata sotto il fuoco
short('B', A, 179.5, 26.0, [(alarm_bells(6.0), 4.6, 0.30), (fire(10.0, 1.2), 4.5, 0.75), (boom(2.6, 140), 4.5, 0.35), (hammer(6), 17.0, 0.18), (hammer(7), 20.0, 0.16)],
      duck=[(4.4, 14.5, 0.45)])
# C: Christiansborg su "Monument"; fuochi a 7,6 s (1794) e 17 s (1884)
short('C', B, 30.0, 28.0, [(hammer(6), 3.2, 0.16), (fire(4.5, 0.9), 7.6, 0.65), (alarm_bells(3.5), 7.8, 0.22), (hammer(6), 13.0, 0.16),
                           (fire(4.5, 0.9), 17.0, 0.65), (alarm_bells(3.5), 17.2, 0.22), (hammer(7), 22.0, 0.16), (bell(f0=392), 25.6, 0.30)],
      duck=[(7.4, 11.4, 0.5), (16.8, 20.8, 0.5)])
