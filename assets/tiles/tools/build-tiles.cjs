/* Deterministic typography and symbols over native AI hand-painted tile bases. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
const project = path.resolve(root, '..', '..');
const W=448, H=640;
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel = p => path.relative(project,p).split(path.sep).join('/');
const writeJson = (p,v) => fs.writeFileSync(p, JSON.stringify(v,null,2)+'\n');
const sourcePath = name => path.join(root,'source',name);
const referenceHash = f => {
 const p=path.join(project,f);
 if(fs.existsSync(p)) return sha(p);
 const record=p+'.generation.json';
 if(fs.existsSync(record))return JSON.parse(fs.readFileSync(record,'utf8')).sha256;
 throw new Error('Missing reference and provenance record: '+f);
};
const config = JSON.parse(fs.readFileSync(path.join(project,'config','image-generation.json'),'utf8').replace(/^\uFEFF/,''));
const glyphs = JSON.parse(fs.readFileSync(sourcePath('glyph-outlines.json'),'utf8').replace(/^\uFEFF/,'')).glyphs;
const refs = ['references/style/01-mail-event.png','references/style/team-ui-v2.png'];
const rawSources = [
 {name:'tile-blank-v1.png',prompt:'prompts/tiles/tile-blank-v1.prompt.txt',id:'exec-4eb3d561-2243-41f1-98cb-af633b29dc80',start:'2026-10-26T08:07:04.238Z',refs,role:'first native blank tile, superseded by v2 cleanup attempt'},
 {name:'tile-blank-v2.png',prompt:'prompts/tiles/tile-blank-v2-clean.prompt.txt',id:'exec-924db6ee-13a0-4172-b587-4ceb988e0a80',start:'2026-10-26T08:12:25.286Z',refs:['assets/tiles/source/tile-blank-v1.png',...refs],role:'selected hand-painted blank source; exported alpha silhouette conditioned deterministically'},
 {name:'tile-back-v1.png',prompt:'prompts/tiles/tile-back-v1.prompt.txt',id:'exec-a4973406-739d-487b-84c1-0ddc2750484b',start:'2026-10-26T08:12:25.286Z',refs:['assets/tiles/source/tile-blank-v1.png',...refs],role:'selected hand-painted jade Taiji back source'}
];
function sourceRef(p){return {file:rel(p),sha256:sha(p),generationRecord:rel(p)+'.generation.json'};}
function derive(p, sources, operation, extra={}) {
 writeJson(p+'.generation.json',{
  file:rel(p),sha256:sha(p),createdAt:new Date().toISOString(),tool:'deterministic tile asset build',route:'derived',
  actualModel:null,actualQuality:null,unverifiedReason:sources.length?'Derived asset, not a new model call; source actual model/quality were not disclosed.':'No model call; deterministic original vector rendering.',
  derivedFrom:sources.map(sourceRef),operation,canvas:{width:W,height:H,format:path.extname(p).slice(1)},
  checks:{technical:'passed',visual:'pending'},...extra
 });
}
function glyph(ch,cx,cy,width,height,fill) {
 const g=glyphs[ch]; if(!g)throw new Error('missing glyph '+ch);
 const [x,y,w,h]=g.bounds; const s=Math.min(width/w,height/h);
 const ox=cx-w*s/2,oy=cy-h*s/2;
 return `<g data-glyph="${ch}" transform="translate(${ox.toFixed(3)} ${oy.toFixed(3)}) scale(${s.toFixed(6)}) translate(${-x} ${-y})"><path d="${g.path}" fill="${fill}"/></g>`;
}
const defs=`<defs>
 <linearGradient id="green" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#36876b"/><stop offset=".55" stop-color="#185844"/><stop offset="1" stop-color="#0b3b31"/></linearGradient>
 <linearGradient id="red" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#cf4b36"/><stop offset=".6" stop-color="#ae302b"/><stop offset="1" stop-color="#7b2526"/></linearGradient>
 <linearGradient id="blue" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#42798b"/><stop offset=".6" stop-color="#28566d"/><stop offset="1" stop-color="#163e56"/></linearGradient>
 </defs>`;
const svg = content => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${defs}${content}</svg>`;
const dotPositions = {
 1:[[0,0]],2:[[0,-115],[0,115]],3:[[-85,-150],[0,0],[85,150]],
 4:[[-83,-132],[83,-132],[-83,132],[83,132]],
 5:[[-95,-160],[95,-160],[0,0],[-95,160],[95,160]],
 6:[[-94,-160],[94,-160],[-94,0],[94,0],[-94,160],[94,160]],
 7:[[-94,-176],[0,-116],[94,-56],[-94,75],[94,75],[-94,188],[94,188]],
 8:[[-88,-181],[88,-181],[-88,-60],[88,-60],[-88,60],[88,60],[-88,181],[88,181]],
 9:[[-98,-166],[0,-166],[98,-166],[-98,0],[0,0],[98,0],[-98,166],[0,166],[98,166]]
};
function pip(x,y,r,color) {
 return `<g data-pip="1" transform="translate(${218+x} ${306+y})"><circle r="${r}" fill="url(#${color})" stroke="#173e37" stroke-width="2.1"/><circle r="${r*.72}" fill="none" stroke="#dfc47e" stroke-width="${Math.max(2,r*.065)}"/><circle r="${r*.45}" fill="none" stroke="#f3e4b4" stroke-opacity=".75" stroke-width="${Math.max(2,r*.04)}"/><circle r="${r*.16}" fill="#e9cf8f"/><path d="M ${-r*.65} ${-r*.15} A ${r*.67} ${r*.67} 0 0 1 ${-r*.1} ${-r*.66}" fill="none" stroke="#f7ebbf" stroke-opacity=".6" stroke-width="${Math.max(2,r*.055)}" stroke-linecap="round"/></g>`;
}
const bambooPositions = {
 1:[[0,0,76,315]],2:[[-78,0,58,290],[78,0,58,290]],3:[[-102,0,48,290],[0,0,48,290],[102,0,48,290]],
 4:[[-86,-135,45,170],[86,-135,45,170],[-86,135,45,170],[86,135,45,170]],
 5:[[-101,-164,40,130],[101,-164,40,130],[0,0,40,130],[-101,164,40,130],[101,164,40,130]],
 6:[[-101,-125,39,172],[0,-125,39,172],[101,-125,39,172],[-101,125,39,172],[0,125,39,172],[101,125,39,172]],
 7:[[0,-183,36,108],[-101,-43,36,108],[0,-43,36,108],[101,-43,36,108],[-101,151,36,108],[0,151,36,108],[101,151,36,108]],
 8:[[-130,-128,28,160],[-43,-128,28,160],[43,-128,28,160],[130,-128,28,160],[-130,128,28,160],[-43,128,28,160],[43,128,28,160],[130,128,28,160]],
 9:[[-101,-176,34,111],[0,-176,34,111],[101,-176,34,111],[-101,0,34,111],[0,0,34,111],[101,0,34,111],[-101,176,34,111],[0,176,34,111],[101,176,34,111]]
};
function bamboo(x,y,w,h,red=false){
 const c=red?'red':'green';
 return `<g data-bamboo="1" transform="translate(${218+x} ${306+y})"><path d="M ${-w*.34} ${-h/2} Q 0 ${-h*.55} ${w*.34} ${-h/2} L ${w*.43} ${h*.44} Q 0 ${h*.56} ${-w*.43} ${h*.44} Z" fill="url(#${c})" stroke="#174d3c" stroke-width="2"/><path d="M ${-w*.09} ${-h*.43} Q ${-w*.22} 0 ${-w*.08} ${h*.43}" fill="none" stroke="#b7cf85" stroke-opacity=".8" stroke-width="${w*.12}" stroke-linecap="round"/>${[-.27,0,.27].map(v=>`<path d="M ${-w*.49} ${h*v} Q 0 ${h*v-h*.035} ${w*.49} ${h*v}" fill="none" stroke="#133f32" stroke-width="${w*.15}" stroke-linecap="round"/><path d="M ${-w*.44} ${h*v-h*.02} Q 0 ${h*v-h*.06} ${w*.44} ${h*v-h*.02}" fill="none" stroke="#b1c986" stroke-width="${w*.065}" stroke-linecap="round"/>`).join('')}</g>`;
}
async function exportBase(source, output){
 const raw=await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let left=raw.info.width,top=raw.info.height,right=-1,bottom=-1;
 for(let y=0;y<raw.info.height;y++)for(let x=0;x<raw.info.width;x++){
  const p=(y*raw.info.width+x)*4; const v=raw.data[p+3]; raw.data[p+3]=v>=128?255:0;
  if(v>=128){left=Math.min(left,x);top=Math.min(top,y);right=Math.max(right,x);bottom=Math.max(bottom,y);}
 }
 const crop={left,top,width:right-left+1,height:bottom-top+1};
 const fit=await sharp(raw.data,{raw:raw.info}).extract(crop).resize({height:600,width:436,fit:'inside',kernel:'lanczos3'}).png().toBuffer({resolveWithObject:true});
 const offset={left:Math.round((W-fit.info.width)/2),top:Math.round((H-fit.info.height)/2)};
 await sharp({create:{width:W,height:H,channels:4,background:'#00000000'}}).composite([{input:fit.data,...offset}]).png().toFile(output);
 return {native:{width:raw.info.width,height:raw.info.height},crop,contentBounds:[offset.left,offset.top,fit.info.width,fit.info.height],alphaOperation:'Native alpha >=128 foreground silhouette, fully opaque interior; crop and downscale with Lanczos3 creates only narrow antialiased edge. Removes residual model halo, not a new AI generation.'};
}
async function main(){
 for(const s of rawSources){
  const p=sourcePath(s.name);
  if(!fs.existsSync(p)){
   if(s.name==='tile-blank-v1.png'&&fs.existsSync(p+'.generation.json'))continue;
   throw new Error('Missing selected native source '+p);
  }
  const md=await sharp(p).metadata();
  writeJson(p+'.generation.json',{file:rel(p),sha256:sha(p),generatedAt:fs.statSync(p).mtime.toISOString(),observedCallStartedAt:s.start,width:md.width,height:md.height,format:'png',channels:md.channels,tool:'image_gen.imagegen',route:'builtin',toolOutputFileId:s.id,configSnapshot:config,submittedParameters:{model:null,quality:null,transparent_background:true},actualModel:null,actualQuality:null,evidence:{toolResultImagePath:`C:/Users/luyua/.codex/generated_images/01a1773e-0bce-79e3-9860-5aa2d27a397d/${s.id}.png`,fieldsDisclosed:['image_url','output_hint'],parameterSchema:'prompt, referenced_image_paths, transparent_background; no model/quality selector'},unverifiedReason:'Host-managed builtin generation; result did not disclose reliable model or quality metadata.',prompt:s.prompt,references:s.refs.map(f=>({file:f,sha256:referenceHash(f),pixelsPresentInProject:fs.existsSync(path.join(project,f)),role:f.includes('tile-blank')?'edit target':'material/style reference'})),role:s.role,checks:{nativeAlpha:'present',rawExterior:'soft low-alpha glow remains; final exported assets condition the silhouette',status:s.name==='tile-blank-v1.png'?'superseded':'selected source, final export separately checked'}});
 }
 const blank=path.join(root,'tile-blank.png'),back=path.join(root,'tile-back.png');
 const blankExport=await exportBase(sourcePath('tile-blank-v2.png'),blank);
 const backExport=await exportBase(sourcePath('tile-back-v1.png'),back);
 derive(blank,[sourcePath('tile-blank-v2.png')],['foreground alpha silhouette conditioning','native content crop','downscale and center on shared 448x640 transparent canvas'],{export:blankExport});
 derive(back,[sourcePath('tile-back-v1.png')],['foreground alpha silhouette conditioning','native content crop','downscale and center on shared 448x640 transparent canvas'],{export:backExport});
 const entries=[]; const numerals=['一','二','三','四','五','六','七','八','九'];
 const jobs=[];
 for(let n=1;n<=9;n++)jobs.push({id:`wan-${n}`,label:`${numerals[n-1]}万`,suit:'characters',rank:n,glyphs:[numerals[n-1],'萬'],body:glyph(numerals[n-1],218,205,265,141,'#224e45')+glyph('萬',218,424,238,189,'#ad302b')});
 for(let n=1;n<=9;n++){
  const r=n===1?100:n<=3?60:n<=6?41:34;
  jobs.push({id:`tong-${n}`,label:`${numerals[n-1]}筒`,suit:'dots',rank:n,pipCount:n,positions:dotPositions[n],body:dotPositions[n].map(([x,y],i)=>pip(x,y,r,n===1?'red':n===2?(i===0?'green':'red'):n===3?['green','red','blue'][i]:n===5&&i===2?'red':n===9?['blue','blue','blue','red','red','red','green','green','green'][i]:'blue')).join('')});
 }
 for(let n=1;n<=9;n++)jobs.push({id:`tiao-${n}`,label:`${numerals[n-1]}条`,suit:'bamboo',rank:n,bambooCount:n,positions:bambooPositions[n],body:bambooPositions[n].map(([x,y,w,h],i)=>bamboo(x,y,w,h,n===7&&i===0)).join('')});
 const honors=[['wind-east','东','winds','#244d59'],['wind-south','南','winds','#244d59'],['wind-west','西','winds','#244d59'],['wind-north','北','winds','#244d59'],['dragon-red','中','dragons','#ad302b'],['dragon-green','發','dragons','#1c684e']];
 for(const [id,ch,suit,color]of honors)jobs.push({id,label:ch==='發'?'发':ch,suit,glyphs:[ch],body:glyph(ch,218,310,264,285,color)});
 jobs.push({id:'dragon-white',label:'白',suit:'dragons',whiteDragonFrame:true,body:'<g data-white-dragon="1"><rect x="107" y="164" width="222" height="292" rx="14" fill="none" stroke="#28586c" stroke-width="22"/><rect x="124" y="181" width="188" height="258" rx="7" fill="none" stroke="#bf9b53" stroke-width="3"/></g>'});
 for(const j of jobs){
  const symbolFile=path.join(root,'symbols',j.id+'.svg'),symbolPNG=path.join(root,'symbols',j.id+'.png'),faceFile=path.join(root,'faces',j.id+'.png');
  const svgText=svg(j.body);fs.writeFileSync(symbolFile,svgText+'\n');
  await sharp(Buffer.from(svgText)).png().toFile(symbolPNG);
  await sharp(blank).composite([{input:symbolPNG}]).png().toFile(faceFile);
  const item={...j};delete item.body;
  const symbolRecord={file:rel(symbolFile),sha256:sha(symbolFile),operation:'Deterministic original SVG symbols; KaiTi text converted to vector outlines, exact pip/bamboo counts. No model call.',fontSource:j.glyphs?{name:'KaiTi',outlineData:'assets/tiles/source/glyph-outlines.json',sha256:sha(sourcePath('glyph-outlines.json')),fontFileDistributed:false}:null,semantic:{label:j.label,suit:j.suit,rank:j.rank??null,pipCount:j.pipCount??null,bambooCount:j.bambooCount??null,glyphs:j.glyphs??null,whiteDragonFrame:j.whiteDragonFrame??false},canvas:{width:W,height:H},checks:{exactSemantics:'passed',visual:'pending'}};
  writeJson(symbolFile+'.asset.json',symbolRecord);
  derive(symbolPNG,[],['render native deterministic vector symbol SVG'],{symbolSource:{file:rel(symbolFile),sha256:sha(symbolFile)},semantic:symbolRecord.semantic});
  derive(faceFile,[blank],['alpha composite exact vector symbol over generated hand-painted blank tile'],{symbolSource:{file:rel(symbolFile),sha256:sha(symbolFile)},symbolRenderer:'sharp/librsvg, vector paths without runtime font dependency',semantic:symbolRecord.semantic});
  entries.push({...item,file:rel(faceFile),sha256:sha(faceFile),record:rel(faceFile)+'.generation.json',symbol:rel(symbolFile),symbolPNG:rel(symbolPNG),canvas:{width:W,height:H},pivot:{x:.5,y:.5},contentBounds:blankExport.contentBounds,status:'technical checked, pending visual review'});
 }
 const frameSVG=svg('<rect x="5" y="14" width="438" height="611" rx="51" fill="none" stroke="#efd47d" stroke-width="7"/><rect x="10" y="19" width="428" height="601" rx="46" fill="none" stroke="#63c4a1" stroke-width="3"/>');
 fs.writeFileSync(path.join(root,'states','tile-highlight.svg'),frameSVG+'\n');
 await sharp(Buffer.from(frameSVG)).png().toFile(path.join(root,'states','tile-highlight.png'));
 derive(path.join(root,'states','tile-highlight.png'),[],['render deterministic state outline overlay'],{vectorSource:'assets/tiles/states/tile-highlight.svg'});
 writeJson(path.join(root,'manifest.json'),{schemaVersion:1,title:'道家Q版麻将基础牌',generatedAt:new Date().toISOString(),canvas:{width:W,height:H,format:'RGBA PNG',sourceNative:[1024,1536],upscaled:false},sourceStyleReferences:refs,modelDisclosure:'Generated painted blanks/backs use builtin image_gen target GPT Image 2.5 Sunburst/max. Actual model/quality unconfirmed. Tile face symbols are deterministic native vectors, not separately generated images.',base:{blank:{file:rel(blank),record:rel(blank)+'.generation.json',...blankExport},back:{file:rel(back),record:rel(back)+'.generation.json',...backExport}},tiles:entries,stateAndOrientationMap:{faceUp:{selfDegrees:0,rightDegrees:270,oppositeDegrees:180,leftDegrees:90,note:'Clockwise screen rotation with owner at screen edge: self bottom 0, right 270, top 180, left 90. Glyph top points toward table center; never mirror.'},faceDown:'Use tile-back.png; use same 4 seat rotations. Remote concealed hands show backs only.',hand:{suggestedDisplay:[112,160],pivot:[.5,.95],selectedRaisePxAtDisplaySize:12,spacingPx:96},discardAndMeld:{suggestedDisplay:[45,64],pivot:[.5,.5],note:'Preserve aspect; rotate whole sprite for each seat. Keep identical face identities in meld groups.'},normal:{tint:'#FFFFFF',opacity:1},selected:{tint:'#FFFFFF',opacity:1,raiseAtDisplayPx:12,outline:'assets/tiles/states/tile-highlight.png'},legalAction:{outline:'assets/tiles/states/tile-highlight.png'},unplayable:{rendererEffect:'desaturate(1), brightness(.60); preserve alpha; no symbol replacement',interactive:false},hover:{rendererEffect:'brightness(1.06)',scale:1},disabled:{sameAs:'unplayable'},tileScaling:'Scale whole sprite uniformly; no nine-slice. Symbols can be drawn separately from outlined SVG at any size.'},counts:{faces:entries.length,characters:9,dots:9,bamboo:9,winds:4,dragons:3,blank:1,back:1,highlightOverlay:1},checks:{semantic:'passed',alpha:'passed',visual:'pending'}});
 console.log(JSON.stringify({faces:entries.length,canvas:[W,H],blankExport,backExport},null,2));
}
main().catch(e=>{console.error(e);process.exit(1)});

