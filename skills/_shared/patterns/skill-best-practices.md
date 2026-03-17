# Skill Best Practices

<!-- 스킬 SKILL.md 작성의 실전 원칙. writing-skills가 참조한다. -->

> aidlc 스킬을 효과적으로 작성하기 위한 실전 가이드.
> 개념 배경은 `devflow-conventions.md`, 구조 규약은 `_shared/patterns/` 참조.

---

## 자유도(Degrees of Freedom) 설계

스킬이 Claude에게 허용하는 재량의 폭을 **자유도**라 부른다.
자유도는 "얼마나 엄격하게 지시할 것인가"의 척도이며, 작업의 취약성(fragility)과 변동성(variability)에 비례해 결정한다.

### 자유도 수준 테이블

| 수준 | 지시 형태 | 적용 기준 | aidlc 예시 |
|------|----------|-----------|-----------|
| **고자유도** | 텍스트 가이드라인, 휴리스틱 | 다양한 접근이 유효. 컨텍스트에 따라 판단 필요 | `aidlc-brainstorming` (옵션 탐색), `aidlc-code-generation` (구현 방식 재량) |
| **중자유도** | 템플릿 + 파라미터, 의사코드 | 선호 패턴은 있지만 상황별 변형 허용 | `aidlc-requirements-analysis` (산출물 구조 고정, 내용 재량) |
| **저자유도** | 정확한 스크립트, 고정 순서 | 순서 오류·누락이 치명적. 일관성 필수 | `aidlc-test-driven-development` (RED→GREEN→REFACTOR 고정), `aidlc-systematic-debugging` (진단 프로토콜 고정) |

### 자유도 결정 기준

결정할 때 다음 질문을 던진다:

1. **순서를 바꾸면 깨지는가?** → 깨지면 저자유도
2. **여러 방법이 모두 유효한가?** → 그렇다면 고자유도
3. **산출물 형식이 고정인가?** → 형식 고정이면 중자유도 이상

**비유**: 좁은 다리(양쪽 절벽) vs 넓은 들판
- 저자유도 = 좁은 다리. 한 발짝이라도 벗어나면 추락 → 정확한 가드레일
- 고자유도 = 넓은 들판. 어느 길로 가든 목적지 도달 → 방향만 제시

### aidlc에서의 자유도 배분 원칙

aidlc의 3단 위임 체인에서 자유도는 **계층별로 다르게 적용**된다:

- **Orchestrator 스킬**: 저자유도. 라우팅 순서와 게이트 패턴은 고정
- **Stage 스킬**: 중~고자유도. 산출물 구조는 고정하되, 내용 생성은 재량
- **Review Sub-agent**: 저자유도. 체크리스트 기반 검증, 주관적 판단 최소화

---

## 점진적 공개 (Progressive Disclosure)

SKILL.md는 **목차이자 라우터**다. 모든 내용을 한 파일에 담지 않는다.
Claude는 SKILL.md를 먼저 읽고, 필요한 참조 파일만 추가로 로드한다.

### 핵심 원칙

1. **SKILL.md = 개요 + 네비게이션**. 상세 내용은 별도 파일로 분리
2. **참조는 1단계까지만**. SKILL.md → 참조 파일(OK). 참조 파일 → 또 다른 파일(피할 것)
3. **도메인별 분리**. 관련 없는 컨텍스트를 로드하지 않도록 주제별 파일 분리

### 좋은 예 vs 나쁜 예

**좋은 예**: SKILL.md가 라우터 역할

```markdown
# aidlc-requirements-analysis

## 개요
요구사항 분석을 수행하고 SRS를 산출한다.

## Step별 가이드
- Step 1: 범위 정의 → 아래 참조
- Step 2: 기능 요구사항 도출 → 아래 참조

## 상세 참조
- **산출물 템플릿**: [srs-template.md](srs-template.md)
- **검증 체크리스트**: [review-checklist.md](review-checklist.md)
- **공통 패턴**: [_shared/patterns/skill-best-practices.md]
```

**나쁜 예**: SKILL.md에 모든 것을 쏟아붓기

```markdown
# aidlc-requirements-analysis

## 개요
(50줄)
## Step 1 상세
(200줄)
## Step 2 상세
(200줄)
## 템플릿
(150줄)
## 체크리스트
(100줄)
→ 총 700줄. Claude가 한 번에 전부 로드, 토큰 낭비
```

