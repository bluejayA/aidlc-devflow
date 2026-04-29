---
name: aidlc-auto-mode
description: |
  Use when user explicitly requests "auto 모드", "자동 모드", "auto mode", or "알아서 만들어줘".
  초보자를 위한 완전 자동 devflow. greenfield 전용.
  요구사항 입력 → inception → construction → build-test를 자동 진행하며
  각 flow 종료 시 멀티에이전트 리뷰 필수.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
  return_behavior: stop-with-gate
  skill_nature: amplification
  lifecycle: active
---

# aidlc-auto-mode

<!-- 출력 언어: 한국어 (Korean) -->
<!-- 초보자용 완전 자동 devflow. greenfield 전용. 단일 파일 자기 완결형. -->
<!-- 기존 devflow SKILL.md 무수정. stage 스킬 재활용. -->

## Trigger

"auto 모드", "자동 모드", "auto mode", "알아서 만들어줘" 키워드가 명시적으로 포함된 경우에만 활성화.
그 외 모든 개발 요청은 기존 `aidlc-using-devflow`로 라우팅.

## Examples

```
user: "auto 모드로 TODO 앱 만들어줘"
→ greenfield 확인 → INCEPTION 자동 → 사용자 확인 → CONSTRUCTION 자동 → 완료

user: "자동 모드로 로그인이 있는 블로그 만들어줘"
→ 고위험 가정 게이트(인증 방식) → 사용자 확인 → 코드 생성 → 완료
```

## Troubleshooting

| 상황 | 대응 |
|------|------|
| 터미널을 닫거나 세션이 끊겼을 때 | "auto 모드"로 다시 시작하면 자동 감지하여 이어서 진행 제안 |
| 요구사항이 모호해서 반복 실패 | 고위험 가정 게이트에서 핵심 결정을 확인. 그래도 실패 시 단계별 모드로 전환 |
| "이거 아닌데요" — 결과가 기대와 다를 때 | 다음 요청에서 구체적으로 무엇이 다른지 설명하면 auto 모드로 재진행 |

## On Activation

### Step 1: 세션 감지

`devflow-docs/auto-decision-log-inception.md` 또는 `devflow-docs/auto-decision-log-construction.md` 존재 여부 확인.

**존재하면 → 재개 제안:**
```
이전에 자동 모드로 진행하던 작업이 있습니다.
진행 상황: [devflow-state.md에서 읽은 completed stages 수] 단계 완료
A) 이어서 진행하기
B) 처음부터 새로 시작하기
```

A → Session Resume 실행.
B → 기존 산출물을 `.archive/`로 이동 후 Step 2로.

**존재하지 않으면 → Step 2로.**

### Step 2: greenfield 확인

사용자 요구사항과 현재 디렉토리를 분석:
- 소스 코드 파일(`.py`, `.ts`, `.js`, `.go`, `.rs`, `.java`, `.kt`, `.swift` 등)이 존재하면 → brownfield.
- 설정 파일만 있거나(`.gitignore`, `CLAUDE.md`, `package.json` 초기 상태 등) 비어있으면 → greenfield.

**brownfield:**
```
auto 모드는 새 프로젝트(greenfield) 전용입니다.
기존 코드가 있는 프로젝트는 단계별 모드로 진행합니다.
→ aidlc-using-devflow로 전환합니다.
```

**greenfield → Step 3로.**

### Step 3: 재진입 확인 (첫 실행 아닌 경우)

`.archive/`에 이전 auto-mode 세션(`auto-decision-log-*.md`)이 존재하면:
```
이전에 auto 모드로 완료한 작업이 있습니다.
이번에도 auto 모드로 진행할까요?
A) 네, auto 모드로 진행
B) 아니오, 단계별 모드로 진행 → aidlc-using-devflow
```

A 또는 첫 실행 → Step 4로.

### Step 4: 초기화

1. `devflow-docs/` 디렉토리 생성 (하위 `inception/`, `construction/` 포함)
2. `devflow-state.md` 초기화:
   ```markdown
   # DevFlow State

   ## Current Phase
   INCEPTION

   ## Current Stage
   (pending)

   ## Complexity
   (pending)

   ## Selected Approach
   (pending)

   ## Last Updated
   <ISO 8601 timestamp>
   ```
   `## Last Updated`는 post-tool-file-edit hook이 후속 file-edit마다 soft-save하는 필드. 누락 시 hook이 no-op이 되므로 초기화 단계에서 반드시 포함한다.
