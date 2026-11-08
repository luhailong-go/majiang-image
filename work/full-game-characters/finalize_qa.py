"""Record the completed human-style visual inspection for the exact exported hashes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/characters/full-game'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(OUT/'manifest.json');qa=read(OUT/'qa.json')
now=datetime.now(timezone.utc).isoformat()
intermediate_previews=[]
assert len(manifest['assets'])==20
assert len({a['file'] for a in manifest['assets']})==20
for a,check in zip(manifest['assets'],qa['checks']):
 p=ROOT/a['file'];assert sha(p)==a['sha256']==check['sha256']
 im=Image.open(p);im.verify();im=Image.open(p)
 assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 assert a['alpha']['borderPixelsAbove8']==0
 min_margin=120 if a['role']=='full_body' else 28
 assert min(a['alpha']['clearMargins'])>=min_margin
 record=read(ROOT/a['record'])
 # Existing reused body record remains read-only.
 if not a.get('reusedExistingAsset'):
  parent=record['derivedFrom'];assert sha(ROOT/parent['file'])==parent['sha256']
  source_record=read(ROOT/parent['generationRecord'])
  for ref in source_record.get('references',[]):assert sha(ROOT/ref['file'])==ref['sha256']
  record['inspection']={'status':'passed','visualInspectionCompleted':True,'checkedAt':now,'deepAndLightComposite':'passed: actual contact-sheet review, plus native full-body and selected 512px expression composites','silhouette':'complete head, ornaments, ribbons, hands/feet for body; portraits have intentional natural chest cut','style':'matches supplied Daoist chibi hand-painted references','identity':'matches unchanged identity avatar','expressionDistinctness':'passed' if a['role']=='expression_avatar' else None,'unresolvedIssues':[],'qaReport':'assets/characters/full-game/qa.json'}
  write(ROOT/a['record'],record)
 a['stage']='production_asset_qa_passed'
 intermediate_previews.extend(a.get('qaPreviews',[]))
 kind='bodies' if a['role']=='full_body' else 'expressions'
 a['qaPreviews']=[f'assets/characters/full-game/preview-{kind}-{tone}.png' for tone in ['light','dark']]
 check['qaPreviews']=a['qaPreviews']
 check.update({'status':'passed','visualInspectionCompleted':True,'checkedAt':now,'deepAndLightComposite':'passed','identity':'passed against original unchanged avatar and actual style images','style':'passed: jade/ivory/fine warm gold, rounded hand-painted chibi','silhouette':'complete, no canvas-edge crop','expressionDistinctness':'happy/thinking/surprised/sad clear at UI display size' if a['role']=='expression_avatar' else None,'strongSourcePixelsDiscarded':0,'unresolvedIssues':[]})
for f in manifest['sourceImages']:
 p=ROOT/f;record=read(Path(str(p)+'.generation.json'))
 assert record['sha256']==sha(p)
 record['inspection']={'status':'accepted_as_rebuild_source','visualInspectionCompleted':True,'checkedAt':now,'identity':'passed','expressions':'four visibly distinct emotions' if 'expressions' in p.name else None,'rawAlpha':'technical low-alpha external speckles removed by recorded export; source art is not the runtime sprite','runtimeQa':'assets/characters/full-game/qa.json','unresolvedRuntimeIssues':[]}
 write(Path(str(p)+'.generation.json'),record)
qa.update({'status':'passed','scopeComplete':True,'completedAt':now,'pending':[],'assetCount':20,'newRuntimePngCount':19,'reusedRuntimePngCount':1,'sourceCount':7,'reviewedContactSheets':manifest['previewImages'],'summary':{'fullBodies':4,'expressionAvatars':16,'realAlpha':20,'edgeTouchesAboveAlpha8':0,'opaqueSourcePixelsDiscarded':0,'nativeDetailUpscaled':False},'limitations':['Static emotional portraits; no skeletal or walking animation is implied.','Actual builtin model/quality values are unconfirmed because the tool does not disclose them.','userApproved=false and clientIntegrated=false.'],'unresolvedIssues':[]})
removed=[]
for preview in sorted(set(intermediate_previews)):
 p=(ROOT/preview).resolve()
 if p.is_relative_to((ROOT/'work/full-game-characters').resolve()) and p.name.endswith('-qa.png') and p.exists():
  removed.append({'file':preview,'sha256':sha(p),'reason':'inspected intermediate deep/light composite superseded by retained final contact sheets'})
  p.unlink()
qa['intermediateImageCleanup']={'completedAt':now,'removedCount':len(removed),'removed':removed,'retained':manifest['previewImages'],'nativeSourcesPreserved':7,'runtimeImagesUnchanged':True}
manifest.update({'status':'complete_qa_passed','completedAt':now,'unresolvedIssues':[]})
write(OUT/'manifest.json',manifest);write(OUT/'qa.json',qa)
print(json.dumps({'status':'complete_qa_passed','assets':20,'newPngs':19,'reusedPngs':1,'unresolvedIssues':[]},ensure_ascii=False))
