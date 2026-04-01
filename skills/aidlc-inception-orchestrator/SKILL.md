---
name: aidlc-inception-orchestrator
description: Use when INCEPTION phase begins, to orchestrate workspace detection, requirements, planning, and design stages.
metadata:
  version: 0.7.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# aidlc-inception-orchestrator

<!-- 출력 언어: 한국어 (Korean) -->
<!-- INCEPTION Phase 오케스트레이터: 스테이지 순서 + 게이트 관리 -->
<!-- 게이트 패턴 참조: _shared/gate-patterns.md -->

## INCEPTION 스테이지 순서

```
workspace-detection → [Complexity Gate] → requirements-analysis → [Open Questions Gate]
  → [Pre-Planning Gate] → (user-stories) → (nfr-requirements)
  → workflow-planning → [Approach Proposal Gate]
  → (application-design + NFR Design) → [HELD Revisit Gate] → 완료
```

## The Orchestration Loop
<!-- @step:1 id=workspace-detection -->
<!-- @step:2 id=complexity-declaration -->
<!-- @step:3 id=requirements-analysis -->
<!-- @step:4 id=pre-planning -->
<!-- @step:5 id=user-stories skip-when=Minimal -->
<!-- @step:6 id=nfr-requirements skip-when=Minimal -->
<!-- @step:7 id=workflow-planning -->
<!-- @step:8 id=application-design -->
<!-- @step:9 id=held-revisit skip-when=no-held-items -->

아래 순서대로 스테이지를 순회한다. 각 스테이지에서:

### Step A: 스킬 호출

devflow-state의 `## Current Stage`를 업데이트하고 해당 스킬을 호출한다.
호출 시 필요한 파라미터는 인라인으로 전달한다:
- Complexity: `"Complexity: [level]"`
- Depth: `"Depth: [level]"`

### Step B: 결과 표시 + 로깅

스킬 반환값을 사용자에게 표시하고, devflow-audit에 기록한다. 결정 이유 포함 (session-continuity 규약 참조).

### Step B-1: session-summary 업데이트

게이트 승인 후 `devflow-docs/session-summary.md`를 업데이트한다:
- 파일이 없으면 신규 생성 (`_shared/patterns/session-continuity.md`의 템플릿 참조)
- `## Completed Work > ### INCEPTION`에 완료 스테이지 추가: `- [x] [stage-name] — [핵심 결과 한 줄]`
- `## Current State`의 Stage 필드 업데이트
- `## Key Decisions`에 게이트 선택 기록 (결정 이유 포함)
- `**Commit**` 필드에 현재 HEAD hash

### Step C: 게이트 제시

아래 게이트 정의에 따라 사용자에게 선택지를 제시한다.

### Step D: 라우팅

사용자 선택에 따라 다음 스테이지를 결정한다.

---

## 게이트 정의

### 1. workspace-detection 게이트 [조건부 게이트]
<!-- @gate: workspace-detection -->
<!-- @gate-option: A -> workspace-detection {재호출} -->
<!-- @gate-option: B -> reverse-engineering {brownfield-only, plugin-required} -->
<!-- @gate-option: C -> complexity-declaration -->

스킬 반환값에서 Greenfield/Brownfield 확인.

**reverse-engineering 가용성 검사:**
시스템 프롬프트의 사용 가능한 스킬 목록에서 `reverse-engineering:reverse-engineering`이 존재하는지 확인한다.

**Greenfield 경로:**
```
[workspace-detection 결과 표시]
A) 경로 수정 → workspace-detection 재호출
B) 확인, 다음 단계 진행 → Complexity Declaration Gate
```

**Brownfield 경로:**

reverse-engineering 스킬이 사용 가능한지 확인한다. 사용 가능하면 B 옵션을 포함, 불가능하면 A/B(=C) 2-option으로 표시한다.

