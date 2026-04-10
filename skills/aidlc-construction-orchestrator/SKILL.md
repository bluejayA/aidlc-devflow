---
name: aidlc-construction-orchestrator
description: Use when CONSTRUCTION phase begins, to manage the full build cycle for each unit from implementation through verification.
metadata:
  version: 0.7.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# aidlc-construction-orchestrator

<!-- 출력 언어: 한국어 (Korean) -->
<!-- CONSTRUCTION Phase 오케스트레이터: 코드 생성 + 빌드/테스트 관리 -->
<!-- 게이트 패턴 참조: _shared/gate-patterns.md -->
<!-- 리뷰 정책: Standard 이상에서 리뷰 서브에이전트 dispatch (스킬 내부에서 처리) -->

## CONSTRUCTION 스테이지 순서

```
units-generation (조건부) → [units 게이트]
  → functional-design (Comprehensive만) → [설계 게이트]
  → code-generation Plan → [code-plan 게이트]
  → code-generation Generate → [구현 게이트]
  → (multi-unit이면 다음 unit으로 반복)
  → build-and-test → [완료 게이트]
```

## On Activation
<!-- @step:1 id=context-load -->
<!-- @step:2 id=revalidation skip-when=no-completed-units -->
<!-- @step:3 id=stage-decision -->

### Step 1: 컨텍스트 로드

다음 파일을 읽는다:
- `devflow-docs/devflow-state.md` — Complexity, Completed Units 확인
- `devflow-docs/inception/workflow-plan.md` — Approved Stages, Stage Depths 확인
- `devflow-docs/inception/requirements.md` — 요구사항 맥락 복원
- `devflow-docs/inception/application-design.md` — 설계 맥락 복원 (있으면)
- `devflow-docs/inception/units.md` — unit 목록 (있으면)
- `devflow-docs/session-summary.md` — 이전 세션 맥락 (있으면)

<!-- 아티팩트 로딩 규칙: _shared/patterns/session-continuity.md 참조 -->

컨텍스트 로드 완료 후 요약 표시:
```
📋 컨텍스트 로드 완료
- 로드한 파일: [count]개
- Phase: CONSTRUCTION
- 마지막 완료: [last completed unit or stage]
```

### Step 1.5: 재검증 (세션 재개 시)

devflow-state의 `## Completed Units`에 완료 unit이 있는 경우에만 실행.
신규 세션(완료 unit 없음)에서는 스킵.

`_shared/patterns/session-continuity.md` 섹션 4 "태스크 재검증 프로토콜" 적용.
통과 시 Step 2로 진행. 실패 시 프로토콜의 분기(debugging 라우팅 / 에스컬레이션) 따름.

### Step 2: 스테이지 결정

`workflow-plan.md`의 `## Approved Stages`에서:
- `units-generation: included` → units-generation부터 시작
- `units-generation: skipped` → code-generation으로 바로 진행

## The Orchestration Loop

### 1. units-generation (조건부)

**실행 조건**: `workflow-plan.md`에서 `units-generation: included`인 경우

스킬 호출 → 결과 표시

#### units 게이트 [표준 게이트]
<!-- @gate: units-generation -->
<!-- @gate-option: A -> units-generation {재호출} -->
<!-- @gate-option: B -> code-generation -->
```
[units-generation 결과 표시]
A) 변경 요청 (예: unit 분할/병합, 구현 순서 변경 등) → units-generation 재호출
B) 승인, 코드 생성 진행
```

<!-- @state-update: units-generation 승인 → devflow-state에 unit 목록 기록 -->
승인 후: devflow-state에 unit 목록 기록

### 1.5. SDD 모드 게이트 (Multi-unit만)
<!-- @gate: sdd-mode -->
<!-- @gate-option: A -> subagent-driven-development {SDD} -->
<!-- @gate-option: B -> code-generation {인라인} -->

units-generation 승인 후, unit 수를 확인하여 SDD 모드 게이트를 제시한다.

**unit 1개**: 게이트 없이 인라인 모드 자동 적용 → 섹션 2로 진행.

