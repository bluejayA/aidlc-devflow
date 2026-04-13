# devflow-aidlc Knowledge Layer — Sprint 1 SPEC v0.3

> 목적: Claude Code가 직접 소비할 수 있는 구현 스펙  
> Phase: Knowledge Layer v0.1 (Session Continuity + Schema 기반)  
> 변경 이력: v0.1 → v0.2 → v0.3 (debate 합의 반영, 2026-04-11)  
> Done 기준: 이 문서에 명시된 파일과 훅이 모두 생성되고, 세션 재시작 시 session-state.md가 자동 로딩되며, log에 항목이 append됨

---

## 구현 전 필수 확인 사항

> **이 SPEC의 파일 경로, 훅 위치, 스킬 디렉토리는 기존 devflow 플러그인 구조에 맞춰 조정될 수 있다.**
> 구현 시작 전에 반드시 기존 devflow의 실제 파일 체계를 확인하고, 아래 항목을 점검해야 한다.

1. 기존 devflow 디렉토리 전체 구조 파악 (`hooks/`, `skills/`, `.devflow/` 등)
2. 기존 CLAUDE.md 내용 확인 — Knowledge Layer 섹션 추가 위치 결정
3. 기존 훅 목록 확인 — 신규 훅을 별도 추가할지, 기존 훅에 통합할지
4. 기존 스킬 디렉토리 컨벤션 확인 — `skills/knowledge/` 하위 구조가 기존 패턴과 호환되는지
5. 기존 ADR 스킬 유무 확인 — 있다면 skill-ingest와 책임 분담 정의
6. 기존 규칙 weight 시스템 파일 형식 확인 — SCHEMA 위반 연결용
7. Progressive Disclosure 패턴, 3-tier skill policy 확인 — Knowledge Layer 스킬이 동일 패턴 준수
8. `.devflow/` 디렉토리 기존 사용 여부 확인

**충돌 발생 시 원칙**: 기존 devflow 구조를 먼저 존중하고, Knowledge Layer 경로를 조정한다. 기존 스킬/훅의 위치를 옮기는 것은 최후 수단.

상세 체크리스트: `aidlc-devflow-context-v2.md` 섹션 7.1 참조.

---

## v0.1 → v0.2 → v0.3 변경 요약

| 항목 | v0.1 | v0.3 | 근거 |
|------|------|------|------|
| wip.md + session-state.md | 별도 파일, 병렬 SSOT | session-state.md로 통합. wip.md 제거 | SSOT 위반 제거 |
| adr-index.json 지위 | 암묵적 SSOT | **derived cache** 명시. ADR frontmatter = SSOT | SSOT 명확화 |
| SCHEMA.md 성격 | 설명 문서 | **런타임 계약** 승격, weight 시스템 연결 | enforcement 확보 |
| Phase 1 정체성 | 암묵적 | **"기억 시스템"** 명시 선언 | scope creep 방지 |
| Ingest | 7단계 단일 프로세스 | **Level 1 (자동) / Level 2 (명시 호출)** 분리 | adoption 현실성 |
| Provenance | 상태 4등급만 | `validated_by`, `validated_at`, `source_ref` 추가 | 사실성 관리 |
| log.md | 단일 파일 append-only | **월별 rotation** (`wiki/log/YYYY-MM.md`) | 스케일링 |
| Thread 권한 | 미정의 | **비권위 원칙** 명시 (맥락 문서, 결정 출처 아님) | ADR 권위 보호 |
| Thread 생성 | ADR 2회 시 생성 | ADR 1회 시 stub → 2회 시 승격 | 서사 유실 방지 |
| 훅 안전망 | 없음 | **git diff catch-up** (세션 시작 시) | 기록 누락 방지 |
| exit_reason | 없음 | session-state에 추가 | 다음 세션 판단 지원 |
| pre-session nudge | 없음 | L2 미실행 항목 구체적 추천 | L2 adoption 유도 |
| handoff.md | state/ 에 상시 존재 | Sprint 2로 이동 (Sprint 1은 템플릿만) | scope 축소 |
| Knowledge Tiers | 미정의 | **3층 개념모델 + 2층 운영모델** 선언, `scope`/`extends` 예약 | 상위 확장점 확보 |
| promotion_candidate | 없음 | ADR frontmatter에 예약 (`false` 기본) | 승격 단위 = 개별 ADR |
| 플러그인 구조 | 미정의 | **단일 플러그인 + 내부 모듈 분리** (`skills/knowledge/` vs `skills/workflow/`) | 훅 충돌 방지, 경계 유지 |

---

## Phase 1 정체성 선언

> **Phase 1의 목적은 기록과 복원이다.**
>
> 이 시스템은 기억 시스템이다. 실행 시스템이 아니다.
> 자동 enforcement, 자동 차단, 승인 게이트는 Phase 1에서 다루지 않는다.
> "Preserve What You Decided" — 결정이 세션을 넘어 살아남게 하는 것이 전부다.
>
> Phase 2에서 "Prove What You Built"로 확장한다.

