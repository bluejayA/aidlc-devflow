# Brainstorming 패턴 반영 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** superpowers:brainstorming의 핵심 패턴(Complexity Declaration, Approach Proposal, Ambiguity Resolution Loop, 2단계 설계 승인)을 aidlc 오케스트레이터 중심 아키텍처에 맞게 SKILL.md 4개 파일에 반영한다.

**Complexity:** Comprehensive

**Architecture:** 역할 분리 하이브리드 — 오케스트레이터(`aidlc-using-devflow`)가 macro-level 흐름(Complexity Declaration Gate, Approach Proposal Gate, Open Questions Gate)을 담당하고, 각 stage 스킬이 domain-level 대화(Ambiguity Loop, one-at-a-time Q&A, 2단계 설계)를 담당한다. 기존 `return_behavior: stop-no-gate` 원칙을 모든 스킬에서 유지한다. 스킬 간 파라미터 전달은 호출 인라인 신호(primary) + devflow-state fallback(secondary) 방식을 사용한다.

**Tech Stack:** Markdown (SKILL.md 프롬프트 파일), bash (grep 검증)

**Spec:** `docs/plans/2026-03-12-brainstorming-pattern-adoption-design.md`

---

## Chunk 1: aidlc-workflow-planning 개선

### Task 1: workflow-planning — 2-3개 접근법 생성

**Files:**
- Modify: `skills/aidlc-workflow-planning/SKILL.md`

- [ ] **Step 1: 현재 상태 확인 (실패 기준 정의)**

현재 SKILL.md에 단일 권고안만 있음을 확인:
```bash
grep -n "Approaches\|A안\|B안\|접근법" skills/aidlc-workflow-planning/SKILL.md
```
Expected: 결과 없음 (아직 접근법 생성 로직 없음)

- [ ] **Step 2: Step 2 교체 — 단일 권고 → 접근법 2-3개 생성**

`skills/aidlc-workflow-planning/SKILL.md`의 `### Step 2: Recommend stages` 섹션을 아래로 교체:

```markdown
### Step 2: Generate approaches (2-3개)

요구사항과 workspace를 기반으로 접근법을 생성한다.

**접근법 개수 기준 (complexity 연동)**:
- Comprehensive complexity → 3개
- Minimal / Standard complexity → 2개

complexity는 호출 텍스트 또는 `devflow-docs/devflow-state.md`의 `## Complexity` 필드에서 확인.

**항상 포함해야 하는 접근법**:
- "빠른/간결" 접근법: application-design 스킵, Minimal depth 위주
- "안전한/완전" 접근법: application-design 포함, Standard+ depth 위주
- (3개인 경우) 중간 접근법: 상황에 맞게 구성

**접근법 간 실질적 차이 필수**: 스테이지 포함 여부 또는 depth가 달라야 함.

각 접근법 형식:
```
### [A안 | B안 | C안]) [접근법명] [(권장)]
- 포함 스테이지: [list]
- 깊이: [Minimal | Standard | Comprehensive]
- 적합: [한 줄]
- 주의: [한 줄]
```
```

- [ ] **Step 3: Return to Orchestrator 형식 업데이트**

`## Return to Orchestrator` 섹션의 반환 형식을 접근법 목록 포함으로 업데이트:

```markdown
## Return to Orchestrator

STOP here. No approval gate — orchestrator handles approach selection, state update, and routing.

```
[workflow-planning 결과]
- 생성된 접근법: [A안명] / [B안명] / ([C안명])
- 권장 접근법: [A안 | B안 | C안]
- 접근법 상세: (위 ## Approaches 섹션 참조)
- 산출물: devflow-docs/inception/workflow-plan.md (Selected Approach 확정 후 오케스트레이터가 업데이트)
```
```

- [ ] **Step 4: workflow-plan.md 아티팩트 형식 확장**

`### Step 4: Save artifact` 섹션의 workflow-plan.md 형식을 아래로 교체:

```markdown
### Step 4: Save artifact (Approaches 섹션 포함)

Create `devflow-docs/inception/workflow-plan.md`:

```markdown
# Workflow Plan

**Timestamp**: [ISO 8601]
**Selected Approach**: TBD (오케스트레이터 gate에서 사용자 선택 후 업데이트)

## Approaches Considered
- A안) [접근법명] — [한 줄 요약]
- B안) [접근법명] — [한 줄 요약]
- (C안) [접근법명] — [한 줄 요약]