**unit 2개 이상**: SDD 모드 게이트 제시:
```
unit이 [N]개입니다. 컨텍스트 격리를 위해 SDD 모드를 권장합니다.

A) SDD 모드 (기본) — unit별 서브에이전트로 컨텍스트 리셋
   → aidlc-subagent-driven-development에 위임
B) 인라인 모드 — 현재 컨텍스트에서 순차 실행
```

**A (SDD 모드) 선택 시:**
1. Comprehensive에서 functional-design이 포함된 경우, SDD 호출 **전에** orchestrator가 unit별로 functional-design을 실행한다
2. `aidlc-subagent-driven-development` 호출 (인라인 신호: `"SDD: units=[devflow-docs/inception/units.md], summary=[devflow-docs/session-summary.md], complexity=[level], functional-designs=[devflow-docs/inception/functional-design-*.md]"`)
   - functional-design 산출물이 있으면 경로를 인라인 신호에 포함. SDD가 서브에이전트에 전달한다.
   - functional-design이 없으면 (Standard 이하) 해당 필드 생략
3. SDD 모드에서는 개별 unit 게이트(code-plan 게이트, 구현 게이트)가 **비활성화** — SDD 스킬의 태스크 완료 + R1 리뷰가 품질 게이트 역할
4. SDD 완료 후 → build-and-test(섹션 3)로 바로 진행

**B (인라인 모드) 선택 시:** 기존 섹션 2 루프 그대로 실행.

### 2. code-generation (Multi-unit 핸들링)

`devflow-docs/inception/units.md`에서 구현 순서를 읽는다.
units-generation이 스킵된 경우, 단일 unit으로 처리한다.

<!-- @state-update: unit 루프 진입 → devflow-state Active Unit을 현재 unit으로 설정 -->
**각 unit에 대해 아래를 반복:**

#### 2a. functional-design (조건부)

**실행 조건**: Complexity가 `Comprehensive`인 경우만

`aidlc-functional-design` 호출 (unit명 전달)

##### 설계 게이트 [표준 게이트]
<!-- @gate: functional-design -->
<!-- @gate-option: A -> functional-design {재호출} -->
<!-- @gate-option: B -> code-generation-plan -->
```
[functional-design 결과 표시]
A) 변경 요청 (예: 도메인 엔티티, 비즈니스 규칙, API 계약 등) → functional-design 재호출
B) 승인, 코드 생성 진행
```

**Minimal/Standard**: 이 단계 스킵, 바로 code-generation으로.

#### 2b. code-generation Plan 호출

`aidlc-code-generation` 호출 (unit명 + Complexity 인라인 전달: `"Complexity: [level]"`)

#### code-plan 게이트 [리뷰 연계 게이트 + Override 변형]
<!-- @gate: code-plan -->
<!-- @gate-option: A -> code-generation-plan {재호출} -->
<!-- @gate-option: B -> code-generation-generate -->
<!-- @gate-option: C -> code-generation-generate {override} -->

`_shared/patterns/review-gate-pattern.md` 적용. 리뷰 결과에 따라 게이트 분기:

- A) 변경 요청 → code-generation 재호출
- B) 승인 → code-generation: GENERATE 호출
- 확장 옵션: C) 오버라이드 (FAIL/CONDITIONAL 시, review-gate-pattern의 오버라이드 audit 형식 적용)

리뷰 루프 5회 소진 시 conventions escalation 메시지 우선.

#### 2c. code-generation Generate 호출

`"aidlc-code-generation: GENERATE — proceed with the approved plan for [unit-name]"` 인라인 신호로 호출

#### 구현 게이트 [리뷰 연계 게이트]
<!-- @gate: code-generation-result -->
<!-- @gate-option: A -> code-generation-generate {재호출} -->
<!-- @gate-option: B -> next-unit -->
<!-- @gate-option: S -> next-unit {skip-review} -->
`_shared/patterns/review-gate-pattern.md` 적용:

- A) 변경 요청 → code-generation: GENERATE 재호출
- B) 승인, 다음 unit 진행
- 확장 옵션: S) 리뷰 스킵 (audit 기록됨, 다음 unit은 정상 리뷰)

