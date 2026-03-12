# New INCEPTION Skills Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** INCEPTION 단계에 user-stories, nfr-requirements 스킬을 추가하고 application-design에 NFR Design 섹션을 확장하여, 비개발자가 상용 운영급 소프트웨어를 만들 수 있도록 한다.

**Complexity:** Standard

**Architecture:** 기존 B안(Orchestrator-Centric) 아키텍처를 유지하면서, requirements-analysis와 workflow-planning 사이에 Pre-Planning 스테이지 그룹(user-stories, nfr-requirements)을 삽입한다. 새 스킬은 기존 패턴(stop-no-gate, orchestrator-only)을 따르며, 공유 프로토콜(import-review-protocol)로 GENERATE/IMPORT 모드와 Hold/Skip을 지원한다.

**Tech Stack:** Markdown (SKILL.md 프롬프트 파일), YAML frontmatter

**Spec:** `docs/plans/2026-03-12-new-inception-skills-design.md`

---

## File Structure

| 파일 | 변경 유형 | 책임 |
|------|----------|------|
| `skills/_shared/import-review-protocol.md` | CREATE | GENERATE/IMPORT 모드 + Hold/Skip 공유 프로토콜 |
| `skills/_shared/gate-patterns.md` | MODIFY | Hold 게이트 변형 + 모드 선택 게이트 패턴 추가 |
| `skills/_shared/devflow-conventions.md` | MODIFY | import-review-protocol 참조 + Hold/Skip 규약 |
| `skills/aidlc-user-stories/SKILL.md` | CREATE | 요구사항 → INVEST 사용자 스토리 변환 |
| `skills/aidlc-nfr-requirements/SKILL.md` | CREATE | 도메인 컨텍스트 + 프로파일 기반 NFR 수집 |
| `skills/aidlc-application-design/SKILL.md` | MODIFY | Comprehensive DETAIL에 NFR Design Patterns 섹션 |
| `skills/aidlc-inception-orchestrator/SKILL.md` | MODIFY | Pre-Planning Gate + 모드 선택 + hold/skip |
| `skills/aidlc-workflow-planning/SKILL.md` | MODIFY | Approved Stages에 PRE-PLANNING 섹션 |
| `.claude-plugin/plugin.json` | MODIFY | v0.5.0 → v0.6.0 |

---

## Chunk 1: Shared Infrastructure

### Task 1: Create `_shared/import-review-protocol.md`

**Files:**
- Create: `skills/_shared/import-review-protocol.md`

**Context:** 이 파일은 user-stories와 nfr-requirements 스킬이 참조하는 공유 프로토콜이다. 기존 `_shared/` 파일들(`devflow-conventions.md`, `gate-patterns.md`, `tdd-protocol.md`)과 동일한 수준의 참조 문서로, frontmatter 없이 순수 마크다운으로 작성한다.

- [ ] **Step 1: Create the protocol file**

Create `skills/_shared/import-review-protocol.md`:

```markdown
# Import-Review Protocol

<!-- GENERATE/IMPORT 모드 + Hold/Skip 공유 프로토콜 -->
<!-- 참조하는 스킬: aidlc-user-stories, aidlc-nfr-requirements -->

## 두 가지 모드

| 모드 | 주체 | 흐름 |
|------|------|------|
| **GENERATE** | Claude | 질문 → 수집 → 생성 → 리뷰 |
| **IMPORT** | 사용자 | 파일 수신 → 검증 → 피드백 → 확정 |

모드는 오케스트레이터가 호출 시 인라인 신호로 전달: `"Mode: GENERATE"` 또는 `"Mode: IMPORT"`

## IMPORT Mode 프로세스

```
1. 파일 수신: 사용자가 경로 전달 또는 내용 붙여넣기
2. 형식 검증: 필수 섹션 존재 여부 확인
3. 내용 검토: 누락/모순/모호한 항목 식별
4. 피드백 제시:
   - ✅ 충분한 항목
   - ⚠️ 보완 권장 항목 (이유 포함)
   - ❌ 누락/모순 항목 (이유 포함)
