# CURRENT — mem_strg / rsch

- 상태: ACTIVE · 2026-10-17
- 현재 work act: REQ-001 에이전트 메모 로컬 저장소 연구 — ACTIVE. S1 완료(research/S1_STORAGE_FORM.md, B jsonl+SQLite 투영), S2 완료(research/S2_CONCURRENT_WRITES.md, 역할별 스트림+잠금 파일+단일 CLI), S3 완료(research/S3_ROLLUP.md, 쓰기마다 도메인 view 재생성·필수 머리 8칸)
- 다음 한 단계: S4 아카이브
- 막힘: 없음
- Owner 결정(2026-10-17): "여긴 여기대로 따로 쓰세요. 개별 병렬 연구입니다." / "btsr에서 잠시 연구한바 있는걸 이관 받으라는거예요." / "네 그곳은 그대로 두고 알아서 아카이브하라는거였어요" → BTSR의 메모리 연구는 이 채널이 넘겨받음. bootstrap 원본은 그대로 두고, 이 작업대 archive/에 참조값(경로·커밋·해시)과 요약으로 아카이브함 (앞서 적은 "이관 없음"은 이 결정으로 정정)
- 작성 세션: AAA/NEW/RSCH/MEM_STRG (local_edac275f-…, 2026-10-17 개설)

## 목표 (Owner 2026-10-17, 개정 1)

Owner가 하는 **모든 도메인의 공통 메모리 규칙**을 만듭니다. RHS는 첫 적용 사례입니다 → [requests/REQ-001_REV1_OWNER_SCOPE.md](requests/REQ-001_REV1_OWNER_SCOPE.md)

## REQ-001 연구 범위 (Owner 확정 2026-10-17: "범위·순서 확정합니다")

순서대로 진행. 각 단계 끝에 결정 카드 후보를 남김.

| 단계 | 질문 | 방법 |
| --- | --- | --- |
| S1 | 저장 형태: 파일(MD/JSON) vs jsonl+SQLite 투영(D1) vs SQLite 단독. 관계 엔진 memory-store와 합칠지 분리할지 | 문서 대조 + 작은 실측 |
| S2 | 동시 쓰기: 같은 PC의 Claude 세션 여럿 + Codex | 표준 라이브러리 실측(프로세스 여럿 동시 기록) |
| S3 | 롤업: 역할 Current → 도메인 Current, 고정 머리 칸 | RHS rollup_sim 대조 + 양식안 |
| S4 | 아카이브: 쌓는 시점·이름 규칙·목록 | 대안 비교 |
| S5 | Git 참조값: 남길 시점·해시, PR 백업과 복원 절차 | 절차안 + 복원 1회 실측 |
| S6 | 여러 기기(HANAl·jwDev, Google Drive 미러)·모바일 열람 | 문서 조사, 실측 가능한 것만 |
| S7 | 지금 Git에 있는 메모 이전 방법 | 대상 목록 + 단방향 이전안 |

- 공통 제약: 외부 서비스 없음, 키·시크릿 기록 금지, 삭제 없음(D16), 상대 경로(D20)
- 범위 밖: 저장소 구현(impl 몫), 관계 엔진 자체 설계, Codex 쪽 훅 설정, Owner 결정 대행
- 원천: aaaNew 문서. RHS는 원본 checkout `rghtHpSnpr/rghtHpSnpr`에서 `git show <커밋>:<경로>`로 읽기만 함(4df6aae·bc344e2). Owner 결정 #36–#39는 미커밋이라 `rghtHpSnpr-wt-plnw` 작업 폴더에서 읽기만 함(RHS/DPM 안내). 실측 스크립트는 research/ 안에만 둠
- 반환: returns/REQ-001.md 1개(6항목) → 요약을 RHS/DPM에 전송

- 위치 정정(2026-10-17, AAA/NEW/RSCH/BTSR): 이 채널이 옛 패킷 경로 projects/bootstrap/rsch_mem_strg에 처음 쓴 CURRENT를 정본 위치 projects/mem_strg/rsch로 옮김. 내용은 그대로.
