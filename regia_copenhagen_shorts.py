# Regia degli Shorts di Copenaghen (20 ott 2026, OK di Fabio per il pod). Camere PROPRIE, verticale 1080x1920, 24 fps.
# Test A/B/C come Rotterdam: A = controllo (tutta la storia), B e C = "su un evento" (qui i fuochi SONO nel render).
#  A "850 years in 28 seconds": camera larga in lenta orbita che si allontana mentre la citta' cresce, 1167 -> 2026.
#  B "This city burned to the ground": 20 ottobre 1728, camera sulla zona dell'incendio. Intatta -> onda di fuoco -> vuoto -> ricostruita.
#  C "This palace burned down twice": Slotsholmen. Castello di Copenaghen -> abbattuto 1731 -> Christiansborg I -> brucia 1794
#    -> Christiansborg II -> brucia 1884 -> Christiansborg III con la torre (1928).
# Controllo: nessun fotogramma deve cadere nella finestra di un incendio non voluto (lampi di un fotogramma = sembrano errori).
import json, math
FPS = 24
FIRES = [(1728.80, 1729.06), (1795.43, 1795.69), (1807.67, 1807.93), (1794.15, 1794.41), (1884.75, 1885.01)]   # finestre visibili (fumo fino a y1+0.25)

def lerp(t, K):
    for (t0, y0), (t1, y1) in zip(K, K[1:]):
        if t0 <= t <= t1: return y0 + (y1 - y0) * (t - t0) / (t1 - t0 or 1)
    return K[-1][1]

def orbit(t, T, cx, cy, r0, r1, h0, h1, a0, a1, tz=0.0):
    u = t / T; u = u * u * (3 - 2 * u)
    a = math.radians(a0 + (a1 - a0) * u); r = r0 + (r1 - r0) * u; h = h0 + (h1 - h0) * u
    return [round(cx + r * math.sin(a), 1), round(cy - r * math.cos(a), 1), round(h, 1)], [cx, cy, tz]

def write(name, dur, years, camf, lens, allowed):
    n = int(round(dur * FPS))
    bad = [(f, round(lerp((f - 1) / FPS, years), 3)) for f in range(1, n + 1)
           if any(a <= lerp((f - 1) / FPS, years) <= b for a, b in FIRES if (a, b) not in allowed)]
    assert not bad, f'short {name}: fotogrammi in incendi non voluti {bad[:6]}'
    cam = []; m = int(dur * 2) + 1
    for i in range(m):
        t = round(i * dur / (m - 1), 2); p, q = camf(t); cam.append([t, p, q, lens])
    json.dump({'_doc': f'Short {name} di Copenaghen: generato da regia_copenhagen_shorts.py (modificare li\').',
               'duration': dur, 'lens': lens, 'years': years, 'cam': cam}, open(f'schedule_copenhagen_short{name}.json', 'w'), indent=1)
    print(name, dur, 's =', n, 'fotogrammi')

# A: tutta la storia. Centro medievale ~(500, 400); si allarga fino alla citta' intera. I salti sui fuochi sono saltati a meta' fotogramma.
DA = 28.0
YA = [[0, 1167], [3.0, 1350], [6.0, 1600], [9.0, 1728.5], [9.0001, 1729.2], [11.0, 1794.0], [11.0001, 1796.0],
      [12.0, 1807.5], [12.0001, 1808.2], [16.0, 1880], [20.0, 1950], [25.0, 2026], [DA, 2026]]
write('A', DA, YA, lambda t: orbit(t, DA, 600, 450, 900, 5200, 420, 2600, -30, 15), 32, [])

# B: incendio del 1728. Zona ~(40..600, 0..800), origine (120, 120) a sud-ovest: camera da sud-ovest, il fuoco viene verso di noi.
DB = 26.0
YB = [[0, 1722.0], [4.5, 1728.79], [6.0, 1728.82], [12.5, 1728.99], [14.5, 1729.10], [16.0, 1730.0], [24.0, 1748.0], [DB, 1748.0]]
write('B', DB, YB, lambda t: orbit(t, DB, 330, 420, 1500, 1150, 700, 560, -40, -22, 10), 30, [FIRES[0]])

# C: Christiansborg. Palazzo ~(650, -30), torre (697, -22). Camera bassa da sud, sopra il canale.
DC = 28.0
YC = [[0, 1729.2], [1.6, 1731.2], [2.2, 1731.5], [3.0, 1733.0], [6.5, 1745.0], [7.6, 1794.14],     # castello vecchio, abbattuto, sale CB I
      [11.0, 1794.42], [11.6, 1795.30], [11.6001, 1795.75], [12.0, 1807.5], [12.0001, 1808.0], [12.6, 1810.0],   # brucia; rovina 1794-1810
      [16.0, 1821.0], [17.0, 1884.74], [20.5, 1885.02], [21.4, 1906.9], [26.0, 1929.0], [DC, 1929.0]]   # CB II, brucia, CB III + torre
write('C', DC, YC, lambda t: orbit(t, DC, 660, -30, 760, 600, 330, 260, -28, 8, 30), 35, [FIRES[3], FIRES[4]])
