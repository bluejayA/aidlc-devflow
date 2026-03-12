# Review Sub-agent Framework + Token Optimization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AIDLC 오케스트레이터를 3단 위임 체인으로 분리하고, 리뷰 서브에이전트 프레임워크를 도입하여 토큰 효율 ~60% 개선

**Complexity:** Comprehensive

**Architecture:** 현재 549줄 단일 오케스트레이터를 Entry(~80줄) + INCEPTION Phase(~180줄) + CONSTRUCTION Phase(~200줄)로 분리. 리뷰어 프롬프트 3개를 `_shared/reviewers/`에 추가하고, 리뷰 대상 스킬 6개에 Review 섹션(~15줄)을 추가. 게이트 패턴을 `_shared/gate-patterns.md`로 템플릿화. `devflow-conventions.md`를 아키텍처 가이드로 확장.

**Tech Stack:** Markdown (SKILL.md prompt files), JSON (plugin.json)

**Spec:** `docs/plans/2026-03-12-review-framework-token-optimization-design.md`

**검증 방법:** 이 프로젝트는 코드가 아닌 SKILL.md 마크다운 프롬프트 파일 변경이므로, TDD 대신 grep 기반 키워드 검증을 사용한다.

---

## Chunk 1: 공통 인프라 (gate-patterns, reviewers, conventions)

### Task 1: `_shared/gate-patterns.md` 생성

**Files:**
- Create: `skills/_shared/gate-patterns.md`

- [ ] **Step 1: 파일 생성**

```markdown
# Gate Patterns

<!-- 게이트 작성 규약. Phase 오케스트레이터가 게이트 정의 시 이 패턴명을 참조한다. -->

## 표준 게이트 (Standard Gate)

스킬 반환 후 사용자 확인이 필요할 때 사용.

```
[스킬 결과 요약 표시]
A) 변경 요청 → 스킬 재호출
B) 승인, 다음 단계 진행 → 다음 스테이지
```

## 조건부 게이트 (Conditional Gate)

스킬 반환값의 특정 패턴에 따라 선택지가 달라질 때 사용.

```
[패턴 매칭: 반환값에서 조건 추출]
조건 충족 시: 확장된 선택지 (A/B/C)
조건 미충족 시: 표준 게이트 (A/B)
```

## 리뷰 연계 게이트 (Review-Aware Gate)

Standard 이상 depth에서 리뷰 서브에이전트 결과를 포함하는 게이트.
스킬이 리뷰까지 완료한 뒤 반환하므로, 게이트에서는 리뷰 결과만 표시.

```
[스킬이 리뷰 완료 후 반환]
[리뷰 결과 요약 표시]
A) 리뷰 이슈 수정 요청 → 스킬 재호출
B) 승인, 다음 단계 진행
```
```

- [ ] **Step 2: 검증**

Run: `grep -c "표준 게이트\|조건부 게이트\|리뷰 연계 게이트" skills/_shared/gate-patterns.md`
Expected: 3

- [ ] **Step 3: 커밋**

```bash
git add skills/_shared/gate-patterns.md
git commit -m "feat: 게이트 패턴 규약 파일 추가 (_shared/gate-patterns.md)"
```

---

### Task 2: `_shared/reviewers/artifact-reviewer-prompt.md` 생성

**Files:**
- Create: `skills/_shared/reviewers/artifact-reviewer-prompt.md`

- [ ] **Step 1: 디렉토리 생성 + 파일 작성**

```bash
mkdir -p skills/_shared/reviewers
```

```markdown
# Artifact Reviewer

<!-- INCEPTION 산출물 공통 리뷰어. 리뷰 대상 스킬이 서브에이전트로 dispatch한다. -->

## 역할

산출물(requirements.md, workflow-plan.md, application-design.md, units.md)이 완전하고 일관되며 구현에 필요한 정보를 빠짐없이 담고 있는지 검증한다.

**핵심 원칙**: "작성자의 보고를 믿지 마세요." 산출물을 직접 읽고 검증한다.

## 입력

리뷰 대상 스킬이 다음 정보를 전달한다:
- `산출물 경로`: 리뷰할 파일 (예: `devflow-docs/inception/requirements.md`)
- `상위 산출물 경로`: 참조할 선행 산출물 (있으면)

## 체크리스트

| 항목 | 확인 내용 |
|------|----------|
| **완전성** | TODO, TBD, placeholder, 미완성 섹션 없음 |
| **일관성** | 내부 모순 없음, 용어 일관, 상위 산출물과 충돌 없음 |
| **명확성** | 모호한 요구사항 없음, 해석의 여지가 없는 표현 |
| **YAGNI** | 요청 범위를 벗어난 내용 없음 |
| **구조** | 필수 섹션 존재, 형식 준수 |

## 주의

- 산출물을 직접 Read하여 내용 확인 (요약이나 보고 의존 금지)
- 상위 산출물이 있으면 교차 검증 (예: requirements.md의 요구사항이 application-design.md에 반영되었는지)

## 출력 형식

```
## Artifact Review

**대상**: [파일 경로]
**Status:** ✅ Approved | ❌ Issues Found

**Issues (있으면):**
- [섹션]: [구체적 이슈] — [왜 문제인지]

**Recommendations (권고, 승인 차단 아님):**
- [제안 사항]
```
```

- [ ] **Step 2: 검증**

Run: `grep -c "완전성\|일관성\|명확성\|YAGNI" skills/_shared/reviewers/artifact-reviewer-prompt.md`
Expected: 4

- [ ] **Step 3: 커밋**

```bash
git add skills/_shared/reviewers/artifact-reviewer-prompt.md
git commit -m "feat: INCEPTION 산출물 리뷰어 프롬프트 추가"
```

---

### Task 3: `_shared/reviewers/code-plan-reviewer-prompt.md` 생성

**Files:**
- Create: `skills/_shared/reviewers/code-plan-reviewer-prompt.md`

- [ ] **Step 1: 파일 작성**

