# B안 Skill Guide 준수 수정 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** skill-building-guide.md 리뷰 결과 발견된 12개 이슈를 Critical → Important → Minor 순서로 모두 수정

**Architecture:** phase3/b-plan 브랜치에서 직접 수정. 각 SKILL.md 파일을 가이드 기준(YAML frontmatter WHAT+WHEN, 에러 핸들링, 예시, 구체적 파일 경로 등)에 맞게 보완.

**Tech Stack:** Markdown (SKILL.md), YAML frontmatter

**리뷰 문서:** `docs/analysis/2026-03-10-skill-guide-review.md` (Task 0에서 생성)

---

## Task 0: 리뷰 문서 저장

**Files:**
- Create: `docs/analysis/2026-03-10-skill-guide-review.md`

**Step 1: 리뷰 문서 작성**

Create `docs/analysis/2026-03-10-skill-guide-review.md`:

```markdown
# B안 Skill Guide 준수 리뷰

- **작성일**: 2026-03-10
- **기준**: `~/.claude/projects/-Users-jay-ahn-projects-ai/memory/skill-building-guide.md`
- **대상**: `phase3/b-plan` 브랜치 — 9개 skill (using-devflow, 7개 stage skill, 2개 _utils)

---

## 발견된 이슈 (12개)

### 🔴 Critical

#### 1. `devflow-state`, `devflow-audit` — YAML frontmatter 완전 누락
- **위치**: `skills/_utils/devflow-state/SKILL.md`, `skills/_utils/devflow-audit/SKILL.md`
- **문제**: `---` 구분자, `name`, `description` 필드 없음
- **영향**: skill 로드/트리거 불가

#### 2. stage skill 7개 — description이 내부 구현 메모
- **위치**: workspace-detection, requirements-analysis, workflow-planning, application-design, units-generation, code-generation, build-and-test
- **문제**: `description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨` — WHAT+WHEN 없음
- **영향**: 오케스트레이터 호출 시 Claude가 skill을 올바르게 식별하지 못할 수 있음

#### 3. 에러 핸들링 없음 — 모든 skill
- **위치**: 전체
- **문제**: devflow-docs/ 없음, 이전 산출물 없음, units.md 없는데 multi-unit 진입 등 에러 케이스 미처리
- **영향**: 런타임 실패 시 복구 불가

---

### 🟡 Important

#### 4. `application-design`, `units-generation` — 파일 경로 미명시
- "Read requirements and workspace analysis" — 어느 파일인지 불명확

#### 5. `code-generation` PART 2 — 호출 메커니즘 불명확
- "orchestrator signals with 'generate'" — 실제 Claude 실행 방식 미명시

#### 6. `build-and-test` Step 1 — 분석 대상 미명시
- "Review generated code" — 어디를 볼지 불명확

#### 7. `using-devflow` — devflow-docs/ 디렉토리 생성 보장 없음
- devflow-state 유틸 호출 전 디렉토리 존재를 확인하는 단계 없음

#### 8. 예시(Examples) 없음 — 모든 skill
- using-devflow(진입점), code-generation(2단계 프로세스)에 특히 필요

---

### 🔵 Minor

#### 9. `using-devflow` description — trigger phrase 부족
- "AI-DLC workflow"는 사용자가 쓰는 표현이 아님

#### 10. 선택 메타데이터 없음
- version, author 미기재

#### 11. `using-devflow` Troubleshooting 없음
- 세션 재개 실패, 산출물 없음 등 케이스 미기재

#### 12. `_utils` 폴더명 규칙 검토 필요
- `_utils`는 언더스코어로 시작 — kebab-case 예외 케이스, plugin.json에서는 정상 참조됨

---

## 수정 결과

수정 완료 후 이 섹션에 결과 기록.
```

**Step 2: 커밋**

```bash
cd ~/projects/ai/aidlc-pilot
git add docs/analysis/2026-03-10-skill-guide-review.md
git commit -m "docs: B안 skill guide 준수 리뷰 문서 추가"
```

---

## Task 1: [Critical] `devflow-state` YAML frontmatter 추가

**Files:**
- Modify: `skills/_utils/devflow-state/SKILL.md`

**Step 1: frontmatter 추가**

현재 파일 맨 앞에 다음을 추가 (기존 내용 앞에 삽입):

