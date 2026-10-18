# Knowledge System Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** aidlc-devflow v1.9.0의 기존 자산을 6-type knowledge taxonomy로 재분류하고, Solution layer를 활성화하며, L1 ingest 훅을 도입한다.

**Complexity:** Comprehensive

**Architecture:**
기존 `devflow-docs/` 와 `skills/` 구조를 유지하면서 6 타입 taxonomy (Decision/Solution/Pattern/Skill/Evidence/SessionState)를 frontmatter 기반으로 오버레이한다. Solution layer를 dead state에서 live state로 전환하기 위해 `aidlc-systematic-debugging`을 STORE 단일 owner로 재정의하며, construction-orchestrator K-gate는 verdict 소비자로 단순화한다. 파일 편집 이벤트를 `audit.md`에 자동 기록하는 `post-tool-file-edit` 훅을 새로 도입하되, self-amplification과 race condition을 방지하는 whitelist/exclusion + "Last Updated only" 제약을 엄격 적용한다.

**Tech Stack:** Bash shell hooks (POSIX-compatible, jq optional), Markdown + YAML frontmatter, Claude Code plugin manifest (`.claude-plugin/plugin.json`, `hooks/hooks.json`)

**Reference Docs:**

설계 단계 자료:
- Taxonomy: `docs/research/knowledgesystem/knowledge-taxonomy.md`
- Integration plan: `docs/research/knowledgesystem/aidlc-knowledge-integration-plan.md`
- Executable detail: `docs/research/knowledgesystem/executable-next-steps.md`
- BL-081 source: `docs/research/2026-04-06-skill-lifecycle-strategy.md`

구현 완료 후 자료 (Phase 2 진입 시 필수 참조):
- Phase 1 사용자 영향 요약: `docs/research/knowledgesystem/phase1-overview.md`
- Phase 1 baseline (plugin repo 기준 T0 = 2026-04-13): `docs/research/knowledgesystem/phase1-baseline.md`
- Phase 2 관측 설계 (consumer repo nexttui T0 = 2026-04-14): `docs/research/knowledgesystem/phase2-observation-plan.md`
- Rollback 가이드 (5-level): `docs/research/knowledgesystem/rollback-guide.md`

**Critical constraints:**
- 6 타입만, 하위 타입 금지
- 새 최상위 디렉토리 없음
- Session start token overhead ≤ +20% vs baseline (~2,555 tokens)
- 기존 28+ skill의 output_path 선언 건드리지 않음
- heading-based Markdown `devflow-state.md` 포맷 유지 (YAML 마이그레이션 없음)

**Task execution order (중요):**
```
Task 1 → Task 2+3 (반드시 동일/연속 commit) → Task 4 → Task 5 → Task 6
```

---

## Task 1: Legacy `devflow-audit.md` Retirement

**Goal:** `devflow-audit.md` legacy 파일 삭제 + 4곳 stale 참조 canonical `audit.md`로 정정. Evidence SSOT 확립의 전제.

**Files:**
- Delete: `devflow-docs/devflow-audit.md`
- Modify: `skills/aidlc-auto-mode/SKILL.md:374`
- Modify: `skills/aidlc-superpowers-tracking/SKILL.md:24`
- Modify: `docs/plans/2026-04-02-auto-mode-plan.md:490`
- Modify: `docs/plans/2026-04-02-auto-mode-design.md:306`
- Test: shell verification commands

---

- [ ] **Step 1: Write failing verification command**

Expected behavior: `devflow-audit.md` 참조 0건 (legacy historical refs 제외).

Verification script (runs before changes — MUST FAIL):
```bash
#!/bin/bash
# tests/verify-change-1.sh
set -e

# Check 1: legacy file should NOT exist
if [ -f "devflow-docs/devflow-audit.md" ]; then
  echo "FAIL: devflow-docs/devflow-audit.md still exists"
  exit 1
fi

# Check 2: no stale references in md/py (excluding historical context blocks)
STALE=$(rg 'devflow-audit\.md' --type md --type py --glob '!docs/research/knowledgesystem/**' --glob '!docs/plans/2026-04-13-knowledge-system-phase1-plan.md' || true)
if [ -n "$STALE" ]; then
  echo "FAIL: stale devflow-audit.md references found:"
  echo "$STALE"
  exit 1
fi

echo "PASS: Change 1 verified"
```

- [ ] **Step 2: Run verification — verify FAIL**

Run: `bash tests/verify-change-1.sh`

Expected: FAIL. Either legacy file exists or stale refs present (currently both).

- [ ] **Step 3: Delete legacy file**

Run: `git rm devflow-docs/devflow-audit.md`

Expected: `git status` shows "deleted: devflow-docs/devflow-audit.md".

- [ ] **Step 4: Fix `aidlc-auto-mode/SKILL.md:374`**

Modify: `skills/aidlc-auto-mode/SKILL.md`, line 374.

Before:
```
3. `devflow-audit.md` — `[timestamp] [stage] — auto-approved — [이유 1줄]`
```

After:
```
3. `devflow-docs/audit.md` — `[timestamp] [stage] — auto-approved — [이유 1줄]`
```

- [ ] **Step 5: Fix `aidlc-superpowers-tracking/SKILL.md:24`**

Modify: `skills/aidlc-superpowers-tracking/SKILL.md`, line 24.

Before:
```
devflow-audit.md를 파싱하여:
```

After:
```
devflow-docs/audit.md를 파싱하여:
```

- [ ] **Step 6: Fix `docs/plans/2026-04-02-auto-mode-plan.md:490`**

Read line 490 of `docs/plans/2026-04-02-auto-mode-plan.md`. If it contains `devflow-audit.md`, replace with `devflow-docs/audit.md` inline.

- [ ] **Step 7: Fix `docs/plans/2026-04-02-auto-mode-design.md:306`**

