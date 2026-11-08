from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib
R=Path(r"D:\work\majiang-image")
D=R/"designs/ui/full-game/modules"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
notes={
"ui28-announcement":["标题公告/欢迎来到牌桌、2026-10-26及三句正文清楚；有返回大厅和关闭；可选通用模块与示例数据标注可见。","卷轴和麻将装饰未遮挡正文，未添加领取/收费内容。"],
"ui29-reward-pending":["头像框×1、收藏徽章×1及两处待领取标记清楚；领取奖励为可用玉绿主按钮，返回大厅可用。","当前只有待领取状态，无已领取回执或成功勾记；奖励内容为展示示例且可选模块脚注可见。"],
"ui29-reward-claimed":["两项附件均为已领取并带勾，主按钮灰色禁用仅显示已领取，另有领取成功回执；返回大厅和关闭仍可用。","未残留待领取/活跃领取奖励动作；同一礼盒与两项附件保持一致，两态分别交付。","本编辑返回原生1671×941，比待领态宽度少1像素；未裁切/放大或伸缩改写原生文件，接入时按独立原生文本与控件布局。"],
"ui30-achievements":["已解锁1/1满进度、进行中3/10约30%进度、未解锁0/5空进度匹配；三行名称/说明和返回关闭均清楚。","未把未解锁项画成可领奖励；可选模块示例数据脚注可见。"],
"ui31-ranking":["前三名与第4/5名及本人第12位清楚，+320/+260/+180/+120/+80均朱砂红，-12为玉绿，数字符号完整。","四角色身份沿用头像母版；返回关闭和可选示例标注可见，无现金或商业奖励。"],
"ui32-item-collection":["装扮体验券×2未使用、收藏礼盒×1已选中、太极徽章×1使用中及空槽完整可见。","右详情名称/图标与选中礼盒一致，使用按钮对应礼盒而非使用中的徽章；返回关闭与可选示例标注可见。"]
}
pages=[]
for p in sorted(D.glob("ui*.png")):
 rp=Path(str(p)+".generation.json");rec=read(rp)
 rec["inspection"].update({"visualStatus":"passed","notes":notes[p.stem],"unresolvedIssues":[],"styleConsistency":"passed","chineseLegibility":"passed","stateSemantics":"passed","safeArea":"passed"})
 rec["status"].update({"readyForReview":True,"artworkQaPassed":True})
 if p.stem=="ui29-reward-claimed":
  rec["requestedDimensionsInPrompt"]={"width":1672,"height":941}
  rec["operation"]="AI state edit"
  rec["editTarget"]={"file":"designs/ui/full-game/modules/ui29-reward-pending.png","sha256":sha(D/"ui29-reward-pending.png"),"generationRecord":"designs/ui/full-game/modules/ui29-reward-pending.png.generation.json"}
 if p.stem=="ui31-ranking":
  rec["requestedColorTokens"]={"positive":"#B52F20","negative":"#196448"}
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:assert im.size==(rec["width"],rec["height"])
 assert sha(p)==rec["sha256"]
 assert sha(R/rec["prompt"])==rec["promptSha256"]
 assert all(sha(R/x["file"])==x["sha256"] for x in rec["references"])
 assert len([x for x in rec["references"] if x["file"].startswith("references/style/")])>=2
 assert rec["actualModel"] is None and rec["actualQuality"] is None
 write(rp,rec)
 pages.append({"id":rec["uiId"],"variant":rec["variant"],"title":rec["title"],"file":rec["file"],"record":rec["file"]+".generation.json","generationRecord":rec["file"]+".generation.json","prompt":rec["prompt"],"sha256":rec["sha256"],"width":rec["width"],"height":rec["height"],"format":rec["format"],"mode":rec["mode"],"native":True,"resampled":False,"states":rec["coveredStates"],"inspection":rec["inspection"],"status":"artwork_qa_passed"})
