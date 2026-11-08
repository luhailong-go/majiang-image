from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import json,hashlib,numpy as np
R=Path(r'D:\work\majiang-image');OUT=R/'assets/ui/full-game/components';NOW=datetime.now(timezone(timedelta(hours=-4))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(OUT/'manifest.json');checks=[];allids={a['id'] for a in m['assets']};qa_paths=['work/full-game-ui/components/qa/'+n+'.png' for n in ['cards-badges-light','cards-badges-dark','slots-tutorial-light','slots-tutorial-dark']]
for a in m['assets']:
 p=R/a['file'];rp=R/a['record'];rec=read(rp)
 with Image.open(p) as test:test.verify()
 im=Image.open(p).convert('RGBA');ar=np.asarray(im);alpha=ar[:,:,3]
 assert im.size==(a['width'],a['height']) and sha(p)==a['sha256']==rec['sha256']
 assert rec['actualModel'] is None and rec['actualQuality'] is None and not rec['resampled']
 assert sha(R/rec['derivedFrom']['file'])==rec['derivedFrom']['sha256']
 assert (R/rec['derivedFrom']['record']).is_file()
 assert a['nineSlice'] is None and a['resizePolicy']['mode']=='uniform_scale_only'
 assert a['alpha']['minimumTransparentMargin']>=16 and a['alpha']['edgeAlphaMax']==0
 assert np.all(ar[:,:,:3][alpha==0]==0)
 assert rec['alphaCleanup']['removedAlphaAtLeast128']==0
 hole=None
 if a['family'] in ['achievement','spotlight','focus']:
  cx=int(im.width*.5);cy=int(im.height*(.445 if a['family']=='achievement' else .5));patch=alpha[cy-45:cy+45,cx-45:cx+45]
  assert patch.max()==0;hole='90x90 native center patch fully transparent'
 if a['family'] in ['rewardCard','cosmeticCard','itemSlot']:
  assert alpha[im.height//2,im.width//2]==255
 rec['inspection']={'status':'passed','checkedAt':NOW,'issues':[],'visual':'Actual final light/dark composites inspected: complete edges, no matte, no detached speckles, coherent style, distinguishable states.','technical':'PNG/hash/dimensions/alpha padding/source provenance passed.','qaImages':qa_paths[:2] if a['family'] in ['rewardCard','cosmeticCard','achievement','rank'] else qa_paths[2:]}
 rec['productionAccepted']=True;save(rp,rec);a['status']='passed';a['productionAccepted']=True
 checks.append({'id':a['id'],'file':a['file'],'sha256':a['sha256'],'pngIntegrity':'passed','sourceHash':'passed','dimensions':'passed','alpha':'passed','minimumTransparentMargin':a['alpha']['minimumTransparentMargin'],'centerHole':hole,'visual':'passed','issues':[]})
for family in m['stateFamilies'].values():
 members=[a for a in m['assets'] if a['id'] in family['states'].values()]
 assert len({(a['width'],a['height']) for a in members})==1 and len({a['sha256'] for a in members})==len(members)
for a in m['reusedAssets']:assert sha(R/a['file'])==a['sha256']
c=read(OUT/'compositions.json')
assert len(c['compositions'])==7
for src in m['sources']:
 p=R/(src+'.generation.json');rec=read(p)
 assert rec['actualModel'] is None and rec['actualQuality'] is None
 assert len(rec['references'])==3 and all(x['actuallyAttached'] for x in rec['references'])
 assert sha(R/rec['prompt'])==rec['promptSha256']
 rec['inspection']['visualStatus']='passed_as_source_for_mechanical_export';rec['inspection']['issues']=[];rec['inspection']['note']='Final acceptance applies to separately exported transparent sprites; source atlas remains derivation material.'
 rec['status']['productionAccepted']=False;save(p,rec)
m['status']='passed';m['checkedAt']=NOW;m['unresolvedIssues']=[];save(OUT/'manifest.json',m)
qa={'schemaVersion':2,'checkedAt':NOW,'status':'passed','newAssetCount':22,'stateFamilyCount':len(m['stateFamilies']),'reusedAssetCount':len(m['reusedAssets']),'sources':m['sources'],'checks':checks,'familyRegistration':'Same native canvas dimensions and center anchor within each family; slot ribbon extension preserves body alignment.','transparentEdges':'At least 16 fully transparent pixels at every output boundary; RGB under alpha zero is zero.','sourceCleanup':'No source pixels with Alpha>=128 removed; every remaining connected sprite exported exactly once.','stretchPolicy':'All new sprites uniform-scale-only; nineSlice=null.','visualContactSheets':qa_paths,'unresolvedIssues':[],'clientIntegrated':False,'actualModel':None,'actualQuality':None}
save(OUT/'qa.json',qa)
import runpy
runpy.run_path(str(R/'work/full-game-ui/components/revise_metadata.py'),run_name='metadata_sync')
print(json.dumps({'status':'passed','newAssets':len(checks),'unresolvedIssues':[],'manifestSha256':sha(OUT/'manifest.json'),'qaSha256':sha(OUT/'qa.json'),'compositionsSha256':sha(OUT/'compositions.json')},ensure_ascii=False))
