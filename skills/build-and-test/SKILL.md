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
Expected: [description]

## Manual Verification
[any steps that can't be automated]
```

### Step 4: Update state and audit log

Mark Construction phase as complete in devflow-state.
Use devflow-audit to log: "build-and-test completed — Construction phase complete"

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
