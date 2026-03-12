---
name: aidlc-workflow-planning
description: Determines which Construction stages to run and at what depth. Saves workflow plan. Called by inception-orchestrator.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/workflow-plan.md
---

# aidlc-workflow-planning

<!-- 워크플로우 계획: 어떤 스테이지를 실행할지 결정 -->
<!-- 중요: 이 skill의 산출물을 오케스트레이터가 읽어 조건부 스테이지를 결정 -->

## Purpose

Determine which stages to execute and at what depth.

## Execute

### Step 1: Load prior context

Read (if they exist):
- `devflow-docs/inception/workspace.md`
- `devflow-docs/inception/requirements.md`
- `devflow-docs/inception/user-stories.md` — 사용자 스토리 (있으면)
- `devflow-docs/inception/nfr-requirements.md` — NFR 요구사항 (있으면)

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

**NFR 컨텍스트 반영:**
`devflow-docs/inception/nfr-requirements.md`가 존재하면:
- "안전한/완전" 접근법에 `application-design: Comprehensive` 포함 (NFR Design 활성화)
- "빠른/간결" 접근법에서도 NFR 존재 사실 명시
- 접근법 형식에 NFR 관련 고려사항 추가

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
### PRE-PLANNING
- user-stories: [included | skipped | held] — [reason]
- nfr-requirements: [included | skipped | held] — [reason]

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

**참고**: `### PRE-PLANNING` 섹션은 오케스트레이터가 파싱하지 않는다.
Pre-Planning 스테이지는 오케스트레이터가 직접 게이트로 관리하며, 이 섹션은 기록용.
기존 `### CONSTRUCTION` 파싱 로직은 변경 없음.

## Review

conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/workflow-plan.md
- 리뷰어: artifact-reviewer-prompt.md

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 생성된 접근법: [A안명] / [B안명] / ([C안명])
- 권장 접근법: [A안 | B안 | C안]
- 접근법 상세: (Step 2의 접근법 목록 참조)
- 산출물: devflow-docs/inception/workflow-plan.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

## Common Issues

### No clear indication of new components needed
application-design 포함 여부가 모호하면:
- 기본적으로 포함
- workflow plan에 모호성 기록
