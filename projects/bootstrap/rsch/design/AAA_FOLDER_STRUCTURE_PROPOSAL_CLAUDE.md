# aaa 폴더 구조 제안 v0.1

```text
STATUS = 제안 / F1 결정됨, F2–F7 대기 / 옮긴 것 없음
WRITER = AAA_NEW/BTSR/RSCH (bootstrap rsch)
요청 = Owner 2026-10-17 20:30 KST "rhs/dpm 과 연락해서 … aaa의 폴더 구조를 정할 수 있도록 제안합니다."
근거 = 이 세션의 Owner 원문 + RHS/DPM 회신(2026-10-17) + RHS 문서(rghtHpSnpr-wt-plnw, 읽기만)
UPDATED = 2026-10-17 KST
```

## 0. Owner 결정 기록

| # | 결정 | 원문 (2026-10-17, 이 세션) |
|---|---|---|
| F1 | 가안(장부 방식). 도메인 저장소는 제자리, aaa `domains/`는 장부 | "장부방식은 맞습니다." |
| F1-a | Git에는 각 도메인의 Current(갱신된 현재 상태)를 작성한다 | "기본적으로는 GIT에는 각 도메인의 커런트- 갱신된 현재 상태를 만들어 작성하며" |
| F1-b | 작업대는 백업이 충분히 된 로컬 저장소를 쓴다 (연구는 MEM_STRG) | "작업대는 기본적으로 백업이 충분히 된 로컬 저장소를 활용할 계획이예요." / "일단 지금은 로컬 저장소로 기억을 만들려고 합니다. 그 연구를 MEM_STRG에 넘겼습니다." |

| F1-c | Current는 역할마다 분리되어 있다. README 같은 것이다 | "커런트는 분리되어 있어요 기본적으로 역할마다 분리되어 있습니다. 어떻게 보면 READ ME 같은겁니다. 그부분에 대한 발화는 RHS/DPM이 갖고 있을겁니다." |

정정: 앞서 "도메인 Current를 어느 Git에 한 장으로 쓰나"를 물었는데, 이는 F1-c와 맞지 않아 거둔다. Current 관련 RHS 원문을 RHS/DPM에 요청함(2026-10-17). 받은 뒤 §3의 Current 자리를 다시 쓴다.

### 0.1 Current — RHS 원문 (RHS/DPM 회신 2026-10-17, 시각 기록 없음, 순서만)

- 모형: ① "이력과 current 인거죠." ② "커런트는 계속 갱신이 되며 갱신된 커런트는 적절한 형태로 아카이브는 차곡 차곡 쌓인다" ③ 아카이브는 역할별, 도메인은 도메인 아카이브 ④ 로드맵은 역할마다 자기 범위 ⑤ "각 역할별 current가 모여서 dpm이 가지고 있는 domain 커런트가 나옵니다."
- 저장: ⑥–⑨ "git은 참조값만 에이전트 메모는 될수 있으면 분리" — RHS/DPM은 Current를 "메모"에 넣어 로컬로 읽었으나, F1-a("GIT에는 각 도메인의 커런트")가 이를 바로잡음(RHS/DPM 동의, Owner 확인 예정).
- "README 같은 것"은 이 세션에서 처음 나온 말씀(F1-c).
- RHS 미결 9가지 중 Current 관련: 롤업 시점·담당, 머리 칸, Current 덮어씀(고쳐 쓰지 않음 범위), WORKLOG와 아카이브 합칠지, 검증 대기 칸, 역할 폴더 양식 보강 (`STRUCTURE_SIMULATION_REVIEW_v0.1` §4, RHS main bc344e2).

