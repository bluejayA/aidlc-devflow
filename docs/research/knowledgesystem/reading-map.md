# Knowledge System — Reading Map

> **목적**: 현재 `docs/research/knowledgesystem/` 아래 문서들의 생성 순서·역할·참조 관계를 한눈에 파악하기 위한 **수동 네비게이션 맵**.
> **상태**: 임시 수동 버전. 향후 자동 생성(Mermaid/GRAPH_REPORT 자동화)으로 대체 예정 — `graphify-inspired-ideas.md` §2.2 참조.
> **최종 갱신**: 2026-04-15

---

## 1. 목적별 빠른 진입점

| "이것이 궁금하다면..." | 먼저 읽을 문서 |
|----------------------|--------------|
| Phase 1이 뭘 했는지 사용자 관점 요약 | [`phase1-overview.md`](phase1-overview.md) |
| 왜 이렇게 설계했는지 (debate 이력) | [`handoff-context.md`](handoff-context.md) |
| 6-type 분류가 정확히 무슨 뜻인지 | [`knowledge-taxonomy.md`](knowledge-taxonomy.md) |
| 통합 전략 (A+C 하이브리드) 전체 그림 | [`aidlc-knowledge-integration-plan.md`](aidlc-knowledge-integration-plan.md) |
| Phase 2 평가를 시작할 준비 | [`phase2-observation-plan.md`](phase2-observation-plan.md) |
| 뭔가 잘못됐을 때 되돌림 | [`rollback-guide.md`](rollback-guide.md) |
| 다음 단계 아이디어 후보 (graphify 차용) | [`graphify-inspired-ideas.md`](graphify-inspired-ideas.md) |

---

## 2. 생성 순서 (timeline)

