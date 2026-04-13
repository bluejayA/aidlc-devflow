# Executable Next Steps — Phase C First

> **Date**: 2026-04-13
> **This document is a patch plan, NOT a proposal.**
> **Execution order**: Phase C → Phase A → Phase B → Phase D → Phase E
> Rationale (Codex): Canonical path cleanup MUST precede new hook rollout.

---

## Overview — 5 Concrete Changes (Phase C + Phase D scaffolding)

The first 5 changes cover the **blocking legacy cleanup** (Codex top-3 blockers) and **minimum scaffolding for new hooks**.

| # | Change | Phase | Risk |
|---|--------|-------|------|
| 1 | Legacy `devflow-audit.md` 삭제 + 4곳 stale 참조 수정 | C | Low (1 파일 삭제 + 4곳 편집) |
| 2 | **K-gate 재정의**: STORE 직접 호출 제거 → verdict 로그만 (`construction-orchestrator:319`) | C | Med (기존 테스트 영향 검토 필요 — `tests/test_devflow_solutions.py`) |
| 3 | Pattern 33개 (17 patterns + 12 reviewers + 4 protocols) 필수 frontmatter 추가 | A | Low (non-destructive) |
| 4 | Skill 28개 `skill_nature` + `model_dependency` 일괄 태깅 (BL-081 초안 적용) | A | Low (non-destructive) |
| 5 | `hooks/post-tool-file-edit` 신규 스크립트 + `hooks.json` 업데이트 | D | Med (exclusion list 정확성 필요) |
| 6 | **`aidlc-systematic-debugging` STORE 단일 owner 책임** (완료 시 guaranteed trigger) | C | Med (Solution layer 활성화 — dead layer 방지 핵심) |

**Change 1-2**는 **파일 동작 버그** 수정 → 우선 실행.
**Change 3-4**는 **non-destructive** metadata 추가 → 중간에 실행.
**Change 5**는 **신규 훅 도입** → 가장 마지막 (1-4 완료 후 canonical path 정리된 상태에서).

---

## Change 1 — Legacy `devflow-audit.md` retirement + stale refs

### 1a. 파일 삭제

**Path**: `devflow-docs/devflow-audit.md`

**Before**: 1.8KB legacy 파일 존재 (`audit.md`와 분리된 rogue file)
**After**: 삭제

**Command**:
```bash
git rm devflow-docs/devflow-audit.md
```

**Expected result**: `git status`에 "deleted: devflow-docs/devflow-audit.md" 표시. `devflow-audit` utility의 기본 target은 `devflow-docs/audit.md` (skill 선언과 일치).

---

### 1b. `skills/aidlc-auto-mode/SKILL.md` line 374

**Before**:
```
3. `devflow-audit.md` — `[timestamp] [stage] — auto-approved — [이유 1줄]`
```

**After**:
```
3. `devflow-docs/audit.md` — `[timestamp] [stage] — auto-approved — [이유 1줄]`
```

**Expected result**: auto-mode skill이 정확한 audit 파일로 로깅.

---

### 1c. `skills/aidlc-superpowers-tracking/SKILL.md` line 24

**Before**:
```
devflow-audit.md를 파싱하여:
```

**After**:
```
devflow-docs/audit.md를 파싱하여:
```

**Expected result**: 동일 skill 내 line 48(`devflow-docs/audit.md`)과 일관성 확보.

---

### 1d. `docs/plans/2026-04-02-auto-mode-plan.md` line 490

**Before**:
```
devflow-audit.md 파일에 stage별 auto-approved 로그 기록
```

**After**:
```
devflow-docs/audit.md 파일에 stage별 auto-approved 로그 기록
```

**Expected result**: 문서-구현 일관성 확보.

---

### 1e. `docs/plans/2026-04-02-auto-mode-design.md` line 306

**Before**: (동일 패턴의 stale reference)
**After**: `devflow-docs/audit.md`로 치환

**Expected result**: design 문서와 구현 일관성 확보.

---

### 1f. Verification

```bash
# 다음 명령이 0건 반환해야 함 (단, plan.md 내 과거 타임라인 언급은 예외로 둘 것인지 검토)
rg 'devflow-audit\.md' --type md --type py
```

