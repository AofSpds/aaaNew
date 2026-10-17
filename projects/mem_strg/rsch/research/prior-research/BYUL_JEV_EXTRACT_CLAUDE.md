# S0 Byul·JEV 추출 — 저장 체계 설계에 걸리는 것

- 작성: 2026-10-17, AAA/NEW/RSCH/MEM_STRG
- 방법: Sonnet 서브에이전트 1명이 읽기 전용으로 추출했습니다(도구 호출 80회). 이 채널은 원문을 다시 대조하지 않았습니다 [문서 요약]. Pro 의뢰의 입력으로 씁니다.
- 원천 약어:
  - **BM-NN**: Byul main(79c00bf) `versions/v0.01/memory/NN_*.md`
  - **BV**: Byul main `versions/v0.1/`
  - **BW-\***: Byul 브랜치 `origin/research/byul-world-model-deep-review-20260826`(1144d07) `versions/v0.01/world-model/`
    - ATLAS = PRIOR_ART_ATLAS v1.0
    - DR = DEEP_DESIGN_REVIEW v1.0 CANDIDATE
    - Q = OWNER_QUESTIONS
    - RM = ROADMAP v2.0 CANDIDATE
    - ID = OWNER_DECISION_Q0-1
  - **AR0·AR0B·AR1·AR2·AR3**: AAA(체크아웃 `codex/hef-operations`) `projects/AAA/work/jev-byul-research/20260927/`의 r0, r0b, r123/r1·r2·r3
  - **AP**: AAA `20260926/PLAN_PUBLISHED_EN_KO.md`
- 읽기 한계:
  - AR1이 인용한 Byul synthesis126은 로컬 Byul에 없습니다(main은 125까지) [미확인].
  - v0.1 테스트는 실행하지 않았습니다.

## 1. Byul 원칙 중 저장 설계를 제약하는 것

1. **관계(relation)가 기본 단위입니다.** "View를 저장할 것인가"는 핵심 질문이 아닙니다. 물어야 할 것은 "과거·현재의 관계와 수명주기를 재현·감사·재도출하려면 최소한 무엇을 보존해야 하는가"입니다 [BM-81].
2. **모든 모델은 View입니다.** 객체, 표, 그래프, 이벤트 로그, ID, 캐시 모두 로컬 구현 View로 허용합니다. 다만 그것을 전역 법칙으로 굳히지는 않습니다 [BM-84, BM-123].
3. **네 평면을 섞지 않습니다.**
   - (a) 기반 관계 네트워크의 변경
   - (b) View 수명주기
   - (c) View 내부의 파생 관계
   - (d) 구현상의 materialization·캐시·저장

   캐시와 저장은 구현 결정일 뿐, 세계가 바뀌었다는 증거가 아닙니다 [BM-98].
4. **View의 성능은 목적에 따라 정해집니다.**
   - 원천을 다시 만들 수 있는가, 구분을 보존하는가는 반복성과 별개의 축입니다.
   - 완전히 되돌릴 수 있는 것은 기대하지 않습니다. 대상은 보존 계약과 손실 프로필(preserved/collapsed/discarded)입니다.
   - 시스템은 "무엇을 보존·축약·생략했고, 고해상도 원천을 어디서 다시 찾는가"에 답할 수 있어야 합니다 [BM-101–103, 123].
5. **추상화의 "discard"는 생략이지 원천 삭제가 아닙니다** [BM-103, BM-110].
6. **수명주기와 동일성은 다릅니다.** 전역 동일성은 가정하지 않고, 계보는 보존합니다 [BM-104, BM-91].
7. **존재·가시성·활성·보존·초기화·보관·논리삭제·물리삭제는 모두 다른 상태입니다.**
   - 초기화(reset)는 삭제(delete)가 아닙니다.
   - 법적 예외가 있으면 명시해서 모델링합니다 [BM-116–118].