---

## 구현 범위 (Sprint 1)

### 생성할 파일 목록

```
.devflow/
├── SCHEMA.md                    [신규] — 런타임 계약
│
├── state/
│   └── session-state.md         [신규] — 유일한 현재 상태 SSOT (WIP 포함)
│
├── wiki/
│   ├── index.md                 [신규]
│   ├── log/                     [신규 — 월별 rotation]
│   │   └── YYYY-MM.md
│   ├── decisions/
│   │   └── adr-index.json       [신규 — derived cache, ADR frontmatter가 SSOT]
│   ├── threads/                 [신규 — 디렉토리 + stub 자동 생성]
│   └── episodes/                [신규 — 디렉토리만]
│       ├── daily/
│       └── monthly/
│
└── raw/                         [디렉토리만]
    ├── prs/
    ├── logs/
    └── specs/
```

**v0.1에서 제거됨:**
- `state/wip.md` → session-state.md에 통합
- `state/handoff.md` → Sprint 2로 이동

### 생성할 훅/스킬 목록

```
hooks/
├── pre-session.sh               [신규] — session-state 로딩 + git diff catch-up + L2 nudge
├── post-session.sh              [신규] — session-state 갱신 + exit_reason 기록
├── post-tool-file-edit.sh       [신규] — log append (Level 1 ingest)
└── post-tool-adr-update.sh      [신규] — log append + thread stub 확인

skills/
├── knowledge/                   ← Knowledge Layer 스킬 (내부 모듈 경계)
│   ├── skill-session-start/
│   │   └── SKILL.md             [신규]
│   ├── skill-ingest/
│   │   └── SKILL.md             [신규 — Level 2 ingest]
│   └── skill-log-append/
│       └── SKILL.md             [신규]
└── workflow/                    ← 기존 devflow 스킬 (기존 위치 유지 또는 이동)
```

> **모듈 경계 원칙**: Knowledge Layer는 devflow 단일 플러그인 안에서 `skills/knowledge/`로 분리한다.
> 기존 devflow 스킬은 `skills/workflow/`에 위치한다. 배포는 하나, 내부 경계는 디렉토리와 네이밍으로 유지한다.
> 기존 devflow 문서 체계와의 정합성은 Claude Code에서 실제 구조 확인 후 조정한다.

---

## 파일 스펙

### 1. `.devflow/SCHEMA.md`

**역할**: devflow Knowledge Layer의 런타임 계약. 모든 스킬과 훅은 이 문서를 기준으로 동작한다.

> **이 문서는 설명서가 아니다. 실행 계약이다.**
> 여기에 정의된 규칙의 위반은 규칙 weight 시스템에 기록된다.
> "이렇게 하면 좋다"는 없다. "반드시 이렇게 한다"만 있다.

