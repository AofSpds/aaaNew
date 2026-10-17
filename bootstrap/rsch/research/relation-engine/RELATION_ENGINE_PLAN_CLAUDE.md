# 관계 엔진 구현 계획: 저장소 → 관계 스키마 → 검토 분리 → view 생성, 모델 자리는 교체 가능하게

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 요청: 사용자 "저장소·관계 스키마·검토 분리·view 생성부터 세우고 모델 자리는 교체 가능하게 비워 두는 순서를 구현하기 위한 계획"
- 대상 요구: [R05·R06](../../requirements/REQUIREMENTS_CODEX.md), 정교화 [M01–M06](../sub-memory/R05_R06_REFINEMENT_CODEX.md)
- 입력: [JEVLIKE_GAP_CLAUDE.md](JEVLIKE_GAP_CLAUDE.md)의 A1–A12, Codex 그래프 프로토타입, JEV-BYUL 선행 연구의 기록 계약(§7)
- 성격: 구현 계획 제안. 저장 제품·검토 주체·자동 확정 범위는 아직 Owner 결정이 없으므로 §8에 결정 항목으로 분리했다. 이 문서로 구현을 시작하지 않는다.

**한 줄 요약: 네 단계를 각각 "작은 코드 + 실제 작업대 자료 하나로 검증"으로 끝내고, 모델은 `Judge` 인터페이스 뒤에 두어 규칙 → Kev → 일반 LLM 순으로 바꿔 끼울 수 있게 한다. 모델 점수는 어느 단계에서도 확정 변경을 일으키지 않는다.**

## 0. 원칙

1. **원본은 건드리지 않는다.** 작업대의 MD·코드가 원자료(source)다. 엔진은 원자료의 개정(해시)을 등록하고 발췌·관계·view를 그 위에 둔다. 원자료 수정은 사람이나 실행기가 Git으로 한다.
2. **판정과 변경을 분리한다.** 규칙·모델·사람은 "판정 기록"을 만들고, 기억 상태를 바꾸는 것은 별도 "변경 기록"뿐이다. 변경 기록은 권한·근거·대상 버전을 가진다.
3. **모든 기록은 추가 전용(append-only), 현재 상태는 투영(projection).** 되돌리기·감사·"왜 이 기억이 view에 들어갔나"를 기록에서 재구성할 수 있어야 한다.
4. **모델 자리는 인터페이스다.** `Judge.ask(state, questions) → 선택지별 점수 + 보류 사유`. 기본 구현은 규칙+보류(`RuleJudge`). Kev는 이미 있는 코드로 두 번째 구현. 일반 LLM은 세 번째.
5. **입력 포함 / 실제 준수 / 효과는 따로 센다.** view에 넣었다는 사실, 실행기 입력에 들어갔다는 증거, 다음 업무에서 재작업이 줄었다는 관측을 구분해 기록한다.

## 1. 전체 구조

```text
작업대(원자료: MD·코드, Git)
   │ 등록(해시·발췌)
   ▼
[1] 기억 저장소 ── source_rev / memory_rev / relation / selection / bundle / judgment / change
   │                                   ▲                 ▲
   │ 후보 생성 + 판정 요청              │ 판정 기록        │ 승인된 변경만
   ▼                                   │                 │
[2] 관계 스키마 ──► [5] Judge 인터페이스 ─┘      [3] 검토 큐 ─┘
   (종류·조건·탐색 규칙)   RuleJudge | KevJudge | LLMJudge     (분류·승인·거부·보류)
   │
   ▼
[4] view 생성 ── 역할·업무·선정 규칙 → MD + manifest → 전달 전 최신성 검사
   │
   ▼
실행기 접점 (CLAUDE.md @import / SessionStart / --settings …)  ← 별도 조사 결과
```

[1]~[5]는 아래 단계 번호다. 화살표는 데이터 흐름이며 모듈 경계이기도 하다.

## 2. 단계 1 — 기억 저장소

**목표:** 원자료 개정·기억 개정·관계·선정·전달 묶음·판정·변경을 한 곳에 추가 전용으로 기록하고, 현재 상태를 조회할 수 있다.

