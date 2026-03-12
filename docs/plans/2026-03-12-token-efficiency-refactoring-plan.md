# 토큰 효율화 리팩토링 구현 계획

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AIDLC 스킬 파일 전체 줄 수 20% 감소 (4,216 → ≤3,373) + 혼동 지점 12개 해소

**Complexity:** Standard

**Architecture:** `devflow-conventions.md`에 공통 패턴(Return Format, Review Workflow, Complexity/Depth, 용어)을 SSOT로 추가한 뒤, 18개 스킬 파일에서 중복 섹션을 conventions 참조로 대체한다.

**Tech Stack:** Markdown (프롬프트 파일)

**현재 줄 수 기준선:**
```
conventions.md:           114줄
inception-orchestrator:   293줄
workspace-detection:       92줄
requirements-analysis:    228줄
user-stories:             112줄
nfr-requirements:         181줄
workflow-planning:        158줄
application-design:       194줄
units-generation:          80줄
code-generation:          175줄
build-and-test:           123줄
systematic-debugging:     285줄
verification-before-completion: 273줄
finishing-a-development-branch: 329줄
receiving-code-review:    267줄
dispatching-parallel-agents: 278줄
writing-skills:           276줄
using-git-worktrees:      194줄
총합 (shared 포함):      4,216줄
```

---

## Task 1: conventions.md 확장 (SSOT 먼저)

**Files:**
- Modify: `skills/_shared/devflow-conventions.md`

- [ ] **Step 1: 현재 파일 읽기**

`skills/_shared/devflow-conventions.md` 전체를 읽고 기존 구조를 파악한다.

- [ ] **Step 2: 5개 섹션 추가**

파일 끝에 다음 섹션들을 추가한다:

**2a. Return to Orchestrator 표준 형식:**
```markdown
## Return to Orchestrator 표준 형식

모든 stage skill은 실행 완료 후 아래 형식으로 반환한다:

    STOP.
    [{skill-name} 결과]
    - {필드1}: {값}
    - ...

- 각 스킬의 SKILL.md에는 반환 필드 목록만 정의한다.
- return_behavior가 stop-no-gate인 스킬은 게이트를 제시하지 않는다.
```

**2b. Review Workflow:**
```markdown
## Review Workflow (Standard 이상)

depth가 Standard 이상이면:
1. 해당 reviewer prompt 읽기 (artifact/code-plan/code-reviewer)
2. 리뷰 서브에이전트 dispatch (산출물 경로 전달)
3. Approved → Return to Orchestrator
4. Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator.
depth 확인: devflow-state.md의 `## Complexity` 필드.
```

**2c. Complexity와 Stage Depth:**
```markdown
## Complexity와 Stage Depth

- **Complexity**: 프로젝트 전체 복잡도. INCEPTION 초기에 선언 (Minimal/Standard/Comprehensive).
- **Stage Depth**: 개별 스테이지 실행 깊이. workflow-planning에서 Stage별로 결정.
- **기본 규칙**: Stage Depth는 Complexity를 따르되, workflow-planning이 override 가능.
- **전달 방식**: 오케스트레이터가 스킬 호출 시 인라인 텍스트로 depth를 전달.
  스킬은 호출 텍스트의 depth를 우선 사용하고, 없으면 devflow-state.md에서 읽는다.
```

**2d. 용어:**
```markdown
## 용어

| 용어 | 정의 |
|------|------|
| **unit** | 독립적으로 구현·테스트 가능한 개발 단위. story(사용자 가치)나 component(아키텍처 단위)와 다름. 구현 순서와 병렬성을 결정하기 위한 분해 단위. |
| **Orchestrator-Centric** | 오케스트레이터가 게이트·상태·라우팅을 소유하고, stage skill은 순수 실행자인 아키텍처. |
| **Pre-Planning** | requirements-analysis와 workflow-planning 사이의 조건부 단계 (user-stories, nfr-requirements). |
| **depth** | 개별 스테이지의 실행 깊이 (Minimal/Standard/Comprehensive). Complexity와 구분. |
```

**2e. invoke_mode 보완:**
기존 YAML 메타데이터 규약 테이블의 `user-invocable` 행 설명을 보완:
- 현재: `사용자 직접 호출 가능`
- 변경: `사용자가 직접 호출 가능. 오케스트레이터 워크플로우 외부에서 독립적으로 사용`

- [ ] **Step 3: 버전 업데이트**

conventions.md의 version을 v0.3.0 → v0.4.0으로 업데이트.

- [ ] **Step 4: 줄 수 확인**

```bash
wc -l skills/_shared/devflow-conventions.md
```
예상: ~175줄 (114 + ~61줄 추가)

- [ ] **Step 5: 커밋**

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "refactor: conventions.md에 공통 패턴 추가 (Return/Review/Depth/용어)"
```

---

## Task 2: inception-orchestrator 혼동 해소

