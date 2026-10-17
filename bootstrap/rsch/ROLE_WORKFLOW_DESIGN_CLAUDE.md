# bootstrap 역할·워크플로 설계 초안 (AAA 벤치마크 기반)

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 요청: 사용자 "역할 설계도 같이 해주세요. 그동안의 AAA에서 쓴 역할들을 벤치마킹", "워크플로우도 같이 벤치마킹"
- 벤치마크 원천: AofSpds/AAA main `9ec67c5` (2026-10-13 스냅샷 `dev/AAA/workspaces/rsch-video-records-20261013`). 직접 읽은 정본: `projects/AAA/planning/{ROLE_ALIASES, SUB_PLANNER_OPERATING_REQUIREMENTS, SUB_PLANNER_OPERATING_PLAN, SUB_PLANNER_OWNER_TERMINATION_LIFECYCLE_AMENDMENT, CHANNEL_START_INVOCATION_MATRIX, COMMON_OWNER_CONTINUOUS_WORK_RESPONSE_FORMAT_REQUIREMENT}`, `projects/AAA/coordination/{PROTOCOL, PACKET_DELIVERY_POLICY, INDEX}`, `projects/AAA/subplans/{INDEX, TEMPLATE}`, `core/{AGENTS, CURRENT, bootstrap/AAA_OPERATIONAL_V1_PROJECT_INSTRUCTIONS}`, `projects/AAA/CURRENT.md`, `records/personas/INDEX.md`, 활성화 패킷 1편, WORKLOG 말미.
- aaaNew 측 근거: 역할 운용 실태 조사(살아남은 조사자 1명 결과) + `Agent_memory/README.md`·`LESSONS_CODEX.md`·`sub/AGENTS.md`·R01–R08.
- 개정: v0.2 (2026-10-17) — Opus 반박 검토 1회 반영. 반영 내역은 §9.
- 한계: 교환 59건·서브플랜 10여 개의 실패 사례 전수 조사는 사용량 한도로 하지 못했다. 아래 "관측된 비용"은 정본 문서와 색인에서 직접 읽은 범위다. 이 문서는 제안이며 채택 확정이 아니다.

**결론: AAA의 역할 체계는 경계 선언(≠ 부등식, 상한 목록, Owner 전용 종료)이 정교하지만, 그 경계를 문서와 사람의 복사·확인으로만 지켰다. bootstrap은 역할을 4개(pln·sub_pln·rsch·impl)+검증(iva)+Owner로 줄이고, 역할을 "작업대 폴더 + 진입 규칙 + 권한 + 기록 의무"로 정의하며, 경계 중 기계가 지킬 수 있는 것(작업대 밖 쓰기, 전달 전 검사, 종료 시 인계 기록)은 훅·manifest·저장소 기록으로 지킨다. 단 훅 강제는 지금 Claude Code `-p` 실측 범위에 한정되고, Bash 쓰기·Codex·앱 대화형 세션은 검증 대상이다. 패킷 복사·채널 라벨·Persona는 제거한다.**

## 1. AAA 벤치마크 요약

### 1.1 역할 체계

| AAA 역할 | 정의 위치 | 요점 |
| --- | --- | --- |
| HUMAN OWNER | 종료 수명주기 개정 §1·§4 | 유일한 종료 권한. 요구·범위·단계 처분 결정("M3 M4는 그것으로 일단락") |
| PLANNER (PLN) | 역할 별칭 v1.0, Parent Current | Main Project 계획·얇은 Current·서브플랜 개설·결과 통합. 상세는 child exact ref로만 |
| SUB_PLANNER (SPLN) | 운영 요구 v1.0 §1–§10 | 작업 범위 한정 위임 계획자. 클래스 SR(연구)/SP(계획)/SE(실행). 배정 필수 필드 12개. 상태 PREPARED/ACTIVE/IDLE_READY/BLOCKED/OWNER_TERMINATED |
| Architect / Researcher / PMO / Engineering / IVA | 채널 시작 매트릭스 교정 절(NC-R024) | "기능집합"이며 roster 미고정. PMO는 실행 조율·병합, IVA는 독립 검증 |
| Persona (HLOM 등) | records/personas | 역할·채널·권한과 별개의 정체성. "Persona ≠ 기능 역할 ≠ 실행 권한 ≠ 검증 권한" |
| OPI / WH / HEF / ORDER / SLR | Core Current, 서브플랜 색인 | 운영 항목(OPI), Work Harness(WH), 과거 작업 계열(HEF), 외부 프로젝트 하위 마일스톤(ORDER), 자기학습 런타임 연구(SLR). 역할이라기보다 작업 계열 이름 |

