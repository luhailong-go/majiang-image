import json,hashlib,math
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/ui/production-v3/gameplay'
DESIGN=ROOT/'designs/ui/production-v3/gameplay'
DATA=json.loads((OUT/'runtime-compositions.json').read_text(encoding='utf-8'))
REG=DATA['assetRegistry']; USED=set()
FONT=Path(r'C:\Windows\Fonts\simkai.ttf')
if not FONT.is_file(): FONT=Path(r'C:\Windows\Fonts\msyh.ttc')
fonts={}
def font(n):
 if n not in fonts: fonts[n]=ImageFont.truetype(str(FONT),n)
 return fonts[n]
def text(im,s,xy,n=22,fill='#183D35',anchor='mm'):
 ImageDraw.Draw(im).text(xy,s,font=font(n),fill=fill,anchor=anchor)
def load(aid):
 USED.add(aid)
 return Image.open(ROOT/REG[aid]['file']).convert('RGBA')
def fit_sprite(aid,maxsize,rotation=0,state=None):
 im=load(aid); scale=min(maxsize[0]/im.width,maxsize[1]/im.height)
 # Native alpha and glyphs remain as one sprite; right-angle transpose does not mirror glyphs.
 if scale>1.0001: raise ValueError('Unexpected upscale '+aid)
 im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
 if aid.startswith('avatar-') and aid!='avatar-frame':
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).ellipse((0,0,im.width-1,im.height-1),fill=255)
  import PIL.ImageChops
  im.putalpha(PIL.ImageChops.multiply(im.getchannel('A'),mask))
 if state=='illegal':
  alpha=im.getchannel('A'); im=ImageOps.grayscale(im).convert('RGBA'); im=ImageEnhance.Brightness(im).enhance(.60); im.putalpha(alpha)
 if rotation%360: im=im.rotate(-rotation,expand=True)
 return im
def put(im,aid,center,size,rotation=0,state=None):
 sprite=fit_sprite(aid,size,rotation,state)
 im.alpha_composite(sprite,(round(center[0]-sprite.width/2),round(center[1]-sprite.height/2)))
 return sprite.size
def native9(im,aid,center,size):
 src=load(aid); l,t,r,b=REG[aid]['nineSlice']; W,H=map(round,size)
 policy=REG[aid].get('resizePolicy',{})
 if isinstance(policy,dict) and policy.get('mode')=='horizontal_nine_slice_only':
  k=H/src.height;src=src.resize((round(src.width*k),H),Image.Resampling.LANCZOS)
  l,t,r,b=[max(1,round(v*k)) for v in (l,t,r,b)]
 assert W>l+r and H>t+b
 sx=[0,l,src.width-r,src.width]; sy=[0,t,src.height-b,src.height]
 dx=[0,l,W-r,W]; dy=[0,t,H-b,H]
 tile=Image.new('RGBA',(W,H))
 for y in range(3):
  for x in range(3):
   part=src.crop((sx[x],sy[y],sx[x+1],sy[y+1]))
   part=part.resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS)
   tile.alpha_composite(part,(dx[x],dy[y]))
 im.alpha_composite(tile,(round(center[0]-W/2),round(center[1]-H/2)))
def rotatepoint(p,angle):
 a=math.radians(angle); return (p[0]*math.cos(a)-p[1]*math.sin(a),p[0]*math.sin(a)+p[1]*math.cos(a))
def local(origin,p,angle):
 x,y=rotatepoint(p,angle); return (origin[0]+x,origin[1]+y)
def tile(im,aid,center,size,rotation=0,state=None):
 put(im,aid,center,size,rotation,state)
 if state in ('selected','legal'): put(im,'tile-highlight',center,size,rotation)
 if state=='illegal':
  offset=rotatepoint((size[0]/2-8,-size[1]/2+8),rotation)
  put(im,'illegal-tile-badge',(center[0]+offset[0],center[1]+offset[1]),(24,24),rotation)
