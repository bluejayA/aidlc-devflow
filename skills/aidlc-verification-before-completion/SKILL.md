---
name: aidlc-verification-before-completion
description: |
  태스크 완료를 주장하거나, "될 것 같다", 수정 완료를 선언하거나, "테스트 통과"라고 말하기 전에 실제 검증 명령을 실행해야 할 때 사용.
  Use when about to claim a task is complete, say "it should work", declare a fix is done, say "tests pass", or make any success assertion before running the actual verification commands.
metadata:
  version: 0.2.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-no-gate
---

# aidlc-verification-before-completion

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 완료 선언 전 신선한 검증 증거 필수 -->
<!-- TDD 관련 검증은 _shared/tdd-protocol.md 참조 -->

## 철의 법칙

> **NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE**

"통과됩니다", "동작합니다", "수정됐습니다"는 실제 실행 결과를 확인한 후에만 말할 수 있다.
에이전트의 성공 보고, 이전 실행 기억, 코드 리뷰 만으로는 부족하다.

---

### code-generation과의 관계
code-generation이 이미 TDD + code-review를 거친 경우, 추가 수정이 없으면 재검증 불필요.
이 스킬은 code-generation 이후 추가 변경이 있거나, 사용자가 명시적으로 최종 검증을 요청했을 때 사용.

## Trigger

다음 행동을 하려는 순간 이 스킬을 실행한다:

- "완료됐습니다", "구현이 끝났습니다" 등의 완료 선언
- "테스트가 통과합니다", "빌드가 됩니다" 등의 성공 주장
- "이 수정으로 해결됩니다", "이제 동작할 것입니다" 등의 예측형 확신
- 코드 작성 후 커밋/푸시 전
- PR 생성 전
- 사용자에게 "다음 단계로 넘어가도 됩니다"라고 말하기 전

---

## Purpose

실제로 실행하지 않은 코드에 대한 근거 없는 확신을 방지한다.
"아마도 통과할 것"이 아니라 "지금 막 통과했음"만 허용된다.

---

## Red Flags

다음 표현이 나오려 할 때 즉시 멈추고 Gate 프로세스를 실행한다:

| Red Flag 표현 | 왜 위험한가 |
|--------------|-----------|
| "should work" / "아마 될 것 같아요" | 실행하지 않은 코드에 대한 추측 |
| "에이전트가 성공했다고 보고했습니다" | 에이전트 보고 ≠ 실제 검증 |
| "이전에 테스트했을 때 됐어요" | 코드가 바뀌었을 수 있음 |
| "코드를 보니 맞는 것 같습니다" | 코드 리뷰 ≠ 실행 결과 |
| "로컬에서 됐으니 CI도 통과할 거예요" | 환경 차이 무시 |

---

## Gate 프로세스

완료 주장 전에 다음 5단계를 순서대로 수행한다:

### 1단계: 검증 명령 식별

주장 내용에 맞는 검증 명령을 목록화한다:

```
주장: "API 테스트가 통과합니다"
검증 명령:
- [ ] pytest tests/test_api.py -v
- [ ] 빌드: python -m py_compile src/api.py

주장: "리팩토링 후 기능이 동일합니다"
검증 명령:
- [ ] pytest tests/ -v (전체 회귀 테스트)
- [ ] 핵심 시나리오 수동 실행
```

### 2단계: 명령 실행

식별한 모든 명령을 **지금 이 순간** 실행한다.
- 이전 실행 결과를 재사용하지 않는다
- "방금 실행했는데"도 허용되지 않는다 — 코드가 바뀌었을 수 있다

### 3단계: 전체 출력 읽기

명령 출력의 **전체**를 읽는다:
- 마지막 줄 "PASSED" 하나만 보지 않는다
- Warning도 기록한다 (나중에 버그가 될 수 있음)
- Deprecation 메시지도 기록한다
- 출력이 잘렸다면 더 보여달라고 한다

### 4단계: 출력으로 주장 검증

출력이 실제로 주장을 뒷받침하는지 대조한다:

```
주장: "모든 테스트 통과"
출력: "5 passed, 2 warnings"
결과: 통과 ✓ (Warning은 별도 기록)

주장: "빌드 성공"
출력: "ERROR: ModuleNotFoundError: No module named 'pydantic'"
결과: 불통과 ✗ → 완료 선언 불가
```

