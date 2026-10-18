# Knowledge System Phase 2 — 레드팀 3차 리뷰 결과 + n=2 검증

> **호출일**: 2026-04-28 (T+14)
> **호출 자료**: `redteam-3rd-call.md`
> **리뷰어**: Codex (1·2차와 동일) + Claude (self-adversarial, 동일 자료 기반 독립 리뷰)
> **추가 데이터**: devflow-k8s-deploy 즉시 측정 (n=1 → n=2)

본 문서는 두 리뷰 원문을 그대로 보존하고(요약/수정 금지 — `external-review-handling` 스킬), 그 후 n=2 데이터로 가설을 재평가한 기록.

---

## 1. Codex 리뷰 (verbatim)

```
# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: Q1–Q5 framing over-commits to a single-cause/one-design narrative on weak evidence, so Phase 2 scope decisions can lock in the wrong fix while hiding real failure modes.

Findings:
- [high] Q1 root-cause conclusion is not falsifiable with current measurements (docs/research/knowledgesystem/redteam-3rd-call.md:75-90)
  The document jumps from "events=0" and "solutions=0" to a shared structural cause (LLM path nondeterminism), but it never measures path entry attempts or failure stage breakdown. With zero denominators, this can also be explained by low/absent qualifying flows (e.g., few finishing/systematic-debugging runs) rather than trigger nondeterminism. Impact: you can deploy the wrong remediation pattern and still keep T2 unresolved while believing the root cause is addressed.
  Recommendation: Before choosing scope, add discriminating counters per boundary: attempted, prompted, executed, skipped, write-failed for finishing/resume/pause/store, and require at least one non-zero attempt window before attributing root cause.
- [high] Control-group logic is biased against the documented observation model (docs/research/knowledgesystem/redteam-3rd-call.md:35-43)
  The call treats plugin-repo zeros as corroborating evidence for T2/BL-092, but the established observation design says consumer-repo behavior is the primary signal and warns about single-repo/generalization limits. Using plugin-repo zero events as confirming evidence without exposure normalization creates confirmation bias, not independent validation. Impact: false confidence in "common root cause" and an oversized integration scope decision.
  Recommendation: Reframe plugin-repo data as implementation health only; use consumer-repo flow-normalized metrics as causality evidence, and require explicit exposure criteria per repo before cross-repo inference.
- [high] Unified Session Boundary Sync proposal lacks idempotency/partial-failure contracts (docs/research/knowledgesystem/redteam-3rd-call.md:107-110)
  The plan applies one deterministic 5-step checklist to finishing/pause/resume/store boundaries, but does not specify per-step atomicity, retry semantics, or dedup keys across state/memory/index/audit writes. A shared checklist across heterogeneous boundaries can amplify duplicates, ordering bugs, and irreconcilable drift during retries or interrupted sessions. Impact: user-visible state divergence and harder rollback despite seeming "deterministic" design.
  Recommendation: Gate integration on a boundary contract table: write owner, idempotency key, commit point, retry policy, and compensation action per boundary; if contracts differ materially, keep scopes split.
- [medium] Alternative-ban language can suppress critical-course correction (docs/research/knowledgesystem/redteam-3rd-call.md:136-173)
  The document bans re-proposing rejected alternatives while simultaneously handling a Critical trigger and newly introduced hypothesis risk. This creates process-level lock-in: if current hypothesis is wrong, reviewers are structurally discouraged from proposing safer rollback/containment designs. Impact: delayed recovery and prolonged operation under a misdiagnosed failure model.
  Recommendation: Replace absolute ban with an exception rule: previously rejected options may be re-opened when a Critical trigger fires and new falsification evidence is documented, with explicit rationale diff vs prior rejection.

Next steps:
- Add a short evidence-gate section to Q1-Q4 requiring non-zero attempt denominators and stage-level counters before causal claims.
- Decide integration vs split only after boundary-specific idempotency/retry contracts are written and reviewed.
- Amend the redteam call constraints to allow evidence-based reopening of rejected alternatives under Critical incidents.
```

## 2. Claude self-adversarial 리뷰 (요지 — 원문은 본 세션 대화 보존)