**Files:**
- Modify: `skills/aidlc-inception-orchestrator/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

- [ ] **Step 2: 3가지 혼동 해소**

**2a. Approved Stages 업데이트 책임 명시:**
Gate 7 (workflow-planning 결과 게이트) 섹션에서 사용자 접근법 선택 후 처리에 추가:
```markdown
사용자가 접근법을 선택하면:
1. workflow-plan.md의 **Selected Approach** 필드 업데이트 ← 오케스트레이터
2. workflow-plan.md의 ## Approved Stages를 선택된 접근법 기준으로 재작성 ← 오케스트레이터
3. devflow-state.md 업데이트 ← 오케스트레이터
```

**2b. Pre-Planning Gate 명칭 변경:**
`### 4. Pre-Planning Gate [조건부 게이트]` → `### 4. Pre-Planning 분기 [자동분기 + 조건부 게이트]`
설명에 추가: "Minimal/Comprehensive는 자동 분기, Standard만 사용자 게이트"

**2c. "(B안)" 표기 제거:**
description에서 "(B안)" 제거.

- [ ] **Step 3: 줄 수 확인**

```bash
wc -l skills/aidlc-inception-orchestrator/SKILL.md
```
예상: ~295줄 (소폭 증가 — 책임 명시 추가)

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-inception-orchestrator/SKILL.md
git commit -m "refactor: inception-orchestrator 혼동 해소 (Approved Stages/Pre-Planning/B안)"
```

---

## Task 3: INCEPTION stage skill 중복 제거 (6개 파일)

**Files:**
- Modify: `skills/aidlc-workspace-detection/SKILL.md`
- Modify: `skills/aidlc-requirements-analysis/SKILL.md`
- Modify: `skills/aidlc-user-stories/SKILL.md`
- Modify: `skills/aidlc-nfr-requirements/SKILL.md`
- Modify: `skills/aidlc-workflow-planning/SKILL.md`
- Modify: `skills/aidlc-units-generation/SKILL.md`

- [ ] **Step 1: 6개 파일 읽기**

- [ ] **Step 2: 각 파일에서 중복 제거**

각 파일에 대해 동일한 패턴을 적용:

**Return to Orchestrator 축약:**
기존 "STOP." + 형식 설명 + 필드 목록 (10~15줄) → conventions 참조 + 필드만 (3~4줄):
```markdown
## Return to Orchestrator
conventions 표준 형식. 반환 필드:
- {필드}: [설명]
```

**Review 섹션 축약** (해당 스킬만):
기존 전체 리뷰 프로세스 (12~15줄) → conventions 참조 (3줄):
```markdown
## Review
conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/{artifact}.md
- 리뷰어: artifact-reviewer-prompt.md
```

**"(B안)" 제거:**
metadata description에서 "(B안)" 제거.

**workspace-detection 추가 축약:**
- Common Issues 섹션의 과도한 시나리오 설명 축약 (각 시나리오 3줄 → 1줄)

**스킬별 예상 절감:**

| 스킬 | 현재 | 예상 | 절감 |
|------|------|------|------|
| workspace-detection | 92 | ~65 | -27 |
| requirements-analysis | 228 | ~200 | -28 |
| user-stories | 112 | ~90 | -22 |
| nfr-requirements | 181 | ~160 | -21 |
| workflow-planning | 158 | ~140 | -18 |
| units-generation | 80 | ~65 | -15 |

- [ ] **Step 3: 줄 수 확인**

각 파일의 줄 수를 확인하여 예상 범위 내인지 검증.

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-workspace-detection skills/aidlc-requirements-analysis skills/aidlc-user-stories skills/aidlc-nfr-requirements skills/aidlc-workflow-planning skills/aidlc-units-generation
git commit -m "refactor: INCEPTION stage skills 중복 제거 (Return/Review/B안)"
```

---

## Task 4: application-design NFR 판단 로직 제거 + 중복 제거

**Files:**
- Modify: `skills/aidlc-application-design/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

- [ ] **Step 2: 3가지 변경 적용**

**2a. NFR Design 판단 로직 제거:**
3가지 활성화 조건 체크 로직을 제거하고 수신 로직만 유지:
```markdown
## Step 5: NFR Design Patterns
오케스트레이터가 "NFR Design 포함" 신호를 전달한 경우에만 실행.
활성화 조건 판단은 오케스트레이터 소유 (오케스트레이터 중심 원칙).
```

**2b. Return + Review 축약:** Task 3과 동일 패턴.

**2c. "(B안)" 제거.**

- [ ] **Step 3: 줄 수 확인**

예상: 194 → ~165줄

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-application-design/SKILL.md
git commit -m "refactor: application-design NFR 판단 단일화 + 중복 제거"
```

---

## Task 5: CONSTRUCTION stage skill 중복 제거 (3개 파일)

**Files:**
- Modify: `skills/aidlc-code-generation/SKILL.md`
- Modify: `skills/aidlc-build-and-test/SKILL.md`
- Modify: `skills/aidlc-using-git-worktrees/SKILL.md`

- [ ] **Step 1: 3개 파일 읽기**

- [ ] **Step 2: 각 파일에서 중복 제거**

