# AIDLC 토큰 효율화 리팩토링 설계

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AIDLC 플러그인 스킬 파일들의 중복 제거, 혼동 해소, 토큰 축약을 통해 전체 줄 수 20% 이상 감소 + 혼동 지점 12개 전부 해결

**Complexity:** Standard

**Approach:** Extract & Reference — `devflow-conventions.md`에 공통 패턴을 추가하고, 각 스킬에서는 conventions 참조로 대체

---

## 1. conventions.md 확장

현재 `_shared/devflow-conventions.md` v0.3.0 (114줄)에 4개 섹션을 추가한다.

### 1-1. Standard Return Format

모든 stage skill의 "Return to Orchestrator" 보일러플레이트를 통합.

```markdown
## Return to Orchestrator 표준 형식

모든 stage skill은 실행 완료 후 아래 형식으로 반환한다:

    STOP.
    [{skill-name} 결과]
    - {필드1}: {값}
    - {필드2}: {값}
    ...

- "STOP." 지시와 반환 형식 설명은 이 규약을 따른다.
- 각 스킬의 SKILL.md에는 반환 필드 목록만 정의한다.
- return_behavior가 stop-no-gate인 스킬은 게이트를 제시하지 않는다.
```

각 스킬에서의 대체 형식:
```markdown
## Return to Orchestrator
conventions 표준 형식. 반환 필드:
- {필드1}: [설명]
- {필드2}: [설명]
```

### 1-2. Standard Review Workflow

7개 스킬에 복붙된 리뷰 패턴을 통합.

```markdown
## Review Workflow (Standard 이상)

depth가 Standard 이상이면:
1. 해당 reviewer prompt 읽기 (artifact/code-plan/code-reviewer)
2. 리뷰 서브에이전트 dispatch (산출물 경로 전달)
3. Approved → Return to Orchestrator
4. Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator.
depth 확인: devflow-state.md의 ## Complexity 필드.
```

각 스킬에서의 대체 형식:
```markdown
## Review
conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/{artifact}.md
- 리뷰어: {reviewer}-prompt.md
```

### 1-3. Complexity와 Stage Depth 관계

현재 어디에도 명시되지 않은 관계를 정의.

```markdown
## Complexity와 Stage Depth

- **Complexity**: 프로젝트 전체 복잡도. INCEPTION 초기에 선언 (Minimal/Standard/Comprehensive).
- **Stage Depth**: 개별 스테이지 실행 깊이. workflow-planning에서 Stage별로 결정.
- **기본 규칙**: Stage Depth는 Complexity를 따르되, workflow-planning이 override 가능.
- **전달 방식**: 오케스트레이터가 스킬 호출 시 인라인 텍스트로 depth를 전달.
  스킬은 호출 텍스트의 depth를 우선 사용하고, 없으면 devflow-state.md에서 읽는다.
```

### 1-4. 용어 정의

```markdown
## 용어

| 용어 | 정의 |
|------|------|
| **unit** | 독립적으로 구현·테스트 가능한 개발 단위. story(사용자 가치)나 component(아키텍처 단위)와 다름. 구현 순서와 병렬성을 결정하기 위한 분해 단위. |
| **B안** | Orchestrator-Centric 아키텍처. 오케스트레이터가 게이트·상태·라우팅을 소유하고, stage skill은 순수 실행자. |
| **Pre-Planning** | requirements-analysis와 workflow-planning 사이의 조건부 단계 (user-stories, nfr-requirements). |
| **depth** | 개별 스테이지의 실행 깊이 (Minimal/Standard/Comprehensive). Complexity와 구분. |
```

### 1-5. invoke_mode 값 보완

기존 conventions.md에 `user-invocable` 행이 이미 존재한다. 해당 행의 설명을 보완:
- 현재: `사용자 직접 호출 가능`
- 변경: `사용자가 직접 호출 가능. 오케스트레이터 워크플로우 외부에서 독립적으로 사용`

---

## 2. 혼동 해소 (12개 항목)

### 2-1. invoke_mode 정리

