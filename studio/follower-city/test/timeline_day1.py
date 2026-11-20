"""Timeline (secondi) condivisa tra video e audio del reel FINALE Day 1 (11 s, 30 fps)."""
import math
DUR = 15.0
FPS = 30
T_HOOK = 0.22            # titolo + tick
T_POP = 1.0              # inizio pop-up
T_LAND = T_POP + 0.2656  # impatto (spring >= 0.9 a u=0.2125, u = t*0.8)
T_CARD0, T_CARD1 = 3.3, 6.0      # scheda profilo (taglio netto + colpo grave)
T_COUNT = 4.3            # il contatore passa 0 -> 1
T_GLOW0, T_GLOW1 = 6.0, 7.5
T_PUSH0, T_PUSH1 = 6.0, 8.5
T_CHIME = 5.0
T_COMMENT0 = 7.6          # richiesta commento + scheda commento
T_COMMENT1 = 10.6
T_FOLLOW = 10.6           # 'Follow to become a building'
T_END = 12.4             # 'Day 1' + 'See you tomorrow!' (fermo 2.6 s)
BED_GAIN = [(0, 0), (0.7, 0), (1.9, 1.0), (3.2, 1.0), (3.3, 0.5), (6.0, 0.7), (7.4, 0.7), (7.6, 0.3), (10.4, 0.3), (10.6, 0.7), (12.3, 0.7), (12.4, 0.35), (15.0, 0.35)]
