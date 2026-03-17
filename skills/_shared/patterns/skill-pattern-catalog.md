# Skill Pattern Catalog

<!-- 스킬 패턴 카탈로그: 새 스킬 작성 시 어떤 패턴을 따를지 결정하는 참조 문서 -->

새 스킬을 작성할 때 이 카탈로그에서 적합한 패턴을 선택한다.
각 패턴은 특정 문제를 해결하기 위한 구조적 틀이며, 하나의 스킬이 여러 패턴을 조합할 수 있다.

---

## 패턴 선택 가이드

새 스킬에 어떤 패턴을 적용할지 결정할 때 아래 순서로 판단한다.
복수 해당 시 → [복합 패턴 섹션](#복합-패턴) 참조.

```
위반 시 심각한 결과? 예외 허용 불가?
  → Yes: Iron Law 패턴

사용자의 명시적 선택이 다음 행동을 결정?
  → Yes: Gate 패턴

산출물이 명시적 품질 기준을 충족해야?
  → Yes: Review Loop 패턴

복잡도별 실행 깊이가 달라야?
  → Yes: Three-Mode 패턴

조건부 실행/보류/건너뛰기가 필요?
  → Yes: Hold/Skip 패턴

사용자가 워크플로우 밖에서도 직접 호출 가능해야?
  → Yes: User-Invocable 패턴

위 모두 아님 → Orchestrator-Only 패턴
```

---

## 1. Iron Law 패턴

### 특성

- **절대 위반 불가**한 규칙을 스킬 상단에 선언
- `> **NO [ACTION] WITHOUT [PREREQUISITE] FIRST**` 형태의 선언문
- 위반 시 작업을 되돌리고 처음부터 재시작하도록 강제
- 합리화 방지 테이블/Red Flags 섹션을 동반하여 스킵 시도를 차단

### 대표 스킬: `aidlc-test-driven-development`

> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

TDD는 압력 하에서 가장 스킵하기 쉬운 규율이다. "시간이 없으니 나중에 테스트 추가" 같은 합리화가 빈번하며, 한 번 예외를 허용하면 규칙 자체가 무의미해진다. Iron Law 선언 + 합리화 방지 테이블로 이를 구조적으로 차단한다.

### 구조 템플릿

```markdown
# [skill-name]

## 철의 법칙
> **NO [ACTION] WITHOUT [PREREQUISITE] FIRST**

[한 줄 설명: 왜 이 규칙이 절대적인가]

## 합리화 방지

| 합리화 시도 | 왜 안 되는가 | 올바른 행동 |
|------------|-------------|-----------|
| "[합리화 1]" | [이유] | [올바른 행동] |
| "[합리화 2]" | [이유] | [올바른 행동] |

## Red Flags

다음 행동이 감지되면 Iron Law 위반:
- [위반 신호 1]
- [위반 신호 2]

## 프로세스
[Iron Law를 전제로 한 단계별 지침]

## Self-Review
- [ ] Iron Law를 한 번도 위반하지 않았는가?
- [ ] 합리화를 하지 않았는가?
```

### 적용 판단 기준

다음 세 질문 중 **모두 Yes**이면 Iron Law 패턴 적용:

1. **위반 시 심각한 결과?** — 위반이 기술 부채, 품질 저하, 보안 취약점을 초래하는가?
2. **예외 허용 시 규칙 무의미?** — 한 번 예외를 두면 매번 예외를 주장하게 되는가?
3. **압력 하 스킵 가능성 높음?** — 시간 압박, 복잡도, 귀찮음으로 건너뛸 유혹이 큰가?

### 현재 적용 스킬 목록

- `aidlc-test-driven-development` — NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
- `aidlc-systematic-debugging` — NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
- `aidlc-verification-before-completion` — NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
- `aidlc-writing-skills` — NO SKILL WITHOUT DEFINING TRIGGER CONDITIONS FIRST
- `aidlc-code-generation` — TDD Iron Law 참조 (PART 2에서 적용)
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 2. Gate 패턴

### 특성

- 사용자의 **명시적 선택**이 다음 행동을 결정
- 선택지를 명확하게 나열하고, 사용자 응답 없이 진행하지 않음
- 각 선택지에 구체적인 실행 경로가 매핑됨
- 파괴적 선택지에는 이중 확인 절차 포함

### 대표 스킬: `aidlc-finishing-a-development-branch`

4지선다 (병합/PR/유지/폐기) 게이트. 각 선택이 완전히 다른 git 명령 시퀀스를 트리거한다. 사용자 의도 없이 자동 판단하면 되돌릴 수 없는 결과(브랜치 삭제 등)를 초래할 수 있어 반드시 명시적 선택이 필요하다.

### 구조 템플릿

```markdown
## [N]단계: 선택지 제시

```
[현재 상태 요약]

A) [선택지 1] — [결과 설명]
B) [선택지 2] — [결과 설명]
C) [선택지 3] — [결과 설명]
[D) 파괴적 선택지 — 이중 확인 필요]
```

**선택을 기다린다. 사용자 응답 없이 진행하지 않는다.**

## [N+1]단계: 선택에 따른 실행

### 옵션 A: [실행 경로]
[구체적인 실행 절차]

### 옵션 B: [실행 경로]
[구체적인 실행 절차]
```

