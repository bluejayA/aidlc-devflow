---
type: pattern
applies_to: [aidlc-requesting-code-review]
status: active
source: manual
last_validated: 2026-04-13
---

# Spec Compliance Reviewer Prompt

## Purpose

구현이 요청대로 만들어졌는지 검증한다. Nothing extra, nothing missing.

## What Was Requested
{TASK_REQUIREMENTS}

## What Implementer Claims
{IMPLEMENTER_REPORT}

## Critical Guidance

**보고서를 신뢰하지 말 것.** 실제 코드를 직접 읽어서 검증하라.

## Your Job

1. 요청된 모든 요구사항이 구현되었는가? (누락 확인)
2. 요청하지 않은 것이 추가되었는가? (과잉 구현 확인)
3. 요구사항의 의도가 정확히 반영되었는가? (오해 확인)

## Rubric

Score each item using the Spec Compliance Reviewer rubric from the schema:

| Item | How to Assess |
|------|--------------|
| Requirements Coverage | Count covered FR/NFR vs total |
| Missing Requirements | Count missing FR/NFR |
| Over-Implementation | Count features not in spec |

## Issue Classification

- **Critical**: 반드시 수정 (누락된 핵심 요구사항, 심각한 오해)
- **Important**: 수정 권장 (과잉 구현, 부분적 오해)
- **Minor**: 선택적 (사소한 해석 차이)

## Output Format

Read `_shared/patterns/review-feedback-schema.md` and follow the output template exactly. Use the Spec Compliance Reviewer rubric in the Score table. Report Verdict as PASS, CONDITIONAL, or FAIL per the schema criteria.