```markdown
---
name: devflow-state
description: Reads and writes devflow-docs/devflow-state.md to track AI-DLC workflow
  progress across sessions. Called internally by using-devflow orchestrator to persist
  stage completion, current phase, and unit tracking. Do NOT invoke directly.
---

```

**Step 2: 검증**

```bash
head -6 skills/_utils/devflow-state/SKILL.md
```

Expected:
```
---
name: devflow-state
description: Reads and writes devflow-docs/devflow-state.md to track AI-DLC workflow
...
---
```

**Step 3: 커밋**

```bash
git add skills/_utils/devflow-state/SKILL.md
git commit -m "fix(b-plan): devflow-state YAML frontmatter 추가"
```

---

## Task 2: [Critical] `devflow-audit` YAML frontmatter 추가

**Files:**
- Modify: `skills/_utils/devflow-audit/SKILL.md`

**Step 1: frontmatter 추가**

현재 파일 맨 앞에 다음을 추가:

```markdown
---
name: devflow-audit
description: Appends interaction logs to devflow-docs/audit.md in append-only mode.
  Called internally by using-devflow orchestrator to record stage completions, user
  approvals, and decisions. Do NOT invoke directly — logs are append-only, never overwrite.
---

```

**Step 2: 검증**

```bash
head -6 skills/_utils/devflow-audit/SKILL.md
```

Expected: `---`, `name: devflow-audit`, `description: ...`, `---`

**Step 3: 커밋**

```bash
git add skills/_utils/devflow-audit/SKILL.md
git commit -m "fix(b-plan): devflow-audit YAML frontmatter 추가"
```

---

## Task 3: [Critical] stage skill 7개 description 재작성

**Files:**
- Modify: `skills/workspace-detection/SKILL.md`
- Modify: `skills/requirements-analysis/SKILL.md`
- Modify: `skills/workflow-planning/SKILL.md`
- Modify: `skills/application-design/SKILL.md`
- Modify: `skills/units-generation/SKILL.md`
- Modify: `skills/code-generation/SKILL.md`
- Modify: `skills/build-and-test/SKILL.md`

**Step 1: 각 파일의 description 교체**

`workspace-detection/SKILL.md` — description 교체:
```yaml
description: Scans the current workspace to detect greenfield (new project) or brownfield
  (existing codebase) project type. Called by using-devflow orchestrator as the first
  stage of AI-DLC Inception phase. Do NOT invoke directly — use using-devflow instead.
```

`requirements-analysis/SKILL.md` — description 교체:
```yaml
description: Analyzes user requirements using adaptive depth (Minimal, Standard, or
  Comprehensive) based on request complexity. Called by using-devflow orchestrator
  during AI-DLC Inception phase. Do NOT invoke directly — use using-devflow instead.
```

`workflow-planning/SKILL.md` — description 교체:
```yaml
description: Determines which Construction stages to run and at what depth, then saves
  the approved workflow plan. Called by using-devflow orchestrator during AI-DLC Inception
  phase. Do NOT invoke directly — use using-devflow instead.
```

`application-design/SKILL.md` — description 교체:
```yaml
description: Designs component and service structure before implementation begins.
  Conditionally called by using-devflow orchestrator when new components are needed
  during AI-DLC Construction phase. Do NOT invoke directly — use using-devflow instead.
```

`units-generation/SKILL.md` — description 교체:
```yaml
description: Decomposes the system into independently developable units for parallel
  implementation. Conditionally called by using-devflow orchestrator when the system
  needs decomposition during AI-DLC Construction phase. Do NOT invoke directly.
```

`code-generation/SKILL.md` — description 교체:
```yaml
description: Generates a code plan and then implements it after explicit approval.
  Called by using-devflow orchestrator for each unit during AI-DLC Construction phase.
  Two-stage process: planning first, then generation after orchestrator approval.
  Do NOT invoke directly — use using-devflow instead.
```

`build-and-test/SKILL.md` — description 교체:
```yaml
description: Generates build and test instructions after all code units are complete.
  Called by using-devflow orchestrator as the final stage of AI-DLC Construction phase.
  Do NOT invoke directly — use using-devflow instead.
```

**Step 2: 검증**

```bash
grep -A2 "^description:" skills/workspace-detection/SKILL.md
grep -A2 "^description:" skills/requirements-analysis/SKILL.md
grep -A2 "^description:" skills/code-generation/SKILL.md
```

