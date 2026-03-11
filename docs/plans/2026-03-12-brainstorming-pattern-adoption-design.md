# aidlc 플러그인 개선 설계: Brainstorming 패턴 반영

**작성일**: 2026-03-12
**Complexity**: Comprehensive
**범위**: INCEPTION 단계 + 오케스트레이터 (`aidlc-using-devflow`)
**접근법**: C — 역할 분리 하이브리드

---

## 배경

superpowers:brainstorming 스킬의 핵심 패턴을 aidlc의 오케스트레이터 중심 아키텍처에 맞게 흡수한다.

brainstorming 스킬 ≈ aidlc의 INCEPTION 전체를 하나의 연속 흐름으로 처리하는 것과 구조적으로 유사하며, 가장 큰 차별점은:
- Complexity Declaration (사용자 확인)
- One question at a time + Ambiguity Resolution Loop
- 2-3개 Approach Proposal
- Section-by-section 설계 승인

### 아키텍처 원칙 (변경 없음)

- **오케스트레이터**: macro-level 흐름 제어, 게이팅, 상태 관리
- **Stage 스킬**: domain-level 실행, 결과 반환 후 STOP

---

## Assumptions

- 질문 방식은 채팅 인라인 유지 (dev-playbook의 파일 기반 방식으로 전환하지 않음)
- CONSTRUCTION 단계는 이번 개선 범위 외
- 기존 17개 스킬의 `return_behavior: stop-no-gate` 원칙 유지

## 스킬 간 파라미터 전달 패턴 (C-2 결정)

이 플러그인에서 오케스트레이터가 스킬에 파라미터를 전달하는 방식:

**Primary — 호출 시 인라인 지시**: `aidlc-code-generation`의 PART 2 신호 패턴과 동일하게 적용.

```
"aidlc-requirements-analysis 실행. Complexity: Standard"
"aidlc-application-design: DETAIL — 승인된 목록으로 상세 설계 진행"
"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"
```

**Secondary — devflow-state 백업**: 호출 신호가 없어도 스킬이 devflow-state에서 읽을 수 있도록 `## Complexity` 필드에도 기록. fallback 보장용.

스킬은 호출 텍스트에서 먼저 파라미터를 읽고, 없으면 devflow-state를 확인한다.

---

## 섹션 1: 오케스트레이터 (`aidlc-using-devflow`) 변경

### 변경 1A — Complexity Declaration Gate (신규)

**위치**: `aidlc-workspace-detection` gate 이후, `aidlc-requirements-analysis` 호출 이전

**동작**:
1. workspace.md 결과와 사용자 요청을 기반으로 AI가 complexity를 판단
2. 아래 gate 제시:

```
## 복잡도 판단

복잡도: **[Minimal | Standard | Comprehensive]**
이유: [한 줄 — 예: "다중 컴포넌트 + 외부 API 연동 포함"]

A) 이 복잡도로 요구사항 분석 진행
B) 복잡도 조정 (Minimal / Standard / Comprehensive 중 선택)
```

3. 확정된 complexity를 devflow-state에 기록
4. `aidlc-requirements-analysis` 호출 시 전달

**devflow-state 추가 필드**:
```markdown
## Complexity
[Minimal | Standard | Comprehensive]
```

**Orchestration Loop 변경 위치**: Step D (Present approval gate) — workspace-detection 전용 gate 이후에 삽입

---

### 변경 1B — Approach Proposal Gate (workflow-planning gate 교체)

**위치**: `aidlc-workflow-planning` 반환 후 기존 A/B gate 교체

**동작**: skill이 반환한 2-3개 접근법을 오케스트레이터가 선택 gate로 제시:

```
## aidlc-workflow-planning 완료 — 접근법 선택

**A안) [접근법명]** (권장)
포함: [스테이지 목록] | 깊이: [depth]
적합: [한 줄] | 주의: [한 줄]

**B안) [접근법명]**
포함: [스테이지 목록] | 깊이: [depth]
적합: [한 줄] | 주의: [한 줄]

1) A안으로 진행
2) B안으로 진행
3) 변경 요청
```

