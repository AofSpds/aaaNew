# Pro 답변 원문 — P2 저장소 운영 조사

- ACT_ID: MEM_STRG-PRO-P2-STORAGE-OPERATIONS-20261017-001
- 의뢰서: [P2 v1.0](OPERATIONS_REQUEST_v1.0_CLAUDE.md) · 입력 커밋 AofSpds/aaaNew@2506468
- 보낸 사람: Owner (2026-10-17, ChatGPT 프로젝트 "AAA_NEW_RSCH_MEM_STRG", 대화 "저장소 운영 조사")
- 처리: Pro, "9m 28s 동안 처리함"(화면 표시). 실제 모델은 화면 표시만 확인했습니다 [미확인].
- 대화 URL: https://chatgpt.com/g/g-p-6acef0baa5448191827e7448f85ac439/c/6ad36b75-92ac-83e8-a2e7-2ccea8c4d0c5
- 기록: 2026-10-18, AAA/NEW/RSCH/MEM_STRG
  - 방법: 오른쪽 브라우저의 답변 DOM을 Markdown으로 바꿔 옮겼습니다(읽기만 함).
  - 변환하면서 "일반 텍스트`…`"로 깨진 코드 블록 4곳은 코드 블록 모양으로만 되돌렸습니다. 본문은 고치지 않았습니다.
- 이 채널의 검토(채택·한계·정정)는 별도 문서에 씁니다. 이 파일은 원문 기록입니다.

---

# P2 — 저장소 운영 조사

**ACT_ID:** MEM_STRG-PRO-P2-STORAGE-OPERATIONS-20261017-001
**조사 기준일:** 2026-10-17 KST
**입력:** AofSpds/aaaNew@2506468be2eb117a602f3f8222c53b975d2cafec

운영 관점에서 임시안의 가장 큰 보완점은 **백업 실물의 위치, 여러 기기가 작성한 CURRENT의 충돌 처리, 원장 외에 복원에 필요한 메타데이터**입니다. 역할별 JSONL과 잠금은 같은 PC의 동시 쓰기 후보로 계속 검토할 근거가 있지만, 그 실측만으로 전원 장애·여러 기기 동기화·도메인 전체 복원의 안전성까지 확인된 것은 아닙니다.

지정 커밋에서 다음 세 문서를 확인했습니다. 이하 **S1·S2·S3의 실측은 입력 보고서의 결과**이며, 이번 조사에서 새로 실행한 결과가 아닙니다.

| 입력 자료 | 확인한 blob | 근거 등급·날짜 |
|---|---|---|
| S1_STORAGE_FORM.md | 943c0c78eccf… | [저장소·릴리스, 2026-10-17] |
| S2_CONCURRENT_WRITES.md | 5e9dffe61a329… | [저장소·릴리스, 2026-10-17] |
| S3_ROLLUP.md | cc6ec4ccd772… | [저장소·릴리스, 2026-10-17] |

**표기:** 외부 문서의 개정일을 확인한 경우 함께 적었습니다. 확인 2026-10-17은 열람일이며 발행일을 뜻하지 않습니다. 선택지 평가·운영 절차·필드 예시는 별도 표시가 없으면 **[추정, 2026-10-17]**인 조건부 제안입니다.

# Q1. 원장이 모든 판을 보존할 때 아카이브의 정의

## 1) 찾은 것

이 경우 아카이브는 다음 세 용도를 구분하면 명확해집니다.

| 구분 | 의미 | 보존하는 것 |
|---|---|---|
| 원장 이력 | 작성된 모든 판의 기록 | 모든 유효 레코드와 정정 기록 |
| 업무 아카이브 | 특정 시점이나 작업 종료 상태에 이름을 붙인 기록 | 당시 참조한 판, 생성 이유, 필요한 요약·view |
| 백업 | 원장 또는 저장 매체를 잃었을 때 복구할 사본 | 원장과 복원에 필요한 메타데이터 |

S1의 “스트림 자체가 아카이브”는 **모든 판이 보존된다는 의미에서는 맞습니다.** 다만 “그 PR 직전 상태”, “해당 작업을 닫을 때의 상태”, “그날 Owner가 본 도메인 상태”를 쉽게 찾는 기능까지 자동으로 생기지는 않습니다. 이를 별도의 업무 아카이브로 정의할 여지가 있습니다. **[저장소·릴리스, S1, 2026-10-17; 추정, 2026-10-17]**

선행 사례도 이 구분을 뒷받침합니다.

