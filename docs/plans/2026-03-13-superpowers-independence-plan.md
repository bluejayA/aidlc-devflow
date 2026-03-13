# Superpowers 독립 + 기능 포팅 구현 계획

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** aidlc-like 플러그인의 superpowers 런타임 의존도를 0으로 만들고, devflow 전용 기능 7개를 aidlc-like 구조(conventions SSOT, 토큰 효율)로 포팅한다.

**Complexity:** Comprehensive

**Architecture:** shared 기반을 먼저 확장하고(conventions, tdd-protocol, patterns), 그 위에 신규 스킬 7개를 구축한다. 각 스킬은 공통 로직을 shared로 참조하여 인라인 중복을 제거한다. 마지막으로 기존 스킬의 superpowers 참조를 검증/교체한다.

**Tech Stack:** Claude Code Plugin (Markdown SKILL.md), YAML frontmatter

---

## Chunk 1: Shared 기반 확장

### Task 1: `_shared/patterns/` 디렉토리 + 3개 패턴 파일 생성

**Files:**
- Create: `skills/_shared/patterns/three-mode-selection.md`
- Create: `skills/_shared/patterns/hold-mechanism.md`
- Create: `skills/_shared/patterns/brownfield-exploration.md`

- [ ] **Step 1: `three-mode-selection.md` 생성 (~30줄)**

devflow `shared/patterns/three-mode.md`를 참고하되 aidlc-like 구조에 맞게 축약:

```markdown
# Three-Mode Selection

오케스트레이터 또는 사용자가 stage/스킬 실행 모드를 선택한다.

## 모드 정의

| 모드 | 트리거 | 동작 |
|------|--------|------|
| **Together** | 기본값. 처음부터 함께 진행 | Step별 순차 실행. 각 Step 사이 Hold 가능 |
| **Import** | 사용자가 기존 문서/결과물 제공 | 문서 검증 → 갭/충돌 피드백 → 확인 |
| **Skip** | 사용자가 명시적 스킵 요청 | devflow-state에 SKIPPED 기록 후 다음 단계 |

## 오케스트레이터 규칙

- 모드 선택은 오케스트레이터가 게이트로 제시
- stage skill은 선택된 모드만 실행 (모드 선택 로직 포함 금지)
- Import 모드에서도 Review는 필수 (conventions Review Workflow 참조)

## Together 모드 상세

- Step별 산출물 제시 → 사용자 확인 후 다음 Step
- Hold 시그널 수신 시 → `hold-mechanism.md` 참조
- 옵션 제시 형식: "A안은... B안은..." (Claude는 옵션 제시자)

## Import 모드 상세

- 사용자 제공 파일/내용 수신
- 검증: 갭(누락), 충돌(모순), 적합성(현재 컨텍스트)
- 검증 결과 피드백 → 사용자 확인 → 완료
```

- [ ] **Step 2: `hold-mechanism.md` 생성 (~25줄)**

```markdown
# Hold Mechanism

진행 중 사용자가 일시 중단을 요청할 때의 처리 규약.

## Hold 시그널

사용자가 "잠깐", "Hold", "멈춰" 등으로 중단 요청 시 발동.

## Hold 처리 절차

1. 현재 Step까지의 산출물을 파일에 저장
2. 산출물 파일에 상태 마커 추가:
   ```markdown
   ## Status: partial — [미완료 항목 목록]
   ```
3. devflow-state에는 Completed/Skipped에 기록하지 않음 (incomplete 상태)
4. devflow-audit에 Hold 이벤트 로깅

## Resume 절차

1. 세션 재개 시 산출물 파일의 `Status: partial` 마커 탐지
2. 미완료 항목 목록 표시 → 사용자에게 계속 진행 여부 확인
3. 승인 시 중단 지점부터 재개
4. devflow-audit에 Resume 이벤트 로깅

## 적용 범위

- Together 모드의 모든 Step 사이
- Import 모드의 검증 단계
- 오케스트레이터의 게이트 대기 중
```

- [ ] **Step 3: `brownfield-exploration.md` 생성 (~35줄)**

```markdown
# Brownfield Exploration

기존 코드베이스에서 작업할 때의 탐색 프로토콜.

## 탐색 순서

1. **설계 문서 확인**: `devflow-docs/inception/` 또는 `docs/plans/`에 기존 분석 결과가 있는지 확인
2. **있으면**: 기존 분석 결과 참조 + `git log`로 이후 변경사항만 확인
3. **없으면**: 아래 전체 체크리스트 실행

## 전체 탐색 체크리스트

| 항목 | 확인 대상 | 방법 |
|------|-----------|------|
| 프로젝트 구조 | 디렉토리 레이아웃, 진입점 | `ls`, README |
| 의존성 | 패키지 매니저, 주요 라이브러리 | package.json, go.mod, Cargo.toml 등 |
| 기존 패턴 | 네이밍, 아키텍처, 에러 처리 | 핵심 파일 3-5개 읽기 |
| 최근 변경 | 활발한 영역, 진행 중 작업 | `git log --oneline -20` |
| 테스트 구조 | 테스트 프레임워크, 디렉토리, 실행 방법 | 테스트 파일 탐색 |
| 영향 범위 | 변경 시 영향받는 컴포넌트 | import/dependency 추적 |

## 핵심 원칙

- **기존 패턴 존중**: 새 패턴 도입 전 기존 방식 확인. 기존 방식이 있으면 따른다.
- **최소 탐색**: 필요한 범위만 탐색. 전체 코드베이스를 읽지 않는다.
- **탐색 결과 선언**: 탐색 완료 시 발견한 패턴/영향범위/컨벤션을 요약 선언.

## 참조하는 스킬

- `aidlc-brainstorming` — 설계 전 컨텍스트 파악
- `aidlc-workspace-detection` — 그린필드/브라운필드 판단 후 브라운필드 시 실행
```

