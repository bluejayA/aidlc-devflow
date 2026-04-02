# Auto Mode Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** 초보자를 위한 완전 자동 devflow 모드를 단일 SKILL.md로 구현
**Complexity:** Comprehensive
**Architecture:** `aidlc-auto-mode/SKILL.md` 1개 파일을 생성한다. 기존 stage 스킬을 그대로 호출하고, devflow 호환 상태 파일을 유지한다. 기존 devflow SKILL.md는 무수정. 분리 시 파일 1개 삭제 + plugin.json 1줄 제거.
**Tech Stack:** SKILL.md (자연어 명세), Bash (Layer 1 검증 스크립트)
**Design Spec:** `docs/plans/2026-04-02-auto-mode-design.md`

---

### Task 1: 스킬 디렉토리 생성 + Frontmatter + 전체 골격

**Files:**
- Create: `skills/aidlc-auto-mode/SKILL.md`

- [ ] **Step 1: 디렉토리 및 파일 생성**

```markdown
---
name: aidlc-auto-mode
description: |
  초보자를 위한 완전 자동 devflow. greenfield 전용.
  요구사항 입력 → inception → construction → build-test를 자동 진행하며
  각 flow 종료 시 5개 에이전트 리뷰 필수.
  Use for fully automated devflow for beginners. Greenfield only.
  Triggers: "auto 모드", "자동 모드", "auto mode", "알아서 만들어줘"
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
---

# aidlc-auto-mode

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 초보자용 완전 자동 devflow. greenfield 전용. 단일 파일 자기 완결형. -->
<!-- 기존 devflow SKILL.md 무수정. stage 스킬 재활용. -->

## Trigger

"auto 모드", "자동 모드", "auto mode", "알아서 만들어줘" 키워드가 명시적으로 포함된 경우에만 활성화.
그 외 모든 개발 요청은 기존 `aidlc-using-devflow`로 라우팅.

## On Activation

[Task 2에서 작성]

## Phase 1: INCEPTION 자동 진행

[Task 3에서 작성]

## INCEPTION 리뷰 + 사용자 확인

[Task 4에서 작성]

## Phase 2: CONSTRUCTION 자동 진행

[Task 5에서 작성]

## State Management

[Task 6에서 작성]

## Error Handling

[Task 7에서 작성]

## Session Resume + Completion

[Task 8에서 작성]
```

- [ ] **Step 2: 줄 수 확인**
Run: `wc -l skills/aidlc-auto-mode/SKILL.md`
Expected: ~50줄 (골격)

- [ ] **Step 3: 커밋**
`feat: auto-mode 스킬 골격 생성`

---

### Task 2: On Activation — 진입 조건 + 세션 감지

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## On Activation` 섹션

- [ ] **Step 1: 진입 조건 작성**

`## On Activation` 섹션을 다음 내용으로 교체:

```markdown
## On Activation

### Step 1: 세션 감지

`devflow-docs/auto-decision-log-inception.md` 또는 `devflow-docs/auto-decision-log-construction.md` 존재 여부 확인.

**존재하면 → 재개 제안:**
```
이전에 자동 모드로 진행하던 작업이 있습니다.
진행 상황: [devflow-state.md에서 읽은 completed stages 수] 단계 완료
A) 이어서 진행하기
B) 처음부터 새로 시작하기
```

A → Session Resume (아래) 실행.
B → 기존 산출물을 `.archive/`로 이동 후 Step 2로.

**존재하지 않으면 → Step 2로.**

### Step 2: greenfield 확인

사용자 요구사항과 현재 디렉토리를 분석:
- 소스 코드 파일(`.py`, `.ts`, `.js`, `.go`, `.rs`, `.java`, `.kt`, `.swift` 등)이 존재하면 → brownfield.
- 설정 파일만 있거나(`.gitignore`, `CLAUDE.md`, `package.json` 초기 상태 등) 비어있으면 → greenfield.

**brownfield:**
```
auto 모드는 새 프로젝트(greenfield) 전용입니다.
기존 코드가 있는 프로젝트는 단계별 모드로 진행합니다.
→ aidlc-using-devflow로 전환합니다.
```

**greenfield → Step 3로.**

### Step 3: 재진입 확인 (첫 실행 아닌 경우)

`.archive/`에 이전 auto-mode 세션(`auto-decision-log-*.md`)이 존재하면:
```
이전에 auto 모드로 완료한 작업이 있습니다.
이번에도 auto 모드로 진행할까요?
A) 네, auto 모드로 진행
B) 아니오, 단계별 모드로 진행 → aidlc-using-devflow
```

A 또는 첫 실행 → Step 4로.

### Step 4: 초기화

1. `devflow-docs/` 디렉토리 생성 (하위 `inception/`, `construction/` 포함)
2. `devflow-state.md` 초기화:
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
3. `auto-decision-log-inception.md` 생성:
   ```markdown
   # Auto Decision Log — INCEPTION
   ```
4. 사용자에게 안내:
   ```
   auto 모드를 시작합니다.
   요구사항을 분석하고 설계한 뒤, 확인을 받고 코드를 생성합니다.
   ```
5. Phase 1 진행.
```

