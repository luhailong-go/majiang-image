from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import hashlib,json,shutil,sys
root=Path(r"D:\work\majiang-image")
item=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rel="designs/ui/full-suite/system/"+item["slug"]+".png"
out=root/rel
source=Path(item["source"])
shutil.copyfile(source,out)
with Image.open(out) as im:
 im.verify()
with Image.open(out) as im:
 width,height=im.size
 mode,fmt=im.mode,im.format
promptrel="prompts/system/"+item["slug"]+".prompt.txt"
(root/promptrel).write_text(item["prompt"],encoding="utf-8")
refs=[]
for i,p in enumerate(item["refs"],1):
 rp=Path(p)
 refs.append({"inputIndex":i,"file":str(rp.relative_to(root)).replace("\\","/"),"submittedPath":str(rp),"sha256":sha(rp),"purpose":"主风格参考" if i<3 else ("当前大厅风格补充参考" if i==3 else "四座头像身份参考"),"actuallyAttached":True})
record={"schemaVersion":1,"scopeId":item["id"],"title":item["title"],"file":rel,"sha256":sha(out),"generatedAt":datetime.fromisoformat(item["completed"].replace("Z","+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat(),"generationTimestampBasis":"客户端观察工具完成时间","clientTimezone":"America/New_York","width":width,"height":height,"format":fmt,"mode":mode,"nativeDimensions":{"width":width,"height":height},"requestedDimensionsInPrompt":{"width":2048,"height":1152},"resampled":False,"tool":"image_gen.imagegen","route":"builtin","generationCallId":None,"resultId":None,"outputArtifactFileId":source.stem,"resultReceipt":{"resultKeys":["image_url","output_hint"],"outputHint":item["hint"]},"configSnapshot":json.loads((root/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":False,"referenced_image_paths":item["refs"],"size":None,"promptFile":promptrel},"actualModel":None,"actualQuality":None,"evidence":"工具只披露image_url与output_hint；原生尺寸和哈希由PNG实测。","unverifiedReason":"宿主管理，工具未披露可核实版本/质量","prompt":promptrel,"promptSha256":sha(root/promptrel),"references":refs,"source":{"toolNativeOutput":str(source),"sha256":sha(source),"operation":"byte-identical copy","derived":False},"inspection":{"pngIntegrity":"passed","visualStatus":item.get("qa","pending"),"notes":item.get("notes",[]),"unresolvedIssues":[]},"status":{"assetStage":"full_ui_art_candidate","readyForReview":item.get("qa")=="passed","userApproved":False,"clientIntegrated":False},"delivery":{"localOnly":True,"uploaded":False}}
(root/(rel+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"id":item["id"],"file":rel,"width":width,"height":height,"sha256":record["sha256"]},ensure_ascii=False))
