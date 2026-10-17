# 소주제 등록부 — mem_strg / rsch / research

- 작성: 2026-10-18, AAA/NEW/RSCH/MEM_STRG · Owner 승인: "네 출처는 적어두세요. 구분하기 쉽도록 출처도 중요합니다. 승인합ㄴ다."
- 목적: 소주제 하나는 한 곳에만 둡니다. 새 자료를 넣기 전에 이 표에서 소주제와 위치를 찾습니다.

## 규칙

1. **소주제가 표에 있으면** 그 주제 폴더에 넣습니다. **표에 없으면** 표에 먼저 한 줄 추가한 뒤에 넣습니다.
2. 파일 이름은 `<소주제>_<내용>_<출처>.md`입니다. 소주제와 내용이 같으면 하나만 씁니다.
3. **출처는 꼭 적습니다.**
   - `_CLAUDE`: 이 채널
   - `_GPT_PRO`: ChatGPT Pro 외주
   - `_CODEX`: Codex 세션
   - 서브에이전트가 추출한 문서는 `_CLAUDE`로 쓰되, 문서 머리에 "서브에이전트 추출"을 밝힙니다.
4. 여러 소주제에 걸친 문서(예: Pro 답변 한 건)는 주된 주제 폴더에 **한 번만** 둡니다. 다른 소주제 칸에는 위치만 적고, 내용을 나눠 복사하지 않습니다.
5. 출처·도구·모델 이름으로는 폴더를 만들지 않습니다.
6. 실측 스크립트(`*.py`)와 결과(`*_results_*.json`)는 해당 소주제의 주제 폴더에 함께 둡니다.

## 표

