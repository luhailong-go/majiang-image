from pathlib import Path
from PIL import Image
from collections import deque, Counter
from datetime import datetime, timezone, timedelta
import hashlib, json
import numpy as np

ROOT=Path(r'D:\work\majiang-image')
OUT=ROOT/'assets/characters'
WORK=ROOT/'work/characters'
TZ=timezone(timedelta(hours=-4))
now=datetime.now(TZ).isoformat()
def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stats(im):
    d={'width':im.width,'height':im.height,'format':'PNG','mode':im.mode}
    if im.mode=='RGBA':
        a=im.getchannel('A'); h=Counter(a.get_flattened_data())
        d['alpha']={'range':list(a.getextrema()),'transparentPixels':h[0],'opaquePixels':h[255],'semiTransparentPixels':im.width*im.height-h[0]-h[255],'bboxNonzero':a.getbbox(),'bboxAbove128':a.point(lambda v:255 if v>128 else 0).getbbox(),'corners':[a.getpixel(p) for p in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]],'mostCommon':[list(v) for v in h.most_common(8)]}
    return d
config=json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig'))
ref_manifest=json.loads((ROOT/'references/manifest.json').read_text(encoding='utf-8-sig'))
ref_lookup={r['file']:r for r in ref_manifest['references']}
ref_files=['designs/characters/welcome-daotong-v1.png','references/style/01-mail-event.png','references/style/team-ui-v2.png','references/style/mail-banner-character.png']
references=[]
for idx,f in enumerate(ref_files,1):
    p=ROOT/f; old=ref_lookup.get(f,{})
    references.append({'inputIndex':idx,'file':f,'submittedPath':str(p),'sha256':sha(p),'source':old.get('source',f),'role':'identity edit target' if idx==1 else old.get('role'),'actuallyAttached':True})
def native_record(name,prompt_file,receipt_file,transparent,requested,inspection):
    p=ROOT/'designs/characters/production'/name
    im=Image.open(p); im.load()
    receipt=json.loads((WORK/receipt_file).read_text(encoding='utf-8'))
    completed=datetime.fromisoformat(receipt['completedAt'].replace('Z','+00:00')).astimezone(TZ).isoformat()
    data={'schemaVersion':1,'file':rel(p),'sha256':sha(p),'generatedAt':completed,'timestampBasis':'tool completion observed by client','clientTimezone':'America/New_York','startedAt':receipt['startedAt'],**stats(im),'nativeDimensions':{'width':im.width,'height':im.height},'requestedDimensionsInPrompt':requested,'resampled':False,'tool':'image_gen.imagegen','route':'builtin','generationCallId':None,'resultId':None,'outputArtifactFileId':Path(receipt['sourceFile']).stem,'resultReceipt':receipt,'configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':transparent,'referenced_image_paths':[r['submittedPath'] for r in references],'promptFile':prompt_file},'actualModel':None,'actualQuality':None,'evidence':'Tool returned image_url and output_hint only; source file copied byte-identically. PNG properties and hash measured locally.','unverifiedReason':'宿主管理，工具未披露可核实版本/质量；配置目标不等于实际返回型号。','prompt':prompt_file,'promptSha256':sha(ROOT/prompt_file),'references':references,'source':{'toolNativeOutput':receipt['sourceFile'],'operation':'byte-identical copy','sha256':sha(p)},'inspection':inspection,'status':{'stage':'production_source','userApproved':False,'clientIntegrated':False}}
    write_json(Path(str(p)+'.generation.json'),data)
    return data

