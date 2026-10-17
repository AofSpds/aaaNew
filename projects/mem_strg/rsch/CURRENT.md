# CURRENT — mem_strg / rsch

- 상태: ACTIVE · 2026-10-18
- 현재 work act: REQ-001 — 참조값과 백업·복원(S5) 초벌에 대한 Pro 검토 답을 받음([BACKUP_RESTORE_REVIEW_RESPONSE_GPT_PRO](research/operations/BACKUP_RESTORE_REVIEW_RESPONSE_GPT_PRO.md), Pro가 자기 브랜치로 직접 올림). 검토 처리 전
- 다음 한 단계: Pro 검토 답 처리(채택·정정) → 초벌 v0.2
- **백업 위치 (Owner 2026-10-18)**: "백업은 다른 드라이브에도 하고, 외부 드라이브에도 합니다." → 백업 실물은 두 곳에 둡니다(Owner 결정 D-a 해결)
  - 관찰 [실측, 읽기만]: HANAL의 PC 안 디스크는 C:(NVMe 1.9TB) 하나뿐입니다.
    - E: F: H: I: = 외장 HDD 2.8TB (NTFS, 항상 연결)
    - J: K: = 외장 HDD 7.5TB (exFAT, 항상 연결)
    - D: = USB 메모리, G: = Google Drive (외부 서비스라 제외)
  - 드라이브 선정 (Owner 2026-10-18: "가장 상태좋고 좋은 드라이브에 하시죠" → 이 채널이 상태를 보고 고름):
    - **1차 = E:** (2.8TB NTFS, 빈 공간 1,270GB, 최근 오류 0)
    - **2차 = K:** (7.5TB exFAT, 빈 공간 2,831GB, 최근 오류 0)
    - 근거 [실측, 읽기만]: Windows System 기록 10-15 01:50부터(약 3일치)의 디스크 오류를 드라이브별로 셌습니다.
      - H: 읽기 재시도 335, paging 오류 20, NTFS 지연 쓰기 실패 6
      - I: NTFS 지연 쓰기 실패 10
      - D:(USB 메모리) 재시도 40, paging 오류 126
      - F:·J: 재시도 1씩. E:·K:·C: 0
      - 오류 시각이 USB 재설정(UASPStor 129, 10-15 22:32, 10-16 21:53)과 겹칩니다.
    - 한계: 기록이 3일치뿐입니다. USB 외장의 SMART(온도·오류 계수)는 관리자 권한이나 별도 도구 없이는 읽을 수 없어 보지 못했습니다. Windows 건강 상태는 8개 장치 모두 "Healthy"였습니다.
    - 남은 위험: E:·K:가 모두 항상 연결돼 있어, PC 전체에 생기는 사고(랜섬웨어·실수로 지움)에는 함께 노출됩니다.
      - 결정(2026-10-18, Owner "k: 을 왜 봅나요" → 이 채널 재판단): **K:는 분리하지 않습니다.** PC 밖 사본 역할은 Google Drive desktop-care(판마다 남는 restic 암호화 백업)가 맡습니다.
- **SQLite 수정판 설치 (Owner 2026-10-18: "설치는 하세요", 결정 D-f 해결)**
  - mem_strg 전용 가상환경 `C:\Users\ms1pk\.venvs\mem_strg`(Python 3.13.14)를 만들었습니다. Python 본체와 전역 패키지는 건드리지 않았습니다.
  - `apsw 3.54.0.0`(PyPI 공식 wheel)을 설치했습니다. 담긴 SQLite는 **3.54.0**으로, WAL-reset 버그 수정판(3.51.3 이상)입니다.
  - 확인 [실측]: WAL 모드 열기·쓰기·읽기 통과. 기본 `sqlite3` 모듈은 여전히 3.50.4이므로, SQLite 비교 실측은 이 가상환경의 apsw로 합니다.
- **여러 기기 (Owner 2026-10-18)**: "JWDEV 는 아마 없어지겠지만 당연히 여러개의 디바이스에서 운용할수 있기는 합니다. 다만 일단 현재 HANAl 에 붙어서 원격으로 붙는 형식일겁니다."
  - 저장소에 직접 쓰는 기기는 **HANAL 하나**입니다. 다른 기기는 HANAL에 원격으로 붙어서 씁니다. 그래서 기기 사이 병합은 지금 다루지 않습니다(Owner 결정 D-b 해결).
  - 나중에 기기를 늘릴 수 있도록 기록 봉투에 `device_id`(지금은 HANAL) 칸만 남겨 둡니다(Pro P2 Q3).
    - 따로 알린 것: H:·I:에 문제 징후가 있음 (Owner 자료 확인 권고)
- **하드디스크 백업 저장소 (Owner 2026-10-18: "네 하드디스크 백업 저장소도 정하시고, 해당 세션에 연락이 닿으면 인폼주세요." → 이 채널이 정함)**

