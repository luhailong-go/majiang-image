from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

R = Path(__file__).resolve().parents[1]
relative = 'work/full-game-ui/core/ui27-select-cleanup-failed.png.generation.json'
p = R/relative
d = json.loads(p.read_text(encoding='utf-8-sig'))
previousHash = hashlib.sha256(p.read_bytes()).hexdigest()
replacement = 'designs/ui/full-game/core/ui27-tutorial-select.png'
assert d['pixelsRetainedInProject'] is False and not (R/d['file']).exists()
assert d['sha256'] == '62f9700a714301c3be331f906962db5ac9844b42770ba366b72954801d61f136'
replacementHash = hashlib.sha256((R/replacement).read_bytes()).hexdigest()
assert replacementHash == 'b828e01215e33979e55a3f082c012109224ffd85294587a92f1b2076ab7e23a6'
now = datetime.now(timezone.utc).isoformat()
d['cleanup'].update(sha256BeforeRemoval=d['sha256'], replacement=replacement, replacementSha256=replacementHash)
d['cleanup']['metadataClarification'] = {
    'clarifiedAt': now,
    'previousRecordSha256': previousHash,
    'evidence': 'Existing removedAt, pixelsRetainedInProject=false, recorded native result SHA and producer visual note explicitly say the failed cleanup was superseded by the footer remake. The retained UI27 footer remake is identified here; no pixels were restored or rehashed after deletion.',
    'sha256Evidence': 'Copied from the native-result hash already recorded before deletion; not a new read of deleted image pixels',
    'scope': 'Complete explicit historical cleanup linkage; original generation time, failure findings and actual model/quality remain unchanged'
}
p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
newHash = hashlib.sha256(p.read_bytes()).hexdigest()
qaPath = R/'work/full-game-ui/independent-qa.json'
qa = json.loads(qaPath.read_text(encoding='utf-8-sig'))
qa['historicalCleanupMetadataClarification'] = {'record': relative, 'recordSha256BeforeClarification': previousHash, 'recordSha256AfterClarification': newHash, 'clarifiedAt': now, 'oldReviewRecordSha256IsHistorical': True, 'productionImageChanged': False, 'replacement': replacement}
qaPath.write_text(json.dumps(qa, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'record': relative, 'status': 'explicit_historical_cleanup_link_completed', 'sha256': newHash, 'replacement': replacement}))
