---
type: pattern
applies_to: []
status: active
source: manual
last_validated: 2026-04-13
---

# Hold Mechanism

진행 중 사용자가 일시 중단을 요청할 때의 처리 규약.

## Hold 시그널

사용자가 "잠깐", "Hold", "멈춰" 등으로 중단 요청 시 발동.

## Hold 처리 절차

1. 현재 Step까지의 산출물을 파일에 저장
2. 산출물 파일에 상태 마커 추가:
   ```markdown
   ## Status: partial — [미완료 항목 목록]
   ```
3. devflow-state에는 Completed/Skipped에 기록하지 않음 (incomplete 상태)
4. devflow-audit에 Hold 이벤트 로깅

## Resume 절차

1. 세션 재개 시 산출물 파일의 `Status: partial` 마커 탐지
2. 미완료 항목 목록 표시 → 사용자에게 계속 진행 여부 확인
3. 승인 시 중단 지점부터 재개
4. devflow-audit에 Resume 이벤트 로깅

## 적용 범위

- Together 모드의 모든 Step 사이
- Import 모드의 검증 단계
- 오케스트레이터의 게이트 대기 중

> Three-Mode Selection에서 Together 모드 진행 중 Hold 발생 시 이 메커니즘 적용. `three-mode-selection.md` 참조.
