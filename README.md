# aidlc-devflow

[English](README.en.md) | 한국어

![version](https://img.shields.io/badge/version-1.1.0-blue)
![skills](https://img.shields.io/badge/skills-27-green)
![tests](https://img.shields.io/badge/tests-95-brightgreen)

AI-DLC 방법론을 **오케스트레이터 중심 아키텍처**로 구현한 Claude Code 개발 워크플로우 플러그인입니다.

[AI-DLC(AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows)의 컨셉을 최대한 충실하게 반영하고자 하였으며, [Superpowers 플러그인](https://github.com/obra/superpowers) 을 참조하였습니다. 
`aidlc-using-devflow` 하나가 전체 라이프사이클을 소유하고 구동하며, 나머지 stage skill은 순수 실행자로 동작합니다.

> **처음이신가요?** 👉 [AIDLC와 함께 개발하기](docs/guide/how-it-works.md) — 기술 용어 없이 전체 흐름을 쉽게 설명합니다.

> **사용법** 👉 [사용자 가이드](docs/guide/user-guide.md) — 시작, 질문 방식, 게이트, 독립 스킬 사용법

> **커스터마이즈** 👉 [운영자 가이드](docs/guide/operator-guide.md) — 기술 카탈로그, 질문 원칙, 워크플로우 기본값 조정

> **아키텍처** 👉 [아키텍처 문서](docs/guide/architecture.md) — 3단 위임 체인, 리뷰 체계, 스킬 패턴 7종

---

## 작동 방식

소프트웨어 개발을 시작하는 순간, `aidlc-using-devflow`가 자동으로 활성화됩니다.
세션 시작 훅(`hooks/session-start`)이 Claude에 `aidlc-using-devflow` 컨텍스트를 주입하여 개발 요청을 자동으로 감지합니다.

오케스트레이터가 Stage Routing Table에 따라 전체 라이프사이클을 순차적으로 구동합니다.
각 stage 완료 후 오케스트레이터가 직접 승인 게이트를 제시합니다. Stage skill은 실행 결과만 반환하고 즉시 종료합니다.

---

## 워크플로우

### 🔵 INCEPTION — 무엇을 만들지 결정

1. **aidlc-using-devflow** — 진입점. 기존 세션 재개 여부 확인 후 오케스트레이션 시작
2. **aidlc-workspace-detection** — 그린필드/브라운필드 판단. Brownfield 시 technology stack + code structure 수집
3. **aidlc-requirements-analysis** — 적응형 깊이(Minimal / Standard / Comprehensive) 요구사항 분석. 해석이 분기되는 경우 선택지 제시 후 확정
4. **aidlc-user-stories** _(조건부)_ — 요구사항을 INVEST 기준 사용자 스토리로 변환 (Pre-Planning)
5. **aidlc-nfr-requirements** _(조건부)_ — 도메인 컨텍스트 + 프로파일 기반 비기능 요구사항 수집 (Pre-Planning, GENERATE/IMPORT)
6. **aidlc-workflow-planning** — 실행할 단계와 깊이를 계획하고 명시적 승인 요청
7. **aidlc-application-design** _(조건부)_ — 신규 컴포넌트 설계 + NFR Design Patterns (Comprehensive)
8. **aidlc-units-generation** _(조건부)_ — 복잡한 시스템을 병렬 개발 단위로 분해

### 🟢 CONSTRUCTION — 어떻게 만들지 결정

9. **aidlc-using-git-worktrees** _(선택적)_ — workflow-planning 승인 직후, main 브랜치 보호를 위한 격리 워크트리 생성
10. **aidlc-functional-design** _(조건부)_ — Comprehensive 깊이일 때 상세 기능 설계 (도메인 엔티티, 비즈니스 규칙, 데이터 흐름)
11. **aidlc-code-generation** — Plan → 오케스트레이터 승인 → Generate (TDD Iron Law: RED-GREEN-REFACTOR + Self-Review)
12. **aidlc-build-and-test** — 전체 빌드 실행 + 테스트 스위트 실행 + 지침 문서 생성

---

## Skills 목록 (26개)

### AI-DLC 핵심 스테이지

| Skill | 역할 |
|-------|------|
| `aidlc-using-devflow` | 오케스트레이터. 전체 라이프사이클 소유 및 구동 |
| `aidlc-workspace-detection` | 그린필드/브라운필드 판단 + Brownfield 시 tech-stack/code-structure 수집 |
| `aidlc-requirements-analysis` | 적응형 요구사항 분석. 해석 분기 시 선택지 제시 |
| `aidlc-user-stories` | 요구사항을 INVEST 기준 사용자 스토리로 변환 (조건부, Pre-Planning) |
| `aidlc-nfr-requirements` | 도메인 컨텍스트 + 프로파일 기반 비기능 요구사항 수집 (조건부, GENERATE/IMPORT) |
| `aidlc-workflow-planning` | 실행 계획 수립 (순수 실행) |
| `aidlc-application-design` | 컴포넌트/서비스 설계 + NFR Design Patterns (조건부, 순수 실행) |
| `aidlc-units-generation` | 병렬 개발 단위 분해 (조건부, 순수 실행) |
| `aidlc-using-git-worktrees` | workflow-planning 후 격리 개발 워크트리 생성 (선택적) |
| `aidlc-functional-design` | CONSTRUCTION 상세 기능 설계 — 도메인 엔티티, 비즈니스 규칙, 데이터 흐름 (조건부, Comprehensive만) |
| `aidlc-code-generation` | 2단계 코드 생성 — Plan 후 STOP, 승인 후 Generate (TDD Iron Law + Self-Review) |
| `aidlc-build-and-test` | 빌드 실행 + 전체 테스트 스위트 실행 + 참조용 지침 문서 생성 |

### 개발 워크플로우 도구

| Skill | 역할 |
|-------|------|
| `aidlc-brainstorming` | 아이디어를 설계 문서로 전환. HARD-GATE — 설계 승인 전 코드 작성 금지 |
| `aidlc-writing-plans` | 설계 문서를 태스크별 상세 구현 계획으로 변환 |
| `aidlc-test-driven-development` | TDD Iron Law 강제 (Rigid). RED-GREEN-REFACTOR |
| `aidlc-subagent-driven-development` | 태스크별 서브에이전트 실행 + 2단계 리뷰 (spec → quality) |
| `aidlc-executing-plans` | 구현 계획 배치 실행 + 세션 재개 지원 |
| `aidlc-superpowers-tracking` | 세션 스킬 사용 추적 + 워크플로우 개선 인사이트 |

### 개발 품질 도구

| Skill | 역할 |
|-------|------|
| `aidlc-systematic-debugging` | 버그/실패 발생 시 근본 원인 조사 강제 + 실패 이력 분석 |
| `aidlc-verification-before-completion` | 완료 선언 전 실제 검증 명령 실행 강제 + 회귀 테스트 RED-GREEN 검증 |
| `aidlc-finishing-a-development-branch` | 개발 완료 후 병합/PR/유지/폐기 처리 |
| `aidlc-requesting-code-review` | 2-stage 코드 리뷰 요청 (spec compliance → code quality). 리뷰 로직의 Single Source of Truth |
| `aidlc-receiving-code-review` | 코드 리뷰 피드백 수신 시 체계적 처리 |
| `aidlc-dispatching-parallel-agents` | 독립적 태스크를 병렬 서브에이전트로 디스패치 |
| `aidlc-writing-skills` | 새 스킬 개발 시 TDD 방식 + CSO 원칙 적용 |

### 유틸리티

| Skill | 역할 |
|-------|------|
| `_utils/devflow-state` | `devflow-docs/devflow-state.md` 읽기/쓰기 |
| `_utils/devflow-audit` | `devflow-docs/audit.md` append-only 로깅 |

### 공유 규약 문서

| 파일 | 역할 |
|------|------|
| `_shared/devflow-conventions.md` | YAML 메타데이터 + Complexity/Depth 관계 + Return/Review 규약 + HARD-GATE + TDD Iron Law + Subagent 규약 |
| `_shared/tdd-protocol.md` | TDD Iron Law, RED-GREEN-REFACTOR, Self-Review, 합리화 방지, Red Flags, 회귀 테스트 검증 |
| `_shared/gate-patterns.md` | 표준/조건부/리뷰 연계/Hold 변형/모드 선택 게이트 패턴 정의 |
| `_shared/import-review-protocol.md` | GENERATE/IMPORT 모드 정의 + Hold/Skip 시그널 규약 |
| `_shared/patterns/three-mode-selection.md` | Together/Import/Skip 모드 선택 패턴 |
| `_shared/patterns/hold-mechanism.md` | Mid-step Hold 시그널 + Resume 규약 |
| `_shared/patterns/brownfield-exploration.md` | 기존 코드베이스 탐색 프로토콜 |
| `_shared/patterns/session-continuity.md` | 세션 재개 시 아티팩트 자동 로딩 + session-summary 템플릿 + 재검증 프로토콜 |
| `_shared/patterns/skill-writing-guide.md` | 스킬 작성 원칙 + TDD 방법론 — 자유도 설계, 점진적 공개, CSO 심화, 압박 시나리오 |
| `_shared/patterns/persuasion-principles.md` | 규율 강제 스킬의 설득 원칙 — 합리화 방지 테이블 작성법 |
| `_shared/patterns/skill-pattern-catalog.md` | 7개 스킬 패턴 분류 + 선택 가이드 |
| `_shared/patterns/question-format-guide.md` | 질문 설계 원칙 — 선택지 설계, 수준 적응, 모순 감지 |
| `_shared/patterns/tech-stack-defaults.md` | 아키텍처별 기술 카탈로그 — 선택지 생성 데이터 |
| `_shared/reviewers/` | 리뷰 서브에이전트 프롬프트 8종 (artifact, code-plan, code-reviewer, implementer, spec, quality, skill, spec-document, plan-document) |

#### YAML 메타데이터 규약

모든 AI-DLC 스테이지 스킬은 아래 메타데이터 필드를 사용합니다.

| 필드 | 값 | 의미 |
|------|----|------|
| `invoke_mode` | `orchestrator-only` | 오케스트레이터만 호출 가능. 사용자 직접 호출 불가 |
| `invoke_mode` | `user-invocable` | 사용자가 직접 호출 가능한 유틸리티 스킬 |
| `return_behavior` | `stop-no-gate` | 실행 후 결과 표시 및 STOP. 승인 게이트는 오케스트레이터 소유 |
| `output_path` | `devflow-docs/...` | 스테이지 산출물 저장 경로 |

---

## 산출물 구조

모든 설계 결정은 `devflow-docs/`에 자동 저장됩니다.

```
devflow-docs/
├── inception/
│   ├── workspace.md        # 워크스페이스 분석 결과
│   ├── requirements.md     # 요구사항 문서 (해석 확정 포함)
│   ├── user-stories.md     # 사용자 스토리 (조건부)
│   ├── nfr-requirements.md # 비기능 요구사항 (조건부)
│   ├── workflow-plan.md    # 승인된 실행 계획
│   ├── application-design.md  # 컴포넌트 설계 (조건부)
│   └── units.md            # 개발 단위 목록 (조건부)
├── construction/
│   ├── {unit}/
│   │   ├── functional-design.md  # 상세 기능 설계 (조건부, Comprehensive)
│   │   └── code-plan.md    # 코드 생성 계획 + 진행 체크박스
│   └── build-and-test/
│       ├── build-instructions.md  # 빌드 지침
│       └── test-instructions.md   # 테스트 지침
├── devflow-state.md        # 현재 단계 상태 (세션 재개용)
└── audit.md                # 전체 상호작용 로그 (append-only)
```

---

## 사전 요구사항

### 필수

| 항목 | 최소 버전 | 용도 |
|------|----------|------|
| **Git** | 2.20+ | 버전 관리, worktree 격리 개발 |
| **Claude Code** | 2.x | 플러그인 호스트 |

### 테스트 인프라 실행 시

테스트 인프라(`tests/run-all.sh`)를 실행하려면 추가로 필요합니다:

| 항목 | 최소 버전 | 용도 |
|------|----------|------|
| **Node.js** | 18+ | SKILL.md 메타 태그 파서 (`parse-skills.js`) |
| **Python** | 3.12+ | pytest 기반 L1/L2/L3 테스트 |
| **uv** | 0.4+ | Python 패키지 관리 + pytest 실행 |

### 선택 (특정 스킬 사용 시)

| 항목 | 용도 | 관련 스킬 |
|------|------|----------|
| **GitHub CLI (`gh`)** | PR 생성, 이슈 관리 | `finishing-a-development-branch`, `using-devflow` |

### 퀵 체크

```bash
# 필수 도구 확인
git --version && node --version && python3 --version && uv --version

# (선택) GitHub CLI 확인
gh --version

# 테스트 의존성 설치 + 실행
uv sync && bash tests/run-all.sh
```

---

## 설치

### 방법 1: 마켓플레이스 (권장)

[devflow-marketplace](https://github.com/bluejayA/devflow-marketplace)를 통해 설치합니다:

```bash
# 1. 마켓플레이스 설치
claude plugins install https://github.com/bluejayA/devflow-marketplace.git

# 2. aidlc 플러그인이 자동으로 포함됩니다
```

마켓플레이스에는 두 가지 구현체가 포함되어 있습니다:
- `aidlc` — 이 플러그인 (Orchestrator-Centric)
- `devflow` — 분산형 구현체 (Enhanced Skills)

### 방법 2: 단독 설치

이 플러그인만 직접 설치합니다:

```bash
claude plugins install https://github.com/bluejayA/aidlc-devflow.git
```

### 설치 확인

설치 후 새 세션을 시작하면 안내 메시지가 자동 표시됩니다:

```
🔧 AIDLC devflow 플러그인이 설치되어 있습니다.
시작하려면: "devflow 시작해줘"
```

---

## 차별적 특징

### 스킬 개발 풀사이클 도구 내장

aidlc-devflow는 스킬을 실행하는 플러그인일 뿐 아니라, **스킬을 만들고 검증하는 도구 체계**를 내장하고 있습니다.

| 단계 | 도구 | 설명 |
|------|------|------|
| **설계** | `skill-pattern-catalog` (행동 7종) + `skill-design-patterns` (구조 5종) | 결정 트리로 적합한 패턴을 자동 추천 |
| **작성** | `aidlc-writing-skills` + `skill-writing-guide` + `persuasion-principles` | TDD 방식 스킬 개발. CSO 원칙 + 점진적 공개 |
| **리뷰** | `skill-reviewer` 서브에이전트 | 메타데이터 정합성, 패턴 적합성, 게이트 선언 검증 |
| **테스트** | 3-Layer 정적 검증 (0토큰) | L1 그래프 검증 → L2 라우팅 시뮬레이터 → L3 스텝 순서 체커 |
| **운영** | 정합성 체크리스트 + 영향도 분석 규약 | 스킬 수정 시 참조·호출·연동 파급 확인 |

새 스킬을 추가하거나 기존 스킬을 수정할 때, 설계부터 검증까지 일관된 품질을 유지할 수 있습니다.

---

## AI-DLC 3대 패턴

### 1. 명시적 승인 게이팅

오케스트레이터가 모든 승인 게이트를 통합 관리합니다.

```
## aidlc-workspace-detection 완료

A) 변경 요청
B) 다음 단계 진행
```

### 2. 산출물 자동 문서화

각 stage의 실행 결과가 `devflow-docs/`에 자동 저장됩니다.

### 3. 적응형 깊이 + 해석 분기 확인

요청 복잡도에 따라 분석 깊이를 자동 조절하고, 동등하게 유효한 해석이 여러 개일 경우 먼저 확정합니다.

| 깊이 | 적용 조건 | 해석 분기 확인 |
|------|----------|--------------|
| **Minimal** | 단순/명확한 요청, 저위험 | 없음 |
| **Standard** | 일반적 복잡도 | 해석이 분기될 때만 |
| **Comprehensive** | 다중 컴포넌트, 고위험, 외부 연동 | 항상 |

---

## 참고 자료

- [AWS AI-DLC 방법론 블로그](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) — MIT-0 License, Copyright Amazon.com, Inc.
- [obra/superpowers](https://github.com/obra/superpowers) — MIT License, Copyright Jesse Vincent
- [Skill Guide 준수 리뷰](docs/analysis/2026-03-10-skill-guide-review.md)

서드파티 라이선스 상세: [THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES)

---

## 라이선스

[MIT License](LICENSE)
