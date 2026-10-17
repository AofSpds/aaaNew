# JEV-BYUL 선행 연구와 현재 R06 대조

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 요청: 사용자 "jev-byul 문서 대조"
- 대조 대상: (A) AAA `projects/AAA/work/jev-byul-research/` (2026-09-26/27), HLOM `work/jev-byul-rsch-staging/`, ARCP R20 ↔ (B) 현재 [R05·R06](../../requirements/REQUIREMENTS_CODEX.md), [M01–M06](../sub-memory/R05_R06_REFINEMENT_CODEX.md), [구현 계획](RELATION_ENGINE_PLAN_CLAUDE.md)
- 읽기 수준: 핵심 문서 약 20편을 읽고 구조화했다(기록 계약·라벨 가이드·결정 옵션은 직접, 나머지는 위임 요약). 원문 40만 자 전체를 정독하지는 않았다. 파일은 수정하지 않았다.

**결론: 선행 연구는 "모델 판정 ≠ 정본 관계 ≠ 행동 권한"이라는 경계와 기록 계약을 설계 수준에서 세웠고, 실측은 없었다. 현재 R06과 방향이 같고 충돌은 없다. 다만 선행 연구가 다루지 않은 것이 둘 있다 — (1) 역할별 MD view 생성과 manifest, (2) 작업대 실행기로의 실제 전달. 현재 계획은 이 둘을 첫 성과로 잡았으므로 선행 연구의 빈칸을 메우는 위치다. 선행 연구에서 가져올 것은 기록 봉투·판정/변경 분리·터미널 결과·결측 상태 어휘이고, 가져오지 말아야 할 것은 Pair/Arbiter/Audit 전체 구조와 11개 기록 계약 전부다.**

## 1. 선행 연구가 무엇이었나

| 항목 | 내용 |
| --- | --- |
| 출발 | Owner 지시 "JEV와 BYUL 최신 연구 결과를 의뢰할 수 있어야 함" → SR-JEV-BYUL 채널. 이후 Owner 정정: 상위 목적은 **"BYUL과 JEV의 연구 결과를 이용해 AAA의 실제 메모리 개선 방향을 찾는다"** (`TOP_LEVEL_OBJECTIVE = AAA_MEMORY_IMPROVEMENT_FROM_BYUL_JEV`) |
| JEV 정의 | TypeSafe 상용 판단 모델(typed Choice/Score/Noul, 확률 출력). "JEV-like"는 그 능력 범주를 공개 기법으로 재현한 것(Laya, openjev-sglang 등). 원문: "OPEN JEV-LIKE IMPLEMENTATION != JEV REPRODUCTION" |
| BYUL 정의 | Relation-first 세계 모델. `RELATION: SOURCE → TARGET`, 목적별 view(FOLD/EXPAND), "SAME SOURCE != SAME VIEW". 상태 NON_NORMATIVE / NOT_VALIDATED |
| 산출 | Parent RESULT(아키텍처·포터블 스키마·500건 벤치마크 제안), RSCH(Pair/Arbiter/Audit, 기록 계약 11종), data-spec v0.1(가상 사례 48건, 지표 전부 NOT_RUN), AAA 측 R0(기억 표면 25개·공백 12개)·R0B(5개 프로젝트 패턴 27개)·R1–R3 |
| 상태 | `IMPLEMENTATION = NOT_AUTHORIZED`, `EMPIRICAL_MODEL_RUN = NOT_AUTHORIZED`, 본연구 `RESEARCH_NOT_COMMISSIONED`. ARCP R20: "별도 연구로 보존, ARCP 필수 구현 아님, 정책·admission·Optimizer로 정의 금지" (`DEFERRED_NONBLOCKING`) |
| 한 줄 결론 | "JEV/System-One is a credible capability class for narrow semantic signals, not a demonstrated AAA Memory subsystem"; 벤치마크 검토 결과 "No winner is selected" |

## 2. 일치하는 것 (현재 R06·M01–M06·계획과 같은 방향)

