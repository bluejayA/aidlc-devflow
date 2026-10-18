# aidlc v2 (work in progress)

v1(28 skills, `../skills/`)을 방법론 자산만 추려 스킬 7개로 다시 만드는 중.
설계: "aidlc-devflow v2 재기반 설계안" (2026-10-18).

## 상태

- [x] 1단계 지식 추출 — `_shared/` (이 커밋)
- [ ] 2단계 얇은 코어 — `skills/` 7개, `hooks/` 3개, `.claude-plugin/plugin.json`
- [ ] 3단계 외부 리뷰 1경로 — `scripts/codex-review`
- [ ] v1 → `_archive/v1/` 이동, 사이드 프로젝트 1건 완주

## `_shared/`

| 파일 | 출처 | 내용 |
|------|------|------|
| `conventions.md` | v1 devflow-conventions + gate-patterns, 축약 | 스킬 7개 역할, Size the Work, 사람 게이트 2곳, Rulings, 산출물, 서브에이전트, 리뷰 규약 |
| `handoff.md` | v1 session-continuity 6항 + superpowers ledger | ledger / session-summary 역할 분리, 재개 프로토콜 |
| `brownfield.md` | v1 brownfield-exploration | 3축 탐색 (핫스팟·문서·샘플) |
| `prompts/review-prompt.md` | v1 리뷰어 12종 → 1개, superpowers 3-verdict 구조 | 태스크 리뷰(Part 1~2) / 브랜치 리뷰(1~4) / Codex 공용 |
| `prompts/builder-check-prompt.md` | superpowers | 설계 문서 구현자 관점 질문 1회 |
| `scripts/{task-brief,review-package,sdd-workspace}` | superpowers | 파일 기반 디스패치 |
| `reference/domain-cards.md`, `reference/nfr-presets.md` | v1 docs | 도메인 카드 5종, NFR 프리셋 |

라이선스: `THIRD-PARTY-NOTICES.md`.
