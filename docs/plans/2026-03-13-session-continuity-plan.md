# Session Continuity 구현 계획

> **For agentic workers:** REQUIRED: Use `aidlc:aidlc-executing-plans` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 세션 재개 시 아티팩트 자동 로딩, session-summary 기록 체계, 태스크 재검증 프로토콜을 기존 AIDLC 스킬에 점진적으로 추가한다.

**Complexity:** Standard

**Architecture:** 기존 3단 위임 체인 아키텍처 유지. 신규 shared pattern 1개 추가 후, 기존 오케스트레이터/스킬 5개에 섹션을 추가하는 방식. 아키텍처 변경 없음.

**Tech Stack:** Markdown (SKILL.md 프롬프트 명세)

**Spec:** `docs/plans/2026-03-13-session-continuity-design.md`

**참고:** 이 작업은 프롬프트 명세(SKILL.md) 수정이므로 TDD 대상이 아님. 각 태스크 완료 후 리뷰로 검증.

---

## Chunk 1: 기반 + 오케스트레이터

### Task 1: session-continuity shared pattern 생성

**Files:**
- Create: `skills/_shared/patterns/session-continuity.md`

- [ ] **Step 1: 파일 생성**

설계 문서의 "신규 파일" 섹션(36-209줄)의 내용 구조를 그대로 작성한다.

```markdown
# Session Continuity Pattern

## 1. 아티팩트 로딩 규칙

세션 재개 시 Phase Orchestrator가 컨텍스트 로드 단계에서 참조한다.
모든 경로는 `devflow-docs/` 기준이다.

### INCEPTION 재개

각 스테이지 스킬이 자체적으로 필요한 파일을 로드한다 (참고용 테이블).
현재 Stage에 따라 누적 로드:

| 재개 Stage | 로드할 파일 |
|-----------|-----------|
| requirements-analysis | workspace.md |
| user-stories / nfr-requirements | workspace.md, requirements.md |
| workflow-planning | workspace.md, requirements.md, user-stories.md(있으면), nfr-requirements.md(있으면) |
| application-design | 위 전체 |

### CONSTRUCTION 재개

항상 로드:
- devflow-state.md
- inception/workflow-plan.md

추가 로드 (직전 Phase 핵심 산출물):
- inception/requirements.md
- inception/application-design.md (있으면)
- inception/units.md (있으면)

현재 unit 컨텍스트:
- construction/{unit-name}/code-plan.md (있으면)

### executing-plans 재개

- 계획 파일 로드 (기존과 동일)
- devflow-audit 교차 확인 (기존과 동일)
- session-summary.md 로드 (신규)

### 로딩 후 컨텍스트 요약

로드 완료 후 사용자에게 간략 요약 표시:

    📋 컨텍스트 로드 완료
    - 로드한 파일: [count]개
    - Phase: [current phase]
    - 마지막 완료: [last completed stage/unit]

## 2. Session Summary

### 생성 타이밍

| 시점 | 트리거 |
|------|--------|
| INCEPTION 스테이지 완료 | Inception Orchestrator가 각 스테이지 게이트 승인 시 업데이트 (최초 생성 포함) |
| Phase 전환 | INCEPTION → CONSTRUCTION 전환 시 Entry Orchestrator가 업데이트 |
| Unit 완료 | Construction Orchestrator가 unit 구현 게이트 승인 시 업데이트 |
| CONSTRUCTION 완료 | Entry Orchestrator가 최종 업데이트 |

session-summary.md는 INCEPTION 첫 번째 스테이지 완료 시 생성됨.
INCEPTION 중간에 세션이 끊겨도 재개 시 이 파일로 맥락 복원 가능.

### 파일 위치

`devflow-docs/session-summary.md`

### 템플릿

    # Session Summary

    **Last Updated**: [ISO 8601]
    **Commit**: [short hash]

    ## Current State
    - Phase: [INCEPTION | CONSTRUCTION | complete]
    - Stage: [current stage]
    - Complexity: [level]
    - Approach: [selected approach name]

    ## Key Decisions
    - [timestamp] [결정 내용] — [이유 한 줄]

    ## Completed Work
    ### INCEPTION
    - [x] workspace-detection — [한 줄 결과]
    - [x] requirements-analysis — [한 줄 결과]

    ### CONSTRUCTION
    - [x] unit: [name] — [한 줄 결과]
    - [ ] unit: [name] — (진행 중)

    ## Next Steps
    - [다음 작업 설명]
    <!-- Key Decisions, Completed Work는 최근 20개까지만 유지. 초과 시 오래된 항목 삭제. -->

    ## For Next Session
    - [인수인계 시 알아야 할 핵심 맥락]
    - [주의사항이나 미해결 이슈]

### Commit Hash 기록

기록 지점: 세션 시작/재개, Phase 전환, Unit 구현 완료.
수집 방법: `git rev-parse --short HEAD` (git 미사용 환경에서는 `(no git)` 표기).
기록 위치: session-summary.md의 **Commit** 필드 (최신만) + audit 로그의 전환점 항목에 inline.

## 3. Audit 강화

### 기존 형식
    [timestamp] [stage] — [user choice: A/B/C]

### 강화 형식
    [timestamp] [stage] — [user choice: A/B/C] — [결정 이유/맥락 한 줄]

### 하위 호환성
기존 형식 로그도 유효하다. `— [이유]` 부분은 선택적이며, 파싱 시 없어도 정상 처리한다.

## 4. 태스크 재검증 프로토콜

CONSTRUCTION 세션 재개 시 construction-orchestrator가 실행.

### 재검증 실행 주체 규칙

- **construction-orchestrator 경유**: Step 1.5에서 재검증 실행
- **executing-plans 독립 실행**: construction-orchestrator 외부 호출 시에만 자체 재검증
- **중복 방지**: construction-orchestrator 내부 호출 시 재검증 스킵

### 재검증 후 복귀 경로

재검증 실패 → debugging 완료 시:
- construction-orchestrator: debugging Return 수신 → 재검증 재실행
- executing-plans: debugging 완료 → 재검증 재실행 → 통과 시 정상 재개

### 프로세스

1. devflow-state에서 완료 unit 목록 확인
2. 완료 unit이 있으면 → 직전 완료 unit의 테스트 실행
3. 결과에 따라 분기:

통과 시:
    ✅ 재검증 통과 — [unit-name] 테스트 [N]개 통과
    다음 작업부터 재개합니다.

실패 시:
    ⚠️ 재검증 실패 — [unit-name] 테스트 [N]개 중 [M]개 실패

    A) 전체 테스트 스위트 실행 (회귀 범위 확인)
    B) systematic-debugging으로 즉시 조사
```

