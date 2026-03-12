---
name: aidlc-code-generation
description: aidlc 플러그인(B안) 전용 스킬. Two-stage process — generates a code plan first, then implements after orchestrator approval. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/[unit-name]/code-plan.md
---

# aidlc-code-generation

<!-- 코드 생성: Plan 작성 후 오케스트레이터 승인을 받아 코드 생성 -->
<!-- B안: Plan 제시까지만 담당 — 승인 게이팅은 오케스트레이터 소유 -->

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
- [ ] Step 1: [specific action]
- [ ] Step 2: [specific action]

## Test Strategy
- [ ] [test name]: [what it verifies]
```

After writing the plan, display it and STOP:

```
[code-generation Plan 준비]
- 생성할 파일: [count]개
- 수정할 파일: [count]개
- 구현 단계: [count]개
```

The orchestrator will present the approval gate. Do NOT write any code yet.

### PART 2 — Generation (오케스트레이터 승인 후)

When invoked with explicit generation instruction such as:
`"code-generation: GENERATE — proceed with the approved plan for [unit-name]"`

Or when the conversation context clearly contains an approved plan and the
orchestrator has signaled to proceed with generation.
1. Execute each step in the plan
2. Mark each checkbox `[x]` immediately after completing that step
3. Follow TDD: write tests first, then implementation
4. Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`

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

Actions:
1. Step 1 실행: 스켈레톤 작성 → `[x]` 표시
2. Step 2 실행: 테스트 작성 → `[x]` 표시
3. Step 3 실행: 구현 → `[x]` 표시
4. ... (각 체크박스 즉시 업데이트)

---

## Review (Standard 이상)

### PART 1 (Plan) 완료 시
depth가 Standard 이상이면:
1. `_shared/reviewers/code-plan-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/construction/[unit-name]/code-plan.md`
   - 설계 산출물: `devflow-docs/inception/requirements.md`, `devflow-docs/inception/application-design.md` (있으면)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

### PART 2 (Generate) 완료 시
depth가 Standard 이상이면:
1. `_shared/reviewers/code-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 변경 파일 목록: 구현된 소스 파일
   - code-plan 경로: `devflow-docs/construction/[unit-name]/code-plan.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵

## Return to Orchestrator

STOP.

PART 1 완료 시:
```
[code-generation Plan 준비]
- 생성할 파일: [count]개 / 수정할 파일: [count]개 / 구현 단계: [count]개
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

PART 2 완료 시:
```
[code-generation 완료: unit-name]
- 생성된 파일: [count]개
- 모든 체크박스 완료
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```