5. 사용자 확정: 피드백 반영 여부는 사용자 결정
```

## Hold/Skip Signal

Pre-Planning 스테이지(user-stories, nfr-requirements)에서 실행 중 중단하거나 건너뛸 수 있다.
오케스트레이터가 H(Hold) 또는 S(Skip) 선택을 감지하면 아래 형식으로 산출물을 저장한다.

### Hold

진행 중인 작업을 중단하고 나중에 재개.

```markdown
## Status: HELD
**Held at**: [중단 시점]
**Reason**: [사용자 제공 이유]
**Completed sections**: [완료된 부분]
**Remaining**: [남은 부분]
```

### Skip

이 스테이지를 완전히 건너뜀.

```markdown
## Status: SKIPPED
**Reason**: [사용자 제공 이유]
```

오케스트레이터는 HELD/SKIPPED 상태를 devflow-state에 기록하고 다음 스테이지로 진행한다.
```

- [ ] **Step 2: Verify file exists and content is correct**

Run: `cat skills/_shared/import-review-protocol.md | head -5`
Expected: `# Import-Review Protocol` on first line

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/import-review-protocol.md
git commit -m "feat: add import-review protocol shared document"
```

---

### Task 2: Update `_shared/gate-patterns.md` — Hold 게이트 + 모드 선택 게이트

**Files:**
- Modify: `skills/_shared/gate-patterns.md:36` (파일 끝에 추가)

**Context:** 기존 gate-patterns.md에 3가지 패턴(표준, 조건부, 리뷰 연계)이 있다. Pre-Planning 스테이지에서 사용하는 2가지 새 변형을 추가한다.

- [ ] **Step 1: Append new gate patterns**

`skills/_shared/gate-patterns.md` 끝에 추가:

```markdown

## 표준 게이트 + Hold 변형 (Standard Gate + Hold)

표준 게이트에 보류(Hold) 옵션을 추가한 변형. Pre-Planning 스테이지에서 사용.

```
[스킬 결과 요약 표시]
A) 변경 요청 → 스킬 재호출
B) 승인, 다음 단계 진행 → 다음 스테이지
H) 보류 (나중에 돌아옴) → HELD 상태 저장, 다음 스테이지로 진행
```

H 선택 시: 산출물에 `## Status: HELD` 기록, devflow-state에 상태 반영.

## 모드 선택 게이트 (Mode Selection Gate)

스킬 호출 전에 실행 모드를 선택하는 게이트. 스킬의 동작을 결정한 후 인라인 신호로 전달.

```
[모드 설명]
A) [모드 A] → 스킬 호출 시 "Mode: [A]" 인라인 신호
B) [모드 B] → 스킬 호출 시 "Mode: [B]" 인라인 신호
S) 이 단계 건너뛰기 → SKIPPED 상태 저장, 다음 스테이지로 진행
```
```

- [ ] **Step 2: Verify updated content**

Run: `grep "Mode Selection" skills/_shared/gate-patterns.md`
Expected: `## 모드 선택 게이트 (Mode Selection Gate)`

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/gate-patterns.md
git commit -m "feat: add Hold gate variant and Mode Selection gate pattern"
```

---

### Task 3: Update `_shared/devflow-conventions.md` — import-review-protocol 참조

**Files:**
- Modify: `skills/_shared/devflow-conventions.md:81` (TDD 규약 섹션 뒤에 추가)

**Context:** 기존 conventions에 TDD 규약, 게이트 패턴 규약 등의 참조가 있다. 동일한 패턴으로 import-review-protocol 참조를 추가하고, version을 v0.3.0으로 올린다.

- [ ] **Step 1: Add import-review protocol reference and bump version**

`skills/_shared/devflow-conventions.md`에서:

1. frontmatter `version: 0.2.0` → `version: 0.3.0`
2. TDD 규약 섹션(`## TDD 규약`, line 76-81) 뒤에 추가:

```markdown

## Import-Review 규약

- `_shared/import-review-protocol.md` — GENERATE/IMPORT 모드 전환, Hold/Skip 상태 관리
- Pre-Planning 스테이지(user-stories, nfr-requirements)에서 참조
- 모드 선택은 오케스트레이터가 게이트로 처리 (스킬 내부에서 모드 선택 금지 — B안 규칙)
```

- [ ] **Step 2: Verify version bump**

