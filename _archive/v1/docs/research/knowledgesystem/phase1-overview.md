# Knowledge System Phase 1 — 구현 개요와 사용자 영향

> **릴리스**: aidlc-devflow v1.10.0 (2026-04-13 머지, PR #157)
> **상태**: 실험적, 14일 관측 기간 (2026-04-13 ~ 2026-04-28)
> **본 문서 목적**: Phase 1이 무엇을 도입했는지, 그리고 사용자 관점에서 구현 전후로 무엇이 달라지는지를 정확히 정리.

---

## 1. 한 줄 요약

Phase 1은 **"미래 활용을 위한 데이터 수집·분류 시스템 구축"** 단계로, 사용자 즉각 효용은 audit 자동화 + STORE 자동 발동 두 가지뿐이고, 진짜 효용은 consumer repo에서 데이터가 누적되는 Phase 2부터 발생합니다.

---

## 2. 도입된 변경 (5건)

| 변경 | 내용 |
|------|------|
| **6-type taxonomy** | Decision / Solution / Pattern / Skill / Evidence / SessionState — frontmatter overlay로 기존 자산 재라벨링 |
| **Solution layer 활성화** | STORE 호출 owner를 `aidlc-systematic-debugging` 단독으로 이관 (옵션 α) |
| **L1 ingest hook** | `hooks/post-tool-file-edit` — Edit/Write/MultiEdit/NotebookEdit 시 `devflow-docs/audit.md` 자동 append |
| **Skill lifecycle 분류** | `skill_nature` 태깅: compensation 4 / amplification 10 / hybrid 11 / null 6 (전체 31개) |
| **Pattern frontmatter 강화** | 33개 파일에 `type: pattern` + `applies_to` + `last_validated` 등 5 필드 |

### 환경 변수 (선택)

| 변수 | 용도 |
|------|------|
| `DEVFLOW_ROOT` | MSA/multi-repo 프로젝트에서 공통 audit root 지정 (opt-in). 절대경로 + 존재 디렉토리 + 루트(`/`) 거부 검증 |
| `DEVFLOW_HOOK_DISABLED` | 긴급 무력화 kill switch. 설정 시 hook 0.1ms 안에 exit 0 |

---

## 3. 사용자 관점에서 향상된 것 (구현 전 → 후)

### 3.1 자동으로 작동하는 것 (당장 체감 가능)

| 영역 | 구현 전 | 구현 후 |
|------|--------|--------|
| **파일 수정 활동 기록** | 스킬이 의도적으로 `devflow-audit` 호출해야 기록 → 누락 빈번 | Edit/Write/MultiEdit 발생 시마다 `audit.md`에 자동 entry. 사용자/스킬 개입 0 |
| **세션 상태 신선도** | `devflow-state.md`의 `Last Updated`가 stale 상태 자주 발생 | 모든 파일 수정 시 hook이 자동 갱신 |
| **디버깅 지식 축적** | `systematic-debugging` 완료 후 STORE 호출이 선택적 → `solutions/`가 0건 그대로 | root_cause 확정 + fix 검증 완료 시 **무조건 STORE 발동**. `devflow-docs/solutions/{category}/<slug>.md`에 자동 누적 |

### 3.2 분류·메타데이터 강화 (당장은 안 보임, 미래 효용)

| 영역 | 구현 전 | 구현 후 |
|------|--------|--------|
| **Skill 분류** | skill 간 성격 구분 없음 (모두 동등) | 31개 skill에 `skill_nature` 부여. 모델 발전 시 어떤 skill을 경량화할지 데이터 기반 의사결정 가능 |
| **Pattern 추적성** | pattern 파일 frontmatter 약함 (`type` / `applies_to` / `status` 부재) | 33개 파일에 `applies_to`, `status`, `last_validated` 등 표준화. stale detection / validator 도입 기반 |
| **지식 멘탈 모델** | "이 산출물 어디 두지?" 모호 | 6-type taxonomy로 명시 (Decision은 `docs/plans/`, Solution은 `solutions/`, Pattern은 `_shared/` ...) |

---

## 4. 사용자가 **체감하지 못하는** 것 (정직하게)

- 새로운 slash command 없음
- 스킬 호출 패턴 동일
- 대화 흐름 변화 없음
- "오, 이게 편해졌네" 할 만한 직접적 UX 향상 거의 없음

Phase 1은 본질적으로 **인프라 + 분류 작업**입니다. 새 명령이나 워크플로우는 추가하지 않았고, 기존 자산을 6개 유형으로 재라벨링하고 자동 데이터 누적 hook과 디버깅 지식 자동 저장 메커니즘만 추가했습니다.

---

## 5. 진짜 가치는 어디서 나오나 (Phase 2+)

1. **Knowledge Compounding** — `solutions/`가 누적되면 systematic-debugging이 과거 사례를 자동 검색·재활용. 같은 버그를 두 번 풀지 않게 됨.
2. **관측성** — `audit.md` 데이터로 token cost, skill 사용 패턴, gate 발동률 분석 가능 (지금 baseline 측정이 그 첫걸음).
3. **유지보수성** — pattern frontmatter로 6개월 후 어떤 pattern이 stale인지 자동 식별.
4. **모델 발전 대응** — `skill_nature`로 모델 자체가 잘하게 된 영역의 skill을 경량화하거나 제거하는 의사결정 가능.

이래서 baseline 측정이 중요합니다 — Phase 1이 진짜 효용을 만들고 있는지(예: `solutions/`가 실제로 쌓이는지, audit이 의미 있는 신호를 주는지) **데이터로 증명해야** 다음 단계 투자를 정당화할 수 있습니다.

---

## 6. 관측 기간

v1.10.0 릴리스 후 14일간 운영 데이터 수집. **2026-04-28 시점에 Phase 2 방향 결정 예정**.

관측 대상 repo: `nexttui` (Tier 1 단일, OR 조건). 자세한 관측 설계는 [`phase2-observation-plan.md`](phase2-observation-plan.md) 참조.

---

## 7. 관련 GitHub 이슈 / PR

### 구현 PR

- [**PR #157**](https://github.com/bluejayA/aidlc-devflow/pull/157) — Knowledge System Phase 1 구현 (2026-04-13 머지, merge commit `0201e9a`). 9 commits, verify-change-1~6 PASS, pytest 273 passed, Success Signals 12/12.

### 구현 이슈 (closed)

- [**#154**](https://github.com/bluejayA/aidlc-devflow/issues/154) (BL-085) — Phase 1 구현 트래킹 이슈. PR #157로 closed.

### 후속 작업 (post-merge follow-up, open)

- [**#155**](https://github.com/bluejayA/aidlc-devflow/issues/155) (BL-086) — `aidlc-writing-plans` mapping 검증. Phase 1 Task 4에서 `applies_to` 매핑이 초기 ~10/33만 정확했던 사고의 재발 방지.
- [**#156**](https://github.com/bluejayA/aidlc-devflow/issues/156) (BL-087) — hook 보안 가드 강화. Codex 리뷰에서 발견된 8건 중 일부는 PR #157에 흡수, 잔여 강화 작업.

### 선행 / 잔여 백로그

- [**#145**](https://github.com/bluejayA/aidlc-devflow/issues/145) (BL-081) — Phase 1 MVP 1, 2번 (skill_nature 분류 + STORE owner 단독화)은 본 릴리스에 흡수. **3, 4번 (Compensation Decay + validator) 잔존** — Phase 2 범위 후보.

---

## 8. 관련 문서

- **Rollback 가이드**: [`rollback-guide.md`](rollback-guide.md) — 5-level 되돌림 (Kill switch → 전체 revert → Abandon)
- **Phase 1 baseline (plugin repo 기준)**: [`phase1-baseline.md`](phase1-baseline.md) — 트리거 T1-T10 평가 기준점 (T0 = 2026-04-13)
- **Phase 2 관측 설계 (consumer repo 기준)**: [`phase2-observation-plan.md`](phase2-observation-plan.md) — nexttui T0 snapshot + 재측정 명령
- **설계 의도 + 과거 debate**: [`handoff-context.md`](handoff-context.md)
- **6-type taxonomy 상세**: [`knowledge-taxonomy.md`](knowledge-taxonomy.md)
- **통합 전략**: [`aidlc-knowledge-integration-plan.md`](aidlc-knowledge-integration-plan.md)