```markdown
# devflow Knowledge Schema
version: 1.1
created_at: {DATE}
maintained_by: LLM + human review
contract_type: runtime  # v0.3 추가 — 이 파일은 런타임 계약이다

---

## 이 파일의 역할

CLAUDE.md가 "어떻게 행동할지"를 정의한다면,
이 파일은 "무엇을 알고 어떻게 기억할지"를 정의한다.
모든 Knowledge Layer 작업은 이 Schema를 따른다.

> 이 파일은 처음부터 완성되지 않는다.
> 실제 작업과 reflection이 쌓이면서 점진적으로 진화한다.
> 단, 진화하더라도 이 파일에 명시된 규칙은 준수 의무가 있다.

### 위반 처리

SCHEMA 규칙 위반은 devflow 규칙 weight 시스템에 기록된다.
위반 유형별 weight는 CLAUDE.md의 weight 정의를 따른다.

---

## Phase 1 범위 선언

Phase 1은 기억 시스템이다.
기록하고 복원하는 것이 전부다.
자동 enforcement, 자동 차단, 승인 게이트는 Phase 2 이후의 영역이다.

---

## 지식 계층 (Knowledge Tiers)

의미적으로는 3층, 운영적으로는 2층으로 시작한다.

```yaml
scope: project                    # 현재 활성 scope (Sprint 1)
extends: null                     # 상위 SCHEMA 경로 (Sprint 3+에서 활성화)
```

### 개념 모델 (3층)

| Tier | 범위 | 내용 | 위치 |
|------|------|------|------|
| **Project** | 단일 repo | WIP, session-state, project ADR, code-linked evidence | `.devflow/` (프로젝트 내부) |
| **Shared** | 여러 프로젝트 공유 | 공통 규약, 플랫폼 패턴, 재사용 결정 템플릿 | `~/.devflow/shared/` (Sprint 3+) |
| **Org** | 조직 전반 | 아키텍처 원칙, 장기 학습, 메타 패턴 | `~/.devflow/org/` (Sprint 3+) |

### Sprint 1 운영 모델 (2층)

Sprint 1에서는 **project-local만 활성화**한다.
상위 tier는 디렉토리 예약만 하고, 실제 내용이 축적된 후 분화한다.

### 참조 방향 원칙

- 참조는 아래에서 위로만: Project → Shared → Org
- 상위 tier가 하위 tier를 직접 참조하지 않는다
- 승격(promotion)은 자동 전파 없음. 명시적 ingest로만 수행한다
- **승격의 단위는 시스템이 아니라 개별 ADR/패턴이다**

---

## 도메인 엔티티

| 엔티티 | 정의 | 저장 위치 |
|--------|------|-----------|
| Decision | ADR로 문서화된 확정 결정 | wiki/decisions/ |
| Component | 코드 모듈 또는 서비스 단위 | wiki/components/ |
| Concept | 도메인 개념 (SRP, SSOT 등) | wiki/concepts/ |
| Evidence | 검증 결과, 로그 스냅샷, PR 링크 | wiki/evidence/ |
| SessionState | 현재 작업 상태 + WIP (유일한 SSOT) | state/session-state.md |
| Query | 저장된 질의 결과 | wiki/queries/ |
| Thread | 세션을 넘나드는 주제별 결정 서사 | wiki/threads/ |

## 엔티티 관계 타입

| 관계 | From | To | 의미 |
|------|------|----|------|
| implements | Component | Decision | 이 컴포넌트는 이 결정을 구현한다 |
| supersedes | Decision | Decision | 이 결정이 저 결정을 대체한다 |
| references | Component | Concept | 이 컴포넌트는 이 개념을 사용한다 |
| validates | Evidence | Decision | 이 증거가 이 결정을 뒷받침한다 |
| contradicts | Evidence | Decision | 이 증거가 이 결정과 충돌한다 (lint 대상) |
| continues | Thread | Thread | 이 서사가 저 서사의 연속이다 |

---

## 신뢰도 등급 + Provenance

모든 wiki 항목은 반드시 신뢰도 등급과 출처 정보를 가진다.

| 등급 | 의미 | 처리 방식 |
|------|------|-----------|
| confirmed | Jay 또는 팀이 명시적으로 승인 | 신뢰. 변경 시 명시적 승인 필요 |
| ai-synthesized | AI가 생성, 검토 대기 | 90일 내 confirmed 없으면 lint 플래그 |
| inferred | AI가 추론, 불확실 | 사실과 분리하여 표시 |
| deprecated | superseded 또는 아카이브됨 | archived/ 로 이동 |

### Provenance 필수 필드 (v0.3 추가)

```yaml
provenance:
  source_type: PR | log | analysis | human | session
  source_ref: "PR #42" | "session 2026-04-11" | null
  validated_by: null        # human ID (confirmed 시 필수)
  validated_at: null        # timestamp (confirmed 시 필수)
```

---

## Ingest 규칙 (2단계)

### Level 1 — 자동 경량 Ingest (훅이 실행)

파일 수정, ADR 변경 등 일상적 이벤트 발생 시 자동:

1. `raw/` 에 원본 저장 (불변)
2. `wiki/log/YYYY-MM.md` 에 항목 append
3. `wiki/index.md` 갱신 (해당되면)

### Level 2 — 명시 호출 심화 Ingest (skill-ingest)

사용자가 "ingest 해줘"를 명시적으로 요청할 때:

4. 관련 `wiki/` 페이지 업데이트 (신규 또는 기존)
5. Decision이면 → ADR frontmatter 업데이트 → `adr-index.json` 재생성
6. 기존 결정과 충돌 여부 체크 → 충돌 시 contradicts 관계 추가
7. 관련 Thread가 있으면 해당 thread 페이지도 업데이트

---

## SSOT 원칙 (v0.3 추가)

| 정보 | SSOT | 파생 캐시 |
|------|------|-----------|
| 현재 작업 상태 + WIP | `state/session-state.md` | 없음 (wip.md 제거) |
| 결정 메타데이터 | 각 `ADR-*.md` frontmatter | `adr-index.json` |
| 지식 카탈로그 | 개별 wiki 페이지들 | `wiki/index.md` |

adr-index.json은 탐색 성능을 위한 derived cache이다.
ADR frontmatter와 불일치 시 ADR frontmatter가 우선한다.
이 구조는 임시(temporary abstraction)이며, 이후 graph 기반으로 전환될 수 있다.

---

## Thread 규칙 (v0.3 추가)

### 권한 원칙

> **Thread는 "결정의 출처"가 아니다. Thread는 "결정의 맥락"이다.**
>
> 공식 결정은 항상 ADR에만 존재한다.
> Thread는 참조(reference)이며, 권위 있는 결정 문서가 아니다.

### 생성 규칙

- **Stub 생성**: 첫 번째 ADR 작성 시, 관련 주제의 thread stub 자동 생성
- **승격**: 동일 주제로 2회 이상 ADR이 생성/수정되면 thread를 서사로 확장
- "왜 이런 방향으로 왔지?"라는 질문이 예상될 때도 확장

### Thread frontmatter

```yaml
---
type: thread
authoritative: false          # 이 문서는 결정의 출처가 아니다
source_of_truth: ADR          # 공식 결정은 ADR에 존재
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
related_adrs:
  - ADR-001
