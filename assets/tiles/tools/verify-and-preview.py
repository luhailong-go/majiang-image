"""Independent pixel checks and contact previews for the delivered tile sprites."""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
from collections import deque
import json, hashlib, datetime

ROOT=Path(__file__).resolve().parent.parent
PROJECT=ROOT.parent.parent
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8-sig'))
FONT=Path('C:/Windows/Fonts/simkai.ttf')
def font(size): return ImageFont.truetype(str(FONT),size)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def project_rel(p): return p.relative_to(PROJECT).as_posix()
def components(alpha):
    a=alpha.point(lambda v:255 if v>=128 else 0)
    px=a.load(); w,h=a.size; seen=set(); sizes=[]
    for y in range(h):
        for x in range(w):
            if not px[x,y] or (x,y) in seen: continue
            q=deque([(x,y)]); seen.add((x,y)); count=0
            while q:
                xx,yy=q.popleft(); count+=1
                for nx,ny in ((xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)):
                    if 0<=nx<w and 0<=ny<h and px[nx,ny] and (nx,ny) not in seen:
                        seen.add((nx,ny)); q.append((nx,ny))
            if count>40: sizes.append(count)
    return sizes

results=[]
for tile in manifest['tiles']:
    p=PROJECT/tile['file']; im=Image.open(p).convert('RGBA')
    assert im.size==(448,640), p
    assert digest(p)==tile['sha256'],p
    alpha=im.getchannel('A')
    assert alpha.getextrema()==(0,255),p
    assert alpha.crop((0,0,448,6)).getextrema()[1]==0,p
    assert alpha.crop((0,634,448,640)).getextrema()[1]==0,p
    assert alpha.getpixel((224,306))==255,p
    symbol=Image.open(PROJECT/tile['symbolPNG']).convert('RGBA')
    actual_components=components(symbol.getchannel('A')) if tile['suit'] in ('dots','bamboo') else None
    if actual_components is not None:
        assert len(actual_components)==tile['rank'],(p,len(actual_components),tile['rank'])
    results.append({'id':tile['id'],'label':tile['label'],'canvas':'448x640','sha256':digest(p),'alpha':'0..255, transparent margins, opaque face','expectedSymbolCount':tile.get('rank') if actual_components is not None else None,'connectedSymbolComponents':len(actual_components) if actual_components is not None else None,'technical':'passed','visual':'pending'})
assert len(results)==34
assert len({r['sha256'] for r in results})==34

previews=ROOT/'previews';previews.mkdir(exist_ok=True)
entries=[(t['label'],PROJECT/t['file'],t['id']) for t in manifest['tiles']]+[('空白牌胚',ROOT/'tile-blank.png','blank'),('统一牌背',ROOT/'tile-back.png','back')]
cw,ch=174,258
sheet=Image.new('RGB',(cw*9,120+ch*4),'#e7dfce'); d=ImageDraw.Draw(sheet)
d.text((28,20),'道家 Q 版麻将 · 34 种基础牌',font=font(39),fill='#174d42')
d.text((30,75),'手绘生成牌胚 + 精确矢量符号 | 万 / 筒 / 条 1—9，东南西北中发白',font=font(21),fill='#526358')
for i,(label,p,identifier) in enumerate(entries):
    x=(i%9)*cw;y=120+(i//9)*ch
    d.rounded_rectangle((x+6,y+4,x+cw-6,y+ch-5),radius=13,fill='#f7f0df',outline='#c9b480',width=1)
    tile=Image.open(p).convert('RGBA').resize((140,200),Image.Resampling.LANCZOS)
    sheet.paste(tile,(x+(cw-140)//2,y+9),tile)
    box=d.textbbox((0,0),label,font=font(24));d.text((x+(cw-box[2])/2,y+211),label,font=font(24),fill='#173f37')
    box=d.textbbox((0,0),identifier,font=font(12));d.text((x+(cw-box[2])/2,y+239),identifier,font=font(12),fill='#736b55')
sheet.save(previews/'tiles-contact-sheet.png')

state=Image.new('RGB',(1600,710),'#e7dfce');sd=ImageDraw.Draw(state)
sd.text((30,20),'状态 / 朝向 / 透明边缘检查',font=font(36),fill='#174d42')
labels=['正常','选中（上抬）','可操作高亮','不可打（灰化）','左家 +90°','对家 180°','右家 +270°','牌背']
base=Image.open(ROOT/'faces/wan-6.png').convert('RGBA')
for row,bg in enumerate(('#f4ecdc','#173d35')):
    for col,label in enumerate(labels):
        x=col*200;y=85+row*300
        sd.rounded_rectangle((x+5,y,x+195,y+270),radius=12,fill=bg)
        im=base.copy()
        if col==3:
            gray=ImageEnhance.Color(im).enhance(0); gray=ImageEnhance.Brightness(gray).enhance(.60); gray.putalpha(im.getchannel('A')); im=gray
        if col==2:
            im=Image.alpha_composite(im,Image.open(ROOT/'states/tile-highlight.png').convert('RGBA'))
        if col in (4,5,6): im=im.rotate(-90*(col-3),expand=True)
        if col==7: im=Image.open(ROOT/'tile-back.png').convert('RGBA')
        im.thumbnail((178,218),Image.Resampling.LANCZOS)
        iy=y+20+(218-im.height)//2-(12 if col==1 else 0)
        state.paste(im,(x+(200-im.width)//2,iy),im)
        box=sd.textbbox((0,0),label,font=font(18));sd.text((x+(200-box[2])/2,y+240),label,font=font(18),fill='#1e4d40' if row==0 else '#f3e7c9')
state.save(previews/'tile-states-alpha.png')

for p in previews.glob('*.png'):
    im=Image.open(p)
    input_paths=([PROJECT/t['file'] for t in manifest['tiles']]+[ROOT/'tile-blank.png',ROOT/'tile-back.png']) if p.name=='tiles-contact-sheet.png' else [ROOT/'faces/wan-6.png',ROOT/'tile-back.png',ROOT/'states/tile-highlight.png']
    record={'file':project_rel(p),'sha256':digest(p),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'route':'derived','tool':'Pillow contact sheet assembly','actualModel':None,'actualQuality':None,'unverifiedReason':'Preview assembled from delivered tile assets, no model call','derivedFrom':[{'file':project_rel(source),'sha256':digest(source),'generationRecord':project_rel(source)+'.generation.json'} for source in input_paths],'operation':'downscale and arrange exported sprites on labeled preview boards; native source sizes remain in manifest','width':im.width,'height':im.height,'checks':{'technical':'passed','visual':'pending'}}
    Path(str(p)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

report={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'faceCount':34,'uniqueFaceHashes':34,'pixelCountChecks':'All 9 dot tiles and 9 bamboo tiles have exact rank connected foreground symbol components (>40px), measured from rendered transparent symbol PNGs','sourceNativeDimensions':[1024,1536],'exportCanvas':[448,640],'upscaled':False,'checks':results,'manualVisualReview':'pending'}
(ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'faces':34,'exactPipAndBambooChecks':18,'previewSize':sheet.size,'statePreview':state.size},ensure_ascii=False))