## Approved Stages
### CONSTRUCTION
- application-design: [included | skipped] — [reason]
- units-generation: [included | skipped] — [reason]
- code-generation: included — always
- build-and-test: included — always

## Stage Depths
- application-design: [Minimal | Standard | Comprehensive]
- units-generation: [Minimal | Standard | Comprehensive]
- code-generation: [Minimal | Standard | Comprehensive]
- build-and-test: [Minimal | Standard | Comprehensive]
```

**중요**: `## Approved Stages`는 선택된 접근법 기준으로 작성한다.
오케스트레이터가 선택을 받은 후 `**Selected Approach**` 필드를 업데이트한다.
오케스트레이터 Routing Table은 `## Approved Stages` 이하만 파싱한다.
```

- [ ] **Step 5: Visualization을 선택된 접근법 기준으로 생성하도록 Step 3 수정**

`### Step 3: Generate workflow visualization` 섹션 끝에 아래 주석 추가:

```markdown
**주의**: Visualization은 A안(권장) 기준으로 생성한다.
선택된 접근법이 다를 경우 오케스트레이터가 재요청할 수 있다.
스킵된 스테이지는 `⏭ [stage] — 스킵 (A안 기준)` 형식으로 표시한다.
```

- [ ] **Step 6: 검증**

```bash
grep -n "Approaches\|A안\|B안\|Complexity\|접근법" skills/aidlc-workflow-planning/SKILL.md
```
Expected: `## Approaches Considered`, `A안`, `B안`, `Complexity 연동` 등 존재

- [ ] **Step 7: 커밋**

```bash
git add skills/aidlc-workflow-planning/SKILL.md
git commit -m "feat(workflow-planning): 단일 권고안 → 2-3개 접근법 생성으로 변경

- complexity 연동: Comprehensive=3개, 그 외=2개
- 항상 빠른/안전 접근법 포함
- workflow-plan.md에 Approaches Considered 섹션 추가
- Selected Approach 필드 추가 (오케스트레이터가 gate 이후 업데이트)
- Approved Stages는 선택된 접근법 기준 유지 (파싱 호환성 보장)"
```

---

## Chunk 2: aidlc-requirements-analysis 개선

### Task 2: requirements-analysis — Complexity 수신 + QUESTIONS 모드

**Files:**
- Modify: `skills/aidlc-requirements-analysis/SKILL.md`

- [ ] **Step 1: 현재 상태 확인**

```bash
grep -n "QUESTIONS\|Complexity.*오케스트레이터\|인라인\|fallback" skills/aidlc-requirements-analysis/SKILL.md
```
Expected: 결과 없음

- [ ] **Step 2: Step 1을 Complexity 수신 로직으로 교체**

`### Step 1: Assess complexity` 섹션 전체를 아래로 교체:

```markdown
### Step 1: Load complexity

**호출 텍스트에서 complexity 확인 (Primary)**:
호출 텍스트에 `Complexity: [level]` 패턴이 있으면 그 값을 사용:
- "aidlc-requirements-analysis 실행. Complexity: Standard" → Standard 사용
- "[Complexity: Standard] 오케스트레이터에서 확정된 복잡도로 분석합니다." 표시

**devflow-state에서 확인 (Fallback)**:
호출 텍스트에 complexity 정보가 없으면 `devflow-docs/devflow-state.md`의 `## Complexity` 필드를 읽는다.
해당 필드도 없으면 기존 기준으로 자체 판단:

**Choose Minimal if ALL of:**
- Single, clearly defined feature
- No ambiguity in requirements
- No cross-component dependencies
- Low risk (reversible, isolated)

**Choose Comprehensive if ANY of:**
- Multiple components or services affected
- High risk or irreversible changes
- Ambiguous requirements
- External integrations involved
- Performance or security critical

**Otherwise: Standard**
```

- [ ] **Step 3: QUESTIONS 모드 추가 (파일 맨 앞 ## Execute 위에 삽입)**

`## Execute` 섹션 바로 위에 아래 섹션 삽입:

```markdown
## Execution Modes

### Normal Mode (기본)
일반 호출. Step 1부터 순서대로 실행.

### QUESTIONS Mode
호출 텍스트에 `QUESTIONS` 키워드 포함 시 활성화:
`"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"`

QUESTIONS 모드에서는:
1. `devflow-docs/inception/requirements.md` 읽기
2. `## Open Questions` 섹션의 미해결 질문만 one-at-a-time으로 처리
3. 답변을 `## Assumptions` 또는 해당 요구사항 섹션에 반영
4. `requirements.md` 업데이트 후 STOP

