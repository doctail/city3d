# Infografica stile "One Map, One Battle" sopra il render 3D di Costantinopoli 1453. Legata ai secondi della voce.
# Uso: overlay.py <frame.png> <secondo> <out.jpg>      tempi e sottotitoli: audio/cpl_tempi.json
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from portraits import portrait
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
SRC, sec, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
W, H = 1080, 1920
base = Image.open(SRC).convert('RGB').resize((W, H), Image.LANCZOS)
# bagliore: le parti molto chiare (lampi, fuochi, catena) si allargano un po'
lum = base.convert('L').point(lambda v: 255 if v > 205 else int(v * 0.0))
glow = Image.composite(base, Image.new('RGB', (W, H)), lum).filter(ImageFilter.GaussianBlur(22))
base = ImageChops.add(base, glow.point(lambda v: int(v * 0.55)))
im = base.convert('RGBA')
lab = json.load(open(SRC + '.json'))
TIM = json.load(open(os.path.join(HERE, 'audio', 'cpl_tempi.json')))
FD = os.environ.get('FONTS', os.path.join(HERE, 'fonts') + '/')
A = lambda s: ImageFont.truetype(FD + 'anton/files/anton-latin-400-normal.woff', s)
O = lambda s: ImageFont.truetype(FD + 'oswald/files/oswald-latin-700-normal.woff', s)
RED, BLK, WHT, BLU, ORG, GLD, SEA = (200, 30, 28), (16, 16, 18), (255, 255, 255), (30, 80, 210), (230, 110, 20), (225, 175, 55), (20, 60, 110)

def fade(t0, t1, ramp=0.25):
    if sec < t0 or sec > t1: return 0.0
    return max(0.0, min(1.0, (sec - t0) / ramp if t0 > 0 else 1.0, (t1 - sec) / ramp))
def layer(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))
def paste(l, a):
    global im
    if a <= 0: return
    if a < 1: l.putalpha(l.split()[3].point(lambda v: int(v * a)))
    im = Image.alpha_composite(im, l)
def tag(d, x, y, text, size=34, bg=BLK, fg=WHT, pad=(16, 8), anchor='mm'):
    f = O(size); bb = d.textbbox((0, 0), text, font=f); w, h = bb[2] - bb[0], bb[3] - bb[1]
    if anchor == 'mm': x0, y0 = x - w / 2 - pad[0], y - h / 2 - pad[1]; x0 = max(20, min(W - 20 - w - 2 * pad[0], x0))
    else: x0, y0 = x, y
    d.rectangle([x0, y0, x0 + w + 2 * pad[0], y0 + h + 2 * pad[1] + 4], fill=bg)
    d.text((x0 + pad[0], y0 + pad[1] - bb[1]), text, font=f, fill=fg)
    return x0, y0, x0 + w + 2 * pad[0], y0 + h + 2 * pad[1]
def big(l, s, y, size=230, fill=WHT):
    f = A(size); d = ImageDraw.Draw(l); bb = d.textbbox((0, 0), s, font=f); x = W / 2 - (bb[2] - bb[0]) / 2
    sh = layer(); ImageDraw.Draw(sh).text((x + 6, y + 8), s, font=f, fill=(0, 0, 0, 180)); sh = sh.filter(ImageFilter.GaussianBlur(8))
    l2 = Image.alpha_composite(sh, l); ImageDraw.Draw(l2).text((x, y), s, font=f, fill=fill); return l2
def vis(key):
    if key not in lab: return None
    u, v, z = lab[key]
    if z <= 0 or not (0.04 < u < 0.96 and 0.10 < v < 0.93): return None
    return u * W, v * H
def at(key, text, t0, t1, bg=BLK, size=32, dy=-60):
    a = fade(t0, t1); p = vis(key)
    if not a or not p: return
    l = layer(); d = ImageDraw.Draw(l); x, y = p
    d.line([x, y, x, y + dy + (20 if dy < 0 else -20)], fill=WHT, width=3); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WHT)
    tag(d, x, y + dy, text, size, bg); paste(l, a)
def marker(key, kind, text, col, t0, t1, dy=-170, R=56):
    a = fade(t0, t1); p = vis(key)
    if not a or not p: return
    l = layer(); d = ImageDraw.Draw(l); x, y = p; cy = y + dy
    d.line([x, y, x, cy + R], fill=WHT, width=4); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=WHT)
    d.ellipse([x - R - 5, cy - R - 5, x + R + 5, cy + R + 5], fill=WHT); l.alpha_composite(portrait(kind, R, col + (255,)), (int(x - R), int(cy - R)))
    tag(d, x, cy - R - 34, text, 28, BLK); paste(l, a)
