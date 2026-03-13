# Superpowers 독립 + 기능 포팅 설계

**Complexity:** Comprehensive

**작성일**: 2026-03-13
**목표**: aidlc-like 플러그인의 superpowers 런타임 의존도를 0으로 만들고, devflow에만 있는 기능을 aidlc-like 구조적 장점(conventions SSOT, 토큰 효율, 오케스트레이터 중심)을 유지하며 포팅한다.

**접근 방식**: A안 (Aggressive SSOT) — devflow 대비 40-60% 크기로 축약. 공통 패턴은 최대한 conventions/shared로 추출하고, 스킬은 참조만.

---

## 1. Shared 기반 확장

### 1-1. `_shared/devflow-conventions.md` 확장 (135줄 → ~170줄)

기존 conventions에 아래 3개 규약 추가:

**Brainstorming HARD-GATE**:
- 새 기능/컴포넌트/동작 수정 시 설계 문서 작성 + 승인 전까지 코드 작성 금지
- "단순해서 설계 불필요" 합리화 차단

**TDD Iron Law**:
- 실패하는 테스트 없이 프로덕션 코드 작성 금지
- conventions에 1줄 원칙, 상세는 tdd-protocol.md 참조

**Subagent Dispatch Rules**:
- 독립적 태스크 2개 이상일 때만 서브에이전트 디스패치
- 구현 서브에이전트 병렬 실행 금지 (충돌 방지)
- Two-stage review 필수 (spec compliance → code quality)

### 1-2. `_shared/tdd-protocol.md` 확장 (132줄 → ~180줄)

기존 TDD 프로토콜에 devflow에서 가져온 내용 흡수:

**합리화 방지 테이블** (devflow 원천):

| 합리화 | 현실 |
|--------|------|
| "너무 단순해서 테스트 불필요" | 단순한 코드가 가장 자주 깨짐 |
| "나중에 테스트 추가" | 나중은 오지 않음 |
| "리팩토링이라 테스트 불필요" | 리팩토링이야말로 테스트 필수 |
| "시간이 없다" | 테스트 없는 코드가 더 많은 시간 소모 |
| "프로토타입이라 괜찮다" | 프로토타입은 프로덕션이 됨 |

**Red Flags 체크리스트**:
- 테스트 전에 구현 코드 작성 시도
- "이건 테스트하기 어렵다"는 설계 문제 신호
- GREEN에서 바로 다음 기능으로 이동 (REFACTOR 스킵)
- 테스트가 구현 세부사항에 의존

### 1-3. 신규 shared pattern 파일 3개

**`_shared/patterns/three-mode-selection.md` (~30줄)**:
- Together / Import / Skip 모드 정의
- 각 모드의 트리거 조건과 동작
- 오케스트레이터가 모드를 선택하고, stage skill은 선택된 모드만 실행

**`_shared/patterns/hold-mechanism.md` (~25줄)**:
- Mid-step Hold 시그널 정의 (사용자가 "잠깐" 또는 질문 시)
- Hold 상태에서 devflow-state 업데이트 규약
- Resume 시 복귀 절차 (audit 로깅 포함)

**`_shared/patterns/brownfield-exploration.md` (~35줄)**:
- 기존 코드베이스 탐색 프로토콜
- 탐색 순서: README → 프로젝트 구조 → 최근 커밋 → 핵심 파일
- 기존 패턴 존중 원칙 (새 패턴 도입 전 기존 방식 확인)
- brainstorming, workspace-detection에서 참조

---

## 2. 계층 1 — 신규 스킬 5개

### 2-1. `aidlc-brainstorming` (~200줄, devflow 472줄 대비 42%)

아이디어를 설계로 전환하는 협업 대화 스킬.

- **invoke_mode**: `user-invocable`
- **설계 문서 저장**: `docs/plans/YYYY-MM-DD-<topic>-design.md`

**핵심 6단계 프로세스**:
1. Explore project context — 파일, 문서, 최근 커밋 확인
2. Ask clarifying questions — 한 번에 하나씩, 객관식 선호
3. Declare complexity + Propose approaches — Adaptive Depth 선언 후 2-3개 접근법
4. Present design — 섹션별 제시, 각 섹션 승인 후 다음
5. Write design doc — `docs/plans/`에 저장 + 커밋
6. Spec review loop + Transition — conventions Review Workflow 참조 후 writing-plans 호출

**Ambiguity Resolution Loop** (유지):
- 모호성 신호 탐지 → 즉시 후속 질문
- 선택/범위/우선순위 모호성 유형별 후속 질문 방향
- 탈출 조건: 모호함 해소 또는 사용자 명시적 진행 요청 시 가정 처리

**Adaptive Depth** (유지):
- Minimal / Standard / Comprehensive 3단계
- 접근법 제안 전 복잡도 선언 + 사용자 확인
- 설계 문서에 Complexity 필드 기록