### 적용 판단 기준

- 사용자의 명시적 선택이 **다음 행동을 완전히 결정**하는가?
- 자동 판단 시 **되돌릴 수 없는 결과**가 발생할 수 있는가?
- 선택지 간 **실행 경로가 질적으로 다른가?** (단순 파라미터 차이가 아님)

### 참조 문서

`_shared/gate-patterns.md` — 표준 게이트, 조건부 게이트, 리뷰 연계 게이트, Hold 변형, 모드 선택 게이트 정의

### 현재 적용 스킬 목록

- `aidlc-finishing-a-development-branch` — 병합/PR/유지/폐기 4지선다
- `aidlc-inception-orchestrator` — 각 스테이지 완료 후 승인/변경/보류 게이트
- `aidlc-construction-orchestrator` — 유닛별 진행 게이트
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 3. Review Loop 패턴

### 특성

- 산출물이 **명시적 품질 기준**을 충족해야 다음 단계로 진행
- 리뷰어 프롬프트 기반 서브에이전트 리뷰 → 이슈 발견 시 수정 → 재리뷰
- 자동 리뷰(서브에이전트) + 사용자 리뷰의 2중 구조
- 최대 반복 횟수 제한 (초과 시 사용자 판단으로 위임)

### 대표 스킬: `aidlc-code-generation`

2-stage review — PART 1(Plan)에서는 code-plan-reviewer가, PART 2(Generate)에서는 code-reviewer가 산출물을 검증한다. 코드 품질은 작성자 자신이 판단할 수 없으므로 외부 리뷰어 역할의 서브에이전트가 필수적이다.

### 구조 템플릿

```markdown
## Review

conventions Review Workflow 적용.

### [단계 1]
- 산출물: [파일 경로]
- 리뷰어: [reviewer-prompt.md]

### [단계 2] (있는 경우)
- 산출물: [파일 경로]
- 리뷰어: [reviewer-prompt.md]
```

리뷰 워크플로우 실행:
1. 산출물 생성
2. 리뷰어 서브에이전트 디스패치
3. 이슈 발견 → 수정 → 재리뷰 (최대 N회)
4. 사용자 리뷰 게이트

### 적용 판단 기준

- 산출물이 **정해진 품질 기준**을 충족해야 하는가?
- 작성자 자신이 **품질을 객관적으로 판단하기 어려운가?**
- 이슈가 발견되면 **수정 후 재검증**이 필요한가?

### 현재 적용 스킬 목록

- `aidlc-code-generation` — Plan 리뷰 (code-plan-reviewer) + Code 리뷰 (code-reviewer)
- `aidlc-brainstorming` — Spec 리뷰 (spec-document-reviewer)
- `aidlc-writing-skills` — 배포 전 검증 체크리스트 (구조/내용/CSO)
- `aidlc-requirements-analysis` — artifact-reviewer로 요구사항 문서 리뷰
- `aidlc-nfr-requirements` — artifact-reviewer로 NFR 문서 리뷰
- `aidlc-functional-design` — 설계 산출물 리뷰
- `aidlc-application-design` — 애플리케이션 설계 리뷰
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 4. Three-Mode 패턴

### 특성

- **Minimal / Standard / Comprehensive** (또는 Together / Import / Skip) 분기
- 복잡도나 사용자 선택에 따라 실행 깊이가 달라짐
- 모드 선택은 오케스트레이터 게이트 또는 자체 판단으로 결정
- 각 모드별 질문 수, 산출물 분량, 검증 깊이가 명시적으로 다름

