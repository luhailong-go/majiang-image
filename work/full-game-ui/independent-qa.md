# Full-game v2 独立 QA

结论：通过，未通过项为空。

检查时间：2026-10-26T19:23:04.256107+00:00

UI25–UI32 共 8 个合同 ID、11 张独立整屏（UI27 三步、UI29 待领/已领两态）与 22 项新增透明组件完成独立检查。四张组件母版是来源，不冒算正式整屏；UI25/UI27 编辑来源保留作真实输入但不计交付。

## 文件与来源

逐图 PNG 可解码；文件与清单/sidecar 的 SHA-256、原生尺寸、实际提示词及其哈希、实际参考输入及其哈希全部一致。两张指定主参考均已记录为真实附图。工具未披露型号/质量，实际字段保持 null。

| ID | 正式图 | 原生尺寸 | SHA-256 前12位 |
|---|---|---|---|
| UI25 | [ui25-customization.png](D:/work/majiang-image/designs/ui/full-game/core/ui25-customization.png) | 1671×941 | `2982c6d00a73` |
| UI26 | [ui26-character-detail.png](D:/work/majiang-image/designs/ui/full-game/core/ui26-character-detail.png) | 1672×941 | `fcd5e35b6ccd` |
| UI27 | [ui27-tutorial-actions.png](D:/work/majiang-image/designs/ui/full-game/core/ui27-tutorial-actions.png) | 1672×941 | `0496da6f0b02` |
| UI27 | [ui27-tutorial-complete.png](D:/work/majiang-image/designs/ui/full-game/core/ui27-tutorial-complete.png) | 1672×941 | `2097991c272d` |
| UI27 | [ui27-tutorial-select.png](D:/work/majiang-image/designs/ui/full-game/core/ui27-tutorial-select.png) | 1672×941 | `b828e01215e3` |
| UI28 | [ui28-announcement.png](D:/work/majiang-image/designs/ui/full-game/modules/ui28-announcement.png) | 1672×941 | `42e0573f2fb4` |
| UI29 | [ui29-reward-pending.png](D:/work/majiang-image/designs/ui/full-game/modules/ui29-reward-pending.png) | 1672×941 | `94d689ce3de7` |
| UI29 | [ui29-reward-claimed.png](D:/work/majiang-image/designs/ui/full-game/modules/ui29-reward-claimed.png) | 1671×941 | `c0ab91828b53` |
| UI30 | [ui30-achievements.png](D:/work/majiang-image/designs/ui/full-game/modules/ui30-achievements.png) | 1672×941 | `cf70fe76c933` |
| UI31 | [ui31-ranking.png](D:/work/majiang-image/designs/ui/full-game/modules/ui31-ranking.png) | 1672×941 | `722ea9e2a034` |
| UI32 | [ui32-item-collection.png](D:/work/majiang-image/designs/ui/full-game/modules/ui32-item-collection.png) | 1672×941 | `d99ed4b89cc5` |

UI25 与 UI29 已领取图的原生尺寸为 1671×941，其余9张整屏为 1672×941。保留真实返回尺寸，没有重采样伪造一致尺寸。

## 实际视觉检查

全部 11 张整屏已用 view_image 实际打开。装扮的预览/当前使用/应用操作清楚；角色已使用按钮禁用；三步教程连续并说明规则由房间决定。公告、成就、排行与收藏具备可选模块/示例说明，中文可读、返回/关闭清楚。成就进度匹配数值，排行正红负绿，收藏详情对应选中物品。

奖励待领态只有待领标签和可用领取；已领态显示勾选、灰色禁用已领取及成功回执，没有待领残留或重复领取动作。两个状态使用不同真实图。

四张深浅底组件接触表已实际查看：22 项轮廓完整、无邻格残片、最小透明边距16像素，透明像素RGB为0。奖励/装扮/成就/排行/物品状态视觉可区分；成就框、聚焦框和光环中心透明。12状态族画布/中心锚点统一，全部等比缩放，无获准九宫格。四母版 Alpha≥128 的有效像素总数与各自切片完全一致。

## 映射复核

核心5图、模块6图清单均与最终文件一致；7组合、12状态族、23旧组件引用可解析，原有58张PNG哈希不变。领取动作的族名已准确指向旧 buttonFamilies.primary，并指定来源组合文件。

箭头尖端已按原生396×334修正为(350,313)，归一化约(0.883838,0.937126)，该点Alpha245。sidecar、manifest与composition一致。证据的最下强Alpha行范围按Alpha>128计为y315/x344–351；邻像素x343的Alpha恰为128，报告已明确此口径。

## 范围与证据

JSON报告保存逐图完整哈希、尺寸、提示词/参考检查、Alpha统计、切片来源、清单快照哈希、视觉观察及预览哈希。仅本报告与JSON由独立QA写入；页面、组件、旧README/index/exports没有修改。

本次不宣称客户端接入、规则引擎或真实浏览器交互完成；没有再次尝试浏览器file URL、服务器或其他绕行路径。

## 总域清单与主题绑定补检

总域页面清单与组件清单的 11/22/33 计数、8 个 ID、逐项文件/记录哈希、3 份 sourceManifests 哈希和子清单完整内容一致。总域状态在本次读取时仍为等待最终QA；只改变该状态不会影响已经验收的内容，JSON保存了排除status字段后的语义哈希。

`assets/ui/full-game/theme-bindings.json` 的三组桌面/牌背共6个真实图像路径均存在、可解码，SHA-256全部匹配。UI25中的概念名称明确映射到clientLabel：青玉云纹/青玉牌背、竹韵米白/竹韵牌背、月莲青蓝/月莲牌背。合同与绑定表均明确概念小样不是最终纹理的逐像素预览；客户端使用实际主题图，不从概念图裁切纹理。本次仅复核绑定，外部主题美术仍由对应域验收。

UI25当前使用区牌背标签已由“青玉云纹”修正为“太极青玉”，实际打开最终图确认与右侧选中牌背一致；桌布名仍为“青玉云纹”。新版原生1671×941，哈希2982c6d00a735205f5ac2c597215b485dccd906266ce75c1a79daadd723b02d3。旧图作为实际编辑输入保留，不计正式交付。同一搭配的预览/应用为幂等行为；其余10页与22组件的哈希全部冻结不变。
