"""Helpers for building the Banyuexuan scene in Blender (bpy as a module)."""
import bpy, bmesh, math, os
from mathutils import Vector, geometry

TEX = os.path.join(os.path.dirname(__file__), '..', 'tex')

# ---------------------------------------------------------------- materials
_mats = {}
def _bsdf(m):
    nt = m.node_tree
    return nt.nodes.get('Principled BSDF')

def mat(name, color=(0.8, 0.8, 0.8), rough=0.6, metal=0.0, emit=None, emit_s=0.0,
        alpha=1.0, transmission=0.0, img=None, coat=0.0, sheen=0.0):
    if name in _mats: return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = _bsdf(m)
    def srgb(c): return [((v / 255) if v > 1 else v) for v in c] + [1.0]
    col = srgb(color) if isinstance(color, tuple) else color
    lin = [c ** 2.2 for c in col[:3]] + [1.0]
    b.inputs['Base Color'].default_value = lin
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat: b.inputs['Coat Weight'].default_value = coat
    if sheen: b.inputs['Sheen Weight'].default_value = sheen
    if emit is not None:
        e = srgb(emit); b.inputs['Emission Color'].default_value = [c ** 2.2 for c in e[:3]] + [1]
        b.inputs['Emission Strength'].default_value = emit_s
    if transmission:
        b.inputs['Transmission Weight'].default_value = transmission
        b.inputs['IOR'].default_value = 1.45
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    if img:
        t = m.node_tree.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(os.path.join(TEX, img), check_existing=True)
        m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    _mats[name] = m
    return m

# ---------------------------------------------------------------- mesh helpers
COLL = None
def collection(name):
    global COLL
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    COLL = c
    return c

def _link(obj):
    (COLL or bpy.context.scene.collection).objects.link(obj)
    return obj

def box_uv(bm, scale=1.0):
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        for l in f.loops:
            p = l.vert.co
            if abs(n.z) >= max(abs(n.x), abs(n.y)): u, v = p.x, p.y
            elif abs(n.x) >= abs(n.y): u, v = p.y, p.z
            else: u, v = p.x, p.z
            l[uv].uv = (u / scale, v / scale)

def mesh_obj(name, bm, material=None, uv_scale=None, smooth=False):
    if uv_scale: box_uv(bm, uv_scale)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); _link(o)
    if material: me.materials.append(material)
    return o

def prism(name, outer, holes=(), z0=0.0, z1=1.0, material=None, uv_scale=1.0, top_mat=None):
    """Extrude a 2D polygon (list of (x,y)) with holes between z0..z1."""
    rings = [list(outer)] + [list(h) for h in holes]
    rings = [r[:-1] if r[0] == r[-1] else r for r in rings]
    bm = bmesh.new()
    flat = [Vector((x, y, 0)) for r in rings for (x, y) in r]
    tris = geometry.tessellate_polygon([[Vector((x, y, 0)) for (x, y) in r] for r in rings])
    vb = [bm.verts.new((v.x, v.y, z0)) for v in flat]
    vt = [bm.verts.new((v.x, v.y, z1)) for v in flat]
    for t in tris:
        try: bm.faces.new([vt[t[0]], vt[t[1]], vt[t[2]]])
        except ValueError: pass
        try: bm.faces.new([vb[t[2]], vb[t[1]], vb[t[0]]])
        except ValueError: pass
    k = 0
    for r in rings:
        n = len(r)
        for i in range(n):
            a, b = k + i, k + (i + 1) % n
            try: bm.faces.new([vb[a], vb[b], vt[b], vt[a]])
            except ValueError: pass
        k += n
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, material, uv_scale)
    if top_mat:
        o.data.materials.append(top_mat)
        for p in o.data.polygons:
            if p.normal.z > 0.9 and p.center.z > z1 - 1e-4: p.material_index = 1
    return o

