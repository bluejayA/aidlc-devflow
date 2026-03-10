---
name: units-generation
description: Decomposes the system into independently developable units for parallel implementation. Conditional Construction stage.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/units.md
---

# units-generation

<!-- 작업 단위 분해: 복잡한 시스템을 병렬 개발 가능한 단위로 분해 -->
<!-- B안: 실행 전용, 조건부 — 오케스트레이터가 workflow-plan 기반으로 호출 여부 결정 -->

## Purpose

Decompose the system into independently developable units.

## Execute

### Step 1: Load context

Read the following files (if they exist):
- `devflow-docs/inception/application-design.md` — component structure
- `devflow-docs/inception/requirements.md` — functional requirements

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

STOP here. No approval gate — orchestrator handles it.

```
[units-generation 결과]
- 생성된 단위: [count]개
- 구현 순서: [unit1] → [unit2] → ...
- 산출물: devflow-docs/inception/units.md
```

## Common Issues

### application-design.md not found
If `devflow-docs/inception/application-design.md` does not exist:
- Display: "⚠️ application-design.md를 찾을 수 없습니다. requirements.md 기반으로 단위를 분해합니다."
- Proceed using requirements.md only

### Only one logical unit identified
If decomposition results in a single unit:
- Create units.md with one unit
- Orchestrator will treat this as single-unit code-generation