### 대표 스킬: `aidlc-requirements-analysis`

Minimal / Standard / Comprehensive 3단계 깊이. Minimal은 단일 기능의 명확한 요청에 적합하고, Comprehensive는 다중 컴포넌트·높은 리스크·모호한 요구사항에 적합하다. 같은 스킬이 요청 복잡도에 따라 2~3배 다른 분량의 산출물을 생성한다.

### 구조 템플릿

```markdown
## Step 1: Load complexity

[복잡도 판단 기준 또는 오케스트레이터로부터 전달받는 방법]

**Choose Minimal if ALL of:**
- [조건 1]
- [조건 2]

**Choose Comprehensive if ANY of:**
- [조건 1]
- [조건 2]

**Otherwise: Standard**

## Step N: Execute at chosen depth

### Minimal
[최소 실행 — 핵심만]

### Standard
[표준 실행 — 보조 항목 포함]

### Comprehensive
[심층 실행 — 전체 카테고리 순회]
```

### 적용 판단 기준

- 요청의 **복잡도 범위가 넓어** 하나의 깊이로 처리하기 부적절한가?
- 간단한 요청에 **과도한 절차**를 적용하면 비효율적인가?
- 복잡한 요청에 **얕은 분석**을 적용하면 품질이 떨어지는가?

### 참조 문서

`_shared/patterns/three-mode-selection.md` — Together / Import / Skip 모드 정의

### 현재 적용 스킬 목록

- `aidlc-requirements-analysis` — Minimal / Standard / Comprehensive 분석 깊이
- `aidlc-nfr-requirements` — GENERATE / IMPORT 모드 + 프로파일별 질문 수 조정
- `aidlc-user-stories` — 모드 기반 실행
- `aidlc-brainstorming` — Minimal / Standard / Comprehensive 복잡도 선언
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 5. Hold/Skip 패턴

### 특성

- 실행 도중 **보류(Hold)** 또는 사전에 **건너뛰기(Skip)** 가능
- Hold 시 현재까지의 산출물을 `Status: partial` 마커와 함께 저장
- Skip 시 devflow-state에 SKIPPED 기록 후 다음 단계로 진행
- Resume 시 중단 지점부터 재개

### 대표 스킬: `aidlc-nfr-requirements`

Import/Generate 모드 + 보류/건너뛰기. NFR 수집은 시간이 오래 걸릴 수 있고, MVP 단계에서는 불필요할 수 있다. Hold로 일시 중단하거나 Skip으로 건너뛸 수 있어 워크플로우의 유연성을 보장한다.

### 구조 템플릿

```markdown
## Hold 처리

`_shared/patterns/hold-mechanism.md` 참조.

1. 현재 Step까지의 산출물 저장
2. `## Status: partial — [미완료 항목]` 마커 추가
3. devflow-audit에 Hold 이벤트 로깅

## Skip 처리

1. devflow-state에 SKIPPED 기록
2. 다음 스테이지로 진행
3. devflow-audit에 Skip 이벤트 로깅
```

### 적용 판단 기준

- 실행이 **장시간**이거나 **사용자 입력 대기**가 많아 중단 가능성이 있는가?
- 워크플로우에서 이 스킬이 **선택적**(필수가 아닌)인 경우가 있는가?
- 중단 후 **재개 시 이전 상태 복원**이 필요한가?

### 참조 문서

- `_shared/patterns/hold-mechanism.md` — Hold/Resume 절차
- `_shared/import-review-protocol.md` — Import 모드 검증 프로세스

### 현재 적용 스킬 목록

- `aidlc-nfr-requirements` — GENERATE/IMPORT + Hold/Skip 지원
- `aidlc-user-stories` — Import/Skip 지원
- `aidlc-requirements-analysis` — QUESTIONS 모드 (부분 재실행)
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 6. Orchestrator-Only 패턴

### 특성

- `invoke_mode: orchestrator-only` — 사용자 직접 호출 불가
- 판단/게이트 없이 **실행 후 결과 반환**
- 모든 제어 흐름을 오케스트레이터에 위임
- 반환값은 표준 형식(`Return to Orchestrator`)으로 구조화

### 대표 스킬: `aidlc-workspace-detection`

순수 실행 스킬. 워크스페이스를 스캔하고 Greenfield/Brownfield를 판단한 뒤 결과만 반환한다. 사용자에게 선택지를 제시하거나 승인을 요청하지 않는다. 오케스트레이터가 이 결과를 받아 다음 행동을 결정한다.

### 구조 템플릿

```markdown
---
metadata:
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: [산출물 경로]
---

