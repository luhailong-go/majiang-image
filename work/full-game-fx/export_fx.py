from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil,sys
from scipy import ndimage
R=Path(r'D:\work\majiang-image');A=R/'assets/fx/full-game';D=R/'designs/fx/full-game';W=R/'work/full-game-fx'
sys.path.insert(0,r'C:\Users\luyua\.codex\skills\generate2dsprite\scripts')
from forge_core import alpha_hygiene
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
assets=[];timelines={};sources=[];pipeline=[]
def record(out,source,title,kind,operation,extra=None):
 im=Image.open(out).convert('RGBA');im,final_hygiene=alpha_hygiene(np.asarray(im),mode='both',floor=4);im.save(out);operation['finalAlphaHygiene']=final_hygiene;a=np.asarray(im.getchannel('A'));bb=im.getchannel('A').getbbox()
 srcs=[source] if isinstance(source,Path) else source
 original=[json.loads(Path(str(s)+'.generation.json').read_text(encoding='utf-8')) for s in srcs]
 rr={'schemaVersion':2,'file':rel(out),'title':title,'sha256':sha(out),'generatedAt':now,'derivedAt':now,'tool':'generate2dsprite.py process / Pillow deterministic export','route':'derivative_of_builtin_host_image','art_source':'host_image_derivative','actualModel':None,'actualQuality':None,'unverifiedReason':'原始内置生成未披露可核实型号/质量；本文件是切片或文字合成，不是新模型生成。','width':im.width,'height':im.height,'format':'PNG','mode':'RGBA','nativeDimensions':original[0]['nativeDimensions'],'configSnapshot':original[0]['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'derivedFrom':[{'file':rel(s),'sha256':sha(s),'record':rel(Path(str(s)+'.generation.json'))} for s in srcs],'operation':operation,'alpha':{'range':[int(a.min()),int(a.max())],'transparentPixels':int((a==0).sum()),'opaquePixels':int((a==255).sum()),'semiTransparentPixels':int(((a>0)&(a<255)).sum()),'bboxNonzero':bb,'corners':[int(a[0,0]),int(a[0,-1]),int(a[-1,0]),int(a[-1,-1])]},'inspection':{'visualStatus':'pending','issues':[]},'status':{'productionAccepted':False,'userApproved':False,'clientIntegrated':False},'delivery':{'localOnly':True,'uploaded':False}}
 if extra:rr.update(extra)
 dump(Path(str(out)+'.generation.json'),rr)
 item={'id':out.stem,'name':title,'file':rel(out),'record':rel(Path(str(out)+'.generation.json')),'sha256':rr['sha256'],'width':im.width,'height':im.height,'mode':'RGBA','kind':kind,'anchorPx':[im.width//2,im.height//2],'scaleMode':'uniform_scale_only','nineSlice':None,'status':'pending_visual_qa'}
 assets.append(item);return item
def resize(im,size):return im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
def hygiene(im):
 arr,report=alpha_hygiene(np.asarray(im.convert('RGBA')),mode='both',floor=4)
 return arr if isinstance(arr,Image.Image) else Image.fromarray(np.asarray(arr,dtype=np.uint8)),report

cfg=[('draw-focus','draw-focus','摸牌聚光',[5,5,7,7],False),('discard-impact','discard-impact-refined','出牌落光',[4,4,5,7],False),('player-ring','player-ring','当前玩家光环',[10,10,10,10],True),('hu-burst','hu-burst','胡牌金云',[7,5,8,12],False),('victory-confetti','victory-confetti','胜利彩纸',[8,8,10,14],False),('reward-stars','reward-stars','奖励星辉',[6,6,9,15],False)]
frames=[];clips={}
for slug,source_slug,name,ticks,loop in cfg:
 source=D/f'{source_slug}-v1.png';source_record=Path(str(source)+'.generation.json');sources.append(rel(source))
 pp=W/f'process-{source_slug}/pipeline-meta.json';meta=json.loads(pp.read_text(encoding='utf-8'));assert meta['qa']['status']=='pass'
 pipeline.append({'effect':slug,'file':rel(pp),'sha256':sha(pp),'geometry':meta['geometry'],'hygiene':meta['hygiene'],'qa':meta['qa']})
 paths=[]
 for i in range(4):
  src=W/f'process-{source_slug}/sheet-{i+1}.png';out=A/f'frames/{slug}-{i:02}.png';out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out)
  operation={'type':'native_alpha_slice_registered_downsample','sourceBox':meta['frames'][i]['source_box'],'sourceAnchorPx':meta['geometry']['registration_anchor'],'sourceToOutputScale':meta['geometry']['scale'],'outputAnchorPx':[256,256],'globalOffsetPx':meta['frames'][i]['offset_px'],'resampler':'premultiplied_lanczos','alphaHygiene':meta['hygiene'],'pixelsRegenerated':False,'sourceDimensions':[1254,1254],'outputDimensions':[512,512],'pipelineReport':rel(pp),'pipelineFrame':i}
  # Correct the generator's within-cell center drift using the visible effect core,
  # not a per-frame bbox fit. No relative scale, painting or timing is changed.
  centers={'draw-focus':[(315,324),(319,325),(314,306),(320,317)],'discard-impact':[(319,374),(297,372),(322,322),(322,314)],'hu-burst':[(335,380),(311,383),(335,316),(316,311)]}
  shift=(0,0);center_method=None
  if slug in centers:
   cx,cy=centers[slug][i];scale=meta['geometry']['scale'];shift=(round((313.5-cx)*scale),round((313.5-cy)*scale));center_method={'method':'artist_declared_star_or_ripple_core_in_source_cell','sourceCorePx':[cx,cy]}
  elif slug=='player-ring':
   a=np.asarray(Image.open(out).getchannel('A'));solid=a>127;holes=ndimage.binary_fill_holes(solid)&~solid;labels,n=ndimage.label(holes);areas=np.bincount(labels.ravel());areas[0]=0
   assert areas.max()>1000
   yy,xx=np.where(labels==int(areas.argmax()));cx=(int(xx.min())+int(xx.max())+1)/2;cy=(int(yy.min())+int(yy.max())+1)/2;shift=(round(256-cx),round(256-cy));center_method={'method':'center_of_enclosed_avatar_hole_not_outer_glow_bbox','unadjustedHoleCenterPx':[cx,cy]}
  if center_method:
   im=Image.open(out).convert('RGBA');fixed=Image.new('RGBA',im.size);fixed.alpha_composite(im,shift);fixed.save(out);operation['centerDriftCorrection']={**center_method,'translationOutputPx':list(shift),'scaleUnchanged':True,'blankPaddingOnly':True}
  record(out,source,f'{name} 第{i+1}阶段','animation_frame',operation,{'frameIndex':i,'phase':['onset','expansion','peak','dissipation'][i] if not loop else ['top','right','bottom','left'][i]})
  paths.append(rel(out));frames.append(f'frames/{slug}-{i:02}.png')
 start=len(frames)-4
 clips[slug]={'frames':list(range(start,start+4)),'ticks':ticks,'loop_policy':'cycle' if loop else 'oneshot','role':'fx','events':[{'at':0,'name':'in'},{'at':2,'name':'impact'},{'at':3,'name':'end'}] if not loop else []}
 timelines[slug]={'name':name,'artMethod':'generated_phase_sheet','frameFiles':paths,'frameTicks':ticks,'tickHz':60,'loop':loop,'onComplete':'repeat' if loop else 'hide','anchorPx':[256,256],'canvasPx':[512,512],'blendBetweenPhasesMs':33,'finalFadeOutMs':0 if loop else 80,'clientIntegrated':False,'note':'Four generated distinct phase paintings; alpha conditioning and one common sheet scale. Optional runtime crossfade is interpolation, not additional generated art.'}

# Keep the generated plaque as a separate reusable art layer. Text is typeset, never claimed as generated.
source=D/'callout-plate-v1.png';sources.append(rel(source));raw=Image.open(source).convert('RGBA');clean,h=hygiene(raw);base=resize(clean,(768,512));base_file=A/'callout-base.png';base.save(base_file)
record(base_file,source,'麻将操作提示空底','callout_blank',{'type':'native_alpha_hygiene_downsample','sourceBox':[0,0,1536,1024],'sourceToOutputScale':0.5,'resampler':'premultiplied_lanczos','alphaHygiene':h,'textGenerated':False})
font_path=Path('C:/Windows/Fonts/simkai.ttf')
labels=[('chi','吃'),('peng','碰'),('gang','杠'),('hu','胡'),('ting','听'),('self-draw','自摸'),('draw','流局'),('victory','胜利')]
for slug,label in labels:
 im=base.copy();draw=ImageDraw.Draw(im);font=ImageFont.truetype(str(font_path),118 if len(label)==1 else 105)
 box=draw.textbbox((0,0),label,font=font,stroke_width=2);x=(768-(box[2]-box[0]))/2-box[0];y=256-(box[3]-box[1])/2-box[1]
 color='#AC3425' if slug in ['hu','self-draw','victory'] else '#174B3C'
 draw.text((x,y+2),label,font=font,fill='#BCA16A',stroke_width=2,stroke_fill='#BCA16A')
 draw.text((x,y),label,font=font,fill=color,stroke_width=1,stroke_fill='#E0C282')
 out=A/f'callouts/{slug}.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
 record(out,source,f'操作提示：{label}','callout_label',{'type':'generated_plaque_plus_deterministic_typesetting','baseFile':rel(base_file),'baseSha256':sha(base_file),'text':label,'fontFamily':'KaiTi / 楷体','fontFileLocal':str(font_path),'fontSha256':sha(font_path),'fontDistributed':False,'fontSizePx':font.size,'fill':color,'stroke':'warm gold 1px','targetCenterPx':[384,256],'sourceToOutputScale':0.5,'AIgeneratedText':False}, {'exactText':label})

source=D/'settlement-decor-v1.png';sources.append(rel(source));raw=Image.open(source).convert('RGBA')
for i,(slug,title) in enumerate([('defeat','失败结算无字装饰'),('draw','平局结算无字装饰')]):
 box=[i*887,0,(i+1)*887,887];im,h=hygiene(raw.crop(box));im=resize(im,(440,440));outim=Image.new('RGBA',(512,512));outim.alpha_composite(im,(36,36));out=A/f'settlement-{slug}.png';outim.save(out)
 record(out,source,title,'settlement_decoration',{'type':'native_alpha_slice_hygiene_downsample_pad','sourceBox':box,'sourceToOutputScale':440/887,'resampler':'premultiplied_lanczos','alphaHygiene':h,'padOffsetPx':[36,36],'textIncluded':False})

dump(A/'clips-input.json',{'schema':'generate2dsprite.animation_clips.v2','frames':frames,'anchor_px':[256,256],'clips':clips,'states':{slug:slug for slug,*_ in cfg},'sampling':'linear','pixel_art':False,'art_source':'host_image','placeholder':False})
dump(A/'timelines.json',{'schemaVersion':1,'generatedAt':now,'clips':timelines,'timingNote':'Integer60Hz ticks. Runtime crossfade/final opacity is optional sprite interpolation over these four phase images; no video/rig/extra native frames are claimed.','clientIntegrated':False})
dump(A/'processing-receipts.json',{'schemaVersion':1,'reports':pipeline,'rawSheetQCNote':'raw safe_frame and faint_specks advisories are superseded by registered padding and alpha_hygiene both; all selected raw sheets have zero cross-cell/visible crossings and zero sheet-edge contact. See work/full-game-fx/spill-*/sheet-qc.json.'})
dump(A/'manifest.json',{'schemaVersion':2,'status':'pending_visual_qa','scope':'Full game Mahjong FX:8 callouts,24 generated key-phase frames,2 textless result ornaments,1 reusable blank plaque','assetCount':len(assets),'assets':assets,'sourceImages':sources,'actualModel':None,'actualQuality':None,'art_source':'host_image_and_derived_typesetting','clientIntegrated':False,'userApproved':False,'clips':'assets/fx/full-game/timelines.json','clipInput':'assets/fx/full-game/clips-input.json','engineExport':None,'qaReport':'assets/fx/full-game/qa.json','processingReceipts':'assets/fx/full-game/processing-receipts.json','previews':[]})

# Deep/light visual sheets show runtime pixels, not raw RGB under nearly transparent alpha.
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
def sheet(kind,outname,items,cols,w,h,thumb):
 rows=(len(items)+cols-1)//cols;sheet=Image.new('RGB',(cols*w,rows*h),'#EEE7D6');d=ImageDraw.Draw(sheet)
 for j,item in enumerate(items):
  x=(j%cols)*w;y=(j//cols)*h;d.text((x+10,y+6),item['name'],font=font,fill='#163D32');im=Image.open(R/item['file']).convert('RGBA');im.thumbnail(thumb,Image.Resampling.LANCZOS)
  for k,bgcolor in enumerate(['#FFF9E9','#123F35']):
   bg=Image.new('RGBA',(w//2,h-36),bgcolor);bg.alpha_composite(im,((w//2-im.width)//2,(h-36-im.height)//2));sheet.paste(bg.convert('RGB'),(x+k*w//2,y+32))
 out=A/f'previews/{outname}.png';out.parent.mkdir(parents=True,exist_ok=True);sheet.save(out)
 return {'file':rel(out),'sha256':sha(out),'purpose':kind,'derivedFrom':[{'file':i['file'],'sha256':i['sha256']} for i in items]}
previews=[sheet('24 FX phase frame alpha review','frames-alpha',[a for a in assets if a['kind']=='animation_frame'],4,512,300,(248,248)),sheet('8 Chinese callouts and3 blanks/result ornaments alpha review','callouts-alpha',[a for a in assets if a['kind']!='animation_frame'],2,768,300,(370,250))]
for preview in previews:
 im=Image.open(R/preview['file']);dump(Path(str(R/preview['file'])+'.generation.json'),{'schemaVersion':2,'file':preview['file'],'sha256':preview['sha256'],'derivedAt':now,'tool':'Pillow contact sheet','route':'deterministic_derivative','actualModel':None,'actualQuality':None,'width':im.width,'height':im.height,'mode':im.mode,'format':'PNG','derivedFrom':preview['derivedFrom'],'operation':'thumbnail downsample and alpha-composite runtime assets over light/dark review backgrounds; no new art generated','inspection':{'visualStatus':'pending'}})
manifest=json.loads((A/'manifest.json').read_text(encoding='utf-8'));manifest['previews']=previews;dump(A/'manifest.json',manifest)
print(json.dumps({'assetCount':len(assets),'frames':len(frames),'clips':len(clips),'previews':[p['file'] for p in previews]},ensure_ascii=False))
