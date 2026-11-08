# 麻将完整美术 v2：角色包

2026-10-26 用户要求继续补到完整游戏美术。本角色域已交付四位独立身份的全身透明素材，以及每位开心、思考、惊讶、沮丧四个表情头像，共 20 项运行素材。金带道童全身直接引用已有正式 PNG，新增 19 个运行 PNG；四张联系图不计入运行素材数量。

## 文件入口

- 正式素材清单：`assets/characters/full-game/manifest.json`。
- 逐项验收：`assets/characters/full-game/qa.json`，20 项通过，未解决项为 0。
- 全身预览：`assets/characters/full-game/preview-bodies-light.png`、`preview-bodies-dark.png`。
- 表情预览：`assets/characters/full-game/preview-expressions-light.png`、`preview-expressions-dark.png`。
- 来源原画与每图记录：`designs/characters/full-game/`，3 张新全身、4 张四表情母图，共 7 张；它们是保留供重建的配套设计来源，不作为透明运行素材使用。
- 实际提示词：`prompts/full-game/characters/`。
- 透明导出与切片脚本：`work/full-game-characters/export_characters.py`。来源登记脚本 `register_native.py`；对已实际查看且哈希不变的本批输出记验收用 `finalize_qa.py`。

## 身份与规格

| 身份 ID | 保持的身份 | 全身 | 表情头像 |
|---|---|---|---|
| `daotong` | 金色发带、短棕刺发、圆眼笑脸、玉绿米白袍、太极金葫芦 | 既有 `assets/characters/welcome-daotong.png`，1536×1536 RGBA | 4×512×512 RGBA |
| `healer` | 银发高髻与直发垂绺、金白花簪、玉珠耳饰、米白玉绿绣花医师裙、草药袋 | `assets/characters/full-game/fullbody-healer.png`，1536×1536 RGBA | 4×512×512 RGBA |
| `master` | 白眉白须、玉金冠横簪、玉绿金边道袍、太极腰饰、玉如意 | `assets/characters/full-game/fullbody-master.png`，1536×1536 RGBA | 4×512×512 RGBA |
| `swordswoman` | 黑发高马尾与细辫、金玉发冠红穗、玉耳坠、玉绿朱砂武服、背负鞘剑 | `assets/characters/full-game/fullbody-swordswoman.png`，1536×1536 RGBA | 4×512×512 RGBA |

表情文件命名为 `expression-{身份ID}-{happy|thinking|surprised|sad}.png`。四种表情有明确的眉眼、嘴型及思考手势变化，分别为开心、思考、惊讶、沮丧。它们是静态情绪头像，不冒称行走、骨骼或完整角色动作动画。原四张既有常态头像及旧角色 manifest 没有被覆盖。

## 原生尺寸与透明处理

7 张内置工具原生返回图均为 1254×1254 RGBA；提示词期望尺寸没有作为实际返回值宣称。三张新全身通过透明边缘技术处理、裁去无效透明边并居中补到 1536×1536，人物像素未放大。金带道童复用旧正式文件，未重复生成或另存同图 alias。

表情母图各有四个独立轮廓。部分发带、发尾或发髻跨过名义的 627 像素分格线，导出采用整张母图的 8 连通轮廓归属提取，再按各轮廓包围盒取图，不按 627 等分截断。母图内所有 Alpha 大于 128 的可见像素都归属对应角色；技术处理丢弃的 Alpha 大于 128 像素为 0。每角色四表情使用同一缩小比例，预乘 Alpha LANCZOS 下采样，置于 512 方形透明画布并保留约 32 像素以上安全边。来源框、比例和偏移逐项写入 `.generation.json`。

透明处理只移除低 Alpha 的外部孤立杂点、清空透明像素 RGB，并将接近不透明的 Alpha 250—254 归一为 255；没有重绘 RGB，没有以模糊或放大伪造细节。每项运行 PNG 具有真实 0—255 Alpha，画布外缘 Alpha 大于 8 的像素数为 0。

## 使用与验收

全身使用 uniform contain，脚底位置锚点按各素材实际包围盒底部登记在 manifest 的 `anchor`；头像为中心锚点 `[0.5,0.5]`，不使用九宫格拉伸。运行时可将全身等比缩小到界面角色槽，表情通常显示 128—256 像素，保留提供的 512 原导出供适配；不要拉伸脸部或将透明留白当作脚底。

已实际查看 7 张母图、4 张深浅底联系图、三张新全身的原尺寸深浅底合成，以及 512 像素表情边缘抽查；逐项核对身份、情绪、全身手足、发带/发簪/发尾完整性、脸部可读性、边缘、透明通道及来源哈希。深浅底都无明显红黄噪边，四种情绪在常用头像尺寸可区分。验收结果为 agent 美术检查通过；`userApproved` 保持 `false`，`clientIntegrated` 保持 `false`。

全部新原画通过宿主内置 `image_gen.imagegen` 生成。配置目标为 GPT Image 2.5 Sunburst / max；该入口未开放 model/quality 选择器，实际返回型号和质量都为未确认，各图记录为 null。不存在额外付费 API/CLI 调用。

## 重建

在项目根运行已配置的 Python 3.12：

```powershell
& 'D:\luyuan\image-skills\runtime\agent-sprite-forge\.venv\Scripts\python.exe' work/full-game-characters/export_characters.py
```

脚本只做既有原画的透明导出和切片，不调用生成服务。新输入或像素变化后须重新实际查看，不能直接复用旧人工视觉结论。当前来源与像素哈希已固定；根协调者负责全项目汇总与打包。

环境诊断的唯一 WARN 为 `python.path: other python.exe on PATH`，本次已显式使用隔离 Python 3.12 路径，因此不影响导出。可选付费提供商凭据和视频路线未配置，本角色包使用的宿主图片路线已实际成功，不涉及视频动画。
