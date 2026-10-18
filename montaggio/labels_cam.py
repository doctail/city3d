# Posizione sullo schermo dei monumenti, fotogramma per fotogramma, con la STESSA camera di build_render.py
# (chiavi di posizione e bersaglio, vincolo TRACK_TO, obiettivo interpolato). Serve alle etichette del montaggio.
# Uso: <python con bpy> labels_cam.py schedule.json landmarks.json OUT.json [W H] [F0 F1]
#   landmarks.json: {"Nome": [x, y, altezza, anno], ...}  (metri locali come i dati della citta')
import bpy, json, sys
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
SCHED, LM, OUT = json.load(open(a[0])), json.load(open(a[1])), a[2]
W, H = (int(a[3]), int(a[4])) if len(a) > 4 else (1920, 1080)
FPS = 24; N = int(round(SCHED['duration'] * FPS)) + 1
F0, F1 = (int(a[5]), int(a[6])) if len(a) > 6 else (1, N)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS
cam = bpy.data.cameras.new('cam'); cam.lens = float(SCHED.get('lens', 30)); cam.clip_end = 200000
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
tg = bpy.data.objects.new('target', None); sc.collection.objects.link(tg)
c = co.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
LENSK = [(int(round(k[0] * FPS)) + 1, float(k[3]) if len(k) > 3 else cam.lens) for k in SCHED['cam']]
def lens_at(f):
    if f <= LENSK[0][0]: return LENSK[0][1]
    for (fa, la), (fb, lb) in zip(LENSK, LENSK[1:]):
        if f <= fb: u = (f - fa) / max(1, fb - fa); u = u * u * (3 - 2 * u); return la + (lb - la) * u
    return LENSK[-1][1]
for k in SCHED['cam']:
    f = int(round(k[0] * FPS)) + 1
    co.location = k[1]; co.keyframe_insert('location', frame=f); tg.location = k[2]; tg.keyframe_insert('location', frame=f)
out = {n: {'h': v[2], 'y': v[3], 'p': []} for n, v in LM.items()}
for f in range(F0, F1 + 1):
    sc.frame_set(f); cam.lens = lens_at(f); bpy.context.view_layer.update()
    for n, v in LM.items():
        p = world_to_camera_view(sc, co, Vector((v[0], v[1], v[2])))
        out[n]['p'].append([round(p.x * W, 1), round((1 - p.y) * H, 1), round(p.z, 1)])   # z = distanza davanti alla camera
json.dump({'F0': F0, 'W': W, 'H': H, 'lm': out}, open(OUT, 'w'))
print('etichette', len(LM), 'monumenti,', F1 - F0 + 1, 'fotogrammi ->', OUT)
