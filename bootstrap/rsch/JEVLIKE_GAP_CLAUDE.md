# jevlike 기존 구현 점검: 이미 가능한 것과 추가할 것

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 요청: 사용자 "jevlike 기존 구현을 확인해 이미 가능한 부분과 추가할 부분을 구분하여 보고"
- 대상 요구: [R06 jevlike 기반 관계 엔진](requirements/REQUIREMENTS_CODEX.md), R05 경험 축적
- 근거: `rsch_sub_memory`의 Codex 연구 보고서 8편과 실험 코드·결과, 로컬 vendored Kev 코드. 이번에 모델을 새로 실행하거나 Codex 파일을 수정하지는 않았다.

**결론: "jevlike 엔진"이라는 이름으로 바로 쓸 수 있는 구현은 로컬에도 공개 저장소에도 없다. 로컬에 실제로 있는 것은 (1) 학습된 판단 모델 Kev 0.8B를 호출하는 실험 코드, (2) 관계 그래프 선별·갱신 프로토타입, (3) 기억 사례·판정·모델 응답 원장이다. 이 셋을 합치면 "관계 후보에 점수를 매기고, 근거 버전으로 묶음을 보류·재계산하는" 뼈대는 이미 있다. 관계 엔진이 되려면 기억 저장소·관계 스키마·검토 확정·view 생성·실행기 연결이 추가로 필요하고, 그중 의미 판정의 정확도는 현재 모델·현재 질문 형식으로는 자동 병합에 쓸 수준이 아니다.**

## 1. "jevlike"가 가리키는 것

| 이름 | 실체 | 로컬 상태 |
| --- | --- | --- |
| Jev (TypeSafe) | 상업용 판단 모델·API. 형식이 정해진 질문(noul/choice/score)에 확률로 답한다 | 없음. API 개념만 참조 |
| vinnylarouge/jevlike | 연구용 출발점. 문맥 192바이트·선택지 32바이트 byte 모델을 처음부터 학습 | 없음. 고정 commit `94f5fd1`의 README·predict.py·model.py·data.py·eval.py만 읽음 |
| **Kev** (jaredpalmer/kev) | 공개 가중치 판단 모델(0.8B/4B/9B/27B). Jev 호환 요청 형식 | **있음.** `rsch_sub_memory/memory-pilot-20261014/vendor/kev` (commit `0a6d3fa`), 모델 캐시 `.cache/huggingface` (kev-0.8b v1.0) |
| open-jev, NanoJev, NLI 모델 | 비교군 | 없음 |

사용자가 염두에 둔 구현이 위 넷 중 어느 것인지는 Codex 하위 세션도 "미확인"으로 남겼다. 이번 점검은 **로컬에 실제로 있는 Kev와 실험 코드**를 기준으로 했다. 다른 구현을 뜻하셨다면 경로를 알려 주시면 다시 대조한다.

**로컬 전체 검색 결과(2026-10-17, `dev/` 전체·`.codex/skills`·`.claude/skills`, 숨김·gitignore 폴더 포함, node_modules·.venv·.git 제외):** `rsch_sub_memory` 밖에는 jevlike·open-jev·NanoJev·Kev의 clone이나 구현이 없다. `jev`/`jevlike`라는 이름의 폴더도 없다. 관련 흔적은 두 종류뿐이다.

- **AAA의 JEV-BYUL 연구 프로젝트** (`dev/AAA/projects/AAA/work/jev-byul-research/`, `subplans/SR-JEV-BYUL`, ARCP 요구 "R20 BYUL + JEV-like relation primitive / Memory Analyze Engine", `human-llm-operating-model/work/jev-byul-rsch-staging/`): 전부 문서다. 코드 없음. 그 안의 결론 한 줄은 지금도 유효하다 — "OPEN JEV-LIKE IMPLEMENTATION != JEV REPRODUCTION".
- **Hermes 설치본 안의 Jev 클라이언트 코드** (`rsch/hermes/hermes-agent/evals/compaction/jev_arm.py` 등): 호스팅된 TypeSafe `jev-latest`를 OpenRouter Decisions API로 호출하는 압축 평가용 코드다. 로컬 판단 모델이 아니다. 플러그인 카탈로그에 `jev-judge.yaml`("TypeSafe Jev as a judgment layer — a pre-tool gate") 등 외부 저장소를 가리키는 항목 13개가 있으나 로컬 복사본은 없다.