- [ ] **Step 4: 커밋**

```bash
git add skills/_shared/patterns/
git commit -m "feat: shared patterns 3개 추가 (three-mode, hold, brownfield)"
```

---

### Task 2: `_shared/devflow-conventions.md` 확장

**Files:**
- Modify: `skills/_shared/devflow-conventions.md`

- [ ] **Step 1: conventions.md 읽기 및 확장 위치 확인**

파일 끝(또는 적절한 섹션)에 아래 3개 규약 추가.

- [ ] **Step 2: Brainstorming HARD-GATE 규약 추가**

```markdown
## Brainstorming HARD-GATE

새 기능, 컴포넌트, 동작 수정 시 설계 문서 작성 + 사용자 승인 전까지 코드 작성 금지.
"단순해서 설계 불필요"는 합리화 — 모든 프로젝트에 적용.
설계 분량은 복잡도에 따라 조절 (Minimal: 2-5문장, Comprehensive: 전체 섹션).
```

- [ ] **Step 3: TDD Iron Law 규약 추가**

```markdown
## TDD Iron Law

실패하는 테스트 없이 프로덕션 코드 작성 금지. 상세: `_shared/tdd-protocol.md` 참조.
```

- [ ] **Step 4: Subagent Dispatch Rules 규약 추가**

```markdown
## Subagent Dispatch Rules

- 독립적 태스크 2개 이상일 때만 서브에이전트 디스패치
- 구현 서브에이전트 병렬 실행 금지 (충돌 방지)
- Two-stage review 필수: spec compliance → code quality (순서 변경 금지)
- Model Selection: mechanical task → haiku, integration → sonnet, architecture/review → opus
```

- [ ] **Step 5: 커밋**

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "feat: conventions에 HARD-GATE, TDD Iron Law, Subagent 규약 추가"
```

---

### Task 3: `_shared/tdd-protocol.md` 확장

**Files:**
- Modify: `skills/_shared/tdd-protocol.md`

- [ ] **Step 1: tdd-protocol.md 읽기 및 확장 위치 확인**

- [ ] **Step 2: 합리화 방지 테이블 추가**

기존 Red Flags 섹션 근처에 추가:

```markdown
## 합리화 방지

| 합리화 | 현실 |
|--------|------|
| "너무 단순해서 테스트 불필요" | 단순한 코드가 가장 자주 깨짐 |
| "나중에 테스트 추가" | 나중은 오지 않음 |
| "리팩토링이라 테스트 불필요" | 리팩토링이야말로 테스트 필수 |
| "시간이 없다" | 테스트 없는 코드가 더 많은 시간 소모 |
| "프로토타입이라 괜찮다" | 프로토타입은 프로덕션이 됨 |
```

- [ ] **Step 3: Red Flags 보강 (기존 항목에 추가)**

기존 Red Flags에 아래 항목이 없으면 추가:

```markdown
- "이건 테스트하기 어렵다" → 설계 문제 신호 (테스트 불가 = 결합도 높음)
- GREEN에서 바로 다음 기능으로 이동 → REFACTOR 스킵은 기술 부채
- 테스트가 구현 세부사항에 의존 → 인터페이스를 테스트할 것
```

- [ ] **Step 4: 커밋**

```bash
git add skills/_shared/tdd-protocol.md
git commit -m "feat: tdd-protocol에 합리화 방지 테이블 + Red Flags 보강"
```

---

### Task 4: 서브에이전트 프롬프트 3개 추가

**Files:**
- Create: `skills/_shared/reviewers/implementer-prompt.md`
- Create: `skills/_shared/reviewers/spec-reviewer-prompt.md`
- Create: `skills/_shared/reviewers/code-quality-reviewer-prompt.md`

- [ ] **Step 1: `implementer-prompt.md` 생성 (~40줄)**

devflow `subagent-driven-development/implementer-prompt.md`를 참고하여 작성:

```markdown
# Implementer Subagent Prompt

## Task
{TASK_FULL_TEXT}

## Context
{SCENE_SETTING_CONTEXT}

## Before You Begin

요구사항이 불명확하면 구현 전에 질문하라. 추측하지 말 것.

## Your Job

1. 요구사항 이해 → 불명확하면 질문 (status: NEEDS_CONTEXT)
2. TDD 사이클로 구현 (`_shared/tdd-protocol.md` 준수)
   - RED: 실패하는 테스트 작성
   - GREEN: 최소 구현으로 통과
   - REFACTOR: 정리
3. 모든 테스트 통과 확인
4. Self-Review 수행 (아래 체크리스트)
5. 커밋
6. 결과 보고

## Self-Review Checklist

- [ ] 요구사항 전부 구현했는가?
- [ ] 요청하지 않은 것을 추가하지 않았는가? (YAGNI)
- [ ] 테스트가 동작을 검증하는가? (구현 세부사항 아님)
- [ ] 기존 테스트가 모두 통과하는가?
- [ ] 코드가 기존 패턴을 따르는가?

## Report Format

**Status**: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED

**구현 내용**: [요약]
**테스트 결과**: [통과/실패 수]
**변경 파일**: [목록]
**Self-Review 결과**: [발견사항]
**우려사항** (있을 경우): [상세]
```

- [ ] **Step 2: `spec-reviewer-prompt.md` 생성 (~40줄)**

```markdown
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
```

- [ ] **Step 3: `code-quality-reviewer-prompt.md` 생성 (~40줄)**

```markdown
# Code Quality Reviewer Prompt

> Spec compliance review를 통과한 후에만 실행할 것.

## Purpose

구현의 코드 품질을 검증한다. Spec 준수는 이미 확인됨 — 여기서는 구현이 잘 만들어졌는지만 본다.

## Context
- **구현 내용**: {WHAT_WAS_IMPLEMENTED}
- **요구사항**: {PLAN_OR_REQUIREMENTS}
- **변경 범위**: {BASE_SHA}..{HEAD_SHA}

## Review Focus

1. **코드 품질**: 가독성, 네이밍, 구조
2. **테스트 품질**: 커버리지, 경계 케이스, 테스트 격리
3. **아키텍처**: 기존 패턴 준수, 적절한 추상화 수준
4. **보안**: OWASP Top 10 기준 취약점

## Issue Classification

- **Critical**: 반드시 수정 (버그, 보안 취약점, 데이터 손실 위험)
- **Important**: 수정 권장 (성능, 유지보수성, 테스트 갭)
- **Minor**: 선택적 (스타일, 네이밍 개선)

## Report Format

**Strengths**: [잘된 점]
**Issues**: [Critical/Important/Minor 분류별 목록]
**Assessment**: ✅ Approved | ❌ Requires Changes (Critical/Important 이슈 시)
```

- [ ] **Step 4: 커밋**

```bash
git add skills/_shared/reviewers/implementer-prompt.md skills/_shared/reviewers/spec-reviewer-prompt.md skills/_shared/reviewers/code-quality-reviewer-prompt.md
git commit -m "feat: subagent 리뷰어 프롬프트 3개 추가 (implementer, spec, quality)"
```

---

## Chunk 2: 계층 1 스킬 — brainstorming + writing-plans

### Task 5: `aidlc-brainstorming` 스킬 생성

**Files:**
- Create: `skills/aidlc-brainstorming/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~200줄)**

devflow `brainstorming/SKILL.md`(472줄)을 참고하되 conventions SSOT 패턴으로 축약:

```markdown
---
name: aidlc-brainstorming
description: 아이디어를 설계로 전환하는 협업 대화 스킬. HARD-GATE — 설계 승인 전 코드 작성 금지.
invoke_mode: user-invocable
---

# Brainstorming

아이디어를 설계 문서로 전환한다.

> **HARD-GATE**: `_shared/devflow-conventions.md` Brainstorming HARD-GATE 참조. 설계 승인 전 코드 작성 금지.

**시작 시 선언**: "aidlc-brainstorming 스킬을 사용하여 설계를 진행합니다."

## 프로세스

### Step 1: 프로젝트 컨텍스트 탐색

- 파일, 문서, 최근 커밋 확인
- 브라운필드인 경우: `_shared/patterns/brownfield-exploration.md` 참조
- 범위 판단: 여러 독립 서브시스템이면 먼저 분해 제안

### Step 2: 명확화 질문

- **한 번에 하나만** 질문
- 객관식 선호 (가능한 경우)
- 각 답변에 **Ambiguity Resolution Loop** 적용 (아래 참조)

### Step 3: 복잡도 선언 + 접근법 제안

**복잡도 선언** (접근법 제안 전 필수):

```
이 작업의 복잡도를 **[Minimal/Standard/Comprehensive]**로 판단했습니다.
이유: [한 줄]

다르게 조정하시겠습니까?
```

| 단계 | 기준 | 설계 분량 | 접근법 |
|------|------|-----------|--------|
| Minimal | 단일 파일/함수, 명확한 경로 | 2-5문장 | 1-2개 |
| Standard | 새 컴포넌트, 복수 고려사항 | 표준 섹션 | 2-3개 |
| Comprehensive | 시스템 설계, 아키텍처 결정 | 전체 섹션 + 다이어그램 | 2-3개 |

사용자 승인 후 2-3개 접근법 제안. 추천안 + 이유 먼저 제시.

### Step 4: 설계 제시

- 섹션별 제시, 각 섹션 승인 후 다음
- 섹션: architecture, components, data flow, error handling, testing
- 각 섹션 분량은 복잡도에 비례

**설계 원칙**:
- 단일 책임 단위로 분해
- 잘 정의된 인터페이스로 소통
- 독립적으로 이해/테스트 가능
- YAGNI — 불필요한 기능 제거

### Step 5: 설계 문서 작성

- 저장 경로: `docs/plans/YYYY-MM-DD-<topic>-design.md`
- 가정이 있으면 `## Assumptions` 섹션 포함
- 문서 상단에 `**Complexity:** [Minimal|Standard|Comprehensive]` 기록
- 커밋

### Step 6: Spec Review + 사용자 리뷰 + 전환

1. `_shared/reviewers/` 기반 Review Workflow 실행 (conventions 참조)
   - spec-document-reviewer 역할로 리뷰 서브에이전트 디스패치
   - 이슈 발견 시 수정 → 재리뷰 (최대 5회, 초과 시 사용자 판단)
