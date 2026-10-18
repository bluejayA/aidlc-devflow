# aidlc-devflow 진화 방향 — 전체 컨텍스트 기록 v2.1
> 최초 작성: 2026-04-11  
> 최종 갱신: 2026-04-11 (Knowledge Tier + 플러그인 구조 합의 완료)  
> 목적: Claude Code에서 구현을 시작할 때 전체 맥락을 복원하기 위한 영속 기록

---

## 1. 출발점 (변경 없음)

원칙의 생존 조건이 핵심 주제. 세 단계 통찰:
1. 원칙 선언만으로는 지켜지지 않는다
2. AI + 반복 주입으로 코드 구조는 좋아졌다
3. **증거 영속화**가 추가되었을 때 원칙이 "운영 기준"이 됐다

핵심 문장:
> "검증했다는 사실보다, 그 검증 결과가 다음 세션과 다음 사람에게도 남아 있어야 한다"

---

## 2. Debate를 통해 확정된 설계 원칙

### 2.1 Phase 1 정체성

> **Phase 1은 기억 시스템이다. 실행 시스템이 아니다.**
> 기록하고 복원하는 것이 전부. 자동 enforcement, 차단, 승인 게이트는 Phase 2.

슬로건: "Preserve What You Decided" → Phase 2: "Prove What You Built"

### 2.2 SSOT 원칙 (Debate 최대 합의 사항)

| 정보 | SSOT | 파생 캐시 |
|------|------|-----------|
| 현재 작업 상태 + WIP | `state/session-state.md` | 없음 (wip.md 제거) |
| 결정 메타데이터 | 각 `ADR-*.md` frontmatter | `adr-index.json` |
| 지식 카탈로그 | 개별 wiki 페이지들 | `wiki/index.md` |

- wip.md 제거 → session-state.md에 구조화된 YAML로 통합
- session-state = "resume instruction"이다. knowledge가 아니다. wiki stats/history 넣지 않는다.
- adr-index.json은 명시적 derived cache이자 temporary abstraction

### 2.3 SCHEMA.md = 런타임 계약

- 설명 문서가 아니라 실행 계약
- 위반은 기존 규칙 weight 시스템에 기록
- "이렇게 하면 좋다"는 없다. "반드시 이렇게 한다"만 있다.

### 2.4 Ingest 2단계 분리

- **Level 1 (자동)**: raw 보존 + log append + index 반영 — 훅이 처리
- **Level 2 (명시 호출)**: ADR 연결 + thread 갱신 + contradiction 체크 — skill-ingest

L2 adoption을 위해 pre-session에서 **구체적 추천 nudge** (파일명까지 표시)

### 2.5 Thread 비권위 원칙

> Thread는 "결정의 출처"가 아니다. Thread는 "결정의 맥락"이다.
> 공식 결정은 항상 ADR에만 존재한다.

- ADR 1회 시 thread stub 자동 생성
- ADR 2회 이상 시 thread 승격 (서사 확장)

### 2.6 보존/망각 원칙

> **소프트웨어 프로젝트에서 망각의 기준은 시간이 아니라 코드와의 연결이다.**

gyeol의 시간 기반 tiering이 아닌, 코드 연결 기반 보존/압축/아카이브.

### 2.7 Provenance 확장

기존 4등급 상태(confirmed/ai-synthesized/inferred/deprecated)에 추가:
```yaml
provenance:
  source_type: PR | log | analysis | human | session
  source_ref: "PR #42"
  validated_by: null
  validated_at: null
```

---

## 3. Knowledge Tiers (지식 계층)

### 합의: 의미적으로 3층, 운영적으로 2층

| Tier | 범위 | 내용 | Sprint 1 상태 |
|------|------|------|---------------|
| **Project** | 단일 repo | WIP, session-state, project ADR, code-linked evidence | **활성** |
| **Shared** | 여러 프로젝트 | 공통 규약, 플랫폼 패턴, 재사용 템플릿 | 예약만 |
| **Org** | 조직 전반 | 아키텍처 원칙, 장기 학습, 메타 패턴 | 예약만 |