따라서 사용자가 뜻한 "jevlike 엔진"이 **기존에 만들어 둔 우리 구현**이라면 이 PC에는 없고, AAA 쪽 JEV-BYUL 연구 문서가 그 계보다. Byul(`dev/Byul`, HEAD `79c00bfe`)은 그래프·view 연구 코드이며 판단 모델은 아니다.

## 2. 이미 가능한 것 (코드와 실행 결과가 있는 범위)

### 2.1 판단 모델 호출 — Kev (vendored, 실행 검증됨)

| 기능 | 위치 | 확인 수준 |
| --- | --- | --- |
| 질문 3종: `noul`(예/아니오), `choice`(선택지별 확률·confidence), `score`(순서 척도) | `kev/api.py` `SystemOneRequest` | 코드 확인 |
| 한 문맥(state)에 여러 질문을 한 번에 묻기 | `to_record()` → `model.encode()` → `model.probs()` | **실행됨.** 18쌍 × 2문항 등 총 300여 회 CPU 추론 |
| 입력 길이 초과를 오류로 거부(`strict=True`, `ContextOverflow`) | `kev/model.py`, `predictors.py` | **실행됨.** 절단 0건, 의도적 초과 거부 확인 |
| 선택지 순서 바꿔 재실행·분산 측정 | `serve.py /v1/systemone/permute`, `predictors.RotationAveraged` | 코드 확인. 실험은 자체 스크립트로 순환·역순 등 13개 배치 실행 |
| 로컬 HTTP 서버(`/v1/systemone`, `/v1/models`) | `kev/serve.py` (FastAPI, 127.0.0.1:8008) | 코드 확인. 실행 안 함 |
| 날짜 산술 전처리(`date_facts`) | `kev/api.py` | 코드 확인 |
| 확률 보정·학습·벤치마크 | `calibrate.py`, `train.py`, `benchmark.py`, `suite.py` | 코드 있음. 우리 데이터로 실행 안 함 |
| 고정 재현: 모델 revision, base revision, temperature, head sha256 기록 | `run_pilot.py` → `runs/*/run.json` | **실행됨** |

주의: `option_isolation` 경로는 현재 Qwen3.5 hybrid 체크포인트에서 거부된다(Codex 기록). 순서 민감도 완화를 스위치 하나로 켤 수는 없다.

### 2.2 관계 그래프 선별·갱신 프로토타입 (실행 검증됨, LLM 없음)

`rsch_sub_memory/graph-pilot-20261014/study.py` (표준 라이브러리 + SQLite 인메모리).

| 기능 | 확인 결과 |
| --- | --- |
| 원자료 발췌에 경로·행 범위·파일 해시·발췌 해시 연결 | 12개 항목, 7개 파일 |
| 업무별 선정 관계(`SELECTS`/`INCLUDES`)로 필요한 기억만 조회 | 전체 전달 대비 항목 70%·바이트 71.4% 감소. 목록·Python 그래프·SQLite 재귀 CTE가 같은 결과 |
| 원자료 변경 → 역방향 의존 탐색으로 영향받는 view 특정 | 6개 view 중 2개 특정 |
| 사용 직전 버전 대조로 오래된 묶음 보류(READY/BLOCKED) | 알림 유실·버전만 바꾼 재생성·삭제·그룹 변경 사례에서 보류 동작 |
| 19개 구조 검사 통과 | 의미 정확도 아님 |

한계도 실측됐다. 관계 하나를 빼면 필요한 항목이 빠지는데도 READY가 나온다. **최신성 검사와 의미적 충분성은 다른 조건**이며, 관계가 틀리면 그래프도 틀린 결과를 전달한다.

### 2.3 데이터 원장과 수집 도구

| 자료 | 내용 |
| --- | --- |
| `collection/cases.jsonl` | 기억 쌍 18건(실제 3 + 통제 변형 15), 출처·해시·맥락 |
| `collection/annotations.jsonl` | 기대 판정 18건. **독립 검토된 라벨 0건** |
| `collection/observations.jsonl`, `order-observations.v1.jsonl` | 모델 응답 24 + 282건 |
| `collection/review_packets.jsonl`, `review_requests.jsonl` | 검토 요청. L01 질문은 아직 미응답 |
| `collect.py` | 중복 ID·해시 불일치·검토 표시 없는 승격을 거부하는 수집 도구 |
| `data/questions.v1.json`, `freeze.v1.json` | 질문 형식·고정 조건 |

### 2.4 요구 정교화(M01–M06)와 설계 문서

[R05_R06_REFINEMENT_CODEX.md](rsch_sub_memory/R05_R06_REFINEMENT_CODEX.md)에 확인 주체·시점·실패 처리가 표로 정리돼 있다. 구현 전이지만 **무엇을 만들어야 하는지는 이미 적혀 있다.** 이번 보고의 §4 항목은 이 표와 대응한다.