청구 상한(claim ceilings, 운영 요구 §10)이 체계의 핵심이다: 연구 결과 ≠ 요구 채택, 계획 완료 ≠ 구현 완료, 실행자 완료 ≠ 독립 검증, 검증 PASS ≠ Owner 수용, Work Act 종료 ≠ Sub-Planner 종료 ≠ Project 종료.

### 1.2 작업대·기록 관행

- 서브플랜마다 `ASSIGNMENT / CURRENT / PLAN` 세 파일. Parent Current는 "얇게"(exact child ref만).
- 교환마다 `coordination/exchanges/<EXCHANGE_ID>/{REQUEST, RESPONSE, RECEIPT…}`. 상태 `PREPARED ≠ DISPATCH_CONFIRMED ≠ RESPONSE_RECEIVED ≠ REVIEWED ≠ CLOSED`.
- 새 채널 진입은 activation/succession 패킷(PROJECT, TARGET_PERSONA, FUNCTIONAL_ROLE, REPOSITORY, EXACT_COMMIT, PACKET). Owner 채팅에는 7필드 envelope 한 코드블록만, 지시는 Git 패킷 안에. 패킷은 persist → readback → envelope 순.
- Owner 응답 형식: 상단 실제 시작 시각, 말미 "전체 Workflow Milestone / 현재 위치 / 실제 완료 / 다음 / 막힘", 최하단 시각·경과·Owner 행동 1개.
- 반환 6항목: result / evidence / delta / open items / learnings / next dependency. `RETURNED ≠ PARENT_ADMITTED`.

### 1.3 워크플로 유형 (정의 문서 기준)

| 흐름 | 단계 |
| --- | --- |
| 배정 시작 | Parent Current 복구 → CONTEXT_BASE_REF/REVISION 결속 → 클래스·범위·의존·쓰기 범위 → 실행 모드/정책 → 능력·증거·권한 확인 → 서브플랜 Current 생성 → 합법적 독립 작업만 시작 |
| RESEARCH | 질문 → 증거 계획 → 조사 lane → 근거 조정 → 결과/불확실성/대안 → 계획 영향 → 반환 |
| PLAN | 범위 요구 → 아키텍처/옵션 → 결정 후보 → 실행 입력 → 반환 |
| EXECUTE | 목표 → 필요 연구/계획 → 정확한 실행 계획 → 승인된 구현 → 완료/freeze → 독립 검증 → 영향 한정 교정 → fresh-reader 증명 → 완료 패키지 → 반환·기록 → IDLE_READY |
| 패스트트랙(Parent Current §6) | 요구 정의 → PMO 실행계획 → 실행·동결 → 검증·SUB_PLN 계획대비 확인 → PMO 병합·현행화 |
| 교환 | REQUEST 기록·readback → envelope → (사람이 복사) → 수신 → RESPONSE 기록 → 검토 → Current 갱신(필요 시만) |

### 1.4 관측된 비용과 문제 (정본·색인에서 직접 확인)

