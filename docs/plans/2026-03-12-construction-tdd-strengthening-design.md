# Construction TDD 강화 설계

> Superpowers 비교 분석 기반 AIDLC Construction 단계 개선

**Complexity:** Comprehensive

**Goal:** Construction 단계에 TDD Iron Law, 실행 기반 검증, 테스트 리뷰 강화를 도입하여 코드 품질 보증 체계를 완성한다.

**Architecture:** `_shared/tdd-protocol.md`에 TDD 규약을 중앙 정의하고, 각 Construction 스킬이 자기 역할에 맞게 참조하는 Hybrid 접근법. 오케스트레이터는 경량 유지.

**Tech Stack:** SKILL.md (Markdown), 기존 AIDLC 플러그인 아키텍처

---

## Design Decisions

### DD-1: build-and-test 역할 재정의 (Option C 채택)

**결정**: code-generation이 unit별 TDD 사이클 담당, build-and-test는 전체 통합 테스트/회귀 테스트 실행 + 지침 문서 생성 전담.

**근거**:
- TDD의 RED-GREEN-REFACTOR는 코드 작성과 동일 스킬 내에서 수행되어야 자연스러운 반복이 가능
- build-and-test를 삭제(A)하면 통합 테스트 전담 스킬이 사라짐
- 실행 변환(B)은 TDD 반복을 스킬 경계로 끊어 비효율
- 5 unit 시나리오에서 토큰 효율 최적 (C: ~1120줄 vs A/B: ~1500줄)

**기각된 대안**:
- A) code-generation에 통합: 스킬 비대화 위험 (549줄 모놀리스 재발)
- B) 실행 변환: TDD 사이클이 스킬 간 핑퐁으로 끊김

### DD-2: TDD Iron Law 위반 처리 (Option A 채택)

**결정**: Superpowers 동일 수준 — Iron Law + 위반 시 코드 삭제 후 RED부터 재시작. 참조용 보관 금지.

**근거**:
- AIDLC는 프로덕션 코드를 만드는 워크플로우
- "이번만 예외"가 습관이 되는 것을 방지
- 예외는 사용자 명시적 승인 필요 (throwaway prototype, 설정 파일 등)

### DD-3: TDD 서브에이전트 구조 (구조 3 채택)

**결정**: 단일 에이전트가 TDD 전체 수행 + 별도 리뷰어가 테스트 품질 검증.

**근거**:
- TDD는 본질적으로 반복적(iterative) 프로세스 — RED/GREEN 분리 서브에이전트(구조 2)는 매 사이클마다 컨텍스트 전달 필요, 분리의 의미 퇴색
- 구조 2는 5개 함수 unit에서 10회+ 서브에이전트 핑퐁 → 토큰 8-12x 증가
- 제3자 검증의 실질적 가치는 **리뷰**(완성물 검증)에서 발생, 작성 분리에서는 아님
- 구조 3: 자연스러운 TDD 흐름 + 리뷰어의 독립적 테스트 품질 검증 = 최적 균형

**기각된 대안**:
- 구조 1 (단일 에이전트, 리뷰 없음): 제3자 테스트 검증 부재
- 구조 2 (RED/GREEN 분리): 토큰 비용 8-12x, 오케스트레이터 핑퐁 복잡도

### DD-4: 코드 리뷰어 분리 여부 (Option B 채택)

**결정**: 현재 통합 유지 (1개 서브에이전트가 Spec + Quality 2단계 수행) + 테스트 리뷰 항목 강화.

**근거**:
- 분리하면 매 unit마다 서브에이전트 2회 dispatch (컨텍스트 중복 로딩)
- 3-tier 체인에서 서브에이전트 수 증가 → construction-orchestrator 게이트 관리 복잡화
- "Stage 1 통과 후에만 Stage 2 진행" 규칙이 이미 있으므로 분리와 같은 효과
- 테스트 리뷰는 Stage 2 내 항목 확장으로 충분

### DD-5: TDD 컨벤션 중앙화 (접근법 B 채택)

**결정**: `_shared/tdd-protocol.md`에 TDD 규약을 중앙 정의, 각 스킬이 참조.

**근거**:
- TDD Iron Law가 3개 스킬(code-generation, verification, debugging)에서 참조됨 → DRY
- 기존 `_shared/gate-patterns.md`, `_shared/reviewers/` 패턴과 일관
- 오케스트레이터 경량 유지 (접근법 C 기각)
- 규칙 변경 시 1곳만 수정

---

