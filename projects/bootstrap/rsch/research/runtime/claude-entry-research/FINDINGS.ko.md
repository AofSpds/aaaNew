# Claude Code 진입 조사: 기억 주입과 작업대 도달 접점

- 작성: 2026-10-14, aaa_new_rsch (Claude Code 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 요청: Codex rsch 세션 `01a13598-96f6-7d21-9ec8-61173316981e`의 인계(사용자 지시). Codex 쪽 조사는 Codex가 맡는다.
- 범위: 세션이 시작될 때 도메인이 필요한 기억을 **실제 모델 입력**에 넣고, 에이전트를 **역할별 작업대**에 도달시킬 수 있는 Claude Code의 접점.
- 방법: 공식 문서 대조 + 일회용 폴더에서 소규모 실측. 전역 설정 변경·설치는 하지 않았다. Codex 파일은 수정하지 않았다.

**결론: Claude Code에서는 "작업대 폴더를 cwd로 시작"하는 것이 작업대 도달의 핵심 접점이다. 기억은 cwd와 상위 폴더의 CLAUDE.md, 그리고 cwd의 `.claude/settings.json`이나 실행 시 `--settings`로 건 SessionStart 훅으로 넣을 수 있다. 다만 SessionStart 훅은 실패해도 첫 작업을 막지 못한다. 기억 전달에 실패했을 때 멈추게 하려면 UserPromptSubmit 게이트나 실행기(launcher)의 사전 점검이 따로 필요하다.**

## 0. 확인한 버전과 증거 수준

| 대상 | 버전 | 비고 |
| --- | --- | --- |
| 독립 CLI (`claude` on PATH, winget) | 2.1.268 | 대부분의 실측 |
| 데스크톱 앱 내장 실행기 | 2.1.295 (`%APPDATA%\Claude\claude-code\2.1.295\…\claude.exe`) | 핵심 실측(시작 로딩, 실패 처리, 상위 폴더 훅) 반복 |
| 데스크톱 앱 | 2.37337.1 | 프로세스 명령줄 관측 |
| 공식 문서 | code.claude.com/docs (2026-10-14 열람, v2.1.296까지 언급) | 아래 링크 |

증거 표기:

- **[실측]**: 이번에 실행해서 확인한 것
- **[문서]**: 공식 문서에 적힌 것
- **[관측]**: 실행 중인 프로세스나 파일을 본 것
- **[미확인]**: 확인하지 못한 것

실측 모델은 비용을 줄이려고 `haiku`를 썼다. 준수 여부 실측은 표본이 작아서 경향을 보여 줄 뿐, 보장의 근거는 아니다.

## 1. 시작 순서와 도메인이 개입할 수 있는 지점

```text
프로세스 시작(cwd 결정)
 → 설정 소스 결정(--setting-sources, --settings)
 → 지침 로딩(cwd·상위 CLAUDE.md, @import 확장, rules)
 → SessionStart 훅 실행(source=startup|resume|clear|compact)
 → 첫 사용자 프롬프트 → UserPromptSubmit 훅 → 첫 모델 호출
 → 하위 폴더 파일 접근 시 그 폴더 CLAUDE.md 지연 로딩
```

| 접점 | 도메인이 할 수 있는 것 | 막을 수 있나 | 근거 |
| --- | --- | --- | --- |
| cwd | 작업대 폴더에서 프로세스를 시작한다 | 해당 없음 | [문서] CLI에는 cwd 플래그가 없고 프로세스 cwd를 쓴다. SDK는 `cwd` 옵션 |
| `--settings <file\|json>` | 실행마다 훅을 주입한다. 파일 수정이 필요 없다 | — | [실측] `--settings`의 훅과 프로젝트 훅이 **둘 다** 실행됨 |
| `--setting-sources` | 사용자·프로젝트·로컬 설정 사용 여부를 고른다 | — | [실측] 아래 §3 |
| CLAUDE.md / @import | 공통·역할 기억을 둔다 | — | [실측] 시작 시 모델 입력에 포함됨 |
| SessionStart 훅 | 동적 기억(현재 업무, 경험 view 요약)을 넣는다 | **아니오** | [실측]+[문서] §4 |
| UserPromptSubmit 훅 | 첫 프롬프트 전에 조건을 확인한다 | **예** (exit 2) | [실측] §4 |
| `--append-system-prompt` | 시스템 프롬프트에 추가한다 | — | [문서] 대화별로 고정되어, 재개해도 바뀌지 않고 압축 후에야 반영 |

## 2. 기억은 실제 모델 입력에 어떻게 들어가는가 [실측 2.1.268·2.1.295]

실험 구성은 다음과 같다. `exp1/CLAUDE.md`(MARKER_CLAUDEMD)가 `@imported.md`(MARKER_IMPORT)를 import한다. `exp1/sub/CLAUDE.md`(MARKER_SUB)를 하위 폴더에 두었다. `exp1/.claude/settings.json`에는 SessionStart 훅이 있고, additionalContext로 MARKER_HOOK을 내보낸다. 이 상태에서 모델에게 컨텍스트 안의 MARKER_ 줄을 모두 그대로 나열하게 했고, 세션 기록(`~/.claude/projects/<proj>/<sid>.jsonl`)도 대조했다.

| 기억 | 시작 시 입력에 포함 | 기록에 남는 형태 |
| --- | --- | --- |
| cwd의 CLAUDE.md | 예 | `attachment: instructions` (type Project) |
| `@imported.md` | 예. 로더가 확장한다 | 같은 `instructions` 안의 별도 파일 |
| 상위 폴더 CLAUDE.md | 예 | `instructions` |
| 하위 폴더 `sub/CLAUDE.md` | **아니오**. `sub/` 파일을 Read한 뒤에 포함됨 | `attachment: nested_memory` |
| SessionStart additionalContext | 예 | `hook_additional_context`, 렌더링은 `<system-reminder>SessionStart hook additional context: …` |
| SessionStart 일반 stdout(JSON 아님) | 예 | `SessionStart:startup hook success: …` 형태로 전달 |
| `--add-dir`로 추가한 폴더의 CLAUDE.md | **아니오** | 환경 변수 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`이면 포함됨 [실측] |

- [문서] CLAUDE.md와 훅 컨텍스트는 시스템 프롬프트가 아니라 **대화 안**(사용자 메시지 위치의 system-reminder)으로 들어간다. 훅 출력은 10,000자로 제한된다. 넘으면 파일로 저장하고 2,000자 미리보기만 넣으며, 모델에게 그 파일을 읽으라고 시키지는 않는다.
- [문서] `@import`의 상대 경로는 import를 적은 파일 기준으로 해석한다. 최대 4단계까지 import한다. 프로젝트 import가 작업 폴더 밖을 가리키면 처음 한 번 승인 창이 뜬다.
- [문서] `.claude/rules/*.md` 중 paths가 없는 규칙은 시작 시 로딩한다. paths가 있으면 일치하는 파일을 다룰 때 로딩한다.
- [문서] AGENTS.md는 2.1.277 이상에서, CLAUDE.md 계열이 없을 때만 읽는다. 2.1.268 CLI는 이 기능 이전 버전이다.

## 3. 설정 소스와 작업대 위치의 영향 [실측]

| 조건 | 프로젝트 CLAUDE.md | 프로젝트 훅 |
| --- | --- | --- |
| `--setting-sources project` | 포함 | 실행 |
| `--setting-sources user` (project 제외) | **미포함** | 미실행 |
| `--setting-sources ""` | **미포함** (2.1.268·2.1.295) | 미실행 |
| cwd = `exp5/rsch`, `exp5/CLAUDE.md` + `exp5/.claude/settings.json` 훅 | 상위·현재 CLAUDE.md **둘 다 포함** | 상위 `.claude` 훅은 **미실행** (git 저장소 여부와 무관, 2.1.268·2.1.295) |

이 결과에서 작업대 설계에 대해 나오는 점은 다음과 같다.

- **CLAUDE.md는 상위 폴더까지 올라가며 읽고, 훅 설정은 cwd의 `.claude/`만 읽는다.** [문서] SDK 문서도 "프로젝트 설정·훅은 `<cwd>/.claude/`에서만, 상위로 거슬러 올라가지 않음"이라고 적었다. 따라서 `projects/bootstrap/.claude/settings.json`에 훅을 두고 `projects/bootstrap/rsch`에서 시작하면 그 훅은 실행되지 않는다. 훅이 필요하면 각 작업대에 `.claude/settings.json`을 두거나, 실행기가 `--settings`로 넘겨야 한다.
- **저장소 루트에서 시작하면 작업대의 CLAUDE.md는 시작 시 들어가지 않는다.** 하위 폴더 지연 로딩이라, 그 폴더 파일을 읽어야 들어온다. 역할 기억을 시작부터 보장하려면 cwd를 작업대로 두는 편이 맞다.
- 실행기가 `--setting-sources`를 좁히면 프로젝트 CLAUDE.md까지 빠진다. 설정을 격리하려다 기억까지 잃을 수 있다.

## 4. 실패 시 첫 작업을 멈출 수 있는가

| SessionStart 훅 결과 | 첫 모델 호출 | 2.1.268 | 2.1.295 |
| --- | --- | --- | --- |
| exit 2 (stderr) | **진행됨**, 훅 내용은 입력에 없음 | 실측 | 실측 |
| exit 1 | **진행됨** | 실측 | — |
| `{"continue": false, "stopReason": …}` | **진행됨**. 기록에는 hook_success로 남고 stopReason은 무시됨 | 실측 | 실측 |

- [문서] SessionStart는 "Context only, no blocking"이다. 첫 응답은 훅이 끝날 때까지 **기다리기만** 한다(지연이지 차단이 아님). 명령형 훅의 기본 시간 제한은 600초다.
- **UserPromptSubmit exit 2는 첫 프롬프트를 차단한다** [실측 2.1.268]. 모델 호출 0회(`num_turns: 0`), 비용 0이었다. 결과 텍스트는 "UserPromptSubmit operation blocked by hook: … Original prompt: …"였다.
  - 주의: 이 경우에도 프로세스 종료 코드는 0이고 `is_error: false`, `subtype: success`다. **실행기는 `num_turns == 0`이나 결과 문구로 차단 여부를 판별해야 한다.**
  - [문서] UserPromptSubmit에는 matcher가 없어 모든 프롬프트에서 실행된다. "첫 프롬프트만" 같은 조건은 스크립트가 직접 관리해야 한다. 차단된 프롬프트 원문은 기록에 남는다.
- 실패 시 멈추는 구성의 후보(제안이며 채택 확정 아님):
  1. **실행기 사전 점검**: 도메인 실행기가 기억과 작업대를 준비하고 확인한 뒤에만 `claude`를 시작한다. 가장 단순하다.
  2. **SessionStart 성공 표식 + UserPromptSubmit 게이트**: SessionStart가 기억을 넣는 데 성공하면 세션별 표식을 남긴다. UserPromptSubmit은 표식이 없으면 exit 2로 막는다. 실측은 표식 파일 유무로만 했다.

## 5. 재개·압축 시 갱신 경계 [실측 2.1.268]

| 사건 | SessionStart | 이전 훅 블록 | CLAUDE.md |
| --- | --- | --- | --- |
| `--resume` | `source=resume`로 다시 실행. 입력에 `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired` 등이 추가됨 | **남는다**. startup과 resume 블록이 함께 보임 | 내용이 그대로면 다시 넣지 않음. **디스크에서 바뀌었으면 새 내용이 다시 첨부됨** |
| `/compact` | `source=compact`로 실행 | 압축 전 블록은 요약에 흡수되어 사라짐. compact 블록부터 다시 쌓임 | 내용 변경이 없어도 **디스크에서 다시 넣음** |

- [문서] 압축 뒤에는 프로젝트 루트 CLAUDE.md와 범위 없는 rules를 디스크에서 다시 넣는다. 하위 폴더 CLAUDE.md와 paths 규칙은 필요할 때 다시 로딩한다. 대화에서만 준 지시는 사라진다.
- [문서] `--append-system-prompt` 등 시스템 프롬프트는 대화 시작 때 기록된 것을 재개 후에도 그대로 쓴다. 바꾼 플래그는 압축하거나 새 대화를 시작해야 반영된다. **갱신이 필요한 기억은 시스템 프롬프트보다 CLAUDE.md나 SessionStart로 넣는 편이 맞다.**
- 재개할 때 블록이 계속 쌓이므로, SessionStart 출력은 짧은 "현재 상태와 포인터" 형태가 적절하다(제안).

## 6. 사용자가 앱에서 직접 시작할 때와 도메인이 실행할 때

| 구분 | 사용자 앱 직접 시작 (데스크톱 Code 탭) | 도메인 실행 (CLI `-p` / Agent SDK) |
| --- | --- | --- |
| cwd(작업대) | 사용자가 고른 폴더. worktree도 선택 가능 | 실행기가 지정 |
| 실행 형태 [관측] | 앱이 내장 `claude.exe`를 `--resume=<세션ID> --setting-sources=user,project,local --add-dir=… --settings "<JSON>"` 등으로 실행 | 실행기가 플래그와 환경 변수를 정함 |
| 도메인이 쓸 수 있는 접점 | 그 폴더에 있는 파일뿐(CLAUDE.md, `.claude/settings.json`, rules). 사용자 전역 설정은 이번 범위에서 제외 | `--settings` 훅, `--append-system-prompt`, `--setting-sources`, 환경 변수, 사전 점검 |
| 작업대 지정 강제 | 사용자의 폴더 선택에 달림 | 가능 |

- [관측] 이 세션 자체도 데스크톱이 `--resume`으로 띄운 프로세스다. 데스크톱이 실행기를 다시 띄우면 SessionStart가 `source=resume`으로 다시 실행될 수 있다. 실제로 언제 다시 띄우는지(메시지마다인지, 앱 재시작 때만인지)는 **[미확인]**이다.
- [실측] **환경 변수 상속 주의**: Claude 데스크톱 세션 안에서 `claude`를 실행하면 `CLAUDE_CODE_ENTRYPOINT=claude-desktop` 등이 상속된다. 그러면 자식 세션이 데스크톱 세션처럼 동작했다(사용자 이메일 컨텍스트, `scratchpad_dir` 훅 입력 등). 도메인 실행기는 `CLAUDE*`·`MCP_*` 환경 변수를 정리하고 실행해야 한다.
- [문서] SDK에서 `settingSources`를 생략하면 user, project, local을 모두 쓴다. 빈 배열이면 모두 끈다(이때 CLAUDE.md도 빠지는 것은 위 CLI 실측과 같은 방향). `systemPrompt`를 생략하면 claude_code 프리셋이 아닌 최소 기본값이 된다.
- [문서] SessionStart 훅으로 이미 시작한 세션의 cwd를 바꾸는 방법은 문서에 없다. Codex 쪽 결론과 같다.

## 7. 존재 / 입력 포함 / 실제 준수의 구분

| 단계 | 확인 방법 | 이번 결과 |
| --- | --- | --- |
| 기억 파일 존재 | 파일 시스템, 훅 실행 로그 | 실험 파일과 `hook_log.jsonl` |
| 모델 입력 포함 | 세션 기록의 `instructions`, `hook_additional_context`, `nested_memory`. [문서] `InstructionsLoaded` 훅(로딩 이유: session_start, nested_traversal, include, compact 등), `/context` | §2·§5 표 |
| 실제 준수 | 응답 행동 관측 | 표본만 확인. "모든 응답을 `[WB:역할]`로 시작하라"는 지시를 SessionStart 훅으로 준 경우 3/3, CLAUDE.md로 준 경우 3/3 준수(haiku, 단순 질문) |

준수 표본은 작고 과제도 단순하다. 길고 복잡한 작업에서 계속 지키는지는 **[미확인]**이다. "기억을 받았다"는 입력 증거와 "따랐다"는 행동 증거는 따로 남겨야 한다. 예를 들어 첫 응답에 역할·작업대·인수한 계획을 확인하는 줄을 쓰게 하고, 실행기나 Stop 훅이 이를 검사하는 방식이 있다(제안).

## 8. bootstrap 작업대 구상에 대한 함의 (제안, 미채택)

1. 작업대 폴더(`projects/bootstrap/rsch`, `projects/bootstrap/pln`, …)를 **cwd**로 시작한다.
2. `projects/bootstrap/CLAUDE.md`에 도메인 공통 진입 규칙을 둔다(상위 폴더라 시작 시 포함). `<작업대>/CLAUDE.md`에는 역할, 현재 업무 포인터, 경험 view `@import`를 둔다.
3. 동적인 현재 상태는 SessionStart(startup·resume·compact)로 짧게 넣는다. 훅 설정은 작업대마다 `.claude/settings.json`에 두거나 실행기의 `--settings`로 넘긴다(상위 `.claude`는 적용되지 않음).
4. 실패 시 멈추는 장치는 실행기 사전 점검이나 UserPromptSubmit 게이트로 따로 둔다.
5. 사용자가 앱에서 직접 연 세션은 폴더 선택이 맞을 때만 이 구조가 작동한다. 잘못된 폴더에서 열린 경우를 감지할 방법이 필요하다(**[미확인]**, Codex 쪽 결과와 함께 비교할 항목).

## 9. 확인하지 못한 것

- 데스크톱 앱이 실행기를 다시 띄우는 시점과 그때마다 SessionStart(resume)가 실행되는지
- 대화 도중(재개 없이) CLAUDE.md가 바뀌면 다음 턴에 다시 첨부되는지. 이번에는 재개 경계에서만 관측
- `onFailure: "block"`(2.1.295+)이 SessionStart에 적용되는지. 문서에 없고 실측하지 않음
- 신뢰하지 않은 폴더를 대화형으로 처음 열 때 프로젝트 훅이 신뢰 확인 창보다 먼저 실행되는지
- 자동 기억(MEMORY.md)이 압축 뒤 다시 들어가는지
- UserPromptSubmit 게이트의 2.1.295 실측, InstructionsLoaded 훅 실측

## 10. 근거

**공식 문서** (2026-10-14 열람)
- Hooks reference: https://code.claude.com/docs/en/hooks
- Hooks guide: https://code.claude.com/docs/en/hooks-guide
- Memory(CLAUDE.md, import, rules, AGENTS.md, auto memory): https://code.claude.com/docs/en/memory
- Context window(압축 후 남는 것): https://code.claude.com/docs/en/context-window
- CLI reference(`--settings`, `--setting-sources`, `--append-system-prompt`, `--add-dir`, `--bare`): https://code.claude.com/docs/en/cli-reference
- Settings(우선순위): https://code.claude.com/docs/en/settings
- Permissions(신뢰와 훅): https://code.claude.com/docs/en/permissions
- Agent SDK(cwd, settingSources): https://code.claude.com/docs/en/agent-sdk/claude-code-features
- Agent SDK(시스템 프롬프트): https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts
- Desktop: https://code.claude.com/docs/en/desktop

**실측 재현 자료**: [`repro/`](repro/)
- `ss.py`: SessionStart 훅(모드 ok, plain, exit1, exit2, stop)
- `ups.py`: UserPromptSubmit 게이트
- `comply.py`: 준수 표본용 훅
- `run.sh`: 환경 변수를 정리하고 실행. `XBIN`으로 실행 파일 선택
- `tx.py`: 세션 기록 요약

실험 폴더와 원시 결과는 Claude 세션의 임시 scratchpad에 있으므로 영구 보존을 전제하지 않는다. 실측 세션 기록은 `~/.claude/projects/C--Users-ms1pk-AppData-Local-Temp-claude-…-scratchpad-exp*/`에 남았다.
