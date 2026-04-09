# Review Timeout Defense + Codex Integration — Implementation Plan

> **For agentic workers:** REQUIRED: Use `aidlc-subagent-driven-development` or `aidlc-executing-plans` to implement.

**Goal:** 리뷰 서브에이전트 타임아웃 방어 + R1 Stage 병렬화 + Codex 세컨드 오피니언 통합
**Complexity:** Standard
**Architecture:** devflow-conventions.md에 타임아웃/병렬화 정책 SSoT 추가. requesting-code-review에서 Stage 2+3 병렬 dispatch + Codex 병렬 실행. INCEPTION 리뷰에는 orchestrator가 Codex adversarial-review를 병렬 실행.
**Tech Stack:** SKILL.md (Markdown), Bash (Codex CLI 감지)

---

### Task 1: devflow-conventions.md — 타임아웃 + 병렬화 정책 추가

**Files:**
- Modify: `skills/_shared/devflow-conventions.md:65-81` (리뷰 규약 섹션)

- [ ] **Step 1: 타임아웃 기본값 섹션 추가**
`### Depth 정책` 아래, `### 리뷰 루프` 위에 다음 섹션을 추가한다:

```markdown
### 타임아웃 정책

| 설정 | 기본값 | 비고 |
|------|--------|------|
| 개별 리뷰어 타임아웃 | 300초 | 사용자 자유 발화로 세션별 오버라이드 가능 |
| R3 팀 전체 타임아웃 | 600초 | 사용자 자유 발화로 세션별 오버라이드 가능 |

타임아웃 발생 시:
- 해당 stage "⏭ 타임아웃" 표시, 나머지 stage 결과로 Verdict 종합
- 모든 리뷰어 타임아웃 → 사용자 escalate: "리뷰 실행 불가. A) 재시도 / B) 리뷰 스킵"

> R2 (Council)는 기존 council-review-protocol.md 타임아웃 정책을 유지한다.
```

- [ ] **Step 2: 병렬화 정책 추가**
같은 섹션에 다음을 추가:

```markdown
### 병렬화 정책

- **Standard**: Stage 2 (Quality) + Stage 3 (Security) 병렬 dispatch
- **Comprehensive**: Stage 2 + Stage 3 + Stage 4 병렬 dispatch
- Stage FAIL 시: FAIL stage만 수정 루프 진입, PASS stage는 재실행하지 않음
```

- [ ] **Step 3: Codex 통합 정책 추가**
다음 섹션을 추가:

```markdown
### Codex 세컨드 오피니언

Codex CLI 설치 시(`command -v codex`) 리뷰에 병렬로 Codex를 실행한다.
감지는 세션당 1회, 결과 캐싱. 미설치 시 "ℹ Codex 미설치 — Claude 단독 리뷰로 진행합니다." (세션당 1회 안내).

| Phase | Codex 도구 | 실행 주체 |
|-------|-----------|----------|
| CONSTRUCTION Stage 2 | `/codex:review` | requesting-code-review (메인) |
| INCEPTION Spec Review | `/codex:adversarial-review` | inception-orchestrator (메인) |
| INCEPTION Plan Review | `/codex:adversarial-review` | inception-orchestrator (메인) |

- Verdict에는 Claude 결과만 반영
- Codex 결과는 "참고 의견" / "약점 분석"으로 별도 표시
- Codex 타임아웃 시 Claude 결과만으로 진행
```

- [ ] **Step 4: 커밋**
`chore: devflow-conventions에 타임아웃/병렬화/Codex 정책 추가`

---

### Task 2: requesting-code-review — R1 병렬화 + Codex 통합

**Files:**
- Modify: `skills/aidlc-requesting-code-review/SKILL.md:85-126` (R1 흐름)

- [ ] **Step 1: Stage 2+3 병렬화 적용**
현재 Stage 2 → Stage 3 순차 흐름을:

```markdown
#### Stage 2+3 — Code Quality + Security (병렬)

Stage 1 완료 후, depth에 따라 병렬 dispatch한다.

**Minimal**: Stage 2만 단독 실행 (Stage 3 스킵)
**Standard**: Stage 2 + Stage 3 병렬 dispatch
**Comprehensive**: Stage 2 + Stage 3 + Stage 4 전부 병렬 dispatch

1. 해당 Stage 서브에이전트들을 background dispatch
2. 모든 결과 수신 후 종합:
   - 모두 PASS → 결과 반환
   - 일부 FAIL → FAIL stage만 수정 루프 (PASS stage 결과 유지)
   - 모두 FAIL → 모든 stage 수정 루프
```

로 변경한다.

- [ ] **Step 2: Codex 병렬 실행 로직 추가**
Stage 2+3 병렬 dispatch 직전에 Codex 감지 + 실행 로직을 추가한다:

```markdown
#### Codex 세컨드 오피니언 (Stage 2 병렬)

conventions Codex 세컨드 오피니언 정책 적용.

Stage 2+3 병렬 dispatch와 동시에 메인 컨텍스트에서 `/codex:review`를 실행한다.
- Codex CLI 미감지 시 스킵 (conventions fallback 참조)
- Codex 결과는 Stage 2+3 결과 표시 시 "Codex 참고 의견" 섹션으로 별도 표시
- Codex 타임아웃 시 "Codex 세컨드 오피니언: ⏭ 타임아웃" 표시
```

