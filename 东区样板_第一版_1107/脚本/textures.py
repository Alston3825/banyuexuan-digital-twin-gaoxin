import numpy as np
from PIL import Image, ImageFilter
rng=np.random.default_rng(7)
def noise(n,scale,oct=4):
    out=np.zeros((n,n))
    for o in range(oct):
        s=max(2,int(scale*2**o)); g=rng.random((s+1,s+1))
        im=Image.fromarray((g*255).astype(np.uint8)).resize((n,n),Image.BICUBIC)
        out+=np.asarray(im)/255/(2**o)
    return out/out.max()
def save(a,name): Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save('tex/'+name,quality=90)
def planks(name,base,var,n=1024,rows=6,grain=0.10):
    a=np.zeros((n,n,3)); h=n//rows
    for r in range(rows):
        off=rng.integers(0,n); L=n//2
        for k in range(-1,3):
            x0=(off+k*L)%n
            tone=np.array(base)*(1+rng.uniform(-var,var))
            y=np.arange(h)[:,None]; x=np.arange(n)[None,:]
            g=np.sin((y*0.9+np.sin(x/37+r)*6)*0.55+rng.random()*6)*0.5+0.5
            fib=noise(n,3,3)[r*h:(r+1)*h,:]
            shade=1-grain*g-0.08*fib
            seg=np.zeros((h,n),bool); xs=(np.arange(n)-x0)%n; seg[:, xs<L]=True
            for c in range(3): a[r*h:(r+1)*h,:,c]=np.where(seg,tone[c]*shade,a[r*h:(r+1)*h,:,c])
            a[r*h:(r+1)*h, x0:x0+2,:]*=0.75
        a[r*h:r*h+2,:,:]*=0.72
    save(a,name)
planks('oak_light.jpg',(222,186,140),0.05)
planks('walnut.jpg',(120,78,52),0.08,grain=0.14)
planks('oak_warm.jpg',(205,160,112),0.06)
# vertical wall panel (light wood veneer)
def panel(name,base,n=1024,cols=4):
    a=np.zeros((n,n,3)); w=n//cols
    for c in range(cols):
        tone=np.array(base)*(1+rng.uniform(-0.03,0.03))
        x=np.arange(w)[None,:]; y=np.arange(n)[:,None]
        g=np.sin((x*0.6+np.sin(y/53+c)*5)*0.4+c)*0.5+0.5
        for k in range(3): a[:,c*w:(c+1)*w,k]=tone[k]*(1-0.06*g)
        a[:,c*w:c*w+3,:]*=0.82
    save(a,name)
panel('wall_panel.jpg',(226,198,160))
# marble tiles
def marble(name,base,vein,n=1024,tiles=2):
    nz=noise(n,4,6); v=np.abs(np.sin((np.linspace(0,1,n)[None,:]*9+nz*7)*np.pi))
    v=1-np.clip(v*6,0,1)**0.6
    a=np.array(base)[None,None,:]*(0.97+0.05*noise(n,8,3))[:,:,None]
    a=a*(1-0.35*v[:,:,None])+np.array(vein)[None,None,:]*0.35*v[:,:,None]
    t=n//tiles
    for i in range(tiles+1):
        a[i*t-2:i*t+1,:,:]=a[i*t-2:i*t+1,:,:]*0.88; a[:,i*t-2:i*t+1,:]*=0.88
    save(a,name)
marble('marble.jpg',(236,230,222),(170,158,148))
marble('terrazzo_warm.jpg',(232,214,192),(196,168,138),tiles=4)
def fabric(name,base,n=512):
    nz=noise(n,40,2); y,x=np.mgrid[0:n,0:n]; w=(np.sin(x*1.4)*np.sin(y*1.4))*0.04
    a=np.array(base)[None,None,:]*(0.94+0.08*nz+w)[:,:,None]; save(a,name)
fabric('fabric_grey.jpg',(150,152,146)); fabric('fabric_cream.jpg',(236,226,210)); fabric('fabric_teal.jpg',(34,86,84)); fabric('fabric_blush.jpg',(232,190,180)); fabric('carpet_round.jpg',(226,208,186))
print('ok')