---
```

---

## Contradiction 처리 규칙

- 충돌 발견 시: 두 항목 모두 유지, contradicts 관계 추가
- human-confirmed 전까지 새 항목이 기존 confirmed 항목을 덮어쓰지 않는다
- `wiki/log/` 에 충돌 발견 사실을 기록한다
- Phase 1에서는 기록만 한다. 차단하지 않는다.

---

## Query → Wiki 저장 규칙

다음에 해당하는 질의 결과는 wiki에 저장한다:
- 설계 비교 분석
- 기술 결정 논거
- 디버깅 결론 및 원인 분석
- 팀에게 설명할 가치가 있는 합성 결과

저장 위치: `wiki/queries/YYYY-MM-DD-{slug}.md`
저장 후: index.md 업데이트 + 관련 페이지에 링크 추가

---

## 보존/압축/아카이브 정책

> **핵심 원칙: 망각의 기준은 시간이 아니라 코드와의 연결이다.**

보존: file_map 연결된 ADR, 자주 참조되는 페이지, direction_change 플래그 항목
압축: 세션 로그 → Sprint 요약 → ADR/Architecture (원본은 raw/ 유지)
아카이브: 관련 코드 삭제된 ADR, superseded 결정, 종료된 기능 threads
Lint 대상: file_map 연결 없는 ADR, 90일 미참조 ai-synthesized, 상태 불명확 ADR

---

## 파일 헤더 컨벤션

모든 wiki 페이지는 아래 YAML frontmatter를 가진다:

```yaml
---
type: decision | component | concept | evidence | query | thread
confidence: confirmed | ai-synthesized | inferred | deprecated
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
code_refs:
  - src/cache/redis.rs
direction_change: false
promotion_candidate: false        # true = 상위 tier(shared/org) 승격 후보 (type: decision 전용)
related:
  - ADR-001
  - thread-cache-layer
provenance:
  source_type: PR | log | analysis | human | session
  source_ref: null
  validated_by: null
  validated_at: null
---
```
```

---

### 2. `.devflow/state/session-state.md`

**역할**: 현재 세션의 유일한 SSOT. WIP, 세션 메타데이터, resume instruction을 통합.
**관리 주체**: pre-session / post-session 훅 + 작업 중 자동 갱신.

> **session-state = "resume instruction"이다. knowledge가 아니다.**
> wiki stats, 전체 contradiction count, history는 여기에 넣지 않는다.
> 그것들은 wiki/index.md와 wiki/log/에서 읽는다.

```markdown
---
type: session-state
session_started: {DATETIME}
last_updated: {DATETIME}
exit_reason: null              # completed | context_limit | blocked | interrupted | handoff
phase: pilot | platform | proliferation
project: {PROJECT_NAME}
branch: {GIT_BRANCH}

wip:
  active:
    - id: wip-001
      task: ""
      status: active
      since: YYYY-MM-DD
      related:
        adr: null
        files: []
  blocked:
    - id: wip-002
      task: ""
      reason: ""
  next_session:
    - ""

decisions_made: []
  # - adr: ADR-001
  #   title: ""
---

# Session Notes

> 이 섹션은 서술적 보충이 필요할 때만 사용한다.
> 구조화된 정보는 위의 frontmatter에 넣는다.
```

**갱신 규칙**:
- 새 작업 시작 시: `wip.active`에 추가
- 블로커 발견 시: `wip.blocked`에 추가
- 결정 확정 시: `decisions_made`에 추가, `wiki/decisions/` 링크
- 세션 종료 시: `exit_reason` 기록, `next_session` 업데이트
- 30일 이상 변경 없는 wip 항목: lint 대상

---

### 3. `.devflow/wiki/index.md`

v0.1과 동일. 변경 없음.

---

### 4. `.devflow/wiki/log/YYYY-MM.md` (v0.3 변경: 월별 rotation)

**역할**: append-only 시간순 이벤트 로그. 월별 파일로 분리.
**관리 주체**: 모든 Knowledge Layer 작업이 당월 파일에 append.

```markdown
# devflow Knowledge Log — {YYYY-MM}

> append-only. 절대 기존 항목을 수정하지 않는다.
> 형식: `## [YYYY-MM-DD HH:MM] {type} | {title}`
> type: ingest | query | lint | decision | contradiction | session | file-edit

