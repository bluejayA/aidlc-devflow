# Auto Mode 설계 문서

**Complexity:** Comprehensive
**Date:** 2026-04-02
**Author:** Jay + Claude brainstorming

## Summary

초보자를 위한 완전 자동 devflow 모드. 사용자가 요구사항만 입력하면 INCEPTION → CONSTRUCTION → BUILD & TEST를 Claude가 자율적으로 진행하고, 각 flow 종료 시 5개 에이전트 리뷰를 필수로 거친다. 전 과정의 판단과 선택을 기록하여 사후 검토가 가능하다.

## Assumptions

- auto-mode는 greenfield 전용이다. brownfield에서는 기존 devflow로 전환한다.
- 기존 devflow **SKILL.md 파일**은 한 줄도 수정하지 않는다. 공유 상태 파일(devflow-state.md, session-summary.md 등)은 현행 포맷으로 기록하며, 이는 기존 devflow와 동일한 규약이다. (U1 해소)
- auto-mode는 언제든 깔끔하게 분리 가능해야 한다 (파일 1개 삭제 + plugin.json 1줄 제거).
- 리뷰 자동수정 루프는 conventions의 5회 대신 **3회로 축소**한다. 근거: auto-mode는 자율 진행이므로 3회 실패는 "Claude가 해결할 수 없는 문제"를 의미하며, 추가 시도보다 사용자 에스컬레이션이 효과적이다. (U2 해소)

---

## 1. Architecture

```
┌────────────────────────────────────────────────┐
│                사용자 요구사항                     │
│                    │                            │
│            ┌───────┴───────┐                    │
│            ▼               ▼                    │
│   aidlc-auto-mode    aidlc-using-devflow        │
│   (단일 파일, 독립)    (현행 유지, 무수정)          │
│            │               │                    │
│            │          ┌────┴────┐               │
│            │          ▼         ▼               │
│            │   inception-  construction-        │
│            │   orchestrator  orchestrator        │
│            │          │         │               │
│            └────┬─────┴─────────┘               │
│                 ▼                               │
│         stage skills (공유, 무수정 재활용)          │
│   requirements-analysis, code-generation,       │
│   build-and-test, workspace-detection, ...      │
└────────────────────────────────────────────────┘
```

**원칙:**
- auto-mode는 단일 SKILL.md 파일 (~500줄)
- 기존 devflow SKILL.md 파일 무수정 (공유 상태 파일은 현행 포맷으로 기록)
- stage 스킬을 동일하게 호출
- 분리 시: 파일 1개 삭제 + plugin.json에서 1줄 제거
- 플러그인 startup 추가 토큰: ~30-40t (description 1줄)

### SKILL.md Frontmatter (M3)

```yaml
---
name: aidlc-auto-mode
description: |
  초보자를 위한 완전 자동 devflow. greenfield 전용.
  요구사항 입력 → inception → construction → build-test를 자동 진행하며
  각 flow 종료 시 5개 에이전트 리뷰 필수.
  Use for fully automated devflow for beginners. Greenfield only.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
---
```

### Trigger 구분 (M4)

auto-mode와 using-devflow의 트리거를 명확히 분리한다:

| | auto-mode | using-devflow |
|---|---|---|
| 트리거 키워드 | "auto 모드", "자동 모드", "auto mode", "알아서 만들어줘" | "devflow", "aidlc", "워크플로우", 일반 구현 요청 |
| invoke_mode | user-invocable | user-invocable |
| 우선순위 | "auto" 키워드 명시 시만 활성화 | auto 키워드 없는 모든 구현 요청 |

**충돌 방지:** "auto" 또는 "자동"이 명시적으로 포함된 경우에만 auto-mode가 트리거된다. 그 외 모든 개발 요청은 기존 using-devflow로 라우팅된다.

---

## 2. Flow & Components

