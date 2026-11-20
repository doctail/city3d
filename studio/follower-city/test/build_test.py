"""Reel di TEST Follower City: 1080x1920, 30 fps, ~29,5 s.
Clip sorgente: blender/day1_frames (120 fotogrammi 270x480, 24 fps, senza testo), upscale lanczos x4.
Uso: python3 build_test.py <out.mp4> [workdir]"""
import sys, os, subprocess, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timeline import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'cozy_test_full.mp4')
WORK = sys.argv[2] if len(sys.argv) > 2 else '/tmp'
FR = os.path.join(HERE, '..', 'blender', 'day1_frames')
FD = '/usr/share/fonts/opentype/inter/'
W, H = 1080, 1920
BROWN = (58, 35, 18); ORANGE = (232, 135, 30); ACCENT_ON_WHITE = (217, 115, 26); BLUE = (29, 120, 220)

frames = [Image.open(os.path.join(FR, f'{i:04d}.png')).convert('RGB') for i in range(120)]
SRC_FPS = 24; LAST = 119 / SRC_FPS
avatar = Image.open(os.path.join(HERE, 'assets', 'avatar_400.png')).convert('RGB')

def font(name, size): return ImageFont.truetype(FD + name, int(round(size)))
_fc = {}
def F(name, size):
    k = (name, int(round(size)))
    if k not in _fc: _fc[k] = font(name, size)
    return _fc[k]

def ease_out_back(u, s=1.9):
    u = min(max(u, 0), 1); return 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2
def smooth(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)

# ---------- scena ----------
def src_frame(ts):
    ts = min(max(ts, 0), LAST); x = ts * SRC_FPS; i = int(x); j = min(i + 1, 119); a = x - i
    return frames[i] if a < 1e-3 else Image.blend(frames[i], frames[j], a)

def zoom_up(img, z, cx=0.5, cy=0.5):
    w, h = 270 / z, 480 / z
    x0 = min(max(cx * 270 - w / 2, 0), 270 - w); y0 = min(max(cy * 480 - h / 2, 0), 480 - h)
    out = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
    return out.filter(ImageFilter.UnsharpMask(radius=2.0, percent=55, threshold=2))

def scene_params(t):
    """(tempo sorgente, zoom, cx, cy) oppure None se la scena e' coperta dalla scheda profilo."""
    if t < T_CARD:
        ts = 0.0 if t < CLIP_OFFSET else t - CLIP_OFFSET
        return ts, 1.0 + 0.08 * smooth(t / T_CARD), 0.5, 0.5
    if t < T_SCENE2: return None
    if t < T_REPLAY:
        u = (t - T_SCENE2) / (T_REPLAY - T_SCENE2)
        return 2.77 + u * (4.96 - 2.77), 1.08 + 0.14 * u, 0.5, 0.5
    if t < T_COMMENT:
        ts = REPLAY_SRC0 + (t - T_REPLAY) * REPLAY_RATE
        u = (t - T_REPLAY) / (T_COMMENT - T_REPLAY)
        return min(ts, 3.0), 1.35, 0.5, 0.46 + 0.04 * u
    if t < T_LABEL:
        u = (t - T_COMMENT) / (T_LABEL - T_COMMENT)
        return min(3.0 + u * 1.96, 4.96), 1.35 - 0.10 * u, 0.5, 0.5
    u = (t - T_LABEL) / (DUR - T_LABEL)
    return 4.96, 1.25 + 0.20 * smooth(u), 0.5, 0.5 + 0.02 * math.sin(u * 3)

