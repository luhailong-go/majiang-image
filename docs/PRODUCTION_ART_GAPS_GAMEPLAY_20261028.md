# 2026-10-28 对局运行美术审计

以下先保存生产前审计快照，当前闭合结果见末节。本次只读检查旧资源；范围为通用四人横屏麻将，不新增地方规则。实际打开 UI09、UI10、UI23 控件板/流局页、UI24 异常板，以及牌朝向/深浅底检查图、风位盘、离线/托管徽章、结算卡与独立牌桌背景。整屏图只作为设计依据，不算运行切片。

## 现存素材可导入结论

逐文件解码并核对清单 SHA-256 与尺寸：34 标准牌、8 可选花牌、13 对局组件、45 通用组件均存在且与清单相符。标准/花牌全为 448×640 RGBA；对局组件为 12 RGBA 加 1 独立 RGB 背景。通用遮罩 modal-shade 是有意的恒定 Alpha 填充，不要求同时含 0/255。其他本次核对的 RGBA 均有透明与不透明像素。旧图未修改。

| 需求 | 可复用的独立资源/合同 | 当前边界 |
|---|---|---|
| 34 标准牌 | assets/tiles/manifest.json 的 wan-1..9、tong-1..9、tiao-1..9、wind-east/south/west/north、dragon-red/green/white | 牌字与数量已有通过记录，不需要重生 34×4 图 |
| 8 花牌 | assets/tiles/flowers/manifest.json 的 flower-plum/orchid/bamboo/chrysanthemum/spring/summer/autumn/winter | optional=true；存在素材不代表开启花牌规则 |
| 全座朝向/不可打 | stateAndOrientationMap；tile-back.png、tile-highlight.png | 自家0°/左90°/对家180°/右270°，整体旋转不镜像；已有灰化与上抬方案 |
| 头像/当前玩家 | avatar-frame、current-player-ring，四个独立头像 | 皮肤可用；还需四座位置与层次组合 |
| 托管/离线 | autoplay-badge、offline-badge | 两个不同文件与图案，可分别叠加原生中文，不能互相代替 |
| 风位/庄家/计时 | wind-round-dial、dealer-badge、countdown-frame | 无字本体独立；component-compositions.json 已有锚点和动态数字约定 |
| 操作按钮 | action-button-normal/pressed/selected/disabled | 四状态独立；碰/杠/胡/过为原生文字；合法性由服务器提供 |
| 候选/听牌基础容器 | content-card、tab-selected、tooltip-bubble + 标准牌 | 已有简短组合声明，但缺完整尺寸、牌位、选择/禁用/空候选构成 |
| 结算 | settlement-card、window-frame、content-card、avatar-frame、主次按钮；FX 中 callouts/draw、victory、settlement-draw/defeat | 可组合独立行/卡与文字，整屏 UI11/12/23 不能算运行窗口 |
| 牌桌 | table-background；table-moon-lotus、table-ivory-bamboo | 独立背景没有烘焙手牌、字或按钮，可直接复用 |

## 有限 P0

1. **四座牌组缺完整组合合同与实看检查图。** 现有说明只给角度和建议大小，没有暗手/双层牌墙的重复向量、遮挡顺序、弃牌网格，以及副露中来源座位横置牌、加杠堆叠、暗杠隐藏的参数。解决方式是现有牌材的等比缩放与整体旋转组合，不生成或冒算 168 张新牌画。UI09 的立体窄边墙效果只存在概念图；本轮采用明确的平面四座组合合同，不从概念图抠窄边、不伪称提供新立体牌模型。
2. **多候选/听牌/非法牌/当前弃牌缺可核验的状态组成。** 需要独立框皮肤或明确复用、文字/牌槽/计数区、空候选、唯一选中、确认前后、非法不可交互与最后弃牌指向。现有灰化和高亮可复用；候选内容与剩余数量只能绑定数据，不把样例当合法牌判断。
3. **牌桌动态标识与结算缺统一运行层树。** 风位当前是东左/南上/西右/北下的样例锚点，尚缺 seatWind 重绑定；庄家、当前玩家、计时、离线/托管与结算也没有一个统一的四座/动态文字/遮挡合同。皮肤齐全，补 JSON 和组合验证即可，不要求新生风位/徽章/按钮/结算图。

## 精确新增范围

生产目录限定 assets/ui/production-v3/gameplay，源设计/提示词/检查工具使用对应 production-v3/gameplay 域；旧图与旧清单不改。

- 1 张原生无字透明图集，至多 6 个必要皮肤：candidate-panel、ready-hand-panel、candidate-selected-outline、illegal-tile-badge、discard-pointer、ready-hand-badge。不绘制牌字、金额或玩法文字。
- runtime-compositions.json：四座坐标/全牌同转、牌墙双层、弃牌网格、碰/明杠/加杠/暗杠布局（仅渲染模式）、听牌/候选/非法牌、四座状态与结算组合。
- manifest.json、qa.json、逐 PNG 来源记录；新图集切片记录实际 crop/导出尺寸，不放大、不冒称各张独立生图。
- 只用独立正式素材的四座牌桌、牌组/副露、状态候选、结算与深浅底检查图，实看后再置通过。

关闭判据：每个上述运行场景都能解析到现存文件及参数，中文/牌字朝向与层次可辨，禁用无点击，原输入哈希不变。客户端/服务端接入与实际规则合法性仍另行验收；本报告不以静态图证明它们已实现。

## 本域产物与最终闭合

已实际通过内置 image_gen 生成 1 张原生 1254×1254 RGBA 六皮肤图集，真实附入两张指定风格参考。工具没有公开型号/质量返回证据，实际字段为 null，配置目标仍为 GPT Image 2.5 Sunburst/max。来源和逐图记录均已落盘。

独立正式切片为 candidate-panel 756×323、ready-hand-panel 511×310、candidate-selected-outline 703×341、illegal-tile-badge 288×284、discard-pointer 242×265、ready-hand-badge 274×270。全部是实际原生裁切加 16px 透明边距，没有放大；不是六次独立模型生成。六项已实际在深浅底和常用尺寸检查，空心候选框中心透明、轮廓完整，均通过本域制作视觉检查。

入口为 `assets/ui/production-v3/gameplay/index.html`；清单、完整运行组合合同和 QA 分别为同目录 manifest.json、runtime-compositions.json、qa.json。113 个独立引用在组成合同构建时读取并记录哈希。四座/副露/候选状态/结算/深浅底共 5 张组合预览位于 `designs/ui/production-v3/gameplay/`，它们不是新增运行原画。

最终状态为 passed：用户明确授权单线程美术收尾后，根协调者仅定点刷新四座桌图，未改其他四张预览。HUD 标签位于中央左侧 x695、最大宽 140，制作人与根协调者均实际查看当前原图，确认不遮挡左右弃牌、中央计时与牌字，中文完整。新图 SHA-256 为 9521bec298989a9d3b34d179636490d096228cc18b9945f132caf09b1613c049。旧 HUD 位置缺陷作为 resolved 保留在 QA；blockingFindings 与 pendingChecks 为空。六张正式皮肤与五张组合预览已冻结；本工未运行全域脚本或重新生图，最终全局依赖检查由协调者整合执行，客户端/服务端接入仍另行验收。
