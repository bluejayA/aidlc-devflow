---
name: aidlc-user-stories
description: Use when requirements need to be converted into INVEST-compliant user stories with acceptance criteria.
metadata:
  version: 0.7.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/user-stories.md
---

# aidlc-user-stories

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 사용자 스토리 생성: 요구사항을 INVEST 기준 스토리로 변환 -->
<!-- Hold/Skip: _shared/import-review-protocol.md 참조 -->

## Purpose

요구사항을 INVEST 기준 사용자 스토리로 변환한다.
비대화형 생성 — requirements.md를 기반으로 일괄 변환하고, 변경 요청은 오케스트레이터 게이트에서 처리.

### IMPORT 모드
User-stories는 IMPORT 미지원. requirements-analysis 결과를 기반으로 생성하는 것이 핵심 가치.
IMPORT 신호 수신 시: "User-stories는 IMPORT 미지원입니다. GENERATE 모드로 실행합니다." 메시지 후 GENERATE 진행.

### UPDATE 모드
호출 텍스트에 `UPDATE` 키워드 포함 시 활성화:
`"aidlc-user-stories: UPDATE — 기존 스토리 유지, [변경 내용] 반영"`

UPDATE 모드에서는:
1. `devflow-docs/inception/user-stories.md` 읽기 (기존 스토리)
2. `devflow-docs/inception/requirements.md` 읽기 (변경된 요구사항)
3. 변경 요청과 기존 스토리를 대조하여 **연관성 판단**:
   - **연관 스토리 있음** (동일 액터/기능 범위) → 해당 스토리를 기반으로 수정/확장 (수용 기준 보강, 우선순위 변경 등). Edit 도구로 해당 섹션만 교체
   - **연관 스토리 없음** (새로운 액터/기능) → 신규 스토리로 기존 목록에 추가 (번호는 기존 마지막 번호 이후부터). Edit 도구로 삽입
   - **요구사항 삭제로 스토리가 불필요** → 해당 스토리 삭제 (번호 재부여 안 함)
4. `## Change Log` 섹션에 변경 내역 기록: `- [ISO 8601] UPDATE: [변경 요약]`
5. `user-stories.md` 업데이트 후 STOP

**도구 선택**: 부분 업데이트에는 반드시 Edit 도구를 사용한다. Write 도구로 전체 덮어쓰기 금지.

Step 1, 2, 3, 4는 실행하지 않는다.

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

### Step 4 참고: 기존 파일이 존재할 때

인라인 신호 없이 재호출되었는데 `user-stories.md`가 이미 존재하면 **UPDATE로 간주**한다.
기존 내용 보존이 기본값이다.

## Review

conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/user-stories.md
- 리뷰어: artifact-reviewer-prompt.md

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 액터: [count]명 ([액터명 나열])
- 사용자 스토리: [count]개 (Must: [N], Should: [N], Could: [N])
- 산출물: devflow-docs/inception/user-stories.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

## Common Issues

### requirements.md에 사용자 유형이 명시되지 않은 경우
- 기능 요구사항에서 암묵적 액터 추출
- "기본 사용자" 액터를 생성하여 매핑
- 산출물에 "⚠️ 명시적 액터 없음 — 요구사항에서 추론" 기록

### 요구사항이 기술 중심이고 사용자 스토리로 변환이 어려운 경우
- 기술 요구사항은 "시스템" 액터로 매핑 (예: As a system, I want...)
- 순수 인프라 요구사항은 스토리 변환 스킵하고 "기술 요구사항" 섹션에 별도 기록
