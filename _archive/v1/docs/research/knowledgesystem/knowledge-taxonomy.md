# aidlc-devflow Knowledge Taxonomy (Phase 1)

> **Date**: 2026-04-13
> **Status**: Design (pending implementation via executable-next-steps.md)
> **Scope**: aidlc-devflow plugin v1.9.0
> **Constraints applied**: red-team prompt at PROMPT-claude-code-knowledge-integration.md

---

## 1. Principle

**This is a classification system, NOT a pipeline.** Types have many-to-many relationships. Decision is **one of six** types, not a central hub.

Every existing asset is classified into **ONE primary type**. Additional relationships are expressed via `related` field references, never by splitting a file across types.

**Primary type is for classification, not enforcement.** 실제 자산은 type 경계를 걸치는 경우가 있으며, 이때 primary는 "가장 많이 해당하는 유형"을 의미한다. 스킬·훅·리뷰 로직이 primary type 값에 따라 동작을 분기하지 않는다. 분류는 조직화 도구이지, runtime enforcement 게이트가 아니다.

**Six types only. No subtypes. Scope / kind / role are fields, not subtypes.**

---

## 2. Six Knowledge Types

### 2.1 Decision

- **Purpose**: 설계·아키텍처·실행 계획의 명시적 기록
- **Scope** (field, not subtype): `plugin | flow | snapshot`
  - `plugin`: 플러그인 전역 결정, 여러 flow에 걸쳐 유효
  - `flow`: 현 개발 flow의 요구/설계 워킹셋 (flow 완료 시 snapshot으로 전환)
  - `snapshot`: 완료된 flow의 동결 결정 세트 (`.archive/`)
- **Storage**:
  - `plugin`: `docs/plans/YYYY-MM-DD-<topic>-design.md`, `docs/plans/YYYY-MM-DD-<feature>-plan.md`, `devflow-docs/backlog.md` (role=priority-queue)
  - `flow`: `devflow-docs/inception/*.md`, `devflow-docs/construction/{unit}/*.md`
  - `snapshot`: `devflow-docs/.archive/{inception,construction}-YYYYMMDD-HHMMSS/`
- **Writers**: `aidlc-brainstorming`, `aidlc-writing-plans`, 7개 inception/construction skills (`aidlc-workspace-detection`, `aidlc-requirements-analysis`, `aidlc-user-stories`, `aidlc-nfr-requirements`, `aidlc-workflow-planning`, `aidlc-application-design`, `aidlc-units-generation`, `aidlc-functional-design`, `aidlc-code-generation`, `aidlc-build-and-test`)
- **Lifecycle**: `draft → active → snapshot → archived`
- **Primary dimension**: `scope`
- **Secondary fields**: `promotion_candidate: bool`, `role` (for special cases like priority-queue)
- **Promotion**: `promotion_candidate: true` → backlog 노출 → shared 승격 후보
- **Scope is metadata only**: 스킬/훅이 scope 값에 따라 로직 분기하지 않는다. 분기 시 subtype-by-proxy가 되어 제약 위반.

### 2.2 Solution

- **Purpose**: 디버깅·문제 해결 경험 지식의 축적 (Knowledge Compounding)
- **Scope**: project-local (Sprint 1). Shared 승격은 Sprint 3+.
- **Storage**: `devflow-docs/solutions/{category}/YYYY-MM-DD-<slug>.md`
- **Writers**: `devflow-solutions` utility **(단독)**. `aidlc-construction-orchestrator`의 K 게이트에서 호출.
- **Lifecycle**: `active → stale (60d 미참조) → archived`
- **Primary dimension**: `category` (build | test | runtime | config | dependency) — 기존 스키마 유지
- **Secondary fields**: `project_type` (plugin | web | api | cli), `stack` (python | node | go | rust | markdown), `error_signature` (중복 판정 키), `last_validated`
- **Duplicate policy**: `error_signature` 완전 일치 → DUPLICATE, 70%+ 유사 → SAVE + `similar_to` 참조

### 2.3 Pattern

- **Purpose**: 재사용 가능한 설계/프로세스 템플릿, 검증된 일반화 지식
- **Scope**: plugin-global
- **Storage**: `skills/_shared/patterns/*.md`, `skills/_shared/reviewers/*.md` (prompt template), `skills/_shared/{devflow-conventions,gate-patterns,import-review-protocol,tdd-protocol}.md`, `CLAUDE.md` (project+user)
- **Writers**: 수동. 자동 생성 없음 (Sprint 1). Solution → Pattern 승격은 3회 이상 유사 Solution 누적 시 수동 승격.
- **Lifecycle**: `draft → active → deprecated`
- **Primary dimension**: 토픽 (파일명 기반: skill-design, gate, review, ...)
- **Required frontmatter (신규)**:
  - `type: pattern`
  - `applies_to: [skill-name, ...]`
  - `status: draft | active | deprecated`
  - `source: manual | promoted_from_solution`
  - `last_validated: YYYY-MM-DD`
