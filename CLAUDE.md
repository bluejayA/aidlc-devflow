# aidlc-devflow 프로젝트 규칙

## 정체성 (2026-10-18 v2 재기반)

**Jay's personal AI workflow plugin — 1인용. 스킬 8개 + 훅 게이트 3개.**

- v1(28 스킬, 2026-03~05)은 `_archive/v1/`에 보존. 유지보수하지 않는다. 태그 `v1.15.0`.
- v2는 방법론 자산(INCEPTION 구조, Handoff=Hypothesis, brownfield 3축, 통합 리뷰 관점, Codex 교차 리뷰)만 남기고 구현 레이어는 Claude Code 네이티브(worktree, auto memory, 서브에이전트 중첩, `/code-review`)와 훅에 맡겼다.
- superpowers v7.0.0(MIT)에서 패턴 6개 차용: Size the Work, builder check, ledger + 파일 기반 디스패치, Rulings-not-stalls, Review Focus, 역할별 모델 선택. 출처는 `THIRD-PARTY-NOTICES`.
- 설계 문서: "aidlc-devflow v2 재기반 설계안" (Claude Docs, 2026-10-18).

## 구조

```
.claude-plugin/plugin.json   # name: aidlc
skills/<8개>/SKILL.md        # devflow, requirements, design, plan-build, review, handoff, brownfield, discipline
hooks/                       # hooks.json + session-start, pretool-git, posttool-audit, _lib.sh
scripts/codex-review         # 외부 리뷰 1경로
_shared/                     # conventions, handoff, brownfield, prompts/, scripts/, reference/
_archive/v1/                 # v1 전체 (읽기 전용)
```

- 스킬 본문은 "무엇을 할지"만. 설득·리캡·합리화 방지 문구는 쓰지 않는다 — 강제는 훅이 한다.
- 새 스킬·패턴 추가 전에 묻는다: Jay의 실제 페인포인트인가, Claude가 짠 이상적 답인가. 후자면 추가하지 않는다.
- 측정 인프라를 만들지 않는다. 유지·종료 판단은 분기 자가 audit(사용 여부)로만.

## Claude와 협업 시 과잉설계 회피 룰 (v1에서 유지)

1. 새 스킬/패턴 추가 욕구는 yak shaving 의심 신호
2. "이상적 목표" 시스템화·일반화·추상화 추천 거부
3. 분기별 본인 audit 필수
4. 측정 인프라 작업 제안 금지

## GitHub Flow (필수)

- GitHub 작업은 모두 `gh` CLI(REST API)로.
- 커밋: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`). 이슈 연결 `refs #N` / `closes #N`. 멀티라인은 HEREDOC.
- PR: body 첫 줄에 `Closes #N`, Summary + Test plan. 승인 없이 push/merge 금지.
- 릴리스: `.claude-plugin/plugin.json` version을 올리고 같은 값으로 `v*` 태그. 태그 push가 marketplace(`bluejayA/devflow-marketplace`)를 동기화한다 (`.github/workflows/sync-marketplace.yml`).

## 수정 전 영향도 확인

1. 바꾸려는 경로·키워드를 `_shared/`, `skills/`, `hooks/`에서 Grep으로 교차 확인 (스킬이 `${CLAUDE_PLUGIN_ROOT}/_shared/...`를 직접 참조한다)
2. 훅 스크립트를 바꾸면 stdin 시뮬레이션으로 allow/deny 케이스를 다시 돌린다 (PR #214 Test plan 참조)
3. `claude plugin validate .` 통과 후 커밋

## 백로그

GitHub 이슈로만 관리한다. v1 시절 BL-xxx 이슈는 v2 범위에서 재평가 후 닫거나 다시 연다. `_archive/v1/backlog.md`는 참고용.
