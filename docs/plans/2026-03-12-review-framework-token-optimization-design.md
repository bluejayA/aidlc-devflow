# Review Sub-agent Framework + Token Optimization Design

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan.

**Goal:** AIDLC 플러그인에 리뷰 서브에이전트 프레임워크를 도입하면서, 오케스트레이터 구조를 분리하여 토큰 효율을 ~60% 개선한다.

**Complexity:** Comprehensive

**Date:** 2026-03-12

---

## 배경

### 문제 1: 자기 검증(Self-Verification)의 한계
현재 AIDLC는 `aidlc-verification-before-completion` 등 자기 검증 방식만 사용한다. superpowers 플러그인은 모든 단계에서 별도 서브에이전트가 산출물을 검증하여 확증 편향을 제거한다.

### 문제 2: 토큰 비효율
오케스트레이터(`aidlc-using-devflow`) 549줄이 매 스테이지마다 재로드된다. 5개 스테이지 기준 오케스트레이터만 ~2,745줄 누적 로드. INCEPTION 게이트가 CONSTRUCTION 때도 로드되고, 그 반대도 마찬가지.

### 토큰 비효율 전수 조사 결과

| 중복 유형 | 규모 |
|-----------|------|
| 게이트 패턴 반복 (A/B/C 선택 구조) | 146줄 |
| "Return to Orchestrator" 보일러플레이트 | 90줄 (9개 스킬) |
| Common Issues (artifact 미발견 처리) | 50줄 (5개 스킬) |
| 유사 예시 반복 | 80줄 |
| **직접 중복 합계** | **~366줄 (전체 3,500줄의 10.5%)** |

구조적 문제:
- Phase 미분리: INCEPTION/CONSTRUCTION 로직이 한 파일에 혼합
- 라우팅 로직 산재: 오케스트레이터, 개별 스킬, devflow-state 3곳에 분산
- devflow-conventions.md 미활용: 39줄 정의, 참조 0회

---

## 설계 결정 사항

### 결정 1: 리뷰 제어 주체 — 하이브리드
- **오케스트레이터**: 리뷰 정책만 정의 (depth별 리뷰 스킵/실행 여부)
- **스킬**: 리뷰 서브에이전트 dispatch 로직을 각자 보유
- **이유**: 토큰 효율. A안(오케스트레이터가 dispatch)은 오케스트레이터 프롬프트가 커져 모든 단계의 토큰 비용이 간접 증가. 하이브리드는 리뷰 로직이 해당 스킬 로딩 시에만 비용 발생 (~10배 효율적)

### 결정 2: 리뷰어 프롬프트 위치 — `_shared/reviewers/`
- 리뷰어 타입은 스킬보다 적음 (3가지로 수렴)
- 스킬별 특수 체크리스트는 YAGNI
- 나중에 필요해지면 각 스킬 디렉토리에 추가 가능

### 결정 3: Depth별 리뷰 정책 — Standard 이상에서만
- Minimal: 리뷰 스킵 (간단한 작업에 과도한 비용 방지)
- Standard / Comprehensive: 리뷰 서브에이전트 dispatch

### 결정 4: Escalation — 최대 5회 → 사용자 escalate
- superpowers와 동일한 정책
- Escalation 시 메시지 형식:
  ```
  ⚠️ 리뷰 루프 5회 초과 — 사용자 판단 필요

  리뷰 이력:
  - 1회: [이슈 요약]
  - 2회: [이슈 요약]
  - ...

  A) 현재 상태로 승인
  B) 직접 수정 지시
  ```

### 결정 5: 접근법 — Phase 분리 + 리뷰 통합 (A안)
- 오케스트레이터 Phase별 분리와 리뷰 프레임워크를 동시에 도입
- 리뷰를 추가하면서도 전체 토큰 비용은 오히려 감소

---

## 아키텍처: 3단 위임 체인

### 슈퍼에이전트가 아닌 경량 위임 구조

```
Entry Orchestrator (aidlc-using-devflow, ~80줄)
  → Phase Orchestrator (inception / construction, ~180-200줄)
    → Stage Skill (requirements-analysis 등)
      → Review Sub-agent (서브에이전트)
```

| 구분 | 슈퍼에이전트 | AIDLC 3단 위임 |
|------|-------------|---------------|
| 역할 | 모든 판단과 실행을 직접 수행 | 라우팅과 게이팅만 수행 |
| 컨텍스트 | 전체 워크플로우를 항상 보유 | 현재 Phase만 로드 |
| 스킬 관계 | 스킬이 도구처럼 종속 | 스킬이 독립 실행 후 반환 |