### Q1 동일 구조 가설
판정: **약함**. 결과 동조에서 역추론한 hindsight bias 의심. 도메인 다름(STORE vs finishing trigger), 대안 가설(디버깅 사이클 부재 / finishing 미진입) 미배제, skill 수동 호출 검증 없음.

### Q2 통합 설계
판정: **premature abstraction**. 5건의 "세션 경계" 우산은 사후 패턴 매칭. review handoff는 외부 협업 경계, mid-cycle pause는 작업 흐름 단절 — 다른 종류의 경계.

### Q3 결정 3건
- M1: skipped=0이라는 사실 자체가 advisory 유지 근거. 트리거 위치 미스매치 가설이 맞다면 MVP 폐기/재설계 가능성까지 고려.
- M3: 추측 기반 ADR은 부채. 충돌 1건 발생 시 작성.
- 통합: BL-097 issue 생성일이 측정 직전 — 사후 합리화 가능성 (시간 순서 confirmation bias).

### Q4 BL-097 결정론 패턴
판정: **자기모순**. LLM 비결정성을 사람 체크리스트로 해결한다는 건 인간 신뢰 의존 = 비결정성 동일. 결정론이라면 hook/code 자동화여야.

### Q5 숨은 가정
- "활발한 사용" 가치판단 (실제는 2.8일에 1번)
- T2 14일 임계가 nexttui baseline 부재
- BL-097 issue 시간 순서
- Falsification 조건 부재

### 자기 비판
- 반례 너무 많이 만든 reviewer bias 가능성
- "premature abstraction" 카드 남용 (통합 비용 미세 분석 없음)
- 검증 미수행 카드의 비대칭성 (대안 가설 데이터도 본 비판이 못 가짐)

---

## 3. 두 리뷰 비교

### 수렴 (양쪽 모두 지적)
- **Q1 falsifiability 부재** — Codex "zero denominators, low qualifying flows로 설명 가능" / Claude "대안 가설 미배제"
- **통합 비용 미평가** — Codex "idempotency/atomicity/retry contract 부재" / Claude "premature abstraction, 단일 실패점"

### Codex만 지적 (실용적·게이트 가능)
- Discriminating counters per boundary (attempted/prompted/executed/skipped/write-failed)
- Plugin-repo as implementation health only (control-group bias 명시)
- Boundary contract table (write owner / idempotency key / commit point / retry / compensation)
- Alternative-ban exception rule (Critical 트리거 + falsification evidence)

### Claude만 지적
- BL-097 결정론 자기모순 (인간 의존 ↔ 결정론 모순)
- BL-097 issue 생성일 시간 순서 (사후 합리화 가능성)
- T2 임계 baseline 부재
- "활발한 사용" 가치판단

### 상충
- 통합 vs 분리 게이팅 메커니즘:
  - Codex: 조건부 통합 (boundary contract 작성 후)
  - Claude: 분리 디폴트 + 단계적 통합

→ 양쪽 모두 "지금 통합 그대로 진행"은 거부.

### 메타 평가
- Codex가 더 정확: control-group bias / idempotency contract / alternative-ban exception
- Claude가 더 정확: BL-097 결정론 자기모순 / 시간 순서 bias
- 종합: Codex가 더 실용적·게이트 가능. Claude는 메타·추상적.

---

## 4. n=2 검증 (devflow-k8s-deploy 추가 측정)

리뷰 직후 사용자 제안으로 추가 consumer repo로 검증 시도.

### devflow-k8s-deploy 자격
- 첫 commit: 2026-04-15 (BL-031 graduation 시점)
- 마지막 commit: 2026-04-24 (4일 휴지기)
- 13일간 87 commits
- audit 234 lines / file-edit 218건 / archive 7건 / state.md 존재
- 도메인: k8s deploy skill plugin (nexttui와 다름)

### n=2 측정 비교

| 측정 | nexttui T+14 | plugin repo | **k8s-deploy 13일** |
|---|---|---|---|
| audit lines | 283 | 189 | 234 |
| file-edit count | 76 | 107 | **218** |
| **file-edit 비율** | 27% | 57% | **93%** |
| **memory-sync- 이벤트** | **0** | **0** | **4** |
| → prompted | 0 | 0 | 2 |
| → staleness-check-run | 0 | 0 | 1 |
| → staleness-resolved | 0 | 0 | 1 |
| → skipped | 0 | 0 | **0** |
| systematic-debugging | 0 | 0 | 0 |
| solutions/ | 0 | 0 | 0 |
| finishing-a-branch | — | — | 1 |