다음 4개 스킬에 `invoke_mode: user-invocable` metadata 필드를 추가 (현재 이 필드가 없으므로 신규 추가):
- `aidlc-systematic-debugging`
- `aidlc-verification-before-completion`
- `aidlc-finishing-a-development-branch`
- `aidlc-receiving-code-review`

### 2-2. Approved Stages 업데이트 책임 명시

`aidlc-inception-orchestrator`의 Gate 7 (workflow-planning 게이트) 섹션에 추가:

```markdown
사용자가 접근법을 선택하면:
1. workflow-plan.md의 **Selected Approach** 필드 업데이트 ← 오케스트레이터
2. workflow-plan.md의 ## Approved Stages를 선택된 접근법 기준으로 재작성 ← 오케스트레이터
3. devflow-state.md 업데이트 ← 오케스트레이터
```

### 2-3. NFR Design 활성화 책임 단일화

- `aidlc-inception-orchestrator`: 3조건 판단 로직 유지 (판단 주체)
- `aidlc-application-design`: 판단 로직 제거, 수신 로직만 유지:
  ```
  오케스트레이터가 "NFR Design 포함" 신호를 전달한 경우에만 실행.
  활성화 조건 판단은 오케스트레이터 소유 (오케스트레이터 중심 원칙).
  ```

### 2-4 ~ 2-6. conventions 용어 정의로 해소

- "B안" 정의 → conventions 용어 테이블
- Complexity vs Depth → conventions 관계 정의
- "unit" 정의 → conventions 용어 테이블

### 2-7. Pre-Planning Gate 명칭 변경

`inception-orchestrator`에서:
- 현재: `### 4. Pre-Planning Gate [조건부 게이트]`
- 변경: `### 4. Pre-Planning 분기 [자동분기 + 조건부 게이트]`
- 설명 추가: "Minimal/Comprehensive는 자동 분기, Standard만 사용자 게이트"

### 2-8. using-devflow 역할

변경 없음. Entry Orchestrator는 세션 재개/신규 판단 + Phase Orchestrator 라우팅이 핵심 역할.

### 2-9. "(B안)" 표기 제거

"(B안)" 표기가 있는 모든 스킬 metadata의 `description`에서 제거. conventions 용어 정의에서 일괄 정의.

### 2-10 ~ 2-12. TDD 중복 설명 정리

| 스킬 | 변경 |
|------|------|
| `code-generation` | TDD 개요 설명 제거 → `tdd-protocol.md` 참조 + 2단계 Plan→Generate 고유 흐름만 유지 |
| `systematic-debugging` | TDD RED 설명 제거 → `tdd-protocol.md` 참조 + 4단계 디버깅 프로세스만 유지 |
| `verification-before-completion` | Self-Review 체크리스트 중복 제거 → `tdd-protocol.md` 참조 + 6단계 검증 프로세스만 유지 |

---

## 3. 토큰 축약

### 3-1. 예시 축약

| 스킬 | 현재 | 목표 |
|------|------|------|
| `systematic-debugging` | Example 2개, 각 20줄 | 각 8줄 (핵심 흐름만) |
| `code-generation` | Example 2개, 각 30줄 | 각 10줄 |
| `verification-before-completion` | Example 3개, 각 25줄 | 2개로 줄이고 각 10줄 |

### 3-2. 합리화 방지 테이블 축약

- `systematic-debugging`, `verification-before-completion`: 테이블 행 수 축약 (핵심 3개만 유지)
- `dispatching-parallel-agents`: 병렬화 금지 테이블 축약

### 3-3. workspace-detection 등 단순 스킬 축약

핵심 로직 대비 과도한 설명 축약. 92줄 → ~60줄 목표.

---

## 4. 변경하지 않는 것

- 스킬의 핵심 로직/프로세스 — 동작 변경 없음
- 오케스트레이터의 게이트 순서 — 그대로 유지
- `_shared/tdd-protocol.md`, `_shared/gate-patterns.md`, `_shared/import-review-protocol.md` — 내용 변경 없음
- 리뷰어 프롬프트 (`_shared/reviewers/`) — 변경 없음
- `_utils/devflow-state`, `_utils/devflow-audit` — 변경 없음

