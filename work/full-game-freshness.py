from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
def assert_fresh(data,validation):
    assert validation['status']=='passed' and not validation['errors']
    checks=[{k:a[k] for k in ['file','sha256','width','height','mode']} for a in data['assets']]
    snapshot=hashlib.sha256(json.dumps(checks,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert snapshot==validation['primaryAssetSnapshotSha256'],'Asset list changed after validation; rebuild then revalidate.'
    assert data.get('sourceManifestHashes',{})==validation['sourceManifestHashes'],'Source manifest set changed after validation.'
    expected={a['file']:a['sha256'] for a in checks}
    expected.update(validation.get('recordHashes',{}))
    expected.update(validation['sourceManifestHashes'])
    for file,digest in expected.items():
        p=R/file
        assert p.is_file(),file
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,'Changed after validation: '+file
