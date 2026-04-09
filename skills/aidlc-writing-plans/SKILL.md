---
name: aidlc-writing-plans
description: |
  설계 문서를 상세 구현 계획으로 변환하거나, "구현 계획 작성", "plan 만들어줘" 요청 시 사용. INCEPTION 워크플로우 계획은 aidlc-workflow-planning 사용.
  Use when a design document needs to be converted into a detailed implementation plan with task breakdown, or when "구현 계획 작성", "plan 만들어줘" is requested. Not for INCEPTION workflow planning — use aidlc-workflow-planning instead.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
---

# Writing Plans

<!-- 출력 언어: 한국어 (Korean) -->

설계 문서(spec)를 엔지니어가 zero context에서도 실행 가능한 구현 계획으로 변환한다.

**시작 시 선언**: "aidlc-writing-plans 스킬을 사용하여 구현 계획을 작성합니다."

## Scope Check

스펙이 여러 독립 서브시스템을 포함하면 서브시스템별로 계획을 분리한다.

## Complexity-Based Detail

설계 문서의 `Complexity` 값을 읽어 태스크 상세도 결정. 없으면 직접 판단.

| Complexity | 태스크 수 | 코드 포함 | Architecture |
|------------|-----------|-----------|--------------|
| Minimal | 1-3개 | 핵심 변경만 | 1문장 |
| Standard | 3-7개 | 주요 코드 | 2-3문장 |
| Comprehensive | 7개+ | 전체 코드 | 전체 섹션 |

복잡도 무관 필수 항목: 정확한 파일 경로, TDD 사이클 체크박스, 커밋.

## File Structure

태스크 정의 전 파일 구조 설계:
- 파일당 한 가지 책임
- 함께 변경되는 파일은 함께 배치
- 기존 코드베이스 패턴 따름

## Plan Document Header (필수)

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** [한 줄]
**Complexity:** [Minimal | Standard | Comprehensive]
**Architecture:** [2-3문장]
**Tech Stack:** [주요 기술]
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/test.py`

- [ ] **Step 1: Write failing test**
[완성된 테스트 코드]

- [ ] **Step 2: Run test — verify FAIL**
Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "..."

- [ ] **Step 3: Write minimal implementation**
[완성된 구현 코드]

- [ ] **Step 4: Run test — verify PASS**
Expected: PASS

- [ ] **Step 5: Commit**
````

## Bite-Sized Granularity

각 Step은 한 가지 행동 (2-5분):
- "실패하는 테스트 작성" — Step
- "실행하여 실패 확인" — Step
- "최소 구현" — Step
- "테스트 통과 확인" — Step
- "커밋" — Step

## Self-Review Checklist

작성된 구현 계획을 아래 3항목으로 셀프리뷰한다. 이슈 발견 시 즉시 인라인 수정 후 재저장. re-review 없이 Plan Review Loop로 진행.

1. **Spec coverage** — 스펙의 각 섹션/요구사항에 대응하는 구현 태스크가 있는가? 갭이 있으면 나열
2. **Placeholder scan** — TBD, TODO, 모호한 단계, 누락된 코드 블록, 불완전한 파일 경로가 있는가?
3. **Type consistency** — 타입, 메서드 시그니처, 속성명이 태스크 간 일관적인가? (예: Task 2에서 `userId`인데 Task 5에서 `user_id`)

수정 사항이 있으면 파일 업데이트 후 Plan Review Loop로 진행.

## Plan Review Loop

청크(≤1000줄) 단위로 작성 후 리뷰 (conventions 리뷰 루프 규약 참조):

1. **Minimal / Standard / Comprehensive depth**:
   - 청크 작성 완료
   - `_shared/reviewers/plan-document-reviewer-prompt.md`를 서브에이전트로 dispatch
   - ❌ Issues Found → 수정 후 re-dispatch (최대 5회)
   - Recommendations만 → 루프 종료 (수정 권장)
   - 5회 초과 → 사용자 escalate

> **Codex 세컨드 오피니언**: 구현 계획에 대해 추가 검증이 필요하면 `/codex:adversarial-review`를 직접 실행할 수 있다.
3. 승인 → 다음 청크 또는 Execution Handoff

## Execution Handoff

계획 저장 후:

> "계획이 `docs/plans/<파일명>`에 저장되었습니다. 실행하시겠습니까?"

- 서브에이전트 가능 → `aidlc-subagent-driven-development` (권장)
- 별도 세션 → `aidlc-executing-plans`

## 핵심 규칙

- 정확한 파일 경로 (상대 경로 금지)
- 완성된 코드 ("검증 추가" 같은 추상적 지시 금지)
- 정확한 실행 명령 + 예상 출력
- DRY, YAGNI, TDD, 빈번한 커밋

---

**저장 경로**: `docs/plans/YYYY-MM-DD-<feature-name>-plan.md`
