"""Bounded exploratory memory classification. Model never receives proposed labels."""
from pathlib import Path
import argparse, collections, copy, datetime, hashlib, json, math, os, re, statistics, sys, time, traceback
ROOT=Path(__file__).resolve().parent
def read_jsonl(path): return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
def sha(raw): return hashlib.sha256(raw).hexdigest()
def digest(obj): return sha(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
def write(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def append(f,obj):
    f.write(json.dumps(obj,ensure_ascii=False,allow_nan=False)+"\n"); f.flush()
def normalized(s): return re.sub(r"[\s.,。]", "", s)
def rules(inp):
    a,b=inp["memory_a"],inp["memory_b"]
    out={"overlap":None,"compatibility":None}
    if normalized(a)==normalized(b):
        return {"overlap":"equivalent","compatibility":"compatible"}
    fa=inp.get("structured_facts",{}).get("a",{}); fb=inp.get("structured_facts",{}).get("b",{})
    if fa and fb:
        if fa["value"]!=fb["value"]: out["overlap"]="distinct"
        fields=("role","purpose","slot","period")
        if any(fa.get(k) is None or fb.get(k) is None for k in fields):
            out["compatibility"]="insufficient"
        elif any(fa[k]!=fb[k] for k in fields):
            out["compatibility"]="compatible"
        elif fa["value"]==fb["value"]:
            out={"overlap":"equivalent","compatibility":"compatible"}
        elif fa.get("exclusive") and fb.get("exclusive"):
            out["compatibility"]="conflict"
    return out

def metrics(rows,expected,questions):
    clean=[r for r in rows if r["variant"]=="original"]
    entries=[]
    for r in clean:
        for qid,answer in r["answers"].items():
            target=expected[r["case_id"]]["labels"][qid]
            entries.append({"case_id":r["case_id"],"question":qid,"expected":target,**answer,
                            "agreement":answer["decision"]==target})
    answered=[e for e in entries if e["decision"] is not None]
    high=[e for e in entries if e.get("p_max") is not None and e["p_max"]>=.8]
    wrong=[e for e in answered if not e["agreement"]]
    all_cases_agree=sum(all(a["decision"]==expected[r["case_id"]]["labels"][q] for q,a in r["answers"].items()) for r in clean)
    order=[]
    original={r["case_id"]:r for r in clean}
    for r in rows:
        if r["variant"]!="options_reversed":continue
        for q,a in r["answers"].items():
            initial=original[r["case_id"]]["answers"][q]
            order.append({"case_id":r["case_id"],"question":q,"changed":a["decision"]!=initial["decision"],
                          "max_probability_delta":max(abs(a["probabilities"][k]-initial["probabilities"][k]) for k in a["probabilities"])})
    byq={}
    for q in questions:
        subset=[e for e in entries if e["question"]==q]
        counts=collections.Counter(e["expected"] for e in subset)
        majority,n=counts.most_common(1)[0]
        byq[q]={"n":len(subset),"answered":sum(e["decision"] is not None for e in subset),
                "agreements":sum(e["agreement"] for e in subset),
                "proposed_label_counts":dict(counts),"posthoc_majority_label":majority,
                "posthoc_majority_agreements":n}
    return {"metric_label":"agreement with unreviewed proposals; not validated accuracy",
            "case_count":len(clean),"question_count":len(entries),"answered":len(answered),
            "abstained":len(entries)-len(answered),"agreements":sum(e["agreement"] for e in entries),
            "agreement_all":sum(e["agreement"] for e in entries)/len(entries),
            "all_questions_agree_cases":all_cases_agree,"by_question":byq,
            "pmax_at_least_0_8":{"questions":len(high),"disagreements":sum(not e["agreement"] for e in high),
                               "note":"prespecified diagnostic cutoff; no error-rate guarantee"},
            "false_equivalence_candidates":[e for e in entries if e["question"]=="overlap" and e["decision"]=="equivalent" and e["expected"]!="equivalent"],
            "conflict_misses":[e for e in entries if e["question"]=="compatibility" and e["expected"]=="conflict" and e["decision"]=="compatible"],
            "disagreements":wrong,"permutation":{"questions":len(order),"changed":sum(e["changed"] for e in order),"details":order},
            "latency_ms":{"total":sum(r["elapsed_ms"] for r in clean),"median":statistics.median(r["elapsed_ms"] for r in clean),
                          "note":"local CPU exploratory run; includes encoding and scoring, excludes model load"},
            "entries":entries}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--engine",choices=["rules","kev"],required=True); ap.add_argument("--run",required=True); args=ap.parse_args()
    if not re.fullmatch(r"[a-z0-9_-]+",args.run):raise ValueError("Unsafe run name")
    out=ROOT/"runs"/args.run; out.mkdir(exist_ok=False)
    freeze=json.loads((ROOT/"data"/"freeze.v1.json").read_text(encoding="utf-8"))
    files={"dataset_sha256":"cases.jsonl","annotations_sha256":"annotations.jsonl","questions_sha256":"questions.v1.json"}
    for key,name in files.items():
        if sha((ROOT/"data"/name).read_bytes())!=freeze[key]:raise ValueError("Frozen v1 file changed: "+name)
        (out/name).write_bytes((ROOT/"data"/name).read_bytes())
    cases=read_jsonl(out/"cases.jsonl")
    anns=read_jsonl(out/"annotations.jsonl"); expected={a["case_id"]:a for a in anns}
    questions=json.loads((out/"questions.v1.json").read_text(encoding="utf-8"))
    if len({c["case_id"] for c in cases})!=len(cases):raise ValueError("Duplicate case ID")
    for c in cases:
        if digest(c["input"])!=c["input_sha256"]:raise ValueError("Input hash mismatch")
        if expected[c["case_id"]]["input_sha256"]!=c["input_sha256"]:raise ValueError("Annotation belongs to another input")
        for q,label in expected[c["case_id"]]["labels"].items():
            if label not in questions[q]["criteria"]:raise ValueError("Unknown label")
        for ref in c["source_refs"]:
            if sha(Path(ref["path"]).read_bytes())!=ref["sha256"]:raise ValueError("Source changed before run")
    meta={"run_id":args.run,"engine":args.engine,"started_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "data_freeze":freeze,"python":sys.version,"input_policy":"input and questions only; labels/source rationales excluded",
          "source_commit":json.loads((ROOT/"source_manifest.json").read_text(encoding="utf-8"))["commit"]}
    write(out/"run.json",meta)
    try:
        tok=model=None
        if args.engine=="kev":
            os.environ["HF_HOME"]=str(ROOT/".cache"/"huggingface")
            os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
            os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"]="1"
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"]="1"
            os.environ["TOKENIZERS_PARALLELISM"]="false"
            sys.path.insert(0,str(ROOT/"vendor"/"kev"))
            import torch
            import transformers,peft
            from huggingface_hub import HfApi
            from kev.checkpoint import Checkpoint,LoadOptions
            from kev.api import SystemOneRequest,to_record
            from kev.model import ContextOverflow
            torch.set_num_threads(4); torch.set_num_interop_threads(1)
            info=HfApi(token=False).model_info("jaredpalmer/kev-0.8b",revision="v1.0")
            meta.update(model="jaredpalmer/kev-0.8b",model_revision=info.sha,torch=torch.__version__,
                        transformers=transformers.__version__,peft=peft.__version__,device="cpu",dtype="float32")
            write(out/"run.json",meta); print("Loading pinned Kev 0.8B "+info.sha,flush=True)
            began=time.perf_counter()
            ck=Checkpoint("jaredpalmer/kev-0.8b@"+info.sha)
            tok,model=ck.load("cpu",LoadOptions(dtype=torch.float32,backend="torch",fused=False,cuda_graphs=False))
            meta.update(load_seconds=time.perf_counter()-began,base=ck.meta.base,base_revision=ck.meta.base_revision,
                        temperature=model.head.temperature,head_sha256=sha(ck.file("head.pt").read_bytes()))
            if not ck.meta.base_revision:raise ValueError("Base revision was not pinned")
            write(out/"run.json",meta); print("Model loaded; begin blinded predictions.",flush=True)
        rows=[]
        with (out/"predictions.jsonl").open("x",encoding="utf-8") as predfile,(out/"requests.jsonl").open("x",encoding="utf-8") as reqfile:
            for variant in (["original","options_reversed"] if args.engine=="kev" else ["original"]):
                for c in cases:
                    if variant=="options_reversed" and c["case_id"] not in freeze["permutation_cases"]: continue
                    q=copy.deepcopy(questions)
                    if variant=="options_reversed":
                        for question in q.values():question["criteria"]=dict(reversed(list(question["criteria"].items())))
                    request={"state":c["input"],"questions":q}
                    append(reqfile,{"case_id":c["case_id"],"variant":variant,"request_sha256":digest(request),"request":request})
                    start=time.perf_counter(); state_tokens=None
                    if args.engine=="rules":
                        decision=rules(c["input"])
                        answers={k:{"decision":v,"p_max":None,"probabilities":None} for k,v in decision.items()}
                    else:
                        record,qmeta=to_record(SystemOneRequest.model_validate(request))
                        enc=model.encode(tok,record,max_state=2048,max_branch=4096,strict=True)
                        if enc["state_truncated"]:raise ValueError("Unexpected truncation")
                        state_tokens=enc["state_tokens"]
                        with torch.inference_mode():probs=model.probs(enc)
                        answers={}
                        for m,p in zip(qmeta,probs):
                            vals=[float(x) for x in p.tolist()]
                            if not all(math.isfinite(x) and 0<=x<=1 for x in vals) or abs(sum(vals)-1)>1e-5:raise ValueError("Invalid probabilities")
                            dist=dict(zip(m["keys"],vals))
                            answers[m["id"]]={"decision":max(dist,key=dist.get),"p_max":max(vals),"probabilities":dist}
                    row={"case_id":c["case_id"],"group_id":c["group_id"],"origin":c["origin"],"variant":variant,
                         "input_sha256":c["input_sha256"],"request_sha256":digest(request),
                         "state_tokens":state_tokens,"truncated":False,"elapsed_ms":(time.perf_counter()-start)*1000,"answers":answers}
                    append(predfile,row);rows.append(row)
                    print(json.dumps({"case":c["case_id"],"variant":variant,"decisions":{k:v["decision"] for k,v in answers.items()},"ms":round(row["elapsed_ms"],1)},ensure_ascii=False),flush=True)
        report=metrics(rows,expected,questions)
        checks={"unique_case_ids":True,"frozen_inputs":True,"labels_excluded_from_requests":True,
                "complete_predictions":len(rows)==(24 if args.engine=="kev" else 18),
                "source_files_unchanged":all(sha(Path(r["path"]).read_bytes())==r["sha256"] for c in cases for r in c["source_refs"])}
        if args.engine=="kev":
            first={"state":cases[0]["input"],"questions":questions}
            record,_=to_record(SystemOneRequest.model_validate(first))
            try:
                model.encode(tok,record,max_state=2,max_branch=4096,strict=True)
                checks["strict_overflow_rejected"]=False
            except ContextOverflow:checks["strict_overflow_rejected"]=True
        report["checks"]=checks
        write(out/"report.json",report)
        meta.update(status="completed",finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        write(out/"run.json",meta)
        print(json.dumps({"run":args.run,"agreements":report["agreements"],"questions":report["question_count"],
                          "all_agree_cases":report["all_questions_agree_cases"],"order_changes":report["permutation"]["changed"],"checks":checks},ensure_ascii=False),flush=True)
    except Exception as e:
        meta.update(status="failed",error_type=type(e).__name__,error=str(e)[:2500])
        write(out/"run.json",meta); (out/"error.txt").write_text(traceback.format_exc(),encoding="utf-8")
        raise
if __name__=="__main__":main()
