# devflow B안 (Orchestrator-Centric) 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use devflow:executing-plans to implement this plan task-by-task.

**Goal:** C안과 비교 가능한 B안(오케스트레이터 중심) 브랜치 구현 — `using-devflow`가 AI-DLC Life Cycle 전체를 구동하고, 각 stage skill은 실행만 담당

**Architecture:** Level 2 Orchestrator — `using-devflow`가 승인 게이팅/상태 업데이트/감사 로깅을 소유. Stage skill은 도메인 실행 로직만 보유. Phase 2 일상 도구는 이 브랜치에 미포함.

**Tech Stack:** Markdown (SKILL.md), JSON (plugin.json), Git branch

**설계 문서:** `docs/plans/2026-03-10-devflow-b-plan-design.md`

---

## Task 0: 브랜치 생성 및 Phase 2 제거

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Delete: `skills/writing-plans/`, `skills/executing-plans/`, `skills/subagent-driven-development/`, `skills/dispatching-parallel-agents/`, `skills/test-driven-development/`, `skills/systematic-debugging/`, `skills/verification-before-completion/`, `skills/requesting-code-review/`, `skills/receiving-code-review/`, `skills/using-git-worktrees/`, `skills/finishing-a-development-branch/`, `skills/writing-skills/`, `skills/brainstorming/`

**Step 1: `phase3/b-plan` 브랜치 생성**

```bash
cd ~/projects/ai/aidlc-pilot
git checkout -b phase3/b-plan
```

Expected: `Switched to a new branch 'phase3/b-plan'`

**Step 2: Phase 2 skill 디렉토리 제거**

```bash
rm -rf skills/writing-plans
rm -rf skills/executing-plans
rm -rf skills/subagent-driven-development
rm -rf skills/dispatching-parallel-agents
rm -rf skills/test-driven-development
rm -rf skills/systematic-debugging
rm -rf skills/verification-before-completion
rm -rf skills/requesting-code-review
rm -rf skills/receiving-code-review
rm -rf skills/using-git-worktrees
rm -rf skills/finishing-a-development-branch
rm -rf skills/writing-skills
rm -rf skills/brainstorming
```

**Step 3: `plugin.json` 업데이트 — B안 9개 skill만 등록**

`.claude-plugin/plugin.json` 전체 내용을 다음으로 교체:

```json
{
  "name": "devflow",
  "version": "0.2.0-b-plan",
  "description": "AI-DLC 방법론 기반 개발 워크플로우 플러그인 (B안: Orchestrator-Centric)",
  "skills": {
    "using-devflow": "skills/using-devflow",
    "workspace-detection": "skills/workspace-detection",
    "requirements-analysis": "skills/requirements-analysis",
    "workflow-planning": "skills/workflow-planning",
    "application-design": "skills/application-design",
    "units-generation": "skills/units-generation",
    "code-generation": "skills/code-generation",
    "build-and-test": "skills/build-and-test",
    "devflow-state": "skills/_utils/devflow-state",
    "devflow-audit": "skills/_utils/devflow-audit"
  }
}
```

**Step 4: 검증**

```bash
ls skills/
```

Expected: `_utils  application-design  build-and-test  code-generation  requirements-analysis  units-generation  using-devflow  workflow-planning  workspace-detection`

(Phase 2 디렉토리 없음 확인)

**Step 5: 커밋**

```bash
git add -A
git commit -m "chore: phase3/b-plan 브랜치 생성, Phase 2 skill 제거"
```

---

## Task 1: `workspace-detection` — 순수 실행자로 재작성

**Files:**
- Modify: `skills/workspace-detection/SKILL.md`

**변경 내용:** Step 4 (Update state), Step 5 (Log to audit), Step 6 (Completion gate) 제거. 대신 "Return to Orchestrator" 섹션 추가.

**Step 1: SKILL.md 재작성**

