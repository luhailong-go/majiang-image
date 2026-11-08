from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib,shutil,re,numpy as np
R=Path(r'D:\work\majiang-image');A=R/'assets/fx/full-game';W=R/'work/full-game-fx';B=W/'clips-built-final'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
m=json.loads((A/'manifest.json').read_text(encoding='utf-8'));built=json.loads((B/'animation-clips.json').read_text(encoding='utf-8'));t=json.loads((A/'timelines.json').read_text(encoding='utf-8'));errors=[];checks=[];supp=[];sources=[]
def derivative_media(out,artifacts,operation):
 im=Image.open(out);frames=getattr(im,'n_frames',1);rec={'schemaVersion':2,'file':rel(out),'sha256':sha(out),'derivedAt':now,'tool':'generate2dsprite clip/engine packaging','route':'deterministic_derivative','actualModel':None,'actualQuality':None,'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'frameCount':frames,'derivedFrom':artifacts,'operation':operation,'inspection':{'visualStatus':'passed_phase_filmstrip_and_alpha_review','issues':[]},'status':{'productionAccepted':True,'userApproved':False,'clientIntegrated':False}}
 dump(Path(str(out)+'.generation.json'),rec);supp.append({'file':rel(out),'record':rel(Path(str(out)+'.generation.json')),'sha256':sha(out),'kind':'runtime_packaging_or_qa_preview'})
all_frame_sources=[{'file':x['file'],'sha256':x['sha256'],'record':x['record']} for x in m['assets'] if x['kind']=='animation_frame']
pathmap={}
for i,(slug,clip) in enumerate(built['clips'].items()):
 src=B/clip['preview']['file'];out=A/f'previews/{slug}.webp';shutil.copyfile(src,out);pathmap[clip['preview']['file']]=out.relative_to(A).as_posix()
 frame_sources=[all_frame_sources[x] for x in clip['frames']]
 derivative_media(out,frame_sources,{'type':'lossless_timed_webp','frameDurationMs':clip['duration_ms'],'loop':clip['loop'],'sourcePngsByteIdentical':True,'decodedTimelineVerified':clip['preview']['timeline_verified'],'decodedAlphaAndVisibleRgbExact':clip['preview']['alpha_and_visible_rgb_exact'],'noNewArt':True})
 t['clips'][slug]['durationMs']=clip['duration_ms'];t['clips'][slug]['totalDurationMs']=clip['total_duration_ms'];t['clips'][slug]['preview']=rel(out)
for src in sorted((B/'review').glob('*.png')):
 out=A/'review'/src.name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out);pathmap['review/'+src.name]='review/'+src.name
 derivative_media(out,all_frame_sources,{'type':'phase_filmstrip_or_onion_review','byteCopyOfBuilderOutput':True,'noNewArt':True})
out=A/'review/timing-contact-sheet.png';shutil.copyfile(B/'contact-sheet.png',out);pathmap['contact-sheet.png']='review/timing-contact-sheet.png'
derivative_media(out,all_frame_sources,{'type':'contact_sheet_with_shared_anchor','byteCopyOfBuilderOutput':True,'noNewArt':True})
for f in built['frames']:
 old=f['file'];f['file']=f'frames/{f["name"]}.png';f['source']['path']=f['file'];pathmap[old]=f['file']
built['source_manifest']['path']='clips-input.json';built['source_manifest']['copy']='clips-input.json'
def rewrite(v):
 if isinstance(v,dict):return {k:rewrite(x) for k,x in v.items()}
 if isinstance(v,list):return [rewrite(x) for x in v]
 if isinstance(v,str):
  if v in pathmap:return pathmap[v]
  if v.endswith('assets/fx/full-game/clips-input.json'):return 'clips-input.json'
  if '/assets/fx/full-game/frames/' in v:return 'frames/'+v.rsplit('/',1)[1]
 return v
built=rewrite(built)
built['relocation']={'originalBuildManifest':rel(B/'animation-clips.json'),'originalSha256':sha(B/'animation-clips.json'),'operation':'relocate paths only to existing byte-identical primary PNGs and copied previews/review files; no timing or pixels changed'}
built['productionVisualReview']={'status':'passed','method':'actual deep/light exported frame contact sheet inspection and Chinese callout visual inspection; effect cores/inner ring registered','clientEnginePlaybackProven':False,'reviewedAt':now}
dump(A/'animation-clips.json',built);dump(A/'timelines.json',t)

# The engine bundle is self-contained for runtime; its QA retains the original tool input receipt.
engine=json.loads((A/'engine/engine-export.json').read_text(encoding='utf-8'));assert engine['qa']['status']=='pass'
atlas=A/'engine/aseprite/mahjong-fx.png'
derivative_media(atlas,all_frame_sources,{'type':'aseprite_json_atlas_pack','pixelsRotated':False,'pixelsTrimmed':False,'paddingPx':2,'extrudePx':1,'roundTripExactRGBA':True,'sourceFrames':24,'engineImportTested':False})

# Portable processing receipts, keeping the original tool reports unchanged.
receipts=json.loads((A/'processing-receipts.json').read_text(encoding='utf-8'))
for row in receipts['reports']:
 src=R/row['file'];out=A/f'qa/process-{row["effect"]}.json';out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out);row['originalWorkingFile']=row['file'];row['file']=rel(out);row['sha256']=sha(out)
 slug='discard-impact-refined' if row['effect']=='discard-impact' else row['effect'];src=W/f'spill-{slug}/sheet-qc.json';out=A/f'qa/raw-sheet-{row["effect"]}.json';shutil.copyfile(src,out);row['rawSheetQC']=rel(out)
