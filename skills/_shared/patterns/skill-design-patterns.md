---
type: pattern
applies_to: [aidlc-writing-skills]
status: active
source: manual
last_validated: 2026-04-13
---

# Skill Design Patterns — 구조 패턴 가이드

<!-- 스킬 내부 구조를 어떻게 설계할지 결정하는 참조 문서. writing-skills Stage 2에서 Claude가 자동 판별에 사용한다. -->

> **행동 패턴**(skill-pattern-catalog.md: Iron Law, Gate, Review Loop 등)과 **직교**하는 별도 축.
> 행동 패턴 = "사용자와 어떻게 상호작용하는가", 구조 패턴 = "스킬 내부를 어떻게 설계하는가".
> 하나의 스킬은 행동 패턴과 구조 패턴을 각각 하나씩 갖는다.

---

## 결정 트리

> **이 결정 트리는 Claude가 내부적으로 사용한다.** 사용자에게 5가지를 나열하지 않는다.
> Claude는 스킬의 목적을 분석하여 패턴을 자동 판별하고, 효과 중심으로 추천 + 근거를 제시한다.
> 사용자는 확인하거나 교정할 수 있고, 전문가는 패턴명으로 직접 지정할 수 있다.

```
1. 특정 라이브러리/도구의 전문 지식을 가르쳐야 하는가?
   → Yes: Tool Wrapper

2. 매번 고정된 템플릿/구조의 산출물을 생성해야 하는가?
   → Yes: Generator

3. 산출물을 체크리스트 기준으로 평가해야 하는가?
   → Yes: Reviewer

4. 행동하기 전에 사용자로부터 정보를 수집해야 하는가?
   → Yes: Inversion

5. 순서가 있는 다단계 워크플로우 + 단계 간 검증 게이트가 필요한가?
   → Yes: Pipeline
```

**복수 해당 시**: Pipeline이 다른 패턴을 내부 단계로 포함할 수 있다 (예: Pipeline의 한 단계가 Reviewer).

---

## 5가지 구조 패턴

### 1. Tool Wrapper — 도구 전문 지식 제공

특정 라이브러리, API, 도구의 컨벤션과 베스트 프랙티스를 `references/`에 패키징하여 에이전트가 전문가처럼 사용하도록 한다. 가장 단순한 패턴.

**디렉토리 구조**:
```
skill-name/
├── SKILL.md           # 핵심 지침 + references 로드 시점
└── references/
    └── conventions.md # 도구별 규칙/패턴
```

**핵심 설계**:
- SKILL.md = "언제, 어떤 참조를 로드하고, 어떻게 적용하라"
- 상세 규칙은 `references/`에 분리 → 점진적 공개
- 코드 리뷰 시: 참조 로드 → 규칙 대조 → 위반 지적
- 코드 작성 시: 참조 로드 → 규칙 준수

**적용 기준**: 에이전트가 특정 도구에 대해 일관된 전문가 수준의 판단을 내려야 할 때

---

### 2. Generator — 고정 구조 산출물 생성

`assets/`의 템플릿과 `references/`의 스타일 가이드를 조합하여 매번 일관된 구조의 산출물을 만든다. 템플릿이 구조를 강제하고, 스타일 가이드가 품질을 강제한다.

**디렉토리 구조**:
```
skill-name/
├── SKILL.md
├── references/
│   └── style-guide.md    # 품질 규칙
└── assets/
    └── template.md       # 산출물 구조
```

**핵심 설계**:
- 템플릿 = 구조 강제, 스타일 가이드 = 품질 강제
- 둘 중 하나만 교체하면 산출물이 변경됨 (지침 수정 불필요)
- 단계: 스타일 가이드 로드 → 템플릿 로드 → 입력 수집 → 채우기

**적용 기준**: 산출물의 일관성이 창의성보다 중요할 때 — 보고서, API 문서, 설정 파일, 커밋 메시지

---

### 3. Reviewer — 체크리스트 기반 평가

`references/`의 체크리스트를 기준으로 코드, 문서, 산출물을 평가하고 심각도별 결과를 보고한다. **무엇을 검사할지**(체크리스트)와 **어떻게 검사할지**(리뷰 프로토콜)가 분리되어 있다.

**디렉토리 구조**:
```
skill-name/
├── SKILL.md                # 리뷰 프로토콜
└── references/
    └── review-checklist.md # 검사 항목
```

**핵심 설계**:
- 체크리스트 교체 = 다른 리뷰 (보안 체크리스트 → 보안 리뷰)
- 각 발견 항목에 심각도 + 이유 + 수정안 포함
- 단계: 체크리스트 로드 → 대상 이해 → 항목별 대조 → 보고서

**적용 기준**: 인간 리뷰어가 체크리스트를 들고 검토하는 모든 상황

---

### 4. Inversion — 스킬이 사용자에게 질문

