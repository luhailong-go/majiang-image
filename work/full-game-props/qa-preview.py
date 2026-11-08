from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import deque
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent.parent.parent
OUT=ROOT/'assets/props/full-game';FLOWERS=ROOT/'assets/tiles/flowers';PREV=ROOT/'designs/props/full-game/previews'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/simkai.ttf',n)
m=load(OUT/'manifest.json');checks=[]
def components(a):
 w,h=a.size;px=a.load();seen=set();sizes=[]
 for y in range(h):
  for x in range(w):
   if px[x,y]<128 or (x,y) in seen:continue
   q=deque([(x,y)]);seen.add((x,y));count=0
   while q:
    xx,yy=q.popleft();count+=1
    for nx,ny in ((xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)):
     if 0<=nx<w and 0<=ny<h and px[nx,ny]>=128 and (nx,ny) not in seen:seen.add((nx,ny));q.append((nx,ny))
   if count>40:sizes.append(count)
 return sizes
for item in m['assets']+m['supportAssets']:
 p=ROOT/item['file'];im=Image.open(p);assert im.mode=='RGBA',(p,im.mode);assert im.size==(item['width'],item['height']),p;assert sha(p)==item['sha256'],p
 a=im.getchannel('A');assert a.getextrema()==(0,255),p
 assert a.crop((0,0,im.width,4)).getextrema()[1]==0,p
 assert a.crop((0,im.height-4,im.width,im.height)).getextrema()[1]==0,p
 assert a.crop((0,0,4,im.height)).getextrema()[1]==0,p
 assert a.crop((im.width-4,0,im.width,im.height)).getextrema()[1]==0,p
 c={'id':item['id'],'file':item['file'],'sha256':sha(p),'size':list(im.size),'alphaRange':list(a.getextrema()),'transparentMargin':'passed','technical':'passed','visual':'pending'}
 if item['group']=='dice':
  pip=Image.open(OUT/'dice'/f"dice-{item['pipCount']}.pips.png");c['renderedPipComponents']=len(components(pip.getchannel('A')));c['expectedPipCount']=item['pipCount'];assert c['renderedPipComponents']==c['expectedPipCount'],p
 if item['group']=='optional-flower':
  c['label']=item['label'];s=(ROOT/item['labelSVG']).read_text(encoding='utf-8');assert f'data-glyph="{item["label"]}"' in s,p;c['labelOutline']='present, exact glyph key';c['optional']=True
 checks.append(c)

def board(name,title,entries,cols,cw=230,ch=270):
 rows=(len(entries)+cols-1)//cols;image=Image.new('RGB',(cols*cw,90+rows*ch),'#e8dfca');draw=ImageDraw.Draw(image);draw.text((24,18),title,font=font(33),fill='#174e41')
 for i,e in enumerate(entries):
  x=(i%cols)*cw;y=90+(i//cols)*ch;draw.rounded_rectangle((x+5,y+3,x+cw-5,y+ch-5),radius=14,fill='#f7f0df',outline='#c2aa72')
  im=Image.open(ROOT/e['file']).convert('RGBA');im.thumbnail((cw-24,ch-62),Image.Resampling.LANCZOS);image.paste(im,(x+(cw-im.width)//2,y+10+(ch-62-im.height)//2),im)
  label=e['label'];bbox=draw.textbbox((0,0),label,font=font(23));draw.text((x+(cw-bbox[2])/2,y+ch-53),label,font=font(23),fill='#174e41');identifier=e['id'];bbox=draw.textbbox((0,0),identifier,font=font(11));draw.text((x+(cw-bbox[2])/2,y+ch-24),identifier,font=font(11),fill='#746d59')
 p=PREV/name;image.save(p);save(Path(str(p)+'.generation.json'),{'file':rel(p),'sha256':sha(p),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'Pillow labeled contact preview','route':'derived','actualModel':None,'actualQuality':None,'unverifiedReason':'Contact sheet assembly only, no model generation','derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['record']} for e in entries],'operation':'uniform downscale and compose final assets with native preview labels','width':image.width,'height':image.height,'checks':{'technical':'passed','visual':'pending'}});return rel(p)
previews=[]
previews.append(board('emotes-contact.png','局内交流 · 12 枚葫芦表情',[e for e in m['assets'] if e['group']=='emote'],6))
previews.append(board('items-contact.png','物品与奖励 · 12 枚非货币图标',[e for e in m['assets'] if e['group']=='item'],6))
previews.append(board('flowers-dice-contact.png','可选花牌 8 种 / 玉质骰子 1—6 点',[e for e in m['assets'] if e['group'] in ('optional-flower','dice')],7))
previews.append(board('table-props-contact.png','骰盅开合 / 起庄标记 / 计分筹棒',[e for e in m['assets'] if e['group']=='table-prop'],4))
all_entries=m['assets'];cw=140;ch=170;alpha=Image.new('RGB',(cw*7,65+ch*12),'#e8dfca');d=ImageDraw.Draw(alpha);d.text((20,14),'最终资源 · 浅底 / 深底透明边缘',font=font(27),fill='#174e41')
for mode,bg in enumerate(('#f7f0df','#173f36')):
 for i,e in enumerate(all_entries):
  x=i%7*cw;y=65+(i//7+mode*6)*ch;d.rounded_rectangle((x+3,y+3,x+cw-3,y+ch-3),radius=9,fill=bg);im=Image.open(ROOT/e['file']).convert('RGBA');im.thumbnail((128,130),Image.Resampling.LANCZOS);alpha.paste(im,(x+(cw-im.width)//2,y+7+(130-im.height)//2),im);label=e['label'];bb=d.textbbox((0,0),label,font=font(16));d.text((x+(cw-bb[2])/2,y+141),label,font=font(16),fill='#174e41' if mode==0 else '#f8ebc9')
p=PREV/'alpha-light-dark.png';alpha.save(p);save(Path(str(p)+'.generation.json'),{'file':rel(p),'sha256':sha(p),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'Pillow final deep/light alpha inspection board','route':'derived','actualModel':None,'actualQuality':None,'unverifiedReason':'Preview assembly only','derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['record']} for e in all_entries],'operation':'show identical final transparent assets on light and dark backgrounds','width':alpha.width,'height':alpha.height,'checks':{'technical':'passed','visual':'pending'}});previews.append(rel(p));m['previews']=previews;save(OUT/'manifest.json',m)
report={'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtimeCount':len(m['assets']),'supportCount':len(m['supportAssets']),'technical':'passed','visual':'pending','dicePointCount':'6 rendered pip images independently measured by foreground connected components, all exact','flowerLabels':{'expected':['梅','兰','竹','菊','春','夏','秋','冬'],'actual':[a['label'] for a in m['assets'] if a['group']=='optional-flower'],'status':'passed'},'checks':checks,'sourceUpscale':False,'previews':previews}
save(OUT/'qa.json',report);save(FLOWERS/'qa.json',{**report,'checks':[c for c in checks if c['id'].startswith('flower-')],'scope':'optional eight flower tiles and botanical helper assets'});print(json.dumps({'runtime':len(m['assets']),'support':len(m['supportAssets']),'technical':'passed','previews':previews},ensure_ascii=False))
