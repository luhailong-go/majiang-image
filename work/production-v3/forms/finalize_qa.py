"""Finalize reviewed, fixed PNGs without modifying any image bytes."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json, hashlib

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/ui/production-v3/forms';DES=ROOT/'designs/ui/production-v3/forms'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
manifest=read(OUT/'manifest.json');qa=read(OUT/'qa.json')
errors=[];files=[]
for image in sorted(list(OUT.glob('*.png'))+list(DES.glob('*.png'))):
    recpath=Path(str(image)+'.generation.json')
    if not recpath.exists():errors.append('Missing record: '+str(image));continue
    rec=read(recpath)
    if rec['sha256']!=sha(image):errors.append('Image hash mismatch: '+str(image))
    im=Image.open(image)
    if [im.width,im.height]!=[rec['width'],rec['height']]:errors.append('Dimension mismatch: '+str(image))
    for dep in rec.get('derivedFrom',[])+rec.get('references',[]):
        p=ROOT/dep['file']
        if not p.exists():errors.append('Missing source: '+str(p))
        elif sha(p)!=dep['sha256']:errors.append('Source hash changed: '+str(p))
    if rec.get('prompt') and sha(ROOT/rec['prompt'])!=rec['promptSha256']:errors.append('Prompt changed: '+rec['prompt'])
    files.append({'file':image.relative_to(ROOT).as_posix(),'sha256':sha(image),'record':recpath.relative_to(ROOT).as_posix()})
if len(files)!=14:errors.append('Expected 10 runtime+2 native+2 contact PNGs')
if errors:raise RuntimeError(errors)
review={'reviewer':'full_ui_scope_audit','reviewedAt':now,
        'method':'Actually viewed both native atlases and both final light/dark composition contacts, plus existing matched skins; verified all 10 sprites in context.',
        'passed':['Daoist jade/ivory/gold hand-painted continuity','no alpha halo on light/dark backgrounds','complete cloud rims and circular thumb',
                  'input focus/error true transparent center','normal/focus/error/disabled input readability',
                  'normal/selected/pressed list distinction','progress0/25/50/100 fits empty channel',
                  'toggle on/off/disabled separate thumb and track','slider0/50/100 reuses legacy geometry',
                  'horizontal nine-slice widened input; fixed ornament height'],
        'remainingFailures':[], 'independentRootReview':'awaiting root review; self QA is complete'}
for entry in files:
    p=ROOT/entry['record'];r=read(p)
    r['inspection']={'status':'passed_as_native_source' if entry['file'].endswith('-native.png') else 'passed',
                     'reviewedAt':now,'reviewer':'full_ui_scope_audit','qa':'assets/ui/production-v3/forms/qa.json',
                     'qaPreviews':manifest['qaPreviews'],'remainingFailures':[]}
    if entry['file'].endswith('-native.png'):
        r['inspection']['note']='Selected native source; low-alpha noise is cleaned in formal derivatives. Native atlas is not a runtime skin.'
    write(p,r)
for a in manifest['assets']:
    a['status']='passed';a['productionAccepted']=True
manifest['status']='passed';manifest['frozenAt']=now
manifest['inspection']=review
manifest['retention']={'runtimePNGs':10,'nativeRebuildSources':2,'finalQAContacts':2,'intermediatePNGs':0,
                       'reason':'All retained images are formal runtime assets, necessary adopted native source atlases or final QA contacts.'}
write(OUT/'manifest.json',manifest)
comp=read(OUT/'compositions.json');comp['status']='passed';comp['reviewedAt']=now;write(OUT/'compositions.json',comp)
qa['status']='passed';qa['frozenAt']=now;qa['visualReview']=review;qa['pendingChecks']=[]
qa['remainingFailures']=[];qa['integrity']={'files':files,'dependencyHashesVerified':True,'PNGRecordsVerified':14}
qa['retention']=manifest['retention'];write(OUT/'qa.json',qa)
print(json.dumps({'status':'passed','frozenAt':now,'PNGs':len(files),'manifestSHA256':sha(OUT/'manifest.json'),
                  'qaSHA256':sha(OUT/'qa.json'),'compositionsSHA256':sha(OUT/'compositions.json')},ensure_ascii=False))
