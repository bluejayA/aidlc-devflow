# SDD Brownfield Stub Blind Spot Phase 1 — Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** Brownfield 프로젝트에서 stub이 은폐되는 문제를 사전 인식(Stub Scan) + 사후 검증(잔존 검증)으로 해결
**Complexity:** Standard
**Architecture:** construction-orchestrator가 unit 시작 전 stub 스캔 결과를 code-generation에 전달하고, build-and-test가 성공 후 변경 파일 내 잔존 stub을 검증하는 2중 방어 구조.
**Tech Stack:** SKILL.md (Markdown)

---

### Task 1: construction-orchestrator — 컨텍스트 로드에 workspace.md 추가

**Files:**
- Modify: `skills/aidlc-construction-orchestrator/SKILL.md:37-42` (Step 1 컨텍스트 로드)

- [ ] **Step 1: 테스트 시나리오 확인**
기존 테스트가 construction-orchestrator의 컨텍스트 로드를 검증하는지 확인:
```bash
grep -rn "workspace" tests/scenarios/ --include="*.yaml"
```

- [ ] **Step 2: workspace.md를 컨텍스트 로드 목록에 추가**
`skills/aidlc-construction-orchestrator/SKILL.md` Step 1 컨텍스트 로드에 추가:
```markdown
- `devflow-docs/inception/workspace.md` — brownfield/greenfield 여부 확인 (있으면)
```

- [ ] **Step 3: 테스트 실행 — 기존 테스트 PASS 확인**
```bash
python3 -m pytest tests/ -q
```
Expected: 전체 PASS (regression 없음)

- [ ] **Step 4: 커밋**
`feat: construction-orchestrator 컨텍스트 로드에 workspace.md 추가 (refs #147)`

---

### Task 2: construction-orchestrator — Stub Scan 단계 추가

**Files:**
- Modify: `skills/aidlc-construction-orchestrator/SKILL.md:144-146` (code-generation Plan 호출 직전)

- [ ] **Step 1: 테스트 시나리오 작성**
`tests/scenarios/construction-stub-scan-brownfield.yaml` 생성:
```yaml
name: "Construction — Brownfield stub scan before code-generation"
orchestrator: aidlc-construction-orchestrator
inputs:
  complexity: Standard
  workspace_type: brownfield
  choices:
    code-plan: B
    code-generation-result: B
expect:
  stage_path:
    - code-generation
    - build-and-test
  contains_step: stub-scan
```

- [ ] **Step 2: 테스트 실행 — FAIL 확인 (RED)**
```bash
python3 -m pytest tests/ -q
```
Expected: 새 시나리오 FAIL (stub-scan 미구현)

- [ ] **Step 3: Stub Scan 로직 추가**
`skills/aidlc-construction-orchestrator/SKILL.md`의 code-generation Plan 호출(2b) 직전에 추가:

```markdown
#### 2a-1. Stub Scan (Brownfield 전용)

workspace.md에서 brownfield로 확인된 경우에만 실행. Greenfield는 스킵.

프로젝트 루트에서 stub 패턴 스캔:
\```bash
grep -rn "not yet implemented\|todo!()\|unimplemented!()\|NotImplementedError\|raise NotImplementedError\|UnsupportedOperationException\|TODO(\".*\")\|panic(\"not implemented\")\|panic(\"TODO\")" . --include="*.rs" --include="*.py" --include="*.ts" --include="*.java" --include="*.kt" --include="*.go" --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git --exclude-dir=target --exclude-dir=build --exclude-dir=__pycache__
\```

**스캔 결과 처리:**
- stub 발견 시: code-generation 호출 인라인 컨텍스트에 "## Stub 교체 대상 (Brownfield)" 섹션으로 포함
- stub 미발견 시: 전달 안 함 (무출력)
- 스캔 실패 (exit code != 0, 1 제외) 시: "⚠️ Stub 스캔 실패" 게이트 표시 — A) 재시도 / B) 스킵 (audit 기록)

게이트: 없음 (스캔 성공 시). 스캔 실패 시만 조건부 게이트.
```

- [ ] **Step 4: 테스트 실행 — PASS 확인 (GREEN)**
```bash
python3 -m pytest tests/ -q
```
Expected: 전체 PASS

- [ ] **Step 5: 커밋**
`feat: construction-orchestrator에 Brownfield Stub Scan 단계 추가 (refs #147)`

---

### Task 3: build-and-test — Stub 잔존 검증 추가

**Files:**
- Modify: `skills/aidlc-build-and-test/SKILL.md:57-59` (Step 3 테스트 성공 후, Step 4 지침 생성 전)