**축약 포인트**:
- HARD-GATE → conventions 참조 (1줄)
- Spec Review Loop → conventions Review Workflow 참조
- Visual Companion 섹션 삭제
- Brownfield Exploration → `_shared/patterns/brownfield-exploration.md` 참조

### 2-2. `aidlc-test-driven-development` (~250줄, devflow 613줄 대비 41%)

TDD 원칙을 강제하는 Rigid 타입 스킬.

- **invoke_mode**: `user-invocable`
- **Skill Type**: Rigid (정확히 따를 것, 적응 금지)

**구조**:
- Iron Law → conventions 참조 + 스킬 상단 1줄 인용
- RED-GREEN-REFACTOR 사이클 → `_shared/tdd-protocol.md` 확장본 참조
- 합리화 방지 테이블 → `_shared/tdd-protocol.md`에 흡수, 스킬은 참조만
- Red Flags 체크리스트 → 동일하게 참조
- When to Use / Exceptions 섹션 유지
- 예시 1개만 유지 (가장 범용적인 것)

### 2-3. `aidlc-subagent-driven-development` (~180줄, devflow 352줄 대비 51%)

구현 계획을 서브에이전트로 실행하는 스킬.

- **invoke_mode**: `user-invocable`

**핵심 프로세스**:
- Fresh subagent per task + two-stage review (spec → quality)
- Model Selection: mechanical → haiku, integration → sonnet, architecture → opus
- Implementer Status 4종: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED

**서브에이전트 프롬프트** (`_shared/reviewers/`에 추가):
- `implementer-prompt.md` (~40줄) — 태스크 구현 서브에이전트용
- `spec-reviewer-prompt.md` (~40줄) — spec compliance 검증용 (설계 문서 대비 구현 일치 여부)
- `code-quality-reviewer-prompt.md` (~40줄) — 코드 품질 검증용 (기존 `code-reviewer-prompt.md`는 일반 코드 리뷰용, 이 프롬프트는 subagent 워크플로우 전용 품질 게이트)

**축약 포인트**:
- Red Flags / Advantages → 핵심만
- 워크플로우 예시 → devflow의 1/3로 축약

### 2-4. `aidlc-executing-plans` (~120줄, devflow 183줄 대비 66%)

구현 계획을 별도 세션에서 배치 실행하는 스킬.

- **invoke_mode**: `user-invocable`

**5단계 프로세스**:
1. Load — 계획 파일 로드, 체크박스 파싱
2. Execute batch — 배치 단위 실행
3. Report — 배치 완료 후 진행 상황 보고
4. Continue — 다음 배치 또는 리뷰 체크포인트
5. Complete — 전체 완료 후 finishing-a-development-branch 호출

**세션 재개**: 체크박스 파싱 + devflow-audit 교차 확인
**Mid-Execution 변경 5종**: skip / restart / insert / edit / pause

### 2-5. `aidlc-writing-plans` (~180줄, devflow 281줄 대비 64%)

설계 문서를 상세 구현 계획으로 변환하는 스킬. 기존 `aidlc-workflow-planning`(INCEPTION 단계의 실행 계획 수립)과는 역할이 다르다:
- `aidlc-workflow-planning` — INCEPTION 단계에서 **어떤 stage를 어떤 깊이로 실행할지** 결정 (orchestrator-only)
- `aidlc-writing-plans` — 승인된 설계 문서를 **태스크별 구현 계획**으로 변환 (user-invocable)

- **invoke_mode**: `user-invocable`
- **계획 저장**: `docs/plans/YYYY-MM-DD-<feature-name>-plan.md`

**Complexity-Based Detail**:

| Complexity | 태스크 수 | 코드 포함 | Architecture 섹션 |
|------------|-----------|-----------|-------------------|
| Minimal | 1-3개 | 핵심 변경만 | 1문장 |
| Standard | 3-7개 | 주요 코드 | 2-3문장 |
| Comprehensive | 7개+ | 전체 코드 | 전체 섹션 |

**필수 구조**:
- Plan Document Header (Goal, Complexity, Architecture, Tech Stack)
- Task Structure 템플릿 (TDD 사이클 체크박스)
- Plan Review Loop → conventions Review Workflow 참조

**Execution Handoff**:
- 서브에이전트 가능 → `aidlc-subagent-driven-development`
- 별도 세션 → `aidlc-executing-plans`

---

## 3. 계층 2 — functional-design + shared patterns

### 3-1. `aidlc-functional-design` (~150줄, devflow 225줄 대비 67%)

CONSTRUCTION 단계에서 code-generation 전에 상세 기능 설계를 수행하는 stage skill.

- **invoke_mode**: `orchestrator-only`
- **return_behavior**: `stop-no-gate`
- **산출물**: `devflow-docs/construction/{unit}/functional-design.md`
- **조건부 실행**: Comprehensive 깊이일 때만