Read line 306 of `docs/plans/2026-04-02-auto-mode-design.md`. If it contains `devflow-audit.md`, replace with `devflow-docs/audit.md` inline.

- [ ] **Step 8: Run verification — verify PASS**

Run: `bash tests/verify-change-1.sh`

Expected: PASS with "Change 1 verified".

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "refactor: devflow-audit.md legacy 파일 제거 + stale 참조 4곳 정정

- devflow-docs/devflow-audit.md 삭제 (legacy)
- skills/aidlc-auto-mode/SKILL.md:374: devflow-docs/audit.md로 정정
- skills/aidlc-superpowers-tracking/SKILL.md:24: 동일 정정
- docs/plans/2026-04-02-auto-mode-{plan,design}.md 동일 정정
- Evidence SSOT를 audit.md로 확립 (taxonomy §2.5)"
```

---

## Task 2: `aidlc-systematic-debugging` STORE 단일 Owner

**Goal:** systematic-debugging 완료 시 `devflow-solutions` STORE를 guaranteed trigger로 호출. Solution layer를 live state로 전환. **Task 3과 연속 commit 필수**.

**Files:**
- Modify: `skills/aidlc-systematic-debugging/SKILL.md` (본문 확장)
- Test: shell verification

---

- [ ] **Step 1: Write failing verification**

Script (runs before changes — MUST FAIL):
```bash
#!/bin/bash
# tests/verify-change-6.sh
set -e

SKILL="skills/aidlc-systematic-debugging/SKILL.md"

# Check 1: STORE 섹션 존재
if ! grep -q '^## STORE 호출' "$SKILL"; then
  echo "FAIL: '## STORE 호출' section missing in $SKILL"
  exit 1
fi

# Check 2: 5 필드 모두 언급
for field in root_cause fix_summary regression_test test_result error_message; do
  if ! grep -q "$field=" "$SKILL"; then
    echo "FAIL: STORE field '$field' missing"
    exit 1
  fi
done

# Check 3: solution_verdict Return 필드 명시
if ! grep -q 'solution_verdict' "$SKILL"; then
  echo "FAIL: solution_verdict Return field missing"
  exit 1
fi

echo "PASS: Change 6 verified"
```

- [ ] **Step 2: Run verification — verify FAIL**

Run: `bash tests/verify-change-6.sh`

Expected: FAIL ("'## STORE 호출' section missing").

- [ ] **Step 3: Add STORE 섹션 to `aidlc-systematic-debugging/SKILL.md`**

Append at the end of `skills/aidlc-systematic-debugging/SKILL.md` (before any "References" or final section):

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

### Return 필드 (caller 소비용)

STORE Return값을 systematic-debugging 자체 Return에 포함:

- `solution_verdict`: `"SAVE" | "DUPLICATE" | "REJECT"`
- `solution_saved_path`: `string | null`
- `solution_similar_to`: `string | null`
- `solution_reject_reason`: `string | null`

caller (construction-orchestrator, user-invocable, chain)는 이 값을 audit에 로그만 남김 (STORE 재호출 금지).

### 호출 경로 (3가지 모두 동일)

1. **Orchestrator 경로**: construction-orchestrator K-gate → systematic-debugging 호출 → 내부 STORE
2. **User-invocable 경로**: `/aidlc:aidlc-systematic-debugging` 직접 호출 → 내부 STORE
3. **Debugging chain 경로**: 다른 skill이 인라인 호출 → 내부 STORE

세 경로 모두 guaranteed trigger. writer ownership = systematic-debugging 단독.

### Noise 관리 (Sprint 1 정책)

- Phase 1 목표: **Solution layer가 비어있지 않음**. 깨끗함은 Phase 2+.
- 중복 판정은 `error_signature` 기반 duplicate check에 위임 (utility 책임).
- 유사 문제 반복 저장 허용. promotion_filter는 Sprint 2+ 주제.
- 첫 2주 noise 관측 후 실제 데이터로 필터 기준 수립.
```

- [ ] **Step 4: Run verification — verify PASS**

Run: `bash tests/verify-change-6.sh`

Expected: PASS ("Change 6 verified").

- [ ] **Step 5: Do NOT commit yet**

**중요**: Task 3와 동일/연속 commit 필요. Task 3 완료 후 함께 commit.

---

## Task 3: `construction-orchestrator` K-gate 재정의

**Goal:** K-gate에서 STORE 직접 호출 제거. systematic-debugging Return의 verdict만 audit에 로그. **Task 2와 연속 commit 필수**.

**Files:**
- Modify: `skills/aidlc-construction-orchestrator/SKILL.md:299-319` (K-gate 섹션)
- Test: shell verification

---

- [ ] **Step 1: Write failing verification**

Script (runs before changes — MUST FAIL):
```bash
#!/bin/bash
# tests/verify-change-2.sh
set -e

SKILL="skills/aidlc-construction-orchestrator/SKILL.md"

# Check 1: STORE 직접 호출 없음 (devflow-solutions STORE( 패턴)
if grep -qE 'devflow-solutions.*STORE\s*\(' "$SKILL"; then
  echo "FAIL: direct STORE call still present in $SKILL"
  grep -nE 'devflow-solutions.*STORE\s*\(' "$SKILL"
  exit 1
fi

# Check 2: solution_verdict 소비 언급
if ! grep -q 'solution_verdict' "$SKILL"; then
  echo "FAIL: solution_verdict not consumed in K-gate"
  exit 1
fi

echo "PASS: Change 2 verified"
```

- [ ] **Step 2: Run verification — verify FAIL**

Run: `bash tests/verify-change-2.sh`

Expected: FAIL ("direct STORE call still present").

- [ ] **Step 3: Rewrite K-gate section in construction-orchestrator**

Modify: `skills/aidlc-construction-orchestrator/SKILL.md`, lines 299-319 (K-gate 관련 전체 블록).

Before (현재, 요약):
```
- `devflow-solutions` STORE 호출 (debugging Return 4필드 + 보존된 error_message)
```