일반적인 "사용자 질문 → 에이전트 답변" 흐름을 뒤집는다. 에이전트가 정해진 단계별 질문을 하여 충분한 컨텍스트를 수집한 후에만 행동한다.

**디렉토리 구조**:
```
skill-name/
├── SKILL.md          # 질문 단계 + 게이트
└── assets/
    └── template.md   # 수집 완료 후 채울 산출물
```

**핵심 설계**:
- **단계별 게이트가 핵심** — Phase 1 완료 전 Phase 2 진입 금지
- "DO NOT start [행동] until all phases are complete" 게이트 필수
- 이 게이트가 없으면 에이전트는 첫 답변만 듣고 추측으로 진행
- 질문 설계: `question-format-guide.md` 참조

**적용 기준**: 에이전트가 추측 대신 사실에 기반해 행동해야 할 때 — 요구사항 수집, 진단 인터뷰, 설정 위자드

---

### 5. Pipeline — 다단계 워크플로우 + 검증 게이트

순서가 있는 단계들을 정의하고, 각 단계 사이에 검증 게이트를 둔다. 가장 복잡한 패턴이며, 다른 4가지 패턴을 내부 단계로 포함할 수 있다.

**디렉토리 구조**:
```
skill-name/
├── SKILL.md
├── references/
│   ├── style-guide.md
│   └── quality-checklist.md
└── assets/
    └── template.md
```

**핵심 설계**:
- **게이트 조건이 핵심** — "Do NOT proceed to Step N until [조건]"
- 각 단계는 필요한 리소스만 로드 (토큰 효율)
- 단계 스킵 시 잘못된 산출물이 발생하는 워크플로우에 적합
- 패턴 합성: Step 2가 Reviewer, Step 3이 Generator 등

**적용 기준**: 단계를 건너뛰면 산출물이 오염되는 순서 의존적 워크플로우

---

## aidlc 기존 스킬 매핑

| aidlc 스킬 | 구조 패턴 | 행동 패턴 | 근거 |
|------------|----------|----------|------|
| `brainstorming` | **Inversion** | Review Loop | 사용자에게 질문 수집 → 설계 산출 |
| `requirements-analysis` | **Inversion + Generator** | Three-Mode | 질문으로 요구사항 수집 → SRS 템플릿 채우기 |
| `code-generation` | **Generator** | Review Loop | 계획 템플릿 → 코드 생성 |
| `requesting-code-review` | **Reviewer** | Review Loop | 체크리스트 기반 코드 평가 |
| `systematic-debugging` | **Pipeline + Inversion** | Iron Law | 정보 수집 → 4단계 순서 분석 |
| `using-devflow` | **Pipeline** | Gate | 다단계 워크플로우 + A/B 게이트 |
| `units-generation` | **Generator** | Orchestrator-Only | 유닛 목록 산출물 생성 |
| `writing-skills` | **Pipeline + Inversion** | User-Invocable | 시나리오 수집 → RED/GREEN/REFACTOR 단계 |

---

## 베스트 프랙티스

### 기본값을 제공하라, 메뉴를 제공하지 마라

여러 도구/접근법이 가능할 때, 기본값을 정하고 대안은 간략히 언급한다.

```markdown
<!-- 나쁜 예 — 선택 마비 유발 -->
pypdf, pdfplumber, PyMuPDF, pdf2image 중 선택할 수 있습니다...

<!-- 좋은 예 — 기본값 + 탈출 경로 -->
pdfplumber로 텍스트를 추출한다. 스캔 PDF(OCR 필요)는 pdf2image + pytesseract를 대신 사용한다.
```

### 절차를 가르쳐라, 정답을 주지 마라

스킬은 특정 인스턴스의 정답이 아니라, 문제 유형을 풀어가는 방법을 가르쳐야 한다.

```markdown
<!-- 나쁜 예 — 이 태스크에만 유효 -->
orders 테이블과 customers를 customer_id로 JOIN, region = 'EMEA' 필터...

<!-- 좋은 예 — 재사용 가능한 절차 -->
1. references/schema.yaml에서 관련 테이블 찾기
2. _id 외래키 컨벤션으로 JOIN
3. 사용자 요청의 필터를 WHERE 절로 변환
4. 집계 + 마크다운 테이블 포맷
```

### 에이전트가 모르는 것만 넣어라

에이전트가 이미 아는 일반 지식(PDF란 무엇인가, HTTP 작동 원리)은 생략한다. "이 지시 없이 에이전트가 틀릴까?" — 아니라면 삭제.

---

## 출처

이 가이드는 아래 자료에서 aidlc 맥락에 맞게 재구성한 것이다 (ADK/Python 특화 내용 제외):

- [5 Agent Skill Design Patterns Every ADK Developer Should Know](https://lavinigam.com/posts/adk-skill-design-patterns/) — Lavi Nigam
- [Agent Skills Specification](https://agentskills.io/specification) — agentskills.io
- [Best Practices for Skill Creators](https://agentskills.io/skill-creation/best-practices) — agentskills.io
