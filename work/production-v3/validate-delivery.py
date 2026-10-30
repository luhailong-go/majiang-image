from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,re,argparse
R=Path(__file__).resolve().parents[2]
hold=R/'.work/production-v3/resource-hold.json'
if hold.is_file() and json.loads(hold.read_text(encoding='utf-8-sig')).get('status')=='holding_local_heavy_work':raise SystemExit('Deferred: shared-machine heavy-work slot has not been returned.')
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--manifest',default='exports/production-art-v3-manifest.json');parser.add_argument('--report',default='exports/production-v3-validation.json');parser.add_argument('--expected-assets',type=int,default=292);args=parser.parse_args()
errors=[];records={};assets=[];fileHashes={};old=read('exports/full-game-art-manifest.json');data=read(args.manifest)
def issue(value):errors.append(str(value))
def dep(file,expected=None):
    p=Path(file)
    if p.is_absolute():
        try:p=p.relative_to(R)
        except ValueError:issue('Nonportable dependency '+str(file));return
    file=p.as_posix();p=R/p
    if not p.is_file():
        rp=Path(str(p)+'.generation.json')
        if rp.is_file():
            d=json.loads(rp.read_text(encoding='utf-8-sig'));c=d.get('cleanup',{});replacement=c.get('replacement') or c.get('replacedBy')
            if expected and d.get('pixelsRetainedInProject') is False and d.get('sha256')==expected and c.get('sha256BeforeRemoval')==expected and replacement and (R/replacement).is_file():return
            # Exact historical v1 tile input was independently accepted and deleted before v2 delivery.
            # Its original record predates the later explicit cleanup-link schema; never recover its pixels.
            if file=='assets/tiles/source/tile-blank-v1.png' and expected=='20ab59cf3793717c77b54fbc227c661cba9e799a2b722c759f6f783b7a291e75':
                prior=read('exports/package-independent-qa.json')
                proof=next((x for x in prior.get('historicalDeletedSourcesWithEvidence',[]) if x.get('file')==file and x.get('sha256')==expected),None)
                if proof and prior.get('status')=='passed' and d.get('pixelsRetainedInProject') is False and d.get('sha256')==expected and c.get('reason') and c.get('removedAt') and (R/'assets/tiles/source/tile-blank-v2.png').is_file():return
        issue('Missing dependency '+file);return
    h=sha(file);fileHashes[file]=h
    if expected and h!=expected:issue('Dependency hash mismatch '+file)
def record(file):
    if file in records:return
    p=R/file
    if not p.is_file():issue('Missing record '+file);return
    d=read(file);records[file]=sha(file)
    if isinstance(d.get('file'),str):dep(d['file'],d.get('sha256'))
    for key in ['references','derivedFrom']:
        values=d.get(key) or []
        if isinstance(values,(dict,str)):values=[values]
        for entry in values:
            if isinstance(entry,str):entry={'file':entry}
            if not isinstance(entry,dict):continue
            target=entry.get('file') or entry.get('path')
            if target:dep(target,entry.get('sha256'))
            rp=entry.get('generationRecord') or entry.get('record')
            if rp and isinstance(rp,str) and (R/rp).is_file():record(rp)
    prompt=d.get('prompt');expected=d.get('promptSha256')
    if isinstance(prompt,dict):expected=prompt.get('sha256',expected);prompt=prompt.get('file') or prompt.get('path')
    if prompt:dep(prompt,expected)
    if d.get('actualModel') not in [None,'unconfirmed','未确认']:issue('Unproven model '+file)
    if d.get('actualQuality') not in [None,'unconfirmed','未确认']:issue('Unproven quality '+file)
