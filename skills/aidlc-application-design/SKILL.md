---
name: aidlc-application-design
description: Use when component and service structure needs to be designed before implementation, as a conditional INCEPTION stage after workflow-planning.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/application-design.md
  skill_nature: hybrid
  lifecycle: active
  model_dependency: "모델이 컴포넌트 경계를 임의로 결정함"
  amplification_notes: "도메인 entity + 서비스 구조 명시적 분해"
---

# aidlc-application-design

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 애플리케이션 설계: 신규 컴포넌트/서비스 구조 설계 -->

## Purpose

Design the component and service structure before implementation begins.

## Execution Modes

### LIST Mode (기본)
일반 호출. 컴포넌트 목록만 생성하고 STOP.
모든 depth에서 `application-design.md`에 컴포넌트 목록을 저장한다 (Minimal 포함).

### DETAIL Mode
호출 텍스트에 `DETAIL` 키워드 포함 시 활성화:
`"aidlc-application-design: DETAIL — 승인된 목록으로 상세 설계 진행"`

DETAIL 모드에서는:
1. `devflow-docs/inception/application-design.md` 읽기 (목록 단계 결과)
2. depth에 따라 상세 설계 진행:
   - **Standard**: 주요 인터페이스 + 의존성
   - **Comprehensive**: 전체 인터페이스 + 의존성 + 데이터 소유 + 상호작용 다이어그램
3. `application-design.md` 업데이트 후 STOP

**depth 확인 (Primary)**: 호출 텍스트에 `Depth: [level]` 패턴이 있으면 그 값을 사용.
**depth 확인 (Fallback)**: 호출 텍스트에 없으면 `devflow-docs/inception/workflow-plan.md`의 `## Stage Depths` → `application-design` 행에서 읽는다.

**Minimal depth**: LIST Mode만 실행. DETAIL 호출 없음.

## Execute

### Step 1: Load context

Read the following files (if they exist):
- `devflow-docs/inception/requirements.md` — functional and non-functional requirements
- `devflow-docs/inception/workspace.md` — greenfield/brownfield context

### Step 2: Generate component list (LIST Mode)

DETAIL 모드인 경우 Step 4로 건너뛴다.

각 새 컴포넌트에 대해 아래 정보만 수집 (상세 설계는 DETAIL 모드에서):
- **Name**: 컴포넌트명
- **Responsibility**: 한 줄 책임
- **Type**: Service | Repository | Adapter | Controller | Util 중 하나

반환 형식:
```markdown
## 컴포넌트 목록 (초안)

| 컴포넌트 | 책임 | 타입 |
|---------|------|------|
| [Name] | [한 줄 책임] | [Type] |

총 [N]개 컴포넌트
```

### Step 3: Save LIST artifact and STOP (LIST Mode)

LIST 모드에서는 컴포넌트 목록을 `devflow-docs/inception/application-design.md`에 저장 후 STOP.
**Minimal depth 포함 모든 depth에서 저장 필수** (이후 스킬이 이 파일을 참조).

```markdown
# Application Design

**Mode**: LIST (목록 단계)
**Timestamp**: [ISO 8601]

## 컴포넌트 목록

| 컴포넌트 | 책임 | 타입 |
|---------|------|------|
| [Name] | [한 줄 책임] | [Type] |
```

**session-summary 중간 기록**: LIST 완료 후 session-summary.md의 `## Completed Work`에 `[~] application-design — LIST 완료 ([N]개 컴포넌트)` 업데이트.

→ Return to Orchestrator (목록 반환)

### Step 4: DETAIL Mode — 상세 설계

DETAIL 모드에서만 실행.

**Standard depth**:
각 컴포넌트에 대해:
- **Public interface**: 주요 메서드/API (2-3개)
- **Dependencies**: 의존하는 컴포넌트

**Comprehensive depth**:
각 컴포넌트에 대해:
- **Public interface**: 전체 메서드/API (입력, 출력, 예외)
- **Dependencies**: 의존 컴포넌트 및 방향
- **Data it owns**: 이 컴포넌트가 소유하는 데이터
- **Interactions**: 주요 시퀀스 (ASCII 다이어그램, 기본 ASCII 전용: `+`, `-`, `|`, `^`, `v`, `>`, `<`)

`application-design.md`를 업데이트하여 상세 섹션 추가:
```markdown
## 컴포넌트 상세 설계

### [ComponentName]
**Responsibility**: [한 줄]
**Interface**: [메서드 목록]
**Dependencies**: [의존 컴포넌트]
**Data Owned**: [소유 데이터] (Comprehensive만)
**Interactions**: [ASCII 다이어그램] (Comprehensive만)
```

### Step 5: NFR Design Patterns (오케스트레이터 신호 시)

호출 텍스트에 `NFR Design 포함` 키워드가 있을 때만 실행.
없으면 이 Step을 스킵하고 Review로 진행.

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

## Review

conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/application-design.md
- 리뷰어: artifact-reviewer-prompt.md

**session-summary 중간 기록**: DETAIL 모드에서 각 컴포넌트 상세 설계 완료 시 `[~] application-design — DETAIL [N]/[M] 컴포넌트 완료` 업데이트.

## Return to Orchestrator

conventions 표준 형식. 반환 필드:

**LIST Mode:**
- 설계된 컴포넌트: [count]개
- 목록: [컴포넌트명 나열]
- 산출물: devflow-docs/inception/application-design.md (목록 단계)
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

**DETAIL Mode:**
- 상세 설계 완료: [count]개 컴포넌트
- NFR Design Patterns: [count]개 카테고리 (NFR 신호 시)
- 산출물: devflow-docs/inception/application-design.md (업데이트됨)
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

## Common Issues

### No clear component boundaries
시스템이 단일 컴포넌트로 충분하면:
- 단일 컴포넌트로 설계
- "Single-component system — no decomposition needed" 기록
