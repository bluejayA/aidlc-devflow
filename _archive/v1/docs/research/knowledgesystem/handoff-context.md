# Knowledge System — Handoff Context

> **Purpose**: Phase 1 설계 완료 후, 새 세션에서 이 프로젝트를 이어받는 Claude가 반드시 알아야 할 decision rationale과 과거 debate 결과를 영속화한다.
>
> **읽기 순서**: 이 문서 → `docs/plans/2026-04-13-knowledge-system-phase1-plan.md` → `docs/research/knowledgesystem/` 3개 문서 순.
>
> **작성 시점**: 2026-04-13, Phase 1 설계 완료 직후, 구현 착수 전.

---

## 1. 프로젝트가 무엇인가 (30초 요약)

aidlc-devflow v1.9.0 플러그인의 기존 자산(devflow-state, devflow-solutions, devflow-audit, 31 skills, 17 patterns, `docs/plans/`, `devflow-docs/`)을 **6-type knowledge taxonomy** (Decision/Solution/Pattern/Skill/Evidence/SessionState)로 재분류하고, **Solution layer를 dead state에서 live state로 전환**하며, **L1 ingest 훅(post-tool-file-edit)**을 도입하는 Phase 1 작업이다.

핵심 원칙:
- **기존 구조 재분류 > 새 시스템 구축**
- **6 타입 플랫, 하위 타입 없음**
- **새 최상위 디렉토리 없음**
- **Session start 토큰 오버헤드 ≤ +20%**
- **aidlc의 enforcement-heavy 철학 존중** (SPEC v0.3의 "memory only" 프레이밍 거부)

---

## 2. 반드시 알아야 할 5가지 (Must Know)

### 2.1 Solution layer는 live가 목표, 깨끗함은 Phase 2

**배경**: 레드팀 분석에서 "devflow-solutions가 untriggered 상태 → Solution layer empty → Pattern 승격 경로 죽음 → Knowledge Compounding 0"이 가장 치명적 리스크로 지적됨.

**결정**: Sprint 1에서 Solution은 **비어있지 않음**만 목표. 노이즈(유사 중복 등)는 수용. 필터링·승격 기준은 2주 운영 데이터 기반으로 Phase 2에 정함.

**왜 중요한가**: Phase 1 직후 Solution이 0개면 구조적 실패 신호(Re-evaluation Criteria T2 = Critical). 깔끔하지 않아도 우선 생성되어야 함.

### 2.2 STORE ownership은 `aidlc-systematic-debugging` 단독

**배경**: construction-orchestrator K-gate가 STORE를 호출하는 기존 설계에서, systematic-debugging이 user-invocable 경로로 직접 호출될 때 Solution이 생성되지 않는 **누락 경로**가 있었음. 동시에 "무조건 STORE"를 양쪽(orchestrator + systematic-debugging)에서 호출하면 **이중 호출** 발생.

**결정 (Q3 옵션 α)**: STORE 호출을 systematic-debugging 내부로 이관. construction-orchestrator K-gate는 Return verdict만 audit에 로그.

**기각된 대안**:
- **옵션 β** (context 분기): orchestrator/direct 감지 로직 필요 → Sprint 1 범위 초과
- **옵션 γ** (이중 호출 + dedup): duplicate check에 기대는 방치. audit에 REJECT 엔트리 과다
- **이유**: 레드팀 피드백 — "Solution layer를 살리는 방법은 이중 호출이 아니라 writer를 하나로 고정하는 것"

**영향**: Task 2(systematic-debugging STORE 추가) + Task 3(K-gate STORE 제거)는 **반드시 동일/연속 commit**. 분리 시 중간 상태에서 double call 또는 누락.

### 2.3 audit.md signal filtering은 Sprint 1에 하지 않음

**배경**: audit.md 성장 시 "모든 이벤트 = Evidence"가 되어 dominant source화될 위험. 레드팀이 "high-signal vs low-signal" 분류를 Sprint 1에 권고.

