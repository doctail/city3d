"""Follower City - clip di prova 'Day 1' (primo follower): 270x480, 24 fps, 120 frame (5 s). Animazione analitica, nessun keyframe.
Timeline: 0-12 lotto+strada vuoti -> 12-42 palazzo 'pop-up' (sale dal terreno, overshoot piccolo, rimbalzo, scala 0.9->1.0, polvere + foglie)
-> 50-80 finestre/lampione si accendono (caldo) -> 62-119 push-in lento. Testo con PIL, assemblaggio con ffmpeg.
Uso:  python -u anim_day1.py render [--samples 24]   (idempotente: salta i frame gia' fatti)
      python -u anim_day1.py assemble
Lancio tracciato:  nohup python -u anim_day1.py render > day1.log 2>&1 &   poi  pgrep -f anim_day1 ; tail day1.log
"""
import sys, os, math, time, subprocess, glob
import bpy, bmesh
from mathutils import Vector
import cozy_city as cc

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "day1_frames")
TXT = os.path.join(HERE, "day1_text")
OUT = os.path.join(HERE, "cozy_day1.mp4")
NF, FPS, RES = 120, 24, (270, 480)
F_POP, F_GLOW0, F_GLOW1, F_PUSH = 12, 50, 80, 62
D_RISE = 11.0


def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def spring(u):
    """0 -> 1 con overshoot piccolo (~7%) e un rimbalzo."""
    if u <= 0:
        return 0.0
    return 1.0 - math.exp(-7.0 * u) * (math.cos(9.0 * u) + 0.78 * math.sin(9.0 * u))


def setup(samples):
    sc = cc.build_scene(1, 7, RES, samples)
    sc.cycles.use_animated_seed = False
    hero = bpy.data.objects["lot0"]
    cam = bpy.data.objects["cam"]
    tgt = bpy.data.objects["ctgt"].location.copy()
    pos0 = cam.location.copy()
    base = hero.location.copy()
    # polvere + foglie: oggetti condividono una mesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    me = bpy.data.meshes.new("puff"); bm.to_mesh(me); bm.free()
    me.materials.append(cc.flat("dust", (0.93, 0.87, 0.76), rough=1.0))
    mel = bpy.data.meshes.new("leafm")
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts:
        v.co.z *= 0.18
    bm.to_mesh(mel); bm.free()
    mel.materials.append(cc.m_leaf(0))
    rg = cc.rgs(7, "anim")
    xf, yc = base.x, base.y
    puffs = []
    for q in range(16):                                   # lungo il perimetro del lotto (8 x 5.8 m)
        t = q / 16.0
        if t < 0.3:   px, py, nx, ny = xf, yc - 2.9 + t / 0.3 * 5.8, 1, 0
        elif t < 0.5: px, py, nx, ny = xf - 8 * (t - 0.3) / 0.2, yc + 2.9, 0, 1
        elif t < 0.75: px, py, nx, ny = xf - 8, yc + 2.9 - (t - 0.5) / 0.25 * 5.8, -1, 0
        else:         px, py, nx, ny = xf - 8 * (1 - (t - 0.75) / 0.25), yc - 2.9, 0, -1
        o = bpy.data.objects.new(f"puff{q}", me); sc.collection.objects.link(o)
        puffs.append((o, px, py, nx, ny, rg.uniform(0.7, 1.3), rg.uniform(0, 0.25)))
    leaves = []
    for q in range(12):
        o = bpy.data.objects.new(f"leaf{q}", mel); sc.collection.objects.link(o)
        a = rg.uniform(0, 6.283)
        leaves.append((o, xf - 4 + 5.5 * math.cos(a), yc + 4.2 * math.sin(a), rg.uniform(2.0, 4.5), rg.uniform(0, 6.28), rg.uniform(0.12, 0.2), rg.uniform(0, 0.2)))
    return sc, hero, cam, tgt, pos0, base, puffs, leaves


