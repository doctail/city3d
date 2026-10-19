# Sostituisce l'anno finale (es. 2026) con "NOW" su una copertina gia' fatta con thumb_city.py.
# Uso: python3 thumb_now.py IN.jpg OUT.jpg ANNO_INIZIO [ANNO_FINE=2026]
import sys, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
IN, OUT, Y0 = sys.argv[1:4]; Y1 = sys.argv[4] if len(sys.argv) > 4 else '2026'
FD = os.environ.get('FONTS', '/tmp/claude-0/fonts'); OSW = f'{FD}/oswald/package/files/oswald-latin-600-normal.woff'
GOLD = (240, 180, 70); WHITE = (250, 248, 242); DARK = (12, 16, 20)
im = Image.open(IN).convert('RGB'); d = ImageDraw.Draw(im); fy = ImageFont.truetype(OSW, 92)
l = d.textlength(Y0, font=fy); r = d.textlength(Y1, font=fy); gap = 260; x0 = 640 - (l + gap + r) / 2; y = 118; xs = x0 + l + gap
m = Image.new('L', im.size, 0); ImageDraw.Draw(m).text((xs, y), Y1, font=fy, fill=255, anchor='ls', stroke_width=5, stroke_fill=255)
mk = cv2.dilate(np.array(m), np.ones((9, 9), np.uint8))
out = cv2.inpaint(cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR), mk, 9, cv2.INPAINT_TELEA)
im = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(im)
d.text((xs, y), 'NOW', font=fy, fill=GOLD, anchor='ls', stroke_width=5, stroke_fill=DARK)
im.save(OUT, quality=93); print('ok', OUT)
