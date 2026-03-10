# devflow 플러그인 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** AI-DLC 방법론 기반 devflow Claude Code 플러그인 구현 (22개 skill)

**Architecture:** Enhanced Skills — 각 skill은 독립 실행 가능하며, `_utils/devflow-state`와 `_utils/devflow-audit`을 통해 상태와 로그를 공유한다. Phase 1(AI-DLC 스테이지 10개)과 Phase 2(일상 도구 12개)를 별도 git worktree에서 병행 개발한다.

**Tech Stack:** Markdown (SKILL.md), JSON (plugin.json), Git worktrees

**설계 문서:** `docs/plans/2026-03-10-devflow-design.md`
**참조 레포:** https://github.com/obra/superpowers (skills 구조 참고)

---

## 사전 준비: 프로젝트 뼈대 (main 브랜치)

### Task 0: Git Worktree 및 프로젝트 뼈대 설정

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `skills/` (디렉토리)
- Create: `skills/_utils/` (디렉토리)

**Step 1: 디렉토리 구조 생성**

```bash
cd ~/projects/ai/aidlc-pilot
mkdir -p .claude-plugin
mkdir -p skills/_utils
```

**Step 2: plugin.json 작성**

Create `.claude-plugin/plugin.json`:
```json
{
  "name": "devflow",
  "version": "0.1.0",
  "description": "AI-DLC 방법론 기반 개발 워크플로우 플러그인",
  "skills": [
    "skills/using-devflow",
    "skills/workspace-detection",
    "skills/requirements-analysis",
    "skills/workflow-planning",
    "skills/application-design",
    "skills/units-generation",
    "skills/code-generation",
    "skills/build-and-test",
    "skills/writing-plans",
    "skills/executing-plans",
    "skills/subagent-driven-development",
    "skills/dispatching-parallel-agents",
    "skills/test-driven-development",
    "skills/systematic-debugging",
    "skills/verification-before-completion",
    "skills/requesting-code-review",
    "skills/receiving-code-review",
    "skills/using-git-worktrees",
    "skills/finishing-a-development-branch",
    "skills/writing-skills",
    "skills/_utils/devflow-state",
    "skills/_utils/devflow-audit"
  ]
}
```

**Step 3: Phase 1 worktree 생성**

```bash
git checkout -b phase1/aidlc-stages
git worktree add ../aidlc-pilot-phase1 phase1/aidlc-stages
```

Expected: `../aidlc-pilot-phase1/` 디렉토리 생성됨

**Step 4: Phase 2 worktree 생성**

```bash
git checkout main
git checkout -b phase2/daily-tools
git worktree add ../aidlc-pilot-phase2 phase2/daily-tools
```

Expected: `../aidlc-pilot-phase2/` 디렉토리 생성됨

**Step 5: 뼈대 커밋 (main)**

```bash
git checkout main
git add .claude-plugin/ skills/
git commit -m "chore: 프로젝트 뼈대 및 worktree 설정"
```

**Step 6: main 변경사항을 phase1, phase2에 반영**

```bash
cd ../aidlc-pilot-phase1
git merge main

cd ../aidlc-pilot-phase2
git merge main
```

---

## Phase 1: AI-DLC 핵심 스테이지
> 작업 디렉토리: `~/projects/ai/aidlc-pilot-phase1`

### Task 1: `_utils/devflow-state` skill

**Files:**
- Create: `skills/_utils/devflow-state/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/_utils/devflow-state/SKILL.md`:
```markdown
# devflow-state

<!-- devflow-state: devflow-docs/devflow-state.md 파일을 읽고 쓰는 유틸 -->
<!-- 다른 모든 devflow skill에서 상태 공유에 사용 -->

## Purpose

Read and write `devflow-docs/devflow-state.md` to share workflow state across skills and sessions.

## State File Location

Always use `devflow-docs/devflow-state.md` relative to the project workspace root.

## State File Structure

When creating or updating the state file, maintain this exact structure:

```markdown
# devflow State

## Current Phase
<!-- 현재 단계: inception | construction | operations | complete -->
[phase name]

