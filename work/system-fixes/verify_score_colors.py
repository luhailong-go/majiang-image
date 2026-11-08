from pathlib import Path
from PIL import Image
import hashlib,json
R=Path(r"D:\work\majiang-image")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
areas={
"UI19":{"file":"designs/ui/full-suite/system/ui19-records.png","samples":[("positive_24",(1105,361,1205,411),"red"),("negative_12",(1105,453,1205,504),"green"),("positive_8",(1105,635,1205,683),"red")]},
"UI11":{"file":"designs/ui/full-suite/core/ui11-round-result.png","samples":[("positive_30",(1303,253,1445,333),"red"),("negative_10_row2",(1348,427,1445,480),"green"),("negative_10_row3",(1348,549,1445,603),"green"),("negative_10_row4",(1348,673,1445,729),"green")]}
}
out=[]
for key,item in areas.items():
 with Image.open(R/item["file"]) as im:
  for label,bounds,expected in item["samples"]:
   px=list(im.convert("RGB").crop(bounds).getdata())
   red=sum(r>g*1.4 and r>b*1.4 and r>70 for r,g,b in px)
   green=sum(g>r*1.3 and g>b*1.1 and g>40 for r,g,b in px)
   passed=(red>30 and red>green*4) if expected=="red" else (green>30 and green>red*4)
   out.append({"uiId":key,"sample":label,"roi":list(bounds),"expectedFamily":expected,"redPixels":red,"greenPixels":green,"passed":passed})
assert all(x["passed"] for x in out),out
(R/"work/system-fixes/score-color-verification.json").write_text(json.dumps({"method":"read-only ROI color-family counts; actual image editing used builtin image_gen","checks":out},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))