def set_frame(f, S):
    sc, hero, cam, tgt, pos0, base, puffs, leaves = S
    u = max(0.0, (f - F_POP) / FPS) * 0.8
    p = spring(u) if f >= F_POP else 0.0
    vis = f >= F_POP
    hero.location = (base.x, base.y, base.z - (1.0 - p) * D_RISE if vis else -60.0)
    sxy = 0.9 + 0.1 * p
    hero.scale = (sxy, sxy, 0.9 + 0.1 * p)
    # impatto: istante in cui p supera 0.9 la prima volta
    ui = next(i / 240.0 for i in range(1, 400) if spring(i / 240.0) >= 0.9)
    f_imp = F_POP + ui / 0.8 * FPS
    for (o, px, py, nx, ny, sz, dl) in puffs:
        tt = (f - f_imp) / FPS - dl
        if tt < 0 or tt > 0.9:
            o.scale = (0, 0, 0); continue
        k = tt / 0.9
        r = sz * (0.25 + 1.0 * math.sin(math.pi * min(1.0, k * 1.15)) ** 0.8 * (1.0 - 0.15 * k))
        o.location = (px + nx * (0.3 + 1.6 * k), py + ny * (0.3 + 1.6 * k), 0.14 + 0.35 + 0.9 * k)
        o.scale = (r * 0.9, r * 0.9, r * 0.6) if k < 0.98 else (0, 0, 0)
    for (o, lx, ly, hv, ph, sz, dl) in leaves:
        tt = (f - f_imp) / FPS - dl
        if tt < 0 or tt > 1.7:
            o.scale = (0, 0, 0); continue
        k = tt / 1.7
        o.location = (lx + 0.8 * math.sin(ph + 3 * tt), ly + 0.8 * math.cos(ph + 2.4 * tt), 0.5 + hv * (1 - (1 - k) ** 2) * 1.2 - 1.0 * k * k * 1.2)
        o.rotation_euler = (1.3 * tt * 4 + ph, 0.9 * tt * 5, ph)
        o.scale = (sz,) * 3 if k < 0.85 else (sz * (1 - k) / 0.15,) * 3
    # finestre / lampione: spenti -> caldi
    g = sstep(F_GLOW0, F_GLOW1, f)
    fl = 1.0 + 0.06 * math.sin(f * 1.7) * g
    dark = (0.05, 0.07, 0.09)
    for name, col, em, strn in (("winlit", (1.0, 0.82, 0.45), (1.0, 0.68, 0.26), 4.2), ("shoplit", (1.0, 0.86, 0.55), (1.0, 0.72, 0.32), 7.0)):
        b = cc._mats[name].node_tree.nodes["Principled BSDF"]
        c = [d + (cl - d) * g for d, cl in zip(dark, col)]
        b.inputs["Base Color"].default_value = (*cc.lin(c), 1)
        b.inputs["Emission Strength"].default_value = strn * g * fl
    for name, strn in (("lamp", 40.0), ("lettr", 1.5)):
        b = cc._mats[name].node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Strength"].default_value = strn * g
    # camera: ferma, poi push-in lento (ease in-out)
    e = sstep(F_PUSH, NF - 1, f)
    e = e * e * (3 - 2 * e)
    k = 1.0 - 0.17 * e
    cam.location = (tgt.x + (pos0.x - tgt.x) * k, tgt.y + (pos0.y - tgt.y) * k, tgt.z + (pos0.z - tgt.z) * k)
    cam.data.dof.focus_distance = (cam.location - tgt).length
    bpy.context.view_layer.update()


def render(samples):
    os.makedirs(RAW, exist_ok=True)
    S = setup(samples)
    sc = S[0]
    t_all = time.time(); done = 0
    for f in range(NF):
        path = os.path.join(RAW, f"{f:04d}.png")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue
        set_frame(f, S)
        t = time.time()
        sc.render.filepath = path + ".tmp.png"
        bpy.ops.render.render(write_still=True)
        cc.grade(path + ".tmp.png")
        os.replace(path + ".tmp.png", path)
        done += 1
        print(f"[day1] frame {f:03d}/{NF} {time.time()-t:.1f}s", flush=True)
    print(f"[day1] RENDER FINITO: {done} frame nuovi in {time.time()-t_all:.0f}s", flush=True)


def overlay():
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(TXT, exist_ok=True)
    fp = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
    ft = ImageFont.truetype(fp, 21)
    fb = ImageFont.truetype(fp, 30)
    for f in range(NF):
        im = Image.open(os.path.join(RAW, f"{f:04d}.png")).convert("RGBA")
        a = int(255 * sstep(3, 11, f))
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for txt, font, y in (("1 follower = 1 building", ft, 34), ("Day 1", fb, im.size[1] - 62)):
            w = d.textlength(txt, font=font)
            x = (im.size[0] - w) / 2
            d.text((x + 1.5, y + 2), txt, font=font, fill=(40, 22, 10, int(a * 0.55)), stroke_width=2, stroke_fill=(40, 22, 10, int(a * 0.55)))
            d.text((x, y), txt, font=font, fill=(255, 246, 228, a), stroke_width=1, stroke_fill=(70, 40, 20, int(a * 0.9)))
        Image.alpha_composite(im, lay).convert("RGB").save(os.path.join(TXT, f"{f:04d}.png"))


def assemble():
    overlay()
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(TXT, "%04d.png"),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", "-an", OUT])
    print("[day1] mp4:", OUT, os.path.getsize(OUT), "byte")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "assemble":
        assemble()
    else:
        s = int(a[a.index("--samples") + 1]) if "--samples" in a else 24
        render(s)
