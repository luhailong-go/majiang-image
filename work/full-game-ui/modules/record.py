from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil,sys
R=Path(r"D:\work\majiang-image")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
req=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
j=req["job"];source=Path(req["source"]);target=R/j["file"]
if target.exists():raise RuntimeError("Existing output must not be overwritten: "+str(target))
shutil.copyfile(source,target)
with Image.open(target) as im:im.verify()
with Image.open(target) as im:w,h=im.size;fmt=im.format;mode=im.mode
refs=[{"inputIndex":i+1,"file":p,"submittedPath":str(R/p),"sha256":sha(R/p),"purpose":"主UI风格参考" if p.startswith("references/style/") else "当前大厅布局与风格" if "lobby" in p else "四角色身份参考" if "avatars" in p else "实际编辑目标","actuallyAttached":True} for i,p in enumerate(j["references"])]
time=datetime.fromisoformat(req["finished"].replace("Z","+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat()
record={"schemaVersion":2,"scopeId":j["id"],"uiId":j["id"],"variant":j.get("variant","default"),"title":j["title"],"file":j["file"],"sha256":sha(target),"generatedAt":time,"generationTimestampBasis":"客户端观察工具完成时间","clientTimezone":"America/New_York","width":w,"height":h,"format":fmt,"mode":mode,"nativeDimensions":{"width":w,"height":h},"requestedDimensionsInPrompt":{"width":2048,"height":1152},"resampled":False,"tool":"image_gen.imagegen","route":"builtin","generationCallId":None,"resultId":None,"outputArtifactFileId":source.stem,"resultReceipt":req["receipt"],"configSnapshot":json.loads((R/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"size":None,"transparent_background":False,"referenced_image_paths":[r["submittedPath"] for r in refs],"promptFile":j["promptFile"]},"actualModel":None,"actualQuality":None,"evidence":"工具只提供image_url与output_hint及输出PNG路径；尺寸、格式及SHA-256由落盘图片测量。","unverifiedReason":"宿主管理，工具未披露可核实版本/质量","prompt":j["promptFile"],"promptSha256":sha(R/j["promptFile"]),"references":refs,"source":{"toolNativeOutput":str(source),"sha256":sha(source),"operation":"byte-identical copy","derived":False},"coveredStates":j["states"],"inspection":{"pngIntegrity":"passed","visualStatus":"pending","notes":[],"unresolvedIssues":[]},"status":{"assetStage":"full_game_ui_art_candidate","readyForReview":False,"userApproved":False,"clientIntegrated":False},"delivery":{"localOnly":True,"uploaded":False}}
Path(str(target)+".generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"id":j["id"],"file":j["file"],"width":w,"height":h,"sha256":record["sha256"]},ensure_ascii=False))

