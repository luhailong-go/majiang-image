from pathlib import Path
from PIL import Image
import json,hashlib,re,datetime
R=Path(r"D:\work\majiang-image")
m=json.loads((R/"exports/ui-delivery-manifest.json").read_text(encoding="utf-8"))
errors=[];warnings=[];record_count=0;checked_records=set();checks=[];historical_removed=set()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:errors.append(msg)
def resolve(value):
 p=Path(value)
 return p if p.is_absolute() else R/p
def check_ref(ref,label):
 if isinstance(ref,str):return
 if not isinstance(ref,dict):return
 f=ref.get("file")
 if f:
  p=resolve(f)
  if not p.is_file() and ref.get("pixelsPresentInProject") is False:
   rp=p.with_name(p.name+".generation.json")
   require(rp.is_file(),"Removed source must retain provenance "+f)
   if rp.is_file():
    rd=json.loads(rp.read_text(encoding="utf-8-sig"))
    require(rd.get("pixelsRetainedInProject") is False and bool(rd.get("cleanup")),"Removed source cleanup evidence "+f)
    require(rd.get("sha256")==ref.get("sha256"),"Removed source provenance hash "+f)
    historical_removed.add(f);check_record(rp)
  else:
   require(p.is_file(),label+" missing "+f)
   if p.is_file() and ref.get("sha256"):require(digest(p)==ref["sha256"].lower(),label+" hash "+f)
 if ref.get("generationRecord"):
  check_record(resolve(ref["generationRecord"]))
def check_record(p):
 global record_count
 if p in checked_records:return
 checked_records.add(p);require(p.is_file(),"Missing record "+str(p))
 if not p.is_file():return
 try:d=json.loads(p.read_text(encoding="utf-8-sig"))
 except Exception as e:errors.append("Record parse "+str(p)+": "+str(e));return
 record_count+=1
 if d.get("file") and d.get("sha256"):
  f=resolve(d["file"])
  if not f.is_file() and d.get("pixelsRetainedInProject") is False and d.get("cleanup"):
   historical_removed.add(d["file"])
  else:
   require(f.is_file(),"Record image missing "+str(f))
   if f.is_file():require(digest(f)==d["sha256"].lower(),"Record image hash "+str(f))
 prompt=d.get("prompt")
 if isinstance(prompt,str):
  pp=resolve(prompt);require(pp.is_file(),"Prompt missing "+prompt)
  if pp.is_file() and d.get("promptSha256"):require(digest(pp)==d["promptSha256"].lower(),"Prompt hash "+prompt)
 for ref in d.get("references",[]):check_ref(ref,"Reference")
 derived=d.get("derivedFrom")
 for ref in derived if isinstance(derived,list) else [derived] if derived else []:check_ref(ref,"Derived source")
 if d.get("actualModel") is not None or d.get("actualQuality") is not None:
  warnings.append("Review actual metadata evidence: "+str(p))
items=sum([m[k] for k in ["pages","components","characters","tiles"]],[])
for item in items:
 p=R/item["file"];require(p.is_file(),"Asset missing "+item["file"])
 if not p.is_file():continue
 require(digest(p)==item["sha256"],"Catalogue hash "+item["file"])
 try:
  with Image.open(p) as im:im.verify()
  with Image.open(p) as im:
   require(im.size==(item["width"],item["height"]),"Dimensions "+item["file"])
   if item in m["components"] and item.get("id")!="table-background":
    require("A" in im.getbands(),"Component has no alpha "+item["file"])
   ns=item.get("nineSlice")
   if ns:
    require(len(ns)==4 and min(ns)>=0 and ns[0]+ns[2]<im.width and ns[1]+ns[3]<im.height,"Invalid nineSlice "+item["file"])
 except Exception as e:errors.append("PNG decode "+item["file"]+": "+str(e))
 if item.get("record"):check_record(R/item["record"])
 else:errors.append("Asset record missing "+item["file"])
 if item.get("prompt"):require((R/item["prompt"]).is_file(),"Catalogue prompt missing "+item["prompt"])
require(len({p["id"] for p in m["pages"]})==24,"Contract must cover 24 unique IDs")
require(m["tileFaceCount"]==34,"Tile face count must equal34")
require(len(m["characters"])==5,"One full body and four avatars required")
require(len(m["components"])>=1,"Components missing")
for row in m["states"]:
 require(row["status"]=="mapped","Pending state "+row["state"])
 for file in row["files"]:require((R/file).is_file(),"State source missing "+file)
for path in m.get("sourceManifests",[]):require((R/path).is_file(),"Domain manifest missing "+path)
for name,field in [("assets/tiles/manifest.json","tiles"),("assets/ui/manifest.json","assets"),("assets/characters/manifest.json","assets")]:
 d=json.loads((R/name).read_text(encoding="utf-8-sig"))
 for a in d.get(field,[]):
  if a.get("sha256") and a.get("file"):
   p=R/a["file"];require(p.is_file() and digest(p)==a["sha256"],"Domain manifest hash "+a.get("file","?"))
  status=str(a.get("status","")).lower()
  if status:require("pending" not in status and "fail" not in status,"Unpassed domain asset "+a.get("file","?")+": "+status)
html=(R/"index.html").read_text(encoding="utf-8")
for href in re.findall(r'href="([^"]+)"',html):
 if href.startswith(("http:","https:","#")) or "+" in href or "'" in href:continue
 require((R/href.split("#")[0]).is_file(),"Static link missing "+href)
script=re.search(r"<script>([\s\S]*)</script>",html).group(1)
(R/"work/full_ui/gallery-runtime.js").write_text(script,encoding="utf-8")
for checkpath in ["work/full_ui/component-independent-qa.json"]:
 if not (R/checkpath).exists():warnings.append("Independent report not yet available: "+checkpath)
result={"checkedAt":datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat(),"status":"passed" if not errors else "failed","assetCount":len(items),"pageImages":len(m["pages"]),"contractIds":len({p["id"] for p in m["pages"]}),"components":len(m["components"]),"characters":len(m["characters"]),"tileFaces":m["tileFaceCount"],"recordsChecked":record_count,"statesChecked":len(m["states"]),"errors":errors,"warnings":warnings,"historicalSourcesRemovedPerRetentionPolicy":sorted(historical_removed),"browserInteraction":"not tested: file:// denied by browser URL policy; no workaround attempted","checks":["PNG integrity/dimensions/hash","Generated and derived record graph","Prompt/reference hashes","24 unique contract IDs","Precise draw/claimed/match state files","Domain manifest file hashes","Nine-slice bounds","Static gallery links and extracted JS syntax target"]}
(R/"exports/delivery-validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))