```
[workspace-detection 결과 표시]
A) 분석 범위 수정 → workspace-detection 재호출
B) 코드베이스 심층 분석 (reverse-engineering) → reverse-engineering 호출 → 완료 후 Complexity Declaration Gate
   [reverse-engineering 플러그인 설치 시에만 표시]
C) 확인, 다음 단계 진행 → Complexity Declaration Gate
```

B 선택 시: reverse-engineering 스킬을 호출한다. 완료 후 산출물(`reverse-engineering/`)이 생성되며, 이후 requirements-analysis 호출 시 참조 컨텍스트로 전달한다: `"참조: reverse-engineering/README.md"`

### 2. Complexity Declaration Gate
<!-- @gate: complexity-declaration -->
<!-- @gate-option: A -> complexity-declaration {adjust} -->
<!-- @gate-option: B -> requirements-analysis -->

workspace-detection 결과를 기반으로 복잡도를 선언.

```
복잡도: **[Minimal/Standard/Comprehensive]** — [한 줄 이유]

A) 조정 요청
B) 승인
```

Complexity 값을 requirements-analysis 호출 시 인라인으로 전달: `"Complexity: [level]"`

### 3. requirements-analysis 게이트 [조건부 게이트 + 자동진행]
<!-- @gate: requirements-analysis -->
<!-- @condition: N==0,assumptions==0 -> pre-planning {auto} -->
<!-- @gate-option: A -> requirements-analysis {questions} -->
<!-- @gate-option: B -> pre-planning -->
<!-- @gate-option: C -> requirements-analysis {UPDATE} -->

패턴: `열린 질문: [N]개`

**패턴 매칭 실패 시**: LLM이 "없음", "0개", 다른 표현을 사용한 경우 N=0으로 처리하고 표준 gate 진행.

**N > 0인 경우:**
```
[requirements-analysis 결과 표시]
A) 미해결 질문 처리 → aidlc-requirements-analysis: QUESTIONS 재호출
B) 현재 가정으로 유지하고 다음 단계로 진행
C) 변경 요청 (예: 요구사항 추가/삭제, 우선순위 변경 등) → requirements-analysis UPDATE 재호출
```

A) 선택 시: `"aidlc-requirements-analysis: QUESTIONS — 기존 분석 유지, 미해결 질문만 처리"` 인라인 신호로 재호출 → 반환 → `열린 질문: [N]개` 패턴 재확인
C) 선택 시: `"aidlc-requirements-analysis: UPDATE — 기존 분석 유지, [사용자 변경 요청 내용] 반영"` 인라인 신호로 재호출

**N == 0이고 가정 있음:**
```
[requirements-analysis 결과 표시]
가정으로 처리된 항목이 있습니다: [목록]
A) 가정 수정 → requirements-analysis UPDATE 재호출
B) 가정 승인, 다음 단계 진행
```

A) 선택 시: `"aidlc-requirements-analysis: UPDATE — 기존 분석 유지, [사용자 변경 요청 내용] 반영"` 인라인 신호로 재호출

**N == 0이고 가정 없음:**

> 요구사항 분석 완료 — 열린 질문 없음, 가정 없음. 다음 단계로 진행합니다.

게이트 없이 자동 진행한다. 변경이 필요하면 사용자가 인터럽트(자유 발화)로 요청 가능.

### 4. Pre-Planning 분기 [자동분기 + 조건부 게이트]
<!-- @gate: pre-planning -->
<!-- @condition: complexity==Minimal -> workflow-planning -->
<!-- @condition: complexity==Comprehensive -> user-stories -->
<!-- @gate-option: A -> user-stories -->
<!-- @gate-option: B -> nfr-requirements -->
<!-- @gate-option: C -> workflow-planning -->

requirements-analysis 게이트 통과 후, workflow-planning 호출 전에 실행.
Pre-Planning은 INCEPTION 내 스테이지 그룹명이며, workflow-plan.md의 `### PRE-PLANNING` 섹션에 결과가 기록된다.
Minimal/Comprehensive는 자동 분기, Standard만 사용자 게이트.

**Minimal complexity**: 자동 스킵. 사용자에게 안내 후 workflow-planning으로 직행:

> Minimal complexity — Pre-Planning(User Stories, NFR) 자동 스킵 → 워크플로우 계획으로 진행합니다.

**Comprehensive complexity**: 자동 포함. 사용자에게 안내 후 User-Stories 게이트로 진행:

> Comprehensive complexity — Pre-Planning(User Stories + NFR) 자동 포함 → User Stories 작성을 시작합니다.

**Standard complexity**: 3-option 게이트 제시

```
요구사항 분석이 완료되었습니다. 다음 단계 전에 추가 분석이 가능합니다:

A) User Stories + NFR 수집 → 두 스테이지 모두 실행
B) NFR 수집만 → nfr-requirements만 실행 (상용 배포 시 권장)
C) 바로 워크플로우 계획으로 → 추가 분석 스킵
```

A → User-Stories 게이트로 진행
B → NFR-Requirements 게이트로 진행 (user-stories 스킵)
C → workflow-planning으로 직행

### 5. User-Stories 게이트 [표준 게이트 + Hold]
<!-- @gate: user-stories -->
<!-- @gate-option: A -> user-stories {UPDATE} -->
<!-- @gate-option: B -> nfr-requirements -->
<!-- @gate-option: H -> nfr-requirements {held} -->

Pre-Planning Gate에서 user-stories 실행이 결정된 경우에만.
aidlc-user-stories 호출 → 결과 게이트:

```
[user-stories 결과 표시]
A) 변경 요청 (예: 스토리 분할, 수용 기준 수정, 액터 변경 등) → user-stories UPDATE 재호출
B) 승인, 다음 단계 진행 → NFR-Requirements 게이트
H) 보류 (나중에 돌아옴) → HELD 상태 저장, NFR-Requirements 게이트로 진행
```

A) 선택 시: `"aidlc-user-stories: UPDATE — 기존 스토리 유지, [사용자 변경 요청 내용] 반영"` 인라인 신호로 재호출

### 6. NFR-Requirements 게이트 [모드 선택 게이트 + 표준 게이트 + Hold]
<!-- @gate: nfr-requirements-mode -->
<!-- @gate-option: A -> nfr-requirements {generate} -->
<!-- @gate-option: B -> nfr-requirements {import} -->
<!-- @gate-option: S -> workflow-planning {skipped} -->

Pre-Planning Gate에서 nfr-requirements 실행이 결정된 경우에만.

**6a. 모드 선택 (오케스트레이터 소유)**:
```
NFR 요구사항을 어떻게 진행하시겠습니까?

A) Claude가 질문하며 수집 (GENERATE)
B) 이미 작성된 NFR 문서가 있음 (IMPORT)
S) 이 단계 건너뛰기 (SKIP)
```

A → `"Mode: GENERATE"` 인라인 신호로 aidlc-nfr-requirements 호출
B → `"Mode: IMPORT"` 인라인 신호로 aidlc-nfr-requirements 호출
S → SKIPPED 상태 저장, workflow-planning으로 진행

<!-- @gate: nfr-requirements-result -->
<!-- @gate-option: A -> nfr-requirements {재호출} -->
<!-- @gate-option: B -> workflow-planning -->
<!-- @gate-option: H -> workflow-planning {held} -->
**6b. 결과 게이트**:
```
[nfr-requirements 결과 표시]
A) 변경 요청 (예: 성능 기준, 보안 요건, 가용성 목표 등) → nfr-requirements 재호출
B) 승인, 다음 단계 진행 → workflow-planning
H) 보류 (나중에 돌아옴) → HELD 상태 저장, workflow-planning으로 진행
```

### 7. workflow-planning 게이트 [2단계 게이트]
<!-- @gate: workflow-planning-approach -->
<!-- @gate-option: A -> workflow-planning-env -->
<!-- @gate-option: B -> workflow-planning-env -->
<!-- @gate-option: C -> workflow-planning-env {comprehensive-only} -->
<!-- @gate-option: D -> workflow-planning {재호출} -->