`skills/workspace-detection/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: workspace-detection
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨
---

# workspace-detection

<!-- 워크스페이스 분석: 그린필드/브라운필드 판단, 기존 코드베이스 스캔 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Analyze the current workspace to determine project type and context.

## Execute

### Step 1: Scan workspace

Check for the following indicators:

**Greenfield indicators:**
- No source code files (`.py`, `.go`, `.ts`, `.js`, `.rs`, `.java`, etc.)
- No `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`, `pyproject.toml`
- No existing test files

**Brownfield indicators:**
- Existing source code files present
- Build configuration files present
- Git history with multiple commits
- Existing tests

### Step 2: Determine project type

| Result | Condition |
|--------|-----------|
| **Greenfield** | No existing code found |
| **Brownfield** | Existing code found |

### Step 3: Save artifact

Create `devflow-docs/inception/workspace.md`:

```markdown
# Workspace Analysis

**Detected**: [Greenfield | Brownfield]
**Timestamp**: [ISO 8601]

## Project Structure
[brief description of what was found]

## Key Files Found
[list of significant files, if brownfield]
\```

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP. Do NOT present an approval gate.

```
[workspace-detection 결과]
- 프로젝트 유형: [Greenfield | Brownfield]
- 발견된 주요 파일: [count]개
- 산출물: devflow-docs/inception/workspace.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
```

**Step 2: 검증 체크리스트**

- [ ] Step 4 (Update state) 없음
- [ ] Step 5 (Log to audit) 없음
- [ ] Step 6 (Completion gate / A/B 선택) 없음
- [ ] "Return to Orchestrator" 섹션 있음
- [ ] "STOP. Do NOT present an approval gate." 명시됨

**Step 3: 커밋**

```bash
git add skills/workspace-detection/SKILL.md
git commit -m "feat(b-plan): workspace-detection 순수 실행자로 재작성"
```

---

## Task 2: `requirements-analysis` — 순수 실행자로 재작성

**Files:**
- Modify: `skills/requirements-analysis/SKILL.md`

**Step 1: SKILL.md 재작성**

`skills/requirements-analysis/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: requirements-analysis
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨
---

# requirements-analysis

<!-- 요구사항 분석: 적응형 깊이로 사용자 의도와 요구사항을 분석 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Analyze and document requirements at a depth appropriate to the request's complexity.

## Execute

### Step 1: Assess complexity

Evaluate the user's request against these criteria:

**Choose Minimal if ALL of:**
- Single, clearly defined feature
- No ambiguity in requirements
- No cross-component dependencies
- Low risk (reversible, isolated)

**Choose Comprehensive if ANY of:**
- Multiple components or services affected
- High risk or irreversible changes
- Ambiguous requirements
- External integrations involved
- Performance or security critical

**Otherwise: Standard**

### Step 2: Execute at chosen depth

#### Minimal
1. Document user's intent in one paragraph
2. List 3-5 key acceptance criteria
3. Note any assumptions made

#### Standard
1. Analyze user intent
2. List functional requirements (what the system must do)
3. List non-functional requirements (performance, security, etc.)
4. Identify constraints and assumptions
5. Note open questions (if any)

#### Comprehensive
1. Full intent analysis
2. Detailed functional requirements with priority (Must/Should/Could)
3. Non-functional requirements with measurable criteria
4. Risk assessment (High/Medium/Low per requirement)
5. Dependencies and constraints
6. Open questions — ask user ONE at a time before proceeding

### Step 3: Ask clarifying questions (Comprehensive only)

<!-- Comprehensive 깊이에서 열린 질문이 있을 때만 -->
Ask ONE question at a time. Wait for answer before asking next.

### Step 4: Save artifact

Create `devflow-docs/inception/requirements.md`:

```markdown
# Requirements Analysis

**Depth**: [Minimal | Standard | Comprehensive]
**Timestamp**: [ISO 8601]

## User Intent
[What the user wants to achieve]

## Functional Requirements
[List of requirements]

## Non-Functional Requirements
[Performance, security, etc.]

## Assumptions
[List of assumptions made]

## Open Questions
[Any unresolved questions]
\```

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP. Do NOT present an approval gate.

```
[requirements-analysis 결과]
- 분석 깊이: [Minimal | Standard | Comprehensive]
- 기능 요구사항: [count]개
- 열린 질문: [count]개
- 산출물: devflow-docs/inception/requirements.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
```

**Step 2: 검증 체크리스트**

- [ ] "Step 5: Update state" 없음
- [ ] "Step 6: Completion gate" 없음
- [ ] "Return to Orchestrator" 섹션 있음
- [ ] 적응형 깊이 3가지 기준 유지됨

**Step 3: 커밋**

```bash
git add skills/requirements-analysis/SKILL.md
git commit -m "feat(b-plan): requirements-analysis 순수 실행자로 재작성"
```

---

## Task 3: `workflow-planning` — 순수 실행자로 재작성

**Files:**
- Modify: `skills/workflow-planning/SKILL.md`

**Step 1: SKILL.md 재작성**

`skills/workflow-planning/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: workflow-planning
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨
---

# workflow-planning

<!-- 워크플로우 계획: 어떤 스테이지를 실행할지 결정 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->
<!-- 중요: 이 skill의 산출물을 오케스트레이터가 읽어 조건부 스테이지를 결정 -->

## Purpose

Determine which stages to execute and at what depth.

## Execute

### Step 1: Load prior context

Read (if they exist):
- `devflow-docs/inception/workspace.md`
- `devflow-docs/inception/requirements.md`

### Step 2: Recommend stages

Based on the requirements, recommend which Construction stages to include:

| Stage | Include if |
|-------|-----------|
| `application-design` | New components or services needed |
| `units-generation` | System needs decomposition into parallel units |
| `code-generation` | **Always** |
| `build-and-test` | **Always** |

For each included stage, recommend depth: Minimal / Standard / Comprehensive.

### Step 3: Generate workflow visualization

Create a text-based workflow diagram:

```
INCEPTION
  ✅ workspace-detection (완료)
  ✅ requirements-analysis (완료)
  ⏭ workflow-planning (현재)

CONSTRUCTION
  ➡ application-design [Standard] (?)
  ➡ units-generation [Minimal] (?)
  ➡ code-generation [Standard]
  ➡ build-and-test [Standard]
```

### Step 4: Save artifact

Create `devflow-docs/inception/workflow-plan.md`:

```markdown
# Workflow Plan

**Timestamp**: [ISO 8601]

## Approved Stages

### CONSTRUCTION
- application-design: [included | skipped] — [reason]
- units-generation: [included | skipped] — [reason]
- code-generation: included — always
- build-and-test: included — always

## Stage Depths
- application-design: [Minimal | Standard | Comprehensive]
- units-generation: [Minimal | Standard | Comprehensive]
- code-generation: [Minimal | Standard | Comprehensive]
- build-and-test: [Minimal | Standard | Comprehensive]
\```

## Return to Orchestrator

After saving the artifact, display the workflow diagram — then STOP. Do NOT present an approval gate.

```
[workflow-planning 결과]
- 포함된 스테이지: [list]
- 스킵된 스테이지: [list]
- 산출물: devflow-docs/inception/workflow-plan.md
```

The orchestrator (using-devflow) will handle the approval gate, state update, and conditional stage routing.
```

**Step 2: 검증 체크리스트**

- [ ] "Step 4: Present plan for approval" (A/B gate) 없음
- [ ] "Step 5: Update state" 없음
- [ ] workflow-plan.md에 `included | skipped` 명시적으로 기록됨
- [ ] "Return to Orchestrator" 섹션 있음
- [ ] 오케스트레이터가 조건부 스테이지 결정에 이 파일을 읽음이 명시됨

