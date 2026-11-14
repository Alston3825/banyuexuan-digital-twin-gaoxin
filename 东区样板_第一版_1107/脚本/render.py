import bpy, sys, time
blend, cam, out, res, spp = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
bpy.ops.wm.open_mainfile(filepath=blend)
s=bpy.context.scene; s.camera=bpy.data.objects['cam_'+cam]
w,h=map(int,res.split('x')); s.render.resolution_x=w; s.render.resolution_y=h; s.cycles.samples=spp
s.render.filepath=out; t=time.time(); bpy.ops.render.render(write_still=True); print('RENDER',cam,round(time.time()-t,1),'s')
