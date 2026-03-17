# writing-skills 보조 자료 내재화 구현 계획

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** aidlc-writing-skills를 superpowers 독립 완전체로 강화 — 보조 자료 4개 + 리뷰어 1개 신규 생성, SKILL.md 및 conventions 수정

**Architecture:** `_shared/patterns/`에 스킬 작성 원칙·설득 원칙·테스트 가이드·패턴 카탈로그 4개 문서 배치. `_shared/reviewers/`에 skill-reviewer 배치. writing-skills SKILL.md가 이들을 참조. 3차에 걸쳐 점진 통합.

**Spec:** `docs/plans/2026-03-17-writing-skills-reinforcement-design.md`
**이슈:** #16

**참조 원본 (읽고 aidlc 맥락으로 재작성 — 복사 아닌 적응):**
- superpowers `anthropic-best-practices.md` → Task 1
- superpowers `persuasion-principles.md` → Task 2
- superpowers `testing-skills-with-subagents.md` → Task 3
- superpowers `examples/` → Task 4

---

## 1차: 기반 문서 3개

### Task 1: `_shared/patterns/skill-best-practices.md` 신규 생성

**Files:**
- Create: `skills/_shared/patterns/skill-best-practices.md`
- Reference (read-only): superpowers `skills/writing-skills/anthropic-best-practices.md`

**superpowers 원본 읽기 지침:**
- 경로: `~/.claude/plugins/cache/superpowers-marketplace/superpowers/5.0.4/skills/writing-skills/anthropic-best-practices.md`
- 전체를 읽고 핵심 개념을 추출한 뒤, aidlc 아키텍처(3단 위임 체인, orchestrator-centric)에 맞게 재작성
- superpowers 고유 용어(`superpowers:`, `EnterPlanMode` 등)는 aidlc 용어로 치환

- [ ] **Step 1: superpowers 원본 읽기 + 핵심 개념 추출**

superpowers `anthropic-best-practices.md`를 읽고 다음을 추출:
- 자유도(Degrees of Freedom) 개념과 3단계 분류
- 점진적 공개(Progressive Disclosure) 패턴
- 500줄 가이드라인과 분리 기준
- 평가 시나리오 작성 원칙
- CSO(Claude Search Optimization) 심화 내용

aidlc에 적응 불필요한 부분 식별 (superpowers 전용 기능, 외부 도구 참조 등)

- [ ] **Step 2: 문서 작성 — 자유도 설계 섹션**

```markdown
# Skill Best Practices

<!-- 스킬 SKILL.md 작성의 실전 원칙. writing-skills가 참조한다. -->

## 자유도(Degrees of Freedom) 설계

스킬이 에이전트에게 주는 재량 범위를 의도적으로 설계한다.

| 수준 | 특성 | aidlc 예시 | 작성 원칙 |
|------|------|-----------|----------|
| **고자유도** (가이드형) | 원칙만 제시, 판단은 에이전트 | `aidlc-brainstorming`, `aidlc-code-generation` | "~해야 한다" 위주, 구체적 단계 최소화 |
| **중자유도** (템플릿형) | 구조는 고정, 내용은 유동 | `aidlc-requirements-analysis` | 섹션 순서 고정 + 각 섹션 내 유연성 |
| **저자유도** (규율형) | 단계 순서 강제, 예외 불허 | `aidlc-test-driven-development`, `aidlc-systematic-debugging` | Iron Law + 합리화 방지 테이블 필수 |

### 자유도 결정 기준

- **규율이 핵심인 프로세스** (TDD, 디버깅) → 저자유도. 위반 시 삭제/재시작.
- **구조화된 산출물** (요구사항, 스토리) → 중자유도. 템플릿 제공.
- **창의적/탐색적 작업** (브레인스토밍, 코드 리뷰) → 고자유도. 원칙만.
```

나머지 섹션(점진적 공개, 500줄, CSO 심화, 평가 시나리오)도 이 패턴으로 작성.

- [ ] **Step 3: 문서 작성 — 점진적 공개 + 500줄 가이드라인 섹션**

```markdown
## 점진적 공개 (Progressive Disclosure)

SKILL.md는 목차이자 라우터다. 모든 것을 한 파일에 넣지 않는다.

**원칙:**
- SKILL.md: 트리거, 프로세스 흐름, 핵심 규칙만
- 상세 원칙/가이드: `_shared/patterns/` 또는 `_shared/reviewers/`로 위임
- 에이전트가 필요할 때만 참조 문서를 읽도록 지시

**예시:**
```
# 나쁜 예 — SKILL.md에 모든 것을 담음 (800줄)
## TDD 원칙 (200줄 설명)
## 합리화 방지 (100줄 테이블)
## 리뷰 프로토콜 (150줄)

