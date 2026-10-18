# GitHub Flow 가이드

> Claude Code에서 GitHub 이슈/PR/백로그를 운영하는 표준 절차.
> 이 가이드를 `~/CLAUDE.md`와 프로젝트 `CLAUDE.md`에 적용하면 모든 프로젝트에서 일관된 GitHub Flow를 사용할 수 있다.

---

## 적용 방법

### 1단계: `~/CLAUDE.md`에 공통 규칙 추가

아래 "공통 규칙 (~/CLAUDE.md용)" 섹션을 `~/CLAUDE.md`에 복사한다. 모든 프로젝트에 자동 적용된다.

### 2단계: 프로젝트 `CLAUDE.md`에 프로젝트별 규칙 추가

백로그-이슈 연동이 필요한 프로젝트에만 "프로젝트별 규칙 (CLAUDE.md용)" 섹션을 복사한다.

### 3단계: 백로그 파일 생성

`devflow-docs/backlog.md` 파일을 "백로그 템플릿"에서 복사하여 생성한다.

### (선택) GitHub 이슈 연동 활성화

프로젝트 `CLAUDE.md`에 `<!-- github-issues: enabled -->` 설정을 추가하면 GitHub 이슈 자동 생성/연결이 활성화된다. 기본값은 disabled (파일 기반 백로그만 운영).

---

## 공통 규칙 (~/CLAUDE.md용)

아래를 `~/CLAUDE.md`의 적절한 위치에 추가한다.

```markdown
## GitHub Flow

### gh CLI 사용

GitHub 작업은 모두 `gh` CLI로 수행한다. MCP GitHub 도구는 사용하지 않는다.

### 커밋 메시지

- Conventional Commits 형식: `feat:`, `fix:`, `chore:`, `docs:`
- 이슈 연결: 진행 중 `refs #N`, 완료 시 `closes #N`
- HEREDOC으로 멀티라인 메시지 작성
- Co-Authored-By 포함

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
```

---

## 프로젝트별 규칙 (CLAUDE.md용)

백로그 관리가 필요한 프로젝트에 아래를 추가한다. `[owner/repo]`를 실제 값으로 교체.

```markdown
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
- GitHub 이슈를 `enhancement` 라벨로 동시 생성 (`[owner/repo]`)
- 백로그에 이슈 번호와 링크 기록

**백로그 구현 시:**
1. **커밋 메시지에 이슈 번호 포함**
   - 진행 중: `refs #N`
   - 완료 시: `closes #N` (머지 시 이슈 자동 클로즈)

2. **GitHub 이슈에 진행 코멘트 남기기**
   - 구현 시작 시: 간략한 접근 방식 코멘트
   - 커밋 완료 시: 변경 내용 요약 + 커밋 해시 코멘트

3. **백로그 파일 정리**
   - 구현 완료 시 `devflow-docs/backlog.md`에서 해당 항목 제거
```

---

## 백로그 템플릿

`devflow-docs/backlog.md`로 저장한다.

```markdown
# Backlog

> **완료 항목 조회 방법:**
> - GitHub: `is:issue is:closed` 필터
> - Claude: "완료된 백로그 항목 보여줘" 요청 (git history 검색)

---

## Next

(즉시 착수할 3-5건)
- **BL-001**: [제목] [P1] [#N](https://github.com/[owner/repo]/issues/N)

---

## Open

(확인된 개선사항)
- **BL-002**: [제목] [P2] [#N](https://github.com/[owner/repo]/issues/N)

---

## Someday

(아이디어 단계)
- **BL-003**: [제목] [P3] [#N](https://github.com/[owner/repo]/issues/N)
```

### 백로그 항목 형식

각 항목은 **1줄**로 작성한다: `- **BL-NNN**: [제목] [Px] [#N](link)`

상세 정보가 필요한 경우 GitHub 이슈에 기록한다 (github-issues: enabled일 때).

### 우선순위 기준

| 우선순위 | 기준 |
|---------|------|
| P0 | 즉시 수정 — 동작 불가, 보안 이슈, 다른 작업 차단 |
| P1 | 수정 권장 — 품질/UX에 영향, 합리적 시일 내 처리 |
| P2 | 개선 가능 — 있으면 좋지만 긴급하지 않음 |
| P3 | 장기 — 언젠가 하면 좋을 것 |

---

## 전체 워크플로우 요약

```
1. 작업 발견
   └→ 백로그 파일에 항목 추가 + GitHub 이슈 생성 (동시)

2. 구현 시작
   └→ 이슈에 시작 코멘트
   └→ git checkout -b [type]/[topic]

3. 구현 완료
   └→ 변경 전 영향도 확인 (Grep)
   └→ 테스트 통과 확인
   └→ git commit -m "feat: [제목] (refs #N)"
   └→ git push -u origin [branch]

4. PR 생성
   └→ gh pr create --body "Closes #N ..."
   └→ body 첫 줄에 Closes #N (필수)

5. 머지
   └→ gh pr merge [N] --squash --delete-branch
   └→ git checkout main && git pull

6. 동기화
   └→ 백로그에서 완료 항목 제거
```

---

## 이슈 클로즈 (구현 없이 닫는 경우)

```bash
gh issue close [N] --repo [owner/repo] \
  --reason "not planned" \
  --comment "[클로즈 사유]"
```

백로그에서도 해당 항목을 제거한다.
