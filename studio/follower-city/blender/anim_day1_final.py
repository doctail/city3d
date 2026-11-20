"""Follower City - reel FINALE Day 1: 1080x1920 nativo, 30 fps, 11 s. Scena = anim_day1 (stesso setup/animazione).
Si rendono SOLO i frame unici (render a 1188x2112, 1.1x, cosi' lo zoom di montaggio non fa mai upscale):
  n=0 (scena vuota), n=30..99 (pop-up, 30 fps; 99..179 coperti dalla scheda profilo), n=180..225 (finestre, 1 su 2, i vuoti si fondono), n=225 (statico).
Uso:  python -u anim_day1_final.py render [--samples 32] [--threads 2] [--only 0,60,120]
      python -u anim_day1_final.py assemble
"""
import sys, os, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test"))
import bpy
import anim_day1 as A
import cozy_city as cc
import timeline_day1 as T

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "day1_final_frames")
FINAL = os.path.join(HERE, "day1_final_out")
OUT = os.path.join(HERE, "..", "test", "cozy_day1_silent.mp4")
W, H = 1080, 1920
RW, RH = 1188, 2112
FPS = T.FPS
A.FPS = FPS; A.RES = (RW, RH)
A.F_POP = int(T.T_POP * FPS); A.F_GLOW0 = int(T.T_GLOW0 * FPS); A.F_GLOW1 = int(T.T_GLOW1 * FPS)
A.F_CARD0 = int(T.T_CARD0 * FPS)
A.F_PUSH = 10 ** 6; A.NF = 10 ** 6 + 10        # camera ferma: lo zoom e' in montaggio
NTOT = int(T.DUR * FPS)


def unique_frames():
    L = [0] + list(range(A.F_POP, A.F_CARD0)) + list(range(A.F_GLOW0, A.F_GLOW1, 2)) + [A.F_GLOW1]
    return L


def render(samples, threads, only):
    os.makedirs(RAW, exist_ok=True)
    S = A.setup(samples)
    sc = S[0]
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.render.threads_mode = 'FIXED'; sc.render.threads = threads
    L = unique_frames()
    if only:
        L = [f for f in L if f in only]
    t_all = time.time(); done = 0
    for i, f in enumerate(L):
        path = os.path.join(RAW, f"{f:04d}.png")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue
        A.set_frame(f, S)
        t = time.time()
        sc.render.filepath = path + ".tmp.png"
        bpy.ops.render.render(write_still=True)
        cc.grade(path + ".tmp.png")
        os.replace(path + ".tmp.png", path)
        done += 1
        print(f"[day1f] unique {i+1}/{len(L)} (n={f}) {time.time()-t:.1f}s", flush=True)
    print(f"[day1f] RENDER FINITO: {done} frame nuovi in {time.time()-t_all:.0f}s", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "assemble":
        import day1_compose; day1_compose.assemble()
    else:
        s = int(a[a.index("--samples") + 1]) if "--samples" in a else 32
        th = int(a[a.index("--threads") + 1]) if "--threads" in a else 4
        only = set(int(x) for x in a[a.index("--only") + 1].split(",")) if "--only" in a else None
        render(s, th, only)
