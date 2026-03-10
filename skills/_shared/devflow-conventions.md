---
name: devflow-conventions
description: Shared conventions for all AI-DLC stage skills. Defines invoke_mode and return_behavior metadata semantics.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
---

# devflow Conventions

## YAML 메타데이터 규약

### invoke_mode: orchestrator-only

이 값을 가진 스킬은 **사용자가 직접 호출하면 안 됩니다**.
`using-devflow` 오케스트레이터만 호출합니다.

직접 호출 시 응답:
> "이 스킬은 using-devflow 오케스트레이터를 통해 자동으로 호출됩니다. `devflow:using-devflow`를 시작해주세요."

### return_behavior: stop-no-gate

이 값을 가진 스킬은 **Return to Orchestrator 프로토콜**을 따릅니다:

1. 스테이지 로직 실행
2. 산출물 저장
3. 결과 요약 표시 (각 스킬의 `## Return to Orchestrator` 섹션 형식 사용)
4. **STOP** — A/B 승인 게이트 절대 표시 금지

승인 게이트와 상태 업데이트는 `using-devflow` 오케스트레이터가 전담합니다.

## 공통 이슈 처리

### 입력 산출물 파일 없음

필요한 입력 파일(예: `requirements.md`, `workspace.md`)이 없을 때:
- 진행 가능한 컨텍스트로 계속 진행
- 파일 참조 위치에 메모: `"⚠️ [filename]를 찾을 수 없습니다. 가용한 컨텍스트로 진행합니다."`
