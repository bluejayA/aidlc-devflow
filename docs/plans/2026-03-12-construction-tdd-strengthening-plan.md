# Construction TDD 강화 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construction 단계에 TDD Iron Law, 실행 기반 검증, 테스트 리뷰 강화를 도입하여 코드 품질 보증 체계를 완성한다.

**Complexity:** Comprehensive

**Architecture:** `_shared/tdd-protocol.md`에 TDD 규약을 중앙 정의하고, 각 Construction 스킬이 자기 역할에 맞게 참조하는 Hybrid 접근법. 오케스트레이터는 경량 유지. 모든 변경은 SKILL.md (Markdown) 파일 대상이므로 TDD 사이클이 아닌 스펙 대조 검증으로 확인한다.

**Tech Stack:** SKILL.md (Markdown), AIDLC 플러그인 아키텍처

**Spec:** `docs/plans/2026-03-12-construction-tdd-strengthening-design.md`

---

## File Structure

| 파일 | 역할 | 변경 유형 |
|------|------|----------|
| `skills/_shared/tdd-protocol.md` | TDD Iron Law + RED-GREEN-REFACTOR + Self-Review + 회귀 테스트 검증의 Single Source of Truth | **신규** |
| `skills/_shared/devflow-conventions.md` | 아키텍처 가이드에 TDD 규약 섹션 추가 | 수정 |
| `skills/aidlc-code-generation/SKILL.md` | PART 1 TDD 단계 명시 + PART 2 TDD 프로토콜 적용 + Self-Review + Return 강화 | 수정 |
| `skills/_shared/reviewers/code-plan-reviewer-prompt.md` | TDD 사이클 확인 항목 추가 | 수정 |
| `skills/_shared/reviewers/code-reviewer-prompt.md` | 테스트 리뷰 항목 4개로 확장 | 수정 |
| `skills/aidlc-build-and-test/SKILL.md` | 지침 생성 → 실행+지침 생성으로 전면 재작성 | **재작성** |
| `skills/aidlc-construction-orchestrator/SKILL.md` | 완료 게이트 조건부 변경 + Debugging 라우팅 추가 | 수정 |
| `skills/aidlc-verification-before-completion/SKILL.md` | 6단계 회귀 테스트 검증 추가 + Example 3 | 수정 |
| `skills/aidlc-systematic-debugging/SKILL.md` | 실패 이력 분석 강화 + Return 형식 추가 | 수정 |
| `.claude-plugin/plugin.json` | 0.4.0 → 0.5.0 | 수정 |

---

## Chunk 1: Foundation

### Task 1: Create `_shared/tdd-protocol.md`

**Files:**
- Create: `skills/_shared/tdd-protocol.md`

**Context:** 모든 Construction 스킬이 참조할 TDD 규약의 중앙 정의. 스펙 섹션 1의 내용을 그대로 파일로 작성한다.

- [ ] **Step 1: 파일 생성**

`skills/_shared/tdd-protocol.md` 생성. 내용:

