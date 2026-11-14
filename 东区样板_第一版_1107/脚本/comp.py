import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGBA'); w,h=im.size
bg=Image.new('RGBA',(w,h)); px=bg.load()
import math
for y in range(h):
    for x in range(0,w):
        pass
# radial warm gradient
import numpy as np
yy,xx=np.mgrid[0:h,0:w]; d=np.sqrt(((xx-w*0.5)/w)**2+((yy-h*0.35)/h)**2)
c0=np.array([253,242,228]); c1=np.array([240,208,176]); t=np.clip(d/0.75,0,1)[...,None]
arr=(c0*(1-t)+c1*t).astype(np.uint8); bg=Image.fromarray(np.dstack([arr,np.full((h,w),255,np.uint8)]),'RGBA')
bg.alpha_composite(im); bg.convert('RGB').save(sys.argv[2],quality=92)