def bubble(text, sub, t0, t1, y=520):
    a = fade(t0, t1)
    if not a: return
    l = layer(); d = ImageDraw.Draw(l); tag(d, W / 2, y, text, 64, RED, WHT, (26, 12))
    if sub: tag(d, W / 2, y + 86, sub, 30, BLK, WHT)
    paste(l, a)

# ---- intestazione: data e capitolo
PH = [(0, 26.4, 'SPRING 1453', '01', 'THE WALLS'), (26.4, 35.2, 'APRIL 1453', '02', 'THE CANNON'), (35.2, 37.9, 'NIGHT', '02', 'THE CANNON'),
      (37.9, 50.9, '22 APRIL 1453', '03', 'THE CHAIN'), (50.9, 99, '29 MAY 1453', '04', 'THE FALL')]
for t0, t1, chip, n, title in PH:
    if t0 <= sec < t1: break
l = layer(); d = ImageDraw.Draw(l)
x0, y0, x1, y1 = tag(d, 60, 110, '     ' + chip, 30, WHT, BLK, anchor='tl')
d.ellipse([x0 + 14, (y0 + y1) / 2 - 6, x0 + 26, (y0 + y1) / 2 + 6], fill=RED)
d.rectangle([60, 180, 122, 236], fill=RED); d.text((74, 186), n, font=O(34), fill=WHT)
tag(d, 122, 180, title, 34, BLK, WHT, (16, 6), anchor='tl')
paste(l, 1.0)

# ---- 1. gancio
a = fade(0.0, 3.3)
if a:
    l = layer(); d = ImageDraw.Draw(l); tag(d, W / 2, 610, 'NEVER BREACHED IN', 34, RED, WHT); l = big(l, '1,000', 640); d = ImageDraw.Draw(l)
    tag(d, W / 2, 990, 'YEARS', 50, BLK, WHT, (24, 8)); paste(l, a)
marker('CANNON', 'cannon', "ORBAN'S CANNON · 9 M", (60, 60, 60), 3.6, 5.1, -190)

# ---- 2. l'acqua su tre lati
at('MARMARA', 'SEA OF MARMARA', 9.9, 11.6, SEA, 30, -40)
at('GOLDEN HORN', 'GOLDEN HORN', 10.2, 11.6, SEA, 30, -40)
at('BOSPHORUS', 'BOSPHORUS', 10.5, 11.6, SEA, 30, -40)
at('CITY', 'CONSTANTINOPLE', 7.6, 11.6, RED, 38, -70)

# ---- 3. le mura: sezione disegnata + etichette sul terreno
a = fade(11.7, 19.2)
if a:
    l = layer(); d = ImageDraw.Draw(l); X0, Y0, SW = 90, 1120, 900      # sezione schematica, da ovest (sinistra) a est
    d.rounded_rectangle([X0 - 30, Y0 - 330, X0 + SW + 30, Y0 + 60], 22, fill=(10, 12, 18, 215))
    tag(d, X0, Y0 - 310, 'THEODOSIAN WALLS · CROSS-SECTION', 26, RED, WHT, anchor='tl')
    gy = Y0; d.line([X0, gy, X0 + SW, gy], fill=(150, 140, 120), width=4)
    k1, k2, k3 = fade(13.9, 19.2, 0.2), fade(14.5, 19.2, 0.2), fade(15.4, 19.2, 0.2)
    if k1: d.rectangle([X0 + 60, gy, X0 + 260, gy + 40], fill=(30, 90, 170)); tag(d, X0 + 160, gy - 40, 'MOAT · 20 M', 22, BLK, WHT)
    if k2: d.rectangle([X0 + 330, gy - 150, X0 + 360, gy], fill=(190, 175, 150)); tag(d, X0 + 345, gy - 190, 'OUTER WALL', 22, BLK, WHT)
    if k3:
        d.rectangle([X0 + 560, gy - 230, X0 + 620, gy], fill=(215, 200, 175))
        for yy in range(int(gy - 220), int(gy), 34): d.line([X0 + 560, yy, X0 + 620, yy], fill=(150, 60, 40), width=4)
        d.rectangle([X0 + 640, gy - 290, X0 + 740, gy], fill=(205, 190, 165)); tag(d, X0 + 650, gy - 270, 'INNER WALL · 12 M', 22, RED, WHT)
    if sec > 17.6: tag(d, X0 + SW - 130, gy - 120, '96 TOWERS', 40, RED, WHT)
    d.text((X0 + 10, gy + 14), 'OUTSIDE', font=O(20), fill=(200, 200, 200)); d.text((X0 + SW - 90, gy + 14), 'CITY', font=O(20), fill=(200, 200, 200))
    paste(l, a)

