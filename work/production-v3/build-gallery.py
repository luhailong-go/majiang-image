from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pages=read('production/layouts.json')['pages'];states=read('production/states.json')['states']
bodies={r:'assets/characters/'+('welcome-daotong.png' if r=='daotong' else 'full-game/fullbody-'+r+'.png') for r in ['daotong','healer','master','swordswoman']}
expressions={f'expression-{r}-{e}':f'assets/characters/full-game/expression-{r}-{e}.png' for r in bodies for e in ['happy','thinking','surprised','sad']}
themes=['assets/ui/gameplay/table-background.png','assets/scenes/full-game/table-ivory-bamboo.png','assets/scenes/full-game/table-moon-lotus.png']
files=set(bodies.values())|set(expressions.values())|set(themes)
for p in pages+states:
    for n in p['layers']:
        if n.get('file'):files.add(n['file'])
        files.update(n.get('stateAssets',{}).values())
assets={}
for file in sorted(files):
    with Image.open(R/file) as im:width,height=im.size;mode=im.mode
    assets[file]={'file':file,'width':width,'height':height,'mode':mode,'sha256':hashlib.sha256((R/file).read_bytes()).hexdigest(),'record':file+'.generation.json'}
data={'pages':pages,'states':states,'assets':assets,'characterBodies':bodies,'expressions':expressions,'characterCatalog':read('assets/presentation/production-v3/character-bindings.json')['charactersById'],'themeFiles':themes}
template=(R/'work/production-v3/gallery-template.html').read_text(encoding='utf-8').replace('32 个页面与 75 个状态',str(len(pages))+' 个页面与 '+str(len(states))+' 个状态')
if (R/'config/brand.json').is_file():template=template.replace('麻将完整美术 · 独立素材组合',read('config/brand.json')['gameName']+' · 独立素材组合')
assert '__PRODUCTION_DATA__' in template
(R/'production/index.html').write_text(template.replace('__PRODUCTION_DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')),encoding='utf-8')
write('production/asset-index.json',{'schemaVersion':3,'status':'pending_final_qa','assetCount':len(assets),'assets':list(assets.values()),'allImagesIndependent':True,'screenConceptsUsedAsRuntimeSkins':False,'pageCount':len(pages),'stateCount':len(states)})
print(json.dumps({'pageCount':len(pages),'stateCount':len(states),'resolvedRuntimeFiles':len(assets),'htmlBytes':(R/'production/index.html').stat().st_size,'networkCalls':False}))