- [ ] **Step 3: 타임아웃 표시 처리 추가**
각 Stage dispatch 설명에 타임아웃 처리를 추가:

```markdown
> **타임아웃**: conventions 타임아웃 정책 적용. 개별 리뷰어 기본 300초. 타임아웃 시 "⏭ 타임아웃" 표시, 나머지 결과로 종합.
```

- [ ] **Step 4: 커밋**
`feat: requesting-code-review R1 병렬화 + Codex 세컨드 오피니언`

---

### Task 3: brainstorming + writing-plans — Codex 사후 실행 안내 추가

**Files:**
- Modify: `skills/aidlc-brainstorming/SKILL.md:91` (Step 6 Spec Review Loop)
- Modify: `skills/aidlc-writing-plans/SKILL.md:107` (Plan Review Loop)

- [ ] **Step 1: brainstorming에 Codex 안내 추가**
Spec Review Loop 설명에 다음을 추가:

```markdown
> **Codex 세컨드 오피니언**: 이 스킬 완료 후 inception-orchestrator가 산출물에 `/codex:adversarial-review`를 사후 실행한다. 이 스킬은 Claude 리뷰어 결과만 반환한다.
```

- [ ] **Step 2: writing-plans에 동일 안내 추가**
Plan Review Loop 설명에 다음을 추가:

```markdown
> **Codex 세컨드 오피니언**: 이 스킬 완료 후 inception-orchestrator가 산출물에 `/codex:adversarial-review`를 사후 실행한다. 이 스킬은 Claude 리뷰어 결과만 반환한다.
```

- [ ] **Step 3: 커밋**
`docs: brainstorming/writing-plans에 Codex 사후 실행 안내`

---

### Task 4: inception-orchestrator — Codex 사후 실행 로직 추가

**Files:**
- Modify: `skills/aidlc-inception-orchestrator/SKILL.md`
  - `## The Orchestration Loop` 직전 (line 27 부근): Codex CLI 감지
  - brainstorming 게이트 직후 (brainstorming 결과 표시 후): Codex 사후 실행
  - writing-plans 게이트 직후: Codex 사후 실행

- [ ] **Step 1: Codex CLI 감지 로직 추가**
`## The Orchestration Loop` 직전에 다음 섹션을 추가:

```markdown
### Step 0: Codex CLI 감지

conventions Codex 세컨드 오피니언 정책 적용.
`command -v codex`로 Codex CLI 가용성을 감지한다 (세션당 1회, 결과 캐싱).
- 감지 성공: 이후 brainstorming/writing-plans 완료 후 Codex 사후 실행
- 감지 실패: "ℹ Codex 미설치 — Claude 단독 리뷰로 진행합니다." (1회 안내)
```

- [ ] **Step 2: brainstorming 완료 후 Codex 사후 실행 로직 추가**
brainstorming 결과를 사용자에게 표시한 뒤, 게이트 제시 전에:

```markdown
### brainstorming 완료 후 Codex 사후 리뷰

Codex 가용 시, brainstorming이 저장한 설계 문서에 `/codex:adversarial-review`를 실행한다.
1. 대상: brainstorming이 저장한 `docs/plans/` 또는 `devflow-docs/inception/` 파일
2. Codex 결과를 "Codex 약점 분석" 섹션으로 사용자에게 별도 표시
3. Codex 타임아웃 시 "Codex 세컨드 오피니언: ⏭ 타임아웃" 표시, Claude 결과만으로 진행
4. 사용자가 Codex 지적을 채택할지 판단 후 게이트 진행
```

- [ ] **Step 3: writing-plans 완료 후 동일 로직 추가**
writing-plans 결과를 사용자에게 표시한 뒤, Execution Handoff 전에:

```markdown
### writing-plans 완료 후 Codex 사후 리뷰

Codex 가용 시, writing-plans가 저장한 구현 계획에 `/codex:adversarial-review`를 실행한다.
1. 대상: writing-plans가 저장한 `docs/plans/` 파일
2. Codex 결과를 "Codex 약점 분석" 섹션으로 사용자에게 별도 표시
3. Codex 타임아웃 시 "Codex 세컨드 오피니언: ⏭ 타임아웃" 표시, Claude 결과만으로 진행
4. 사용자가 Codex 지적을 채택할지 판단 후 Execution Handoff 진행
```

- [ ] **Step 4: 커밋**
`feat: inception-orchestrator에 Codex 사후 실행 로직 추가`

---

> **Scope note**: R3 타임아웃 부분 완료 허용(설계 2.4)은 R3 자체가 이번 구현 범위 밖이므로 plan에 포함하지 않는다. 향후 R3 개선 시 별도 태스크로 처리.

---

### Task 5: 테스트 검증

**Files:**
- Run: `tests/` 디렉토리 전체

- [ ] **Step 1: 기존 테스트 실행**
```bash
python3 -m pytest tests/ -q
```
Expected: 모든 기존 테스트 PASS (regression 없음)

- [ ] **Step 2: 변경 키워드 영향도 확인**
```bash
grep -rn "리뷰 스킵\|review skip\|Stage 2.*Stage 3" skills/ --include="*.md"
```
"리뷰 스킵"이 Minimal 컨텍스트에서 남아있지 않은지 확인.

- [ ] **Step 3: 커밋**
테스트 통과 확인 후 최종 커밋 (필요 시).