After (전체 K-gate 섹션 교체):
```markdown
K) 학습 기록 확인 → devflow-solutions verdict 수집

systematic-debugging이 성공적으로 완료되면 **systematic-debugging 내부에서 STORE 호출**이 이루어진다 (Change 6 참조, `skills/aidlc-systematic-debugging/SKILL.md` `## STORE 호출` 섹션).

construction-orchestrator는 STORE를 **직접 호출하지 않는다**. 대신 systematic-debugging의 Return 필드를 소비하여 audit에 기록한다:

- `solution_verdict: "SAVE"` → audit prefix `solution-store`, `solution_saved_path` 포함
- `solution_verdict: "DUPLICATE"` → audit prefix `solution-duplicate`, `solution_similar_to` 포함
- `solution_verdict: "REJECT"` → audit prefix `solution-reject`, `solution_reject_reason` 포함

audit 엔트리 prefix는 taxonomy §2.5 Evidence event type 규약 준수 (`docs/research/knowledgesystem/knowledge-taxonomy.md`).

이 재정의의 근거:
- writer ownership 단일화 (systematic-debugging)
- user-invocable + orchestrator 경로 동일 처리
- 이중 호출 제거 (중복 판정 낭비 제거)
```

- [ ] **Step 4: Run verification — verify PASS**

Run: `bash tests/verify-change-2.sh`

Expected: PASS ("Change 2 verified").

- [ ] **Step 5: Check existing test impact**

Run: `bash -c 'ls tests/test_devflow_solutions.py && grep -l construction_orchestrator tests/test_devflow_solutions.py'`

If `tests/test_devflow_solutions.py` references construction-orchestrator의 직접 STORE 호출:
- 해당 테스트 케이스를 systematic-debugging 경로로 재구성
- 또는 Task 3.6으로 분리 (테스트 재작성)

만약 테스트 영향 없음이면 Step 6 진행.

- [ ] **Step 6: Commit (Task 2 + Task 3 묶음)**

```bash
git add -A
git commit -m "refactor: STORE ownership을 systematic-debugging으로 이관 (옵션 α)

Task 2 + Task 3 묶음 commit:
- systematic-debugging: STORE 호출 guaranteed trigger 책임 추가 (Change 6)
- construction-orchestrator K-gate: STORE 직접 호출 제거, verdict 소비자로 단순화 (Change 2)

효과:
- Solution layer를 dead state → live state 전환
- writer ownership 단일화 (이중 호출 제거)
- user-invocable + orchestrator + chain 경로 동일 처리

refs #145"
```

---

## Task 4: Pattern 33개 Frontmatter 강화

**Goal:** `skills/_shared/` 하위 33개 Pattern 파일에 필수 frontmatter 5 필드 추가. metadata staleness는 Phase 1에서 수용.

**Files:**
- Modify: `skills/_shared/patterns/*.md` (17 files)
- Modify: `skills/_shared/reviewers/*.md` (12 files)
- Modify: `skills/_shared/devflow-conventions.md`, `gate-patterns.md`, `import-review-protocol.md`, `tdd-protocol.md` (4 files)

---

- [ ] **Step 1: Write failing verification**

Script:
```bash
#!/bin/bash
# tests/verify-change-3.sh
set -e

PATTERN_FILES=(
  skills/_shared/patterns/*.md
  skills/_shared/reviewers/*.md
  skills/_shared/devflow-conventions.md
  skills/_shared/gate-patterns.md
  skills/_shared/import-review-protocol.md
  skills/_shared/tdd-protocol.md
)

REQUIRED_FIELDS=(type applies_to status source last_validated)

MISSING=()
for f in "${PATTERN_FILES[@]}"; do
  [ -f "$f" ] || continue
  for field in "${REQUIRED_FIELDS[@]}"; do
    if ! grep -qE "^${field}:" "$f"; then
      MISSING+=("$f:$field")
    fi
  done
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "FAIL: missing frontmatter fields:"
  printf '%s\n' "${MISSING[@]}"
  exit 1
fi

echo "PASS: Change 3 verified (33 files frontmatter complete)"
```

- [ ] **Step 2: Run verification — verify FAIL**

Run: `bash tests/verify-change-3.sh`

Expected: FAIL (현재 frontmatter 없음).

- [ ] **Step 3: Add frontmatter to `skills/_shared/patterns/*.md` (17 files)**

각 파일 상단에 다음 block을 추가 (기존 frontmatter 있으면 병합, 없으면 신규):

```yaml
---
type: pattern
applies_to: [<skill-name 또는 빈 배열>]
status: active
source: manual
last_validated: 2026-04-13
---
```

`applies_to` 개별 값 (executable-next-steps §3c 참조):

| File | `applies_to` |
|------|-------------|
| `brownfield-exploration.md` | `[aidlc-workspace-detection, aidlc-brainstorming]` |
| `council-cli-detection.md` | `[aidlc-inception-orchestrator]` |
| `hold-mechanism.md` | `[aidlc-inception-orchestrator, aidlc-construction-orchestrator]` |
| `interrupt-handler.md` | `[aidlc-construction-orchestrator, aidlc-code-generation]` |
| `meta-tag-standard.md` | `[aidlc-writing-skills]` |
| `persuasion-principles.md` | `[aidlc-requesting-code-review, aidlc-receiving-code-review]` |
| `question-format-guide.md` | `[aidlc-brainstorming, aidlc-requirements-analysis]` |
| `review-feedback-schema.md` | `[aidlc-receiving-code-review]` |
| `review-gate-pattern.md` | `[aidlc-requesting-code-review, aidlc-inception-orchestrator, aidlc-construction-orchestrator]` |
| `review-team-protocol.md` | `[aidlc-requesting-code-review]` |
| `session-continuity.md` | `[aidlc-using-devflow, aidlc-executing-plans, aidlc-auto-mode]` |
| `skill-design-patterns.md` | `[aidlc-writing-skills]` |
| `skill-pattern-catalog.md` | `[aidlc-writing-skills]` |
| `skill-writing-guide.md` | `[aidlc-writing-skills]` |
| `tech-stack-catalog.md` | `[aidlc-workflow-planning, aidlc-application-design]` |
| `tech-stack-defaults.md` | `[aidlc-workflow-planning]` |
| `three-mode-selection.md` | `[aidlc-workflow-planning, aidlc-auto-mode]` |

- [ ] **Step 4: Add frontmatter to `skills/_shared/reviewers/*.md` (12 files)**

각 reviewer 파일에:
```yaml
---
type: pattern
applies_to: [aidlc-requesting-code-review]
status: active
source: manual
last_validated: 2026-04-13
---
```

(모든 reviewer가 `aidlc-requesting-code-review`가 사용하는 prompt template)

- [ ] **Step 5: Add frontmatter to 4 shared protocols**

각각에:
```yaml
---
type: pattern
applies_to: []
status: active
source: manual
last_validated: 2026-04-13
---
```

파일 목록: `devflow-conventions.md`, `gate-patterns.md`, `import-review-protocol.md`, `tdd-protocol.md`

(전역 적용 → `applies_to: []`)

- [ ] **Step 6: Run verification — verify PASS**

Run: `bash tests/verify-change-3.sh`

Expected: PASS ("33 files frontmatter complete").

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "docs: Pattern 33개 frontmatter 강화 (taxonomy §2.3)

- 17 patterns + 12 reviewers + 4 protocols
- 필수 5 필드 추가: type, applies_to, status, source, last_validated
- Phase 1 metadata staleness 수용 정책 (자동 갱신 없음)"
```

---

## Task 5: Skill 28개 `skill_nature` + `model_dependency` 태깅

**Goal:** BL-081 초안 분류를 28개 `aidlc-*` SKILL.md + 3개 `_utils` SKILL.md에 적용. compensation 4 + hybrid 7에 `model_dependency` 필수. hybrid 7에 `amplification_notes` 추가.

**Files:**
- Modify: `skills/aidlc-*/SKILL.md` (28 files)
- Modify: `skills/_utils/devflow-{state,audit,solutions}/SKILL.md` (3 files)

---

- [ ] **Step 1: Write failing verification**

Script:
```bash
#!/bin/bash
# tests/verify-change-4.sh
set -e

