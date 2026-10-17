# MEM_STRG — P1 저장 구조·엔진 아키텍처 선행 조사

- ACT_ID: **MEM_STRG-PRO-P1-STORAGE-ENGINE-ARCH-20261017-001**
- 의뢰자: Owner / AAA/NEW/RSCH/MEM_STRG
- 작성·조사 기준: 2026-10-17 (저장: 2026-10-18 KST)
- 고정 입력: **AofSpds/aaaNew@2506468be2eb117a602f3f8222c53b975d2cafec**
- 범위: 기록 envelope / 출처·영향 추적 / 층 구조 / 내장 그래프 DB / RAG / JEV-like / S0–S3 실측 반박
- 성격: 선행 조사·조건부 권고. **제품·최종 설계 미확정.**
- 변경 범위: 이 연구 문서 신규 추가만. 입력 실측·기존 문서 수정 없음.
- 근거 표기: **[공식 문서] [논문] [저장소·릴리스] [2차 출처] [추정]**. 각 항목에 날짜 또는 2026-10-17 조회일 기재.
- 주의: 공급자·저자의 성능 수치를 AAA 환경의 독립 실측으로 취급하지 않음.

## 요약

현재의 **(a) 역할별 jsonl 원장 + SQLite 투영 + 생성 Markdown view**는 계속 비교할 기준선으로 타당하다. 다만 원장의 확정 내구성, 논리적 충돌, S3 동시 롤업, 백업·복원 검증까지 충족했다는 뜻은 아니다. **SQLite append-only 정본 + PR 때 결정적 JSONL export**도 빠진 대조군으로 포함한다. 그래프 DB 추가는 특정한 출처·영향 계산의 이득이 입증되는 경우에 한한다. **Bitemporal은 저장 제품과 별개로 구현 가능한 시간 의미론**이다. [추정] 2026-10-17

입력은 아래 6개 고정 경로와 거기에 연결된 실측 코드로 한정했다.

1. [S1_STORAGE_FORM.md](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S1_STORAGE_FORM.md)
2. [S2_CONCURRENT_WRITES.md](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S2_CONCURRENT_WRITES.md)
3. [S3_ROLLUP.md](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S3_ROLLUP.md)
4. [S0_SOURCES.md](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S0_SOURCES.md)
5. [S0_BYUL_JEV_EXTRACT.md](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S0_BYUL_JEV_EXTRACT.md)
6. [2026-10-17_BTSR_MEMORY_RESEARCH.md](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/archive/2026-10-17_BTSR_MEMORY_RESEARCH.md)

---

## Q1. 기록 형식: 최소 envelope

### 찾은 것

