from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil,sys,copy
R=Path(r"D:\work\majiang-image")
jobs=json.loads((R/"work/system-fixes/jobs.json").read_text(encoding="utf-8-sig"))
selected=set(sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
notes={
"UI18":["实际查看修复后整屏：右下灰色“已领取”块已完全移除，纸绢底纹连续。","本页仅为待领取状态；红色待领取、领取附件主按钮、禁用删除及领取后可删除保留。","标题、日期、三句正文、头像框附件、道童兔子、场景、返回与关闭均保持清楚。"],
"UI19":["实际查看修复后整屏：+24、+8为朱砂红；-12为玉绿；0保留中性灰。","四行数值、日期时间、胜负/流局结果徽章、详情入口和其他版式保持不变。"],
"UI11":["实际查看修复后整屏：三行-10统一为玉绿，+30保留朱砂红。","四家头像昵称、牌面摘要、胡牌标记、标题、两项操作与关闭入口保持清楚。"]}
for j in jobs:
 if j["id"] not in selected:continue
 target=R/j["target"]; src=R/j["source"]; rp=Path(str(target)+".generation.json"); srp=Path(str(src)+".generation.json")
 old=json.loads(rp.read_text(encoding="utf-8-sig"))
 if not srp.exists():
  s=copy.deepcopy(old);s["originalFileAtGeneration"]=s["file"];s["file"]=j["source"];s["retainedAs"]="immutable_input_for_targeted_fix";s["sha256"]=sha(src)
  s["inspection"]["visualStatus"]="superseded_requires_fix";s["inspection"]["unresolvedIssues"]=[j["fix"]]
  s["status"]["productionAccepted"]=False
  srp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 receipt=json.loads((R/f"work/system-fixes/{j['id']}-receipt.json").read_text(encoding="utf-8-sig"))
 candidate=R/f"work/system-fixes/{j['id']}-candidate.png"
 with Image.open(candidate) as im:im.verify()
 with Image.open(candidate) as im:w,h=im.size;fmt=im.format;mode=im.mode
 assert (w,h)==(1672,941),(j["id"],w,h)
 shutil.copyfile(candidate,target)
 refs=[]
 for index,path in enumerate(receipt["submittedReferences"],1):
  p=Path(path)
  refs.append({"inputIndex":index,"file":p.relative_to(R).as_posix(),"submittedPath":str(p),"sha256":sha(p),"purpose":"不可变编辑目标" if index==1 else "主UI风格参考","actuallyAttached":True})
 t=datetime.fromisoformat(receipt["observedCompletedAt"].replace("Z","+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat()
 record={"schemaVersion":2,"scopeId":j["id"],"uiId":j["id"],"title":j["title"],"file":j["target"],"sha256":sha(target),"generatedAt":t,"generationTimestampBasis":"客户端观察工具完成时间","clientTimezone":"America/New_York","width":w,"height":h,"format":fmt,"mode":mode,"nativeDimensions":{"width":w,"height":h},"requestedDimensionsInPrompt":{"width":1672,"height":941},"resampled":False,"tool":"image_gen.imagegen","route":"builtin","operation":"AI targeted edit","generationCallId":None,"resultId":None,"outputArtifactFileId":Path(receipt["source"]).stem,"resultReceipt":receipt,"configSnapshot":json.loads((R/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"size":None,"transparent_background":False,"referenced_image_paths":receipt["submittedReferences"],"promptFile":j["promptFile"]},"actualModel":None,"actualQuality":None,"evidence":"工具仅披露image_url与output_hint路径；原生尺寸和SHA-256由PNG实测。","unverifiedReason":"宿主管理，工具未披露可核实版本/质量","prompt":j["promptFile"],"promptSha256":sha(R/j["promptFile"]),"references":refs,"source":{"toolNativeOutput":receipt["source"],"sha256":sha(Path(receipt["source"])),"operation":"byte-identical copy","derived":False},"editTarget":{"file":j["source"],"sha256":sha(src),"generationRecord":j["source"]+".generation.json"},"inspection":{"pngIntegrity":"passed","visualStatus":"passed","notes":notes[j["id"]],"unresolvedIssues":[]},"status":{"assetStage":"full_ui_art_candidate","readyForReview":True,"artworkQaPassed":True,"userApproved":False,"clientIntegrated":False},"delivery":{"localOnly":True,"uploaded":False}}
 if j["id"] in ["UI19","UI11"]:record["requestedColorTokens"]={"scorePositive":"#B52F20","scoreNegative":"#196448","scoreZero":"neutral_gray"}
 rp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"id":j["id"],"file":j["target"],"sha256":sha(target),"visual":"passed"},ensure_ascii=False))

