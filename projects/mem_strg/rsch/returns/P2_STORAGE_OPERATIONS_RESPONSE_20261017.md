# P2 조사 회신 — 에이전트 메모 로컬 저장소의 운영

| 항목 | 기록 |
| --- | --- |
| ACT_ID | `MEM_STRG-PRO-P2-STORAGE-OPERATIONS-20261017-001` |
| 의뢰자 | Owner · 요청 작성 채널 `AAA/NEW/RSCH/MEM_STRG` |
| 조사 기준일 | 2026-10-17 |
| 저장소 기록일 | 2026-10-18 KST |
| 입력 저장소·커밋 | `AofSpds/aaaNew@2506468be2eb117a602f3f8222c53b975d2cafec` |
| 기록 근거 | 조사 회신 후 Owner의 후속 지시: “저장소 기록해주세요” |
| 성격 | 선택지 비교와 조건부 권고. 제품 채택·최종 설계·구현 결정 전의 조사 회신 |
| 기록 범위 | Q1–Q7, 근거 URL·등급·날짜, 다음 실측 항목. 입력 S1–S3의 최신판으로 근거를 바꾸지 않음 |

## 반환 요약

| 구획 | 내용 |
| --- | --- |
| result | 아카이브를 의미 있는 시점의 고정 참조로 구분하고, Git 참조·백업 실체·복원 검증·여러 기기·권한·모바일·이전의 운영 선택지를 비교했다. |
| evidence | 아래 고정 입력 3건과 공식 문서·논문·저장소 및 릴리스. 외부 근거의 확인일은 2026-10-17이며, 발표·갱신일을 확인한 경우 함께 적었다. |
| delta | “추가 전용이면 손실 없음”, “백업 전 checkpoint 필수”, “텍스트라 미러에서 안전”, “merge=union이면 병합 가능”은 조건을 붙이거나 정정해야 한다. SQLite 3.50.4의 WAL 관련 알려진 결함도 실측 조건에 포함해야 한다. |
| open | ‘Git에는 참조값만’의 적용 범위와 ‘PR마다 Git에 백업’의 의미, 오프라인 동시 쓰기 허용 여부, 외부 서비스의 경계, 허용 가능한 백업 간격·복구 시간은 미정이다. |
| learnings | 기록의 보존, 현재 상태의 의미, 다른 기기로의 전송, 사고 후 복원은 서로 다른 보장이다. 하나의 도구나 파일 형식만으로 모두 충족되지 않는다. |
| next | 문서 마지막의 ‘우리가 다음에 실측할 것’ 5개. 이번 회신에서 새 벤치마크·설치·운영 설정 변경은 수행하지 않았다. |

## 입력과 근거 표기

다음 3개 문서만 프로젝트의 실측 입력으로 사용했다. 숫자는 해당 문서가 보고한 결과이며 이번 조사에서 재실행한 값이 아니다. 연결된 벤치마크 스크립트·원자료 전체에 대한 독립 감사까지 수행한 것은 아니다.

| 입력 | 고정 링크 | Git blob SHA | 등급·날짜 |
| --- | --- | --- | --- |
| S1 저장 형태 | [S1_STORAGE_FORM.md][I1] | `943c0c78eccf3c2a687df260332c4a48571e668e` | [저장소·릴리스] 문서 작성 2026-10-17 |
| S2 동시 쓰기 | [S2_CONCURRENT_WRITES.md][I2] | `5e9dffe61a32976f58135b30b56b434d9235c608` | [저장소·릴리스] 문서 작성 2026-10-17 |
| S3 롤업 | [S3_ROLLUP.md][I3] | `cc6ec4ccd77295bba40de46496e87dead20220d6` | [저장소·릴리스] 문서 작성 2026-10-17 |

근거의 등급은 `[공식 문서]`, `[논문]`, `[저장소·릴리스]`, `[2차 출처]`, `[추정]`으로 구분한다. 아래의 `[추정, 2026-10-17]`은 문헌을 이 환경에 적용한 운영상 판단이나 예시이며 실제 구현·실측 결과가 아니다. 공식 문서가 설명하는 일반 기능과 HANAL·jwDev에서 실제로 검증된 동작을 구분한다. 이 회신은 2차 출처에 의존하지 않는다.

## Q1. 아카이브

### 찾은 것

**원장이 모든 판을 보존한다면, 아카이브는 ‘다시 찾을 가치가 있는 시점을 이름 붙여 고정한 기록’으로 정의할 수 있다.** 원장은 모든 이벤트의 이력, 아카이브는 작업 종료·결정·상태 전환 같은 의미 있는 경계, 백업은 원장을 잃었을 때 복구할 별도 사본이다. 이 구분은 선택지이며 확정 설계가 아니다. [추정, 2026-10-17]

이벤트 소싱의 snapshot은 특정 지점까지의 상태를 저장하여 재생 비용을 줄이는 방법이다. 전체 이벤트 이력을 버려야 한다는 뜻이 아니다. 시계열 downsampling도 상세 데이터를 시간 구간의 요약으로 바꾸어 조회 비용을 줄이는 선행 사례지만, 이 의뢰에서는 ‘아무것도 지우지 않음’에 따라 상세 원장을 계속 보존하는 조건으로만 비유할 수 있다. [공식 문서, 확인 2026-10-17: Event Sourcing][E01] · [공식 문서, 확인 2026-10-17: downsampling][E02]

역할 아카이브는 특정 역할의 원장 revision을 가리킨다. 도메인 아카이브는 역할별 revision의 **목록과 조합**을 고정해야 한다. 도메인 파일을 나중에 각 역할의 최신 상태로 다시 만들면 과거 아카이브가 달라진다. `roles.json` 같은 역할 등록부, 스키마, 투영기 버전, `as_of`도 함께 고정해야 S3의 MISSING·STALE·대기 관계를 같은 기준으로 재생할 수 있다. [저장소·릴리스, 2026-10-17: S3][I3] · [추정, 2026-10-17]

### 선택지 표

| 시점 | 남기는 것 | 장점 | 한계·조건 |
| --- | --- | --- | --- |
| 갱신마다 | 매 revision의 상태 또는 view | 어떤 변경도 즉시 열람 가능 | 원장이 이미 가진 이력과 중복된다. 큰 view 사본을 매번 만들면 파일 수·용량 증가 |
| 상태가 바뀔 때 | 전환 전후 revision과 전환 사유 | BLOCKED·DONE 같은 운영 전환을 찾기 좋음 | ACTIVE 안에서 바뀐 중요한 결정은 놓칠 수 있음 |
| 하루 1회 | 정해진 기준시각의 source heads와 요약 | 일일 회고·모바일 조회에 단순함 | 그날의 중간 경계가 희석되고 시각·시간대 규칙 필요 |
| 작업 단위가 닫힐 때 | task/PR/교환 ID, 결과·미해결 항목, source heads | 작업의 의미와 직접 연결됨 | 장기 작업·종료 표시가 빠진 작업의 공백을 보완해야 함 |
| 복합 | 종료·중요 전환 아카이브 + 일일 인덱스 | 사건과 시간 양쪽으로 탐색 가능 | 중복을 없애기 위해 동일 revision 묶음의 ID와 사유 목록 필요 |

표의 비교는 [추정, 2026-10-17]이다. S1은 갱신 10,000건에서 CURRENT 사본 방식 A의 파일 수 10,022개와 JSONL 방식 B의 42개를 보고했다. 이는 매번 파일을 복제할 때의 비용을 보여 주지만 모든 규모에 대한 상한을 증명하지 않는다. [저장소·릴리스, 2026-10-17: S1][I1]

### 조건부 권고

작업 회고가 목적이면 **작업 종료와 중요한 상태 전환**에 이름을 붙이고, 날짜 탐색이 필요하면 일일 INDEX를 더하는 방식이 후보가 된다. 매 갱신 view를 보존해야 할 별도 이유가 없다면 원장 revision 참조만으로 충족되는지 먼저 확인할 수 있다. [추정, 2026-10-17]

이름은 Windows에서 사용할 수 있는 문자로 만들고, 날짜만으로 고유성을 판단하지 않는다. 예시는 다음과 같다. UTC 시각에는 파일명에 쓸 수 없는 콜론을 넣지 않고, 화면에는 KST를 별도 표시한다. `archive_id`는 같은 시각·같은 사유의 충돌을 피하기 위한 독립 식별자다. [추정, 2026-10-17]

```text
2026-10-17T140000Z__mem_strg__rsch__task-close__<archive_id>.md
```

INDEX 후보 형식은 다음과 같다. 모든 역할이 동시에 정지한 일관된 시점인지, 역할마다 다른 시점에서 얻은 참조 벡터인지도 구별한다. [추정, 2026-10-17]