## Current Stage
<!-- 현재 실행 중인 스테이지 이름 -->
[stage name]

## Completed Stages
<!-- 완료된 스테이지 목록 (타임스탬프 포함) -->
- [stage-name]: [ISO 8601 timestamp]

## Skipped Stages
<!-- 스킵된 스테이지 및 이유 -->
- [stage-name]: [reason]

## Active Unit
<!-- 현재 Construction 단계에서 작업 중인 unit 이름 -->
[unit name or "none"]

## Completed Units
<!-- 완료된 unit 목록 -->
- [unit-name]: [ISO 8601 timestamp]

## Extension Configuration
<!-- 활성화된 extension 목록 -->
- security: [enabled | disabled]
\```

## Read State

When reading state:
1. Check if `devflow-docs/devflow-state.md` exists
2. If exists: parse and return the current state
3. If not exists: return default state (no active phase, no completed stages)

## Write State

When writing state:
1. Read current state file (if exists)
2. Update only the specified fields
3. Write back the full file — preserve all other fields
4. NEVER overwrite with partial content

## Create Initial State

When creating a new state file:
1. Create `devflow-docs/` directory if it doesn't exist
2. Write the state file with default values
3. Set `## Current Phase` to `inception`
4. Set `## Current Stage` to `workspace-detection`
```

**Step 2: 검증 체크리스트**

다음 항목을 확인:
- [ ] 상태 파일 경로가 `devflow-docs/devflow-state.md`로 명시됨
- [ ] 읽기/쓰기/생성 세 가지 동작이 모두 명시됨
- [ ] 부분 덮어쓰기 방지 규칙 포함됨
- [ ] 상태 파일 구조 템플릿 포함됨

**Step 3: 커밋**

```bash
git add skills/_utils/devflow-state/
git commit -m "feat: devflow-state 유틸 skill 추가"
```

---

### Task 2: `_utils/devflow-audit` skill

**Files:**
- Create: `skills/_utils/devflow-audit/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/_utils/devflow-audit/SKILL.md`:
```markdown
# devflow-audit

<!-- devflow-audit: devflow-docs/audit.md에 append-only로 모든 상호작용을 기록 -->
<!-- 사용자 입력과 AI 응답을 원문 그대로 보존 -->

## Purpose

Append interaction logs to `devflow-docs/audit.md`. This file is APPEND-ONLY — never overwrite its contents.

## Critical Rules

1. **ALWAYS append** — never use tools that overwrite the entire file
2. **Read first, then edit** — use Edit tool to append, never Write tool on the full file
3. **Raw input only** — never summarize or paraphrase user input
4. **ISO 8601 timestamps** — always include full timestamp

## Log Entry Format

Each entry must follow this exact format:

```markdown
## [Stage Name]
**Timestamp**: [YYYY-MM-DDTHH:MM:SSZ]
**User Input**: "[Complete raw user input — never summarized]"
**AI Response**: "[Action taken or response given]"
**Context**: [Stage name, decision made, or notable event]

---
\```

## When to Log

Log at these moments:
- When user sends any message during a devflow workflow
- When a stage completes (log the completion)
- When a stage is skipped (log the skip + reason)
- When user approves or requests changes at a gate

## How to Append

<!-- 올바른 방법: Read 후 Edit으로 추가 -->
1. Check if `devflow-docs/audit.md` exists
2. If not: create with header `# devflow Audit Log\n\n`
3. Append the new entry using Edit tool at end of file
4. NEVER use Write tool to rewrite the entire file

## Correct Tool Usage

✅ CORRECT:
1. Read `devflow-docs/audit.md`
2. Use Edit tool to append new entry at end

❌ WRONG:
1. Read `devflow-docs/audit.md`
2. Use Write tool with old content + new content (this is a full overwrite)
```

**Step 2: 검증 체크리스트**

- [ ] append-only 규칙이 명확히 강조됨
- [ ] 올바른/잘못된 도구 사용법이 예시로 포함됨
- [ ] 로그 포맷 템플릿 포함됨
- [ ] 언제 로그를 남길지 명시됨

**Step 3: 커밋**

```bash
git add skills/_utils/devflow-audit/
git commit -m "feat: devflow-audit 유틸 skill 추가"
```

---

### Task 3: `using-devflow` skill

**Files:**
- Create: `skills/using-devflow/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/using-devflow/SKILL.md`:
```markdown
# using-devflow

