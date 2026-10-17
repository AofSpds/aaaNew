"""Order-only perturbations with stable candidate identities and no reference labels in model requests."""
from pathlib import Path
import collections,copy,datetime,hashlib,json,math,os,random,statistics,sys,time,traceback
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"runs"/"order_study_v1"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def lines(p):return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x]
def dumps(x):return json.dumps(x,ensure_ascii=False,separators=(",",":"),allow_nan=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def ordered_hash(x):return sha(dumps(x).encode())
def semantic_hash(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def route(label):return "keep_unchanged_candidate" if label=="compatible" else "review"
def methods(cid,qid,q,prior):
    keys=list(q["criteria"]); orders={"original":keys,"reverse":keys[::-1],"key_asc":sorted(keys),
         "description_length_asc":sorted(keys,key=lambda k:(len(q["criteria"][k]),k))}
    for seed in (11,29):
        ks=keys[:];random.Random(str(seed)+":"+cid+":"+qid).shuffle(ks);orders["random_"+str(seed)]=ks
    orders["prior_score_desc"]=sorted(keys,key=lambda k:(-prior[k],k))
    for shift in range(1,len(keys)):orders["cycle_"+str(shift)]=keys[shift:]+keys[:shift]
    return orders
def main():
    OUT.mkdir(exist_ok=False)
    os.environ["HF_HOME"]=str(ROOT/".cache"/"huggingface");os.environ["HF_HUB_OFFLINE"]="1";os.environ["TOKENIZERS_PARALLELISM"]="false"
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    sys.path.insert(0,str(ROOT/"vendor"/"kev"))
    import torch,transformers,peft
    from kev.checkpoint import Checkpoint,LoadOptions
    from kev.api import SystemOneRequest,to_record
    torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(17)
    cases=lines(ROOT/"data"/"cases.jsonl");questions=read(ROOT/"data"/"questions.v1.json")
    old_run=read(ROOT/"runs"/"kev08_v1"/"run.json")
    prior={r["case_id"]:r for r in lines(ROOT/"runs"/"kev08_v1"/"predictions.jsonl") if r["variant"]=="original"}
    source_hashes={ref["path"]:ref["sha256"] for c in cases for ref in c["source_refs"]}
    if not all(sha(Path(p).read_bytes())==s for p,s in source_hashes.items()):raise ValueError("Original source changed")
    plans=[]; requests={}; lookup={}; prep=[]
    for c in cases:
        cid=c["case_id"]
        for qid,q in questions.items():
            orders=methods(cid,qid,q,prior[cid]["answers"][qid]["probabilities"])
            base_keys=list(q["criteria"])
            schedules=[(name,"original",order) for name,order in orders.items()]
            schedules.append(("memory_b_first","memory_b_first",base_keys))
            if cid in ["L01","P04","S04"]:schedules.append(("repeat_original","original",base_keys))
            for name,style,order in schedules:
                state=copy.deepcopy(c["input"])
                if style=="memory_b_first":
                    state={k:state[k] for k in ["context","memory_b","memory_a"]+([ "structured_facts"] if "structured_facts" in state else [])}
                assert semantic_hash(state)==semantic_hash(c["input"])
                question=copy.deepcopy(q);question["criteria"]={k:q["criteria"][k] for k in order}
                assert set(order)==set(base_keys) and len(order)==len(base_keys)
                req={"state":state,"questions":{qid:question}}
                rec,meta=to_record(SystemOneRequest.model_validate(req))
                rendered={"state":rec["state"],"instructions":rec["questions"][0]["instr"],"options":rec["questions"][0]["options"]}
                h=ordered_hash(rendered)
                cache_key=(cid,qid,h,"repeat" if name=="repeat_original" else "main")
                if cache_key not in lookup:
                    rid="request_"+str(len(requests)+1).zfill(4);lookup[cache_key]=rid
                    requests[rid]={"request_id":rid,"case_id":cid,"question_id":qid,"input_layout":style,"option_order":order,
                         "rendered_sha256":h,"request":req,"rendered_input":rendered}
                rid=lookup[cache_key]
                plans.append({"case_id":cid,"question_id":qid,"method":name,"request_id":rid,"option_order":order})
    for name in ["cases.jsonl","annotations.jsonl","questions.v1.json"]:
        (OUT/name).write_bytes((ROOT/"data"/name).read_bytes())
    write(OUT/"plan.json",plans)
    with (OUT/"requests.jsonl").open("x",encoding="utf-8") as f:
        for req in requests.values():f.write(dumps(req)+"\n")
    run={"status":"prepared","started_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "model_revision":old_run["model_revision"],"source_commit":old_run["source_commit"],
         "base_revision":old_run["base_revision"],"device":"cpu","dtype":"float32","torch":torch.__version__,
         "transformers":transformers.__version__,"peft":peft.__version__,"questions_per_request":1,
         "unique_requests":len(requests),"method_assignments":len(plans),"plan_sha256":sha((OUT/"plan.json").read_bytes()),
         "data_sha256":sha((OUT/"cases.jsonl").read_bytes()),"questions_sha256":sha((OUT/"questions.v1.json").read_bytes()),
         "design":"original/reverse/key/description length/prior score/2 seeded shuffles/balanced cycles; B-first display; 3-case repeat control",
         "deduplication":"identical rendered requests share an evaluation; repeat controls always rerun",
         "evaluation":"labels read only after inference; agreement with unreviewed proposals, not validated accuracy",
         "context_limits":{"state":2048,"branch":4096},"source_hashes_before":source_hashes}
    write(OUT/"run.json",run)
    print(json.dumps({"requests":len(requests),"plan_assignments":len(plans)},ensure_ascii=False),flush=True)
    try:
        ck=Checkpoint("jaredpalmer/kev-0.8b@"+run["model_revision"])
        began=time.perf_counter()
        tok,model=ck.load("cpu",LoadOptions(dtype=torch.float32,backend="torch",fused=False,cuda_graphs=False))
        run.update(status="running",load_seconds=time.perf_counter()-began,temperature=model.head.temperature)
        write(OUT/"run.json",run)
        results={}
        with (OUT/"predictions.jsonl").open("x",encoding="utf-8") as f:
            for idx,(rid,item) in enumerate(requests.items(),1):
                rec,meta=to_record(SystemOneRequest.model_validate(item["request"]))
                start=time.perf_counter()
                enc=model.encode(tok,rec,max_state=2048,max_branch=4096,strict=True)
                if enc["state_truncated"]:raise ValueError("Input truncated")
                with torch.inference_mode():p=model.probs(enc)[0]
                dist=dict(zip(meta[0]["keys"],map(float,p.tolist())))
                if any(not math.isfinite(v) or v<0 or v>1 for v in dist.values()) or abs(sum(dist.values())-1)>1e-5:raise ValueError("Bad distribution")
                row={k:item[k] for k in ["request_id","case_id","question_id","input_layout","option_order","rendered_sha256"]}
                row.update(decision=max(dist,key=dist.get),probabilities=dist,p_max=max(dist.values()),
                           elapsed_ms=(time.perf_counter()-start)*1000,state_tokens=enc["state_tokens"],truncated=False)
                results[rid]=row;f.write(dumps(row)+"\n");f.flush()
                if idx%12==0 or idx==len(requests):
                    print(json.dumps({"completed":idx,"total":len(requests),"last_case":item["case_id"],"last_question":item["question_id"]}),flush=True)
        annotations={a["case_id"]:a for a in lines(OUT/"annotations.jsonl")}
        table={(p["case_id"],p["question_id"],p["method"]):results[p["request_id"]] for p in plans}
        original={(c["case_id"],q):table[(c["case_id"],q,"original")] for c in cases for q in questions}
        method_rows=[]
        for name in dict.fromkeys(p["method"] for p in plans):
            for qid in questions:
                selected=[p for p in plans if p["method"]==name and p["question_id"]==qid]
                if not selected:continue
                diffs=[];flips=0;correct=0;routeflips=0;keep=0;miss=0
                for p in selected:
                    row=results[p["request_id"]];orig=original[(p["case_id"],qid)]
                    flips+=row["decision"]!=orig["decision"]
                    diffs.append(max(abs(row["probabilities"][k]-orig["probabilities"][k]) for k in row["probabilities"]))
                    target=annotations[p["case_id"]]["labels"][qid]
                    correct+=row["decision"]==target
                    if qid=="compatibility":
                        routeflips+=route(row["decision"])!=route(orig["decision"])
                        keep+=route(row["decision"])=="keep_unchanged_candidate"
                        miss+=route(row["decision"])=="keep_unchanged_candidate" and target!="compatible"
                method_rows.append({"method":name,"question_id":qid,"n":len(selected),"flips_from_original":flips,
                       "agreements_with_proposal":correct,"mean_max_probability_delta":statistics.mean(diffs),"max_probability_delta":max(diffs),
                       "review_route_flips":routeflips if qid=="compatibility" else None,
                       "keep_candidates":keep if qid=="compatibility" else None,"missed_reference_review":miss if qid=="compatibility" else None})
        sensitivity=[];ensembles=[]
        for c in cases:
            cid=c["case_id"]
            for qid,q in questions.items():
                optionplans=[p for p in plans if p["case_id"]==cid and p["question_id"]==qid and p["method"] not in ("memory_b_first","repeat_original")]
                unique={p["request_id"]:results[p["request_id"]] for p in optionplans}
                decisions={r["decision"] for r in unique.values()}
                span={k:max(r["probabilities"][k] for r in unique.values())-min(r["probabilities"][k] for r in unique.values()) for k in q["criteria"]}
                target=annotations[cid]["labels"][qid]
                sensitivity.append({"case_id":cid,"question_id":qid,"unique_orders":len(unique),"different_decisions":sorted(decisions),
                       "unstable":len(decisions)>1,"stable_wrong":len(decisions)==1 and next(iter(decisions))!=target,
                       "max_option_probability_range":max(span.values()),
                       "route_unstable":len({route(d) for d in decisions})>1 if qid=="compatibility" else None,
                       "all_orders_keep":decisions=={"compatible"} if qid=="compatibility" else None})
                cycles=[original[(cid,qid)]]+[table[(cid,qid,"cycle_"+str(i))] for i in range(1,len(q["criteria"]))]
                means={k:sum(r["probabilities"][k] for r in cycles)/len(cycles) for k in q["criteria"]}
                meanpred=max(means,key=means.get);vote=collections.Counter(r["decision"] for r in cycles)
                winners=[k for k,n in vote.items() if n==max(vote.values())]
                ensembles.append({"case_id":cid,"question_id":qid,"n_passes":len(cycles),"mean_probabilities":means,
                      "mean_decision":meanpred,"mean_agrees":meanpred==target,"vote_decision":winners[0] if len(winners)==1 else None,
                      "vote_tied":len(winners)>1,"vote_agrees":len(winners)==1 and winners[0]==target,
                      "mean_keep":meanpred=="compatible" if qid=="compatibility" else None,
                      "mean_missed_reference_review":meanpred=="compatible" and target!="compatible" if qid=="compatibility" else None})
        parity=[]
        for (cid,qid),r in original.items():
            old=prior[cid]["answers"][qid]
            parity.append({"case_id":cid,"question_id":qid,"argmax_changed":r["decision"]!=old["decision"],
                          "max_delta":max(abs(old["probabilities"][k]-r["probabilities"][k]) for k in r["probabilities"])})
        checks={"complete_requests":len(results)==len(requests),"no_input_truncation":all(not r["truncated"] for r in results.values()),
                "source_files_unchanged":all(sha(Path(p).read_bytes())==s for p,s in source_hashes.items()),
                "plan_unchanged":sha((OUT/"plan.json").read_bytes())==run["plan_sha256"],
                "prior_packed_vs_current_single_question_argmax_changes":sum(p["argmax_changed"] for p in parity),
                "prior_packed_vs_current_single_question_max_delta":max(p["max_delta"] for p in parity)}
        report={"case_count":18,"question_count":36,"unique_requests":len(results),"methods":method_rows,
                "option_sensitivity":{q:{"unstable":sum(s["unstable"] for s in sensitivity if s["question_id"]==q),
                                        "stable_wrong":sum(s["stable_wrong"] for s in sensitivity if s["question_id"]==q),
                                        "n":18} for q in questions},
                "review_route_unstable_cases":[s["case_id"] for s in sensitivity if s["question_id"]=="compatibility" and s["route_unstable"]],
                "all_tested_orders_keep_cases":[s["case_id"] for s in sensitivity if s["question_id"]=="compatibility" and s["all_orders_keep"]],
                "cycle_mean":{q:{"agreements":sum(e["mean_agrees"] for e in ensembles if e["question_id"]==q),
                                "vote_agreements":sum(e["vote_agrees"] for e in ensembles if e["question_id"]==q),
                                "vote_ties":sum(e["vote_tied"] for e in ensembles if e["question_id"]==q),"n":18} for q in questions},
                "cycle_mean_keep_candidates":sum(bool(e["mean_keep"]) for e in ensembles if e["question_id"]=="compatibility"),
                "cycle_mean_missed_reference_review":sum(bool(e["mean_missed_reference_review"]) for e in ensembles if e["question_id"]=="compatibility"),
                "inference_seconds":sum(r["elapsed_ms"] for r in results.values())/1000,
                "single_question_median_ms":statistics.median(r["elapsed_ms"] for r in results.values()),"checks":checks,
                "limitations":["18 examples from 3 source families; unreviewed proposals","sorts fixed before this run but v1 was already inspected",
                               "no independent test split","display reorder does not alter identities or event chronology",
                               "not all 24 overlap permutations necessarily covered","no long-context placement trial","mean/vote needs K passes per question"]}
        write(OUT/"report.json",report);write(OUT/"sensitivity.json",sensitivity);write(OUT/"ensembles.json",ensembles);write(OUT/"parity.json",parity)
        run.update(status="completed",finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());write(OUT/"run.json",run)
        print(json.dumps({"done":True,"sensitivity":report["option_sensitivity"],"route_unstable":report["review_route_unstable_cases"],"checks":checks}),flush=True)
    except Exception as e:
        run.update(status="failed",error_type=type(e).__name__,error=str(e)[:2000]);write(OUT/"run.json",run)
        (OUT/"error.txt").write_text(traceback.format_exc(),encoding="utf-8");raise
if __name__=="__main__":main()
