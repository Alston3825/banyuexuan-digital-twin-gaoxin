set -e
cd /home/claude/w2
python3 blender/build_scene.py plan_n.json out > out/log_build.txt 2>&1
python3 blender/stage.py out/banyuexuan_24f_east.blend out/banyuexuan_staff.blend out/banyuexuan_24f_east_final.blend > out/log_stage.txt 2>&1
for c in overview reception nursery guestroom; do
  python3 blender/render.py out/banyuexuan_24f_east_final.blend $c out/final_$c.png 1600x900 96 >> out/log_render.txt 2>&1
  python3 blender/comp.py out/final_$c.png out/final_$c.jpg
done
python3 blender/lineup.py out/banyuexuan_staff.blend out/final_staff.png idle 6 96 >> out/log_render.txt 2>&1
python3 blender/comp.py out/final_staff.png out/final_staff.jpg
echo DONE >> out/log_render.txt