<!-- devflow 진입점: 모든 소프트웨어 개발 시작 시 자동 활성화 -->
<!-- 세션 재개 또는 신규 워크플로우 시작을 판단 -->

## Trigger

Activate at the start of ANY software development request. Check for devflow state before doing anything else.

## On Activation

### Step 1: Check for existing session

Read `devflow-docs/devflow-state.md` using the devflow-state utility.

**If state file exists:**

Display:
```
## devflow — 진행 중인 작업 발견

현재 단계: [Current Phase] > [Current Stage]
완료된 스테이지: [list]

A) 이전 작업 재개
B) 새 작업 시작 (기존 상태 초기화)
```

Wait for user response before proceeding.

**If state file does not exist:**

Proceed to Step 2 automatically.

### Step 2: Display welcome message

```
## devflow 워크플로우 시작

AI-DLC 기반 개발 워크플로우가 활성화되었습니다.

진행 단계:
🔵 INCEPTION  → 무엇을 만들지 결정
🟢 CONSTRUCTION → 어떻게 만들지 결정
🟡 OPERATIONS  → 배포 및 운영 (준비 중)

workspace-detection 단계를 시작합니다...
```

### Step 3: Initialize audit log

Use devflow-audit to log:
- Timestamp
- User's original request (raw)
- "New devflow session started"

### Step 4: Proceed to workspace-detection

Invoke the workspace-detection skill automatically.

## Resume Behavior

When user selects "A) 이전 작업 재개":
1. Read current stage from state
2. Display summary of completed stages
3. Continue from the current stage

When user selects "B) 새 작업 시작":
1. Archive existing state (rename to `devflow-state-archived-[timestamp].md`)
2. Start fresh from workspace-detection
```

**Step 2: 검증 체크리스트**

- [ ] 자동 트리거 조건 명시됨
- [ ] 세션 재개 / 신규 시작 분기 처리 포함됨
- [ ] devflow-state, devflow-audit 유틸 사용 명시됨
- [ ] workspace-detection으로 자동 전환 명시됨

**Step 3: 커밋**

```bash
git add skills/using-devflow/
git commit -m "feat: using-devflow 진입점 skill 추가"
```

---

### Task 4: `workspace-detection` skill

**Files:**
- Create: `skills/workspace-detection/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/workspace-detection/SKILL.md`:
```markdown
# workspace-detection

<!-- 워크스페이스 분석: 그린필드/브라운필드 판단, 기존 코드베이스 스캔 -->
<!-- ALWAYS 실행 — 스킵 불가 -->

## Purpose

Analyze the current workspace to determine project type and context before requirements gathering.

## Always Execute

This stage ALWAYS runs. It cannot be skipped.

## Execution Steps

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

### Step 3: Save workspace analysis

Create `devflow-docs/inception/workspace.md`:

```markdown
# Workspace Analysis

**Detected**: [Greenfield | Brownfield]
**Timestamp**: [ISO 8601]

## Project Structure
[brief description of what was found]

## Key Files Found
[list of significant files, if brownfield]

## Recommended Next Stage
requirements-analysis
\```

### Step 4: Update state

Use devflow-state to update:
- `## Current Stage` → `requirements-analysis`
- Append to `## Completed Stages`: `workspace-detection: [timestamp]`

### Step 5: Log to audit

Use devflow-audit to log the workspace detection result.

### Step 6: Completion gate

Display:
```
## Workspace Detection 완료

- 프로젝트 유형: [Greenfield | Brownfield]
- 산출물: devflow-docs/inception/workspace.md

A) 변경 요청
B) requirements-analysis 단계로 진행
```