**결정 (Q1 옵션 A)**: **스키마(event type prefix)만 고정, 판단 로직(signal_level)은 Phase 2**.

**왜 그렇게 했나**:
1. signal_level 할당은 **주관성**이 큼. file-edit가 low인지, 특정 decision 파일 수정이 high인지 기준이 흔들림
2. **데이터 없이 기준 정하면 오설계 리스크**. 운영 데이터 축적 후 grep 필터 또는 summary skill 도입이 더 합리적
3. prefix 스키마만 고정해 두면 Phase 2에서 과거 데이터 **버리지 않고 재사용** 가능

**현재 정의된 event type prefix** (taxonomy §2.5):
`file-edit`, `stage-complete`, `stage-skipped`, `gate-response`, `decision`, `solution-store`, `solution-duplicate`, `solution-reject`, `session`, `phase-transition`, `flow-finished`, `error`, `stub-deferred`, `stub-scan-error`, `auto-approved`

### 2.4 SessionState 2파일 구조는 의도적 유지

**배경**: SPEC v0.3이 "session-state로 통합, wip.md 제거"를 제안. 하지만 현재 aidlc는 `devflow-state.md` + `session-summary.md`를 **7+ skill이 의존**하는 분리 구조.

**결정**: 2파일 유지. state = resume instruction, summary = completed work + deferred stubs + for-next-session.

**왜 합쳤지 않았나**: 통합은 7+ skill 수정이 필요한 파괴적 변경. SSOT 원칙은 이상적이나 ROI 낮음. **"의도적 경계" 문서화로 혼란 방지**하는 편이 나음.

### 2.5 taxonomy primary type은 classification, not enforcement

**배경**: 레드팀이 "exactly one primary type" 표현이 현실 drift를 무시할 위험 지적.

**결정**: taxonomy §1에 "classification, not enforcement" 명시. 스킬/훅/리뷰 로직이 primary type 값에 따라 **동작 분기하지 않음** 강제.

**왜 그렇게 했나**: 분류는 조직화 도구이지, runtime 게이트가 아님. 팀이 억지로 맞추거나 무시하게 만드는 것을 방지.

---

## 3. 레드팀 3회 + Codex 2회 리뷰 이력

### Red Team 1차 (설계 초기)

**Focus**: 설계 생존성 평가. "붙일 수 있는 수준 vs 터질 수 있는 지점"

**Verdict**: 실제 적용 가능. 단, 2-3주 내 터질 리스크 5개 존재:
1. audit.md 병목 + 오염
2. **Solution 시스템 untriggered (가장 치명적)**
3. SessionState soft-save 충돌
4. Pattern frontmatter 유지 메커니즘 없음
5. taxonomy 현실 drift

→ 이후 모든 결정이 이 5 리스크를 중심으로 조정됨.

### Red Team 2차 (debate 단계)

**Focus**: Q1(signal filtering) + Q2(Solution trigger) 옵션 평가

**Verdict**:
- Q1 = 옵션 A (prefix만 문서화) — 근거: 주관성, 데이터 부재, 확장성
- Q2 = 옵션 A+D (systematic-debugging 완료 시 무조건 STORE) — 근거: dead layer 방지 > 깨끗함

### Red Team 3차 (Q3 debate)

**Focus**: Change 2 ↔ Change 6 충돌 해결 (writer ownership)

**Verdict**: 옵션 α (systematic-debugging 단독 owner) — 근거: writer 1개 고정, user-invocable + orchestrator 모두 커버

**핵심 인사이트**: "Solution layer를 살리는 방법은 이중 호출이 아니라 writer를 하나로 고정하는 것"

### Codex 리뷰 1차 (Step 1+2 검증)

**Verdict**: Step 1 PARTIAL, Step 2 PARTIAL

**핵심 정정 3건**:
1. `devflow-docs/inception/design-review-raw/` Evidence 매핑 누락 → 추가
2. stale `devflow-audit.md` 참조가 1곳 아닌 **4곳** + legacy 파일 존재 → executable-next-steps Change 1에 통합
3. Solution K-gate call-site semi-concrete → Change 2(이후 Change 6로 이관)에서 5 필드 명시

