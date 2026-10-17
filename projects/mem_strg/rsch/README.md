# mem_strg / rsch — 에이전트 메모 로컬 저장소 연구 작업대

- 채널(세션) 이름: `AAA/NEW/RSCH/MEM_STRG` (Owner 제안 aaa_new_rsch_mem_strg, 세션 이름 규칙: 대문자·`_` 대신 `/`)
- 프로젝트: mem_strg (별도 프로젝트, bootstrap과 독립). 역할: rsch. AAA/NEW/RSCH/BTSR([bootstrap/rsch](../../bootstrap/rsch))와 같은 항렬의 병렬 연구 채널
- 요청 출처: RHS/DPM 세션 경유 Owner 지시 — [requests/REQ-001](requests/REQ-001_RHS_DPM_LOCAL_MEMORY_STORE.md)
- 주제: Owner가 하는 모든 도메인의 공통 메모리 규칙(Owner 2026-10-17). 자주 고치는 에이전트 메모(Current·로드맵·아카이브)를 Git에서 분리해 담을 로컬 저장소의 형태와 기술. Git에는 참조값만, 로컬 저장소는 내재화, PR마다 Git 백업. RHS는 첫 적용 사례.
- 관련: 관계 엔진 [memory-store](../../bootstrap/memory-store) 결정(D1·D8·D15·D16·D20), [역할·워크플로 설계](../../bootstrap/rsch/design/ROLE_WORKFLOW_DESIGN_CLAUDE.md)
- 구조: projects/<project>/<role>/ 규칙을 따름. 진입 파일(CLAUDE.md·AGENTS.md)은 Owner 결정 E7·E9·D18 전이라 만들지 않음.

```text
projects/mem_strg/rsch/
├─ README.md     이 파일
├─ CURRENT.md    현재 상태 (작성 세션 1개: AAA/NEW/RSCH/MEM_STRG)
├─ PLAN_PRELIM_AND_OUTSOURCE_CLAUDE.md   초벌 연구·외주(Pro) 계획
├─ requests/     받은 요청 원문 (확정 기록, 고치지 않음)
├─ returns/      반환 (result/evidence/delta/open/learnings/next, 확정 기록)
├─ archive/      지난 CURRENT·인수 기록 (추가만)
├─ research/     조사·실측 자료 — 주제 폴더별
│  ├─ TOPICS.md            소주제 등록부 (소주제 → 폴더·문서·출처)
│  ├─ storage-structure/   저장 구조: 원장·층·추적·그래프 DB·검색·판정 (S1, 외주 P1)
│  ├─ concurrent-writes/   쓰기 경로: 잠금·내구성·충돌·끝줄 복구 (S2)
│  ├─ rollup/              롤업·view: 머리 칸·도메인 롤업·오래됨·게시 (S3)
│  ├─ operations/          운영: 아카이브·백업·기기·위치·모바일·이전 (외주 P2)
│  └─ prior-research/      선행 연구: 원천 수집·Byul·JEV·AAA 패턴 (S0)
└─ reviews/      검토·검증 결과
```

- 새 자료는 [research/TOPICS.md](research/TOPICS.md)에서 소주제를 먼저 찾고 넣습니다. 없는 소주제는 등록부에 먼저 추가합니다.

- 파일 이름 규칙: 주제를 먼저 쓰고 출처를 끝에 붙입니다. `<주제>_<출처>.md`
  - 출처: `_CLAUDE`(이 채널), `_GPT_PRO`(ChatGPT Pro 외주), `_CODEX`
  - 실측 스크립트와 결과(`s1_*.py`, `*_results_*.json`)는 해당 주제 폴더에 함께 둡니다
- 외주 의뢰서는 해당 주제 폴더에 `_REQUEST_v<판>_CLAUDE.md`로, 답변 원문은 `_RESPONSE_GPT_PRO.md`로 둡니다
- 소주제 중복 방지: 새 폴더를 만들기 전에 기존 주제 폴더부터 확인하고, 맞는 폴더가 있으면 그 안에 파일로 넣습니다. 출처·도구·모델 이름으로는 폴더를 만들지 않습니다(Owner 2026-10-18)
