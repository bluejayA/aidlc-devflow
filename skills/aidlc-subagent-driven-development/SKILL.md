---
name: aidlc-subagent-driven-development
description: Use when executing an implementation plan in the current session with independent tasks that benefit from fresh subagent context per task.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
---

# Subagent-Driven Development

태스크별 신규 서브에이전트를 디스패치하여 구현하고, 2단계 리뷰(spec → quality)로 품질을 보장한다.

**시작 시 선언**: "aidlc-subagent-driven-development 스킬을 사용하여 계획을 실행합니다."

> Subagent Dispatch Rules: `_shared/devflow-conventions.md` 참조.

## When to Use

- 현재 세션에서 계획 실행 시 (별도 세션: `aidlc-executing-plans`)
- 태스크가 대부분 독립적일 때
- 서브에이전트 지원 환경 (Claude Code 등)

## 입력 모드

### 모드 1: 계획 파일 기반 (기본)
사용자가 직접 호출하거나 `aidlc-writing-plans`에서 호출 시. 계획 파일에서 태스크 목록을 읽는다.

### 모드 2: Orchestrator 위임 모드 (units.md 기반)
`aidlc-construction-orchestrator`가 SDD 모드로 호출 시.

**호출 신호**: `"SDD: units=[devflow-docs/inception/units.md], summary=[devflow-docs/session-summary.md], complexity=[level]"`

이 신호를 받으면:
1. units.md에서 unit 목록을 읽고, 각 unit을 태스크로 변환
2. session-summary.md에서 unit 완료 상태 + units.md의 인터페이스 정의만 참조
3. **컨텍스트 격리**: 각 unit 서브에이전트에 이전 unit의 code-plan, 구현 코드, 변경 파일 목록 전달 금지
4. **finishing-branch 비활성화**: orchestrator 위임 모드에서는 `aidlc-finishing-a-development-branch` 호출을 스킵. orchestrator가 후속 처리
5. **최종 코드 리뷰 비활성화**: orchestrator가 build-and-test를 별도 실행하므로 SDD 내 최종 리뷰 스킵
6. 모든 unit의 R1 리뷰 통과 → orchestrator에 제어 반환

## 프로세스 (태스크 반복)

> **순차 실행 필수**: Task 1의 리뷰까지 완전 완료 → Task 2 시작. 태스크 간 병렬 실행 금지.

### 1. 계획 읽기
- **모드 1**: 계획 파일에서 전체 태스크 텍스트 + 컨텍스트 추출
- **모드 2**: units.md에서 unit 목록 추출. 각 unit의 구현 범위를 태스크로 변환
- 태스크 목록 생성

### 2. 구현 서브에이전트 디스패치
- `_shared/reviewers/implementer-prompt.md` 템플릿 사용
- 태스크 전문 + 아키텍처 컨텍스트 제공
- 서브에이전트가 계획 파일을 직접 읽지 않도록 전문 제공

### 3. Implementer Status 처리

| Status | 처리 |
|--------|------|
| **DONE** | Spec 리뷰로 진행 |
| **DONE_WITH_CONCERNS** | 우려사항 읽기 → 정정성/범위 문제면 먼저 해결, 관찰 사항이면 기록 후 진행 |
| **NEEDS_CONTEXT** | 누락 정보 제공 → 재디스패치 |
| **BLOCKED** | 평가: 컨텍스트 문제 → 추가 제공, 추론 한계 → 상위 모델, 태스크 과대 → 분할, 계획 오류 → 사용자 에스컬레이션 |

### 4. Code Review — `aidlc-requesting-code-review` 호출

구현 완료 후 `aidlc-requesting-code-review` 스킬을 호출하여 2-stage review 실행.
- 입력: 변경 파일 + spec/plan 경로 (해당 태스크) + depth (plan Complexity 연동)
- ❌ Issues → 구현자 수정 → 재호출
- ✅ Ready to merge → 태스크 완료

> 리뷰 로직은 `aidlc-requesting-code-review`가 Single Source of Truth. 이 스킬에서 직접 리뷰어를 dispatch하지 않는다.

### 5. 태스크 완료 표시

### 6. 전체 완료
- 모든 태스크 완료 후 최종 코드 리뷰 디스패치
- `aidlc-finishing-a-development-branch` 호출

## Model Selection

| 복잡도 | 모델 | 기준 |
|--------|------|------|
| Mechanical | haiku | 1-2 파일, 명확한 spec, CRUD/설정 |
| Integration | sonnet | 멀티파일, API, 테스트, 리팩토링 |
| Architecture | opus | 설계 판단, 광범위한 코드베이스 이해 |

## Red Flags

- main/master에서 시작 금지 (명시적 승인 없이)
- 리뷰 스킵 금지 (spec OR quality)
- Spec 통과 전 quality 리뷰 시작 금지
- 구현 서브에이전트 병렬 실행 금지
- 서브에이전트 질문 무시 금지
- 리뷰 이슈 미해결 상태로 다음 태스크 진행 금지

## 예시 워크플로우 (축약)

```
[계획 읽기: 5개 태스크 추출]

Task 1:
  → 구현자 디스패치 → 질문 발생 → 답변 → 구현 완료
  → requesting-code-review 호출 → Ready to merge
  → Task 1 완료

Task 2:
  → 구현자 디스패치 → 구현 완료
  → requesting-code-review 호출 → Needs fixes (spec 누락 1건)
  → 구현자 수정 → requesting-code-review 재호출 → Ready to merge
  → Task 2 완료

...전체 완료 → 최종 리뷰 → finishing-branch
```

## Integration

- **호출하는 스킬**: `aidlc-writing-plans` (Execution Handoff)
- **리뷰 위임**: `aidlc-requesting-code-review` (per-task 2-stage review)
- **완료 시 호출**: `aidlc-finishing-a-development-branch`
- **TDD 준수**: `_shared/tdd-protocol.md`
- **서브에이전트 프롬프트**: `_shared/reviewers/implementer-prompt.md`
