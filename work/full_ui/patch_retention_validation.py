from pathlib import Path
R=Path(r"D:\work\majiang-image")
p=R/"work/full_ui/validate_delivery.py";s=p.read_text(encoding="utf-8-sig")
s=s.replace("errors=[];warnings=[];record_count=0;checked_records=set();checks=[]","errors=[];warnings=[];record_count=0;checked_records=set();checks=[];historical_removed=set()")
s=s.replace('''  p=resolve(f);require(p.is_file(),label+" missing "+f)
  if p.is_file() and ref.get("sha256"):require(digest(p)==ref["sha256"].lower(),label+" hash "+f)''','''  p=resolve(f)
  if not p.is_file() and ref.get("pixelsPresentInProject") is False:
   rp=p.with_name(p.name+".generation.json")
   require(rp.is_file(),"Removed source must retain provenance "+f)
   if rp.is_file():
    rd=json.loads(rp.read_text(encoding="utf-8-sig"))
    require(rd.get("pixelsRetainedInProject") is False and bool(rd.get("cleanup")),"Removed source cleanup evidence "+f)
    require(rd.get("sha256")==ref.get("sha256"),"Removed source provenance hash "+f)
    historical_removed.add(f);check_record(rp)
  else:
   require(p.is_file(),label+" missing "+f)
   if p.is_file() and ref.get("sha256"):require(digest(p)==ref["sha256"].lower(),label+" hash "+f)''')
s=s.replace('''  f=resolve(d["file"]);require(f.is_file(),"Record image missing "+str(f))
  if f.is_file():require(digest(f)==d["sha256"].lower(),"Record image hash "+str(f))''','''  f=resolve(d["file"])
  if not f.is_file() and d.get("pixelsRetainedInProject") is False and d.get("cleanup"):
   historical_removed.add(d["file"])
  else:
   require(f.is_file(),"Record image missing "+str(f))
   if f.is_file():require(digest(f)==d["sha256"].lower(),"Record image hash "+str(f))''')
s=s.replace('"warnings":warnings,"browserInteraction"','"warnings":warnings,"historicalSourcesRemovedPerRetentionPolicy":sorted(historical_removed),"browserInteraction"')
p.write_text(s,encoding="utf-8")
print("Validator now verifies explicit historical-source cleanup evidence without restoring deleted pixels.")

