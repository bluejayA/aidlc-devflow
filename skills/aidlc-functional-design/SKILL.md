---
name: aidlc-functional-design
description: Use when a unit needs detailed functional design including domain entities, business rules, and API contracts before code generation.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/{unit}/functional-design.md
---

# Functional Design

unit별 비즈니스 로직을 상세 설계한다. application-design(아키텍처 수준)과 code-generation(구현 수준) 사이의 갭을 메운다.

## 조건부 실행

- **EXECUTE**: 복잡한 비즈니스 로직, 도메인 모델 필요, 다중 엔티티
- **SKIP**: 단순 CRUD, 설정 변경, UI만 수정
- Comprehensive 깊이일 때만 실행 (Minimal/Standard는 skip)

## 실행 모드

`_shared/patterns/three-mode-selection.md` 참조.

| 모드 | 동작 |
|------|------|
| Together | Step별 순차 설계, Hold 가능 |
| Import | 기존 설계 문서 검증 |
| Skip | devflow-state에 SKIPPED 기록 |

## Together 모드 Steps

### Step 1: 도메인 엔티티 정의

- 핵심 엔티티 목록
- 엔티티 간 관계 (1:N, N:M 등)
- 각 엔티티의 핵심 속성 + 불변 조건

### Step 2: 비즈니스 규칙

- 규칙 목록: 조건 → 동작 형식
- 규칙 간 우선순위
- 예외/엣지 케이스

### Step 3: 데이터 흐름

- 입력 → 변환 → 출력 경로
- 에러 전파 경로
- 외부 시스템 연동 포인트

### Step 4: 에러/예외 시나리오

| 시나리오 | 원인 | 처리 방식 | 사용자 메시지 |
|----------|------|-----------|---------------|
| ... | ... | ... | ... |

## code-generation 연결

- 비즈니스 규칙 → 테스트 케이스 도출 (TDD RED)
- 에러 시나리오 → 에러 핸들링 테스트
- 엔티티 불변 조건 → validation 테스트

## Review

`_shared/devflow-conventions.md` Review Workflow 참조.

## Return

```
STOP.

**Functional Design 완료**
- 산출물: `devflow-docs/construction/{unit}/functional-design.md`
- 엔티티: [N]개
- 비즈니스 규칙: [N]개
- 에러 시나리오: [N]개
```