# ---- 4. le forze
a = fade(19.4, 26.3)
if a:
    l = layer(); d = ImageDraw.Draw(l)
    d.ellipse([W / 2 - 66, 560, W / 2 + 66, 692], fill=WHT); l.alpha_composite(portrait('mehmed', 62, RED + (255,)), (int(W / 2 - 62), 564))
    tag(d, W / 2, 730, 'SULTAN MEHMED II · AGE 21', 30, BLK, WHT)
    l = big(l, '~80,000', 760, 170, fill=(255, 235, 230)); d = ImageDraw.Draw(l)
    if sec > 23.0:
        d.ellipse([W / 2 - 66, 990, W / 2 + 66, 1122], fill=WHT); l.alpha_composite(portrait('constantine', 62, BLU + (255,)), (int(W / 2 - 62), 994))
        tag(d, W / 2, 1160, 'EMPEROR CONSTANTINE XI', 30, BLK, WHT); tag(d, W / 2, 1230, '~7,000 DEFENDERS', 54, BLU, WHT, (22, 8))
    paste(l, a)

# ---- 5. il cannone
marker('CANNON', 'cannon', "ORBAN'S CANNON", (60, 60, 60), 26.6, 28.4, -190)
bubble('HALF A TON', 'STONE BALL, ~500 KG', 28.5, 30.6)
bubble('A FEW SHOTS A DAY', 'IT HAD TO COOL BETWEEN SHOTS', 30.8, 32.8)
bubble('THE WALL CRACKS', None, 33.0, 35.2)
# ---- 6. notte
bubble('REBUILT EVERY NIGHT', 'TIMBER, EARTH AND BARRELS', 35.4, 37.8)
# ---- 7. la catena
at('CHAIN', 'THE GREAT CHAIN', 38.0, 42.3, GLD, 34, -80)
at('GOLDEN HORN', 'GOLDEN HORN', 38.2, 42.3, SEA, 28, -40)
# ---- 8. le navi sulla collina
bubble('THE IMPOSSIBLE', None, 40.5, 42.5)
at('SHIPS', '~70 SHIPS OVER THE HILL', 42.7, 47.5, RED, 34, -110)
at('GALATA', 'GALATA HILL', 43.0, 47.5, BLK, 28, -60)
# ---- 9. da ogni lato
bubble('SURROUNDED', 'LAND · SEA · GOLDEN HORN', 47.8, 50.8)
# ---- 10. la caduta
a = fade(51.0, 55.3)
if a:
    l = layer(); d = ImageDraw.Draw(l); n = int(1 + 52 * min(1, max(0, (sec - 51.0) / 2.4)))
    tag(d, W / 2, 560, 'DAY', 40, BLK, WHT); l = big(l, str(n), 600, 200); paste(l, a)
bubble('THE WALL FALLS', None, 53.8, 55.3, y=1150)
# ---- 11. Costantino
marker('BREACH', 'constantine', 'CONSTANTINE XI · LAST SEEN HERE', BLU, 55.4, 58.0, -200)
# ---- 12. chiusura
bubble('1,000-YEAR EMPIRE', 'ENDED 29 MAY 1453', 58.2, 61.6)
bubble('A CANNON. AND A FLEET', 'THAT CROSSED A HILL.', 61.6, 64.8)
a = fade(63.4, 64.8)
if a:
    l = layer(); d = ImageDraw.Draw(l); tag(d, W / 2, 1250, 'SUBSCRIBE FOR MORE', 44, RED, WHT, (30, 14)); paste(l, a)

# ---- sottotitoli
cur = None
for c in TIM['captions']:
    if c['start'] <= sec < c['end']: cur = c['text']
if cur:
    l = layer(); d = ImageDraw.Draw(l); f = O(58); bb = d.textbbox((0, 0), cur, font=f)
    x, y = W / 2 - (bb[2] - bb[0]) / 2, 1440
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 3)): d.text((x + dx, y + dy), cur, font=f, fill=(0, 0, 0, 200))
    d.text((x, y), cur, font=f, fill=WHT); paste(l, 1.0)
im.convert('RGB').save(OUT, quality=92)
