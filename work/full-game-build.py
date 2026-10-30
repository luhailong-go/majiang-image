from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib,re,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stamp():return datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
def normalize(a,group):
    a=dict(a);p=R/a['file']
    if a.get('sha256') and sha(p)!=a['sha256']:raise ValueError('Manifest hash mismatch '+a['file'])
    with Image.open(p) as im:w,h=im.size;mode=im.mode
    rp=a.get('record') or a['file']+'.generation.json'
    meta=read(rp);prompt=meta.get('prompt');prompt=prompt.get('file') if isinstance(prompt,dict) else prompt
    return {**a,'title':a.get('title') or a.get('name') or a.get('label') or a.get('id') or p.stem,'id':a.get('id') or p.stem,'group':group,'width':w,'height':h,'mode':mode,'sha256':sha(p),'record':rp,'prompt':prompt}
def unique(items):
    result=[];seen=set()
    for a in items:
        if a['file'] not in seen:seen.add(a['file']);result.append(a)
    return result

old=read('exports/ui-delivery-manifest.json')
pages=list(old['pages']);components=list(old['components']);characters=list(old['characters']);tiles=list(old['tiles'])
titles={25:'装扮设置',26:'角色详情',27:'新手引导',28:'公告详情',29:'奖励领取',30:'成就收藏',31:'积分排行',32:'物品收藏'}
for p in sorted((R/'designs/ui/full-game').rglob('ui*.png')):
    if any(x in p.parts for x in ['component-sources','edit-sources']):continue
    if any(x in p.stem for x in ['source','before','rejected','draft','attempt','old']):continue
    m=re.match(r'ui(\d\d)',p.stem)
    if not m or int(m[1]) not in titles:continue
    i=int(m[1]);file=p.relative_to(R).as_posix();suffix=' · 已领取' if 'claimed' in p.stem else ' · 操作提示' if 'action' in p.stem else ' · 引导完成' if 'tutorial-complete' in p.stem else ' · 选牌' if 'tutorial-select' in p.stem else ''
    pages.append(normalize({'id':f'UI{i:02d}','file':file,'name':titles[i]+suffix},'配套界面'))
cm=read('assets/ui/full-game/components/manifest.json')
components+= [normalize(a,'配套组件') for a in cm['assets']]
charManifest=read('assets/characters/full-game/manifest.json')
characterAliases=[]
for a in charManifest['assets']:
    if a.get('id')=='fullbody-daotong' and any(c['sha256']==a['sha256'] for c in characters):
        target=next(c for c in characters if c['sha256']==a['sha256'])
        target['group']='完整角色立绘'
        for field in ['role','identity','anchor','scaleMode']:
            if field in a:target[field]=a[field]
        characterAliases.append({'id':a['id'],'file':a['file'],'targetFile':target['file'],'sha256':a['sha256'],'purpose':'same existing accepted daotong art; count once'})
        continue
    characters.append(normalize(a,'角色表情' if ('expression' in a.get('role','') or 'expression' in a.get('kind','') or 'expressions/' in a['file']) else '完整角色立绘'))