body_source=ROOT/'designs/characters/production/welcome-daotong-production-v2.png'
src=Image.open(body_source).convert('RGBA')
rgba=np.array(src)
alpha=rgba[:,:,3]
h,w=alpha.shape
mask=(alpha>8).ravel()
seen=bytearray(w*h)
seed=(h//2)*w+w//2
if not mask[seed]: seed=int(np.argmax(alpha.ravel()))
seen[seed]=1; q=deque([seed]); count=0
while q:
    i=q.popleft(); count+=1
    y,x=divmod(i,w)
    for dy in (-1,0,1):
        ny=y+dy
        if ny<0 or ny>=h: continue
        for dx in (-1,0,1):
            nx=x+dx
            if nx<0 or nx>=w or (dx==0 and dy==0): continue
            j=ny*w+nx
            if not seen[j] and mask[j]: seen[j]=1; q.append(j)
keep=np.frombuffer(seen,dtype=np.uint8).reshape(h,w).astype(bool)
removed_nonzero=int(np.count_nonzero((alpha>0)&~keep))
removed_strong=int(np.count_nonzero((alpha>128)&~keep))
removed_components=int(np.count_nonzero((alpha>8)&~keep))
rgba[~keep]=[0,0,0,0]
near_opaque=int(np.count_nonzero((rgba[:,:,3]>=250)&(rgba[:,:,3]<255)))
rgba[:,:,3][rgba[:,:,3]>=250]=255
clean=Image.fromarray(rgba)
bbox=clean.getchannel('A').getbbox()
cropped=clean.crop(bbox)
canvas=Image.new('RGBA',(1536,1536),(0,0,0,0))
offset=((1536-cropped.width)//2,(1536-cropped.height)//2)
canvas.paste(cropped,offset)
full=OUT/'welcome-daotong.png'; canvas.save(full)
operations=[{'operation':'alpha sanitation','lowAlphaThresholdInclusive':8,'keepComponent':'8-connected component containing center body pixel','removedNonzeroPixels':removed_nonzero,'removedPixelsAbove128':removed_strong,'removedDisconnectedPixelsAbove8':removed_components,'promoteAlpha250To255':True,'promotedNearOpaquePixels':near_opaque,'transparentRgbZeroed':True,'note':'Technical alpha export only; no painted RGB detail redrawn.'},{'operation':'crop transparent source margins','box':list(bbox)},{'operation':'pad transparent canvas without resampling','canvas':[1536,1536],'offset':list(offset)}]
fullstat=stats(canvas)
for name,color in [('light',(246,238,218,255)),('dark',(14,44,39,255))]:
    bg=Image.new('RGBA',canvas.size,color); bg.alpha_composite(canvas)
    bg.convert('RGB').save(WORK/f'welcome-daotong-{name}-qa.png')
body_record=native_record('welcome-daotong-production-v2.png','prompts/characters/welcome-daotong-production-v2.prompt.txt','production-v2-receipt.json',True,{'width':1536,'height':1536},{'status':'source_accepted_for_mechanical_export','identity':'passed','anatomy':'passed, full hands and feet','text':'single red 中 passed','trueAlpha':'passed','rawEdgeCleanup':'requires_export_sanitation','rawMargin':'not_requested_8_percent','notes':['Real-alpha light/dark composite visually clean; raw transparent viewer exposes saturated RGB in very low-alpha pixels.','Low-alpha isolated pixels and tight source framing are handled by documented mechanical export.'],'visualInspectionCompleted':True})
fullrecord={'schemaVersion':1,'file':rel(full),'sha256':sha(full),'exportedAt':now,**fullstat,'nativeDimensions':body_record['nativeDimensions'],'exportDimensions':{'width':1536,'height':1536},'derivedFrom':{'file':rel(body_source),'sha256':sha(body_source),'generationRecord':rel(Path(str(body_source)+'.generation.json'))},'operation':operations,'resampled':False,'newModelGeneration':False,'actualModel':None,'actualQuality':None,'prompt':body_record['prompt'],'inspection':{'status':'pending_final_visual_qa','alphaSanitationMetrics':{'removedPixelsAbove128':removed_strong,'removedDisconnectedPixelsAbove8':removed_components},'qaPreviews':['work/characters/welcome-daotong-light-qa.png','work/characters/welcome-daotong-dark-qa.png']},'usage':{'purpose':'lobby full-body welcome character','anchor':[0.5,1.0],'scaleMode':'uniform contain','nineSlice':None,'transparent':True}}
write_json(Path(str(full)+'.generation.json'),fullrecord)

atlas=ROOT/'designs/characters/production/seat-avatars-atlas-v1.png'
atlas_im=Image.open(atlas).convert('RGB'); aw,ah=atlas_im.size
atlas_record=native_record('seat-avatars-atlas-v1.png','prompts/characters/seat-avatars-atlas-v1.prompt.txt','avatars-v1-receipt.json',False,{'width':2048,'height':2048},{'status':'accepted_for_derived_portraits','visualInspectionCompleted':True,'distinctIdentities':'passed: boy/healer/elder/swordswoman clearly distinguished','style':'passed against both UI references','layout':'four quadrant portraits; square crop intended; selected hair/ribbon tails may reach portrait edges','text':'no lettering','unresolvedIssues':[]})
identities=[('avatar-daotong','金带道童',(0,0,aw//2,ah//2)),('avatar-healer','银发医师',(aw//2,0,aw,ah//2)),('avatar-master','白眉老道',(0,ah//2,aw//2,ah)),('avatar-swordswoman','黑发侠女',(aw//2,ah//2,aw,ah))]
assets=[{'id':'welcome-daotong','name':'迎宾道童透明全身','file':rel(full),'record':rel(Path(str(full)+'.generation.json')),'sha256':sha(full),**fullstat,'role':'full_body','stage':'pending_final_visual_qa'}]
for ident,title,box in identities:
    native=atlas_im.crop(box)
    im=native.resize((512,512),Image.Resampling.LANCZOS)
    p=OUT/(ident+'.png'); im.save(p)
    d={'schemaVersion':1,'file':rel(p),'sha256':sha(p),'exportedAt':now,**stats(im),'nativeDimensions':{'width':native.width,'height':native.height},'exportDimensions':{'width':512,'height':512},'derivedFrom':{'file':rel(atlas),'sha256':sha(atlas),'generationRecord':rel(Path(str(atlas)+'.generation.json'))},'operation':[{'operation':'quadrant crop','box':list(box)},{'operation':'resize down','method':'LANCZOS','from':[native.width,native.height],'to':[512,512]}],'newModelGeneration':False,'actualModel':None,'actualQuality':None,'prompt':atlas_record['prompt'],'inspection':{'status':'pending_final_visual_qa'},'usage':{'identity':title,'purpose':'seat/profile/character selector avatar','anchor':[0.5,0.5],'scaleMode':'uniform cover','nineSlice':None,'transparent':False,'mask':'client circular or rounded-square clip; no border baked in'}}
    write_json(Path(str(p)+'.generation.json'),d)
    assets.append({'id':ident,'name':title,'file':rel(p),'record':rel(Path(str(p)+'.generation.json')),'sha256':sha(p),**stats(im),'role':'avatar','stage':'pending_final_visual_qa'})
manifest={'schemaVersion':1,'generatedAt':now,'scope':'FULL_UI_SCOPE role assets: one clean transparent full body and four differentiated avatars','root':'D:/work/majiang-image','actualModel':None,'actualQuality':None,'userApproved':False,'clientIntegrated':False,'assets':assets,'sourceImages':[rel(body_source),rel(atlas)],'qaReport':'assets/characters/QA.md','exportScript':'work/characters/export_characters.py','note':'Avatar files are derived crops/downsamples of one generated atlas. The 1536 transparent full-body canvas contains unscaled native character detail from a 1254 image; padding is not native resolution increase.'}
write_json(OUT/'manifest.json',manifest)
write_json(WORK/'export-summary.json',{'fullBody':fullrecord,'avatars':assets[1:]})
print(json.dumps({'fullBody':fullstat,'cleanup':operations,'avatars':[(a['file'],a['width'],a['height']) for a in assets[1:]]},ensure_ascii=False))