```markdown
# Code Plan Reviewer

<!-- 코드 계획(code-plan.md) 리뷰어. aidlc-code-generation이 Plan 완료 후 서브에이전트로 dispatch한다. -->

## 역할

코드 계획이 설계 산출물과 일치하고, 태스크 분해가 적절하며, 구현에 필요한 정보가 완전한지 검증한다.

**핵심 원칙**: "작성자의 보고를 믿지 마세요." code-plan.md를 직접 읽고, 설계 산출물과 대조한다.

## 입력

- `code-plan 경로`: `devflow-docs/construction/[unit-name]/code-plan.md`
- `설계 산출물 경로`: `devflow-docs/inception/requirements.md`, `devflow-docs/inception/application-design.md` (있으면)

## 체크리스트

| 항목 | 확인 내용 |
|------|----------|
| **완전성** | TODO, placeholder, 미완성 단계 없음 |
| **스펙 정합성** | 설계 요구사항 누락 없음, scope creep 없음 |
| **태스크 분해** | 각 단계가 atomic하고 실행 가능 |
| **파일 구조** | 파일 경로 명확, 단일 책임, 과도한 크기 아님 |
| **검증 단계** | 각 태스크에 검증 방법 포함 |

## 출력 형식

```
## Code Plan Review

**대상**: [code-plan 경로]
**Status:** ✅ Approved | ❌ Issues Found

**Issues (있으면):**
- [Task N, Step M]: [구체적 이슈] — [왜 문제인지]

**Recommendations (권고):**
- [제안 사항]
```
```

- [ ] **Step 2: 검증**

Run: `grep -c "스펙 정합성\|태스크 분해\|파일 구조" skills/_shared/reviewers/code-plan-reviewer-prompt.md`
Expected: 3

- [ ] **Step 3: 커밋**

```bash
git add skills/_shared/reviewers/code-plan-reviewer-prompt.md
git commit -m "feat: 코드 계획 리뷰어 프롬프트 추가"
```

---

### Task 4: `_shared/reviewers/code-reviewer-prompt.md` 생성

**Files:**
- Create: `skills/_shared/reviewers/code-reviewer-prompt.md`

- [ ] **Step 1: 파일 작성**

```markdown
# Code Reviewer

<!-- 구현 코드 리뷰어 (Spec Compliance + Code Quality 2단계 통합). aidlc-code-generation이 Generate 완료 후 서브에이전트로 dispatch한다. -->

## 역할

구현된 코드가 (1) 요구사항을 정확히 충족하고, (2) 품질 기준을 만족하는지 2단계로 검증한다.

**핵심 원칙**: "Implementer의 보고를 믿지 마세요." 실제 코드를 직접 읽고 검증한다.

## 입력

- `변경 파일 목록`: 구현된 소스 파일 경로들
- `code-plan 경로`: `devflow-docs/construction/[unit-name]/code-plan.md`
- `설계 산출물 경로`: `devflow-docs/inception/requirements.md` 등

## Stage 1: Spec Compliance (먼저 실행)

요청된 것을 정확히 만들었는지 확인. 더 이상도 덜도 아님.

| 확인 항목 | 설명 |
|----------|------|
| **Missing** | code-plan의 요구사항 중 구현되지 않은 것 |
| **Extra** | code-plan에 없는데 추가된 기능 |
| **Misunderstood** | 요구사항을 잘못 해석한 구현 |

**하지 말 것**: 보고서만 믿기, 완성 주장 수용, 요구사항 해석 수용
**반드시 할 것**: 실제 코드 읽기, 요구사항과 line-by-line 비교

## Stage 2: Code Quality (Stage 1 통과 후)

구현이 잘 만들어졌는지 확인.

| 항목 | 확인 내용 |
|------|----------|
| **테스트** | 테스트가 실제 로직을 검증하는가 (mock 남용 아닌가) |
| **에러 핸들링** | 적절한 에러 처리 |
| **보안** | OWASP Top 10 기준 취약점 없음 |
| **DRY** | 불필요한 중복 없음 |
| **구조** | 파일 단일 책임, 이해 가능한 크기 |

## 이슈 분류

- **Critical (Must Fix)**: 버그, 보안 취약점, 데이터 손실 위험
- **Important (Should Fix)**: 아키텍처 문제, 테스트 부족, 에러 처리 미흡
- **Minor (Nice to Have)**: 코드 스타일, 최적화, 문서화

## 출력 형식

```
## Code Review

**대상**: [변경 파일 목록]

### Stage 1: Spec Compliance
**Status:** ✅ Spec Compliant | ❌ Issues Found
- [Missing/Extra/Misunderstood]: [구체적 내용, file:line 참조]

### Stage 2: Code Quality
**Status:** ✅ Approved | ❌ Issues Found

#### Strengths
[잘한 점]

#### Issues
**Critical:** [있으면]
**Important:** [있으면]
**Minor:** [있으면]

### Assessment
**Ready to proceed?** [Yes / With fixes / No]
**Reasoning:** [기술적 판단]
```
```

- [ ] **Step 2: 검증**

Run: `grep -c "Spec Compliance\|Code Quality\|Critical.*Must Fix\|Important.*Should Fix" skills/_shared/reviewers/code-reviewer-prompt.md`
Expected: 4

- [ ] **Step 3: 커밋**

```bash
git add skills/_shared/reviewers/code-reviewer-prompt.md
git commit -m "feat: 구현 코드 리뷰어 프롬프트 추가 (spec+quality 통합)"
```

---

### Task 5: `_shared/devflow-conventions.md` 확장

**Files:**
- Modify: `skills/_shared/devflow-conventions.md` (39줄 → ~80줄)

- [ ] **Step 1: 기존 내용 읽기**

Read: `skills/_shared/devflow-conventions.md`

- [ ] **Step 2: 파일 전체 재작성**

기존 파일의 YAML frontmatter(`---` 블록)를 보존한다. 본문만 아래 내용으로 전체 교체:

```markdown
# devflow Conventions

<!-- AIDLC 플러그인 아키텍처 가이드 + 스킬 작성 규약 -->

## 아키텍처 개요

AIDLC는 **3단 위임 체인** 구조를 사용한다. 슈퍼에이전트(하나가 모든 것을 처리)가 아닌 경량 위임 구조:

- **Entry Orchestrator** (`aidlc-using-devflow`): Phase 라우터. New/Resume 판별 + Phase 전환만 처리
- **Phase Orchestrator** (`aidlc-inception-orchestrator`, `aidlc-construction-orchestrator`): 스테이지 순서 + 게이트 관리. 실제 작업은 하지 않음
- **Stage Skill**: 실제 작업 수행 + 리뷰 dispatch (해당 시)
- **Review Sub-agent**: 산출물 검증만 (스킬이 dispatch)

각 계층은 자기 역할만 하고 빠진다. 이를 통해 현재 Phase에 필요한 컨텍스트만 로드하여 토큰 효율을 확보한다.

## YAML 메타데이터 규약

### invoke_mode

- `orchestrator-only`: **상위 오케스트레이터만** 호출 가능. 사용자 직접 호출 불가.
  - Phase Orchestrator → Entry Orchestrator만 호출
  - Stage Skill → Phase Orchestrator만 호출
- `user-invocable`: 사용자가 직접 호출 가능

### return_behavior

- `stop-no-gate`: 실행 완료 후 결과 표시하고 STOP. 승인 게이트는 상위 오케스트레이터가 소유.
- `stop-with-gate`: 스킬 내부에서 사용자 승인을 받고 STOP (예외적 사용)

## 게이트 패턴 규약

Phase 오케스트레이터가 사용하는 게이트 패턴은 `_shared/gate-patterns.md`에 정의:
- **표준 게이트**: A) 변경 요청 / B) 승인
- **조건부 게이트**: 반환값 패턴에 따라 선택지 분기
- **리뷰 연계 게이트**: 리뷰 결과를 포함하는 게이트

## 리뷰 규약

### Depth 정책
- **Minimal**: 리뷰 스킵
- **Standard / Comprehensive**: 리뷰 서브에이전트 dispatch

### 리뷰 루프
1. `_shared/reviewers/[type]-prompt.md` 읽기
2. 서브에이전트 dispatch (산출물 경로 전달)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회)
5. 5회 초과 시 사용자 escalate

### 리뷰어 프롬프트
- `_shared/reviewers/artifact-reviewer-prompt.md` — INCEPTION 산출물
- `_shared/reviewers/code-plan-reviewer-prompt.md` — 코드 계획
- `_shared/reviewers/code-reviewer-prompt.md` — 구현 코드 (Spec + Quality 통합)

### Escalation 메시지 형식
```
⚠️ 리뷰 루프 5회 초과 — 사용자 판단 필요

리뷰 이력:
- 1회: [이슈 요약]
- ...

A) 현재 상태로 승인
B) 직접 수정 지시
```

## Return to Orchestrator 규약

모든 `orchestrator-only` 스킬은 실행 완료 후 아래 형식으로 반환:

```
[stage-name 결과]
- [핵심 결과 항목들]
- 산출물: [path]
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

STOP 후 게이트는 상위 오케스트레이터가 처리한다.

## 산출물 미발견 시 공통 처리

입력 산출물 파일이 없으면:
- "⚠️ [파일명]을 찾을 수 없습니다" 표시
- 사용 가능한 컨텍스트만으로 진행
- 산출물에 누락 사실 기록

## 새 스킬 추가 가이드

1. **frontmatter 필수 필드**: name, description, metadata (version, author, category, invoke_mode, return_behavior)
2. **리뷰 대상 스킬이면**: `## Review (Standard 이상)` 섹션 추가. 리뷰 규약의 리뷰 루프 패턴 참조
3. **Phase Orchestrator에 등록**: 해당 Phase 오케스트레이터의 스테이지 순회 + 게이트 매핑에 추가
4. **plugin.json**: skills 디렉토리에 자동 인식 (별도 등록 불필요)
```

- [ ] **Step 3: 검증**

Run: `grep -c "3단 위임 체인\|표준 게이트\|리뷰 규약\|Return to Orchestrator 규약\|새 스킬 추가 가이드" skills/_shared/devflow-conventions.md`
Expected: 5

- [ ] **Step 4: 커밋**

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "feat: devflow-conventions.md 아키텍처 가이드로 확장"
```

---

## Chunk 2: 오케스트레이터 분리

### Task 6: Entry Orchestrator 재작성 (`aidlc-using-devflow/SKILL.md`)

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md` (549줄 → ~80줄)

- [ ] **Step 1: 현재 파일 읽기**

Read: `skills/aidlc-using-devflow/SKILL.md`

- [ ] **Step 2: 전체 재작성**

기존 549줄을 ~100줄 Entry Orchestrator로 교체. INCEPTION/CONSTRUCTION 게이트와 라우팅 테이블은 Phase Orchestrator로 이동. 기존 오케스트레이터의 Resume Flow A/B gate, state archive, Error Handling, Troubleshooting, auxiliary skill 라우팅을 보존.

```markdown
---
name: aidlc-using-devflow
description: AIDLC Entry Orchestrator. Phase 라우팅 + devflow-state 초기화. 사용자가 호출하는 유일한 진입점.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
---

# aidlc-using-devflow

<!-- Entry Orchestrator: Phase 라우터. 3단 위임 체인의 최상위 -->
<!-- 아키텍처 참조: skills/_shared/devflow-conventions.md -->

## Trigger

사용자가 아래 중 하나를 요청하면 이 워크플로우를 시작한다:
- 새 기능 개발, 버그 수정, 리팩토링 등 구현 작업
- "devflow", "aidlc", "워크플로우" 언급
- 코드 변경이 필요한 모든 요청

## On Activation

### Step 1: 기존 세션 확인

`devflow-docs/devflow-state.md`가 존재하는지 확인한다.

**존재하지 않으면 → New Flow**
**존재하면 → Resume Flow**

### New Flow

1. 환영 메시지 표시:
   ```
   ## aidlc 워크플로우 시작

   AI-DLC 기반 개발 워크플로우가 활성화되었습니다.

   진행 단계:
   🔵 INCEPTION  → 무엇을 만들지 결정
   🟢 CONSTRUCTION → 어떻게 만들지 결정
   ```