flowerManifest=read('assets/tiles/flowers/manifest.json')
tiles += [normalize(a,'可选花牌') for a in flowerManifest.get('assets',flowerManifest.get('tiles',[]))]
propManifest=read('assets/props/full-game/manifest.json')
props=[normalize(a,'交流表情' if 'emote' in a.get('kind','') or '/emotes/' in a['file'] else '物品图标' if '/items/' in a['file'] else '牌桌道具') for a in propManifest['assets'] if not a['file'].startswith('assets/tiles/flowers/')]
fxManifest=read('assets/fx/full-game/manifest.json');fx=[normalize(a,'特效阶段帧' if a.get('kind')=='animation_frame' else '中文提示与装饰') for a in fxManifest['assets']]
scenes=[normalize(a,'牌桌主题' if a.get('usage')=='table' else '纯场景') for a in read('assets/scenes/full-game/manifest.json')['assets']]
branding=[normalize(a,'牌背主题' if a['id'].startswith('tile-back') else '标识与加载') for a in read('assets/branding/full-game/manifest.json')['assets']]
characters=unique(characters);tiles=unique(tiles);props=unique(props)
ids={a['id'] for a in pages};missing=[f'UI{i:02d}' for i in range(1,33) if f'UI{i:02d}' not in ids]
allAssets=unique(pages+components+characters+tiles+props+fx+scenes+branding)
for asset in allAssets:asset['assetKey']=asset['file'].removesuffix('.png')
data={'schemaVersion':2,'project':'道家Q版麻将完整游戏美术','generatedAt':stamp(),'contract':'docs/FULL_GAME_ART_SCOPE.md','previousContract':'docs/FULL_UI_SCOPE.md','contractCompleteCount':len(ids),'contractTotal':32,'missingIds':missing,'pages':pages,'components':components,'characters':characters,'tiles':tiles,'props':props,'fx':fx,'scenes':scenes,'branding':branding,'states':old['states'],'baseTileFaceCount':34,'optionalFlowerCount':8,'tileFaceCount':42,'fullBodyCharacterCount':4,'expressionCount':16,'clipCount':6,'primaryAssetCount':len(allAssets),'assets':allAssets,'sourceManifests':old.get('sourceManifests',[])+['assets/ui/full-game/components/manifest.json','assets/characters/full-game/manifest.json','assets/tiles/flowers/manifest.json','assets/props/full-game/manifest.json','assets/fx/full-game/manifest.json','assets/scenes/full-game/manifest.json','assets/branding/full-game/manifest.json'],'browserVerification':old['browserVerification'],'modelEvidence':old['modelEvidence'],'clientIntegrated':False,'uploaded':False,'remoteConfigured':False,'deliveryStatus':'pending_full_game_final_validation','package':'exports/mahjong-complete-game-art-v2.zip','optionalModules':['花牌','成就','排行榜','物品收藏'],'scopeLimitations':['默认通用四人横屏2D麻将；正式名称与地方番型未指定','角色为立绘加独立表情，6类特效为真实关键阶段帧加可选补间；无角色战斗或视频动画合同','真实客户端/服务端/平台与设备导入另行验收','浏览器file协议被策略拒绝；不绕行，图片实看与静态脚本检查分别记录']}
data['fullBodyCharacterCount']=len({a['file'] for a in characters if a.get('role') in ['full_body','fullbody'] or a.get('id')=='welcome-daotong'})
data['expressionCount']=len([a for a in characters if a.get('role') in ['expression','expression_avatar']])
data['characterAliases']=characterAliases
data['optionalFlowerCount']=len([a for a in tiles if a['group']=='可选花牌'])
data['baseTileFaceCount']=old['tileFaceCount']
data['tileFaceCount']=data['baseTileFaceCount']+data['optionalFlowerCount']
data['clipCount']=read('assets/fx/full-game/final-validation.json')['runtimeClipsChecked']
data['sourceManifests'].append('designs/ui/full-game/manifest.json')
data['sourceManifestHashes']={p:sha(R/p) for p in data['sourceManifests']}
extraStates={
    'cosmetic.unselected':(['UI25'],['cosmetic-card-unselected']),
    'cosmetic.preview_selected':(['UI25'],['cosmetic-card-selected']),
    'cosmetic.in_use':(['UI25'],['cosmetic-card-in-use']),
    'character.in_use':(['UI26'],[]),
    'tutorial.select':(['UI27'],['tutorial-focus-frame','tutorial-tap-hand']),
    'tutorial.actions':(['UI27'],['tutorial-arrow','tutorial-step-marker']),
    'tutorial.complete':(['UI27'],[]),
    'reward.not_achieved':(['UI29'],['reward-card-default']),
    'reward.claimable':(['UI29'],['reward-card-claimable']),
    'reward.claimed':(['UI29'],['reward-card-claimed']),
    'achievement.locked':(['UI30'],['achievement-frame-locked']),
    'achievement.unlocked':(['UI30'],['achievement-frame-unlocked']),
    'ranking.top_three':(['UI31'],['rank-marker-gold','rank-marker-silver','rank-marker-bronze']),
    'ranking.self':(['UI31'],[]),
    'inventory.default':(['UI32'],['item-slot-default']),
    'inventory.selected':(['UI32'],['item-slot-selected']),
    'inventory.disabled':(['UI32'],['item-slot-disabled']),
    'inventory.new':(['UI32'],['item-slot-new']),
    'announcement.detail':(['UI28'],[])}
