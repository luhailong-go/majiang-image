# 全游戏补充 UI 美术 v2

8个页面ID，11张独立整屏，22项透明组件。无旧包覆盖、无上传。

| ID | 图稿 | 原生尺寸 |
|---|---|---|
| UI25 | [装扮设置](core/ui25-customization.png) | 1671×941 |
| UI26 | [角色详情](core/ui26-character-detail.png) | 1672×941 |
| UI27 | [新手引导第2步：操作提示](core/ui27-tutorial-actions.png) | 1672×941 |
| UI27 | [新手引导第3步：完成](core/ui27-tutorial-complete.png) | 1672×941 |
| UI27 | [新手引导第1步：选牌](core/ui27-tutorial-select.png) | 1672×941 |
| UI28 | [公告详情](modules/ui28-announcement.png) | 1672×941 |
| UI29 | [奖励领取 · 待领取](modules/ui29-reward-pending.png) | 1672×941 |
| UI29 | [奖励领取 · 已领取](modules/ui29-reward-claimed.png) | 1671×941 |
| UI30 | [成就收藏](modules/ui30-achievements.png) | 1672×941 |
| UI31 | [排行榜](modules/ui31-ranking.png) | 1672×941 |
| UI32 | [物品收藏](modules/ui32-item-collection.png) | 1672×941 |

完整索引见 `manifest.json`。逐图同名 `.generation.json` 含实际提示词、参考、原生尺寸与检查。

UI25原始装扮图及UI27原始选牌图仅为AI编辑来源，不计交付。角落清理失败尝试已被最终页脚版本替代，保留文字记录而不重复保留无用像素。

UI25为先行布局示例；实际主题名与素材见 `assets/ui/full-game/theme-bindings.json`，客户端须用该映射中的真实桌面/牌背生成预览，不裁切概念稿小样。

接入说明：`docs/UI_FULL_GAME.md`。全游戏其他美术域及v2总包由主任务另行整合。
