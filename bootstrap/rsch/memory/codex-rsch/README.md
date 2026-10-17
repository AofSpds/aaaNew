# rsch 작업 기억

기록일: 2026-10-14 KST. 이 기록은 현재 대화에서 확정한 작업 원칙, 설치 결과와 다음 단계를 보존한다.

## 이어받을 때 먼저 읽기

- 작업대: C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch. 기본 실행 cwd와 혼동하지 않는다.
- 목적: bootstrap에서 역할별 작업대와 경험 view를 마련하여 다음 에이전트의 재설명·재탐색·재작업을 줄인다.
- 현재 상태: 사용자 요구와 설계 후보를 정리하여 [현재 요구사항](../../requirements/REQUIREMENTS_CODEX.md)에 별도 보관했다. 구현·실측 여부는 해당 문서에서 구분한다.
- 시행착오와 적용할 교훈: [LESSONS_CODEX.md](LESSONS_CODEX.md).
- 사용자 진행 방식: 외부 사례를 하나씩 약 2페이지 분량으로 본다. 첫 사례 [Cline Memory Bank](../../research/memory-external/MEMORY_CLINE_CODEX.md) 정리 완료. 다음 사례는 아직 작성하지 않았다.
- 외부 사례와 이번 수정 범위: [MEMORY_RESEARCH_CODEX.md](../../research/memory-external/MEMORY_RESEARCH_CODEX.md).
- 모델별 요청 기록은 같은 rsch 폴더의 [REQUEST_CODEX.md](../../requests/REQUEST_CODEX.md), [REQUEST_CLAUDE.md](../../requests/REQUEST_CLAUDE.md)에 동일한 형식으로 둔다. 파일 저장과 상대 세션 전달·접수는 별개다.
- Claude 진입 조사: 완료 통보 수신 및 결과 파일 확인. Codex가 실험을 독립 재현한 것은 아니다.
- 다음 검증 후보: 새 세션이 이 기록을 읽고 작업대·메모 위치·현재 목적을 재질문 없이 인수하는지 확인한다. 아직 수행하지 않았다.

## 기록을 갱신하는 시점과 확인

사용자 정정, 작업 위치·범위 결정, 조사 결과 수신, 작업 완료가 생기면 관련 항목을 그 작업 안에서 갱신한다. 완료 전에 현재 상태와 결과 링크를 읽어 확인한 뒤에만 “기록했다”고 보고한다. 미확인 결과를 완료로 올리지 않으며, 오래된 다음 단계는 보류로 표시한다.

시행착오는 관측한 문제 → 영향 → 다음에 적용할 교훈 → 확인 수준으로 남긴다. 이 기록은 역할 경험 view의 후보이며, 다른 상황에도 유효한지 검토하지 않은 교훈을 보편 규칙으로 승격하지 않는다.

파일 존재, 모델 입력 포함, 실제 준수, 다음 작업의 효과를 따로 확인한다. 이 README는 현재 수동 진입점이며 자동 로딩을 보장하는 설정이 아니다.

## 작업 원칙

- 이 대화의 작업 영역은 `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch`다. 설치와 문서 작성은 이 폴더 아래에서 수행한다.
- 도구의 기본 작업 디렉터리가 `C:\Users\ms1pk\dev\AAA`여도 그곳에 산출물을 만들지 않는다. 작업 명령에 정확한 경로를 지정한다.
- 사용자는 한꺼번에 많은 작업이나 설명을 원하지 않는다. 작은 단계로 진행하고 핵심만 짧게 알린다.
- 기존 사용자 파일과 설정을 보존한다. 설치 위치를 임의로 바꾸지 않는다.
- 여기의 기억은 rsch 작업을 이어가기 위한 기록이다. 다른 프로젝트의 Persona나 Memory 소유권을 변경하지 않는다.

## 연구 맥락

### 현재 우선 연구 과제

2026-10-14 사용자 정정: bootstrap은 도메인을 처음 만드는 프로젝트다. rsch는 그 안의 조사 작업대이며, 프로젝트에는 pln 및 규모에 따라 마일스톤 서브 프로젝트와 sub_pln 등 역할별 작업대가 생긴다. rsch의 상설 여부는 확정하지 않았다. 각 작업대의 수행 기록을 리뷰하여 역할별 경험 view로 만들고, 다음 에이전트가 필요한 경험을 전달받아 일을 이어가는 것이 구상이다.

