"""Follower City - reel FINALE Day 2 REALE: 1080x1920 nativo (render 1188x2112), 30 fps, 18 s. Il palazzo 1 e' gia' in piedi; compaiono
4 palazzi (A, B, OG @m.bardi56, villa @lillyflxwer) con il pop-up del Day 1. Camera = path che si allarga con il conteggio (el < 30 gradi).
Si rendono SOLO i frame unici (vedi unique_frames); 28 campioni + OIDN.
Uso:  python -u anim_day2_final.py render [--samples 28] [--threads 4] [--only 10,20] [--res 1188x2112] [--dir frames]
      python -u anim_day2_final.py list     (conteggio frame unici)
Lancio tracciato:  nohup python -u anim_day2_final.py render > day2_final.log 2>&1 &
"""
import sys, os, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "test"))
import timeline_day2_final as T
FPS = T.FPS
SCENE_END_F = T.SCENE_END_F + 1               # frame 0..SCENE_END_F (poi la scena resta ferma sull'ultimo)
POPF = [int(p * FPS) for p in T.POP]


def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)


def spring(u):
    return 0.0 if u <= 0 else 1.0 - math.exp(-7.0 * u) * (math.cos(9.0 * u) + 0.78 * math.sin(9.0 * u))


def unique_frames():
    """Solo le finestre dei pop cambiano immagine (la camera si muove SOLO dentro le finestre dei pop): salita = ogni frame, poi 1 su 3.
    Fuori dalle finestre la scena e' ferma e si riusa l'ultimo frame renderizzato (zero costo)."""
    S = set([0])
    for fp in POPF:
        S.update(range(fp, fp + 10)); S.update(range(fp + 10, fp + WIN, 3)); S.add(fp + WIN)
    return sorted(S)


WIN = 40


def cam_w():
    """conteggio continuo 0..1: la camera si allarga ad ogni pop, dentro la finestra [fp, fp+36] (fuori e' ferma)."""
    return [sum(sstep(fp, fp + 36, f) for fp in POPF) / 4.0 for f in range(SCENE_END_F + 1)]


END_AZ, END_EL, END_DIST, END_LENS = 34.0, 23.0, 47.0, 24.0
END_TGT = (-7.0, -5.0, 3.6)
GLOW_DELAY, GLOW_LEN = 10, 16
D_RISE = 11.0


def render(samples, threads, only, res, outdir):
    import bpy, bmesh
    from mathutils import Vector
    import cozy_city as cc
    import day2_specials as D
    D.register()
    os.makedirs(outdir, exist_ok=True)
    RES = res
    LP = {}
    sc = cc.build_scene(5, 7, RES, samples, lot_props=LP)
    sc.cycles.use_animated_seed = False
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.render.threads_mode = 'FIXED'; sc.render.threads = threads
    cam = bpy.data.objects["cam"]; cam.data.shift_y = 0.11       # il palazzo scende: titoli nella zona sicura alta senza coprire il tetto
    import anim_day2 as A2                                       # materiali con emissione pilotata dal colore oggetto
    A2.make_glow_materials()
    NT = 5
    slots = [cc.all_slots(7)[r] for r in cc.PICK]
    lots = [bpy.data.objects[f"lot{i}"] for i in range(NT)]
    for o in lots:
        o.color = (0, 0, 0, 1)
    lots[0].color = (1, 1, 1, 1)
    bases = [o.location.copy() for o in lots]
    gardens = {}
    for k in range(1, NT):
        b = cc.MB(); cc.prop_garden(b, slots[k], cc.rgs(7, 'garden', slots[k]['rank']))
        gardens[k] = cc.link(bpy.data.objects.new(f"garden{k}", b.build(f"garden{k}")), sc.collection)
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
    for k in range(1, NT):
        s = slots[k]; rg = cc.rgs(7, "anim", k)
        sg = -1 if s['side'] == 'W' else 1
        xf, yc, w = s['xf'], s['yc'], s['w']
        puffs = []
        for q in range(12):
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
    lprops = {k: bpy.data.objects[f"lprops{k}"] for k in range(1, NT)}
    p0, t0, _, _, _ = cc.camera_for(1, 7)
    P0, T0 = Vector(p0), Vector(t0)
    CW = cam_w()
    imps = [t * FPS for t in T.IMPACT]

    def set_frame(f):
        f = min(f, SCENE_END_F)
        for k in range(1, NT):
            o, base = lots[k], bases[k]
            f0 = T.POP[k - 1] * FPS; rate = T.RATE[k - 1]; fi = imps[k - 1]
            if f < f0:
                o.location = (base.x, base.y, -60.0); o.scale = (1, 1, 1)
            else:
                p = spring((f - f0) / FPS * rate)
                o.location = (base.x, base.y, base.z - (1.0 - p) * D_RISE)
                sxy = 0.9 + 0.1 * p
                o.scale = (sxy, sxy, 0.9 + 0.1 * p)
            g = sstep(fi + GLOW_DELAY, fi + GLOW_DELAY + GLOW_LEN, f)
            o.color = (g, g, g, 1)
            gardens[k].scale = (1, 1, 1) if f < f0 else (0, 0, 0)
            pp = sstep(fi - 2, fi + 9, f)
            lprops[k].location = (0, 0, -(1.0 - pp) * 9.0 - (0.0 if f >= fi - 2 else 30.0))
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
        w = CW[f]; w = w * w * (3 - 2 * w) if False else w
        v0 = P0 - T0; d0 = v0.length; hz = math.hypot(v0.x, v0.y)
        el0, az0 = math.atan2(v0.z, hz), math.atan2(v0.x, -v0.y)
        d = d0 * (END_DIST / d0) ** w
        el = el0 + (math.radians(END_EL) - el0) * w
        az = az0 + (math.radians(END_AZ) - az0) * w
        Tg = T0.lerp(Vector(END_TGT), w)
        cam.location = Tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
        cam.data.lens = 24.0 + (END_LENS - 24.0) * w
        bpy.data.objects["ctgt"].location = Tg
        cam.data.dof.focus_distance = d
        bpy.context.view_layer.update()
        return math.degrees(el)

    L = unique_frames()
    if only:
        L = [f for f in L if f in only]
    t_all = time.time(); done = 0
    for i, f in enumerate(L):
        path = os.path.join(outdir, f"{f:04d}.png")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue
        el = set_frame(f)
        t = time.time()
        sc.render.filepath = path + ".tmp.png"
        bpy.ops.render.render(write_still=True)
        cc.grade(path + ".tmp.png")
        os.replace(path + ".tmp.png", path)
        done += 1
        print(f"[day2f] unique {i+1}/{len(L)} (n={f}) el={el:.1f} {time.time()-t:.1f}s", flush=True)
    print(f"[day2f] RENDER FINITO: {done} frame nuovi in {time.time()-t_all:.0f}s", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "list":
        L = unique_frames(); print(len(L), "frame unici su", SCENE_END_F + 1, "frame di scena"); sys.exit()
    s = int(a[a.index("--samples") + 1]) if "--samples" in a else 28
    th = int(a[a.index("--threads") + 1]) if "--threads" in a else 4
    only = set(int(x) for x in a[a.index("--only") + 1].split(",")) if "--only" in a else None
    rs = a[a.index("--res") + 1] if "--res" in a else "1188x2112"
    res = tuple(int(x) for x in rs.split("x"))
    od = a[a.index("--dir") + 1] if "--dir" in a else os.path.join(HERE, "day2_final_frames")
    render(s, th, only, res, od)
