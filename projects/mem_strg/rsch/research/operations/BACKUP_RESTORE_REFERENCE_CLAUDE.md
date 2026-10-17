# 참조값과 백업·복원 — 초벌안 v0.2 (S5)

- 작성: 2026-10-18, AAA_NEW/MEM_STRG/RSCH · 상태: **초벌 v0.2**. 설계 확정이 아닙니다.
- 바뀐 근거:
  - Pro 검토 [BACKUP_RESTORE_REVIEW_RESPONSE_GPT_PRO](BACKUP_RESTORE_REVIEW_RESPONSE_GPT_PRO.md)
  - Owner 결정(작업 흐름, 백업 위치, 저장소 위치, 기기 운용)
- 지난 판: v0.1은 커밋 `99952a8`에 있습니다(이 파일의 이전 판).
- 실측:
  - [backup_restore_bench_v2.py](backup_restore_bench_v2.py), [결과](backup_restore_v2_results_20261018.json)
  - v1 [backup_restore_bench.py](backup_restore_bench.py)는 결함 비교용으로 남겨 둡니다.

## 0. 전제 (Owner 결정, 2026-10-18)

- 사람 개발팀처럼 일합니다.
  - 작업 단위마다 Git 브랜치를 땁니다.
  - 역할별 자료(메모·시험 자료·산출물)는 **그대로** 자료 저장소에 보관합니다.
  - 도메인 Git에는 참조값만 둡니다.
