---
name: aidlc-build-and-test
description: Use when code implementation is complete and needs to be built, tested, and verified before completion.
metadata:
  version: 0.5.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/construction/build-and-test/
---

# aidlc-build-and-test

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 빌드 실행 + 전체 테스트 실행 + 지침 문서 생성: 모든 unit 완료 후 실행 -->

## Purpose

Execute build and full test suite after all units are implemented, then generate reference instructions for future use.

## Execute

### Step 1: 프로젝트 분석

다음을 확인하여 빌드/테스트 환경을 파악한다:

1. **빌드 설정 파일** — `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml`
2. **소스 파일** — `.py`, `.go`, `.ts`, `.js`, `.rs`, `.java`
3. **Code plans** — `devflow-docs/construction/*/code-plan.md`에서 생성된 파일 목록
4. **units.md** — `devflow-docs/inception/units.md` (있으면) — unit 간 통합 포인트
5. **Verification Contract** — `devflow-docs/construction/{unit}/code-plan.md`의 `## Verification Contract` 섹션을 확인한다. 섹션이 있으면 검증 명령을 Step 3에서 우선 사용한다. 섹션이 없으면 기존 동작(프로젝트 타입 자동 감지)을 유지한다. auto-fix 후 재실행 시에도 Verification Contract의 검증 명령 전체를 다시 실행한다.

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
   - **전체 통과** → Step 3.5로
   - **실패 있음** → 실패 테스트 목록 포함하여 Return
     "⚠️ [N]개 테스트 실패. systematic-debugging 권장."

### Step 3.5: Stub 잔존 검증 (Brownfield 전용)

construction-orchestrator가 호출 시 `"Brownfield: true"` 인라인 전달한 경우에만 실행. 미전달 시 스킵하고 Step 4로.

1. Stub Scan과 동일 패턴으로 프로젝트 루트 스캔
2. 변경 파일 목록 추출:
   - `devflow-state.md`의 `## Worktree` → `branch` 확인
   - 워크트리 있음: `git diff --name-only main...HEAD`
   - 워크트리 없음: `git diff --name-only $(git merge-base HEAD origin/main)...HEAD`
   - diff 결과 비어있으면: `"⚠️ 변경 파일 감지 불가. A) 수동 지정 / B) 전체 스캔"`
3. stub 스캔 결과와 변경 파일 교차 비교 — 변경 파일 내 stub만 추출

**관련 stub 없음:**
```
✅ Stub 잔존 검증 통과 — 변경 파일 내 미구현 stub 없음
```
→ Step 4로 진행

**관련 stub 발견 시 — 조건부 게이트:**
```
⚠️ Stub 잔존 발견 — 변경 파일 내 미구현 stub [N]건

| 파일 | 라인 | 내용 |
|------|------|------|
| [파일경로] | [라인] | [stub 내용] |

A) stub 수정 후 build-and-test 재실행
B) stub을 인지하고 진행 → 사유 입력 요청
```

**A 선택 시:** 사용자가 stub 수정 → build-and-test 재실행 (Step 2부터)
**B 선택 시:** 사유 입력 요청 후, session-summary `## Deferred Stubs` 구조화 테이블에 기록:

```markdown
## Deferred Stubs
| 파일:라인 | stub 내용 | 사유 | 관련 unit | 예상 해결 시점 |
|-----------|----------|------|----------|--------------|
```

+ devflow-audit에 `"stub-deferred: [파일:라인] — [사유]"` 기록
+ 다음 세션 재개 시 construction-orchestrator가 `## Deferred Stubs`를 감지하여 Stub Scan에 포함

**스캔 실패 시:** 재시도/스킵 게이트 + devflow-audit에 `"stub-scan-error"` 기록

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

conventions 표준 형식. 반환 필드:
- 빌드: ✅ 성공 | ❌ 실패 ([에러 요약])
- 테스트: ✅ [N]개 통과, 0 실패 | ❌ [N]개 통과, [M]개 실패
- Verification Contract: [완료 조건 pass/fail 체크리스트] (계약이 있는 경우에만 포함)
- 산출물: build-instructions.md, test-instructions.md

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
