---
name: aidlc-workspace-detection
description: Use when starting INCEPTION to detect whether the workspace is greenfield or brownfield and analyze existing code structure.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/workspace.md
---

# aidlc-workspace-detection

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 워크스페이스 분석: 그린필드/브라운필드 판단, 기존 코드베이스 스캔 -->

## Purpose

Analyze the current workspace to determine project type and context.

## Execute

### Step 0: 기존 분석 확인 (델타 모드)

`devflow-docs/inception/workspace.md`가 이미 존재하는지 확인한다.

**존재하지 않으면** → Step 1로 진행 (풀스캔)

**존재하면** → 델타 분석 수행:

1. 기존 `workspace.md`를 읽어 이전 분석 내용을 확보한다. **파싱 실패 시 (비표준 형식, 손상 등) → Step 1로 진행 (풀스캔으로 전환)**
2. 변경 감지를 수행한다:
   - 매니페스트 파일 변경 여부: `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml` 등의 존재/부재 변화 또는 내용 변경
   - Git 커밋 변화: `git log --oneline -5`로 최근 커밋이 이전 분석의 Recent Commits와 다른지 확인
   - CLAUDE.md 변경 여부: 기술 스택 섹션의 내용 변화 확인
3. 변경 판정:
   - **변경 없음**: 기존 내용 유지, `**Timestamp**`만 갱신하여 저장. `**Source**` 필드에 `이전 분석([이전 Timestamp 값]) 기반 — 변경 없음` 기록 → Step 3으로 직행
   - **변경 있음**: 아래 매핑에 따라 해당 섹션만 재분석하여 기존 내용을 업데이트. `**Source**` 필드에 `이전 분석([이전 Timestamp 값]) 기반 + 델타 업데이트` 기록 → Step 3으로 직행

**변경 유형 → 재분석 섹션 매핑:**

| 변경 감지 대상 | 재분석 섹션 |
|--------------|-----------|
| 매니페스트 파일 | Technology Stack, Key Dependencies |
| Git 커밋 | Git Activity (Recent Commits, Recent Focus) |
| CLAUDE.md 기술 스택 | Pre-specified Tech Stack |

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

**2) Git Activity** — 최근 활동 기반 핫스팟:

```bash
git log --oneline -20  # 최근 커밋 20개 요약
git log --pretty=format: --name-only -20 | sort | uniq -c | sort -rn | head -10  # 최근 변경 파일 top 10
```

수집 항목:
- 최근 커밋 메시지 요약 (진행 중인 작업 파악)
- 최근 변경이 집중된 디렉토리/파일 top 5 (핫스팟)
- 마지막 커밋 날짜 (프로젝트 활성 여부)

git 저장소가 아니면 이 항목을 스킵한다.

**3) Existing Documentation** — 기존 문서 감지:

아래 파일/디렉토리 존재 여부를 확인하고, 존재하면 핵심 내용 1~2줄 요약:

| 감지 대상 | 설명 |
|----------|------|
| `README.md` | 프로젝트 소개, 설치/실행 방법 |
| `CLAUDE.md` | Claude Code 지시사항 |
| `CONTRIBUTING.md` | 기여 가이드 |
| `ARCHITECTURE.md` | 아키텍처 문서 |
| `docs/` 디렉토리 | 추가 문서 존재 여부 + 파일 수 |
| `ADR/` 또는 `decisions/` | 아키텍처 결정 기록 |

없는 항목은 기록하지 않는다.

### Step 2b: CLAUDE.md 기술 스택 감지

> Greenfield/Brownfield 공통. Step 2a와 독립적으로 실행.

CLAUDE.md 파일의 존재를 직접 확인하고, 기술 스택 섹션을 구조적으로 파싱한다.

**감지 패턴:**
- `##` 헤딩 중 "기술 스택" 또는 "Tech Stack"을 포함하는 것
- 헤딩 하위에 `언어:`, `프레임워크:`, `DB:`, `테스트:`, `CI/CD:` 등 키-값 쌍

