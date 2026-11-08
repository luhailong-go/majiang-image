# 云间雀社 · 道家Q版麻将美术

通用四人横屏麻将的完整美术和接入参考，覆盖休闲匹配、好友房、四人牌桌、结算、四位角色和UI01—UI32既有模块。沿用指定邮件/组队原图的玉绿、象牙米白、暖金手绘风格。游戏名为《云间雀社》，副标“麻将”；地方番型和商业付费未指定，不自行添加。


## 游戏名称与Logo

本次按用户委托选名为**《云间雀社》**，副标“麻将”。“云间”承接仙山道观、云纹玉色，“雀社”对应四人麻将与好友聚桌。

- [透明Logo原图](assets/branding/yunjian-queshe/logo-primary.png)：原生1536×1024 RGBA，保持内置生成返回像素。
- [深浅底实际检查图](assets/branding/yunjian-queshe/preview-light-dark.png) · [逐图记录](assets/branding/yunjian-queshe/logo-primary.png.generation.json) · [Logo清单与QA](assets/branding/yunjian-queshe/manifest.json)
- [品牌配置](config/brand.json) · [包含Logo的当前美术总清单](exports/game-art-with-brand-manifest.json)：原292项基础美术加1项品牌Logo，共293项正式主PNG。检查图不混算新原画。

v4统一包包含全部293项正式美术、品牌Logo、32页86状态组成树及接入资料。登录/加载组合已使用Logo，大厅使用品牌名称。旧概念整屏保留为设计依据；当前运行排布以production/为准。Logo按等比使用，不作九宫格。

## 使用入口

- [全部美术画廊](index.html)：概念整屏、运行切片、角色、牌面、场景、道具与特效。
- [独立素材组合参考](production/index.html)：32页面、86状态；按钮、文字、角色与牌面分层，支持四角色详情和桌面纹理选择。
- [下载公开仓库全部文件](https://github.com/luhailong-go/majiang-image/archive/refs/heads/main.zip) · [公开仓库](https://github.com/luhailong-go/majiang-image)
- [当前总清单](exports/game-art-with-brand-manifest.json) · [当前文件与来源验收](exports/release-v4-validation.json) · [最终交付说明](docs/ART_RELEASE_V4.md)

clone或解压后直接打开根index.html。素材用普通Git保存，无LFS指针；无需配置图片API账号。

## 实际交付

| 类别 | 内容 |
|---|---|
| 正式主PNG | **293项**，包括品牌Logo；既有293项原生素材像素均保持 |
| 概念整屏 | 38张，覆盖32个原UI合同ID，独立于运行素材组合参考 |
| UI独立控件 | **102项**；原80项加6空态、10表单皮肤、6对局状态皮肤 |
| 人物 | 4位全身、4座头像、16独立表情；开心/思考/惊讶/沮丧统一绑定 |
| 牌面和牌具 | 34标准面、8可选花牌、牌胚/牌背/高亮，34项牌具/交流/物品图标 |
| 场景与装扮 | 3张纯背景、3套空桌主题；两套新增牌背、标题/加载装饰与应用图标变体 |
| 特效 | 35正式PNG，6条播放时序、24真实阶段帧、独立中文提示与结算装饰 |
| 接入组成树 | **32页面、86状态**；逐层坐标、独立图片路径、文字/数据绑定、九宫格和交互状态 |
| 对局组合 | 四座手牌/暗手/两层牌墙/弃牌、16种方向副露示例、多候选/听牌/非法牌/最后弃牌、动态标识与结算 |
| 组合检查图 | 118张根页面/状态组合图，另有各域深浅底与专项检查图；均为派生检查图，不混算新增原画 |

新增四张原生母图切出22项必要运行素材。表单补齐focus/error、list selected/pressed、独立progress、toggle与slider fill；对局补齐候选容器、听牌提示、选中外框、不可出牌/最后弃牌/听牌底章。禁用、数字、昵称、分数、倒计时和进度仍由原生UI层表达，不从整屏抠文字或示例牌。

## 接入与证据

[production/layouts.json](production/layouts.json)和[production/states.json](production/states.json)是可读组成树，设计画布1600×900；PNG组合预览为1280×720的机械缩小检查图，不冒称新原生分辨率。每个界面列出独立资源、坐标、配置文本和状态素材。样例四家分数分别绑定result.players[0..3]，角色以selectedCharacterId绑定，领取前后互斥，听牌/动作由合法候选控制。

只对manifest允许的素材作九宫格；新增输入描边/列表只横向，开关/滑块/人物/牌面与珠饰等比。所有新运行切片有真实Alpha和逐图记录。来源、实际提示词与真实参考保留，目标GPT Image2.5 Sunburst/max；内置工具没有可核实实际型号/质量返回，因此实际字段保持null。

本包交付整款已定范围的美术和接入资料。真实客户端/服务端、平台账号、规则和目标设备须由游戏工程另行验收。图片实看、组合图及静态脚本检查均有记录；本地file浏览被工具策略拒绝后没有绕行，未声称真实浏览器或游戏客户端实测。

## 文档与后续

[完整接入说明](docs/FULL_GAME_INTEGRATION.md) · [新增表单组合](assets/ui/production-v3/forms/compositions.json) · [牌桌运行组合](assets/ui/production-v3/gameplay/runtime-compositions.json) · [人物/效果/主题绑定](assets/presentation/production-v3/)

本地目录为D:\work\majiang-image；新参考放references/incoming/。本地最新离线ZIP为exports/yunjian-queshe-complete-art-v4.zip，不重复提交大ZIP到Git；GitHub的Download ZIP可下载全部发布文件。旧v1/v2/v3报告是各自交付时的历史证据；当前检查以release-v4报告为准。

用户已授权公开仓库luhailong-go/majiang-image，main只维护一个无父提交；当前发布按[公开规则](docs/PUBLIC_REPOSITORY.md)进行。开始新图前读[AGENTS.md](AGENTS.md)、配置和逐图记录规则。
