from pathlib import Path
import json,re,hashlib
root=Path(r"D:\work\majiang-image")
p=root/"work/record-input.json"
data=json.loads(p.read_text(encoding="utf-8-sig"))
ui=data["records"][1]["checks"]
ui["independentVisualReviewCompleted"]=True
ui["unresolvedIssues"] += [
    {"id":"UI-TILE-01","severity":"nonblocking_concept_note","description":"装饰二筒使用旋纹图案；后续正式牌面需单独统一，当前不把概念装饰当作可用牌面素材。"},
    {"id":"UI-SMALL-SCREEN-01","severity":"nonblocking_concept_note","description":"场景细节与标题较醒目，正式交互稿阶段需在目标小屏尺寸复核视觉负担。"}
]
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
readme=root/"README.md"
text=readme.read_text(encoding="utf-8-sig")
text=text.replace("2026-10-26 已建立项目目录、风格规则、生成配置和参考图清单。首批为大厅概念与迎宾道童，具体进度见 [制作说明](docs/PRODUCTION_BRIEF.md)。成图生成后须在下面补充图片和记录索引，不把参考图当作新生成成果。", "2026-10-26 首批大厅与迎宾道童 v1 已生成并保存，均为待用户评审的美术方向稿。已完成原生尺寸、PNG 完整性、来源哈希、中文、风格和角色轮廓检查；道童具有真实 Alpha，但透明边缘清洁度仍有待修项。具体状态见 [制作说明](docs/PRODUCTION_BRIEF.md)。")
text=text.replace("新图索引：尚未生成。", """## 新图索引（首批 v1）

| 图片 | 原生规格 | 检查状态 | 制作记录 |
|---|---|---|---|
| [麻将大厅 v1](designs/ui/mahjong-lobby-v1.png) | 1672×941，RGB PNG，约 16:9 | 可评审方向稿；五项中文与主次层级通过 | [提示词](prompts/mahjong-lobby-v1.prompt.txt) · [生成与检查记录](designs/ui/mahjong-lobby-v1.png.generation.json) |
| [迎宾道童 v1](designs/characters/welcome-daotong-v1.png) | 1254×1254，RGBA PNG，真实透明 | 可评审方向稿；少量边缘黄红杂点待清理，构图留白偏紧 | [提示词](prompts/welcome-daotong-v1.prompt.txt) · [生成与检查记录](designs/characters/welcome-daotong-v1.png.generation.json) |

使用宿主内置 image_gen。配置目标为 GPT Image 2.5 Sunburst/max；本次工具没有 model/quality 参数，也未披露可核实实际版本，逐图记录的 actualModel、actualQuality 均为 null（未确认）。以上为工具原生返回尺寸，未放大或拉伸；目标尺寸 2048×1152 / 1536×1536 未作为实际尺寸宣称。

大厅实际附入两张主 UI 参考、道童横幅及本批独立道童；角色实际附入三张原始风格参考。图片、提示词和记录均已落盘，参考 SHA-256 经核对。标题“麻将大厅”仅为功能标题，未确定正式游戏名或地方玩法。

### 首批预览

![麻将大厅概念稿 v1](designs/ui/mahjong-lobby-v1.png)

![透明迎宾道童 v1](designs/characters/welcome-daotong-v1.png)

### 后续待修与验收边界

- 道童：发丝、发带、衣缘和鞋边存在细碎黄红色杂点，透明区亦有少量低 Alpha 噪点；正式入库前需清理并在深浅底复核。顶部和右侧留白偏紧，当前手脚与飘带完整。
- 大厅：装饰二筒的旋纹画法仅用于概念；正式牌面另行统一。标题与场景细节较醒目，后续在确定的目标设备上检查小屏视觉负担。
- 两张均未经过用户最终确认，不代表正式切片、角色入库、玩法或客户端接入验收。当前仅本地制作，未配置远端、未上传。""")
readme.write_text(text,encoding="utf-8")
brief=root/"docs/PRODUCTION_BRIEF.md"
text=brief.read_text(encoding="utf-8-sig")
text=text.replace("- 大厅概念稿：待制作。","- 大厅概念稿：v1 已落盘（designs/ui/mahjong-lobby-v1.png），原生 1672×941 RGB；中文、主次层级、风格检查通过，可供方向评审，未用户定稿。")
text=text.replace("- 迎宾道童：待制作。","- 迎宾道童：v1 已落盘（designs/characters/welcome-daotong-v1.png），原生 1254×1254 RGBA；真实 Alpha、身份与完整手脚通过首稿检查，边缘黄红色杂点待清理，尚未正式入库验收。")
text += "\n## 首批完成记录\n\n两张首稿于 2026-10-26（America/New_York）通过宿主内置 image_gen 生成。实际提示词位于 prompts/，同名 .png.generation.json 与成图并排保存，含来源哈希、实际输入参考、原生尺寸、检查结果及具体待修项。模型与质量实际值未由工具披露，保持 null。未通过重采样伪造目标尺寸；README 已补图像与记录索引。\n"
brief.write_text(text,encoding="utf-8")
print("README and production brief updated; independent lobby review recorded.")

