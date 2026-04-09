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

## Instruction Priority

충돌 시 우선순위:

1. **사용자 지시** (CLAUDE.md, 프로젝트 설정, 직접 요청) — 최우선
2. **스킬 규칙** (SKILL.md, `_shared/` 규약) — 기본 동작 오버라이드
3. **기본 동작** (시스템 프롬프트) — 최하위

사용자 지시가 스킬 규칙과 충돌하면 사용자 지시를 따른다. 예: CLAUDE.md가 "TDD 불필요"라고 하면 tdd-protocol의 Iron Law보다 사용자 지시 우선.

## YAML 메타데이터 규약

### invoke_mode

- `orchestrator-only`: **상위 오케스트레이터만** 호출 가능. 사용자 직접 호출 불가.
  - Phase Orchestrator → Entry Orchestrator만 호출
  - Stage Skill → Phase Orchestrator만 호출
- `user-invocable`: 사용자가 직접 호출 가능. 오케스트레이터 워크플로우 외부에서 독립적으로 사용

### return_behavior

- `stop-no-gate`: 실행 완료 후 결과 표시하고 STOP. 오케스트레이터 게이트 제시 금지. 단, 스킬 내 단계별 사용자 확인(섹션별 승인 등)은 허용 — 이는 게이트가 아닌 작업 진행 방식.
- `stop-with-gate`: 스킬 내부에서 사용자 승인을 받고 STOP (예외적 사용)

## 게이트 패턴 규약

Phase 오케스트레이터가 사용하는 게이트 패턴은 `_shared/gate-patterns.md`에 정의:
- **표준 게이트**: A) 변경 요청 / B) 승인
- **조건부 게이트**: 반환값 패턴에 따라 선택지 분기
- **리뷰 연계 게이트**: 리뷰 결과를 포함하는 게이트
- **인터럽트 게이트**: 선택지 밖 자유 발화 시 의도 분류 → 라우팅 (모든 게이트에 암묵적 적용)

### 인터럽트 프로토콜

사용자가 게이트 선택지 밖의 요청을 할 때의 처리 규약. `_shared/patterns/interrupt-handler.md`에 정의.

- **적용 범위**: `construction-orchestrator`, `inception-orchestrator`의 모든 게이트
- **using-devflow와의 관계**: entry orchestrator의 "Auxiliary Skill 라우팅"은 Phase 레벨에서 작동. 인터럽트 핸들러는 sub-orchestrator의 게이트 레벨에서 작동. 두 메커니즘은 상호 보완적이며 충돌하지 않음
- **핵심 원칙**: 조용히 라우팅 금지. 항상 사용자에게 현재 단계 + 대상 스킬을 표시하고 확인을 받은 후 라우팅

## 리뷰 규약

### Depth 정책
- **Minimal / Standard**: R1 단일 리뷰어 순차 dispatch
- **Comprehensive**: R1 기본 + Maintainability 추가 (4-stage)
- depth 확인 (fallback 우선순위):
  1. 호출 텍스트의 인라인 depth 신호
  2. `workflow-plan.md`의 `## Stage Depths`
  3. `devflow-state.md`의 `## Complexity`

### 타임아웃 정책

| 설정 | 기본값 | 비고 |
|------|--------|------|
| 개별 리뷰어 타임아웃 | 300초 | 사용자 자유 발화로 세션별 오버라이드 가능 |
| R3 팀 전체 타임아웃 | 600초 | ��용자 자유 발화로 세션별 오버라이드 가능 |

타임아웃 발생 시:
- 해당 stage "⏭ 타임아웃" 표시, 나머지 stage 결과로 Verdict 종합
- 모든 리뷰어 타임아웃 → 사용자 escalate: "리뷰 실행 불가. A) 재시도 / B) 리뷰 스킵"

> R2 (Council)는 기존 council-review-protocol.md 타임아웃 정책을 유지한다.

### 병렬화 정책

