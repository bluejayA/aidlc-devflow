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

**Plan format (TDD order — tests first):**
```markdown
# Code Generation Plan: [unit-name]

## Test Files (Write First — TDD RED)
- [ ] `tests/path/to/test_file.py` — [what it tests]

## Test Strategy
- [ ] [test name]: [what it verifies]
- [ ] Run tests → confirm RED (failing)

## Implementation Files
- [ ] `path/to/file.py` — [purpose]

## Files to Modify
- [ ] `path/to/existing.py` — [what changes]

## Implementation Steps
- [ ] Step 1: Write failing test
- [ ] Step 2: Run test → confirm RED
- [ ] Step 3: [implement specific action]
- [ ] Step 4: Run test → confirm GREEN
- [ ] Step 5: Refactor if needed → confirm GREEN
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

1. Update devflow-state: mark this unit complete in `## Completed Units`
2. Update devflow-state: set `## Current Stage` to next stage
3. Use devflow-audit to log: "code-generation completed: [unit-name]"

Display:
```
## Code Generation 완료: [unit-name]

- 생성된 파일: [count]
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md

A) 변경 요청
B) 다음 단계로 진행
```
