---
type: pattern
applies_to: [aidlc-functional-design]
status: active
source: manual
last_validated: 2026-04-13
---

# Three-Mode Selection

오케스트레이터 또는 사용자가 stage/스킬 실행 모드를 선택한다.

## 모드 정의

| 모드 | 트리거 | 동작 |
|------|--------|------|
| **Together** | 기본값. 처음부터 함께 진행 | Step별 순차 실행. 각 Step 사이 Hold 가능 |
| **Import** | 사용자가 기존 문서/결과물 제공 | 문서 검증 → 갭/충돌 피드백 → 확인 |
| **Skip** | 사용자가 명시적 스킵 요청 | devflow-state에 SKIPPED 기록 후 다음 단계 |

## 오케스트레이터 규칙

- 모드 선택은 오케스트레이터가 게이트로 제시
- stage skill은 선택된 모드만 실행 (모드 선택 로직 포함 금지)
- Import 모드에서도 Review는 필수 (conventions Review Workflow 참조)

## Together 모드 상세

- Step별 산출물 제시 → 사용자 확인 후 다음 Step
- Hold 시그널 수신 시 → `hold-mechanism.md` 참조
- 옵션 제시 형식: "A안은... B안은..." (Claude는 옵션 제시자)

## Import 모드 상세

- 사용자 제공 파일/내용 수신
- 검증: 갭(누락), 충돌(모순), 적합성(현재 컨텍스트)
- 검증 결과 피드백 → 사용자 확인 → 완료
