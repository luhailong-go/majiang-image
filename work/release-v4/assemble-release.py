from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[2]
def read(f):return json.loads((R/f).read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256((R/f).read_bytes()).hexdigest()
def write(f,d):
    p=R/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=read('exports/game-art-with-brand-manifest.json')
assert len(data['assets'])==293 and len({a['file'] for a in data['assets']})==293
for a in data['assets']:assert sha(a['file'])==a['sha256'],a['file']
data.update(schemaVersion=4,project='云间雀社 · 完整麻将美术',gameName='云间雀社',deliveryStatus='pending_release_v4_validation',releaseContract='docs/ART_RELEASE_V4.md',package='exports/yunjian-queshe-complete-art-v4.zip',assembledAt=datetime.now(timezone.utc).isoformat(),validationReport='exports/release-v4-validation.json',productionGalleryValidation='production/gallery-validation.json')
data['sourceManifests']=list(dict.fromkeys(data['sourceManifests']+['assets/branding/yunjian-queshe/manifest.json']))
data['sourceManifestHashes']={f:sha(f) for f in data['sourceManifests']}
data['productionBindingFiles']=list(dict.fromkeys(data['productionBindingFiles']+['config/brand.json']))
data['productionBindingHashes']={f:sha(f) for f in data['productionBindingFiles']}
data['brandIntegratedPages']=['UI01','UI02','UI03','system.loading']
data['scopeLimitations'][0]='通用四人横屏麻将：UI01—32、四身份、三主题、可选花牌，品牌已定为云间雀社；地方番型、付费和平台SDK未指定。'
write('exports/game-art-with-brand-manifest.json',data)
write('production/completion-status.json',{'schemaVersion':4,'status':'pending_release_v4_validation','gameName':'云间雀社','primaryAssets':293,'newIndependentRuntimeAssets':22,'newNativeBrandLogo':1,'independentPageLayouts':32,'stateCompositions':86,'proofImages':118,'brandIntegratedPages':data['brandIntegratedPages'],'existingAccepted293NativePixelsUnchanged':True,'pending':['final unified validation','complete branded package CRC and payload verification','publish and anonymous download verification'],'currentManifest':'exports/game-art-with-brand-manifest.json','currentValidation':'exports/release-v4-validation.json','clientIntegrated':False})
template=(R/'work/full-game-gallery-template.html').read_text(encoding='utf-8-sig')
template=template.replace('麻将完整游戏美术 · v2','云间雀社 · 完整美术 v4').replace('麻将完整游戏美术画廊','云间雀社 · 完整游戏美术画廊').replace('docs/FULL_GAME_ART_SCOPE.md','docs/ART_RELEASE_V4.md').replace('exports/full-game-art-manifest.json','exports/game-art-with-brand-manifest.json')
bar='<div style="padding:12px 24px;text-align:center;background:#165b4a"><a style="color:#fff9e9" href="production/index.html">32页面与86状态的独立素材组合</a>　<a style="color:#fff9e9" href="assets/branding/yunjian-queshe/logo-primary.png">透明Logo原图</a></div>'
template=template.replace('<body>','<body>'+bar,1)
(R/'index.html').write_text(template.replace('__DELIVERY_DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
readme=(R/'README.md').read_text(encoding='utf-8-sig')
readme=readme.replace('正式品牌、地方番型和商业付费未指定，不自行添加。','游戏名为《云间雀社》，副标“麻将”；地方番型和商业付费未指定，不自行添加。')
readme=readme.replace('## 游戏名称与Logo（2026-10-28新增）','## 游戏名称与Logo')
readme=readme.replace('原v3离线包和验收报告是本次命名前已封存的292项基础包；本次Logo补充在当前Git仓库中，GitHub Download ZIP包含全部最新文件。牌面、角色与UI功能标题沿用已验收文件，本次不批量覆盖旧整屏图。Logo按等比使用，不作九宫格。','v4统一包包含全部293项正式美术、品牌Logo、32页86状态组成树及接入资料。登录/加载组合已使用Logo，大厅使用品牌名称。旧概念整屏保留为设计依据；当前运行排布以production/为准。Logo按等比使用，不作九宫格。')
readme=readme.replace('[总清单](exports/production-art-v3-manifest.json) · [最终文件与来源验收](exports/production-v3-validation.json) · [本轮完成合同](docs/PRODUCTION_ART_COMPLETION_V3.md)','[当前总清单](exports/game-art-with-brand-manifest.json) · [当前文件与来源验收](exports/release-v4-validation.json) · [最终交付说明](docs/ART_RELEASE_V4.md)')
readme=readme.replace('**292项**，按正式文件去重；原270项已验收像素保持','**293项**，包括品牌Logo；既有293项原生素材像素均保持')
readme=readme.replace('本地最新离线ZIP为exports/mahjong-complete-game-art-v3.zip','本地最新离线ZIP为exports/yunjian-queshe-complete-art-v4.zip')
readme=readme.replace('旧v2报告是当时270项交付的历史证据，不冒称v3当前检查报告。','旧v1/v2/v3报告是各自交付时的历史证据；当前检查以release-v4报告为准。')
(R/'README.md').write_text(readme,encoding='utf-8')
public=(R/'docs/PUBLIC_REPOSITORY.md').read_text(encoding='utf-8-sig').replace('本地最新离线包 `exports/mahjong-complete-game-art-v3.zip`','本地最新离线包 `exports/yunjian-queshe-complete-art-v4.zip`')
public+='\n\n## 当前统一交付 v4\n\n当前游戏名为《云间雀社》，293项正式主PNG包含Logo。当前总清单为exports/game-art-with-brand-manifest.json，完整包、组成树、品牌与文档统一核验；旧版本报告仅作历史证据。当前发布文件集见exports/git-publication-files.json，实际Push及匿名下载以最新发布回执为准。\n'
(R/'docs/PUBLIC_REPOSITORY.md').write_text(public,encoding='utf-8')
brief=R/'docs/PRODUCTION_BRIEF.md'
brief.write_text(brief.read_text(encoding='utf-8-sig')+'\n\n## 当前接手入口（2026-10-29）\n\n上述“未命名/未上传”和旧包是历史里程碑。当前游戏名为《云间雀社》，完整统一交付范围见docs/ART_RELEASE_V4.md，总清单见exports/game-art-with-brand-manifest.json，当前验收见exports/release-v4-validation.json。共293项正式主PNG、32页86状态，登录/加载/大厅已接入品牌。公开库为luhailong-go/majiang-image；以最新发布回执为准。\n',encoding='utf-8')
print(json.dumps({'assembled':True,'primaryAssets':293,'pages':32,'states':86,'unchangedNativeArt':293}))
