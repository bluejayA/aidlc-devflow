---
name: application-design
description: Use when new components or services need structural design before implementation begins, as determined by workflow-planning
---

# application-design

<!-- 애플리케이션 설계: 신규 컴포넌트/서비스 구조 설계 -->
<!-- 조건부 실행 — workflow-planning에서 포함된 경우만 -->

## Purpose

Design the component and service structure before implementation begins.

## Conditional Execution

**Execute if:** New components or services are needed.
**Skip if:** Changes are within existing component boundaries.

Check `devflow-docs/inception/workflow-plan.md` to confirm this stage is included.

## Execution Steps

### Step 1: Load context

Read requirements and workspace analysis.

### Step 2: Design components

For each new component/service, define:
- **Name and responsibility** (single sentence)
- **Public interface** (key methods/APIs)
- **Dependencies** (what it needs from other components)
- **Data it owns**

### Step 3: Design interactions

Describe how components interact using a simple diagram:

```
[ComponentA] --calls--> [ComponentB]
[ComponentB] --returns--> [ComponentA]
```

### Step 4: Save design document

Create `devflow-docs/inception/application-design.md`.

### Step 5: Completion gate

Display:
```
## Application Design 완료

- 산출물: devflow-docs/inception/application-design.md

A) 변경 요청
B) 다음 단계로 진행
```
