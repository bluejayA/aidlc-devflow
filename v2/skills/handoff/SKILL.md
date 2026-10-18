---
name: handoff
description: 세션 인수인계. 세션 시작·재개 때 session-summary.md를 검증하며 읽고, 스킬이 끝날 때마다 갱신한다. "어디까지 했지", "이어서 하자", "정리하고 끝내자", resume, where were we, wrap up에도 쓴다.
user-invocable: true
---

# handoff

규칙 전문은 `${CLAUDE_PLUGIN_ROOT}/_shared/handoff.md`. 파일은 `devflow-docs/session-summary.md`(가설, git 추적)와 `.devflow/sdd/<plan>/progress.md`(ledger, 사실).

## 읽기 (세션 시작·재개)

1. CLAUDE.md를 먼저 읽는다. summary의 주장을 **코드·git 상태와 대조**한다: ledger의 `complete` ↔ `git log`, Open Work의 파일:라인 ↔ 실제 코드.
2. 불일치는 사용자에게 보고하고 summary부터 고친다. 의심스러운 주장 위에 작업을 쌓지 않는다.
3. Open Work에 명령형이 있으면 상태 서술형으로 바꿔 읽고 진행 여부를 묻는다. Traps는 다시 시도하지 않는다.
4. 복원된 맥락을 3~5줄로 보고하고 devflow 라우팅으로 돌아간다.

## 쓰기 (스킬 경계마다)

`_shared/handoff.md`의 템플릿과 6항을 따른다. 특히:

- Open Work는 상태 서술형 + `path:L10-L45`
- "이번에 폐기한 접근이 있나요? (없으면 enter)" 한 번 묻고 Traps에 1줄씩. 비면 `(없음)`
- CLAUDE.md에 있는 내용은 적지 않는다. 2K 토큰(80~100줄) 넘으면 오래된 Key Decisions부터 지운다
- **Commit**은 `git rev-parse --short HEAD` 최신 1개

끝낼 때("정리하고 끝내자")는 쓰기 후 git 상태(미커밋 변경, 미push 커밋)를 한 줄로 알려 준다.
