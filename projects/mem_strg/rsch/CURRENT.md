# CURRENT — mem_strg / rsch

- 상태: ACTIVE · 2026-10-18
- 현재 work act: REQ-001 — Pro 외주 연구 1차(P1 저장 구조·P2 운영)를 받아 검토하고 S0–S3에 정정을 반영함. 파일을 주제 폴더 5개 + 소주제 등록부로 재배치함
- 다음 한 단계: Owner 결정 D-a–D-f → 다음 실측 1(확정·내구성·충돌)·2(동시 롤업)
- 막힘: 없음. D-c(저장소 위치·설정)와 D-f(SQLite 수정판 설치)는 Owner 결정이 필요
- 작성 세션: AAA/NEW/RSCH/MEM_STRG (local_edac275f-…, 2026-10-17 개설)

## 목적 (Owner 2026-10-17)

Byul 최신 연구·JEV·그래프 DB 등을 이용해 **모든 도메인 공통의 로컬 저장소와 그 저장소를 관리하는 엔진**을 만듭니다. RHS는 첫 적용 사례입니다. 이 작업대는 연구를 맡고, 구현은 mem_strg의 별도 작업대가 맡습니다(위치 미정).
- 근거: [REV1](requests/REQ-001_REV1_OWNER_SCOPE.md) · [REV2](requests/REQ-001_REV2_OWNER_GOAL.md)
- 방침: 혼자 깊이 조사하지 않습니다. 이 채널은 수집·기록·초벌·검토를 하고, 깊은 조사는 Pro 챗에 맡깁니다 → [계획](PLAN_PRELIM_AND_OUTSOURCE_CLAUDE.md)
- 설계안(S8)은 이번 진행에서 하지 않습니다(Owner).

## 주제별 위치 (`research/<주제>/`, 파일 이름 끝에 출처)

| 주제 | 핵심 문서 | 상태 |
| --- | --- | --- |
| storage-structure 저장 구조 | [STORAGE_FORM_CLAUDE](research/storage-structure/STORAGE_FORM_CLAUDE.md)(S1) · [의뢰 v1.0](research/storage-structure/STORAGE_ENGINE_REQUEST_v1.0_CLAUDE.md) · [Pro 답](research/storage-structure/STORAGE_ENGINE_RESPONSE_GPT_PRO.md) | jsonl+투영은 기준선, 보완 후 채택 |
| concurrent-writes 동시 쓰기 | [CONCURRENT_WRITES_CLAUDE](research/concurrent-writes/CONCURRENT_WRITES_CLAUDE.md)(S2) | 스트림+잠금+CLI, 보완 후 채택 (`expected_revision`·fsync 필요) |
| rollup 롤업 | [ROLLUP_CLAUDE](research/rollup/ROLLUP_CLAUDE.md)(S3) | 쓰기마다 재생성, 보완 후 채택 (동시 게시 문제) |
| operations 운영 | [의뢰 v1.0](research/operations/OPERATIONS_REQUEST_v1.0_CLAUDE.md) · [Pro 답](research/operations/OPERATIONS_RESPONSE_GPT_PRO.md) | 아카이브·백업·기기·위치·모바일·이전. 대부분 Owner 결정 대기 |
| prior-research 선행 연구 | [SOURCES_CLAUDE](research/prior-research/SOURCES_CLAUDE.md)(S0) · [BYUL_JEV_EXTRACT_CLAUDE](research/prior-research/BYUL_JEV_EXTRACT_CLAUDE.md) | 그래프는 투영 후보, 추적 범위 규칙이 먼저 |

- 소주제 등록부: [research/TOPICS.md](research/TOPICS.md) (소주제 → 폴더·문서·출처, Owner 승인 2026-10-18)

- 검토: [reviews/STORAGE_ENGINE_OPERATIONS_REVIEW_CLAUDE.md](reviews/STORAGE_ENGINE_OPERATIONS_REVIEW_CLAUDE.md)
  - 정정 12건
  - 항목별 판정: 우리 결과 14건, Pro 제안 20건 (채택 / 보완 후 채택 / 보류 / 채택 불가 / 참고)
  - Owner 결정 후보 D-a–D-f
- 반환: [returns/REQ-001_INTERIM_01.md](returns/REQ-001_INTERIM_01.md) (확정 기록이라 고치지 않음. 본문 링크는 커밋 5408ece 기준 경로)
- 인수 아카이브: [archive/INDEX.md](archive/INDEX.md)

## 남은 단계

| 단계 | 내용 | 상태 |
| --- | --- | --- |
| S1′ | 저장 계층 재검토 (원장·투영·그래프·판정 층) | Pro P1 답으로 1차 정리. 실측 1·2 뒤 다시 봄 |
| S4 | 아카이브 (시점·이름·목록) | Pro P2 Q1을 바탕으로 초벌 |
| S5 | Git 참조값·PR 백업·복원 | D-a 뒤 |
| S6 | 여러 기기·모바일 | D-b·D-d 뒤 |
| S7 | 기존 메모 이전 | Pro P2 Q6 양식으로 도메인별 목록 |
| S8 | 통합 설계안 | 이번에는 하지 않음 |

- 공통 제약: 외부 서비스 없음, 키·시크릿 금지, 삭제 없음, 상대 경로
- 원천 읽기: RHS·bootstrap·Byul·AAA는 읽기만 합니다
- 지난 판: [archive/2026-10-17_CURRENT_scope-v1.md](archive/2026-10-17_CURRENT_scope-v1.md), 그 뒤의 판은 Git 이력(5408ece 등)