### 5단계: 완료 선언

4단계 결과가 모두 통과일 때만 완료를 선언한다.

완료 선언 형식:
```
## 검증 완료

실행한 검증:
- `pytest tests/` → 23 passed, 0 failed (2026-03-11 14:32)
- `ruff check src/` → All checks passed

결론: 모든 검증 통과. 완료 선언.
```

### 6단계: 회귀 테스트 RED-GREEN 검증 (버그 수정 시)

`_shared/tdd-protocol.md`의 "회귀 테스트 RED-GREEN 검증" 섹션을 수행한다.

**적용 조건**: systematic-debugging을 거쳐 수정한 경우, 또는 버그 수정 완료 주장 시.
**미적용**: 신규 기능 개발 (code-generation TDD에서 이미 커버).

5단계에서 검증이 모두 통과해도, 버그 수정인 경우 이 단계를 추가로 수행한다.

---

## Examples

### Example 1: 올바른 완료 선언

**상황**: FastAPI 엔드포인트 추가 완료 후 완료 보고 요청

**잘못된 방법** (Red Flag):
```
엔드포인트 구현이 완료됐습니다. 코드를 보면 요구사항을 모두 충족하고 있어요.
테스트도 잘 작성되어 있으니 통과할 것입니다.
```

**올바른 방법** (Gate 프로세스 적용):
```bash
# 1단계: 검증 명령 식별
# - pytest tests/test_endpoints.py -v
# - ruff check src/

# 2단계: 실행
$ pytest tests/test_endpoints.py -v
==================== test session starts ====================
test_create_item PASSED
test_read_item PASSED
test_delete_item PASSED
3 passed in 0.42s

$ ruff check src/
All checks passed.
```

완료 선언:
```
## 검증 완료

실행한 검증:
- `pytest tests/test_endpoints.py -v` → 3 passed, 0 failed
- `ruff check src/` → All checks passed

결론: 모든 검증 통과. 엔드포인트 구현 완료.
```

---

### Example 2: 검증 실패 → 완료 선언 거부

**상황**: 리팩토링 완료 주장 전 Gate 실행

```bash
$ pytest tests/ -v
==================== test session starts ====================
test_user_service.py::test_create_user PASSED
test_user_service.py::test_delete_user FAILED
  AssertionError: Expected 204, got 500
2 passed, 1 failed
```

**처리**:
```
## 검증 실패 — 완료 선언 불가

실행한 검증:
- `pytest tests/` → 2 passed, 1 FAILED

실패한 테스트: test_delete_user
완료 선언을 보류합니다. systematic-debugging 프로세스로 실패 원인 조사를 시작합니다.
```

---

### Example 3: 버그 수정 후 회귀 테스트 검증

**상황**: systematic-debugging으로 버그 수정 완료 → 1~5단계 수행 후 6단계:
회귀 테스트 PASS → `git stash` → 회귀 테스트 FAIL(유효성 증명) → `git stash pop` → 전체 PASS

---

## Troubleshooting

### 검증 명령이 없거나 불명확할 때

**증상**: 어떤 명령으로 검증해야 할지 모름 (새 프로젝트, 문서 부족 등)

**처리 방법**:
1. 프로젝트의 `README`, `Makefile`, `package.json scripts`, `pyproject.toml` 등을 확인한다
2. 표준 검증 명령을 추론한다:
   - Python: `pytest`, `python -m pytest`
   - Node: `npm test`, `yarn test`
   - Go: `go test ./...`
   - Rust: `cargo test`
3. 그래도 없다면 사용자에게 "이 프로젝트의 테스트 실행 방법을 알려주세요"라고 요청한다
4. 검증 방법 없이는 완료 선언을 하지 않는다

---

### 테스트가 너무 오래 걸려서 실행하기 어려울 때

**증상**: 전체 테스트 스위트가 10분 이상 걸림

**처리 방법**:
1. 변경한 코드와 관련된 테스트만 선택적으로 실행한다:
   ```bash
   pytest tests/test_changed_module.py -v
   pytest -k "test_feature_name"
   ```
2. 선택적 테스트 + "전체 테스트는 CI에서 확인 예정"을 함께 명시한다
3. 핵심 경로 테스트만이라도 반드시 실행한다
4. "오래 걸리니 생략하고 완료"는 허용되지 않는다