- [ ] **Step 2: 줄 수 확인**
Run: `wc -l skills/aidlc-auto-mode/SKILL.md`
Expected: ~120줄

- [ ] **Step 3: 커밋**
`feat: auto-mode 진입 조건 + 세션 감지 구현`

---

### Task 3: INCEPTION 자동 진행

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## Phase 1` 섹션

- [ ] **Step 1: INCEPTION 플로우 작성**

`## Phase 1` 섹션을 다음으로 교체:

```markdown
## Phase 1: INCEPTION 자동 진행

### 스테이지 순서

```
workspace-detection → complexity 자동 선언 → requirements-analysis
  → [고위험 가정 게이트] → (user-stories) → (nfr-requirements)
  → workflow-planning → (application-design)
```

각 스테이지에서 아래를 반복:

### Step A: 스테이지 시작

devflow-state의 `## Current Stage`를 `[stage-name] (in-progress)`로 기록.
사용자에게 진행 메시지 표시:

| 스테이지 | 메시지 |
|---------|--------|
| workspace-detection | "프로젝트 환경을 분석하고 있습니다..." |
| complexity | "프로젝트 규모를 판단하고 있습니다..." |
| requirements-analysis | "요구사항을 분석하고 있습니다..." |
| user-stories | "사용자 시나리오를 작성하고 있습니다..." |
| nfr-requirements | "성능/보안 기준을 설정하고 있습니다..." |
| workflow-planning | "구현 계획을 수립하고 있습니다..." |
| application-design | "시스템 구조를 설계하고 있습니다..." |

### Step B: 스킬 호출

인라인 신호로 stage 스킬을 호출:

| 스킬 | 인라인 신호 |
|------|-----------|
| workspace-detection | (직접 호출) |
| requirements-analysis | `"Complexity: [level]"` |
| requirements-analysis 재호출 | `"aidlc-requirements-analysis: UPDATE — [변경 내용]"` |
| user-stories | `"Complexity: [level]"` |
| nfr-requirements | `"Mode: GENERATE"`, `"Complexity: [level]"` |
| workflow-planning | `"Complexity: [level]"` |
| application-design LIST | `"Complexity: [level]"` |
| application-design DETAIL | `"aidlc-application-design: DETAIL"` (NFR 있으면 `"— NFR Design 포함"`) |

### Step C: 자동 판단 + Checkpoint

스킬 반환값을 자동 승인하고 Checkpoint 실행 (State Management 참조).
decision-log에 판단 상세 기록.

### 자동 판단 규칙

**Complexity 자동 선언** (workspace-detection 직후):

| 기준 | Minimal | Standard | Comprehensive |
|------|---------|----------|---------------|
| 예상 파일 수 | ~5개 이하 | 6-20개 | 20개 이상 |
| 서비스/컴포넌트 | 단일 | 2-3개 | 4개 이상 |
| DB | 불필요 | 단일 | 복수 또는 복잡 스키마 |
| 외부 연동 | 없음 | 1-2개 | 3개 이상 |

복수 기준이 다른 레벨 → 높은 쪽으로 선언. 각 기준별 근거를 decision-log 기록.

**기술 스택 자동 선택** (requirements-analysis 내):
1. CLAUDE.md에 명시된 기술 → 무조건 채택
2. 아키텍처 패턴 → `tech-stack-defaults.md` 매핑 참조
3. 미커버 계층 → `tech-stack-catalog.md`에서 "(권장)" 자동 선택
4. 모든 선택을 decision-log에 기록

