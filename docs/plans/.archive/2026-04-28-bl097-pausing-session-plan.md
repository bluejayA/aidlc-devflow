# BL-097 aidlc-pausing-a-session Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** mid-cycle pause 시점에 `devflow-state.md` / project auto-memory / git log 3-way drift를 방지하는 advisory 스킬 (Phase 1 MVP).

**Complexity:** Standard

**Architecture:** `aidlc-finishing-a-development-branch`의 mid-cycle 형제 스킬. 사용자가 mid-cycle pause를 선언하면 5단계 체크리스트(state sync → memory 갱신 → index 갱신 → audit commit → 3-way verify)를 실행한다. drift 감지 시 사용자 게이트(BL-092 advisory 패턴 일관). `aidlc-using-devflow` Resume Flow에는 drift detect를 추가하여 진입 시 자동 검증 → drift면 사용자 옵션 제시.

**Tech Stack:** Markdown SKILL.md, Bash (git/grep), pytest 회귀 테스트, audit emit prefix (BL-098 #191 패턴 채택)

**Issue:** [#189](https://github.com/bluejayA/aidlc-devflow/issues/189) BL-097
**Seed 사례:** nexttui BL-P2-085 (2026-04-27 pause → 2026-04-28 resume stale recovery)
**선결:** 없음 (BL-098 #191 / BL-099 #192와 병렬 가능)

> ### ⚠️ 리뷰 상태 (2026-04-29 시점)
>
> - ✅ **plan-document-reviewer Round 1**: ❌ Issues 8건
> - ✅ **plan-document-reviewer Round 2**: ✅ Approved
> - 🚨 **Codex adversarial Round 3**: ❌ **No-ship** (high 3건 + medium 1건)
>
> 본 plan은 형식·정합성(plan-reviewer)은 통과했으나 동작·안전성(Codex adversarial)에서 블로킹 리스크 4건 식별됨. **다음 세션에서 plan v2로 수정 후 ship 가능**. 상세는 본 문서 §Codex Round 3 Findings 참조. 현재 상태로는 implementation 시작 금지.

---

## 트레이드오프 결정 (6건)

본 섹션은 적대적 리뷰(Codex 3차 + Claude self) 결과 식별된 트레이드오프와 본 plan에서의 결정을 기록한다.

### TR-1. 결정론 vs 인간 의존
- **지적**: "LLM 비결정성"을 사람 체크리스트로 해결 = 자기모순 (Claude self-adversarial)
- **결정**: **automation tier 분리**
  - 자동 (hook/code): state.md HEAD sync, audit emit, 3-way cross-check, MEMORY.md index
  - 사람/LLM 수행: project auto-memory 정밀 갱신 (LLM 판단), 사용자 게이트 응답
- 5단계 각 step 옆에 `[자동]` / `[LLM]` / `[사용자]` tier 명시

### TR-2. devflow-state.md gitignore 정책
- **현황**: nexttui PR #81에서 .gitignore 처리 (commit-driven SOT 아님)
- **본 plan 가정**: **옵션 B (gitignore 유지 + skill sync 책임)**. 본 plan 범위 외.
- **별도 BL 후보**: gitignore 해제(옵션 A) / Hybrid(옵션 C) — Phase 2에서 데이터 누적 후 재평가

### TR-3. 3-way drift 시 정책
- **결정**: **사용자 게이트 (advisory)**. BL-092 M1 결정(advisory 유지 확정)과 일관.
- 강제 commit 거부는 채택 안 함.
- **자동(unconditional) reconcile은 채택 안 함**. 다만 *사용자 선택 결과로* git HEAD 기준 재작성을 수행하는 옵션은 게이트 안에서 제공 (사용자가 명시 선택해야 발동 — 즉 user-gated reconcile, not silent auto-reconcile).

### TR-4. Resume Flow drift detect 게이팅
- **결정**: 자동 detect → 사용자 게이트 (advisory). BL-092 패턴 그대로.
- drift 시 옵션: A) 갱신 후 Resume / B) 그대로 Resume. 강제 차단 없음.

### TR-5. BL-098 audit emit 의존성
- **결정**: BL-098(#191) 병행 진행 가능하나, 본 plan의 4종 prefix는 BL-098과 같은 emit 패턴 채택.
- 본 BL이 BL-098보다 먼저 머지될 경우 임시 emit 로직을 본 skill 안에 인라인하고 BL-098 머지 시 표준화.
- **TR-5 cross-link**: Task 3 Step 3의 인라인 emit 코드는 BL-098 머지 시 제거 대상. 인라인 emit 위치마다 `<!-- TODO(BL-098): unify with standard audit emit pattern -->` 주석 의무.

### TR-7. BL-099 invoke_mode 표준화 영향
- **현황**: 본 skill frontmatter는 `invoke_mode: user-invocable` (형제 finishing-a-development-branch와 일관).
- **BL-099(#192) 결정에 따라 영향**: BL-099가 utility skill의 multi-mode 확장으로 결정될 경우, 본 skill이 호출하는 utility(devflow-state, devflow-audit)의 invoke_mode가 변경됨. 본 skill frontmatter는 그대로 유지.
- BL-099 머지 후 본 skill의 utility 호출 경로 재검증 필요 (정합성 linter BL-090 영역).

### TR-6. 단일 사례(BL-P2-085) 일반화 위험
- **지적**: n=1 사례로 5단계 결정론 도입은 over-engineering
- **결정**: **MVP 최소화 + Phase 2 보류**. 본 plan(Phase 1)은 BL-P2-085 시나리오에 직접 적용 가능한 최소 구현. T+28(2026-05-12) 추가 데이터 + 다른 사례 누적 후 Phase 2 plan에서 확장.

---

## File Structure

### 신규 파일
- `skills/aidlc-pausing-a-session/SKILL.md` — 본 skill 본문
- `tests/test_pausing_a_session.py` — 회귀 테스트 (pytest)

### 수정 파일
- `skills/aidlc-using-devflow/SKILL.md` — Resume Flow에 drift detect 게이트 추가
- `devflow-docs/backlog.md` — BL-097 항목 Done 처리 (PR 머지 시)
- `CHANGELOG.md` — v1.12.0 후보 노트 (별도)

### 참조 파일
- `skills/_shared/patterns/skill-writing-guide.md` — skill 작성 표준
- `skills/_shared/patterns/skill-design-patterns.md` — design pattern catalog
- `skills/_shared/patterns/skill-pattern-catalog.md` — 호출 패턴
- `skills/_shared/reviewers/skill-reviewer-prompt.md` — 작성 후 리뷰
- `skills/_shared/devflow-conventions.md` — frontmatter 규약 + audit prefix 표
- `skills/aidlc-finishing-a-development-branch/SKILL.md` — 형제 패턴
- `docs/guide/consistency-checklist.md` — 정합성 5종 체크
- `docs/guide/operator-guide.md` — 운영자 가이드 (mid-cycle pause 안내 추가 대상)

---

## Phase 1 (MVP) Tasks

### Task 1: SKILL.md 신규 작성

**Files:**
- Create: `skills/aidlc-pausing-a-session/SKILL.md`

- [ ] **Step 1: writing-skills 가이드 참조 준비**

읽기: `skills/_shared/patterns/skill-writing-guide.md`, `skill-design-patterns.md`, `skill-pattern-catalog.md`. frontmatter 규약 확인.

- [ ] **Step 2: SKILL.md 본문 작성**

frontmatter:
```yaml
---
name: aidlc-pausing-a-session
description: |
  mid-cycle pause 시점에 devflow-state.md / project auto-memory / git log 3-way 동기화를 수행할 때 사용. finishing-a-development-branch의 mid-cycle 형제. drift 감지 시 사용자 게이트(advisory).
  Use when pausing a development session mid-cycle to sync devflow-state.md, project auto-memory, and git log; sibling of finishing-a-development-branch for mid-cycle stops.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
  skill_nature: null
  lifecycle: active
---
```

본문 구조 (한국어 출력):

```markdown
# aidlc-pausing-a-session

<!-- 출력 언어: 한국어 (Korean) -->
<!-- mid-cycle pause: state/memory/git 3-way 동기화 -->

## Trigger

다음 상황에서 이 스킬을 실행한다:
- mid-cycle pause 선언 ("잠시 중단", "오늘은 여기까지", "내일 이어서")
- 컨텍스트 윈도우 한계 도달로 세션 종료 예정
- 다른 우선 작업으로 전환 (브랜치 미완료 상태)
- 일반적으로 finishing-a-development-branch가 아닌 임시 정지

## Purpose

`devflow-state.md`, project auto-memory, `git log` 사이의 drift를 방지한다. 한 번이라도 drift가 발생하면 다음 resume 시점에 stale 정보로 잘못된 결정을 내릴 위험이 크다 (seed 사례: nexttui BL-P2-085).

## 5단계 체크리스트

각 단계 옆 tier: `[자동]` = hook/code 수행, `[LLM]` = AI 수행, `[사용자]` = 사람 수행.

### 1단계: devflow-state.md 정합 갱신 [자동 + LLM]

- `[자동]` git log -1 HEAD == state.md HEAD 비교
- `[자동]` code-plan.md 마지막 phase vs state.md 기록 phase 비교
- `[자동]` 실제 test count 측정 (`pytest --collect-only -q | tail -1`)
- `[LLM]` 위 3개 데이터로 state.md 본문 재작성 (mismatch 항목 사용자에게 표시 후 갱신)

### 2단계: project auto-memory 정밀 갱신 [LLM]

- `[LLM]` project auto-memory 디렉토리 식별:
  - 위치: `~/.claude/projects/<encoded-cwd>/memory/`
  - `<encoded-cwd>`는 현재 작업 디렉토리 절대 경로의 URL-safe 인코딩 (슬래시→하이픈, 예: `/Users/jay/repo` → `-Users-jay-repo`)
  - 디렉토리 부재 시 → 본 단계 skip + audit emit `pause-checklist-completed`에 `auto-memory=skipped` 필드 추가
- `[LLM]` 다음 메모리 갱신:
  - 진행 중인 task의 commit 해시, test 결과, resume point, architecture 요점
- `[LLM]` 갱신 항목을 사용자에게 보여주고 승인 받음

### 3단계: MEMORY.md index + project_backlog description 갱신 [자동]

- `[자동]` MEMORY.md index 라인의 description 부분을 최신 상태로 업데이트
- `[자동]` 백로그 description 라인이 최근 commit과 일관되는지 비교 → mismatch 시 갱신

### 4단계: audit.md session-end marker append + commit [자동]

- `[자동]` audit.md에 다음 emit:
  `[<ISO timestamp>] session-paused | branch=<name> | head=<short-hash> | resume-point=<phase>`
- `[자동]` git stage: `devflow-docs/audit.md` + 갱신된 state/MEMORY.md 등
- `[자동]` `chore(devflow): session pause checklist` 메시지로 commit

### 5단계: 3-way cross-check [자동 + 사용자]

- `[자동]` 3-way 비교:
  - `git log -1 --format=%H` == state.md HEAD ?
  - state.md 마지막 phase == auto-memory commit ?
- `[자동]` 모두 일치 → audit emit `pause-checklist-completed` → ✅ Pause 완료
- `[자동]` drift 감지 → audit emit `pause-drift-detected` + 사용자 게이트 표시:
  ```
  ⚠️ 3-way drift 감지:
    - git HEAD: <hash-A>
    - state.md HEAD: <hash-B>
    - auto-memory commit: <hash-C>

  A) git HEAD 기준 재작성 (사용자가 명시 선택해야 발동 — 자동 아님)
  B) 수동 reconcile (사용자가 직접 state/memory 수정)
  C) 그대로 pause (drift 상태로 종료, resume 시 다시 게이트)
  ```
- `[사용자]` A/B/C **명시 선택** 필수 (default action 없음).
  - A 선택 시: 본 skill이 git HEAD 기준으로 state.md 재작성 → audit emit `pause-reconciled | strategy=auto-from-git`
  - B 선택 시: 사용자에게 컨트롤 반환 → 사용자 작업 완료 후 본 skill 5단계 재실행 → audit emit `pause-reconciled | strategy=manual` (재실행 시 일치 확인되면)
  - C 선택 시: audit emit `pause-checklist-completed | drift=accepted` (drift 표시 보존)

> **TR-3 일관성**: 옵션 A는 *사용자가 선택해야 발동하는* gated 동작이지, 자동(silent)으로 일어나지 않는다. silent auto-reconcile은 본 plan에서 채택 안 함.

## audit.md emit prefix (4종)

| Prefix | 시점 | 의미 |
|---|---|---|
| `session-paused` | 4단계 marker | pause 시작 |
| `pause-checklist-completed` | 5단계 자동 일치 시 | 정상 종료 |
| `pause-drift-detected` | 5단계 drift 시 | 게이트 진입 |
| `pause-reconciled` | 5단계 옵션 A/B 후 | reconcile 완료 |

## Examples

### Example 1: 정상 pause (drift 없음)

[5단계 정상 흐름 + audit log + state.md 갱신 결과 표시]

### Example 2: drift 감지 + 자동 reconcile (옵션 A)

[BL-P2-085 시나리오 재현: state.md Phase 1만 → auto-memory Phase 5 → git HEAD 일치 → 옵션 A 선택 → state.md를 git 기준으로 재작성]

## Troubleshooting

### auto-memory 디렉토리 부재
~/.claude/projects/.../memory/ 부재 → 2단계 skip + audit emit `pause-checklist-completed`에 `auto-memory=skipped` 필드 추가.

### git uncommitted changes 다수
4단계 commit 시 unrelated 변경이 staged면 사용자에게 확인 받음 (auto-stage 금지).

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- pause 결과: success | drift-detected | aborted
- audit emit count: 4 (정상) / 1-3 (skip/abort)
- next resume point: <phase>
```

