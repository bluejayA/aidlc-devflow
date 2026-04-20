---
name: aidlc-using-devflow
description: |
  AIDLC 워크플로우로 새 프로젝트를 시작하거나, 기존 devflow 세션을 재개하거나, "devflow 시작" 또는 "devflow 재개" 요청 시 사용.
  Use when starting a new project with AIDLC workflow, resuming an existing devflow session, or when "devflow 시작" or "devflow 재개" is requested.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
  skill_nature: amplification
  lifecycle: active
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
2. **기존 산출물 확인 게이트**: `devflow-docs/inception/` 디렉토리에 산출물(`.md` 파일, workspace.md 제외)이 존재하는지 확인한다. 또한 `devflow-docs/.archive/` 내 이전 세션 수를 카운트한다 (`inception-*` 디렉토리 수).

   **산출물이 없는 경우**:
   - `.archive/`에 이전 세션이 있으면 이력 안내 후 Step 3으로 진행:
     ```
     (현재 inception/ 산출물 없음)
     이전 아카이브: [N]개 세션 (.archive/에서 참조 가능)

     → 새 작업을 시작합니다.
     ```
   - `.archive/`도 없으면 안내 없이 Step 3으로 진행 (정상 새 시작)

   **산출물이 있는 경우** → `requirements.md`에서 `## User Intent` 내용과 `**Depth**` 값, `**Timestamp**` 값을 읽어 기존 산출물 처리 게이트를 제시한다. `requirements.md`가 없거나 해당 섹션이 비어 있으면 "(정보 없음)"으로 대체한다:
   ```
   ## 기존 INCEPTION 산출물 발견

   이전 작업: "[User Intent 1줄 요약]" ([Timestamp 날짜], [Depth])
   산출물: [파일 목록] ([N]개)
   이전 아카이브: [N]개 세션 (.archive/에서 참조 가능)

   A) 기존 설계 기반으로 보완 (UPDATE 모드)
      → 이전 요구사항/설계를 유지하고 새 기능을 추가합니다
   B) 처음부터 새로 시작 (기존 산출물 아카이브)
      → 기존 inception/, construction/ 을 .archive/로 이동 후 새로 시작합니다
      ※ workspace.md는 유지됩니다
      ※ 이전 산출물은 .archive/에서 언제든 참조 가능합니다
   ```

   A 선택 시:
   - devflow-audit에 로깅: `"New flow — UPDATE mode (preserving existing artifacts)"`
   - 이후 inception-orchestrator에서 호출하는 각 스테이지 스킬이 기존 파일을 감지하면 UPDATE 모드로 동작

   B 선택 시:
   - `devflow-docs/inception/workspace.md`가 있으면 임시로 보존 (이동 전 별도 보관)
   - `devflow-docs/inception/`을 `devflow-docs/.archive/inception-[timestamp]/`로 이동
   - `devflow-docs/construction/`을 `devflow-docs/.archive/construction-[timestamp]/`로 이동 (있으면)
   - 보존한 `workspace.md`를 새로 생성된 `devflow-docs/inception/workspace.md`로 복원
   - devflow-audit에 로깅: `"New flow — clean start (artifacts archived, workspace.md preserved)"`

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
5. **백로그 확인 (Lazy Loading)**: `devflow-docs/backlog.md`가 존재하면:
   - `## Next`, `## Open` 섹션의 항목 수(`- **BL-` 패턴)만 카운트한다. 파일 내용은 로드하지 않는다.
   - 안내 표시:
     ```
     백로그: Next [N]건, Open [M]건
     → 백로그를 확인하려면 "백로그 보여줘"라고 요청하세요.
     ```
   - 사용자가 요청하지 않으면 내용을 로드하지 않고 다음 단계로 진행한다.
   - 파일이 없으면 이 단계를 건너뛴다.
6. devflow-audit에 로깅: "New aidlc session started" + 사용자 원래 요청
7. `aidlc-inception-orchestrator` 호출

### Resume Flow

1. `devflow-docs/devflow-state.md` 읽기
2. `devflow-docs/session-summary.md` 읽기 (있으면)

   **Memory Sync Staleness Check** *(optional, auto-memory 운영 시)*:
   - (a) 머지 이력 비교 — `MEMORY.md`/`project_*.md` 최근 PR/BL 번호와 `git log --first-parent main -10` 대조
   - (b) 로컬 미푸시 검사 — `git rev-list --count origin/main..HEAD` ≥ 1이면 unpushed 존재
   - 임계: (a)에서 3 PR 이상 또는 3일 이상 불일치, 또는 (b)에서 미푸시 발견 시 아래 프롬프트
   - 프롬프트: "⚠️ Memory staleness / push 보류 감지 — memory PR #N / git latest PR #M (+K) / local ahead J commits. A) 갱신 후 Resume / B) 그대로 Resume"
   - auto-memory 부재 또는 (a)(b) 모두 0이면 no-op

   > 📌 **관측 요청 (BL-092 L3, ~2026-04-28 T+14까지)**: 이 Step 2.5 실행 시 Jay에게 "Memory Sync Staleness Check 실행됨"을 명시적으로 알리고, issue #177에 `observed (3-2)` 코멘트를 제안. T+14 Phase 2 plan 작성 시 이 hint 제거 예정 (만료 test가 강제).