2. `devflow-docs/` 디렉토리 생성 (하위 `inception/`, `construction/` 포함)
3. `devflow-docs/devflow-state.md` 초기화:
   ```markdown
   # DevFlow State

   ## Current Phase
   INCEPTION

   ## Current Stage
   (pending)

   ## Complexity
   (pending)

   ## Selected Approach
   (pending)
   ```
4. devflow-audit에 로깅: "New aidlc session started" + 사용자 원래 요청
5. `aidlc-inception-orchestrator` 호출

### Resume Flow

1. `devflow-docs/devflow-state.md` 읽기
2. 재개 게이트 제시:
   ```
   ## aidlc — 진행 중인 작업 발견

   현재 단계: [Current Phase] > [Current Stage]
   완료된 스테이지: [list]

   A) 이전 작업 재개
   B) 새 작업 시작 (기존 상태 초기화)
   ```
3. A 선택 시:
   - devflow-audit에 로깅: "Session resumed at [stage]"
   - `## Current Phase` 확인하여 해당 Phase Orchestrator 호출:
     - `INCEPTION` → `aidlc-inception-orchestrator` 호출
     - `CONSTRUCTION` → `aidlc-construction-orchestrator` 호출
4. B 선택 시:
   - 기존 state를 `devflow-state-archived-[timestamp].md`로 이름 변경
   - New Flow 진행

## Phase 전환

### INCEPTION 완료 시

`aidlc-inception-orchestrator`가 INCEPTION 완료를 반환하면:
1. devflow-state의 `## Current Phase`를 `CONSTRUCTION`으로 업데이트
2. `aidlc-construction-orchestrator` 호출

### CONSTRUCTION 완료 시

`aidlc-construction-orchestrator`가 CONSTRUCTION 완료를 반환하면:
1. devflow-state의 `## Current Phase`를 `complete`로 업데이트
2. devflow-audit에 로깅: "Construction phase complete"
3. 완료 안내:
   ```
   🎉 INCEPTION + CONSTRUCTION 완료

   산출물:
   - devflow-docs/inception/ (요구사항, 설계, 워크플로우 계획)
   - devflow-docs/construction/ (코드 계획, 빌드/테스트 지침)

   다음 단계:
   → aidlc-finishing-a-development-branch로 머지/PR 진행
   ```

## Auxiliary Skill 라우팅

CONSTRUCTION 도중 사용자가 아래 상황을 보고하면 해당 스킬로 안내한다:

### 버그/테스트 실패 시
`aidlc-systematic-debugging` 스킬을 호출하도록 안내한다.
근본 원인 파악 없이 즉흥적으로 코드를 수정하지 않는다.

### 완료 주장 시
`aidlc-verification-before-completion` 스킬을 호출하여 실제 명령 실행 결과로 완료를 검증한다.

### 개발 브랜치 완료 후
`aidlc-finishing-a-development-branch` 스킬을 호출하여 병합/PR/유지/폐기 선택지를 제시한다.

## Error Handling

### devflow-docs/ directory missing
`devflow-docs/`가 없으면 디렉토리를 생성하고 새 세션으로 시작한다.

### Stage artifact missing at resume
재개 시 기대하는 산출물이 없으면:
1. "⚠️ [stage-name] 산출물을 찾을 수 없습니다: [file-path]" 표시
2. A) 이전 단계부터 재실행 / B) 현재 단계 그대로 진행

### devflow-state.md 손상
상태 파일 파싱 불가 시:
1. `devflow-state-backup-[timestamp].md`로 백업
2. 새 세션 시작 (기존 산출물은 그대로 활용)

### Stage skill 호출 실패
스킬이 예상치 못한 결과를 반환하면:
A) 해당 단계 재시도 / B) 단계 스킵 (devflow-state에 skipped 기록)
```

- [ ] **Step 3: 검증**

Run: `grep -c "Entry Orchestrator\|aidlc-inception-orchestrator\|aidlc-construction-orchestrator\|Phase 전환" skills/aidlc-using-devflow/SKILL.md`
Expected: 4 이상

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-using-devflow/SKILL.md
git commit -m "refactor: Entry Orchestrator로 축소 (549줄 → ~80줄, Phase 라우팅만)"
```

---

### Task 7: INCEPTION Orchestrator 생성

**Files:**
- Create: `skills/aidlc-inception-orchestrator/SKILL.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p skills/aidlc-inception-orchestrator
```

- [ ] **Step 2: 파일 작성**

현재 `aidlc-using-devflow/SKILL.md`의 INCEPTION 관련 게이트(lines 143-237)와 라우팅(lines 339-358)을 기반으로 작성. 게이트는 `gate-patterns.md` 템플릿명 + 매개변수 형식으로 축약.

```markdown
---
name: aidlc-inception-orchestrator
description: INCEPTION Phase 오케스트레이터. 스테이지 순회 + 게이트 관리. Entry Orchestrator가 호출.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# aidlc-inception-orchestrator

<!-- INCEPTION Phase 오케스트레이터: 스테이지 순서 + 게이트 관리 -->
<!-- 게이트 패턴 참조: _shared/gate-patterns.md -->

## INCEPTION 스테이지 순서

```
workspace-detection → [Complexity Gate] → requirements-analysis → [Open Questions Gate]
  → workflow-planning → [Approach Proposal Gate] → application-design (조건부) → 완료
```

## The Orchestration Loop

아래 순서대로 스테이지를 순회한다. 각 스테이지에서:

### Step A: 스킬 호출

devflow-state의 `## Current Stage`를 업데이트하고 해당 스킬을 호출한다.
호출 시 필요한 파라미터는 인라인으로 전달한다:
- Complexity: `"Complexity: [level]"`
- Depth: `"Depth: [level]"`

### Step B: 결과 표시 + 로깅

스킬 반환값을 사용자에게 표시하고, devflow-audit에 기록한다.

### Step C: 게이트 제시

아래 게이트 정의에 따라 사용자에게 선택지를 제시한다.

### Step D: 라우팅