**리뷰 자동 실행 (인라인 모드, Standard 이상)**: `aidlc-requesting-code-review`를 R1(단일 리뷰) 모드로 자동 호출.
Council/Teams 리뷰를 원하면 자유 발화로 요청 → Interrupt Handler가 처리.
requesting-code-review가 모든 리뷰 로직을 소유한다 (Single Source of Truth).
**Minimal depth**: R1 단일 리뷰 자동 실행 (Standard와 동일).

<!-- @state-update: unit 완료 → devflow-state Completed Units 추가 + Active Unit 갱신 -->
승인 후:
- devflow-state의 `## Completed Units`에 unit명 추가
- `devflow-docs/session-summary.md` 업데이트: Completed Work에 unit 추가 + `**Commit**` 필드에 현재 HEAD hash
- devflow-audit에 로깅: `[timestamp] unit-complete: [unit-name] — [commit hash]`

#### 2d. 다음 unit 확인

미완료 unit이 있으면 → 2a로 돌아가 다음 unit 처리
모든 unit 완료 시 → build-and-test로 진행

### 3. build-and-test

`aidlc-build-and-test` 호출

#### 3a. Auto-fix 전처리 (Self-Healing Loop)

build-and-test 결과를 받은 후, 완료 게이트를 표시하기 **전에** 자동 수정을 시도한다.

**즉시 게이트로 전달 (auto-fix 스킵):**
- 빌드 실패 (컴파일 에러, 설정 문제, 의존성 누락)
- 환경 문제 (missing binary, permission denied)
- 리스크 태그에 `auth/security` 표시된 unit의 오류
- 에러 메시지에 `auth`, `permission`, `forbidden`, `unauthorized` 키워드 포함 시 (리스크 태그 누락 방어)

**auto-fix 대상 (코드 수정으로 해결 가능한 객관적 오류):**
- 테스트 실패 (assertion error, runtime error in tests)
- 린트 에러 (formatting, unused imports, type errors)

**auto-fix 루프 (최대 3회):**
1. 실패한 테스트명 + 에러 메시지 추출
2. `code-generation: GENERATE — auto-fix for [unit-name]: [실패 테스트명], [에러 메시지 요약]` 재호출
3. `aidlc-build-and-test` 재실행
4. 종료 조건 확인:
   - 성공 → 완료 게이트 (성공 분기)로 전달. `"(auto-fix [N]회 적용됨)"` 안내 추가
   - plateau (연속 2회 동일 테스트명 집합 실패, 또는 실패 수가 감소하지 않음) → 완료 게이트 (실패 분기)로 전달
   - 3회 도달 → 완료 게이트 (실패 분기)로 전달
5. 각 시도를 devflow-audit에 기록: `[timestamp] auto-fix attempt [N]/3: [에러 요약] → [수정 내용]`
6. auto-fix 루프 내에서 code-generation 호출이 실패하면 즉시 루프 중단 후 완료 게이트(실패 분기)로 전달
7. 루프 완료 시 session-summary에 `auto-fix [N]회 적용` 형태로 요약 기록

auto-fix 실패 시 완료 게이트에 실패 보고서(시도한 수정 목록, 각 시도 결과) 추가 표시.

#### 완료 게이트 [조건부 게이트]
<!-- @gate: build-and-test-result -->
<!-- @gate-option: A -> CONSTRUCTION-complete -->
<!-- @gate-option: B -> code-generation-plan {추가수정} -->

build-and-test 결과 (auto-fix 전처리 후)에 따라 분기:

**빌드 성공 + 테스트 전체 통과 시:**
```
[build-and-test 결과 표시]
(auto-fix [N]회 적용됨 — 해당 시에만 표시)
A) CONSTRUCTION 완료 승인
B) 추가 변경 요청 (예: 테스트 보완, 성능 개선 등) → code-generation 재호출
```