**Step 3: 커밋**

```bash
git add skills/workflow-planning/SKILL.md
git commit -m "feat(b-plan): workflow-planning 순수 실행자로 재작성"
```

---

## Task 4: `application-design` + `units-generation` — 순수 실행자로 재작성

**Files:**
- Modify: `skills/application-design/SKILL.md`
- Modify: `skills/units-generation/SKILL.md`

**Step 1: `application-design` SKILL.md 재작성**

`skills/application-design/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: application-design
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨 (조건부)
---

# application-design

<!-- 애플리케이션 설계: 신규 컴포넌트/서비스 구조 설계 -->
<!-- B안: 실행 전용, 조건부 — 오케스트레이터가 workflow-plan 기반으로 호출 여부 결정 -->

## Purpose

Design the component and service structure before implementation begins.

## Execute

### Step 1: Load context

Read requirements and workspace analysis.

### Step 2: Design components

For each new component/service, define:
- **Name and responsibility** (single sentence)
- **Public interface** (key methods/APIs)
- **Dependencies** (what it needs from other components)
- **Data it owns**

### Step 3: Design interactions

Describe how components interact:

```
[ComponentA] --calls--> [ComponentB]
[ComponentB] --returns--> [ComponentA]
```

### Step 4: Save artifact

Create `devflow-docs/inception/application-design.md`.

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP.

```
[application-design 결과]
- 설계된 컴포넌트: [count]개
- 산출물: devflow-docs/inception/application-design.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
```

**Step 2: `units-generation` SKILL.md 재작성**

`skills/units-generation/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: units-generation
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨 (조건부)
---

# units-generation

<!-- 작업 단위 분해: 복잡한 시스템을 병렬 개발 가능한 단위로 분해 -->
<!-- B안: 실행 전용, 조건부 — 오케스트레이터가 workflow-plan 기반으로 호출 여부 결정 -->

## Purpose

Decompose the system into independently developable units.

## Execute

### Step 1: Load context

Read application design and requirements documents.

### Step 2: Identify units

Each unit must be:
- Independently implementable
- Completable in a single focused session
- Testable in isolation

### Step 3: Define each unit

```markdown
### Unit: [unit-name]
**Responsibility**: [single sentence]
**Dependencies**: [other units, or "none"]
**Interfaces**: [what it exposes]
**Implementation order**: [number]
```

### Step 4: Save artifact

Create `devflow-docs/inception/units.md`.

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP.

```
[units-generation 결과]
- 생성된 단위: [count]개
- 구현 순서: [unit1] → [unit2] → ...
- 산출물: devflow-docs/inception/units.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
```

**Step 3: 검증 체크리스트 (두 파일 모두)**

- [ ] Completion gate (A/B) 없음
- [ ] devflow-state 업데이트 없음
- [ ] devflow-audit 로깅 없음
- [ ] "Return to Orchestrator" 섹션 있음

**Step 4: 커밋**

```bash
git add skills/application-design/SKILL.md skills/units-generation/SKILL.md
git commit -m "feat(b-plan): application-design, units-generation 순수 실행자로 재작성"
```

---

## Task 5: `code-generation` + `build-and-test` — 순수 실행자로 재작성

**Files:**
- Modify: `skills/code-generation/SKILL.md`
- Modify: `skills/build-and-test/SKILL.md`

**Step 1: `code-generation` SKILL.md 재작성**

`skills/code-generation/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: code-generation
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨
---

# code-generation

<!-- 코드 생성: Plan 작성 후 오케스트레이터 승인을 받아 코드 생성 -->
<!-- B안: Plan 제시까지만 담당 — 승인 게이팅은 오케스트레이터 소유 -->

## Purpose

Generate a code plan and, after orchestrator approval, execute the plan.

## Two-Stage Process

### PART 1 — Planning (항상 실행)

Create a code generation plan with checkboxes:

```markdown
# Code Generation Plan: [unit-name]

