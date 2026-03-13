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

## Report Format

**✅ Spec Compliant** — 요구사항 전부 충족, 과잉 구현 없음

또는

**❌ Issues Found**
- Missing: [누락된 요구사항] — [파일:라인]
- Extra: [추가된 불필요 기능] — [파일:라인]
- Misunderstood: [오해된 요구사항] — [상세 설명]
