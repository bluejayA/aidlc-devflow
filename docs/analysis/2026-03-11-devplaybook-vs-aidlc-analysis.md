# dev-playbook vs aidlc 상세 분석 보고서

**작성일**: 2026-03-11
**분석 범위**:
- dev-playbook: `/Users/jay.ahn/projects/ai/dev-playbook-ai-coding/.claude/rules/` (common, inception, construction, extensions, operations)
- aidlc: `/Users/jay.ahn/projects/ai/aidlc-devflow/skills/` (15개 스킬 + _shared + _utils)

---

## 1. 아키텍처 철학의 근본적 차이

### dev-playbook (A안): 계획-지향 (Plan-Driven)
- 모든 단계의 상세 템플릿, 검증 체크리스트, 질문 기반 가이드 제공
- "무엇을 먼저 물어볼 것인가"를 체계적으로 정의
- 각 단계 파일이 approval gate를 직접 포함

### aidlc (B안): 실행-지향 (Execution-Focused)
- 오케스트레이터 중심 아키텍처 — 각 스킬은 실행만 담당
- 게이팅과 상태 관리는 `aidlc-using-devflow` 오케스트레이터가 전담
- Stage Routing Table로 조건부 라우팅

---

## 2. 스테이지/스킬 1:1 매핑 테이블

| dev-playbook Rule | aidlc Skill | 일치도 | 비고 |
|---|---|---|---|
| inception/workspace-detection.md | aidlc-workspace-detection | 100% | 동일 |
| inception/requirements-analysis.md | aidlc-requirements-analysis | 85% | 질문 방식 상이 |
| inception/user-stories.md | **(없음)** | 0% | 누락 |
| inception/reverse-engineering.md | *(workspace-detection 일부)* | 20% | 심화 분석 없음 |
| construction/application-design.md | aidlc-application-design | 70% | 유사하나 NFR 통합 없음 |
| construction/units-generation.md | aidlc-units-generation | 90% | 거의 동일 |
| construction/functional-design.md | **(없음)** | 0% | 누락 |
| construction/nfr-requirements.md | **(없음)** | 0% | 누락 |
| construction/nfr-design.md | **(없음)** | 0% | 누락 |
| construction/infrastructure-design.md | **(없음)** | 0% | 누락 |
| construction/code-generation.md | aidlc-code-generation | 80% | GENERATE 신호 방식 상이 |
| construction/build-and-test.md | aidlc-build-and-test | 75% | 테스트 커버리지 상이 |
| common/depth-levels.md | *(workflow-planning 일부)* | 40% | _shared 파일 없음 |
| common/error-handling.md | **(없음)** | 0% | 누락 |
| common/workflow-changes.md | **(없음)** | 0% | 누락 |
| common/overconfidence-prevention.md | *(verification-before-completion 일부)* | 50% | 일부 중복 |
| extensions/security/baseline/ | **(없음)** | 0% | 선택적 확장 — aidlc에서도 opt-in 플러그인으로 구현 필요 |
| operations/ | *(placeholder)* | 10% | 양쪽 모두 미완 |
| *(없음)* | aidlc-using-devflow | — | aidlc 고유 |
| *(없음)* | aidlc-systematic-debugging | — | aidlc 고유 |
| *(없음)* | aidlc-receiving-code-review | — | aidlc 고유 |
| *(없음)* | aidlc-verification-before-completion | — | aidlc 고유 |
| *(없음)* | aidlc-finishing-a-development-branch | — | aidlc 고유 |
| *(없음)* | aidlc-using-git-worktrees | — | aidlc 고유 |
| *(없음)* | aidlc-dispatching-parallel-agents | — | aidlc 고유 |
| *(없음)* | devflow-state (util) | — | aidlc 고유 |
| *(없음)* | devflow-audit (util) | — | aidlc 고유 |

---

## 3. dev-playbook에는 있고 aidlc에 없는 것 (상세)

### 3.1 User Stories 단계 (`inception/user-stories.md`)

**파일 내용**:
- 사용자 페르소나 정의 프레임워크
- INVEST 기준(Independent, Negotiable, Valuable, Estimable, Small, Testable) 기반 스토리 검증
- 스토리 분해 방식: User Journey / Feature-based / Epic-based
- 수용 기준(Acceptance Criteria) 작성 가이드: Given-When-Then 형식
- 스토리별 우선순위 결정 기준 (MoSCoW)
- `user-stories.md` 아티팩트 생성 및 `aidlc-state.md` 업데이트

**aidlc에 없는 이유**: `aidlc-workflow-planning`에서 조건부 실행으로 언급하지만 스킬 파일 자체가 없음

**필요성**: Greenfield 프로젝트나 복잡한 도메인에서 요구사항을 구체적 구현 단위로 연결하는 핵심 단계

**권고**: `aidlc-user-stories/SKILL.md` 신규 작성 필요

---

### 3.2 Reverse Engineering 심화 (`inception/reverse-engineering.md`)

