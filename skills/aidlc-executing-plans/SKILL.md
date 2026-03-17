---
name: aidlc-executing-plans
description: Use when executing an implementation plan in a separate session with checkpoint reviews and session resume support.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
---

# Executing Plans

구현 계획 파일을 배치 단위로 실행한다.

**시작 시 선언**: "aidlc-executing-plans 스킬을 사용하여 계획을 실행합니다."

## When to Use

- 별도 세션에서 계획 실행 시 (현재 세션: `aidlc-subagent-driven-development` 사용)
- 서브에이전트 불가 환경
- 순차 실행이 필요한 tightly-coupled 태스크

## 프로세스

### Step 1: 계획 로드

1. 계획 파일 읽기 + 비판적 리뷰
2. 완료된 태스크(`[x]`) 있으면 → 현재 상태 공지 (세션 재개)
3. devflow-audit와 교차 확인
4. 우려사항 있으면 사용자와 논의
5. 우려 없으면 진행

### Step 2: 배치 실행

- 기본 배치 크기: 3 태스크
- 각 태스크: 시작 표시 → 단계 수행(TDD) → 검증 → 완료 표시

### Step 3: 배치 보고

- 구현 내용 요약
- 검증 결과
- "피드백 준비됨" 공지

### Step 4: 계속

- 사용자 피드백 반영
- 다음 배치 실행
- 반복

### Step 5: 완료

- `aidlc-finishing-a-development-branch` 스킬 호출

## 세션 재개

1. `devflow-docs/session-summary.md` 로드 (있으면) — 이전 세션 맥락 확인
2. 체크박스 `[x]` 파싱으로 완료 태스크 식별
3. devflow-audit 교차 확인
4. 재검증 (독립 실행 시에만):
   - construction-orchestrator 경유 호출인 경우 → 재검증 스킵 (이미 Step 1.5에서 완료)
   - 독립 실행인 경우 → 직전 완료 태스크의 테스트 실행
   - 통과 → 다음 태스크부터 재개
   - 실패 → 사용자 게이트:
     ```
     ⚠️ 재검증 실패 — [task-name] 테스트 실패

     A) 전체 테스트 스위트 실행
     B) systematic-debugging으로 조사
     ```
   - debugging 완료 후 재검증 재실행
5. 완료 태스크 건너뛰고 다음부터 재개

## Mid-Execution Changes

| 변경 | 절차 |
|------|------|
| **Skip** | 영향도 설명 → 확인 → `[SKIP]` 마크 → audit 기록 |
| **Restart** | 하위 의존 태스크 나열 → 경고 → 확인 → `[ ]` 재설정 |
| **Insert** | 의존성 분석 → 위치 확인 → `[NEW]` 추가 → 실행 |
| **Edit Plan** | 현재 태스크 완료 → Pause → 편집 → 재개 |
| **Pause** | 현재 태스크 완료 → audit 기록 → 재개 방법 공지 |

## 멈춰야 할 때

- 블로커 발생 (의존성 부재, 테스트 실패, 지시 불명확)
- 계획에 비판적 갭 발견
- 반복 검증 실패

## Integration

- **호출하는 스킬**: `aidlc-writing-plans` (Execution Handoff)
- **완료 시 호출**: `aidlc-finishing-a-development-branch`
- **TDD 준수**: `_shared/tdd-protocol.md`
