# Session Resume Protocol — auto-mode

auto-mode `## Session Resume` 섹션의 보조 명세. baseline은 `_shared/patterns/session-continuity.md` (Handoff = Hypothesis Phase 1 사용자 가이드, BL-095). 본 문서는 auto-mode 특수 처리만 정의한다.

## Drift 감지 (Step 3)

devflow-state.md는 advisory cache이므로 stale 가능성 있음. 다음을 비교하여 drift를 감지한다:

- **산출물 디렉토리**: `devflow-docs/inception/`, `devflow-docs/construction/`의 실제 파일 ↔ state.md `## Approved Stages` / `## Completed Units`
- **git log**: `git log --oneline -20`의 commit message 키워드(예: `feat: requirements-analysis`, `feat(unit): X 완료`) ↔ state.md 상태

### 게이트 (불일치 시)

```
⚠️ devflow-state.md drift 감지

state.md 기록: [요약]
산출물/git log: [요약]

A) 산출물 우선 신뢰 (state.md 갱신 후 재개)
B) state.md 우선 신뢰 (산출물은 검증용으로만 참조)
C) 단계별 모드로 전환 (수동 정리)
```

### Audit Emit

Resume 진입 시 `auto-mode-invoked | mode=resume | intent=<short>` emit. drift 발견 시 (게이트 결과 무관) `auto-mode-resume-drift-detected | gap=<short>` 즉시 추가 emit. emit은 Read → Edit append 절차 (Write 전체 재작성 금지).

## Handoff Verification (Step 4)

session-summary.md를 fact가 아닌 hypothesis로 다룬다. 새 세션이 로드 직후 다음 3단계를 실행한다.

### 4a. Completed Work 검증

`## Completed Work`의 각 `[x]` 항목에 대해:
- 산출물 디렉토리 확인:
  - INCEPTION 항목 → `devflow-docs/inception/<artifact>.md` 존재
  - CONSTRUCTION unit 항목 → `devflow-docs/construction/<unit>/code-plan.md` 또는 코드 산출물 존재
- `git log --oneline -20`에서 stage/unit 키워드 commit 확인
- 불일치 발견 시 사용자 보고:

```
⚠️ session-summary 검증 실패

기록: [x] [stage/unit name] — [한 줄 결과]
실제: [산출물 미존재 | git log 흔적 없음 | ...]

A) 산출물 우선 — summary 갱신 후 재개
B) summary 우선 — 산출물 재생성 후 재개
C) 단계별 모드 전환 (수동 정리)
```

### 4b. Open Work 재해석

명령형 표현 자동 변환 (auto-mode 자동 진행 모드라 사용자 확인 게이트 없이 진행):

| 명령형 (위반) | 상태 서술형 (정합) |
|---|---|
| "X를 구현하라" | "X는 미구현" |
| "Y를 수정하라" | "Y는 수정 필요 상태" |
| "Z를 호출하라" | "Z 호출 미완" |

변환 결과를 session-summary.md에 갱신하고 decision-log에 `"open-work-rephrased: <원문> → <변환>"` 기록.

### 4c. Traps 존중

`## Traps to Avoid` 항목과 다음 자동 결정의 잠재적 충돌 검사. 다음 중 하나라도 해당하면 미니 게이트:
- Trap 항목의 키워드(예: "JWT cookie", "websocket polling")가 자동 결정 후보에 포함
- Trap 항목과 동일한 외부 라이브러리/패턴 재선택

```
⚠️ Traps to Avoid 충돌 가능성

이전에 폐기한 접근: [Trap 항목 1줄]
현재 자동 결정: [결정 내용 1줄]

A) Trap 존중 — 다른 접근으로 자동 재선택
B) 사용자 명시 승인 후 재시도 (Trap 항목에 "재시도 승인 [date]" 코멘트 추가)
C) 단계별 모드 전환
```

키워드 매칭 false positive 가능성 — 사용자 게이트가 최종 안전망 역할.

## Audit Emit

Step 4 완료 시 `devflow-docs/audit.md`에 한 줄 append:

```
[<ISO timestamp>] auto-mode-resume-handoff-verified | completed_work_match=<true|false> | traps_count=<N> | rephrased_count=<N>
```

drift 감지(Step 3, SKILL.md 본체 참조)와 별개의 emit. drift는 state.md 정합, handoff verification은 session-summary 정합.

## 실패 처리

- 4a 사용자 게이트에서 C 선택 → using-devflow로 전환 (devflow-state는 그대로 유지)
- 4c 사용자 게이트에서 C 선택 → 동일
- 4b는 사용자 게이트 없음 (자동 변환만)
- 모든 단계 PASS → Session Resume Step 5로 진행
