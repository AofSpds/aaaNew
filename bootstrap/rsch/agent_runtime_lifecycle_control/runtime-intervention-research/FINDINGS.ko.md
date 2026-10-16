# 호출 이후 런타임 개입점: 어떻게 확보할 것인가

- 작성: 2026-10-17, aaa_new_rsch (Claude 세션 `e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b`)
- 요청: 사용자 "호출이 된 이후 런타임에서 우리의 개입점을 어떻게 확보하면 좋을지 보고"
- 범위: 세션이 시작된 뒤(첫 모델 호출 이후) 도메인이 관찰·개입·차단·주입할 수 있는 접점. 시작 전 접점은 [claude-entry-research](../claude-entry-research/FINDINGS.ko.md)·[codex-entry-research](../codex-entry-research/FINDINGS.ko.md)가 다룬다.
- 대상 실행기: Claude Code, Codex, Pi, Hermes, OpenCode. 각각 설치본과 공식 문서를 근거로 했고, Claude Code는 실측했다.

**결론: 다섯 실행기 모두 "도구 호출 직전"에 프로그램이 끼어들어 막거나 바꿀 수 있는 접점을 제공한다. 이것이 실행 중 통제의 공통 기반이다. 반면 "모델 호출 자체를 멈추기"는 실행기마다 다르고, Claude Code·Codex는 훅으로 모델 호출을 막을 수 없다(프롬프트 제출 단계에서만 가능). 따라서 개입점은 (1) 도구 호출 전후 훅으로 관문을 세우고, (2) 턴 경계(프롬프트 제출·턴 종료·압축)에서 기억을 다시 넣고, (3) 도메인이 실행기를 소유한 경우 이벤트 스트림과 steer/interrupt로 실시간 개입하는 세 겹으로 확보하는 것을 권한다.**

## 0. 증거 수준

| 실행기 | 버전 | 근거 |
| --- | --- | --- |
| Claude Code | CLI 2.1.268 (실측), 데스크톱 내장 2.1.295 | 공식 문서 + 이번 실측 (`repro/mid.py`) |
| Codex | CLI 0.157.1 | 설치본이 생성한 App Server 프로토콜 타입(`codex-entry-research/protocol-0.157.1/v2`) + 공식 문서 |
| Pi | `@earendil-works/pi-coding-agent` 1.2.0 (pi-web 내장) | 설치본 `docs/extensions.md`, `docs/rpc-commands.md`, `dist/core/extensions/types.d.ts` |
| Hermes | 0.21.7+500 (`8f81791`) | 설치본 소스 `agent/shell_hooks.py`, `agent/turn_context.py`, `hermes_cli/lifecycle.py` 호출부 |
| OpenCode | 1.19.0 | 공식 문서(별도 조사 결과 반영 예정). 로컬에는 바이너리만 있어 코드 대조 불가 |

[실측] = 실행해 확인. [코드] = 설치본 소스·생성 타입에서 확인. [문서] = 공식 문서. [미확인] = 확인 못 함.

## 1. 실행 중 개입점의 공통 지도

```text
프롬프트 제출 ─┬─ (가) 제출 훅: 차단 / 문맥 추가
               ▼
         모델 호출 ──── (나) 모델 호출 전후: 요청·응답 변형 (Pi·Hermes만)
               ▼
   도구 호출 요청 ─┬─ (다) 도구 전 훅: 차단 / 입력 수정 / 승인 요청 가로채기
                   ▼
         도구 실행 → (라) 도구 후 훅: 문맥 추가 / 결과 수정
               ▼
    턴 종료(Stop) ─┬─ (마) 종료 훅: 계속하게 하기(block) / 후속 요청
                   ▼
   압축·재개·종료 ── (바) 압축 전후·세션 종료 훅: 기억 재주입 / 정리
 ───────────────────────────────────────────────
 외부에서 항상: (사) 이벤트 스트림 관찰, (아) steer / 큐 / interrupt / fork
```

