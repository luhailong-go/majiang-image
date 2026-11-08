from pathlib import Path
import json,re,hashlib
from datetime import datetime,timezone,timedelta
root=Path(r"D:\work\majiang-image")
path=root/"index.html"
raw=path.read_text(encoding="utf-8-sig")
blocks=re.findall(r"<script[^>]*>(.*?)</script>",raw,re.S)
assert len(blocks)==1
js_path=root/"work/rooms/gallery-inline-static-check.js"
js_path.write_text(blocks[0],encoding="utf-8")
m=re.search(r"const DATA=(.*?);\s*let tab=",blocks[0],re.S)
assert m,"Inline data not found"
data=json.loads(m.group(1))
missing=[]
for section in ["pages","components","tiles","characters"]:
 for entry in data.get(section,[]):
  for field in ["file","record","prompt"]:
   value=entry.get(field)
   if value and not (root/value).exists():missing.append({"section":section,"field":field,"value":value})
required_ids=["stats","search","section-title","section-note","bg","filters","grid","viewer","view-title","prev","next","view-bg","close","view-media","view-img","view-info","view-open"]
missing_elements=[i for i in required_ids if not re.search(r'id=["\x27]'+re.escape(i)+r'["\x27]',raw)]
out={"checkedAt":datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec="seconds"),"snapshotFile":"index.html","snapshotSha256":hashlib.sha256(path.read_bytes()).hexdigest(),"scope":"static_only_current_snapshot","browserTest":{"status":"blocked_by_browser_url_policy","attemptedUrl":"file:///D:/work/majiang-image/index.html","reason":"Browser tool allows only http/https and explicitly disallows workarounds; no browser interaction pass claimed."},"inlineDataParsed":True,"listedCounts":{k:len(data.get(k,[])) for k in ["pages","components","tiles","characters"]},"listedAssetPathsExist":not missing,"missingPaths":missing,"requiredElementsPresent":not missing_elements,"missingElements":missing_elements,"scriptSyntaxStatus":"pending_node_check","note":"根画廊仍在汇总中；本记录不作为最终完整度或浏览器视觉/交互验收。"}
(root/"work/rooms/gallery-static-qa.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))

