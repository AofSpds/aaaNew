from pathlib import Path
import copy,json,os,sys,time,hashlib,datetime
ROOT=Path(__file__).resolve().parent
out=ROOT/"runs"/"diagnostic_v1";out.mkdir(exist_ok=False)
os.environ["HF_HOME"]=str(ROOT/".cache"/"huggingface");os.environ["HF_HUB_OFFLINE"]="1";os.environ["TOKENIZERS_PARALLELISM"]="false"
sys.path.insert(0,str(ROOT/"vendor"/"kev"))
import torch
from kev.checkpoint import Checkpoint,LoadOptions
from kev.api import SystemOneRequest,to_record
torch.set_num_threads(4);torch.set_num_interop_threads(1)
base=json.loads((ROOT/"runs"/"kev08_v1"/"run.json").read_text(encoding="utf-8"))
simple_en={"door":{"type":"choice","instructions":"What is the door's state? Use only the given statement.","criteria":{"open":"The door is open.","closed":"The door is closed.","unknown":"The statement does not specify."}}}
simple_ko={"door":{"type":"choice","instructions":"제시된 문장에 따르면 문은 어떤 상태인가?","criteria":{"open":"문이 열려 있다.","closed":"문이 닫혀 있다.","unknown":"문장에 정보가 없다."}}}
english_questions={
 "overlap":{"type":"choice","instructions":"Compare the specific assertions in memory A and B, including their scope and conditions. Sharing a topic is not the same as making a shared assertion. Do not invent missing conditions.",
 "criteria":{"equivalent":"Both memories make the same assertions, without unique additional content.","partial":"They share an assertion, and at least one also contains unique assertions or conditions.","distinct":"They share no asserted fact or rule. Opposite claims or facts about different subjects also count as distinct.","insufficient":"Missing subjects or content prevent assessing shared assertions."}},
 "compatibility":{"type":"choice","instructions":"Considering the given role, purpose, time and conditions, can both memories be maintained as valid records? Different roles or past and present states may coexist. Do not choose a memory to delete.",
 "criteria":{"compatible":"Both can be maintained, including equivalent, complementary, unrelated, different-role or different-time claims.","conflict":"Both cannot hold in the same scope and time.","insufficient":"Required role, purpose or time information is missing."}}}
records=[
 {"id":"control_en_open","request":{"state":"The door is open.","questions":simple_en},"expected":{"door":"open"}},
 {"id":"control_en_closed","request":{"state":"The door is closed.","questions":simple_en},"expected":{"door":"closed"}},
 {"id":"control_ko_open","request":{"state":"문이 열려 있다.","questions":simple_ko},"expected":{"door":"open"}},
 {"id":"control_ko_closed","request":{"state":"문이 닫혀 있다.","questions":simple_ko},"expected":{"door":"closed"}},
 {"id":"L01_en","request":{"state":{"context":"Both are candidate lessons for the same research role at the start of work.","memory_a":"At the start of work, verify your role and absolute workspace path, and specify the path in file commands.","memory_b":"First cross-check the user-designated role, absolute path, current task, and memory entry point."},"questions":english_questions},"expected":{"overlap":"partial","compatibility":"compatible"}},
 {"id":"L04_en","request":{"state":{"context":"Both rules apply to the same role and situation at the start of work.","memory_a":"At the start of work, you must verify your role and workspace path.","memory_b":"At the start of work, you must not verify your role and workspace path."},"questions":english_questions},"expected":{"overlap":"distinct","compatibility":"conflict"}}
]
(out/"inputs_with_separate_expected.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
tok,model=Checkpoint("jaredpalmer/kev-0.8b@"+base["model_revision"]).load("cpu",LoadOptions(dtype=torch.float32,backend="torch",fused=False,cuda_graphs=False))
results=[]
for r in records:
    req=r["request"];rec,meta=to_record(SystemOneRequest.model_validate(req));enc=model.encode(tok,rec,max_state=2048,max_branch=4096,strict=True)
    start=time.perf_counter()
    with torch.inference_mode():ps=model.probs(enc)
    ans={}
    for m,p in zip(meta,ps):
        dist=dict(zip(m["keys"],map(float,p.tolist())))
        ans[m["id"]]={"decision":max(dist,key=dist.get),"probabilities":dist,"expected":r["expected"][m["id"]]}
    row={"id":r["id"],"answers":ans,"elapsed_ms":(time.perf_counter()-start)*1000}
    results.append(row)
    with (out/"predictions.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    print(json.dumps(row,ensure_ascii=False),flush=True)
report={"purpose":"post-result diagnostic only; not a replacement or pooled score for the original pilot","model_revision":base["model_revision"],"results":results,
        "simple_control_agreements":sum(r["answers"]["door"]["decision"]==r["answers"]["door"]["expected"] for r in results[:4]),
        "english_memory_question_agreements":sum(a["decision"]==a["expected"] for r in results[4:] for a in r["answers"].values())}
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
