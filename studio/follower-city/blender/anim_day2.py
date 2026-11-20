"""Follower City - clip di prova 'Day 2' (1 -> 12 palazzi): 270x480, 24 fps, 264 frame (11 s). Analitico, nessun keyframe.
Regola di regia: il Giorno N parte dallo stato del giorno prima -> il palazzo n.1 (rank 0) e' gia' in piedi e acceso; i rank 1..11
compaiono uno alla volta con il pop-up del Day 1 (sale, overshoot, polvere), ritmo che accelera (timeline_day2.py). Finestre/insegne
si accendono per palazzo (colore oggetto -> emissione). Camera = camera_for(N continuo) che segue il conteggio (low-pass).
Uso:  python -u anim_day2.py render [--samples 24]   (idempotente)   |   python -u anim_day2.py assemble
Lancio tracciato:  nohup python -u anim_day2.py render > day2.log 2>&1 &   poi  pgrep -f anim_day2 ; tail day2.log
"""
import sys, os, math, time, subprocess
import bpy, bmesh
from mathutils import Vector
import cozy_city as cc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "test"))
import timeline_day2 as T
from timeline_day2 import spring, FPS, NF, POP_START, RATE, IMPACT, N_NEW

RAW = os.path.join(HERE, "day2_frames")
TXT = os.path.join(HERE, "day2_text")
OUT = os.path.join(HERE, "cozy_day2_silent.mp4")
RES = (270, 480)
D_RISE = 11.0
N_TOT = N_NEW + 1
FINAL_N = 12.0
END_TGT = (0.0, 9.0, 2.0)         # centro dell abitato a 12 palazzi
END_AZ, END_EL, END_DIST = 8.0, 44.0, 65.0
GLOW_DELAY, GLOW_LEN = 10, 16