**파일 내용 — 생성 아티팩트 8개**:
1. `business-overview.md` — 비즈니스 목적, 주요 사용자, 가치 제안
2. `architecture.md` — 시스템 아키텍처 다이어그램 (ASCII/Mermaid)
3. `code-structure.md` — 디렉토리 구조, 모듈 의존성
4. `api-documentation.md` — 엔드포인트, 파라미터, 응답 형식
5. `component-inventory.md` — 핵심 컴포넌트 목록 및 역할
6. `technology-stack.md` — 사용 기술 스택 및 버전
7. `dependencies.md` — 외부 의존성 및 라이선스
8. `code-quality-assessment.md` — 코드 품질, 테스트 커버리지, 기술 부채

**aidlc 현황**: `aidlc-workspace-detection`은 프로젝트 타입(Greenfield/Brownfield)과 기본 메타데이터만 탐지. 위 8개 아티팩트 없음.

**권고**: `aidlc-reverse-engineering/SKILL.md` 신규 작성 또는 `aidlc-workspace-detection`을 Brownfield 경로에서 심화 분석으로 확장

---

### 3.3 Functional Design (`construction/functional-design.md`)

**파일 내용 — 유닛별 설계 포함 항목**:
- 데이터 모델 및 도메인 객체 정의 (field types, constraints, relationships)
- API 계약 및 메서드 시그니처 (inputs, outputs, error cases)
- 비즈니스 로직 분해 (sub-functions, decision points)
- 엣지 케이스 및 오류 흐름 (예외 처리 방침)
- 컴포넌트 간 상호작용 시퀀스 (sequence diagram)
- `functional-design.md` 아티팩트 생성 (유닛별)

**aidlc 현황**: `aidlc-code-generation` 전에 이런 상세 설계 단계가 없음. 코드 생성 플랜 단계(PART 1)가 이를 일부 대체하지만 데이터 모델/시그니처 수준의 상세도는 없음.

**권고**: `aidlc-functional-design/SKILL.md` 신규 작성. `aidlc-code-generation` 전에 선택적 실행.

---

### 3.4 NFR Requirements & NFR Design

**`construction/nfr-requirements.md` 내용**:
- 질문 카테고리 8개:
  1. Scalability (동시 사용자 수, 데이터 볼륨, 성장 예측)
  2. Performance (응답 시간 SLA, 처리량 요구사항)
  3. Availability (업타임 요구사항, RTO/RPO)
  4. Security (인증 방식, 데이터 암호화, 컴플라이언스)
  5. Reliability (오류 처리, 재시도 정책, 내결함성)
  6. Maintainability (모니터링, 로깅, 알림)
  7. Usability (접근성 요구사항, 국제화)
  8. Cost (예산 제약, 클라우드 비용 최적화)
- 모호한 답변 시 follow-up 질문 강제
- `nfr-requirements.md` 아티팩트 생성

**`construction/nfr-design.md` 내용**:
- NFR → 아키텍처 패턴 변환 결정 가이드
- Tech stack 선택 (언어, 프레임워크, 데이터베이스)을 NFR 기반으로 결정
- `tech-stack-defaults.md` 참조 강제
- `nfr-design.md` 아티팩트 생성

**`construction/infrastructure-design.md` 내용**:
- 논리 컴포넌트 → 실제 인프라 서비스 매핑
- 카테고리: compute, storage, messaging, networking, monitoring
- 클라우드 제공자 결정 프레임워크 (AWS/GCP/Azure/self-hosted)
- 공유 인프라 전략 (여러 유닛이 공유하는 리소스)
- `infrastructure-design.md` 아티팩트 생성

**aidlc 현황**: `aidlc-workflow-planning`의 Stage Routing Table에 NFR과 Infrastructure Design이 조건부로 참조되지만 실제 스킬 파일 없음.

**권고**: 3개 스킬 신규 작성 — `aidlc-nfr-requirements`, `aidlc-nfr-design`, `aidlc-infrastructure-design`

---

### 3.5 보안 확장 프레임워크 (`extensions/security/baseline/`)

> **⚠️ 선택적 확장(Extension) 성격 주의**
>
> dev-playbook에서 이 내용은 `rules/extensions/` 하위에 위치한다. `extensions/`는 모든 프로젝트에 강제 적용되는 core 규칙이 아니라 **선택적으로 활성화하는 확장**임을 의미한다. aidlc에 반영할 때도 동일하게 **opt-in 플러그인** 형태로 구현해야 하며, core 워크플로우에 내장하거나 자동 실행하는 방식은 적합하지 않다.

**파일 내용 — SECURITY-01 ~ SECURITY-15 규칙**:

| 규칙 ID | 내용 | OWASP 매핑 |
|---|---|---|
| SECURITY-01 | 인증 및 세션 관리 | A07:2021 |
| SECURITY-02 | 입력 검증 및 인코딩 | A03:2021 |
| SECURITY-03 | SQL Injection 방지 | A03:2021 |
| SECURITY-04 | XSS 방지 | A03:2021 |
| SECURITY-05 | CSRF 방지 | A01:2021 |
| SECURITY-06 | 시크릿 관리 | A02:2021 |
| SECURITY-07 | 의존성 취약점 스캔 | A06:2021 |
| SECURITY-08 | 로깅 및 모니터링 | A09:2021 |
| SECURITY-09 | API 보안 (인증, rate limiting) | A01:2021 |
| SECURITY-10 | 데이터 암호화 (전송/저장) | A02:2021 |
| SECURITY-11 | 접근 제어 (RBAC/ABAC) | A01:2021 |
| SECURITY-12 | 오류 처리 (정보 노출 방지) | A05:2021 |
| SECURITY-13 | 파일 업로드 보안 | A04:2021 |
| SECURITY-14 | 서드파티 통합 보안 | A08:2021 |
| SECURITY-15 | Infrastructure as Code 보안 | A05:2021 |

