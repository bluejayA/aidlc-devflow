---
name: units-generation
description: Decomposes the system into independently developable units for parallel
  implementation. Conditionally called by using-devflow orchestrator when the system
  needs decomposition during AI-DLC Construction phase. Do NOT invoke directly.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
---

# units-generation

<!-- 작업 단위 분해: 복잡한 시스템을 병렬 개발 가능한 단위로 분해 -->
<!-- B안: 실행 전용, 조건부 — 오케스트레이터가 workflow-plan 기반으로 호출 여부 결정 -->

## Purpose

Decompose the system into independently developable units.

## Execute

### Step 1: Load context

Read application design and requirements documents.

### Step 2: Identify units

Each unit must be:
- Independently implementable
- Completable in a single focused session
- Testable in isolation

### Step 3: Define each unit

```markdown
### Unit: [unit-name]
**Responsibility**: [single sentence]
**Dependencies**: [other units, or "none"]
**Interfaces**: [what it exposes]
**Implementation order**: [number]
```

### Step 4: Save artifact

Create `devflow-docs/inception/units.md`.

## Return to Orchestrator

After saving the artifact, display results in this format — then STOP. Do NOT present an approval gate.

```
[units-generation 결과]
- 생성된 단위: [count]개
- 구현 순서: [unit1] → [unit2] → ...
- 산출물: devflow-docs/inception/units.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
