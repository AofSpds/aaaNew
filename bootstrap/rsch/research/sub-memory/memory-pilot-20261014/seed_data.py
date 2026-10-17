from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent
def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(b): return hashlib.sha256(b).hexdigest()
def digest(obj): return sha(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
source_defs={
 "lesson_a":("Agent_memory/LESSONS_CODEX.md","첫 작업에서 역할과 절대 작업대 경로를 확인하고, 파일 명령에 명시한다."),
 "lesson_b":("Agent_memory/LESSONS_CODEX.md","사용자 지정 역할·절대 경로·현재 과제·메모 진입점을 먼저 대조한다."),
 "parent_dir":("Agent_memory/README.md",r"작업대: C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch."),
 "child_dir":("rsch_sub_memory/INTAKE_CODEX.md",r"C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\rsch_sub_memory"),
 "before":("rsch_sub_memory/INTAKE_CODEX.md","실제 jevlike 구현 조사는 아직 시작하지 않았다."),
 "after":("rsch_sub_memory/R05_R06_REFINEMENT_CODEX.md","README와 핵심 텍스트 코드를 읽었다."),
}
sources={}
for key,(relative,excerpt) in source_defs.items():
    p=BASE/relative
    raw=p.read_bytes(); text=raw.decode("utf-8-sig")
    pos=text.index(excerpt)
    sources[key]={"path":str(p),"sha256":sha(raw),"excerpt":excerpt,"start_line":text[:pos].count("\n")+1,
                  "excerpt_sha256":sha(excerpt.encode())}
dump(ROOT/"data"/"sources.initial.json",sources)
questions={
 "overlap":{"type":"choice","instructions":"조건과 적용 대상을 포함해 기억 A와 B가 같은 구체적 주장·규칙을 담는지 판단한다. 같은 주제를 다룬다는 것만으로 겹친다고 하지 않는다. 부족한 조건을 추측하지 않는다.",
 "criteria":{"equivalent":"두 기억의 주장이 실질적으로 같고 고유한 추가 내용이 없다.","partial":"공통으로 주장하는 내용이 있고, 적어도 한쪽에만 있는 조건이나 내용도 있다.","distinct":"공통으로 주장하는 구체적 내용이 없다. 반대 주장이나 다른 대상의 사실도 여기에 포함한다.","insufficient":"대상이나 내용이 빠져 겹침 여부를 판단할 수 없다."}},
 "compatibility":{"type":"choice","instructions":"주어진 역할·용도·시점·조건을 고려할 때 기억 A와 B가 동시에 올바른 기록으로 유지될 수 있는가? 서로 다른 역할 또는 과거와 현재의 상태는 함께 유지될 수 있다. 충돌 해소나 삭제 승자를 선택하지 않는다.",
 "criteria":{"compatible":"둘을 함께 유지할 수 있다. 같은 주장, 보완, 무관, 역할 차이, 시점 차이도 포함한다.","conflict":"동일 적용 범위와 시점에서 두 주장이 양립할 수 없다.","insufficient":"역할·용도·시점 등 필요한 조건이 부족해 양립 여부를 판단할 수 없다."}}
}
dump(ROOT/"data"/"questions.v1.json",questions)
cases=[]; anns=[]
def add(cid,group,origin,a,b,context,labels,reason,refs,facts=None,change=None):
    inp={"context":context,"memory_a":a,"memory_b":b}
    if facts: inp["structured_facts"]=facts
    row={"schema_version":1,"case_id":cid,"group_id":group,"origin":origin,"created_at":now,
         "source_refs":[{"key":k,**sources[k]} for k in refs],"transformation":change,
         "input":inp,"input_sha256":digest(inp),"split":"exploratory"}
    cases.append(row)
    anns.append({"annotation_id":cid+"-proposal-1","case_id":cid,"input_sha256":row["input_sha256"],
                 "status":"proposed","author":"Codex research draft","independent_review":False,
                 "created_at":now,"labels":dict(zip(questions,labels)),"rationale":reason,"supersedes":None})
def fact(role,purpose,value,period="current",slot="workdir"):
    return {"role":role,"purpose":purpose,"slot":slot,"value":value,"period":period,"exclusive":True}
observed="observed_source_pair"; variant="controlled_variant"
L=["lesson_a","lesson_b"]; P=["parent_dir","child_dir"]; S=["before","after"]
la=sources["lesson_a"]["excerpt"]; lb=sources["lesson_b"]["excerpt"]
lc="A와 B는 같은 연구 역할이 업무를 시작할 때 적용하는 교훈 후보다."
add("L01","lessons",observed,la,lb,lc,("partial","compatible"),"역할·경로 확인은 공통이며 파일 명령 명시와 과제·메모 확인은 고유하다.",L)
add("L02","lessons",variant,la,la,lc,("equivalent","compatible"),"완전히 같은 기억을 복제했다.",L,change="B를 A의 정확한 복사로 변경")
add("L03","lessons",variant,"업무를 시작할 때 담당 역할과 절대 작업 경로를 확인한다.","작업 시작 전 맡은 역할 및 작업 폴더의 절대 경로를 점검한다.",lc,("equivalent","compatible"),"동일한 조건과 의무의 표현만 바꿨다.",L,change="공통 주장만 추출해 동의 표현으로 재작성")
add("L04","lessons",variant,"업무 시작 시 역할과 작업대 경로를 반드시 확인한다.","업무 시작 시 역할과 작업대 경로를 확인해서는 안 된다.",lc,("distinct","conflict"),"동일 상황의 의무와 금지가 반대다.",L,change="반대 규칙을 만든 충돌 대조군")
add("L05","lessons",variant,"업무 시작 시 역할과 작업대 경로를 확인한다.","조사 완료 통보를 받으면 결과 파일의 위치를 기록한다.",lc,("distinct","compatible"),"대상 행위가 다르며 함께 지킬 수 있다.",L,change="B를 다른 교훈으로 교체")
add("L06","lessons",variant,"업무 시작 시 역할과 작업대 경로를 확인한다.","그때 그것을 대조한다.","B의 '그때'와 '그것'을 가리키는 앞 문장은 제공되지 않았다.",("insufficient","insufficient"),"생략된 대상을 추측하지 않는다.",L,change="B의 적용 조건과 대상을 삭제")
pdir=r"C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch"; cdir=pdir+r"\rsch_sub_memory"
add("P01","paths",observed,"부모 rsch의 연구 작업대는 "+pdir+"다.","자식 rsch_sub_memory의 연구 작업대는 "+cdir+"다.","A와 B는 서로 다른 역할의 현재 연구 산출물 작업대를 지정한다.",("distinct","compatible"),"적용 역할이 달라 각 경로를 유지한다.",P,{"a":fact("rsch","output",pdir),"b":fact("rsch_sub_memory","output",cdir)},change="원문 역할을 붙여 두 경로를 문장으로 구성")
add("P02","paths",variant,"rsch_sub_memory의 현재 유일한 연구 산출물 폴더는 D:/research/A다.","rsch_sub_memory의 현재 유일한 연구 산출물 폴더는 D:/research/B다.","두 지시는 같은 기간에 동시에 적용된다. 변경·취소 지시는 없다.",("distinct","conflict"),"같은 역할·용도·기간의 유일한 값이 다르다.",P,{"a":fact("rsch_sub_memory","output","D:/research/A"),"b":fact("rsch_sub_memory","output","D:/research/B")},change="같은 범위의 서로 다른 유일 경로로 변경")
add("P03","paths",variant,"현재 유일한 작업대는 D:/research/A다.","현재 유일한 작업대는 D:/research/B다.","각 경로가 어느 역할·용도에 적용되는지 정보가 빠져 있다.",("distinct","insufficient"),"값은 다르지만 같은 범위인지 알 수 없다.",P,{"a":fact(None,None,"D:/research/A"),"b":fact(None,None,"D:/research/B")},change="P02에서 역할·용도 제거")
add("P04","paths",variant,"기억 연구의 산출물은 D:/research/A에 둔다.","기억 연구 결과의 저장 폴더는 D:/research/A다.","둘 다 rsch_sub_memory의 현재 연구 산출물 폴더를 지정한다.",("equivalent","compatible"),"같은 역할·용도·기간·경로다.",P,{"a":fact("rsch_sub_memory","output","D:/research/A"),"b":fact("rsch_sub_memory","output","D:/research/A")},change="동일한 위치를 다르게 표현")
add("P05","paths",variant,"rsch_sub_memory의 연구 산출물은 D:/research/output에 둔다.","rsch_sub_memory의 지속 기억은 D:/research/memory에 둔다.","같은 역할의 두 지시지만 산출물과 지속 기억의 용도가 다르다.",("distinct","compatible"),"용도가 달라 동시에 지킬 수 있다.",P,{"a":fact("rsch_sub_memory","output","D:/research/output"),"b":fact("rsch_sub_memory","memory","D:/research/memory")},change="역할은 같고 용도만 다르게 구성")
add("P06","paths",variant,"이전 단계의 유일한 작업대는 D:/research/A였다.","사용자의 변경 지시 이후 유일한 작업대는 D:/research/B다.","동일 역할과 용도다. A는 변경 전, B는 변경 후의 상태이며 과거 기록도 보존한다.",("distinct","compatible"),"서로 다른 적용 기간의 위치 변화다.",P,{"a":fact("rsch_sub_memory","output","D:/research/A","before_change"),"b":fact("rsch_sub_memory","output","D:/research/B","after_change")},change="사용자 변경 지시와 적용 기간을 추가")
add("S01","status",observed,sources["before"]["excerpt"],"공개 jevlike 후보의 README와 핵심 텍스트 코드를 읽었다.","동일 세션이다. A는 초기 인수 때의 상태이고, B는 그 이후 조사 단계의 수행 기록이다.",("distinct","compatible"),"과거 미착수와 이후 수행을 서로 다른 시점으로 보존한다.",S,{"a":fact("rsch_sub_memory","research","not_started","intake","status"),"b":fact("rsch_sub_memory","research","source_read","later","status")},change="두 원문의 대상과 선후 관계를 명시")
add("S02","status",variant,"오후 3시 기준으로 해당 구현의 문서 조사를 아직 시작하지 않았다.","같은 날 오후 3시 기준으로 해당 구현의 문서 조사를 시작했다.","동일 세션·동일 구현·동일 기준 시점의 현재 상태 주장이다.",("distinct","conflict"),"동일 시점의 착수 여부가 반대다.",S,change="시점 차이를 없애 상충 상태 생성")
add("S03","status",variant,"사용자가 Jevlike 조사를 요청했다.","이번 입력에는 실제 조사 수행 기록이 없다.","연구 지시를 수신했으나 수행 여부에 관한 추가 자료는 제공되지 않았다. 지시 수신과 수행 완료는 구분한다.",("distinct","compatible"),"요청 존재와 수행 기록 부재는 양립한다. 어느 쪽도 완료 증거가 아니다.",S,change="사용자 지시와 수행 증거 부재를 비교")
add("S04","status",variant,"현재까지 다른 세션의 완료 통보만 받았고 독립 재현은 하지 않았다.","현재까지 같은 결과를 직접 실행하여 독립 재현을 마쳤다.","같은 검토자·같은 결과·같은 기준 시점이다.",("distinct","conflict"),"독립 재현의 미수행과 완료가 양립하지 않는다.",S,change="전달과 독립 검증을 혼동하는 충돌 사례")
add("S05","status",variant,"해당 구현의 문서 조사를 아직 시작하지 않았다.","해당 구현의 문서 조사를 시작했다.","동일 세션과 구현이다. 두 기록의 작성 순서와 적용 시점은 알려져 있지 않다.",("distinct","insufficient"),"상태 변화일 수도 동일 시점 충돌일 수도 있다.",S,change="선후 관계와 기준 시점 제거")
add("S06","status",variant,"해당 구현에 대한 문서 조사를 시작했다.","해당 구현의 문서 조사에 착수했다.","동일 세션·동일 구현·동일 기준 시점의 현재 상태다.",("equivalent","compatible"),"같은 상태를 다른 표현으로 기록했다.",S,change="동일 상태를 동의 표현으로 변경")
for path,rows in [(ROOT/"data"/"cases.jsonl",cases),(ROOT/"data"/"annotations.jsonl",anns)]:
    with path.open("x",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row,ensure_ascii=False)+"\n")
freeze={"created_at":now,"dataset_sha256":sha((ROOT/"data"/"cases.jsonl").read_bytes()),
        "annotations_sha256":sha((ROOT/"data"/"annotations.jsonl").read_bytes()),
        "questions_sha256":sha((ROOT/"data"/"questions.v1.json").read_bytes()),
        "case_count":len(cases),"groups":sorted({r["group_id"] for r in cases}),
        "observed_source_pairs":sum(r["origin"]==observed for r in cases),"controlled_variants":sum(r["origin"]==variant for r in cases),
        "label_status":"proposed; no independent review; never provided to predictor",
        "split_policy":"exploratory only; future train/validation/test must keep source families together",
        "permutation_cases":["L01","L04","P01","P03","S01","S04"],
        "diagnostic_probability_threshold":0.8,"training_performed":False}
dump(ROOT/"data"/"freeze.v1.json",freeze)
print(json.dumps(freeze,ensure_ascii=False,indent=2))
