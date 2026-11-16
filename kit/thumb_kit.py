"""Year Built thumbnail composer (split screen, both halves full).

Usage: python -m kit.thumb_kit OUT.jpg --left L.jpg --right R.jpg --title VALENCIA
         --ly 1238 --ry NOW [--lbox x0,y0,w] [--rbox x0,y0,w]
Boxes crop a region (x0, y0, width) of each 16:9 frame; height follows the aspect.
Rules: kit/AVVIO_NUOVA_CITTA.md "Thumbnail layout".
"""
import argparse
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
YELLOW = (255, 214, 0)


def _prep(img, box, sat=1.4, con=1.2, bri=1.05):
    x0, y0, w = box
    pw = W // 2 + 60
    h = int(w * H / pw)
    c = img.crop((x0, y0, x0 + w, y0 + h)).resize((pw, H), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(2, 120, 2))
    c = ImageEnhance.Color(c).enhance(sat)
    c = ImageEnhance.Contrast(c).enhance(con)
    return ImageEnhance.Brightness(c).enhance(bri)


def compose(left, right, title, ly, ry, lbox, rbox, out, ts=118, lx=215, rx=1065):
    L = _prep(Image.open(left).convert('RGB'), lbox)
    R = _prep(Image.open(right).convert('RGB'), rbox)
    base = Image.new('RGB', (W, H))
    base.paste(L, (0, 0))
    rf = Image.new('RGB', (W, H))
    rf.paste(R, (W - R.width, 0))
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).polygon([(W // 2 + 40, 0), (W, 0), (W, H), (W // 2 - 40, H)], fill=255)
    im = Image.composite(rf, base, mask)
    d = ImageDraw.Draw(im)
    d.line([(W // 2 + 40, 0), (W // 2 - 40, H)], fill=(255, 255, 255), width=6)

    def txt(xy, s, size, fill, stroke):
        d.text(xy, s, font=ImageFont.truetype(FONT, size), fill=fill, anchor='mm',
               stroke_width=stroke, stroke_fill=(0, 0, 0))
    txt((lx, 85), ly, ts, YELLOW, 10)
    txt((rx, 85), ry, ts, YELLOW, 10)
    txt((W // 2, 85), '›', 100, (255, 255, 255), 8)
    size = 205 if len(title) <= 9 else int(205 * 9 / len(title))
    txt((W // 2, 615), title, size, (255, 255, 255), 14)
    im.filter(ImageFilter.UnsharpMask(1, 60, 2)).save(out, quality=95)


def _box(s):
    a = [int(x) for x in s.split(',')]
    return tuple(a)


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('out')
    a.add_argument('--left', required=True)
    a.add_argument('--right', required=True)
    a.add_argument('--title', required=True)
    a.add_argument('--ly', required=True)
    a.add_argument('--ry', default='NOW')
    a.add_argument('--lbox', default='0,0,1280')
    a.add_argument('--rbox', default='0,0,1280')
    a.add_argument('--city', help='slug: reads city.cover.text_size / text_lx / text_rx from cities/<slug>/story.json')
    a.add_argument('--text-size', type=int)
    a.add_argument('--lx', type=int)
    a.add_argument('--rx', type=int)
    o = a.parse_args()
    cv = {}
    if o.city:
        import json, os
        cv = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'cities', o.city, 'story.json')))['city'].get('cover', {})
    compose(o.left, o.right, o.title.upper(), o.ly, o.ry, _box(o.lbox), _box(o.rbox), o.out,
            o.text_size or cv.get('text_size', 118), o.lx or cv.get('text_lx', 215), o.rx or cv.get('text_rx', 1065))