```
사용자 요구사항 입력
  │
  ▼
[진입 조건 확인]
  ├─ greenfield? → NO → "auto 모드는 greenfield 전용입니다" → devflow 전환
  ├─ 첫 실행 아닌 경우 → "auto 모드로 계속 진행할까요?" 확인
  │
  ▼
[INCEPTION 자동 진행] ── 매 스테이지 완료 시 진행 메시지 표시
  ├─ workspace-detection   → "프로젝트 환경을 분석하고 있습니다..."
  ├─ complexity 자동 선언   → "프로젝트 규모를 판단하고 있습니다..."
  ├─ requirements-analysis → "요구사항을 분석하고 있습니다..."
  │   └─ 고위험 가정 게이트 (아래 상세)
  ├─ (user-stories)        → "사용자 시나리오를 작성하고 있습니다..."
  ├─ (nfr-requirements)    → "성능/보안 기준을 설정하고 있습니다..."
  ├─ workflow-planning     → "구현 계획을 수립하고 있습니다..."
  └─ (application-design)  → "시스템 구조를 설계하고 있습니다..."
  │
  ▼
[INCEPTION 리뷰] → "설계를 검토하고 있습니다... (5개 관점)"
  5개 리뷰어 전체 병렬 dispatch
  ├─ ALL PASS → 사용자 확인 게이트로
  ├─ ISSUES → 순차 수정 후 전체 re-dispatch (아래 상세)
  └─ 3회 초과 → 사용자 에스컬레이션
  │
  ▼
[사용자 확인 — 유일한 게이트]
  일상 언어 요약 + 자율 판단 하이라이트 + 선택지 기반 수정
  ├─ A) 항목별 수정 선택지 → 해당 스테이지 재실행
  └─ B) 승인 → CONSTRUCTION 자동 진행
  │
  ▼
[CONSTRUCTION 자동 진행] ── 매 스테이지 완료 시 진행 메시지 표시
  ├─ (units-generation)     → "구현 단위를 나누고 있습니다..."
  ├─ per-unit:
  │   ├─ (functional-design) → "[unit명] 상세 설계 중..."
  │   ├─ code-plan           → "[unit명] 구현 계획 작성 중..."
  │   └─ code-gen            → "[unit명] 코드 생성 중..."
  ├─ build-and-test          → "빌드 및 테스트 실행 중..."
  │   └─ auto-fix 루프 (최대 3회)
  │
  ▼
[CONSTRUCTION 리뷰] → "코드를 검토하고 있습니다... (5개 관점)"
  5개 리뷰어 전체 병렬 dispatch
  ├─ ALL PASS → 최종 결과 표시
  ├─ ISSUES → 순차 수정 후 전체 re-dispatch
  └─ 3회 초과 → 사용자 에스컬레이션
  │
  ▼
[최종 결과물 제시 + 실행 안내]
  → "다음 작업도 auto 모드로 진행할까요?"
```

### Stage 스킬 호출 인라인 신호 (M1)

기존 오케스트레이터와 동일한 인라인 신호 패턴을 사용한다:

| 스킬 | 인라인 신호 |
|------|-----------|
| workspace-detection | (신호 없음, 직접 호출) |
| requirements-analysis | `"Complexity: [level]"` |
| requirements-analysis 재호출 | `"aidlc-requirements-analysis: UPDATE — [변경 내용]"` |
| user-stories | `"Complexity: [level]"` |
| nfr-requirements | `"Mode: GENERATE"`, `"Complexity: [level]"` |
| workflow-planning | `"Complexity: [level]"` |
| application-design LIST | `"Complexity: [level]"` |
| application-design DETAIL | `"aidlc-application-design: DETAIL"` (NFR 있으면 `"— NFR Design 포함"` 추가) |
| code-generation Plan | `"Complexity: [level]"` + unit명 |
| code-generation Generate | `"aidlc-code-generation: GENERATE — proceed with the approved plan for [unit-name]"` |
| build-and-test | (신호 없음, 직접 호출) |

### Complexity 자동 선언 기준 (M2)

workspace-detection 결과를 기반으로 아래 매핑으로 자동 선언한다:

| 기준 | Minimal | Standard | Comprehensive |
|------|---------|----------|---------------|
| 예상 파일 수 | ~5개 이하 | 6-20개 | 20개 이상 |
| 서비스/컴포넌트 수 | 단일 | 2-3개 | 4개 이상 |
| DB 필요 여부 | 불필요 | 단일 DB | 복수 DB 또는 복잡한 스키마 |
| 외부 연동 | 없음 | 1-2개 API | 3개 이상 또는 복잡한 인증 |
| 대표 예시 | CLI 도구, 유틸리티 | CRUD 웹앱, REST API | 마이크로서비스, 플랫폼 |

복수 기준이 서로 다른 레벨을 가리키면 **높은 쪽**으로 선언한다. decision-log에 각 기준별 판단 근거를 기록한다.

### 자동 판단 규칙

| 판단 지점 | 규칙 |
|----------|------|
| Complexity | workspace-detection 결과 + 위 매핑 기준으로 자동 선언 |
| 기술 스택 | CLAUDE.md 우선 → 카탈로그 "(권장)" 자동 선택 (번들 없음, 규칙 기반) |
| 열린 질문 | 업계 기본값으로 가정 처리, decision-log에 기록 |
| Pre-Planning 포함 | Minimal→스킵, Standard→NFR만, Comprehensive→전체 |
| Approach 선택 | workflow-planning 결과에서 첫 번째(권장) 자동 선택 |
| SDD vs 인라인 | Minimal→인라인 강제, Standard/Comprehensive + unit 2개 이상→SDD |

### 리뷰어 목록 및 프로토콜 (M5, U3)

**5개 리뷰어 (INCEPTION/CONSTRUCTION 동일):**
1. spec-reviewer (~347t)
2. code-reviewer (~1,013t)
3. quality-reviewer (~398t)
4. security-reviewer (~440t)
5. maintainability-reviewer (~438t)

**INCEPTION 리뷰:** auto-mode가 직접 5개 리뷰어를 병렬 dispatch한다. 설계 산출물 대상이므로 `requesting-code-review` 스킬의 범위 밖이다.

**CONSTRUCTION 리뷰:** `aidlc-requesting-code-review`를 R1 모드로 호출하여 전체 위임한다. R1은 이미 4단계 리뷰(Stage 1: spec, Stage 2: code-quality, Stage 3: security, Stage 4: maintainability)를 수행하므로 auto-mode가 별도로 리뷰어를 추가 dispatch하지 않는다. Comprehensive가 아닌 경우 Stage 4가 스킵되지만, auto-mode에서는 모든 depth에서 전체 4단계를 실행하도록 `"Review: full-depth"` 인라인 신호를 전달한다. (U3 해소)

**리뷰 루프 최대 횟수:** 3회 (conventions의 5회 대신. 근거는 Assumptions 참조). (U2 해소)

### 리뷰 수정 충돌 해소 — 순차 수정 + 전체 re-dispatch

```
리뷰어 5개 병렬 dispatch
  → 결과 수집
  → ISSUES 리뷰어 피드백을 우선순위 순서대로 순차 수정:
    1순위: security (보안 이슈 먼저)
    2순위: spec (요구사항 정합성)
    3순위: code → quality → maintainability
  → 전체 5개 리뷰어 re-dispatch
  → 최대 3라운드
```

### 고위험 가정 게이트

requirements-analysis 완료 후 가정 목록을 평가한다.

**고위험 가정 판별 기준:**
- 인증/보안 방식 관련
- 유료 외부 서비스 의존
- 데이터 모델의 핵심 구조

**고위험 가정 1건 이상 → 미니 게이트 삽입:**
```
확인이 필요한 자동 판단이 있습니다:
1. 로그인 방식: 구글/카카오 계정 로그인 (직접 이메일/비밀번호가 맞나요?)
2. 결제 연동: 없음으로 가정 (결제 기능이 필요한가요?)

A) 맞습니다, 계속 진행
B) 수정할 부분이 있습니다 → [번호 선택]
```

고위험 가정 0건 → 자동 진행.

