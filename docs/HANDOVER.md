# 인수인계 문서

> 작성일: 2026-04-02 | 플러그인 버전: v1.6.0

---

## 프로젝트 개요

AI-DLC 방법론을 오케스트레이터 중심 아키텍처로 구현한 Claude Code 개발 워크플로우 플러그인.
2026-03-10부터 개발 시작, 27개 스킬 + 3개 유틸리티 + 5개 리뷰 에이전트 + 269개 테스트.

### 온보딩 필독 문서

| 순서 | 문서 | 설명 |
|------|------|------|
| 1 | [how-it-works.md](guide/how-it-works.md) | 기술 용어 없이 전체 흐름 이해 |
| 2 | [user-guide.md](guide/user-guide.md) | 시작, 질문 방식, 게이트, 독립 스킬 |
| 3 | [architecture.md](guide/architecture.md) | 3단 위임 체인, 스킬 패턴 7종 |
| 4 | [operator-guide.md](guide/operator-guide.md) | 기술 카탈로그, 질문 원칙, NFR 프리셋 커스터마이즈 |
| 5 | [consistency-checklist.md](guide/consistency-checklist.md) | 스킬 수정 시 정합성 검증 체크리스트 |
| 6 | [nfr-domain-presets.md](guide/nfr-domain-presets.md) | CLAUDE.md 기반 NFR 도메인 프리셋 예제 |

---

## 현재 상태

### 완료된 주요 마일스톤

| 버전 | 내용 |
|------|------|
| v0.5.0 | brainstorming 패턴 + Review Framework + Token 최적화 |
| v0.6.0 | 토큰 효율화 리팩토링 |
| v0.7.0 | GitHub Actions 마켓플레이스 동기화 |
| v0.8.0 | Brownfield 분석 (workspace-detection) |
| v0.9.0 | Session Continuity + 태스크 재검증 + TDD 명시 |
| v1.0.0 | Superpowers 독립 구현 + 코드 리뷰 체계 + 훅 시스템 |
| v1.1.0 | 메타 태그 시스템 + 테스트 인프라 Phase 2 |
| v1.2.0 | Agent-Council 리뷰 인프라 + application-design/code 리뷰 |
| v1.3.0 | Code Review Agent Teams (R3) + Distrust by Default |
| v1.4.1 | Verification Contract + Self-Healing Loop |
| v1.5.0 | SDD 기본화 + 정량 루브릭 + Distrust by Default + Knowledge Compounding |
| v1.6.0 | P1 Sprint (게이트 UX 3건) + 워크스페이스 캐시 + 백로그 재설계 + 상태 전환 문서화 |

### 코드 품질

- 테스트: 269개 전체 통과 (`bash tests/run-all.sh`)
- 스킬 메타데이터 정합성: 100%
- 테스트 인프라: 12개 테스트 파일 + 20개 시나리오 (YAML)

---

## 백로그 현황

백로그 파일: `devflow-docs/backlog.md` (Next/Open/Someday 3단계)
GitHub Issues: [`bluejayA/aidlc-devflow`](https://github.com/bluejayA/aidlc-devflow/issues)

- **Next**: 1건 (BL-031 deployment-prep)
- **Open**: 4건 (대규모 기능 — Agent Teams, LLM 행동 테스트, Playwright E2E)
- **Someday**: 12건

GitHub 연동은 CLAUDE.md의 `<!-- github-issues: enabled -->` 설정으로 제어.

---

## 핵심 규칙

### 반드시 지켜야 할 것

1. **A/B 게이팅**: devflow 스테이지 완료 시 사용자가 B를 선택하기 전까지 다음 스테이지 진행 금지
2. **TDD Iron Law**: 실패 테스트 없이 프로덕션 코드 작성 금지
3. **증거 우선**: 완료 주장 전 반드시 검증 실행
4. **정합성 체크**: 스킬 수정 시 `docs/guide/consistency-checklist.md` 확인
5. **백로그-GitHub 연동** (`github-issues: enabled` 시): 커밋 시 `refs #N` / `closes #N` + 이슈 코멘트 + 완료 항목 백로그에서 제거
6. **재검증 리밋**: 세션 재개 재검증 최대 2회, 디버깅 루프 최대 3회

### 테스트 실행

```bash
# 전체 테스트 (269개)
bash tests/run-all.sh

# 개별 테스트
pytest tests/test_meta_tag_format.py    # 메타 태그 형식
pytest tests/test_graph_validator.py    # 그래프 구조
pytest tests/test_routing_engine.py     # 라우팅 로직
pytest tests/test_step_order.py         # 스텝 순서
pytest tests/test_construction_k_gate.py # K-gate + 리뷰 게이트
pytest tests/test_verification_contract.py # Verification Contract
pytest tests/test_quantitative_rubric.py # 정량 루브릭
pytest tests/test_devflow_solutions.py  # Knowledge Compounding
```

### 주요 파일 위치

| 항목 | 경로 |
|------|------|
| 플러그인 설정 | `.claude-plugin/plugin.json` |
| 공유 규약 | `skills/_shared/devflow-conventions.md` |
| 게이트 패턴 | `skills/_shared/gate-patterns.md` |
| TDD 프로토콜 | `skills/_shared/tdd-protocol.md` |
| 세션 연속성 | `skills/_shared/patterns/session-continuity.md` |
| NFR 프리셋 가이드 | `docs/guide/nfr-domain-presets.md` |

---

## 참고

- GitHub 리포: [bluejayA/aidlc-devflow](https://github.com/bluejayA/aidlc-devflow)
- 원본 참조: [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows)
- 백로그 전체: `devflow-docs/backlog.md`
