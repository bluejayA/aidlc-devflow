---
name: plan-build
description: 승인된 설계(또는 대화로 합의한 작은 변경)를 태스크별 계획으로 바꾸고, 태스크마다 구현 → 리뷰 → ledger 기록을 멈추지 않고 돌린다. devflow가 설계 승인 뒤에 호출한다. 끝나면 review 스킬로.
user-invocable: false
---

# plan-build

**입력**: `devflow-docs/inception/design.md` 또는 대화에서 합의한 작은 변경. **산출물**: `devflow-docs/plans/YYYY-MM-DD-<topic>.md`, 코드, `.devflow/sdd/<plan>/progress.md`(ledger). 끝나면 `review`.

## A. 계획

독자는 이 코드베이스도 spec도 못 본 유능한 엔지니어다. 그가 모르는 건 **내가 정한 것**: 어느 파일, 어떤 이름과 시그니처, spec의 어떤 값, 어떤 테스트가 각 태스크를 증명하는가. 그것만 적는다. 코드는 적지 않는다 — 시그니처와 테스트가 정하지 않는 알고리즘에만 코드 블록.

### 파일 구조 먼저
어떤 파일을 만들고 고치는지, 각 파일의 책임 하나. 기존 코드베이스의 패턴을 따른다.

### 태스크 크기
태스크 = 자기 테스트 사이클을 갖고 리뷰어가 따로 승인·반려할 수 있는 최소 단위. 설정·스캐폴딩·문서는 그것을 필요로 하는 태스크에 접는다.

### 계획 템플릿

```markdown
# <topic> — Plan
**Spec:** devflow-docs/inception/design.md (또는 "대화 합의: <한 단락>")
**Goal:** 한 문장   **Architecture:** 2~3문장   **Tech stack:** 핵심만

## Global Constraints
spec의 프로젝트 전역 요구를 한 줄씩, 값은 그대로 복사. 모든 태스크에 암묵 적용.

## Review Focus
spec이 암시하지만 어느 태스크의 테스트도 안 건드리는 실패 모드 ≤5개 — 입력/조건과 기대 동작,
가능성 높은 것부터. 각 줄을 소유 태스크의 테스트 스텝으로 핀한다.

### Task N: <이름>
**Files:** Create/Modify(`path:L10-L45`)/Test
**Interfaces:** Consumes(앞 태스크에서 쓰는 시그니처) / Produces(뒤 태스크가 의존하는 이름·타입)
- [ ] Step 1: 실패하는 테스트 작성 — 테스트 이름과 단정 내용
- [ ] Step 2: 실패 확인 — `실행 명령`, 기대: FAIL "<이유>"
- [ ] Step 3: `시그니처` 구현 in `path` — 선택이 남는 곳만 한 줄
- [ ] Step 4: 통과 확인 — `실행 명령`, 기대: PASS
- [ ] Step 5: 커밋 — `feat: …`
```

### 자기 점검 (쓰고 나서)
- 자리표시자(TBD, TODO)가 남아 있나 · 태스크끼리 이름·시그니처가 맞나 · 계획이 spec보다 몇 배 길면 코드를 적은 것이다 → 결정만 남기고 지운다.
- Review Focus 각 줄에 핀된 테스트가 있나.

작은 변경이면 Global Constraints·Review Focus는 한두 줄, 태스크 1~3개.

## B. 실행 방식 하나를 고른다

| 방식 | 비용 | 언제 |
|------|------|------|
| **서브에이전트** | 태스크마다 구현자 1 + 리뷰어 1 (새 컨텍스트) | 태스크마다 리뷰 게이트를 원할 때, 계획이 길어 뒤 태스크가 compaction 뒤에 돌 때 |
| **인라인** | 내 컨텍스트 1 + 브랜치 끝 리뷰 1 | 그 외 기본. 계획이 충분히 구체적이면 전사 + 테스트다 |

사용자가 정해 두지 않았으면 인라인. 두 방식 다 같은 ledger를 쓰고 태스크 사이에 멈추지 않는다.

## C. 설정

1. 작업은 격리 브랜치에서. main/master면 `git switch -c`로 feature 브랜치 (worktree가 필요하면 Claude Code 내장 `--worktree`/`EnterWorktree`를 쓴다 — 자체 스킬 없음).
2. `bash ${CLAUDE_PLUGIN_ROOT}/_shared/scripts/sdd-workspace <plan>` → 이 계획의 디렉터리. `progress.md`가 있고 첫 줄이 이 계획이면 **재개**: `Task N: complete`인 태스크는 건너뛰고, 마지막 줄이 fix round면 그 다음 라운드부터. 없으면 `# ledger — plan: <path>`로 만든다.
3. 사전 스캔: 파일·인터페이스를 공유하는 태스크 쌍마다 Produces/Consumes가 맞는지, 각 태스크의 테스트와 코드 스텝이 서로 맞는지 표로 ledger에 적는다. 충돌은 Ruling으로 정하고 시작한다. 깨끗하면 "Pre-flight: clean" 한 줄.

## D. 태스크 루프

### 인라인
1. `bash ${CLAUDE_PLUGIN_ROOT}/_shared/scripts/task-brief <plan> N` → 브리프를 읽는다. BASE = 현재 HEAD.
2. 스텝을 순서대로. 테스트는 실패를 **보고** 나서 구현한다(`discipline`). 각 검증 스텝의 출력을 읽고 계획의 기대와 비교한다 — 다르면: 계획이 틀렸으면 Ruling, 코드가 틀렸으면 고친다.
3. 계획의 커밋 스텝대로 커밋. ledger에 `Task N: complete — <hash> — <한 줄>`.

### 서브에이전트
1. 브리프 생성 → 구현자 디스패치(`${CLAUDE_PLUGIN_ROOT}/_shared/prompts/implementer-prompt.md`, **모델 명시**: 기계적 태스크는 저가). 구현자는 구현·테스트·커밋 후 보고서 파일을 쓴다.
2. `bash ${CLAUDE_PLUGIN_ROOT}/_shared/scripts/review-package <plan> BASE HEAD` → 리뷰어 디스패치(`_shared/prompts/review-prompt.md` Part 1~2, 모델은 diff 크기에 맞춤).
3. ❌ → fix round. 1~2회는 같은 구현자 재개, 3회는 더 강한 모델의 새 구현자. 3회 넘으면 finding을 Ruling으로 판정하고 ledger에 남긴 채 계속. ⚠️는 브랜치 리뷰로.
4. ledger 기록, 다음 태스크.

### 멈추는 조건 (둘 다)
되돌릴 수 없는·파괴적 작업 · 보안 민감 작업 · worktree 밖 부작용(머지·공유 브랜치 push·배포) · 모든 길이 추측인 계획. 그 외의 모호함은 `Ruling: 결정 — 이유 — 틀리면 비용`을 ledger에 적고 계속한다. "계속할까요?"를 묻지 않는다.

## E. 끝

모든 태스크가 `complete`면 `handoff`로 session-summary를 갱신하고 `review`를 호출한다. 리뷰가 깨끗하면 이 계획의 `.devflow/sdd/<plan>/`을 지운다.