## 3. 측정된 성능 — 현재 상태로는 자동 병합 불가

| 항목 | Kev 0.8B (CPU fp32) | 규칙(명시 정보만) |
| --- | --- | --- |
| 기대 제안과 일치 | 17/36 | 결정한 16/16 (20건 보류) |
| 겹침 구별 / 양립 구별 | 5/18, 12/18 | — |
| 최대 p_max | 0.714 (사전 기준 0.8 미달 36/36) | — |
| 선택지 역순 시 답 변화 | 3/12 → 전수 시험에서 겹침 10/18, 양립 5/18 | 해당 없음 |
| 기억 A/B 표시 순서 바꿈 | 8/36 변화. 의무/금지 충돌(L04)이 "양립"으로 뒤집힘 | — |
| 재검토 분류 용도(양립이면 유지 후보) | 제안 대비 15/18 일치, 검토 누락 0. 단 규칙만으로도 같은 5쌍 보존 → **모델의 추가 효과 0** | — |
| 지연 | 쌍당 중앙값 1.5~3.0초, 첫 로딩 98초 | 즉시 |

이 수치는 **연구자 제안 라벨 기준**이다. 정답이 검증된 적이 없으므로 정확도라고 부를 수 없다. 다만 방향은 분명하다. 부분 중복을 완전 중복으로, 다른 역할의 기억을 같은 것으로 분류하는 오류가 있고, 선택지와 표시 순서에 따라 판정이 흔들린다. 현재 질문 형식(4범주 강제 선택 + 3범주 강제 선택)도 사례 1 같은 "일부 겹치고 일부 보완"을 표현하지 못한다.

## 4. 추가해야 하는 것

번호는 우선순위가 아니라 흐름 순서다. ★는 "이게 없으면 관계 엔진이라 부를 수 없는" 항목.

| # | 추가 항목 | 지금 없는 이유 / 근거 | 대응 요구 |
| --- | --- | --- | --- |
| A1 ★ | **기억 저장소와 스키마**: 기억 ID·버전·본문, 역할·업무·시점 조건, 원자료 개정 연결, 확인 수준 | 프로토타입은 인메모리·실행마다 재구성. 영속 저장소 없음. Git/SQLite/그래프 DB 미선정 | M01, M05 |
| A2 ★ | **관계 스키마와 다중 관계 표현**: 동일/부분중복/보완/충돌/대체/보류를 하나의 강제 선택이 아니라 분해된 질문(같은 대상? 조건 겹침? 공통 주장? 양립? 정보 부족?)으로 | 현재 질문 v1은 강제 4+3 범주. 사례 1 표현 불가 | M02 |
| A3 ★ | **후보 생성 단계**: 어떤 기억 쌍을 비교할지 검색·명시 관계로 좁히기. 전체 쌍 비교 불가 | 프로토타입은 비교할 쌍을 손으로 지정 | M03 |
| A4 | **코드 판정 선행**: ID·버전·역할·시점처럼 명시된 값은 모델 전에 규칙으로 처리하고 보류 가능 | `rules()`가 run_pilot.py 안에 실험용으로만 있음 | M02 |
| A5 | **입력 보존 검사**: 역할·조건이 잘리지 않았는지, 정답 후보가 선택지에 있는지, 순서 고정과 기록 | strict 절단 거부는 있음. 조건 보존·후보 누락 검사는 없음 | M03 |
| A6 | **순서 민감도 처리**: 기본 정렬을 재현 가능하게 기록, 순서 불일치를 검토 신호로 수집(개선 수단이 아니라 신호로) | permute/rotation 코드는 있으나 집계가 개선을 주지 못함(17→15/36) | M03 |
| A7 ★ | **판정 ↔ 확정 변경 분리**: 모델 점수로 병합·삭제·대체·확인 수준 승격을 하지 않는 검토 정책과 권한 확인 | 미구현. 검토 주체·자동 확정 범위 미정 | M04 |
| A8 ★ | **역할별 경험 view 생성**: 선택된 기억 ID·버전·조건·검토 상태에서 MD를 생성하고 manifest로 추적 | 프로토타입은 전달 묶음까지. MD 생성·view 수정의 원본 반영 없음 | M05, R05 |
| A9 | **실행기 연결**: 전달 직전 버전 대조 → 실행기 접점(CLAUDE.md/SessionStart/`--settings`, Codex `developerInstructions`/SessionStart, Pi `before_agent_start`)으로 주입. 실패 시 보류 | 프로토타입 serve()는 READY/BLOCKED만 반환. 실제 차단은 별도 보고서([claude-entry-research](agent_runtime_lifecycle_control/claude-entry-research/FINDINGS.ko.md), [codex-entry-research](agent_runtime_lifecycle_control/codex-entry-research/FINDINGS.ko.md)) 참고 | R02, R04 |
| A10 | **한국어 평가 묶음과 독립 검토**: 원문 가족 단위 분할, 검토된 라벨, 허용 오류율 기준 | 라벨 0건. 3개 원문 가족뿐 | M06 |
| A11 | **모델 비교 기준선**: 같은 사례로 규칙 / NLI / 일반 LLM(짧은 구조화 출력) / Kev 4B / Kev 0.8B 비교 | 0.8B만 실행. GPU(RTX 3050 Ti 4GB) 미사용 | M06 |
| A12 | **효과 지표**: 다음 업무에서 재설명·재탐색·재작업·사용자 정정이 줄었는지 연결 | 없음 | M06, R05 |

