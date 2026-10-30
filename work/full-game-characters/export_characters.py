"""Deterministic alpha export and ownership slicing; never generates or paints art."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
import numpy as np
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'designs/characters/full-game'
OUT=ROOT/'assets/characters/full-game'
WORK=ROOT/'work/full-game-characters'
NOW=datetime.now(timezone.utc).isoformat()
IDENTITIES={'daotong':'金带道童','healer':'银发医师','master':'白眉老道','swordswoman':'黑发侠女'}
EXPRESSIONS=[('happy','开心'),('thinking','思考'),('surprised','惊讶'),('sad','沮丧')]
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(im):
 a=np.array(im.getchannel('A')); bb=im.getchannel('A').getbbox()
 return {'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA','alpha':{'range':[int(a.min()),int(a.max())],'transparentPixels':int((a==0).sum()),'opaquePixels':int((a==255).sum()),'semiTransparentPixels':int(((a>0)&(a<255)).sum()),'bbox':list(bb),'clearMargins':[bb[0],bb[1],im.width-bb[2],im.height-bb[3]],'borderPixelsAbove8':int((a[0]>8).sum()+(a[-1]>8).sum()+(a[:,0]>8).sum()+(a[:,-1]>8).sum())}}
def labels_of(im,n):
 rgba=np.array(im.convert('RGBA'));a=rgba[:,:,3]
 labels,_=ndimage.label(a>8,structure=np.ones((3,3)))
 counts=np.bincount(labels.ravel());counts[0]=0
 chosen=np.argsort(counts)[-n:]
 components=[]
 for lab in chosen:
  mask=labels==lab;yy,xx=np.nonzero(mask)
  box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
  components.append({'label':int(lab),'mask':mask,'box':box,'center':(float(xx.mean()),float(yy.mean())),'pixels':int(mask.sum())})
 owned=np.isin(labels,chosen)
 removedStrong=int(((a>128)&~owned).sum())
 if removedStrong:raise RuntimeError(f'Alpha export would discard {removedStrong} strong pixels')
 return rgba,components,{'alphaThreshold':8,'connectivity':8,'ownership':'connected subject components on entire source, never equal-grid crop','removedNonzeroPixels':int(((a>0)&~owned).sum()),'removedPixelsAbove128':removedStrong,'componentCount':n,'RGBRepainted':False}
def cut_component(rgba,component):
 data=rgba.copy();data[~component['mask']]=[0,0,0,0]
 promoted=int(((data[:,:,3]>=250)&(data[:,:,3]<255)).sum())
 data[:,:,3][data[:,:,3]>=250]=255
 box=component['box'];im=Image.fromarray(data).crop(box)
 return im,promoted
def downscale_rgba(im,size):
 # Pillow premultiplied alpha mode avoids dark fringes during downsampling.
 return im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
def previews(asset,im):
 paths=[]
 for key,color in [('light',(246,238,218,255)),('dark',(14,44,39,255))]:
  bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im)
  path=WORK/f"{asset['id']}-{key}-qa.png";bg.convert('RGB').save(path);paths.append(rel(path))
 return paths
assets=[];source_images=[];checks=[]
def derived(ident,role,im,source,operations,expression=None,pivot=None):
 ident_id=f'fullbody-{ident}' if role=='full_body' else f'expression-{ident}-{expression}'
 out=OUT/f'{ident_id}.png';im.save(out)
 parent=read(Path(str(source)+'.generation.json'))
 d={'schemaVersion':1,'file':rel(out),'sha256':sha(out),'exportedAt':NOW,**info(im),'derivedFrom':{'file':rel(source),'sha256':sha(source),'generationRecord':rel(Path(str(source)+'.generation.json'))},'operation':operations,'newModelGeneration':False,'actualModel':parent.get('actualModel'),'actualQuality':parent.get('actualQuality'),'nativeDimensions':parent.get('nativeDimensions',[parent.get('width'),parent.get('height')]),'prompt':parent.get('prompt'),'usage':{'identity':ident,'identityName':IDENTITIES[ident],'role':role,'expression':expression,'anchor':pivot or [0.5,0.5],'scaleMode':'uniform contain','nineSlice':None,'isAnimationFrame':False,'filter':'linear','alphaMode':'straight RGBA; premultiplied sampling recommended'},'userApproved':False,'clientIntegrated':False,'inspection':{'status':'pending_final_visual_qa'}}
 write(Path(str(out)+'.generation.json'),d)
 item={'id':ident_id,'name':IDENTITIES[ident]+('透明全身' if role=='full_body' else dict(EXPRESSIONS)[expression]+'表情'),'file':rel(out),'record':rel(Path(str(out)+'.generation.json')),'sha256':sha(out),**info(im),'role':role,'identity':ident,'expression':expression,'anchor':pivot or [0.5,0.5],'scaleMode':'uniform contain','stage':'pending_final_visual_qa'}
 item['qaPreviews']=previews(item,im);assets.append(item)
 checks.append({'id':ident_id,'file':rel(out),'sha256':sha(out),'status':'pending_final_visual_qa','pngIntegrity':'passed','alpha':'real_RGBA','borderPixelsAbove8':item['alpha']['borderPixelsAbove8'],'sourceHashVerified':True,'mechanicalOperations':operations,'qaPreviews':item['qaPreviews'],'visualInspectionCompleted':False,'unresolvedIssues':[],'userApproved':False})
 return item

# Reuse the existing inspected body, preserving its complete provenance chain.
existing=ROOT/'assets/characters/welcome-daotong.png'
existing_im=Image.open(existing).convert('RGBA');bb=existing_im.getchannel('A').getbbox()
existing_item={'id':'fullbody-daotong','name':'金带道童透明全身','file':rel(existing),'record':rel(Path(str(existing)+'.generation.json')),'sha256':sha(existing),**info(existing_im),'role':'full_body','identity':'daotong','expression':None,'anchor':[0.5,bb[3]/existing_im.height],'scaleMode':'uniform contain','stage':'pending_final_visual_qa','reusedExistingAsset':True,'newFileWritten':False}
existing_item['qaPreviews']=previews(existing_item,existing_im)
assets.append(existing_item)
checks.append({'id':'fullbody-daotong','file':rel(existing),'sha256':sha(existing),'status':'pending_final_visual_qa','pngIntegrity':'passed','alpha':'real_RGBA','borderPixelsAbove8':existing_item['alpha']['borderPixelsAbove8'],'sourceHashVerified':True,'mechanicalOperations':[{'operation':'reference existing accepted asset; no duplicate PNG or source record created','resampled':False}],'qaPreviews':existing_item['qaPreviews'],'visualInspectionCompleted':False,'unresolvedIssues':[],'userApproved':False})
for ident in ['healer','master','swordswoman']:
 source=SRC/f'{ident}-fullbody-native.png';source_images.append(rel(source))
 im=Image.open(source).convert('RGBA');rgba,comps,metrics=labels_of(im,1)
 cut,promoted=cut_component(rgba,comps[0]);canvas=Image.new('RGBA',(1536,1536))
 offset=((1536-cut.width)//2,(1536-cut.height)//2);canvas.paste(cut,offset)
 operations=[{'operation':'technical alpha sanitation',**metrics,'promoteAlpha250To255':True,'promotedPixels':promoted},{'operation':'crop transparent margins','sourceBox':list(comps[0]['box'])},{'operation':'transparent padding without resampling','canvas':[1536,1536],'offset':list(offset),'nativeDetailUpscaled':False}]
 derived(ident,'full_body',canvas,source,operations,pivot=[0.5,(offset[1]+cut.height)/1536])

for ident in IDENTITIES:
 source=SRC/f'{ident}-expressions-native.png';source_images.append(rel(source))
 im=Image.open(source).convert('RGBA');rgba,comps,metrics=labels_of(im,4)
 # Sort by semantic quadrant using component centroid; ownership may cross nominal 627-px grid.
 comps=sorted(comps,key=lambda c:(c['center'][1]>im.height/2,c['center'][0]>im.width/2))
 max_extent=max(max(c['box'][2]-c['box'][0],c['box'][3]-c['box'][1]) for c in comps)
 scale=min(1.0,448/max_extent)
 for (expr,_),component in zip(EXPRESSIONS,comps):
  cut,promoted=cut_component(rgba,component)
  size=(round(cut.width*scale),round(cut.height*scale))
  small=downscale_rgba(cut,size) if size!=cut.size else cut
  canvas=Image.new('RGBA',(512,512));offset=((512-small.width)//2,480-small.height);canvas.paste(small,offset)
  operations=[{'operation':'whole-source ownership slice',**metrics,'sourceBox':list(component['box']),'componentCentroid':list(component['center']),'sourcePixelsRetained':component['pixels'],'crossGridDetailsPreserved':True,'promoteAlpha250To255':True,'promotedPixels':promoted},{'operation':'uniform downsample with per-identity shared scale','sourceSize':list(cut.size),'outputContentSize':list(size),'scale':scale,'method':'premultiplied LANCZOS','nativeDetailUpscaled':False},{'operation':'transparent padding','canvas':[512,512],'offset':list(offset),'localSafeMargin':32}]
  derived(ident,'expression_avatar',canvas,source,operations,expression=expr)

# Review contact sheets are derived previews only, separate from runtime PNG counts.
font_path=Path('C:/Windows/Fonts/msyh.ttc')
font=ImageFont.truetype(str(font_path),24) if font_path.exists() else ImageFont.load_default()
for kind,group,cols,cell in [('bodies',[a for a in assets if a['role']=='full_body'],4,(384,440)),('expressions',[a for a in assets if a['role']=='expression_avatar'],4,(320,360))]:
 rows=(len(group)+cols-1)//cols
 for tone,color in [('light',(246,238,218)),('dark',(14,44,39))]:
  board=Image.new('RGB',(cols*cell[0],rows*cell[1]),color);draw=ImageDraw.Draw(board)
  for i,a in enumerate(group):
   src=Image.open(ROOT/a['file']).convert('RGBA');limit=(cell[0]-24,cell[1]-54)
   factor=min(limit[0]/src.width,limit[1]/src.height,1)
   small=downscale_rgba(src,(round(src.width*factor),round(src.height*factor)))
   x=(i%cols)*cell[0]+(cell[0]-small.width)//2;y=(i//cols)*cell[1]+12
   board.paste(small,(x,y),small)
   draw.text(((i%cols)*cell[0]+12,(i//cols)*cell[1]+cell[1]-36),a['name'],font=font,fill=(16,59,48) if tone=='light' else (246,238,218))
  preview_path=OUT/f'preview-{kind}-{tone}.png';board.save(preview_path)
  preview_record={'schemaVersion':1,'file':rel(preview_path),'sha256':sha(preview_path),'exportedAt':NOW,'width':board.width,'height':board.height,'format':'PNG','mode':'RGB','newModelGeneration':False,'tool':'Pillow deterministic contact-sheet layout','route':'local_derivative','actualModel':None,'actualQuality':None,'unverifiedReason':'This contact sheet is not an AI generation. Follow each derivedFrom source record for actual model/quality evidence.','derivedFrom':[{'file':a['file'],'sha256':a['sha256'],'generationRecord':a['record']} for a in group],'operation':[{'operation':'premultiplied-alpha uniform thumbnail downsample and grid layout','columns':cols,'rows':rows,'cellSize':list(cell),'contentMaxSize':[cell[0]-24,cell[1]-54],'nativeDetailUpscaled':False},{'operation':'composite onto opaque inspection background','backgroundRgb':list(color),'tone':tone},{'operation':'draw labels from manifest names','font':'Microsoft YaHei; system msyh.ttc or Pillow fallback','fontSize':24}],'purpose':'retained final visual QA/design contact sheet, not runtime asset','userApproved':False,'clientIntegrated':False}
  write(Path(str(preview_path)+'.generation.json'),preview_record)

manifest={'schemaVersion':2,'generatedAt':NOW,'scope':'four distinct full-body characters and sixteen emotional portrait sprites, static art','root':str(ROOT),'status':'pending_final_visual_qa','expectedAssetCount':20,'actualAssetCount':len(assets),'counts':{'fullBodies':4,'expressionAvatars':16,'newNativeSources':7,'reusedBodies':1,'newRuntimePngFiles':19},'assets':assets,'sourceImages':source_images,'reusedAssets':[rel(existing)],'previewImages':[f'assets/characters/full-game/preview-{kind}-{tone}.png' for kind in ['bodies','expressions'] for tone in ['light','dark']],'qaReport':'assets/characters/full-game/qa.json','exportScript':'work/full-game-characters/export_characters.py','sourceRegistrationScript':'work/full-game-characters/register_native.py','actualModel':None,'actualQuality':None,'userApproved':False,'clientIntegrated':False,'notes':['Full-body canvases are 1536 square with native detail unscaled; transparency padding does not increase source detail.','Expression avatars are 512 square downsampled from ownership-extracted native sheet components; four emotional states are static portraits, not motion animation.','Existing avatar identities remain unchanged.','Builtin generation route; model and quality parameters unavailable and actual values unconfirmed.']}
write(OUT/'manifest.json',manifest)
write(OUT/'qa.json',{'schemaVersion':1,'status':'pending_final_visual_qa','checks':checks,'scopeComplete':len(assets)==20,'userApproved':False,'pending':['Actual view_image review of final light and dark contact sheets and 512-pixel expression silhouettes']})
print(json.dumps({'assets':len(assets),'counts':manifest['counts'],'sourceImages':source_images,'previews':manifest['previewImages'],'qaStatus':'pending_final_visual_qa'},ensure_ascii=False))
