from pathlib import Path
import json
R=Path(r"D:\work\majiang-image")
p=R/"work/full_ui/build_gallery.py";s=p.read_text(encoding="utf-8")
s=s.replace('state_rows=[{"state":k,"uiIds":v,"files":[p["file"] for p in pages if p["id"] in v],"status":"mapped" if all(i in ids for i in v) else "pending"} for k,v in states.items()]','''state_rows=[{"state":k,"uiIds":v,"files":[p["file"] for p in pages if p["id"] in v],"status":"mapped" if all(i in ids for i in v) else "pending"} for k,v in states.items()]
precise_states={
"play.draw":["designs/ui/full-suite/rooms/ui23-draw-result.png"],
"mail.claim_pending":["designs/ui/full-suite/system/ui18-mail-detail.png"],
"mail.claimed":["designs/ui/full-suite/system/ui18-mail-claimed.png"],
"system.matching":["designs/ui/full-suite/rooms/ui04-casual-match.png"],
"system.match_success":["designs/ui/full-suite/rooms/ui04-match-success.png"]}
for key,paths in precise_states.items():
 row=next((x for x in state_rows if x["state"]==key),None)
 if row is None:
  row={"state":key,"uiIds":[]};state_rows.append(row)
 row["files"]=paths
 row["status"]="mapped" if all((R/path).exists() for path in paths) else "pending"
domain_manifests=[]
domain_state_coverage=[]
for mp in [R/"designs/ui/full-suite/rooms/manifest.json",R/"designs/ui/full-suite/system/manifest.json",R/"assets/characters/manifest.json",R/"assets/tiles/manifest.json",R/"assets/ui/manifest.json",R/"assets/ui/common/manifest.json",R/"assets/ui/gameplay/manifest.json"]:
 if not mp.exists():continue
 d=json.loads(mp.read_text(encoding="utf-8-sig"));domain_manifests.append(rel(mp))
 domain_state_coverage+=d.get("stateCoverage",[])
''')
s=s.replace('"modelEvidence":"配置目标GPT Image 2.5 Sunburst/max；工具未披露的实际值保持null"}','''"modelEvidence":"配置目标GPT Image 2.5 Sunburst/max；工具未披露的实际值保持null","sourceManifests":domain_manifests,"domainStateCoverage":domain_state_coverage,"browserVerification":{"status":"not_run_policy_blocked","reason":"内置浏览器URL策略拒绝file://；未采用替代浏览器/本地HTTP服务器绕过。已进行本地文件/脚本静态验证。"},"deliveryStatus":"pending_final_validation"}''')
p.write_text(s,encoding="utf-8")
print("Precise state sources and delivery evidence added.")

