# SDD Brownfield Stub Blind Spot — Phase 1 설계

**Complexity:** Standard
**Date:** 2026-04-10
**Related:** BL-082 (#147), Phase 1 of 3

---

## 1. 문제

Brownfield 프로젝트에서 SDD로 구현 시, 기존 코드에 `"not yet implemented"` stub이 존재해도:
- Implementer가 인식하지 못하고 신규 코드만 작성
- Mock 기반 테스트가 전부 통과하여 stub이 은폐됨
- 런타임에서 즉시 실패

## 2. Phase 1 범위

| 변경 | 위치 | 역할 |
|------|------|------|
| **Stub Scan** | construction-orchestrator, unit 시작 전 | 사전 인식 — stub 목록을 implementer에 전달 |
| **Stub 잔존 검증** | build-and-test, 성공 후 | 사후 검증 — 변경 파일 내 잔존 stub 게이트 |

Phase 2 (CRITICAL 자동 승격 + Brownfield 체크리스트)와 Phase 3 (Mock/Real 갭 리포트)는 별도 백로그.

---

## 3. 설계: Stub Scan (Unit 시작 전)

### 실행 조건

- `workspace.md`에서 brownfield 여부 확인
- Brownfield일 때만 실행. Greenfield는 스킵 (무출력)

### 스캔 명령

```bash
grep -rn "not yet implemented\|todo!()\|unimplemented!()\|NotImplementedError\|raise NotImplementedError\|UnsupportedOperationException\|TODO(\".*\")\|panic(\"not implemented\")\|panic(\"TODO\")" . --include="*.rs" --include="*.py" --include="*.ts" --include="*.java" --include="*.kt" --include="*.go" --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git --exclude-dir=target --exclude-dir=build --exclude-dir=__pycache__
```

### 결과 전달

stub 발견 시, code-generation 호출 인라인 컨텍스트에 포함:

```markdown
## Stub 교체 대상 (Brownfield)
아래 stub이 이 unit의 구현 범위와 관련될 수 있습니다:
- src/adapters/http.rs:42 — "not yet implemented"
- src/adapters/http.rs:67 — "not yet implemented"
관련 stub이 있다면 실제 구현으로 교체하세요.
```

stub 미발견 시 전달 안 함.

### 게이트

없음. 정보 전달만.

### 토큰 비용

~1K/unit (scan 결과 텍스트). Greenfield: 0.

---

## 4. 설계: Stub 잔존 검증 (build-and-test 성공 후)

### 실행 조건

- Brownfield일 때만 실행. Greenfield는 스킵
- build + test 모두 성공한 후 실행 (실패 시 실행 안 함)

### 스캔 + 필터링

1. 동일 stub 패턴으로 스캔
2. `git diff --name-only main...HEAD`로 main 브랜치 대비 변경 파일 목록 추출 (워크트리 없이 main 직접 작업 시 `git diff --name-only HEAD~[커밋수]`)
3. stub 스캔 결과와 변경 파일 교차 비교
4. **변경 파일 내 stub만 보고** (무관한 기존 stub은 제외)

### 결과 분기

**관련 stub 없음:**
```
✅ Stub 잔존 검증 통과 — 변경 파일 내 미구현 stub 없음
```

**관련 stub 발견 시 — 조건부 게이트:**
```
⚠️ Stub 잔존 발견 — 변경 파일 내 미구현 stub [N]건

| 파일 | 라인 | 내용 |
|------|------|------|
| src/adapters/http.rs | 42 | "not yet implemented" |

A) stub 수정 후 build-and-test 재실행
B) stub을 인지하고 진행 → 사유 입력 요청 후 session-summary에 [DEFERRED_STUB] 기록
```

### A/B 선택 동작

- **A**: 사용자가 stub 수정 → build-and-test 재실행
- **B**: session-summary `## Deferred Stubs` 섹션에 기록 + devflow-audit에 `"stub-deferred: [파일:라인] — [사용자 사유]"` 기록

### 게이트

조건부 1개 (stub 발견 시만). review-gate-pattern 적용.

### 토큰 비용

~2.8K (1회, 전체 빌드 후). Greenfield: 0.

---

## 5. 변경 대상 파일

| 파일 | 변경 내용 |
|------|----------|
| `aidlc-construction-orchestrator/SKILL.md` | Step 1 컨텍스트 로드에 `workspace.md` 추가 + unit별 code-generation 호출 전 stub scan + 결과 전달 |
| `aidlc-build-and-test/SKILL.md` | brownfield 여부를 orchestrator에서 전달받아 성공 후 stub 잔존 검증 + 조건부 게이트 |

---

## Assumptions

- `workspace.md`의 brownfield/greenfield 구분이 정확하다
- stub 패턴이 주요 언어를 커버한다: Rust (`todo!()`, `unimplemented!()`), Python (`NotImplementedError`), Go (`panic("not implemented")`), Java/Kotlin (`UnsupportedOperationException`, `TODO()`), 공통 (`not yet implemented`)
- 변경 파일 내 stub만 필터링하면 false positive가 낮다