# 1. 모든 aidlc-* skill이 skill_nature + lifecycle 보유
MISSING_NATURE=$(grep -L 'skill_nature:' skills/aidlc-*/SKILL.md || true)
if [ -n "$MISSING_NATURE" ]; then
  echo "FAIL: skill_nature missing in:"
  echo "$MISSING_NATURE"
  exit 1
fi

# 2. compensation + hybrid 11개에 model_dependency 필수
COMP_HYBRID=(
  aidlc-verification-before-completion aidlc-test-driven-development
  aidlc-systematic-debugging aidlc-build-and-test
  aidlc-code-generation aidlc-executing-plans
  aidlc-application-design aidlc-functional-design
  aidlc-units-generation aidlc-user-stories aidlc-nfr-requirements
)
for skill in "${COMP_HYBRID[@]}"; do
  f="skills/$skill/SKILL.md"
  if ! grep -q 'model_dependency:' "$f"; then
    echo "FAIL: model_dependency missing in $f"
    exit 1
  fi
done

# 3. hybrid 7개에 amplification_notes 필수
HYBRID=(
  aidlc-code-generation aidlc-executing-plans
  aidlc-application-design aidlc-functional-design
  aidlc-units-generation aidlc-user-stories aidlc-nfr-requirements
)
for skill in "${HYBRID[@]}"; do
  f="skills/$skill/SKILL.md"
  if ! grep -q 'amplification_notes:' "$f"; then
    echo "FAIL: amplification_notes missing in $f"
    exit 1
  fi
done

# 4. _utils 3개에 skill_nature: null + lifecycle
for util in devflow-state devflow-audit devflow-solutions; do
  f="skills/_utils/$util/SKILL.md"
  if ! grep -q 'skill_nature: null' "$f"; then
    echo "FAIL: infrastructure skill_nature: null missing in $f"
    exit 1
  fi
done

echo "PASS: Change 4 verified"
```

- [ ] **Step 2: Run verification — verify FAIL**

Run: `bash tests/verify-change-4.sh`

Expected: FAIL (skill_nature missing in all).

- [ ] **Step 3: Tag compensation 4개**

각 SKILL.md의 `metadata:` block에 필드 추가:

`skills/aidlc-verification-before-completion/SKILL.md`:
```yaml
metadata:
  # ... 기존 필드들 ...
  skill_nature: compensation
  lifecycle: active
  model_dependency: "모델이 완료 선언 전 검증 명령 실행을 생략함"
```

`skills/aidlc-test-driven-development/SKILL.md`:
```yaml
metadata:
  skill_nature: compensation
  lifecycle: active
  model_dependency: "모델이 자발적으로 실패 테스트를 먼저 작성하지 않음"
```

`skills/aidlc-systematic-debugging/SKILL.md`:
```yaml
metadata:
  skill_nature: compensation
  lifecycle: active
  model_dependency: "모델이 원인 미확정 상태로 수정을 시도함"
```

`skills/aidlc-build-and-test/SKILL.md`:
```yaml
metadata:
  skill_nature: compensation
  lifecycle: active
  model_dependency: "모델이 빌드/테스트를 실행 없이 '통과'로 선언함"
```

- [ ] **Step 4: Tag amplification 17개**

다음 17개 SKILL.md의 `metadata:` block에 추가:
```yaml
  skill_nature: amplification
  lifecycle: active