접근법 선택 후 worktree gate로 이어짐 (기존 유지):
```
## 개발 환경 설정

A) 변경 요청
B) Git Worktree 생성 후 시작 (격리 개발)
C) 현재 브랜치에서 바로 시작
```

**선택된 접근법**: devflow-state `## Selected Approach` 필드에 기록.

**오케스트레이터 SKILL.md 재작성 범위** (I-1 해소): 기존 `aidlc-workflow-planning 전용 게이트` 섹션 전체를 아래 구조로 교체:
1. Approach Proposal Gate (신규) — 접근법 선택
2. worktree gate (기존 그대로 유지)

두 gate는 순차적으로 실행되며, 1번 gate 완료 후 2번 gate 진행.

---

### 변경 1C — Open Questions Follow-up Gate (신규)

**위치**: `aidlc-requirements-analysis` 반환 후, 기존 승인 gate 이전에 조건부 삽입

**동작**: requirements-analysis 반환값의 `열린 질문: [N]개` 필드를 확인:

```
## aidlc-requirements-analysis 완료

[open_questions_count > 0인 경우]
⚠️ 미해결 질문이 {N}개 있습니다.

A) 지금 답변 (아래 신호로 재실행)
B) 현재 가정으로 진행 (가정은 requirements.md에 기록됨)
C) 변경 요청

[open_questions_count == 0인 경우]
A) 변경 요청
B) 다음 단계 진행
```

**A 선택 시 재실행 신호** (C-1 해소):
```
"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"
```

이 신호를 받은 스킬은 Step 1, 2를 건너뛰고 미해결 Open Questions만 one-at-a-time으로 처리한 후 requirements.md를 업데이트하고 STOP한다.

**open_questions_count 판단 기준**: 반환 텍스트에서 `열린 질문: [N]개` 패턴 매칭. N > 0이면 미해결로 판단.

---

## 섹션 2: `aidlc-requirements-analysis` 개선

### 변경 2A — Complexity를 오케스트레이터로부터 수신

**현재**: Step 1에서 스킬이 독자적으로 complexity 판단
**변경**: 오케스트레이터 결정값 우선 사용, 없으면 자체 판단 fallback

```markdown
## Step 1: Load complexity

오케스트레이터로부터 전달된 complexity level 확인:
- 전달값 있음 → 그대로 사용. 첫 줄 표시:
  "[Complexity: Standard] 오케스트레이터에서 확정된 복잡도로 분석합니다."
- 전달값 없음 → 기존 기준으로 자체 판단 (fallback)
```

---

### 변경 2B — Ambiguity Resolution Loop (전 depth 적용)

**현재**: Step 2 해석 분기 확인 후 루프 없이 진행
**변경**: 선택 후 모호성 탐지 → 후속 질문 루프 추가

모호성 신호:
- "~하거나", "둘 다", "상황에 따라", "아직 모르겠어", "적당히"
- 설계 결정을 내리기에 불충분한 답변

루프 동작:
```
1. 모호성 탐지 → 후속 질문 ONE at a time
2. 모호성이 해소될 때까지 반복
3. 사용자가 "그냥 진행해" 요청 시 (I-4 해소 — stop-no-gate 원칙 준수):
   - 스킬이 해소되지 않은 항목을 가정으로 확정하여 requirements.md의 ## Assumptions에 기록
   - 반환 텍스트에 "가정으로 처리된 항목: [N]개" 포함
   - STOP (승인 대기 없음 — 오케스트레이터 게이트에서 사용자에게 가정 항목 표시)
```

오케스트레이터는 반환된 가정 항목을 기존 gate에 아래와 같이 포함:
```
## aidlc-requirements-analysis 완료

ℹ️ 아래 항목은 가정으로 처리되었습니다:
- [가정 1]
- [가정 2]

A) 변경 요청  B) 다음 단계 진행
```

---