- [ ] **Step 3: skill-reviewer로 검증**

`skills/_shared/reviewers/skill-reviewer-prompt.md`를 서브에이전트로 dispatch. 결과 ❌ 시 수정 후 재검증 (최대 5회).

- [ ] **Step 4: 정합성 체크**

`docs/guide/consistency-checklist.md` 5종 항목 적용. SKILL.md 추가로 영향 받는 다른 skill 검색:
```bash
grep -rn "pausing\|pause" skills/ devflow-docs/ docs/
```

- [ ] **Step 5: Commit**
```bash
git add skills/aidlc-pausing-a-session/SKILL.md
git commit -m "feat(skills): aidlc-pausing-a-session 스킬 추가 (BL-097 Phase 1 MVP) (refs #189)"
```

---

### Task 2: using-devflow Resume Flow drift detect 게이트 추가

**Files:**
- Modify: `skills/aidlc-using-devflow/SKILL.md` — Resume Flow 섹션 (line 118 이후)

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/test_using_devflow_resume_drift.py
def test_resume_detects_3way_drift(tmp_path, monkeypatch):
    """Resume 진입 시 git HEAD, state.md HEAD, auto-memory commit이 다르면 drift detect prompt 출력."""
    # GIVEN: state.md HEAD = abc123 / git HEAD = def456 / auto-memory = ghi789
    # WHEN: Resume Flow 진입
    # THEN: stdout에 "3-way drift 감지" 포함 + audit에 resume-drift-detected emit
    ...