### 참조 방향

- 아래에서 위로만: Project → Shared → Org
- 상위가 하위를 직접 참조하지 않는다
- 승격은 자동 전파 없음. 명시적 ingest로만
- **승격 단위는 시스템이 아니라 개별 ADR** (`promotion_candidate` 필드)

### 운영 모델

- Sprint 1: project-local만
- Sprint 3+: `~/.devflow/` 내부에 `shared/`와 `org/` 디렉토리 분리
- 실제 내용이 축적되면 별도 repo로 분화 (마이크로서비스 분리와 같은 판단)

---

## 4. 플러그인 구조: 단일 플러그인 + 내부 모듈 분리

### 합의

- **별도 플러그인(devflow-knowledge)으로 분리하지 않는다**
- 이유: 훅 충돌, CLAUDE.md 이중화, 사용자에게 불필요한 복잡성
- **내부에서 `skills/workflow/` vs `skills/knowledge/`로 디렉토리 경계**

### 아키텍처 원칙: Single Plugin, Dual Subsystem

> 분리해야 하는 것은 플러그인이 아니라 책임이다.

- **배포 단위**: devflow 하나
- **내부 서브시스템**: workflow / knowledge
- **통합 진입점**: CLAUDE.md 하나 (내부에 workflow rules / knowledge schema 섹션 분리)
- **통합 훅**: 하나의 훅 체인 안에서 순서 명시 (knowledge 복원 → workflow 초기화)
- **느슨한 결합**: knowledge 스킬은 knowledge 디렉토리에만, knowledge 훅 로직은 별도 함수로 분리. workflow는 knowledge를 "호출"하는 방식으로 연결. 향후 독립 플러그인으로 분리 가능한 구조 유지.

### .devflow/ 경계 원칙

> **.devflow/는 knowledge substrate 전용이다. workflow 실행 상태를 여기에 넣지 않는다.**

- `.devflow/state/` — knowledge의 session-state, resume instruction
- `.devflow/wiki/` — knowledge의 결정, 개념, 증거, 로그
- `.devflow/raw/` — knowledge의 불변 원천 자료
- `.devflow/SCHEMA.md` — knowledge 전용 런타임 계약

workflow 실행 상태(규칙 weight 누적, 스킬 실행 이력 등)는 `.devflow/` 밖, devflow 플러그인 자체의 영역에 둔다.
이 경계가 흐려지면 "이건 workflow 상태인가 knowledge 상태인가?" 혼란이 재발한다.

### 구조

```
devflow/                              ← 단일 플러그인
├── CLAUDE.md                         ← 통합 (workflow + knowledge 섹션)
├── hooks/
│   ├── pre-session.sh                ← knowledge 복원 + workflow 초기화
│   ├── post-session.sh               ← knowledge 기록
│   ├── post-tool-file-edit.sh        ← weight 체크 + log append
│   └── post-tool-adr-update.sh       ← log + thread stub
├── skills/
│   ├── workflow/                     ← 기존 devflow 스킬
│   └── knowledge/                    ← Knowledge Layer 스킬
│       ├── skill-session-start/
│       ├── skill-ingest/
│       └── skill-log-append/
└── .devflow/                         ← 프로젝트 데이터 (knowledge)
    ├── SCHEMA.md
    ├── state/session-state.md
    ├── wiki/
    └── raw/
```

### 미결: 기존 devflow 문서 체계 정합성

Claude Code에서 기존 devflow 플러그인의 실제 디렉토리 구조를 확인한 후,
Knowledge Layer 파일들의 위치와 기존 파일들의 충돌 여부를 조정해야 한다.

---

## 5. 추가 합의 사항 (Debate에서 도출)