Run: `grep "version:" skills/_shared/devflow-conventions.md`
Expected: `  version: 0.3.0`

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "feat: add import-review protocol reference to conventions (v0.3.0)"
```

---

## Chunk 2: New Skills

### Task 4: Create `aidlc-user-stories/SKILL.md`

**Files:**
- Create: `skills/aidlc-user-stories/SKILL.md`

**Context:** 기존 스킬(`aidlc-requirements-analysis/SKILL.md`)의 구조를 따른다: frontmatter → Purpose → Execute (Steps) → Review → Return to Orchestrator → Common Issues. 비대화형 생성 스킬이다.

- [ ] **Step 1: Create skill directory and file**

```bash
mkdir -p skills/aidlc-user-stories
```

Create `skills/aidlc-user-stories/SKILL.md`:

```markdown
---
name: aidlc-user-stories
description: 요구사항을 INVEST 기준 사용자 스토리로 변환. Pre-Planning 스테이지. Called by aidlc-inception-orchestrator.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/user-stories.md
---

# aidlc-user-stories

<!-- 사용자 스토리 생성: 요구사항을 INVEST 기준 스토리로 변환 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->
<!-- Hold/Skip: _shared/import-review-protocol.md 참조 -->

## Purpose

요구사항을 INVEST 기준 사용자 스토리로 변환한다.
비대화형 생성 — requirements.md를 기반으로 일괄 변환하고, 변경 요청은 오케스트레이터 게이트에서 처리.

## Execute

### Step 1: Load context

Read (if they exist):
- `devflow-docs/inception/requirements.md` — 기능/비기능 요구사항
- `devflow-docs/inception/workspace.md` — 그린필드/브라운필드 컨텍스트

### Step 2: Identify actors

요구사항에서 사용자 유형을 추출한다:
- 직접 언급된 사용자 (예: "관리자", "일반 사용자")
- 암묵적 사용자 (예: 인증 요구사항 → 인증된 사용자)
- 외부 시스템 (예: API 연동 → 외부 API)

### Step 3: Generate user stories

각 액터별로:
1. Given-When-Then 형식 Acceptance Criteria 작성
2. INVEST 기준 검증:
   - **I**ndependent: 다른 스토리와 독립적
   - **N**egotiable: 구현 방식 협상 가능
   - **V**aluable: 사용자에게 가치 제공
   - **E**stimable: 구현 범위 추정 가능
   - **S**mall: 한 스프린트 내 완료 가능
   - **T**estable: 검증 기준 명확
3. 우선순위 부여: Must / Should / Could

### Step 4: Save artifact

Create `devflow-docs/inception/user-stories.md`:

```markdown
# User Stories

**Timestamp**: [ISO 8601]
**Source**: devflow-docs/inception/requirements.md

## Actors
- [Actor1]: [역할 설명]
- [Actor2]: [역할 설명]

## Stories

### US-001: [스토리 제목]
**Actor**: [Actor명]
**Story**: As a [actor], I want [goal] so that [benefit]
**Acceptance Criteria**:
- Given [context], When [action], Then [result]
- Given [context], When [action], Then [result]
**Priority**: [Must | Should | Could]
```

## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/user-stories.md`
   - 상위 산출물: `devflow-docs/inception/requirements.md`
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

**depth 확인**: `devflow-docs/devflow-state.md`의 `## Complexity` 필드를 읽는다.

## Return to Orchestrator

STOP.

```
[user-stories 결과]
- 액터: [count]명 ([액터명 나열])
- 사용자 스토리: [count]개 (Must: [N], Should: [N], Could: [N])
- 산출물: devflow-docs/inception/user-stories.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

## Common Issues

### requirements.md에 사용자 유형이 명시되지 않은 경우
- 기능 요구사항에서 암묵적 액터 추출
- "기본 사용자" 액터를 생성하여 매핑
- 산출물에 "⚠️ 명시적 액터 없음 — 요구사항에서 추론" 기록

### 요구사항이 기술 중심이고 사용자 스토리로 변환이 어려운 경우
- 기술 요구사항은 "시스템" 액터로 매핑 (예: As a system, I want...)
- 순수 인프라 요구사항은 스토리 변환 스킵하고 "기술 요구사항" 섹션에 별도 기록
```

- [ ] **Step 2: Verify file structure**

Run: `head -3 skills/aidlc-user-stories/SKILL.md`
Expected: `---` (frontmatter start)

- [ ] **Step 3: Commit**

```bash
git add skills/aidlc-user-stories/
git commit -m "feat: add aidlc-user-stories skill (Pre-Planning stage)"
```

---

### Task 5: Create `aidlc-nfr-requirements/SKILL.md`

**Files:**
- Create: `skills/aidlc-nfr-requirements/SKILL.md`

