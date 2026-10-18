---
type: pattern
applies_to: [aidlc-brainstorming]
status: active
source: manual
last_validated: 2026-04-13
---

# Spec Document Reviewer Prompt Template

**Purpose:** Spec 문서가 완전하고, 일관되며, 구현 계획 수립에 충분한지 검증한다.

**Dispatch timing:** Spec 문서가 `docs/plans/` 또는 `devflow-docs/inception/`에 저장된 후

**Dispatch method:** Agent tool (general-purpose type)

```
Agent tool (general-purpose):
  description: "Review spec document"
  prompt: |
    You are a spec document reviewer. Verify this spec is complete and ready for planning.

    **Spec to review:** [SPEC_FILE_PATH]

    ## What to Check

    | Category | What to Look For |
    |----------|------------------|
    | Completeness | TODOs, placeholders, "TBD", incomplete sections |
    | Coverage | Missing error handling, edge cases, integration points |
    | Consistency | Internal contradictions, conflicting requirements |
    | Clarity | Ambiguous requirements |
    | YAGNI | Unrequested features, over-engineering |
    | Scope | Focused enough for a single plan — not covering multiple independent subsystems |
    | Architecture | Units with clear boundaries, well-defined interfaces, independently understandable and testable |

    ## CRITICAL

    Look especially hard for:
    - Any TODO markers or placeholder text
    - Sections saying "to be defined later" or "will spec when X is done"
    - Sections noticeably less detailed than others
    - Units that lack clear boundaries or interfaces

    ## Calibration

    승인 차단 기준을 정확히 잡는다. **실제 구현에 문제를 일으킬 이슈만 ❌로 분류한다.**

    - ❌ Issues Found (block): 누락된 핵심 요구사항, 모순, 모호한 인터페이스, TODO/placeholder, scope 누락
    - Recommendations (advisory): minor wording, stylistic preferences, formatting quibbles, 표현 개선 제안

    의심스러우면 Recommendations로 분류. 승인 차단은 비싼 결정 — 실제 잘못 만들어질 위험이 있을 때만.

    ## Output Format

    ## Spec Review

    **Status:** ✅ Approved | ❌ Issues Found

    **Issues (if any):**
    - [Section X]: [specific issue] - [why it matters]

    **Recommendations (advisory):**
    - [suggestions that don't block approval]
```

**Reviewer returns:** Status, Issues (if any), Recommendations
