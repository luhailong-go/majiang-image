from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
from PIL import Image
R=Path(r'D:\work\majiang-image')
def read(s): return json.loads((R/s).read_text(encoding='utf-8'))
def sha(s): return hashlib.sha256((R/s).read_bytes()).hexdigest()
def write(s,d): (R/s).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
iq=read('work/full-game-ui/independent-qa.json');assert iq['status']=='passed',iq['status']
m=read('designs/ui/full-game/manifest.json');errors=[]
for d in m['pages']+m['components']:
 assert sha(d['file'])==d['sha256'],d['file']
 with Image.open(R/d['file']) as im: assert [im.width,im.height]==[d['width'],d['height']],d['file']
for d in m['sourceManifests']: assert sha(d['file'])==d['sha256'],d['file']
assert len(m['pages'])==11 and len(m['components'])==22
m['status']='passed';write('designs/ui/full-game/manifest.json',m)
q={'schemaVersion':1,'scope':'full_game_ui_v2','status':'passed','verifiedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'uiIds':m['uiIds'],'pageCount':11,'componentCount':22,'primaryAssetCount':33,'manifest':'designs/ui/full-game/manifest.json','manifestSha256':sha('designs/ui/full-game/manifest.json'),'independentQA':'work/full-game-ui/independent-qa.json','independentQASha256':sha('work/full-game-ui/independent-qa.json'),'componentQA':'assets/ui/full-game/components/qa.json','componentQASha256':sha('assets/ui/full-game/components/qa.json'),'nativeDimensionsNote':m['nativeDimensionsNote'],'errors':[],'unpassedItems':[],'browserTested':False,'clientIntegrated':False,'actualModel':None,'actualQuality':None}
write('designs/ui/full-game/qa.json',q)
print(json.dumps({'status':'passed','manifestSha256':q['manifestSha256'],'qaSha256':sha('designs/ui/full-game/qa.json'),'independentQASha256':q['independentQASha256'],'ui25Sha256':sha('designs/ui/full-game/core/ui25-customization.png'),'pages':11,'components':22,'unpassedItems':[]},ensure_ascii=False))
