# 스킬 셀프 리뷰 결과 (2026-03-19)

> 27개 aidlc 스킬을 디자인 패턴 가이드 + 스킬 작성 가이드 기준으로 전수 리뷰한 결과.

## 리뷰 기준

| 기준 문서 | 검증 항목 |
|----------|----------|
| `_shared/patterns/skill-design-patterns.md` | 구조 패턴 적합성 (Tool Wrapper / Generator / Reviewer / Inversion / Pipeline) |
| `_shared/patterns/skill-writing-guide.md` | 자유도, CSO, progressive disclosure, 500줄 가이드라인 |
| `_shared/patterns/skill-pattern-catalog.md` | 행동 패턴 적합성 (Iron Law, Gate, Review Loop 등 7종) |
| `_shared/reviewers/skill-reviewer-prompt.md` | 구조/내용/CSO/구조패턴 검증 체크리스트 |

---

## 심각도별 집계

| 심각도 | 건수 |
|--------|------|
| Critical | 8건 |
| Important | 20건 |
| Minor | 39건 |

---

## Critical 이슈

| # | 스킬 | 이슈 |
|---|------|------|
| 1 | `functional-design` | 제목 `# Functional Design`이 frontmatter name `aidlc-functional-design`과 불일치 |
| 2 | `functional-design` | v0.1.0 스텁 수준 — Return 비표준, Review 모호, 필수 섹션 부재, Inception vs Construction 분류 혼동 |
| 3 | `finishing-a-development-branch` | `git add -p` (인터랙티브 모드) 사용 — Claude Code에서 실행 불가 |
| 4 | `brainstorming` | Trigger/Examples/Troubleshooting 필수 섹션 3개 모두 누락 |
| 5 | `writing-plans` | description CSO 위반 — "Use when..."으로 시작하지 않고 워크플로우 요약 포함 |
| 6 | `writing-plans` | Trigger/Examples/Troubleshooting 필수 섹션 3개 모두 누락 |
| 7 | `executing-plans` | Trigger/Examples/Troubleshooting 필수 섹션 3개 모두 누락 |
| 8 | `superpowers-tracking` | 스킬 미완성 (50줄, 프로세스 없음, 필수 섹션 전무, description과 기능 불일치) |

---

## Important 이슈

### CSO 위반

| 스킬 | 이슈 |
|------|------|
| `code-generation` | description에 내부 구현 상세("two-stage process") 노출 |
| `construction-orchestrator` | description에 내부 스테이지 구조 노출 |

### 필수 섹션 부재 (개별)

| 스킬 | 누락 섹션 |
|------|----------|
| `test-driven-development` | Trigger, Troubleshooting, Examples(1개뿐) |
| `subagent-driven-development` | Troubleshooting, Examples(1개뿐) |
| `build-and-test` | Examples |
| `using-devflow` | Examples |
| `using-git-worktrees` | Examples |
| `code-generation` | Troubleshooting |

### 구조/패턴 위반

| 스킬 | 이슈 |
|------|------|
| `using-git-worktrees` | orchestrator-only인데 Step 1에서 사용자에게 A/B 게이트 직접 제시 |
| `receiving-code-review` | 6단계 Pipeline에 명시적 게이트 선언 없음 ("DO NOT proceed..." 부재) |
| `user-stories` | skill-pattern-catalog에 Three-Mode(보조)로 매핑되어 있으나 구현에 Three-Mode 분기 없음 |
| `units-generation` | workflow-plan 템플릿에 depth 명시되나 SKILL.md에 depth별 동작 차이 없음 |
| `functional-design` | CSO description에 "unit"이라는 내부 용어 노출 |

---

## 공통 패턴 이슈