- 추가 원문 (이 세션, 2026-10-17~18): "CURRENT 도 종류가 있어요." / "역할별/도메인 별/도메인 모듈별 로 조립해서 런타임 컨텍스트에 넣어주는걸 계획하고 있어요."
  - 이해: Current 종류 = 역할별 · 도메인별 · 도메인 모듈별. 세션이 시작·실행될 때 필요한 조각을 골라 조립해 컨텍스트에 넣는다.
  - bootstrap 연구와 연결: R02 시작 시 기억 전달, runtime-intervention(SessionStart·UserPromptSubmit additionalContext로 주입 실측), 관계 엔진 단계 4 view 생성.
  - 구조에 주는 영향: Current는 조립 단위 → 종류마다 고정 머리 칸·크기 한도·식별자가 필요. "모듈"이 무엇인지는 Owner 설명 대기.
  - Owner 확인: "네 에이전트 호출되고 나서 훅을 걸때 조립될 각 부분의 모듈화된 메모리 뷰입니다." → 도메인 모듈 = 도메인 구성 부품(예: RHS order의 engine·host·observer·control, aaa apps/의 memory-engine). Current 세 종류는 모두 "모듈화된 메모리 뷰"이고, 에이전트가 호출된 뒤 훅에서 조립된다.
  - 제안 (결정 전): 조각은 각 도메인 저장소에 둔다(역할 Current는 역할 폴더, 도메인 Current는 DPM 칸, 모듈 Current는 모듈 옆). aaa 장부 `domains/<도메인>/DOMAIN.md`에는 조각 위치 목록을 둔다. 조립기(훅에서 도는 프로그램)는 aaa 코어 실행부 `apps/`에 둔다.
  - Owner (2026-10-18): "네 CORE에 대한 고민이 필요합니다." → 위 자리 제안(조각은 도메인 저장소, 장부엔 위치 목록, 조립기는 apps/)에 동의. 다음 주제 = CORE.
  - Owner (2026-10-18) CORE 정의: "CORE는 이 프로젝트(워크 플로우)와 역할에 대한 기본 모델입니다." → CORE = 프로젝트(워크플로)·역할의 기본 모델. 실행부(apps/)는 이 모델을 돌리는 프로그램. 기존 ROLE_WORKFLOW_DESIGN v0.2(역할 pln·sub_pln·rsch·impl+iva)는 RHS 결정(DPM > PLN > RSCH/ARCH/PMO, V 비상설) 이전 판이라 맞춰 다시 써야 함.
  - 아래 0.2는 종류 구분 전 초안.

### 0.2 Current 모형 — 이해한 대로 (Owner 확인 대기)

| | Git (참조·현재 상태) | 로컬 저장소 (작업대, 백업 충분히) |
|---|---|---|
| 역할 | 역할 폴더마다 `CURRENT.md` 한 장 — README처럼 이 역할이 무엇이고 지금 어디까지 왔고 다음은 무엇인지. 덮어씀 | 작업 메모, 진행 기록, 중간 산출물 |
| 도메인 | 역할 Current가 모여 도메인 Current (DPM이 모음) | — |
| 지난 판 | Git 이력이 지난 Current를 이미 남김 → 아카이브를 따로 둘지는 열린 것 | |

주의: Current를 Git에 두면 갱신마다 커밋이 생긴다. RHS 하루 병합 65회의 원인. 대책 후보: Current는 상태가 바뀔 때만 갱신, 커밋은 묶어서, 역할마다 브랜치·병합 의식 없이 한 사본에서 자기 경로만 커밋.

## 1. Owner 원문 — aaaNew (이 세션, 시간은 KST)

| 시각 | 원문 |
|---|---|
| 10:03 | "rsch 폴더 아래에 현황판을 두시면 되겠네요." |
| 10:06 | "폴더 별로 정리가 필요합니다. rsch 루트로 표현하겠습니다." |
| 10:26 | "기존 앱에 대한 조사자료는 폴더 만들어서 아래에 두어야 될듯 해요." |
| 11:12 | "apps 는 aaa core 실행부가 들어가게 될것입니다." / "현재 진행중인 다른 모든 프로젝트가 이 구조로 따라오게 될겁니다." / "bootsrap은 프로젝트 명입니다." / "projects 폴더를 aaaNew 바로 위에 만드시고 bootsrap은 projects 안에 들어갑니다." |
| 11:40 | "domains 폴더를  루트에 만들어주세요." |
| 18:14 | "bootstrap은 따로 입니다. 병렬이라고 했잖아요." / "별도 프로젝트입니다." (mem_strg) |
| 20:25 | "mem_strg는 여기서 관리하는게 아닙니다." |
| 20:30 | "aaa 는 모든 도메인의 코어입니다. 여기서 모든게 관리 됩니다." / "domains 는 기본적으로 각 domain 들을 모두 관리하게 됩니다." / "현재 채널은 그 aaa 의 코어가 되는 부트스트랩을 만드는 rsch이며 rhs처럼 pln과 dpm을 만들게 됩니다." |

