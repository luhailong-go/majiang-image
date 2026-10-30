from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=read('exports/full-game-art-manifest.json')
lookup={}
for a in old['assets']:
    lookup.setdefault(a.get('id') or Path(a['file']).stem,a)
    lookup.setdefault(Path(a['file']).stem,a)
for m in ['assets/ui/production-v3/empty/manifest.json','assets/ui/production-v3/forms/manifest.json','assets/ui/production-v3/gameplay/manifest.json','assets/branding/yunjian-queshe/manifest.json']:
    if (R/m).is_file():
        for a in read(m).get('assets',[]):lookup[a['id']]=a
layouts={};n=0
def node(kind,rect,**kw):
    global n;n+=1;return {'id':'node-'+str(n),'type':kind,'rect':rect,**kw}
def image(id,rect,**kw):
    a=lookup[id]
    return node('image',rect,asset=id,file=a['file'],record=a.get('record',a['file']+'.generation.json'),fit='contain',**kw)
def skin(id,rect,**kw):
    a=lookup[id];policy=a.get('resizePolicy',{});nine=a.get('nineSlice')
    if not nine and isinstance(policy,dict):nine=policy.get('nineSlice')
    if nine:return image(id,rect,fitMode='nine_slice',nineSlice=nine,stretchAxes=policy.get('stretchAxes',['x','y']),**kw)
    return image(id,rect,**kw)
def text(value,rect,size=28,color='#183d35',align='left',**kw):return node('text',rect,text=value,fontSize=size,color=color,align=align,fontFamily='Microsoft YaHei / platform CJK font',**kw)
def button(value,x,y,w=250,target=None,enabled=True,secondary=False,**kw):
    id='button-secondary-normal' if secondary else 'button-primary-normal'
    return node('button',[x,y,w,64],file=lookup[id]['file'],asset=id,record=lookup[id]['record'],text=value,fontSize=25,color='#183d35' if secondary else '#fff9e9',target=target,enabled=enabled,nineSlice=lookup[id]['nineSlice'],stretchAxes=['x'],stateAssets={s:lookup[id.replace('normal',s)]['file'] for s in ['normal','pressed','selected','disabled']},**kw)
def card(x,y,w,h):return skin('content-card',[x,y,w,h])
def title(value):return [image('title-plaque',[560,24,480,166]),text(value,[580,82,440,60],38,'#fff9e9','center')]
def base(id,name,bg='courtyard-day',window=True):
    layers=[image(bg,[0,0,1600,900],fitMode='cover')]
    if window:layers += [skin('content-card',[58,82,1484,760]),skin('window-frame',[58,82,1484,760])]
    layers += title(name)
    if id not in ['UI01','UI02','UI03']:layers += [image('icon-close',[1438,86,70,70],target='UI03',interactive=True)]
    layouts[id]={'id':id,'name':name,'canvas':[1600,900],'safeRect':[100,150,1400,650],'layers':layers,'bindingNotes':[]}
    return layers
def labelrow(l,label,value,y,x=210,w=1100):
    l.extend([card(x,y,w,82),text(label,[x+30,y+20,250,42],25),text(value,[x+315,y+20,w-350,42],25)])
def field(l,label,value,x,y,w=620):
    l.extend([text(label,[x,y-43,w,40],25),skin('input-field',[x,y,w,70]),text(value,[x+24,y+16,w-48,40],26,binding=label)])
roles=['daotong','healer','master','swordswoman'];roleNames=['金带道童','银发医师','白眉老道','黑发侠女']
def portrait(l,role,x,y,size=112,frame=True,binding=None):
    l.append(image('expression-'+role+'-happy',[x,y,size,size],binding=binding))
    if frame:l.append(image('avatar-frame',[x-12,y-12,size+24,size+24]))
def tabs(l,items,x=180,y=177,active=0):
    for i,label in enumerate(items):
        l.append(skin('tab-selected' if i==active else 'tab-normal',[x+i*225,y,210,65]));l.append(text(label,[x+i*225+5,y+17,200,40],25,'#fff9e9' if i==active else '#183d35','center'))
def empty(l,id,label,action='返回',target='UI03'):
    l.extend([image(id,[620,275,360,360]),text(label,[400,650,800,50],31,align='center'),button(action,675,730,250,target)])

l=base('UI01','启动加载','waterside-night',False)
l.extend([image('welcome-daotong',[560,180,480,480]),card(435,620,730,86),text('正在整理牌桌，请稍候',[450,640,700,48],31,align='center'),skin('slider-track',[440,720,720,48]),image('loading-ring',[750,760,90,90]),button('进入游戏',1150,740,260,'UI02')])
l=base('UI02','麻将','waterside-night',False)
l.extend([image('welcome-daotong',[160,170,600,600]),card(860,235,550,450),button('进入游戏',1000,310,280,'UI03'),button('账号入口',1000,410,280,None,secondary=True),image('checkbox-on',[940,550,46,46]),text('同意用户协议与隐私说明',[995,555,370,45],23),button('规则帮助',1000,610,280,'UI22',secondary=True)])
l=base('UI03','麻将大厅','courtyard-day',False)
l.extend([image('welcome-daotong',[130,180,610,610]),card(850,215,590,460),text('欢迎来到云间牌桌',[930,245,430,55],34,align='center'),button('休闲匹配',1010,340,280,'UI04'),button('创建房间',920,445,220,'UI05',secondary=True),button('加入房间',1160,445,220,'UI06',secondary=True),button('新手引导',1010,550,280,'UI27',secondary=True)])
if (R/'config/brand.json').is_file():
    brand=read('config/brand.json')
    for ui in ['UI01','UI02']:
        layers=layouts[ui]['layers']
        layers[:]=[a for a in layers if a.get('asset')!='title-plaque' and not(a['type']=='text' and a.get('text') in ['启动加载','麻将'])]
        layers.insert(1,image('yunjian-queshe-logo-primary',[550,0,500,235],sourceRect=[24,128,1512,896],binding='brand.primaryLogo'))
        layouts[ui]['brandConfig']='config/brand.json'
        if ui=='UI01':
            for a in layers:
                if a.get('asset')=='welcome-daotong':a['rect']=[580,245,440,380]
    for a in layouts['UI03']['layers']:
        if a.get('text')=='麻将大厅':a.update(text=brand['gameName'],binding='brand.gameName')
        if a.get('text')=='欢迎来到云间牌桌':a.update(text='欢迎来到'+brand['gameName'],binding='brand.welcomeText')
