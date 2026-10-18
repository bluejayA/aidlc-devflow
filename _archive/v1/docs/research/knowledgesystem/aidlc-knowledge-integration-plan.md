# aidlc-devflow Knowledge System Integration Plan (Phase 1)

> **Date**: 2026-04-13
> **Scope**: aidlc-devflow plugin v1.9.0 → v1.10.0 (planned)
> **Companion docs**: `knowledge-taxonomy.md`, `executable-next-steps.md`

---

## 1. Current State Summary

### 1.1 What aidlc v1.9.0 already has (ground truth from SKILL.md declarations)

- **SessionState** infrastructure: `devflow-state.md` (heading-based Markdown) + `session-summary.md`, 7+ skills read/write
- **Solution** infrastructure: `devflow-solutions` utility + `construction-orchestrator` K-gate invocation (currently untriggered — no `devflow-docs/solutions/` directory yet)
- **Evidence** infrastructure: `devflow-audit` utility → `devflow-docs/audit.md` (append-only; at analysis time 10.4KB / 79 entries / 3 days of activity), `superpowers-tracking` → `devflow-docs/tracking/*.md`
- **Decision** infrastructure: `aidlc-brainstorming` → `docs/plans/*-design.md`, `aidlc-writing-plans` → `docs/plans/*-plan.md`, 7 inception/construction skills → `devflow-docs/{inception,construction}/*.md`
- **Pattern** library: `skills/_shared/patterns/*.md` (17), `_shared/reviewers/*.md` (12), `_shared/*-protocol.md` (4) — weak frontmatter
- **Skill** library: 28 `aidlc-*` + 3 `_utils` with metadata (version, invoke_mode, return_behavior), but BL-081 `skill_nature` field not yet applied

### 1.2 Known gaps / issues

| Gap | Impact | Resolution location |
|-----|--------|---------------------|
| 28 skills lack `skill_nature` | No promotion path between Skill ↔ Pattern | executable-next-steps §4 |
| Pattern frontmatter too weak | Cannot validate freshness, applicability | executable-next-steps §3 |
| `devflow-audit.md` vs `audit.md` divergence (4 stale refs) | Writes to wrong file possible | executable-next-steps §1 |
| `devflow-docs/devflow-audit.md` legacy file exists | Orphan, confusion risk | executable-next-steps §1 |
| K-gate STORE call-site semi-concrete (construction-orchestrator:319) | Contract ambiguous | executable-next-steps §2 |
| `audit.md` growth rate (≈3.5KB/day) | Token budget pressure within months | 5e rotation plan |
| `inception-orchestrator:386` writes to `design-review-raw/` but absent from current taxonomy | Missed Evidence surface | Taxonomy §2.5 updated |

### 1.3 Codebase hygiene findings (from Codex review)

- Archived files in `.archive/` and `devflow-state-archived-*.md` are **normal size** (125-2344 bytes). Initial "0-byte" claim was analyst error.
- `tests/*.py` are implementation code, not Evidence. Out of taxonomy scope.
- `docs/research/*.md` are free-form workspace, not formal Decisions. Out of taxonomy scope until promoted.

---

## 2. Integration Strategy (A + C Hybrid)

Per user selection at Step 2:
- **A**: 기존 자산 흡수 + 점진 확장. Decision/Solution/Pattern/Skill/Evidence/SessionState의 실 저장소를 기존 경로로 확정.
- **C**: 지식 유형 경계 먼저 정의 (`knowledge-taxonomy.md`), 이후 그 경계에 맞춰 자산 재라벨.

### 2.1 Strategy principles

1. **Reclassify, don't duplicate**: 기존 파일을 재라벨링 (frontmatter 추가). 새 디렉토리 최소화.
2. **Existing writers preserved**: 28+ skill이 가진 output_path 선언을 건드리지 않음. 신규 쓰기 경로는 `devflow-docs/audit-log/YYYY-MM.md` 하나만.
3. **Phased migration**: 비파괴 (frontmatter 추가) → 소폭 파괴 (legacy 정리) → 신규 기능 (훅).
4. **Token-first design**: 모든 구조 변경에 토큰 영향 평가. Session start overhead ≤ +20% 강제.
5. **Heading format respected**: `devflow-state.md`의 heading-based Markdown 형식을 Sprint 1에서 유지. YAML 마이그레이션은 Sprint 2+.