### 결정적 발견

**k8s-deploy에서 BL-092 memory-sync 이벤트 4건 정상 트리거**.
- nexttui/plugin 0건은 *trigger 실패가 아니라 finishing flow 진입 자체가 없었던 것*
- → Codex Q1 비판 정확: "low qualifying flows" 가설이 데이터로 검증
- → 자료의 "LLM 호출 경로 비결정성" 진단은 오진

---

## 5. 가설 반증 결과

| 가설 | 본 자료 결론 | n=2 데이터 후 |
|---|---|---|
| Q1 동일 구조(T2 ≡ BL-092) | 강한 시사 | **반증** — k8s-deploy에서 BL-092 작동, T2 0 = 다른 메커니즘 |
| Q2 4+1건 통합 | 통합 후보 | **무너짐** — 공통 실패 패턴 가정 자체가 틀림 |
| BL-092 M1 advisory→강제 | 보류 | **advisory 유지 확정** — k8s-deploy skipped=0 (4건 prompt 모두 처리) |
| BL-092 M3 ADR | 진행 권장 | 그대로 (데이터 무관) |
| BL-091 통합 | BL-097 합쳐 4+1건 | **분리 유지** — 통합 근거 약화 |
| T2 Critical 해법 | BL-097 5단계 패턴 1순위 | **단독 진단 필요** — 디버깅 사이클 존재 검증 선결 |
| BL-097 결정론 패턴 | T2 해법 후보 | **단독 plan으로 분리** (BL-P2-085 사례 한정) |

---

## 6. 검증된 결론

1. **단일 repo 관측은 confirmation bias 발생**. n=1 → n=2 한 번에 가설 다수 반증. handoff-context §4의 "다중 repo 합산 금지"는 유지하되, **OR 조건 다중 repo 독립 관측은 필수**로 격상.
2. **k8s-deploy를 정식 Tier 1 추가 관측 repo로 등재** (`phase2-observation-update.md`).
3. **BL-092 MVP는 작동 중**. M1 advisory 유지 확정.
4. **Phase 2 plan은 통합 단일 plan이 아니라 분리**:
   - T2 단독: 진단(systematic-debugging dogfooding) 후 plan 또는 임계 재설정
   - BL-097 단독: BL-P2-085 사례 기반 5단계 체크리스트
5. **Codex 권고 적용 사항**:
   - Discriminating counters per boundary (다음 관측 기간에 추가)
   - Alternative-ban exception rule (Critical + falsification evidence 시 재제안 가능 — 이미 본 사이클에서 다중 repo 관측 재고로 적용됨)
   - Boundary contract table (통합 재검토 시 게이트)

---

## 7. T2 단독 진단 결과 (2026-04-28, dogfooding)

`/aidlc:aidlc-systematic-debugging`을 본 case에 적용하여 진단. 코드 변경 금지 제약으로 1-3단계만 수행.

### 디버깅 활동 baseline 측정

| Repo | 기간 | 전체 commits | fix/bug 키워드 commits |
|---|---|---|---|
| nexttui | 14일 | 15 | **2** |
| k8s-deploy | 13일 | 87 | **33** |

→ k8s-deploy fix 33건은 결정적. **H1 (디버깅 사이클 부재) 반증**.

### 작동 vs 미작동 비교 (대조: BL-092 memory-sync)

| 항목 | memory-sync (작동, k8s-deploy 4건) | systematic-debugging (0건) |
|---|---|---|
| audit emit 로직 | skill 본문에 명시 | **부재** (caller 책임만 명시) |
| 자동 트리거 위치 | aidlc-using-devflow Resume + finishing-a-branch | **없음** (orchestrator K-gate / 명시 호출만) |
| invoke_mode | (utility 아님) | STORE는 `orchestrator-only` (devflow-solutions) |
| 호출 추적 | audit prefix 4종으로 명확 | **흔적 자체가 안 남음** |

### 결정적 검증

