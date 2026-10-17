# 아카이브 — 이름·목록 양식 초벌 (S4)

- 작성: 2026-10-18, AAA_NEW/MEM_STRG/RSCH · 상태: **초벌**. 설계 확정이 아닙니다.
- 바탕:
  - Pro P2 답 Q1 ([OPERATIONS_RESPONSE_GPT_PRO](OPERATIONS_RESPONSE_GPT_PRO.md))
  - [참조값과 백업·복원 v0.2](BACKUP_RESTORE_REFERENCE_CLAUDE.md)
  - Owner 결정(2026-10-18)
- 전제:
  - 일지(원장)가 이미 모든 판을 보존합니다. 그래서 아카이브는 **이력에 이름과 업무 의미를 붙이는 일**입니다(Pro P2 Q1, 채택).
  - **언제 쌓나**는 정해졌습니다: PR 머지 때 작업 브랜치 묶음을 봉인합니다(Owner).
  - CURRENT는 머지된 main입니다. 그래서 CURRENT의 지난 판은 **Git main 이력이 이미 아카이브**입니다. 따로 사본을 만들지 않습니다.

## 1. 자료 저장소 안의 위치

```text
C:\Users\ms1pk\memstore\
└─ <도메인>\                                   예: rhs, aaa_new
   ├─ projects\<프로젝트>\work\<work_id>\      작업 중 자료 (브랜치 하나 = work_id 하나)
   │  ├─ WORK.txt                               work_id · 브랜치 이름(바뀌면 줄 추가) · 시작 시각 · 주관 PLN
   │  └─ <역할>\                                역할별 자료 그대로 (메모 일지·시험 자료·산출물)
   └─ archive\
      ├─ INDEX.tsv                              기계용 목록 (추가만)
      ├─ INDEX.md                               사람용 목록 (생성 view, 직접 고치지 않음)
      └─ seals\<seal_id>\                       봉인 묶음 (MANIFEST.tsv + bundle\<역할>\…)
```

- **work_id**: 브랜치마다 한 번 만들고 바꾸지 않는 이름입니다(예: `W20261018-a1b2c3`).
  - 브랜치 이름은 `WORK.txt`에만 적습니다.
  - 브랜치 이름에 `/`가 있거나 이름이 바뀌어도 폴더 이름은 그대로입니다. Pro P3가 지적한 이름 바꿔 쓰기 충돌과 브랜치 이름 변경 문제를 피합니다.
- **seal_id**: 봉인할 때마다 새로 만듭니다(예: `20261018T021430Z-f47fec`). 참조값과 백업·복원 v0.2 §2와 같습니다.
- 폴더 이름에는 사람용 설명을 넣지 않습니다. 설명은 목록(INDEX)에 둡니다. Windows 금지 문자나 길이 문제를 피하기 위해서입니다.

## 2. 아카이브 종류

