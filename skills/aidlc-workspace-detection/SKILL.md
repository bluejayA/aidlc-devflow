---
name: aidlc-workspace-detection
description: Scans the workspace to detect greenfield or brownfield project type. First stage of INCEPTION. Called by inception-orchestrator.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/workspace.md
---

# aidlc-workspace-detection

<!-- 워크스페이스 분석: 그린필드/브라운필드 판단, 기존 코드베이스 스캔 -->

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
**Project Root**: [현재 작업 디렉토리 절대 경로]
**Requires Path Confirmation**: [true | false]

## Project Structure
[brief description of what was found]

## Key Files Found
[list of significant files, if brownfield]
```

**Requires Path Confirmation 기준:**
- Greenfield → `true` (새 프로젝트 디렉토리 위치 미확정)
- Brownfield → `false` (기존 코드가 있는 위치가 곧 프로젝트 루트)

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 프로젝트 유형: [Greenfield | Brownfield]
- 감지된 경로: [절대 경로]
- 경로 확인 필요: [yes | no]
- 발견된 주요 파일: [count]개
- 산출물: devflow-docs/inception/workspace.md

## Common Issues

- 빈 워크스페이스 → Greenfield로 처리, 산출물에 기록
- 권한 오류 → 현재 디렉토리만 스캔 (비재귀), 산출물에 제한 기록