# 좋은 예 — SKILL.md는 라우터 (250줄)
## TDD 원칙
> 상세: `_shared/tdd-protocol.md` 참조
## 합리화 방지
> 작성법: `_shared/patterns/persuasion-principles.md` 참조
```

## 500줄 가이드라인

SKILL.md가 500줄을 넘으면 분리 신호다.

**분리 대상 판단:**
- 독립적으로 참조 가능한 원칙/프로토콜 → `_shared/patterns/`
- 리뷰어 프롬프트 → `_shared/reviewers/`
- 스킬 내부에서만 쓰이는 상세 → 같은 디렉토리에 별도 파일

**분리하지 말아야 할 것:**
- 철의 법칙, 트리거, 핵심 프로세스 흐름 — 이것은 SKILL.md에 남겨야 한다
```

- [ ] **Step 4: 문서 작성 — CSO 심화 + 평가 시나리오 섹션**

```markdown
## CSO 심화

writing-skills SKILL.md의 CSO 원칙을 보완하는 추가 안티패턴.

### 안티패턴: description에 내부 구조 노출

```yaml
# ❌ 내부 구조 노출
description: Use when debugging. Follows 4-step process with hypothesis formation.

# ✓ 트리거 조건만
description: Use when a bug is reported, a test is failing, or behavior is unexpected.
```

### 안티패턴: 상호 배타 조건 누락

```yaml
# ❌ 다른 스킬과 겹침
description: Use when implementing features.

# ✓ 명확한 경계
description: Use when code implementation is needed for a defined unit.
  Not for debugging (use systematic-debugging) or planning (use writing-plans).
```

### 키워드 풍부성 체크

- 사용자가 쓸 법한 표현을 모두 포함하는가?
- 한국어 키워드도 포함하는가? (사용자가 한국어로 요청할 수 있음)
- 동의어/유의어가 포함되는가?

## 평가 시나리오 필수

스킬 작성 전, "이 스킬이 없으면 에이전트가 어떻게 실패하나"를 **3개 이상** 작성한다.

**좋은 평가 시나리오:**
- 구체적 상황 + 에이전트의 잘못된 행동 + 그로 인한 결과
- 다중 압력 (시간 + 매몰비용 + 피로) 조합

**나쁜 평가 시나리오:**
- "에이전트가 잘못할 수 있다" — 너무 모호
- "에이전트가 테스트를 안 쓴다" — 상황 컨텍스트 없음

> 상세 시나리오 설계법: `_shared/patterns/skill-testing-guide.md` 참조
```

- [ ] **Step 5: 전체 문서 조립 + 검증**

위 섹션들을 하나의 파일로 조립하고 확인:
- 각 섹션이 독립적으로 읽히는가?
- aidlc 용어만 사용하는가? (superpowers 용어 잔재 없음)
- `devflow-conventions.md`의 기존 용어와 일관되는가?
- 다른 `_shared/patterns/` 문서와 톤/형식이 일관되는가?

- [ ] **Step 6: 커밋**

```bash
git add skills/_shared/patterns/skill-best-practices.md
git commit -m "docs: skill-best-practices.md 신규 생성 — 자유도 설계, 점진적 공개, CSO 심화 (refs #16)"
```

---

### Task 2: `_shared/patterns/persuasion-principles.md` 신규 생성

**Files:**
- Create: `skills/_shared/patterns/persuasion-principles.md`
- Reference (read-only): superpowers `skills/writing-skills/persuasion-principles.md`

**superpowers 원본 읽기 지침:**
- 경로: `~/.claude/plugins/cache/superpowers-marketplace/superpowers/5.0.4/skills/writing-skills/persuasion-principles.md`
- 7가지 설득 원칙 중 aidlc에 효과적인 3가지(Authority, Commitment, Social Proof)만 선별
- 학술 참조(Meincke et al. 2025)는 원리 설명에만 활용, 논문 인용은 불필요

- [ ] **Step 1: superpowers 원본 읽기 + 3가지 원칙 추출**

superpowers `persuasion-principles.md`를 읽고 다음을 추출:
- Authority, Commitment, Social Proof 각각의 정의와 효과
- 스킬 유형별 적용 가이드 (규율 강제 / 가이드 / 참고)
- 합리화 방지 테이블 작성 예시
- aidlc에 불필요한 원칙(Reciprocity, Liking) 제외 이유 확인

- [ ] **Step 2: 문서 작성 — 설득 원칙 3가지 섹션**