def test_resume_proceeds_without_drift(tmp_path, monkeypatch):
    """3-way 일치 시 정상 Resume."""
    ...
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

Run: `pytest tests/test_using_devflow_resume_drift.py -v`
Expected: FAIL with "3-way drift 감지 prompt 미출력"

- [ ] **Step 3: 최소 구현 — Resume Flow의 step 2 안에 서브블록 추가**

**삽입 anchor**: `skills/aidlc-using-devflow/SKILL.md`의 Resume Flow `2. devflow-docs/session-summary.md 읽기 (있으면)` 항목 안의 **Memory Sync Staleness Check 서브블록 직후** + **`3. 백로그 확인 (Lazy Loading)` 직전**. 즉 step 번호는 그대로 1./2./3. 유지하고, step 2 안에 새 서브블록 추가 (BL-092 staleness check 형식 일관).

추가할 서브블록:

```markdown
   **3-way Drift Detect** *(BL-097, devflow-state.md 존재 시):
   - **3-way 비교**:
     - git HEAD: `git rev-parse HEAD`
     - state.md HEAD: state.md frontmatter 또는 본문에서 추출
     - auto-memory commit: `~/.claude/projects/<encoded-cwd>/memory/`의 가장 최근 메모리 commit field
   - **drift 감지 시** — `devflow-docs/audit.md`에 한 줄 append:
     `[<ISO timestamp>] resume-drift-detected | git=<hash-A> | state=<hash-B> | memory=<hash-C>`
   - **사용자 게이트**:
     "⚠️ 3-way drift 감지 — 마지막 pause 이후 정합성 깨짐. A) aidlc-pausing-a-session 재실행으로 sync 후 Resume (권장) / B) drift 상태 수용하고 그대로 Resume"
   - **A 선택 시**: `aidlc-pausing-a-session` 호출 후 다시 Resume Flow 진입
   - **B 선택 시** — audit emit:
     `[<ISO timestamp>] resume-drift-skipped | git=<hash-A> | state=<hash-B> | memory=<hash-C>`
   - drift 미감지 시 → 게이트 표시 안 함 (no-op)
```