**테스트 실패 시 (auto-fix 소진 포함):**
```
[build-and-test 결과 표시 — 실패 테스트 목록 포함]
[auto-fix 실패 보고서 — 해당 시에만 표시]
A) systematic-debugging으로 조사
B) 실패를 무시하고 완료 (devflow-state에 "테스트 실패 [N]건 미해결" 기록)
```

**빌드 실패 시:**
```
[build-and-test 결과 표시 — 빌드 에러 포함]
A) systematic-debugging으로 조사
(빌드 실패는 완료 불가 — 무시 선택지 없음)
```

### Debugging 라우팅

build-and-test에서 테스트/빌드 실패 시 (auto-fix 소진 후) 사용자가 debugging을 선택하면:

0. build-and-test 실패 시점의 에러 메시지(테스트명 + 에러 출력)를 컨텍스트에 보존한다
   — 이 error_message는 K 게이트에서 devflow-solutions에 전달하는 데 사용
1. `aidlc-systematic-debugging` 호출
2. debugging 완료 시 Return 수신:
   ```
   [systematic-debugging 완료]
   - 근본 원인: [요약]
   - 수정 내용: [요약]
   - 테스트: [회귀 테스트명] 추가됨
   ```
3. K 게이트 표시 (재진입 방지: devflow-audit에 현재 unit + compound 로그 있으면 K 미표시):
   ```
   [systematic-debugging 완료]
   - 근본 원인: [요약]
   - 수정 내용: [요약]

   K) 학습 기록 저장 → devflow-solutions 호출
      → 이 해결 사례를 구조화하여 devflow-docs/solutions/에 저장합니다
   →) 바로 build-and-test 재실행 (기본)
   ```
4. K 선택 시:
   - `devflow-solutions` STORE 호출 (debugging Return 4필드 + 보존된 error_message)
   - verdict별 안내:
     - SAVE: "✅ 솔루션 저장 완료: {saved_path}" 표시
     - DUPLICATE: "⚠️ 유사한 솔루션이 이미 존재합니다: {similar_to}\n   저장을 건너뜁니다." 표시
     - REJECT: "❌ 솔루션 저장 실패: {reason}\n   Privacy 위반 또는 형식 오류로 저장하지 않았습니다." 표시
   - verdict 표시 후 `aidlc-build-and-test` 재실행
5. K 스킵(기본 →) 시: 바로 `aidlc-build-and-test` 재실행

K 선택/스킵 모두 devflow-audit에 로깅:
```
- timestamp: [ISO 8601]
- type: compound
- unit: [unit-name]
- action: [save | skip]
- verdict: [SAVE | DUPLICATE | REJECT | null (skip 시)]
- path: [saved_path | null]
```

**재진입 방지**: devflow-audit의 최근 로그에서 현재 unit + compound 타입 로그 존재 시 K 미표시.
동일 build-and-test 실패 건 내에서만 적용. 새로운 실패에서는 다시 K 표시.

**Step 1.5 재검증 Debugging에는 K 게이트를 적용하지 않는다.** K 게이트는 본 Debugging 라우팅(build-and-test 실패 후)에서만 표시.

**디버깅 루프 소프트 리밋**: 동일 unit에서 debugging→build-and-test 루프는 **최대 3회**까지. 3회 실패 시 에스컬레이션:
```
⚠️ 동일 unit에서 디버깅 3회 실패 — 자동 복구 한계

A) 수동으로 디버깅 계속 (루프 카운트 리셋)
B) 이 unit을 실패 상태로 완료 (devflow-state에 "빌드/테스트 실패 미해결" 기록)
```

## Interrupt Handling
<!-- @interrupt: global -->

모든 게이트에서 사용자 응답이 선택지 밖 자유 발화인 경우:
→ `_shared/patterns/interrupt-handler.md` 참조하여 인터럽트 게이트 프로토콜 실행.

## Audit Logging

각 게이트 결정 시 devflow-audit에 기록:
결정 이유 포함 (session-continuity 규약 참조).
- 스테이지명, 타임스탬프, 사용자 선택 (A/B/C), 결정 이유, 리뷰 결과 (있으면)
- override 이벤트: code-plan 게이트 C 선택 시 별도 형식 (code-plan 게이트 섹션 참조)

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
