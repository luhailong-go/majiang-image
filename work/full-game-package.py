from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,zipfile,re,sys,runpy
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp():return datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
data=json.loads((R/'exports/full-game-art-manifest.json').read_text(encoding='utf-8'))
assert data['deliveryStatus']=='complete_full_game_art_delivery'
validation=json.loads((R/'exports/full-game-validation.json').read_text(encoding='utf-8'))
assert validation['status']=='passed' and not validation['errors']
runpy.run_path(str(R/'work/full-game-freshness.py'))['assert_fresh'](data,validation)
files=set()
allowed={'.png','.webp','.svg','.json','.md','.html','.txt','.py','.ps1','.cjs','.js','.mjs','.tres','.tscn'}
for folder in ['assets','config','docs','prompts','designs','references/style']:
    for p in (R/folder).rglob('*'):
        if p.is_file() and p.suffix.lower() in allowed and '__pycache__' not in p.parts:files.add(p)
for p in ['AGENTS.md','README.md','index.html','references/manifest.json','references/incoming/README.md','exports/full-game-art-manifest.json','exports/full-game-validation.json','exports/full-game-gallery-validation.json','exports/ui-delivery-manifest.json','exports/delivery-validation.json','exports/component-independent-qa.json','exports/gallery-script-validation.json','exports/scenes-branding-independent-qa.json','exports/supplemental-components-independent-qa.json','exports/supplemental-pages-independent-qa.json']:
    files.add(R/p)
for p in (R/'work').glob('full-game*'):
    if p.is_file() and p.suffix.lower() in allowed:files.add(p)
# Include extant provenance/QA/export scripts referenced by delivered metadata.
# Historical cleaned work images remain textual evidence, not missing runtime files.
pending=list(files);seen=set()
while pending:
    p=pending.pop()
    if p in seen:continue
    seen.add(p)
    if p.suffix.lower() not in {'.json','.md','.html','.txt','.py','.js','.cjs','.mjs'}:continue
    txt=p.read_text(encoding='utf-8-sig')
    for s in re.findall(r'work/[A-Za-z0-9_./-]+\.(?:png|webp|json|py|ps1|cjs|js|html|md|txt)',txt):
        q=(R/s).resolve()
        if q.is_relative_to(R) and q.is_file() and q not in files:files.add(q);pending.append(q)
for p in files:assert p.is_file() and p.resolve().is_relative_to(R),str(p)
entries=[{'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]
fm={'schemaVersion':2,'createdAt':stamp(),'archive':'mahjong-complete-game-art-v2.zip','payloadFileCount':len(entries),'payloadBytes':sum(e['bytes'] for e in entries),'selfHashExcluded':True,'files':entries,'scope':'Complete generic four-player2D Mahjong art package; actual client integration separate','notes':['Relative project paths preserved. Primary assets, current native sources, exact prompts and provenance/QA/integration files included.','No credentials or account configuration included.','This manifest is included in ZIP but excluded from its own recursive hash.']}
manifest=R/'exports/full-game-package-files.json';manifest.write_text(json.dumps(fm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive=R/'exports/mahjong-complete-game-art-v2.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for e in entries:z.write(R/e['file'],e['file'])
    z.write(manifest,'exports/full-game-package-files.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=set(z.namelist())
    for e in entries:
        assert e['file'] in names,e['file']
        assert hashlib.sha256(z.read(e['file'])).hexdigest()==e['sha256'],e['file']
    assert z.read('exports/full-game-package-files.json')==manifest.read_bytes()
result={'schemaVersion':2,'status':'passed','archive':archive.relative_to(R).as_posix(),'sha256':sha(archive),'bytes':archive.stat().st_size,'memberCount':len(names),'payloadHashesVerified':len(entries),'zipCRC':'passed','primaryAssetsIncluded':len(data['assets']),'verifiedAt':stamp(),'clientIntegrated':False,'uploaded':False,'browserInteraction':'not_run_policy_blocked','errors':[]}
(R/'exports/full-game-package-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
