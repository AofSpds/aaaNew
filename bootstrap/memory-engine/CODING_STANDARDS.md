# bootstrap 코딩 기준 (초안 v0.1)

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션)
- 적용 범위: `bootstrap/memory-engine/`과 이후 bootstrap의 impl 작업대 코드. 실험 코드(`rsch/research/**/repro`, pilot)는 대상이 아니다.
- 성격: Owner와 함께 정하기 위한 초안. 각 항목 끝의 [D/E 번호]는 근거가 된 결정 항목이고, **[결정]** 표시는 Owner 확인이 필요한 항목이다.

## 1. 언어·런타임

1. Python 3.12 이상, **표준 라이브러리만**(관계 엔진 단계 1–4). 외부 패키지가 필요하면 그 단계 계획에 사유를 적고 Owner 승인 뒤 추가한다. [D21]
2. 실행 인터프리터: 이 PC의 `python`(3.13). Codex 번들 Python(`~/.cache/codex-runtimes/.../python`, 3.12)은 KevJudge 실행 때만 경로로 호출한다. 전역 설치·전역 설정 변경을 하지 않는다. **[결정]**
3. KevJudge 같은 선택 의존성은 import를 함수 안으로 지연하고, 없으면 명확한 오류로 보류(abstain)한다. 기본 경로는 RuleJudge만으로 동작해야 한다. [D10·D11]

## 2. 폴더와 파일

```text
memory-engine/
├─ engine/            # 패키지: store.py, schema.py, candidates.py, combine.py, review.py, change.py, view.py, judges/
├─ cli.py             # 유일한 쓰기 진입점 (append, rebuild-index, verify, generate-view …)
├─ tests/             # unittest. 실패 먼저(§5)
├─ fixtures/          # 시험용 고정 입력. 실제 기억 원장 복사 금지
├─ receipts/          # 변경 묶음별 E2E 영수증(§5)
└─ CODING_STANDARDS.md
```

- 모듈 하나 = 계획의 단계 하나. 모듈 간 의존은 `store` → `schema` → `review/change` → `view` 방향으로만.
- 파일·폴더 이름은 영어 소문자·`_`. 문서는 한국어 가능.

## 3. 데이터 규칙 (memory-store)

1. 기록은 **추가 전용 jsonl**. 줄 단위 JSON, 기존 줄 수정·삭제 금지. 교정은 `change.kind=redact`·`revises` 새 기록으로만. [D1·D12·D16]
2. 쓰기는 `cli.py` 경유만. 세션·에이전트가 jsonl을 직접 편집하지 않는다. [D15]
3. 공통 봉투: `record_id, record_type, schema_version, taxonomy_version(관계·판정만), recorded_at, created_by, stream_id, sequence, content_digest{algorithm, canonicalization, value}, source_refs[], causal_parent_ids[]`. [D1·D13·JEV-BYUL §4]
4. 식별자: `<type>_<ULID>`, memory_id는 최초 1회 발급 + 정수 version. `latest` 같은 가변 참조 금지. [D14]
5. 정규화(`canonicalization="v1"`): UTF-8, 유니코드 NFC, LF, 줄 끝 공백 제거, JSON은 `sort_keys=True, ensure_ascii=False, separators=(",", ":")`. 해시는 SHA-256. [D17]
6. 경로는 **저장소 상대 경로만**. 절대 경로·사용자명·세션 ID·이메일·토큰 패턴은 등록 시 거부한다. [D20]
7. 파생 파일(`index.sqlite`)은 jsonl에서 언제든 재구성 가능해야 하고 Git에 넣지 않는다. [D1]
8. 본문은 원문 그대로(번역·의역 금지). 필드명·enum은 영어, view·REVIEW_INBOX·abstain_reason은 한국어. [D17]

## 4. 코드 규칙