- **Event Sourcing snapshot:** 특정 이벤트 위치까지 계산한 상태를 저장해 재생 시간을 줄입니다. Microsoft 문서는 snapshot을 이벤트 원장의 대체물이 아닌 재생 최적화로 설명합니다. 따라서 원장은 유지하면서 특정 위치의 상태를 별도로 고정하는 방식의 참고 사례입니다. **[공식 문서, 개정 2026-03-28]**  [Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing?utm_source=chatgpt.com)
- **시계열 downsampling:** InfluxDB는 시간 구간별 집계 결과를 별도 bucket에 저장하는 방식을 설명합니다. 메모에 적용한다면 일일 요약·상태 전환 목록에 해당합니다. 다만 요약에서 빠진 정보가 있으므로, 여기서는 원본을 없애는 보존 정책까지 가져오면 안 됩니다. **[공식 문서, 확인 2026-10-17; 적용 판단은 추정]**  [InfluxDB OSS v2 Documentation](https://docs.influxdata.com/influxdb/v2/process-data/common-tasks/downsample-data/?utm_source=chatgpt.com)

또한 JSONL 한 줄에 CURRENT 전체 판본을 저장하는 방식은 **상태 판본 로그**로도 충분히 설명할 수 있습니다. 업무 의도를 나타내는 이벤트를 설계하는 본격적인 Event Sourcing과 동일하다고 전제할 필요는 없습니다. **[추정, 2026-10-17]**

## 2) 선택지 표

| 생성 기준 | 장점 | 놓치는 것·비용 | 맞는 용도 |
|---|---|---|---|
| 갱신마다 | 모든 판을 직접 찾아보기 쉬움 | 원장과 중복되는 파일·INDEX 항목 증가 | 모든 제출 판을 별도 문서로 남겨야 할 때 |
| 상태가 바뀔 때 | ACTIVE→BLOCKED→DONE 같은 전환 추적이 쉬움 | 같은 상태에서 바뀐 중요한 내용은 놓칠 수 있음 | 진행 흐름·막힘 이력 |
| 하루 1회 | 도메인별 일지·모바일 회고가 단순함 | 하루 중 여러 전환을 한 장으로 축약함. 실행 누락·시간대 규칙 필요 | 일일 운영 기록 |
| 작업 단위가 닫힐 때 | 요청·PR·교환 ID와 연결하기 좋음 | 장기 작업·중단 작업은 오랫동안 아카이브가 없을 수 있음 | 완료·승계·심사 증거 |
| 조합 | 종료 기록과 정기 회고를 함께 확보 | 중복 생성 방지와 INDEX 분류 필요 | 여러 역할의 일상 운영 |

## 3) 조건부 권고

**모든 갱신이 이미 원장에 남는다면**, 별도 아카이브는 “이력을 추가로 보존하는 장치”보다 **이력에 이름과 업무 의미를 붙이는 장치**로 검토하는 편이 합리적입니다.

- 작업의 종료·반환·승계가 중요하면 **작업 종료 기준**.
- 도메인 전체의 하루 진행을 보고 싶으면 **일일 도메인 아카이브**.
- 장기 BLOCKED나 재개 시점이 중요하면 **상태 전환 아카이브**를 추가.
- 모든 갱신별 파일 생성은 독립된 요구가 있을 때 비교 대상으로 유지.

**이름 규칙 예시**

```text
20261017T123517Z__role__<scope-id>__task-close__<archive-id>.md
20261017T145900Z__domain__<domain-id>__daily__<archive-id>.md
```

시간은 UTC로 저장하고 표시에는 KST를 쓸 수 있습니다. 파일명에는 Windows에서 문제가 되는 :나 역할 경로의 /를 그대로 넣지 않고, 식별자의 원문은 manifest에 남기는 방식입니다. timestamp만으로 유일성을 확보하거나 기기 간 순서를 정하지는 않습니다.

**INDEX 후보 형식**

| 필드 묶음 | 필요한 이유 |
|---|---|
| archive_id, scope, reason | 어떤 범위의 기록이며 왜 만들었는지 |
| created_at, period_start/end, as_of | 생성 시각·대상 기간·평가 기준 시각 구분 |
| source_heads | 포함한 스트림별 정확한 판과 digest |
| registry_rev, schema_version, projector_version | 당시 역할 구성과 생성 규칙 재현 |
| view_ref, view_digest | 고정한 문서를 찾고 동일성 검사 |
| missing_roles, unresolved_heads | 완전한 기록인지, 빠진 입력·충돌이 있는지 |

기계용 INDEX는 원장 또는 불변 manifest에서 재구성하고, 사람이 읽는 INDEX.md는 생성 view로 둘 수 있습니다. **요약문을 사람이 수정하거나 LLM이 작성한다면 그 요약문 자체도 보존 대상**입니다. 다시 요약해서 같은 문장이 나올 것이라고 기대할 수 없기 때문입니다.

**도메인 아카이브와 역할 아카이브의 관계**

도메인 아카이브는 역할 아카이브의 “최신 파일”을 모으기보다, **각 역할의 정확한 revision 목록을 고정**하는 방식이 재현에 유리합니다. 역할별 아카이브 파일이 없는 판도 원장 참조로 포함할 수 있으므로, 도메인 아카이브 한 번마다 모든 역할의 사본을 새로 만들 필요는 없습니다.

## 4) 모르는 것

- 실제로 자주 찾게 될 단위가 날짜·PR·요청 ID·세션 승계 중 무엇인지.
- 하루 갱신량과 중요한 상태 전환 빈도.
- 과거 화면을 **당시 문서 그대로** 보존해야 하는지, 같은 내용으로 재생성하면 충분한지.
- 당시 역할 등록부와 ROADMAP 판본까지 원장에서 재현 가능한지.

# Q2. Git 참조값, PR별 백업, 복원

## 1) 찾은 것

**참조값은 백업 실물이 아닙니다.** Git에 digest나 snapshot ID를 남겨도 실제 데이터가 다른 매체에 저장되지 않으면 복원할 수 없습니다. git-annex는 기본 metadata 동기화와 content 동기화를 구분하고, DVC도 git push와 dvc push를 구분합니다. **[공식 문서, 확인 2026-10-17]**  [git-annex.branchable.com+1](https://git-annex.branchable.com/walkthrough/?utm_source=chatgpt.com)

따라서 고정 조건의 해석을 나눠야 합니다.

| 조건 해석 | 본문 위치 | Git에 남는 것 | 양립 여부 |
|---|---|---|---|
| PR마다 백업하고 그 참조를 Git에 남김 | Git 밖 로컬 백업 | manifest·digest·backup ID | “Git에는 참조만”과 양립 |
| 도메인 Git은 참조만, 백업용 로컬 Git은 별도 | 별도 로컬 Git | 도메인 Git에는 백업 commit 참조 | “참조만”이 도메인 Git에 한정되면 양립 |
| 모든 Git에 본문 금지이면서 본문도 반드시 Git object로 백업 | 상충 | 상충 | 두 조건을 문자 그대로 동시에 충족할 수 없음 |
| GitHub의 별도 private 저장소에 본문 백업 | GitHub | 메모 본문과 이력 | 본문 Git 보관·외부 보관의 예외가 필요 |

이 조사에서는 어느 해석을 채택했다고 간주하지 않습니다.

## 2) 선택지 표

### 참조값 후보

| 후보 | 식별·검증할 수 있는 것 | 단독으로 부족한 것 |
|---|---|---|
| 스트림 순번 | 특정 스트림에서 어디까지 포함했는지 | 같은 순번의 다른 내용, 기기 분기, 저장소 혼동 |
| 내용 digest | 정해진 바이트열과 복원 결과의 동일성 | 실물의 존재·위치·완전성·업무 의미 |
| Merkle root | 여러 항목의 포함 여부, 정해진 로그 prefix의 일관성 | leaf 규칙·순서·개수·proof·실물 저장소 |
| snapshot 파일 | 해당 시점의 상태 또는 복원 데이터 | 모든 과거 판 포함 여부. 실제 파일을 Git에 넣으면 본문 보관 |

Merkle을 이용한 포함 증명·prefix 일관성 증명의 공식 선행 사례는 RFC 9162입니다. **root만 보관하는 것과 증명·복원에 필요한 데이터를 보관하는 것은 별개**입니다. **[공식 문서, RFC 9162, 2021-12, Experimental RFC]**  [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9162.html?utm_source=chatgpt.com)

### 백업 수단 비교

아래 기능 설명은 **[공식 문서, 확인 2026-10-17]**, 운영 적합성은 **[추정, 2026-10-17]**입니다.

| 수단 | Git와 실물의 관계 | 운영상 장점 | 주요 조건·한계 |
|---|---|---|---|
| JSONL 사본 commit | 실물이 Git object에 들어감 | 기존 Git으로 판본 조회·복원 가능 | 본문 보관 예외 필요. 실행 중 파일을 그대로 git add하면 도메인 전체의 일관된 시점을 보장하지 못함 |
| git-annex | Git에는 pointer, 내용은 annex·별도 대상 | 여러 디스크의 위치·사본 수 추적 | metadata만 동기화하고 백업 완료로 오인하기 쉬움. 현재 판뿐 아니라 과거 content 범위도 확인해야 함.  git-annex.branchable.com +1 |
| DVC | Git에는 .dvc 등, 내용은 cache·local remote | hash 기반 연결, 로컬 폴더·외장 디스크 사용 가능 | dvc push와 Git 전송을 각각 확인. 기본 push는 현재 workspace 참조 기준이며 전체 이력은 별도 범위 지정.  Data Version Control · DVC +1 |
| restic — 로컬 대상 | Git 밖 snapshot, Git에는 그 참조 | Windows 실행 경로, 중복 제거, 암호화, 검증 기능 | 원장을 이해하는 도구는 아니므로 고정한 사본을 입력하는 편이 명확함. 구조 검사와 payload 전체 검사는 다름.  restic 0.19.1 documentation +2 |
| Borg — 로컬 대상 | Git 밖 archive, Git에는 그 참조 | 중복 제거와 archive 검증 | 안정 문서 1.4.5는 Windows의 WSL·Cygwin 경로를 experimental로 설명. HANAL 운용 비용이 추가됨.  Deduplicating Archiver 1.4.5 documentation +1 |
| SQLite backup API | 일관된 DB 사본 생성 | 실행 중 DB의 내용을 SQLite가 이해한 상태에서 복사 | DB가 캐시라면 JSONL 원장 백업을 대체하지 못함. 별도 매체 저장은 추가 단계.  sqlite.org |
| SQLite VACUUM INTO | 별도 DB 파일 생성 | 일관된 snapshot과 압축된 파일 배치 | 원본과 출력의 물리 바이트가 같을 필요는 없음. 생성 완료 후 출력 자체의 digest를 기록해야 함.  sqlite.org |
| Litestream — local file replica | SQLite 복제 데이터는 로컬 대상, Git 연결은 별도 | cloud 없이 SQLite 지속 복제 가능 | JSONL 백업이 아님. Windows 지원 수준·retention·복원 시점의 세밀함을 버전별로 확인해야 함.  Litestream +1 |

**Litestream은 문서와 릴리스의 차이를 남겨야 합니다.**

Windows 가이드와 바이너리는 있지만, 확인한 v0.5.17 릴리스는 Windows를 공식 지원 플랫폼으로 명시하지 않습니다. 또한 설정 문서는 l0-retention: 0을 거부한다고 설명하는 반면, 해당 릴리스에는 이를 disabled로 허용하는 수정이 기록돼 있습니다. 따라서 “영구 보존 불가능” 또는 “retention을 끄면 모든 중간 판이 영구 보존됨”을 단정할 수 없습니다. **[공식 문서, 확인 2026-10-17; 저장소·릴리스, v0.5.17, 확인 2026-10-17]**  [Litestream+2](https://litestream.io/reference/config/?utm_source=chatgpt.com)

**merge=union은 의미적 병합기가 아닙니다.**

Git 공식 문서는 양쪽 줄을 취하면서 충돌 표식을 남기지 않지만, 추가된 줄의 순서가 불규칙해질 수 있어 검증이 필요하다고 설명합니다. JSONL에 적용하면 순번 중복·동일 ID의 다른 내용·인과 순서·깨진 줄을 해결하지 못합니다. “충돌 표시가 안 떴다”가 “원장이 올바르게 합쳐졌다”는 뜻은 아닙니다. **[공식 문서, 확인 2026-10-17; 적용 판단은 추정]**  [gitattributes Documentation](https://git-scm.com/docs/gitattributes?utm_source=chatgpt.com)

## 3) 조건부 권고

### 참조값 조합

현재 규모에서 부분 증명 요구가 크지 않다면, 먼저 비교할 조합은 다음과 같습니다.

```text
store_id
backup_id
scope
stream_id + writer_epoch + last_seq
고정 prefix의 byte_count + digest
registry/schema/projector의 revision
backup_store_id + 실물 locator
검증 결과
```

last_seq는 물리적인 줄 번호와 구분해야 합니다. 또한 **마지막 이벤트 하나의 digest만으로 앞부분 전체의 무결성을 확인할 수는 없습니다.** 전체 prefix digest, segment별 digest 목록, hash chain 또는 Merkle 같은 연결 방법 중 하나가 필요합니다.

Merkle은 기기 간 부분 동기화·부분 검증의 이점이 실제로 필요할 때 확장 후보로 두는 편이 단순합니다.

### PR마다 백업하는 절차 후보

1. **PR과 백업 범위를 고정합니다.**
  backup_id, PR 식별자, 대상 도메인·역할, 코드의 source_commit을 정합니다. 현재 활성 역할뿐 아니라 보존해야 하는 종료 역할·과거 스트림도 범위에 포함합니다.
2. **백업할 기록의 경계를 잡습니다.**
  쓰기 CLI의 신규 쓰기를 잠시 대기시키고 진행 중 쓰기를 끝내거나, 모든 대상 잠금을 일정한 순서로 획득합니다. 각 스트림에서 완성되고 내구성이 확인된 이벤트까지의 순번·바이트 수를 기록합니다. 역할 등록부 변경도 같은 경계에 포함해야 합니다.
3. **그 경계의 고정 사본을 만듭니다.**
  이후 append와 독립된 staging 또는 봉인된 segment를 사용합니다. 스트림별 prefix를 따로 고정할 수도 있지만, 그 경우는 **여러 시점의 조합**일 수 있으므로 “도메인 전체의 단일 시점 snapshot”과 구분합니다.
4. **실물을 백업 대상으로 보내고 다시 읽어 검증합니다.**
  파일 존재·개수·byte 수·digest를 대조합니다. 원장, 역할 등록부, schema, 투영기 revision, 아카이브 manifest, 필요한 원문 객체까지 확인합니다. 같은 물리 디스크의 다른 폴더는 디스크 고장에 대한 별도 사본이 아닙니다.
5. **성공한 실물의 참조를 Git에 기록합니다.**
  payload 저장이 먼저, 완료 참조가 나중입니다. 백업이 실패했는데 Git에는 완료로 기록되는 상태를 피합니다. 반대로 실물 저장 후 Git 기록이 실패하면 기존 실물은 보존하고 기록 단계를 재시도할 수 있습니다.
6. **PR에서 사용할 최종 기준점을 다시 확인합니다.**
  PR 생성 때 한 번 수행할지, 갱신 때마다 수행할지, 병합 직전에 다시 수행할지는 별도 정책입니다. 최소한 “이 PR의 백업”이 어떤 head와 어떤 메모 시점을 가리키는지 명확해야 합니다. PR이 오랫동안 없으면 백업 간격도 길어지므로, PR 주기만으로 일일 복구 수준을 보장할 수는 없습니다.

manifest가 **자신을 포함한 Git commit hash를 자기 내용에 넣는 순환 참조**도 피해야 합니다. 대상 코드의 source_commit과 manifest를 기록한 commit은 다른 값입니다.

### 복원 절차와 완료 판정

1. **정확한 Git commit의 manifest를 읽고, 그 ID의 실물을 확보합니다.** 재현 검증에서 latest에 의존하지 않습니다.
2. **새 폴더에 복원합니다.** 기존 원장을 덮어쓰거나 삭제하지 않습니다.
3. **물리 검증을 수행합니다.** manifest 항목 전체의 존재·크기·digest를 대조하고, 중간 손상·부분 줄·다른 내용의 동일 ID를 검출합니다.
4. **원장 검증을 수행합니다.** 스트림 identity, 순번, 중복, 부모 참조, 누락된 객체를 검사합니다. 재시도에 의한 동일 이벤트와 독립적으로 작성된 유사 내용을 구분합니다.
5. **SQLite와 Markdown을 재생성합니다.** 동일한 역할 등록부·schema·투영기와 **동일한 평가 시각 as_of**를 사용해 CURRENT·ROADMAP·아카이브의 결과를 비교합니다. 평가 시각을 고정하지 않으면 STALE 결과가 달라지는 것이 정상일 수 있습니다.
6. **기기 재개 조건을 확인합니다.** 오래된 백업으로 되돌아온 기기가 기존 순번을 재사용하지 않도록 새 writer epoch 또는 명시적인 승계 처리가 필요합니다.

검증 명령의 의미도 구분해야 합니다.

| 검사 | 확인하는 것 | 확인하지 못하는 것 |
|---|---|---|
| git fsck | Git object의 연결·유효성 | 메모의 업무 의미·외부 payload의 존재 |
| restic check --read-data | 저장된 payload까지 읽는 무결성 검사 | 입력 당시 빠진 파일·도메인 의미 |
| borg check --verify-data | archive 데이터의 무결성 | 올바른 시점·올바른 대상의 백업인지 |
| SQLite integrity_check | DB 구조의 무결성 | 원장과 같은 CURRENT인지, 모든 외래키 오류 |
| 원장 재생 후 비교 | 저장한 기록으로 기대 상태를 만들 수 있는지 | 백업에 애초에 포함하지 않은 기록 |

위 검사 범위는 각 공식 문서로 확인됩니다. 외래키를 사용한다면 SQLite foreign_key_check는 별도 검사입니다. **[공식 문서, 확인 2026-10-17]**  [git-fsck Documentation+3](https://git-scm.com/docs/git-fsck?utm_source=chatgpt.com)

**전판 보존 조건**에서는 과거 판을 정리하는 retention·GC를 기본 절차에 넣지 않는 비교안이 적합합니다. 특히 Borg의 append-only는 archive를 영구히 목록에 유지하는 정책과 같지 않고, DVC 공유 cache의 GC는 다른 프로젝트의 객체 보존에도 영향을 줄 수 있습니다. **[공식 문서, 확인 2026-10-17]**  [Deduplicating Archiver 1.4.5 documentation+1](https://borgbackup.readthedocs.io/en/stable/usage/notes.html?utm_source=chatgpt.com)

## 4) 모르는 것

- “Git에는 참조만”의 범위가 도메인 Git인지 모든 Git인지.
- PR별 백업 범위가 작성 역할·변경 도메인·전체 저장소 중 무엇인지.
- 실제 백업 매체, 누적 증가량, 허용 가능한 복구 시간과 최근 유실 범위.
- JSONL 외의 등록부·이전 영수증·첨부 원문·아카이브 요약이 모두 복원 가능한지.
- Litestream을 사용할 경우 선택 버전에서의 local cleanup·retention·복원 범위.

# Q3. HANAL과 jwDev의 여러 기기 운영

## 1) 찾은 것

**Google Drive 미러와 네트워크 파일시스템은 구분해야 합니다.**

Google 공식 문서상 미러는 로컬 디스크와 cloud에 사본을 두고 변경을 전파합니다. 따라서 SQLite의 “WAL은 network filesystem에서 동작하지 않는다”는 설명만으로 미러 안의 로컬 파일이 항상 손상된다고 결론 내리면 과장입니다. **[공식 문서, 확인 2026-10-17]**  [Google Drive Help+1](https://support.google.com/drive/answer/13401938?hl=en&utm_source=chatgpt.com)

실제 운영 위험은 **두 로컬 사본 사이에 잠금과 트랜잭션이 공유되지 않는 것**입니다.

| 대상 | 우려하는 실패 |
|---|---|
| 같은 역할의 JSONL | 양쪽이 공통 prefix 뒤에 서로 다른 줄을 추가했을 때, 두 레코드가 자동 합쳐진다는 보장이 없음 |
| 잠금 파일 | .lock의 바이트를 복사해도 HANAL의 OS lock 소유 상태가 jwDev에 전달되지 않음 |
| SQLite·WAL | 서로 다른 시점의 DB와 WAL이 전파되거나, 쓰기 도중 복사한 파일이 섞일 수 있음 |
| SQLite 캐시 | 원장은 살아 있어도 오래된 캐시가 들어와 CURRENT를 잘못 보여줄 수 있음 |
| 생성 Markdown | 나중에 도착한 파일이 더 최신 원장을 반영한다는 보장이 없음 |

Windows lock은 열린 파일의 범위에 적용됩니다. SQLite는 실행 중 일반 파일 복사와 DB·journal의 잘못된 조합이 손상을 일으킬 수 있다고 설명합니다. Google 문서에서는 JSONL 병합·분산 잠금·여러 파일의 원자적 전파 보장을 확인하지 못했습니다. **[공식 문서, Microsoft 개정 2021-10-13·SQLite/Google 확인 2026-10-17; 미러 적용은 추정]**  [Microsoft Learn+2](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex?utm_source=chatgpt.com)

또한 jwDev의 dev에 Git 저장소 자체가 포함돼 동기화된다면 메모 외의 위험도 있습니다. Git 공식 FAQ는 cloud 파일 동기화로 Git 저장소를 동기화하지 말고 Git의 push/fetch 방식으로 전송할 것을 설명합니다. **[공식 문서, 확인 2026-10-17]**  [gitfaq Documentation](https://git-scm.com/docs/gitfaq?utm_source=chatgpt.com)

## 2) 선택지 표

| 선택지 | 장점 | 필요한 조건·남는 위험 |
|---|---|---|
| 공통 live 폴더를 Drive 미러 | 기존 사용 흐름과 가까움 | JSONL·lock·SQLite의 공동 쓰기 안전성이 확인되지 않음 |
| 미러 밖 저장소 + Git 전송 | commit 기준으로 전송·검증 가능 | 참조만 Git에 있으면 본문이 이동하지 않음. Q2의 본문 전송 조건 필요 |
| 미러 밖 저장소 + Syncthing | 중앙 본문 저장소 없이 직접 전송 가능 | 동일 파일 공동 수정은 충돌. 완성된 segment·export 전송과 비교해야 함 |
| 역할×기기별 스트림 + 병합 | 오프라인 쓰기 가능, 파일별 작성 기기 구분 | 중복·누락·기기 복제·동일 역할 CURRENT 충돌 규칙 필요 |
| CRDT식 추가 전용 병합 | 전송 순서·중복에 관계없이 기록 집합을 수렴시킬 수 있음 | CURRENT의 유일한 상태를 자동으로 정해주지는 않음 |
| 주 작성 기기 1대 + 다른 기기 읽기·가져오기 | 가장 단순하게 공동 쓰기 충돌 감소 | 주 기기 부재 시 쓰기 제한 또는 명시적 승계 필요 |

Syncthing은 동시 수정된 파일을 sync-conflict 사본으로 보존하고 파일 단위로 교체합니다. **JSONL 레코드를 이해해서 합치는 도구는 아닙니다.** **[공식 문서, 확인 2026-10-17]**  [Syncthing documentation](https://docs.syncthing.net/users/syncing.html?utm_source=chatgpt.com)

**Syncthing의 외부 서비스 여부는 구성에 따라 달라집니다.**

- 기본 global discovery와 relay는 외부 시스템을 이용합니다.
- 전송 내용은 TLS로 보호되지만, discovery·relay 운영자는 연결 메타데이터 일부를 알 수 있습니다.
- LAN 직접 전송만 사용하려면 discovery·relay·NAT 관련 설정을 구분해야 합니다.
- 인터넷 통신 자체도 피하려면 update check·usage/crash reporting까지 확인해야 합니다.

따라서 “중앙 cloud에 본문을 저장하지 않음”과 “외부와 전혀 통신하지 않음”은 서로 다른 조건입니다. **[공식 문서, 확인 2026-10-17]**  [Syncthing documentation+1](https://docs.syncthing.net/users/security.html?utm_source=chatgpt.com)

## 3) 조건부 권고

**두 기기의 독립적인 오프라인 쓰기가 필요하다면**, 역할×기기×writer epoch별로 스트림을 나누고 완성된 segment를 전송하는 후보를 먼저 실측할 가치가 있습니다. 잠금과 SQLite 캐시는 각 기기에 두고, 수신한 데이터는 레코드 단위로 검증해 가져오는 조건입니다.

기기 정보를 넣는 **봉투 필드 예시**는 다음과 같습니다. S3의 엄격한 CURRENT 필드 안에 무작정 추가하는 대신 바깥 envelope로 비교할 수 있습니다.

| 봉투 필드 | 목적 |
|---|---|
| store_id, domain_id, role_id | 다른 저장소·도메인과의 혼합 탐지 |
| device_id | 설치 단위의 안정적인 비밀 아닌 ID |
| device_label | HANAL, jwDev 같은 표시 이름 |
| writer_epoch | 복원·복제·순번 상태 상실 후 기존 writer와 구분 |
| stream_seq, event_id | 해당 스트림의 순번과 재시도 식별 |
| payload_digest, schema_version | 동일 ID의 다른 내용 탐지와 해석 규칙 |
| created_by | 기존 세션 이름 보존 |
| parents 또는 observed_heads | 어떤 이전 판들을 보고 작성했는지 |

기기를 복제하면 ID도 복제될 수 있고, 백업 복원은 순번을 과거로 돌릴 수 있습니다. 이때 기존 writer와 구분할 새 epoch 등이 필요합니다. **동일 event_id에 다른 digest가 들어오면 한쪽을 중복으로 버리지 않고 충돌로 보존**하는 조건도 필요합니다.

**CRDT는 기록 수렴과 상태 선택을 나눠 평가해야 합니다.**

G-Set은 추가된 항목의 합집합으로 수렴하는 선행 사례입니다. 그러나 CURRENT는 값을 덮어쓰는 register에 더 가깝습니다. CRDT 문헌에서도 LWW register와 동시 값을 보존하는 multi-value register를 구분합니다. **[논문, Shapiro et al., 2011-01-13; Preguiça et al., arXiv v1, 2018-05-16]**  [dsf.berkeley.edu+1](https://dsf.berkeley.edu/cs286/papers/crdt-tr2011.pdf?utm_source=chatgpt.com)

예를 들어 HANAL이 DONE, jwDev가 BLOCKED를 서로 보지 못한 상태에서 작성했다면:

- 두 레코드를 모두 보존하는 것은 가능합니다.
- timestamp나 ULID의 정렬만으로 업무적으로 올바른 CURRENT를 결정할 수는 없습니다.
- 동시 판을 표시한 뒤 해결 기록을 추가하거나, 역할별 작성 권한을 한 기기로 제한하는 등의 정책이 필요합니다.

벽시계와 기기 ID를 합쳐 전체 순서를 만들더라도 clock skew 때문에 인과 순서를 보장하지 않는다는 점은 논문에서도 지적합니다. **[논문, 2018-05-16]**  [arxiv.org](https://arxiv.org/html/1805.06358v1?utm_source=chatgpt.com)

S3의 상태값을 곧바로 확장하기보다, 비교 단계에서는 rollup 메타데이터의 unresolved_heads 등으로 동시 판을 나타낼 수 있습니다.

## 4) 모르는 것

- jwDev 경로의 실제 Drive 설정·동기화 범위·파일시스템·client 버전.
- 두 기기에서 같은 역할을 오프라인으로 동시에 작성해야 하는 빈도.
- 현재 Drive client의 JSONL 충돌 처리 및 버전 보존 세부 동작.
- 허용할 외부 통신 범위와 수신 지연.
- 기기별 기록을 병합했을 때 기존 S3 투영기가 같은 결과를 만드는지.

# Q4. 저장소 위치와 세션 권한

## 1) 찾은 것

**폴더 때문에 생기는 승인과 명령 자체의 승인은 별개입니다.**

Claude Code의 additionalDirectories는 추가 경로에 현재 permission mode를 적용합니다. acceptEdits에서 파일 편집이 허용되더라도 모든 임의 CLI 실행까지 자동 승인되는 것은 아닙니다. Desktop은 CLI와 같은 설정 파일을 읽지만, 폴더별로 선택한 모드가 기본 설정보다 우선할 수 있습니다. **[공식 문서, 확인 2026-10-17]**  [Claude Code Docs+1](https://code.claude.com/docs/en/permissions?utm_source=chatgpt.com)

Codex의 sandbox_workspace_write.writable_roots는 sandbox 전체를 해제하지 않고 쓰기 범위를 넓히는 설정입니다. 따라서 “고정 경로이면 항상 매번 승인”보다는 **사전에 허용된 실제 경로인지, 어떤 명령·정책으로 실행하는지에 따라 달라진다**가 정확합니다. **[공식 문서, 확인 2026-10-17]**  [ChatGPT Learn](https://learn.chatgpt.com/docs/sandboxing?utm_source=chatgpt.com)

링크로 이 문제를 해결한다고 가정해서도 안 됩니다. Claude Code 공식 문서는 Windows junction을 포함해 요청 경로와 실제 대상 경로를 검사한다고 명시합니다. **[공식 문서, 확인 2026-10-17]**  [Claude Code Docs](https://code.claude.com/docs/en/permissions?utm_source=chatgpt.com)

## 2) 선택지 표

| 위치 | 저장소 분산 위험 | 승인·설정 | 운영상 위험 |
|---|---|---|---|
| 각 checkout의 Git 제외 폴더 | 높음. worktree마다 다른 실물이 생기기 쉬움 | 현재 작업 범위에 있으면 경로 관련 부담 감소 | checkout 정리·복사에 따라 원장 누락·분기 |
| 도메인별 고정 로컬 폴더 | 낮음 | 도메인별 추가 경로 등록 | 경로 목록 관리 필요, 권한을 좁히기 쉬움 |
| 전체 도메인 공통 고정 경로 1곳 | 낮음 | 각 실행기의 추가 경로 설정 필요 | 전체를 허용하면 다른 도메인에 대한 영향 범위 확대 |
| 세션 폴더의 link/junction → 고정 경로 | 대상이 같으면 낮음 | 실제 대상의 허용은 여전히 필요 | 깨진 링크·대상 변경·제품별 처리 차이 |
| 상위 dev 전체를 workspace로 사용 | 일부 완화 | 넓은 범위를 한 번에 허용 | 다른 저장소까지 권한 확대. jwDev의 Drive 문제는 남음 |

Git worktree는 별도의 작업 파일 공간을 사용합니다. 또한 .gitignore는 보존 장치가 아니며 git clean -x는 ignored 파일도 삭제 대상으로 삼습니다. **[공식 문서, 확인 2026-10-17]**  [git-worktree Documentation+1](https://git-scm.com/docs/git-worktree?utm_source=chatgpt.com)

## 3) 조건부 권고

**공통 메모를 worktree의 수명과 분리하는 것이 우선이라면**, checkout과 Drive 미러 밖의 고정 로컬 디렉터리를 우선 비교할 만합니다. 경로는 기기마다 달라도 논리적인 store_id와 도메인 식별자는 유지할 수 있습니다.

이 후보에서는 다음 조건이 승인 빈도와 분산 위험을 함께 줄입니다.

- 모든 세션이 설정으로 같은 실제 경로를 찾음.
- 쓰기 CLI가 예상한 store_id를 확인함.
- 경로가 없거나 ID가 다르면 현재 작업 폴더에 새 저장소를 조용히 만들지 않음.
- 전체 저장소 허용과 도메인 하위 경로만 허용하는 구성을 비교함.
- native Windows·WSL·Desktop 세션이 같은 파일 집합을 보고 있는지 확인함.

설정 변경을 최소화해야 한다면 작업 폴더 안 후보도 남지만, **worktree별 폴더를 공통 원장으로 착각하지 않게 하는 장치**가 필요합니다. 링크는 경로 입력 편의 후보이며 승인 우회 수단으로 평가하지 않습니다.

또한 “CLI 하나만 사용”은 운영 규칙입니다. 동일 OS 사용자로 원장 폴더에 직접 쓰기 권한을 가진 모든 프로세스를 기술적으로 격리한다는 뜻은 아닙니다.

## 4) 모르는 것

- HANAL의 실제 Claude Desktop·Claude Code·Codex 버전과 모드.
- 사용자 설정·프로젝트 설정·관리 정책의 우선순위.
- native Windows와 WSL 사용 여부.
- Codex의 해당 환경에서 junction·추가 쓰기 경로가 처리되는 실제 방식.
- 기존 worktree들에 메모 사본이 이미 생겼는지, 승인 요청이 실제로 얼마나 반복되는지.

# Q5. 모바일에서 도메인 CURRENT 열람

## 1) 찾은 것

GitHub Mobile은 Android·iOS에서 저장소 탐색을 지원하므로 생성 문서를 읽는 후보가 됩니다. 다만 **요약문도 메모 내용**입니다. private 저장소에 올려도 “Git에는 참조값만”이라는 조건의 예외가 필요합니다. **[공식 문서, 확인 2026-10-17; 조건 판정은 추정]**  [GitHub Docs](https://docs.github.com/en/get-started/using-github/github-mobile?utm_source=chatgpt.com)

LAN 웹은 외부 호스팅 없이 가능하지만 접속 범위를 별도로 다뤄야 합니다. PC의 127.0.0.1에만 바인딩하면 휴대폰에서 접근할 수 없고, 모든 인터페이스에 바인딩했다고 같은 Wi-Fi만 허용되는 것도 아닙니다. Python 표준 HTTP 서버는 심볼릭 링크를 따라 지정 폴더 밖의 파일을 제공할 수 있다고 명시합니다. **[공식 문서, Python 3.13 문서 개정 2026-10-01]**  [Python 3.13.16 documentation](https://docs.python.org/3.13/library/http.server.html?utm_source=chatgpt.com)

## 2) 선택지 표

| 후보 | 외부 의존·조건 | 최신성·사용성 | 보안·노출 위험 |
|---|---|---|---|
| 생성 view를 GitHub에 게시 | 기존 GitHub 이용. 본문 보관 예외 필요 | PC가 꺼져도 마지막 push 열람 가능 | 접근 권한자·복제본·이력에 내용이 남음 |
| LAN 읽기 전용 웹 | 외부 본문 보관 없이 가능 | PC 실행·LAN 연결 중 조회 | 원장 전체를 web root로 잡으면 과다 노출. 접속 범위·인증·전송 보호 필요 |
| 세션 이름에 상태 표기 | 기존 세션 서비스에 제목 전달 | 지금 보이는 화면에서 간단히 확인 | 길이·갱신·누락 한계. 상세 사유를 제목에 쓰면 노출 범위 확대 |
| USB로 정적 HTML/TXT 전달 | 외부 서비스 없이 가능 | 오프라인에서 마지막 사본 열람 | 휴대폰과 파일 앱에 사본이 남음. 자동 최신화 없음 |
| P2P로 생성 view 전달 | 직접 연결 설정에 따라 외부 의존 축소 | 연결됐을 때 갱신, 이후 오프라인 열람 | 모바일 client 관리와 전송 지연. 원장 writer로 참여시킬 필요 없음 |

Android 공식 도움말은 Windows와 USB 파일 전송을 지원합니다. 별도 서버 설치를 전제하지 않는 대안입니다. **[공식 문서, 확인 2026-10-17]**  [Android Help](https://support.google.com/android/answer/9064445?utm_source=chatgpt.com)

Syncthing의 기존 공식 Android wrapper 저장소는 2024-12-03 archive됐습니다. 따라서 모바일 후보에서 “공식 Android 앱을 그대로 쓰면 된다”고 전제하지 않고, community client의 현재 유지보수 상태를 별도 확인해야 합니다. **[저장소·릴리스, 2024-12-03; 확인 2026-10-17]**  [GitHub](https://github.com/syncthing/syncthing-android?utm_source=chatgpt.com)

## 3) 조건부 권고

- **집·사무실 LAN에서 주로 읽는다면:** 별도 생성 export만 제공하는 읽기 전용 웹을 우선 비교할 수 있습니다.
- **외부에서 오프라인 열람이 필요하다면:** 휴대폰에 전달한 정적 사본이 조건에 맞습니다.
- **어디서나 마지막 게시 상태를 읽는 편의를 우선하고 본문 게시 예외를 허용한다면:** GitHub의 제한된 생성 요약을 비교할 수 있습니다.
- **세션 이름만 사용할 수 있는 현재 UI를 보완한다면:** 도메인 / BLOCKED 수 / WAITING 수 / 시각 정도의 신호로 활용할 수 있습니다. 전체 CURRENT의 대체물로 보기는 어렵습니다.

모든 방식에서 다음 두 시간을 구분하는 것이 중요합니다.

| 표시 | 의미 |
|---|---|
| generated_at | 이 화면·문서를 만든 시각 |
| data_as_of와 source_heads | 실제 반영한 기록의 기준점 |

여기에 누락 역할과 기기별 마지막 수신 시각을 표시하면, **오늘 생성했지만 jwDev 데이터는 어제 것인 화면**을 구분할 수 있습니다. S3에 적힌 STALE 문제도 조회 시 나이를 다시 계산하거나, 생성 시각을 명확히 드러내는 방식으로 보완할 수 있습니다. **[저장소·릴리스, S3, 2026-10-17; 추정, 2026-10-17]**

보안 측면에서는 원장·DB·잠금 파일 대신 **허용한 필드로 만든 export만 전달**하는 조건이 적합합니다. 다만 now, next, owner_wait 같은 허용 필드 안의 자유문자열에도 민감 내용이 들어갈 수 있으므로 필드명 제한만으로 시크릿 금지를 보장할 수는 없습니다.

GitHub에 게시한 내용은 복제본·fork·일부 참조에 남을 수 있다는 공식 설명이 있습니다. 전판 보존 조건에서는 게시 전 범위를 줄이는 쪽이 특히 중요합니다. **[공식 문서, 확인 2026-10-17]**  [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository?utm_source=chatgpt.com)

## 4) 모르는 것

- 실제 휴대폰의 파일 열람 기능과 LAN 접근 환경.
- PC 절전 시간, Wi-Fi client isolation, 주소 변경.
- 세션 이름의 자동 갱신 기능·API·동기화 지연.
- 모바일에 공개할 정보 범위와 Git 요약 게시 예외 여부.
- 외부에서 실시간 조회가 필요한지, 마지막 동기화 사본이면 충분한지.

# Q6. 기존 Git 메모의 로컬 저장소 이전

## 1) 찾은 것

이전은 **원본 이력 보존, 내용 가져오기, 현재 쓰기 위치 전환**을 나누면 검증하기 쉽습니다.

Git의 commit·path·blob은 원문의 정확한 위치를 가리킬 수 있습니다. git cat-file은 Git object의 내용을 읽는 수단이며, checkout 파일과 달리 필터·줄바꿈 변환이 적용된 작업 사본을 원문으로 오인하지 않게 할 수 있습니다. **[공식 문서, 확인 2026-10-17]**  [git-cat-file Documentation](https://git-scm.com/docs/git-cat-file?utm_source=chatgpt.com)

다만 git log --follow는 한 파일의 rename 추적 기능입니다. 여러 branch·복사·병합이 있는 저장소 전체 이력을 이것 하나로 완전하게 수집했다고 보면 안 됩니다. **[공식 문서, 확인 2026-10-17]**  [git-log Documentation](https://git-scm.com/docs/git-log?utm_source=chatgpt.com)

현재 판만 가져와도 Git 이력은 그대로 남길 수 있지만, **로컬 저장소만으로 과거를 복원하려면 과거 판도 가져와야 합니다.** 두 요구는 다릅니다.

## 2) 선택지 표

| 가져오기 범위 | 장점 | 한계·조건 |
|---|---|---|
| 고정 commit의 현재 판만 | 작고 빠름. 운영 전환이 쉬움 | 이전 이력은 Git을 계속 참조해야 함 |
| 현재 판 + 지정 기간·업무 이력 | 필요한 과거를 우선 확보 | 수집 범위 밖 이력이 있다는 표시 필요 |
| 선정 파일의 도달 가능한 전체 이력 | 로컬에서 과거 조회·재현 가능 | rename·branch·merge·중복 출처 처리 비용 증가 |
| 단계적 가져오기 | 현재 운영 전환과 이력 수집을 분리 | “현재 판 이전 완료”와 “이력 이전 완료”를 구별해야 함 |

## 3) 조건부 권고

**운영 중단을 줄이면서 이력을 보존하려면**, 도메인별로 단방향 가져오기와 쓰기 전환을 검증하는 절차를 비교할 수 있습니다.

### 이전 절차 후보

1. **대상 목록과 원본 revision을 고정합니다.**
  도메인·역할·repo·path·kind를 기록하고 파일별 기준 commit과 blob을 남깁니다. CURRENT, WORKLOG, ROADMAP, 자유 메모를 구분합니다. 작업 사본의 미커밋 내용은 Git 이력과 별도로 목록화해야 합니다.
2. **원본 이력의 보존 상태를 확인합니다.**
  대상 branch·tag 등 필요한 ref를 유지합니다. 필요하면 Git bundle 같은 독립 사본도 비교할 수 있습니다. Git bundle은 도달 가능한 Git 이력을 보존하는 수단이며, 미커밋 작업 파일·로컬 설정까지 보존하는 것은 아닙니다. **[공식 문서, 확인 2026-10-17]**  [git-bundle Documentation](https://git-scm.com/docs/git-bundle?utm_source=chatgpt.com)
3. **내용을 원본 출처와 함께 가져옵니다.**
  source_repo, source_commit, source_path, source_blob, imported_at, migration_id를 남깁니다. 원본 바이트의 digest와 정규화 후 내용의 digest는 구분합니다.
4. **재실행해도 중복 판이 생기지 않는지 확인합니다.**
  원본 위치를 기준으로 안정적인 import 식별자를 만들 수 있습니다. 내용이 같다는 이유만으로 서로 다른 출처 기록을 없애지 않고, 내용 중복과 출처 중복을 나눕니다.
5. **원본과 가져온 결과를 비교합니다.**
  대상 수·원문 digest·누락·해석 실패를 확인합니다. 가져오기에서 제외한 항목은 내용 대신 제외 상태만 기록하고, 전체 완료로 처리하지 않습니다.
6. **CURRENT의 기준 판을 명시적으로 전환합니다.**
  과거 문서를 오늘 가져왔다는 이유로 imported_at이 최신인 판을 CURRENT로 삼으면 안 됩니다. 운영 기준 branch·commit에서 선택한 판을 초기 CURRENT로 삼고, 과거 판은 이력으로 구분합니다.
7. **Git 원본에 ‘옮겨짐’을 표시하고 쓰기 경로를 전환합니다.**
  기존 본문을 보존한 채 안내를 추가하거나, 원본을 변경하지 않는 별도 MIGRATION_INDEX에서 연결하는 두 방식을 비교할 수 있습니다. 이후 Git 쪽에 늦게 들어온 수정은 추가 import 후보로 탐지하며, 자동으로 현재 로컬 판을 덮어쓰지 않습니다.

“단방향”은 Git의 기존 내용을 로컬로 가져오는 흐름입니다. 로컬 최신 CURRENT를 다시 기존 Git CURRENT에 계속 덮어쓰는 양방향 운용은 이전 완료 상태를 모호하게 만듭니다.

### 도메인별 대상 목록 양식

**파일 하나당 한 행**으로 시작할 수 있습니다.

| 도메인·역할 | repo / path | 분류 | 기준 commit / blob | 이력 범위 | 이전 ID·대상 참조 | 상태 |
|---|---|---|---|---|---|---|
| <domain>/<role> | <repo>/<path> | CURRENT / WORKLOG / ROADMAP / MEMO | <commit>/<blob> | 현재 / 기간 / 전체 | <migration_id>/<target_ref> | 목록화 / 검증 / 전환 |

별도 검증 기록에는 다음을 연결합니다.

```text
원본 byte digest
정규화 규칙과 변환 후 digest
예상 판 수 / 가져온 판 수 / 제외·오류 수
대상 stream·event 참조
검증한 backup_id
전환 기준 commit
옮겨짐 표시 commit
```

### Git에 남길 참조 예시

```text
MIGRATED_TO_LOCAL

migration_id: <id>
store_id: <논리 저장소 ID>
role: <도메인/프로젝트/역할>
source_commit: <표시 추가 전 원본 commit>
source_blob: <원본 blob>
target_ref: <stream / epoch / seq / digest>
backup_ref: <검증된 backup ID>
write_target: LOCAL_ONLY
```

절대 로컬 경로만 남기면 jwDev에서 사용할 수 없으므로 논리적 store_id를 기본으로 하고, 실제 경로는 기기 설정에서 해석하는 후보가 적합합니다. 위 예시는 참조 형식이며 확정 schema는 아닙니다.

## 4) 모르는 것

- 실제 도메인별 대상 파일 수와 분류.
- 미커밋 파일·로컬 branch에만 있는 기록의 규모.
- 모든 과거 판을 로컬로 가져올지, Git 이력을 보존하는 것으로 충분한지.
- 과거 CURRENT들이 같은 역할의 연속 판인지, 서로 다른 작업 사본의 분기인지.
- 기존 세션이 이전 후에도 Git CURRENT를 수정할 가능성과 이를 탐지할 경로.

# Q7. 임시 결과에 대한 운영상 반박·보완

## 1) 찾은 것

S2는 **같은 Windows 로컬 환경에서 잠금 없는 쓰기와 잠금 있는 쓰기의 차이**를 보여줍니다. 이 근거는 유효합니다. 그러나 다음 세 종류의 “손실 없음”은 구분해야 합니다.

- 기록 바이트가 섞이거나 사라지지 않음.
- 성공 응답한 기록이 장애 후에도 남음.
- 두 세션의 의도가 최종 CURRENT에 모두 올바르게 반영됨.

append-only는 첫 번째에 도움을 주지만, 두 번째에는 내구성 경계가, 세 번째에는 오래된 기준 판을 바탕으로 한 갱신의 충돌 처리가 필요합니다. Microsoft의 Event Sourcing 문서도 기존 상태를 동시에 읽은 작성자 사이의 충돌에 optimistic concurrency 검사가 필요하다고 설명합니다. **[저장소·릴리스, S2, 2026-10-17; 공식 문서, 개정 2026-03-28]**  [Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing?utm_source=chatgpt.com)

**별도로, 실측 SQLite 버전은 재검증 조건에 포함할 근거가 있습니다.**

S1·S2의 SQLite는 3.50.4입니다. SQLite 공식 WAL 문서는 3.7.0부터 3.51.2까지 영향 가능성이 있는 **WAL-reset bug**를 설명하고, 3.51.3 이후 및 일부 backport인 3.44.6, 3.50.7에서 수정했다고 명시합니다. 조건은 같은 DB를 연 여러 connection의 write/checkpoint 경합이며 드문 문제로 설명돼 있습니다. 이것이 S2 실측에서 실제 발생했다는 뜻은 아니지만, 후속 실측에서 패치 상태를 기록할 이유는 됩니다. **[공식 문서, 개정 2026-08-25; 입력 버전과의 대조는 추정]**  [sqlite.org](https://www.sqlite.org/wal.html?utm_source=chatgpt.com)

## 2) 선택지 표

| 임시 표현·누락 | 운영 관점의 정정 | 비교할 보완 |
|---|---|---|
| “추가 전용이라 손실이 없다” | 두 판이 모두 남아도 오래된 기준으로 작성한 마지막 CURRENT가 다른 변경을 가릴 수 있음 | base_event·예상 revision 검사 / 동시 판 보존 |
| “CLI 하나” | 같은 CLI를 여러 세션이 실행하면 여러 프로세스임 | 모든 호출의 공통 잠금 준수 / 실제 단일 writer 프로세스 |
| kill 후 잠금이 바로 풀림 | 잠금 해제와 디스크 내구성은 다른 성질임 | 성공 응답 전 flush / 묶음 flush와 durable 경계 표시 |
| 불완전 EOF를 건너뛰고 다음 줄 작성 | 다음 append 후에는 손상 줄이 파일 중간에 남을 수 있음 | 원본 tail 보존 후 새 segment / 명시적인 복구 기록 |
| 역할별 잠금이면 도메인 view도 안전 | 오래된 view 생성기가 늦게 끝나 최신 view를 덮을 수 있음 | 도메인 publish 직렬화 / 생성 세대·source heads 확인 |
| 각 스트림의 끝줄만 읽음 | 같은 스트림에 ROADMAP 등 여러 kind가 들어가면 마지막 줄이 CURRENT가 아닐 수 있음 | kind별 마지막 유효 판 추적. S3의 향후 ROADMAP안과 함께 검증 |
| SQLite는 재생성 캐시 | 순번 발급 상태·import 영수증·중복 제거 정보가 캐시에만 있으면 완전 재생 불가 | 복원 필수 메타데이터를 원장·manifest에 포함 |
| 쓰는 때마다 생성하면 최신 | 입력이 없어도 STALE의 시간은 증가함 | 조회 시 나이 계산 / 기준 시각 표시 |
| WAL은 백업 전에 checkpoint 필요 | backup API·VACUUM INTO까지 포함한 일반 명제로는 틀림 | DB 지원 snapshot / 정지한 일관된 사본 / 캐시 재생성 |
| +2,000/−0이면 백업 비용이 작음 | diff의 모양이며 전체 저장량·전송량·복원 시간의 보장은 아님 | 누적 데이터에서 Git 크기·전송량·복원 시간 측정 |
| 백업 snapshot이 있으면 성공 | 일부 파일이 빠진 snapshot도 만들어질 수 있음 | 종료 상태·manifest coverage·payload 검사 |
| .lock이 남으면 stale lock | S2처럼 상시 파일에 OS lock을 거는 방식이면 파일 존재는 정상임 | 파일 삭제보다 실제 lock 획득·timeout 상태 확인 |

표의 입력 해석과 보완 후보는 **[추정, 2026-10-17]**입니다. 관련 공식 근거는 다음과 같습니다.

- Python은 버퍼 파일을 디스크에 반영할 때 flush() 후 os.fsync()를 설명하며, Windows에서는 _commit()을 호출한다고 명시합니다. **[공식 문서, 확인 2026-10-17]**  [Python 3.13.16 documentation](https://docs.python.org/3.13/library/os.html?utm_source=chatgpt.com)
- Windows는 프로세스 종료 후 OS가 lock을 해제하지만 자원 상태에 따라 해제 완료 시간이 달라질 수 있다고 설명합니다. S2의 세 번 측정값을 보편적인 최대 시간으로 쓸 수는 없습니다. **[공식 문서, 개정 2021-10-13]**  [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex?utm_source=chatgpt.com)
- SQLite의 backup API와 VACUUM INTO는 실행 중 DB의 일관된 사본을 만들 수 있습니다. 반대로 checkpoint를 한 번 수행한 뒤 계속 쓰는 DB 파일만 일반 복사하는 것은 충분한 보장이 아닙니다. **[공식 문서, 확인 2026-10-17]**  [sqlite.org+2](https://www.sqlite.org/backup.html?utm_source=chatgpt.com)
- restic은 읽기 실패가 있는 경우 일부 데이터가 빠진 snapshot과 종료 코드 3을 남길 수 있습니다. **[공식 문서, 0.19.1 문서, 확인 2026-10-17]**  [restic 0.19.1 documentation](https://restic.readthedocs.io/en/stable/040_backup.html?utm_source=chatgpt.com)

S1 자체에서도 Git 정리 후 크기는 JSONL 방식 **3,235 KiB**, SQLite 방식 **2,007 KiB**였습니다. 따라서 이 실측이 입증하는 JSONL의 장점은 우선 **읽을 수 있는 추가 diff**이며, 항상 더 작은 저장소라는 결론은 아닙니다. **[저장소·릴리스, S1, 2026-10-17]**

추가로 digest 정규화도 확인 대상입니다. S1의 UTF-8·NFC·LF·sort_keys를 자체 규칙으로 사용하는 것은 가능하지만, 이것을 그대로 RFC 8785의 JCS와 같다고 부르면 안 됩니다. JCS는 Unicode 문자열을 그대로 보존하며 숫자·속성 정렬 규칙도 별도로 정의합니다. **[공식 문서, RFC 8785, 2020-06]**  [RFC Editor](https://www.rfc-editor.org/rfc/rfc8785?utm_source=chatgpt.com)

## 3) 조건부 권고

임시안의 후속 검증에서는 제품을 더 붙이기 전에 다음 네 경계를 먼저 정리하는 편이 유용합니다.

1. **저장 성공:** 어떤 시점 이후의 기록을 장애 후에도 남는다고 약속하는가.
2. **기록 유효성:** 파싱·schema·digest·순번을 모두 통과했는가.
3. **CURRENT 반영:** 어떤 입력 판과 충돌 처리 규칙으로 현재 상태가 만들어졌는가.
4. **백업 완료:** 어떤 범위의 실물이 어디에 있고, 빈 폴더에서 복원되는가.

이 네 가지가 정의되면 S2의 무손실 결과와 S3의 빠른 view 생성 결과를 운영상의 보장으로 연결할 수 있습니다. 반대로 SQLite가 정말 전적으로 재생성 가능하다면, **캐시를 동기화·백업하는 비용과 원장에서 재생성하는 비용**을 비교하면 됩니다.

## 4) 모르는 것

- S2 구현이 성공 응답 전에 수행하는 실제 flush·fsync 순서.
- disk-full·부분 쓰기·성공 응답 유실 후 재시도의 동작.
- 오래된 CURRENT를 바탕으로 작성한 갱신의 검출 여부.
- 도메인 view의 동시 생성과 publish 순서 역전 처리.
- 캐시 없이 순번·중복 제거·이전 영수증까지 재구성 가능한지.
- 실제 장기 보관량과 아카이브·백업 누적에 따른 운영 비용.

# 우리가 다음에 실측할 것

| # | 실측 | 확인할 결과 |
|---|---|---|
| 1 | 쓰기 내구성과 재시도 — 격리된 시험 데이터에서 쓰기 중단·disk-full·응답 유실·깨진 tail 이후 재개 | 성공 처리한 이벤트의 생존 범위, 중복 방지, 원본 손상 바이트 보존. SQLite 비교 시 각 실행 경로의 실제 버전·패치 상태 기록 |
| 2 | PR 백업과 빈 폴더 복원 — 원장·등록부·ROADMAP·이전 영수증을 포함하고 일부 누락도 주입 | 누락 탐지, byte/digest 일치, 고정 as_of에서 같은 CURRENT 재생성, 복원 시간·추가 저장량 |
| 3 | HANAL↔jwDev 오프라인 작성 후 병합 — 동일 역할의 다른 판, 재전송, 복원된 writer를 포함 | 모든 유효 기록 보존, ID 충돌 탐지, 같은 기록 집합으로 수렴, 동시 CURRENT를 조용히 하나로 덮지 않음 |
| 4 | 새 세션·새 worktree의 위치와 권한 — Claude Desktop·Claude Code·Codex에서 같은 시험 저장소 접근 | 실제 경로·store_id 일치, 원장 사본의 자동 생성 여부, 설정 유지와 승인 요청 빈도 |
| 5 | 도메인 롤업과 모바일 최신성 — 생성 완료 순서 역전, 장치 미수신, 무갱신 시간 경과 | 오래된 view의 퇴행 방지, generated_at과 data_as_of 구분, STALE·누락 표시, 허용된 export만 열람 가능 |
