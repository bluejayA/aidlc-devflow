---
type: pattern
applies_to: [aidlc-inception-orchestrator, aidlc-construction-orchestrator]
status: active
source: manual
last_validated: 2026-04-13
---

# Review Gate Pattern

리뷰 결과(Verdict)에 따른 게이트 분기의 공통 패턴. 오케스트레이터에서 리뷰 결과를 받아 사용자에게 선택지를 제시할 때 이 패턴을 적용한다.

## Verdict 분기

| Verdict | 기본 옵션 |
|---------|----------|
| **PASS** | A) 변경 요청 → 재호출, B) 승인 → 다음 단계 |
| **CONDITIONAL** | A) 변경 요청 → 재호출, B) 승인 → 다음 단계 (수정 권장) |
| **FAIL** | A) 리뷰 이슈 수정 → 재호출, B) 승인 → 다음 단계 |

## 확장 옵션 (오케스트레이터별 선택)

기본 A/B 외에 오케스트레이터가 필요에 따라 추가할 수 있는 옵션:

| 옵션 | 용도 | 사용처 |
|------|------|--------|
| **C) 오버라이드** | FAIL/CONDITIONAL 이슈를 인지하고 현재 상태로 진행. 사유를 devflow-audit에 기록 | construction-orchestrator code-plan 게이트 |
| **S) 리뷰 스킵** | 리뷰어 이슈를 무시하고 진행. audit 기록됨, 다음 단계는 정상 리뷰 | construction-orchestrator code-generation 게이트 |
| **R) 리뷰 모드 변경** | R1/R2/Ra 등 다른 리뷰 모드로 재실행 | inception-orchestrator application-design 게이트 |

## 리뷰 루프 제한

- 최대 5회 re-dispatch (conventions 리뷰 루프 규약 참조)
- 5회 초과 시 conventions escalation 메시지 표시

## 오버라이드 audit 형식

C(오버라이드) 선택 시 devflow-audit에 기록:

```
[timestamp] review-override: [gate-name] — [사용자 사유]
  issues-acknowledged: [리뷰 이슈 목록]
```