| 관측 | 근거 |
| --- | --- |
| 경계가 문서로만 선언됨. Owner: "안막아도 됩니다. 명시만 할수 있으면 되어요" → `TECHNICAL_FENCE = NOT_INSTALLED_BY_OWNER_DECISION` | Parent Current §1, Core Current |
| 패킷 전달이 사람의 복사에 의존. "packet 존재 ≠ dispatch confirmed"를 매번 명시해야 함 | PACKET_DELIVERY_POLICY §5·§7, PROTOCOL §4 |
| 같은 경고의 반복: "SUB_PLN 확인을 독립검증으로 승격하지 않음", "RETURNED ≠ PARENT_ADMITTED"가 Current·색인·영수증마다 다시 적힘 — 체계가 기억하지 못하고 사람이 매번 적는다 | Core Current, 서브플랜 색인, 교환 색인 말미 |
| 채널·Persona 혼선: Owner가 검토 수신처를 재확인하며 "이 채널입니다. 페르소나 오류인가보네요" | Core Current 2026-09-26 절 |
| 규모: 교환 59개, 활성화 패킷 10개, 서브플랜 10여 개, 로컬 workspaces 폴더 150여 개(2026-10-13) | coordination/exchanges, workspaces 목록 |
| 외부 채널 응답 대기: Pro 보고 전송 20:03 → 20:35까지 미수집, 상태 해석 불가 | WORKLOG 2026-10-07 |
| 실사용 관찰(WBS-75)은 끝까지 `NOT_OBSERVED` | Parent Current §4 |
| 역할 이름 과잉: PLN/SPLN/PMO/ARCH/IVA/OPI/WH/HEF/SLR/ORDER + Persona + 채널 라벨 | 위 표 |

### 1.5 aaaNew에서 실제로 겪은 문제 (조사자 결과)

- 기본 cwd(AAA)와 작업대(rsch) 혼동 → 사용자가 경로를 반복 설명. 자동 강제 없음.
- 세션 간 통신이 비공식·비대칭(Claude→Codex는 내부 큐 DB 직접 삽입, Codex→Claude는 화면 입력). 요청 파일 합의 후 미생성.
- 작업 기억이 "결과 예정"인 채 stale → 다음 세션이 끝난 조사를 재요청할 위험.
- 서브 세션은 작업대(rsch_sub_memory)와 기억(sub/)이 이원화. 세션 생성 시 cwd 바인딩 불가.
- 검토 주체(사용자) 병목: L01 검토 질문 장기 미응답, 라벨 0건.
- 범위 과확장(인수만 → 18쌍·282회 모델 시험) 뒤 사용자 정정.
- Owner와 사용자 표기 혼용, 초기 커밋 작성 주체 미표기.

## 2. 설계 원칙

1. **역할 = 작업대 폴더 + 진입 규칙 + 권한 + 기록 의무.** 세션·실행기(Codex/Claude/Pi)는 역할을 수행하는 수단이며 역할 정의에 들어가지 않는다. AAA의 "Persona ≠ 역할 ≠ 권한"에서 Persona를 뺀 형태.
2. **역할 수는 최소.** R01이 "현재 논의한 역할"로 든 rsch·pln(rsch는 상설로 확정하지 않음, 프로젝트별 조건부), 조건부 sub_pln, 그리고 실행을 맡을 impl. 검증은 역할이 아니라 "다른 세션이 읽기 전용으로 하는 행위"(iva)로 둔다. PMO·ARCH·OPI·WH 같은 이름은 만들지 않는다.
3. **기계가 지킬 수 있는 경계는 기계가 지킨다.** 실측 범위는 Claude Code 2.1.268 `-p` 한 세션에서 PreToolUse가 Read를 거부한 것과 Stop block 1회다. Write/Edit 차단은 같은 수단으로 가능하지만, Bash 리다이렉트·스크립트 쓰기, Codex 훅, 앱 대화형 세션은 미실측이다. "강제"는 이 범위로 한정하고 나머지는 검증 대상으로 둔다. 나머지 경계(반환 ≠ 수용 등)는 저장소 기록(change·judgment)의 상태 전이로 남긴다. 어디까지 fail-closed로 할지는 Owner 결정(R04, D11).
4. **인계는 파일과 큐로, 채팅 복사는 최소화.** AAA의 7필드 envelope은 사람이 복사하는 전제였다. bootstrap은 요청 파일을 대상 작업대 `REQUESTS/`에 쓰고 전달은 도메인 실행기 또는 큐가 한다. 그 전까지 1차 경로는 사용자 중계(E5)이며, 이때 DELIVERED는 수신 측 인수 확인 줄로만 사후 확인하고 전달 시각을 만들지 않는다(AAA PROTOCOL §4). 전달 영수증은 D20에 맞춰 attachment 종류 + bundle_id + 시각만 남긴다(세션 ID 미기록).
5. **증거 사다리와 청구 상한은 그대로 가져온다.** 파일 존재 ≠ 입력 포함 ≠ 준수 ≠ 효과; 실행자 완료 ≠ 검증 PASS ≠ Owner 수용; 반환 ≠ 수용 ≠ 종료. 단, 문서마다 다시 적는 대신 상태 enum과 템플릿에 한 번 박는다.
6. **Owner 부담은 결정 카드 하나와 응답 footer로 고정.** Owner는 모바일에서 읽는다. 질문은 "선택지 + 권고 + 기본값" 한 카드, 응답 말미는 AAA 형식을 축약한 5줄.

