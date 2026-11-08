from pathlib import Path
from PIL import Image
from datetime import datetime,timezone,timedelta
import json,hashlib,sys,shutil
R=Path(r'D:\work\majiang-image')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
slug,src=sys.argv[1],Path(sys.argv[2]); out=R/f'designs/fx/full-game/{slug}-v1.png'
assert not out.exists() or sha(out)==sha(src),out
shutil.copyfile(src,out)
im=Image.open(out); im.load(); prompt=R/f'prompts/full-game/fx/{slug}.txt'
refs=[]
for file in ['references/style/01-mail-event.png','references/style/team-ui-v2.png']:
 refs.append({'file':file,'submittedPath':str(R/file),'sha256':sha(R/file),'actuallyAttached':True,'role':'style_reference'})
for file in sys.argv[3:]:
 refs.append({'file':file,'submittedPath':str(R/file),'sha256':sha(R/file),'actuallyAttached':True,'role':'edit_target'})
r={'schemaVersion':2,'file':out.relative_to(R).as_posix(),'title':slug,'sha256':sha(out),'generatedAt':datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds'),'clientTimezone':'America/New_York','generationTimestampBasis':'observed tool return and adoption time','tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((R/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[x['submittedPath'] for x in refs],'promptFile':prompt.relative_to(R).as_posix()},'actualModel':None,'actualQuality':None,'evidence':'Tool returned image_url, output_hint and native PNG path; no model or quality disclosed.','unverifiedReason':'宿主管理，工具未披露可核实版本/质量。配置目标不是实际版本证明。','width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'nativeDimensions':[im.width,im.height],'resampled':False,'prompt':prompt.relative_to(R).as_posix(),'promptSha256':sha(prompt),'references':refs,'source':{'toolNativeOutput':str(src),'sha256':sha(src),'operation':'byte-identical copy'},'inspection':{'visualStatus':'pending','issues':[]},'status':{'productionAccepted':False,'userApproved':False,'clientIntegrated':False},'delivery':{'localOnly':True,'uploaded':False}}
Path(str(out)+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'size':im.size,'mode':im.mode,'alpha':im.getchannel('A').getextrema() if im.mode=='RGBA' else None},ensure_ascii=False))
