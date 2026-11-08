from pathlib import Path
import json,shutil,hashlib
R=Path(r'D:\work\majiang-image')
src=R/'designs/ui/full-game/core/ui25-customization.png'
dst=R/'designs/ui/full-game/core/ui25-customization-source.png'
assert not dst.exists()
shutil.copyfile(src,dst)
r=json.loads(src.with_name(src.name+'.generation.json').read_text(encoding='utf-8'))
r['file']=str(dst.relative_to(R)).replace('\\','/')
r['status']['productionAccepted']=False;r['status']['stage']='retained_edit_source'
r['inspection']['visualStatus']='needs_correction'
r['inspection']['issues']=['当前使用区牌背标签误用桌布名青玉云纹，应与选中牌背统一为太极青玉。']
r['inspection']['blockingIssues']=r['inspection']['issues']
r['retainedReason']='最终版AI编辑对象，保留像素和原生成证据。'
dst.with_name(dst.name+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(hashlib.sha256(dst.read_bytes()).hexdigest())
