---
name: dispatching-parallel-agents
description: Use when two or more independent tasks can be executed simultaneously,
  when different domains need separate investigation, or when waiting for one task
  to complete before starting another would waste time.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
---

# dispatching-parallel-agents

<!-- 병렬 에이전트 디스패치: 독립적 문제를 동시에 해결 -->

## Trigger

다음 상황에서 이 스킬을 실행한다:

- 2개 이상의 태스크가 동시에 발생했을 때
- 각 태스크가 서로 다른 파일/모듈/도메인을 다룰 때
- 한 태스크의 결과가 다른 태스크의 시작 조건이 아닐 때
- 순차 실행보다 병렬 실행이 명백히 빠를 때
- `units-generation`으로 분해된 여러 unit을 동시에 구현할 때

---

## Purpose

독립적인 문제를 병렬로 처리하여 전체 작업 시간을 줄인다.
단, 잘못된 병렬화는 충돌과 상태 오염을 유발하므로 독립성 검증이 필수다.

---

## 핵심 원칙

> 독립적 문제 도메인당 에이전트 1개, 모두 동시 실행

에이전트를 늘린다고 항상 빠르지 않다. 잘못된 병렬화는 오히려 느리고 오류를 유발한다.

---

## 병렬화 사용 금지 경우

다음 중 하나라도 해당하면 병렬 디스패치를 하지 않는다:

| 금지 조건 | 이유 | 대안 |
|---------|------|------|
| 공유 상태가 있음 (동일 DB, 파일, 전역 변수) | 경쟁 조건 및 상태 오염 | 순차 실행 또는 락 메커니즘 |
| 순차 의존성 있음 (A 완료 후 B 시작) | B가 A 결과에 의존 | A → B 순서로 실행 |
| 한 에이전트 실패가 다른 모든 에이전트를 무의미하게 함 | 낭비 | 실패 가능성 높은 태스크 먼저 순차 실행 |
| 에이전트 간 중간 조율이 필요 | 조율 오버헤드가 병렬화 이익 초과 | 오케스트레이터 패턴으로 설계 재검토 |
| 태스크가 1개뿐 | 병렬화할 대상 없음 | 단일 실행 |

---

## 프로세스

### 1단계: 태스크 독립성 검증

각 태스크 쌍에 대해 다음 질문에 "아니오"여야 병렬화 가능:

```
독립성 체크리스트 (각 태스크 쌍에 대해):
□ 태스크 A의 출력이 태스크 B의 입력인가?
□ 두 태스크가 동일한 파일을 수정하는가?
□ 두 태스크가 동일한 DB 테이블/컬렉션을 수정하는가?
□ 한 태스크의 실패가 다른 태스크를 의미 없게 만드는가?
□ 두 태스크가 동일한 전역/공유 상태에 의존하는가?
```

모든 질문에 "아니오"인 태스크 쌍만 병렬화한다.

태스크 독립성 도표 작성 (3개 이상의 태스크 시):
```
태스크 A: 사용자 인증 모듈 (auth/)
태스크 B: 알림 서비스 (notifications/)
태스크 C: 대시보드 UI (frontend/dashboard/)

A ↔ B: 공유 파일 없음 ✓ 독립
A ↔ C: 공유 파일 없음 ✓ 독립
B ↔ C: 공유 파일 없음 ✓ 독립
→ A, B, C 모두 병렬 가능
```

---

### 2단계: 에이전트 프롬프트 작성

각 에이전트는 오케스트레이터 없이도 완전히 독립적으로 동작할 수 있어야 한다.

**좋은 에이전트 프롬프트 4가지 요소**:

1. **Focused**: 단 하나의 명확한 목표
2. **Self-contained**: 필요한 컨텍스트를 모두 포함 (다른 에이전트에게 묻지 않음)
3. **Specific output**: 구체적인 산출물 명시 (파일 경로, 형식 등)
4. **Constraints**: 절대 하지 말아야 할 것 명시

**에이전트 프롬프트 템플릿**:
```
## 태스크: [태스크명]

### 목표
[단 한 문장으로 무엇을 해야 하는지]

### 컨텍스트
- 프로젝트 루트: [path]
- 작업 디렉토리: [path]
- 관련 파일: [file list]
- 기술 스택: [language, framework, test runner]

### 요구사항
1. [구체적 요구사항 1]
2. [구체적 요구사항 2]
...

### 산출물
- 생성할 파일: [경로 + 용도]
- 완료 기준: [테스트 통과 조건 등]

### 제약사항
- 다음 파일은 절대 수정하지 말 것: [파일 목록]
- 다음 디렉토리 범위 내에서만 작업: [path]
- 완료 후 verification-before-completion 스킬로 검증할 것
```

**나쁜 에이전트 프롬프트 예시** (피해야 할 것):
```
❌ "인증 기능 구현해줘" — 너무 모호, 범위 불명확
❌ "다른 에이전트가 만든 모델을 사용해" — 다른 에이전트에 의존
❌ "알아서 판단해" — Self-contained하지 않음
❌ "모든 관련 파일 수정해도 됩니다" — 범위 제한 없음
```

