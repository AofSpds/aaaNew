# 아카이브 — BTSR 메모리 연구 인수 (참조값 + 요약)

- 작성: 2026-10-17, AAA/NEW/RSCH/MEM_STRG
- 근거: Owner "btsr에서 잠시 연구한바 있는걸 이관 받으라는거예요." / "네 그곳은 그대로 두고 알아서 아카이브하라는거였어요"
- 방식: 원본은 `projects/bootstrap/` 아래에 그대로 둡니다. 여기에는 **참조값(경로·커밋·SHA-256 앞 12자리·바이트)과 요약**만 남기고, 복사본은 만들지 않습니다.
- 기준 커밋: aaaNew `6b19bb0`. 아래 파일은 모두 이 커밋에 있고, 작성 시점에 작업 사본 변경이 없었습니다 [실측].
- 요약 출처: Sonnet 서브에이전트 1명이 읽기 전용으로 추출했습니다. 원문을 모두 다시 대조하지는 않았습니다 [문서 요약].

## 1. 문서 목록

경로는 `projects/bootstrap/` 기준입니다.

| 경로 | 작성 | 날짜 | sha256(12) · 바이트 | 결론 한 줄 | 관련 |
| --- | --- | --- | --- | --- | --- |
| rsch/research/relation-engine/RELATION_ENGINE_PLAN_CLAUDE.md | Claude | 10-17 | 976cb116b93e · 20262 | jsonl 추가 전용 + SQLite 투영 + Git, 그래프 DB 없음, view 읽기 전용, 모델 점수로 변경 없음 | S1·S3·S4·S5 |
| rsch/research/relation-engine/DECISIONS_D1_D21_CLAUDE.md | Claude | 10-17 | 6697e6eebeb1 · 11779 | D1–D13 반박 검토(유지 8·변경 5·Owner 1) + D14–D21. 스트림 분할, 단일 CLI, `merge=union`, ULID, redact, 상대 경로 | S1·S2·S4·S5·S7 |
| rsch/research/relation-engine/JEVLIKE_GAP_CLAUDE.md | Claude | 10-17 | f529f9e48ac8 · 14618 | 로컬에 jevlike 엔진은 없음(Kev 호출 코드·프로토타입만). 본체는 저장소+스키마+검토 흐름 | 관계 엔진 |
| rsch/research/relation-engine/JEV_BYUL_COMPARISON_CLAUDE.md | Claude | 10-17 | 0e0678849eab · 14101 | AAA JEV-BYUL 선행 연구와 충돌 없음. 봉투·판정/변경 분리·결측 어휘·시간 역할을 가져옴 | 관계 엔진·S1 |
| rsch/research/sub-memory/INTAKE_CODEX.md | Codex | 10-14 | 139075fa70d9 · 2663 | 인수 기록. 저장 방식 미선정 | 관계 엔진 |
| rsch/research/sub-memory/RELATION_CASES_CODEX.md | Codex | 10-14 | d4ab22608ada · 10036 | 실제 3사례. 부분 중복은 병합 안 함, 역할이 다르면 공존 | 관계 엔진·S4 |
| rsch/research/sub-memory/JEVLIKE_CASE_01_DRAFT.json | 미상(Codex 추정) | 없음 | 6785567b7040 · 2513 | 첫 jevlike 평가 입력 초안. 192바이트에서 자르면 자식 역할이 사라짐 | 관계 엔진 |
| rsch/research/sub-memory/JEVLIKE_MEMORY_UTILITY_CODEX.md | Codex | 10-14 | c307b006f2de · 15243 | jevlike 계열 판정은 후보 제안용. 대체·삭제는 점수만으로 못 정함 | 관계 엔진 |
| rsch/research/sub-memory/MEMORY_PILOT_RESULTS_CODEX.md | Codex | 10-14 | ce0409e0300c · 9248 | Kev 0.8B 17/36, 규칙 16/16. 자동 병합 근거 부족 | 관계 엔진 |
| rsch/research/sub-memory/ORDER_SENSITIVITY_RESULTS_CODEX.md | Codex | 10-14 | 06b1e5f9f9e3 · 10228 | 선택지 순서가 판정을 바꿈(겹침 10/18). 정렬법 미확정 | 관계 엔진 |
| rsch/research/sub-memory/ORDER_SENSITIVITY_SURVEY_CODEX.md | Codex | 10-14 | 4d92227393be · 9660 | 외부 연구도 같은 방향 | 관계 엔진 |
| rsch/research/sub-memory/REVIEW_TRIAGE_STUDY_CODEX.md | Codex | 10-14 | 271166967db6 · 7790 | 재검토 분류 효용은 보이나 규칙 대비 모델 추가 효과 없음 | 관계 엔진 |
| rsch/research/sub-memory/R05_R06_REFINEMENT_CODEX.md | Codex | 10-14 | 63cf7f705ab3 · 14712 | 판정과 확정 변경 분리. 저장·동시 수정·보관 정책은 미정으로 명시 | S1·S2·S3·S4 |
| rsch/research/sub-memory/BYUL_GRAPH_RESEARCH_CODEX.md | Codex | 10-14 | 2896f08921fd · 9802 | Byul(79c00bf)에서 공통 view → 역할 view, 원자료 변경 시 파생 무효화. 그래프 DB 미채택 | S1·S3 |
| rsch/research/sub-memory/GRAPH_IMPLEMENTATION_STUDY_CODEX.md | Codex | 10-14 | d718aeb7eed1 · 17247 | 목록·Python 그래프·SQLite CTE 결과 같음. 이 규모에서 그래프 DB 근거 없음 | S1·S2·S4·S5 |
| rsch/research/sub-memory/EXTERNAL_MEMORY_SURVEY_CODEX.md | Codex | 10-14 | 279aa087769b · 21161 | Graphiti·Mem0·LightRAG 등 18묶음 비교. 패키지 채택은 비교 뒤 | S1·S4·S7 |
| rsch/research/memory-external/MEMORY_RESEARCH_CODEX.md | Codex | 10-14 | 9b7064fb54ea · 5102 | 저장 성공 ≠ 읽음 ≠ 준수. 짧은 진입점 + 상세 파일 | S1·S3·S5 |
| rsch/research/memory-external/MEMORY_CLINE_CODEX.md | Codex | 10-14 | e7f49c32e5e3 · 6801 | Cline Memory Bank 대입. 지침과 작업 기억 구분 | S1·S3 |
| memory-engine/README.md | 미상 | 10-17 | 8a407ddf8940 · 573 | 관계 엔진 코드 작업대 안내(코드 없음) | 관계 엔진 |
| memory-engine/CODING_STANDARDS.md | Claude | 10-17 | a21f8a189c96 · 6353 | 표준 라이브러리, 추가 전용, CLI 경유, 봉투 필드, 같은 파일 동시 수정 금지 | S1·S2·S5 |
| memory-store/README.md | 미상 | 10-17 | 3a651202704a · 528 | 기록은 CLI로만, `index.sqlite`·`records/local/` Git 제외 | S1·S2·S5 |
| rsch/memory/codex-rsch/LESSONS_CODEX.md | Codex | 10-14 | 5efa427b3a39 · 3341 | 저장·읽기까지 해야 이행. 완료 통보 때 상태도 갱신 (참고용, bootstrap 세션 메모) | S2·S3 |

