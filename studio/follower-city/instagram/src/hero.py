"""Hero render (primo follower) per Instagram. Uso: python hero.py profile|post out.png [samples]"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "blender"))
import bpy
from mathutils import Vector
import cozy_city as cc

mode, out = sys.argv[1], sys.argv[2]
samples = int(sys.argv[3]) if len(sys.argv) > 3 else 56
BG = {"profile": (0.70, 0.80, 0.69), "post": (0.76, 0.83, 0.88)}[mode]   # salvia / blu polvere
res = (1080, 1080) if mode == "profile" else (1080, 1350)
sc = cc.build_scene(1, 7, res, samples)
keep = {"lot0", "cam", "ctgt", "sun", "fill", "tg"}
for o in list(bpy.data.objects):
    if o.name not in keep:
        bpy.data.objects.remove(o, do_unlink=True)
hero = bpy.data.objects["lot0"]
# fondale: disco + world monocromo stesso colore (look 'studio')
mat = cc.flat("bgdisc", BG, rough=1.0)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=400, fill_type='NGON', location=(hero.location.x, hero.location.y, 0.0))
d = bpy.context.object; d.data.materials.append(mat); d.is_shadow_catcher = True; sc.render.film_transparent = True
w = sc.world; nt = w.node_tree
for n in list(nt.nodes):
    if n.name != "World Output": nt.nodes.remove(n)
bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Color"].default_value = (*cc.lin(BG), 1); bg.inputs["Strength"].default_value = 1.0
nt.links.new(bg.outputs[0], nt.nodes["World Output"].inputs[0])
# pedana piccola (base del palazzo)
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=6.2, depth=0.3, location=(hero.location.x, hero.location.y, 0.0))
pl = bpy.context.object; pl.data.materials.append(cc.flat("plinth", (0.93, 0.88, 0.80), rough=0.9))
cam = bpy.data.objects["cam"]; tg = bpy.data.objects["ctgt"]
sc.render.resolution_x, sc.render.resolution_y = res
c = Vector((hero.location.x, hero.location.y, 0))
fx = 1 if hero.location.x > 0 else -1   # facciata verso il viale (asse x)
az = math.radians(float(os.environ.get("AZ", 32))); el = math.radians(float(os.environ.get("EL", 16)))
dist = float(os.environ.get("DIST", 30)); tz = float(os.environ.get("TZ", 5.0))
cam.constraints.clear()
cam.data.lens = float(os.environ.get("LENS", 50)); cam.data.sensor_fit = 'VERTICAL'
cam.data.dof.aperture_fstop = 5.6
off = Vector((-fx * math.cos(az), -math.sin(az) * 0.0 + 0, 0))
# direzione dalla facciata verso fuori: -fx in x, ruotata di az su y
dirv = Vector((-fx * math.cos(az), -math.sin(az), 0)).normalized()
tgt = Vector((c.x, c.y, tz + float(os.environ.get("DZ", 0)))) + Vector((0, float(os.environ.get("DY", 0)), 0))
cam.location = tgt + dirv * dist * math.cos(el) + Vector((0, 0, dist * math.sin(el)))
tg.location = tgt
cam.data.dof.focus_distance = dist
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
from PIL import Image
import numpy as np
im = Image.open(out).convert("RGBA")
W, H = im.size
yy = np.linspace(0, 1, H)[:, None, None]
bgc = np.array([int(v * 255) for v in BG], dtype=np.float32)[None, None, :]
base = np.broadcast_to(bgc * (1.04 - 0.10 * yy), (H, W, 3))
base = np.clip(base, 0, 255)
bgim = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
bgim.alpha_composite(im)
bgim.convert("RGB").save(out)
cc.grade(out, sat=1.08)
print("done", out)