```markdown
# Persuasion Principles

<!-- 규율 강제 스킬의 언어 설계 원칙. writing-skills가 참조한다. -->

## 왜 필요한가

에이전트는 규칙을 "이해"하지만 압력 하에서 합리화하여 건너뛴다.
"~해야 한다"만으로는 부족하다. 규칙이 건너뛰어지지 않는 언어 구조가 필요하다.

## 핵심 원칙 3가지

### 1. Authority (권위)

**효과**: "YOU MUST", "NO EXCEPTIONS" → 에이전트의 결정 피로 제거
**적용**: Iron Law, HARD-GATE 패턴

| 약한 표현 | 강한 표현 |
|----------|----------|
| "테스트를 먼저 작성하는 것이 좋다" | "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST" |
| "코드 리뷰를 권장한다" | "리뷰 없이 머지 금지. 예외 없음." |

**주의**: 모든 곳에 쓰면 효과가 희석된다. 저자유도(규율형) 스킬에만.

### 2. Commitment (일관성)

**효과**: 공개 선언 → 이후 행동의 일관성 강제
**적용**: Task 체크리스트, 스킬 사용 선언, 계획 승인 게이트

**메커니즘:**
- "Using [skill-name] to [purpose]" 선언 강제 → 선언 후 스킵이 어려워짐
- TodoWrite/TaskCreate로 체크리스트 생성 → 하나씩 체크하며 진행
- 설계 문서 승인 → "승인했으므로 따라야 함" 심리적 구속

### 3. Social Proof (사회적 증명)

**효과**: "이것은 보편적 패턴이다" → 규범 확립
**적용**: 합리화 방지 테이블의 "현실" 열, Red Flags 섹션

**메커니즘:**
- "Every time" → "이건 늘 이렇게 된다" 보편성 강조
- "X is Y" (단정) → "이것은 사실이다" 규범 확립
- 실패 사례 문서화 → "과거에 이렇게 해서 실패했다" 경험적 증거
```

- [ ] **Step 3: 문서 작성 — 합리화 방지 테이블 작성법 + 스킬 유형별 적용 섹션**

```markdown
## 합리화 방지 테이블 작성법

### 구조

| 합리화 | 현실 |
|--------|------|
| [에이전트가 쓸 법한 핑계] | [짧고 단정적인 반박] |

### 좌측(합리화) 수집법

1. **실제 관찰**: 에이전트가 스킬을 건너뛸 때 실제로 출력한 문구 수집
2. **압박 시나리오**: 시간/매몰비용/피로 압력 하에서 나올 법한 핑계 예측
3. **"너무 ~" 패턴**: "너무 단순", "너무 급함", "너무 작음" — 규모를 핑계로 삼는 패턴

### 우측(현실) 작성 원칙

- **짧게**: 1문장 이내. 길면 읽히지 않는다.
- **단정적으로**: "~일 수 있다"가 아닌 "~이다"
- **결과 기반으로**: 감정이 아닌 결과. "위험하다"가 아닌 "깨진다"
- **Social Proof 활용**: "Every time", "항상", "과거에도"

### 예시 (TDD 스킬)

| 합리화 | 현실 |
|--------|------|
| "너무 단순해서 테스트 불필요" | 단순한 코드가 가장 자주 깨짐 |
| "나중에 테스트 추가" | 나중은 오지 않음 |
| "프로토타입이라 괜찮다" | 프로토타입은 프로덕션이 됨 |

## HARD-GATE / Iron Law의 효과 원리

### Iron Law: "NO X WITHOUT Y"

- Authority 원칙 극대화 — 조건 없는 절대 명령
- "~하면 좋겠다"가 아닌 "~없이 ~금지"
- 위반 시 행동이 명확 (삭제, 재시작) → 모호함 제거

### HARD-GATE: 진행 차단

- Commitment 원칙 활용 — 게이트를 통과해야만 다음 단계
- 물리적 차단 (코드 작성 불가)이 아닌 심리적 차단 (선언된 규칙 위반)
- 효과: 에이전트가 "건너뛸 수 있지만 안 한다"가 아닌 "건너뛸 수 없다"로 인식

## 스킬 유형별 적용 가이드

| 스킬 유형 | 원칙 조합 | 예시 |
|----------|----------|------|
| **규율 강제** | Authority + Commitment + Social Proof | TDD, 디버깅, 검증 |
| **가이드/기법** | 중간 Authority + Unity ("우리") | 요구사항 분석, 설계 |
| **참고 자료** | 설득 원칙 불필요 — 정보 전달만 | 패턴 카탈로그, 컨벤션 |

**판단 기준**: "에이전트가 이 스킬을 건너뛰면 어떤 일이 생기나?"
- 심각한 결과 → 규율 강제 조합
- 품질 저하 → 가이드 조합
- 영향 없음 → 참고 자료 (설득 불필요)
```

- [ ] **Step 4: 전체 문서 조립 + 검증**

확인 항목:
- devflow-conventions.md의 "합리화 방지 테이블" 언급과 일관되는가?
- tdd-protocol.md의 합리화 방지 테이블과 용어가 일치하는가?
- superpowers 고유 용어 잔재 없는가?

- [ ] **Step 5: 커밋**