**Pre-Planning 자동 결정:**
- Minimal → 스킵
- Standard → NFR만
- Comprehensive → 전체 (user-stories + NFR)

**Approach 자동 선택** (workflow-planning 직후):
- 첫 번째(권장) approach 자동 선택
- devflow-state `## Selected Approach` + `## Approved Stages` 업데이트
- workflow-plan.md `**Selected Approach**` 마킹

**SDD vs 인라인** (units-generation 직후):
- Minimal → 인라인 강제
- Standard/Comprehensive + unit 2개 이상 → SDD

### 고위험 가정 게이트

requirements-analysis 완료 후, 가정 목록에서 고위험 항목을 판별:
- 인증/보안 방식 관련
- 유료 외부 서비스 의존
- 데이터 모델 핵심 구조

**고위험 가정 1건 이상 → 미니 게이트:**
```
확인이 필요한 자동 판단이 있습니다:
1. [가정 내용] ([이유])
2. [가정 내용] ([이유])

A) 맞습니다, 계속 진행
B) 수정할 부분이 있습니다 → [번호 선택]
```

B → 수정 반영 후 requirements-analysis UPDATE 재호출.
고위험 가정 0건 → 자동 진행.
```

- [ ] **Step 2: 줄 수 확인**
Run: `wc -l skills/aidlc-auto-mode/SKILL.md`
Expected: ~230줄

- [ ] **Step 3: 커밋**
`feat: auto-mode INCEPTION 자동 진행 플로우 구현`

---

### Task 4: INCEPTION 리뷰 + 사용자 확인 게이트

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## INCEPTION 리뷰 + 사용자 확인` 섹션

- [ ] **Step 1: 리뷰 + 게이트 작성**

```markdown
## INCEPTION 리뷰 + 사용자 확인

### INCEPTION 리뷰 (필수)

모든 INCEPTION 스테이지 완료 후 실행.
사용자에게: "설계를 검토하고 있습니다... (5개 관점)"

5개 리뷰어를 병렬 dispatch (프롬프트 경로 확인됨):
1. spec-reviewer — `agents/spec-reviewer.md` (대상: requirements.md, user-stories.md)
2. code-reviewer — `agents/code-reviewer.md` (대상: application-design.md)
3. quality-reviewer — `agents/quality-reviewer.md` (대상: 전체 inception 산출물)
4. security-reviewer — `agents/security-reviewer.md` (대상: nfr-requirements.md, application-design.md)
5. maintainability-reviewer — `agents/maintainability-reviewer.md` (대상: application-design.md)

**결과 처리:**
- ALL PASS → 사용자 확인 게이트로.
- ISSUES Found → 순차 수정:
  수정 우선순위: security → spec → code → quality → maintainability
  수정 후 전체 5개 re-dispatch. 최대 3라운드.
- 3라운드 초과 → 사용자 에스컬레이션 (Error Handling 참조).

### 사용자 확인 게이트 (유일한 게이트)

일상 언어로 요약 + Claude 자율 판단 하이라이트:

```
## 설계가 완료되었습니다

만들려는 것: [사용자 요구사항 1줄 요약]
프로젝트 규모: [일상 언어] ([Complexity])
기술 스택: [주요 기술 나열]

## 자동으로 결정한 항목 (검토해 주세요)
[번호. 결정 내용 → 선택값 (이유: 판단 근거)]
...

설계 검토 결과: [N]개 관점 통과 [결과 요약]

상세 내용: devflow-docs/inception/ 에서 확인 가능

A) 수정할 부분이 있습니다
   [자동 결정 항목별 번호 선택지]
   N) 기타 (직접 입력)
B) 좋습니다, 코드 생성을 시작합니다
```

**A 선택 시:** 번호 선택 → 해당 항목의 대안 제시 → 수정 반영 → 해당 스테이지 재실행 → 리뷰 재실행 → 게이트 재표시.
**B 선택 시:** Phase 2 진행. devflow-state `## Current Phase`를 `CONSTRUCTION`으로 업데이트.
```

- [ ] **Step 2: 줄 수 확인**
Expected: ~280줄

- [ ] **Step 3: 커밋**
`feat: auto-mode INCEPTION 리뷰 + 사용자 확인 게이트 구현`

---

### Task 5: CONSTRUCTION 자동 진행 + 리뷰 + 완료

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## Phase 2` 섹션