## 2. RHS에서 가져온 것

### 2.1 RHS Owner 결정 중 aaa가 따를 것 (원문은 RHS `planning/STRUCTURE_DECISIONS.md` §1)

| RHS # | 내용 | aaa에 적용 |
|---|---|---|
| 1, 2 | 지우지 않는다 / 결정은 Owner, 역할은 문의만 | 그대로 |
| 7, 8 | 기본 트리 DPM > PLN > PMO/RSCH, 역할마다 검증자 페어 / 프로젝트 일은 PLN | 그대로 |
| 11, 12 | 연구·기획·설계·구현 단계, ARCH는 PLN 아래 존치 | 그대로 |
| 13 | 검증자(V)는 모두 비상설 | 그대로 (V 폴더는 열 때 만든다) |
| 14, 15 | 코드 작업은 PMO / 시험은 RSCH 안 | 그대로 |
| 17, 18 | 세션 이름에 위계 / 개설 위치·플랫폼 자유 | 그대로 (순서는 §6 F6) |
| 20–23 | projects = 작업 단위(PLN 하나), 앱 아님 / 이력·현황·계획은 각 프로젝트 안 | 그대로 |
| 25 | apps = 앱만 | aaa는 "aaa core 실행부" (Owner 11:12) |
| 28 | 외부 서비스 이름으로 폴더를 짓지 않는다 | 그대로 |
| 29–33 | 역할마다 Current(덮어씀)·로드맵(자기 범위)·아카이브(차곡차곡), 역할 → 도메인 롤업 | 그대로 |
| 36–39 | 자주 고치는 메모는 로컬 저장소 + 백업, Git은 참조값만, 메모로 수십 번 병합하지 않음 | 그대로. 저장소 형태는 mem_strg 연구 결과를 받는다 |

### 2.2 RHS/DPM이 "aaa(도메인 공통)가 가지면 좋겠다"고 한 규칙 (DPM 의견, Owner 결정 아님)

역할 트리·검증자 페어 / 프로젝트 = PLN 단위 / 역할 폴더 양식(Current·로드맵·아카이브, 롤업) / 이력 원칙(역할당 작업 사본 하나, 묶음은 브랜치, 고정은 커밋) / Git은 참조값만 / 세션 이름 위계 / 외부 도메인 이름 규칙 / 삭제 없음·결정은 Owner / Owner 원문 장부 규칙 / 다른 도메인 방식을 들일 때 가져올 것·버릴 것 검토.

RHS에 남는 것: 제품 코드 배치(`apps/order` 등), 프로젝트 목록(order, sim), 엔진 자리.

### 2.3 RHS 실패 원인 → aaa가 처음부터 막을 것 (RHS `HISTORY_FAILURE_CAUSES_20261017.md`)

| 실측 (RHS 10-17) | 원인 | aaa 규칙 |
|---|---|---|
| 저장소 사본 약 20개, AAA 사본 65개 | 묶음마다 폴더로 고정, 도구 기본값(세션마다 사본) | 저장소 작업 사본은 기기당 하나. 고정은 커밋 번호로. `.claude/worktrees` 쓰지 않음 |
| 하루 병합 36회(한 세션)·65회(전체) | 메모를 Git으로 관리 | 메모는 로컬 저장소, Git에는 참조값만 |
| Current에 `§0.000000`까지 누적 | 아카이브 칸이 없음 | 역할 폴더 양식에 archive를 처음부터 둠 |
| 도메인 Current 10-04 이후 그대로 | 롤업 담당 없음 | DPM이 롤업·빠짐 확인 |
| AAA 습관(작업별 사본)까지 이관 | 참조처를 거르지 않음 | 옛 AAA(`dev\AAA`)는 읽기 참조만, 들일 때 가져올 것·버릴 것 목록 + Owner 확인 |

