# B안 vs C안 비교 분석

- **작성일**: 2026-03-10
- **대상**: devflow 플러그인 B안(phase3/b-plan) vs C안(main)
- **목적**: 두 아키텍처의 장단점과 AI-DLC 컨셉 부합도 비교

---

## 1. 아키텍처 개요

### C안 — Enhanced Skills (Distributed)

각 stage skill이 자급자족(self-contained)한다.
실행 로직 + 승인 게이팅 + 상태 업데이트 + 감사 로깅을 **각 skill이 직접 수행**.

```
[using-devflow]
  │ "workspace-detection 시작해"
  ▼
[workspace-detection]
  1. 스캔 (실행)
  2. 산출물 저장
  3. devflow-state 업데이트  ← skill 내부
  4. devflow-audit 로깅      ← skill 내부
  5. A/B gate 제시           ← skill 내부
  ▼
[requirements-analysis]  ← 이전 skill이 직접 전환
  ...
```

**핵심**: "다음에 뭘 할지"를 각 skill이 알고 있다.

---

### B안 — Orchestrator-Centric (Centralized)

`using-devflow`가 AI-DLC Life Cycle 전체를 구동한다.
Stage skill은 실행만 하고 STOP. 모든 게이팅과 전환은 오케스트레이터가 담당.

```
[using-devflow (Orchestrator)]
  │
  ├─ LOOP:
  │   1. "workspace-detection 실행해 (결과만 줘)"
  │   ▼
  │   [workspace-detection]
  │     1. 스캔 (실행)
  │     2. 산출물 저장
  │     3. 결과 표시 후 STOP  ← skill 종료
  │   ▼
  │   2. devflow-audit 로깅   ← 오케스트레이터
  │   3. A/B gate 제시        ← 오케스트레이터
  │   4. devflow-state 업데이트← 오케스트레이터
  │   5. 다음 스테이지 결정   ← 오케스트레이터 (Stage Routing Table)
  │   6. 반복
  └─
```

**핵심**: "다음에 뭘 할지"를 오케스트레이터만 알고 있다.

---

## 2. 책임 분포 비교

| 책임 | C안 위치 | B안 위치 |
|------|---------|---------|
| 승인 게이팅 (A/B) | 각 stage skill | `using-devflow` |
| devflow-state 업데이트 | 각 stage skill | `using-devflow` |
| devflow-audit 로깅 | 각 stage skill | `using-devflow` |
| 다음 스테이지 결정 | 각 stage skill (hardcoded) | `using-devflow` (Routing Table) |
| 도메인 실행 로직 | 각 stage skill | 각 stage skill |
| 조건부 스테이지 판단 | 각 skill이 workflow-plan 확인 | 오케스트레이터만 확인 |
| 세션 재개 판단 | `using-devflow` (기본) | `using-devflow` |

---

## 3. 코드 구조 비교

### C안 — stage skill 내부 구조

```
[workspace-detection SKILL.md]

## Execution Steps
  Step 1: 스캔 (도메인)
  Step 2: 판단 (도메인)
  Step 3: 산출물 저장 (도메인)
  Step 4: Update state ← 비도메인 책임
  Step 5: Log to audit ← 비도메인 책임
  Step 6: Completion gate ← 비도메인 책임
```

7개 stage skill 각각이 Step 4~6을 반복 보유.

### B안 — stage skill 내부 구조

```
[workspace-detection SKILL.md]

## Execute
  Step 1: 스캔 (도메인)
  Step 2: 판단 (도메인)
  Step 3: 산출물 저장 (도메인)

## Return to Orchestrator
  결과 표시 후 STOP
```

도메인 로직만. 비도메인 책임 없음.

---

## 4. 장단점 분석

### C안 장점

**1. Skill 독립성 (Autonomy)**
각 skill이 단독으로 완전하게 실행된다. `using-devflow` 없이 `requirements-analysis`만 직접 호출해도 완전히 동작한다. 디버깅과 테스트가 skill 단위로 가능하다.