| 선행 연구 | 현재 | 비고 |
| --- | --- | --- |
| Judgment Graph ≠ Memory/World Graph. 모델 출력은 정본 관계가 아님 | M04 판정과 확정 변경 분리. 계획 §4 `judgment` ↔ `change` | 같은 원칙. 현재 계획은 "admission"을 `change` 기록 + 권한 필드로 단순화 |
| 흐름: 후보 검색 → 결정적 검사 → 판정 probe → RelationProposal → 검토 → 결정적 admission | 계획 §1 흐름: 후보 생성 → RuleJudge → Judge → 검토 큐 → change | 단계 수까지 같다 |
| "cheap semantic head"는 좁은 관계 질문에만. Arbiter 자체로는 부적합(W/H) | JEVLIKE_GAP: Kev는 후보 점수화 한 칸. 자동 병합 불가 | 선행 연구가 설계로 말한 것을 Kev 0.8B 실측(17/36, 순서 민감)이 뒷받침 |
| 한국어는 필수 local slice; 보정은 버전·head·데이터셋별 측정 | A10 한국어 평가 묶음, M06 허용 오류율 | 선행 연구의 "highest-value missing evidence"가 한국어 gold — 현재도 라벨 0건 |
| 병렬 질문의 논리 동일성 비보장(C2) | 질문 v2 결합 규칙에서 "질문 간 모순 → open" | 실측에서 L04가 정확히 이 모순을 보였다 |
| UNKNOWN을 학습 class로 할지 abstention으로 할지는 OPEN | 계획: `abstain_reason` 필드, RuleJudge 기본 보류 | 현재는 abstention 쪽으로 기본값. 선행 연구 Q2에 대한 암묵적 선택이므로 D-항목으로 올림(§5) |
| 관계 종류 초안 RELATED/SUPPORTS/REFINES/CONTRADICTS/SAME_REFERENT/SAME_SCOPE/SUCCESSOR/SUPERSEDES/INSUFFICIENT_EVIDENCE/UNKNOWN/multi-relation | 계획 §3 SUPPORTS/OVERLAPS/CONFLICTS_WITH/SUPERSEDES/SIMILAR_TO + open | 이름은 다르나 대응됨. 선행 Q1 "SUCCESSOR/SUPERSEDES를 모델 admission loop에서 제외"는 현재 "SUPERSEDES는 변경 기록으로만"과 동일 |
| 시간 역할 분리(occurred/recorded/valid/observed/judgment_created) | memory_rev.conditions.time, source_rev.recorded_at | 현재는 둘뿐. 선행 연구가 더 세밀 — §4에서 차용 |
| "hash·확률은 진실·권한을 입증하지 않는다"(R0B RF03) | 원칙 5 입력 포함/준수/효과 분리 | 같은 경계 |
| R0 F03: AAA의 가장 명확한 관측 문제는 "라우팅·패킷 사건의 반복 교정 실패"이지 기억 백엔드 결함이 아님 | R05 "재설명·재탐색·재작업을 줄이는 데 초점" | 둘 다 "저장소 교체"가 아니라 "교정이 다음 행동에 유지되는가"를 문제로 본다 |

## 3. 다른 것

| 축 | 선행 연구 | 현재 | 판단 |
| --- | --- | --- | --- |
| 구조의 중심 | 여러 View의 독립 판정(Pair) → Arbiter 종료 → Audit. 11개 기록 계약 | 단일 흐름: 규칙 → 판정 → 검토 큐 → 변경. 기록 7종 | 선행 연구의 Pair/Arbiter/Audit는 "서로 다른 해석을 어떻게 수렴시키나"에 대한 답이고, 현재 문제는 "한 작업대 안의 중복·충돌·대체"다. **Pair 구조는 가져오지 않는다.** 복수 Judge 비교는 평가 하네스에서만 |
| 행동 권한 | ActionAuthorityRecord, `eligible_to_execute` 5항 결합, 실행기 commit 재확인 | 범위 밖. 도구 실행 통제는 [runtime-intervention-research](../runtime/runtime-intervention-research/FINDINGS.ko.md)의 관문 | 현재 R06에 행동 권한은 없다. 다만 "판정 ≠ 권한"의 경계 문장은 change.authority 필드로 반영 |
| 평가 설계 | 500건 벤치마크 제안, 48건 가상 fixture(지표 NOT_RUN), 1% 미만 희귀 오류 bound에 ~299 negatives 필요 | 18쌍 실측(라벨 0건), 목표 라벨 30건 | 선행 연구는 크고 실행 안 됨, 현재는 작고 실행됨. 300/150/50 분할·변형 가족(ORDER, STALENESS…)·"frozen test에서 threshold tuning 금지" 규칙은 차용 |
| 기억 단위 | NodeRecord(원자료 locator·digest·scope·valid/effective time) | source_rev / memory_rev 분리 | 현재가 "원자료 개정"과 "기억 주장"을 두 기록으로 나눈 점이 더 명시적. 유지 |
| view | BYUL "Persona on TARGET side ⇒ human-friendly VIEW / RENDER PRIMITIVE = NOT ADMITTED"; Planning Context EXPERIENCE_PROJECTION/CONTEXT_MANIFEST 후보 | 역할별 MD view 생성 + manifest + 전달 직전 검사 + delivery_receipts | **선행 연구에 직접 대응 설계 없음.** 현재 계획의 단계 4가 빈칸을 메운다 |
| 실행기 전달 | 없음(R7 실증은 별도 권한) | 세션 기록에서 포함 증거, 훅 로그 | 선행 연구에 없음 |
| 중복 관리 | R0 5.5, DUPLICATED_SOURCE_ANCESTRY 변형 factor, P03 수준 | R06의 중심 문제. OVERLAPS{shared, unique_a, unique_b} | 선행 연구에서 전용 설계 없음 |
| 효과 측정 | R7 별도 권한, WBS-75 NOT_OBSERVED → 전부 미측정 | M06, 계획 §7 | 둘 다 아직 0. 현재 계획이 측정 위치를 지정한 점이 진전 |

