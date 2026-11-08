from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import json,hashlib
root=Path(r"D:\work\majiang-image")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((root/"work/rooms/finalize-input.json").read_text(encoding="utf-8-sig"))
draw={"id":"UI23","variant":"draw","slug":"ui23-draw-result","title":"流局结算状态","file":"designs/ui/full-suite/rooms/ui23-draw-result.png","prompt":"prompts/rooms/ui23-draw-result.prompt.txt","type":"independent_state_screen","checks":["实际查看恢复的完整1672×941原生图：本局流局、本局无人成胡中文清楚","四名身份不同头像与四行本局积分0齐全，未出现胜者或正负积分","继续下一局为玉绿主操作，返回大厅为米白次操作，关闭X与局次清楚","不把零分演示态当地方规则；未设置真实计分合同","生成回执的revisedPrompt与保存提示词完全一致，四个输入参考及哈希核验通过"]}
if not any(x["file"]==draw["file"] for x in data["finals"]):data["finals"].append(draw)
now=datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec="seconds")
pages=[]; validation=[]
for entry in data["finals"]:
 p=root/entry["file"]; rp=Path(str(p)+".generation.json")
 rec=json.loads(rp.read_text(encoding="utf-8-sig"))
 assert sha(p)==rec["sha256"],entry["file"]
 assert sha(root/rec["prompt"])==rec["promptSha256"]
 for ref in rec["references"]:
  assert sha(root/ref["file"])==ref["sha256"],ref["file"]
 with Image.open(p) as im:im.verify()
 review="recovered_generated_output_visually_checked_and_completion_event_verified" if entry.get("variant")=="draw" else "prior_worker_visual_checks_reused_at_unchanged_sha256_and_parent_independent_review"
 rec["inspection"].update({"visualInspectionCompleted":True,"visualStatus":"passed","checkedAt":now,"checks":entry["checks"],"reviewEvidence":review,"unresolvedIssues":[]})
 rec["status"].update({"readyForUserReview":True,"productionAccepted":True,"acceptanceScope":"static_ui_artwork_qa","userApproved":False,"clientIntegrated":False})
 if entry.get("variant")=="draw":
  rec["variant"]="draw"
  rec["generationTimestampBasis"]="从原生成会话已完成的image_gen.generation事件恢复；时间为该事件完成时间"
  rec["evidence"]="恢复完成事件exec-4693da90-d2a2-46d7-a0e4-731cdc4bf14b；savedPath、revisedPrompt及四张inputImages路径/SHA-256已核对。工具未披露实际模型/质量。"
  rec["completionEventId"]="exec-4693da90-d2a2-46d7-a0e4-731cdc4bf14b"
  rec["recoveryEvidence"]="work/rooms/draw-recovery-evidence.json"
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 key=entry["id"]+"."+entry["variant"] if entry.get("variant") else entry["id"]
 pages.append({"id":entry["id"],"variant":entry.get("variant"),"sourceKey":key,"type":entry.get("type","independent_full_screen"),"title":entry["title"],"file":entry["file"],"generationRecord":entry["file"]+".generation.json","prompt":entry["prompt"],"width":rec["width"],"height":rec["height"],"format":rec["format"],"mode":rec["mode"],"sha256":rec["sha256"],"status":"artwork_qa_passed","inspection":rec["inspection"],"notes":entry.get("notes",[])})
 validation.append({"file":entry["file"],"png":"passed","fileHash":"passed","promptHash":"passed","referenceHashes":"passed","visual":"passed"})
state_map=[]
for state in data["stateMap"]:
 sources=[]
 for key in state["sources"]:
  match=[p for p in pages if p["sourceKey"]==key]
  assert match,key
  sources.extend({"key":key,"file":p["file"],"sha256":p["sha256"]} for p in match)
 state_map.append({**state,"sourceFiles":sources,"status":"mapped_to_verified_artwork","coverageType":"component_assembly_mapping" if state["state"]=="room.full" else "direct_artwork"})
state_map.append({"state":"play.draw","sources":["UI23.draw"],"sourceFiles":[{"key":"UI23.draw","file":draw["file"],"sha256":sha(root/draw["file"])}],"description":"真实新增独立流局状态图：四家本局积分0，继续下一局/返回大厅；不再仅映射旧UI23控件板。","status":"mapped_to_verified_artwork","coverageType":"direct_artwork"})
manifest={"schemaVersion":1,"domain":"rooms_and_states","scope":"FULL_UI_SCOPE UI04/UI05/UI06/UI07/UI08/UI23/UI24","generatedAt":now,"count":len(pages),"contractIdCount":7,"completedIds":data["scopeIds"],"pages":pages,"stateCoverage":state_map,"stateMap":state_map,"integrationNotes":["UI04匹配中与成功为互斥状态，运行时分开显示。","UI23主图和UI24均为状态规范板，板内缩略态不作为额外整屏计数。UI23.draw另为真实独立流局整屏，仍属于UI23一个合同ID。","房间满员状态采用UI07四座容器+第四个头像/准备标签+正常开始按钮组装；不存在额外满员独立全屏，不应冒算。","流局0分是本轮通用示例；实际计分与地方规则需由产品/服务端给定。","示例昵称/房号不是真实用户或服务器数据。"],"validation":{"checkedAt":now,"entries":validation,"failures":[],"allPassed":True},"actualModel":None,"actualQuality":None,"delivery":{"localOnly":True,"userApproved":False,"clientIntegrated":False,"uploaded":False}}
(root/"designs/ui/full-suite/rooms/manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(root/"work/rooms/finalize-input.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
qa="# 房间与状态域检查\n\n"+now+"。已完成7个合同ID，9张真实成图。UI04包含匹配中/成功两态，UI23包含控件板/流局两图，不额外冒算ID。\n\n"+ "\n".join("- "+p["sourceKey"]+" "+p["title"]+"："+str(p["width"])+"×"+str(p["height"])+"；PNG/图像哈希/提示词哈希/参考哈希/视觉检查通过。" for p in pages)+"\n\n流局图从中断前已完成的生成事件恢复，并非重绘。完成回执与实际提示词、4张输入参考SHA-256完全一致；实际型号/质量未披露，保持null。\n"
(root/"designs/ui/full-suite/rooms/QA.md").write_text(qa,encoding="utf-8")
print(json.dumps({"files":len(pages),"ids":data["scopeIds"],"states":len(state_map),"draw":draw["file"],"drawSha256":sha(root/draw["file"]),"validation":"passed"},ensure_ascii=False))

