---
name: aidlc-functional-design
description: Use when a unit needs detailed functional design including domain entities, business rules, and API contracts before code generation.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/{unit}/functional-design.md
---

# aidlc-functional-design

unit별 비즈니스 로직을 상세 설계한다. application-design(아키텍처 수준)과 code-generation(구현 수준) 사이의 갭을 메운다.

## 조건부 실행

- **EXECUTE**: 복잡한 비즈니스 로직, 도메인 모델 필요, 다중 엔티티
- **SKIP**: 단순 CRUD, 설정 변경, UI만 수정
- Comprehensive 깊이일 때만 실행 (Minimal/Standard는 skip)

## 실행 모드

오케스트레이터가 인라인 신호로 모드를 전달한다. 모드 선택은 이 스킬에서 하지 않음 (Orchestrator-Centric).

`_shared/patterns/three-mode-selection.md` 참조.

| 모드 | 동작 |
|------|------|
| Together | Step별 순차 설계. 각 Step 사이 사용자 확인 가능 |
| Import | 기존 설계 문서 검증 — 파일 수신 → 형식 검증 → 내용 검토 → 피드백 → 사용자 확정 |
| Skip | devflow-state에 SKIPPED 기록 후 Return to Orchestrator |

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

conventions Review Workflow 적용.
- 산출물: devflow-docs/construction/{unit}/functional-design.md
- 리뷰어: artifact-reviewer-prompt.md

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 엔티티: [count]개
- 비즈니스 규칙: [count]개
- 에러 시나리오: [count]개
- 산출물: devflow-docs/construction/{unit}/functional-design.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal/Standard)]

## Error Handling

### 도메인 지식이 부족할 때
unit의 요구사항(requirements.md)에 비즈니스 규칙이 충분히 기술되지 않은 경우:
- application-design.md에서 해당 unit의 컴포넌트 설명 참조
- 그래도 부족하면 사용자에게 구체적 질문 (예: "결제 실패 시 재시도 정책이 있는가?")
- 가정으로 진행하지 않는다

### Import 문서가 형식에 맞지 않을 때
사용자가 제공한 설계 문서에 필수 섹션(엔티티, 비즈니스 규칙)이 없는 경우:
- 누락 섹션을 명시하고 보완을 요청
- 부분 Import 후 나머지를 Together 모드로 채우는 하이브리드 진행 가능
