from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,zipfile,re
R=Path(r"D:\work\majiang-image").resolve()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=set()
for folder in ["assets","config","docs","prompts","designs"]:
 for p in (R/folder).rglob("*"):
  if p.is_file() and "__pycache__" not in p.parts and p.suffix.lower() not in [".tmp",".log",".pyc"]:
   files.add(p)
for p in (R/"references/style").glob("*"):
 if p.is_file():files.add(p)
files.add(R/"references/manifest.json")
for name in ["AGENTS.md","README.md","index.html","exports/ui-delivery-manifest.json","exports/delivery-validation.json","exports/component-independent-qa.json","exports/gallery-script-validation.json"]:
 files.add(R/name)
# Include actual provenance/QA/reproduction files referenced from delivered metadata,
# while leaving unrelated work-in-progress outside the archive.
pending=list(files);seen=set()
while pending:
 p=pending.pop()
 if p in seen:continue
 seen.add(p)
 if p.suffix.lower() not in [".json",".md",".html",".txt"]:continue
 text=p.read_text(encoding="utf-8-sig",errors="strict")
 for s in re.findall(r'work/[A-Za-z0-9_./-]+\.(?:png|json|py|cjs|html|txt)',text):
  q=(R/s).resolve()
  if q.is_relative_to(R) and q.is_file() and q not in files:files.add(q);pending.append(q)
for p in files:
 assert p.is_file() and p.resolve().is_relative_to(R),str(p)
entries=[{"file":p.relative_to(R).as_posix(),"bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted(files)]
file_manifest={"schemaVersion":1,"createdAt":datetime.now(timezone(timedelta(hours=-4))).isoformat(),"archive":"mahjong-ui-full-suite-v1.zip","payloadFileCount":len(entries),"payloadBytes":sum(e["bytes"] for e in entries),"selfHashExcluded":True,"files":entries,"notes":["Relative project paths preserved; includes native sources and provenance/QA files required by delivered records.","No configured remote or credentials included.","package-file-manifest.json is inside ZIP but excluded from its own recursive hash list."]}
fm=R/"exports/package-file-manifest.json";fm.write_text(json.dumps(file_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
archive=R/"exports/mahjong-ui-full-suite-v1.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for e in entries:z.write(R/e["file"],e["file"])
 z.write(fm,"exports/package-file-manifest.json")
with zipfile.ZipFile(archive) as z:
 bad=z.testzip();assert bad is None,bad
 names=set(z.namelist())
 for e in entries:
  assert e["file"] in names,e["file"]
  assert hashlib.sha256(z.read(e["file"])).hexdigest()==e["sha256"],e["file"]
 assert z.read("exports/package-file-manifest.json")==fm.read_bytes()
 result={"status":"passed","archive":archive.relative_to(R).as_posix(),"sha256":digest(archive),"bytes":archive.stat().st_size,"memberCount":len(names),"payloadFilesHashVerified":len(entries),"zipCRC":"passed","relativePaths":True,"verifiedAt":datetime.now(timezone(timedelta(hours=-4))).isoformat(),"keyFiles":["index.html","README.md","exports/ui-delivery-manifest.json","assets/ui/manifest.json","assets/tiles/manifest.json","assets/characters/manifest.json"],"scope":"Complete static UI art delivery; browser interaction was not tested because file:// was policy-blocked."}
(R/"exports/package-verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))