**Expected result**: 0건 (또는 historical reference만 명시적으로 남김).

---

## Change 2 — K-gate 재정의: STORE 직접 호출 제거

> **중요 아키텍처 결정 (옵션 α)**: STORE ownership을 `aidlc-systematic-debugging`으로 이관 (Change 6 참조).
> construction-orchestrator는 더 이상 STORE를 직접 호출하지 않고, systematic-debugging의 Return verdict만 로그에 기록한다.
> 이유: writer ownership 1개로 통일, 이중 호출 제거, user-invocable 경로와 orchestrator 경로 모두 동일 처리.

**Path**: `skills/aidlc-construction-orchestrator/SKILL.md:299-319`

**Before** (현재, semi-concrete 직접 호출):
```
K) 학습 기록 저장 → devflow-solutions 호출
...
- `devflow-solutions` STORE 호출 (debugging Return 4필드 + 보존된 error_message)
```

**After** (옵션 α, verdict 소비자 역할):
```markdown
K) 학습 기록 확인 → devflow-solutions verdict 수집

systematic-debugging이 성공적으로 완료되면 내부에서 STORE를 호출한다 (Change 6 참조).
construction-orchestrator는 STORE를 **직접 호출하지 않는다**.

systematic-debugging의 Return 필드:
- solution_verdict: "SAVE" | "DUPLICATE" | "REJECT"
- solution_saved_path: string | null
- solution_similar_to: string | null

이 값을 devflow-audit에 기록:
  - solution_verdict="SAVE"   → audit에 `solution-store` 이벤트 + path
  - solution_verdict="DUPLICATE" → audit에 `solution-duplicate` + similar_to
  - solution_verdict="REJECT" → audit에 `solution-reject` + reason

audit 엔트리 prefix는 taxonomy §2.5 Evidence event type 규약 준수.
```

**Expected result**:
- construction-orchestrator K-gate는 STORE의 consumer 역할.
- STORE 자체는 systematic-debugging이 독립적으로 수행.
- 이중 호출 제거.

**Side effects (주의)**:
- **`tests/test_devflow_solutions.py` 영향 확인 필수**. 기존 테스트가 construction-orchestrator의 STORE 직접 호출을 검증하고 있다면 업데이트 필요. systematic-debugging → STORE 경로로 테스트 재구성.
- systematic-debugging의 Return 필드 (solution_verdict 등) 추가는 Change 6에서 처리.
- 이 Change는 Change 6과 **함께 적용**되어야 일관성 유지. 두 Change를 동일 commit에 묶거나 연속 commit으로.

---

## Change 3 — Pattern 33개 frontmatter 강화

### 3a. Target files

- `skills/_shared/patterns/*.md` (17개)
- `skills/_shared/reviewers/*.md` (12개)
- `skills/_shared/{devflow-conventions,gate-patterns,import-review-protocol,tdd-protocol}.md` (4개)

**Total: 33 files**

### 3b. Required frontmatter (신규 추가)

모든 Pattern 파일 상단에 다음 YAML block 추가 (기존 frontmatter 있으면 병합):

```yaml
---
type: pattern
applies_to: []                    # skill names that use this pattern
status: active                    # draft | active | deprecated
source: manual                    # manual | promoted_from_solution
last_validated: 2026-04-13        # today's date at migration time
---
```

### 3c. 개별 `applies_to` 채우기 (수동 판단)

