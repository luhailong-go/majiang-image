from pathlib import Path
import json
R=Path(r"D:\work\majiang-image")
notes={
"UI01":"牌局加载、68%与加载状态清楚，场景和道童统一，无正式商标。",
"UI02":"进入/账号/帮助及协议勾选清楚，协议文案标明待配置，作为根入口按平台退出。",
"UI03":"主三入口以及个人资料、好友、邮件、战绩、规则帮助、设置齐全，未读点可辨。",
"UI09":"四座手牌/弃牌/副露与牌墙、风位、轮次、余牌、倒计时、庄家与设置/聊天齐全；本人13张加独立摸牌。",
"UI10":"碰杠胡过、多候选、选中牌、听牌提示、当前玩家、离线/托管状态清楚；文案说明为操作示意，实际条件由规则配置。",
"UI12":"四家累计积分与共8局、返回大厅/再来一局明确，积分样例且合计0。",
"UI14":"四个不同脸型发型/年龄/身份头像一致，选择/已选中及确认/返回/关闭清楚。",
"UI16":"快捷语/表情页签、4条快捷语与4个表情、发送/关闭/语音/静音清楚，叠加牌桌背景符合面板用途。"}
for p in (R/"designs/ui/full-suite/core").glob("*.generation.json"):
 d=json.loads(p.read_text(encoding="utf-8-sig"));i=d.get("uiId")
 if i not in notes:continue
 d["inspection"].update({"visualStatus":"passed","visualInspectionCompleted":True,"visualNotes":notes[i],"blockingIssues":[],"nativeDimensionsChecked":True})
 d["status"].update({"productionAccepted":True,"userApproved":False,"clientIntegrated":False})
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Core QA recorded; UI11 left to correction worker.")

