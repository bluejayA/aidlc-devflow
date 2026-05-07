# aidlc-devflow 진화 타임라인 — 내부 워크샵 자료

**작성일**: 2026-05-06
**대상**: 내부 워크샵 — aidlc 플러그인 진화 과정 공유 (Jay 1인 운영 경험)
**범위**: 2026-03-10 (v0.1) ~ 2026-04-29 (v1.12.0) — 약 7주, 441 commits, 200+ PR/issues
**작성 의도**: "어떤 문제를 만났고, 어떤 결정을 내렸고, 무엇을 배웠는가"의 시간순 회고

---

## 한 줄 요약

> **단편 스킬 22개 → orchestrator-centric AIDLC 워크플로우 → 자동화 가드레일 → 외부 AI 협업(Codex) → 지식 시스템 → handoff 가설 모델 → "측정에서 사용 경험으로" frame 전환**으로 진화. 핵심 학습은 "**자동화는 가드레일과 분리(separation)로 산다, 측정으로 가치를 증명하려는 시도는 yak shaving이 된다**"이다.

---

## Phase 0 — 출발점 (2026-03-10, v0.1)

### 문제
- AIDLC 방법론을 Claude Code 위에서 실행 가능한 형태로 구현하고 싶다.
- superpowers 패턴은 단편 스킬의 모음일 뿐, 워크플로우 강제력이 없다.

### 적용
- **Phase 1**: AIDLC 핵심 스테이지 10개 (workspace-detection, requirements-analysis, workflow-planning, application-design, units-generation, code-generation, build-and-test, executing-plans, subagent-driven-development, writing-plans).
- **Phase 2**: 일상 개발 도구 12개 (TDD, code review, parallel agents, worktrees, brainstorming 등 superpowers 흡수).
- **B-plan(Orchestrator-Centric) 채택**: `using-devflow` 진입점이 phase를 라우팅, stage skill은 "순수 실행자"로 재작성.

### 인사이트
- 스킬을 "단편의 합"으로 늘어놓으면 사용자가 어떤 스킬을 언제 호출할지 모른다 → **단일 진입점 + phase orchestrator**가 필수.
- C안(스킬 자율 호출) vs B안(orchestrator) 비교에서 B안 채택. 자율 호출은 SSoT 충돌·게이트 누락 위험이 너무 컸다.
- 산출물 포맷은 MD가 기본, JSON은 정형 파싱 필요할 때만. 이 결정이 이후 모든 산출물 일관성의 토대.

---

## Phase 1 — 기반 체계 구축 (2026-03-17, v1.0.0)

### 문제
- 코드 리뷰를 "받는 스킬"만 있고 "요청하는 스킬"이 없다 — 리뷰 진입점 부재.
- 서브에이전트에 세션 히스토리 통째로 넘겨 토큰 낭비.
- 매 세션 사용자가 수동으로 devflow를 호출.
- dev-playbook의 좋은 패턴(질문 가이드, 기술 스택 카탈로그)이 흡수되지 않음.

### 적용
- **#8 requesting-code-review** — 단일 진입점, Spec → Quality 2단계.
- **#9 컨텍스트 격리 원칙** — conventions에 명시 ("태스크에 필요한 최소 컨텍스트만").
- **#10 SessionStart hook** — devflow 자동 활성화 + 안내.
- **#11 Brainstorming Spec Review Loop** — 설계 자동 리뷰 + 수정-재리뷰 (max 5회).
- **#12, #13** dev-playbook 패턴 흡수 (question-format-guide, tech-stack-defaults, ASCII 다이어그램, 엔터프라이즈 체크리스트).
- **#14 Instruction Priority Hierarchy** — "사용자 지시 > 스킬 규칙 > 기본 동작" 명문화.
- **#15** Phase 1 테스트 인프라 (validate-skills.sh) — frontmatter 구조 검증.
- **#16** writing-skills 보조 자료 — pattern-catalog + persuasion-principles.