| Pattern | `applies_to` 제안 |
|---------|------------------|
| `brownfield-exploration.md` | `aidlc-workspace-detection, aidlc-brainstorming` |
| `council-cli-detection.md` | `aidlc-inception-orchestrator` |
| `hold-mechanism.md` | `aidlc-inception-orchestrator, aidlc-construction-orchestrator` |
| `interrupt-handler.md` | `aidlc-construction-orchestrator, aidlc-code-generation` |
| `meta-tag-standard.md` | `aidlc-writing-skills` |
| `persuasion-principles.md` | `aidlc-requesting-code-review, aidlc-receiving-code-review` |
| `question-format-guide.md` | `aidlc-brainstorming, aidlc-requirements-analysis` |
| `review-feedback-schema.md` | `aidlc-receiving-code-review` |
| `review-gate-pattern.md` | `aidlc-requesting-code-review, aidlc-inception-orchestrator, aidlc-construction-orchestrator` |
| `review-team-protocol.md` | `aidlc-requesting-code-review` |
| `session-continuity.md` | `aidlc-using-devflow, aidlc-executing-plans, aidlc-auto-mode` |
| `skill-design-patterns.md` | `aidlc-writing-skills` |
| `skill-pattern-catalog.md` | `aidlc-writing-skills` |
| `skill-writing-guide.md` | `aidlc-writing-skills` |
| `tech-stack-catalog.md` | `aidlc-workflow-planning, aidlc-application-design` |
| `tech-stack-defaults.md` | `aidlc-workflow-planning` |
| `three-mode-selection.md` | `aidlc-workflow-planning, aidlc-auto-mode` |

### 3d. Reviewers (12 files in `_shared/reviewers/`)

동일 구조 적용:
```yaml
---
type: pattern
applies_to: [aidlc-requesting-code-review]   # 대부분 리뷰 skill이 사용
status: active
source: manual
last_validated: 2026-04-13
---
```

### 3e. Protocols (4 files)

`devflow-conventions.md`, `gate-patterns.md`, `import-review-protocol.md`, `tdd-protocol.md`:
```yaml
---
type: pattern
applies_to: []                    # 전역 적용 (모든 skill이 참조)
status: active
source: manual
last_validated: 2026-04-13
---
```

**Expected result**: 33 Pattern 파일 (17 patterns + 12 reviewers + 4 protocols) 전부 frontmatter 구조화. 검색/검증 가능.

---

## Change 4 — Skill 28개 `skill_nature` 일괄 태깅

### 4a. Target files

`skills/aidlc-*/SKILL.md` 28개 (infrastructure 3개 `_utils/` 제외).

### 4b. BL-081 초안 분류 적용

각 SKILL.md의 `metadata:` block에 2 필드 추가:

#### Compensation (4개) — `model_dependency` **필수**:
```yaml
metadata:
  # 기존 필드들...
  skill_nature: compensation
  lifecycle: active
  model_dependency: "<해당 skill 고유의 모델 약점 1줄>"
```

- `aidlc-verification-before-completion` — `model_dependency: "모델이 완료 선언 전 검증 명령 실행을 생략함"`
- `aidlc-test-driven-development` — `model_dependency: "모델이 자발적으로 실패 테스트를 먼저 작성하지 않음"`
- `aidlc-systematic-debugging` — `model_dependency: "모델이 원인 미확정 상태로 수정을 시도함"`
- `aidlc-build-and-test` — `model_dependency: "모델이 빌드/테스트를 실행 없이 '통과'로 선언함"`

#### Amplification (17개):
```yaml
metadata:
  skill_nature: amplification
  lifecycle: active
  # model_dependency 필드 생략 (모델 능력과 무관)
```

대상:
`aidlc-using-devflow`, `aidlc-inception-orchestrator`, `aidlc-construction-orchestrator`, `aidlc-brainstorming`, `aidlc-workflow-planning`, `aidlc-workspace-detection`, `aidlc-requirements-analysis`, `aidlc-writing-skills`, `aidlc-superpowers-tracking`, `aidlc-requesting-code-review`, `aidlc-receiving-code-review`, `aidlc-writing-plans`, `aidlc-dispatching-parallel-agents`, `aidlc-subagent-driven-development`, `aidlc-using-git-worktrees`, `aidlc-finishing-a-development-branch`, `aidlc-auto-mode`

#### Hybrid (7개) — `model_dependency` + `amplification_notes` **필수**:
```yaml
metadata:
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "<compensation 측면 1줄>"       # 필수
  amplification_notes: "<amplification 측면 1줄>"    # 필수
  # decomposition_target은 optional — 실제 lightening 시점에 작성
```