**2. 확장성 (Extensibility)**
새 stage를 추가할 때 오케스트레이터를 수정할 필요가 없다. 새 SKILL.md를 작성하고 plugin.json에 등록하면 된다. Phase 2 일상 도구 12개를 추가한 것처럼, 시스템을 건드리지 않고 기능을 확장할 수 있다.

**3. 충돌 내성 (Fault Isolation)**
특정 skill이 잘못 동작해도 다른 skill에 영향이 없다. 오케스트레이터 버그가 전체 시스템을 마비시키는 상황이 없다.

**4. Claude의 skill 호출 방식과 자연스러운 정합**
Claude는 skill을 "직접 읽고 따르는" 방식으로 동작한다. C안은 각 skill이 명시적 next step을 포함하므로 Claude가 "다음에 뭘 해야 하는지" 명확히 알 수 있다.

### C안 단점

**1. 로직 중복 (DRY 위반)**
7개 stage skill 모두 동일한 패턴을 반복한다:
```
Step N-2: devflow-state to update...
Step N-1: Log to audit...
Step N:   A/B gate...
```
이 패턴이 변경될 경우 7곳을 모두 수정해야 한다.

**2. 워크플로우 가시성 부족 (Workflow Opacity)**
"전체 흐름"을 한 곳에서 볼 수 없다. 다음 스테이지로의 전환 로직이 각 skill에 분산되어 있어, 전체 Life Cycle을 파악하려면 7개 파일을 모두 읽어야 한다.

**3. 전환 일관성 보장 어려움**
각 skill이 독자적으로 다음 스테이지를 결정한다. 실수로 잘못된 스테이지로 연결하거나, 조건부 스테이지 판단이 skill마다 달라질 수 있다.

**4. 승인 게이팅 변경 비용**
A/B gate의 문구나 동작을 바꾸려면 7개 skill을 모두 수정해야 한다.

---

### B안 장점

**1. AI-DLC Life Cycle의 명시적 구현**
"Life Cycle"이 오케스트레이터 하나에 명확히 표현된다. Stage Routing Table을 보면 전체 흐름이 한눈에 보인다. 새로운 개발자가 워크플로우를 파악하는 데 파일 하나면 충분하다.

**2. 단일 변경점 (Single Point of Change)**
게이팅 로직, 상태 관리, 로깅 포맷이 바뀌면 `using-devflow` 하나만 수정한다. DRY 원칙에 충실하다.

**3. Stage skill의 순수성 (Pure Executors)**
각 stage skill은 도메인 로직에만 집중한다. "스캔해라", "분석해라", "설계해라" — 인프라 걱정 없이 본질에 집중한다. skill이 짧고 읽기 쉽다.

**4. 전환 로직의 중앙 통제**
오케스트레이터가 Stage Routing Table을 소유하므로, 스테이지 순서나 조건이 일관되게 유지된다. 실수로 잘못된 스테이지로 전환하는 문제가 없다.

### B안 단점

**1. 오케스트레이터 단일 실패점 (Single Point of Failure)**
`using-devflow`에 버그가 생기면 전체 워크플로우가 중단된다. C안처럼 개별 skill을 직접 호출해서 복구하는 것도 어렵다 — skill 단독 실행 시 게이팅과 상태 관리가 없기 때문이다.

**2. 확장 비용 (Extension Cost)**
새 스테이지를 추가할 때 오케스트레이터의 Stage Routing Table을 반드시 수정해야 한다. 확장이 오케스트레이터를 통과해야 하는 구조다.

**3. Skill 단독 테스트 불가**
B안의 stage skill은 오케스트레이터 없이 단독으로 실행하면 "불완전한 경험"을 준다. 게이팅과 상태 관리가 없어 세션이 끊긴다.

