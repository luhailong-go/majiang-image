from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import argparse,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--name',required=True);p.add_argument('--reference',action='append',default=[]);a=p.parse_args()
source=Path(a.source);out=ROOT/'designs/ui/production-v3/forms'/f'{a.name}-native.png';prompt=ROOT/'prompts/production-v3/forms'/f'{a.name}.prompt.txt'
if out.exists() and sha(out)!=sha(source):raise RuntimeError('Refuse source overwrite')
if not out.exists():shutil.copy2(source,out)
im=Image.open(out);im.load();now=datetime.now(timezone.utc).isoformat()
refs=[{'file':r,'sha256':sha(ROOT/r),'role':'style reference' if i<2 else 'existing function-matched skin reference','actuallyAttached':True,'inputIndex':i+1} for i,r in enumerate(a.reference)]
d={'schemaVersion':1,'file':rel(out),'sha256':sha(out),'generatedAt':datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),'completionObservedAt':now,'timestampBasis':'host artifact modification time observed after image_gen completion','width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'nativeDimensions':[im.width,im.height],'resampled':False,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[str(ROOT/r) for r in a.reference]},'actualModel':None,'actualQuality':None,'evidence':{'toolReturnFields':['image_url','output_hint'],'hostNativeOutput':str(source),'sha256':sha(source),'copy':'byte-identical'},'unverifiedReason':'Host managed; tool exposes no model/quality selector or verifiable result metadata.','prompt':rel(prompt),'promptSha256':sha(prompt),'references':refs,'inspection':{'status':'pending_export_qa'},'userApproved':False,'clientIntegrated':False}
Path(str(out)+'.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':rel(out),'size':im.size,'mode':im.mode,'sha256':sha(out)}))
