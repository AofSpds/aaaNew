# 관계 엔진 결정 항목 D1–D21: 기본값, 반박 검토, 권고안

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 대상: [RELATION_ENGINE_PLAN_CLAUDE.md](RELATION_ENGINE_PLAN_CLAUDE.md) §8의 D1–D9, [JEV_BYUL_COMPARISON_CLAUDE.md](JEV_BYUL_COMPARISON_CLAUDE.md) §6의 D10–D13
- 방법: 결정 그룹 5개(저장·관계·검토·view·담당)에 각각 회의적 검토자 1명을 붙여 기본값을 문서 근거로 반박하게 하고, 완결성 검토자 1명이 빠진 결정을 찾았다. 검토자는 계획·갭·선행 대조·요구사항·Codex 실험 보고서·실행기 접점 조사·JEV-BYUL 스키마 문서 13편을 읽었고 파일을 수정하지 않았다. 판정 어휘: **유지** = 반박 불성립, **변경** = 더 나은 선택이 분명, **Owner 선택** = 가치 판단.
- 결과: 유지 8 (D1·D6·D7·D8·D10·D11·D12 + 보완), 변경 5 (D2·D3·D4·D9·D13), Owner 선택 1 (D5). 누락 결정 8건(D14–D21) 추가.

## 1. D1–D13 요약표

| # | 결정 | 판정 | 권고안 (검토 후) |
| --- | --- | --- | --- |
| D1 | 저장 형식 | 유지 (높음) | jsonl 추가 전용 + SQLite 투영 + 그래프 DB 없음. 단 `index.sqlite`는 gitignore, jsonl은 종류×기록 주체(스트림)로 분할, 봉투에 `created_by`·`stream_id/sequence` 추가, digest 정규화 규칙 명시 |
| D2 | 관계 종류 | **변경** (중간) | 9종 유지 + `COEXISTS{scope}` 1종 추가(역할별 공존·양립 결과 기록용). 완전 중복 = `OVERLAPS(unique_a=unique_b=∅)`로 명시. `SUPPORTS`·`SIMILAR_TO`는 v1에서 "예약(생산자 없음)" |
| D3 | 후보 생성에 임베딩 | **변경** (중간) | 임베딩은 1차 제외 유지. 단 "같은 작업대·같은 역할" 필터 제거 → 프로젝트 안 전체 쌍(현재 66쌍)을 어휘·경로·slot 근접으로 순위화. 역할은 필터가 아니라 질문 2의 입력. 임베딩 추가 트리거는 측정 가능한 조건(사람이 추가한 쌍의 생성기 누락 비율, 항목 수 상한)으로 |
| D4 | 자동 변경 허용 범위 | **변경** (중간) | "모델 점수 기반 자동 변경 없음"은 유지. 자동 범위를 (a) 정규화 digest(본문+claim_type+조건) 동일 기록의 출처 병합(삭제 없음), (b) 사람 authority로 해석되는 instruction_ref에 의한 supersede로 한정해 정의. 첫 사례까지는 그것도 후보 기록으로 두고 Owner 일괄 승인 뒤 자동화 |
| D5 | 검토 주체 | **Owner 선택** (중간) | 첫 사례(단계 4)까지 Owner 단독 + REVIEW_INBOX 한 줄 응답 형식. 미응답이 이어지면(L01처럼) 계층 분리 — LLM 세션이 reviewed 승격·merge 후보만 승인, 평가 라벨은 Owner 전용 — 를 택할지 Owner가 결정. 구조적 제약: 평가 라벨은 사람만(아니면 Judge 비교가 순환) |
| D6 | 필수/선택 누락 시 bundle | 유지 (중간) | 필수 누락 blocked, 선택 누락 표시 후 생성. 보완: 선택 누락을 manifest뿐 아니라 MD 본문에도 표시, blocked의 하류(스텁 view 공개·우선 검토 적재·retire 시 재선정·required 예산 면제) 명시. blocked가 사용자 직접 세션을 잠글지는 R04 예외 정책으로 Owner 별도 결정 |
| D7 | 생성 view 수정 | 유지 (높음) | 읽기 전용 + 양방향 동기화 없음. 보완: views/ 쓰기를 PreToolUse 거부로 강제(Claude 실측 deny), 제안은 REVIEW_INBOX.md 직접 기록이 아니라 추가 전용 큐 기록으로, REVIEW_INBOX.md는 사람 답변지로만 생성 |
| D8 | 저장소 위치 | 유지 (중간) | `projects/bootstrap/memory-store/`. 선행 조건: .gitignore 신설, 쓰기·커밋 주체 결정(D15), 작업대 CLAUDE.md는 store가 아니라 views/만 import, `rsch/sub`의 "기억 저장소"(세션 지속 기억)와 이름 구분 |
| D9 | 구현 담당 | **변경** (중간) | 단계 1–4 코드는 Claude 세션 단일 담당(프로토타입은 복사, Codex 파일 무수정). Codex rsch_sub_memory는 고정 원천 제공·수용 기준 독립 검증·(단계 5) KevJudge 실행만. Codex 측 전달 영수증은 Codex rsch 세션. 단계 4 전달 대상은 cwd=bootstrap/rsch 자식 세션. collection 원장 고정·정본 이전·L01 응답은 Owner 직접 지시 |
| D10 | UNKNOWN 처리 | 유지 (높음) | abstention 유지. 세 층으로 명시: 선택지 "판단불가"(모델 class) / 시스템 abstention(`abstain_reason` enum: rule_not_applicable, rule_error, model_unknown_option, low_margin, order_inconsistent, input_truncated, question_contradiction) / 사람 라벨 open. 학습 class는 라벨 30건 후 재검토 |
| D11 | error budget / hard block | 유지 (높음) | 모델 판정 기반 hard block 없음·propose-only 유지. head별 재정의: exact-rule=자동+전량 로그+표본 감사 / model=propose-only / human=유일 authority / block=규칙 기반만. 수치 예산은 "라벨 30건 전 미정"(1% bound엔 ~299 negatives). 미해결 충돌 view 전달 차단 여부는 D6·R04와 묶어 별도 Owner 항목 |
| D12 | 판정 기록 영속 | 유지 (높음) | 영속·거부 판정 보존. 보완: 마스킹 정정 기록(`redact`) 추가(삭제 없이 본문 회수), pilot 원장은 동결 후 source_refs 달아 1회 import, 투영에 "버전 불일치 judgment 재사용 금지" 명시, 보유 기간·원응답 전문 계층은 라벨 30건 후 Owner 결정 |
| D13 | 관계 분류 고정 시점 | **변경** (중간) | 추적 수단을 group_version(선정 그룹 버전)이 아니라 봉투 `schema_version` + 별도 `taxonomy_version`(relation·judgment·combine 규칙에 태깅, 변경은 migration/revises 기록)으로. 단계 2 = v0 후보, 단계 3 첫 reviewed 라벨 + 단계 4 첫 전달 사례 통과 후 v1 선언 |