| archive_id | 범위 | 사유·작업 ID | as_of | 고정 source heads | 역할 등록부 revision | view/투영기 revision | backup_id |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<id>` | `<domain 또는 role>` | `<task-close / state-change / daily>` | `<UTC>` | `<stream·epoch·seq·digest 목록의 참조>` | `<digest>` | `<version/digest>` | `<검증된 백업 ID>` |

원장으로부터 완전히 재생 가능한 view는 사본 대신 recipe와 digest를 남길 수 있다. 반대로 사람의 편집이나 LLM의 비결정적 요약이 섞였다면 그 요약 자체가 새로운 보존 대상이다. “나중에 다시 생성하면 같다”고 가정하면 안 된다. [추정, 2026-10-17]

### 모르는 것

Owner가 찾으려는 경계가 PR·작업·결정·교환 중 무엇인지, 하루 갱신량과 아카이브 조회 빈도, 요약의 작성 주체, 역할 간 단일 시점 일관성이 필요한지 아직 정해지지 않았다. 일일 아카이브를 만든다고 일일 백업까지 자동으로 충족되는 것도 아니다.

## Q2. Git 참조값·PR 백업·복원

### 찾은 것

**참조값은 백업 본문이 아니다.** `seq`와 digest를 Git에 커밋해도 해당 JSONL 바이트가 모두 사라지면 원장을 복원할 수 없다. ‘Git에는 참조값만’과 ‘PR마다 Git에 백업’은 Git의 범위를 어떻게 정하느냐에 따라 양립 여부가 달라진다. [추정, 2026-10-17]

| 요구의 해석 | 가능한 운영 의미 | 남는 조건 |
| --- | --- | --- |
| 도메인 Git에는 참조만 | 원장 본문은 별도 로컬 백업 대상에, 도메인 Git에는 검증된 백업 영수증과 참조 | 이것을 ‘Git에 백업’이라고 부를지 Owner의 용어 정리가 필요 |
| 도메인 Git에는 참조만, 별도 백업 Git은 허용 | 별도 로컬 Git 저장소에 JSONL 본문, 도메인 Git에는 그 저장소·커밋·내용 digest 참조 | 별도 Git에 본문을 넣는 예외와 그 Git 자체의 재해 백업이 필요 |
| 모든 Git에 본문 금지, 본문도 Git 객체로 백업 | 두 조건을 동시에 충족할 수 없음 | 둘 중 무엇을 완화할지 결정하기 전에는 제품을 정해도 해결되지 않음 |
| private GitHub에 본문 또는 요약 | 원격 열람과 전송은 쉬움 | 비공개여도 외부 서비스이며, 본문·요약의 Git 저장 예외에 해당 |

위 표는 [추정, 2026-10-17]이다. 로컬 디스크의 별도 폴더는 논리적 백업은 될 수 있지만 같은 물리 디스크의 고장까지 분리하지 않는다.

Git 참조에는 최소한 **어느 저장소·어느 스트림의 어느 범위인지**와 **그 범위의 무결성 값**이 함께 있어야 한다. 마지막 이벤트 하나의 digest만으로 앞의 모든 줄이 변하지 않았음을 증명할 수 없다. Merkle root도 leaf 순서·해시 규칙·tree size·증명 검증 규칙이 정해져야 의미가 있다. [공식 문서, 2021-12·확인 2026-10-17: RFC 9162][E03] · [추정, 2026-10-17]

SQLite는 online backup API나 `VACUUM INTO`로 실행 중인 DB의 일관된 사본을 만들 수 있다. 따라서 “WAL이면 모든 백업 전에 checkpoint가 필수”는 정정해야 한다. 반대로 checkpoint가 끝났다는 이유만으로 이후에도 쓰기 중인 DB 파일 하나를 임의로 복사해도 된다는 뜻은 아니다. WAL과 DB의 관계, 쓰기 중단 또는 공식 백업 방식이 중요하다. [공식 문서, 확인 2026-10-17: backup API][E10] · [VACUUM INTO][E11] · [파일 복사 위험][E12]

### 선택지 표

#### 참조값

| 후보 | 검증할 수 있는 것 | 부족한 것·비용 | 맞는 조건 |
| --- | --- | --- | --- |
| 스트림 순번 | 지정 스트림에서의 위치 | 스트림·writer epoch 없으면 모호하고 내용 변조를 못 잡음 | 사람이 찾는 보조 주소 |
| 개별 내용 digest | 해당 이벤트/객체의 내용 일치 | 이전 전체 이력·백업 존재를 보증하지 않음 | 개별 메모 revision 참조 |
| 고정 prefix의 길이·digest | 특정 byte 범위 전체의 일치 | prefix 전체를 읽어 검증해야 함 | 소규모 원장·간단한 전체 복원 검증 |
| Merkle root | inclusion/consistency proof로 부분 검증 가능 | leaf 정의·순서·증명 저장·구현 비용 | 큰 원장의 부분 검증·부분 전송이 필요할 때 |
| snapshot 파일 | 즉시 열람하거나 복원할 내용 | Git에 본문이 들어가며 원장 전체 보존과는 별개 | 본문 예외가 허용되거나 별도 백업 Git을 쓸 때 |

위 비교는 [공식 문서, 확인 2026-10-17: RFC 9162][E03]와 [추정, 2026-10-17]이다. 단순한 후보 조합은 `store_id + stream_id + writer_epoch + seq + prefix_bytes + digest_algorithm + prefix_digest + backup_id`다. 확정 스키마가 아니며, digest는 실체가 있는 검증된 범위에 대해 계산해야 한다.

#### 백업 수단

| 수단 | 로컬 대상·기능 | Git과의 관계 | 이 환경의 조건·한계 | 근거 |
| --- | --- | --- | --- | --- |
| JSONL 사본 커밋 | 읽기 쉬운 원장 사본, Git 이력으로 revision 보존 | 본문이 Git 객체에 들어감 | 가장 적은 개념으로 시작할 수 있지만 참조 전용 범위와 충돌할 수 있음. 활성 파일 대신 고정 사본을 커밋해야 함 | [저장소·릴리스, 2026-10-17: S1][I1], [추정, 2026-10-17] |
| git-annex | Git의 참조와 대용량 내용 위치를 분리하고 내용 검증 가능 | 기본 `sync`는 내용까지 모두 복제했다는 보장이 아님 | 내용 전송·필요한 과거 revision의 가용성을 별도로 확인. Windows 방식은 실제 HANAL 검증 필요 | [공식 문서, 확인 2026-10-17][E04] [E05] [E06] |
| DVC | 로컬 디렉터리를 remote로 사용할 수 있음 | Git 메타데이터와 DVC 데이터 전송은 별개 | `git push`와 `dvc push`를 혼동하지 말 것. `--all-commits` 같은 범위 옵션과 캐시·remote·GC 정책까지 확인 | [공식 문서, 확인 2026-10-17][E07] [E08] [E09] |
| restic | Windows와 로컬 저장소 지원, snapshot·검증 | Git에는 snapshot/백업 참조를 남길 수 있음 | 일반 검사와 실제 데이터 전체 읽기 검사는 다름. 백업 exit 3은 불완전 snapshot 가능성을 포함하므로 성공 처리하면 안 됨 | [공식 문서, 확인 2026-10-17][E13] [E14] [E15] [E16] |
| Borg | 로컬 repository·archive, 무결성 검사 | Git에는 archive 참조 | 확인한 stable 1.4.5 문서의 Windows WSL/Cygwin 지원은 실험적. append-only 저장 모드만으로 모든 archive가 영구히 조회 가능하다고 볼 수 없음 | [공식 문서, 확인 2026-10-17][E17] [E18] [E19] |
| SQLite backup API / VACUUM INTO | DB의 일관된 snapshot 생성 | 파일을 Git에 넣으면 여전히 바이너리 snapshot | JSONL이 정본이면 이것만으로 원장 백업을 대신할 수 없음. VACUUM 산출물은 원본 DB 파일과 물리 바이트가 달라도 됨 | [공식 문서, 확인 2026-10-17][E10] [E11] |
| Litestream, file target | SQLite 변경을 로컬 대상에 복제하고 복구 | Git에는 복구 범위·참조를 남길 수 있음 | SQLite 정본일 때 역할이 큼. 캐시만 복제하면 JSONL은 보호하지 않음. Windows 지원 수준·보존 규칙은 버전별 확인 필요 | [공식 문서, 확인 2026-10-17][E20] [E21] [E22], [저장소·릴리스, 확인 2026-10-17][E23] |

**Litestream은 문서와 릴리스를 함께 읽어야 한다.** Windows 안내와 배포물이 있어도 확인한 `v0.5.17` 릴리스는 Windows를 공식 지원 대상으로 보지 않는다고 명시한다. 또한 설정 문서는 `l0-retention=0`을 거부한다고 설명하지만 같은 릴리스는 0으로 비활성화하는 동작을 수정했다고 적는다. `retention.enabled=false`도 원격 삭제와 로컬 정리를 동일하게 멈춘다고 단정할 수 없다. “영구 보존 불가능”이나 “한 설정이면 전부 영구 보존” 어느 쪽도 이 환경의 실측 없이 결론 내릴 수 없다. [공식 문서, 확인 2026-10-17][E20] [E22] · [저장소·릴리스, 확인 2026-10-17: v0.5.17][E23]

**`.gitattributes merge=union`은 원장 병합 규칙으로 충분하지 않다.** Git 공식 문서도 충돌 양쪽의 줄이 무작위 순서로 남을 수 있다고 경고한다. 문법상 JSONL이어도 중복 ID, 중복 seq, 끊긴 JSON, 인과관계가 뒤집힌 이벤트, 같은 역할의 경쟁 CURRENT는 해결하지 못한다. Git 텍스트 병합의 성공을 원장 검증 성공으로 삼으면 안 된다. [공식 문서, 확인 2026-10-17: gitattributes][E24] · [추정, 2026-10-17]

검증 수준을 기록할 때는 제품 명령도 구분할 수 있다. `restic check`와 `restic check --read-data`는 실제 백업 데이터를 읽어 확인하는 범위가 다르며, Borg는 `borg check --verify-data`로 데이터 무결성 검증을 추가한다. `git-annex fsck`는 annex 내용 검사에 사용할 수 있다. 이런 제품 검사를 통과하더라도 원장 재생과 CURRENT의 의미 검증은 별도로 필요하다. [공식 문서, 확인 2026-10-17][E15] [E18] [E05] · [추정, 2026-10-17]

### 조건부 권고

작고 로컬 중심인 원장은 **검증 가능한 고정 JSONL 범위 + manifest + 재생성 정보**가 운영의 출발점이 될 수 있다. 제품은 이 백업 실체를 어디에 보관하고 어떻게 옮길지에 따라 비교한다. Merkle 구조나 SQLite 복제는 실제 부분 복원·복제 요구가 드러났을 때 비용을 평가하면 된다. [추정, 2026-10-17]

PR마다 수행할 절차 후보는 다음과 같다. 구현 명령이 아니라 실패를 구분하기 위한 운영 순서다. [추정, 2026-10-17]

1. **대상을 고정한다.** PR 대상 소스 커밋, `store_id`, 도메인·스트림 목록, 등록부·schema·projector revision, 백업 ID를 정한다. manifest가 자신을 담는 Git 커밋의 SHA를 미리 포함하도록 만들면 순환 참조가 생기므로 `source_commit`과 ‘manifest를 기록한 커밋’을 구분한다.
2. **일관성 범위를 고정한다.** 쓰기 gate를 잠시 닫거나 필요한 OS 잠금을 정해진 순서로 획득하여 완료된 기록의 byte 경계를 정한다. 잠금으로 기록 경계만 잡는 것과 도메인 전체의 한 시점을 잡는 것은 다르다. 역할별 다른 시점의 head vector를 허용하면 그 사실을 manifest에 명시한다.
3. **고정된 범위를 별도 staging에 만든다.** 활성 파일에 계속 쓰더라도 복사할 byte prefix가 변하지 않아야 한다. 완성되지 않은 마지막 기록은 정상 이벤트로 세지 않고 원래 바이트와 오류 위치를 별도로 보존한다. 등록부·스키마·재생 코드·필요한 사람이 쓴 요약도 포함한다.
4. **백업 대상에 실체를 기록한다.** 같은 디스크의 다른 폴더, 별도 디스크, 별도 로컬 Git 등 허용된 대상을 사용한다. ‘아무것도 지우지 않음’과 충돌하는 prune/forget/GC/retention 동작을 자동 기본값으로 받아들이지 않는다.
5. **검증한 뒤 영수증을 만든다.** 파일 수·크기·완료 이벤트 수·prefix digest를 확인하고 선택한 제품의 내용 검사를 수행한다. 누락·부분 성공을 정상 성공으로 승격하지 않는다. 복원 위치·백업 ID·검증 수준·완료 시각을 남긴다.
6. **그 뒤 Git 참조를 커밋한다.** 실체와 검증이 완료된 백업만 PR 참조에 연결한다. 실패한 시도는 실패 기록으로 남기고 완료된 백업으로 표시하지 않는다. 이후 쓰기는 다음 백업 범위에 속한다.

복원 절차 후보는 다음과 같다. [추정, 2026-10-17]

1. 기존 저장소를 보존한 채 **새 디렉터리**에서 복구한다. 빈 디렉터리에 복원해야 기존 캐시·파일이 누락을 가려 주지 않는다.
2. Git의 특정 manifest revision에서 `backup_id`와 포함 범위를 읽어 정확한 백업 실체를 가져온다. 단순히 ‘가장 최신 폴더’를 고르지 않는다.
3. 보관된 바이트의 크기·digest를 확인한다. SQLite snapshot은 생성된 snapshot 자체의 digest를 검증하며, VACUUM 전 원본 파일과 같은 바이트가 되기를 요구하지 않는다.
4. JSON 파싱, 스키마, ID 중복과 동일 ID의 상이한 digest, seq 범위, 참조가 가리키는 이벤트의 존재, import provenance를 검사한다. 형식이 깨진 바이트도 버리지 않고 격리·보고한다.
5. 등록부·schema·projector를 고정하여 SQLite와 Markdown을 재생성한다. S3의 STALE은 시각에 따라 달라지므로 백업 때의 `as_of`를 고정한 결과와 현재 시각의 운영 view를 구분한다.
6. 원래 manifest의 논리 상태·집계·참조와 비교하고 실제 CURRENT 조회를 확인한다. `git fsck`는 Git 객체의 연결성과 무결성 검사이며 메모 상태의 의미까지 검사하는 도구가 아니다. [공식 문서, 확인 2026-10-17][E26]

PR만 백업 기회로 삼으면 PR이 없는 기간의 손실 가능 시간은 제한되지 않는다. 허용 가능한 손실 시간(RPO)이 정해지면 일일·주기 백업을 추가할지 평가해야 한다. 백업 매체가 같은 물리 디스크에만 있으면 디스크 고장 시의 복원 시험도 별도로 성립하지 않는다. [추정, 2026-10-17]

### 모르는 것

본문을 담는 별도 Git이 허용되는지, 실제 백업 매체, 목표 RPO·복구 시간(RTO), 원장 증가량, 과거 모든 revision의 오프라인 복원 필요성, Windows에서 각 제품의 실제 동작은 미확인이다. 제품 버전과 보존 설정을 고정한 장기 복구 시험도 이번 조사에서 수행하지 않았다.

## Q3. HANAL·jwDev와 여러 기기

### 찾은 것

**Google Drive 미러는 두 기기가 같은 OS 잠금을 공유하는 파일시스템이 아니다.** 각 기기에서 로컬 파일을 수정한 뒤 변경이 동기화되는 모델이다. Google의 미러 설명은 제공하지만 JSONL 레코드 병합, 두 기기 사이의 OS 잠금, DB·WAL의 원자적 묶음 전송을 보장하는 문서는 확인하지 못했다. [공식 문서, 확인 2026-10-17: Google Drive 미러][E30] · [추정, 2026-10-17]

따라서 HANAL에서 `<role>.jsonl.lock`의 OS 잠금을 잡았어도 jwDev가 자기 로컬 파일에 쓰는 것을 막지 못한다. `.lock` 파일 자체를 동기화하는 것과 커널이 관리하는 잠금 상태의 공유는 다르다. 잠금 파일의 존재 여부만 보고 잠금으로 쓰는 설계도 S2에서 시험한 OS 잠금과 다른 방식이다. [공식 문서, 확인 2026-10-17: LockFileEx][E36] · [저장소·릴리스, 2026-10-17: S2][I2] · [추정, 2026-10-17]

SQLite의 “WAL은 network filesystem에서 작동하지 않는다”는 제한을 Google Drive의 로컬 미러와 동일시하면 설명이 부정확해진다. 미러의 로컬 NTFS DB가 로컬에서 항상 손상된다는 뜻은 아니다. 문제는 활성 DB·WAL·관련 파일이 서로 다른 시점에 전송되거나 원격 수정으로 교체되어 일관된 상태를 잃을 수 있다는 점이다. 이는 SQLite의 쓰기 중 파일 복사 경고와 미러 동작을 함께 적용한 판단이며, jwDev에서 실제 손상을 재현한 결과는 아니다. [공식 문서, 확인 2026-10-17: WAL][E37] · [파일 복사 위험][E12] · [추정, 2026-10-17]

Git도 공식 FAQ에서 클라우드 동기화로 repository를 공유하는 방식의 문제를 경고한다. 저장소를 미러 밖으로 옮기더라도 **Git에 참조만 있다면 Git 동기화만으로 메모 본문은 이동하지 않는다.** [공식 문서, 확인 2026-10-17: Git FAQ][E25] · [추정, 2026-10-17]

### 선택지 표

| 대안 | 동시 쓰기·오프라인 | 장점 | 조건·위험 |
| --- | --- | --- | --- |
| 활성 JSONL·lock·SQLite를 Drive 미러에 둠 | 두 기기가 각각 쓸 수 있으나 공동 잠금은 없음 | 이미 쓰는 동기화 경로 활용 | 충돌·교체 등 파일 동기화 위험과 다중 파일 시점 불일치. client의 구체 처리와 일관성 보장은 미확인 |
| 미러 밖 저장소 + Git 전송 | 명시적인 commit/fetch/병합 단계 | 전달 revision을 추적하기 쉬움 | 본문을 담는 별도 Git 또는 별도 전송 수단 필요. 활성 동일 스트림 텍스트 병합의 의미 검증 필요 |
| Syncthing 등 P2P로 파일 전송 | 오프라인 후 재접속 가능 | 직접 기기 간 전송 가능 | 파일 동기화이며 JSONL 병합 엔진이 아님. 충돌 사본 처리·동기화 경계 필요 |
| 역할×기기×writer epoch별 스트림 + 병합 | 각 기기는 자기 스트림에만 기록 | 서로의 활성 파일을 덮어쓰지 않음 | 봉인된 segment 전송, ID 중복 검사, 현재 상태 충돌 처리가 필요 |
| 추가 전용 집합의 CRDT식 병합 | 이벤트 집합은 합집합으로 수렴 가능 | 재전송·순서 역전에 강한 모델을 만들 수 있음 | 원장 수렴과 CURRENT의 의미상 수렴은 다름. 이벤트 동일성·인과관계·충돌 정책이 필요 |
| 한 기기를 유일한 writer로 두고 나머지는 읽기 | 오프라인 쓰기 제한 | 원장 충돌 문제가 단순해짐 | writer 기기 부재 때 쓰기 불가 또는 임시 요청 큐 필요 |

표는 [공식 문서, 확인 2026-10-17: Syncthing syncing][E31], [논문, 2011-01·확인 2026-10-17: CRDT][E34], [논문, 2018-05·확인 2026-10-17: CRDT][E35] 및 [추정, 2026-10-17]에 근거한다.

Syncthing은 충돌 사본과 임시 파일 후 교체를 다루지만, 두 JSONL의 이벤트를 의미에 맞게 합쳐 주지는 않는다. P2P라는 이름만으로 외부 서비스가 없는 것도 아니다. 기본 discovery·relay 사용은 외부 기반시설 및 일부 연결 메타데이터를 수반한다. 전송 내용 보호와 discovery에 드러나는 정보는 구분해야 한다. LAN 직접 연결과 discovery·relay 제한을 검토할 수 있지만, 외부 통신 전체를 금지하려면 업데이트·보고 등 다른 통신도 확인해야 한다. [공식 문서, 확인 2026-10-17: syncing][E31] · [security][E32] · [tuning][E33]

CRDT의 grow-only set은 원소를 추가하고 합집합으로 병합하는 모델이다. 그러나 HANAL이 `DONE`, jwDev가 같은 역할을 `BLOCKED`로 바꾼 상황에서 두 이벤트를 모두 보존하는 것만으로 CURRENT의 답이 하나로 정해지지는 않는다. 시각이나 ULID의 정렬만으로 승자를 정하면 기기 시계 오차와 경쟁 변경을 가릴 수 있다. 다중 값으로 충돌을 보이거나 명시적 역할 writer 소유권을 두는 방법이 별도로 필요하다. [논문, 2011-01·확인 2026-10-17][E34] · [논문, 2018-05·확인 2026-10-17][E35] · [추정, 2026-10-17]

### 조건부 권고

두 기기에서 오프라인 쓰기를 허용해야 한다면, **활성 저장소는 미러 밖에 두고 기기별로 소유하는 스트림을 전송·병합**하는 후보가 비교하기 쉽다. 전송 대상은 가능하면 더 이상 바뀌지 않는 봉인 segment로 좁힌다. 단일 writer를 유지할 수 있다면 그 제약으로 충돌 비용을 크게 줄일 수 있다. 어느 경우든 동기화 수단을 정하기 전에 허용되는 쓰기 모델을 먼저 구분하는 것이 좋다. [추정, 2026-10-17]

기기 식별자는 사용자 이름·계정 대신 설치 단위의 안정된 ID로 두고, `HANAL`·`jwDev`는 사람이 알아보는 label로 분리하는 방법이 있다. 복제 이미지나 백업 복원으로 두 writer가 같은 ID·seq를 동시에 이어 쓰지 않도록 `writer_epoch` 또는 새 writer ID 발급 규칙이 필요하다. [추정, 2026-10-17]

봉투의 후보 필드는 다음과 같다. **S3의 엄격한 CURRENT payload에 임의 필드를 바로 추가하는 제안이 아니다.** 봉투 스키마와 payload 스키마의 구분·버전 변경을 별도로 검토해야 한다. [저장소·릴리스, 2026-10-17: S3][I3] · [추정, 2026-10-17]

| 봉투 후보 필드 | 목적 |
| --- | --- |
| `store_id`, `domain`, `role` | 어느 저장소·업무 범위인지 식별 |
| `device_id`, `device_label` | 안정된 기기 ID와 사람이 보는 HANAL/jwDev 이름 분리 |
| `writer_epoch`, `seq`, `stream_id` | 복원·재설치 후 순번 재사용을 구분 |
| `event_id`, `content_digest` | 재전송 중복과 동일 ID의 다른 내용을 판별 |
| `schema_version`, `kind` | 봉투와 이벤트 종류의 해석 기준 |
| `created_by`, `created_at` | 작성 세션·기록 시각. 시각만으로 인과 순서를 결정하지 않음 |
| `parents` 또는 관측한 source heads | 어떤 revision을 읽고 변경했는지 추적하는 후보 |

같은 ID와 같은 digest는 재전송으로 처리할 수 있지만, 같은 ID에 다른 digest가 오면 양쪽 원문을 보존하고 충돌로 격리해야 한다. 자동으로 한쪽을 버리는 dedup은 ‘아무것도 지우지 않음’과 의미 보존을 해칠 수 있다. 도메인 CURRENT에는 기기별로 어디까지 관측했는지 표시해야 하며, 오프라인 기기의 최신 상태까지 포함했다고 표현하면 안 된다. [추정, 2026-10-17]

`seq`는 역할×기기×writer epoch로 식별되는 해당 stream 내부에서 비교한다. 서로 다른 stream의 순번을 전역 시간이나 인과 순서로 해석하지 않는다. [추정, 2026-10-17]

### 모르는 것

jwDev의 실제 미러 대상·제외 규칙·Drive 버전, 두 기기의 동시 쓰기 빈도, 역할별 writer 소유권, 오프라인 요구, 네트워크 경로와 외부 discovery 허용 여부를 확인하지 않았다. Drive 충돌·파일 교체·재접속 상황의 실측도 없다. CRDT형 CURRENT 충돌 표현은 현재 S3의 state enum에 이미 구현되어 있다고 볼 수 없다.

## Q4. 저장소 위치와 세션 권한

### 찾은 것

Claude Code는 작업 디렉터리와 additional directories를 작업 범위로 다루지만, 실제 실행 승인에는 permission mode와 도구별 규칙이 함께 작용한다. `additionalDirectories`에 넣었다고 모든 임의 CLI 실행까지 자동 승인되는 것은 아니다. Claude Desktop의 폴더별 설정도 기본 모드와 구분해야 한다. [공식 문서, 확인 2026-10-17: permissions][E38] · [Desktop][E39]

Codex의 `workspace-write`는 쓰기 허용 범위를 제한하며 `sandbox_workspace_write.writable_roots`로 범위를 넓힐 수 있다. sandbox의 쓰기 허용과 승인 정책은 별개이므로 “밖이면 항상 매번 같은 승인 창”처럼 횟수까지 문서만으로 확정할 수 없다. 실제 세션 종류와 설정의 확인이 필요하다. [공식 문서, 확인 2026-10-17: sandboxing][E40] · [저장소·릴리스, 2026-10-17: S2][I2]

세션 폴더 안의 symlink·Windows junction도 권한 경계를 우회하는 장치로 보면 안 된다. Claude Code 공식 문서는 요청 경로와 해석된 실제 경로를 함께 검사한다고 설명한다. Codex의 실제 경로 처리·구성도 직접 확인해야 한다. [공식 문서, 확인 2026-10-17: permissions][E38]

`.gitignore`는 추적 제외 규칙이다. 파일을 보호하거나 백업해 주지 않으며, `git clean -x`처럼 ignored 파일까지 제거하는 명령이 있다. Git worktree마다 작업 파일은 따로 존재하므로 각 worktree의 상대 경로 아래에 저장소를 자동 생성하면 메모가 갈라질 수 있다. [공식 문서, 확인 2026-10-17: git-clean][E28] · [git-worktree][E29] · [추정, 2026-10-17]

### 선택지 표

| 위치 | worktree 분리 위험 | 승인·설정 관점 | 운영상 위험 |
| --- | --- | --- | --- |
| 각 checkout의 Git 제외 폴더 | 높음. 같은 상대 경로가 다른 저장소가 됨 | 기본 작업 범위에 들어갈 가능성이 큼 | checkout 정리·삭제에 따라 손실 가능. 도메인 롤업 누락 |
| worktree들을 포괄하는 공통 상위 폴더 | 모든 세션이 같은 canonical path를 쓰면 낮음 | 상위 폴더가 실제 허용 범위인지 확인 필요 | checkout을 옮기거나 Drive 미러 상위에 놓을 때 경계가 바뀜 |
| checkout·미러 밖의 고정 경로 한 곳 | 낮음 | Claude additionalDirectories·Codex writable_roots 등 설정 필요 가능성 | 모든 도메인에 넓은 쓰기 권한을 줄지, 도메인별로 좁힐지 판단 필요 |
| 세션 폴더 안의 link/junction | 실제 대상이 같으면 낮음 | resolved target 권한이 여전히 중요 | 끊긴 링크·오인된 대상·우회라고 믿는 실수 |
| 로컬 broker/서비스를 통한 한 저장소 접근 | 클라이언트가 한 대상에 붙으면 낮음 | 파일 권한 대신 API·실행 승인 경계가 생김 | 서비스 생명주기·인증·복구 운영이 추가되므로 단순 경로 문제만으로 도입하기에는 비용 큼 |

위 표는 앞의 공식 문서와 [추정, 2026-10-17]에 근거한다. 실제 승인 횟수를 측정한 표는 아니다.

### 조건부 권고

worktree가 많고 여러 도메인이 하나의 원장을 공유해야 한다면 **checkout과 동기화 미러 밖의 canonical 경로**가 저장소 분리를 줄이는 후보가 된다. 예를 들어 `C:\AgentMemo\` 같은 고정 경로를 생각할 수 있지만, 이는 예시이며 실제 생성·설정 변경 지시가 아니다. 전체 저장소를 각 세션의 쓰기 범위에 넣을지 도메인별 하위 경로만 허용할지에 따라 편의와 오작성 영향 범위가 달라진다. [추정, 2026-10-17]

설정 변경을 피해야 한다면 하나의 지정 작업 폴더에서만 쓰게 하거나, 명시적인 작업 범위를 가진 세션 운영이 대안이다. 승인 빈도는 Claude Desktop 세션 여러 개, Claude Code, Codex, 새 worktree 각각에서 별도로 측정해야 한다. [추정, 2026-10-17]

경로 선택과 무관하게 CLI는 시작할 때 canonical path와 `store_id`를 검증하는 편이 좋다. 기대한 경로가 없다는 이유로 현재 작업 폴더에 빈 저장소를 자동 생성하면 조용히 분리된다. 또한 “CLI 하나”는 공통 진입점이라는 의미이며 여러 CLI 프로세스가 동시에 실행될 수 있다. 직접 파일 수정 금지는 관례만으로 강제되지 않는다. [추정, 2026-10-17]

### 모르는 것

HANAL의 실제 Claude Desktop·Codex 버전과 session mode, 조직·사용자 설정, writable roots 구성, Windows junction의 실제 승인 경로, 새 세션에서 설정이 유지되는지는 미실측이다. Owner가 도메인 전체 쓰기 권한과 도메인별 제한 중 어느 범위를 원하는지도 결정되지 않았다.

## Q5. 모바일에서 도메인 CURRENT 열람

### 찾은 것

GitHub Mobile은 저장소를 탐색하는 기능을 제공하므로 생성 Markdown view를 Git에 올려 보는 방법은 가능하다. 다만 private repository여도 외부 서비스에 요약 내용이 저장되며 ‘Git에는 참조값만’의 예외가 된다. private이라는 이유로 복사·알림·계정 권한·보존 문제까지 없어지는 것은 아니다. [공식 문서, 확인 2026-10-17: GitHub Mobile][E41] · [추정, 2026-10-17]

LAN 웹 서버는 휴대폰이 접근할 수 있는 주소에 바인딩하고 방화벽에서 허용해야 한다. `localhost`는 휴대폰이 PC의 서버를 보는 주소가 아니며, 모든 인터페이스에 바인딩했다고 LAN 전용으로 제한되는 것도 아니다. Python의 `http.server`는 symbolic link를 따라갈 수 있으므로 원장 루트를 그대로 내보내는 예시를 운영 서버로 받아들이면 안 된다. [공식 문서, 확인 2026-10-17: http.server][E42] · [Windows Firewall][E43]

S3는 쓰기가 없으면 STALE을 표시하는 view 자체도 갱신되지 않는다고 명시한다. 모바일에서 필요한 것은 화면 생성 시각 하나만이 아니라 **데이터가 어느 시점·어느 기기의 어느 revision까지 반영됐는지**다. [저장소·릴리스, 2026-10-17: S3][I3] · [추정, 2026-10-17]

### 선택지 표

| 방법 | 외부 서비스·접속 조건 | 장점 | 보안·최신성·제약 |
| --- | --- | --- | --- |
| 생성 view를 GitHub에 커밋, GitHub 앱 열람 | GitHub 사용 | 휴대폰에서 익숙하게 조회, revision 고정 가능 | 요약이 Git 이력에 남음. 자유 텍스트·링크·경로의 노출 위험. 외부 서비스·본문 예외 필요 |
| LAN의 읽기 전용 웹 view | PC와 휴대폰이 접근 가능한 망, PC 가동 | 외부 저장 없이 CURRENT 열람 가능 | 별도 export 폴더, 인증·TLS·방화벽 범위·노출 경로 검증 필요. 집 밖에서는 기본적으로 접근 불가 |
| 세션 이름에 상태 | 해당 세션 제품의 메타데이터 경로 | Owner의 현재 사용 방식과 맞고 한눈에 보기 쉬움 | 길이 제한·수동 갱신·최신성·자동화 미확인. 제목 자체가 외부 메타데이터일 수 있음 |
| USB 등으로 정적 HTML/TXT 전달 | PC와 휴대폰 사이 직접 복사 | 클라우드 없이 오프라인 열람 가능 | 마지막 복사 시점 이후는 반영되지 않음. 휴대폰 저장 사본의 관리 필요 |
| P2P로 생성 view만 전달 | 기기 간 연결·모바일 클라이언트 필요 | 원장 없이 요약만 휴대 가능 | discovery·relay 범위 확인. 모바일 구현의 지원·보존·충돌 정책 검증 필요 |

표는 [공식 문서, 확인 2026-10-17: GitHub Mobile][E41], [http.server][E42], [Android USB 전송][E44], [Syncthing security][E32]와 [추정, 2026-10-17]에 근거한다. Syncthing의 공식 Android wrapper 저장소는 2024-12-03에 archive되었다. 커뮤니티 클라이언트가 있다는 사실과 Owner의 휴대폰에서 유지보수·기능이 검증되었다는 것은 구분해야 한다. [저장소·릴리스, archive 2024-12-03·확인 2026-10-17][E45]

### 조건부 권고

같은 망에서만 조회해도 충분하다면 **도메인 CURRENT의 최소 읽기 전용 export**를 제공하는 LAN 방식이 후보가 된다. 원장·SQLite·백업·잠금 파일이 있는 디렉터리를 통째로 웹에 노출하기보다 정해진 파일만 내보내는 구조를 비교한다. 정적 파일이어도 연결과 접근 제어는 별도의 문제다. [추정, 2026-10-17]

밖에서도 읽어야 하고 GitHub 사용을 허용한다면, 공개 가능한 필드만으로 만든 view를 명시적 예외로 검토할 수 있다. Git에 한번 들어간 내용은 나중에 파일만 지워도 과거 커밋·복제본에서 사라지지 않으므로, 이미 저장한 뒤 제거에 의존하기보다 export 단계에서 범위를 정해야 한다. 이번 의뢰는 ‘아무것도 지우지 않음’이므로 새 자료에 시크릿을 넣지 않는 통제가 더 중요하다. [공식 문서, 확인 2026-10-17: GitHub 민감 정보 제거][E46] · [추정, 2026-10-17]

세션 이름은 `도메인 · BLOCKED 수 · Owner 대기 수 · 갱신 시각`처럼 짧은 신호의 후보로 볼 수 있다. 전체 CURRENT를 대신하는 정확한 상태 저장소로 간주하기는 어렵다. 제품명이 붙은 세션 제목이 기기 로컬에만 남는다고 가정해서도 안 된다. [추정, 2026-10-17]

모바일 view의 후보 필드는 도메인·역할·state·간결한 now/next·Owner 대기·`generated_at`·`data_as_of`·반영된 source heads·누락 역할/기기 경고다. 필드 allowlist만으로 자유 텍스트의 시크릿을 제거할 수는 없으므로 민감한 경로·내부 링크·원문 첨부가 섞이는지 export 전 검증이 필요하다. 키·계정·시크릿은 이 조사와 기록에서 요구하거나 사용하지 않았다. [추정, 2026-10-17]

### 모르는 것

Owner의 휴대폰 OS, LAN 밖 열람 필요성, PC 상시 가동 여부, 허용하는 외부 서비스 범위, 세션 이름을 갱신하는 공식 기능과 자동화 가능성, 인증·TLS 구성은 확인하지 않았다. 모바일에서 보이는 내용·링크·STALE의 실제 동작과 시크릿 검사도 실행하지 않았다.

## Q6. 기존 Git 메모의 단방향 이전

### 찾은 것

**이전은 원본 Git 이력을 유지한 채, 출처를 고정하여 새 원장에 한 번씩 가져오는 작업**으로 정의할 수 있다. 파일을 Git에서 삭제하거나 과거 커밋을 다시 쓰는 일이 필수는 아니다. 원본 파일에 안내를 추가하거나 별도 migration index를 두어 이후의 쓰기 위치를 알릴 수 있다. [추정, 2026-10-17]

Git은 commit·tree·blob으로 특정 revision의 파일을 고정할 수 있다. 작업 폴더의 파일은 줄바꿈 변환이나 편집 중인 내용이 섞일 수 있으므로, 가져오기 근거를 `repository + commit + path + blob`로 남기는 것이 추적에 유리하다. `git log --follow`는 단일 파일을 대상으로 하며 모든 저장소의 이름 변경·복사·모든 브랜치 이력을 자동으로 완벽하게 수집하는 도구라고 가정하면 안 된다. [공식 문서, 확인 2026-10-17: git-cat-file][E52] · [git-log][E51] · [추정, 2026-10-17]

Git bundle은 지정된 refs가 가리키는 Git 객체 이력을 보관·전송할 수 있지만, 미커밋 작업 파일이나 모든 로컬 설정을 자동으로 포함하지 않는다. ‘Git 이력 보존’의 범위에는 유지할 refs와 브랜치, 커밋되지 않은 별도 자료의 처리도 필요하다. [공식 문서, 확인 2026-10-17: git-bundle][E27]

### 선택지 표

| 가져오기 범위 | 장점 | 한계·조건 |
| --- | --- | --- |
| 고정 커밋의 현재 파일만 | 빠르게 현재 운영 상태로 전환 가능 | 과거 판은 원래 Git에서 찾아야 함. Git 이력을 보존한다는 조건과는 양립 가능 |
| 정한 기간·작업 범위의 revision | 비용과 필요한 이력 사이를 조절 가능 | 기간 경계와 포함한 브랜치를 기록해야 함 |
| 지정 refs의 전체 관련 파일 이력 | 로컬 원장에서 상세 과거 탐색 가능 | rename·중복 blob·merge DAG·스키마 변화 처리와 출처 매핑 비용 |
| 현재 상태부터 옮긴 뒤 과거를 단계적으로 추가 | 운영 전환과 이력 보강을 나눌 수 있음 | 과거 import가 새 CURRENT로 잘못 승격되지 않도록 의미를 분리해야 함 |

표는 [추정, 2026-10-17]이다. ‘아무것도 지우지 않음’은 반드시 모든 Git revision을 즉시 로컬 원장에도 복제해야 한다는 뜻은 아니다. 원래 Git 이력의 지속적인 가용성과 새 원장에 수집할 범위를 구분할 수 있다.

### 조건부 권고

현재 운영을 빨리 옮기는 것이 우선이면 고정 커밋의 현재 파일부터 단방향으로 가져오고, 필요한 과거 이력을 나중에 추가하는 방식이 후보가 된다. 과거 전체의 로컬 질의가 필수면 처음부터 refs·기간·rename 범위를 명시한 전체 수집이 필요하다. [추정, 2026-10-17]

절차 후보는 다음과 같다. 이번 기록에서 실제 다른 도메인 저장소를 조사하거나 메모를 이동하지는 않았다. [추정, 2026-10-17]

1. **도메인별 대상 목록과 source revision을 고정한다.** 각 파일을 CURRENT·ROADMAP·WORKLOG·일반 메모·기타로 구분하고, 원본 저장소·커밋·경로·blob·이력 범위·소유 역할을 기록한다. 파일 종류와 역할 매핑이 애매하면 자동 CURRENT 승격 대상으로 넣지 않는다.
2. **원래 Git 이력을 보존한다.** 유지할 refs를 명시하고 필요하면 별도 bundle 등으로 복구 가능성을 확인한다. 미커밋 파일은 Git 백업에 들어 있다고 간주하지 않는다. 기존 Git 이력을 rewrite하거나 정리하지 않는다.
3. **원본 바이트와 해석 결과를 분리한다.** 원본 blob의 바이트 digest와 Git blob SHA를 남기고, NFC·LF 등 정규화를 한다면 normalized digest를 별도로 둔다. 원본의 줄바꿈·인코딩·본문을 정규화 결과로 덮어쓰지 않는다.
4. **가져오기 ID를 안정적으로 만든다.** 예를 들어 원본 저장소 식별·커밋·경로·blob·변환 규칙 버전의 조합을 사용하여 같은 작업 재실행을 판별한다. 동일 본문이 여러 경로·커밋에 나타나도 서로 다른 provenance를 없애지 않는다.
5. **import 이벤트로 기록하고 검증한다.** import 영수증에는 `migration_id`, source provenance, target event/stream revision, 원본·변환 digest, 변환기 버전, 성공·보류 상태를 남긴다. 재실행 때 중복 생성과 동일 ID의 상이한 내용을 구분한다.
6. **CURRENT 전환 기준을 명시한다.** `imported_at`은 수집 시각이지 원래 상태의 갱신 시각이 아니다. 어제의 CURRENT를 오늘 가져왔다고 오늘 작성한 live CURRENT보다 최신으로 선택해서는 안 된다. 전환에 사용할 baseline과 그 뒤의 live 이벤트를 구분한다.
7. **복원·대조와 전환 직전 변경 확인 뒤 원본에 안내를 남긴다.** source commit 고정 이후 새 커밋·미커밋 변경이 생겼는지 확인하고 추가 가져오기 또는 보류 상태를 기록한다. 그 뒤 원문을 유지한 채 ‘옮겨짐’ 안내를 덧붙이거나 별도 migration index에서 안내한다. 이 안내를 추가하기 전 source commit을 provenance로 유지한다.
8. **이후 쓰기는 새 원장으로 전환한다.** Git 원본이 다시 수정되면 추가 가져오기 후보로 탐지한다. Git과 원장을 상시 양방향 갱신하는 방식으로 확장하지 않는다. 기존 파일과 이력을 없애지 않는다.

원본에 남길 안내의 예시는 다음과 같다. 아래는 양식이며 실제 경로·ID가 발급되었다는 뜻이 아니다. [추정, 2026-10-17]

```text
이동 안내: 이 파일의 원문과 Git 이력은 보존합니다.
이후 운영 기록의 기준: <store_id / domain / role>
가져온 원본: <repository>@<source_commit>:<path> (blob <blob_sha>)
이전 기록: <migration_id>
새 참조: <stream_id / writer_epoch / seq / content_digest>
검증된 백업 참조: <backup_id 또는 manifest 경로·revision>
전환 시각: <UTC, 표시용 KST>
```

Git 쪽에는 이 안내와 provenance·대상 revision·검증된 백업 참조를 남기는 후보가 적합하다. 내용 digest는 원장 주소와 함께 있어야 하며, `migration_id`만 있고 그 ID를 해석할 기록을 잃는 구조는 피해야 한다. [추정, 2026-10-17]

도메인별 대상 목록은 **파일당 한 행**으로 작성하는 편이 rename·중복·보류를 다루기 쉽다. [추정, 2026-10-17]

| 도메인 | 역할·소유 세션 | 원본 저장소 | 원본 경로 | 종류 | source commit / blob | 이력 범위 | migration_id | 대상 stream/revision | 원본 digest / 변환 규칙 | 검증 상태·비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<domain>` | `<role/session>` | `<owner/repo>` | `<path>` | `<CURRENT/ROADMAP/WORKLOG/메모>` | `<SHA / SHA>` | `<현재/기간/refs>` | `<id>` | `<참조>` | `<digest / version>` | `<예정/가져옴/검증됨/보류>` |

