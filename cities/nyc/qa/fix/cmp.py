"""cmp.py A B out.jpg [labels...]: side-by-side before(A dir)/after(B dir) per label, prints mean V and S p90"""
import sys, numpy as np
from PIL import Image, ImageDraw
A, B, out = sys.argv[1:4]; labs = sys.argv[4:]
def met(p):
    im = Image.open(p).convert('RGB'); h = np.asarray(im.convert('HSV')).astype(float) / 255
    return h[..., 2].mean(), np.percentile(h[..., 1], 90)
rows = []
for l in labs:
    a = Image.open(f'{A}/{l}.jpg').convert('RGB'); b = Image.open(f'{B}/{l}.jpg').convert('RGB')
    w, h = 640, 360; r = Image.new('RGB', (2 * w, h + 16), (20, 20, 20)); r.paste(a.resize((w, h)), (0, 16)); r.paste(b.resize((w, h)), (w, 16))
    ma, mb = met(f'{A}/{l}.jpg'), met(f'{B}/{l}.jpg')
    ImageDraw.Draw(r).text((4, 2), f'{l} BEFORE V={ma[0]:.2f} Sp90={ma[1]:.2f}   |   AFTER V={mb[0]:.2f} Sp90={mb[1]:.2f}', fill=(255, 255, 255))
    rows.append(r); print(l, 'before V %.3f S90 %.3f | after V %.3f S90 %.3f' % (*ma, *mb))
s = Image.new('RGB', (rows[0].width, sum(r.height for r in rows)))
y = 0
for r in rows: s.paste(r, (0, y)); y += r.height
s.save(out, quality=88)