| 종류 | 언제 | 무엇 | 따로 만드나 |
| --- | --- | --- | --- |
| 작업 아카이브 (봉인 묶음) | PR 머지 때 (Owner 결정) | 그 브랜치의 역할별 자료 그대로 | 예 (`seals\`) |
| CURRENT의 지난 판 | 머지할 때마다 | 도메인 CURRENT | **아니요**. Git main 이력이 이미 보존함 |
| 역할 아카이브 | 봉인 때 | 봉인 묶음 안의 `<역할>\` | **아니요**. 봉인 묶음 안에 있음 |
| 프로젝트 아카이브 | 필요할 때 | INDEX를 프로젝트로 거른 목록 | 아니요. 생성 view |
| 도메인 아카이브 | 필요할 때 | 도메인 INDEX 전체 + 도메인 사건(마일스톤, Owner 결정 묶음) | 도메인 사건 줄만 추가(기록 주체는 DPM) |
| 하루 1회 일지 | (선택) | 그날의 봉인·머지·상태 요약 | **기본은 만들지 않음**. INDEX.md로 충분하다고 봄 (Owner 결정 대기) |

## 3. 기계용 목록 `INDEX.tsv` (추가만)

- 한 줄은 **사건 하나**입니다. 상태를 고쳐 쓰지 않고 사건을 덧붙입니다. 그래서 현재 상태는 그 seal_id의 마지막 사건입니다(지우지 않는 원칙과 맞음).
- 칸 (TAB 구분, UTF-8, LF, 머리줄 1개):

| 칸 | 뜻 | 예 |
| --- | --- | --- |
| event_utc | 사건 시각 (UTC) | 2026-10-18T02:14:30Z |
| event | 사건 종류 (아래) | MERGED |
| seal_id | 봉인 번호 (없으면 `-`) | 20261018T021430Z-f47fec |
| work_id | 작업 ID | W20261018-a1b2c3 |
| project | 프로젝트 | order |
| branch | 그때의 브랜치 이름 | feat/f3 |
| roles | 포함 역할 | pln,pmo,rsch |
| manifest_sha256 | 목록표 지문 | b300…86fa |
| git_ref | PR 번호·최종 head·main 반영 커밋·머지 방식 | PR#12 head=abc… main=def… merge |
| by | 기록한 세션 | RHS/ORDER/PLN |
| note | 한 줄 메모 (자유, 짧게) | DPM 승인 확인 |

- 사건 종류:
  - 봉인 흐름: `SEALED` `BACKED_UP` `REF_COMMITTED` `APPROVED` `MERGED`
  - 그 밖: `REVERTED` `CLOSED_UNMERGED` `SUPERSEDED` `INCOMPLETE` `RENAMED` `OWNER_CONFIRMED`
  - 도메인 사건: `MILESTONE` `OWNER_DECISION`
- 위치: 자료 저장소 `<도메인>\archive\INDEX.tsv`. 봉인할 때마다 백업 위치(E:·K:)에도 사본을 둡니다.

## 4. 사람용 목록 `INDEX.md` (생성 view)

- INDEX.tsv에서 만듭니다. 직접 고치지 않습니다.
- 프로젝트별, 최신 순서입니다. 시각은 **KST로 표시**합니다(저장은 UTC).
- 한 줄 모양:

```text
2026-10-18 11:14 KST · order · feat/f3 · MERGED(merge) · pln, pmo, rsch · main def1234 · 봉인 20261018T021430Z-f47fec
```

- 맨 위에 "생성 시각"과 "반영한 마지막 사건 시각"을 따로 적습니다(Pro P2 Q5: generated_at ≠ data_as_of).

## 5. 역할 아카이브와 도메인 아카이브의 관계

- 역할 아카이브는 봉인 묶음 안의 `<역할>\`입니다. 따로 사본을 만들지 않습니다.
- 도메인 아카이브는 **도메인 INDEX 하나**입니다. 모든 프로젝트의 봉인 사건과 도메인 사건을 함께 담습니다. Pro P2가 권한 "역할 판본 목록을 고정"하는 일은 봉인 묶음과 seal_id가 이미 합니다.
- 도메인 사건(마일스톤, Owner 결정 묶음)은 DPM이 기록합니다. 프로젝트 사건은 그 프로젝트의 PLN이 기록합니다.

## 6. 정할 것 (결정 후보)

| # | 질문 | 권고 | 미응답 시 |
| --- | --- | --- | --- |
| 1 | 하루 1회 일지를 만들까 | 만들지 않음. INDEX.md와 GitHub의 main으로 충분 | 만들지 않음 |
| 2 | INDEX.md를 Git에도 올릴까 (모바일 열람) | 올리지 않음. Git에는 참조값만 둔다는 원칙. 필요하면 요약만 | 올리지 않음 |
| 3 | 도메인 사건의 종류 | MILESTONE·OWNER_DECISION 두 개로 시작 | 이 둘로 시작 |
| 4 | work_id를 누가 만드나 | 브랜치를 딸 때 그 프로젝트의 PLN(쓰기 도구가 발급) | 이 안으로 연구 계속 |

## 7. 남은 것

- 실측하지 않았습니다. 다음 실측에서 v2 봉인 시험 결과로 INDEX.tsv와 INDEX.md를 만들어 확인하겠습니다.
- 지금 Git 안에 있는 기존 메모를 옮기는 일(S7)은 이 양식으로 가져옵니다. 이전한 자료에는 `event=IMPORTED`를 둘지 정해야 합니다.
