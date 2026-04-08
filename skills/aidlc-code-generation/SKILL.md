---
name: aidlc-code-generation
description: Use when a defined unit or feature needs code implementation with TDD, or when "코드 생성", "구현해줘", "code generation" is requested.
metadata:
  version: 0.5.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/{unit}/code-plan.md
---

# aidlc-code-generation

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 코드 생성: Plan 작성 후 오케스트레이터 승인을 받아 코드 생성 -->

## Purpose

Generate a code plan and, after orchestrator approval, execute the plan.

## Two-Stage Process

### PART 1 — Planning (항상 실행)

Create a code generation plan with checkboxes:

```markdown
# Code Generation Plan: [unit-name]

> **For agentic workers:** REQUIRED: Use `aidlc:aidlc-code-generation` with the
> "GENERATE" signal to execute this plan. Do NOT implement ad-hoc.
> `"code-generation: GENERATE — proceed with the approved plan for [unit-name]"`

## Files to Create
- [ ] `path/to/file.py` — [purpose]
- [ ] `tests/path/to/test_file.py` — [what it tests]

## Files to Modify
- [ ] `path/to/existing.py` — [what changes]

## Implementation Steps
- [ ] Step 1: [기능명]
  - [ ] RED: [테스트명] 작성
  - [ ] Verify RED: 실패 확인
  - [ ] GREEN: [구현 내용]
  - [ ] Verify GREEN: 통과 확인 + 전체 회귀
  - [ ] REFACTOR: [정리 대상이 있으면 명시, 없으면 생략]
- [ ] Step 2: [기능명]
  - [ ] RED: [테스트명] 작성
  ...

## Test Strategy
- [ ] [test name]: [what it verifies]

> 각 테스트는 Implementation Steps의 RED 단계에서 작성된다. 별도 테스트 단계가 아님.

## Verification Contract

### 완료 조건
- [ ] [구체적 기능 요건 1]
- [ ] [구체적 기능 요건 2]

### 검증 명령
- `[test command]` — [what it verifies]
- `[lint command]` — [what it checks]

### 리스크 태그
- [ ] auth/security — [해당 시 표시]
- [ ] DB schema change — [해당 시 표시]
```

After writing the plan, display it and STOP:

```
[code-generation Plan 준비]
- 생성할 파일: [count]개
- 수정할 파일: [count]개
- 구현 단계: [count]개
```

The orchestrator will present the approval gate. Do NOT write any code yet.

**session-summary 중간 기록**: Plan 작성 완료 후 session-summary.md의 `## Completed Work`에 `[~] code-generation — Plan 작성 완료, 승인 대기` 업데이트.

### PART 2 — Generation (오케스트레이터 승인 후)

When invoked with explicit generation instruction such as:
`"code-generation: GENERATE — proceed with the approved plan for [unit-name]"`

Or when invoked with auto-fix error context:
`"code-generation: GENERATE — auto-fix for [unit-name]: [failed test], [error summary]"`

When error context is present, fix only the failing part instead of re-executing the full plan. Use the error message and failed test name to identify the affected Implementation Step.

Or when the conversation context clearly contains an approved plan and the
orchestrator has signaled to proceed with generation.
1. `_shared/tdd-protocol.md` 읽기
2. 각 Implementation Step에 대해 TDD 사이클 실행:
   a. RED: 실패 테스트 작성 → 실행 → 실패 확인
   b. GREEN: 최소 구현 → 실행 → 해당 테스트 + 전체 테스트 통과 확인
   c. REFACTOR: 정리 → 전체 테스트 재실행
   d. 체크박스 [x] 표시 (하위 RED/Verify RED/GREEN/Verify GREEN/REFACTOR 포함)
   e. **session-summary 중간 기록**: Step 완료마다 `[~] code-generation — Step [N]/[M] 완료` 업데이트
3. Iron Law 위반 시: 해당 코드 삭제 후 RED부터 재시작
4. 모든 Step 완료 후 Self-Review 체크리스트 수행 (`_shared/tdd-protocol.md` 참조)
5. 자가 수정 후 Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`

## Examples

### Example 1: PART 1 — 계획 수립
Orchestrator calls: "code-generation — plan for unit: notification-service"

Output:
```markdown
# Code Generation Plan: notification-service

## Files to Create
- [ ] `notifications/service.py` — 알림 생성/조회/삭제 비즈니스 로직
- [ ] `tests/test_notification_service.py` — 서비스 단위 테스트

## Implementation Steps
- [ ] Step 1: NotificationService 클래스 스켈레톤 작성
- [ ] Step 2: create_notification() 테스트 작성 (RED)
- [ ] Step 3: create_notification() 구현 (GREEN)
- [ ] Step 4: list_notifications() 테스트 및 구현
- [ ] Step 5: delete_notification() 테스트 및 구현

## Test Strategy
- [ ] test_create_notification_success: 정상 생성 확인
- [ ] test_create_notification_invalid_user: 잘못된 사용자 처리
- [ ] test_list_notifications_empty: 빈 목록 반환
```

### Example 2: PART 2 — 코드 생성
Orchestrator calls: "code-generation: GENERATE — proceed with the approved plan for notification-service"

Actions: `_shared/tdd-protocol.md` 읽기 → 각 Step에 대해 RED→GREEN→REFACTOR 사이클 → Self-Review → code-plan.md 저장

## Review

conventions Review Workflow 적용.

### PART 1 (Plan)
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md
- 리뷰어: code-plan-reviewer-prompt.md
- **Depth 정책**: Minimal/Standard/Comprehensive → code-plan-reviewer dispatch (R1)

### PART 2 (Generate)
- 산출물: 구현된 소스 파일
- 리뷰어: code-reviewer-prompt.md
- **Depth 정책**: conventions 리뷰 규약 참조

## Return to Orchestrator

conventions 표준 형식. 반환 필드:

**PART 1:** 생성할 파일 [count]개 / 수정할 파일 [count]개 / 구현 단계 [count]개 / 리뷰

**PART 2:** 생성된 파일 [count]개 / 테스트 [count]개 통과 / TDD 사이클 [count]회 / Self-Review / 산출물 / 리뷰