## 5. 판단과 제안

1. **"jevlike 기반 관계 엔진"은 모델이 아니라 저장소+스키마+검토 흐름이 본체다.** 모델(Kev)은 그중 A2/A3의 후보 점수화 한 칸을 맡는다. 지금 자료로는 그 한 칸조차 규칙보다 나은 효과가 입증되지 않았다. 따라서 **A1·A2·A7·A8부터 코드로 세우고, 모델 자리는 처음에 규칙+보류로 채운 뒤 교체 가능하게 두는 순서**를 권한다.
2. Kev를 유지한다면 0.8B 결과로 기각하지 말고, A10 라벨을 먼저 만든 뒤 4B(GPU)와 일반 LLM을 같은 사례로 비교한다. 순서 불일치는 "개선 수단"이 아니라 "검토 신호"로만 쓴다.
3. vinnylarouge/jevlike(처음부터 학습)는 라벨이 수백 건 이상 쌓이고 앞의 비교가 끝난 뒤에나 의미가 있다. 지금 단계의 후보에서 제외해도 된다.
4. 그래프 저장소는 아직 필요 없다. 현재 규모에서는 목록·SQLite가 같은 결과를 냈다. 관계 종류가 분명하고 버전 manifest가 있는 작은 계층부터 시작한다.

## 6. 미확인·보류

- 사용자가 뜻한 jevlike가 위 후보 중 무엇인지(로컬 검색 완료 — §1 참고. 우리 구현은 없음). AAA JEV-BYUL 연구 문서와 ARCP R20 요구를 이번 R06과 대조하는 작업은 하지 않았다.
- Hermes 플러그인 카탈로그의 "Jev를 도구 전 관문으로 쓰는" 외부 플러그인(`jev-judge`)은 [runtime-intervention-research](agent_runtime_lifecycle_control/runtime-intervention-research/FINDINGS.ko.md)의 관문 설계와 같은 발상이다. 외부 저장소만 확인했고 코드는 읽지 않았다.
- L01 검토 질문 응답(미응답). 검토된 라벨이 생겨야 §3 수치가 정확도로 바뀐다.
- Kev 4B·9B의 한국어 성능, GPU 실행, 일반 LLM 기준선.
- 검토 주체·자동 확정 범위·삭제 정책(요구사항 미결정 항목).

## 7. 근거 파일

- 연구 보고: `rsch_sub_memory/JEVLIKE_MEMORY_UTILITY_CODEX.md`, `MEMORY_PILOT_RESULTS_CODEX.md`, `ORDER_SENSITIVITY_RESULTS_CODEX.md`, `REVIEW_TRIAGE_STUDY_CODEX.md`, `GRAPH_IMPLEMENTATION_STUDY_CODEX.md`, `R05_R06_REFINEMENT_CODEX.md`, `RELATION_CASES_CODEX.md`, `EXTERNAL_MEMORY_SURVEY_CODEX.md`
- 코드: `rsch_sub_memory/memory-pilot-20261014/{run_pilot.py, run_order_study.py, analyze_review_triage.py, collect.py, vendor/kev}`, `rsch_sub_memory/graph-pilot-20261014/study.py`
- 고정 버전: Kev 코드 `0a6d3fafeee7f3f76a9a4a522bf8b9d5b50bd7e5`, 모델 `jaredpalmer/kev-0.8b@bf75a6a8…`, base `Qwen/Qwen3.5-0.8B-Base@dc7cdfe2…`, jevlike `94f5fd1b…`, Byul `79c00bfe…`
