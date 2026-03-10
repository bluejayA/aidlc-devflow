---
name: using-devflow
description: Initializes and drives the AI-DLC development workflow for any software
  project. Use when user says "let's build", "start coding", "new project", "devflow",
  "AI-DLC", or begins any software development request. Manages the full lifecycle
  from requirements through code generation.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
---

# using-devflow (Orchestrator)

<!-- B안 오케스트레이터: AI-DLC Life Cycle 전체를 소유하고 구동 -->
<!-- 승인 게이팅 / devflow-state 업데이트 / devflow-audit 로깅을 모두 이 skill이 담당 -->
<!-- Stage skill은 실행만 하고, 오케스트레이터에게 결과를 반환 -->

## Trigger

Activate at the start of ANY software development request.

---

## On Activation

### Step 1: Check for existing session

Read `devflow-docs/devflow-state.md` using devflow-state utility.

**If state file exists**, display:

```
## devflow — 진행 중인 작업 발견

현재 단계: [Current Phase] > [Current Stage]
완료된 스테이지: [list]

A) 이전 작업 재개
B) 새 작업 시작 (기존 상태 초기화)
```

Wait for user selection. Then:
- A → Resume Flow (see below)
- B → Archive state file as `devflow-state-archived-[timestamp].md`, then New Flow

**If state file does not exist**, proceed to New Flow automatically.

---

## New Flow

### Step 1: Display welcome

```
## devflow 워크플로우 시작 (B안 — Orchestrator)

AI-DLC 기반 개발 워크플로우가 활성화되었습니다.

진행 단계:
🔵 INCEPTION  → 무엇을 만들지 결정
🟢 CONSTRUCTION → 어떻게 만들지 결정
🟡 OPERATIONS  → 배포 및 운영 (준비 중)
```

### Step 2: Ensure devflow-docs/ directories

Before initializing state, ensure required directories exist:
- Check if `devflow-docs/` exists in the workspace root
- If not: create `devflow-docs/`, `devflow-docs/inception/`, `devflow-docs/construction/`
- This prevents devflow-state and devflow-audit from failing on first write

### Step 3: Initialize state and audit

Use devflow-state to create initial state:
- `## Current Phase` → `inception`
- `## Current Stage` → `workspace-detection`

Use devflow-audit to log:
- Timestamp
- User's original request (raw)
- "New devflow session started (B-plan orchestrator)"

### Step 4: Start orchestration loop

Proceed to **The Orchestration Loop** below.

---

## Resume Flow

1. Read current stage from devflow-state
2. Display:
   ```
   [completed stages list] 완료
   [current stage]부터 재개합니다.
   ```
3. Use devflow-audit to log: "Session resumed at [stage]"
4. Proceed to **The Orchestration Loop** below, starting from the current stage.

---

## The Orchestration Loop

This loop runs until Construction is complete. The orchestrator owns all gates.

### Loop Iteration

**Step A: Invoke the current stage skill**

Call the skill for the current stage. Wait for it to return results and STOP.

**Step B: Display stage results**

Show what the stage returned (already displayed by the stage skill).

**Step C: Log to audit**

Use devflow-audit to log:
- Stage name
- Summary of results
- Timestamp

**Step D: Present approval gate**

Standard gate for most stages:

```
## [Stage Name] 완료

A) 변경 요청
B) 다음 단계 진행
```

**workspace-detection 전용 게이트:** `workspace.md`의 `Requires Path Confirmation` 값을 읽어 분기한다.

- `Requires Path Confirmation: true` (Greenfield) → 아래 게이트 사용:

  ```
  ## workspace-detection 완료 — Greenfield

  새 프로젝트를 어디에 만들까요?
  (예: ~/projects/my-app, ./my-app)

  경로를 입력하거나, 현재 디렉토리에 만들려면 '.' 를 입력해주세요.
  ```

  사용자가 경로를 입력하면 해당 경로를 `workspace.md`의 `Project Root`에 업데이트한 뒤 Step E로 진행.

- `Requires Path Confirmation: false` (Brownfield) → 아래 게이트 사용:

  ```
  ## workspace-detection 완료 — Brownfield

  감지된 프로젝트 경로: [Project Root 값]

  A) 경로 변경
  B) 이 경로로 진행
  ```

Wait for user selection.

- If A (또는 경로 변경 요청): Re-invoke the current stage skill with the user's change request. Repeat from Step B.
- If B: Proceed to Step E.

**Step E: Update state**

