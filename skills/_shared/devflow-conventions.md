---
name: devflow-conventions
description: Shared conventions for all AI-DLC stage skills. Defines invoke_mode and return_behavior metadata semantics.
metadata:
  version: 0.5.0
  author: Jay
  category: ai-dlc-workflow
---

# devflow Conventions

<!-- AIDLC 플러그인 아키텍처 가이드 + 스킬 작성 규약 -->

## 아키텍처 개요

AIDLC는 **3단 위임 체인** 구조를 사용한다. 슈퍼에이전트(하나가 모든 것을 처리)가 아닌 경량 위임 구조:

- **Entry Orchestrator** (`aidlc-using-devflow`): Phase 라우터. New/Resume 판별 + Phase 전환만 처리
- **Phase Orchestrator** (`aidlc-inception-orchestrator`, `aidlc-construction-orchestrator`): 스테이지 순서 + 게이트 관리. 실제 작업은 하지 않음
- **Stage Skill**: 실제 작업 수행 + 리뷰 dispatch (해당 시)
- **Review Sub-agent**: 산출물 검증만 (스킬이 dispatch)

각 계층은 자기 역할만 하고 빠진다. 이를 통해 현재 Phase에 필요한 컨텍스트만 로드하여 토큰 효율을 확보한다.

## YAML 메타데이터 규약

### invoke_mode

- `orchestrator-only`: **상위 오케스트레이터만** 호출 가능. 사용자 직접 호출 불가.
  - Phase Orchestrator → Entry Orchestrator만 호출
  - Stage Skill → Phase Orchestrator만 호출
- `user-invocable`: 사용자가 직접 호출 가능. 오케스트레이터 워크플로우 외부에서 독립적으로 사용

### return_behavior

- `stop-no-gate`: 실행 완료 후 결과 표시하고 STOP. 승인 게이트는 상위 오케스트레이터가 소유.
- `stop-with-gate`: 스킬 내부에서 사용자 승인을 받고 STOP (예외적 사용)

## 게이트 패턴 규약

Phase 오케스트레이터가 사용하는 게이트 패턴은 `_shared/gate-patterns.md`에 정의:
- **표준 게이트**: A) 변경 요청 / B) 승인
- **조건부 게이트**: 반환값 패턴에 따라 선택지 분기
- **리뷰 연계 게이트**: 리뷰 결과를 포함하는 게이트

## 리뷰 규약

### Depth 정책
- **Minimal**: 리뷰 스킵, 바로 Return to Orchestrator
- **Standard / Comprehensive**: 리뷰 서브에이전트 dispatch
- depth 확인: 호출 텍스트의 depth를 우선 사용. 없으면 `devflow-state.md`의 `## Complexity` 필드

### 리뷰 루프
1. `_shared/reviewers/[type]-prompt.md` 읽기
2. 서브에이전트 dispatch (산출물 경로 전달)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회)
5. 5회 초과 시 사용자 escalate

### 리뷰어 프롬프트
- `_shared/reviewers/artifact-reviewer-prompt.md` — INCEPTION 산출물
- `_shared/reviewers/code-plan-reviewer-prompt.md` — 코드 계획
- `_shared/reviewers/code-reviewer-prompt.md` — 구현 코드 (Spec + Quality 통합)

### Escalation 메시지 형식
```
⚠️ 리뷰 루프 5회 초과 — 사용자 판단 필요

리뷰 이력:
- 1회: [이슈 요약]
- ...

A) 현재 상태로 승인
B) 직접 수정 지시
```

## TDD 규약

- `_shared/tdd-protocol.md` — TDD Iron Law, RED-GREEN-REFACTOR, Self-Review 체크리스트, 회귀 테스트 검증
- Construction 스킬 중 코드를 작성/수정하는 스킬은 이 프로토콜을 참조
- 참조 스킬: `aidlc-code-generation`, `aidlc-verification-before-completion`, `aidlc-systematic-debugging`
- 리뷰 시 TDD 준수 확인: `code-reviewer-prompt.md`, `code-plan-reviewer-prompt.md`

## Import-Review 규약

- `_shared/import-review-protocol.md` — GENERATE/IMPORT 모드 전환, Hold/Skip 상태 관리
- Pre-Planning 스테이지(user-stories, nfr-requirements)에서 참조
- 모드 선택은 오케스트레이터가 게이트로 처리 (스킬 내부에서 모드 선택 금지 — Orchestrator-Centric 규칙)