- [ ] **Step 1: CONSTRUCTION 플로우 작성**

```markdown
## Phase 2: CONSTRUCTION 자동 진행

사용자에게: "코드 생성을 시작합니다."
`auto-decision-log-construction.md` 생성.

### 스테이지 순서

```
(units-generation) → per-unit: [(functional-design) → code-plan → code-gen]
  → build-and-test → [auto-fix 루프]
```

### 스테이지별 실행

**units-generation (조건부):**
workflow-plan.md `## Approved Stages`에서 `units-generation: included`이면 실행.
결과 자동 승인 + Checkpoint.

**SDD 자동 결정** (unit 2개 이상):
- Minimal → 인라인 강제
- Standard/Comprehensive → `aidlc-subagent-driven-development` 호출
  인라인 신호: `"SDD: units=[devflow-docs/inception/units.md], summary=[devflow-docs/session-summary.md], complexity=[level], functional-designs=[devflow-docs/inception/functional-design-*.md]"` (functional-design 없으면 해당 필드 생략)

**인라인 모드 (unit 1개 또는 Minimal):**
각 unit에 대해:
1. (functional-design) — Comprehensive만. `aidlc-functional-design` 호출 (unit명 전달).
   사용자에게: "[unit명] 상세 설계 중..."
2. code-generation Plan — `"Complexity: [level]"` + unit명.
   사용자에게: "[unit명] 구현 계획 작성 중..."
   결과 자동 승인 + Checkpoint.
3. code-generation Generate — `"aidlc-code-generation: GENERATE — proceed with the approved plan for [unit-name]"`
   사용자에게: "[unit명] 코드 생성 중..."
   결과 자동 승인 + Checkpoint.
   devflow-state `## Completed Units`에 unit명 추가.

**build-and-test:**
사용자에게: "빌드 및 테스트 실행 중..."
`aidlc-build-and-test` 호출.

auto-fix 루프 (테스트 실패, 린트 에러):
- `code-generation: GENERATE — auto-fix for [unit]: [에러 요약]` 재호출
- `aidlc-build-and-test` 재실행
- 최대 3회. 수정 후 전체 테스트 재실행 (regression 방지).
- 3회 소진 → 에스컬레이션 (Error Handling 참조).

빌드 실패, 환경 문제, auth/security 태그 unit → 즉시 에스컬레이션.

### CONSTRUCTION 리뷰 (필수)

사용자에게: "코드를 검토하고 있습니다... (5개 관점)"
`aidlc-requesting-code-review` R1 호출. 인라인 신호: `"Review: full-depth"`
R1이 4단계 리뷰 수행:
- Stage 1: `_shared/reviewers/spec-reviewer-prompt.md`
- Stage 2: `_shared/reviewers/code-quality-reviewer-prompt.md`
- Stage 3: `_shared/reviewers/security-reviewer-prompt.md`
- Stage 4: `_shared/reviewers/maintainability-reviewer-prompt.md`
(INCEPTION 5개 + CONSTRUCTION 4개 = 합산 5개 고유 관점 커버.
 INCEPTION의 code-reviewer가 code-quality를 포괄하므로 중복 없음)

- PASS → 최종 결과 표시.
- ISSUES → 순차 수정 (security → spec → code → quality → maintainability) 후 re-dispatch. 최대 3라운드.
- 3라운드 초과 → 에스컬레이션.

### 최종 결과물 + 실행 안내

```
프로젝트가 완성되었습니다!

생성된 파일: [N]개
테스트: [N]개 통과

→ 지금 바로 실행해볼까요?
A) 네, 실행 방법을 알려주세요
   → [빌드 시스템에서 감지한 실행 명령] + [접속 URL]
B) 나중에 실행하겠습니다
```

### 세션 체이닝

```
다음 작업도 auto 모드로 진행할까요?
A) 네, auto 모드로 계속
B) 아니오, 단계별 모드로 전환
C) 종료
```

A → devflow-state `finished` → `.archive/` 이동 (decision-log 포함) → 새 auto-mode 세션.
B → devflow-state `finished` → `.archive/` 이동 → using-devflow 안내.
C → devflow-state `finished` → 세션 종료.
```

- [ ] **Step 2: 줄 수 확인**
Expected: ~380줄

- [ ] **Step 3: 커밋**
`feat: auto-mode CONSTRUCTION 플로우 + 리뷰 + 완료 구현`

---

### Task 6: State Management

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## State Management` 섹션

