# Infografica stile "One Map, One Battle" sopra il render 3D (v4, 1 nov): Short completo legato ai secondi della voce.
# Uso: overlay.py <frame.png> <secondo> <out.png>     Tempi e sottotitoli da audio/termopili_tempi.json
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from portraits import portrait
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC, sec, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
W, H = 1080, 1920
im = Image.open(SRC).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')
lab = json.load(open(SRC + '.json'))
TIM = json.load(open(os.path.join(HERE, 'audio', 'termopili_tempi.json')))
FD = os.environ.get('FONTS', '/tmp/fonts/')
A = lambda s: ImageFont.truetype(FD + 'anton/files/anton-latin-400-normal.woff', s)
O = lambda s: ImageFont.truetype(FD + 'oswald/files/oswald-latin-700-normal.woff', s)
RED, BLK, WHT, BLU, ORG, GRY = (200, 30, 28), (16, 16, 18), (255, 255, 255), (30, 80, 210), (230, 110, 20), (110, 110, 118)

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
    if anchor == 'mm':
        x0, y0 = x - w / 2 - pad[0], y - h / 2 - pad[1]; x0 = max(20, min(W - 20 - w - 2 * pad[0], x0))
    else: x0, y0 = x, y
    d.rectangle([x0, y0, x0 + w + 2 * pad[0], y0 + h + 2 * pad[1] + 4], fill=bg)
    d.text((x0 + pad[0], y0 + pad[1] - bb[1]), text, font=f, fill=fg)
    return x0, y0, x0 + w + 2 * pad[0], y0 + h + 2 * pad[1]
def big(l, s, y, size=250):
    f = A(size); d = ImageDraw.Draw(l); bb = d.textbbox((0, 0), s, font=f); x = W / 2 - (bb[2] - bb[0]) / 2
    sh = layer(); ImageDraw.Draw(sh).text((x + 6, y + 8), s, font=f, fill=(0, 0, 0, 170)); sh = sh.filter(ImageFilter.GaussianBlur(8))
    l2 = Image.alpha_composite(sh, l); ImageDraw.Draw(l2).text((x, y), s, font=f, fill=WHT); return l2

# ---- intestazione: data e capitolo per fase
PH = [(0, 26.9, 'AUGUST 480 BC', '01', 'THE PASS'), (26.9, 32.0, 'DAY 1', '01', 'THE PASS'), (32.0, 36.8, 'DAY 2', '01', 'THE PASS'),
      (36.8, 47.35, 'NIGHT · DAY 2', '02', 'THE PATH'), (47.35, 59.3, 'DAWN · DAY 3', '03', 'THE LAST STAND'), (59.3, 99, 'TODAY', '04', 'THERMOPYLAE TODAY')]
for t0, t1, chip, n, title in PH:
    if t0 <= sec < t1: break
l = layer(); d = ImageDraw.Draw(l)
x0, y0, x1, y1 = tag(d, 60, 110, '     ' + chip, 30, WHT, BLK, anchor='tl')
d.ellipse([x0 + 14, (y0 + y1) / 2 - 6, x0 + 26, (y0 + y1) / 2 + 6], fill=RED)
d.rectangle([60, 180, 122, 236], fill=RED); d.text((74, 186), n, font=O(34), fill=WHT)
tag(d, 122, 180, title, 34, BLK, WHT, (16, 6), anchor='tl')
paste(l, 1.0)

# ---- scena 1: gancio
a = fade(0.0, 5.55)
if a:
    l = layer(); d = ImageDraw.Draw(l); tag(d, W / 2, 600, 'GREEKS AT THE PASS', 34, RED, WHT)
    l = big(l, '7,000', 640); d = ImageDraw.Draw(l)
    if sec > 1.5: tag(d, W / 2, 1010, 'VS  100,000+  PERSIANS (EST.)', 40, BLK, WHT)
    if sec > 4.4: tag(d, W / 2, 1130, 'HOW?', 78, RED, WHT, (30, 10))
    paste(l, a)

# ---- etichette e segnalini agganciati al terreno
def vis(key):
    if key not in lab: return None
    u, v, z = lab[key]
    if z <= 0 or not (0.03 < u < 0.97 and 0.08 < v < 0.95): return None
    return u * W, v * H
def at(key, text, t0, t1, bg=BLK, size=32, dy=-60):
    a = fade(t0, t1); p = vis(key)
    if not a or not p: return
    l = layer(); d = ImageDraw.Draw(l); x, y = p
    d.line([x, y, x, y + dy + (20 if dy < 0 else -20)], fill=WHT, width=3); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WHT)
    tag(d, x, y + dy, text, size, bg); paste(l, a)
def marker(key, kind, text, col, t0, t1, dy=-150):
    a = fade(t0, t1); p = vis(key)
    if not a or not p: return
    l = layer(); d = ImageDraw.Draw(l); x, y = p; cy = y + dy; R = 52
    d.line([x, y, x, cy + R], fill=WHT, width=4); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=WHT)
    d.ellipse([x - R - 5, cy - R - 5, x + R + 5, cy + R + 5], fill=WHT)
    l.alpha_composite(portrait(kind, R, col + (255,)), (int(x - R), int(cy - R)))
    tag(d, x, cy - R - 34, text, 28, BLK); paste(l, a)
def bubble(text, sub, t0, t1, y=520):
    a = fade(t0, t1)
    if not a: return
    l = layer(); d = ImageDraw.Draw(l); tag(d, W / 2, y, text, 64, RED, WHT, (26, 12))
    if sub: tag(d, W / 2, y + 86, sub, 30, BLK, WHT)
    paste(l, a)

