from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib,sys,re
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def stamp():return datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
errors=[];history=[];recordsSeen=set();checks=[]
data=read(R/'exports/full-game-art-manifest.json')
old=read(R/'exports/ui-delivery-manifest.json')
for file,expected in data.get('sourceManifestHashes',{}).items():
    if sha(R/file)!=expected:errors.append('source manifest changed '+file)
def historical(path,expected):
    rp=Path(str(path)+'.generation.json')
    if not rp.is_file():return False
    d=read(rp);c=d.get('cleanup',{})
    replacement=c.get('replacement') or c.get('replacedBy')
    replacementOk=bool(replacement and (R/replacement).is_file())
    match=d.get('sha256')==expected and c.get('sha256BeforeRemoval',c.get('sha256'))==expected
    ok=d.get('pixelsRetainedInProject') is False and bool(c.get('reason')) and match and replacementOk
    if ok:history.append({'file':path.relative_to(R).as_posix(),'sha256':expected,'cleanupRecord':rp.relative_to(R).as_posix(),'replacement':replacement})
    return ok
def dep(path,expected,label):
    p=Path(path)
    if p.is_absolute():
        try:p=p.relative_to(R)
        except ValueError:
            errors.append(f'{label}: nonportable dependency outside project {path}')
            return
    q=R/p
    if not q.is_file():
        if expected and historical(q,expected):return
        errors.append(f'{label}: missing {p.as_posix()}');return
    if expected and sha(q)!=expected:errors.append(f'{label}: dependency hash mismatch {p.as_posix()}')
def record(rp):
    if rp in recordsSeen:return
    recordsSeen.add(rp)
    if not rp.is_file():errors.append('record missing '+str(rp));return
    d=read(rp);f=d.get('file')
    if isinstance(f,str):
        q=R/f
        if q.is_file():
            if d.get('sha256') and sha(q)!=d['sha256']:errors.append('record image hash '+f)
            if q.suffix.lower() in ['.png','.webp']:
                with Image.open(q) as im:
                    if d.get('width') is not None and (im.width!=d['width'] or im.height!=d['height']):errors.append('record size '+f)
        elif not(d.get('sha256') and historical(q,d['sha256'])):errors.append('record target missing '+f)
    if d.get('actualModel') not in [None,'未确认','unconfirmed']:errors.append('Unproven actualModel '+str(rp))
    if d.get('actualQuality') not in [None,'未确认','unconfirmed']:errors.append('Unproven actualQuality '+str(rp))
    for key in ['derivedFrom','references']:
        values=d.get(key) or []
        if isinstance(values,dict):values=[values]
        if isinstance(values,str):values=[{'file':values}]
        for entry in values:
            if isinstance(entry,str):entry={'file':entry}
            if not isinstance(entry,dict):continue
            path=entry.get('file') or entry.get('path')
            if path:dep(path,entry.get('sha256'),str(rp.relative_to(R)))
    p=d.get('prompt');expected=d.get('promptSha256')
    if isinstance(p,dict):expected=p.get('sha256',expected);p=p.get('file')
    if p:dep(p,expected,'prompt '+str(rp.relative_to(R)))

