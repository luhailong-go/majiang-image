"""Add provenance for retained previews and freeze reviewed final domain records."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'assets/characters/full-game'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat();m=read(OUT/'manifest.json');qa=read(OUT/'qa.json')
for kind,role,cell in [('bodies','full_body',[384,440]),('expressions','expression_avatar',[320,360])]:
 group=[a for a in m['assets'] if a['role']==role]
 for tone,color in [('light',[246,238,218]),('dark',[14,44,39])]:
  p=OUT/f'preview-{kind}-{tone}.png';im=Image.open(p)
  d={'schemaVersion':1,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'exportedAt':now,'width':im.width,'height':im.height,'format':'PNG','mode':'RGB','newModelGeneration':False,'tool':'Pillow deterministic contact-sheet layout','route':'local_derivative','actualModel':None,'actualQuality':None,'unverifiedReason':'This contact sheet is not an AI generation. Follow each derivedFrom source record for actual model/quality evidence.','derivedFrom':[{'file':a['file'],'sha256':a['sha256'],'generationRecord':a['record']} for a in group],'operation':[{'operation':'premultiplied-alpha uniform thumbnail downsample and grid layout','columns':4,'rows':(len(group)+3)//4,'cellSize':cell,'contentMaxSize':[cell[0]-24,cell[1]-54],'nativeDetailUpscaled':False},{'operation':'composite onto opaque inspection background','backgroundRgb':color,'tone':tone},{'operation':'draw labels from manifest names','font':'Microsoft YaHei; system msyh.ttc or Pillow fallback','fontSize':24}],'purpose':'retained final visual QA/design contact sheet, not runtime asset','userApproved':False,'clientIntegrated':False}
  write(Path(str(p)+'.generation.json'),d)
qa['independentReview']={'reviewer':'root coordinator','checkedAt':now,'evidence':'Parent agent confirmed actual view_image review of all four final contact sheets in collaboration message before freeze','scope':'4 bodies,16 expressions, light and dark composites','status':'passed','findings':'distinct identities, complete hands/feet/ribbons, clear emotions, no abnormal residual edge shadows','userApproval':False}
qa['frozenAt']=now;m['frozenAt']=now
write(OUT/'qa.json',qa);write(OUT/'manifest.json',m)
print(json.dumps({'status':'frozen','at':now,'manifestSha256':sha(OUT/'manifest.json'),'qaSha256':sha(OUT/'qa.json'),'runtimeItems':len(m['assets']),'nativeSourcePngs':len(list((ROOT/'designs/characters/full-game').glob('*.png'))),'previewRecords':4,'remainingWorkPngs':len(list((ROOT/'work/full-game-characters').glob('*.png')))},ensure_ascii=False))
