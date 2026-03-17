# 스킬 정합성 체크리스트

> 백로그 작업 시 해당 스킬/파일을 수정하면 여기서 관련 이슈를 확인하고 함께 수정한다.
> 수정 완료 시 `[x]`로 체크.

**분석일**: 2026-03-17

---

## HIGH — 즉시 해결

### H1: return_behavior 누락 (12개 스킬)

conventions에서 필수로 정의했지만 누락된 스킬. 해당 스킬 수정 시 함께 추가.

- [ ] `aidlc-brainstorming` — user-invocable, stop-with-gate 예상
- [x] `aidlc-dispatching-parallel-agents` — user-invocable ✅ (#9에서 수정)
- [x] `aidlc-executing-plans` — user-invocable ✅ (#9에서 수정)
- [ ] `aidlc-finishing-a-development-branch` — user-invocable, stop-with-gate 예상
- [ ] `aidlc-receiving-code-review` — user-invocable
- [x] `aidlc-subagent-driven-development` — user-invocable ✅ (#8에서 수정)
- [ ] `aidlc-superpowers-tracking` — user-invocable
- [ ] `aidlc-test-driven-development` — user-invocable
- [ ] `aidlc-verification-before-completion` — user-invocable
- [ ] `aidlc-writing-plans` — user-invocable
- [ ] `aidlc-writing-skills` — user-invocable
- [ ] `_utils/devflow-audit` — orchestrator-only
- [ ] `_utils/devflow-state` — orchestrator-only

### H2: description CSO 위반 (21개 스킬)

"Use when..."으로 시작해야 하는데 워크플로우/동작 설명으로 시작. 해당 스킬 수정 시 함께 수정.

- [x] `aidlc-application-design` — "Designs component..." → "Use when..." ✅ (#4에서 수정)
- [ ] `aidlc-brainstorming` — "아이디어를 설계로..." → "Use when..."
- [ ] `aidlc-build-and-test` — "Execute build and..." → "Use when..."
- [ ] `aidlc-code-generation` — "Two-stage process..." → "Use when..."
- [ ] `aidlc-construction-orchestrator` — "CONSTRUCTION Phase..." → "Use when..."
- [x] `aidlc-executing-plans` — "구현 계획을 별도..." → "Use when..." ✅ (#9에서 수정)
- [ ] `aidlc-functional-design` — "CONSTRUCTION 단계..." → "Use when..."
- [ ] `aidlc-inception-orchestrator` — "INCEPTION Phase..." → "Use when..."
- [ ] `aidlc-nfr-requirements` — "도메인 컨텍스트..." → "Use when..."
- [ ] `aidlc-requirements-analysis` — "Analyzes user requirements..." → "Use when..."
- [x] `aidlc-subagent-driven-development` — "구현 계획을 태스크별..." → "Use when..." ✅ (#8에서 수정)
- [ ] `aidlc-superpowers-tracking` — "세션 중 스킬/패턴..." → "Use when..."
- [ ] `aidlc-test-driven-development` — "TDD 원칙 강제..." → "Use when..."
- [ ] `aidlc-units-generation` — "Decomposes the system..." → "Use when..."
- [ ] `aidlc-user-stories` — "요구사항을 INVEST..." → "Use when..."
- [x] `aidlc-using-devflow` — "AIDLC Entry Orchestrator..." → "Use when..." ✅ (#10에서 수정)
- [ ] `aidlc-using-git-worktrees` — "Creates an isolated..." → "Use when..."
- [ ] `aidlc-workflow-planning` — "Determines which..." → "Use when..."
- [ ] `aidlc-workspace-detection` — "Scans the workspace..." → "Use when..."
- [ ] `_utils/devflow-audit` — "Appends interaction..." → "Use when..."
- [ ] `_utils/devflow-state` — "Reads and writes..." → "Use when..."

### H3: functional-design 모드 정의 불완전

- [ ] Together/Import/Skip 모드의 구현 로직 명시 (현재 참조만 있고 로직 없음)
- [ ] construction-orchestrator에서 모드 신호 전달 방식 명시

### H4: units-generation ↔ application-design 의존성 미명시

- [ ] application-design 스킵 시 units-generation 동작 규칙 명시
- [ ] workflow-plan.md의 Approved Stages에 의존성 표시

---

## MEDIUM — 워크플로우 안정성

### M1: code-generation PART 1 리뷰 depth 조건

- [x] PART 1(Plan)에서 Minimal 시 리뷰 스킵, Standard+ 시 code-plan-reviewer dispatch 명시 ✅ (#8에서 수정)

### M2: stop-no-gate 스킬의 중간 승인 패턴 불일치

- [x] conventions에서 stop-no-gate의 정확한 의미 명확화 (중간 사용자 입력 허용 여부) ✅ (#9에서 수정)

### M3: subagent-driven-development 태스크 순차 실행

- [ ] 태스크별 순차 실행 순서 명시 (Task 1 완전 완료 → Task 2 시작)

### M4: requirements-analysis QUESTIONS 모드 반환값

- [ ] QUESTIONS 모드의 Return to Orchestrator 형식에 "열린 질문: [N]개" 패턴 포함 명시

### M5: depth fallback 우선순위

- [x] conventions에 명시: 호출 텍스트 → workflow-plan Stage Depths → devflow-state Complexity ✅ (#9에서 수정)

### M6: using-git-worktrees 호출 주체

- [ ] inception-orchestrator에서 호출한다는 사실을 메타데이터 또는 SKILL.md에 반영

---

## LOW — 개선 사항

- [ ] **L1**: _shared/patterns/ 간 상호 참조 (three-mode ↔ hold-mechanism)
- [ ] **L2**: functional-design output_path 메타데이터 추가
- [ ] **L3**: user-stories IMPORT 모드 거부 메시지 명시
- [ ] **L4**: verification-before-completion과 TDD 관계 명확화

---

## 백로그 → 정합성 이슈 매핑

각 백로그 작업에서 함께 수정할 정합성 이슈:

| 백로그 이슈 | 수정 스킬 | 함께 처리할 정합성 이슈 |
|------------|----------|----------------------|
| #8 requesting-code-review | code-generation, conventions | M1, H1(해당 스킬), H2(해당 스킬) |
| #9 컨텍스트 격리 + #14 Instruction Priority | conventions, SDD, dispatching, executing-plans | M2, M3, M5, H1(해당 스킬), H2(해당 스킬) |
| #10 SessionStart 훅 | using-devflow | H1(해당 스킬), H2(해당 스킬) |
| #13 dev-playbook 보조 2종 | application-design, functional-design, nfr-requirements | H3, L2, H1(해당 스킬), H2(해당 스킬) |
| #1 workspace-detection | workspace-detection | H2(해당 스킬) |
| #2 planning 리뷰 | inception-orchestrator, workflow-planning | H4, M4, M6, H2(해당 스킬) |
| #4 design 리뷰 | inception-orchestrator, application-design | M2, H2(해당 스킬) |
| #6 정적분석 | construction-orchestrator, code-generation | M1, H2(해당 스킬) |
| #3 devflow-state 체크박스 | devflow-state, orchestrators | H1(devflow-state), H2(devflow-state) |
| #15 테스트 인프라 | 전체 스킬 description 검증 | H2 잔여 항목 일괄 처리 |