---

## 5. 수정 대상 파일 목록

### 수정 파일 (18개)

| 파일 | 변경 내용 |
|------|----------|
| `_shared/devflow-conventions.md` | 4개 섹션 추가 (Return Format, Review Workflow, Complexity/Depth, 용어) + invoke_mode 값 추가 |
| `aidlc-inception-orchestrator/SKILL.md` | Approved Stages 책임 명시, Pre-Planning 명칭 변경 |
| `aidlc-workspace-detection/SKILL.md` | Return 축약, "(B안)" 제거, 과도한 설명 축약 |
| `aidlc-requirements-analysis/SKILL.md` | Return+Review 축약, "(B안)" 제거 |
| `aidlc-user-stories/SKILL.md` | Return+Review 축약 |
| `aidlc-nfr-requirements/SKILL.md` | Return+Review 축약 |
| `aidlc-workflow-planning/SKILL.md` | Return+Review 축약 |
| `aidlc-application-design/SKILL.md` | Return+Review 축약, NFR 판단 로직 제거 |
| `aidlc-units-generation/SKILL.md` | Return+Review 축약 |
| `aidlc-code-generation/SKILL.md` | Return+Review 축약, TDD 중복 제거, 예시 축약 |
| `aidlc-build-and-test/SKILL.md` | Return 축약 |
| `aidlc-systematic-debugging/SKILL.md` | invoke_mode 추가, TDD 중복 제거, 예시 축약, 합리화 테이블 축약 |
| `aidlc-verification-before-completion/SKILL.md` | invoke_mode 추가, TDD 중복 제거, 예시 축약, 합리화 테이블 축약 |
| `aidlc-finishing-a-development-branch/SKILL.md` | invoke_mode 추가 |
| `aidlc-receiving-code-review/SKILL.md` | invoke_mode 추가 |
| `aidlc-dispatching-parallel-agents/SKILL.md` | 병렬화 금지 테이블 축약 |
| `aidlc-writing-skills/SKILL.md` | "(B안)" 제거만 |
| `aidlc-using-git-worktrees/SKILL.md` | "(B안)" 제거만 |

### 변경 없는 파일

- `aidlc-using-devflow/SKILL.md` (Entry Orchestrator — 변경 불필요)
- `aidlc-construction-orchestrator/SKILL.md` (혼동 지점 없음)
- `_shared/tdd-protocol.md`, `gate-patterns.md`, `import-review-protocol.md`
- `_shared/reviewers/*`
- `_utils/*`
- `.claude-plugin/plugin.json` (v0.6.0 유지, 이번은 내부 리팩토링)

---

## 6. 성공 기준

| 지표 | 현재 | 목표 |
|------|------|------|
| 전체 스킬 파일 줄 수 (skills/ 이하, reviewers/_utils 제외) | ~4,000 | ≤3,200 (20%↓) |
| 같은 내용 2곳 이상 패턴 | 12+ | 0 |
| 혼동 지점 | 12 | 0 |
| conventions.md 크기 | 114줄 | ~180줄 |

---

## 7. 실행 순서

1. `devflow-conventions.md` 확장 (SSOT 먼저)
2. `inception-orchestrator` 혼동 해소 (Approved Stages, Pre-Planning, NFR Design)
3. Stage skill 중복 제거 (Return + Review 축약, invoke_mode 정리)
4. 토큰 축약 (예시, 테이블, 과도한 설명)
5. 검증: 줄 수 20% 감소 확인 + 혼동 해소 12개 항목 체크리스트 점검

## Assumptions

- plugin.json 버전은 변경하지 않음 (내부 리팩토링이므로 v0.6.0 유지)
- 스킬의 외부 인터페이스(반환 필드, 게이트 형식)는 변경하지 않음
- conventions.md를 참조하는 방식은 "섹션명 언급"으로 충분 (파일 내 앵커 링크 불필요)
