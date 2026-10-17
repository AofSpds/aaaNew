"""Append cases and human/model annotations without rewriting the frozen pilot data."""
from pathlib import Path
import argparse, datetime, hashlib, json, re
ROOT=Path(__file__).resolve().parent
LIVE=ROOT/"collection"
def rows(path): return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()] if path.exists() else []
def digest(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding="utf-8-sig"))
def append(path,item):
    with path.open("a",encoding="utf-8") as f:
        f.write(json.dumps(item,ensure_ascii=False,allow_nan=False)+"\n")
def validate_case(item,existing,check_source=False):
    if not re.fullmatch(r"[A-Za-z0-9_-]+",item["case_id"]):raise ValueError("Invalid case ID")
    if item["case_id"] in {r["case_id"] for r in existing}:raise ValueError("Case ID already exists; add a new version")
    if not item.get("group_id"):raise ValueError("Source family group is required")
    if item["origin"] not in ("observed_source_pair","controlled_variant"):raise ValueError("Unknown origin")
    inp=item["input"]
    if not all(isinstance(inp.get(k),str) and inp[k].strip() for k in ("memory_a","memory_b","context")):raise ValueError("Two memories and context required")
    if item["input_sha256"]!=digest(inp):raise ValueError("Input hash mismatch")
    if item["input_sha256"] in {r["input_sha256"] for r in existing}:raise ValueError("Duplicate input; reuse the existing case")
    if not item.get("source_refs"):raise ValueError("Source evidence required")
    if item["origin"]=="controlled_variant" and not item.get("transformation"):raise ValueError("Describe controlled changes")
    for ref in item["source_refs"]:
        for field in ("path","sha256","excerpt","excerpt_sha256","start_line"):
            if field not in ref:raise ValueError("Incomplete source reference: "+field)
        if hashlib.sha256(ref["excerpt"].encode()).hexdigest()!=ref["excerpt_sha256"]:raise ValueError("Excerpt hash mismatch")
        if check_source:
            raw=Path(ref["path"]).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=ref["sha256"]:raise ValueError("Source changed; capture its new revision")
            if ref["excerpt"] not in raw.decode("utf-8-sig"):raise ValueError("Source excerpt missing")
    if item.get("split")!="exploratory":raise ValueError("New captures remain exploratory until a group-aware split is frozen")

def validate_annotation(item,cases,existing):
    indexed={r["case_id"]:r for r in cases}
    if item["case_id"] not in indexed:raise ValueError("Unknown case ID")
    if item["input_sha256"]!=indexed[item["case_id"]]["input_sha256"]:raise ValueError("Annotation input mismatch")
    if item["annotation_id"] in {r["annotation_id"] for r in existing}:raise ValueError("Annotation ID already exists")
    if item["status"] not in ("proposed","reviewed","disputed"):raise ValueError("Unknown annotation status")
    if not item.get("author") or not item.get("rationale"):raise ValueError("Author and rationale required")
    if item["status"]=="reviewed" and item.get("independent_review") is not True:raise ValueError("Reviewed label needs an explicitly recorded independent review")
    questions=load(ROOT/"data"/"questions.v1.json")
    if set(item["labels"])!=set(questions):raise ValueError("Question mismatch")
    for key,label in item["labels"].items():
        if label not in questions[key]["criteria"]:raise ValueError("Unknown label")
    if item.get("supersedes"):
        old=next((r for r in existing if r["annotation_id"]==item["supersedes"]),None)
        if old is None or old["case_id"]!=item["case_id"]:raise ValueError("Invalid superseded annotation")

def validate_all(check_source=False):
    cases=rows(LIVE/"cases.jsonl"); anns=rows(LIVE/"annotations.jsonl")
    prior=[]
    for item in cases:validate_case(item,prior,check_source);prior.append(item)
    prior=[]
    for item in anns:validate_annotation(item,cases,prior);prior.append(item)
    latest={}
    for a in anns:latest[a["case_id"]]=a
    return {"cases":len(cases),"annotations":len(anns),"independently_reviewed":sum(a["status"]=="reviewed" for a in latest.values()),
            "observed_source_pairs":sum(c["origin"]=="observed_source_pair" for c in cases),
            "controlled_variants":sum(c["origin"]=="controlled_variant" for c in cases),
            "unlabelled_cases":[c["case_id"] for c in cases if c["case_id"] not in latest],
            "groups":sorted({c["group_id"] for c in cases}),"source_current_check":check_source}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("command",choices=["validate","add-case","add-annotation"]);ap.add_argument("--file");ap.add_argument("--check-current-sources",action="store_true");a=ap.parse_args()
    if a.command=="validate":print(json.dumps(validate_all(a.check_current_sources),ensure_ascii=False,indent=2));return
    if not a.file:raise ValueError("--file required")
    item=load(a.file);cases=rows(LIVE/"cases.jsonl");anns=rows(LIVE/"annotations.jsonl")
    if a.command=="add-case":
        item.setdefault("schema_version",1);item.setdefault("created_at",datetime.datetime.now(datetime.timezone.utc).isoformat())
        item.setdefault("input_sha256",digest(item["input"]));item.setdefault("split","exploratory")
        validate_case(item,cases,True);append(LIVE/"cases.jsonl",item)
    else:
        item.setdefault("created_at",datetime.datetime.now(datetime.timezone.utc).isoformat())
        validate_annotation(item,cases,anns);append(LIVE/"annotations.jsonl",item)
    print(json.dumps(validate_all(),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
