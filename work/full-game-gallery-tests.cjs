const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
const payload=JSON.parse(script.match(/const DATA=([\s\S]*?);\s*let tab=/)[1]);
function el(){return {value:'',innerHTML:'',textContent:'',hidden:false,open:false,src:'',href:'',alt:'',className:'',dataset:{},classList:{set:new Set(),toggle(k,v){if(v===undefined)v=!this.set.has(k);if(v)this.set.add(k);else this.set.delete(k);return v}},showModal(){this.open=true},close(){this.open=false}}}
const nodes={};for(const id of ['stats','search','section-title','section-note','bg','grid','filters','viewer','view-title','view-img','view-info','view-open','view-media','view-bg','close','prev','next'])nodes[id]=el();
const tabNames=['pages','components','tiles','characters','scenes','props','fx','branding'];
const tabs=tabNames.map(x=>{const e=el();e.dataset.tab=x;return e});
let views=[],filters=[];const body=el(),events={};
const doc={body,querySelector(s){const n=nodes[s.slice(1)];if(!n)throw Error('unknown selector '+s);return n},querySelectorAll(s){if(s==='[data-tab]')return tabs;if(s==='[data-view]'){views=[...nodes.grid.innerHTML.matchAll(/data-view="(\d+)"/g)].map(m=>{const e=el();e.dataset.view=m[1];return e});return views}if(s==='[data-filter]'){filters=[...nodes.filters.innerHTML.matchAll(/data-filter="([^"]+)"/g)].map(m=>{const e=el();e.dataset.filter=m[1];return e});return filters}throw Error('unknown selector '+s)},addEventListener(k,f){events[k]=f}};
vm.runInNewContext(script,{document:doc,console,encodeURI,Set,String},{timeout:10000});
const tests=[];
function test(name,fn){fn();tests.push({name,status:'passed'})}
function cards(){return (nodes.grid.innerHTML.match(/<article /g)||[]).length}
function tab(name){nodes.search.value='';tabs.find(x=>x.dataset.tab===name).onclick()}
test('Initial page count',()=>assert.equal(cards(),payload.pages.length));
test('All32 page IDs represented',()=>{for(let i=1;i<=32;i++)assert(payload.pages.some(x=>x.id==='UI'+String(i).padStart(2,'0')))});
test('UI14 search',()=>{nodes.search.value='UI14';nodes.search.oninput();assert.equal(cards(),1);assert(nodes.grid.innerHTML.includes('角色与头像'))});
test('Image viewer opens and closes',()=>{views[0].onclick();assert(nodes.viewer.open);assert(nodes['view-img'].src.includes('ui14'));nodes.close.onclick();assert(!nodes.viewer.open)});
test('UI29 pending and claimed present',()=>{nodes.search.value='UI29';nodes.search.oninput();assert.equal(cards(),2);assert(nodes.grid.innerHTML.includes('已领取'))});
test('UI27 has3 tutorial steps',()=>{nodes.search.value='UI27';nodes.search.oninput();assert.equal(cards(),3)});
for(const name of tabNames.slice(1))test(name+' tab count',()=>{tab(name);assert.equal(cards(),payload[name].length)});
test('Gameplay component filter',()=>{tab('components');const b=filters.find(x=>x.dataset.filter==='对局组件');assert(b);b.onclick();assert.equal(cards(),payload.components.filter(x=>x.group==='对局组件').length)});
test('Alpha background toggle',()=>{nodes.bg.onclick();assert(body.classList.set.has('dark'));nodes.bg.onclick();assert(!body.classList.set.has('dark'))});
test('Tile search remains exact',()=>{tab('tiles');nodes.search.value='wan-1';nodes.search.oninput();assert.equal(cards(),1)});
test('Flower filter has8 optional faces',()=>{tab('tiles');const b=filters.find(x=>x.dataset.filter==='可选花牌');assert(b);b.onclick();assert.equal(cards(),8)});
test('All16 expressions searchable',()=>{tab('characters');nodes.search.value='expression-';nodes.search.oninput();assert.equal(cards(),16)});
test('Scene cards are landscape',()=>{tab('scenes');assert(!nodes.grid.className.includes('asset-grid'));assert(nodes.bg.hidden)});
test('Scene table-theme filter has2 extras',()=>{const b=filters.find(x=>x.dataset.filter==='牌桌主题');assert(b);b.onclick();assert.equal(cards(),2)});
test('Props exclude flower duplicates',()=>{tab('props');assert.equal(cards(),34);assert(!payload.props.some(x=>x.file.startsWith('assets/tiles/flowers/')))});
test('FX has24 stage frames',()=>{tab('fx');const b=filters.find(x=>x.dataset.filter==='特效阶段帧');assert(b);b.onclick();assert.equal(cards(),24)});
test('Next previous keyboard and background controls',()=>{views[0].onclick();const src=nodes['view-img'].src;nodes.next.onclick();assert.notEqual(nodes['view-img'].src,src);nodes.prev.onclick();assert.equal(nodes['view-img'].src,src);events.keydown({key:'ArrowRight'});assert.notEqual(nodes['view-img'].src,src);events.keydown({key:'ArrowLeft'});assert.equal(nodes['view-img'].src,src);nodes['view-bg'].onclick();assert(nodes['view-media'].classList.set.has('light'));nodes.close.onclick()});
test('Global primary file list is deduplicated',()=>assert.equal(new Set(payload.assets.map(x=>x.file)).size,payload.primaryAssetCount));
test('All primary files and source records exist',()=>{for(const a of payload.assets){assert(fs.existsSync(path.join(root,a.file)),a.file);assert(fs.existsSync(path.join(root,a.record)),a.record)}});
test('No empty result breaks rendering',()=>{tab('pages');nodes.search.value='no_such_asset_734819';nodes.search.oninput();assert.equal(cards(),0);assert(nodes.grid.innerHTML.includes('没有匹配'))});
const result={status:'passed',testCount:tests.length,tests,method:'Static JavaScript executed against an in-memory mock DOM, plus direct file checks; no browser or network',limits:'Real browser layout/rendering/interaction was not run because local file navigation was policy-blocked.'};
fs.writeFileSync(path.join(root,'exports/full-game-gallery-validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