### log.md 월별 rotation
- `wiki/log/YYYY-MM.md` 형태
- 이전 월 파일 수정 금지
- pre-session은 당월만 읽음

### git diff catch-up (세션 시작 시)
- 마지막 로그 이후 기록되지 않은 변경 파일 감지
- 기억 시스템에서 가장 치명적 실패 = "기록이 안 된 채 지나가는 것"

### exit_reason
- session-state.md에 포함
- completed | context_limit | blocked | interrupted | handoff
- 다음 세션이 "이어서 하면 되는가 vs 방향 재검토가 필요한가" 판단 지원

### session-state 비대화 방지
- session-state = resume instruction만
- wiki stats, contradiction count, history는 넣지 않는다
- 이것들은 wiki/index.md와 wiki/log/에서 읽는다

### 훅 실행 순서 (확정)
- **원칙: knowledge 먼저, workflow 나중** — 기록이 먼저 있어야 분석 가능, 실패해도 log는 남아야 함
- pre-session: session-state 로드 → 관련 ADR 자동 출력 → catch-up → nudge → workflow 초기화
- post-tool-file-edit: log append → soft-save → weight check
- post-tool-adr-update: log append → adr-index 자동 재생성 → thread stub 확인
- post-session: session-state 갱신 → log append

### CLAUDE.md Entry 구조 (확정)
- Read Order가 최상단 — 이것이 전체 시스템의 Entry Point
- 순서: session-state → adr-index → 관련 ADR 본문 → 당월 log
- Knowledge System Contract, Ingest Policy 섹션 명시

### adr-index.json 자동 재생성 (확정)
- post-tool-adr-update 훅에서 자동 재생성 (stale cache 방지)
- Level 2 ingest에서의 재생성과 별도로, ADR 변경 시 즉시 반영

### session-state 중간 저장 (권고)
- post-tool-file-edit에서 `last_updated` 타임스탬프만 갱신 (soft-save)
- wip 구조 변경은 세션 종료 시에만 확정 (full-save)
- 세션 중 crash 시 상태 유실 최소화

### wiki 자동 소비 경로 (확정)
- pre-session에서 현재 WIP의 관련 ADR 1~3개를 자동 출력
- 저장만 되고 아무도 안 읽는 wiki 문제 해결
- ingestion보다 consumption이 더 중요

---

## 6. 구현 로드맵 (갱신)

### Phase 1: Knowledge Layer

**Sprint 1 — Session Continuity + Schema 기반**  
스펙: `SPEC-knowledge-layer-sprint1-v0.3.md` ← **현재 최신**

**Sprint 2 — ADR Graph + Wiki Ingest + Handoff**
- skill-lint
- skill-handoff 자동 생성
- skill-thread-start (서사 확장 자동화)
- adr-index.json 자동 재생성
- wiki/queries/ 저장 자동화
- bonds/ (팀원/에이전트 컨텍스트)

**Sprint 3 — Lint + Governance + Tier 확장**
- 30일 WIP 만료 감지
- contradiction 자동 감지
- approved/rejected 피드백 루프
- health score
- Knowledge Tier: shared/org 활성화
- promotion_candidate → 승격 워크플로

### Phase 2: Done 판정
- 테스트 + 배포 + 관찰 3종 세트
- "Prove What You Built"

---

## 7. 다음 단계 (Claude Code에서 할 것)

### 7.1 기존 devflow 플러그인 구조 확인 (최우선)

Knowledge Layer 구현 전에 반드시 기존 devflow의 실제 파일 체계를 파악해야 한다.
기존 구조를 모르고 Knowledge Layer를 얹으면 중복, 충돌, 컨벤션 불일치가 발생한다.

**확인해야 할 것:**

