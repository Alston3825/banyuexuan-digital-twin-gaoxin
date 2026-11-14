"""Build the Banyuexuan 24F east-wing style sample in Blender.
usage: python3 build_scene.py <plan_n.json> <out_dir>
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
import lib as L
from lib import mat, cube, cyl, sphere, torus, lathe, empty, text, prism, flat

PLAN, OUT = sys.argv[1], sys.argv[2]
REGION = (44.4, 0.0, 77.9, 23.0)
WALL_H = 1.3
random.seed(4)
plan = json.load(open(PLAN))
CX, CY = (REGION[0] + REGION[2]) / 2, 11.6
def P(x, y): return (x - CX, -(y - CY))
CLIP = sbox(*REGION)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------------ materials
M = dict(
    wall=mat('wall_plaster', (242, 233, 220), rough=0.7),
    wallwood=mat('wall_panel', img='wall_panel.jpg', rough=0.55),
    wall_top=mat('wall_top', (176, 128, 92), rough=0.45),
    slab=mat('slab', (236, 222, 204), rough=0.8),
    walnut=mat('floor_walnut', img='walnut.jpg', rough=0.35, coat=0.2),
    oak=mat('floor_oak', img='oak_light.jpg', rough=0.4, coat=0.15),
    oakw=mat('floor_oak_warm', img='oak_warm.jpg', rough=0.4, coat=0.15),
    marble=mat('floor_marble', img='marble.jpg', rough=0.12, coat=0.5),
    terrazzo=mat('floor_terrazzo', img='terrazzo_warm.jpg', rough=0.35),
    glass=mat('glass', (205, 232, 238), rough=0.05, alpha=0.08),
    acrylic=mat('acrylic', (240, 248, 250), rough=0.05, transmission=1.0, alpha=0.3),
    white=mat('white_gloss', (246, 243, 238), rough=0.25, coat=0.4),
    cream=mat('cream', (240, 230, 214), rough=0.6),
    linen=mat('linen', img='fabric_cream.jpg', rough=0.85, sheen=0.4),
    grey=mat('fabric_grey', img='fabric_grey.jpg', rough=0.8, sheen=0.5),
    sage=mat('sofa_sage', (142, 150, 138), rough=0.55),
    blush=mat('blush', img='fabric_blush.jpg', rough=0.85, sheen=0.4),
    teal=mat('curtain_teal', img='fabric_teal.jpg', rough=0.85, sheen=0.5),
    rust=mat('rust_orange', (196, 112, 70), rough=0.55),
    salmon=mat('salmon', (214, 132, 108), rough=0.55),
    wood=mat('wood_mid', img='oak_warm.jpg', rough=0.45),
    dark=mat('walnut_solid', (96, 64, 44), rough=0.45),
    gold=mat('gold', (214, 170, 96), rough=0.25, metal=1.0),
    steel=mat('steel', (200, 200, 198), rough=0.3, metal=0.9),
    marble_w=mat('marble_white', img='marble.jpg', rough=0.15, coat=0.6),
    pot=mat('pot', (206, 122, 88), rough=0.6),
    leaf=mat('leaf', (92, 140, 82), rough=0.6),
    leaf2=mat('leaf2', (120, 162, 98), rough=0.6),
    skin=mat('baby_skin', (246, 214, 194), rough=0.6),
    pink=mat('pink_soft', (244, 196, 206), rough=0.8),
    mint=mat('mint', (178, 222, 206), rough=0.7),
    water=mat('water', (150, 214, 224), rough=0.05, transmission=0.6, alpha=0.6),
    screen=mat('screen', (20, 30, 36), emit=(120, 220, 230), emit_s=3.0, rough=0.2),
    led=mat('led_warm', (255, 230, 190), emit=(255, 214, 160), emit_s=6.0),
    cyan=mat('tech_cyan', (120, 220, 230), emit=(110, 220, 235), emit_s=5.0),
    holo=mat('holo', (140, 220, 235), emit=(120, 210, 230), emit_s=1.5, alpha=0.35, rough=0.1),
    rug=mat('rug', img='carpet_round.jpg', rough=0.95, sheen=0.6),
    lift=mat('lift_metal', (150, 150, 156), rough=0.3, metal=0.8),
    black=mat('tv_black', (24, 24, 26), rough=0.2),
    balloon_a=mat('balloon_a', (240, 214, 170), rough=0.3, coat=0.8),
    balloon_b=mat('balloon_b', (236, 236, 236), rough=0.3, coat=0.8),
)
FLOOR = {'单间': 'walnut', '套间': 'walnut', '套房': 'walnut', '走廊': 'oak', '接待大厅': 'marble', '观看区': 'marble',
         '消毒换鞋区': 'marble', '电梯厅': 'marble', '多功能室': 'oakw', '护理站': 'oak', '托管室': 'oak', '游泳抚触室': 'oak',
         '卫生间': 'terrazzo', '公卫': 'terrazzo'}
UVS = {'walnut': 1.8, 'oak': 1.8, 'oakw': 1.8, 'marble': 1.6, 'terrazzo': 2.4}

# ------------------------------------------------------------------ architecture
L.collection('Architecture')
foot = Polygon(plan['foot']).intersection(CLIP)
prism('slab', [P(*p) for p in foot.exterior.coords], z0=-0.45, z1=-0.003, material=M['slab'], uv_scale=2)

def clipped(polys):
    for w in polys:
        try: g = Polygon(w['outer'], w['holes']).buffer(0).intersection(CLIP)
        except Exception: continue
        for p in getattr(g, 'geoms', [g]):
            if p.is_empty or p.area < 0.01 or p.geom_type != 'Polygon': continue
            yield p

for i, p in enumerate(clipped(plan['walls'])):
    prism(f'wall_{i}', [P(*c) for c in p.exterior.coords], [[P(*c) for c in h.coords] for h in p.interiors],
          0, WALL_H, M['wall'], uv_scale=1.6, top_mat=M['wall_top'])
for i, p in enumerate(clipped(plan['glass'])):
    prism(f'glass_{i}', [P(*c) for c in p.exterior.coords], [[P(*c) for c in h.coords] for h in p.interiors],
          0.02, WALL_H - 0.02, M['glass'], uv_scale=1)

rooms = []
for r in plan['rooms']:
    x0, y0, x1, y1 = r['bbox']
    if x1 < REGION[0] + 0.2 or x0 > REGION[2]: continue
    rooms.append(r)
    key = FLOOR.get(r['name'], 'terrazzo')
    if r['name'] == '电梯': key = None
    for j, poly in enumerate(r['poly']):
        if len(poly) < 3: continue
        g = Polygon(poly).buffer(0).intersection(CLIP)
        for k, pp in enumerate(getattr(g, 'geoms', [g])):
            if pp.is_empty or pp.geom_type != 'Polygon': continue
            flat(f"floor_{r['name']}_{r.get('num','')}_{j}_{k}", [P(*c) for c in pp.exterior.coords], z=0.0,
                 material=M[key] if key else M['lift'], uv_scale=UVS.get(key, 1))

def R(name, num=None):
    for r in rooms:
        if r['name'] == name and (num is None or r.get('num') == num): return r
def bb(r):
    x0, y0, x1, y1 = r['bbox']; return x0, y0, x1, y1

# ------------------------------------------------------------------ furniture
L.collection('Furniture')
def plant(x, y, s=1.0, tall=False):
    X, Y = P(x, y)
    cyl('pot', 0.2 * s, 0.38 * s, (X, Y, 0), M['pot'], r2=0.16 * s, bevel=0.01)
    n = 9 if tall else 6
    for i in range(n):
        a = i * 2.4; h = (0.55 + (i / n) * (0.9 if tall else 0.35)) * s
        sphere('leaf', 0.2 * s * (1.1 if tall else 1), (X + math.cos(a) * 0.14 * s, Y + math.sin(a) * 0.14 * s, h),
               M['leaf'] if i % 2 else M['leaf2'], scale=(1, 1, 0.8))

def bed(X, Y, rot, w=1.8, l=2.1):
    g = empty('bed', (X, Y, 0), rot)
    cube('frame', (w + 0.1, l, 0.32), (0, 0, 0.06), M['grey'], bevel=0.05, parent=g)
    cube('mattress', (w, l - 0.15, 0.22), (0, 0.06, 0.36), M['linen'], bevel=0.07, parent=g)
    cube('duvet', (w + 0.06, l * 0.62, 0.12), (0, l * 0.17, 0.52), M['grey'], bevel=0.06, seg=4, parent=g)
    cube('duvet_trim', (w + 0.08, 0.1, 0.13), (0, l * 0.17 - l * 0.31, 0.52), M['blush'], bevel=0.04, parent=g)
    cube('head', (w + 0.3, 0.22, 1.05), (0, -l / 2 - 0.02, 0), M['grey'], bevel=0.09, seg=5, parent=g)
    for sx in (-1, 1):
        cube('pillow', (w * 0.4, 0.42, 0.16), (sx * w * 0.22, -l / 2 + 0.36, 0.58), M['linen'], bevel=0.07, seg=4, parent=g)
    for i, c in enumerate([M['pink'], M['mint'], M['balloon_a']]):
        sphere('plush', 0.11, (-0.4 + i * 0.32, -l / 2 + 0.75, 0.74), c, scale=(1, 0.9, 1), parent=g)
    return g

def _tube(name, pts, r, material, cyclic=False, parent=None):
    """Round tube along a polyline/curve given as plan-local 3D points (bevelled curve -> mesh)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, cu); L._link(o); cu.materials.append(material)
    if parent: o.parent = parent
    return o

