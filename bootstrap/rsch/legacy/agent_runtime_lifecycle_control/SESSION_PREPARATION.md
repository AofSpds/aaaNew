# 세션 준비: 지침 파일 로딩과 Pi의 제어 경계

작성·공식 문서 열람: 2026-10-14. 범위는 세션 시작에서 첫 모델 요청까지이며, 이후 동작은 시작 시 로딩과 구분하는 데 필요한 만큼만 다룬다.

**Codex와 Claude Code는 실행 프로그램이 지침 파일을 찾아 모델 입력에 넣는다. Pi를 실행기로 사용하면 이 준비 과정을 직접 구성할 수 있다. Pi에서 별도 Codex·Claude Code를 실행하는 구성에서는 자식 프로그램이 공개한 접점까지만 제어할 수 있다.**

## 1. 무엇이 언제 읽는가

여기서 ‘자동 읽기’는 모델의 판단에 앞서 실행 프로그램의 로더가 파일 내용을 가져오는 것이다. ‘모델 읽기’는 모델이 이미 받은 지침을 보고 Read·명령 실행 등의 도구를 호출하는 것이다. 초기 지침의 존재와 그 지침을 실제로 준수했다는 증거도 구분한다.

공통 흐름은 다음과 같다.

`실행 위치·설정 결정 → 지침 발견·내용 로딩 → 모델 입력 구성 → 첫 추론 → 필요하면 추가 파일 읽기`

이는 설명을 위한 공통 순서다. 설정·훅·인증 등의 내부 초기화가 모두 직렬이라는 뜻은 아니다.

### Codex

- **시점:** 공식 문서는 실행 시작 때 지침 체인을 구성한다고 설명한다. TUI는 보통 한 번 실행한 세션당 한 번이다.
- **전역:** Codex home(기본 `~/.codex`)에서 `AGENTS.override.md` → `AGENTS.md` 순으로 첫 비어 있지 않은 파일을 선택한다.
- **프로젝트:** 프로젝트 루트(보통 Git 루트)부터 시작 작업 디렉터리(cwd)까지 내려오며, 각 디렉터리에서 `AGENTS.override.md` → `AGENTS.md` → 설정된 fallback 파일명 순으로 최대 한 파일을 선택한다. 루트가 없으면 cwd만 확인한다.
- **합성:** 상위에서 하위 순으로 이어 붙인다. 더 가까운 지침이 뒤에 온다. 크기 제한은 `project_doc_max_bytes`, 기본 32 KiB다.
- **경계:** 시작 cwd 아래의 모든 지침 파일을 재귀적으로 미리 읽는다는 의미가 아니다. 실행 중 파일을 고쳐도 자동 갱신을 전제하지 않고, 새 실행에서 확인한다.