첫 연구 질문은 “에이전트가 시작되면 도메인이 역할·필요한 기억·작업대 위치를 전달하여, 해당 작업대에서 업무를 이어가도록 할 수 있는가?”다. 기억 전달의 주체는 도메인이다. 특정 실행기나 UI 선정을 선행 조건으로 두지 않는다.

첫 조사에서는 다음 세 경계를 구분한다.

1. 진입: 도메인이 실행을 시작한 경우와 사용자가 실행환경에서 직접 세션을 연 경우에, 도메인이 개입할 수 있는 시점이 있는가?
2. 전달: 첫 업무 수행 전에 역할, 현재 업무, 관련 경험 view를 실제 모델 입력에 넣고 작업 디렉터리를 지정할 수 있는가? 파일을 디스크에 놓는 것만으로 주입 성공이라 하지 않는다.
3. 확인: 에이전트가 지정된 작업대와 업무를 인수했음을 무엇으로 확인하며, 전달 실패를 감지하거나 첫 업무 실행을 보류할 수 있는가? 이는 조사할 기준이며 아직 구현된 보장이 아니다.

우선 이 진입·전달 경로 하나를 조사한다. 전체 실행기 비교, 추가 설치, 일정 관리 확장보다 앞선다. UI의 파일 탐색·검색은 사용자가 작업대를 관찰하는 별도 요구로 보존한다.

사용자는 에이전트의 세션 준비, AGENTS.md와 CLAUDE.md 로딩, 실행기와 모델 연결의 경계를 조사하고 있다. SLR에서 검토한 Pi, Hermes, OMP, Chainlit을 직접 설치해 비교하고 있으며 OpenCode도 추가 비교 대상이다.

사용자가 말하는 API 방식은 별도 API 키와 과금 방식이다. OAuth 구독 인증과 구분해서 설명한다. OAuth로 모델을 연결하는 것과 Codex 또는 Claude Code CLI 자체를 실행하는 것도 서로 다른 실행 구조다.

Pi를 가장 많이 쓰이는 앱이나 보편적인 최선으로 단정하지 않는다. SLR의 검토·실험과 제품 채택 확정을 구분한다.

## 설치와 확인 결과

아래 경로는 모두 작업 영역 기준이다. 웹 실행 상태는 2026-10-14 설치 확인 시점의 기록이므로 다음 작업 전에 필요하면 다시 확인한다.

| 대상 | 설치 폴더 | 확인 결과 | 웹 주소 |
|---|---|---|---|
| Pi Web | `pi\pi-web` | 기존 설치 유지, pi-web 0.12.1 | http://127.0.0.1:30141/ |
| OpenCode | `opencode` | 1.19.0, 버전·HTTP 200·한국어 시작 화면 확인 | http://127.0.0.1:4096/ |
| Hermes Agent | `hermes` | 0.21.7+500.g8f81791, CLI와 대시보드 확인 | http://127.0.0.1:9119/ |
| OMP Oh My Pi | `omp` | 18.10.3, 공식 SHA256·버전·도움말 확인 | 터미널 앱 |
| Chainlit | `chainlit` | 2.12.0, Python 3.12.13, 공식 hello 예제 화면 확인 | http://127.0.0.1:30142/ |

OpenCode, Hermes, Chainlit의 HTTP 응답은 2026-10-14 02:39 KST에 모두 200이었다. OMP는 CLI 실행만 확인했으며 모델 응답 검증은 아직 하지 않았다. Chainlit은 채팅 UI 프레임워크이고 현재 앱은 모델 연결이 없는 공식 예제다.

Hermes 설치 소스 commit: `8f817911723e3ec13e7f47fc022fdcc9e2149354`.

## 실행 파일

PowerShell에서 아래 스크립트를 실행한다. 각각 자신의 폴더를 작업 디렉터리로 설정한다.

