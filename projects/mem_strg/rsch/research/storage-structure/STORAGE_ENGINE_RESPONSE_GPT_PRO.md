# Pro 답변 원문 — P1 저장 구조 선행 조사

- ACT_ID: MEM_STRG-PRO-P1-STORAGE-ENGINE-ARCH-20261017-001
- 의뢰서: [P1 v1.0](STORAGE_ENGINE_REQUEST_v1.0_CLAUDE.md) · 입력 커밋 AofSpds/aaaNew@2506468
- 보낸 사람: Owner (2026-10-17 21:34, ChatGPT 프로젝트 "AAA_NEW_RSCH_MEM_STRG", 대화 "저장 구조 선행 조사")
- 처리: Pro, "22m 36s 동안 처리함"(화면 표시). 실제 모델은 화면 표시만 확인했고, 그 이상은 확인하지 않았습니다 [미확인].
- 대화 URL: https://chatgpt.com/g/g-p-6acef0baa5448191827e7448f85ac439-aaa-new-rsch-mem-strg/c/6ad36b64-6a58-83ee-a388-3d9c2bd00ea7
- 기록: 2026-10-18, AAA/NEW/RSCH/MEM_STRG
  - 방법: 오른쪽 브라우저의 답변 DOM을 Markdown으로 바꿔 옮겼습니다(읽기만 함).
  - 표와 링크 모양은 변환 과정에서 달라졌을 수 있습니다. 본문은 고치지 않았습니다.
- 이 채널의 검토(채택·한계·정정)는 별도 문서에 씁니다. 이 파일은 원문 기록입니다.

---

# MEM_STRG 저장 구조 선행 조사

**ACT_ID: MEM_STRG-PRO-P1-STORAGE-ENGINE-ARCH-20261017-001**
**조사 기준일: 2026-10-17**

현재의 **(a) jsonl 원장 + SQLite 투영은 계속 비교할 기준선으로 타당합니다.** 다만 현재 실측만으로 정본을 jsonl로 확정하기에는 내구성, 충돌 처리, 동시 롤업, 복원 검증이 남아 있습니다. 그래프 투영의 추가 여부는 기록 수보다 **출처 설명·영향 계산 등 특정 작업에서 얻는 이득**으로 판단하는 편이 맞습니다. Bitemporal은 (a)~(c)에도 적용할 수 있는 시간 의미론이므로, 별도 제품 채택과 분리해서 비교해야 합니다. **[추정] 2026-10-17**