Step 1, 2, 3, 4는 실행하지 않는다.
```

- [ ] **Step 4: 검증**

```bash
grep -n "QUESTIONS\|Complexity.*Primary\|Fallback\|devflow-state" skills/aidlc-requirements-analysis/SKILL.md
```
Expected: `QUESTIONS`, `Primary`, `Fallback`, `devflow-state` 키워드 존재

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-requirements-analysis/SKILL.md
git commit -m "feat(requirements-analysis): Complexity 수신 + QUESTIONS 모드 추가

- 호출 인라인 신호(Primary) + devflow-state fallback(Secondary) 방식
- QUESTIONS 모드: 미해결 질문만 처리 후 STOP (재실행 부분 실행 지원)"
```

### Task 3: requirements-analysis — Ambiguity Loop + Standard 핵심 질문

**Files:**
- Modify: `skills/aidlc-requirements-analysis/SKILL.md`

- [ ] **Step 1: 현재 상태 확인**

```bash
grep -n "Ambiguity\|모호성\|Standard.*질문\|그냥 진행\|가정.*확정" skills/aidlc-requirements-analysis/SKILL.md
```
Expected: 결과 없음

- [ ] **Step 2: Step 2에 Ambiguity Resolution Loop 추가**

기존 `### Step 2: Interpretation check (Minimal 제외)` 섹션 끝(선택 후)에 아래 내용 추가:

```markdown
#### Ambiguity Resolution Loop (Standard / Comprehensive)

해석 선택 후, 다음 모호성 신호를 탐지한다:
- "~하거나", "둘 다", "상황에 따라", "아직 모르겠어", "적당히"
- 설계 결정을 내리기에 불충분한 답변 (조건부 표현, 수치 없는 모호한 표현)

**신호 감지 시**: 후속 질문 ONE at a time:
```
[이전 답변]을 더 구체화해야 합니다.
A와 B 중에서 상충할 때 어느 쪽을 우선하시겠어요?
```

모호성이 해소될 때까지 반복.

**사용자가 "그냥 진행해" 또는 "계속해" 요청 시**:
- 해소되지 않은 항목을 가정으로 확정
- requirements.md의 `## Assumptions`에 기록
- 반환 텍스트에 "가정으로 처리된 항목: [N]개 — [목록]" 포함
- STOP (승인 대기 없음 — 오케스트레이터 gate에서 표시)
```

- [ ] **Step 3: Standard depth에 핵심 질문 Step 추가**

`#### Standard` 섹션에 기존 4개 스텝 뒤에 아래 추가:

```markdown
5. 핵심 질문 (최대 2개, one at a time): 요구사항에서 설계 방향을 바꿀 수 있는 불확실성이 있으면 질문. 없으면 스킵.
   - 처리 방식: "실시간 처리가 필요한가요, 배치로 충분한가요?"
   - 사용자 유형: "단일 사용자인가요, 다중 사용자인가요?"
   - 각 답변 후 Ambiguity Resolution Loop 발동 여부 판단.
```

- [ ] **Step 4: Depth별 질문 정책 테이블 추가**

SKILL.md 내부의 `### Step 4: Ask clarifying questions (Comprehensive only)` 섹션 헤더 **바로 앞**에 삽입.
**(주의: 여기서 "Step 4"는 플랜의 Task 3 Step 4가 아니라, requirements-analysis SKILL.md 내부 섹션 헤더를 가리킴)**

```markdown
### Depth별 질문 정책

| Depth | 해석 분기 | 핵심 질문 | Ambiguity Loop |
|-------|-----------|-----------|----------------|
| Minimal | 없음 | 없음 | 없음 |
| Standard | 있음 | 최대 2개 (each → loop) | 있음 |
| Comprehensive | 있음 | 제한 없음 (each → loop) | 있음 |
```

- [ ] **Step 5: Return to Orchestrator 형식에 가정 항목 필드 추가**

`## Return to Orchestrator` 반환 형식에 아래 필드 추가:

```markdown
- 가정으로 처리된 항목: [0개 | N개 — 항목명 목록]
```

- [ ] **Step 6: 검증**

