# Knowledge System Phase 2 — 레드팀 3차 리뷰 호출 자료

> **호출일**: 2026-04-28 (T+14)
> **호출 방식**: `/codex:adversarial-review` (1·2차와 동일 방식 — Codex adversarial)
> **목적**: T+14 운영 데이터 + BL-097 신규 신호로 Phase 2 plan 스코프 결정.
> 레드팀이 결정하는 건 plan 작성 여부가 아니라 **plan의 스코프**(통합 vs 분리).

---

## 0. 핵심 질문 (레드팀에게)

1. **Q1**: T2 Critical 발동(solutions/ 0개 / 14일)과 BL-092 이벤트 0건은 **동일한 구조적 실패**(skill 호출 경로 비결정성)인가, 다른 원인인가?
2. **Q2**: BL-091 / BL-092 / BL-095 / BL-095b / BL-097 5건을 **단일 "Session Boundary Sync" 설계로 통합**하는 것이 정당한가, 분리 유지가 더 안전한가?
3. **Q3**: BL-092 결정 3건(M1 강제 sync / M3 ADR / BL-091 통합)을 데이터 기반으로 어떻게 판정해야 하는가? (특히 BL-097 등장으로 **트리거 위치 미스매치** 가설이 추가됨)
4. **Q4**: T2 Critical 해법으로 **BL-097의 결정론적 5단계 체크리스트 패턴**을 STORE 호출에도 적용하는 것이 합리적인가, 다른 가설이 있는가?
5. **Q5**: 위 분석에 깔린 **숨은 가정 / confirmation bias**는 무엇인가? (예: "사용자는 finishing 안 하고 mid-cycle pause만 한다"는 단일 사례 일반화)

---

## 1. T+14 측정 데이터

### nexttui (Tier 1, 2026-04-28T13:37:55Z, commit `bec4c05`)

| 측정 | T0 (4/14) | T+14 (4/28) | Δ |
|---|---|---|---|
| audit.md size | 17,326 B / 172 lines | **27,478 B / 283 lines** | +59% / +65% |
| file-edit prefix 건수 | 0 | **76** | E2E 확인 ✅ |
| **solutions/ 파일 수** | 0 | **0** | **변화 없음** |
| devflow-state.md | 3,028 B 존재 | 부재 (마지막 archive 4/23) | — |
| .archive/ states | 11 | 16 (+5) | 활발 |
| .archive/ summaries | 3 | 8 (+5) | 활발 |
| .archive/ inception/ | 9 | 11 (+2) | 활발 |
| .archive/ construction/ | 5 | 7 (+2) | 활발 |

### plugin repo 대조군 (2026-04-28T13:38:40Z, commit `ad48f75`)

| 측정 | T0 (4/13) | T+14 (4/28) | Δ |
|---|---|---|---|
| audit.md size | 10,632 B / 86 lines | **19,027 B / 189 lines** | +79% / +120% |
| file-edit | (첫 도입) | **107** | hook 활발 |
| **memory-sync- 이벤트** | — | **0** | BL-092 신호 |
| solutions/ | 0 | **0** | **변화 없음** |
| state.md | 부재 | 부재 | — |

### BL-092 Memory Sync MVP 측정

```bash
grep -c "memory-sync-" devflow-docs/audit.md
# nexttui: 0
# plugin repo: 0
```

**14일간 3종 이벤트(`prompted`/`run`/`skipped`) 모두 0건.** finishing flow와 using-devflow Resume preflight 어디서도 트리거 안 됨.

---

## 2. 트리거 발동 현황 (T1-T10)

| 트리거 | 임계 | 측정값 | 상태 | 우선도 |
|---|---|---|---|---|
| **T2** | solutions/ = 0 (14일) | **nexttui 0, plugin 0** | 🚨 **발동** | **Critical** |
| T9 | state.md heading 누락/깨짐 | 부재(archive 정상) | 미발동 | Critical |
| T1 | audit.md > 100KB | 27KB / 19KB | 미발동 | High |
| T5 | session-start 토큰 > 2,900 | 미측정 | — | High |
| T10 | file-edit > 80% | 27% / 57% | 미발동 | Low |
| T3, T4, T6, T7, T8 | — | 데이터 부족 | — | — |

**Critical 1건 발동(T2)** → 레드팀 호출 기준 충족. 우선순위 규칙에 따라 **T2 즉시 착수**.

---

## 3. T2 Critical 해석: 동일 구조 가설

### 관찰
- **T2 (Knowledge System)**: 14일간 systematic-debugging의 STORE 호출 0건 → solutions/ 빈 디렉토리
- **BL-092 (Memory Sync)**: 14일간 finishing/Resume 진입 시 sync prompt 0건 → audit 0건
- 양쪽 모두 **skill은 정의되어 있으나 호출 경로가 안 탔음**

### BL-097 (#189)의 외부 증거

> *"feedback_memory_sync_on_flow_end.md는 seed지만 매 세션 LLM 재해석 → 결정론적이지 않음"*

nexttui **BL-P2-085 사례** (2026-04-27 pause → 2026-04-28 resume):
- `devflow-state.md`(.gitignore됨) Phase 1만 기록
- auto-memory + code-plan.md는 Phase 1~5 done
- **수동 cross-check로 발견 + 수동 reconcile** — 즉 mid-cycle pause 시점에 sync skill이 안 탔다

### 가설
**"skill 호출 경로의 LLM 재해석 비결정성"**이 T2 / BL-092 / BL-097의 공통 근본 원인.
→ **BL-097의 5단계 결정론적 체크리스트 + 트리거 위치 보강**이 일반 해법 후보.

---

## 4. 통합 설계 가설 — "Session Boundary Sync"

