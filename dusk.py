# Tramonto tra la passata di giorno e quella di notte (nessun render in piu': colori + dissolvenza).
# Uso: python dusk.py DAY_DIR NIGHT_DIR OUT_DIR NT NF [STEP]
#   NT = primo fotogramma della notte nella regia (night_t). Scaletta (secondi dal fotogramma NT):
#   0-5 s  giorno -> luce dorata -> tramonto arancio (solo colori sui fotogrammi di giorno)
#   5-10 s tramonto -> notte in dissolvenza (le finestre si accendono mentre la luce cala) = crepuscolo
#   10 s+  notte piena
# Fuori dalla finestra i fotogrammi vengono collegati (link), non copiati. Nomi a 4 o 5 cifre come build_render.
import sys, os, glob
import numpy as np, cv2

DAY, NIGHT, OUT, NT, NF = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
STEP = int(sys.argv[6]) if len(sys.argv) > 6 else 1
FPS = 24; S0, S1, S2 = NT, NT + 5 * FPS, NT + 10 * FPS
os.makedirs(OUT, exist_ok=True)
NW = 5 if NF > 9999 else 4
def name(d, f): return os.path.join(d, f'{f:0{NW}d}.jpg')

_mm = {}
def sunset(im, k):
    h = im.shape[0]
    if h not in _mm:   # arancio piu' forte in alto (verso l'orizzonte), BGR
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        m = np.array([0.42, 0.70, 1.12], np.float32)[None, None, :]; mt = np.array([0.30, 0.55, 1.25], np.float32)[None, None, :]
        _mm[h] = mt * (1 - yy) * 0.5 + m * (1 - (1 - yy) * 0.5)
    return im * (1 - k) + np.clip(im * _mm[h] * 0.92, 0, 1) * k
def ease(u): u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)

n_link = n_mix = 0
for f in range(1, NF + 1, STEP):
    src = name(DAY, f) if f < S2 else name(NIGHT, f)
    dst = name(OUT, f)
    if os.path.exists(dst): continue
    if f < S0 or f >= S2:
        if os.path.exists(src): os.symlink(os.path.abspath(src), dst); n_link += 1
        continue
    d = cv2.imread(name(DAY, f))
    if d is None: continue
    d = d.astype(np.float32) / 255
    if f < S1: out = sunset(d, ease((f - S0) / (S1 - S0)))
    else:
        n = cv2.imread(name(NIGHT, f))
        n = n.astype(np.float32) / 255 if n is not None else d * 0.15
        u = ease((f - S1) / (S2 - S1))
        out = sunset(d, 1.0) * (1 - u) + n * u
    cv2.imwrite(dst, (np.clip(out, 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95]); n_mix += 1
print(f'[dusk] collegati {n_link}, tramonto/crepuscolo {n_mix} fotogrammi ({S0}-{S2})', flush=True)