### 사용자 확인 게이트 — 일상 언어

```
## 설계가 완료되었습니다

만들려는 것: 로그인 기능이 있는 웹앱
프로젝트 규모: 큰 프로젝트 (서비스 3개 + 데이터베이스)
기술 스택: Next.js + PostgreSQL

## 자동으로 결정한 항목 (검토해 주세요)
1. 로그인 방식 → 구글/카카오 계정 로그인 (이유: 사용자 명세 없음)
2. 데이터베이스 → PostgreSQL (이유: 범용성 높은 기본 선택)
3. 응답 속도 목표 → 0.5초 이내 (이유: 웹앱 업계 기본값)

설계 검토 결과: 5개 관점 모두 통과

상세 내용: devflow-docs/inception/ 에서 확인 가능

A) 수정할 부분이 있습니다
   1. 로그인 방식 변경
   2. 기술 스택 변경
   3. 기타 (직접 입력)
B) 좋습니다, 코드 생성을 시작합니다
```

### 최종 결과물 + 실행 안내

```
프로젝트가 완성되었습니다!

생성된 파일: [N]개
테스트: [N]개 통과

→ 지금 바로 실행해볼까요?
A) 네, 실행 방법을 알려주세요
   → 프로젝트별 실행 명령 안내
B) 나중에 실행하겠습니다

다음 작업도 auto 모드로 진행할까요?
```

### 에스컬레이션 메시지 원칙

- "문제/에러/실패" 대신 → "확인이 필요한 부분"
- "devflow로 전환" 대신 → "하나씩 확인하면서 진행하기 (단계별 모드)"
- 항상 진행률 포함: "[N]단계 중 [M]단계 완료"
- 기술 용어는 괄호 안 부연 또는 생략

### 세션 체이닝 상태 전이 (E1)

첫 결과물 이후 "다음 작업도 auto 모드로?" 질문 시:

| 사용자 선택 | 상태 전이 |
|------------|----------|
| auto 계속 | 현재 devflow-state를 `finished`로 마킹 → `.archive/`로 이동 → 새 auto-mode 세션 시작 |
| devflow 전환 | 현재 devflow-state를 `finished`로 마킹 → `.archive/`로 이동 → using-devflow 안내 |
| 종료 | 현재 devflow-state를 `finished`로 마킹 → 세션 종료 |

auto-mode 간 연속 실행에서 이전 세션의 산출물은 `.archive/`에 보존되며, 새 세션은 깨끗한 상태로 시작한다. 이전 세션의 decision-log도 함께 아카이브된다.

### 실행 안내 범위 (E2)

최종 결과물 제시 시 실행 안내는 auto-mode의 범위 내이다. 근거: 초보자 UX 리뷰에서 "완료 후 실행 방법 모름"이 이탈 1순위로 확인됨. 안내 범위는 프로젝트 빌드 시스템에서 감지한 실행 명령 1줄 + 접속 URL 표시로 제한한다.

---

## 3. State Management & devflow 호환

### 파일 구조

```
devflow-docs/
├─ devflow-state.md                      ← 현행 포맷 동일 (호환)
├─ session-summary.md                    ← 현행 포맷 동일 (호환)
├─ devflow-audit.md                      ← 현행 포맷 동일 (호환)
├─ auto-decision-log-inception.md        ← auto 전용 (append-only, 감사 전용)
├─ auto-decision-log-construction.md     ← auto 전용 (append-only, 감사 전용)
├─ inception/                            ← stage 스킬이 생성
│   └─ workflow-plan.md                  ← Selected Approach 마킹 필수
└─ construction/                         ← stage 스킬이 생성
```

### Checkpoint 블록 패턴

매 스테이지 완료 시 단일 블록으로 실행. 누락 방지를 위해 개별 파일 업데이트를 나열하지 않고 하나의 체크포인트로 묶는다:

```
1단계: 기록
  다음 4개 파일을 순서대로 업데이트:
  1. devflow-state.md — Current Stage 갱신
  2. session-summary.md — Completed Work에 추가
  3. devflow-audit.md — 이벤트 1줄 추가
  4. auto-decision-log-[phase].md — 판단 상세 append

2단계: 검증
  devflow-state.md를 Read로 열어
  Current Stage 값이 방금 완료한 스테이지와 일치하는지 확인.
  불일치 시 즉시 수정.

3단계: 진행 메시지
  사용자에게 다음 스테이지 진행 메시지를 표시.
```

### devflow 호환 레이어

| 파일 | 기록 시점 | 필드 |
|------|----------|------|
| devflow-state.md | 매 checkpoint | Current Phase, Current Stage, Complexity, Selected Approach, Approved Stages, Completed Units, Active Unit |
| session-summary.md | 매 checkpoint | Current State, Completed Work, Key Decisions, Commit |
| devflow-audit.md | 매 checkpoint | timestamp + stage + event 1줄 |
| workflow-plan.md | approach 자동 선택 시 | Selected Approach 마킹 + Approved Stages 기록 |
| auto-decision-log-[phase].md | 매 checkpoint | 판단 상세 (append-only) |

### devflow-state.md 화이트리스트

auto 모드가 devflow-state.md에 기록할 수 있는 필드. 이 목록에 없는 필드는 쓰지 않는다. auto 전용 메타데이터(auto-fix 횟수, 리뷰 라운드 등)는 auto-decision-log에 기록:

- `## Current Phase` → INCEPTION | CONSTRUCTION | complete
- `## Current Stage` → 스테이지명 | 스테이지명 (in-progress)
- `## Complexity` → Minimal | Standard | Comprehensive
- `## Selected Approach` → 접근법명
- `## Approved Stages` → 스테이지 목록
- `## Completed Units` → unit 목록
- `## Active Unit` → 현재 unit
- `## Worktree` → branch, path (사용 시)

### decision-log 운용 규칙

- **append-only**: 새 항목을 파일 끝에 추가만 한다. 기존 항목 수정 금지.
- **감사 전용**: auto-mode 실행 중 과거 결정 참조 시 devflow-state.md만 읽는다. decision-log를 Read하지 않는다.
- **사후 검토용**: 사용자가 명시적으로 요청할 때만 읽는다.
- **이유**: 컨텍스트 소비 방지. Comprehensive 프로젝트에서 수백 줄 가능.

### decision-log 포맷

```markdown
## [2026-04-02T14:30:05] complexity-declaration
- decision: Comprehensive
- reason: "3개 서비스 + DB 스키마 + API 설계 필요"
- alternatives_considered: ["Standard — 단일 서비스면 적합"]

## [2026-04-02T14:31:00] requirements-analysis
- decision: 가정 2건 자동 승인
- assumptions:
  - "인증은 OAuth2 기반" (사용자 명세 없음, 업계 기본값)
  - "DB는 PostgreSQL" (CLAUDE.md 프리셋)
- open_questions_resolved: 0

## [2026-04-02T14:32:00] tech-stack
- selections:
  | 계층 | 선택 | 근거 |
  |------|------|------|
  | Frontend | Next.js + Tailwind + shadcn | CLAUDE.md 명시 |
  | Backend | FastAPI | 카탈로그 권장 + AI/ML 요구사항 |
- source_priority: CLAUDE.md → 카탈로그 권장 → 업계 기본값

## [2026-04-02T14:35:00] inception-review
- reviewers: [spec, code, quality, security, maintainability]
- results:
  | reviewer | verdict | issues |
  |----------|---------|--------|
  | quality-reviewer | CONDITIONAL | naming 1건 |
  | (나머지) | PASS | — |
- auto-fix-attempt: 1/3
- fix-detail: "naming convention 수정"
- re-review: quality-reviewer → PASS
- final: ALL PASS
```

### 전환 시나리오

