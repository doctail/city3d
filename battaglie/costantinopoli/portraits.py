# Ritratti stilizzati dei comandanti per i segnalini (disegno originale vettoriale, nessuna immagine esterna).
from PIL import Image, ImageDraw
S = 400  # disegno a 400 px poi ridotto (bordi puliti)
BRONZE, BRONZE_D, CREST, SKIN, SKIN_D, BEARD, GOLD, CLOTH = (196, 140, 58), (120, 80, 30), (200, 30, 28), (214, 168, 128), (160, 115, 80), (28, 22, 20), (235, 190, 60), (120, 30, 140)
def P(pts): return [(x * S / 100, y * S / 100) for x, y in pts]
def spartan(bg):
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    d.polygon(P([(30, 100), (34, 82), (66, 82), (70, 100)]), fill=CREST)                     # mantello rosso
    q = P([(12, 2), (88, 50)]); d.chord(q[0] + q[1], 180, 360, fill=CREST)                    # cresta trasversale
    for k in range(7): d.line(P([(50, 26), (16 + k * 11.3, 8 + abs(3 - k) * 3)]), fill=(150, 18, 18), width=4)
    d.chord(P([(26, 28), (74, 80)])[0] + P([(26, 28), (74, 80)])[1], 180, 360, fill=BRONZE)   # calotta
    d.polygon(P([(26, 54), (74, 54), (72, 84), (60, 90), (56, 70), (44, 70), (40, 90), (28, 84)]), fill=BRONZE)  # guance
    d.polygon(P([(30, 48), (47, 48), (47, 56), (44, 58), (30, 56)]), fill=(20, 15, 12))       # feritoie occhi
    d.polygon(P([(53, 48), (70, 48), (70, 56), (56, 58), (53, 56)]), fill=(20, 15, 12))
    d.polygon(P([(47, 48), (53, 48), (52, 68), (48, 68)]), fill=BRONZE_D)                      # paranaso
    d.line(P([(28, 46), (72, 46)]), fill=BRONZE_D, width=6)
    return im
def xerxes(bg):
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    d.polygon(P([(22, 100), (28, 78), (72, 78), (78, 100)]), fill=CLOTH)                      # veste porpora
    d.ellipse(P([(32, 26), (68, 70)])[0] + P([(32, 26), (68, 70)])[1], fill=SKIN)             # volto
    d.polygon(P([(32, 52), (68, 52), (66, 72), (58, 88), (50, 92), (42, 88), (34, 72)]), fill=BEARD)  # barba
    d.ellipse(P([(42, 54), (58, 62)])[0] + P([(42, 54), (58, 62)])[1], fill=SKIN_D)           # bocca/baffi area
    d.polygon(P([(30, 30), (30, 8), (36, 16), (43, 6), (50, 16), (57, 6), (64, 16), (70, 8), (70, 30)]), fill=GOLD)  # corona merlata
    d.rectangle(P([(30, 26), (70, 32)]), fill=(200, 150, 40))
    d.rectangle(P([(38, 42), (46, 45)]), fill=BEARD); d.rectangle(P([(54, 42), (62, 45)]), fill=BEARD)  # occhi
    d.polygon(P([(26, 30), (32, 30), (34, 60), (28, 64)]), fill=BEARD); d.polygon(P([(74, 30), (68, 30), (66, 60), (72, 64)]), fill=BEARD)  # capelli
    return im
def immortal(bg):
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    d.line(P([(82, 100), (82, 6)]), fill=(90, 60, 30), width=10); d.polygon(P([(82, 0), (77, 12), (87, 12)]), fill=(210, 210, 210))  # lancia
    d.polygon(P([(20, 100), (26, 76), (74, 76), (80, 100)]), fill=(240, 220, 170))             # tunica chiara
    d.polygon(P([(28, 74), (26, 34), (34, 16), (50, 10), (66, 16), (74, 34), (72, 74)]), fill=(225, 205, 160))  # cappuccio/tiara di stoffa
    d.ellipse(P([(36, 32), (64, 66)])[0] + P([(36, 32), (64, 66)])[1], fill=SKIN)
    d.polygon(P([(36, 54), (64, 54), (60, 74), (50, 80), (40, 74)]), fill=BEARD)
    d.rectangle(P([(41, 43), (47, 46)]), fill=BEARD); d.rectangle(P([(53, 43), (59, 46)]), fill=BEARD)
    d.polygon(P([(28, 74), (36, 62), (36, 76)]), fill=(225, 205, 160)); d.polygon(P([(72, 74), (64, 62), (64, 76)]), fill=(225, 205, 160))  # lembi che coprono il mento
    return im