def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def make_glow_materials():
    """winlit/shoplit/lettr: emissione e colore pilotati dal Colore dell'oggetto (R = livello di accensione 0..1)."""
    spec = {"winlit": ((0.05, 0.07, 0.09), (1.0, 0.82, 0.45), 4.2), "shoplit": ((0.05, 0.07, 0.09), (1.0, 0.86, 0.55), 7.0),
            "lettr": ((0.10, 0.08, 0.06), (0.98, 0.88, 0.62), 1.5)}
    for name, (dark, lit, strn) in spec.items():
        m = cc._mats[name]; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        sp = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(oi.outputs["Color"], sp.inputs[0])
        mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = strn
        nt.links.new(sp.outputs[0], mu.inputs[0]); nt.links.new(mu.outputs[0], b.inputs["Emission Strength"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        mx.inputs[6].default_value = (*cc.lin(dark), 1); mx.inputs[7].default_value = (*cc.lin(lit), 1)
        nt.links.new(sp.outputs[0], mx.inputs[0]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])


def cam_curve():
    """N continuo della camera per ogni frame: conteggio morbido (pop) -> low-pass -> ease verso FINAL_N."""
    out, cs = [], 0.0
    for f in range(NF):
        c = sum(sstep(IMPACT[k] - 14, IMPACT[k] + 8, f) for k in range(N_NEW))
        cs += (c - cs) * 0.10
        out.append(cs)
    # normalizza: a conteggio completo -> FINAL_N
    mx = max(out[-1], 1e-6)
    return [1.0 + (FINAL_N - 1.0) * min(1.0, v / mx) if False else 1.0 + (FINAL_N - 1.0) * v / N_NEW for v in out]


def setup(samples):
    sc = cc.build_scene(N_TOT, 7, RES, samples)
    sc.cycles.use_animated_seed = False
    make_glow_materials()
    slots = cc.all_slots(7)[:N_TOT]
    lots = [bpy.data.objects[f"lot{i}"] for i in range(N_TOT)]
    for o in lots:
        o.color = (0, 0, 0, 1)
    lots[0].color = (1, 1, 1, 1)                       # n.1 gia' acceso (stato del giorno prima)
    bases = [o.location.copy() for o in lots]
    cam = bpy.data.objects["cam"]
    # orti sui lotti E in attesa (spariscono quando il lotto sale)
    gardens = {}
    for q in slots[1:]:
        if q['side'] == 'E' and not q['lm']:
            b = cc.MB(); cc.prop_garden(b, q, cc.rgs(7, 'garden', q['rank']))
            o = cc.link(bpy.data.objects.new(f"garden{q['rank']}", b.build(f"garden{q['rank']}")), sc.collection)
            gardens[q['rank']] = o
    # polvere + foglie
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    me = bpy.data.meshes.new("puff"); bm.to_mesh(me); bm.free()
    me.materials.append(cc.flat("dust", (0.93, 0.87, 0.76), rough=1.0))
    mel = bpy.data.meshes.new("leafm")
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts:
        v.co.z *= 0.18
    bm.to_mesh(mel); bm.free()
    mel.materials.append(cc.m_leaf(0))
    FX = {}
    for k in range(1, N_TOT):
        s = slots[k]; rg = cc.rgs(7, "anim", k)
        sg = -1 if s['side'] == 'W' else 1                # profondita' del lotto verso -sg
        xf, yc, w = s['xf'], s['yc'], s['w']
        puffs = []
        for q in range(12):                               # perimetro del lotto (8 x w)
            t = q / 12.0
            if t < 0.3:    px, py, nx, ny = xf, yc - w / 2 + t / 0.3 * w, sg, 0
            elif t < 0.5:  px, py, nx, ny = xf - sg * 8 * (t - 0.3) / 0.2, yc + w / 2, 0, 1
            elif t < 0.75: px, py, nx, ny = xf - sg * 8, yc + w / 2 - (t - 0.5) / 0.25 * w, -sg, 0
            else:          px, py, nx, ny = xf - sg * 8 * (1 - (t - 0.75) / 0.25), yc - w / 2, 0, -1
            o = bpy.data.objects.new(f"puff{k}_{q}", me); sc.collection.objects.link(o)
            puffs.append((o, px, py, nx, ny, rg.uniform(0.7, 1.3), rg.uniform(0, 0.25)))
        leaves = []
        for q in range(6):
            o = bpy.data.objects.new(f"leaf{k}_{q}", mel); sc.collection.objects.link(o)
            a = rg.uniform(0, 6.283)
            leaves.append((o, xf - sg * 4 + 5.5 * math.cos(a), yc + 0.5 * w * math.sin(a), rg.uniform(2.0, 4.5), rg.uniform(0, 6.28), rg.uniform(0.12, 0.2), rg.uniform(0, 0.2)))
        FX[k] = (puffs, leaves)
    return sc, cam, lots, bases, gardens, FX, cam_curve()


def set_frame(f, S):
    sc, cam, lots, bases, gardens, FX, ncam = S
    for k in range(1, N_TOT):
        o, base = lots[k], bases[k]
        f0, rate, fi = POP_START[k - 1], RATE[k - 1], IMPACT[k - 1]
        if f < f0:
            o.location = (base.x, base.y, -60.0)
            o.scale = (1, 1, 1)
        else:
            p = spring((f - f0) / FPS * rate)
            o.location = (base.x, base.y, base.z - (1.0 - p) * D_RISE)
            sxy = 0.9 + 0.1 * p
            o.scale = (sxy, sxy, 0.9 + 0.1 * p)
        g = sstep(fi + GLOW_DELAY, fi + GLOW_DELAY + GLOW_LEN, f) * (1.0 + 0.06 * math.sin(f * 1.7 + k) * 0)
        o.color = (g, g, g, 1)
        if k in gardens:
            gardens[k].scale = (1, 1, 1) if f < f0 else (0, 0, 0)
        puffs, leaves = FX[k]
        for (po, px, py, nx, ny, sz, dl) in puffs:
            tt = (f - fi) / FPS - dl
            if tt < 0 or tt > 0.9:
                po.scale = (0, 0, 0); continue
            kk = tt / 0.9
            r = sz * (0.25 + 1.0 * math.sin(math.pi * min(1.0, kk * 1.15)) ** 0.8 * (1.0 - 0.15 * kk))
            po.location = (px + nx * (0.3 + 1.6 * kk), py + ny * (0.3 + 1.6 * kk), 0.14 + 0.35 + 0.9 * kk)
            po.scale = (r * 0.9, r * 0.9, r * 0.6) if kk < 0.98 else (0, 0, 0)
        for (lo, lx, ly, hv, ph, sz, dl) in leaves:
            tt = (f - fi) / FPS - dl
            if tt < 0 or tt > 1.7:
                lo.scale = (0, 0, 0); continue
            kk = tt / 1.7
            lo.location = (lx + 0.8 * math.sin(ph + 3 * tt), ly + 0.8 * math.cos(ph + 2.4 * tt), 0.5 + hv * (1 - (1 - kk) ** 2) * 1.2 - 1.0 * kk * kk * 1.2)
            lo.rotation_euler = (1.3 * tt * 4 + ph, 0.9 * tt * 5, ph)
            lo.scale = (sz,) * 3 if kk < 0.85 else (sz * (1 - kk) / 0.15,) * 3
    # camera: stato di partenza = fine Day 1 (push-in 0.83), poi camera_for(N) che segue il conteggio
    N = ncam[f]
    pos, tgt, lens, fstop, fd = cc.camera_for(N, 7)
    kd = 0.83 + 0.17 * sstep(1.0, 3.0, N)
    w = sstep(2.5, 11.0, N)                           # camera_for(N) -> posa alta/obliqua man mano che i palazzi crescono
    az, el = math.radians(END_AZ), math.radians(END_EL)
    ep = Vector(END_TGT) + END_DIST * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    P = Vector(pos).lerp(ep, w); Tg = Vector(tgt).lerp(Vector(END_TGT), w)
    cam.location = Tg + (P - Tg) * kd
    cam.data.lens = lens
    bpy.data.objects["ctgt"].location = Tg
    cam.data.dof.focus_distance = (cam.location - Tg).length
    bpy.context.view_layer.update()


def render(samples):
    os.makedirs(RAW, exist_ok=True)
    S = setup(samples); sc = S[0]
    t_all = time.time(); done = 0; tt = []
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
        done += 1; tt.append(time.time() - t)
        print(f"[day2] frame {f:03d}/{NF} {tt[-1]:.1f}s", flush=True)
    print(f"[day2] RENDER FINITO: {done} frame nuovi in {time.time()-t_all:.0f}s ({(sum(tt)/max(1,len(tt))):.2f} s/frame medi)", flush=True)


def overlay():
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(TXT, exist_ok=True)
    fp = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
    ftit = ImageFont.truetype(fp, 15)
    fday = ImageFont.truetype(fp, 30)
    flab = ImageFont.truetype(fp, 12)
    imps = IMPACT
    for f in range(NF):
        im = Image.open(os.path.join(RAW, f"{f:04d}.png")).convert("RGBA")
        W, H = im.size
        a = int(255 * sstep(2, 10, f))
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)

        def txt(s, font, cx, y, alpha, fill=(255, 246, 228), sw=2):
            w = d.textlength(s, font=font)
            x = cx - w / 2
            d.text((x, y + 1.5), s, font=font, fill=(40, 22, 10, int(alpha * 0.5)), stroke_width=sw, stroke_fill=(40, 22, 10, int(alpha * 0.5)))
            d.text((x, y), s, font=font, fill=(*fill, alpha), stroke_width=sw, stroke_fill=(70, 40, 20, int(alpha * 0.95)))
        txt("1 follower = 1 building", ftit, W / 2, 46, a)                  # alto, safe zone, piccolo con contorno
        n = 1 + sum(1 for x in imps if f >= int(math.ceil(x)))
        last = max([x for x in imps if f >= int(math.ceil(x))] or [-99])
        since = f - int(math.ceil(last)) if last > -99 else 99
        sc_ = 1.0 + 0.30 * max(0.0, 1 - since / 5.0) ** 1.5 if since < 5 else 1.0
        fc = ImageFont.truetype(fp, int(round(40 * sc_)))
        txt(str(n), fc, W / 2, 68 - (fc.size - 40) * 0.5, a, fill=(255, 226, 150), sw=3)
        txt("Day 2", fday, W / 2, H - 66, a)
        Image.alpha_composite(im, lay).convert("RGB").save(os.path.join(TXT, f"{f:04d}.png"))


def assemble():
    overlay()
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(TXT, "%04d.png"),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", "-an", OUT])
    print("[day2] mp4 muto:", OUT, os.path.getsize(OUT), "byte")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "assemble":
        assemble()
    elif a and a[0] == "probe":                       # anteprima frame scelti: probe f1 f2 ... [--samples n]
        s = int(a[a.index("--samples") + 1]) if "--samples" in a else 12
        fr = [int(x) for x in a[1:] if x.isdigit()]
        os.makedirs(RAW + "_probe", exist_ok=True)
        S = setup(s)
        for f in fr:
            set_frame(f, S); S[0].render.filepath = os.path.join(RAW + "_probe", f"{f:04d}.png")
            t = time.time(); bpy.ops.render.render(write_still=True); cc.grade(S[0].render.filepath)
            print(f"[probe] {f} {time.time()-t:.1f}s", flush=True)
    else:
        s = int(a[a.index("--samples") + 1]) if "--samples" in a else 24
        render(s)