**Sprint 1 범위**: `model_dependency` + `amplification_notes` 각 1줄 필수 기재. 전체 `decomposition_target` (drop/absorb_into 구조) 은 **optional** — 실제 lightening 결정 시점에 작성.
**이유**: Sprint 1에 label-only 상태 방지 (rationale 없는 태그 방지). 동시에 완전 분해는 lightening 결정 시 필요한 추가 정보를 요구하므로 연기.

초안 (Phase A 실행 시 각 SKILL.md 검토 후 최종 확정):

| Skill | `model_dependency` | `amplification_notes` |
|-------|-------------------|----------------------|
| `aidlc-code-generation` | "모델이 TDD 순서 없이 구현하고 합리화함" | "2단계 plan+generate 구조로 설계-구현 경계 유지" |
| `aidlc-executing-plans` | "모델이 세션 경계를 넘어 맥락을 유지하지 못함" | "체크포인트-재개 프로토콜로 긴 작업 추적" |
| `aidlc-application-design` | "모델이 컴포넌트 경계를 임의로 결정함" | "도메인 entity + 서비스 구조 명시적 분해" |
| `aidlc-functional-design` | "모델이 API 계약 없이 구현함" | "비즈니스 규칙 + 계약 선행 정의" |
| `aidlc-units-generation` | "모델이 의존성 순서를 무시함" | "독립 개발/테스트 가능 단위 분해" |
| `aidlc-user-stories` | "모델이 INVEST 기준 없이 작성함" | "Acceptance Criteria 강제 + 추적성" |
| `aidlc-nfr-requirements` | "모델이 NFR을 기능 요구에 혼재시킴" | "도메인 프리셋 기반 NFR 체계화" |

(위 표는 Phase A 실행 시 SKILL.md 본문 재확인 후 최종 적용.)

#### Infrastructure (3개, `_utils/`):
```yaml
metadata:
  skill_nature: null
  lifecycle: active
```

- `skills/_utils/devflow-state/SKILL.md`
- `skills/_utils/devflow-audit/SKILL.md`
- `skills/_utils/devflow-solutions/SKILL.md`

### 4c. Verification

```bash
# 모든 aidlc-* skill이 skill_nature 필드를 가져야 함
for f in skills/aidlc-*/SKILL.md; do
  grep -q 'skill_nature:' "$f" || echo "MISSING: $f"
done
```

**Expected result**: 0건 missing. 28개 skill이 compensation/amplification/hybrid 중 하나로 분류됨.

### 4d. BL-081 이슈 업데이트

- GitHub issue #145 에 코멘트: "Phase 1 MVP 중 1, 2번 항목 (규약 정의, 28 skill 태깅)이 `docs/research/knowledgesystem/` 설계로 흡수되어 완료됨. 3, 4번 (Compensation Decay 분석, validator 확장)은 본 이슈에 남음."

---

## Change 5 — `hooks/post-tool-file-edit` 신규 + `hooks.json` 업데이트

### 5a. `hooks/post-tool-file-edit` (신규 파일)

**Path**: `hooks/post-tool-file-edit`

