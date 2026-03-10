---
name: application-design
description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨 (조건부)
---

# application-design

<!-- 애플리케이션 설계: 신규 컴포넌트/서비스 구조 설계 -->
<!-- B안: 실행 전용, 조건부 — 오케스트레이터가 workflow-plan 기반으로 호출 여부 결정 -->

## Purpose

Design the component and service structure before implementation begins.

## Execute

### Step 1: Load context

Read requirements and workspace analysis.

### Step 2: Design components

For each new component/service, define:
- **Name and responsibility** (single sentence)
- **Public interface** (key methods/APIs)
- **Dependencies** (what it needs from other components)
- **Data it owns**

### Step 3: Design interactions

Describe how components interact:

```
[ComponentA] --calls--> [ComponentB]
[ComponentB] --returns--> [ComponentA]
```

### Step 4: Save artifact

Create `devflow-docs/inception/application-design.md`.

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP. Do NOT present an approval gate.

```
[application-design 결과]
- 설계된 컴포넌트: [count]개
- 산출물: devflow-docs/inception/application-design.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
