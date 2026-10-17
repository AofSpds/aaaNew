# S0 원천 수집 — Byul·JEV·그래프 DB·BTSR 연구

- 작성: 2026-10-17, AAA/NEW/RSCH/MEM_STRG · REQ-001 개정 2
- 원칙(Owner): "너무 혼자 딮써치 하지 마시고, 연구 결과를 모으고 기록한 후 초벌 연구와 프로챗으로 연구 외주줄 계획을 세우시면 됩니다." 그래서 이 문서는 **수집 기록**입니다. 깊은 조사는 Pro 의뢰로 넘깁니다([PLAN](../../PLAN_PRELIM_AND_OUTSOURCE_CLAUDE.md)).

## 1. 모은 것

| 원천 | 기록 | 등급 |
| --- | --- | --- |
| BTSR 메모리 연구 22건 + 폴더 3개 | [archive/2026-10-17_BTSR_MEMORY_RESEARCH.md](../../archive/2026-10-17_BTSR_MEMORY_RESEARCH.md) (aaaNew 6b19bb0, sha256) | 문서 요약 |
| Byul 원칙·최신 브랜치·v0.1 구현, AAA JEV-BYUL 연구(9-26/27) | [BYUL_JEV_EXTRACT_CLAUDE.md](BYUL_JEV_EXTRACT_CLAUDE.md) | 문서 요약 |
| 내장형 그래프 DB 후보의 2026년 상태 | 아래 §2 | 웹 2차 출처 |
| SQLite 그래프 규모 실측 | 아래 §3 | 실측 |

Byul 최신본 위치: 로컬 main(79c00bf, 2026-08-26)과 deep-review 브랜치(1144d07, 2026-08-26)를 기준으로 했습니다. 이보다 새 판이 있는지는 [미확인]입니다. AAA가 인용한 synthesis126은 로컬에 없습니다.

## 2. 내장형 그래프 DB 후보 (외부 서비스 없이 로컬에서 도는 것) [웹 2차 출처, 2026-10-17 검색]

| 후보 | 형태 | 상태 |
| --- | --- | --- |
| SQLite 재귀 CTE | 지금 쓰는 투영에 그대로 | 표준 라이브러리. §3 실측 |
| Kuzu | 내장 property graph, Cypher | **2025-10-10 저장소 archived.** 마지막 v0.11.3, 새 릴리스 없음 |
| RyuGraph | Kuzu 포크 (Predictable Labs) | 활동 중으로 보고됨 |
| LadybugDB (lbug) | 내장 property graph, Cypher, ACID | Kuzu 대안으로 언급됨. 분석용 큰 DB 지향 |
| DuckPGQ | DuckDB의 SQL/PGQ 확장 | 연구 단계 커뮤니티 확장. 2026 릴리스 공지는 확인하지 못함 |
| FalkorDBLite | Redis+FalkorDB를 하위 프로세스로 띄움 | 개발·CI용. 엄밀히는 프로세스 내장이 아님 |
| Oxigraph (pyoxigraph) | 내장 RDF, SPARQL | 디스크 저장. 저장 형식 안정성 경고가 있었음(옛 판) |
| CozoDB | 내장 Datalog | 근거가 약함 (비교 사이트 1곳) |