```text
백업 위치 3곳
  hdd-e-primary    = E:\MEMSTORE_BACKUP\   (1차, 봉인할 때마다 복사·대조)
  hdd-k-secondary  = K:\MEMSTORE_BACKUP\   (2차, 1차 대조가 통과한 뒤 복사·대조)
  gdrive-desktopcare = localComputer desktop-care의 restic 암호화 저장소 (자료 저장소 폴더를 보호 목록에 넣음)

<드라이브>:\MEMSTORE_BACKUP\
├─ LOCATION.txt          위치 ID·만든 날·장치 설명(모델·용량, 시리얼 없음). 드라이브 문자가 바뀌어도 이 표식으로 찾음
└─ <store_id>\           store_id = memstore-01 (모든 도메인 공통 저장소 1개)
   ├─ INDEX.tsv          봉인 목록 (추가만): seal_id · bundle_id · sealed_at(UTC) · manifest_sha256 · 상태
   └─ seals\<seal_id>\   MANIFEST.tsv + bundle\ (읽기 전용 표시)
seal_id = <UTC yyyymmddThhmmssZ>-<임의 6자>   ← 브랜치 이름과 무관 (Pro P3: 이름 겹침·봉인 세대 문제)
```

  - 순서: 봉인본 대조 통과 → E: 복사·대조 → K: 복사·대조 → 그다음에 참조값 기록. **어느 단계든 실패하면 멈춥니다**(Pro P3).
  - 용량: 지우지 않는 원칙이라, 빈 공간이 10% 또는 100GB 아래로 내려가면 봉인을 멈추고 보고합니다(정리는 Owner 결정).
  - 아직 E:·K:에 폴더를 만들지 않았습니다. 첫 실제 봉인 때 만듭니다.
  - ~~자료 저장소의 실제 위치는 아직 미정(D-c)~~ → **결정 (Owner 2026-10-18 "허락해요")**: 자료 저장소는 `C:\Users\ms1pk\memstore\`입니다.
    - Git 저장소·작업 사본·동기화 폴더 밖입니다.
    - 표식 파일 `MEMSTORE.txt`(store_id: memstore-01)를 두었습니다. 쓰기 도구는 이 store_id가 맞을 때만 기록하고, 경로가 없으면 새로 만들지 않고 멈춥니다(Pro P2 권고).
  - **세션 쓰기 권한 (Owner 2026-10-18: "세션이 쓰게 하는것이지요" / "허락해요")**: 한 번만 설정했고, 이후 여는 모든 세션에 적용됩니다.
    - Claude: `~\.claude\settings.json`에 `permissions.additionalDirectories` = memstore, E:\MEMSTORE_BACKUP, K:\MEMSTORE_BACKUP. JSON 검사 통과
    - Codex: `~\.codex\config.toml` 끝에 `[sandbox_workspace_write] writable_roots` 같은 세 경로. TOML 검사 통과
    - 고치기 전 사본: 두 파일 모두 `*.bak-20261018`(해시 일치 확인)
    - 한계: 파일 쓰기 승인만 줄어듭니다. 명령 실행 승인은 따로입니다. Codex의 writable_roots가 Windows 자체 샌드박스에서 동작하는지는 아직 시험하지 않았습니다 [미확인]. 이미 열려 있는 세션은 다시 열어야 반영될 수 있습니다.
- **관련 프로젝트: 시스템 복원 `localComputer` (DEV-ENV)** (Owner 2026-10-18: "우리가 시스템 복원을 위한 프로젝트도 있을거예요")
  - 위치: `C:\Users\ms1pk\dev\localComputer`, GitHub AofSpds/localComputer (읽기만 함)
  - 이미 돌고 있는 것 [문서: localComputer CURRENT 2026-10-15 18:59]: 데스크톱 정기 백업 desktop-care
    - restic 암호화 저장소 → Google Drive
    - 핵심 자료 09·13·17·21시, 전체 22시, 토 점검, 일 복원 시험
    - 경로 탈출·ADS·예약 파일명 거부 시험 포함
  - 활용 후보: 자료 저장소 폴더를 desktop-care 보호 목록에 넣으면 백업이 세 곳(E: + K: + Google Drive)이 됩니다. Google Drive가 "외부 서비스 지양"과 맞는지는 Owner가 결정합니다
  - 담당 세션: desktop-care를 설정한 것은 **Codex 세션 01a12865…**(localComputer DEV-ENV, 10-11부터)입니다. 기록에서 DesktopCare-Core·restic-v1-20261015를 찾아 확인했습니다. Claude 세션 format_rec는 담당이 아닙니다(Owner: "따로 있을겁니다 아마").
  - 인폼(2026-10-18): Codex 대기열에 정보 공유 1건을 넣었습니다(작업 요청 아님, 회신 "수신" 한 줄). **90초 안에 가져가지 않았습니다.** 다른 스레드 앞으로 쌓인 메시지도 15–18시간째 남아 있어서, 그 스레드가 열려야 전달될 것으로 봅니다 [미확인].
  - ⚠ 알린 위험: D:가 백업 키 USB입니다(`D:\DevEnvBackup-G14` 존재 확인, 내용은 열지 않음). 최근 3일 기록에 D: 오류 166(paging 126, 재시도 40)이 있습니다. 키 USB 사본을 하나 더 두기를 권고했습니다(키 작업은 이 채널이 하지 않음)
- **작업 위치 (Owner 2026-10-18: "아 지금부터 하시면 됩니다." / "여기까지만 머지하시고 브랜치따세요.")**
  - 작업 사본: `C:\Users\ms1pk\dev\aaaNew-wt-mem_strg` (mem_strg 전용 worktree 1개). 브랜치는 `mem_strg/req-001`이고, main `d6f7f99`에서 땄습니다.
  - 공용 폴더 `C:\Users\ms1pk\dev\aaaNew`(main)에서는 mem_strg 파일을 고치지 않습니다. BTSR 세션과 같은 폴더이기 때문입니다.
  - 외주(Pro) 결과는 외주 브랜치 → 이 작업 브랜치로 합칩니다. 작업 단위가 끝나면 PR로 main에 올립니다. 머지는 주관 PLN이 DPM 승인을 받아 하고, PLN이 생기기 전에는 Owner가 맡습니다.
  - 작업 흐름을 정하기 전의 커밋: `2506468` `8771f1f` `5408ece` `c9215e5` `99952a8` `b4be47a`는 main에 바로 푸시했습니다. 되돌리지 않습니다. 이어서 `d6f7f99`에서 Pro P3 외주 브랜치를 main에 머지해 그 단락을 닫았습니다.
- 막힘: 없음. D-c(저장소 위치·설정)와 D-f(SQLite 수정판 설치)는 Owner 결정이 필요
- 작성 세션: AAA_NEW/MEM_STRG/RSCH (local_edac275f-…, 2026-10-17 개설. 2026-10-18 이름 규칙 확정으로 AAA/NEW/RSCH/MEM_STRG에서 바꿈)

## 목적 (Owner 2026-10-17)

Byul 최신 연구·JEV·그래프 DB 등을 이용해 **모든 도메인 공통의 로컬 저장소와 그 저장소를 관리하는 엔진**을 만듭니다. RHS는 첫 적용 사례입니다. 이 작업대는 연구를 맡고, 구현은 mem_strg의 별도 작업대가 맡습니다(위치 미정).
- 근거: [REV1](requests/REQ-001_REV1_OWNER_SCOPE.md) · [REV2](requests/REQ-001_REV2_OWNER_GOAL.md)
- 방침: 혼자 깊이 조사하지 않습니다. 이 채널은 수집·기록·초벌·검토를 하고, 깊은 조사는 Pro 챗에 맡깁니다 → [계획](PLAN_PRELIM_AND_OUTSOURCE_CLAUDE.md)
- 설계안(S8)은 이번 진행에서 하지 않습니다(Owner).
- **저장 형태 (Owner 2026-10-18)**: "사실 프로젝트와 아카이브를 저장하는 형태가 맞지 않을까 싶어요." / "네 커런트는 머지된 현재의 공식적인 현재버젼인겁니다. 어렵게 생각할게 없어요."
  - 저장소의 모양은 **프로젝트 + 아카이브**입니다.
  - **CURRENT = 머지된 공식 현재판**입니다. 작업 중인 메모는 CURRENT가 아닙니다.
  - 머지할 때만 CURRENT가 바뀌고, 직전 공식판은 아카이브로 갑니다.
  - ~~머지는 Git이 아니라 로컬 저장소 안에서 합니다.~~ ← 이 채널의 잘못된 해석이라 정정합니다(아래 "작업 흐름").
- **작업 흐름 (Owner 2026-10-18)**: "그리고 깃 브랜치를 따서 작업을 하게 되는데 메모나 자료 테스트를 위한 자료등 모이는 산출물들은 우리가 만들 자료 저장소에 들어가게 됩니다. 그렇게 도메인은 작업된 깃 브랜치를 PR 머지후 커런트로 갖게 됩니다."
  - 작업 단위마다 Git 브랜치를 땁니다. 코드·설계 정본 같은 공식 산출물은 브랜치에 커밋합니다.
  - 메모·시험 자료·중간 산출물은 자료 저장소에 쌓습니다. Git에 매번 커밋하지 않습니다.
  - PR 머지 뒤 main의 상태가 도메인 CURRENT입니다. Git 병합은 PR마다 한 번입니다.
  - PR 때 자료 저장소를 백업하고, 그 참조값을 PR에 남깁니다(S5가 중심 단계가 됨).
  - **자료 묶음 단위 (Owner 2026-10-18 확정)**: "네, 자료는 작업 브랜치 단위로 묶고, PR 머지 때 고정해 아카이브로 보냅니다." 머지 커밋은 그 묶음의 참조값을 가리킵니다.

- **원칙 (Owner 2026-10-18)**: "그냥 우리가 평소에 인간 개발팀이 작업하는 형태를 모사한겁니다. 각 역할별로 수집한 자료는 그대로 도메인에 참조값을 넣고 보관합니다."
  - 역할별로 모은 자료는 **그대로** 보관합니다. 변환·요약은 필수가 아닙니다.
  - 도메인(Git)에는 **참조값만** 넣습니다.
  - 그래서 연구의 중심 질문은 "참조값의 모양(무엇을 가리키고, 무엇으로 변조를 확인하고, 어떻게 다시 찾나)"이 됩니다(S5). 그래프·쓰기마다 롤업은 보조 기능으로 내려갑니다.

```text
자료 저장소/
└─ <도메인>/
   ├─ projects/<프로젝트>/work/<브랜치>/<역할>/      작업 중 자료: 메모 일지·시험 자료·산출물 (그대로 보관)
   └─ archive/<프로젝트>/<브랜치>@<머지 커밋>/<역할>/  PR 머지 때 고정한 묶음 (지우지 않음)