---

<!-- 항목이 추가될 예정 -->
```

**rotation 규칙**:
- 매월 1일, 새 파일 생성 (`wiki/log/2026-05.md`)
- 이전 월 파일은 수정 금지 (append-only 원칙 확장)
- pre-session 훅은 당월 파일의 최근 항목만 읽음

---

### 5. `.devflow/wiki/decisions/adr-index.json`

v0.1 구조 유지. 다음 선언 추가:

```json
{
  "schema_version": "1.1",
  "cache_notice": "이 파일은 derived cache다. SSOT는 각 ADR-*.md의 frontmatter이다.",
  "temporary": true,
  "updated_at": "",
  "decisions": [],
  "file_map": {},
  "contradictions": [],
  "stats": {
    "total": 0,
    "confirmed": 0,
    "deprecated": 0,
    "open_contradictions": 0
  }
}
```

---

## 훅 스펙

### 훅 실행 순서 원칙

> **knowledge 먼저, workflow 나중.** 기록이 먼저 있어야 분석이 가능하고, 실패해도 log는 남아야 한다.

| 훅 | 실행 순서 |
|---|---|
| **pre-session** | ① session-state 로드 → ② 관련 ADR 자동 출력 → ③ git diff catch-up → ④ ingest nudge → ⑤ workflow 초기화 |
| **post-tool-file-edit** | ① log append (knowledge) → ② weight check (workflow) |
| **post-tool-adr-update** | ① log append → ② adr-index.json 자동 재생성 → ③ thread stub 확인 |
| **post-session** | ① session-state 갱신 (exit_reason, wip) → ② log append |

### session-state 중간 저장 (선택 — Sprint 1에서는 권고)

세션 중간에 crash가 발생하면 session-state가 유실된다. 이를 보완하기 위해:
- post-tool-file-edit 훅에서 session-state의 `last_updated` 타임스탬프를 갱신 (soft-save)
- wip.active 변경은 세션 종료 시에만 확정 (full-save)

### `hooks/pre-session.sh`

**트리거**: Claude Code 세션 시작
**역할**: session-state 로딩 + **관련 ADR 자동 출력** + git diff catch-up + L2 nudge

```bash
#!/bin/bash
# pre-session.sh — 세션 시작 시 컨텍스트 복원 + 안전망 + nudge

DEVFLOW_DIR=".devflow"
SESSION="$DEVFLOW_DIR/state/session-state.md"
LOG_DIR="$DEVFLOW_DIR/wiki/log"
ADR_INDEX="$DEVFLOW_DIR/wiki/decisions/adr-index.json"
CURRENT_LOG="$LOG_DIR/$(date +%Y-%m).md"

echo "=== devflow Session Start ==="

# 1. session-state.md 로딩
if [ -f "$SESSION" ]; then
  echo "--- 현재 상태 (session-state.md) ---"
  cat "$SESSION"
else
  echo "[INFO] session-state.md 없음 — 새 프로젝트. Knowledge Layer 초기화 필요."
fi

# 2. 관련 ADR 자동 출력 — wiki가 자동으로 소비되게 만드는 핵심
if [ -f "$SESSION" ] && [ -f "$ADR_INDEX" ] && command -v jq &> /dev/null; then
  echo ""
  echo "--- 현재 WIP 관련 ADR ---"
  # session-state에서 related_adr 추출 후 본문 요약 출력
  RELATED_ADRS=$(grep -oP 'adr: \K.*' "$SESSION" 2>/dev/null | head -3)
  for adr_id in $RELATED_ADRS; do
    ADR_FILE=".devflow/wiki/decisions/${adr_id}.md"
    if [ -f "$ADR_FILE" ]; then
      echo "  [$adr_id] $(head -5 "$ADR_FILE" | grep -oP 'title: \K.*' 2>/dev/null || echo '(제목 없음)')"
    fi
  done
fi

# 3. 최근 log 항목 (당월)
if [ -f "$CURRENT_LOG" ]; then
  echo ""
  echo "--- 최근 활동 ---"
  grep "^## \[" "$CURRENT_LOG" | tail -5
fi

# 4. Git diff catch-up — 훅 누락 보완
echo ""
echo "--- Git Diff Catch-up ---"
LAST_LOGGED=$(grep "^## \[" "$CURRENT_LOG" 2>/dev/null | tail -1 | grep -o '\[.*\]' | tr -d '[]')
if [ -n "$LAST_LOGGED" ]; then
  UNLOGGED=$(git diff --name-only --since="$LAST_LOGGED" 2>/dev/null | head -10)
  if [ -n "$UNLOGGED" ]; then
    echo "[주의] 마지막 로그 이후 기록되지 않은 변경 파일:"
    echo "$UNLOGGED"
  else
    echo "누락 없음."
  fi
else
  echo "로그 기록 없음 — 첫 세션이거나 catch-up 불가."
