# Pro 의뢰서 P1 — 로컬 메모 저장소와 관리 엔진의 구조 (v1.0)

- 상태: **v1.0 완성. 입력은 커밋 `2506468` 고정 링크. 아직 보내지 않음.**
- 작성: 2026-10-17, AAA/NEW/RSCH/MEM_STRG
- 입력 전달: Owner 결정(2026-10-17) "mem_strg를 커밋·푸시하고 커밋 고정 링크로 의뢰서를 완성하세요." → 커밋 2506468be2eb117a602f3f8222c53b975d2cafec

---

아래가 Pro 챗에 보낼 본문입니다.

```text
ACT_ID: MEM_STRG-PRO-P1-STORAGE-ENGINE-ARCH-20261017-001
의뢰자: Owner (작성: aaaNew 연구 채널 AAA/NEW/RSCH/MEM_STRG)
입력 커밋: AofSpds/aaaNew@2506468be2eb117a602f3f8222c53b975d2cafec (§8 링크는 모두 이 커밋에 고정. main 최신을 읽지 말 것)
답변 언어: 한국어. 식별자·제품명·논문명은 원문 그대로.
성격: 한 번에 끝내는 조사 의뢰. 이어서 묻기 없음. 최종 설계안은 요구하지 않음. 선택지 비교와 조건부 권고까지.

## 1. 무엇을 만드는가
Owner가 운영하는 여러 도메인(저장소 여러 개)이 공통으로 쓸 "에이전트 메모 로컬 저장소"와 그 저장소를 관리하는 "엔진"을 만든다. 이 의뢰는 그 저장 구조를 고르기 위한 선행 조사다.

## 2. 사용 환경과 고정 제약
- Windows 11 PC(HANAL). 같은 PC에서 Claude Desktop 세션 여러 개와 Codex 세션이 동시에 읽고 쓴다. 다른 기기(jwDev)도 있고, 그쪽 dev 폴더는 Google Drive 미러로 보고됐다.
- 세션마다 역할이 있다(예: <도메인>/<프로젝트>/PLN, PMO, RSCH, ARCH). 역할마다 CURRENT(덮어씀), ROADMAP(자기 범위), ARCHIVE(지난 CURRENT 누적)를 둔다. 역할 CURRENT를 모아 도메인 CURRENT를 만든다(롤업).
- Git에는 참조값만 둔다(코드, 설계 정본, 증거, Owner 원문 장부, 정식 요청·회신). 자주 고치는 메모는 로컬 저장소에 둔다. 로컬 저장소는 내재화(외부 서비스 지양)하고 PR마다 Git에 백업한다.
- 아무것도 지우지 않는다. 키·시크릿은 어디에도 쓰지 않는다.
- 동기: 한 도메인(RHS)에서 메모 한 줄을 고칠 때마다 Git 병합을 반복해 하루에 main 병합 36회(전체 65회), 저장소 사본 20개가 생겼다.

## 3. 지금까지의 결과 (우리 실측, HANAL, Python 3.13 표준 라이브러리, SQLite 3.50.4)
- S1 저장 형태(갱신 1만 건, 역할 20개):
  · 파일 덮어쓰기+사본: 6.42 ms/건, 파일 10,022개
  · 역할별 jsonl 추가 전용+SQLite 투영: 0.24 ms/건, 파일 42개, Git 백업은 추가 줄만(+2,000/−0)
  · SQLite 단독: 0.06 ms/건, 바이너리 1개
  → 임시 권고: jsonl 원장 + SQLite 투영(재생성 캐시) + 생성 Markdown view(읽기 전용).
- S2 동시 쓰기(프로세스 8·16개 동시):
  · 파일을 읽고 고쳐 통째로 저장: 기록 36–54% 손실
  · 같은 jsonl에 잠금 없이 추가: 15–23% 손실 + 깨진 줄
  · 잠금 파일 / 프로세스별 파일 / SQLite WAL: 손실 0
  · 잠금을 잡은 프로세스를 죽이면 잠금은 즉시 풀림
  → 임시 권고: 역할별 스트림 + 스트림마다 잠금 파일 + 쓰기는 CLI 하나.
- S3 롤업: 쓰기마다 도메인 view 재생성(중앙값 8.4 ms/건, 1만 건). 고정 머리 칸 8개(role, session, state, updated, now, next, waiting_for[종류 붙은 대상], owner_wait).
- S0 그래프 규모(SQLite 재귀 CTE, 기록이 최근 2,000건 안의 1–3개에서 파생된다고 가정):
  · 1만 건: 출처 전부 1.8 ms
  · 10만 건: 115 ms
  · 100만 건: 1.36 s
  · 어느 규모든 출처를 끝까지 따라가면 이력의 70–80%가 딸려 나온다.
  → 해석: 제한 없는 전이 추적은 엔진 문제가 아니라 의미 문제. 따라갈 범위 규칙이 엔진 선택보다 먼저.

## 4. 반영해야 할 선행 연구 (요약)
- Byul(Owner의 relation-first 세계 모델 연구):
  · 관계가 기본 단위다. View는 원천을 표현하는 파생 관계 묶음이다. 캐시·저장은 구현 결정이지 세계 변경이 아니다.
  · View의 성능에는 원천 재구성 가능성과 구분 보존이 들어간다. 보존 계약·손실 프로필(preserved/collapsed/discarded)을 남긴다.
  · 존재·가시성·활성·보존·초기화·보관·논리삭제·물리삭제는 서로 다른 상태다.
  · 원천을 삭제하면 파생 상태를 선택적으로 다시 계산한다. 과거 사건은 남는다.
  · 합성은 View 조건부이고, 자동 전이 폐쇄가 아니다.
  · Causal Set·Petri·Event Structure는 후보 계열일 뿐 정본이 아니다.
  · 하나의 범용 동적 그래프 runtime은 비권고다(deep review 후보 문서).
  · prior-art 우선순위: P0 Provenance, IVM, lenses, Causal Set, Petri / P1 RDF, Datalog / P2 Event Sourcing.
- JEV(typesafe.ai System-One 계열 판단 모델, 호스팅 API):
  · AAA 결론은 "좁은 의미 신호의 비교 대상으로는 유효하나 입증된 Memory subsystem은 아님".
  · 쓸 만한 후보는 문맥 관련성 후보, 의미 중복·관계 제안, 요약 충분성 경고뿐이다. ID·시각·권한·삭제에는 쓰지 않는다.
  · 로컬 실측(Kev 0.8B)은 17/36이었고, 선택지 순서에 따라 판정이 바뀌었다.
- AAA 교차 프로젝트 기억 패턴:
  · 얇은 Current + 정확한 상세 회수, 근거를 보존하는 의존성 무효화, Source/인수 Delta 구분, 원천 보존 + 별도 교정본.
  · 기본값으로 그래프·스키마·공급자를 고르지 않는다. 단순 기준선과 반드시 비교한다.

## 5. 질문
Q1. 기록 형식: 위 원칙을 담는 최소 봉투(envelope)는 무엇인가.
    · 다룰 것: 기록 ID, 스트림·순번, 내용 digest, 출처 연결, 관계 종류, 손실 프로필, 상태(가시성…물리삭제), 교정(tombstone), 기록 시각과 유효 시각
    · 선행 사례와 함께 답한다: W3C PROV, 이벤트 소싱, XTDB 같은 bitemporal, Datomic 등
Q2. 따라갈 범위 규칙: 출처·영향 추적을 제한하는 방법과 그 선행 사례.
    · 후보: typed provenance, 깊이·종류 제한, view 조건부 합성, provenance semiring, IVM/DBSP, differential dataflow
    · 원천이 바뀌거나 지워졌을 때 선택적으로 재계산하는 방법
Q3. 층 구조 비교: 다음 안을 "이름 붙은 작업"별로 비교한다.
    · 안
      (a) jsonl 원장 + SQLite 투영 (현재)
      (b) (a) + 내장 그래프 투영
      (c) 그래프 DB를 정본으로
      (d) bitemporal 이벤트 저장소
    · 작업: 현재 상태 조회, 도메인 롤업, 출처 추적, 영향 범위·무효화, 검색(RAG), 아카이브 조회, 백업·복원
    · 각 안의 구축·유지 비용, 여러 프로세스 동시 쓰기, Windows 지원도 함께
Q4. 내장형 그래프 DB의 2026년 상태: 아래 후보 각각을 조사한다.
    · 후보: Kuzu(2025-10 archived)와 후속 포크(RyuGraph, LadybugDB), DuckPGQ, Oxigraph, FalkorDBLite, CozoDB, SQLite
    · 볼 것: 유지 상태, 마지막 릴리스, 라이선스, Windows·Python 지원, 동시 쓰기 제약, 파일 형식 안정성
    · "투영으로만 쓸 때" 이득이 나는 작업이 무엇인지도 답한다
Q5. 엔진 안의 검색 층(RAG)을 외부 서비스 없이 만드는 방법.
    · 후보: SQLite FTS5/BM25, 로컬 임베딩 모델, 하이브리드
    · 언제부터 필요한가(메모 규모·질문 유형)
    · 검색 결과의 최신성·권한 검사를 어떻게 붙이는가
Q6. JEV-like 판정을 외부 서비스 없이 쓸 수 있는가.
    · 로컬 대안과 품질 근거
    · 판정을 기록하는 형식: 분포 전체, 모델·질문·순서·원천 revision
    · 판정과 확정 변경을 분리하는 방법
Q7. 우리 임시 결과(§3)에 대한 반박: 틀렸거나 빠진 위험이 있으면 근거와 함께 쓴다.

## 6. 하지 말 것
- 특정 제품을 채택한다고 결정하지 않는다. 비교와 조건부 권고만 한다.
- 우리 저장소에 쓰지 않는다. 설치·배포를 안내하는 데서 그치고 실행을 요구하지 않는다.
- 저자·공급자가 보고한 수치를 독립 검증으로 쓰지 않는다.

## 7. 답변 형식
- 질문마다 4칸: 찾은 것 / 선택지 표 / 조건부 권고 / 모르는 것
- 근거마다 등급과 날짜를 붙인다: [공식 문서] [논문] [저장소·릴리스] [2차 출처] [추정]
- 마지막에 "우리가 다음에 실측할 것" 5개 이내. 무엇을, 어떤 조건으로, 무엇을 보면 판단이 바뀌는지.
- 길이: 질문당 핵심 위주. 전체를 한 번에 끝낸다.

## 8. 입력 자료 (커밋 2506468be2eb117a602f3f8222c53b975d2cafec 고정)
- https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S1_STORAGE_FORM.md
- https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S2_CONCURRENT_WRITES.md
- https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S3_ROLLUP.md
- https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S0_SOURCES.md
- https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S0_BYUL_JEV_EXTRACT.md
- https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/archive/2026-10-17_BTSR_MEMORY_RESEARCH.md
```
