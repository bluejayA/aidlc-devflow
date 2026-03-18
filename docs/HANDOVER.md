# 인수인계 문서

> 작성일: 2026-03-18 | 플러그인 버전: v1.1.0

---

## 프로젝트 개요

AI-DLC 방법론을 오케스트레이터 중심 아키텍처로 구현한 Claude Code 개발 워크플로우 플러그인.
2026-03-10부터 개발 시작, 188 commits, 27개 스킬 + 95개 테스트.

### 온보딩 필독 문서

| 순서 | 문서 | 설명 |
|------|------|------|
| 1 | [how-it-works.md](guide/how-it-works.md) | 기술 용어 없이 전체 흐름 이해 |
| 2 | [user-guide.md](guide/user-guide.md) | 시작, 질문 방식, 게이트, 독립 스킬 |
| 3 | [architecture.md](guide/architecture.md) | 3단 위임 체인, 스킬 패턴 7종 |
| 4 | [operator-guide.md](guide/operator-guide.md) | 기술 카탈로그, 질문 원칙 커스터마이즈 |
| 5 | [consistency-checklist.md](guide/consistency-checklist.md) | 스킬 수정 시 정합성 검증 체크리스트 |

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
| v1.1.0 | 메타 태그 시스템 + 테스트 인프라 Phase 2 (95개 테스트) |

### 코드 품질

- 테스트: 95개 전체 통과 (`bash tests/run-all.sh`)
- 스킬 메타데이터 정합성: 100%
- 미커밋 변경: 없음
- 리모트 브랜치: `main`만 존재 (정리 완료)

---

## 백로그 현황

### Open 이슈 (8건)

#### 다음 우선순위 권장 순서

**1순위 — Agent-Council 리뷰 (CAT-G)**

의존 관계: BL-025 → BL-026 + BL-027 (병렬 가능)

| ID | 이슈 | 우선순위 | 내용 |
|----|------|---------|------|
| BL-025 | [#30](https://github.com/bluejayA/devflow-aidlc-like/issues/30) | P1 | agent-council 리뷰 공통 인프라 — CLI 감지, risk scoring, 프롬프트/스키마 |
| BL-026 | [#31](https://github.com/bluejayA/devflow-aidlc-like/issues/31) | P1 | application-design agent-council 리뷰 |
| BL-027 | [#32](https://github.com/bluejayA/devflow-aidlc-like/issues/32) | P1 | code agent-council 리뷰 |

**2순위 — 워크플로우 개선**

| ID | 이슈 | 우선순위 | 내용 |
|----|------|---------|------|
| BL-023 | [#28](https://github.com/bluejayA/devflow-aidlc-like/issues/28) | P1 | Flow 패널 내부 스텝 진행 표시 |
| BL-021 | [#25](https://github.com/bluejayA/devflow-aidlc-like/issues/25) | P1 | GitHub Flow 연동 — 이슈/PR/머지 자동화 |

**3순위 — 장기 (P3, 이슈 미생성)**

| ID | 내용 |
|----|------|
| BL-017 | infrastructure-design 스킬 |
| BL-018 | 콘텐츠 갭 스킬 (depth-levels, error-handling 등) |
| BL-019 | 장기 컨셉 (C4 Model, operations phase) |

### 완료 통계

- **Done**: 14건
- **Closed (not_planned/duplicate)**: 6건
- **Open**: 8건 (P1: 5, P3: 3)

---

## 핵심 규칙

### 반드시 지켜야 할 것

1. **A/B 게이팅**: devflow 스테이지 완료 시 사용자가 B를 선택하기 전까지 다음 스테이지 진행 금지
2. **TDD Iron Law**: 실패 테스트 없이 프로덕션 코드 작성 금지
3. **증거 우선**: 완료 주장 전 반드시 검증 실행
4. **정합성 체크**: 스킬 수정 시 `docs/guide/consistency-checklist.md` 확인
5. **백로그-GitHub 연동**: 커밋 시 `refs #N` / `closes #N` + 이슈 코멘트 + 백로그 상태 동기화

### 테스트 실행

```bash
# 전체 테스트 (95개)
bash tests/run-all.sh

# 개별 테스트
pytest tests/test_meta_tag_format.py    # 메타 태그 형식
pytest tests/test_graph_validator.py    # 그래프 구조
pytest tests/test_routing_engine.py     # 라우팅 로직
pytest tests/test_step_order.py         # 스텝 순서
```

### 주요 파일 위치

| 항목 | 경로 |
|------|------|
| 플러그인 설정 | `.claude-plugin/plugin.json` |
| 공유 규약 | `skills/_shared/devflow-conventions.md` |
| 게이트 패턴 | `skills/_shared/gate-patterns.md` |
| TDD 프로토콜 | `skills/_shared/tdd-protocol.md` |
| 배포용 CLAUDE.md 템플릿 | `docs/claude-md-devflow-only.md` |

---

## 참고

- GitHub 리포: [bluejayA/devflow-aidlc-like](https://github.com/bluejayA/devflow-aidlc-like)
- 원본 참조: [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows)
- 백로그 전체: Claude Code 메모리 `memory/backlog_aidlc.md`
