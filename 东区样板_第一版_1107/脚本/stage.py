"""Place staff characters into the scene and save a final .blend.
usage: python3 stage.py <scene.blend> <staff.blend> <out.blend>"""
import bpy, sys, math
scene_blend, staff_blend, out = sys.argv[1:4]
bpy.ops.wm.open_mainfile(filepath=scene_blend)
CX, CY = (44.4 + 77.9) / 2, 11.6
def P(x, y): return (x - CX, -(y - CY))
coll = bpy.data.collections.new('Staff'); bpy.context.scene.collection.children.link(coll)
# facing: characters face +Y in Blender (= plan north). south = pi, west = +pi/2, east = -pi/2
S, N, W, E = math.pi, 0.0, math.pi / 2, -math.pi / 2
PLACES = [
    ('sales', 63.65, 5.15, S, 'idle', 6),
    ('sales', 66.2, 7.3, E, 'wave', 8),
    ('nurse', 55.0, 9.0, S, 'idle', 20),
    ('nurse', 53.0, 11.45, W, 'carry', 4),
    ('nurse', 47.6, 4.2, W, 'work', 10),
    ('nurse', 58.75, 17.35, W, 'work', 30),
    ('nurse', 52.6, 17.0, W, 'work', 14),
    ('cleaner', 60.0, 11.8, N, 'work', 22),
]
for i, (role, x, y, rot, act, frame) in enumerate(PLACES):
    with bpy.data.libraries.load(staff_blend, link=False) as (src, dst):
        dst.objects = [role, role + '_body']
        dst.actions = [a for a in src.actions if a.startswith(role + '_')]
    rig, body = dst.objects
    for o in (rig, body): coll.objects.link(o)
    body.modifiers['rig'].object = rig
    X, Y = P(x, y); rig.location = (X, Y, 0); rig.rotation_euler = (0, 0, rot); rig.scale = (1.1, 1.1, 1.1)
    a = next(a for a in dst.actions if a.name.startswith(role + '_' + act))
    rig.animation_data_create(); rig.animation_data.action = a
    try: rig.animation_data.action_slot = a.slots[0]
    except Exception: pass
    # bake the chosen frame as a static pose so every instance keeps its own phase
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    pose = {b.name: (b.rotation_euler.copy(), b.location.copy()) for b in rig.pose.bones}
    rig.animation_data.action = None
    for b in rig.pose.bones:
        b.rotation_mode = 'XYZ'; b.rotation_euler, b.location = pose[b.name]
    if act == 'carry':   # milk bottle in hands
        m = bpy.data.materials.get('white_gloss')
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.2, location=(X - 0.28, Y, 0.78)); bt = bpy.context.object
        bt.data.materials.append(bpy.data.materials.get('linen')); coll.objects.link(bt) if bt.name not in coll.objects else None
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=out)
print('STAGED', len(PLACES))
