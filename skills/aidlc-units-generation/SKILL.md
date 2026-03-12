---
name: aidlc-units-generation
description: aidlc 플러그인(B안) 전용 스킬. Decomposes the system into independently developable units for parallel implementation. Conditional Construction stage. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/units.md
---

# aidlc-units-generation

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

## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/units.md`
   - 상위 산출물: `devflow-docs/inception/application-design.md` (있으면), `devflow-docs/inception/requirements.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

## Return to Orchestrator

STOP.

```
[units-generation 결과]
- 생성된 단위: [count]개
- 구현 순서: [unit1] → [unit2] → ...
- 산출물: devflow-docs/inception/units.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

## Common Issues

### Only one logical unit identified
분해 결과 단일 unit이면:
- units.md에 1개 unit으로 작성
- 오케스트레이터가 single-unit code-generation으로 처리