def meld(kind,angle=0,face='wan-6',called=1,size=(42,60)):
 count=3 if kind in ('triplet','added-kong') else 4
 bw,bh=size; gap=3; entries=[]; x=16; baseline=round(bh)+16+(18 if kind=='added-kong' else 0)
 for i in range(count):
  back=kind=='concealed-kong' and i in (0,3)
  iscalled=kind!='concealed-kong' and i==called
  src=fit_sprite('tile-back' if back else face,(bw,bh),90 if iscalled else 0)
  entries.append((src,x,baseline-src.height,i,iscalled));x+=src.width+gap
 out=Image.new('RGBA',(x+16,baseline+16),(0,0,0,0))
 for src,x,y,i,c in entries: out.alpha_composite(src,(x,y))
 if kind=='added-kong':
  src,x,y,_,_=next(e for e in entries if e[4]);out.alpha_composite(src,(x,y-18))
 bb=out.getchannel('A').getbbox();cut=out.crop(bb);out=Image.new('RGBA',(cut.width+32,cut.height+32));out.alpha_composite(cut,(16,16))
 if angle:out=out.rotate(-angle,expand=True)
 return out
def paste(im,sprite,center):
 im.alpha_composite(sprite,(round(center[0]-sprite.width/2),round(center[1]-sprite.height/2)))
def background():
 im=load('table-background')
 return im
def panelbg(size,shade='#EDE5CF'):
 return Image.new('RGBA',size,shade)