pages.sort(key=lambda p:(p["id"],p["variant"]=="claimed"))
assert len(pages)==6 and len(set(p["id"] for p in pages))==5
manifest={"schemaVersion":1,"domain":"full_game_optional_modules","scope":"docs/UI_FULL_GAME.md","rootScope":"docs/FULL_GAME_ART_SCOPE.md","generatedAt":datetime.now(timezone(timedelta(hours=-4))).isoformat(),"count":6,"imageCount":6,"contractPageCount":5,"completedIds":["UI28","UI29","UI30","UI31","UI32"],"pages":pages,"stateCoverage":[{"state":s,"sourceId":p["id"],"variant":p["variant"],"file":p["file"]} for p in pages for s in p["states"]],"mutuallyExclusiveStates":{"UI29":{"pending_claim":"designs/ui/full-game/modules/ui29-reward-pending.png","claimed":"designs/ui/full-game/modules/ui29-reward-claimed.png","transition":"仅收到真实成功回执后由pending_claim切换claimed；禁止重复领取。"}},"integrationNotes":["公告、奖励、成就、排行及收藏为可选通用模块；示例数据不代表产品已开启或真实账号。","UI29是同一个合同ID的两张互斥独立状态，不能同时显示待领与已领。","UI31正积分朱砂红、负积分玉绿；保留正负号，不以颜色单独表达增减。","UI32右侧使用按钮对应选中的收藏礼盒，使用中的太极徽章不同时成为当前使用动作目标。","所有文字和进度应由客户端原生文本与真实数据驱动；整屏为美术规范，不是客户端服务完成证明。","UI29已领取原生1671×941，其他五张1672×941。未通过缩放伪造一致原生尺寸。"],"validation":{"pngIntegrity":"passed","imageHashes":"passed","promptHashes":"passed","referenceHashes":"passed","twoPrimaryReferencesAttached":"passed","visualReview":"passed","actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露可核实版本/质量"},"delivery":{"localOnly":True,"uploaded":False,"clientIntegrated":False,"userApproved":False}}
write(D/"manifest.json",manifest)
qa={"scope":"UI28–UI32 六张独立图","timestamp":manifest["generatedAt"],"imageCount":6,"contractIds":manifest["completedIds"],"checks":[{"file":p["file"],"sha256":p["sha256"],"result":"passed","notes":p["inspection"]["notes"]} for p in pages],"technicalValidation":manifest["validation"],"externalIndependentQA":"work/full-game-ui/independent-qa.json","unresolvedIssues":[]}
write(D/"qa.json",qa)
doc="# 可选通用模块 UI28–UI32 检查\n\n已完成5个合同ID、6张独立原生成图；UI29待领与已领分开。所有图片均实际查看，中文、控件层级、示例标注、返回/关闭及状态语义通过；图片/提示词/实际参考哈希与PNG完整性通过。\n\n| ID | 画面 | 原生尺寸 | 检查 |\n|---|---|---|---|\n"
for p in pages:doc+=f"| {p['id']} | [{p['title']}]({Path(p['file']).name}) | {p['width']}×{p['height']} | 通过 |\n"
doc+="\n## 关键状态\n\n- 奖励：待领只显示可用领取奖励；已领只显示禁用已领取及成功回执，禁止叠加。\n- 成就：1/1已解锁、3/10进行中、0/5未解锁，进度条匹配。\n- 排行：前三与本人位置完整；正分朱砂红、负分玉绿，正负号保留。\n- 收藏：普通券、选中礼盒、使用中徽章、空槽齐全；详情和使用按钮对应礼盒。\n\nUI29已领原生宽度1671，其他为1672，均高941；未拉伸或放大。全套实际型号/质量未由内置工具披露，继续记录null。可选模块和示例文案不代表已确认运营或经济系统；本域未修改旧文件、根README、总画廊或exports。\n"
(D/"QA.md").write_text(doc,encoding="utf-8")
print(json.dumps({"count":6,"manifest":"designs/ui/full-game/modules/manifest.json","hashes":{Path(p["file"]).name:p["sha256"] for p in pages}},ensure_ascii=False))