사용자 선택에 따라 다음 스테이지를 결정한다.

---

## 게이트 정의

### 1. workspace-detection 게이트 [조건부 게이트]

스킬 반환값에서 Greenfield/Brownfield 확인.

**Greenfield 경로:**
```
[workspace-detection 결과 표시]
A) 경로 수정 → workspace-detection 재호출
B) 확인, 다음 단계 진행 → Complexity Declaration Gate
```

**Brownfield 경로:**
```
[workspace-detection 결과 표시]
A) 분석 범위 수정 → workspace-detection 재호출
B) 확인, 다음 단계 진행 → Complexity Declaration Gate
```

### 2. Complexity Declaration Gate

workspace-detection 결과를 기반으로 복잡도를 선언.

```
이 작업의 복잡도를 **[Minimal/Standard/Comprehensive]**로 판단했습니다.
이유: [한 줄 이유]

다르게 조정하시겠습니까?

A) 조정 요청 → 사용자 입력 받아 반영
B) 승인 → devflow-state의 ## Complexity 업데이트 → requirements-analysis 호출
```

Complexity 값을 requirements-analysis 호출 시 인라인으로 전달: `"Complexity: [level]"`

### 3. requirements-analysis 게이트 [조건부 게이트]

패턴: `열린 질문: [N]개`

**패턴 매칭 실패 시**: LLM이 "없음", "0개", 다른 표현을 사용한 경우 N=0으로 처리하고 표준 gate 진행.

**N > 0인 경우:**
```
[requirements-analysis 결과 표시]
A) 미해결 질문 처리 → aidlc-requirements-analysis: QUESTIONS 재호출
B) 현재 가정으로 유지하고 다음 단계로 진행
C) 변경 요청 → requirements-analysis 재호출
```

A) 선택 시: `"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"` 인라인 신호로 재호출 → 반환 → `열린 질문: [N]개` 패턴 재확인

**N == 0이고 가정 있음:**
```
[requirements-analysis 결과 표시]
가정으로 처리된 항목이 있습니다: [목록]
A) 가정 수정 → requirements-analysis 재호출
B) 가정 승인, 다음 단계 진행
```

**N == 0이고 가정 없음:**
```
[requirements-analysis 결과 표시]
A) 변경 요청 → requirements-analysis 재호출
B) 승인, 다음 단계 진행
```

### 4. workflow-planning 게이트 [2단계 게이트]

**1단계: 접근법 선택**
```
[workflow-planning 결과 표시]
[생성된 접근법 2-3개 표시]

A) [A안명] 선택
B) [B안명] 선택
C) [C안명] 선택 (Comprehensive만)
D) 변경 요청 → workflow-planning 재호출
```

선택 후:
- devflow-state의 `## Selected Approach` 업데이트
- workflow-plan.md의 `**Selected Approach**` 업데이트
- `## Approved Stages`를 선택된 접근법 기준으로 업데이트

**2단계: 개발 환경 설정**
```
개발 환경을 설정합니다.

A) 변경 요청 → workflow-planning 재호출
B) Git worktree로 격리 개발 (main 브랜치 보호) → aidlc-using-git-worktrees 호출
C) 현재 브랜치에서 바로 시작
```

### 워크트리 결과 게이트

workflow-planning 승인 후, 개발 환경 설정 게이트에서 B (Git Worktree) 선택 시:

`aidlc-using-git-worktrees` 호출 → 결과 게이트:
```
## aidlc-using-git-worktrees 완료

[스킬 반환 결과 표시]

A) 브랜치 이름 변경 요청 (스킬 재실행)
B) 이 워크트리에서 진행
⚠️ 베이스라인 테스트 실패 시: C) aidlc-systematic-debugging 먼저 / B) 실패 인지 후 진행
```

### INCEPTION → CONSTRUCTION 라우팅

workflow-plan.md의 `## Approved Stages`를 읽어 분기:
- `application-design: included` → application-design 게이트 실행
- `application-design: skipped`, `units-generation: included` → INCEPTION 완료, CONSTRUCTION에서 units-generation부터 시작
- `application-design: skipped`, `units-generation: skipped` → INCEPTION 완료, CONSTRUCTION에서 code-generation 직행

### 5. application-design 게이트 (조건부 실행)

`application-design: included`인 경우에만 실행.

#### 5a. LIST 게이트 [표준 게이트]

```
[application-design LIST 결과 표시]
A) 변경 요청 → application-design 재호출
B) [depth에 따라 조건부 표시]
   - Minimal: 승인, INCEPTION 완료 → INCEPTION 완료
   - Standard/Comprehensive: 승인, 상세 설계 진행 → application-design: DETAIL 호출
```

#### 5b. DETAIL 게이트 [표준 게이트] (Standard/Comprehensive만)

```
[application-design DETAIL 결과 표시]
A) 변경 요청 → application-design: DETAIL 재호출
B) 승인, INCEPTION 완료
```

---

## Error Handling

### Stage skill 호출 실패
스킬이 예상치 못한 결과를 반환하면:
A) 해당 단계 재시도 / B) 단계 스킵 (devflow-state에 skipped 기록)

### workflow-plan.md의 included/skipped 값 파싱 실패
`workflow-plan.md` 라우팅 키 형식이 예상과 다르면:
1. 파일 직접 확인 후 형식 수정
2. 기본값: application-design included, units-generation skipped

### Stage skill이 직접 gate를 제시하는 경우
스킬이 오케스트레이터 역할을 침범하면:
1. "이 게이트는 무시하고 B를 선택해주세요" 안내
2. 오케스트레이터가 정상 게이팅 처리

## INCEPTION 완료

모든 INCEPTION 스테이지 완료 시:

```
[INCEPTION 완료]
- 완료된 스테이지: [목록]
- 산출물: devflow-docs/inception/
```

→ Return to Entry Orchestrator (Phase 전환)
```

- [ ] **Step 3: 검증**

Run: `grep -c "Complexity Declaration\|Approach Proposal\|Open Questions\|application-design 게이트\|INCEPTION 완료" skills/aidlc-inception-orchestrator/SKILL.md`
Expected: 5

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-inception-orchestrator/SKILL.md
git commit -m "feat: INCEPTION Phase 오케스트레이터 추가"
```