3. **백로그 확인 (Lazy Loading)**: `devflow-docs/backlog.md`가 존재하면:
   - `## Next`, `## Open` 섹션의 항목 수(`- **BL-` 패턴)만 카운트한다. 파일 내용은 로드하지 않는다.
   - 안내 표시:
     ```
     백로그: Next [N]건, Open [M]건
     → 백로그를 확인하려면 "백로그 보여줘"라고 요청하세요.
     ```
   - 사용자가 요청하지 않으면 내용을 로드하지 않고 다음 단계로 진행한다.
   - 파일이 없으면 이 단계를 건너뛴다.
4. `## Current Phase` 값에 따라 분기:

### 상태 디스패치 테이블

| Phase 값 | 조건 | 동작 | 게이트 |
|----------|------|------|--------|
| `finished` | — | 아카이브 → New Flow | 없음 (자동) |
| `complete` | Finishing == "B (PR pending)" | PR 자동 확인 → 게이트 | A/B |
| `complete` | Finishing 없음 | — | A/B |
| `INCEPTION` | — | — | A/B |
| `CONSTRUCTION` | — | — | A/B |
| 파싱 불가 | — | 백업 → New Flow | 없음 (자동) |

### 자동 처리 경로

**`finished`**: state와 session-summary(있으면)를 `devflow-docs/.archive/`로 이동 후 New Flow 진행. 사용자 안내 없음.

**파싱 불가**: `devflow-docs/.archive/devflow-state-backup-[timestamp].md`로 백업 후 New Flow 진행.

### 게이트 경로

#### `complete` + PR pending

<!-- @state-update: PR 머지 확인 → Current Phase를 finished로 -->

`gh pr view [PR URL] --json state`로 PR 상태를 자동 확인한 뒤 게이트를 제시한다.

**PR 이미 머지된 경우:**
```
## aidlc — PR 머지 확인됨

PR [URL]이 머지되었습니다.

A) devflow 종료 처리 → 아카이브 + 워크트리 정리 + New Flow
B) 새 작업 시작 (아카이브만)
```

**PR 아직 열린 경우:**
```
## aidlc — PR 대기 중

PR [URL]이 아직 열려있습니다.

A) devflow 종료 처리 (PR 머지 완료로 간주)
B) 다른 작업 시작 (아카이브)
```

A 선택 시:
- devflow-state의 `## Current Phase`를 `finished`로 업데이트
- state와 session-summary를 `.archive/`로 이동
- 워크트리 존재 시 제거 (`git worktree remove` + `git worktree prune`)
- devflow-audit에 로깅: `"Flow finished — PR merged"`

B 선택 시:
- state와 session-summary를 `.archive/`로 이동
- New Flow 진행

#### `complete` (Finishing Choice 없음)

```
## aidlc — CONSTRUCTION 완료, 브랜치 처리 대기

A) aidlc-finishing-a-development-branch 실행 → 브랜치 처리
B) 새 작업 시작 (기존 상태 초기화)
```

#### `INCEPTION` 또는 `CONSTRUCTION`

```
## aidlc — 진행 중인 작업 발견

현재 단계: [Current Phase] > [Current Stage]
완료된 스테이지: [list]

A) 이전 작업 재개
B) 새 작업 시작 (기존 상태 초기화)
```

A 선택 시:
- devflow-audit에 로깅: `"Session resumed at [stage] — commit: [git rev-parse --short HEAD]"`
- 해당 Phase Orchestrator 호출

B 선택 시:
- state와 session-summary를 `.archive/`로 이동
- New Flow 진행

## Phase 전환

### INCEPTION 완료 시

<!-- @state-update: INCEPTION 완료 → Current Phase를 CONSTRUCTION으로 -->
`aidlc-inception-orchestrator`가 INCEPTION 완료를 반환하면:
1. devflow-state의 `## Current Phase`를 `CONSTRUCTION`으로 업데이트
2. `devflow-docs/session-summary.md` 업데이트:
   - `## Current State`의 Phase를 `CONSTRUCTION`으로
   - `**Commit**` 필드에 현재 HEAD hash
   - devflow-audit에 `"Phase transition: INCEPTION → CONSTRUCTION — commit: [hash]"`
3. `aidlc-construction-orchestrator` 호출

### CONSTRUCTION 완료 시

<!-- @state-update: CONSTRUCTION 완료 → Current Phase를 complete로 -->
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
| inception/ (B: 새로 시작) | `.archive/inception-[timestamp]/` (workspace.md 제외 — 복원) |
| construction/ (B: 새로 시작) | `.archive/construction-[timestamp]/` |

### 아카이브 일관성 규칙

**state와 session-summary는 항상 함께 아카이브한다.** 어떤 경로로 아카이브가 발생하든 두 파일 모두 이동한다 (session-summary가 없으면 state만).

### 아카이브 참조 정책

`.archive/`는 이전 산출물의 참조 저장소이다. 사용자 요청 또는 컨텍스트상 필요할 때 (예: 이전 기능의 요구사항 참고, NFR 재활용 등) 언제든 탐색·참조할 수 있다.
