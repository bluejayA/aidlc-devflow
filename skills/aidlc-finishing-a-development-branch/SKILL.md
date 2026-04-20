---
name: aidlc-finishing-a-development-branch
description: |
  구현이 완료되고 모든 테스트가 통과한 후, 개발 브랜치를 머지, PR, 유지, 폐기 중 어떻게 처리할지 결정할 때 사용.
  Use when implementation is done and all tests pass, and a decision is needed on what to do with the development branch — merge, PR, keep, or discard.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
  skill_nature: null
  lifecycle: active
---

# aidlc-finishing-a-development-branch

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 개발 브랜치 마무리: 병합, PR, 유지, 폐기 중 하나를 선택 -->

## Trigger

다음 상황에서 이 스킬을 실행한다:

- 구현이 완료되고 모든 테스트가 통과했을 때
- "브랜치를 어떻게 할까요?"라는 질문을 받았을 때
- AI-DLC `aidlc-build-and-test` 단계가 완료되었을 때
- 기능 개발 또는 버그 수정 작업이 완전히 마무리되었을 때

---

## Purpose

개발이 완료된 브랜치의 다음 행동을 명확하게 결정하고, 선택에 따라 안전하게 실행한다.
불명확한 상태(완료됐지만 아무것도 안 한 브랜치)를 남기지 않는다.

---

## 프로세스

### 1단계: 테스트 검증

브랜치 처리 전에 반드시 검증이 완료되어야 한다.

`aidlc-verification-before-completion` 스킬 사용을 권장한다.
이미 검증이 완료된 경우 현재 상태를 확인한다:

```bash
# 현재 브랜치 및 상태 확인
git status
git log --oneline -5
git branch --show-current
```

검증이 완료되지 않았다면 이 스킬을 중단하고 `aidlc-verification-before-completion`을 먼저 실행한다.

---

### 2단계: 선택지 제시

정확히 4가지 선택지를 제시한다:

```
## 브랜치 처리 선택

현재 브랜치: [branch-name]
베이스 브랜치: [base-branch]
변경사항: [X commits, Y files changed]

A) 로컬에서 [base-branch]로 병합
   → 브랜치를 로컬에서 병합하고 개발 브랜치를 삭제합니다
   → 워크트리 사용 중이면 워크트리도 제거합니다

B) 푸시 후 Pull Request 생성
   → 원격 저장소에 푸시하고 PR을 생성합니다
   → 코드 리뷰가 필요하거나 팀과 공유할 때 선택합니다

C) 브랜치 유지 (나중에 처리)
   → 현재 상태를 유지하고 나중에 다시 결정합니다
   → 워크트리는 그대로 남습니다

D) 작업 폐기
   → 브랜치와 모든 변경사항을 삭제합니다
   → 취소하려면 'discard'를 직접 입력해야 합니다
```

**선택을 기다린다. 사용자 응답 없이 진행하지 않는다.**

---

### 3단계: 선택에 따른 실행

#### 옵션 A: 로컬 병합

```bash
# 1. 현재 브랜치 확인
git branch --show-current

# 2. 베이스 브랜치로 이동
git checkout [base-branch]

# 3. 병합 실행
git merge --no-ff [branch-name] -m "Merge branch '[branch-name]'"

# 4. 개발 브랜치 삭제
git branch -d [branch-name]
```

워크트리 사용 중인 경우:
```bash
# 워크트리 제거 (옵션 A에서만 실행)
git worktree remove [worktree-path]
git worktree prune
```

완료 메시지:
```
## 병합 완료

병합된 브랜치: [branch-name] → [base-branch]
삭제된 브랜치: [branch-name]
[워크트리 제거: [worktree-path]] (워크트리 사용 시)
```

**백로그 Next 정리 제안**: `devflow-docs/backlog.md`가 존재하면:
```
백로그 Next를 정리할까요?
- 완료된 항목 제거
- Open에서 새 항목 승격

→ "정리" 또는 "건너뛰기"
```
사용자가 "정리"를 선택하면 파일을 열어 함께 정리한다. "건너뛰기"하면 그대로 진행한다.

**Memory Sync Reconciliation** (프로젝트 auto-memory 갱신 필요 여부 확인):

이번 사이클 결과가 auto-memory에 반영돼야 하는지 점검한다. 하나라도 해당되면 "동기화"를 권장한다:

- 완료된 BL/PR 번호가 기존 `project_*.md`의 기록과 달라지는가?
- 진행 우선순위가 바뀌었는가 (Next에서 완료/승격)?
- 이번 세션에서 새로 배운 피드백/제약(사용자 판단 근거, 기각된 대안)이 있는가?

→ "동기화" / "건너뛰기"

