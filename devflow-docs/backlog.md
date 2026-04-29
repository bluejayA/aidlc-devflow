# Backlog

> **완료 항목 조회 방법:**
> - GitHub: [`is:issue is:closed`](https://github.com/bluejayA/aidlc-devflow/issues?q=is%3Aissue+is%3Aclosed) 필터
> - Claude: "완료된 백로그 항목 보여줘" 요청 (git history 검색)
> - Done/Closed 항목은 git history에 보존되어 있습니다.

---

## Next

- **BL-098**: systematic-debugging audit emit 일관성 fix — 2종 prefix(`-invoked` / `-completed`)만. memory-sync 등 다른 skill과 일관 (사용 경험 fix, measurement 인프라 아님). 2026-04-29 scope 축소 [P2] [#191](https://github.com/bluejayA/aidlc-devflow/issues/191)
- **BL-086**: aidlc-writing-plans에 mapping/매핑 검증 단계 추가 — Task 4 사고 재발 방지 [P2] [#155](https://github.com/bluejayA/aidlc-devflow/issues/155)
- **BL-088**: MSA 통합 audit 지원 — marker file / config-based scope discovery [P3] [#158](https://github.com/bluejayA/aidlc-devflow/issues/158) (Phase 2 후보; DEVFLOW_ROOT opt-in으로 MVP 대체)
- **BL-081**: 스킬 라이프사이클 관리 — skill_nature 태깅 + 경량화 체계 도입 [P2] [#145](https://github.com/bluejayA/aidlc-devflow/issues/145) (Phase 1 MVP 1,2번은 BL-085에 흡수, 3,4번 잔존)
- **BL-095**: Handoff Strategy: "Handoff = hypothesis" 원칙 명문화 — Phase 1만 (Phase 2는 BL-095b) [P2] [#183](https://github.com/bluejayA/aidlc-devflow/issues/183)
- **BL-095b**: Handoff Strategy: session-summary verification gate (Phase 2, evidence=산출물 디렉터리+git log) [P2] [#184](https://github.com/bluejayA/aidlc-devflow/issues/184)
- **BL-097**: `aidlc-pausing-a-session` 스킬 — mid-cycle stop checklist + 3-way sync (`devflow-state.md` / project auto-memory / git log) — `aidlc-finishing-a-development-branch`의 mid-cycle 형제. 5단계 체크리스트 (state 갱신 / memory 정밀 / 인덱스 / audit commit / 3-way verify) + drift 시 commit 거부. `aidlc-using-devflow` Resume Flow에 자동 drift detect 추가. seed=nexttui BL-P2-085 stale recovery (2026-04-28). 별도 BL 후보: `devflow-state.md` gitignore 정책 재검토 [P2] [#189](https://github.com/bluejayA/aidlc-devflow/issues/189)

> **2026-04-29 frame 전환 + BL-097 단순화**: Knowledge System Phase 2 측정 인프라 작업 stop. devflow 가치 검증을 시스템 측정 → 사용 경험 회고로 전환. BL-097(mid-cycle pause)은 정보 분해 분석으로 5단계 → 2단계 자동화 + state.md advisory cache 격하로 단순화 (코드 변경 0). 상세: `memory/user_devflow_focus_shift.md` / `feedback_simple_first_decomposition.md` / `docs/guide/operator-guide.md` §7. Closed: BL-097 (#189) / BL-099 (#192). T+28 routine disabled.

---

## Graduated (별도 repo로 분리됨)

- **BL-031**: deployment-prep 독립 스킬 → [bluejayA/devflow-k8s-deploy](https://github.com/bluejayA/devflow-k8s-deploy) repo로 분리 (2026-04-15). 이름 변경: `deployment-prep` → `devflow-k8s-deploy`. Tracking: [devflow-k8s-deploy#1](https://github.com/bluejayA/devflow-k8s-deploy/issues/1). 원본 이슈: [#41 closed](https://github.com/bluejayA/aidlc-devflow/issues/41)

---

## Open

- **BL-042**: 행동 테스트 계층 (Layer 2) — LLM 기반 스킬 동작 검증 [P2] [#61](https://github.com/bluejayA/aidlc-devflow/issues/61)
- **BL-044**: Multi-Unit Construction Agent Teams — 독립 유닛 병렬 구현 + 인터페이스 조율 [P2] [#70](https://github.com/bluejayA/aidlc-devflow/issues/70)
- **BL-045**: dispatching-parallel-agents Agent Teams 강화 — 실행 중 충돌 감지/조율 [P2] [#71](https://github.com/bluejayA/aidlc-devflow/issues/71)
- **BL-052**: Playwright E2E 자동 검증 + 평가기 비대칭 도구 설계 [P2] [#92](https://github.com/bluejayA/aidlc-devflow/issues/92)
- **BL-084**: Mock vs Real adapter 테스트 갭 + Reachable stub 탐지 (선행: BL-082 ✅) [P2] [#152](https://github.com/bluejayA/aidlc-devflow/issues/152)
- **BL-089**: aidlc-cost-review 스킬 — LLM/인프라 비용 효율성 리뷰 (performance는 quality-reviewer 확장으로 대체) [P2] [#174](https://github.com/bluejayA/aidlc-devflow/issues/174)
- **BL-090**: 정합성 linter — consistency-check 스크립트 + git pre-commit hook MVP (감사 N=13 최대 friction 대응) [P2] [#175](https://github.com/bluejayA/aidlc-devflow/issues/175)
- **BL-091**: Knowledge System — review-deferred evidence prefix + session-summary 공식화 (Codex adversarial 후 P1→P2 하향, T+14 Phase 2 plan 대기) [P2] [#176](https://github.com/bluejayA/aidlc-devflow/issues/176)
- **BL-096**: Handoff Strategy: in-session 관리 가이드 (Tier 1) — /compact focus, 토큰 임계점. 093/094/095 적용 후 4주 관측(~2026-05-22) 후 재평가 [P3] [#185](https://github.com/bluejayA/aidlc-devflow/issues/185)


---

## Someday

- **BL-053**: audit 기반 하네스 최적화 + 비용-품질 메트릭 [P3] [#93](https://github.com/bluejayA/aidlc-devflow/issues/93)
- **BL-054**: 모델별 게이트 프로파일 — 동적 하네스 단순화 [P3] [#94](https://github.com/bluejayA/aidlc-devflow/issues/94)
- **BL-055**: 리뷰 ROI 자동화 — risk score 기반 리뷰 강도 동적 조절 [P3] [#95](https://github.com/bluejayA/aidlc-devflow/issues/95)
- **BL-057**: Knowledge Compounding Option B — workflow-planning 솔루션 선검색 [P3] [#97](https://github.com/bluejayA/aidlc-devflow/issues/97)
- **BL-058**: Self-Healing × Knowledge Compounding 통합 — 경험 기반 자동 수정 [P3] [#98](https://github.com/bluejayA/aidlc-devflow/issues/98)
- **BL-017**: infrastructure-design 스킬 [P3] [#37](https://github.com/bluejayA/aidlc-devflow/issues/37)
- **BL-019**: 장기 컨셉 — C4 Model, operations phase [P3] [#39](https://github.com/bluejayA/aidlc-devflow/issues/39)
- **BL-068**: units 위상 정렬 검증 게이트 [P3] [#113](https://github.com/bluejayA/aidlc-devflow/issues/113)
- **BL-069**: auto-fix 에러 분류 정교화 [P3] [#114](https://github.com/bluejayA/aidlc-devflow/issues/114)
- **BL-071**: workflow-planning 다이어그램 선택 접근법 반영 [P3] [#116](https://github.com/bluejayA/aidlc-devflow/issues/116)
- **BL-073**: 컨텍스트 누적 최적화 — 스테이지별 점진 로딩 [P3] [#118](https://github.com/bluejayA/aidlc-devflow/issues/118)
