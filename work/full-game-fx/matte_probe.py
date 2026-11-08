from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
R=Path(r'D:\work\majiang-image');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
S=Image.new('RGB',(1200,960),'#fff9e9');d=ImageDraw.Draw(S)
stats=[]
for row,slug in enumerate(['draw-focus','player-ring','reward-stars']):
 im=Image.open(R/f'designs/fx/full-game/{slug}-v1.png').convert('RGBA').crop((627,0,1254,627));a=np.asarray(im.getchannel('A'))
 stats.append({'slug':slug,'alphaCounts':{str(x):int(np.sum(a==x)) for x in [0,1,16,64,128,190,220,240,250,253,254,255]}})
 for col,cut in enumerate([0,64,128,200]):
  v=im.copy();b=np.asarray(v).copy();b[b[:,:,3]<cut,3]=0
  v=Image.fromarray(b).resize((280,280),Image.Resampling.LANCZOS)
  bg=Image.new('RGBA',(280,280),'#123f35' if row%2 else '#fff9e9');bg.alpha_composite(v);S.paste(bg.convert('RGB'),(col*300,row*320+35));d.text((col*300+8,row*320+8),f'{slug} alpha<{cut} removed',font=font,fill='#163d32')
S.save(R/'work/full-game-fx/matte-probe.png');print(json.dumps(stats))