각 규칙마다:
- **Verification criteria**: 코드 생성 후 확인 항목
- **Blocking finding 처리**: Critical 발견 시 진행 중단 절차
- **적용 단계**: 어떤 construction 단계에서 검증하는지 명시

**aidlc 현황**: 보안 프레임워크 전무. `aidlc-code-generation`의 "Automation Friendly Code Rules" (data-testid 속성)만 언급.

**권고**: 별도 aidlc 플러그인(`aidlc-security-extension`)으로 구현. 설치한 경우에만 워크플로우에 보안 검증 게이트가 추가되는 **opt-in 구조**로 설계할 것. core 스킬(`aidlc-code-generation`, `aidlc-build-and-test`)에 보안 로직을 직접 내장하는 방식은 지양.

**aidlc 플러그인 구현 방향**:
- 플러그인 설치 시: `aidlc-using-devflow` 오케스트레이터가 security gate 단계를 자동으로 workflow에 삽입
- 미설치 시: core 워크플로우에 영향 없음
- 활성화 범위 선택 가능: 전체 SECURITY-01~15 또는 카테고리별(예: "API 보안만", "의존성 스캔만") 선택 설치 지원 고려

---

### 3.6 에러 핸들링 & 복구 (`common/error-handling.md`)

**파일 내용 — Phase별 오류 시나리오**:

**Inception 단계 오류**:
- 사용자가 불충분한 정보 제공 → 최소 viable 세트로 진행 후 표시
- 요구사항 충돌 → 충돌 목록 표시 후 사용자 결정 요청
- User stories 범위 초과 → 자동 범위 축소 + 사용자 확인

**Construction 단계 오류**:
- Code generation 중 문법 오류 → 즉시 수정 후 재시도 1회
- 의존성 충돌 → 대안 제시 후 사용자 선택
- Test 실패 → 실패 원인 분석 후 코드 수정 (최대 3회 재시도)
- State file 손상 → 마지막 유효한 checkpoint로 복구 절차

**Session Resumption 오류**:
- devflow-state.md 없음 → workspace-detection 재실행
- Phase 불일치 → 현재 아티팩트 스캔 후 state 재구성
- Partial completion → 미완성 단계부터 재개

**aidlc 현황**: 개별 스킬에서 "Common Issues" 정도만 언급. 체계적인 오류 처리 프레임워크 없음.

**권고**: `skills/_shared/error-handling.md` 신규 작성

---

### 3.7 Workflow 중간 변경 관리 (`common/workflow-changes.md`)

**파일 내용 — 변경 유형별 처리**:

| 변경 유형 | 탐지 방법 | 처리 절차 |
|---|---|---|
| 단계 추가 | "~도 필요해" 키워드 | 영향 분석 → 사용자 확인 → workflow-plan.md 업데이트 |
| 단계 삭제 | "~는 필요 없어" 키워드 | 의존성 확인 → 삭제 가능 여부 판단 → 사용자 확인 |
| 깊이 변경 | "더 자세히/간략하게" 키워드 | 현재 아티팩트 재생성 여부 결정 |
| 아키텍처 결정 변경 | 이전 결정과 충돌 | 영향받는 아티팩트 목록 제시 → 재생성 여부 결정 |
| 범위 확장 | 새 기능 추가 요청 | units-generation 재실행 여부 판단 |

**aidlc 현황**: 오케스트레이터에서 명시적으로 다루지 않음. 사용자가 중간에 변경 요청 시 어떻게 처리하는지 정의 없음.

**권고**: `aidlc-using-devflow`의 오케스트레이터 로직에 변경 요청 처리 섹션 추가

---

### 3.8 Overconfidence Prevention (`common/overconfidence-prevention.md`)

**파일 내용**:

"Default to Asking" 철학:
> "When in doubt about a decision, always ask the user. The cost of one extra question is always lower than the cost of a wrong assumption."

답변 모호성 탐지 규칙:
- **Vague responses**: "좋아 보여요", "괜찮아요" → follow-up 필수
- **Undefined terms**: "보통 수준", "적당히" → 정량화 요청
- **Contradictions**: 앞뒤 요구사항 충돌 → 명시적 해소 요청
- **Incomplete answers**: 일부 질문만 답변 → 미답 질문 재제시

Follow-up 강제 규칙:
- 답변에 조건부 표현("~할 수도", "상황에 따라") 포함 시 → 조건 명시 요청
- 수치 없이 "많이", "빠르게" 사용 시 → 구체적 수치 요청