8. **원천을 삭제하면 파생 상태를 다시 계산합니다.**
   - 가능하면 전역 재구축이 아니라 선택적으로 재계산합니다.
   - 이미 일어난 과거 사건은 이력으로 남습니다.
   - 이것을 특정 그래프 DB나 이벤트 소싱으로 단정하지 않습니다 [BM-119, 120].
9. **공통 View → 역할 View의 다단 처리는 선택 사항입니다.**
   - 공통 View는 유일한 정본이 아닙니다.
   - 필요하면 고해상도 원천으로 되돌아가 읽을 수 있습니다(fallback).
   - 중간 표현이 의미를 좁히는 병목이 되면 안 됩니다 [BM-110, 123].
10. **핵심 원칙**: 변화 가능성, 비고정 실체성, 합성·발현, 조건·관계 의존성.
    - Causal Set, Petri Net, Event Structure 같은 어떤 구현도 가능하지만, 숨은 가정이 들어오지 않는지 검토합니다 [BM-11].
11. **Round-1의 수렴**: 내용 주소(content-addressed) 원천이 가장 아래 권위층입니다. 변화는 추가 전용 + 계보로 나타내고, 파생 view는 다시 만들 수 있는 투영입니다. 다만 "규율 있는 Git+Markdown이 더 나을 수 있다"는 반론이 남아 있습니다 [BM-16, 17].
12. **병렬 thread마다 자기 추가 전용 Run Journal을 둡니다.** 공유 가변 메모의 경합을 피하기 위해서입니다 [BM-22, 28].
    - v0.1의 권위 순서: raw memory > 파생 index/view > routing > 요약 [BV SOURCE_MANIFEST].

## 2. Byul 최신 (deep-review 브랜치, 모두 NON-NORMATIVE·NOT VALIDATED)

- **ID (Q0-1, Owner 방향)**
  - BYUL은 "RELATION-FIRST DATA / WORLD MODEL PROJECT"입니다. 언어, compiler, runtime은 선택적 도구입니다.
  - 순서: 세계·데이터 의미 → 투영·어댑터 → 도메인·사람·AI 추상화 → …
- **DR (CANDIDATE)**
  - "하나의 범용 동적 그래프 runtime"으로 바로 구현하는 것은 비권고입니다.
  - 다층 의미 모델과 명시적 실행 프로필을 둡니다. `WORLD SEMANTICS ≠ EXECUTION IR ≠ RUNTIME DATA STRUCTURE`
  - 가능한 네트워크를 전부 materialize하지 않습니다. 실현된 것은 trace로 남깁니다.
  - 위험: "Graph/meta-rule explosion — high"
- **RM v2.0 (CANDIDATE)**: R0–R15 단계. v1.0이 Owner 채택 전까지 현행입니다.
- **ATLAS**
  - P0: Causal Set, Petri, Event Structure, DPO/SPO 그래프 변환, Provenance, IVM, lenses
  - P1: RDF·관계 모델·Datalog
  - P2: Event Sourcing
  - "Do not import blindly"
- **Q**: Owner 결정 칸은 모두 비어 있습니다. 저장 관련 항목:
  - Q0-8: VIEW는 기본적으로 분석·투영
  - Q1-10: 최적화한 뒤에도 원천 계보를 다대다 provenance 연결로 유지
  - Q2-5: 인과(causality)는 OPEN

## 3. Byul v0.1 구현 (실험, 미검증)

- stdlib 전용 `src/byul_v01.py`(약 480줄)입니다.
- **데이터**: Byul 메모 `.md` 자체를 줄 단위 `MemoryAtom`으로 읽고, sha256과 정규화 digest를 계산합니다.
- **파생 view 6개**: 의존성은 코드에 고정돼 있습니다. raw를 대체하지 않습니다.
- **Router**: 모르는 의도나 정확한 수치가 필요한 요청은 `REVIEW_REQUIRED`로 보냅니다. 핵심 원칙도 항상 `REVIEW_REQUIRED`입니다.
- **가상 변경 시험**:
  - 복사본에 줄 하나를 더하고, digest와 영향 view, `invalidation_radius = 영향 view 수 / 전체`를 계산합니다.
  - 소스는 고치지 않습니다.
