# REQ-001 중간 반환 01 — 로컬 메모 저장소와 관리 엔진 연구

- FROM: AAA/NEW/RSCH/MEM_STRG · TO: RHS/DPM (RETURN_TO) · 참고: AAA/NEW/RSCH/BTSR
- 작성: 2026-10-17 · 상태: **중간 반환**입니다. 최종 반환은 S8 설계안 뒤인데, S8은 이번 진행에서 하지 않습니다(Owner).
- 기준 커밋: AofSpds/aaaNew `2506468`(연구 자료), `8771f1f`(Pro 의뢰서 v1.0). 두 커밋 모두 origin/main에 푸시했습니다.

## result

- **목적이 넓어졌습니다** (Owner 개정 1·2): RHS 전용이 아닙니다. Owner의 모든 도메인이 공통으로 쓸 **로컬 저장소와 그 저장소를 관리하는 엔진**을 만들고, Byul 최신 연구·JEV·그래프 DB 등을 반영합니다. RHS는 첫 적용 사례입니다.
- **임시 권고** (확정 아님):
  1. 저장 형태: 역할별 jsonl 추가 전용 원장을 정본으로 둡니다. SQLite는 재생성 캐시, Markdown은 생성 view(읽기 전용)입니다.
  2. 동시 쓰기: 스트림마다 잠금 파일을 두고, 쓰기는 CLI 하나로만 합니다.
  3. 롤업: 쓰기마다 도메인 CURRENT를 다시 만듭니다. 고정 머리 칸은 8개이고, 기다리는 대상에는 종류를 붙입니다(`role:` `verifier:` `owner:` `external:`).
  4. 그래프는 정본이 아니라 투영으로 둡니다. 엔진을 고르기 전에 **출처를 어디까지 따라갈지 정하는 규칙**이 먼저입니다.
  5. JEV는 저장 기술이 아닙니다. 호스팅 API라 "외부 서비스 없음"과 충돌합니다. 후보 역할은 문맥 관련성, 의미 중복 제안, 요약 충분성 경고 3개뿐입니다.
- **깊은 조사는 Pro 챗에 맡깁니다** (Owner 방침). 의뢰서 2건이 완성됐고, 아직 보내지 않았습니다.
  - P1: 저장소·엔진 구조. 기록 봉투, 추적 범위 규칙, 층 구조 4안, 내장 그래프 DB, 로컬 RAG, 로컬 JEV-like
  - P2: 운영. 아카이브, Git 참조·백업·복원, 여러 기기·Drive, 저장소 위치·권한, 모바일 열람, 기존 메모 이전

## evidence (모두 커밋 2506468 기준)

| 근거 | 핵심 수치 | 등급 |
| --- | --- | --- |
| [S1_STORAGE_FORM](../research/S1_STORAGE_FORM.md) | 갱신 1만 건: 파일 방식은 파일 10,022개, jsonl은 42개. Git 백업은 추가 줄만(+2,000/−0) | 실측 |
| [S2_CONCURRENT_WRITES](../research/S2_CONCURRENT_WRITES.md) | 프로세스 8·16개: 덮어쓰기 36–54% 손실, 잠금 없는 추가 15–23% 손실·깨진 줄. 잠금 파일·프로세스별 파일·SQLite는 손실 0 | 실측 |
| [S3_ROLLUP](../research/S3_ROLLUP.md) | RHS 시뮬 10-17 시나리오의 문제 5가지 해소. 쓰기 + 재생성 중앙값 8.4 ms | 실측(시제품) |
| [S0_SOURCES](../research/S0_SOURCES.md) | SQLite 재귀 CTE: 10만 건 115 ms, 100만 건 1.36 s. 제한 없는 출처 추적은 이력의 70–80%를 끌어옴. Kuzu는 2025-10 archived | 실측 + 웹 |
| [S0_BYUL_JEV_EXTRACT](../research/S0_BYUL_JEV_EXTRACT.md) | Byul 원칙 12, JEV 처분 M01–M12, 지금 설계와 어긋나는 점 7 | 문서 요약 |
| [archive/BTSR](../archive/2026-10-17_BTSR_MEMORY_RESEARCH.md) | BTSR 메모리 연구 22건을 참조값(6b19bb0·sha256)으로 인수 | 문서 요약 |

## delta

- 새 프로젝트 작업대 `projects/mem_strg/rsch` (BTSR이 옮김). 구 경로 `bootstrap/rsch_mem_strg`는 쓰지 않습니다.
- 요청 개정: [REV1](../requests/REQ-001_REV1_OWNER_SCOPE.md)(모든 도메인 공통), [REV2](../requests/REQ-001_REV2_OWNER_GOAL.md)(Byul·JEV·그래프 DB로 새 저장 체계)
- bootstrap 원본은 옮기거나 복사하지 않았습니다. 참조 아카이브만 만들었습니다.
- 계획: [PLAN_PRELIM_AND_PRO](../PLAN_PRELIM_AND_PRO.md). 의뢰서: [P1 v1.0](../pro/P1_STORAGE_ENGINE_ARCH_REQUEST_v1.0.md), [P2 v1.0](../pro/P2_OPERATIONS_REQUEST_v1.0.md)

## open

1. Pro 의뢰를 누가 보낼지 (Owner 결정 대기). 아직 보내지 않았습니다.
2. 저장소가 비공개라면 Pro가 GitHub 링크를 읽을 수 있는지 [미확인]
3. Byul 최신본: 로컬 main과 deep-review 브랜치(2026-08-26)를 기준으로 했습니다. 더 새 판이 있는지는 [미확인]
4. S4–S7 초벌(대안 표 + 질문)은 아직 하지 않았습니다.
5. Owner 결정 후보:
   - S1-a 저장 형태, S1-b memory-store와의 관계
   - S2-b 작업 폴더 밖 저장 시 권한 처리
   - S3-c 역할 등록부 주인

## learnings

- 같은 파일을 두 세션이 고치면 한쪽이 사라집니다. 2026-10-17 18:20 이 작업대 CURRENT.md에서 실제로 일어났습니다 (MEM_STRG와 BTSR). 그래서 작업대당 작성 세션은 1개라는 규칙을 실제로 지켜야 합니다.
- Windows에서 파이썬 추가 모드는 여러 프로세스가 쓸 때 원자적이지 않았습니다. "추가만 하면 안전하다"는 가정은 틀렸습니다.
- 자동 권한 검사는 `;`로 묶은 명령을 허용 규칙과 다르게 봅니다. 푸시는 단독 명령으로, 허용 규칙은 도구마다(Bash/PowerShell) 따로 넣어야 합니다.

## next

1. Owner가 Pro 전송 방법을 정하면 P1·P2를 보냅니다(동시 가능).
2. Pro의 답을 받으면 이 채널이 검토(채택·한계·정정)하고 `research/`에 기록한 뒤 RHS/DPM에 요약합니다.
3. 그사이 S4–S7 초벌을 만듭니다(대안 표와 질문까지만).
