# Brownfield 코드베이스 분석 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** workspace-detection의 Brownfield 경로를 확장하여 technology-stack과 code-structure를 수집한다.

**Complexity:** Minimal

**Architecture:** 기존 `aidlc-workspace-detection/SKILL.md`에 Step 2a를 추가하고, 산출물 템플릿과 Return 필드를 확장한다.

**Tech Stack:** Markdown (스킬 정의 파일)

---

## Chunk 1: workspace-detection 확장

### Task 1: Step 2a + 산출물 템플릿 + Return 필드 확장

**Files:**
- Modify: `skills/aidlc-workspace-detection/SKILL.md`

**참조:**
- 설계 문서: `docs/plans/2026-03-13-brownfield-analysis-design.md`
- 기존 파일 현재 내용: 81줄, Step 1~3 + Return + Common Issues 구조

- [ ] **Step 1: Step 2a "Brownfield 코드베이스 분석" 추가**

Step 2 "Determine project type" 테이블 바로 아래, Step 3 "Save artifact" 앞에 삽입:

```markdown
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
```

- [ ] **Step 2: 산출물 템플릿에 Brownfield 섹션 추가**

기존 Step 3 "Save artifact"의 `workspace.md` 템플릿에서, `## Key Files Found` 아래에 Brownfield 전용 섹션 2개를 추가:

```markdown
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

템플릿 바로 위에 `> Brownfield일 때만 포함. Greenfield는 이 섹션 없이 저장.` 안내를 추가한다.

- [ ] **Step 3: Return 필드 확장**

기존 Return to Orchestrator 섹션의 필드 목록에 2개 추가:

```markdown
- 코드베이스 분석: [포함 | 해당 없음]
- 리뷰: 해당 없음 (detection 스테이지 — 사실 수집만 수행)
```

- [ ] **Step 4: 버전 bump**

YAML 메타데이터의 `version: 0.3.0` → `version: 0.4.0`

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-workspace-detection/SKILL.md
git commit -m "feat: workspace-detection Brownfield 경로에 tech-stack + code-structure 분석 추가"
```

---

### Task 2: README 현행화

**Files:**
- Modify: `README.md`

- [ ] **Step 1: workspace-detection 설명 업데이트**

README의 스킬 설명 테이블에서 `aidlc-workspace-detection`의 설명을 업데이트하여 Brownfield 분석 기능 추가를 반영한다.

- [ ] **Step 2: 커밋**

```bash
git add README.md
git commit -m "docs: README에 workspace-detection Brownfield 분석 기능 반영"
```