## Purpose
[이 스킬의 목표 — 2-3문장]

## Execute

### Step 1: [데이터 수집/분석]
[자동 실행 — 사용자 입력 불필요]

### Step 2: [결과 도출]
[판단 기준 테이블 등]

### Step 3: Save artifact
[산출물 저장]

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- [필드 1]: [값]
- [필드 2]: [값]
- 산출물: [경로]
```

### 적용 판단 기준

- 사용자 **판단이나 선택 없이** 자동 실행 가능한가?
- 결과를 **오케스트레이터가 해석**하여 다음 행동을 결정하는가?
- 단독 호출 시 **의미가 없거나 불완전한가?**

### 현재 적용 스킬 목록

- `aidlc-workspace-detection` — 워크스페이스 스캔 + Greenfield/Brownfield 판단
- `aidlc-requirements-analysis` — 요구사항 분석 (오케스트레이터가 depth 전달)
- `aidlc-functional-design` — 기능 설계
- `aidlc-application-design` — 애플리케이션 설계
- `aidlc-nfr-requirements` — NFR 수집
- `aidlc-user-stories` — 사용자 스토리 생성
- `aidlc-workflow-planning` — 워크플로우 계획
- `aidlc-code-generation` — 코드 생성 (오케스트레이터 승인 후 실행)
- `aidlc-build-and-test` — 빌드 및 테스트
- `aidlc-units-generation` — 유닛 분할
- `aidlc-inception-orchestrator` — Inception 페이즈 오케스트레이션
- `aidlc-construction-orchestrator` — Construction 페이즈 오케스트레이션
- `aidlc-using-git-worktrees` — Git 워크트리 관리
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 7. User-Invocable 패턴

### 특성

- `invoke_mode: user-invocable` — 사용자 직접 호출 가능
- 워크플로우 안에서도, **독립적으로도** 동작해야 함
- 스킬 시작 시 선언문 출력 ("aidlc-[name] 스킬을 사용합니다")
- 오케스트레이터 없이도 완결적인 실행 흐름을 가짐

### 대표 스킬: `aidlc-brainstorming`

standalone + orchestrator 양용. 사용자가 직접 "브레인스토밍 해줘"로 호출할 수도 있고, inception-orchestrator가 워크플로우 일부로 호출할 수도 있다. 독립 호출 시에도 설계 문서 생성까지 완결되어야 한다.

### 구조 템플릿

```markdown
---
metadata:
  invoke_mode: user-invocable
---

# [skill-name]

**시작 시 선언**: "aidlc-[name] 스킬을 사용합니다."

## Trigger

다음 상황에서 이 스킬을 실행한다:
- [사용자가 직접 호출하는 상황 1]
- [사용자가 직접 호출하는 상황 2]
- [오케스트레이터가 호출하는 상황]

## Purpose
[이 스킬의 목표]

## 프로세스
[독립 실행에도 완결적인 단계별 지침]

## Examples
[최소 2개 — standalone 호출 예시 포함]