**Context:** GENERATE/IMPORT 두 모드를 지원하는 대화형 스킬. 도메인 컨텍스트 → 프로파일 선택 → 맞춤 질문 → 기본값 제시 흐름. `_shared/import-review-protocol.md`를 참조한다.

- [ ] **Step 1: Create skill directory and file**

```bash
mkdir -p skills/aidlc-nfr-requirements
```

Create `skills/aidlc-nfr-requirements/SKILL.md`:

```markdown
---
name: aidlc-nfr-requirements
description: 도메인 컨텍스트 + 프로파일 기반 비기능 요구사항(NFR) 수집. GENERATE/IMPORT 모드 지원. Pre-Planning 스테이지. Called by aidlc-inception-orchestrator.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/nfr-requirements.md
---

# aidlc-nfr-requirements

<!-- 비기능 요구사항 수집: 도메인 + 프로파일 기반 체계적 NFR 수집 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->
<!-- IMPORT 모드: _shared/import-review-protocol.md 참조 -->

## Purpose

비개발자가 "이 소프트웨어에 어떤 품질 요구사항이 필요한가"를 체계적으로 수집한다.
NFR 값을 **결정**하는 것이 아니라 **수집**하는 것.

## Execution Modes

### GENERATE Mode (기본)
호출 텍스트에 `Mode: GENERATE` 또는 모드 지정이 없으면 GENERATE.
Step 1부터 순서대로 실행.

### IMPORT Mode
호출 텍스트에 `Mode: IMPORT` 포함 시 활성화.
`_shared/import-review-protocol.md`의 IMPORT 프로세스를 따른다.

IMPORT 모드 검증 항목:
- 8개 NFR 카테고리 중 누락 여부
- 수치 없는 정성적 표현 ("빨라야 한다" → 구체적 수치 요청)
- 카테고리 간 모순 (예: "최저 비용" + "99.99% 가용성")

검증 후 `devflow-docs/inception/nfr-requirements.md`에 저장하고 Return to Orchestrator.

## Execute (GENERATE Mode)

### Step 1: Load context

Read (if they exist):
- `devflow-docs/inception/requirements.md` — 기능/비기능 요구사항
- `devflow-docs/inception/user-stories.md` — 사용자 스토리 (있으면)

### Step 2: Domain context 질문

```
이 소프트웨어의 도메인은?

A) 금융/핀테크 — 높은 보안+컴플라이언스, 감사 추적 필수
B) 헬스케어 — 데이터 프라이버시(HIPAA 등), 높은 가용성
C) 이커머스 — 트래픽 변동 대응, 결제 보안
D) 사내 도구 — 낮은 가용성 허용, 보안 내부망 기준
E) IoT/임베디드 — 저전력, 네트워크 불안정 고려
F) 기타 (직접 입력)
```

선택된 도메인을 Step 4의 기본값 조정에 사용한다.

### Step 3: Profile 선택

```
이 소프트웨어의 운영 환경은?

A) MVP/프로토타입 — 기본값으로 충분, NFR 최소화
B) 소규모 운영 — 사용자 100명 이하, 기본 안정성
C) 중규모 운영 — 사용자 1000명+, 모니터링 필요
D) 대규모/엔터프라이즈 — 고가용성, 보안 컴플라이언스
```

### Step 4: Profile 기반 맞춤 질문

도메인 × 프로파일 조합에 따라 질문 범위를 결정:

| 프로파일 | 질문 수 | 대상 카테고리 |
|---------|--------|--------------|
| MVP | 2~3개 | 핵심 보안, 데이터 백업 |
| 소규모 | 4~5개 | + 응답 시간, 동시 접속 |
| 중규모 | 6~7개 | + 모니터링, 장애 복구 |
| 대규모 | 8개 전체 | 전체 카테고리 순회 |

**8개 NFR 카테고리:**
1. 성능 (응답 시간, 처리량)
2. 가용성 (업타임, 장애 허용)
3. 확장성 (수평/수직 확장)
4. 보안 (인증, 암호화, 접근 제어)
5. 데이터 무결성 (백업, 일관성)
6. 모니터링 (로깅, 알림, 대시보드)
7. 재해 복구 (RPO, RTO)
8. 컴플라이언스 (규제, 감사)

각 질문은 one at a time. 비개발자 친화 표현 사용.

### Step 5: Domain × Profile 기본값 제시 + 조정

프로파일과 도메인을 조합하여 기본값을 제시한다:

```
프로파일 기반으로 다음 NFR을 제안합니다:
- 응답 시간: [값] (이유: [도메인] 기준 [근거])
- 가용성: [값] (이유: [프로파일] 기준 [근거])
- ...