Wait for user response before proceeding.
```

**Step 2: 검증 체크리스트**

- [ ] 그린필드/브라운필드 판단 기준 명시됨
- [ ] 산출물 파일 경로 명시됨 (`devflow-docs/inception/workspace.md`)
- [ ] devflow-state 업데이트 포함됨
- [ ] 승인 게이팅 (A/B 선택) 포함됨

**Step 3: 커밋**

```bash
git add skills/workspace-detection/
git commit -m "feat: workspace-detection skill 추가"
```

---

### Task 5: `requirements-analysis` skill

**Files:**
- Create: `skills/requirements-analysis/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/requirements-analysis/SKILL.md`:
```markdown
# requirements-analysis

<!-- 요구사항 분석: 적응형 깊이로 사용자 의도와 요구사항을 분석 -->
<!-- ALWAYS 실행 — 깊이(depth)만 조절됨 -->

## Purpose

Analyze and document requirements at a depth appropriate to the request's complexity.

## Always Execute

This stage always runs. Only the depth varies.

## Step 1: Assess complexity

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

## Step 2: Execute at chosen depth

### Minimal
1. Document user's intent in one paragraph
2. List 3-5 key acceptance criteria
3. Note any assumptions made

### Standard
1. Analyze user intent
2. List functional requirements (what the system must do)
3. List non-functional requirements (performance, security, etc.)
4. Identify constraints and assumptions
5. Note open questions (if any)

### Comprehensive
1. Full intent analysis
2. Detailed functional requirements with priority (Must/Should/Could)
3. Non-functional requirements with measurable criteria
4. Risk assessment (High/Medium/Low per requirement)
5. Dependencies and constraints
6. Open questions — ask user one at a time before proceeding

## Step 3: Ask clarifying questions (if needed)

<!-- Comprehensive 깊이에서 열린 질문이 있을 때만 -->
Ask ONE question at a time. Wait for answer before asking next.
Prefer multiple-choice over open-ended.

## Step 4: Save requirements document

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

## Step 5: Update state and audit log

Use devflow-state to update current stage to `workflow-planning`.
Use devflow-audit to log this stage completion.

## Step 6: Completion gate

Display:
```
## Requirements Analysis 완료 ([Minimal | Standard | Comprehensive])

- 산출물: devflow-docs/inception/requirements.md

A) 변경 요청
B) workflow-planning 단계로 진행
```

Wait for explicit user approval before proceeding.
```

**Step 2: 검증 체크리스트**

- [ ] 3가지 깊이 기준이 명확히 정의됨
- [ ] 각 깊이별 실행 내용이 구체적임
- [ ] 산출물 파일 구조 포함됨
- [ ] 승인 게이팅 포함됨
- [ ] 적응형 깊이 레이블이 완료 메시지에 표시됨

**Step 3: 커밋**

```bash
git add skills/requirements-analysis/
git commit -m "feat: requirements-analysis skill 추가 (적응형 깊이)"
```

---

### Task 6: `workflow-planning` skill

**Files:**
- Create: `skills/workflow-planning/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/workflow-planning/SKILL.md`:
```markdown
# workflow-planning

<!-- 워크플로우 계획: 어떤 스테이지를 실행할지 결정하고 사용자 승인을 받음 -->
<!-- ALWAYS 실행 — 반드시 명시적 사용자 승인 후 진행 -->

## Purpose

Determine which stages to execute and at what depth, then present the plan for explicit user approval.

## Always Execute

This stage always runs. User can override recommendations.

## Execution Steps

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

For each included stage, also recommend depth: Minimal / Standard / Comprehensive.

### Step 3: Generate workflow visualization

Create a simple text-based workflow diagram showing:
- Included stages in order
- Depth level for each stage
- Conditional stages marked with (?)

Example:
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

### Step 4: Present plan for approval

Display the plan and explicitly state:
```
위 계획을 검토해주세요. 스테이지를 추가하거나 제외할 수 있습니다.

A) 변경 요청 (포함/제외할 스테이지 또는 깊이 조정)
B) 계획 승인 후 진행
```

**MANDATORY**: Do NOT proceed until user explicitly selects B.

### Step 5: Save workflow plan

Create `devflow-docs/inception/workflow-plan.md` with approved plan.