**내 오류 자인**: 0-byte archive 주장 철회 (실제는 정상 크기 125-2344 bytes). 초기 `ls -l` awk 파싱 오류.

### Codex 리뷰 2차 (Step 3+4+5 검증)

**Verdict**: Step 3 PARTIAL, Step 4 PARTIAL, Step 5 PARTIAL

**Blocking 3건**:
1. **Rotation 경로 충돌**: `devflow-docs/audit.md` (파일) + `devflow-docs/audit/` (디렉토리) 공존 불가 → `audit-log/YYYY-MM.md`로 변경
2. **Hook matcher 과도**: `Edit|Write` 단독은 위험 → exclusion list 필수
3. **state.md 파서 contract**: YAML frontmatter 가정 오류 → heading grep 기반으로 수정

**추가 정정**:
- `tests/*.py` Evidence 분류 기각 → 범위 외
- `.archive/` dual-type 기각 → Evidence 단일
- `docs/research/*.md` Decision.draft 기각 → 범위 외 (workspace, 승격 시에만 편입)
- Pattern primary dimension 강화 (topical 단독 → applies_to/status/source/last_validated)
- 100 token guard band 확보 → effective headroom 329

---

## 4. 주요 Decision + 기각된 대안

### 4.1 `.devflow/` 신규 디렉토리 — 기각

**SPEC v0.3 제안**: `.devflow/` 루트 신설
**기각**: 기존 `devflow-docs/` 이미 프로젝트 working memory로 활성. 병행 구조는 혼란. 7+ skill이 `devflow-docs/`에 의존.

### 4.2 `skills/knowledge/` vs `skills/workflow/` 분리 — 기각

**SPEC v0.3 제안**: 모듈 경계로 분리
**기각**: 28+ skill이 flat 구조에 의존. 이동은 파괴적. 내부 모듈 경계는 `_shared/`, `_utils/` prefix로 이미 표현.

### 4.3 `adr-index.json` derived cache — 연기

**SPEC v0.3 제안**: ADR 탐색 성능 최적화
**연기**: YAGNI. Decision 14개 수준에서 grep 충분. Sprint 2+ 재평가.

### 4.4 Thread 개념 — 연기

**SPEC v0.3 제안**: 결정 서사 추적 구조
**연기**: Pattern + Decision의 `related` 필드 체인이 서사 대체 가능. Sprint 2+ 복잡도 요구 시 재검토.

### 4.5 "Phase 1 = memory only, no enforcement" 철학 — 기각

**SPEC v0.3 제안**: 기억 시스템과 실행 시스템 분리
**기각**: aidlc는 이미 enforcement-heavy (A/B gate, K-gate, review gate). 이 철학은 aidlc와 정체성 충돌. 기록과 enforcement 공존 설계 채택.

### 4.6 docs/research/*.md을 Decision.draft로 포함 — 기각 (2차 Codex 리뷰 후)

**초기 제안**: lifecycle=draft로 taxonomy 진입
**기각 이유**: free-form workspace. frontmatter 강제 오버헤드. Decision 승격 시에만 `docs/plans/`로 편입하는 관행 유지.

### 4.7 tests/*.py을 Evidence.kind=test로 포함 — 기각 (2차 Codex 리뷰 후)

**초기 제안**: 검증된 behavior 기록
**기각 이유**: 테스트는 **구현 코드**. 실행 **결과/로그**만 Evidence. 이미 audit.md에 build-and-test-result 기록.

### 4.8 hybrid 7개 `decomposition_target` 전체 작성 — Sprint 1 optional

**레드팀 제안**: label-only 방지 위해 rationale 필수
**타협**: `model_dependency` + `amplification_notes` 각 1줄만 Sprint 1 필수. 전체 decomposition_target (drop/absorb_into) 은 실제 lightening 시점에 작성.

---

## 5. 현재 상태 (Phase 1 착수 직전)

### 완료된 작업