## 3. 역할 설계

| 역할 | 작업대 | 목적 | 결정 가능 | 금지(상위로) | 반환물 | AAA 대응 |
| --- | --- | --- | --- | --- | --- | --- |
| **owner** | 없음. `bootstrap/OWNER_INBOX.md`(결정 카드) | 요구·범위·단계 처분·종료 결정, 검토 승인 | 전부 | — | 결정 기록(change.authority) | HUMAN OWNER |
| **pln** | `bootstrap/pln/` | 프로젝트 전체 계획, 마일스톤, 작업대 개설·배정, 반환 수용(admit), 얇은 CURRENT | 배정·우선순위·수용·BLOCKED 처리 | 직접 구현, 검증 PASS 선언, 역할 종료, 요구 변경 | PLAN, 배정 요청, ADMIT 기록 | PLN |
| **sub_pln** | `bootstrap/pln/<milestone>/` | 한 마일스톤의 범위 계획과 실행 조율. 작업대 2개 이상이 얽히거나 세션을 넘길 때만 개설(조건은 E2) | 마일스톤 안의 배정·순서 | pln 권한 전부, 마일스톤 밖 쓰기 | 마일스톤 PLAN·반환 묶음 | SPLN(SP) |
| **rsch** | `bootstrap/rsch/` | 조사·실측·대조. 결과는 findings + 결정 카드 후보 | 조사 방법·증거 등급 | 제품 변경, 요구 채택, 구현 시작 | FINDINGS, 결정 카드 후보, 교훈 후보 | SPLN(SR), Researcher |
| **impl** | `bootstrap/<component>/` (예: `memory-engine/`) | 코드·실행. 변경 묶음마다 E2E 1회 + 영수증 | 구현 세부, 자기 묶음의 E2E | 자기 PASS 선언, 요구·계획 변경, 다른 작업대 쓰기 | 변경 묶음 + 영수증 + learnings | SPLN(SE), PMO+Engineering |
| **iva** (행위) | 없음. 결과는 대상 작업대 `reviews/`(추가 전용) | 독립 검증. 대상은 변경 묶음과 PLAN·설계 산출물. 작성 세션과 다른 세션, 가능하면 다른 실행기, 읽기 전용 | PASS/FAIL/PARTIAL 판정 | 수정, 승인 | REVIEW 기록(judgment head=llm; human은 Owner만) | IVA, ARCH 심사 |

Architect는 별도 역할로 두지 않는다. 설계 산출물은 rsch(조사 설계)나 pln(계획 설계)의 반환물이고, AAA의 별도 ARCH 심사 기능은 iva가 PLAN·설계 산출물을 검증하는 것으로 대신한다. AAA PMO의 통합 기능(병합·재조회·Current 현행화)은 이렇게 나눈다: 커밋·푸시는 Owner 지시 때만(D15), 각 CURRENT는 그 작업대의 작성 세션만 갱신한다. Persona·채널 라벨·실행기 이름은 기록의 `created_by`·`delivery_receipts` 필드로만 남는다.

### 3.1 상태

- 작업대 상태: `ACTIVE / IDLE / BLOCKED / CLOSED`. CLOSED는 owner만. (AAA PREPARED/ACTIVE/IDLE_READY/BLOCKED/OWNER_TERMINATED의 축약)
- 작업 단위(work act) 상태: `PREPARED → ACTIVE → RETURNED → ADMITTED | REJECTED`. RETURNED ≠ ADMITTED.
- 요청 상태: `PREPARED → DELIVERED → RECEIVED → RETURNED → CLOSED | CANCELLED`. DELIVERED는 전달 증거, RECEIVED는 수신 세션의 첫 응답 확인 줄.

### 3.2 작업대 표준 구조

