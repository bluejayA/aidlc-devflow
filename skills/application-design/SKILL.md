---
name: application-design
description: Designs component and service structure before implementation begins.
  Conditionally called by using-devflow orchestrator when new components are needed
  during AI-DLC Construction phase. Do NOT invoke directly — use using-devflow instead.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
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

## Common Issues

### requirements.md not found
If `devflow-docs/inception/requirements.md` does not exist:
- Display: "⚠️ requirements.md를 찾을 수 없습니다. 사용자 요청 컨텍스트만으로 설계를 진행합니다."
- Proceed based on available conversation context

### No clear component boundaries
If the system is too simple to decompose:
- Design as a single component
- Note: "Single-component system — no decomposition needed"