> 본 서브블록은 step 2의 "Memory Sync Staleness Check" 서브블록과 동일한 들여쓰기·형식을 따른다. step 번호 1/2/3 변경 없음.

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_using_devflow_resume_drift.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**
```bash
git add skills/aidlc-using-devflow/SKILL.md tests/test_using_devflow_resume_drift.py
git commit -m "feat(skills): Resume Flow에 3-way drift detect 게이트 추가 (BL-097 Phase 1) (refs #189)"
```

---

### Task 3: audit emit prefix 명세 + emit 인라인 로직

**Files:**
- Modify: `skills/aidlc-pausing-a-session/SKILL.md` — emit 인라인 로직 추가
- Modify: `skills/_shared/devflow-conventions.md` — audit prefix 표 추가

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/test_pausing_a_session_audit_emit.py
def test_pause_emits_4_prefixes_normal(tmp_path):
    """정상 pause 시 4종 prefix 중 session-paused + pause-checklist-completed 2종 emit."""
    ...

def test_pause_emits_drift_prefix(tmp_path):
    """drift 감지 시 pause-drift-detected emit + 사용자 옵션 A 시 pause-reconciled emit."""
    ...
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

Run: `pytest tests/test_pausing_a_session_audit_emit.py -v`
Expected: FAIL

- [ ] **Step 3: emit 로직 인라인 (BL-098 머지 전 임시)**

본 plan의 emit 메커니즘은 **BL-092 memory-sync 패턴과 동일하게 인라인 Edit append** (devflow-audit utility의 markdown stage 형식이 아닌, 한 줄 형식). devflow-audit utility 본문의 stage 형식과 본 emit은 별개 ─ utility 형식 정합화는 BL-098 머지 시 표준화.

SKILL.md에 다음 명세 + 인라인 emit 절차 추가:

```markdown
## audit emit 명세 (BL-098 #191 머지 후 표준화 예정)

### 형식

`devflow-docs/audit.md`에 한 줄 append (BL-092와 동일 형식):

[<ISO timestamp>] <prefix> | <field>=<value> | ...

### prefix 4종

| Prefix | timing | required fields |
|---|---|---|
| `session-paused` | 4단계 marker | branch, head, resume-point |
| `pause-checklist-completed` | 5단계 일치 시 또는 옵션 C drift=accepted | branch, head, [drift, auto-memory] |
| `pause-drift-detected` | 5단계 drift 감지 직후 | git, state, memory |
| `pause-reconciled` | 옵션 A 또는 B 완료 후 | strategy(auto-from-git|manual) |

### 인라인 emit 절차 (skill 본문에서 직접 실행)

<!-- TODO(BL-098): unify with standard audit emit pattern after #191 merges -->

bash:
```bash
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "[${TS}] ${PREFIX} | ${FIELDS}" >> devflow-docs/audit.md
```

또는 Edit tool 호출 시:
- Read `devflow-docs/audit.md`
- Edit append (마지막 줄 뒤에 신규 줄 추가)
- 절대 Write tool로 전체 재작성 금지 (devflow-audit utility의 critical rule 준수)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_pausing_a_session_audit_emit.py -v`
Expected: 2 passed

- [ ] **Step 5: devflow-conventions.md에 prefix 표 추가**

