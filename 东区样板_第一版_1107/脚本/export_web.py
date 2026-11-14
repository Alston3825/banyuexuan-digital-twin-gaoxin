"""Export the static scene (architecture + furniture) as one merged glb for the web viewer.
usage: python3 export_web.py <scene.blend> <out.glb>"""
import bpy, sys
blend, out = sys.argv[1:3]
bpy.ops.wm.open_mainfile(filepath=blend)
keep = {'Architecture', 'Furniture'}
# drop overlays, rig (lights/cameras) and anything hidden
for c in list(bpy.data.collections):
    if c.name not in keep:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.data.objects):
    if o.hide_render or o.type in ('LIGHT', 'CAMERA'): bpy.data.objects.remove(o, do_unlink=True)
# convert everything (texts, modifiers, parented empties) to plain meshes, then join into one object
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'FONT'): o.select_set(True)
bpy.context.view_layer.objects.active = next(o for o in bpy.data.objects if o.type == 'MESH')
bpy.ops.object.convert(target='MESH')
for o in list(bpy.data.objects):
    if o.type == 'EMPTY':
        for ch in o.children:
            mw = ch.matrix_world.copy(); ch.parent = None; ch.matrix_world = mw
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
glass = [o for o in meshes if o.name.startswith('glass') or any(m and m.name in ('glass', 'acrylic', 'holo', 'water') for m in o.data.materials)]
solid = [o for o in meshes if o not in glass]
def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); j = bpy.context.view_layer.objects.active; j.name = name; return j
join(solid, 'scene_solid'); join(glass, 'scene_glass')
bpy.ops.export_scene.gltf(filepath=out, export_apply=True, export_yup=True, export_lights=False, export_cameras=False,
                          export_image_format='JPEG', export_jpeg_quality=82)
print('EXPORTED', len(solid), len(glass))
