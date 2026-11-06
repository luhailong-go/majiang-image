"""Read-only asset verification; writes only the independent QA report in work/full_ui."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageChops

ROOT = Path(r'D:\work\majiang-image')
OUT = ROOT / 'work/full_ui/component-independent-qa.json'
BASELINE = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else None

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def info(path):
    with Image.open(ROOT / path) as im:
        im.load()
        result = {'width': im.width, 'height': im.height, 'mode': im.mode, 'format': im.format}
        if 'A' in im.getbands():
            a = im.getchannel('A'); h = a.histogram(); bbox = a.getbbox()
            result['alpha'] = {'range': list(a.getextrema()), 'fullyTransparent': h[0], 'semiTransparent': sum(h[1:255]), 'opaque': h[255], 'bbox': list(bbox) if bbox else None, 'corners': [a.getpixel(xy) for xy in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]]}
            result['transparentPixelHiddenRGBCount'] = sum(1 for p in im.getdata() if p[3] == 0 and any(p[:3]))
            if bbox:
                result['nonzeroAlphaMargins'] = [bbox[0], bbox[1], im.width-bbox[2], im.height-bbox[3]]
        return result

def validate_file(entry, manifest_name):
    file = entry['file']; recpath = entry.get('record', file + '.generation.json'); rec = read(recpath)
    observed = info(file); sha = digest(file); errors = []
    def check(condition, message):
        if not condition: errors.append(message)
    check(rec.get('sha256') == sha, 'sidecar hash mismatch')
    if entry.get('sha256'): check(entry['sha256'] == sha, 'manifest hash mismatch')
    for k in ['width','height','mode']:
        if k in entry: check(entry[k] == observed[k], 'manifest '+k+' mismatch')
        if k in rec: check(rec[k] == observed[k], 'sidecar '+k+' mismatch')
    check(rec.get('actualModel') is None and rec.get('actualQuality') is None, 'actual model/quality incorrectly asserted')
    for owner in [entry,rec]:
        if owner.get('alpha') and 'fullyTransparent' in owner['alpha']:
            check(owner['alpha'] == observed.get('alpha'), 'alpha metadata mismatch')
    ns = entry.get('nineSlice')
    if ns is not None:
        check(len(ns)==4 and all(isinstance(n,(int,float)) and n>=0 for n in ns), 'invalid nineSlice shape')
        if len(ns)==4: check(ns[0]+ns[2]<observed['width'] and ns[1]+ns[3]<observed['height'], 'nineSlice leaves no center area')
    if 'nineSlice' in entry and 'nineSlice' in rec: check(ns == rec['nineSlice'], 'manifest/sidecar nineSlice mismatch')
    if 'resizePolicy' in entry: check(entry['resizePolicy']==rec.get('resizePolicy'),'manifest/sidecar resizePolicy mismatch')
    anchor = entry.get('anchor', rec.get('anchor'))
    if anchor: check(all(isinstance(anchor.get(k),(int,float)) and 0<=anchor[k]<=1 for k in ['x','y']), 'invalid normalized anchor')
    sources = rec.get('derivedFrom') or []
    if isinstance(sources,dict): sources=[sources]
    source_checks=[]
    for s in sources:
        sp = s.get('file')
        if not sp: continue
        exists=(ROOT/sp).is_file(); check(exists,'missing source '+sp)
        if exists:
            source_sha=digest(sp); check(not s.get('sha256') or s['sha256']==source_sha,'source hash mismatch '+sp)
            source_checks.append({'file':sp,'sha256':source_sha,'declaredHashMatches':not s.get('sha256') or s['sha256']==source_sha})
        sr=s.get('record') or s.get('generationRecord')
        if sr: check((ROOT/sr).is_file(),'missing source record '+sr)
    crop = rec.get('crop')
    if isinstance(crop,list) and sources:
        with Image.open(ROOT/sources[0]['file']) as src:
            l,t,r,b=crop; check(0<=l<r<=src.width and 0<=t<b<=src.height,'crop outside native source')
            pad=rec.get('transparentPadding',0)
            check((r-l+pad*2,b-t+pad*2)==(observed['width'],observed['height']),'crop/padding/export dimensions inconsistent')
    if rec.get('stateTransform') and sources:
        with Image.open(ROOT/file) as dst, Image.open(ROOT/sources[0]['file']) as src:
            check(dst.size==src.size and ImageChops.difference(dst.getchannel('A'),src.getchannel('A')).getbbox() is None,'button state changed geometry/alpha')
    if manifest_name.startswith('assets/ui'):
        if entry['id']=='table-background': check(observed['mode']=='RGB','background must be RGB')
        elif entry['id']=='modal-shade': check(observed['alpha']['range']==[144,144],'overlay alpha is not 144')
        else:
            check(observed['mode']=='RGBA','cutout has no real alpha')
            check(observed.get('alpha',{}).get('range')==[0,255],'cutout alpha range is unexpected')
            check(min(observed.get('nonzeroAlphaMargins',[0]))>0,'nonzero alpha touches export boundary')
            check(observed.get('transparentPixelHiddenRGBCount',-1)==0,'hidden RGB left under fully transparent pixels')
    return {'id':entry.get('id',Path(file).stem),'file':file,'record':recpath,'sha256':sha,'recordSha256':digest(recpath),'observed':observed,'nineSlice':ns,'resizePolicy':entry.get('resizePolicy',rec.get('resizePolicy')),'sources':source_checks,'status':'passed' if not errors else 'failed','issues':errors}

ui_path='assets/ui/manifest.json'; ui=read(ui_path); assets=ui['assets']
results=[validate_file(a,ui_path) for a in assets]
structural=[]
def record_check(name,passed,detail=None):
    structural.append({'check':name,'status':'passed' if passed else 'failed','detail':detail})
record_check('58 unique component IDs',len(assets)==58 and len({a['id'] for a in assets})==58)
by_id={a['id']:a for a in assets}
for group,count in [('common',45),('gameplay',13)]:
    child=read(f'assets/ui/{group}/manifest.json')['assets']
    record_check(group+' manifest matches total manifest',len(child)==count and all(a==by_id.get(a['id']) for a in child),{'count':len(child)})

comp_path=ui['compositionFile']; comp=read(comp_path); refs=[]; unresolved=[]
asset_keys={'frame','fill','title','closeIcon','normal','pressed','selected','disabled','off','on','track','thumb','fillSkin','skin','keySkin','shade','spinner','avatarFrame','currentPlayerOverlay','candidatePanelSkin','candidateSelectedSkin','modalShade','asset'}
def walk_refs(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            loc=path+'.'+k
            if isinstance(v,str):
                if v.startswith('assets/'):
                    refs.append({'location':loc,'target':v,'exists':(ROOT/v).is_file()})
                    if not (ROOT/v).is_file(): unresolved.append(loc+': '+v)
                elif v in by_id: refs.append({'location':loc,'target':v,'file':by_id[v]['file'],'exists':(ROOT/by_id[v]['file']).is_file()})
                elif k in asset_keys: unresolved.append(loc+': '+v)
            else: walk_refs(v,loc)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            if isinstance(v,str) and v.startswith('assets/'):
                refs.append({'location':path+f'[{i}]','target':v,'exists':(ROOT/v).is_file()})
                if not (ROOT/v).is_file(): unresolved.append(path+f'[{i}]: '+v)
            else: walk_refs(v,path+f'[{i}]')
walk_refs(comp)
record_check('all composition raster/file references resolve',not unresolved,unresolved)
record_check('three button families expose four actual raster states',all(all(comp['buttonFamilies'][f].get(s) in by_id for s in ['normal','pressed','selected','disabled']) for f in ['primary','secondary','action']))
record_check('window frame has conservative 200px margins',by_id['window-frame']['nineSlice']==[200,200,200,200] and comp['compositions']['window']['frameNineSliceMargins']==[200,200,200,200])
settlement=by_id['settlement-card']; settlement_comp=comp['compositions']['settlement']
record_check('settlement card preserves aspect without nine-slicing',settlement['nineSlice'] is None and settlement['resizePolicy']['mode']=='uniform_scale_only' and settlement_comp.get('nineSlice') is None and settlement_comp.get('preserveAspect') is True and settlement_comp.get('resizePolicy')=='uniform_scale_only')
button_policies=[]
for f in ['primary','secondary','action']:
    family=comp['buttonFamilies'][f]
    button_policies.append(family['resizePolicy'])
    for state in ['normal','pressed','selected','disabled']:
        button_policies.append(by_id[family[state]]['resizePolicy'])
record_check('12 button states and 3 families allow only horizontal stretch with locked height',all(p.get('mode')=='horizontal_nine_slice_only' and p.get('stretchAxes')==['x'] and p.get('lockHeightAfterUniformScale') is True for p in button_policies))
if BASELINE:
    baseline_hashes={a['id']:a['sha256'] for a in BASELINE.get('assets',[])}
    record_check('all 58 PNG hashes unchanged from independent visual review',len(baseline_hashes)==58 and all(a['sha256']==baseline_hashes.get(a['id']) for a in results))
background_record=read(by_id['table-background']['record'])
record_check('background operation accurately describes PNG re-encode',background_record['operation']=='pixel-identical native RGB PNG re-encode; metadata stripped; no resampling')
with Image.open(ROOT/by_id['table-background']['file']) as exported, Image.open(ROOT/background_record['derivedFrom']['file']) as original:
    record_check('table background is pixel-identical to native source',exported.mode==original.mode and exported.size==original.size and ImageChops.difference(exported,original).getbbox() is None,{'operation':background_record['operation'],'sourceSha256':digest(background_record['derivedFrom']['file']),'exportSha256':digest(by_id['table-background']['file'])})

support=[]
chars=read('assets/characters/manifest.json')
support.append({'manifest':'assets/characters/manifest.json','manifestSha256':digest('assets/characters/manifest.json'),'assets':[validate_file(a,'assets/characters/manifest.json') for a in chars['assets']]})
tiles=read('assets/tiles/manifest.json')
tile_entries=tiles['tiles']+[dict(v,id='tile-'+k) for k,v in tiles['base'].items()]+[{'id':'tile-highlight','file':'assets/tiles/states/tile-highlight.png'}]
support.append({'manifest':'assets/tiles/manifest.json','manifestSha256':digest('assets/tiles/manifest.json'),'assets':[validate_file(a,'assets/tiles/manifest.json') for a in tile_entries]})

preview_paths=['work/components/qa/common-light.png','work/components/qa/common-dark.png','work/components/qa/gameplay-light.png','work/components/qa/gameplay-dark.png']
previews=[{'file':p,'sha256':digest(p),'dimensions':{k:info(p)[k] for k in ['width','height']},'actualViewed':True} for p in preview_paths]
support_preview_paths=['work/characters/welcome-daotong-light-qa.png','work/characters/welcome-daotong-dark-qa.png','assets/tiles/previews/tile-states-alpha.png','assets/tiles/previews/tiles-contact-sheet.png']
support_previews=[{'file':p,'sha256':digest(p),'actualViewed':True,'status':'passed'} for p in support_preview_paths]
errors=[{'file':a['file'],'issues':a['issues']} for a in results if a['issues']]
for s in support:
    errors.extend({'file':a['file'],'issues':a['issues']} for a in s['assets'] if a['issues'])
errors.extend(s for s in structural if s['status']=='failed')
report={'schemaVersion':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'independent rooms_finish_qa agent','scope':'Read-only component validation plus character/tile hash recheck; no asset file mutation','status':'passed' if not errors else 'failed','actualModel':None,'actualQuality':None,'manifests':[{'file':p,'sha256':digest(p)} for p in ['assets/ui/manifest.json','assets/ui/common/manifest.json','assets/ui/gameplay/manifest.json',comp_path]],'counts':{'ui':len(results),'common':sum(a.get('group')=='common' for a in assets),'gameplay':sum(a.get('group')=='gameplay' for a in assets),'characters':5,'tileRasters':len(tile_entries),'compositionGroups':len(comp['compositions']),'resolvedCompositionReferences':len(refs)},'structuralChecks':structural,'assets':results,'compositionReferences':refs,'supportingAssetRecheck':support,'visualReview':{'status':'passed','method':'Actually opened and inspected all four supplied light/dark contact sheets using view_image. Reused parent independent full 58 PNG visual acceptance for unchanged hashes; checked contact sheet silhouettes, interior transparency and absence of adjacent atlas fragments. Modal shade is an intentional constant-alpha runtime primitive. Table background is an opaque full frame. No new generation was requested.','previews':previews,'observations':['45 common skins/icons maintain complete silhouettes on light and dark backgrounds; transparent interior in window-frame and hole-bearing icons is correct.','12 cutout gameplay elements have intact silhouettes; avatar-frame and current-player-ring retain transparent centers.','Pressed, selected and disabled button rasters preserve geometry and are visually distinguishable.','Loading-ring/current-player-ring glow is intentional semi-transparent light, not an opaque matte.']},'limitations':['No engine/client integration claimed. Nine-slice stretch behavior is validated by metadata and source appearance, not executed in a client.','No browser execution: prior file:// request was rejected by browser policy; no alternative browser or server attempted.'],'issues':errors}
report['supportingVisualReview']={'previews':support_previews,'observations':['Final padded welcome-daotong export, not raw generation, retains complete hair, ribbons, hands, feet and costume on light and dark backgrounds.','Tile contact sheet has 34 distinct identities and clean blank/back; state sheet preserves same identity in highlight, disabled, and 90/180/270 degree rotations.']}
report['validationScript']='work/full_ui/component_independent_qa.py'
report['producerFinalQA']={'file':'assets/ui/qa.json','sha256':digest('assets/ui/qa.json'),'status':read('assets/ui/qa.json').get('status')}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'counts':report['counts'],'issues':errors,'output':str(OUT)},ensure_ascii=False))
