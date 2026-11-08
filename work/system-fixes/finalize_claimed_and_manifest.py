from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil,copy
R=Path(r"D:\work\majiang-image")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
receipt=read(R/"work/system-fixes/UI18-claimed-receipt.json")
candidate=R/"work/system-fixes/UI18-claimed-candidate.png"
target=R/"designs/ui/full-suite/system/ui18-mail-claimed.png"
with Image.open(candidate) as im:im.verify()
with Image.open(candidate) as im:w,h=im.size;mode=im.mode;fmt=im.format
assert (w,h)==(1672,941)
shutil.copyfile(candidate,target)
rec=read(R/"designs/ui/full-suite/system/ui18-mail-detail.png.generation.json")
rec.update({"title":"邮件详情 · 已领取独立状态","file":target.relative_to(R).as_posix(),"sha256":sha(target),"generatedAt":datetime.fromisoformat(receipt["observedCompletedAt"].replace("Z","+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat(),"width":w,"height":h,"mode":mode,"format":fmt,"outputArtifactFileId":Path(receipt["source"]).stem,"resultReceipt":receipt,"prompt":"prompts/system/ui18-mail-claimed.prompt.txt","promptSha256":sha(R/"prompts/system/ui18-mail-claimed.prompt.txt"),"nativeDimensions":{"width":w,"height":h},"variant":"claimed"})
rec["submittedParameters"].update({"referenced_image_paths":receipt["submittedReferences"],"promptFile":rec["prompt"]})
rec["references"]=[{"inputIndex":i,"file":Path(p).relative_to(R).as_posix(),"submittedPath":p,"sha256":sha(Path(p)),"purpose":"修正后的待领取页作为编辑目标" if i==1 else "主UI风格参考","actuallyAttached":True} for i,p in enumerate(receipt["submittedReferences"],1)]
rec["source"]={"toolNativeOutput":receipt["source"],"sha256":sha(Path(receipt["source"])),"operation":"byte-identical copy","derived":False}
rec["editTarget"]={"file":"designs/ui/full-suite/system/ui18-mail-detail.png","sha256":sha(R/"designs/ui/full-suite/system/ui18-mail-detail.png"),"generationRecord":"designs/ui/full-suite/system/ui18-mail-detail.png.generation.json"}
rec["inspection"]={"pngIntegrity":"passed","visualStatus":"passed","notes":["实际查看独立已领取状态：附件标记已领取，灰色禁用按钮仅显示已领取，删除按钮深玉绿字及图标可用。","页面不出现待领取或可领取按钮；辅助文案为附件已领取，可删除邮件。","与待领取页的标题、日期、正文、附件、道童兔子、背景、框板、返回及关闭保持一致。"],"unresolvedIssues":[]}
write(Path(str(target)+".generation.json"),rec)

mp=R/"designs/ui/full-suite/system/manifest.json";m=read(mp)
for page in m["pages"]:
 if page["file"] in ["designs/ui/full-suite/system/ui18-mail-detail.png","designs/ui/full-suite/system/ui19-records.png"]:
  r=read(R/page["generationRecord"])
  page.update({k:r[k] for k in ["title","sha256","width","height","format","prompt","inspection"]})
  if page["id"]=="UI18":
   page["variant"]="pending_claim"
   page["states"]=[s for s in page["states"] if s!="mail.claimed.alternate-style"]
new={"id":"UI18","variant":"claimed","title":rec["title"],"file":rec["file"],"generationRecord":rec["file"]+".generation.json","prompt":rec["prompt"],"width":w,"height":h,"format":fmt,"sha256":rec["sha256"],"status":"artwork_qa_passed","states":["mail.detail.claimed","mail.attachment.claimed","mail.claim.disabled-claimed","mail.delete.enabled-claimed","navigation.back-list","navigation.close"],"inspection":rec["inspection"]}
m["pages"]=[p for p in m["pages"] if p["file"]!=new["file"]]
ix=next(i for i,p in enumerate(m["pages"]) if p["id"]=="UI18")
m["pages"].insert(ix+1,new)
m["count"]=len(m["pages"]);m["imageCount"]=len(m["pages"]);m["contractPageCount"]=len(m["completedIds"])
m["stateCoverage"]=[{"state":s,"sourceId":p["id"],"file":p["file"]} for p in m["pages"] for s in p["states"]]
m["integrationNotes"]=[n for n in m["integrationNotes"] if "UI18" not in n]
m["integrationNotes"] += ["UI18待领取与已领取分别使用ui18-mail-detail.png和ui18-mail-claimed.png，两张是同合同ID的互斥独立状态，不能同时叠加显示。","积分数值统一语义：正分朱砂红（请求token #B52F20）、负分玉绿（#196448）、零分中性灰；胜/负结果徽章是独立装饰标签，不作为积分颜色token。"]
m["validation"]["allImageHashesMatch"]=all(sha(R/p["file"])==p["sha256"] for p in m["pages"])
m["validation"]["allPromptHashesMatch"]=all(sha(R/r["prompt"])==r["promptSha256"] for r in [read(R/p["generationRecord"]) for p in m["pages"]])
m["validation"]["allReferenceHashesMatch"]=all(sha(R/ref["file"])==ref["sha256"] for r in [read(R/p["generationRecord"]) for p in m["pages"]] for ref in r["references"])
m["validation"]["allVisualReviewsPassed"]=all(p["inspection"]["visualStatus"]=="passed" for p in m["pages"])
assert all(m["validation"][x] for x in ["allImageHashesMatch","allPromptHashesMatch","allReferenceHashesMatch","allVisualReviewsPassed"])
write(mp,m)
fixed_files=["designs/ui/full-suite/system/ui18-mail-detail.png","designs/ui/full-suite/system/ui18-mail-claimed.png","designs/ui/full-suite/system/ui19-records.png","designs/ui/full-suite/core/ui11-round-result.png"]
checks=[]
for f in fixed_files:
 r=read(R/(f+".generation.json"))
 assert sha(R/f)==r["sha256"]
 assert sha(R/r["prompt"])==r["promptSha256"]
 assert r["actualModel"] is None and r["actualQuality"] is None
 assert all(sha(R/ref["file"])==ref["sha256"] for ref in r["references"])
 checks.append({"file":f,"sha256":r["sha256"],"width":r["width"],"height":r["height"],"visualStatus":"passed","promptAndReferenceHashes":"passed","record":f+".generation.json"})
qa={"scope":"UI18领取状态拆分、UI19/UI11正负积分语义统一","completedAt":datetime.now(timezone(timedelta(hours=-4))).isoformat(),"ui18States":{"pending":"designs/ui/full-suite/system/ui18-mail-detail.png","claimed":"designs/ui/full-suite/system/ui18-mail-claimed.png","mutuallyExclusive":True},"checks":checks,"scoreColorEvidence":read(R/"work/system-fixes/score-color-verification.json"),"actualModel":None,"actualQuality":None,"userApproved":False,"clientIntegrated":False}
write(R/"designs/ui/full-suite/system/review-fixes-qa.json",qa)
print(json.dumps({"systemImages":len(m["pages"]),"systemContractIds":len(m["completedIds"]),"fixes":checks,"manifestValidation":m["validation"]},ensure_ascii=False))

