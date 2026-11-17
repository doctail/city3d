"""Foglio A/B/C: righe = camere (v1, v3, Oakland, Strip/Lawrenceville, v1 2024, nadir), colonne = A corrente | B palette reale + sole neutro | C + esposizione/cielo.
Uso: python make_sheet.py out.jpg A_dir B_dir C_dir"""
import sys
from PIL import Image, ImageDraw
out, dirs = sys.argv[1], sys.argv[2:]
names = ['A  current (default)', 'B  real palette + neutral sun', 'C  B + exposure -0.6 EV + cool horizon']
rows = ['v1 Point 1936.15', 'v3 north 1936.15', 'Oakland 1936.15', 'Strip/Lawrenceville 1936.15', 'v1 Point 2024.5', 'nadir 2024.5']
cw, ch = 640, 360
S = Image.new('RGB', (cw * len(dirs), ch * len(rows)), 'black'); d = ImageDraw.Draw(S)
for j, r in enumerate(rows):
    for i, dr in enumerate(dirs):
        im = Image.open(f'{dr}/{j + 1:04d}.jpg').convert('RGB').resize((cw, ch), Image.LANCZOS); S.paste(im, (i * cw, j * ch))
        d.rectangle([i * cw, j * ch, i * cw + 330, j * ch + 18], fill=(0, 0, 0)); d.text((i * cw + 4, j * ch + 3), f'{names[i][:3]} | {r}' if i == 0 else names[i][:3] + ' | ' + r, fill=(255, 255, 255))
S.save(out, quality=88)
print(out, S.size)
