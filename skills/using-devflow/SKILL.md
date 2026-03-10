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
| `code-generation` (complete) | `build-and-test` | All units done — see Multi-Unit Handling |
| `build-and-test` | END | Construction complete |

### Multi-Unit Handling

If `units-generation` was run and produced multiple units:
1. Read `devflow-docs/inception/units.md` for unit list and order
2. Track completed units in devflow-state `## Completed Units`
3. Run `code-generation` for each unit in order
4. After each unit's `code-generation`, present gate before moving to next unit
5. **"All units done"** = all unit names in `units.md` appear in `## Completed Units` in devflow-state
6. After all units complete, run `build-and-test`

**Note on routing keys**: `workflow-plan.md` stores stage decisions as `[stage]: included` or `[stage]: skipped`. Read the exact line to determine routing (e.g. `application-design: included`).

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

---

## Error Handling

### devflow-docs/ directory missing
If `devflow-docs/` does not exist when trying to read state:
- Create the directory before calling devflow-state
- Treat as a new session (no existing state)

### Stage artifact missing at resume
If resuming a session but the expected artifact file is missing
(e.g., `requirements.md` not found when starting `workflow-planning`):
1. Display warning:
   ```
   ⚠️ [stage-name] 산출물을 찾을 수 없습니다: [file-path]
   이전 단계부터 다시 실행하거나, 해당 파일을 직접 생성해주세요.
   ```
2. Offer:
   ```
   A) 이전 단계([stage-name])부터 재실행
   B) 현재 단계 그대로 진행 (산출물 없이)
   ```

### units.md missing during multi-unit code-generation
If `devflow-docs/inception/units.md` does not exist but multi-unit routing is expected:
1. Display warning:
   ```
   ⚠️ units.md를 찾을 수 없습니다.
   단일 unit으로 code-generation을 진행합니다.
   ```
2. Proceed with single-unit code-generation

### Stage skill invocation fails
If a stage skill returns an unexpected result or errors:
1. Display:
   ```
   ⚠️ [stage-name] 실행 중 오류가 발생했습니다.
   ```
2. Offer:
   ```
   A) 해당 단계 재시도
   B) 단계 스킵 (devflow-state에 skipped로 기록)
   ```