## Files to Create
- [ ] `path/to/file.py` — [purpose]
- [ ] `tests/path/to/test_file.py` — [what it tests]

## Files to Modify
- [ ] `path/to/existing.py` — [what changes]

## Implementation Steps
- [ ] Step 1: [specific action]
- [ ] Step 2: [specific action]

## Test Strategy
- [ ] [test name]: [what it verifies]
```

After writing the plan, display it and STOP:

```
[code-generation Plan 준비]
- 생성할 파일: [count]개
- 수정할 파일: [count]개
- 구현 단계: [count]개
```

The orchestrator will present the approval gate. Do NOT write any code yet.

### PART 2 — Generation (오케스트레이터 승인 후)

When the orchestrator signals approval and calls this skill again with "generate":
1. Execute each step in the plan
2. Mark each checkbox `[x]` immediately after completing that step
3. Follow TDD: write tests first, then implementation
4. Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`

## Return to Orchestrator

After PART 1 (planning), display the plan summary — then STOP.
After PART 2 (generation), display:

```
[code-generation 완료: unit-name]
- 생성된 파일: [count]개
- 모든 체크박스 완료
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md
```

The orchestrator handles all approval gates and state updates.
```

**Step 2: `build-and-test` SKILL.md 재작성**

`skills/build-and-test/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: build-and-test
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨
---

# build-and-test

<!-- 빌드/테스트 지침 생성: 모든 unit 완료 후 실행 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Generate comprehensive build and test instructions after all units are implemented.

## Execute

### Step 1: Analyze the implementation

Review generated code to understand:
- Build tools and commands
- Test frameworks used
- Integration points between units

### Step 2: Generate build instructions

Create `devflow-docs/construction/build-and-test/build-instructions.md`:

```markdown
# Build Instructions

## Prerequisites
[tools and versions required]

## Steps
1. [exact command]
2. [exact command]

## Expected Output
[what success looks like]
\```

### Step 3: Generate test instructions

Create `devflow-docs/construction/build-and-test/test-instructions.md`:

```markdown
# Test Instructions

## Unit Tests
Run: `[exact command]`
Expected: [number] tests pass

## Integration Tests
Run: `[exact command]`

## Manual Verification
[any steps that can't be automated]
\```

## Return to Orchestrator

After saving both artifacts, display results — then STOP.

```
[build-and-test 결과]
- devflow-docs/construction/build-and-test/build-instructions.md
- devflow-docs/construction/build-and-test/test-instructions.md
```

The orchestrator handles the final completion gate and state update.
```

**Step 3: 검증 체크리스트**

code-generation:
- [ ] "MANDATORY: 승인 전 코드 작성 금지" → 오케스트레이터 위임으로 변경됨
- [ ] PART 1 이후 STOP 명시됨
- [ ] PART 2는 오케스트레이터 승인 신호 후에만 실행됨

build-and-test:
- [ ] Completion gate 없음
- [ ] "Construction Phase 완료" 메시지 없음 (오케스트레이터 담당)
- [ ] "Return to Orchestrator" 있음

**Step 4: 커밋**

```bash
git add skills/code-generation/SKILL.md skills/build-and-test/SKILL.md
git commit -m "feat(b-plan): code-generation, build-and-test 순수 실행자로 재작성"
```

---

## Task 6: `using-devflow` — 오케스트레이터로 완전 재작성 (핵심)

**Files:**
- Modify: `skills/using-devflow/SKILL.md`

**Step 1: SKILL.md 재작성**

`skills/using-devflow/SKILL.md` 전체를 다음으로 교체:

```markdown
---
name: using-devflow
description: Use when starting any software development task to initialize the AI-DLC workflow
---

# using-devflow (Orchestrator)

<!-- B안 오케스트레이터: AI-DLC Life Cycle 전체를 소유하고 구동 -->
<!-- 승인 게이팅 / devflow-state 업데이트 / devflow-audit 로깅을 모두 이 skill이 담당 -->
<!-- Stage skill은 실행만 하고, 오케스트레이터에게 결과를 반환 -->

## Trigger

Activate at the start of ANY software development request.

---

## On Activation

### Step 1: Check for existing session

Read `devflow-docs/devflow-state.md` using devflow-state utility.

**If state file exists**, display:

```
## devflow — 진행 중인 작업 발견

현재 단계: [Current Phase] > [Current Stage]
완료된 스테이지: [list]

A) 이전 작업 재개
B) 새 작업 시작 (기존 상태 초기화)
```

Wait for user selection. Then:
- A → Resume Flow (see below)
- B → Archive state file as `devflow-state-archived-[timestamp].md`, then New Flow

**If state file does not exist**, proceed to New Flow automatically.

---

## New Flow

### Step 1: Display welcome

```
## devflow 워크플로우 시작 (B안 — Orchestrator)