| 생성일 | 문서 | 배경 |
|--------|------|------|
| **2026-04-13** (Phase 1 설계일) | `aidlc-devflow-context-v2.1.md` | 설계 컨텍스트 스냅샷 (v1.9.0 기준 자산 현황) |
| 2026-04-13 | `PROMPT-claude-code-knowledge-integration.md` | 레드팀 프롬프트 (설계 제약 주입용) |
| 2026-04-13 | `SPEC-knowledge-layer-sprint1-v0.3.md` | 초기 사양 (이후 integration-plan으로 수렴) |
| 2026-04-13 | `NOTE-knowledge-tier-multi-team-sprint3.md` | Sprint 3+ 멀티팀 티어 아이디어 (Phase 1 범위 밖) |
| 2026-04-13 | `knowledge-taxonomy.md` ★ | **6-type taxonomy 확정** |
| 2026-04-13 | `aidlc-knowledge-integration-plan.md` ★ | **통합 전략 (A+C)** |
| 2026-04-13 | `executable-next-steps.md` | Change 1-6 실행 상세 |
| 2026-04-13 | `handoff-context.md` | 설계 의도 + debate 보존 |
| **2026-04-13 23:36** (구현 직후) | `phase1-baseline.md` | plugin repo T0 측정 |
| **2026-04-14 08:37** | `rollback-guide.md` | 5-level 되돌림 절차 |
| **2026-04-15 09:11** (PR #163 머지) | `phase1-overview.md` ★ | **구현 완료 후 사용자 영향 요약** |
| 2026-04-15 09:11 | `phase2-observation-plan.md` ★ | **consumer repo(nexttui) 관측 설계** |
| **2026-04-15** (본 문서 + 동시 작성) | `graphify-inspired-ideas.md` | Phase 2+ 차용 아이디어 |
| 2026-04-15 | `reading-map.md` | (본 문서) |

(★ = 주요 진입점)

---

## 3. 역할 분류

### 3.1 설계 단계 (Phase 1 INCEPTION)

> 무엇을 만들지 결정한 근거. **Phase 1 완료 후 역사적 레퍼런스**로만 참조.

- `aidlc-devflow-context-v2.1.md` — 설계 시점 자산 현황 스냅샷
- `PROMPT-claude-code-knowledge-integration.md` — 레드팀 제약 주입용 prompt
- `SPEC-knowledge-layer-sprint1-v0.3.md` — 초기 사양 (integration-plan에 흡수됨)
- `NOTE-knowledge-tier-multi-team-sprint3.md` — Sprint 3+ 범위 외 아이디어 메모

### 3.2 확정 설계 (Phase 1 CONSTRUCTION 근거)

> 구현이 이 문서를 근거로 이루어짐. **재구현/롤백 시 재참조**.

- `knowledge-taxonomy.md` — 6-type 분류 정의 ★
- `aidlc-knowledge-integration-plan.md` — 통합 전략 + 디렉토리 구조 ★
- `executable-next-steps.md` — Change 1-6 실행 상세 patch
- `handoff-context.md` — 왜 그 선택을 했는지 (debate 보존)

### 3.3 구현 완료 후 (Phase 2 진입 필수)

> Phase 2 재평가 절차의 **측정 기준점 + 실행 자료**.

- `phase1-overview.md` — 구현 전후 사용자 영향 요약 (진입점) ★
- `phase1-baseline.md` — plugin repo T0 = 2026-04-13
- `phase2-observation-plan.md` — consumer repo nexttui T0 = 2026-04-14, 재측정 명령 ★
- `rollback-guide.md` — 5-level 되돌림 (Kill switch → 전체 revert → Abandon)

### 3.4 미래 방향 (Phase 2 plan 작성 시 참조)

- `graphify-inspired-ideas.md` — 차용 후보 (Evidence tagging / GRAPH_REPORT / pre-read hook 등)
- `reading-map.md` — (본 문서, 수동 네비게이션)

---

## 4. 의존 관계 (무엇을 읽으려면 무엇을 먼저?)

```
aidlc-devflow-context-v2.1        [설계 시점 현황]
        │
        ├─► knowledge-taxonomy ◄── PROMPT-claude-code-knowledge-integration
        │            │               (레드팀 제약 주입)
        │            ▼
        └─► aidlc-knowledge-integration-plan
                     │
                     ├─► executable-next-steps
                     │         │
                     │         ▼
                     │   [PR #157 구현]
                     │         │
                     │         ▼
                     ├─► phase1-baseline (plugin repo T0)
                     │         │
                     │         ▼
                     ├─► rollback-guide
                     │
                     └─► handoff-context ◄── (Phase 2 평가 시 필수)
                               │
                               ▼
                         phase1-overview (사용자 영향 요약)
                               │
                               ▼
                         phase2-observation-plan (consumer repo nexttui T0)
                               │
                               ▼
                         graphify-inspired-ideas (차용 후보)
                               │
                               ▼
                         [Phase 2 plan 작성 — 미완]

SPEC-knowledge-layer-sprint1-v0.3  [흡수됨, history]
NOTE-knowledge-tier-multi-team-sprint3  [Sprint 3+, 범위 외]
```

### 핵심 Reading Path

**신규 참여자 (Phase 1 전체 이해)**:
1. `phase1-overview.md` — 사용자 관점 요약
2. `handoff-context.md` — 왜 이렇게?
3. `knowledge-taxonomy.md` — 분류 체계
4. `aidlc-knowledge-integration-plan.md` — 전체 전략

**Phase 2 평가자**:
1. `docs/plans/2026-04-13-knowledge-system-phase1-plan.md` §Phase 2 Re-evaluation Criteria
2. `phase2-observation-plan.md` — 재측정 명령
3. `phase1-baseline.md` — T0 비교
4. `handoff-context.md` — 원설계 의도 복원
5. `graphify-inspired-ideas.md` — 새 아이디어 후보

**Rollback 결정자**:
1. `rollback-guide.md` — 5-level 절차
2. `phase1-overview.md` §구현된 변경 — 되돌릴 범위 파악
3. `handoff-context.md` §기각된 대안 — 대체 경로 확인

---

## 5. 외부 연결 (knowledgesystem/ 밖)

| 대상 | 역할 |
|------|------|
| [`docs/plans/2026-04-13-knowledge-system-phase1-plan.md`](../../plans/2026-04-13-knowledge-system-phase1-plan.md) | Phase 1 실행 plan (이 문서들의 실제 구현 계획) |
| [`docs/research/2026-04-06-skill-lifecycle-strategy.md`](../2026-04-06-skill-lifecycle-strategy.md) | BL-081 skill_nature 분류의 원설계 |
| [PR #157](https://github.com/bluejayA/aidlc-devflow/pull/157) | Phase 1 구현 (2026-04-13 merged) |
| [PR #163](https://github.com/bluejayA/aidlc-devflow/pull/163) | phase1-overview + phase2-observation-plan 작성 |
| [PR #164](https://github.com/bluejayA/aidlc-devflow/pull/164) | plan 문서에 신규 docs 참조 링크 추가 |
| [Issue #154 (BL-085)](https://github.com/bluejayA/aidlc-devflow/issues/154) | Phase 1 구현 트래킹 (closed) |
| [Issue #145 (BL-081)](https://github.com/bluejayA/aidlc-devflow/issues/145) | skill_nature 1,2번 흡수. 3,4번 잔존 |
| [Issue #155 (BL-086)](https://github.com/bluejayA/aidlc-devflow/issues/155) | aidlc-writing-plans mapping 검증 (후속) |
| [Issue #156 (BL-087)](https://github.com/bluejayA/aidlc-devflow/issues/156) | hook 보안 가드 강화 (후속) |

---

## 6. 갱신 정책

본 문서는 **수동 유지**. 새 문서 추가·삭제 시 함께 갱신. 자동화는 Phase 2에서 `graphify-inspired-ideas.md` §2.2 의사결정 후 결정.

**갱신 트리거**:
- 신규 knowledgesystem 문서 생성
- 문서 삭제 또는 대체
- Phase 2 plan 작성 완료 (당시 시점 스냅샷 포함)

stale 위험 수용. 주요 진입점(★ 표시 4개) 중 하나라도 틀리면 먼저 수정.