def flat(name, outer, holes=(), z=0.0, material=None, uv_scale=1.0):
    rings = [list(outer)] + [list(h) for h in holes]
    tris = geometry.tessellate_polygon([[Vector((x, y, 0)) for (x, y) in r] for r in rings])
    bm = bmesh.new(); pts = [p for r in rings for p in r]
    vs = [bm.verts.new((x, y, z)) for (x, y) in pts]
    for t in tris:
        try: bm.faces.new([vs[t[0]], vs[t[1]], vs[t[2]]])
        except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    return mesh_obj(name, bm, material, uv_scale)

def _finish(o, bevel=0.0, seg=3, subsurf=0, smooth=False):
    if bevel:
        m = o.modifiers.new('bevel', 'BEVEL'); m.width = bevel; m.segments = seg; m.limit_method = 'ANGLE'
    if subsurf:
        m = o.modifiers.new('sub', 'SUBSURF'); m.levels = subsurf; m.render_levels = subsurf
    if smooth or bevel or subsurf:
        for p in o.data.polygons: p.use_smooth = True
    return o

def cube(name, size, loc, material=None, bevel=0.0, seg=3, rot=0.0, parent=None, uv=0.5, subsurf=0):
    """size=(sx,sy,sz); loc is bottom-center."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], (v.co.z + 0.5) * size[2]))
    o = mesh_obj(name, bm, material, uv)
    o.location = loc; o.rotation_euler.z = rot
    if parent: o.parent = parent
    return _finish(o, bevel, seg, subsurf)

def cyl(name, r, h, loc, material=None, seg=32, r2=None, bevel=0.0, parent=None, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    for v in bm.verts: v.co.z += h / 2
    o = mesh_obj(name, bm, material, 0.5)
    o.location = loc
    if rot: o.rotation_euler = rot
    if parent: o.parent = parent
    return _finish(o, bevel, 2, 0, smooth=True)

def sphere(name, r, loc, material=None, scale=(1, 1, 1), parent=None, seg=24):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    o = mesh_obj(name, bm, material, 0.5, smooth=True)
    o.location = loc; o.scale = scale
    if parent: o.parent = parent
    return o

def torus(name, R, r, loc, material=None, rot=(0, 0, 0), parent=None, arc=1.0, seg=48):
    bm = bmesh.new()
    vs = []
    n1 = max(3, int(seg * arc)); n2 = 12
    for i in range(n1 + (0 if arc >= 1 else 1)):
        a = 2 * math.pi * arc * i / n1
        ring = []
        for j in range(n2):
            b = 2 * math.pi * j / n2
            ring.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        vs.append(ring)
    m = len(vs)
    for i in range(m if arc >= 1 else m - 1):
        a, b = vs[i], vs[(i + 1) % m]
        for j in range(n2):
            bm.faces.new([a[j], b[j], b[(j + 1) % n2], a[(j + 1) % n2]])
    o = mesh_obj(name, bm, material, 0.5, smooth=True)
    o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o

def lathe(name, profile, loc, material=None, seg=40, parent=None):
    """profile: list of (radius, z) from bottom to top -> surface of revolution."""
    bm = bmesh.new(); rings = []
    for (r, z) in profile:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(seg):
            bm.faces.new([a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, material, 0.5, smooth=True)
    o.location = loc
    if parent: o.parent = parent
    return o

def empty(name, loc=(0, 0, 0), rot=0.0, parent=None):
    o = bpy.data.objects.new(name, None); _link(o)
    o.location = loc; o.rotation_euler.z = rot
    if parent: o.parent = parent
    return o

def text(name, body, loc, size=0.3, material=None, rot=(0, 0, 0), extrude=0.0, align='CENTER', parent=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = 'CENTER'
    f = FONT()
    if f: cu.font = f
    o = bpy.data.objects.new(name, cu); _link(o)
    o.location = loc; o.rotation_euler = rot
    if material: cu.materials.append(material)
    if parent: o.parent = parent
    return o

_font = [None]
def FONT():
    if _font[0] is None:
        for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']:
            if os.path.exists(p):
                try: _font[0] = bpy.data.fonts.load(p); break
                except Exception: pass
        if _font[0] is None: _font[0] = False
    return _font[0] or None