- PR은 그 프로젝트를 주관하는 PLN이 DPM 승인을 받아 머지합니다. 머지된 main이 도메인 CURRENT이고, Owner가 최종 확인합니다.
- 자료는 작업 브랜치 단위로 묶고, PR 머지 때 봉인해 아카이브로 보냅니다.
- 자료 저장소: `C:\Users\ms1pk\memstore\` (store_id `memstore-01`)
- 저장소에 직접 쓰는 기기는 HANAL 하나입니다. 다른 기기는 원격으로 붙습니다.
- 백업은 세 곳입니다.
  - E:\MEMSTORE_BACKUP (1차)
  - K:\MEMSTORE_BACKUP (2차)
  - Google Drive (localComputer desktop-care, PC 밖 사본)
- 지우지 않습니다. 키·시크릿을 두지 않습니다.

## 1. v0.1에서 바뀐 것

| # | 항목 | v0.1 | v0.2 | 근거 |
| --- | --- | --- | --- | --- |
| 1 | 참조값을 두는 곳 | PR 본문 | **Git이 추적하는 참조 파일**(`.memstore-ref`). PR 본문에는 사본만 | PR 본문은 Git에 남지 않고 나중에 고칠 수 있음 (Pro Q2) |
| 2 | 묶음 이름 | `<브랜치>@<head 7자>` | **봉인 번호 seal_id** = UTC 시각 + 임의 6자. 폴더 이름도 seal_id. bundle_id는 설명용 | 같은 head에서 자료만 바뀌면 이름이 겹침. `/`→`__` 치환도 충돌 (Pro Q1) |
| 3 | 실패할 때 | 문제가 있어도 다음 단계로 감 | **어느 단계든 대조가 실패하면 멈추고 참조 파일을 만들지 않음** | Pro Q2. v1 코드 결함 |
| 4 | 백업 원본 | 아직 바뀔 수 있는 작업 폴더에서 다시 복사 | **대조를 마친 봉인본에서** 복사하고 fsync | Pro Q2. v1 코드 결함 |
| 5 | manifest | 경로·크기·지문만 | **v2**: 머리줄과 형식 버전, 항목 수, 빈 폴더, 경로 규칙, 중복 거부, 0개 표현 | Pro Q1 |
| 6 | 원본 파일 | (규칙 없음) | **바꾸지 않음**. 정해진 형식은 manifest에만 적용(원본의 CRLF 그대로) | "그대로 보관" (Pro Q1) |
| 7 | 머지 기록 | 머지 커밋 해시를 INDEX에 | **실제 main에 반영된 커밋 + 머지 방식**(merge/squash/rebase) | 방식마다 결과 커밋이 다름. "순환" 설명은 과장이었음 (Pro Q2) |
| 8 | 승인 연결 | 없음 | 승인 대상 = PR + 최종 head + seal_id + manifest_sha256. 머지 직전에 같은지 다시 확인 | Pro Q2 |
| 9 | 상태 | "머지 안 됨" 한 가지 | 상태 어휘 9개 (§6) | revert ≠ 머지 안 됨 (Pro Q3) |
| 10 | 복원 | 메모리에 있던 값으로 시험 | **참조 파일만 보고**, 위치 표식(LOCATION.txt)으로 백업을 찾아 복원. 걸린 시간에 대조 포함 | Pro Q2 |
| 11 | 백업 위치 | 미정 | E:·K:·Google Drive (§7) | Owner 결정 |

## 2. 참조 파일 (Git이 추적)

- 위치: 도메인 저장소의 `memstore-refs/<seal_id>.memstore-ref` (프로젝트 폴더 아래)
- 작업 브랜치에 커밋해서 PR에 함께 들어가게 합니다. PR 본문에는 같은 내용을 사본으로 붙입니다.
- `source_commit`은 **참조 파일을 넣기 전의 브랜치 head**입니다. 자기 자신을 가리키는 순환을 피하기 위해서입니다.
- 실측 예 (시험 값):

```text
format: MEMSTORE-REF v2
store_id: memstore-01
seal_id: 20261017T181541Z-f47fec
bundle_id: rhs/order/feat-f3
source_commit: a1b2c3d4e5f60718293a4b5c6d7e8f9012345678
sealed_at_utc: 20261017T181541Z
device_id: HANAL
roles: pln,pmo,rsch
files: 21
manifest_sha256: b3003c4bbbd16bb9e9f705ef19889d396de62e0b275e606bc84a11f122f286fa
backups: hdd-e-primary,hdd-k-secondary
```

- `sealed_by`(PLN 세션 이름)와 승인 기록은 봉인된 자료가 아니라 **별도 이력**(archive INDEX)에 남깁니다. 봉인본에 덧붙이면 지문이 깨지기 때문입니다.

## 3. manifest v2 규칙

```text
MEMSTORE-MANIFEST v2
seal_id<TAB><seal_id>
bundle_id<TAB><bundle_id>
entries<TAB><항목 수>
D<TAB><빈 폴더 경로>
F<TAB><파일 경로><TAB><바이트><TAB><sha256>
```

- 형식: UTF-8, BOM 없음, LF, 마지막 줄 뒤에도 LF
- 정렬: 경로의 UTF-8 바이트 순서
- 0개 묶음은 `entries 0`이고 그 아래 줄이 없습니다(실측 통과).
- 경로 규칙: 다음 중 하나라도 있으면 **봉인 거부**입니다.
  - 구분자가 `/`가 아님, 절대경로·드라이브·`.`·`..`·역슬래시
  - 제어 문자(TAB·CR·LF 포함), Windows 금지 문자(`<>:"|?*`)
  - 예약 이름(CON·AUX·COM1 등), 끝이 점이나 공백
  - 대소문자만 다른 두 이름
- 심볼릭 링크와 junction(재분석 지점)이 있으면 봉인을 멈춥니다.
- 보존 범위: **파일 내용과 이름, 빈 폴더**만 보존합니다. ACL, 소유권, ADS, 시각, 하드링크 관계는 보존하지 않습니다(명시).
- manifest를 읽을 때 지문, 문법, 중복 경로, 항목 수를 먼저 검사한 뒤 복사합니다.

## 4. PR 때 고정 절차 (PLN)