작업대는 중첩하지 않고 `bootstrap/` 아래 형제 폴더로 둔다. 자식 cwd에서 상위 CLAUDE.md가 함께 로딩되어 지침이 섞이기 때문이다(claude-entry-research §3). 작업대당 CURRENT 작성 세션은 1개이고, 다른 실행기는 RETURNS로만 기여한다.

```text
bootstrap/<role>/
├─ CLAUDE.md            # 1줄 @views/<role>/current.md import + 생성 정보 (Claude)
├─ AGENTS.md            # 같은 내용의 Codex 미러 (E7)
├─ CURRENT.md           # 얇게: 상태, 현재 work act, 다음 한 단계, 막힘. Stop 훅이 갱신 강제
├─ REQUESTS/<ID>.md     # 받은 요청 (pln이 씀)
├─ RETURNS/<ID>.md      # 반환: result/evidence/delta/open/learnings/next
├─ reviews/<ID>.md      # iva 결과
├─ views/<role>/current.md + .manifest.json   # 관계 엔진이 생성, 읽기 전용
└─ .claude/settings.json  # 앱 직접 세션용 관문 (첫 사례는 D18대로 --settings로 주입)
```

관문 규칙: 쓰기 허용 = 자기 작업대 + 활성 REQUEST의 `WRITE_SCOPE` + 다른 작업대의 `REQUESTS/`·`reviews/`에는 새 파일 추가만. REQUESTS/RETURNS/reviews는 덮어쓰지 않고 개정 파일로만 고친다(AAA PROTOCOL §8). Codex 쪽 동등 관문(`.codex/hooks.json`, `/hooks` 신뢰)은 Codex 세션이 설정·실측한다.

파일 수는 AAA의 ASSIGNMENT/CURRENT/PLAN + 교환 폴더보다 적고, 역할당 CURRENT는 하나다.

## 4. 워크플로 설계

### W1 진입 (R02·R04)

```text
도메인 실행:  역할·작업대 선택 → bundle 검사(blocked면 보류) → cwd=작업대, --settings 관문, SessionStart(bundle_id) → 첫 프롬프트
사용자 직접:  폴더 선택 → CLAUDE.md/AGENTS.md 로딩 → 첫 응답 "인수 확인 줄"
```

첫 응답 첫 줄 고정 형식: `[역할 rsch · 작업대 bootstrap/rsch · bundle b_… · 현재 T-42]`. 이 줄이 없으면 "준수 미관측"으로 기록한다. 전달(입력 포함) 증거는 세션 기록의 instructions·hook_additional_context로 따로 남긴다. 도메인 실행 시에는 자식 프로세스의 `CLAUDE*`·`MCP_*` 환경 변수를 정리한다(claude-entry-research §6). 잘못된 폴더 경고는 aaaNew 안의 상위 CLAUDE.md 진입 규칙으로만 가능하다. AAA처럼 aaaNew 밖 폴더에서 연 세션에는 작업대 훅이 실행되지 않아 경고도 불가능하다(한계).

### W2 배정·요청 (AAA 교환 프로토콜의 축약)

1. pln이 `<대상 작업대>/REQUESTS/<ID>.md` 작성. 필드 10개: `ID, FROM, TO, GOAL, SCOPE, WRITE_SCOPE, MUTATION(NONE/ALLOWED), DEPENDENCIES, CONTEXT(bundle_id@version), RETURN_CONDITION`. AAA 12필드 중 SUBPLAN_CLASS는 작업대 역할로, EXECUTION_MODE·AUTHORITY_REF는 change.authority로 대체한다. 병렬 진행 시 같은 범위의 작성 세션은 1개(AAA PRIMARY_INTEGRATOR).
2. 전달: 도메인 실행기가 대상 세션을 띄우거나 큐에 넣는다. 사람 복사 없음. 저장소에 `delivery_receipt`.
3. 수신: 대상의 첫 응답 인수 확인 줄에 요청 ID 포함 → RECEIVED.
4. 반환: `RETURNS/<ID>.md` 6항목. 상태 RETURNED.
5. 수용: pln(마일스톤 안이면 sub_pln)이 ADMITTED/REJECTED를 change 기록으로 남긴다. ADMIT 기록에는 `계획대비 / 미결 / 필요 검증` 3칸이 필수다(AAA SUB_PLN 계획대비 확인의 대체). CURRENT는 실제 바뀔 때만 갱신(AAA PROTOCOL §7 유지).
6. 반환 뒤에는 스스로 다음 작업을 시작하지 않는다. 범위 확장은 REQUEST 개정으로만 한다(AAA 종료 수명주기 §3; aaaNew rsch_sub_memory의 범위 과확장 사례).

