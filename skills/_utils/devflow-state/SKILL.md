---
name: devflow-state
description: Use when reading or writing devflow state during orchestrator execution, including phase tracking and stage completion.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

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
<!-- 현재 단계: inception | construction | operations | complete | finished -->
[phase name]

## Current Stage
<!-- 현재 실행 중인 스테이지 이름 -->
[stage name]

## Completed Stages
<!-- 완료된 스테이지 목록 (타임스탬프 포함) -->
- [stage-name]: [ISO 8601 timestamp]

## Approved Stages
<!-- workflow-planning에서 승인된 실행 예정 스테이지 목록 (depth 포함) -->
- [stage-name]: [Minimal | Standard | Comprehensive]

## Skipped Stages
<!-- 스킵된 스테이지 및 이유 -->
- [stage-name]: [reason]

## Active Unit
<!-- 현재 Construction 단계에서 작업 중인 unit 이름 -->
[unit name or "none"]

## Completed Units
<!-- 완료된 unit 목록 -->
- [unit-name]: [ISO 8601 timestamp]

## Worktree
<!-- using-git-worktrees 실행 결과 -->
- branch: [feature/xxx | none]
- path: [.worktrees/xxx | none]

## Extension Configuration
<!-- 활성화된 extension 목록 -->
- security: [enabled | disabled]
```

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
4. Set `## Current Stage` to `aidlc-workspace-detection`