**핵심 3단계**:
1. **인터페이스 설계** — 공개 API, 타입 시그니처, 의존성 주입 포인트
2. **데이터 흐름 설계** — 입력→변환→출력 경로, 에러 전파 경로
3. **테스트 전략 설계** — 단위/통합 테스트 경계, 모킹 전략 (tdd-protocol.md 참조)

### 3-2. Stage Routing Table 업데이트

`skills/aidlc-using-devflow/SKILL.md`의 CONSTRUCTION Stage Routing Table에 functional-design 분기 추가:

```
application-design → [Comprehensive?] → functional-design → code-generation
                     [Minimal/Standard?] → code-generation (skip)
```

---

## 4. 계층 3 — superpowers-tracking

### 4-1. `aidlc-superpowers-tracking` (~60줄, devflow 76줄 대비 79%)

세션 중 스킬/패턴 사용을 추적하여 워크플로우 개선 인사이트 제공.

- **invoke_mode**: `user-invocable`
- **산출물**: `devflow-docs/tracking/session-{date}.md`

**핵심 기능**:
1. **세션 요약** — 호출된 스킬 목록, 각 단계 소요 시간, 성공/실패/스킵 상태
2. **패턴 분석** — 자주 스킵되는 단계, 반복 실패 단계 식별 → 워크플로우 튜닝 제안

추적 데이터는 devflow-audit.md를 파싱하여 생성 (중복 저장 안 함).

---

## 5. 기존 스킬 수정 — superpowers 참조 검증 및 잔여 교체

> **참고**: 이전 리팩토링(commit `a3273e2`)에서 대부분의 `superpowers:` 참조가 `aidlc-` prefix로 이미 교체됨. 이 단계는 잔여 참조 검증 + 신규 스킬 추가에 따른 참조 업데이트.

**검증 단계**:
1. `grep -r "superpowers" skills/ _shared/` 실행하여 잔여 참조 확인
2. 잔여 참조가 있으면 `aidlc-` prefix로 교체
3. 신규 스킬(brainstorming, TDD, subagent 등) 추가 후 오케스트레이터에서 해당 스킬 참조 추가
4. `plugin.json`에 superpowers 관련 필드가 없는지 확인 (현재 clean 상태)

**최종 검증**: `grep -r "superpowers:" skills/ _shared/` 결과 **0건**

---

## 6. 변경 후 프로필

| 지표 | 현재 | 변경 후 |
|------|------|---------|
| 스킬 수 | 19개 | 26개 (+7) |
| 총 풋프린트 | ~4,348줄 | ~5,661줄 |
| superpowers 런타임 의존 | 5개 스킬 위임 | **0** |
| devflow 대비 풋프린트 | 38% | 50% |
| 최대 스킬 크기 | 330줄 | ~250줄 |

---

## 7. 성공 기준

1. `grep -r "superpowers:" skills/ _shared/` 결과 **0건**
2. 모든 신규 스킬이 conventions SSOT 패턴 준수 (인라인 중복 없음)
3. 포팅된 7개 스킬의 devflow 대비 평균 크기 **60% 이하** 유지 (현재 추정 평균: ~55%)
4. 기존 19개 스킬의 동작 변경 없음 (이름 교체만)

---

## 구현 순서

의존 관계에 따른 구현 순서:

1. **Section 1: Shared 기반 확장** — conventions.md, tdd-protocol.md, 신규 pattern 파일 3개. 모든 신규 스킬이 참조하므로 먼저 완성.
2. **Section 2: 계층 1 스킬 5개** — shared 파일에 의존. brainstorming → writing-plans → executing-plans/subagent-driven-dev → TDD 순서 권장 (brainstorming이 writing-plans를 호출, writing-plans가 executing/subagent를 호출).
3. **Section 3: 계층 2** — functional-design 스킬 + 오케스트레이터 routing table 업데이트. Section 2와 독립적이므로 병렬 가능.
4. **Section 4: 계층 3** — superpowers-tracking. 완전 독립, 언제든 가능.
5. **Section 5: 검증** — 전체 완료 후 잔여 superpowers 참조 검증.

---

## Future Improvements

| 항목 | 우선순위 | 근거 |
|------|---------|------|
| `dev-progress` (진행률 대시보드) | P3 | devflow-state + audit로 대체 가능 |
| `dev-improve` (코드 개선 제안) | P3 | code-review 스킬과 기능 중복 |
| `dev-explain` (코드 설명) | P3 | Claude 기본 능력으로 충분 |
| Visual Companion (brainstorming 시각화) | P2 | 브라우저 기반 목업, 현재 텍스트로 충분 |

## Assumptions

- devflow의 brainstorming/TDD/subagent 스킬은 superpowers 원천을 참고하여 작성됨 — 포팅 시 devflow 버전을 1차 참고하되, superpowers 최신 버전과 교차 확인
- aidlc-like의 conventions SSOT 패턴이 신규 스킬에도 동일하게 적용 가능함
- Visual Companion는 현 단계에서 불필요하며 향후 별도 설계로 추가 가능
