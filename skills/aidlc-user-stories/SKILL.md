---
name: aidlc-user-stories
description: 요구사항을 INVEST 기준 사용자 스토리로 변환. Pre-Planning 스테이지. Called by aidlc-inception-orchestrator.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/user-stories.md
---

# aidlc-user-stories

<!-- 사용자 스토리 생성: 요구사항을 INVEST 기준 스토리로 변환 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->
<!-- Hold/Skip: _shared/import-review-protocol.md 참조 -->

## Purpose

요구사항을 INVEST 기준 사용자 스토리로 변환한다.
비대화형 생성 — requirements.md를 기반으로 일괄 변환하고, 변경 요청은 오케스트레이터 게이트에서 처리.

## Execute

### Step 1: Load context

Read (if they exist):
- `devflow-docs/inception/requirements.md` — 기능/비기능 요구사항
- `devflow-docs/inception/workspace.md` — 그린필드/브라운필드 컨텍스트

### Step 2: Identify actors

요구사항에서 사용자 유형을 추출한다:
- 직접 언급된 사용자 (예: "관리자", "일반 사용자")
- 암묵적 사용자 (예: 인증 요구사항 → 인증된 사용자)
- 외부 시스템 (예: API 연동 → 외부 API)

### Step 3: Generate user stories

각 액터별로:
1. Given-When-Then 형식 Acceptance Criteria 작성
2. INVEST 기준 검증:
   - **I**ndependent: 다른 스토리와 독립적
   - **N**egotiable: 구현 방식 협상 가능
   - **V**aluable: 사용자에게 가치 제공
   - **E**stimable: 구현 범위 추정 가능
   - **S**mall: 한 스프린트 내 완료 가능
   - **T**estable: 검증 기준 명확
3. 우선순위 부여: Must / Should / Could

### Step 4: Save artifact

Create `devflow-docs/inception/user-stories.md`:

```markdown
# User Stories

**Timestamp**: [ISO 8601]
**Source**: devflow-docs/inception/requirements.md

## Actors
- [Actor1]: [역할 설명]
- [Actor2]: [역할 설명]

## Stories

### US-001: [스토리 제목]
**Actor**: [Actor명]
**Story**: As a [actor], I want [goal] so that [benefit]
**Acceptance Criteria**:
- Given [context], When [action], Then [result]
- Given [context], When [action], Then [result]
**Priority**: [Must | Should | Could]
```

## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/user-stories.md`
   - 상위 산출물: `devflow-docs/inception/requirements.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

**depth 확인**: `devflow-docs/devflow-state.md`의 `## Complexity` 필드를 읽는다.

## Return to Orchestrator

STOP.

```
[user-stories 결과]
- 액터: [count]명 ([액터명 나열])
- 사용자 스토리: [count]개 (Must: [N], Should: [N], Could: [N])
- 산출물: devflow-docs/inception/user-stories.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

## Common Issues

### requirements.md에 사용자 유형이 명시되지 않은 경우
- 기능 요구사항에서 암묵적 액터 추출
- "기본 사용자" 액터를 생성하여 매핑
- 산출물에 "⚠️ 명시적 액터 없음 — 요구사항에서 추론" 기록

### 요구사항이 기술 중심이고 사용자 스토리로 변환이 어려운 경우
- 기술 요구사항은 "시스템" 액터로 매핑 (예: As a system, I want...)
- 순수 인프라 요구사항은 스토리 변환 스킵하고 "기술 요구사항" 섹션에 별도 기록
