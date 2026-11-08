from pathlib import Path
from PIL import Image
import hashlib,json,sys,shutil
from datetime import datetime,timezone,timedelta
root=Path(r"D:\work\majiang-image")
request=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
out=root/request["file"]
out.parent.mkdir(parents=True,exist_ok=True)
src=Path(request["source"])
if out.exists(): raise RuntimeError("Refusing overwrite: "+str(out))
shutil.copyfile(src,out)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(out) as im:
    im.verify()
with Image.open(out) as im:
    im.load()
    meta={"width":im.width,"height":im.height,"format":im.format,"mode":im.mode}
refs=[]
for i,ref in enumerate(request["references"],1):
    p=root/ref["file"]
    refs.append({"inputIndex":i,**ref,"submittedPath":str(p),"sha256":sha(p),"actuallyAttached":True})
rec={
"schemaVersion":1,"id":request["id"],"file":request["file"],"sha256":sha(out),
"generatedAt":request["generatedAt"],"generationTimestampBasis":"客户端观察到工具返回的完成时间，非服务端披露时间","clientTimezone":"America/New_York",
**meta,"nativeDimensions":{"width":meta["width"],"height":meta["height"]},"requestedDimensionsInPrompt":{"width":2048,"height":1152},"resampled":False,
"tool":"image_gen.imagegen","route":"builtin","generationCallId":None,"resultId":None,
"outputArtifactFileId":src.stem,"resultReceipt":request["receipt"],
"configSnapshot":json.loads((root/"config/image-generation.json").read_text(encoding="utf-8-sig")),
"submittedParameters":{"model":None,"quality":None,"transparent_background":False,"referenced_image_paths":[r["submittedPath"] for r in refs],"promptFile":request["prompt"],"size":None},
"actualModel":None,"actualQuality":None,"evidence":"返回值仅提供image_url/output_hint及PNG路径；尺寸、哈希、格式实测。",
"unverifiedReason":"宿主管理，工具未披露可核实版本/质量",
"prompt":request["prompt"],"promptSha256":sha(root/request["prompt"]),"references":refs,
"source":{"toolNativeOutput":str(src),"sha256":sha(src),"operation":"byte-identical copy","derived":False},
"inspection":{"pngIntegrity":"passed","visualInspectionCompleted":False,"checks":[],"unresolvedIssues":[]},
"status":{"assetStage":"complete_ui_art_direction_v1","readyForUserReview":False,"userApproved":False,"productionAccepted":False,"clientIntegrated":False},
"delivery":{"localOnly":True,"uploaded":False,"remoteConfigured":False}
}
(out.parent/(out.name+".generation.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":str(out),**meta,"sha256":sha(out)},ensure_ascii=False))

