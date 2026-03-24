# Codex 이관 논의 요약

이 문서는 aidlc-devflow를 Codex에서 사용하기 위해 지금까지 합의한 내용을 빠르게 재확인하기 위한 요약이다.

## 1) 저장소 동기화

- 소스: `bluejayA/aidlc-devflow`
- 타겟: `kt-cloud-ai/ktc-ai-dlc-bluejayA`
- `v1.3.0` 태그는 타겟으로 복사 완료
- 타겟 `main`은 소스 `main`과 SHA 일치 상태로 동기화 완료

## 2) 자동 동기화 전략

- 트리거: 새 태그(`v*`) 생성 시
- 동작: 타겟 저장소에 `main` + 생성된 태그를 함께 동기화
- 인증: PAT 대신 GitHub App 토큰 방식 사용
- 필요한 Secrets:
  - `SYNC_APP_ID`
  - `SYNC_APP_PRIVATE_KEY`

관련 워크플로우 파일:
- `.github/workflows/sync-target-on-tag.yml`

## 3) Codex 포팅 핵심

- Claude 전용 엔트리(`.claude-plugin`, `hooks`)는 Codex에서 자동 실행되지 않음
- 스킬은 Codex 스킬 디렉터리에 직접 배치해서 사용
- `_shared/...` 경로를 Codex 친화적으로 정규화 필요
- `/aidlc:...` 문법은 Codex 호출 방식으로 변환 필요

## 4) 포팅 산출물

- 체크리스트: `docs/guide/codex-porting-checklist.md`
- 자동 변환 스크립트: `scripts/port_to_codex.py`

실행 예:

```bash
python3 scripts/port_to_codex.py --root .
python3 scripts/port_to_codex.py --root . --apply
```

## 5) 실사용 호출 원칙

- 시작: `$aidlc-using-devflow`
- 디버깅: `$aidlc-systematic-debugging`
- 완료 전 검증: `$aidlc-verification-before-completion`
- 리뷰: `$aidlc-requesting-code-review`
- 마무리: `$aidlc-finishing-a-development-branch`

## 6) 다음 권장 액션

1. 이 문서와 체크리스트를 소스 저장소에 커밋/PR
2. Codex 설치 스크립트(`install_codex_pack.sh`) 추가
3. 샘플 프로젝트에서 1회 end-to-end 리허설