AI-DLC 기반 개발 워크플로우가 활성화되었습니다.

진행 단계:
🔵 INCEPTION  → 무엇을 만들지 결정
🟢 CONSTRUCTION → 어떻게 만들지 결정
🟡 OPERATIONS  → 배포 및 운영 (준비 중)
```

### Step 2: Initialize state and audit

Use devflow-state to create initial state:
- `## Current Phase` → `inception`
- `## Current Stage` → `workspace-detection`

Use devflow-audit to log:
- Timestamp
- User's original request (raw)
- "New devflow session started (B-plan orchestrator)"

### Step 3: Start orchestration loop

Proceed to **The Orchestration Loop** below.

---

## Resume Flow

1. Read current stage from devflow-state
2. Display:
   ```
   [completed stages list] 완료
   [current stage]부터 재개합니다.
   ```
3. Use devflow-audit to log: "Session resumed at [stage]"
4. Proceed to **The Orchestration Loop** below, starting from the current stage.

---

## The Orchestration Loop

This loop runs until Construction is complete. The orchestrator owns all gates.

### Loop Iteration

**Step A: Invoke the current stage skill**

Call the skill for the current stage. Wait for it to return results and STOP.

**Step B: Display stage results**

Show what the stage returned (already displayed by the stage skill).

**Step C: Log to audit**

Use devflow-audit to log:
- Stage name
- Summary of results
- Timestamp

**Step D: Present approval gate**

```
## [Stage Name] 완료

A) 변경 요청
B) 다음 단계 진행
```

Wait for user selection.

- If A: Re-invoke the current stage skill with the user's change request. Repeat from Step B.
- If B: Proceed to Step E.

**Step E: Update state**

Use devflow-state to:
- Append to `## Completed Stages`: `[stage-name]: [ISO 8601 timestamp]`
- Update `## Current Stage` to the next stage

**Step F: Determine next stage**

Use the **Stage Routing Table** below to determine the next stage.

**Step G: Invoke next stage skill → repeat from Step A**

---

## Stage Routing Table

### INCEPTION sequence

| Current Stage | Next Stage | Condition |
|--------------|-----------|-----------|
| `workspace-detection` | `requirements-analysis` | Always |
| `requirements-analysis` | `workflow-planning` | Always |
| `workflow-planning` | See below | Read workflow-plan.md |

After `workflow-planning` approval:
1. Read `devflow-docs/inception/workflow-plan.md`
2. Check `application-design: included | skipped`
3. Check `units-generation: included | skipped`

Routing:
- application-design included → next: `application-design`
- application-design skipped, units-generation included → next: `units-generation`
- both skipped → next: `code-generation`

| Current Stage | Next Stage | Condition |
|--------------|-----------|-----------|
| `application-design` | `units-generation` | if units-generation included in workflow-plan |
| `application-design` | `code-generation` | if units-generation skipped |
| `units-generation` | `code-generation` | Always |

