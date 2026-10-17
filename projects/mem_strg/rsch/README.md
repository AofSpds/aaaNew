# mem_strg / rsch — 에이전트 메모 로컬 저장소 연구 작업대

- 채널(세션) 이름: `AAA/NEW/RSCH/MEM_STRG` (Owner 제안 aaa_new_rsch_mem_strg, 세션 이름 규칙: 대문자·`_` 대신 `/`)
- 프로젝트: mem_strg (별도 프로젝트, bootstrap과 독립). 역할: rsch. AAA/NEW/RSCH/BTSR([bootstrap/rsch](../../bootstrap/rsch/))와 같은 항렬의 병렬 연구 채널
- 요청 출처: RHS/DPM 세션 경유 Owner 지시 — [requests/REQ-001](requests/REQ-001_RHS_DPM_LOCAL_MEMORY_STORE.md)
- 주제: Owner가 하는 모든 도메인의 공통 메모리 규칙(Owner 2026-10-17). 자주 고치는 에이전트 메모(Current·로드맵·아카이브)를 Git에서 분리해 담을 로컬 저장소의 형태와 기술. Git에는 참조값만, 로컬 저장소는 내재화, PR마다 Git 백업. RHS는 첫 적용 사례.
- 관련: 관계 엔진 [memory-store](../../bootstrap/memory-store/) 결정(D1·D8·D15·D16·D20), [역할·워크플로 설계](../../bootstrap/rsch/design/ROLE_WORKFLOW_DESIGN_CLAUDE.md)
- 구조: projects/<project>/<role>/ 규칙을 따름. 진입 파일(CLAUDE.md·AGENTS.md)은 Owner 결정 E7·E9·D18 전이라 만들지 않음.

```text
projects/mem_strg/rsch/
├─ README.md     이 파일
├─ CURRENT.md    현재 상태 (작성 세션 1개: AAA/NEW/RSCH/MEM_STRG)
├─ requests/     받은 요청 원문
├─ returns/      반환 (result/evidence/delta/open/learnings/next)
├─ research/     조사·실측 자료
└─ reviews/      독립 검증 결과
```