**1단계: 접근법 선택**
```
[workflow-planning 결과 표시]
[생성된 접근법 2-3개 표시]

A) [A안명] 선택
B) [B안명] 선택
C) [C안명] 선택 (Comprehensive만)
D) 변경 요청 (예: 접근법 수정, 스테이지 포함/제외 등) → workflow-planning 재호출
```

선택 후:
- devflow-state의 `## Selected Approach` 업데이트
- workflow-plan.md의 `**Selected Approach**` 업데이트
- `## Approved Stages`를 선택된 접근법 기준으로 업데이트

<!-- @gate: workflow-planning-env -->
<!-- @gate-option: A -> workflow-planning {재호출} -->
<!-- @gate-option: B -> branch-name-confirm -->
<!-- @gate-option: C -> inception-routing -->
**2단계: 개발 환경 설정**
```
개발 환경을 설정합니다.

A) 변경 요청 (예: 개발 환경 설정 변경 등) → workflow-planning 재호출
B) Git worktree로 격리 개발 (main 브랜치 보호) → 브랜치 이름 확인 후 워크트리 생성
C) 현재 브랜치에서 바로 시작
```

### 브랜치 이름 도출 및 확인 게이트
<!-- @gate: branch-name-confirm -->
<!-- @gate-option: A -> branch-name-confirm {변경} -->
<!-- @gate-option: B -> worktree-create -->

개발 환경 설정에서 B (Git Worktree) 선택 시, 브랜치 이름을 도출하여 사용자에게 확인 기회를 제공한다.

**브랜치 이름 도출:**

devflow-docs/inception/requirements.md의 ## User Intent에서 브랜치 이름을 도출:
- 한국어/영어 혼합 → 영어 키워드 추출 (2-4단어)
- 공백/특수문자 → 하이픈 치환, 소문자, feature/ 접두사

**도출 실패 처리:**

도출 결과가 비어 있거나 부적절할 경우 (예: 의미 없는 키워드, 너무 짧거나 긴 이름):
```
브랜치 이름을 자동으로 도출하지 못했습니다.
사용할 브랜치 이름을 직접 입력해 주세요 (예: my-feature-name):
feature/[입력값]
```

입력값에 feature/ 접두사를 자동 적용하고 소문자·하이픈 규칙을 적용한 후, 아래 확인 게이트를 표시한다.

**확인 게이트:**

```
도출된 브랜치 이름: feature/[이름]

A) 변경 → 원하는 이름 입력 (feature/ 접두사 자동 적용, 소문자·하이픈 규칙 적용)
B) 확인, 이 이름으로 워크트리 생성
```

A 선택 시: devflow-audit에 브랜치명 변경 이벤트 기록 → 사용자가 입력한 이름에 feature/ 접두사 적용 및 명명 규칙(소문자, 하이픈) 적용 후 게이트 재표시
B 선택 시: devflow-audit에 브랜치명 확정 이벤트 기록 → "Branch: feature/[이름]" 인라인 신호로 aidlc-using-git-worktrees 호출

### 워크트리 결과 게이트

`aidlc-using-git-worktrees` 반환 후:
```
## aidlc-using-git-worktrees 완료

[스킬 반환 결과 표시]

→ 다음 단계로 진행
⚠️ 베이스라인 테스트 실패 시: A) aidlc-systematic-debugging 먼저 / B) 실패 인지 후 진행
```

테스트 실패가 없으면 자동 진행한다.

### INCEPTION → CONSTRUCTION 라우팅
<!-- @condition: application-design==included -> application-design -->
<!-- @condition: application-design==skipped,units-generation==included -> CONSTRUCTION/units-generation -->
<!-- @condition: application-design==skipped,units-generation==skipped -> CONSTRUCTION/code-generation -->

workflow-plan.md의 `## Approved Stages`를 읽어 분기:
- `application-design: included` → application-design 게이트 실행
- `application-design: skipped`, `units-generation: included` → INCEPTION 완료, CONSTRUCTION에서 units-generation부터 시작
- `application-design: skipped`, `units-generation: skipped` → INCEPTION 완료, CONSTRUCTION에서 code-generation 직행

