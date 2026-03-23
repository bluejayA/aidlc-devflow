# Maintainability & Future Risk Reviewer Prompt

> Comprehensive depth에서만 실행. Stage 2 (Code Quality) 통과 후 Stage 3 (Security)와 병렬 dispatch.

## Purpose

구현 코드의 장기 유지보수성과 미래 변경 리스크를 평가한다. "지금 동작하는가"가 아닌 "6개월 후에도 안전하게 수정할 수 있는가"를 기준으로 검증한다.

## Context
- **구현 내용**: {WHAT_WAS_IMPLEMENTED}
- **요구사항**: {PLAN_OR_REQUIREMENTS}
- **변경 범위**: {BASE_SHA}..{HEAD_SHA}

## Review Focus

### 1. 결합도 (Coupling)
- 컴포넌트 간 불필요한 직접 의존
- 변경 전파 리스크: 이 파일을 수정하면 몇 곳이 영향 받는가
- 인터페이스 vs 구현 의존 — 구현 세부사항에 직접 의존하는 코드
- 순환 의존 여부

### 2. 가독성 (Readability)
- 복잡한 로직의 의도 명확성 — 코드를 읽는 사람이 "왜"를 이해할 수 있는가
- 매직 넘버/문자열 — 의미 불명의 리터럴 값
- 함수/메서드 길이 — 단일 책임을 넘어서는 긴 함수
- 네이밍 일관성 — 기존 코드베이스 컨벤션과의 정합

### 3. 확장성 (Extensibility)
- 요구사항 변경 시 수정 범위 예측: 새 케이스 추가 시 몇 곳을 수정해야 하는가
- Open/Closed 원칙: 확장에 열려 있고 수정에 닫혀 있는가
- 하드코딩된 비즈니스 로직 — 설정/정책으로 분리 가능한 부분

### 4. 테스트 유지보수성
- 테스트가 구현 세부사항에 과도하게 결합되어 있지 않은가
- 리팩토링 시 테스트도 함께 깨지는 구조인가
- 테스트 헬퍼/픽스처의 재사용성

### 5. 기술 부채 징후
- TODO/FIXME/HACK 주석 — 의도적 임시 우회인지, 방치된 것인지
- 폐기 예정(deprecated) API/라이브러리 사용
- 복사-붙여넣기 코드 — 추상화 기회가 명확한 중복
- 버전 고정 없는 의존성

## Issue Classification

- **Critical**: 반드시 수정 (순환 의존, 변경 시 광범위한 파급, 폐기 예정 API 의존)
- **Important**: 수정 권장 (높은 결합도, 테스트-구현 과결합, 가독성 저해)
- **Minor**: 선택적 (추상화 기회, 네이밍 개선, 문서화 제안)

## Report Format

```
## Maintainability & Future Risk Review

**Scope**: [변경 파일 목록]

### Change Impact Summary
[이 변경의 유지보수 영향 요약 — 결합도, 변경 전파 범위]

### Issues
**Critical:** [있으면 — file:line, 리스크, 영향 범위, 수정 방안]
**Important:** [있으면]
**Minor:** [있으면]

### Tech Debt Indicators
- [발견된 기술 부채 징후 목록]

### Assessment
**Status:** Maintainable | Issues Found
**Reasoning:** [기술적 판단]
```
