# Decision Log Format

## 스테이지 결정 기록

```markdown
## [ISO-8601] [stage-name]
- decision: [결정 내용]
- reason: [판단 근거]
- alternatives_considered: [고려한 대안]
- assumptions: [가정 목록, 있으면]
```

## 리뷰 결과 기록

```markdown
## [ISO-8601] [phase]-review
- reviewers: [목록]
- results: [리뷰어별 verdict + issues]
- auto-fix-attempt: [N/3]
- fix-detail: [수정 내용]
- final: [ALL PASS | ESCALATE]
```

## 기술 스택 선택 기록

```markdown
## [ISO-8601] tech-stack
- selections:
  | 계층 | 선택 | 근거 |
  |------|------|------|
  | Frontend | Next.js + Tailwind + shadcn | CLAUDE.md 명시 |
  | Backend | FastAPI | 카탈로그 권장 + AI/ML 요구사항 |
- source_priority: CLAUDE.md → 카탈로그 권장 → 업계 기본값
```