```bash
grep -n "Ambiguity\|그냥 진행\|가정으로 처리\|최대 2개\|Depth별" skills/aidlc-requirements-analysis/SKILL.md
```
Expected: 모든 키워드 존재

- [ ] **Step 7: 커밋**

```bash
git add skills/aidlc-requirements-analysis/SKILL.md
git commit -m "feat(requirements-analysis): Ambiguity Loop + Standard 핵심 질문 추가

- Standard/Comprehensive: 해석 분기 후 Ambiguity Resolution Loop 적용
- Standard: 핵심 질문 최대 2개 (one at a time, 각 답변 후 loop 판단)
- 진행 요청 시 가정 확정 → requirements.md Assumptions 기록 후 STOP
- Depth별 질문 정책 테이블 추가"
```

---

## Chunk 3: aidlc-using-devflow 오케스트레이터 변경

> **WIP 커밋 참고**: Task 4, 5, 6은 모두 동일 파일(`skills/aidlc-using-devflow/SKILL.md`)을 수정한다. 각 Task의 커밋은 해당 gate만 추가된 중간 상태(WIP)이며, Task 6 커밋 완료 후 3개 gate가 모두 반영된 최종 상태가 된다.

### Task 4: orchestrator — Complexity Declaration Gate (변경 1A)

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md`

- [ ] **Step 1: 현재 workspace-detection gate 위치 확인**

```bash
grep -n "workspace-detection 완료\|Complexity\|복잡도 판단" skills/aidlc-using-devflow/SKILL.md
```
Expected: `workspace-detection 완료` 관련 gate는 있지만 `복잡도 판단` 없음

- [ ] **Step 2: devflow-state Complexity 필드 추가 정의**

`### Step 3: Initialize state and audit` 섹션에서 초기 state 생성 부분에 아래 필드 추가:

```markdown
- `## Complexity` → (workspace-detection 이후 Complexity Declaration Gate에서 결정)
```

- [ ] **Step 3: Complexity Declaration Gate 삽입 (I-4 해소 — Greenfield/Brownfield 양쪽)**

`aidlc-workspace-detection 전용 게이트` 이후 `Wait for user selection.` 처리 완료 후 Step E 진입 **이전**에 삽입한다. Greenfield(경로 입력 완료)와 Brownfield(B 선택) **두 경로 모두** 이 gate를 거친다. 구체적 삽입 위치: "Proceed to Step E." 또는 "Step E로 진행" 텍스트 **바로 앞**.

```markdown
**[Complexity Declaration] workspace-detection 승인 후, requirements-analysis 호출 전:**

workspace.md 결과와 사용자의 원래 요청을 기반으로 complexity를 판단하여 아래 gate 제시:

```
## 복잡도 판단

복잡도: **[Minimal | Standard | Comprehensive]**
이유: [한 줄 — 예: "다중 컴포넌트 + 외부 API 연동 포함"]

A) 이 복잡도로 요구사항 분석 진행
B) 복잡도 조정 (원하는 복잡도를 알려주세요)
```

- A 선택 시 → 확정된 complexity를 devflow-state `## Complexity`에 기록 후 Step E 진행
- B 선택 시 → 사용자가 입력한 complexity로 업데이트 후 Step E 진행

requirements-analysis 호출 시 인라인 신호 포함:
`"aidlc-requirements-analysis 실행. Complexity: [확정된 값]"`
```

- [ ] **Step 4: 검증**

```bash
grep -n "복잡도 판단\|Complexity Declaration\|## Complexity\|Complexity:.*실행" skills/aidlc-using-devflow/SKILL.md
```
Expected: 모든 키워드 존재

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-using-devflow/SKILL.md
git commit -m "feat(orchestrator): Complexity Declaration Gate 추가 (변경 1A)

- workspace-detection 승인 후, requirements-analysis 호출 전에 삽입
- 확정된 complexity → devflow-state ## Complexity 기록
- requirements-analysis 호출 시 인라인 신호로 전달"
```

