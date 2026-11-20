"""Timeline condivisa Day 2 (frame a 24 fps) tra render (blender/anim_day2.py), audio e montaggio.
Il palazzo n.1 e' gia' in piedi (contatore 1); i palazzi 2..12 (rank 1..11 della citta') compaiono con ritmo che accelera."""
import math
FPS = 24
NF = 264
DUR = NF / FPS
N_NEW = 11
F_FIRST = 20            # inizio salita del primo palazzo nuovo
GAP0, GAPR = 30.0, 0.80  # intervallo (frame) tra un pop e il successivo: 30, 24, 19, ... ~4


def spring(u):
    if u <= 0:
        return 0.0
    return 1.0 - math.exp(-7.0 * u) * (math.cos(9.0 * u) + 0.78 * math.sin(9.0 * u))


def _ui():
    return next(i / 240.0 for i in range(1, 400) if spring(i / 240.0) >= 0.9)


UI = _ui()
POP_START, RATE = [], []
_f = float(F_FIRST)
for k in range(N_NEW):
    POP_START.append(_f)
    RATE.append(0.8 + 0.7 * k / (N_NEW - 1))   # salita piu' veloce verso la raffica
    _f += GAP0 * GAPR ** k
IMPACT = [POP_START[k] + UI / RATE[k] * FPS for k in range(N_NEW)]   # frame (float) in cui il palazzo tocca terra
T_IMPACT = [f / FPS for f in IMPACT]
T_CHIME = T_IMPACT[-1] + 0.45
if __name__ == "__main__":
    print([round(x, 1) for x in POP_START]); print([round(x, 1) for x in IMPACT]); print(round(T_CHIME, 2), DUR)