### 기록 종류 (7개)

| 기록 | 필수 필드 | 출처 |
| --- | --- | --- |
| `source_rev` | source_id, path, file_sha256, excerpt_locator(행 범위), excerpt_sha256, recorded_at, status(active/deleted) | 그래프 프로토타입 "원자료 개정" |
| `memory_rev` | memory_id, version, body, claim_type(fact/summary/lesson/preference), conditions{role, task, time, scope}, source_rev_refs[], confidence_level(candidate/reviewed/verified), supersedes?, recorded_at | "기억 개정" + M01 |
| `relation` | relation_id, from{memory_id, version}, to{memory_id, version}, kind(§3), conditions, evidence_refs[], judge_ref(판정 기록), review_state(proposed/reviewed/rejected/open), group_id, group_version | "관계" + M02 |
| `selection` | selection_id, role, task, rule_version, includes[], budget, required[] | "선정 기준" |
| `bundle` | bundle_id, selection_ref, memory_revs[], source_revs[], relation_group_versions[], view_path, manifest_sha256, state(ready/blocked), blocked_reason | "전달 묶음·manifest" + M05 |
| `judgment` | judgment_id, judge{kind: rule/model/human, ref, version}, question_set_version, input_digest, option_order[], raw_scores, decision, abstain_reason, recorded_at | Kev 실험 `observations`, JEV-BYUL `ViewJudgment` |
| `change` | change_id, kind(create/merge/supersede/retire/promote_confidence), target{memory_id, version}, basis{judgment_refs, instruction_ref}, authority(사람/규칙 ID), recorded_at | M04, JEV-BYUL `ArbiterDecision`과 "authority ≠ judgment" 경계 |

공통 봉투: `record_id, record_type, schema_version, recorded_at, content_digest, causal_parent_ids[]`. JEV-BYUL R8 봉투에서 필요한 것만 가져온다(§7).

### 저장 형식 (기본값 제안, 결정 항목 D1)

- 기록: `memory-store/records/*.jsonl` 추가 전용 (종류별 파일). Git으로 이력 관리.
- 투영: `memory-store/index.sqlite` — jsonl에서 재구성 가능해야 한다(재구성 스크립트가 수용 기준).
- 이유: 프로토타입에서 SQLite 재귀 CTE로 충분했고, 그래프 DB 채택 근거가 없다. jsonl은 사람이 diff로 볼 수 있다.

### 산출물·수용 기준

- `store.py`: append / project / rebuild_index / verify(해시 재검사).
- 실제 작업대 자료로 검증: `rsch/requirements/REQUIREMENTS_CODEX.md`, `memory/codex-rsch/README.md`, `LESSONS_CODEX.md`에서 발췌 12개 등록(프로토타입 dataset 재사용).
- 수용: (a) jsonl 삭제 후 index 재구성이 동일, (b) 원자료 1줄 변경 시 해당 source_rev만 stale, (c) 모든 기록이 content_digest로 변조 검출.

## 3. 단계 2 — 관계 스키마

**목표:** 관계 종류와 각 종류의 탐색·합성 규칙을 코드로 고정하고, 후보 관계를 "분해된 질문"으로 표현한다.

### 관계 종류 (초안, 결정 항목 D2)

| kind | 의미 | 탐색에 사용 | 자동 생성 가능 |
| --- | --- | --- | --- |
| `SELECTS` / `INCLUDES` | 업무·그룹이 기억을 고름 | view 선별 | 규칙(선정 규칙) |
| `DERIVED_FROM` | 기억이 원자료 발췌에서 나옴 | 변경 영향(역방향) | 등록 시 자동 |
| `DEPENDS_ON` | view/묶음이 기억·관계 그룹에 의존 | 변경 영향 | 생성 시 자동 |
| `SUPPORTS` | 근거 관계 | 설명 | 판정 필요 |
| `OVERLAPS{shared, unique_a, unique_b}` | 부분 중복 + 보완 (동시 성립) | 중복 후보 제시 | 판정 필요 |
| `CONFLICTS_WITH{scope}` | 같은 조건에서 양립 불가 | 우선 검토 | 판정 필요 |
| `SUPERSEDES` | 새 기억이 옛 기억을 대체 | 현재 상태 투영 | **변경 기록으로만** |
| `SIMILAR_TO` | 의미 유사 후보 | 후보 생성에만 | 검색/모델 |
| `MENTIONS` | 단순 언급 | 사용 안 함 | 등록 시 |