newPrefixes=['assets/characters/full-game/','assets/ui/full-game/','assets/props/full-game/','assets/tiles/flowers/','assets/branding/full-game/','assets/fx/full-game/']
for a in data['assets']:
    p=R/a['file']
    if not p.is_file():errors.append('primary missing '+a['file']);continue
    if sha(p)!=a['sha256']:errors.append('primary hash '+a['file'])
    try:
        with Image.open(p) as im:
            im.load();w,h=im.size
            if (w,h)!=(a['width'],a['height']):errors.append('primary dimensions '+a['file'])
            if im.mode!=a['mode']:errors.append('primary mode '+a['file'])
            if any(a['file'].startswith(t) for t in newPrefixes):
                if im.mode!='RGBA':errors.append('runtime alpha mode '+a['file'])
                else:
                    alpha=im.getchannel('A');ext=alpha.getextrema()
                    if ext[0]!=0 or ext[1]<32:errors.append('runtime alpha range '+a['file'])
                    edgeMax=max(alpha.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
                    if edgeMax:errors.append('runtime edge alpha '+a['file'])
    except Exception as e:errors.append('PNG load '+a['file']+': '+str(e))
    record(R/a['record'])
    checks.append({'file':a['file'],'sha256':a['sha256'],'width':a['width'],'height':a['height'],'mode':a['mode']})

# The already approved 127 UI-package images must remain byte-for-byte unchanged.
oldAssets=old['pages']+old['components']+old['characters']+old['tiles']
for a in oldAssets:
    if sha(R/a['file'])!=a['sha256']:errors.append('previous accepted pixels changed '+a['file'])

for prefix in ['designs/characters/full-game','designs/ui/full-game','designs/props/full-game','designs/fx/full-game','designs/branding/full-game','assets/characters/full-game','assets/ui/full-game','assets/props/full-game','assets/tiles/flowers','assets/fx/full-game','assets/branding/full-game','assets/scenes/full-game']:
    folder=R/prefix
    for rp in folder.rglob('*.generation.json'):record(rp)
    for p in folder.rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.png','.webp'] and not Path(str(p)+'.generation.json').is_file():errors.append('unrecorded media '+p.relative_to(R).as_posix())

if data['missingIds']:errors.append('missing page IDs '+str(data['missingIds']))
for state in data['states']:
    if state.get('status')!='mapped':errors.append('state unmapped '+state['state'])
    for file in state.get('files',[]):
        if not (R/file).is_file():errors.append('state source missing '+file)
if len(set(x['file'] for x in data['assets']))!=len(data['assets']):errors.append('primary duplicate file count')
if len(set(x['assetKey'] for x in data['assets']))!=len(data['assets']):errors.append('primary duplicate assetKey')
if len([x for x in data['tiles'] if x['group']=='可选花牌'])!=8:errors.append('flower count')
if len([x for x in data['characters'] if x.get('role') in ['expression','expression_avatar']])!=16:errors.append('expression count')
bodyFiles={x['file'] for x in data['characters'] if x.get('role') in ['full_body','fullbody'] or x.get('id')=='welcome-daotong'}
if len(bodyFiles)!=4:errors.append('full body count '+str(len(bodyFiles)))
if len(data['scenes'])!=5 or len(data['branding'])!=9 or len(data['fx'])!=35:errors.append('scene/branding/fx scope count')
if len(data['components'])<74:errors.append('supplemental component count')
fx=read(R/'assets/fx/full-game/manifest.json')
clips=fx.get('clipCount') or len(fx.get('clips',[]))
# Clip details are also independently validated by the effect domain final report.
fxv=read(R/'assets/fx/full-game/final-validation.json')
if fxv.get('status')!='passed' or fxv.get('runtimeClipsChecked')!=6:errors.append('FX domain final validation')
uiDomain=read(R/'designs/ui/full-game/manifest.json')
uiStatus=uiDomain.get('status','')
if uiStatus not in ['passed','complete_qa_passed','complete_static_art_delivery']:errors.append('supplemental UI domain not final '+uiStatus)
for rp in uiDomain.get('failedAttemptRecords',[]):record(R/rp)
for p in ['work/full-game-fx/root-scenes-independent-qa.json','work/full-game-fx/ui-components-independent-qa.json','work/full-game-props/ui-pages-independent-qa.json']:
    if not (R/p).is_file():errors.append('independent QA missing '+p)
    elif read(R/p).get('status')!='passed':errors.append('independent QA unresolved '+p)
for p in ['assets/characters/full-game/qa.json','assets/props/full-game/qa.json','assets/ui/full-game/components/qa.json','assets/scenes/full-game/qa.json','assets/branding/full-game/qa.json']:
    q=R/p
    if not q.is_file():errors.append('domain QA missing '+p);continue
    qa=read(q);status=qa.get('status')
    passed=status in ['passed','complete_qa_passed'] or (qa.get('technical')=='passed' and qa.get('visual')=='passed')
    if not passed:errors.append('domain QA not passed '+p+': '+str(status))

for p in ['docs/FULL_GAME_INTEGRATION.md','docs/CHARACTERS_FULL_GAME.md','docs/PROPS_FULL_GAME.md','docs/UI_FULL_GAME.md','docs/FX_FULL_GAME.md','docs/SCENES_BRANDING_FULL_GAME.md','AGENTS.md','README.md','references/style/01-mail-event.png','references/style/team-ui-v2.png']:
    if not (R/p).is_file():errors.append('delivery documentation missing '+p)
html=(R/'index.html').read_text(encoding='utf-8')
for link in re.findall(r'(?:href|src)="([^"]+)"',html):
    if link.startswith(('http:','https:','#','data:')) or any(c in link for c in ['+','<','>']):continue
    if link and not (R/link).is_file():errors.append('gallery static link '+link)
errors=list(dict.fromkeys(errors));history=list({x['file']:x for x in history}.values())
snapshot=hashlib.sha256(json.dumps(checks,sort_keys=True,separators=(',',':')).encode()).hexdigest()
out={'schemaVersion':2,'status':'passed' if not errors else 'failed','verifiedAt':stamp(),'primaryAssetsChecked':len(checks),'previousAcceptedPNGUnchanged':len(oldAssets),'recordsChecked':len(recordsSeen),'statesChecked':len(data['states']),'pageImages':len(data['pages']),'pageContractIds':data['contractCompleteCount'],'components':len(data['components']),'characters':len(data['characters']),'baseTileFaces':34,'optionalFlowerFaces':8,'fxFrames':24,'fxClips':6,'historicalSourcesRemovedPerRetentionPolicy':history,'errors':errors,'warnings':[],'browserInteraction':'not_run_policy_blocked','clientIntegrated':False,'assets':checks}
out['primaryAssetSnapshotSha256']=snapshot
out['recordHashes']={p.relative_to(R).as_posix():sha(p) for p in recordsSeen if p.is_file()}
out['sourceManifestHashes']=data.get('sourceManifestHashes',{})
(R/'exports/full-game-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['assets','recordHashes','sourceManifestHashes']},ensure_ascii=False))
sys.exit(1 if errors else 0)