- **Promotion**: Solution 누적으로 승격 시 `promoted_from_solution: [paths]` 필드 기록
- **Metadata staleness policy (Phase 1)**: 자동 갱신 없음. `last_validated`는 수동 migration/review 시점에 갱신. **2주~수개월 경과 시 stale 상태 수용**. Sprint 2+에서 validator 도입 검토 (BL-081 Phase 2 범위). Phase 1은 "구조만 세우고 유지 자동화는 나중에"로 진행.

### 2.4 Skill

- **Purpose**: 프로세스/워크플로우의 실행 단위 (AIDLC 방법론 구현체)
- **Scope**: plugin-global
- **Storage**: `skills/<name>/SKILL.md`
- **Writers**: `aidlc-writing-skills` (사용자 호출)
- **Lifecycle**: `draft → active → lightened → absorbed | archived` (BL-081)
- **Primary dimension**: **`skill_nature`** (`compensation | amplification | hybrid | infrastructure`)
  - `compensation`: 모델 약점 보상. 모델 발전 시 경량화 후보.
  - `amplification`: 조직/개인 고유 지식 인코딩. 영구 유지.
  - `hybrid`: 양쪽 겸함. 분해/합성 가능.
  - `infrastructure`: 유틸 (`_utils/`). 분류 대상 외 (skill_nature=null).
- **Secondary dimensions** (기존 유지):
  - `invoke_mode`: user-invocable | orchestrator-only
  - `return_behavior`: stop-no-gate | stop-with-gate
  - `version`, `author`, `category`
- **BL-081 초안 분류**: compensation 4 / amplification 17 / hybrid 7 / infrastructure 3 (총 31 스킬)
- **model_dependency** (compensation/hybrid 전용 필드): "모델이 해결 못하는 것"의 설명

### 2.5 Evidence

- **Purpose**: 실행·검증·관찰의 불변 기록 (증거 영속화)
- **Scope**: project-local, append-only
- **Storage**:
  - Primary (interaction): `devflow-docs/audit.md` — per-stage 상호작용 로그
  - Rotation (신규): `devflow-docs/audit-log/YYYY-MM.md` — 월별 아카이브 (Sprint 1은 warning-only)
  - Summary: `devflow-docs/tracking/session-YYYY-MM-DD.md` — 세션별 요약
  - Review-raw: `devflow-docs/inception/design-review-raw/*.md` — council 리뷰 원문 (inception-orchestrator가 생성)
  - Snapshot: `devflow-docs/.archive/*` — flow 완료 스냅샷 (Decision content는 read 시 파생, dual-type 금지)
- **Writers**:
  - `audit.md`: `devflow-audit` utility (**단독**)
  - `audit-log/`: rotation hook (Sprint 2 실제 구현)
  - `tracking/`: `aidlc-superpowers-tracking`
  - `design-review-raw/`: `aidlc-inception-orchestrator`
  - `.archive/`: `aidlc-using-devflow`, `aidlc-finishing-a-development-branch`
- **Lifecycle**: append-only, never updated. Rotation/archive만.
- **Primary dimension**: `kind` (interaction | summary | snapshot | review-raw)
- **Event type prefix (audit.md 엔트리 규약)**: audit.md append 시 다음 prefix 중 하나 사용:
  - `file-edit` — Edit/Write 도구로 파일 수정 (hook 자동)
  - `stage-complete` — devflow stage 완료 (orchestrator)
  - `stage-skipped` — devflow stage 스킵 (사유 포함)
  - `gate-response` — A/B/C/D 게이트 응답
  - `decision` — ADR/Design 문서 작성/변경 (skill 명시)
  - `solution-store` — devflow-solutions STORE 결과 (verdict 포함)
  - `session` — 세션 시작/종료/재개
  - `phase-transition` — INCEPTION → CONSTRUCTION 등
  - `flow-finished` — flow 종료 (옵션 A/B/D)
  - `error` — 훅/스킬 실패 로그
  - `stub-deferred`, `stub-scan-error` — brownfield stub 관련
  - `auto-approved` — auto-mode 자동 승인
- **Signal filtering policy (Phase 1)**: 위 prefix는 **스키마로만 고정**, 자동 filtering/signal-level 할당은 Phase 2+. Sprint 1은 prefix만 준수하여 후속 필터 도입 시 기존 데이터 재사용 가능하도록 구조만 확보.
- **Note**: 이미 timestamp + stage + actor가 매 엔트리에 포함되어 있어 별도 provenance 필드 불필요.

