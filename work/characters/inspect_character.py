from PIL import Image
from pathlib import Path
from collections import Counter
import json, hashlib

root=Path(r'D:\work\majiang-image')
src=root/'designs/characters/production/welcome-daotong-production-v2.png'
im=Image.open(src)
im.load()
a=im.getchannel('A')
hist=Counter(a.getdata())
stats={'file':str(src.relative_to(root)), 'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'width':im.width,'height':im.height,'mode':im.mode,'alphaRange':a.getextrema(),'alphaZero':hist[0],'alpha255':hist[255],'alphaLow1to8':sum(hist[x] for x in range(1,9)),'bboxAbove128':a.point(lambda p:255 if p>128 else 0).getbbox(),'bboxNonzero':a.getbbox(),'commonAlpha':hist.most_common(10)}
(root/'work/characters/production-v2-statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
for name,color in [('light',(246,238,218,255)),('dark',(14,44,39,255)),('black',(0,0,0,255))]:
    bg=Image.new('RGBA',im.size,color)
    bg.alpha_composite(im)
    bg.convert('RGB').save(root/f'work/characters/production-v2-{name}.png')
print(json.dumps(stats,ensure_ascii=False))
