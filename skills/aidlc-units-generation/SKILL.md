---
name: aidlc-units-generation
description: Use when the system needs to be decomposed into independently developable and testable units with dependency ordering.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/units.md
---

# aidlc-units-generation

<!-- 작업 단위 분해: 복잡한 시스템을 병렬 개발 가능한 단위로 분해 -->

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

## Review

conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/units.md
- 리뷰어: artifact-reviewer-prompt.md

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 생성된 단위: [count]개
- 구현 순서: [unit1] → [unit2] → ...
- 산출물: devflow-docs/inception/units.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

## Common Issues

### Only one logical unit identified
분해 결과 단일 unit이면:
- units.md에 1개 unit으로 작성
- 오케스트레이터가 single-unit code-generation으로 처리
