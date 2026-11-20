"""Timeline (secondi) condivisa tra video e audio del reel FINALE Day 1 (11 s, 30 fps)."""
import math
DUR = 11.0
FPS = 30
T_HOOK = 0.22            # titolo + tick
T_POP = 1.0              # inizio pop-up
T_LAND = T_POP + 0.2656  # impatto (spring >= 0.9 a u=0.2125, u = t*0.8)
T_CARD0, T_CARD1 = 3.3, 6.0      # scheda profilo (taglio netto + colpo grave)
T_COUNT = 4.3            # il contatore passa 0 -> 1
T_GLOW0, T_GLOW1 = 6.0, 7.5
T_PUSH0, T_PUSH1 = 6.0, 8.5
T_CHIME = 5.0
T_END = 8.5              # 'Day 1' + 'See you tomorrow!'
BED_GAIN = [(0, 0), (0.7, 0), (1.9, 1.0), (3.2, 1.0), (3.3, 0.5), (6.0, 0.7), (8.4, 0.7), (8.5, 0.5), (11.0, 0.5)]