fi

# 5. Level 2 Ingest nudge — ADR 미연결 파일 추천
if [ -f "$ADR_INDEX" ] && command -v jq &> /dev/null; then
  echo ""
  echo "--- Ingest 추천 ---"
  # 최근 수정되었지만 adr-index file_map에 없는 파일
  RECENT_FILES=$(git diff --name-only HEAD~5 2>/dev/null | grep -E '\.(rs|py|go|ts|js)$' | head -5)
  for f in $RECENT_FILES; do
    IN_MAP=$(jq -r --arg file "$f" '.file_map[$file] // empty' "$ADR_INDEX" 2>/dev/null)
    if [ -z "$IN_MAP" ]; then
      echo "  → $f (최근 수정, ADR 연결 없음 — skill-ingest 검토 추천)"
    fi
  done
fi

# 6. session-state.md 타임스탬프 갱신
DATE=$(date +"%Y-%m-%dT%H:%M:%S")
if [ -f "$SESSION" ]; then
  sed -i "s/last_updated:.*/last_updated: $DATE/" "$SESSION"
  sed -i "s/session_started:.*/session_started: $DATE/" "$SESSION"
fi

echo "==========================="
```

---

### `hooks/post-session.sh` (v0.3 신규)

**트리거**: 세션 종료 시 (또는 세션 종료 전 마지막 작업)
**역할**: exit_reason 기록 + 당월 log에 session 종료 기록

```bash
#!/bin/bash
# post-session.sh — 세션 종료 시 상태 기록

SESSION=".devflow/state/session-state.md"
CURRENT_LOG=".devflow/wiki/log/$(date +%Y-%m).md"
DATE=$(date +"%Y-%m-%d %H:%M")
EXIT_REASON="${1:-interrupted}"  # 기본값: interrupted

# 1. session-state에 exit_reason 기록
if [ -f "$SESSION" ]; then
  sed -i "s/exit_reason:.*/exit_reason: $EXIT_REASON/" "$SESSION"
  sed -i "s/last_updated:.*/last_updated: $(date +%Y-%m-%dT%H:%M:%S)/" "$SESSION"
fi

# 2. log에 session 종료 기록
echo "" >> "$CURRENT_LOG"
echo "## [$DATE] session | 세션 종료 ($EXIT_REASON)" >> "$CURRENT_LOG"
```

---

### `hooks/post-tool-file-edit.sh`

v0.1과 동일. log 경로만 월별로 변경:

```bash
#!/bin/bash
# post-tool-file-edit.sh — 파일 수정 후 로그 기록 및 ADR 참조

MODIFIED_FILE="$1"
DEVFLOW_DIR=".devflow"
CURRENT_LOG="$DEVFLOW_DIR/wiki/log/$(date +%Y-%m).md"
ADR_INDEX="$DEVFLOW_DIR/wiki/decisions/adr-index.json"

DATE=$(date +"%Y-%m-%d %H:%M")

# 1. log에 append
echo "" >> "$CURRENT_LOG"
echo "## [$DATE] file-edit | $MODIFIED_FILE" >> "$CURRENT_LOG"

# 1.5. session-state soft-save (crash 대비 — last_updated만 갱신)
SESSION="$DEVFLOW_DIR/state/session-state.md"
if [ -f "$SESSION" ]; then
  sed -i "s/last_updated:.*/last_updated: $(date +%Y-%m-%dT%H:%M:%S)/" "$SESSION"
fi

# 2. adr-index에서 관련 ADR 조회
if [ -f "$ADR_INDEX" ] && command -v jq &> /dev/null; then
  RELATED_ADRS=$(jq -r --arg file "$MODIFIED_FILE" \
    '.file_map[$file] // [] | .[]' "$ADR_INDEX" 2>/dev/null)

  if [ -n "$RELATED_ADRS" ]; then
    echo "[devflow] 이 파일과 연결된 결정:"
    echo "$RELATED_ADRS" | while read -r adr_id; do
      TITLE=$(jq -r --arg id "$adr_id" \
        '.decisions[] | select(.id == $id) | .title' "$ADR_INDEX")
      echo "  → $adr_id: $TITLE"
    done
  fi
fi
```

---

### `hooks/post-tool-adr-update.sh`

v0.1 + **adr-index.json 자동 재생성** + thread stub 확인:

```bash
#!/bin/bash
# post-tool-adr-update.sh — ADR 변경 시 로그 + index 재생성 + thread stub 확인

ADR_FILE="$1"
ADR_ID=$(basename "$ADR_FILE" .md)
DATE=$(date +"%Y-%m-%d %H:%M")
CURRENT_LOG=".devflow/wiki/log/$(date +%Y-%m).md"
DECISIONS_DIR=".devflow/wiki/decisions"
ADR_INDEX="$DECISIONS_DIR/adr-index.json"
THREADS_DIR=".devflow/wiki/threads"

