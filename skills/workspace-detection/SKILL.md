# workspace-detection

<!-- 워크스페이스 분석: 그린필드/브라운필드 판단, 기존 코드베이스 스캔 -->
<!-- ALWAYS 실행 — 스킵 불가 -->

## Purpose

Analyze the current workspace to determine project type and context before requirements gathering.

## Always Execute

This stage ALWAYS runs. It cannot be skipped.

## Execution Steps

### Step 1: Scan workspace

Check for the following indicators:

**Greenfield indicators:**
- No source code files (`.py`, `.go`, `.ts`, `.js`, `.rs`, `.java`, etc.)
- No `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`, `pyproject.toml`
- No existing test files

**Brownfield indicators:**
- Existing source code files present
- Build configuration files present
- Git history with multiple commits
- Existing tests

### Step 2: Determine project type

| Result | Condition |
|--------|-----------|
| **Greenfield** | No existing code found |
| **Brownfield** | Existing code found |

### Step 3: Save workspace analysis

Create `devflow-docs/inception/workspace.md`:

```markdown
# Workspace Analysis

**Detected**: [Greenfield | Brownfield]
**Timestamp**: [ISO 8601]

## Project Structure
[brief description of what was found]

## Key Files Found
[list of significant files, if brownfield]

## Recommended Next Stage
requirements-analysis
```

### Step 4: Update state

Use devflow-state to update:
- `## Current Stage` → `requirements-analysis`
- Append to `## Completed Stages`: `workspace-detection: [timestamp]`

### Step 5: Log to audit

Use devflow-audit to log the workspace detection result.

### Step 6: Completion gate

Display:
```
## Workspace Detection 완료

- 프로젝트 유형: [Greenfield | Brownfield]
- 산출물: devflow-docs/inception/workspace.md

A) 변경 요청
B) requirements-analysis 단계로 진행
```

Wait for user response before proceeding.
