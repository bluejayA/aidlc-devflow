---
type: pattern
applies_to: [aidlc-auto-mode, aidlc-inception-orchestrator, aidlc-construction-orchestrator]
status: active
source: manual
last_validated: 2026-04-13
---

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

### 작성 규칙

session-summary.md는 다음 6개 규칙을 따른다. 위반하면 다음 세션이 맥락을 잘못 복원하거나, 검증 없이 명령을 맹목 실행해 부작용을 일으킨다.

#### 1. Open Work는 상태 서술형, 명령형 금지

- 좋은 예: `RefreshTokenService is not yet implemented; rotation 로직 누락`
- 나쁜 예: `RefreshTokenService를 다음에 구현할 것`

명령형은 새 세션이 맥락 검증 없이 그대로 실행하게 만든다. 상태 서술형은 현재 사실만 기술하므로 다음 세션이 검증 후 행동을 선택한다.

#### 2. 파일 참조는 라인 번호까지

- 좋은 예: `src/auth/TokenService.kt:L45-L72 — refresh 로직, race 의심`
- 나쁜 예: `src/auth/TokenService.kt — refresh 로직 확인 필요`

라인 범위가 없으면 다음 세션이 전체 파일을 읽어야 한다 (토큰 낭비 + 맥락 희석).

#### 3. "Traps to Avoid" 섹션 명시

폐기한 접근을 1줄씩 회수해 다음 세션이 같은 함정을 다시 밟지 않도록 한다.

```markdown
## Traps to Avoid
- [폐기한 접근 1]: [이유]로 폐기. 재시도 금지.
- [폐기한 접근 2]: ...
```

비어 있으면 `(없음)` 명시. **운영 규칙**(어느 시점에 누가 회수하는가, orchestrator stage-end 절차) **및 표준 템플릿 통합은 BL-094 참조**.

#### 4. 검증 지시 포함

session-summary.md를 읽는 다음 세션 prompt 마지막에 항상 다음 한 줄을 포함한다:

> "이 문서의 주장을 코드/git 상태와 대조해 검증한 후 작업을 시작하라."

handoff는 fact가 아니라 hypothesis다 (BL-095). 이전 세션이 혼동 상태에서 작성했다면 새 세션이 그 오류를 그대로 이어받는다. **시스템 강제**(orchestrator 재개 시 verification gate)는 **BL-095b 참조**.

#### 5. CLAUDE.md 중복 회피

handoff 텍스트 첫 줄 또는 prompt에 다음 지시를 포함한다:

> "Read CLAUDE.md first. Do NOT restate its contents in this summary."

CLAUDE.md에 이미 있는 컨벤션을 session-summary가 다시 적으면 매 세션 동일 컨텍스트를 다시 빌드해 토큰 낭비. session-summary는 **CLAUDE.md에 없는 세션 고유 정보**만 담는다.

#### 6. 2K 토큰 상한

session-summary.md는 registry 수준 (~2,000 토큰 이내, 약 80~100줄)만 유지. 상세는 별도 산출물로 분리한다:

| 상세 종류 | 분리 위치 |
|----------|----------|
| 결정 이유, 토론 맥락 | `devflow-audit.md` 또는 ADR |
| 코드 발췌 | 원본 파일 라인 참조 (규칙 #2) |
| 설계 다이어그램, 산출물 | `devflow-docs/inception/`, `devflow-docs/construction/...` |

상한 초과 시 시간이 갈수록 비대화되어 매 세션 로딩 비용이 누적된다. **Commit Hash 기록**(아래)도 최신 1개만 유지하는 이유와 같다.

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
- construction-orchestrator: debugging Return 수신 → 재검증 재실행 (최대 2회, 초과 시 에스컬레이션)
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