### 2.2 Rejected / deferred from SPEC v0.3

- `.devflow/` 신규 디렉토리 — **거부** (devflow-docs/ 유지)
- `skills/knowledge/` vs `skills/workflow/` 분리 — **거부** (flat 유지)
- `adr-index.json` derived cache — **연기** (YAGNI)
- Thread 개념 — **연기** (Sprint 2+; Pattern + Decision.related로 대체)
- "Phase 1 = memory only, no enforcement" 철학 — **거부** (aidlc는 enforcement-heavy 시스템)

---

## 3. Directory Plan

### 3.1 No new top-level directories

모든 변경은 기존 루트 내부. 프롬프트 제약 준수.

### 3.2 Proposed structure (minimal changes)

```
devflow-aidlc-like/
├── CLAUDE.md                           [Pattern — 기존, 수정 없음]
├── skills/
│   ├── aidlc-*/SKILL.md                [Skill × 28, frontmatter 추가]
│   ├── _utils/
│   │   ├── devflow-state/SKILL.md      [Skill infra]
│   │   ├── devflow-audit/SKILL.md      [Skill infra]
│   │   └── devflow-solutions/SKILL.md  [Skill infra]
│   └── _shared/
│       ├── patterns/*.md               [Pattern × 17, frontmatter 강화]
│       ├── reviewers/*.md              [Pattern × 12, frontmatter 강화]
│       └── *-{protocol,pattern,convention}.md  [Pattern × 4]
├── docs/
│   └── plans/*-{design,plan}.md        [Decision × 14, frontmatter 추가]
├── hooks/
│   ├── hooks.json                      [수정: PostToolUse 추가]
│   ├── session-start                   [수정: 상태 라인 확장]
│   └── post-tool-file-edit             ★ 신규 shell script
└── devflow-docs/
    ├── devflow-state.md                [SessionState primary]
    ├── session-summary.md              [SessionState secondary]
    ├── audit.md                        [Evidence primary — legacy devflow-audit.md 제거]
    ├── audit-log/                      ★ 신규 (rotation 시 생성)
    │   └── YYYY-MM.md                  [Evidence kind=interaction, rotated]
    ├── backlog.md                      [Decision role=priority-queue]
    ├── tracking/session-*.md           [Evidence kind=summary]
    ├── inception/                      [Decision scope=flow]
    │   ├── *.md
    │   └── design-review-raw/          [Evidence kind=review-raw, on-demand]
    ├── construction/{unit}/            [Decision scope=flow]
    ├── solutions/{category}/           [Solution, K-gate trigger 시 생성]
    └── .archive/                       [Evidence kind=snapshot]
```

### 3.3 Deletions

- `devflow-docs/devflow-audit.md` (legacy, 1.8KB)

### 3.4 Preserved unchanged

- Flat skill structure (28 aidlc-* + 3 _utils)
- 모든 기존 output_path 선언
- `skills/_shared/` 전체 구조

---

## 4. Hook Integration Plan

### 4.1 Execution order principle

**Knowledge first, workflow second.** 기록이 먼저 있어야 분석 가능, 실패 시에도 log는 남아야 함.

### 4.2 Hook specifications

#### Hook A: session-start (EXTEND existing)

**현재**: `hooks/session-start` 쉘 스크립트. 배너 메시지만 출력.

**변경**: 배너 출력 **전**에 상태 라인 추가. `devflow-state.md`를 heading grep으로 파싱.

```bash
# 신규 로직 (pseudo):
if [ -f "devflow-docs/devflow-state.md" ]; then
  PHASE=$(grep -A1 '^## Current Phase' "$STATE" | tail -1 | xargs)
  STAGE=$(grep -A1 '^## Current Stage' "$STATE" | tail -1 | xargs)
  BRANCH=$(git branch --show-current 2>/dev/null || echo "-")
  UPDATED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$STATE")
  echo "📍 Flow: $PHASE / $STAGE | Branch: $BRANCH | Updated: $UPDATED"
  echo ""
fi
# 기존 배너 출력 이어서
```

**토큰 영향**: 상태 라인 1줄 ≈ 50 tokens.

**Sprint 2+ 확장 예약**: Pre-session nudge (미해결 backlog/deferred stubs 힌트).

#### Hook B: post-tool-file-edit (NEW)

**트리거**: `PostToolUse`, matcher `Edit|Write`