---

### 3단계: 병렬 디스패치

검증된 에이전트 프롬프트를 동시에 실행한다.

```
## 병렬 디스패치 시작

디스패치하는 에이전트:
- Agent 1: [태스크명] → [담당 디렉토리]
- Agent 2: [태스크명] → [담당 디렉토리]
- Agent 3: [태스크명] → [담당 디렉토리]

독립성 확인: 공유 파일 없음 ✓
```

---

### 4단계: 결과 수집 및 통합

모든 에이전트 완료 후:

1. **각 에이전트 결과 확인**:
   ```
   Agent 1 결과: [성공/실패] — [산출물 목록]
   Agent 2 결과: [성공/실패] — [산출물 목록]
   Agent 3 결과: [성공/실패] — [산출물 목록]
   ```

2. **실패한 에이전트가 있는 경우**:
   - 해당 태스크만 재실행 (나머지는 유지)
   - 실패 원인이 공유 상태 충돌이면 병렬화를 취소하고 순차 실행

3. **통합 테스트 실행** (모든 에이전트 성공 후):
   ```bash
   # 개별 모듈 테스트가 통과했어도 통합 테스트는 별도로 실행
   pytest tests/integration/ -v
   ```

4. **최종 상태 확인**:
   ```bash
   git status  # 예상치 못한 파일 변경 없는지 확인
   git diff --stat
   ```

---

## Examples

### Example 1: 3개 독립 모듈 병렬 구현

**상황**: AI-DLC units-generation이 3개 unit을 생성함
- `notification-model`: DB 모델 정의
- `notification-service`: 비즈니스 로직
- `email-adapter`: 외부 이메일 API 연동

**독립성 확인**:
```
notification-model ↔ notification-service: service가 model을 사용 ← 의존성 발견!
notification-model ↔ email-adapter: 공유 없음 ✓
notification-service ↔ email-adapter: 공유 없음 ✓
```

**수정된 계획**:
- 1차 병렬: `notification-model` (단독) — model이 먼저 완성되어야 service가 사용 가능
- 2차 병렬: `notification-service` + `email-adapter` (동시)

**Agent 2 프롬프트 예시**:
```
## 태스크: notification-service

### 목표
알림 생성, 조회, 삭제 비즈니스 로직 구현

### 컨텍스트
- 작업 디렉토리: src/notifications/
- notification-model은 이미 완성됨: src/notifications/models.py
- 테스트 러너: pytest

### 요구사항
1. NotificationService 클래스 구현
2. create_notification(), list_notifications(), delete_notification() 메서드 구현
3. TDD: 테스트 먼저 작성 후 구현

### 산출물
- src/notifications/service.py
- tests/test_notification_service.py
- 완료 기준: pytest tests/test_notification_service.py -v → all passed

### 제약사항
- src/notifications/models.py 수정 금지
- src/email/ 디렉토리 접근 금지
```

---

### Example 2: 코드베이스 분석 병렬화

**상황**: 레거시 시스템 분석 — 3개 영역을 동시에 조사

**태스크 분해**:
```
Agent 1: API 엔드포인트 목록 작성 (src/api/ 분석)
Agent 2: DB 스키마 문서화 (migrations/ + models/ 분석)
Agent 3: 외부 의존성 목록 작성 (requirements.txt + import 분석)
```

**독립성**: 모두 읽기 전용 분석, 파일 수정 없음 → 완전 독립 ✓

**결과 통합**:
```
Agent 1: 23개 엔드포인트 → devflow-docs/analysis/api-endpoints.md
Agent 2: 15개 테이블 → devflow-docs/analysis/db-schema.md
Agent 3: 42개 의존성 → devflow-docs/analysis/dependencies.md
```

---

## Troubleshooting

### 에이전트가 서로의 파일을 수정하는 충돌이 발생할 때

**증상**: Agent 1과 Agent 2가 같은 `__init__.py`나 `settings.py`를 수정함

**처리 방법**:
1. 실행을 중단한다
2. 충돌 파일을 식별한다: `git diff --name-only HEAD`
3. 공유 파일을 어떻게 처리할지 결정한다:
   - 공유 파일은 별도 "공통 기반" 에이전트가 처리
   - 나머지 에이전트는 공통 기반 완료 후 병렬 실행
4. 충돌한 변경사항을 수동으로 병합하거나 한쪽을 되돌린다

---

### 에이전트 하나가 실패하고 나머지는 성공했을 때

**증상**: Agent 1 성공, Agent 2 실패, Agent 3 성공

**처리 방법**:
1. Agent 1, 3의 결과를 보존한다 (되돌리지 않음)
2. Agent 2만 별도로 재실행한다:
   - 실패 원인 파악 (`systematic-debugging` 스킬 활용)
   - 프롬프트를 더 구체적으로 수정 후 재시도
3. Agent 2 재실행 시 Agent 1, 3의 산출물이 영향을 주는지 확인한다
4. 모든 에이전트 완료 후 통합 테스트를 실행한다