## 2. 변경 판정의 근거 요약

- **D2**: 계획 §3 결합 규칙은 OVERLAPS/CONFLICTS_WITH/open 셋만 낸다. 실측 세 사례 중 P(역할별 공존)와 파일럿 다수 결과(양립 11/18, "별개" 12/18)를 기록할 kind가 없어 후보 생성기가 같은 쌍을 반복 제안한다. 완전 중복(오분류 후보 9건)은 병합 시 고유 조건 손실이 가장 크므로 표현을 명시해야 한다. 선행 연구의 SAME_REFERENT/SAME_SCOPE 층과 대응.
- **D3**: "같은 작업대·같은 역할" 필터는 실측 사례 P01(rsch ↔ rsch_sub_memory)과 R06이 겨냥한 역할 간 문서 중복(README:141 ↔ INTAKE:7)을 구조적으로 배제한다. "회수율 낮으면" 트리거는 라벨 0건 상태에서 발화할 수 없다. 현재 규모(66쌍)에서 전체 쌍 생성은 비용이 없고 유일한 회수율 분모다.
- **D4**: "동일 digest"의 범위가 미정의라 본문만 해시하면 조건이 다른 동일 문장을 자동 병합해 사례 2 수용 기준을 위반한다. "명시된 대체 지시"의 출처가 모호해 에이전트가 적은 문구가 지시로 읽히면 모델 출력이 사실상 자동 변경을 일으킨다. 해당 change.kind가 §4 표에 없다. 선행 분류 연구는 생략 후보도 "처음엔 후보로만"을 권고.
- **D9**: "또는"은 담당 결정이 아니며 동시 수정·권한 미결정을 구현 첫 단계에 들여온다. Codex rsch_sub_memory의 지속 기억은 Owner 정정("외부 연구 해석 자체검증 정도", "제품 구현으로 확대하지 않는다")을 보존하므로 구현을 맡기면 그 범위와 충돌한다. 프로토타입은 표준 라이브러리 단일 파일이라 복사로 충분하고, 세션 간 수동 인계 실패 사례(LESSONS_CODEX)가 이미 있다.
- **D13**: group_version은 계획·GRAPH 연구 모두에서 선정 그룹 멤버십 버전이다. taxonomy 추적에 쓰면 bundle 보류 의미가 잘못 발동하고 judgment는 태깅되지 않는다. 라벨 0건·실사례 3쌍에서 v1을 잠그면 첫 사례 뒤 v2가 거의 확실하다. 선행 연구 "fixed taxonomy after labels".

