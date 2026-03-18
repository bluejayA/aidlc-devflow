# 아키텍처 문서

aidlc 플러그인의 내부 구조를 설명합니다. 스킬 개발자와 기여자를 위한 기술 참조 문서입니다.

---

## 3단 위임 체인

```
Entry Orchestrator (aidlc-using-devflow)
  └── Phase Orchestrator
      ├── aidlc-inception-orchestrator
      └── aidlc-construction-orchestrator
          └── Stage Skill (실제 작업 수행)
              └── Review Sub-agent (산출물 검증)
```

각 계층은 자기 역할만 하고 빠진다:
- **Entry Orchestrator**: Phase 라우터. New/Resume 판별 + Phase 전환
- **Phase Orchestrator**: 스테이지 순서 + 게이트 관리. 실제 작업 안 함
- **Stage Skill**: 실제 작업 수행 + 리뷰 dispatch
- **Review Sub-agent**: 산출물 검증만

---

## Phase 구조

### INCEPTION

```
workspace-detection → requirements-analysis → [Pre-Planning] → workflow-planning → [application-design]
```

| 스테이지 | 실행 조건 | 산출물 |
|---------|----------|--------|
| workspace-detection | 항상 | workspace.md |
| requirements-analysis | 항상 | requirements.md |
| user-stories | 조건부 (Pre-Planning) | user-stories.md |
| nfr-requirements | 조건부 (Pre-Planning) | nfr-requirements.md |
| workflow-planning | 항상 | workflow-plan.md |
| application-design | 조건부 (workflow-plan) | application-design.md |

### CONSTRUCTION

```
[functional-design] → code-generation → build-and-test → verification
```

Unit별 반복 실행. 각 Unit마다:

| 스테이지 | 실행 조건 | 산출물 |
|---------|----------|--------|
| functional-design | 조건부 | functional-design.md |
| code-generation | 항상 (PART 1: Plan → PART 2: Generate) | code-plan.md + 소스 코드 |
| build-and-test | 항상 | 빌드/테스트 결과 |
| verification | 항상 | 최종 검증 |

---

## 메타데이터 규약

### invoke_mode

| 값 | 의미 | 호출 주체 |
|----|------|----------|
| `orchestrator-only` | 오케스트레이터만 호출 | Phase Orchestrator |
| `user-invocable` | 사용자 직접 호출 가능 | 사용자 또는 오케스트레이터 |

### return_behavior

| 값 | 의미 |
|----|------|
| `stop-no-gate` | 결과 표시 후 STOP. 게이트는 오케스트레이터가 소유. 스킬 내 단계별 사용자 확인은 허용. |
| `stop-with-gate` | 스킬 내부에서 사용자 승인을 받고 STOP |

---

## 게이트 패턴

오케스트레이터가 사용하는 게이트 유형 (`_shared/gate-patterns.md`):

| 패턴 | 선택지 | 사용처 |
|------|--------|--------|
| **표준 게이트** | A) 변경 / B) 승인 | 대부분의 스테이지 |
| **조건부 게이트** | 반환값에 따라 분기 | requirements-analysis (열린 질문 유무) |
| **리뷰 연계 게이트** | A) 수정 / B) 승인 / R) 리뷰 | application-design DETAIL |
| **표준 + Hold** | A) 변경 / B) 승인 / H) 보류 | Pre-Planning 스테이지 |
| **모드 선택** | A) 모드A / B) 모드B / S) 스킵 | nfr-requirements |

---

## Instruction Priority

충돌 시 우선순위:

1. **사용자 지시** (CLAUDE.md, 직접 요청) — 최우선
2. **스킬 규칙** (SKILL.md, `_shared/` 규약)
3. **기본 동작** (시스템 프롬프트) — 최하위

---

## 리뷰 체계

### 리뷰 루프

```
리뷰어 dispatch → Issues 있음? → 수정 → 재dispatch (최대 5회)
                → Recommendations만? → 종료
                → 5회 초과? → 사용자 escalate
```

### 리뷰어 프롬프트

| 프롬프트 | 용도 | 사용 스킬 |
|---------|------|----------|
| `spec-document-reviewer-prompt.md` | 설계 문서 | brainstorming |
| `plan-document-reviewer-prompt.md` | 구현 계획 | writing-plans |
| `artifact-reviewer-prompt.md` | INCEPTION 산출물 | application-design 게이트 |
| `spec-reviewer-prompt.md` | Spec compliance | requesting-code-review Stage 1 |
| `code-quality-reviewer-prompt.md` | 코드 품질 + OWASP | requesting-code-review Stage 2 |
| `code-reviewer-prompt.md` | Spec + Quality 통합 | construction-orchestrator |
| `code-plan-reviewer-prompt.md` | 코드 계획 | code-generation PART 1 |
| `skill-reviewer-prompt.md` | 스킬 검증 | writing-skills REFACTOR |

### Depth 정책

- **Minimal**: 리뷰 스킵
- **Standard/Comprehensive**: 리뷰 자동 실행
- fallback 우선순위: 호출 텍스트 → workflow-plan Stage Depths → devflow-state Complexity

---

## 공유 패턴 (`_shared/patterns/`)

