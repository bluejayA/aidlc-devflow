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

## audit emit 형식 (devflow-docs/audit.md)

decision-log는 판단 상세를 기록하고, audit.md는 이벤트 marker만 한 줄씩 append한다. plugin 공통 emit 표준 (BL-098, memory-sync 패턴) 준수:

```
[<ISO timestamp>] auto-mode-invoked | mode=<new|resume> | intent=<short>
[<ISO timestamp>] auto-mode-stage-completed | stage=<name> | complexity=<level> | auto-approved=true
[<ISO timestamp>] auto-mode-resume-drift-detected | gap=<short>
[<ISO timestamp>] auto-mode-escalated | phase=<INCEPTION|CONSTRUCTION> | reason=<short> | retries=<N>
```

상세 SKILL.md `## State Management` → `### audit emit 형식` 참조.
