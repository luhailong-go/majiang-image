from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,shutil,sys
from PIL import Image
R=Path(r'D:\work\majiang-image')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
out=R/spec['file']; out.parent.mkdir(parents=True,exist_ok=True)
src=Path(spec['source']); shutil.copyfile(src,out)
im=Image.open(out); im.verify(); im=Image.open(out)
refs=[{'file':r,'sha256':sha(R/r),'purpose':'主UI风格' if i<2 else '当前游戏角色或桌面参考','actuallyAttached':True,'submittedPath':str(R/r)} for i,r in enumerate(spec['references'])]
p=R/spec['prompt']
rec={'schemaVersion':2,'file':spec['file'],'uiId':spec['uiId'],'title':spec['title'],'sha256':sha(out),'generatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'generationTimestampBasis':'客户端落盘时间，工具未返回生成时间','clientTimezone':'America/New_York','tool':'image_gen.imagegen','route':'builtin','generationCallId':None,'resultId':None,'outputArtifactFileId':src.stem,'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'nativeDimensions':{'width':im.width,'height':im.height},'resampled':False,'configSnapshot':json.loads((R/'config/image-generation.json').read_text(encoding='utf-8')),'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False,'referenced_image_paths':[r['submittedPath'] for r in refs],'promptFile':spec['prompt']},'actualModel':None,'actualQuality':None,'evidence':'工具仅提供image_url及output_hint，尺寸和哈希由落盘文件读取。','unverifiedReason':'宿主管理，工具未披露可核实版本/质量。配置目标不是实际版本证明。','prompt':spec['prompt'],'promptSha256':sha(p),'references':refs,'source':{'toolNativeOutput':str(src),'sha256':sha(src),'operation':'byte-identical copy','derived':False},'inspection':{'pngIntegrity':'passed','visualStatus':'passed','visualInspectionCompleted':True,'visualNotes':spec['notes'],'issues':[],'blockingIssues':[],'nativeDimensionsChecked':True},'status':{'stage':'full_game_ui_art_v2','userApproved':False,'productionAccepted':True,'clientIntegrated':False},'coveredStates':spec['states'],'delivery':{'localOnly':True,'uploaded':False},'receipt':{'keys':['image_url','output_hint'],'output_hint':spec['outputHint']}}
for ref in rec['references']:
 ref['purpose']='主UI风格' if ref['file'] in ['references/style/01-mail-event.png','references/style/team-ui-v2.png'] else ('AI编辑对象' if '-source.png' in ref['file'] else '角色/场景/连续步骤参考')
if spec.get('productionAccepted') is False:
 rec['status']['productionAccepted']=False
 rec['status']['stage']='superseded_candidate_or_edit_source'
 rec['inspection']['visualStatus']='needs_correction'
 rec['inspection']['issues']=spec.get('issues',[])
 rec['inspection']['blockingIssues']=spec.get('issues',[])
if spec.get('isEdit'):
 rec['generationType']='ai_edit'
 rec['editTarget']=spec['references'][0]
if spec.get('removeSupersededPixels'):
 rec['pixelsRetainedInProject']=False
 rec['cleanup']={'reason':'已由更明确页脚重制取代，不用于任何后续参考；保留提示词、结果证据、哈希与记录。','removedAt':datetime.now(ZoneInfo('America/New_York')).isoformat()}
out.with_name(out.name+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
if spec.get('removeSupersededPixels'):
 im.close()
 out.unlink()
print(json.dumps({'file':spec['file'],'size':[im.width,im.height],'sha256':rec['sha256']},ensure_ascii=False))
