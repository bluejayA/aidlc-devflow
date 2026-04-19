# Backlog

> **완료 항목 조회 방법:**
> - GitHub: [`is:issue is:closed`](https://github.com/bluejayA/aidlc-devflow/issues?q=is%3Aissue+is%3Aclosed) 필터
> - Claude: "완료된 백로그 항목 보여줘" 요청 (git history 검색)
> - Done/Closed 항목은 git history에 보존되어 있습니다.

---

## Next

- **BL-086**: aidlc-writing-plans에 mapping/매핑 검증 단계 추가 — Task 4 사고 재발 방지 [P2] [#155](https://github.com/bluejayA/aidlc-devflow/issues/155)
- **BL-088**: MSA 통합 audit 지원 — marker file / config-based scope discovery [P3] [#158](https://github.com/bluejayA/aidlc-devflow/issues/158) (Phase 2 후보; DEVFLOW_ROOT opt-in으로 MVP 대체)
- **BL-081**: 스킬 라이프사이클 관리 — skill_nature 태깅 + 경량화 체계 도입 [P2] [#145](https://github.com/bluejayA/aidlc-devflow/issues/145) (Phase 1 MVP 1,2번은 BL-085에 흡수, 3,4번 잔존)

> BL-085 (Knowledge System Phase 1)는 구현 완료 후 본 파일에서 제거 (git history로 추적).
> Baseline + Phase 2 trigger 평가 기준: `docs/research/knowledgesystem/phase1-baseline.md` 참조.

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
