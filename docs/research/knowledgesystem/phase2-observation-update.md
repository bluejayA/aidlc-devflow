# Phase 2 Observation Plan — Update (n=2 확장)

> **갱신일**: 2026-04-28 (T+14 직후)
> **이유**: 단일 repo(nexttui) 관측이 confirmation bias 발생시킨 것을 레드팀 3차 리뷰에서 확인. n=1 → n=2 확장으로 가설 다수 반증.
> **상위 문서**: `phase2-observation-plan.md` (T0 baseline 보존), `redteam-3rd-result.md` (반증 기록)

본 문서는 `phase2-observation-plan.md`의 **변경분**만 명시. T0 baseline·기각 대안·관측 프로토콜 본문은 상위 문서 참조.

---

## 1. 변경 요약

| 항목 | 이전 | 변경 후 |
|---|---|---|
| Tier 1 관측 repo | nexttui 단독 | **nexttui + devflow-k8s-deploy** (OR 조건) |
| Plugin repo 위치 | (대조군) | **implementation health only** (Codex 권고) |
| Counter 수집 | size / line / count | **+ discriminating counters per boundary** (Codex 권고) |
| Alternative-ban 규칙 | 절대 금지 | **Critical 트리거 + falsification evidence 시 예외** (Codex 권고) |

handoff-context §4의 "다중 repo **합산** 금지" 원칙은 유지. 본 변경은 **다중 repo 독립 관측 (OR 조건)**으로, §4 위반 아님.

---

## 2. devflow-k8s-deploy 등재

### 자격 검증 (2026-04-28T13:38Z)

| 조건 | 결과 |
|---|---|
| 3주+ devflow 실사용 | △ 13일 (4/15 graduation~). 활동량으로 보완 |
| 도메인 다름 | ✅ k8s deploy skill plugin (nexttui는 TUI) |
| audit/state 이력 | ✅ audit 234 lines, state.md 존재, archive 7건 |
| 본업/시뮬 아님 | ✅ BL-031 graduated 후 별도 repo 운영 |
| 활동량 | ✅ 87 commits / 13일 = 6.7/day (nexttui 이상) |
| 마지막 활동 | 2026-04-24 (4일 휴지기) |

### k8s-deploy T0 (현재 시점을 T0로 간주, 13일 누적치)

```bash
cd /Users/jay.ahn/projects/infra/devflow-k8s-deploy
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit: $(git rev-parse --short HEAD)"
echo "audit.md size: $(wc -c < devflow-docs/audit.md) bytes"
echo "audit.md lines: $(wc -l < devflow-docs/audit.md) lines"
echo "file-edit count: $(grep -c 'file-edit' devflow-docs/audit.md 2>/dev/null || echo 0)"
echo "memory-sync events: $(grep -c 'memory-sync-' devflow-docs/audit.md 2>/dev/null || echo 0)"
echo "systematic-debugging events: $(grep -c 'systematic-debugging' devflow-docs/audit.md 2>/dev/null || echo 0)"
echo "solutions/ count: $(find devflow-docs/solutions -type f 2>/dev/null | wc -l)"
echo "state.md present: $([ -f devflow-docs/devflow-state.md ] && echo yes || echo no)"
echo "archived: $(find devflow-docs/.archive -maxdepth 1 -type f 2>/dev/null | wc -l)"
```

### 13일 누적 측정값 (참고용 baseline + 신호)

| 측정 | 값 | 해석 |
|---|---|---|
| audit.md | 234 lines | nexttui T+14(283)와 비슷 |
| file-edit count | 218 | nexttui(76)의 ~3배 |
| **file-edit 비율** | **93%** | T10 임계(>80%) **후보**. 단 도메인 차이(코드 편집 비중)일 가능성 |
| **memory-sync 이벤트** | **4** (prompted 2 / check-run 1 / resolved 1 / **skipped 0**) | BL-092 MVP **정상 작동 확인** |
| systematic-debugging | 0 | nexttui와 동일. 디버깅 사이클 부재 가설 |
| solutions/ | 0 | T2 0건 — n=2에서도 동일 |
| finishing-a-branch | 1 | finishing flow 1회 진입 확인 |

---

## 3. n=2 데이터로 본 가설 반증 (요약)

상세 비교는 `redteam-3rd-result.md` §4-5. 핵심:

1. **BL-092 "0건" → 반증**. k8s-deploy에서 정상 트리거. nexttui/plugin은 진입 부족.
2. **T2 ≡ BL-092 동일 구조 → 반증**. k8s-deploy에서 BL-092 작동·T2 0 = 다른 메커니즘.
3. **M1 advisory 유지 정당**. k8s-deploy skipped 0 / prompt 2건 모두 처리.
4. **통합 가설(BL-091/092/095/097) → 무너짐**. 공통 실패 가정이 틀림.
5. **T2는 단독 진단 필요**. 디버깅 사이클 자체 부재 가능성 우선 검증.

