---
name: aidlc-requirements-analysis
description: aidlc 플러그인(B안) 전용 스킬. Analyzes user requirements using adaptive depth (Minimal/Standard/Comprehensive) based on request complexity. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/requirements.md
---

# aidlc-requirements-analysis

<!-- 요구사항 분석: 적응형 깊이로 사용자 의도와 요구사항을 분석 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Analyze and document requirements at a depth appropriate to the request's complexity.

## Execution Modes

### Normal Mode (기본)
일반 호출. Step 1부터 순서대로 실행.

### QUESTIONS Mode
호출 텍스트에 `QUESTIONS` 키워드 포함 시 활성화:
`"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"`

QUESTIONS 모드에서는:
1. `devflow-docs/inception/requirements.md` 읽기
2. `## Open Questions` 섹션의 미해결 질문만 one-at-a-time으로 처리
3. 답변을 `## Assumptions` 또는 해당 요구사항 섹션에 반영
4. `requirements.md` 업데이트 후 STOP

Step 1, 2, 3, 4는 실행하지 않는다.

## Execute

### Step 1: Load complexity

**호출 텍스트에서 complexity 확인 (Primary)**:
호출 텍스트에 `Complexity: [level]` 패턴이 있으면 그 값을 사용:
- "aidlc-requirements-analysis 실행. Complexity: Standard" → Standard 사용
- "[Complexity: Standard] 오케스트레이터에서 확정된 복잡도로 분석합니다." 표시

**devflow-state에서 확인 (Fallback)**:
호출 텍스트에 complexity 정보가 없으면 `devflow-docs/devflow-state.md`의 `## Complexity` 필드를 읽는다.
해당 필드도 없으면 기존 기준으로 자체 판단:

**Choose Minimal if ALL of:**
- Single, clearly defined feature
- No ambiguity in requirements
- No cross-component dependencies
- Low risk (reversible, isolated)

**Choose Comprehensive if ANY of:**
- Multiple components or services affected
- High risk or irreversible changes
- Ambiguous requirements
- External integrations involved
- Performance or security critical

**Otherwise: Standard**

### Step 2: Interpretation check (Minimal 제외)

<!-- 해석 분기 확인: 동등하게 유효한 해석이 2가지 이상 존재하는지 판단 -->

Skip this step entirely if depth is **Minimal**.

For **Standard** and **Comprehensive**, ask: *"이 요청에 동등하게 유효한 해석이 2가지 이상 존재하는가?"*

**판단 기준 — 해석이 분기되는 신호:**
- 요청 키워드가 여러 구현 방식을 가리킴 (예: "검색", "알림", "인증")
- 기술 선택이 요구사항 자체를 바꿀 수 있음 (예: 실시간 vs 배치)
- 사용자가 최종 사용자 유형이나 사용 맥락을 명시하지 않음

**해석이 분기되지 않으면:** Step 3으로 바로 진행.

**해석이 분기되면:** 2-3가지 해석을 제시하고 사용자의 확인을 받은 후 Step 3으로 진행.

```
이 요청은 다음 중 어떤 방향인가요?

A) [해석 1] — [한 줄 설명]
B) [해석 2] — [한 줄 설명]
C) [해석 3] — [한 줄 설명, 있는 경우]

직접 설명하셔도 됩니다.
```

선택된 해석을 requirements.md의 `## User Intent`에 반영한다.

### Step 3: Execute at chosen depth

#### Minimal
1. Document user's intent in one paragraph
2. List 3-5 key acceptance criteria
3. Note any assumptions made

#### Standard
1. Analyze user intent (Step 2에서 확정된 해석 기반)
2. List functional requirements (what the system must do)
3. List non-functional requirements (performance, security, etc.)
4. Identify constraints and assumptions
5. Note open questions (if any)

#### Comprehensive
1. Full intent analysis (Step 2에서 확정된 해석 기반)
2. Detailed functional requirements with priority (Must/Should/Could)
3. Non-functional requirements with measurable criteria
4. Risk assessment (High/Medium/Low per requirement)
5. Dependencies and constraints
6. Open questions — ask user ONE at a time before proceeding

### Step 4: Ask clarifying questions (Comprehensive only)

<!-- Comprehensive 깊이에서 열린 질문이 있을 때만 -->

열린 질문이 있는 경우, 질문을 시작하기 전에 맥락을 먼저 선언한다:

```
요구사항을 확정하기 전에 몇 가지 질문을 드리겠습니다.
[질문 수]개의 열린 질문이 있습니다.
```

그 후 ONE question at a time. Wait for answer before asking next.

### Step 5: Save artifact

Create `devflow-docs/inception/requirements.md`:

```markdown
# Requirements Analysis

**Depth**: [Minimal | Standard | Comprehensive]
**Timestamp**: [ISO 8601]

## User Intent
[What the user wants to achieve — Step 2에서 확정된 해석 포함]

## Functional Requirements
[List of requirements]

## Non-Functional Requirements
[Performance, security, etc.]

## Assumptions
[List of assumptions made]

## Open Questions
[Any unresolved questions]
```

## Return to Orchestrator

STOP here. No approval gate — orchestrator handles it.

```
[requirements-analysis 결과]
- 분석 깊이: [Minimal | Standard | Comprehensive]
- 해석 확정: [확정된 해석 한 줄 요약, 또는 "단일 해석 — 확인 불필요"]
- 기능 요구사항: [count]개
- 열린 질문: [count]개
- 산출물: devflow-docs/inception/requirements.md
※ 누락된 요구사항이 있다면 오케스트레이터 게이트에서 A) 변경 요청을 선택해주세요.
```

## Common Issues

### User provides no requirements context
If the user's request is too vague to analyze:
- Default to Comprehensive depth
- Step 2에서 가능한 해석을 제시: "어떤 방향을 원하시나요?"

### workspace.md not found
If `devflow-docs/inception/workspace.md` does not exist:
- Proceed without it
- Note in requirements: "Workspace analysis not available"

### Step 2에서 해석이 3가지 이상으로 늘어날 때
해석이 너무 많으면 사용자가 선택하기 어렵다.
- 가장 가능성 높은 2-3가지로 압축
- 나머지는 "기타: 다른 방향이라면 직접 설명해주세요"로 열어두기
