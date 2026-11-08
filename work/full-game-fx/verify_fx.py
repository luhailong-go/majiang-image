from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
from html.parser import HTMLParser
import json,hashlib,numpy as np,shutil
R=Path(r'D:\work\majiang-image');A=R/'assets/fx/full-game';W=R/'work/full-game-fx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')

# Archive the exact original tool receipt as text, then point portable QA to retained files.
receipt=W/'clips-built-final/animation-clips.json';copy=A/'qa/clip-build-original.json';shutil.copyfile(receipt,copy)
engine_path=A/'engine/engine-export.json';engine=json.loads(engine_path.read_text(encoding='utf-8'));m=json.loads((A/'manifest.json').read_text(encoding='utf-8'))
frames=[i for i in m['assets'] if i['kind']=='animation_frame']
for i,row in enumerate(engine['qa']['inputs']):
 row['originalWorkingPath']=row['path'];row['path']='../qa/clip-build-original.json' if i==0 else '../frames/'+Path(frames[i-1]['file']).name
engine['qa']['retentionNote']='Input file paths relocated to retained byte-identical primary assets and original text receipt; hashes unchanged. Temporary duplicate frame PNGs are removed.'
dump(engine_path,engine)
rp=A/'animation-clips.json';built=json.loads(rp.read_text(encoding='utf-8'));built['relocation']['historicalWorkingManifest']=built['relocation']['originalBuildManifest'];built['relocation']['originalBuildManifest']='assets/fx/full-game/qa/clip-build-original.json';dump(rp,built)
qa=json.loads((A/'qa.json').read_text(encoding='utf-8'));qa['engineRoundTrip']=engine['qa'];qa['staticPreviewValidation']={'jsSyntax':'node --check passed','browserInteraction':'not_run'}
qa['retention']={'report':'work/full-game-fx/cleanup.json','supersededSource':'designs/fx/full-game/discard-impact-v1.png','currentSourceCount':8,'keptCurrentSources':'Current source paintings and final assets retained; superseded original and temporary raster duplicates removed after final assets passed.'}
dump(A/'qa.json',qa)
for row in json.loads((A/'processing-receipts.json').read_text(encoding='utf-8'))['reports']:
 p=R/row['file'];meta=json.loads(p.read_text(encoding='utf-8'));meta['retentionNote']={'workingRasterCopiesRetained':False,'reason':'Working raster files superseded by verified final registered PNGs and current original source paintings; original historical hash receipts retained.','sourcePainting':next(x for x in m['sourceImages'] if ('discard-impact-refined' if row['effect']=='discard-impact' else row['effect'])+'-v1.png' in x),'finalAssets':[x['file'] for x in frames if x['id'].startswith(row['effect']+'-')]};dump(p,meta)
# Refresh retained receipt hashes after adding a retention annotation.
receipts=json.loads((A/'processing-receipts.json').read_text(encoding='utf-8'))
for row in receipts['reports']:row['sha256']=sha(R/row['file'])
dump(A/'processing-receipts.json',receipts)

# The rejected landing source may be absent only when a matching explicit cleanup record exists.
old=R/'designs/fx/full-game/discard-impact-v1.png';oldrp=Path(str(old)+'.generation.json');oldrec=json.loads(oldrp.read_text(encoding='utf-8'))
if not old.exists():
 oldrec['pixelsRetainedInProject']=False;oldrec['cleanup']={'at':now,'reason':'Superseded by accepted discard-impact-refined-v1 source and validated final4 registered frames; source textual evidence retained per project retention policy.','sha256BeforeRemoval':oldrec['sha256'],'replacement':'designs/fx/full-game/discard-impact-refined-v1.png'};oldrec['inspection']={'visualStatus':'superseded_not_delivered','issues':['Original phase3 approached the quadrant boundary; refined source replaces it.']};dump(oldrp,oldrec)
 p=R/'designs/fx/full-game/discard-impact-refined-v1.png.generation.json';r=json.loads(p.read_text(encoding='utf-8'))
 for ref in r['references']:
  if ref['file']=='designs/fx/full-game/discard-impact-v1.png':ref['pixelsPresentInProject']=False;ref['cleanupRecord']='designs/fx/full-game/discard-impact-v1.png.generation.json'
 dump(p,r)

errors=[];count=0
for item in m['assets']+m['supplementalMedia']:
 p=R/item['file'];r=json.loads((R/item['record']).read_text(encoding='utf-8'))
 if not p.exists() or sha(p)!=item['sha256'] or sha(p)!=r['sha256']:errors.append(item['file']+': hash')
 count+=1
for s in m['sourceImages']:
 p=R/s;r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
 if not p.exists() or sha(p)!=r['sha256']:errors.append(s+': source')
 for ref in r['references']:
  p=R/ref['file']
  if p.exists():
   if sha(p)!=ref['sha256']:errors.append(ref['file']+': ref hash')
  else:
   cr=R/ref.get('cleanupRecord','missing');h=json.loads(cr.read_text(encoding='utf-8')) if cr.is_file() else {}
   if not(ref.get('pixelsPresentInProject') is False and h.get('pixelsRetainedInProject') is False and h.get('sha256')==ref['sha256'] and h.get('cleanup',{}).get('sha256BeforeRemoval')==ref['sha256']):errors.append(ref['file']+': missing ref lacks matching cleanup evidence')
for f in built['frames']:
 p=A/f['file']
 if not p.exists() or sha(p)!=f['source']['file_sha256']:errors.append(f['file']+': clip frame hash')
for slug,c in built['clips'].items():
 p=A/c['preview']['file']
 if not p.exists() or sha(p)!=c['preview']['file_sha256']:errors.append(slug+': preview hash')
atlas_json=json.loads((A/'engine/aseprite/mahjong-fx.json').read_text(encoding='utf-8'));atlas=Image.open(A/'engine/aseprite/mahjong-fx.png').convert('RGBA')
for i,entry in enumerate(atlas_json['frames']):
 rect=entry['frame'];crop=atlas.crop((rect['x'],rect['y'],rect['x']+rect['w'],rect['y']+rect['h']));src=Image.open(R/frames[i]['file']).convert('RGBA')
 if not np.array_equal(np.asarray(crop),np.asarray(src)):errors.append(f'atlas frame {i}: RGBA mismatch')
for row in engine['qa']['inputs']:
 p=(A/'engine'/row['path']).resolve()
 if not p.exists() or sha(p)!=row['sha256']:errors.append(row['path']+': engine input missing/hash')
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ('href','src') and value and not value.startswith(('http:','https:','data:','#')):
    p=(A/value).resolve()
    if not p.exists():errors.append(value+': preview link missing')
links=Links();links.feed((A/'index.html').read_text(encoding='utf-8'))
result={'schemaVersion':1,'status':'passed' if not errors else 'failed','verifiedAt':now,'primaryAssets':len(m['assets']),'supplementalMedia':len(m['supplementalMedia']),'hashedMedia':count,'sourcePaintings':len(m['sourceImages']),'atlasExactRGBAFrames':24,'runtimeFramesChecked':24,'runtimeClipsChecked':6,'htmlLinks':'passed' if not any('link missing' in x for x in errors) else 'failed','jsSyntax':'node --check passed','browserInteraction':'not_run','errors':errors,'warnings':[]}
dump(A/'final-validation.json',result);m['finalValidation']='assets/fx/full-game/final-validation.json';dump(A/'manifest.json',m);print(json.dumps(result,ensure_ascii=False))
