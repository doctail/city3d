# Allinea le frasi del copione ai blocchi di parlato della voce (pause rilevate con silencedetect).
import re, subprocess, json, sys
src = sys.argv[1]
out = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', 'silencedetect=noise=-38dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
S = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]; E = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
sil = [(s, e) for s, e in zip(S, E) if e - s > 0]
chunks = []; t = 0.0
for s, e in sil:
    if s - t > 0.05: chunks.append((t, s))
    t = e
if dur - t > 0.05: chunks.append((t, dur))
ph = open('audio/phrases.txt').read().split('\n')
def w(p): return len(re.sub(r'[^A-Za-z0-9]', '', p.replace('480', 'four eighty'))) + 3
rate = sum(e - s for s, e in chunks) / sum(w(p) for p in ph)
n, m = len(chunks), len(ph); INF = 1e9
D = [[INF] * (m + 1) for _ in range(n + 1)]; B = [[0] * (m + 1) for _ in range(n + 1)]; D[0][0] = 0
for i in range(1, n + 1):
    for j in range(1, m + 1):
        for k in range(max(0, i - 4), i):          # una frase = da 1 a 4 blocchi consecutivi
            if D[k][j - 1] >= INF: continue
            got = chunks[i - 1][1] - chunks[k][0]; exp = w(ph[j - 1]) * rate
            c = D[k][j - 1] + ((got - exp) / (exp + 0.3)) ** 2 + 0.15 * (i - k - 1)
            if c < D[i][j]: D[i][j] = c; B[i][j] = k
res = []; i, j = n, m
while j > 0:
    k = B[i][j]; res.append((chunks[k][0], chunks[i - 1][1], ph[j - 1], i - k)); i, j = k, j - 1
res.reverse()
for s, e, p, nb in res: print(f'{s:6.2f} {e:6.2f}  [{nb}] {p}')
json.dump([dict(start=round(s, 3), end=round(e, 3), text=p) for s, e, p, _ in res], open(src + '.phrases.json', 'w'), indent=1)
print('chunks', n, 'phrases', m, 'durata', round(dur, 2))