조정이 필요한 항목이 있나요?
```

**도메인별 기본값 조정 예시:**
- 금융 + 소규모: 가용성 99.95% (금융은 기본보다 높음)
- 사내 도구 + 중규모: 가용성 99.5% (내부 사용이므로 낮춤)
- 헬스케어 + MVP: 보안 등급 상향 (HIPAA 필수)
- IoT + 대규모: 네트워크 지연 허용 상향

사용자가 조정한 항목은 `## 조정 이력`에 기록.

### Step 6: Save artifact

Create `devflow-docs/inception/nfr-requirements.md`:

```markdown
# NFR Requirements

**Timestamp**: [ISO 8601]
**Mode**: [GENERATE | IMPORT]
**Domain**: [선택된 도메인]
**Profile**: [선택된 프로파일]

## NFR Summary

| 카테고리 | 요구사항 | 근거 |
|---------|---------|------|
| 성능 | [값] | [도메인+프로파일 기준 근거] |
| 가용성 | [값] | [근거] |
| ... | ... | ... |

## 조정 이력
- [항목]: [원래 기본값] → [사용자 조정값] (이유: [사용자 설명])
```

## Review (Standard 이상)

depth가 Standard 이상이면:
1. `_shared/reviewers/artifact-reviewer-prompt.md` 읽기
2. 리뷰 서브에이전트 dispatch:
   - 산출물 경로: `devflow-docs/inception/nfr-requirements.md`
   - 상위 산출물: `devflow-docs/inception/requirements.md`, `devflow-docs/inception/user-stories.md` (있으면)
3. ✅ Approved → Return to Orchestrator
4. ❌ Issues → 수정 후 re-dispatch (최대 5회, 초과 시 사용자 escalate)

depth가 Minimal이면: 리뷰 스킵, 바로 Return to Orchestrator

**depth 확인**: `devflow-docs/devflow-state.md`의 `## Complexity` 필드를 읽는다.

## Return to Orchestrator

STOP.

```
[nfr-requirements 결과]
- 모드: [GENERATE | IMPORT]
- 도메인: [선택된 도메인]
- 프로파일: [선택된 프로파일]
- NFR 항목: [count]개 카테고리
- 사용자 조정: [count]개 항목
- 산출물: devflow-docs/inception/nfr-requirements.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

## Common Issues

### 사용자가 도메인을 모르거나 "기타" 선택 시
- 요구사항에서 도메인 특성을 추론
- 추론 근거를 사용자에게 제시: "결제 기능이 있으므로 이커머스 기준을 적용하겠습니다. 맞나요?"
- 확인 후 진행

### 프로파일 선택이 모호한 경우
- "현재 사용자가 몇 명인가요?" 추가 질문으로 범위 확인
- 확실하지 않으면 한 단계 높은 프로파일 적용 (안전 방향)
```

- [ ] **Step 2: Verify file structure**

Run: `head -3 skills/aidlc-nfr-requirements/SKILL.md`
Expected: `---` (frontmatter start)

- [ ] **Step 3: Commit**

```bash
git add skills/aidlc-nfr-requirements/
git commit -m "feat: add aidlc-nfr-requirements skill (Pre-Planning stage, GENERATE/IMPORT)"
```

---

## Chunk 3: Existing Skill Modifications

### Task 6: Extend `aidlc-application-design/SKILL.md` — NFR Design Patterns

**Files:**
- Modify: `skills/aidlc-application-design/SKILL.md`

**Context:** Comprehensive DETAIL 모드에서만 활성화되는 NFR Design Patterns 섹션을 추가한다. 활성화 조건: (1) Comprehensive depth + (2) DETAIL mode + (3) nfr-requirements.md 존재. 오케스트레이터가 `"DETAIL — NFR Design 포함"` 인라인 신호를 전달.

- [ ] **Step 1: Bump version in frontmatter**

Change `version: 0.4.0` → `version: 0.6.0`

- [ ] **Step 2: Add NFR Design section after Step 4 (DETAIL Mode)**

`skills/aidlc-application-design/SKILL.md`의 Step 4 (DETAIL Mode — 상세 설계) 끝, `## Review` 섹션 전에 추가:

```markdown

### Step 5: NFR Design Patterns (Comprehensive DETAIL + NFR Design 신호 시)

호출 텍스트에 `NFR Design 포함` 키워드가 있을 때만 실행.
없으면 이 Step을 스킵하고 Review로 진행.

**활성화 조건** (3가지 모두 충족):
1. depth가 Comprehensive
2. DETAIL 모드
3. 오케스트레이터가 `NFR Design 포함` 신호 전달

**핵심 원칙**: Claude는 **정보 정리자**이지 **의사결정자**가 아니다. NFR 설계에는 정답이 없고 트레이드오프만 존재한다.

1. `devflow-docs/inception/nfr-requirements.md` 읽기
2. 각 NFR 카테고리에 대해 컴포넌트 설계와 연계된 패턴 옵션 테이블 생성:
   - 각 패턴의 장점, 단점, 비용 영향을 병렬 제시
   - **"권장 패턴: X" 형식 사용 금지** — 옵션만 제시
   - `⚠️ 이 선택은 기술 담당자와 상의를 권장합니다` 경고 포함
3. `application-design.md`에 `## NFR Design Patterns` 섹션 추가

**산출물 형식:**
```markdown
## NFR Design Patterns

> ⚠️ NFR 패턴 선택은 운영 환경과 비용에 따라 달라집니다.
> 기술 담당자와 상의를 권장합니다.

### [NFR 카테고리]: [요구사항 값]

| 패턴 | 장점 | 단점 | 비용 영향 |
|------|------|------|----------|
| [패턴 A] | [장점] | [단점] | [비용] |
| [패턴 B] | [장점] | [단점] | [비용] |
| [패턴 C] | [장점] | [단점] | [비용] |
```
```

- [ ] **Step 3: Update DETAIL Mode return format**

기존 DETAIL Mode 반환:
```
[application-design 결과 — DETAIL]
- 상세 설계 완료: [count]개 컴포넌트
- 산출물: devflow-docs/inception/application-design.md (업데이트됨)
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

변경 (NFR Design 포함 시):
```
[application-design 결과 — DETAIL]
- 상세 설계 완료: [count]개 컴포넌트
- NFR Design Patterns: [count]개 카테고리 (Comprehensive + NFR 신호 시)
- 산출물: devflow-docs/inception/application-design.md (업데이트됨)
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

- [ ] **Step 4: Verify changes**

Run: `grep "NFR Design" skills/aidlc-application-design/SKILL.md`
Expected: Multiple matches including "Step 5: NFR Design Patterns"

- [ ] **Step 5: Commit**

```bash
git add skills/aidlc-application-design/SKILL.md
git commit -m "feat: add NFR Design Patterns to application-design Comprehensive DETAIL (v0.6.0)"
```

---

### Task 7: Update `aidlc-inception-orchestrator/SKILL.md` — Pre-Planning Gates

**Files:**
- Modify: `skills/aidlc-inception-orchestrator/SKILL.md`

**Context:** 가장 큰 변경. 기존 5개 게이트에 Pre-Planning Gate(조건부), User-Stories Gate(표준+Hold), NFR-Requirements Gate(모드 선택+표준+Hold)를 추가한다. INCEPTION 스테이지 순서와 게이트 정의를 모두 업데이트해야 한다.

- [ ] **Step 1: Bump version**

Change `version: 0.4.0` → `version: 0.6.0`

- [ ] **Step 2: Update INCEPTION 스테이지 순서**

기존 (line 19-22):
```
workspace-detection → [Complexity Gate] → requirements-analysis → [Open Questions Gate]
  → workflow-planning → [Approach Proposal Gate] → application-design (조건부) → 완료
```

변경:
```
workspace-detection → [Complexity Gate] → requirements-analysis → [Open Questions Gate]
  → [Pre-Planning Gate] → (user-stories) → (nfr-requirements)
  → workflow-planning → [Approach Proposal Gate]
  → (application-design + NFR Design) → 완료
```

- [ ] **Step 3: Add Pre-Planning Gate (게이트 3과 4 사이)**

기존 `### 3. requirements-analysis 게이트` 뒤, `### 4. workflow-planning 게이트` 앞에 추가.
기존 4, 5번 게이트를 6, 7번으로 번호 변경.