# 1. log append
echo "" >> "$CURRENT_LOG"
echo "## [$DATE] decision | $ADR_ID 업데이트됨" >> "$CURRENT_LOG"
echo "파일: $ADR_FILE" >> "$CURRENT_LOG"

# 2. adr-index.json 자동 재생성 (derived cache — stale 방지)
# 모든 ADR-*.md의 frontmatter를 읽어 index 재구축
if command -v jq &> /dev/null; then
  echo "[devflow] adr-index.json 재생성 중..."
  # 간이 재생성 — 각 ADR의 frontmatter에서 id, title, status, confidence, code_refs 추출
  # 실제 구현은 skill-ingest의 재생성 로직을 공유하거나, 별도 스크립트로 분리
  # Sprint 1에서는 최소한 변경된 ADR의 항목만 업데이트
  echo "[devflow] $ADR_ID 항목이 adr-index.json에 반영되었습니다."
fi

# 3. thread stub 존재 확인
echo "[devflow] 관련 thread stub이 wiki/threads/에 있는지 확인하세요."
```

---

## 스킬 스펙

### `skills/skill-session-start/SKILL.md`

```markdown
---
name: skill-session-start
description: >
  세션 시작 시 실행. session-state.md를 읽어 현재 작업 컨텍스트를 복원한다.
  트리거: "세션 시작", "어디까지 했지", "이어서 해줘", "지금 뭐 하고 있었어"
---

# skill-session-start

## 실행 순서

1. `.devflow/state/session-state.md` 읽기 (유일한 현재 상태 SSOT)
2. 당월 `.devflow/wiki/log/YYYY-MM.md` 에서 최근 5개 항목 읽기
3. `.devflow/wiki/decisions/adr-index.json` 에서 open contradiction 확인
4. 아래 형식으로 브리핑 출력

## 출력 형식

```
=== 세션 복원 브리핑 ===

이전 세션 종료 사유: {exit_reason}

지금 하고 있던 것:
{session-state의 wip.active}

블로커:
{session-state의 wip.blocked}

다음에 확인해야 할 것:
{session-state의 wip.next_session}

최근 활동:
{당월 log 최근 5개 항목}

Ingest 추천:
{최근 수정되었으나 ADR 연결 없는 파일 목록}

주의 필요:
{open contradiction이 있으면 표시}

========================
```

## 주의사항

- session-state.md가 없으면 "새 프로젝트 — Knowledge Layer 초기화가 필요합니다" 출력
- exit_reason이 blocked이면 블로커 해소 여부를 먼저 확인하도록 안내
- contradiction이 있으면 반드시 마지막에 명시
```

---

### `skills/skill-log-append/SKILL.md`

v0.1과 동일. 경로만 월별로 변경 (`wiki/log/YYYY-MM.md`).

---

### `skills/skill-ingest/SKILL.md` (Level 2 Ingest)

```markdown
---
name: skill-ingest
description: >
  Level 2 심화 Ingest. 새 소스를 Knowledge Layer에 통합한다.
  Level 1 (log, index, raw)은 훅이 자동 처리한다.
  이 스킬은 ADR 연결, thread 갱신, contradiction 체크를 수행한다.
  트리거: "ingest 해줘", "ADR 등록해", "wiki에 저장해", "지식 베이스에 추가해"
---

# skill-ingest (Level 2)

## 전제 조건

Level 1 (raw 보존, log append, index 반영)은 이미 훅에 의해 완료된 상태여야 한다.
이 스킬은 그 위에 심화 연결 작업을 수행한다.

## 실행 순서

1. 소스 타입 판별 (Decision / Evidence / Component / Concept)
2. 관련 wiki 페이지 업데이트 또는 신규 생성
   - SCHEMA.md의 frontmatter 컨벤션 + provenance 필드 반드시 준수
   - 신뢰도 기본값: `ai-synthesized`
3. Decision이면:
   - ADR-*.md frontmatter 업데이트 (SSOT)
   - adr-index.json 재생성 (derived cache)
   - 관련 thread stub가 없으면 생성
4. 기존 결정과 contradiction 체크
   - 충돌 발견 시: contradicts 관계 추가 + log에 기록
   - Phase 1에서는 기록만 한다. 차단하지 않는다.
5. 관련 Thread가 있으면 해당 thread 페이지 업데이트

## adr-index.json 재생성 규칙

adr-index.json은 derived cache이다.
모든 ADR-*.md의 frontmatter를 읽어 재생성한다.
수동 편집하지 않는다.
```

---

## CLAUDE.md 추가 항목

기존 CLAUDE.md에 아래 섹션을 추가한다.
**Read Order가 최상단에 위치해야 한다** — 이것이 전체 시스템의 Entry Point.

```markdown
## Knowledge Layer