Expected: 각각 WHAT+WHEN+Do NOT invoke 포함

**Step 3: 커밋**

```bash
git add skills/workspace-detection/SKILL.md skills/requirements-analysis/SKILL.md \
  skills/workflow-planning/SKILL.md skills/application-design/SKILL.md \
  skills/units-generation/SKILL.md skills/code-generation/SKILL.md \
  skills/build-and-test/SKILL.md
git commit -m "fix(b-plan): stage skill 7개 description WHAT+WHEN으로 재작성"
```

---

## Task 4: [Critical] 에러 핸들링 추가

**Files:**
- Modify: `skills/using-devflow/SKILL.md`
- Modify: `skills/workspace-detection/SKILL.md`
- Modify: `skills/requirements-analysis/SKILL.md`
- Modify: `skills/workflow-planning/SKILL.md`
- Modify: `skills/application-design/SKILL.md`
- Modify: `skills/units-generation/SKILL.md`
- Modify: `skills/build-and-test/SKILL.md`

**Step 1: `using-devflow`에 `## Error Handling` 섹션 추가**

`using-devflow/SKILL.md` 맨 끝에 추가:

```markdown
---

## Error Handling

### devflow-docs/ directory missing
If `devflow-docs/` does not exist when trying to read state:
- Create the directory before calling devflow-state
- Treat as a new session (no existing state)

### Stage artifact missing at resume
If resuming a session but the expected artifact file is missing
(e.g., `requirements.md` not found when starting `workflow-planning`):
1. Display warning:
   ```
   ⚠️ [stage-name] 산출물을 찾을 수 없습니다: [file-path]
   이전 단계부터 다시 실행하거나, 해당 파일을 직접 생성해주세요.
   ```
2. Offer:
   ```
   A) 이전 단계([stage-name])부터 재실행
   B) 현재 단계 그대로 진행 (산출물 없이)
   ```

### units.md missing during multi-unit code-generation
If `devflow-docs/inception/units.md` does not exist but multi-unit routing is expected:
1. Display warning:
   ```
   ⚠️ units.md를 찾을 수 없습니다.
   단일 unit으로 code-generation을 진행합니다.
   ```
2. Proceed with single-unit code-generation

### Stage skill invocation fails
If a stage skill returns an unexpected result or errors:
1. Display:
   ```
   ⚠️ [stage-name] 실행 중 오류가 발생했습니다.
   오류 내용: [error description]
   ```
2. Offer:
   ```
   A) 해당 단계 재시도
   B) 단계 스킵 (devflow-state에 skipped로 기록)
   ```
```

**Step 2: 각 stage skill에 `## Common Issues` 섹션 추가**

`workspace-detection/SKILL.md` 맨 끝에 추가:
```markdown

## Common Issues

### No files found in workspace
If the workspace appears completely empty (no files at all):
- Treat as Greenfield
- Note in the artifact: "Empty workspace — assumed Greenfield"

### Permission errors when scanning
If file scanning fails due to permissions:
- Scan only the current directory (non-recursive)
- Note limitation in the artifact
```

`requirements-analysis/SKILL.md` 맨 끝에 추가:
```markdown

## Common Issues

### User provides no requirements context
If the user's request is too vague to analyze:
- Default to Comprehensive depth
- Ask ONE clarifying question before proceeding: "What problem are you trying to solve?"

### workspace.md not found
If `devflow-docs/inception/workspace.md` does not exist:
- Proceed without it
- Note in requirements: "Workspace analysis not available"
```

`workflow-planning/SKILL.md` 맨 끝에 추가:
```markdown

## Common Issues

### requirements.md or workspace.md not found
If prior artifacts are missing:
- Proceed with available information
- Note missing context in the workflow plan
- Default to including all optional stages (safer assumption)

### No clear indication of new components needed
When it's ambiguous whether application-design is needed:
- Default to including it (conservative)
- Note the ambiguity in the workflow plan
```

`application-design/SKILL.md` 맨 끝에 추가:
```markdown

## Common Issues

### requirements.md not found
If `devflow-docs/inception/requirements.md` does not exist:
- Display: "⚠️ requirements.md를 찾을 수 없습니다. 사용자 요청 컨텍스트만으로 설계를 진행합니다."
- Proceed based on available conversation context

### No clear component boundaries
If the system is too simple to decompose into components:
- Design as a single component
- Note: "Single-component system — no decomposition needed"
```