**W3C PROV**는 Entity–Activity–Agent, derivation, revision, invalidation을 구분하는 provenance 모델이다. 여러 입력을 사용한 변환을 하나의 Activity로 표현하면 단순 source ID 나열보다 입력 역할을 정확히 보존할 수 있다. 그러나 저장 봉투 전체, append 순서·충돌·시간 정책까지 정하지는 않는다. **[공식 문서] 2013-04-30** — [PROV-DM](https://www.w3.org/TR/prov-dm/).

**Event Sourcing**은 불변 사건을 남기고 취소·교정을 새 사건으로 기록하며 조회 상태를 투영으로 만든다. 스키마 진화, 중복 재시도, 동시 변경 충돌, 재생성 결정성은 별도 구현 책임이다. **[공식 문서] 2026-03-28** — [Microsoft Event Sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing).

**XTDB**의 system time과 valid time은 시스템이 무엇을 언제 알았는지와 사실의 업무상 유효 기간을 구분한다. **[공식 문서] 2026-10-17 조회** — [XTDB key concepts](https://docs.xtdb.com/concepts/key-concepts.html).

**Datomic**은 transaction 이력과 as-of/history 질의를 제공하지만 업무상 valid time이 저절로 bitemporal로 생기는 것은 아니며 필요하면 모델링해야 한다. **[공식 문서] 2026-10-17 조회** — [Datomic transactions](https://docs.datomic.com/transactions/model.html), [filters](https://docs.datomic.com/reference/filters.html).

### 선택지 표

아래는 모든 기록에 무조건 똑같은 대형 스키마를 강제하기보다 **공통 봉투 + 사건 종류별 부속 정보**라는 후보이다. **[추정] 2026-10-17**

| 항목 | 최소 후보 | 별도로 보존할 구분 |
|---|---|---|
| 형식·사건 | schema_version, event_type | CURRENT/ROADMAP/교정/철회/View 생성, 읽기 변환 규칙 버전 |
| 기록·대상 | event_id, subject_id | 사건 ID와 변경 대상 ID 분리; 필요하면 revision ID. 같은 내용도 서로 다른 사건일 수 있음 |
| 스트림·순서·재시도 | stream_id, seq, command_id, expected_revision(필요 시) | seq는 스트림 내부 순서. 다기기에는 writer/device 또는 stream epoch 필요. 중복 제거와 동시 충돌 검사는 다름 |
| 내용·digest | payload 또는 불변 내용 참조, digest_algorithm, content_digest, canonicalization_version | 원문 바이트 digest와 정규화 내용 digest 분리. digest만으로 원문 복원 불가능 |
| 출처·관계 | 정확한 source revision, relation_type, 필요 시 입력 역할·본문 범위·activity_id | mentions / derived_from / corrects / depends_on 구별. Git은 repo/commit/path/blob, 원장은 stream/event/revision |
| View·손실 | view_spec_revision, generator_revision, 입력 revisions, loss_profile_ref | preserved/collapsed/discarded가 **무엇에 대해** 적용되는지. View의 discarded는 원장 삭제가 아님 |
| 상태 | 상태 축별 변경 사건 | 존재, 가시성, 활성, 보존, 보관, 논리적 철회, 물리적 가용성, 초기화/epoch 구분 |
| 교정·tombstone | target_revision, 변경 종류, 이유, 후속 revision | 수정·철회는 후속 사건으로 남김. 과거 사건은 보존 |
| 시간 | recorded_at, valid_from, valid_to 또는 미지정 | 기록 시각과 유효 시각 분리; 경계 규칙 명시. 벽시계만으로 전역 정렬 불가 |
| 주체·정책 | 작성 주체·역할·세션 ID, policy revision(필요 시) | 선언된 역할과 검증된 권한은 다름. 키·시크릿 기록 금지 |

JSON digest는 바이트 정규화 규칙을 먼저 고정해야 한다. RFC 8785 JCS 자체는 Unicode NFC 정규화를 하지 않는다. NFC + Python sort_keys는 별도 계약이지 JCS와 동일하지 않다. **[공식 문서] 2020-06** — [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785).

### 조건부 권고

PROV 전체나 범용 그래프 스키마를 매 기록에 강제하지 않고, **공통 봉투 및 파생·교정·상태 사건의 부속 정보**를 비교한다. 관계를 개별 교정·인용해야 한다면 관계 자체도 식별 가능한 기록으로 다루는 방식을 비교한다. [추정] 2026-10-17

“그때의 CURRENT”만 필요하면 기록 이력으로 출발할 수 있다. “나중에 알게 된 교정을 기준으로 과거 유효 상태를 조회”해야 한다면 system/valid 시간 의미론이 필요하다. 별도 temporal 제품 채택과는 구별한다. [추정] 2026-10-17

### 모르는 것

subject 단위를 문서/항목/주장/관계 중 어디까지 분해할지, 재구성 가능성의 강도(원문·동일 View 바이트·의미 동등성), 기기별 시계·충돌 정책, 보존 계약의 실행 가능한 검사 수준은 미확정이다.

---

## Q2. 출처·영향을 따라갈 범위 규칙

### 찾은 것

**사람에게 출처를 설명하는 범위 제한과, View를 정확히 무효화하는 의존성 계산은 다른 계약**이다. 설명은 깊이·종류·출력 수로 줄일 수 있지만 무효화에 그 제한을 무조건 적용하면 변경 대상이 누락될 수 있다. 계산 예산이 부족하면 미처리 범위를 dirty/pending으로 남겨야 한다. [추정] 2026-10-17

PROV에서도 Activity의 입력·출력 연결만으로 모든 Entity 사이의 derivation이 자동 성립하지는 않는다. Byul의 View 조건부 합성과 일치한다. **[공식 문서] 2013-04-30** — [PROV-DM](https://www.w3.org/TR/prov-dm/).

### 선택지 표

| 방법 | 선행 사례 | 유용한 작업 및 한계 |
|---|---|---|
| Typed provenance | PROV use/generation/derivation/revision/invalidation. **[공식 문서] 2013-04-30** | mentions/related_to와 실제 계산 depends_on 구분. 설명 및 무효화에 다른 관계 집합 사용 |
| 깊이·종류·시간·출력 제한 | 정책·frontier 관리. **[추정] 2026-10-17** | 설명 요청에 적합. 중단 사실·이유·남은 frontier를 반환하고 무효화 완료로 표시하지 않음 |
| View 조건부 합성 | **Relational Lenses**, View↔원천 변환 법칙. **[논문] 2006-06** — [PODS paper](https://www.cis.upenn.edu/~bcpierce/papers/dblenses-pods.pdf) | 허용된 View 조건과 보존 계약이 맞을 때만 합성. 자연어 요약에 임의의 역변환 보장 부여 불가 |
| Provenance semiring | 대안 증명은 +, 공동 기여는 ×. **[논문] 2007-06** — [Provenance Semirings](https://www.cs.ucdavis.edu/~green/papers/pods07.pdf) | 예: ab+c를 “a,b가 함께 또는 c”로 해석. 신뢰도 점수는 아님. 부정·집계·자연어는 의미론 확대 필요 |
| IVM/DBSP | **DBSP: Automatic Incremental View Maintenance for Rich Query Languages**. **[논문] 2023** — [VLDB](https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf) | 필터·집계·롤업의 Delta 계산 후보. 삭제·MIN·TOP K 등에 추가 상태/재계산 필요 가능. LLM 요약은 별개 |
| Differential Dataflow | 반복·재귀 및 논리적 시간 기반 증분 처리. **[논문] 2013-01** — [CIDR](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf) | 반복 경로 계산 후보. 논리적 시간은 기록 시각·업무 valid time과 다름. 운용 부담 검증 필요 |

### 조건부 권고

선택적 재계산은 다음 단계를 비교 기준으로 둔다. **[추정] 2026-10-17**

1. 내용 변경/교정/철회/권한 변경/역할 등록/표시 변경을 별도 Delta로 구별.
2. 정확한 source revision과 질의 조건을 의존성으로 기록. 입력 목록뿐 아니라 부재·범위·시간 조건 포함.
3. 역방향 의존성에 따라 관련 View/파티션을 invalidation. 계산 중단 대상은 dirty/pending.
4. 일관된 입력 snapshot으로 재계산. 입력 revision 목록만으로 transaction 일관성을 가정하지 않음.
5. 게시 직전에 generation과 입력 revision을 재검사하여 오래된 결과의 덮어쓰기를 막고 계약에 필요한 후속 영향 전파.

**부재에 대한 의존성**이 핵심이다. “대기 항목 없음”은 현재 읽은 행 외에 쿼리 조건에도 의존하고, “모든 역할” 롤업은 신규 역할 등록에 의존한다. 과거 derived_from 간선만 역추적하면 누락된다. [추정] 2026-10-17

### 모르는 것

실제 관계 유형별 fan-out, 부정·집계 질의 비중, 요약 재실행 빈도, View stale 허용 시간 미확정. semiring/DBSP/Differential Dataflow가 단순 역색인+재계산보다 나은지는 실측 전 불명이다.

---

## Q3. 층 구조 비교: 이름 붙은 작업

### 찾은 것

**(d) bitemporal은 (a)~(c)와 논리적으로 배타적이지 않다.** jsonl 사건과 SQLite 투영에도 두 시간 축을 모델링할 수 있다. 그래프를 관계의 기본 표현으로 삼는 것과 그래프 DB를 정본으로 삼는 것도 다르다. [추정] 2026-10-17

### 선택지 표

아래 표는 작업 적합성을 나타내며 실측 성능 순위는 아니다. **[추정] 2026-10-17**

| 이름 붙은 작업 | (a) jsonl + SQLite 투영 | (b) + 내장 그래프 투영 | (c) 그래프 DB 정본 | (d) bitemporal 중심 |
|---|---|---|---|---|
| 현재 상태 조회 | head·상태 SQL, 간단 | 추가 이득 대체로 작음 | 현재 revision 선택 규칙 별도 | 기록/유효 시각 기준 지정 |
| 도메인 롤업 | SQL 집계·결정적 생성 | 관계 조건 복잡할 때만 후보 | 집계·게시 일관성 문제 남음 | 시점별 롤업 재현에 강점 |
| 출처 추적 | 역색인·재귀 CTE 시작점 | typed path 복합 조건 후보 | 그래프 중심 작업에 자연스러움 | 당시 알려진 출처와 교정 후 출처 구별 |
| 영향 범위·무효화 | 의존성·dirty 테이블 | 복잡한 역방향 패턴 후보 | 저장만으로 무효화 의미 해결 안 됨 | 유효 시간 구간 영향 표현 |
| 검색 / RAG | FTS·벡터 투영 추가 | 검색 후 제한된 관계 확장 | 본문 검색·권한 검사는 별도 | 과거와 현재 검색 시간 필터 |
| 아카이브 | 사건 replay+snapshot | 과거 관계 구조 조회 후보 | 이력 보존 규칙 따로 필요 | “그때 알던 것/지금 아는 과거” |
| 백업·복원 | 원장·원천·계약 보존 후 replay | 그래프 재생성 가능 | DB snapshot+논리 export와 이력 검증 | 두 시간 축/교정 이력 보존 필요 |

| 안 | 구축·유지 비용 [추정] | 동시 쓰기 제약 | Windows 관점 |
|---|---|---|---|
| (a) | 중간; append 확정·복구·replay·투영 진도 관리 자체 책임 | stream 잠금과 SQLite transaction 조정, 두 저장물 사이 실패 복구 | 현재 HANAL 실측 기반 |
| (b) | (a)보다 높음; 색인 갱신·재구축·호환 비용 | 그래프 DB 단일 소유 프로세스 제약 후보 많음 | wheel 설치와 다중 파일 공유는 별개 |
| (c) | 높음; 기록·교정·정본 export를 그래프 transaction에 맞춤 | 그래프 서버 동시 클라이언트와 다중 프로세스 직접 열기 구별 | native Windows 커널·Python client 별도 |
| (d) | 시간 의미론만 추가면 중간, 전용 temporal 엔진 운영 시 상승 가능 | 전용 제품의 transaction·writer 모델 의존 | 의미론은 이식 가능, 엔진은 별도 검증 |

SQLite WAL은 동일 PC의 여러 프로세스에서 접근할 수 있지만 동시에 commit하는 writer는 하나이다. **[공식 문서] 2026-08-25** — [SQLite WAL](https://www.sqlite.org/wal.html).

### 조건부 권고

- (a): 현재 상태·롤업·정확한 회수가 중심이면 기본 비교선.
- (b): 특정 출처·영향 질의에서 쓰기/재구축 비용까지 포함한 이득이 확인되면 비교.
- (c): 그래프 질의가 핵심 작업이라는 근거와 이력·복원·동시성 충족이 확보되면 비교.
- (d): 소급 교정·감사가 반복되면 시간 의미론을 먼저 비교. 전용 제품은 이를 구현·운영하는 비용에서 이득이 있을 때만 후보.

모두 **[추정] 2026-10-17**.

### 모르는 것

조회 구성비, p95 허용 지연, 여러 스트림의 원자적 업데이트 필요성, jwDev 독립 쓰기 여부, 허용 투영 지연이 미확정이다.

---

## Q4. 내장형 그래프 DB의 2026년 상태

### 찾은 것

**Windows Python 패키지 제공과 여러 프로세스가 하나의 DB 파일을 동시에 직접 열 수 있다는 뜻은 다르다.** 릴리스 버전은 2026-10-17에 확인한 공개 배포 기준이며 Python wrapper와 엔진 자체를 혼동하지 않는다.

### 선택지 표

| 후보 | 공개 유지·최신 배포 | 라이선스 | Windows/Python 지원 |
|---|---|---|---|
| Kuzu | **2025-10-10 archived**, kuzu **0.11.3** (2025-10-10) | MIT | Windows x64 CPython 3.13 wheel. **[저장소·릴리스]** [PyPI](https://pypi.org/project/kuzu/) |
| RyuGraph | 후속 포크, ryugraph **25.9.2** (2025-12-06), 이후 Python 릴리스 미확인 | MIT | Windows x64 CPython 3.13 wheel. **[저장소·릴리스]** [PyPI](https://pypi.org/project/ryugraph/) |
| LadybugDB | 후속 포크, ladybug **0.21.2** (2026-10-01) | MIT | Windows x64/ARM64 CPython 3.13 wheel. **[저장소·릴리스]** [PyPI](https://pypi.org/project/ladybug/) |
| DuckPGQ | 연구 확장 진행, community descriptor **1.0.0**. GitHub에 배포 Release 없음; 그 날짜 미확인 | MIT | DuckDB 확장. Windows·Python·DuckDB 현재 조합 가용성 미확정. **[저장소·릴리스] 2026-10-17 조회** [descriptor](https://github.com/duckdb/community-extensions/blob/main/extensions/duckpgq/description.yml), **[공식 문서]** [DuckPGQ](https://duckdb.org/community_extensions/extensions/duckpgq) |
| Oxigraph | pyoxigraph **0.5.11** (2026-09-02) | MIT 또는 Apache-2.0 | Windows x64 CPython 3.13 wheel. **[저장소·릴리스]** [PyPI](https://pypi.org/project/pyoxigraph/) |
| FalkorDBLite | falkordblite **0.10.0** (2026-05-02) | wrapper BSD 계열, FalkorDB core **SSPLv1**, Redis 포함 구성 별도 확인 | Python ≥3.12; 확인한 wheel Linux/macOS. native Windows 미확인; WSL과 구별. **[저장소·릴리스]** [PyPI](https://pypi.org/project/falkordblite/), [source](https://github.com/FalkorDB/falkordblite), [core LICENSE](https://github.com/FalkorDB/FalkorDB/blob/master/LICENSE.txt) |
| CozoDB | cozo-embedded **0.7.6** (2023-12-11); 장기간 공개 릴리스 공백 | MPL-2.0 | Windows x64 cp37-abi3 wheel; Python 3.13 실제 작동 미검증. **[저장소·릴리스]** [PyPI](https://pypi.org/project/cozo-embedded/) |
| SQLite | **3.54.1** (2026-10-16) | Public Domain | Windows와 Python sqlite3. 실제 연결 SQLite 버전 별도 확인. **[저장소·릴리스]/[공식 문서]** [changes](https://www.sqlite.org/changes.html), [copyright](https://www.sqlite.org/copyright.html) |

DuckPGQ는 2026-10-17 조회한 공식 Graph Queries 안내에서 아직 DuckDB 1.5.x에 사용할 수 없으며 1.4.4를 사용하라고 적고 일부 기능을 미완성으로 설명한다. descriptor의 버전만으로 호환성을 확정할 수 없다. **[공식 문서] 2026-10-17 조회** — [DuckDB Graph Queries](https://www.duckdb.org/docs/current/guides/sql_features/graph_queries).

| 후보 | 동시 접근·파일 형식 이관 | 투영에만 사용할 때의 이득 작업 후보 [추정] |
|---|---|---|
| Kuzu | 하나의 RW 소유자 또는 다수 RO 소유자; writer+별도 reader 프로세스의 동시 직접 접근 전제 불가. archive로 유지 위험. **[공식 문서] 2026-10-17 조회** [concurrency](https://kuzudb.github.io/docs/concurrency/) | Cypher/path 비교 기준 |
| RyuGraph | 단일 RW 또는 다수 RO. export/import 경로는 있으나 무변환 영구 파일 호환 보장 미확인. **[공식 문서] 2026-10-17 조회** [concurrency](https://docs.ryugraph.io/concurrency/), [migrate](https://docs.ryugraph.io/migrate/) | typed path·여러 관계 패턴 |
| LadybugDB | 동일한 소유 모델. 다른 세션은 소유 프로세스를 통한 접근 후보. export/import 경로 있으나 포크 간 상호 파일 호환 가정 금지. **[공식 문서] 2026-10-17 조회** [concurrency](https://docs.ladybugdb.com/concurrency/), [migrate](https://docs.ladybugdb.com/migrate/) | provenance·복합 영향 패턴 |
| DuckPGQ | DuckDB: 단일 RW 프로세스 또는 다수 RO. 본체 저장 형식과 확장 ABI/PG metadata 별도 관리. **[공식 문서] 2026-10-17 조회** [concurrency](https://duckdb.org/docs/current/connect/concurrency) | 관계 테이블에 SQL/PGQ, 배치 그래프 분석 |
| Oxigraph | RocksDB store 소유 프로세스 필요. 다른 프로세스 writer 활동 중 read_only 오픈은 undefined behavior. RDF dump/reload와 major migration 필요. **[공식 문서] 2026-10-17 조회** [store](https://pyoxigraph.readthedocs.io/en/stable/store.html), [migration](https://pyoxigraph.readthedocs.io/en/stable/migration.html) | PROV/RDF·SPARQL·named graph |
| FalkorDBLite | Python이 하위 Redis/FalkorDB 서버를 관리; 다수 client는 **동일 서버**에 연결. persistence는 Redis/module 버전에 의존. **[저장소·릴리스] 2026-10-17 조회** [source](https://github.com/FalkorDB/falkordblite) | 로컬 서버를 허용한 경우 복수 클라이언트 그래프 질의 |
| CozoDB | Python client thread-safe와 복수 프로세스 embedded DB 열기는 다름; 후자는 문서상 허용되지 않음. pre-1.0 형식 호환 보장 없음. **[저장소·릴리스] 2026-10-17 조회** [pycozo](https://github.com/cozodb/pycozo), [cozo](https://github.com/cozodb/cozo) | Datalog·재귀 규칙 |
| SQLite | 여러 프로세스 가능, WAL writer 1개. SQLite 파일 장기 호환 근거 강함; 애플리케이션 스키마/WAL 별도. **[공식 문서] 2026-10-17 조회** [WAL](https://www.sqlite.org/wal.html), [onefile](https://www.sqlite.org/onefile.html) | head/rollup/역색인/제한 재귀 CTE/FTS 통합 |

### 조건부 권고

- Cypher/property graph → RyuGraph/LadybugDB 계열 비교.
- PROV/RDF 교환·SPARQL → Oxigraph.
- SQL 기반 관계 배치 분석 → DuckPGQ(버전부터 확인).
- 규칙·재귀 중심 → CozoDB.
- 로컬 서버 허용 → FalkorDBLite.
- Kuzu → archive 상태를 반영한 재현 대조군.

하나의 그래프 투영 파일을 각 세션에서 마음대로 RW로 여는 방법이 아니라, 필요하면 **단일 소유 프로세스 + 질의 인터페이스**의 관리 비용까지 비교한다. **[추정] 2026-10-17**

### 모르는 것

HANAL 설치·실행·실파일 reopen, 장기 upgrade/downgrade, CPU/RAM·동시 transaction 실패 양상, DuckPGQ 현재 Windows 바이너리 조합, 포크 유지 지속성은 미실측·미확정이다.

---

## Q5. 엔진 안의 외부 서비스 없는 검색(RAG)

### 찾은 것

도입 기준은 사건 개수보다 **검색 질문 유형과 chunk 수**이다. 작은 자료에도 말바꾸기·의미 중복 검색이 필요할 수 있고, 큰 자료라도 exact ID/역할 조회는 SQL이면 충분할 수 있다. [추정] 2026-10-17

SQLite FTS5의 unicode61은 한국어 형태소 분석기가 아니다. trigram MATCH는 3개 Unicode 문자 미만 검색어를 매칭하지 않으며 external-content FTS에는 본문/색인 동기화 책임이 있다. 두 음절·조사·혼합 식별자를 시험해야 한다. **[공식 문서] 2026-10-17 조회** — [SQLite FTS5](https://www.sqlite.org/fts5.html).

### 선택지 표

| 안 | 필요한 질문 유형 | 비용/제약 |
|---|---|---|
| SQL+FTS5/BM25 | exact ID/역할/상태 및 원문 키워드, archive 회수 | 가장 단순한 대조군. 한국어 tokenizer·별칭·prefix 검증 |
| 로컬 임베딩 | 말바꾸기·유사 개념·한영 혼합 | 모델·chunker version/재색인, vector 보관 비용 |
| 하이브리드 | exact+semantic 동시 필요 | BM25와 cosine 원점수 단순 합산보다 rank fusion 비교 |
| 하이브리드+reranker | 후보 recall은 충분하나 순위가 부정확할 때 | 추론 지연 추가. 후보 누락은 rerank로 해결 불가 |

**[추정] 2026-10-17.**

로컬 임베딩의 대조 후보 **multilingual-e5-small**은 MIT, 384차원, 최대 512 tokens, query:/passage: 접두어를 명시한다. 다국어 모델이라는 사실은 후보 선정 근거이지 AAA 한국어 품질 검증은 아니다. **[저장소·릴리스] 2026-10-17 조회** — [model card](https://huggingface.co/intfloat/multilingual-e5-small/blob/main/README.md).

CPU 실행은 ONNX를 비교 가능하나 pooling/normalization을 포함한 실제 출력 검증 필요. **[공식 문서] 2026-10-17 조회** — [Sentence Transformers efficiency](https://sbert.net/docs/sentence_transformer/usage/efficiency.html).

**Reciprocal Rank Fusion**은 다른 점수 척도를 직접 더하지 않는 rank 결합 사례. **[논문] 2009-07** — [RRF](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf).

### 조건부 권고

먼저 FTS가 실패하는 질의를 모아 임베딩의 추가 recall과 관리 비용을 비교한다. 특정 건수에 도달했다는 이유만으로 ANN/vector DB를 채택하지 않는다. 10만×384 float32의 원시 벡터는 약 **153.6 MB**이고 메타데이터/인덱스는 별도다. [추정·계산] 2026-10-17

최신성·권한 검사: (1) 검색 항목에 source_revision/chunker_revision/model_revision/투영 진도 기록; (2) 현재 조회와 과거 조회 분리; (3) 비동기 임베딩 게시 전에 source revision 재확인; (4) 검색 본문을 모델에 넘기기 **전** 권한 검사, 제공 직전 재확인; (5) 투영 지연이 있으면 따라잡거나 snapshot 기준을 명시한다. [추정] 2026-10-17

권한 밖 결과를 전역 Top-K 이후 제거하면 recall이 낮아질 수 있으므로 허용 범위 내 검색을 비교한다. 또한 한 Windows 계정이 모든 원장 파일에 직접 접근할 수 있는 상태에서 엔진의 역할 필터만으로 OS 수준 격리를 보장한다고 주장하면 안 된다.

### 모르는 것

한국어 recall, 반복 CURRENT 중복 chunk 비율, CPU 추론 비용, 원천 변경 중 검색 품질, HANAL에서 모델/runtime의 재현성 미실측.

---

## Q6. 로컬 JEV-like 판정

### 찾은 것

좁은 관련성·중복·경고 판정은 외부 API 없이 구성 가능하다. **그러나 JEV와의 품질 동등성은 입증되지 않는다.** AAA 자체 Kev 0.8B 17/36과 선택지 순서 민감성은 자동 확정 적용의 근거가 부족하다는 관찰이다. **[저장소·릴리스] 2026-10-17, 고정 입력 S0_BYUL_JEV_EXTRACT/BTSR 요약**.

LLM-as-judge의 위치 편향과 선택지 분포 편향은 외부 연구에서도 보고되었다. 이것은 로컬 모델의 AAA 성능을 증명하지 않으며, 질문·선택지 순서·전체 점수 분포를 보존해야 할 근거다. **[논문] 2025-12, 2025-07** — [Judging the Judges](https://aclanthology.org/2025.ijcnlp-long.18/), [CalibraEval](https://aclanthology.org/2025.acl-long.808/).

### 선택지 표

| 대안 | 좁은 신호 | 근거·제약 |
|---|---|---|
| 규칙/digest/필드 비교 | exact 중복·revision·필수 항목 누락 | 자동 ID·권한·시간 검사 기본선. **[추정] 2026-10-17** |
| embedding/reranker | 관련 문맥·의미 중복 후보 | **bge-reranker-v2-m3**, Apache-2.0, 다국어 관련성 후보. 관련성≠사실성/승인. **[저장소·릴리스] 2026-10-17 조회** [card](https://huggingface.co/BAAI/bge-reranker-v2-m3) |
| 로컬 NLI | entailment/contradiction/neutral 후보 | **mDeBERTa-v3-base-mnli-xnli**, MIT. 모델 카드 XNLI 평가에 한국어가 없어 품질 직접 검증 필요. **[저장소·릴리스] 2026-10-17 조회** [card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli) |
| 로컬 instruction model | 관계 제안·요약 충분성 경고 | **Qwen3-4B-Instruct-2507**, Apache-2.0, llama.cpp Windows 실행 경로 존재. 품질·CPU latency 미실측. **[저장소·릴리스]/[공식 문서] 2026-10-17 조회** [card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), [build](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) |

### 판정 기록 부속 정보

| 그룹 | 기록 |
|---|---|
| 대상 | source IDs/revisions/digests/본문 범위, 주입된 문맥의 revisions |
| 질문 | 질문 원문 또는 불변 참조, prompt/rubric revision, label ID·뜻 |
| 순서 | 원천·문맥·선택지의 실제 제시 순서, 순열 실행마다 별도 event |
| 모델/실행 | model weights digest·revision, tokenizer, quantization, runtime/backend, decoding, seed |
| 전체 산출 | 각 label의 raw score/logprob, 계산 방법, 확률화한 전체 분포, parse failure·missing |
| 보정·안정성 | calibration revision, 순열별 결과, abstention 이유 |
| 상태 | judgment_id, proposed/accepted/rejected/abstained/expired, 승인·후속 event 참조 |

모델이 스스로 말한 confidence, sigmoid/softmax 산출값, 검증 데이터로 보정된 확률은 서로 구분해야 한다. 독립 label의 확률에 합=1을 강제하지 않는다. Calibration의 중요성은 **On Calibration of Modern Neural Networks**를 참조. **[논문] 2017-08** — [ICML](https://proceedings.mlr.press/v70/guo17a.html).

### 조건부 권고

판정은 제안 이벤트로 남기고, **확정 변경은 별도 사건**으로 남긴다. 승인 주체·정책·expected_revision을 검증하며, 원천 revision이 바뀌면 오래된 판정을 자동 적용하지 않는다. 거절·기권도 보존한다. 허용 후보는 (1) 문맥 관련성, (2) 의미 중복·관계 제안, (3) 요약 충분성 경고까지다. ID·시간·권한·삭제·확정 상태의 결정권은 모델에 두지 않는다. **[추정] 2026-10-17**

순서 변동 시 abstain 정책을 비교할 수 있으나, 순서가 같아도 정답률이 입증되는 것은 아니다.

### 모르는 것

AAA 한국어 판정 품질, 오류별 위험도, 기권 기준, 실제 full-distribution 추출 가능 여부, quantization 영향, 확률 보정 근거 미확정.

---

## Q7. S0–S3 임시 결과에 대한 반박

### 찾은 것

**SQLite WAL-reset 버그에 HANAL에서 시험한 3.50.4가 포함된다.** 공식 문서는 영향 가능 범위를 3.7.0–3.51.2로, 수정 버전을 3.51.3 및 backport 3.44.6·3.50.7로 명시한다. 다중 연결의 쓰기/checkpoint가 겹칠 때 드물게 손상될 수 있다. S2에서 실제로 발생했다는 증거는 아니지만, 후속 시험은 수정된 실제 연결 라이브러리를 사용·기록해야 한다. **[공식 문서] 수정 릴리스 2026-03-13, 문서 갱신 2026-08-25** — [SQLite WAL](https://www.sqlite.org/wal.html).

### 선택지 표

| 쟁점 | 코드·문서에서 확인한 사실 | 해석 변경·필요 검증 |
|---|---|---|
| S1 0.24 vs 0.06 ms | JSONL은 fsync 없는 append/close. SQLite WAL은 synchronous=NORMAL. JSONL 측정 쓰기에 SQLite 투영 갱신 없음; rollup은 :memory: 전량 재생성. **[저장소·릴리스] 2026-10-17** [S1 코드](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/s1_form_bench.py) | 동일 내구성·end-to-end 속도 비교는 아님. 조건 통일 필요 |
| S2 손실 0 | 검사는 파싱과 (w,i) 중심. payload 완전성·재시도·같은 CURRENT 충돌 미검증. kill 재획득 타이머는 p.kill(); p.wait() 후 시작. **[저장소·릴리스] 2026-10-17** [S2 코드](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/s2_concurrency_bench.py) | “해당 시험의 예상 ID 누락 0”으로 한정. 0.03 ms는 kill-to-unlock이 아님 |
| 논리적 lost update | lock append가 직렬화되어도 두 세션이 오래된 동일 CURRENT 기반으로 전체 값을 쓸 수 있음. **[추정] 2026-10-17** | lock/transaction 안에서 expected_revision 비교, 충돌 정책 필요. CLI 1개≠프로세스 1개 |
| S3 concurrent rollup | role lock 해제 후 regenerate, 각 stream head에 공통 snapshot 없이 접근, current.md 직접 overwrite, 성능 루프 순차. flag는 두 역할의 상호 기다림만 검사. **[저장소·릴리스] 2026-10-17** [S3 코드](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/s3_rollup_proto.py) | 부분 읽기·오래된 generation 게시가 **가능한 경쟁 조건**, 발생률은 미실측. snapshot/게시 순서/원자적 교체 필요 |
| JSONL 꼬리 복구 | S3 reader는 incomplete final line을 건너뛰지만 그 뒤 append 시 복구 프로토콜 없음. **[저장소·릴리스] 2026-10-17** | 원본 바이트 보존+새 segment/복구 event 비교 |
| S0 규모 일반화 | 1만 ancestry 1,686(약 17%). 100만 시 source 2만 중 1만8천이 생성상 기록과 연결되지 않음. 결과 측정 count(*)이지 원문 회수 아님. **[저장소·릴리스] 2026-10-17** [S0 코드](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/s0_graph_scale_bench.py) | 70–80%를 모든 규모·실데이터에 일반화 금지. 의미 기반 범위 규칙은 여전히 우선 |
| Git binary 비교 | “SQLite 1개”는 변경 binary 수이며 파일 총수는 S1에서 25개. Git GC 후 SQLite 2,007 KiB, JSONL 3,235 KiB 보고. **[저장소·릴리스] 2026-10-17** [S1 문서](https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S1_STORAGE_FORM.md) | 줄 diff의 가독성과 저장 효율 구분. SQLite 정본 + 결정적 JSONL export 추가 |
| Git/Drive/PR 백업 | OS lock은 jwDev의 복제 파일까지 보장하지 않음; 텍스트 Git merge는 event 순서/중복/인과 검증이 아님. PR 사이 기록은 미백업 손실 구간. **[추정] 2026-10-17** | 기기별 immutable segment, 수입 정책, snapshot 경계, 복원 검증 비교 |

S1과 S2를 직접 동기화 내구성 결과로 혼동하지 않는다. Python flush와 os.fsync는 다르며, SQLite WAL NORMAL은 갑작스러운 전원 손실 시 최근 commit이 되돌아갈 수 있다. S2는 synchronous를 명시·기록하지 않아 S1 설정과 같다고 가정하지 않는다. **[공식 문서] 2026-10-17 조회** — [Python os](https://docs.python.org/3.13/library/os.html), [SQLite PRAGMA](https://www.sqlite.org/pragma.html).

Git merge=union은 합쳐진 줄 순서가 임의일 수 있다고 명시된다. 해당 driver에 대한 경고이며 기본 Git merge 전체로 일반화하지 않는다. **[공식 문서] 2026-10-17 조회** — [gitattributes](https://git-scm.com/docs/gitattributes).

### 조건부 권고

임시 (a) 권고를 **비교 가설로 유지**하되, 다음 검증 우선순위를 속도보다 내구성/충돌/복원에 둔다. SQLite append-only 정본 + PR에 결정적 JSONL export하는 대조군은 사건 추가와 CURRENT 변경의 한 transaction 처리라는 장점 및 export/replay 비용을 함께 비교할 수 있다. **[추정] 2026-10-17**

운영 중 SQLite 파일의 단순 복사와 안정적인 snapshot은 다르다. SQLite backup API 또는 VACUUM INTO를 이용한 snapshot 생성 경로가 있다. **[공식 문서] 2026-10-17 조회** — [backup](https://www.sqlite.org/backup.html), [how to corrupt](https://www.sqlite.org/howtocorrupt.html).

JSONL에도 stream별 확정 경계·digest·schema·View 계약·필요한 원천을 포함한 manifest가 필요하다. Git commit/digest만 존재하고 원문이나 Git 객체를 잃으면 원천 보존을 만족하지 않는다. STALE 표시는 시간이 지남에 따라 바뀌므로 쓰기 시 롤업만으로는 충분하지 않을 수 있다. **[추정] 2026-10-17**

### 모르는 것

HANAL의 실제 storage flush 동작, Windows kill/전원손실 차이, Drive 동기화 경로와 방식, 실운용 충돌·손상 발생률, PR 사이 허용 손실 구간, 원문 장기 보존 보장이 미확정이다.

---

## 우리가 다음에 실측할 것 (5개 이내)

아래는 **미실행 실험 제안**이며 기존 S0–S3 값과 혼동하지 않는다. **[추정] 2026-10-17**

| 실험 | 조건 | 판정 변경 기준 |
|---|---|---|
| **1. 확정·내구성·충돌 동일 조건 비교** | HANAL 8/16 프로세스, 1/10KB 동일 payload. JSONL과 수정 SQLite의 fsync/synchronous 조건 기록. append·투영·응답 사이 중단, 재시도, 같은 CURRENT revision 병행 변경. kill vs 전원손실 구분 | 응답 완료 기록의 누락·중복·내용 변형·조용한 덮어쓰기. SQLite 정본+JSONL export가 계약을 더 단순히 충족하면 정본 판단 변경 |
| **2. 동시 롤업** | 20/200 역할 병행 수정, 계산 지연으로 순서 역전 유도, 신규 역할·3개 이상 대기 순환·시간 경과 STALE·소급 교정 | 최신 generation 역행·부분 파일·snapshot 위반. 전체 재생성 비용 높으면 증분/배치/조회 시 생성 비교 |
| **3. 백업·복원·다기기 합류** | 쓰기 중 snapshot/replay, 중복·누락·역전 segment 수입, 두 기기 독립 변경 후 합류 | 사건 수만 아니라 digest/head/time 조회/관계 회수 일치. 손실 창·복원 시간 허용 범위 초과 시 방식 변경 |
| **4. 그래프의 이름 붙은 작업** | 실제 typed 관계 분포 1만/10만/100만, 제한 출처 설명·정확한 영향·부정/집계 의존성. SQLite와 후보를 동등 정답으로 비교 | 조회 p95 + 쓰기/무효화/재구축·RAM을 포함해 (b)의 실질 이득 확인 |
| **5. 한국어 검색·로컬 판정 추가 가치** | exact ID·두 음절·말바꾸기·부정·과거 결정 보류 평가셋. FTS/규칙 vs embedding/hybrid/reranker/judge. 순열 및 source/권한 변경 포함 | recall/precision, 잘못된 관계, abstain의 정확도·커버리지, calibration, p95. 기본선 대비 이득 없으면 모델 층 보류. 권한 밖·stale 본문 제공 시 연결부터 수정 |

---

## 상태·범위

- 확정된 제품 선정, 구현 승인, 설치/배포, 로컬 데이터 변경: **없음**.
- 기존 S0–S3 실측 원본 변경: **없음**.
- 본 문서는 연구 회신·비교 자료이며 Owner/PMO의 선택을 대신하지 않음.
- 근거 URL 중 공개 문서의 수정 시점이 고정되지 않은 경우 **2026-10-17 조회**로 표기했고, 입력 자료 6개의 의미는 지정 Git SHA에만 고정했다.