---

## 4. 다음 관측 사이클 — Discriminating Counters 도입

Codex 권고에 따라 **다음 14일 관측에서는 boundary별 분리 카운터** 수집:

### Boundary 정의
- `finishing` — `aidlc-finishing-a-development-branch` 진입
- `resume` — `aidlc-using-devflow` Resume Step 진입
- `pause` — (BL-097 미구현 시 N/A) mid-cycle pause
- `store` — `aidlc-systematic-debugging` STORE 트리거
- `session-start` — Hook session-start

### Counter 종류 (per boundary)
- `attempted` — boundary 진입 시도
- `prompted` — 사용자에게 prompt 표시
- `executed` — 사용자가 실행 선택
- `skipped` — 사용자가 skip 선택
- `write-failed` — 실행했으나 write/sync 실패

### 수집 방법
- 현재 audit.md 이벤트 prefix를 boundary로 분류
- 각 prefix가 attempted/executed/skipped 어느 단계인지 매핑 (next sprint에서 audit emit 코드 보강)
- denominator(attempted) ≥ 1 확보 전까지 인과 추론 금지 (Codex Q1 권고)

---

## 5. Plugin Repo Reframe — Implementation Health Only

기존: nexttui와 함께 대조군으로 사용 (event 0 = T2 corroborating)
변경: **implementation health 채널로만 사용**. consumer-repo 메트릭만 인과 추론에 활용.

### Implementation health 항목
- Hook 정상 실행 여부 (file-edit prefix가 audit에 들어가는지)
- Skill 정의 검증 (description / examples)
- Pattern frontmatter staleness

### 금지 사항
- plugin-repo의 event 0건을 consumer-repo 가설의 corroborating evidence로 사용 금지 (Codex Finding 2)
- exposure normalization 없이 cross-repo 추론 금지

---

## 6. Alternative-Ban Exception Rule (Codex Finding 4)

handoff-context §4의 "기각된 대안 재제안 금지" 절대 룰을 다음 예외로 보강:

> **예외 조건**: 다음 모두 충족 시 기각된 대안 재고 가능
> 1. Critical 트리거 발동 (T1-T10 중 Critical 항목)
> 2. 새 falsification evidence 문서화 (구체 데이터)
> 3. Rationale diff vs prior rejection 명시

본 사이클에서 이미 적용된 사례:
- 기각 대안: "다중 repo 관측"
- Critical 트리거: T2 발동 (2026-04-28)
- Falsification evidence: nexttui 단일 관측이 confirmation bias 발생 (Codex Finding 2 + Claude reviewer self-critique)
- Rationale diff: §4가 기각한 건 "합산"이지 "OR 독립 관측"이 아님 (재해석)

→ devflow-k8s-deploy 등재가 §4 위반 아님을 명시.

---

## 7. 측정 시점 갱신

| 시점 | 날짜 | 액션 |
|---|---|---|
| T0 (nexttui) | 2026-04-14 | 기존 baseline 유지 |
| T0 (k8s-deploy) | 2026-04-28 | 본 등재 시점 = T0 |
| T+14 (nexttui) | 2026-04-28 | 완료 (본 사이클) |
| T+14 (k8s-deploy) | 2026-05-12 | 다음 사이클 측정 |
| T+14 동기화 (양 repo) | 2026-05-12 | nexttui도 재측정 (T+28) |

다음 사이클 핵심 변경:
- discriminating counters 수집 시작
- 양 repo OR 조건 평가
- BL-097 단독 plan + T2 진단 결과 반영

---

## 8. 운영자 가이드 추가 권고

(메모리 feedback `feedback_operator_guide_recommendations.md` 적용)

본 변경에서 운영자 가이드에 추가할 내용:
- "신규 consumer repo 등재 자격 5조건" (3주+ / 도메인 다름 / 이력 / 본업 / 활동량)
- "단일 repo 관측 시 confirmation bias 위험" 경고
- "Discriminating counters per boundary" 패턴 — 새 hook/skill 추가 시 attempted/prompted/executed/skipped/write-failed 카운터 emit
- "Alternative-ban exception rule" — Critical + falsification 시 재제안 절차

---

## 참조

- 상위 관측 plan: `docs/research/knowledgesystem/phase2-observation-plan.md`
- 레드팀 3차 결과: `docs/research/knowledgesystem/redteam-3rd-result.md`
- 호출 자료: `docs/research/knowledgesystem/redteam-3rd-call.md`
- 설계 의도: `docs/research/knowledgesystem/handoff-context.md` (§4 기각 대안 절대 룰의 예외 규칙 추가됨)
- Phase 1 baseline: `docs/research/knowledgesystem/phase1-baseline.md`
- BL-092 결정 메모리: `project_bl092_observation.md`
