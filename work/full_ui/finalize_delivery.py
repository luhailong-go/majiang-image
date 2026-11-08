from pathlib import Path
from datetime import datetime,timezone,timedelta
import json, shutil
R=Path(r"D:\work\majiang-image")
m=json.loads((R/"exports/ui-delivery-manifest.json").read_text(encoding="utf-8"))
v=json.loads((R/"exports/delivery-validation.json").read_text(encoding="utf-8"))
assert v["status"]=="passed" and not v["errors"]
for f in ["work/full_ui/component-independent-qa.json","exports/gallery-script-validation.json"]:
 assert (R/f).is_file()
shutil.copyfile(R/"work/full_ui/component-independent-qa.json",R/"exports/component-independent-qa.json")
m["deliveryStatus"]="complete_static_art_delivery"
m["completedAt"]=datetime.now(timezone(timedelta(hours=-4))).isoformat()
m["validationReport"]="exports/delivery-validation.json"
m["independentAssetReview"]="exports/component-independent-qa.json"
m["gallerySourceTests"]="exports/gallery-script-validation.json"
m["package"]="exports/mahjong-ui-full-suite-v1.zip"
m["scopeLimitations"]=["真实客户端/服务端未接入","正式游戏名、地方规则未确定","浏览器file://被策略拒绝，实浏览交互未测试；静态路径、语法及10项mock DOM源代码行为检查通过"]
(R/"exports/ui-delivery-manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
template=(R/"work/full_ui/gallery-template.html").read_text(encoding="utf-8-sig")
(R/"index.html").write_text(template.replace("__DELIVERY_DATA__",json.dumps(m,ensure_ascii=False).replace("</","<\\/")),encoding="utf-8")
rows=[]
for i in range(1,25):
 id="UI%02d"%i;items=[p for p in m["pages"] if p["id"]==id]
 rows.append("| "+id+" | "+" · ".join("["+p["title"]+"]("+p["file"]+")" for p in items)+" | 已检查 |")
readme="""# 麻将游戏 UI 与角色 · 完整美术交付 v1

本地项目：D:\\work\\majiang-image。沿用原 image 项目的道家 Q 版高清手绘风格。2026-10-26 已按 [完整合同](docs/FULL_UI_SCOPE.md) 完成静态美术交付，实际客户端与服务端接入另行验收。

## 打开与下载

- [本地画廊](index.html)：双击 index.html，按页面、组件、牌面、角色分类浏览；支持搜索、原图查看和透明素材深浅底切换。
- [完整交付包](exports/mahjong-ui-full-suite-v1.zip)：解压后打开其中 index.html，目录结构保持一致。
- [机器可读总清单](exports/ui-delivery-manifest.json) · [完整性检查](exports/delivery-validation.json) · [接入说明](docs/UI_INTEGRATION.md)

## 交付内容

| 类别 | 数量与内容 | 清单/说明 |
|---|---|---|
| 页面和状态规范板 | 27 张完整图，覆盖 UI01—UI24 共24个合同ID；匹配成功、流局和邮件已领取为额外独立状态 | [页面与状态总清单](exports/ui-delivery-manifest.json) |
| 通用与对局组件 | 58 项，含通用45项、对局13项及独立牌桌背景；24组组合映射 | [组件清单](assets/ui/manifest.json) · [伸缩/状态说明](assets/ui/README.md) |
| 基础牌材 | 34种牌面、统一牌背、空白牌胚与状态高亮层 | [牌面清单](assets/tiles/manifest.json) · [牌面浏览](assets/tiles/index.html) · [交付说明](docs/TILES_DELIVERY.md) |
| 角色配套 | 1张修净透明全身道童、4个不同身份的座位头像 | [角色清单](assets/characters/manifest.json) · [角色检查](assets/characters/QA.md) |
| 制作来源 | 实际提示词、逐图记录、实际输入参考、SHA-256、原生与派生尺寸 | prompts/、相邻 .generation.json |

独立整屏常用原生尺寸为1672×941（约16:9），实际尺寸逐图登记。透明道童由1254×1254原生内容清边并添加透明留白导出1536×1536；没有放大细节。头像512×512、牌材448×640为记录清楚的派生输出。

## 页面索引

| ID | 页面与独立状态 | 检查 |
|---|---|---|
"""+ "\n".join(rows)+"""

## 已完成的修正与检查

- 迎宾道童已清除低Alpha孤立点并加足透明留白；正式文件为 assets/characters/welcome-daotong.png，生成来源图不作为最终透明素材使用。
- UI18待领取与已领取分成独立互斥状态；已领取页禁用领取、恢复删除。
- 积分统一正分朱砂红、负分玉绿；动态文字token见 [ui-tokens.json](config/ui-tokens.json)。
- 窗框九宫格边距为200；主/次/对局按钮只允许横向伸缩并锁定高度；结算卡与人物/头像等比显示。
- 127项主PNG、132份来源记录和56项必需状态映射通过文件、尺寸、哈希与引用检查。组件/角色/牌面另有 [独立验收](exports/component-independent-qa.json)。
- 画廊静态引用、JS语法和10项内存mock DOM源代码行为检查通过。内置浏览器URL策略拒绝file://，未绕过策略，也未宣称真实浏览器渲染/交互实测通过，见 [画廊检查](exports/gallery-script-validation.json)。

## 风格、模型与边界

两张主参考及道童横幅已实际查看并用于对应生成，来源与哈希见 [参考清单](references/manifest.json)。配置目标为 GPT Image 2.5 Sunburst/max；内置工具未提供型号/质量选择器和可核实实际值，记录保持 actualModel/actualQuality=null。生成底图、AI编辑、程序排版牌面与裁切派生均分别登记。

“麻将大厅”仅是功能标题；地方规则、正式品牌、计分合同未确定，页面数字与昵称为布局样例。当前包是完整UI美术与接入资料，不是已经联机的麻将客户端。本项目未配置远端、未上传，未修改原 image 仓库。

新参考可放入 references/incoming/。后续制作先读 [AGENTS.md](AGENTS.md)、[风格](docs/STYLE_GUIDE.md) 与 [完整合同](docs/FULL_UI_SCOPE.md)。
"""
(R/"README.md").write_text(readme,encoding="utf-8")
brief=R/"docs/PRODUCTION_BRIEF.md"
text=brief.read_text(encoding="utf-8-sig")
text=text.replace("边缘黄红色杂点待清理，尚未正式入库验收。","首稿已由修净的 assets/characters/welcome-daotong.png 替代正式使用，最终透明边缘已检查通过。")
text+="""\n## 全套交付完成（2026-10-26）\n\n按 FULL_UI_SCOPE 完成24个合同ID、27张独立完整图、58项组件、34种标准牌面及牌背/牌胚、1张透明立绘与4头像。邮件领取互斥态、分数颜色及组件伸缩元数据已修正。逐图记录、56项必需状态映射、画廊、接入说明与ZIP均纳入交付。检查结果见 exports/delivery-validation.json。美术制作检查通过，用户最终产品确认与真实客户端/服务端接入仍单独验收。\n\n本地画廊的文件/JS静态检查通过；内置浏览器不允许file://，未做真实浏览器交互测试，也未采用替代路径绕过。\n"""
brief.write_text(text,encoding="utf-8")
print(json.dumps({"finalized":True,"pages":len(m["pages"]),"components":len(m["components"]),"states":len(m["states"]),"status":m["deliveryStatus"]}))

