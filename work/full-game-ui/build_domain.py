from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import hashlib,json
R=Path(r'D:\work\majiang-image')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(s): return json.loads((R/s).read_text(encoding='utf-8'))
def write(s,d): (R/s).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
core=read('designs/ui/full-game/core/manifest.json'); modules=read('designs/ui/full-game/modules/manifest.json'); components=read('assets/ui/full-game/components/manifest.json')
pages=[]
for d in core['assets']+modules['pages']:
 p=R/d['file']; im=Image.open(p); assert sha(p)==d['sha256']; assert [im.width,im.height]==[d['width'],d['height']]
 rec=d.get('record',d.get('generationRecord')); record=read(rec)
 assert record['actualModel'] is None and record['actualQuality'] is None
 pages.append({'id':d.get('uiId',d.get('id')),'title':d['title'],'file':d['file'],'record':rec,'recordSha256':sha(R/rec),'prompt':d['prompt'],'sha256':d['sha256'],'width':d['width'],'height':d['height'],'mode':d['mode'],'native':True,'resampled':False,'states':d.get('coveredStates',d.get('states')),'status':'passed','optionalModule':d.get('uiId',d.get('id')) in ['UI28','UI29','UI30','UI31','UI32']})
assert len(pages)==11
assert len({p['id'] for p in pages})==8
assert len(components['assets'])==22
for c in components['assets']: assert sha(R/c['file'])==c['sha256']
theme_specs=[
 ('jade-cloud','青玉云纹','青玉云纹','assets/ui/gameplay/table-background.png','太极青玉','青玉牌背','assets/tiles/tile-back.png'),
 ('ivory-bamboo','竹影清风','竹韵米白','assets/scenes/full-game/table-ivory-bamboo.png','竹韵墨青','竹韵牌背','assets/branding/full-game/tile-back-ivory-bamboo.png'),
 ('moon-lotus','月白云海','月莲青蓝','assets/scenes/full-game/table-moon-lotus.png','流云暖金','月莲牌背','assets/branding/full-game/tile-back-moon-lotus.png')]
bindings=[]
for id,concept,name,table,backConcept,backName,back in theme_specs:
 assert (R/table).is_file() and (R/back).is_file()
 bindings.append({'id':id,'table':{'conceptLabelInUI25':concept,'clientLabel':name,'file':table,'sha256':sha(R/table)},'tileBack':{'conceptLabelInUI25':backConcept,'clientLabel':backName,'file':back,'sha256':sha(R/back)}})