- OpenCode 웹: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\opencode\start.ps1`
- Hermes CLI: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\hermes\start.ps1`
- Hermes 웹: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\hermes\dashboard.ps1`
- OMP CLI: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\omp\start.ps1`
- Chainlit 예제: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\chainlit\start.ps1`

Chainlit의 기본 포트 8000은 Windows에서 바인딩이 거부되어 사용 가능한 30142로 변경했다. 기존 서버가 실행 중이면 같은 서버를 중복 실행하지 않는다.

OpenCode의 XDG 설정·데이터는 `opencode\.runtime`, Hermes 데이터는 `hermes\data`, OMP 데이터는 `omp\data`에 저장하도록 실행 스크립트를 구성했다. Chainlit은 전용 `.venv`를 사용한다.

## 설치 관련 보류 사항

- 현재 우선 과제는 기억·작업대 진입 조사다. 추가 로그인과 모델 연결은 보류한다. 재개하면 하나씩 진행한다. 설치 성공과 모델 연결 성공을 구분한다.
- 사용자는 앞서 Pi CLI 로그인을 완료했다고 알렸다. 다른 앱으로 자격 증명을 임의 복사하지 않는다.
- Hermes의 컴퓨터 제어 도구 파일은 설치됐지만 Windows cua-driver 자동 시작 등록은 관리자 권한 UAC가 필요하여 공식 설치 프로그램이 보류했다. 필요할 때 대화형 터미널에서 `hermes computer-use install --upgrade` 단계를 진행한다.
- Chainlit에서 실제 모델과 대화하려면 별도 백엔드 연결이 필요하다.

## 관련 기록

- 설치 상세: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\agent-installations.json`
- 세션 준비 문서: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\legacy\agent_runtime_lifecycle_control\SESSION_PREPARATION.md`
- SLR 후보 연구 자료: `C:\Users\ms1pk\dev\slr-p5a\src\projects\AAA\coordination\exchanges\AAA-SLR-APP-IMPLEMENTATION-UNCERTAINTY-RESEARCH-20261007-001` — 참고용으로 읽으며 산출물 저장 위치로 사용하지 않는다.

이후 확정된 변경 사항은 이 폴더에 기록한다. 비밀번호, OAuth 토큰, API 키는 기록하지 않는다.

## 2026-10-14 OMP 18.10.3 재점검

- 설치 build commit 81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b의 공식 소스를 고정해 비교했다.
- 단독 실행 파일과 RPC 기능은 배포·통합 부담을 줄인다. Python 클라이언트는 여전히 alpha이며 SDK 전체 기능 동등성을 증명한 것은 아니다.
- before_provider_request 오류/timeout 후 기존 payload 유지, fsync 없는 세션 기록은 현재 소스에서도 확인돼 SLR의 강제 통제·독립 durable journal 요구가 남는다.
- 이번 점검은 소스 확인이다. 모델 전송·오류 주입·장애 시험은 하지 않았다.
- 상세: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\legacy\omp\review-18.10.3\FINDINGS.ko.md`


## 2026-10-14 세션 진입 조사와 분담

- Codex: CLI 0.157.1의 --cd 및 App Server cwd/developerInstructions 접점을 확인했다. SessionStart 문맥 전달과 실제 cwd 지정은 별개다. 현재 앱의 실제 주입 실험은 아직 하지 않았다.
- 상세: `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\research\runtime\codex-entry-research\FINDINGS.ko.md`
- 사용자가 Claude Code 조사를 기존 `aaa_new_rsch` 세션에 맡기도록 지시했다. Claude 앱의 해당 세션 입력창으로 전달했고 “접수했습니다” 및 조사 시작 응답을 확인했다. CoS 제어 연결은 이용 불가였으므로 사용하지 않았다.
- Claude 조사 완료 통보 수신 및 결과 파일 확인(실험 독립 재현은 미실시): `C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\research\runtime\claude-entry-research\FINDINGS.ko.md`

## 2026-10-14 이전 연구 보관

사용자 지시로 이전 수명주기 연구, SESSION_PREPARATION.md, OMP 18.10.3 재점검 결과와 근거 소스를 rsch\legacy 아래 원래 분류대로 이동했다. 현재 Codex·Claude 진입 조사와 설치 폴더는 유지했다. 이동 전후 파일 SHA256을 대조했다.


## 2026-10-14 조사 초점 정정

사용자는 모바일에서 짧게 한 부분씩 읽기를 원한다. 원하는 것은 메모 작성 가이드보다 실행환경이 기억 전달·도구 실행·실패 처리를 어떻게 통제하는지다. 이후 사례는 제어 주체, 개입 시점, 차단 조건, 우회 경계를 먼저 설명한다. 기존 Cline 설명은 운영 방법 중심이었으며 통제 구현 검증을 대신하지 않는다.

