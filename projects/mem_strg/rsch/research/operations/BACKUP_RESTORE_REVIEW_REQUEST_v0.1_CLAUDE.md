# 외주 검토 의뢰서 — 참조값과 백업·복원 초벌안 (v0.1)

- 상태: **초안. 입력 링크는 커밋 뒤에 채웁니다(`<COMMIT>`). 아직 보내지 않음.**
- 작성: 2026-10-18, AAA/NEW/RSCH/MEM_STRG
- 성격: 조사 의뢰가 아니라 **검토 의뢰**입니다. 조사는 이전 P2 답에서 받았습니다.

---

아래가 Pro 챗에 보낼 본문입니다.

```text
ACT_ID: MEM_STRG-PRO-P3-BACKUP-RESTORE-REVIEW-20261018-001
의뢰자: Owner (작성: aaaNew 연구 채널 AAA/NEW/RSCH/MEM_STRG)
입력 커밋: AofSpds/aaaNew@<COMMIT> (아래 링크는 모두 이 커밋에 고정. main 최신을 읽지 말 것)
답변 언어: 한국어. 식별자는 원문 그대로.
성격: 검토 의뢰. 새 조사를 넓히지 말고, 아래 초벌안의 틀린 점·빠진 위험만 짚어 주세요. 한 번에 끝냅니다.

## 1. 전제 (Owner가 정한 작업 방식, 2026-10-18)
- 사람 개발팀처럼 일한다. 작업 단위마다 Git 브랜치를 딴다.
- 역할(PLN·PMO·RSCH 등)별로 모은 자료(메모·시험 자료·산출물)는 그대로 로컬 "자료 저장소"에 보관한다. Git에는 참조값만 둔다.
- PR은 그 프로젝트를 주관하는 PLN이 DPM 승인을 받아 머지한다. 머지된 main이 도메인 CURRENT다. Owner가 최종 확인한다.
- 자료는 작업 브랜치 단위로 묶고, PR 머지 때 고정해 아카이브로 보낸다.
- 아무것도 지우지 않는다. 외부 서비스는 지양한다. 키·시크릿은 쓰지 않는다. Windows 11.

## 2. 초벌안 요지 (상세는 §5 링크)
- 묶음 = work/<브랜치>/<역할>/ 전체.
- manifest = 파일마다 "상대경로 ⇥ 크기 ⇥ sha256" 한 줄(경로순, UTF-8·LF).
- 참조값(PR 본문): format, store_id, bundle_id(<도메인>/<프로젝트>/<브랜치>@<head7>), sealed_by, source_commit(브랜치 head), roles, files, bytes, manifest_sha256, backup(위치 ID).
- 머지 커밋 해시는 참조값에 넣지 않는다(순환 방지). 머지 뒤 archive/INDEX에 "머지 커밋 → bundle_id"를 추가한다.
- PR 때 고정 절차: 쓰기 막기 → manifest → 봉인 사본(읽기 전용) → 다시 대조 → 백업 복사·대조(실물 먼저) → PR에 참조값(참조 나중) → DPM 승인 → 머지 → INDEX → Owner 확인.
- 복원: 참조값 → 백업에서 묶음 찾기 → 빈 새 폴더에 복사 → manifest 지문·파일별 크기·지문·누락·추가 대조.

## 3. 우리 실측 (HANAL, 시험 자료)
- 역할 3개, 파일 21개, 336,837바이트
- 봉인+백업 0.37초. 빈 폴더 복원 0.02초, 완전 일치.
- 일부러 넣은 고장 5가지가 모두 잡혔다: 1바이트 변경, 파일 누락, 파일 추가, 봉인 뒤 일지 한 줄 추가, manifest 바꿔치기.
- 시험하지 않은 것: 큰 자료, 다른 디스크 백업, 쓰는 도중 봉인, 전원 장애, 실제 Git PR 연결.

## 4. 질문
Q1. 참조값 블록과 manifest 규칙에 빠진 칸이나 위험이 있는가. (예: 빈 폴더·심볼릭 링크·대소문자·줄바꿈 처리, 경로 정규화)
Q2. 고정 절차의 순서(실물 먼저 → 참조 나중, 머지 커밋은 INDEX로)가 맞는가. 고칠 순서가 있으면 이유와 함께.
Q3. 브랜치 묶음 방식에서 놓치기 쉬운 경우와 처리 방법.
    · 리베이스·force push로 head가 바뀜
    · 브랜치 이름 변경
    · 같은 브랜치의 두 번째 PR
    · 되돌린(revert) 머지, 머지 안 하고 닫은 PR
    · 하나의 PR이 여러 프로젝트에 걸침
Q4. 외부 서비스 없이 쓸 수 있는 백업 실물 위치의 선택지와 각각의 위험 (같은 PC 다른 디스크 / 외장 디스크 / 별도 로컬 Git / 다른 기기). 이전 P2 답 Q2와 겹치면 결론만.

## 5. 입력 자료 (커밋 <COMMIT> 고정)
- 초벌안: https://github.com/AofSpds/aaaNew/blob/<COMMIT>/projects/mem_strg/rsch/research/operations/BACKUP_RESTORE_REFERENCE_CLAUDE.md
- 실측 스크립트: https://github.com/AofSpds/aaaNew/blob/<COMMIT>/projects/mem_strg/rsch/research/operations/backup_restore_bench.py
- 실측 결과: https://github.com/AofSpds/aaaNew/blob/<COMMIT>/projects/mem_strg/rsch/research/operations/backup_restore_results_20261018.json
- 참고(이전 P2 답): https://github.com/AofSpds/aaaNew/blob/<COMMIT>/projects/mem_strg/rsch/research/operations/OPERATIONS_RESPONSE_GPT_PRO.md

## 6. 하지 말 것
- 특정 제품을 채택한다고 결정하지 않는다.
- 우리 저장소에 쓰지 않는다. 실행·설치를 요구하지 않는다.

## 7. 답변 형식
- 질문마다 3칸: 맞음 / 고칠 것 / 빠진 것
- 근거 등급과 날짜를 붙인다: [공식 문서] [논문] [저장소·릴리스] [2차 출처] [추정]
- 짧게. 전체를 한 번에 끝낸다.
```
