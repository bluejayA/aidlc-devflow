---
type: pattern
applies_to: [aidlc-receiving-code-review]
status: active
source: manual
last_validated: 2026-04-13
---

# Review Feedback Schema

<!-- Single Source of Truth for reviewer output format. All 4 code reviewers reference this file. -->

## Purpose

Define the standardized output format, verdict criteria, and scoring rubric for all code reviewers. Each reviewer reads this file and follows the format exactly.

## Output Template

```markdown
## Review Result

**Verdict**: PASS | CONDITIONAL | FAIL

### Score

| Item | Rating | Notes |
|------|--------|-------|
| [rubric item] | 🟢 Good / 🟡 Acceptable / 🔴 Needs Work | [brief justification] |

### Context
[Optional — domain-specific summary. Security: Threat Surface. Maintainability: Change Impact Summary. 2-3 sentences max.]

### Issues

| # | Severity | File:Line | Issue | Fix |
|---|----------|-----------|-------|-----|
| 1 | Critical | path:42 | description | recommended fix |

### Pass Criteria
- [x] [met criterion]
- [ ] [unmet criterion]
```

## Verdict Criteria

| Verdict | Condition |
|---------|-----------|
| **PASS** | 0 Critical issues AND 0 🔴 rubric items |
| **CONDITIONAL** | 0 Critical issues AND 1+ 🔴 rubric items |
| **FAIL** | 1+ Critical issues |

When aggregating across multiple reviewers (synthesis), use **worst-of** logic: if any reviewer returns FAIL, the aggregate is FAIL.

## Issue Severity

| Level | Definition | Action |
|-------|-----------|--------|
| **Critical** | Bugs, security vulnerabilities, data loss risk | Must fix before merge |
| **Important** | Architecture, test gaps, error handling | Should fix |
| **Minor** | Style, naming, optimization | Optional |

## Score Levels

| Level | Symbol | Meaning |
|-------|--------|---------|
| Good | 🟢 | Meets or exceeds expectations |
| Acceptable | 🟡 | Adequate but could improve |
| Needs Work | 🔴 | Below threshold, contributes to CONDITIONAL verdict |

---

## Reviewer-Specific Rubrics

### Spec Compliance Reviewer

| Rubric Item | 🟢 Good | 🟡 Acceptable | 🔴 Needs Work |
|-------------|---------|---------------|---------------|
| Requirements Coverage | 100% FR/NFR covered | 90%+ covered, gaps are minor | <90% covered or critical gap |
| Missing Requirements | 0 missing | 0 missing but assumptions made | 1+ FR/NFR missing |
| Over-Implementation | 0 extra features | Minor convenience additions | Significant scope creep |

### Code Quality Reviewer

| Rubric Item | 🟢 Good | 🟡 Acceptable | 🔴 Needs Work |
|-------------|---------|---------------|---------------|
| Complexity | No high-complexity functions | 1-2 complex functions with justification | 3+ high-complexity functions |
| Test Coverage | All behaviors tested, edge cases included | Core paths tested, some edges missing | Critical paths untested |
| Error Handling | All error paths handled consistently | Most errors handled, some gaps | Missing error handling on critical paths |

### Security Reviewer

| Rubric Item | 🟢 Good | 🟡 Acceptable | 🔴 Needs Work |
|-------------|---------|---------------|---------------|
| OWASP Compliance | All applicable OWASP items pass | Minor items pending, no exploitable paths | Exploitable vulnerability found |
| Auth/Authz Validation | All auth checks present and correct | Auth present but edge cases uncovered | Missing or bypassable auth check |
| Input Validation Coverage | All external inputs validated | Most inputs validated, low-risk gaps | Unvalidated input on trust boundary |

### Maintainability Reviewer

| Rubric Item | 🟢 Good | 🟡 Acceptable | 🔴 Needs Work |
|-------------|---------|---------------|---------------|
| Coupling Assessment | Low coupling, clear interfaces | Moderate coupling with justification | High coupling, changes propagate widely |
| Change Impact Scope | Changes are localized | 2-3 files affected by future changes | 4+ files affected, ripple risk |
| Tech Debt Indicators | 0 new debt indicators | 1-2 minor indicators (TODO with ticket) | 3+ indicators or deprecated API usage |