| 시나리오 | devflow-state 상태 | workflow-plan.md | using-devflow 동작 |
|---------|-------------------|-----------------|-------------------|
| INCEPTION 중 에스컬레이션 | `Phase: INCEPTION`, `Stage: [현재]` | 미완성 가능 | inception-orch가 해당 stage부터 재개 |
| INCEPTION 확인 후 devflow 전환 | `Phase: CONSTRUCTION`, `Stage: (pending)` | Selected Approach 마킹됨 | construction-orch가 정상 라우팅 |
| CONSTRUCTION 중 에스컬레이션 | `Phase: CONSTRUCTION`, `Stage: [현재]` | 마킹됨 | construction-orch가 해당 stage부터 재개 |
| 완료 후 devflow 전환 | `Phase: complete` | 마킹됨 | finishing-branch 안내 |

---

## 4. Error Handling

### 글로벌 서킷 브레이커

phase당 총 리트라이 상한:
- INCEPTION: 최대 5회 (모든 유형의 리트라이 합산)
- CONSTRUCTION: 최대 8회

상한 도달 시:
```
거의 완성되었지만 자동으로 해결하기 어려운 부분이 있습니다.
완료된 작업: [N]단계 중 [M]단계
A) 하나씩 확인하면서 진행하기 (단계별 모드)
B) 현재 상태 저장 후 나중에 이어하기
```

### 스테이지 실행 상태 추적

**시작 시:** devflow-state.md Current Stage를 `[stage-name] (in-progress)` 기록
**완료 시 (checkpoint):** `(in-progress)` 제거

**재개 시 교차 검증:**
- `(in-progress)` 발견 → 산출물 파일 존재 확인
- 산출물 있음 → 완료 처리, 다음 스테이지 재개
- 산출물 없음 → 해당 스테이지 처음부터 재실행

### 1. Stage 스킬 호출 실패

**실패 판정 기준:**
- 스킬이 산출물 파일을 생성하지 않음
- 스킬 반환값에 기대 패턴 없음 (예: requirements-analysis → "열린 질문: [N]개")
- 스킬이 에러 메시지를 반환

**대응:**
- 1회 자동 재시도
- 재시도 실패 → 사용자 에스컬레이션:
  ```
  [N]단계 중 [M]단계까지 완료되었습니다.
  [스테이지 설명]에서 확인이 필요합니다: [한 문장]
  A) 다시 시도
  B) 하나씩 확인하면서 진행하기 (단계별 모드)
  ```
- decision-log에 실패 이벤트 + 에러 내용 기록
- 글로벌 리트라이 카운터 +1

### 2. 리뷰어 실패

**2a. 리뷰어 자체 실패 (타임아웃/파싱 에러):**
- 실패 리뷰어 1회 재시도
- 재시도 실패 → 응답한 리뷰어만으로 판정 (최소 3/5 응답 필요)
- 3개 미만 응답 → 전체 리뷰 재시도 1회
- 그래도 3개 미만 → 사용자 에스컬레이션
- decision-log에 실패 리뷰어 + 사유 기록

**2b. 리뷰 자동수정 실패 (3라운드 초과):**
- 수정 우선순위: security → spec → code → quality → maintainability
- 순차 수정 후 전체 5개 re-dispatch
- 3라운드 초과 → 사용자 에스컬레이션 (진행률 포함)
- 글로벌 리트라이 카운터 +3

### 3. build-and-test 실패

**auto-fix 대상** (테스트 실패, 린트 에러):
- auto-fix 루프 최대 3회
- 수정 후 전체 테스트 재실행 (regression 방지)

**auto-fix 스킵 대상:**
- 빌드 실패, 환경 문제, auth/security 태그 unit
- 즉시 에스컬레이션

**auto-fix 3회 소진:**
- 에스컬레이션 (진행률 포함)
- 글로벌 리트라이 카운터 +3

### 4. 세션 중단/재개

**재개 시 (자동 감지):**
- devflow-state.md + auto-decision-log 존재 → 자동 감지:
  ```
  이전에 자동 모드로 진행하던 작업이 있습니다.
  진행 상황: [N]단계 중 [M]단계 완료
  A) 이어서 진행하기
  B) 처음부터 새로 시작하기
  ```