- [ ] **Step 1: 상태 관리 작성**

```markdown
## State Management

### Checkpoint 블록 (매 스테이지 완료 시 반드시 실행)

**1단계 — 기록:** 다음 4개 파일을 순서대로 업데이트:
1. `devflow-state.md` — Current Stage 갱신 (in-progress 제거)
2. `session-summary.md` — Completed Work에 추가 (`_shared/patterns/session-continuity.md` 템플릿 준수)
3. `devflow-audit.md` — `[timestamp] [stage] — auto-approved — [이유 1줄]`
4. `auto-decision-log-[phase].md` — 판단 상세 append

**2단계 — 검증:** `devflow-state.md`를 Read로 열어 Current Stage 값 확인. 불일치 시 즉시 수정.

**3단계 — 진행 메시지:** 사용자에게 다음 스테이지 진행 메시지 표시.

### devflow-state.md 화이트리스트

auto 모드가 기록할 수 있는 필드 (이 목록 외 기록 금지):
- `## Current Phase` → INCEPTION | CONSTRUCTION | complete
- `## Current Stage` → 스테이지명 | 스테이지명 (in-progress)
- `## Complexity` → Minimal | Standard | Comprehensive
- `## Selected Approach` → 접근법명
- `## Approved Stages` → 스테이지 목록
- `## Completed Units` → unit 목록
- `## Active Unit` → 현재 unit
- `## Worktree` → branch, path (auto-mode v0.1에서는 worktree 미사용. 향후 확장 시 추가)

auto 전용 메타데이터(auto-fix 횟수, 리뷰 라운드 등)는 auto-decision-log에만 기록.

### decision-log 규칙

- **append-only**: 파일 끝에 추가만. 수정 금지.
- **감사 전용**: 실행 중 과거 결정 참조 → devflow-state.md만 읽는다. decision-log를 Read하지 않는다.
- **사후 검토용**: 사용자 명시 요청 시에만 읽는다.

### decision-log 포맷

```markdown
## [ISO-8601] [stage-name]
- decision: [결정 내용]
- reason: [판단 근거]
- alternatives_considered: [고려한 대안]
- assumptions: [가정 목록, 있으면]
```

리뷰 결과:
```markdown
## [ISO-8601] [phase]-review
- reviewers: [목록]
- results: [리뷰어별 verdict + issues]
- auto-fix-attempt: [N/3]
- fix-detail: [수정 내용]
- final: [ALL PASS | ESCALATE]
```
```

- [ ] **Step 2: 줄 수 확인**
Expected: ~430줄

- [ ] **Step 3: 커밋**
`feat: auto-mode 상태 관리 + checkpoint + decision-log 구현`

---

### Task 7: Error Handling

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## Error Handling` 섹션

- [ ] **Step 1: 에러 핸들링 작성**

```markdown
## Error Handling

### 글로벌 서킷 브레이커

phase당 총 리트라이 상한 (모든 유형 합산):
- INCEPTION: 최대 5회
- CONSTRUCTION: 최대 8회

상한 도달 시:
```
거의 완성되었지만 자동으로 해결하기 어려운 부분이 있습니다.
완료된 작업: [N]단계 중 [M]단계
A) 하나씩 확인하면서 진행하기 (단계별 모드)
B) 현재 상태 저장 후 나중에 이어하기
```
A → devflow-state 기록 후 using-devflow 안내. B → 상태 보존 후 종료.

### 스테이지 실행 상태 추적

시작: Current Stage = `[name] (in-progress)`. 완료 (Checkpoint): `(in-progress)` 제거.
재개 시 `(in-progress)` 발견 → 산출물 존재 확인 → 있으면 완료 처리, 없으면 재실행.

### 1. Stage 스킬 호출 실패

판정: 산출물 미생성, 기대 패턴 없음, 에러 반환.
→ 1회 자동 재시도 → 실패 시 에스컬레이션. 리트라이 카운터 +1.

### 2. 리뷰어 실패

2a. 타임아웃/파싱 에러: 실패 리뷰어 1회 재시도 → 응답 리뷰어만 판정 (최소 3/5).
    3개 미만 → 전체 재시도 1회 → 에스컬레이션.
2b. 자동수정 3라운드 초과: 에스컬레이션. 리트라이 카운터 +3.

### 3. build-and-test 실패

auto-fix 대상(테스트/린트): 최대 3회 + 전체 재실행.
스킵 대상(빌드/환경/auth): 즉시 에스컬레이션.
3회 소진: 에스컬레이션. 리트라이 카운터 +3.

### 4. greenfield 오판

requirements-analysis에서 기존 코드 참조 발견 시:
→ decision-log 경고 + 사용자 확인 게이트 하이라이트에 포함.

### 5. 고위험 가정 대량 거부

requirements-analysis만 수정된 가정으로 재실행 → 후속 자동 진행. 리트라이 카운터 +1.

### 에스컬레이션 메시지 원칙

- "문제/에러/실패" 대신 → "확인이 필요한 부분"
- "devflow 전환" 대신 → "하나씩 확인하면서 진행하기 (단계별 모드)"
- 항상 진행률: "[N]단계 중 [M]단계 완료"
- 기술 용어 → 괄호 부연 또는 생략
```