```

대상:
`aidlc-using-devflow`, `aidlc-inception-orchestrator`, `aidlc-construction-orchestrator`, `aidlc-brainstorming`, `aidlc-workflow-planning`, `aidlc-workspace-detection`, `aidlc-requirements-analysis`, `aidlc-writing-skills`, `aidlc-superpowers-tracking`, `aidlc-requesting-code-review`, `aidlc-receiving-code-review`, `aidlc-writing-plans`, `aidlc-dispatching-parallel-agents`, `aidlc-subagent-driven-development`, `aidlc-using-git-worktrees`, `aidlc-finishing-a-development-branch`, `aidlc-auto-mode`

- [ ] **Step 5: Tag hybrid 7개 (초안 기반)**

각 SKILL.md 본문을 Read로 먼저 확인 후 `metadata:`에 추가:

`skills/aidlc-code-generation/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 TDD 순서 없이 구현하고 합리화함"
  amplification_notes: "2단계 plan+generate 구조로 설계-구현 경계 유지"
```

`skills/aidlc-executing-plans/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 세션 경계를 넘어 맥락을 유지하지 못함"
  amplification_notes: "체크포인트-재개 프로토콜로 긴 작업 추적"
```

`skills/aidlc-application-design/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 컴포넌트 경계를 임의로 결정함"
  amplification_notes: "도메인 entity + 서비스 구조 명시적 분해"
```

`skills/aidlc-functional-design/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 API 계약 없이 구현함"
  amplification_notes: "비즈니스 규칙 + 계약 선행 정의"
```

`skills/aidlc-units-generation/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 의존성 순서를 무시함"
  amplification_notes: "독립 개발/테스트 가능 단위 분해"
```

`skills/aidlc-user-stories/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 INVEST 기준 없이 작성함"
  amplification_notes: "Acceptance Criteria 강제 + 추적성"
```

`skills/aidlc-nfr-requirements/SKILL.md`:
```yaml
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 NFR을 기능 요구에 혼재시킴"
  amplification_notes: "도메인 프리셋 기반 NFR 체계화"
```

- [ ] **Step 6: Tag infrastructure 3개**

`skills/_utils/devflow-state/SKILL.md`:
```yaml
metadata:
  # ... 기존 ...
  skill_nature: null
  lifecycle: active
```

`skills/_utils/devflow-audit/SKILL.md`: 동일 패턴

`skills/_utils/devflow-solutions/SKILL.md`: 동일 패턴

- [ ] **Step 7: Run verification — verify PASS**

Run: `bash tests/verify-change-4.sh`

Expected: PASS ("Change 4 verified").

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: Skill skill_nature 일괄 태깅 — BL-081 초안 적용 (closes part of #145)

- 28 aidlc-* skill + 3 _utils skill 태깅 완료
- compensation (4): verification-before-completion, test-driven-development, systematic-debugging, build-and-test — model_dependency 1줄 필수
- amplification (17): using-devflow, orchestrator 2종, brainstorming 등 — 영구 유지
- hybrid (7): code-generation, executing-plans, application/functional-design, units-generation, user-stories, nfr-requirements — model_dependency + amplification_notes 각 1줄 필수
- infrastructure (3, _utils): skill_nature: null
- decomposition_target은 optional (Sprint 1에 label-only 방지만 + 실제 lightening 시점에 작성)

BL-081 MVP 중 규약 + 태깅 완료. Compensation Decay 분석 + validator는 BL-081 이슈에 잔존.
refs #145"
```

- [ ] **Step 9: GitHub 이슈 업데이트**

```bash
gh issue comment 145 --body "Phase 1 MVP 중 1, 2번 항목 (규약 정의, 28 skill 태깅)이 docs/research/knowledgesystem/ 설계 + 본 구현으로 완료됨. 3, 4번 항목 (Compensation Decay 분석 + validate-skills.sh 확장)은 본 이슈에 잔존."
```

---

## Task 6: `post-tool-file-edit` Hook + `hooks.json` 업데이트

**Goal:** 파일 편집 이벤트를 audit.md에 자동 append하는 L1 ingest 훅 도입. whitelist + exclusion 정밀 필터. `devflow-state.md`의 `## Last Updated`만 soft-save (race condition 방지).

**Files:**
- Create: `hooks/post-tool-file-edit`
- Modify: `hooks/hooks.json`
- Test: shell verification + simulation

---

- [ ] **Step 1: Write failing verification**

Script:
```bash
#!/bin/bash
# tests/verify-change-5.sh
set -e

HOOK="hooks/post-tool-file-edit"
CONFIG="hooks/hooks.json"

# Check 1: hook script exists + executable
if [ ! -f "$HOOK" ]; then
  echo "FAIL: $HOOK does not exist"
  exit 1
fi
if [ ! -x "$HOOK" ]; then
  echo "FAIL: $HOOK not executable"
  exit 1
fi

# Check 2: hooks.json에 PostToolUse 블록
if ! grep -q 'PostToolUse' "$CONFIG"; then
  echo "FAIL: PostToolUse block missing in $CONFIG"
  exit 1
fi

# Check 3: hook script에 exclusion + whitelist 로직
if ! grep -q 'tests/' "$HOOK"; then
  echo "FAIL: tests/ exclusion missing"
  exit 1
fi
if ! grep -q 'devflow-docs/.archive/' "$HOOK"; then
  echo "FAIL: .archive/ exclusion missing"
  exit 1
fi
if ! grep -q '## Last Updated' "$HOOK"; then
  echo "FAIL: Last Updated soft-save logic missing"
  exit 1
fi

echo "PASS: Change 5 verified"
```

- [ ] **Step 2: Run verification — verify FAIL**

Run: `bash tests/verify-change-5.sh`

Expected: FAIL (`hooks/post-tool-file-edit does not exist`).

- [ ] **Step 3: Create `hooks/post-tool-file-edit` script**

Create file `hooks/post-tool-file-edit`:

```bash
#!/bin/bash
# post-tool-file-edit — L1 auto ingest on Edit/Write tool calls
# Writes to devflow-docs/audit.md, soft-saves devflow-docs/devflow-state.md
#
# Race condition 방지 제약:
# - 이 hook은 '## Last Updated' heading 값만 수정한다.
# - 구조 섹션 (## Current Phase, ## Current Stage, ## Worktree, ## WIP 등) 절대 건드리지 않음.
# - 구조 변경은 skill(using-devflow, auto-mode 등)의 책임.

set -eo pipefail

# Tool input comes via stdin as JSON per Claude Code hook contract
INPUT=$(cat)
MODIFIED_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

# Path empty → nothing to log
[ -z "$MODIFIED_PATH" ] && exit 0

# Convert absolute to repo-relative
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
case "$MODIFIED_PATH" in
  "$REPO_ROOT"/*) REL_PATH="${MODIFIED_PATH#$REPO_ROOT/}" ;;
  /*) exit 0 ;;  # Outside repo — skip
  *) REL_PATH="$MODIFIED_PATH" ;;
esac

# === Exclusion filter (self-amplification 방지 + noise 제거) ===
case "$REL_PATH" in
  tests/*|hooks/*|.claude-plugin/*|.git/*|.worktrees/*)
    exit 0 ;;
  devflow-docs/.archive/*|devflow-docs/audit.md|devflow-docs/audit-log/*)
    exit 0 ;;
  devflow-docs/devflow-state.md|devflow-docs/session-summary.md)
    exit 0 ;;
esac

# === Whitelist filter (의미있는 지식 surface만 로깅) ===
case "$REL_PATH" in
  devflow-docs/*|docs/*|skills/*|CLAUDE.md|README.md) : ;;
  *) exit 0 ;;
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

# === devflow-state.md soft-save (## Last Updated only) ===
# 구조 섹션 절대 수정 금지 — race condition 방지.
STATE="devflow-docs/devflow-state.md"
if [ -f "$STATE" ]; then
  if grep -q '^## Last Updated' "$STATE"; then
    awk -v ts="$TS" '
      /^## Last Updated$/ { print; getline; print ts; next }
      { print }
    ' "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
  fi
fi

exit 0
```

- [ ] **Step 4: Make hook executable**

Run: `chmod +x hooks/post-tool-file-edit`

- [ ] **Step 5: Update `hooks/hooks.json`**

Modify `hooks/hooks.json`:

Before:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\""
          }
        ]
      }
    ]
  }
}
```

After:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/post-tool-file-edit\""
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 6: Run verification — verify PASS**

Run: `bash tests/verify-change-5.sh`

Expected: PASS ("Change 5 verified").

- [ ] **Step 7: Manual integration test (whitelist + exclusion)**

Create `/tmp/test-hook-input.json`:
```json
{"tool_input": {"file_path": "/Users/jay.ahn/projects/ai/devflow-aidlc-like/devflow-docs/backlog.md"}}
```

Run:
```bash
AUDIT_SIZE_BEFORE=$(wc -c < devflow-docs/audit.md 2>/dev/null || echo 0)
cat /tmp/test-hook-input.json | hooks/post-tool-file-edit
AUDIT_SIZE_AFTER=$(wc -c < devflow-docs/audit.md 2>/dev/null || echo 0)
if [ "$AUDIT_SIZE_AFTER" -gt "$AUDIT_SIZE_BEFORE" ]; then
  echo "PASS: whitelist works (audit.md grew)"
else
  echo "FAIL: whitelist broken"
fi
```

Expected: PASS.

- [ ] **Step 8: Manual exclusion test**

Create `/tmp/test-hook-input-exclude.json`:
```json
{"tool_input": {"file_path": "/Users/jay.ahn/projects/ai/devflow-aidlc-like/tests/test_sample.py"}}
```

Run:
```bash
AUDIT_SIZE_BEFORE=$(wc -c < devflow-docs/audit.md)
cat /tmp/test-hook-input-exclude.json | hooks/post-tool-file-edit
AUDIT_SIZE_AFTER=$(wc -c < devflow-docs/audit.md)
if [ "$AUDIT_SIZE_AFTER" -eq "$AUDIT_SIZE_BEFORE" ]; then
  echo "PASS: exclusion works (audit.md unchanged for tests/)"
else
  echo "FAIL: exclusion broken"
fi
```

Expected: PASS.

- [ ] **Step 9: Self-amplification test**

Create `/tmp/test-hook-input-self.json`:
```json
{"tool_input": {"file_path": "/Users/jay.ahn/projects/ai/devflow-aidlc-like/devflow-docs/audit.md"}}
```

Run:
```bash
AUDIT_SIZE_BEFORE=$(wc -c < devflow-docs/audit.md)
cat /tmp/test-hook-input-self.json | hooks/post-tool-file-edit
AUDIT_SIZE_AFTER=$(wc -c < devflow-docs/audit.md)
if [ "$AUDIT_SIZE_AFTER" -eq "$AUDIT_SIZE_BEFORE" ]; then
  echo "PASS: self-amplification prevented"
else
  echo "FAIL: self-amplification active"
fi
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "feat: post-tool-file-edit hook — L1 auto ingest

- hooks/post-tool-file-edit 신규 (whitelist + exclusion + Last Updated soft-save)
- hooks/hooks.json에 PostToolUse Edit|Write matcher 추가
- Evidence event type prefix 'file-edit' 사용 (taxonomy §2.5)
- Race condition 방지: ## Last Updated heading 값만 수정, 구조 섹션 보호
- Self-amplification 방지: audit.md/audit-log/state.md/.archive/ 제외
- Noise 제거: tests/, hooks/, .claude-plugin/, .git/, .worktrees/ 제외
- Whitelist: devflow-docs/, docs/, skills/, CLAUDE.md, README.md만 로깅
- audit.md > 100KB 시 stderr warning (Sprint 2에 실제 rotation)"
```

---

## Post-Implementation Verification

모든 Task 완료 후 전체 통합 검증:

- [ ] **Step 1: All verification scripts pass**

```bash
for t in tests/verify-change-*.sh; do
  echo "Running $t..."
  bash "$t" || { echo "FAILED: $t"; exit 1; }
