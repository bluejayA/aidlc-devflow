---
name: aidlc-requirements-analysis
description: Use when user requirements need to be analyzed, structured into a requirements document, or when open questions from a previous analysis need resolution.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/requirements.md
---

# aidlc-requirements-analysis

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 요구사항 분석: 적응형 깊이로 사용자 의도와 요구사항을 분석 -->

## Purpose

Analyze and document requirements at a depth appropriate to the request's complexity.

## Execution Modes

### Normal Mode (기본)
일반 호출. Step 1부터 순서대로 실행.

### QUESTIONS Mode
호출 텍스트에 `QUESTIONS` 키워드 포함 시 활성화:
`"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"`

QUESTIONS 모드에서는:
1. `devflow-docs/inception/requirements.md` 읽기
2. `## Open Questions` 섹션의 미해결 질문만 one-at-a-time으로 처리
3. 답변을 `## Assumptions` 또는 해당 요구사항 섹션에 반영
4. `requirements.md` 업데이트 후 STOP

Step 1, 2, 3, 4는 실행하지 않는다.

### QUESTIONS 모드 반환값
미해결 질문이 남아있으면 `열린 질문: [N]개` 패턴을 포함하여 반환. 모두 해결되면 `열린 질문: 0개`.

### UPDATE 모드
호출 텍스트에 `UPDATE` 키워드 포함 시 활성화:
`"aidlc-requirements-analysis: UPDATE — 기존 분석 유지, [변경 내용] 반영"`

UPDATE 모드에서는:
1. `devflow-docs/inception/requirements.md` 읽기 (기존 분석)
2. 변경 요청과 기존 요구사항을 대조하여 **연관성 판단**:
   - **연관 요구사항 있음** (동일 기능/영역) → 해당 항목을 기반으로 수정/확장 (우선순위 변경, 기준 보강 등). Edit 도구로 해당 섹션만 교체
   - **연관 요구사항 없음** (새로운 기능) → 신규 항목으로 기존 목록에 추가. Edit 도구로 삽입
   - **요구사항 삭제** → 해당 항목 삭제 + 연쇄 영향 확인 (Assumptions, Open Questions에서 관련 항목 제거/갱신)
3. 변경이 다른 섹션에 영향을 주는지 확인:
   - Assumptions: 변경으로 무효화된 가정이 있으면 제거 또는 갱신
   - Open Questions: 변경에서 새 질문이 발생하면 추가
   - Technology Stack, Non-Functional Requirements: 영향이 있으면 갱신
4. `## Change Log` 섹션에 변경 내역 기록: `- [ISO 8601] UPDATE: [변경 요약]`
5. `requirements.md` 업데이트 후 STOP

**도구 선택**: 부분 업데이트에는 반드시 Edit 도구를 사용한다. Write 도구로 전체 덮어쓰기 금지.

Step 1, 2, 3, 4, 5는 실행하지 않는다.

**UPDATE 범위 제한**: User Intent 자체를 변경하는 요청은 UPDATE 대상이 아니다. "방향을 바꾸고 싶다"는 요청에는 "전체 재분석이 필요합니다"라고 안내하고 일반 모드로 재호출을 유도한다.

## Execute

### Step 1: Load complexity

**호출 텍스트에서 complexity 확인 (Primary)**:
호출 텍스트에 `Complexity: [level]` 패턴이 있으면 그 값을 사용:
- "aidlc-requirements-analysis 실행. Complexity: Standard" → Standard 사용
- "[Complexity: Standard] 오케스트레이터에서 확정된 복잡도로 분석합니다." 표시

**devflow-state에서 확인 (Fallback)**:
호출 텍스트에 complexity 정보가 없으면 `devflow-docs/devflow-state.md`의 `## Complexity` 필드를 읽는다.
해당 필드도 없으면 기존 기준으로 자체 판단:

**Choose Minimal if ALL of:**
- Single, clearly defined feature
- No ambiguity in requirements
- No cross-component dependencies
- Low risk (reversible, isolated)

**Choose Comprehensive if ANY of:**
- Multiple components or services affected
- High risk or irreversible changes
- Ambiguous requirements
- External integrations involved
- Performance or security critical

**Otherwise: Standard**

### Step 2: Interpretation check (Minimal 제외)

<!-- 해석 분기 확인: 동등하게 유효한 해석이 2가지 이상 존재하는지 판단 -->

Skip this step entirely if depth is **Minimal**.

For **Standard** and **Comprehensive**, ask: *"이 요청에 동등하게 유효한 해석이 2가지 이상 존재하는가?"*

