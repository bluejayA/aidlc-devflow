# devflow 플러그인 설계 문서

- **작성일**: 2026-03-10
- **상태**: 승인됨

---

## 프로젝트 개요

**devflow**는 AI-DLC(AI-Driven Development Life Cycle) 방법론을 Superpowers 스타일의 Skills 아키텍처로 구현한 오픈소스 Claude Code 플러그인이다.

### 목표

- AI-DLC의 3대 패턴(명시적 승인 게이팅, 산출물 문서화, 적응형 깊이)을 Skills 기반으로 구현
- Superpowers의 일상 개발 도구(TDD, 디버깅, 코드리뷰 등)를 통합
- 최종적으로 하나의 완전한 개발 워크플로우 플러그인 완성

### 배포 형태

- **오픈소스**: GitHub 공개 레포지토리
- **설치**: Claude Code 플러그인 마켓플레이스 (`/plugin install devflow`)
- **언어**: 영어 (내용) + 한국어 (주석)

---

## 아키텍처: Enhanced Skills

### 설계 결정

세 가지 접근법 중 **Enhanced Skills (접근 C)** 채택:

| 접근 | 설명 | 결정 |
|------|------|------|
| A. Thin Wrapper | Superpowers 구조 유지, AI-DLC 개념만 추가 | ❌ AI-DLC 스테이지 세분화 희석 |
| B. 오케스트레이터 중심 | 중앙 skill이 전체 흐름 제어 | ❌ 복잡도 과다 |
| C. Enhanced Skills | 독립 skill + AI-DLC 패턴 내장 + 공통 유틸 | ✅ 채택 |

**핵심 원칙**: 각 skill은 독립적으로 실행 가능하면서, 공통 유틸(`devflow-state`, `devflow-audit`)을 통해 상태와 로그를 공유한다.

---

## 개발 전략: 2-Phase Worktree 병행 개발

```
~/projects/ai/aidlc-pilot/          ← main (뼈대, plugin.json, README)
~/projects/ai/aidlc-pilot-phase1/   ← phase1/aidlc-stages worktree
~/projects/ai/aidlc-pilot-phase2/   ← phase2/daily-tools worktree
```

- **Phase 1**: AI-DLC 핵심 스테이지 구현 (신규 skill 7개 + 유틸 2개 + 진입점)
- **Phase 2**: Superpowers 일상 개발 도구 재구성 (기존 skill 12개 강화)
- 각 Phase 완료 후 main에 머지 → 최종 통합 비교

---

## 최종 Skills 구조 (22개)

```
devflow/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   │
│   ├── using-devflow/                 # 진입점
│   │
│   ├── # ── Phase 1: AI-DLC 핵심 스테이지 ──
│   ├── workspace-detection/
│   ├── requirements-analysis/
│   ├── workflow-planning/
│   ├── application-design/
│   ├── units-generation/
│   ├── code-generation/
│   ├── build-and-test/
│   │
│   ├── # ── Phase 2: 일상 개발 도구 ──
│   ├── writing-plans/
│   ├── executing-plans/
│   ├── subagent-driven-development/
│   ├── dispatching-parallel-agents/
│   ├── test-driven-development/
│   ├── systematic-debugging/
│   ├── verification-before-completion/
│   ├── requesting-code-review/
│   ├── receiving-code-review/
│   ├── using-git-worktrees/
│   ├── finishing-a-development-branch/
│   ├── writing-skills/
│   │
│   └── _utils/
│       ├── devflow-state/
│       └── devflow-audit/
│
├── docs/
│   ├── research/
│   └── plans/
└── README.md
```

---

## Phase 1: AI-DLC 핵심 스테이지 (신규 구현)

### using-devflow
- 역할: 진입점. 세션 시작 시 `devflow-state.md` 확인
- AI-DLC 패턴: 상태 기반 세션 재개
- 동작:
  1. `devflow-docs/devflow-state.md` 존재 확인
  2. 진행 중인 작업 있으면 재개 안내
  3. 신규 작업이면 `workspace-detection` 실행 지시