(가)~(바)는 실행기 **안**에서 설정 파일이나 확장으로 거는 훅이다. (사)(아)는 도메인이 실행기를 **자식 프로세스나 서버로 소유**할 때만 가능하다. 사용자가 앱에서 직접 연 세션에는 (가)~(바)만 닿는다.

## 2. 실행기별 접점

### 2.1 Claude Code [실측 2.1.268]

이번에 `--settings`로 훅 네 개를 걸고 한 세션에서 확인했다.

| 접점 | 결과 | 모델 입력에 남는 형태 |
| --- | --- | --- |
| UserPromptSubmit → `additionalContext` | 첫 턴에 포함됨 | `hook_additional_context` (system-reminder) |
| PreToolUse → `permissionDecision: deny` | `Read secret.txt` **차단됨**. 결과 JSON `permission_denials`에 기록 | 모델은 거부 사유를 보고 다음 행동 |
| PostToolUse → `additionalContext` | 도구 결과 뒤에 포함됨 | `hook_additional_context` |
| Stop → `decision: block` + reason | 모델이 멈추지 않고 **reason을 수행**한 뒤 종료(`DONE-OMICRON`) | `hook_blocking_error` + `stop_hook_summary`. 두 번째 Stop은 `stop_hook_active: true`로 와서 무한 반복 방지 |

[문서] 그 밖의 이벤트: PermissionRequest(승인 요청 가로채기), PostToolUseFailure, SubagentStart/Stop, PreCompact/PostCompact, SessionStart(source=compact), InstructionsLoaded(지침이 실제 로딩된 사실 관측), CwdChanged, FileChanged, SessionEnd 등 33종. 훅 설정은 cwd의 `.claude/settings.json` 또는 `--settings`(실행기 소유 시)로 건다. 상위 폴더 `.claude`는 적용되지 않는다(이전 조사 실측).

경계:
- 모델 호출 자체를 막는 훅은 없다. 첫 호출 차단은 UserPromptSubmit exit 2뿐(이전 조사 실측, `num_turns: 0`).
- 도메인이 `-p`/SDK로 실행하면 stream-json 이벤트 스트림으로 모든 도구 호출·메시지를 관찰할 수 있다 [문서]. 데스크톱 앱 세션은 앱이 소유하므로 도메인은 훅만 쓸 수 있다.
- 훅 출력 10,000자 제한.

### 2.2 Codex [코드 0.157.1 + 문서]

훅 이벤트(`HookEventName.ts`): `preToolUse, permissionRequest, postToolUse, preCompact, postCompact, sessionStart, sessionEnd, userPromptSubmit, subagentStart, subagentStop, stop, interrupt`. 핸들러 종류: command(sync/async, `additionalContextLimit` 기본 2,500 토큰 spill), mcp_tool, prompt, agent. 훅 출력 항목 종류(`HookOutputEntryKind`): `warning | stop | feedback | context | error`.

