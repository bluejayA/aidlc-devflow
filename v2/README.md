# aidlc v2 (work in progress)

v1(28 skills, `../skills/`)을 방법론 자산만 추려 스킬 7개로 다시 만드는 중.
설계: "aidlc-devflow v2 재기반 설계안" (2026-10-18).

## 상태

- [x] 1단계 지식 추출 — `_shared/`
- [x] 2단계 얇은 코어 — `skills/` 8개(7 + discipline), `hooks/` 3개, `.claude-plugin/plugin.json` (`claude plugin validate` 통과)
- [x] 3단계 외부 리뷰 1경로 — `scripts/codex-review`
- [ ] v1 → `_archive/v1/` 이동, v2를 레포 루트로
- [ ] 사이드 프로젝트 1건 v2로 완주

## 설치 (alpha)

```bash
# 레포 루트가 아직 v1이라 디렉터리로 직접 로드
claude --plugin-dir /path/to/aidlc-devflow/v2
# v2가 루트로 올라간 뒤:
/plugin install aidlc --marketplace bluejayA/devflow-marketplace
```

## 스킬 8개

| 스킬 | 호출 | 역할 |
|------|------|------|
| `devflow` | 자동·직접 | 진입. 재개 확인 → Size the Work → 라우팅. 사람 게이트 2곳(설계 승인·finishing) |
| `requirements` | devflow | 프로젝트 크기: workspace + 요구 + NFR 프리셋 → `inception/requirements.md` |
| `design` | devflow | 설계 문서 + builder check 1회 + 설계 승인 게이트 → `inception/design.md` |
| `plan-build` | devflow | 계획(Global Constraints·Review Focus) → 인라인 또는 서브에이전트로 태스크 루프, ledger, Rulings |
| `review` | 자동·직접 | 브랜치 리뷰 1회(최강 모델, Part 1~4) + Codex 교차 1회 → `.devflow/review-done` |
| `handoff` | 자동·직접 | session-summary 검증 읽기 / 6항 쓰기 |
| `brownfield` | 자동·직접 | 기존 코드 3축 탐색 |
| `discipline` | 참조 | 테스트 먼저·증거 먼저 요령 (제안형) |

## 훅 3개

| 이벤트 | 동작 |
|------|------|
| SessionStart | 안내 + session-summary 있으면 재개 프로토콜 지시 |
| PreToolUse(Bash) | main push 차단 · 커밋 전 테스트 흔적(docs/chore 예외) · `.devflow/sdd` 있으면 push/PR 전 review-done 확인. `DEVFLOW_GATE=off`로 우회 |
| PostToolUse | 테스트 실행 마커 · `devflow-docs/audit.md` append |

게이트 2·3은 `devflow-docs/` 또는 `.devflow/`가 있는 프로젝트에서만 작동한다.

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