```markdown
# TDD Protocol

<!-- TDD 규약의 Single Source of Truth. code-generation, verification-before-completion, systematic-debugging, code-reviewer가 참조한다. -->

## Iron Law

> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

위반 시: 해당 코드 삭제 후 RED부터 재시작. 참조용 보관 금지.

- 삭제한 코드를 "참고"하지 않는다
- "이미 작성한 것을 활용"하지 않는다
- 테스트부터 새로 시작한다

---

## RED-GREEN-REFACTOR 사이클

### RED — 실패 테스트 작성

- 하나의 행위만 테스트
- 명확한 테스트 이름 (행위를 설명)
- 실제 코드 사용 (mock은 외부 의존성에만, 최소화)

### Verify RED — 실패 확인 (필수, 스킵 불가)

테스트를 실행하고 **실패**를 확인한다.

- 실패 이유가 "기능 미구현"이어야 함 (오타, import 에러가 아님)
- 테스트가 즉시 통과하면 → 기존 동작을 테스트 중. 테스트를 수정한다.
- 테스트가 에러로 실패하면 → 에러를 수정하고 다시 실행한다. 올바른 실패를 확인할 때까지.

### GREEN — 최소 구현

테스트를 통과하는 **최소한의** 코드만 작성한다.

- YAGNI: 옵션, 설정, 확장 포인트 추가 금지
- "나중에 필요할 것 같은" 코드를 미리 작성하지 않는다
- 테스트가 요구하는 것만 구현한다

### Verify GREEN — 통과 확인 (필수)

- 해당 테스트 통과 확인
- **기존 전체 테스트도 통과 확인** (회귀 방지)
- Warning/Deprecation도 기록한다 (나중에 버그가 될 수 있음)
- 다른 테스트가 깨졌으면 → 지금 수정한다 (다음으로 미루지 않는다)

### REFACTOR — 정리

GREEN 확인 후에만 수행한다.

- 중복 제거, 이름 개선, 헬퍼 추출
- 리팩토링 후 **전체 테스트 재실행** — 여전히 GREEN이어야 한다
- 새로운 행위를 추가하지 않는다 (그건 다음 RED에서)

---

## 예외 (사용자 명시적 승인 필요)

다음은 TDD 없이 진행할 수 있으나, **사용자가 명시적으로 승인**해야 한다:

- Throwaway prototype (버릴 코드)
- 설정 파일 (config, yaml, 환경 설정)
- 자동 생성 코드 (코드젠, 스캐폴딩)

---

## Red Flags — 즉시 삭제 후 재시작

아래 상황이 발생하면 **해당 코드를 삭제하고 RED부터 재시작**한다:

- 테스트 전에 프로덕션 코드를 작성함
- 테스트가 즉시 통과함 (RED 없이 GREEN)
- "이번만 예외"라고 합리화함
- "참조용으로 보관"하려 함
- "테스트는 나중에 추가"하려 함
- "이미 수동으로 테스트했으니 괜찮다"고 주장함
- "TDD는 교조적이다, 실용적으로 가자"고 합리화함

---

## Self-Review 체크리스트

구현 완료 후, 리뷰어에게 넘기기 전 자가 점검.
(이 체크리스트는 정식 코드 리뷰 전 pre-flight check이다. 명백한 이슈를 미리 잡아 리뷰 루프 횟수를 줄인다.)

### 완전성
- [ ] 스펙의 모든 요구사항을 구현했는가
- [ ] 누락된 엣지케이스가 없는가

### 품질
- [ ] 이름이 명확하고 정확한가
- [ ] 코드가 깨끗하고 유지보수 가능한가

### 규율
- [ ] YAGNI 위반 없는가 (요청되지 않은 기능을 추가하지 않았는가)
- [ ] 기존 코드베이스 패턴을 따랐는가

### 테스트
- [ ] 모든 테스트가 실제 행위를 검증하는가 (mock 남용이 아닌가)
- [ ] 각 테스트의 RED를 확인했는가
- [ ] 전체 테스트 스위트가 통과하는가

---

## 회귀 테스트 RED-GREEN 검증

버그 수정 완료 시, 회귀 테스트가 진짜 버그를 잡는지 증명한다.

**적용 조건**: systematic-debugging을 거쳐 수정한 경우, 또는 버그 수정 완료 주장 시.
**미적용**: 신규 기능 개발 (code-generation TDD에서 이미 커버)

### 프로세스

1. 회귀 테스트 실행 → PASS 확인
2. 수정 되돌리기 (`git stash` 또는 수동)
3. 회귀 테스트 실행 → **MUST FAIL**
   - FAIL이면: 테스트가 유효함 증명 ✓
   - PASS이면: ⚠️ 테스트가 버그를 잡지 못함. 테스트 재작성 필요.
4. 수정 복원 (`git stash pop`)
5. 회귀 테스트 + 전체 테스트 실행 → 전체 PASS 확인

### 검증 완료 형식

```
## 회귀 테스트 검증
- 회귀 테스트: [test_name]
- 수정 적용 시: PASS ✓
- 수정 되돌림 시: FAIL ✓ (테스트 유효성 증명)
- 수정 복원 후: 전체 PASS ✓
결론: 회귀 테스트 유효. 완료 선언.
```
```

- [ ] **Step 2: 스펙 대조 검증**

