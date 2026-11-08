from pathlib import Path
import json
R=Path(r"D:\work\majiang-image")
p=R/"work/full_ui/build_gallery.py";s=p.read_text(encoding="utf-8-sig")
start=s.index("tiles=[]\n")
end=s.index("ids={x[",start)
s=s[:start]+'''tiles=[]
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
''' +s[end:]
s=s.replace('"tileFaceCount":0','"tileFaceCount":tile_face_count')
s=s.replace('if "matching" in p.name:title+=" · 匹配中"','if "casual-match" in p.name:title+=" · 匹配中"\n if "draw-result" in p.name:title="流局结算状态"\n if "mail-claimed" in p.name:title+=" · 已领取"')
p.write_text(s,encoding="utf-8")
doc=R/"docs/UI_INTEGRATION.md";s=doc.read_text(encoding="utf-8-sig")
s+='''

## 通用色彩与积分语义

| Token | 推荐值 | 用途 |
|---|---|---|
| score.positive | #B52F20 朱砂红 | 正积分，数值保留 + 号 |
| score.negative | #196448 玉绿 | 负积分，数值保留 − 号 |
| score.neutral | #6F6654 暖灰褐 | 0分、不变、说明文字 |
| action.primary | #165B4A 玉绿 | 主要操作底色 |
| text.primary | #183D35 深玉绿 | 正文与次操作文字 |
| surface.paper | #FFF9E9 象牙米白 | 信息面板与卡片 |
| border.gold | #BCA16A 暖金 | 边框与分隔 |
| state.disabled | #A8A18E 灰米色 | 不可用控件及文字 |

积分颜色语义在单局/整场结算、战绩列表/详情中一致。正负号与文字同时表达结果，不能只用颜色区分。生成图存在手绘明暗，以上为动态原生文字与客户端主题的规范值，不把截图每个像素当作精确色值。
'''
doc.write_text(s,encoding="utf-8")
tokens={"score":{"positive":"#B52F20","negative":"#196448","neutral":"#6F6654"},"action":{"primary":"#165B4A"},"text":{"primary":"#183D35"},"surface":{"paper":"#FFF9E9"},"border":{"gold":"#BCA16A"},"state":{"disabled":"#A8A18E"}}
(R/"config/ui-tokens.json").write_text(json.dumps(tokens,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Gallery uses canonical tile manifest and includes score tokens.")