- [ ] **Step 2: 커밋**

```bash
git add skills/_shared/patterns/session-continuity.md
git commit -m "feat: session-continuity shared pattern 추가 (아티팩트 로딩 + summary + 재검증)"
```

---

### Task 2: devflow-conventions.md에 Session Continuity 규약 추가

**Files:**
- Modify: `skills/_shared/devflow-conventions.md` (153줄 뒤에 추가)

- [ ] **Step 1: Session Continuity 규약 섹션 추가**

`## Subagent Dispatch Rules` 섹션(148줄) 뒤에 아래 섹션 추가:

```markdown
## Session Continuity 규약

- `_shared/patterns/session-continuity.md` — 아티팩트 로딩 규칙, session-summary 템플릿, 재검증 프로토콜
- 세션 재개 시 Phase Orchestrator가 이 패턴을 참조하여 컨텍스트 로드
- session-summary.md는 INCEPTION 스테이지 완료, Phase 전환, Unit 완료 시 자동 업데이트
- commit hash는 핵심 전환점에서만 기록 (세션 시작/재개, Phase 전환, Unit 완료)

### Audit 강화 형식
기존 `[timestamp] [stage] — [choice]`에 결정 이유 한 줄 추가:
`[timestamp] [stage] — [choice] — [이유]`
기존 형식도 유효 (하위 호환).
```

- [ ] **Step 2: 버전 업데이트**

frontmatter의 `version: 0.4.0` → `version: 0.5.0`

