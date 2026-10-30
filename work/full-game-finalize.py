from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,shutil,sys,runpy
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=read('exports/full-game-art-manifest.json')
assert read('exports/full-game-validation.json')['status']=='passed'
runpy.run_path(str(R/'work/full-game-freshness.py'))['assert_fresh'](data,read('exports/full-game-validation.json'))
assert read('exports/full-game-gallery-validation.json')['status']=='passed'
for source,name in [('work/full-game-fx/root-scenes-independent-qa.json','scenes-branding-independent-qa.json'),('work/full-game-fx/ui-components-independent-qa.json','supplemental-components-independent-qa.json'),('work/full-game-props/ui-pages-independent-qa.json','supplemental-pages-independent-qa.json')]:
    src=R/source
    assert src.is_file(),source
    report=json.loads(src.read_text(encoding='utf-8-sig'))
    assert report.get('status') in ['passed','complete_qa_passed'],(source,report.get('status'))
    shutil.copyfile(src,R/'exports'/name)
data['deliveryStatus']='complete_full_game_art_delivery'
data['completedAt']=datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
data['validationReport']='exports/full-game-validation.json'
data['galleryValidation']='exports/full-game-gallery-validation.json'
data['independentReviews']=['exports/scenes-branding-independent-qa.json','exports/supplemental-components-independent-qa.json','exports/supplemental-pages-independent-qa.json']
write('exports/full-game-art-manifest.json',data)
old=read('exports/ui-delivery-manifest.json')
old['package']='exports/mahjong-complete-game-art-v2.zip'
old['supersededByFullGameManifest']='exports/full-game-art-manifest.json'
old['previousMilestonePackage']={'file':'exports/mahjong-ui-full-suite-v1.zip','sha256':'eb5e1a7ba819e6463ecb9284c929d87200fcfda6d63e4cf2f70ee4de22dc81d3','purpose':'historical UI-only milestone; complete art is delivered in v2'}
write('exports/ui-delivery-manifest.json',old)
template=(R/'work/full-game-gallery-template.html').read_text(encoding='utf-8-sig')
(R/'index.html').write_text(template.replace('__DELIVERY_DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
rows=[]
for i in range(1,33):
    id=f'UI{i:02d}';items=[p for p in data['pages'] if p['id']==id]
    rows.append('| '+id+' | '+' · '.join('['+p['title']+']('+p['file']+')' for p in items)+' |')
readme=f'''# 道家Q版麻将 · 完整游戏美术 v2

本地项目：`D:\\work\\majiang-image`。按用户“完整游戏全部美术，没达到就继续做完”的要求，已完成[通用四人横屏2D麻将美术合同](docs/FULL_GAME_ART_SCOPE.md)。沿用原image项目两张指定成图的道家Q版高清手绘风格，新增素材均实际附参考生成。

## 浏览与交付

- [统一美术画廊](index.html)：界面、切片、牌面、角色、场景、道具、特效和标识8类，支持搜索、查看原图和透明深浅底。
- [完整游戏美术包](exports/mahjong-complete-game-art-v2.zip)：目录、来源、提示词、清单、QA和接入资料一并交付。
- [完整接入说明](docs/FULL_GAME_INTEGRATION.md) · [总清单](exports/full-game-art-manifest.json) · [完整性验收](exports/full-game-validation.json)
- [特效播放页](assets/fx/full-game/index.html) · [牌具/物品页](assets/props/full-game/index.html) · [基础牌面页](assets/tiles/index.html)

## 已交付内容

| 类别 | 实际内容 | 说明 |
|---|---|---|
| 界面与状态 | {len(data['pages'])}张完整图，覆盖32个UI合同ID | 含原UI01—24、新增UI25—32，三步教学与奖励两态；UI23/24为规范板 |
| 透明组件 | {len(data['components'])}项 | 通用/对局58项加配套22项，伸缩和互斥状态逐项登记 |
| 人物 | 4位全身、4座头像、16独立表情 | 金带道童、银发医师、白眉老道、黑发侠女；角色为静态立绘与表情 |
| 牌材 | 34标准面、8可选花牌，另有牌胚/牌背/高亮 | 合计42种正面图；花牌不强制加入当前玩法 |
| 道具与图标 | 34项 | 骰子1—6、骰盅开合/起庄/筹棒4项，交流12项，物品12项 |
| 特效 | 35项正式PNG、6条播放时序 | 8中文提示+24真实阶段帧+2结算装饰+1无字底；含Aseprite图集和WebP |
| 场景与桌面 | 3纯场景、3空桌主题 | 新增5图加已有青绿桌面，中心无烘焙牌与控件 |
| 标识与牌背 | 9项导出 | 2新牌背、标题牌、加载装饰、独立原生大图导出的1024图标及4小尺寸变体 |

总计**{data['primaryAssetCount']}项主PNG**，按实际文件全局去重。来源母图、图集、支持层与QA拼图另列，不混算独立原画；同一图标的大小变体已明确标记。

## 验收与实际能力

原127项通过的主图哈希保持不变。新图已检查中文、牌面/点数、轮廓、透明深浅底和道家Q版一致性。教学箭头尖端已按实际像素修正；领取、选中与使用中状态分别映射。全包检查每项尺寸、哈希、来源、提示词和依赖，并独立复核各域。检查报告见`exports/`。

页面通常原生1672×941，真实尺寸逐图记录。角色及切片没有通过放大冒称新原生细节。特效四阶段为实际不同图像，客户端可选淡化补间；不是影片或角色骨骼动画。

模型目标为GPT Image2.5 Sunburst/max，入口为宿主内置image_gen。工具没有可核实的实际型号/质量返回，这两字段如实保持null。每张生成/AI编辑/派生图保留同名记录，实际提示词在`prompts/`，风格参考在`references/style/`。

本包完成美术资源与接入资料。真实客户端/服务端尚未接入；正式名称、地方番型、账号与支付合同未指定。公告/成就/排行/收藏是可选通用模块美术，未虚构收费。画廊已做静态脚本/文件检查；本地file协议被内置浏览器策略拒绝，没有绕行，也不声称真实浏览器交互实测。

## 页面索引

| ID | 完整图与独立状态 |
|---|---|
'''+ '\n'.join(rows)+'''

## 后续参考与上传

新参考图放入`references/incoming/`。全部成果已保存到本项目；未配置远端、未上传，不继承原image仓库的上传职责。完整ZIP可交给客户端工程接入；网络上传地址由用户另行指定。

继续制作先读[AGENTS.md](AGENTS.md)、[风格](docs/STYLE_GUIDE.md)、[统一图像设置](config/image-generation.json)和[完整游戏合同](docs/FULL_GAME_ART_SCOPE.md)。
'''
(R/'README.md').write_text(readme,encoding='utf-8')
p=R/'docs/PRODUCTION_BRIEF.md';brief=p.read_text(encoding='utf-8-sig')
marker='\n## 完整游戏美术v2完成'
if marker in brief:brief=brief.split(marker)[0]
brief+=f'''{marker}（2026-10-26）

用户在UI包完成后明确要求全游戏美术继续补完，当前以docs/FULL_GAME_ART_SCOPE.md为范围合同。现已完成{len(data['pages'])}张界面/状态图、{len(data['components'])}项组件、4全身/16表情、34标准牌/8花牌、34牌具与图标、35效果资源/6clips、独立场景/桌面和标识。总清单按文件去重为{data['primaryAssetCount']}主PNG。原127项哈希不变；新域视觉与统一文件/来源检查通过。请使用根index.html与exports/mahjong-complete-game-art-v2.zip；旧UI包是此前里程碑，不代表本轮全美术范围。客户端接入、正式品牌与地方规则仍分别验收。
'''
p.write_text(brief,encoding='utf-8')
print(json.dumps({'status':data['deliveryStatus'],'primaryAssets':data['primaryAssetCount'],'pages':len(data['pages']),'components':len(data['components'])},ensure_ascii=False))
