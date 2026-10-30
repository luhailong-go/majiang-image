from pathlib import Path
from PIL import Image
from datetime import datetime, timezone, timedelta
import argparse, hashlib, json, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

root=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(): return datetime.now(timezone(timedelta(hours=-4))).isoformat(timespec='seconds')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--dest',required=True)
    ap.add_argument('--prompt',required=True)
    ap.add_argument('--refs',nargs='+',required=True)
    ap.add_argument('--transparent',action='store_true')
    ap.add_argument('--purpose',required=True)
    a=ap.parse_args()
    src=Path(a.source); dst=root/a.dest
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and sha(dst)!=sha(src): raise ValueError('Use a new versioned path: '+str(dst))
    if not dst.exists(): shutil.copyfile(src,dst)
    with Image.open(dst) as im:
        im.load(); size=im.size; mode=im.mode
        alpha=im.getchannel('A') if 'A' in im.getbands() else None
        alphaInfo=None if alpha is None else {'range':list(alpha.getextrema()),'bbox':alpha.getbbox(),'corners':[alpha.getpixel(p) for p in [(0,0),(size[0]-1,0),(0,size[1]-1),(size[0]-1,size[1]-1)]]}
    cfg=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig'))
    rec={'schemaVersion':2,'file':a.dest.replace('\\','/'),'sha256':sha(dst),'generatedAt':stamp(),'generationTimestampBasis':'client observed completion, not provider timestamp','tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':a.transparent,'referenced_image_paths':[str(root/r) for r in a.refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未披露可核实实际型号/质量。配置目标不等于真实返回参数。','evidence':'工具output_hint提供PNG落盘路径；尺寸/格式/哈希由文件实测。','prompt':a.prompt,'promptSha256':sha(root/a.prompt),'references':[{'file':r,'sha256':sha(root/r),'actuallyAttached':True} for r in a.refs],'source':{'toolNativeOutput':str(src),'sha256':sha(src),'operation':'byte-identical copy'},'width':size[0],'height':size[1],'nativeDimensions':{'width':size[0],'height':size[1]},'mode':mode,'format':'PNG','alpha':alphaInfo,'resampled':False,'purpose':a.purpose,'inspection':{'status':'pending_visual_review'},'status':{'productionAccepted':False,'userApproved':False,'clientIntegrated':False},'delivery':{'localOnly':True,'uploaded':False}}
    Path(str(dst)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:rec[k] for k in ['file','sha256','width','height','mode']},ensure_ascii=False))
if __name__=='__main__':main()