1. **쓰기 잠그기**: 그 브랜치 묶음의 역할 스트림 잠금을 정해진 순서로 모두 잡습니다. 진행 중인 쓰기가 끝나기를 기다립니다. CLI 밖에서 직접 고친 것도 이 경계 안에 포함됩니다.
2. **검사 → manifest v2**: 경로 규칙과 링크를 검사합니다. 하나라도 걸리면 멈춥니다.
3. **봉인본**: `archive/<store_id>/seals/<seal_id>/`에 복사하고 fsync한 뒤 대조합니다. 통과하면 읽기 전용으로 표시합니다.
4. **1차 백업 E:**: 봉인본에서 복사하고 fsync한 뒤 대조합니다. 통과하면 읽기 전용으로 표시합니다.
5. **2차 백업 K:**: 4와 같습니다.
6. **참조 파일**: 브랜치에 커밋합니다. 1–5가 모두 통과했을 때만 만듭니다. PR 본문에 사본을 붙입니다.
7. **DPM 승인**: 승인 대상은 PR, 최종 head, seal_id, manifest_sha256입니다. 자료나 참조가 바뀌면 기존 승인은 쓰지 않습니다.
8. **PLN 머지**: 머지하기 직전에 head가 승인한 head와 같은지 확인합니다(GitHub의 기대 head 검사).
9. **INDEX 기록**: `MERGED`, 실제 main 반영 커밋, 머지 방식을 적습니다. 그다음 Owner 확인을 표시합니다. INDEX 기록이 실패해도 "머지 안 됨"으로 바꾸지 않고, 빠진 연결만 다시 씁니다.
10. **Google Drive**: desktop-care가 정해진 시각에 저장소 폴더 전체를 백업합니다(보호 목록에 넣은 뒤).

- 중간에 멈추면 이미 만든 봉인본과 백업은 지우지 않고 `INCOMPLETE`로 남깁니다. 다시 할 때는 새 seal_id를 씁니다.
- 용량: 백업 위치의 빈 공간이 10% 또는 100GB 아래이면 봉인하지 않고 보고합니다. 정리는 Owner가 결정합니다.

## 5. 복원 절차

1. Git에서 참조 파일(`.memstore-ref`)을 읽습니다.
2. `backups`에 적힌 위치 ID를 차례로, 드라이브마다 `MEMSTORE_BACKUP\LOCATION.txt` 표식으로 찾습니다. 드라이브 문자가 바뀌어도 찾을 수 있습니다(실측).
3. 그 위치의 manifest 지문이 참조 파일과 같은지 봅니다. 다르면 다음 위치로 넘어갑니다.
4. **빈 새 폴더**에 복사합니다. 기존 자료를 덮어쓰지 않습니다.
5. 대조합니다: 파일마다 크기와 지문, 누락, 목록에 없는 항목, 빈 폴더
6. 대조가 실패하면 다음 백업 위치로 다시 시도합니다(규칙. v2 코드는 위치를 직접 고르는 방식으로만 시험함).
7. 결과는 "완전 일치(위치 ID)" 또는 "불일치 목록"입니다.

## 6. 상태 어휘와 특별한 경우

상태(INDEX): `SEALED` → `BACKED_UP` → `REF_COMMITTED` → `APPROVED` → `MERGED`. 그 밖에 `REVERTED`, `CLOSED_UNMERGED`, `SUPERSEDED`, `INCOMPLETE`가 있습니다.

