---
name: aidlc-test-driven-development
description: |
  프로덕션 코드 작성, 버그 수정, 리팩토링 시 사용 — 예외 없이 RED-GREEN-REFACTOR 사이클을 강제.
  Use when writing any production code, fixing bugs, or refactoring — enforces RED-GREEN-REFACTOR cycle with no exceptions.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
  skill_nature: compensation
  lifecycle: active
  model_dependency: "모델이 자발적으로 실패 테스트를 먼저 작성하지 않음"
---

# Test-Driven Development

<!-- 출력 언어: 한국어 (Korean) -->

> **Skill Type: Rigid** — 정확히 따를 것. 상황에 맞게 적응하지 않는다.

> **Iron Law**: `_shared/devflow-conventions.md` TDD Iron Law 참조. 실패하는 테스트 없이 프로덕션 코드 작성 금지.

**시작 시 선언**: "aidlc-test-driven-development 스킬을 사용합니다. TDD Iron Law를 적용합니다."

## RED-GREEN-REFACTOR

`_shared/tdd-protocol.md` 참조. 아래는 요약:

### RED: 실패하는 테스트 작성

- 한 가지 동작만 테스트
- 명확한 이름 (테스트가 문서 역할)
- 실제 코드 사용 (모킹 최소화)

### Verify RED (필수)

- 테스트가 실패해야 함
- 실패 이유가 "기능 부재"여야 함 (오타, 구문 에러 아님)
- 실패 메시지 확인

### GREEN: 최소 구현

- 테스트를 통과시키는 가장 간단한 코드
- YAGNI — 요청되지 않은 기능 금지
- "나중에 필요할 것 같다"는 합리화

### Verify GREEN (필수)

- 해당 테스트 통과
- 기존 테스트 모두 통과
- 에러/경고 없음

### REFACTOR: 코드 정리

- 중복 제거
- 이름 개선
- 헬퍼 추출
- **테스트는 계속 통과해야 함**

## When to Use

**항상 사용** — 이것이 기본값. 아래 예외 외에는 예외 없음.

## Exceptions (사용자 명시적 승인 필요)

- Throwaway 프로토타입 (사용 후 삭제 확인)
- 설정 파일 변경 (로직 없음)
- 자동 생성 코드 (생성기를 테스트)

예외를 적용하려면 사용자가 명시적으로 "TDD 스킵"을 승인해야 한다.

## 합리화 방지 + Red Flags

`_shared/tdd-protocol.md` "합리화 방지" 및 "Red Flags" 섹션 참조.

핵심만 발췌:
- 코드 먼저 작성했으면 → **삭제하고 처음부터**
- 테스트가 즉시 통과하면 → 기존 동작 테스트 중이거나 잘못된 테스트
- "나중에 테스트 추가"는 → 나중은 오지 않음

## Self-Review

구현 완료 후, 리뷰어에게 보내기 전 self-review:

- [ ] 모든 프로덕션 코드에 실패 테스트가 먼저 있었는가?
- [ ] RED 확인을 매번 했는가?
- [ ] GREEN에서 최소 구현만 했는가?
- [ ] REFACTOR 후 테스트가 모두 통과하는가?
- [ ] 합리화를 하지 않았는가?

## 예시: API 엔드포인트 추가

```
1. RED: GET /api/users 테스트 — 404 예상
   → 실행 → FAIL (라우트 없음) ✓
2. GREEN: 라우트 + 빈 배열 반환
   → 실행 → PASS ✓
3. RED: 사용자 있을 때 반환 테스트
   → 실행 → FAIL (DB 조회 없음) ✓
4. GREEN: DB 조회 + 반환
   → 실행 → PASS ✓
5. REFACTOR: 쿼리 로직 분리
   → 실행 → PASS ✓
6. 커밋
```

## Integration

- **사용하는 스킬**: `aidlc-code-generation`, `aidlc-subagent-driven-development`, `aidlc-executing-plans`
- **참조 문서**: `_shared/tdd-protocol.md`, `_shared/devflow-conventions.md`