근거: [Codex AGENTS.md 공식 문서](https://learn.chatgpt.com/docs/agent-configuration/agents-md). 데스크톱의 앱 실행, 연결, thread 생성, turn 시작은 별개다. 위 CLI 설명을 “매 사용자 메시지마다 프로세스와 로더가 새로 시작한다”로 확대하지 않는다. [App Server](https://learn.chatgpt.com/docs/app-server)

### Claude Code

- **시점·범위:** 시작할 때 조직·사용자 지침과 cwd 및 상위 디렉터리의 `CLAUDE.md`·`CLAUDE.local.md` 등을 컨텍스트에 넣는다. 프로젝트 파일은 `CLAUDE.md` 또는 `.claude/CLAUDE.md`에 둘 수 있다.
- **합성:** 발견한 내용을 합친다. 디렉터리는 루트부터 cwd 순이며, 같은 디렉터리에서는 local 내용이 뒤에 온다. 파일 자체를 서로 대체하는 방식은 아니다.
- **하위 디렉터리:** 그 안의 파일을 읽거나 수정하는 시점에 해당 지침을 추가 로딩한다. 시작부터 하위 전체 본문을 넣지 않는다.
- **import:** `@path`는 로더가 내용을 확장한다. 상대 경로 기준은 import를 적은 파일이며, 재귀 import는 최대 4단계다. 외부 경로는 import 승인 조건의 영향도 받는다.
- **AGENTS.md:** 직접 자동 로딩은 2.1.277 이상 기능이다. 기본 설정에서는 cwd·상위에 프로젝트 `CLAUDE.md` 계열이 없을 때 적용된다. 두 종류를 함께 읽는 설정도 있다.

근거: [Claude Code memory 공식 문서](https://code.claude.com/docs/en/memory). 이번 PC에서 직접 확인한 버전은 **Codex CLI 0.157.1 / Claude Code 2.1.268**이다. 따라서 이 Claude 설치본에 최신 AGENTS.md 직접 로딩을 전제하면 안 된다. 인접한 `CLAUDE.md`의 `@AGENTS.md` import는 별도 방식이다. 로컬 CLI 버전은 데스크톱 내장 실행기의 버전 증명이 아니다.

## 2. ‘다음 문서를 읽으라’는 언제 실행되는가

| 지침 파일 내용 | 실제 의미 |
| --- | --- |
| `CURRENT.md를 먼저 읽으세요.` | 모델이 이 문장을 받은 뒤 추가 읽기를 수행해야 한다. 로딩된 문장만으로 CURRENT.md 본문까지 입력됐다고 할 수 없다. |
| Markdown 링크 `[Current](CURRENT.md)` | 링크가 있다는 사실과 대상 본문을 읽었다는 사실은 다르다. |
| Claude의 `@CURRENT.md` | 지원되는 import 문법으로 로더가 확장한다. 모델의 첫 도구 호출에 맡기는 것과 다르다. |

Claude 공식 문서도 자연어로 “AGENTS.md를 읽으라”고 적는 방식과 `@AGENTS.md`를 구분한다. Codex의 파일 탐색 규칙에 Claude의 import 문법을 그대로 적용해서는 안 된다. [Claude import 설명](https://code.claude.com/docs/en/memory#remove-an-earlier-agentsmd-workaround), [Codex 탐색 규칙](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Claude의 `SessionStart` 훅은 시작·재개 시 컨텍스트를 추가할 수 있다. 그러나 이를 지침 로더 전체를 대체하는 인터페이스로 보지는 않는다. 최신 문서의 `InstructionsLoaded`는 로딩 관측용 비동기 이벤트로, 로딩을 차단하거나 내용을 바꿀 수 없다. compaction 뒤 재로딩도 구분한다. 이 최신 훅 설명 전체가 로컬 2.1.268에서 검증된 것은 아니다. [Claude hooks](https://code.claude.com/docs/en/hooks#instructionsloaded)

## 3. SLR에서 연구한 Pi는 무엇인가

SLR-R05가 지정한 제품은 **Pi Agent Harness / `@earendil-works/pi-coding-agent` / `earendil-works/pi`**다. `badlogic/pi-mono`는 이전 저장소 주소다. 원 연구는 0.87.1을 고정했고, 실행·세션·컨텍스트·확장 기반을 확인했다. [SLR-R05 원문 §1·§3](https://github.com/AofSpds/AAA/blob/12a1f656b42a049cfe95995accc2663dea9053a3/projects/AAA/subplans/SE-SELF-LEARNING-RUNTIME/work/research/20260928-rsch-commission/raw/SLR_R05_PI_GIT_BASED_FINAL_RAW_v1.0_20260928.md)

도입 설계의 역할 구분은 **AAA 제어부가 Pi 실행기를 연결하는 구성**이다. Pi subprocess의 JSONL RPC와 in-process SDK를 비교했다. Pi가 Codex·Claude Code의 내부를 자동으로 지배하는 상위 프로그램이라는 뜻은 아니다. [Pi 도입 설계 §1](https://github.com/AofSpds/AAA/blob/ec359d7035f5cfb5a520831f290dd9869840acd3/projects/AAA/subplans/SE-SELF-LEARNING-RUNTIME/work/architecture/20261007-pi-adoption/PI_ADOPTION_ARCHITECTURE.md)

후속 PS5 기록은 **1.1.0 / `abe508e1b89912adde45528136c3221eb69acdd7`**을 검증 대상으로 삼았다. Pi는 그 기준을 통과한 첫 후보이며, 기록상 제품 선택은 별도다. 이를 모든 구성에서 성능·품질이 가장 좋다는 순위로 일반화하지 않는다. [PS5 확인 종결 기록](C:/Users/ms1pk/dev/AAA/.claude/worktrees/se-slr-sub-pln-c4596b/slr-subpln/ps5/16_SUBPLN_PS5_PI_CLOSURE.md)

## 4. Pi는 어디까지 제어하는가

아래 Pi 기능은 SLR 후속 검증과 같은 **1.1.0 pin**의 문서·소스 및 보존 설치본을 대조했다.

| 경계 | 가능한 제어 | 남는 한계 |
| --- | --- | --- |
| Pi 세션 생성 전 | SDK host가 cwd, agentDir, ResourceLoader, SessionManager, 모델·도구를 지정 | 생략한 항목은 기본 구현을 사용하므로 “SDK 사용”만으로 자동 로딩이 없어지지 않는다. [SDK](https://github.com/earendil-works/pi/blob/abe508e1b89912adde45528136c3221eb69acdd7/packages/coding-agent/docs/sdk.md) |
| Pi의 지침 파일 로딩 | 기본 탐색을 끄고 승인된 지침만 공급하거나, 사용자 ResourceLoader로 교체 | 설정·확장 등 다른 로딩 경로는 별도다. [ResourceLoader](https://github.com/earendil-works/pi/blob/abe508e1b89912adde45528136c3221eb69acdd7/packages/coding-agent/src/core/resource-loader.ts) |
| Pi가 모델에 보낼 입력 | `before_agent_start`로 system prompt 조정. `context`로 대화 메시지, `context_with_system`으로 시스템 메시지를 포함한 요청별 transcript 변환 | Pi가 보내는 입력의 제어다. 공급자 서버 내부 지침·추론·행동 준수까지 제어하는 것은 아니다. [Extensions](https://github.com/earendil-works/pi/blob/abe508e1b89912adde45528136c3221eb69acdd7/packages/coding-agent/docs/extensions.md) |
| Pi에서 별도 Codex·Claude Code 실행 | 외부 호출부가 실행 위치·파일·옵션을 준비하고, 자식의 공개 API·훅을 연결 | 자식 CLI의 로더·숨은 프롬프트·개별 모델 요청에 Pi 훅이 자동 적용되지는 않는다. 연결 구현이 필요하다. **구성상 추론** |
| 이미 시작한 Codex·Claude 대화 안에서 Pi를 도구로 호출 | 호출 이후 Pi 작업과 반환 내용을 제어 | 현재 대화의 최초 지침 로딩은 이미 끝났다. 그 세션의 시작 이전 단계로 소급할 수 없다. **시간 순서에 따른 결론** |

### 파일 읽기와 모델 노출은 서로 다른 경계다

Pi 1.1.0 기본 로더는 agentDir의 전역 지침과 파일시스템 루트→cwd의 지침을 모은다. 각 디렉터리에서는 `AGENTS.override.md → AGENTS.md → AGENTS.MD → CLAUDE.md → CLAUDE.MD` 순으로 첫 읽기 가능한 파일을 선택한다. 중첩 worktree에는 중복 지침 처리도 있다.

`agentsFilesOverride`는 **기본 파일 읽기가 끝난 뒤** 결과 목록에 적용된다. 빈 목록을 반환하면 모델에 넣을 지침을 없앨 수 있지만, 파일을 읽지 않았다는 증거가 되지는 않는다. 기본 context-file 읽기를 건너뛰려면 `noContextFiles: true`를 쓰거나 이를 수행하지 않는 ResourceLoader를 공급해야 한다. 이것도 다른 도구·확장의 파일 접근까지 막는 OS 격리를 뜻하지 않는다. [고정 소스: 탐색과 reload](https://github.com/earendil-works/pi/blob/abe508e1b89912adde45528136c3221eb69acdd7/packages/coding-agent/src/core/resource-loader.ts)

## 5. 이번 주제에서 확인된 범위

SLR의 보존 E2 코드는 실제로 `noContextFiles: true`, 빈 agentsFiles, 명시적 system prompt를 사용했다. 기존 검증 보고는 fake 모델 범위에서 입력 분리를 확인했다고 기록한다. SDK core 내부 경로를 사용했으므로 일반 CLI·package root 진입과 같은 동작이라고 확대하지 않는다. 이번에는 코드를 읽고 기록을 대조했으며 새 세션 실험을 실행하지 않았다. [E2 보존 코드](C:/Users/ms1pk/dev/slr-p5a/pi/runs/pi-e2-20261012T234936Z-01/SOURCE_run-core-e2.mjs:40), [기존 검증 보고](C:/Users/ms1pk/dev/slr-p5a/review/PI_IVA_REPORT.md)

**세션 준비를 확실히 제어하려면 제어부가 로더 실행 전에 있어야 한다.** Pi SDK를 실행 기반으로 택하면 지침 선택·내용·모델 입력을 직접 구성할 접점이 있다. 기존 Codex·Claude Code를 유지하면 시작 전 준비와 각 제품의 공개 로딩 규칙을 연결해야 한다. 이 문서는 그 경계를 정리한 것이며 실행기 선택이나 설치 변경을 수행하지 않는다.