Byul 97의 원칙을 코드로: **관계 종류마다 합성 규칙이 다르다.** `DERIVED_FROM`·`DEPENDS_ON`은 역방향 전이 탐색, `SELECTS`는 1단계, `OVERLAPS`·`CONFLICTS_WITH`는 전이 금지, `SIMILAR_TO`는 탐색 불가. 도달 가능하다는 이유로 전달·대체하지 않는다.

### 후보 판정 질문 (question_set v2, M02)

강제 4+3 범주(v1)를 버리고 분해한다. 각 질문은 `noul`(예/아니오/판단불가) 또는 `choice`.

1. 같은 대상·주제를 말하는가? (noul)
2. 적용 역할·시점·조건이 겹치는가 / 구분되는가 / 알 수 없는가? (choice 3)
3. 공통 주장이 있는가? A에만 있는 주장이 있는가? B에만 있는가? (noul ×3)
4. 겹치는 조건 아래 두 주장이 함께 성립할 수 있는가? (choice: 양립/충돌/판단불가)
5. 판정에 필요한 조건·근거가 부족한가? (noul)

결합 규칙(코드): 1=예 ∧ 3.공통=예 ∧ (A만∨B만)=예 → `OVERLAPS` 후보; 2=겹침 ∧ 4=충돌 → `CONFLICTS_WITH` 후보; 5=예 → `open`. 질문 간 모순(예: "완전 중복"인데 "충돌")은 자동으로 `open`. 대체(`SUPERSEDES`)는 이 질문으로 결정하지 않는다.

### 후보 생성 (A3)

- 1차: 같은 작업대·같은 역할·같은 claim_type 안에서만 쌍을 만든다.
- 2차: 제목·키워드·원자료 경로 근접(규칙). 임베딩 검색은 선택(결정 항목 D3). 모든 쌍 비교는 하지 않는다.
- 후보 누락은 "검색 회수율"로 별도 측정한다(모델 정확도와 섞지 않음).

### 산출물·수용 기준

- `schema.py`(kind·합성 규칙), `questions_v2.json`, `candidates.py`, `combine.py`.
- 실제 사례 3쌍(L01 부분중복, P 역할별 공존, S 상태 변화)과 변형 15쌍이 v2 질문으로 표현되는지 — 특히 **L01이 `OVERLAPS`로 표현**되는지가 수용 기준.
- `RuleJudge`만으로 돌려 명시 정보 케이스(동일 digest, 같은 ID 다른 버전, 날짜 순서)가 모델 없이 결정되는지.

## 4. 단계 3 — 검토 분리

**목표:** 판정은 쌓이고, 변경은 승인된 것만 일어나며, 검토 큐가 둘 사이에 있다.

### 흐름

```text
judgment(규칙/모델/사람) ──► 검토 분류 ──► 검토 큐 ──► change(승인된 것만) ──► 투영 갱신
                              │                 │
                              │                 └─ 거부/보류 기록(판정은 그대로 보존)
                              └─ 자동 적용 허용 범위: 정확 규칙 결과만(D4)
```

### 검토 분류 (REVIEW_TRIAGE 연구의 세 범주를 그대로)

| 범주 | 조건 | 처리 |
| --- | --- | --- |
| 생략 후보 | 정확 규칙으로 결정됨(동일 digest, 명시된 대체 지시) 그리고 필수 검토 사유 없음 | 후보로 기록. D4에서 허용한 종류만 자동 변경 |
| 추가 검토 | 모델 판정, 점수 경합, `open`, 순서 불일치, 지원 범위 밖 | 큐에 적재. 상위 LLM 또는 사람 |
| 우선 검토 | `CONFLICTS_WITH` 후보, 사용자 정정, 근거 버전 불일치, 지침 변경 | 큐 상단. 해당 기억을 쓰는 view는 "검토 중" 표시 |

