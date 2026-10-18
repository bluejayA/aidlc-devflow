# AIDLC DevFlow — 세션 기록 및 컨텍스트 핸드오프 메커니즘 분석

**작성일**: 2026-04-24
**대상 버전**: v1.8.0 (BL-079 + BL-080 진행 중)
**범위**: 세션 상태 저장, 재개 프로토콜, 스테이지/서브에이전트 간 컨텍스트 핸드오프

---

## 1. 개요

aidlc-devflow 플러그인은 멀티 세션, 멀티 스테이지로 진행되는 장기 워크플로우를 지원하기 위해 다음 4가지 축으로 세션 컨텍스트를 관리한다.

1. **파일 기반 SSOT** — markdown 파일 3종 (`devflow-state.md`, `session-summary.md`, `audit.md`)
2. **3계층 orchestrator** — entry → phase → stage 순으로 재개 책임 분담
3. **명시적 artifact 경로 핸드오프** — 스테이지/서브에이전트 간에는 파일 경로만 전달
4. **L1 ingest hook** — 파일 수정 이벤트를 자동으로 audit log에 기록

설계의 일관된 원칙은 **"메모리/DB가 아닌 파일에 기록하고, 재개 시 단순 이어가기가 아닌 직전 산출물 재검증을 강제한다"** 이다.

---

## 2. 세션 상태 SSOT — 파일 3종

### 2.1 devflow-state.md

**경로**: `devflow-docs/devflow-state.md`

**포맷**: Heading 기반 Markdown (YAML frontmatter 의도적 회피)

**주요 섹션**:
- `## Current Phase` — INCEPTION / CONSTRUCTION
- `## Current Stage` — workspace-detection, requirements-analysis 등
- `## Complexity` — Minimal / Standard / Comprehensive
- `## Selected Approach` — 워크플로우 선택 결과
- `## Units` — 분해된 unit 목록
- `## Completed Units` — CONSTRUCTION 진행 추적
- `## Worktree` — branch, path
- `## Last Updated` — ISO8601 타임스탬프

**Race condition 보호 설계**:
- `hooks/post-tool-file-edit:131-159` — hook은 `## Last Updated` 필드만 soft-save
- 구조 섹션(Phase/Stage/Units 등)은 **스킬만 수정** — hook은 절대 건드리지 않음
- 동일 파일에 hook과 스킬이 동시 쓸 때 발생하는 race를 필드 분리로 해결

**R/W 주체**:
- Write: `aidlc-using-devflow`, `aidlc-inception-orchestrator`, `aidlc-construction-orchestrator`
- Read: 7개 이상 스킬 (context load 시), `aidlc-executing-plans` (재개 시)

### 2.2 session-summary.md

**경로**: `devflow-docs/session-summary.md`

**생성/업데이트 타이밍** (`session-continuity.md:59-72`):
- INCEPTION 첫 스테이지 완료 시 초기 생성
- 각 스테이지 게이트 승인 후 업데이트
- 스테이지 내부 중간 진행은 `[~]` 마커로 in-progress 표시

**주요 섹션**:
- `## Current State` — Phase, Stage, Complexity, Approach
- `## Key Decisions` — 타임스탬프 + 결정 이유
- `## Completed Work` — INCEPTION/CONSTRUCTION별 `[x]`/`[~]` 체크리스트
- `## Deferred Stubs` — 미완 작업
- `## For Next Session` — 미결 맥락 (가장 중요)

**역할**: 세션 중단 시 다음 세션이 "무엇을 어디서 왜 멈췄는가"를 한 파일에서 읽을 수 있게 함.

### 2.3 audit.md

**경로**: `devflow-docs/audit.md`

**생성 주체**: `hooks/post-tool-file-edit` (자동)

**포맷**: `- [ISO8601] — [event-type] — [file-path]`

**Event Type Taxonomy** (15종):
file-edit, stage-complete, decision, solution-store, error, …

**Safety Measures**:
- Exclusion: `tests/`, `hooks/`, `.archive/`, `audit.md` 자신
- Whitelist: `devflow-docs/`, `docs/`, `skills/`, `CLAUDE.md`만 기록 대상

---

## 3. 재개 메커니즘 — 3계층 Orchestrator

### 3.1 aidlc-using-devflow (Entry)

**파일**: `skills/aidlc-using-devflow/SKILL.md:33-88`

**판별 로직**:
```
Step 1: devflow-state.md 존재 확인
  ├─ 없음 → New Flow (devflow-docs/ 초기화)
  └─ 있음 → Resume Flow
            └─ inception/ 산출물 존재 시 2-option gate
                ├─ UPDATE: 기존 파일 유지, 새 기능 추가
                └─ Clean start: .archive/inception-[ts]/로 이동
                                (workspace.md만 보존)
```

### 3.2 aidlc-construction-orchestrator (Phase)

**파일**: `skills/aidlc-construction-orchestrator/SKILL.md:58-64`

**Step 1.5 재검증**:
- `devflow-state`의 `## Completed Units` 확인
- 완료 unit 존재 → `session-continuity.md` §4 "태스크 재검증 프로토콜" 적용
- 통과 → Step 2 진행 / 실패 → systematic-debugging 라우팅