### 8. application-design 게이트 (조건부 실행)

`application-design: included`인 경우에만 실행.

#### 8a. LIST 게이트 [표준 게이트]
<!-- @gate: application-design-list -->
<!-- @gate-option: A -> application-design {재호출} -->
<!-- @gate-option: B -> application-design-detail -->

```
[application-design LIST 결과 표시]
A) 변경 요청 (예: 컴포넌트 추가/삭제, 책임 분리 등) → application-design 재호출
B) [depth에 따라 조건부 표시]
   - Minimal: 승인, INCEPTION 완료 → INCEPTION 완료
   - Standard/Comprehensive: 승인, 상세 설계 진행 → application-design: DETAIL 호출
```

#### 8b. DETAIL 게이트 [리뷰 연계 게이트] (Standard/Comprehensive만)
<!-- @gate: application-design-detail -->
<!-- @gate-option: A -> application-design-detail {재호출} -->
<!-- @gate-option: B -> INCEPTION-complete -->
<!-- @gate-option: R -> application-design-detail {review} -->

```
[application-design DETAIL 결과 표시]
A) 변경 요청 (예: 인터페이스 수정, 의존성 변경, 데이터 구조 등) → application-design: DETAIL 재호출
B) 승인, INCEPTION 완료
R) 리뷰 요청
   R1) 단일 리뷰 (Claude artifact-reviewer) — 기존 동작
   R2) Council 리뷰 (Codex + Gemini + Claude 의장)
   Ra) 자동 선택 (risk score 기반) ← 기본
```

**R1 선택 시 (기존 동작):**
1. `_shared/reviewers/artifact-reviewer-prompt.md`를 서브에이전트로 dispatch
   - 리뷰 대상: `devflow-docs/inception/application-design.md`
   - 참조 컨텍스트: `requirements.md`, `nfr-requirements.md` (있으면), `workspace.md`
2. 리뷰 결과를 게이트에 포함하여 재표시:
   ```
   [리뷰 결과 표시]
   A) 리뷰 반영하여 수정 → application-design: DETAIL 재호출
   B) 리뷰 참고, 현재 상태로 승인 → INCEPTION 완료
   ```
3. conventions 리뷰 루프 규약 적용 (Issues → 수정 권장, Recommendations → 참고)

**R2/Ra 선택 시 (Council 리뷰):**
1. `_shared/patterns/council-cli-detection.md` 절차 실행:
   - CLI 감지 → 가용 AI 목록 표시 → 사용자에게 참여 AI 확인 (전부/일부/없이)
   - 사용자 선택으로 모드 확정 (council-full/council-lite/single)
   - Ra 선택 시: 확정된 모드 범위 내에서 Risk Scoring으로 single/council 자동 결정
2. council-review-protocol의 **설계 리뷰용 프롬프트**로 에이전트 dispatch
   - agent-council 플러그인을 통해 외부 AI 호출
   - 리뷰 입력 번들 (파일 경로만 전달):
     - 리뷰 대상: `devflow-docs/inception/application-design.md`
     - 참조: `requirements.md`, `nfr-requirements.md` (있으면), `workspace.md`
   - council-lite 시: 병합 프롬프트 사용 (1개 AI가 두 관점 수행)
3. 결과 저장: `devflow-docs/inception/design-review-raw/{codex,gemini,synthesis}.md`
4. Claude 의장이 개별 결과를 읽고 synthesis.md 작성 (충돌 해결 4단계 적용)
5. **synthesis 결과를 사용자에게 표시 + 승인 대기**:
   ```
   [Council 리뷰 결과]
   Gate Decision: [PASS|CONDITIONAL|FAIL]
   Rationale: [판정 근거]

   Consensus: [합의 사항]
   Divergence: [충돌 + 의장 판정]
   Action Items: [수정 항목]

   A) 리뷰 반영하여 수정 → application-design: DETAIL 재호출
   B) 현재 상태로 승인 → INCEPTION 완료
   ```

