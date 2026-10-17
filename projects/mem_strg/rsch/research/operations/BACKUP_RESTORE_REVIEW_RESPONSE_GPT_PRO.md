# P3 — 백업·복원 초벌안 검토

**ACT_ID:** `MEM_STRG-PRO-P3-BACKUP-RESTORE-REVIEW-20261018-001`

**기본 순서는 타당합니다. 다만 참조값의 Git 보존, 봉인 세대의 식별, 검증 실패 시 진행 중단은 반드시 보완해야 합니다.**

지정 커밋 `99952a8b3f8d9c78554b56b512e639c02ef33f07`의 [초벌안][draft]·[실측 코드][bench]·[실측 결과][results]·[P2 Q2][p2]를 확인했습니다. 저장소 변경이나 새 실측은 하지 않았습니다.

**근거 표기:** 입력 문서·코드 사실은 **[저장소·릴리스, 2026-10-18]**, 아래 처리 제안은 **[추정, 2026-10-18]**입니다. 공식 문서는 별도로 표시하며, 날짜는 확인일입니다.

## Q1. 참조값 블록과 manifest

| 맞음 | 고칠 것 | 빠진 것 |
|---|---|---|
| **식별·출처:** `store_id`와 전체 `source_commit`을 남기는 방향. | **`<브랜치>@<head7>`은 봉인 고유 ID로 부족합니다.** 7자 충돌 외에도, 같은 Git head에서 로컬 자료만 바뀌면 ID가 재사용됩니다. 전체 SHA로 늘려도 후자는 해결되지 않습니다. | 브랜치명과 독립된 **봉인 ID 또는 봉인 세대**, `source_repo`, PR 식별자, 시간대가 있는 `sealed_at`, 프로젝트·역할의 포함 범위. |
| **manifest:** 파일별 크기·SHA-256과 manifest 자체 SHA-256의 조합. | UTF-8·LF 규칙은 **manifest에만** 적용해야 합니다. 원본 파일의 CRLF·LF·인코딩을 변환하면 “그대로 보관”과 어긋납니다. | manifest 규격 버전, BOM 유무, 정렬 기준, 마지막 LF, **0개 파일일 때 표현**, 크기·지문의 문법, 중복 경로 거부 규칙. |
| **경로:** 묶음 루트 기준 상대경로 사용. | 코드의 `/` → `__` 치환은 충돌합니다. 예를 들어 브랜치 `a/b`와 `a__b`가 같은 백업 폴더명으로 바뀝니다. **충돌 없는 ID→경로 대응**이 필요합니다. | `/` 구분자 규칙, 절대경로·드라이브·UNC·`.`·`..`·TAB/CR/LF 거부, 복원 루트 이탈 방지. 대소문자·Unicode를 조용히 합치지 말고 대상 파일시스템의 이름 충돌을 검사해야 합니다. |
| **범위:** 역할별 폴더 전체를 묶겠다는 기준. | 현재 `is_file()` 목록은 **빈 폴더를 검증하지 못하고**, 파일 symlink를 대상 내용으로 취급할 수 있습니다. 기본 `copytree()`도 symlink를 따라 복사합니다. | 빈 디렉터리 기록과 객체 종류 규칙. symlink·junction/reparse point는 명시적으로 보존하거나 **지원하지 않으면 봉인을 중단**해야 합니다. ADS·ACL·소유권·시간·hard link 관계까지 보존하는지도 범위를 밝혀야 합니다. |
| **검증:** 누락·추가·크기·내용을 대조하는 방식. | 코드에서 중복 경로는 dictionary에 덮어써집니다. 빈 묶음은 manifest가 `"\n"`이 되어 파일 수를 1로 세고 파싱도 실패합니다. **manifest 지문·문법·경로를 먼저 검사한 뒤 복사**하는 편이 맞습니다. | `files/bytes/roles`와 실제 목록의 정합성, 읽기·열거 오류의 실패 처리. “있어야 할 역할·자료” 목록도 필요합니다. 애초에 manifest 작성에서 빠진 자료는 사후 지문 검사로 찾을 수 없습니다. |

