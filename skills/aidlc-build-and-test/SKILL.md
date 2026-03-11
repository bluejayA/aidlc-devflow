---
name: aidlc-build-and-test
description: aidlc 플러그인(B안) 전용 스킬. Generates build and test instructions after all code units are complete. Final Construction stage. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/build-and-test/
---

# aidlc-build-and-test

<!-- 빌드/테스트 지침 생성: 모든 unit 완료 후 실행 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Generate comprehensive build and test instructions after all units are implemented.

## Execute

### Step 1: Analyze the implementation

Review the following to understand the build and test requirements:

1. **Source files** in the workspace root (outside `devflow-docs/`) — look for:
   - Build config files: `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml`
   - Source file extensions: `.py`, `.go`, `.ts`, `.js`, `.rs`, `.java`

2. **Code plans** in `devflow-docs/construction/*/code-plan.md` — understand:
   - What files were created and what tests exist

3. **units.md** at `devflow-docs/inception/units.md` (if exists) — understand:
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

STOP here. No approval gate — orchestrator handles final completion.

```
[build-and-test 결과]
- devflow-docs/construction/build-and-test/build-instructions.md
- devflow-docs/construction/build-and-test/test-instructions.md
```

## Common Issues

### No generated code found
If no source files exist outside `devflow-docs/`:
- Display: "⚠️ 생성된 코드를 찾을 수 없습니다."
- Generate placeholder instructions: "Run after code is available"

### Unknown build tool
If the build system cannot be determined, use file extensions:
- `.py` → `pip install -r requirements.txt && python -m pytest`
- `.ts`/`.js` → `npm install && npm test`
- `go.mod` → `go build ./... && go test ./...`
- `Cargo.toml` → `cargo build && cargo test`
