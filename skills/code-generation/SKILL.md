---
name: code-generation
description: Generates a code plan and then implements it after explicit approval.
  Called by using-devflow orchestrator for each unit during AI-DLC Construction phase.
  Two-stage process: planning first, then generation after orchestrator approval.
  Do NOT invoke directly — use using-devflow instead.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
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

When invoked with explicit generation instruction such as:
`"code-generation: GENERATE — proceed with the approved plan for [unit-name]"`

Or when the conversation context clearly contains an approved plan and the
orchestrator has signaled to proceed with generation.
1. Execute each step in the plan
2. Mark each checkbox `[x]` immediately after completing that step
3. Follow TDD: write tests first, then implementation
4. Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`

## Return to Orchestrator

After PART 1 (planning), display the plan summary — then STOP. Do NOT present an approval gate.
After PART 2 (generation), display:

```
[code-generation 완료: unit-name]
- 생성된 파일: [count]개
- 모든 체크박스 완료
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md
```

The orchestrator handles all approval gates and state updates.