**aidlc 현황**: `aidlc-verification-before-completion`이 완료 주장 전 검증을 강제하지만, 사용자 답변의 모호성 탐지는 없음. Minimal depth에서는 질문 자체를 생략하는 경향.

**권고**: `aidlc-requirements-analysis`의 Step 4 (깊이별 질문)에 모호성 탐지 규칙 추가

---

### 3.9 Adaptive Depth 명시 (`common/depth-levels.md`)

**파일 내용**:

```
Minimal:
- 핵심 내용만 (1-2 paragraphs per section)
- 다이어그램 없음
- 상세 구현 노트 없음

Standard:
- 충분한 상세도 (3-5 paragraphs per section)
- 핵심 다이어그램 1-2개
- 주요 구현 결정 명시

Comprehensive:
- 완전한 상세도 (전체 섹션 커버)
- 여러 다이어그램 (architecture, sequence, data model)
- 모든 엣지 케이스, 오류 흐름, 대안 포함
```

원칙: "Create exactly the detail needed — no more, no less"

각 단계에서 depth별로 생성되는 아티팩트 목록 명시:
- Minimal에서도 아티팩트 파일은 생성, 단 내용이 간략
- "아티팩트 없음"은 허용되지 않음 (depth와 무관)

**aidlc 현황**: `aidlc-workflow-planning`에서 `minimal | standard | comprehensive` 결정하지만, 각 depth에서 실제로 무엇이 달라지는지 정의하는 shared 문서 없음.

**권고**: `skills/_shared/depth-levels.md` 신규 작성

---

### 3.10 Diagram 검증 규칙 (`common/content-validation.md`)

**파일 내용**:

ASCII 다이어그램 규칙:
- 최대 너비 80자 제한
- 박스 문자 표준: `┌─┐`, `│`, `└─┘`
- 화살표 표준: `→`, `←`, `↑`, `↓`, `↔`

Mermaid 검증:
- 파일 생성 전 syntax 검증 필수
- `graph TD`/`graph LR` 방향 일관성
- 노드명에 특수문자 금지 (따옴표 처리)
- 서브그래프 중첩 최대 2단계

Pre-creation validation checklist:
- [ ] 파일명이 kebab-case인지 확인
- [ ] 아티팩트 경로가 devflow-docs/ 하위인지 확인
- [ ] 이전 아티팩트와 내용 충돌 없는지 확인
- [ ] 사용자 승인 후 생성하는지 확인

**aidlc 현황**: 다이어그램 품질 및 파일 생성 전 검증 가이드 없음.

**권고**: `skills/_shared/content-validation.md` 신규 작성

---

## 4. aidlc에는 있고 dev-playbook에는 없는 것 (상세)

### 4.1 오케스트레이터 중심 아키텍처 (`aidlc-using-devflow`)

**내용**:
- **역할 분리 원칙**: Orchestrator(게이팅, 상태, 감사) vs Stage Skills(실행만)
- **Stage Routing Table**: 조건에 따른 명시적 다음 단계 결정
  ```
  workspace-detection → (Brownfield) → reverse-engineering
                      → (Greenfield) → requirements-analysis
  requirements-analysis → (복잡도 높음) → user-stories
                        → (단순) → application-design
  ```
- **Multi-unit handling**: 여러 유닛을 순차 처리하며 각각 추적
- **devflow-state**: 현재 단계, 완료된 단계, 진행 중인 유닛 구조화 추적

**dev-playbook 현황**: 각 phase 파일이 approval gate를 직접 포함. 일관된 오케스트레이터 없음.

---

### 4.2 Git Worktree 통합 (`aidlc-using-git-worktrees`)

**내용**:
- 자동 브랜치명 도출: requirements.md에서 주제 추출 → kebab-case 변환
- 프로젝트별 의존성 자동 설치:
  - Node.js: `package.json` 감지 → `npm install`
  - Python: `pyproject.toml` → `uv sync` / `requirements.txt` → `pip install`
  - Go: `go.mod` → `go mod download`
  - Rust: `Cargo.toml` → `cargo build`
- 베이스라인 테스트 자동 실행 후 실패 목록 기록
- Greenfield/Brownfield 모두 지원
- 워크트리 경로: `../[project-name]-[branch-name]/`

**dev-playbook 현황**: git worktree 언급 없음.

---

### 4.3 Systematic Debugging (`aidlc-systematic-debugging`)

**내용**:
- **Iron Law**: "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
- 4단계 프로세스:
  1. Root Cause Analysis (증상 vs 원인 구분)
  2. Pattern Analysis (버그 패턴 분류: logic/data/integration/performance)
  3. Hypothesis Formation (가설 → 검증 방법)
  4. Targeted Fix (최소 변경으로 수정)
- Rationalization 방지 테이블:
  | 금지 사고 패턴 | 올바른 접근 |
  |---|---|
  | "아마 ~때문일 거야" | 실제 재현 후 확인 |
  | "고쳐보고 틀리면 다시" | 원인 확정 후 수정 |
  | "관련 없어 보이는데 건드려보자" | 영향 범위 분석 먼저 |

**dev-playbook 현황**: 디버깅을 별도 단계로 다루지 않음.