### Task 5: orchestrator — Approach Proposal Gate (변경 1B)

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md`

- [ ] **Step 1: 현재 workflow-planning 전용 게이트 위치 확인**

```bash
grep -n "workflow-planning 전용\|Construction 진입 방식\|A안\|접근법 선택" skills/aidlc-using-devflow/SKILL.md
```
Expected: `Construction 진입 방식` gate는 있지만 `접근법 선택` gate 없음

- [ ] **Step 2: workflow-planning 전용 게이트 전체 교체**

기존 `**aidlc-workflow-planning 전용 게이트:**` 섹션을 아래로 교체.
**중요**: 교체 후 내용에 Task 6(requirements-analysis gate)의 앵커 텍스트가 이 섹션과 분리된 별도 위치에 있으므로, Step D 전체 구조를 기준으로 작업한다.

교체 후 `**aidlc-workflow-planning 전용 게이트:**` 섹션의 최종 형태:

~~~markdown
**aidlc-workflow-planning 전용 게이트 (2단계):**

**1단계 — 접근법 선택 gate:**

skill이 반환한 접근법 목록을 표시하고 선택받는다:

```
## aidlc-workflow-planning 완료 — 접근법 선택

**A안) [A안 접근법명]** (권장)
포함: [스테이지 목록] | 깊이: [depth]
적합: [한 줄] | 주의: [한 줄]

**B안) [B안 접근법명]**
포함: [스테이지 목록] | 깊이: [depth]
적합: [한 줄] | 주의: [한 줄]

([C안) [C안 접근법명] — Comprehensive complexity인 경우만]
포함: [스테이지 목록] | 깊이: [depth]
적합: [한 줄] | 주의: [한 줄])

1) A안으로 진행
2) B안으로 진행
(3) C안으로 진행)
X) 변경 요청
```

- 선택 후: `devflow-docs/inception/workflow-plan.md`의 `**Selected Approach**` 필드를 선택된 안으로 업데이트
- 선택 후: devflow-state `## Selected Approach` 필드 기록
- X 선택 시: `aidlc-workflow-planning` 재호출

**2단계 — 개발 환경 설정 gate (기존 worktree gate 유지):**

```
## 개발 환경 설정

A) 변경 요청
B) Git Worktree 생성 후 시작 (격리 개발 — main 브랜치 보호)
C) 현재 브랜치에서 바로 시작
```

(이하 B/C 선택 처리 로직은 기존과 동일)
~~~

**Task 6의 앵커 확인**: Task 6 Step 2는 `**Step D: Present approval gate**` 섹션 내에서 `**aidlc-requirements-analysis 전용 게이트:**` 삽입 위치를 찾는다. 위 교체 후에도 `**Step D: Present approval gate**` 섹션 헤더는 그대로 유지되므로 Task 6 삽입에 영향 없음.

- [ ] **Step 3: Stage Routing Table Note 추가 (C-2 해소)**

`### Stage Routing Table` → `| aidlc-workflow-planning | ...` 행 아래에 주석 추가:

```markdown
**Note (workflow-planning)**: workflow-planning 라우팅은 `## Approved Stages` 이하만 파싱한다.
`## Approaches Considered`, `**Selected Approach**` 섹션은 라우팅 파싱에 영향 없음.
```

**Task 7 Step 6과의 공존**: Task 7 Step 6에서 `aidlc-application-design` 행 교체 후 아래 Note도 추가된다. 두 Note는 서로 다른 위치(workflow-planning 행 아래 / application-design 행 아래)에 삽입되어 충돌하지 않는다. 최종 Routing Table Note 구조:
- `| aidlc-workflow-planning | ...` 아래: **Note (workflow-planning)** (이 Task에서 추가)
- `| aidlc-application-design (DETAIL) | ...` 아래: **Note (application-design)** (Task 7 Step 6에서 추가)

- [ ] **Step 4: 검증**

```bash
grep -n "접근법 선택\|Selected Approach\|개발 환경 설정\|1단계\|2단계" skills/aidlc-using-devflow/SKILL.md
```
Expected: 모든 키워드 존재. `Construction 진입 방식` 키워드는 사라졌거나 `개발 환경 설정`으로 교체됨.

- [ ] **Step 5: 커밋**

```bash
git add skills/aidlc-using-devflow/SKILL.md
git commit -m "feat(orchestrator): Approach Proposal Gate 추가 (변경 1B)

- workflow-planning 전용 gate를 2단계로 교체
  1단계: 접근법 선택 (A안/B안/C안)
  2단계: 개발 환경 설정 (기존 worktree gate 유지)
- 선택된 접근법 → workflow-plan.md + devflow-state 기록
- Routing Table 파싱은 ## Approved Stages만 사용 (호환성 유지)"
```

### Task 6: orchestrator — Open Questions Follow-up Gate (변경 1C)

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md`