**4. 오케스트레이터의 복잡도**
`using-devflow`가 Orchestration Loop + Stage Routing Table + Multi-Unit Handling + Resume Flow + Construction Complete를 모두 담아야 한다. 파일이 길고 복잡하다. 잘못 이해한 Claude가 루프 로직을 무시할 위험이 있다.

---

## 5. AI-DLC 컨셉과의 부합도

### AI-DLC의 3대 패턴

원본 AI-DLC 방법론이 정의하는 핵심 패턴:

| 패턴 | 설명 |
|------|------|
| **명시적 승인 게이팅** | 각 스테이지 전환 전 사용자 명시적 승인 필수 |
| **산출물 문서화** | 각 스테이지 결과를 구조화된 파일로 저장 |
| **적응형 깊이** | 요청 복잡도에 따라 분석 깊이 자동 조절 |

### 패턴별 구현 비교

#### 명시적 승인 게이팅

| 구현 | 방식 | AI-DLC 부합도 |
|------|------|--------------|
| C안 | 각 skill 끝에 A/B gate — skill이 게이팅 담당 | ✅ 기능적으로 동일 |
| B안 | 오케스트레이터가 모든 gate를 순서대로 관리 | ✅✅ **더 충실** — "Life Cycle이 게이팅을 구동"한다는 원본 컨셉에 가깝다 |

원본 AI-DLC는 게이팅을 "프로세스(오케스트레이터)의 책임"으로 정의한다. 개별 도구(skill)가 게이팅을 소유하는 것은 컨셉과 다르다.

#### 산출물 문서화

| 구현 | 방식 | AI-DLC 부합도 |
|------|------|--------------|
| C안 | 각 skill이 직접 산출물 저장 | ✅ 동일 |
| B안 | 각 skill이 직접 산출물 저장 | ✅ 동일 |

두 구현 모두 동일한 `devflow-docs/` 구조에 산출물을 저장한다. 차이 없음.

#### 적응형 깊이

| 구현 | 방식 | AI-DLC 부합도 |
|------|------|--------------|
| C안 | `requirements-analysis` skill 내부에서 Minimal/Standard/Comprehensive 판단 | ✅ 동일 |
| B안 | 동일 | ✅ 동일 |

두 구현 모두 동일하게 구현됨.

### AI-DLC "Life Cycle" 개념과의 부합

AI-DLC의 이름 자체가 "Development **Life Cycle**"이다. 원본의 핵심 의도는 다음과 같다:

> 개발 프로세스를 하나의 생명주기로 보고, 각 페이즈(Inception → Construction → Operations)를 순서대로 통과하되, 명시적 승인 없이 다음 페이즈로 넘어가지 않는다.

| 관점 | C안 | B안 |
|------|-----|-----|
| "Life Cycle"이 명시적으로 표현되는가 | ❌ 분산됨 — 흐름이 보이지 않음 | ✅ `using-devflow` 하나에 Life Cycle이 표현됨 |
| 워크플로우 전체를 한 곳에서 파악 가능한가 | ❌ 7개 파일을 읽어야 함 | ✅ `using-devflow` 하나로 가능 |
| "프로세스가 전환을 주도"하는가 | ❌ skill이 자체 판단으로 전환 | ✅ 오케스트레이터가 전환을 소유 |
| 게이팅이 "프로세스의 일부"로 느껴지는가 | 보통 — skill 기능처럼 느껴짐 | ✅ 오케스트레이터 루프의 의식(ritual)처럼 느껴짐 |

**결론**: B안이 AI-DLC "Life Cycle" 컨셉에 더 충실하다.

---

## 6. 실용성 비교

### 일반 사용자 관점

| 시나리오 | C안 | B안 |
|---------|-----|-----|
| 워크플로우 전체 흐름 파악 | 어렵다 (파일 다수 읽어야) | 쉽다 (`using-devflow` 1개) |
| 특정 stage만 단독 실행 | ✅ 가능 (skill이 완전함) | ⚠️ 가능하지만 불완전한 경험 |
| 새 stage 추가 | 쉽다 (오케스트레이터 불필요) | 보통 (Routing Table 수정 필요) |
| 버그 발생 시 원인 파악 | 보통 (각 skill 확인) | 쉽다 (오케스트레이터 먼저 확인) |