### 모르는 것

실제 도메인별 파일 목록·rename 이력·브랜치 범위·미커밋 자료·문서별 상태 의미는 수집하지 않았다. 기존 메모의 스키마와 작성 시각 신뢰도, 동일 본문이 여러 도메인에 있을 때의 소유 관계, 과거 이력을 어느 깊이까지 가져올지는 미정이다.

## Q7. 임시 결과에 대한 반박과 빠진 운영 위험

### 찾은 것

S2의 잠금 파일·writer별 파일·SQLite에서 **해당 시험 중 손실 0**이 관측된 것은 유효한 비교 근거다. 다만 갑작스러운 전원 상실, 디스크 가득 참, 응답 유실 후 재시도, 두 기기 오프라인 병합, 장기간 백업·복원까지 보증한 결과는 아니다. `append`와 트랜잭션은 서로 다른 실패 범위를 해결하며, 비즈니스 상태의 경쟁 변경까지 자동 해결하지 않는다. [저장소·릴리스, 2026-10-17: S2][I2] · [추정, 2026-10-17]

**실측 환경의 SQLite 3.50.4는 알려진 WAL-reset 결함의 영향 범위에 들어간다.** SQLite 공식 문서는 3.7.0부터 3.51.2까지의 일부 WAL 동시 쓰기·checkpoint 경쟁에서 드물게 손상이 가능했고, 3.51.3 및 backport 3.44.6·3.50.7에서 수정됐다고 설명한다. 수정이 포함된 SQLite 3.51.3의 릴리스일은 2026-03-13이며 해당 WAL 문서는 2026-08-25에 갱신됐다. 이것은 S2에서 실제 손상이 발생했다는 뜻이 아니다. 다음 실측에서 각 프로세스가 실제 로드한 SQLite 버전과 수정 적용 여부를 기록해야 할 이유다. [공식 문서, 갱신 2026-08-25·확인 2026-10-17: WAL §11][E37] · [저장소·릴리스, 2026-10-17: 입력 버전][I1] [I2]