### Step 6: Update state

Use devflow-state to record approved stages list.
Use devflow-audit to log approval.
```

**Step 2: 검증 체크리스트**

- [ ] 스테이지 포함 기준 테이블 포함됨
- [ ] 워크플로우 시각화 예시 포함됨
- [ ] 사용자가 스테이지 조정 가능함이 명시됨
- [ ] "MANDATORY" 승인 게이팅 강조됨

**Step 3: 커밋**

```bash
git add skills/workflow-planning/
git commit -m "feat: workflow-planning skill 추가"
```

---

### Task 7: `application-design` skill

**Files:**
- Create: `skills/application-design/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/application-design/SKILL.md`:
```markdown
# application-design

<!-- 애플리케이션 설계: 신규 컴포넌트/서비스 구조 설계 -->
<!-- 조건부 실행 — workflow-planning에서 포함된 경우만 -->

## Purpose

Design the component and service structure before implementation begins.

## Conditional Execution

**Execute if:** New components or services are needed.
**Skip if:** Changes are within existing component boundaries.

Check `devflow-docs/inception/workflow-plan.md` to confirm this stage is included.

## Execution Steps

### Step 1: Load context

Read requirements and workspace analysis.

### Step 2: Design components

For each new component/service, define:
- **Name and responsibility** (single sentence)
- **Public interface** (key methods/APIs)
- **Dependencies** (what it needs from other components)
- **Data it owns**

### Step 3: Design interactions

Describe how components interact using a simple diagram:

```
[ComponentA] --calls--> [ComponentB]
[ComponentB] --returns--> [ComponentA]
```

### Step 4: Save design document

Create `devflow-docs/inception/application-design.md`.

### Step 5: Completion gate

Display:
```
## Application Design 완료

- 산출물: devflow-docs/inception/application-design.md

A) 변경 요청
B) 다음 단계로 진행
```
```

**Step 2: 검증 체크리스트**

- [ ] 조건부 실행 조건 명시됨
- [ ] workflow-plan 확인 단계 포함됨
- [ ] 컴포넌트 설계 구조 명시됨
- [ ] 승인 게이팅 포함됨

**Step 3: 커밋**

```bash
git add skills/application-design/
git commit -m "feat: application-design skill 추가 (조건부)"
```

---

### Task 8: `units-generation` skill

**Files:**
- Create: `skills/units-generation/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/units-generation/SKILL.md`:
```markdown
# units-generation

<!-- 작업 단위 분해: 복잡한 시스템을 병렬 개발 가능한 단위로 분해 -->
<!-- 조건부 실행 — workflow-planning에서 포함된 경우만 -->

## Purpose

Decompose the system into independently developable units for parallel implementation.

## Conditional Execution

**Execute if:** System needs decomposition into multiple parallel units.
**Skip if:** Single-unit implementation is sufficient.

## Execution Steps

### Step 1: Load context

Read application design and requirements documents.

### Step 2: Identify units

Each unit must be:
- Independently implementable (minimal dependency on other units)
- Completable in a single focused session
- Testable in isolation

### Step 3: Define each unit

For each unit:
```markdown
### Unit: [unit-name]
**Responsibility**: [single sentence]
**Dependencies**: [other units this depends on, or "none"]
**Interfaces**: [what it exposes to other units]
**Implementation order**: [number — lower = implement first]
```

### Step 4: Save units document

Create `devflow-docs/inception/units.md`.

### Step 5: Update state

Record unit list in devflow-state under `## Completed Units` preparation.

### Step 6: Completion gate

Display:
```
## Units Generation 완료

단위 목록:
[list of unit names with one-line descriptions]

A) 변경 요청
B) Construction 단계로 진행 (첫 번째 unit부터)
```
```

**Step 2: 검증 체크리스트**

- [ ] 단위 분해 기준 3가지 명시됨
- [ ] 각 단위 정의 형식 포함됨
- [ ] 구현 순서 결정 포함됨
- [ ] 승인 게이팅 포함됨

**Step 3: 커밋**

```bash
git add skills/units-generation/
git commit -m "feat: units-generation skill 추가 (조건부)"
```

---

### Task 9: `code-generation` skill

**Files:**
- Create: `skills/code-generation/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/code-generation/SKILL.md`:
```markdown
# code-generation

