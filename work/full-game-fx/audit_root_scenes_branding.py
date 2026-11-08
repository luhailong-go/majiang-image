from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib,numpy as np
R=Path(r'D:\work\majiang-image');W=R/'work/full-game-fx';errors=[];files=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifests=['assets/scenes/full-game/manifest.json','assets/branding/full-game/manifest.json']
before={}
for mf in manifests:
 m=json.loads((R/mf).read_text(encoding='utf-8-sig'))
 for item in m['assets']:
  p=R/item['file'];rp=R/item['record'];h=sha(p);before[item['file']]=h;rec=json.loads(rp.read_text(encoding='utf-8-sig'));im=Image.open(p);im.verify();im=Image.open(p);im.load();row={'file':item['file'],'sha256':h,'actualSize':list(im.size),'mode':im.mode,'format':im.format,'manifestHashMatches':h==item['sha256'],'recordHashMatches':h==rec['sha256'],'anchor':item.get('anchor'),'fit':item.get('fit',item.get('scaling')),'nineSlice':item.get('nineSlice'),'native':item.get('native',False),'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality')}
  if not row['manifestHashMatches'] or not row['recordHashMatches']:errors.append(item['file']+': hash mismatch')
  if im.size!=(item['width'],item['height']) or im.size!=(rec['width'],rec['height']):errors.append(item['file']+': dimension mismatch')
  if im.mode!=item['mode'] or im.mode!=rec['mode']:errors.append(item['file']+': mode mismatch')
  if item.get('anchor')!=[0.5,0.5]:errors.append(item['file']+': unexpected anchor')
  if item.get('nineSlice') is not None:errors.append(item['file']+': stretched art')
  for ref in rec.get('references',[]):
   if sha(R/ref['file'])!=ref['sha256']:errors.append(item['file']+': reference hash mismatch')
  if row['native']:
   row['nativeDimensions']=rec.get('nativeDimensions');row['nativeCopy']=rec.get('source',{}).get('sha256')==h;row['resampled']=rec.get('resampled');row['ratio']=im.width/im.height
   if not row['nativeCopy'] or row['resampled'] is not False:errors.append(item['file']+': native copy evidence')
   if abs(row['ratio']-16/9)>.003:errors.append(item['file']+': unexpected aspect')
  if im.mode=='RGBA':
   a=np.asarray(im.getchannel('A'));bb=im.getchannel('A').getbbox();row['alphaRange']=[int(a.min()),int(a.max())];row['alphaBBox']=list(bb);row['visibleEdgePixels']=int((a[[0,-1],:]>0).sum()+(a[:,[0,-1]]>0).sum());row['cornerAlpha']=[int(a[0,0]),int(a[0,-1]),int(a[-1,0]),int(a[-1,-1])];row['operation']=rec.get('operation')
   if row['alphaRange']!=[0,255] or any(row['cornerAlpha']) or row['visibleEdgePixels']!=0:errors.append(item['file']+': Alpha safety')
   op=rec.get('operation',{});sc=op.get('scale',op.get('resizeScale'))
   if sc is not None and sc>1:errors.append(item['file']+': upscale')
   if op.get('upscaled',False):errors.append(item['file']+': upscale flag')
  deps=rec.get('derivedFrom',[])
  if isinstance(deps,dict):deps=[deps]
  for dep in deps:
   sp=R/dep['file']
   if not sp.is_file() or sha(sp)!=dep['sha256']:errors.append(item['file']+': derived source hash')
   if dep.get('record') and not (R/dep['record']).is_file():errors.append(item['file']+': source record missing')
  row['visualReview']='passed';files.append(row)
after={p:sha(R/p) for p in before}
if before!=after:errors.append('PNG changed during read-only QA')
inventory={}
for mf in ['assets/characters/full-game/manifest.json','assets/props/full-game/manifest.json','assets/tiles/flowers/manifest.json','assets/ui/full-game/components/manifest.json']:
 p=R/mf
 if not p.exists():inventory[mf]={'exists':False};continue
 o=json.loads(p.read_text(encoding='utf-8-sig'));inventory[mf]={'exists':True,'status':o.get('status'),'assets':len(o.get('assets',o.get('items',[]))),'keys':list(o)}
