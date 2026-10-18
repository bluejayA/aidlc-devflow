# Session Handoff 전략 비교 — 4-Layer 블로그 vs aidlc-devflow

**작성일**: 2026-04-24
**비교 대상**:
- 외부 글: ["Claude 세션 간 Context Handoff: 맥락을 잃지 않는 4계층 전략"](https://codex.epril.com/claude-session-context-handoff-4-layer-strategy) (2026-04-23)
- 내부 분석: [`2026-04-24-session-handoff-mechanism.md`](./2026-04-24-session-handoff-mechanism.md)

**선행 분석**: 본 문서는 위 두 문서를 모두 읽은 독자를 가정한다. 우리 메커니즘의 상세는 선행 분석 참조.

---

## 1. 한 줄 요약

블로그는 **개인 개발자의 일상 워크플로우**를 위한 4계층(in-session → 문서 → 영구 → 오케스트레이션)을 제시하고, 우리는 **AIDLC라는 공식 워크플로우**를 위한 phase-orchestrator + artifact 디렉터리 구조를 가지고 있다.

**개념적으로 우리 시스템은 Tier 3-4를 강하게 구현했지만, Tier 1-2(in-session 관리, handoff 문서 작성술)는 사실상 비어 있다.**

---

## 2. Layer별 매핑

| 블로그 4-Layer | 우리 대응 | 평가 |
|----------------|-----------|------|
| **Tier 1**: In-session (`/rewind`, `/compact focus`, subagent) | ❌ 없음 | 가이드 부재. orchestrator가 무겁게 풀세션을 끌고 감 |
| **Tier 2**: Document & Clear (handoff.md 작성술) | △ `session-summary.md` 존재 | 파일은 있지만 작성 규칙(명령형 금지, 라인번호, 검증지시)은 부재 |
| **Tier 3**: CLAUDE.md + report registry + memory tool | ✅ devflow-docs/ 구조 + Knowledge System 6-type | **우리가 더 정교함** |
| **Tier 4**: SDD + ADR + Git commit + Master-Clone | ✅ aidlc-subagent-driven-development + audit hook | **우리가 가장 강함** |

---

## 3. 우리가 강한 지점 (블로그에 없는 것)

### 3.1 Orchestrator 3계층의 재개 책임 분담
블로그는 "handoff.md를 새 세션에서 읽어라" 한 가지 패턴뿐. 우리는 entry(`using-devflow`) → phase(`construction-orchestrator`) → stage(`executing-plans`)가 각각 다른 깊이로 재개 책임을 분담한다.

### 3.2 Hook 기반 자동 audit log
블로그의 모든 handoff는 **수동 작성**에 의존(세션 끝에 1분 투자). 우리는 `hooks/post-tool-file-edit`이 Edit/Write를 자동 캡처해 `audit.md`에 ISO8601 이벤트로 기록한다 → 수동 작성 누락 시에도 backup이 남는다.

### 3.3 재검증 강제 (Verify-on-Resume)
블로그의 "검증 지시"는 단순 텍스트 한 줄. 우리는 `session-continuity.md §4`에서 **"직전 완료 태스크 재검증 → 실패 시 systematic-debugging 라우팅"** 을 프로토콜화했다.

### 3.4 산출물 디렉터리의 강제성
블로그의 `.claude/reports/{analysis,arch,bugs,...}`는 **권장**. 우리 `devflow-docs/{inception,construction}/{workspace,requirements,units,...}.md`는 스킬이 **강제 생성**한다.

### 3.5 Knowledge System Solution Layer 단독 writer
블로그의 `_registry.md`는 단순 인덱스. 우리는 6-type taxonomy + `aidlc-systematic-debugging`만 STORE 권한 → dead layer 방지를 설계 단계에서 차단했다.

### 3.6 Checkpoint Memorize의 보안 파이프라인
블로그는 redaction 언급 0. 우리 v0.3 spec은 Redaction Filter → Summarizer(Haiku 4.5) → Validator 3단 + AWS keys/내부 IP/PII 마스킹.

### 3.7 Hook race-condition 방지
블로그에는 동시성 고려 없음. 우리는 `devflow-state.md`의 `## Last Updated`만 hook이 soft-save, 구조 섹션은 스킬 전용 → 같은 파일 동시 쓰기 race 회피.

---

## 4. 우리가 약한 지점 (블로그가 강조하는 것)

### 4.1 ⚠ In-session 관리 가이드 부재 (Tier 1)
- `/rewind` (Esc Esc) 활용 패턴 없음
- `/compact focus on X` 처럼 focus 지시 강제 없음
- 토큰 60% 임계점 모니터링 가이드 부재
- → **현재 우리는 컨텍스트 오염을 phase-orchestrator 재시작으로만 해결.** 한 stage 내부의 in-session 관리는 사용자 재량이다.

### 4.2 ⚠ Handoff 문서 작성술 부재 (Tier 2)
블로그가 강조하는 5가지 작성 규칙 중 우리 `session-summary.md`에 명시된 것:

| 규칙 | 우리 상태 |
|------|-----------|
| Open Work는 **상태 서술형** ("X is not yet implemented"), 명령형 금지 | ❌ 명시 없음 |
| 파일 참조는 **라인 번호까지** (`path:L10-L45`) | ❌ 없음 |
| **"Traps to Avoid"** 섹션 (실패 접근 명시) | ❌ "Deferred Stubs"만 있음 |
| **검증 지시** ("이 문서를 코드와 대조해 검증하라") | △ 재검증 프로토콜은 있지만 문서 자체 검증은 없음 |
| **Handoff = hypothesis** 마인드셋 | ❌ 명시 없음 |

→ session-summary.md가 SSOT라면, 작성 규칙도 SSOT 수준으로 명시되어야 한다.

### 4.3 ⚠ CLAUDE.md 중복 회피 지시 부재
블로그는 "Read CLAUDE.md first. Do NOT restate" 지시를 handoff 프롬프트에 강제. 우리는 orchestrator가 매번 같은 컨텍스트를 다시 빌드 → 토큰 낭비 가능성.

### 4.4 ⚠ Master-Clone vs Lead-Specialist 논쟁 미해결
블로그(Shrivu Shankar)는 **Lead-Specialist(custom subagent 다수) 회의론**을 제기한다:
> "main agent가 컨텍스트를 빼앗겨서, 자기 코드 테스트 방법조차 subagent를 호출해야 안다"

우리 SDD는 명시적 unit별 격리 = **Lead-Specialist 방향**. 이 방향이 옳다는 근거(예: AIDLC unit 단위가 충분히 독립적이어서 main 컨텍스트 손실이 문제 안 됨)를 design rationale로 남길 필요가 있다.

### 4.5 ⚠ 빠른 컨텍스트 복원 (`/catchup` 패턴) 없음
블로그는 `/clear` 직후 `/catchup`(현재 git branch 변경 파일 read) 한 줄로 코드 레벨 복원. 우리는 orchestrator가 항상 풀 phase를 다시 로드 → 가벼운 재개가 안 된다.

### 4.6 ⚠ 토큰 예산 가이드 부재
블로그는 "handoff 2,000 토큰 이내, 상세는 reports/로 분리". 우리 `session-summary.md`는 크기 가이드 없음 → 시간이 지나면 비대화 가능.

---

## 5. 블로그가 우리 설계를 검증해주는 지점

- **명령형 금지** = 우리의 **재검증 강제**와 같은 정신 (다음 세션이 맹목 실행하지 않게)
- **report registry on-demand load** = 우리의 **artifact 경로 명시 핸드오프**와 동일 패턴
- **ADR/spec이 handoff 매체** = 우리의 **`workflow-plan.md`, `application-design.md`**가 그 역할
- **commit + ADR 이중 기록** = 우리는 audit.md + 산출물 파일의 이중 기록 (단, commit message 활용은 약함)

---

## 6. 우선순위 액션 아이템

| # | 액션 | 영향 | 난이도 | 백로그 |
|---|------|------|--------|--------|
| 1 | `session-summary.md` 작성 규칙 6항 명시 (명령형금지/라인번호/Traps/검증지시/CLAUDE.md중복회피/2K토큰상한) | 고 | 저 | BL-093 |
| 2 | "Traps to Avoid" 섹션을 `session-summary.md` 표준 템플릿에 추가 | 고 | 저 | BL-094 |
| 3 | `/aidlc:catchup` 같은 경량 재개 스킬 추가 (orchestrator 풀로드 회피) | 중 | 중 | (보류) |
| 4 | In-session 관리 가이드(Tier 1)를 `session-continuity.md`에 추가: /compact focus 강제, 60% 임계점 모니터링 | 중 | 저 | (보류) |
| 5 | Master-Clone vs Lead-Specialist 디자인 결정을 ADR로 문서화 | 중 | 중 | (보류) |
| 6 | "Handoff = hypothesis" 원칙 명문화 (session-summary.md 주장은 항상 코드와 대조) | 고 | 저 | BL-095 |

**1차 등록 기준**: 영향 "고" + 난이도 "저"인 #1, #2, #6 → 백로그 등록. 나머지는 1차 적용 후 효과 측정 후 결정.

---

## 7. 메타 통찰

블로그는 **"개인 개발자가 하루를 1분으로 마무리"** 하는 경량 문화를 제안하고, 우리는 **"AIDLC라는 공식 프로세스를 다세션에 걸쳐 안전하게 진행"** 하는 중량 시스템이다. 두 접근의 본질적 차이:

- **블로그**: 사용자 규율(habit) 중심 — 도구는 markdown + slash command만
- **우리**: 시스템 강제(orchestrator + hook) 중심 — 사용자가 빠뜨려도 audit.md가 남음

→ 우리가 비어 있는 부분은 **시스템 자동화로 해결할 게 아니라 작성 규칙(rule) / 문화로 채워야** 한다. 특히 #1, #2, #6은 "session-summary.md 표준 템플릿" 한 번 업데이트로 끝나는 일이라 ROI가 매우 높다.

---

## 8. 참조

- 외부: <https://codex.epril.com/claude-session-context-handoff-4-layer-strategy>
- 내부: `docs/analysis/2026-04-24-session-handoff-mechanism.md`
- 내부: `skills/_shared/patterns/session-continuity.md`
- 내부: `devflow-docs/session-summary.md` (수정 대상)