### W3 수행·검증

- 실행 묶음 = 변경 + E2E 1회 + 영수증(해시·실행 시각·결과). 성공한 묶음은 재실행하지 않는다(NO_RERUN).
- iva 필수 조건: 다른 작업대·main에 반영되는 변경 묶음, 그리고 다른 역할이 입력으로 쓸 PLAN·설계 산출물. 그 밖은 선택. 결과는 `reviews/`에 judgment(head=llm). "실행자 완료 ≠ iva PASS ≠ owner 수용"은 상태 enum으로.
- AAA의 "SUB_PLN 계획대비 확인" 단계는 두지 않는다. 그 확인은 pln의 ADMIT 기록이 대신한다.

### W4 반환·인계

- Stop 훅이 1회 요구한다: 이번 세션에 파일 변경이 있었는데 CURRENT.md 수정 시각이 갱신되지 않았으면 block + reason으로 갱신을 요구한다(실측: `-p`에서 block 1회, 두 번째는 `stop_hook_active`로 통과). "비어 있으면" 조건은 stale 내용을 통과시키므로 쓰지 않는다. Stop은 매 턴 끝에 발화하며, 창 닫기·한도 중단에는 발화하지 않을 수 있다(미실측).
- RETURNS의 `learnings`는 경험 후보로 저장소 검토 큐에 들어간다(관계 엔진 단계 3).
- 세션이 바뀌어도 작업대의 CURRENT + views + REQUESTS/RETURNS만으로 재개한다. AAA의 succession 패킷은 만들지 않는다.

### W5 경험화 (R05)

`RETURNS.learnings → 검토 큐 → reviewed → 역할 view 재생성 → 다음 세션 진입 시 포함`. 검토 주체·자동 범위는 D4·D5.

### W6 Owner 루프

- 결정 카드: 채팅으로 1개씩 보내고, 파일 기록은 관계 엔진의 REVIEW_INBOX 하나에 합친다(OWNER_INBOX 별도 생성 안 함). 형식은 "질문 / 선택지 / 권고 / 기본값 / 미응답 시 처리", 응답은 한 줄. 미응답 시 기본값 진행은 되돌릴 수 있는 순서 결정에만 허용하고, 요구·범위·종료·reviewed 승격은 보류한다(AAA 종료 수명주기 §7, D4).
- 응답 footer(AAA 형식 축약): `현재 위치 / 실제 완료 / 다음 / 막힘 / Owner 행동 1개`. 시작 시각 1줄은 선택(외부 응답 대기 해석에 시각이 쓰였음, §1.4). E6에서 Owner 선택.

### W7 종료·보관

- 작업대 CLOSED는 owner만. 기본안: 제자리 보존 + CLAUDE.md/AGENTS.md를 "닫힘·후속 위치" 1줄로 교체(로딩·후보 생성 재진입 방지) + AAA 종료 기록 필드 채택. 대안: 기존 관행대로 `legacy/` 이동. Owner 선택(E8).
- 대용량 실험 환경(.venv, 모델 캐시, 백업 zip)은 작업대 밖(gitignore) — D15·D20.

## 5. AAA와 다른 점과 이유

| AAA | bootstrap | 이유 |
| --- | --- | --- |
| 역할 10여 개 + Persona + 채널 라벨 | 역할 4 + iva 행위 + owner | 이름 과잉이 혼선(페르소나 오류)과 반복 경고를 낳았다 |
| 7필드 envelope을 사람이 복사 | 요청 파일 + 도메인 전달 + 수신 증거 | "packet 존재 ≠ dispatch confirmed"를 사람이 아니라 기록이 보장 |
| 기술적 fence 없음(Owner 결정) | 작업대 밖 쓰기·전달 전 검사·종료 인계는 훅으로 | R04가 "프로그램이 개입하는 지점 우선"을 요구. 강제 범위는 Owner 결정 |
| ASSIGNMENT/CURRENT/PLAN + 교환 폴더 59개 | 작업대당 CURRENT 1개 + REQUESTS/RETURNS | Current 파편화·재확인 비용 감소 |
| 반환 → SUB_PLN 확인 → PMO 병합 | 반환 → iva(선택) → pln ADMIT | 단계 하나 제거. 확인 주체가 둘이면 승격 혼동이 생겼다 |
| 활성화·승계 패킷 | 작업대만으로 재개 | 작업대가 세션보다 오래 간다(R01) |
| Owner 응답 형식 3블록 | footer 5줄 | 모바일 Owner |