파일을 읽고 스펙 섹션 1과 대조한다:
- Iron Law 문구 일치
- RED-GREEN-REFACTOR 5단계 모두 포함
- 예외 목록 포함
- Red Flags 목록 포함
- Self-Review 체크리스트 4개 영역 (완전성, 품질, 규율, 테스트)
- 회귀 테스트 RED-GREEN 검증 프로세스 5단계

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/tdd-protocol.md
git commit -m "feat: TDD 프로토콜 중앙 규약 추가 — Iron Law, RED-GREEN-REFACTOR, Self-Review, 회귀 테스트 검증"
```

---

### Task 2: Update `_shared/devflow-conventions.md`

**Files:**
- Modify: `skills/_shared/devflow-conventions.md:59-63` (리뷰어 프롬프트 목록 뒤)

**Context:** 스펙 섹션 8. 리뷰 규약 뒤에 TDD 규약 섹션을 추가한다.

- [ ] **Step 1: TDD 규약 섹션 추가**

`## 리뷰 규약` 섹션 뒤, `## Return to Orchestrator 규약` 섹션 앞에 추가:

```markdown
## TDD 규약

- `_shared/tdd-protocol.md` — TDD Iron Law, RED-GREEN-REFACTOR, Self-Review 체크리스트, 회귀 테스트 검증
- Construction 스킬 중 코드를 작성/수정하는 스킬은 이 프로토콜을 참조
- 참조 스킬: `aidlc-code-generation`, `aidlc-verification-before-completion`, `aidlc-systematic-debugging`
- 리뷰 시 TDD 준수 확인: `code-reviewer-prompt.md`, `code-plan-reviewer-prompt.md`
```

- [ ] **Step 2: 버전 업데이트**

frontmatter의 `version: 0.1.0` → `version: 0.2.0`

- [ ] **Step 3: 스펙 대조 검증**

파일을 읽고 확인:
- TDD 규약 섹션이 올바른 위치에 있는가
- tdd-protocol.md 경로가 정확한가
- 버전이 0.2.0인가

- [ ] **Step 4: Commit**

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "docs: devflow-conventions에 TDD 규약 섹션 추가 (v0.2.0)"
```

---

## Chunk 2: Code Generation + Reviewers

### Task 3: Modify `aidlc-code-generation/SKILL.md`

**Files:**
- Modify: `skills/aidlc-code-generation/SKILL.md`

**Context:** 스펙 섹션 2. 4개 영역을 변경한다: PART 1 Plan 형식, PART 2 TDD 프로토콜, Return 형식, Example.

- [ ] **Step 1: PART 1 — Implementation Steps 템플릿에 TDD 하위 단계 추가**

현재 Plan 템플릿의 `## Implementation Steps` 부분 (line 36~37 부근):

```markdown
## Implementation Steps
- [ ] Step 1: [specific action]
- [ ] Step 2: [specific action]
```

을 다음으로 교체:

```markdown
## Implementation Steps
- [ ] Step 1: [기능명]
  - [ ] RED: [테스트명] 작성
  - [ ] Verify RED: 실패 확인
  - [ ] GREEN: [구현 내용]
  - [ ] Verify GREEN: 통과 확인 + 전체 회귀
  - [ ] REFACTOR: [정리 대상이 있으면 명시, 없으면 생략]
- [ ] Step 2: [기능명]
  - [ ] RED: [테스트명] 작성
  ...
```

- [ ] **Step 2: PART 1 — Test Strategy를 TDD 사이클과 연결**

`## Test Strategy` 섹션 하단에 추가:

```markdown
> 각 테스트는 Implementation Steps의 RED 단계에서 작성된다. 별도 테스트 단계가 아님.
```

- [ ] **Step 3: PART 2 — TDD 프로토콜 적용**

현재 PART 2 지침 (line 68~71 부근):

```
1. Execute each step in the plan
2. Mark each checkbox [x] immediately after completing that step
3. Follow TDD: write tests first, then implementation
4. Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`
```

을 다음으로 교체:

```
1. `_shared/tdd-protocol.md` 읽기
2. 각 Implementation Step에 대해 TDD 사이클 실행:
   a. RED: 실패 테스트 작성 → 실행 → 실패 확인
   b. GREEN: 최소 구현 → 실행 → 해당 테스트 + 전체 테스트 통과 확인
   c. REFACTOR: 정리 → 전체 테스트 재실행
   d. 체크박스 [x] 표시 (하위 RED/Verify RED/GREEN/Verify GREEN/REFACTOR 포함)
3. Iron Law 위반 시: 해당 코드 삭제 후 RED부터 재시작
4. 모든 Step 완료 후 Self-Review 체크리스트 수행 (`_shared/tdd-protocol.md` 참조)
5. 자가 수정 후 Save plan progress to `devflow-docs/construction/[unit-name]/code-plan.md`
```

- [ ] **Step 4: PART 2 Return 형식 강화**

현재 PART 2 Return (line 143~150 부근):

```
[code-generation 완료: unit-name]
- 생성된 파일: [count]개
- 모든 체크박스 완료
- 산출물: devflow-docs/construction/[unit-name]/code-plan.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