- A 선택 시: 교차 검증 후 마지막 완료 스테이지 다음부터 재개

### 5. greenfield 오판

- requirements-analysis에서 기존 코드 참조 발견 시 decision-log에 경고
- INCEPTION 사용자 확인 게이트 하이라이트에 포함:
  "기존 코드가 일부 감지되었습니다. 새로 만드는 프로젝트가 맞나요?"

### 6. 고위험 가정 대량 거부

- requirements-analysis만 수정된 가정으로 재실행
- 후속 스테이지(user-stories, nfr 등)는 정상 자동 진행
- decision-log에 변경 내용 기록
- 글로벌 리트라이 카운터 +1

### 에스컬레이션 메시지 원칙

- "문제/에러/실패" 대신 → "확인이 필요한 부분"
- "devflow로 전환" 대신 → "하나씩 확인하면서 진행하기 (단계별 모드)"
- 항상 진행률 포함: "[N]단계 중 [M]단계 완료"
- 기술 용어는 괄호 안 부연 또는 생략

---

## 5. Testing Strategy

### 2계층 검증 체계

#### Layer 1: 파일 기반 정적 검증 (일상, 토큰 비용 0)

SKILL.md 수정 시마다 실행. 셸 스크립트로 자동화:

- devflow-state.md 스키마 검증 — 화이트리스트 필드 존재 여부 grep
- session-summary.md 필수 섹션 존재 확인
- workflow-plan.md Selected Approach 마킹 확인
- auto-decision-log 포맷 검증 — 타임스탬프 + decision + reason 패턴
- SKILL.md 구조 검증 — skill-reviewer-prompt.md로 1회 리뷰

#### Layer 2: 시나리오 기반 eval (릴리스 전)

skill-creator eval로 서브에이전트 실행.

**P0 — 배포 차단 필수:**

| # | 시나리오 | 기대 결과 | 검증 유형 |
|---|---------|----------|----------|
| 1 | 정상 greenfield E2E | 전체 플로우 완료 + 산출물 생성 | binary |
| 2 | devflow 전환 호환성 | state + summary + workflow-plan 정합 | binary |
| 3 | 세션 재개 교차 검증 | 자동 감지 + 산출물 교차 검증 + 재개 | binary |

**P1 — 배포 전 권장:**

| # | 시나리오 | 기대 결과 | 검증 유형 |
|---|---------|----------|----------|
| 4 | brownfield 거부 | "greenfield 전용" 안내 | binary |
| 5 | 고위험 가정 게이트 | 미니 게이트 발동 | binary |
| 6 | 리뷰 자동수정 | 순차 수정 + re-dispatch | binary |
| 7 | 서킷 브레이커 | 상한 도달 + 에스컬레이션 + 상태 정합 | binary |
| 8 | 모호한 요구사항 | 자동 구체화 + 가정 기록 | judgment |
| 9 | 완료 후 실행 안내 | 실행 명령 + URL 안내 출력 | binary |

**P2 — 주기적 스팟체크:**

| # | 시나리오 | 기대 결과 | 검증 유형 |
|---|---------|----------|----------|
| 10 | 에스컬레이션 메시지 톤 | 초보자 친화 표현 + 진행률 | judgment |
| 11 | 결과 불만족 재조정 | 수정 범위 확인 + 재실행 | judgment |
| 12 | auto→devflow→auto 왕복 | 상태 정합성 유지 | binary |
| 13 | 부분 checkpoint 복구 | 교차 검증 → 누락 파일 재생성 | binary |

#### 시뮬레이션 불가 항목

| 시나리오 | 이유 | 대안 |
|---------|------|------|
| 리뷰어 타임아웃 | 장애 주입 불가 | 의도적 불완전 입력으로 ISSUES 경로 간접 검증 |
| 파일 I/O 에러 | 파일시스템 장애 재현 불가 | 수동 파일 삭제 후 resume 확인 |
| 컨텍스트 한계 도달 | 시뮬레이션 비용 과다 | decision-log 크기 모니터링 대체 |
