# Skill Lifecycle Strategy: 모델 발전에 따른 스킬 진화 관리

> **Date**: 2026-04-06
> **Status**: Brainstorming Complete — 실행 미착수
> **Participants**: Claude (Plan, Explore, Codex 에이전트 3종 병렬 브레인스토밍)

## 배경

aidlc-devflow 플러그인의 ~30개 스킬 중 상당수가 모델의 약점을 보상(compensation)하는 역할을 한다.
모델이 발전하면 이 보상 스킬들의 활용 가치가 떨어지는 시점이 온다.
전부는 아니더라도 일부라도 활용도가 떨어지면 일하는 방식을 바꿔야 한다.

**핵심 프레임워크**: 스킬의 가치는 "보상(compensation)"과 "증폭(amplification)"으로 나뉜다.
- **보상**: 모델이 못하는 것을 강제 — 모델이 잘하게 되면 불필요
- **증폭**: 조직/개인 고유 지식 인코딩 — 모델이 아무리 똑똑해져도 대체 불가

---

## 4가지 제안

### 제안 1: 스킬 태깅 (skill_nature)

각 SKILL.md frontmatter에 `skill_nature`와 `model_dependency` 추가.

```yaml
metadata:
  skill_nature: compensation | amplification | hybrid
  model_dependency: "모델이 자발적으로 실패 테스트를 먼저 작성하지 않음"
```

#### 전수 분류 초안

**Compensation (4개)** — 모델 발전 시 첫 번째 경량화 후보:
- `verification-before-completion` — 조기 완료 선언 방지
- `test-driven-development` — TDD 강제
- `systematic-debugging` — 추측 수정 방지
- `build-and-test` — 실행 검증 강제

**Amplification (17개)** — 모델과 무관하게 영구 유지:
- `using-devflow`, `inception-orchestrator`, `construction-orchestrator`
- `brainstorming`, `workflow-planning`, `workspace-detection`
- `requirements-analysis`, `writing-skills`, `superpowers-tracking`
- `requesting-code-review`, `receiving-code-review`, `writing-plans`
- `dispatching-parallel-agents`, `subagent-driven-development`
- `using-git-worktrees`, `finishing-a-development-branch`, `auto-mode`

**Hybrid (7개)** — compensation 부분만 경량화, amplification 부분 유지:
- `code-generation` (TDD 강제 = compensation, 2단계 plan+generate = amplification)
- `executing-plans` (체크포인트 리뷰 = compensation, 세션 재개 = amplification)
- `application-design`, `functional-design`
- `units-generation`, `user-stories`, `nfr-requirements`

**Infrastructure (3개)** — 태깅 대상 아님:
- `devflow-state`, `devflow-audit`, `devflow-solutions`

#### 향후 진화: 3축 점수 모델

이분법의 한계를 넘기 위해, 운영 데이터가 충분히 쌓이면 3축 점수로 전환 가능.

| 축 | 의미 | 예시 |
|---|------|------|
| Model Gap (0-1) | 모델 약점 보완도 | TDD 강제 = 0.9 |
| Org Specificity (0-1) | 조직 고유 지식 | 컨벤션 가이드 = 0.9 |
| Process Value (0-1) | 모델과 무관한 프로세스 가치 | A/B 게이팅 = 0.9 |

MVP는 `skill_nature` 3종 태그로 시작. 처음부터 점수를 매기면 근거 없는 숫자가 됨.

---

### 제안 2: superpowers-tracking 확장

현재 `superpowers-tracking`은 수동 호출 + 세션별 분석. 이것을 **compensation decay 감지기**로 확장.

#### A. Compensation Decay 분석 템플릿

tracking 스킬에 섹션 추가:

```markdown
## Compensation Decay Analysis

| Skill | 보상 대상 | 최근 10세션 gate 트리거율 | Decay 판정 |
|-------|----------|------------------------|-----------|
| verification-before-completion | 조기 완료 선언 | 5% | full decay |
| test-driven-development | TDD 스킵 | 40% | none |
```

#### B. audit.md 데이터 활용

`devflow-audit`가 기록하는 `[timestamp] [stage] -- [choice]` 데이터에서:
- 게이트가 행동을 실제로 교정한 비율
- 사용자가 routinely skip하는 스킬
- 장기 미호출 스킬

#### C. 실행 주기

모델 메이저 업데이트 시 또는 분기 1회. `devflow-conventions.md`에 규약으로 명시.

---

### 제안 3: 경량화 라이프사이클

#### 상태 모델

```
draft → active → lightened → absorbed | archived
```