## 변경 상세

### 1. 신규: `_shared/tdd-protocol.md` (~80줄)

TDD의 Single Source of Truth. code-generation, verification-before-completion, systematic-debugging, code-reviewer가 참조.

#### 구성

```
# TDD Protocol

## Iron Law
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
위반 시: 해당 코드 삭제 후 RED부터 재시작. 참조용 보관 금지.

## RED-GREEN-REFACTOR 사이클

### RED — 실패 테스트 작성
- 하나의 행위만 테스트
- 명확한 테스트 이름
- 실제 코드 사용 (mock 최소화)

### Verify RED — 실패 확인 (필수, 스킵 불가)
- 테스트 실행 → 실패 확인
- 실패 이유가 "기능 미구현"이어야 함 (오타/에러 아님)
- 테스트가 즉시 통과하면 → 기존 동작을 테스트 중. 테스트 수정.

### GREEN — 최소 구현
- 테스트를 통과하는 최소한의 코드만 작성
- YAGNI: 옵션, 설정, 확장 포인트 추가 금지

### Verify GREEN — 통과 확인 (필수)
- 해당 테스트 통과 확인
- 기존 전체 테스트도 통과 확인 (회귀 방지)
- Warning/Deprecation도 기록

### REFACTOR — 정리
- GREEN 확인 후에만 수행
- 중복 제거, 이름 개선, 헬퍼 추출
- 리팩토링 후 전체 테스트 재실행

## 예외 (사용자 명시적 승인 필요)
- Throwaway prototype
- 설정 파일 (config, yaml)
- 자동 생성 코드

## Red Flags — 즉시 삭제 후 재시작
- 테스트 전에 코드 작성
- 테스트가 즉시 통과
- "이번만 예외"
- "참조용으로 보관"
- "테스트 나중에 추가"

## Self-Review 체크리스트
구현 완료 후, 리뷰어에게 넘기기 전 자가 점검.
(이 체크리스트는 정식 코드 리뷰 전 pre-flight check이다. 명백한 이슈를 미리 잡아 리뷰 루프 횟수를 줄인다.)

### 완전성
- [ ] 스펙의 모든 요구사항 구현했는가
- [ ] 누락된 엣지케이스가 없는가

### 품질
- [ ] 이름이 명확하고 정확한가
- [ ] 코드가 깨끗하고 유지보수 가능한가

### 규율
- [ ] YAGNI 위반 없는가 (요청되지 않은 기능 추가하지 않았는가)
- [ ] 기존 코드베이스 패턴을 따랐는가

### 테스트
- [ ] 모든 테스트가 실제 행위를 검증하는가 (mock 남용 아닌가)
- [ ] 각 테스트의 RED를 확인했는가
- [ ] 전체 테스트 스위트가 통과하는가

## 회귀 테스트 RED-GREEN 검증

버그 수정 완료 시, 회귀 테스트가 진짜 버그를 잡는지 증명한다.

적용 조건: systematic-debugging을 거쳐 수정한 경우, 또는 버그 수정 완료 주장 시.
미적용: 신규 기능 개발 (code-generation TDD에서 이미 커버)

프로세스:
1. 회귀 테스트 실행 → PASS 확인
2. 수정 되돌리기 (git stash 또는 수동)
3. 회귀 테스트 실행 → MUST FAIL
   - FAIL이면: 테스트가 유효함 증명
   - PASS이면: ⚠️ 테스트가 버그를 잡지 못함. 테스트 재작성 필요.
4. 수정 복원 (git stash pop)
5. 회귀 테스트 + 전체 테스트 실행 → 전체 PASS 확인

검증 완료 형식:
  ## 회귀 테스트 검증
  - 회귀 테스트: test_xxx
  - 수정 적용 시: PASS ✓
  - 수정 되돌림 시: FAIL ✓ (테스트 유효성 증명)
  - 수정 복원 후: 전체 PASS ✓
  결론: 회귀 테스트 유효. 완료 선언.
```

---

### 2. 수정: `aidlc-code-generation/SKILL.md` (151 → ~200줄)

#### 2-1. PART 1 (Plan) — Implementation Steps 형식 변경

각 Step이 TDD 사이클을 명시:

```markdown
## Implementation Steps
- [ ] Step 1: [기능명]
  - [ ] RED: [테스트명] 작성
  - [ ] Verify RED: 실패 확인
  - [ ] GREEN: [구현 내용]
  - [ ] Verify GREEN: 통과 확인 + 전체 회귀
  - [ ] REFACTOR: [정리 대상이 있으면 명시, 없으면 생략]
- [ ] Step 2: [기능명]
  - [ ] RED: ...
  ...
```