def _tub_outline(L_, W_, n=48, bulge=0.18):
    """Paramount-style tub outline: an oval that is wider at the head end (x>0)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = L_ / 2 * math.cos(t)
        w = W_ / 2 * (1 + bulge * math.cos(t)) / (1 + bulge)
        sx = math.copysign(abs(math.cos(t)) ** 0.7, math.cos(t)); sy = math.copysign(abs(math.sin(t)) ** 0.7, math.sin(t))
        pts.append((L_ / 2 * sx, w * sy))
    return pts

def bassinet(X, Y, rot=0.0, baby=True):
    """Newborn bassinet after the Paramount Bed (八乐梦) photo: clear acrylic tub, white tube rail,
    pink mattress, T-stand with wire basket, four curved legs on pink casters. Long axis = local X."""
    import bmesh
    g = empty('bassinet', (X, Y, 0), rot)
    PINKW = mat('caster_pink', (232, 168, 150), rough=0.4)
    FRAME = mat('frame_white', (238, 236, 232), rough=0.3, coat=0.3)
    TL, TW, zb, zt = 0.78, 0.44, 0.66, 0.92
    # tub: loft between a smaller bottom outline and the top outline, open at the top
    bm = bmesh.new(); rings = []
    for k, (z, s) in enumerate([(zb, 0.86), (zb + 0.05, 0.95), (zt, 1.0)]):
        rings.append([bm.verts.new((x * s, y * s, z)) for (x, y) in _tub_outline(TL, TW)])
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(n): bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]])
    bm.faces.new(rings[0][::-1])
    tub = L.mesh_obj('tub', bm, M['acrylic'], 0.5, smooth=True); tub.parent = g
    sm = tub.modifiers.new('sol', 'SOLIDIFY'); sm.thickness = 0.008
    # pink mattress
    pad = prism('pad', _tub_outline(TL * 0.84, TW * 0.84), z0=zb + 0.005, z1=zb + 0.05, material=M['pink'], uv_scale=0.5); pad.parent = g
    # white rail around the rim, with U-loops at both ends
    rim = [(x * 1.06, y * 1.12, zt - 0.03) for (x, y) in _tub_outline(TL, TW, 40)]
    _tube('rail', rim, 0.011, FRAME, cyclic=True, parent=g)
    for sx in (-1, 1):
        loop = [(sx * (TL / 2 + 0.03), -0.12, zt - 0.03), (sx * (TL / 2 + 0.06), -0.12, zt - 0.17), (sx * (TL / 2 + 0.06), 0.12, zt - 0.17), (sx * (TL / 2 + 0.03), 0.12, zt - 0.03)]
        _tube('loop', loop, 0.01, FRAME, parent=g)
    # T-stand: two flat posts + crossbar
    for sx in (-1, 1):
        cube('post', (0.05, 0.035, zb - 0.1), (sx * 0.16, 0, 0.1), FRAME, bevel=0.008, parent=g)
    cube('cross', (0.36, 0.035, 0.04), (0, 0, zb - 0.12), FRAME, bevel=0.008, parent=g)
    cube('cradle', (0.6, 0.3, 0.02), (0, 0, zb - 0.03), FRAME, bevel=0.006, parent=g)
    # wire basket
    zbk = 0.3
    _tube('bk_rim', [(-0.2, -0.15, zbk + 0.1), (0.2, -0.15, zbk + 0.1), (0.2, 0.15, zbk + 0.1), (-0.2, 0.15, zbk + 0.1)], 0.004, FRAME, cyclic=True, parent=g)
    for i in range(7):
        x = -0.18 + i * 0.06; _tube('bk_w', [(x, -0.15, zbk + 0.1), (x, -0.13, zbk), (x, 0.13, zbk), (x, 0.15, zbk + 0.1)], 0.003, FRAME, parent=g)
    # curved legs + casters
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = [(sx * 0.16, 0, 0.14), (sx * 0.2, sy * 0.06, 0.13), (sx * 0.3, sy * 0.18, 0.1), (sx * 0.33, sy * 0.21, 0.07)]
            _tube('leg', leg, 0.014, FRAME, parent=g)
            w = cyl('wheel', 0.035, 0.03, (sx * 0.33, sy * 0.21 + 0.015 * sy, 0.035), PINKW, rot=(math.pi / 2, 0, 0), parent=g)
            cube('fork', (0.03, 0.05, 0.04), (sx * 0.33, sy * 0.21, 0.05), M['black'], parent=g)
    if baby:
        sphere('baby_head', 0.085, (TL * 0.26, 0, zb + 0.12), M['skin'], parent=g)
        cube('swaddle', (0.34, 0.24, 0.1), (-0.04, 0, zb + 0.05), M['blush'], bevel=0.05, seg=4, parent=g)
    return g

def sofa(X, Y, rot, length=1.8, m=None, depth=0.86):
    m = m or M['sage']; g = empty('sofa', (X, Y, 0), rot)
    cube('seat', (length, depth, 0.42), (0, 0, 0.06), m, bevel=0.08, seg=4, parent=g)
    cube('back', (length, 0.24, 0.84), (0, -depth / 2 + 0.12, 0.06), m, bevel=0.1, seg=4, parent=g)
    for sx in (-1, 1):
        cube('arm', (0.22, depth, 0.62), (sx * (length / 2 - 0.11), 0, 0.06), m, bevel=0.09, seg=4, parent=g)
        cube('cushion', (length * 0.4, depth * 0.62, 0.14), (sx * length * 0.21, 0.08, 0.48), m, bevel=0.06, seg=4, parent=g)
    cube('pillow', (0.42, 0.14, 0.42), (-length * 0.25, -depth / 2 + 0.34, 0.5), M['linen'], bevel=0.07, parent=g, rot=0.1)
    cube('pillow2', (0.42, 0.14, 0.42), (length * 0.25, -depth / 2 + 0.34, 0.5), M['balloon_a'], bevel=0.07, parent=g, rot=-0.1)
    return g

def oval_table(X, Y, rx=0.6, ry=0.4, h=0.42, top=None):
    o = cyl('tabletop', 1, 0.05, (X, Y, h - 0.05), top or M['marble_w'], seg=48, bevel=0.015)
    o.scale = (rx, ry, 1)
    for a in (0.6, 2.5, 4.4):
        c = cyl('leg', 0.018, h - 0.05, (X + math.cos(a) * rx * 0.6, Y + math.sin(a) * ry * 0.6, 0), M['gold'], seg=10)

def round_chair(X, Y, rot, m=None):
    m = m or M['salmon']; g = empty('chair', (X, Y, 0), rot)
    cyl('seat', 0.24, 0.1, (0, 0, 0.45), m, bevel=0.03, parent=g)
    o = cyl('back', 0.26, 0.06, (0, -0.2, 0.62), m, bevel=0.02, parent=g, rot=(math.radians(80), 0, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube('leg', (0.025, 0.025, 0.45), (sx * 0.15, sy * 0.15, 0), M['gold'], parent=g)
    return g

def lounge_chair(X, Y, rot, m=None):
    m = m or M['rust']; g = empty('lounge', (X, Y, 0), rot)
    lathe('shell', [(0.0, 0.18), (0.36, 0.2), (0.42, 0.45), (0.44, 0.8), (0.4, 0.85)], (0, 0, 0), m, parent=g)
    cyl('cushion', 0.34, 0.14, (0, 0.05, 0.3), M['cream'], bevel=0.05, parent=g)
    cyl('base', 0.2, 0.18, (0, 0, 0), M['gold'], r2=0.08, parent=g)
    return g

def curtain(X, Y, rot, width=0.5, h=WALL_H - 0.05, m=None):
    import bmesh
    bm = bmesh.new(); n = 14; fold = 0.06
    top = []; bot = []
    for i in range(n + 1):
        x = -width / 2 + width * i / n; y = math.sin(i * math.pi / 2) * fold
        bot.append(bm.verts.new((x, y, 0.02))); top.append(bm.verts.new((x, y, h)))
    for i in range(n): bm.faces.new([bot[i], bot[i + 1], top[i + 1], top[i]])
    o = L.mesh_obj('curtain', bm, m or M['teal'], 0.5, smooth=True)
    s = o.modifiers.new('solid', 'SOLIDIFY'); s.thickness = 0.02
    o.location = (X, Y, 0); o.rotation_euler.z = rot
    return o

def call_terminal(X, Y, rot):
    g = empty('terminal', (X, Y, 0.0), rot)
    cube('body', (0.16, 0.06, 0.22), (0, 0, 0.9), M['white'], bevel=0.02, parent=g)
    torus('ring', 0.045, 0.008, (0, 0.035, 1.02), M['cyan'], rot=(math.pi / 2, 0, 0), parent=g)

def guest_room(r):
    x0, y0, x1, y1 = bb(r); N = y1 < 11
    dirv = 1 if N else -1                      # plan-y direction into the room from the window
    yw = y0 + 0.15 if N else y1 - 0.15         # window line (plan)
    west = int(r.get('num', '0')) % 2 == 0
    wallx = x0 + 0.12 if west else x1 - 0.12; inx = 1 if west else -1
    # bed: headboard on side wall, centred ~3.1m in from window
    by = yw + dirv * 3.3
    bx = wallx + inx * 1.08
    X, Y = P(bx, by); bed(X, Y, -math.pi / 2 if west else math.pi / 2)   # headboard (local -Y) on the side wall
    rx, ry = P(bx + inx * 0.2, by); c = cyl('rug', 1.0, 0.012, (rx, ry, 0.003), M['rug'], seg=48); c.scale = (1.5, 1.25, 1)
    nx, ny = P(wallx + inx * 0.28, by - dirv * 1.25); cube('nightstand', (0.44, 0.42, 0.5), (nx, ny, 0), M['wood'], bevel=0.03)
    cyl('lamp', 0.1, 0.24, (nx, ny, 0.5), M['led'], r2=0.07)
    tx, ty = P(wallx + inx * 0.28, by + dirv * 1.25); call_terminal(tx, ty, (math.pi / 2 if west else -math.pi / 2))
    # bassinet next to bed
    cx, cy = P(bx + inx * 1.55, by - dirv * 1.45); bassinet(cx, cy, 0)
    # sofa against window, facing room; oval coffee table
    sx = (x0 + x1) / 2 + (-inx) * 0.35
    X, Y = P(sx, yw + dirv * 0.55); sofa(X, Y, math.pi if N else 0, 1.7)   # back to the window, seat faces the bed
    X, Y = P(sx, yw + dirv * 1.45); oval_table(X, Y)
    # curtains at window ends
    for cxp in (x0 + 0.35, x1 - 0.35):
        X, Y = P(cxp, yw - dirv * 0.02); curtain(X, Y, 0, 0.55)
    # TV + cabinet on opposite wall facing bed
    ox = (x1 - 0.18) if west else (x0 + 0.18)
    X, Y = P(ox, by); cube('tv_cab', (1.5, 0.42, 0.45), (X, Y, 0), M['wood'], bevel=0.02, rot=math.pi / 2)
    cube('tv', (1.1, 0.04, 0.62), (X, Y, 0.8), M['black'], bevel=0.01, rot=math.pi / 2)
    X, Y = P(x1 - 0.4 if not west else x0 + 0.4, yw + dirv * 0.35)
    plant(*((x1 - 0.4) if not west else (x0 + 0.4), yw + dirv * 0.35), s=0.75)

for r in rooms:
    if r['name'] in ('单间', '套间') and r.get('num'): guest_room(r)

# 2429 suite (former recovery room)
r = R('套房')
if r:
    x0, y0, x1, y1 = bb(r)
    X, Y = P(x0 + 1.2, (y0 + y1) / 2 + 1.2); bed(X, Y, -math.pi / 2); X, Y = P(x0 + 2.9, y1 - 1.2); bassinet(X, Y)
    X, Y = P(x1 - 0.55, y0 + 2.2); sofa(X, Y, math.pi / 2, 2.0); X, Y = P(x1 - 1.7, y0 + 2.2); oval_table(X, Y)
    for cxp in (x0 + 0.35, x1 - 0.35): X, Y = P(cxp, y1 - 0.13); curtain(X, Y, 0, 0.55)

# reception hall (after the real photo): marble desk facing the entrance, wood logo wall behind,
# moon-gate bookshelf lounge on the east half, teal curtains on the windows
r = R('接待大厅'); x0, y0, x1, y1 = bb(r)
def sector(r0, r1, a0, a1, n=40):
    out = [(math.cos(a0 + (a1 - a0) * i / n) * r1, math.sin(a0 + (a1 - a0) * i / n) * r1) for i in range(n + 1)]
    inn = [(math.cos(a1 - (a1 - a0) * i / n) * r0, math.sin(a1 - (a1 - a0) * i / n) * r0) for i in range(n + 1)]
    return out + inn
dx_, dy_ = x0 + 3.0, y0 + 4.6                                   # desk centre (plan)
X2, Y2 = P(dx_, dy_ - 1.6)
cube('logo_wall', (3.8, 0.14, 2.1), (X2, Y2, 0), M['wallwood'], bevel=0.02)
torus('logo_ring', 0.34, 0.03, (X2, Y2 - 0.09, 1.45), M['gold'], rot=(math.pi / 2, 0, 0))
cyl('logo_moon', 0.24, 0.03, (X2 + 0.07, Y2 - 0.09, 1.45), M['led'], rot=(math.pi / 2, 0, 0))
text('logo_txt', '伴月轩母婴护理中心', (X2, Y2 - 0.09, 0.95), 0.2, M['gold'], rot=(math.pi / 2, 0, 0), extrude=0.006)
cube('logo_led', (3.7, 0.04, 0.03), (X2, Y2 - 0.08, 2.08), M['led'])
cx_, cy_ = P(dx_, dy_ - 0.9)
prism('desk', [(cx_ + a, cy_ + b) for a, b in sector(1.25, 1.6, math.radians(205), math.radians(335))], z0=0, z1=1.0, material=M['marble_w'], uv_scale=1.2)
prism('desk_top', [(cx_ + a, cy_ + b) for a, b in sector(1.18, 1.68, math.radians(203), math.radians(337))], z0=1.0, z1=1.05, material=M['white'])
prism('desk_led', [(cx_ + a, cy_ + b) for a, b in sector(1.6, 1.64, math.radians(205), math.radians(335))], z0=0.05, z1=0.08, material=M['led'])
cube('desk_pc', (0.5, 0.04, 0.32), (cx_ - 0.5, cy_ - 1.2, 1.05), M['screen'], bevel=0.01)
round_chair(cx_, cy_ - 0.75, math.pi, M['cream'])
# lounge east half
mx, my = P(x0 + 6.4, y0 + 0.45)
torus('moon_gate', 0.95, 0.1, (mx, my, 1.15), M['white'], rot=(math.pi / 2, 0, 0), arc=0.5)
for sx in (-1, 1): cube('gate_post', (0.2, 0.3, 1.15), (mx + sx * 0.95, my, 0), M['white'], bevel=0.02)
for k in range(3):
    for sx in (-1, 1):
        cube('shelf', (0.85, 0.3, 0.03), (mx + sx * 1.55, my, 0.3 + k * 0.4), M['wood'])
        for j in range(3):
            cube('book', (0.07, 0.2, 0.22 + 0.03 * j), (mx + sx * (1.3 + j * 0.2), my, 0.33 + k * 0.4), [M['rust'], M['cream'], M['sage']][(j + k) % 3])
        cube('shelf_side', (0.03, 0.3, 1.25), (mx + sx * 2.0, my, 0), M['wood'])
lx, ly = P(x0 + 6.4, y0 + 3.0)
cyl('lounge_rug', 1.7, 0.012, (lx, ly, 0.003), M['rug'], seg=64)
sofa(lx, ly + 0.95, math.pi, 2.4, M['cream'])
def tub_chair(X, Y, rot, m):
    g = empty('tub', (X, Y, 0), rot)
    cyl('seat', 0.36, 0.42, (0, 0, 0.0), m, bevel=0.05, parent=g)
    torus('back', 0.34, 0.1, (0, 0, 0.55), m, rot=(0, 0, math.radians(-30)), arc=0.62, parent=g)
    cyl('cushion', 0.3, 0.08, (0, 0, 0.42), M['cream'], bevel=0.03, parent=g)
    return g
tub_chair(lx - 1.25, ly - 0.55, math.radians(150), M['rust']); tub_chair(lx + 1.25, ly - 0.55, math.radians(210), M['rust'])
oval_table(lx, ly, 0.5, 0.5, 0.42, M['marble_w'])
cyl('vase', 0.07, 0.25, (lx, ly, 0.42), M['glass']); sphere('flower', 0.12, (lx, ly, 0.72), M['balloon_b'])
for p in [(x0 + 0.5, y0 + 0.6), (x1 - 0.5, y1 - 0.7), (x0 + 0.6, y1 - 0.7)]: plant(*p, s=1.3, tall=True)
for k in range(4):
    X, Y = P(x0 + 0.6 + k * 2.3, y0 + 0.17); curtain(X, Y, 0, 0.5)
cube('vitrine', (0.5, 2.4, 1.2), P(x1 - 0.35, y0 + 5.0) + (0,), M['white'], bevel=0.02)

# multi-function room: long skirted table, salmon chairs, balloons
r = R('多功能室'); x0, y0, x1, y1 = bb(r)
X, Y = P((x0 + x1) / 2, y0 + 3.0)
cube('table_top', (4.2, 1.0, 0.05), (X, Y, 0.72), M['white'], bevel=0.01)
cube('table_skirt', (4.25, 1.05, 0.7), (X, Y, 0.02), M['balloon_a'], bevel=0.01)
for i in range(5):
    round_chair(X - 1.7 + i * 0.85, Y - 0.85, 0); round_chair(X - 1.7 + i * 0.85, Y + 0.85, math.pi)
bx, by = P(x1 - 0.8, y0 + 0.8)
for i in range(7):
    sphere('balloon', 0.17, (bx + random.uniform(-0.4, 0.4), by + random.uniform(-0.3, 0.3), 1.1 + random.uniform(0, 0.6)),
           [M['balloon_a'], M['balloon_b'], M['pink']][i % 3], scale=(1, 1, 1.15))
X, Y = P(x0 + 1.2, y0 + 0.3); cube('board', (1.0, 0.06, 1.3), (X, Y, 0), M['cream'], bevel=0.02)
text('board_txt', 'HAPPY\n30 DAYS', (X, Y - 0.04, 0.85), 0.16, M['rust'], rot=(math.pi / 2, 0, 0), extrude=0.004)

# nurse station: white counter + wood top, glowing monitors, hologram panel
r = R('护理站'); x0, y0, x1, y1 = bb(r)
X, Y = P((x0 + x1) / 2, y1 - 0.65)
cube('counter', (4.0, 0.6, 1.0), (X, Y, 0), M['white'], bevel=0.04)
cube('counter_top', (4.2, 0.75, 0.05), (X, Y, 1.0), M['wood'], bevel=0.01)
cyl('counter_led', 0.01, 3.9, (X - 1.95, Y - 0.31, 0.12), M['cyan'], rot=(0, math.pi / 2, 0))
for dx in (-1.0, 0.6):
    cube('monitor', (0.55, 0.04, 0.34), (X + dx, Y + 0.15, 1.12), M['screen'], bevel=0.01)
    round_chair(X + dx, Y + 0.75, math.pi, M['cream'])
hx, hy = P((x0 + x1) / 2, y1 - 0.65)
cube('holo', (1.6, 0.02, 0.6), (hx, hy, 1.75), M['holo'])
text('holo_t', '智能呼叫中心', (hx, hy - 0.02, 2.13), 0.13, M['cyan'], rot=(math.pi / 2, 0, 0))
text('holo_t2', '2408  拿母乳  · 已接单', (hx, hy - 0.02, 1.98), 0.09, M['cyan'], rot=(math.pi / 2, 0, 0))
text('holo_t3', '平均响应 26 秒', (hx, hy - 0.02, 1.86), 0.08, M['cyan'], rot=(math.pi / 2, 0, 0))
X, Y = P(x1 - 0.4, y0 + 0.5); cube('fridge', (0.6, 0.6, 1.5), (X, Y, 0), M['white'], bevel=0.03)

# nursery (托管室) after the CAD: x 53.3-56.75, y 15.1-21.6 (plan m). Glass wall on the east (to the SPA)
# and along the north, door gap at the north-west. Six bassinets in a column along the glass wall.
NX0, NX1, NY0, NY1 = 53.3, 56.75, 15.1, 21.6
def glass_run(pts, h=WALL_H, t=0.06):
    from shapely.geometry import LineString
    poly = LineString(pts).buffer(t / 2, cap_style=2, join_style=2)
    prism('glass_wall', [P(*c) for c in poly.exterior.coords], z0=0.02, z1=h - 0.04, material=M['glass'])
    poly2 = LineString(pts).buffer(0.035, cap_style=2, join_style=2)
    prism('glass_cap', [P(*c) for c in poly2.exterior.coords], z0=h - 0.04, z1=h, material=M['wall_top'])
    prism('glass_sill', [P(*c) for c in poly2.exterior.coords], z0=0.0, z1=0.08, material=M['wall_top'])
arc = [(56.2 + 0.55 * math.sin(a), 15.1 + 0.55 * (1 - math.cos(a))) for a in [i * math.pi / 2 / 8 for i in range(9)]]
glass_run([(54.35, 15.1)] + arc + [(56.75, 21.55)])
for i in range(6):
    X, Y = P(55.8, 17.2 + i * 0.7); bassinet(X, Y, 0, baby=i % 3 != 2)
X, Y = P(53.62, 18.4); cube('counter', (0.6, 5.0, 0.9), (X, Y, 0), M['white'], bevel=0.03)
cube('counter_top', (0.66, 5.05, 0.04), (X, Y, 0.9), M['wood'])
for k in range(4): cube('appliance', (0.3, 0.3, 0.32), (X, Y - 1.8 + k * 1.2, 0.94), M['cream'], bevel=0.04)
X, Y = P(54.6, 20.8); lounge_chair(X, Y, math.radians(200), M['rust'])
X, Y = P(54.9, 17.6); c = cyl('cloud_rug', 0.6, 0.012, (X, Y, 0.003), M['rug'], seg=40); c.scale = (1, 1.6, 1)

# swim & touch (游泳抚触室) after the CAD: two pods in the north part, a 2x4 touch-table island in the middle
SX0, SX1, SY0, SY1 = 56.85, 60.8, 13.6, 21.6
for k, (px, py) in enumerate([(57.9, 14.4), (59.4, 15.8)]):
    X, Y = P(px, py)
    lathe('pod', [(0.1, 0.0), (0.42, 0.05), (0.55, 0.35), (0.58, 0.7), (0.52, 0.95), (0.47, 0.95), (0.52, 0.7), (0.5, 0.35), (0.38, 0.12), (0.0, 0.12)], (X, Y, 0), M['white'])
    cyl('pod_water', 0.48, 0.02, (X, Y, 0.78), M['water'], seg=40)
    torus('pod_ring', 0.5, 0.012, (X, Y, 0.95), M['cyan'])
for i in range(2):
    for j in range(4):
        X, Y = P(58.4 + i * 0.95, 17.0 + j * 0.78)
        cube('touch_base', (0.9, 0.74, 0.85), (X, Y, 0), M['wood'], bevel=0.02)
        cube('touch_pad', (0.82, 0.66, 0.07), (X, Y, 0.85), M['mint'] if (i + j) % 2 else M['pink'], bevel=0.03)
X, Y = P(60.45, 19.6); cube('cabinet', (0.45, 1.6, 1.3), (X, Y, 0), M['white'], bevel=0.02)
X, Y = P(57.4, 20.8); bassinet(X, Y, 0)

# viewing / shoe-change / misc
r = R('观看区')
if r:
    x0, y0, x1, y1 = bb(r); X, Y = P((x0 + x1) / 2, y0 + 1.0); cube('bench', (2.0, 0.45, 0.45), (X, Y, 0), M['wood'], bevel=0.04)
r = R('消毒换鞋区')
if r:
    x0, y0, x1, y1 = bb(r); X, Y = P(x0 + 0.35, (y0 + y1) / 2); cube('shoe_cab', (0.45, 3.0, 1.2), (X, Y, 0), M['white'], bevel=0.02)
    X, Y = P((x0 + x1) / 2, y0 + 1.4); cube('bench', (1.8, 0.45, 0.45), (X, Y, 0), M['wood'], bevel=0.04); plant(x1 - 0.6, y1 - 0.6, 1.1, True)
r = R('员工餐厅')
if r:
    x0, y0, x1, y1 = bb(r); X, Y = P((x0 + x1) / 2, (y0 + y1) / 2); cube('dtable', (2.4, 0.9, 0.04), (X, Y, 0.72), M['wood'], bevel=0.01)
    cube('dtable_leg', (2.2, 0.7, 0.72), (X, Y, 0), M['white'])
    for i in range(3):
        round_chair(X - 0.8 + i * 0.8, Y - 0.75, 0, M['sage']); round_chair(X - 0.8 + i * 0.8, Y + 0.75, math.pi, M['sage'])
r = R('厨房')
if r:
    x0, y0, x1, y1 = bb(r); X, Y = P((x0 + x1) / 2, y0 + 0.45); cube('k_counter', (x1 - x0 - 0.6, 0.65, 0.9), (X, Y, 0), M['steel'], bevel=0.01)
    X, Y = P((x0 + x1) / 2, (y0 + y1) / 2 + 0.4); cube('k_island', (2.6, 1.0, 0.9), (X, Y, 0), M['steel'], bevel=0.01)
r = R('机房')
if r:
    x0, y0, x1, y1 = bb(r)
    for i in range(4): X, Y = P((x0 + x1) / 2, y0 + 1.5 + i * 1.2); cube('rack', (0.6, 0.9, 1.5), (X, Y, 0), M['black'], bevel=0.01)
for r in rooms:
    if r['name'] == '电梯':
        x0, y0, x1, y1 = bb(r); X, Y = P((x0 + x1) / 2, (y0 + y1) / 2)
        cube('lift', (x1 - x0 - 0.2, y1 - y0 - 0.2, 0.06), (X, Y, 0), M['dark'], bevel=0.01)
        west = (x0 + x1) / 2 < 40; DX, DY = P(x1 - 0.12 if west else x0 + 0.12, (y0 + y1) / 2)
        cube('lift_door', (0.06, 1.1, WALL_H - 0.05), (DX, DY, 0), M['lift'], bevel=0.01)
        cube('lift_led', (0.07, 0.3, 0.05), (DX, DY, WALL_H - 0.18), M['cyan'])
    if r['name'] == '楼梯间' and r['bbox'][2] - r['bbox'][0] > 3.0:
        x0, y0, x1, y1 = bb(r); cx = (x0 + x1) / 2
        for i in range(10):
            for sx, hh in ((-1, i + 1), (1, 10 - i)):
                X, Y = P(cx + sx * 0.7, y0 + 2.0 + i * 0.3); cube('step', (1.2, 0.3, 0.15 * hh), (X, Y, 0), M['terrazzo'])

# corridor dressing + door number plates
co = R('走廊')
for x in (47.0, 55.0, 63.5, 70.5):
    plant(x, co['bbox'][1] + 0.4 if x % 2 else co['bbox'][3] - 0.4, 0.8)
for r in rooms:
    if r.get('num') and r.get('door'):
        dx, dy = r['door']; N = r['bbox'][3] < 11
        X, Y = P(dx + 0.55, dy - (0.06 if N else -0.06))
        pl = cube('plate', (0.34, 0.03, 0.16), (X, Y, 1.25), M['white'], bevel=0.01)
        text('plate_no', r['num'], (X, Y + (0.02 if not N else -0.02) * -1, 1.33), 0.09, M['dark'],
             rot=(math.pi / 2, 0, 0 if N else math.pi), extrude=0.003)
        cube('plate_led', (0.3, 0.012, 0.012), (X, Y, 1.23), M['cyan'])

for r in rooms:
    if r['name'] in ('卫生间', '公卫') and 2.0 < r['area'] < 7:
        x0, y0, x1, y1 = bb(r); w_, h_ = x1 - x0, y1 - y0
        if w_ < 1.0 or h_ < 1.0: continue
        X, Y = P(x0 + 0.35, (y0 + y1) / 2)
        lathe('toilet', [(0.0, 0.0), (0.16, 0.0), (0.2, 0.3), (0.22, 0.42), (0.0, 0.42)], (X, Y, 0), M['white'])
        cube('tank', (0.16, 0.38, 0.32), (X - 0.2, Y, 0.38), M['white'], bevel=0.03)
        X, Y = P(x1 - 0.3, (y0 + y1) / 2); cube('vanity', (0.45, 0.7, 0.82), (X, Y, 0), M['wood'], bevel=0.02)
        cube('basin', (0.4, 0.5, 0.06), (X, Y, 0.82), M['white'], bevel=0.02)
# warm LED strips along the corridor wall bases + cyan call lights at guest doors
co = R('走廊')
for yy in (co['bbox'][1] + 0.5, co['bbox'][3] - 0.5):
    X0_, Y_ = P(REGION[0] + 0.2, yy); X1_, _ = P(min(co['bbox'][2], REGION[2]) - 0.3, yy)
    cube('corr_led', (X1_ - X0_, 0.03, 0.012), ((X0_ + X1_) / 2, Y_, 0.0), M['led'])
# ------------------------------------------------------------------ demo-only overlays (not exported to web)
L.collection('DemoOverlay')
r = R('单间', '2408')
if r:
    x0, y0, x1, y1 = bb(r); X, Y = P((x0 + x1) / 2, y0 + 4.2)
    torus('call_ring', 0.9, 0.035, (X, Y, 0.04), mat('call_glow', (240, 120, 100), emit=(255, 120, 96), emit_s=8))
    torus('call_ring2', 1.2, 0.02, (X, Y, 0.04), mat('call_glow2', (240, 120, 100), emit=(255, 150, 120), emit_s=4))

# ------------------------------------------------------------------ world, light, cameras
L.collection('Rig')
w = bpy.data.worlds.new('World'); scene.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes['Background']; bg.inputs[0].default_value = (1.0, 0.86, 0.7, 1); bg.inputs[1].default_value = 0.35
bg2 = nt.nodes.new('ShaderNodeBackground'); bg2.inputs[0].default_value = (0.92, 0.62, 0.42, 1); bg2.inputs[1].default_value = 1.0
lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader'); outn = nt.nodes['World Output']
nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(bg.outputs[0], mix.inputs[1]); nt.links.new(bg2.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], outn.inputs['Surface'])
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 6.0; sun.angle = math.radians(8); sun.color = (1.0, 0.9, 0.78)
so = bpy.data.objects.new('sun', sun); L._link(so); so.rotation_euler = (math.radians(42), math.radians(-18), math.radians(35))
fill = bpy.data.lights.new('fill', 'AREA'); fill.energy = 450; fill.size = 30; fill.color = (1.0, 0.93, 0.85)
fo = bpy.data.objects.new('fill', fill); L._link(fo); fo.location = (0, 0, 18)

def cam(name, loc, look, lens=40, ortho=None):
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_end = 400
    if ortho: c.type = 'ORTHO'; c.ortho_scale = ortho
    o = bpy.data.objects.new(name, c); L._link(o); o.location = loc
    d = __import__('mathutils').Vector(look) - __import__('mathutils').Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o
cams = {
    'overview': cam('cam_overview', (-8, -30, 28), (2, 0.5, 0), 34),
    'reception': cam('cam_reception', (P(60.5, 18)[0] + 2, P(60.5, 18)[1] - 2, 9.5), P(64.0, 5.5) + (0,), 30),
    'nursery': cam('cam_nursery', (P(52, 3)[0] + 2, P(52, 3)[1] + 1, 9.5), P(56.5, 17.5) + (0,), 30),
    'guestroom': cam('cam_guestroom', (P(49.5, 13.5)[0] - 3.2, P(49.5, 13.5)[1] - 2.0, 7.5), P(50.6, 4.6) + (0,), 30),
}
scene.camera = cams['overview']

# render settings
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
scene.cycles.samples = 96; scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6; scene.cycles.transparent_max_bounces = 8
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Punchy'
except Exception: pass
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
scene.render.film_transparent = True

os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'banyuexuan_24f_east.blend'))
print('SAVED objects', len(bpy.data.objects))
