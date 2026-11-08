from pathlib import Path
import json
R=Path(r"D:\work\majiang-image")
p=R/"work/full_ui/build_gallery.py";s=p.read_text(encoding="utf-8")
start=s.index("components=[]\n");end=s.index("characters=[]\n",start)
s=s[:start]+'''components=[]
cm=R/"assets/ui/manifest.json"
if cm.exists():
 compdata=json.loads(cm.read_text(encoding="utf-8-sig"))
 for a in compdata["assets"]:
  item=image_item(R/a["file"],a.get("name",a["id"]),a["id"],"通用组件" if a["group"]=="common" else "对局组件",a.get("record"))
  item["nineSlice"]=a.get("nineSlice");item["anchor"]=a.get("anchor");item["qaStatus"]=a.get("status")
  components.append(item)
''' +s[end:]
p.write_text(s,encoding="utf-8")
print("Component gallery now uses authoritative manifest names.")