**감지 결과:**
- CLAUDE.md 없음 또는 기술 스택 섹션 없음 → 이 단계를 스킵 (이후 requirements-analysis에서 질문으로 수집)
- 기술 스택 섹션 있음 → 각 항목을 파싱하여 리스트로 추출

**이 단계에서 Coverage 판단은 하지 않는다.** 아키텍처 패턴이 아직 결정되지 않았으므로, 감지된 항목 목록만 기록한다. Coverage 판단은 requirements-analysis Step 2b-1에서 수행.

**제약:**
- CLAUDE.md 전체를 요약하는 것이 아닌, 기술 스택 섹션만 구조적으로 파싱
- 파싱 실패 시 (비표준 형식) 스킵

**4) Code Structure** — 디렉토리 트리 + 진입점:

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

**5) Coding Patterns (Sampled)** — 핵심 파일 샘플링:

진입점 파일 중 **가장 작은 파일 1~2개**를 실제로 읽어 코딩 패턴을 추출한다.

추출 항목:
- 네이밍 컨벤션 (camelCase, snake_case, 파일명 규칙)
- import/require 구조 (절대 경로, 상대 경로, alias)
- 에러 핸들링 패턴 (try-catch, Result type, error return)
- 주석 스타일 (JSDoc, docstring, 한국어/영어)
- 코드 구조 패턴 (함수형, 클래스 기반, 모듈 패턴)

제약:
- 200줄 이하 파일만 대상 (토큰 효율)
- 200줄 초과 시 처음 100줄만 읽기
- 진입점이 없으면 `src/` 또는 `lib/` 내 가장 작은 파일 선택
- 적절한 파일을 찾지 못하면 이 항목을 스킵한다

### Step 3: Save artifact

Create `devflow-docs/inception/workspace.md`:

```markdown
# Workspace Analysis

**Detected**: [Greenfield | Brownfield]
**Timestamp**: [ISO 8601]
**Project Root**: [현재 작업 디렉토리 절대 경로]
**Requires Path Confirmation**: [true | false]
**Source**: [신규 분석 | 이전 분석([이전 Timestamp 값]) 기반 — 변경 없음 | 이전 분석([이전 Timestamp 값]) 기반 + 델타 업데이트]

## Project Structure
[brief description of what was found]

## Key Files Found
[list of significant files, if brownfield]

<!-- CLAUDE.md에 기술 스택이 명시되어 있을 때만 포함. 없으면 이 섹션 생략. -->

## Pre-specified Tech Stack
- **Source**: CLAUDE.md
- **Items**: [감지된 항목 목록 — 키: 값 형태로 나열]

<!-- Brownfield일 때만 포함. Greenfield는 이 섹션 없이 저장. -->

## Technology Stack
- **Language**: [언어 + 버전]
- **Framework**: [프레임워크]
- **Package Manager**: [패키지 매니저]
- **Test Framework**: [테스트 프레임워크]
- **Key Dependencies**: [주요 의존성 목록]

## Git Activity
- **Last Commit**: [날짜 — 프로젝트 활성 여부]
- **Recent Focus**: [최근 변경 집중 디렉토리/파일 top 5]
- **Recent Commits**: [최근 커밋 메시지 3~5줄 요약]

## Existing Documentation
- [감지된 문서 목록 — 각 1~2줄 요약]

## Code Structure
- **Directory Layout**: [1단계 트리]
- **Entry Points**: [진입점 파일]
- **Observed Patterns**: [관찰된 패턴 — 보이는 것만]

## Coding Patterns (Sampled)
- **Source**: [샘플링한 파일명]
- **Naming**: [네이밍 컨벤션]
- **Imports**: [import 구조]
- **Error Handling**: [에러 핸들링 패턴]
- **Comments**: [주석 스타일]
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
- 사전 지정 기술 스택: [감지됨 (N개 항목) | 미지정]
- 산출물: devflow-docs/inception/workspace.md
- 리뷰: 해당 없음 (detection 스테이지 — 사실 수집만 수행)

## Common Issues

- 빈 워크스페이스 → Greenfield로 처리, 산출물에 기록
- 권한 오류 → 현재 디렉토리만 스캔 (비재귀), 산출물에 제한 기록