### workspace-detection
- 역할: 그린필드/브라운필드 판단, 기존 코드베이스 분석
- AI-DLC 패턴: 승인 게이팅, audit 로깅
- 동작:
  1. 워크스페이스 스캔 (기존 코드, `devflow-state.md` 존재 여부)
  2. 그린필드 / 브라운필드 결정
  3. 결과를 `devflow-docs/inception/workspace.md`에 저장
  4. `devflow-audit`에 로깅
  5. 자동으로 `requirements-analysis`로 진행

### requirements-analysis
- 역할: 요구사항 분석 (적응형 깊이)
- AI-DLC 패턴: 적응형 깊이, 승인 게이팅, 산출물 저장
- 깊이 결정 기준:
  - **Minimal**: 단순/명확한 요청 → 의도 분석만
  - **Standard**: 일반적 복잡도 → 기능/비기능 요구사항
  - **Comprehensive**: 복잡/고위험/다중 컴포넌트 → 전체 요구사항 추적
- 산출물: `devflow-docs/inception/requirements.md`
- 완료 메시지:
  ```
  요구사항 분석 완료.
  A) 변경 요청
  B) 다음 단계(workflow-planning) 진행
  ```

### workflow-planning
- 역할: 어떤 단계를 실행할지 결정, 사용자 승인
- AI-DLC 패턴: 명시적 승인 게이팅, 적응형 실행 계획
- 동작:
  1. 앞 단계 산출물 로드
  2. 필요한 스테이지 목록 및 각 깊이 추천
  3. Mermaid 워크플로우 시각화 생성
  4. 사용자가 스테이지 포함/제외 조정 가능
- 산출물: `devflow-docs/inception/workflow-plan.md`
- **반드시 명시적 승인 후 진행**

### application-design _(조건부)_
- 실행 조건: 신규 컴포넌트/서비스 필요 시
- 스킵 조건: 기존 컴포넌트 범위 내 변경
- 산출물: `devflow-docs/inception/application-design.md`

### units-generation _(조건부)_
- 실행 조건: 복잡한 시스템 분해 필요 시
- 스킵 조건: 단일 단순 작업
- 산출물: `devflow-docs/inception/units.md`

### code-generation
- 역할: 코드 생성 (항상 실행)
- AI-DLC 패턴: 2단계 Plan → Approve → Generate
- 동작:
  1. **Part 1 — Planning**: 체크박스 포함 코드 생성 계획 작성
  2. 사용자 계획 승인 대기
  3. **Part 2 — Generation**: 승인된 계획대로 코드 생성
  4. 각 체크박스 완료 즉시 업데이트
- 산출물: `devflow-docs/construction/{unit-name}/code-plan.md`

### build-and-test
- 역할: 빌드/테스트 지침 생성 (항상 실행, 모든 unit 완료 후)
- 산출물:
  - `devflow-docs/construction/build-and-test/build-instructions.md`
  - `devflow-docs/construction/build-and-test/test-instructions.md`

---

## Phase 2: 일상 개발 도구 (Superpowers 재구성)

Superpowers 기존 skill을 기반으로 AI-DLC 패턴을 추가하여 강화.

| Skill | 강화 내용 |
|-------|----------|
| `writing-plans` | 명시적 승인 게이팅 강화, 계획을 `devflow-docs/`에 저장 |
| `executing-plans` | 각 태스크 완료 시 `devflow-audit` 로깅, 체크박스 즉시 업데이트 |
| `subagent-driven-development` | 서브에이전트 산출물을 `devflow-docs/construction/`에 저장 |
| `dispatching-parallel-agents` | 변경 없음 |
| `test-driven-development` | 변경 없음 |
| `systematic-debugging` | 디버깅 세션을 `devflow-audit`에 기록 |
| `verification-before-completion` | 명시적 승인 게이팅 강화 |
| `requesting-code-review` | 변경 없음 |
| `receiving-code-review` | 변경 없음 |
| `using-git-worktrees` | 변경 없음 |
| `finishing-a-development-branch` | 변경 없음 |
| `writing-skills` | devflow skill 작성 가이드 포함 |

---

## AI-DLC 3대 패턴 구현 상세

### 1. 명시적 승인 게이팅

모든 AI-DLC 스테이지 skill 끝에 표준 완료 메시지 강제:

```
[단계명] 완료.
A) 변경 요청
B) 다음 단계 진행
```

- 승인 기록은 `devflow-state.md`의 `## Completed Stages`에 저장
- 세션 재개 시 이전 승인 상태 복원 가능
- **NO EMERGENT BEHAVIOR**: 2-option 이외 메뉴 형태 사용 금지

### 2. 산출물 문서화

```
devflow-docs/
├── inception/
│   ├── workspace.md           # workspace-detection 산출물
│   ├── requirements.md        # requirements-analysis 산출물
│   ├── workflow-plan.md       # workflow-planning 산출물
│   ├── application-design.md  # application-design 산출물 (조건부)
│   └── units.md               # units-generation 산출물 (조건부)
├── construction/
│   └── {unit-name}/
│       └── code-plan.md       # code-generation 산출물
│   └── build-and-test/
│       ├── build-instructions.md
│       └── test-instructions.md
├── devflow-state.md            # 현재 단계, 완료/스킵 기록
└── audit.md                   # 모든 상호작용 로그 (append-only)
```

**규칙**:
- 앱 코드는 워크스페이스 루트에 저장 (`devflow-docs/` 바깥)
- `devflow-docs/`는 문서 전용

### 3. 적응형 깊이

`requirements-analysis`, `workflow-planning` 등에서 복잡도 평가 후 자동 결정:

| 깊이 | 조건 | 실행 내용 |
|------|------|----------|
| **Minimal** | 단순/명확한 요청 | 핵심만, 빠르게 |
| **Standard** | 일반적 복잡도 | 표준 프로세스 |
| **Comprehensive** | 복잡/고위험/다중 컴포넌트 | 전체 분석, 문서 풍부 |

---

## 공통 유틸 (_utils)

### devflow-state
- `devflow-docs/devflow-state.md` 읽기/쓰기 담당
- 구조:
  ```markdown
  ## Current Phase
  ## Completed Stages
  ## Skipped Stages
  ## Active Unit
  ## Extension Configuration
  ```

### devflow-audit
- `devflow-docs/audit.md` append-only 기록
- 규칙:
  - 항상 append 모드만 사용 (전체 덮어쓰기 금지)
  - 사용자 입력은 요약 없이 원문 그대로 기록
  - ISO 8601 타임스탬프 필수
- 포맷:
  ```markdown
  ## [스테이지명]
  **Timestamp**: 2026-03-10T12:00:00Z
  **User Input**: "[원문 그대로]"
  **AI Response**: "[응답 또는 수행한 액션]"
  **Context**: [단계, 결정 사항]
  ---
  ```

---

## plugin.json 구조

```json
{
  "name": "devflow",
  "version": "0.1.0",
  "description": "AI-DLC 방법론 기반 개발 워크플로우 플러그인",
  "skills": [
    "skills/using-devflow",
    "skills/workspace-detection",
    "skills/requirements-analysis",
    "skills/workflow-planning",
    "skills/application-design",
    "skills/units-generation",
    "skills/code-generation",
    "skills/build-and-test",
    "skills/writing-plans",
    "skills/executing-plans",
    "skills/subagent-driven-development",
    "skills/dispatching-parallel-agents",
    "skills/test-driven-development",
    "skills/systematic-debugging",
    "skills/verification-before-completion",
    "skills/requesting-code-review",
    "skills/receiving-code-review",
    "skills/using-git-worktrees",
    "skills/finishing-a-development-branch",
    "skills/writing-skills",
    "skills/_utils/devflow-state",
    "skills/_utils/devflow-audit"
  ]
}
```

---

## 미결 사항 (Phase 2 이후 검토)

- **reverse-engineering**: 브라운필드 코드베이스 분석 (현재 미포함)
- **nfr-requirements / nfr-design**: 비기능 요구사항 명시화 (현재 미포함)
- **Extensions 시스템**: 보안/컴플라이언스 확장 (현재 미포함)
- **Operations Phase**: 배포/모니터링 자동화 (AI-DLC도 placeholder 상태)
- **영어 공개**: 현재 한국어로 구현 후 추후 글로벌 공개 여부 결정
