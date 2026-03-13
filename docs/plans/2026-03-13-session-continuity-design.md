# Session Continuity + 태스크 재검증 + TDD 명시 설계

**Date**: 2026-03-13
**Complexity**: Standard
**Approach**: A안 — 점진적 확장 (기존 파일에 섹션/단계 추가, 신규 파일 1개)

## 배경

### 해결할 문제 3건

1. **세션 재개 시 아티팩트 미로드** — 세션이 끊기고 재개하면 이전 단계 산출물을 자동으로 로드하지 않아 맥락이 유실됨
2. **태스크 재검증 부재** — CONSTRUCTION 재개 시 이전 완료 태스크의 테스트가 여전히 통과하는지 확인하지 않음
3. **workflow-planning에 TDD 미명시** — 계획 단계에서 TDD 적용 여부가 보이지 않아 작업 규모 파악 어려움

### 설계 결정 (brainstorming에서 확정)

| # | 결정 | 선택 |
|---|------|------|
| Q1 | 아티팩트 로딩 범위 | **B** — 현재 Phase + 직전 Phase 핵심 산출물 |
| Q2 | 기록 체계 | **C** — audit 강화 + session-summary + 핵심 전환점 commit hash |
| Q3 | 태스크 재검증 | **B** — 직전 unit 테스트 → 실패 시 전체 확대 |
| Q4 | workflow-planning TDD | **A** — Stage Depths에 TDD 참조 한 줄 추가 |

---

## 변경 대상

### 신규 파일

#### `skills/_shared/patterns/session-continuity.md`

Phase별 아티팩트 로딩 규칙 + session-summary 템플릿 + 재검증 프로토콜을 정의.

**내용 구조:**

```markdown
# Session Continuity Pattern

## 1. 아티팩트 로딩 규칙

세션 재개 시 Phase Orchestrator가 컨텍스트 로드 단계에서 참조.
모든 경로는 `devflow-docs/` 기준이다.

### INCEPTION 재개

현재 Stage에 따라 누적 로드:

| 재개 Stage | 로드할 파일 |
|-----------|-----------|
| requirements-analysis | workspace.md |
| user-stories / nfr-requirements | workspace.md, requirements.md |
| workflow-planning | workspace.md, requirements.md, user-stories.md(있으면), nfr-requirements.md(있으면) |
| application-design | 위 전체 |

### CONSTRUCTION 재개

항상 로드:
- devflow-state.md
- inception/workflow-plan.md (기존과 동일)

추가 로드 (직전 Phase 핵심 산출물):
- inception/requirements.md
- inception/application-design.md (있으면)
- inception/units.md (있으면)

현재 unit 컨텍스트:
- construction/{unit-name}/code-plan.md (있으면)

### executing-plans 재개

- 계획 파일 로드 (기존과 동일)
- devflow-audit 교차 확인 (기존과 동일)
- session-summary.md 로드 (신규)

### 로딩 후 컨텍스트 요약

로드 완료 후 사용자에게 간략 요약 표시:
```
📋 컨텍스트 로드 완료
- 로드한 파일: [count]개
- Phase: [current phase]
- 마지막 완료: [last completed stage/unit]
```

## 2. Session Summary

### 생성 타이밍

| 시점 | 트리거 |
|------|--------|
| INCEPTION 스테이지 완료 | Inception Orchestrator가 각 스테이지 게이트 승인 시 업데이트 (최초 생성 포함) |
| Phase 전환 | INCEPTION → CONSTRUCTION 전환 시 Entry Orchestrator가 업데이트 |
| Unit 완료 | Construction Orchestrator가 unit 구현 게이트 승인 시 업데이트 |
| CONSTRUCTION 완료 | Entry Orchestrator가 최종 업데이트 |

**참고**: session-summary.md는 INCEPTION 첫 번째 스테이지 완료 시 생성됨. INCEPTION 중간에 세션이 끊겨도 재개 시 이 파일로 맥락 복원 가능.

### 파일 위치

`devflow-docs/session-summary.md`

### 템플릿

```markdown
# Session Summary

**Last Updated**: [ISO 8601]
**Commit**: [short hash]

## Current State
- Phase: [INCEPTION | CONSTRUCTION | complete]
- Stage: [current stage]
- Complexity: [level]
- Approach: [selected approach name]

## Key Decisions
- [timestamp] [결정 내용] — [이유 한 줄]
- ...