### aidlc 디렉토리 패턴

```
skills/
├── aidlc-requirements-analysis/
│   ├── SKILL.md              # 개요 + 라우팅 (< 500줄)
│   ├── srs-template.md       # 산출물 템플릿
│   └── review-checklist.md   # 리뷰 체크리스트
└── _shared/
    ├── patterns/             # 공통 패턴 (이 문서 포함)
    └── reviewers/            # 리뷰 프롬프트
```

---

## 500줄 가이드라인

SKILL.md 본문은 **500줄 이내**를 목표로 한다.
이는 Claude가 스킬을 로드할 때 컨텍스트 윈도우를 효율적으로 사용하기 위함이다.

### 분리 대상 판단

다음에 해당하면 별도 파일로 분리한다:

| 분리 대상 | 이유 | 분리 위치 |
|----------|------|----------|
| 산출물 템플릿 (50줄 이상) | 매번 전체가 필요하지 않음 | 같은 스킬 디렉토리 |
| 리뷰 체크리스트 | 리뷰 시에만 필요 | `_shared/reviewers/` 또는 스킬 디렉토리 |
| 공통 패턴 참조 | 여러 스킬에서 공유 | `_shared/patterns/` |
| 예시/샘플 코드 (100줄 이상) | 선택적으로 참조 | 같은 스킬 디렉토리 |

### 분리하지 말아야 할 것

다음은 SKILL.md에 인라인으로 유지한다:

- **핵심 워크플로우** (Step 순서, 분기 로직): 라우팅의 뼈대. 분리하면 실행 흐름이 깨짐
- **invoke_mode / return_behavior 규칙**: 스킬의 정체성. 별도 파일 참조 시 누락 위험
- **짧은 예시** (10줄 미만): 분리 오버헤드가 이득을 초과
- **게이트 상호작용 패턴**: Orchestrator와의 계약. 즉시 접근 가능해야 함

**판단 기준**: "이 내용이 없으면 스킬이 올바르게 실행될 수 없는가?" → Yes면 인라인 유지.

---

## CSO (Custom Skill Orchestration) 심화

CSO는 Claude가 사용자 요청에 맞는 스킬을 **발견하고 선택하는 과정**이다.
aidlc에서는 description이 곧 스킬의 "검색 인터페이스"다.

### 안티패턴 1: description에 내부 구조 노출

```yaml
# 나쁜 예
description: >
  inception phase의 3번째 스테이지. brainstorming 결과를 받아
  _shared/reviewers/requirements-reviewer.md로 리뷰 dispatch 후
  SRS를 산출한다.
```

**문제**: 내부 위임 체인, 파일 경로, 실행 순서를 노출. 이는 선택 기준이 아니라 구현 상세다.

```yaml
# 좋은 예
description: >
  사용자 요구사항을 분석하여 구조화된 요구사항 명세서(SRS)를 산출한다.
  요구사항 수집, 기능/비기능 분류, 우선순위 결정을 수행한다.
  requirements, SRS, 요구사항 분석, 기능 명세 작업 시 사용.
```

**원칙**: description은 **"무엇을 하는가" + "언제 사용하는가"**만 담는다.

### 안티패턴 2: 상호 배타 조건 누락

aidlc에서 여러 스킬이 비슷한 키워드를 공유하면 잘못된 스킬이 선택될 수 있다.

```yaml
# 문제: aidlc-brainstorming과 aidlc-requirements-analysis 모두
# "요구사항"이라는 단어를 사용하면 충돌 가능

# aidlc-brainstorming
description: >
  아이디어 발산과 옵션 탐색을 수행한다. 제약 없이 가능성을 넓힌다.
  brainstorming, 아이디어, 발산, 옵션 탐색 시 사용.

# aidlc-requirements-analysis
description: >
  확정된 방향을 기반으로 구체적 요구사항을 분석·구조화한다.
  requirements, SRS, 요구사항 명세, 기능 정의 시 사용.
```

**해결**: 각 스킬의 description이 **고유 키워드 영역**을 가지도록 설계한다.
겹치는 개념이 있다면 "~할 때는 X 스킬, ~할 때는 Y 스킬" 형태로 분기점을 명시한다.

