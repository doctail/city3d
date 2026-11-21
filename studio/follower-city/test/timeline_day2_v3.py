"""Timeline (secondi) del RIMONTAGGIO Day 2 v3 (ordine del riferimento): hook -> scheda profilo 1->5 -> palazzi che nascono con le schede commento -> finale largo + CTA.
Nessun nuovo render: i frame sorgente restano quelli di blender/day2_final_frames (SRC_MAP in blender/day2_v3_compose.py). 30 fps."""
DUR = 23.0
FPS = 30
UI = 0.2125
RATE = [1.15, 1.15, 1.10, 1.0]
POP = [219 / 30, 244 / 30, 315 / 30, 393 / 30]    # inizio salita A, B, OG, villa (frame multipli: mappa sorgente 1:1)
IMPACT = [POP[k] + UI / RATE[k] for k in range(4)]
T_HOOK = 0.2
T_HOOK_END = 3.1
T_CARD0, T_CARD1 = 3.3, 7.0                       # scheda profilo (come i Day precedenti: 3.3-7.0)
T_TICK = [4.2, 4.6, 5.0, 5.4]
T_CHIME = 5.6
T_ASKED0, T_ASKED1 = 9.4, 14.9                    # 'You asked, we built it'
T_OGCARD0, T_OGCARD1 = 9.7, 11.5
T_LILLY0, T_LILLY_BIG, T_LILLY_SMALL, T_LILLY1 = 11.9, 12.3, 13.1, 15.0
T_REPLY = 14.0
T_FOLLOW = 15.3
T_COMMENT0, T_COMMENT1 = 17.3, 19.5
T_GOAL = 19.5
T_PUSH0 = 14.4
BED_GAIN = [(0, 0), (0.7, 0), (1.9, 1.0), (3.2, 1.0), (3.3, 0.5), (6.9, 0.5), (7.0, 0.8), (15.2, 0.8), (15.3, 0.45), (19.4, 0.45), (19.5, 0.7), (21.0, 0.7), (23.0, 0.35)]
