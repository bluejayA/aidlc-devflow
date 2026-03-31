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