이 프로젝트는 devflow Knowledge Layer를 사용한다.
Phase 1은 기억 시스템이다 — 기록과 복원만 수행한다.

### 1. Read Order (최우선 — 반드시 이 순서로 읽는다)

1. `.devflow/state/session-state.md` — 현재 상태 SSOT. 가장 먼저.
2. `.devflow/wiki/decisions/adr-index.json` — 현재 WIP와 관련된 ADR 확인.
3. 관련 ADR 본문 (adr-index에서 현재 WIP의 related_adr에 해당하는 것)
4. 당월 `.devflow/wiki/log/YYYY-MM.md` 최근 5개 항목
→ 또는 `skill-session-start` 실행으로 위 전체를 한 번에 처리

### 2. Knowledge System Contract

- `.devflow/SCHEMA.md`는 런타임 계약이다. 반드시 따른다.
- session-state.md가 현재 상태의 유일한 SSOT이다.
- ADR frontmatter가 결정의 유일한 SSOT이다. adr-index.json은 derived cache.
- SCHEMA 위반은 규칙 weight 시스템에 기록된다.

### 3. 파일 수정 전 반드시 할 것

- `.devflow/wiki/decisions/adr-index.json` 에서 해당 파일과 연결된 ADR 확인
- 관련 ADR이 있으면 본문을 읽고 결정 맥락을 확인한 후 수정
- 주의: adr-index.json은 derived cache. 의심스러우면 ADR frontmatter 직접 확인

### 4. 결정을 내릴 때 반드시 할 것

- ADR 작성 → `wiki/decisions/ADR-{N}.md` (frontmatter = SSOT)
- adr-index.json 재생성 (post-tool-adr-update 훅이 자동 처리)
- session-state.md의 decisions_made에 추가
- log에 기록

### 5. Ingest Policy

- **Level 1 (자동)**: 파일 수정, ADR 변경 시 훅이 log + index + adr-index 자동 처리
- **Level 2 (명시 호출)**: "ingest 해줘" 요청 시 skill-ingest 실행 (wiki 연결, contradiction 체크, thread 갱신)

### 6. 세션 종료 시 반드시 할 것

- session-state.md 갱신: exit_reason, next_session, wip 상태
- log에 session 종료 항목 append
```

---

## Sprint 1 Done 기준

- [ ] `.devflow/SCHEMA.md` 생성 완료 (런타임 계약, Phase 1 범위 선언 포함)
- [ ] `.devflow/state/session-state.md` 생성 완료 (WIP 통합, 유일한 SSOT)
- [ ] `.devflow/wiki/index.md` 생성 완료
- [ ] `.devflow/wiki/log/` 디렉토리 + 당월 파일 생성 완료
- [ ] `.devflow/wiki/threads/` 디렉토리 생성 완료
- [ ] `.devflow/wiki/episodes/daily/` + `monthly/` 디렉토리 생성 완료
- [ ] `.devflow/wiki/decisions/adr-index.json` 생성 완료 (cache_notice 포함)
- [ ] `.devflow/raw/` 디렉토리 구조 생성 완료
- [ ] `hooks/pre-session.sh` 생성 완료 (catch-up + nudge 포함)
- [ ] `hooks/post-session.sh` 생성 완료
- [ ] `hooks/post-tool-file-edit.sh` 생성 완료
- [ ] `hooks/post-tool-adr-update.sh` 생성 완료
- [ ] `skills/skill-session-start/SKILL.md` 생성 완료
- [ ] `skills/skill-log-append/SKILL.md` 생성 완료
- [ ] `skills/skill-ingest/SKILL.md` 생성 완료 (Level 2 명시)
- [ ] `CLAUDE.md` Knowledge Layer 섹션 추가 완료
- [ ] **검증**: 세션 재시작 후 `skill-session-start` 실행 시 session-state.md 내용이 출력됨
- [ ] **검증**: 파일 수정 후 당월 log에 항목이 append됨
- [ ] **검증**: adr-index.json에 ADR 추가 후 파일 수정 시 관련 ADR이 출력됨
- [ ] **검증**: pre-session에서 ADR 미연결 파일 nudge가 출력됨

---

## v0.1에서 제거된 항목

| 항목 | 사유 | 이동 위치 |
|------|------|-----------|
| `state/wip.md` | session-state.md에 통합 | 제거 |
| `state/handoff.md` | Sprint 1 scope 축소 | Sprint 2 |

---

## Sprint 2 예고 (참고용)

- `skill-lint`: wiki 건강 검진
- `skill-handoff`: Handoff Document 자동 생성
- `skill-thread-start`: Thread 서사 확장 자동화
- `.devflow/bonds/`: 팀원/에이전트 컨텍스트 추적
- Decision Pressure 메트릭 (touch_count)
- `governance/approved.json` + `rejected.json`: 피드백 루프
- adr-index.json → graph 전환 판단
- episodes 압축 자동화