"동기화" 선택 시: **현재 repo(cwd)에 매핑되는 프로젝트 auto-memory 디렉토리**(Claude Code 규약상 `~/.claude/projects/<dashed-cwd>/memory/`)의 관련 `project_*.md` 또는 `feedback_*.md`만 업데이트한다. 다른 프로젝트 memory는 건드리지 않는다. auto-memory 시스템이 구성돼 있지 않으면 이 체크는 no-op으로 넘긴다.

> 📌 **관측 요청 (BL-092 L3, ~2026-04-28 T+14까지)**: 이 프롬프트가 표시되면 Jay에게 "Memory Sync Reconciliation 프롬프트 출력됨"을 명시적으로 알리고, issue #177에 `observed (3-1)` 코멘트를 제안. T+14 Phase 2 plan 작성 시 이 hint 제거 예정 (만료 test가 강제).

<!-- @state-update: 옵션 A 완료 → Current Phase를 finished로 -->
**devflow 종료 처리** (devflow-state.md가 존재하는 경우):
1. `devflow-docs/devflow-state.md`의 `## Current Phase`를 `finished`로 업데이트
2. state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동
3. devflow-audit에 로깅: `"Flow finished — option A (local merge)"`

---

#### 옵션 B: Push 후 Pull Request 생성

```bash
# 1. 원격 저장소에 푸시
git push -u origin [branch-name]
```

GitHub CLI로 PR 생성:
```bash
gh pr create \
  --base [base-branch] \
  --title "[PR 제목]" \
  --body "$(cat <<'EOF'
## 변경 사항

[변경 내용 요약]

## 테스트

- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과

## 체크리스트

- [ ] 코드 리뷰 완료
- [ ] 문서 업데이트
EOF
)"
```

완료 메시지:
```
## PR 생성 완료

브랜치: [branch-name]
PR URL: [github-pr-url]
리뷰어에게 공유하거나 직접 병합할 수 있습니다.
워크트리는 PR 머지 전까지 유지됩니다.
devflow는 PR 머지 후 종료 처리됩니다.
```

**워크트리는 PR이 머지될 때까지 유지한다. 이 단계에서 제거하지 않는다.**

**백로그 Next 정리 제안**: `devflow-docs/backlog.md`가 존재하면:
```
백로그 Next를 정리할까요?
- 완료된 항목 제거
- Open에서 새 항목 승격

→ "정리" 또는 "건너뛰기"
```
사용자가 "정리"를 선택하면 파일을 열어 함께 정리한다. "건너뛰기"하면 그대로 진행한다.

**Memory Sync Reconciliation** (프로젝트 auto-memory 갱신 필요 여부 확인):

이번 사이클 결과가 auto-memory에 반영돼야 하는지 점검한다. 하나라도 해당되면 "동기화"를 권장한다:

- 완료된 BL/PR 번호가 기존 `project_*.md`의 기록과 달라지는가?
- 진행 우선순위가 바뀌었는가 (Next에서 완료/승격)?
- 이번 세션에서 새로 배운 피드백/제약(사용자 판단 근거, 기각된 대안)이 있는가?

→ "동기화" / "건너뛰기"

"동기화" 선택 시: **현재 repo(cwd)에 매핑되는 프로젝트 auto-memory 디렉토리**(Claude Code 규약상 `~/.claude/projects/<dashed-cwd>/memory/`)의 관련 `project_*.md` 또는 `feedback_*.md`만 업데이트한다. 다른 프로젝트 memory는 건드리지 않는다. auto-memory 시스템이 구성돼 있지 않으면 이 체크는 no-op으로 넘긴다.

> 📌 **관측 요청 (BL-092 L3, ~2026-04-28 T+14까지)**: 이 프롬프트가 표시되면 Jay에게 "Memory Sync Reconciliation 프롬프트 출력됨"을 명시적으로 알리고, issue #177에 `observed (3-1)` 코멘트를 제안. T+14 Phase 2 plan 작성 시 이 hint 제거 예정 (만료 test가 강제).

<!-- @state-update: 옵션 B PR 생성 → Finishing Choice + PR URL 기록 -->
**devflow state 유지**: 옵션 B에서는 devflow-state.md를 아카이브하지 않는다. PR 머지 후 다음 세션에서 using-devflow가 PR 머지 확인 → 종료 처리를 안내한다. devflow-state에 `## Finishing Choice`를 `B (PR pending)` + `## PR URL`을 `[github-pr-url]`로 기록한다.

---

#### 옵션 C: 브랜치 유지

현재 상태 저장:
```bash
# 미커밋 변경사항 있으면 커밋 또는 스태시
git status

# 필요시
git add <changed-files>  # 변경된 파일을 명시적으로 스테이징
git commit -m "WIP: [작업 내용]"
# 또는
git stash push -m "[작업 내용] — 나중에 처리"
```

