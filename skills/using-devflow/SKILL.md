# using-devflow

<!-- devflow 진입점: 모든 소프트웨어 개발 시작 시 자동 활성화 -->
<!-- 세션 재개 또는 신규 워크플로우 시작을 판단 -->

## Trigger

Activate at the start of ANY software development request. Check for devflow state before doing anything else.

## On Activation

### Step 1: Check for existing session

Read `devflow-docs/devflow-state.md` using the devflow-state utility.

**If state file exists:**

Display:
```
## devflow — 진행 중인 작업 발견

현재 단계: [Current Phase] > [Current Stage]
완료된 스테이지: [list]

A) 이전 작업 재개
B) 새 작업 시작 (기존 상태 초기화)
```

Wait for user response before proceeding.

**If state file does not exist:**

Proceed to Step 2 automatically.

### Step 2: Display welcome message

```
## devflow 워크플로우 시작

AI-DLC 기반 개발 워크플로우가 활성화되었습니다.

진행 단계:
🔵 INCEPTION  → 무엇을 만들지 결정
🟢 CONSTRUCTION → 어떻게 만들지 결정
🟡 OPERATIONS  → 배포 및 운영 (준비 중)

workspace-detection 단계를 시작합니다...
```

### Step 3: Initialize audit log

Use devflow-audit to log:
- Timestamp
- User's original request (raw)
- "New devflow session started"

### Step 4: Proceed to workspace-detection

Invoke the workspace-detection skill automatically.

## Resume Behavior

When user selects "A) 이전 작업 재개":
1. Read current stage from state
2. Display summary of completed stages
3. Continue from the current stage

When user selects "B) 새 작업 시작":
1. Archive existing state (rename to `devflow-state-archived-[timestamp].md`)
2. Start fresh from workspace-detection