| 이슈 | 해당 스킬 수 | 심각도 | 비고 |
|------|------------|--------|------|
| `Trigger` 섹션 부재 | 25/27 | Important | orchestrator-only 예외 규칙 검토 필요 |
| `Examples` 섹션 부재/부족 | 23/27 | Important | 동일 |
| `Troubleshooting` 부재 또는 `Common Issues`로 명칭 불일치 | 22/27 | Minor | 명칭 통일 방침 결정 필요 |
| description에 한국어 키워드 부재 | 24/27 | Minor | user-invocable만 우선 보강 |

---

## 구조 패턴 매핑 결과

| 구조 패턴 | 해당 스킬 |
|----------|----------|
| **Pipeline** | using-devflow, inception-orchestrator, construction-orchestrator, systematic-debugging, verification-before-completion, receiving-code-review, dispatching-parallel-agents, subagent-driven-development, executing-plans, writing-skills |
| **Inversion** | brainstorming, requirements-analysis, nfr-requirements |
| **Generator** | code-generation, units-generation, user-stories, workflow-planning, application-design, writing-plans |
| **Reviewer** | requesting-code-review |
| **Tool Wrapper** | test-driven-development |
| **복합/미분류** | functional-design, workspace-detection, finishing-a-development-branch, using-git-worktrees, build-and-test, superpowers-tracking |

---

## 조치 계획 (S1~S6)

### S1: 즉시 수정 — 명확한 버그/위반

| 대상 | 수정 |
|------|------|
| `finishing-a-development-branch` | `git add -p` → 비인터랙티브 방식 |
| `writing-plans` | description CSO 수정 ("Use when..."으로 변경) |
| `functional-design` | 제목 불일치 수정 |
| `code-generation` | description에서 "two-stage process" 제거 |
| `construction-orchestrator` | description에서 내부 스테이지 구조 제거 |

### S2: 기준 정립 — skill-reviewer 예외 규칙 + 명칭 통일

| 결정 사항 |
|----------|
| orchestrator-only 스킬에 Trigger/Examples/Troubleshooting 필수 여부 |
| `Troubleshooting` vs `Common Issues` 명칭 통일 방침 |
| description 한국어 키워드 적용 범위 (user-invocable만 vs 전체) |

### S3: 미완성 스킬 처리

| 대상 | 조치 |
|------|------|
| `functional-design` | v0.1.0 → 완성도 보강 (Return 표준화, 섹션 추가, Inception/Construction 분류 확정) |
| `superpowers-tracking` | 완성 또는 비활성화 판단 |

### S4: 게이트/구조 보강

| 대상 | 수정 |
|------|------|
| `receiving-code-review` | Pipeline 게이트 선언 추가 ("DO NOT proceed...") |
| `systematic-debugging` | 2→3, 3→4 게이트 조건 명시 |

### S5: user-invocable 스킬 보강 (전반 6개)

| 대상 스킬 | 보강 내용 |
|----------|----------|
| `brainstorming` | Trigger + Examples 2개 + Troubleshooting 2개 |
| `writing-plans` | Trigger + Examples 2개 + Troubleshooting 2개 |
| `executing-plans` | Trigger + Examples 2개 + Troubleshooting 2개 |
| `test-driven-development` | Trigger 보강 + Examples 1개 추가 + Troubleshooting 2개 |
| `subagent-driven-development` | Examples 1개 추가 + Troubleshooting 2개 |
| `writing-skills` | description 한국어 키워드 추가 |

### S6: user-invocable 스킬 보강 (후반) + 한국어 키워드 일괄

| 대상 스킬 | 보강 내용 |
|----------|----------|
| `systematic-debugging` | description 한국어 키워드 |
| `verification-before-completion` | description 한국어 키워드 |
| `dispatching-parallel-agents` | description 한국어 키워드 |
| `finishing-a-development-branch` | description 한국어 키워드 |
| `receiving-code-review` | 금지 응답 한국어 표현 추가 |
| `using-devflow` | Examples 2개 추가 |
| 나머지 user-invocable 스킬 | description 한국어 키워드 일괄 |