[문서] 차단 의미(https://learn.chatgpt.com/docs/hooks): `PreToolUse` → `permissionDecision: "deny"` 또는 exit 2로 차단, `"allow"` + `updatedInput`으로 입력 수정. `PermissionRequest` → `decision.behavior: "deny"`(하나라도 deny면 deny). `UserPromptSubmit` → `decision: "block"`. `PostToolUse` → `decision: "block"`은 결과를 대체하지만 실행을 되돌리지는 않음. `Stop`/`SubagentStop` → `decision: "block"` + reason이 계속 프롬프트를 만든다. `Interrupt`는 막을 수 없음. `additionalContext`는 SessionStart·SubagentStart·PreToolUse·PostToolUse·UserPromptSubmit에서 가능. `async: true` 훅은 차단·승인·수정 불가. 훅은 `/hooks`로 신뢰해야 실행된다. 설정 위치: `~/.codex/hooks.json`, `<repo>/.codex/hooks.json`, `config.toml [hooks]`. Claude Code와 이벤트·출력 형식이 거의 같다.

App Server(도메인이 소유할 때)의 실행 중 접점:

| 메서드/알림 | 기능 |
| --- | --- |
| `turn/steer` (`TurnSteerParams`, `expectedTurnId` 필수) | 진행 중인 턴에 입력과 `additionalContext` 주입 |
| `turn/interrupt` | 턴 중단 |
| `thread/queue/add·list·reorder·delete·start` | 다음 턴 입력 큐 |
| `thread/injectItems` | Responses API 항목을 모델 가시 이력에 직접 추가 |
| `turn/start.cwd`, `runtimeWorkspaceRoots`, `additionalContext` | 턴마다 작업대·문맥 지정 |
| `thread/fork`, `thread/compact/start`, `thread/revert` | 분기·압축·되돌리기 |
| `item/started·completed`, `agentMessage/delta`, `commandExecution/outputDelta`, `hook/started·completed`, `turn/completed`, `thread/statusChanged` | 관찰용 알림 |
| `commandExecution/requestApproval`, `fileChange/requestApproval`, `permissions/requestApproval` | **승인 요청이 클라이언트로 옴** → 도메인이 정책으로 허용/거부 |

주의: 실험적 타입으로 생성했으므로 "타입 존재"와 "호스트 지원"은 다르다. Codex 실측은 Codex rsch 세션이 맡는 편이 맞다(이 세션은 Codex 파일을 건드리지 않는다).

### 2.3 Pi [코드 1.2.0]

확장(`pi.on()`) 이벤트가 가장 촘촘하다. `types.d.ts`에서 확인한 이름:

| 단계 | 이벤트 | 할 수 있는 것 |
| --- | --- | --- |
| 시작 | `startup`, `session_start`, `resources_discover` | 리소스·지침 파일 교체(`agentsFilesOverride`, `noContextFiles`) |
| 턴 | `before_agent_start`(프롬프트·systemPromptOptions 수정, 메시지 추가), `agent_start`, `turn_start`, `turn_end`(엔트리 추가 + `continue: true`로 한 번 더), `agent_before_settle`(마지막 개입), `agent_end`, `agent_settled`(알림만) | 턴 경계에서 문맥 편집·계속 |
| 모델 | `before_provider_request`(**요청 페이로드 교체**), `before_provider_headers`, `provider_stream_event`(읽기 전용), `after_provider_response`, `model_select` | 모델 호출 직전 전체 입력 통제 |
| 문맥 | `context`, `context_with_system`, `context_edit`, `compaction`, `session_before_compact`(취소 가능) | 요청별 문맥 변형 |
| 도구 | `tool_call`(**입력 수정 또는 `block: true`**), `tool_execution_start/update/end`, `tool_result`(결과 수정, 핸들러 체인) | 차단·수정 |
| 입력 | `input`, `user_bash`(처리하면 로컬 실행 안 함), `custom_message` | 사용자 입력 가로채기 |
| 세션 | `session_before_switch/fork/tree`(취소 가능), `session_shutdown`, `ui_prompt_start/end` | |

RPC(도메인이 소유할 때): `prompt`, `steer`(현재 어시스턴트 턴의 도구 호출 뒤·다음 LLM 호출 전 전달), `follow_up`, `abort`, `clear_queue`, `compact`, `fork`, `switch_session`, `get_state`, `get_messages`. 이벤트는 `message_update`, `agent_settled` 등 레코드 스트림.

Pi는 **모델 호출 직전 입력 전체**(`before_provider_request`)를 바꿀 수 있는 유일한 후보다. 다른 넷은 "문맥 추가"까지다.

### 2.4 Hermes [코드 0.21.7]

두 계층이 있다.
- **셸 훅**(`agent/shell_hooks.py`): 이벤트 `pre_tool_call`, `post_tool_call`, `pre_verify`. 응답 `{"decision"|"action": "block"|"modify"}` 또는 `{"context": …}`. **exit 2는 `pre_tool_call`을 차단**(Claude Code/Cursor 호환이라고 주석에 명시). 차단이 적용되는 이벤트는 `pre_tool_call`뿐(`_BLOCKING_EVENTS`). 기본 fail-open, `fail_closed` 옵션은 차단 가능 이벤트에만.
- **플러그인 훅**(Python): `pre_llm_call`(반환한 `context`가 **사용자 메시지에 주입**, 시스템 프롬프트에는 안 들어감, 초과분 spill), `post_llm_call`, `pre_tool_call`, `post_tool_call`, `on_session_start/end/reset/finalize`, `on_stream_start/delta/end`, `on_human_input_request/resolved`, `on_interim_message`, `after_memory` 등.

`pre_llm_call` 페이로드에는 `user_message`, `conversation_history`, `is_first_turn`, `model`, `session_id`가 온다. 매 모델 호출 전에 도메인 문맥을 넣는 접점으로 쓸 수 있다. [문서] `pre_llm_call`은 차단 불가, `pre_tool_call` 시간 초과는 fail-closed, 승인 훅(`pre_approval_request/post_approval_response`)은 관찰 전용, `pre_verify`는 턴을 한 번 더 강제할 수 있다. 게이트웨이 훅(`~/.hermes/hooks/`, `agent:start/step/end`, `session:*`)은 모두 관찰 전용. 외부 프로세스용 steer/abort HTTP API는 "공개하지 않는다"고 문서에 명시 — Hermes는 소유해도 겹 2가 약하다.

### 2.5 OpenCode [문서 + 공개 타입 `@opencode-ai/plugin`]

로컬에는 바이너리만 있어 코드 대조를 못 했다. 공식 문서(https://opencode.ai/docs/plugins/, /docs/server/)와 공개 플러그인 타입 기준.

| 접점 | 기능 |
| --- | --- |
| `tool.execute.before` | `output.args` 수정. **차단은 예외를 던져서**(문서 예: ".env 읽기 금지") |
| `tool.execute.after` | `title, output, metadata` 수정 |
| `permission.ask` | `status: "ask" \| "deny" \| "allow"` |
| `chat.message`, `chat.params`, `chat.headers` | 새 메시지 수신, LLM 파라미터·헤더 수정 |
| `experimental.chat.messages.transform`, `experimental.chat.system.transform` | **모델에 보내는 메시지·시스템 프롬프트 배열 변형** (Pi의 `context`/`before_provider_request`에 해당하나 experimental) |
| `experimental.session.compacting`, `experimental.compaction.autocontinue` | 압축 문맥 추가·프롬프트 교체 |
| `tool.definition`, `event`, `config`, `dispose` | 도구 정의 수정, 버스 이벤트 관찰 |
| HTTP `POST /session/:id/message`, `prompt_async`, `abort`, `fork`, `revert`, `permissions/:id` | 소유 시 제어. `prompt({noReply: true})`로 "응답 없이 문맥 추가" |
| `GET /event` SSE | `session.*`, `message.part.updated`, `permission.asked/replied`, `tool.execute.before/after`, `file.edited` 관찰 |

진행 중인 턴에 steer를 넣는 API는 문서에 없다(prompt_async/abort만). 훅의 동기/비동기 의미도 문서에 없다.

## 3. 비교표 (실행 중)

| 능력 | Claude Code | Codex | Pi | Hermes | OpenCode |
| --- | --- | --- | --- | --- | --- |
| 도구 호출 차단 | **실측** PreToolUse deny | 문서: PreToolUse deny / exit 2, PermissionRequest deny | 코드: `tool_call.block` | 코드: `pre_tool_call` exit 2 / block | 문서: `tool.execute.before`에서 throw, `permission.ask` deny |
| 도구 입력 수정 | 문서(updatedInput) | 문서(updatedInput) | 코드 | 코드(`modify`) | 문서(`output.args`) |
| 매 모델 호출 전 문맥 추가 | 실측 UserPromptSubmit·PostToolUse(턴 단위) | 문서: Pre/PostToolUse·UserPromptSubmit `additionalContext`, `thread/injectItems` | 코드: `before_agent_start`, `context`, `before_provider_request` | 코드: `pre_llm_call.context` | 문서: `experimental.chat.messages.transform`, `prompt({noReply})` |
| 모델 요청 전체 교체 | 없음 | 없음 | **있음** | 없음 | experimental(`chat.messages/system.transform`) |
| 턴 종료 시 계속시키기 | **실측** Stop block | 문서: Stop block → 계속 프롬프트 | 코드: `turn_end`/`agent_before_settle` continue | 문서: `pre_verify` | 문서: `experimental.compaction.autocontinue`만 |
| 승인 요청 가로채기 | 문서 PermissionRequest | 문서: PermissionRequest 훅 + App Server `requestApproval` | 코드 (`tool_call`로 대체) | 문서: 관찰 전용 | 문서: `permission.ask`, HTTP permissions 응답 |
| 모델 호출 자체 차단 | **없음**(프롬프트 제출 단계만) | 없음(UserPromptSubmit block만) | `before_agent_start`/`before_provider_request`에서 가능할 것으로 보임, 미실측 | 문서: `pre_llm_call` 차단 불가 | 문서에 없음 |
| 외부에서 실시간 관찰 | stream-json(소유 시) | App Server 알림(소유 시) | RPC 레코드(소유 시) | 문서: 외부 스트림 없음(in-process만) | SSE `/event`(소유 시) |
| 실행 중 steer/interrupt | 없음(큐만) | `turn/steer`, `turn/interrupt` | `steer`, `abort` | 사용자 `/steer`만, 외부 API 없음 | `abort`만, steer 없음 |
| 압축 후 재주입 | 실측 SessionStart(compact) | 문서: PostCompact, SessionStart(source=compact) | 코드: `session_compact`, `compaction` | 미확인 | 문서: `experimental.session.compacting` |

## 4. 개입점을 "확보"하는 방법 — 제안

실행기 선택과 무관하게 도메인이 가져야 할 것을 세 겹으로 나눈다. 제안이며 채택 확정이 아니다.

### 겹 1. 실행기 안의 관문 (모든 진입 방식에 닿음)

1. **도구 전 관문 하나를 표준화한다.** 입력은 공통 형식(`session_id, tool_name, tool_input, cwd, role`)으로 받고, 출력은 허용/거부/수정과 사유로 통일한다. 실행기별 어댑터가 Claude `PreToolUse` JSON, Codex `preToolUse`, Pi `tool_call`, Hermes `pre_tool_call`로 변환한다. Hermes가 이미 Claude Code 형식(exit 2)을 수용하므로 Claude 형식을 기준으로 삼으면 어댑터 비용이 준다.
2. **턴 경계에서 기억을 다시 넣는다.** 프롬프트 제출 훅(Claude `UserPromptSubmit`, Codex `userPromptSubmit`, Pi `before_agent_start`, Hermes `pre_llm_call`)에 "현재 업무 포인터 + 바뀐 기억의 버전"만 짧게 넣는다. 전체 기억은 CLAUDE.md/AGENTS.md와 시작 훅이 맡고, 턴 훅은 차이만 전달한다. 이유: 재개 시 훅 블록이 계속 쌓이는 것을 실측했다.
3. **압축 후 재주입을 필수로 둔다.** Claude `SessionStart(compact)`, Codex `postCompact`, Pi `session_compact`. 압축 전 훅 블록은 요약에 흡수되어 사라진다(실측).
4. **종료 훅으로 "인계 기록" 강제.** Claude `Stop` block은 모델에게 마지막 행동을 시킬 수 있다(실측). "작업대에 현재 상태·다음 단계 기록 후 종료"를 여기서 요구한다. 단 한 번만(`stop_hook_active` 확인).
5. **관문의 실패 정책을 명시한다.** 모든 실행기가 훅 실패를 조용히 넘길 수 있다(Claude SessionStart 실측, Hermes 기본 fail-open). 차단이 꼭 필요한 도구(파일 쓰기·외부 전송)는 fail-closed로, 나머지는 fail-open으로 나눈다.

### 겹 2. 도메인이 실행기를 소유할 때 (CLI/SDK/App Server/RPC)

6. **이벤트 스트림을 기록의 원본으로 삼는다.** Claude stream-json, Codex App Server 알림, Pi RPC 레코드를 도메인이 받아 "어떤 도구가 어떤 입력으로 실행됐고 훅이 무엇을 했는지"를 작업대에 남긴다. 실행기의 세션 파일에 의존하지 않는다.
7. **steer/interrupt를 정책 위반 대응에 쓴다.** 관문이 거부한 뒤에도 모델이 우회를 시도하면 Codex `turn/interrupt`, Pi `abort`로 멈추고, Codex `turn/steer`·Pi `steer`로 정정 지시를 넣는다. Claude Code는 이 수단이 없으므로 PreToolUse 거부 사유와 Stop block으로 대신한다.
8. **승인 요청을 도메인 정책으로 받는다.** Codex는 승인 요청이 클라이언트(=도메인)로 온다. Claude는 `PermissionRequest` 훅, Pi는 `tool_call`. 사용자에게 물을 것과 정책으로 자동 결정할 것을 여기서 가른다.

### 겹 3. 사용자가 앱에서 직접 연 세션

9. 겹 1만 닿는다. 작업대 폴더에 `.claude/settings.json`(Claude)·프로젝트 훅(Codex)을 두어 관문이 자동으로 걸리게 한다. 상위 폴더 설정은 적용되지 않으므로 **작업대마다** 둔다.
10. 잘못된 폴더에서 열렸는지는 시작 훅이 `cwd`로 판별해 첫 프롬프트 훅에서 경고를 넣는다. 차단은 못 한다(실측). 사용자 협조가 필요한 한계로 기록한다.

### 우선 검증할 것

- Codex 훅 실측(PreToolUse deny, Stop block, `/hooks` 신뢰 절차) — Codex rsch 세션 담당 권장.
- Pi `before_provider_request`로 모델 호출을 보류할 수 있는지, `tool_call.block` 실측.
- 공통 관문 형식 초안과 Claude·Codex·Hermes 세 실행기에서의 어댑터 동작. 셋 다 Claude Code 훅 형식(JSON stdin, exit 2 차단, `additionalContext`)을 쓰므로 **하나의 관문 스크립트로 세 실행기를 덮을 가능성**이 크다.

## 6. 문서 출처 (2026-10-17 열람)

- Codex: https://learn.chatgpt.com/docs/hooks , https://learn.chatgpt.com/docs/app-server
- Pi: https://github.com/earendil-works/pi/tree/main/packages/coding-agent/docs (extensions.md, rpc.md, rpc-commands.md, sdk.md)
- OpenCode: https://opencode.ai/docs/plugins/ , https://opencode.ai/docs/server/ , https://opencode.ai/docs/sdk/ , `@opencode-ai/plugin` 타입
- Hermes: https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks , .../features/plugins , .../developer-guide/observer-hooks
- Claude Code: https://code.claude.com/docs/en/hooks , https://code.claude.com/docs/en/hooks-guide

## 5. 근거 파일

- 실측: `repro/mid.py`(PreToolUse/PostToolUse/UserPromptSubmit/Stop), `repro/run.sh`, `repro/tx.py`. 세션 `0bcbada5-1f53-48ad-9eb6-92cd02d93dd0`의 기록에서 `hook_additional_context`, `permission_denials`, `hook_blocking_error`, `stop_hook_summary` 확인.
- Codex 타입: `../codex-entry-research/protocol-0.157.1/v2/{HookEventName, ConfiguredHookHandler, HookOutputEntryKind, TurnSteerParams, TurnInterruptParams, ThreadInjectItemsParams, ThreadQueueAddParams, TurnStartParams}.ts`
- Pi: `rsch/pi/pi-web/node_modules/@earendil-works/pi-coding-agent/{docs/extensions.md, docs/rpc-commands.md, dist/core/extensions/types.d.ts}`
- Hermes: `rsch/hermes/hermes-agent/{agent/shell_hooks.py, agent/turn_context.py:795-840, hermes_cli/hooks.py}`
- Claude Code 문서: https://code.claude.com/docs/en/hooks , https://code.claude.com/docs/en/hooks-guide
