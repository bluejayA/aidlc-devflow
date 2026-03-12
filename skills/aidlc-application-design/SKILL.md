---
name: aidlc-application-design
description: aidlc 플러그인(B안) 전용 스킬. Designs component and service structure before implementation. Conditional Construction stage. Called by aidlc:aidlc-using-devflow orchestrator.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/application-design.md
---

# aidlc-application-design

<!-- 애플리케이션 설계: 신규 컴포넌트/서비스 구조 설계 -->
<!-- B안: 실행 전용, 조건부 — 오케스트레이터가 workflow-plan 기반으로 호출 여부 결정 -->

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

## Return to Orchestrator

STOP here. No approval gate — orchestrator handles it.

**LIST Mode 반환:**
```
[application-design 결과 — LIST]
- 설계된 컴포넌트: [count]개
- 목록: [컴포넌트명 나열]
- 산출물: devflow-docs/inception/application-design.md (목록 단계)
※ Minimal depth: 오케스트레이터가 DETAIL 호출 없이 바로 다음 단계 진행
※ Standard/Comprehensive: 오케스트레이터가 목록 승인 후 DETAIL 호출
```

**DETAIL Mode 반환:**
```
[application-design 결과 — DETAIL]
- 상세 설계 완료: [count]개 컴포넌트
- 산출물: devflow-docs/inception/application-design.md (업데이트됨)
```

## Common Issues

### requirements.md not found
If `devflow-docs/inception/requirements.md` does not exist:
- Display: "⚠️ requirements.md를 찾을 수 없습니다. 사용자 요청 컨텍스트만으로 설계를 진행합니다."
- Proceed based on available conversation context

### No clear component boundaries
If the system is too simple to decompose:
- Design as a single component
- Note: "Single-component system — no decomposition needed"
