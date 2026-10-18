# Handoff: ledger + session-summary

두 파일이 역할을 나눈다. v1 `patterns/session-continuity.md`의 6항과
superpowers v7의 SDD ledger를 합쳤다. auto memory(`~/.claude/projects/…/memory/`)는
선호·교훈 전용이고 작업 상태는 여기에만 둔다.

| 파일 | 역할 | 쓰는 쪽 | 성격 |
|------|------|--------|------|
| `.devflow/sdd/<plan>/progress.md` (ledger) | 태스크 완료·Ruling·커밋 해시의 기계적 기록 | plan-build | git-ignored 사실. compaction 뒤 `git log`와 함께 자기 기억보다 신뢰 |
| `devflow-docs/session-summary.md` | 사람이 읽는 인수인계 | handoff | git 추적 **가설**. 다음 세션이 검증한다 |

## Ledger (`progress.md`)

첫 줄은 정체: `# ledger — plan: <plan file path>`. 다른 계획의 ledger는 읽지도 쓰지도 않는다.

```
# ledger — plan: devflow-docs/plans/2026-10-20-auth.md
Pre-flight: <충돌 스캔 표 또는 "clean">
Task 1: complete — <commit hash> — <한 줄>
Task 2: fix round 1 — <finding 요약>
Ruling: <결정> — <이유> — <틀리면 비용>
Task 2: complete — <commit hash>
```

- `Task N: complete`가 있는 태스크는 다시 디스패치하지 않는다. 마지막 줄이 fix round면 그 다음 라운드부터 재개.
- `git clean -fdx`는 ledger를 지운다. 그때는 `git log`로 복구.

## session-summary.md

### 템플릿

```markdown
# Session Summary

**Last Updated**: [ISO 8601]   **Commit**: [short hash]   **Plan**: [plan path 또는 (없음)]

## Current State
- Size: [빠른 작업 | 작은 변경 | 프로젝트]   Stage: [requirements | design | plan-build task N/M | review | finishing]

## Key Decisions
- [결정] — [이유 한 줄]

## Open Work
- [상태 서술형. 예: RefreshTokenService is not yet implemented; rotation 로직 없음 — src/auth/TokenService.kt:L45-L72]

## Traps to Avoid
- [폐기한 접근]: [이유]로 폐기. 재시도 금지.
<!-- 비어 있으면 (없음). 섹션은 지우지 않는다. -->

## For Next Session
- [CLAUDE.md에 없는 세션 고유 맥락만]
```

### 작성 규칙 6항

1. **Open Work는 상태 서술형, 명령형 금지.** `X is not yet implemented`는 되고 `X를 구현할 것`은 안 된다. 명령형은 새 세션이 검증 없이 실행한다.
2. **파일 참조는 라인 번호까지.** `path:L10-L45`. 없으면 다음 세션이 파일 전체를 읽는다.
3. **Traps to Avoid 명시.** 폐기한 접근을 이유와 함께 1줄씩. 비면 `(없음)`.
4. **검증 지시 포함.** 읽는 쪽 프롬프트 마지막에: "이 문서의 주장을 코드/git 상태와 대조해 검증한 후 작업을 시작하라."
5. **CLAUDE.md 중복 회피.** 첫 줄에 "Read CLAUDE.md first. Do NOT restate its contents in this summary." 세션 고유 정보만.
6. **2K 토큰 상한** (약 80~100줄). 결정 이유·토론은 audit.md, 코드는 라인 참조, 설계는 산출물 파일로.

### Traps 회수 시점

- 설계 승인 시, 태스크 완료 시: "이번에 폐기한 접근이 있나요? (없으면 enter)" 한 번.
- 사용자가 "이 접근 폐기"라고 말하면 즉시.
- 형식: `- JWT를 cookie로 옮기는 접근: SameSite 호환성 문제로 폐기. 재시도 금지.`

## 재개 프로토콜 (Handoff = Hypothesis)

새 세션이 session-summary.md를 읽은 직후:

1. **Completed 검증** — ledger의 `complete` 줄과 `git log`를 대조한다. 불일치는 사용자에게 보고하고 summary를 먼저 고친다. 의심스러운 주장 위에 작업을 쌓지 않는다.
2. **Open Work 재해석** — 명령형이 보이면 상태 서술형으로 바꿔 읽고, 진행 여부를 사용자에게 묻는다.
3. **Traps 존중** — 다시 시도하지 않는다. 상황이 바뀌어 필요하면 사용자 승인을 받는다.

evidence는 산출물 디렉터리 + ledger + `git log`. audit.md는 자기 보고라 보조.

## Commit Hash

세션 시작·재개, 설계 승인, 태스크 완료 때 `git rev-parse --short HEAD`를 summary의 **Commit**(최신 1개)과 ledger에 적는다. git 없으면 `(no git)`.