---

### Task 8: CONSTRUCTION Orchestrator 생성

**Files:**
- Create: `skills/aidlc-construction-orchestrator/SKILL.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p skills/aidlc-construction-orchestrator
```

- [ ] **Step 2: 파일 작성**

현재 `aidlc-using-devflow/SKILL.md`의 CONSTRUCTION 관련 라우팅(lines 376-398)과 Multi-unit 핸들링을 기반으로 작성.

```markdown
---
name: aidlc-construction-orchestrator
description: CONSTRUCTION Phase 오케스트레이터. 스테이지 순회 + 게이트 관리 + Multi-unit 핸들링. Entry Orchestrator가 호출.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# aidlc-construction-orchestrator

<!-- CONSTRUCTION Phase 오케스트레이터: 코드 생성 + 빌드/테스트 관리 -->
<!-- 게이트 패턴 참조: _shared/gate-patterns.md -->
<!-- 리뷰 정책: Standard 이상에서 리뷰 서브에이전트 dispatch (스킬 내부에서 처리) -->

## CONSTRUCTION 스테이지 순서

```
units-generation (조건부) → [units 게이트]
  → code-generation Plan → [code-plan 게이트]
  → code-generation Generate → [구현 게이트]
  → (multi-unit이면 다음 unit으로 반복)
  → build-and-test → [완료 게이트]
```

## On Activation

### Step 1: 컨텍스트 로드

다음 파일을 읽는다:
- `devflow-docs/devflow-state.md` — Complexity, Completed Units 확인
- `devflow-docs/inception/workflow-plan.md` — Approved Stages, Stage Depths 확인

### Step 2: 스테이지 결정

`workflow-plan.md`의 `## Approved Stages`에서:
- `units-generation: included` → units-generation부터 시작
- `units-generation: skipped` → code-generation으로 바로 진행

## The Orchestration Loop

### 1. units-generation (조건부)

**실행 조건**: `workflow-plan.md`에서 `units-generation: included`인 경우

스킬 호출 → 결과 표시

#### units 게이트 [표준 게이트]
```
[units-generation 결과 표시]
A) 변경 요청 → units-generation 재호출
B) 승인, 코드 생성 진행
```

승인 후: devflow-state에 unit 목록 기록

### 2. code-generation (Multi-unit 핸들링)

`devflow-docs/inception/units.md`에서 구현 순서를 읽는다.
units-generation이 스킵된 경우, 단일 unit으로 처리한다.

**각 unit에 대해 아래를 반복:**

#### 2a. code-generation Plan 호출

`aidlc-code-generation` 호출 (unit명 + Complexity 인라인 전달: `"Complexity: [level]"`)


#### code-plan 게이트 [리뷰 연계 게이트]
```
[code-generation Plan 결과 표시]
[리뷰 결과 표시 (Standard 이상)]
A) 변경 요청 → code-generation 재호출
B) 승인, 코드 생성 진행 → code-generation: GENERATE 호출
```

#### 2b. code-generation Generate 호출

`"aidlc-code-generation: GENERATE — proceed with the approved plan for [unit-name]"` 인라인 신호로 호출

#### 구현 게이트 [리뷰 연계 게이트]
```
[code-generation 완료 결과 표시]
[리뷰 결과 표시 (Standard 이상)]
A) 수정 요청 → code-generation: GENERATE 재호출
B) 승인, 다음 unit 진행
```

승인 후: devflow-state의 `## Completed Units`에 unit명 추가

#### 2c. 다음 unit 확인

미완료 unit이 있으면 → 2a로 돌아가 다음 unit 처리
모든 unit 완료 시 → build-and-test로 진행

### 3. build-and-test

`aidlc-build-and-test` 호출

#### 완료 게이트 [표준 게이트]
```
[build-and-test 결과 표시]
A) 수정 요청 → build-and-test 재호출
B) 승인, CONSTRUCTION 완료
```

## Audit Logging

각 게이트 결정 시 devflow-audit에 기록:
- 스테이지명, 타임스탬프, 사용자 선택 (A/B/C), 리뷰 결과 (있으면)

## Error Handling

### units.md 미발견 시 (Multi-unit 라우팅)
`devflow-docs/inception/units.md`가 없으면:
1. "⚠️ units.md를 찾을 수 없습니다. 단일 unit으로 진행합니다." 표시
2. 단일 unit으로 code-generation 진행

### Stage skill 호출 실패
스킬이 예상치 못한 결과를 반환하면:
A) 해당 단계 재시도 / B) 단계 스킵 (devflow-state에 skipped 기록)

### Stage skill이 직접 gate를 제시하는 경우
"이 게이트는 무시하고 B를 선택해주세요" 안내 후 오케스트레이터가 정상 게이팅 처리

## CONSTRUCTION 완료

```
[CONSTRUCTION 완료]
- 완료된 unit: [목록]
- 산출물: devflow-docs/construction/
```

→ Return to Entry Orchestrator
```

- [ ] **Step 3: 검증**

Run: `grep -c "Multi-unit\|code-plan 게이트\|구현 게이트\|완료 게이트\|CONSTRUCTION 완료" skills/aidlc-construction-orchestrator/SKILL.md`
Expected: 5

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-construction-orchestrator/SKILL.md
git commit -m "feat: CONSTRUCTION Phase 오케스트레이터 추가"
```

---

## Chunk 3: 스킬 업데이트 (Review 섹션 추가 + Return 표준화)

### Task 9: aidlc-requirements-analysis 업데이트

**Files:**
- Modify: `skills/aidlc-requirements-analysis/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

Read: `skills/aidlc-requirements-analysis/SKILL.md`

- [ ] **Step 2: Return to Orchestrator 섹션 교체 (lines 192-205)**

현재:
```markdown
## Return to Orchestrator

STOP here. No approval gate — orchestrator handles it.

```
[requirements-analysis 결과]
...
```
```

교체:
```markdown
## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/requirements.md`
   - 상위 산출물: `devflow-docs/inception/workspace.md` (있으면)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

