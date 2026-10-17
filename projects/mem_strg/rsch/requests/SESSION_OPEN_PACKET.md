# 세션 개설 패킷 — AAA/NEW/RSCH/MEM_STRG

- 준비: 2026-10-17, AAA/NEW/RSCH/BTSR (구 aaa_new_rsch, Claude 세션 e3bfd5a5-…)
- 상태: PREPARED (Owner가 세션을 직접 열고 아래 첫 메시지를 붙여 넣음)
- 세션 이름 규칙(Owner, 2026-10-17): 대문자, 계층은 `/`로 구분. 한 이름 안의 낱말은 `_` 유지(MEM_STRG). 예: aaa_new_rsch_mem_strg → `AAA/NEW/RSCH/MEM_STRG`

## Owner가 할 일

1. Claude 데스크톱 Code 탭에서 새 세션을 엽니다.
   - 폴더: `C:\Users\ms1pk\dev\aaaNew\projects\mem_strg\rsch`
   - 세션 이름: `AAA/NEW/RSCH/MEM_STRG`
   - 모델: Opus 권장(연구·설계 판단), 사용량이 부족하면 Sonnet
2. 아래 "첫 메시지"를 그대로 붙여 넣습니다. 연구 요청 내용이 메시지 안에 모두 들어 있습니다.

## 첫 메시지 (복사해서 붙여 넣기)

