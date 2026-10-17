from pathlib import Path
import json,hashlib,sys,statistics
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"runs"/"order_study_v1"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def lines(p):return [json.loads(s) for s in p.read_text(encoding="utf-8").splitlines() if s]
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(",",":"),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
run=read(OUT/"run.json");report=read(OUT/"report.json");plans=read(OUT/"plan.json")
requests={x["request_id"]:x for x in lines(OUT/"requests.jsonl")}
pred={x["request_id"]:x for x in lines(OUT/"predictions.jsonl")}
cases={x["case_id"]:x for x in lines(OUT/"cases.jsonl")}
ann={x["case_id"]:x for x in lines(OUT/"annotations.jsonl")}
questions=read(OUT/"questions.v1.json")
table={(p["case_id"],p["question_id"],p["method"]):pred[p["request_id"]] for p in plans}
sensitivity=read(OUT/"sensitivity.json");ensembles=read(OUT/"ensembles.json")
triage=read(ROOT/"review-triage-analysis-v1"/"report.json")
checks={
"run_completed":run["status"]=="completed",
"unique_requests_and_predictions":len(requests)==len(pred)==282 and set(requests)==set(pred),
"method_assignments_complete":len(plans)==384 and all(p["request_id"] in pred for p in plans),
"frozen_data_exact":all((OUT/f).read_bytes()==(ROOT/"data"/f).read_bytes() for f in ["cases.jsonl","annotations.jsonl","questions.v1.json"]),
"rendered_order_hashes_match":all(sha(dump(r["rendered_input"]).encode())==r["rendered_sha256"]==pred[k]["rendered_sha256"] for k,r in requests.items()),
"state_semantics_unchanged":all(r["request"]["state"]==cases[r["case_id"]]["input"] for r in requests.values()),
"no_reference_fields_in_requests":all(set(r["request"])=={"state","questions"} and r["request"]["questions"]=={r["question_id"]:questions[r["question_id"]]} for r in requests.values()),
"candidate_order_matches_rendered_request":all(list(r["request"]["questions"][r["question_id"]]["criteria"])==r["option_order"]==pred[k]["option_order"] for k,r in requests.items()),
"candidate_membership_unchanged":all(set(r["option_order"])==set(questions[r["question_id"]]["criteria"]) and len(r["option_order"])==len(set(r["option_order"])) for r in requests.values()),
"source_files_unchanged":all(sha(Path(p).read_bytes())==h for p,h in run["source_hashes_before"].items()),
"no_input_truncation":all(not p["truncated"] for p in pred.values()),
"same_input_repeat_exact":all(table[(cid,q,"repeat_original")]["probabilities"]==table[(cid,q,"original")]["probabilities"] for cid in ["L01","P04","S04"] for q in questions),
"reference_labels_still_unreviewed":all(a["status"]=="proposed" and not a["independent_review"] for a in ann.values()),
}
assert all(checks.values()),checks
method_details={}
for method in dict.fromkeys(p["method"] for p in plans):
    pp=[p for p in plans if p["method"]==method]
    mm=[m for m in report["methods"] if m["method"]==method]
    method_details[method]={
        "n_questions":len(pp),
        "actual_option_order_changes":sum(p["option_order"]!=table[(p["case_id"],p["question_id"],"original")]["option_order"] for p in pp),
        "decision_flips":sum(m["flips_from_original"] for m in mm),
        "proposal_agreements":sum(m["agreements_with_proposal"] for m in mm),
        "keep_candidates":next((m["keep_candidates"] for m in mm if m["question_id"]=="compatibility"),None),
        "missed_reference_review":next((m["missed_reference_review"] for m in mm if m["question_id"]=="compatibility"),None),
        "pmax05_keep_ids":[p["case_id"] for p in pp if p["question_id"]=="compatibility" and pred[p["request_id"]]["decision"]=="compatible" and pred[p["request_id"]]["p_max"]>=.5],
    }
