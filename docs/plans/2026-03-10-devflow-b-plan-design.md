# devflow B안 (Orchestrator-Centric) 설계 문서

- **작성일**: 2026-03-10
- **상태**: 승인됨
- **브랜치**: `phase3/b-plan`
- **참조 문서**: `docs/plans/2026-03-10-devflow-design.md` (C안 설계)

---

## 배경 및 결정 과정

### 원래 아키텍처 선택지 (C안 설계 문서에서)

C안 설계 시 세 가지 아키텍처를 검토했다:

| 접근 | 설명 | 당시 결정 |
|------|------|----------|
| A. Thin Wrapper | Superpowers 구조 유지, AI-DLC 개념만 추가 | ❌ |
| B. 오케스트레이터 중심 | 중앙 skill이 전체 흐름 제어 | ❌ (복잡도 과다) |
| C. Enhanced Skills | 독립 skill + AI-DLC 패턴 내장 + 공통 유틸 | ✅ 채택 |

C안(Enhanced Skills)이 채택되어 현재 main 브랜치에 완성되었다 (22개 skill).

### Phase 3: B안 재검토

C안 완성 후, B안을 별도 브랜치에서 구현하여 두 접근법을 실제로 비교하기로 결정했다.

### 결정 과정 토론 요약 (2026-03-10)

**Q1: B안이란 무엇인가?**

세 가지 해석이 제시되었다:
- A) 오케스트레이터 재구현: 중앙 skill이 전체 AI-DLC 흐름을 순차 제어
- B) Phase 1만 추출: C안 아키텍처 유지, Phase 2(일상 도구) 제외
- C) 둘 다: Phase 1 스테이지 + 오케스트레이터 패턴

**Q2: 어느 선택지가 AI-DLC 컨셉에 가장 가까운가?**

- **B) Phase 1만 추출**: "덜 복잡한 C안"에 불과. AI-DLC 컨셉을 새롭게 구현하지 않음.
- **A) 순수 오케스트레이터**: AI-DLC "생명주기" 컨셉은 잘 살리지만, 오케스트레이터가 God Object가 될 위험.
- **C) Phase 1 + 오케스트레이터**: **가장 AI-DLC 컨셉에 가깝다고 판단.** AI-DLC는 시작부터 끝까지 흐르는 단일 프로세스(Life Cycle)를 전제하며, 이를 오케스트레이터가 명시적으로 구현.

→ **옵션 C (Phase 1 스테이지 + 오케스트레이터) 방향으로 결정**

**Q3: 오케스트레이터를 얼마나 중앙화할 것인가?**

세 가지 수준이 제시되었다:

| 수준 | 설명 | 판단 |
|------|------|------|
| Level 1 (얕음) | 오케스트레이터는 "다음 단계 결정"만. 게이트/상태/로깅은 각 skill | C안과 사실상 동일. 의미 없음. |
| Level 2 (중간) | 오케스트레이터가 게이트+전환+상태+로깅 소유. 각 skill은 실행만 | **채택** — AI-DLC 사이클의 리듬이 한 곳에 집중 |
| Level 3 (완전) | 오케스트레이터가 도메인 로직까지 소유 | God Object. 유지보수 불가. |

→ **Level 2 채택**: "승인 게이팅 = Life Cycle의 마디"가 오케스트레이터에 집중되어 AI-DLC 컨셉이 살아남.

---

## 설계

### 브랜치 전략

```
main                  ← C안 완성 (건드리지 않음)
  └── phase3/b-plan   ← B안 Level 2 (신규, 독립 발전)
```

`phase3/b-plan`은 `main`에서 분기하지만 머지를 목표로 하지 않는다.
두 브랜치는 **비교 목적**으로 독립적으로 유지된다.

### 스킬 구성

**C안 (22개)** vs **B안 (9개)**:

