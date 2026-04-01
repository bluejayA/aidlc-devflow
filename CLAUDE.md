# aidlc-devflow 프로젝트 규칙

## GitHub Flow (필수)

### gh CLI 사용
GitHub 작업은 모두 `gh` CLI로 수행한다. MCP GitHub 도구는 사용하지 않는다.

### 커밋 메시지
- Conventional Commits 형식: `feat:`, `fix:`, `chore:`, `docs:`
- 이슈 연결: 진행 중 `refs #N`, 완료 시 `closes #N`
- HEREDOC으로 멀티라인 메시지 작성

### PR 생성 규칙
- **body 첫 줄에 `Closes #N`** — 타이틀에만 넣으면 GitHub에서 이슈 연결이 안 됨
- Summary + Test plan 포함
- 테스트 통과 확인 후 PR 생성
- 승인 없이 push/merge 금지

### 수정 전 영향도 확인
코드를 변경하기 전에 다음을 확인한다:
1. 변경하려는 텍스트/키워드를 다른 파일에서 참조하는지 Grep으로 확인
2. 핵심 특성 키워드(TDD, Review 등)를 삭제하는 경우, 의도적인지 재확인
3. 출력 경로(output_path 등) 변경 시, 하류에서 해당 경로를 참조하지 않는지 확인

---

## 백로그 관리

### 백로그 파일
- 위치: `devflow-docs/backlog.md`
- 구조: Next (3-5건) / Open / Someday
- Done 항목은 파일에서 제거 (git history로 추적)

### GitHub 이슈 연동
<!-- github-issues: enabled -->
> 아래 규칙은 `github-issues: enabled`일 때만 적용한다.
> disabled일 때는 `devflow-docs/backlog.md` 파일 기반으로만 운영한다.

**백로그 등록 시:**
- `devflow-docs/backlog.md`에 항목 추가
- GitHub 이슈를 `enhancement` 라벨로 동시 생성 (`bluejayA/aidlc-devflow`)
- 백로그에 이슈 번호와 링크 기록

**백로그 구현 시:**
백로그 항목을 구현하여 커밋할 때, 연결된 GitHub 이슈와 반드시 연동한다.

1. **커밋 메시지에 이슈 번호 포함**
   - 진행 중: `refs #N`
   - 완료 시: `closes #N` (머지 시 이슈 자동 클로즈)
   - 예: `feat: workspace-detection에 사용자 질문 분기 추가 (closes #1)`

2. **GitHub 이슈에 진행 코멘트 남기기**
   - 구현 시작 시: 간략한 접근 방식 코멘트
   - 커밋 완료 시: 변경 내용 요약 + 커밋 해시 코멘트

3. **백로그 파일 정리**
   - 구현 완료 시 `devflow-docs/backlog.md`에서 해당 항목 제거