필수 검토 사유는 가중합으로 상쇄되지 않는다(코드로 강제).

### 변경 종류와 권한 (M04, 결정 항목 D5)

| change.kind | 허용 근거 | 기본 권한 |
| --- | --- | --- |
| `create` | 등록 | 등록 주체 |
| `promote_confidence`(candidate→reviewed→verified) | 검토 완료 judgment(human) 또는 실행 증거 | 사람 |
| `merge`(OVERLAPS → 새 기억 + 둘 다 유지) | 검토 완료. 고유 조건·출처 보존 검사 통과 | 사람 |
| `supersede` | 권한 있는 지시 또는 검토 완료 + 방향·유효 시점 명시 | 사람 |
| `retire` | 원자료 삭제 반영 또는 검토 완료 | 사람 |

"모델 점수 ≥ x이면 자동 병합" 같은 규칙은 **이 계획에 없다.** 그런 규칙을 추가하려면 §6의 평가 데이터로 허용 오류율을 보인 뒤 D4를 바꿔야 한다.

### 판정 보존

- 모델 판정은 선택지 순서·모델 버전·입력 digest·절단 여부와 함께 `judgment`로 보존(이미 Kev 실험이 하는 것).
- 사람 판정은 작성자·이유·이전 판정 연결(collect.py의 annotations 방식).
- 거부된 판정도 지우지 않는다.

### 산출물·수용 기준

- `review.py`(분류·큐), `change.py`(권한 검사·적용), 큐는 `memory-store/review-queue.jsonl` + 사람이 편집하는 `REVIEW_INBOX.md` 생성.
- 수용: (a) 모델 점수만으로는 어떤 change도 생성되지 않음(테스트), (b) L04 의무/금지 충돌이 우선 검토로 감, (c) 검토 거부 뒤에도 judgment가 남고 view는 변하지 않음, (d) L01 사용자 검토 응답(미응답 건)을 이 흐름으로 처리해 첫 `reviewed` 라벨을 만든다.

## 5. 단계 4 — view 생성

**목표:** 역할·업무별 MD를 저장소에서 생성하고, manifest로 추적하며, 전달 직전 최신성을 검사한다.

### 입력과 출력

- 입력: `selection`(role, task, rule_version, budget, required[]) + 현재 투영.
- 출력: `<작업대>/views/<role>/<task>.md` + `.manifest.json`(bundle 기록과 동일 내용). MD 상단에 생성 정보 3줄(bundle_id, 생성 시각, 원자료 버전 요약)과 "수정하지 말고 `REVIEW_INBOX.md`에 쓰라"는 안내.
- 섹션 규칙: 현재 유효 / 검토 중(충돌·대체 후보) / 만료·대체됨은 분리해 표시(M05). 근거 경로를 각 항목에 붙인다.

### 최신성과 재생성

- 전달 직전 `verify_bundle`: 원자료 해시·기억 버전·관계 그룹 버전·선정 규칙 버전 대조. 불일치면 `blocked` + 사유. 프로토타입의 READY/BLOCKED를 그대로 승격.
- 원자료 변경 등록 → `DEPENDS_ON` 역방향으로 영향 bundle을 stale로 → 재생성 → 재검사 → 공개. 재생성 중 또 바뀌면 보류.
- 삭제: 필수 기억이 빠지면 blocked, 선택 기억이면 생성하되 manifest에 누락 표시(D6).

### 실행기 연결 (이전 조사 결과 적용)

- Claude Code: `<작업대>/CLAUDE.md`에 `@views/<role>/current.md` import. SessionStart 훅은 bundle_id·stale 여부만 한 줄 전달. 전달 실패 차단은 UserPromptSubmit 게이트(실측 완료).
- Codex: `developerInstructions` 또는 SessionStart. Pi: `before_agent_start`. 세부는 [runtime-intervention-research](../runtime/runtime-intervention-research/FINDINGS.ko.md).
- "입력에 들어갔다"는 증거: Claude는 세션 기록의 `instructions`/`hook_additional_context`, Codex는 `instructionSources`. bundle에 `delivery_receipts[]`로 기록.