- [ ] **Step 1: 현재 requirements-analysis gate 위치 확인**

```bash
grep -n "requirements-analysis 완료\|Open Questions\|미해결\|QUESTIONS" skills/aidlc-using-devflow/SKILL.md
```
Expected: `requirements-analysis 완료` gate는 있지만 `미해결 질문` 분기 없음

- [ ] **Step 2: requirements-analysis 전용 gate 추가 (C-1 앵커 확인)**

`**Step D: Present approval gate**` 섹션 안에서 `**aidlc-workspace-detection 전용 게이트:**` 및 `**aidlc-workflow-planning 전용 게이트:**` 블록 **아래**에 새 블록으로 추가한다.
Task 5 완료 후에도 `**Step D: Present approval gate**` 헤더는 그대로 존재하므로 앵커 안전.

```markdown
**aidlc-requirements-analysis 전용 게이트:**

반환 텍스트에서 `열린 질문: [N]개` 패턴을 확인한다.
**패턴 매칭 실패 시 (I-3 해소)**: LLM이 "없음", "0개", 다른 표현을 사용한 경우 N=0으로 처리하고 표준 gate 진행.

**N > 0인 경우 (미해결 질문 있음):**

```
## aidlc-requirements-analysis 완료

⚠️ 미해결 질문이 {N}개 있습니다.
[가정으로 처리된 항목이 있는 경우:]
ℹ️ 가정으로 처리된 항목: [목록]

A) 지금 답변 (미해결 질문만 처리 후 계속)
B) 현재 가정으로 진행 (가정은 requirements.md에 기록됨)
C) 변경 요청
```

- A 선택 시: 아래 신호로 재호출:
  `"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"`
  결과 반환 후 다시 이 gate로 복귀.
- B 선택 시: 표준 gate (B) 다음 단계 진행으로 처리.
- C 선택 시: `aidlc-requirements-analysis` 전체 재호출.

**N == 0인 경우 (미해결 질문 없음):**

[가정 항목이 있는 경우:]
```
## aidlc-requirements-analysis 완료

ℹ️ 가정으로 처리된 항목:
- [가정 1]
- [가정 2]

A) 변경 요청  B) 다음 단계 진행
```

[가정 항목도 없는 경우:]
```
## aidlc-requirements-analysis 완료

A) 변경 요청  B) 다음 단계 진행
```
```

- [ ] **Step 3: 검증**

```bash
grep -n "미해결\|QUESTIONS.*재호출\|열린 질문.*패턴\|가정으로 처리" skills/aidlc-using-devflow/SKILL.md
```
Expected: 모든 키워드 존재

- [ ] **Step 4: 커밋**

```bash
git add skills/aidlc-using-devflow/SKILL.md
git commit -m "feat(orchestrator): Open Questions Follow-up Gate 추가 (변경 1C)

- requirements-analysis 반환 후 열린 질문 수 조건부 분기
- N>0: QUESTIONS 모드 재호출 or 가정으로 진행 선택
- 가정 항목은 gate에 인라인 표시
- stop-no-gate 원칙 유지 (승인은 오케스트레이터 gate에서만)"
```

---

## Chunk 4: aidlc-application-design 2단계 모드

### Task 7: application-design — LIST/DETAIL 2단계 실행 모드

**Files:**
- Modify: `skills/aidlc-application-design/SKILL.md`
- Modify: `skills/aidlc-using-devflow/SKILL.md` (Routing Table 변경)

- [ ] **Step 1: 현재 상태 확인**

```bash
grep -n "DETAIL\|LIST\|목록.*초안\|2단계\|컴포넌트 목록" skills/aidlc-application-design/SKILL.md
```
Expected: 결과 없음

