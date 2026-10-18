---
name: review
description: 브랜치 전체 코드 리뷰 1회(가장 강한 모델) + Codex 교차 리뷰 1회. plan-build가 끝나면 자동 호출되고, "리뷰해줘", "코드 리뷰", review this branch로 직접 부를 수도 있다. 결과 파일이 있어야 push 훅이 열린다.
user-invocable: true
model: opus
---

# review

**입력**: 현재 브랜치(base = main과의 merge-base, 또는 사용자가 준 범위), 있으면 계획 파일. **산출물**: `.devflow/sdd/<plan>/branch-review.md`, `codex-review.md`, 그리고 push 훅이 보는 `.devflow/review-done`. 끝나면 `handoff` → finishing 게이트.

## 1. 패키지

```bash
BASE=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master)
bash ${CLAUDE_PLUGIN_ROOT}/_shared/scripts/review-package <plan 또는 "-"> $BASE HEAD
```

계획이 없는 작업(`-`)이면 디렉터리는 `.devflow/sdd/_noplan/`. 패키지는 내 컨텍스트에 넣지 않는다 — 경로만 넘긴다.

## 2. 브랜치 리뷰 (Claude, 가장 강한 모델)

`${CLAUDE_PLUGIN_ROOT}/_shared/prompts/review-prompt.md`의 **Part 1~4 전부**로 서브에이전트 1개. `[BRIEF_FILE]`은 계획 파일(없으면 합의 단락을 임시 파일로), `[REVIEW_FOCUS]`는 계획의 Review Focus. 결과를 `branch-review.md`에 저장.

## 3. Codex 교차 리뷰 (다른 모델, 1회)

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/codex-review <diff 패키지> <계획 파일 또는 -> > .devflow/sdd/<plan>/codex-review.md
```

같은 리뷰 프롬프트를 `codex exec`에 넘긴다. 가치는 다수결이 아니라 **같은 모델의 맹점 보완**이다. `codex` CLI가 없으면 스크립트가 그렇게 적힌 파일을 만들고 0으로 끝난다 — 건너뛰되 결과에 "Codex 미실행"이라고 남긴다.

## 4. 합치기

두 결과의 finding을 하나의 목록으로. 같은 지적은 합치고, 근거 위치(file:line)가 없는 지적은 버린다. Codex만 지적한 것은 "Codex only"로 표시 — 그게 교차 리뷰의 산출이다.

- Critical/Important가 있으면 **수정 디스패치 1회** (인라인이면 직접) → 범위를 그 finding으로 좁힌 재리뷰 1회. 그래도 남으면 각각 Ruling으로 판정해 ledger에 적는다.
- Minor는 목록으로 사용자에게 보여 주고 손대지 않는다.

## 5. 끝

```bash
printf '%s %s\n' "$(git rev-parse --short HEAD)" "$(date -u +%FT%TZ)" > .devflow/review-done
```

session-summary 갱신(`handoff`) 후 **finishing 게이트**: 머지 / PR(`gh pr create`, body 첫 줄 `Closes #N`) / 브랜치 유지 / 폐기 중 하나를 사용자가 고른다. 승인 없이 push·merge하지 않는다.
