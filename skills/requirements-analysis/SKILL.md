---
name: requirements-analysis
description: Analyzes user requirements using adaptive depth (Minimal, Standard, or
  Comprehensive) based on request complexity. Called by using-devflow orchestrator
  during AI-DLC Inception phase. Do NOT invoke directly — use using-devflow instead.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
---

# requirements-analysis

<!-- 요구사항 분석: 적응형 깊이로 사용자 의도와 요구사항을 분석 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Analyze and document requirements at a depth appropriate to the request's complexity.

## Execute

### Step 1: Assess complexity

Evaluate the user's request against these criteria:

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

### Step 2: Execute at chosen depth

#### Minimal
1. Document user's intent in one paragraph
2. List 3-5 key acceptance criteria
3. Note any assumptions made

#### Standard
1. Analyze user intent
2. List functional requirements (what the system must do)
3. List non-functional requirements (performance, security, etc.)
4. Identify constraints and assumptions
5. Note open questions (if any)

#### Comprehensive
1. Full intent analysis
2. Detailed functional requirements with priority (Must/Should/Could)
3. Non-functional requirements with measurable criteria
4. Risk assessment (High/Medium/Low per requirement)
5. Dependencies and constraints
6. Open questions — ask user ONE at a time before proceeding

### Step 3: Ask clarifying questions (Comprehensive only)

<!-- Comprehensive 깊이에서 열린 질문이 있을 때만 -->
Ask ONE question at a time. Wait for answer before asking next.

### Step 4: Save artifact

Create `devflow-docs/inception/requirements.md`:

```markdown
# Requirements Analysis

**Depth**: [Minimal | Standard | Comprehensive]
**Timestamp**: [ISO 8601]

## User Intent
[What the user wants to achieve]

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

After saving the artifact, display results in this format — then STOP. Do NOT present an approval gate.

```
[requirements-analysis 결과]
- 분석 깊이: [Minimal | Standard | Comprehensive]
- 기능 요구사항: [count]개
- 열린 질문: [count]개
- 산출물: devflow-docs/inception/requirements.md
```

The orchestrator (using-devflow) will handle the approval gate and state update.