write('assets/ui/full-game/theme-bindings.json',{'schemaVersion':1,'scope':'UI25 live-client theme art mapping','themes':bindings,'notes':['UI25 was generated before these final theme assets and remains a layout example. Its swatches are illustrative, not exact pixel previews of the final texture files.','For client implementation use the clientLabel and actual texture file above for each card and table preview; do not crop the illustrated concept swatches as exported texture assets.','No theme prices or ownership rules are defined.'],'clientIntegrated':False})
manifest={'schemaVersion':2,'scope':'UI25-UI32 full game supplemental UI art','contract':'docs/UI_FULL_GAME.md','status':'artwork_passed_pending_domain_final_qa','generatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'uiIds':sorted({p['id'] for p in pages}),'pageCount':11,'componentCount':22,'primaryAssetCount':33,'pages':pages,'components':components['assets'],'componentManifest':'assets/ui/full-game/components/manifest.json','compositions':'assets/ui/full-game/components/compositions.json','themeBindings':'assets/ui/full-game/theme-bindings.json','independentQA':'work/full-game-ui/independent-qa.json','sourceManifests':[{'file':f,'sha256':sha(R/f)} for f in ['designs/ui/full-game/core/manifest.json','designs/ui/full-game/modules/manifest.json','assets/ui/full-game/components/manifest.json']],'retainedEditSources':core['retainedEditSources'],'failedAttemptRecords':core['failedAttemptRecords'],'nativeDimensionsNote':'9 pages 1672x941; UI25 and UI29 claimed 1671x941. No resampling of full page outputs.','actualModel':None,'actualQuality':None,'clientIntegrated':False,'uploaded':False,'userApproved':False,'limitations':['Static art and integration specifications only; not an implemented game client.','Optional modules and sample data do not imply confirmed product features.','No browser interaction testing due file URL policy block.'],'blockingIssues':[]}
write('designs/ui/full-game/manifest.json',manifest)
write('assets/ui/full-game/manifest.json',{'schemaVersion':2,'status':'passed','scope':'additional full game UI components','assetCount':22,'assets':components['assets'],'componentManifest':'assets/ui/full-game/components/manifest.json','compositions':'assets/ui/full-game/components/compositions.json','themeBindings':'assets/ui/full-game/theme-bindings.json','pageManifest':'designs/ui/full-game/manifest.json','actualModel':None,'actualQuality':None,'clientIntegrated':False})
lines=['# 全游戏补充 UI 美术 v2','', '8个页面ID，11张独立整屏，22项透明组件。无旧包覆盖、无上传。','', '| ID | 图稿 | 原生尺寸 |','|---|---|---|']
for p in pages: lines.append(f"| {p['id']} | [{p['title']}]({Path(p['file']).relative_to('designs/ui/full-game').as_posix()}) | {p['width']}×{p['height']} |")
lines.extend(['','完整索引见 `manifest.json`。逐图同名 `.generation.json` 含实际提示词、参考、原生尺寸与检查。','', 'UI25原始装扮图及UI27原始选牌图仅为AI编辑来源，不计交付。角落清理失败尝试已被最终页脚版本替代，保留文字记录而不重复保留无用像素。','', 'UI25为先行布局示例；实际主题名与素材见 `assets/ui/full-game/theme-bindings.json`，客户端须用该映射中的真实桌面/牌背生成预览，不裁切概念稿小样。','', '接入说明：`docs/UI_FULL_GAME.md`。全游戏其他美术域及v2总包由主任务另行整合。'])
(R/'designs/ui/full-game/README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(R/'assets/ui/full-game/README.md').write_text('# 全游戏补充 UI 组件\n\n22项透明PNG及7组组合映射见 `components/README.md`、`components/manifest.json`、`components/compositions.json`。全部保留等比；文字原生绘制。\n\n装扮接入使用 `theme-bindings.json` 中真实桌面/牌背路径与客户端名称。页面图稿见 `designs/ui/full-game/manifest.json`。\n\n箭头锚点以完整396×334画布坐标(350,313)为尖端，归一化约(0.883838,0.937126)。按钮族引用旧域primary，重复领取及禁用状态由客户端阻止交互。\n',encoding='utf-8')
doc=R/'docs/UI_FULL_GAME.md'; text=doc.read_text(encoding='utf-8')
marker='## 完成与最终接入补充'
text=text.split(marker)[0].replace('本域制作进行中；最终数量、哈希、检查结论将在完成后写入本域清单。','本域制作已完成，最终数量、哈希和检查见 `designs/ui/full-game/manifest.json` 与独立QA。')
text+='\n'+marker+'\n\n- 8个ID、11张独立整屏、22项新透明组件；4张组件母版与必要编辑来源保留。\n- UI27为连续三步；UI29为互斥两态。9张原生1672×941，装扮设置及已领取图原生1671×941，未拉伸统一尺寸。\n- 组件全部等比缩放，7组合/12状态族，23项旧组件引用。箭头尖端为原生(350,313)，依完整396×334画布归一化。\n- 总清单：`designs/ui/full-game/manifest.json`；组件：`assets/ui/full-game/manifest.json`；独立QA：`work/full-game-ui/independent-qa.json`。\n\nUI25先于新主题资源生成，整屏中的“竹影清风／月白云海”等名称与小样为布局示例。接入时以 `assets/ui/full-game/theme-bindings.json` 的 `clientLabel` 和真实图像为准：青玉云纹、竹韵米白、月莲青蓝桌面与青玉、竹韵、月莲牌背。该表显式保存概念名与客户端名映射；使用实际纹理填装扮卡及预览，不把概念小样冒充实际导出纹理。\n'
doc.write_text(text,encoding='utf-8')
print(json.dumps({'pages':len(pages),'components':len(components['assets']),'manifestSha256':sha(R/'designs/ui/full-game/manifest.json'),'themeBindingsSha256':sha(R/'assets/ui/full-game/theme-bindings.json')},ensure_ascii=False))
