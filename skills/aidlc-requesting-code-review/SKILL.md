---
name: aidlc-requesting-code-review
description: |
  태스크나 unit 구현이 완료되어 머지 전 코드 리뷰가 필요할 때, 또는 사용자가 명시적으로 코드 리뷰를 요청할 때 사용.
  Use when a task or unit implementation is complete and needs code review before merging, or when the user explicitly requests a code review on their changes.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 자신의 코드를 비판적으로 재검토하지 않음"
  amplification_notes: "3-stage/4-stage 리뷰 + 다중 reviewer 디스패치 구조"
---

# aidlc-requesting-code-review

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 코드 리뷰 요청의 Single Source of Truth. Standard 3-stage / Comprehensive 4-stage review 실행. -->

## Trigger

다음 상황에서 이 스킬을 실행한다:

- 태스크/유닛 구현이 완료되고 머지 전 리뷰가 필요할 때
- PR 생성 전 코드 품질을 확인하고 싶을 때
- 복잡한 리팩토링이나 버그 수정 후 검증이 필요할 때
- `aidlc-subagent-driven-development`가 태스크 완료 후 자동 호출할 때

## Purpose

depth에 따라 3-stage (Standard) 또는 4-stage (Comprehensive) code review를 실행하고 결과를 반환한다.
이 스킬이 코드 리뷰 프로세스의 유일한 정의이다 — 다른 스킬은 리뷰 로직을 자체 구현하지 않고 이 스킬을 호출한다.

---

## 입력

| 항목 | 필수 | 설명 |
|------|------|------|
| 리뷰 대상 | 필수 | git diff, 파일 경로, 또는 커밋 SHA |
| spec/plan 경로 | 선택 | spec compliance 검증용. 미제공 시 Stage 1 스킵 |
| depth | 선택 | Minimal/Standard/Comprehensive. 기본 Standard |

---

## 프로세스

### 0. Depth 확인

- **Minimal / Standard / Comprehensive**: 리뷰 모드 선택으로 진행

### 0.1. 리뷰 모드 선택

리뷰 모드를 선택한다. 호출 시 모드가 지정되면 해당 모드를 사용하고, 미지정이면 기본값(R1).

```
리뷰 모드:
R1) 단일 리뷰 (3-stage Standard / 4-stage Comprehensive) ← 기본
R2) Council 리뷰
R3) Agent Teams 협업 리뷰 (리뷰어 간 소통 기반)
Ra) 자동 선택 (risk score 기반)
```

**R1 선택**: Stage 1 → Stage 2 → Stage 3 → Stage 4 (기존 동작 그대로)

**R2/Ra 선택**: Council 리뷰로 진행

**R3 선택**: Agent Teams 리뷰로 진행

---

### R1 흐름: 단일 리뷰

#### Step 0 — 프로젝트 루트 결정

`devflow-docs/devflow-state.md`의 `## Worktree` → `path` 값을 확인한다.
- **값이 있으면**: 해당 워크트리의 절대 경로를 `{project-root}`로 사용
- **값이 없거나 `none`이면**: 현재 CWD를 `{project-root}`로 사용

이후 모든 Stage의 서브에이전트 dispatch 시 `{project-root}`를 프롬프트에 포함한다:
```
프로젝트 루트: {project-root}
중요: 모든 파일 경로는 프로젝트 루트 기준이다. 파일을 읽을 때 반드시 프로젝트 루트를 prefix로 사용하라.
```

#### Stage 1 — Spec Compliance

spec/plan 경로가 제공된 경우에만 실행. 미제공 시 Stage 2로 바로 진행.

1. `_shared/reviewers/spec-reviewer-prompt.md` 읽기
2. 서브에이전트 dispatch — `{project-root}` + 리뷰 대상 + spec/plan 경로 전달
3. 결과 확인 (Verdict 기준):
   - PASS → Stage 2로
   - FAIL → 수정 후 re-dispatch (conventions 리뷰 루프 규약: 최대 5회, 초과 시 사용자 escalate)
   - CONDITIONAL → Stage 2로 (수정 권장)

#### Codex 세컨드 오피니언 (결과 반환 시 안내)

conventions Codex 세컨드 오피니언 정책 적용.

Claude 리뷰 결과 반환 시, Codex 세컨드 오피니언 실행 가이드를 함께 표시한다.