### 2.6 SessionState

- **Purpose**: 현재 작업의 resume instruction (기억 시스템 복원점)
- **Scope**: project-local, flow-scoped
- **Storage** (2파일 분리 의도적 유지):
  - `devflow-docs/devflow-state.md` — resume instruction (phase/stage/worktree/wip 등)
  - `devflow-docs/session-summary.md` — completed work + deferred stubs + for-next-session
- **Writers** (공유, 7+ 스킬):
  - `aidlc-using-devflow`, `aidlc-auto-mode`, `aidlc-executing-plans`, `aidlc-finishing-a-development-branch`
  - 업데이트 권한 skill: `aidlc-inception-orchestrator`, `aidlc-construction-orchestrator`, `aidlc-requirements-analysis`, `aidlc-code-generation`, `aidlc-build-and-test`
- **Lifecycle**: `active → archived` (flow 종료 시 `.archive/`로 이동)
- **Primary dimension**: `phase` (inception | construction | operations | complete | finished)
- **Format**: heading-based Markdown (`## Current Phase`, `## Current Stage` 등) — YAML frontmatter 아님. Sprint 1 파서는 heading grep 기반.
- **SSOT rationale**: 2파일 분리는 **의도적 경계** — state=resume instruction, summary=completed work narrative. 7+ skill이 이 분리 가정. 통합은 파괴적 변경. 현행 유지.

---

## 3. Relationship Matrix

**많은-many** 관계. 단방향 강제 없음. 관계는 각 자산 frontmatter의 `related` 필드로 표현.

| From ↓ / To → | Decision | Solution | Pattern | Skill | Evidence | SessionState |
|---|---|---|---|---|---|---|
| **Decision** | supersedes | — | generalizes-from | **defines** (어느 skill 사용) / operationalized-by | validated-by | referenced-by |
| **Solution** | supports | duplicates | promotes-to | triggered-by | validated-by | referenced-by |
| **Pattern** | generalizes | generalizes-from | — | operationalizes | — | — |
| **Skill** | produces | triggers-store | applies | — | produces | updates |
| **Evidence** | validates | validates | **observed-from** | **observed-from** | — | — |
| **SessionState** | references | references | — | invokes | **generates** | — |

### 핵심 관계 예시 (prompt 예시 준수)

- **Solution supports Decision** (Solution은 Decision을 뒷받침, 중심 아님)
- **Pattern generalizes Solution** (승격 방향)
- **Skill operationalizes Solution or Pattern** (실행 계층)
- **Evidence validates Decision or Solution**
- **SessionState references active Decision, invokes Skills, generates Evidence**

### 관계의 실제 구현

- **Decision → Skill "defines"**: Decision 본문에 "이 결정은 `aidlc-brainstorming` 적용 전제" 같은 명시 또는 `applicable_skills: [...]` 필드
- **Evidence → Pattern/Skill "observed-from"**: audit.md 엔트리의 stage 필드가 어느 skill 호출인지 기록 (이미 구현됨)
- **Pattern → Skill "operationalizes"**: Pattern의 `applies_to` 필드 (신규 도입)
- **Solution → Pattern "promotes-to"**: Pattern의 `promoted_from_solution` 필드 (신규 도입, 수동 승격 시 기록)

---

## 4. Scope Dimension (cross-cutting)

모든 타입에 적용 가능한 위치 분류 (field, not subtype):

| Scope | 의미 | 저장 위치 |
|-------|------|----------|
| `project` | 현 repo의 working memory | `devflow-docs/` 아래 |
| `plugin` | 플러그인 전역, 여러 repo에 걸쳐 유효 | `docs/`, `skills/_shared/`, `skills/<name>/` 등 |
| `archived` | 완료된 flow 스냅샷 | `devflow-docs/.archive/` |

**Sprint 1에서 `shared`, `org` tier는 예약만.** 실제 활성화는 Sprint 3+ (SPEC v0.3 "의미적 3층, 운영적 2층" 원칙).

---

## 5. Existing Asset → Primary Type Mapping

### Plugin-scope

| Asset | Primary Type | Scope | Related |
|-------|-------------|-------|---------|
| `skills/aidlc-*/SKILL.md` (28) | **Skill** | plugin | — |
| `skills/_utils/devflow-state/SKILL.md` | **Skill** (infrastructure) | plugin | → SessionState |
| `skills/_utils/devflow-audit/SKILL.md` | **Skill** (infrastructure) | plugin | → Evidence |
| `skills/_utils/devflow-solutions/SKILL.md` | **Skill** (infrastructure) | plugin | → Solution |
| `skills/_shared/patterns/*.md` (17) | **Pattern** | plugin | → Skills (applies_to) |
| `skills/_shared/reviewers/*.md` (12) | **Pattern** (prompt template) | plugin | → Skills (review protocols) |
| `skills/_shared/*-protocol.md`, `*-patterns.md`, `*-conventions.md` (4) | **Pattern** | plugin | — |
| `docs/plans/*-{design,plan}.md` (14) | **Decision** | plugin | ↔ design/plan pair |
| `CLAUDE.md` (project + user) | **Pattern** | plugin | — |