| 경우 | 처리 |
| --- | --- |
| 리베이스·force push로 head가 바뀜 | 새로 봉인하고(새 seal_id), 옛 봉인은 `SUPERSEDED`로 보존합니다. 옛 head를 다시 열어야 하면 Git 보존 ref가 필요합니다 |
| 브랜치 이름 변경 | seal_id와 아카이브 경로는 그대로 둡니다. INDEX에 이름 변경만 추가합니다 |
| 같은 브랜치의 두 번째 PR | 새로 봉인합니다. 앞 봉인에 덧붙이지 않습니다 |
| 머지했다가 되돌림 | `MERGED`를 그대로 두고 `REVERTED`와 되돌린 커밋을 추가합니다. CURRENT는 실제 main 기준입니다 |
| 머지 없이 닫힌 PR | `CLOSED_UNMERGED`로 보존합니다. 다시 열면 바뀐 자료는 새로 봉인합니다 |
| 여러 프로젝트에 걸친 PR | 프로젝트마다 봉인하고, 참조 파일에 목록을 적습니다. 모든 대상의 백업과 승인이 끝나야 머지합니다 |
| 다른 경로로 머지됨 | GitHub에서 "merged"여도 DPM 승인이 있었다고 추론하지 않습니다. 승인 기록과 따로 대조합니다 |

## 7. 백업 위치 (결정)

| 위치 ID | 경로 | 역할 | 비고 |
| --- | --- | --- | --- |
| hdd-e-primary | E:\MEMSTORE_BACKUP\ | 1차, 봉인마다 | NTFS, 최근 오류 0 |
| hdd-k-secondary | K:\MEMSTORE_BACKUP\ | 2차, 봉인마다 | exFAT(권한 기능 없음, 읽기 전용 표시만), 최근 오류 0, 항상 연결 |
| gdrive-desktopcare | (desktop-care restic 저장소) | PC 밖 사본, 정기 | localComputer에 보호 목록 추가를 요청할 예정 |

- 같은 위치 폴더에 manifest, 참조 파일 사본, INDEX, LOCATION 표식을 함께 둡니다.

## 8. 실측 v2 (HANAL, 시험 자료, 2026-10-18) [실측]

시험 묶음: 역할 3개, 파일 21개, 빈 폴더 1개, 한글 파일명, 원본 CRLF. E:와 K:는 임시 폴더에 만든 **가상 드라이브**입니다.

| 시험 | 결과 |
| --- | --- |
| 봉인 + E·K 백업(각각 fsync·대조) | 0.60초, 통과 |
| 참조 파일만 보고 E에서 복원 (대조 포함) | 0.11초, 완전 일치 |
| 참조 파일만 보고 K에서 복원 (대조 포함) | 0.11초, 완전 일치 |
| 봉인본에 쓰기 시도 | **막힘** (읽기 전용 표시) |
| K 백업이 대조에 실패하도록 손상 | **봉인 멈춤, 참조 파일 안 만듦** |
| E 백업 1바이트 손상 후 복원 | E에서는 "내용 다름"으로 잡힘, K에서는 정상 복원 |
| 위치 목록 순서를 바꿔도 표식으로 찾기 | 통과 |
| 예약 이름(`AUX.txt.md`) 포함 | 봉인 거부 |
| 빈 묶음 | `entries 0`으로 표현, 대조 통과 |
| manifest에 같은 경로 두 번 | 거부 |
| 원본 CRLF 보존 | 보존됨 |

## 9. 남은 것 (미실측·미정)

- 전원 장애, 큰 자료(수백 MB 이상), 실제 E:·K:·GitHub PR과의 연결은 시험하지 않았습니다.
- 쓰기 CLI와 역할 스트림 잠금은 아직 구현되지 않았습니다. §4-1은 설계입니다.
- 복원할 때 대조에 실패하면 다음 위치로 자동 재시도하는 부분은 규칙만 있습니다(코드 미구현).
- desktop-care 보호 목록 추가는 localComputer Codex 세션에 알리는 중입니다(대기열에 넣었으나 아직 전달 안 됨).
- 승인 기록(DPM·Owner)의 형식과 위치는 정하지 않았습니다.
- 아카이브 INDEX의 칸과 이름 규칙은 아카이브 단계(S4)에서 정합니다.
- "읽기 전용 표시"는 실수를 막는 장치이고 보안 장치가 아닙니다. 같은 Windows 사용자는 표시를 풀 수 있습니다.