### 변경 2C — Standard depth 핵심 질문 추가

**현재**: Standard = 해석 분기 확인만
**변경**: Standard에도 최대 2개의 핵심 질문 허용

```markdown
## Step 3 (Standard): 핵심 질문 (최대 2개, one at a time)

요구사항에서 설계 방향을 바꿀 수 있는 불확실성이 있으면 질문.
없으면 스킵.

질문 대상 예시:
- 처리 방식: "실시간 처리가 필요한가요, 배치로 충분한가요?"
- 사용자 유형: "단일 사용자인가요, 다중 사용자인가요?"
- 규모: "동시 사용자 수가 어느 정도를 예상하시나요?"
```

**Standard depth에서 핵심 질문과 Ambiguity Loop 우선순위** (M-2 해소):
핵심 질문(최대 2개)을 먼저 진행하고, 각 답변 후 Ambiguity Loop 발동 여부를 판단한다.
즉 핵심 질문 → (모호하면) Ambiguity Loop → 다음 핵심 질문 → ... 순서.

### Depth별 질문 정책 요약 (변경 후)

| Depth | 해석 분기 | 핵심 질문 | Ambiguity Loop |
|-------|-----------|-----------|----------------|
| Minimal | 없음 | 없음 | 없음 |
| Standard | 있음 | 최대 2개 | 있음 (각 답변 후 판단) |
| Comprehensive | 있음 | 제한 없음 | 있음 (각 답변 후 판단) |

---

## 섹션 3: `aidlc-workflow-planning` 개선

### 변경 3A — 단일 권고 → 2-3개 접근법 생성

**현재**: Step 2에서 단일 스테이지 권고안 생성
**변경**: 2-3개 접근법 생성, 오케스트레이터가 선택 gate 제시

접근법 생성 기준 (M-3 해소 — complexity와 연동):
- 항상 "빠른/간결" 접근법 포함 (Minimal depth 위주)
- 항상 "안전한/완전" 접근법 포함 (Standard+ depth 위주)
- **Comprehensive complexity이면 3개**, 그 외(Minimal/Standard)는 2개
- 접근법 간 실질적 차이 필수 (스테이지 포함 여부, depth 차이)

반환 형식:
```markdown
## Approaches

### A안) [접근법명] (권장)
- 포함 스테이지: [list]
- 깊이: [depth]
- 적합: [한 줄]
- 주의: [한 줄]

### B안) [접근법명]
- 포함 스테이지: [list]
- 깊이: [depth]
- 적합: [한 줄]
- 주의: [한 줄]
```

---

### 변경 3B — workflow-plan.md 아티팩트 확장

```markdown
# Workflow Plan

**Timestamp**: [ISO 8601]
**Selected Approach**: [A안 | B안] — [접근법명]  ← 신규

## Approaches Considered       ← 신규
- A안) [요약] (선택됨 | 기각)
- B안) [요약] (선택됨 | 기각)

## Approved Stages
...
```

---

### 변경 3C — Visualization 선택된 접근법 기준으로 생성

```
INCEPTION
  ✅ workspace-detection
  ✅ requirements-analysis
  ⏭ workflow-planning (현재)

CONSTRUCTION [A안 — 빠른 구현]
  ➡ code-generation [Minimal]
  ➡ build-and-test [Minimal]
  ⏭ application-design — 스킵
  ⏭ units-generation — 스킵
```

---

## 섹션 4: `aidlc-application-design` 개선

### 변경 4A — 2단계 실행 모드

`aidlc-code-generation`의 PART 1/PART 2 패턴과 동일한 구조 적용.

**1차 호출 (기본)**: 컴포넌트 목록만 생성

반환 형식:
```markdown
## 컴포넌트 목록 (초안)

| 컴포넌트 | 책임 | 타입 |
|---------|------|------|
| [Name] | [한 줄 책임] | [Service | Repository | Adapter | ...] |

총 [N]개 컴포넌트
```