- [ ] **Step 2: 줄 수 확인**
Expected: ~480줄

- [ ] **Step 3: 커밋**
`feat: auto-mode 에러 핸들링 + 서킷 브레이커 구현`

---

### Task 8: Session Resume

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` — `## Session Resume + Completion` 섹션

- [ ] **Step 1: 세션 재개 작성**

```markdown
## Session Resume

On Activation Step 1에서 재개 선택(A) 시 실행:

1. `devflow-state.md` 읽기 — Current Phase, Current Stage 확인.
2. `session-summary.md` 읽기 — 완료 작업 맥락 복원.
3. **교차 검증**: Current Stage에 `(in-progress)` 포함 시:
   - 산출물 파일 존재 → 완료 처리 (Checkpoint 실행), 다음 스테이지로.
   - 산출물 미존재 → 해당 스테이지 처음부터 재실행.
4. Phase에 따라 해당 플로우 진입:
   - `INCEPTION` → Phase 1의 해당 스테이지부터 재개.
   - `CONSTRUCTION` → Phase 2의 해당 스테이지부터 재개.
5. decision-log에 `"session-resumed at [stage]"` 기록.
```

- [ ] **Step 2: 최종 줄 수 확인**
Run: `wc -l skills/aidlc-auto-mode/SKILL.md`
Expected: ≤500줄. 초과 시 분리 후보:
- decision-log 포맷 → `skills/aidlc-auto-mode/decision-log-format.md` (~30줄)
- 리뷰어 dispatch 상세 → `skills/aidlc-auto-mode/review-protocol.md` (~40줄)
분리 시 SKILL.md에서 1단계 참조만 허용.

- [ ] **Step 3: 커밋**
`feat: auto-mode 세션 재개 구현`

---

### Task 9: 스킬 리뷰 + 검증

**Files:**
- Modify: `skills/aidlc-auto-mode/SKILL.md` (리뷰 피드백 반영)

- [ ] **Step 1: 500줄 가이드라인 확인**
Run: `wc -l skills/aidlc-auto-mode/SKILL.md`
Expected: ≤ 500줄. 초과 시 분리 검토.

- [ ] **Step 2: skill-reviewer 실행**
`_shared/reviewers/skill-reviewer-prompt.md`를 서브에이전트로 dispatch.
대상: `skills/aidlc-auto-mode/SKILL.md`
참조 컨텍스트: 설계 문서 `docs/plans/2026-04-02-auto-mode-design.md`

- [ ] **Step 3: 리뷰 피드백 반영**
Issues Found → 수정 후 re-dispatch (최대 3회).
Recommendations → 반영 권장.

- [ ] **Step 4: 커밋**
`fix: auto-mode 스킬 리뷰 피드백 반영`

---

### Task 10: Layer 1 검증 스크립트

**Files:**
- Create: `skills/aidlc-auto-mode/verify.sh`

- [ ] **Step 1: 검증 스크립트 작성**