```
B안 skills/
├── using-devflow/         ← 오케스트레이터 (완전 재작성)
├── workspace-detection/   ← 순수 실행자 (게이트/상태/로깅 제거)
├── requirements-analysis/ ← 순수 실행자
├── workflow-planning/     ← 순수 실행자
├── application-design/    ← 순수 실행자 (조건부)
├── units-generation/      ← 순수 실행자 (조건부)
├── code-generation/       ← 순수 실행자
├── build-and-test/        ← 순수 실행자
└── _utils/
    ├── devflow-state/     ← 동일 (오케스트레이터가 호출)
    └── devflow-audit/     ← 동일 (오케스트레이터가 호출)
```

Phase 2 일상 개발 도구(12개)는 이 브랜치에 포함하지 않는다.

### 책임 분리

| 책임 | C안 | B안 Level 2 |
|------|-----|------------|
| 승인 게이트 (A/B) | 각 stage skill | `using-devflow` |
| devflow-state 업데이트 | 각 stage skill | `using-devflow` |
| devflow-audit 로깅 | 각 stage skill | `using-devflow` |
| 다음 스테이지 결정 | 각 stage skill | `using-devflow` |
| 도메인 실행 로직 | 각 stage skill | 각 stage skill (동일) |
| Phase 2 일상 도구 | 포함 (12개) | 제외 |

### 오케스트레이터(`using-devflow`) 동작 흐름

```
using-devflow 활성화
  │
  ├─ [세션 재개] devflow-state 확인 → 중단 지점부터 재개
  │
  └─ [신규 세션] INCEPTION 루프 시작:
       ┌─────────────────────────────────────────┐
       │ 1. 현재 스테이지 skill 호출              │
       │    ("실행하고 결과만 반환할 것")           │
       │                                         │
       │ 2. 결과를 오케스트레이터가 표시            │
       │                                         │
       │ 3. devflow-audit 로깅 (오케스트레이터)    │
       │                                         │
       │ 4. 승인 게이트 제시:                     │
       │    "A) 변경 요청 B) 다음 단계 진행"       │
       │                                         │
       │ 5. B 선택 시:                            │
       │    - devflow-state 업데이트              │
       │    - 다음 스테이지 결정                  │
       │    - 반복                               │
       └─────────────────────────────────────────┘
```

### 각 Stage Skill의 새로운 역할

C안의 stage skill은 실행+게이트+상태관리를 모두 했다.
B안의 stage skill은 **실행만** 한다:

```markdown
# [stage-name] — B안 형식

## Purpose
[도메인 목적]

## Execute
[실행 단계 — 분석/설계/생성]

## Output Format
[오케스트레이터에게 반환할 결과 형식]

## Artifact
[저장할 파일 경로]
```

게이트, 상태 업데이트, 감사 로깅은 일절 포함하지 않는다.

---

## C안과의 비교 포인트

이 브랜치가 완성되면 다음을 실제로 비교할 수 있다:

### 응집도
- **B안**: AI-DLC 사이클의 "리듬" (게이트 → 전환 → 재개)이 `using-devflow` 하나에 집중
- **C안**: 같은 로직이 10개 skill에 분산

### 확장성
- **B안**: 새 스테이지 추가 시 오케스트레이터 수정 필요 (단일 변경점)
- **C안**: 새 skill만 추가하면 됨 (오케스트레이터 불필요)

### 단순성
- **B안**: 9개 skill, stage skill은 단순
- **C안**: 22개 skill, 각 skill은 자급자족

### AI-DLC 컨셉 충실도
- **B안**: "Life Cycle = 오케스트레이터가 구동하는 사이클"이 명시적
- **C안**: "Life Cycle = 독립 skill들이 devflow-state로 연결" — 묵시적

---

## 미결 사항

- 오케스트레이터가 `workflow-planning` 결과를 어떻게 읽고 조건부 스테이지(application-design, units-generation)를 판단할지 — 구현 계획 수립 시 상세화
- `plugin.json` 관리: B안과 C안이 같은 레포에서 다른 브랜치이므로 각 브랜치의 plugin.json은 독립적으로 유지