**code-generation:**
- Return + Review 축약
- TDD 개요 설명 제거 → `_shared/tdd-protocol.md` 참조 1줄로 대체. 2단계 Plan→Generate 고유 흐름만 유지
- 예시 2개를 각 10줄로 축약 (핵심 흐름만)
- "(B안)" 제거

**build-and-test:**
- Return 축약
- "(B안)" 제거

**using-git-worktrees:**
- "(B안)" 제거만

**예상 절감:**

| 스킬 | 현재 | 예상 | 절감 |
|------|------|------|------|
| code-generation | 175 | ~130 | -45 |
| build-and-test | 123 | ~115 | -8 |
| using-git-worktrees | 194 | ~193 | -1 |

- [ ] **Step 3: 줄 수 확인**

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-code-generation skills/aidlc-build-and-test skills/aidlc-using-git-worktrees
git commit -m "refactor: CONSTRUCTION stage skills 중복 제거 (TDD/Return/B안)"
```

---

## Task 6: 개발 품질 도구 스킬 정리 (5개 파일)

**Files:**
- Modify: `skills/aidlc-systematic-debugging/SKILL.md`
- Modify: `skills/aidlc-verification-before-completion/SKILL.md`
- Modify: `skills/aidlc-finishing-a-development-branch/SKILL.md`
- Modify: `skills/aidlc-receiving-code-review/SKILL.md`
- Modify: `skills/aidlc-dispatching-parallel-agents/SKILL.md`

- [ ] **Step 1: 5개 파일 읽기**

- [ ] **Step 2: 각 파일 수정**

**systematic-debugging (285줄 → ~220줄 목표):**
- `invoke_mode: user-invocable` metadata 추가
- TDD RED 설명 제거 → `tdd-protocol.md` 참조. 4단계 디버깅 프로세스만 유지
- 합리화 방지 테이블: 핵심 3행만 유지 (6행 → 3행)
- Example 2개를 각 8줄로 축약
- "(B안)" 제거

**verification-before-completion (273줄 → ~215줄 목표):**
- `invoke_mode: user-invocable` metadata 추가
- Self-Review 체크리스트 중복 제거 → `tdd-protocol.md` 참조. 6단계 검증 프로세스만 유지
- 합리화 방지 테이블: 핵심 3행만 유지
- Example 3개 → 2개로 줄이고 각 10줄로 축약
- "(B안)" 제거

**finishing-a-development-branch (329줄 → ~325줄 목표):**
- `invoke_mode: user-invocable` metadata 추가
- "(B안)" 제거

**receiving-code-review (267줄 → ~263줄 목표):**
- `invoke_mode: user-invocable` metadata 추가
- "(B안)" 제거

**dispatching-parallel-agents (278줄 → ~265줄 목표):**
- 병렬화 금지 테이블 축약 (핵심 항목만)
- "(B안)" 제거

- [ ] **Step 3: 줄 수 확인**

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-systematic-debugging skills/aidlc-verification-before-completion skills/aidlc-finishing-a-development-branch skills/aidlc-receiving-code-review skills/aidlc-dispatching-parallel-agents
git commit -m "refactor: 개발 품질 도구 정리 (invoke_mode/TDD참조/예시축약/B안)"
```

---

## Task 7: writing-skills "(B안)" 제거 + 최종 검증

**Files:**
- Modify: `skills/aidlc-writing-skills/SKILL.md`

- [ ] **Step 1: "(B안)" 제거**

metadata description에서 "(B안)" 제거.

- [ ] **Step 2: 전체 줄 수 검증**

```bash
cd skills && find . -name "*.md" -not -path "./_utils/*" -not -path "./_shared/reviewers/*" | xargs cat | wc -l
```

목표: ≤3,373줄 (4,216의 80%)
참고: spec의 "~4,000 → 3,200" 기준은 shared 파일 제외. 여기서는 shared 포함 총합 기준으로 측정.

- [ ] **Step 3: 혼동 해소 12개 항목 체크리스트**

| # | 항목 | 확인 |
|---|------|------|
| 1 | invoke_mode 4개 스킬에 user-invocable 추가됨 | |
| 2 | Approved Stages 업데이트 책임 inception-orchestrator에 명시됨 | |
| 3 | NFR Design 판단 로직 application-design에서 제거됨 | |
| 4 | "B안" 정의가 conventions 용어에 있음 (→ "Orchestrator-Centric") | |
| 5 | Complexity vs Depth 관계 conventions에 명시됨 | |
| 6 | "unit" 정의 conventions에 있음 | |
| 7 | Pre-Planning Gate 명칭 "분기 + 조건부 게이트"로 변경됨 | |
| 8 | using-devflow 역할 — 변경 없음 확인 | |
| 9 | "(B안)" 표기 모든 스킬에서 제거됨 | |
| 10 | code-generation TDD 중복 → tdd-protocol 참조 | |
| 11 | systematic-debugging TDD 중복 → tdd-protocol 참조 | |
| 12 | verification-before-completion TDD 중복 → tdd-protocol 참조 | |

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-writing-skills/SKILL.md
git commit -m "refactor: writing-skills (B안) 제거 + 전체 검증 완료"
```