`skills/_shared/devflow-conventions.md` audit prefix 섹션에 4종 추가. BL-098 prefix들과 같은 표.

- [ ] **Step 6: Commit**
```bash
git add skills/aidlc-pausing-a-session/SKILL.md skills/_shared/devflow-conventions.md tests/test_pausing_a_session_audit_emit.py
git commit -m "feat(skills): pausing-a-session audit emit 4종 prefix 명세 (refs #189)"
```

---

### Task 4: 회귀 테스트 — nexttui BL-P2-085 시나리오

**Files:**
- Create: `tests/test_bl097_p2_085_regression.py`

> **본 Task는 통합 검증 (integration verification)** — Task 1-3에서 이미 unit/component 테스트 작성됨. Task 4는 BL-P2-085 시나리오 전체를 end-to-end로 검증하는 회귀 테스트로, TDD Red→Green 순서가 아닌 통합 검증 단계로 작성한다.

- [ ] **Step 1: BL-P2-085 fixture 정의 (구체 내용)**

다음 fixture 데이터를 `tests/fixtures/bl097_p2_085/`에 생성:

`tests/fixtures/bl097_p2_085/devflow-state.md` (stale — Phase 1만 기록):
```markdown
# Devflow State

## Current Phase: Phase 1
**Last Updated**: 2026-04-27T10:00:00Z
**HEAD**: <fixture_old_hash>

### Completed
- Phase 1: 초기 설계
```

`tests/fixtures/bl097_p2_085/code-plan.md` (실제 Phase 5까지 done):
```markdown
# Code Plan

## Phase 1: 초기 설계 [Done]
## Phase 2: ... [Done]
## Phase 3: ... [Done]
## Phase 4: ... [Done]
## Phase 5: 통합 + 검증 [Done]
```

`tests/fixtures/bl097_p2_085/auto-memory-snapshot.md` (가장 최근 메모리, Phase 5 commit hash 보유):
```markdown
---
name: project_p2_085
description: nexttui BL-P2-085 작업 중
type: project
last_commit: <fixture_phase5_hash>
phase: Phase 5 done
---
```

`<fixture_old_hash>`와 `<fixture_phase5_hash>`는 fixture git repo 초기화 시 실제 git rev-parse로 생성.

- [ ] **Step 2: 회귀 테스트 작성**

```python
# tests/test_bl097_p2_085_regression.py
import subprocess
import shutil
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "bl097_p2_085"

def _setup_fixture_repo(tmp_path):
    """fixture를 tmp git repo로 복사 + Phase 1 commit + Phase 5 commit 2개 생성."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
    # Phase 1 commit
    (repo / "devflow-docs").mkdir()
    shutil.copy(FIXTURE / "devflow-state.md", repo / "devflow-docs" / "devflow-state.md")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Phase 1"], cwd=repo, check=True)
    old_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    # Phase 5 commit (state.md는 update 안 함 — drift 의도적 생성)
    (repo / "code-plan.md").write_text((FIXTURE / "code-plan.md").read_text())
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Phase 5"], cwd=repo, check=True)
    new_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    return repo, old_hash, new_hash

def test_p2_085_pause_detects_drift(tmp_path):
    """state.md가 Phase 1만 기록한 상태에서 pause skill 실행 → drift 감지 + audit emit."""
    repo, old_hash, new_hash = _setup_fixture_repo(tmp_path)
    # WHEN: aidlc-pausing-a-session 5단계 실행 (skill 호출 시뮬레이션 — 실제 구현 호출)
    result = run_pausing_skill(cwd=repo, drift_choice="C")  # 옵션 C: 그대로 pause
    # THEN: audit emit 확인
    audit = (repo / "devflow-docs" / "audit.md").read_text()
    assert "pause-drift-detected" in audit
    assert f"git={new_hash[:7]}" in audit  # short hash
    assert "state=" in audit and old_hash[:7] in audit  # stale state.md 의 old hash
    assert "pause-checklist-completed | drift=accepted" in audit

def test_p2_085_pause_option_a_reconciles_state(tmp_path):
    """옵션 A 선택 시 state.md가 git HEAD 기준으로 재작성됨."""
    repo, old_hash, new_hash = _setup_fixture_repo(tmp_path)
    result = run_pausing_skill(cwd=repo, drift_choice="A")
    state_md = (repo / "devflow-docs" / "devflow-state.md").read_text()
    assert new_hash[:7] in state_md  # state.md HEAD가 git HEAD로 갱신
    assert "Phase 1만" not in state_md  # stale 표지 제거
    audit = (repo / "devflow-docs" / "audit.md").read_text()
    assert "pause-reconciled | strategy=auto-from-git" in audit

def test_p2_085_resume_detects_drift(tmp_path):
    """drift 상태(옵션 C로 pause)에서 Resume Flow 진입 시 drift detect prompt."""
    repo, old_hash, new_hash = _setup_fixture_repo(tmp_path)
    run_pausing_skill(cwd=repo, drift_choice="C")  # 의도적 drift 보존
    # WHEN: Resume Flow 진입
    result = run_resume_flow(cwd=repo, drift_choice="B")  # B) 그대로 Resume
    audit = (repo / "devflow-docs" / "audit.md").read_text()
    assert "resume-drift-detected" in audit
    assert "resume-drift-skipped" in audit  # B 선택의 결과
```