- **한계**:
  - Git 객체에 고정하지 않고 파일시스템에서 읽습니다.
  - 정규화 기준이라 바이트 단위로 같지 않습니다.
  - 태깅은 휴리스틱이고, 상태 전이는 실제로 일어나지 않습니다 [BM-17].

## 4. JEV

- **무엇인가**
  - typesafe.ai의 System-One 계열 판단 모델입니다(문서상 `jev-1.13.0`). 상태와 typed 질문(Choice/Score/Noul)을 주면 확률을 돌려줍니다. **저장 기술이 아닙니다.**
  - 가중치는 비공개입니다. JEV-like(OpenJev, Laya)는 외형만 비슷합니다 [AR3 F01].
- **AAA 결론**: "좁은 의미 신호의 비교 대상으로는 유효하나 입증된 AAA Memory subsystem도 범용 보정 권위도 아님" [AR3].
- **역할 처분**
  - **PLAUSIBLE**: M01 문맥 관련성 후보, M02 의미 중복·관계 제안, M05 요약 충분성 경고
  - **INSUFFICIENT**: M03, M04, M11, M12
  - **결정적 대안 우선**: M06 교정 유지, M07 권한, M08 ID·시간·NO_RERUN
  - **CONTRADICTED**: M09 capture 대체, M10 인수·삭제 권한
- **쓰면 안 되는 곳**: 정확한 ID·해시·시각·권한·원천 우선순위·영수증. 확률은 권한이 아닙니다 [AR3 F07, F09].
- **기록할 때**
  - 분포 전체를 보존합니다. 예: (0.5,0,0.5)와 (0,1,0)은 기대값이 같습니다 [AR3 F05].
  - 모델·endpoint·질문 순서·원천 revision 등도 남깁니다(체크리스트) [AR3 F08].
- **수치** (모두 공급자·저자 보고, AAA 측정 아님):
  - $0.042/M tokens. 64k total, 32k state.
  - E01: Direct 62.6% vs Haiku 81.3%. 5신호 로지스틱 Jev 95.0%.
  - 지연 239 ms median.
- **한계**
  - 독립 재현이 없고, 한국어 근거도 좁습니다.
  - 질문 문구·순서에 민감합니다.
  - **호스팅 API라서 "외부 서비스 없음" 원칙과 충돌합니다.** 로컬 대안은 품질이 같다고 입증되지 않았습니다 [AR3 F04, F06, F10].
- 로컬 실측(BTSR 아카이브): Kev 0.8B 17/36, 선택지 순서에 따라 판정이 바뀜(겹침 10/18).

## 5. 그래프

**Byul 쪽**
- Causal Set은 최종 구조가 아니라 강한 후보입니다. link만 써도 "O(N²)에 근접 가능"하고, "자동 경량 storage가 아니라 의미론적 추상화"입니다 [BM-02].
- Petri·Occurrence Net·Event Structure·LTS는 서로 보완하는 계열이고, 목적별 투영입니다. 단일 정본 표현을 강제하지 않습니다 [BM-03].
- 합성은 View 조건부이며, 자동 전이 폐쇄가 아닙니다 [BM-98].
- 의존성 추적은 특정 그래프 DB와 같은 말이 아닙니다 [BM-119].
- ASA v2.1 후보:
  - 고차 그래프와 hypergraph는 참조·저장 후보입니다.
  - DBSP/IVM은 최소 재계산 후보입니다.
  - provenance는 트리가 아니라 회로·DAG로 둡니다.

**AAA 쪽**
- H23: 논리 역할마다 DB를 둘 필요는 없습니다. property graph는 "optional, not BYUL itself"이고, "Git plus PostgreSQL may suffice"라는 설계 제안이 있습니다. R2 처분은 ALTERNATIVE입니다 [AR1, AR2].
- 도달 가능성으로는 유효한 합성, 권한, 부정 의존성을 증명하지 못합니다. "graph alone does not discover them" [AR2 H02, H16].
- 기본값으로 그래프·스키마·Pair·공급자를 고르지 않습니다. 단순 처리와 현행 유지가 필수 비교 대상입니다 [AR0B Q10, AP §3.4].