가져온 것: 청구 상한, 반환 6항목, 얇은 Current, Owner 전용 종료, 상태 부등식(enum으로), NO_RERUN, 증거 등급.

## 6. 첫 사례 수용 기준 (관계 엔진 계획 단계 4와 결합)

1. `bootstrap/rsch`에 CLAUDE.md·views를 두고, 환경 변수를 정리한 뒤 cwd=bootstrap/rsch로 CLI 자식 세션을 시작한다(훅은 `--settings`). 통과: 세션 기록에 instructions·hook_additional_context가 있고 첫 응답에 인수 확인 줄이 있다.
2. 요청 1건(R-001)을 `rsch/REQUESTS/`에 두고 수행 → `RETURNS/R-001.md`. 통과: 6항목이 모두 있고 상태가 RETURNED. ADMIT change 기록은 pln 작업대와 저장소(관계 엔진 단계 1)가 생긴 뒤의 기준으로 분리한다.
3. 통과: 작업대 밖 Write/Edit가 거부된다. Bash 리다이렉트 쓰기는 결과(거부 또는 미차단)를 기록한다. Stop 훅이 CURRENT 미갱신 시 1회 block하고 두 번째는 통과한다.
4. 기대 다음 단계를 미리 기록해 두고, 새 세션 재개 시 첫 응답의 다음 단계와 대조한다. 판정자는 Owner.
5. 실패 주입: bundle을 blocked로 만들고 UserPromptSubmit exit 2로 첫 모델 호출이 0회인지 확인한다(2.1.268 실측 재현).

## 7. Owner 결정 항목 (E1–E9)

| # | 결정 | 권고 |
| --- | --- | --- |
| E1 | 역할 집합 확정: pln·sub_pln·rsch·impl + iva 행위 + owner | 이대로. rsch는 프로젝트별 조건부. Architect·PMO 기능은 iva(설계 검증)·Owner(통합 커밋)로 분산 |
| E2 | sub_pln 개설 조건 | 마일스톤이 작업대 2개 이상을 얽거나 세션을 넘길 때만 |
| E3 | iva 운영 방식 | 구현과 다른 세션, 가능하면 다른 실행기(Claude↔Codex 교차). 읽기 전용 |
| E4 | 강제 수준(D6·D11과 묶음) | Claude Write/Edit의 작업대 밖 쓰기는 fail-closed. bundle blocked 시 앱 세션 잠금 여부는 D6·D11 결정을 따름(앱 세션 수단은 UserPromptSubmit exit 2뿐). Bash·Codex 관문은 실측 후 결정 |
| E5 | 요청 전달 경로 | 1차는 파일 + 사용자 중계(현재 Codex→Claude 큐가 없음). 도메인 실행기 생기면 자동 |
| E6 | Owner 응답 footer 채택 | 5줄 축약형 + 시작 시각 1줄(선택). Owner 선택 |
| E7 | Codex 미러 AGENTS.md | 생성 전에 Codex rsch 세션의 동의와 Codex 상위 AGENTS.md 로딩 범위 확인을 조건으로 함(rsch_sub_memory 지침이 바뀔 위험) |
| E8 | 닫힌 작업대 처리 | 제자리 보존 + 진입 파일 1줄 교체(기본) / legacy 이동(대안) |
| E9 | D18 재결정 | 첫 사례는 `--settings`, 앱 직접 세션은 `.claude/settings.json` — 단계별 병행으로 D18 문구 수정 |

## 8. 미확인·보류