#### 2-2. PART 2 (Generate) — TDD 프로토콜 적용

현재 "Follow TDD" 1줄을 다음으로 교체:

```
1. `_shared/tdd-protocol.md` 읽기
2. 각 Implementation Step에 대해 TDD 사이클 실행:
   a. RED: 실패 테스트 작성 → 실행 → 실패 확인
   b. GREEN: 최소 구현 → 실행 → 해당 테스트 + 전체 테스트 통과 확인
   c. REFACTOR: 정리 → 전체 테스트 재실행
   d. 체크박스 [x] 표시 (하위 RED/GREEN 포함)
3. Iron Law 위반 시: 해당 코드 삭제 후 RED부터 재시작
4. 모든 Step 완료 후 Self-Review 체크리스트 수행 (tdd-protocol.md 참조)
5. 자가 수정 후 Save plan progress
```

#### 2-3. Return 형식 강화

PART 2 Return에 테스트 정보 + Self-Review 상태 추가:

```
[code-generation 완료: unit-name]
- 생성된 파일: [count]개
- 테스트: [count]개 통과, 0 실패
- TDD 사이클: [count]회 완료
- Self-Review: ✅ 완료
- 모든 체크박스 완료
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

#### 2-4. Example 업데이트

Example 2(PART 2)를 TDD 사이클이 보이도록 변경:

```
1. Step 1 실행:
   - RED: test_create_notification_success 작성 → 실행 → FAIL ✓
   - GREEN: create_notification() 구현 → 실행 → PASS ✓ (전체 1/1)
   - [x] Step 1 완료
2. Step 2 실행:
   - RED: test_create_notification_invalid_user 작성 → 실행 → FAIL ✓
   - GREEN: 유효성 검증 추가 → 실행 → PASS ✓ (전체 2/2)
   - [x] Step 2 완료
3. Self-Review 수행 → 이슈 없음
```

---

### 3. 전면 재작성: `aidlc-build-and-test/SKILL.md` (97 → ~120줄)

#### 3-1. Purpose + Frontmatter 변경

**description**: `Execute build and full test suite after all units are implemented, then generate reference instructions. Called by aidlc-construction-orchestrator.`

**purpose**: `Generate comprehensive build and test instructions` → `Execute build and full test suite after all units are implemented, then generate reference instructions.`

`return_behavior`는 `stop-no-gate` 유지 — 결과(성공/실패)를 Return하고 오케스트레이터가 조건부 게이트를 제시하는 현재 패턴과 일치.

#### 3-2. 실행 프로세스 (4단계)

```
### Step 1: 프로젝트 분석 (현재와 동일)
빌드 설정 파일, 소스 파일, code-plan 분석

### Step 2: 빌드 실행
1. 빌드 명령 결정 (프로젝트 타입별 자동 감지)
2. 빌드 실행
3. 결과 확인:
   - 성공 → Step 3으로
   - 실패 → 에러 메시지 포함하여 Return (오케스트레이터가 처리)

### Step 3: 전체 테스트 스위트 실행
1. 테스트 명령 결정 (프로젝트 타입별 자동 감지)
2. 전체 테스트 실행 (unit + 통합 포함)
3. 결과 파싱:
   - 전체 통과 → Step 4로
   - 실패 있음 → 실패 테스트 목록 포함하여 Return
     "⚠️ [N]개 테스트 실패. systematic-debugging 권장."

### Step 4: 지침 문서 생성
build-instructions.md + test-instructions.md 생성 (현재와 동일한 형식)
```

#### 3-3. Return 형식 변경

```
[build-and-test 결과]
- 빌드: ✅ 성공 | ❌ 실패 ([에러 요약])
- 테스트: ✅ [N]개 통과, 0 실패 | ❌ [N]개 통과, [M]개 실패
- 산출물:
  - devflow-docs/construction/build-and-test/build-instructions.md
  - devflow-docs/construction/build-and-test/test-instructions.md
```

#### 3-4. Error Handling

```
빌드 실패 시: 오케스트레이터에 Return. 빌드 실패는 무시 불가.
테스트 실패 시: 오케스트레이터에 Return. 오케스트레이터가 선택지 제시.
빌드 명령 불명 시: 파일 확장자 기반 추론 (현재 Common Issues 유지)
```

---

### 4. 수정: `aidlc-construction-orchestrator/SKILL.md` (135 → ~155줄)

#### 4-1. build-and-test 게이트 → 조건부 게이트로 변경

```
#### 완료 게이트 [조건부 게이트]

