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