### 선택지 표

| 임시 주장 또는 빠진 위험 | 정정·추가로 볼 것 | 운영 선택지·검증 조건 | 근거 |
| --- | --- | --- | --- |
| 추가 전용이면 손실 없음 | S2의 no-lock append도 손실·깨진 줄이 있었다. 완료 응답과 실제 디스크 지속성도 다름 | OS 잠금, 완료 기록 경계, flush·fsync 정책, 재시도 ID를 구분 | [저장소·릴리스, 2026-10-17][I2]; [공식 문서, 확인 2026-10-17][E47] [E48] |
| OS 잠금이 풀리니 복구 완료 | 잠금 해제는 파일 내용의 완성·영속성을 보증하지 않음. 프로세스 종료 후 해제가 항상 즉각적이라고 일반화할 수 없음 | 잠금 수명과 기록 검증·복구 절차를 별도로 둠 | [공식 문서, 확인 2026-10-17][E36]; [추정, 2026-10-17] |
| CLI 하나이면 writer 하나 | 여러 세션이 같은 CLI 실행 파일을 여러 프로세스로 실행 가능 | 공통 진입점과 직렬화·OS 접근 통제의 책임을 분리 | [추정, 2026-10-17] |
| 레코드가 남으면 CURRENT도 맞음 | 두 writer가 같은 과거 상태를 읽고 각각 갱신하면 기록은 남아도 의미상 갱신이 가려짐 | expected head·부모 revision 검사, 경쟁 상태 표시, 역할 writer 소유권 비교 | [공식 문서, 확인 2026-10-17][E01]; [추정, 2026-10-17] |
| 쓰다 만 끝줄을 건너뛰고 다음 줄에 추가 | 다음 append 뒤에는 깨진 줄이 파일 중간에 남아 ‘끝줄만 건너뜀’ 규칙으로 처리되지 않음 | 원 바이트 보존·오류 offset 기록·새 segment 시작 등 복구 규칙 검토. truncate를 기본으로 하지 않음 | [저장소·릴리스, 2026-10-17][I2]; [추정, 2026-10-17] |
| 역할별 잠금이면 도메인 view도 최신 | A가 옛 head를 읽고 느리게 생성하여 B의 더 최신 view를 나중에 덮어쓸 수 있음 | 도메인 게시 조정, source heads 비교·세대 검사, 안전한 파일 교체를 함께 검토 | [저장소·릴리스, 2026-10-17][I3]; [추정, 2026-10-17] |
| 각 스트림 끝줄이면 CURRENT | 같은 스트림에 `kind=roadmap`을 섞으면 끝줄이 CURRENT라는 전제가 깨짐 | kind별 head 또는 투영 규칙을 먼저 정하고 재검증 | [저장소·릴리스, 2026-10-17][I3]; [추정, 2026-10-17] |
| 쓰기 때만 갱신해도 상태가 최신 | 쓰기가 없을 때 STALE·누락 기기 표시가 낡음 | 읽기 시점 계산·주기 갱신·표시 시각의 역할을 비교 | [저장소·릴리스, 2026-10-17][I3] |
| SQLite는 캐시니까 언제든 버려도 됨 | 등록부·스키마·변환기·dedup/import 정보가 캐시에만 있으면 동일 상태 재생 불가 | 정본으로 남겨야 하는 메타데이터를 정의하고 빈 폴더 재생 시험 | [추정, 2026-10-17] |
| WAL 백업에는 checkpoint 필수 | 공식 backup API·VACUUM INTO는 별도 안전한 방법. checkpoint 직후의 활성 파일 단독 복사도 자동으로 안전하지 않음 | 선택한 백업 방식의 일관성 절차와 실제 복원을 검증 | [공식 문서, 확인 2026-10-17][E10] [E11] [E12] |
| `+2,000/-0`이면 백업 비용도 작음 | 줄 diff는 리뷰 형태다. 저장 용량·압축·전송량·복원 시간을 직접 뜻하지 않음 | S1의 같은 실험에서 Git gc 후 B 3,235 KiB, C 2,007 KiB였다는 점도 함께 평가 | [저장소·릴리스, 2026-10-17][I1] |
| 텍스트·merge=union이면 여러 기기에 안전 | 파일 형식·텍스트 병합은 OS 잠금·인과관계·CURRENT 충돌을 해결하지 않음 | 기기별 소유 스트림과 별도 의미 검증 비교 | [공식 문서, 확인 2026-10-17][E24] [E25] [E31]; [추정, 2026-10-17] |
| NFC·LF·sort_keys면 digest 표준 완성 | 숫자·Unicode·키 정렬·중복 키·정규화 범위가 구현마다 달라질 수 있음. RFC 8785의 JCS는 Unicode를 NFC로 바꾸지 않음 | 원본 byte digest와 명세화한 정규화 digest를 분리하고 같은 입력의 교차 구현 결과 비교 | [공식 문서, 2020-06·확인 2026-10-17][E49]; [추정, 2026-10-17] |
| PR마다 백업이면 충분 | PR 없는 기간과 같은 디스크 고장은 별도 위험 | 허용 RPO에 따른 추가 cadence와 독립 매체 복원 시험 | [추정, 2026-10-17] |
| 백업 제품이 알아서 이력을 보존 | GC·forget·prune·retention은 요구에 따라 과거 가용성을 줄일 수 있음 | ‘아무것도 지우지 않음’의 보존 범위를 각 제품 정책에 대응시켜 검증 | [공식 문서, 확인 2026-10-17][E09] [E19] [E20]; [추정, 2026-10-17] |

