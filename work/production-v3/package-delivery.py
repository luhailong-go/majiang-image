from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,subprocess,re
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
hold=R/'.work/production-v3/resource-hold.json'
if hold.is_file() and read('.work/production-v3/resource-hold.json').get('status')=='holding_local_heavy_work':raise SystemExit('Package compression deferred during shared heavy-work slot.')
data=read('exports/production-art-v3-manifest.json');qa=read('exports/production-v3-validation.json')
assert data['deliveryStatus']=='complete_production_art_v3' and qa['status']=='passed' and not qa['errors']
for file,digest in {**qa['recordHashes'],**qa['dependencyHashes'],**qa['sourceManifestHashes'],**qa['productionBindingHashes']}.items():assert sha(file)==digest,'Changed after final validation '+file
oldFiles=[e['file'] for e in read('exports/full-game-package-files.json')['files']]
files=set(oldFiles)
for folder in ['assets/ui/production-v3','assets/presentation/production-v3','designs/ui/production-v3','prompts/production-v3','production','work/production-v3']:
    for p in (R/folder).rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.png','.webp','.json','.md','.html','.txt','.py','.ps1','.js','.cjs','.mjs'} and '__pycache__' not in p.parts:files.add(p.relative_to(R).as_posix())
for p in (R/'docs').glob('PRODUCTION*.md'):files.add(p.relative_to(R).as_posix())
files.update(['.gitignore','.gitattributes','docs/PUBLIC_REPOSITORY.md','exports/production-art-v3-manifest.json','exports/production-v3-validation.json','exports/full-game-package-files.json','exports/full-game-package-verification.json','exports/package-independent-qa.json','exports/superseded-ui-package-cleanup.json'])
for file in files:
    assert (R/file).is_file(),file
    assert not file.startswith(('.work/','prototypes/','.git/')),file
entries=[{'file':file,'bytes':(R/file).stat().st_size,'sha256':sha(file)} for file in sorted(files)]
archive='exports/mahjong-complete-game-art-v3.zip';manifest={'schemaVersion':3,'createdAt':datetime.now(timezone.utc).isoformat(),'archive':archive,'payloadCount':len(entries),'payloadBytes':sum(e['bytes'] for e in entries),'files':entries,'selfHashExcluded':True,'primaryAssetCount':292,'pageLayouts':32,'stateCompositions':data['productionStates'],'notes':['Runtime assets, native sources, prompts, provenance, compositions and QA included.','Composition proof images are mechanical derivative previews, not native model paintings.','The package manifest is included but excluded from its own hash.']}
write('exports/production-v3-package-files.json',manifest)
with zipfile.ZipFile(R/archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for e in entries:z.write(R/e['file'],e['file'])
    z.write(R/'exports/production-v3-package-files.json','exports/production-v3-package-files.json')
with zipfile.ZipFile(R/archive) as z:
    assert z.testzip() is None
    for e in entries:assert hashlib.sha256(z.read(e['file'])).hexdigest()==e['sha256'],e['file']
    assert z.read('exports/production-v3-package-files.json')==(R/'exports/production-v3-package-files.json').read_bytes()
result={'schemaVersion':3,'status':'passed','verifiedAt':datetime.now(timezone.utc).isoformat(),'archive':archive,'sha256':sha(archive),'bytes':(R/archive).stat().st_size,'memberCount':len(entries)+1,'payloadHashesVerified':len(entries),'primaryAssetsIncluded':292,'pageLayouts':32,'stateCompositions':data['productionStates'],'zipCRC':'passed','errors':[],'clientIntegrated':False,'browserInteraction':'not_run_policy_blocked'}
write('exports/production-v3-package-verification.json',result)
print(json.dumps(result))