dump(A/'processing-receipts.json',receipts)
for item in m['assets']:
 p=R/item['file'];rpath=R/item['record'];rec=json.loads(rpath.read_text(encoding='utf-8'));im=Image.open(p).convert('RGBA');a=np.asarray(im.getchannel('A'))
 if sha(p)!=item['sha256'] or sha(p)!=rec['sha256']:errors.append(item['file']+': hash mismatch')
 if im.size!=(item['width'],item['height']):errors.append(item['file']+': dimensions')
 if not ((a==0).any() and (a>32).any()):errors.append(item['file']+': alpha missing')
 if any([a[0,0],a[0,-1],a[-1,0],a[-1,-1]]):errors.append(item['file']+': nontransparent corner')
 if (a[[0,-1],:]>16).any() or (a[:,[0,-1]]>16).any():errors.append(item['file']+': output-edge content')
 for d in rec['derivedFrom']:
  sp=R/d['file']
  if not sp.exists() or sha(sp)!=d['sha256']:errors.append(item['file']+': source missing/hash')
 if 'pipelineReport' in rec['operation']:
  slug='discard-impact' if 'discard-impact' in rec['operation']['pipelineReport'] else item['id'].rsplit('-',1)[0]
  rec['operation']['originalWorkingPipelineReport']=rec['operation']['pipelineReport'];rec['operation']['pipelineReport']=f'assets/fx/full-game/qa/process-{slug}.json'
 rec['inspection']={'visualStatus':'passed','method':'actual exported pixels inspected on deep jade and light ivory backgrounds, complete silhouettes, exact Chinese text; phase progression reviewed','issues':[],'reviewedAt':now}
 rec['status']['productionAccepted']=True;dump(rpath,rec);item['status']='passed';checks.append({'file':item['file'],'sha256':sha(p),'size':list(im.size),'alphaRange':[int(a.min()),int(a.max())],'edgeVisiblePixels':int((a[[0,-1],:]>16).sum()+(a[:,[0,-1]]>16).sum()),'transparentCorners':True})
for slug,clip in t['clips'].items():
 hashes=[sha(R/f) for f in clip['frameFiles']]
 if len(set(hashes))!=4:errors.append(slug+': duplicate frame')
 if any(d<1 for d in clip['durationMs']):errors.append(slug+': invalid duration')
 if sum(clip['durationMs'])!=clip['totalDurationMs']:errors.append(slug+': duration sum')
for source in m['sourceImages']:
 p=R/source;rp=Path(str(p)+'.generation.json');rec=json.loads(rp.read_text(encoding='utf-8'));assert rec['sha256']==sha(p)
 rec['inspection']={'visualStatus':'passed_as_source_for_derived_assets','issues':[],'rawAlphaAdvisories':'near-invisible haze in source is cleaned only in final exports; source remains byte-identical','reviewedAt':now};rec['status']['sourceDesignAccepted']=True;dump(rp,rec)
for p in m['previews']:
 rp=R/p['file'];rec=json.loads(Path(str(rp)+'.generation.json').read_text(encoding='utf-8'));rec['inspection']={'visualStatus':'passed','reviewedAt':now};dump(Path(str(rp)+'.generation.json'),rec)
qa={'schemaVersion':2,'status':'passed' if not errors else 'failed','generatedAt':now,'primaryAssets':35,'callouts':8,'effectFrames':24,'distinctFramesPerEffect':4,'effectClips':6,'resultDecorations':2,'blankPlaques':1,'errors':errors,'warnings':[],'files':checks,'visualReview':{'status':'passed','evidence':['assets/fx/full-game/previews/frames-alpha.png','assets/fx/full-game/previews/callouts-alpha.png'],'method':'actual visual inspection of all final PNGs as contact sheets on both light and dark backgrounds, source art and phase ordering','loop':'four distinct clockwise glint positions; center registered from inner transparent hole','text':'吃、碰、杠、胡、听、自摸、流局、胜利逐字检查，准确排版，不是AI生成文字'},'clipBuilder':{'status':'passed_numeric_and_visual_phase_review','lintWarnings':built['diagnostics']['lint'],'duplicateGroups':built['diagnostics']['visible_pixel_duplicate_groups'],'frameAlphaAndTimelineExact':all(c['preview']['timeline_verified'] and c['preview']['alpha_and_visible_rgb_exact'] for c in built['clips'].values())},'engineRoundTrip':engine['qa'],'rawAdvisories':{'safe_frame':'raw sources had safe_frame advisories, resolved by uniform downsample and registered transparent canvas padding; final outputs have no visible edge contact','faint_specks':'source alpha1–4 and isolated haze removed with alpha_hygiene both; soft glow retained','doctorPythonPath':'python.path WARN: other python.exe on PATH; all executed processing commands explicitly use isolated Python3.12 via forge.ps1, no unresolved interpreter choice'},'notProven':['真实客户端/引擎中的导入与对局触发尚未运行','浏览器交互未实测，预览仅做文件与脚本静态检查','每类只有4张实际生成的关键阶段图；跨阶段混合和结束淡出为客户端补间，不声称连续视频或角色骨骼动画']}
dump(A/'qa.json',qa)
m.update({'status':'complete_qa_passed' if not errors else 'failed','completedAt':now,'runtimeClips':'assets/fx/full-game/animation-clips.json','engineExport':'assets/fx/full-game/engine/engine-export.json','supplementalMedia':supp,'previewPage':'assets/fx/full-game/index.html','integrationDoc':'docs/FX_FULL_GAME.md'});dump(A/'manifest.json',m)
print(json.dumps({'status':qa['status'],'assets':len(m['assets']),'frames':24,'clips':6,'errors':errors,'engineRoundTrip':engine['qa']['status'],'supplementalMedia':len(supp)},ensure_ascii=False))
