---
name: aidlc-workspace-detection
description: Use when starting INCEPTION to detect whether the workspace is greenfield or brownfield and analyze existing code structure.
metadata:
  version: 0.4.0
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

### Step 2a: Brownfield 코드베이스 분석

> Brownfield일 때만 실행. Greenfield면 이 단계를 건너뛴다.

두 가지를 수집한다:

**1) Technology Stack** — 매니페스트 파일 파싱:

| 매니페스트 | 언어/런타임 |
|-----------|-----------|
| `package.json` | Node.js — dependencies에서 주요 프레임워크 식별 |
| `go.mod` | Go — 모듈 경로 + 주요 의존성 |
| `Cargo.toml` | Rust — [dependencies] 섹션 |
| `pyproject.toml` / `requirements.txt` | Python — 패키지 + 버전 |
| `pom.xml` / `build.gradle` | Java — 프레임워크 (Spring 등) |

추가로 빌드 도구, 테스트 프레임워크, 린터 설정 파일도 기록한다.

- 복수 매니페스트 존재 시: 모두 나열, 주 언어 판단하지 않음
- 모노레포 구조: 1단계 깊이 제약으로 하위 매니페스트는 탐색하지 않음

**2) Code Structure** — 디렉토리 트리 + 진입점:

- 1단계 깊이 디렉토리 트리 (대규모 프로젝트 토큰 방지)
- 진입점 파일 식별 (`main.py`, `index.ts`, `cmd/` 등)
- 관찰된 아키텍처 패턴 — 디렉토리 이름 기반 규칙만 적용:

| 디렉토리 패턴 | 기록할 패턴 |
|--------------|-----------|
| `controllers/` + `models/` + `views/` | MVC |
| `routes/` + `services/` + `repositories/` | 레이어 구조 |
| `cmd/` + `internal/` + `pkg/` | Go 표준 레이아웃 |
| `src/` + `tests/` | src 레이아웃 |
| 위에 해당 없음 | "특정 패턴 미감지" |

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

<!-- Brownfield일 때만 포함. Greenfield는 이 섹션 없이 저장. -->

## Technology Stack
- **Language**: [언어 + 버전]
- **Framework**: [프레임워크]
- **Package Manager**: [패키지 매니저]
- **Test Framework**: [테스트 프레임워크]
- **Key Dependencies**: [주요 의존성 목록]

## Code Structure
- **Directory Layout**: [1단계 트리]
- **Entry Points**: [진입점 파일]
- **Observed Patterns**: [관찰된 패턴 — 보이는 것만]
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
- 코드베이스 분석: [포함 | 해당 없음]
- 산출물: devflow-docs/inception/workspace.md
- 리뷰: 해당 없음 (detection 스테이지 — 사실 수집만 수행)

## Common Issues

- 빈 워크스페이스 → Greenfield로 처리, 산출물에 기록
- 권한 오류 → 현재 디렉토리만 스캔 (비재귀), 산출물에 제한 기록
