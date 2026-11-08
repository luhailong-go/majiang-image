# 运行表单控件补件

本域交付 10 个透明 PNG，均由两张 1254×1254 原生母图裁切、技术 Alpha 清理和透明补边得到，运行切片没有放大或重绘。配置目标 GPT Image 2.5 Sunburst / max；内置工具没有型号、质量选择器或可核实返回元数据，因此实际 model/quality 均为 null。逐图来源、真实裁切框和处理步骤见同名 `.generation.json`。

- [manifest.json](manifest.json)：10 个正式皮肤、尺寸、锚点、伸缩合同、来源和 QA。
- [compositions.json](compositions.json)：复用旧常态、输入叠层、进度、开关、音量条的精确坐标和状态逻辑。
- [qa.json](qa.json)：透明检测、深浅底实看及哈希。
- 原生母图及最终联系图位于 `designs/ui/production-v3/forms/`。

## 必须遵守的组合规则

所有尺寸先按目标分辨率统一等比缩放。输入边框、列表边框、进度轨道与填充只允许随后横向九宫格伸缩；高度锁定，侧边云纹保形。开关轨道和圆滑块只允许等比缩放。PNG 内透明补边属于画布的一部分，不能每状态自动紧裁导致锚点跳动。

输入使用已有 `input-field` 米白承载面，焦点或错误皮肤仅叠边，中心保持透明；错误状态覆盖焦点。六位房号继续使用已有 `keypad-key` 与原生数字，给整个输入组用新描边或给单格用原生焦点线；不能把横向描边压成方格。

列表常态继续使用 `content-card`；新 selected/pressed 底板以同一布局矩形替换背景，文字、未读圆点、日期与分数单独绘制。原始常态卡片需要九宫格组合到目标矩形，不能直接压扁。

进度和滑条先将独立填充的 `fillAssetCrop` 画入合同 `contentRect`，再按 0—1 左侧裁剪；0 时隐藏填充，1 时完整显示，不用整张按钮作为填充。百分比是原生文字。

开关轨道不烘焙滑块，开关状态使用同一画布和独立圆珠。禁用态采用 opacity 0.48 与 interactive=false；没有另存重复禁用 PNG。滑条继续复用旧 `slider-track` 与 `slider-thumb`，只增加专用 `slider-fill`。

联系图中的中文由 Windows 微软雅黑绘制，仅作本地验收；项目未打包该字体，也不代表已经决定客户端字体或取得其再分发许可。所有业务文字与客户端交互仍由接入方实现，`clientIntegrated=false`、`userApproved=false`。

## 重建

需要 Pillow、NumPy、SciPy 的 Python 环境。运行 `work/production-v3/forms/export_forms.py` 只会重建本域 10 个切片、两张联系图及待验收记录；实际查看新输出后运行 `work/production-v3/forms/finalize_qa.py` 正式化检查。原生母图、提示词与所有来源记录保留；没有收录中间检查 PNG。
