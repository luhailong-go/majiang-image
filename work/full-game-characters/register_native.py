from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
TZ=timezone.utc
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser()
p.add_argument('--source',required=True)
p.add_argument('--name',required=True)
p.add_argument('--prompt',required=True)
p.add_argument('--identity',required=True)
p.add_argument('--fullbody-reference')
a=p.parse_args()
source=Path(a.source)
target=ROOT/'designs/characters/full-game'/f'{a.name}-native.png'
if target.exists() and sha(target)!=sha(source): raise RuntimeError('Refusing to overwrite a different source')
if not target.exists(): shutil.copy2(source,target)
im=Image.open(target); im.load()
config=json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig'))
refs=['references/style/01-mail-event.png','references/style/team-ui-v2.png',f'assets/characters/avatar-{a.identity}.png']
if a.fullbody_reference: refs.append(a.fullbody_reference)
references=[{'inputIndex':i+1,'file':f,'submittedPath':str(ROOT/f),'sha256':sha(ROOT/f),'role':'authoritative style reference' if i<2 else 'identity reference','actuallyAttached':True} for i,f in enumerate(refs)]
observed=datetime.now(TZ).isoformat()
record={'schemaVersion':1,'file':rel(target),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(source.stat().st_mtime,TZ).isoformat(),'completionObservedAt':observed,'timestampBasis':'host artifact filesystem modification time, observed after builtin tool completion','width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'nativeDimensions':[im.width,im.height],'resampled':False,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','generationCallId':None,'resultId':None,'configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':True,'referenced_image_paths':[r['submittedPath'] for r in references]},'actualModel':None,'actualQuality':None,'evidence':{'toolReturnFields':['image_url','output_hint'],'nativeOutputFile':str(source),'nativeOutputSha256':sha(source),'copy':'byte-identical'},'unverifiedReason':'宿主管理，工具未披露可核实版本/质量；配置目标与实际返回证据分开。','prompt':a.prompt,'promptSha256':sha(ROOT/a.prompt),'references':references,'inspection':{'status':'pending_alpha_export_and_visual_qa'},'userApproved':False,'clientIntegrated':False}
write(Path(str(target)+'.generation.json'),record)
print(json.dumps({'file':rel(target),'size':im.size,'mode':im.mode,'sha256':sha(target)},ensure_ascii=False))