- [ ] **Step 3: 커밋**

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "feat: devflow-conventions에 Session Continuity 규약 + Audit 강화 형식 추가"
```

---

### Task 3: construction-orchestrator — 컨텍스트 로드 확장 + 재검증

**Files:**
- Modify: `skills/aidlc-construction-orchestrator/SKILL.md`

- [ ] **Step 1: Step 1 컨텍스트 로드 확장**

현재 Step 1 (31-36줄)의 파일 목록을 확장:

```markdown
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
```

- [ ] **Step 2: Step 1.5 재검증 삽입**

Step 1과 Step 2 사이에 아래 섹션 삽입:

```markdown
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
```

- [ ] **Step 3: Unit 구현 완료 시 session-summary 업데이트 추가**

구현 게이트 승인 후 (106줄 부근) 기존 "devflow-state의 Completed Units에 unit명 추가" 이후에:

```markdown
승인 후:
- devflow-state의 `## Completed Units`에 unit명 추가
- `devflow-docs/session-summary.md` 업데이트: Completed Work에 unit 추가 + `**Commit**` 필드에 현재 HEAD hash
- devflow-audit에 로깅: `[timestamp] unit-complete: [unit-name] — [commit hash]`
```

- [ ] **Step 4: 버전 업데이트**

frontmatter의 `version: 0.5.0` → `version: 0.6.0`

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-construction-orchestrator/SKILL.md
git commit -m "feat: construction-orchestrator 컨텍스트 로드 확장 + 재검증 프로토콜"
```

---

### Task 4: using-devflow — Resume Flow + Phase 전환 시 session-summary

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md`

- [ ] **Step 1: Resume Flow에 session-summary 로드 + commit hash 추가**

Resume Flow 섹션 (65-85줄)을 아래로 교체:

```markdown
### Resume Flow

1. `devflow-docs/devflow-state.md` 읽기
2. `devflow-docs/session-summary.md` 읽기 (있으면)
3. 재개 게이트 제시:
   ```
   ## aidlc — 진행 중인 작업 발견

   현재 단계: [Current Phase] > [Current Stage]
   완료된 스테이지: [list]
   마지막 완료: [session-summary의 최근 완료 항목] (있으면)

   A) 이전 작업 재개
   B) 새 작업 시작 (기존 상태 초기화)
   ```
4. A 선택 시:
   - devflow-audit에 로깅: `"Session resumed at [stage] — commit: [git rev-parse --short HEAD]"`
   - `## Current Phase` 확인하여 해당 Phase Orchestrator 호출:
     - `INCEPTION` → `aidlc-inception-orchestrator` 호출
     - `CONSTRUCTION` → `aidlc-construction-orchestrator` 호출
5. B 선택 시:
   - 기존 state를 `devflow-state-archived-[timestamp].md`로 이름 변경
   - 기존 session-summary를 `session-summary-archived-[timestamp].md`로 이름 변경 (있으면)
   - New Flow 진행
```

- [ ] **Step 2: INCEPTION 완료 시 session-summary 업데이트 추가**

`### INCEPTION 완료 시` 섹션 (89-93줄)을 아래로 교체:

```markdown
### INCEPTION 완료 시

`aidlc-inception-orchestrator`가 INCEPTION 완료를 반환하면:
1. devflow-state의 `## Current Phase`를 `CONSTRUCTION`으로 업데이트
2. `devflow-docs/session-summary.md` 업데이트:
   - `## Current State`의 Phase를 `CONSTRUCTION`으로
   - `**Commit**` 필드에 현재 HEAD hash
   - devflow-audit에 `"Phase transition: INCEPTION → CONSTRUCTION — commit: [hash]"`
3. `aidlc-construction-orchestrator` 호출
```

- [ ] **Step 3: CONSTRUCTION 완료 시 session-summary 최종 업데이트 추가**

`### CONSTRUCTION 완료 시` 섹션 (95-110줄)의 기존 step 1 뒤, step 2 (devflow-audit 로깅) 앞에 session-summary 업데이트를 삽입:

```markdown
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
```

- [ ] **Step 4: 버전 업데이트**

frontmatter의 `version: 0.4.0` → `version: 0.5.0`

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-using-devflow/SKILL.md
git commit -m "feat: using-devflow Resume Flow에 session-summary 로드 + Phase 전환 시 업데이트"
```

---

## Chunk 2: 나머지 스킬 + 마무리

### Task 5: inception-orchestrator — 스테이지 완료 시 session-summary 업데이트

**Files:**
- Modify: `skills/aidlc-inception-orchestrator/SKILL.md`

- [ ] **Step 1: The Orchestration Loop에 session-summary 업데이트 추가**

`### Step B: 결과 표시 + 로깅` 섹션 (37-39줄) 뒤에 아래 추가:

```markdown
### Step B-1: session-summary 업데이트

게이트 승인 후 `devflow-docs/session-summary.md`를 업데이트한다:
- 파일이 없으면 신규 생성 (`_shared/patterns/session-continuity.md`의 템플릿 참조)
- `## Completed Work > ### INCEPTION`에 완료 스테이지 추가: `- [x] [stage-name] — [핵심 결과 한 줄]`
- `## Current State`의 Stage 필드 업데이트
- `## Key Decisions`에 게이트 선택 기록 (결정 이유 포함)
- `**Commit**` 필드에 현재 HEAD hash
```

- [ ] **Step 2: 버전 업데이트**

frontmatter의 `version: 0.6.0` → `version: 0.7.0`

- [ ] **Step 3: 커밋**

```bash
git add skills/aidlc-inception-orchestrator/SKILL.md
git commit -m "feat: inception-orchestrator 스테이지 완료 시 session-summary 업데이트"
```

---

### Task 6: executing-plans — 세션 재개 확장

**Files:**
- Modify: `skills/aidlc-executing-plans/SKILL.md`

- [ ] **Step 1: 세션 재개 섹션 교체**

`## 세션 재개` 섹션 (54-58줄)을 아래로 교체:

```markdown
## 세션 재개

1. `devflow-docs/session-summary.md` 로드 (있으면) — 이전 세션 맥락 확인
2. 체크박스 `[x]` 파싱으로 완료 태스크 식별
3. devflow-audit 교차 확인
4. 재검증 (독립 실행 시에만):
   - construction-orchestrator 경유 호출인 경우 → 재검증 스킵 (이미 Step 1.5에서 완료)
   - 독립 실행인 경우 → 직전 완료 태스크의 테스트 실행
   - 통과 → 다음 태스크부터 재개
   - 실패 → 사용자 게이트:
     ```
     ⚠️ 재검증 실패 — [task-name] 테스트 실패

     A) 전체 테스트 스위트 실행
     B) systematic-debugging으로 조사
     ```
   - debugging 완료 후 재검증 재실행
5. 완료 태스크 건너뛰고 다음부터 재개
```

- [ ] **Step 2: 버전 업데이트**

frontmatter의 `version: 0.1.0` → `version: 0.2.0`

- [ ] **Step 3: 커밋**

```bash
git add skills/aidlc-executing-plans/SKILL.md
git commit -m "feat: executing-plans 세션 재개에 summary 로드 + 재검증 추가"
```

---

### Task 7: workflow-planning — TDD 참조 추가

**Files:**
- Modify: `skills/aidlc-workflow-planning/SKILL.md`

- [ ] **Step 1: Stage Depths 템플릿에 TDD 참조 추가**

`## Stage Depths` 템플릿 (111-115줄)에서 code-generation 항목 변경:

```markdown
## Stage Depths
- application-design: [Minimal | Standard | Comprehensive]
- units-generation: [Minimal | Standard | Comprehensive]
- code-generation: [Minimal | Standard | Comprehensive] (TDD protocol 적용 — _shared/tdd-protocol.md)
- build-and-test: [Minimal | Standard | Comprehensive]
```

- [ ] **Step 2: 버전 업데이트**

frontmatter의 `version: 0.6.0` → `version: 0.7.0`

- [ ] **Step 3: 커밋**

```bash
git add skills/aidlc-workflow-planning/SKILL.md
git commit -m "feat: workflow-planning Stage Depths에 TDD protocol 참조 추가"
```

---

### Task 8: plugin.json 버전 + README 업데이트

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `README.md`

- [ ] **Step 1: plugin.json 버전 업데이트**

`version: "0.8.0"` → `version: "0.9.0"`

- [ ] **Step 2: README에 session-continuity 기능 반영**

Features 또는 스킬 목록 테이블에 session-continuity 관련 내용 추가:
- `_shared/patterns/session-continuity.md` — 세션 재개 시 아티팩트 자동 로딩 + session-summary + 재검증

변경 사항 요약:
- 세션 재개 시 이전 Phase 핵심 산출물 자동 로드
- session-summary.md로 세션 간 맥락 인수인계
- CONSTRUCTION 재개 시 직전 unit 테스트 재검증
- audit 로그에 결정 이유 + commit hash 기록

- [ ] **Step 3: 커밋**

```bash
git add .claude-plugin/plugin.json README.md
git commit -m "chore: bump plugin version to 0.9.0 + README session-continuity 반영"
```
