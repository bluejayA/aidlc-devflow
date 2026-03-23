# Interrupt Handler Pattern

<!-- 글로벌 인터럽트: 게이트 응답이 선택지 밖일 때 의도 분류 → 라우팅 → 복귀 -->

## 적용 시점

사용자 응답이 현재 게이트의 선택지(A/B/C/R/H 등)가 아닌 자유 발화일 때 발동한다.
단, 선택지에 대한 부연("B로 할게, 근데...")은 정상 응답으로 처리한다.

## 의도 분류 테이블

| 의도 신호 (한/영) | 라우팅 대상 |
|------------------|-----------|
| 버그, 에러, 실패, 안됨, bug, error, fail | `aidlc-systematic-debugging` |
| 계획 수정, plan 변경, 다시 계획 | `aidlc-writing-plans` |
| 설계 재검토, 다시 생각, 방향 변경, redesign | `aidlc-brainstorming` |
| 테스트 작성, TDD, 테스트부터 | `aidlc-test-driven-development` |
| 브랜치 정리, PR, 머지, merge, 완료 처리 | `aidlc-finishing-a-development-branch` |
| **위에 해당 없음** | **사용자에게 의도 확인 질문** |

## 인터럽트 게이트 UX

인터럽트 감지 시 아래 형식으로 사용자에게 확인한다. 조용히 라우팅하지 않는다.

```
현재 [stage-name] 단계를 진행 중입니다.
요청하신 내용은 [target-skill]에 해당합니다.

A) 현재 작업 중단하고 [target-skill] 진행 (완료 후 현재 지점으로 복귀)
B) 현재 게이트에서 계속 진행
```

매칭 실패 시:
```
현재 [stage-name] 단계를 진행 중입니다.
요청하신 내용이 아래 중 어디에 해당하나요?

A) 버그/에러 조사 → systematic-debugging
B) 계획 수정 → writing-plans
C) 설계 재검토 → brainstorming
D) 현재 게이트에서 계속 진행
```

## 상태 저장

A 선택 시 devflow-state.md에 중단 지점을 기록한다:

```markdown
## Interrupted At
CONSTRUCTION/code-generation/code-plan

## Interrupt Reason
[사용자 원문 요약]
```

## 복귀 프로토콜

인터럽트 스킬 완료 후:

```
[target-skill] 완료.

A) [stage-name] 게이트로 복귀 (중단 지점에서 재개)
B) 다른 작업 진행
```

A 선택 시 `## Interrupted At` 필드를 제거하고 해당 게이트를 재표시한다.
