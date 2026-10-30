from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
R=Path(__file__).resolve().parents[2]
hold=R/'.work/production-v3/resource-hold.json'
if hold.is_file() and json.loads(hold.read_text(encoding='utf-8-sig')).get('status')=='holding_local_heavy_work':raise SystemExit('Deferred: shared-machine heavy-work slot has not been returned; existing previews remain unchanged.')
from PIL import Image,ImageDraw,ImageFont
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
cache={};fontCache={};fitIssues=[]
def opened(file):
    if file not in cache:cache[file]=Image.open(R/file).convert('RGBA')
    return cache[file]
def font(size):
    if size not in fontCache:fontCache[size]=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
    return fontCache[size]
def resized(im,size):
    if im.size==size:return im
    return im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
def nine(im,size,slices,axes):
    w,h=size;l,t,r,b=slices
    scale=h/im.height if 'y' not in axes else min(1,w/im.width,h/im.height)
    L=max(1,round(l*scale));T=max(1,round(t*scale));RR=max(1,round(r*scale));B=max(1,round(b*scale))
    if L+RR>=w or T+B>=h:return resized(im,size)
    out=Image.new('RGBA',size)
    sx=[0,l,im.width-r,im.width];sy=[0,t,im.height-b,im.height];dx=[0,L,w-RR,w];dy=[0,T,h-B,h]
    for y in range(3):
        for x in range(3):
            part=im.crop((sx[x],sy[y],sx[x+1],sy[y+1]));part=resized(part,(dx[x+1]-dx[x],dy[y+1]-dy[y]));out.alpha_composite(part,(dx[x],dy[y]))
    return out
def wrap(value,f,w,draw):
    result=[]
    for paragraph in value.split('\n'):
        if not paragraph:result.append('');continue
        line=''
        for char in paragraph:
            if line and draw.textlength(line+char,font=f)>w:result.append(line);line=char
            else:line+=char
        result.append(line)
    return result
def drawText(canvas,node,tag):
    x,y,w,h=map(round,node['rect']);size=node.get('fontSize',28);f=font(size);draw=ImageDraw.Draw(canvas);lines=wrap(node.get('text',''),f,w,draw);lineHeight=round(size*1.5)
    if len(lines)>1 and len(lines)*lineHeight>h+lineHeight*.25:fitIssues.append({'composition':tag,'node':node['id'],'text':node['text'],'height':h,'requiredHeight':len(lines)*lineHeight})
    for i,line in enumerate(lines):
        textWidth=draw.textlength(line,font=f);xx=x+(w-textWidth)/2 if node.get('align')=='center' else x+w-textWidth if node.get('align')=='right' else x
        draw.text((xx,y+i*lineHeight),line,font=f,fill=node.get('color','#183d35'),stroke_width=0)