1. 판정과 변경 분리: Judge·규칙은 `judgment`만 만든다. 기억 상태를 바꾸는 코드는 `change.py` 하나이며, `authority`가 없거나 D4 허용 범위 밖이면 거부한다. **모델 점수로 change를 만드는 코드 경로는 두지 않는다.** [D4·D11]
2. 실패는 조용히 넘기지 않는다. 결측 상태는 `FAILURE / TIMEOUT / CANCELLATION / PARTIAL / NO_OUTPUT / NOT_INVOKED / UNAVAILABLE`로 구분해 기록한다. TIMEOUT을 NOT_INVOKED로 바꾸지 않는다. [JEV-BYUL §4]
3. 보류(abstain)는 enum: `rule_not_applicable, rule_error, model_unknown_option, low_margin, order_inconsistent, input_truncated, question_contradiction`. [D10]
4. 입력 절단 금지: 길이 초과는 오류로 거부(strict). 절단된 입력으로 판정하지 않는다. [M03]
5. 시간: 저장은 UTC ISO 8601, 표시는 KST. 실행 시각을 소급 생성하지 않는다.
6. Windows 호환: `pathlib`, 파일 열기는 항상 `encoding="utf-8"`·쓰기는 `newline="\n"`, 경로 구분자 하드코딩 금지.
7. 타입 힌트와 짧은 docstring(무엇을·왜). 주석은 왜를 설명할 때만.
8. 비밀값(토큰·API 키·비밀번호)을 코드·로그·기록에 넣지 않는다.

## 5. 시험과 검증

1. **실패 먼저**: 새 기능은 그 기능이 없어서 실패하는 시험을 먼저 쓰고, 통과시키는 코드를 쓴다. 각 단계 수용 기준(계획 §2–§6)이 곧 시험 목록이다.
2. 시험은 `python -m unittest discover -s tests`로 돌아가야 하고, 네트워크·모델 호출 없이 끝나야 한다(KevJudge 시험은 별도 표시·선택 실행).
3. 변경 묶음 = 코드 변경 + 영향 시험 + E2E 1회 + 영수증. 영수증(`receipts/<날짜>-<묶음>.json`)에는 커밋 대상 파일 해시, 실행 명령, 시작·종료 시각, 결과, 실패 수를 남긴다. 이미 통과한 묶음은 새 문제 없이 재실행하지 않는다(NO_RERUN).
4. 실행자 완료 ≠ 검증 PASS ≠ Owner 수용. main에 들어가는 묶음은 구현과 다른 세션(가능하면 다른 실행기)이 읽기 전용으로 검증(iva)하고, 결과는 `reviews/`에 남긴다. **[결정: E3]**
5. 실측 범위를 넘는 주장을 하지 않는다. 보고에는 [실측]/[문서]/[미확인]을 붙인다.

## 6. Git

1. 커밋·푸시는 Owner 지시 때만. 자동 커밋 없음. [D15]
2. 커밋 하나 = 변경 묶음 하나. 메시지: 첫 줄 영어 명령형 요약, 본문에 무엇을·왜, 끝에 `Co-Authored-By` 한 줄.
3. 같은 파일을 두 세션이 동시에 고치지 않는다. 작업대·모듈별 작성 세션은 1개. [E 동시 작성자]
4. 큰 파일(1 MB 초과), 실행 환경, 캐시, 백업은 커밋하지 않는다(.gitignore).

## 7. Owner 결정 필요

| # | 항목 | 권고 |
| --- | --- | --- |
| C1 | 실행 인터프리터 | 이 PC `python` 3.13, 표준 라이브러리만 |
| C2 | 시험 프레임워크 | 표준 `unittest`(pytest 설치 안 함) |
| C3 | 코드 검증(iva) 필수 범위 | main 반영 묶음 전부, Codex 세션이 읽기 전용 검증 |
| C4 | 영수증 보관 | `memory-engine/receipts/`에 커밋 |
| C5 | 문서·주석 언어 | 코드·식별자 영어, docstring·문서 한국어 허용 |