을 다음으로 교체:

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

- [ ] **Step 5: Example 2 업데이트**

현재 Example 2 (line 99~106 부근):

```
Actions:
1. Step 1 실행: 스켈레톤 작성 → `[x]` 표시
2. Step 2 실행: 테스트 작성 → `[x]` 표시
3. Step 3 실행: 구현 → `[x]` 표시
4. ... (각 체크박스 즉시 업데이트)
```

을 다음으로 교체:

```
Actions:
1. `_shared/tdd-protocol.md` 읽기
2. Step 1 실행:
   - RED: test_create_notification_success 작성 → 실행 → FAIL ✓
   - GREEN: create_notification() 구현 → 실행 → PASS ✓ (전체 1/1)
   - [x] Step 1 완료
3. Step 2 실행:
   - RED: test_create_notification_invalid_user 작성 → 실행 → FAIL ✓
   - GREEN: 유효성 검증 추가 → 실행 → PASS ✓ (전체 2/2)
   - [x] Step 2 완료
4. Step 3~5: 동일 패턴 반복
5. Self-Review 수행 (`_shared/tdd-protocol.md` 체크리스트) → 이슈 없음
6. code-plan.md 저장
```

- [ ] **Step 6: 버전 업데이트**

frontmatter의 `version: 0.4.0` → `version: 0.5.0`

- [ ] **Step 7: 스펙 대조 검증**

파일을 읽고 스펙 섹션 2와 대조:
- PART 1 Plan 템플릿에 RED/Verify RED/GREEN/Verify GREEN/REFACTOR 하위 단계가 있는가
- PART 2에서 "Follow TDD" 1줄이 tdd-protocol 참조 + 5단계 프로세스로 교체되었는가
- Return에 테스트/TDD 사이클/Self-Review 필드가 추가되었는가
- Example에 RED → FAIL, GREEN → PASS 흐름이 보이는가
- 버전이 0.5.0인가

- [ ] **Step 8: Commit**

```bash
git add skills/aidlc-code-generation/SKILL.md
git commit -m "feat: code-generation에 TDD Iron Law 적용 — RED-GREEN-REFACTOR + Self-Review (v0.5.0)"
```

---

### Task 4: Modify `code-plan-reviewer-prompt.md`

**Files:**
- Modify: `skills/_shared/reviewers/code-plan-reviewer-prompt.md:16-24` (체크리스트 테이블)

**Context:** 스펙 섹션 7-2. TDD 사이클 확인 항목 1개 추가.

- [ ] **Step 1: TDD 체크 항목 추가**

체크리스트 테이블 마지막 행 (`| **검증 단계** |`) 뒤에 추가:

```markdown
| **TDD 사이클** | 각 Implementation Step이 RED-GREEN-REFACTOR 하위 단계를 포함하는가 |
```

- [ ] **Step 2: 스펙 대조 검증**

파일을 읽고 확인:
- 체크리스트에 6개 항목 존재 (완전성, 스펙 정합성, 태스크 분해, 파일 구조, 검증 단계, TDD 사이클)

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/reviewers/code-plan-reviewer-prompt.md
git commit -m "feat: code-plan-reviewer에 TDD 사이클 확인 항목 추가"
```

---

### Task 5: Modify `code-reviewer-prompt.md`

**Files:**
- Modify: `skills/_shared/reviewers/code-reviewer-prompt.md:33-40` (Stage 2 테이블)

**Context:** 스펙 섹션 7-1. 기존 테스트 항목 1개를 4개로 확장.

- [ ] **Step 1: 테스트 항목 확장**

Stage 2 Code Quality 테이블의 기존 항목:

```markdown
| **테스트** | 테스트가 실제 로직을 검증하는가 (mock 남용 아닌가) |
```

을 다음 4개로 교체:

```markdown
| **테스트: 행위 검증** | 테스트가 실제 행위를 검증하는가 (mock이 아닌 실제 코드) |
| **테스트: TDD 준수** | 각 기능에 대응하는 테스트가 존재하는가, RED-GREEN 흔적이 보이는가 |
| **테스트: 엣지케이스** | 정상 경로만 테스트하지 않았는가, 실패/경계 케이스가 포함되었는가 |
| **테스트: 회귀 안전성** | 기존 테스트가 모두 유지되었는가, 삭제/변경된 테스트가 있다면 타당한 이유가 있는가 |
```

- [ ] **Step 2: 스펙 대조 검증**

파일을 읽고 확인:
- Stage 2 테이블에 테스트 관련 4개 항목 존재
- 기존 테스트 항목 1개가 제거되고 4개로 교체

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/reviewers/code-reviewer-prompt.md
git commit -m "feat: code-reviewer 테스트 리뷰 항목 4개로 확장 — 행위검증, TDD준수, 엣지케이스, 회귀안전성"
```