### Project-scope (`devflow-docs/`)

| Asset | Primary Type | Scope | Related |
|-------|-------------|-------|---------|
| `devflow-state.md` | **SessionState** | project | → session-summary |
| `session-summary.md` | **SessionState** | project | → devflow-state |
| `audit.md` | **Evidence** (kind=interaction) | project | → all types (observed-from) |
| `tracking/session-*.md` | **Evidence** (kind=summary) | project | → audit.md |
| `inception/*.md` | **Decision** (scope=flow) | project | → SessionState |
| `inception/design-review-raw/*` | **Evidence** (kind=review-raw) | project | → inception Decisions |
| `construction/{unit}/*.md` | **Decision** (scope=flow) | project | → Skill, Evidence |
| `solutions/{category}/*.md` | **Solution** | project | → Evidence, Decision |
| `.archive/*` | **Evidence** (kind=snapshot) | archived | — |
| `backlog.md` | **Decision** (role=priority-queue) | plugin | → plugin Decisions |

### 제외 (taxonomy 외, Out-of-scope)

| Asset | 사유 |
|-------|------|
| `docs/research/*.md` | 자유 형식 research workspace. Decision 승격 시에만 `docs/plans/`로 편입 |
| `tests/*.py` | 구현 코드. 테스트 실행 **결과/로그**만 Evidence (audit.md에 이미 기록) |
| `hooks/session-start`, `hooks/hooks.json` | 실행 인프라 |
| `.claude-plugin/plugin.json`, `pyproject.toml`, `.gitignore` | 설정 |
| `THIRD-PARTY-NOTICES`, `LICENSE` | 법적 artifact |
| `README.md`, `README.en.md` | 문서 (선택적 Pattern 가능하나 Sprint 1 미포함) |
| `devflow-docs/.tui-token` | 런타임 토큰 |
| `reverse-engineering/` | 독립 플러그인 (사용자 결정: 범위 외) |
| `devflow-docs/devflow-audit.md` | **LEGACY** — executable-next-steps에서 삭제 |

---

## 6. Constraints Honored

| 프롬프트 제약 | 준수 여부 |
|---|---|
| 6 타입만, 하위 타입 금지 | ✅ (scope/kind/skill_nature는 field) |
| Decision 중심 금지 | ✅ (Solution/Evidence/Skill이 Decision 없이 독립 존재) |
| 각 타입 purpose/scope/storage/lifecycle 정의 | ✅ |
| 기존 분류 시도 위에 구축 | ✅ (BL-081 skill_nature, Solution 5-field schema, invoke_mode/return_behavior, heading-based state.md 모두 흡수) |
| 새 최상위 디렉토리 금지 | ✅ (신규 `devflow-docs/audit-log/`만, 기존 루트 내부) |
| 파일 분할 금지 | ✅ (모든 자산 단일 primary type) |
| 추가 지식 타입 금지 | ✅ (6개 고정) |

---

## 7. BL-081 Integration Point

Skill 타입의 primary dimension = `skill_nature`는 6 타입 taxonomy의 **핵심 승격 메커니즘**이다.

- `amplification` Skill의 일반화 가능 부분 → **Pattern으로 승격** (수동)
- `compensation` Skill이 model-gap 해소 → `lightened → absorbed | archived`
- `hybrid` Skill → decomposition: amplification 부분은 Pattern으로, compensation 부분은 lightened

이 메커니즘 없이는 Skill ↔ Pattern 승격 경로가 작동하지 않아 타입 간 관계가 정적으로 퇴화.

**Sprint 1에서 BL-081 MVP 중 1, 2번 작업 (규약 정의, 28 skill 태깅)을 이 설계가 포함**. 3, 4번 작업 (Compensation Decay 분석, validator)은 BL-081 이슈에 남김.

---

## 8. References

- PROMPT: `docs/research/knowledgesystem/PROMPT-claude-code-knowledge-integration.md`
- SPEC v0.3 (선택 통합): `docs/research/knowledgesystem/SPEC-knowledge-layer-sprint1-v0.3.md`
- BL-081 분류 초안: `docs/research/2026-04-06-skill-lifecycle-strategy.md`
- Integration plan: `docs/research/knowledgesystem/aidlc-knowledge-integration-plan.md`
- Executable patches: `docs/research/knowledgesystem/executable-next-steps.md`