1. **디렉토리 구조 전체**: devflow 플러그인 루트에서 `find . -type f` 수준으로 파악
2. **기존 CLAUDE.md 내용**: Knowledge Layer 섹션을 추가할 때 기존 섹션과 충돌하지 않는지
3. **기존 훅 목록**: pre-session, post-tool 등 이미 등록된 훅이 있는지. 있다면 Knowledge Layer 훅을 별도로 추가할지, 기존 훅에 통합할지 결정 필요
4. **기존 스킬 디렉토리 구조**: `skills/` 아래에 이미 어떤 스킬들이 있는지. `skills/workflow/`와 `skills/knowledge/` 분리가 기존 구조와 호환되는지. 기존 스킬들을 `skills/workflow/`로 이동해야 하는지, 아니면 현재 위치를 유지하고 knowledge만 하위 디렉토리로 넣을지
5. **기존 ADR 관련 구조**: ADR 스킬이 이미 있다면, 그 스킬이 생성하는 ADR 파일의 위치와 frontmatter 형식이 Knowledge Layer의 `wiki/decisions/ADR-*.md`와 어떻게 다른지
6. **기존 규칙 weight 시스템 파일**: SCHEMA.md 위반을 weight에 연결하려면, 현재 weight가 어떤 파일에 어떤 형식으로 저장되는지 확인 필요
7. **기존 `.devflow/` 디렉토리 유무**: 이미 `.devflow/`라는 이름을 쓰고 있는지, 다른 이름인지
8. **Progressive Disclosure 패턴**: 기존 SKILL.md들이 Progressive Disclosure를 어떤 구조로 쓰고 있는지. Knowledge Layer 스킬도 동일 패턴을 따라야 함
9. **3-tier skill policy**: 기존 devflow의 스킬 정책(Tier 1/2/3)에서 Knowledge Layer 스킬은 어느 tier에 배치되는지

**판단해야 할 것:**

- `.devflow/` 디렉토리가 기존에 없다면: SPEC v0.3 그대로 생성
- `.devflow/` 또는 유사 디렉토리가 이미 있다면: 기존 내용과 병합 방안 결정
- 기존 ADR 스킬이 있다면: Knowledge Layer의 skill-ingest와 책임 분담 정의
- 기존 훅이 있다면: 단일 훅 안에서 workflow + knowledge 로직을 순서대로 호출하는 구조로 통합 (별도 훅 파일 추가가 아닌 기존 훅 확장이 더 나을 수 있음)
- 기존 스킬이 flat 구조(`skills/skill-xxx/`)라면: `skills/knowledge/`를 추가하되 기존 스킬 위치는 건드리지 않는 것이 안전. `skills/workflow/` 이동은 기존 참조 깨질 위험

### 7.2 Knowledge Layer 파일 위치 조정

7.1 확인 결과에 따라 SPEC v0.3의 파일 경로를 조정한다.
특히 다음 항목은 기존 구조에 맞춰 변경될 가능성이 높다:

- `hooks/` 경로 (기존 훅 디렉토리와 통합)
- `skills/knowledge/` 경로 (기존 스킬 디렉토리 컨벤션에 맞춤)
- `.devflow/` 루트 경로 (기존 프로젝트 데이터 디렉토리와 통합)
- CLAUDE.md 내 Knowledge Layer 섹션 위치 (기존 섹션 구조에 맞춤)

### 7.3 Sprint 1 구현 시작

SPEC v0.3 기준. 7.1과 7.2에서 조정된 경로를 반영하여 구현.

---

## 8. 참고 자료 (변경 없음)

| 자료 | 핵심 |
|------|------|
| Karpathy llm-wiki | Raw/Wiki/Schema 3레이어, Ingest/Query/Lint |
| safishamsi/graphify | 코드-문서-ADR 그래프화 |
| inureyes/gyeol | AI 정체성 = 기억, threads, 압축 원칙, 망각 철학 |
| AI-Context-OS | L0/L1/L2 Progressive Memory, SQLite governance |
| glaucobrito/unified-memory | wip.md 패턴, 피드백 루프 |