Windows에서는 기본 대소문자 처리, 예약명·금지문자, 끝의 점·공백, 경로 길이도 고려해야 합니다. Python 공식 문서는 Windows의 `copy2()`가 소유권·ACL·ADS를 복사하지 못한다고 명시합니다. **[공식 문서, 확인 2026-10-18]** ([learn.microsoft.com](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file?utm_source=chatgpt.com), [docs.python.org](https://docs.python.org/3/library/shutil.html?utm_source=chatgpt.com))

`sealed_by`는 출처 표기입니다. 그 문자열이나 SHA-256만으로 DPM 승인·작성자 진위를 증명하는 것은 아닙니다. 지문 대조에는 **기준 참조값 자체가 보존되어 있다는 조건**이 붙습니다. **[추정, 2026-10-18]**

## Q2. 고정·참조·머지·복원 순서

| 맞음 | 고칠 것 | 빠진 것 |
|---|---|---|
| **쓰기 차단 → 봉인 → 대조.** | 새 쓰기 거부에 더해 **진행 중 쓰기의 종료·닫힘과 공통 잠금**이 필요합니다. CLI 밖의 편집도 봉인 경계에 포함해야 합니다. | 잠금 해제 시점과 후속 쓰기의 새 세대 처리. DPM·Owner 확인 기록을 봉인된 자료에 덧붙이면 지문이 깨지므로 별도 이력에 남겨야 합니다. |
| **검증된 백업 실물 → 참조값.** | 코드에서는 백업을 검증한 `archive/bundle` 대신 **가변 `work`에서 다시 복사**합니다. 또한 `seal_problems`·`backup_problems`가 있어도 참조 블록을 만듭니다. 운영 절차에서는 어느 단계든 실패하면 완료 참조 발행을 중단해야 합니다. | 부분 복사본과 완료본 구분, 용량 부족·전원 장애 후 재개 규칙, 저장 완료의 내구성 기준. 단순 재읽기 성공만으로 전원 장애 후 생존이 입증되지는 않습니다. |
| **PR에서 참조값을 검토하고 DPM 승인 후 머지.** | **PR 본문은 Git 커밋에 자동 보존되지 않습니다.** Git에 참조를 남기려면 추적되는 참조 파일 등의 고정 기록이 필요합니다. PR 본문만을 복원의 유일한 출발점으로 삼으면 안 됩니다. | 승인 대상을 **`repo/PR + 최종 head + bundle_id + manifest_sha256`**에 연결하고, 머지 직전 일치 여부를 재확인하는 조건. 자료·참조가 바뀌면 기존 승인을 그대로 적용하지 않아야 합니다. |
| **머지 결과를 나중에 INDEX에 연결.** | “PR 본문에 머지 해시를 넣으면 순환”은 과도한 설명입니다. 순환은 **그 커밋 자체에 자기 해시를 넣을 때** 생깁니다. 머지 뒤 PR 본문·외부 INDEX에 쓰는 것은 순환하지 않습니다. [P2 원문][p2]도 전자만 지적했습니다. | `merge_method`와 **실제 main 반영 결과 commit**. rebase merge에는 merge commit이 없고 squash도 별도 결과 SHA가 생깁니다. 머지 전의 시험용 merge SHA를 확정값으로 쓰면 안 됩니다. |
| **머지 → INDEX → Owner 확인.** | INDEX 기록 실패를 “미머지”로 처리하면 안 됩니다. 실제 머지 결과를 확인해 **누락된 연결만 재작성**해야 합니다. | INDEX·승인·머지 결과·Owner 확인 기록의 백업, 중복 재시도 처리. `MERGED` 여부와 Owner 확인 여부도 별개로 보존해야 합니다. |
| **샘플의 5종 변경 탐지는 유효.** | **복원 0.017초는 검증을 제외한 복사 시간**입니다. “봉인 뒤 일지 추가”도 쓰기 허용한 **복원본**에 추가한 시험이므로 봉인본 쓰기 차단의 증거는 아닙니다. | 저장한 PR 블록을 다시 읽어 `backup` ID를 해석하고 그 안의 지문으로 복원하는 경로는 미시험입니다. 코드에서는 메모리의 참조·기존 지문 변수·별도 백업 경로를 사용했습니다. [실측 코드][bench] |

참조 파일을 Git에 추가하면 head가 달라집니다. 이 방식을 택한다면 `source_commit`은 **참조 파일 추가 전의 코드 기준 SHA**, 최종 승인 head는 별도 승인·머지 기록으로 구분해야 자기 참조 문제가 재발하지 않습니다. **[추정, 2026-10-18]**

공식 근거상 Git 저장소 백업과 GitHub 메타데이터 백업은 구분되며, PR 본문은 수정 가능한 필드입니다. GitHub는 머지 시 기대 head SHA를 검사하는 기능과 머지 방식별 결과 SHA의 의미도 명시합니다. Windows의 버퍼 기록 역시 별도 내구성 경계입니다. **[공식 문서, 확인 2026-10-18]** ([docs.github.com](https://docs.github.com/en/repositories/archiving-a-github-repository/backing-up-a-repository?utm_source=chatgpt.com), [docs.github.com](https://docs.github.com/en/rest/pulls/pulls?utm_source=chatgpt.com), [docs.github.com](https://docs.github.com/en/rest/pulls/pulls?utm_source=chatgpt.com), [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers?utm_source=chatgpt.com))

## Q3. 브랜치 묶음에서 놓치기 쉬운 경우

아래 처리 방식은 **[추정, 2026-10-18]**입니다.

| 맞음 | 고칠 것 | 빠진 것 |
|---|---|---|
| **리베이스·force push:** 이전 봉인본 보존. | 새 head에는 새 봉인 세대·참조·승인을 연결합니다. 이전 봉인본의 `source_commit`을 수정하지 않습니다. | 구 head도 다시 열어야 한다면 **Git 객체를 유지하는 보존 ref 또는 독립 백업**이 필요합니다. SHA 문자열만으로 객체가 보존되지는 않습니다. |
| **브랜치 이름 변경:** 같은 작업으로 추적 가능. | 봉인 ID와 과거 아카이브 경로는 유지하고 이름 변경 이력만 추가합니다. | 이전 이름·새 이름과 불변 작업 ID의 연결. |
| **같은 브랜치의 두 번째 PR:** 첫 PR 묶음 보존. | PR·봉인 세대를 구분합니다. 후속 PR의 자료를 첫 PR 아카이브에 덧붙이지 않습니다. | 이전 자료까지 포함한 전체 묶음인지 범위를 명시. squash 후 같은 브랜치를 계속 쓰면 이전 커밋이 후속 PR에 다시 나타날 수 있다는 Git 이력 문제도 있습니다. |
| **revert된 머지:** 자료를 지우지 않음. | **“머지 안 됨”으로 바꾸면 틀립니다.** 원래 `MERGED` 사실과 `revert_commit`·되돌림 관계를 함께 남깁니다. | 부분 revert 구분. 묶음 전체가 무효라고 단정하지 않고 CURRENT는 실제 main을 기준으로 판단합니다. |
| **머지 없이 닫은 PR:** 봉인본 보존. | `CLOSED_UNMERGED` 등으로 구분하고 main CURRENT에 포함시키지 않습니다. | 재개 시 이전 봉인본을 재참조하는지, 변경된 자료에 새 세대를 발급하는지 기록. |
| **여러 프로젝트에 걸친 PR:** 공동 작업으로 연결 가능. | 같은 repo라면 프로젝트별 묶음 목록 또는 전체 포함 범위를 명시하고, **모든 대상의 백업·승인**을 확인해야 합니다. | 주관 PLN과 승인 범위. 여러 repo라면 PR도 각각이므로 공동 작업 ID와 부분 완료 상태가 필요합니다. |

squash 후 브랜치 재사용 문제와 rebase merge의 새 SHA 생성은 공식 문서에 명시되어 있습니다. 또한 **간접 머지로도 PR이 `merged`가 될 수 있으므로, 그 상태만으로 DPM 승인이 있었다고 추론하면 안 됩니다.** **[공식 문서, 확인 2026-10-18]** ([docs.github.com](https://docs.github.com/en/pull-requests/reference/pull-request-merges?utm_source=chatgpt.com))

## Q4. 외부 서비스 없는 백업 위치

[P2 Q2][p2]와 겹치는 제품 비교는 생략하고, 위치별 위험만 정리합니다. 아래 적합성 판단은 **[추정, 2026-10-18]**입니다.

| 맞음 | 고칠 것 | 빠진 것 |
|---|---|---|
| **같은 PC의 다른 물리 디스크:** 원본 디스크 한 개의 고장 대비에 유효. | 다른 파티션·폴더를 다른 디스크와 같게 취급하면 안 됩니다. | 전원·OS·오삭제·랜섬웨어·PC 도난/화재는 함께 영향을 줄 수 있습니다. |
| **외장 디스크:** 분리해 두면 PC에서 발생한 손상의 전파를 줄일 수 있음. | 계속 연결해 둔 사본을 오프라인 사본으로 세면 안 됩니다. | 분실·매체 고장·백업 지연·복사 중 분리. 드라이브 문자 변경에도 찾을 수 있는 매체 식별과 경로 대응이 필요합니다. |
| **별도 로컬 Git:** 판본 보존 수단으로는 가능. | **Git은 물리 위치가 아닙니다.** 참조만 복사하면 실물 백업이 아니며, 본문을 넣으려면 “Git에는 참조만” 조건의 적용 범위에 예외가 필요합니다. | 실제 저장 매체, 원본과의 공유 객체 의존, 필요한 객체의 보존 ref, 줄바꿈·필터 변환과 메타데이터 손실. |
| **다른 기기:** PC 전체 고장에 대비하는 별도 사본이 될 수 있음. | 동기화만으로 백업 완료라고 보면 안 됩니다. 덮어쓰기·손상도 전달될 수 있습니다. | 연결이 끊긴 동안의 미백업 구간, 상시 쓰기 공유의 전파 위험, 같은 장소의 화재·도난, 목적지에서의 검증 완료 기록. |

로컬 Git의 공유 객체 의존과 참조가 끊긴 객체의 제거 위험, Git의 줄바꿈 변환은 공식 문서로 확인됩니다. **[공식 문서, 확인 2026-10-18]** ([git-scm.com](https://git-scm.com/docs/git-clone?utm_source=chatgpt.com), [git-scm.com](https://git-scm.com/docs/gitattributes?utm_source=chatgpt.com))

**모든 선택지에 공통으로 빠진 것은** `MANIFEST.tsv`, 고정 참조값, `archive/INDEX`, 백업 위치 ID→실제 매체·경로 대응표의 함께 보존입니다. PR 전 작업 자료의 백업 간격, 오래된 사본의 재검증, **무삭제 누적에 따른 용량 부족 시 중단 기준**도 필요합니다. 디스크 한 개 고장만 대비한다면 다른 물리 디스크가 조건에 맞고, PC 전체 손실까지 대비하려면 분리한 외장 디스크나 다른 기기의 사본이 필요합니다. **[추정, 2026-10-18]**

[draft]: https://github.com/AofSpds/aaaNew/blob/99952a8b3f8d9c78554b56b512e639c02ef33f07/projects/mem_strg/rsch/research/operations/BACKUP_RESTORE_REFERENCE_CLAUDE.md
[bench]: https://github.com/AofSpds/aaaNew/blob/99952a8b3f8d9c78554b56b512e639c02ef33f07/projects/mem_strg/rsch/research/operations/backup_restore_bench.py
[results]: https://github.com/AofSpds/aaaNew/blob/99952a8b3f8d9c78554b56b512e639c02ef33f07/projects/mem_strg/rsch/research/operations/backup_restore_results_20261018.json
[p2]: https://github.com/AofSpds/aaaNew/blob/99952a8b3f8d9c78554b56b512e639c02ef33f07/projects/mem_strg/rsch/research/operations/OPERATIONS_RESPONSE_GPT_PRO.md