## 3. 누락 결정 D14–D21

| # | 결정 | 누가 | 제안 기본값 |
| --- | --- | --- | --- |
| D14 | 식별자 체계 | 구현자 (Owner 확인 1건: 사람이 읽는 라벨 필수 여부) | `<type>_<ULID>`(시간순, 두 세션 무조정 발급). memory_id = `m_<ULID>` 1회 + 정수 version. source_id = 저장소 상대 경로 슬러그. 사람용 `label`은 선택 필드. `latest` 금지 |
| D15 | 다중 세션 동시 쓰기·Git | **Owner** | 쓰기 주체는 엔진 CLI(`store.py append`) 하나. jsonl에 `.gitattributes merge=union`. `index.sqlite` gitignore. 자동 커밋 없음, verify가 미커밋 기록 수 보고. 커밋은 사람 지시 때만 |
| D16 | 삭제·보존·교정 | **Owner** | 시간 만료 없음. retire는 투영에서만 제외. 교정은 `change.kind=redact` 하나(tombstone, digest·연결 보존, Owner 권한). 원자료 삭제 → `source_rev deleted` + DERIVED_FROM 기억 open |
| D17 | 언어·정규화 | 구현자 (Owner 한 줄 확인: 본문 번역·의역 금지, view·INBOX 한국어) | body = 원문 그대로. 필드명·kind·상태값 영어. view·REVIEW_INBOX·abstain_reason·질문 한국어. 정규화 = UTF-8·NFC·LF·줄끝 공백 제거·JSON sort_keys. `canonicalization="v1"` 기록 |
| D18 | 첫 사례의 작업대·세션·전달 경로 | **Owner** | 작업대 `projects/bootstrap/rsch`, 역할 rsch, 업무 "runtime lifecycle 연구". Claude가 `rsch/CLAUDE.md`(import 1줄 + 생성 정보) + `rsch/views/rsch/current.md` 생성. Codex 파일은 읽기(해시 등록)만. 훅은 `.claude/settings.json` 대신 실행 스크립트 `--settings`. 검증은 데스크톱 세션이 아니라 cwd=bootstrap/rsch로 띄운 CLI 세션 |
| D19 | 기억 단위 크기·등록 주체 | **Owner 승인** | 1 memory_rev = 원문에 그대로 있는 문장·목록 항목·표 행 1개. 자동 분할 없음. 문단은 `claim_type=summary` + DERIVED_FROM. 단계 1은 수동 12개 |
| D20 | 민감 정보·공개 범위 | **Owner** | 상대 경로만(절대 경로 등록 거부). 세션 ID·이메일·토큰 패턴 거부. delivery_receipts는 세션 기록 원문이 아니라 attachment 종류+bundle_id+시각만. 봉투 `sensitivity ∈ {repo, local}`, local은 gitignore. 파일럿 데이터(절대 경로 18+19건) 이관 시 상대화 |
| D21 | 코드 위치·Codex 자산 이관 | **Owner** | 코드 = `projects/bootstrap/memory-engine/`(표준 라이브러리만). `rules()` 재작성. KevJudge는 `vendor/kev` 경로 import(복사 없음, 선택 의존). 번들 Python은 호출만. 데이터는 단방향 import 스크립트(cases→memory_rev+source_rev, annotations→judgment proposed) |

## 4. Owner가 지금 정해야 진행되는 것 (최소 집합)

단계 1 착수에 필요한 결정만 추리면 다음 여섯이다. 나머지는 기본값으로 시작해도 된다.

1. **D5** 검토 주체(첫 사례까지 Owner 단독으로 갈지)
2. **D9** 구현 담당(Claude 단일 담당 권고 수용 여부, Codex rsch_sub_memory 범위 재지정 여부)
3. **D15** 쓰기·커밋 주체와 자동 커밋 금지
4. **D16** 보존·교정 정책(원격 이력에 영구 보존 전제 수용)
5. **D18** 첫 사례 전달 경로(공유 작업대 `projects/bootstrap/rsch`에 CLAUDE.md·views/ 생성 허용)
6. **D20** 민감 정보 규칙(상대 경로·세션 ID 거부·local 분리)

## 5. 근거

- 검토 원문: 워크플로 `wf_d3fea74c-1f5` 결과(6 에이전트, 126 도구 호출). 각 항목에 반박 시도·대안 2–4개·근거 경로가 있다. 이 문서는 그 요약이다.
- 실측 확인된 사실(검토자 보고): 저장소에 .gitignore 없음, git 저자 1종, `research/sub-memory/` 미추적, `.venv` 약 3.4 GB·`.cache` 약 1.8 GB 미추적, 파일럿 원장 18/18/24/282행(최대 190 KB), cases.jsonl·dataset.json에 절대 경로 포함.
