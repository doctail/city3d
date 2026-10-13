# Prova quale backend GPU funziona davvero (ognuno in un processo separato). Stampa: DEVICE=OPTIX|CUDA|CPU
import subprocess, sys
CODE = r'''
import bpy, sys
dt = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.mesh.primitive_cube_add(); c = bpy.data.cameras.new("c"); o = bpy.data.objects.new("c", c); sc.collection.objects.link(o); sc.camera = o; o.location = (5, -5, 4); o.rotation_euler = (1.0, 0, 0.78)
sc.render.engine = "CYCLES"; sc.cycles.samples = 4; sc.render.resolution_x = sc.render.resolution_y = 64
pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = dt; pr.get_devices()
for d in pr.devices: d.use = d.type == dt
sc.cycles.device = "GPU"; sc.render.filepath = "/tmp/gputest.png"
bpy.ops.render.render(write_still=True); print("RENDER_OK")
'''
for dt in ('OPTIX', 'CUDA'):
    r = subprocess.run([sys.executable, '-c', CODE, dt], capture_output=True, text=True, timeout=600)
    ok = 'RENDER_OK' in r.stdout and 'Failed' not in (r.stdout + r.stderr)
    print(f'[gputest] {dt}: {"OK" if ok else "FALLITO"}', flush=True)
    if not ok: print('\n'.join((r.stdout + r.stderr).strip().splitlines()[-4:]), flush=True)
    if ok: print(f'DEVICE={dt}'); break
else: print('DEVICE=CPU')