## Return to Orchestrator

STOP.

```
[requirements-analysis 결과]
- 분석 깊이: [Minimal | Standard | Comprehensive]
- 해석 확정: [확정된 해석 한 줄 요약, 또는 "단일 해석 — 확인 불필요"]
- 기능 요구사항: [count]개
- 열린 질문: [count]개
- 가정으로 처리된 항목: [0개 | N개 — 항목명 목록]
- 산출물: devflow-docs/inception/requirements.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```
```

- [ ] **Step 3: Common Issues 간소화 (lines 207-223)**

스킬 고유 이슈만 남기고, "workspace.md not found"는 `devflow-conventions.md`의 공통 처리로 대체:

```markdown
## Common Issues

### User provides no requirements context
요청이 너무 모호하면:
- Comprehensive depth 기본 적용
- Step 2에서 가능한 해석 제시

### Step 2에서 해석이 3가지 이상으로 늘어날 때
- 가장 가능성 높은 2-3가지로 압축
- 나머지는 "기타: 다른 방향이라면 직접 설명해주세요"로 열어두기
```

- [ ] **Step 4: 검증**

Run: `grep -c "Review (Standard 이상)\|artifact-reviewer-prompt\|리뷰: \[" skills/aidlc-requirements-analysis/SKILL.md`
Expected: 3

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-requirements-analysis/SKILL.md
git commit -m "feat(requirements-analysis): Review 섹션 추가 + Return 표준화"
```

---

### Task 10: aidlc-workflow-planning 업데이트

**Files:**
- Modify: `skills/aidlc-workflow-planning/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

Read: `skills/aidlc-workflow-planning/SKILL.md`

- [ ] **Step 2: Return to Orchestrator 섹션 교체 (lines 112-122)**

교체:
```markdown
## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/workflow-plan.md`
   - 상위 산출물: `devflow-docs/inception/requirements.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

## Return to Orchestrator

STOP.

```
[workflow-planning 결과]
- 생성된 접근법: [A안명] / [B안명] / ([C안명])
- 권장 접근법: [A안 | B안 | C안]
- 접근법 상세: (Step 2의 접근법 목록 참조)
- 산출물: devflow-docs/inception/workflow-plan.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```
```

- [ ] **Step 3: Common Issues 간소화 (lines 124-136)**

"requirements.md or workspace.md not found" 대신 스킬 고유 이슈만:

```markdown
## Common Issues

### No clear indication of new components needed
application-design 포함 여부가 모호하면:
- 기본적으로 포함
- workflow plan에 모호성 기록
```

- [ ] **Step 4: 검증**

Run: `grep -c "Review (Standard 이상)\|artifact-reviewer-prompt\|리뷰: \[" skills/aidlc-workflow-planning/SKILL.md`
Expected: 3

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-workflow-planning/SKILL.md
git commit -m "feat(workflow-planning): Review 섹션 추가 + Return 표준화"
```

---

### Task 11: aidlc-application-design 업데이트

**Files:**
- Modify: `skills/aidlc-application-design/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

Read: `skills/aidlc-application-design/SKILL.md`

- [ ] **Step 2: Return to Orchestrator 섹션 교체 (lines 120-139)**

교체:
```markdown
## Review (Standard 이상)

depth가 Standard 이상이면 (LIST/DETAIL 모드 공통):
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/application-design.md`
   - 상위 산출물: `devflow-docs/inception/requirements.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

## Return to Orchestrator

STOP.

**LIST Mode 반환:**
```
[application-design 결과 — LIST]
- 설계된 컴포넌트: [count]개
- 목록: [컴포넌트명 나열]
- 산출물: devflow-docs/inception/application-design.md (목록 단계)
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

**DETAIL Mode 반환:**
```
[application-design 결과 — DETAIL]
- 상세 설계 완료: [count]개 컴포넌트
- 산출물: devflow-docs/inception/application-design.md (업데이트됨)
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```
```

- [ ] **Step 3: Common Issues 간소화 (lines 141-152)**

"requirements.md not found" 제거, 스킬 고유 이슈만:

```markdown
## Common Issues

### No clear component boundaries
시스템이 단일 컴포넌트로 충분하면:
- 단일 컴포넌트로 설계
- "Single-component system — no decomposition needed" 기록
```

- [ ] **Step 4: 검증**

Run: `grep -c "Review (Standard 이상)\|artifact-reviewer-prompt\|리뷰: \[" skills/aidlc-application-design/SKILL.md`
Expected: 3 이상

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-application-design/SKILL.md
git commit -m "feat(application-design): Review 섹션 추가 + Return 표준화"
```

---

### Task 12: aidlc-units-generation 업데이트

**Files:**
- Modify: `skills/aidlc-units-generation/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

Read: `skills/aidlc-units-generation/SKILL.md`

- [ ] **Step 2: Return to Orchestrator 섹션 교체 (lines 51-60)**

교체:
```markdown
## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/units.md`
   - 상위 산출물: `devflow-docs/inception/application-design.md` (있으면), `devflow-docs/inception/requirements.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

## Return to Orchestrator

STOP.

```
[units-generation 결과]
- 생성된 단위: [count]개
- 구현 순서: [unit1] → [unit2] → ...
- 산출물: devflow-docs/inception/units.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```
```

- [ ] **Step 3: Common Issues 간소화 (lines 62-73)**

"application-design.md not found" 제거, 스킬 고유 이슈만:

```markdown
## Common Issues

### Only one logical unit identified
분해 결과 단일 unit이면:
- units.md에 1개 unit으로 작성
- 오케스트레이터가 single-unit code-generation으로 처리
```

- [ ] **Step 4: 검증**