def compose(layers,tag):
    canvas=Image.new('RGBA',(1600,900),'#123e34')
    for node in layers:
        if node['type']=='text':drawText(canvas,node,tag);continue
        x,y,w,h=map(round,node['rect']);file=node.get('file')
        if not file:continue
        if node['type']=='button':
            state=node.get('previewState','normal') if node.get('enabled',True) else 'disabled';file=node.get('stateAssets',{}).get(state,file)
        im=opened(file)
        if node.get('sourceRect'):im=im.crop(tuple(node['sourceRect']))
        if node.get('rotation'):im=im.rotate(-node['rotation'],expand=True,resample=Image.Resampling.BICUBIC)
        if node.get('nineSlice'):part=nine(im,(w,h),node['nineSlice'],node.get('stretchAxes',['x','y']));px=x;py=y
        elif node.get('fitMode')=='stretch_x':part=resized(im,(w,h));px=x;py=y
        elif node.get('fitMode')=='cover':
            scale=max(w/im.width,h/im.height);temp=resized(im,(round(im.width*scale),round(im.height*scale)));part=temp.crop(((temp.width-w)//2,(temp.height-h)//2,(temp.width+w)//2,(temp.height+h)//2));px=x;py=y
        else:
            scale=min(w/im.width,h/im.height);part=resized(im,(max(1,round(im.width*scale)),max(1,round(im.height*scale))));px=x+(w-part.width)//2;py=y+(h-part.height)//2
        if node.get('clipFraction') is not None:part=part.crop((0,0,max(0,round(part.width*node['clipFraction'])),part.height))
        if part.width:canvas.alpha_composite(part,(px,py))
        if node['type']=='button':drawText(canvas,{**node,'rect':[x+12,y+round((h-node.get('fontSize',25)*1.45)/2)-2,w-24,h],'align':'center','color':node.get('color','#fff9e9') if node.get('enabled',True) else '#777160'},tag)
    return canvas.convert('RGB')
pages=read('production/layouts.json')['pages'];states=read('production/states.json')['states'];records=[];stamp=datetime.now(timezone.utc).isoformat()
layoutHashes={'pages':hashlib.sha256(json.dumps(pages,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'states':hashlib.sha256(json.dumps(states,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
rendererHash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def emit(id,layers,kind):
    canvas=compose(layers,id);canvas=canvas.resize((1280,720),Image.Resampling.LANCZOS);file=f'production/previews/{kind}/{id}.png';p=R/file;p.parent.mkdir(parents=True,exist_ok=True);canvas.save(p)
    deps=sorted({a['file'] for a in layers if a.get('file')}|{f for a in layers for f in a.get('stateAssets',{}).values()})
    d={'schemaVersion':3,'file':file,'sha256':sha(file),'createdAt':stamp,'width':1280,'height':720,'mode':'RGB','format':'PNG','newModelGeneration':False,'actualModel':None,'actualQuality':None,'derivedFrom':[{'file':f,'sha256':sha(f),'generationRecord':f+'.generation.json'} for f in deps],'operation':{'type':'independent_asset_UI_composition','designCanvas':[1600,900],'previewCanvas':[1280,720],'layoutSource':'production/layouts.json' if kind=='pages' else 'production/states.json','layoutId':id,'layoutContentSha256':layoutHashes[kind],'rendererSha256':rendererHash,'nineSlice':'only explicit source contract','text':'native CJK font at render time; no font binaries redistributed','notANativeNewPainting':True},'inspection':{'status':'pending_visual_qa'}}
    write(file+'.generation.json',d);records.append({'id':id,'kind':kind,'file':file,'record':file+'.generation.json','sha256':d['sha256'],'sourceFiles':deps})
for page in pages:emit(page['id'],page['layers'],'pages')
for state in states:emit(state['state'],state['layers'],'states')
for group,entries in [('pages',records[:32]),('states',records[32:])]:
    for start in range(0,len(entries),12):
        subset=entries[start:start+12];rows=math.ceil(len(subset)/3);contact=Image.new('RGB',(1440,rows*302),'#ece7d7');draw=ImageDraw.Draw(contact)
        for i,a in enumerate(subset):
            part=Image.open(R/a['file']).resize((472,266),Image.Resampling.LANCZOS);x=(i%3)*480+4;y=(i//3)*302;contact.paste(part,(x,y));draw.text((x+7,y+269),a['id'],font=font(18),fill='#183d35')
        file=f'production/previews/contact-{group}-{start//12+1}.png';contact.save(R/file)
        write(file+'.generation.json',{'file':file,'sha256':sha(file),'width':contact.width,'height':contact.height,'format':'PNG','mode':'RGB','newModelGeneration':False,'actualModel':None,'actualQuality':None,'derivedFrom':[{'file':a['file'],'sha256':a['sha256'],'generationRecord':a['record']} for a in subset],'operation':'deterministic visual QA contact sheet, not an independent painting','createdAt':stamp})
write('production/composition-previews.json',{'schemaVersion':3,'pageCount':len(pages),'stateCount':len(states),'previewCount':len(records),'images':records,'textFitIssues':fitIssues,'layoutContentHashes':layoutHashes,'rendererSha256':rendererHash,'browserRender':False,'clientIntegrated':False,'status':'pending_visual_qa'})
print(json.dumps({'pageComposites':len(pages),'stateComposites':len(states),'runtimeImagesUsed':len(cache),'textFitIssueCount':len(fitIssues),'issues':fitIssues[:15]},ensure_ascii=False))
