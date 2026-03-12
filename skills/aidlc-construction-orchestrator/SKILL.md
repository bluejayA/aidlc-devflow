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