2. 사용자 리뷰 게이트:
   > "Spec이 `<경로>`에 저장되었습니다. 리뷰 후 변경사항이 있으면 알려주세요."
3. 사용자 승인 후 `aidlc-writing-plans` 스킬로 전환

---

## Ambiguity Resolution Loop

명확화 질문의 답변을 받을 때마다 적용.

### 모호성 신호

- "depends", "maybe", "not sure", "~하거나", "~일 수도", "상황에 따라"
- 키워드 없어도 설계 결정에 불충분하면 모호한 것으로 간주

### 후속 질문 방향

| 유형 | 예시 답변 | 후속 질문 |
|------|-----------|-----------|
| 선택 모호 | "A나 B나 괜찮아요" | "어떤 기준으로 A를, 어떤 기준으로 B를?" |
| 범위 모호 | "적당히 빠르면 됩니다" | "구체적으로 어느 정도? (예: 1초 이내)" |
| 우선순위 모호 | "성능도 비용도 중요" | "둘이 상충할 때 어느 쪽 우선?" |

### 탈출 조건

1. 모든 모호함 해소 → 다음 단계
2. 사용자가 "그냥 진행해" → 가정 목록 정리 → 승인 대기 → Assumptions에 기록

---

## 핵심 원칙

- 한 번에 하나만 질문
- 객관식 선호
- YAGNI 엄격 적용
- 2-3개 대안 제시 후 선택
- 섹션별 점진적 검증
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-brainstorming/
git commit -m "feat: aidlc-brainstorming 스킬 추가 (superpowers 독립)"
```

---

### Task 6: `aidlc-writing-plans` 스킬 생성

**Files:**
- Create: `skills/aidlc-writing-plans/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~180줄)**

devflow `writing-plans/SKILL.md`(281줄)을 참고하되 축약:

```markdown
---
name: aidlc-writing-plans
description: 설계 문서를 상세 구현 계획으로 변환. aidlc-workflow-planning(INCEPTION 실행 계획)과 구분 — 이 스킬은 태스크별 구현 계획 작성.
invoke_mode: user-invocable
---

# Writing Plans

설계 문서(spec)를 엔지니어가 zero context에서도 실행 가능한 구현 계획으로 변환한다.

**시작 시 선언**: "aidlc-writing-plans 스킬을 사용하여 구현 계획을 작성합니다."

## Scope Check

스펙이 여러 독립 서브시스템을 포함하면 서브시스템별로 계획을 분리한다.

## Complexity-Based Detail

설계 문서의 `Complexity` 값을 읽어 태스크 상세도 결정. 없으면 직접 판단.

| Complexity | 태스크 수 | 코드 포함 | Architecture |
|------------|-----------|-----------|--------------|
| Minimal | 1-3개 | 핵심 변경만 | 1문장 |
| Standard | 3-7개 | 주요 코드 | 2-3문장 |
| Comprehensive | 7개+ | 전체 코드 | 전체 섹션 |

복잡도 무관 필수 항목: 정확한 파일 경로, TDD 사이클 체크박스, 커밋.

## File Structure

태스크 정의 전 파일 구조 설계:
- 파일당 한 가지 책임
- 함께 변경되는 파일은 함께 배치
- 기존 코드베이스 패턴 따름

## Plan Document Header (필수)

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** [한 줄]
**Complexity:** [Minimal | Standard | Comprehensive]
**Architecture:** [2-3문장]
**Tech Stack:** [주요 기술]
```

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/test.py`

- [ ] **Step 1: Write failing test**
[완성된 테스트 코드]

- [ ] **Step 2: Run test — verify FAIL**
Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "..."

- [ ] **Step 3: Write minimal implementation**
[완성된 구현 코드]

- [ ] **Step 4: Run test — verify PASS**
Expected: PASS

- [ ] **Step 5: Commit**
```

## Bite-Sized Granularity

각 Step은 한 가지 행동 (2-5분):
- "실패하는 테스트 작성" — Step
- "실행하여 실패 확인" — Step
- "최소 구현" — Step
- "테스트 통과 확인" — Step
- "커밋" — Step

## Plan Review Loop

청크(≤1000줄) 단위로 작성 후 리뷰:
1. 청크 작성 완료
2. Review Workflow 실행 (conventions 참조) — plan-document-reviewer 역할
3. 이슈 발견 → 수정 → 재리뷰 (최대 5회)
4. 승인 → 다음 청크 또는 Execution Handoff

## Execution Handoff

계획 저장 후:

> "계획이 `docs/plans/<파일명>`에 저장되었습니다. 실행하시겠습니까?"

- 서브에이전트 가능 → `aidlc-subagent-driven-development` (권장)
- 별도 세션 → `aidlc-executing-plans`

## 핵심 규칙

- 정확한 파일 경로 (상대 경로 금지)
- 완성된 코드 ("검증 추가" 같은 추상적 지시 금지)
- 정확한 실행 명령 + 예상 출력
- DRY, YAGNI, TDD, 빈번한 커밋

---

**저장 경로**: `docs/plans/YYYY-MM-DD-<feature-name>-plan.md`
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-writing-plans/
git commit -m "feat: aidlc-writing-plans 스킬 추가 (superpowers 독립)"
```

---

## Chunk 3: 계층 1 스킬 — TDD + executing-plans + subagent-driven-dev

### Task 7: `aidlc-test-driven-development` 스킬 생성

**Files:**
- Create: `skills/aidlc-test-driven-development/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~250줄)**