> **수동 실행 전용**: `/codex:review`는 `disable-model-invocation` 제약으로 Claude가 자동 호출할 수 없다. 아래 가이드를 표시하고 사용자가 직접 실행한다.

**안내 생성 규칙:**

1. `devflow-state.md`에서 워크트리 정보를 읽는다:
   - `## Worktree` → `branch`, `path` 값 확인
2. 리뷰 대상 범위를 결정한다:
   - 워크트리 있음 → `--scope branch` (현재 브랜치의 전체 변경)
   - 워크트리 없음 + staged 변경 → `--uncommitted`
   - 워크트리 없음 + 커밋 완료 → `--base main` (main 대비 diff)
3. CONDITIONAL/FAIL stage가 있으면 해당 관점을 힌트로 포함한다

**안내 템플릿:**

```
> **Codex 세컨드 오피니언**: 추가 검증이 필요하면 아래 명령을 실행하세요.
> → `/codex:review --scope branch`
>   브랜치: [branch명], 워크트리: [path]
>   [CONDITIONAL/FAIL stage가 있으면] 참고: [stage명]에서 [이슈 요약] 발견 — Codex 관점도 확인 권장
```

Codex CLI 미감지 시 안내를 생략한다 (conventions fallback 참조).

#### Stage 2+3(+4) — Code Quality + Security (+ Maintainability) 병렬

> **타임아웃**: conventions 타임아웃 정책 적용. 개별 리뷰어 기본 300초. 타임아웃 시 "⏭ 타임아웃" 표시, 나머지 결과로 종합.

Stage 1 완료 후, depth에 따라 병렬 dispatch한다.

**Minimal**: Stage 2만 단독 실행 (Stage 3 스킵)
**Standard**: Stage 2 + Stage 3 병렬 dispatch
**Comprehensive**: Stage 2 + Stage 3 + Stage 4 전부 병렬 dispatch

1. `_shared/reviewers/code-quality-reviewer-prompt.md` — Stage 2 서브에이전트 dispatch (background, `{project-root}` 포함)
2. `_shared/reviewers/security-reviewer-prompt.md` — Stage 3 서브에이전트 dispatch (background, Standard 이상)
3. `_shared/reviewers/maintainability-reviewer-prompt.md` — Stage 4 서브에이전트 dispatch (background, Comprehensive만)
4. 모든 결과 수신 후 종합:
   - 모두 PASS → 결과 반환
   - 일부 FAIL → FAIL stage만 수정 루프 (PASS stage 결과 유지, 최대 5회)
   - 모두 FAIL → 모든 stage 수정 루프

---

### R2/Ra 흐름: Council 리뷰

R2 또는 Ra 선택 시, 4-stage 관점을 외부 AI와 함께 실행한다.
> **4-stage와 Council의 관계**: 4-stage는 "무엇을 볼 것인가"(관점 커버리지), Council은 "누가 볼 것인가"(다모델 편향 보완). 두 차원은 직교한다. Council이 바꾸는 것은 Stage 2-4의 실행 주체이지, 관점 자체를 대체하지 않는다.

1. **Stage 1 (Spec Compliance)**: spec/plan 제공 시 Claude 서브에이전트로 실행 (R1과 동일)
   - 요구사항 대조는 사실 확인이므로 외부 AI 불필요
2. `_shared/patterns/council-cli-detection.md` 절차 실행:
   - CLI 감지 → 가용 AI 목록 표시 → 사용자에게 참여 AI 확인 (전부/일부/없이)
   - 사용자 선택으로 모드 확정 (council-full/council-lite/single)
   - Ra 선택 시: 확정된 모드 범위 내에서 Risk Scoring으로 single/council 자동 결정
   - single 확정 시: R1 흐름의 Stage 2로 전환하여 이후 Stage 3 → Stage 4 순서대로 진행
3. **Stage 2-4를 council-review-protocol로 dispatch**:
   - Codex 관점: Stage 2 (Quality) + Stage 4 (Maintainability, Comprehensive만)
   - Gemini 관점: Stage 3 (Security/Edge-case)
   - council-lite 시: 병합 프롬프트 사용 (1개 AI가 모든 관점 수행)
   - 리뷰 입력 번들 (파일 경로만 전달):
     - 리뷰 대상: git diff + 변경 파일 경로
     - 참조: 테스트 결과 요약, `requirements.md`
