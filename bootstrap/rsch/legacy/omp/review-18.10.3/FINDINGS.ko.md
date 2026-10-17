# OMP 18.10.3 — SLR 우려 재점검

확인일: 2026-10-14. 설치한 OMP 18.10.3의 build manifest commit `81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b`에 고정하여 공식 소스를 확인했다. 전 세계 최신 릴리스라는 의미는 아니다. 이번 점검은 문서·소스 비교이며 실제 모델 전송, 오류 주입, 전원 장애 시험은 수행하지 않았다.

## 결론

배포 편의성과 RPC 통합 기능은 개선됐다. 그러나 SLR이 요구한 전송 차단·독립 기록 보장은 자동으로 충족되지 않는다. OMP를 재평가할 근거는 충분하지만 Pi보다 우월하거나 기존 우려가 모두 해소됐다는 결론은 아니다. 과거 SLR도 OMP를 성능 때문에 탈락시킨 것이 아니라 대안 실행기로 남겨 두었다.

| 항목 | 현재 확인 | 판정 |
|---|---|---|
| Windows 배포 | 이번 설치는 단독 omp.exe로 실행했다. 공식 Python 클라이언트 기본 명령은 `omp --mode rpc`이며 실행 명령을 지정할 수 있다. 따라서 외부 Bun 설치를 모든 RPC 배포의 필수 조건으로 볼 수 없다. 반면 프로세스 내부 SDK는 공식 문서상 Bun >=1.3.14가 필요하다. | RPC 배포 부담 완화. SDK 제약은 별도 |
| Python RPC 완성도 | 공통 wire schema 기반 생성 클라이언트와 서버 타입 대조 검사가 README에 명시돼 있다. 패키지는 여전히 0.1.0, `Development Status :: 3 - Alpha`이다. | 기능 개선, 안정판 전환·SDK 전체 기능 동등성은 확인되지 않음 |
| 요청 전 훅 실패 시 차단 | `emitBeforeProviderRequest`는 실패 처리 인자로 undefined를 전달한다. 공통 실행기는 오류/timeout을 보고한 뒤 undefined를 반환하고, 호출자는 기존 currentPayload를 유지한다. | 해당 훅의 실패가 곧 전송 차단이라는 보장 없음. 핵심 우려 남음 |
| 자동 동작 통제 | memory.backend 기본값은 off다. 그러나 sdk.ts에는 별도의 autolearn, cache warming, Codex prewarm 경로가 존재한다. RPC의 cache warming 관측·설정 기능도 추가됐다. | 통제 수단은 있으나 memory off 하나로 전체 보조 동작이 꺼진다고 볼 수 없음 |
| 기록 내구성 | SessionManager는 완료 항목을 OS에 동기 전달하지만 fsync하지 않는다고 명시한다. 소프트웨어 충돌 복구와 전원 손실 보장은 구분된다. | SLR의 독립 durable journal 요구는 남음 |

## 실제로 추가·수정된 내용

설치 버전의 CHANGELOG에서 과거 기준 버전 18.3.5 이후 항목을 확인했다. 아래는 공식 변경 기록이며 이번에 직접 재현한 시험 결과는 아니다.

- 18.4.5: RPC cache_warming_start/end 이벤트 및 set_cache_warming 제어, Python 대응 메서드.
- 18.5.0: Windows RPC stdout 역압으로 입력 처리까지 멈추던 교착 수정. 서브에이전트 완료 예상 시간 요청은 RPC/ACP/SDK 실행에서는 하지 않도록 변경.
- 18.5.1: 기계 판독 가능한 RPC wire schema와 Python/Rust/Go 생성 클라이언트 지원.
- 18.10.0: RpcClient.stop()이 프로세스에 종료 신호를 보내지 않아 무한 대기하던 문제 수정.

공식 Python RPC 자체, protocol negotiation, chunking, prompt correlation, host tools는 과거 SLR 자료에도 존재한다. 이를 모두 최신 버전에서 처음 생긴 기능으로 계산하지 않는다.

## 근거

설치 버전 고정 소스는 이 문서 옆 `sources`에 보관했다.

- [확장 훅 구현](https://github.com/can1357/oh-my-pi/blob/81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b/packages/coding-agent/src/extensibility/extensions/runner.ts): 1515–1595, 2059–2096행.
- [세션 기록 구현](https://github.com/can1357/oh-my-pi/blob/81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b/packages/coding-agent/src/session/session-manager.ts): 851–875행의 내구성 계약.
- [Python 패키지 상태](https://github.com/can1357/oh-my-pi/blob/81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b/sdk/python/omp-rpc/pyproject.toml), [Python 클라이언트 설명](https://github.com/can1357/oh-my-pi/blob/81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b/sdk/python/omp-rpc/README.md).
- [변경 기록](https://github.com/can1357/oh-my-pi/blob/81e1d8927a3c16cfaff2e9456baa8c060e1e0e9b/packages/coding-agent/CHANGELOG.md).
- [공식 SDK 문서](https://omp.sh/docs/sdk): 조회 시점 SDK의 Bun 요구 사항. 이 웹 문서는 버전 고정 문서가 아니다.
- 과거 SLR: `C:\Users\ms1pk\dev\slr-p5a\src\projects\AAA\coordination\exchanges\AAA-SLR-APP-IMPLEMENTATION-UNCERTAINTY-RESEARCH-20261007-001\OMP_RESEARCH_RESPONSE.md` §2. 참고 자료로만 읽었다.

구독 인증의 경로 고정, 실패 후 다른 계정·과금 경로 전환, 취소 후 실제 도구 효과, SDK와 RPC 전체 기능 동등성은 이번 범위에서 해결 판정을 하지 않았다. 다음 검증은 모델에 접속하지 않는 격리 시험으로 훅 오류·timeout 시 전달 결과를 확인하는 작은 단계부터 가능하다.
