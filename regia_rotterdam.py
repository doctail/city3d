# Regia di Rotterdam sulla traccia "The Shining in Dubai" (Unicorn Heads, 5:27). Scrive schedule_rotterdam.json.
# Misure della traccia (15 ott 2026): calo 3:27-3:31, quasi silenzio 3:32-3:36 (-45 dB), ripresa piano 3:37-3:56,
# crescendo finale da 3:57. Il 14 maggio 1940 cade nel calo; il centro vuoto nel silenzio; la ricostruzione nella ripresa.
# Camera sempre a SUD guardando verso nord (il sole viene da sud: controsole la citta' diventa marrone scuro).
# Origine: Laurenskerk (0, 0). La Nieuwe Maas passa ~1,3 km a sud: e' il primo piano naturale.
import json, math

DUR = 326.6
YEARS = [
    (0, 2026), (2.0, 2026), (5.5, 1340),          # riavvolgimento: 1340 diritti di citta', il triangolo c'e' gia'
    (30, 1450), (65, 1600), (100, 1700),           # Waterstad 1590-1640
    (135, 1800), (165, 1870), (192, 1905),         # Waterproject, porti della riva sud dal 1870
    (204, 1938), (207, 1940.0),                    # si rallenta verso il 1940
    (211, 1940.42),                                # 3:27-3:31: il 14 maggio (1940.37) cade qui, il centro sparisce
    (217, 1940.6),                                 # 3:31-3:37 silenzio sul centro vuoto
    (222, 1946), (236, 1957),                      # ripresa piano: macerie sgomberate, prima ricostruzione
    (270, 1975), (300, 2000), (312, 2015), (318, 2026), (DUR, 2026)]

# ancore camera: (t, posizione, bersaglio, obiettivo mm). Inclinazione ~20-22 gradi come Madrid.
A = [
    (0,     (-1600, -8200, 2600), (0, -400, 0), 35),     # oggi, largo dal sud
    (5.5,   (-700, -3000, 1050), (0, -100, 0), 35),      # stretto sul triangolo medievale
    (30,    (-800, -3000, 1080), (-50, -80, 0), 35),
    (65,    (-1300, -3300, 1250), (-200, -150, 0), 35),  # Waterstad
    (100,   (-2300, -4300, 1600), (-900, -250, 0), 35),  # si apre verso Delfshaven
    (135,   (-3600, -5600, 2100), (-2300, -400, 0), 35), # Schiedam e Delfshaven nel quadro
    (165,   (-1900, -6400, 2350), (-900, -300, 0), 35),  # le due rive, i porti nuovi
    (192,   (-200, -5000, 1800), (-100, -100, 0), 35),
    (204,   (300, -3900, 1350), (0, 0, 0), 35),          # si avvicina al centro prima del 1940
    (211,   (300, -3600, 1250), (0, 50, 0), 35),
    (217,   (250, -3450, 1200), (0, 80, 0), 35),         # quasi ferma nel silenzio
    (236,   (-300, -3700, 1000), (0, -100, 0), 35),      # ricostruzione
    (256,   (-1500, -3900, 600), (-100, -700, 60), 38),  # scende bassa (400-600 m) per far leggere le altezze
    (285,   (-2300, -3700, 450), (-150, -1000, 120), 40),
    (312,   (-1900, -3300, 420), (50, -1000, 130), 40),  # skyline sul fiume
    (318,   (-2100, -4200, 700), (0, -800, 80), 38),
    (DUR,   (-2600, -6800, 1700), (0, -500, 0), 35)]     # ritorno largo per il finale

def cr(p0, p1, p2, p3, u):   # Catmull-Rom per un movimento continuo (le chiavi Bezier di Blender rallentano su ogni chiave)
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
def sample(t):
    i = max(k for k in range(len(A)) if A[k][0] <= t) if t < DUR else len(A) - 2
    i = min(i, len(A) - 2); t0, t1 = A[i][0], A[i + 1][0]; u = (t - t0) / (t1 - t0)
    g = lambda j: A[max(0, min(len(A) - 1, j))]
    out = []
    for f in (1, 2):
        out.append([round(cr(g(i - 1)[f][d], g(i)[f][d], g(i + 1)[f][d], g(i + 2)[f][d], u), 1) for d in range(3)])
    mm = g(i)[3] + (g(i + 1)[3] - g(i)[3]) * (u * u * (3 - 2 * u))
    return out[0], out[1], round(mm, 1)

cam = []; t = 0.0
ts = sorted(set([a[0] for a in A] + [round(x * 2.5, 2) for x in range(int(DUR / 2.5) + 1)]))
for t in ts:
    if t > DUR: continue
    p, q, mm = sample(t); cam.append([t, p, q, mm])
json.dump({'_doc': 'Regia Rotterdam sulla traccia "The Shining in Dubai" (5:27). Generata da regia_rotterdam.py: modificare li\', non qui. '
                   't = secondi, y = anno, cam: [t, [pos], [target], mm], origine Laurenskerk.',
           'duration': DUR, 'lens': 35, 'years': [list(y) for y in YEARS], 'cam': cam},
          open('schedule_rotterdam.json', 'w'), indent=1)
print('chiavi camera', len(cam))
