from pathlib import Path
import json,hashlib
root=Path(r"D:\work\majiang-image")
domain=root/"designs/ui/full-suite/system"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
states={
"UI13":["profile.default","profile.edit-entry","profile.statistics","profile.recent-game","navigation.back-lobby","navigation.close"],
"UI15":["friends.tab.selected","requests.tab.unselected.badge","friends.search","friends.add-entry","friends.online","friends.offline","friends.busy","friends.invite.enabled","friends.invite.disabled","requests.pending.accept","requests.pending.reject","friends.empty-navigation","navigation.back-lobby","navigation.close"],
"UI17":["mail.category.selected","mail.category.unselected","mail.row.selected","mail.unread","mail.read","mail.with-attachment","mail.pending-claim","mail.claimed","mail.clean-read","mail.refresh","mail.open-detail","navigation.back-lobby","navigation.close"],
"UI18":["mail.detail","mail.attachment.pending-claim","mail.claim.enabled","mail.delete.disabled-unclaimed","mail.claimed.alternate-style","navigation.back-list","navigation.close"],
"UI19":["records.category.selected","records.category.unselected","records.win","records.loss","records.draw","records.detail-entry","records.empty-navigation","navigation.back-lobby","navigation.close"],
"UI20":["records.four-player-summary","records.per-round-table","records.replay-entry-only","navigation.back-records","navigation.close"],
"UI21":["settings.music-slider","settings.sfx-slider","settings.voice.on","settings.confirm-play.off","settings.quality.selected","settings.quality.unselected","settings.tile-preview","settings.tablecloth.selected","settings.tablecloth.unselected","settings.restore-default","settings.save","settings.logout-entry","navigation.close"],
"UI22":["help.directory.selected","help.directory.unselected","help.select-play-instruction","help.action-choice-instruction","help.ready-room-instruction","help.tile-suits","help.rules-configurable","navigation.back","navigation.close"]
}
items=[]
for p in sorted(domain.glob("*.png.generation.json")):
 rec=json.loads(p.read_text(encoding="utf-8"))
 assert sha(root/rec["file"])==rec["sha256"]
 assert sha(root/rec["prompt"])==rec["promptSha256"]
 assert rec["inspection"]["visualStatus"]=="passed"
 for ref in rec["references"]:assert sha(root/ref["file"])==ref["sha256"]
 items.append({"id":rec["scopeId"],"title":rec["title"],"file":rec["file"],"generationRecord":str(p.relative_to(root)).replace("\\","/"),"prompt":rec["prompt"],"width":rec["width"],"height":rec["height"],"format":rec["format"],"sha256":rec["sha256"],"status":"artwork_qa_passed","states":states[rec["scopeId"]],"inspection":rec["inspection"]})
assert [i["id"] for i in items]==["UI13","UI15","UI17","UI18","UI19","UI20","UI21","UI22"]
manifest={"schemaVersion":1,"domain":"system_social_records","scope":"docs/FULL_UI_SCOPE.md","count":len(items),"completedIds":[i["id"] for i in items],"pages":items,"stateCoverage":[{"state":state,"sourceId":item["id"],"file":item["file"]} for item in items for state in item["states"]],"externalStateDependencies":[{"scopeId":"UI23","purpose":"按钮按下/禁用/选中、通用确认、成功提示等共享控件状态","owner":"rooms"},{"scopeId":"UI24","purpose":"无好友/无邮件/无战绩/无搜索结果及网络错误状态","owner":"rooms"}],"integrationNotes":["所有图片为独立原生整屏艺术图，不是已接入客户端。正式界面须将动态文字和控件拆开实现。","UI18右下已领取是替换样式，实际邮件状态pending_claim显示领取并禁用删除；claimed隐藏领取入口、显示已领取并启用删除。不得在运行界面同时显示可领取与已领取。","列表与面板的示例数据用于布局，不代表用户账号、真实好友、奖励或计分合同。","UI20四家结果+24/-8/-4/-12，分局列累计一致，每行总和0。回放按钮仅入口示意。","UI22只说明通用交互，地方玩法与番型/计分仍待配置。","设置页所有开关/滑条/单选是美术示意，具体数值保存与音频/显示行为由客户端接入实现。"],"validation":{"allImageHashesMatch":True,"allPromptHashesMatch":True,"allReferenceHashesMatch":True,"allVisualReviewsPassed":True,"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露可核实版本/质量"},"delivery":{"localOnly":True,"uploaded":False,"clientIntegrated":False}}
(domain/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"count":len(items),"ids":manifest["completedIds"],"stateMappings":len(manifest["stateCoverage"]),"verified":"images prompts refs visual QA","manifest":str(domain/"manifest.json")},ensure_ascii=False))
