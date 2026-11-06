from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,zipfile
R=Path(__file__).resolve().parents[2]
def read(f):return json.loads((R/f).read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256((R/f).read_bytes()).hexdigest()
def write(f,d):(R/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qa=read('exports/release-v4-validation.json');assert qa['status']=='passed' and not qa['errors']
for file,digest in {**qa['recordHashes'],**qa['dependencyHashes'],**qa['sourceManifestHashes'],**qa['productionBindingHashes']}.items():assert sha(file)==digest,'Changed after validation '+file
data=read('exports/game-art-with-brand-manifest.json');assert len(data['assets'])==293
data.update(deliveryStatus='complete_game_art_release_v4',completedAt=datetime.now(timezone.utc).isoformat(),validationReport='exports/release-v4-validation.json',unresolvedArtItems=[])
write('exports/game-art-with-brand-manifest.json',data)
status=read('production/completion-status.json');status.pop('publicationState',None);status.update(status='complete_game_art_release_v4',pending=[],validation='exports/release-v4-validation.json',publicationVerification='See the current Git remote and the separately written publication verification receipt.');write('production/completion-status.json',status)
page=(R/'index.html').read_text(encoding='utf-8');a=page.index('const DATA=')+len('const DATA=');b=page.index(';\n',a);page=page[:a]+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+page[b:];(R/'index.html').write_text(page,encoding='utf-8')
files={x.decode('utf-8') for x in subprocess.run(['git','ls-files','-z'],cwd=R,capture_output=True,check=True).stdout.split(b'\0') if x}
files.discard('exports/git-publication-files.json')
files.update(['docs/ART_RELEASE_V4.md','exports/release-v4-validation.json','exports/brand-publication-verification.json'])
for p in (R/'work/release-v4').rglob('*'):
    if p.is_file() and p.suffix in ['.py','.json','.md','.cjs']:files.add(p.relative_to(R).as_posix())
for file in files:
    assert (R/file).is_file(),file
    assert not any(part in ['.git','.work','prototypes','__pycache__','node_modules'] for part in Path(file).parts),file
    assert not Path(file).name.startswith('.env') and not file.endswith('.zip'),file
entries=[{'file':f,'bytes':(R/f).stat().st_size,'sha256':sha(f)} for f in sorted(files)]
archive='exports/yunjian-queshe-complete-art-v4.zip'
manifest={'schemaVersion':4,'createdAt':datetime.now(timezone.utc).isoformat(),'gameName':'云间雀社','archive':archive,'payloadCount':len(entries),'payloadBytes':sum(e['bytes'] for e in entries),'primaryAssetCount':293,'pageLayouts':32,'stateCompositions':86,'files':entries,'selfHashExcluded':True,'notes':['Includes all final art, brand, native sources, prompts, records, layouts, proofs and engine integration docs.','Package manifest included but excluded from its own hash. CRC and archive checksum reports are outside archive to avoid a hash cycle.','Git publication manifest describes the public repository separately; old v1/v2/v3 reports are historical evidence.']}
write('exports/release-v4-package-files.json',manifest)
with zipfile.ZipFile(R/archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for e in entries:z.write(R/e['file'],e['file'])
    z.write(R/'exports/release-v4-package-files.json','exports/release-v4-package-files.json')
with zipfile.ZipFile(R/archive) as z:
    assert z.testzip() is None
    assert set(z.namelist())==files|{'exports/release-v4-package-files.json'}
    for e in entries:
        raw=z.read(e['file']);assert len(raw)==e['bytes'] and hashlib.sha256(raw).hexdigest()==e['sha256'],e['file']
    assert z.read('exports/release-v4-package-files.json')==(R/'exports/release-v4-package-files.json').read_bytes()
report={'schemaVersion':4,'status':'passed','verifiedAt':datetime.now(timezone.utc).isoformat(),'archive':archive,'sha256':sha(archive),'bytes':(R/archive).stat().st_size,'memberCount':len(entries)+1,'payloadHashesVerified':len(entries),'primaryAssetsIncluded':293,'pageLayouts':32,'stateCompositions':86,'zipCRC':'passed','errors':[],'clientIntegrated':False}
write('exports/release-v4-package-verification.json',report)
print(json.dumps(report))