`units-generation/SKILL.md` 맨 끝에 추가:
```markdown

## Common Issues

### application-design.md not found
If `devflow-docs/inception/application-design.md` does not exist:
- Display: "⚠️ application-design.md를 찾을 수 없습니다. requirements.md 기반으로 단위를 분해합니다."
- Proceed using requirements.md only

### Only one logical unit identified
If decomposition results in a single unit:
- Create units.md with one unit
- Orchestrator will treat this as single-unit code-generation
```

`build-and-test/SKILL.md` 맨 끝에 추가:
```markdown

## Common Issues

### No generated code found
If no source files exist outside `devflow-docs/`:
- Display: "⚠️ 생성된 코드를 찾을 수 없습니다."
- Generate placeholder instructions with: "Run after code is available"

### Unknown build tool
If the project's build system cannot be determined:
- Generate instructions for the most common tools based on file extensions:
  - `.py` files → `pip install -r requirements.txt && python -m pytest`
  - `.ts`/`.js` files → `npm install && npm test`
  - `go.mod` → `go build ./... && go test ./...`
```

**Step 3: 검증**

```bash
grep -l "## Common Issues\|## Error Handling" skills/*/SKILL.md skills/_utils/*/SKILL.md
```

Expected: using-devflow, workspace-detection, requirements-analysis, workflow-planning,
application-design, units-generation, build-and-test (7개)

**Step 4: 커밋**

```bash
git add skills/using-devflow/SKILL.md skills/workspace-detection/SKILL.md \
  skills/requirements-analysis/SKILL.md skills/workflow-planning/SKILL.md \
  skills/application-design/SKILL.md skills/units-generation/SKILL.md \
  skills/build-and-test/SKILL.md
git commit -m "fix(b-plan): 에러 핸들링 섹션 추가 (Critical)"
```

---

## Task 5: [Important] `application-design`, `units-generation` 파일 경로 명시

**Files:**
- Modify: `skills/application-design/SKILL.md`
- Modify: `skills/units-generation/SKILL.md`

**Step 1: `application-design` Step 1 수정**

현재:
```markdown
### Step 1: Load context
Read requirements and workspace analysis.
```

교체:
```markdown
### Step 1: Load context

Read the following files (if they exist):
- `devflow-docs/inception/requirements.md` — functional and non-functional requirements
- `devflow-docs/inception/workspace.md` — greenfield/brownfield context
```

**Step 2: `units-generation` Step 1 수정**

현재:
```markdown
### Step 1: Load context
Read application design and requirements documents.
```

교체:
```markdown
### Step 1: Load context

Read the following files (if they exist):
- `devflow-docs/inception/application-design.md` — component structure
- `devflow-docs/inception/requirements.md` — functional requirements
```

**Step 3: 검증**

```bash
grep -A4 "### Step 1: Load context" skills/application-design/SKILL.md
grep -A4 "### Step 1: Load context" skills/units-generation/SKILL.md
```

Expected: 두 파일 모두 `devflow-docs/inception/` 경로 포함

**Step 4: 커밋**

```bash
git add skills/application-design/SKILL.md skills/units-generation/SKILL.md
git commit -m "fix(b-plan): application-design, units-generation 파일 경로 명시"
```

---

## Task 6: [Important] `code-generation` PART 2 호출 메커니즘 명확화

**Files:**
- Modify: `skills/code-generation/SKILL.md`
- Modify: `skills/using-devflow/SKILL.md`

**Step 1: `code-generation` PART 2 설명 명확화**

현재:
```markdown
### PART 2 — Generation (오케스트레이터 승인 후)

When the orchestrator signals approval and calls this skill again with "generate":
```

교체:
```markdown
### PART 2 — Generation (오케스트레이터 승인 후)

When invoked with explicit generation instruction such as:
"code-generation: GENERATE — proceed with the approved plan for [unit-name]"

Or when the conversation context clearly contains an approved plan and the
orchestrator has signaled to proceed with generation.
```

**Step 2: `using-devflow` Routing Table에 code-generation 호출 방식 명시**

`using-devflow/SKILL.md`의 CONSTRUCTION sequence 테이블 아래에 추가:

현재:
```markdown
| `code-generation` (plan) | `code-generation` (generate) | After plan approval — call skill with "generate" signal |
```

이 줄 아래에 다음 설명 추가:
```markdown

**code-generation 2단계 호출 방법:**
- PART 1 (planning): `code-generation` skill을 일반 호출
- PART 2 (generation): 승인 후 다음 문구로 명시적 호출:
  `"code-generation: GENERATE — proceed with the approved plan for [unit-name]"`
```

**Step 3: 검증**

```bash
grep -A5 "PART 2" skills/code-generation/SKILL.md
grep -A5 "code-generation 2단계 호출" skills/using-devflow/SKILL.md
```

**Step 4: 커밋**

```bash
git add skills/code-generation/SKILL.md skills/using-devflow/SKILL.md
git commit -m "fix(b-plan): code-generation PART 2 호출 메커니즘 명확화"
```

---

## Task 7: [Important] `build-and-test` Step 1 분석 대상 명시

**Files:**
- Modify: `skills/build-and-test/SKILL.md`

**Step 1: Step 1 수정**

현재:
```markdown
### Step 1: Analyze the implementation

Review generated code to understand:
- Build tools and commands
- Test frameworks used
- Integration points between units
```

교체:
```markdown
### Step 1: Analyze the implementation

Review the following to understand the build and test requirements:

1. **Source files** in the workspace root (outside `devflow-docs/`) — look for:
   - Build configuration files: `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml`
   - Source file extensions: `.py`, `.go`, `.ts`, `.js`, `.rs`, `.java`

2. **Code plans** in `devflow-docs/construction/*/code-plan.md` — understand:
   - What files were created
   - What test files exist
   - Test framework used

3. **units.md** at `devflow-docs/inception/units.md` (if exists) — understand:
   - Integration points between units
```

**Step 2: 검증**

```bash
grep -A15 "### Step 1: Analyze" skills/build-and-test/SKILL.md
```

Expected: `devflow-docs/construction/` 및 `devflow-docs/inception/units.md` 경로 포함

**Step 3: 커밋**

```bash
git add skills/build-and-test/SKILL.md
git commit -m "fix(b-plan): build-and-test 분석 대상 파일 경로 명시"
```

---

## Task 8: [Important] `using-devflow` devflow-docs/ 디렉토리 보장

**Files:**
- Modify: `skills/using-devflow/SKILL.md`

**Step 1: New Flow Step 2 앞에 디렉토리 확인 단계 추가**

`using-devflow/SKILL.md`의 New Flow 섹션에서 Step 2 앞에 삽입:

현재 Step 2:
```markdown
### Step 2: Initialize state and audit

Use devflow-state to create initial state:
```

앞에 새 Step 삽입:
```markdown
### Step 2: Ensure devflow-docs/ directory

Before initializing state, ensure the directory exists:
- Check if `devflow-docs/` exists in the workspace root
- If not: create `devflow-docs/` and `devflow-docs/inception/` directories
- This prevents devflow-state and devflow-audit from failing on first write

### Step 3: Initialize state and audit
```

(기존 Step 2→3, Step 3→4로 번호 변경)

**Step 2: 검증**

```bash
grep -n "Ensure devflow-docs\|devflow-docs/ directory" skills/using-devflow/SKILL.md
```

Expected: 해당 라인 존재

**Step 3: 커밋**

```bash
git add skills/using-devflow/SKILL.md
git commit -m "fix(b-plan): using-devflow devflow-docs/ 디렉토리 생성 보장"
```

---

## Task 9: [Important] 주요 skill에 Examples 추가

**Files:**
- Modify: `skills/using-devflow/SKILL.md`
- Modify: `skills/code-generation/SKILL.md`

**Step 1: `using-devflow`에 `## Examples` 섹션 추가**

Error Handling 섹션 앞에 삽입:

```markdown
---

## Examples

### Example 1: 신규 Python 프로젝트 시작
User says: "FastAPI로 Todo API를 만들어줘"

1. using-devflow 활성화 → devflow-state 없음 → New Flow 시작
2. workspace-detection → Greenfield 판정
3. requirements-analysis → Standard 깊이로 API 요구사항 분석
4. workflow-planning → application-design: included, units-generation: skipped
5. application-design → API 라우터/모델/서비스 컴포넌트 설계
6. code-generation → Plan 제시 → 승인 → FastAPI 코드 생성
7. build-and-test → `pip install && pytest` 지침 생성

### Example 2: 기존 프로젝트에 기능 추가
User says: "기존 Django 앱에 알림 시스템 추가해줘"

1. using-devflow 활성화 → devflow-state 없음 → New Flow 시작
2. workspace-detection → Brownfield 판정 (Django 파일 발견)
3. requirements-analysis → Standard 깊이
4. workflow-planning → application-design: included (새 컴포넌트), units-generation: included (알림 모델/서비스/API 분리)
5. application-design → 알림 모델/서비스/API 컴포넌트 설계
6. units-generation → 3개 unit 생성: notification-model, notification-service, notification-api
7. code-generation × 3 (unit별)
8. build-and-test → 통합 테스트 포함 지침

### Example 3: 세션 재개
User says: "어제 하던 작업 이어서 해줘"

1. using-devflow 활성화 → devflow-state 발견
2. "A) 이전 작업 재개" 선택
3. requirements-analysis 완료, workflow-planning 진행 중이었음 확인
4. workflow-planning부터 재개
```

**Step 2: `code-generation`에 `## Examples` 섹션 추가**

Return to Orchestrator 섹션 앞에 삽입:

```markdown
---

## Examples

### Example 1: PART 1 — 계획 수립
Orchestrator calls: "code-generation — plan for unit: notification-service"

Output:
```markdown
# Code Generation Plan: notification-service

## Files to Create
- [ ] `notifications/service.py` — 알림 생성/조회/삭제 비즈니스 로직
- [ ] `tests/test_notification_service.py` — 서비스 단위 테스트

## Implementation Steps
- [ ] Step 1: NotificationService 클래스 스켈레톤 작성
- [ ] Step 2: create_notification() 테스트 작성 (RED)
- [ ] Step 3: create_notification() 구현 (GREEN)
- [ ] Step 4: list_notifications() 테스트 및 구현
- [ ] Step 5: delete_notification() 테스트 및 구현

## Test Strategy
- [ ] test_create_notification_success: 정상 생성 확인
- [ ] test_create_notification_invalid_user: 잘못된 사용자 처리
- [ ] test_list_notifications_empty: 빈 목록 반환
\```

### Example 2: PART 2 — 코드 생성
Orchestrator calls: "code-generation: GENERATE — proceed with the approved plan for notification-service"

Actions:
1. Step 1 실행: 스켈레톤 작성 → `[x]` 표시
2. Step 2 실행: 테스트 작성 → `[x]` 표시
3. Step 3 실행: 구현 → `[x]` 표시
4. ... (각 체크박스 즉시 업데이트)
```

**Step 3: 검증**

```bash
grep -n "## Examples" skills/using-devflow/SKILL.md skills/code-generation/SKILL.md
```

Expected: 각 파일에 1개씩 `## Examples` 존재

**Step 4: 커밋**

```bash
git add skills/using-devflow/SKILL.md skills/code-generation/SKILL.md
git commit -m "fix(b-plan): using-devflow, code-generation Examples 섹션 추가"
```

---

## Task 10: [Minor] `using-devflow` description trigger phrase 강화

**Files:**
- Modify: `skills/using-devflow/SKILL.md`

**Step 1: description 교체**

현재:
```yaml
description: Use when starting any software development task to initialize the AI-DLC workflow
```

교체:
```yaml
description: Initializes and drives the AI-DLC development workflow for any software
  project. Use when user says "let's build", "start coding", "new project", "devflow",
  "AI-DLC", or begins any software development request. Manages the full lifecycle
  from requirements through code generation.
```

**Step 2: 검증**

```bash
grep -A3 "^description:" skills/using-devflow/SKILL.md
```

Expected: "let's build", "start coding" 등 trigger phrase 포함

**Step 3: 커밋**

```bash
git add skills/using-devflow/SKILL.md
git commit -m "fix(b-plan): using-devflow description trigger phrase 강화"
```

---

## Task 11: [Minor] 전체 skill metadata version/author 추가

**Files:**
- Modify: `skills/using-devflow/SKILL.md`
- Modify: `skills/workspace-detection/SKILL.md`
- Modify: `skills/requirements-analysis/SKILL.md`
- Modify: `skills/workflow-planning/SKILL.md`
- Modify: `skills/application-design/SKILL.md`
- Modify: `skills/units-generation/SKILL.md`
- Modify: `skills/code-generation/SKILL.md`
- Modify: `skills/build-and-test/SKILL.md`
- Modify: `skills/_utils/devflow-state/SKILL.md`
- Modify: `skills/_utils/devflow-audit/SKILL.md`

**Step 1: 각 파일 frontmatter에 metadata 추가**

모든 skill의 `---` 닫는 구분자 앞에 추가:

```yaml
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
```

**Step 2: 검증**

```bash
grep -l "version: 0.2.0" skills/*/SKILL.md skills/_utils/*/SKILL.md | wc -l
```

Expected: 10 (전체 10개 skill)

**Step 3: 커밋**

```bash
git add skills/*/SKILL.md skills/_utils/*/SKILL.md
git commit -m "fix(b-plan): 전체 skill metadata (version, author) 추가"
```

---

## Task 12: [Minor] `using-devflow` Troubleshooting 섹션 추가

**Files:**
- Modify: `skills/using-devflow/SKILL.md`

**Step 1: 맨 끝에 `## Troubleshooting` 섹션 추가**

```markdown
---

## Troubleshooting

### devflow-state.md가 손상된 경우
Symptom: 상태 파일을 읽었는데 파싱이 불가능한 경우
Solution:
1. `devflow-docs/devflow-state.md` 백업 (`devflow-state-backup-[timestamp].md`로 이름 변경)
2. 새 세션으로 시작 (New Flow)
3. 이전 산출물이 `devflow-docs/inception/`에 있다면 그대로 활용 가능

### 세션 재개 시 산출물 파일이 없는 경우
Symptom: devflow-state는 `requirements-analysis: completed`인데 `requirements.md`가 없음
Solution: Error Handling 섹션의 "Stage artifact missing at resume" 절차 따름

### stage skill이 STOP하지 않고 A/B gate를 직접 제시하는 경우
Symptom: stage skill이 오케스트레이터 역할을 침범하여 직접 승인 요청
Solution:
1. 사용자에게 안내: "이 게이트는 무시하고 B를 선택해주세요"
2. 이후 오케스트레이터가 정상 게이팅을 처리
3. 해당 skill의 SKILL.md를 확인하여 "Return to Orchestrator" 섹션이 올바른지 점검

### workflow-plan.md의 included/skipped 값을 읽지 못하는 경우
Symptom: Routing Table 분기가 예상과 다르게 동작
Solution:
1. `devflow-docs/inception/workflow-plan.md` 직접 확인
2. `application-design: included` 또는 `application-design: skipped` 형식인지 검증
3. 형식이 다르면 파일을 직접 수정 후 재시도
```

**Step 2: 검증**

```bash
grep -n "## Troubleshooting" skills/using-devflow/SKILL.md
```

Expected: 1개 매칭

**Step 3: 최종 커밋**

```bash
git add skills/using-devflow/SKILL.md
git commit -m "fix(b-plan): using-devflow Troubleshooting 섹션 추가"
```

---

## 검증 기준 (전체 완료 조건)

```bash
cd ~/projects/ai/aidlc-pilot

# 1. 모든 skill에 YAML frontmatter 있는지
grep -rL "^---" skills/*/SKILL.md skills/_utils/*/SKILL.md

# 2. 모든 skill에 name: 있는지
grep -rL "^name:" skills/*/SKILL.md skills/_utils/*/SKILL.md

# 3. 모든 skill description에 "Do NOT invoke" 또는 trigger phrase 있는지
grep -rn "Do NOT invoke\|let's build\|start coding" skills/*/SKILL.md skills/_utils/*/SKILL.md | wc -l

# 4. 에러 핸들링 섹션 존재
grep -rl "## Common Issues\|## Error Handling" skills/*/SKILL.md | wc -l

# 5. metadata version 존재
grep -rl "version: 0.2.0" skills/*/SKILL.md skills/_utils/*/SKILL.md | wc -l

# 6. Examples 존재 (using-devflow, code-generation)
grep -l "## Examples" skills/using-devflow/SKILL.md skills/code-generation/SKILL.md | wc -l
```

Expected: 1번 → 빈 출력(없음), 2번 → 빈 출력, 3번 → 9+, 4번 → 7, 5번 → 10, 6번 → 2