### 생성된 MD의 수정 (결정 항목 D7)

초기 기본값: **생성 view는 읽기 전용.** 에이전트·사용자의 수정 제안은 `REVIEW_INBOX.md`에 쓰고 검토 큐로 들어간다. 양방향 동기화는 하지 않는다. 이유: 원본이 둘이 되는 구조(R06이 피하려는 것)를 막는다.

### 산출물·수용 기준

- `view.py`(generate/verify/regenerate), 템플릿 1개.
- 실제 사례: `rsch` 역할의 "runtime lifecycle 연구" 업무 view 하나를 생성해 이 세션(Claude Code)에 실제 전달 → 세션 기록에서 포함 증거 확보 → 첫 응답에서 인수 확인 줄 관측. 이것이 **R02·R04와 R05·R06을 처음으로 잇는 검증**이다.
- 수용: (a) 원자료 1개 변경 시 영향 view만 stale, (b) 같은 기억을 두 역할 view가 쓸 때 원본 변경이 둘 다에 반영, (c) blocked bundle은 전달되지 않음(훅 로그).

## 6. 단계 5 — Judge 인터페이스와 모델 자리

**목표:** 판정자를 바꿔 끼워도 저장소·검토·view는 바뀌지 않는다.

```python
class Judge(Protocol):
    name: str; version: str
    def ask(self, state: dict, questions: dict) -> JudgeResult: ...
# JudgeResult: scores{qid: {option: p}}, option_order{qid: [...]}, decided{qid: option|None},
#              abstain_reason{qid: str|None}, input_digest, truncated: bool, receipt{...}
```

| 구현 | 상태 | 역할 |
| --- | --- | --- |
| `RuleJudge` | 새로 작성(run_pilot.py의 `rules()`를 옮김) | 기본값. 명시 정보만 결정, 나머지 `abstain` |
| `KevJudge` | 기존 코드 감싸기(`vendor/kev`, `LocalPredictor`) | 제안 전용. 순서 2회 이상 실행해 불일치를 `abstain_reason`에 기록 |
| `LLMJudge` | 스텁 → 구조화 출력 1회 | 비교군 |
| `HumanJudge` | REVIEW_INBOX 응답을 judgment로 변환 | 라벨 생성 |

규칙: 어떤 Judge의 결과도 `judgment` 기록으로만 들어간다(§4). Judge 교체는 설정 한 줄. 평가 하네스(`eval.py`)는 같은 사례 묶음으로 모든 Judge를 돌려 §7 지표를 낸다.

### 평가 데이터 (A10)

- 기존 18쌍 + 실제 업무에서 생기는 검토 응답을 라벨로 축적(HumanJudge).
- 원문 가족 단위 분할. 첫 목표: **검토된 라벨 30건**(지금 0건). 이 수가 차기 전에는 Judge 비교 수치를 "제안 일치"로만 부른다.

## 7. 지표와 효과 측정 (M06, A12)

| 지표 | 측정 위치 |
| --- | --- |
| 필요한 검토 누락 / 불필요한 재검토 / 생략 비율 | 검토 큐 |
| 잘못된 병합 후보(고유 조건 손실) | merge 전 보존 검사 |
| 후보 회수율 | candidates vs. 사람이 찾은 쌍 |
| 전달량(항목·바이트), blocked 비율, 재생성 횟수 | bundle |
| 입력 포함 증거 / 첫 응답 인수 / 재설명·재작업 횟수 | delivery_receipts, 세션 기록, 사용자 정정 수 |
| Judge별 제안 일치·보류율·순서 불일치·지연 | eval.py |

## 8. Owner 결정이 필요한 항목

> 2026-10-17 반박 검토 결과와 추가 항목 D14–D21은 [DECISIONS_D1_D21_CLAUDE.md](DECISIONS_D1_D21_CLAUDE.md)에 있다. 아래 표는 검토 전 기본값이며, D2·D3·D4·D9·D13은 그 문서의 권고안으로 바뀌었다.

