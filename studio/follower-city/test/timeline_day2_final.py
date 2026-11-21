"""Timeline (secondi) condivisa tra video e audio del reel FINALE Day 2 REALE (18 s, 30 fps).
Il palazzo 1 (hero) e' gia' in piedi dal Day 1 (contatore 1); compaiono 4 palazzi: A, B (standard), OG (@m.bardi56), villa (@lillyflxwer). Contatore 1 -> 5."""
import math
DUR = 18.0
FPS = 30
UI = 0.2125                                       # spring >= 0.9 a u = 0.2125 (u = t * rate)
POP = [0.90, 1.75, 3.55, 6.25]                   # inizio salita: A, B, OG, villa
RATE = [1.15, 1.15, 1.10, 1.0]
IMPACT = [POP[k] + UI / RATE[k] for k in range(4)]
T_HOOK = 0.2                                      # titolo '4 new followers = 4 new buildings'
T_OGCARD0, T_OGCARD1 = 2.85, 5.1                  # scheda @m.bardi56 (entra, resta, esce)
T_LILLY0, T_LILLY_BIG, T_LILLY_SMALL, T_LILLY1 = 4.95, 5.35, 6.35, 8.5   # entra / ingrandita al centro / ridotta / esce
T_REPLY = 7.0                                     # risposta del profilo 'Let's see what we can do for you!'
T_CARD0, T_CARD1 = 8.6, 11.4                      # scheda profilo
T_TICK = [9.15, 9.55, 9.95, 10.35]                # contatore 1->2->3->4->5
T_CHIME = 10.55
T_COMMENT0, T_COMMENT1 = 11.4, 13.7               # 'Comment OG to claim your OG ticket' + schede OG reali
T_FOLLOW, T_GOAL = 13.7, 15.7                     # 'Follow to become a building' ; poi obiettivo + Day 2
T_PUSH0 = 11.4
SCENE_END_F = int(T_CARD0 * FPS)                  # ultimo frame di scena a pose di camera mobile
BED_GAIN = [(0, 0), (0.7, 0), (1.9, 1.0), (8.4, 1.0), (8.6, 0.5), (11.3, 0.7), (11.4, 0.4), (15.6, 0.4), (15.7, 0.7), (17.0, 0.7), (18.0, 0.35)]