done
echo "ALL CHANGES VERIFIED"
```

- [ ] **Step 2: Success Signals 12개 check (executable-next-steps.md §Success Signals)**

Manual verification per executable-next-steps.md `## Success Signals` section:
1. `rg 'devflow-audit\.md' --type md --type py` → 0 matches (excl. historical)
2. `ls devflow-docs/devflow-audit.md` → file not found
3. `grep -L 'skill_nature:' skills/aidlc-*/SKILL.md` → empty
4. `grep -L 'model_dependency:' skills/aidlc-{verification-before-completion,test-driven-development,systematic-debugging,build-and-test,code-generation,executing-plans,application-design,functional-design,units-generation,user-stories,nfr-requirements}/SKILL.md` → empty
5. `grep -L 'amplification_notes:' skills/aidlc-{code-generation,executing-plans,application-design,functional-design,units-generation,user-stories,nfr-requirements}/SKILL.md` → empty
6. `grep -L 'type: pattern' skills/_shared/patterns/*.md` → empty
7. `grep -q '^## STORE 호출' skills/aidlc-systematic-debugging/SKILL.md` → match
8. `grep -cE 'devflow-solutions.*STORE\s*\(' skills/aidlc-construction-orchestrator/SKILL.md` → 0
9. Manual hook integration test (Task 6 Step 7)
10. Manual hook exclusion test (Task 6 Step 8)
11. Manual self-amplification test (Task 6 Step 9)
12. `grep -q '## Last Updated' hooks/post-tool-file-edit && grep -vq '## Current Phase' hooks/post-tool-file-edit` — Last Updated only, structural sections not referenced

- [ ] **Step 3: 백로그 업데이트**

```bash
# devflow-docs/backlog.md에서 BL-031 다음에 knowledge-system Phase 1 완료 항목 추가 (또는 git history로만 추적)
# BL-081의 #145 이슈에 Phase 1 태깅 작업 완료 comment 달기 (Task 5 Step 9에서 이미 수행)
```

- [ ] **Step 4: 문서 승격 고려**

`docs/research/knowledgesystem/` 설계 단계 3개 문서(taxonomy / integration-plan / executable-next-steps)는 설계 완료 상태. `docs/plans/` 컨벤션 반영해 본 plan 문서가 실제 구현 plan. 구현 완료 후 추가된 phase1-overview / phase1-baseline / phase2-observation-plan / rollback-guide 4건은 Reference Docs 섹션 참조.

실행 완료 후 2주 관측 기간 시작:
- audit.md 성장률 모니터
- Solution layer 실제 생성률 관측 (첫 debugging 에피소드부터)
- Pattern frontmatter staleness 모니터 (수동)

2-3일 사용 후 레드팀 3차 리뷰 요청 권고 (운영 데이터 기반).

---

## Phase 2 Re-evaluation Criteria

> **목적**: Phase 1 실행 후 운영 데이터 기반으로 Phase 2 우선순위를 **주관 없이** 결정한다. 새 세션에서도 동일 기준으로 판단 가능하도록 측정 가능한 트리거를 명시한다.

### 관측 기간

Phase 1 실행 완료 후 **최소 2-3일**, 권장 **14일** 운영.

### 측정 대상 파일/지표 (운영 데이터 수집)

| 소스 | 수집 방법 | 측정 항목 |
|------|----------|----------|
| `devflow-docs/audit.md` | `wc -c`, `grep -c` | 파일 크기, 이벤트 유형 분포, prefix별 빈도 |
| `devflow-docs/solutions/` | `find ... \| wc -l` | Solution 파일 수, category 분포 |
| `devflow-docs/devflow-state.md` | heading 존재/누락 검사 | state 무결성 (`## Current Phase` 등) |
| Hook 실행 로그 | stderr + wall time | PostToolUse 평균/최대 실행 시간 |
| `skills/aidlc-*/SKILL.md` | skill invocation 로그 (audit.md의 stage 필드) | compensation skill gate trigger rate |
| `skills/_shared/patterns/*.md` | `last_validated` diff from today | Pattern staleness 일수 |

### Phase 2 항목별 활성화 트리거

| 트리거 ID | 측정 항목 | 임계 | 활성화 항목 | 우선도 |
|----------|----------|------|-----------|--------|
| T1 | `audit.md` 파일 크기 | > 100KB | **Change 9**: audit-log/ 자동 rotation 구현 | **High** |
| T2 | `devflow-docs/solutions/` 파일 수 (14일 관측 후) | = 0 | **구조 재검토**: STORE trigger 실패 원인 분석 → systematic-debugging 호출 경로 점검 | **Critical** |
| T3 | DUPLICATE verdict 비율 (solution-duplicate / solution-store 전체) | > 50% | **Change 10**: Solution promotion filter + error_signature 정교화 | **Mid** |
| T4 | 동일/유사 `error_signature` Solution 수 | ≥ 3건 | Solution → Pattern **수동 승격** 1건 시도 (제3자 리뷰 포함) | **Mid** |
| T5 | 실측 session-start 토큰 (baseline + state) | > 2,900 | **Change 8 재설계**: state lazy load (heading 일부만) | **High** |
| T6 | Pattern staleness: `last_validated` > 60일 파일 수 | ≥ 5건 | **Sprint 2 validator 조기 도입** (자동 staleness 경고) | **Low** |
| T7 | compensation skill gate trigger rate (audit 분석, 20 세션 윈도우) | < 5% | **BL-081 Phase 2 lightening 시작** (해당 skill을 lightened 상태로 전환) | **Mid** |
| T8 | PostToolUse hook 실행 시간 | > 500ms 평균 | **Hook 5a 경량화**: filter 단순화, jq 제거 검토 | **Mid** |
| T9 | state race 증상: `## Current Phase` heading 누락/깨짐 | ≥ 1건 | **Hook soft-save 제약 재점검** (즉시 핫픽스 필요) | **Critical** |
| T10 | audit.md signal-to-noise (file-edit 비율) | > 80% | **Change 11 (Pre-session nudge)** 조기 도입 검토 — low-signal 흡수 | **Low** |