3. `auto-decision-log-inception.md` 생성:
   ```markdown
   # Auto Decision Log — INCEPTION
   ```
4. 사용자에게 안내:
   ```
   auto 모드를 시작합니다.
   요구사항을 분석하고 설계한 뒤, 확인을 받고 코드를 생성합니다.
   ```
5. Phase 1 진행.

---

## Phase 1: INCEPTION 자동 진행

### 스테이지 순서

```
workspace-detection → complexity 자동 선언 → requirements-analysis
  → [고위험 가정 게이트] → (user-stories) → (nfr-requirements)
  → workflow-planning → (application-design)
```

각 스테이지에서 아래를 반복:

### Step A: 스테이지 시작

devflow-state의 `## Current Stage`를 `[stage-name] (in-progress)`로 기록.
사용자에게 진행 메시지 표시:

| 스테이지 | 메시지 |
|---------|--------|
| workspace-detection | "프로젝트 환경을 분석하고 있습니다..." |
| complexity | "프로젝트 규모를 판단하고 있습니다..." |
| requirements-analysis | "요구사항을 분석하고 있습니다..." |
| user-stories | "사용자 시나리오를 작성하고 있습니다..." |
| nfr-requirements | "성능/보안 기준을 설정하고 있습니다..." |
| workflow-planning | "구현 계획을 수립하고 있습니다..." |
| application-design | "시스템 구조를 설계하고 있습니다..." |

### Step B: 스킬 호출

인라인 신호로 stage 스킬을 호출:

| 스킬 | 인라인 신호 |
|------|-----------|
| workspace-detection | (직접 호출) |
| requirements-analysis | `"Complexity: [level]"` |
| requirements-analysis 재호출 | `"aidlc-requirements-analysis: UPDATE — [변경 내용]"` |
| user-stories | `"Complexity: [level]"` |
| nfr-requirements | `"Mode: GENERATE"`, `"Complexity: [level]"` |
| workflow-planning | `"Complexity: [level]"` |
| application-design LIST | `"Complexity: [level]"` |
| application-design DETAIL | `"aidlc-application-design: DETAIL"` (NFR 있으면 `"— NFR Design 포함"`) |

### Step C: 자동 판단 + Checkpoint

스킬 반환값을 자동 승인하고 Checkpoint 실행 (State Management 참조).
decision-log에 판단 상세 기록.

### 자동 판단 규칙

**Complexity 자동 선언** (workspace-detection 직후):

| 기준 | Minimal | Standard | Comprehensive |
|------|---------|----------|---------------|
| 예상 파일 수 | ~5개 이하 | 6-20개 | 20개 이상 |
| 서비스/컴포넌트 | 단일 | 2-3개 | 4개 이상 |
| DB | 불필요 | 단일 | 복수 또는 복잡 스키마 |
| 외부 연동 | 없음 | 1-2개 | 3개 이상 |
| 대표 예시 | CLI 도구, 유틸리티 | CRUD 웹앱, REST API | 마이크로서비스, 플랫폼 |

복수 기준이 다른 레벨 → 높은 쪽으로 선언. 각 기준별 근거를 decision-log 기록.

**기술 스택 자동 선택** (requirements-analysis 내):
1. CLAUDE.md에 명시된 기술 → 무조건 채택
2. 아키텍처 패턴 → `tech-stack-defaults.md` 매핑 참조
3. 미커버 계층 → `tech-stack-catalog.md`에서 "(권장)" 자동 선택
4. 모든 선택을 decision-log에 기록

**Pre-Planning 자동 결정:**
- Minimal → 스킵
- Standard → NFR만
- Comprehensive → 전체 (user-stories + NFR)

**Approach 자동 선택** (workflow-planning 직후):
- 첫 번째(권장) approach 자동 선택
- devflow-state `## Selected Approach` + `## Approved Stages` 업데이트
- workflow-plan.md `**Selected Approach**` 마킹

**SDD vs 인라인** (units-generation 직후):
- Minimal → 인라인 강제
- Standard/Comprehensive + unit 2개 이상 → SDD

### 고위험 가정 게이트

