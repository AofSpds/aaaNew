# CURRENT — mem_strg / rsch

- 상태: ACTIVE · 2026-10-17
- 현재 work act: REQ-001 — S0 수집 완료([research/S0_SOURCES.md](research/S0_SOURCES.md)). Pro 의뢰서 v1.0 [P1](pro/P1_STORAGE_ENGINE_ARCH_REQUEST_v1.0.md)·[P2](pro/P2_OPERATIONS_REQUEST_v1.0.md) 완성(입력 커밋 2506468 고정), 아직 보내지 않음
- 다음 한 단계: Owner 결정 Q2(누가 Pro에 보내나) → 전송 → 답 회수·검토
- Owner 방침(2026-10-17): "너무 혼자 딮써치 하지 마시고, 연구 결과를 모으고 기록한 후 초벌 연구와 프로챗으로 연구 외주줄 계획을 세우시면 됩니다." / "웹 프로챗에 연구 의뢰를 할것입니다."
- 막힘: 없음. Byul 최신본 위치는 Owner 답이 없어 로컬 `dev/Byul`(main 79c00bf, 2026-08-26) 기준으로 진행 [미확인: 더 새 판 존재 여부]
- 작성 세션: AAA/NEW/RSCH/MEM_STRG (local_edac275f-…, 2026-10-17 개설)

## 목적 (Owner 2026-10-17)

Byul의 최신 연구, JEV, 그래프 DB 등을 이용해 **모든 도메인 공통의 새 저장 체계**를 만듭니다. RHS는 첫 적용 사례입니다.
- 만드는 것(Owner 2026-10-17): "네 우리는 그 로컬 저장소와 그 로컬 저장소를 관리하는 엔진을 만듭니다." 이 작업대(rsch)는 그 저장소와 엔진을 위한 연구를 맡습니다. 구현은 mem_strg의 별도 작업대가 맡습니다(위치는 미정).
- 근거: [REV1](requests/REQ-001_REV1_OWNER_SCOPE.md) · [REV2](requests/REQ-001_REV2_OWNER_GOAL.md)
- BTSR 메모리 연구는 이 채널이 넘겨받습니다. bootstrap 원본은 그대로 두고, `archive/`에 참조값과 요약으로 남깁니다.

## 순서 (Owner 확인 2026-10-17: "네 진행하시고 설계안 까지는 안갑니다. 이거 오늘 못끝냅니다.")

S8 설계안은 이번 진행에서 하지 않습니다.

| 단계 | 내용 | 상태 |
| --- | --- | --- |
| S0 | 원천 인수: BTSR 메모리 연구 아카이브, Byul(v0.01 메모리·v0.1 derived view·라우팅), JEV/JEV-like(AAA JEV-BYUL, Kev 실측), 내장형 그래프 DB 후보 | 수집 완료 ([S0](research/S0_SOURCES.md)) |
| S1′ | 저장 계층 재검토: S1–S3 결과를 "추가 전용 원장 + 운영 메모 층"으로 두고, 그 위에 관계·그래프 층과 판정(JEV-like) 층을 얹는 안을 비교. D1 "그래프 DB 없음"도 다시 봄 | 대기 |
| S4 | 아카이브: 쌓는 시점·이름·목록 | 대기 (착수했다가 멈춤) |
| S5 | Git 참조값·PR 백업·복원 | 대기 |
| S6 | 여러 기기·모바일 | 대기 |
| S7 | 기존 메모 이전 (도메인별 목록) | 대기 |
| S8 | 통합 설계안 (새 저장 체계 한 장) → returns/REQ-001.md | 이번에는 하지 않음 (Owner) |

완료(유지): [S1](research/S1_STORAGE_FORM.md) jsonl+SQLite 투영 · [S2](research/S2_CONCURRENT_WRITES.md) 역할별 스트림+잠금+단일 CLI · [S3](research/S3_ROLLUP.md) 쓰기마다 도메인 view 재생성·필수 머리 8칸

- 공통 제약: 외부 서비스 없음, 키·시크릿 기록 금지, 삭제 없음, 상대 경로
- 범위 밖: 구현(impl 몫), Codex 쪽 설정, Owner 결정 대행
- 원천 읽기: RHS는 `git show <커밋>:<경로>`로 읽습니다(원본 checkout, 읽기만). bootstrap·Byul·AAA도 읽기만 합니다. 실측 스크립트는 research/ 안에만 둡니다.
- 지난 판: [archive/2026-10-17_CURRENT_scope-v1.md](archive/2026-10-17_CURRENT_scope-v1.md)
