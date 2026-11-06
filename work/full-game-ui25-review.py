from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, copy

R = Path(__file__).resolve().parents[1]
p = R / 'work/full-game-props/ui-pages-independent-qa.json'
d = json.loads(p.read_text(encoding='utf-8-sig'))
now = datetime.now(timezone.utc).isoformat()
f = 'designs/ui/full-game/core/ui25-customization.png'
expected = '2982c6d00a735205f5ac2c597215b485dccd906266ce75c1a79daadd723b02d3'
for a in d['files']:
    digest = hashlib.sha256((R/a['file']).read_bytes()).hexdigest()
    if a['file'] != f:
        assert digest == a['after']['sha256'], a['file']
        continue
    assert digest == expected
    if a.get('status') != 'passed':
        a['previousRevisionReview'] = copy.deepcopy({k: a[k] for k in ['before', 'after', 'status', 'findings']})
    for finding in a.get('findings', []):
        item = dict(finding)
        item.update(file=f, status='resolved', resolvedBy='root coordinator, independent of supplemental page producer', resolvedAt=now, fixedImageSha256=digest)
        d.setdefault('resolvedFindings', []).append(item)
    snapshot = {'sha256': digest, 'length': (R/f).stat().st_size, 'observedAt': now}
    a.update(before=snapshot, after=dict(snapshot), hashStable=True, status='passed', findings=[])
    a['inspectionMethod'] = 'Root coordinator actually opened the complete corrected native PNG via view_image(detail=original); production image was not modified by reviewer'
    a['checks'].append('Corrected current-use tile-back label 太极青玉 agrees with the selected back; tablecloth remains 青玉云纹')
    a['recheck'] = {'reviewer': 'root coordinator', 'reviewedAt': now, 'method': 'actual full-image visual review plus current SHA-256; other ten unchanged-image reviews reused', 'status': 'passed', 'sha256': digest, 'modelCalls': 0, 'productionFilesModified': False}
d['originalReviewedAt'] = d.get('originalReviewedAt', d['reviewedAt'])
d.update(reviewer='mahjong_tiles_pack: initial 11-image review; root coordinator: corrected UI25-only independent recheck', reviewedAt=now, status='passed', passedCount=11, hashStableCount=11, openFindings=[])
p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
md = R/'work/full-game-props/ui-pages-independent-qa.md'
s = md.read_text(encoding='utf-8-sig')
s = s.replace('10张通过；UI25有1处需定点修正文案。整体状态为 `needs_ui25_label_fix`，不把该问题隐去后宣称11张全部通过。', '11张通过，整体状态为 `passed`。原10张通过图哈希不变，复用原独立检查；根协调者独立于页面生产者，以原尺寸实际打开修正后的UI25并核对新哈希，当前牌背标签已为“太极青玉”。原缺陷和旧图哈希保留在JSON的previousRevisionReview/resolvedFindings中。')
s = s.replace('| UI25 装扮设置 | 需修正文案 | 当前牌背缩略图上方写“青玉云纹”，右侧同款选中牌背名为“太极青玉”。青玉云纹是桌布名，应将当前牌背标签改为太极青玉。 |', '| UI25 装扮设置 | 修正后通过 | 根协调者实际复看新版完整图：当前牌背名“太极青玉”与右侧选中牌背相同；桌布仍为“青玉云纹”，其他布局和操作保持。 |')
s += '\nUI25修正复核者：root coordinator；方法：view_image(detail=original)，仅改检查记录，未改PNG。新图SHA-256：`'+expected+'`。复核时间：'+now+'。\n'
md.write_text(s, encoding='utf-8')
print(json.dumps({'status': d['status'], 'passedCount': d['passedCount'], 'changedImageRechecked': f, 'sha256': expected}))