**Content**:
```bash
#!/bin/bash
# post-tool-file-edit — L1 auto ingest on Edit/Write tool calls
# Writes to devflow-docs/audit.md, soft-saves devflow-state.md

set -eo pipefail

# Tool input comes via stdin as JSON per Claude Code hook contract
INPUT=$(cat)
MODIFIED_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Path empty → nothing to log
[ -z "$MODIFIED_PATH" ] && exit 0

# Convert absolute to repo-relative (strip cwd prefix if present)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
case "$MODIFIED_PATH" in
  "$REPO_ROOT"/*)
    REL_PATH="${MODIFIED_PATH#$REPO_ROOT/}"
    ;;
  /*)
    # Outside repo — skip
    exit 0
    ;;
  *)
    REL_PATH="$MODIFIED_PATH"
    ;;
esac

# === Exclusion filter (self-amplification 방지 + noise 제거) ===
case "$REL_PATH" in
  tests/*|hooks/*|.claude-plugin/*|.git/*|.worktrees/*)
    exit 0 ;;
  devflow-docs/.archive/*|devflow-docs/audit.md|devflow-docs/audit-log/*)
    exit 0 ;;
  devflow-docs/devflow-state.md|devflow-docs/session-summary.md)
    # state/summary 자체 편집은 스킬이 직접 처리 → 훅 skip
    exit 0 ;;
esac

# === Whitelist filter (의미있는 지식 surface만 로깅) ===
case "$REL_PATH" in
  devflow-docs/*|docs/*|skills/*|CLAUDE.md|README.md)
    : # passed
    ;;
  *)
    exit 0 ;;
esac

# === audit.md append (event prefix: taxonomy §2.5 준수) ===
AUDIT="devflow-docs/audit.md"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
mkdir -p "$(dirname "$AUDIT")"
[ -f "$AUDIT" ] || echo "# DevFlow Audit Log" > "$AUDIT"
echo "- $TS — file-edit — $REL_PATH" >> "$AUDIT"

# === audit.md size warning (Sprint 1: warning only, rotation은 Sprint 2) ===
SIZE=$(wc -c < "$AUDIT" 2>/dev/null || echo 0)
if [ "$SIZE" -gt 102400 ]; then
  echo "[devflow] WARNING: audit.md > 100KB ($SIZE bytes). Rotation recommended." >&2
fi

# === devflow-state.md soft-save ===
# ⚠️ RACE CONDITION 방지 제약:
# 이 hook은 **오직 '## Last Updated' heading 값만** 수정한다.
# 구조 섹션 (## Current Phase, ## Current Stage, ## Worktree, ## WIP 등) 절대 건드리지 않음.
# 구조 변경은 skill(using-devflow, auto-mode, finishing-a-development-branch)의 책임.
# Hook과 skill이 동시 write해도 서로 다른 heading만 건드려 충돌 최소화.
STATE="devflow-docs/devflow-state.md"
if [ -f "$STATE" ]; then
  if grep -q '^## Last Updated' "$STATE"; then
    # Inline update via awk (portable, atomic via mv)
    awk -v ts="$TS" '
      /^## Last Updated$/ { print; getline; print ts; next }
      { print }
    ' "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
  fi
  # Note: "## Last Updated" heading이 없으면 hook은 아무것도 안 함 (skill이 넣어야 함).
fi

exit 0
```

**Permissions**:
```bash
chmod +x hooks/post-tool-file-edit
```

### 5b. `hooks/hooks.json` 업데이트

**Before**:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {"type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\""}
        ]
      }
    ]
  }
}
```

**After**:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {"type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\""}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {"type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/post-tool-file-edit\""}
        ]
      }
    ]
  }
}
```

### 5c. Verification tests

```bash
# 1) Positive: skills/aidlc-test/SKILL.md 편집 시 audit.md append 확인
echo "test" >> /tmp/delete-me.md  # avoid; use Write tool in claude code

# 2) Negative: tests/ 편집 시 audit.md 변경 없음 확인
# 3) Negative: .git/ 편집 시 audit.md 변경 없음 확인
# 4) Self-amplification: audit.md 자체 편집 시 재진입 없음 확인
```

### 5d. Expected result

- Edit/Write 도구 호출 시 (whitelist + not exclude 조건 만족) `audit.md`에 1 line append
- tests/, hooks/, .archive/ 등 제외
- state.md `## Last Updated` 값 자동 갱신 (있을 경우)
- 100KB 초과 시 stderr warning
- Claude에 출력되는 stdout 없음 (0 tokens)

---

## Change 6 — `aidlc-systematic-debugging` STORE 단일 owner

> **Solution layer를 dead layer에서 live layer로 전환하는 핵심 변경.**
> Red team 분석: Solution은 존재하지만 `currently untriggered` → taxonomy상 empty layer. Change 6으로 guaranteed trigger 확보.
> 아키텍처 (옵션 α): systematic-debugging이 STORE 단일 owner. construction-orchestrator는 verdict 소비자 (Change 2 참조).

**Path**: `skills/aidlc-systematic-debugging/SKILL.md`

### 6a. STORE 호출 책임 추가 (완료 시 guaranteed)

**위치**: SKILL.md 본문 하단 또는 "Complete" phase 정의부