---

### 4.4 Code Review Reception (`aidlc-receiving-code-review`)

**내용**:
- **6단계 프로세스**: READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT
- VERIFY 단계: 리뷰어의 기술적 주장이 실제로 맞는지 검증 (맹목적 동의 금지)
- EVALUATE 단계: YAGNI 원칙 적용 — 리뷰 반영이 현재 필요한지 판단
- 이슈 분류: Critical (블로킹) / Important (권장) / Minor (선택)
- 아첨성 응답 금지 패턴 명시: "좋은 지적이에요!", "맞습니다!" 무조건 금지

**dev-playbook 현황**: 코드 리뷰를 별도 단계로 다루지 않음.

---

### 4.5 Verification Before Completion (`aidlc-verification-before-completion`)

**내용**:
- **Iron Law**: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
- Red Flag 표현 목록 (사용 금지):
  - "완료했습니다" (검증 전)
  - "테스트 통과했을 것입니다"
  - "아마 작동할 것입니다"
  - "이전에 확인했습니다"
- 5단계 Gate 프로세스:
  1. Identify: 무엇을 검증해야 하는지 목록 작성
  2. Execute: 실제 명령어 실행
  3. Read: 출력 전체 읽기
  4. Validate: 기대값과 실제값 비교
  5. Declare: 증거 포함하여 완료 선언

**dev-playbook 현황**: 각 단계에서 결과 확인을 요구하지만 별도 verification gate skill 없음.

---

### 4.6 Branch Lifecycle Management (`aidlc-finishing-a-development-branch`)

**내용**:
- 4가지 선택지:
  - **A) 로컬 병합**: `git merge --no-ff` + worktree 정리
  - **B) PR 생성**: GitHub PR 생성 + 브랜치 유지
  - **C) 브랜치 유지**: worktree 정리 + 브랜치는 남김
  - **D) 폐기**: worktree 삭제 + 브랜치 삭제
- Worktree 정리 규칙: 각 선택지마다 명확한 git 명령어 제시
- PR 생성 시 자동 포함 내용: 변경 요약, 관련 requirements, 테스트 결과

**dev-playbook 현황**: 개발 완료 후 브랜치 처리를 별도 단계로 다루지 않음.

---

### 4.7 devflow-state & devflow-audit 유틸 분리

**devflow-state** (`_utils/devflow-state/SKILL.md`):
```yaml
current_phase: inception | construction | operations
current_stage: [stage name]
completed_stages: [list]
current_unit: [unit name] (construction만)
completed_units: [list]
workflow_plan_path: devflow-docs/workflow-plan.md
```
- invoke_mode: `orchestrator-only` (스킬에서 직접 호출 금지)

**devflow-audit** (`_utils/devflow-audit/SKILL.md`):
```yaml
timestamp: ISO 8601
user_request: [raw user message]
state_change: from → to
decision: [결정 내용]
artifacts_created: [목록]
```
- 모든 phase transition, 사용자 승인, 아티팩트 생성 기록

**dev-playbook 현황**: `aidlc-state.md` 단일 파일로 통합. 감사 로그 별도 없음.

---

### 4.8 Minimal Depth 지원

**aidlc `aidlc-requirements-analysis` Minimal 출력**:
```markdown
## Requirements (Minimal)

**Intent**: [1 paragraph]

**Acceptance Criteria**:
- [ ] [criterion 1]
- [ ] [criterion 2]
- [ ] [criterion 3]

**Assumptions**:
- [assumption 1]
- [assumption 2]
```

**dev-playbook 현황**: 모든 깊이에서 전체 requirements 아티팩트 생성. Minimal 전용 간략 형식 없음.

---

## 5. 내용은 같지만 구현 방식이 다른 것 (상세)

### 5.1 질문 생성 방식

**dev-playbook (inception/requirements-analysis.md)**:
- Step 6: "ALWAYS create questions unless exceptionally clear"
- `question-verification-questions.md` 파일에 전체 질문 목록 수집
- [Answer]: 태그 방식으로 사용자 응답 유도
- 답변 수집 후 follow-up 질문 자동 생성
- **모든 깊이에서 질문 의무**

**aidlc (aidlc-requirements-analysis)**:
- Step 2: 해석이 2가지 이상 분기될 때만 선택지 제시
- Step 4: Comprehensive depth에서만 열린 질문 (ONE at a time)
- Minimal depth: 질문 없이 가정 기반으로 진행
- **해석 분기 또는 깊이 조건에서만 선택적 질문**

**차이 분석**: dev-playbook은 철저한 요구사항 수집 지향, aidlc는 효율적 흐름 지향. dev-playbook 방식은 완성도 높지만 간단한 작업에서 불필요한 질문 과다. aidlc 방식은 빠르지만 중요한 모호성을 놓칠 수 있음.

**권고**: aidlc의 Step 2에 dev-playbook의 모호성 탐지 규칙 일부 적용 (특히 Standard/Comprehensive depth에서)

---

### 5.2 코드 생성 2단계 프로세스