빌드 성공 + 테스트 전체 통과 시:
  A) CONSTRUCTION 완료 승인
  B) 추가 수정 요청 → code-generation 재호출

테스트 실패 시:
  A) systematic-debugging으로 조사
  B) 실패를 무시하고 완료 (devflow-state에 "테스트 실패 [N]건 미해결" 기록)

빌드 실패 시:
  A) systematic-debugging으로 조사
  (빌드 실패는 완료 불가 — B 선택지 없음)
```

#### 4-2. Debugging 라우팅 추가

```
### Debugging 라우팅

build-and-test에서 테스트/빌드 실패 시 사용자가 debugging을 선택하면:
1. aidlc-systematic-debugging 호출
2. debugging 완료 시 Return 형식:
   [systematic-debugging 완료]
   - 근본 원인: [요약]
   - 수정 내용: [요약]
   - 테스트: [회귀 테스트명] 추가됨
3. debugging Return 수신 후 build-and-test 재실행
```

**참고**: systematic-debugging은 현재 `return_behavior` 메타데이터가 없다. 이번 변경에서 Return 형식을 추가한다 (섹션 6 참조).

#### 4-3. gate-patterns.md

`_shared/gate-patterns.md`의 기존 "조건부 게이트" 정의가 이미 "반환값 패턴에 따라 선택지 분기"를 커버한다. 빌드 실패 시 "B 선택지 없음"은 조건부 게이트의 자연스러운 변형이므로 gate-patterns.md 수정 불필요.

#### 4-4. 변경하지 않는 것

- units-generation 게이트, code-generation 게이트, 스테이지 순서, Audit Logging: 모두 변경 없음

---

### 5. 수정: `aidlc-verification-before-completion/SKILL.md` (225 → ~235줄)

#### 5-1. 6단계 추가 (tdd-protocol 참조)

기존 5단계 뒤에 추가:

```
### 6단계: 회귀 테스트 RED-GREEN 검증 (버그 수정 시)
`_shared/tdd-protocol.md`의 "회귀 테스트 RED-GREEN 검증" 섹션을 수행한다.
적용 조건: systematic-debugging을 거쳐 수정한 경우, 또는 버그 수정 완료 주장 시.
미적용: 신규 기능 개발 (code-generation TDD에서 이미 커버).
```

#### 5-2. 상단 참조 추가

```
<!-- TDD 관련 검증은 _shared/tdd-protocol.md 참조 -->
```

#### 5-3. Example 3 추가 — 회귀 테스트 검증 예시

```
### Example 3: 버그 수정 후 회귀 테스트 검증

**상황**: systematic-debugging으로 이메일 검증 버그 수정 완료

**6단계 수행**:
1. 회귀 테스트 실행:
   $ pytest tests/test_email.py::test_validate_io_tld -v → PASS ✓
2. 수정 되돌리기:
   $ git stash
3. 회귀 테스트 실행:
   $ pytest tests/test_email.py::test_validate_io_tld -v → FAIL ✓
   (테스트가 버그를 잡음을 증명)
4. 수정 복원:
   $ git stash pop
5. 전체 테스트:
   $ pytest tests/ -v → 24 passed, 0 failed ✓

## 회귀 테스트 검증
- 회귀 테스트: test_validate_io_tld
- 수정 적용 시: PASS ✓
- 수정 되돌림 시: FAIL ✓ (테스트 유효성 증명)
- 수정 복원 후: 전체 PASS ✓
결론: 회귀 테스트 유효. 완료 선언.
```

---

### 6. 수정: `aidlc-systematic-debugging/SKILL.md` (257 → ~275줄)

#### 6-1. 4단계 4번 항목 — 실패 이력 분석 강화

선택지 제시 전 **실패 이력 요약 + 공통 패턴 식별**을 강제:

```
### 실패 이력 요약
| 시도 | 가설 | 수정 내용 | 결과 | 왜 실패했는가 |
|------|------|----------|------|-------------|
| 1회  |      |          |      |             |
| 2회  |      |          |      |             |
| 3회  |      |          |      |             |

### 공통 패턴 식별
- 3번의 가설이 모두 같은 영역을 겨냥했는가? → 다른 영역 탐색 필요
- 수정이 매번 다른 테스트를 깨뜨렸는가? → 설계 결합도 문제
- 근본 원인을 찾지 못한 채 증상만 수정했는가? → 1단계 재현으로 복귀