입력은 지정된 ** [2506468be2eb117a602f3f8222c53b975d2cafec](https://github.com/AofSpds/aaaNew/tree/2506468be2eb117a602f3f8222c53b975d2cafec)**의 문서 6개와 거기서 연결한 S0~S3 실측 코드로 한정했습니다. 제품의 현재 상태는 별도로 공개 1차 자료를 확인했습니다.

아래에서 날짜는 논문·릴리스의 발표일을 우선 표시하고, 갱신일이 불명확한 문서는 **조회일 2026-10-17**을 표시합니다. 표의 비용·적합성·권고는 **[추정]**이며 HANAL 실측값이 아닙니다. 모델 카드와 공급자 문서는 기능·배포 조건의 근거로 사용했고, 그들의 성능 보고를 AAA 환경의 독립 검증으로 취급하지 않았습니다.

## Q1. 기록 형식: 최소 envelope는 무엇인가

### 찾은 것

**W3C PROV는 출처 관계의 어휘와 구조를 제공하지만 저장 봉투 전체를 정하지는 않습니다.** Entity–Activity–Agent, wasDerivedFrom, revision, invalidation을 구분하는 방식은 유용합니다. 특히 여러 입력을 사용한 변환을 하나의 Activity로 나타내면, 입력마다 역할이 다른 관계를 단순한 출처 ID 목록보다 정확히 보존할 수 있습니다. **[공식 문서] 2013-04-30**  [w3.org](https://www.w3.org/TR/prov-dm/?utm_source=chatgpt.com)

Event Sourcing의 핵심 선행 사례는 **불변 사건을 남기고, 교정·취소도 후속 사건으로 표현하며, 조회 상태를 투영으로 만든다**는 것입니다. 다만 event 형식의 버전 관리, 재시도 중복 방지, 동시 변경 충돌은 별도 설계가 필요합니다. **[공식 문서] 2026-03-28**  [Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing?utm_source=chatgpt.com)

시간 모델에서는 다음 차이가 중요합니다.

- **XTDB**는 시스템이 알게 된 시간과 사실이 유효한 시간을 각각 관리합니다. 현재 문서의 _system_from/_system_to, _valid_from/_valid_to가 이 구분입니다. **[공식 문서] 2026-10-17 조회**  [XTDB](https://docs.xtdb.com/concepts/key-concepts.html?utm_source=chatgpt.com)
- **Datomic**은 transaction에 따른 불변 이력과 as-of·history 조회가 강점입니다. 이것만으로 업무상 유효 시간까지 자동으로 갖춘 bitemporal 모델이 되지는 않습니다. 유효 시간은 추가로 모델링해야 합니다. **[공식 문서] 2026-10-17 조회**  [Datomic+1](https://docs.datomic.com/transactions/model.html?utm_source=chatgpt.com)

### 선택지 표

다음은 **공통 봉투 + 사건 종류별 부속 정보**라는 최소 후보입니다. 모든 메모에 모든 필드를 반복하기보다, 변경되지 않는 계약은 revision을 가진 별도 기록으로 참조할 수 있습니다. **[추정] 2026-10-17**

| 항목 | 최소 후보 | 구분해야 할 의미·확장 조건 |
|---|---|---|
| 형식·사건 종류 | schema_version, event_type | CURRENT 변경, ROADMAP 변경, 교정, 철회, View 생성 등을 구별. 과거 형식을 읽는 변환 규칙도 버전 관리 |
| 기록·대상 식별 | event_id, subject_id | 사건의 ID와 변경 대상의 ID를 분리. 한 사건이 한 revision을 만들면 event_id를 revision ID로 겸용 가능. 내용이 같아도 별개 사건일 수 있음 |
| 스트림·순서·재시도 | stream_id, seq, command_id, 필요한 경우 expected_revision | seq는 스트림 내부 순서. 여러 기기가 독립적으로 쓰면 writer/device 또는 stream epoch 구분 필요. 재시도 중복 방지와 오래된 CURRENT 기반 변경의 충돌 검사는 서로 다른 문제 |
| 내용·digest | payload 또는 불변 내용 참조, digest_algorithm, content_digest, canonicalization_version | 어떤 바이트를 해시했는지 명시. 원문 digest와 정규화한 내용 digest는 별개. digest만으로 원문을 복원할 수는 없음 |
| 출처·관계 | 출처의 정확한 revision, relation_type, 필요한 경우 입력 역할·범위 | Git이면 repository/commit/path/blob, 원장이면 stream/event/revision. mentions, derived_from, corrects, depends_on을 구별. 다중 입력 변환에는 activity_id와 입력별 역할 |
| View·손실 계약 | view_spec_revision, generator_revision, 입력 revision 집합, loss_profile_ref | preserved/collapsed/discarded는 어떤 필드·구분을 보존·합침·생략했는지 기술. discarded는 해당 View의 생략이지 원장 삭제를 뜻하지 않음 |
| 상태 | 각 상태 축의 변경 사건 | 존재, 가시성, 활성, 보존, 보관, 논리적 철회, 물리적 가용성을 분리. 초기화는 사건 또는 epoch 전환으로 표현. 운영 헤더의 state 하나로 모두 대체하지 않음 |
| 교정·tombstone | target_revision, 변경 종류, 이유·근거, 후속 revision | 교정은 대체 주장을 추가하는 사건. tombstone은 철회·조회 제외의 의미를 명시하는 사건. 과거 사건과 원문 보존은 계속 유지 |
| 기록·유효 시간 | recorded_at, valid_from, valid_to 또는 미지정 표시 | 엔진 기록 시각과 업무상 유효 시각을 구별. 구간 경계 규칙 명시. 벽시계나 시간순 ID만으로 여러 스트림의 전역 순서를 판단하지 않음 |
| 작성·권한 문맥 | 작성 주체·역할·세션 ID, 필요한 정책 revision | 역할 이름은 권한의 증명이 아님. 실제 호출 문맥에서 검증된 주체와 연결. 키·시크릿은 포함하지 않음 |

JSON digest에는 직렬화 규칙을 고정해야 합니다. **RFC 8785 JCS는 Unicode 정규화를 수행하지 않습니다.** 따라서 “NFC 정규화 + Python sort_keys=True”를 사용한다면 그것은 별도의 자체 규칙이지 JCS와 동일한 규칙이 아닙니다. **[공식 문서] 2020-06**  [RFC Editor](https://www.rfc-editor.org/rfc/rfc8785?utm_source=chatgpt.com)

### 조건부 권고

**우선 비교할 봉투는 위 공통 필드와, 파생·교정·상태 사건에만 붙는 부속 정보입니다.** PROV 전체나 범용 그래프 스키마를 매 기록에 강제할 이유는 아직 없습니다. 관계 자체를 교정하거나 근거를 붙여야 한다면 그 관계도 식별 가능한 기록으로 다루는 편이 자연스럽습니다. **[추정] 2026-10-17**

시간 요구가 “그때 CURRENT가 무엇이었나”에 그치면 기록 이력만으로 시작할 수 있습니다. 반면 **“10월 17일에 알게 된 교정을 반영했을 때, 10월 15일에 유효했던 계획은 무엇인가”**가 필요하면 유효 시간과 기록 시간을 처음부터 구분해야 합니다. 이 요구가 생겨도 곧바로 별도 bitemporal DB가 필요한 것은 아닙니다. **[추정] 2026-10-17**

### 모르는 것

- subject를 메모 전체, 항목, 주장, 관계 중 어디까지 나눌지.
- “재구성 가능”이 원문 복원, 동일 View 바이트 재현, 의미 등가 중 무엇을 보장해야 하는지.
- 기록 시각의 신뢰 기준과 여러 기기 사이의 충돌 정책.
- Byul의 보존 계약을 이 도메인에서 검사 가능한 규칙으로 얼마나 구체화할 수 있는지.

## Q2. 따라갈 범위 규칙과 선택적 재계산

### 찾은 것

**출처를 설명하기 위한 추적과, 갱신 대상을 놓치지 않기 위한 무효화는 다른 계약이 필요합니다.** 설명은 깊이·종류·출력량으로 줄일 수 있습니다. 무효화는 실제 의존성을 누락하면 낡은 View를 유효하다고 제공하게 됩니다. 계산 예산이 부족하면 미처리 범위를 dirty/pending으로 남기는 방식이 필요합니다. **[추정] 2026-10-17**

PROV에서도 어떤 Activity가 입력을 사용하고 결과를 생성했다는 사실만으로 두 Entity 사이의 derivation이 항상 성립하는 것은 아닙니다. **관계 종류와 변환 의미를 먼저 정한다**는 Byul 원칙과 맞닿습니다. **[공식 문서] 2013-04-30**  [w3.org](https://www.w3.org/TR/prov-dm/?utm_source=chatgpt.com)

### 선택지 표

| 방법 | 선행 사례·찾은 것 | 이 환경에서의 용도와 한계 |
|---|---|---|
| Typed provenance | PROV의 사용·생성·파생·revision·invalidation 구분. [공식 문서] 2013-04-30 | mentions/related_to와 실제 계산 의존성을 분리. 출처 설명과 영향 계산에 서로 다른 관계 집합 사용 |
| 깊이·종류·시간·출력량 제한 | 탐색 정책으로 구현 가능. [추정] 2026-10-17 | 설명 요청에 적합. truncated, 중단 이유, 남은 frontier를 반환. 무효화에는 같은 제한을 무조건 적용하지 않음 |
| View 조건부 합성 | Relational Lenses는 View와 원천 사이의 변환 법칙·조건을 다룸. [논문] 2006-06  cis.upenn.edu | 허용된 관계 경로와 View의 보존 계약이 맞을 때만 합성. 임의의 자연어 요약에 역변환 가능성을 부여하지 않음 |
| Provenance semiring | Provenance Semirings의 덧셈은 대안적 증명, 곱셈은 공동 기여를 표현. [논문] 2007-06  cs.ucdavis.edu | 같은 결과 tuple의 근거가 ab+c라면 “a와 b가 함께” 또는 “c”라는 구별 보존. 신뢰도 점수가 아님. 양의 관계대수 밖의 부정·집계·자연어 변환에는 추가 의미론 필요 |
| IVM / DBSP | DBSP: Automatic Incremental View Maintenance for Rich Query Languages는 입력 변화로 출력 변화를 계산하는 체계를 제시. [논문] 2023  vldb.org | 롤업·필터·집계의 증분 계산 후보. 삭제나 MIN, TOP K 등은 추가 상태나 재계산이 필요할 수 있음. 자연어 요약은 별도 재실행 정책 필요 |
| Differential Dataflow | 입력 버전과 반복 계산을 부분 순서의 논리 시간으로 추적. [논문] 2013-01  cidrdb.org | 반복·재귀 계산의 증분 처리 후보. 이 논리 시간은 기록 시간/유효 시간과 다름. 작은 메모 저장소에 도입할 운영 비용은 별도 검증 대상 |

### 조건부 권고

선택적 재계산의 비교 기준은 다음 순서가 적절합니다. **[추정] 2026-10-17**

1. **변경을 구분한다.** 내용 변경, 교정, 철회, 권한 변경, 역할 등록 변경, 단순 표시 변경을 동일한 Delta로 취급하지 않습니다.
2. **정확한 입력 revision과 질의 조건의 의존성을 찾는다.** 역방향 출처 색인뿐 아니라 역할 목록, 검색 조건, 시간 경계 등도 포함합니다.
3. **영향받은 View 또는 파티션을 무효화한다.** 추적을 끝내지 못하면 남은 범위를 유효한 것으로 표시하지 않습니다.
4. **정의된 입력 snapshot으로 재계산한다.** 입력 revision 목록을 적는 것만으로 일관된 snapshot이 생기지는 않습니다.
5. **게시 직전에 입력·generation을 검증한다.** 오래 걸린 계산이 더 최신 결과를 덮지 않게 하고, 계약상 달라진 출력·출처·권한이 있을 때 후속 영향을 전파합니다.

특히 **부재에 대한 의존성**이 빠지기 쉽습니다. “대기 항목 없음”은 현재 읽은 레코드만으로 설명되지 않고, “도메인의 모든 역할”은 새 역할이 추가될 때도 바뀝니다. 과거 derived_from 간선만 따라가면 이런 변경을 놓칩니다. roles.json의 revision이나 질의 범위도 의존성에 들어가야 합니다. **[추정] 2026-10-17**

과거 사건은 보존하고, **현재 유효한 View를 선택적으로 다시 계산**하면 됩니다. 사람이 탐색하는 출처 설명에는 짧은 기본 범위를 두고 상세 회수를 제공하는 방식이 AAA의 “얇은 Current + 정확한 상세 회수”와도 맞습니다.

### 모르는 것

실제 관계 종류별 fan-out, 부정·집계 질의 비중, 자연어 요약의 재실행 빈도, 허용 지연이 없습니다. 따라서 semiring이나 Differential Dataflow가 단순 역색인·SQL 재계산보다 나은지는 아직 판단할 수 없습니다.

## Q3. 네 층 구조를 이름 붙은 작업별로 비교

### 찾은 것

**(d)는 (a)~(c)와 완전히 배타적인 선택지가 아닙니다.** jsonl 사건과 SQLite 투영에도 두 시간 축을 넣을 수 있습니다. 다음 표의 (d)는 시간 이력 질의가 중심인 저장 구조를 뜻하며, 전용 temporal DB 채택 여부는 별도입니다. **[추정] 2026-10-17**

또한 관계를 기본 단위로 보는 것과 그래프 DB를 정본으로 삼는 것은 별개입니다. 관계 테이블, RDF, property graph 모두 관계를 표현할 수 있고, 보존·교정·시간 계약은 어느 쪽에도 필요합니다.

### 선택지 표

**작업별 비교 — [추정] 2026-10-17. 성능 순위가 아니라 구현 적합성 비교입니다.**

| 이름 붙은 작업 | (a) jsonl + SQLite | (b) (a) + 그래프 투영 | (c) 그래프 DB 정본 | (d) bitemporal 저장 구조 |
|---|---|---|---|---|
| 현재 상태 조회 | head·상태 테이블로 단순 | 대체로 추가 이득 작음 | 현재 revision 선택 규칙 필요 | 기록·유효 시간의 기준을 지정해 조회 |
| 도메인 롤업 | SQL 집계·결정적 생성에 적합 | 관계 패턴이 복잡할 때만 이득 후보 | 가능하지만 집계·게시 일관성 문제는 유지 | 특정 시점의 롤업 재현에 강점 |
| 출처 추적 | 역색인·재귀 CTE로 시작 가능 | 여러 관계 종류·경로 조건의 반복 조회에 이득 후보 | 주요 작업이면 자연스러운 표현 가능 | 당시 알려진 출처와 현재 교정된 출처를 구별 |
| 영향 범위·무효화 | 의존성 테이블·dirty 집합 | 복잡한 역방향 패턴 탐색 후보 | 저장 자체가 무효화 의미를 해결하지는 않음 | 어느 유효 구간이 영향을 받는지 좁히기 쉬움 |
| 검색 / RAG | FTS·벡터 투영을 독립적으로 추가 | 검색 후 제한된 관계 확장에 후보 | 본문 검색·최신성·권한 검사는 별도 | 과거 검색과 현재 검색의 시간 필터에 강점 |
| 아카이브 조회 | 사건 이력 + snapshot으로 구현 | 과거 관계 구조 탐색에 후보 | revision·사건을 따로 보존해야 함 | “그때 알던 것 / 지금 아는 과거” 질의에 적합 |
| 백업·복원 | 원장·원천·계약을 보존하고 replay | 그래프는 원장으로 재생성 | DB snapshot과 논리 export, 이력 보존 검증 필요 | 두 시간 축과 교정 이력을 보존하는 export 필요 |

**구축·유지·동시성 비교 — 비용은 [추정] 2026-10-17.**

| 안 | 구축·유지 비용 | 여러 프로세스 쓰기 | Windows 관점 |
|---|---|---|---|
| (a) | 중간. 별도 서버는 줄지만 append 확정, 복구, replay, 투영 진도 관리가 자체 책임 | 스트림 잠금과 SQLite transaction을 조정해야 함. 두 저장물 사이 실패 복구 필요 | 현재 실측 기반을 활용 가능 |
| (b) | (a)에 색인 갱신, 재구축, 버전 호환 비용 추가 | 그래프 파일을 한 프로세스가 소유하도록 구성해야 하는 후보가 많음 | 제품별 wheel·파일 공유 제약 확인 필요 |
| (c) | 높음. 사건·교정·보존·export를 그래프 정본의 transaction 모델에 맞춰야 함 | 로컬 서버의 다중 클라이언트와 다중 프로세스의 직접 파일 열기는 구별 | 내장 커널의 Windows 지원과 Python 클라이언트 지원은 별개 |
| (d) | 기존 저장소에 시간 의미론 추가는 중간, 전용 엔진 운영은 높아질 수 있음 | 제품의 transaction·단일 writer·서버 구조에 의존 | 시간 의미론 자체는 이식 가능, 전용 엔진은 별도 확인 |

SQLite WAL은 같은 PC의 여러 프로세스가 읽고 쓸 수 있지만 **쓰기 transaction은 한 번에 하나**입니다. “여러 프로세스 지원”과 “여러 쓰기가 동시에 확정됨”을 구분해야 합니다. **[공식 문서] 2026-08-25**  [sqlite.org](https://www.sqlite.org/wal.html?utm_source=chatgpt.com)

### 조건부 권고

- 현재 상태·롤업·정확한 회수가 주요 작업이면 **(a)를 기준선으로 유지**할 근거가 있습니다.
- 출처·영향의 특정 질의가 지연 목표를 넘고, 그래프 투영이 **갱신·재구축 비용까지 포함해** 이득을 보이면 (b)를 비교할 가치가 있습니다.
- (c)는 그래프 작업이 핵심이라는 증거와 함께, 정본 이관 후의 이력·복원·동시성 계약도 검증될 때 검토할 선택지입니다.
- 과거 시점에 대한 교정·감사가 반복적으로 필요하면 **(d)의 의미론을 우선 추가하는 안**을 비교해야 합니다. 전용 제품은 그 구현 비용을 줄이는지로 판단합니다.

모두 **[추정] 2026-10-17**입니다.

### 모르는 것

현재 조회 대 아카이브 조회 비중, 요구 p95 지연, 여러 스트림의 원자적 변경 필요성, jwDev의 독립 쓰기 여부, 허용 가능한 투영 지연이 정해지지 않았습니다.

## Q4. 내장형 그래프 DB의 2026년 상태

### 찾은 것

가장 큰 구분은 **Windows Python 패키지가 있다는 사실과, 여러 세션이 같은 DB 파일을 직접 공유할 수 있다는 사실이 다르다**는 점입니다.

아래 최신 배포는 **2026-10-17에 확인한 공개 배포물 기준**입니다. Python wrapper와 엔진 버전을 구별했습니다. 유지 상태는 archive 표시·공개 릴리스 활동으로 판단했으며, 향후 유지 인력이나 지원을 보장하지 않습니다.

### 선택지 표

#### 배포·라이선스·Windows/Python

| 후보 | 유지 상태·확인된 최신 배포 | 라이선스 | Windows·Python 근거 |
|---|---|---|---|
| Kuzu | 2025-10-10 archived. kuzu 0.11.3, 2025-10-10 | MIT | CPython 3.13 Windows x64 wheel 있음. 향후 수정 중단은 별도 위험. [저장소·릴리스]  PyPI |
| RyuGraph | 후속 포크. ryugraph 25.9.2, 2025-12-06. 이번 확인에서 이후 공개 Python 릴리스는 찾지 못함 | MIT | CPython 3.13 Windows x64 wheel 있음. [저장소·릴리스]  PyPI |
| LadybugDB | 후속 포크, 최근 릴리스 활동 확인. ladybug 0.21.2, 2026-10-01 | MIT | CPython 3.13 Windows x64·ARM64 wheel 있음. [저장소·릴리스]  PyPI |
| DuckPGQ | CWI의 진행 중인 연구 확장. Community descriptor는 1.0.0. GitHub의 게시된 Release 목록은 비어 있었고 배포일은 미확인 | MIT | DuckDB의 확장으로 사용. 현재 Windows·Python·DuckDB 버전 조합의 가용성은 미확정. [저장소·릴리스] 2026-10-17 조회,  배포 descriptor. [공식 문서] 2026-10-17 조회  DuckDB Community Extensions |
| Oxigraph | 최근 배포 확인. pyoxigraph 0.5.11, 2026-09-02 | MIT 또는 Apache-2.0 | CPython 3.13 Windows x64 wheel 있음. [저장소·릴리스]  PyPI |
| FalkorDBLite | Python wrapper 0.10.0, 2026-05-02 | wrapper는 BSD 계열, FalkorDB 코어는 SSPLv1. Redis를 포함한 전체 구성은 별도 확인 대상 | Python ≥3.12. 확인된 wheel은 Linux/macOS이며 native Windows 배포는 확인하지 못함. Windows는 WSL 경로와 구별 필요. [저장소·릴리스]  PyPI +2 |
| CozoDB | cozo-embedded 0.7.6, 2023-12-11. 공개 배포 공백이 김 | MPL-2.0 | Windows x64 cp37-abi3 wheel 있음. 태그만으로 Python 3.13 불가라고 할 수는 없지만 HANAL 작동은 미검증. [저장소·릴리스]  PyPI |
| SQLite | 최근 릴리스 3.54.1, 2026-10-16 | Public Domain | Windows 지원, Python sqlite3 연결. 실제 사용 엔진 버전은 Python 버전과 별도로 확인해야 함. [저장소·릴리스] / [공식 문서] 2026-10-17 조회  sqlite.org +1 |

DuckPGQ는 특히 **배포 descriptor의 버전만으로 호환성을 확정하면 안 됩니다.** 조회한 DuckDB 공식 Graph Queries 문서는 아직 “1.5.x에서 사용할 수 없으며 1.4.4를 사용”하라는 안내와 일부 기능의 미완성을 적고 있습니다. 현재 확장 바이너리와 문서의 일치 여부는 추가 확인 대상입니다. **[공식 문서] 2026-10-17 조회**  [DuckDB](https://www.duckdb.org/docs/current/guides/sql_features/graph_queries?utm_source=chatgpt.com)

#### 직접 파일 공유·형식 안정성·투영의 이득

아래 동시성·형식은 **[공식 문서] 또는 [저장소·릴리스], 2026-10-17 조회**입니다. 마지막 열은 **[추정] 2026-10-17**입니다.

| 후보 | 여러 프로세스와 같은 DB | 파일 형식·이관 판단 | 투영으로 이득을 볼 작업 후보 |
|---|---|---|---|
| Kuzu | RW Database 소유자 하나 또는 여러 RO 소유자. writer와 별도 reader 프로세스의 동시 직접 공유를 전제하면 안 됨 | archive 이후 수정 경로가 제한됨. 포크 사이 파일 호환 보장은 별도 | 기존 Cypher·경로 질의 비교 기준. 신규 장기 의존의 근거는 약함.  Kuzu |
| RyuGraph | 하나의 RW 소유자 또는 여러 RO 소유자 | 버전 이관용 export/import 문서 존재. 장기 무변환 호환 보장은 확인하지 못함 | typed path·여러 관계 패턴 조회.  RyuGraph +1 |
| LadybugDB | 같은 소유 모델. 세션들은 DB 소유 프로세스를 통해 접근하는 형태가 비교 대상 | export/import 이관 경로 존재. Kuzu·RyuGraph와 상호 파일 호환을 가정하지 않음 | 복잡한 provenance·영향 패턴, 반복 경로 질의.  Ladybug +1 |
| DuckPGQ | 내장 DuckDB의 기본 모델은 한 RW 프로세스 또는 여러 RO 프로세스 | 본체 저장 형식, 확장 ABI, property-graph 메타데이터 호환성을 구별 | 관계 테이블 위 SQL/PGQ 패턴 조회, 배치 그래프 분석.  DuckDB +1 |
| Oxigraph | RocksDB 저장소를 소유하는 프로세스가 필요. 다른 프로세스가 쓰는 동안 read_only로 여는 것은 문서상 undefined behavior | RDF dump/reload 경로 있음. 과거 major 전환에 이관 요구 및 RDF 의미 변화가 있었음 | PROV/RDF 상호운용, SPARQL·named graph 질의.  pyoxigraph 0.5.11 documentation +1 |
| FalkorDBLite | Python이 로컬 Redis/FalkorDB 하위 서버를 관리. 여러 클라이언트는 같은 서버에 연결 | persistence는 Redis·모듈 버전에 의존. wrapper의 파일 경로 인자가 범용 안정 포맷 계약을 뜻하지 않음 | 로컬 서버 운영을 허용할 때 여러 클라이언트의 그래프 질의.  GitHub |
| CozoDB | Python client는 thread-safe지만 여러 프로세스의 embedded DB 동시 열기는 문서상 허용하지 않음 | pre-1.0의 syntax/API/storage 호환을 보장하지 않는다고 명시 | Datalog 규칙·재귀 질의, 관계와 벡터를 함께 쓰는 투영.  GitHub +1 |
| SQLite | 같은 PC에서 여러 프로세스 사용 가능. WAL에서도 writer는 한 번에 하나 | SQLite 3 파일의 장기 backward compatibility 근거가 강함. WAL과 애플리케이션 스키마 이관은 별도 | head·롤업·역색인·제한된 재귀 CTE·FTS를 한 투영에 결합.  sqlite.org +1 |

### 조건부 권고

**투영 실험의 후보를 질의 언어와 작업으로 나누는 편이 유효합니다.** **[추정] 2026-10-17**

- Cypher·property graph 경로가 필요하면 RyuGraph/LadybugDB 계열을 비교.
- RDF/PROV 교환과 SPARQL이 중요하면 Oxigraph를 비교.
- 관계형 배치 분석에 SQL/PGQ를 붙이려면 DuckPGQ를 비교하되, 버전 조합부터 확인.
- 규칙·재귀가 핵심이면 CozoDB를 비교.
- 로컬 서버 프로세스 운영을 허용하면 FalkorDBLite도 포함.
- Kuzu는 재현용 기준으로는 의미가 있지만, archive 상태를 장기 운영 조건에 반영.

**그래프 투영을 쓰더라도 세션 수만큼 DB를 직접 여는 방식이 기본값이 되어서는 안 됩니다.** 한 소유 프로세스가 투영을 갱신하고 질의를 받는 방식의 추가 운영 비용까지 비교해야 합니다.

### 모르는 것

HANAL에서의 실제 설치·실행, 장기 reopen/upgrade/downgrade 호환성, 동시 transaction 실패 양상, 메모리 사용량은 미실측입니다. 특히 DuckPGQ의 현재 Windows 바이너리 조합과 RyuGraph·CozoDB의 향후 유지 지속성은 공개 자료만으로 확정하지 못했습니다.

## Q5. 외부 서비스 없는 검색 층

### 찾은 것

검색 도입 시점은 **사건 수보다 질문 유형과 검색 대상 chunk 수**에 좌우됩니다. 역할 20개의 현재 상태나 정확한 ACT_ID 조회는 SQL로 충분할 수 있습니다. 반대로 수백 건만 있어도 표현이 다른 동일 주제를 찾아야 한다면 의미 검색을 비교할 이유가 생깁니다. **[추정] 2026-10-17**

FTS5는 로컬 기본선으로 적합하지만 한국어에서 주의점이 있습니다.

- unicode61은 한국어 형태소 분석기가 아닙니다.
- trigram tokenizer의 MATCH는 **3개 Unicode 문자보다 짧은 검색어를 매칭하지 않습니다.**
- external-content FTS를 쓰면 본문과 색인의 동기화 책임이 있습니다.

따라서 두 음절 검색어, 조사 변화, 역할명·ID의 구두점이 있는 실제 질의를 시험해야 합니다. **[공식 문서] 2026-10-17 조회**  [sqlite.org](https://www.sqlite.org/fts5.html?utm_source=chatgpt.com)

### 선택지 표

| 선택지 | 필요한 질문·도입 조건 | 비용·한계 |
|---|---|---|
| 정확한 SQL + FTS5/BM25 | ID·역할·상태 필터, 원문에 존재하는 단어, 아카이브 키워드 회수 | 가장 단순한 대조군. 한국어 토큰화·별칭·prefix 전략 비교 필요 |
| 로컬 임베딩 | 말바꾸기, 표현이 다른 동일 주제, 한국어/영어 혼합 의미 검색 | 모델·chunker 버전, 임베딩 재계산, 벡터 저장 비용 추가 |
| 하이브리드 | 정확한 식별자·어휘와 의미 유사성이 모두 중요한 질의 | FTS와 벡터의 후보를 합침. 서로 다른 원점수를 바로 더하기보다 순위 결합이 비교하기 쉬움 |
| 하이브리드 + reranker | 후보에는 정답이 있지만 상위 순서가 좋지 않을 때 | 추론 지연 추가. 후보 recall 부족은 reranker만으로 해결되지 않음 |

표의 적합성·비용은 **[추정] 2026-10-17**입니다.

로컬 임베딩의 구체적 대조 후보로 **multilingual-e5-small**이 있습니다. 모델 카드는 MIT, 384차원, 최대 512 tokens, query:/passage: prefix 사용을 명시합니다. 한국어를 포함한 다국어 모델이라는 사실은 후보 선정 근거이며, AAA의 한국어 메모 품질을 입증하지는 않습니다. **[저장소·릴리스] 2026-10-17 조회**  [intfloat/multilingual-e5-small at main](https://huggingface.co/intfloat/multilingual-e5-small/blob/main/README.md?utm_source=chatgpt.com)

CPU 실행에는 ONNX 경로도 비교할 수 있습니다. 다만 runtime을 바꿀 때 pooling·normalization을 포함한 출력 동일성 확인이 필요합니다. **[공식 문서] 2026-10-17 조회**  [Sentence Transformers documentation](https://sbert.net/docs/sentence_transformer/usage/efficiency.html?utm_source=chatgpt.com)

하이브리드의 단순 선행 사례는 **Reciprocal Rank Fusion**입니다. 순위 기반 결합이므로 BM25와 cosine의 척도를 직접 같다고 가정하지 않아도 됩니다. **[논문] 2009-07**  [cormack.uwaterloo.ca](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf?utm_source=chatgpt.com)

### 조건부 권고

**FTS 대조군에서 실패하는 질문을 먼저 모은 뒤 임베딩을 추가하는 비교**가 적절합니다. “1만 건부터 벡터 DB” 같은 고정 경계값의 근거는 없습니다. 예를 들어 10만 개의 384차원 float32 벡터는 원시 값만 약 **153.6 MB**이며, 여기에 색인·메타데이터 비용이 붙습니다. 이 규모에서도 ANN의 필요성은 지연 실측으로 결정할 수 있습니다. **[추정·계산] 2026-10-17**

최신성·권한에는 다음 조건이 필요합니다. **[추정] 2026-10-17**

1. 검색 항목에 source_revision, chunker_revision, embedding_model_revision, 투영 진도를 기록합니다.
2. 현재 질문과 과거 질문을 구분하고, 현재 질문에는 현재 유효한 revision만 채택합니다.
3. 임베딩 계산이 끝났을 때 원천 revision을 다시 검사해 오래된 계산 결과의 게시를 막습니다.
4. **본문을 모델 문맥에 넣기 전에 권한을 검사**하고, 최종 제공 직전에도 변경 여부를 확인합니다. 과거 조회에도 현재의 접근 권한 검사가 필요합니다.
5. 검색 색인이 원장보다 뒤처졌다면 따라잡거나 조회 기준 시점을 표시합니다.

전역 Top-K를 먼저 뽑고 권한 밖의 결과를 지우는 방식은 허용된 결과를 충분히 못 찾을 수 있습니다. 작은 corpus라면 허용 범위 내 검색이 단순한 대조군입니다. 같은 Windows 계정으로 모든 원장을 직접 읽을 수 있다면, 엔진의 역할 필터는 **OS 수준의 격리 보장과 구별**해야 합니다.

### 모르는 것

한국어 실질 recall, 반복 CURRENT의 중복 chunk 비율, 한영 혼합 질의 비율, CPU 추론 지연, HANAL의 모델/runtime 조합은 미실측입니다.

## Q6. JEV-like 판정을 로컬에서 쓸 수 있는가

### 찾은 것

**좁은 판정 기능은 외부 API 없이 구성할 수 있습니다.** 다만 JEV와 같은 품질이나 분포를 재현한다는 근거는 없습니다. 현재 Kev 0.8B의 17/36과 선택지 순서 민감성은, 이 환경에서 모델 판정을 곧바로 확정 변경에 연결할 근거가 부족하다는 자체 관찰로 읽는 편이 맞습니다. **[저장소·릴리스] 2026-10-17, 지정 선행 연구 요약**

외부 연구에서도 LLM judge의 순서 편향과 분포 편향이 보고되었습니다. **Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge**와 **CalibraEval: Calibrating Prediction Distribution to Mitigate Selection Bias in LLMs-as-Judges**는 순서·선택지 ID·분포를 기록하고 점검할 근거입니다. 이 논문들이 현재 로컬 후보의 AAA 품질을 검증한 것은 아닙니다. **[논문] 각각 2025-12, 2025-07**  [ACL Anthology+1](https://aclanthology.org/2025.ijcnlp-long.18/?utm_source=chatgpt.com)

### 선택지 표

| 대안 | 적용 가능한 좁은 신호 | 품질 근거·제약 |
|---|---|---|
| 규칙·digest·정확한 필드 비교 | 동일 내용, 같은 revision, 필수 항목 누락 | 의미 판정과 비교할 필수 대조군. 시간·ID·권한·확정 상태 검사에 적합. [추정] 2026-10-17 |
| 임베딩 유사도 / reranker | 관련 문맥 후보, 중복 후보, 검색 순서 | bge-reranker-v2-m3는 다국어 relevance 후보, Apache-2.0. 유사도·관련성이 사실성이나 관계 확정을 뜻하지 않음. [저장소·릴리스] 2026-10-17 조회  Hugging Face |
| 로컬 NLI classifier | 정해진 문장쌍의 entailment/contradiction/neutral 후보 | mDeBERTa-v3-base-mnli-xnli, MIT. 모델 카드의 XNLI 평가 범위에 한국어가 없어 한국어 품질은 추가 검증 필요. [저장소·릴리스] 2026-10-17 조회  Hugging Face |
| 로컬 instruction model | 관계 제안, 요약 충분성 경고, 제한된 rubric 판정 | Qwen3-4B-Instruct-2507, Apache-2.0. llama.cpp에 Windows 실행 경로가 있음. 해당 업무 정확도·CPU 지연은 미실측. [저장소·릴리스] / [공식 문서] 2026-10-17 조회  Hugging Face +1 |

#### 판정을 남길 최소 부속 정보

다음은 Q1의 사건 봉투에 붙일 후보입니다. **[추정] 2026-10-17**

| 묶음 | 보존할 내용 |
|---|---|
| 대상 | 원천 ID·revision·digest·본문 범위, 검색으로 넣은 모든 문맥의 revision |
| 질문 | 질문 원문 또는 불변 참조, prompt/rubric revision, label ID 정의 |
| 순서 | 선택지 ID의 실제 표시 순서, 원천·문맥 순서. 순열별 실행은 각각 기록 |
| 모델·실행기 | 모델·weights revision/digest, tokenizer, quantization, runtime/backend, decoding 설정, seed |
| 전체 산출값 | 모든 label의 원점수/log-probability와 계산법, 확률화했다면 전체 분포와 정규화 방법, parse 실패·누락 표시 |
| 보정·안정성 | calibration 방법·데이터 revision, 순서 변화별 결과, abstention 이유 |
| 제안·확정 상태 | judgment_id, 제안 대상, proposed/accepted/rejected/abstained/expired 상태와 후속 사건 참조 |

모델이 출력한 “confidence 0.9”, sigmoid로 바꾼 점수, 보정된 확률은 서로 다릅니다. 실제 확률을 산출하지 않았다면 그 사실을 기록해야 합니다. 단일 선택 결과를 전체 분포처럼 저장해서는 안 되며, 독립적인 다중 label 과제라면 합이 1인 분포를 강제할 이유도 없습니다. 확률과 실제 정답률의 일치를 평가해야 한다는 근거는 **On Calibration of Modern Neural Networks**에서 찾을 수 있습니다. **[논문] 2017-08**  [proceedings.mlr.press](https://proceedings.mlr.press/v70/guo17a.html?utm_source=chatgpt.com)

### 조건부 권고

판정은 **제안 사건**으로 기록하고, 확정 변경은 별도 사건으로 다루는 방식이 적절합니다. 확정 시에는 승인 주체·정책과 expected_revision을 검증합니다. 그 사이 원천이 바뀌었다면 과거 판정을 현재 변경에 자동 적용하지 않습니다. 거절·기권·만료된 판정도 보존할 수 있습니다. **[추정] 2026-10-17**

적용 범위는 선행 AAA 결론대로 다음에 한정해 비교할 근거가 있습니다.

- 문맥 관련성 후보.
- 의미 중복·관계 제안.
- 명시된 보존 계약에 대한 요약 충분성 경고.

ID·시각·권한·삭제·확정 변경의 권위는 결정적 검사와 승인 절차에 둡니다. 순서에 따라 결론이 바뀌면 기권하거나 검토 대상으로 보내는 조건을 시험할 수 있습니다. 순서 불변성만 통과해도 정확도가 입증되는 것은 아닙니다. **[추정] 2026-10-17**

### 모르는 것

각 후보의 AAA 한국어 판정 품질, 오류 종류별 비용, 적절한 기권 기준, full-distribution 산출 가능 여부, quantization 후 판정 변화가 미확인입니다. 36개 사례로 일반화 성능이나 확률 보정 상태를 확정하기도 어렵습니다.

## Q7. 임시 결과에 대한 반박과 빠진 위험

### 찾은 것

**가장 먼저 비교 조건에 반영할 공개 사실은 SQLite WAL 버전 문제입니다.** 공식 문서는 드문 WAL-reset bug가 3.7.0~3.51.2에 존재할 가능성이 높고, 3.51.3부터 수정되었으며 3.44.6·**3.50.7**에도 backport가 있다고 명시합니다. 둘 이상의 연결이 별도 thread/process에서 같은 WAL DB에 쓰기·checkpoint를 겹쳐 수행할 때 발생 가능한 손상 문제입니다. **HANAL의 3.50.4는 명시된 영향 범위 안에 있습니다.** 기존 S2에서 이 문제가 발생했다는 뜻은 아니지만, 다음 비교는 수정된 실제 연결 라이브러리를 기준으로 해야 합니다. **[공식 문서] 수정 릴리스 2026-03-13, 문서 갱신 2026-08-25**  [sqlite.org](https://www.sqlite.org/wal.html?utm_source=chatgpt.com)

### 선택지 표

아래 코드 관찰은 모두 **[저장소·릴리스] 2026-10-17, 고정 커밋**입니다. 관찰에서 도출한 위험·대안은 **[추정] 2026-10-17**입니다.

| 쟁점 | 확인된 반박·빠진 위험 | 비교·권고에 반영할 변화 |
|---|---|---|
| S1의 0.24 vs 0.06 ms | JSONL 쓰기는 fsync 없이 append/close. SQLite는 WAL synchronous=NORMAL. JSONL의 SQLite 투영은 timed write에 없고, rollup 때 :memory:로 전량 재생성.  S1 코드 | 성능 방향이 틀렸다고 단정할 수는 없지만 동일 내구성·동일 end-to-end 비용 비교는 아님. 원장 확정, 투영, read-after-write 조건을 맞춰 비교 |
| S2의 “손실 0” | 검사는 파싱과 (w,i) 중심으로, 예상 payload 전체의 무결성·재시도·CURRENT 충돌을 검증하지 않음. kill 시험의 타이머는 p.kill(); p.wait() 뒤에 시작.  S2 코드 | “해당 시험에서 예상 ID 누락 없음”, “종료 확인 후 잠금 재획득”으로 한정. 0.03 ms를 kill-to-unlock 지연으로 쓰지 않음 |
| 잠금과 논리적 변경 손실 | append를 직렬화해도 두 세션이 같은 옛 CURRENT를 읽고 각각 전체 상태를 제출하면 뒤의 상태가 앞의 변경을 덮을 수 있음 | 잠금/transaction 안에서 expected_revision 검사와 충돌 처리를 비교. CLI 하나는 실행 프로세스 하나를 뜻하지 않음 |
| S3의 동시 롤업 | role 잠금 해제 후 regenerate(). 여러 stream head를 공통 snapshot 없이 읽고, 공통 current.md를 직접 덮어씀. 성능 loop는 순차 실행. flag()는 두 역할의 상호 대기만 검사.  S3 코드 | 동시 실행에서 빈/부분 읽기, 이전 generation 재게시가 가능한 경쟁 조건. 관측된 손실로 과장하지 않되 snapshot·게시 순서·원자적 교체를 검증. 3개 이상 순환과 실제 deadlock 의미도 별도 |
| 깨진 JSONL 꼬리 복구 | S3 reader는 미완성 마지막 줄을 건너뛰지만, 재시작 writer가 그 뒤에 append할 때의 복구 절차는 구현·검증되어 있지 않음 | 불완전 바이트를 보존한 채 새 segment로 이어 쓰거나 복구 사건을 남기는 방식을 비교. 정상 줄 replay만으로 복구 완료라 하지 않음 |
| S0의 규모 해석 | 1만 건의 ancestry는 1,686건으로 약 17%. 100만 조건에서는 최초 source 2만 개 중 1만8천 개가 생성 규칙상 기록에 연결되지 않아 영향 시험이 편향됨. 측정 질의는 원문 회수가 아닌 count(*).  S0 코드 | 70~80%를 모든 규모·실제 그래프에 일반화할 수 없음. 범위 규칙 우선이라는 해석은 유지하되, 엔진별 색인·사전 계산과 결과 전송 비용을 따로 비교 |
| Git binary에 대한 평가 | S1 원문에서 SQLite의 “1개”는 Git에서 변경된 binary 수와 구별해야 함. 전체 파일 수는 25개로 보고됨. Git GC 후 크기도 SQLite 2,007 KiB, JSONL 3,235 KiB로 보고됨.  S1 문서 | 줄 diff의 편의성과 저장 효율을 구별. SQLite append-only 정본 + PR 시 결정적 JSONL export를 빠진 대조군으로 추가 |
| Drive·Git 병합·PR 백업 | HANAL의 OS 잠금이 jwDev의 복제 파일까지 직렬화한다는 근거는 없음. 텍스트 병합은 사건 순서·중복·인과 유효성 검사가 아님. PR 사이의 변경은 마지막 성공 백업 이후 손실 구간에 속함 | 기기별 불변 전송 단위, 명시적 충돌·재수입 규칙, 백업 snapshot 경계와 복원 검증을 비교 |

S1/S2의 내구성 차이는 공개 문서로도 뒷받침됩니다. Python의 buffer flush와 os.fsync는 구별되며, SQLite WAL의 NORMAL은 전원 손실 뒤 최근 transaction이 되돌아갈 수 있는 설정입니다. **S2는 synchronous 값을 명시·기록하지 않았으므로 S1과 같은 설정이었다고 가정하면 안 됩니다.** **[공식 문서] 2026-10-17 조회**  [Python 3.13.16 documentation+1](https://docs.python.org/3.13/library/os.html?utm_source=chatgpt.com)

merge=union을 사용할 경우에는 Git 문서 자체가 합쳐진 줄의 순서가 임의일 수 있다고 경고합니다. 이 경고는 해당 merge driver에 대한 것이며, 기본 Git merge 전체에 동일하게 일반화해서는 안 됩니다. **[공식 문서] 2026-10-17 조회**  [gitattributes Documentation](https://git-scm.com/docs/gitattributes?utm_source=chatgpt.com)

### 조건부 권고

현재 임시 권고는 **“좋은 비교 가설”로 유지하되, 검증의 우선순위를 확정·충돌·복원으로 옮기는 것**이 적절합니다. 특히 빠진 SQLite 정본 대조군은 사건 추가와 CURRENT 변경을 같은 transaction으로 묶는 이점과, JSONL export·복원 비용을 함께 비교할 수 있습니다. **[추정] 2026-10-17**

백업은 살아 있는 DB 파일을 단순 복사하거나 checkpoint 한 번으로 끝났다고 간주하지 않아야 합니다. SQLite의 **backup API 또는 VACUUM INTO**는 일관된 snapshot을 만드는 공식 경로입니다. 만들어진 닫힌 snapshot을 전송하는 문제와 운영 중인 DB 파일을 동기화하는 문제를 분리할 수 있습니다. **[공식 문서] 2026-10-17 조회**  [sqlite.org+1](https://www.sqlite.org/backup.html?utm_source=chatgpt.com)

JSONL 쪽도 스트림별 확정 경계, digest, schema, View 계약, 필요한 원천을 포함한 manifest가 있어야 복원을 검증할 수 있습니다. **출처 URL·digest만 남기고 실제 원문이나 도달 가능한 Git 객체를 잃으면 보존 계약을 충족하지 못합니다.** 또한 STALE 표시는 시간이 흐르기만 해도 바뀌므로 쓰기 시 재생성만으로는 충분하지 않을 수 있습니다. **[추정] 2026-10-17**

### 모르는 것

실측 실패율이 실제 세션의 변경 패턴에서 재현되는지, 파일시스템·저장장치의 flush 동작, 실제 Drive 경로와 동기화 방식, 백업 간격의 상한, 원천 원문의 장기 보존 범위는 확인되지 않았습니다. 코드상 위험과 실제 발생률은 구분해야 합니다.

## 우리가 다음에 실측할 것

다음은 제품 채택을 바꿀 수 있는 **5개 실험 묶음**입니다. 모두 제안이며 이번 조사에서 실행한 실측은 아닙니다. **[추정] 2026-10-17**

| 무엇을 | 어떤 조건으로 | 무엇을 보면 판단이 바뀌는가 |
|---|---|---|
| 1. 확정·내구성·충돌의 동일 조건 비교 | HANAL, 8/16 프로세스, 동일 1/10 KB payload. JSONL과 수정된 SQLite runtime의 내구성 조건을 명시. append·투영·응답 사이 중단, 재시도, 같은 CURRENT revision의 동시 변경을 포함. 프로세스 종료와 전원 손실 모사를 구별 | 응답 완료 기록의 누락·중복·내용 변형·조용한 변경 덮어쓰기를 비교. SQLite 정본+JSONL export가 계약을 더 단순하게 충족하면 정본 선택의 판단이 바뀜 |
| 2. 동시 롤업의 일관성 | 20/200 역할에서 동시 갱신, 계산 지연으로 게시 순서 역전 유도. 새 역할, 3개 이상 대기 순환, 시간 경과 STALE, 소급 교정 포함 | 최신 generation 퇴행, 부분 파일, 요구된 snapshot 위반을 검사. 매 쓰기 전체 생성이 비용·정합성 목표를 못 맞추면 증분·배치·조회 시 생성 비교로 이동 |
| 3. 백업·복원·두 기기 합류 | 쓰기 중 snapshot, replay, 중복·누락·순서 뒤바뀐 segment 수입, 두 기기의 독립 변경 후 합류. 원천·계약까지 복원 | 사건 수뿐 아니라 내용 digest, head, 시간 조회, 관계·원천 회수가 일치하는지 확인. PR 백업의 실제 손실 구간이나 복원 시간이 허용 범위를 넘으면 백업 단위·빈도를 재검토 |
| 4. 이름 붙은 그래프 작업 | 실제 typed 관계 분포로 1만/10만/100만 건. 제한된 출처 설명, 정확한 영향 계산, 부정·집계 의존성을 포함. SQLite와 필요한 그래프 후보만 동일 결과로 비교 | 질의 p95뿐 아니라 쓰기·무효화·재구축 시간과 메모리를 포함. 특정 작업의 요구를 그래프 투영이 유의미하게 개선할 때 (b)의 근거가 생김 |
| 5. 한국어 검색·로컬 판정의 추가 가치 | 정확한 ID, 두 음절, 말바꾸기, 부정, 과거 결정 질의의 보류 평가셋. FTS/규칙 대 임베딩·하이브리드·reranker·judge 비교. 선택지 순열과 추론 중 원천·권한 변경 포함 | Recall/Precision, 잘못된 관계 제안, 기권 시 정확도·처리 범위, 확률 보정, p95를 함께 평가. 단순 대조군 대비 이득이 없으면 모델 층을 보류하고, 낡은 결과·권한 밖 본문의 제공이 나타나면 검색 연결 방식을 먼저 수정 |
