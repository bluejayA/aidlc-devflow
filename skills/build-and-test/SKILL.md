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
```

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
```

## Return to Orchestrator

After saving both artifacts, display results — then STOP. Do NOT present an approval gate.

```
[build-and-test 결과]
- devflow-docs/construction/build-and-test/build-instructions.md
- devflow-docs/construction/build-and-test/test-instructions.md
```

The orchestrator handles the final completion gate and state update.
