# 스킬 정합성 체크리스트

> 백로그 작업 시 해당 스킬/파일을 수정하면 여기서 관련 이슈를 확인하고 함께 수정한다.
> 수정 완료 시 `[x]`로 체크.

**분석일**: 2026-03-17
**최종 업데이트**: 2026-03-17 (일괄 수정 완료)

---

## HIGH — 즉시 해결

### H1: return_behavior 누락 — ✅ 전부 해결

- [x] `aidlc-brainstorming` — stop-with-gate ✅ (일괄 수정)
- [x] `aidlc-dispatching-parallel-agents` — stop-no-gate ✅ (#9에서 수정)
- [x] `aidlc-executing-plans` — stop-no-gate ✅ (#9에서 수정)
- [x] `aidlc-finishing-a-development-branch` — stop-with-gate ✅ (일괄 수정)
- [x] `aidlc-receiving-code-review` — stop-no-gate ✅ (일괄 수정)
- [x] `aidlc-subagent-driven-development` — stop-no-gate ✅ (#8에서 수정)
- [x] `aidlc-superpowers-tracking` — stop-no-gate ✅ (일괄 수정)
- [x] `aidlc-test-driven-development` — stop-no-gate ✅ (일괄 수정)
- [x] `aidlc-verification-before-completion` — stop-no-gate ✅ (일괄 수정)
- [x] `aidlc-writing-plans` — stop-no-gate ✅ (일괄 수정)
- [x] `aidlc-writing-skills` — stop-no-gate ✅ (일괄 수정)
- [x] `_utils/devflow-audit` — stop-no-gate ✅ (일괄 수정)
- [x] `_utils/devflow-state` — stop-no-gate ✅ (일괄 수정)

### H2: description CSO 위반 — ✅ 전부 해결

- [x] `aidlc-application-design` ✅ (#4에서 수정)
- [x] `aidlc-brainstorming` ✅ (일괄 수정)
- [x] `aidlc-build-and-test` ✅ (일괄 수정)
- [x] `aidlc-code-generation` ✅ (일괄 수정)
- [x] `aidlc-construction-orchestrator` ✅ (일괄 수정)
- [x] `aidlc-executing-plans` ✅ (#9에서 수정)
- [x] `aidlc-functional-design` ✅ (일괄 수정)
- [x] `aidlc-inception-orchestrator` ✅ (일괄 수정)
- [x] `aidlc-nfr-requirements` ✅ (일괄 수정)
- [x] `aidlc-requirements-analysis` ✅ (일괄 수정)
- [x] `aidlc-subagent-driven-development` ✅ (#8에서 수정)
- [x] `aidlc-superpowers-tracking` ✅ (일괄 수정)
- [x] `aidlc-test-driven-development` ✅ (일괄 수정)
- [x] `aidlc-units-generation` ✅ (일괄 수정)
- [x] `aidlc-user-stories` ✅ (일괄 수정)
- [x] `aidlc-using-devflow` ✅ (#10에서 수정)
- [x] `aidlc-using-git-worktrees` ✅ (일괄 수정)
- [x] `aidlc-workflow-planning` ✅ (일괄 수정)
- [x] `aidlc-workspace-detection` ✅ (일괄 수정)
- [x] `_utils/devflow-audit` ✅ (일괄 수정)
- [x] `_utils/devflow-state` ✅ (일괄 수정)

### H3: functional-design 모드 정의 — ✅ 해결

- [x] Together/Import/Skip 모드 구현 로직 명시 ✅ (일괄 수정)
- [x] construction-orchestrator 모드 신호 전달 → Orchestrator-Centric 규약 준수 명시 ✅

### H4: units-generation ↔ application-design 의존성 — ✅ 해결

- [x] application-design 스킵 시 units-generation 동작 규칙 명시 ✅ (일괄 수정)
- [x] requirements.md 기반 폴백 로직 추가 ✅

---

## MEDIUM — 워크플로우 안정성

- [x] **M1**: code-generation PART 1 리뷰 depth 조건 ✅ (#8에서 수정)
- [x] **M2**: stop-no-gate 정의 명확화 ✅ (#9에서 수정)
- [x] **M3**: SDD 태스크 순차 실행 명시 ✅ (일괄 수정)
- [x] **M4**: requirements-analysis QUESTIONS 모드 반환값 ✅ (일괄 수정)
- [x] **M5**: depth fallback 우선순위 ✅ (#9에서 수정)
- [x] **M6**: using-git-worktrees 호출 주체 ✅ (일괄 수정)

---

## LOW — 개선 사항

- [x] **L1**: _shared/patterns/ 간 상호 참조 ✅ (일괄 수정 — hold-mechanism에 three-mode 참조 추가)
- [x] **L2**: functional-design output_path — 이미 존재 확인 ✅
- [x] **L3**: user-stories IMPORT 모드 거부 메시지 ✅ (일괄 수정)
- [x] **L4**: verification-before-completion과 TDD 관계 ✅ (일괄 수정)

---

## 전체 완료 ✅

모든 정합성 이슈가 해결되었습니다. (2026-03-17)
