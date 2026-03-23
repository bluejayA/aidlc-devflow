# Session Continuity Pattern

## 1. 아티팩트 로딩 규칙

세션 재개 시 Phase Orchestrator가 컨텍스트 로드 단계에서 참조한다.
모든 경로는 `devflow-docs/` 기준이다.

### INCEPTION 재개

각 스테이지 스킬이 자체적으로 필요한 파일을 로드한다 (참고용 테이블).
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
- inception/workflow-plan.md

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
| **스테이지 내부 핵심 결정** | Stage Skill이 내부 핵심 결정 시점에 중간 기록 (조기 업데이트) |
| Phase 전환 | INCEPTION → CONSTRUCTION 전환 시 Entry Orchestrator가 업데이트 |
| Unit 완료 | Construction Orchestrator가 unit 구현 게이트 승인 시 업데이트 |
| CONSTRUCTION 완료 | Entry Orchestrator가 최종 업데이트 |

session-summary.md는 INCEPTION 첫 번째 스테이지 완료 시 생성됨.
INCEPTION 중간에 세션이 끊겨도 재개 시 이 파일로 맥락 복원 가능.

### 조기 업데이트 규약 (스테이지 내부 중간 기록)

긴 스테이지 스킬이 내부 핵심 결정 시점에 session-summary.md를 업데이트한다.
세션이 스테이지 도중에 끊겨도 맥락을 복원할 수 있도록 하기 위함.

#### 스킬별 핵심 결정 시점

| 스킬 | 중간 기록 시점 |
|------|--------------|
| `requirements-analysis` | 해석 분기 확정 후, 핵심 질문 답변 후 |
| `application-design` | LIST 완료 후, DETAIL 주요 결정 후 |
| `code-generation` | Plan 승인 후, TDD Step 완료마다 |

#### 중간 기록 형식

`## Completed Work` 섹션에 진행 중 스테이지를 `[~]` 마커로 표시한다:

```markdown
### INCEPTION
- [x] workspace-detection — Brownfield
- [~] requirements-analysis — 해석 확정(B안), 질문 2/5 완료
```

```markdown
### CONSTRUCTION
- [~] code-generation — Plan 승인, Step 3/8 완료
```

`## For Next Session` 섹션에 미결 맥락을 기록한다:

```markdown
## For Next Session
- requirements-analysis: 질문 3~5 미답변. 질문 3은 "실시간 vs 배치" 선택
- 주의: 해석 B안(REST API) 확정됨, 변경 불필요
```

#### 스킬 내 업데이트 지침 형식

각 스킬에 아래 형태로 2~3줄만 추가한다:

```markdown
**session-summary 중간 기록**: [핵심 결정] 후 session-summary.md의
`## Completed Work`에 `[~] [stage] — [진행 상황]` 업데이트 +
`## For Next Session`에 미결 맥락 기록.
```

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

## Completed Work
### INCEPTION
- [x] workspace-detection — [한 줄 결과]
- [x] requirements-analysis — [한 줄 결과]

### CONSTRUCTION
- [x] unit: [name] — [한 줄 결과]
- [ ] unit: [name] — (진행 중)

## Next Steps
- [다음 작업 설명]
<!-- Key Decisions, Completed Work는 최근 20개까지만 유지. 초과 시 오래된 항목 삭제. -->

## For Next Session
- [인수인계 시 알아야 할 핵심 맥락]
- [주의사항이나 미해결 이슈]
```

### Commit Hash 기록

기록 지점: 세션 시작/재개, Phase 전환, Unit 구현 완료.
수집 방법: `git rev-parse --short HEAD` (git 미사용 환경에서는 `(no git)` 표기).
기록 위치: session-summary.md의 **Commit** 필드 (최신만) + audit 로그의 전환점 항목에 inline.

## 3. Audit 강화

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

## 4. 태스크 재검증 프로토콜

CONSTRUCTION 세션 재개 시 construction-orchestrator가 실행.

### 재검증 실행 주체 규칙

- **construction-orchestrator 경유**: Step 1.5에서 재검증 실행
- **executing-plans 독립 실행**: construction-orchestrator 외부 호출 시에만 자체 재검증
- **중복 방지**: construction-orchestrator 내부 호출 시 재검증 스킵

### 재검증 후 복귀 경로

재검증 실패 → debugging 완료 시:
- construction-orchestrator: debugging Return 수신 → 재검증 재실행
- executing-plans: debugging 완료 → 재검증 재실행 → 통과 시 정상 재개

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
