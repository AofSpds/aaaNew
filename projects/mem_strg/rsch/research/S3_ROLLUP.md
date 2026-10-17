# S3 롤업 — 역할 Current에서 도메인 Current로, 고정 머리 칸

- 작성: 2026-10-17, AAA/NEW/RSCH/MEM_STRG · REQ-001 S3
- 원천: RHS `STRUCTURE_SIMULATION_REVIEW_v0.1` §2·§4와 `rollup_sim.py` (둘 다 bc344e2, 읽기만), STRUCTURE_DECISIONS #29–#33
- 시제품: [s3_rollup_proto.py](s3_rollup_proto.py) (S1 B안 + S2 잠금 규칙, 표준 라이브러리만)

## 1. 결론

- 도메인 Current는 **사람이 모으지 않고 쓰기 CLI가 쓸 때마다 다시 만듭니다** [판단]. RHS에서 10-04 이후 도메인 Current가 멈춘 원인이 "누가 언제 모으나"였기 때문입니다.
- 머리 칸은 **필수 8칸**입니다. 그 밖의 칸은 선택이고, CLI가 형식을 검사합니다.
- RHS 시뮬레이션의 10-17 시나리오를 이 규칙으로 다시 돌렸습니다. 그때 드러난 문제 5가지가 모두 바르게 표시됐습니다 [실측].

## 2. 고정 머리 칸 [판단]

| 칸 | 필수 | 형식 |
| --- | --- | --- |
| role | 필수 | `<도메인>/<프로젝트>/<역할>` |
| session | 필수 | 세션 이름 (`RHS/ORDER/PLN`) |
| state | 필수 | `ACTIVE / WAITING / BLOCKED / IDLE / DONE` |
| updated | 필수 | CLI가 채웁니다 (사람이 적지 않음) |
| now · next | 필수 | 한 줄씩 |
| waiting_for | 필수(빈 목록 가능) | 종류가 붙은 대상: `role:` `verifier:<이름>#<교환ID>` `owner:<OR-ID>` `external:` |
| owner_wait | 필수(`-` 가능) | Owner 결정 대기 항목 |
| serves · cross_refs · base_commit · in_flight · body | 선택 | 로드맵 위 항목, 교차 항목 ID, 기준 커밋, 재실행 금지 효과, 자유 본문 |

- 정해진 칸이 아니면 거부합니다. 시제품에서 `history` 칸을 거부했습니다 [실측]. Current에 이력을 붙이는 일을 형식으로 막기 위해서입니다.
- 다만 본문(body)에 이력을 적는 것은 막지 못합니다. 길이 제한을 둘지는 미정입니다 [미확인].
- RHS 제안 16칸과의 대응:
  - "막힘"은 `state=BLOCKED`와 `waiting_for`로 나타냅니다.
  - "단계 수준(RETURNED…MERGED)"과 "열린 교환"은 Current에 두지 않고, 요청·회신 기록에 두고 ID로만 가리킵니다. RHS 시뮬 S1(HIGH)에서 같은 상태를 4곳에 적으면 서로 어긋났기 때문입니다.

## 3. 롤업 규칙과 시나리오 결과 [실측]

규칙:
- STALE(오래됨) 경고는 살아 있는 상태(ACTIVE·WAITING·BLOCKED)에만 냅니다.
- 교착 확인은 `role:` 대상끼리만 합니다.
- DONE인 역할을 기다리면 엇갈림으로 표시하고, 더 오래 갱신하지 않은 쪽 세션을 "확인" 대상으로 적습니다.
- 교차 항목이 한 프로젝트에만 있으면 표시합니다.
- 등록부(roles.json)에 있는데 Current가 없으면 MISSING으로 표시합니다.

| 시각 | RHS 시뮬 (bc344e2) | 이 규칙 |
| --- | --- | --- |
| 11:30 | 이상 없음. 그런데 PLN이 PMO를 기다린다고 잘못 나옴(검증자는 Current가 없음) | `WAIT verifier:PMOV#H3d ← order/pln` (바른 대상) |
| 13:30 | PLN↔PMO 가짜 교착 | 교착 없음. 두 역할이 같은 PMOV#H3d를 기다림. 그리고 `CROSS_ONE_SIDED RHS-X-001: sim 쪽에만 있음` (프로젝트를 넘는 일이 잡힘) |
| 15:30 | 엇갈림은 잡히지만 풀 사람이 없음 | `CONFLICT … → 확인: RHS/ORDER/PLN` |
| 23:59 | 8개 역할 모두 오래됨 경고(잡음) | 경고 2개뿐: order/pln WAITING 10h, sim/pln ACTIVE 12h. 쉬는 역할은 경고 없음 |
| 형식 검사 | 없음 | 잘못된 상태값, 종류 없는 대상(`PMOV`), 정해지지 않은 칸 3건을 모두 거부 |

- 생성 예시: [s3_sample_domain_current.md](s3_sample_domain_current.md). 원자료: [s3_results_20261017.json](s3_results_20261017.json)
- 시나리오는 RHS 시뮬을 이 머리 칸에 맞게 옮긴 것입니다. 14:00 PLN 갱신(PMO 대기)은 엇갈림 규칙을 시험하려고 더했습니다. 실제 사건 그대로는 아닙니다.

## 4. 속도 [실측]

- 역할 20개, 갱신 1만 건 기준, 쓰기 1건 + 도메인 view 재생성: 중앙값 8.4 ms, p99 10.7 ms, 최대 57 ms
- 재생성은 각 스트림의 끝줄만 읽습니다. 쓰다 만 끝줄은 건너뜁니다. 그래서 비용은 기록 수가 아니라 역할 수를 따라갑니다(설계상). 기록 수에 따른 증가는 따로 재지 않았습니다.

## 5. 남은 것

- STALE은 생성 시각 기준이라 오래 쓰지 않으면 view도 낡습니다. 대안은 "읽을 때 재생성"(`memo show domain`) 또는 세션 시작 훅입니다. 둘 다 미실측입니다.
- 로드맵 롤업 설계안: 같은 스트림에 `kind=roadmap` 기록을 두고 `serves` 연결로 트리를 만듭니다. 미실측입니다 [판단].
- 아카이브 롤업은 S4, 모바일 열람은 S6에서 다룹니다.
- 역할 등록부(roles.json)의 주인은 DPM 후보입니다(RHS 시뮬 S7 `projects\INDEX.md`와 같은 자리). Owner 결정 사항입니다.

## 6. 결정 카드 후보

| # | 질문 | 권고 | 미응답 시 |
| --- | --- | --- | --- |
| S3-a | 도메인 Current 생성 시점 | 쓰기마다 자동 재생성 (+ 읽을 때 재생성 검토) | 이 방식으로 연구를 계속합니다 |
| S3-b | 머리 칸 | 필수 8 + 선택 5, 정해진 칸이 아니면 거부 | 이 안으로 계속합니다 |
| S3-c | 역할 등록부 주인 | DPM | 보류합니다 (Owner 결정) |