```markdown

### 4. Pre-Planning Gate [조건부 게이트]

requirements-analysis 게이트 통과 후, workflow-planning 호출 전에 실행.
Pre-Planning은 INCEPTION 내 스테이지 그룹명이며, workflow-plan.md의 `### PRE-PLANNING` 섹션에 결과가 기록된다.

**Minimal complexity**: 자동 스킵 — user-stories, nfr-requirements 모두 건너뜀. workflow-planning으로 직행.

**Comprehensive complexity**: 자동 포함 — user-stories, nfr-requirements 모두 실행. User-Stories 게이트로 진행.

**Standard complexity**: 3-option 게이트 제시

```
요구사항 분석이 완료되었습니다. 다음 단계 전에 추가 분석이 가능합니다:

A) User Stories + NFR 수집 → 두 스테이지 모두 실행
B) NFR 수집만 → nfr-requirements만 실행 (상용 배포 시 권장)
C) 바로 워크플로우 계획으로 → 추가 분석 스킵
```

A → User-Stories 게이트로 진행
B → NFR-Requirements 게이트로 진행 (user-stories 스킵)
C → workflow-planning으로 직행

### 5. User-Stories 게이트 [표준 게이트 + Hold]

Pre-Planning Gate에서 user-stories 실행이 결정된 경우에만.
aidlc-user-stories 호출 → 결과 게이트:

```
[user-stories 결과 표시]
A) 변경 요청 → user-stories 재호출
B) 승인, 다음 단계 진행 → NFR-Requirements 게이트
H) 보류 (나중에 돌아옴) → HELD 상태 저장, NFR-Requirements 게이트로 진행
```

### 6. NFR-Requirements 게이트 [모드 선택 게이트 + 표준 게이트 + Hold]

Pre-Planning Gate에서 nfr-requirements 실행이 결정된 경우에만.

**6a. 모드 선택 (오케스트레이터 소유)**:
```
NFR 요구사항을 어떻게 진행하시겠습니까?

A) Claude가 질문하며 수집 (GENERATE)
B) 이미 작성된 NFR 문서가 있음 (IMPORT)
S) 이 단계 건너뛰기 (SKIP)
```

A → `"Mode: GENERATE"` 인라인 신호로 aidlc-nfr-requirements 호출
B → `"Mode: IMPORT"` 인라인 신호로 aidlc-nfr-requirements 호출
S → SKIPPED 상태 저장, workflow-planning으로 진행

**6b. 결과 게이트**:
```
[nfr-requirements 결과 표시]
A) 변경 요청 → nfr-requirements 재호출
B) 승인, 다음 단계 진행 → workflow-planning
H) 보류 (나중에 돌아옴) → HELD 상태 저장, workflow-planning으로 진행
```
```

- [ ] **Step 4: Renumber existing gates and reposition sections**

기존 `### 4. workflow-planning 게이트` → `### 7. workflow-planning 게이트`
기존 `### 워크트리 결과 게이트` → 게이트 7 (workflow-planning) 바로 뒤에 유지 (상대 위치 변경 없음)
기존 `### INCEPTION → CONSTRUCTION 라우팅` → 워크트리 결과 게이트 뒤에 유지
기존 `### 5. application-design 게이트` → `### 8. application-design 게이트`
기존 `### 5a. LIST 게이트` → `### 8a. LIST 게이트`
기존 `### 5b. DETAIL 게이트` → `### 8b. DETAIL 게이트`

- [ ] **Step 5: Add NFR Design activation logic to application-design gate**

`### 8b. DETAIL 게이트` 내용에 NFR Design 활성화 로직 추가:

기존:
```
[application-design DETAIL 결과 표시]
A) 변경 요청 → application-design: DETAIL 재호출
B) 승인, INCEPTION 완료
```

변경:
```
[application-design DETAIL 결과 표시]
A) 변경 요청 → application-design: DETAIL 재호출
B) 승인, INCEPTION 완료
```

**DETAIL 호출 시 NFR Design 활성화 판단:**
3가지 조건 모두 충족 시 인라인 신호 추가:
1. depth가 Comprehensive
2. DETAIL 모드
3. `devflow-docs/inception/nfr-requirements.md` 존재

충족 시: `"aidlc-application-design: DETAIL — NFR Design 포함"`
미충족 시: `"aidlc-application-design: DETAIL"` (기존대로)

- [ ] **Step 6: Add Hold/Skip handling to Error Handling section**