for state,(uiIds,componentIds) in extraStates.items():
    files=[p['file'] for p in pages if p['id'] in uiIds]+[c['file'] for c in components if c.get('id') in componentIds]
    ok=all(any(p['id']==id for p in pages) for id in uiIds) and all(any(c.get('id')==id for c in components) for id in componentIds)
    if state=='reward.claimable':files=[p for p in files if 'reward-claimed.png' not in p]
    if state=='reward.claimed':files=[p for p in files if 'reward-pending.png' not in p]
    if state.startswith('tutorial.'):
        step={'tutorial.select':'tutorial-select','tutorial.actions':'tutorial-actions','tutorial.complete':'tutorial-complete'}[state]
        files=[p for p in files if 'designs/ui/' not in p or step in p]
    data['states'].append({'state':state,'uiIds':uiIds,'componentIds':componentIds,'files':files,'status':'mapped' if ok else 'pending','binding':'art reference; actual application data and events control transitions'})
write('exports/full-game-art-manifest.json',data)
template=(R/'work/full_ui/gallery-template.html').read_text(encoding='utf-8-sig')
template=template.replace('麻将 UI · 美术交付画廊','麻将完整游戏美术 · v2').replace('麻将 UI 美术交付画廊','麻将完整游戏美术画廊')
template=template.replace('按页面、状态与基础素材浏览完整交付。','按界面、角色、场景、牌具与特效浏览完整交付。')
template=template.replace('docs/FULL_UI_SCOPE.md','docs/FULL_GAME_ART_SCOPE.md').replace('docs/UI_INTEGRATION.md','docs/FULL_GAME_INTEGRATION.md').replace('exports/ui-delivery-manifest.json','exports/full-game-art-manifest.json')
template=template.replace('</div><input id="search"','<button data-tab="scenes">场景与桌面</button><button data-tab="props">牌具与物品</button><button data-tab="fx">对局特效</button><button data-tab="branding">标识与牌背</button></div><input id="search"')
template=template.replace('characters:"迎宾道童与四座头像"','characters:"四位角色与16种表情",scenes:"独立场景与牌桌主题",props:"牌具、交流与物品",fx:"中文提示与动态效果阶段",branding:"牌背、标题与应用图标"')
template=template.replace('tiles:"34 种牌面与基础牌材"','tiles:"34种标准牌面与8张可选花牌"')
template=template.replace('characters:"统一人物身份、画法与色彩。透明立绘已检查深浅底边缘。"','characters:"四位身份独立；透明全身与表情分别交付，深浅底验收。",scenes:"三张无字无人背景、两套新增空桌面；原青绿桌面见对局组件。",props:"花牌为可选规则；骰子点数精确。收藏与奖励图标不含现金充值。",fx:"6类真实四阶段效果，播放页与Aseprite图集见特效接入说明。",branding:"两套可选牌背；应用图标1024及较小尺寸为原生大图缩小。正式名称由客户端配置。"')
template=template.replace('DATA.contractCompleteCount+"/24"','DATA.contractCompleteCount+"/32"').replace('["基础牌面",DATA.tileFaceCount]','["标准/可选牌面",DATA.baseTileFaceCount+" + "+DATA.optionalFlowerCount],["角色/表情",DATA.fullBodyCharacterCount+" / "+DATA.expressionCount],["主PNG",DATA.primaryAssetCount]')
template=template.replace('tab==="pages"?"":" asset-grid"','(tab==="pages"||tab==="scenes")?"":" asset-grid"')
template=template.replace('tab==="pages";$("#grid")','(tab==="pages"||tab==="scenes");$("#grid")')
template=template.replace('这里用于查看美术文件，不是可联机麻将客户端。','这里用于查看美术文件；客户端尚未接入。 <a href="assets/fx/full-game/index.html">特效播放</a> · <a href="docs/FULL_GAME_INTEGRATION.md">完整接入说明</a>')
if '__DELIVERY_DATA__' not in template:raise ValueError('Missing payload slot')
(R/'index.html').write_text(template.replace('__DELIVERY_DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
(R/'work/full-game-gallery-template.html').write_text(template,encoding='utf-8')
print(json.dumps({'pages':len(pages),'pageIds':len(ids),'components':len(components),'characters':len(characters),'tiles':len(tiles),'props':len(props),'fx':len(fx),'scenes':len(scenes),'branding':len(branding),'primaryAssets':len(allAssets),'missing':missing},ensure_ascii=False))