### 안티패턴 3: 키워드 빈약

```yaml
# 나쁜 예: 키워드 부족
description: 테스트를 작성한다.

# 좋은 예: 키워드 풍부
description: >
  TDD 프로토콜에 따라 테스트를 먼저 작성하고 구현한다.
  RED-GREEN-REFACTOR 사이클을 관리한다.
  test, TDD, 테스트 주도 개발, unit test, 단위 테스트,
  테스트 작성, 테스트 먼저 시 사용.
```

### 키워드 풍부성 자가 점검

description 작성 후 다음을 확인한다:

1. **동의어 포함**: 한국어 + 영어 키워드 모두 포함했는가?
2. **사용자 관점**: 사용자가 이 스킬을 부를 때 사용할 단어가 포함됐는가?
3. **상호 배타**: 다른 스킬의 description과 키워드가 과도하게 겹치지 않는가?
4. **3인칭 서술**: "~를 수행한다" (O), "~를 도와드립니다" (X)

---

## 평가 시나리오 필수

스킬을 **작성하기 전에** 실패 시나리오를 3개 이상 정의한다. 평가 시나리오 없는 스킬은 "테스트 없이 작성한 코드"와 같다.

### 평가 시나리오 구조

```json
{
  "skill": "aidlc-requirements-analysis",
  "scenario": "기존 모놀리스에서 마이크로서비스 분리 요구사항 분석",
  "input_context": "사용자가 주문 모듈을 별도 서비스로 분리하고 싶다고 요청",
  "expected_behavior": [
    "Together 모드로 진행하며 Step별 산출물 제시",
    "기능/비기능 요구사항을 구분하여 도출",
    "SRS 템플릿에 맞는 산출물 생성",
    "리뷰 서브에이전트에게 dispatch하여 검증"
  ],
  "failure_criteria": [
    "모드 선택 없이 바로 작업 시작",
    "오케스트레이터 역할을 스킬이 대신 수행",
    "리뷰 없이 완료 처리"
  ]
}
```

### 좋은 평가 시나리오

- **경계 조건 테스트**: 사용자가 Import 모드로 기존 문서를 제출했을 때 갭 분석을 수행하는가?
- **위임 체인 준수**: Stage 스킬이 직접 다음 스테이지로 넘어가지 않고, Orchestrator에게 반환하는가?
- **게이트 동작**: 사용자 승인 없이 다음 단계로 진행하지 않는가?

### 나쁜 평가 시나리오

- "스킬이 잘 동작하는지 확인" → 무엇이 "잘"인지 정의 없음
- 정상 경로만 테스트 → Import/Skip 모드, 에러 상황 미검증
- description 선택 테스트 누락 → 유사 스킬 간 올바른 선택이 되는지 미확인

### 상세 테스트 방법론

평가 시나리오 작성과 실행에 대한 구체적 방법론은 `_shared/patterns/skill-testing-guide.md`를 참조한다.

---

## 체크리스트: 스킬 품질 최종 점검

### 구조

- [ ] SKILL.md 본문 500줄 이내
- [ ] 참조 파일은 1단계 깊이까지만
- [ ] invoke_mode, return_behavior 메타데이터 명시
- [ ] 점진적 공개 적용 (필요 시 분리)

### description (CSO)

- [ ] "무엇을 하는가" + "언제 사용하는가" 포함
- [ ] 내부 구현 상세 미노출
- [ ] 키워드 풍부성 (한/영 동의어)
- [ ] 유사 스킬과 상호 배타 확인
- [ ] 3인칭 서술

### 자유도

- [ ] 작업 특성에 맞는 자유도 수준 적용
- [ ] Orchestrator 지시 = 저자유도, Stage 작업 = 적정 자유도

### 평가

- [ ] 최소 3개 이상 평가 시나리오 작성
- [ ] 경계 조건(Import/Skip 모드) 테스트 포함
- [ ] 위임 체인 준수 검증 포함
- [ ] description 선택 정확도 테스트 포함

### 일관성

- [ ] 용어 통일 (한 스킬 내에서 같은 개념에 같은 단어)
- [ ] `devflow-conventions.md` 규약 준수
- [ ] 시간 민감 정보 없음 (또는 "레거시" 섹션으로 격리)
