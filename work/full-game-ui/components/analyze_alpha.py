from pathlib import Path
from PIL import Image
import numpy as np, json
R=Path(r'D:\work\majiang-image')
def clean(im):
 arr=np.array(im.convert("RGBA")); a=arr[:,:,3].copy(); initial=a.copy()
 a[a<=8]=0
 parent=[]; strong=[]; spans=[]; previous=[]
 def find(x):
  while parent[x]!=x:
   parent[x]=parent[parent[x]]; x=parent[x]
  return x
 def union(aid,bid):
  aa,bb=find(aid),find(bid)
  if aa!=bb: parent[bb]=aa; strong[aa]=strong[aa] or strong[bb]
 for y in range(a.shape[0]):
  delta=np.diff(np.pad((a[y]>0).astype(np.int8),(1,1)))
  starts=np.flatnonzero(delta==1); ends=np.flatnonzero(delta==-1)
  current=[]; pi=0
  for x0,x1 in zip(starts,ends):
   lab=len(parent);parent.append(lab);strong.append(bool(a[y,x0:x1].max()>=128))
   while pi<len(previous) and previous[pi][1]<x0:pi+=1
   k=pi
   while k<len(previous) and previous[k][0]<=x1:
    union(lab,previous[k][2]);k+=1
   current.append((int(x0),int(x1),lab));spans.append((y,int(x0),int(x1),lab))
  previous=current
 for y,x0,x1,lab in spans:
  if not strong[find(lab)]:a[y,x0:x1]=0
 removed=int(((initial>0)&(a==0)).sum())
 strong_removed=int(((initial>=128)&(a==0)).sum())
 a[a>=250]=255
 arr[:,:,3]=a;arr[a==0,:3]=0
 return Image.fromarray(arr),{"thresholdAlpha":8,"removeFloatingComponentsWithoutAlphaAtLeast128":True,"normalizeAlpha250To255":True,"removedPixels":removed,"removedAlphaAtLeast128":strong_removed,"zeroRGBUnderZeroAlpha":True}
def components(a):
    parent=[];spans=[];previous=[]
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):
        x,y=find(x),find(y)
        if x!=y:parent[y]=x
    for y in range(a.shape[0]):
        delta=np.diff(np.pad((a[y]>0).astype(np.int8),(1,1)))
        starts=np.flatnonzero(delta==1);ends=np.flatnonzero(delta==-1);current=[];pi=0
        for x0,x1 in zip(starts,ends):
            lab=len(parent);parent.append(lab)
            while pi<len(previous) and previous[pi][1]<x0:pi+=1
            k=pi
            while k<len(previous) and previous[k][0]<=x1:union(lab,previous[k][2]);k+=1
            current.append((int(x0),int(x1),lab));spans.append((y,int(x0),int(x1),lab))
        previous=current
    groups={}
    for y,x0,x1,lab in spans:
        lab=find(lab)
        d=groups.setdefault(lab,{'bbox':[x0,y,x1,y+1],'area':0,'strong':0,'spans':[]})
        b=d['bbox'];b[0]=min(b[0],x0);b[1]=min(b[1],y);b[2]=max(b[2],x1);b[3]=max(b[3],y+1)
        d['area']+=x1-x0;d['strong']+=int((a[y,x0:x1]>=128).sum());d['spans'].append((y,x0,x1))
    return sorted(groups.values(),key=lambda d:d['area'],reverse=True)
if __name__=='__main__':
    for p in (R/'designs/ui/full-game/component-sources').glob('*.png'):
        im,log=clean(Image.open(p));cs=components(np.asarray(im.getchannel('A')))
        print(p.name,json.dumps([{k:v for k,v in c.items() if k!='spans'} for c in cs if c['area']>100]))
