"""Montaggio Day 1 finale: scelta frame unici + blend finestre, zoom (push-in senza upscale), titolo, scheda profilo (PIL), ffmpeg."""
import os, sys, math, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "test"))
import timeline_day1 as T
RAW = os.path.join(HERE, "day1_final_frames")
FINAL = os.path.join(HERE, "day1_final_out")
OUT = os.path.join(HERE, "..", "test", "cozy_day1_silent.mp4")
W, H, FPS = 1080, 1920, T.FPS
NTOT = int(T.DUR * FPS)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
if not os.path.exists(FX): FX = FB
INK, CREAM, TERRA, SAGE = (62, 38, 22), (255, 246, 228), (196, 88, 58), (104, 150, 102)
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]
def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def spring(u):
    return 0.0 if u <= 0 else 1.0 - math.exp(-7.0 * u) * (math.cos(9.0 * u) + 0.78 * math.sin(9.0 * u))

def load(n):
    return Image.open(os.path.join(RAW, f"{n:04d}.png")).convert("RGB")
G0, G1, C0 = int(T.T_GLOW0 * FPS), int(T.T_GLOW1 * FPS), int(T.T_CARD0 * FPS)
def scene(n):
    if n < int(T.T_POP * FPS): return load(0)
    if n < C0: return load(n)
    if n < G0: return load(G0)
    if n >= G1: return load(G1)
    if (n - G0) % 2 == 0: return load(n)
    return Image.blend(load(n - 1), load(n + 1), 0.5)

def zoomed(im, t):
    e = sstep(T.T_PUSH0, T.DUR, t); e = e * e * (3 - 2 * e)
    z = 1.0 + 0.10 * e
    rw, rh = im.size
    cw, ch = rw / z, rh / z
    # a z=1 tutto il frame (1188x2112) ridotto a 1080x1920; a z=1.1 crop 1080x1920 nativo; lieve ancoraggio verso il basso (il palazzo)
    x0 = (rw - cw) / 2; y0 = (rh - ch) * 0.5
    return im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

def txt(d, cx, y, s, font_, fill, a=255, stroke=None, shadow=True, sw=7):
    w = d.textlength(s, font=font_); x = cx - w / 2
    if shadow: d.text((x + 3, y + 6), s, font=font_, fill=(40, 22, 10, int(a * .45)), stroke_width=sw, stroke_fill=(40, 22, 10, int(a * .45)))
    d.text((x, y), s, font=font_, fill=(*fill, a), stroke_width=sw if stroke else 0, stroke_fill=(*(stroke or (0, 0, 0)), a))

def scene_text(im, t):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f1 = font(FX, 118)
    if T.T_HOOK <= t < T.T_CARD0:                 # titolo hook (zona sicura alta: sotto i 250 px)
        a = int(255 * sstep(T.T_HOOK, T.T_HOOK + 0.25, t)); dy = (1 - sstep(T.T_HOOK, T.T_HOOK + 0.3, t)) * 24
        txt(d, W / 2, 300 + dy, "1 follower", f1, CREAM, a, stroke=(70, 40, 20))
        txt(d, W / 2, 440 + dy, "= 1 building", f1, CREAM, a, stroke=(70, 40, 20))
    if t >= T.T_END:
        a = int(255 * sstep(T.T_END, T.T_END + 0.3, t))
        txt(d, W / 2, 300, "Day 1", font(FX, 190), CREAM, a, stroke=(70, 40, 20), sw=9)
        a2 = int(255 * sstep(T.T_END + 0.4, T.T_END + 0.7, t))
        txt(d, W / 2, 540, "See you tomorrow!", font(FB, 92), CREAM, a2, stroke=(70, 40, 20))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")

_av = None
def avatar(sz):
    global _av
    src = Image.open(os.path.join(HERE, "..", "test", "assets", "avatar_400.png")).convert("RGB").resize((sz, sz), Image.LANCZOS)
    m = Image.new("L", (sz * 3, sz * 3), 0); ImageDraw.Draw(m).ellipse((0, 0, sz * 3 - 1, sz * 3 - 1), fill=255); m = m.resize((sz, sz), Image.LANCZOS)
    return src, m

def card(t):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    tt = t - T.T_CARD0
    # lieve sliding-in del contenuto (primi 0.25 s)
    # avatar + nome
    sz = 300; ax, ay = 90, 470
    src, m = avatar(sz)
    d.ellipse((ax - 6, ay - 6, ax + sz + 6, ay + sz + 6), fill=(214, 226, 200))
    im.paste(src, (ax, ay), m)
    d.text((ax + sz + 50, ay + 20), "ledgerofcities", font=font(FX, 62), fill=INK)
    d.text((ax + sz + 50, ay + 105), "Ledger of Cities", font=font(FR, 44), fill=INK)
    # contatori
    cnt = 1 if t >= T.T_COUNT else 0
    sx = ax + sz + 50; sy = ay + 200
    for lab, v, bold in (("Posts", "1", False), ("followers", str(cnt), True), ("following", "0", False)):
        pass
    x = sx
    for v, lab in (("1", "posts"), (str(cnt), "followers"), ("0", "following")):
        d.text((x, sy), v, font=font(FB, 40), fill=TERRA if (lab == "followers" and cnt) else INK)
        wv = d.textlength(v, font=font(FB, 40))
        d.text((x + wv + 8, sy), lab, font=font(FR, 34), fill=INK)
        x += wv + d.textlength(lab, font=font(FR, 34)) + 40 + 8
    # bio
    by = ay + sz + 70
    for i, ln in enumerate(["1 follower = 1 building", "A cozy city that grows with you.", "Made with Blender · No AI", "Urban history on YouTube"]):
        d.text((ax, by + i * 62), ln, font=font(FR, 46), fill=INK)
    # bottone
    d.rounded_rectangle((ax, by + 300, W - ax, by + 300 + 118), radius=32, fill=SAGE)
    txt(d, W / 2, by + 300 + 30, "Follow", font(FB, 54), (255, 255, 255), shadow=False)
    # contatore grande: 0 -> 1 con pop, poi '= 1 building'
    cy = by + 520
    k = max(0.0, t - T.T_COUNT)
    sc = 1.0 + 0.55 * math.exp(-k * 6) * math.sin(min(k, 1) * 14) * (1 if k < 0.6 else 0) if k > 0 else 1.0
    big = font(FX, int(300 * sc))
    col = TERRA if cnt else (170, 150, 130)
    s = str(cnt); w = d.textlength(s, font=big); d.text(((W - w) / 2, cy - (big.size - 300) / 2), s, font=big, fill=col)
    d.text(((W - d.textlength("follower", font=font(FB, 64))) / 2, cy + 330), "follower", font=font(FB, 64), fill=INK)
    if t >= T.T_CHIME:
        a = sstep(T.T_CHIME, T.T_CHIME + 0.3, t)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.text(((W - dl.textlength("= 1 building", font=font(FX, 92))) / 2, cy + 430 + (1 - a) * 20), "= 1 building", font=font(FX, 92), fill=(*TERRA, int(255 * a)))
        im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    return im

def frame(n):
    t = n / FPS
    if T.T_CARD0 <= t < T.T_CARD1:
        return card(t)
    return scene_text(zoomed(scene(n), t), t)

def assemble(only=None):
    os.makedirs(FINAL, exist_ok=True)
    for n in (only if only is not None else range(NTOT)):
        frame(n).save(os.path.join(FINAL, f"{n:04d}.png"))
    if only is None:
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FINAL, "%04d.png"),
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", "-an", OUT])
        print("[day1f] mp4 muto:", OUT, os.path.getsize(OUT), "byte")