## Completed Work
### INCEPTION
- [x] workspace-detection — [한 줄 결과]
- [x] requirements-analysis — [한 줄 결과]
- ...

### CONSTRUCTION
- [x] unit: [name] — [한 줄 결과]
- [ ] unit: [name] — (진행 중)
- ...

## Next Steps
- [다음 작업 설명]
<!-- Key Decisions, Completed Work는 최근 20개까지만 유지. 초과 시 오래된 항목 삭제. -->

## For Next Session
- [인수인계 시 알아야 할 핵심 맥락]
- [주의사항이나 미해결 이슈]
```

## 3. Audit 강화

기존 audit 로그에 결정 이유 필드 추가.

### 기존 형식
```
[timestamp] [stage] — [user choice: A/B/C]
```

### 강화 형식
```
[timestamp] [stage] — [user choice: A/B/C] — [결정 이유/맥락 한 줄]
```

### 하위 호환성
기존 형식 로그도 유효하다. `— [이유]` 부분은 선택적이며, 파싱 시 없어도 정상 처리한다.

## 4. Commit Hash 기록

### 기록 지점
- 세션 시작/재개 시
- Phase 전환 시
- Unit 구현 완료 시

### 수집 방법
`git rev-parse --short HEAD` (git 미사용 환경에서는 `(no git)` 표기)

### 기록 위치
- session-summary.md의 `**Commit**` 필드 (최신만)
- audit 로그의 Phase 전환/Unit 완료 항목에 inline

## 5. 태스크 재검증 프로토콜

CONSTRUCTION 세션 재개 시 construction-orchestrator가 실행.

### 재검증 실행 주체 규칙

- **construction-orchestrator 경유**: construction-orchestrator의 Step 1.5에서 재검증 실행
- **executing-plans 독립 실행**: executing-plans가 construction-orchestrator 외부에서 호출된 경우에만 자체 재검증 실행
- **중복 방지**: executing-plans가 construction-orchestrator 내부에서 호출된 경우, 이미 Step 1.5에서 재검증 완료이므로 재검증 스킵

### 재검증 후 복귀 경로

재검증 실패 → debugging 완료 시:
- construction-orchestrator: 기존 Debugging 라우팅 패턴 적용 (debugging Return 수신 → build-and-test 재실행이 아닌, 재검증 재실행)
- executing-plans: debugging 완료 후 재검증 재실행 → 통과 시 정상 재개

### 프로세스

1. devflow-state에서 완료 unit 목록 확인
2. 완료 unit이 있으면 → 직전 완료 unit의 테스트 실행
3. 결과에 따라 분기:

**통과 시:**
```
✅ 재검증 통과 — [unit-name] 테스트 [N]개 통과
다음 작업부터 재개합니다.
```
→ 정상 진행

**실패 시:**
```
⚠️ 재검증 실패 — [unit-name] 테스트 [N]개 중 [M]개 실패

A) 전체 테스트 스위트 실행 (회귀 범위 확인)
B) systematic-debugging으로 즉시 조사
```
→ A 선택 시 전체 실행 후 결과에 따라 debugging 라우팅
→ B 선택 시 바로 debugging 진행
```

---

### 수정 파일

#### 1. `skills/aidlc-using-devflow/SKILL.md`

**Resume Flow 변경:**

현재 (65-85줄):
- devflow-state.md 읽기 → 재개 게이트 → Phase Orchestrator 호출

변경:
- devflow-state.md 읽기
- **session-summary.md 로드 (있으면)** → 재개 게이트에 마지막 완료 정보 표시
- **commit hash 기록**: 재개 시 현재 HEAD 커밋을 audit에 기록
- Phase Orchestrator 호출

**INCEPTION 완료 시 변경 (89-93줄):**

현재:
- Phase를 CONSTRUCTION으로 업데이트 → construction-orchestrator 호출

변경:
- Phase 업데이트
- **session-summary.md 업데이트** (INCEPTION 완료 내용 + commit hash)
- construction-orchestrator 호출

**CONSTRUCTION 완료 시 변경 (95-110줄):**

현재:
- Phase complete → 완료 안내

변경:
- Phase complete
- **session-summary.md 최종 업데이트** (전체 완료 + commit hash)
- 완료 안내

#### 2. `skills/aidlc-inception-orchestrator/SKILL.md`

**session-summary 업데이트 추가:**