### 조건부 권고

현재 B안은 **한 PC의 로컬 정본과 재생성 가능한 view**라는 조건에서 계속 검토할 가치가 있다. 다만 선택을 굳히기 전에 ① 승인된 쓰기가 어떤 실패까지 살아남아야 하는지, ② 모든 재생성 입력이 실제 백업되는지, ③ 두 기기의 경쟁 CURRENT를 어떻게 드러낼지 확인하는 것이 우선이다. [추정, 2026-10-17]

Python의 파일 buffer flush와 `os.fsync`, Windows의 `FlushFileBuffers`, SQLite의 journal·`synchronous` 설정은 적용 위치와 보장 범위가 다르다. “잠금 + append 성공”을 디스크 영속성 보증과 동의어로 쓰지 말고, 응답 시점과 허용 손실을 연결해 실측해야 한다. [공식 문서, 확인 2026-10-17: Python os][E47] · [FlushFileBuffers][E48] · [SQLite PRAGMA][E50]

이번 조사에서 SQLite나 다른 제품의 설치·업데이트를 지시하거나 기존 구현의 채택을 결정하지 않는다. 알려진 결함과 문서·릴리스의 차이는 다음 실측의 버전 조건으로 기록한다. 보존 대상의 손상·충돌은 원 바이트와 출처를 남겨 진단 가능하게 하고, 오류를 없애 보이기 위한 자동 삭제로 처리하지 않는 것이 이 의뢰의 제약에 맞다. [추정, 2026-10-17]