본 세션에서 `/aidlc:aidlc-systematic-debugging` 명시 호출 후에도 plugin repo audit.md에 systematic-debugging prefix 0건. 마지막 entry는 file-edit hook뿐.
→ **audit.md "0건"이 "skill 호출 0건"이라는 추론은 잘못됨**. emit 로직 자체 부재.

### 가설 판정 (H1-H5)

| 가설 | 판정 | 근거 |
|---|---|---|
| H1: 디버깅 사이클 부재 | ✅ **반증** | k8s-deploy 33건 fix |
| H2: skill 호출 자체 안 됨 | ⚠️ **강한 의심** | fix workflow 자동 진입점 없음. K-gate 외 자동 트리거 부재 |
| H3: 호출됐지만 STORE 미도달 | ❓ **검증 불가** | audit emit 부재로 호출 추적 자체 불가 |
| H4: STORE는 됐지만 기록 실패 | ✅ **부분 반증** | solutions/ 디렉토리 자체가 양 repo 모두 NOT EXIST. 단 invoke_mode 미스매치 시 부분 잔존 |
| H5 (신규): audit emit 로직 자체 부재 | 🆕 **확정** | 본 세션 호출 직후에도 audit 0건 |

### 근본 원인 (복합 RC)

1. **주 RC (H5 + H2)**: systematic-debugging SKILL 본문에 audit emit 로직 부재 + fix workflow 자동 호출 메커니즘 부재 → **호출 여부 자체가 관측 불가능한 상태에서 T2 측정**
2. **부 RC (T2 임계 설계 결함)**: "solutions/ = 0" 단일 metric이 multi-cause(호출 안 됨 / STORE skip / write 실패) 구분 불가. **T2 Critical 발동 자체가 misleading 신호** — Codex Q1 비판 정확.
3. **부 RC (invoke_mode 미스매치)**: systematic-debugging "세 경로 guaranteed STORE" 약속과 devflow-solutions `orchestrator-only` 명세 불일치. user-invocable 경로 STORE 도달 여부 불확실.

### 진단으로 갱신된 결론

| 이전 결론 | 진단 후 결론 |
|---|---|
| T2 발동 = STORE 호출 경로 실패 | T2 발동은 multi-cause — 임계 자체가 진단 신호로 부적절 |
| BL-097 5단계 패턴이 T2 해법 후보 | **무관**. 선결: audit emit + T2 임계 재설계 |
| solutions/ 0건 = systematic-debugging 호출 0건 | **추론 불가** — emit 부재 |

## 8. 후속 작업

### 즉시 (본 세션 직후)
- [x] T2 단독 진단 (`/aidlc:aidlc-systematic-debugging` dogfooding) — §7
- [x] 본 문서 갱신 (§7 진단 결과 추가)
- [x] 메모리 업데이트 (project_knowledge_system_phase1)

### Phase 2 plan 진입 전 선결 (구현 작업)
- [ ] **BL-098** (#191): systematic-debugging SKILL에 audit emit 로직 추가 (`systematic-debugging-invoked` / `-completed` / `-store-attempted` / `-store-write-failed`) — Codex의 discriminating counters 패턴 직접 적용
- [ ] **BL-099** (#192): devflow-solutions `invoke_mode` 명세 vs systematic-debugging "세 경로" 약속 정합성 검증 (BL-090 정합성 linter 후보)
- [ ] **T2 임계 재설계**: 단일 metric → multi-metric 분해 (`debugging-cycles-detected` / `skill-invoked` / `store-attempted` / `write-succeeded`). denominator ≥ 1 확보 후에만 인과 추론

### Phase 2 plan 작성 (선결 후)
- [ ] BL-097 단독 plan — BL-P2-085 사례 기반 (T2와 무관하게 진행 가능)
- [ ] T2 plan은 audit emit 구현 + multi-metric 측정 후 14일 재관측 후

### 다음 관측 사이클 (T+28 = 2026-05-12)
- [ ] 양 Tier 1 repo (nexttui + k8s-deploy) 동기 측정
- [ ] discriminating counters 도입 후 새 데이터로 H2/H3 재판정

## 참고
- BL-092 결정 3건 메모리: `project_bl092_observation.md`
- 본 결과 통합 Knowledge System 메모리: `project_knowledge_system_phase1.md`
- 호출 자료: `redteam-3rd-call.md`