## 4. 선행 연구에서 가져올 것 (계획에 반영)

1. **기록 봉투 최소 집합** — `record_id, record_type, schema_version, recorded_at, content_digest{algorithm, canonicalization, value}, source_refs[{uri, version_or_commit, digest, locator}], causal_parent_ids, lifecycle_status, supersession_or_correction_refs`. 계획 §2의 봉투를 이 이름으로 맞춘다. `sensitivity/access_profile`, `extensions`는 보류.
2. **Uncertainty 값 타입** — `raw_scores, score_semantics, option_set_and_order, calibration_ref, applicability_domain, abstention_reason`. 계획의 `judgment` 기록이 이미 같은 내용을 담고 있으므로 필드명만 맞춘다. "option-normalized 확률을 보정된 정답률로 재명명하지 않는다"는 규칙을 코드 주석이 아니라 `score_semantics` 필드값으로 남긴다.
3. **결측·실패 상태 어휘** — FAILURE / TIMEOUT / CANCELLATION / PARTIAL / NO_OUTPUT / NOT_INVOKED / UNAVAILABLE + `external_effect_state`. Judge 실행 영수증과 view 전달 영수증에 쓴다. "NO_OUTPUT은 부정 답이 아니다", "TIMEOUT을 NOT_INVOKED로 바꾸지 않는다"를 테스트로.
4. **검토 터미널 결과** — SELECT / DEFER / ASK_USER / BLOCK / ESCALATE. 계획 §4 검토 큐의 처리 결과 어휘로 그대로. "필수 검토 사유는 가중합으로 상쇄되지 않는다"는 선행 연구의 "audit finding never grants authority"와 같은 방향.
5. **시간 역할** — `occurred_at`(원자료가 말하는 사건 시점), `recorded_at`, `valid_from/valid_to`(적용 구간), `observed_at`. memory_rev.conditions.time을 이 넷으로 나눈다.
6. **판정 개정 규칙** — F0는 불변, 수정은 새 judgment + `revises`. 같은 답이라도 새 근거면 새 파생. 계획 §4 "거부된 판정도 지우지 않는다"에 덧붙인다.
7. **벤치마크 규칙** — 원문 가족 단위 분할, frozen test에서 threshold 조정 금지, raw와 보정 후 점수 둘 다 보존, 결정적 기준선 포함, 변형 가족(ORDER, CONFIDENCE_PRESENTATION, DUPLICATED_SOURCE_ANCESTRY, OMITTED_MINORITY_EVIDENCE, STALENESS). 계획 §6 평가 하네스에 반영.
8. **반증 항목(probe)** — "같은 digest라도 프롬프트·순서가 다르면 실행 출처는 다르다", "원자료 삭제 시 EXPAND는 unavailable을 보고하고 그럴듯한 재구성을 하지 않는다", "늦게 온 단순 이견은 닫힌 결정을 바꾸지 않는다". 수용 기준 목록에 추가.

## 5. 가져오지 않을 것과 이유

