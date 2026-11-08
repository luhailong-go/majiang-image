from pathlib import Path
from PIL import Image
from datetime import datetime, timezone, timedelta
import hashlib, json

root = Path(r"D:\work\majiang-image")
args = json.loads((root / "work/record-input.json").read_text(encoding="utf-8-sig"))
config = json.loads((root / "config/image-generation.json").read_text(encoding="utf-8-sig"))
manifest = json.loads((root / "references/manifest.json").read_text(encoding="utf-8-sig"))
ref_sources = {r["file"]: r for r in manifest["references"]}
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def local_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat(timespec="milliseconds")
for item in args["records"]:
    path = root / item["file"]
    with Image.open(path) as check:
        check.verify()
    with Image.open(path) as im:
        im.load()
        width, height = im.size
        alpha_stats = None
        if "A" in im.getbands():
            alpha = im.getchannel("A")
            hist = alpha.histogram()
            alpha_stats = {
                "range": list(alpha.getextrema()),
                "fullyTransparentPixels": hist[0],
                "semiTransparentPixels": sum(hist[1:255]),
                "fullyOpaquePixels": hist[255],
                "nearOpaquePixels250To255": sum(hist[250:]),
                "foregroundPixelsAbove128": sum(hist[129:]),
                "foregroundBBoxAlphaAbove128": list(alpha.point(lambda x: 255 if x > 128 else 0).getbbox()),
                "nonzeroAlphaBBox": list(alpha.getbbox()),
                "cornerAlpha": [alpha.getpixel(q) for q in [(0,0),(width-1,0),(0,height-1),(width-1,height-1)]],
                "mostCommonAlpha": sorted([{"alpha":i,"pixels":n} for i,n in enumerate(hist)],key=lambda x:x["pixels"],reverse=True)[:12],
                "note": "存在真实透明区域；主体 Alpha 以252–253为主，不能把全部半透明像素当作边缘。边缘少量低Alpha杂点另列视觉待修。"
            }
        image_meta = {"width":width,"height":height,"format":im.format,"mode":im.mode}
    refs = []
    for index, ref in enumerate(item["refs"], 1):
        info = ref_sources.get(ref)
        refs.append({
            "inputIndex": index,
            "file": ref,
            "submittedPath": str(root/ref),
            "sha256": digest(root/ref),
            "source": info["source"] if info else "本批新生成道童；同项目原生 PNG",
            "purpose": info["role"] if info else "大厅角色外观与身份一致性参考",
            "generationRecord": None if info else ref+".generation.json",
            "actuallyAttached": True
        })
    record = {
        "schemaVersion": 1,
        "file": item["file"],
        "sha256": digest(path),
        "generatedAt": local_time(item["finished"]),
        "generationTimestampBasis": "记录工具完成的客户端观察时间，非提供方披露的服务器生成时间",
        "clientTimezone": "America/New_York",
        "startedAt": local_time(item["started"]),
        **image_meta,
        "nativeDimensions": {"width":width,"height":height},
        "requestedDimensionsInPrompt": {"width":item["requested"][0],"height":item["requested"][1]},
        "resampled": False,
        "tool": "image_gen.imagegen",
        "route": "builtin",
        "generationCallId": None,
        "resultId": None,
        "outputArtifactFileId": item["id"],
        "resultReceipt": item["receipt"],
        "configSnapshot": config,
        "submittedParameters": {
            "model": None,
            "quality": None,
            "transparent_background": item["transparent"],
            "referenced_image_paths": [r["submittedPath"] for r in refs],
            "promptFile": item["prompt"],
            "size": None
        },
        "actualModel": None,
        "actualQuality": None,
        "evidence": "工具仅返回 image_url 与 output_hint，后者披露输出 PNG 路径。未返回可核实模型/质量。PNG尺寸、格式、Alpha与SHA-256由落盘文件实测。",
        "unverifiedReason": "宿主管理，工具未披露可核实版本/质量；配置目标 GPT Image 2.5 Sunburst/max 不是实际版本证明。",
        "prompt": item["prompt"],
        "promptSha256": digest(root/item["prompt"]),
        "references": refs,
        "source": {"toolNativeOutput":item["source"],"sha256":digest(Path(item["source"])),"operation":"byte-identical copy","derived":False},
        "inspection": {**item["checks"],"pngIntegrity":"passed","nativeCopyHashMatches":digest(path)==digest(Path(item["source"])),"alphaStatistics":alpha_stats},
        "status": {"assetStage":"direction_draft_v1","readyForUserReview":True,"userApproved":False,"productionAccepted":False,"uiSlicesDelivered":False,"clientIntegrated":False},
        "delivery": {"localOnly":True,"uploaded":False,"remoteConfigured":False}
    }
    (root / (item["file"]+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"file":item["file"],"sha256":record["sha256"],"width":width,"height":height,"mode":image_meta["mode"],"recordSaved":True},ensure_ascii=False))

