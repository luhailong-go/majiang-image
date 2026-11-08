from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
old=read('exports/full-game-art-manifest.json');data=copy.deepcopy(old);new=[];sources=[]
for file in ['assets/ui/production-v3/empty/manifest.json','assets/ui/production-v3/forms/manifest.json','assets/ui/production-v3/gameplay/manifest.json']:
    m=read(file);sources.append({'file':file,'sha256':sha(file),'status':m.get('status')})
    for a in m['assets']:
        a=copy.deepcopy(a);a['title']=a.get('name') or a['id'];a['group']='生产控件与状态';a['assetKey']=a['file'].removesuffix('.png');new.append(a)
data['schemaVersion']=3;data['project']='道家Q版麻将整款游戏美术接入包';data['contract']='docs/PRODUCTION_ART_COMPLETION_V3.md';data['previousContract']='docs/FULL_GAME_ART_SCOPE.md'
data['components']+=new;data['assets']+=new;data['primaryAssetCount']=len(data['assets']);assert len({a['file'] for a in data['assets']})==data['primaryAssetCount']
data['newProductionAssetCount']=len(new);data['productionPages']=32;data['productionStates']=len(read('production/states.json')['states']);data['productionReference']='production/index.html';data['productionLayouts']='production/layouts.json';data['productionStateBindings']='production/states.json'
data['deliveryStatus']='pending_production_v3_final_validation';data['package']='exports/mahjong-complete-game-art-v3.zip';data['assembledAt']=datetime.now(timezone.utc).isoformat();data['sourceManifests']+= [s['file'] for s in sources]
data['sourceManifestHashes']={f:sha(f) for f in data['sourceManifests']}
data['productionBindingFiles']=['production/layouts.json','production/states.json','production/asset-index.json','assets/ui/production-v3/forms/compositions.json','assets/ui/production-v3/gameplay/runtime-compositions.json','assets/presentation/production-v3/character-bindings.json','assets/presentation/production-v3/effects-bindings.json','assets/presentation/production-v3/theme-bindings.json']
data['productionBindingHashes']={f:sha(f) for f in data['productionBindingFiles'] if (R/f).is_file()}
data['scopeLimitations']=['通用四人横屏麻将，包含UI01—32既有模块、四身份、三主题及可选花牌；未指定商业收费、正式品牌和地方番型','本包交付独立美术与可接入组成树；真实客户端/服务端及目标设备导入仍由游戏工程验收','所有新素材使用已指定风格和宿主内置图片入口；实际型号/质量未披露的字段保持null','本地文件浏览被策略拒绝，未绕行；组合PNG与静态脚本核验不冒称真实浏览器交互']
write('exports/production-art-v3-manifest.json',data)
template=(R/'work/full-game-gallery-template.html').read_text(encoding='utf-8-sig')
template=template.replace('完整游戏美术 · v2','完整游戏美术 · v3').replace('docs/FULL_GAME_ART_SCOPE.md','docs/PRODUCTION_ART_COMPLETION_V3.md').replace('exports/full-game-art-manifest.json','exports/production-art-v3-manifest.json')
template=template.replace('<body>','<body><div style="padding:12px 24px;background:#165b4a;color:#fff9e9;text-align:center"><a style="color:#fff9e9;font-weight:700" href="production/index.html">查看32页面与'+str(data['productionStates'])+'状态的独立素材组合</a></div>')
(R/'index.html').write_text(template.replace('__DELIVERY_DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
write('production/completion-status.json',{'status':'awaiting_final_preview_and_validation','newIndependentRuntimeAssets':len(new),'primaryAssets':data['primaryAssetCount'],'independentPageLayouts':32,'stateCompositions':data['productionStates'],'existingPassedAssetsUnchanged':270,'pending':['final corrected root composition PNG regeneration and inspection','gameplay four-seat HUD corrected proof','full file/source/record verification','offline gallery validation on final HTML','package and single-commit public update'],'resourceCoordination':'.work/production-v3/resource-hold.json','clientIntegrated':False})
print(json.dumps({'primaryAssets':data['primaryAssetCount'],'components':len(data['components']),'newIndependentAssets':len(new),'pages':32,'states':data['productionStates'],'status':data['deliveryStatus']}))
