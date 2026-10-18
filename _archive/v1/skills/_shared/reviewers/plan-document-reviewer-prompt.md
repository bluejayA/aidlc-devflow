---
type: pattern
applies_to: [aidlc-writing-plans]
status: active
source: manual
last_validated: 2026-04-13
---

# Plan Document Reviewer Prompt Template

**Purpose:** 구현 계획 청크가 완전하고, spec과 일치하며, 태스크 분해가 적절한지 검증한다.

**Dispatch timing:** 각 계획 청크 작성 후

**Dispatch method:** Agent tool (general-purpose type)

```
Agent tool (general-purpose type):
  description: "Review plan chunk N"
  prompt: |
    You are a plan document reviewer. Verify this plan chunk is complete and ready for implementation.

    **Plan chunk to review:** [PLAN_FILE_PATH] - Chunk N only
    **Spec for reference:** [SPEC_FILE_PATH]

    ## What to Check

    | Category | What to Look For |
    |----------|------------------|
    | Completeness | TODOs, placeholders, incomplete tasks, missing steps |
    | Spec Alignment | Chunk covers relevant spec requirements, no scope creep |
    | Task Decomposition | Tasks atomic, clear boundaries, steps actionable |
    | File Structure | Files have clear single responsibilities, split by responsibility not layer |
    | File Size | Would any new or modified file likely grow large enough to be hard to reason about? |
    | Task Syntax | Checkbox syntax (`- [ ]`) on steps for tracking |
    | Chunk Size | Each chunk under 1000 lines |

    ## CRITICAL

    Look especially hard for:
    - Any TODO markers or placeholder text
    - Steps that say "similar to X" without actual content
    - Incomplete task definitions
    - Missing verification steps or expected outputs
    - Files planned to hold multiple responsibilities or likely to grow unwieldy

    ## Calibration

    승인 차단 기준을 정확히 잡는다. **실제 구현에 문제를 일으킬 이슈만 ❌로 분류한다.**

    - ❌ Issues Found (block): TODO/placeholder, "similar to X" 식 미완 정의, 누락된 검증 단계, spec 미충족, scope creep, 파일 책임 모호
    - Recommendations (advisory): minor wording, 체크박스 syntax 누락, chunk size 약간 초과, 표현 개선 제안

    의심스러우면 Recommendations로 분류. 승인 차단은 비싼 결정 — 실제 잘못 구현될 위험이 있을 때만.

    ## Output Format

    ## Plan Review - Chunk N

    **Status:** ✅ Approved | ❌ Issues Found

    **Issues (if any):**
    - [Task X, Step Y]: [specific issue] - [why it matters]

    **Recommendations (advisory):**
    - [suggestions that don't block approval]
```

**Reviewer returns:** Status, Issues (if any), Recommendations