### 분석 후 선택지 제시
A/B/C (기존과 동일)
```

#### 6-2. Return 형식 추가

현재 systematic-debugging에는 Return 형식이 정의되어 있지 않다. construction-orchestrator의 debugging 라우팅을 위해 추가:

```
## Return to Orchestrator

STOP. 수정 완료 후 아래 형식으로 반환:

[systematic-debugging 완료]
- 근본 원인: [1줄 요약]
- 수정 내용: [1줄 요약]
- 테스트: [회귀 테스트명] 추가됨
- 전체 테스트: [N]개 통과, 0 실패
```

Frontmatter에 `return_behavior: stop-no-gate` 추가.

#### 6-3. tdd-protocol 참조 추가

4단계 구현 섹션(RED-GREEN)에: `<!-- TDD RED-GREEN 프로세스 상세: _shared/tdd-protocol.md 참조 -->`

#### 6-4. aidlc-receiving-code-review 참조

4단계 선택지 B) `aidlc-receiving-code-review 스킬로 피드백을 구한다`는 그대로 유지. 해당 스킬은 이번 변경 범위 밖이며 영향 없음.

---

### 7. 수정: 리뷰어 프롬프트

#### 7-1. `code-reviewer-prompt.md` (73 → ~80줄)

Stage 2 Code Quality 테스트 항목 확장:

```
| **테스트: 행위 검증** | 테스트가 실제 행위를 검증하는가 (mock이 아닌 실제 코드) |
| **테스트: TDD 준수** | 각 기능에 대응하는 테스트가 존재하는가, RED-GREEN 흔적이 보이는가 |
| **테스트: 엣지케이스** | 정상 경로만 테스트하지 않았는가, 실패/경계 케이스 포함 여부 |
| **테스트: 회귀 안전성** | 기존 테스트 유지 여부, 삭제/변경된 테스트의 타당성 |
```

#### 7-2. `code-plan-reviewer-prompt.md` (39 → ~42줄)

TDD 확인 항목 추가:

```
| **TDD 사이클** | 각 Implementation Step이 RED-GREEN-REFACTOR 하위 단계를 포함하는가 |
```

---

### 8. 수정: `_shared/devflow-conventions.md` (101 → ~110줄)

TDD 규약 섹션 추가:

```
### TDD 규약
- `_shared/tdd-protocol.md` — TDD Iron Law, RED-GREEN-REFACTOR, Self-Review 체크리스트
- Construction 스킬 중 코드를 작성/수정하는 스킬은 이 프로토콜을 참조
```

---

### 9. 버전 업데이트

| 파일 | 현재 | 변경 |
|------|------|------|
| code-generation | 0.4.0 | 0.5.0 |
| build-and-test | 0.3.0 | 0.5.0 (0.4.0 스킵 — Construction 스킬 버전 정렬) |
| verification-before-completion | 0.1.0 | 0.2.0 |
| systematic-debugging | 0.1.0 | 0.2.0 |
| construction-orchestrator | 0.4.0 | 0.5.0 |
| devflow-conventions.md | 0.1.0 | 0.2.0 |
| plugin.json | 0.4.0 | 0.5.0 |

---

## 변경 파일 총 정리

| 파일 | 변경 유형 | 크기 변화 |
|------|----------|----------|
| `_shared/tdd-protocol.md` | **신규** | ~80줄 |
| `aidlc-code-generation/SKILL.md` | 수정 | 151 → ~200줄 |
| `aidlc-build-and-test/SKILL.md` | **전면 재작성** | 97 → ~120줄 |
| `aidlc-construction-orchestrator/SKILL.md` | 수정 | 135 → ~155줄 |
| `aidlc-verification-before-completion/SKILL.md` | 수정 | 225 → ~235줄 |
| `aidlc-systematic-debugging/SKILL.md` | 수정 | 257 → ~285줄 |
| `_shared/reviewers/code-reviewer-prompt.md` | 수정 | 73 → ~80줄 |
| `_shared/reviewers/code-plan-reviewer-prompt.md` | 수정 | 39 → ~42줄 |
| `_shared/devflow-conventions.md` | 수정 | 101 → ~110줄 |
| `.claude-plugin/plugin.json` | 수정 | 버전만 |

총 10개 파일, 신규 1개 + 전면 재작성 1개 + 수정 8개. 순증 약 +160줄.
