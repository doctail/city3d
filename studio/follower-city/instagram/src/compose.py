"""Testi e copertine con PIL. Uso: python compose.py post|stories|grid"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
F = "/usr/share/fonts/opentype/inter/"
def font(w, s): return ImageFont.truetype(F + f"Inter-{w}.otf", s)
INK = (62, 48, 40)

def tw(d, t, f): b = d.textbbox((0, 0), t, font=f); return b[2] - b[0]

def post():
    im = Image.open(os.path.join(OUT, "post_raw.png")).convert("RGB")
    d = ImageDraw.Draw(im)
    f = font("SemiBold", 44); t = "1 follower = 1 building"
    d.text(((1080 - tw(d, t, f)) / 2, 1215), t, font=f, fill=INK)
    f2 = font("Medium", 28); t2 = "LEDGER OF CITIES  ·  DAY 0"
    d.text(((1080 - tw(d, t2, f2)) / 2, 1280), t2, font=f2, fill=(105, 90, 80))
    im.save(os.path.join(OUT, "post1_1080x1350.png"))

# ---- storie: icone semplici su pastello
PAL = {"daybyday": (244, 214, 196), "ogs": (214, 226, 205), "requests": (205, 219, 232), "making": (240, 226, 190), "ledger": (226, 210, 224)}
LINE = (74, 58, 50)
def lw(): return 14

def icon_daybyday(d, cx, cy):   # calendario con casetta
    d.rounded_rectangle((cx-210, cy-190, cx+210, cy+210), 40, outline=LINE, width=lw(), fill=(255, 250, 243))
    d.line((cx-210, cy-90, cx+210, cy-90), fill=LINE, width=lw())
    for x in (-110, 110): d.rounded_rectangle((cx+x-9, cy-235, cx+x+9, cy-150), 9, fill=LINE)
    d.polygon([(cx-90, cy+30), (cx, cy-45), (cx+90, cy+30)], fill=(201, 107, 79), outline=LINE)
    d.rectangle((cx-65, cy+30, cx+65, cy+140), fill=(240, 205, 150), outline=LINE, width=10)
    d.rectangle((cx-18, cy+80, cx+18, cy+140), fill=(122, 160, 190))

def icon_ogs(d, cx, cy):        # ticket con stella
    d.rounded_rectangle((cx-250, cy-140, cx+250, cy+140), 36, outline=LINE, width=lw(), fill=(255, 250, 243))
    for y in (cy-140, cy+140):
        for x in (cx-60, cx+60): pass
    d.ellipse((cx-250-40, cy-40, cx-250+40, cy+40), fill=PAL["ogs"]); d.ellipse((cx+250-40, cy-40, cx+250+40, cy+40), fill=PAL["ogs"])
    pts = []
    for i in range(10):
        r = 95 if i % 2 == 0 else 40; a = -math.pi/2 + i*math.pi/5
        pts.append((cx + r*math.cos(a), cy + 10 + r*math.sin(a)))
    d.polygon(pts, fill=(224, 160, 85), outline=LINE)
    d.line((cx-150, cy-95, cx+150, cy-95), fill=(201, 107, 79), width=8)

def icon_requests(d, cx, cy):   # fumetto con cuore
    d.rounded_rectangle((cx-230, cy-190, cx+230, cy+120), 60, outline=LINE, width=lw(), fill=(255, 250, 243))
    d.polygon([(cx-90, cy+110), (cx-150, cy+230), (cx+20, cy+110)], fill=(255, 250, 243))
    d.line((cx-90, cy+114, cx-150, cy+230), fill=LINE, width=lw()); d.line((cx-150, cy+230, cx+20, cy+114), fill=LINE, width=lw())
    d.ellipse((cx-95, cy-100, cx, cy-5), fill=(201, 107, 79)); d.ellipse((cx, cy-100, cx+95, cy-5), fill=(201, 107, 79))
    d.polygon([(cx-92, cy-30), (cx+92, cy-30), (cx, cy+75)], fill=(201, 107, 79))

def icon_making(d, cx, cy):     # cubo (Blender)
    s = 170; o = 85
    top = [(cx-s, cy-s+o), (cx-s+o, cy-s), (cx+s+o, cy-s), (cx+s, cy-s+o)]
    fr = [(cx-s, cy-s+o), (cx+s, cy-s+o), (cx+s, cy+s+o), (cx-s, cy+s+o)]
    sd = [(cx+s, cy-s+o), (cx+s+o, cy-s), (cx+s+o, cy+s), (cx+s, cy+s+o)]
    for poly, col in ((fr, (255, 250, 243)), (top, (224, 160, 85)), (sd, (157, 185, 150))):
        d.polygon(poly, fill=col)
        d.line(poly + [poly[0]], fill=LINE, width=lw(), joint="curve")

def icon_ledger(d, cx, cy):     # libro mastro con skyline
    d.rounded_rectangle((cx-210, cy-230, cx+210, cy+230), 30, outline=LINE, width=lw(), fill=(255, 250, 243))
    d.rectangle((cx-210, cy-230, cx-150, cy+230), fill=(122, 160, 190), outline=LINE, width=lw())
    for i, (x, h, c) in enumerate([(-90, 150, (201,107,79)), (-20, 230, (157,185,150)), (50, 110, (224,160,85)), (110, 180, (122,160,190))]):
        d.rectangle((cx+x-30, cy+120-h, cx+x+30, cy+120), fill=c, outline=LINE, width=8)
    d.line((cx-120, cy+120, cx+170, cy+120), fill=LINE, width=lw())
    d.line((cx-100, cy-170, cx+120, cy-170), fill=LINE, width=lw())

def stories():
    ic = [("daybyday", icon_daybyday), ("ogs", icon_ogs), ("requests", icon_requests), ("making", icon_making), ("ledger", icon_ledger)]
    for i, (k, fn) in enumerate(ic, 1):
        im = Image.new("RGB", (1080, 1920), PAL[k]); d = ImageDraw.Draw(im)
        # alone chiaro
        lay = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay), 540, 540)
        lay = lay.resize((1620, 1620), Image.LANCZOS); im.paste(lay, (540 - 810, 960 - 810), lay)
        im.save(os.path.join(OUT, f"story{i}_{k}_1080x1920.png"))

def grid():
    W, H = 1080, 1440; g = 6; cw = (W - 2*g) // 3; ch = int(cw * 1.25)
    ph = 330; im = Image.new("RGB", (W, ph + 2 * ch + g + 20), (255, 255, 255)); d = ImageDraw.Draw(im)
    pr = Image.open(os.path.join(OUT, "profile_1080x1080.png")).resize((150, 150))
    m = Image.new("L", (150, 150), 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255); im.paste(pr, (30, 30), m)
    d.text((210, 40), "ledgerofcities", font=font("SemiBold", 34), fill=(30, 30, 30))
    d.text((210, 90), "1 follower = 1 building", font=font("Regular", 26), fill=(60, 60, 60))
    d.text((210, 128), "3 posts   1 followers   0 following", font=font("Regular", 24), fill=(90, 90, 90))
    cols = [(244, 214, 196), (214, 226, 205), (205, 219, 232), (240, 226, 190), (226, 210, 224)]
    for i, (k, _) in enumerate([("daybyday", 0), ("ogs", 0), ("requests", 0), ("making", 0), ("ledger", 0)]):
        x = 40 + i * 205; sm = Image.open(os.path.join(OUT, f"story{i+1}_{k}_1080x1920.png")).crop((0, 390, 1080, 1470)).resize((140, 140), Image.LANCZOS)
        m = Image.new("L", (140, 140), 0); ImageDraw.Draw(m).ellipse((0, 0, 139, 139), fill=255)
        d.ellipse((x-5, 205, x+145, 355-0), outline=(200, 200, 200), width=2) if False else None
        im.paste(sm, (x, 200), m)
        lab = ["Day by Day", "The OGs", "Requests", "Making of", "Ledger"][i]
        d.text((x + 70 - tw(d, lab, font("Regular", 20)) / 2, 348), lab, font=font("Regular", 20), fill=(60, 60, 60))
    y0 = ph + 20
    posts = [Image.open(os.path.join(OUT, "post1_1080x1350.png")), "d2", "d1"]   # ordine griglia: piu' recente in alto a sinistra
    frames = []
    for n in (2, 1):
        fp = os.path.join(HERE, "..", "out", f"day{n}_frame.png")
        frames.append(Image.open(fp).convert("RGB") if os.path.exists(fp) else None)
    tiles = [("DAY 2", "2 buildings", frames[0]), ("DAY 1", "1 building", frames[1]), (None, None, posts[0])]
    for i, (a, b, src) in enumerate(tiles):
        cx = (i % 3) * (cw + g); cy = y0 + (i // 3) * (ch + g)
        t = src.convert("RGB")
        sc = max(cw / t.width, ch / t.height); t = t.resize((int(t.width * sc) + 1, int(t.height * sc) + 1), Image.LANCZOS)
        l = (t.width - cw) // 2; tp = (t.height - ch) // 2
        im.paste(t.crop((l, tp, l + cw, tp + ch)), (cx, cy))
        if a:
            f = font("Bold", 44); fs = font("SemiBold", 26)
            d.rounded_rectangle((cx + 40, cy + ch - 150, cx + cw - 40, cy + ch - 40), 20, fill=(255, 250, 243))
            d.text((cx + cw / 2 - tw(d, a, f) / 2, cy + ch - 142), a, font=f, fill=INK)
            d.text((cx + cw / 2 - tw(d, b, fs) / 2, cy + ch - 84), b, font=fs, fill=(150, 90, 60))
    im.crop((0, 0, W, y0 + ch + 20)).save(os.path.join(OUT, "mockup_griglia.png"))

{"post": post, "stories": stories, "grid": grid}[sys.argv[1]]()
