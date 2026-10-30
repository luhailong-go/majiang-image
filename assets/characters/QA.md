# 角色素材检查

2026-10-26，America/New_York。角色域全部 5 个交付文件通过本地制作检查；用户定稿与客户端集成尚未发生。

## 交付

| 文件 | 用途 | 真实尺寸与来源 |
|---|---|---|
| welcome-daotong.png | 迎宾道童透明全身 | 1536×1536 RGBA；1254×1254 AI 原图的内容不缩放，清理 Alpha 后加透明留白 |
| avatar-daotong.png | 金带道童头像 | 512×512 RGB；627×627 母版象限降采样 |
| avatar-healer.png | 银发医师头像 | 同上 |
| avatar-master.png | 白眉老道头像 | 同上 |
| avatar-swordswoman.png | 黑发侠女头像 | 同上 |

## 已完成检查

- 全身保留短棕刺发、金发带、圆眼笑脸、玉绿金边与米白衣裤、红色“中”牌、太极金葫芦；双手双脚完整。
- 实际使用 RGBA Alpha 合成深玉绿与浅米白背景，并用 view_image 分别检查。轮廓干净，无可见红黄散点，无棋盘格烘焙，无底板与地面投影。
- 透明区 1,568,729 像素，完全不透明区 759,405 像素；Alpha 范围 0—255。四角全透明。主体边界 [199,157,1336,1379]，四边留白均大于 8%。
- 机械导出清理 Alpha≤8 像素和 31 个不连通残点；未移除任何 Alpha>128 的主体像素。Alpha≥250 规范化为 255，透明像素 RGB 清零，避免纹理采样污染。保留中间 Alpha 的自然轮廓抗锯齿。
- 四头像逐张查看；性别、年龄、脸型、头发及服装区别明确，保持同套画法。头像为不透明方形肖像，局部发带/马尾与肩膀到达画框属头像裁切，不属于全身裁切错误。
- PNG 完整性、文件 SHA-256、派生来源哈希与记录路径均核验通过。

## 来源与限制

AI 透明修订源与头像母版保留在 designs/characters/production，提示词位于 prompts/characters。两张母版都实际附上角色首稿、邮件 UI、组队 UI、道童横幅四张参考；实际调用仅使用内置 image_gen。

welcome-daotong-production-v2.png 仅为清理前生成来源，状态为 raw_source_not_delivery_alpha_cleanup_failed，不作为透明成品验收。唯一正式全身交付是 assets/characters/welcome-daotong.png；本报告的深浅底检查均从此最终导出文件的像素合成。

配置目标 GPT Image 2.5 Sunburst/max。工具只披露图片与保存路径，实际 model/quality 均为 null。全身导出的 1536 画布不是新增原生绘画分辨率；四头像是同一母版的派生切图，不冒称四次独立生成。

技术导出脚本：work/characters/export_characters.py；QA 收尾脚本：work/characters/finalize_character_qa.py。深浅底工作检查图位于 work/characters/welcome-daotong-light-qa.png 与 welcome-daotong-dark-qa.png。

## 接入约定

全身等比 contain，锚点 [0.5,1]；透明边距已包含，禁止九宫格拉伸。头像等比 cover，锚点 [0.5,0.5]，由客户端裁圆或圆角；统一头像框与庄家/当前玩家状态由 UI 组件覆盖，不能烧入头像。推荐 UI 使用尺寸不超过 512 像素。每项完整来源与导出操作见同名 .png.generation.json；汇总入口 manifest.json。
