---
name: requirements-analysis
description: Use when analyzing user requirements at adaptive depth (Minimal/Standard/Comprehensive) based on request complexity, before workflow planning
---

# requirements-analysis

<!-- 요구사항 분석: 적응형 깊이로 사용자 의도와 요구사항을 분석 -->
<!-- ALWAYS 실행 — 깊이(depth)만 조절됨 -->

## Purpose

Analyze and document requirements at a depth appropriate to the request's complexity.

## Always Execute

This stage always runs. Only the depth varies.

## Step 1: Assess complexity

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

## Step 2: Execute at chosen depth

### Minimal
1. Document user's intent in one paragraph
2. List 3-5 key acceptance criteria
3. Note any assumptions made

### Standard
1. Analyze user intent
2. List functional requirements (what the system must do)
3. List non-functional requirements (performance, security, etc.)
4. Identify constraints and assumptions
5. Note open questions (if any)

### Comprehensive
1. Full intent analysis
2. Detailed functional requirements with priority (Must/Should/Could)
3. Non-functional requirements with measurable criteria
4. Risk assessment (High/Medium/Low per requirement)
5. Dependencies and constraints
6. Open questions — ask user one at a time before proceeding

## Step 3: Ask clarifying questions (if needed)

<!-- Comprehensive 깊이에서 열린 질문이 있을 때만 -->
Ask ONE question at a time. Wait for answer before asking next.
Prefer multiple-choice over open-ended.

## Step 4: Save requirements document

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

## Step 5: Update state and audit log

Use devflow-state to update current stage to `workflow-planning`.
Use devflow-audit to log this stage completion.

## Step 6: Completion gate

Display:
```
## Requirements Analysis 완료 ([Minimal | Standard | Comprehensive])

- 산출물: devflow-docs/inception/requirements.md

A) 변경 요청
B) workflow-planning 단계로 진행
```

Wait for explicit user approval before proceeding.