for i,(icon,label,target) in enumerate([('icon-profile','资料','UI13'),('icon-friends','好友','UI15'),('icon-mail','邮件','UI17'),('icon-records','战绩','UI19'),('icon-settings','设置','UI21'),('icon-help','帮助','UI22')]):
    x=185+i*205;l.extend([image(icon,[x,735,68,68],target=target,interactive=True),text(label,[x-20,806,110,40],23,'#183d35','center')])
l=base('UI04','休闲匹配')
l.extend([image('loading-ring',[685,275,230,230]),text('正在寻找同桌牌友',[440,540,720,55],34,align='center'),text('匹配状态由服务返回；此处为排布样例',[390,607,820,44],24,align='center'),button('取消匹配',525,727,250,'UI03',secondary=True),button('进入牌桌',825,727,250,'UI09',enabled=False,binding='match.state == matched')])
l=base('UI05','创建房间');tabs(l,['通用设置','规则说明'])
for i,(label,val) in enumerate([('对局类型','四人好友房'),('对局局数','示例 8 局'),('花牌','可选；以实际房间规则为准'),('加入方式','房间号加入')]):labelrow(l,label,val,280+i*100)
l.extend([button('返回大厅',510,735,260,'UI03',secondary=True),button('创建房间',835,735,260,'UI07')])
l=base('UI06','加入房间');field(l,'六位房间号','1  0  2  4  8  6',440,250,720)
for i,value in enumerate(['1','2','3','4','5','6','7','8','9','清空','0','删除']):
    x=545+(i%3)*185;y=365+(i//3)*88;l.append(skin('keypad-key',[x,y,140,72]));l.append(text(value,[x+5,y+20,130,36],26,align='center'))
l.extend([button('返回',390,760,230,'UI03',secondary=True),button('确认加入',980,760,230,'UI07')])
l=base('UI07','好友房间');l.append(text('房间号：102486',[180,174,700,46],30,binding='room.code'))
for i,role in enumerate(roles):
    x=180+i*320;l.append(card(x,270,290,365));portrait(l,role,x+85,303,120,binding='players['+str(i)+'].portrait');l.append(text(roleNames[i],[x+15,465,260,46],27,align='center',binding='players['+str(i)+'].name'));l.append(text('房主 · 已准备' if i==0 else ('已准备' if i<3 else '未准备'),[x+15,525,260,42],24,align='center',binding='players['+str(i)+'].ready'))
l.extend([button('房间已满',240,720,260,'UI08',enabled=False,secondary=True,binding='room.occupiedSeats < room.capacity'),button('取消准备',670,720,260,secondary=True),button('等待全部准备',1080,720,280,'UI09',enabled=False,binding='room.localIsHost && room.allReady')])
l=base('UI08','邀请好友');field(l,'搜索好友','输入昵称或编号',180,230,600)
for i,role in enumerate(roles[1:]):
    y=340+i*130;l.append(card(180,y,1240,115));portrait(l,role,220,y+20,75);l.append(text(roleNames[i+1],[340,y+28,400,46],29));l.append(text('在线' if i!=1 else '离线',[850,y+30,160,44],25));l.append(button('邀请' if i!=1 else '暂不可邀请',1115,y+26,240,None,enabled=i!=1))
l.append(button('返回房间',660,760,280,'UI07',secondary=True))

tileIds=['wan-1','wan-2','wan-3','wan-4','wan-5','wan-6','wan-7','wan-8','wan-9','tong-1','tong-2','tiao-1','tiao-2','zhong']
# Derive valid filenames from the tile domain, never from screen thumbnails.
tileFiles=[a['file'] for a in old['tiles'] if '/faces/' in a['file']]
if not tileFiles:tileFiles=[a['file'] for a in old['tiles'] if Path(a['file']).stem not in ['tile-back','tile-blank','tile-highlight'] and 'flowers' not in a['file']][:34]
for a in old['tiles']:lookup.setdefault(Path(a['file']).stem,a)
def tile(l,index,rect,rotation=0,face=True):
    file=tileFiles[index%len(tileFiles)] if face else lookup['tile-back']['file']
    a=next(a for a in old['tiles'] if a['file']==file)
    l.append(node('image',rect,file=file,record=a.get('record',file+'.generation.json'),fit='contain',rotation=rotation,asset=Path(file).stem))
def table(id,name):
    l=base(id,name,'table-background',False)
    for i,(role,x,y) in enumerate([('daotong',180,680),('healer',55,335),('master',730,130),('swordswoman',1390,335)]):
        portrait(l,role,x,y,90,binding='table.playersByDisplaySeat['+str(i)+'].portrait');l.append(text(roleNames[i],[x-50,y+104,190,35],21,'#fff9e9','center',binding='table.playersByDisplaySeat['+str(i)+'].name'))
    l.extend([image('wind-round-dial',[670,325,260,247]),image('countdown-frame',[740,385,120,124]),text('18',[754,423,92,44],33,'#fff9e9','center',binding='turn.secondsRemaining'),image('dealer-badge',[265,650,65,54])])
    for i in range(14):tile(l,i,[350+i*63,730,63,90])
    for i in range(13):tile(l,i,[450+i*49,205,41,58],180,False)
    for i in range(10):tile(l,i,[230,285+i*37,37,53],90,False);tile(l,i,[1310,285+i*37,37,53],270,False)
    for i in range(12):tile(l,i,[452+(i%6)*38,335+(i//6)*52,34,49]);tile(l,i+12,[958+(i%6)*38,490+(i//6)*52,34,49],180)
    l.extend([image('icon-settings',[1420,80,65,65],target='UI21',interactive=True),image('icon-chat',[1420,165,65,65],target='UI16',interactive=True)])
    return l
l=table('UI09','四人对局');l.append(button('查看操作',1090,625,240,'UI10'))
l=table('UI10','操作选择')
for i,(value,enabled) in enumerate([('碰',True),('杠',False),('胡',False),('过',True)]):l.append(button(value,810+i*160,615,140,'UI09',enabled=enabled))
l.extend([card(410,560,350,122),text('候选牌组',[440,570,290,36],23),text('按当前合法候选显示',[440,620,290,36],21)])

def results(id,name,whole=False):
    l=base(id,name)
    l.append(text('整场积分' if whole else '单局积分',[570,178,460,50],31,align='center'))
    for i,role in enumerate(roles):
        x=200+i*310;l.append(image('settlement-card',[x,270,260,329]));portrait(l,role,x+80,285,100,False,binding='result.players['+str(i)+'].portrait');l.append(text(roleNames[i],[x+15,400,230,42],25,align='center',binding='result.players['+str(i)+'].name'));l.append(text('+240' if i==0 else '−80',[x+20,475,220,55],37,'#b52f20' if i==0 else '#196448','center',binding='result.players['+str(i)+'].score'))
    l.extend([button('返回大厅',470,725,280,'UI03',secondary=True),button('再来一场' if whole else '继续下一局',850,725,280,'UI07' if whole else 'UI09')]);return l
results('UI11','单局结算');results('UI12','整场结算',True)
l=base('UI13','个人资料');portrait(l,'daotong',280,280,220)
for i,(key,val) in enumerate([('昵称','青云小道'),('编号','示例玩家'),('当前角色','金带道童'),('个人签名','相逢一桌，轻松论牌')]):labelrow(l,key,val,240+i*110,x=650,w=720)
l.extend([button('角色与头像',250,650,280,'UI14'),button('返回大厅',980,740,280,'UI03',secondary=True)])
l=base('UI14','角色与头像')
for i,role in enumerate(roles):
    x=180+i*320;l.append(card(x,250,290,380));portrait(l,role,x+70,285,150);l.append(text(roleNames[i],[x+15,460,260,48],29,align='center'));l.append(button('查看详情',x+35,540,220,'UI26',secondary=True,role=role))
l.extend([text('外观选择不影响玩法与计分',[400,675,800,45],25,align='center'),button('确认选择',650,745,300,'UI13')])
l=base('UI15','好友与申请');tabs(l,['好友','好友申请','最近同桌']);field(l,'昵称或编号','搜索牌友',180,300,620)
for i,role in enumerate(roles[1:]):
    y=410+i*105;l.append(card(180,y,1240,95));portrait(l,role,215,y+15,62);l.append(text(roleNames[i+1],[330,y+25,350,42],27));l.append(text(['在线','离线','对局中'][i],[850,y+25,170,42],25));l.append(button('邀请' if i==0 else '查看',1120,y+16,240,'UI08',secondary=i!=0))
l.append(button('添加好友',1110,750,280))
l=base('UI16','快捷交流');tabs(l,['快捷语','表情'])
for i,value in enumerate(['大家好，准备开始吧','稍等一下，谢谢','打得漂亮','承让，下局再会','请保持轻松心情','很高兴同桌']):
    x=200+(i%2)*610;y=300+(i//2)*135;l.append(card(x,y,580,100));l.append(text(value,[x+30,y+30,520,45],29))
l.append(button('返回对局',650,750,300,'UI09',secondary=True))
l=base('UI17','邮件');tabs(l,['全部','系统','奖励'])
for i,value in enumerate(['欢迎来到牌桌','新手引导奖励','版本说明','好友房使用帮助']):
    y=290+i*105;l.append(card(180,y,1240,93));l.append(image('icon-mail',[210,y+17,70,50]));l.append(text(value,[340,y+23,780,45],28));l.append(button('查看',1155,y+15,220,'UI18',secondary=True))
l.append(button('一键领取',1130,745,280))
l=base('UI18','邮件详情');l.extend([text('欢迎来到牌桌',[210,225,1160,55],36),text('寄件人：系统　　日期：示例日期',[210,300,1160,42],24),text('欢迎与牌友一起体验轻松的麻将对局。\n附件数量由实际服务回执提供；阅读不会自动领取。',[210,385,1160,150],29),card(210,570,1160,115),image('gift-box',[250,580,90,90]),text('新手礼盒 × 1',[385,605,700,45],28),button('返回列表',470,745,280,'UI17',secondary=True),button('领取附件',850,745,280)])
l=base('UI19','战绩记录');tabs(l,['全部对局','好友房','休闲匹配'])
for i in range(4):
    y=290+i*105;l.append(card(180,y,1240,93));l.append(text('四人对局　示例日期',[220,y+24,680,45],27));l.append(text('+240' if i%2==0 else '−80',[930,y+22,170,45],31,'#b52f20' if i%2==0 else '#196448'));l.append(button('详情',1160,y+16,220,'UI20',secondary=True))
l=base('UI20','战绩详情')
for i,(key,val) in enumerate([('对局方式','好友房 · 示例局'),('参与者','金带道童 / 银发医师 / 白眉老道 / 黑发侠女'),('结算数据','各项积分与牌型以真实回执填入'),('回放入口','绑定实际可用的回放记录')]):labelrow(l,key,val,240+i*112)
l.extend([button('返回战绩',480,745,280,'UI19',secondary=True),button('查看牌桌',850,745,280,'UI09')])
l=base('UI21','设置');tabs(l,['声音','显示','帮助'])
for i,value in enumerate(['音乐音量','音效音量','提示音量']):
    y=300+i*130;l.append(text(value,[220,y+5,300,50],30));l.append(skin('slider-track',[650,y,620,46]));l.append(image('slider-thumb',[970,y-7,62,66]));l.append(image('checkbox-on',[1320,y,46,46]))
l.extend([text('调整后立即在本地示例中反馈',[370,700,860,45],25,align='center'),button('完成',650,758,300,'UI03')])
l=base('UI22','规则与帮助');tabs(l,['基础操作','房间说明','状态说明'])
for i,(heading,body) in enumerate([('选择与出牌','点击手牌选中，再按当前客户端操作方式确认出牌。'),('吃、碰、杠、胡','只有当前房间规则允许且存在合法候选时显示可操作项。'),('计分与花牌','地方番型和花牌是否启用，以实际房间规则及服务端配置为准。'),('准备与重连','全部参与者满足开始条件才开局；断线后应先恢复真实牌局。')]):
    y=290+i*110;l.extend([text(heading,[220,y,1080,42],29),text(body,[220,y+47,1140,48],24)])
l.append(button('新手教学',1080,750,280,'UI27'))
l=base('UI23','房间确认与投票')
l.extend([text('是否离开当前房间？',[330,230,940,70],37,align='center'),text('投票参与者、进度和结果由真实房间状态提供。',[300,315,1000,55],26,align='center')])
for i,role in enumerate(roles):
    x=350+i*240;portrait(l,role,x,420,110);l.append(text(['已同意','等待回应','等待回应','等待回应'][i],[x-30,560,170,45],24,align='center'))
l.extend([button('继续留在房间',420,725,320,'UI07',secondary=True),button('确认离开',850,725,320,'UI03')])
l=base('UI24','连接与空状态');empty(l,'connection-interrupted','连接暂时中断，请稍后重试','重新连接','UI09')
l=base('UI25','装扮设置');tabs(l,['桌面','牌背'])
for i,(name,id) in enumerate([('青玉云纹','table-background'),('竹影清风','table-ivory-bamboo'),('月白云海','table-moon-lotus')]):
    x=180+i*430;l.append(card(x,290,400,290));l.append(image(id,[x+20,310,360,203],interactive=True,themeIndex=i));l.append(text(name,[x+20,520,360,42],29,align='center',binding='themes['+str(i)+'].label'))
l.extend([text('主题与牌背使用各自独立纹理；不依赖概念图缩略图',[270,650,1060,50],26,align='center'),button('应用装扮',650,745,300)])
l=base('UI26','角色详情');l.append(image('welcome-daotong',[150,180,500,500],binding='charactersById[selectedCharacterId].fullBody.file'));l.extend([text('金带道童',[760,220,580,65],40,binding='charactersById[selectedCharacterId].displayName'),text('金带、玉袍与太极葫芦',[760,300,580,50],29,binding='charactersById[selectedCharacterId].description'),text('独立表情',[760,385,580,45],28)])
for i,(emotion,name) in enumerate([('happy','开心'),('thinking','思考'),('surprised','惊讶'),('sad','沮丧')]):
    x=720+i*170;l.extend([image('expression-daotong-'+emotion,[x,465,150,150],binding='charactersById[selectedCharacterId].expressions.'+emotion+'.file'),text(name,[x,630,150,40],25,align='center',binding='expressionLabels.'+emotion)])
l.extend([button('已使用',220,720,280,enabled=False),button('返回角色',1000,745,300,'UI14',secondary=True)])
l=base('UI27','新手教学')
l.extend([text('第 1 步　选择一张手牌',[330,200,940,60],36,align='center'),text('选中状态与可出牌状态独立呈现；按房间规则提示合法操作。',[250,295,1100,70],27,align='center')])
for i in range(7):tile(l,i,[480+i*90,430-(20 if i==2 else 0),82,117])
l.extend([image('tutorial-tap-hand',[650,575,100,100]),button('跳过',420,740,270,'UI03',secondary=True),button('下一步',900,740,270,'UI10')])
l=base('UI28','公告详情');l.extend([text('牌桌使用说明',[200,220,1200,65],37),text('公告日期：示例日期',[200,300,1200,45],24),text('欢迎来到麻将大厅。\n\n休闲匹配与好友房分别提供入口，开始前请确认房间规则。\n保持友善交流；所有奖励、积分和状态以真实业务回执为准。\n\n正式内容通过原生文字层替换，不烘焙进背景素材。',[200,390,1200,290],29),button('返回大厅',650,745,300,'UI03',secondary=True)])
l=base('UI29','奖励领取')
for i,(name,id) in enumerate([('完成新手教学','gift-box'),('了解房间规则','item-voucher')]):
    y=300+i*195;l.append(card(200,y,1200,155));l.append(image(id,[240,y+20,110,110]));l.append(text(name,[420,y+30,600,50],32));l.append(text('示例奖励，真实回执后变为已领取',[420,y+90,600,40],23));l.append(button('领取',1110,y+46,240,action='claim'))
l=base('UI30','成就收藏')
for i,(name,progress) in enumerate([('初识牌桌','1 / 1 · 已解锁'),('同桌相逢','3 / 10 · 进行中'),('熟悉规则','0 / 5 · 未解锁')]):
    y=280+i*155;l.append(card(200,y,1200,130));l.append(image('achievement-frame-unlocked' if i==0 else 'achievement-frame-locked',[235,y+15,100,100]));l.append(text(name,[400,y+20,720,50],31));l.append(text(progress,[400,y+78,720,42],24))
l=base('UI31','积分排行')
for i,role in enumerate(roles):
    y=240+i*120;l.append(card(200,y,1200,105));portrait(l,role,300,y+15,68);l.append(text(str(i+1),[220,y+27,60,45],30,align='center'));l.append(text(roleNames[i],[430,y+26,550,48],29));l.append(text(['+960','+640','+320','−80'][i],[1120,y+25,200,50],33,'#b52f20' if i<3 else '#196448','right'))
l=base('UI32','物品收藏');tabs(l,['全部','道具','装扮'])
items=[a for a in old['props'] if '/items/' in a['file']][:8]
for i,a in enumerate(items):
    x=210+(i%4)*200;y=285+(i//4)*205;l.append(image('item-slot-selected' if i==0 else 'item-slot-default',[x,y,170,170]));l.append(node('image',[x+25,y+20,120,120],file=a['file'],record=a['record'],fit='contain'));l.append(text(a.get('title',a.get('label',a['id'])),[x-10,y+172,190,40],21,align='center'))
l.extend([card(1080,285,330,430),text('物品详情',[1120,320,250,55],32,align='center'),text('名称、数量和用途\n绑定实际物品数据。',[1120,405,250,140],25),button('使用',1125,610,240)])

# Every old state now references actual independent runtime files and a composition.
stateBase={
 'room.empty_seat':'UI07','room.full':'UI07','room.owner':'UI07','room.member':'UI07','room.ready':'UI07','room.not_ready':'UI07','room.wait_start':'UI07',
 'room.leave_confirmation':'UI23','room.dissolve_request':'UI23','room.dissolve_vote':'UI23','room.dissolve_progress':'UI23','room.dissolve_result':'UI23','room.join_failure':'UI24',
 'play.wait_discard':'UI09','play.current_player':'UI09','play.countdown':'UI09','play.dealer':'UI09','play.offline':'UI09','play.autoplay':'UI09','play.peng_gang_hu_pass':'UI10','play.multiple_candidates':'UI10','play.ready_hand':'UI10','play.win':'UI11','play.draw':'UI11','play.continue_round':'UI11','play.match_return':'UI12',
 'social.friend_online':'UI15','social.friend_offline':'UI15','social.friend_busy':'UI15','social.invite_sent':'UI08','social.friend_application':'UI15','social.quick_chat':'UI16','social.emoticons':'UI16',
 'mail.unread':'UI17','mail.read':'UI17','mail.attachment':'UI18','mail.claim_pending':'UI18','mail.claimed':'UI18','mail.delete':'UI18','list.no_results':'UI24',
 'system.loading':'UI01','system.error':'UI24','system.disconnected':'UI24','system.reconnecting':'UI24','system.recovery_failed':'UI24','system.matching':'UI04','system.match_timeout':'UI24','system.match_cancel':'UI04','system.match_success':'UI04',
 'control.normal':'UI05','control.pressed':'UI05','control.selected':'UI05','control.disabled':'UI05','control.toggle':'UI21','control.slider':'UI21','control.input':'UI06',
 'cosmetic.unselected':'UI25','cosmetic.preview_selected':'UI25','cosmetic.in_use':'UI25','character.in_use':'UI26','tutorial.select':'UI27','tutorial.actions':'UI27','tutorial.complete':'UI27','reward.not_achieved':'UI29','reward.claimable':'UI29','reward.claimed':'UI29','achievement.locked':'UI30','achievement.unlocked':'UI30','ranking.top_three':'UI31','ranking.self':'UI31','inventory.default':'UI32','inventory.selected':'UI32','inventory.disabled':'UI32','inventory.new':'UI32','announcement.detail':'UI28'}
states=[]
for previous in old['states']:
    state=previous['state'];ui=stateBase[state];layers=copy.deepcopy(layouts[ui]['layers']);binding={'state':state,'uiId':ui,'compositionFile':'production/layouts.json','independentAssetFiles':sorted({a['file'] for a in layers if a.get('file')}),'textDataIsSeparate':True,'serverOrClientStateBindingRequired':True,'sampleOnly':True,'layers':layers}
    if state=='play.offline':layers.extend([image('offline-badge',[1240,220,90,90]),text('离线',[1240,312,90,36],24,'#fff9e9','center')]);binding['independentFrom']=['play.autoplay']
    if state=='play.autoplay':layers.extend([image('autoplay-badge',[1240,220,90,90]),text('托管',[1240,312,90,36],24,'#fff9e9','center')]);binding['independentFrom']=['play.offline']
    if state=='play.current_player':layers.extend([image('current-player-ring',[150,650,150,150]),text('正在出牌',[150,822,180,35],23,'#fff9e9','center')])
    if state=='play.wait_discard':layers.append(text('请选择要打出的手牌',[350,680,780,40],27,'#fff9e9','center'))
    if state=='system.reconnecting':layers.append(image('loading-ring',[745,195,110,110]))
    if state=='system.loading':
        for a in layers:
            if a['type']=='button' and a.get('text')=='进入游戏':a['text']='等待加载';a['enabled']=False;a['binding']='loading.ready'
    if state in ['mail.claimed','reward.claimed','reward.not_achieved']:
        for a in layers:
            if a['type']=='button' and a['text'] in ['领取','领取附件']:a['text']='已领取' if state.endswith('claimed') else '尚未达成';a['enabled']=False
    if state in ['system.error','system.disconnected','system.reconnecting','system.recovery_failed','system.match_timeout','room.join_failure','list.no_results']:
        icon='match-timeout' if state=='system.match_timeout' else 'empty-search' if state in ['list.no_results','room.join_failure'] else 'connection-interrupted'
        for a in layers:
            if a.get('asset')=='connection-interrupted':a.update(file=lookup[icon]['file'],asset=icon,record=lookup[icon]['record'])
    if state=='play.draw':
        for a in layers:
            if a['type']=='text' and a.get('text') in ['+240','−80']:a['text']='0';a['color']='#6f6654'
            if a.get('text')=='单局结算':a['text']='流局结算'
        layers.append(image('draw',[650,600,300,130]))
    if state=='control.disabled':
        for a in layers:
            if a['type']=='button':a['enabled']=False
    if state=='control.pressed':
        for a in layers:
            if a['type']=='button':a['previewState']='pressed'
    if state=='control.selected':
        for a in layers:
            if a['type']=='button':a['previewState']='selected'
    if state=='room.empty_seat':
        layers=[a for a in layers if not(a.get('asset','').startswith('expression-swordswoman') or a.get('text')=='黑发侠女')]
        layers.append(image('icon-add',[1270,340,100,100]));layers.append(text('空缺席位',[1150,465,260,46],28,align='center'))
        for a in layers:
            if a.get('text')=='未准备' and a['rect'][0]>1100:a['text']='等待加入'
            if a['type']=='button' and a.get('text')=='房间已满':a['text']='邀请好友';a['enabled']=True
    if state in ['room.owner','room.member']:layers.append(text('你的身份：'+('房主' if state=='room.owner' else '成员'),[1000,174,360,42],27,align='right'))
    if state=='room.wait_start':
        for a in layers:
            if a.get('text')=='未准备':a['text']='已准备'
            if a['type']=='button' and a.get('text')=='等待全部准备':a['text']='开始游戏';a['enabled']=True
    if state=='room.not_ready':
        for a in layers:
            if a.get('text')=='房主 · 已准备':a['text']='房主 · 未准备'
            if a['type']=='button' and a.get('text')=='取消准备':a['text']='准备'
    if state in ['room.leave_confirmation','room.dissolve_request','room.dissolve_vote','room.dissolve_progress','room.dissolve_result']:
        wording={'room.leave_confirmation':'是否离开当前房间？','room.dissolve_request':'是否发起解散投票？','room.dissolve_vote':'房主发起了解散投票','room.dissolve_progress':'等待所有参与者回应','room.dissolve_result':'解散结果：同意解散'}[state]
        for a in layers:
            if a.get('text')=='是否离开当前房间？':a['text']=wording
            if a['type']=='button' and a.get('text')=='确认离开':a['text']='发起投票' if state=='room.dissolve_request' else '同意解散' if state=='room.dissolve_vote' else '返回大厅' if state=='room.dissolve_result' else '等待投票结果' if state=='room.dissolve_progress' else '确认离开';a['enabled']=state!='room.dissolve_progress'
            if a['type']=='button' and a.get('text')=='继续留在房间':a['text']='拒绝解散' if state=='room.dissolve_vote' else '返回房间' if state=='room.dissolve_progress' else '继续留在房间'
            if state=='room.dissolve_result' and a.get('text')=='等待回应':a['text']='已同意'
        if state=='room.dissolve_result':layers=[a for a in layers if not(a['type']=='button' and a.get('text')=='继续留在房间')]
    if state in ['play.multiple_candidates','play.ready_hand']:
        layers=[a for a in layers if a.get('text') not in ['候选牌组','按当前合法候选显示'] and not (a['rect']==[410,560,350,122])]
        layers.append(card(340,510,610,195));layers.append(text('请选择一组合法候选' if state=='play.multiple_candidates' else '可听牌与剩余张数',[370,525,550,40],26))
        if state=='play.multiple_candidates':
            for group in range(2):
                for t in range(3):tile(layers,group*4+t,[390+group*285+t*54,575,48,69])
            layers.append(text('已选中',[390,651,170,32],21));layers.append(text('候选二',[680,651,170,32],21))
        else:
            for t in range(4):tile(layers,t*3,[390+t*130,575,46,66]);layers.append(text('余 '+str(4-t)+' 张',[380+t*130,650,120,32],20,align='center'))
    if state=='play.win':layers.append(image('hu',[650,590,300,150]))
    if state=='social.friend_application':
        for a in layers:
            if a['type']=='button' and a.get('text') in ['邀请','查看']:a['text']='同意申请'
        layers.append(text('新的好友申请',[930,185,420,42],27))
    if state=='social.invite_sent':
        for a in layers:
            if a['type']=='button' and a.get('text')=='邀请':a['text']='已邀请';a['enabled']=False
    if state=='social.emoticons':
        layers=[a for a in layers if not (a['type']=='text' and a.get('text') in ['大家好，准备开始吧','稍等一下，谢谢','打得漂亮','承让，下局再会','请保持轻松心情','很高兴同桌']) and not(a.get('asset')=='content-card' and a['rect'][1]>=300 and a['rect'][1]<=570)]
        emotes=[a for a in old['props'] if '/emotes/' in a['file']]
        for i,a in enumerate(emotes):layers.append(node('image',[275+(i%6)*180,310+(i//6)*195,135,135],file=a['file'],record=a['record'],fit='contain'))
    if state=='mail.unread':
        for i in range(4):layers.append(image('unread-badge',[300,305+i*105,30,30]))
    if state=='mail.delete':
        for a in layers:
            if a['type']=='button' and a.get('text')=='领取附件':a['text']='删除邮件';a['enabled']=True
    if state in ['system.error','system.disconnected','system.reconnecting','system.recovery_failed','system.match_timeout','room.join_failure','list.no_results']:
        wording={'system.error':'操作未完成，请稍后重试','system.disconnected':'连接暂时中断','system.reconnecting':'正在尝试恢复连接','system.recovery_failed':'恢复失败，可重新连接或返回大厅','system.match_timeout':'匹配超时，请重试','room.join_failure':'加入房间失败，请检查房间号','list.no_results':'没有找到相关内容'}[state]
        for a in layers:
            if a.get('text')=='连接暂时中断，请稍后重试':a['text']=wording
            if a['type']=='button' and a.get('text')=='重新连接':a['text']='正在恢复…' if state=='system.reconnecting' else '返回大厅' if state in ['list.no_results','room.join_failure'] else '重试';a['enabled']=state!='system.reconnecting'
    if state=='system.match_success':
        for a in layers:
            if a.get('asset')=='loading-ring':a.update(asset='icon-confirm',file=lookup['icon-confirm']['file'],record=lookup['icon-confirm']['record'])
            if a.get('text')=='正在寻找同桌牌友':a['text']='已找到同桌牌友'
            if a['type']=='button' and a.get('text')=='进入牌桌':a['enabled']=True
    if state=='system.match_cancel':
        for a in layers:
            if a.get('text')=='正在寻找同桌牌友':a['text']='匹配已取消'
            if a['type']=='button' and a.get('text')=='进入牌桌':a['text']='重新匹配';a['enabled']=True;a['target']='UI04'
            if a['type']=='button' and a.get('text')=='取消匹配':a['text']='返回大厅'
    if state in ['cosmetic.unselected','cosmetic.preview_selected','cosmetic.in_use']:
        if state!='cosmetic.unselected':layers.append(image('icon-confirm',[505,320,60,60]))
        layers.append(text({'cosmetic.unselected':'尚未选择','cosmetic.preview_selected':'已选中，待应用','cosmetic.in_use':'当前使用'}[state],[200,595,360,42],25,align='center'))
        for a in layers:
            if a['type']=='button' and a.get('text')=='应用装扮' and state=='cosmetic.in_use':a['text']='已使用';a['enabled']=False
    if state in ['tutorial.actions','tutorial.complete']:
        layers=[a for a in layers if a.get('asset')!='tutorial-tap-hand' and not (a.get('asset') in [Path(f).stem for f in tileFiles] and 400<=a['rect'][1]<=450)]
        for a in layers:
            if a.get('text')=='第 1 步　选择一张手牌':a['text']='第 2 步　选择合法操作' if state=='tutorial.actions' else '第 3 步　学习完成'
            if a['type']=='button' and a.get('text')=='下一步' and state=='tutorial.complete':a['text']='返回大厅';a['target']='UI03'
            if a['type']=='button' and a.get('text')=='跳过' and state=='tutorial.complete':a['text']='重新学习';a['target']='UI27'
        if state=='tutorial.actions':
            for i,(v,on) in enumerate([('碰',True),('杠',False),('胡',False),('过',True)]):layers.append(button(v,450+i*185,480,160,None,on))
        else:layers.append(image('icon-confirm',[690,425,220,220]))
    if state in ['achievement.locked','achievement.unlocked']:
        changed=False
        for a in layers:
            if a.get('asset','').startswith('achievement-frame-') and not changed:
                id='achievement-frame-unlocked' if state.endswith('unlocked') else 'achievement-frame-locked';a.update(asset=id,file=lookup[id]['file'],record=lookup[id]['record']);changed=True
            if a.get('text')=='1 / 1 · 已解锁' and state=='achievement.locked':a['text']='0 / 1 · 未解锁'
    if state=='ranking.top_three':
        for i,id in enumerate(['rank-marker-gold','rank-marker-silver','rank-marker-bronze']):layers.append(image(id,[220,255+i*120,65,65]))
    if state=='ranking.self':layers.append(text('我的位置：第 4 名',[800,745,550,46],30))
    if state.startswith('inventory.'):
        id={'inventory.default':'item-slot-default','inventory.selected':'item-slot-selected','inventory.disabled':'item-slot-disabled','inventory.new':'item-slot-new'}[state]
        for a in layers:
            if a.get('asset')=='item-slot-selected':a.update(asset=id,file=lookup[id]['file'],record=lookup[id]['record'])
            if a['type']=='button' and a.get('text')=='使用' and state=='inventory.disabled':a['enabled']=False
    binding['layers']=layers;binding['independentAssetFiles']=sorted({a['file'] for a in layers if a.get('file')});states.append(binding)
extraFixtures=[('play.loss','UI11'),('play.self_draw','UI11'),('play.chi_prompt','UI10'),('play.gang_prompt','UI10'),('play.ting_prompt','UI10'),('match.loss','UI12'),('mail.empty','UI17'),('social.no_friends','UI15'),('records.empty','UI19'),('room.join_invalid_code','UI06'),('room.join_full','UI24')]
for state,ui in extraFixtures:
    layers=copy.deepcopy(layouts[ui]['layers'])
    if state in ['play.loss','match.loss']:
        scoreNodes=[a for a in layers if a['type']=='text' and a.get('text') in ['+240','−80']]
        for i,a in enumerate(scoreNodes):a['text']='+240' if i==1 else '−80';a['color']='#b52f20' if i==1 else '#196448'
        for a in layers:
            if a.get('text') in ['单局结算','整场结算']:
                a['text']='本局未获胜' if state=='play.loss' else '本场未获胜'
                a['binding']='result.title'
        layers.append(text('本地玩家：金带道童',[570,220,460,42],25,align='center',binding='result.localPlayerName'))
        layers.append(image('settlement-defeat',[650,590,300,140]))
    if state in ['play.self_draw','play.chi_prompt','play.gang_prompt','play.ting_prompt']:
        id={'play.self_draw':'self-draw','play.chi_prompt':'chi','play.gang_prompt':'gang','play.ting_prompt':'ting'}[state]
        layers.append(image(id,[650,600,300,130] if state=='play.self_draw' else [640,280,320,160]))
    if state in ['mail.empty','social.no_friends','records.empty']:
        layers=layers[:6]
        id,label={'mail.empty':('empty-mail','暂无邮件'),'social.no_friends':('empty-friends','还没有好友'),'records.empty':('empty-records','暂无战绩')}[state]
        empty(layers,id,label)
    if state=='room.join_invalid_code':
        layers.append(text('房间号无效，请重新输入',[440,330,720,40],25,'#b52f20',align='center'))
    if state=='room.join_full':
        for a in layers:
            if a.get('text')=='连接暂时中断，请稍后重试':a['text']='房间已满，请加入其他房间'
            if a['type']=='button' and a.get('text')=='重新连接':a['text']='返回加入';a['target']='UI06'
            if a.get('asset')=='connection-interrupted':a.update(asset='empty-search',file=lookup['empty-search']['file'],record=lookup['empty-search']['record'])
    states.append({'state':state,'uiId':ui,'compositionFile':'production/layouts.json','independentAssetFiles':sorted({a['file'] for a in layers if a.get('file')}),'textDataIsSeparate':True,'serverOrClientStateBindingRequired':True,'sampleOnly':True,'additionalV3RequiredState':True,'layers':layers})
    if state in ['play.loss','match.loss']:states[-1].update(sampleLocalOutcome='loss',sampleLocalPlayerIndex=0,outcomeMustNotBeInferredFromScore=True)
for page in layouts.values():
    # Use the dedicated production form skins while retaining native text separately.
    if page['id']=='UI01' and 'progress-track' in lookup:
        layers=page['layers'];layers[:]=[a for a in layers if a.get('asset') not in ['slider-track','loading-ring']]
        for a in layers:
            if a.get('text')=='正在整理牌桌，请稍候':a.update(text='牌桌已就绪',binding='loading.statusText')
        layers.extend([skin('progress-track',[440,715,720,64]),image('progress-fill',[464,733,672,29],sourceRect=[12,14,555,97],fitMode='stretch_x',clipFraction=1),text('100%',[660,726,280,40],24,'#fff9e9','center',binding='loading.progress')])
    if page['id']=='UI21' and 'toggle-track-on' in lookup:
        layers=page['layers'];layers[:]=[a for a in layers if a.get('asset')!='checkbox-on']
        for i in range(3):
            y=300+i*130
            fill=image('slider-fill',[736,y+16,450,15],sourceRect=[12,14,520,78],fitMode='stretch_x',clipFraction=.55)
            index=next(j for j,a in enumerate(layers) if a.get('asset')=='slider-thumb' and a['rect'][1]==y-7);layers.insert(index,fill)
            layers.extend([image('toggle-track-on',[1310,y,120,46]),image('toggle-thumb',[1394,y+9,28,28],sourceRect=[14,15,194,193])])
    if page['id'] in ['UI17','UI19','UI15'] and 'list-row-selected' in lookup:
        for a in page['layers']:
            if a.get('asset')=='content-card' and a['rect'][1] in [290,410] and a['rect'][2]==1240:
                a.update(file=lookup['list-row-selected']['file'],record=lookup['list-row-selected']['record'],asset='list-row-selected',nineSlice=lookup['list-row-selected']['nineSlice'],stretchAxes=['x']);break
    page['independentAssetFiles']=sorted({a['file'] for a in page['layers'] if a.get('file')})
    page['conceptReferenceFiles']=[a['file'] for a in old['pages'] if a['id']==page['id']]
    page['implementationStatus']='composition_reference_not_game_client'
    page['textAndDataBindingsAreNative']=True
    if page['id']=='UI26':page['templateDataContract']='assets/presentation/production-v3/character-bindings.json';page['sampleSelectedCharacterId']='daotong';page['runtimeSelector']='selectedCharacterId'
    for a in page['layers']:
        if a['type']=='button' and a.get('stateAssets'):assert all((R/f).is_file() for f in a['stateAssets'].values())
for state in states:
    if state['state'] in ['control.input','room.join_invalid_code'] and 'input-focus-overlay' in lookup:
        id='input-error-overlay' if state['state']=='room.join_invalid_code' else 'input-focus-overlay';state['layers'].append(skin(id,[440,250,720,70]))
    if state['state'] in ['play.multiple_candidates','play.ready_hand'] and 'candidate-panel' in lookup:
        # The dedicated containers keep their full aspect; old flexible fallback is not stretched into them.
        panelId='candidate-panel' if state['state']=='play.multiple_candidates' else 'ready-hand-panel'
        state['compositionContract']='assets/ui/production-v3/gameplay/runtime-compositions.json'
        state['dedicatedContainerAsset']=lookup[panelId]['file']
    state['independentAssetFiles']=sorted({a['file'] for a in state['layers'] if a.get('file')})
write('production/layouts.json',{'schemaVersion':3,'canvas':[1600,900],'status':'pending_composition_visual_qa','pages':list(layouts.values()),'pageCount':32,'policy':'Independent native assets and configurable text/data layers; no full-screen concepts used as runtime images','fontFileRedistributed':False})
write('production/states.json',{'schemaVersion':3,'status':'pending_composition_visual_qa','stateCount':len(states),'states':states})
print(json.dumps({'pages':len(layouts),'states':len(states),'nodes':sum(len(x['layers']) for x in layouts.values()),'independentFiles':len({f for x in layouts.values() for f in x['independentAssetFiles']}),'status':'pending_composition_visual_qa'}))
