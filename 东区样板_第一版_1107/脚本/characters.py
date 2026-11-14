"""Chibi staff characters for Banyuexuan, one per uniform (from the uniform photos).
usage: python3 characters.py <out_dir>
Builds rigid-parented meshes on a small armature, with walk / idle / work / carry actions,
exports one .glb per role and saves staff.blend; renders a turnaround lineup.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector, Euler
import lib as L
from lib import mat, cube, cyl, sphere, torus, empty

OUT = sys.argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene; scene.render.fps = 24

SKIN = mat('skin', (252, 206, 176), rough=0.5, sheen=0.3)
BLUSH = mat('blush_face', (246, 140, 132), rough=0.8)
EYE = mat('eye', (40, 30, 28), rough=0.15, coat=1.0)
EYEHI = mat('eye_hi', (255, 255, 255), emit=(255, 255, 255), emit_s=1.0)
MOUTH = mat('mouth', (170, 80, 70), rough=0.6)

ROLES = {
    # 护理部: sky-blue tunic + trousers, white collar scarf & cuffs, white nurse cap, bob hair
    'nurse': dict(top=(150, 190, 232), bottom=(150, 190, 232), trim=(250, 250, 250), hair=(52, 36, 30), style='bob',
                  shoes=(248, 248, 248), cap=True, label='护理部'),
    # 保洁部: sage-green jacket with dark-green collar & cuffs, black trousers, bun
    'cleaner': dict(top=(176, 204, 172), bottom=(44, 44, 48), trim=(32, 86, 58), hair=(38, 28, 24), style='bun',
                    shoes=(40, 40, 44), cap=False, label='保洁部'),
    # 销售部: ivory tweed jacket + pencil skirt, gold buttons, white heels, low bun
    'sales': dict(top=(238, 222, 196), bottom=(236, 220, 194), trim=(214, 170, 96), hair=(70, 46, 34), style='lowbun',
                  shoes=(250, 248, 244), cap=False, skirt=True, label='销售部'),
}

def build(role, cfg, x_off=0.0):
    x_off = 0.0  # build at origin; placed after skinning
    L.collection('Char_' + role)
    TOP = mat(role + '_top', cfg['top'], rough=0.7, sheen=0.4)
    BOT = mat(role + '_bottom', cfg['bottom'], rough=0.7, sheen=0.3)
    TRIM = mat(role + '_trim', cfg['trim'], rough=0.5 if role != 'sales' else 0.25, metal=0.9 if role == 'sales' else 0.0)
    HAIR = mat(role + '_hair', cfg['hair'], rough=0.55, sheen=0.4)
    SHOE = mat(role + '_shoe', cfg['shoes'], rough=0.35, coat=0.5)

    # ---- armature
    arm_data = bpy.data.armatures.new(role + '_rig')
    rig = bpy.data.objects.new(role, arm_data); L._link(rig); rig.location = (x_off, 0, 0)
    bpy.context.view_layer.objects.active = rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones
    def bone(name, head, tail, parent=None):
        b = eb.new(name); b.head = head; b.tail = tail
        if parent: b.parent = eb[parent]
        return b
    bone('root', (0, 0, 0), (0, 0.2, 0))
    bone('hips', (0, 0, 0.55), (0, 0, 0.7), 'root')
    bone('spine', (0, 0, 0.7), (0, 0, 0.98), 'hips')
    bone('head', (0, 0, 0.98), (0, 0, 1.3), 'spine')
    for s, sx in (('L', 1), ('R', -1)):
        bone('arm.' + s, (sx * 0.2, 0, 0.93), (sx * 0.22, 0, 0.62), 'spine')
        bone('leg.' + s, (sx * 0.09, 0, 0.55), (sx * 0.09, 0, 0.1), 'hips')
    bpy.ops.object.mode_set(mode='OBJECT')

    def P(x, y, z): return (x + x_off, y, z)

    parts = []
    # torso: tapered rounded body
    t = cube('torso', (0.36, 0.26, 0.42), P(0, 0, 0.55), TOP, bevel=0.1, seg=4); t.scale = (1, 1, 1)
    parts.append((t, 'spine'))
    if cfg.get('skirt'):
        sk = cyl('skirt', 0.17, 0.34, P(0, 0, 0.3), BOT, r2=0.2, bevel=0.03); parts.append((sk, 'hips'))
    else:
        pv = cube('pelvis', (0.34, 0.24, 0.16), P(0, 0, 0.45), BOT, bevel=0.07); parts.append((pv, 'hips'))
    # collar / trim details
    if role == 'nurse':
        parts.append((torus('collar', 0.12, 0.025, P(0, 0, 0.96), TRIM), 'spine'))
        parts.append((cube('scarf', (0.07, 0.03, 0.14), P(0.03, 0.135, 0.82), TRIM, bevel=0.015), 'spine'))
        for k in range(3): parts.append((sphere('btn', 0.014, P(-0.06, 0.135, 0.85 - k * 0.09), TRIM), 'spine'))
        parts.append((cube('pocket', (0.08, 0.01, 0.02), P(0.1, 0.135, 0.85), TRIM), 'spine'))
    elif role == 'cleaner':
        parts.append((torus('collar', 0.12, 0.028, P(0, 0, 0.96), TRIM), 'spine'))
        parts.append((cube('placket', (0.045, 0.02, 0.36), P(0, 0.132, 0.6), TRIM, bevel=0.01), 'spine'))
    else:
        parts.append((torus('collar', 0.13, 0.035, P(0, 0, 0.95), TOP), 'spine'))
        for k in range(3):
            for sx in (-1, 1): parts.append((sphere('btn', 0.016, P(sx * 0.05, 0.133, 0.88 - k * 0.1), TRIM), 'spine'))
        parts.append((cube('belt', (0.37, 0.27, 0.03), P(0, 0, 0.62), TOP, bevel=0.012), 'spine'))
    # neck + head
    parts.append((cyl('neck', 0.06, 0.06, P(0, 0, 0.96), SKIN), 'head'))
    head = sphere('head', 0.25, P(0, 0, 1.2), SKIN, scale=(1.0, 0.95, 0.95)); parts.append((head, 'head'))
    for sx in (-1, 1):
        parts.append((sphere('eye', 0.042, P(sx * 0.088, 0.208, 1.175), EYE, scale=(0.85, 0.5, 1.2)), 'head'))
        parts.append((sphere('eyehi', 0.013, P(sx * 0.088 + 0.014, 0.229, 1.196), EYEHI), 'head'))
        parts.append((cube('brow', (0.06, 0.012, 0.012), P(sx * 0.088, 0.22, 1.245), HAIR, bevel=0.005), 'head'))
        parts.append((sphere('cheek', 0.035, P(sx * 0.15, 0.19, 1.13), BLUSH, scale=(1, 0.35, 0.6)), 'head'))
        parts.append((sphere('ear', 0.04, P(sx * 0.245, 0.0, 1.19), SKIN, scale=(0.5, 0.8, 1)), 'head'))
    sm = torus('smile', 0.03, 0.008, P(0, 0.228, 1.12), MOUTH, rot=(-math.pi / 2, 0, 0), arc=0.5); parts.append((sm, 'head'))
    # hair
    hc = sphere('hair_cap', 0.268, P(0, -0.03, 1.25), HAIR, scale=(1.02, 1.0, 0.92)); parts.append((hc, 'head'))
    parts.append((sphere('fringe', 0.21, P(0, 0.1, 1.355), HAIR, scale=(1.12, 0.6, 0.38)), 'head'))
    if cfg['style'] == 'bob':
        for sx in (-1, 1): parts.append((sphere('bob_side', 0.13, P(sx * 0.2, -0.02, 1.08), HAIR, scale=(0.6, 1.0, 1.25)), 'head'))
        parts.append((sphere('bob_back', 0.22, P(0, -0.12, 1.1), HAIR, scale=(1.1, 0.7, 0.9)), 'head'))
    elif cfg['style'] == 'bun':
        parts.append((sphere('bun', 0.1, P(0, -0.2, 1.33), HAIR), 'head'))
    else:
        parts.append((sphere('bun', 0.09, P(0, -0.24, 1.14), HAIR), 'head'))
        for sx in (-1, 1): parts.append((sphere('earring', 0.016, P(sx * 0.245, 0.02, 1.1), TRIM), 'head'))
    if cfg.get('cap'):
        capm = mat('cap_white', (252, 252, 252), rough=0.5)
        parts.append((cyl('cap', 0.16, 0.08, P(0, 0.02, 1.43), capm, r2=0.13, bevel=0.02), 'head'))
        parts.append((cube('cap_band', (0.14, 0.01, 0.025), P(0, 0.175, 1.46), mat('cap_band', (150, 190, 232))), 'head'))
    # arms
    for s, sx in (('L', 1), ('R', -1)):
        a = cyl('arm_' + s, 0.058, 0.3, P(sx * 0.215, 0, 0.62), TOP, r2=0.064, bevel=0.03); parts.append((a, 'arm.' + s))
        parts.append((cyl('cuff_' + s, 0.062, 0.04, P(sx * 0.215, 0, 0.6), TRIM if role != 'sales' else TOP), 'arm.' + s))
        parts.append((sphere('hand_' + s, 0.055, P(sx * 0.215, 0, 0.57), SKIN), 'arm.' + s))
        legm = SKIN if cfg.get('skirt') else BOT
        lg = cyl('leg_' + s, 0.065, 0.42, P(sx * 0.09, 0, 0.1), legm, r2=0.07, bevel=0.02); parts.append((lg, 'leg.' + s))
        parts.append((cube('shoe_' + s, (0.12, 0.2, 0.09), P(sx * 0.09, 0.03, 0.0), SHOE, bevel=0.04), 'leg.' + s))
    # rigid skinning: every part gets a vertex group for its bone, then all parts join into one mesh
    bpy.ops.object.select_all(action='DESELECT')
    for o, bname in parts:
        vg = o.vertex_groups.new(name=bname); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0][0]
    bpy.ops.object.convert(target='MESH')          # applies bevel/subsurf
    bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active; body.name = role + '_body'
    for p_ in body.data.polygons: p_.use_smooth = True
    body.parent = rig
    md = body.modifiers.new('rig', 'ARMATURE'); md.object = rig
    rig['role'] = role
    return rig

def key_actions(rig):
    pb = rig.pose.bones
    for b in pb: b.rotation_mode = 'XYZ'
    rig.animation_data_create()
    def make(name, frames, fn):
        act = bpy.data.actions.new(rig['role'] + '_' + name); act.use_fake_user = True
        rig.animation_data.action = act
        for f in range(0, frames + 1, 2):
            t = f / frames
            for b in pb: b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0)
            fn(t)
            for b in pb:
                b.keyframe_insert('rotation_euler', frame=f); b.keyframe_insert('location', frame=f)
        return act
    TAU = 2 * math.pi
    def walk(t):
        s = math.sin(TAU * t)
        pb['leg.L'].rotation_euler.x = s * 0.55; pb['leg.R'].rotation_euler.x = -s * 0.55
        pb['arm.L'].rotation_euler.x = -s * 0.5; pb['arm.R'].rotation_euler.x = s * 0.5
        pb['hips'].location.y = abs(math.sin(TAU * t)) * 0.03   # bone-local Y is up the chain
        pb['spine'].rotation_euler.y = s * 0.08; pb['head'].rotation_euler.x = 0.05
    def idle(t):
        s = math.sin(TAU * t)
        pb['spine'].location.y = s * 0.008; pb['head'].rotation_euler.z = s * 0.06
        pb['arm.L'].rotation_euler.y = s * 0.04; pb['arm.R'].rotation_euler.y = -s * 0.04
    def work(t):
        s = math.sin(TAU * t * 2)
        pb['arm.L'].rotation_euler.x = 1.1 + s * 0.2; pb['arm.R'].rotation_euler.x = 1.1 - s * 0.2
        pb['spine'].rotation_euler.x = 0.18; pb['head'].rotation_euler.x = 0.2
    def carry(t):
        s = math.sin(TAU * t)
        pb['arm.L'].rotation_euler.x = 1.25; pb['arm.R'].rotation_euler.x = 1.25
        pb['arm.L'].rotation_euler.y = -0.35; pb['arm.R'].rotation_euler.y = 0.35
        pb['leg.L'].rotation_euler.x = s * 0.45; pb['leg.R'].rotation_euler.x = -s * 0.45
        pb['hips'].location.y = abs(s) * 0.02
    def wave(t):
        s = math.sin(TAU * t * 2)
        pb['arm.R'].rotation_euler.x = 2.6; pb['arm.R'].rotation_euler.y = 0.3 + s * 0.35; pb['head'].rotation_euler.z = 0.15
    acts = [make('walk', 24, walk), make('idle', 48, idle), make('work', 48, work), make('carry', 24, carry), make('wave', 24, wave)]
    rig.animation_data.action = acts[1]
    # keep every action reachable for the exporter via NLA strips
    for a in acts:
        nm = a.name.split('_', 1)[1]; tr = rig.animation_data.nla_tracks.new(); tr.name = nm; st = tr.strips.new(nm, 0, a); tr.mute = True
    rig.animation_data.action = None
    return acts

rigs = {}
for i, (role, cfg) in enumerate(ROLES.items()):
    rigs[role] = build(role, cfg)
    rigs[role]['role'] = role
    rigs[role].location.x = (i - 1) * 0.9
    key_actions(rigs[role])

os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'banyuexuan_staff.blend'))

# export each role to its own glb (centred at origin)
for role, rig in rigs.items():
    bpy.ops.object.select_all(action='DESELECT')
    off = rig.location.x; rig.location.x = 0
    rig.select_set(True)
    for c in rig.children_recursive: c.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, f'staff_{role}.glb'), use_selection=True, export_apply=True,
                              export_animations=True, export_animation_mode='NLA_TRACKS', export_yup=True)
    rig.location.x = off
print('CHAR OK')
