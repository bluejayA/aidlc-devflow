---
name: aidlc-writing-skills
description: Use when creating a new SKILL.md file, editing an existing skill, validating a skill before deployment, or when any process documentation needs to be defined as an executable skill.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
---

# aidlc-writing-skills

<!-- 스킬 작성: 프로세스 문서화의 TDD -->

## 철의 법칙

> **NO SKILL WITHOUT DEFINING TRIGGER CONDITIONS FIRST**

트리거 조건 없는 스킬은 절대 호출되지 않거나 잘못 호출된다.
스킬을 작성하기 전에 "이 스킬이 언제 발동되어야 하는가"를 먼저 정의한다.

---

## Trigger

다음 상황에서 이 스킬을 실행한다:

- 새로운 SKILL.md 파일을 생성할 때
- 기존 스킬의 내용을 수정할 때
- 스킬을 배포(skills/ 디렉토리에 추가)하기 전 검증할 때
- "이 프로세스를 스킬로 만들어줘"라는 요청을 받았을 때
- 에이전트가 반복적으로 같은 실수를 할 때 (→ 스킬이 부재한 신호)

---

## Purpose

스킬 작성 = 프로세스 문서화의 TDD.

스킬 없이 에이전트가 실패하는 시나리오를 먼저 정의하고,
그 시나리오를 통과시키는 SKILL.md를 작성한다.

---

## TDD 매핑

| TDD 개념 | 스킬 작성에서의 대응 |
|---------|-----------------|
| 테스트케이스 | 압박 시나리오 — 에이전트가 스킬 없이 실패하는 상황 |
| 프로덕션 코드 | SKILL.md |
| RED | 스킬 없이 에이전트가 잘못 행동하는 상태 |
| GREEN | 스킬 있을 때 에이전트가 올바르게 준수하는 상태 |
| REFACTOR | 스킬을 더 명확하게, 더 짧게, 더 잘 호출되도록 개선 |

---

## CSO (Claude Search Optimization) 원칙

Claude는 스킬 목록에서 `description`을 먼저 읽어 어떤 스킬을 호출할지 결정한다.
description이 잘못 작성되면 스킬이 존재해도 호출되지 않는다.

### description 작성 규칙

**절대 금지 — 워크플로우 요약 포함**:
```yaml
# ❌ 잘못된 예 — 에이전트가 description만 읽고 본문을 건너뜀
description: Manages the full debugging lifecycle by investigating root causes,
  analyzing patterns, forming hypotheses, and implementing verified fixes using TDD.
```

**올바른 형식 — "Use when..." 트리거 조건만**:
```yaml
# ✓ 올바른 예 — 에이전트가 정확한 상황에서만 호출
description: Use when a bug is reported, a test is failing, behavior is unexpected,
  or any symptom requires diagnosis before a code change is made.
```

**description 작성 체크리스트**:
- [ ] "Use when..."으로 시작하는가?
- [ ] 호출 조건(트리거)만 담겨 있는가?
- [ ] 워크플로우 단계나 구현 방법 설명이 없는가?
- [ ] 1024자 이하인가?
- [ ] 검색 키워드가 풍부하게 포함되어 있는가? (동의어, 관련 용어)

---

## 스킬 구조 가이드

```
skills/
└── [skill-name]/
    └── SKILL.md
```

### 필수 섹션

```markdown
---
name: [skill-name]          # skills/ 디렉토리명과 일치
description: Use when ...   # CSO 원칙 준수 — 트리거 조건만
metadata:
  version: 0.1.0
  author: [작성자]
  category: [카테고리]
---

# [skill-name]

<!-- 한 줄 주석: 이 스킬이 무엇을 하는가 -->

## 철의 법칙 (선택)
> NO [ACTION] WITHOUT [PREREQUISITE]

## Trigger
[언제 이 스킬이 발동되는가 — 목록 형식]

## Purpose
[이 스킬의 목표 — 2-3문장]

## [메인 프로세스 섹션]
[단계별 지침]

## Examples
[실제 사용 예시 최소 2개]

## Troubleshooting
[흔한 문제 최소 2개]
```

### 선택 섹션

- `## 철의 법칙`: 절대 위반하면 안 되는 원칙 (강력한 프로세스 스킬에 권장)
- `## Red Flags`: 잘못된 행동 패턴 목록
- `## 합리화 방지 테이블`: 스킬을 건너뛰려는 시도 차단

---

## 스킬 작성 프로세스

### 1단계: 압박 시나리오 정의 (RED)

스킬을 작성하기 전에 에이전트가 스킬 없이 실패하는 상황을 나열한다:

```
압박 시나리오 목록:
1. 에이전트가 버그를 수정 요청받고 원인 조사 없이 바로 코드를 수정한다
2. 에이전트가 "아마도 될 것 같다"며 테스트 없이 완료를 선언한다
3. ...
```

이 목록이 스킬의 Trigger 섹션이 된다.

### 2단계: 최소 동작 스킬 작성 (GREEN)

압박 시나리오를 통과시키는 최소한의 스킬을 작성한다:

- 모든 기능을 한 번에 넣으려 하지 않는다
- 핵심 프로세스 하나가 올바르게 동작하는 것이 먼저다
- 예시와 troubleshooting은 나중에 추가해도 된다

### 3단계: 배포 전 검증 체크리스트 실행 (REFACTOR)

아래 체크리스트를 모두 통과해야 배포한다.

---

## 배포 전 검증 체크리스트

### 구조 검증
- [ ] `name`이 디렉토리명과 일치하는가?
- [ ] `description`이 "Use when..."으로 시작하는가?
- [ ] `description`에 워크플로우 요약이 없는가?
- [ ] `metadata.version`, `metadata.author`, `metadata.category`가 있는가?
- [ ] `## Trigger` 섹션이 있는가?
- [ ] `## Examples` 섹션에 예시가 2개 이상 있는가?
- [ ] `## Troubleshooting` 섹션에 항목이 2개 이상 있는가?

### 내용 검증
- [ ] 에이전트가 스킬 없이 이 상황을 어떻게 잘못 처리할지 상상했을 때, 이 스킬이 그것을 방지하는가?
- [ ] 각 단계가 구체적이고 실행 가능한가? ("잘 처리한다" 같은 모호한 지침 없음)
- [ ] 스킬이 standalone으로 동작하는가? (오케스트레이터 없이도)
- [ ] 예시가 실제로 유용한 케이스를 다루는가? (진부한 "hello world" 예시 아님)
- [ ] Troubleshooting이 실제로 발생 가능한 문제를 다루는가?

### CSO 검증
- [ ] description만 읽고 에이전트가 이 스킬이 언제 쓰이는지 정확히 알 수 있는가?
- [ ] description 키워드가 사용자가 사용할 법한 표현을 포함하는가?
- [ ] 1024자 이하인가?

---

## Examples

### Example 1: 신규 스킬 생성 — systematic-debugging

**1단계 압박 시나리오**:
```
- 에이전트가 "TypeError: 'NoneType'..." 에러를 받고 즉시 None 체크 코드를 추가한다
  → 실제 원인은 상위 함수에서 None을 잘못 반환하는 것
- 에이전트가 "이전에 비슷한 버그를 봤다"며 다른 케이스의 수정을 그대로 복사한다
  → 증상만 같고 원인은 전혀 다름
```

**2단계 최소 동작 스킬 핵심**:
```markdown
## 철의 법칙
> NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

## 4단계 프로세스
1단계: 재현 및 스택 트레이스 전체 읽기
2단계: 작동하는 케이스와 차이점 비교
3단계: 단일 가설 → 최소 변경으로 검증
4단계: 실패 테스트 작성 → 수정 → 통과 확인
```

**3단계 배포 전 체크리스트**:
- [x] description: "Use when a bug is reported, a test is failing..."
- [x] 워크플로우 요약 없음
- [x] Examples 2개 포함
- [x] Troubleshooting 2개 포함

---

### Example 2: 기존 스킬 개선

**상황**: `aidlc-code-generation` 스킬이 오케스트레이터 없이 단독 호출될 때 승인 게이트 처리가 모호함

**수정 전 문제**:
```markdown
# 기존 description
description: Generates a code plan and implements it after approval.
  Do NOT invoke directly — use using-devflow instead.
```

**문제 분석**:
- "Do NOT invoke directly"가 description에 있으면 Claude가 standalone 호출을 거부할 수 있음
- standalone 호출 가능하도록 설계해야 함

**수정 후**:
```markdown
description: Use when code implementation is needed for a defined unit or feature.
  Produces a checkbox plan first, then generates code after explicit approval.
  Can be used standalone or called by using-devflow orchestrator.
```

배포 전 체크리스트 재실행 → 통과 확인 후 배포

---

## Troubleshooting

### 스킬이 호출되지 않을 때 (너무 적게 발동)

**증상**: 스킬이 있는데 에이전트가 스킬을 호출하지 않고 직접 처리함

**원인과 해결**:
1. description 확인: "Use when..."으로 시작하는 트리거 조건인가?
   - "Use when a bug occurs..." → 호출됨
   - "Manages debugging process..." → 에이전트가 건너뜀
2. 트리거 키워드 보강: 사용자가 쓸 법한 다양한 표현 추가
   - "bug", "error", "failing", "broken", "not working", "unexpected behavior"
3. Trigger 섹션에 구체적인 상황 나열 추가

---

### 스킬이 너무 자주 호출될 때 (잘못 발동)

**증상**: 관련 없는 상황에서 스킬이 호출됨

**원인과 해결**:
1. description이 너무 넓게 작성된 경우:
   - 나쁜 예: "Use when working with code" — 범위 무한정
   - 좋은 예: "Use when a test is failing and root cause is unknown"
2. 상호 배타적인 조건 추가:
   - "Use when X, but NOT when Y (use [다른 스킬] instead)"
3. 구체적인 컨텍스트 조건 추가:
   - "Use when the error message is already visible in the terminal"