**DETAIL 호출 시 NFR Design 활성화 판단:**
3가지 조건 모두 충족 시 인라인 신호 추가:
1. depth가 Comprehensive
2. DETAIL 모드
3. `devflow-docs/inception/nfr-requirements.md` 존재

충족 시: `"aidlc-application-design: DETAIL — NFR Design 포함"`
미충족 시: `"aidlc-application-design: DETAIL"` (기존대로)

### 9. HELD 항목 재방문 게이트 [조건부 게이트]
<!-- @gate: held-revisit -->
<!-- @gate-option: A -> held-revisit {재방문} -->
<!-- @gate-option: B -> INCEPTION-complete {held-유지} -->

application-design 게이트 통과 후, INCEPTION 완료 직전에 1회 실행.

**조건 확인**: devflow-state에서 HELD 항목 검색.
- `user-stories: HELD` 또는 `nfr-requirements: HELD` 항목이 있는지 확인.

**HELD 항목 없음**: 자동 스킵 → INCEPTION 완료로 진행.

**HELD 항목 있음**: 아래 게이트 표시.

```
INCEPTION 완료 전, 보류된 항목이 있습니다:
- [HELD 항목 목록 표시]

A) 재방문 → 해당 스킬 재호출 (결과에 따라 HELD 해제 또는 유지)
B) HELD 상태 유지하고 완료 진행
```

**A 선택 시 — 재방문 흐름:**
HELD 항목이 복수이면, 각 항목을 순차 재호출하며 항목별 서브게이트를 제시한다.
모든 항목 처리 완료 후 최상위 HELD 재방문 게이트는 재표시하지 않는다.

1. HELD 항목 순서대로 해당 스킬을 재호출한다:
   - user-stories: HELD → aidlc-user-stories 호출 (기존 산출물 컨텍스트 전달)
   - nfr-requirements: HELD → aidlc-nfr-requirements 호출 (기존 산출물 컨텍스트 전달)
2. 각 스킬 반환 후 표준 게이트 제시:
   A) 변경 요청 → 스킬 재호출
   B) 승인 → devflow-state에서 HELD 해제 (status: COMPLETED), devflow-audit에 기록
   H) 이번에도 보류 → HELD 상태 유지, devflow-audit에 재방문-보류 기록
3. 모든 HELD 항목 처리 완료 후 INCEPTION 완료로 진행.

**B 선택 시:**
- devflow-audit에 HELD 유지 결정 기록 (항목명 + 이유)
- INCEPTION 완료로 진행.

**재방문 결과 기록 (devflow-state + session-summary):**
- devflow-state: 항목별 최종 상태 업데이트
- session-summary ## Key Decisions에 재방문 결정 기록

---

## Interrupt Handling
<!-- @interrupt: global -->

모든 게이트에서 사용자 응답이 선택지 밖 자유 발화인 경우:
→ `_shared/patterns/interrupt-handler.md` 참조하여 인터럽트 게이트 프로토콜 실행.

---

## Error Handling

### Stage skill 호출 실패
스킬이 예상치 못한 결과를 반환하면:
A) 해당 단계 재시도 / B) 단계 스킵 (devflow-state에 skipped 기록)

### workflow-plan.md의 included/skipped 값 파싱 실패
`workflow-plan.md` 라우팅 키 형식이 예상과 다르면:
1. 파일 직접 확인 후 형식 수정
2. 기본값: application-design included, units-generation skipped

### Hold/Skip 상태 처리
Pre-Planning 스테이지에서 HELD 또는 SKIPPED가 발생하면:
1. devflow-state에 상태 기록: `user-stories: HELD` 또는 `nfr-requirements: SKIPPED`
2. devflow-audit에 로깅
3. 다음 스테이지로 진행
4. workflow-plan.md의 `### PRE-PLANNING` 섹션에 상태 기록

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