- 설계 3개 문서 작성 완료 (`docs/research/knowledgesystem/`)
- Phase 1 Implementation Plan 작성 완료 (`docs/plans/2026-04-13-knowledge-system-phase1-plan.md`)
- 레드팀 3회 + Codex 2회 리뷰 반영 완료
- Phase 2 Re-evaluation Criteria 정의 완료 (plan 내부)
- Handoff context 영속화 완료 (본 문서)

### 대기 중인 작업

**Task 1-6 실행 미착수**. 실행 순서 엄격 준수 필요:
```
Task 1 → Task 2+3 (동일/연속 commit) → Task 4 → Task 5 → Task 6
```

### 알려진 side effects

- **tests/test_devflow_solutions.py** 가 construction-orchestrator의 직접 STORE 호출을 검증하는 테스트 포함 가능성. Task 3 Step 5에서 확인 후 필요 시 재구성.
- hook 구현 시 **jq** 의존성. 대부분 macOS/Linux에 기본 설치되나 부재 환경에서는 pure bash fallback 필요 (Sprint 2 검토 항목).

### 시점별 판단 기준

| 시점 | 판단 | 근거 |
|------|------|------|
| 지금 (설계 완료) | Task 1-6 실행 착수 가능 | 3회 레드팀 + 2회 Codex 리뷰 반영 완료 |
| 2-3일 운영 후 | Re-evaluation Criteria T1-T10 체크 | plan의 체크리스트 준수 |
| 14일 운영 후 | 레드팀 3차 리뷰 호출 + Phase 2 plan 작성 | 운영 데이터 축적 충분 |

---

## 6. 새 세션 진입 시 행동 지침

**만약 새 Claude가 이 프로젝트를 처음 본다면**:

1. `memory/MEMORY.md` 확인 → project 섹션에서 knowledge-system-phase1 entry 찾기
2. 본 `handoff-context.md` 읽기 (이 문서)
3. `docs/plans/2026-04-13-knowledge-system-phase1-plan.md` 읽기
4. 필요 시 `docs/research/knowledgesystem/` 3개 문서 심화

**Phase 2 재평가 요청 받았을 때**:
1. plan의 "Phase 2 Re-evaluation Criteria" 섹션 로드
2. 실측 스크립트 실행 (plan의 측정 대상 테이블)
3. T1-T10 트리거 검증
4. 우선순위 규칙 적용
5. **주관적 판단 금지**. 트리거 근거 없이 Phase 2 항목 선택 안 함.

**설계 결정이 불명확할 때**:
본 문서 §4 (기각된 대안) 참조. 이미 기각된 방안 재제안 시 새로운 근거 없으면 유지.

**레드팀/Codex 리뷰가 필요할 때**:
본 문서 §3 이력 참조. 이미 수용된 권고 재권고 시 확인. 새 권고는 기존 5 리스크 중 어느 것에 해당하는지 매핑.

---

## 7. 참조 문서

| 경로 | 역할 |
|------|------|
| `docs/plans/2026-04-13-knowledge-system-phase1-plan.md` | **실행 plan + Phase 2 Re-evaluation Criteria** |
| `docs/research/knowledgesystem/knowledge-taxonomy.md` | 6 타입 정의 + 관계 + 자산 매핑 |
| `docs/research/knowledgesystem/aidlc-knowledge-integration-plan.md` | 통합 전략 + 훅 설계 + 토큰 예산 |
| `docs/research/knowledgesystem/executable-next-steps.md` | Change 1-6 상세 patch (plan 재구성 전 원본) |
| `docs/research/knowledgesystem/PROMPT-claude-code-knowledge-integration.md` | 레드팀 원본 지시 (제약 + 6 타입 고정) |
| `docs/research/knowledgesystem/SPEC-knowledge-layer-sprint1-v0.3.md` | 참고 자료 (선택 통합 대상) |
| `docs/research/2026-04-06-skill-lifecycle-strategy.md` | BL-081 초안 분류 근거 |
| GitHub #145 | BL-081 이슈 (Phase 2 Compensation Decay + validator 잔존) |