devflow `test-driven-development/SKILL.md`(613줄)을 참고하되 tdd-protocol.md에 흡수된 내용은 참조만:

```markdown
---
name: aidlc-test-driven-development
description: TDD 원칙 강제. Rigid — 예외 없이 정확히 따를 것. 실패하는 테스트 없이 프로덕션 코드 작성 금지.
invoke_mode: user-invocable
---

# Test-Driven Development

> **Skill Type: Rigid** — 정확히 따를 것. 상황에 맞게 적응하지 않는다.

> **Iron Law**: `_shared/devflow-conventions.md` TDD Iron Law 참조. 실패하는 테스트 없이 프로덕션 코드 작성 금지.

**시작 시 선언**: "aidlc-test-driven-development 스킬을 사용합니다. TDD Iron Law를 적용합니다."

## RED-GREEN-REFACTOR

`_shared/tdd-protocol.md` 참조. 아래는 요약:

### RED: 실패하는 테스트 작성

- 한 가지 동작만 테스트
- 명확한 이름 (테스트가 문서 역할)
- 실제 코드 사용 (모킹 최소화)

### Verify RED (필수)

- 테스트가 실패해야 함
- 실패 이유가 "기능 부재"여야 함 (오타, 구문 에러 아님)
- 실패 메시지 확인

### GREEN: 최소 구현

- 테스트를 통과시키는 가장 간단한 코드
- YAGNI — 요청되지 않은 기능 금지
- "나중에 필요할 것 같다"는 합리화

### Verify GREEN (필수)

- 해당 테스트 통과
- 기존 테스트 모두 통과
- 에러/경고 없음

### REFACTOR: 코드 정리

- 중복 제거
- 이름 개선
- 헬퍼 추출
- **테스트는 계속 통과해야 함**

## When to Use

**항상 사용** — 이것이 기본값. 아래 예외 외에는 예외 없음.

## Exceptions (사용자 명시적 승인 필요)

- Throwaway 프로토타입 (사용 후 삭제 확인)
- 설정 파일 변경 (로직 없음)
- 자동 생성 코드 (생성기를 테스트)

예외를 적용하려면 사용자가 명시적으로 "TDD 스킵"을 승인해야 한다.

## 합리화 방지 + Red Flags

`_shared/tdd-protocol.md` "합리화 방지" 및 "Red Flags" 섹션 참조.

핵심만 발췌:
- 코드 먼저 작성했으면 → **삭제하고 처음부터**
- 테스트가 즉시 통과하면 → 기존 동작 테스트 중이거나 잘못된 테스트
- "나중에 테스트 추가"는 → 나중은 오지 않음

## Self-Review

구현 완료 후, 리뷰어에게 보내기 전 self-review:

- [ ] 모든 프로덕션 코드에 실패 테스트가 먼저 있었는가?
- [ ] RED 확인을 매번 했는가?
- [ ] GREEN에서 최소 구현만 했는가?
- [ ] REFACTOR 후 테스트가 모두 통과하는가?
- [ ] 합리화를 하지 않았는가?

## 예시: API 엔드포인트 추가

```
1. RED: GET /api/users 테스트 — 404 예상
   → 실행 → FAIL (라우트 없음) ✓
2. GREEN: 라우트 + 빈 배열 반환
   → 실행 → PASS ✓
3. RED: 사용자 있을 때 반환 테스트
   → 실행 → FAIL (DB 조회 없음) ✓
4. GREEN: DB 조회 + 반환
   → 실행 → PASS ✓
5. REFACTOR: 쿼리 로직 분리
   → 실행 → PASS ✓
6. 커밋
```

## Integration

- **사용하는 스킬**: `aidlc-code-generation`, `aidlc-subagent-driven-development`, `aidlc-executing-plans`
- **참조 문서**: `_shared/tdd-protocol.md`, `_shared/devflow-conventions.md`
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-test-driven-development/
git commit -m "feat: aidlc-test-driven-development 스킬 추가 (superpowers 독립)"
```

---

### Task 8: `aidlc-executing-plans` 스킬 생성

**Files:**
- Create: `skills/aidlc-executing-plans/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~120줄)**

devflow `executing-plans/SKILL.md`(183줄)을 참고하되 축약:

```markdown
---
name: aidlc-executing-plans
description: 구현 계획을 별도 세션에서 배치 실행. 체크포인트 리뷰 + 세션 재개 지원.
invoke_mode: user-invocable
---

# Executing Plans

구현 계획 파일을 배치 단위로 실행한다.

**시작 시 선언**: "aidlc-executing-plans 스킬을 사용하여 계획을 실행합니다."

## When to Use

- 별도 세션에서 계획 실행 시 (현재 세션: `aidlc-subagent-driven-development` 사용)
- 서브에이전트 불가 환경
- 순차 실행이 필요한 tightly-coupled 태스크

## 프로세스

### Step 1: 계획 로드

1. 계획 파일 읽기 + 비판적 리뷰
2. 완료된 태스크(`[x]`) 있으면 → 현재 상태 공지 (세션 재개)
3. devflow-audit와 교차 확인
4. 우려사항 있으면 사용자와 논의
5. 우려 없으면 진행

### Step 2: 배치 실행

- 기본 배치 크기: 3 태스크
- 각 태스크: 시작 표시 → 단계 수행(TDD) → 검증 → 완료 표시

### Step 3: 배치 보고

- 구현 내용 요약
- 검증 결과
- "피드백 준비됨" 공지

