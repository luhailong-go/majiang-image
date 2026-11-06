# 2026-10-28 角色、场景与效果的接入覆盖审计

结论：本域没有需要新增整套角色、场景或特效原画的 P0 缺口。4 全身、16 表情、3 纯背景、3 空桌面、6 条效果与8个中文提示均有正式资源及通过记录。原先的页数与状态映射不足以证明运行组合完成；以下有限 P1 应以组合、准确绑定和更新后的实际预览闭合。本次只新增映射数据及审计文字，没有生成、修改或删除旧 PNG，也没有改旧 ZIP、Git 或启动浏览器。

## 可复用证据

| 域 | 实际资源与证据 | 本轮判断 |
|---|---|---|
| 四人 | `assets/characters/full-game/manifest.json`、`qa.json`：4 full_body、16 expression_avatar；旧 `assets/characters/manifest.json` 另有4常态头像 | 已实看全身浅底、16表情深浅底联系图；身份、情绪、轮廓成立。道童全身直接引用旧正式路径，不双算。其余身体1536方形画布是透明补边，人物未放大。 |
| 三背景 | `assets/scenes/full-game/{courtyard-day,waterside-night,tea-room}.png` 与同域 manifest | 三张都实际查看；无人物、界面或牌，风格一致，中前景可叠角色/面板。不是可行走地图，不缺导航/碰撞美术。 |
| 三桌面 | 上述域 `table-moon-lotus.png`、`table-ivory-bamboo.png` 与旧 `assets/ui/gameplay/table-background.png` | 三张都实际查看；动态牌区为空，不需重新抹字。各桌是含环境的静态完整底图；等比显示，最终四座/牌墙/手牌布局仍需按实际组合验收。 |
| 六效果 | `assets/fx/full-game/manifest.json`、`timelines.json`、`animation-clips.json`、`final-validation.json` | 24个独立阶段帧，6 clips，已实看当前深浅联系图。每类统一512画布和中心注册；时长400/333/667循环/533/667/600ms。既有图集回读、Alpha和帧差异通过记录可复用；本轮未重跑播放或批处理。 |
| 文字及结算 | `assets/fx/full-game/callouts/{chi,peng,gang,hu,ting,self-draw,draw,victory}.png`、`callout-base.png`、`settlement-{defeat,draw}.png` | 已实看，8字形正确。失败/平局装饰有意无字，需配准确原生结果标题；无字装饰本身不能证明结果状态可辨。 |
| 听牌与网络 | `assets/ui/component-compositions.json` 的 `readyHand/loadingOverlay/offline/autoplay`；已有 tooltip-bubble、loading-ring、modal-shade、offline-badge、autoplay-badge | 所需绘画底材已经存在，已实际看关键切片。听牌持续面板与短暂“听”提示不同；离线与托管不同，不能互相替代。 |
| 六空态 | `assets/ui/production-v3/empty/manifest.json` 及 `preview-light.png`、`preview-dark.png` | 六张联系图元素均实际看过；邮件、好友、搜索、战绩、断连、超时语义可辨，未见明显烘焙底、截边或噪边阻塞。另实看断连单图。独立视觉通过，不冒称本轮重跑逐像素Alpha检查。 |

本次新增 `assets/presentation/production-v3/character-bindings.json`、`effects-bindings.json`、`theme-bindings.json`：登记78个去重直接PNG引用及相应record、来源manifest、预期SHA、真实已登记尺寸、锚点/伸缩方式、用途、事件与帧时序。直接PNG/record路径存在，JSON可解析；未在本机重型作业独占暂停期间另开PNG批量哈希、渲染或客户端测试。最终像素freshness由根统一验证。

## 有限 P1 与当前修正状态