## Return to Orchestrator 규약

모든 `orchestrator-only` 스킬은 실행 완료 후 아래 형식으로 반환:

```
STOP.
[stage-name 결과]
- [핵심 결과 항목들]
- 산출물: [path]
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

- 각 스킬의 SKILL.md에는 반환 필드 목록만 정의한다. 형식 설명은 이 규약을 따른다.
- `return_behavior: stop-no-gate` 스킬은 게이트를 제시하지 않는다.
- STOP 후 게이트는 상위 오케스트레이터가 처리한다.

## 산출물 미발견 시 공통 처리

입력 산출물 파일이 없으면:
- "⚠️ [파일명]을 찾을 수 없습니다" 표시
- 사용 가능한 컨텍스트만으로 진행
- 산출물에 누락 사실 기록

## Complexity와 Stage Depth

- **Complexity**: 프로젝트 전체 복잡도. INCEPTION 초기에 선언 (Minimal/Standard/Comprehensive).
- **Stage Depth**: 개별 스테이지 실행 깊이. workflow-planning에서 Stage별로 결정.
- **기본 규칙**: Stage Depth는 Complexity를 따르되, workflow-planning이 override 가능.
- **전달 방식**: 오케스트레이터가 스킬 호출 시 인라인 텍스트로 depth를 전달.
  스킬은 호출 텍스트의 depth를 우선 사용하고, 없으면 devflow-state.md에서 읽는다.

## 용어

| 용어 | 정의 |
|------|------|
| **unit** | 독립적으로 구현·테스트 가능한 개발 단위. story(사용자 가치)나 component(아키텍처 단위)와 다름. 구현 순서와 병렬성을 결정하기 위한 분해 단위. |
| **Orchestrator-Centric** | 오케스트레이터가 게이트·상태·라우팅을 소유하고, stage skill은 순수 실행자인 아키텍처. |
| **Pre-Planning** | requirements-analysis와 workflow-planning 사이의 조건부 단계 (user-stories, nfr-requirements). |
| **depth** | 개별 스테이지의 실행 깊이 (Minimal/Standard/Comprehensive). Complexity와 구분. |

## 새 스킬 추가 가이드

1. **frontmatter 필수 필드**: name, description, metadata (version, author, category, invoke_mode, return_behavior)
2. **리뷰 대상 스킬이면**: 리뷰 규약의 리뷰 루프 패턴 참조. SKILL.md에는 산출물 경로와 리뷰어 종류만 명시
3. **Phase Orchestrator에 등록**: 해당 Phase 오케스트레이터의 스테이지 순회 + 게이트 매핑에 추가
4. **plugin.json**: skills 디렉토리에 자동 인식 (별도 등록 불필요)

## Brainstorming HARD-GATE

새 기능, 컴포넌트, 동작 수정 시 설계 문서 작성 + 사용자 승인 전까지 코드 작성 금지.
"단순해서 설계 불필요"는 합리화 — 모든 프로젝트에 적용.
설계 분량은 복잡도에 따라 조절 (Minimal: 2-5문장, Comprehensive: 전체 섹션).

## TDD Iron Law

실패하는 테스트 없이 프로덕션 코드 작성 금지. 상세: `_shared/tdd-protocol.md` 참조.

## Subagent Dispatch Rules

- 독립적 태스크 2개 이상일 때만 서브에이전트 디스패치
- 구현 서브에이전트 병렬 실행 금지 (충돌 방지)
- Two-stage review 필수: `aidlc-requesting-code-review` 스킬이 spec compliance → code quality 순서로 실행 (순서 변경 금지)
- Model Selection: mechanical task → haiku, integration → sonnet, architecture/review → opus

## Session Continuity 규약

- `_shared/patterns/session-continuity.md` — 아티팩트 로딩 규칙, session-summary 템플릿, 재검증 프로토콜
- 세션 재개 시 Phase Orchestrator가 이 패턴을 참조하여 컨텍스트 로드
- session-summary.md는 INCEPTION 스테이지 완료, Phase 전환, Unit 완료 시 자동 업데이트
- commit hash는 핵심 전환점에서만 기록 (세션 시작/재개, Phase 전환, Unit 완료)

### Audit 강화 형식
기존 `[timestamp] [stage] — [choice]`에 결정 이유 한 줄 추가:
`[timestamp] [stage] — [choice] — [이유]`
기존 형식도 유효 (하위 호환).