- [ ] **Step 2: Execution Modes 섹션 추가 (## Execute 위에 삽입)**

```markdown
## Execution Modes

### LIST Mode (기본)
일반 호출. 컴포넌트 목록만 생성하고 STOP.
모든 depth에서 `application-design.md`에 컴포넌트 목록을 저장한다 (Minimal 포함).

### DETAIL Mode
호출 텍스트에 `DETAIL` 키워드 포함 시 활성화:
`"aidlc-application-design: DETAIL — 승인된 목록으로 상세 설계 진행"`

DETAIL 모드에서는:
1. `devflow-docs/inception/application-design.md` 읽기 (목록 단계 결과)
2. depth에 따라 상세 설계 진행:
   - **Standard**: 주요 인터페이스 + 의존성
   - **Comprehensive**: 전체 인터페이스 + 의존성 + 데이터 소유 + 상호작용 다이어그램
3. `application-design.md` 업데이트 후 STOP

depth는 호출 텍스트 또는 `devflow-docs/devflow-state.md`의 `## Selected Approach` 필드에서 확인.

**Minimal depth**: LIST Mode만 실행. DETAIL 호출 없음.
```

- [ ] **Step 3: Step 2를 컴포넌트 목록 생성으로 제한**

기존 `### Step 2: Design components` 섹션을 LIST/DETAIL 분기로 교체:

```markdown
### Step 2: Generate component list (LIST Mode)

DETAIL 모드인 경우 Step 4로 건너뛴다.

각 새 컴포넌트에 대해 아래 정보만 수집 (상세 설계는 DETAIL 모드에서):
- **Name**: 컴포넌트명
- **Responsibility**: 한 줄 책임
- **Type**: Service | Repository | Adapter | Controller | Util 중 하나

반환 형식:
```markdown
## 컴포넌트 목록 (초안)

| 컴포넌트 | 책임 | 타입 |
|---------|------|------|
| [Name] | [한 줄 책임] | [Type] |

총 [N]개 컴포넌트
```
```

- [ ] **Step 4: Step 3 → DETAIL Mode 상세 설계로 교체**

기존 `### Step 3: Design interactions` 섹션을 아래로 교체:

```markdown
### Step 3: Save LIST artifact and STOP (LIST Mode)

LIST 모드에서는 컴포넌트 목록을 `devflow-docs/inception/application-design.md`에 저장 후 STOP.
**Minimal depth 포함 모든 depth에서 저장 필수** (이후 스킬이 이 파일을 참조).

```markdown
# Application Design

**Mode**: LIST (목록 단계)
**Timestamp**: [ISO 8601]

## 컴포넌트 목록

| 컴포넌트 | 책임 | 타입 |
|---------|------|------|
| [Name] | [한 줄 책임] | [Type] |
```

→ Return to Orchestrator (목록 반환)

### Step 4: DETAIL Mode — 상세 설계

DETAIL 모드에서만 실행.

**Standard depth**:
각 컴포넌트에 대해:
- **Public interface**: 주요 메서드/API (2-3개)
- **Dependencies**: 의존하는 컴포넌트

**Comprehensive depth**:
각 컴포넌트에 대해:
- **Public interface**: 전체 메서드/API (입력, 출력, 예외)
- **Dependencies**: 의존 컴포넌트 및 방향
- **Data it owns**: 이 컴포넌트가 소유하는 데이터
- **Interactions**: 주요 시퀀스 (ASCII 다이어그램, 기본 ASCII 전용: `+`, `-`, `|`, `^`, `v`, `>`, `<`)

`application-design.md`를 업데이트하여 상세 섹션 추가:
```markdown
## 컴포넌트 상세 설계

### [ComponentName]
**Responsibility**: [한 줄]
**Interface**: [메서드 목록]
**Dependencies**: [의존 컴포넌트]
**Data Owned**: [소유 데이터] (Comprehensive만)
**Interactions**: [ASCII 다이어그램] (Comprehensive만)
```
```

- [ ] **Step 5: Return to Orchestrator를 모드별로 분기**

`## Return to Orchestrator` 섹션을 아래로 교체:

```markdown
## Return to Orchestrator

STOP here. No approval gate — orchestrator handles it.

**LIST Mode 반환:**
```
[application-design 결과 — LIST]
- 설계된 컴포넌트: [count]개
- 목록: [컴포넌트명 나열]
- 산출물: devflow-docs/inception/application-design.md (목록 단계)
※ Minimal depth: 오케스트레이터가 DETAIL 호출 없이 바로 다음 단계 진행
※ Standard/Comprehensive: 오케스트레이터가 목록 승인 후 DETAIL 호출
```

**DETAIL Mode 반환:**
```
[application-design 결과 — DETAIL]
- 상세 설계 완료: [count]개 컴포넌트
- 산출물: devflow-docs/inception/application-design.md (업데이트됨)
```
```

- [ ] **Step 6: 오케스트레이터 Routing Table에 2단계 gate 추가**

`skills/aidlc-using-devflow/SKILL.md`의 Stage Routing Table에서 `aidlc-application-design` 관련 행을 아래로 교체:

```markdown
| `aidlc-application-design` (LIST) | `aidlc-application-design` (DETAIL) | Standard/Comprehensive depth |
| `aidlc-application-design` (LIST) | `aidlc-units-generation` 또는 `aidlc-code-generation` | Minimal depth |
| `aidlc-application-design` (DETAIL) | `aidlc-units-generation` | if units-generation included in workflow-plan |
| `aidlc-application-design` (DETAIL) | `aidlc-code-generation` | if units-generation skipped |
```

그리고 `**Step D: Present approval gate**`에 application-design 전용 gate 추가:

```markdown
**aidlc-application-design (LIST) 전용 게이트:**

```
## aidlc-application-design 완료 — 컴포넌트 목록 확인

[컴포넌트 목록 표시]

A) 컴포넌트 추가/변경 요청 (LIST 재실행)
B) 이 목록으로 상세 설계 진행 (DETAIL 호출)  ← Standard/Comprehensive만
B) 다음 단계 진행  ← Minimal만
```

- A 선택 시: `aidlc-application-design` 재호출 (일반)
- B 선택 시 (Standard/Comprehensive): `"aidlc-application-design: DETAIL — 승인된 목록으로 상세 설계 진행"` 호출
- B 선택 시 (Minimal): 다음 stage로 이동
```