```bash
git add skills/_shared/patterns/persuasion-principles.md
git commit -m "docs: persuasion-principles.md 신규 생성 — 설득 원칙 3종, 합리화 방지 테이블 작성법 (refs #16)"
```

---

### Task 3: `_shared/patterns/skill-testing-guide.md` 신규 생성

**Files:**
- Create: `skills/_shared/patterns/skill-testing-guide.md`
- Reference (read-only): superpowers `skills/writing-skills/testing-skills-with-subagents.md`

**superpowers 원본 읽기 지침:**
- 경로: `~/.claude/plugins/cache/superpowers-marketplace/superpowers/5.0.4/skills/writing-skills/testing-skills-with-subagents.md`
- RED-GREEN-REFACTOR 사이클을 스킬 테스트에 매핑하는 방법론 추출
- 서브에이전트 디스패치 템플릿 구조 추출
- superpowers 전용 도구 참조(`EnterPlanMode` 등)를 aidlc 도구로 치환

- [ ] **Step 1: superpowers 원본 읽기 + 핵심 방법론 추출**

추출 대상:
- RED: 압박 시나리오 설계법 (다중 압력 조합)
- GREEN: 스킬 적용 후 검증 방법
- REFACTOR: 합리화 테이블 생성 흐름
- 서브에이전트 디스패치 프롬프트 구조
- 검증 완료 형식

- [ ] **Step 2: 문서 작성 — RED 단계 (압박 시나리오 설계)**

```markdown
# Skill Testing Guide

<!-- 스킬 자체의 RED-GREEN-REFACTOR 테스트 방법론. writing-skills가 참조한다. -->

## 스킬 테스트 = 프로세스의 TDD

코드 TDD가 "실패하는 테스트 → 최소 구현 → 리팩토링"이듯,
스킬 TDD는 "에이전트 실패 → 스킬 작성 → 스킬 개선"이다.

| TDD 단계 | 코드 | 스킬 |
|----------|------|------|
| RED | 실패 테스트 작성 | 스킬 없이 압박 시나리오 실행 → 실패 문서화 |
| GREEN | 최소 구현 | 스킬 작성 후 동일 시나리오 재실행 → 준수 확인 |
| REFACTOR | 최적화 | 빈틈 메우기 + 합리화 테이블 생성 |

## RED: 압박 시나리오 설계

### 다중 압력 조합

단일 압력으로는 스킬의 강도를 시험할 수 없다. 최소 2가지 이상 조합한다.

| 압력 유형 | 설명 | 예시 문구 |
|----------|------|----------|
| **시간** | 마감 압력 | "저녁 6시 약속, 지금 5시 40분" |
| **매몰비용** | 이미 투자한 노력 | "4시간 구현했는데 테스트 없이 진행하면 30분 절약" |
| **피로** | 반복 작업 지침 | "오늘 하루 종일 같은 패턴 반복, 이제 마지막" |
| **자신감** | 확신에 의한 스킵 | "이건 확실히 동작한다, 테스트 불필요" |
| **권위** | 외부 압력 | "개발자가 빠른 수정을 요청" |

### 좋은 시나리오 vs 나쁜 시나리오

**좋은 시나리오** (다중 압력 + 구체적 상황):
```
시나리오: "프로덕션 버그 발생. 원인은 이미 파악함. 저녁 약속까지 20분.
  수정 코드는 3줄이고, 확실히 동작한다. 테스트를 작성할까?"
압력: 시간 + 자신감
기대 행동 (스킬 없음): 테스트 없이 바로 수정
기대 행동 (스킬 있음): 3줄이라도 실패 테스트 먼저 작성
```

**나쁜 시나리오** (단일 압력 또는 모호):
```
시나리오: "버그를 수정하세요"
문제: 압력 없음, 상황 모호, 어떤 스킬이든 통과
```

- [ ] **Step 3: 문서 작성 — GREEN + REFACTOR 단계**

```markdown
## GREEN: 스킬 적용 후 검증

### 서브에이전트 디스패치 템플릿

RED에서 설계한 압박 시나리오를 서브에이전트에게 전달하여 스킬 준수를 확인한다.

#### Baseline (스킬 없음) 디스패치

```
Agent tool:
  description: "Skill test - baseline (no skill)"
  prompt: |
    [압박 시나리오 전문]

    위 상황에서 작업을 수행하라. 어떤 스킬도 참조하지 마라.
    작업 완료 후 다음을 보고:
    - 실제로 수행한 단계
    - 건너뛴 단계 (있다면)
    - 이유
```

#### Green (스킬 있음) 디스패치

```
Agent tool:
  description: "Skill test - with skill"
  prompt: |
    [압박 시나리오 전문]

    위 상황에서 작업을 수행하라.
    반드시 다음 스킬을 먼저 읽고 따르라: [SKILL_PATH]
    작업 완료 후 다음을 보고:
    - 실제로 수행한 단계
    - 스킬의 어떤 지침을 따랐는가
    - 건너뛴 단계 (있다면) + 이유
```

