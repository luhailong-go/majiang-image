from pathlib import Path
from PIL import Image
import numpy as np, json
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[2]
results=[]
for p in sorted((ROOT/'designs/characters/full-game').glob('*-native.png')):
 im=Image.open(p).convert('RGBA'); raw=np.array(im)
 full_labels,full_n=ndimage.label(raw[:,:,3]>8,structure=np.ones((3,3)))
 full_counts=np.bincount(full_labels.ravel());full_counts[0]=0
 biggest=np.argsort(full_counts)[-4:][::-1]
 if 'expressions' in p.name:
  cells=[]
  for ident in biggest:
   yy,xx=np.nonzero(full_labels==ident)
   cells.append({'area':int(full_counts[ident]),'box':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'center':[float(xx.mean()),float(yy.mean())]})
  keep=np.isin(full_labels,biggest)
  print(json.dumps({'ownership':p.name,'fourMainComponents':cells,'remainingStrong':int(((raw[:,:,3]>128)&~keep).sum())}))
 regions=[(0,0,im.width,im.height)] if 'fullbody' in p.name else [(0,0,im.width//2,im.height//2),(im.width//2,0,im.width,im.height//2),(0,im.height//2,im.width//2,im.height),(im.width//2,im.height//2,im.width,im.height)]
 for idx,box in enumerate(regions):
  x0,y0,x1,y1=box;a=raw[y0:y1,x0:x1,3]
  labels,n=ndimage.label(a>8,structure=np.ones((3,3)))
  counts=np.bincount(labels.ravel());counts[0]=0
  keep=labels==counts.argmax()
  strong=(a>128)
  results.append({'file':p.name,'cell':idx,'box':box,'nonzero':int((a>0).sum()),'mainComponent':int(keep.sum()),'removedNonzero':int(((a>0)&~keep).sum()),'removedStrong':int((strong&~keep).sum()),'borderAbove128':[int(strong[0].sum()),int(strong[:,-1].sum()),int(strong[-1].sum()),int(strong[:,0].sum())],'maxAlphaOutsideMain':int(a[~keep].max()) if (~keep).any() else 0})
print(json.dumps(results,ensure_ascii=False,indent=2))