- [ ] **Step 7: 검증**

```bash
grep -n "LIST Mode\|DETAIL Mode\|DETAIL.*호출\|목록.*초안\|Minimal.*저장 필수" skills/aidlc-application-design/SKILL.md
grep -n "application-design.*LIST\|DETAIL.*gate\|컴포넌트 목록 확인" skills/aidlc-using-devflow/SKILL.md
```
Expected: 두 파일 모두 관련 키워드 존재

- [ ] **Step 8: 커밋**

```bash
git add skills/aidlc-application-design/SKILL.md skills/aidlc-using-devflow/SKILL.md
git commit -m "feat(application-design): LIST/DETAIL 2단계 실행 모드 추가

- LIST Mode: 컴포넌트 목록만 생성 (모든 depth에서 application-design.md 저장)
- DETAIL Mode: 상세 설계 (Standard: 인터페이스+의존성 / Comprehensive: 전체)
- Minimal: LIST만 (DETAIL 호출 없음)
- 오케스트레이터 Routing Table + application-design 전용 gate 추가"
```

---

## 최종 smoke test 시나리오

모든 Task 완료 후 아래 두 시나리오로 전체 흐름을 수동 검증한다.

### 시나리오 A: 신규 FastAPI 프로젝트 (Standard)
```
사용자: "aidlc로 FastAPI Todo API 만들어줘"

예상 흐름:
1. workspace-detection → Greenfield 판정
2. [신규] Complexity Declaration: Standard 제안 → 사용자 확인
3. requirements-analysis (Complexity: Standard 전달) → 해석 분기 확인 → 핵심 질문 1-2개
4. [신규] Open Questions gate: 미해결 없으면 표준 gate
5. workflow-planning → A안(빠른)/B안(안전) 2개 접근법 생성
6. [신규] Approach Proposal gate (1단계) → 사용자 접근법 선택
7. 개발 환경 설정 gate (2단계) → Worktree 생성 or 현재 브랜치
8. application-design LIST → 컴포넌트 목록 gate
9. application-design DETAIL → 상세 설계
10. code-generation → build-and-test
```

### 시나리오 B: 복잡한 마이크로서비스 (Comprehensive)
```
사용자: "aidlc로 주문/결제/알림 마이크로서비스 만들어줘"

예상 흐름:
1. workspace-detection → Greenfield 판정
2. [신규] Complexity Declaration: Comprehensive 제안 → 사용자 확인
3. requirements-analysis → 해석 분기 + Ambiguity Loop + 다수 질문
4. [신규] Open Questions gate: N>0이면 QUESTIONS 모드 재실행 option
5. workflow-planning → A안/B안/C안 3개 접근법 생성
6. [신규] Approach Proposal gate → 사용자 선택
7. application-design LIST → 목록 확인
8. application-design DETAIL (Comprehensive) → 전체 설계
9. units-generation → code-generation × 3 → build-and-test
```

각 시나리오에서 새로 추가된 gate가 정상 표시되고, 선택 흐름이 올바르게 작동하는지 확인한다.
