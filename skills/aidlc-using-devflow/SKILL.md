---
name: aidlc-using-devflow
description: |
  AIDLC 워크플로우로 새 프로젝트를 시작하거나, 기존 devflow 세션을 재개하거나, "devflow 시작" 또는 "devflow 재개" 요청 시 사용.
  Use when starting a new project with AIDLC workflow, resuming an existing devflow session, or when "devflow 시작" or "devflow 재개" is requested.
metadata:
  version: 0.5.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
---

# aidlc-using-devflow

<!-- 출력 언어: 한국어 (Korean) -->
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
2. **기존 산출물 확인 게이트**: `devflow-docs/inception/` 디렉토리에 산출물(`.md` 파일)이 존재하는지 확인한다.

   **산출물이 없으면** → Step 3으로 진행 (정상 새 시작)

   **산출물이 있으면** → 기존 산출물 처리 게이트 제시:
   ```
   ## 기존 INCEPTION 산출물 발견

   이전 작업의 설계 산출물이 남아있습니다:
   - [파일 목록 표시: requirements.md, application-design.md 등]

   A) 기존 설계 기반으로 보완 (UPDATE 모드)
      → 이전 요구사항/설계를 유지하고 새 기능을 추가합니다
   B) 처음부터 새로 시작 (기존 산출물 아카이브)
      → 기존 inception/, construction/ 을 .archive/로 이동 후 새로 시작합니다
   ```

   A 선택 시:
   - devflow-audit에 로깅: `"New flow — UPDATE mode (preserving existing artifacts)"`
   - 이후 inception-orchestrator에서 호출하는 각 스테이지 스킬이 기존 파일을 감지하면 UPDATE 모드로 동작

   B 선택 시:
   - `devflow-docs/inception/`을 `devflow-docs/.archive/inception-[timestamp]/`로 이동
   - `devflow-docs/construction/`을 `devflow-docs/.archive/construction-[timestamp]/`로 이동 (있으면)
   - devflow-audit에 로깅: `"New flow — clean start (artifacts archived)"`

3. `devflow-docs/` 디렉토리 생성 (하위 `inception/`, `construction/` 포함 — 이미 있으면 유지)
4. `devflow-docs/devflow-state.md` 초기화:
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
5. devflow-audit에 로깅: "New aidlc session started" + 사용자 원래 요청
6. `aidlc-inception-orchestrator` 호출

### Resume Flow

1. `devflow-docs/devflow-state.md` 읽기
2. `devflow-docs/session-summary.md` 읽기 (있으면)
3. `## Current Phase` 값에 따라 분기:

#### Phase가 `finished`인 경우

이전 플로우가 완전히 종료된 상태. 아카이브 처리가 누락된 경우.

```
## aidlc — 이전 플로우 완료됨

이전 작업이 완료된 상태입니다.

→ 새 작업을 시작합니다.
```

state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동 후 New Flow 진행.
- `devflow-docs/.archive/devflow-state-[timestamp].md`
- `devflow-docs/.archive/session-summary-[timestamp].md` (있으면)

#### Phase가 `complete`이고 `## Finishing Choice`가 `B (PR pending)`인 경우

PR 생성 후 머지 대기 중인 상태.

```
## aidlc — PR 머지 대기 중

이전 작업의 PR이 아직 열려있습니다.
PR URL: [## PR URL 값]

A) PR 머지 완료 → devflow 종료 처리
B) PR 아직 진행 중 → 다른 작업 시작
C) PR 확인 후 결정
```

A 선택 시:
- `gh pr view [PR URL] --json state`로 머지 확인 (가능한 경우)
- devflow-state의 `## Current Phase`를 `finished`로 업데이트
- state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동
- 워크트리 존재 시 제거 (`git worktree remove` + `git worktree prune`)
- devflow-audit에 로깅: `"Flow finished — PR merged"`
- 새 작업 시작 여부 안내

B 선택 시:
- state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동
- New Flow 진행

C 선택 시:
- PR 상태를 `gh pr view`로 확인 후 결과에 따라 A 또는 재안내

