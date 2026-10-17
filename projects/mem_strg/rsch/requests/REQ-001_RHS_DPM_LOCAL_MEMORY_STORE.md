# REQ-001 — 에이전트 메모를 담을 로컬 저장소의 형태와 기술

- ID: REQ-001
- FROM: RHS/DPM 세션 (local_01db8a4d-a6bf-4df7-87aa-435e11d713bc), Owner 지시 전달
- TO: AAA/NEW/RSCH/BTSR(구 aaa_new_rsch) → 병렬 연구 채널 AAA/NEW/RSCH/MEM_STRG(Owner 제안 aaa_new_rsch_mem_strg)
- 수신: 2026-10-17, AAA/NEW/RSCH/BTSR (Claude 세션 e3bfd5a5-…)
- 상태: RECEIVED (채널 미개설)
- RETURN_TO: RHS/DPM (결과를 RHS에서 Owner께 올림)

## Owner 원문 (RHS/DPM 세션, 2026-10-17, 전달받은 그대로)
- "네 이렇게 자주고치는 것들은 git에는 참조값만 두고 저장소로 관리하는게 결국은 맞지 않나 싶어요."
- "로컬 저장소와 백업을 해두는것으로 하겠습니다. 로컬 저장소의 형태나 기술적인 부분은 일단 병행연구과제로 진행할생각입니다. aaaNew에서 연구를 할테니 git을 36번 머지하는 일은 없도록 하겠습니다. git은 참조값만 에이전트 메모는 될수 있으면 분리 ㅇㅇ"
- 앞서: "될수 있으면 내제화 하고 pr 될때마다 백업하는걸로 했던듯 합니다."
- 채널 요청: "일단 저장소 관련한 해당 연구를 aaa_new_rsch 에서 연구할수 있도록 연락하세요. … 병렬 연구 채널을 하나 더 만들 수 있도록 하고 폴더 공간도 미리 정해둔 규칙에 따라 만들어 두도록 요청하세요. aaa_new_rsch_mem_strg 정도가 적당할까요."

## 배경 (RHS 실제 사례, RHS/DPM 보고)
- 역할 에이전트가 메모(Current 갱신, 원문 한 줄)를 고칠 때마다 Git 브랜치 → 병합 → push → readback 반복.
- 2026-10-17 하루 RHS/DPM 한 세션이 main에 36회 병합, 전체 세션 합계 65회. main 커밋 767개 중 276개가 병합 커밋.
- 역할·묶음마다 저장소 사본 폴더를 새로 만들어 같은 저장소 사본 20개. Owner 평: "극혐".
- Current에 이력을 계속 덧붙여 현재 상태를 읽을 수 없게 됨.

## RHS에서 정해진 요구 (Owner 결정, RHS/DPM 보고)
1. 역할마다 Current(덮어씀), 로드맵(자기 범위), 아카이브(지난 Current 누적).
2. 역할 Current가 모여 도메인 Current. 아카이브·로드맵도 같은 방식으로 롤업.
3. 역할 트리 DPM > PLN > RSCH/ARCH/PMO. 검증자(V)는 비상설.
4. Git에는 참조값만(코드, 설계 정본, 증거, Owner 원문 장부, 정식 요청·회신). 자주 고치는 메모는 로컬 저장소.
5. 로컬 저장소는 내재화(외부 서비스 지양). PR마다 Git에 백업.
6. 아무것도 지우지 않음.

## 연구 질문 (RHS/DPM 제안, 범위는 연구 채널이 정함)
- 저장 형태: 파일(Markdown/JSON), 로컬 DB(SQLite 등), 그 밖의 방식 비교
- 동시 쓰기: 같은 PC에서 Claude Desktop 세션 여럿 + Codex 세션
- 롤업: 역할 → 도메인 자동 생성, 고정 머리 칸(상태·다음·기다리는 대상·갱신 시각 등)
- 아카이브: 쌓는 시점(갱신마다 / 상태 변화 / 하루 1회), 이름 규칙, 목록
- Git 참조값: 메모의 어느 시점·해시를 Git에 남길지, PR 백업 방법과 복원 절차
- 여러 기기: 데스크탑 HANAl, 다른 기기 jwDev(C:\Users\ms1pk\dev가 Google Drive 미러로 보고됨)
- 모바일: Owner는 모바일에서 세션 이름만 봄. 도메인 Current 모바일 열람 방법
- 키·시크릿은 어디에도 쓰지 않음
- 지금 Git에 있는 메모 이전 방법

## 참고 자료 (AofSpds/rghtHpSnpr)
- 결정 목록: planning/STRUCTURE_DECISIONS.md (main 4df6aae). 위 4–6은 RHS 로컬에만 있고 곧 올릴 예정.
- 시뮬레이션·검증: planning/requests/STRUCTURE_SIMULATION_REVIEW_v0.1_20261017.md (main bc344e2), 롤업 모형 planning/requests/sim/rollup_sim.py
- 역할 폴더 양식 초안: planning/STRUCTURE_PLAN.md §1.8

## aaaNew 쪽 관련 자산
- 관계 엔진 저장소 결정: ../../../bootstrap/rsch/research/relation-engine/DECISIONS_D1_D21_CLAUDE.md (D1 jsonl+SQLite 투영, D15 동시 쓰기·Git, D16 보존·교정, D20 민감 정보)
- 역할·워크플로 설계(작업대당 CURRENT 1개, 롤업 개념): ../../../bootstrap/rsch/design/ROLE_WORKFLOW_DESIGN_CLAUDE.md