- [ ] **Step 3: 테스트 실행 (Task 1-3 구현 후 PASS)**

Run: `pytest tests/test_bl097_p2_085_regression.py -v`
Expected: 3 passed

> Task 4는 통합 검증이라 Task 1-3 머지 후 직접 통과 기대. fixture 자체가 Task 1-3 구현 spec과 1:1 매핑.

- [ ] **Step 4: Mutation 검증 — fixture 변경 시 실패 확인**

회귀 테스트가 fixture에 의존하는지(즉 stale state.md를 정상 state.md로 바꾸면 실패하는지) 수동 확인:

```bash
# fixture 임시 변경: stale state.md를 phase 5로 갱신
sed -i.bak 's/Phase 1$/Phase 5/' tests/fixtures/bl097_p2_085/devflow-state.md
pytest tests/test_bl097_p2_085_regression.py::test_p2_085_pause_detects_drift -v
# Expected: FAIL (drift가 사라졌으므로)
mv tests/fixtures/bl097_p2_085/devflow-state.md.bak tests/fixtures/bl097_p2_085/devflow-state.md
```

이 mutation이 실패해야 회귀 테스트가 의미 있음. PASS면 테스트가 trivial mock — 실제 회귀 검증 못 함.

- [ ] **Step 5: 전체 테스트 실행 — 회귀 없음 확인**

Run: `pytest -v`
Expected: 모든 기존 테스트 통과 + 본 회귀 테스트 3건 통과

- [ ] **Step 6: Commit**
```bash
git add tests/test_bl097_p2_085_regression.py tests/fixtures/bl097_p2_085/
git commit -m "test(skills): BL-P2-085 회귀 테스트 + fixture 추가 (BL-097 acceptance) (refs #189)"
```

---

### Task 5: backlog 정리 + PR 생성

**Files:**
- Modify: `devflow-docs/backlog.md`
- Create: PR

- [ ] **Step 1: backlog.md 정리**

BL-097 항목을 Next에서 제거 (Done 처리 — git history로 추적).

- [ ] **Step 2: 영향도 검토 + 운영자 가이드 갱신**

```bash
grep -rn "pausing-a-session\|aidlc-pausing" docs/ devflow-docs/ skills/
```
- `docs/guide/operator-guide.md`에 "mid-cycle pause 시 본 skill 사용" 안내 추가 (메모리 feedback `feedback_operator_guide_recommendations.md` 적용).

- [ ] **Step 3: 정합성 체크**

`docs/guide/consistency-checklist.md` 5종 항목 모두 통과 확인.

- [ ] **Step 4: PR 생성**

```bash
gh pr create --repo bluejayA/aidlc-devflow --title "feat(skills): aidlc-pausing-a-session 스킬 추가 (BL-097 Phase 1)" --body "$(cat <<'EOF'
Closes #189

## Summary
- mid-cycle pause 시 devflow-state.md / project auto-memory / git log 3-way drift 방지 advisory 스킬 추가
- aidlc-using-devflow Resume Flow에 drift detect 게이트 추가 (BL-092 advisory 패턴 일관)
- 4종 audit prefix (session-paused / pause-checklist-completed / pause-drift-detected / pause-reconciled)

## 트레이드오프 결정
plan 문서 §트레이드오프 6건 참조 — automation tier 분리, gitignore 정책 유보, advisory 게이팅, MVP 최소화

## Test plan
- [ ] tests/test_pausing_a_session_audit_emit.py 통과 (2 cases)
- [ ] tests/test_using_devflow_resume_drift.py 통과 (2 cases)
- [ ] tests/test_bl097_p2_085_regression.py 통과 (3 cases — pause drift / option A / resume drift)
- [ ] BL-P2-085 fixture mutation 검증 (stale state.md → phase 5로 갱신 시 회귀 테스트 FAIL 확인)
- [ ] pytest 전체 회귀 0건
- [ ] skill-reviewer-prompt 검증 ❌ 0건
- [ ] docs/guide/consistency-checklist.md 5종 항목 통과
- [ ] skills/_shared/devflow-conventions.md prefix 표에 4종 prefix 추가 머지
- [ ] devflow-docs/backlog.md BL-097 항목 정리 (Done 처리)
- [ ] 트레이드오프 6건(TR-1~TR-6) + TR-7(BL-099 영향) 본 PR body에 요약 (선택지 / 결정 / 근거 1줄씩)
EOF
)"
```

- [ ] **Step 5: 머지 후 GitHub Project 상태 갱신**

메모리 feedback `feedback_github_project_workflow.md`: PR 머지 시 In progress → Done. 이슈 종료 코멘트 + 클로즈.

---

## Phase 2 (확장) — 별도 BL 후보

본 plan에서는 다루지 않는다. T+28(2026-05-12) 이후 데이터 누적 + 추가 사례 발생 시 새 BL로 작성한다.

### 후보 항목