### 우선순위 결정 규칙

**Critical > High > Mid > Low**, 동급이면 다음 규칙 적용:
1. **Solution 활성화 우선** — T2 (dead layer) 해결이 가장 중요 (knowledge compounding 존립)
2. **State 무결성** — T9 (race bug)은 즉시 핫픽스
3. **Token 예산** — T5 (overhead 초과)는 곧바로 session-start 영향
4. **Growth 관리** — T1 (audit.md 비대)은 실제 임계 도달 시에만

여러 트리거 동시 발동 시: Critical 항목 1건만 즉시 착수, 나머지는 Critical 해결 후 재평가.

### 레드팀 3차 리뷰 호출 기준

**언제**: 다음 중 **1개 이상** 만족 시
- Phase 1 실행 완료 + 14일 운영 경과
- Critical 트리거 발동 (T2 또는 T9)
- 예상치 못한 증상 발견 (예: audit.md에 이상 prefix 등장)

**호출 시 전달 자료**:
1. 본 plan의 Re-evaluation Criteria 섹션 (기준)
2. `docs/research/knowledgesystem/handoff-context.md` (설계 의도 + 과거 debate)
3. `docs/research/knowledgesystem/phase1-baseline.md` (plugin repo 기준 T0)
4. `docs/research/knowledgesystem/phase2-observation-plan.md` (consumer repo 측정 절차 + nexttui T0)
5. `docs/research/knowledgesystem/rollback-guide.md` (트리거 발동 시 옵션 중 하나)
6. 운영 데이터 스냅샷 (audit.md, solutions/ 목록, state 스냅샷)
7. 트리거 발동 현황 (T1-T10 중 어느 것이 임계 넘었는가)

### Phase 2 실행 시 의사결정 체크리스트

새 세션에서 Phase 2 판단 시 다음을 순차 검증:

1. [ ] `docs/plans/2026-04-13-knowledge-system-phase1-plan.md`의 본 섹션 읽기
2. [ ] `docs/research/knowledgesystem/handoff-context.md` 읽기 (설계 의도 복원)
3. [ ] `docs/research/knowledgesystem/phase1-overview.md` 읽기 (구현 완료 시점 상태)
4. [ ] `docs/research/knowledgesystem/phase2-observation-plan.md`의 재측정 명령을 nexttui에서 실행
5. [ ] 새 측정값을 `phase1-baseline.md` T0 값과 비교 (plugin repo 대조군)
6. [ ] 트리거 테이블로 활성화 항목 도출
7. [ ] 우선순위 결정 규칙 적용
8. [ ] 레드팀 호출 기준 체크 (필요 시 `rollback-guide.md`도 옵션 검토)
9. [ ] 의사결정: 즉시 착수 항목 1-2개 선정 + 나머지 유보
10. [ ] 신규 `docs/plans/YYYY-MM-DD-knowledge-system-phase2-*.md` plan 작성

이 체크리스트는 **주관 없이 Phase 2 우선순위를 결정**하기 위한 장치. 체크리스트 항목별로 측정치를 plan에 기록.

---

## Out of Scope (Phase 1 외)

- adr-index.json derived cache (Sprint 2+)
- Thread 개념 + stub 자동 생성 (Sprint 2+)
- Git diff catch-up (Sprint 2+)
- L2 ingest 신규 skill (Sprint 2+)
- audit.md 자동 rotation 실제 이동 (Sprint 2, 현재는 warning-only)
- YAML 마이그레이션 (state.md)
- shared/org tier 활성화 (Sprint 3+)
- BL-081 Compensation Decay 분석 + validator 확장 (BL-081 이슈 잔존)
- Pattern metadata 자동 갱신 (Sprint 2+)
- audit.md signal_level 자동 분류 / filtering (Sprint 2+, 2주 관측 데이터 후)
- hybrid 7개 `decomposition_target` 세부 작성 (실제 lightening 시점)
- Decision 14개 (`docs/plans/`) + backlog.md frontmatter 추가 (Phase B — 후속 plan)
- session-start 상태 라인 확장 (Phase E — 후속 plan)

---

## References

설계 단계:
- Taxonomy: `docs/research/knowledgesystem/knowledge-taxonomy.md`
- Integration plan: `docs/research/knowledgesystem/aidlc-knowledge-integration-plan.md`
- Executable detail: `docs/research/knowledgesystem/executable-next-steps.md`
- Red-team prompt: `docs/research/knowledgesystem/PROMPT-claude-code-knowledge-integration.md`
- 설계 의도 + debate: `docs/research/knowledgesystem/handoff-context.md`

구현 완료 후 (Phase 2 진입 시 필수):
- Phase 1 사용자 영향 요약: `docs/research/knowledgesystem/phase1-overview.md`
- Phase 1 baseline (plugin repo T0): `docs/research/knowledgesystem/phase1-baseline.md`
- Phase 2 관측 설계 (consumer repo nexttui T0): `docs/research/knowledgesystem/phase2-observation-plan.md`
- Rollback 가이드 (5-level): `docs/research/knowledgesystem/rollback-guide.md`

기타:
- BL-081 source: `docs/research/2026-04-06-skill-lifecycle-strategy.md`
- BL-081 issue: https://github.com/bluejayA/aidlc-devflow/issues/145
- Phase 1 구현 PR: https://github.com/bluejayA/aidlc-devflow/pull/157
