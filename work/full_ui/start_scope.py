from pathlib import Path
import json
root=Path(r"D:\work\majiang-image")
brief=root/"docs/PRODUCTION_BRIEF.md"
text=brief.read_text(encoding="utf-8")
text=text.replace("# 首批制作说明","# 制作说明：完整麻将 UI")
text=text.replace("先完成以上两张并视觉检查，保存逐图记录、提示词和 README 索引。将首批预览交给用户反馈；不擅自扩大为全套角色动画、所有玩法皮肤或客户端接入。","以上两张首稿已完成。2026-10-26 用户将范围明确扩展为“你把游戏的所有UI做完给我”，现在按 docs/FULL_UI_SCOPE.md 的完整页面与状态合同持续生产。旧的首批两张后停止边界已被此授权替代；独立整屏、对应弹窗/状态、透明组件、牌面、可浏览本地索引和交付清单/包纳入本轮。真实客户端/服务端接入仍分别标记，不以美术稿冒充已接入。")
text=text.replace("这些不阻塞首批美术方向稿。","这些不阻塞完整 UI 的通用美术生产。默认按16:9横屏、好友房与休闲匹配继续；未确认的地方玩法和正式游戏名保持未指定。")
text += "\n## 完整 UI 生产启动\n\n2026-10-26 已依用户扩展要求启动并行生产。范围合同由协调聊天编写到 docs/FULL_UI_SCOPE.md，本制作聊天不并发覆盖。当前分工为对局核心与交付整合、房间/匹配、系统/社交/记录、角色透明修整；各域使用互斥目录与逐图记录。\n"
brief.write_text(text,encoding="utf-8")
readme=root/"README.md"
text=readme.read_text(encoding="utf-8")
text=text.replace("[首批制作说明](docs/PRODUCTION_BRIEF.md)","[制作说明](docs/PRODUCTION_BRIEF.md)")
text=text.replace("## 当前状态\n","## 当前状态\n\n2026-10-26 用户已扩展为完整麻将 UI 美术交付，当前进入全套页面、状态、透明组件与牌面生产。完整页面合同将由协调聊天保存到 docs/FULL_UI_SCOPE.md，后续进度按合同逐项核对；本聊天负责制作与本地打包。\n")
readme.write_text(text,encoding="utf-8")
print("Expanded scope recorded without touching FULL_UI_SCOPE.md.")