### 인사이트
- **외부 패턴 흡수의 핵심은 "흡수 후에도 SSoT가 깨지지 않는 구조"**. dev-playbook 패턴을 그대로 가져오는 게 아니라 conventions로 추출해 단일 출처로 만든 것이 핵심.
- **persuasion-principles** 도입 — 에이전트가 규율을 우회하려는 합리화 패턴(skill 우회, 게이트 무시 등)을 미리 정의해 차단.
- 우선순위 게이트(#14)는 사용자가 항상 최종 결정권을 가진다는 명시적 계약. 이후 모든 자동화의 안전판.

---

## Phase 2 — 테스트 인프라 + 외부 AI 도입 (2026-03-18, v1.1.0)

### 문제
- 28개 스킬, 테스트 전무. 스킬을 수정하면 다른 스킬에 어떤 영향이 가는지 모른다.
- 같은 모델(Claude)로 리뷰하면 같은 종류의 맹점이 남는다.
- Brownfield 분석이 "1-depth 디렉토리 트리"만 봐서 컨텍스트 빈약.

### 적용
- **#29 L1/L2/L3 테스트 피라미드** — SKILL.md를 상태 머신 명세로 취급:
  - L1: 데드엔드/순환 탐지
  - L2: 라우팅 시뮬레이션
  - L3: 스텝 순서 검증
- **#33** 테스트 리팩토링 — 시뮬레이션 엔진 모듈 분리, fixture 통합, 95개 테스트.
- **#30/31/32 agent-council 인프라** — Codex/Gemini 외부 AI 리뷰 (CLI 자동 감지, risk-score 기반 모드 자동 선택).
- **#42 Brownfield 분석 강화** — git 핫스팟, 기존 문서 감지, 핵심 파일 샘플링.
- **#43 기술 스택 정책 모드** (open/guided/strict) — 조직 표준 강제력.

### 인사이트
- **"SKILL.md = 상태 머신 명세"** 라는 관점 전환이 정적 검증의 문을 열었다. 코드 실행 없이 흐름 오류를 잡는다.
- **다른 모델로 리뷰 = 같은 모델 맹점 보완**. agent-council의 본질적 가치는 다수결이 아니라 "관점 다양성".
- Brownfield는 "디렉토리 트리"가 아니라 "활동 핫스팟 + 기존 문서 + 샘플 코드"의 3축으로 봐야 진단이 의미 있다.

---

## Phase 3 — 스킬 품질 전면 점검 + GitHub Flow (2026-03-19, v1.1.1)

### 문제
- 27개 스킬 전수 검사에서 명확한 버그 5건 발견 (`git add -p` 사용, CSO 위반 등).
- orchestrator-only 스킬에는 어떤 섹션이 필수인지 기준 없음.
- 한국어 사용자가 "디버깅해줘" 같은 발화로 트리거 안 됨.

### 적용
- **#47~52 S1~S6 셀프 리뷰** — 즉시 버그 수정 → 기준 정립 → 미완성 보강 → Pipeline 게이트 → user-invocable 보강 → 한국어 키워드 일괄 추가.
- **#45 구조 디자인 패턴 가이드** — Pipeline / Decision Tree / Iterative Refinement / Template Method / Composite (행동 패턴과 직교).
- **#25 GitHub Flow 옵트인** — INCEPTION 시작 시 이슈 자동 생성, 스테이지별 코멘트, PR 자동화.

### 인사이트
- **스킬에도 "구조" 패턴이 있다** — 행동 패턴(TDD, Gate, Review Loop)과 직교하는 5가지 구조 패턴. 이후 신규 스킬 설계 시 결정 트리로 적용.
- **invoke_mode별 필수 섹션 분기** (orchestrator-only vs user-invocable)는 "스킬 종류에 따른 책임 분리" — 같은 잣대로 모두 평가하지 않는다.
- 한국어 키워드는 description-level 트리거. body는 영어로 두어도 무방 → SKILL.md 언어 3원칙의 시발점.

---

## Phase 4 — 리뷰 체계 고도화 (2026-03-23, v1.2.0)

### 문제
- 2-stage 리뷰(Spec → Quality)만으로는 보안/유지보수성 관점이 누락.
- 게이트가 A/B 선택지만 있어 "계획 수정하고 싶어" 같은 자유 발화 처리 불가.
- Anthropic 공식 `skill-creator` 플러그인과 우리 `writing-skills`가 무엇이 다른지 정리 안 됨.

### 적용
- **#62 4-stage 코드 리뷰** — Standard에서 Security 추가(3-stage), Comprehensive에서 Maintainability까지(4-stage).
- **#64 4-stage × Council 직교** 명시 — Council 모드에서도 4-stage 관점 유지.
- **#57 글로벌 인터럽트 핸들러** — 모든 orchestrator 게이트에 자유 발화 → 의도 분류 → 라우팅 탈출 경로.
- **#56 skill-creator 통합** — writing-skills의 REFACTOR 단계에 정량적 벤치마크 + description 최적화 게이트.
- **#58 스킬 설계 패턴 외부 공개** — _shared/patterns 구조 재구성.
- **#67 session-summary 조기 업데이트** — 스테이지 내부 맥락 보존.

### 인사이트
- **리뷰는 두 직교 차원**: (1) 관점 커버리지 (Spec/Quality/Security/Maintainability), (2) 다모델 편향 보완 (Claude/Codex/Gemini). 두 차원을 혼동하면 리뷰 ROI 분석이 깨진다.
- **인터럽트 핸들러**는 게이트 UX의 "탈출 밸브" — A/B 선택지로 안 끝나는 사용자 의도를 자유 발화로 라우팅. 이게 없으면 사용자는 강제 리부트로 우회한다.
- aidlc(설계) + skill-creator(검증) 조합이 단독 사용보다 강함. **외부 공식 자산은 "통합 지점"을 잡아 흡수**하는 게 답이다.

---

## Phase 5 — 워크플로우 연결 (2026-03-24~25, v1.3.x ~ v1.4.0)

### 문제
- Agent Teams(R3) 모드가 빠짐 — 협업 시뮬레이션 불가.
- Brownfield INCEPTION이 reverse-engineering과 연동되지 않음.
- `tech-stack-defaults.md` 파일은 있지만 어떤 스킬에서도 참조하지 않음 — **dead asset**.

### 적용
- **#69 R3(Agent Teams)** — 협업 코드 리뷰.
- **inception-orchestrator → reverse-engineering 연동** — Brownfield 진입 시 가용성 검사 후 자동 호출.
- **#77 tech-stack 워크플로우 연동** — workspace-detection (Step 2b: CLAUDE.md 감지), requirements-analysis (Step 2b: 조건부 선택), 카탈로그/인덱스 분리, **사용자 프리셋** ("이대로 사용? Y/n").

### 인사이트
- **"기능 추가 ≠ 사용 경로 연결"** — 자산 파일이 있어도 워크플로우에 enter 지점이 없으면 dead state. 이후 모든 신규 자산은 "어느 스킬에서 어떻게 호출되는가"를 먼저 정의.
- 사용자 프리셋은 반복 입력 토큰 절감 + 의사결정 피로 감소 — 양쪽에서 ROI.

---

## Phase 6 — 산출물 정책 + Codex 단일화 (2026-03-26~28, v1.4.1 ~ v1.5.0)

### 문제
- INCEPTION 산출물 재호출 시 기존 내용을 덮어씀 — 사용자 작업 손실.
- 아카이브 정책이 일관성 없어 산출물이 흩어짐.
- agent-council의 Gemini를 운영 안 함 — 외부 AI 다수 유지 비용 과다.

### 적용
- **#80 UPDATE 모드** — INCEPTION 재호출 시 보존.
- **#81 아카이브 정책 개선** — 디렉토리 분리 + 산출물 처리 게이트.
- **Codex 단일 외부 AI 마이그레이션** — Gemini 운영 중단, codex-migration-guide + port helper script.
- **#86 리뷰 서브에이전트 워크트리 접근/도구 권한 제한** — 보안 가드.

### 인사이트
- **외부 AI는 "적은 수로 깊게"** — Council 다수 모델 운영은 1인 운영 부담이 큼. Codex 단일 + 깊이가 ROI 우수.
- 산출물 덮어쓰기 같은 "데이터 손실 가능 동작"은 **명시적 모드 분기**(CREATE/UPDATE)로만 허용 — 이후 모든 destructive 동작 default = preserve.

---

## Phase 7 — Council 인사이트 흡수 + Distrust by Default (2026-03-30~31, v1.5.0)

### 문제
- Anthropic harness design 인사이트 13건 미흡수 (Verification Contract, Self-Healing Loop, Distrust by Default 등).
- 우리 시스템은 "리뷰는 R 옵션" — "모델이 잘 할 것" 가정에 의존.
- SKILL.md 언어 일관성 없음 (한/영 혼재).

### 적용
- **#87/88 Verification Contract + Self-Healing Loop** — 자동 평가 루프 (max retry N=3, 루브릭 임계치, diff 급증 시 게이트 전환).
- **#89/90 SDD Default + 정량 루브릭** — Standard 이상에서 SDD가 기본.
- **#91 Distrust by Default** — Standard 이상 코드 리뷰 자동 실행.
- **#96 Knowledge Compounding** 초안 — 솔루션 누적 구조 설계.
- **SKILL.md 언어 3원칙** — description 한글, body 현행 유지(신규 영어), 출력 언어 명시.

### 인사이트
- **Gate(주관적 판단) + Auto-Loop(객관적 검증) 하이브리드** 가 자동화의 정답. Lint/타입체크/유닛테스트 = Auto-Loop, 아키텍처/UX/보안결정 = Gate.
- **"검증 실패 전까지 불신"** 이 자동화의 전제. 옵션 R로 두면 사용자가 게이트를 누락한다 → default ON.
- N회 실패 시 사용자 게이트로 자동 escalation — 무한 자동수정 = 비용/시간 폭발.

---

## Phase 8 — P1 Sprint: 게이트 UX + 가드레일 + 백로그 재설계 (2026-04-01~02, v1.6.0 ~ v1.7.0)

### 문제
- 게이트 텍스트 모호 ("S = 스킵"이 무엇을 의미하는지 불명).
- 백로그가 GitHub 이슈에만 있어 다음 세션 재개 시 매번 검색.
- 디버깅 루프/재검증이 무한 반복 가능 — 사용자 시간 낭비.
- tech-stack 카탈로그 부재 시 처리 경로 없음.
- INCEPTION 산출물에 Worktree 필드 누락 — Construction 진입 시 정합성 깨짐.

### 적용
- **#104~106 게이트 UX 3건** — "S = 무시하고 진행 (audit 기록됨)" 명시.
- **#127 백로그 재설계** — `devflow-docs/backlog.md` 기반 + 선택적 GitHub 연동.
- **#108 재검증 횟수 제한** (2회 초과 시 escalation), **#115 디버깅 루프 소프트 리밋** (3회).
- **#119 오류 복구 폴백** — tech-stack 카탈로그 부재, 워크트리 생성 실패.
- **#129/130 devflow-state 정합성** — Worktree 필드 + 템플릿 필드.
- **#112 NFR 도메인 프리셋** 가이드.

### 인사이트
- **"강제력 있는 가드레일"** 이 자동화 안정성의 핵심. 무한 재시도 = 비용 폭발이자 사용자 신뢰 손실.
- **백로그는 SSoT 1개**가 답. GitHub 이슈를 옵션으로 두되, devflow-docs를 단일 출처로.
- 게이트 텍스트는 "**선택지 + 결과**" 둘 다 명시 — "스킵"은 모호, "무시하고 진행 (audit 기록)"은 명확.

---

## Phase 9 — Auto Mode (2026-04-02~03, v1.8.0)

### 문제
- 초보자가 devflow를 사용하기 어렵다 — A/B 게이팅이 무겁고, 매번 stage를 인지해야 한다.
- "그냥 알아서 만들어줘"라는 요청을 처리할 진입점이 없다.

### 적용
- **#141 aidlc-auto-mode 스킬** — 단일 SKILL.md ~500줄, greenfield 전용, 자동 진행.
  - 기존 SKILL.md 무수정으로 옵트인.
  - 자동수정 루프 5회 → 3회 축소 (자율 모드는 빨리 escalate).
  - 분리 비용 0 (파일 1개 삭제 + plugin.json 1줄 제거).
- **Layer 1 verify.sh** + **Layer 2 시나리오 3건**.

### 인사이트
- **"초보자 모드"는 기존 시스템과 분리(separation)되어야 한다** — 통합하면 두 모드의 결정 분기가 SKILL.md를 비대하게 만든다 (이 결정이 Phase 14에서 다시 확인됨).
- 회수 비용을 0으로 두면 실험 부담이 없다.
- 트리거 키워드를 "auto"/"자동" 명시로 제한 → using-devflow와 충돌 회피.

---

## Phase 10 — 효율 + Stub Blind Spot + 게이트 단순화 (2026-04-08~10, v1.9.0)

### 문제
- INCEPTION에 셀프리뷰 부재 — 산출물 정합성 검증 누락.
- 코드 리뷰 R1/R2/R3 타임아웃 빈번.
- Codex가 agent-council에 통합되지 않음 — 자동 병렬 호출 시 통제 불가.
- **Brownfield Stub Blind Spot**: 기존 코드의 `"not yet implemented"` stub을 implementer가 인지 못함, Mock 테스트가 stub을 은폐.
- 게이트 종류가 너무 많아 자동/수동 경계 모호.

### 적용
- **#143/144 INCEPTION 셀프리뷰 + 서브에이전트 온보딩 스킵**.
- **리뷰 R1 병렬화** + **Codex 사후 수동 실행 가이드**.
- **BL-082 Phase 1 Stub Blind Spot**:
  - construction-orchestrator: 사전 Stub Scan (brownfield only).
  - build-and-test: 사후 Stub 잔존 검증 게이트.
- **게이트 3등급 분류** — 자동 진행 / 경량 확인 / 정식 게이트.
- **개발 환경 설정 게이트** 3단계 → 1단계, **NFR-Requirements** 이중 → 단일 게이트.
- **review-gate 공통 패턴 추출** — 3곳 중복 제거.
- **Revalidation 인라인 로직 → session-continuity 패턴 참조**.

### 인사이트
- **SDD + Mock의 함정**: SDD가 강한 격리를 제공하지만 그 자체로 "이미 정의됨 = 구현됨"이라는 착각을 유발한다. Mock 테스트는 stub을 은폐. → **사전 스캔 + 사후 검증** 양면 가드 필수.
- 이는 단일 사례가 아니라 **공식 검증 시스템(SDD)이 만드는 새로운 맹점**의 패턴. 이후 nexttui 실전에서도 동일 사례 발견.
- 게이트는 "있는 게 좋다"가 아니라 "**의사결정이 필요한 곳에만 있어야**" — 자동 진행 가능한 곳에 게이트를 두면 사용자 피로도 ↑.
- **공통 패턴 추출**(review-gate, session-continuity)은 정합성 비용을 1/N로 줄인다.

---

## Phase 11 — Knowledge System Phase 1 (2026-04-13~14, v1.10.0)

### 문제
- devflow-docs/skill에 6-type taxonomy 없음 — Decision/Solution/Pattern/Skill/Evidence/SessionState 분류 부재.
- **Solution layer가 dead state** — 생성/저장 owner 없음.
- audit이 수동 기록 — 누락 위험.

### 적용
- **6-type frontmatter** 일괄 적용 — Skill 31개 + Pattern 33개.
- **Solution layer STORE 단일 owner** — `aidlc-systematic-debugging`만 STORE 권한 (dead layer 차단).
- **post-tool-file-edit hook (L1 auto ingest)** — Edit/Write 자동 캡처 → audit.md ISO8601 기록.
- **DEVFLOW_HOOK_DISABLED kill switch** + **rollback guide 5-level**.
- hook race-condition 회피 — `## Last Updated` 필드만 hook이 soft-save, 구조 섹션은 스킬 전용.

### 인사이트
- **"Dead layer 방지의 본질은 단일 writer를 설계 단계에서 박는 것"** — 누구나 쓸 수 있게 두면 아무도 안 쓴다.
- **Hook은 "최소 침습"** — race condition 회피를 위해 어느 필드를 누가 쓸지 명시. 구조 섹션 = skill, 메타 = hook.
- Phase 2 baseline + rollback guide를 Phase 1과 함께 작성 — **변경의 회수 경로를 사전에 마련**.

---

## Phase 12 — Repo 분리 + AI 프로젝트 착수 도구 (2026-04-15~17)

### 문제
- `deployment-prep` 스킬이 aidlc 내에 있을 이유 없음 — JVM/k8s 특화 도메인.
- AI 프로젝트 착수 문서가 일반 SaaS만 가정 — 사내툴/데이터/인프라/빌링 사례 부재.

### 적용
- **BL-031 deployment-prep 졸업** → `bluejayA/devflow-k8s-deploy` 별도 repo, 이름 변경.
- **AI 프로젝트 초안 v2/v2.1** — 3-persona 리뷰 + 3-scenario 검증 12건.
- **도메인 템플릿 카드 5종** — A SaaS / B 사내 / C 데이터 / D 인프라 / E 빌링.
- **project-bootstrap v0.1** — 착수 문서 작성 스킬.

### 인사이트
- **"한 플러그인이 모든 걸 다 하면 안 된다"** — 명확히 독립 가능한 도메인은 졸업. plugin은 building block, 운영 정책은 프로젝트 auto-memory에 위임.
- 시나리오 검증은 1개로는 부족. **3-persona × 3-scenario = 9 cell 검증**으로 일반성 확보.

---

## Phase 13 — Memory Sync + Handoff = Hypothesis (2026-04-20~24, v1.11.x)

### 문제
- auto-memory와 devflow-docs 동기화 갭 — 두 SSoT가 drift.
- 외부 4-Layer 블로그 분석에서 우리 약점 노출:
  - **Tier 1 (in-session) 가이드 부재** — `/compact focus`, 토큰 임계점 모니터링 없음.
  - **Tier 2 (handoff 작성술) 부재** — session-summary 작성 규칙 없음.

### 적용
- **BL-092 Memory Sync Reconciliation MVP**.
- **BL-093 session-summary 작성 규칙 6항**:
  1. Open Work는 상태 서술형 (명령형 금지)
  2. 파일 참조는 라인 번호까지
  3. Traps to Avoid 섹션
  4. 검증 지시 ("이 문서를 코드와 대조해 검증")
  5. CLAUDE.md 중복 회피
  6. 2K 토큰 상한
- **BL-094 Traps to Avoid 섹션** — 표준 템플릿 + orchestrator 회수 절차.
- **BL-095 "Handoff = hypothesis" 원칙** 명문화 — session-summary의 모든 주장은 다음 세션에서 검증되어야 할 가설.

### 인사이트
- **우리는 Tier 3-4(공식 산출물/SDD/Audit)는 강하지만 Tier 1-2(in-session, handoff 작성술)가 비어있었다** — 외부 비교 없이는 자체 진단 불가.
- **"Handoff = 가설"**: 다음 세션은 session-summary를 사실로 신뢰하지 않고 코드와 대조 검증한다 → 이전 세션의 잘못된 추정이 다음 세션을 오염시키지 않는다.
- 우선순위 결정 — "영향 고 + 난이도 저" 3건만 1차 등록 (#1/#2/#6), 나머지는 4주 관측 후 재평가.

---

## Phase 14 — Frame 전환: 측정 → 사용 경험 + 외부 분리 패턴 (2026-04-28~29, v1.12.0)

### 문제
- **Phase 2 측정 인프라 자체가 yak shaving이 됨** — n=1 환경에서 시간/인과 분리 한계로 "devflow 가치"를 시스템 측정으로 증명 불가.
- mid-cycle pause가 5단계로 비대 (state 검색/저장/audit/commit/요약 출력 등).
- **auto-mode SKILL.md가 정합 fix마다 한도 무한 상향**: v1.8.0(489) → BL-100(526) → BL-102(543) → ...
- E2E 점검 시 7건 결함 (audit emit 비표준, state.md 정합 깨짐, session-summary 6항 자동 기록 누락 등).

### 적용
- **frame 전환 — 시스템 측정 stop**:
  - Knowledge System Phase 2 측정 인프라 작업 중단.
  - BL-097 close, BL-098 scope 축소, BL-099 close, T+28 routine disabled.
  - 가치 검증을 "**사용 경험 회고**"로 전환.
- **mid-cycle pause 5단계 → 2단계 단순화**:
  - 정보 분해 (unique / cache / derive) — 5단계 중 3단계가 derived였음.
  - state.md = advisory cache 격하 (자연 발화 시에만 갱신).
  - **코드 변경 0** (구조 재정의만으로 압축).
- **BL-100~104 auto-mode E2E fix** — audit emit 표준화, state.md advisory 정합, session-summary 6항 + Traps/Commit/Last Updated 자동 기록, Session Resume Handoff=Hypothesis 검증 절차.
- **BL-105 SKILL.md 외부 분리 패턴**:
  - "한도 무한 상향 안티패턴" 명시 차단.
  - 정합성 fix는 외부 파일 분리(`_shared/patterns` 또는 부속 파일)로 처리.
- **BL-106 skill-reviewer + Codex adversarial HIGH 5건 통합 fix**:
  - verify.sh 외부 분리 무결성 검증 3종 (8a 파일 존재 / 8b section anchor / 8c **참조 깊이 1단계 가드** — 부속 파일 간 cross-reference 차단).

### 인사이트
- **시스템 측정으로 가치 증명은 불가능했다** — n=1, 시간 영향 분리 불가, 인과 분리 불가의 3중 한계. proxy를 정교화할수록 yak shaving이 됨.
- **"한도 상향" 욕구 = yak shaving 신호**: SKILL.md 한도를 4번 상향한 것은 외부 분리를 회피한 결과. 외부 파일로 빼면 핵심은 가벼워지고 fix는 비핵심 파일로.
- **정보 분해(unique/cache/derive)** 가 단순화의 강력한 도구 — 5단계를 2단계로 압축하는 데 코드 변경 0. **"단순화 가능 부분 식별"** 이 핵심 스킬.
- **참조 깊이 1단계 가드**: 부속 파일끼리 다시 cross-reference하면 자기완결성이 깨진다 → SKILL → 부속 → 또다른 부속 체인 차단.
- **"이슈 먼저, 데이터 나중"은 confirmation bias** — Phase 2 측정 사이클을 앞당기지 않는다. 데이터가 먼저 쌓이고 가설이 뒤따른다.

---

## 누적 학습 — 메타 인사이트 7가지

### 1. Orchestrator-Centric > 자율 호출
스킬을 단편의 합으로 두면 SSoT 충돌·게이트 누락. **단일 진입점 + phase orchestrator + stage 순수 실행자** 가 답.

### 2. 자동화는 가드레일과 함께 산다
"리뷰 R 옵션" → "Distrust by Default + Self-Healing Loop + N회 escalation". **default ON + 무한 루프 차단** 이 안정성 두 축.

### 3. 외부 AI는 적은 수로 깊게
Council 다수 모델 → Codex 단일 + 사후 수동 실행. **운영 비용/통제권**과 **관점 다양성**의 트레이드오프에서 후자만 챙기고 전자는 줄임.

### 4. Dead state 차단은 설계 단계에서
- tech-stack-defaults.md (Phase 5) — 워크플로우 미연동 → 사용 안 됨.
- Solution layer (Phase 11) — owner 미정 → 채워지지 않음.
→ **사용 경로 + 단일 writer**를 자산 도입과 동시에 정의.

### 5. SDD가 만드는 새 맹점
SDD/Mock은 강한 격리지만 "이미 정의됨 = 구현됨" 착각, Mock이 stub 은폐. **사전 스캔 + 사후 검증** 양면 가드 필수.

### 6. Handoff는 가설이다
session-summary는 다음 세션에 사실로 전달되는 게 아니라 **검증 대상 가설로 전달**된다. 이전 세션의 잘못된 추정이 다음 세션을 오염시키지 않게 하는 게 핵심.

### 7. 측정 욕구를 의심하라
"가치 증명 인프라"는 n=1 환경에서 yak shaving이 된다. **시스템 측정 → 사용 경험 회고**로의 frame 전환은 후퇴가 아니라 자원 재할당. 측정으로 증명할 수 없는 가치가 있다는 인정.

---

## 부록 A — 버전별 핵심 변화

| 버전 | 날짜 | 핵심 변화 |
|------|------|---------|
| v0.1 (b-plan) | 03-10 | 22 skill + orchestrator-centric |
| v1.0.0 | 03-17 | 기반 체계 (review/conventions/hooks) |
| v1.1.0 | 03-18 | L1/L2/L3 테스트 + agent-council |
| v1.1.1 | 03-19 | 27 skill 셀프 리뷰 + GitHub Flow |
| v1.2.0 | 03-23 | 4-stage 리뷰 + 인터럽트 핸들러 + skill-creator 통합 |
| v1.3.x | 03-24 | R3 Agent Teams + Brownfield 연동 |
| v1.4.0 | 03-25 | tech-stack 워크플로우 연동 |
| v1.5.0 | 03-31 | Verification Contract + Distrust by Default |
| v1.6.0 | 04-01 | P1 Sprint (게이트 UX + 가드레일) |
| v1.7.0 | 04-02 | 백로그 재설계 + 오류 복구 |
| v1.8.0 | 04-03 | Auto Mode |
| v1.9.0 | 04-10 | Stub Blind Spot + 게이트 3등급 |
| v1.10.0 | 04-14 | Knowledge System Phase 1 (6-type, hook) |
| v1.11.x | 04-24 | Memory Sync + session-summary 6항 + Handoff=Hypothesis |
| v1.12.0 | 04-29 | Frame 전환 + mid-cycle pause 단순화 + 외부 분리 패턴 |

---

## 부록 B — 진행 중 / 보류된 의사결정

- **BL-042** (Layer 2 행동 테스트 — LLM 기반 검증): 실행 ROI 판단 보류. 정의만 추적, 실행은 중대 변경 시만.
- **BL-044/045** (Multi-Unit Construction Agent Teams): 설계 단계.
- **BL-052** (Playwright E2E 비대칭 도구): 평가기 강화 미실행.
- **BL-084** (Mock vs Real adapter 갭): BL-082 Phase 2.
- **BL-096** (in-session 관리 가이드 Tier 1): 4주 관측 후 재평가 (~2026-05-22).
- **BL-107** (auto-mode 한도 정책 재검토): BL-106에서 한도 520 sustainable 자리 약함 입증, 차기 결정 필요.

---

## 워크샵 토론 거리

1. **Phase 14의 frame 전환을 더 일찍 했어야 했나?** Phase 11 Knowledge System Phase 1 baseline 설정 시점에 이미 측정의 한계는 보였다. n=1 / 시간 분리 불가는 사전에 인지 가능했나?
2. **외부 분리 패턴(BL-105)을 더 일찍 인지하지 못한 이유**: SKILL.md 한도를 4번 상향하는 동안 왜 yak shaving 신호로 못 봤는가? "지금 한 번만 더"의 함정.
3. **agent-council 다수 모델 운영 비용**: Codex 단일화는 정답이었나? 향후 Gemini 재도입 조건은?
4. **Handoff = Hypothesis가 모든 다세션 시스템에 일반화되는가?** session-summary뿐 아니라 PR description, design doc 등에도 적용 가능한 메타 원칙인지.
5. **"단편 스킬 → orchestrator-centric"의 일반화**: 다른 도메인(예: 데이터 파이프라인 도구) 플러그인에도 같은 패턴이 적용 가능한가?