option_route=set(report["review_route_unstable_cases"])
display_route={cid for cid in cases if table[(cid,"compatibility","original")]["decision"]!=table[(cid,"compatibility","memory_b_first")]["decision"]}
all_stable_keep=set(report["all_tested_orders_keep_cases"])
new_keep=all_stable_keep-set(triage["rules_mapping"]["keep_candidate_ids"])
l04={m:table[("L04","compatibility",m)] for m in ["original","memory_b_first"]}
out={
"status":"post-hoc descriptive analysis; no operating threshold adopted",
"methods":method_details,
"option_route_unstable_ids":sorted(option_route),
"display_route_unstable_ids":sorted(display_route),
"either_axis_route_unstable_ids":sorted(option_route|display_route),
"all_tested_option_orders_keep_ids":sorted(all_stable_keep),
"all_tested_option_orders_keep_beyond_rules":sorted(new_keep),
"stable_wrong_question_count":sum(s["stable_wrong"] for s in sensitivity),
"unique_option_orders_per_case_question":{q:sorted(set(s["unique_orders"] for s in sensitivity if s["question_id"]==q)) for q in questions},
"max_option_probability_span":{q:max(s["max_option_probability_range"] for s in sensitivity if s["question_id"]==q) for q in questions},
"state_token_range":[min(r["state_tokens"] for r in pred.values()),max(r["state_tokens"] for r in pred.values())],
"l04_input":cases["L04"]["input"],"l04_predictions":l04,
"checks":checks,
}
write(OUT/"analysis.posthoc.json",out)
observations=[{"observation_id":"order_study_v1:"+r["request_id"],"run_id":"order_study_v1","kind":"model_prediction_not_reference_label","request_file":"../runs/order_study_v1/requests.jsonl",**r} for r in pred.values()]
assert len({o["observation_id"] for o in observations})==282
obs_file=ROOT/"collection"/"order-observations.v1.jsonl"
obs_content="".join(dump(x)+"\n" for x in observations)
if obs_file.exists():assert obs_file.read_text(encoding="utf-8")==obs_content
else:obs_file.write_text(obs_content,encoding="utf-8")
assert len(lines(obs_file))==282
write(OUT/"verification.json",{"checks":checks,"observations":282,"independent_new_cases":0,"independently_reviewed_labels":0})
names={"original":"원래 순서","reverse":"역순","key_asc":"범주 ID 오름차순","description_length_asc":"설명 문자 수 오름차순","random_11":"무작위 seed 11","random_29":"무작위 seed 29","prior_score_desc":"이전 점수 내림차순","cycle_1":"순환 +1","cycle_2":"순환 +2","cycle_3":"순환 +3 (겹침만)","memory_b_first":"기억 B 먼저 표시","repeat_original":"같은 입력 반복 (3쌍)"}
rows="\n".join(f"| {names[m]} | {d['decision_flips']}/{d['n_questions']} | {d['proposal_agreements']}/{d['n_questions']} | {d['keep_candidates'] if d['keep_candidates'] is not None else '—'} | {d['missed_reference_review'] if d['missed_reference_review'] is not None else '—'} |" for m,d in method_details.items())
text=f"""# 기억 관계 판정: 정렬·표시 순서 민감도 실제 시험

작성: 2026-10-14 KST. 실행 상태: completed. 외부 연구: [ORDER_SENSITIVITY_SURVEY_CODEX.md](ORDER_SENSITIVITY_SURVEY_CODEX.md).

## 판정

순서 영향이 실제 관찰됐다. 선택지 배치들 중 판정이 한 번이라도 바뀐 문항은 겹침 10/18(55.6%), 양립 5/18(27.8%)다. 양립의 5쌍은 모두 “함께 보존 후보/추가 검토” 경로도 바뀌었다. 반면 같은 입력을 재실행한 6개 문항은 확률까지 같았다. 현재 조건의 순서 변화 효과를 단순 실행 흔들림과 구별할 근거다.

현재 판정 모델과 자료에서 좋은 정렬법을 확정하지 않았다. 순환 배치 확률 평균의 제안 일치는 원순 17/36에서 15/36으로 낮아졌다. 여러 배치 내내 제안과 다른 문항도 10/36개다. 순서 불일치는 검토 신호 후보지만 순서 일치는 정답 보장이 아니다.

## 범위·고정 조건

- 기존 실제 기록 3쌍과 통제 변형 15쌍, 3개 원문 가족이다. 독립 검토 완료 라벨은 0건이다.
- 겹침 4범주, 양립 3범주를 별도 요청으로 판정했다. 모든 “일치/검토 누락” 수치는 아직 검토되지 않은 제안 라벨 기준이다.
- 384개 방법 할당에서 같은 렌더링 입력을 합쳐 282개 실제 추론을 실행했다. 반복 통제 6개는 별도 재실행했다. 282개를 독립 사례 282개로 세지 않는다.
- 선택지 ID·설명·기억 내용은 유지했다. B 먼저 표시는 JSON 필드의 표시 위치만 바꾸며 A/B의 값·이름·역할·시점은 바꾸지 않았다.
- 선택지 고유 배치는 사례별 겹침 7–9/24개, 양립 4–6/6개다. 전체 순열을 모든 사례에서 탐색한 결과가 아니다.
- 순환 배치는 모든 후보를 모든 위치에 한 번씩 둔다. 겹침 4회, 양립 3회 추론이며 K! 전체 순열 평균과 다르다.
- 이전 점수순은 첫 v1 모델 응답의 점수만 이용했다. 정답 제안을 사용하지 않았으나 선행 추론 비용이 필요하다.
- 이번 방법은 실행 전 계획 파일에 고정했지만 v1 결과를 이미 본 후의 탐색 연구다. 독립 시험셋이 없고 최적 정렬 선택의 일반화 주장을 할 수 없다.
- 상태 길이는 48–205토큰, 엄격 길이 제한을 적용했고 입력 절단은 없었다. 긴 문맥·예시 순서·선택지와 기억 배치의 교차 조합은 미시험이다.

“보존 후보”는 두 기억을 수정 없이 보관할 때 양립 추가 검토를 줄일 수 있는지 연구하기 위한 임시 분류다. 진실성, 최신성, 역할별 사용, 병합, 삭제, 대체 검토의 생략을 뜻하지 않는다.

## 정렬별 결과

답 변경과 제안 일치는 두 질문 총 36판정 기준이다. 보존 후보와 누락은 양립 질문 18쌍 기준이다.

| 방법 | 원순 대비 답 변경 | 제안 일치 | 보존 후보 | 제안상 검토 필요 누락 |
|---|---:|---:|---:|---:|
{rows}
| 순환 배치 확률 평균 | 4/36 | 15/36 | 6 | 0 |

범주 ID 정렬은 양립 질문에서 원래 순서와 같으므로 그 부분의 변화 0을 강건성 근거로 쓰면 안 된다. 무작위 seed 11/29도 원순과 겹치는 배치가 있어 실제 선택지 배열이 바뀐 문항은 각각 35/36, 31/36이다. 이전 점수순은 36/36개 배열이 모두 바뀌었다.

순환 다수결의 제안 일치도 겹침 5/18, 양립 10/18이었다. 겹침 1건은 동률로 보류했다. 순환 평균/다수결이 이 자료에서 개선됐다는 증거는 없다.

## 검토 생략 분류에 직접 관련된 사례

L04는 같은 역할·같은 업무 시작 상황에서 다음 두 교훈이다.

- A: “업무 시작 시 역할과 작업대 경로를 반드시 확인한다.”
- B: “업무 시작 시 역할과 작업대 경로를 확인해서는 안 된다.”

원래 표시는 충돌 0.3823, 양립 0.3326으로 충돌을 골랐다. B 먼저 표시하면 양립 0.3710, 충돌 0.3177로 양립을 골랐다. 제안 라벨은 충돌이며 독립 검토 전이다. 직접 반대되는 의무/금지 예시에서 표시 위치만으로 검토 경로가 바뀌므로 이전 시험의 “검토 필요 누락 0”을 일반 보장으로 유지할 수 없다. 이 판단을 제품에 적용하지 않았다.

선택지 배치에서 검토 경로가 바뀐 사례는 L01/L02/L03/P06/S03, 기억 표시 위치에서는 L02/L04/L05다. 어느 축이든 바뀐 사례는 합쳐 7/18개다. 두 축을 동시에 변경한 조합은 평가하지 않았다.

모든 시험 선택지 배치에서 양립을 유지한 4쌍(P01/P04/P05/S01)은 모두 기존 규칙으로도 보존 후보였다. 이 작은 자료에서 순서 검사를 추가해 얻은 새로운 규칙 외 보존 사례는 0개다. 범위 밖 실제 업무의 검토 절감 효과는 아직 없다.

## 점수가 같은가와 최상위 답이 같은가는 다르다

이전 점수 내림차순은 답 변경 0/36이지만 선택지 확률은 달랐다. 앞선 사후 분석의 p_max≥0.5 조건을 동일하게 적용하면 보존 후보는 원순 5쌍에서 점수순 4쌍으로 줄었다(S01 제외). 역순은 1쌍, 설명 길이순은 2쌍이다. 0.5는 검증된 운영 기준이 아니며 이 결과는 순서가 임계값 기반 분류에도 영향을 준다는 관찰이다.

시험 선택지 배치에서 한 범주의 확률 최대-최소 차이는 겹침 약 0.1404, 양립 약 0.1434였다. 확률은 분포 점수이며 그대로 실제 정답 확률로 해석하지 않는다. 처음 판정을 앞세우는 점수순이 원래 오판을 유지할 가능성도 있으므로 답 변화가 작다는 이유만으로 우수 정렬이라 선정하지 않는다.

모든 선택지 배치에서 제안과 다르게 유지된 문항은 겹침 5개, 양립 5개다. 양립의 일부는 “충돌”을 “정보 부족”으로 판정해 관계 범주는 달라도 검토 경로는 유지했다. 범주 오류와 검토 누락을 구별한다.

## 비용·무결성

CPU float32, 4 threads, 캐시된 모델을 offline으로 실행했다. 추론 합계 {report['inference_seconds']:.2f}초, 문항당 중앙값 {report['single_question_median_ms']/1000:.3f}초, 모델 로드 {run['load_seconds']:.2f}초다. 순환 평균은 질문당 K회 분기 평가가 필요하며 실제 서비스 최적화·GPU·배치 처리 비용은 측정하지 않았다.

모델 jaredpalmer/kev-0.8b, revision {run['model_revision']}; 기반 Qwen/Qwen3.5-0.8B-Base revision {run['base_revision']}; 코드 {run['source_commit']}. torch {run['torch']}, transformers {run['transformers']}, peft {run['peft']}, temperature {run['temperature']}.

- 기존 두 질문 묶음과 이번 단일 질문 원순의 답 변경은 0/36, 최대 확률 차이는 3.28e-7이었다. 이 차이는 순서 효과 수치보다 훨씬 작다.
- 완료 요청 수, 고정 자료, 입력 의미/선택지 집합 유지, 제안 라벨 제외, 순서를 보존한 렌더링 해시, 원문 불변, 절단 없음, 동일 입력 반복을 확인했다.
- 이전 실행의 키 정렬 JSON 해시는 순서 차이를 단독 구별하지 못하므로 이번에는 실제 렌더링된 상태·지시·선택지 배열의 순서 보존 해시를 저장했다. 이전 원시 요청을 수정하지 않았다.
- collection/order-observations.v1.jsonl에 282개 모델 관찰을 별도 기록했다. 같은 18개 사례의 추가 응답이며 새 독립 사례나 검토 라벨로 승격하지 않았다.
- L01의 이전 사용자 검토 질문은 여전히 미응답이다. 이번 “네”를 정답 판정으로 취급하지 않았다.

## 다음 연구에 반영할 제안

기본 정렬은 재현을 위해 고정하고, 순서 변화에 따른 최상위 답·점수·검토 경로 변화를 별도 특징으로 저장한다. 필수 검토 사유나 순서 불일치를 단순 가중합으로 상쇄하지 않는 정책을 비교한다. 검토 생략은 독립된 원문 가족의 검토 결과로 필요한 검토 누락과 절감량을 함께 검증한 뒤 판단한다.

외부 연구는 여러 배치 집계의 개선 사례도 보고하지만, 우리 현재 모델에서는 평균만으로 개선되지 않았다. 현 단계에서 순서 민감도를 검토 우선순위의 신호로 수집하는 효용은 확인할 가치가 있으며, 자동 검토 생략이나 기억 수정의 충분조건은 입증되지 않았다.

## 재현 파일

- memory-pilot-20261014/run_order_study.py: 고정 입력 생성·실제 모델 실행·기본 집계.
- memory-pilot-20261014/summarize_order_study.py: 사후 정리·무결성 확인·이 보고서와 별도 관찰 원장 생성.
- runs/order_study_v1: run.json, plan.json, requests.jsonl, predictions.jsonl, report.json, sensitivity.json, ensembles.json, parity.json, analysis.posthoc.json, verification.json.
- frozen cases.jsonl, annotations.jsonl, questions.v1.json은 해당 실행 폴더에 보존.
"""
(ROOT.parent/"ORDER_SENSITIVITY_RESULTS_CODEX.md").write_text(text,encoding="utf-8")
print(json.dumps({"all_checks_pass":all(checks.values()),"checks":checks,"observations":len(observations),"either_axis_unstable":len(option_route|display_route),"new_stable_keep_beyond_rules":len(new_keep)},ensure_ascii=False))