### 모르는 것

한 번의 append가 실제로 어떤 system call과 flush를 거치는지, 디스크 가득 참·전원 상실 때 완료 응답한 기록이 어디까지 남는지, 여러 생성기의 view 게시 경쟁, 장기간 스트림 크기와 롤업 비용, 실제 SQLite runtime별 결함 적용 여부는 확인하지 않았다. 정규화·ID·import 재실행·백업 복원까지 포함한 교차 기기 통합 시험도 아직 없다.

## 근거 목록

아래 외부 링크는 조사 당시 확인한 문서의 주소다. 대부분의 웹 문서는 이후 바뀔 수 있으며 입력 S1–S3와 달리 전부 immutable snapshot은 아니다. 릴리스 태그·RFC·논문 버전이 있는 경우 그 식별자를 남겼다. 날짜를 따로 적지 않은 발표·갱신일은 확인하지 않았으며, 확인일을 발표일로 해석하지 않는다.

| ID | 근거 | 등급 | 날짜·버전 |
| --- | --- | --- | --- |
| I1 | [S1_STORAGE_FORM.md][I1] | [저장소·릴리스] | 작성 2026-10-17; 입력 SHA 고정 |
| I2 | [S2_CONCURRENT_WRITES.md][I2] | [저장소·릴리스] | 작성 2026-10-17; 입력 SHA 고정 |
| I3 | [S3_ROLLUP.md][I3] | [저장소·릴리스] | 작성 2026-10-17; 입력 SHA 고정 |
| E01 | [Microsoft — Event Sourcing pattern][E01] | [공식 문서] | 갱신 2026-03-28; 확인 2026-10-17 |
| E02 | [InfluxDB — Downsample data][E02] | [공식 문서] | v2 문서; 확인 2026-10-17 |
| E03 | [RFC 9162 — Certificate Transparency Version 2.0][E03] | [공식 문서] | 2021-12, Experimental RFC; 확인 2026-10-17 |
| E04 | [git-annex — walkthrough][E04] | [공식 문서] | 확인 2026-10-17 |
| E05 | [git-annex — fsck][E05] | [공식 문서] | 확인 2026-10-17 |
| E06 | [git-annex — Windows installation][E06] | [공식 문서] | 확인 2026-10-17 |
| E07 | [DVC — Remote Storage][E07] | [공식 문서] | 확인 2026-10-17 |
| E08 | [DVC — push][E08] | [공식 문서] | 확인 2026-10-17 |
| E09 | [DVC — gc][E09] | [공식 문서] | 확인 2026-10-17 |
| E10 | [SQLite — Online Backup API][E10] | [공식 문서] | 확인 2026-10-17 |
| E11 | [SQLite — VACUUM / VACUUM INTO][E11] | [공식 문서] | 확인 2026-10-17 |
| E12 | [SQLite — How To Corrupt An SQLite Database File][E12] | [공식 문서] | 확인 2026-10-17 |
| E13 | [restic — Installation][E13] | [공식 문서] | stable 0.19.1 문서; 확인 2026-10-17 |
| E14 | [restic — Preparing a new repository][E14] | [공식 문서] | stable 0.19.1 문서; 확인 2026-10-17 |
| E15 | [restic — Working with repositories][E15] | [공식 문서] | stable 0.19.1 문서; 확인 2026-10-17 |
| E16 | [restic — Backing up][E16] | [공식 문서] | stable 0.19.1 문서; 확인 2026-10-17 |
| E17 | [Borg — Installation][E17] | [공식 문서] | stable 1.4.5 문서; 확인 2026-10-17 |
| E18 | [Borg — borg check][E18] | [공식 문서] | stable 1.4.5 문서; 확인 2026-10-17 |
| E19 | [Borg — Additional Notes][E19] | [공식 문서] | stable 1.4.5 문서; 확인 2026-10-17 |
| E20 | [Litestream — Configuration Reference][E20] | [공식 문서] | 확인 2026-10-17; v0.5.17의 retention 설명과 대조 필요 |
| E21 | [Litestream — Replicating to a local file path][E21] | [공식 문서] | 확인 2026-10-17 |
| E22 | [Litestream — Running on Windows][E22] | [공식 문서] | 확인 2026-10-17 |
| E23 | [Litestream — Release v0.5.17][E23] | [저장소·릴리스] | tag v0.5.17; 확인 2026-10-17 |
| E24 | [Git — gitattributes][E24] | [공식 문서] | union merge 항목; 확인 2026-10-17 |
| E25 | [Git — FAQ][E25] | [공식 문서] | cloud syncing 항목; 확인 2026-10-17 |
| E26 | [Git — git-fsck][E26] | [공식 문서] | 확인 2026-10-17 |
| E27 | [Git — git-bundle][E27] | [공식 문서] | 확인 2026-10-17 |
| E28 | [Git — git-clean][E28] | [공식 문서] | 확인 2026-10-17 |
| E29 | [Git — git-worktree][E29] | [공식 문서] | 확인 2026-10-17 |
| E30 | [Google Drive — Stream and mirror files][E30] | [공식 문서] | 확인 2026-10-17 |
| E31 | [Syncthing — Understanding Synchronization][E31] | [공식 문서] | 확인 2026-10-17 |
| E32 | [Syncthing — Security Principles][E32] | [공식 문서] | 확인 2026-10-17 |
| E33 | [Syncthing — Tuning][E33] | [공식 문서] | 확인 2026-10-17 |
| E34 | [Shapiro et al. — A comprehensive study of Convergent and Commutative Replicated Data Types][E34] | [논문] | INRIA RR-7506, v1 2011-01-13; 확인 2026-10-17 |
| E35 | [Preguiça, Baquero, Shapiro — Conflict-free Replicated Data Types][E35] | [논문] | arXiv:1805.06358v1, 2018-05-16; 확인 2026-10-17 |
| E36 | [Microsoft — LockFileEx][E36] | [공식 문서] | 갱신 2021-10-13; 확인 2026-10-17 |
| E37 | [SQLite — Write-Ahead Logging][E37] | [공식 문서] | WAL-reset §11 포함, 갱신 2026-08-25; 확인 2026-10-17 |
| E38 | [Claude Code — Permissions][E38] | [공식 문서] | 확인 2026-10-17 |
| E39 | [Claude Code — Desktop][E39] | [공식 문서] | 확인 2026-10-17 |
| E40 | [Codex — Sandboxing][E40] | [공식 문서] | 확인 2026-10-17 |
| E41 | [GitHub — GitHub Mobile][E41] | [공식 문서] | 확인 2026-10-17 |
| E42 | [Python — http.server][E42] | [공식 문서] | Python 3.13 문서, 갱신 2026-10-01; 확인 2026-10-17 |
| E43 | [Microsoft — Windows Firewall rules][E43] | [공식 문서] | 확인 2026-10-17 |
| E44 | [Android — Transfer files between your computer and Android device][E44] | [공식 문서] | 확인 2026-10-17 |
| E45 | [Syncthing Android wrapper repository][E45] | [저장소·릴리스] | archive 2024-12-03; 확인 2026-10-17 |
| E46 | [GitHub — Removing sensitive data from a repository][E46] | [공식 문서] | 확인 2026-10-17 |
| E47 | [Python — os, fsync][E47] | [공식 문서] | Python 3.13 문서; 확인 2026-10-17 |
| E48 | [Microsoft — FlushFileBuffers][E48] | [공식 문서] | 갱신 2021-10-13; 확인 2026-10-17 |
| E49 | [RFC 8785 — JSON Canonicalization Scheme][E49] | [공식 문서] | 2020-06; 확인 2026-10-17 |
| E50 | [SQLite — PRAGMA statements][E50] | [공식 문서] | 확인 2026-10-17 |
| E51 | [Git — git-log][E51] | [공식 문서] | 확인 2026-10-17 |
| E52 | [Git — git-cat-file][E52] | [공식 문서] | 확인 2026-10-17 |

