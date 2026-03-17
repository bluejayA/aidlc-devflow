# Document Review Loop 설계

**이슈**: #7 ([2/13] Document Review Loop)
**날짜**: 2026-03-17
**상태**: 설계 승인됨

## 배경

리뷰어 프롬프트(`spec-document-reviewer-prompt.md`, `plan-document-reviewer-prompt.md`)가 이미 존재하지만, brainstorming/writing-plans 스킬에서 호출하지 않는 상태.

## 설계 결정

- 심각도 체계(Critical/High/Medium/Low) 도입하지 않음 — 판단 기준이 모호하고 에이전트마다 다르게 분류
- 기존 리뷰어의 Issues vs Recommendations 이분법 활용
- 기존 리뷰어 프롬프트 수정 없음

## 루프 종료 조건

```
리뷰 결과:
- Issues 있음 → 수정 후 재리뷰 (최대 5회)
- Recommendations만 있음 → 루프 종료
- 5회 초과 → 사용자 escalate
```

## 수정 파일

### Task 1: `devflow-conventions.md`
기존 "리뷰 루프" 섹션에 종료 조건 명확화 (Issues vs Recommendations 기준). 2-3줄 추가.

### Task 2: `aidlc-brainstorming/SKILL.md`
설계 문서 작성 완료 후 spec-document-reviewer 자동 dispatch 단계 추가.
- Standard/Comprehensive: 자동 실행
- Minimal: 스킵
- 리뷰어: `_shared/reviewers/spec-document-reviewer-prompt.md` (기존, 변경 없음)

### Task 3: `aidlc-writing-plans/SKILL.md`
계획 문서 작성 완료 후 plan-document-reviewer 자동 dispatch 단계 추가.
- Standard/Comprehensive: 자동 실행
- Minimal: 스킵
- 리뷰어: `_shared/reviewers/plan-document-reviewer-prompt.md` (기존, 변경 없음)

## 신규 파일 없음

기존 인프라를 연결만 하는 작업.
