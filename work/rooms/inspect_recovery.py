import json,hashlib
from pathlib import Path
p=Path(r"C:\Users\luyua\.codex\sessions\2026\10\26\rollout-2026-10-26T04-01-19-01a1773a-69c8-7161-aea9-9df0511993e3.jsonl")
events=[]
for n,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
 try:d=json.loads(line)
 except:continue
 pl=d.get("payload",{})
 if n>=390 and pl.get("type")=="custom_tool_call":
  print(n,pl.get("name"),pl.get("input","")[:2500])
 item=pl.get("item",{})
 if item.get("id")=="exec-4693da90-d2a2-46d7-a0e4-731cdc4bf14b":
  events.append({"line":n,"timestamp":d["timestamp"],"eventType":pl.get("type"),"item":{k:v for k,v in item.items() if k not in ["result","image","data"]}})
print(json.dumps(events,ensure_ascii=False,indent=2))
(Path(r"D:\work\majiang-image\work\rooms")/"draw-recovery-evidence.json").write_text(json.dumps({"sourceSession":str(p),"events":events},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

