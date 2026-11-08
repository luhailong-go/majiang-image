const fs=require("fs"),vm=require("vm"),path=require("path"),assert=require("assert");
const root=String.raw`D:\work\majiang-image`;
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
const payload=JSON.parse(script.match(/const DATA=([\s\S]*?);\s*let tab=/)[1]);
function el(){return {value:"",innerHTML:"",textContent:"",hidden:false,open:false,src:"",href:"",alt:"",className:"",dataset:{},classList:{set:new Set(),toggle(k,v){if(v===undefined)v=!this.set.has(k);if(v)this.set.add(k);else this.set.delete(k);return v}},showModal(){this.open=true},close(){this.open=false}}}
const nodes={};for(const id of ["stats","search","section-title","section-note","bg","grid","filters","viewer","view-title","view-img","view-info","view-open","view-media","view-bg","close","prev","next"])nodes[id]=el();
const tabs=["pages","components","tiles","characters"].map(x=>{const e=el();e.dataset.tab=x;return e});
let views=[],filters=[];const body=el(),events={};
const doc={body,querySelector(s){const n=nodes[s.slice(1)];if(!n)throw Error("unknown selector "+s);return n},querySelectorAll(s){if(s==="[data-tab]")return tabs;if(s==="[data-view]"){views=[...nodes.grid.innerHTML.matchAll(/data-view="(\d+)"/g)].map(m=>{const e=el();e.dataset.view=m[1];return e});return views}if(s==="[data-filter]"){filters=[...nodes.filters.innerHTML.matchAll(/data-filter="([^"]+)"/g)].map(m=>{const e=el();e.dataset.filter=m[1];return e});return filters}throw Error("unknown selector "+s)},addEventListener(k,f){events[k]=f}};
vm.runInNewContext(script,{document:doc,console,encodeURI,Set,String},{timeout:5000});
const tests=[];
function test(name,fn){fn();tests.push({name,status:"passed"})}
function cards(){return (nodes.grid.innerHTML.match(/<article /g)||[]).length}
test("Initial page rendering data",()=>assert.equal(cards(),payload.pages.length));
test("Search UI14",()=>{nodes.search.value="UI14";nodes.search.oninput();assert.equal(cards(),1);assert(nodes.grid.innerHTML.includes("角色与头像"))});
test("Image viewer open/close handlers",()=>{views[0].onclick();assert(nodes.viewer.open);assert(nodes["view-img"].src.includes("ui14"));nodes.close.onclick();assert(!nodes.viewer.open)});
test("Components tab",()=>{nodes.search.value="";tabs[1].onclick();assert.equal(cards(),payload.components.length)});
test("Gameplay filter",()=>{const b=filters.find(x=>x.dataset.filter==="对局组件");assert(b);b.onclick();assert.equal(cards(),payload.components.filter(x=>x.group==="对局组件").length)});
test("Background toggle",()=>{nodes.bg.onclick();assert(body.classList.set.has("dark"))});
test("Tiles tab data",()=>{tabs[2].onclick();assert.equal(cards(),payload.tiles.length)});
test("Tile search",()=>{nodes.search.value="wan-1";nodes.search.oninput();assert.equal(cards(),1)});
test("Character tab data",()=>{nodes.search.value="";tabs[3].onclick();assert.equal(cards(),payload.characters.length)});
test("Next and previous handlers",()=>{views[0].onclick();const src=nodes["view-img"].src;nodes.next.onclick();assert.notEqual(nodes["view-img"].src,src);nodes.prev.onclick();assert.equal(nodes["view-img"].src,src)});
const result={status:"passed",testCount:tests.length,tests,method:"Static JavaScript source executed against an in-memory mock DOM, with no browser or network",limits:"Does not assert real-browser layout or rendering. Browser file:// navigation was policy-blocked."};
fs.writeFileSync(path.join(root,"exports/gallery-script-validation.json"),JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result));