1. **devflow-state.md gitignore 정책 결정** — 옵션 A(해제) vs C(Hybrid) 데이터 기반 선택 (TR-2 deferred)
2. **자동 reconcile 정교화** — 단순 git 기준 재작성 외에 LLM-driven semantic reconcile
3. **다중 사례 일반화** — 추가 사례(P2-XXX) 발견 시 5단계 일반화 검증 (TR-6 deferred)
4. **boundary contract table 적용** (Codex 권고) — write owner / idempotency key / commit point per boundary 명세
5. **discriminating counters 본격 도입** (BL-098 #191 머지 후) — paused-attempted / drift-detected / reconciled-auto / reconciled-manual. **TR-5 cross-link**: BL-098 머지 시 본 skill의 인라인 emit 로직을 표준 emit 패턴으로 교체.

---

## Acceptance Criteria

본 plan(Phase 1)의 완료 기준 (모두 객관 검증 가능):

- [ ] `aidlc-pausing-a-session` SKILL.md 머지 + skill-reviewer ❌ 0건
- [ ] using-devflow Resume Flow의 step 2 안에 "3-way Drift Detect" 서브블록 머지 (step 1/2/3 번호 변경 없음)
- [ ] 4종 audit emit prefix 명세 + 인라인 emit bash snippet 머지
- [ ] BL-P2-085 시나리오 회귀 테스트 통과 (3 cases)
- [ ] BL-P2-085 fixture mutation 검증 (stale state.md를 phase 5로 변경 시 `test_p2_085_pause_detects_drift` FAIL 확인)
- [ ] pytest 전체 통과 (회귀 0건)
- [ ] `skills/_shared/devflow-conventions.md` prefix 표에 4종 prefix(`session-paused` / `pause-checklist-completed` / `pause-drift-detected` / `pause-reconciled`) 추가
- [ ] `devflow-docs/backlog.md` BL-097 항목 Done 처리
- [ ] PR body 첫 줄 `Closes #189` 포함
- [ ] `docs/guide/consistency-checklist.md` 5종 항목 통과
- [ ] `docs/guide/operator-guide.md`에 mid-cycle pause skill 안내 추가
- [ ] 트레이드오프 7건(TR-1~TR-6 + TR-7) 본 plan + PR body에 요약 포함

---

## Self-Review Checklist (작성자 체크)

본 plan을 셀프 리뷰한다 (writing-plans skill 표준):

1. **Spec coverage**: BL-097 issue body의 5단계 + 적대적 리뷰 권고가 모든 Task에 반영되었는가?
   - 5단계 → Task 1 (SKILL.md 본문)
   - Resume Flow drift detect → Task 2
   - audit emit 4종 → Task 3
   - BL-P2-085 시나리오 검증 → Task 4
   - backlog 정리 → Task 5
   - 트레이드오프 6건 → 상단 §트레이드오프 결정
   - ✅ Coverage 충족

2. **Placeholder scan**: TBD/TODO 없음. 코드 블록 모두 완성. 파일 경로 모두 절대 또는 명확한 상대 경로.

3. **Type consistency**: prefix 명명 일관 (`session-paused` / `pause-*`), tier 표기 일관 (`[자동]` / `[LLM]` / `[사용자]`).

---

## Plan Review Loop

본 plan 저장 후 `_shared/reviewers/plan-document-reviewer-prompt.md`를 서브에이전트로 dispatch한다 (skill 본문 §Plan Review Loop). 

- ❌ Issues Found → 수정 후 재dispatch (최대 5회)
- Recommendations만 → 루프 종료
- 5회 초과 → 사용자 escalate

---

## Codex Round 3 Findings (2026-04-29) — No-ship

본 plan v1에 대한 Codex adversarial review (`/codex:adversarial-review`) 결과. plan-document-reviewer가 검출하지 못한 동작·안전성 영역. **다음 세션에서 plan v2로 모두 처리 필요**.

### Verdict (verbatim)

**No-ship**. 이 plan은 핵심 동기화 플로우의 원자성/재진입 안전성, cross-project memory 경계, 회귀 검증력에서 블로킹 리스크가 남아 있어 병렬 실행(특히 BL-098/099) 시 실패를 숨기거나 상태 드리프트를 고착시킬 가능성이 큽니다.

### Findings (verbatim)

#### F1. [high] Commit point가 drift 검증보다 앞서 있어 불일치 상태를 영구화할 수 있음 (line 160-187)

Step 4에서 `session-paused` emit + commit을 먼저 수행하고(라인 160-166), Step 5에서야 3-way drift를 판정/재조정합니다(라인 167-187). 이 순서는 drift 상태를 이미 커밋한 뒤에 reconcile을 시도하게 만들어 partial failure 시 audit/state가 서로 다른 truth를 갖게 됩니다. 또한 Resume 쪽 A 경로가 pause 재실행 후 Resume 재진입만 정의하고(라인 287), 수렴 조건/중복 방지 키가 없어 반복 감지-재진입 루프가 가능합니다. 영향은 사용자-visible 상태 불일치, 중복 audit marker, 재개 루프입니다.

**Recommendation**: commit point를 Step 5 성공 이후로 이동하고, Step 4는 임시 marker append까지만 허용하세요. `session_id`/`idempotency key`를 도입해 pause/resume 재진입 시 동일 이벤트 중복 기록을 차단하고, Resume A-path에는 최대 1회 재검증 후 실패 시 명시적 abort 경로를 추가하세요.

#### F2. [high] auto-memory 업데이트 경계가 느슨해 다른 프로젝트 메모리 오염 위험이 있음 (line 147-153)

auto-memory 대상 선택 규칙이 `~/.claude/projects/<encoded-cwd>/memory/` 추정과 디렉토리 부재 skip만 정의되어 있고(라인 147-150), 다중 후보/심볼릭 링크/경로 이탈 차단이 없습니다. 이 상태에서 LLM이 memory를 갱신하도록 지시하면(라인 151-153) 잘못된 프로젝트 memory를 수정할 수 있습니다. 이는 tenant isolation 성격의 데이터 오염 리스크입니다.

**Recommendation**: 대상 경로를 exact-match + fail-closed로 제한하세요: 후보 0개/2개 이상이면 무조건 중단, symlink 금지, base dir prefix 검증 필수. 실패 사유를 `auto-memory=skipped|reason=*`로 audit에 남기고 write는 금지하세요.

#### F3. [high] 회귀 테스트 설계가 실행 경로를 검증하지 못하고 단일 사례에 과적합됨 (line 396-519)

핵심 테스트가 `run_pausing_skill`/`run_resume_flow` 호출을 전제로 하지만(라인 470, 481, 493) plan 내 어디에도 해당 실행 하네스 구현 태스크가 없습니다. 또한 검증 축이 BL-P2-085 단일 fixture + 단일 mutation에 집중되어(라인 396-519, 610-612) race/재시도/부분실패를 잡지 못합니다. 결과적으로 '테스트 통과'가 실제 회귀 방지 능력을 보장하지 못할 가능성이 큽니다.

**Recommendation**: 먼저 테스트 실행 모델을 명시하세요: (1) 정적 규약 테스트와 (2) transcript/시뮬레이터 기반 동작 테스트를 분리. 그리고 최소 3개 adversarial fixture를 추가하세요: no-drift 정상 케이스, Step4~Step5 사이 HEAD 변동 경쟁 케이스, auto-memory 경로 다중 후보 케이스.

#### F4. [medium] BL-098/099 병렬 전제인데 의존성 정렬 게이트가 없어 관측 포맷 드리프트 위험 (line 15-47)

문서는 선결 없음/병렬 가능을 선언하면서(라인 15) BL-098 전 임시 emit 인라인을 허용합니다(라인 45-47, 332-370). 하지만 수용 기준은 prefix 존재 여부 중심이라(라인 609, 613) BL-098 표준과 충돌/중복 emit이 생겨도 통과할 수 있습니다. 관측 품질이 핵심인 변경에서 이는 실패 은닉으로 이어집니다.

**Recommendation**: 병렬 실행 조건을 명시적 게이트로 바꾸세요. `if BL-098 merged -> 인라인 emit 금지 + 표준 emitter만 허용`, `if not merged -> migration task(인라인 제거)와 호환성 테스트를 완료해야 merge`를 AC에 추가하세요.

### Next steps (verbatim)

- Step 4/5를 원자적 트랜잭션으로 재설계하고 재진입 한계/중복 방지 규칙을 문서화
- auto-memory 경로 선택을 fail-closed 정책으로 강화하고 관련 테스트를 추가
- BL-098/099와의 병렬 조건을 명시적 merge gate와 호환성 테스트로 고정

### Plan v2 수정 범위 (다음 세션 진입점)

| Finding | 수정 위치 | 신규 / 갱신 |
|---|---|---|
| F1 (트랜잭션) | Task 1 §5단계 + TR-3 + Task 2 Step 3 (Resume A-path) | 갱신 — Step 4/5 재배치, idempotency key 도입 |
| F2 (auto-memory 경계) | Task 1 §2단계 + Task 4 fixture | 갱신 — fail-closed 정책 명문화 |
| F3 (실행 하네스) | **신규 Task 0** (실행 하네스 + 시뮬레이터) + Task 4 fixture 확장 | 신규 task 추가 |
| F4 (BL-098 게이트) | TR-5 + Acceptance Criteria | 갱신 — merge gate 분기 명시 |

### 두 리뷰의 보완 관계 (메모) — 다음 세션 컨텍스트

- **plan-document-reviewer**: 경로/번호/일관성/문서 구조 = 형식 정합성
- **Codex adversarial**: 트랜잭션/원자성/race/cross-project boundary/실행 하네스 = 동작 안전성
- 단일 review로는 동작 안전성 영역을 못 잡는다. **2-track 리뷰가 표준 패턴화 후보** (별도 BL 후보).

---

## References

- BL-097 issue: https://github.com/bluejayA/aidlc-devflow/issues/189
- T+14 결과 + 진단: `docs/research/knowledgesystem/redteam-3rd-result.md`
- 관측 update + alternative-ban exception: `docs/research/knowledgesystem/phase2-observation-update.md`
- 형제 skill: `skills/aidlc-finishing-a-development-branch/SKILL.md`
- Resume Flow 위치: `skills/aidlc-using-devflow/SKILL.md` line 118-135
- BL-098 audit emit (병행): #191
- BL-099 invoke_mode 정합성 (병행): #192
- skill 작성 가이드: `skills/_shared/patterns/skill-writing-guide.md`, `skill-design-patterns.md`, `skill-pattern-catalog.md`
- 메모리: `project_knowledge_system_phase1.md`, `project_bl092_observation.md`