각 계층의 역할:
- **Entry Orchestrator** (~80줄): Phase 라우터. "INCEPTION인가 CONSTRUCTION인가?" 판별만
- **Phase Orchestrator** (~180-200줄): 스테이지 순서 + 게이트 관리. 실제 작업은 하지 않음
- **Stage Skill**: 실제 작업 수행 + 리뷰 dispatch
- **Review Sub-agent**: 산출물 검증만

---

## 오케스트레이터 분리 구조

### Entry Orchestrator: `aidlc-using-devflow/SKILL.md` (~80줄)

사용자가 호출하는 유일한 진입점. 역할:
- New Flow vs Resume Flow 판별
- devflow-state 초기화 (Complexity, Selected Approach 필드)
- Phase 라우팅: INCEPTION → `aidlc-inception-orchestrator`, CONSTRUCTION → `aidlc-construction-orchestrator`
- INCEPTION 완료 후 자동으로 CONSTRUCTION 전환

```
aidlc-using-devflow (Entry)
  ├─ New Flow → devflow-state 초기화 → aidlc-inception-orchestrator 호출
  │                                      ↓
  │                              INCEPTION 완료 반환
  │                                      ↓
  │                              aidlc-construction-orchestrator 호출
  │                                      ↓
  │                              CONSTRUCTION 완료 반환
  │                                      ↓
  │                              완료 gate (finishing-branch 안내)
  │
  └─ Resume Flow → devflow-state 읽기 → 현재 Phase의 orchestrator 호출
```

### INCEPTION Orchestrator: `aidlc-inception-orchestrator/SKILL.md` (~180줄)

- `invoke_mode: orchestrator-only` — 상위 오케스트레이터(Entry)만 호출 가능
- `plugin.json`에 스킬로 등록, Entry Orchestrator가 스킬 호출(invoke) 방식으로 실행
- 스테이지 순회 + 게이트 매핑:
  1. workspace-detection → workspace-detection 전용 게이트 [조건부 게이트]
  2. Complexity Declaration Gate
  3. requirements-analysis → Open Questions 게이트 [조건부 게이트]
  4. workflow-planning → Approach Proposal 게이트 [2단계 게이트]
  5. application-design (조건부) → LIST 게이트 → DETAIL 게이트 [표준 게이트]
- 각 게이트는 `_shared/gate-patterns.md` 템플릿 참조

### CONSTRUCTION Orchestrator: `aidlc-construction-orchestrator/SKILL.md` (~200줄)

- `invoke_mode: orchestrator-only` — 상위 오케스트레이터(Entry)만 호출 가능
- `plugin.json`에 스킬로 등록
- 스테이지 순회 + 게이트 매핑:
  1. units-generation (조건부) → units 게이트 [표준 게이트]
  2. code-generation Plan → code-plan 게이트 [리뷰 연계 게이트]
  3. code-generation Generate → 구현 게이트 [리뷰 연계 게이트]
  4. build-and-test → 완료 게이트 [표준 게이트]
- Multi-unit 핸들링: devflow-state의 `## Completed Units`를 읽어 미완료 unit 순회, unit당 step 2-3 반복

### `invoke_mode: orchestrator-only` 정의 확장

기존 정의 "aidlc-using-devflow만 호출"을 **"상위 오케스트레이터만 호출 가능"**으로 확장:
- Phase Orchestrator: Entry Orchestrator만 호출
- Stage Skill: Phase Orchestrator만 호출
- 사용자 직접 호출 불가는 동일

### devflow-state 읽기/쓰기 책임

| 필드 | 쓰기 책임 | 읽기 |
|------|----------|------|
| `## Current Phase` | Entry Orchestrator | Phase Orchestrator |
| `## Current Stage` | Phase Orchestrator | Stage Skill (선택적) |
| `## Complexity` | Entry Orchestrator (초기화) | Phase Orchestrator, Stage Skill |
| `## Selected Approach` | INCEPTION Orchestrator (gate 후) | Stage Skill |
| `## Completed Units` | CONSTRUCTION Orchestrator (unit 완료 시) | CONSTRUCTION Orchestrator |
| `## Audit Log` | Phase Orchestrator (gate 결정 시) | — |

---

## 게이트 템플릿화

### `_shared/gate-patterns.md` (~40줄)

게이트 **작성 규약**을 정의. 실제 게이트 내용은 각 Phase 오케스트레이터에 작성.

#### 표준 게이트 (Standard Gate)
스킬 반환 후 사용자 확인이 필요할 때.
```
[스킬 결과 요약 표시]
A) 변경 요청 → 스킬 재호출
B) 승인, 다음 단계 진행 → 다음 스테이지
```