<!-- 코드 생성: Plan → Approve → Generate 2단계 실행 -->
<!-- ALWAYS 실행 — 각 unit마다 반복 -->

## Purpose

Generate code through a two-stage process: first plan with explicit checkboxes, then execute after user approval.

## Always Execute

Runs for every unit. Cannot be skipped.

## Two-Stage Process

### PART 1 — Planning

Create a detailed code generation plan with checkboxes.

**Plan format:**
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
- [ ] ...

## Test Strategy
- [ ] [test name]: [what it verifies]
```

Present the plan and wait for approval:
```
## Code Generation Plan 준비 완료

위 계획을 검토해주세요.

A) 변경 요청
B) 계획 승인 — 코드 생성 시작
```

**MANDATORY**: Do NOT write any code until user approves the plan.

### PART 2 — Generation

After approval:
1. Execute each step in the plan
2. Mark each checkbox `[x]` **immediately** after completing that step
3. Follow TDD: write tests first, then implementation
4. Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`

## Checkbox Rules

- Update checkboxes in the SAME interaction where the work is done
- NEVER defer checkbox updates
- If a step is blocked, note the blocker in the checkbox: `- [!] Step N: BLOCKED — [reason]`

## Completion Gate

After all checkboxes are marked:
```
## Code Generation 완료: [unit-name]

- 생성된 파일: [count]
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md

A) 변경 요청
B) 다음 단계로 진행
```
```

**Step 2: 검증 체크리스트**

- [ ] 2단계 구조 (Plan → Approve → Generate) 명확히 분리됨
- [ ] "MANDATORY: 승인 전 코드 작성 금지" 강조됨
- [ ] 체크박스 즉시 업데이트 규칙 포함됨
- [ ] 산출물 저장 경로 명시됨
- [ ] 승인 게이팅 포함됨

**Step 3: 커밋**

```bash
git add skills/code-generation/
git commit -m "feat: code-generation skill 추가 (Plan→Approve→Generate)"
```

---

### Task 10: `build-and-test` skill

**Files:**
- Create: `skills/build-and-test/SKILL.md`

**Step 1: SKILL.md 작성**

Create `skills/build-and-test/SKILL.md`:
```markdown
# build-and-test

<!-- 빌드/테스트 지침 생성: 모든 unit 완료 후 실행 -->
<!-- ALWAYS 실행 — Construction의 마지막 단계 -->

## Purpose

Generate comprehensive build and test instructions after all units are implemented.

## Always Execute

Runs after all code-generation units are complete.

## Execution Steps

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
Expected: [description]

## Manual Verification
[any steps that can't be automated]
\```

### Step 4: Update state

Mark Construction phase as complete in devflow-state.

### Step 5: Completion gate

Display:
```
## Build and Test 완료

- devflow-docs/construction/build-and-test/build-instructions.md
- devflow-docs/construction/build-and-test/test-instructions.md

Construction Phase 완료. Operations Phase는 현재 준비 중입니다.

A) 변경 요청
B) 완료 확인
```
```

**Step 2: 검증 체크리스트**

- [ ] 빌드/테스트 지침 두 파일 모두 생성됨
- [ ] 정확한 커맨드와 예상 출력 포함 명시됨
- [ ] Construction 완료 상태 업데이트 포함됨
- [ ] 승인 게이팅 포함됨

**Step 3: Phase 1 최종 커밋**

```bash
git add skills/build-and-test/
git commit -m "feat: build-and-test skill 추가"

git commit -m "feat: Phase 1 AI-DLC 핵심 스테이지 완료 (10개 skill)"
```

---

## Phase 2: 일상 개발 도구
> 작업 디렉토리: `~/projects/ai/aidlc-pilot-phase2`

> **참조**: Superpowers 원본 skill을 먼저 읽고, AI-DLC 패턴을 추가하여 강화한다.
> 원본 경로: `~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1/skills/`

