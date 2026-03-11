---
name: aidlc-workflow-planning
description: aidlc 플러그인(B안) 전용 스킬. Determines which Construction stages to run and at what depth. Saves workflow plan. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/workflow-plan.md
---

# aidlc-workflow-planning

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
| `aidlc-application-design` | New components or services needed |
| `aidlc-units-generation` | System needs decomposition into parallel units |
| `aidlc-code-generation` | **Always** |
| `aidlc-build-and-test` | **Always** |

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
```

## Return to Orchestrator

STOP here. No approval gate — orchestrator handles routing, state update, and approval.

```
[workflow-planning 결과]
- 포함된 스테이지: [list]
- 스킵된 스테이지: [list]
- 산출물: devflow-docs/inception/workflow-plan.md
```

## Common Issues

### requirements.md or workspace.md not found
If prior artifacts are missing:
- Proceed with available information
- Note missing context in the workflow plan
- Default to including all optional stages (conservative assumption)

### No clear indication of new components needed
When it's ambiguous whether application-design is needed:
- Default to including it
- Note the ambiguity in the workflow plan
