from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json
R=Path(r'D:\work\majiang-image')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
source=R/'designs/ui/full-game/core/ui27-tutorial-select-source.png.generation.json'
s=read(source); s['status']['productionAccepted']=False; s['status']['stage']='retained_edit_source'; s['inspection']['visualStatus']='needs_correction'; s['inspection']['issues']=['页脚右下存在极小无意义笔画，已由最终版修正。']; s['inspection']['blockingIssues']=s['inspection']['issues']; s['retainedReason']='最终版AI编辑实际参考，保留像素以维持可核对来源。';write(source,s)
final=R/'designs/ui/full-game/core/ui27-tutorial-select.png.generation.json'
s=read(final);s['generationType']='ai_edit';s['editTarget']='designs/ui/full-game/core/ui27-tutorial-select-source.png'
for ref in s['references']: ref['purpose']='AI编辑对象' if ref['file']==s['editTarget'] else '主UI风格'
write(final,s)
items=[]
for p in sorted((R/'designs/ui/full-game/core').glob('*.png.generation.json')):
 d=read(p)
 if not d['status']['productionAccepted']: continue
 items.append({k:d[k] for k in ['file','uiId','title','sha256','width','height','mode','prompt','coveredStates']}|{'record':str(p.relative_to(R)).replace('\\','/'),'recordSha256':sha(p),'productionAccepted':True,'clientIntegrated':False})
assert len(items)==5
m={'schemaVersion':2,'scope':'full_game_ui_core','createdAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'status':'passed','pageCount':5,'uiIds':['UI25','UI26','UI27'],'assets':items,'actualModel':None,'actualQuality':None,'retainedEditSources':[{'file':'designs/ui/full-game/core/ui27-tutorial-select-source.png','record':'designs/ui/full-game/core/ui27-tutorial-select-source.png.generation.json','productionAccepted':False}],'failedAttemptRecords':['work/full-game-ui/core/ui27-select-cleanup-failed.png.generation.json'],'clientIntegrated':False}
m['retainedEditSources'].append({'file':'designs/ui/full-game/core/ui25-customization-source.png','record':'designs/ui/full-game/core/ui25-customization-source.png.generation.json','productionAccepted':False})
write(R/'designs/ui/full-game/core/manifest.json',m)
write(R/'designs/ui/full-game/core/qa.json',{'status':'passed','pageCount':5,'uiIds':m['uiIds'],'blockingIssues':[],'checks':['actual full image visual review','Chinese text and state consistency','dimensions and SHA-256','input references and prompts','tutorial sequence and selectable action availability'],'nativeDimensions':[1672,941],'actualModel':None,'actualQuality':None,'limitations':['Artwork and state specification only; no client runtime integration.','No real browser testing because file:// was rejected.'],'pages':items})
qp=R/'designs/ui/full-game/core/qa.json';q=read(qp);q.pop('nativeDimensions',None);q['nativeDimensionsByFile']={d['file']:[d['width'],d['height']] for d in items};write(qp,q)
print(json.dumps({'status':'passed','pages':len(items),'manifestSha256':sha(R/'designs/ui/full-game/core/manifest.json')},ensure_ascii=False))