Cline 공식 저장소 훅 설명에는 PreToolUse의 cancel 제어가 있다. 유지관리자 이슈 #13277의 2026-08-25 설명에 따르면 Claude Code/Codex처럼 공급자 내부에서 실행하는 도구는 관측 이벤트로 표시되지만 Cline 훅 파이프라인을 통과하지 않는 경계가 있다. 이는 유지관리자 기록이며 현재 설치본 실측은 아니다. 근거: https://github.com/cline/cline/issues/13277 및 https://github.com/cline/cline/blob/main/.clinerules/hooks/README.md
## 2026-10-14 실행 옵션 요구

사용자는 OAuth 인증으로 모델을 직접 연결하는 방식과 Codex CLI·Claude Code CLI를 실행하는 방식을 선택 옵션으로 지원하고 싶다고 밝혔다. OAuth는 인증 방식이고 CLI 사용은 실행기 선택이므로 설정에서 구분한다. CLI 자체도 OAuth 인증을 사용할 수 있어 두 개념을 상호 배타적인 인증 방식으로 설명하지 않는다.

설계 방향: 도메인이 역할·작업대·기억을 공통으로 준비하고, 선택한 실행기에 맞춘 연결부가 시작 인자·지침 전달·시작 훅을 적용한다. 첫 모델 호출 전 준비 완료와 주입 실패 처리 가능 여부를 옵션별로 검증한다. 외부 CLI 내부 도구의 통제는 해당 CLI 접점에서 확인해야 한다. 이는 요구와 설계 방향 기록이며 실행 옵션이나 훅을 실제로 설정한 것은 아니다.
## 2026-10-14 jevlike 기반 관계 엔진 방향

사용자 원문: “네 이부분은 jevlike엔진 기반으로 관계엔진을 두고 싶습니다”. 배경은 MD 내부와 문서 사이의 불필요한 의미 중복, 충돌, 관계 미정립 문제다.

설계 방향은 기억 항목과 관계를 구조화하여 관리하고 역할별 MD는 필요한 기억을 보여주는 view로 만드는 것이다. 관계 엔진의 기반으로 jevlike를 사용하려는 사용자 의향을 보존한다. 앞서 제안한 MD 원본 중심 구성과 SQLite 선택은 확정 사항으로 취급하지 않는다.

관계 엔진에 요구할 기능 후보: 기억의 식별, 근거·적용 역할·조건·검토 상태의 연결, 중복 후보와 충돌 검토, 보완·대체 이력, 역할별 경험 view 구성. 이는 요구 후보이며 jevlike가 이미 제공한다고 확인한 기능 목록이 아니다. jevlike의 현재 구현·저장 방식·연결 API는 아직 확인하지 않았다. 실행환경별 기억 전달과 도구 실행 차단은 관계 엔진과 연결할 별도 책임이다.

## 2026-10-14 기억 서브리서치 세션

사용자 요청으로 별도 Codex 채팅 rsch_sub_memory를 생성했다. threadId: 01a1385f-e559-7ca2-b20a-698c5e84497b, host: local. 앱 소속은 AAA-CONTEXT이며, 실제 지정 작업대는 C:\Users\ms1pk\dev\aaaNew\bootstrap\rsch\research\sub-memory다. 생성 도구로 기본 cwd를 rsch에 직접 바인딩한 것은 아니며, 인계문에 모든 작업 명령과 산출물의 절대 경로를 지정했다.

범위: requirements/REQUIREMENTS_CODEX.md의 R05·R06, 시행착오의 경험화 및 jevlike 기반 관계 엔진. 첫 턴은 요구·작업 기억 인수와 INTAKE_CODEX.md 작성으로 제한했다. 전체 조사·설치·구현을 시작하도록 지시하지 않았다. 부모 rsch는 전체 요구와 실행 접점 조사를 유지한다. 세션 생성과 인계문 전달은 완료했으며, 작업대 인수와 결과 작성은 해당 채팅의 응답으로 확인해야 한다.

사용자 추가 지시로 서브리서치 지속 기억 위치를 rsch\sub로 지정했다. 지침은 [sub/AGENTS.md](../codex-sub-memory/AGENTS.md), rsch_sub_memory 세션의 기억은 [sub/rsch_sub_memory.md](../codex-sub-memory/rsch_sub_memory.md)다. 연구 산출물 작업대 rsch\rsch_sub_memory는 유지한다.