requirements-analysis 완료 후, 가정 목록에서 고위험 항목을 판별:
- 인증/보안 방식 관련
- 유료 외부 서비스 의존
- 데이터 모델 핵심 구조

**고위험 가정 1건 이상 → 미니 게이트:**
```
확인이 필요한 자동 판단이 있습니다:
1. [가정 내용] ([이유])
2. [가정 내용] ([이유])

A) 맞습니다, 계속 진행
B) 수정할 부분이 있습니다 → [번호 선택]
```

B → 수정 반영 후 requirements-analysis UPDATE 재호출.
고위험 가정 0건 → 자동 진행.

---

## INCEPTION 리뷰 + 사용자 확인

### INCEPTION 리뷰 (필수)

모든 INCEPTION 스테이지 완료 후 실행.
사용자에게: "설계를 검토하고 있습니다... (5개 관점)"

5개 리뷰어를 병렬 dispatch (subagent_type 사용):
1. `aidlc:spec-reviewer` (대상: requirements.md, user-stories.md)
2. `aidlc:code-reviewer` (대상: application-design.md)
3. `aidlc:quality-reviewer` (대상: 전체 inception 산출물)
4. `aidlc:security-reviewer` (대상: nfr-requirements.md, application-design.md)
5. `aidlc:maintainability-reviewer` (대상: application-design.md)

**결과 처리:**
- ALL PASS → 사용자 확인 게이트로.
- ISSUES Found → 순차 수정:
  수정 우선순위: security → spec → code → quality → maintainability
  수정 후 전체 5개 re-dispatch. 최대 3라운드.
- 3라운드 초과 → 사용자 에스컬레이션 (Error Handling 참조).

### 사용자 확인 게이트 (유일한 게이트)

일상 언어로 요약 + Claude 자율 판단 하이라이트:

```
## 설계가 완료되었습니다

만들려는 것: [사용자 요구사항 1줄 요약]
프로젝트 규모: [일상 언어] ([Complexity])
기술 스택: [주요 기술 나열]

## 자동으로 결정한 항목 (검토해 주세요)
[번호. 결정 내용 → 선택값 (이유: 판단 근거)]
...

설계 검토 결과: [N]개 관점 통과 [결과 요약]

상세 내용: devflow-docs/inception/ 에서 확인 가능

A) 수정할 부분이 있습니다
   [자동 결정 항목별 번호 선택지]
   N) 기타 (직접 입력)
B) 좋습니다, 코드 생성을 시작합니다
```

**A 선택 시:** 번호 선택 → 해당 항목의 대안 제시 → 수정 반영 → 해당 스테이지 재실행 → 리뷰 재실행 → 게이트 재표시.
**B 선택 시:** Phase 2 진행. devflow-state `## Current Phase`를 `CONSTRUCTION`으로 업데이트.

---

## Phase 2: CONSTRUCTION 자동 진행

사용자에게: "코드 생성을 시작합니다."
`auto-decision-log-construction.md` 생성.

### 스테이지 순서

```
(units-generation) → per-unit: [(functional-design) → code-plan → code-gen]
  → build-and-test → [auto-fix 루프]
```

### 스테이지별 실행

**units-generation (조건부):**
workflow-plan.md `## Approved Stages`에서 `units-generation: included`이면 실행.
결과 자동 승인 + Checkpoint.

**SDD 자동 결정** (unit 2개 이상):
- Minimal → 인라인 강제
- Standard/Comprehensive → `aidlc-subagent-driven-development` 호출
  인라인 신호: `"SDD: units=[devflow-docs/inception/units.md], summary=[devflow-docs/session-summary.md], complexity=[level], functional-designs=[devflow-docs/inception/functional-design-*.md]"` (functional-design 없으면 해당 필드 생략)

**인라인 모드 (unit 1개 또는 Minimal):**
각 unit에 대해:
1. (functional-design) — Comprehensive만. `aidlc-functional-design` 호출 (unit명 전달).
   사용자에게: "[unit명] 상세 설계 중..."
2. code-generation Plan — `"Complexity: [level]"` + unit명.
   사용자에게: "[unit명] 구현 계획 작성 중..."
   결과 자동 승인 + Checkpoint.
3. code-generation Generate — `"aidlc-code-generation: GENERATE — proceed with the approved plan for [unit-name]"`
   사용자에게: "[unit명] 코드 생성 중..."
   결과 자동 승인 + Checkpoint.
   devflow-state `## Completed Units`에 unit명 추가.