```text
당신은 AAA/NEW/RSCH/MEM_STRG 세션입니다. aaaNew 도메인의 별도 프로젝트 mem_strg의 rsch 작업대를 맡습니다(AAA/NEW/RSCH/BTSR와 같은 항렬의 병렬 연구 채널, bootstrap 프로젝트와 독립).

작업대: C:\Users\ms1pk\dev\aaaNew\projects\mem_strg\rsch (이 폴더 밖에는 쓰지 않습니다. 읽기는 aaaNew 전체 가능)

연구 요청 내용 (REQ-001, RHS/DPM 세션이 전달한 Owner 지시, 2026-10-17):

[Owner 원문]
- "네 이렇게 자주고치는 것들은 git에는 참조값만 두고 저장소로 관리하는게 결국은 맞지 않나 싶어요."
- "로컬 저장소와 백업을 해두는것으로 하겠습니다. 로컬 저장소의 형태나 기술적인 부분은 일단 병행연구과제로 진행할생각입니다. aaaNew에서 연구를 할테니 git을 36번 머지하는 일은 없도록 하겠습니다. git은 참조값만 에이전트 메모는 될수 있으면 분리 ㅇㅇ"
- "될수 있으면 내제화 하고 pr 될때마다 백업하는걸로 했던듯 합니다."

[왜 필요한가 — RHS 실제 사례]
- 역할 에이전트가 메모(Current 갱신, 원문 한 줄)를 고칠 때마다 Git 브랜치 → 병합 → push → readback을 반복했다.
- 2026-10-17 하루 RHS/DPM 한 세션이 main에 36회 병합, 전체 세션 합계 65회. main 커밋 767개 중 276개가 병합 커밋.
- 역할·묶음마다 저장소 사본 폴더를 새로 만들어 같은 저장소 사본이 20개가 됐다.
- Current에 이력을 계속 덧붙여 지금 상태를 읽을 수 없게 됐다.

[Owner 결정 (RHS)]
1. 역할마다 Current(덮어씀), 로드맵(자기 범위), 아카이브(지난 Current 누적).
2. 역할 Current가 모여 도메인 Current가 된다. 아카이브·로드맵도 같은 방식으로 롤업.
3. 역할 트리: DPM > PLN > RSCH/ARCH/PMO. 검증자(V)는 비상설.
4. Git에는 참조값만(코드, 설계 정본, 증거, Owner 원문 장부, 정식 요청·회신). 자주 고치는 메모는 로컬 저장소.
5. 로컬 저장소는 내재화(외부 서비스 지양). PR마다 Git에 백업.
6. 아무것도 지우지 않는다.

[연구 질문 (범위는 이 채널이 정함)]
- 저장 형태: 파일(Markdown/JSON), 로컬 DB(SQLite 등), 그 밖의 방식 비교
- 동시 쓰기: 같은 PC에서 Claude Desktop 세션 여럿 + Codex 세션이 동시에 읽고 씀
- 롤업: 역할 → 도메인 자동 생성, 고정 머리 칸(상태·다음·기다리는 대상·갱신 시각 등)
- 아카이브: 언제 쌓을지(갱신마다 / 상태 변화 / 하루 1회), 이름 규칙, 목록
- Git 참조값: 메모의 어느 시점·해시를 Git에 남길지, PR 백업 방법과 복원 절차
- 여러 기기: 데스크탑 HANAl, 다른 기기 jwDev(C:\Users\ms1pk\dev가 Google Drive 미러로 보고됨)
- 모바일: Owner는 모바일에서 세션 이름만 볼 수 있다. 도메인 Current를 모바일에서 보는 방법
- 키·시크릿은 어디에도 쓰지 않는다
- 지금 Git에 있는 메모를 옮기는 방법

[참고 자료 (AofSpds/rghtHpSnpr)]
- planning/STRUCTURE_DECISIONS.md (main 4df6aae; 결정 4–6은 곧 올라감)
- planning/requests/STRUCTURE_SIMULATION_REVIEW_v0.1_20261017.md (main bc344e2), 롤업 모형 planning/requests/sim/rollup_sim.py
- planning/STRUCTURE_PLAN.md §1.8 (역할 폴더 양식 초안)

[aaaNew 쪽 관련 자료 (읽기)]
1. README.md, CURRENT.md (이 작업대), requests/REQ-001_RHS_DPM_LOCAL_MEMORY_STORE.md (위 내용의 기록본)
2. ../../bootstrap/rsch/research/relation-engine/DECISIONS_D1_D21_CLAUDE.md (D1 jsonl+SQLite 투영, D15 동시 쓰기·Git, D16 보존·교정, D20 민감 정보)
3. ../../bootstrap/rsch/design/ROLE_WORKFLOW_DESIGN_CLAUDE.md (§3 작업대 구조, §4 워크플로)
4. ../../README.md (projects 표준 구조)

할 일:
- REQ-001을 인수하고, 첫 응답 첫 줄에 [역할 rsch · 프로젝트 mem_strg · 작업대 projects/mem_strg/rsch · REQ-001] 인수 확인 줄을 씁니다.
- 연구 범위를 확정해 CURRENT.md에 적고, 범위·순서를 Owner에게 한 번 확인받은 뒤 진행합니다.
- 결과는 returns/에 반환 6항목(result/evidence/delta/open/learnings/next)으로 남기고, 요약을 RHS/DPM 세션에 보냅니다(SendMessage, 이름 RHS/DPM). RHS에서 Owner께 올립니다.
- 채널이 열렸다는 사실과 연구 범위를 AAA/NEW/RSCH/BTSR 세션과 RHS/DPM 세션에 알립니다.

지켜야 할 것:
- Owner는 사용량 압박이 있습니다. 서브에이전트는 꼭 필요할 때만 1명 단위로 씁니다(중요 판단 Opus, 단순 추출 Sonnet).
- 실측 범위를 넘는 주장을 하지 않고 [실측]/[문서]/[미확인]을 붙입니다.
- Codex 세션 파일은 수정하지 않습니다. 전역 설정 변경·대규모 설치를 하지 않습니다.
- 키·시크릿은 어디에도 쓰지 않습니다.
- 커밋·푸시는 Owner 지시 때만 합니다. 아무것도 지우지 않습니다.
- 답변은 모바일에서 읽기 쉽게 짧게, 한 부분씩 끝냅니다.
```

## 개설 후 기록
- 개설: 2026-10-17, 세션 ID local_edac275f-f25e-47d6-bede-6cf607e848fb, 이름 AAA/NEW/RSCH/MEM_STRG(개설 이름 aaa_new_rsch_mem_strg에서 변경). 세션 폴더는 작업대가 아니라 aaaNew 루트로 열림
