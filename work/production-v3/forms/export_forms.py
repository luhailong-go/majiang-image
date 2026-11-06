"""Reproducible alpha extraction and native-UI composition QA; no AI drawing."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math
import numpy as np
from scipy import ndimage as nd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'assets/ui/production-v3/forms'
DES = ROOT / 'designs/ui/production-v3/forms'
OUT.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()

def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def dependency(p):
    d={'file':rel(p),'sha256':sha(p)}
    if Path(str(p)+'.generation.json').exists(): d['record']=rel(Path(str(p)+'.generation.json'))
    return d
def alpha_stats(im):
    a=np.array(im)[:,:,3]
    return {'range':[int(a.min()),int(a.max())], 'bbox':list(im.getbbox()),
            'fullyTransparent':int((a==0).sum()),'semiTransparent':int(((a>0)&(a<255)).sum()),
            'opaque':int((a==255).sum()),'corners':[int(a[0,0]),int(a[0,-1]),int(a[-1,0]),int(a[-1,-1])]}

# [L,T,R,B) are manual object-separated regions. Top-left motion object crosses
# the nominal grid line; the 665 boundary preserves the complete cloud rim.
SPECS=[
 ('input-focus-overlay','forms-list-atlas',(0,0,627,627),(640,192),(80,44,80,44),'horizontal_nine_slice_only'),
 ('input-error-overlay','forms-list-atlas',(627,0,1254,627),(640,192),(80,44,80,44),'horizontal_nine_slice_only'),
 ('list-row-selected','forms-list-atlas',(0,627,627,1254),(640,192),(80,44,80,44),'horizontal_nine_slice_only'),
 ('list-row-pressed','forms-list-atlas',(627,627,1254,1254),(640,192),(80,44,80,44),'horizontal_nine_slice_only'),
 ('progress-track','motion-controls-atlas',(0,0,665,480),(660,176),(96,40,96,40),'horizontal_nine_slice_only'),
 ('progress-fill','motion-controls-atlas',(665,0,1254,480),(568,112),(60,0,60,0),'horizontal_nine_slice_only'),
 ('toggle-track-on','motion-controls-atlas',(0,480,627,850),(480,184),None,'uniform_scale_only'),
 ('toggle-track-off','motion-controls-atlas',(627,480,1254,850),(480,184),None,'uniform_scale_only'),
 ('toggle-thumb','motion-controls-atlas',(0,850,627,1254),(208,208),None,'uniform_scale_only'),
 ('slider-fill','motion-controls-atlas',(627,850,1254,1254),(532,92),(44,0,44,0),'horizontal_nine_slice_only'),
]

assets=[]; qa_items=[]; ims={}
for aid,atlas,region,canvas,nine,policy in SPECS:
    source=DES/f'{atlas}-native.png'
    raw=Image.open(source).convert('RGBA'); arr=np.array(raw.crop(region)); a=arr[:,:,3]
    labels,n=nd.label(a>=128)
    sizes=np.bincount(labels.ravel()); sizes[0]=0; label=int(sizes.argmax())
    solid=labels==label
    # Keep the complete dominant object and its two-pixel antialias fringe.
    # The model's disconnected colored low-alpha specks are not sprite detail.
    distance=nd.distance_transform_edt(~solid)
    keep=(a>8)&(distance<=2)
    discarded_high=int(((a>=128)&~keep).sum())
    if discarded_high: raise ValueError((aid,'discarded solid pixels',discarded_high))
    opaque=solid&(a>=240)
    _,nearest=nd.distance_transform_edt(~opaque,return_indices=True)
    edge=keep&(a<128)
    # Replace only fringe RGB by nearest opaque RGB, preserving alpha, so
    # yellow/red hidden RGB from the transparent output cannot tint backgrounds.
    near_rgb=arr[nearest[0],nearest[1],:3]
    arr[edge,:3]=near_rgb[edge]
    arr[~keep]=0
    arr[:,:,3][(a>=250)&keep]=255
    ys,xs=np.where(keep); bbox=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
    sprite=Image.fromarray(arr).crop(bbox)
    if sprite.width>canvas[0]-8 or sprite.height>canvas[1]-8: raise ValueError((aid,'canvas too small',sprite.size))
    im=Image.new('RGBA',canvas); pos=((canvas[0]-sprite.width)//2,(canvas[1]-sprite.height)//2)
    im.alpha_composite(sprite,pos)
    hole_check=None
    if aid.startswith('input-'):
        center=np.array(im)[:,:,3][72:120,132:508]
        hole_check={'testedRect':[132,72,508,120],'nonzeroAlpha':int((center>0).sum())}
        if hole_check['nonzeroAlpha']: raise ValueError((aid,'hole not transparent'))
    path=OUT/f'{aid}.png'; im.save(path,optimize=True); ims[aid]=im
    source_box=[bbox[0]+region[0],bbox[1]+region[1],bbox[2]+region[0],bbox[3]+region[1]]
    stats=alpha_stats(im)
    resize={'mode':policy,'uniformScaleAllowed':True,'preserveAspectOfDecoratedEnds':True,
            'stretchAxes':[] if policy=='uniform_scale_only' else (['x','y'] if policy=='nine_slice' else ['x']),
            'lockHeightAfterUniformScale':policy=='horizontal_nine_slice_only'}
    minimum=[canvas[0],canvas[1]] if nine is None else [nine[0]+nine[2]+1,nine[1]+nine[3]+1]
    if policy=='horizontal_nine_slice_only': minimum[1]=canvas[1]
    item={'id':aid,'file':rel(path),'record':rel(Path(str(path)+'.generation.json')),'sha256':sha(path),
          'width':im.width,'height':im.height,'mode':'RGBA','nativeSourceDimensions':list(raw.size),
          'sourceCrop':source_box,'resampled':False,'anchor':{'x':.5,'y':.5},'nineSlice':list(nine) if nine else None,
          'nineSliceOrder':'left,top,right,bottom','resizePolicy':resize,'minimumGeometrySize':minimum,
          'alpha':stats,'status':'pending_visual_review','productionAccepted':False,'derivedFrom':[dependency(source)]}
    assets.append(item)
    checks={'id':aid,'discardedSolidPixels':discarded_high,'isolatedLowAlphaPixelsRemoved':int(((a>0)&~keep).sum()),
            'fringeRGBDecontaminatedPixels':int(edge.sum()),'alpha':stats,'transparentCenter':hole_check,
            'silhouettePreserved':True,'resampled':False}
    qa_items.append(checks)
    record={'schemaVersion':1,'file':rel(path),'sha256':sha(path),'generatedAt':NOW,'width':im.width,'height':im.height,
            'format':'PNG','mode':'RGBA','tool':'Pillow / NumPy / SciPy','route':'local_derivative',
            'actualModel':None,'actualQuality':None,'newModelGeneration':False,'derivedFrom':[dependency(source)],
            'operation':{'sourceRegion':list(region),'nativeCrop':source_box,'cropSize':list(sprite.size),'paddingOffset':list(pos),
                         'outputCanvas':list(canvas),'resample':False,'alphaFloor':8,'antialiasDistanceLimit':2,
                         'removeDisconnectedNoise':True,'fringeRGB':'nearest opaque source RGB for alpha<128',
                         'opaquePromotion':'source alpha>=250 to255','RGBWhenAlphaZero':'zero'},
            'sourceModelEvidence':'See native source record; inherited actualModel and actualQuality remain null.',
            'qa':checks,'inspection':{'status':'pending_visual_review'},'userApproved':False,'clientIntegrated':False}
    write(Path(str(path)+'.generation.json'),record)

old_ids=['input-field','content-card','keypad-key','slider-track','slider-thumb']
old_manifest=json.loads((ROOT/'assets/ui/manifest.json').read_text(encoding='utf-8-sig'))
old={i['id']:i for i in old_manifest['assets'] if i['id'] in old_ids}
reused=[{'id':k,'file':v['file'],'sha256':sha(ROOT/v['file']),'record':v['record'],'reuseOnly':True} for k,v in old.items()]
composition={
 'schemaVersion':1,'status':'pending_visual_review','coordinateSystem':'asset-local design pixels; multiply all dimensions uniformly before horizontal resize',
 'dynamicTextPolicy':'All labels, values, placeholders and errors are native client text; no baked text.',
 'input':{'base':'input-field','focusOverlay':'input-focus-overlay','errorOverlay':'input-error-overlay',
          'sharedDisplayRect':[0,0,640,192],'baseDisplayRect':[20,16,620,176],
          'overlayDisplayRect':[0,0,640,192],'textRect':[100,58,540,134],
          'resizeOrder':'uniform scale all parts first; then horizontal nine-slice to same requested width',
          'verticalStretchAllowed':False,'validationErrorText':'native below the field; never baked into paper',
          'disabled':{'opacity':.48,'interactive':False},'focusAndErrorPrecedence':'error overlay supersedes focus'},
 'codeEntry':{'normalCell':'keypad-key','focusOverlay':'input-focus-overlay','errorOverlay':'input-error-overlay',
              'overlayUse':'horizontal nine-slice only: minimum native width161, height192; for square cells use common whole-container border or native focus ring, do not squash this artwork into six squares',
              'digitsAreNative':True,'reuseOnly':True},
 'list':{'normal':'content-card','selected':'list-row-selected','pressed':'list-row-pressed',
         'displaySize':[640,192],'textRect':[104,42,536,150],'selectedAndPressedPrecedence':'pressed replaces selected while held',
         'resizePolicy':'uniform scale entire family first, then horizontal nine-slice only; fixed row height preserves side cloud ornaments; native text/counters/icons are independent'},
 'progress':{'track':'progress-track','fill':'progress-fill','trackSize':[660,176],
             'contentRect':[66,48,594,128],'fillPaintedRect':'fit opaque painted fill silhouette inside contentRect; discard transparent canvas padding before display sizing',
             'fillAssetCrop':list(ims['progress-fill'].getbbox()),'trackNineSlice':[96,40,96,40],
             'valueRange':[0,1],'clip':'left-to-right in contentRect; fill hidden at0, full at1',
             'labelIsNative':True,'heightLockedAfterUniformScale':True,'minimumNativeWidth':193},
 'toggle':{'onTrack':'toggle-track-on','offTrack':'toggle-track-off','thumb':'toggle-thumb',
           'trackSize':[480,184],'thumbPaintedDiameter':112,'thumbCenters':{'off':[87,92],'on':[393,92]},
           'thumbAssetCrop':list(ims['toggle-thumb'].getbbox()),'stateChangesGeometry':False,
           'resizePolicy':'uniform scale entire composition only; never stretch capsules/circle',
           'disabled':{'opacity':.48,'interactive':False},'labelsAreNative':True},
 'slider':{'track':'slider-track','fill':'slider-fill','thumb':'slider-thumb','trackSize':[359,95],
           'contentRect':[50,32,309,63],'fillAssetCrop':list(ims['slider-fill'].getbbox()),
           'thumbCenters':{'min':[50,47.5],'max':[309,47.5]},'thumbPaintedDiameter':68,
           'thumbAssetCrop':list(Image.open(ROOT/old['slider-thumb']['file']).getbbox()),
           'valueRange':[0,1],'clip':'left-to-right contentRect; hide at0','resizePolicy':'uniform scale first then horizontal track/fill resize; thumb always uniform',
           'disabled':{'opacity':.48,'interactive':False}},
 'runtimeStates':{'loading':'progress 0—1; loading-ring for indeterminate','settings':'toggle and slider',
                  'loginSearchRoom':'input normal/focus/error/disabled','mailRecordsFriends':'list normal/selected/pressed',
                  'notClientIntegrated':True},
 'reusedAssets':reused,'userApproved':False,'clientIntegrated':False}
write(OUT/'compositions.json',composition)

# Nine-slice QA is deliberately limited to the axes allowed by the manifest.
def nine_slice(im,size,margins):
    l,t,r,b=margins; w,h=im.size; nw,nh=size
    if nw<l+r+1 or nh<t+b+1: raise ValueError('Nine-slice below minimum')
    result=Image.new('RGBA',size)
    sx=[0,l,w-r,w]; sy=[0,t,h-b,h]; dx=[0,l,nw-r,nw]; dy=[0,t,nh-b,nh]
    for j in range(3):
        for i in range(3):
            if sx[i+1]==sx[i] or sy[j+1]==sy[j] or dx[i+1]==dx[i] or dy[j+1]==dy[j]: continue
            part=im.crop((sx[i],sy[j],sx[i+1],sy[j+1]))
            target=(dx[i+1]-dx[i],dy[j+1]-dy[j])
            if part.size!=target: part=part.resize(target,Image.Resampling.LANCZOS)
            result.alpha_composite(part,(dx[i],dy[j]))
    return result

def painted(im,size): return im.crop(im.getbbox()).resize(size,Image.Resampling.LANCZOS)
def paste(dst,im,pos,opacity=1):
    if opacity!=1:
        im=im.copy(); im.putalpha(im.getchannel('A').point(lambda a:round(a*opacity)))
    dst.alpha_composite(im,tuple(map(round,pos)))
def oldim(k): return Image.open(ROOT/old[k]['file']).convert('RGBA')
def input_sample(state,width=640):
    im=Image.new('RGBA',(width,192)); base=nine_slice(oldim('input-field'),(width-40,160),(34,30,34,30));paste(im,base,(20,16))
    if state in ['focus','error']:paste(im,nine_slice(ims[f'input-{state}-overlay'],(width,192),(80,44,80,44)),(0,0))
    if state=='disabled': im.putalpha(im.getchannel('A').point(lambda a:round(a*.48)))
    return im
def toggle(state,disabled=False):
    im=ims['toggle-track-'+state].copy();thumb=painted(ims['toggle-thumb'],(112,112));cx=87 if state=='off' else 393;paste(im,thumb,(cx-56,36))
    if disabled:im.putalpha(im.getchannel('A').point(lambda a:round(a*.48)))
    return im
def progress(v,width=660):
    im=nine_slice(ims['progress-track'],(width,176),(96,40,96,40));l,t,r,b=66,48,width-66,128
    fill=painted(ims['progress-fill'],(r-l,b-t));cut=round((r-l)*v)
    if cut:paste(im,fill.crop((0,0,cut,b-t)),(l,t))
    return im
def slider(v):
    im=oldim('slider-track');l,t,r,b=50,32,309,63;fill=painted(ims['slider-fill'],(r-l,b-t));cut=round((r-l)*v)
    if cut:paste(im,fill.crop((0,0,cut,b-t)),(l,t))
    thumb=painted(oldim('slider-thumb'),(68,68));paste(im,thumb,(l+(r-l)*v-34,47.5-34));return im

FONT='C:/Windows/Fonts/msyh.ttc'
font=ImageFont.truetype(FONT,22); small=ImageFont.truetype(FONT,18); title=ImageFont.truetype(FONT,30)
previews=[]
for theme,bg,fg in [('light','#f4eddb','#183d35'),('dark','#153b35','#fff4d9')]:
    contact=Image.new('RGBA',(1640,1980),bg);draw=ImageDraw.Draw(contact)
    draw.text((32,20),'表单控件生产验收 / 原生文案与运行组合',font=title,fill=fg)
    draw.text((32,64),'10 个独立透明皮肤 · 复用旧常态输入、列表、滑条 · 本图仅为验收联系图',font=small,fill=fg)
    y=110
    for col,state in enumerate(['normal','focus','error','disabled']):
        x=32+(col%2)*800; yy=y+(col//2)*208
        draw.text((x,yy),{'normal':'输入常态 / 复用','focus':'输入焦点 / 透明描边','error':'输入错误 / 透明描边','disabled':'输入禁用 / 透明度与交互锁'}[state],font=font,fill=fg)
        sample=input_sample(state).resize((600,180),Image.Resampling.LANCZOS);paste(contact,sample,(x+20,yy+24))
        draw.text((x+122,yy+89),'房间名称：清风雅局',font=font,fill='#183d35' if state!='disabled' else'#737e72')
    y=560
    for col,state in enumerate(['normal','selected','pressed']):
        x=32+col*532;draw.text((x,y),'列表 '+state,font=font,fill=fg)
        sample=nine_slice(oldim('content-card'),(640,192),(45,45,45,45)) if state=='normal' else ims['list-row-'+state]
        sample=sample.resize((500,150),Image.Resampling.LANCZOS);paste(contact,sample,(x,y+34))
        draw.text((x+80,y+94),'清风来信  ·  未读',font=font,fill='#183d35')
    y=790
    for n,v in enumerate([0,.25,.5,1]):
        x=32+(n%2)*800;yy=y+(n//2)*200;draw.text((x,yy),f'进度 {round(v*100)}% / 填充单独裁剪',font=font,fill=fg)
        paste(contact,progress(v).resize((600,160),Image.Resampling.LANCZOS),(x,yy+20))
    y=1210
    for n,(state,disabled) in enumerate([('off',False),('on',False),('on',True)]):
        x=32+n*532;draw.text((x,y),'开关 '+state+(' / disabled' if disabled else''),font=font,fill=fg)
        paste(contact,toggle(state,disabled).resize((384,147),Image.Resampling.LANCZOS),(x+50,y+40))
    y=1440
    for n,v in enumerate([0,.5,1]):
        x=32+n*532;draw.text((x,y),f'音量条 {v:g} / 复用轨道与滑块',font=font,fill=fg)
        paste(contact,slider(v),(x+75,y+50))
    y=1640;draw.text((32,y),'横向九宫格：固定高度与云纹端部；不把概念图整体拉伸',font=font,fill=fg)
    sample=input_sample('focus',1120).resize((1008,173),Image.Resampling.LANCZOS);paste(contact,sample,(32,y+30))
    draw.text((132,y+100),'焦点示例：横向扩展，文案保持原生',font=font,fill='#183d35')
    # The isolated circular thumb is visible independently and with alpha on both themes.
    paste(contact,ims['toggle-thumb'],(1280,1670));draw.text((1240,1880),'独立滑块：等比',font=font,fill=fg)
    path=DES/f'preview-forms-{theme}.png';contact.convert('RGB').save(path,optimize=True);previews.append(rel(path))
    dep=[dependency(OUT/f'{a[0]}.png') for a in SPECS]+[dependency(ROOT/v['file']) for v in old.values()]
    rec={'schemaVersion':1,'file':rel(path),'sha256':sha(path),'generatedAt':NOW,'width':1640,'height':1980,'mode':'RGB','format':'PNG',
         'tool':'Pillow','route':'local_derivative','actualModel':None,'actualQuality':None,'newModelGeneration':False,
         'derivedFrom':dep,'operation':{'type':'QA contact composition','background':bg,'nativeChineseLabels':FONT,
            'samples':['input normal/focus/error/disabled','list normal/selected/pressed','progress0/25/50/100',
                      'toggle on/off/disabled','slider0/50/100','horizontal-nine-slice widened input','separate circular thumb'],
            'geometryContracts':rel(OUT/'compositions.json')},'inspection':{'status':'pending_visual_review'},'userApproved':False}
    write(Path(str(path)+'.generation.json'),rec)

manifest={'schemaVersion':3,'scope':'production-v3 forms P0 limited 10 runtime skins','createdAt':NOW,
          'status':'pending_visual_review','assetCount':len(assets),'nativeAtlasCount':2,'assets':assets,
          'nativeSources':[dependency(DES/f'{name}-native.png') for name in ['forms-list-atlas','motion-controls-atlas']],
          'reusedAssets':reused,'compositions':rel(OUT/'compositions.json'),'qa':rel(OUT/'qa.json'),'qaPreviews':previews,
          'actualModel':None,'actualQuality':None,'userApproved':False,'clientIntegrated':False}
qa={'schemaVersion':1,'status':'pending_visual_review','createdAt':NOW,'counts':{'newRuntimeSkins':10,'nativeAtlases':2,'finalContacts':2},
    'items':qa_items,'previews':previews,'automatedChecks':{'allExpectedFiles':len(assets)==10,
    'discardedSolidPixels':sum(i['discardedSolidPixels'] for i in qa_items),'allCornersTransparent':all(max(i['alpha']['corners'])==0 for i in qa_items),
    'allRGBA':all(Image.open(ROOT/a['file']).mode=='RGBA' for a in assets),'noRuntimeUpscaling':True},
    'pendingChecks':['actual light/dark visual review','overlay fit and native-text readability','0/100 progress, toggle and slider geometry'],
    'userApproved':False,'clientIntegrated':False}
write(OUT/'manifest.json',manifest);write(OUT/'qa.json',qa)
print(json.dumps({'assets':len(assets),'previews':previews,'nativeSizes':{a['id']:[a['width'],a['height']] for a in assets},'qa':qa['automatedChecks']},ensure_ascii=False))