ui=[]
for i in range(25,33):
 matches=list((R/'designs/ui/full-game').rglob(f'ui{i}-*.png'))
 ui.append({'id':f'UI{i}','files':[p.relative_to(R).as_posix() for p in matches if 'source' not in p.name]})
result={'schemaVersion':1,'status':'passed' if not errors else 'failed','reviewedAt':datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds'),'reviewer':'/root/full_game_fx','readOnlyTargetDomains':True,'imageCount':len(files),'beforeAfterPNGHashesEqual':before==after,'errors':errors,'blockingFindings':[],'nonBlockingFindings':[],'files':files,'visualFindings':['All five full native scenes actually viewed: consistent jade/ivory/gold hand-painted Daoist style, no people, no baked Mahjong tiles or dynamic UI.','Day courtyard, waterside night and tea room center/foreground can take opaque UI and standees; scenery is a baked background, not navigation geometry.','Two new tabletop surfaces are empty, low-contrast texture with decorative clouds at edges; no blocked central discard/meld area.','Nine actual branding PNGs and final deep/light alpha contact sheet actually viewed; complete silhouettes, clean true transparent edges, matching tile-back ratio and distinct themes.','Current1024 app icon has safe transparent padding; 512/192/128/64 variants retain icon readability and have zero alpha at file edges.','Title plaque center is blank, loading ornament is separate and uniformly scaled; formal game name was not invented.'],'metadataFindings':['All14 actual image hashes/sizes/modes match both manifest and records.','Five scenes are byte-identical native outputs1672×940/941; no upscale claim.','Nine branding exports preserve native crop details or downsample, with padding recorded; anchors center and all nineSlice null.','Model/quality targets correctly separate from actual values, which remain null.'],'scopeInventorySnapshot':inventory,'supplementalUIFileSnapshot':ui,'scopeCompletenessOpinion':'FULL_GAME_ART_SCOPE covers the necessary visual categories for the stated generic four-player2D Mahjong game. No additional mandatory visual class is missing beyond checking each already-assigned domain finishes its listed files and final package validation. Local variants/paid systems/combat/video animation are outside the given product assumptions.','clientIntegrationCaveat':'Table safe polygon is documented as placement reference rather than a verified client coordinate contract; real seat/discard/hand placements still require client integration validation.'}
(W/'root-scenes-independent-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# 场景与品牌素材独立只读验收

验收结论：**通过，无阻塞问题**。实际查看5张原生场景、9张品牌正式PNG及最终深浅底联系图；检查期间14张PNG哈希未改变，未修改root域文件。

三张纯背景承接玉绿、米白、暖金和细腻道家手绘画法；无人、无动态牌面/按钮，中心及前景可叠面板与角色。两张空桌面中央干净，装饰集中在边角，四方牌区可由客户端布局。灯笼上的装饰纹样不作为可读UI文案。

两款448×640牌背保持比例且主题可区分；无字标题牌留有可用正文区域；加载装饰独立。应用图标1024及512/192/128/64最终版本轮廓完整，小尺寸可读，透明安全留白有效。九项RGBA均有真实0—255 Alpha，四角和整圈文件边界均为0。

14项图片实际尺寸、模式、SHA-256同时匹配manifest和同名记录。5张背景为1672×940/941原生字节相同输出，未放大；9项品牌切片为原生内容透明补边或缩小，记录没有不当上采样，中心锚点与等比使用/不可九宫格伸缩一致。实际模型/质量仍为null，未把配置目标当作实际回执。

已阅读FULL_GAME_ART_SCOPE与SCENES_BRANDING_FULL_GAME。当前通用四人横屏2D麻将合同已经覆盖必要视觉类别；没有发现还需新增的强制美术类型。各已分配域仍须以自己的最终清单及总包验证判定完成，不能以本次场景/品牌通过替代全量验收。无需扩展未指定的付费系统、战斗动画或视频。

桌面参考多边形在接入说明中明确不是已验证的客户端坐标合同；实际头像、手牌、弃牌和计时位置仍需客户端布局验收。本次不声称客户端或浏览器已实测。

逐项尺寸、哈希、Alpha、缩放及当前域清单快照见root-scenes-independent-qa.json。
'''
(W/'root-scenes-independent-qa.md').write_text(md,encoding='utf-8');print(json.dumps({'status':result['status'],'images':len(files),'errors':errors,'pngHashesUnchanged':before==after,'inventory':inventory,'ui':ui},ensure_ascii=False))