def save(im,name,description):
 path=DESIGN/(name+'.png'); im.convert('RGB').save(path)
 record={'schemaVersion':1,'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':'RGB PNG','tool':'Pillow deterministic assembly','route':'derived','actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'operation':'Composite accepted independent raster skins, whole-sprite right-angle rotations, proportional downscales, approved nine-slice and native preview labels. No new AI image, no code-drawn replacement painting.','description':description,'nativeTextFont':str(FONT),'fontRedistributed':False,'derivedFrom':[{'id':aid,'file':REG[aid]['file'],'sha256':REG[aid]['sha256']} for aid in sorted(USED)],'runtimeContract':'assets/ui/production-v3/gameplay/runtime-compositions.json','clientIntegrated':False,'checks':{'visual':'pending','technical':'pending'}}
 path.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 USED.clear()
 return path
# 1: all seats. This is a layout fixture, not a server-valid replay.
im=background(); table=DATA['compositions']['table']; seats=table['seats']
for seat,cfg in seats.items():
 angle=cfg['clockwiseDegrees']; origin=cfg['wallOrigin']
 for layer,offset in [('lower',0),('upper',-8)]:
  for i in range(12):
   put(im,'tile-back',local(origin,((i-5.5)*24,offset),angle),cfg.get('wallTileSize',(28,40)),angle)
for si,(seat,cfg) in enumerate(seats.items()):
 angle=cfg['clockwiseDegrees']; origin=cfg['discardOrigin']
 grid=table['discardGrid'];ov=grid['seatOverrides'].get(seat,{});ts=ov.get('tileSize',grid['tileSize']);step=ov.get('stepLocal',grid['stepLocal']);first=ov.get('firstLocalOffset',grid['firstLocalOffset'])
 for i in range(6):
  aid=['wan-4','tong-7','tiao-2','wind-south','wan-8','dragon-white'][(i+si)%6]
  p=local(origin,(first[0]+i*step[0],first[1]),angle)
  tile(im,aid,p,ts,angle)
  if seat=='self' and i==5:
   put(im,'discard-pointer',local(p,(0,-38),angle),(22,24),angle)
 origin=cfg['meldOrigin'];paste(im,meld('triplet',angle,'tong-3',0,cfg.get('meldTileSize',(31.5,45))),origin)
 origin=cfg['handOrigin']; size=cfg['handTileSize']; stride=cfg['handStride']
 for i in range(13):
  p=local(origin,((i-6)*stride,0),angle)
  if seat=='self':
   aid=['wan-1','wan-2','wan-3','tong-1','tong-2','tong-3','tiao-1','tiao-2','tiao-3','wind-east','wind-east','dragon-red','dragon-red'][i]
   state='selected' if i==2 else ('illegal' if i==11 else None)
   if state=='selected':p=local(p,(0,-12),angle)
   tile(im,aid,p,size,angle,state)
  else: tile(im,'tile-back',p,size,angle)
 if seat=='self':
  for i in (2,11):
   p=local(origin,((i-6)*stride,-12 if i==2 else 0),angle)
   if i==2:put(im,'tile-highlight',p,size,angle)
   else:put(im,'illegal-tile-badge',(p[0]+size[0]/2-8,p[1]-size[1]/2+8),(24,24))
 avatar=cfg['avatarCenter'];put(im,cfg['avatar'],avatar,(96,96));put(im,'avatar-frame',avatar,(111,113.4))
 if seat=='self':put(im,'current-player-ring',avatar,(128,114.9))
 put(im,'button-primary-normal',(avatar[0],avatar[1]+67),(140,44))
 text(im,'我' if seat=='self' else {'left':'左家','opposite':'对家','right':'右家'}[seat],(avatar[0],avatar[1]+67),21,fill='#FFF4D9')
 put(im,'ready-hand-badge',(avatar[0]-61,avatar[1]+27),(34,34));text(im,cfg['sampleWind'],(avatar[0]-61,avatar[1]+27),20,fill='#FFF4D9')
 if seat=='left':
  put(im,'offline-badge',(avatar[0]+83,avatar[1]),(34,32.8));put(im,'button-secondary-normal',(avatar[0]+83,avatar[1]+30),(90,28));text(im,'离线',(avatar[0]+83,avatar[1]+30),15)
 if seat=='opposite':
  put(im,'autoplay-badge',(avatar[0]+83,avatar[1]),(34,32.8));put(im,'button-secondary-normal',(avatar[0]+83,avatar[1]+30),(90,28));text(im,'托管',(avatar[0]+83,avatar[1]+30),15)
 if seat=='right':
  put(im,'dealer-badge',(avatar[0]-67,avatar[1]-38),(38,31.1));text(im,'庄',(avatar[0]-67,avatar[1]-38),19)
hud=table['centerHud'];put(im,'wind-round-dial',hud['center'],hud['size'])
for s,p in [('东',(790,475)),('南',(836,430)),('西',(882,475)),('北',(836,520))]:text(im,s,p,17,fill='#FFF4D9')
put(im,'countdown-frame',(836,488),(46,47.7));text(im,'12',(836,488),18,fill='#FFF4D9')
put(im,'button-secondary-normal',(695,452),(140,43));text(im,'第1局',(695,452),20)
put(im,'button-secondary-normal',(695,501),(140,43));text(im,'余牌56',(695,501),20)
text(im,'四座独立牌材组合 · 布局样例，不是合法牌局回放',(836,914),23,fill='#FFF4D9')
save(im,'table-four-seats','Four seats, visible/hidden hands, two wall layers, discards, called meld, illegal/selected hand, active player, dealer/offline/autoplay, dynamic wind and timer.')
# 2: rotations and four meld types, without perspective warps.
im=panelbg((2000,1510))
text(im,'四座方向与副露渲染样例（来源座位由数据指定）',(1000,45),36)
kinds=[('triplet','碰 · 横置来自他家的一张'),('open-kong','明杠 · 四张同牌'),('added-kong','加杠 · 原横牌上叠第四张'),('concealed-kong','暗杠 · 隐藏位只显示牌背')]
for index,(seat,cfg) in enumerate(seats.items()):
 qx=(index%2)*1000; qy=(index//2)*665+100; angle=cfg['clockwiseDegrees']
 text(im,f'{seat}  顺时针 {angle}° · 全牌与牌字同转',(qx+500,qy+25),27)
 for ki,(kind,label) in enumerate(kinds):
  cx=qx+255+(ki%2)*490;cy=qy+210+(ki//2)*290
  spr=meld(kind,angle)
  # Whole composite can be scaled down but never up.
  paste(im,spr,(cx,cy))
  text(im,label,(cx,cy+140),22)
text(im,'示例牌统一用六万以检验字头；这里只检查布局/身份/隐藏，不定义玩法或重复牌数量。',(1000,1480),24)
save(im,'melds-and-directions','16 independent compositions: triplet, open/added/concealed kong at each clockwise seat rotation. Native six-wan glyph makes mirroring and rotation observable.')
# 3: candidate chooser, ready hand, invalid, empty/disabled confirmation.
im=panelbg((1672,1000))
text(im,'候选、听牌与不可出牌状态 · 仅显示服务器候选，不由美术计算',(836,40),32)
put(im,'candidate-panel',(430,257),(560,239.26));text(im,'可选组合',(430,204),25)
for gi,aid in enumerate(['dragon-red','wind-east']):
 center=(325+gi*210,280)
 if gi==0:put(im,'candidate-selected-outline',center,(185,90))
 for ti in range(3):tile(im,aid,(center[0]+(ti-1)*39,center[1]),(35,50))
native9(im,'button-primary-normal',(535,420),(220,70));text(im,'确认',(535,420),26,fill='#FFF4D9')
native9(im,'button-secondary-normal',(285,420),(220,70));text(im,'取消',(285,420),26)
text(im,'唯一选中 · 确认前重新核对候选ID',(430,475),21)
put(im,'ready-hand-panel',(1200,257),(350,212.33));text(im,'听牌提示',(1200,214),24)
put(im,'ready-hand-badge',(1012,196),(40,39.4));text(im,'听',(1012,196),21,fill='#FFF4D9')
for aid,cx,count in [('wind-east',1160,'余4'),('dragon-red',1240,'余2')]:
 tile(im,aid,(cx,260),(31.5,45));text(im,count,(cx,296),18)
text(im,'数量缺失时不显示剩余数；候选为空可隐藏或显示空态',(1190,420),20)
put(im,'candidate-panel',(430,688),(560,239.26));text(im,'可选组合',(430,635),25)
text(im,'暂无可选组合',(430,713),26)
native9(im,'button-primary-disabled',(535,866),(220,70));text(im,'确认',(535,866),26,fill='#85877D')
native9(im,'button-secondary-normal',(285,866),(220,70));text(im,'取消',(285,866),26)
text(im,'无候选/超时/提交中：确认禁用',(430,925),22)
for si,(label,state) in enumerate([('正常',None),('选中','selected'),('不可出','illegal'),('最后弃牌',None)]):
 cx=970+si*175;cy=700
 tile(im,'wan-6',(cx,cy-12 if state=='selected' else cy),(70,100),state=state)
 if si==3:put(im,'discard-pointer',(cx,620),(28,31))
 text(im,label,(cx,790),22)
text(im,'不可出：灰化、角标和禁点；理由使用原生文字',(1210,866),22)
text(im,'最后弃牌指针跟随整牌座位旋转；牌被副露取走后隐藏',(1210,924),19)
save(im,'candidates-and-states','Candidate exact tile identities, single selected outline, native confirm/cancel, disabled empty state, ready-hand counts, invalid badge, selected lift and last-discard pointer.')
# 4: settlement rows use accepted 9-slice card, native fields and portrait.
im=background();put(im,'window-frame',(836,470),(1560,844))
native9(im,'content-card',(836,470),(1390,710))
put(im,'title-plaque',(836,130),(500,172.58));text(im,'本局结算',(836,125),38,fill='#FFF4D9')
for i,(who,name,score) in enumerate([('daotong','金带道童','+12'),('healer','银发医师','-4'),('master','白眉老道','-4'),('swordswoman','黑发侠女','-4')]):
 y=260+i*125;native9(im,'content-card',(836,y),(1040,118))
 put(im,'avatar-'+who,(410,y),(80,80));text(im,name,(600,y),29)
 text(im,'本局积分',(958,y),24)
 text(im,score,(1190,y),36,fill='#B52F20' if score.startswith('+') else '#196448')
native9(im,'button-secondary-normal',(592,801),(290,82));text(im,'返回大厅',(592,801),30)
native9(im,'button-primary-normal',(1080,801),(320,82));text(im,'继续下一局',(1080,801),30,fill='#FFF4D9')
text(im,'原生昵称/分数/结果；示例分数不定义规则；整场结束隐藏继续按钮',(836,873),21)
save(im,'settlement-composition','Independent background, transparent frame, nine-slice cards and buttons, portraits and native Chinese/score fields. Scores retain signs and color; match completion removes continue.')
# 5: six exported assets on light and dark, at typical runtime scales.
im=Image.new('RGBA',(1600,1000),'#EDE5CF')
ImageDraw.Draw(im).rectangle((800,0,1600,1000),fill='#123F35')
manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
for side in range(2):
 base=side*800;color='#183D35' if side==0 else '#FFF4D9'
 text(im,'浅底 / 常用显示尺寸' if side==0 else '深底 / 真Alpha检查',(base+400,42),30,fill=color)
 for i,a in enumerate(manifest['assets']):
  y=140+i*140; size=(400,112) if i<3 else (64,64)
  put(im,a['id'],(base+430,y),size)
  text(im,a['name'],(base+133,y),20,fill=color)
save(im,'skins-alpha-light-dark','Six native atlas slices at actual game-size or smaller on light and dark backgrounds; no drawn replacement artwork.')
print('Rendered five previews from independent source assets.')