**build-and-test:**
사용자에게: "빌드 및 테스트 실행 중..."
`aidlc-build-and-test` 호출.

auto-fix 루프 (테스트 실패, 린트 에러):
- `code-generation: GENERATE — auto-fix for [unit]: [에러 요약]` 재호출
- `aidlc-build-and-test` 재실행
- 최대 3회. 수정 후 전체 테스트 재실행 (regression 방지).
- 3회 소진 → 에스컬레이션 (Error Handling 참조).

빌드 실패, 환경 문제, auth/security 태그 unit → 즉시 에스컬레이션.

### CONSTRUCTION 리뷰 (필수)

사용자에게: "코드를 검토하고 있습니다... (4개 관점)"
`aidlc-requesting-code-review` R1 호출. 인라인 신호: `"Review: full-depth"`
R1이 4단계 리뷰 수행:
- Stage 1: `_shared/reviewers/spec-reviewer-prompt.md`
- Stage 2: `_shared/reviewers/code-quality-reviewer-prompt.md`
- Stage 3: `_shared/reviewers/security-reviewer-prompt.md`
- Stage 4: `_shared/reviewers/maintainability-reviewer-prompt.md`

- PASS → 최종 결과 표시.
- ISSUES → 순차 수정 (security → spec → code → quality → maintainability) 후 re-dispatch. 최대 3라운드.
- 3라운드 초과 → 에스컬레이션.

### 최종 결과물 + 실행 안내

```
프로젝트가 완성되었습니다!

생성된 파일: [N]개
테스트: [N]개 통과

→ 지금 바로 실행해볼까요?
A) 네, 실행 방법을 알려주세요
   → [빌드 시스템에서 감지한 실행 명령] + [접속 URL]
B) 나중에 실행하겠습니다
```

### 세션 체이닝

```
다음 작업도 auto 모드로 진행할까요?
A) 네, auto 모드로 계속
B) 아니오, 단계별 모드로 전환
C) 종료
```

A → devflow-state `finished` → `.archive/` 이동 (decision-log 포함) → 새 auto-mode 세션.
B → devflow-state `finished` → `.archive/` 이동 → using-devflow 안내.
C → devflow-state `finished` → 세션 종료.

---

## State Management

### Checkpoint 블록 (매 스테이지 완료 시 반드시 실행)

**1단계 — 기록:** 다음 4개 파일을 순서대로 업데이트:
1. `devflow-state.md` — Current Stage 갱신 (in-progress 제거), `## Last Updated`를 ISO 8601 timestamp로 갱신
2. `session-summary.md` — 아래 §session-summary 갱신 규칙 준수
3. `devflow-docs/audit.md` — 아래 §audit emit 형식으로 한 줄 append
4. `auto-decision-log-[phase].md` — 판단 상세 append

**2단계 — 검증:** `devflow-state.md`를 Read로 열어 Current Stage 값 확인. 불일치 시 즉시 수정.

**3단계 — 진행 메시지:** 사용자에게 다음 스테이지 진행 메시지 표시.

### session-summary 갱신 규칙

baseline은 `_shared/patterns/session-continuity.md` (템플릿 + 6항 작성 규칙 + Traps to Avoid 운영 규칙). auto-mode 특수 규칙만 아래 인라인.

**필수 필드 자동 기록**: `Last Updated` (ISO 8601), `Commit` (`git rev-parse --short HEAD`, Phase 전환·Unit 완료 시 갱신), `Completed Work` (`[x]` + 한 줄 결과), `Key Decisions` (최근 20개), `Next Steps`, `Traps to Avoid` (`(없음)` 기본값, BL-104 적용 전까지), `For Next Session` (에스컬레이션·완료 시점에만).

**6항 규칙(BL-093) 적용 — auto-mode 컨텍스트:**

