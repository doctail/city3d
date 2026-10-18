# Copertina stile "Year Built" (formato della nicchia: anni in alto con freccia, nome citta' spaziato in basso, bandiera).
# Uso: python3 thumb_city.py OUT.jpg "NEW YORK" 1609 2026 DOPO.jpg [PRIMA.jpg] [--flag us] [--box x0 y0 x1 y1] [--box-before x0 y0 x1 y1]
# SAT=1.0 (variabile d'ambiente) per meno saturazione (default 1.3)
# Con PRIMA.jpg fa lo split diagonale prima|dopo (stessa camera), senza fa un'immagine sola.
# Font: @fontsource/anton e @fontsource/oswald (npm pack, file .woff) in FONTS (default /tmp/claude-0/fonts).
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
a = sys.argv[1:]
def opt(n, k=1, d=None):
    if n in a: i = a.index(n); v = a[i + 1:i + 1 + k]; del a[i:i + 1 + k]; return v if k > 1 else v[0]
    return d
FLAG = opt('--flag', 1, 'none'); BOX = opt('--box', 4); BOX2 = opt('--box-before', 4); FD = os.environ.get('FONTS', '/tmp/claude-0/fonts')
OUT, NAME, Y0, Y1, AFTER = a[:5]; BEFORE = a[5] if len(a) > 5 else None
ANT = f'{FD}/anton/package/files/anton-latin-400-normal.woff'; OSW = f'{FD}/oswald/package/files/oswald-latin-600-normal.woff'
INTER = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
GOLD = (240, 180, 70); WHITE = (250, 248, 242); DARK = (12, 16, 20)

def prep(p, box=None):
    im = Image.open(p).convert('RGB'); box = box or BOX
    if box: im = im.crop(tuple(map(int, box)))
    im = im.resize((1280, 720), Image.LANCZOS)
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(float(os.environ.get('SAT', '1.3')))).enhance(1.12)
def shade(im):   # scurisce in alto e in basso per far leggere le scritte
    g = Image.new('L', (1, 720))
    for y in range(720):
        t = max(0, (y - 470) / 250); u = max(0, (150 - y) / 150)
        g.putpixel((0, y), int(255 * min(1, 0.85 * t ** 1.3 + 0.75 * u ** 1.5)))
    return Image.composite(Image.new('RGB', (1280, 720), (8, 12, 16)), im, g.resize((1280, 720)))
def flag_us(d, x, y, w, h):
    for i in range(13): d.rectangle([x, y + i * h / 13, x + w, y + (i + 1) * h / 13], fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.42, y + h * 7 / 13], fill=(60, 59, 110))
    for r in range(4):
        for c in range(5):
            cx = x + w * 0.42 * (c + 0.5) / 5; cy = y + h * 7 / 13 * (r + 0.5) / 4; d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill='white')
    d.rectangle([x, y, x + w, y + h], outline=DARK, width=2)
def flag_es(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(170, 21, 27)); d.rectangle([x, y + h / 4, x + w, y + h * 3 / 4], fill=(241, 191, 0))
    d.rectangle([x, y, x + w, y + h], outline=DARK, width=2)
def flag_nl(d, x, y, w, h):
    for i, c in enumerate([(174, 28, 40), (255, 255, 255), (33, 70, 139)]): d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
FLAGS = {'us': flag_us, 'es': flag_es, 'nl': flag_nl}

img = prep(AFTER)
if BEFORE:
    m = Image.new('L', (1280, 720), 0); ImageDraw.Draw(m).polygon([(0, 0), (720, 0), (480, 720), (0, 720)], fill=255)
    img.paste(prep(BEFORE, BOX2), (0, 0), m); ImageDraw.Draw(img).line([(720, 0), (480, 720)], fill=GOLD, width=6)
im = shade(img); d = ImageDraw.Draw(im)
fy = ImageFont.truetype(OSW, 92); l = d.textlength(Y0, font=fy); r = d.textlength(Y1, font=fy); gap = 260; x0 = 640 - (l + gap + r) / 2; y = 118
for x, s in ((x0, Y0), (x0 + l + gap, Y1)): d.text((x, y), s, font=fy, fill=WHITE, anchor='ls', stroke_width=5, stroke_fill=DARK)
ax0, ax1, ay = x0 + l + 30, x0 + l + gap - 30, y - 34
d.line([(ax0, ay), (ax1 - 24, ay)], fill=DARK, width=16); d.line([(ax0, ay), (ax1 - 24, ay)], fill=GOLD, width=9)
d.polygon([(ax1, ay), (ax1 - 34, ay - 20), (ax1 - 34, ay + 20)], fill=GOLD, outline=DARK)
size = 150
while True:   # il nome deve stare in larghezza
    fn = ImageFont.truetype(ANT, size); track = size * 0.15
    tot = sum(d.textlength(c, font=fn) for c in NAME) + track * (len(NAME) - 1) + (130 if FLAG in FLAGS else 0)
    if tot < 1180 or size < 70: break
    size -= 6
x = 640 - tot / 2
if FLAG in FLAGS: FLAGS[FLAG](d, x, 680 - size * 0.62, size * 0.64, size * 0.41); x += 130
for c in NAME:
    d.text((x, 680), c, font=fn, fill=WHITE, anchor='ls', stroke_width=6, stroke_fill=DARK); x += d.textlength(c, font=fn) + track
d.text((22, 700), 'YEAR BUILT', font=ImageFont.truetype(INTER, 20), fill=(235, 230, 220), anchor='ls', stroke_width=2, stroke_fill=DARK)
im.save(OUT, quality=92); print('ok', OUT)
