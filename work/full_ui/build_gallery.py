from pathlib import Path
from PIL import Image
import json,re,hashlib,datetime
R=Path(r"D:\work\majiang-image")
TITLES={1:"启动与加载",2:"登录入口",3:"完整大厅",4:"休闲匹配",5:"创建房间",6:"输入房间号",7:"好友房等待",8:"邀请好友",9:"四人牌桌基础态",10:"对局操作选择态",11:"单局结算",12:"整场结算",13:"个人资料",14:"角色与头像选择",15:"好友与申请",16:"快捷聊天与表情",17:"邮件列表",18:"邮件详情",19:"战绩列表",20:"战绩详情",21:"设置",22:"规则与帮助",23:"弹窗与控件状态规范板",24:"网络错误与空态规范板"}
def rel(p):return p.relative_to(R).as_posix()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def image_item(p,title=None,id=None,group=None,record=None,prompt=None):
 with Image.open(p) as im:w,h=im.size;mode=im.mode
 return {"id":id,"title":title or p.stem,"file":rel(p),"width":w,"height":h,"mode":mode,"sha256":digest(p),"record":record,"prompt":prompt,"group":group}
def page_group(i):
 return "入口" if i<=3 else "房间与匹配" if i<=8 else "牌桌与结算" if i<=12 else "角色与社交" if i<=16 else "邮件与战绩" if i<=20 else "设置与帮助" if i<=22 else "规范板"
pages=[]
for p in sorted((R/"designs/ui/full-suite").rglob("*.png")):
 match=re.search(r"ui(\d{2})",p.name,re.I)
 if not match or any(k in p.stem.lower() for k in ["source","rejected","draft","old","attempt"]):continue
 i=int(match[1])
 if i not in TITLES:continue
 record=p.with_name(p.name+".generation.json")
 if not record.exists():continue
 meta=json.loads(record.read_text(encoding="utf-8-sig"))
 prompt=meta.get("prompt")
 if isinstance(prompt,dict):prompt=prompt.get("file")
 if prompt and (":" in prompt):prompt=rel(Path(prompt))
 title=TITLES[i]
 if "success" in p.name:title+=" · 匹配成功"
 if "casual-match" in p.name:title+=" · 匹配中"
 if "draw-result" in p.name:title="流局结算状态"
 if "mail-claimed" in p.name:title+=" · 已领取"
 pages.append(image_item(p,title,"UI%02d"%i,page_group(i),rel(record),prompt))
pages.sort(key=lambda x:(x["id"],x["file"]))
components=[]
cm=R/"assets/ui/manifest.json"
if cm.exists():
 compdata=json.loads(cm.read_text(encoding="utf-8-sig"))
 for a in compdata["assets"]:
  item=image_item(R/a["file"],a.get("name",a["id"]),a["id"],"通用组件" if a["group"]=="common" else "对局组件",a.get("record"))
  item["nineSlice"]=a.get("nineSlice");item["anchor"]=a.get("anchor");item["qaStatus"]=a.get("status")
  components.append(item)
characters=[]
char_names={"welcome-daotong":"迎宾道童 · 透明全身","avatar-daotong":"金带道童","avatar-healer":"银发医师","avatar-master":"白眉老道","avatar-swordswoman":"黑发侠女"}
for stem,name in char_names.items():
 p=R/"assets/characters"/(stem+".png")
 if p.exists():
  rec=p.with_name(p.name+".generation.json")
  if not rec.exists():rec=p.with_name(p.name+".derived.json")
  characters.append(image_item(p,name,group="透明立绘" if stem=="welcome-daotong" else "座位头像",record=rel(rec) if rec.exists() else "assets/characters/manifest.json"))
tiles=[]
tile_manifest=R/"assets/tiles/manifest.json"
tile_face_count=0
if tile_manifest.exists():
 tm=json.loads(tile_manifest.read_text(encoding="utf-8-sig"))
 tile_face_count=len(tm["tiles"])
 labels={"characters":"万子","dots":"筒子","bamboo":"条子","winds":"字牌","dragons":"字牌"}
 for t in tm["tiles"]:
  tiles.append(image_item(R/t["file"],t["label"],t["id"],labels.get(t["suit"],"字牌"),t["record"]))
 for key,label in [("blank","空白牌胚"),("back","统一牌背")]:
  t=tm["base"][key];tiles.append(image_item(R/t["file"],label,group="基础牌材",record=t["record"]))
 for p2 in sorted((R/"assets/tiles/states").glob("*.png")):
  record=p2.with_name(p2.name+".generation.json")
  tiles.append(image_item(p2,group="牌面状态",record=rel(record) if record.exists() else "assets/tiles/manifest.json"))
ids={x["id"] for x in pages}
states=json.loads((R/"work/full_ui/required-states.json").read_text(encoding="utf-8-sig"))
state_rows=[{"state":k,"uiIds":v,"files":[p["file"] for p in pages if p["id"] in v],"status":"mapped" if all(i in ids for i in v) else "pending"} for k,v in states.items()]
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

manifest={"schemaVersion":1,"project":"麻将 UI 美术","generatedAt":datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat(),"contract":"docs/FULL_UI_SCOPE.md","contractCompleteCount":len(ids),"missingIds":["UI%02d"%i for i in range(1,25) if "UI%02d"%i not in ids],"pages":pages,"components":components,"characters":characters,"tiles":tiles,"tileFaceCount":tile_face_count,"states":state_rows,"scope":"美术与接入资料；不代表真实客户端/服务端验收","modelEvidence":"配置目标GPT Image 2.5 Sunburst/max；工具未披露的实际值保持null","sourceManifests":domain_manifests,"domainStateCoverage":domain_state_coverage,"browserVerification":{"status":"not_run_policy_blocked","reason":"内置浏览器URL策略拒绝file://；未采用替代浏览器/本地HTTP服务器绕过。已进行本地文件/脚本静态验证。"},"deliveryStatus":"pending_final_validation"}
(R/"exports").mkdir(exist_ok=True)
(R/"exports/ui-delivery-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
template=(R/"work/full_ui/gallery-template.html").read_text(encoding="utf-8-sig")
(R/"index.html").write_text(template.replace("__DELIVERY_DATA__",json.dumps(manifest,ensure_ascii=False).replace("</","<\\/")),encoding="utf-8")
print(json.dumps({"pages":len(pages),"contractIds":len(ids),"missingIds":manifest["missingIds"],"components":len(components),"characters":len(characters),"tiles":len(tiles)},ensure_ascii=False))

