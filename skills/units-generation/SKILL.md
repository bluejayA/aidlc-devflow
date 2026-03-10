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
