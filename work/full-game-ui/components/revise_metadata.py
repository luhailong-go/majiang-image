from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib,numpy as np
R=Path(r'D:\work\majiang-image');D=R/'assets/ui/full-game/components';NOW=datetime.now(timezone(timedelta(hours=-4))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
c=read(D/'compositions.json');claim=c['compositions']['rewardCard']['states']['claimable']
claim['actionFamily']='primary';claim['actionFamilySource']='assets/ui/component-compositions.json'
assert claim['actionFamily'] in read(R/claim['actionFamilySource'])['buttonFamilies']
arrow=D/'tutorial-arrow.png';im=Image.open(arrow);a=np.asarray(im.getchannel('A'));w,h=im.size;x,y=350,313
assert (w,h)==(396,334) and int(a[y,x])>128
ys,xs=np.where(a>128);lowest=int(ys.max());bottomxs=xs[ys==lowest]
hotspot={'pointPixels':[x,y],'pointNormalized':[x/w,y/h],'normalization':'x / imageWidth, y / imageHeight; origin top-left; coordinates refer to full delivered PNG canvas.','imageDimensions':[w,h],'role':'arrow tip target alignment','evidence':{'sampleAlpha':int(a[y,x]),'strongAlphaThreshold':128,'lowestStrongRowY':lowest,'lowestStrongRowXRange':[int(bottomxs.min()),int(bottomxs.max())],'basis':'Native pixel inspection; chosen point lies in the opaque lower arrowhead near the terminal tip.'},'assetSha256':sha(arrow)}
t=c['compositions']['tutorial'];t['arrowTipNormalized']=hotspot['pointNormalized'];t['arrowTipPixels']=hotspot['pointPixels'];t['arrowTipEvidence']=hotspot['evidence'];t['arrowTipNormalization']=hotspot['normalization']
save(D/'compositions.json',c)
rp=D/'tutorial-arrow.png.generation.json';rec=read(rp);rec['hotspot']=hotspot;save(rp,rec)
readme=D/'README.md';text=readme.read_text(encoding='utf-8-sig')
addition='\n## 精确接入点\n\n领取动作引用旧 `assets/ui/component-compositions.json` 的 `buttonFamilies.primary`，组合清单明确记录 `actionFamilySource`。教程箭头原生396×334，目标对齐点为左上原点像素(350,313)，归一化坐标为(0.8838383838383839, 0.937125748502994)，按x/宽、y/高计算。该像素Alpha245；Alpha>128的最下行是y315、x344—351。此处修正仅涉及接入元数据，PNG内容和哈希保持不变。\n'
if '\n## 精确接入点\n' not in text:text+=addition
readme.write_text(text,encoding='utf-8')
m=read(D/'manifest.json');aentry=next(a for a in m['assets'] if a['id']=='tutorial-arrow');aentry['hotspot']=hotspot
meta=[{'file':rel(p),'sha256':sha(p)} for p in [D/'compositions.json',readme]]
m['supportingMetadata']=meta;m['metadataCheckedAt']=NOW;save(D/'manifest.json',m)
q=read(D/'qa.json');q['metadataCheckedAt']=NOW;q['metadataChecks']={'buttonFamilyLookup':{'status':'passed','source':claim['actionFamilySource'],'key':claim['actionFamily']},'tutorialArrowHotspot':{'status':'passed',**hotspot},'pngHashesUnchanged':all(sha(R/e['file'])==e['sha256'] for e in m['assets'])};assert q['metadataChecks']['pngHashesUnchanged']
q['supportingMetadata']=meta+[{'file':rel(D/'manifest.json'),'sha256':sha(D/'manifest.json')}];save(D/'qa.json',q)
if __name__=='__main__':print(json.dumps({'status':'passed','pngHashesUnchanged':True,'hashes':{p.name:sha(p) for p in [D/'manifest.json',D/'compositions.json',D/'qa.json',readme]},'arrowHotspot':hotspot},ensure_ascii=False))
