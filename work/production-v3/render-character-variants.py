from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, copy
R=Path(__file__).resolve().parents[2]
def read(file): return json.loads((R/file).read_text(encoding='utf-8-sig'))
def sha(file): return hashlib.sha256((R/file).read_bytes()).hexdigest()
def write(file, data):
    p=R/file
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
hold=R/'.work/production-v3/resource-hold.json'
if hold.is_file() and read('.work/production-v3/resource-hold.json').get('status')=='holding_local_heavy_work':
    raise SystemExit('Deferred during shared heavy-work hold.')
renderer=R/'work/production-v3/render-compositions.py'
scope={'__file__':str(renderer)}
exec(compile(renderer.read_text(encoding='utf-8').split("pages=read('production/layouts.json')")[0], str(renderer), 'exec'), scope)
page=next(x for x in read('production/layouts.json')['pages'] if x['id']=='UI26')
catalog=read('assets/presentation/production-v3/character-bindings.json')
stamp=datetime.now(timezone.utc).isoformat()
proofs=[]
for role, char in catalog['charactersById'].items():
    layers=copy.deepcopy(page['layers'])
    for node in layers:
        binding=node.get('binding','')
        if binding.endswith('.fullBody.file'):
            node.update(file=char['fullBody']['file'],record=char['fullBody']['record'])
        elif binding.endswith('.displayName'): node['text']=char['displayName']
        elif binding.endswith('.description'): node['text']=char['description']
        elif '.expressions.' in binding and binding.endswith('.file'):
            emotion=binding.split('.expressions.',1)[1].split('.')[0]
            node.update(file=char['expressions'][emotion]['file'],record=char['expressions'][emotion]['record'])
    canvas=scope['compose'](layers,'UI26-'+role).resize((1280,720),scope['Image'].Resampling.LANCZOS)
    file='production/previews/characters/UI26-'+role+'.png'
    (R/file).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(R/file)
    dependencies=sorted({n['file'] for n in layers if n.get('file')} | {f for n in layers for f in n.get('stateAssets',{}).values()})
    record={'schemaVersion':3,'file':file,'sha256':sha(file),'width':1280,'height':720,'mode':'RGB','format':'PNG','createdAt':stamp,'newModelGeneration':False,'actualModel':None,'actualQuality':None,'derivedFrom':[{'file':f,'sha256':sha(f),'record':f+'.generation.json'} for f in dependencies],'operation':{'type':'independent_asset_UI_character_variant','selectedCharacterId':role,'layoutSource':'production/layouts.json','layoutId':'UI26','layoutSha256':sha('production/layouts.json'),'bindingSource':'assets/presentation/production-v3/character-bindings.json','bindingSha256':sha('assets/presentation/production-v3/character-bindings.json'),'rendererSha256':sha('work/production-v3/render-compositions.py'),'variantScriptSha256':sha('work/production-v3/render-character-variants.py')},'inspection':{'status':'pending_actual_visual_review'}}
    write(file+'.generation.json',record)
    proofs.append({'id':role,'file':file,'sha256':record['sha256'],'record':file+'.generation.json'})
assert not scope['fitIssues'],scope['fitIssues']
write('production/character-variant-proofs.json',{'status':'pending_visual_review','createdAt':stamp,'images':proofs,'browserInteraction':False,'clientIntegrated':False})
print(json.dumps({'characterVariantProofs':len(proofs),'textFitIssues':scope['fitIssues']}))