완료 메시지:
```
## 브랜치 유지

브랜치: [branch-name]
상태: [커밋됨 / WIP 스태시됨]
워크트리: [path] (그대로 유지)

나중에 이 스킬을 다시 실행하면 동일한 선택지를 받을 수 있습니다.
```

---

#### 옵션 D: 작업 폐기

**이중 확인 절차** — 반드시 사용자가 'discard'를 직접 입력해야 진행한다:

```
⚠️  경고: 이 작업은 되돌릴 수 없습니다.

다음 항목이 영구적으로 삭제됩니다:
- 브랜치: [branch-name]
- 커밋 [count]개
- 변경된 파일 [count]개

계속하려면 'discard'를 입력하세요.
취소하려면 다른 키를 입력하세요.
```

'discard' 입력 확인 후:
```bash
# 베이스 브랜치로 이동
git checkout [base-branch]

# 브랜치 강제 삭제
git branch -D [branch-name]
```

워크트리 사용 중인 경우:
```bash
# 워크트리 제거 후 브랜치 삭제 (옵션 D에서만 실행)
git worktree remove --force [worktree-path]
git worktree prune
git branch -D [branch-name]
```

완료 메시지:
```
## 브랜치 폐기 완료

삭제된 브랜치: [branch-name]
[삭제된 워크트리: [worktree-path]] (워크트리 사용 시)
```

<!-- @state-update: 옵션 D 폐기 → Current Phase를 finished로 -->
**devflow 종료 처리** (devflow-state.md가 존재하는 경우):
1. `devflow-docs/devflow-state.md`의 `## Current Phase`를 `finished`로 업데이트
2. state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동
3. devflow-audit에 로깅: `"Flow finished — option D (discarded)"`

---

## 워크트리 정리 규칙 요약

| 옵션 | 워크트리 처리 | devflow 처리 |
|------|------------|------------|
| A (로컬 병합) | 워크트리 제거 (`git worktree remove`) | `finished` + `.archive/`로 이동 |
| B (PR 생성) | 워크트리 유지 (PR 머지 후 처리) | state 유지 (PR 머지 후 종료) |
| C (브랜치 유지) | 워크트리 유지 | state 유지 |
| D (폐기) | 워크트리 강제 제거 (`--force`) | `finished` + `.archive/`로 이동 |

---

## Examples

### Example 1: 기능 개발 완료 후 로컬 병합 (옵션 A)

**상황**: `feature/notification-service` 브랜치에서 개발 완료, 팀 혼자 작업

```bash
# 1단계: 검증
pytest tests/ -v  # 15 passed

# 2단계: 선택지 제시 → 사용자가 A 선택

# 3단계: 실행
git checkout main
git merge --no-ff feature/notification-service -m "Merge branch 'feature/notification-service'"
git branch -d feature/notification-service
git worktree remove ~/workspaces/notification-service-worktree
git worktree prune
```

결과:
```
병합 완료: feature/notification-service → main
삭제된 브랜치: feature/notification-service
워크트리 제거: ~/workspaces/notification-service-worktree
```

---

### Example 2: 팀 리뷰가 필요한 경우 PR 생성 (옵션 B)

**상황**: `feature/payment-refactor` 브랜치, 코드 리뷰 필요

```bash
# 2단계: 선택지 제시 → 사용자가 B 선택

# 3단계: 실행
git push -u origin feature/payment-refactor
gh pr create \
  --base main \
  --title "feat: payment 서비스 리팩토링" \
  --body "..."
```

결과:
```
PR 생성 완료
브랜치: feature/payment-refactor
PR URL: https://github.com/org/repo/pull/42
워크트리는 PR 머지 후 처리합니다.
```

---

## Troubleshooting

### 병합 충돌 발생 시 (옵션 A)

**증상**: `git merge` 실행 후 충돌 메시지
```
CONFLICT (content): Merge conflict in src/service.py
Automatic merge failed; fix conflicts and then commit the result.
```

**처리 방법**:
1. 충돌 파일 목록 확인: `git status`
2. 각 파일의 충돌 마커(`<<<<<<<`, `=======`, `>>>>>>>`) 해소
3. 해소 후 스테이징: `git add <파일>`
4. 병합 커밋: `git commit`
5. 충돌 해소가 복잡하면 병합을 중단하고 옵션 B(PR)를 선택하는 것을 고려
   ```bash
   git merge --abort  # 병합 취소
   ```

---

### 원격 저장소 푸시 권한 없을 때 (옵션 B)

**증상**: `git push` 실행 후 `Permission denied` 또는 `403` 에러

**처리 방법**:
1. SSH 키 또는 토큰 설정 확인: `gh auth status`
2. 인증 재설정: `gh auth login`
3. HTTPS 대신 SSH 사용: `git remote set-url origin git@github.com:org/repo.git`
4. 권한 문제가 해결되지 않으면 옵션 A(로컬 병합)를 대안으로 제시한다