[I1]: https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S1_STORAGE_FORM.md
[I2]: https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S2_CONCURRENT_WRITES.md
[I3]: https://github.com/AofSpds/aaaNew/blob/2506468be2eb117a602f3f8222c53b975d2cafec/projects/mem_strg/rsch/research/S3_ROLLUP.md
[E01]: https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing
[E02]: https://docs.influxdata.com/influxdb/v2/process-data/common-tasks/downsample-data/
[E03]: https://www.rfc-editor.org/rfc/rfc9162.html
[E04]: https://git-annex.branchable.com/walkthrough/
[E05]: https://git-annex.branchable.com/git-annex-fsck/
[E06]: https://git-annex.branchable.com/install/Windows/
[E07]: https://doc.dvc.org/user-guide/data-management/remote-storage
[E08]: https://doc.dvc.org/command-reference/push
[E09]: https://doc.dvc.org/command-reference/gc
[E10]: https://www.sqlite.org/backup.html
[E11]: https://www.sqlite.org/lang_vacuum.html
[E12]: https://www.sqlite.org/howtocorrupt.html
[E13]: https://restic.readthedocs.io/en/stable/020_installation.html
[E14]: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
[E15]: https://restic.readthedocs.io/en/stable/045_working_with_repos.html
[E16]: https://restic.readthedocs.io/en/stable/040_backup.html
[E17]: https://borgbackup.readthedocs.io/en/stable/installation.html
[E18]: https://borgbackup.readthedocs.io/en/stable/usage/check.html
[E19]: https://borgbackup.readthedocs.io/en/stable/usage/notes.html
[E20]: https://litestream.io/reference/config/
[E21]: https://litestream.io/guides/file/
[E22]: https://litestream.io/guides/windows/
[E23]: https://github.com/benbjohnson/litestream/releases/tag/v0.5.17
[E24]: https://git-scm.com/docs/gitattributes
[E25]: https://git-scm.com/docs/gitfaq
[E26]: https://git-scm.com/docs/git-fsck
[E27]: https://git-scm.com/docs/git-bundle
[E28]: https://git-scm.com/docs/git-clean
[E29]: https://git-scm.com/docs/git-worktree
[E30]: https://support.google.com/drive/answer/13401938?hl=en
[E31]: https://docs.syncthing.net/users/syncing.html
[E32]: https://docs.syncthing.net/users/security.html
[E33]: https://docs.syncthing.net/users/tuning.html
[E34]: https://dsf.berkeley.edu/cs286/papers/crdt-tr2011.pdf
[E35]: https://arxiv.org/html/1805.06358v1
[E36]: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex
[E37]: https://www.sqlite.org/wal.html
[E38]: https://code.claude.com/docs/en/permissions
[E39]: https://code.claude.com/docs/en/desktop
[E40]: https://learn.chatgpt.com/docs/sandboxing
[E41]: https://docs.github.com/en/get-started/using-github/github-mobile
[E42]: https://docs.python.org/3.13/library/http.server.html
[E43]: https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/rules
[E44]: https://support.google.com/android/answer/9064445
[E45]: https://github.com/syncthing/syncthing-android
[E46]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
[E47]: https://docs.python.org/3.13/library/os.html
[E48]: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers
[E49]: https://www.rfc-editor.org/rfc/rfc8785
[E50]: https://www.sqlite.org/pragma.html
[E51]: https://git-scm.com/docs/git-log
[E52]: https://git-scm.com/docs/git-cat-file

