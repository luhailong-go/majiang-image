from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
hold=R/'.work/production-v3/resource-hold.json'
if hold.is_file() and read('.work/production-v3/resource-hold.json').get('status')=='holding_local_heavy_work':raise SystemExit('Finalization deferred while final checks are held.')
qa=read('exports/production-v3-validation.json');assert qa['status']=='passed' and not qa['errors']
for file,digest in {**qa['recordHashes'],**qa['dependencyHashes'],**qa['sourceManifestHashes'],**qa['productionBindingHashes']}.items():assert sha(file)==digest,'Changed after validation '+file
d=read('exports/production-art-v3-manifest.json');assert len(d['assets'])==292
d['deliveryStatus']='complete_production_art_v3';d['completedAt']=datetime.now(timezone.utc).isoformat();d['validationReport']='exports/production-v3-validation.json';d['productionGalleryValidation']='production/gallery-validation.json';write('exports/production-art-v3-manifest.json',d)
status=read('production/completion-status.json');status.update(status='complete_production_art_v3',pending=[],proofImages=32+d['productionStates'],validation='exports/production-v3-validation.json',resourceCoordination='production/resource-coordination.json',clientIntegrated=False);write('production/completion-status.json',status)
template=(R/'work/full-game-gallery-template.html').read_text(encoding='utf-8-sig').replace('完整游戏美术 · v2','完整游戏美术 · v3').replace('docs/FULL_GAME_ART_SCOPE.md','docs/PRODUCTION_ART_COMPLETION_V3.md').replace('exports/full-game-art-manifest.json','exports/production-art-v3-manifest.json')
template=template.replace('<body>','<body><div style="padding:12px 24px;background:#165b4a;color:#fff9e9;text-align:center"><a style="color:#fff9e9;font-weight:700" href="production/index.html">查看32页面与'+str(d['productionStates'])+'状态的独立素材组合</a></div>')
(R/'index.html').write_text(template.replace('__DELIVERY_DATA__',json.dumps(d,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
readme=f'''# 道家Q版麻将 · 整款游戏美术 v3

通用四人横屏麻将的完整美术和接入参考，覆盖休闲匹配、好友房、四人牌桌、结算、四位角色和UI01—UI32既有模块。沿用指定邮件/组队原图的玉绿、象牙米白、暖金手绘风格。正式品牌、地方番型和商业付费未指定，不自行添加。

## 使用入口

- [全部美术画廊](index.html)：概念整屏、运行切片、角色、牌面、场景、道具与特效。
- [独立素材组合参考](production/index.html)：32页面、{d['productionStates']}状态；按钮、文字、角色与牌面分层，支持四角色详情和桌面纹理选择。
- [下载公开仓库全部文件](https://github.com/luhailong-go/majiang-image/archive/refs/heads/main.zip) · [公开仓库](https://github.com/luhailong-go/majiang-image)
- [总清单](exports/production-art-v3-manifest.json) · [最终文件与来源验收](exports/production-v3-validation.json) · [本轮完成合同](docs/PRODUCTION_ART_COMPLETION_V3.md)

clone或解压后直接打开根index.html。素材用普通Git保存，无LFS指针；无需配置图片API账号。

## 实际交付

| 类别 | 内容 |
|---|---|
| 正式主PNG | **292项**，按正式文件去重；原270项已验收像素保持 |
| 概念整屏 | 38张，覆盖32个原UI合同ID，独立于运行素材组合参考 |
| UI独立控件 | **102项**；原80项加6空态、10表单皮肤、6对局状态皮肤 |
| 人物 | 4位全身、4座头像、16独立表情；开心/思考/惊讶/沮丧统一绑定 |
| 牌面和牌具 | 34标准面、8可选花牌、牌胚/牌背/高亮，34项牌具/交流/物品图标 |
| 场景与装扮 | 3张纯背景、3套空桌主题；两套新增牌背、标题/加载装饰与应用图标变体 |
| 特效 | 35正式PNG，6条播放时序、24真实阶段帧、独立中文提示与结算装饰 |
| 接入组成树 | **32页面、{d['productionStates']}状态**；逐层坐标、独立图片路径、文字/数据绑定、九宫格和交互状态 |
| 对局组合 | 四座手牌/暗手/两层牌墙/弃牌、16种方向副露示例、多候选/听牌/非法牌/最后弃牌、动态标识与结算 |
| 组合检查图 | {32+d['productionStates']}张根页面/状态组合图，另有各域深浅底与专项检查图；均为派生检查图，不混算新增原画 |

新增四张原生母图切出22项必要运行素材。表单补齐focus/error、list selected/pressed、独立progress、toggle与slider fill；对局补齐候选容器、听牌提示、选中外框、不可出牌/最后弃牌/听牌底章。禁用、数字、昵称、分数、倒计时和进度仍由原生UI层表达，不从整屏抠文字或示例牌。

## 接入与证据

[production/layouts.json](production/layouts.json)和[production/states.json](production/states.json)是可读组成树，设计画布1600×900；PNG组合预览为1280×720的机械缩小检查图，不冒称新原生分辨率。每个界面列出独立资源、坐标、配置文本和状态素材。样例四家分数分别绑定result.players[0..3]，角色以selectedCharacterId绑定，领取前后互斥，听牌/动作由合法候选控制。

只对manifest允许的素材作九宫格；新增输入描边/列表只横向，开关/滑块/人物/牌面与珠饰等比。所有新运行切片有真实Alpha和逐图记录。来源、实际提示词与真实参考保留，目标GPT Image2.5 Sunburst/max；内置工具没有可核实实际型号/质量返回，因此实际字段保持null。

本包交付整款已定范围的美术和接入资料。真实客户端/服务端、平台账号、规则和目标设备须由游戏工程另行验收。图片实看、组合图及静态脚本检查均有记录；本地file浏览被工具策略拒绝后没有绕行，未声称真实浏览器或游戏客户端实测。

## 文档与后续

[完整接入说明](docs/FULL_GAME_INTEGRATION.md) · [新增表单组合](assets/ui/production-v3/forms/compositions.json) · [牌桌运行组合](assets/ui/production-v3/gameplay/runtime-compositions.json) · [人物/效果/主题绑定](assets/presentation/production-v3/)

本地目录为D:\\work\\majiang-image；新参考放references/incoming/。本地最新离线ZIP为exports/mahjong-complete-game-art-v3.zip，不重复提交大ZIP到Git；GitHub的Download ZIP可下载全部发布文件。旧v2报告是当时270项交付的历史证据，不冒称v3当前检查报告。

用户已授权公开仓库luhailong-go/majiang-image，main只维护一个无父提交；当前发布按[公开规则](docs/PUBLIC_REPOSITORY.md)进行。开始新图前读[AGENTS.md](AGENTS.md)、配置和逐图记录规则。
'''
(R/'README.md').write_text(readme,encoding='utf-8')
public=(R/'docs/PUBLIC_REPOSITORY.md').read_text(encoding='utf-8-sig')
public=public.replace('正式美术仍为 270 项主 PNG','v3 正式美术为 292 项主 PNG；此前270项保持像素不变，新增22项运行素材')
public=public.replace('本地离线包 `exports/mahjong-complete-game-art-v2.zip` 约 308 MB，不重复放入 Git。','本地最新离线包 `exports/mahjong-complete-game-art-v3.zip` 不重复放入 Git。旧v2包按最新素材保留规则处理，来源与历史校验文字保留。')
(R/'docs/PUBLIC_REPOSITORY.md').write_text(public,encoding='utf-8')
print(json.dumps({'status':d['deliveryStatus'],'primaryAssets':292,'pages':32,'states':d['productionStates'],'newRuntimeAssets':22}))