| 항목 | 이유 |
| --- | --- |
| Pair/Arbiter/Audit 3층 구조, PairDeliberation·DisagreementRecord·AuditFinding 기록 | 현재 문제(한 작업대의 중복·충돌·대체)에 복수 View 수렴이 필요하다는 근거가 없다. 선행 연구 스스로 "No universal Pair … is recommended"(R3 F09) |
| ActionAuthorityRecord·CapabilityEvidence·RuleEvaluation | 행동 권한·능력 증거는 R06 범위 밖. 도구 실행 통제는 실행기 훅 관문이 맡는다 |
| 4개 독립 surface(Canonical Data / MemoryGraphPort / GraphQueryPort / JudgmentPort) | 현재 규모에서 목록·SQLite로 충분(프로토타입 실측). 포트 분리는 저장소를 바꿀 때 |
| CalibrationProfile 기록 | Judge 비교가 시작되고 라벨이 생긴 뒤에. 지금 만들면 빈 기록 |
| 500건 벤치마크 전체 | 라벨 30건 목표가 먼저. 분할 비율과 규칙만 차용 |

## 6. 선행 연구가 남긴 OPEN 중 현재 계획이 암묵적으로 답한 것 → Owner 결정 항목으로 승격

계획 §8의 D1–D9에 다음을 추가한다.

| # | 선행 OPEN | 현재 계획의 암묵적 선택 |
| --- | --- | --- |
| D10 | UNKNOWN을 학습 class로 할지 abstention policy로 할지 | abstention(`abstain_reason`). RuleJudge 기본 보류 |
| D11 | head별 error budget(auto-proposal / human / hard block) | 자동 변경은 정확 규칙만(D4), 모델은 propose-only, hard block 없음 |
| D12 | Judgment Graph 영속 vs 임시 | 영속(judgment jsonl). 삭제 안 함 |
| D13 | Relation taxonomy freeze 시점 | 단계 2 완료 시 v1 고정, 이후 변경은 group_version으로 |

## 7. 현재 작업과의 관계 정리

- **R20 처분과의 관계**: ARCP는 "JEV-like를 별도 연구로 보존, 정책·admission·Optimizer로 정의하지 않음"이라고 했다. 현재 계획은 모델을 propose-only로 두고 admission(change)은 권한 필드가 결정하므로 **R20 처분에 부합**한다. AAA 쪽 "본연구 미발주(`RESEARCH_NOT_COMMISSIONED`)" 상태는 그대로이며, aaaNew의 이 작업이 그 발주를 대신한다고 주장하지 않는다.
- **선행 연구의 AAA 기억 표면(R0)**: M2 admission·Planning Context(mandatory context, exact expansion, invalidation, Experience applicability)가 후보로 이미 있으나 live 미입증. aaaNew는 그 코드를 이전하지 않고 새로 세우는 중이므로, 단계 1·4를 만들 때 Planning Context의 `CONTEXT_MANIFEST`/`EXPERIENCE_PROJECTION` 개념과 이름이 겹치는지 한 번 대조할 가치가 있다(미수행).
- **미확인**: 48건 fixture(CASES.jsonl)의 한국어 포함 여부, r123 r1/r2 세부, R4·R5·R8 미수행 상태 이후 진행 여부. 이 문서는 2026-09-27 이후 선행 연구가 더 진행되지 않았다고 가정하지 않는다.

## 8. 근거 (고정 버전)

- AAA 게시: `2aec5f06` (SUB_PLN 003), PLAN_ID `AAA-JEV-BYUL-MEMORY-IMPROVEMENT-v1.0-20260926`, R0 base `b22e2603`, R0B `4fc5d5ed`→`983e0a24`, R1–R3 authority `e18eb312`
- HLOM: Parent RESULT `897d923b`→`d7facadf`, RSCH RESULT `d64df785`, data-spec 승인 `7a7c59d9`
- BYUL main `79c00bfe`(Codex 조사와 동일), 전달 synthesis 126 `1129af74`
- 외부: Jev 1.13.0, Laya 0.3.20, openjev-sglang `5f633dcc`, 벤치 sysone-bench `1ac3650a`, jev-phishing-bench `1d56e8c6`
- 문서 경로: `C:\Users\ms1pk\dev\AAA\projects\AAA\work\jev-byul-research\{20260926,20260927}\`, `C:\Users\ms1pk\dev\human-llm-operating-model\work\jev-byul-rsch-staging\{PARENT_RESULT.md, BYUL_SYNTHESIS.md, rules-lineage-schema.md, pair-arbiter-audit.md, provider-benchmark.md, data-spec\*}`, `C:\Users\ms1pk\dev\AAA\workspaces\arcp-pmo-triage-20261009\sources\Q.md:216,287,331-333,552`