**추가할 섹션**:
```markdown
## STORE 호출 (완료 시 guaranteed)

root_cause 확정 + 수정 검증 완료 상태에서 **무조건** `devflow-solutions` STORE 호출.

### 호출 조건

다음 **모두** 만족 시에만 STORE 호출:
1. root_cause가 명확히 확정됨 (가설이 아닌 확증)
2. fix가 적용되고 회귀 테스트가 PASS됨
3. debugging이 inconclusive / aborted 상태 아님

위 조건 미충족 시 STORE 호출하지 않음.

### 호출 형식

```
devflow-solutions STORE(
  root_cause="[확정된 근본 원인 한 줄]",
  fix_summary="[적용된 수정 내용 한 줄]",
  regression_test="[추가/수정된 회귀 테스트명 또는 경로]",
  test_result="[수정 후 전체 테스트 결과, 예: '139 passed, 0 failed']",
  error_message="[원본 에러 메시지 — build-and-test 경로 또는 caller가 전달]"
)
```

### Return 처리

STORE는 다음 verdict 중 하나 반환:
- `SAVE`: 신규 저장 (saved_path 반환)
- `DUPLICATE`: 동일 `error_signature` 존재 (similar_to 반환, 저장 안 함)
- `REJECT`: Privacy scrubbing 실패 또는 format 오류

systematic-debugging은 verdict를 자신의 Return 필드에 포함:
- `solution_verdict: "SAVE" | "DUPLICATE" | "REJECT"`
- `solution_saved_path: string | null`
- `solution_similar_to: string | null`
- `solution_reject_reason: string | null`

caller (construction-orchestrator 또는 user-invocable 경로)는 이 Return 값을 소비하여 audit에 로그만 남김 (STORE 재호출 금지).

### 호출 경로 (3가지 모두 동일)

1. **Orchestrator 경로**: construction-orchestrator K-gate에서 systematic-debugging 호출 → 완료 시 내부 STORE
2. **User-invocable 경로**: 사용자가 `/aidlc:aidlc-systematic-debugging` 직접 호출 → 완료 시 내부 STORE
3. **Debugging chain 경로**: 다른 skill이 systematic-debugging을 인라인 호출 → 완료 시 내부 STORE

세 경로 모두 동일 STORE 행동을 보장 (guaranteed trigger).

### Noise 관리 (Sprint 1 정책)

- Phase 1에서는 **깨끗한 Solution 확보가 아니라 비어있지 않음 확보**가 목표.
- 중복은 `error_signature` 기반 duplicate check에 위임 (utility 책임).
- 유사 문제가 반복 저장되어도 허용 (promotion_filter는 Sprint 2+ 주제).
- 2주 관측 후 실제 데이터 기반으로 필터 기준 수립.
```

### 6b. Verification

```bash
# 1. systematic-debugging SKILL.md에 STORE 섹션 존재 확인
grep -q '^## STORE 호출' skills/aidlc-systematic-debugging/SKILL.md

# 2. 5 필드 명시 확인
grep -A8 '^## STORE 호출' skills/aidlc-systematic-debugging/SKILL.md | grep -E 'root_cause|fix_summary|regression_test|test_result|error_message'

# 3. Return 필드 solution_verdict 명시 확인
grep -q 'solution_verdict' skills/aidlc-systematic-debugging/SKILL.md

# 4. construction-orchestrator가 STORE 직접 호출 안 함 확인 (Change 2 효과)
! grep -E 'devflow-solutions.*STORE\s*\(' skills/aidlc-construction-orchestrator/SKILL.md
```

### 6c. Side effects

- `aidlc-systematic-debugging/SKILL.md` 본문 확장 (~40 lines 추가)
- `aidlc-construction-orchestrator/SKILL.md` K-gate 섹션 단순화 (Change 2 결과)
- `tests/test_devflow_solutions.py`: 호출 경로가 systematic-debugging 기준으로 재구성되면 테스트 업데이트 필요
- 기존 construction-orchestrator가 systematic-debugging 호출 시 전달하는 `error_message`는 계속 전달 필요 (caller contract)

### 6d. Expected result

- Solution layer 활성화: systematic-debugging 완료 시마다 Solution 생성 시도
- writer ownership 단일화 (이중 호출 제거)
- user-invocable + orchestrator 경로 동일 처리
- 첫 2주 관측 데이터로 Phase 2 필터링 기준 수립

