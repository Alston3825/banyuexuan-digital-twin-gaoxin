import bpy, sys, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
s=bpy.context.scene
# pose: idle frame for each rig
for o in s.objects:
    if o.type=='ARMATURE':
        o.animation_data.action=bpy.data.actions.get(o['role']+'_'+(sys.argv[3] if len(sys.argv)>3 else 'idle'))
        try: o.animation_data.action_slot=o.animation_data.action.slots[0]
        except Exception: pass
s.frame_set(int(sys.argv[4]) if len(sys.argv)>4 else 6)
c=bpy.data.cameras.new('c'); c.lens=70; co=bpy.data.objects.new('c',c); s.collection.objects.link(co)
co.location=(0.6,5.6,1.5); d=Vector((0,0,0.75))-co.location; co.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); s.camera=co
for nm,loc,en,sz in [('key',(2.5,4,4),400,3),('rim',(-3,-3,3),250,3),('fill',(-3,4,1.5),120,4)]:
    l=bpy.data.lights.new(nm,'AREA'); l.energy=en; l.size=sz; o=bpy.data.objects.new(nm,l); s.collection.objects.link(o); o.location=loc
    d=Vector((0,0,0.8))-o.location; o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(1,0.9,0.8,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.6
bpy.ops.mesh.primitive_plane_add(size=20); fl=bpy.context.object; fl.is_shadow_catcher=True
s.render.engine='CYCLES'; s.cycles.samples=int(sys.argv[5]) if len(sys.argv)>5 else 64; s.cycles.use_denoising=True; s.render.film_transparent=True
s.view_settings.view_transform='AgX'
s.render.resolution_x=1400; s.render.resolution_y=900; s.render.filepath=sys.argv[2]; bpy.ops.render.render(write_still=True)