- **Standard**: Stage 2 (Quality) + Stage 3 (Security) 병렬 dispatch
- **Comprehensive**: Stage 2 + Stage 3 + Stage 4 병렬 dispatch
- Stage FAIL 시: FAIL stage만 수정 루프 진입, PASS stage는 재실행하지 않음

### Codex 세컨�� 오피니언

Codex CLI 설치 시(`command -v codex`) 리뷰에 병렬로 Codex를 실행한다.
감지는 세션당 1회, 결과 캐싱. 미설치 시 "ℹ Codex 미설치 �� Claude 단독 리뷰로 진행합니다." (세션당 1회 ��내).

| Phase | Codex 도구 | 실행 방식 |
|-------|-----------|----------|
| CONSTRUCTION Stage 2 | `/codex:review` | 자동 — requesting-code-review가 메인에서 병렬 실행 |
| INCEPTION Spec/Plan | `/codex:adversarial-review` | 수동 — 사용자가 필요 시 직접 실행 |

- Verdict에는 Claude 결과만 반영
- Codex 결과는 "참고 의견" / "약점 분석"으로 별도 표시
- Codex 타임아�� 시 Claude 결과만으�� 진행

### 리�� 루프
1. `_shared/reviewers/[type]-prompt.md` 읽기
2. 서브에이전트 dispatch (산출물 경로 전달)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues Found → 수정 후 re-dispatch (최대 5회)
5. Recommendations만 있음 (Issues 없음) → 루프 종료 (수정은 권장)
6. 5회 초과 시 사용자 escalate

### 리뷰어 프롬프트
- `_shared/reviewers/spec-document-reviewer-prompt.md` — 설계 문서 (brainstorming)
- `_shared/reviewers/plan-document-reviewer-prompt.md` — 구현 계획 (writing-plans)
- `_shared/reviewers/artifact-reviewer-prompt.md` — INCEPTION 산출물
- `_shared/reviewers/code-plan-reviewer-prompt.md` — 코드 계획
- `_shared/reviewers/code-reviewer-prompt.md` — 구현 코드 Spec + Quality 통합 (construction-orchestrator 간편 리뷰용)
- `_shared/reviewers/spec-reviewer-prompt.md` — Spec compliance 단독 검증 (requesting-code-review Stage 1)
- `_shared/reviewers/code-quality-reviewer-prompt.md` — 코드 품질 단독 검증 (requesting-code-review Stage 2)
- `_shared/reviewers/security-reviewer-prompt.md` — 보안/엣지케이스 심층 분석 (Standard 이상)
- `_shared/reviewers/maintainability-reviewer-prompt.md` — 유지보수성/기술부채 평가 (Comprehensive)

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
5. **사용자 질문 설계**: `_shared/patterns/question-format-guide.md` — 선택지 설계, 수준 적응, 모순 감지
6. **스킬 작성 원칙 참조**: `_shared/patterns/skill-writing-guide.md` — 자유도 설계, 점진적 공개, CSO 심화, 스킬 TDD 방법론
7. **패턴 선택**: `_shared/patterns/skill-pattern-catalog.md` — 7개 패턴 중 적합한 것 선택

## Brainstorming HARD-GATE

새 기능, 컴포넌트, 동작 수정 시 설계 문서 작성 + 사용자 승인 전까지 코드 작성 금지.
"단순해서 설계 불필요"는 합리화 — 모든 프로젝트에 적용.
설계 분량은 복잡도에 따라 조절 (Minimal: 2-5문장, Comprehensive: 전체 섹션).

## TDD Iron Law

실패하는 테스트 없이 프로덕션 코드 작성 금지. 상세: `_shared/tdd-protocol.md` 참조.

## 합리화 방지 원칙

규율 강제 스킬(TDD, 디버깅 등)의 합리화 방지 테이블 작성법과 설득 원칙:
`_shared/patterns/persuasion-principles.md` 참조.

## Subagent Dispatch Rules