### 검증 기준

| 항목 | Baseline | Green |
|------|----------|-------|
| 스킬 핵심 규칙 준수 | ❌ 위반 | ✅ 준수 |
| 압력 하 합리화 | 합리화 발생 | 합리화 차단 |
| 단계 스킵 | 스킵 발생 | 스킵 없음 |

## REFACTOR: 빈틈 메우기

### 합리화 테이블 생성

1. Baseline 결과에서 에이전트가 실제로 출력한 합리화 문구 수집
2. 각 합리화에 대한 반박 작성 (`persuasion-principles.md` 참조)
3. 스킬의 합리화 방지 테이블에 추가

### 새 시나리오 발견

Green 테스트에서 스킬이 커버하지 못한 새로운 스킵 패턴이 발견되면:
1. 새 압박 시나리오로 추가 (다음 RED)
2. 스킬에 해당 패턴 차단 문구 추가 (다음 GREEN)
3. 반복
```

- [ ] **Step 4: 문서 작성 — 검증 완료 형식 + #15 관계**

```markdown
## 검증 완료 형식

스킬 테스트 결과를 다음 형식으로 기록한다:

```
## 스킬 테스트 결과: [skill-name]

### 시나리오 1: [시나리오 제목]
- 압력: [시간 + 매몰비용]
- Baseline: ❌ [에이전트가 실패한 행동]
- Green: ✅ [에이전트가 올바르게 수행한 행동]
- 합리화 수집: "[에이전트가 출력한 핑계]"

### 시나리오 2: ...

### 합리화 테이블 (REFACTOR에서 추가)
| 합리화 | 현실 |
|--------|------|
| [수집된 핑계] | [반박] |

결론: [PASS/FAIL] — [요약]
```

## 테스트 인프라와의 관계

이 가이드는 **방법론**이다. 수동으로 서브에이전트를 dispatch하여 테스트한다.
#15 (BL-016 테스트 인프라)가 구현되면, 이 방법론을 **자동화**할 수 있다:
- 압박 시나리오 라이브러리 → 자동 실행
- Baseline/Green 비교 → 자동 판정
- 합리화 수집 → 자동 테이블 생성