### 3.3 aidlc-executing-plans (Stage)

**파일**: `skills/aidlc-executing-plans/SKILL.md:63-80`

**재개 4단계**:
1. `session-summary.md` 로드 (이전 맥락)
2. 체크박스 `[x]` 파싱으로 완료 태스크 식별
3. `audit.md` 교차 확인
4. 직전 완료 태스크 재검증 (독립 실행 시만)
   - 통과 → 다음 태스크부터 재개
   - 실패 → systematic-debugging 게이트

**핵심**: 단순 "이어하기"가 아닌 **재검증 후 이어가기**. 외부 변경 (다른 도구의 수정, 의존성 업데이트 등)으로 인한 silent regression 방지.

---

## 4. 컨텍스트 핸드오프 — Artifacts & Paths

### 4.1 INCEPTION → CONSTRUCTION

**규칙 정의**: `skills/_shared/patterns/session-continuity.md:28-38`

| 파일 | 경로 | 핸드오프 정보 |
|------|------|---------------|
| `requirements.md` | `devflow-docs/inception/` | 요구사항 |
| `application-design.md` | `devflow-docs/inception/` | 아키텍처 |
| `units.md` | `devflow-docs/inception/` | Unit 분해 + 인터페이스 |
| `workspace.md` | `devflow-docs/inception/` | Brownfield/Greenfield 정보 |
| `workflow-plan.md` | `devflow-docs/inception/` | Approved Stages, Stage Depths |
| `functional-design-*.md` | `devflow-docs/inception/` | (Comprehensive only) 상세 설계 |
| `devflow-state.md` | `devflow-docs/` | Phase 상태, Completed Units |

### 4.2 CONSTRUCTION 내 Unit 산출물

```
devflow-docs/construction/
  └── [unit-name]/
      ├── code-plan.md
      ├── implementation/   # 생성 코드
      └── test-results.md
```

### 4.3 디렉터리 전체 구조

```
devflow-docs/
├── devflow-state.md              # SSOT — Phase/Stage/Complexity
├── session-summary.md            # SSOT — 진행 상황 + 미결 맥락
├── audit.md                      # SSOT — 자동 이벤트 로그
├── backlog.md                    # 향후 작업
├── .archive/                     # 이전 세션 아카이브
│   ├── inception-[timestamp]/
│   └── construction-[timestamp]/
├── inception/                    # INCEPTION 산출물
│   ├── workspace.md
│   ├── requirements.md
│   ├── application-design.md
│   ├── units.md
│   ├── workflow-plan.md
│   └── functional-design-*.md
├── construction/                 # CONSTRUCTION 산출물 (unit별)
│   └── [unit-name]/
│       ├── code-plan.md
│       └── implementation/
└── tracking/                     # 메트릭, 진행 추적
```

---

## 5. 서브에이전트 핸드오프 — 격리(Isolation) 프로토콜

### 5.1 aidlc-subagent-driven-development

**파일**: `skills/aidlc-subagent-driven-development/SKILL.md:40-51`

**Orchestrator 호출 신호**:
```
SDD: units=[devflow-docs/inception/units.md],
     summary=[devflow-docs/session-summary.md],
     complexity=[level],
     functional-designs=[devflow-docs/inception/functional-design-*.md]
```

**전달 정보**:
- `units.md` — unit 목록 + 인터페이스
- `session-summary.md` — 완료 상태 + 이전 진행
- `functional-design-*.md` — (Comprehensive only)

**격리 규칙** (의도적 차단):
- 이전 unit의 `code-plan.md` 전달 금지
- 이전 unit의 구현 코드 전달 금지
- 이전 unit의 변경 파일 목록 전달 금지

→ **Context pollution 방지**가 설계 의도. 신선한 컨텍스트로 unit 별 독립 실행.

### 5.2 aidlc-dispatching-parallel-agents

**파일**: `skills/aidlc-dispatching-parallel-agents/SKILL.md:64-104`

**에이전트 프롬프트 템플릿**:
```
## 태스크: [name]
### 목표: [1문장]
### 컨텍스트:
- 프로젝트 루트, 작업 디렉토리
- 관련 파일 목록
- 기술 스택
```

**독립성 검증**: 각 에이전트는 다른 에이전트 결과에 의존하지 않아야 함 (공유 상태 없음).

---

## 6. Hooks 체계

### 6.1 hooks.json

**파일**: `hooks/hooks.json`

```json
{
  "SessionStart": [
    { "matcher": "startup|resume",
      "command": "hooks/session-start" }
  ],
  "PostToolUse": [
    { "matcher": "Edit|Write|MultiEdit",
      "command": "hooks/post-tool-file-edit" }
  ]
}
```

### 6.2 session-start hook

**파일**: `hooks/session-start`

- 서브에이전트 모드 제외 (`CLAUDE_AGENT_ID` 체크)
- 온보딩 메시지 출력 (사용 가능 스킬 목록)

### 6.3 post-tool-file-edit hook (L1 Ingest)

**파일**: `hooks/post-tool-file-edit`