night = 36.8 <= sec < 47.35
# scena 2
marker('XERXES', 'xerxes', 'XERXES · PERSIAN ARMY', RED, 7.6, 14.6, -170)
# scena 3
at('THE HOT GATES', 'THE HOT GATES', 15.7, 22.0, BLK, 34, 190)
at('MALIAN GULF', 'SEA (480 BC COAST)', 16.8, 22.0, (20, 60, 110), 28, -50)
at('KALLIDROMO', 'MOUNT KALLIDROMO', 16.8, 22.0, (60, 70, 40), 28, -50)
bubble('NO ROOM TO SURROUND', 'IN PLACES, ONE CART WIDE', 16.9, 22.0)
# scena 4
at('WALL', 'PHOCIAN WALL', 22.6, 26.8, (90, 80, 60), 30, -170)
marker('GREEKS', 'spartan', 'LEONIDAS · 300 SPARTANS', BLU, 22.3, 47.3, -150 if night else 170)   # in scena 8 lascia spazio ai gettoni
# scena 5
marker('PERSIANS', 'xerxes', 'XERXES · WAVE AFTER WAVE', RED, 27.1, 31.8, -170)
at('IMMDAY', 'IMMORTALS', 32.2, 34.6, ORG, 30, -70)
bubble('EVEN THE IMMORTALS', "XERXES' ELITE GUARD, THROWN BACK", 32.2, 34.6)
bubble('THE WALL HOLDS', 'TWO DAYS OF ASSAULTS', 34.8, 36.8)
# scene 6-7
bubble('THE BETRAYAL', 'EPHIALTES SHOWS XERXES A PATH OVER THE MOUNTAIN', 37.0, 42.85)
at('ANOPAEA PATH', 'ANOPAEA PATH', 41.0, 47.3, RED, 34, 90)
marker('IMMORTALS', 'immortal', 'HYDARNES · IMMORTALS', ORG, 43.1, 47.3, -150)
bubble('SURROUNDED', 'BY DAWN, THE PERSIANS ARE BEHIND THEM', 45.9, 47.35)

# scena 8: gettoni (1 gettone = 100 uomini): 7,000 -> ~1,400
a = fade(47.5, 54.2)
if a:
    l = layer(); d = ImageDraw.Draw(l); go = min(1.0, max(0.0, (sec - 48.3) / 1.6)); go = go * go * (3 - 2 * go)
    stayed = min(1.0, max(0.0, (sec - 50.0) / 0.6))
    d.rounded_rectangle([W / 2 - 250, 570, W / 2 + 250, 1150], 24, fill=(10, 12, 18, 205))     # pannello scuro sotto i gettoni
    tag(d, W / 2, 610, '1 SHIELD = 100 MEN', 26, BLK, WHT)
    R, gap, cols = 17, 44, 10; x0 = W / 2 - (cols - 1) * gap / 2; yb = 680
    for i in range(70):
        r, c = divmod(i, cols); x = x0 + c * gap; y = yb + r * gap
        stay = r < 2 and 2 <= c <= 8                     # 14 gettoni = ~1.400 restano
        if not stay:
            gi = min(1.0, max(0.0, (sec - 48.3 - 0.07 * (9 - c) - 0.03 * r) / 1.1)); gi = gi * gi * (3 - 2 * gi); x += gi * (W + 200 - x); fill = tuple(int(BLU[k] * (1 - gi) + GRY[k] * gi) for k in range(3))
        else: fill = BLU
        if -R < x < W / 2 + 250 - R:
            d.ellipse([x - R - 3, y - R - 3, x + R + 3, y + R + 3], fill=WHT); d.ellipse([x - R, y - R, x + R, y + R], fill=fill)
            d.line([x, y - R + 5, x, y + R - 5], fill=WHT, width=3)
    if stayed:
        tag(d, W / 2, 1020, '~1,400 STAYED', 60, RED, WHT, (24, 10)); tag(d, W / 2, 1100, '300 SPARTANS · 700 THESPIANS · 400 THEBANS', 26, BLK, WHT)
    else:
        tag(d, W / 2, 1020, '7,000', 60, BLU, WHT, (24, 10))
    paste(l, a)

# scena 9
at('KOLONOS', 'KOLONOS HILL', 54.4, 59.0, BLK, 32, 130)
bubble('THE LAST STAND', 'THEY FOUGHT TO THE LAST MAN', 54.4, 56.95)
# scena 10
bubble('XERXES TAKES THE PASS', 'THE ROAD TO ATHENS IS OPEN', 57.1, 59.2)
bubble('WITHIN A YEAR: DEFEAT', 'SALAMIS 480 BC · PLATAEA 479 BC', 59.4, 62.7)
at('COAST480', 'COAST IN 480 BC', 60.0, 62.7, (20, 60, 110), 28, -60)
at('COASTTODAY', 'COAST TODAY', 60.3, 62.7, (20, 60, 110), 28, -60)
a = fade(61.0, 62.7)
if a:
    l = layer(); d = ImageDraw.Draw(l); tag(d, W / 2, 1250, 'SUBSCRIBE FOR MORE', 44, RED, WHT, (30, 14))
    paste(l, a)

# ---- sottotitoli (2-3 parole, tempi dalla voce)
cur = None
for c in TIM['captions']:
    if c['start'] <= sec < c['end']: cur = c['text']
if cur:
    l = layer(); d = ImageDraw.Draw(l); f = O(58); bb = d.textbbox((0, 0), cur, font=f)
    x, y = W / 2 - (bb[2] - bb[0]) / 2, 1440
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 3)): d.text((x + dx, y + dy), cur, font=f, fill=(0, 0, 0, 200))
    d.text((x, y), cur, font=f, fill=WHT); paste(l, 1.0)
im.convert('RGB').save(OUT, quality=92)