```bash
#!/bin/bash
# auto-mode Layer 1 검증 스크립트
# SKILL.md 수정 후 실행하여 구조적 정합성 확인

set -euo pipefail

SKILL="skills/aidlc-auto-mode/SKILL.md"
ERRORS=0

echo "=== auto-mode Layer 1 Verification ==="

# 1. 줄 수 확인
LINES=$(wc -l < "$SKILL")
if [ "$LINES" -gt 500 ]; then
  echo "FAIL: SKILL.md is $LINES lines (max 500)"
  ERRORS=$((ERRORS + 1))
else
  echo "PASS: SKILL.md is $LINES lines"
fi

# 2. 필수 섹션 존재 확인
for SECTION in "## On Activation" "## Phase 1" "## Phase 2" "## State Management" "## Error Handling" "## Session Resume" "## Trigger"; do
  if grep -q "$SECTION" "$SKILL"; then
    echo "PASS: Section '$SECTION' found"
  else
    echo "FAIL: Section '$SECTION' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 3. frontmatter 필수 필드
for FIELD in "invoke_mode: user-invocable" "return_behavior: stop-with-gate"; do
  if grep -q "$FIELD" "$SKILL"; then
    echo "PASS: Frontmatter '$FIELD' found"
  else
    echo "FAIL: Frontmatter '$FIELD' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 4. 화이트리스트 필드 언급 확인
for FIELD in "Current Phase" "Current Stage" "Complexity" "Selected Approach" "Approved Stages"; do
  if grep -q "$FIELD" "$SKILL"; then
    echo "PASS: State field '$FIELD' referenced"
  else
    echo "FAIL: State field '$FIELD' not referenced"
    ERRORS=$((ERRORS + 1))
  fi
done

# 5. 서킷 브레이커 언급
if grep -q "서킷 브레이커\|circuit breaker\|리트라이 상한" "$SKILL"; then
  echo "PASS: Circuit breaker defined"
else
  echo "FAIL: Circuit breaker not found"
  ERRORS=$((ERRORS + 1))
fi

# 6. 리뷰 관련 섹션 확인
for SECTION in "INCEPTION 리뷰" "CONSTRUCTION 리뷰" "requesting-code-review"; do
  if grep -q "$SECTION" "$SKILL"; then
    echo "PASS: Review section '$SECTION' found"
  else
    echo "FAIL: Review section '$SECTION' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
echo "=== Results: $ERRORS error(s) ==="
exit $ERRORS
```

- [ ] **Step 2: 실행 권한 부여 + 테스트**
Run: `chmod +x skills/aidlc-auto-mode/verify.sh && bash skills/aidlc-auto-mode/verify.sh`
Expected: 0 errors

- [ ] **Step 3: 커밋**
`feat: auto-mode Layer 1 검증 스크립트 추가`

---

### Task 11: 최종 통합 검증 + plugin.json 등록 확인

**Files:**
- Verify: `.claude-plugin/plugin.json` — skills 경로에 auto-mode 포함 확인

- [ ] **Step 1: plugin.json 확인**
plugin.json의 `"skills": "./skills"` 설정이 디렉토리 기반이므로 자동 인식 확인.
수동 등록이 필요하면 추가.

- [ ] **Step 2: 전체 검증**
Run: `bash skills/aidlc-auto-mode/verify.sh`
Expected: 0 errors

- [ ] **Step 3: 설계 문서 대비 체크리스트**

| 설계 요건 | 구현 여부 |
|----------|----------|
| greenfield 전용 | On Activation Step 2 |
| 기존 SKILL.md 무수정 | 신규 파일만 생성 |
| 분리: 1파일 삭제 + plugin.json 1줄 | 디렉토리 삭제로 완료 |
| INCEPTION 5개 리뷰어 | INCEPTION 리뷰 섹션 |
| CONSTRUCTION requesting-code-review 위임 | CONSTRUCTION 리뷰 섹션 |
| 유일한 게이트: INCEPTION 후 사용자 확인 | 사용자 확인 게이트 |
| 고위험 가정 미니 게이트 | 고위험 가정 게이트 |
| devflow 호환 상태 파일 | State Management |
| decision-log append-only | decision-log 규칙 |
| 글로벌 서킷 브레이커 | Error Handling |
| 세션 재개 자동 감지 | Session Resume |
| 초보자 친화 에스컬레이션 | 에스컬레이션 메시지 원칙 |
| 세션 체이닝 (매번 확인) | 세션 체이닝 |
| 실행 안내 | 최종 결과물 섹션 |

- [ ] **Step 4: 최종 커밋**
`feat: auto-mode 스킬 구현 완료 — 초보자용 완전 자동 devflow (closes #N)`