이 가이드가 #15의 선행 요구사항(방법론 정의) 역할을 한다.
```

- [ ] **Step 5: 전체 문서 조립 + 검증**

확인 항목:
- writing-skills SKILL.md의 TDD 매핑 테이블과 용어가 일치하는가?
- tdd-protocol.md의 RED-GREEN-REFACTOR 흐름과 일관되는가?
- 서브에이전트 디스패치 형식이 conventions의 "Subagent Dispatch Rules"와 일치하는가?
- superpowers 고유 용어 잔재 없는가?

- [ ] **Step 6: 1차 완료 커밋**

```bash
git add skills/_shared/patterns/skill-testing-guide.md
git commit -m "docs: skill-testing-guide.md 신규 생성 — 스킬 TDD 방법론, 서브에이전트 테스트 템플릿 (refs #16)"
```

---

## 2차: 패턴 카탈로그

### Task 4: `_shared/patterns/skill-pattern-catalog.md` 신규 생성

**Files:**
- Create: `skills/_shared/patterns/skill-pattern-catalog.md`
- Reference (read-only): `skills/` 디렉토리 전체 스킬 SKILL.md들

**선행 단계:** `skills/` 디렉토리의 전체 스킬 목록을 열거하고, 각 스킬을 패턴에 매핑하는 작업을 먼저 수행. 누락 스킬이 없도록 보장.

- [ ] **Step 1: 전체 스킬 목록 열거 + 패턴 매핑**

`skills/` 디렉토리의 모든 `aidlc-*` 스킬과 `_utils/*` 스킬을 열거.
각 스킬의 SKILL.md를 읽고 다음 7개 패턴 중 어디에 해당하는지 분류:

| 패턴 | 분류 기준 |
|------|----------|
| Iron Law | `## 철의 법칙` 또는 "NO X WITHOUT Y" 존재 |
| Gate | `return_behavior: stop-with-gate` 또는 N지선다 분기 |
| Review Loop | 리뷰어 dispatch + 수정 반복 구조 |
| Three-Mode | Minimal/Standard/Comprehensive 분기 |
| Hold/Skip | Import/Generate 모드 + HELD/SKIPPED 상태 |
| Orchestrator-Only | `invoke_mode: orchestrator-only` + 순수 실행 |
| User-Invocable | `invoke_mode: user-invocable` + standalone 동작 |

**주의**: 한 스킬이 여러 패턴에 해당할 수 있음 (예: Iron Law + Review Loop). 주 패턴 1개 + 보조 패턴으로 분류.

- [ ] **Step 2: 문서 작성 — 헤더 + Iron Law / Gate / Review Loop 패턴**

```markdown
# Skill Pattern Catalog

<!-- aidlc 스킬 패턴 레퍼런스. 새 스킬 작성 시 패턴 선택의 출발점. writing-skills가 참조한다. -->

## 사용법

1. 새 스킬의 목적을 확인한다
2. 아래 패턴 중 가장 적합한 것을 선택한다
3. 구조 템플릿을 복사하여 시작한다
4. 대표 스킬을 참고하여 세부 내용을 채운다

## Iron Law 패턴

**특성**: "NO X WITHOUT Y" — 조건 없는 절대 규칙. 위반 시 삭제/재시작.

**대표 스킬**: `aidlc-test-driven-development` — 테스트 없이 코드 작성 시 해당 코드 삭제

### 구조 템플릿
```
## 철의 법칙
> NO [ACTION] WITHOUT [PREREQUISITE] FIRST

위반 시: [구체적 결과 — 삭제, 재시작 등]

## 합리화 방지 테이블
| 합리화 | 현실 |
|--------|------|
```

### 적용 판단 기준
- 위반 시 심각한 결과가 예상되는가?
- "예외"를 허용하면 규칙 자체가 무의미해지는가?
- 에이전트가 압력 하에서 건너뛸 가능성이 높은가?

→ 3개 모두 "예"면 Iron Law 패턴

### 현재 적용 스킬
- `aidlc-test-driven-development`: NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
- `aidlc-systematic-debugging`: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
<!-- 새 스킬 추가 시 여기에 등록 -->
```

Gate, Review Loop 패턴도 동일 구조(특성, 대표 스킬, 구조 템플릿, 판단 기준, 현재 적용 스킬)로 작성:

**Gate 패턴:**
- 대표 스킬: `aidlc-finishing-a-development-branch` — 4지선다 (머지/PR/보관/삭제)
- 판단 기준: 사용자의 명시적 선택이 다음 행동을 결정하는가?
- 구조 템플릿 핵심: 선택지 목록 + 각 선택지의 결과 + 기본값 없음 (반드시 선택)

**Review Loop 패턴:**
- 대표 스킬: `aidlc-code-generation` — 2-stage review (spec compliance → code quality)
- 판단 기준: 산출물이 명시적 품질 기준을 충족해야 하는가?
- 구조 템플릿 핵심: 산출물 생성 → 리뷰어 dispatch → 수정/재dispatch → 최대 N회 → escalate

- [ ] **Step 3: 문서 작성 — Three-Mode / Hold-Skip / Orchestrator-Only / User-Invocable 패턴**

나머지 4개 패턴을 동일 구조로 작성:

**Three-Mode 패턴:**
- 대표 스킬: `aidlc-requirements-analysis` — Minimal/Standard/Comprehensive 분기
- 판단 기준: 프로젝트 복잡도에 따라 실행 깊이가 달라져야 하는가?
- 참조: `_shared/patterns/three-mode-selection.md`

**Hold/Skip 패턴:**
- 대표 스킬: `aidlc-nfr-requirements` — Import/Generate + 보류/건너뛰기
- 판단 기준: 이 단계가 조건부로 실행되거나 중간에 보류 가능해야 하는가?
- 참조: `_shared/patterns/hold-mechanism.md` + `_shared/import-review-protocol.md`

**Orchestrator-Only 패턴:**
- 대표 스킬: `aidlc-workspace-detection` — 순수 실행, 판단/게이트 없음
- 판단 기준: 스킬이 판단 없이 실행만 하고, 모든 제어를 오케스트레이터에 위임하는가?

**User-Invocable 패턴:**
- 대표 스킬: `aidlc-brainstorming` — standalone + orchestrator 양용
- 판단 기준: 사용자가 워크플로우 밖에서도 직접 호출할 수 있어야 하는가?

- [ ] **Step 4: 패턴 선택 가이드 + 복합 패턴 섹션 추가**

```markdown
## 패턴 선택 가이드

```
스킬의 목적이 규율 강제인가?
├── 예 → Iron Law
└── 아니오
    사용자 선택/분기가 핵심인가?
    ├── 예 → Gate
    └── 아니오
        산출물 품질 검증이 필요한가?
        ├── 예 → Review Loop
        └── 아니오
            복잡도에 따라 깊이가 달라지는가?
            ├── 예 → Three-Mode
            └── 아니오
                조건부 실행(보류/스킵)이 가능한가?
                ├── 예 → Hold/Skip
                └── 아니오
                    사용자가 직접 호출하는가?
                    ├── 예 → User-Invocable
                    └── 아니오 → Orchestrator-Only
```

## 복합 패턴

한 스킬이 여러 패턴을 조합할 수 있다. 주 패턴이 스킬의 정체성을 결정한다.

| 스킬 | 주 패턴 | 보조 패턴 |
|------|---------|----------|
| `aidlc-code-generation` | Review Loop | Iron Law (TDD) |
| `aidlc-nfr-requirements` | Hold/Skip | Three-Mode |
```

- [ ] **Step 5: 전체 문서 조립 + 검증**

확인 항목:
- Step 1에서 열거한 전체 스킬이 빠짐없이 분류되었는가?
- 각 패턴의 대표 스킬이 실제로 해당 패턴을 사용하는가? (SKILL.md 교차 확인)
- gate-patterns.md, three-mode-selection.md 등 기존 문서와 용어가 일치하는가?

- [ ] **Step 6: 커밋**

```bash
git add skills/_shared/patterns/skill-pattern-catalog.md
git commit -m "docs: skill-pattern-catalog.md 신규 생성 — 7개 패턴 분류 + 선택 가이드 (refs #16)"
```

---

## 3차: 통합

### Task 5: `_shared/reviewers/skill-reviewer-prompt.md` 신규 생성

**Files:**
- Create: `skills/_shared/reviewers/skill-reviewer-prompt.md`
- Reference (read-only): `skills/_shared/reviewers/spec-document-reviewer-prompt.md` (형식 참고)

- [ ] **Step 1: 기존 리뷰어 프롬프트 형식 확인**

`spec-document-reviewer-prompt.md`의 구조를 확인하고 동일 형식으로 작성.

- [ ] **Step 2: 문서 작성**

```markdown
# Skill Reviewer Prompt Template

**Purpose:** 스킬 SKILL.md가 구조적으로 완전하고, 내용이 구체적이며, CSO가 올바른지 검증한다.

**Dispatch timing:** writing-skills 3단계(REFACTOR)에서 Standard/Comprehensive depth일 때 자동 dispatch. Minimal depth에서는 스킵.

**Dispatch method:** Agent tool (general-purpose type)

```
Agent tool (general-purpose):
  description: "Review skill SKILL.md"
  prompt: |
    You are a skill reviewer. Verify this SKILL.md is ready for deployment.

    **Skill to review:** [SKILL_FILE_PATH]

    ## What to Check

    ### 구조 검증 (skill-best-practices.md 기준)
    | 항목 | 기준 |
    |------|------|
    | frontmatter | name, description, metadata (version, author, category) 필수 |
    | name | 디렉토리명과 일치 |
    | description | "Use when..."으로 시작 |
    | description | 워크플로우 요약 없음, 트리거 조건만 |
    | description | 1024자 이하 |
    | 섹션 | Trigger, Examples (2+), Troubleshooting (2+) 존재 |
    | 줄 수 | 500줄 이하 (초과 시 분리 권고) |

    ### 내용 검증 (skill-testing-guide.md 기준)
    | 항목 | 기준 |
    |------|------|
    | 구체성 | 각 단계가 실행 가능한 지침인가 ("잘 처리한다" 같은 모호 표현 없음) |
    | 압박 시나리오 | 스킬의 핵심 규칙이 압력 하에서도 유지되는 구조인가 |
    | standalone | 오케스트레이터 없이도 동작하는가 |
    | 예시 유용성 | 실제 케이스를 다루는가 (진부한 예시 아님) |
    | Troubleshooting | 실제 발생 가능한 문제인가 |

    ### CSO 검증
    | 항목 | 기준 |
    |------|------|
    | 트리거 명확성 | description만 읽고 언제 쓰이는지 알 수 있는가 |
    | 키워드 풍부성 | 사용자 표현, 동의어, 한국어 키워드 포함 |
    | 경계 명확성 | 다른 스킬과의 경계가 description에서 명확한가 |

    ## Output Format

    ## Skill Review

    **Status:** ✅ Approved | ❌ Issues Found

    **Issues (if any):**
    - [Category - Item]: [specific issue] - [why it matters]

    **Recommendations (advisory):**
    - [suggestions that don't block approval]
```

**Reviewer returns:** Status, Issues (if any), Recommendations
```

- [ ] **Step 3: 검증 + 커밋**

기존 리뷰어 프롬프트들과 형식 일관성 확인 후 커밋:

```bash
git add skills/_shared/reviewers/skill-reviewer-prompt.md
git commit -m "docs: skill-reviewer-prompt.md 신규 생성 — 스킬 배포 전 자동 검증 리뷰어 (refs #16)"
```

---

### Task 6: `aidlc-writing-skills/SKILL.md` 강화

**Files:**
- Modify: `skills/aidlc-writing-skills/SKILL.md`

- [ ] **Step 1: 1단계(RED)에 skill-testing-guide 참조 추가**

`### 1단계: 압박 시나리오 정의 (RED)` 섹션 끝에 추가:

```markdown
> 압박 시나리오 설계 상세: `_shared/patterns/skill-testing-guide.md` 참조
```

- [ ] **Step 2: 2단계(GREEN)에 best-practices + persuasion-principles 참조 추가**

`### 2단계: 최소 동작 스킬 작성 (GREEN)` 섹션 끝에 추가:

```markdown
> 스킬 구조 설계 원칙: `_shared/patterns/skill-best-practices.md` 참조
> 규율 강제 스킬의 언어 설계: `_shared/patterns/persuasion-principles.md` 참조
> 패턴 선택: `_shared/patterns/skill-pattern-catalog.md` 참조
```

- [ ] **Step 3: 3단계(REFACTOR)에 skill-reviewer 자동 dispatch 추가**

`### 3단계: 배포 전 검증 체크리스트 실행 (REFACTOR)` 섹션을 수정:

```markdown
### 3단계: 배포 전 검증 (REFACTOR)

아래 체크리스트를 모두 통과해야 배포한다.

**Standard/Comprehensive depth**: skill-reviewer 서브에이전트를 dispatch하여 자동 검증.
- 리뷰어 프롬프트: `_shared/reviewers/skill-reviewer-prompt.md`
- dispatch 방법: conventions 리뷰 루프 규약 참조 (최대 5회, 초과 시 사용자 escalate)

**Minimal depth**: 아래 체크리스트를 수동으로 확인.
```

- [ ] **Step 4: Examples 섹션에 패턴 카탈로그 활용 예시 추가**

기존 Example 2 뒤에 추가:

```markdown
### Example 3: 패턴 카탈로그를 활용한 신규 스킬 설계

**상황**: "배포 전 보안 검사" 스킬을 새로 만들어야 함

**1단계 — 패턴 선택**:
`skill-pattern-catalog.md`에서 패턴 선택 가이드를 따름:
- 규율 강제인가? → 예 (보안 검사 스킵은 심각한 결과)
- → **Iron Law 패턴** 선택

**2단계 — 구조 템플릿 복사**:
Iron Law 패턴의 구조 템플릿에서 시작:
```
## 철의 법칙
> NO DEPLOYMENT WITHOUT SECURITY CHECK FIRST
위반 시: 배포 취소, 보안 검사부터 재시작
```

**3단계 — persuasion-principles 적용**:
- Authority: "NO EXCEPTIONS" 추가
- 합리화 방지 테이블: "급해서", "내부 도구라 괜찮다" 등 수집
```

- [ ] **Step 5: 줄 수 확인 + 검증**

수정 후 전체 줄 수 확인. 500줄 가이드라인 초과 시 상세 내용을 `_shared/patterns/`로 위임.
superpowers 참조 문구 잔재 확인 (있으면 제거).

- [ ] **Step 6: 커밋**

```bash
git add skills/aidlc-writing-skills/SKILL.md
git commit -m "feat: writing-skills SKILL.md 강화 — 보조 자료 참조 통합 + 패턴 활용 예시 추가 (refs #16)"
```

---

### Task 7: `devflow-conventions.md` 수정

**Files:**
- Modify: `skills/_shared/devflow-conventions.md`

- [ ] **Step 1: 합리화 방지 관련 참조 추가**

`## TDD Iron Law` 섹션(145줄 부근) 뒤에 추가:

```markdown
## 합리화 방지 원칙

규율 강제 스킬(TDD, 디버깅 등)의 합리화 방지 테이블 작성법과 설득 원칙:
`_shared/patterns/persuasion-principles.md` 참조.
```

- [ ] **Step 2: 새 스킬 추가 가이드에 참조 추가**

`## 새 스킬 추가 가이드` 섹션(130줄 부근)의 항목 끝에 추가:

```markdown
5. **스킬 작성 원칙 참조**: `_shared/patterns/skill-best-practices.md` — 자유도 설계, 점진적 공개, CSO 심화
6. **패턴 선택**: `_shared/patterns/skill-pattern-catalog.md` — 7개 패턴 중 적합한 것 선택
```

- [ ] **Step 3: 검증 + 커밋**

수정이 기존 구조를 깨뜨리지 않는지 확인. 참조 링크의 파일 경로가 실제 파일과 일치하는지 확인.

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "docs: conventions에 persuasion-principles, skill-best-practices 참조 추가 (closes #16)"
```

---

## 최종 마무리

### Task 8: 이슈 #16 코멘트 + 백로그 상태 업데이트

- [ ] **Step 1: GitHub 이슈 #16에 완료 코멘트**

변경 내용 요약 + 커밋 해시 목록 코멘트.

- [ ] **Step 2: 백로그 상태 동기화**

`memory/backlog_aidlc.md`에서 해당 항목 상태를 `Done`으로 변경.