# ---------- testo ----------
_tl = {}
def text_layer(text, fname, size, fill=(255, 255, 255), stroke=0, stroke_fill=BROWN, shadow=True):
    key = (text, fname, size, fill, stroke, stroke_fill, shadow)
    if key in _tl: return _tl[key]
    f = F(fname, size); pad = stroke + 40
    d0 = ImageDraw.Draw(Image.new('L', (4, 4)))
    l, t, r, b = d0.textbbox((0, 0), text, font=f, stroke_width=stroke)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l, pad - t + 10), text, font=f, fill=(20, 10, 0, 170), stroke_width=stroke, stroke_fill=(20, 10, 0, 170))
        lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(9)))
    ImageDraw.Draw(lay).text((pad - l, pad - t), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
    _tl[key] = lay
    return lay

def put(img, lay, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.003 or scale <= 0.01: return
    if abs(scale - 1) > 1e-3: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BILINEAR)
    a = lay.getchannel('A')
    if alpha < 1: a = a.point(lambda v: int(v * alpha))
    img.paste(lay.convert('RGB'), (int(cx - lay.width / 2), int(cy - lay.height / 2)), a)

def pop_in(t, t0, dur=0.38): u = (t - t0) / dur; return (ease_out_back(u) if u > 0 else 0, min(1, max(0, u * 5)))

def title(img, t, lines, t0, t1, cy, size, fname='Inter-ExtraBold.otf', gap=1.12, colors=None, fade_out=0.15):
    if not (t0 <= t < t1): return
    sc, al = pop_in(t, t0)
    if t > t1 - fade_out: al *= (t1 - t) / fade_out
    n = len(lines); y = cy - (n - 1) * size * gap / 2
    for k, ln in enumerate(lines):
        s = size if not isinstance(ln, tuple) else ln[1]
        txt = ln if not isinstance(ln, tuple) else ln[0]
        col = (255, 255, 255) if not colors else colors[k]
        put(img, text_layer(txt, fname, s, col, stroke=max(8, int(s * 0.1))), W / 2, y + k * size * gap, sc, al)

# ---------- scheda profilo ----------
def rr(d, box, r, fill, outline=None, width=1): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def count_at(t):
    n = sum(1 for x in TICK_TIMES if t >= x); return n
def last_tick(t):
    ts = [x for x in TICK_TIMES if t >= x]; return ts[-1] if ts else -9

def profile_card(t):
    img = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    n = count_at(t)
    ph_a = t < 4.55
    if ph_a:   # mock profilo con zoom sul numero follower
        u = smooth((t - T_CARD) / 1.0)
        k = 1.0 + 1.9 * u; cx, cy = 700, 300
        def P(x, y): return ((x - cx) * k + W / 2 + (540 - cx) * 0, (y - cy) * k + 300 + 80 * (1 - u) * 0 + (960 - 300) * u)
        def S(v): return v * k
        px, py = P(60, 100); d.text((px, py), 'ledgerofcities', font=F('Inter-Bold.otf', S(48)), fill=(20, 20, 20))
        ax, ay = P(60, 220); a2 = avatar.resize((int(S(220)), int(S(220))), Image.LANCZOS)
        m = Image.new('L', a2.size, 0); ImageDraw.Draw(m).ellipse((0, 0, a2.size[0] - 1, a2.size[1] - 1), fill=255); img.paste(a2, (int(ax), int(ay)), m)
        for x, num, lab in [(520, '1', 'posts'), (700, str(n), 'followers'), (900, '0', 'following')]:
            X, Y = P(x, 285); d.text((X, Y), num, font=F('Inter-Bold.otf', S(58)), fill=(20, 20, 20), anchor='mm')
            X, Y = P(x, 345); d.text((X, Y), lab, font=F('Inter-Regular.otf', S(32)), fill=(60, 60, 60), anchor='mm')
        X, Y = P(60, 470); d.text((X, Y), 'Ledger of Cities', font=F('Inter-Bold.otf', S(38)), fill=(20, 20, 20))
        X, Y = P(60, 525); d.text((X, Y), '1 follower = 1 building', font=F('Inter-Regular.otf', S(36)), fill=(30, 30, 30))
        X, Y = P(60, 575); d.text((X, Y), 'Follow to become a building', font=F('Inter-Regular.otf', S(36)), fill=(30, 30, 30))
        for bx, lab in [(60, 'Edit profile'), (520, 'Share profile')]:
            x0, y0 = P(bx, 650); x1, y1 = P(bx + 420, 730); rr(d, (x0, y0, x1, y1), S(16), (239, 239, 239))
            d.text(((x0 + x1) / 2, (y0 + y1) / 2), lab, font=F('Inter-SemiBold.otf', S(34)), fill=(20, 20, 20), anchor='mm')
        if t > 4.2:   # dissolvenza verso il layout grande
            big = profile_big(t); img = Image.blend(img, big, smooth((t - 4.2) / 0.35))
    else:
        img = profile_big(t)
    return img

def profile_big(t):
    img = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    d.text((W / 2, 470), 'Ledger of Cities', font=F('Inter-SemiBold.otf', 78), fill=(20, 20, 20), anchor='mm')
    n = count_at(t); lt = last_tick(t)
    bump = 1 + 0.10 * max(0, 1 - (t - lt) / 0.10) if lt > 0 else 1
    num = F('Inter-ExtraBold.otf', 340 * bump)
    d.text((W / 2, 790), str(n), font=num, fill=(10, 10, 10), anchor='mm')
    nb = d.textbbox((W / 2, 790), str(n), font=num, anchor='mm')
    if t >= T_COUNT0:
        sc, al = pop_in(t, T_COUNT0, 0.3)
        txt = f'+{COUNT_TO}'; f = F('Inter-Bold.otf', 86 * max(sc, 0.1)); c = tuple(int(255 - (255 - v) * min(al, 1)) for v in BLUE)
        d.text((nb[2] + 30, nb[1] + 90), txt, font=f, fill=c, anchor='lm')
    d.text((W / 2, 1010), 'followers', font=F('Inter-Regular.otf', 92), fill=(40, 40, 40), anchor='mm')
    if t >= T_CHIME:
        sc, al = pop_in(t, T_CHIME, 0.4)
        c = tuple(int(255 - (255 - v) * min(al, 1)) for v in ACCENT_ON_WHITE)
        d.text((W / 2, 1100), '=', font=F('Inter-Bold.otf', 70 * max(sc, .1)), fill=c, anchor='mm')
        d.text((W / 2, 1200), f'{COUNT_TO} buildings', font=F('Inter-ExtraBold.otf', 104 * max(sc, .1)), fill=c, anchor='mm')
    sc, al = pop_in(t, T_CARD + 1.4, 0.4)
    d.text((W / 2, 1500), 'Day 1', font=F('Inter-ExtraBold.otf', 130 * max(sc, .1)), fill=tuple(int(255 - 255 * min(al, 1) + 10) for _ in range(3)), anchor='mm')
    return img

# ---------- commento (PLACEHOLDER) ----------
def sparkles(img, t, cx, cy, t0, dur=0.9, n=12, spread=330, seed=1):
    if not (t0 <= t < t0 + dur): return
    r = random.Random(seed); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(n):
        ox, oy = r.uniform(-spread, spread), r.uniform(-spread * .8, spread * .8); ph = r.uniform(0, 0.45); sz = r.uniform(26, 62)
        u = (t - t0 - ph) / (dur - 0.45)
        if not (0 < u < 1): continue
        s = sz * math.sin(math.pi * u); x, y = cx + ox, cy + oy - 40 * u
        d.polygon([(x, y - s), (x + s * .22, y - s * .22), (x + s, y), (x + s * .22, y + s * .22), (x, y + s), (x - s * .22, y + s * .22), (x - s, y), (x - s * .22, y - s * .22)], fill=(255, 244, 200, 235))
    img.paste(lay.convert('RGB'), (0, 0), lay.getchannel('A'))

def comment_card(img, t):
    if not (T_COMMENT <= t < T_COMMENT_END): return
    u = (t - T_COMMENT - 0.15) / 0.45; sc = ease_out_back(u) if u > 0 else 0
    if t > T_COMMENT_END - 0.2: sc *= max(0.01, (T_COMMENT_END - t) / 0.2)
    if sc <= 0.01: return
    cw, ch = 940, 330
    lay = Image.new('RGBA', (cw + 120, ch + 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); rr(ImageDraw.Draw(sh), (60, 90, 60 + cw, 90 + ch), 44, (0, 0, 0, 120))
    lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(22))); d = ImageDraw.Draw(lay)
    rr(d, (60, 70, 60 + cw, 70 + ch), 44, (255, 255, 255, 255), outline=ORANGE + (255,), width=7)
    ap = avatar.resize((96, 96), Image.LANCZOS); m = Image.new('L', (96, 96), 0); ImageDraw.Draw(m).ellipse((0, 0, 95, 95), fill=255)
    g = Image.new('RGB', (96, 96), (205, 205, 210)); lay.paste(g, (110, 108), m)
    d.text((158, 156), 'A', font=F('Inter-Bold.otf', 52), fill=(255, 255, 255), anchor='mm')
    d.text((232, 130), '@placeholder_user', font=F('Inter-Bold.otf', 40), fill=(20, 20, 20), anchor='lm')
    d.text((232, 176), '2h  ·  PLACEHOLDER', font=F('Inter-Medium.otf', 30), fill=(120, 120, 120), anchor='lm')
    d.text((110, 290), 'can you make me a bakery?', font=F('Inter-Bold.otf', 56), fill=(20, 20, 20), anchor='lm')
    hx, hy = 60 + cw - 90, 156   # cuore
    d.polygon([(hx, hy + 22), (hx - 30, hy - 6), (hx - 22, hy - 24), (hx, hy - 12), (hx + 22, hy - 24), (hx + 30, hy - 6)], fill=(235, 50, 70))
    put(img, lay, W / 2, 1000, sc, min(1, sc * 2))
    # intestazione + etichetta placeholder
    al = min(1, max(0, (t - T_COMMENT - 0.1) / 0.25)) * (1 if t < T_COMMENT_END - 0.2 else max(0, (T_COMMENT_END - t) / 0.2))
    put(img, text_layer('Custom building requests', 'Inter-Bold.otf', 52, (255, 255, 255), stroke=7), W / 2, 700, 1, al)
    tag = Image.new('RGBA', (780, 120), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
    rr(td, (10, 10, 770, 110), 50, (220, 40, 40, 255)); td.text((390, 60), 'PLACEHOLDER · TEST COMMENT', font=F('Inter-ExtraBold.otf', 42), fill=(255, 255, 255), anchor='mm')
    put(img, tag, W / 2, 1290, 1, al)

# ---------- composizione ----------
def render(t):
    sp = scene_params(t)
    if sp is None:
        img = profile_card(t)
        return img
    ts, z, cx, cy = sp
    sf = src_frame(ts)
    # spotlight sul commento: sfocatura + scurimento della scena
    dim = 0.0
    if T_COMMENT <= t < T_COMMENT_END:
        dim = min(smooth((t - T_COMMENT) / 0.3), smooth((T_COMMENT_END - t) / 0.25))
    if dim > 0:
        sf = Image.blend(sf, sf.filter(ImageFilter.GaussianBlur(2.2)), dim)
    img = zoom_up(sf, z, cx, cy)
    if dim > 0: img = Image.eval(img, lambda v: int(v * (1 - 0.42 * dim)))
    # hook
    title(img, t, ['1 follower', ('=', 110), '1 building'], T_HOOK, T_CARD, 590, 150, gap=1.0)
    # replay: scintillio dopo l'atterraggio
    sparkles(img, t, W / 2, 900, T_LAND2 + 0.45, 1.0, seed=3)
    sparkles(img, t, W / 2, 1000, T_COMMENT + 0.1, 1.0, n=10, spread=420, seed=5)
    sparkles(img, t, W / 2, 900, T_LAND + 0.1, 0.9, n=8, spread=300, seed=9)
    comment_card(img, t)
    title(img, t, ['12 buildings', ('DAY 1', 80)], T_LABEL, T_CTA, 600, 128, gap=1.15)
    title(img, t, ['Follow to become', 'a building'], T_CTA, T_END, 560, 104, gap=1.08)
    if T_CTA <= t < T_END:
        sc, al = pop_in(t, T_CTA + 0.25)
        pill = text_layer('Ledger of Cities', 'Inter-Bold.otf', 62, (255, 255, 255), stroke=7)
        put(img, pill, W / 2, 790, sc, al * (1 if t < T_END - 0.15 else (T_END - t) / 0.15))
    title(img, t, ['See you tomorrow!'], T_END, DUR + 1, 600, 94, fade_out=0)
    return img

if __name__ == '__main__':
    n = int(round(DUR * FPS))
    if len(sys.argv) > 3 and sys.argv[3] == 'stills':
        for tt in [float(x) for x in sys.argv[4:]]:
            render(tt).save(os.path.join(WORK, f'still_{tt:05.2f}.png'))
        sys.exit()
    audio = os.path.join(WORK, 'cozy_test_audio.wav')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', os.environ.get('CRF', '23'),
           '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(render(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print('video ok', OUT)