| 파일 | 용도 |
|------|------|
| `three-mode-selection.md` | Together/Import/Skip 모드 |
| `hold-mechanism.md` | 보류(Hold) 상태 관리 |
| `brownfield-exploration.md` | 기존 코드베이스 탐색 |
| `session-continuity.md` | 세션 재개 프로토콜 |
| `skill-best-practices.md` | 스킬 작성 원칙 |
| `persuasion-principles.md` | 규율 강제 언어 설계 |
| `skill-testing-guide.md` | 스킬 TDD 방법론 |
| `skill-pattern-catalog.md` | 7개 스킬 패턴 분류 |
| `question-format-guide.md` | 질문 설계 원칙 |
| `tech-stack-defaults.md` | 기술 카탈로그 |
| `meta-tag-standard.md` | 메타 태그 규격 + 유지보수 |

---

## 메타 태그 시스템

오케스트레이터 SKILL.md에 HTML 주석 형태의 메타 태그가 삽입되어 있다.
이를 통해 **LLM 토큰 0으로** 분기/라우팅/스텝 순서를 정적 검증할 수 있다.

### 태그 타입

| 태그 | 용도 | 예시 |
|------|------|------|
| `@gate` | 분기점 선언 | `<!-- @gate: complexity-declaration -->` |
| `@gate-option` | 선택지 정의 | `<!-- @gate-option: A -> requirements-analysis -->` |
| `@step` | 실행 단계 순서 | `<!-- @step:1 id=workspace-detection -->` |
| `@condition` | 자동 분기 조건 | `<!-- @condition: complexity==Minimal -> workflow-planning -->` |

### 데이터 흐름

```
SKILL.md (메타 태그)
    → [parse-skills.js] → tests/graph/*.json
    → [pytest L1] 구조 무결성 (dead-end, unreachable, circular)
    → [pytest L2] 라우팅 시뮬레이션 (YAML fixtures)
    → [pytest L3] 스텝 순서 + 필수 스텝 검증
```

### 현재 적용 범위

- `aidlc-inception-orchestrator` — 8 steps, 11 gates, 5 conditions
- `aidlc-construction-orchestrator` — 3 steps, 5 gates

규격 상세: `_shared/patterns/meta-tag-standard.md`

---

## 스킬 패턴 7종

| 패턴 | 핵심 | 대표 스킬 |
|------|------|----------|
| **Iron Law** | "NO X WITHOUT Y" 강제 | test-driven-development |
| **Gate** | N지선다 분기 | finishing-a-development-branch |
| **Review Loop** | 산출물 → 리뷰 → 수정 반복 | code-generation |
| **Three-Mode** | Minimal/Standard/Comprehensive | requirements-analysis |
| **Hold/Skip** | Import/Generate + 보류 | nfr-requirements |
| **Orchestrator-Only** | 순수 실행자 | workspace-detection |
| **User-Invocable** | standalone + orchestrator 양용 | brainstorming |

상세: `_shared/patterns/skill-pattern-catalog.md`

---

## 서브에이전트 컨텍스트 격리

- 세션 히스토리 전달 금지 — 태스크에 필요한 최소 컨텍스트만 구성
- 필수: 태스크 명세, 파일 경로, 기술 제약, 산출물 형식
- 금지: 이전 대화, 다른 태스크 결과, 사용자 피드백 원문

---

## 디렉토리 구조

```
skills/
├── aidlc-using-devflow/           ← Entry Orchestrator
├── aidlc-inception-orchestrator/  ← Phase Orchestrator
├── aidlc-construction-orchestrator/
├── aidlc-*/                       ← Stage Skills (20+)
├── _shared/
│   ├── devflow-conventions.md     ← 전체 규약
│   ├── gate-patterns.md           ← 게이트 패턴
│   ├── tdd-protocol.md            ← TDD 규약
│   ├── import-review-protocol.md  ← Import/Generate 프로토콜
│   ├── patterns/                  ← 공유 패턴 (11개, meta-tag-standard 포함)
│   └── reviewers/                 ← 리뷰어 프롬프트 (8개)
├── _utils/
│   ├── devflow-audit/             ← 감사 로그
│   └── devflow-state/             ← 상태 관리
hooks/
├── hooks.json                     ← SessionStart 이벤트
└── session-start                  ← 안내 메시지 출력
tests/
├── validate-skills.sh             ← 구조 검증 스크립트
├── run-all.sh                     ← 전체 테스트 러너 (파서 → pytest)
├── parse-skills.js                ← 메타 태그 파서 (Node.js)
├── conftest.py                    ← pytest 공유 fixtures
├── graph/                         ← 파서 출력 JSON (.gitignore)
├── scenarios/                     ← L2 라우팅 시뮬레이션 YAML fixtures
├── test_meta_tag_format.py        ← 태그 형식 검증
├── test_parser_output.py          ← 파서 출력 검증
├── test_graph_validator.py        ← L1 정적 그래프 검증
├── test_routing_simulator.py      ← L2 라우팅 시뮬레이션
└── test_step_order.py             ← L3 스텝 순서 검증
docs/
├── guide/                         ← 가이드 문서
└── plans/                         ← 설계/구현 계획
```