**dev-playbook (construction/code-generation.md)**:
- Part 1: Detailed plan (파일별 변경 사항, 번호 매긴 단계)
- Approval 후 Part 2 시작 — 동일 파일 내 연속 진행
- 체크박스 업데이트: `- [ ]` → `- [x]` 실시간 업데이트

**aidlc (aidlc-code-generation)**:
- PART 1: `code-generation-plan.md` 아티팩트 생성
  - 생성/수정 파일 목록
  - 단계별 실행 계획
  - 테스트 전략
- PART 2: 오케스트레이터가 "GENERATE" 신호 발신 후 실행
- 각 단계 완료 후 오케스트레이터에 제어 반환

**차이 분석**: aidlc가 오케스트레이터-스킬 경계를 명확히 유지. dev-playbook은 단계 내 self-contained. aidlc 방식이 구조적으로 더 깔끔.

---

### 5.3 Build & Test 커버리지

**dev-playbook (construction/build-and-test.md) — 5개 아티팩트**:
1. `build-instructions.md` — 빌드 명령어, 환경 설정
2. `unit-test-instructions.md` — 유닛 테스트 명령어, 커버리지 목표
3. `integration-test-instructions.md` — 통합 테스트 시나리오
4. `performance-test-instructions.md` — 성능 테스트 기준 (응답 시간, 처리량)
5. `build-and-test-summary.md` — 전체 요약 및 CI/CD 파이프라인 설정

추가 테스트 유형: contract tests, security tests, E2E tests

**aidlc (aidlc-build-and-test) — 2개 아티팩트**:
1. `build-instructions.md` — 빌드 도구 자동 감지 후 명령어
2. `test-instructions.md` — 단위/통합 테스트 명령어

소스 파일 스캔으로 빌드 도구 자동 감지 (package.json, pyproject.toml 등)

**차이 분석**: dev-playbook은 테스트 유형별 세분화, aidlc는 실용적 자동화. performance/contract/security/E2E 테스트가 aidlc에서 누락.

**권고**: aidlc의 `aidlc-build-and-test`에 performance/contract/security 테스트 지침 추가 (별도 파일 또는 통합)

---

### 5.4 Workflow Planning 출력

**dev-playbook (inception/execution-plan.md 형식)**:
```markdown
## Phase Determination
**Project Type**: Brownfield
**Rationale**: Existing codebase detected, reverse engineering required

## Stage Plan
| Stage | Execute? | Reason |
|---|---|---|
| Workspace Detection | EXECUTE | Always required |
| Reverse Engineering | EXECUTE | Brownfield project |
| Requirements Analysis | EXECUTE | New feature addition |
| User Stories | SKIP | Simple CRUD, no need |
| NFR Requirements | EXECUTE | Performance requirements mentioned |
...

## Risk Assessment
- Technical debt in authentication module may affect timeline
- Third-party API dependency needs contract validation

## Component Relationships
- auth-service → user-service (dependency)
- notification-service ← order-service (event-driven)
```

**aidlc (aidlc-workflow-planning, workflow-plan.md 형식)**:
```markdown
## Workflow Plan

**Depth**: standard
**Project Type**: brownfield

### Stages
| Stage | Status | Depth | Reason |
|---|---|---|---|
| workspace-detection | included | — | 항상 실행 |
| requirements-analysis | included | standard | 신규 기능 |
| user-stories | skipped | — | 단순 CRUD |
...
```

**차이 분석**: dev-playbook이 rationale/risk/relationships를 포함한 더 풍부한 계획 문서 생성. aidlc는 실행 결정에 집중. dev-playbook의 Risk Assessment와 Component Relationships는 aidlc에 없음.

---

### 5.5 Application Design 구조

**dev-playbook (construction/application-design.md)**:
- System Context Diagram (외부 액터와의 관계)
- Container Diagram (주요 컨테이너/서비스)
- Component Diagram (내부 컴포넌트)
- Deployment Diagram (인프라 배치)
- **C4 Model** 기반 4단계 다이어그램
- cross-cutting concerns (보안, 로깅, 에러 핸들링) 명시

**aidlc (aidlc-application-design)**:
- Architecture Overview (Mermaid 다이어그램 1개)
- Component List with responsibilities
- Tech Stack (언어, 프레임워크, DB, 인프라)
- Integration Points
- cross-cutting concerns 언급

**차이 분석**: dev-playbook은 C4 Model의 4계층 다이어그램, aidlc는 단일 architecture overview. aidlc가 간결하지만 복잡한 시스템에서는 C4 접근이 더 명확.

**권고**: aidlc의 Standard/Comprehensive depth에서 C4 Model 다이어그램 선택적 생성 추가

---

## 6. 보안 정책 격차 상세

> **⚠️ Extension 성격 재확인**: dev-playbook의 보안 프레임워크는 `rules/extensions/` 하위에 위치하여 선택적 적용이 전제된 내용이다. 아래 격차 분석은 "보안 확장을 활성화했을 때"를 기준으로 한다.

