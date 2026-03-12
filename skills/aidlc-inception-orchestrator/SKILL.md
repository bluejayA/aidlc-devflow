---
name: aidlc-inception-orchestrator
description: INCEPTION Phase 오케스트레이터. 스테이지 순회 + 게이트 관리. Entry Orchestrator가 호출.
metadata:
  version: 0.4.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# aidlc-inception-orchestrator

<!-- INCEPTION Phase 오케스트레이터: 스테이지 순서 + 게이트 관리 -->
<!-- 게이트 패턴 참조: _shared/gate-patterns.md -->

## INCEPTION 스테이지 순서

```
workspace-detection → [Complexity Gate] → requirements-analysis → [Open Questions Gate]
  → workflow-planning → [Approach Proposal Gate] → application-design (조건부) → 완료
```

## The Orchestration Loop

아래 순서대로 스테이지를 순회한다. 각 스테이지에서:

### Step A: 스킬 호출

devflow-state의 `## Current Stage`를 업데이트하고 해당 스킬을 호출한다.
호출 시 필요한 파라미터는 인라인으로 전달한다:
- Complexity: `"Complexity: [level]"`
- Depth: `"Depth: [level]"`

### Step B: 결과 표시 + 로깅

스킬 반환값을 사용자에게 표시하고, devflow-audit에 기록한다.

### Step C: 게이트 제시

아래 게이트 정의에 따라 사용자에게 선택지를 제시한다.

### Step D: 라우팅

사용자 선택에 따라 다음 스테이지를 결정한다.

---

## 게이트 정의

### 1. workspace-detection 게이트 [조건부 게이트]

스킬 반환값에서 Greenfield/Brownfield 확인.

**Greenfield 경로:**
```
[workspace-detection 결과 표시]
A) 경로 수정 → workspace-detection 재호출
B) 확인, 다음 단계 진행 → Complexity Declaration Gate
```

**Brownfield 경로:**
```
[workspace-detection 결과 표시]
A) 분석 범위 수정 → workspace-detection 재호출
B) 확인, 다음 단계 진행 → Complexity Declaration Gate
```

### 2. Complexity Declaration Gate

workspace-detection 결과를 기반으로 복잡도를 선언.

```
이 작업의 복잡도를 **[Minimal/Standard/Comprehensive]**로 판단했습니다.
이유: [한 줄 이유]

다르게 조정하시겠습니까?

A) 조정 요청 → 사용자 입력 받아 반영
B) 승인 → devflow-state의 ## Complexity 업데이트 → requirements-analysis 호출
```

Complexity 값을 requirements-analysis 호출 시 인라인으로 전달: `"Complexity: [level]"`

### 3. requirements-analysis 게이트 [조건부 게이트]

패턴: `열린 질문: [N]개`

**패턴 매칭 실패 시**: LLM이 "없음", "0개", 다른 표현을 사용한 경우 N=0으로 처리하고 표준 gate 진행.

**N > 0인 경우:**
```
[requirements-analysis 결과 표시]
A) 미해결 질문 처리 → aidlc-requirements-analysis: QUESTIONS 재호출
B) 현재 가정으로 유지하고 다음 단계로 진행
C) 변경 요청 → requirements-analysis 재호출
```

A) 선택 시: `"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"` 인라인 신호로 재호출 → 반환 → `열린 질문: [N]개` 패턴 재확인

**N == 0이고 가정 있음:**
```
[requirements-analysis 결과 표시]
가정으로 처리된 항목이 있습니다: [목록]
A) 가정 수정 → requirements-analysis 재호출
B) 가정 승인, 다음 단계 진행
```

**N == 0이고 가정 없음:**
```
[requirements-analysis 결과 표시]
A) 변경 요청 → requirements-analysis 재호출
B) 승인, 다음 단계 진행
```

### 4. workflow-planning 게이트 [2단계 게이트]

**1단계: 접근법 선택**
```
[workflow-planning 결과 표시]
[생성된 접근법 2-3개 표시]

A) [A안명] 선택
B) [B안명] 선택
C) [C안명] 선택 (Comprehensive만)
D) 변경 요청 → workflow-planning 재호출
```

선택 후:
- devflow-state의 `## Selected Approach` 업데이트
- workflow-plan.md의 `**Selected Approach**` 업데이트
- `## Approved Stages`를 선택된 접근법 기준으로 업데이트

**2단계: 개발 환경 설정**
```
개발 환경을 설정합니다.

A) 변경 요청 → workflow-planning 재호출
B) Git worktree로 격리 개발 (main 브랜치 보호) → aidlc-using-git-worktrees 호출
C) 현재 브랜치에서 바로 시작
```

### 워크트리 결과 게이트

workflow-planning 승인 후, 개발 환경 설정 게이트에서 B (Git Worktree) 선택 시:

`aidlc-using-git-worktrees` 호출 → 결과 게이트:
```
## aidlc-using-git-worktrees 완료

[스킬 반환 결과 표시]

A) 브랜치 이름 변경 요청 (스킬 재실행)
B) 이 워크트리에서 진행
⚠️ 베이스라인 테스트 실패 시: C) aidlc-systematic-debugging 먼저 / B) 실패 인지 후 진행
```

### INCEPTION → CONSTRUCTION 라우팅

workflow-plan.md의 `## Approved Stages`를 읽어 분기:
- `application-design: included` → application-design 게이트 실행
- `application-design: skipped`, `units-generation: included` → INCEPTION 완료, CONSTRUCTION에서 units-generation부터 시작
- `application-design: skipped`, `units-generation: skipped` → INCEPTION 완료, CONSTRUCTION에서 code-generation 직행

### 5. application-design 게이트 (조건부 실행)

`application-design: included`인 경우에만 실행.

#### 5a. LIST 게이트 [표준 게이트]

```
[application-design LIST 결과 표시]
A) 변경 요청 → application-design 재호출
B) [depth에 따라 조건부 표시]
   - Minimal: 승인, INCEPTION 완료 → INCEPTION 완료
   - Standard/Comprehensive: 승인, 상세 설계 진행 → application-design: DETAIL 호출
```

#### 5b. DETAIL 게이트 [표준 게이트] (Standard/Comprehensive만)

```
[application-design DETAIL 결과 표시]
A) 변경 요청 → application-design: DETAIL 재호출
B) 승인, INCEPTION 완료
```

---

## Error Handling

### Stage skill 호출 실패
스킬이 예상치 못한 결과를 반환하면:
A) 해당 단계 재시도 / B) 단계 스킵 (devflow-state에 skipped 기록)

### workflow-plan.md의 included/skipped 값 파싱 실패
`workflow-plan.md` 라우팅 키 형식이 예상과 다르면:
1. 파일 직접 확인 후 형식 수정
2. 기본값: application-design included, units-generation skipped

### Stage skill이 직접 gate를 제시하는 경우
스킬이 오케스트레이터 역할을 침범하면:
1. "이 게이트는 무시하고 B를 선택해주세요" 안내
2. 오케스트레이터가 정상 게이팅 처리

## INCEPTION 완료

모든 INCEPTION 스테이지 완료 시:

```
[INCEPTION 완료]
- 완료된 스테이지: [목록]
- 산출물: devflow-docs/inception/
```

→ Return to Entry Orchestrator (Phase 전환)