| # | 결정 | 기본값 제안 |
| --- | --- | --- |
| D1 | 저장 형식 | jsonl 추가 전용 + SQLite 투영, Git 관리. 그래프 DB 없음 |
| D2 | 관계 종류 목록 | §3 표. `OVERLAPS`를 부분중복+보완 통합 종류로 |
| D3 | 후보 생성에 임베딩 검색 사용 여부 | 1차는 규칙만. 회수율이 낮으면 추가 |
| D4 | 자동 변경 허용 범위 | 정확 규칙 결과(동일 digest, 명시 지시)만. 모델 점수 기반 자동 변경 없음 |
| D5 | 검토 주체 | 사용자. 상위 LLM은 "추가 검토" 초안만 |
| D6 | 필수/선택 기억 누락 시 bundle 정책 | 필수 누락 blocked, 선택 누락 표시 후 생성 |
| D7 | 생성 view 수정 | 읽기 전용 + REVIEW_INBOX |
| D8 | 저장소 위치 | `bootstrap/memory-store/` (작업대와 분리, 같은 Git) |
| D9 | 구현 담당 | 단계 1–2: 이 세션 또는 Codex rsch_sub_memory(기존 코드 보유). 단계 4의 실행기 연결: 이 세션 |

## 9. 순서와 완료 조건

| 단계 | 선행 | 완료 조건(요약) | 크기 |
| --- | --- | --- | --- |
| 1 저장소 | D1, D8 | 재구성 동일·stale 추적·변조 검출 | 작음 (프로토타입 재배치) |
| 2 관계 스키마 | 1, D2 | L01이 OVERLAPS로 표현, RuleJudge가 명시 정보 결정 | 중간 |
| 3 검토 분리 | 2, D4, D5 | 점수만으로 change 0건, L04 우선 검토, 첫 reviewed 라벨 | 중간 |
| 4 view 생성 | 1–3, D6, D7 | rsch 업무 view 1개를 실제 세션에 전달하고 포함 증거 확보 | 중간 |
| 5 Judge | 2 | RuleJudge·KevJudge·HumanJudge가 같은 하네스에서 동작 | 작음 (기존 코드) |
| 평가 | 3, 5 | 검토 라벨 30건, 지표 첫 집계 | 지속 |

단계 5는 2 뒤 언제든 병행 가능하다. **단계 4 완료가 첫 실질 성과**(R02·R04·R05·R06이 한 사례에서 연결)이므로, 1–3은 그 사례 하나를 통과시키는 최소 범위로 좁힌다.

## 10. 위험

- 관계 작성 비용이 효과보다 클 수 있다 → 단계 4 사례 하나로 먼저 재는 이유.
- 라벨 0건 상태에서 모델을 평가하면 "제안 일치"를 정확도로 오해 → §6 규칙.
- 생성 view와 원본의 이중 수정 → D7 읽기 전용.
- 실행기가 검사를 우회해 옛 파일을 읽음 → delivery_receipts로 실제 포함을 확인, 훅 로그 대조.
- JEV-BYUL의 11개 기록 계약을 그대로 들이면 과설계 → §7 봉투와 judgment/change 분리만 차용(상세 대조는 별도 문서).

## 11. 관련 문서

- 근거·범위: [JEVLIKE_GAP_CLAUDE.md](JEVLIKE_GAP_CLAUDE.md)
- 프로토타입: `research/sub-memory/graph-pilot-20261014/study.py`, `research/sub-memory/memory-pilot-20261014/`
- 실행기 접점: [claude-entry-research](../runtime/claude-entry-research/FINDINGS.ko.md), [codex-entry-research](../runtime/codex-entry-research/FINDINGS.ko.md), [runtime-intervention-research](../runtime/runtime-intervention-research/FINDINGS.ko.md)
- 선행 연구 대조: [JEV_BYUL_COMPARISON_CLAUDE.md](JEV_BYUL_COMPARISON_CLAUDE.md) — D10–D13 추가 결정 항목 포함