#### 조건부 게이트 (Conditional Gate)
스킬 반환값의 특정 패턴에 따라 선택지가 달라질 때.
```
[패턴 매칭: 반환값에서 조건 추출]
조건 충족 시: 확장된 선택지 (A/B/C)
조건 미충족 시: 표준 게이트 (A/B)
```

#### 리뷰 연계 게이트 (Review-Aware Gate)
Standard 이상 depth에서 리뷰 결과를 포함하는 게이트.
```
[스킬이 리뷰 완료 후 반환]
[리뷰 결과 요약 표시]
A) 리뷰 이슈 수정 요청 → 스킬 재호출
B) 승인, 다음 단계 진행
```

### Phase 오케스트레이터에서의 적용

게이트 정의는 **패턴명 + 매개변수**로 축약:
```markdown
### requirements-analysis 게이트 [조건부 게이트]
패턴: `열린 질문: [N]개`
- N > 0: A) QUESTIONS 재호출 / B) 가정으로 진행 / C) 변경 요청
- N == 0: 표준 게이트
```

현재 146줄 → ~60줄로 축소.

---

## 리뷰 서브에이전트 프레임워크

### 리뷰어 유형 (3가지)

```
skills/_shared/reviewers/
  artifact-reviewer-prompt.md     ← INCEPTION 산출물 리뷰 (~60줄)
  code-plan-reviewer-prompt.md    ← 코드 계획 리뷰 (~50줄)
  code-reviewer-prompt.md         ← 구현 코드 리뷰: spec + quality 통합 (~80줄)
```

### artifact-reviewer-prompt.md
- **대상**: requirements.md, workflow-plan.md, application-design.md
- **체크 항목**: 완전성 (TODO/TBD 없음), 일관성 (내부 모순 없음), 명확성 (모호함 없음), YAGNI (불필요한 범위 없음)
- **입력**: 산출물 경로 + 상위 산출물 경로 (있으면)

### code-plan-reviewer-prompt.md
- **대상**: code-plan.md
- **체크 항목**: 스펙 대비 누락/초과 확인, 태스크 분해 적절성, 파일 구조 명확성
- **입력**: code-plan.md 경로 + requirements.md/application-design.md 경로

### code-reviewer-prompt.md
- **대상**: 구현된 코드 파일
- **체크 항목 (2단계 통합)**:
  - Stage 1 (Spec Compliance): 요구사항 대비 구현 일치, 누락/초과 기능
  - Stage 2 (Code Quality): 테스트 커버리지, 에러 핸들링, 보안, DRY
- **입력**: 변경 파일 목록 + code-plan.md 경로
- **참고**: superpowers는 이 둘을 별도 서브에이전트로 분리하지만, 토큰 효율을 위해 단일 프롬프트에 2단계 체크리스트로 통합

### 리뷰 dispatch 패턴 (스킬 내부, ~10-15줄)

```markdown
## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/[reviewer-type]-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch (산출물 경로 전달)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator
```

### 리뷰 대상 스킬

| 스킬 | 리뷰어 | 리뷰 대상 산출물 |
|------|--------|-----------------|
| aidlc-requirements-analysis | artifact-reviewer | requirements.md |
| aidlc-workflow-planning | artifact-reviewer | workflow-plan.md |
| aidlc-application-design | artifact-reviewer | application-design.md |
| aidlc-code-generation (Plan) | code-plan-reviewer | code-plan.md |
| aidlc-code-generation (Generate) | code-reviewer | 구현 코드 |
| aidlc-units-generation | artifact-reviewer | units.md |
| aidlc-workspace-detection | 리뷰 없음 | (사실 확인 — 검증 불필요) |
| aidlc-build-and-test | 리뷰 없음 | (검증 자체가 목적) |

### 리뷰 결과 반환 형식

```
[stage-name 결과]
- ...기존 결과...
- 리뷰: ✅ 승인됨 | ⏭ 스킵 (Minimal)
```

---

## 스킬 보일러플레이트 표준화

### Return to Orchestrator 표준화

현재 각 스킬마다 5~15줄 → 표준 형식으로 통일:
```markdown
## Return to Orchestrator

STOP.

```
[stage-name 결과]
- [핵심 결과 항목들]
- 산출물: [path]
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```
```

설명 문구("STOP here. No approval gate — orchestrator handles it.")는 `devflow-conventions.md`에 한 번만 정의. 예상 절감: ~45줄.

### Common Issues 표준화

5개 스킬의 "artifact not found" 처리를 `devflow-conventions.md`에 공통 규칙으로 정의. 각 스킬에서는 스킬 고유의 이슈만 남김. 예상 절감: ~50줄.

### 메타데이터

현행 유지. `version`, `author`, `category`는 가독성을 위해 각 스킬에 남김.