| 주제 폴더 | 소주제 (키) | 문서 · 위치 | 출처 |
| --- | --- | --- | --- |
| storage-structure 저장 구조 | 원장 형식·봉투 (ledger-format) | [STORAGE_FORM_CLAUDE](storage-structure/STORAGE_FORM_CLAUDE.md) (S1) | CLAUDE |
| | | [STORAGE_ENGINE_RESPONSE_GPT_PRO](storage-structure/STORAGE_ENGINE_RESPONSE_GPT_PRO.md) Q1 | GPT_PRO |
| | 층 구조 (layers) | STORAGE_FORM_CLAUDE §5 (memory-store와의 관계) | CLAUDE |
| | | STORAGE_ENGINE_RESPONSE_GPT_PRO Q3 | GPT_PRO |
| | 출처·무효화 추적 (provenance) | [s0_graph_scale_bench.py](storage-structure/s0_graph_scale_bench.py) · [결과](storage-structure/s0_graph_results_20261017.json). 해설은 prior-research/SOURCES_CLAUDE §3 | CLAUDE |
| | | STORAGE_ENGINE_RESPONSE_GPT_PRO Q2 | GPT_PRO |
| | 그래프 DB 후보 (graph-db) | prior-research/SOURCES_CLAUDE §2 (2026-10-17 웹 2차 출처) | CLAUDE |
| | | STORAGE_ENGINE_RESPONSE_GPT_PRO Q4 | GPT_PRO |
| | 검색 층 (search) | STORAGE_ENGINE_RESPONSE_GPT_PRO Q5 | GPT_PRO |
| | 판정 JEV-like (judgment) | STORAGE_ENGINE_RESPONSE_GPT_PRO Q6. JEV 배경은 prior-research/BYUL_JEV_EXTRACT_CLAUDE §4 | GPT_PRO |
| | 의뢰서 | [STORAGE_ENGINE_REQUEST_v1.0_CLAUDE](storage-structure/STORAGE_ENGINE_REQUEST_v1.0_CLAUDE.md) (보낸 판), v0.1 (초안) | CLAUDE |
| concurrent-writes 쓰기 경로 | 잠금 (locking) | [CONCURRENT_WRITES_CLAUDE](concurrent-writes/CONCURRENT_WRITES_CLAUDE.md) §2·§4 (S2) | CLAUDE |
| | 내구성 (durability) | CONCURRENT_WRITES_CLAUDE 정정 절. P1 답 Q7, P2 답 Q7 | CLAUDE · GPT_PRO |
| | 충돌 (conflict, expected_revision) | P1 답 Q7, P2 답 Q7 | GPT_PRO |
| | 깨진 끝줄 복구 (tail-recovery) | CONCURRENT_WRITES_CLAUDE §4-5와 정정 절. P1 답 Q7, P2 답 Q7 | CLAUDE · GPT_PRO |
| rollup 롤업·view | 머리 칸 (header) | [ROLLUP_CLAUDE](rollup/ROLLUP_CLAUDE.md) §2 (S3) | CLAUDE |
| | 도메인 롤업 (domain-rollup) | ROLLUP_CLAUDE §3 · [생성 예시](rollup/s3_sample_domain_current.md) | CLAUDE |
| | 오래됨 표시 (staleness) | ROLLUP_CLAUDE §5. P2 답 Q5 | CLAUDE · GPT_PRO |
| | 게시 순서 (publish) | ROLLUP_CLAUDE 정정 절. P1 답 Q7, P2 답 Q7 | CLAUDE · GPT_PRO |
| operations 운영 | 아카이브 (archiving) | [OPERATIONS_RESPONSE_GPT_PRO](operations/OPERATIONS_RESPONSE_GPT_PRO.md) Q1 | GPT_PRO |
| | 백업·복원·참조값 (backup-restore) | [BACKUP_RESTORE_REFERENCE_CLAUDE](operations/BACKUP_RESTORE_REFERENCE_CLAUDE.md) (초벌 + 실측, [스크립트](operations/backup_restore_bench.py)) | CLAUDE |
| | | OPERATIONS_RESPONSE_GPT_PRO Q2 | GPT_PRO |
| | | [BACKUP_RESTORE_REVIEW_REQUEST_v0.1_CLAUDE](operations/BACKUP_RESTORE_REVIEW_REQUEST_v0.1_CLAUDE.md) (Pro 검토 의뢰서 초안) | CLAUDE |
| | 여러 기기 (devices) | OPERATIONS_RESPONSE_GPT_PRO Q3 | GPT_PRO |
| | 위치·권한 (location-permissions) | CONCURRENT_WRITES_CLAUDE §5 (세션 권한, 문서). OPERATIONS_RESPONSE_GPT_PRO Q4 | CLAUDE · GPT_PRO |
| | 모바일 열람 (mobile) | OPERATIONS_RESPONSE_GPT_PRO Q5 | GPT_PRO |
| | 기존 메모 이전 (migration) | OPERATIONS_RESPONSE_GPT_PRO Q6 | GPT_PRO |
| | 의뢰서 | [OPERATIONS_REQUEST_v1.0_CLAUDE](operations/OPERATIONS_REQUEST_v1.0_CLAUDE.md) (보낸 판), v0.1 (초안) | CLAUDE |
| prior-research 선행 연구 | 원천 수집 (sources) | [SOURCES_CLAUDE](prior-research/SOURCES_CLAUDE.md) (S0) | CLAUDE |
| | Byul | [BYUL_JEV_EXTRACT_CLAUDE](prior-research/BYUL_JEV_EXTRACT_CLAUDE.md) §1–3·§5 (서브에이전트 추출) | CLAUDE |
| | JEV | BYUL_JEV_EXTRACT_CLAUDE §4 | CLAUDE |
| | AAA 기억 패턴 | BYUL_JEV_EXTRACT_CLAUDE §6 | CLAUDE |
| | BTSR 메모리 연구 인수 | [../archive/2026-10-17_BTSR_MEMORY_RESEARCH.md](../archive/2026-10-17_BTSR_MEMORY_RESEARCH.md) (참조값만, 원본은 bootstrap) | CLAUDE (원본: CLAUDE·CODEX) |

## 주제를 넘는 문서

| 문서 | 다루는 소주제 | 출처 |
| --- | --- | --- |
| [reviews/STORAGE_ENGINE_OPERATIONS_REVIEW_CLAUDE.md](../reviews/STORAGE_ENGINE_OPERATIONS_REVIEW_CLAUDE.md) | P1·P2 답 전체 검토, S0–S3 정정, 항목별 판정, Owner 결정 후보 | CLAUDE |
| [../PLAN_PRELIM_AND_OUTSOURCE_CLAUDE.md](../PLAN_PRELIM_AND_OUTSOURCE_CLAUDE.md) | 초벌 연구와 외주 계획 | CLAUDE |
