from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageFilter,ImageDraw,ImageFont
from scipy.ndimage import label,find_objects
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record(p,source,operation):
    with Image.open(p) as im:w,h=im.size;mode=im.mode
    write(Path(str(p)+'.generation.json'),{'schemaVersion':2,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'exportedAt':datetime.now(timezone.utc).isoformat(),'width':w,'height':h,'mode':mode,'format':'PNG','newModelGeneration':False,'actualModel':None,'actualQuality':None,'derivedFrom':source,'operation':operation,'nativeDetailUpscaled':False})
src=R/'designs/ui/production-v3/empty-states-native.png';im=Image.open(src).convert('RGBA');arr=np.array(im);alpha=arr[:,:,3]
# Ownership extraction keeps decorations that cross a nominal grid boundary.
labels,count=label(alpha>16);boxes=find_objects(labels);centers=np.array([[256,256],[768,256],[1280,256],[256,768],[768,768],[1280,768]])
owned=np.zeros((6,im.height,im.width),dtype=np.uint8);pieces=[[] for _ in range(6)]
for idx,box in enumerate(boxes):
    if box is None:continue
    local=labels[box]==idx+1
    if np.count_nonzero(local)<4:continue
    yy,xx=np.where(local);x=float(xx.mean()+box[1].start);y=float(yy.mean()+box[0].start)
    owner=int(np.argmin(((centers-[x,y])**2).sum(1)))
    owned[owner][box][local]=alpha[box][local]
    pieces[owner].append({'sourceBox':[box[1].start,box[0].start,box[1].stop,box[0].stop],'pixels':int(local.sum())})
ids=['empty-mail','empty-friends','empty-search','empty-records','connection-interrupted','match-timeout'];names=['暂无邮件','暂无好友','暂无搜索结果','暂无战绩','连接中断','等待超时'];assets=[]
for i,(id,name) in enumerate(zip(ids,names)):
    mask=Image.fromarray(owned[i]);bbox=mask.getbbox();assert bbox
    crop=im.crop(bbox);crop.putalpha(mask.crop(bbox))
    scale=min(1,464/crop.width,464/crop.height)
    # Premultiplied resize avoids colour bleeding into softened transparent edges.
    if scale<1:crop=crop.convert('RGBa').resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS).convert('RGBA')
    out=Image.new('RGBA',(512,512));out.alpha_composite(crop,((512-crop.width)//2,(512-crop.height)//2))
    p=R/f'assets/ui/production-v3/empty/{id}.png';p.parent.mkdir(parents=True,exist_ok=True);out.save(p)
    deps=[{'file':src.relative_to(R).as_posix(),'sha256':sha(src),'generationRecord':src.relative_to(R).as_posix()+'.generation.json'}]
    op={'ownership':'assign each alpha>16 connected component to nearest 3x2 subject center; preserve complete crossing components','tinyNoiseRemovedBelowPixels':4,'sourceBBox':list(bbox),'sourceComponents':pieces[i],'uniformScale':scale,'canvas':[512,512],'padding':24,'rgbRepainting':False}
    record(p,deps,op)
    assert max(np.array(out.getchannel('A'))[0,:])==0
    assets.append({'id':id,'name':name,'file':p.relative_to(R).as_posix(),'record':p.relative_to(R).as_posix()+'.generation.json','sha256':sha(p),'width':512,'height':512,'mode':'RGBA','anchor':[.5,.5],'recommendedDisplaySize':[180,180],'resizePolicy':{'mode':'uniform_scale_only','nineSlice':None},'status':'pending_visual_review'})
for tone,color in [('light','#fff9e9'),('dark','#123e34')]:
    sheet=Image.new('RGB',(1260,850),color);draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
    for i,a in enumerate(assets):
        icon=Image.open(R/a['file']);icon=icon.resize((360,360),Image.Resampling.LANCZOS);x=(i%3)*420+30;y=(i//3)*425+15
        sheet.paste(icon,(x,y),icon);draw.text((x+25,y+365),a['name'],font=font,fill='#fff9e9' if tone=='dark' else '#183d35')
    p=R/f'assets/ui/production-v3/empty/preview-{tone}.png';sheet.save(p)
    record(p,[{'file':a['file'],'sha256':a['sha256'],'generationRecord':a['record']} for a in assets],{'operation':'QA contact sheet over opaque inspection background','background':color,'newRuntimeAsset':False})
write(R/'assets/ui/production-v3/empty/manifest.json',{'schemaVersion':3,'status':'pending_visual_review','assets':assets,'primaryAssetCount':6,'previews':['assets/ui/production-v3/empty/preview-light.png','assets/ui/production-v3/empty/preview-dark.png'],'source':src.relative_to(R).as_posix()})
print(json.dumps({'exported':6,'sourceSize':im.size,'strongPixelsUnassigned':int(((alpha>128)&(owned.max(0)==0)).sum()),'status':'pending_visual_review'}))