**dev-playbook** 각 construction 단계에 보안 체크포인트 내장 (확장 활성화 시):
- Code Generation 후: SECURITY-02(입력검증), SECURITY-03(SQL Injection), SECURITY-04(XSS) 검증
- Build & Test 후: SECURITY-07(의존성 취약점 스캔) 실행
- Application Design 후: SECURITY-11(접근 제어), SECURITY-09(API 보안) 검토

**aidlc** 보안 관련 언급:
- `aidlc-code-generation`: "data-testid 속성을 UI 요소에 추가" (테스트 자동화용)
- `skills/_shared/devflow-conventions.md`: tech-stack-defaults.md 참조 (보안 스택 선택 일부)

**격차**: aidlc에 보안 확장을 선택적으로 활성화할 수 있는 플러그인 메커니즘 자체가 없음. 보안이 필요한 프로젝트에서 해당 확장을 opt-in으로 설치·활성화할 수 있는 구조가 없는 것이 핵심 문제.

**방향**: aidlc 플러그인 시스템에서 extension을 지원하는 구조(설치 → 워크플로우 자동 확장)를 먼저 정의한 뒤, 보안 확장을 그 첫 번째 사례로 구현하는 것이 적합.

---

## 7. aidlc 개선 권고사항 (우선순위별)

### Priority 1 — 즉시 (핵심 기능 완성)

#### P1-1. `aidlc-user-stories/SKILL.md` 신규 작성
**기반 파일**: `dev-playbook/rules/inception/user-stories.md`

포함할 내용:
- 페르소나 정의 템플릿
- INVEST 기준 체크리스트
- 스토리 분해 방식 (User Journey / Feature-based / Epic-based)
- Given-When-Then 수용 기준 형식
- MoSCoW 우선순위 결정
- 출력: `devflow-docs/inception/user-stories.md`

라우팅 조건: `aidlc-workflow-planning`에서 복잡한 도메인 또는 여러 페르소나가 있을 때 포함

---

#### P1-2. 보안 확장 플러그인 구현 *(opt-in — core 워크플로우 분리 필수)*
**기반 파일**: `dev-playbook/rules/extensions/security/baseline/security-baseline.md`

> dev-playbook에서 `extensions/`는 선택적 확장을 의미한다. aidlc에서도 동일하게 **별도 플러그인으로 분리**하여 설치한 경우에만 워크플로우에 영향을 주도록 설계해야 한다. core 스킬에 보안 로직을 직접 내장하는 방식은 지양.

**구현 방향**:

**Step 1 — aidlc Extension 메커니즘 정의 (선행 작업)**
- aidlc 플러그인이 core 워크플로우를 확장하는 방식 정의
  - 예: `plugin.json`의 `extensions` 필드로 활성화
  - 예: `aidlc-using-devflow` 오케스트레이터가 설치된 extension 스킬 목록을 읽어 stage routing table에 동적 삽입
- Extension 스킬의 invoke 조건과 gate 위치 정의 (어느 core 단계 전/후에 삽입되는지)

**Step 2 — `aidlc-security-extension/SKILL.md` 신규 작성**
- SECURITY-01~15 규칙 포함
- 각 규칙이 어느 core 단계 다음에 실행되는지 명시
  - `aidlc-application-design` 완료 후 → SECURITY-09, SECURITY-11 검토
  - `aidlc-code-generation` PART 2 완료 후 → SECURITY-02, SECURITY-03, SECURITY-04 검증
  - `aidlc-build-and-test` 완료 후 → SECURITY-07 의존성 취약점 스캔
- Blocking finding 발생 시 오케스트레이터에 중단 신호 반환

**Step 3 — 선택적 활성화 범위 지원 (선택)**
- 전체 SECURITY-01~15 일괄 활성화
- 카테고리별 선택 활성화 (예: "API 보안", "의존성 스캔" 등)

**미설치 시**: core 워크플로우에 전혀 영향 없음

---

#### P1-3. `aidlc-nfr-requirements/SKILL.md` 신규 작성
**기반 파일**: `dev-playbook/rules/construction/nfr-requirements.md`

포함할 내용:
- 8개 NFR 카테고리별 질문 세트
- 모호한 답변 시 follow-up 강제 규칙
- 기술 스택 선택과 NFR 연결 로직
- 출력: `devflow-docs/construction/nfr-requirements.md`

---

#### P1-4. `aidlc-nfr-design/SKILL.md` 신규 작성
**기반 파일**: `dev-playbook/rules/construction/nfr-design.md`

포함할 내용:
- NFR → 아키텍처 패턴 변환 결정 가이드
- 언어/프레임워크/DB 선택 (tech-stack-defaults.md 참조)
- 출력: `devflow-docs/construction/nfr-design.md`

---

#### P1-5. `aidlc-infrastructure-design/SKILL.md` 신규 작성
**기반 파일**: `dev-playbook/rules/construction/infrastructure-design.md`

포함할 내용:
- 논리 컴포넌트 → 인프라 서비스 매핑
- 클라우드 제공자 결정 프레임워크
- 공유 인프라 전략
- 출력: `devflow-docs/construction/infrastructure-design.md`

---

### Priority 2 — 단기 (워크플로우 견고성)

#### P2-1. `skills/_shared/depth-levels.md` 신규 작성
**기반 파일**: `dev-playbook/rules/common/depth-levels.md`