for a in data['assets']:
    file=a['file'];dep(file,a['sha256']);record(a.get('record',file+'.generation.json'))
    with Image.open(R/file) as im:
        im.load()
        if list(im.size)!=[a['width'],a['height']] or im.mode!=a['mode']:issue('Primary dimensions or mode '+file)
        if '/production-v3/' in file:
            if im.mode!='RGBA':issue('New runtime not RGBA '+file)
            else:
                al=im.getchannel('A');w,h=im.size
                edge=max(al.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
                if al.getextrema()[0]!=0 or edge:issue('New runtime alpha edge '+file)
    assets.append({'file':file,'sha256':a['sha256'],'width':a['width'],'height':a['height'],'mode':a['mode']})
for a in old['assets']:
    if sha(a['file'])!=a['sha256']:issue('Previous accepted270 pixels changed '+a['file'])
for folder in ['assets/ui/production-v3','designs/ui/production-v3','production/previews']+(['assets/branding/yunjian-queshe'] if args.expected_assets==293 else []):
    for p in (R/folder).rglob('*.generation.json'):record(p.relative_to(R).as_posix())
    for p in (R/folder).rglob('*.png'):
        if not Path(str(p)+'.generation.json').is_file():issue('Unrecorded new PNG '+p.relative_to(R).as_posix())
pages=read('production/layouts.json')['pages'];states=read('production/states.json')['states'];previews=read('production/composition-previews.json')
if len(pages)!=32 or len(states)<86:issue('Production page/state scope')
oldStates={s['state'] for s in old['states']}
if not oldStates.issubset({s['state'] for s in states}):issue('Missing existing state')
if previews.get('pageCount')!=len(pages) or previews.get('stateCount')!=len(states) or previews.get('previewCount')!=len(pages)+len(states):issue('Stale/missing composition previews')
for group,nodes in [('pages',pages),('states',states)]:
    expected=hashlib.sha256(json.dumps(nodes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if previews.get('layoutContentHashes',{}).get(group)!=expected:issue('Stale '+group+' preview source hash')
if previews.get('rendererSha256')!=sha('work/production-v3/render-compositions.py'):issue('Preview renderer changed after images')
if previews.get('textFitIssues'):issue('Unresolved text fit issue')
visualPath='production/final-visual-qa.json'
if (R/visualPath).is_file():
    visual=read(visualPath)
    if visual.get('layoutContentHashes')!=previews.get('layoutContentHashes'):issue('Final visual receipt source snapshot stale')
    for file,digest in visual.get('all118ProofHashes',{}).items():dep(file,digest)
    for entry in visual.get('actualViewed',[]):dep(entry['file'],entry['sha256'])
for p in pages+states:
    for n in p['layers']:
        x,y,w,h=n['rect']
        if min(x,y)<0 or min(w,h)<=0 or x+w>1600.1 or y+h>900.1:issue('Out-of-canvas '+str(p.get('id',p.get('state')))+' '+n['id'])
        if n.get('file'):
            dep(n['file'])
            if n['file'].startswith('designs/'):issue('Baked concept used as runtime '+n['file'])
        for f in n.get('stateAssets',{}).values():dep(f)
        if n.get('sourceRect') and n.get('file'):
            with Image.open(R/n['file']) as im:
                x0,y0,x1,y1=n['sourceRect']
                if x0<0 or y0<0 or x1>im.width or y1>im.height or x1<=x0 or y1<=y0:issue('Source crop bounds '+n['id'])
for p in ['assets/ui/production-v3/empty/qa.json','assets/ui/production-v3/forms/qa.json','assets/ui/production-v3/gameplay/qa.json','assets/presentation/production-v3/qa.json','production/final-visual-qa.json','production/gallery-validation.json']:
    if not (R/p).is_file():issue('Missing final domain QA '+p)
    else:
        q=read(p)
        if q.get('status') not in ['passed','complete_qa_passed']:issue('Domain not final '+p+': '+str(q.get('status')))
        fileHashes[p]=sha(p)
for f in data.get('productionBindingFiles',[]):
    dep(f)
    if not (R/f).is_file():continue
    if data.get('productionBindingHashes',{}).get(f)!=sha(f):issue('Binding snapshot changed '+f)
for f,h in data.get('sourceManifestHashes',{}).items():dep(f,h)
if len({a['file'] for a in assets})!=len(assets):issue('Duplicate primary files')
if len(assets)!=args.expected_assets or data.get('newProductionAssetCount')!=22:issue('Unexpected primary/new asset count')
if args.expected_assets==293:
    brand=read('config/brand.json');logo=brand['primaryLogo']
    if brand['gameName']!='云间雀社':issue('Game brand mismatch')
    for ui in ['UI01','UI02']:
        page=next(x for x in pages if x['id']==ui)
        if not any(n.get('file')==logo for n in page['layers']):issue('Missing logo in '+ui)
    loading=next(x for x in states if x['state']=='system.loading')
    if not any(n.get('file')==logo for n in loading['layers']):issue('Missing loading logo')
    if any(n['type']=='button' and n.get('enabled',True) for n in loading['layers']):issue('Loading entry must remain disabled')
    for a in read('exports/production-art-v3-manifest.json')['assets']:
        if sha(a['file'])!=a['sha256']:issue('Accepted292 native pixel changed '+a['file'])
    if read('assets/branding/yunjian-queshe/qa.json').get('status')!='passed':issue('Logo art not accepted')
if read('production/gallery-validation.json').get('checkCount',0)<127:issue('Final gallery check scope')
errors=list(dict.fromkeys(errors))
report={'schemaVersion':3,'status':'passed' if not errors else 'failed','verifiedAt':datetime.now(timezone.utc).isoformat(),'primaryAssetsChecked':len(assets),'newRuntimeAssets':22,'previousAccepted270Unchanged':True,'recordsChecked':len(records),'pageLayouts':len(pages),'stateCompositions':len(states),'proofImages':previews.get('previewCount'),'sourceHashCount':len(fileHashes),'errors':errors,'browserInteraction':'not_run_policy_blocked','clientIntegrated':False,'assets':assets,'recordHashes':records,'dependencyHashes':fileHashes,'sourceManifestHashes':data.get('sourceManifestHashes',{}),'productionBindingHashes':data.get('productionBindingHashes',{})}
report['primaryAssetSnapshotSha256']=hashlib.sha256(json.dumps(assets,sort_keys=True,separators=(',',':')).encode()).hexdigest()
write=lambda f,d:(R/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(args.report,report)
print(json.dumps({k:v for k,v in report.items() if k not in ['assets','recordHashes','dependencyHashes','sourceManifestHashes','productionBindingHashes']},ensure_ascii=False))
sys.exit(1 if errors else 0)
