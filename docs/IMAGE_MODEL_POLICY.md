# 图像入口与逐图记录

型号、质量目标只在 [统一配置](../config/image-generation.json) 维护。用户本次明确指定 GPT Image 2.5；配置沿用原 image 项目高质量目标，2026-10-26 已核对官方 Sunburst 模型和 image-prompting 文档，支持 max。不得将配置目标当成本次工具实际返回版本。

优先使用内置 image_gen。若宿主有 model/quality 参数，则显式传入配置；当前内置 schema 无此选择器时继续宿主管理路径，submittedParameters.model 和 quality 均记 null。提示词不能锁定 API 分支。只有真实结果、receipt 或可信来源元数据可以填 actualModel/actualQuality；未披露写 null，并说明“宿主管理，工具未披露可核实版本/质量”。API/CLI 为用户明确选择的备用路线，当前未授权新增单独计费调用。

每张新生成、AI 编辑或重试图在旁边保存 `<图片文件名>.generation.json`，至少包括：

- file、sha256、generatedAt（含时区）、真实 width/height/format。
- tool、route、调用或结果 ID（若提供）。
- configSnapshot：当次 model、quality、builtin_product、verified_on、sources；用户覆盖另记。
- submittedParameters：真实提交的 model/quality，没有选择器为 null。
- actualModel、actualQuality、evidence、unverifiedReason。
- prompt：实际提示词文件；references：实际传入图片与用途。
- 检查状态和具体未通过项。候选与成品状态分开，不把未检查的图登记为已验收。

裁切、缩放、拼接等派生素材记录 derivedFrom（原图、SHA-256、生成记录）和 operation；分别记录原生及导出尺寸。参考图仅复制不视作新生成，不用当前配置回填历史版本。

在项目 README 登记每张成图和记录索引。完成前确认图片已经落盘到本项目，不只留在宿主默认生成目录；核对透明 Alpha、中文可读性、构图、道家 Q 版一致性。交付包只收录真实已通过的资源及必要记录。