---

## Chunk 3: Build & Test + Orchestrator

### Task 6: Rewrite `aidlc-build-and-test/SKILL.md`

**Files:**
- Rewrite: `skills/aidlc-build-and-test/SKILL.md` (전면 재작성)

**Context:** 스펙 섹션 3. "지침 생성 전용"에서 "실행 + 지침 생성"으로 전면 재작성.

- [ ] **Step 1: 전면 재작성**

파일 전체를 다음으로 교체:

```markdown
---
name: aidlc-build-and-test
description: Execute build and full test suite after all units are implemented, then generate reference instructions. Called by aidlc-construction-orchestrator.
metadata:
  version: 0.5.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/build-and-test/
---

# aidlc-build-and-test

<!-- 빌드 실행 + 전체 테스트 실행 + 지침 문서 생성: 모든 unit 완료 후 실행 -->
<!-- B안: 실행 전용 — 게이팅/상태 업데이트/로깅 없음 -->

## Purpose

Execute build and full test suite after all units are implemented, then generate reference instructions for future use.

## Execute

### Step 1: 프로젝트 분석

다음을 확인하여 빌드/테스트 환경을 파악한다:

1. **빌드 설정 파일** — `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml`
2. **소스 파일** — `.py`, `.go`, `.ts`, `.js`, `.rs`, `.java`
3. **Code plans** — `devflow-docs/construction/*/code-plan.md`에서 생성된 파일 목록
4. **units.md** — `devflow-docs/inception/units.md` (있으면) — unit 간 통합 포인트

### Step 2: 빌드 실행

1. 빌드 명령 결정 (프로젝트 타입별 자동 감지):
   - `package.json` → `npm run build` (build 스크립트 있으면) 또는 `npm install`
   - `pyproject.toml` → `pip install -e .` 또는 `poetry install`
   - `go.mod` → `go build ./...`
   - `Cargo.toml` → `cargo build`
   - `pom.xml` → `mvn compile`
2. 빌드 실행
3. 결과 확인:
   - **성공** → Step 3으로
   - **실패** → 에러 메시지 포함하여 Return (오케스트레이터가 처리)

### Step 3: 전체 테스트 스위트 실행

1. 테스트 명령 결정 (프로젝트 타입별 자동 감지):
   - `.py` → `pytest -v` 또는 `python -m pytest -v`
   - `.ts`/`.js` → `npm test`
   - `go.mod` → `go test ./... -v`
   - `Cargo.toml` → `cargo test`
   - `pom.xml` → `mvn test`
2. **전체 테스트 실행** (unit 테스트 + 통합 테스트 포함)
3. 결과 파싱:
   - **전체 통과** → Step 4로
   - **실패 있음** → 실패 테스트 목록 포함하여 Return
     "⚠️ [N]개 테스트 실패. systematic-debugging 권장."

### Step 4: 지침 문서 생성

빌드와 테스트가 모두 성공한 후, 참조용 지침 문서를 생성한다.

**`devflow-docs/construction/build-and-test/build-instructions.md`**:

```markdown
# Build Instructions

## Prerequisites
[빌드에 필요한 도구와 버전]

## Steps
1. [정확한 명령어]
2. [정확한 명령어]

## Expected Output
[성공 시 어떤 결과가 나오는지]
```

**`devflow-docs/construction/build-and-test/test-instructions.md`**:

```markdown
# Test Instructions

## Unit Tests
Run: `[정확한 명령어]`
Expected: [N]개 테스트 통과

## Integration Tests
Run: `[정확한 명령어]`

## Manual Verification
[자동화할 수 없는 확인 단계가 있으면]
```

## Return to Orchestrator

STOP here. No approval gate — orchestrator handles final completion.

```
[build-and-test 결과]
- 빌드: ✅ 성공 | ❌ 실패 ([에러 요약])
- 테스트: ✅ [N]개 통과, 0 실패 | ❌ [N]개 통과, [M]개 실패
- 산출물:
  - devflow-docs/construction/build-and-test/build-instructions.md
  - devflow-docs/construction/build-and-test/test-instructions.md
```

## Error Handling

### 빌드 명령을 결정할 수 없을 때

빌드 시스템이 확인되지 않으면 파일 확장자로 추론한다:
- `.py` → `pip install -r requirements.txt && python -m pytest`
- `.ts`/`.js` → `npm install && npm test`
- `go.mod` → `go build ./... && go test ./...`
- `Cargo.toml` → `cargo build && cargo test`

### 생성된 코드가 없을 때

`devflow-docs/` 밖에 소스 파일이 없으면:
- "⚠️ 생성된 코드를 찾을 수 없습니다." 표시
- placeholder 지침 생성: "코드 생성 후 실행"
```

- [ ] **Step 2: 스펙 대조 검증**

파일을 읽고 스펙 섹션 3과 대조:
- frontmatter description이 변경되었는가
- version이 0.5.0인가
- 4단계 프로세스 (분석 → 빌드 실행 → 테스트 실행 → 지침 생성)
- Return 형식에 빌드/테스트 상태 + 산출물 포함
- Error Handling 3가지 (빌드 불명, 테스트 실패, 코드 없음)

- [ ] **Step 3: Commit**

```bash
git add skills/aidlc-build-and-test/SKILL.md
git commit -m "feat: build-and-test를 실행 스킬로 전면 재작성 — 빌드+테스트 실행+지침 생성 (v0.5.0)"
```

---

### Task 7: Modify `aidlc-construction-orchestrator/SKILL.md`

**Files:**
- Modify: `skills/aidlc-construction-orchestrator/SKILL.md`

**Context:** 스펙 섹션 4. 완료 게이트를 조건부로 변경하고 Debugging 라우팅을 추가한다.

- [ ] **Step 1: 완료 게이트를 조건부 게이트로 변경**

현재 완료 게이트 (line 101~106 부근):

```markdown
#### 완료 게이트 [표준 게이트]
```
[build-and-test 결과 표시]
A) 수정 요청 → build-and-test 재호출
B) 승인, CONSTRUCTION 완료
```
```

을 다음으로 교체:

```markdown
#### 완료 게이트 [조건부 게이트]

build-and-test 결과에 따라 분기:

**빌드 성공 + 테스트 전체 통과 시:**
```
[build-and-test 결과 표시]
A) CONSTRUCTION 완료 승인
B) 추가 수정 요청 → code-generation 재호출
```

**테스트 실패 시:**
```
[build-and-test 결과 표시 — 실패 테스트 목록 포함]
A) systematic-debugging으로 조사
B) 실패를 무시하고 완료 (devflow-state에 "테스트 실패 [N]건 미해결" 기록)
```

**빌드 실패 시:**
```
[build-and-test 결과 표시 — 빌드 에러 포함]
A) systematic-debugging으로 조사
(빌드 실패는 완료 불가 — 무시 선택지 없음)
```
```

- [ ] **Step 2: Debugging 라우팅 섹션 추가**

`## Error Handling` 섹션 앞에 추가:

```markdown
### Debugging 라우팅

build-and-test에서 테스트/빌드 실패 시 사용자가 debugging을 선택하면:

1. `aidlc-systematic-debugging` 호출
2. debugging 완료 시 Return 수신:
   ```
   [systematic-debugging 완료]
   - 근본 원인: [요약]
   - 수정 내용: [요약]
   - 테스트: [회귀 테스트명] 추가됨
   ```
3. debugging Return 수신 후 `aidlc-build-and-test` 재실행
```

- [ ] **Step 3: 버전 업데이트**

frontmatter의 `version: 0.4.0` → `version: 0.5.0`

- [ ] **Step 4: 스펙 대조 검증**

파일을 읽고 스펙 섹션 4와 대조:
- 완료 게이트가 3-way 조건부 (성공/테스트실패/빌드실패)인가
- 빌드 실패 시 무시 선택지가 없는가
- Debugging 라우팅 섹션이 있고 debugging → build-and-test 재실행 루프가 명시되어 있는가
- 버전이 0.5.0인가

- [ ] **Step 5: Commit**

```bash
git add skills/aidlc-construction-orchestrator/SKILL.md
git commit -m "feat: construction-orchestrator 완료 게이트 조건부 변경 + Debugging 라우팅 (v0.5.0)"
```

---

## Chunk 4: Auxiliary Skills

### Task 8: Modify `aidlc-verification-before-completion/SKILL.md`

**Files:**
- Modify: `skills/aidlc-verification-before-completion/SKILL.md`

**Context:** 스펙 섹션 5. 6단계 추가, 상단 참조 추가, Example 3 추가.

- [ ] **Step 1: 상단 참조 추가**

frontmatter 바로 아래, `# aidlc-verification-before-completion` 바로 뒤의 HTML 코멘트에 추가:

```markdown
<!-- TDD 관련 검증은 _shared/tdd-protocol.md 참조 -->
```

- [ ] **Step 2: 6단계 추가**

`### 5단계: 완료 선언` 섹션 뒤에 추가:

```markdown
### 6단계: 회귀 테스트 RED-GREEN 검증 (버그 수정 시)

`_shared/tdd-protocol.md`의 "회귀 테스트 RED-GREEN 검증" 섹션을 수행한다.

**적용 조건**: systematic-debugging을 거쳐 수정한 경우, 또는 버그 수정 완료 주장 시.
**미적용**: 신규 기능 개발 (code-generation TDD에서 이미 커버).

5단계에서 검증이 모두 통과해도, 버그 수정인 경우 이 단계를 추가로 수행한다.
```

- [ ] **Step 3: Example 3 추가**

기존 Examples 섹션 (Example 1, Example 2 뒤)에 추가:

```markdown
### Example 3: 버그 수정 후 회귀 테스트 검증

**상황**: systematic-debugging으로 이메일 검증 버그 수정 완료

**1~5단계**: (일반 Gate 프로세스 수행)

**6단계 수행**:
```bash
# 1. 회귀 테스트 실행
$ pytest tests/test_email.py::test_validate_io_tld -v
# → PASS ✓

# 2. 수정 되돌리기
$ git stash

# 3. 회귀 테스트 실행
$ pytest tests/test_email.py::test_validate_io_tld -v
# → FAIL ✓ (테스트가 버그를 잡음을 증명)

# 4. 수정 복원
$ git stash pop

# 5. 전체 테스트
$ pytest tests/ -v
# → 24 passed, 0 failed ✓
```

완료 선언:
```
## 회귀 테스트 검증
- 회귀 테스트: test_validate_io_tld
- 수정 적용 시: PASS ✓
- 수정 되돌림 시: FAIL ✓ (테스트 유효성 증명)
- 수정 복원 후: 전체 PASS ✓
결론: 회귀 테스트 유효. 완료 선언.
```
```

- [ ] **Step 4: 버전 업데이트**

frontmatter의 `version: 0.1.0` → `version: 0.2.0`

- [ ] **Step 5: 스펙 대조 검증**

파일을 읽고 스펙 섹션 5와 대조:
- 상단에 tdd-protocol 참조 코멘트가 있는가
- 6단계가 5단계 뒤에 있는가
- 적용 조건/미적용 조건이 명시되어 있는가
- Example 3이 회귀 테스트 RED-GREEN 프로세스를 보여주는가
- 버전이 0.2.0인가

- [ ] **Step 6: Commit**

```bash
git add skills/aidlc-verification-before-completion/SKILL.md
git commit -m "feat: verification에 6단계 회귀 테스트 RED-GREEN 검증 추가 (v0.2.0)"
```

---

### Task 9: Modify `aidlc-systematic-debugging/SKILL.md`

**Files:**
- Modify: `skills/aidlc-systematic-debugging/SKILL.md`

**Context:** 스펙 섹션 6. 실패 이력 분석 강화 + Return 형식 추가 + tdd-protocol 참조 + frontmatter 변경.

- [ ] **Step 1: frontmatter에 return_behavior 추가 + 버전 업데이트**

frontmatter에 추가/변경:

```yaml
  return_behavior: stop-no-gate
```

> **주의**: `invoke_mode`는 추가하지 않는다. systematic-debugging은 사용자가 직접 호출할 수도 있고 오케스트레이터가 호출할 수도 있다. 현재 description의 "Invoke via aidlc:aidlc-systematic-debugging" 그대로 유지.

`version: 0.1.0` → `version: 0.2.0`

- [ ] **Step 2: 4단계 4번 항목 강화**

현재 (line 144~151 부근):

```markdown
4. **3회 이상 수정 실패 시 → 아키텍처 재검토**
   - 동일 버그에 3번 이상 수정을 시도했는데 계속 실패하면 멈춘다
   - 현재 접근 방식이 근본적으로 잘못되었을 가능성이 높다
   - 다음 중 하나를 선택한다:
     - A) 더 상위 레벨에서 설계를 재검토한다
     - B) `aidlc-receiving-code-review` 스킬로 피드백을 구한다
     - C) 문제를 최소 재현 케이스로 격리하여 다시 1단계부터 시작한다
```

을 다음으로 교체:

```markdown
4. **3회 이상 수정 실패 시 → 멈추고 실패 이력 분석**

   **즉시 수정 시도를 중단한다.** 먼저 왜 3번 실패했는지 분석한다:

   #### 실패 이력 요약
   | 시도 | 가설 | 수정 내용 | 결과 | 왜 실패했는가 |
   |------|------|----------|------|-------------|
   | 1회  |      |          |      |             |
   | 2회  |      |          |      |             |
   | 3회  |      |          |      |             |

   #### 공통 패턴 식별
   - 3번의 가설이 모두 같은 영역을 겨냥했는가? → 다른 영역 탐색 필요
   - 수정이 매번 다른 테스트를 깨뜨렸는가? → 설계 결합도 문제
   - 근본 원인을 찾지 못한 채 증상만 수정했는가? → 1단계 재현으로 복귀

   #### 분석 후 선택지 제시
   - A) 더 상위 레벨에서 설계를 재검토한다
   - B) `aidlc-receiving-code-review` 스킬로 피드백을 구한다
   - C) 문제를 최소 재현 케이스로 격리하여 다시 1단계부터 시작한다
```

- [ ] **Step 3: tdd-protocol 참조 추가**

4단계 1번 항목 "실패 테스트 작성 (TDD RED)" (line 131 부근) 위에 코멘트 추가:

```markdown
<!-- TDD RED-GREEN 프로세스 상세: _shared/tdd-protocol.md 참조 -->
```

- [ ] **Step 4: Return to Orchestrator 섹션 추가**

파일 끝 (`## Troubleshooting` 섹션 뒤)에 추가:

```markdown
## Return to Orchestrator

STOP. 수정 완료 후 아래 형식으로 반환:

```
[systematic-debugging 완료]
- 근본 원인: [1줄 요약]
- 수정 내용: [1줄 요약]
- 테스트: [회귀 테스트명] 추가됨
- 전체 테스트: [N]개 통과, 0 실패
```
```

- [ ] **Step 5: 스펙 대조 검증**

파일을 읽고 스펙 섹션 6과 대조:
- frontmatter에 `return_behavior: stop-no-gate`와 `invoke_mode: orchestrator-only`가 있는가
- 4단계 4번이 실패 이력 테이블 + 공통 패턴 식별 + 선택지 형태인가
- tdd-protocol 참조 코멘트가 있는가
- Return to Orchestrator 섹션이 있는가
- `aidlc-receiving-code-review` 참조가 유지되었는가
- 버전이 0.2.0인가

- [ ] **Step 6: Commit**

```bash
git add skills/aidlc-systematic-debugging/SKILL.md
git commit -m "feat: systematic-debugging 실패 이력 분석 강화 + Return 형식 추가 (v0.2.0)"
```

---

## Chunk 5: Version Bump

### Task 10: Update `plugin.json`

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Context:** 스펙 섹션 9. 플러그인 전체 버전을 0.5.0으로 업데이트.

- [ ] **Step 1: 버전 업데이트**

`"version": "0.4.0"` → `"version": "0.5.0"`

- [ ] **Step 2: 전체 버전 일관성 검증**

모든 변경 파일의 버전을 확인한다:

| 파일 | 기대 버전 |
|------|----------|
| `skills/aidlc-code-generation/SKILL.md` | 0.5.0 |
| `skills/aidlc-build-and-test/SKILL.md` | 0.5.0 |
| `skills/aidlc-construction-orchestrator/SKILL.md` | 0.5.0 |
| `skills/aidlc-verification-before-completion/SKILL.md` | 0.2.0 |
| `skills/aidlc-systematic-debugging/SKILL.md` | 0.2.0 |
| `skills/_shared/devflow-conventions.md` | 0.2.0 |
| `.claude-plugin/plugin.json` | 0.5.0 |

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: plugin.json v0.4.0 → v0.5.0"
```
