from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone,timedelta
root=Path(r"D:\work\majiang-image")
ev=json.loads((root/"work/rooms/draw-recovery-evidence.json").read_text(encoding="utf-8"))["events"][0]
item=ev["item"]
prompt_path=root/"prompts/rooms/ui23-draw-result.prompt.txt"
actual=prompt_path.read_text(encoding="utf-8-sig")
assert actual==item["revisedPrompt"],"Persisted prompt differs from actual generation prompt"
refs=[]
for entry in item["inputImages"]:
 path=Path(entry["path"])
 assert hashlib.sha256(path.read_bytes()).hexdigest()==entry["sha256"]
 refs.append({"file":path.relative_to(root).as_posix(),"purpose":"实际生成输入，已按完成回执核对" })
req={"id":"UI23","file":"designs/ui/full-suite/rooms/ui23-draw-result.png","source":item["savedPath"],"prompt":"prompts/rooms/ui23-draw-result.prompt.txt","references":refs,"generatedAt":datetime.fromisoformat(ev["timestamp"].replace("Z","+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat(),"receipt":{"recoveredFromCompletionEvent":True,"eventId":item["id"],"eventStatus":item["status"],"completedAtUTC":ev["timestamp"],"savedPath":item["savedPath"],"inputImages":item["inputImages"],"evidenceFile":"work/rooms/draw-recovery-evidence.json"}}
rp=root/"work/rooms/save-ui23-draw-result.json"
rp.write_text(json.dumps(req,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(str(rp))

