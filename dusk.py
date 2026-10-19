# Tramonto tra la passata di giorno e quella di notte (nessun render in piu': colori + fusione).
# Uso: python dusk.py DAY_DIR NIGHT_DIR OUT_DIR NT NF [STEP]      (prova: python dusk.py --test DAY.jpg NIGHT.jpg OUT.jpg)
#   NT = primo fotogramma della notte nella regia (night_t). Scaletta (secondi da NT), fasi continue:
#   0-5 s   giorno -> luce dorata -> tramonto: arancio SOLO sulle luci (tetti, facciate al sole), ombre viola-blu, prati verdi
#   5-10 s  ora blu: il giorno vira al blu e si scurisce, le luci della notte si accendono sopra (fusione "screen")
#   10 s+   notte piena
# 19 ott 2026: la prima versione era un filtro arancio uniforme (prati oliva, crepuscolo verdastro): scartata.
import sys, os
import numpy as np, cv2

def ease(u): u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)
def lum(im): return (im[..., 0] * 0.114 + im[..., 1] * 0.587 + im[..., 2] * 0.299)[..., None]
_cache = {}
def sky_band(h, w):   # bagliore all'orizzonte (in alto nel quadro), BGR
    if (h, w) not in _cache:
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        _cache[(h, w)] = np.clip(1 - yy / 0.45, 0, 1) ** 1.6
    return _cache[(h, w)]

def warm(im, k):
    """k 0->1: giorno -> tramonto. Luci arancio-oro, ombre viola-blu, poca perdita di luce."""
    L = lum(im); hi = np.clip((L - 0.25) / 0.55, 0, 1); lo = 1 - hi
    m_hi = np.array([0.62, 0.86, 1.10], np.float32)          # luci: oro -> arancio
    m_lo = np.array([1.06, 0.80, 0.86], np.float32)          # ombre: viola-blu
    tint = hi * m_hi + lo * m_lo
    out = im * (1 - k) + np.clip(im * tint * (1 - 0.18 * k), 0, 1) * k
    band = sky_band(*im.shape[:2]) * k * 0.35
    out = out * (1 - band) + np.array([0.45, 0.62, 1.0], np.float32) * band   # orizzonte rosa-arancio
    return np.clip(out, 0, 1)

def blue_hour(day_warm, night, u):
    """u 0->1: il giorno (gia' al tramonto) diventa blu e scuro, le luci della notte si sommano (screen) fino alla notte piena."""
    L = lum(day_warm)
    blue = np.clip(L * np.array([1.35, 0.85, 0.55], np.float32) * (0.75 - 0.45 * u), 0, 1)   # monocromo blu che si spegne
    b = (1 - 0.5 * u) * day_warm * (1 - u) + blue * (0.5 * u + u * (1 - u))                 # dal caldo al blu
    b = day_warm * (1 - ease(u * 1.6)) + blue * ease(u * 1.6)
    lights = night * min(1.0, 0.35 + 0.9 * u)
    screen = 1 - (1 - b) * (1 - lights)
    return np.clip(screen * (1 - ease((u - 0.6) / 0.4)) + night * ease((u - 0.6) / 0.4), 0, 1)

def frame(day, night, t):
    """t = secondi da NT. Restituisce il fotogramma finale (float BGR 0-1)."""
    if t < 5.0: return warm(day, ease(t / 5.0))
    if night is None: night = day * 0.1
    return blue_hour(warm(day, 1.0), night, (t - 5.0) / 5.0)

if __name__ == '__main__':
    if sys.argv[1] == '--test':   # foglio di prova: 6 momenti
        d = cv2.imread(sys.argv[2]).astype(np.float32) / 255; n = cv2.imread(sys.argv[3]).astype(np.float32) / 255
        ims = []
        for t, lab in [(0, 'giorno 7:40'), (2.5, 'luce dorata'), (5, 'tramonto'), (6.8, 'ora blu'), (8.5, 'luci accese'), (11, 'notte')]:
            im = (frame(d, n, t) * 255).astype(np.uint8) if t < 10 else (n * 255).astype(np.uint8)
            cv2.putText(im, lab, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2); ims.append(im)
        cv2.imwrite(sys.argv[4], np.vstack([np.hstack(ims[:3]), np.hstack(ims[3:])]), [cv2.IMWRITE_JPEG_QUALITY, 88]); sys.exit()
    DAY, NIGHT, OUT, NT, NF = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    STEP = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    FPS = 24; S0, S2 = NT, NT + 10 * FPS
    os.makedirs(OUT, exist_ok=True)
    NW = 5 if NF > 9999 else 4
    def name(d, f): return os.path.join(d, f'{f:0{NW}d}.jpg')
    n_link = n_mix = 0
    for f in range(1, NF + 1, STEP):
        dst = name(OUT, f)
        if os.path.exists(dst): continue
        if f < S0 or f >= S2:
            src = name(DAY, f) if f < S0 else name(NIGHT, f)
            if os.path.exists(src): os.symlink(os.path.abspath(src), dst); n_link += 1
            continue
        d = cv2.imread(name(DAY, f))
        if d is None: continue
        n = cv2.imread(name(NIGHT, f))
        out = frame(d.astype(np.float32) / 255, n.astype(np.float32) / 255 if n is not None else None, (f - S0) / FPS)
        cv2.imwrite(dst, (out * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95]); n_mix += 1
    print(f'[dusk] collegati {n_link}, tramonto/ora blu {n_mix} fotogrammi ({S0}-{S2})', flush=True)
