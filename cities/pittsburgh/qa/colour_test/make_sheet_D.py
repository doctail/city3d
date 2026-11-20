"""Foglio A | B | D (960x540 per cella, 6 camere): A default (giallo) | B iterazione 1 (palette reale, -2.6 EV) | D iterazione 2 (saturazione, acqua, strade, ground_tint).
Uso: python make_sheet_D.py out.jpg A_dir B_dir D_dir"""
import sys
from PIL import Image, ImageDraw
out, dirs = sys.argv[1], sys.argv[2:]
names = ['A current default', 'B iter.1 real palette', 'D iter.2 sat+water+streets+tint']
rows = ['v1 Point 1936.15', 'v3 north 1936.15', 'Oakland 1936.15', 'Strip/Lawrenceville 1936.15', 'v1 Point 2024.5', 'nadir 2024.5']
cw, ch = 960, 540
S = Image.new('RGB', (cw * len(dirs), ch * len(rows)), 'black'); d = ImageDraw.Draw(S)
for j, r in enumerate(rows):
    for i, dr in enumerate(dirs):
        S.paste(Image.open(f'{dr}/{j + 1:04d}.jpg').convert('RGB').resize((cw, ch), Image.LANCZOS), (i * cw, j * ch))
        d.rectangle([i * cw, j * ch, i * cw + 420, j * ch + 18], fill=(0, 0, 0)); d.text((i * cw + 4, j * ch + 3), f'{names[i]} | {r}', fill=(255, 255, 255))
S.save(out, quality=85)
print(out, S.size)