---

## Execution Order Summary

```
Step 1 (Change 1):  devflow-audit.md legacy cleanup + 4 stale refs     [git commit #1]
Step 2 (Change 2+6): K-gate 재정의 + systematic-debugging STORE owner  [git commit #2 — 2/6 묶음]
Step 3 (Change 3):  Pattern 33개 frontmatter 강화                       [git commit #3]
Step 4 (Change 4):  Skill 28개 skill_nature + model_dependency 태깅   [git commit #4]
Step 5 (Change 5):  post-tool-file-edit 훅 + hooks.json 업데이트       [git commit #5]
```

> **Change 2와 Change 6은 반드시 동일 commit 또는 연속 commit으로 적용**. 분리 시 중간 상태에서 STORE 이중 호출 또는 누락 발생 가능.

**후속 (별도 작업, Phase B/E)**:
- Change 7: Decision 14개 (`docs/plans/`) + backlog.md frontmatter 추가 (Phase B)
- Change 8: session-start 상태 라인 확장 (Phase E)
- Change 9: hybrid 7개의 `decomposition_target` 실제 lightening 시점 작성
- Change 10 (Sprint 2): audit-log/ 자동 rotation 구현
- Change 11 (Sprint 2): Solution promotion filter (2주 데이터 관측 후)
- Change 12 (Sprint 2): L2 ingest 신규 skill 검토

---

## Rollback Plan

각 Change는 단일 commit으로 관리. 문제 발생 시:
- Change 1-2: `git revert <commit>` — 파일 복원 + 참조 되돌림
- Change 3-4: `git revert <commit>` — frontmatter 제거 (non-destructive라 영향 적음)
- Change 5: `hooks.json`에서 PostToolUse 블록 제거 + 새 스크립트 삭제

전체 롤백: 순서 역순으로 revert (Change 5 → 1).

---

## Success Signals

실행 완료 후 다음이 참이면 integration plan 성공:

1. `rg 'devflow-audit\.md' --type md --type py` → 0건 (또는 명시적 historical 참조만)
2. `ls devflow-docs/devflow-audit.md` → No such file
3. `grep -L 'skill_nature:' skills/aidlc-*/SKILL.md` → 0건
4. `grep -L 'model_dependency:' skills/aidlc-{verification-before-completion,test-driven-development,systematic-debugging,build-and-test,code-generation,executing-plans,application-design,functional-design,units-generation,user-stories,nfr-requirements}/SKILL.md` → 0건 (compensation 4 + hybrid 7)
5. `grep -L 'amplification_notes:' skills/aidlc-{code-generation,executing-plans,application-design,functional-design,units-generation,user-stories,nfr-requirements}/SKILL.md` → 0건 (hybrid 7)
6. `grep -L 'type: pattern' skills/_shared/patterns/*.md` → 0건
7. `skills/aidlc-systematic-debugging/SKILL.md`에 `## STORE 호출` 섹션 존재 + 5 필드 (root_cause, fix_summary, regression_test, test_result, error_message) 명시
8. `skills/aidlc-construction-orchestrator/SKILL.md`에서 `devflow-solutions.*STORE\s*\(` 패턴 0건 (직접 호출 제거 확인)
9. Edit tool로 `devflow-docs/backlog.md` 편집 → `audit.md`에 "file-edit" 엔트리 append 확인
10. Edit tool로 `tests/test_sample.py` 편집 → `audit.md` 크기 변화 없음 확인
11. `hooks.json`에 PostToolUse 블록 존재
12. Hook이 `devflow-state.md`의 `## Last Updated`만 수정, 구조 섹션 (`## Current Phase` 등) 무변경 확인

---

## References

- Taxonomy: `knowledge-taxonomy.md`
- Integration plan: `aidlc-knowledge-integration-plan.md`
- BL-081 분류 근거: `docs/research/2026-04-06-skill-lifecycle-strategy.md`
- K-gate 호출측 현재: `skills/aidlc-construction-orchestrator/SKILL.md:299-319`
- K-gate utility-side: `skills/_utils/devflow-solutions/SKILL.md:26-49`