#### Phase가 `complete`인 경우 (Finishing Choice 없음)

CONSTRUCTION은 완료됐지만 finishing-branch를 아직 실행하지 않은 상태.

```
## aidlc — CONSTRUCTION 완료, 브랜치 처리 대기

INCEPTION + CONSTRUCTION이 완료되었습니다.

A) aidlc-finishing-a-development-branch 실행 → 브랜치 처리
B) 새 작업 시작 (기존 상태 초기화)
```

#### Phase가 `INCEPTION` 또는 `CONSTRUCTION`인 경우 (기존 동작)

```
## aidlc — 진행 중인 작업 발견

현재 단계: [Current Phase] > [Current Stage]
완료된 스테이지: [list]
마지막 완료: [session-summary의 최근 완료 항목] (있으면)

A) 이전 작업 재개
B) 새 작업 시작 (기존 상태 초기화)
```

A 선택 시:
- devflow-audit에 로깅: `"Session resumed at [stage] — commit: [git rev-parse --short HEAD]"`
- `## Current Phase` 확인하여 해당 Phase Orchestrator 호출:
  - `INCEPTION` → `aidlc-inception-orchestrator` 호출
  - `CONSTRUCTION` → `aidlc-construction-orchestrator` 호출

B 선택 시:
- 기존 state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동
- New Flow 진행

## Phase 전환

### INCEPTION 완료 시

`aidlc-inception-orchestrator`가 INCEPTION 완료를 반환하면:
1. devflow-state의 `## Current Phase`를 `CONSTRUCTION`으로 업데이트
2. `devflow-docs/session-summary.md` 업데이트:
   - `## Current State`의 Phase를 `CONSTRUCTION`으로
   - `**Commit**` 필드에 현재 HEAD hash
   - devflow-audit에 `"Phase transition: INCEPTION → CONSTRUCTION — commit: [hash]"`
3. `aidlc-construction-orchestrator` 호출

### CONSTRUCTION 완료 시

`aidlc-construction-orchestrator`가 CONSTRUCTION 완료를 반환하면:
1. devflow-state의 `## Current Phase`를 `complete`로 업데이트
2. `devflow-docs/session-summary.md` 최종 업데이트:
   - `## Current State`의 Phase를 `complete`로
   - `**Commit**` 필드에 현재 HEAD hash
   - `## Next Steps`에 "aidlc-finishing-a-development-branch로 머지/PR 진행"
3. devflow-audit에 로깅: `"Construction complete — commit: [hash]"`
4. 완료 안내:
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
1. `devflow-docs/.archive/devflow-state-backup-[timestamp].md`로 백업
2. 새 세션 시작 (기존 산출물은 그대로 활용)

### Stage skill 호출 실패
스킬이 예상치 못한 결과를 반환하면:
A) 해당 단계 재시도 / B) 단계 스킵 (devflow-state에 skipped 기록)

## Archive Convention

모든 아카이브 파일은 `devflow-docs/.archive/`에 저장한다. 디렉토리가 없으면 첫 아카이브 시 생성한다.

### 아카이브 대상 및 경로

| 대상 | 아카이브 경로 |
|------|-------------|
| devflow-state.md | `.archive/devflow-state-[timestamp].md` |
| session-summary.md | `.archive/session-summary-[timestamp].md` |
| devflow-state.md (손상 백업) | `.archive/devflow-state-backup-[timestamp].md` |
| inception/ (B: 새로 시작) | `.archive/inception-[timestamp]/` |
| construction/ (B: 새로 시작) | `.archive/construction-[timestamp]/` |

### 아카이브 일관성 규칙

**state와 session-summary는 항상 함께 아카이브한다.** 어떤 경로로 아카이브가 발생하든 두 파일 모두 이동한다 (session-summary가 없으면 state만).

### 아카이브 파일은 읽지 않는다

아카이브된 파일은 이력 보존 목적이다. 어떤 스킬도 `.archive/` 내부 파일을 참조하지 않는다. 필요 시 사용자가 수동으로 확인한다.