### CONSTRUCTION sequence

| Current Stage | Next Stage | Condition |
|--------------|-----------|-----------|
| `code-generation` (plan) | `code-generation` (generate) | After plan approval — call skill with "generate" signal |
| `code-generation` (complete) | `build-and-test` | All units done |
| `build-and-test` | END | Construction complete |

### Multi-Unit Handling

If `units-generation` was run and produced multiple units:
1. Read `devflow-docs/inception/units.md` for unit list and order
2. Run `code-generation` for each unit in order
3. After each unit's `code-generation`, present gate before moving to next unit
4. After all units complete, run `build-and-test`

---

## Construction Complete

When `build-and-test` is approved:

1. Use devflow-state to set `## Current Phase` → `complete`
2. Use devflow-audit to log "Construction phase complete"
3. Display:

```
## devflow 워크플로우 완료

🎉 Construction Phase가 완료되었습니다.

완료된 스테이지:
[list from devflow-state]

산출물 위치: devflow-docs/
Operations Phase는 현재 준비 중입니다.
```
```

**Step 2: 검증 체크리스트**

- [ ] 모든 `devflow-state` 업데이트가 오케스트레이터에 있음 (stage skill에 없음)
- [ ] 모든 `devflow-audit` 로깅이 오케스트레이터에 있음
- [ ] 모든 A/B 승인 게이트가 오케스트레이터에 있음
- [ ] Stage Routing Table이 모든 분기를 커버함
- [ ] Multi-unit 처리 로직 포함됨
- [ ] code-generation의 2단계 (plan → generate) 오케스트레이션 명시됨
- [ ] 세션 재개(Resume Flow) 로직 포함됨

**Step 3: 커밋**

```bash
git add skills/using-devflow/SKILL.md
git commit -m "feat(b-plan): using-devflow 오케스트레이터로 완전 재작성 (핵심 변경)"
```

---

## Task 7: 최종 검증 및 브랜치 정리

**Step 1: skills 디렉토리 구조 확인**

```bash
ls skills/
ls skills/_utils/
```

Expected:
```
_utils  application-design  build-and-test  code-generation
requirements-analysis  units-generation  using-devflow
workflow-planning  workspace-detection
```

```
devflow-audit  devflow-state
```

**Step 2: plugin.json 확인**

```bash
cat .claude-plugin/plugin.json
```

Expected: version `0.2.0-b-plan`, 10개 항목 (8개 stage + 2개 utils)

**Step 3: 각 stage skill에 Completion gate 없음 확인**

```bash
grep -r "A) 변경" skills/ --include="*.md" -l
```

Expected: `skills/using-devflow/SKILL.md` 만 나와야 함

**Step 4: 오케스트레이터에 Stage Routing Table 있음 확인**

```bash
grep "Stage Routing Table" skills/using-devflow/SKILL.md
```

Expected: 1개 매칭

**Step 5: 최종 커밋**

```bash
git add .
git commit -m "feat(b-plan): B안 Level 2 오케스트레이터 구현 완료 v0.2.0-b-plan"
```

**Step 6: 브랜치 원격 푸시 (선택)**

```bash
git push origin phase3/b-plan
```

---

## 검증 기준 (완료 조건)

| 항목 | 기준 |
|------|------|
| 브랜치 | `phase3/b-plan` 존재, `main` 미수정 |
| Skill 수 | 9개 (`_utils` 포함하면 10개) |
| Phase 2 제거 | 12개 일상 도구 skill 미존재 |
| 승인 게이트 위치 | `using-devflow`에만 존재 |
| State 업데이트 위치 | `using-devflow`에만 존재 |
| Audit 로깅 위치 | `using-devflow`에만 존재 |
| Stage Routing Table | 모든 분기 커버 |
| `grep` 검증 | stage skill에서 "A) 변경" 없음 |