- 독립적 태스크 2개 이상일 때만 서브에이전트 디스패치
- 구현 서브에이전트 병렬 실행 금지 (충돌 방지)
- 리뷰 Stage 3 (Security) + Stage 4 (Maintainability)는 병렬 dispatch 허용 (독립적 관점, 상호 의존 없음)
- 코드 리뷰 단계: `aidlc-requesting-code-review` 스킬이 depth에 따라 실행
  - **Standard**: 3-stage (spec compliance → code quality → security)
  - **Comprehensive**: 4-stage (spec compliance → code quality → security + maintainability 병렬)
- Model Selection: mechanical task → haiku, integration → sonnet, architecture/review → opus

## 서브에이전트 컨텍스트 격리

### 원칙
- 서브에이전트에 세션 히스토리 전달 금지 — 태스크에 필요한 최소 컨텍스트만 구성
- 각 서브에이전트는 독립된 컨텍스트에서 실행 (다른 태스크 결과 미전달)

### 필수 포함 항목
- 태스크 명세 (전문 텍스트 — 계획 파일을 직접 읽게 하지 않음)
- 관련 파일 경로
- 기술 제약 / 아키텍처 컨텍스트
- 산출물 형식
- **프로젝트 루트 경로** — 워크트리 사용 시 `devflow-state.md`의 `## Worktree` → `path` 값을 절대 경로로 전달. 워크트리 미사용 시 CWD 전달. 서브에이전트는 이 경로를 기준으로 파일을 읽어야 한다.

### 금지 항목
- 이전 대화 내역
- 다른 태스크의 결과
- 사용자 피드백 원문 (요약만 허용)

### 적용 스킬
- `aidlc-subagent-driven-development` — per-task implementer dispatch
- `aidlc-dispatching-parallel-agents` — 병렬 에이전트 dispatch
- `aidlc-requesting-code-review` — 리뷰어 서브에이전트 dispatch
- `aidlc-executing-plans` — 별도 세션 실행 (세션 자체가 격리)

## Council Review Mode

### 4-stage와 Council의 관계

두 차원은 **직교**한다:
- **4-stage** (관점 축): "무엇을 볼 것인가" — Spec, Quality, Security, Maintainability
- **Council** (실행 주체 축): "누가 볼 것인가" — Claude 단독 vs 다모델 편향 보완

Council 모드에서도 4-stage 관점은 그대로 적용된다. Council이 바꾸는 것은 Stage 2-4의 실행 주체이다. Stage 1(Spec Compliance)은 요구사항 대조(사실 확인)이므로 항상 Claude 서브에이전트가 수행한다.

| Stage | single (R1) | council (R2) | teams (R3) |
|-------|-------------|--------------|------------|
| Stage 1 (Spec) | Claude 서브에이전트 | Claude 서브에이전트 | Claude 서브에이전트 |
| Stage 2 (Quality) | Claude 서브에이전트 | Codex + Claude 의장 | Agent Teams 병렬 리뷰 |
| Stage 3 (Security) | Claude 서브에이전트 | Gemini + Claude 의장 | Agent Teams 병렬 리뷰 |
| Stage 4 (Maintainability) | Claude 서브에이전트 | Codex + Claude 의장 | Agent Teams 병렬 리뷰 |

### 리뷰 모드 4종

| 모드 | 참여 에이전트 | 사용 시점 |
|------|------------|----------|
| **single** | Claude 서브에이전트 | 기존 단일 리뷰 (R1) |
| **council-lite** | Claude 의장 + 외부 AI 1개 | 외부 AI가 1개만 설치된 경우 (R2) |
| **council-full** | Claude 의장 + Codex + Gemini | 외부 AI가 모두 설치된 경우 (R2) |
| **teams** | Agent Teams (리뷰어 간 소통) | 리뷰어 협업이 필요한 경우 (R3) |

### R 서브옵션 규약

