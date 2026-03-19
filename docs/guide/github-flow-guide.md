# GitHub Flow 가이드

> Claude Code에서 GitHub 이슈/PR/백로그를 운영하는 표준 절차.
> 이 가이드를 `~/CLAUDE.md`와 프로젝트 `CLAUDE.md`에 적용하면 모든 프로젝트에서 일관된 GitHub Flow를 사용할 수 있다.

---

## 적용 방법

### 1단계: `~/CLAUDE.md`에 공통 규칙 추가

아래 "공통 규칙 (~/CLAUDE.md용)" 섹션을 `~/CLAUDE.md`에 복사한다. 모든 프로젝트에 자동 적용된다.

### 2단계: 프로젝트 `CLAUDE.md`에 프로젝트별 규칙 추가

백로그-이슈 연동이 필요한 프로젝트에만 "프로젝트별 규칙 (CLAUDE.md용)" 섹션을 복사한다.

### 3단계: 백로그 파일 생성

`memory/backlog_[project].md` 파일을 "백로그 템플릿"에서 복사하여 생성한다.

---

## 공통 규칙 (~/CLAUDE.md용)

아래를 `~/CLAUDE.md`의 적절한 위치에 추가한다.

```markdown
## GitHub Flow

### gh CLI 사용

GitHub 작업은 모두 `gh` CLI로 수행한다. MCP GitHub 도구는 사용하지 않는다.

### 커밋 메시지

- Conventional Commits 형식: `feat:`, `fix:`, `chore:`, `docs:`
- 이슈 연결: 진행 중 `refs #N`, 완료 시 `closes #N`
- HEREDOC으로 멀티라인 메시지 작성
- Co-Authored-By 포함

### PR 생성 규칙

- **body 첫 줄에 `Closes #N`** — 타이틀에만 넣으면 GitHub에서 이슈 연결이 안 됨
- Summary + Test plan 포함
- 테스트 통과 확인 후 PR 생성
- 승인 없이 push/merge 금지

### 수정 전 영향도 확인

코드를 변경하기 전에 다음을 확인한다:
1. 변경하려는 텍스트/키워드를 다른 파일에서 참조하는지 Grep으로 확인
2. 핵심 특성 키워드(TDD, Review 등)를 삭제하는 경우, 의도적인지 재확인
3. 출력 경로(output_path 등) 변경 시, 하류에서 해당 경로를 참조하지 않는지 확인
```

---

## 프로젝트별 규칙 (CLAUDE.md용)

백로그-GitHub 이슈 연동이 필요한 프로젝트에 아래를 추가한다. `[owner/repo]`와 `[project]`를 실제 값으로 교체.

```markdown
## 백로그-GitHub 이슈 연동 (필수)

### 백로그 등록 시
- `memory/backlog_[project].md`에 항목 추가
- GitHub 이슈를 `enhancement` 라벨로 동시 생성 (`[owner/repo]`)
- 백로그에 이슈 번호와 링크 기록

### 백로그 구현 시
백로그 항목을 구현하여 커밋할 때, 연결된 GitHub 이슈와 반드시 연동한다.

1. **커밋 메시지에 이슈 번호 포함**
   - 진행 중: `refs #N`
   - 완료 시: `closes #N` (머지 시 이슈 자동 클로즈)

2. **GitHub 이슈에 진행 코멘트 남기기**
   - 구현 시작 시: 간략한 접근 방식 코멘트
   - 커밋 완료 시: 변경 내용 요약 + 커밋 해시 코멘트

3. **백로그 파일 상태 동기화**
   - 구현 완료 시 `backlog_[project].md`의 상태를 `Done`으로 변경
   - 현황 카운트(Open/Done/Closed) 갱신
```

---

## 백로그 템플릿

`memory/backlog_[project].md`로 저장한다.

```markdown
---
name: [프로젝트명] 백로그
description: [프로젝트] 개선사항 백로그. 카테고리별 정리. GitHub Issues 연동.
type: project
---

## 백로그 현황

- **Open**: 0건
- **Done**: 0건
- **Closed**: 0건
- **마지막 정리**: YYYY-MM-DD

---

## CAT-A: [카테고리명]

> [카테고리 설명]

### BL-001: [제목] [P1]
- **상태**: Open
- **GitHub**: [#N](https://github.com/[owner/repo]/issues/N)
- **등록일**: YYYY-MM-DD
- **출처**: [어디서 발견/요청되었는가]
- **현재 동작**: [현재 어떻게 동작하는가]
- **제안**: [어떻게 변경할 것인가]
- **영향 범위**: [변경되는 파일/컴포넌트]

---

## CAT-B: [카테고리명]

> [카테고리 설명]

(항목 추가)
```

### 백로그 항목 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| 상태 | 필수 | Open / Done / Closed (사유) |
| GitHub | 필수 | 이슈 링크 |
| 등록일 | 필수 | 절대 날짜 (상대 날짜 금지) |
| 출처 | 필수 | 발견 경위 |
| 현재 동작 | 권장 | 변경 전 상태 |
| 제안 | 필수 | 변경 내용 |
| 영향 범위 | 필수 | 변경되는 파일/컴포넌트 |
| 선행 | 선택 | 의존하는 다른 BL |
| 관련 | 선택 | 관련된 다른 BL |

### 우선순위 기준

| 우선순위 | 기준 |
|---------|------|
| P0 | 즉시 수정 — 동작 불가, 보안 이슈, 다른 작업 차단 |
| P1 | 수정 권장 — 품질/UX에 영향, 합리적 시일 내 처리 |
| P2 | 개선 가능 — 있으면 좋지만 긴급하지 않음 |
| P3 | 장기 — 언젠가 하면 좋을 것 |

---

## 전체 워크플로우 요약

```
1. 작업 발견
   └→ 백로그 파일에 항목 추가 + GitHub 이슈 생성 (동시)

2. 구현 시작
   └→ 이슈에 시작 코멘트
   └→ git checkout -b [type]/[topic]

3. 구현 완료
   └→ 변경 전 영향도 확인 (Grep)
   └→ 테스트 통과 확인
   └→ git commit -m "feat: [제목] (refs #N)"
   └→ git push -u origin [branch]

4. PR 생성
   └→ gh pr create --body "Closes #N ..."
   └→ body 첫 줄에 Closes #N (필수)

5. 머지
   └→ gh pr merge [N] --squash --delete-branch
   └→ git checkout main && git pull

6. 동기화
   └→ 백로그 상태 → Done
   └→ 현황 카운트 갱신
```

---

## 이슈 클로즈 (구현 없이 닫는 경우)

```bash
gh issue close [N] --repo [owner/repo] \
  --reason "not planned" \
  --comment "[클로즈 사유]"
```

백로그에도 상태를 `Closed (not_planned) — [사유]`로 업데이트.