## Troubleshooting
[최소 2개]
```

### 적용 판단 기준

- 사용자가 **워크플로우 밖에서도** 이 스킬을 직접 호출할 필요가 있는가?
- **오케스트레이터 없이도** 의미 있는 산출물을 생성하는가?
- CSO description에 **사용자가 사용할 법한 키워드**가 충분한가?

### 현재 적용 스킬 목록

- `aidlc-brainstorming` — 아이디어 → 설계 문서
- `aidlc-test-driven-development` — TDD 규율 적용
- `aidlc-systematic-debugging` — 체계적 디버깅
- `aidlc-verification-before-completion` — 완료 전 검증
- `aidlc-writing-skills` — 스킬 작성
- `aidlc-writing-plans` — 구현 계획 작성
- `aidlc-executing-plans` — 계획 실행
- `aidlc-subagent-driven-development` — 서브에이전트 병렬 개발
- `aidlc-dispatching-parallel-agents` — 병렬 에이전트 디스패치
- `aidlc-finishing-a-development-branch` — 브랜치 마무리
- `aidlc-receiving-code-review` — 코드 리뷰 수신
- `aidlc-superpowers-tracking` — 진행 추적
- `aidlc-using-devflow` — devflow 사용
<!-- 새 스킬 추가 시 여기에 등록 -->

---

## 복합 패턴

하나의 스킬이 여러 패턴을 조합하는 경우가 흔하다.
주 패턴은 스킬의 **핵심 구조**를 결정하고, 보조 패턴은 **특정 단계에서** 적용된다.

### 조합 예시

| 스킬 | 주 패턴 | 보조 패턴 | 설명 |
|------|---------|----------|------|
| `aidlc-code-generation` | Review Loop | Iron Law (TDD) | Plan 리뷰 + Code 리뷰가 핵심 구조, PART 2에서 TDD Iron Law 적용 |
| `aidlc-nfr-requirements` | Hold/Skip | Three-Mode | Hold/Skip이 핵심 유연성, 프로파일별 깊이 분기가 보조 |
| `aidlc-brainstorming` | User-Invocable | Review Loop + Three-Mode | standalone 호출 가능이 핵심, Spec 리뷰 + 복잡도별 분량 조정이 보조 |
| `aidlc-requirements-analysis` | Three-Mode | Hold/Skip | Minimal/Standard/Comprehensive가 핵심, QUESTIONS 모드로 부분 재실행 |
| `aidlc-finishing-a-development-branch` | Gate | User-Invocable | 4지선다 게이트가 핵심, 사용자 직접 호출 가능 |
| `aidlc-writing-skills` | Iron Law | Review Loop + User-Invocable | 트리거 정의 Iron Law가 핵심, 배포 전 체크리스트 + standalone 호출 |
| `aidlc-test-driven-development` | Iron Law | User-Invocable | TDD 규율이 핵심, 사용자 직접 호출 가능 |
| `aidlc-workspace-detection` | Orchestrator-Only | — | 순수 실행, 보조 패턴 없음 |

### 복합 패턴 적용 원칙

1. **주 패턴이 스킬 구조를 결정한다** — 스킬의 전체 뼈대는 주 패턴의 템플릿을 따름
2. **보조 패턴은 특정 단계에 삽입한다** — Iron Law는 프로세스 상단에, Review Loop는 산출물 생성 후에
3. **3개 이상의 패턴 조합은 경고 신호** — 스킬이 너무 많은 책임을 가지고 있을 수 있음. 분리 검토

---

## 전체 스킬 × 패턴 매트릭스

빠른 참조용. 각 스킬의 주 패턴(●)과 보조 패턴(○)을 표시한다.

| 스킬 | Iron Law | Gate | Review Loop | Three-Mode | Hold/Skip | Orch-Only | User-Inv |
|------|:--------:|:----:|:-----------:|:----------:|:---------:|:---------:|:--------:|
| aidlc-brainstorming | | | ○ | ○ | | | ● |
| aidlc-test-driven-development | ● | | | | | | ○ |
| aidlc-systematic-debugging | ● | | | | | | ○ |
| aidlc-verification-before-completion | ● | | | | | | ○ |
| aidlc-writing-skills | ● | | ○ | | | | ○ |
| aidlc-code-generation | ○ | | ● | | | ○ | |
| aidlc-finishing-a-development-branch | | ● | | | | | ○ |
| aidlc-requirements-analysis | | | ○ | ● | ○ | ○ | |
| aidlc-nfr-requirements | | | ○ | ○ | ● | ○ | |
| aidlc-user-stories | | | | ○ | ● | ○ | |
| aidlc-workspace-detection | | | | | | ● | |
| aidlc-functional-design | | | ○ | | | ● | |
| aidlc-application-design | | | ○ | | | ● | |
| aidlc-workflow-planning | | | | | | ● | |
| aidlc-build-and-test | | | | | | ● | |
| aidlc-units-generation | | | | | | ● | |
| aidlc-inception-orchestrator | | ○ | | | | ● | |
| aidlc-construction-orchestrator | | ○ | | | | ● | |
| aidlc-using-git-worktrees | | | | | | ● | |
| aidlc-writing-plans | | | | | | | ● |
| aidlc-executing-plans | | | | | | | ● |
| aidlc-subagent-driven-development | | | | | | | ● |
| aidlc-dispatching-parallel-agents | | | | | | | ● |
| aidlc-receiving-code-review | | | | | | | ● |
| aidlc-superpowers-tracking | | | | | | | ● |
| aidlc-using-devflow | | | | | | | ● |

<!-- 새 스킬 추가 시 이 매트릭스에도 행을 추가할 것 -->