1. **角色详情标签与正式表情不一致。** 旧 `designs/ui/full-game/core/ui26-character-detail.png` 烘焙“微笑/喝彩/思考/问候”，与正式 `happy/thinking/surprised/sad` 不同。新 `production/previews/pages/UI26.png` 已实际查看，正确使用“开心/思考/惊讶/沮丧”，当前道童实例视觉通过。四身份全身、简介、表情序列由新 character-bindings 提供统一映射；根随后已将 layouts 的 UI26 全身/姓名/简介/4表情接为 `charactersById[selectedCharacterId].fullBody/displayName/description/expressions`，并声明 templateDataContract 与 sampleSelectedCharacterId=daotong；本审计已定点实读确认。当前实际预览是已通过的道童模板实例，其他身份预览/真实客户端切换仍待接入验收，不把源绑定存在宣称为客户端已实现。
2. **四家结算分数绑定同一字段。** 首读 `production/states.json` 的 play.loss/match.loss/play.draw/play.self_draw 均四次复用 `result.score`。已反馈，根修为 `result.players[0..3].score/name/portrait`；已定点实读确认源修正。结果标题、胜/败/流局装饰与分数需互斥，零分不是流局判定依据；新 effects-bindings 明确此合同。新增 play.loss/match.loss 等状态已在86项源数据内，更新后的预览仍待根重新生成/实看。
3. **重连圈遮挡状态文字。** 实看旧 `production/previews/states/system.reconnecting.png`，金色加载圈压住“正在尝试恢复连接”。根已把源唯一spinner移到 `[745,195,110,110]`，system.loading 也只保留一圈；已定点实读确认。旧预览不能标为修后通过，等待重新渲染复验。
4. **流局缺明确文字。** 实看旧 `production/previews/states/play.draw.png`，四家0分和空白装饰无法区分流局与普通零分。根已将源标题改“流局结算”并加现有 `callouts/draw.png`；已定点实读确认。更新后的预览仍待重新生成/实看，不需新生图。

以上源修正写入 `assets/presentation/production-v3/qa.json` 的 `resolved_in_source_pending_preview`，保留旧缺陷证据，未混同源修正与最终图验收。

## 接入边界

角色名是外观身份，四座昵称、头像选择与得分来自每个玩家，不固定等同“青云/桂枝/松隐/墨翎”等概念样例。UI26用已确认4表情，不扩增角色或情绪。失败不自动等同负分、全零不自动等同流局，判断由实际规则给出。三桌面参考多边形仅帮助排布，不充当命中区域或最终客户端合同；theme-bindings把原 `[left,top,right,bottom]` 安全区明确转换为 `[x,y,width,height]`，避免误用。

六条效果保持真实不同阶段绘画，33ms crossfade/结束淡出只是可选运行补间，不冒称新绘连续动画。无需视频、战斗动作、新收费系统或更多角色即可闭合通用四人横屏麻将本域美术。当前审计和映射不证明真实客户端、浏览器交互、设备导入、音效同步或上传完成。

## 待资源时段归还后的定点复看

根另报告已修房主/成员本地身份、全部准备才允许开始、解散结束不再等待、匹配中禁入桌/成功启用/取消可重匹配、离线与托管可并存。此轮仅登记这些组的定点预览复看，不复跑历史全部素材，不把根报告的源修正写为本工已独立看过新图。具体状态组及本工实际核实的源修正列于 presentation/qa.json。三份绑定与本审计到此冻结；新组合图、最终freshness和客户端验证由根继续闭合。

## 最终独立复验闭合

本工已实际查看17张最终受影响状态单图与4张角色详情变体；最后重开的play.loss、match.loss、system.loading分别明确本地未获胜结果/姓名及禁用等待加载。此前的四家绑定、重连遮字、流局缺字、四身份详情，以及末轮发现的loss身份结果与加载入口状态均闭合；旧缺陷依据保留在presentation/qa.json的resolvedFindings。根另已通过全32页/86状态及其来源收据，入口production/final-visual-qa.json；本工未独立实看其余最终单图，不冒称全套独立视觉检查。当前本域艺术合同status=passed，无待重渲染项，browser/client仍false。effects-bindings补明result.localPlayerName/localPlayerIndex/localOutcome，三份映射与QA再次冻结。


## 最终闭合（2026-10-28）

本域旧记录中的待重渲染项目已闭合。独立复核另指出失败结算缺少本地结果文字、加载中进入按钮仍启用；根已实际修复并重新导出。最终由根实看四角色完整详情、流局/自摸/失败结算、加载与全套页面/状态联系图，并通过来源核验。真实独立观察与根接手终验分别记录于本域qa.json；不把根实看冒称子工独立实看。最终状态为passed，当前收据见production/final-visual-qa.json，完整文件核验见exports/production-v3-validation.json。浏览器/客户端实测仍未进行。上文待验措辞是审计经过，当前结论以本节和最终QA为准。
