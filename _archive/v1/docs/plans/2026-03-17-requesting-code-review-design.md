# requesting-code-review 스킬 추가 설계

**이슈**: #8 ([3/13] requesting-code-review)
**날짜**: 2026-03-17
**상태**: 설계 승인됨

## 배경

aidlc에 receiving-code-review(수신)는 있지만 requesting(요청) 스킬이 없음. 리뷰어 프롬프트 3종(spec-reviewer, code-quality-reviewer, code-reviewer 통합)도 이미 존재. 부족한 건 "언제, 무엇을 리뷰 요청하는가"의 트리거 스킬.

## 설계 결정

- requesting-code-review가 리뷰 로직의 **Single Source of Truth**
- SDD의 자체 2-stage review 로직을 제거하고 이 스킬 호출로 대체 — **per-task review를 대체** (최종 리뷰가 아님. SDD가 각 태스크 완료 시마다 이 스킬 호출)
- DRY: 리뷰 프로세스가 한 곳에만 존재. #6(정적분석) 추가 시에도 이 스킬만 수정

## 리뷰어 프롬프트 관계 정리

| 프롬프트 | 용도 | 사용처 |
|---------|------|--------|
| `spec-reviewer-prompt.md` | Stage 1: spec compliance 단독 | requesting-code-review Stage 1 |
| `code-quality-reviewer-prompt.md` | Stage 2: 코드 품질 단독 | requesting-code-review Stage 2 |
| `code-reviewer-prompt.md` | Spec + Quality 통합 (단일 dispatch) | construction-orchestrator 간편 리뷰 (기존 유지) |

requesting-code-review는 분리 프롬프트(Stage 1 → 2 순차)를 사용. 통합 프롬프트(code-reviewer-prompt.md)는 오케스트레이터의 간편 리뷰용으로 공존.

## 신규: `aidlc-requesting-code-review/SKILL.md`

- invoke_mode: user-invocable
- return_behavior: stop-no-gate

### 프로세스

```
리뷰 요청
  → depth 확인 (Minimal: 스킵, Standard+: 실행)
  → Stage 1: spec-reviewer-prompt.md dispatch → spec compliance
    → Issues → 수정 후 재리뷰 (최대 5회)
    → Recommendations만 → 통과
  → Stage 2: code-quality-reviewer-prompt.md dispatch → 코드 품질
    → Issues → 수정 후 재리뷰 (최대 5회)
    → Recommendations만 → 통과
  → 결과 반환
```

### 입력
- 리뷰 대상 파일 (git diff 또는 파일 경로)
- spec/plan 경로 (선택, spec compliance용) — 미제공 시 Stage 1 스킵, Stage 2만 실행
- depth (호출자 전달 또는 기본 Standard)

### 출력
```
## Code Review 결과
- Stage 1 (Spec Compliance): ✅/❌
- Stage 2 (Code Quality): ✅/❌
- Assessment: Ready to merge / Needs fixes
- Issues: [목록]
- Recommendations: [목록]
```

### Standalone vs SDD 호출
| 모드 | 트리거 | depth |
|------|--------|-------|
| Standalone | 사용자 직접 호출 | 사용자 지정 또는 Standard |
| SDD | 태스크 완료 후 자동 호출 | plan Complexity 연동 |

### 리뷰 시점 가이드
- 필수: 태스크/유닛 구현 완료 후, PR/머지 전
- 권장: 복잡한 리팩토링 후, 버그 수정 후

## 수정: `aidlc-subagent-driven-development/SKILL.md`

- 자체 2-stage review 로직(spec-reviewer dispatch → code-quality-reviewer dispatch) 제거
- per-task 흐름 변경: `Implementer 완료 → aidlc-requesting-code-review 호출 → 결과에 따라 수정/통과 → 다음 태스크`
- 정합성: return_behavior: stop-no-gate 추가 (H1), description을 "Use when..." 형식으로 변경 (H2)

## 수정: `devflow-conventions.md`

"Subagent Dispatch Rules"의 Two-stage review 규칙을 다음으로 변경:
```markdown
- Two-stage review 필수: `aidlc-requesting-code-review` 스킬이 spec compliance → code quality 순서로 실행 (순서 변경 금지)
```

## 수정: `aidlc-code-generation/SKILL.md`

PART 1(Plan) 리뷰 depth 조건 추가 (M1):
- Minimal: 리뷰 스킵
- Standard+: code-plan-reviewer dispatch
(코드 계획 리뷰는 requesting-code-review와 별개)

## 기존 리뷰어 프롬프트 수정 없음

spec-reviewer-prompt.md, code-quality-reviewer-prompt.md 그대로 사용.

## 정합성 이슈 함께 처리

- H1: subagent-driven-development return_behavior 추가
- H2: subagent-driven-development description CSO 수정
- M1: code-generation PART 1 리뷰 depth 조건 명시
