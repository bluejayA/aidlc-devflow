# Persuasion Principles

<!-- 규율 강제 스킬의 언어 설계 원칙. writing-skills가 참조한다. -->

## 왜 필요한가

에이전트는 규칙을 "이해"하지만 압력 하에서 합리화하여 건너뛴다.

"테스트를 먼저 작성하라"를 이해하는 것과, 실제로 시간 압박 속에서 테스트를 먼저 작성하는 것은 다른 문제다. 설득 원칙은 이 간극을 메운다.

**연구 근거**: Meincke et al. (2025)는 N=28,000 AI 대화에서 7가지 설득 원칙을 테스트했다. 설득 기법 적용 시 준수율이 33%에서 72%로 2배 이상 증가했다 (p < .001).

aidlc에서는 이 중 규율 강제에 가장 효과적인 **3가지 원칙**을 핵심으로 사용한다.

---

## 핵심 원칙 3가지

### 1. Authority (권위)

**정의**: 전문성, 공식 규범, 명령적 어조에 대한 순응.

**작동 방식**:
- "YOU MUST", "Never", "Always" 같은 명령형 언어
- "No exceptions" 같은 비협상적 프레이밍
- 결정 피로를 제거하고 합리화 여지를 차단

**약한 표현 vs 강한 표현**:

| 약한 표현 (효과 낮음) | 강한 표현 (Authority 적용) |
|---------------------|--------------------------|
| 테스트를 먼저 작성하는 것을 고려하세요 | 실패하는 테스트 없이 프로덕션 코드 작성 금지 |
| 가능하면 원인을 먼저 파악해보세요 | **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST** |
| 코드 리뷰를 받으면 좋습니다 | 리뷰 없이 머지 금지. 예외 없음. |
| 설계를 한번 생각해보세요 | 승인된 설계 없이 코드 작성 불가 |

**aidlc 실제 사례**:
- `tdd-protocol.md` Iron Law: "**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**"
- `aidlc-systematic-debugging` Iron Law: "**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST**"
- `aidlc-test-driven-development`: "Skill Type: **Rigid** — 정확히 따를 것. 상황에 맞게 적응하지 않는다."

**주의: 효과 희석**

모든 곳에 Authority를 쓰면 효과가 희석된다. 저자유도(규율형) 스킬에만 사용한다.

- Iron Law는 **스킬당 최대 1개**
- "YOU MUST"가 10개이면 0개와 같다 — 진짜 중요한 것에만 집중
- 가이드/기법형 스킬에서는 중간 수준의 Authority로 충분

---

### 2. Commitment (일관성)

**정의**: 사전 선언이나 공개 약속과 이후 행동의 일관성.

**작동 방식**:
- 공개 선언을 강제하면 이후 행동이 선언과 일관되게 유지된다
- 체크리스트와 게이트로 중간 검증 포인트를 만든다
- "이미 약속했으므로 따라야 한다"는 내적 압력을 생성

**aidlc 적용 패턴**:

| 패턴 | 설명 | 예시 |
|------|------|------|
| 스킬 사용 선언 | 스킬 시작 시 명시적으로 선언 | "aidlc-test-driven-development 스킬을 사용합니다. TDD Iron Law를 적용합니다." |
| TaskCreate 체크리스트 | 할 일을 공개적으로 나열 | 계획의 각 태스크를 TaskCreate로 등록 → 하나씩 완료 처리 |
| 설계 승인 게이트 | 코드 작성 전 설계를 승인 받음 | "승인된 설계 없이 코드 작성 불가" → 승인 = 공개 약속 |
| Self-Review 체크리스트 | 리뷰 전 자가 점검 | tdd-protocol.md Self-Review 체크리스트 → 각 항목에 체크 = 약속 |

**aidlc 실제 사례**:
- `aidlc-test-driven-development`: **시작 시 선언** — "aidlc-test-driven-development 스킬을 사용합니다."
- `tdd-protocol.md`: **Self-Review 체크리스트** — 리뷰어에게 넘기기 전 공개 점검
- 오케스트레이터 Gate 패턴: 승인 게이트 = Commitment의 구조화된 형태

---

### 3. Social Proof (사회적 증명)

**정의**: "모두가 이렇게 한다"는 규범에 따르려는 경향.

**작동 방식**:
- "Every time", "항상" 같은 보편적 표현으로 규범을 확립
- "X 없이 Y = 실패" 패턴으로 위반의 결과를 보편적 사실로 제시
- 실패 사례를 문서화하여 "이것이 실제로 일어나는 일"을 보여줌

**aidlc 실제 사례**:

`tdd-protocol.md` 합리화 방지 테이블:
```
| "너무 단순해서 테스트 불필요" | 단순한 코드가 가장 자주 깨짐 |
| "나중에 테스트 추가"         | 나중은 오지 않음            |
| "프로토타입이라 괜찮다"      | 프로토타입은 프로덕션이 됨   |
```
→ 우측 "현실" 칸이 Social Proof다. "항상 그렇다", "매번 그렇다"는 보편적 사실로 프레이밍.

`tdd-protocol.md` Red Flags:
```
- "이번만 예외"라고 합리화함
- "나중에 테스트 추가"하려 함
```
→ "이런 행동을 하면 실패한다"는 보편적 패턴으로 문서화.

---

## 합리화 방지 테이블 작성법

합리화 방지 테이블은 Authority + Social Proof의 조합이다. 에이전트가 규칙을 건너뛰려 할 때 사용하는 변명을 미리 차단한다.

