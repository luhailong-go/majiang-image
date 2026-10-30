from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime,timezone,timedelta
import json, hashlib, math
from analyze_alpha import clean,components,np
R=Path(r'D:\work\majiang-image')
SRC=R/'designs/ui/full-game/component-sources';OUT=R/'assets/ui/full-game/components';QA=R/'work/full-game-ui/components/qa'
NOW=datetime.now(timezone(timedelta(hours=-4))).isoformat()
def rel(p):return p.relative_to(R).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def savej(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stats(im):
 a=np.asarray(im.getchannel('A'));b=im.getchannel('A').getbbox()
 return {'range':[int(a.min()),int(a.max())],'fullyTransparent':int((a==0).sum()),'semiTransparent':int(((a>0)&(a<255)).sum()),'opaque':int((a==255).sum()),'bbox':list(b),'edgeAlphaMax':int(max(a[0,:].max(),a[-1,:].max(),a[:,0].max(),a[:,-1].max())),'minimumTransparentMargin':min(b[0],b[1],im.width-b[2],im.height-b[3]),'zeroRgbUnderZeroAlpha':bool((np.asarray(im)[:,:,:3][a==0]==0).all())}
specs=[
 ('reward-cosmetic-cards-v1','reward-card-default','奖励卡·默认','rewardCard','default',(267,200)),
 ('reward-cosmetic-cards-v1','reward-card-claimable','奖励卡·待领取','rewardCard','claimable',(769.5,198)),
 ('reward-cosmetic-cards-v1','reward-card-claimed','奖励卡·已领取','rewardCard','claimed',(1270,200.5)),
 ('reward-cosmetic-cards-v1','cosmetic-card-unselected','装扮卡·未选中','cosmeticCard','unselected',(278.5,655.5)),
 ('reward-cosmetic-cards-v1','cosmetic-card-selected','装扮卡·选中','cosmeticCard','selected',(768.5,654)),
 ('reward-cosmetic-cards-v1','cosmetic-card-in-use','装扮卡·使用中','cosmeticCard','inUse',(1257,657.5)),
 ('achievement-rank-badges-v1','achievement-frame-locked','成就框·未解锁','achievement','locked',(409.5,275)),
 ('achievement-rank-badges-v1','achievement-frame-unlocked','成就框·已解锁','achievement','unlocked',(1121,276)),
 ('achievement-rank-badges-v1','rank-marker-gold','排行·金','rank','gold',(268.5,752.5)),
 ('achievement-rank-badges-v1','rank-marker-silver','排行·银','rank','silver',(769,753)),
 ('achievement-rank-badges-v1','rank-marker-bronze','排行·铜','rank','bronze',(1271,755)),
 ('inventory-slots-v1','item-slot-default','物品槽·默认','itemSlot','default',(348,314.5)),
 ('inventory-slots-v1','item-slot-selected','物品槽·选中','itemSlot','selected',(907.5,314.5)),
 ('inventory-slots-v1','item-slot-disabled','物品槽·禁用','itemSlot','disabled',(348,924)),
 ('inventory-slots-v1','item-slot-new','物品槽·新获得','itemSlot','new',(907.5,924)),
 ('tutorial-reward-icons-v1','tutorial-spotlight-ring','教程·聚光圆环','spotlight','default',(251,297)),
 ('tutorial-reward-icons-v1','tutorial-arrow','教程·方向箭头','arrow','default',(678.5,309.5)),
 ('tutorial-reward-icons-v1','tutorial-step-marker','教程·步骤标记','step','default',(1045.5,314)),
 ('tutorial-reward-icons-v1','tutorial-tap-hand','教程·点击手势','tap','default',(1385,308.5)),
 ('tutorial-reward-icons-v1','tutorial-focus-frame','教程·焦点角框','focus','default',(233.5,752.5)),
 ('tutorial-reward-icons-v1','item-voucher','道具券','voucher','default',(655,768)),
 ('tutorial-reward-icons-v1','gift-box','奖励礼盒','gift','default',(1052.5,771.5)),
]
cache={}
for src in sorted(set(s[0] for s in specs)):
 p=SRC/(src+'.png');raw=Image.open(p).convert('RGBA');im,log=clean(raw);cs=components(np.asarray(im.getchannel('A')))
 assert log['removedAlphaAtLeast128']==0
 cache[src]={'path':p,'image':im,'log':log,'components':cs,'size':raw.size,'used':set()}
prepared=[];extents={}
for src,name,title,family,state,center in specs:
 d=cache[src];cx,cy=center
 # Select one fully connected sprite by nearest alpha bounding-box center. This avoids cutting overlapping row extents.
 ci=min(range(len(d['components'])),key=lambda i:((sum(d['components'][i]['bbox'][::2])/2-cx)**2+(sum(d['components'][i]['bbox'][1::2])/2-cy)**2))
 assert ci not in d['used'];d['used'].add(ci);c=d['components'][ci];b=c['bbox']
 assert 0<b[0]<b[2]<d['size'][0] and 0<b[1]<b[3]<d['size'][1]
 ex=max(cx-b[0],b[2]-cx);ey=max(cy-b[1],b[3]-cy)
 prior=extents.get(family,(0,0));extents[family]=(max(ex,prior[0]),max(ey,prior[1]))
 prepared.append({'source':src,'id':name,'name':title,'family':family,'state':state,'center':center,'component':c})
for d in cache.values():assert len(d['used'])==len(d['components'])
assets=[]
for item in prepared:
 d=cache[item['source']];c=item['component'];b=c['bbox'];cx,cy=item['center'];family=item['family']
 w,h=[2*math.ceil(e)+32 for e in extents[family]]
 ox=round(w/2-(cx-b[0]));oy=round(h/2-(cy-b[1]))
 # Mask solely selects the identified connected sprite; no painting, synthesis or resizing.
 region=np.array(d['image'].crop(b));mask=np.zeros(region.shape[:2],bool)
 for y,x0,x1 in c['spans']:mask[y-b[1],x0-b[0]:x1-b[0]]=True
 region[~mask]=0;trim=Image.fromarray(region);out=Image.new('RGBA',(w,h));out.paste(trim,(ox,oy))
 p=OUT/(item['id']+'.png');out.save(p);alpha=stats(out);assert alpha['minimumTransparentMargin']>=15 and alpha['edgeAlphaMax']==0
 assert int((np.asarray(out)[:,:,3]>=128).sum())==c['strong']
 padding=[ox,oy,w-ox-trim.width,h-oy-trim.height]
 policy={'mode':'uniform_scale_only','stretchAxes':[],'uniformScaleAllowed':True,'preserveAspect':True,'reason':'Keep rounded clouds, beads, crown, ribbon and pointer shapes undistorted; no nine-slice has been approved.'}
 rec={'schemaVersion':2,'file':rel(p),'sha256':sha(p),'exportedAt':NOW,'kind':'derived_ui_asset','generatedByModel':False,'actualModel':None,'actualQuality':None,'unverifiedReason':'Source generated through builtin image_gen; host did not disclose verifiable model or quality.','width':w,'height':h,'mode':'RGBA','format':'PNG','nativeSourceDimensions':{'width':d['size'][0],'height':d['size'][1]},'derivedFrom':{'file':rel(d['path']),'sha256':sha(d['path']),'record':rel(d['path'])+'.generation.json'},'operation':'mechanical native connected-sprite selection + low-alpha cleanup + crop + family-aligned transparent padding; no resampling','crop':b,'componentIsolation':{'method':'8-connected alpha component; all components in each atlas exported once','selectedStrongPixels':c['strong'],'selectedAlphaPixels':c['area']},'alphaCleanup':d['log'],'transparentPadding':padding,'placement':{'x':ox,'y':oy,'familyCanvas':[w,h],'sourceContentCenter':[cx,cy]},'anchor':{'x':0.5,'y':0.5},'resampled':False,'nineSlice':None,'resizePolicy':policy,'alpha':alpha,'family':family,'state':item['state'],'dynamicText':'All labels, ranks, quantities, achievement icons and step numbers are separate client elements.','inspection':{'status':'technical_passed_visual_pending','issues':[]},'productionAccepted':False,'clientIntegrated':False}
 rp=p.with_name(p.name+'.generation.json');savej(rp,rec)
 a={k:rec[k] for k in ['file','sha256','width','height','mode','anchor','nineSlice','resizePolicy','alpha','family','state']};a.update({'id':item['id'],'name':item['name'],'record':rel(rp),'status':'technical_passed_visual_pending','productionAccepted':False});assets.append(a)
old=json.loads((R/'assets/ui/manifest.json').read_text(encoding='utf-8-sig'))
reuse_ids=['window-frame','title-plaque','content-card','button-primary-normal','button-primary-pressed','button-primary-selected','button-primary-disabled','button-secondary-normal','button-secondary-pressed','button-secondary-selected','button-secondary-disabled','tab-selected','tab-normal','input-field','icon-search','icon-close','icon-back','icon-confirm','icon-lock','tooltip-bubble','modal-shade','unread-badge','loading-ring']
reused=[{'id':a['id'],'file':a['file'],'record':a['record'],'sha256':a['sha256'],'sourceManifest':'assets/ui/manifest.json','status':'reused_existing_passed'} for a in old['assets'] if a['id'] in reuse_ids]
assert len(reused)==len(reuse_ids)
families={}
for a in assets:
 f=families.setdefault(a['family'],{'canvas':[a['width'],a['height']],'anchor':a['anchor'],'resizePolicy':a['resizePolicy'],'states':{}})
 assert f['canvas']==[a['width'],a['height']];f['states'][a['state']]=a['id']
manifest={'schemaVersion':2,'generatedAt':NOW,'scope':'full_game_v2_additional_ui_components','status':'technical_passed_visual_pending','newAssetCount':len(assets),'actualModel':None,'actualQuality':None,'userApproved':False,'clientIntegrated':False,'assets':assets,'stateFamilies':families,'reusedAssets':reused,'sources':[rel(d['path']) for d in cache.values()],'compositionFile':'assets/ui/full-game/components/compositions.json','notes':['Native source crops are never enlarged.','All families use equal canvases and center anchors. Small hand-painted outline variations remain between state skins.','No slice in this batch permits anisotropic stretching.','Actual model and quality are unconfirmed null values.']}
savej(OUT/'manifest.json',manifest)
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',15)
for start,end,label in [(0,11,'cards-badges'),(11,22,'slots-tutorial')]:
 subset=assets[start:end];cols=4;cw=320;ch=320;rows=math.ceil(len(subset)/cols)
 for mode,bg in [('light',(245,237,216)),('dark',(18,48,40))]:
  sheet=Image.new('RGB',(cols*cw,rows*ch),bg);draw=ImageDraw.Draw(sheet)
  for i,a in enumerate(subset):
   im=Image.open(R/a['file']).convert('RGBA');im.thumbnail((cw-32,ch-65));x=i%cols*cw+(cw-im.width)//2;y=i//cols*ch+10
   sheet.paste(im,(x,y),im);color=(25,60,45) if mode=='light' else (245,237,216)
   draw.text((i%cols*cw+8,i//cols*ch+ch-46),a['id'],fill=color,font=font)
   draw.text((i%cols*cw+8,i//cols*ch+ch-24),str(a['width'])+' x '+str(a['height']),fill=color,font=font)
  sheet.save(QA/(label+'-'+mode+'.png'))
print(json.dumps({'assets':len(assets),'families':len(families),'reused':len(reused),'allStrongForegroundPreserved':True,'minimumMargin':min(a['alpha']['minimumTransparentMargin'] for a in assets),'sizes':{k:v['canvas'] for k,v in families.items()}},ensure_ascii=False))
