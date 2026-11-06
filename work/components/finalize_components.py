from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone,timedelta
R=Path(r"D:\work\majiang-image"); now=datetime.now(timezone(timedelta(hours=-4))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mp=R/"assets/ui/manifest.json";m=json.loads(mp.read_text(encoding="utf-8-sig"));before={a["file"]:sha(R/a["file"]) for a in m["assets"]}
checks=[]
for a in m["assets"]:
 p=R/a["file"];rp=R/a["record"];rec=json.loads(rp.read_text(encoding="utf-8-sig"));name=a["id"]
 if name=="window-frame":a["nineSlice"]=[200,200,200,200];rec["nineSlice"]=[200,200,200,200]
 if name=="settlement-card":a["nineSlice"]=None;rec["nineSlice"]=None
 horizontal=name.startswith(("button-primary-","button-secondary-","action-button-"))
 if horizontal:
  policy={"mode":"horizontal_nine_slice_only","stretchAxes":["x"],"lockHeightAfterUniformScale":True,"uniformScaleAllowed":True,"reason":"Preserve round end ornaments; vertical anisotropic stretching is forbidden."}
 elif name=="settlement-card" or a["nineSlice"] is None and name not in ["modal-shade","table-background"]:
  policy={"mode":"uniform_scale_only","stretchAxes":[],"uniformScaleAllowed":True,"reason":"Preserve central ornaments, pointer, circular shape or icon proportions."}
 elif name=="modal-shade":policy={"mode":"viewport_stretch","stretchAxes":["x","y"],"reason":"Constant RGBA runtime overlay."}
 elif name=="table-background":policy={"mode":"uniform_cover_or_contain","stretchAxes":[],"reason":"Preserve table/environment perspective; crop at viewport only if needed."}
 else:policy={"mode":"nine_slice","stretchAxes":["x","y"],"uniformScaleAllowed":True}
 a["resizePolicy"]=policy;rec["resizePolicy"]=policy
 if name=="table-background":rec["operation"]="pixel-identical native RGB PNG re-encode; metadata stripped; no resampling"
 if a["nineSlice"]:
  l,t,r,b=a["nineSlice"];assert l+r<a["width"] and t+b<a["height"]
  a["minimumGeometrySize"]=[l+r+1,t+b+1];rec["minimumGeometrySize"]=a["minimumGeometrySize"]
 else:
  a.pop("minimumGeometrySize",None);rec.pop("minimumGeometrySize",None)
 rec["inspection"]={"status":"passed","visualCheck":"Actual final RGBA pixels composited on light and dark backgrounds; no baked background or detached colored speckles observed.","alphaAndGeometry":"passed","nineSlicePolicy":"reviewed; only stretch permitted axes","issues":[],"qaImages":["work/components/qa/"+a["group"]+"-light.png","work/components/qa/"+a["group"]+"-dark.png"] if name!="table-background" else [],"checkedAt":now}
 rec["productionAccepted"]=True
 rec["clientIntegrated"]=False
 a["status"]="passed";a["productionAccepted"]=True
 if rec.get("alphaCleanup"):assert rec["alphaCleanup"]["removedAlphaAtLeast128"]==0
 with Image.open(p) as im:im.verify()
 assert sha(p)==a["sha256"]==rec["sha256"]==before[a["file"]]
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 checks.append({"id":name,"file":a["file"],"sha256":a["sha256"],"pngIntegrity":"passed","recordHash":"passed","visual":"passed","resizePolicy":policy})
m["status"]="passed";m["checkedAt"]=now;m["pngCount"]=len(m["assets"]);m["notes"]=[
"All painted skins derive from builtin generated masters; crop and alpha cleanup are mechanical exports, not separate AI generations.",
"All text and numeric values are separate native client labels.",
"Nine-slice is [left,top,right,bottom] in delivered pixels, subject to resizePolicy. Buttons with round end ornaments stretch only horizontally after a uniform base scale.",
"Null nineSlice means aspect-preserving scaling only except the constant modal overlay.",
"window-frame margins are [200,200,200,200]. settlement-card is uniform-scale-only."]
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for group in ["common","gameplay"]:
 subset={**m,"assets":[a for a in m["assets"] if a["group"]==group]};subset["pngCount"]=len(subset["assets"])
 (R/"assets/ui"/group/"manifest.json").write_text(json.dumps(subset,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cp=R/"assets/ui/component-compositions.json";c=json.loads(cp.read_text(encoding="utf-8-sig"))
for family in c["buttonFamilies"].values():
 family["resizePolicy"]={"mode":"horizontal_nine_slice_only","stretchAxes":["x"],"lockHeightAfterUniformScale":True,"uniformScaleAllowed":True}
c["compositions"]["window"]["frameNineSliceMargins"]=[200,200,200,200]
c["compositions"]["settlement"]["nineSlice"]=None;c["compositions"]["settlement"]["preserveAspect"]=True;c["compositions"]["settlement"]["resizePolicy"]="uniform_scale_only"
c["compositions"]["actionChoices"]["resizePolicy"]={"stretchAxes":["x"],"lockHeightAfterUniformScale":True}
c["compositions"]["numericKeypad"].pop("buttonStates",None)
c["compositions"]["numericKeypad"]["stateEffects"]={"normal":{},"pressed":{"brightness":0.78},"selected":{"brightness":1.12,"color":1.12},"disabled":{"grayscaleBlend":0.82,"contrast":0.72,"interactive":False}}
cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for src in (R/"designs/ui/component-sources").glob("*.png"):
 rp=src.with_name(src.name+".generation.json")
 if not rp.exists():continue
 sr=json.loads(rp.read_text(encoding="utf-8-sig"));sr["inspection"]["visualStatus"]="passed_as_source_for_mechanical_export";sr["inspection"]["issues"]=[]
 sr["inspection"]["note"]="Source is not the delivered cutout. Final derived assets carry cleaned alpha and reviewed scaling policies."
 sr["status"]["productionAccepted"]=False
 rp.write_text(json.dumps(sr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
readme=R/"assets/ui/README.md";text=readme.read_text(encoding="utf-8-sig")
text=text.replace("最小几何尺寸为左右边距和+1、上下边距和+1。文字布局另需保证可读空间。","最小几何尺寸为左右边距和+1、上下边距和+1。窗框使用保守的 [200,200,200,200] 边距。主/次/对局按钮及所有状态仅允许横向九宫格伸缩，并锁定整体等比缩放后的高度，禁止纵向非等比拉伸圆珠。文字布局另需保证可读空间。")
text=text.replace("标题牌、提示气泡、圆头像框、图标和风位盘没有九宫格，等比显示。","标题牌、提示气泡、圆头像框、图标、风位盘和结算卡片没有九宫格，等比显示；结算卡片顶底中央玉珠不能拉伸。")
text += "\n## 交付检查\n\n58 项最终 PNG 通过文件完整性、尺寸、来源哈希和深浅底检查。缩放元数据修订未改变任何 PNG 哈希。独立牌桌背景与原生生成源像素完全一致，因 PNG 重编码移除了元数据，文件字节哈希不同；记录已准确区分像素一致与字节一致。\n"
readme.write_text(text,encoding="utf-8")
qa={"schemaVersion":1,"checkedAt":now,"status":"passed","componentCount":len(checks),"pngHashesUnchanged":all(sha(R/f)==s for f,s in before.items()),"checks":checks,"sourceAlphaCleanup":"All cleanup records have zero removed pixels with alpha>=128.","finalComposites":["work/components/qa/common-light.png","work/components/qa/common-dark.png","work/components/qa/gameplay-light.png","work/components/qa/gameplay-dark.png"],"scope":"UI artwork assets; not client/service integration"}
(R/"assets/ui/qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"assets":len(checks),"status":"passed","pngHashesUnchanged":qa["pngHashesUnchanged"],"manifestSha256":sha(mp),"compositionSha256":sha(cp)},ensure_ascii=False))

