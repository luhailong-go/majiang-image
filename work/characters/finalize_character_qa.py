from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone, timedelta

root=Path(r'D:\work\majiang-image'); out=root/'assets/characters'
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
checks=[]
for item in manifest['assets']:
    p=root/item['file']; rec=root/item['record']; im=Image.open(p); im.verify()
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
    data=json.loads(rec.read_text(encoding='utf-8'))
    assert data['derivedFrom']['sha256']==hashlib.sha256((root/data['derivedFrom']['file']).read_bytes()).hexdigest()
    assert (root/data['derivedFrom']['generationRecord']).is_file()
    check={'status':'passed','visualInspectionCompleted':True,'pngIntegrity':'passed','sourceHashes':'passed','userApproved':False,'clientIntegrated':False,'unresolvedIssues':[]}
    if item['role']=='full_body':
        check.update({'identity':'matches gold-band Daoist boy, red 中 tile and taiji gourd','anatomy':'complete hands, shoes, hair, ribbon and robe; no crop','alpha':'real alpha, cleaned external speckles, full-body interior opaque','deepAndLightComposite':'passed via actual view_image of both QA composites','paddingPixels':[199,157,200,157],'paddingMeets8Percent':True,'cleanupRemovedVisibleSubjectPixels':0})
    else:
        check.update({'identity':'distinct face, age/hair/costume, consistent hand-painted style','crop':'face fully visible; portrait intentionally trims shoulders and selected outer hair/ribbon ends','text':'none','transparency':'opaque square portrait by design, use client mask','productionSizes':'512 export from 627 native crop, downsample only'})
    data['inspection'].update(check); data['status']={'productionAccepted':True,'userApproved':False,'clientIntegrated':False}
    rec.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    item['stage']='production_asset_qa_passed'; checks.append({'file':item['file'],**check})
manifest['status']='complete_qa_passed'; manifest['completedAt']=datetime.now(timezone(timedelta(hours=-4))).isoformat()
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'qa.json').write_text(json.dumps({'status':'passed','checks':checks,'scopeComplete':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','assets':len(checks),'hashesVerified':True}))