게이트에서 `R) 리뷰 요청` 선택 시 서브옵션을 제시한다:
- `R1)` 단일 리뷰 — 기존 동작 유지 (artifact-reviewer 또는 code-quality-reviewer)
- `R2)` Council 리뷰 — CLI 환경에 따라 council-lite 또는 council-full
- `R3)` Agent Teams 협업 리뷰 — 리뷰어 간 소통 기반 (`_shared/patterns/review-team-protocol.md`)
- `Ra)` 자동 선택 — risk score 기반 모드 결정 (기본값)

CLI 감지 → 가용 모드 판별: `_shared/patterns/council-cli-detection.md` 참조

### 결과 저장 경로 규약

- 설계 리뷰: `devflow-docs/inception/design-review-raw/{codex,gemini,synthesis}.md`
- 코드 리뷰: `devflow-docs/construction/{unit}/code-review-raw/{codex,gemini,synthesis}.md`
- council-lite에서 외부 AI가 1개면 해당 AI 이름의 파일 1개만 생성

### 의장 종합 후 사용자 승인 필수

의장(Claude)이 synthesis.md를 작성한 후 반드시:
1. Gate Decision + 내용을 사용자에게 표시
2. 사용자 승인을 대기 (A: 수정 반영 / B: 현재 상태 승인)
3. 사용자 응답 없이 자동 진행 금지

### Graceful Degradation

- 외부 AI CLI 미설치 → single 모드로 폴백 (에러 없음)
- agent-council 플러그인 미설치 → R1만 가용, R2/Ra 비활성 안내
- council 리뷰 중 외부 AI 응답 실패 → 해당 에이전트 결과 없이 의장이 가용한 결과만으로 종합

### 프로토콜 참조

council 리뷰의 상세 절차 (risk scoring, 프롬프트, 스키마, 충돌 해결):
`_shared/reviewers/council-review-protocol.md`

---

## Session Continuity 규약

- `_shared/patterns/session-continuity.md` — 아티팩트 로딩 규칙, session-summary 템플릿, 재검증 프로토콜
- 세션 재개 시 Phase Orchestrator가 이 패턴을 참조하여 컨텍스트 로드
- session-summary.md는 INCEPTION 스테이지 완료, Phase 전환, Unit 완료 시 자동 업데이트
- commit hash는 핵심 전환점에서만 기록 (세션 시작/재개, Phase 전환, Unit 완료)

### Audit 강화 형식
기존 `[timestamp] [stage] — [choice]`에 결정 이유 한 줄 추가:
`[timestamp] [stage] — [choice] — [이유]`
기존 형식도 유효 (하위 호환).

## 산출물 포맷 규약

산출물의 주요 독자가 누구인지에 따라 포맷을 선택한다.

| 독자 | 포맷 | 이유 |
|------|------|------|
| **사람 + AI** (리뷰, 승인, 공유) | Markdown | 가독성, 편집 용이 |
| **AI 전용** (맥락 복원, 중간 상태, 머신 파싱) | JSON / JSONL | 토큰 효율, 파싱 정확도 |

### 판단 기준

"사용자가 이 파일을 열어서 읽거나 승인할 일이 있는가?"
- **Yes** → Markdown
- **No** → JSON/JSONL

### 현재 적용

| 파일 | 독자 | 포맷 |
|------|------|------|
| requirements.md, application-design.md | 사람 + AI | Markdown |
| session-summary.md | 사람 + AI | Markdown |
| devflow-state.md | 사람 + AI | Markdown |
| audit.md | 사람 (디버깅) + AI | Markdown |
| stage-context.jsonl (예정) | AI 전용 | JSONL |

### 새 산출물 추가 시

1. 독자 판단 → 포맷 결정
2. AI 전용이면 JSON/JSONL 우선 검토
3. 사람이 디버깅 목적으로 볼 수 있으면 `cat file | python3 -m json.tool` 등으로 확인 가능한 구조화 포맷 사용
