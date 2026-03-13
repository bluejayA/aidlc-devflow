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

### 설계/계획 요청 시
- 설계 협업 요청 → `aidlc-brainstorming` 안내
- 구현 계획 작성 요청 → `aidlc-writing-plans` 안내
- 서브에이전트 기반 실행 요청 → `aidlc-subagent-driven-development` 안내
- 배치 실행 요청 → `aidlc-executing-plans` 안내
- TDD 강제 필요 시 → `aidlc-test-driven-development` 참조

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