| # | 규칙 | auto-mode 적용 |
|---|---|---|
| 1 | Open Work 상태 서술형 | "X 미구현" (명령형 "X 구현하라" 금지) |
| 2 | 파일 참조는 라인 번호까지 | code-generation 산출물 인용 시 `path:L<N>-L<M>` |
| 3 | Traps to Avoid 섹션 | `(없음)` 기본값. BL-104 적용 전까지 auto-fix 폐기는 decision-log에만 |
| 4 | 검증 지시 포함 | summary 첫 줄에 "이 문서의 주장을 코드/git 상태와 대조해 검증한 후 작업 시작" |
| 5 | CLAUDE.md 중복 회피 | 첫 줄에 "Read CLAUDE.md first. Do NOT restate" 포함 |
| 6 | 2K 토큰 상한 (~80-100줄) | 상한 근접 시 Key Decisions / Completed Work 최근 20개 외 삭제 |

### audit emit 형식

plugin 공통 emit 표준(BL-098, memory-sync 패턴) 준수. 상세는 `decision-log-format.md` §audit emit 참조.

| Prefix | 시점 | fields |
|---|---|---|
| `auto-mode-invoked` | skill 진입 직후 (Step 1 후) | `mode=new\|resume`, `intent` |
| `auto-mode-stage-completed` | 매 스테이지 Checkpoint | `stage`, `complexity`, `auto-approved=true` |
| `auto-mode-resume-drift-detected` | Session Resume Step 3 drift 감지 시 | `gap` |
| `auto-mode-resume-handoff-verified` | Session Resume Step 4 완료 시 | `completed_work_match`, `traps_count`, `rephrased_count` |
| `auto-mode-escalated` | 서킷 브레이커 도달/에스컬레이션 | `phase`, `reason`, `retries` |

emit 절차: Read → Edit append (Write 전체 재작성 금지).

### devflow-state.md 화이트리스트

auto 모드가 기록할 수 있는 필드 (이 목록 외 기록 금지):
- `## Current Phase` → INCEPTION | CONSTRUCTION | complete
- `## Current Stage` → 스테이지명 | 스테이지명 (in-progress)
- `## Complexity` → Minimal | Standard | Comprehensive
- `## Selected Approach` → 접근법명
- `## Approved Stages` → 스테이지 목록
- `## Completed Units` → unit 목록
- `## Active Unit` → 현재 unit
- `## Worktree` → branch, path (auto-mode v0.1에서는 worktree 미사용. 향후 확장 시 추가)
- `## Last Updated` → ISO 8601 timestamp (post-tool-file-edit hook이 자동 soft-save하는 필드. auto-mode도 매 Checkpoint에서 명시 갱신)

auto 전용 메타데이터(auto-fix 횟수, 리뷰 라운드 등)는 auto-decision-log에만 기록.

> **devflow-state.md는 advisory cache** (`_shared/devflow-conventions.md` §파일 포맷).
> truth source는 git log + 산출물 디렉토리 + code-plan.md. stale 허용.
> Session Resume 시 git log 교차검증으로 drift를 감지한다 (아래 §Session Resume 참조).

### decision-log 규칙

- **append-only**: 파일 끝에 추가만. 수정 금지.
- **감사 전용**: 실행 중 과거 결정 참조 → devflow-state.md만 읽는다. decision-log를 Read하지 않는다.
- **사후 검토용**: 사용자 명시 요청 시에만 읽는다.

### decision-log 포맷

`skills/aidlc-auto-mode/decision-log-format.md` 참조.

### devflow 전환 시나리오

에스컬레이션 또는 사용자 요청으로 devflow 전환 시:

| 시나리오 | devflow-state 상태 | using-devflow 동작 |
|---------|-------------------|-------------------|
| INCEPTION 중 에스컬레이션 | `Phase: INCEPTION`, `Stage: [현재]` | inception-orch가 해당 stage부터 재개 |
| INCEPTION 확인 후 전환 | `Phase: CONSTRUCTION`, `Stage: (pending)` | construction-orch가 정상 라우팅 |
| CONSTRUCTION 중 에스컬레이션 | `Phase: CONSTRUCTION`, `Stage: [현재]` | construction-orch가 해당 stage부터 재개 |
| 완료 후 전환 | `Phase: complete` | finishing-branch 안내 |

---

## Error Handling

### 글로벌 서킷 브레이커

phase당 총 리트라이 상한 (모든 유형 합산):
- INCEPTION: 최대 5회
- CONSTRUCTION: 최대 8회