**Trigger**: Edit, Write, MultiEdit, NotebookEdit
**Output**: `audit.md`에 ISO8601 이벤트 추가
**구현 특이점**: `devflow-state.md`의 `## Last Updated`만 soft-save (race 방지)

---

## 7. 진행 중인 확장 — Knowledge System & Checkpoint

### 7.1 Knowledge System Phase 1 (PR #157)

**설계 문서**: `docs/research/knowledgesystem/`
**Baseline**: T0 = 2026-04-13 (관측 시작)

**6-Type Taxonomy**:
1. **Decision** — 아키텍처/설계 결정
2. **Solution** — 문제 해결 방법 (live state 목표)
3. **Pattern** — 반복 구조 (skill pattern, design pattern)
4. **Skill** — AIDLC 스킬 정의
5. **Evidence** — 실행 결과, 테스트 로그, audit 이벤트
6. **SessionState** — `devflow-state.md`, `session-summary.md`

**Solution Layer 단독 소유권**:
- `aidlc-systematic-debugging`만 STORE 권한 보유
- construction-orchestrator의 K-gate는 verdict만 로깅
- 이유: dead layer 방지 + 이중 호출 제거

### 7.2 Memory Sync Reconciliation (BL-092)

**상태**: T+14 재평가 예정 (2026-04-28)
**다룰 항목 3건**:
- M1 강제 sync
- M3 ADR
- BL-091 통합

### 7.3 Checkpoint Memorize v0.3 (untracked)

**경로**: `docs/research/checkpoint-memorize/SPEC_devflow_checkpoint.md`
**저장 경로**: `.devflow/checkpoints/<head-sha>.md`
**목적**: PR 리뷰 시 human reviewer의 cognitive load 감소

**Front Matter 필드**:
- `checkpoint_version`, `head_sha`, `commit_range`
- `source_mode` (session+diff | diff-only | uncertain)
- `attribution_confidence` (high | medium | low)
- `redaction_applied`, `redaction_rules_version`
- `validator_warnings[]`

**파이프라인**:
1. **Redaction Filter** — rule-based, LLM 전 실행 (AWS keys, 내부 IP, PII 마스킹)
2. **Summarizer** — Haiku 4.5 (Rejected Alternatives, Uncertainty Flags, Constraints, Key Changes)
3. **Post-check Validator** — rule-based 공허 섹션/redaction leak 감지

**Enforcement 레벨**: advisory (Pilot default) | require_stub | require_checkpoint

---

## 8. 핵심 통찰 요약

| 항목 | 구현 방식 | 핵심 파일 |
|------|----------|-----------|
| 상태 저장 | Heading-based Markdown + soft-save hook | `devflow-state.md`, `post-tool-file-edit` |
| 재개 메커니즘 | 3단 orchestrator의 state 로드 + 재검증 | `session-continuity.md` |
| 산출물 경로 | `devflow-docs/{inception,construction}/` 구조화 | `workflow-plan.md`가 경로 정의 |
| 서브에이전트 격리 | 호출 신호 + 컨텍스트 파일 목록만 전달 | `aidlc-subagent-driven-development` |
| 감시(Audit) | file-edit hook → `audit.md`. event-type taxonomy | `post-tool-file-edit` + `audit.md` |
| Knowledge System | 6-type taxonomy, Solution layer 단독 writer | `knowledge-taxonomy.md` |

### 설계 일관성

1. **파일 기반 SSOT** — markdown만 사용. 외부 DB 의존성 0
2. **Hook + Skill 권한 분리** — hook은 metadata만, skill은 구조 변경
3. **격리 by default** — 서브에이전트엔 필요한 것만
4. **재검증 on resume** — 단순 이어가기 금지, 직전 태스크 통과 재확인 강제
5. **명시적 핸드오프** — implicit shared state가 아닌 파일 경로 전달

### 한계 및 향후 과제

- **session-summary.md**의 `[~]` in-progress 마커가 stale될 수 있음 (수동 갱신 의존)
- Hook이 markdown 파일 외 코드 변경을 모두 동등하게 기록 → 노이즈 가능성
- Knowledge System Solution Layer가 systematic-debugging에만 묶여 있어 일반 학습 케이스 누락 가능
- Checkpoint Memorize는 아직 spec 단계 (untracked) — 실제 구현 시 hook 통합 방식 결정 필요

---

## 참고 파일 (수집된 SSOT 문서)

- `skills/_shared/patterns/session-continuity.md` — 핸드오프 헌법
- `skills/aidlc-using-devflow/SKILL.md` — entry orchestrator
- `skills/aidlc-inception-orchestrator/SKILL.md`, `aidlc-construction-orchestrator/SKILL.md`
- `skills/aidlc-executing-plans/SKILL.md`
- `skills/aidlc-subagent-driven-development/SKILL.md`
- `skills/aidlc-dispatching-parallel-agents/SKILL.md`
- `hooks/hooks.json`, `hooks/session-start`, `hooks/post-tool-file-edit`
- `docs/research/knowledgesystem/handoff-context.md`
- `docs/research/checkpoint-memorize/SPEC_devflow_checkpoint.md`