4. 결과 저장: `devflow-docs/construction/{unit}/code-review-raw/{codex,gemini,synthesis}.md`
5. Claude 의장이 개별 결과를 읽고 synthesis.md 작성 (충돌 해결 4단계 적용)
6. **synthesis 결과를 사용자에게 표시 + 승인 대기**:
   ```
   [Council Code Review 결과]
   Verdict: [PASS|CONDITIONAL|FAIL]
   Rationale: [판정 근거]
   Action Items: [수정 항목]

   A) 리뷰 반영하여 수정
   B) 현재 상태로 승인
   ```
7. 결과를 결과 반환 형식으로 반환 (council 모드 표시 추가)

---

### R3 흐름: Agent Teams 리뷰

R3 선택 시, 리뷰어들이 Agent Teams로 팀을 구성하여 소통 기반 협업 리뷰를 수행한다.

> **R1과 R3의 차이**: R1은 각 리뷰어가 독립 실행 후 결과만 수집. R3은 리뷰어 간 발견 사항을 공유하여 중복 제거, 크로스 커팅 이슈 발견이 가능하다.

1. `_shared/patterns/review-team-protocol.md` 읽기
2. **Stage 1 (Spec Compliance)**: spec/plan 제공 시 서브에이전트로 실행 (R1과 동일)
   - 요구사항 대조는 사실 확인이므로 팀 협업 불필요
3. **Stage 2-4를 Agent Teams로 실행**:
   - TeamCreate → 리뷰 팀 생성
   - depth에 따라 리뷰어 spawn (Explore 타입):
     - Standard: quality-reviewer + security-reviewer (+ spec-reviewer if spec 제공)
     - Comprehensive: + maintainability-reviewer
   - 리뷰어들이 병렬로 리뷰 수행 + SendMessage로 발견 사항 공유
   - 팀 리드가 모든 결과 수신 후 종합 (결과 반환 형식으로 변환)
   - TeamDelete로 팀 정리
   - **이슈 수정 루프**: FAIL 또는 CONDITIONAL 판정 시 수정 후 팀 재생성하여 re-review (최대 5회, 초과 시 사용자 escalate — R1과 동일 제한)
4. **종합 결과를 사용자에게 표시 + 승인 대기**:
   ```
   [Agent Teams Code Review 결과]
   Verdict: [PASS | CONDITIONAL | FAIL]
   Cross-cutting Issues: [리뷰어 간 소통에서 도출된 교차 이슈]
   Issues: [분류별 목록]

   A) 리뷰 반영하여 수정
   B) 현재 상태로 승인
   ```
5. 결과를 결과 반환 형식으로 반환 (teams 모드 표시 추가)

**에러 핸들링**:
- TeamCreate 실패 → "Agent Teams를 사용할 수 없습니다. R1으로 전환합니다." 안내 후 R1 흐름으로 자동 전환
- Agent spawn 실패 (일부 리뷰어) → 성공한 리뷰어 결과만 종합 + 실패한 관점은 "⏭ 스킵 (spawn 실패)" 표시
- 전체 Agent spawn 실패 → R1 fallback

---

### 결과 반환

각 Stage의 리뷰어는 `_shared/patterns/review-feedback-schema.md`의 출력 포맷을 따른다. Synthesis는 개별 Verdict를 worst-of 로직으로 집계한다.

```
## Code Review 결과
- Stage 1 (Spec Compliance): PASS | CONDITIONAL | FAIL | ⏭ 스킵 (spec 미제공)
- Stage 2 (Code Quality): PASS | CONDITIONAL | FAIL
- Stage 3 (Security/Edge-case): PASS | CONDITIONAL | FAIL | ⏭ 스킵 (Minimal)
- Stage 4 (Maintainability): PASS | CONDITIONAL | FAIL | ⏭ 스킵 (Standard 이하)
- Verdict: PASS | CONDITIONAL | FAIL (worst-of across all stages)
- Issues: [있으면 — severity + file:line 테이블]
- Score: [루브릭 항목별 🟢/🟡/🔴 집계]
```

**Verdict 집계 (worst-of)**: 어느 Stage든 FAIL이면 전체 FAIL. FAIL 없이 CONDITIONAL 있으면 전체 CONDITIONAL. 모두 PASS면 전체 PASS.

---

## Standalone vs SDD 호출

| 모드 | 트리거 | spec/plan | depth | 리뷰 모드 |
|------|--------|-----------|-------|----------|
| **Standalone** | 사용자 직접 호출 | 사용자 지정 (없으면 Stage 1 스킵) | 사용자 지정 또는 Standard | 사용자 선택 (R1/R2/R3/Ra) |
| **SDD** | 태스크 완료 후 자동 | 태스크의 spec/plan 경로 | plan Complexity 연동 | R1 (기본값 고정) |