| 항목 | 시점 | 역할 | 이슈 |
|---|---|---|---|
| BL-091 | review handoff | session-summary 공식화 | #176 |
| BL-092 | finishing + Resume | memory sync trigger | PR #178 (머지 완료) |
| BL-095 | handoff hypothesis | 원칙 명문화 (Phase 1 완료) | #183 |
| BL-095b | session-summary verification gate | Phase 2 | #184 |
| **BL-097** | **mid-cycle pause** | **3-way drift 방지** | #189 (신규) |
| Knowledge T2 | STORE 호출 | systematic-debugging trigger | (T2 Critical) |

**공통 패턴**: 세션 경계(시작/일시정지/재개/종료/리뷰) state↔memory↔git 동기화가 LLM 재해석에 의존 → 비결정성 → 누락.

**통합 후보 원칙**:
- finishing/pause/resume/store 어느 시점이든 **동일한 결정론적 체크리스트** 적용
- BL-097의 5단계가 abstract pattern: ① state sync ② memory update ③ index refresh ④ audit marker ⑤ 3-way cross-check
- Knowledge System T2는 ⑤의 cross-check가 STORE 트리거를 감지하는 형태

---

## 5. T+14 결정 3건 (BL-092)

원래 결정 항목 (메모리 `project_bl092_observation.md`):

1. **M1 강제 sync 전환?** (advisory→강제)
   - 데이터: skipped=0이라 advisory 유효성 판단 불가
   - **본질 문제**: prompt 자체가 0 → 트리거 위치 미스매치
   - → 강제 vs advisory 결정 보류, **트리거 위치 보강 선결**
2. **M3 SPEC boundary ADR 작성?**
   - SPEC_devflow_checkpoint.md(checkpoint-memorize)와 BL-092(세션 연속성) 책임 경계
   - 데이터 무관 설계 부채 → **작성 진행 권장**
3. **BL-091과 통합 설계?**
   - **BL-097까지 합쳐 4+1건 통합 후보**로 확장
   - 통합 시 단일 plan, 분리 시 4건 별도 plan + Knowledge T2 별도

---

## 6. 알려진 제약 / 반례 후보

- **단일 repo(nexttui) 관측**: nexttui 특이 패턴이 plugin 일반 문제로 해석될 위험. 절대값 임계는 OK이나 신호 해석은 보수적이어야.
- **단일 사례(BL-P2-085) 일반화 위험**: BL-097은 1건의 stale recovery에 기반. "사용자가 finishing 안 한다"는 일반화는 표본 부족.
- **Hook 반영 지연**: nexttui hook 적용은 4/14. 그 전 데이터는 file-edit 트리거 대상 외.
- **기각된 대안 재고려 금지** (handoff-context §4): 다중 repo 합산, 중앙집계 DEVFLOW_ROOT, 신규 greenfield 시뮬, `.devflow/` 신규, `skills/knowledge` 분리, `adr-index.json`, Thread 개념, "memory only" 철학, `docs/research/*` Decision 포함, `tests/*.py` Evidence 포함 — 전부 재제안 금지.

---

## 7. 자료 경로 (Codex가 직접 읽을 것)

### Phase 1·2 설계 문서
- `docs/plans/2026-04-13-knowledge-system-phase1-plan.md` — 특히 §`Phase 2 Re-evaluation Criteria` (1076행~)
- `docs/research/knowledgesystem/handoff-context.md` — 설계 의도 + 1·2차 debate 결과 + 기각된 대안 §4
- `docs/research/knowledgesystem/phase1-baseline.md` — plugin repo T0
- `docs/research/knowledgesystem/phase2-observation-plan.md` — nexttui T0 + 재측정 명령
- `docs/research/knowledgesystem/rollback-guide.md` — 5-level rollback
- `docs/research/knowledgesystem/phase1-overview.md` — Phase 1 사용자 영향
- `docs/research/knowledgesystem/knowledge-taxonomy.md` — 6 타입 taxonomy
- `docs/research/knowledgesystem/aidlc-knowledge-integration-plan.md` — 통합 전략 + 훅 설계
- `docs/research/knowledgesystem/executable-next-steps.md` — Change 1-6 patch

### BL-092 / 097 / 091 / 095 컨텍스트
- GitHub Issue #178 (BL-092 PR — 머지 완료)
- GitHub Issue #189 (BL-097 — mid-cycle pause skill, 본 호출 자료의 §3-4 핵심 입력)
- GitHub Issue #176 (BL-091)
- GitHub Issue #183 (BL-095 Phase 1 — 머지 완료)
- GitHub Issue #184 (BL-095b Phase 2)
- `docs/research/checkpoint-memorize/SPEC_devflow_checkpoint.md` — M3 ADR 대상

### 운영 데이터 (직접 grep 가능)
- nexttui: `/Users/jay.ahn/projects/infra/nexttui/devflow-docs/audit.md`
- plugin: `devflow-docs/audit.md`

---

## 8. 레드팀에게 요청하는 산출물

1. **Q1-Q5 각 질문에 대한 비판적 답** (예/아니오가 아닌 근거 + 반례)
2. **숨은 가정 / confirmation bias 명시적 식별**
3. **통합 vs 분리 결론** + 결론에 따른 plan 스코프 권고
4. **T2 Critical 해법 후보 1순위** (BL-097 패턴 적용 / 별도 가설 / 추가 측정 필요)
5. **반례·기각 대안 재제안 금지** (handoff-context §4 준수)
6. **Phase 2 plan 작성 시 반드시 포함할 의사결정 5-7개** 체크리스트

리뷰 결과는 **그대로 보존** (요약/수정 금지 — `external-review-handling` 스킬 적용).