- [ ] **Step 1: 테스트 시나리오 작성**
`tests/scenarios/construction-stub-residual-check.yaml` 생성:
```yaml
name: "Construction — Stub residual validation after build success"
orchestrator: aidlc-construction-orchestrator
inputs:
  complexity: Standard
  workspace_type: brownfield
  choices:
    code-plan: B
    code-generation-result: B
    build-and-test-result: success
expect:
  stage_path:
    - code-generation
    - build-and-test
  contains_step: stub-residual-check
```

- [ ] **Step 2: 테스트 실행 — FAIL 확인 (RED)**
```bash
python3 -m pytest tests/ -q
```

- [ ] **Step 3: Stub 잔존 검증 로직 추가**
`skills/aidlc-build-and-test/SKILL.md` Step 3 성공 분기(전체 통과 → Step 4로) 직전에 삽입:

```markdown
### Step 3.5: Stub 잔존 검증 (Brownfield 전용)

Brownfield 프로젝트이고 빌드+테스트 모두 성공한 경우에만 실행.
brownfield 여부는 construction-orchestrator가 호출 시 인라인 전달: `"Brownfield: true"`.

1. Stub Scan과 동일 패턴으로 프로젝트 루트 스캔
2. 변경 파일 목록 추출:
   - `devflow-state.md`의 `## Worktree` → `branch` 확인
   - 워크트리 있음: `git diff --name-only main...HEAD`
   - 워크트리 없음: `git diff --name-only $(git merge-base HEAD origin/main)...HEAD`
   - diff 결과 비어있으면: "⚠️ 변경 파일 감지 불가. A) 수동 지정 / B) 전체 스캔"
3. stub 스캔 결과와 변경 파일 교차 비교 — 변경 파일 내 stub만 추출

**관련 stub 없음:**
\```
✅ Stub 잔존 검증 통과 — 변경 파일 내 미구현 stub 없음
\```
→ Step 4로 진행

**관련 stub 발견 시 — 조건부 게이트:**
\```
⚠️ Stub 잔존 발견 — 변경 파일 내 미구현 stub [N]건

| 파일 | 라인 | 내용 |
|------|------|------|
| [파일경로] | [라인] | [stub 내용] |

A) stub 수정 후 build-and-test 재실행
B) stub을 인지하고 진행 → 사유 입력 요청
\```

**B 선택 시:**
사유 입력 요청 후, session-summary `## Deferred Stubs` 구조화 테이블에 기록:
\```markdown
## Deferred Stubs
| 파일:라인 | stub 내용 | 사유 | 관련 unit | 예상 해결 시점 |
|-----------|----------|------|----------|--------------|
\```
+ devflow-audit에 `"stub-deferred: [파일:라인] — [사유]"` 기록

**스캔 실패 시:** Task 2와 동일 — 재시도/스킵 게이트 + audit 기록
```

- [ ] **Step 4: 테스트 실행 — PASS 확인 (GREEN)**
```bash
python3 -m pytest tests/ -q
```

- [ ] **Step 5: 커밋**
`feat: build-and-test에 Brownfield Stub 잔존 검증 추가 (refs #147)`

---

### Task 4: construction-orchestrator — build-and-test 호출 시 brownfield 전달

**Files:**
- Modify: `skills/aidlc-construction-orchestrator/SKILL.md` (build-and-test 호출 부분)

- [ ] **Step 1: build-and-test 호출 텍스트에 brownfield 인라인 전달 추가**
construction-orchestrator의 build-and-test 호출 시:
```markdown
workspace.md에서 brownfield로 확인된 경우, build-and-test 호출 시 인라인 전달:
`"Brownfield: true"` — stub 잔존 검증 활성화
Greenfield인 경우 전달하지 않음 — stub 검증 스킵
```

- [ ] **Step 2: 테스트 실행 — 전체 PASS 확인**
```bash
python3 -m pytest tests/ -q
```

- [ ] **Step 3: 커밋**
`feat: construction-orchestrator에서 build-and-test에 brownfield 상태 전달 (refs #147)`

---

### Task 5: 전체 검증 + 영향도 확인

**Files:**
- Run: `tests/` 디렉토리 전체

- [ ] **Step 1: 전체 테스트 실행**
```bash
python3 -m pytest tests/ -q
```
Expected: 전체 PASS

- [ ] **Step 2: 변경 키워드 영향도 확인**
```bash
grep -rn "stub.*scan\|stub.*residual\|Brownfield.*true\|DEFERRED_STUB\|stub-deferred" skills/ --include="*.md"
```
변경한 파일 외에 참조하는 곳이 없는지 확인.

- [ ] **Step 3: graph validator 확인**
```bash
python3 -m pytest tests/test_graph_validator.py -v
```
새 gate annotation이 추가되었으므로 그래프 순환/탈출 검증.

- [ ] **Step 4: 커밋 (필요 시)**