---

## `devflow-conventions.md` 확장 (~80줄)

현재 39줄, 참조 0회 → 플러그인 아키텍처 가이드로 확장:

- **아키텍처 개요**: 3단 위임 체인 설명, 슈퍼에이전트와의 차이
- **메타데이터 규약**: invoke_mode, return_behavior 정의
- **게이트 패턴 규약**: gate-patterns.md 참조
- **리뷰 규약**: depth 정책, 리뷰 루프, escalation, 반환 형식
- **Return to Orchestrator 규약**: 표준 형식 정의
- **산출물 미발견 시 공통 처리**: 공통 에러 처리 규칙
- **새 스킬 추가 가이드**: frontmatter 필수 필드, 리뷰 섹션 추가 방법, Phase Orchestrator 라우팅 등록 방법

이 파일은 **스킬 작성 시 참조용**이며, 매 스테이지마다 로드되지 않으므로 토큰 비용 증가 없음.

---

## 파일 변경 요약

### 신규 파일 (6개)

| 파일 | 역할 | 예상 분량 |
|------|------|----------|
| `aidlc-inception-orchestrator/SKILL.md` | INCEPTION Phase 루프 + 게이트 | ~180줄 |
| `aidlc-construction-orchestrator/SKILL.md` | CONSTRUCTION Phase 루프 + 게이트 | ~200줄 |
| `_shared/gate-patterns.md` | 게이트 패턴 규약 | ~40줄 |
| `_shared/reviewers/artifact-reviewer-prompt.md` | INCEPTION 산출물 리뷰어 | ~60줄 |
| `_shared/reviewers/code-plan-reviewer-prompt.md` | 코드 계획 리뷰어 | ~50줄 |
| `_shared/reviewers/code-reviewer-prompt.md` | 구현 코드 리뷰어 (spec+quality) | ~80줄 |

### 수정 파일 (8개)

| 파일 | 변경 내용 |
|------|----------|
| `aidlc-using-devflow/SKILL.md` | 549줄 → ~80줄 (Phase 라우팅만) |
| `aidlc-requirements-analysis/SKILL.md` | +Review 섹션, Return 표준화, Common Issues 간소화 |
| `aidlc-workflow-planning/SKILL.md` | +Review 섹션, Return 표준화 |
| `aidlc-application-design/SKILL.md` | +Review 섹션, Return 표준화 |
| `aidlc-code-generation/SKILL.md` | +Review 섹션 (Plan+Generate), Return 표준화 |
| `aidlc-units-generation/SKILL.md` | +Review 섹션, Return 표준화 |
| `_shared/devflow-conventions.md` | 39줄 → ~80줄 (아키텍처 가이드) |
| `.claude-plugin/plugin.json` | 버전 0.3.0 → 0.4.0 |

### 변경 없는 파일 (9개)

aidlc-build-and-test, aidlc-workspace-detection, aidlc-verification-before-completion, aidlc-receiving-code-review, aidlc-systematic-debugging, aidlc-dispatching-parallel-agents, aidlc-finishing-a-development-branch, aidlc-using-git-worktrees, aidlc-writing-skills

### 기존 스킬과의 관계

| 기존 스킬 | 새 리뷰 프레임워크와의 관계 |
|-----------|--------------------------|
| `aidlc-receiving-code-review` | **역할 분리, 충돌 없음.** 이 스킬은 외부(사람 또는 다른 AI)로부터 받은 코드 리뷰에 대응하는 방법을 정의. 새 리뷰 프레임워크는 내부 서브에이전트가 자동으로 수행하는 리뷰. 둘은 보완적 관계 |
| `aidlc-verification-before-completion` | **역할 유지.** 리뷰 서브에이전트는 산출물 품질 검증, verification은 실행 증거(테스트 통과 등) 검증. 서로 다른 관점의 검증이므로 둘 다 유지 |

### 토큰 비용 비교

| 시나리오 | 현재 | 변경 후 |
|---------|------|---------|
| INCEPTION 스테이지당 오케스트레이터 로드 | 549줄 | ~180줄 |
| CONSTRUCTION 스테이지당 오케스트레이터 로드 | 549줄 | ~200줄 |
| Entry Orchestrator 로드 | — | ~80줄 × 1회 (최초만) |
| 5 스테이지 워크플로우 총 오케스트레이터 비용 | ~2,745줄 | ~1,020줄 (Entry 80×1 + INCEPTION 180×3단계 + CONSTRUCTION 200×2단계. 조건부 스테이지 제외 기준) |
| 리뷰 추가 비용 (Standard, 5 스킬) | 0 | ~75줄 |
| **순 절감** | — | **약 60%** |
