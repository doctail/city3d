# Accorcia le pause della voce (tetto per pausa) e accelera leggermente. Uso: tighten.py in.mp3 out.wav tetto tetto_punto atempo
import sys, json, subprocess, numpy as np, re
src, dst, CAP, CAPP, TEMPO = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
SR = 44100
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.int16)
out = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', 'silencedetect=noise=-38dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
S = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]; E = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
ph = json.load(open(src + '.phrases.json'))
ends_period = {round(p['end'], 2) for p in ph if p['text'].endswith('.')}
parts = []; t = 0; MAP = [(0.0, 0.0)]; nt = 0.0   # punti (tempo vecchio, tempo nuovo) prima dell'atempo
for s, e in zip(S, E):
    if e - s <= 0: continue
    cap = CAPP if any(abs(s - x) < 0.05 for x in ends_period) else CAP
    parts.append(a[int(t * SR):int(s * SR)]); nt += s - t; MAP.append((s, nt))
    keep = min(e - s, cap); h = keep / 2; nt += keep; MAP.append((e, nt))
    parts.append(a[int(s * SR):int((s + h) * SR)]); parts.append(a[int((e - h) * SR):int(e * SR)])
    t = e
parts.append(a[int(t * SR):])
b = np.concatenate(parts).astype(np.int16)
def f(x):
    for (o0, n0), (o1, n1) in zip(MAP, MAP[1:]):
        if x <= o1: return (n0 + (x - o0) * (n1 - n0) / max(1e-9, o1 - o0)) / TEMPO
    return (MAP[-1][1] + x - MAP[-1][0]) / TEMPO
json.dump([dict(start=round(f(p['start']), 3), end=round(f(p['end']), 3), text=p['text']) for p in ph], open(dst + '.phrases.json', 'w'), indent=1)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={TEMPO}', dst], input=b.tobytes())