- 출처:
  - Kuzu: [pypi kuzu](https://pypi.org/project/kuzu/), [oneuptime 2026-08](https://oneuptime.com/blog/post/2026-08-12-kuzu-archived-pin-0-11-3-fork-or-migrate/view)
  - RyuGraph: [ryugraph](https://github.com/predictable-labs/ryugraph)
  - DuckPGQ: [duckpgq demo](https://duckdb.org/library/duckpgq-demo/), [zeli 2026-07](https://zeli.app/en/story/49038481)
  - FalkorDBLite: [falkordblite](https://docs.falkordb.com/operations/falkordblite.md)
  - LadybugDB: [lbug](https://docs.rs/crate/lbug/0.19.0/source/lbug-src/README.md)
  - CozoDB: [cozodb vs duckdb](https://toolradar.com/compare/cozodb-vs-duckdb)
  - Oxigraph: [oxigraph python](https://git.nextgraph.org/NextGraph/oxigraph/raw/commit/2a88927f3f26a2759fe6cd67f11b165982b1c565/python/README.md)
- 공통 제약 [판단]: 내장 DB는 대개 쓰는 프로세스가 하나입니다. 여러 세션이 동시에 써야 하므로(S2), 그래프 DB를 정본에 두면 S2 결론과 부딪힙니다. **추가 전용 원장을 정본으로 두고 그래프는 투영으로** 두는 것이 지금까지의 결과와 맞습니다. 단일 쓰기 제약은 각 DB 문서로 확인하지 않았습니다 [미확인].

## 3. SQLite 재귀 CTE 규모 실측 [실측]

- 스크립트: [s0_graph_scale_bench.py](../storage-structure/s0_graph_scale_bench.py) · 원자료: [s0_graph_results_20261017.json](../storage-structure/s0_graph_results_20261017.json)
- 모형(가정):
  - 기록마다 최근 2,000건 안에서 1–3개 기록에서 파생(DERIVED_FROM)됩니다.
  - view는 기록 20개를 고릅니다.
  - 질의 200회. HANAL, SQLite 3.50.4

| 기록 수 | 노드·관계 | 출처 전부 (위로) | 영향 범위 (아래로) |
| --- | --- | --- | --- |
| 1만 | 1.0만·2.1만 | 1.8 ms, 따라 나온 노드 1,686 | 7.9 ms, 노드 5,318 · view 50 |
| 10만 | 10만·21만 | 115 ms, 노드 73,572 | 181 ms, 노드 89,757 · view 500(전부) |
| 100만 | 103만·210만 | 1.36 s, 노드 791,749 | p95 2.4 s (중앙값은 모형 결함으로 무효*) |

- *100만 건 모형에서는 원자료 대부분이 어떤 기록에서도 참조되지 않아 영향 중앙값이 0으로 나왔습니다. p95만 의미가 있습니다.
- **정정 (2026-10-18, Pro P1 지적 → [REVIEW](../../reviews/STORAGE_ENGINE_OPERATIONS_REVIEW_CLAUDE.md) #7)**: 바로 아래 "70–80%"는 10만·100만 건에만 맞습니다. 1만 건은 16%(1,686/10,250), 10만 건은 72%, 100만 건은 77%입니다. P1 의뢰서의 "어느 규모든 70–80%"라는 표현은 틀렸습니다. 다만 "따라갈 범위 규칙이 엔진 선택보다 먼저"라는 해석은 Pro도 유지했습니다.
- 읽는 법 [판단]:
  - 파생이 촘촘하면 출처를 제한 없이 끝까지 따라갈 때 이력의 70–80%가 딸려 나옵니다.
  - 이것은 엔진 속도의 문제가 아니라 의미의 문제입니다. 전용 그래프 DB도 같은 수의 노드를 지나갑니다.
  - Byul의 "합성은 자동 전이 폐쇄가 아님"(BM-98), "Causal Set은 O(N²)에 근접 가능"(BM-02)과 같은 방향입니다.
  - 그래서 **따라갈 범위(깊이, 관계 종류, view 조건)를 정하는 규칙이 저장 엔진 선택보다 먼저**입니다.
- 한계:
  - 실제 메모의 파생 밀도는 재지 않았습니다. 모형이 실제보다 촘촘할 수 있습니다.
  - 그래프 DB와 직접 비교하지 않았습니다(설치하지 않음).

## 4. Pro에 넘길 질문 (초벌)

1. 추가 전용 원장 + 투영(관계형·그래프)에서, Byul 원칙(원천 재구성 가능성, 손실 프로필, 삭제 뒤 선택적 재계산, view 계보)을 담는 최소 기록 형식은 무엇인가
2. 따라갈 범위를 정하는 규칙(typed provenance, 깊이 제한, view 조건부 합성)의 선행 사례 (PROV, IVM/DBSP, differential dataflow)
3. 내장형 그래프 DB 후보의 2026년 유지 상태, 동시 쓰기 제약, Windows 지원, 라이선스, 그리고 "투영으로만 쓸 때" 이득이 있는 작업
4. JEV-like 판정을 외부 서비스 없이 쓸 수 있는가 (로컬 대안의 품질 근거). 판정 기록 형식
5. 이중 시간축(기록 시각과 유효 시각)을 메모 원장에 넣을지