오케스트레이터 gate:
```
## aidlc-application-design 완료 — 컴포넌트 목록 확인

[컴포넌트 목록 표시]

A) 컴포넌트 추가/변경 요청
B) 이 목록으로 상세 설계 진행
```

**2차 호출 (B 선택 후)**:
```
"aidlc-application-design: DETAIL — 승인된 목록으로 상세 설계 진행"
```

→ 인터페이스, 의존성, 데이터 소유, 상호작용 설계 → STOP

---

### 변경 4B — Depth 연동

| Depth | 동작 |
|-------|------|
| Minimal | 목록 단계만 (DETAIL 호출 없음). **목록을 application-design.md에 저장** 후 STOP. 오케스트레이터 gate 단순화. |
| Standard | 목록 → 승인 → DETAIL (주요 인터페이스 + 의존성) → application-design.md 업데이트 |
| Comprehensive | 목록 → 승인 → DETAIL (전체 인터페이스 + 의존성 + 데이터 소유 + 상호작용 다이어그램) → application-design.md 업데이트 |

**Minimal에서도 application-design.md 저장 필수** (I-3 해소): 이후 스킬(`aidlc-units-generation`, `aidlc-code-generation`)이 이 파일을 읽으므로, 목록만 포함된 형태라도 반드시 저장한다.

---

### Stage Routing Table 변경 (오케스트레이터)

```
# 기존
application-design → units-generation (또는 code-generation)

# 변경 후
application-design (목록) → [목록 승인 gate]
  → A) 재실행
  → B) application-design (DETAIL 호출)  [Standard/Comprehensive만]
       → [상세 승인 gate]
         → A) DETAIL 재실행
         → B) units-generation (또는 code-generation)

Minimal: 목록 gate 후 바로 next stage
```

---

## 변경 파일 목록

| 파일 | 변경 유형 |
|------|-----------|
| `skills/aidlc-using-devflow/SKILL.md` | 수정 — Gate 3개 추가, Routing Table 변경, workflow-plan.md 파싱 로직 업데이트 |
| `skills/aidlc-requirements-analysis/SKILL.md` | 수정 — Complexity 수신, Ambiguity Loop, Standard 질문, QUESTIONS 모드 추가 |
| `skills/aidlc-workflow-planning/SKILL.md` | 수정 — 접근법 2-3개 생성, 아티팩트 형식 확장 |
| `skills/aidlc-application-design/SKILL.md` | 수정 — 2단계 실행 모드, Depth 연동, Minimal 아티팩트 저장 보장 |

**`aidlc-using-devflow` 파싱 로직 업데이트 상세** (I-2 해소):
`workflow-plan.md`에 `## Approaches Considered` 섹션이 추가되지만, 기존 라우팅에 사용하는 `application-design: included | skipped` 패턴은 `## Approved Stages` 섹션 아래에만 존재하도록 아티팩트 형식을 유지한다. 오케스트레이터는 `## Approved Stages` 이하만 파싱하므로 기존 Troubleshooting 로직과 충돌하지 않는다.

---

## 구현 순서 (I-5 해소 — 의존성 명확화)

```
단계 1: aidlc-workflow-planning (변경 3A, 3B, 3C)
  → 독립적. 오케스트레이터 변경 없이 단독 테스트 가능.

단계 2: aidlc-requirements-analysis (변경 2A fallback 포함, 2B, 2C, QUESTIONS 모드)
  → 독립적. 오케스트레이터 Complexity 전달 없이도 fallback으로 동작.

단계 3: aidlc-using-devflow (변경 1A, 1B, 1C + Routing Table + 파싱 업데이트)
  → 단계 1, 2 완료 후. 이 단계에서 Complexity 인라인 신호 전달 구현.
  → 단계 3 완료 시 단계 1, 2의 신규 기능이 오케스트레이터와 완전히 연결됨.

단계 4: aidlc-application-design (변경 4A, 4B)
  → 단계 3 완료 후. Routing Table의 2단계 gate 분기가 필요하므로 오케스트레이터 먼저.
```
