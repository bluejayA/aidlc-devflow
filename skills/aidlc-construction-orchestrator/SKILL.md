---
name: aidlc-construction-orchestrator
description: CONSTRUCTION Phase 오케스트레이터. 스테이지 순회 + 게이트 관리 + Multi-unit 핸들링. Entry Orchestrator가 호출.
metadata:
  version: 0.6.0
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
  → functional-design (Comprehensive만) → [설계 게이트]
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

<!-- 재검증 프로토콜: _shared/patterns/session-continuity.md 참조 -->

1. 직전 완료 unit의 테스트 실행
2. 결과 분기:

**통과 시:**
```
✅ 재검증 통과 — [unit-name] 테스트 [N]개 통과
다음 작업부터 재개합니다.
```
→ Step 2로 진행

**실패 시:**
```
⚠️ 재검증 실패 — [unit-name] 테스트 [N]개 중 [M]개 실패

A) 전체 테스트 스위트 실행 (회귀 범위 확인)
B) systematic-debugging으로 즉시 조사
```
→ A: 전체 실행 후 실패 있으면 debugging 라우팅
→ B: 바로 `aidlc-systematic-debugging` 호출
→ debugging Return 수신 후 재검증 재실행 (Step 1.5 반복)

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

#### 2a. functional-design (조건부)

**실행 조건**: Complexity가 `Comprehensive`인 경우만

`aidlc-functional-design` 호출 (unit명 전달)

##### 설계 게이트 [표준 게이트]
```
[functional-design 결과 표시]
A) 변경 요청 → functional-design 재호출
B) 승인, 코드 생성 진행
```

**Minimal/Standard**: 이 단계 스킵, 바로 code-generation으로.

#### 2b. code-generation Plan 호출

`aidlc-code-generation` 호출 (unit명 + Complexity 인라인 전달: `"Complexity: [level]"`)

#### code-plan 게이트 [리뷰 연계 게이트]
```
[code-generation Plan 결과 표시]
[리뷰 결과 표시 (Standard 이상)]
A) 변경 요청 → code-generation 재호출
B) 승인, 코드 생성 진행 → code-generation: GENERATE 호출
```

#### 2c. code-generation Generate 호출

`"aidlc-code-generation: GENERATE — proceed with the approved plan for [unit-name]"` 인라인 신호로 호출

#### 구현 게이트 [리뷰 연계 게이트]
```
[code-generation 완료 결과 표시]
[리뷰 결과 표시 (Standard 이상)]
A) 수정 요청 → code-generation: GENERATE 재호출
B) 승인, 다음 unit 진행
```

승인 후:
- devflow-state의 `## Completed Units`에 unit명 추가
- `devflow-docs/session-summary.md` 업데이트: Completed Work에 unit 추가 + `**Commit**` 필드에 현재 HEAD hash
- devflow-audit에 로깅: `[timestamp] unit-complete: [unit-name] — [commit hash]`

#### 2d. 다음 unit 확인

미완료 unit이 있으면 → 2a로 돌아가 다음 unit 처리
모든 unit 완료 시 → build-and-test로 진행

### 3. build-and-test

`aidlc-build-and-test` 호출

#### 완료 게이트 [조건부 게이트]

build-and-test 결과에 따라 분기:

**빌드 성공 + 테스트 전체 통과 시:**
```
[build-and-test 결과 표시]
A) CONSTRUCTION 완료 승인
B) 추가 수정 요청 → code-generation 재호출
```

**테스트 실패 시:**
```
[build-and-test 결과 표시 — 실패 테스트 목록 포함]
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

build-and-test에서 테스트/빌드 실패 시 사용자가 debugging을 선택하면:

1. `aidlc-systematic-debugging` 호출
2. debugging 완료 시 Return 수신:
   ```
   [systematic-debugging 완료]
   - 근본 원인: [요약]
   - 수정 내용: [요약]
   - 테스트: [회귀 테스트명] 추가됨
   ```
3. debugging Return 수신 후 `aidlc-build-and-test` 재실행

## Audit Logging

각 게이트 결정 시 devflow-audit에 기록:
결정 이유 포함 (session-continuity 규약 참조).
- 스테이지명, 타임스탬프, 사용자 선택 (A/B/C), 결정 이유, 리뷰 결과 (있으면)

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