### 플러그인 개발자 관점

| 시나리오 | C안 | B안 |
|---------|-----|-----|
| 게이팅 문구 일괄 변경 | 7개 파일 수정 | 1개 파일 수정 |
| 새 stage 삽입 | skill 작성 + plugin.json | skill 작성 + Routing Table 수정 |
| stage 실행 순서 변경 | 각 skill의 next-stage 수정 | Routing Table 1곳 수정 |
| Claude 맥락 오염 위험 | 낮음 (skill 단위 격리) | 높음 (오케스트레이터가 전체 context 보유) |

---

## 7. 종합 평가

### 점수표

| 평가 항목 | C안 | B안 |
|---------|:---:|:---:|
| AI-DLC Life Cycle 컨셉 충실도 | ★★★☆☆ | ★★★★★ |
| 워크플로우 가시성 | ★★☆☆☆ | ★★★★★ |
| Skill 단독 실행 가능성 | ★★★★★ | ★★☆☆☆ |
| 확장 용이성 | ★★★★☆ | ★★★☆☆ |
| 로직 중복 제거 (DRY) | ★★☆☆☆ | ★★★★★ |
| 장애 내성 | ★★★★☆ | ★★☆☆☆ |
| 신규 기여자 학습 용이성 | ★★★☆☆ | ★★★★☆ |
| Phase 2 일상 도구 통합 | ★★★★★ | ★★☆☆☆ |

### 어떤 상황에 어느 안이 적합한가

**C안이 적합한 경우:**
- AI-DLC 스테이지와 일상 개발 도구를 하나의 플러그인으로 통합할 때
- 사용자가 개별 skill을 직접 호출하는 유연한 사용을 원할 때
- 플러그인 생태계를 열어 외부 기여자가 skill을 추가하는 구조를 만들 때

**B안이 적합한 경우:**
- AI-DLC 원본 컨셉을 그대로 구현/시연/교육할 때
- 워크플로우 전체를 하나의 단위로 제어하고 싶을 때
- 게이팅과 상태 관리를 중앙에서 일관되게 유지해야 할 때

### 결론

두 아키텍처는 근본적으로 다른 철학을 가진다:

- **C안**은 "**도구의 컬렉션**" — 각 도구가 독립적이고 조합 가능하다. 현실적이고 유연하다.
- **B안**은 "**프로세스 엔진**" — 하나의 프로세스가 전체를 구동한다. AI-DLC의 원본 철학에 충실하다.

AI-DLC를 "방법론 플러그인"으로 오픈소스화하려는 목적에서는 **B안이 컨셉 전달력이 더 높다**. 하지만 실제 개발 워크플로우 도구로 사용하기 위해서는 **C안의 유연성이 더 실용적**이다.

---

## 8. 향후 방향 제안

### 하이브리드 가능성

두 안의 장점을 결합하는 방향:

1. **B안 오케스트레이터 + C안 Stage Skill 완전성**: stage skill이 게이팅 로직은 없되, 단독 실행 시 경고("이 skill은 using-devflow를 통해 실행하는 것을 권장합니다")를 표시
2. **오케스트레이터를 optional로**: C안에 Routing Table을 가진 오케스트레이터 skill을 추가하되, 직접 skill 호출도 계속 지원

### 실험 가치

현재 B안 브랜치(`phase3/b-plan`)는 이 비교를 위해 보존할 가치가 있다:
- AI-DLC 교육/시연 목적으로 사용 가능
- 오케스트레이터 패턴의 실제 구현 예시로 참조 가능
- C안 개선 시 B안의 Stage Routing Table 설계를 참고 가능