Use devflow-state to:
- Append to `## Completed Stages`: `[stage-name]: [ISO 8601 timestamp]`
- Update `## Current Stage` to the next stage

**Step F: Determine next stage**

Use the **Stage Routing Table** below to determine the next stage.

**Step G: Invoke next stage skill → repeat from Step A**

---

## Stage Routing Table

### INCEPTION sequence

| Current Stage | Next Stage | Condition |
|--------------|-----------|-----------|
| `workspace-detection` | `requirements-analysis` | Always |
| `requirements-analysis` | `workflow-planning` | Always |
| `workflow-planning` | See below | Read workflow-plan.md |

After `workflow-planning` approval:
1. Read `devflow-docs/inception/workflow-plan.md`
2. Check `application-design: included | skipped`
3. Check `units-generation: included | skipped`

Routing:
- application-design included → next: `application-design`
- application-design skipped, units-generation included → next: `units-generation`
- both skipped → next: `code-generation`

| Current Stage | Next Stage | Condition |
|--------------|-----------|-----------|
| `application-design` | `units-generation` | if units-generation included in workflow-plan |
| `application-design` | `code-generation` | if units-generation skipped |
| `units-generation` | `code-generation` | Always |

### CONSTRUCTION sequence

| Current Stage | Next Stage | Condition |
|--------------|-----------|-----------|
| `code-generation` (plan) | `code-generation` (generate) | After plan approval — call skill with "generate" signal |

**code-generation 2단계 호출 방법:**
- PART 1 (planning): `code-generation` skill을 일반 호출
- PART 2 (generation): 승인 후 명시적 호출:
  `"code-generation: GENERATE — proceed with the approved plan for [unit-name]"`
| `code-generation` (complete) | `build-and-test` | All units done — see Multi-Unit Handling |
| `build-and-test` | END | Construction complete |

### Multi-Unit Handling

If `units-generation` was run and produced multiple units:
1. Read `devflow-docs/inception/units.md` for unit list and order
2. Track completed units in devflow-state `## Completed Units`
3. Run `code-generation` for each unit in order
4. After each unit's `code-generation`, present gate before moving to next unit
5. **"All units done"** = all unit names in `units.md` appear in `## Completed Units` in devflow-state
6. After all units complete, run `build-and-test`

**Note on routing keys**: `workflow-plan.md` stores stage decisions as `[stage]: included` or `[stage]: skipped`. Read the exact line to determine routing (e.g. `application-design: included`).

---

## Construction Complete

When `build-and-test` is approved:

1. Use devflow-state to set `## Current Phase` → `complete`
2. Use devflow-audit to log "Construction phase complete"
3. Display:

```
## devflow 워크플로우 완료

🎉 Construction Phase가 완료되었습니다.

완료된 스테이지:
[list from devflow-state]

산출물 위치: devflow-docs/
Operations Phase는 현재 준비 중입니다.
```

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
4. workflow-planning → application-design: included, units-generation: included
5. application-design → 알림 모델/서비스/API 컴포넌트 설계
6. units-generation → 3개 unit: notification-model, notification-service, notification-api
7. code-generation × 3 (unit별)
8. build-and-test → 통합 테스트 포함 지침

### Example 3: 세션 재개
User says: "어제 하던 작업 이어서 해줘"

1. using-devflow 활성화 → devflow-state 발견
2. "A) 이전 작업 재개" 선택
3. requirements-analysis 완료, workflow-planning 진행 중이었음 확인
4. workflow-planning부터 재개

### Example 4: 버그 발생 시 (CONSTRUCTION 도중)
User says: "테스트가 실패해요 — TypeError: NoneType is not subscriptable"

→ using-devflow 오케스트레이터는 CONSTRUCTION을 일시 중단하고
  `devflow:systematic-debugging` 스킬을 호출하도록 안내한다.
  근본 원인 파악 없이 즉흥적으로 코드를 수정하지 않는다.

### Example 5: 완료 주장 전
User says: "구현 다 했어요"

→ using-devflow는 build-and-test로 넘어가기 전
  `devflow:verification-before-completion` 스킬을 호출하여
  실제 명령 실행 결과로 완료를 검증한다.

### Example 6: 개발 브랜치 완료 후
User says: "다 끝났어요, 이제 어떻게 하죠?"

→ `devflow:finishing-a-development-branch` 스킬을 호출하여
  병합 / PR / 유지 / 폐기 4가지 선택지를 제시한다.

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
   ```
2. Offer:
   ```
   A) 해당 단계 재시도
   B) 단계 스킵 (devflow-state에 skipped로 기록)
   ```

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
