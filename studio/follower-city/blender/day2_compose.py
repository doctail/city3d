"""Montaggio Day 2 REALE: frame unici (day2_final_frames) -> hold/blend, titolo, schede commento Instagram (PIL, commenti pubblici reali),
scheda profilo con contatore 1 -> 5 (avatar = palazzo hero), CTA follow/commento, obiettivo 25 follower, zoom senza upscale, ffmpeg."""
import os, sys, math, subprocess, random
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "test")); sys.path.insert(0, HERE)
import timeline_day2_final as T
import anim_day2_final as R
RAW = os.path.join(HERE, "day2_final_frames")
FINAL = os.path.join(HERE, "day2_final_out")
OUT = os.path.join(HERE, "..", "test", "cozy_day2_silent.mp4")
AV_SRC = os.path.join(HERE, "day1_final_frames", "0225.png")     # palazzo hero (Day 1) -> avatar del profilo
W, H, FPS = 1080, 1920, T.FPS
NTOT = int(T.DUR * FPS)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
if not os.path.exists(FX): FX = FB
INK, CREAM, TERRA, SAGE = (62, 38, 22), (255, 246, 228), (196, 88, 58), (104, 150, 102)
LINK = (60, 84, 190)
STK = (70, 40, 20)
_fc = {}
def font(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def spring(u):
    return 0.0 if u <= 0 else 1.0 - math.exp(-7.0 * u) * (math.cos(9.0 * u) + 0.78 * math.sin(9.0 * u))

# ---------------- scena: hold / blend dei frame unici
REND = R.unique_frames()
_cache = {}
def load(n):
    if n not in _cache:
        if len(_cache) > 12: _cache.clear()
        _cache[n] = Image.open(os.path.join(RAW, f"{n:04d}.png")).convert("RGB")
    return _cache[n]
def scene(n):
    n = min(n, REND[-1])
    p = max(x for x in REND if x <= n); q = min(x for x in REND if x >= n)
    if p == q: return load(p)
    if q - p > 3: return load(p)                       # fuori dalle finestre dei pop la scena e' ferma
    return Image.blend(load(p), load(q), (n - p) / (q - p))
def zoomed(im, t):
    e = sstep(T.T_PUSH0, T.DUR, t); e = e * e * (3 - 2 * e)
    z = 1.0 + 0.10 * e
    rw, rh = im.size; cw, ch = rw / z, rh / z
    x0 = (rw - cw) / 2; y0 = (rh - ch) * 0.5
    return im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

# ---------------- testo
def txt(d, cx, y, s, f, fill, a=255, stroke=True, shadow=True, sw=5):
    w = d.textlength(s, font=f); x = cx - w / 2
    if shadow: d.text((x + 3, y + 6), s, font=f, fill=(40, 22, 10, int(a * .45)), stroke_width=sw, stroke_fill=(40, 22, 10, int(a * .45)))
    d.text((x, y), s, font=f, fill=(*fill, a), stroke_width=sw if stroke else 0, stroke_fill=(*STK, a))
def fit(path, s, maxw, top=200):
    sz = top
    while sz > 40 and ImageFont.truetype(path, sz).getlength(s) > maxw: sz -= 4
    return font(path, sz)
def wrap(d, s, f, maxw):
    out, cur = [], ""
    for w_ in s.split(" "):
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w_
    out.append(cur); return out

# ---------------- avatar hero
_av = {}
def avatar(sz):
    if sz not in _av:
        src = Image.open(AV_SRC).convert("RGB").crop((0, 540, 980, 1520)).resize((sz, sz), Image.LANCZOS)
        m = Image.new("L", (sz * 3, sz * 3), 0); ImageDraw.Draw(m).ellipse((0, 0, sz * 3 - 1, sz * 3 - 1), fill=255); m = m.resize((sz, sz), Image.LANCZOS)
        _av[sz] = (src, m)
    return _av[sz]

# ---------------- schede commento Instagram (dark, PIL)
CARD_BG, CARD_TX, CARD_GR = (28, 29, 34), (245, 245, 247), (150, 152, 160)
def heart(d, cx, cy, r, fill):
    d.ellipse((cx - r, cy - r, cx, cy), fill=fill); d.ellipse((cx, cy - r, cx + r, cy), fill=fill)
    d.polygon([(cx - r, cy - r * 0.35), (cx + r, cy - r * 0.35), (cx, cy + r * 1.05)], fill=fill)
def house_icon(d, x, y, s, a):
    d.polygon([(x, y + s * .45), (x + s * .5, y), (x + s, y + s * .45)], fill=(214, 90, 60, a))
    d.rectangle((x + s * .12, y + s * .45, x + s * .88, y + s), fill=(240, 200, 120, a))
    d.rectangle((x + s * .42, y + s * .62, x + s * .6, y + s), fill=(150, 90, 60, a))
AVC = {"m.bardi56": (214, 168, 120), "lillyflxwer": (120, 86, 70), "novasalot": (150, 90, 160), "juilbilswirl": (96, 120, 90), "ledgerofcities": None}
def card_img(user, when, text, likes, reply=False, width=920, tsize=46):
    """scheda commento in stile Instagram (dark); ritorna RGBA."""
    tmp = Image.new("RGBA", (10, 10)); d0 = ImageDraw.Draw(tmp)
    ft = font(FR, tsize); fu = font(FB, tsize - 4); fs = font(FR, tsize - 12)
    lines = wrap(d0, text, ft, width - 250)
    lh = int(tsize * 1.28)
    h = 40 + (tsize + 10) + len(lines) * lh + 20 + (tsize - 8) + 34
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, width - 1, h - 1), radius=44, fill=CARD_BG + (255,))
    ar = 62 if not reply else 56
    cx0, cy0 = 34, 34
    if user == "ledgerofcities":
        src, m = avatar(ar * 2); src = src.resize((ar * 2, ar * 2)); im.paste(src, (cx0, cy0), m)
    else:
        d.ellipse((cx0, cy0, cx0 + ar * 2, cy0 + ar * 2), fill=AVC.get(user, (120, 120, 120)) + (255,))
        d.text((cx0 + ar - d.textlength(user[0].upper(), font=font(FX, 56)) / 2, cy0 + ar - 38), user[0].upper(), font=font(FX, 56), fill=(255, 255, 255, 255))
    x = cx0 + ar * 2 + 26
    d.text((x, 30), user, font=fu, fill=CARD_TX + (255,))
    d.text((x + d.textlength(user, font=fu) + 18, 36), when, font=fs, fill=CARD_GR + (255,))
    y = 30 + tsize + 14
    for i, ln in enumerate(lines):
        if reply and i == 0 and ln.startswith("@"):
            nm, rest = ln.split(" ", 1)
            d.text((x, y), nm, font=ft, fill=(120, 168, 255, 255)); d.text((x + d.textlength(nm + " ", font=ft), y), rest, font=ft, fill=CARD_TX + (255,))
        else:
            d.text((x, y), ln, font=ft, fill=CARD_TX + (255,))
        y += lh
    if reply: house_icon(d, x + d.textlength(lines[-1] + " ", font=ft), y - lh + 6, 40, 255)
    d.text((x, y + 8), "Reply", font=fs, fill=CARD_GR + (255,))
    heart(d, width - 62, h // 2 - 8, 26, (255, 48, 64, 255) if likes else (200, 200, 205, 255))
    if likes: d.text((width - 62 - d.textlength(str(likes), font=fs) / 2, h // 2 + 30), str(likes), font=fs, fill=CARD_GR + (255,))
    return im

_ci = {}
def cardc(key, *a, **k):
    if key not in _ci: _ci[key] = card_img(*a, **k)
    return _ci[key]
LILLY_TXT = "can i get a house with white fence and a glass house mansion kinda thing?  i have a boxer and she had 3 puppies!!! can i also get a playboy flag on the front porch?— OG"
def paste_card(lay, im, cx, cy, sc=1.0, a=255):
    if a <= 0: return
    if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 255:
        al = im.getchannel("A").point(lambda v: v * a // 255); im = im.copy(); im.putalpha(al)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v * 70 // 255))
    lay.alpha_composite(sh, (int(cx - im.width / 2 + 6), int(cy - im.height / 2 + 14)))
    lay.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def star(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r * .22, cy - r * .22), (cx + r, cy), (cx + r * .22, cy + r * .22), (cx, cy + r), (cx - r * .22, cy + r * .22), (cx - r, cy), (cx - r * .22, cy - r * .22)], fill=fill)
def sparkles(d, cx, cy, rx, ry, t, t0, dur, seed):
    k = t - t0
    if k < 0 or k > dur: return
    rg = random.Random(seed)
    for i in range(14):
        ang = rg.uniform(0, 6.283); rad = rg.uniform(1.0, 1.18); ph = rg.uniform(0, 0.5); sz = rg.uniform(16, 40)
        kk = (k - ph * dur) / (dur * 0.5)
        if kk < 0 or kk > 1: continue
        a = int(255 * math.sin(math.pi * kk)); r = sz * math.sin(math.pi * kk)
        star(d, cx + rad * math.cos(ang) * rx, cy + rad * math.sin(ang) * ry, r, (255, 236, 160, a))

# ---------------- testo + schede sulla scena
def scene_text(im, t):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f1 = font(FX, 118)
    if T.T_HOOK <= t < 2.7:
        a = int(255 * sstep(T.T_HOOK, T.T_HOOK + 0.25, t) * (1 - sstep(2.45, 2.7, t))); dy = (1 - sstep(T.T_HOOK, T.T_HOOK + 0.3, t)) * 24
        txt(d, W / 2, 250 + dy, "4 new followers", fit(FX, "4 new followers", 960, 106), CREAM, a)
        txt(d, W / 2, 365 + dy, "= 4 new buildings", fit(FX, "= 4 new buildings", 960, 106), CREAM, a)
    if 2.75 <= t < T.T_CARD0:
        a = int(255 * sstep(2.75, 3.0, t) * (1 - sstep(8.3, 8.55, t)))
        txt(d, W / 2, 255, "You asked,", font(FX, 112), CREAM, a); txt(d, W / 2, 380, "we built it", font(FX, 112), CREAM, a)
    # scheda @m.bardi56 (OG ticket)
    if T.T_OGCARD0 <= t < T.T_OGCARD1 + 0.5:
        k = t - T.T_OGCARD0; p = min(1.0, spring(k * 1.3)); out = sstep(T.T_OGCARD1, T.T_OGCARD1 + 0.4, t)
        im_ = cardc("og", "m.bardi56", "2h", "OG and followed so deliver now !", 2)
        paste_card(lay, im_, W / 2, 1560 + (1 - p) * 420 + out * 420, 1.0, int(255 * sstep(0, 0.15, k)))
        sparkles(d, W / 2, 1560, 470, im_.height * 0.6, t, T.POP[2] - 0.1, 1.1, 5)
    # scheda @lillyflxwer: entra, si ingrandisce al centro, poi si sposta in basso (ridotta) e il suo edificio appare
    if T.T_LILLY0 <= t < T.T_LILLY1 + 0.5:
        im_ = cardc("lilly", "lillyflxwer", "3h", LILLY_TXT, 1)
        if t < T.T_LILLY_BIG:
            k = (t - T.T_LILLY0) / (T.T_LILLY_BIG - T.T_LILLY0); e = sstep(0, 1, k)
            cy, sc, cx = 1750 + (1020 - 1750) * e, 0.85 + 0.15 * e, W / 2
        elif t < T.T_LILLY_SMALL:
            cy, sc, cx = 1020, 1.0, W / 2
        else:
            e = sstep(T.T_LILLY_SMALL, T.T_LILLY_SMALL + 0.55, t); cy, sc, cx = 1020 + (1478 - 1020) * e, 1.0 + (0.50 - 1.0) * e, W / 2 + (760 - W / 2) * e
        out = sstep(T.T_LILLY1, T.T_LILLY1 + 0.4, t); cy += out * 420
        paste_card(lay, im_, cx, cy, sc, int(255 * sstep(T.T_LILLY0, T.T_LILLY0 + 0.15, t)))
        sparkles(d, cx, cy, 470 * sc, im_.height * 0.55 * sc, t, T.T_LILLY_SMALL - 0.1, 1.3, 9)
        if t >= T.T_REPLY:
            k = t - T.T_REPLY; p = min(1.0, spring(k * 1.4))
            rp = cardc("reply", "ledgerofcities", "2h · Author", "@lillyflxwer Let's see what we can do for you!", 0, reply=True, width=840, tsize=40)
            paste_card(lay, rp, 760, 1478 + im_.height * 0.50 / 2 + rp.height * 0.6 / 2 + 12 + (1 - p) * 120 + out * 420, 0.6, int(255 * sstep(0, 0.15, k)))
    # CTA commento: 'Comment OG' + schede OG reali
    if T.T_COMMENT0 <= t < T.T_COMMENT1:
        a = int(255 * sstep(T.T_COMMENT0, T.T_COMMENT0 + 0.3, t))
        txt(d, W / 2, 255, "Comment OG", fit(FX, "Comment OG", 940, 150), CREAM, a)
        txt(d, W / 2, 415, "to claim your OG ticket", fit(FB, "to claim your OG ticket", 940, 90), CREAM, a)
        for (nm, y, k0, key) in (("novasalot", 1450, T.T_COMMENT0 + 0.6, "c1"), ("juilbilswirl", 1160, T.T_COMMENT0 + 1.3, "c2")):
            k = t - k0
            if k > 0:
                p = min(1.0, spring(k * 1.3)); im_ = cardc(key, nm, "now", "OG", 1 if key == "c1" else 0, width=860, tsize=48)
                paste_card(lay, im_, W / 2, y + (1 - p) * 300, 1.0, int(255 * sstep(0, 0.15, k)))
    if T.T_FOLLOW <= t < T.T_GOAL:
        a = int(255 * sstep(T.T_FOLLOW, T.T_FOLLOW + 0.3, t))
        txt(d, W / 2, 255, "Follow to become", fit(FX, "Follow to become", 940, 120), CREAM, a)
        txt(d, W / 2, 395, "a building", font(FX, 130), CREAM, a)
        k = max(0.0, t - T.T_FOLLOW - 0.4); pp = 1 + 0.06 * math.sin(k * 9) * math.exp(-k * 2)
        bw, bh = 520 * pp, 130 * pp
        BY = 1560
        d.rounded_rectangle((W / 2 - bw / 2 + 4, BY + 10, W / 2 + bw / 2 + 4, BY + bh + 10), radius=40, fill=(40, 22, 10, int(a * .3)))
        d.rounded_rectangle((W / 2 - bw / 2, BY, W / 2 + bw / 2, BY + bh), radius=40, fill=(*SAGE, a))
        fb_ = font(FB, 64); w_ = d.textlength("Follow", font=fb_)
        d.text((W / 2 - w_ / 2, BY + bh / 2 - 40), "Follow", font=fb_, fill=(255, 255, 255, a))
    if t >= T.T_GOAL:
        a = int(255 * sstep(T.T_GOAL, T.T_GOAL + 0.3, t))
        txt(d, W / 2, 230, "Day 2", font(FX, 140), CREAM, a, sw=8)
        a2 = int(255 * sstep(T.T_GOAL + 0.4, T.T_GOAL + 0.7, t))
        txt(d, W / 2, 395, "Can we reach 25", fit(FB, "Can we reach 25", 940, 80), CREAM, a2)
        txt(d, W / 2, 485, "followers for Day 3?", fit(FB, "followers for Day 3?", 940, 80), CREAM, a2)
        a3 = int(255 * sstep(T.T_GOAL + 1.0, T.T_GOAL + 1.3, t))
        txt(d, W / 2, 1640, "See you tomorrow!", font(FB, 92), CREAM, a3)
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")

# ---------------- scheda profilo: 1 -> 5
def card(t):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    sz = 300; ax, ay = 90, 380
    src, m = avatar(sz)
    d.ellipse((ax - 6, ay - 6, ax + sz + 6, ay + sz + 6), fill=(214, 226, 200))
    im.paste(src, (ax, ay), m)
    d.text((ax + sz + 50, ay + 20), "ledgerofcities", font=font(FX, 62), fill=INK)
    d.text((ax + sz + 50, ay + 105), "Ledger of Cities", font=font(FR, 44), fill=INK)
    ticks = [x for x in T.T_TICK if t >= x]
    cnt = 1 + len(ticks)
    sx = ax + sz + 50; sy = ay + 200; x = sx
    for v, lab in (("2", "posts"), (str(cnt), "followers"), ("0", "following")):
        d.text((x, sy), v, font=font(FB, 40), fill=TERRA if lab == "followers" else INK)
        wv = d.textlength(v, font=font(FB, 40)); d.text((x + wv + 8, sy), lab, font=font(FR, 34), fill=INK)
        x += wv + d.textlength(lab, font=font(FR, 34)) + 48
    by = ay + sz + 70
    for i, ln in enumerate(["1 follower = 1 building", "A cozy city that grows with you.", "Made with Blender · No AI", "Urban history on YouTube"]):
        d.text((ax, by + i * 62), ln, font=font(FR, 46), fill=INK)
    d.text((ax, by + 4 * 62 + 4), "www.youtube.com/@ledgerofcities", font=font(FB, 40), fill=LINK)
    d.rounded_rectangle((ax, by + 330, W - ax, by + 330 + 118), radius=32, fill=SAGE)
    txt(d, W / 2, by + 330 + 30, "Follow", font(FB, 54), (255, 255, 255), shadow=False, stroke=False)
    cy = by + 560
    last = max(ticks) if ticks else None
    k = (t - last) if last else 99.0
    sc = 1.0 + 0.45 * math.exp(-k * 7) * math.sin(min(k, 0.45) * 14) if k < 0.6 else 1.0
    big = font(FX, int(300 * sc)); col = TERRA
    s = str(cnt); w = d.textlength(s, font=big); d.text(((W - w) / 2, cy - (big.size - 300) / 2), s, font=big, fill=col)
    d.text(((W - d.textlength("followers", font=font(FB, 64))) / 2, cy + 330), "followers", font=font(FB, 64), fill=INK)
    # tick verde (pop ad ogni +1)
    if last and k < 0.9:
        p = min(1.0, spring(k * 3.0)); r = 52 * p; ccx, ccy = W / 2 + 230, cy + 120
        d.ellipse((ccx - r, ccy - r, ccx + r, ccy + r), fill=SAGE)
        d.line([(ccx - r * .45, ccy), (ccx - r * .1, ccy + r * .38), (ccx + r * .5, ccy - r * .35)], fill=(255, 255, 255), width=max(2, int(r * .22)))
    if t >= T.T_CHIME:
        a = sstep(T.T_CHIME, T.T_CHIME + 0.3, t)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        s2 = "= 5 buildings"
        dl.text(((W - dl.textlength(s2, font=font(FX, 92))) / 2, cy + 430 + (1 - a) * 20), s2, font=font(FX, 92), fill=(*TERRA, int(255 * a)))
        im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    return im

def frame(n):
    t = n / FPS
    if T.T_CARD0 <= t < T.T_CARD1:
        return card(t)
    return scene_text(zoomed(scene(min(n, R.SCENE_END_F)), t), t)

def assemble(only=None):
    os.makedirs(FINAL, exist_ok=True)
    for n in (only if only is not None else range(NTOT)):
        frame(n).save(os.path.join(FINAL, f"{n:04d}.png"))
    if only is None:
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FINAL, "%04d.png"),
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", "-an", OUT])
        print("[day2c] mp4 muto:", OUT, os.path.getsize(OUT), "byte")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "frames":
        assemble([int(x) for x in a[1:]])
    else:
        assemble()