### Step 4: 계속

- 사용자 피드백 반영
- 다음 배치 실행
- 반복

### Step 5: 완료

- `aidlc-finishing-a-development-branch` 스킬 호출

## 세션 재개

1. 체크박스 `[x]` 파싱으로 완료 태스크 식별
2. devflow-audit 교차 확인
3. 완료 태스크 건너뛰고 다음부터 재개

## Mid-Execution Changes

| 변경 | 절차 |
|------|------|
| **Skip** | 영향도 설명 → 확인 → `[SKIP]` 마크 → audit 기록 |
| **Restart** | 하위 의존 태스크 나열 → 경고 → 확인 → `[ ]` 재설정 |
| **Insert** | 의존성 분석 → 위치 확인 → `[NEW]` 추가 → 실행 |
| **Edit Plan** | 현재 태스크 완료 → Pause → 편집 → 재개 |
| **Pause** | 현재 태스크 완료 → audit 기록 → 재개 방법 공지 |

## 멈춰야 할 때

- 블로커 발생 (의존성 부재, 테스트 실패, 지시 불명확)
- 계획에 비판적 갭 발견
- 반복 검증 실패

## Integration

- **호출하는 스킬**: `aidlc-writing-plans` (Execution Handoff)
- **완료 시 호출**: `aidlc-finishing-a-development-branch`
- **TDD 준수**: `_shared/tdd-protocol.md`
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-executing-plans/
git commit -m "feat: aidlc-executing-plans 스킬 추가 (superpowers 독립)"
```

---

### Task 9: `aidlc-subagent-driven-development` 스킬 생성

**Files:**
- Create: `skills/aidlc-subagent-driven-development/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~180줄)**

devflow `subagent-driven-development/SKILL.md`(352줄)을 참고하되 축약:

```markdown
---
name: aidlc-subagent-driven-development
description: 구현 계획을 태스크별 서브에이전트로 실행. Fresh subagent per task + two-stage review.
invoke_mode: user-invocable
---

# Subagent-Driven Development

태스크별 신규 서브에이전트를 디스패치하여 구현하고, 2단계 리뷰(spec → quality)로 품질을 보장한다.

**시작 시 선언**: "aidlc-subagent-driven-development 스킬을 사용하여 계획을 실행합니다."

> Subagent Dispatch Rules: `_shared/devflow-conventions.md` 참조.

## When to Use

- 현재 세션에서 계획 실행 시 (별도 세션: `aidlc-executing-plans`)
- 태스크가 대부분 독립적일 때
- 서브에이전트 지원 환경 (Claude Code 등)

## 프로세스 (태스크 반복)

### 1. 계획 읽기
- 계획 파일에서 전체 태스크 텍스트 + 컨텍스트 추출
- 태스크 목록 생성

### 2. 구현 서브에이전트 디스패치
- `_shared/reviewers/implementer-prompt.md` 템플릿 사용
- 태스크 전문 + 아키텍처 컨텍스트 제공
- 서브에이전트가 계획 파일을 직접 읽지 않도록 전문 제공

### 3. Implementer Status 처리

| Status | 처리 |
|--------|------|
| **DONE** | Spec 리뷰로 진행 |
| **DONE_WITH_CONCERNS** | 우려사항 읽기 → 정정성/범위 문제면 먼저 해결, 관찰 사항이면 기록 후 진행 |
| **NEEDS_CONTEXT** | 누락 정보 제공 → 재디스패치 |
| **BLOCKED** | 평가: 컨텍스트 문제 → 추가 제공, 추론 한계 → 상위 모델, 태스크 과대 → 분할, 계획 오류 → 사용자 에스컬레이션 |

### 4. Spec Compliance 리뷰
- `_shared/reviewers/spec-reviewer-prompt.md` 템플릿 사용
- ❌ 이슈 → 구현자 수정 → 재리뷰 (반복)
- ✅ 통과 → Code Quality 리뷰로

### 5. Code Quality 리뷰
- **Spec 통과 후에만 실행** (순서 변경 금지)
- `_shared/reviewers/code-quality-reviewer-prompt.md` 템플릿 사용
- ❌ 이슈 → 구현자 수정 → 재리뷰
- ✅ 통과 → 태스크 완료

### 6. 태스크 완료 표시

### 7. 전체 완료
- 모든 태스크 완료 후 최종 코드 리뷰 디스패치
- `aidlc-finishing-a-development-branch` 호출

## Model Selection

| 복잡도 | 모델 | 기준 |
|--------|------|------|
| Mechanical | haiku | 1-2 파일, 명확한 spec, CRUD/설정 |
| Integration | sonnet | 멀티파일, API, 테스트, 리팩토링 |
| Architecture | opus | 설계 판단, 광범위한 코드베이스 이해 |

## Red Flags

- main/master에서 시작 금지 (명시적 승인 없이)
- 리뷰 스킵 금지 (spec OR quality)
- Spec 통과 전 quality 리뷰 시작 금지
- 구현 서브에이전트 병렬 실행 금지
- 서브에이전트 질문 무시 금지
- 리뷰 이슈 미해결 상태로 다음 태스크 진행 금지

## 예시 워크플로우 (축약)

```
[계획 읽기: 5개 태스크 추출]

Task 1:
  → 구현자 디스패치 → 질문 발생 → 답변 → 구현 완료
  → Spec 리뷰 ✅ → Quality 리뷰: Minor 1건 → 수정 → ✅
  → Task 1 완료