**그래프가 정당화될 조건** (원천들을 종합)
1. 이름 붙은 작업에서 일반 기록·색인보다 실질적으로 우위이고, 유지 비용까지 포함해도 그렇다
2. 관계 위의 관계, 다항 구조처럼 일반 기록으로 나타낼 수 없다는 증거가 있다
3. 부정·미지 의존성의 의미가 먼저 정의돼 있다

## 6. 프로젝트 간 기억 패턴 (AAA R0·R0-B)

- **R0**: AAA는 백지가 아닙니다. Git 진입 → 얇은 Current → 이력·근거 경로로 실제 인계를 복구했습니다 [AR0 F01].
- **R0-B**: 패턴 P01–P27
  - 근거 유형: OBSERVED_OPERATIONAL 4, BOUNDED_VALIDATED 3 …
  - 주요 패턴:
    - 얇은 Current + 정확한 상세 회수(P01)
    - 근거를 보존하는 의존성 무효화(P04)
    - Source와 인수한 Delta 구분(P05)
    - 반환·인수·반영을 별도 전이로(P07)
    - 열화된 보존을 정직하게 표시(P10)
    - 원천 보존 + 별도 교정본(P17)
    - 후보 결정 원장(P19)
  - 기준선 **KEEP01–05**: Git 진입 + 얇은 Current + 정확한 확장, 수동 OPI, …
  - 재사용 후보: RC01–RC06
  - 제외: 파일 수·PASS 라벨을 효용으로 쓰는 것, 기본 graph/JEV/schema 선택

## 7. 지금 임시 설계(S1–S3)와 어긋나는 점

1. **Git 기준선**: AAA KEEP01(Git 문서 복구)과 Byul의 "Git 객체 고정" 방향이 "Git에는 참조값만"과 긴장 관계에 있습니다. 원천 본문이나 해시를 Git에 남길지가 핵심입니다 [미정].
2. **CURRENT 덮어쓰기**: CURRENT가 jsonl 위의 파생 view이고 이전 판을 복원할 수 있을 때만 Byul과 맞습니다. S1 B안은 이 조건을 만족합니다.
3. **쓰기마다 전체 재생성** vs Byul의 "선택적 재계산·IVM". 지금 규모에서 어느 쪽이 나은지는 미정입니다.
4. **단일 CLI + 잠금** vs Byul의 "thread별 journal". 충돌은 아니지만, 쓰는 지점이 하나가 됩니다.
5. **그래프 DB 없음**은 Byul·AAA 원천과 대체로 맞습니다. "그래프 DB 사용"은 Owner의 말이고, 원천에는 채택 근거가 없습니다.
6. **JEV**: 호스팅 API라 "외부 서비스 없음"과 충돌합니다. ID·시각·권한·삭제는 JEV를 쓰지 않는 영역입니다.
7. **Byul 내부**: 이른 구조 점검과 늦은 성능 점검의 순서가 미조정입니다(H24). 사용 시점 동적 재구성에는 AAA 쪽 반론이 있습니다(H06).

## 8. 저장 설계가 정해야 할 것 (OPEN)

1. View·수명주기를 무엇으로 보존하나 (정의, 버전, provenance, materialization)
2. 보존 계약·손실 프로필을 어떤 형태로 기록하나
3. 상태 모델(가시성 … 물리삭제)과 법적 예외의 적용 범위
4. 의존성 추적의 단위와 완전성 (부정·미지 의존성)
5. View 동일성과 계보의 인코딩
6. 공통 경유 vs 원천 직접, 동적 vs materialize
7. 물리 저장 선택: Git+typed record / 관계형 / 그래프. 이름 붙은 작업과 전체 비용 근거가 없으면 비교할 수 없습니다
8. JEV 역할: 후보는 M01·M02·M05뿐입니다. 한국어 검증과 로컬 대체 가능성이 미정입니다