**책임**:
1. Path 필터링 (whitelist-first):
   - **Allow**: `devflow-docs/**`, `docs/**`, `skills/**`, `CLAUDE.md`
   - **Exclude**: `tests/`, `hooks/`, `.claude-plugin/`, `.git/`, `.worktrees/`, `devflow-docs/.archive/`, `devflow-docs/audit.md`, `devflow-docs/audit-log/`, `devflow-docs/devflow-state.md`
2. Allow + not Exclude일 때만 진행:
   - `audit.md`에 1 line append: `- [ISO timestamp] file-edit | $MODIFIED_PATH` (prefix는 taxonomy §2.5 Evidence event type 목록 준수)
   - `devflow-state.md` `## Last Updated` heading 아래 값 갱신 (soft-save)
3. `audit.md` 크기 > 100KB 시 stderr warning (실제 rotation은 Sprint 2)

**Race condition 방지 제약 (중요)**: 
- hook은 **오직 `## Last Updated` heading 값만** 수정한다.
- 구조 섹션 (`## Current Phase`, `## Current Stage`, `## Worktree`, `## WIP` 등) 절대 건드리지 않음.
- 구조 변경은 skill(using-devflow, auto-mode, finishing-a-development-branch 등)의 책임.
- 훅과 skill이 동시에 state.md를 쓰더라도 각자 다른 heading만 건드려 충돌 최소화.

**구현 파일**: `hooks/post-tool-file-edit` (~40 lines shell)

**hooks.json 변경**:
```json
"PostToolUse": [
  {
    "matcher": "Edit|Write",
    "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/post-tool-file-edit"}]
  }
]
```

**토큰 영향**: Hook은 stdout을 Claude에 emit하지 않음 → **0 tokens per invocation**.

**Self-amplification 방지**: audit.md / state.md / audit-log/ 자기 자신 편집은 exclude 목록으로 재진입 차단.

#### Hook C: session-end (DEFER)

Sprint 1 신규 훅 없음. 기존 `aidlc-using-devflow` / `aidlc-finishing-a-development-branch`가 flow 종료 처리.

#### Hook D: audit rotation (Sprint 2 full, Sprint 1 warning only)

Sprint 1: Hook B 내부에서 audit.md > 100KB 시 warning 로그만.
Sprint 2: 월 1일 또는 100KB 임계 초과 시 `audit.md` → `audit-log/YYYY-MM.md`로 이동 + fresh audit.md 생성.

---

## 5. Read Path per Operation

### 5.1 Session start (automatic)

**Minimal read** (기본 실행):
1. `devflow-state.md` heading 4개 추출 (`## Current Phase`, `## Current Stage`, `## Last Updated`, `## Active Unit`) — ~32 tokens
2. `git branch --show-current` — ~0 tokens
3. 상태 라인 1줄 format + 기존 banner — ~50 tokens

**Total: ~82 tokens**

### 5.2 Session start (on-demand, user triggered)

사용자가 "어디까지 했지", "resume", "/aidlc:aidlc-using-devflow" 등 명시:

| 파일 | Token cost |
|------|-----------|
| `devflow-state.md` 전체 | ~400 |
| `session-summary.md` 전체 | ~700 |
| `audit.md` tail 10 lines | ~150 |
| `backlog.md` Next 섹션 | ~100 |
| **Total** | **~1,350** |

**Budget 적용 제외**: 사용자 명시 요청. +20% cap은 자동 주입 오버헤드에만 적용.

### 5.3 File edit (per Edit/Write invocation)

- Hook B 실행 (stdout 없음)
- **Claude token cost: 0**

### 5.4 Decision creation (brainstorming / writing-plans)

- Skill이 직접 읽기/쓰기 (기존 동작)
- 선택적 pre-write: `docs/plans/` 내 유사 슬러그 grep — ~200 tokens
- devflow-audit utility가 1 line append (hook B와 별개)
- state.md의 decisions_made heading 아래 업데이트 (soft-save)

**Token cost: 0 ~ +200** (유사 확인은 skill 선택적)

### 5.5 Solution ingest (K-gate STORE)

- Construction-orchestrator가 debugging 종료 후 K-gate에서 `devflow-solutions` STORE 호출
- STORE 실행: Privacy Scrub + 검증 + Write — skill 내부, 사용자 프롬프트에 출력 없음
- Return 메시지 (SAVE/DUPLICATE/REJECT) — ~50 tokens