Task 2:
  → 구현자 디스패치 → 구현 완료
  → Spec 리뷰 ❌ (누락 1건) → 수정 → ✅
  → Quality 리뷰 ✅
  → Task 2 완료

...전체 완료 → 최종 리뷰 → finishing-branch
```

## Integration

- **호출하는 스킬**: `aidlc-writing-plans` (Execution Handoff)
- **완료 시 호출**: `aidlc-finishing-a-development-branch`
- **TDD 준수**: `_shared/tdd-protocol.md`
- **서브에이전트 프롬프트**: `_shared/reviewers/`
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-subagent-driven-development/
git commit -m "feat: aidlc-subagent-driven-development 스킬 추가 (superpowers 독립)"
```

---

## Chunk 4: 계층 2 + 계층 3 스킬

### Task 10: `aidlc-functional-design` 스킬 생성

**Files:**
- Create: `skills/aidlc-functional-design/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~150줄)**

devflow `functional-design/SKILL.md`(111줄)을 참고하되 aidlc-like 메타데이터 규약 적용:

```markdown
---
name: aidlc-functional-design
description: CONSTRUCTION 단계 상세 기능 설계. 도메인 엔티티, 비즈니스 규칙, 데이터 흐름, 에러 시나리오 설계.
invoke_mode: orchestrator-only
return_behavior: stop-no-gate
output_path: devflow-docs/construction/{unit}/functional-design.md
---

# Functional Design

unit별 비즈니스 로직을 상세 설계한다. application-design(아키텍처 수준)과 code-generation(구현 수준) 사이의 갭을 메운다.

## 조건부 실행

- **EXECUTE**: 복잡한 비즈니스 로직, 도메인 모델 필요, 다중 엔티티
- **SKIP**: 단순 CRUD, 설정 변경, UI만 수정
- Comprehensive 깊이일 때만 실행 (Minimal/Standard는 skip)

## 실행 모드

`_shared/patterns/three-mode-selection.md` 참조.

| 모드 | 동작 |
|------|------|
| Together | Step별 순차 설계, Hold 가능 |
| Import | 기존 설계 문서 검증 |
| Skip | devflow-state에 SKIPPED 기록 |

## Together 모드 Steps

### Step 1: 도메인 엔티티 정의

- 핵심 엔티티 목록
- 엔티티 간 관계 (1:N, N:M 등)
- 각 엔티티의 핵심 속성 + 불변 조건

### Step 2: 비즈니스 규칙

- 규칙 목록: 조건 → 동작 형식
- 규칙 간 우선순위
- 예외/엣지 케이스

### Step 3: 데이터 흐름

- 입력 → 변환 → 출력 경로
- 에러 전파 경로
- 외부 시스템 연동 포인트

### Step 4: 에러/예외 시나리오

| 시나리오 | 원인 | 처리 방식 | 사용자 메시지 |
|----------|------|-----------|---------------|
| ... | ... | ... | ... |

## code-generation 연결

- 비즈니스 규칙 → 테스트 케이스 도출 (TDD RED)
- 에러 시나리오 → 에러 핸들링 테스트
- 엔티티 불변 조건 → validation 테스트

## Review

`_shared/devflow-conventions.md` Review Workflow 참조.

## Return

```
STOP.

**Functional Design 완료**
- 산출물: `devflow-docs/construction/{unit}/functional-design.md`
- 엔티티: [N]개
- 비즈니스 규칙: [N]개
- 에러 시나리오: [N]개
```
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-functional-design/
git commit -m "feat: aidlc-functional-design 스킬 추가 (devflow 포팅)"
```

---

### Task 11: `aidlc-superpowers-tracking` 스킬 생성

**Files:**
- Create: `skills/aidlc-superpowers-tracking/SKILL.md`

- [ ] **Step 1: SKILL.md 생성 (~60줄)**

devflow `superpowers-tracking/SKILL.md`(76줄)을 참고하되 축약:

```markdown
---
name: aidlc-superpowers-tracking
description: 세션 중 스킬/패턴 사용을 추적하여 워크플로우 개선 인사이트 제공.
invoke_mode: user-invocable
---

# Superpowers Tracking

세션에서 사용된 스킬과 패턴을 추적하고, 워크플로우 개선을 위한 인사이트를 제공한다.

## 핵심 기능

### 1. 세션 요약

devflow-audit.md를 파싱하여:
- 호출된 스킬 목록
- 각 단계의 상태 (완료/스킵/실패)
- 게이트에서의 사용자 선택 패턴

### 2. 패턴 분석

여러 세션의 추적 데이터를 비교하여:
- 자주 스킵되는 단계 → 불필요하거나 개선 필요
- 반복 실패 단계 → 스킬 품질 문제 또는 요구사항 불명확
- 자주 사용되는 조합 → 워크플로우 최적화 기회

### 3. 튜닝 제안

분석 결과 기반:
- "X 단계가 최근 5회 연속 스킵됨 → Minimal 깊이에서 기본 스킵 설정 검토"
- "Y 스킬에서 평균 2회 리뷰 루프 → 프롬프트 개선 검토"

## 산출물

`devflow-docs/tracking/session-{YYYY-MM-DD}.md`

## 데이터 소스

- `devflow-docs/audit.md` (1차 소스 — 중복 저장 안 함)
- `devflow-docs/devflow-state.md` (현재 상태 참조)

## 사용법