SDD에서 호출 시, SDD가 리뷰 대상(변경 파일)과 spec/plan 경로를 전달한다. 리뷰 모드는 항상 R1 — 팀/Council 모드는 사용자 명시 선택 시에만.

---

## 리뷰어 프롬프트 관계

| 프롬프트 | 용도 | 이 스킬에서의 역할 |
|---------|------|------------------|
| `spec-reviewer-prompt.md` | spec compliance 단독 검증 | Stage 1 |
| `code-quality-reviewer-prompt.md` | 코드 품질 단독 검증 | Stage 2 |
| `security-reviewer-prompt.md` | 보안/엣지케이스 심층 분석 | Stage 3 (Standard 이상) |
| `maintainability-reviewer-prompt.md` | 유지보수성/기술부채 평가 | Stage 4 (Comprehensive만) |
| `code-reviewer-prompt.md` | Spec + Quality 통합 | 이 스킬에서 사용하지 않음 (construction-orchestrator 간편 리뷰용) |

---

## 리뷰 시점 가이드

**필수:**
- 태스크/유닛 구현 완료 후
- PR/머지 전

**권장:**
- 복잡한 리팩토링 후
- 버그 수정 후 (회귀 테스트와 함께)
- 아키텍처 변경이 포함된 작업 후

---

## Examples

### Example 1: Standalone — PR 전 리뷰 (Standard)

```
사용자: "이 변경사항 리뷰해줘"

[depth: Standard, spec 미제공]
→ Stage 1 스킵 (spec 없음)
→ Stage 2: code-quality-reviewer dispatch → PASS
→ Stage 3: security-reviewer dispatch → PASS
→ Verdict: PASS / Recommendations 2건
```

### Example 2: SDD에서 자동 호출 (Standard)

```
SDD: 태스크 3 완료, requesting-code-review 호출
  리뷰 대상: src/auth.py, tests/test_auth.py
  spec: docs/plans/auth-plan.md Task 3
  depth: Standard

→ Stage 1: spec-reviewer → FAIL (누락된 에러 핸들링)
→ 수정 후 재리뷰 → PASS
→ Stage 2: code-quality-reviewer → PASS
→ Stage 3: security-reviewer → PASS
→ Verdict: PASS
```

### Example 3: Comprehensive 리뷰

```
[depth: Comprehensive, spec 제공]
→ Stage 1: spec-reviewer → PASS
→ Stage 2: code-quality-reviewer → PASS
→ Stage 3 + 4 병렬 dispatch:
  → security-reviewer → FAIL (SQL injection 위험)
  → maintainability-reviewer → PASS
→ 수정 후 Stage 3 재리뷰 → PASS
→ Verdict: PASS / Recommendations 1건
```

### Example 4: Agent Teams 협업 리뷰 (Standard)

```
사용자: "팀 리뷰로 해줘" (R3 선택)

[depth: Standard, spec 미제공]
→ TeamCreate: "code-review-auth"
→ Agent spawn (Explore):
  - quality-reviewer: 코드 품질 분석 시작
  - security-reviewer: 보안 분석 시작
→ quality-reviewer → security-reviewer DM: "입력 검증 누락 발견 (auth.py:42)"
→ security-reviewer: DM 반영하여 injection 경로 추가 분석
→ 결과 종합:
  - Cross-cutting: 입력 검증 누락이 품질+보안 모두에 영향
  - Issues: Important 2건 (중복 제거됨, 원래 3건)
→ TeamDelete
→ Verdict: CONDITIONAL / Important 2건
```

---

## Troubleshooting

### Stage 1에서 반복 실패

**증상**: spec compliance 리뷰가 5회 넘게 실패
**원인**: spec 자체가 모호하거나 현재 구현과 맞지 않음
**해결**: 사용자 escalate 후 spec 수정 또는 Stage 1 스킵 결정

### Standalone에서 Stage 1이 항상 스킵됨

**증상**: spec/plan 경로를 제공하지 않아 항상 Stage 2만 실행
**해결**: 리뷰 요청 시 관련 spec/plan 경로를 함께 전달. 예: "docs/plans/xxx-plan.md의 Task 2 기준으로 리뷰해줘"