상한 도달 시:
```
거의 완성되었지만 자동으로 해결하기 어려운 부분이 있습니다.
완료된 작업: [N]단계 중 [M]단계
A) 하나씩 확인하면서 진행하기 (단계별 모드)
B) 현재 상태 저장 후 나중에 이어하기
```
A → devflow-state 기록 후 using-devflow 안내. B → 상태 보존 후 종료.

### 스테이지 실행 상태 추적

시작: Current Stage = `[name] (in-progress)`. 완료 (Checkpoint): `(in-progress)` 제거.
재개 시 `(in-progress)` 발견 → 산출물 존재 확인 → 있으면 완료 처리, 없으면 재실행.

### 1. Stage 스킬 호출 실패

판정: 산출물 미생성, 기대 패턴 없음, 에러 반환.
→ 1회 자동 재시도 → 실패 시 에스컬레이션. 리트라이 카운터 +1.

### 2. 리뷰어 실패

2a. 타임아웃/파싱 에러: 실패 리뷰어 1회 재시도 → 응답 리뷰어만 판정 (최소 3/5).
    3개 미만 → 전체 재시도 1회 → 에스컬레이션.
2b. 자동수정 3라운드 초과: 에스컬레이션. 리트라이 카운터 +3.

### 3. build-and-test 실패

auto-fix 대상(테스트/린트): 최대 3회 + 전체 재실행.
스킵 대상(빌드/환경/auth): 즉시 에스컬레이션.
3회 소진: 에스컬레이션. 리트라이 카운터 +3.

### 4. greenfield 오판

requirements-analysis에서 기존 코드 참조 발견 시:
→ decision-log 경고 + 사용자 확인 게이트 하이라이트에 포함.

### 5. 고위험 가정 대량 거부

requirements-analysis만 수정된 가정으로 재실행 → 후속 자동 진행. 리트라이 카운터 +1.

### 에스컬레이션 메시지 원칙

- "문제/에러/실패" 대신 → "확인이 필요한 부분"
- "devflow 전환" 대신 → "하나씩 확인하면서 진행하기 (단계별 모드)"
- 항상 진행률: "[N]단계 중 [M]단계 완료"
- 기술 용어 → 괄호 부연 또는 생략

---

## Session Resume

On Activation Step 1에서 재개 선택(A) 시 실행:

1. `devflow-state.md` 읽기 — Current Phase, Current Stage 확인.
2. `session-summary.md` 읽기 — 완료 작업 맥락 복원.
3. **drift 감지 (state.md ↔ git log 교차검증)**: state.md는 advisory cache이므로 stale 가능성 있음. 다음을 비교:
   - **산출물 디렉토리**: `devflow-docs/inception/`, `devflow-docs/construction/`의 실제 파일 ↔ state.md `## Approved Stages` / `## Completed Units`
   - **git log**: `git log --oneline -20`의 commit message 키워드(예: `feat: requirements-analysis`, `feat(unit): X 완료`) ↔ state.md 상태
   - 불일치 시 사용자 게이트 표시:
     ```
     ⚠️ devflow-state.md drift 감지

     state.md 기록: [요약]
     산출물/git log: [요약]

     A) 산출물 우선 신뢰 (state.md 갱신 후 재개)
     B) state.md 우선 신뢰 (산출물은 검증용으로만 참조)
     C) 단계별 모드로 전환 (수동 정리)
     ```
   - `auto-mode-invoked` audit emit 시 `mode=resume`, drift 발견 시 `auto-mode-resume-drift-detected | gap=<short>` 추가 emit.
4. **Handoff Verification (Handoff = Hypothesis, BL-095 Phase 1)**: session-summary.md를 fact가 아닌 hypothesis로 다룬다. 4a Completed Work 검증 / 4b Open Work 재해석 / 4c Traps 존중 — 절차/게이트/audit emit 상세는 `session-resume-protocol.md` §Handoff Verification 참조.
5. **in-progress 교차 검증**: Current Stage에 `(in-progress)` 포함 시:
   - 산출물 파일 존재 → 완료 처리 (Checkpoint 실행), 다음 스테이지로.
   - 산출물 미존재 → 해당 스테이지 처음부터 재실행.
6. Phase에 따라 해당 플로우 진입:
   - `INCEPTION` → Phase 1의 해당 스테이지부터 재개.
   - `CONSTRUCTION` → Phase 2의 해당 스테이지부터 재개.
7. decision-log에 `"session-resumed at [stage]"` 기록.