**판단 기준 — 해석이 분기되는 신호:**
- 요청 키워드가 여러 구현 방식을 가리킴 (예: "검색", "알림", "인증")
- 기술 선택이 요구사항 자체를 바꿀 수 있음 (예: 실시간 vs 배치)
- 사용자가 최종 사용자 유형이나 사용 맥락을 명시하지 않음

**해석이 분기되지 않으면:** Step 3으로 바로 진행.

**해석이 분기되면:** 2-3가지 해석을 제시하고 사용자의 확인을 받은 후 Step 3으로 진행.

```
이 요청은 다음 중 어떤 방향인가요?

A) [해석 1] — [한 줄 설명]
B) [해석 2] — [한 줄 설명]
C) [해석 3] — [한 줄 설명, 있는 경우]

직접 설명하셔도 됩니다.
```

선택된 해석을 requirements.md의 `## User Intent`에 반영한다.

**session-summary 중간 기록**: 해석 확정 후 session-summary.md의 `## Completed Work`에 `[~] requirements-analysis — 해석 확정([선택]안)` 업데이트 + `## For Next Session`에 미결 질문 목록 기록.

#### Ambiguity Resolution Loop (Standard / Comprehensive)

해석 선택 후, 다음 모호성 신호를 탐지한다:
- "~하거나", "둘 다", "상황에 따라", "아직 모르겠어", "적당히"
- 설계 결정을 내리기에 불충분한 답변 (조건부 표현, 수치 없는 모호한 표현)

**신호 감지 시**: 후속 질문 ONE at a time:
```
[이전 답변]을 더 구체화해야 합니다.
A와 B 중에서 상충할 때 어느 쪽을 우선하시겠어요?
```

모호성이 해소될 때까지 반복.

**사용자가 "그냥 진행해" 또는 "계속해" 요청 시**:
- 해소되지 않은 항목을 가정으로 확정
- requirements.md의 `## Assumptions`에 기록
- 반환 텍스트에 "가정으로 처리된 항목: [N]개 — [목록]" 포함
- STOP (승인 대기 없음 — 오케스트레이터 gate에서 표시)

### Step 2b: Tech Stack Selection (조건부)

> Minimal depth에서도 실행한다. 기술 스택은 이후 모든 단계의 전제 조건이므로.

#### 2b-1: 스킵 판단 (카탈로그 Read 없이)

다음 3가지 소스를 순서대로 확인한다:

| 우선순위 | 소스 | 확인 방법 |
|---------|------|----------|
| 1 | CLAUDE.md 사전 지정 | `workspace.md`의 `## Pre-specified Tech Stack` 섹션 존재 여부. 있으면 해당 항목은 확정 |
| 2 | Brownfield 감지 | `workspace.md`의 `## Technology Stack` (Brownfield) 섹션. Language, Framework, DB 등이 감지되었으면 해당 항목은 확정 |
| 3 | 사용자 프리셋 | `tech-stack-defaults.md`의 `## 사용자 프리셋` 섹션 확인 |

**스킵 판단 결과:**
- **전체 스킵**: 소스 1 또는 2에서 Language + Framework + DB + Testing이 모두 확정됨 → `[기술 스택: 사전 지정 — 질문 스킵]` 기록, Step 3으로
- **부분 스킵**: 일부만 확정 → 미확정 계층만 2b-2로
- **스킵 불가**: Greenfield + CLAUDE.md 미지정 → 모든 계층 2b-2로

#### 2b-2: 카탈로그 선택 (필요할 때만 Read)

미커버 계층에 대해 순서대로 처리:

**1. 프리셋 확인**: `tech-stack-defaults.md`에 해당 계층의 프리셋이 있으면:
```
[계층] 기술 스택에 프리셋이 있습니다:
→ [프리셋 기술 조합]

이대로 사용하시겠습니까? (Y/n)
```
- Y → 프리셋 수용, 다음 계층으로 (카탈로그 Read 불필요)
- n → 카탈로그에서 선택 (아래)

**2. 카탈로그 선택**: `tech-stack-catalog.md`의 해당 계층 섹션을 Read
- 선택지 2~5개 구성, 첫 번째 옵션에 `(권장)` 표시 (question-format-guide.md 원칙)
- "직접 입력" 포함 여부는 `tech-stack-defaults.md`의 정책 모드에 따름:
  - **open**: `X) 직접 입력` 포함
  - **guided**: `X) 직접 입력 (사유 필수)` — 선택 시 사유 질문 → requirements.md에 기록
  - **strict**: 직접 입력 미포함

**결과 기록**: `requirements.md`의 `## Technology Stack` 섹션에:

```markdown
## Technology Stack

| 계층 | 선택 | 소스 | 비고 |
|------|------|------|------|
| [계층명] | [기술명] | [CLAUDE.md | Brownfield 감지 | 프리셋 | 카탈로그 선택 | 직접 입력] | [비고] |
```

guided 모드에서 카탈로그 외 기술 선택 시 `## 기술 스택 결정` 섹션에 사유 테이블 추가.

### Step 3: Execute at chosen depth

#### Minimal
1. Document user's intent in one paragraph
2. List 3-5 key acceptance criteria
3. Note any assumptions made

#### Standard
1. Analyze user intent (Step 2에서 확정된 해석 기반)
2. List functional requirements (what the system must do)
3. List non-functional requirements (performance, security, etc.)
4. Identify constraints and assumptions
5. Note open questions (if any)
6. 핵심 질문 (최대 2개, one at a time): 요구사항에서 설계 방향을 바꿀 수 있는 불확실성이 있으면 질문. 없으면 스킵.
   - 처리 방식: "실시간 처리가 필요한가요, 배치로 충분한가요?"
   - 사용자 유형: "단일 사용자인가요, 다중 사용자인가요?"
   - 각 답변 후 Ambiguity Resolution Loop 발동 여부 판단.
   - **session-summary 중간 기록**: 각 핵심 질문 답변 후 `[~] requirements-analysis — 질문 N/M 완료` 업데이트.

#### Comprehensive
1. Full intent analysis (Step 2에서 확정된 해석 기반)
2. Detailed functional requirements with priority (Must/Should/Could)
3. Non-functional requirements with measurable criteria
4. Risk assessment (High/Medium/Low per requirement)
5. Dependencies and constraints
6. Open questions — ask user ONE at a time before proceeding

---

<!-- 아래 테이블은 Step 3/4 전체에 적용되는 정책 요약 -->
### Depth별 질문 정책

| Depth | 해석 분기 | 핵심 질문 | Ambiguity Loop |
|-------|-----------|-----------|----------------|
| Minimal | 없음 | 없음 | 없음 |
| Standard | 있음 | 최대 2개 (each → loop) | 있음 |
| Comprehensive | 있음 | 제한 없음 (each → loop) | 있음 |

### Step 4: Ask clarifying questions (Comprehensive only)

<!-- Comprehensive 깊이에서 열린 질문이 있을 때만 -->

열린 질문이 있는 경우, 질문을 시작하기 전에 맥락을 먼저 선언한다:

```
요구사항을 확정하기 전에 몇 가지 질문을 드리겠습니다.
[질문 수]개의 열린 질문이 있습니다.
```

그 후 ONE question at a time. Wait for answer before asking next.

### Step 5: Save artifact

Create `devflow-docs/inception/requirements.md`:

```markdown
# Requirements Analysis

**Depth**: [Minimal | Standard | Comprehensive]
**Timestamp**: [ISO 8601]

## User Intent
[What the user wants to achieve — Step 2에서 확정된 해석 포함]

## Functional Requirements
[List of requirements]

## Non-Functional Requirements
[Performance, security, etc.]

## Technology Stack
| 계층 | 선택 | 소스 | 비고 |
|------|------|------|------|
[Step 2b 결과]

## Assumptions
[List of assumptions made]

## Open Questions
[Any unresolved questions]
```

## Review

conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/requirements.md
- 리뷰어: artifact-reviewer-prompt.md

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 분석 깊이: [Minimal | Standard | Comprehensive]
- 해석 확정: [확정된 해석 한 줄 요약, 또는 "단일 해석 — 확인 불필요"]
- 기능 요구사항: [count]개
- 기술 스택: [사전 지정 (질문 스킵) | 프리셋 N개 + 선택 M개 | 전체 선택 N개]
- 열린 질문: [count]개
- 가정으로 처리된 항목: [0개 | N개 — 항목명 목록]
- 산출물: devflow-docs/inception/requirements.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

## Common Issues

### User provides no requirements context
요청이 너무 모호하면:
- Comprehensive depth 기본 적용
- Step 2에서 가능한 해석 제시

### Step 2에서 해석이 3가지 이상으로 늘어날 때
- 가장 가능성 높은 2-3가지로 압축
- 나머지는 "기타: 다른 방향이라면 직접 설명해주세요"로 열어두기

### Step 2b: tech-stack-defaults.md에 정책 모드가 없을 때
- 기본값: **open** (직접 입력 자유 허용)
- tech-stack-defaults.md 파일 자체가 없으면 Step 2b 전체를 스킵하고, 사용자에게 기술 스택을 자유 입력으로 질문