기존 `## Error Handling` 섹션에 추가:

```markdown

### Hold/Skip 상태 처리
Pre-Planning 스테이지에서 HELD 또는 SKIPPED가 발생하면:
1. devflow-state에 상태 기록: `user-stories: HELD` 또는 `nfr-requirements: SKIPPED`
2. devflow-audit에 로깅
3. 다음 스테이지로 진행
4. workflow-plan.md의 `### PRE-PLANNING` 섹션에 상태 기록
```

- [ ] **Step 7: Verify changes**

Run: `grep -c "게이트" skills/aidlc-inception-orchestrator/SKILL.md`
Expected: Count should be significantly higher than before (was ~15, should be ~25+)

- [ ] **Step 8: Commit**

```bash
git add skills/aidlc-inception-orchestrator/SKILL.md
git commit -m "feat: add Pre-Planning gates to inception orchestrator (v0.6.0)"
```

---

### Task 8: Update `aidlc-workflow-planning/SKILL.md` — PRE-PLANNING section

**Files:**
- Modify: `skills/aidlc-workflow-planning/SKILL.md`

**Context:** Approved Stages에 PRE-PLANNING 섹션을 추가하고, 접근법 생성 시 NFR 존재를 반영한다.

- [ ] **Step 1: Bump version**

Change `version: 0.4.0` → `version: 0.6.0`

- [ ] **Step 2: Update Step 1 (Load context) to include Pre-Planning outputs**

`skills/aidlc-workflow-planning/SKILL.md`의 Step 1에 추가:
```markdown
- `devflow-docs/inception/user-stories.md` — 사용자 스토리 (있으면)
- `devflow-docs/inception/nfr-requirements.md` — NFR 요구사항 (있으면)
```

- [ ] **Step 3: Update Step 4 artifact format**

`skills/aidlc-workflow-planning/SKILL.md`의 Step 4에서 `## Approved Stages` 형식 변경.

기존 (line 93-104):
```markdown
## Approved Stages
### CONSTRUCTION
- application-design: [included | skipped] — [reason]
- units-generation: [included | skipped] — [reason]
- code-generation: included — always
- build-and-test: included — always
```

변경:
```markdown
## Approved Stages
### PRE-PLANNING
- user-stories: [included | skipped | held] — [reason]
- nfr-requirements: [included | skipped | held] — [reason]

### CONSTRUCTION
- application-design: [included | skipped] — [reason]
- units-generation: [included | skipped] — [reason]
- code-generation: included — always
- build-and-test: included — always
```

- [ ] **Step 4: Add NFR context to Step 2 (approach generation)**

Step 2 끝에 추가:

```markdown

**NFR 컨텍스트 반영:**
`devflow-docs/inception/nfr-requirements.md`가 존재하면:
- "안전한/완전" 접근법에 `application-design: Comprehensive` 포함 (NFR Design 활성화)
- "빠른/간결" 접근법에서도 NFR 존재 사실 명시
- 접근법 형식에 NFR 관련 고려사항 추가
```

- [ ] **Step 5: Add PRE-PLANNING parsing note**

Step 4 끝에 주석 추가:

```markdown
**참고**: `### PRE-PLANNING` 섹션은 오케스트레이터가 파싱하지 않는다.
Pre-Planning 스테이지는 오케스트레이터가 직접 게이트로 관리하며, 이 섹션은 기록용.
기존 `### CONSTRUCTION` 파싱 로직은 변경 없음.
```

- [ ] **Step 6: Verify changes**

Run: `grep "PRE-PLANNING" skills/aidlc-workflow-planning/SKILL.md`
Expected: At least 2 matches

- [ ] **Step 7: Commit**

```bash
git add skills/aidlc-workflow-planning/SKILL.md
git commit -m "feat: add PRE-PLANNING section to workflow-planning (v0.6.0)"
```

---

### Task 9: Update `plugin.json` — version bump

**Files:**
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: Bump version**

Change `"version": "0.5.0"` → `"version": "0.6.0"`

- [ ] **Step 2: Verify**

Run: `cat .claude-plugin/plugin.json`
Expected: `"version": "0.6.0"`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: bump plugin version to v0.6.0"
```

---

## Execution Order

Tasks 1-3 (shared infrastructure) → Tasks 4-5 (new skills) → Tasks 6-8 (existing modifications) → Task 9 (version bump)

Tasks within each group are independent and can be parallelized.
