---
name: workspace-detection
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨
---

# workspace-detection

<!-- 워크스페이스 분석: 그린필드/브라운필드 판단, 기존 코드베이스 스캔 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Analyze the current workspace to determine project type and context.

## Execute

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

### Step 3: Save artifact

Create `devflow-docs/inception/workspace.md`:

```markdown
# Workspace Analysis

**Detected**: [Greenfield | Brownfield]
**Timestamp**: [ISO 8601]

## Project Structure
[brief description of what was found]

## Key Files Found
[list of significant files, if brownfield]
```

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP. Do NOT present an approval gate.

```
[workspace-detection 결과]
- 프로젝트 유형: [Greenfield | Brownfield]
- 발견된 주요 파일: [count]개
- 산출물: devflow-docs/inception/workspace.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