**Token cost: ~50** (Return 메시지만)

### 5.6 Ingest L2 (Sprint 1 미구현)

Sprint 2+로 연기. 기존 manual skill이 implicit L2.

---

## 6. Token Budget Analysis

### 6.1 Baseline measurement (보수 휴리스틱 1 token ≈ 2.5 bytes)

| Source | Bytes | Tokens |
|--------|-------|--------|
| SessionStart 기존 배너 | 260 | 75 |
| `~/CLAUDE.md` (user) | ~4,000 | ~1,600 |
| Project `CLAUDE.md` | 2,200 | ~880 |
| **Session start baseline** | **~6,460** | **~2,555** |

### 6.2 Sprint 1 additions at session start

| Addition | Tokens |
|----------|--------|
| state.md heading 파싱 | ~32 |
| 상태 라인 출력 | ~50 |
| **Total** | **~82** |

### 6.3 Constraint check

- **+20% cap**: `2,555 × 0.20 = +511 tokens` 예산
- **Actual addition**: +82 tokens (16% 예산 사용)
- **Guard band**: 100 tokens (banner drift, i18n 변동 대비)
- **Effective headroom**: 511 − 82 − 100 = **+329 tokens**

### 6.4 Growth projection

| Scenario | Token delta | Cumulative overhead |
|----------|-------------|---------------------|
| Current baseline | — | 2,555 |
| + Sprint 1 (state heading parse) | +82 | 2,637 |
| + Sprint 2 (L2 ingest nudge, deferred stubs hint) | +~150 | 2,787 |
| + Sprint 2 (pre-session audit tail 3 entries) | +~50 | 2,837 |
| **Sprint 2 total** | +282 | **2,837** |

Sprint 2 여유 = 511 − 282 = 229 tokens, 안전권.

### 6.5 On-demand read costs (not counted toward cap)

사용자 명시 트리거:
- "어디까지 했지" → ~1,350 tokens (일회성)
- "최근 활동" → audit.md tail 20 = ~300 tokens
- Decision 작성 pre-write 유사 확인 → ~200 tokens

### 6.6 audit.md 성장 관리

- 현재: 10.4KB / 3일 ≈ 3.5KB/day
- 100KB 임계 = 약 28일
- **Sprint 1**: warning only
- **Sprint 2**: 자동 rotation `audit-log/YYYY-MM.md`
- On-demand 읽기는 tail만 사용 → 전체 읽기 금지 (현재 10.4KB → 4,160 tokens로 단일 파일로 budget 초과)

### 6.7 Lazy loading strategies

- **Metadata first**: state.md 전체 body 대신 4개 heading 값만 (32 vs 400 tokens)
- **Tail-only**: audit.md 전체 대신 tail N lines (150 vs 4,160 tokens)
- **On-demand full**: 사용자 trigger 시에만 전체 로드
- **Symbolic reference**: `session-summary.md`는 skill이 명시 요청할 때만 로드 (기본 세션 시작 오버헤드 제외)

---

## 7. Migration Approach (Phase A-E)

**원칙**: 비파괴 먼저, 파괴적 변경은 canonical path 정리 후, 새 기능은 마지막.

### Phase A — Pattern/Skill frontmatter (non-destructive)

1. Pattern 17개 파일: required fields 추가 (`type`, `applies_to`, `status`, `source`, `last_validated`)
2. Skill 28개 `aidlc-*`: `skill_nature`, `lifecycle: active` 추가 (BL-081 초안 분류 적용)
3. Skill 3개 `_utils`: `skill_nature: null`, `lifecycle: active` 추가

**영향**: 기존 skill 동작 영향 없음 (읽기만, 동작 분기 없음).

### Phase B — Decision frontmatter (non-destructive)

4. `docs/plans/*.md` 14개: `scope: plugin`, `promotion_candidate: false`, provenance 4필드 추가
5. `devflow-docs/backlog.md`: `role: priority-queue` 필드 추가

**영향**: 기존 파일 본문 그대로. 메타만 증가.

### Phase C — Legacy cleanup (minor destructive)

6. `devflow-docs/devflow-audit.md` 삭제
7. Stale `devflow-audit.md` 참조 4곳 수정:
   - `skills/aidlc-auto-mode/SKILL.md:374`
   - `skills/aidlc-superpowers-tracking/SKILL.md:24`
   - `docs/plans/2026-04-02-auto-mode-plan.md:490`
   - `docs/plans/2026-04-02-auto-mode-design.md:306`