- **lightened**: 강제에서 제안으로 전환. 여전히 로드됨.
- **absorbed**: amplification 부분이 다른 스킬에 합성 완료. 원본 제거.
- **archived**: `skills/_archived/`로 이동. 로드되지 않음.

#### frontmatter 추가

```yaml
metadata:
  lifecycle: active
  # lightened 전환 시 추가:
  lightened_date: 2026-06-01
  lightened_reason: "모델이 90%+ 자발적 TDD 수행"
  regression_trigger: "gate 트리거율이 다시 20% 이상이면 active 복원"
```

#### "lightened"의 구체적 의미

| 스킬 유형 | Active 상태 | Lightened 상태 |
|-----------|------------|---------------|
| Iron Law 스킬 (TDD, 검증) | `MUST`, 합리화 방지 테이블 | `SHOULD`, 체크리스트만 유지 |
| 게이팅 스킬 | Hard gate (진행 차단) | Soft gate (자동 진행, 로그만) |
| 프로세스 스킬 | 강제 순서 | 권장 순서, 스킵 가능 |

#### 조기 경량화 리스크 3가지

1. **회귀 맹점**: 모델 능력은 단조 증가가 아님. → `regression_trigger` 조건 필수 기재
2. **분포 이동**: 전체 skip rate 높아도 특정 태스크 유형에선 여전히 필요 → 태스크 유형별 세분화
3. **스킬 상호작용**: A를 lightened 했더니 B 품질도 하락 → lightening 전 counterfactual test 필수

---

### 제안 4: 합성/분해 매핑 (Codex 제안)

hybrid 스킬을 lightening할 때 amplification 조각이 유실되는 문제 해결.

```yaml
decomposition_target:
  drop: ["TDD 강제 게이트", "합리화 방지 테이블"]
  absorb_into:
    - target: code-generation
      content: "2단계 plan+generate 구조"
```

lightening 전에 미리 매핑해두면 "버릴 것 / 옮길 것"이 명확해짐.

---

## 다른 에코시스템 교훈

| 사례 | 교훈 | 적용 |
|------|------|------|
| **ESLint + TypeScript** | `recommended`에서 제거하되 개별 활성화 유지 | lightened ≠ 삭제 |
| **Kubernetes deprecation** | 최소 2 릴리스 유예 + migration guide | `lightened → archived` 사이 최소 기간 |
| **Go gofmt** | 100% 대체 가능한 스킬은 거의 없음 | lightening이 deletion보다 항상 올바른 기본 전략 |
| **Python DeprecationWarning** | 런타임 감지, 즉시 에러 아님 | lightened 스킬 트리거 시 warning 로그 수집 |

---

## Lightening 판정 기준: 3단계 측정 프레임워크

### Level 1 — Skip Rate (필요 조건)

스킬의 강제 게이트가 실제로 행동을 교정한 비율.
- **기준**: 20회 연속 세션에서 gate 트리거율 < 5%
- **주의**: 이것만으로 판단 금지. "해당 유형 태스크가 최근에 없어서"일 수 있음.

### Level 2 — Counterfactual Test (충분 조건에 근접)

스킬 비활성화 상태에서 동일 태스크 실행, 결과 품질 비교.
- 10개 대표 태스크를 ON/OFF로 각각 실행
- 품질 차이가 통계적으로 유의미하지 않으면 lightening 후보
- `superpowers-tracking` 확장에서 자동화 가능

### Level 3 — Time Decay Confirmation (안전망)

Level 2 통과 후 30일간 lightened 상태로 운영.
실제 프로젝트에서 품질 저하 리포트가 없으면 archived 후보.

---

## MVP 실행 계획

### Phase 1 — 단일 세션으로 가능

1. `devflow-conventions.md`에 `skill_nature`, `lifecycle`, `model_dependency` 규약 추가
2. 28개 SKILL.md에 태그 일괄 추가 (위 분류 기준)
3. `superpowers-tracking`에 Compensation Decay 분석 템플릿 추가
4. `validate-skills.sh`에 새 필드 검증 (warning 레벨)

### Phase 2 — 다음 이터레이션

5. 첫 번째 lightening 후보 실행: `verification-before-completion`
6. audit 기반 skip-rate 분석 자동화

### 하지 않을 것

- 별도 레지스트리 파일 (frontmatter로 충분)
- 자동 모델 능력 테스트 인프라 (BL-042로 이미 백로그에 있음)
- 새 스킬 생성 (기존 `writing-skills`와 `superpowers-tracking` 확장으로 흡수)

---

## 핵심 인사이트

> dog-fooding의 진짜 가치는 플러그인 자체가 아니라,
> "AI와 어떻게 일해야 하는가"를 계속 실험하고 있다는 것.
> 도구는 바뀌어도 그 감각은 남는다.
