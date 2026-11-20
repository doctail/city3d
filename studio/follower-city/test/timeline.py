"""Timeline condivisa (secondi) tra audio e video del reel di test."""
DUR = 29.5
FPS = 30
T_HOOK = 0.22          # testo hook + tick
T_LAND = 1.45          # il palazzo atterra (frame 22 del clip a 24 fps)
CLIP_OFFSET = T_LAND - 22 / 24      # istante in cui parte il clip
T_CARD = 3.3           # scheda profilo
T_COUNT0 = 4.4         # inizio conteggio
T_CHIME = 5.8          # fine conteggio
T_SCENE2 = 7.0         # ritorno alla scena
T_REPLAY = 13.0        # replay del pop (richiesta "realizzata", placeholder)
T_COMMENT = 18.5       # commento in evidenza
T_COMMENT_END = 22.8
T_LABEL = 22.8         # "12 buildings / DAY 1"
T_CTA = 24.8
T_END = 27.0           # "See you tomorrow!"
COUNT_TO = 12          # numero PLACEHOLDER del test
# replay: sorgente 0.3 s -> 3.0 s a 0.49x
REPLAY_SRC0, REPLAY_RATE = 0.3, 0.49
T_LAND2 = T_REPLAY + (22 / 24 - REPLAY_SRC0) / REPLAY_RATE

# tick del contatore: fitti all'inizio, radi alla fine
TICK_TIMES = [T_COUNT0 + (T_CHIME - 0.15 - T_COUNT0) * (i / COUNT_TO) ** 1.5 for i in range(1, COUNT_TO + 1)]

# guadagno del letto (silenzio come punteggiatura, come nei riferimenti)
BED_GAIN = [(0, 0), (0.6, 0), (2.2, 1.0), (3.2, 1.0), (3.4, 0.55), (7.0, 0.55), (7.6, 1.0),
            (18.3, 1.0), (18.8, 0.5), (22.6, 0.5), (23.0, 0.25), (24.6, 0.25), (24.9, 0.8), (29.5, 0.8)]
