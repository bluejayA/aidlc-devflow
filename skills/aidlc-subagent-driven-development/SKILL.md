---
name: aidlc-subagent-driven-development
description: 구현 계획을 태스크별 서브에이전트로 실행. Fresh subagent per task + two-stage review.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
---

# Subagent-Driven Development

태스크별 신규 서브에이전트를 디스패치하여 구현하고, 2단계 리뷰(spec → quality)로 품질을 보장한다.

**시작 시 선언**: "aidlc-subagent-driven-development 스킬을 사용하여 계획을 실행합니다."

> Subagent Dispatch Rules: `_shared/devflow-conventions.md` 참조.

## When to Use

- 현재 세션에서 계획 실행 시 (별도 세션: `aidlc-executing-plans`)
- 태스크가 대부분 독립적일 때
- 서브에이전트 지원 환경 (Claude Code 등)

## 프로세스 (태스크 반복)

> **순차 실행 필수**: Task 1의 리뷰까지 완전 완료 → Task 2 시작. 태스크 간 병렬 실행 금지.

### 1. 계획 읽기
- 계획 파일에서 전체 태스크 텍스트 + 컨텍스트 추출
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

### 4. Spec Compliance 리뷰
- `_shared/reviewers/spec-reviewer-prompt.md` 템플릿 사용
- ❌ 이슈 → 구현자 수정 → 재리뷰 (반복)
- ✅ 통과 → Code Quality 리뷰로

### 5. Code Quality 리뷰
- **Spec 통과 후에만 실행** (순서 변경 금지)
- `_shared/reviewers/code-quality-reviewer-prompt.md` 템플릿 사용
- ❌ 이슈 → 구현자 수정 → 재리뷰
- ✅ 통과 → 태스크 완료

### 6. 태스크 완료 표시

### 7. 전체 완료
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
  → Spec 리뷰 ✅ → Quality 리뷰: Minor 1건 → 수정 → ✅
  → Task 1 완료

Task 2:
  → 구현자 디스패치 → 구현 완료
  → Spec 리뷰 ❌ (누락 1건) → 수정 → ✅
  → Quality 리뷰 ✅
  → Task 2 완료

...전체 완료 → 최종 리뷰 → finishing-branch
```

## Integration

- **호출하는 스킬**: `aidlc-writing-plans` (Execution Handoff)
- **완료 시 호출**: `aidlc-finishing-a-development-branch`
- **TDD 준수**: `_shared/tdd-protocol.md`
- **서브에이전트 프롬프트**: `_shared/reviewers/`
