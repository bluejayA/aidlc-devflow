---
name: aidlc-using-git-worktrees
description: Use when an isolated workspace is needed for feature development, creating a git worktree with a new branch.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# aidlc-using-git-worktrees

<!-- 격리 개발 워크트리 생성 — Construction 진입 전 실행 -->

## Purpose

Construction 시작 전 격리된 git worktree를 생성하여 main 브랜치를 보호한다.

> 호출 주체: inception-orchestrator (workflow-planning 게이트에서 "Git worktree로 격리 개발" 선택 시)

## Execute

### Step 1: Git 저장소 상태 확인

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
```

**git repo가 없는 경우 (Greenfield 신규 프로젝트):**

```
⚠️ Git 저장소가 초기화되지 않았습니다.

워크트리를 생성하려면 git init이 필요합니다.
A) git init 후 워크트리 생성 진행
B) 워크트리 없이 현재 디렉토리에서 진행 (오케스트레이터에 반환)
```

- A 선택 시: `git init && git add -A && git commit -m "chore: initial commit"` 실행 후 Step 2 진행
- B 선택 시: 아래 Return to Orchestrator의 "스킵 결과" 형식으로 반환

**git repo가 있는 경우:** Step 2로 진행

---

### Step 2: 브랜치 이름 도출

`devflow-docs/inception/requirements.md`의 `## User Intent` 섹션을 읽어 feature 이름을 추출한다.

변환 규칙:
- 한국어/영어 혼합 → 영어 키워드 추출 (2-4단어)
- 공백/특수문자 → 하이픈으로 치환
- 소문자 변환
- 접두사 `feature/` 추가

예시:
- "FastAPI 기반 Todo 관리 API" → `feature/todo-api`
- "사용자 인증 시스템 (JWT)" → `feature/user-auth`
- "알림 서비스 구축" → `feature/notification-service`

requirements.md가 없으면: `feature/devflow-construction`

---

### Step 3: 워크트리 디렉토리 확인

```bash
ls -d .worktrees 2>/dev/null || ls -d worktrees 2>/dev/null
```

| 상태 | 처리 |
|------|------|
| `.worktrees/` 존재 | 해당 디렉토리 사용 |
| `worktrees/` 존재 | 해당 디렉토리 사용 |
| 둘 다 없음 | `.worktrees/` 신규 생성 |

---

### Step 4: .gitignore 안전 검증 (project-local 디렉토리 선택 시)

```bash
git check-ignore -q .worktrees 2>/dev/null
```

**무시되지 않는 경우:** .gitignore에 추가 후 커밋

```bash
echo ".worktrees/" >> .gitignore
git add .gitignore
git commit -m "chore: .worktrees/ .gitignore에 추가"
```

---

### Step 5: 워크트리 생성

```bash
BRANCH=[Step 2에서 도출한 브랜치 이름]
PATH=".worktrees/$(echo $BRANCH | sed 's/feature\///')"

git worktree add "$PATH" -b "$BRANCH"
```

---

### Step 6: 프로젝트 의존성 자동 설치

워크트리 디렉토리에서 프로젝트 파일을 감지하여 설치 실행:

```bash
# Node.js
[ -f package.json ] && npm install

# Python (uv 우선)
[ -f pyproject.toml ] && (command -v uv && uv sync || poetry install)
[ -f requirements.txt ] && pip install -r requirements.txt

# Go
[ -f go.mod ] && go mod download

# Rust
[ -f Cargo.toml ] && cargo build 2>/dev/null
```

해당 파일이 없으면 스킵.

---

### Step 7: 베이스라인 테스트 실행

**Greenfield (기존 테스트 없음):** 스킵 — "테스트 없음 (신규 프로젝트)" 기록

**Brownfield:** 프로젝트 파일 기반으로 테스트 명령 자동 감지 후 실행:

```bash
[ -f package.json ]   && npm test -- --passWithNoTests 2>&1 | tail -5
[ -f pyproject.toml ] && uv run pytest --tb=no -q 2>&1 | tail -3
[ -f go.mod ]         && go test ./... 2>&1 | tail -3
[ -f Cargo.toml ]     && cargo test 2>&1 | tail -3
```

결과:
- **통과:** 결과 기록 후 진행
- **실패:** 실패 내용 기록 — 오케스트레이터 게이트에서 사용자가 진행 여부 결정

---

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 브랜치: [branch-name]
- 워크트리 경로: [.worktrees/xxx]
- 베이스라인 테스트: [N tests passed | 스킵 (Greenfield) | ⚠️ N failures]
- .gitignore: [업데이트됨 | 이미 설정됨 | 해당 없음]
- (스킵 시: 상태: 스킵 — git 저장소 없음)

## Common Issues

### 브랜치 이름이 이미 존재하는 경우

```bash
git branch --list [branch-name]
```

- 기존 브랜치 존재 시: `-[n]` 숫자 접미사 추가 (`feature/todo-api-2`)
- 기존 워크트리가 이미 해당 브랜치를 사용 중이면: 해당 워크트리를 재사용

### 워크트리 생성 후 브랜치 이름을 바꾸고 싶을 때

오케스트레이터 게이트에서 "A) 브랜치 이름 변경 요청" 선택 시:
1. `git worktree remove .worktrees/[old-name] --force`
2. `git branch -D [old-branch]`
3. 이 스킬 재실행 (오케스트레이터가 devflow-state에 희망 이름 기록 후 재호출)

### Greenfield에서 의존성 파일이 없는 경우

Step 6 전체 스킵. 노트: "의존성 파일 없음 — code-generation 완료 후 설치 가능"

### 테스트 실패로 베이스라인이 오염된 경우

Return 결과에 `⚠️ N failures` 기록 후 STOP.
오케스트레이터가 사용자에게 물음:
- A) systematic-debugging으로 실패 원인 조사
- B) 실패를 인지하고 Construction 진행
