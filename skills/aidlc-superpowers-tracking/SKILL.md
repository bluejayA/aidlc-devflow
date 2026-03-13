---
name: aidlc-superpowers-tracking
description: 세션 중 스킬/패턴 사용을 추적하여 워크플로우 개선 인사이트 제공.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
---

# Superpowers Tracking

세션에서 사용된 스킬과 패턴을 추적하고, 워크플로우 개선을 위한 인사이트를 제공한다.

## 핵심 기능

### 1. 세션 요약

devflow-audit.md를 파싱하여:
- 호출된 스킬 목록
- 각 단계의 상태 (완료/스킵/실패)
- 게이트에서의 사용자 선택 패턴

### 2. 패턴 분석

여러 세션의 추적 데이터를 비교하여:
- 자주 스킵되는 단계 → 불필요하거나 개선 필요
- 반복 실패 단계 → 스킬 품질 문제 또는 요구사항 불명확
- 자주 사용되는 조합 → 워크플로우 최적화 기회

### 3. 튜닝 제안

분석 결과 기반:
- "X 단계가 최근 5회 연속 스킵됨 → Minimal 깊이에서 기본 스킵 설정 검토"
- "Y 스킬에서 평균 2회 리뷰 루프 → 프롬프트 개선 검토"

## 산출물

`devflow-docs/tracking/session-{YYYY-MM-DD}.md`

## 데이터 소스

- `devflow-docs/audit.md` (1차 소스 — 중복 저장 안 함)
- `devflow-docs/devflow-state.md` (현재 상태 참조)

## 사용법

- 세션 종료 시 또는 사용자 요청 시 실행
- 자동 실행 없음 (사용자가 `/aidlc-superpowers-tracking` 호출)