## 우리가 다음에 실측할 것

1. **쓰기 완료·장애·재시도:** 잠금 중/기록 중/완료 응답 전후 종료, 디스크 부족, 응답 유실 후 같은 ID 재전송, 불완전 tail을 주입한다. 완료로 응답한 이벤트의 생존·중복·원 바이트 보존을 확인하고, 프로세스별 실제 SQLite 버전·flush 조건·WAL-reset 수정 적용 여부를 기록한다.
2. **PR 백업과 빈 디렉터리 복원:** 쓰기 중 고정 범위 백업 1회와 새 폴더 복원 1회를 수행한다. 원장·등록부·schema·projector·import provenance를 함께 검증하고, 같은 `as_of`의 CURRENT가 재생되는지와 별도 매체의 용량·복구 시간을 잰다.
3. **두 기기 오프라인 후 재합류:** HANAL·jwDev가 같은 역할을 경쟁 갱신하고 재전송·순서 역전·writer ID 복제 상태로 합류하게 한다. 이벤트 집합 보존과 CURRENT 충돌 표시, 봉인 segment 전송의 누락 탐지, 기기별 반영 범위를 확인한다.
4. **새 세션·새 worktree의 위치와 승인:** Claude Desktop·Claude Code·Codex에서 같은 canonical `store_id`를 보는지 확인하고 승인 횟수·설정 유지·resolved link 대상·경로 누락 때의 동작을 기록한다. 실수로 별도 저장소가 자동 생성되는지 확인한다.
5. **롤업 게시와 모바일 view:** 오래 걸린 생성기가 최신 view를 덮어쓰는 순서, ROADMAP과 CURRENT 혼합, 쓰기 없는 시간의 STALE, 누락 기기 표시를 시험한다. 휴대폰에서는 `generated_at`과 `data_as_of`, 접근 범위, 허용한 export 파일·필드만 보이는지 확인한다.