### Task 11-22: 일상 개발 도구 Skills

각 skill마다 동일한 패턴을 반복한다:

**공통 단계:**

**Step 1: 원본 읽기**
```bash
cat ~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1/skills/[skill-name]/SKILL.md
```

**Step 2: AI-DLC 강화 내용 적용** (아래 강화 목록 참고)

**Step 3: 검증** — 원본 기능 손실 없이 AI-DLC 패턴 추가됨을 확인

**Step 4: 커밋**
```bash
git add skills/[skill-name]/
git commit -m "feat: [skill-name] skill 추가 (superpowers 강화)"
```

---

#### Task 11: `writing-plans`

**강화 내용:**
- 계획 완료 시 `devflow-docs/plans/` 에도 저장
- 계획 제시 후 명시적 승인 게이팅 추가
- devflow-audit에 계획 생성 기록

**추가할 섹션:**
```markdown
## devflow Integration

After saving the plan to `docs/plans/`:
1. Also save to `devflow-docs/plans/[filename]` if devflow-state exists
2. Log to devflow-audit: "Plan created: [filename]"
3. Display approval gate before execution:
   ```
   계획이 저장되었습니다.
   A) 계획 수정 요청
   B) 계획 승인 — 실행 시작
   ```
```

---

#### Task 12: `executing-plans`

**강화 내용:**
- 각 태스크 완료 시 devflow-audit에 로깅
- 체크박스 업데이트 즉시 수행 규칙 강조

**추가할 섹션:**
```markdown
## devflow Integration

For each completed task:
1. Update checkbox immediately in the plan file
2. Log to devflow-audit: "Task completed: [task name]"
```

---

#### Task 13: `subagent-driven-development`

**강화 내용:**
- 서브에이전트 산출물을 `devflow-docs/construction/` 에 저장

---

#### Task 14-22: 변경 없는 Skills

다음 skills는 superpowers 원본을 그대로 복사:
- `dispatching-parallel-agents`
- `test-driven-development`
- `requesting-code-review`
- `receiving-code-review`
- `using-git-worktrees`
- `finishing-a-development-branch`

다음 skills는 devflow-audit 로깅 추가:
- `systematic-debugging` — 디버깅 세션 시작/종료 로깅
- `verification-before-completion` — 검증 결과 로깅

`writing-skills`는 devflow skill 작성 가이드 섹션 추가.

---

## 최종 통합

### Task 23: Phase 1 + Phase 2 main에 머지

**Step 1: Phase 1 머지**
```bash
cd ~/projects/ai/aidlc-pilot
git merge phase1/aidlc-stages
```

**Step 2: Phase 2 머지**
```bash
git merge phase2/daily-tools
```

**Step 3: 충돌 해결 후 최종 커밋**
```bash
git add .
git commit -m "feat: Phase 1 + Phase 2 통합 완료 — devflow v0.1.0"
```

**Step 4: Worktree 정리**
```bash
git worktree remove ../aidlc-pilot-phase1
git worktree remove ../aidlc-pilot-phase2
```

**Step 5: 검증**

다음 항목 확인:
- [ ] `skills/` 아래 22개 디렉토리 존재
- [ ] 각 디렉토리에 `SKILL.md` 존재
- [ ] `.claude-plugin/plugin.json` 의 skills 목록이 22개와 일치
- [ ] `devflow-docs/` 구조가 설계와 일치

---

## 검증 기준 (완료 조건)

| 항목 | 기준 |
|------|------|
| Skill 수 | 22개 (`skills/` 하위 디렉토리) |
| 유틸 skill | `_utils/devflow-state`, `_utils/devflow-audit` 모두 존재 |
| 승인 게이팅 | AI-DLC 스테이지 7개 모두 A/B 완료 메시지 포함 |
| 산출물 경로 | 각 skill의 산출물이 `devflow-docs/` 하위로 저장됨 |
| 적응형 깊이 | `requirements-analysis`에 Minimal/Standard/Comprehensive 3가지 명시 |
| plugin.json | 22개 skill 경로 모두 등록됨 |
