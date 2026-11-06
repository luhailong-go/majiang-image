from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
import numpy as np, json, hashlib, shutil
from datetime import datetime, timezone, timedelta
R=Path(r"D:\work\majiang-image")
SRC=R/"designs/ui/component-sources"; QA=R/"work/components/qa"
QA.mkdir(parents=True,exist_ok=True)
for d in ["assets/ui/common","assets/ui/gameplay"]:(R/d).mkdir(parents=True,exist_ok=True)
NOW=datetime.now(timezone(timedelta(hours=-4))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def stats(im):
 a=np.asarray(im.getchannel("A"))
 return {"range":[int(a.min()),int(a.max())],"fullyTransparent":int((a==0).sum()),"semiTransparent":int(((a>0)&(a<255)).sum()),"opaque":int((a==255).sum()),"bbox":im.getchannel("A").getbbox(),"corners":[int(a[0,0]),int(a[0,-1]),int(a[-1,0]),int(a[-1,-1])]}
def clean(im):
 arr=np.array(im.convert("RGBA")); a=arr[:,:,3].copy(); initial=a.copy()
 a[a<=8]=0
 parent=[]; strong=[]; spans=[]; previous=[]
 def find(x):
  while parent[x]!=x:
   parent[x]=parent[parent[x]]; x=parent[x]
  return x
 def union(aid,bid):
  aa,bb=find(aid),find(bid)
  if aa!=bb: parent[bb]=aa; strong[aa]=strong[aa] or strong[bb]
 for y in range(a.shape[0]):
  delta=np.diff(np.pad((a[y]>0).astype(np.int8),(1,1)))
  starts=np.flatnonzero(delta==1); ends=np.flatnonzero(delta==-1)
  current=[]; pi=0
  for x0,x1 in zip(starts,ends):
   lab=len(parent);parent.append(lab);strong.append(bool(a[y,x0:x1].max()>=128))
   while pi<len(previous) and previous[pi][1]<x0:pi+=1
   k=pi
   while k<len(previous) and previous[k][0]<=x1:
    union(lab,previous[k][2]);k+=1
   current.append((int(x0),int(x1),lab));spans.append((y,int(x0),int(x1),lab))
  previous=current
 for y,x0,x1,lab in spans:
  if not strong[find(lab)]:a[y,x0:x1]=0
 removed=int(((initial>0)&(a==0)).sum())
 strong_removed=int(((initial>=128)&(a==0)).sum())
 a[a>=250]=255
 arr[:,:,3]=a;arr[a==0,:3]=0
 return Image.fromarray(arr),{"thresholdAlpha":8,"removeFloatingComponentsWithoutAlphaAtLeast128":True,"normalizeAlpha250To255":True,"removedPixels":removed,"removedAlphaAtLeast128":strong_removed,"zeroRGBUnderZeroAlpha":True}
assets=[]
def write_asset(im,name,group,source,operation,box=None,nine=None,padding=0,cleanup=None,title=None,variant=None):
 target=R/"assets/ui"/group/(name+".png");im.save(target)
 record={"schemaVersion":1,"file":rel(target),"sha256":sha(target),"exportedAt":NOW,"kind":"derived_ui_asset","generatedByModel":False,"actualModel":None,"actualQuality":None,"width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"nativeSourceDimensions":None,"derivedFrom":None,"operation":operation,"crop":box,"transparentPadding":padding,"resampled":False,"anchor":{"x":0.5,"y":0.5},"nineSlice":nine,"alpha":stats(im) if im.mode=="RGBA" else None,"dynamicText":"Separate native client text; no text baked into this skin.","inspection":{"status":"technical_passed_visual_pending","issues":[]},"productionAccepted":False}
 if source:
  with Image.open(source) as raw:record["nativeSourceDimensions"]={"width":raw.width,"height":raw.height}
  recpath=source.with_name(source.name+".generation.json")
  record["derivedFrom"]={"file":rel(source),"sha256":sha(source),"record":rel(recpath) if recpath.exists() else None}
 if cleanup:record["alphaCleanup"]=cleanup
 if variant:record["stateTransform"]=variant
 rp=target.with_name(target.name+".generation.json");rp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 entry={"id":name,"name":title or name,"file":rel(target),"record":rel(rp),"sha256":record["sha256"],"width":im.width,"height":im.height,"mode":im.mode,"group":group,"nineSlice":nine,"anchor":{"x":0.5,"y":0.5},"alpha":record["alpha"],"status":"technical_passed_visual_pending"}
 assets.append(entry)
 return target
def extract(source_name,name,group,box,nine=None,title=None,padding=8):
 source=SRC/(source_name+".png")
 im=Image.open(source).convert("RGBA").crop(box); cleaned,log=clean(im)
 bb=cleaned.getchannel("A").getbbox()
 if bb is None:raise RuntimeError("Empty sprite "+name)
 aa=np.asarray(cleaned.getchannel("A"));touch=bool((aa[0,:]>=128).any() or (aa[-1,:]>=128).any() or (aa[:,0]>=128).any() or (aa[:,-1]>=128).any())
 if touch:raise RuntimeError("Strong foreground touches crop for "+name)
 trimmed=cleaned.crop(bb)
 out=Image.new("RGBA",(trimmed.width+2*padding,trimmed.height+2*padding))
 out.paste(trimmed,(padding,padding))
 crop=[box[0]+bb[0],box[1]+bb[1],box[0]+bb[2],box[1]+bb[3]]
 return write_asset(out,name,group,source,"native crop + low-alpha/isolated speck removal + transparent padding; no scaling",crop,nine,padding,log,title)
extract("window-frame-v1","window-frame","common",[0,0,1672,941],[200,200,200,200],"透明九宫格窗框",12)
skins=[
("title-plaque",[0,0,636,340],None,"无字标题牌"),
("content-card",[636,0,1254,340],[45,45,45,45],"内容卡片"),
("button-primary-normal",[0,340,636,660],[80,28,80,28],"主按钮·正常"),
("button-secondary-normal",[636,340,1254,660],[80,28,80,28],"次按钮·正常"),
("tab-selected",[0,660,636,930],[60,24,60,24],"页签·选中"),
("tab-normal",[636,660,1254,930],[60,24,60,24],"页签·未选中"),
("input-field",[0,930,636,1254],[34,30,34,30],"输入框"),
("tooltip-bubble",[636,930,1254,1254],None,"提示气泡")]
for name,box,nine,title in skins:extract("common-skins-atlas-v1",name,"common",box,nine,title)
controls=[
("icon-settings",[0,0,320,306]),("icon-close",[320,0,640,306]),("icon-back",[640,0,940,306]),("icon-chat",[940,0,1254,306]),
("icon-profile",[0,306,320,565]),("icon-friends",[320,306,640,565]),("icon-mail",[640,306,940,565]),("icon-records",[940,306,1254,565]),
("icon-sound",[0,565,320,790]),("icon-muted",[320,565,640,790]),("checkbox-on",[640,565,940,790]),("checkbox-off",[940,565,1254,790]),
("radio-on",[0,790,320,1013]),("radio-off",[320,790,640,1013]),("slider-thumb",[640,790,940,1013]),("scrollbar-thumb",[940,778,1254,1013]),
("slider-track",[0,1013,430,1254]),("scrollbar-track",[430,1013,640,1254]),("unread-badge",[640,1013,940,1254]),("loading-ring",[940,1013,1254,1254])]
for name,box in controls:
 nine=[45,24,45,24] if name=="slider-track" else [24,45,24,45] if name=="scrollbar-track" else None
 extract("common-controls-atlas-v1",name,"common",box,nine)
game=[
("wind-round-dial",[0,0,492,480],None,"中央风位与回合牌"),
("avatar-frame",[490,0,910,480],None,"四座共用头像框"),
("countdown-frame",[910,0,1254,475],None,"倒计时框"),
("dealer-badge",[0,480,425,890],None,"庄家徽章底图"),
("current-player-ring",[425,475,925,915],None,"当前玩家高亮圈"),
("offline-badge",[925,480,1254,840],None,"离线标记"),
("autoplay-badge",[0,890,350,1254],None,"托管标记"),
("action-button-normal",[350,920,925,1254],[70,30,70,30],"对局操作按钮"),
("settlement-card",[925,840,1254,1254],None,"结算卡片")]
for name,box,nine,title in game:extract("gameplay-components-atlas-v1",name,"gameplay",box,nine,title)
for group,base in [("common","button-primary"),("common","button-secondary"),("gameplay","action-button")]:
 source=R/"assets/ui"/group/(base+"-normal.png");im=Image.open(source).convert("RGBA")
 entry=next(e for e in assets if e["id"]==base+"-normal")
 for state in ["pressed","selected","disabled"]:
  rgb=im.convert("RGB")
  if state=="pressed":rgb=ImageEnhance.Brightness(rgb).enhance(.78);transform={"brightness":.78}
  elif state=="selected":rgb=ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(1.12)).enhance(1.12);transform={"brightness":1.12,"color":1.12}
  else:rgb=Image.blend(rgb,ImageOps.grayscale(rgb).convert("RGB"),.82);rgb=ImageEnhance.Contrast(rgb).enhance(.72);transform={"grayscaleBlend":.82,"contrast":.72}
  out=rgb.convert("RGBA");out.putalpha(im.getchannel("A"))
  ar=np.array(out);ar[ar[:,:,3]==0,:3]=0;out=Image.fromarray(ar)
  write_asset(out,base+"-"+state,group,source,"deterministic UI state color transform; geometry and alpha preserved",nine=entry["nineSlice"],title=base+"·"+state,variant=transform)
# Native content-card skin provides unlabelled numeric keys; its labels are in composition metadata.
keysource=R/"assets/ui/common/content-card.png";keyim=Image.open(keysource)
write_asset(keyim,"keypad-key","common",keysource,"byte-identical skin reuse for native-labelled numeric keys",nine=[45,45,45,45],title="数字键盘共用无字键")
mask=Image.new("RGBA",(8,8),(0,0,0,144))
write_asset(mask,"modal-shade","common",None,"constant RGBA runtime overlay primitive, 8x8 black alpha144; not AI artwork",title="遮罩")
p=SRC/"table-background-v1.png";bg=Image.open(p).convert("RGB")
write_asset(bg,"table-background","gameplay",p,"pixel-identical native RGB PNG re-encode; metadata stripped; no resampling",title="独立牌桌背景")
# The second atlas may be completed separately.
if (SRC/"common-extra-icons-v1.png").exists():
 extra_names=["icon-search","icon-add","icon-delete","icon-voice","icon-help","icon-lock","icon-copy","icon-confirm"]
 with Image.open(SRC/"common-extra-icons-v1.png") as raw:w,h=raw.size
 for i,name in enumerate(extra_names):
  boxes=[[0,0,445,530],[445,0,810,530],[810,0,1170,530],[1170,0,1536,530],[0,530,450,1024],[450,530,800,1024],[800,530,1170,1024],[1170,530,1536,1024]]; x0,y0,x1,y1=[round(v*(w/1536 if k%2==0 else h/1024)) for k,v in enumerate(boxes[i])]
  extract("common-extra-icons-v1",name,"common",[x0,y0,x1,y1])
manifest={"schemaVersion":1,"generatedAt":NOW,"scope":"FULL_UI_SCOPE common and gameplay components","actualModel":None,"actualQuality":None,"userApproved":False,"clientIntegrated":False,"assets":assets,"compositionFile":"assets/ui/component-compositions.json","sources":[rel(p) for p in sorted(SRC.glob("*.png"))],"notes":["All painted skins derive from builtin generated masters; crop and alpha cleanup are mechanical exports.","All text and numeric values are separate native client labels.","Nine-slice is [left,top,right,bottom] in delivered pixels. Null means aspect-preserving scaling only."]}
(R/"assets/ui/manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for group in ["common","gameplay"]:
 subset={**manifest,"assets":[a for a in assets if a["group"]==group]}
 (R/"assets/ui"/group/"manifest.json").write_text(json.dumps(subset,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# QA contact sheets over actual light and dark backdrops.
font=ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc",14)
for group in ["common","gameplay"]:
 subset=[a for a in assets if a["group"]==group and a["id"]!="table-background"]
 cols=5;cw=260;ch=215;rows=(len(subset)+cols-1)//cols
 for mode,bgcolor in [("light",(245,237,216)),("dark",(18,48,40))]:
  sheet=Image.new("RGB",(cols*cw,rows*ch),bgcolor);draw=ImageDraw.Draw(sheet)
  for i,a in enumerate(subset):
   im=Image.open(R/a["file"]).convert("RGBA");im.thumbnail((cw-20,ch-40))
   x=(i%cols)*cw+(cw-im.width)//2;y=(i//cols)*ch+10
   sheet.paste(im,(x,y),im)
   color=(20,60,45) if mode=="light" else (245,237,216)
   draw.text(((i%cols)*cw+8,(i//cols)*ch+ch-25),a["id"],fill=color,font=font)
  sheet.save(QA/(group+"-"+mode+".png"))
print(json.dumps({"count":len(assets),"common":sum(a["group"]=="common" for a in assets),"gameplay":sum(a["group"]=="gameplay" for a in assets),"allStrongForegroundPreserved":True},ensure_ascii=False))


