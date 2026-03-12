---
name: aidlc-workflow-planning
description: aidlc 플러그인(B안) 전용 스킬. Determines which Construction stages to run and at what depth. Saves workflow plan. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/workflow-plan.md
---

# aidlc-workflow-planning

<!-- 워크플로우 계획: 어떤 스테이지를 실행할지 결정 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->
<!-- 중요: 이 skill의 산출물을 오케스트레이터가 읽어 조건부 스테이지를 결정 -->

## Purpose

Determine which stages to execute and at what depth.

## Execute

### Step 1: Load prior context

Read (if they exist):
- `devflow-docs/inception/workspace.md`
- `devflow-docs/inception/requirements.md`

### Step 2: Generate approaches (2-3개)

요구사항과 workspace를 기반으로 접근법을 생성한다.

**접근법 개수 기준 (complexity 연동)**:
- Comprehensive complexity → 3개
- Minimal / Standard complexity → 2개

complexity는 호출 텍스트 또는 `devflow-docs/devflow-state.md`의 `## Complexity` 필드에서 확인.

**항상 포함해야 하는 접근법**:
- "빠른/간결" 접근법: application-design 스킵, Minimal depth 위주
- "안전한/완전" 접근법: application-design 포함, Standard+ depth 위주
- (3개인 경우) 중간 접근법: 상황에 맞게 구성

**접근법 간 실질적 차이 필수**: 스테이지 포함 여부 또는 depth가 달라야 함.

각 접근법 형식:
```
### [A안 | B안 | C안] [접근법명] [(권장)]
- 포함 스테이지: [list]
- 깊이: [Minimal | Standard | Comprehensive]
- 적합: [한 줄]
- 주의: [한 줄]
```

### Step 3: Generate workflow visualization

Create a text-based workflow diagram:

```
INCEPTION
  ✅ workspace-detection (완료)
  ✅ requirements-analysis (완료)
  ⏭ workflow-planning (현재)

CONSTRUCTION
  ➡ application-design [Standard] (?)
  ➡ units-generation [Minimal] (?)
  ➡ code-generation [Standard]
  ➡ build-and-test [Standard]
```

**주의**: Visualization은 A안(권장) 기준으로 생성한다.
선택된 접근법이 다를 경우 오케스트레이터가 재요청할 수 있다.
스킵된 스테이지는 `⏭ [stage] — 스킵 (A안 기준)` 형식으로 표시한다.

### Step 4: Save artifact (Approaches 섹션 포함)

Create `devflow-docs/inception/workflow-plan.md`:

```markdown
# Workflow Plan

**Timestamp**: [ISO 8601]
**Selected Approach**: TBD (오케스트레이터 gate에서 사용자 선택 후 업데이트)

## Approaches Considered
- A안) [접근법명] — [한 줄 요약]
- B안) [접근법명] — [한 줄 요약]
- (C안) [접근법명] — [한 줄 요약]

## Approved Stages
### CONSTRUCTION
- application-design: [included | skipped] — [reason]
- units-generation: [included | skipped] — [reason]
- code-generation: included — always
- build-and-test: included — always

## Stage Depths
- application-design: [Minimal | Standard | Comprehensive]
- units-generation: [Minimal | Standard | Comprehensive]
- code-generation: [Minimal | Standard | Comprehensive]
- build-and-test: [Minimal | Standard | Comprehensive]
```

**중요**: `## Approved Stages`는 선택된 접근법 기준으로 작성한다.
초기 저장 시에는 권장 접근법(A안) 기준으로 작성한다.
오케스트레이터가 선택을 받은 후 `**Selected Approach**` 필드를 업데이트한다.
오케스트레이터 Routing Table은 `## Approved Stages` 이하만 파싱한다.

## Return to Orchestrator

STOP here. No approval gate — orchestrator handles approach selection, state update, and routing.

```
[workflow-planning 결과]
- 생성된 접근법: [A안명] / [B안명] / ([C안명])
- 권장 접근법: [A안 | B안 | C안]
- 접근법 상세: (위 Step 2의 접근법 목록 참조)
- 산출물: devflow-docs/inception/workflow-plan.md (Selected Approach 확정 후 오케스트레이터가 업데이트)
```

## Common Issues

### requirements.md or workspace.md not found
If prior artifacts are missing:
- Proceed with available information
- Note missing context in the workflow plan
- Default to including all optional stages (conservative assumption)

### No clear indication of new components needed
When it's ambiguous whether application-design is needed:
- Default to including it
- Note the ambiguity in the workflow plan
