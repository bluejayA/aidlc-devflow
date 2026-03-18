---
name: aidlc-requesting-code-review
description: Use when a task or unit implementation is complete and needs code review before merging, or when the user explicitly requests a code review on their changes.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
---

# aidlc-requesting-code-review

<!-- 코드 리뷰 요청의 Single Source of Truth. 2-stage review (spec compliance → code quality) 실행. -->

## Trigger

다음 상황에서 이 스킬을 실행한다:

- 태스크/유닛 구현이 완료되고 머지 전 리뷰가 필요할 때
- PR 생성 전 코드 품질을 확인하고 싶을 때
- 복잡한 리팩토링이나 버그 수정 후 검증이 필요할 때
- `aidlc-subagent-driven-development`가 태스크 완료 후 자동 호출할 때

## Purpose

2-stage code review를 실행하고 결과를 반환한다.
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

### Step 1: Depth 확인

- **Minimal**: 리뷰 스킵. "리뷰 스킵 (Minimal depth)" 반환
- **Standard/Comprehensive**: 아래 Step 1.5로 진행

### Step 1.5: 리뷰 모드 선택 (Standard 이상)

리뷰 모드를 선택한다. 호출 시 모드가 지정되면 해당 모드를 사용하고, 미지정이면 기본값(R1).

```
리뷰 모드:
R1) 단일 리뷰 (기존 2-stage) ← 기본
R2) Council 리뷰
Ra) 자동 선택 (risk score 기반)
```

**R1 선택**: Step 2 → Step 3 → Step 4 (기존 동작 그대로)

**R2/Ra 선택**: Step 2c (Council 리뷰)로 진행

### Step 2: Stage 1 — Spec Compliance (R1 모드)

spec/plan 경로가 제공된 경우에만 실행. 미제공 시 Stage 2로 바로 진행.

1. `_shared/reviewers/spec-reviewer-prompt.md` 읽기
2. 서브에이전트 dispatch — 리뷰 대상 + spec/plan 경로 전달
3. 결과 확인:
   - ✅ Spec compliant → Stage 2로
   - ❌ Issues Found → 수정 후 re-dispatch (conventions 리뷰 루프 규약: 최대 5회, 초과 시 사용자 escalate)
   - Recommendations만 → Stage 2로 (수정 권장)

### Step 3: Stage 2 — Code Quality

1. `_shared/reviewers/code-quality-reviewer-prompt.md` 읽기
2. 서브에이전트 dispatch — 리뷰 대상 전달
3. 결과 확인:
   - ✅ Approved → 결과 반환
   - ❌ Issues Found → 수정 후 re-dispatch (최대 5회)
   - Recommendations만 → 루프 종료 (수정 권장)

### Step 2c: Council 리뷰 (R2/Ra 모드)

R2 또는 Ra 선택 시 기존 2-stage 대신 council 리뷰를 실행한다.

1. `_shared/patterns/council-cli-detection.md` 절차 실행:
   - CLI 감지 → 가용 AI 목록 표시 → 사용자에게 참여 AI 확인 (전부/일부/없이)
   - 사용자 선택으로 모드 확정 (council-full/council-lite/single)
   - Ra 선택 시: 확정된 모드 범위 내에서 Risk Scoring으로 single/council 자동 결정
   - single 확정 시: Step 2(기존 2-stage)로 전환
2. council-review-protocol의 **코드 리뷰용 프롬프트**로 에이전트 dispatch
   - agent-council 플러그인을 통해 외부 AI 호출
   - 리뷰 입력 번들 (파일 경로만 전달):
     - 리뷰 대상: git diff + 변경 파일 경로
     - 참조: 테스트 결과 요약, `requirements.md`
   - council-lite 시: 병합 프롬프트 사용 (1개 AI가 두 관점 수행)
3. 결과 저장: `devflow-docs/construction/{unit}/code-review-raw/{codex,gemini,synthesis}.md`
4. Claude 의장이 개별 결과를 읽고 synthesis.md 작성 (충돌 해결 4단계 적용)
5. **synthesis 결과를 사용자에게 표시 + 승인 대기**:
   ```
   [Council Code Review 결과]
   Gate Decision: [PASS|CONDITIONAL|FAIL]
   Rationale: [판정 근거]
   Action Items: [수정 항목]

   A) 리뷰 반영하여 수정
   B) 현재 상태로 승인
   ```
6. 결과를 Step 4 형식으로 반환 (council 모드 표시 추가)

### Step 4: 결과 반환

```
## Code Review 결과
- Stage 1 (Spec Compliance): ✅ 통과 | ❌ 이슈 | ⏭ 스킵 (spec 미제공)
- Stage 2 (Code Quality): ✅ 통과 | ❌ 이슈
- Assessment: Ready to merge | Needs fixes
- Issues: [있으면 목록]
- Recommendations: [있으면 목록]
```

---

## Standalone vs SDD 호출

| 모드 | 트리거 | spec/plan | depth |
|------|--------|-----------|-------|
| **Standalone** | 사용자 직접 호출 | 사용자 지정 (없으면 Stage 1 스킵) | 사용자 지정 또는 Standard |
| **SDD** | 태스크 완료 후 자동 | 태스크의 spec/plan 경로 | plan Complexity 연동 |

SDD에서 호출 시, SDD가 리뷰 대상(변경 파일)과 spec/plan 경로를 전달한다.

---

## 리뷰어 프롬프트 관계

| 프롬프트 | 용도 | 이 스킬에서의 역할 |
|---------|------|------------------|
| `spec-reviewer-prompt.md` | spec compliance 단독 검증 | Stage 1 |
| `code-quality-reviewer-prompt.md` | 코드 품질 단독 검증 | Stage 2 |
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

### Example 1: Standalone — PR 전 리뷰

```
사용자: "이 변경사항 리뷰해줘"

[depth: Standard, spec 미제공]
→ Stage 1 스킵 (spec 없음)
→ Stage 2: code-quality-reviewer dispatch
→ 결과: ✅ Ready to merge / Recommendations 2건
```

### Example 2: SDD에서 자동 호출

```
SDD: 태스크 3 완료, requesting-code-review 호출
  리뷰 대상: src/auth.py, tests/test_auth.py
  spec: docs/plans/auth-plan.md Task 3
  depth: Standard

→ Stage 1: spec-reviewer → ❌ Issues 1건 (누락된 에러 핸들링)
→ 수정 후 재리뷰 → ✅ Spec compliant
→ Stage 2: code-quality-reviewer → ✅ Approved
→ 결과: Ready to merge
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
