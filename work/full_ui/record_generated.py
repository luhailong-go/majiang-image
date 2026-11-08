from pathlib import Path
from PIL import Image
from datetime import datetime, timezone, timedelta
import json, hashlib, shutil, sys
ROOT=Path(r"D:\work\majiang-image")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
request=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
dest=ROOT/request["file"]; dest.parent.mkdir(parents=True,exist_ok=True)
source=Path(request["source"])
if dest.exists() and sha(dest)!=sha(source): raise RuntimeError("Will not overwrite a different image: "+str(dest))
shutil.copyfile(source,dest)
with Image.open(dest) as img: img.verify()
with Image.open(dest) as img:
 img.load(); size=img.size; mode=img.mode; fmt=img.format
 alpha=None
 if "A" in img.getbands():
  a=img.getchannel("A"); h=a.histogram()
  alpha={"range":list(a.getextrema()),"fullyTransparent":h[0],"semiTransparent":sum(h[1:255]),"fullyOpaque":h[255],"bbox":a.getbbox()}
config=json.loads((ROOT/"config/image-generation.json").read_text(encoding="utf-8-sig"))
refs=[]
for entry in request["references"]:
 p=ROOT/entry["file"]
 refs.append({**entry,"submittedPath":str(p),"sha256":sha(p),"actuallyAttached":True})
now=datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec="seconds")
record={
 "schemaVersion":2,"file":request["file"],"uiId":request.get("uiId"),"title":request.get("title"),
 "sha256":sha(dest),"generatedAt":request.get("generatedAt",now),"generationTimestampBasis":"客户端观察到工具返回的完成时间","clientTimezone":"America/New_York",
 "tool":"image_gen.imagegen","route":"builtin","generationCallId":None,"resultId":None,"outputArtifactFileId":source.stem,
 "width":size[0],"height":size[1],"format":fmt,"mode":mode,"nativeDimensions":{"width":size[0],"height":size[1]},
 "requestedDimensionsInPrompt":request.get("requestedDimensions",[2048,1152]),"resampled":False,
 "configSnapshot":config,"submittedParameters":{"model":None,"quality":None,"size":None,"transparent_background":request.get("transparent",False),"referenced_image_paths":[x["submittedPath"] for x in refs],"promptFile":request["prompt"]},
 "actualModel":None,"actualQuality":None,"evidence":"结果提供image_url与output_hint及PNG文件路径；尺寸、格式和Alpha由文件检测。工具未返回可核实模型或质量。",
 "unverifiedReason":"宿主管理，工具未披露可核实版本/质量。配置目标不是实际版本证明。",
 "prompt":request["prompt"],"promptSha256":sha(ROOT/request["prompt"]),"references":refs,
 "source":{"toolNativeOutput":str(source),"sha256":sha(source),"operation":"byte-identical copy","derived":False},
 "inspection":{"pngIntegrity":"passed","alphaStatistics":alpha,"visualStatus":"pending","issues":[]},
 "status":{"stage":"full_ui_art","userApproved":False,"productionAccepted":False,"clientIntegrated":False},
 "coveredStates":request.get("coveredStates",[]),"receipt":request.get("receipt"),
 "delivery":{"localOnly":True,"uploaded":False}
}
rp=ROOT/(request["file"]+".generation.json"); rp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":str(dest),"record":str(rp),"size":size,"mode":mode,"sha256":record["sha256"]},ensure_ascii=False))