### 구조

```markdown
| 합리화 | 현실 |
|--------|------|
| 에이전트가 말할 법한 변명 | 짧고 단정적인 반박 |
```

### 좌측 (합리화) 수집법

1. **실제 관찰**: 에이전트가 실제로 규칙을 우회한 사례를 수집
2. **압박 시나리오**: 시간 부족, 복잡도 높음, 코드가 이미 작성됨 등의 상황에서 나올 변명
3. **"너무~" 패턴**: "너무 단순해서", "너무 급해서", "너무 복잡해서" — "너무"로 시작하는 합리화는 거의 항상 위반 신호

### 우측 (현실) 작성 원칙

| 원칙 | 설명 | 예시 |
|------|------|------|
| 짧게 | 1문장, 최대 15자 이내 권장 | "나중은 오지 않음" |
| 단정적으로 | "~할 수 있다"가 아니라 "~이다" | "프로토타입은 프로덕션이 됨" |
| 결과 기반으로 | 이유가 아니라 결과를 말한다 | "더 많은 시간 소모" |
| Social Proof 활용 | "항상", "매번", "가장" 등 보편성 표현 | "단순한 코드가 가장 자주 깨짐" |

### TDD 스킬 예시 (실제 tdd-protocol.md에서)

```markdown
| 합리화 | 현실 |
|--------|------|
| "너무 단순해서 테스트 불필요" | 단순한 코드가 가장 자주 깨짐 |
| "나중에 테스트 추가" | 나중은 오지 않음 |
| "리팩토링이라 테스트 불필요" | 리팩토링이야말로 테스트 필수 |
| "시간이 없다" | 테스트 없는 코드가 더 많은 시간 소모 |
| "프로토타입이라 괜찮다" | 프로토타입은 프로덕션이 됨 |
```

### systematic-debugging 예시 (실제 SKILL.md에서)

```markdown
| 합리화 패턴 | 올바른 행동 |
|------------|------------|
| "빠르게 고치면 될 것 같아" | 1단계 Root Cause 조사부터 |
| "이전에 비슷한 버그 봤어" | 현재 케이스를 독립적으로 재현 |
| "에러 메시지가 명확해" | 상위 호출 스택까지 추적 |
| "테스트만 고치면 되겠다" | 테스트가 틀린 이유를 먼저 증명 |
| "시도해보고 안 되면 다른 거" | 단일 가설 → 단일 수정 → 검증 |
```

→ debugging 테이블은 우측을 "올바른 행동"으로 변형했다. 이것도 유효한 패턴이다: 반박 대신 **대안 행동**을 제시.

---

## HARD-GATE / Iron Law의 효과 원리

### Iron Law — Authority 극대화

```markdown
> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**
```

Iron Law는 Authority 원칙의 극대화된 형태다:
- **대문자 + 볼드**: 시각적 권위
- **NO X WITHOUT Y**: 절대적 금지 구문 — 예외의 여지가 없음
- **스킬당 최대 1개**: 희소성이 권위를 강화
- **위반 시 결과 명시**: "해당 코드 삭제 후 RED부터 재시작" — 결과가 구체적이고 즉각적

Iron Law 작성 공식:
```
> **NO [금지 행위] WITHOUT [필수 전제조건] FIRST**
위반 시: [구체적이고 즉각적인 결과]
```

### HARD-GATE — Commitment 활용

HARD-GATE는 진행 자체를 차단하여 Commitment을 강제한다:
- 승인 게이트: "설계 승인 없이 코드 작성 불가" → 승인 = 공개적 약속
- Self-Review 게이트: 체크리스트 완료 없이 리뷰 요청 불가
- 조건부 게이트: 특정 조건 충족 없이 다음 단계 진행 불가

Authority(Iron Law)가 "하지 마라"를 말한다면, HARD-GATE(Commitment)는 "할 수 없다"를 만든다.

---

## 스킬 유형별 적용 가이드

| 스킬 유형 | 원칙 조합 | 예시 |
|-----------|-----------|------|
| 규율 강제 (Rigid) | Authority + Commitment + Social Proof | `aidlc-test-driven-development`, `aidlc-systematic-debugging` |
| 가이드/기법 (Guided) | 중간 Authority + Unity | `aidlc-writing-plans`, `aidlc-brainstorming` |
| 참고 자료 (Reference) | 설득 원칙 불필요. 명확성만. | `_shared/tdd-protocol.md`, `_shared/gate-patterns.md` |

**규율 강제 스킬** 체크리스트:
- [ ] Iron Law 1개 있는가
- [ ] 시작 시 선언문이 있는가 (Commitment)
- [ ] 합리화 방지 테이블이 있는가 (Social Proof)
- [ ] Red Flags 목록이 있는가

**가이드/기법 스킬**은 Authority를 낮추되, 핵심 규칙 1~2개에만 강한 표현을 사용한다.

**참고 자료**는 설득이 아니라 정보 전달이 목적이다. 설득 원칙을 섞으면 오히려 신뢰도가 떨어진다.

---

## 연구 출처

- **Cialdini, R. B. (2021).** *Influence: The Psychology of Persuasion (New and Expanded).* Harper Business.
- **Meincke, L. et al. (2025).** *Call Me A Jerk: Persuading AI to Comply with Objectionable Requests.* University of Pennsylvania. N=28,000 LLM 대화, 준수율 33%→72%.