각 스테이지 게이트 승인 시 (Step B: 결과 표시 + 로깅 이후):
- **session-summary.md 업데이트** (완료 스테이지 + 핵심 결과 한 줄)
- 최초 스테이지 완료 시 session-summary.md 신규 생성

기존 아티팩트 로딩은 변경 없음 — 각 스테이지 스킬이 이미 자체 로드 (예: workflow-planning Step 1).

#### 3. `skills/aidlc-construction-orchestrator/SKILL.md`

**Step 1: 컨텍스트 로드 확장 (30-36줄):**

현재:
- devflow-state.md
- workflow-plan.md

변경:
- devflow-state.md
- workflow-plan.md
- **inception/requirements.md** (추가)
- **inception/application-design.md** (있으면, 추가)
- **inception/units.md** (있으면, 추가)
- **session-summary.md** (있으면, 추가)
- `_shared/patterns/session-continuity.md` 참조 명시

**Step 1.5 신규 — 재검증 (완료 unit이 있는 경우):**

Step 1과 Step 2 사이에 삽입:
- 완료 unit 존재 확인
- 있으면 → 직전 unit 테스트 실행
- 결과에 따라 분기 (session-continuity.md의 재검증 프로토콜)

**Unit 구현 완료 시 (106줄 부근):**

현재:
- devflow-state의 Completed Units에 unit명 추가

변경:
- Completed Units 추가
- **session-summary.md 업데이트** (완료 unit + commit hash)

#### 4. `skills/aidlc-executing-plans/SKILL.md`

**세션 재개 섹션 확장 (56-58줄):**

현재:
1. 체크박스 `[x]` 파싱
2. devflow-audit 교차 확인
3. 다음부터 재개

변경:
1. **session-summary.md 로드** (있으면)
2. 체크박스 `[x]` 파싱
3. devflow-audit 교차 확인
4. **직전 완료 태스크의 테스트 실행** (재검증 — 독립 실행 시에만. construction-orchestrator 경유 시 스킵)
5. 재검증 통과 → 다음부터 재개
6. 재검증 실패 → 사용자에게 전체 실행 / debugging 선택 게이트

#### 5. `skills/aidlc-workflow-planning/SKILL.md`

**Step 4: Save artifact — Stage Depths 섹션 변경 (111-115줄):**

현재:
```markdown
## Stage Depths
- application-design: [depth]
- units-generation: [depth]
- code-generation: [depth]
- build-and-test: [depth]
```

변경:
```markdown
## Stage Depths
- application-design: [depth]
- units-generation: [depth]
- code-generation: [depth] (TDD protocol 적용 — _shared/tdd-protocol.md)
- build-and-test: [depth]
```

#### 6. `skills/_shared/devflow-conventions.md`

**신규 섹션 추가:**

```markdown
## Session Continuity 규약

- `_shared/patterns/session-continuity.md` — 아티팩트 로딩 규칙, session-summary 템플릿, 재검증 프로토콜
- 세션 재개 시 Phase Orchestrator가 이 패턴을 참조하여 컨텍스트 로드
- session-summary.md는 Phase 전환 및 Unit 완료 시 자동 업데이트
- commit hash는 핵심 전환점에서만 기록 (세션 시작/재개, Phase 전환, Unit 완료)

### Audit 강화 형식
기존 `[timestamp] [stage] — [choice]`에 결정 이유 한 줄 추가:
`[timestamp] [stage] — [choice] — [이유]`
```

---

## 변경하지 않는 것

- **inception-orchestrator**: INCEPTION 재개 시 아티팩트 로딩은 각 스테이지 스킬이 이미 자체 처리 (workflow-planning Step 1 등)
- **gate-patterns.md**: 기존 게이트 패턴 변경 없음, 재검증은 construction-orchestrator 고유 로직
- **tdd-protocol.md**: 내용 변경 없음, workflow-planning에서 참조만 추가
- **code-generation**: 변경 없음

---

## 의존성 / 실행 순서

```
1. _shared/patterns/session-continuity.md (신규) — 다른 파일들이 참조
2. devflow-conventions.md (규약 추가) — 1과 동시 가능
3. construction-orchestrator (컨텍스트 로드 + 재검증 + summary 업데이트)
4. using-devflow (resume flow + phase 전환 시 summary)
5. executing-plans (세션 재개 확장)
6. workflow-planning (TDD 한 줄 추가)
```

3~6은 독립적으로 병렬 수정 가능 (1, 2 완료 후).
