# projects — 프로젝트 모음

aaaNew에서 진행하는 모든 프로젝트는 이 폴더 아래 같은 구조를 따른다(Owner 결정, 2026-10-17).

```text
aaaNew/
├─ apps/                    aaa core 실행부
└─ projects/
   └─ <project>/            예: bootstrap
      ├─ rsch/              조사 작업대
      │  └─ ref-apps/       외부 참조 앱(설치·조사 자료)
      ├─ pln/               계획 작업대
      └─ <component>/       구현 작업대 (예: memory-engine, memory-store)
```

| 프로젝트 | 내용 |
| --- | --- |
| [bootstrap](bootstrap/) | 도메인(aaa)을 처음 만드는 프로젝트. 역할·작업대·기억 전달·관계 엔진 연구와 설계 |

역할·작업대 구성은 [역할·워크플로 설계](bootstrap/rsch/design/ROLE_WORKFLOW_DESIGN_CLAUDE.md)를 따른다(Owner 결정 E1–E9 대기).
