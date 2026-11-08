from pathlib import Path
import hashlib,json,re
root=Path(r"D:\work\majiang-image")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=[]
for record_path in sorted((root/"designs").rglob("*.generation.json")):
    record=json.loads(record_path.read_text(encoding="utf-8"))
    assert sha(root/record["file"])==record["sha256"]
    assert sha(root/record["prompt"])==record["promptSha256"]
    for ref in record["references"]:
        assert sha(root/ref["file"])==ref["sha256"]
    assert record["actualModel"] is None and record["actualQuality"] is None
    assert record["inspection"]["independentVisualReviewCompleted"]
    assert record["inspection"]["nativeCopyHashMatches"]
    out.append({"record":str(record_path),"status":"hashes_references_prompt_and_checks_verified"})
for link in re.findall(r"\]\(([^)]+)\)",(root/"README.md").read_text(encoding="utf-8")):
    assert (root/link.split("#")[0]).exists(),link
assert len(out)==2
print(json.dumps({"records":out,"readmeLinks":"all_exist","count":len(out)},ensure_ascii=False))