## 3. 제안 구조

```text
aaaNew/                              aaa = 모든 도메인의 코어 (Git = 참조·버전 관리)
├─ AGENTS.md  CLAUDE.md  README.md   모든 세션 진입점 (새로, 경로·읽는 순서만)
├─ apps/                             aaa core 실행부 — 코드만 ✔Owner
│  └─ <구성요소>/                     예: memory-engine (bootstrap PMO가 씀)
├─ domains/                          모든 도메인 관리 ✔Owner
│  ├─ INDEX.md                       도메인 등록부 (aaa, rhs, live_counting …)
│  ├─ aaa/                           aaa 자신의 도메인 칸 (RHS domain\ 과 같은 모양)
│  │  ├─ core/                       모든 도메인이 따르는 공통 규칙·양식 (§2.2)
│  │  ├─ records/                    Owner 원문 장부 (aaa)
│  │  ├─ dpm/                        aaa DPM — 도메인 정본(마일스톤·결정 기록)
│  │  └─ coordination/               도메인을 넘는 요청·회신, 세션 개설 패킷
│  └─ rhs/                           RHS 장부 칸 ✔F1 (live_counting 등도 같은 모양)
│     ├─ DOMAIN.md                   저장소 주소·로컬 위치·세션 접두사·DPM 세션·적용한 core 판과 예외
│     └─ (Current)                   역할마다 분리, README 같은 것 ✔F1-c — 자리는 RHS 원문 받은 뒤
├─ projects/                         aaa의 프로젝트 (프로젝트 하나 = PLN 하나) ✔Owner
│  ├─ INDEX.md                       프로젝트 등록부
│  ├─ bootstrap/                     aaa core를 만드는 프로젝트
│  │  ├─ pln/                        계획·배정·수용 기록
│  │  ├─ arch/                       설계 정본 (예: 코딩 기준)
│  │  ├─ pmo/                        구현 묶음 기록·증거 요약 (코드는 apps/)
│  │  └─ rsch/                       연구·시험, 현황판 ✔Owner
│  │     └─ ref-apps/                외부 참조 앱 ✔Owner
│  └─ mem_strg/                      별도 프로젝트 (이 세션이 관리하지 않음)
└─ (Git 밖) 로컬 저장소               작업대 = 역할별 메모·판·archive, 백업 충분히 ✔F1-b. 형태는 mem_strg 연구
```