## 2. 폴더 (Git 추적 여부)

| 경로 | 커밋 | 크기 | 파일 | 비고 |
| --- | --- | --- | --- | --- |
| rsch/research/sub-memory/graph-pilot-20261014/ | 6b19bb0 | 83 KB | 4 (추적 4) | study.py·dataset·results |
| rsch/research/sub-memory/memory-pilot-20261014/ | 6b19bb0 | 5.36 GB | 30,045 (추적 91) | Kev 실험 코드·데이터·runs. 나머지는 .venv·.cache(Git 제외) |
| rsch/research/sub-memory/backups/ | 없음 | 6.50 GB | 11 (추적 0) | 백업 zip, Git 제외 |

큰 Git 제외 자료는 옮기지 않습니다. `.venv`는 옮기면 다시 만들어야 하는데, 다시 만드는 것은 대규모 설치라 금지 사항입니다.

## 3. 이 채널 연구와 겹치는 점 [문서 요약]

- **S1**: D1 "jsonl + SQLite 투영 + 그래프 DB 없음"은 이 채널 S1의 B안과 같습니다. GRAPH_IMPLEMENTATION_STUDY도 이 규모에서는 그래프 DB 근거가 없다고 봤습니다. 다만 노드 32개 규모였습니다. Owner 목적 개정 2에 따라 S1′에서 다시 봅니다.
- **S2**: D15 단일 CLI와 CODING_STANDARDS "같은 파일 동시 수정 금지"가 S2 결론과 같은 방향입니다. 동시 쓰기를 실측한 문서는 없었습니다. 이 채널 S2가 처음입니다.
- **S3**: view는 원자료에서 아래로 생성하는 방식(공통 → 역할)만 있고, 역할 → 도메인 롤업은 정의가 없었습니다. 이 채널 S3가 처음입니다.
- **S4·S5**: D12·D16(만료 없음, redact tombstone, 거부 판정도 영속)은 S4 규칙의 전제가 됩니다. "PR마다 백업·복원"은 어느 문서에도 없습니다.
- **S6**: 여러 기기·Drive·모바일은 어느 문서에도 없습니다.
- **S7**: D21은 Git 안에서 가져오기만 다룹니다. Git 밖으로 옮기는 방법은 없습니다.

## 4. 문서 사이의 어긋남 [문서 요약]

- 저장 철학이 다릅니다. Codex 문서(MEMORY_RESEARCH·CLINE·LESSONS)는 손으로 고치는 Markdown+Git을 기억 본체로 보고, Claude 계획은 jsonl을 정본으로, MD는 생성 view로 봅니다.
- 계획 §8 기본값 가운데 D2·D3·D4·D9·D13은 DECISIONS에서 바뀌었습니다.
- JEVLIKE_GAP의 "검토 누락 0"은 ORDER_SENSITIVITY_RESULTS가 일반 보장이 아니라고 정정했습니다.
- 일부 파일에 옛 경로 표기가 남아 있습니다(`aaaNew\bootstrap\…`, `Agent_memory/…`).