def mehmed(bg):
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    d.polygon(P([(20, 100), (26, 78), (74, 78), (80, 100)]), fill=(150, 25, 20))                   # caffettano rosso
    d.polygon(P([(44, 78), (56, 78), (52, 100), (48, 100)]), fill=(230, 190, 70))                   # bordo dorato
    d.ellipse(P([(34, 36), (66, 72)])[0] + P([(34, 36), (66, 72)])[1], fill=SKIN)
    d.polygon(P([(36, 58), (64, 58), (60, 76), (50, 84), (40, 76)]), fill=(60, 40, 25))             # barba bruna
    d.ellipse(P([(18, 6), (82, 52)])[0] + P([(18, 6), (82, 52)])[1], fill=(245, 242, 232))         # turbante grande
    for k in range(4): d.arc(P([(22, 10 + k * 7), (78, 50 + k * 2)])[0] + P([(22, 10 + k * 7), (78, 50 + k * 2)])[1], 200, 340, fill=(205, 200, 185), width=5)
    d.ellipse(P([(46, 2), (54, 12)])[0] + P([(46, 2), (54, 12)])[1], fill=(200, 30, 30))            # cupola rossa del turbante
    d.rectangle(P([(40, 48), (46, 51)]), fill=BEARD); d.rectangle(P([(54, 48), (60, 51)]), fill=BEARD)
    d.polygon(P([(49, 52), (51, 52), (53, 60), (47, 60)]), fill=SKIN_D)                             # naso aquilino
    return im
def constantine(bg):
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    d.polygon(P([(20, 100), (26, 78), (74, 78), (80, 100)]), fill=(95, 25, 110))                    # porpora imperiale
    d.polygon(P([(30, 82), (70, 82), (66, 90), (34, 90)]), fill=GOLD)                                # loros dorato
    d.ellipse(P([(33, 30), (67, 70)])[0] + P([(33, 30), (67, 70)])[1], fill=SKIN)
    d.polygon(P([(34, 54), (66, 54), (63, 74), (50, 88), (37, 74)]), fill=(110, 95, 80))            # barba brizzolata
    d.polygon(P([(30, 36), (30, 14), (50, 6), (70, 14), (70, 36)]), fill=GOLD)                      # corona a calotta
    d.rectangle(P([(30, 30), (70, 36)]), fill=(200, 150, 40))
    for k in range(5): d.ellipse(P([(33 + k * 7.5, 20), (38 + k * 7.5, 25)])[0] + P([(33 + k * 7.5, 20), (38 + k * 7.5, 25)])[1], fill=(170, 20, 30) if k % 2 else (40, 90, 170))
    d.polygon(P([(48, 2), (52, 2), (52, 8), (48, 8)]), fill=GOLD)                                    # croce
    for sx in (27, 69):                                                                              # pendilia
        d.line(P([(sx, 36), (sx, 60)]), fill=GOLD, width=5); d.ellipse(P([(sx - 3, 58), (sx + 3, 64)])[0] + P([(sx - 3, 58), (sx + 3, 64)])[1], fill=(240, 240, 230))
    d.rectangle(P([(40, 44), (46, 47)]), fill=BEARD); d.rectangle(P([(54, 44), (60, 47)]), fill=BEARD)
    return im
def cannon_icon(bg):
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    d.polygon(P([(12, 62), (70, 40), (78, 52), (20, 74)]), fill=(150, 105, 40))                     # canna in bronzo
    d.ellipse(P([(68, 36), (84, 56)])[0] + P([(68, 36), (84, 56)])[1], fill=(30, 22, 15))           # bocca
    for k in range(3): d.polygon(P([(26 + k * 16, 57 - k * 6), (30 + k * 16, 56 - k * 6), (36 + k * 16, 70 - k * 6), (32 + k * 16, 71 - k * 6)]), fill=(110, 75, 25))
    d.rectangle(P([(10, 74), (64, 82)]), fill=(90, 60, 30))                                          # travi
    d.ellipse(P([(70, 70), (88, 88)])[0] + P([(70, 70), (88, 88)])[1], fill=(170, 170, 160))        # palla di pietra
    return im
KINDS = dict(spartan=spartan, xerxes=xerxes, immortal=immortal, mehmed=mehmed, constantine=constantine, cannon=cannon_icon)
def portrait(kind, R, bg):
    im = KINDS[kind](bg).resize((2 * R, 2 * R), Image.LANCZOS)
    mask = Image.new('L', (2 * R * 4, 2 * R * 4), 0); ImageDraw.Draw(mask).ellipse([0, 0, 8 * R - 1, 8 * R - 1], fill=255)
    im.putalpha(mask.resize((2 * R, 2 * R), Image.LANCZOS)); return im
if __name__ == '__main__':
    out = Image.new('RGB', (420, 140), (30, 30, 30))
    out = Image.new('RGB', (420, 140), (30, 30, 30))
    for i, (k, c) in enumerate((('mehmed', (200, 30, 28)), ('constantine', (30, 80, 210)), ('cannon', (60, 60, 60)))):
        p = portrait(k, 60, c + (255,)); out.paste(p, (10 + i * 140, 10), p)
    out.save('ritratti_cpl.png')