- AAA 교환 59건의 실패 사례 전수 대조(BLOCKED·NEEDS_CORRECTION·SUPERSEDED 분포)는 미수행. 필요하면 Sonnet 1명으로 색인 단위만 추출.
- Planning Context의 `CONTEXT_MANIFEST`·`EXPERIENCE_PROJECTION`과 views/manifest의 이름·역할 대조 미수행(선행 대조 §7과 같은 항목).
- pln·sub_pln·impl 작업대는 아직 폴더도 없다. 이 설계는 rsch 하나의 운용 경험에서 일반화한 것이다.

## 9. 반박 검토 반영 (v0.2, 2026-10-17)

Opus 검토자 1명이 초안·요구사항·실측 보고 2편·D1–D21·AAA 정본 3편·교훈 파일을 읽고 판정했다(파일 10개, 수정 없음). 결과: 유지 1, 변경 16, Owner 선택 4.

| 지적 | 반영 |
| --- | --- |
| 관문 "작업대 밖 쓰기 거부"가 pln의 REQUESTS 작성·iva의 reviews 작성과 자기모순. 작업대 중첩 시 지침 섞임 | 관문 규칙을 "자기 작업대 + WRITE_SCOPE + 타 작업대 REQUESTS/reviews 추가만"으로, 작업대는 형제 폴더로(§3.2) |
| 훅 강제 주장이 실측 범위(2.1.268 `-p`, Read 거부 1건, Stop 1회)를 넘음 | 원칙 3을 실측 범위로 한정. Bash·Codex·앱 세션은 검증 대상(§2, E4) |
| D18(--settings)·D20(세션 ID 거부)·D4·D5·D11(사람만 authority)과 모순 | 영수증 필드를 D20에 맞춤, iva head=llm, 첫 사례 훅은 --settings, E9로 D18 재결정 |
| 인수 확인 줄 부재를 "전달 실패"로 기록하면 입력 포함과 준수를 섞음 | "준수 미관측"으로 기록, 전달 증거는 세션 기록으로 분리(W1) |
| 잘못된 폴더 경고는 aaaNew 밖 폴더에서 불가능 | 한계로 명시(W1) |
| Stop "비어 있으면" 조건은 stale 내용을 통과시킴(LESSONS 4행 실패와 같음) | "파일 변경 있는데 CURRENT 미갱신이면 1회 block"으로(W4) |
| 미응답 시 기본값 진행이 Owner 전용 결정·D4와 충돌, INBOX 이중화 | 되돌릴 수 있는 순서 결정에만 허용, INBOX 하나로(W6) |
| 요청 필드 12→8에서 DEPENDENCIES·MUTATION이 설명 없이 빠짐 | 10필드로 복원(W2) |
| SUB_PLN 계획대비 확인을 없앴는데 대체 장치가 없음. iva "선택"과 "1회"가 모순 | ADMIT 기록에 계획대비·미결·필요 검증 3칸 필수, iva 필수 조건 명시(W2·W3) |
| PMO 통합 기능·ARCH 심사 기능을 맡을 곳이 없음 | Owner 커밋(D15)·작업대별 CURRENT 작성자·iva 설계 검증으로 나눔(§3) |
| R01 "rsch·pln 확정"은 오기 | "현재 논의한 역할, rsch는 조건부"로(§2, E1) |
| 수용 기준 3개에 판정 조건 없음. 실패 주입·환경 변수 정리 누락 | 기준별 통과 조건, 기준 5(실패 주입) 추가, ADMIT 기준은 저장소가 생긴 뒤로 분리(§6) |
| 추가 항목: 동시 작성자, 반환 뒤 자가 착수 금지, 개정 기록, R07·R08 쓰기 주체, R03 실행 옵션 | 앞의 셋은 반영(§3.2, W2-6). 나머지는 아래 미결 |

남은 미결:
- `requirements/` 쓰기 주체. rsch는 요구 채택 금지인데 폴더가 rsch 안에 있다.
- 작업대 전체 검색·모바일 요약 경로(R07).
- OAuth 직결·Pi 경로의 작업대 지정·관문 접점(R03).
- Codex 상위 AGENTS.md 로딩 여부, Codex 훅 실동작.
- 앱 대화형 세션의 Stop 발화 조건.
- SUB_PLN 확인·ARCH 심사의 실제 실패 예방 효과(AAA 교환 실패 분포 미조사).
