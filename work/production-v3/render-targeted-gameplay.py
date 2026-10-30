from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
hold=R/'.work/production-v3/resource-hold.json'
if hold.is_file() and json.loads(hold.read_text(encoding='utf-8-sig')).get('status')=='holding_local_heavy_work':raise SystemExit('Targeted image export deferred until the shared heavy-work slot is returned or human grants this bounded art job.')
script=R/'work/production-v3/gameplay/render-previews.py'
raw=script.read_text(encoding='utf-8-sig');marker='# 2: rotations and four meld types, without perspective warps.'
assert raw.count(marker)==1
other=[R/'designs/ui/production-v3/gameplay'/name for name in ['melds-and-directions.png','candidates-and-states.png','settlement-composition.png','skins-alpha-light-dark.png']]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in other}
exec(compile(raw.split(marker)[0],str(script),'exec'),{'__file__':str(script),'__name__':'targeted_gameplay_table_export'})
assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in other},'Unchanged passed previews must be reused'
p=R/'designs/ui/production-v3/gameplay/table-four-seats.png'
print(json.dumps({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'otherFourPassedPreviewsUnchanged':True,'visualStatus':'pending_actual_image_review'}))