Git: 브랜치의 공식 산출물 + PR에 자료 묶음 참조값(묶음 ID·digest). main = 도메인 CURRENT
```
- **머지 주체 (Owner 2026-10-18)**: "해당 프로젝트를 주관하는 PLN이 DPM의 승인을 받고 하게 됩니다. 물론 오너가 최종 확인자입니다."
  - 흐름: 역할의 작업 메모 → PLN 머지안 → DPM 승인 → PLN 머지(CURRENT 갱신, 직전판은 아카이브) → Owner 최종 확인
  - CURRENT를 쓰는 주체는 프로젝트마다 PLN 하나입니다. 다른 역할은 자기 작업 메모만 씁니다.
  - 기본값(이 채널 제안, Owner 이의 없으면 유지): 머지 시점부터 CURRENT는 공식판이고 표시는 "Owner 확인 대기"입니다. Owner가 확인하면 "확인됨"으로 바꿉니다. Owner가 되돌리라고 하면 PLN이 새로 머지합니다. 삭제는 없습니다.

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

## 단계 번호 풀이 (S 번호 = REQ-001 연구 단계)

S0 선행 연구 모으기 · S1 저장 방식 · S2 동시 쓰기 · S3 도메인 현황(롤업) · S4 아카이브 · **S5 참조값과 백업·복원** · S6 여러 컴퓨터·휴대폰 · S7 기존 메모 옮기기 · S8 통합 설계안(이번에는 안 함). 약어는 문서 안에서만 씁니다. Owner께 보고할 때는 번호만 쓰지 않고 "참조값과 백업·복원(S5)"처럼 이름과 함께 씁니다(Owner 2026-10-18: "약어는 내부에서 쓰는걸 허락하지만, S5만 쓰는건 하지말아주세요.").

## 남은 단계

| 단계 | 내용 | 상태 |
| --- | --- | --- |
| S1′ | 저장 계층 재검토 (원장·투영·그래프·판정 층) | Pro P1 답으로 1차 정리. 실측 1·2 뒤 다시 봄 |
| S4 | 아카이브 (시점·이름·목록) | **시점 결정됨**: PR 머지 때 브랜치 묶음을 고정. 이름·목록 양식만 남음 (Pro P2 Q1 INDEX 칸 참고) |
| S5 | 참조값과 백업·복원 | **초벌 + 실측 완료** ([BACKUP_RESTORE_REFERENCE_CLAUDE](research/operations/BACKUP_RESTORE_REFERENCE_CLAUDE.md)): 봉인·백업·빈 폴더 복원 완전 일치, 고장 5가지 모두 잡음. Pro 검토 의뢰 준비 |
| S6 | 여러 기기·모바일 | D-b·D-d 뒤 |
| S7 | 기존 메모 이전 | Pro P2 Q6 양식으로 도메인별 목록 |
| S8 | 통합 설계안 | 이번에는 하지 않음 |

- 공통 제약: 외부 서비스 없음, 키·시크릿 금지, 삭제 없음, 상대 경로
- 원천 읽기: RHS·bootstrap·Byul·AAA는 읽기만 합니다
- 지난 판: [archive/2026-10-17_CURRENT_scope-v1.md](archive/2026-10-17_CURRENT_scope-v1.md), 그 뒤의 판은 Git 이력(5408ece 등)
