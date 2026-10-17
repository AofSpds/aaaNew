# Codex 세션 진입: 도메인 기억 전달과 작업대 지정

확인일: 2026-10-14. 범위는 첫 업무 전에 필요한 기억과 작업대를 전달하는 접점이다. 설치 CLI는 codex-cli 0.157.1이며 데스크톱 내장 엔진과 동일하다고 확인한 것은 아니다. 이번에는 문서·도움말·설치 바이너리가 생성한 프로토콜을 확인했다. 실제 기억 주입 실험과 전역 설정 변경은 하지 않았다.

## 현재 결론

도메인이 Codex 실행을 시작할 수 있다면, 작업 디렉터리와 모델에 전달할 기억을 각각 지정하는 접점이 있다. 사용자가 기존 앱에서 직접 세션을 여는 경우에는 프로젝트 폴더와 SessionStart 훅을 연결하는 방안을 검증해야 한다. 훅 출력만으로 실행기의 작업 디렉터리가 변경된다고 볼 근거는 없다.

| 진입 방식 | 작업대 지정 | 기억 전달 | 확인 수준 |
|---|---|---|---|
| 도메인이 CLI 실행 | `codex --cd <작업대>` | `developer_instructions` 설정 또는 SessionStart | 설치 CLI 도움말 및 공식 문서 |
| 도메인이 App Server 사용 | `thread/start.cwd` | `thread/start.developerInstructions` 또는 SessionStart | 설치 버전 생성 타입 및 공식 문서 |
| 사용자가 Codex 앱에서 새 채팅 | 프로젝트의 primary 폴더 | 해당 실행환경에 로드되고 신뢰된 SessionStart | 문서상 접점. 현재 앱에서 실증 필요 |

App Server는 Codex 실행기를 제어하는 프로토콜이다. 이를 사용하는 것과 별도 모델 API 키를 구매하여 모델만 직접 호출하는 것은 다른 결정이다.

## 1. 도메인이 실행을 준비하는 경계

설치 CLI 도움말에서 `-C, --cd <DIR>`를 확인했다. App Server 생성 타입에는 `ThreadStartParams.cwd`와 `developerInstructions`가 있다. 따라서 도메인이 역할과 작업대를 선택하고 관련 경험 view를 짧은 문자열로 준비한 후, cwd와 기억 본문을 함께 전달하는 설계가 가능하다. `baseInstructions`를 대체해야만 기억을 추가할 수 있는 것은 아니다.

`ThreadStartResponse`에는 실제 `cwd`와 읽은 지침 파일 경로인 `instructionSources`가 있다. `TurnStartParams.cwd`로 이후 턴의 기본 작업 디렉터리를 바꾸는 접점도 있다. 단, 반환된 파일 경로만으로 기억 본문이 모델에 전달됐거나 준수됐음을 입증하지는 못한다. [App Server](https://learn.chatgpt.com/docs/app-server), [설정 참조](https://learn.chatgpt.com/docs/config-file/config-reference)

권장하는 첫 실험 순서는 도메인에서 기억 준비 → cwd 지정 → 세션 생성 결과 확인 → 첫 턴 시작이다. 도메인이 첫 턴 호출을 소유하면 기억 준비 실패 시 그 호출을 보류할 수 있다. 이는 자체 실행 호스트의 설계상 통제이며, 현재 앱에 이미 구현된 보장이 아니다.

## 2. SessionStart: 도메인을 호출할 수 있는 접점

공식 문서에서 SessionStart의 입력은 session_id, cwd와 시작 원인(startup/resume/clear/compact)을 포함한다. 일반 stdout 또는 `hookSpecificOutput.additionalContext`로 추가 developer context를 반환한다. 동기 command 훅은 기본적으로 완료를 기다린다. 첫 기억 전달에는 async 실행을 피하는 편이 적절하다.

사용자·프로젝트 설정 및 플러그인에서 훅을 제공할 수 있으나, 비관리 훅의 신뢰 절차와 프로젝트 신뢰 조건이 적용된다. 변경된 훅이 신뢰되지 않으면 실행되지 않을 수 있다. 기본 약 2,500 토큰을 넘는 문맥은 전체가 파일로 옮겨지고 미리보기로 전달될 수 있으므로 필수 기억은 짧게 구성해야 한다. 실패가 언제나 전체 작업 중단을 뜻한다고 단정할 수 없다. [Hooks](https://learn.chatgpt.com/docs/hooks)

문서의 SessionStart 출력에는 cwd 재지정 필드가 없다. 훅 자식 프로세스의 `cd`는 부모 실행기의 cwd를 바꾸지 않는다. 기억에 “rsch에서 일하라”는 문장을 넣는 것과 실제 실행 디렉터리를 지정하는 것을 분리해야 한다.

## 3. AGENTS.md와 앱 프로젝트의 역할

AGENTS.md는 작업 시작 전에 구성하는 지침 체인의 일부다. 전역 지침과 프로젝트 루트에서 현재 디렉터리까지의 경로에 있는 지침을 합친다. 보통 실행 시작 시 구성하므로 디스크의 변경이 매 메시지마다 자동 반영된다고 가정하면 안 된다. 하위 rsch 폴더의 AGENTS.md가 존재한다는 이유만으로 상위 bootstrap에서 시작한 세션에 자동 로드되는 것도 아니다. 파일 경로를 적어 두는 것은 해당 파일 본문을 주입하는 것과 다르다. [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

앱에서는 프로젝트 primary 폴더가 새 채팅의 기본 위치와 지침 탐색 기준이 된다. 보조 폴더를 연결해 검색 가능하게 하는 것만으로 그 폴더의 지침도 자동 탐색되는 것은 아니다. [프로젝트](https://learn.chatgpt.com/docs/projects?surface=app)

도메인이 역할을 정하려면 세션·역할·작업대의 대응 정보가 필요하다. rsch와 pln이 모두 bootstrap 루트에서 시작한다면 cwd만으로 역할을 알아낼 수 없다. 시작 화면의 역할 선택이나 도메인의 실행 요청 등에서 그 식별 정보를 확보해야 한다.

## 4. 다음에 확인할 최소 실험

격리된 rsch 실험 폴더에서 짧은 기억 표식 하나를 사용한다. 새 세션과 재개에서 (a) 실제 cwd, (b) 주입 경로의 실행 성공, (c) 첫 응답의 기억 인수 여부를 각각 기록한다. 모델의 표식 재현은 관찰 증거일 뿐 모든 지침 준수 보장은 아니다. 현재 앱이 설치 CLI와 같은 훅 기능을 로드하는지도 별도로 확인한다.

## 로컬 근거

설치 버전에서 `codex features list`의 hooks는 stable/true였다. `codex app-server generate-ts --experimental`로 생성한 타입은 이 문서 옆 `protocol-0.157.1`에 보존했다. 주요 파일은 v2/ThreadStartParams.ts, ThreadResumeParams.ts, ThreadStartResponse.ts, TurnStartParams.ts, ConfiguredHookHandler.ts, HookEventName.ts다. 실험적 타입을 포함하여 생성했으므로 필드 존재와 실제 호스트 지원을 구분한다.

## Claude Code 조사 분담

사용자 지시에 따라 기존 Claude Code 세션 `aaa_new_rsch`에 동일 질문을 전달했다. Claude 앱 입력창으로 전송했고 해당 세션의 접수 응답과 조사 시작을 확인했다. 결과 예정 위치는 `../claude-entry-research/FINDINGS.ko.md`다. 이 문서는 Codex 조사만 다룬다.
