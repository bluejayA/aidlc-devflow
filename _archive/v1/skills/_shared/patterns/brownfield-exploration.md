---
type: pattern
applies_to: [aidlc-brainstorming]
status: active
source: manual
last_validated: 2026-04-13
---

# Brownfield Exploration

기존 코드베이스에서 작업할 때의 탐색 프로토콜.

## 탐색 순서

1. **설계 문서 확인**: `devflow-docs/inception/` 또는 `docs/plans/`에 기존 분석 결과가 있는지 확인
2. **있으면**: 기존 분석 결과 참조 + `git log`로 이후 변경사항만 확인
3. **없으면**: 아래 전체 체크리스트 실행

## 전체 탐색 체크리스트

| 항목 | 확인 대상 | 방법 |
|------|-----------|------|
| 프로젝트 구조 | 디렉토리 레이아웃, 진입점 | `ls`, README |
| 의존성 | 패키지 매니저, 주요 라이브러리 | package.json, go.mod, Cargo.toml 등 |
| 기존 패턴 | 네이밍, 아키텍처, 에러 처리 | 핵심 파일 샘플링 (아래 참조) |
| 최근 변경 | 활발한 영역, 진행 중 작업 | `git log --oneline -20` |
| 테스트 구조 | 테스트 프레임워크, 디렉토리, 실행 방법 | 테스트 파일 탐색 |
| 영향 범위 | 변경 시 영향받는 컴포넌트 | import/dependency 추적 |
| 기존 문서 | README, CLAUDE.md, docs/, ADR | 존재 여부 + 핵심 내용 확인 |

## 핵심 파일 샘플링 프로토콜

기존 코딩 패턴을 파악하기 위해 진입점 파일을 선택적으로 읽는다.

### 파일 선택 기준

1. **진입점 우선**: `main.py`, `index.ts`, `app.js`, `cmd/main.go` 등
2. **진입점 없으면**: `src/` 또는 `lib/` 내 가장 작은 파일
3. **선택 수**: 1~2개 (토큰 효율)
4. **크기 제한**: 200줄 이하 전체 읽기, 초과 시 처음 100줄만

### 추출 항목

| 항목 | 관찰 대상 |
|------|----------|
| 네이밍 컨벤션 | camelCase, snake_case, PascalCase, 파일명 규칙 |
| import 구조 | 절대 경로, 상대 경로, alias, 그룹핑 |
| 에러 핸들링 | try-catch, Result/Option, error return, panic |
| 주석 스타일 | JSDoc, docstring, 한국어/영어 혼용, 주석 밀도 |
| 코드 구조 | 함수형, 클래스 기반, 모듈 패턴, 레이어 구조 |

### 결과 활용

- `workspace.md`의 `## Coding Patterns (Sampled)` 섹션에 기록
- code-generation에서 기존 패턴을 존중한 코드 생성에 활용
- 패턴이 불일치하는 코드가 생성되면 리뷰에서 지적 가능

## 핵심 원칙

- **기존 패턴 존중**: 새 패턴 도입 전 기존 방식 확인. 기존 방식이 있으면 따른다.
- **최소 탐색**: 필요한 범위만 탐색. 전체 코드베이스를 읽지 않는다.
- **탐색 결과 선언**: 탐색 완료 시 발견한 패턴/영향범위/컨벤션을 요약 선언.

## 참조하는 스킬

- `aidlc-brainstorming` — 설계 전 컨텍스트 파악
- `aidlc-workspace-detection` — 그린필드/브라운필드 판단 후 브라운필드 시 실행
