import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
from collections import deque
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/ui/production-v3/gameplay'
SRC=ROOT/'designs/ui/production-v3/gameplay/gameplay-state-atlas-native.png'
PROMPT='prompts/production-v3/gameplay/gameplay-state-atlas.txt'
CONFIG=json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig'))
now=datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
image=Image.open(SRC).convert('RGBA')
record={
 'schemaVersion':1,'file':rel(SRC),'sha256':sha(SRC),'generatedAt':now,'width':image.width,'height':image.height,'format':'RGBA PNG',
 'tool':'image_gen.imagegen','route':'builtin','callId':None,'resultEvidence':{'hostPath':r'C:\Users\luyua\.codex\generated_images\01a1773e-0bce-79e3-9860-5aa2d27a397d\exec-0d839809-a09b-41ce-b02e-204cb79d8d05.png'},
 'configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None,'transparent_background':True},
 'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin entry has no model/quality selector and returned no verified version or quality metadata.',
 'prompt':PROMPT,'references':[{'file':f,'sha256':sha(ROOT/f),'role':'actual attached style reference'} for f in ['references/style/01-mail-event.png','references/style/team-ui-v2.png']],
 'operation':'native six-skin atlas generation, not a full-screen runtime UI','checks':{'visual':'inspected raw six intended shapes; final alpha checked on sliced assets','alpha':'RGBA native, disconnected low-alpha peripheral pixels removed only in derived exports'}
}
SRC.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
specs=[
 ('candidate-panel','多候选容器',(0,70,740,450),(520,207)),
 ('ready-hand-panel','听牌提示容器',(740,90,1254,450),(350,202)),
 ('candidate-selected-outline','候选组选中外框',(0,480,740,870),(210,96)),
 ('illegal-tile-badge','不可出牌角标',(800,490,1210,860),(28,28)),
 ('discard-pointer','最后弃牌指针',(200,900,530,1220),(28,31)),
 ('ready-hand-badge','听牌状态底章',(800,880,1190,1220),(40,40)),
]
assets=[]
for aid,name,box,display in specs:
 crop=image.crop(box)
 a=crop.getchannel('A'); w,h=crop.size
 b=a.point(lambda v:255 if v>=64 else 0)
 raw=bytearray(b.tobytes()); seen=bytearray(w*h); largest=[]
 for p,val in enumerate(raw):
  if not val or seen[p]: continue
  seen[p]=1; q=deque([p]); comp=[]
  while q:
   i=q.popleft(); comp.append(i); x=i%w; y=i//w
   for j in ((i-1 if x else -1),(i+1 if x+1<w else -1),(i-w if y else -1),(i+w if y+1<h else -1)):
    if j>=0 and raw[j] and not seen[j]: seen[j]=1; q.append(j)
  if len(comp)>len(largest): largest=comp
 maskbytes=bytearray(w*h)
 for p in largest: maskbytes[p]=255
 mask=Image.frombytes('L',(w,h),bytes(maskbytes)).filter(ImageFilter.MaxFilter(5))
 import PIL.ImageChops
 a=PIL.ImageChops.multiply(a,mask)
 crop.putalpha(a)
 bb=a.getbbox()
 # Keep exact native pixel detail, padded only, never upscale or resample these sprites.
 cut=crop.crop(bb)
 out=Image.new('RGBA',(cut.width+32,cut.height+32),(0,0,0,0)); out.alpha_composite(cut,(16,16))
 pixels=out.load()
 for y in range(out.height):
  for x in range(out.width):
   if pixels[x,y][3]==0: pixels[x,y]=(0,0,0,0)
 file=OUT/(aid+'.png'); out.save(file)
 absbox=[box[0]+bb[0],box[1]+bb[1],bb[2]-bb[0],bb[3]-bb[1]]
 item={'id':aid,'name':name,'file':rel(file),'record':rel(file)+'.generation.json','sha256':sha(file),'width':out.width,'height':out.height,'mode':'RGBA','anchor':[0.5,0.5],'nineSlice':None,'resizePolicy':'uniform_scale_only','recommendedDisplay':list(display),'nativeCrop':absbox,'contentBounds':[16,16,cut.width,cut.height],'upscaled':False,'status':'pending_visual','productionAccepted':False}
 if aid=='candidate-panel': item['contentRectNormalized']=[.105,.27,.79,.54]
 if aid=='ready-hand-panel': item['contentRectNormalized']=[.12,.25,.76,.49]
 if aid=='candidate-selected-outline': item['transparentWindowNormalized']=[.15,.20,.70,.60]
 derived={'schemaVersion':1,**item,'generatedAt':now,'tool':'Pillow deterministic crop/alpha export','route':'derived','actualModel':None,'actualQuality':None,'configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None},'prompt':PROMPT,'references':record['references'],'derivedFrom':[{'file':rel(SRC),'sha256':sha(SRC),'record':rel(SRC)+'.generation.json'}],'operation':{'type':'native_atlas_slice','sourceCropXYWH':absbox,'alphaCleanup':'Keep largest connected component at alpha>=64 within assigned cell, dilate support by 2 source pixels, multiply original alpha by support; preserve interior transparency; zero RGB under zero Alpha.','paddingPx':16,'resampling':'none','nativeDetailSize':[cut.width,cut.height],'outputSize':[out.width,out.height],'upscaled':False},'checks':{'visual':'pending','alpha':'pending'}}
 file.with_suffix('.png.generation.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 assets.append(item)
manifest={'schemaVersion':1,'domain':'production-v3-gameplay','generatedAt':now,'status':'pending_visual','scope':'Six independent skins and explicit compositions reusing accepted tile art; no new rules','actualModel':None,'actualQuality':None,'assets':assets,'source':{'file':rel(SRC),'sha256':sha(SRC),'record':rel(SRC)+'.generation.json','nativeSize':list(image.size)},'runtimeCompositions':'assets/ui/production-v3/gameplay/runtime-compositions.json','qa':'assets/ui/production-v3/gameplay/qa.json','audit':'docs/PRODUCTION_ART_GAPS_GAMEPLAY_20261028.md','clientIntegrated':False,'userApproved':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native':image.size,'exports':[{k:a[k] for k in ['id','width','height','nativeCrop']} for a in assets]},ensure_ascii=False))