- 검증자(plnv·archv·pmov·rschv, dpmv)는 비상설이다. 폴더는 처음 열 때 만들고 판정만 쌓는다.
- 각 역할 폴더의 Git 쪽: README(역할·범위) + 정본 산출물 + 요청·회신. 메모(CURRENT·ROADMAP·archive)는 로컬 저장소, PR 때 Git으로 백업(RHS #37).
- 저장소가 정해지기 전까지 임시: 역할 폴더 `CURRENT.md` 한 장(덮어씀)과 `archive/`, 커밋은 묶어서 한 번에.

## 4. 칸마다 누가 쓰나

| 칸 | 쓰는 역할 | 비고 |
|---|---|---|
| `domains/aaa/core/` | aaa DPM (Owner 결정을 옮겨 적음) | 다른 도메인은 읽고 따른다. 판 번호를 붙인다 |
| `domains/aaa/records/` | aaa DPM | 고쳐 쓰지 않음 |
| `domains/aaa/dpm/`, `coordination/` | aaa DPM | |
| `domains/<도메인>/` | 그 도메인 DPM (AAA DPM과 합의해 기록) ✔R1 | AAA DPM 총괄. 도메인 저장소 안은 건드리지 않는다 |
| `projects/INDEX.md` | aaa DPM | |
| `projects/bootstrap/<역할>/` | 그 역할 | 프로젝트 안 빠짐 확인은 bootstrap PLN |
| `apps/` | bootstrap PMO | 코드 작업은 PMO만 |

## 5. 지금 → 제안 (옮기지 않음, 표만)

| 지금 | 제안 자리 | 시점 |
|---|---|---|
| `domains/` (비어 있음) | `domains/INDEX.md`, `aaa/`, `rhs/` | F1·F2 결정 뒤 |
| `projects/bootstrap/pln/` | 그대로 | — |
| `projects/bootstrap/rsch/` (연구·현황판·ref-apps) | 그대로 | — |
| `projects/bootstrap/memory-engine/` (README·CODING_STANDARDS, 코드 없음) | 코드 → `apps/memory-engine/`, 코딩 기준 → `bootstrap/arch/` | 코드가 생길 때 / C1–C5 결정 뒤 |
| `projects/bootstrap/memory-store/` (README만) | 로컬 저장소 (mem_strg 결과) | mem_strg 회신 뒤 |
| `rsch/design/ROLE_WORKFLOW_DESIGN_CLAUDE.md` | 그대로(연구 산출물). Owner가 고른 부분만 `domains/aaa/core/`로 | E1–E9 결정 뒤 |
| 옛 AAA (`dev\AAA`) | 읽기 참조만 | — |

## 6. Owner께 여쭐 것 (하나씩)

| # | 질문 | 권고 |
|---|---|---|
| ~~F1~~ ✔ | `domains/`의 "관리"는 등록·규칙 적용 칸인가, 도메인 저장소를 이 아래로 옮기는 것인가 | **등록·규칙 칸.** 도메인 저장소는 제자리(`dev\rghtHpSnpr` 등). 옮기면 RHS가 지금 정하는 경로(#24)와 진행 중 병합이 흔들리고, aaaNew 저장소 안에 다른 저장소가 들어가 Git이 꼬인다 |
| F2 | aaa 자신의 도메인 칸 | `domains/aaa/` (aaa도 도메인 중 하나로 등록). 맨 위에 RHS처럼 `domain/`을 따로 두면 `domains/`와 이름이 겹친다 |
| F3 | 공통 규칙 자리 | `domains/aaa/core/`. RHS `domain/core`에는 RHS만의 규칙과 "aaa core 몇 판을 따른다"만 둔다 |
| F4 | bootstrap 역할 폴더 | `pln/ arch/ pmo/ rsch/`. 구성요소 폴더(memory-engine·memory-store)는 §5대로 나중에 나눈다 |
| F5 | aaa DPM·bootstrap PLN 개설 | DPM 정본 자리 `domains/aaa/dpm/`, bootstrap PLN 작업대 `projects/bootstrap/pln/`. 개설 패킷은 이 채널이 만들고 Owner가 연다 |
| ~~F6~~ ✔ (CORE R4로 결정: `<도메인>/<프로젝트>/<역할>`, 도메인 AAA_NEW) | 세션 이름 순서 | 지금 aaa는 `AAA/NEW/RSCH/BTSR`(역할/프로젝트), RHS는 `RHS/order/PMO`(프로젝트/역할). 한쪽으로 맞춤. 권고: 도메인/프로젝트/역할 → `AAA/NEW/BTSR/RSCH`, DPM은 `AAA/NEW/DPM`. RHS의 대소문자 질문도 같이 |
| F7 | 메모 매체가 정해지기 전 임시 방식 | §3 임시안 (역할 폴더 `CURRENT.md` + `archive/`, 커밋은 묶어서) |

## 7. 알아둘 위험

- 다른 기기(jwDev)의 `C:\Users\ms1pk\dev`는 Google Drive 미러로 보고됐다(RHS). aaaNew도 그 아래라면 `.git` 부분 동기화로 깨질 수 있다. [미확인 — jwDev에서 확인 필요]
- RHS/DPM 회신의 일부 근거(WORKLOG 10-17 절, HISTORY_FAILURE_CAUSES)는 RHS 로컬 미커밋 파일이다. RHS가 올리면 커밋 번호로 바꿔 적는다.