각 depth별 출력 형식 명시:
- Minimal: 최소 아티팩트 형식
- Standard: 표준 아티팩트 형식
- Comprehensive: 전체 아티팩트 형식

---

#### P2-2. `skills/_shared/error-handling.md` 신규 작성
**기반 파일**: `dev-playbook/rules/common/error-handling.md`

포함할 내용:
- Phase별 오류 시나리오 및 복구 절차
- State file 손상 복구
- Session resumption 오류 처리

---

#### P2-3. `aidlc-using-devflow` — 변경 요청 처리 섹션 추가
**기반 파일**: `dev-playbook/rules/common/workflow-changes.md`

포함할 내용:
- 변경 유형 탐지 키워드
- 변경 유형별 처리 절차
- workflow-plan.md 업데이트 규칙

---

#### P2-4. `aidlc-requirements-analysis` — 모호성 탐지 규칙 강화
**기반 파일**: `dev-playbook/rules/common/overconfidence-prevention.md`

Standard/Comprehensive depth에서:
- 조건부 표현 탐지 → 구체화 요청
- 수치 없는 표현 탐지 → 정량화 요청
- 답변 불완전성 탐지 → 재제시

---

#### P2-5. `aidlc-build-and-test` — 테스트 커버리지 확장
**기반 파일**: `dev-playbook/rules/construction/build-and-test.md`

추가할 테스트 유형:
- performance-test-instructions.md
- contract-test-instructions.md (API 계약 테스트)
- security-test-instructions.md (의존성 취약점 스캔)

---

#### P2-6. `aidlc-reverse-engineering/SKILL.md` 신규 작성
**기반 파일**: `dev-playbook/rules/inception/reverse-engineering.md`

8개 아티팩트 생성 또는 `aidlc-workspace-detection`의 Brownfield 경로에서 심화 분석으로 확장

---

### Priority 3 — 중장기 (기능 확장)

#### P3-1. `aidlc-functional-design/SKILL.md` 신규 작성
- 유닛별 데이터 모델, API 계약, 비즈니스 로직 상세 설계
- `aidlc-code-generation` 전에 선택적 실행

#### P3-2. `aidlc-workflow-planning` — Risk Assessment & Component Relationships 추가
- 기술 부채 리스크 평가
- 컴포넌트 간 의존성 분석

#### P3-3. C4 Model 다이어그램 지원
- `aidlc-application-design`의 Standard/Comprehensive에서 C4 4계층 다이어그램 선택적 생성

#### P3-4. Operations Phase 구체화
- 현재 placeholder → Deployment, Monitoring, Incident Response 워크플로우 정의
- CD/CI 파이프라인 생성 스킬

#### P3-5. `skills/_shared/content-validation.md` 신규 작성
- ASCII 다이어그램 표준
- Mermaid syntax 검증
- Pre-creation validation checklist

---

## 8. 현황 요약

| 구분 | dev-playbook | aidlc |
|---|---|---|
| 아키텍처 | 계획-지향, 단계별 독립 | 오케스트레이터 중심, 역할 분리 |
| 요구사항 수집 | 철저한 질문 강제 | 선택적, 깊이 기반 |
| NFR/인프라 설계 | 3개 전용 단계 | 없음 (누락) |
| 보안 프레임워크 | SECURITY-01~15 (선택적 extension) | 없음 — opt-in 플러그인으로 구현 필요 |
| 디버깅 | 없음 | 체계적 디버깅 스킬 있음 |
| 코드 리뷰 | 없음 | reception 스킬 있음 |
| 완료 검증 | 각 단계 분산 | 전용 verification gate |
| Git 워크플로우 | 없음 | 워크트리 통합 |
| 에러 복구 | 상세 절차 있음 | 미흡 |
| 변경 관리 | 상세 절차 있음 | 없음 |
| 상태 추적 | 단일 state 파일 | state + audit 분리 |
| Depth 지원 | 명시적 정의 | 정의 문서 없음 |

---

## 9. 결론

**aidlc의 강점**: 오케스트레이터 아키텍처, 워크트리 통합, 디버깅/리뷰/검증 스킬
**aidlc의 약점**: NFR 3단계 누락, 보안 프레임워크 전무, User Stories 없음, 에러 복구/변경 관리 미흡

**통합 전략**: aidlc의 오케스트레이터 아키텍처를 유지하면서 dev-playbook의 콘텐츠(NFR, User Stories, 에러 복구)를 core 스킬로 이식하고, 보안 프레임워크는 dev-playbook의 `extensions/` 위치에 충실하게 **별도 opt-in 플러그인**으로 구현하는 것이 적합.

Priority 순서:
- **P1**: 5개 core 스킬 신규 작성 (user-stories, nfr-requirements, nfr-design, infrastructure-design) + 보안 extension 플러그인 메커니즘 설계
- **P2**: 6개 개선 (depth-levels, error-handling, workflow-changes, 모호성 탐지, build-and-test 확장, reverse-engineering)
- **P3**: 5개 장기 확장 (functional-design, risk assessment, C4 model, operations phase, content-validation)