Run: `grep -c "Review (Standard 이상)\|artifact-reviewer-prompt\|리뷰: \[" skills/aidlc-units-generation/SKILL.md`
Expected: 3

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-units-generation/SKILL.md
git commit -m "feat(units-generation): Review 섹션 추가 + Return 표준화"
```

---

### Task 13: aidlc-code-generation 업데이트

**Files:**
- Modify: `skills/aidlc-code-generation/SKILL.md`

- [ ] **Step 1: 현재 파일 읽기**

Read: `skills/aidlc-code-generation/SKILL.md`

- [ ] **Step 2: Return to Orchestrator 섹션 교체 (lines 110-127)**

code-generation은 PART 1(Plan)과 PART 2(Generate)에서 **다른 리뷰어**를 사용:

교체:
```markdown
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
```

- [ ] **Step 3: 검증**

Run: `grep -c "code-plan-reviewer-prompt\|code-reviewer-prompt\|리뷰: \[" skills/aidlc-code-generation/SKILL.md`
Expected: 4

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-code-generation/SKILL.md
git commit -m "feat(code-generation): Review 섹션 추가 (Plan→code-plan-reviewer, Generate→code-reviewer)"
```

---

## Chunk 4: 마무리 (plugin.json + 스모크 테스트)

### Task 14: plugin.json 버전 업데이트

**Files:**
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: 버전 업데이트**

`"version": "0.3.0"` → `"version": "0.4.0"`

- [ ] **Step 2: 검증**

Run: `grep "0.4.0" .claude-plugin/plugin.json`
Expected: `"version": "0.4.0"`

- [ ] **Step 3: 커밋**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: 플러그인 버전 0.3.0 → 0.4.0"
```

---

### Task 15: 전체 스모크 테스트

모든 파일이 올바르게 생성/수정되었는지 확인.

- [ ] **Step 1: 신규 파일 존재 확인**

```bash
ls -la skills/_shared/gate-patterns.md skills/_shared/reviewers/artifact-reviewer-prompt.md skills/_shared/reviewers/code-plan-reviewer-prompt.md skills/_shared/reviewers/code-reviewer-prompt.md skills/aidlc-inception-orchestrator/SKILL.md skills/aidlc-construction-orchestrator/SKILL.md
```
Expected: 6개 파일 모두 존재

- [ ] **Step 2: Entry Orchestrator 축소 확인**

```bash
wc -l skills/aidlc-using-devflow/SKILL.md
```
Expected: ~80줄 (549줄에서 대폭 축소)

- [ ] **Step 3: 리뷰 섹션 추가 확인 (리뷰 대상 스킬 5개)**

```bash
grep -l "Review (Standard 이상)" skills/aidlc-requirements-analysis/SKILL.md skills/aidlc-workflow-planning/SKILL.md skills/aidlc-application-design/SKILL.md skills/aidlc-units-generation/SKILL.md skills/aidlc-code-generation/SKILL.md
```
Expected: 5개 파일 모두 매칭

- [ ] **Step 4: 리뷰어 참조 확인**

```bash
grep -r "artifact-reviewer-prompt" skills/aidlc-*/SKILL.md | wc -l
```
Expected: 4 (requirements, workflow, application-design, units)

```bash
grep -r "code-plan-reviewer-prompt\|code-reviewer-prompt" skills/aidlc-code-generation/SKILL.md | wc -l
```
Expected: 2

- [ ] **Step 5: 3단 위임 체인 확인**

```bash
grep "aidlc-inception-orchestrator\|aidlc-construction-orchestrator" skills/aidlc-using-devflow/SKILL.md | wc -l
```
Expected: 2 이상 (Entry가 Phase Orchestrator를 참조)

- [ ] **Step 6: devflow-conventions.md 확장 확인**

```bash
wc -l skills/_shared/devflow-conventions.md
```
Expected: ~80줄 (39줄에서 확장)

- [ ] **Step 7: Error Handling 존재 확인**

```bash
grep -l "Error Handling" skills/aidlc-using-devflow/SKILL.md skills/aidlc-inception-orchestrator/SKILL.md skills/aidlc-construction-orchestrator/SKILL.md
```
Expected: 3개 파일 모두 매칭

- [ ] **Step 8: Auxiliary skill 참조 확인**

```bash
grep -c "aidlc-systematic-debugging\|aidlc-verification-before-completion\|aidlc-finishing-a-development-branch" skills/aidlc-using-devflow/SKILL.md
```
Expected: 3 이상

- [ ] **Step 9: Resume Flow A/B gate 확인**

```bash
grep "이전 작업 재개\|새 작업 시작" skills/aidlc-using-devflow/SKILL.md
```
Expected: 2줄 매칭

- [ ] **Step 10: CONSTRUCTION Orchestrator audit logging 확인**

```bash
grep "devflow-audit\|Audit Logging" skills/aidlc-construction-orchestrator/SKILL.md
```
Expected: 1줄 이상 매칭

- [ ] **Step 11: 시나리오 워크스루**

전체 흐름이 문서상 연결되는지 수동 확인:
```
시나리오: Standard depth, application-design 포함, 2 units

1. 사용자 → aidlc-using-devflow (Entry)
2. Entry → New Flow → devflow-state 초기화 → aidlc-inception-orchestrator 호출
3. INCEPTION Orchestrator:
   a. workspace-detection → workspace-detection 게이트
   b. Complexity Declaration Gate → "Standard" 선언
   c. requirements-analysis (Complexity: Standard) → Review dispatch → Open Questions 게이트
   d. workflow-planning → Review dispatch → Approach Proposal 2단계 게이트
   e. application-design LIST → Review dispatch → LIST 게이트 → DETAIL 호출
   f. application-design DETAIL → Review dispatch → DETAIL 게이트
   g. INCEPTION 완료 반환
4. Entry → Phase 전환 → aidlc-construction-orchestrator 호출
5. CONSTRUCTION Orchestrator:
   a. units-generation → Review dispatch → units 게이트
   b. Unit 1: code-generation Plan → Review (code-plan) → code-plan 게이트
   c. Unit 1: code-generation Generate → Review (code) → 구현 게이트
   d. Unit 2: code-generation Plan → Review (code-plan) → code-plan 게이트
   e. Unit 2: code-generation Generate → Review (code) → 구현 게이트
   f. build-and-test → 완료 게이트
   g. CONSTRUCTION 완료 반환
6. Entry → 완료 안내
```