- 세션 종료 시 또는 사용자 요청 시 실행
- 자동 실행 없음 (사용자가 `/aidlc-superpowers-tracking` 호출)
```

- [ ] **Step 2: 커밋**

```bash
git add skills/aidlc-superpowers-tracking/
git commit -m "feat: aidlc-superpowers-tracking 스킬 추가 (devflow 포팅)"
```

---

## Chunk 5: 오케스트레이터 업데이트 + 검증 + README

### Task 12: 오케스트레이터 routing table 업데이트

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md`

- [ ] **Step 1: `aidlc-using-devflow/SKILL.md` 읽기**

CONSTRUCTION 라우팅 섹션 확인.

- [ ] **Step 2: functional-design 분기 추가**

CONSTRUCTION Stage Routing Table에서 `application-design → code-generation` 사이에 조건부 분기 추가:

```
application-design 완료 →
  [Comprehensive 깊이?] → aidlc-functional-design → aidlc-code-generation
  [Minimal/Standard?] → aidlc-code-generation (skip)
```

- [ ] **Step 3: 신규 스킬 참조 추가**

오케스트레이터의 Auxiliary Routing 또는 스킬 목록에 신규 user-invocable 스킬 언급:
- `aidlc-brainstorming` — 설계 전 협업
- `aidlc-writing-plans` — 구현 계획 작성
- `aidlc-test-driven-development` — TDD 강제
- `aidlc-subagent-driven-development` — 서브에이전트 실행
- `aidlc-executing-plans` — 배치 실행

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-using-devflow/SKILL.md
git commit -m "feat: 오케스트레이터에 functional-design 라우팅 + 신규 스킬 참조 추가"
```

---

### Task 13: superpowers 참조 검증 + 잔여 교체

**Files:**
- Potentially modify: 여러 스킬 파일

- [ ] **Step 1: 잔여 superpowers 참조 검색**

```bash
grep -r "superpowers" skills/ _shared/ --include="*.md"
```

- [ ] **Step 2: 잔여 참조가 있으면 교체**

`superpowers:스킬명` → `aidlc-스킬명`으로 교체.
`superpowers` 플러그인 일반 언급(설명 텍스트)은 컨텍스트에 따라 판단.

- [ ] **Step 3: plugin.json 확인**

```bash
cat .claude-plugin/plugin.json | grep -i superpowers
```

superpowers 관련 필드가 있으면 제거.

- [ ] **Step 4: 최종 검증**

```bash
grep -r "superpowers:" skills/ skills/_shared/ --include="*.md"
```

결과 0건 확인.

- [ ] **Step 5: 변경사항 있으면 커밋**

```bash
git add -A
git commit -m "fix: 잔여 superpowers 참조 제거 — 완전 자립 달성"
```

---

### Task 14: README.md 업데이트

**Files:**
- Modify: `README.md`

- [ ] **Step 1: README 읽기**

- [ ] **Step 2: 스킬 목록 업데이트**

신규 7개 스킬 추가:

| 스킬 | 역할 |
|------|------|
| `aidlc-brainstorming` | 아이디어를 설계 문서로 전환 (HARD-GATE) |
| `aidlc-writing-plans` | 설계 문서를 태스크별 구현 계획으로 변환 |
| `aidlc-test-driven-development` | TDD Iron Law 강제 (Rigid) |
| `aidlc-subagent-driven-development` | 서브에이전트 기반 계획 실행 + 2단계 리뷰 |
| `aidlc-executing-plans` | 배치 기반 계획 실행 + 세션 재개 |
| `aidlc-functional-design` | CONSTRUCTION 상세 기능 설계 (조건부) |
| `aidlc-superpowers-tracking` | 세션 스킬 사용 추적 + 워크플로우 인사이트 |

- [ ] **Step 3: 워크플로우 다이어그램에 functional-design 추가**

CONSTRUCTION 섹션에 functional-design 단계 추가 (조건부).

- [ ] **Step 4: 스킬 수 업데이트**

19개 → 26개. 총 풋프린트 업데이트.

- [ ] **Step 5: superpowers 의존 관련 문구 제거/수정**

"superpowers에 위임" 관련 문구 → "자체 내장"으로 수정.

- [ ] **Step 6: 공유 규약 문서 섹션에 patterns/ 추가**

```markdown
| `_shared/patterns/three-mode-selection.md` | Together/Import/Skip 모드 선택 패턴 |
| `_shared/patterns/hold-mechanism.md` | Mid-step Hold 시그널 + Resume 규약 |
| `_shared/patterns/brownfield-exploration.md` | 기존 코드베이스 탐색 프로토콜 |
```

- [ ] **Step 7: 커밋**

```bash
git add README.md
git commit -m "docs: README 현행화 — 26개 스킬, superpowers 완전 독립"
```

---

## 최종 검증

모든 태스크 완료 후:

1. `grep -r "superpowers:" skills/ skills/_shared/` → **0건**
2. 신규 스킬 7개 존재 확인: `ls skills/aidlc-{brainstorming,writing-plans,test-driven-development,executing-plans,subagent-driven-development,functional-design,superpowers-tracking}/SKILL.md`
3. shared patterns 3개 존재 확인: `ls skills/_shared/patterns/`
4. 리뷰어 프롬프트 3개 추가 확인: `ls skills/_shared/reviewers/`
5. conventions.md에 3개 규약 추가 확인
6. tdd-protocol.md에 합리화 방지 테이블 확인
