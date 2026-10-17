"""Post-hoc routing analysis of frozen model predictions, not a new inference or deployment."""
from pathlib import Path
import collections, hashlib, json, math
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"review-triage-analysis-v1"
OUT.mkdir(exist_ok=False)
def rows(path):return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
cases=rows(ROOT/"data"/"cases.jsonl")
annotations={a["case_id"]:a for a in rows(ROOT/"data"/"annotations.jsonl")}
predictions={r["case_id"]:r for r in rows(ROOT/"runs"/"kev08_v1"/"predictions.jsonl") if r["variant"]=="original"}
rules={r["case_id"]:r for r in rows(ROOT/"runs"/"rules_v1"/"predictions.jsonl")}
derived=[]
for c in cases:
    a=annotations[c["case_id"]]
    p=predictions[c["case_id"]]["answers"]["compatibility"]
    dist=p["probabilities"]; vals=sorted(dist.values(),reverse=True); K=len(vals)
    expected="review" if a["labels"]["compatibility"] in ("conflict","insufficient") else "keep_unchanged_candidate"
    choice=p["decision"]
    derived.append({"case_id":c["case_id"],"group_id":c["group_id"],"input_sha256":c["input_sha256"],
        "allowed_action":"keep both memories unchanged","review_scope":"pairwise coexistence only; not truth, merge, deletion, or role-specific use",
        "reference_status":"derived from unreviewed proposal; no independent review",
        "reference_annotation":a["annotation_id"],"reference_route":expected,
        "model_choice":choice,"p_max":vals[0],"margin":vals[0]-vals[1],
        "normalized_choice_confidence":(vals[0]-1/K)/(1-1/K),
        "normalized_entropy":-sum(p*math.log(p) for p in vals if p>0)/math.log(K),
        "rules_choice":rules[c["case_id"]]["answers"]["compatibility"]["decision"],
        "top_choice_route":"keep_unchanged_candidate" if choice=="compatible" else "review",
        "posthoc_p05_route":"keep_unchanged_candidate" if choice=="compatible" and vals[0]>=.5 else "review",
        "rules_route":"keep_unchanged_candidate" if rules[c["case_id"]]["answers"]["compatibility"]["decision"]=="compatible" else "review"})
def summary(field):
    passed=[r for r in derived if r[field]=="keep_unchanged_candidate"]
    reviewed=[r for r in derived if r[field]=="review"]
    return {"keep_candidates":len(passed),"keep_candidate_ids":[r["case_id"] for r in passed],
            "reviewed":len(reviewed),"missed_reference_review":sum(r["reference_route"]=="review" for r in passed),
            "unnecessary_review_against_proposal":sum(r["reference_route"]=="keep_unchanged_candidate" for r in reviewed),
            "agreements_with_derived_proposal":sum(r[field]==r["reference_route"] for r in derived)}
report={"analysis_status":"post-hoc exploratory; thresholds not validated",
        "reference_review_count":sum(r["reference_route"]=="review" for r in derived),
        "reference_keep_count":sum(r["reference_route"]=="keep_unchanged_candidate" for r in derived),
        "case_count":len(derived),"source_families":3,"independently_reviewed_labels":0,
        "top_choice_mapping":summary("top_choice_route"),"pmax_0_5_mapping":summary("posthoc_p05_route"),
        "rules_mapping":summary("rules_route"),
        "pmax_0_5_keep_not_already_kept_by_rules":[r["case_id"] for r in derived if r["posthoc_p05_route"]=="keep_unchanged_candidate" and r["rules_route"]!="keep_unchanged_candidate"],
        "higher_confidence_insufficient_cases":[r["case_id"] for r in derived if r["model_choice"]=="insufficient" and r["p_max"]>=.5],
        "limitations":["reference is derived from the same unreviewed labels","action limited to unchanged preservation","all analyses are after seeing v1 outcomes","no new classifier trained or run","no operational review bypass installed"]}
dump(OUT/"report.json",report)
with (OUT/"derived_routes.jsonl").open("x",encoding="utf-8") as f:
    for r in derived:f.write(json.dumps(r,ensure_ascii=False)+"\n")
dump(OUT/"inputs.json",{"prediction_sha256":hashlib.sha256((ROOT/"runs"/"kev08_v1"/"predictions.jsonl").read_bytes()).hexdigest(),
                      "annotation_sha256":hashlib.sha256((ROOT/"data"/"annotations.jsonl").read_bytes()).hexdigest()})
print(json.dumps(report,ensure_ascii=False,indent=2))
