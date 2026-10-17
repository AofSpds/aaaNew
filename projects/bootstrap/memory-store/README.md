# memory-store — 관계 엔진 기록 저장소

- 내용: 추가 전용 기록(jsonl). source_rev / memory_rev / relation / selection / bundle / judgment / change.
- 근거: [결정 D1–D21](../rsch/research/relation-engine/DECISIONS_D1_D21_CLAUDE.md) D1(형식)·D8(위치)·D15(쓰기 주체)·D16(보존)·D20(민감 정보).
- 규칙(권고안): 기록은 엔진 CLI로만 추가, 직접 편집 금지. `index.sqlite`와 `records/local/`은 Git 제외(.gitignore).
- 상태: 폴더만 생성(2026-10-17). 기록 없음.