8. `aidlc-construction-orchestrator/SKILL.md:319` K-gate STORE call-site를 5개 필드 명시적으로 교체

**이유**: Phase D/E 신규 훅이 정규화된 canonical 경로 위에서 동작해야 함 (Codex 권고: legacy 정리 먼저).

### Phase D — Hook scaffolding (new feature)

9. `hooks/post-tool-file-edit` 신규 스크립트 작성 (path filter + audit append + soft-save)
10. `hooks/hooks.json` 업데이트 (PostToolUse Edit|Write matcher)
11. 테스트: tests/ 편집으로 제외 확인, devflow-docs/ 편집으로 포함 확인

### Phase E — Session start extension (new feature)

12. `hooks/session-start` 확장: state.md heading 4개 파싱 + 상태 라인 출력

**각 Phase 독립 커밋 가능.** 롤백 용이.

---

## 8. Existing Workflow Impact

### 8.1 Skills that continue without modification

- 28 `aidlc-*` skills: frontmatter 추가만. 로직 무변경.
- 3 `_utils`: frontmatter 추가만.
- `aidlc-brainstorming`, `aidlc-writing-plans` 출력: Phase B에서 Decision frontmatter 포함하도록 template 갱신 (선택적 — 기존 파일은 이미 있음).

### 8.2 Skills that need explicit update

- `aidlc-construction-orchestrator`: K-gate STORE 5-field 명시 (Phase C step 8)
- `aidlc-auto-mode`: line 374 `devflow-audit.md` → `audit.md` (Phase C step 7)
- `aidlc-superpowers-tracking`: line 24 텍스트 수정 (Phase C step 7)

### 8.3 Docs that need correction

- `docs/plans/2026-04-02-auto-mode-{plan,design}.md`: 본문 내 `devflow-audit.md` 참조 (Phase C step 7)

### 8.4 Tests impact

- `tests/test_devflow_solutions.py`: K-gate 호출 컨트랙트 변경 시 업데이트 필요 (Phase C step 8 적용 시)
- 기타 tests: 영향 없음

---

## 9. Success Criteria (Prompt 준수 확인)

| 기준 | 달성 여부 |
|------|-----------|
| No duplicate storage for same knowledge | ✅ 매 asset 단일 primary type |
| Every existing asset has exactly one primary type | ✅ Mapping table §5 |
| No new top-level directory | ✅ `audit-log/`는 devflow-docs/ 내부 |
| Session start token overhead ≤ +20% | ✅ +82 / +511 cap (16% 사용) |
| Existing workflows continue without modification, or changes explicitly documented | ✅ §8 documented |
| Read path defined for every operation | ✅ §5 |
| Hook execution order explicitly defined | ✅ §4.1 knowledge-first |

---

## 10. Out of scope (Sprint 1)

다음은 Sprint 2+ 예약:
- adr-index.json derived cache
- Thread 개념 + stub 자동 생성
- Git diff catch-up
- L2 ingest 신규 skill
- audit.md 자동 rotation 실제 이동 (Sprint 1은 warning only)
- YAML 마이그레이션 (state.md)
- shared/org tier 활성화
- BL-081 Compensation Decay 분석 + validator 확장
- **Pattern metadata 자동 갱신 / staleness 검출**. Phase 1은 `last_validated` 수동 갱신만. 2주~수개월 경과 시 stale 수용. Phase 2에서 validator script + refresh workflow 도입 검토.
- **audit.md signal_level 자동 분류 / filtering 로직**. Phase 1은 taxonomy §2.5의 event type prefix 스키마만 고정. Phase 2에서 실제 운영 데이터 기반으로 high/low signal 기준 수립 후 grep 필터 또는 summary skill 도입.

---

## 11. References

- Taxonomy: `knowledge-taxonomy.md`
- Executable patches: `executable-next-steps.md`
- Red-team prompt: `PROMPT-claude-code-knowledge-integration.md`
- Source of inspiration: `SPEC-knowledge-layer-sprint1-v0.3.md`, `aidlc-devflow-context-v2.1.md`
- BL-081 draft: `docs/research/2026-04-06-skill-lifecycle-strategy.md`
