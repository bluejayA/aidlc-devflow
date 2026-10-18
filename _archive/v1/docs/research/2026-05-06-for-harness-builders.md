# AI 개발 하네스를 만들려는 당신에게 — aidlc-devflow 소개

**대상**: Claude Code, Cursor, Aider, Cline 같은 AI 코딩 도구 위에 **자체 개발 워크플로우 시스템(=하네스)을 구축하려는 빌더/아키텍트**.
**작성일**: 2026-05-06
**기준 버전**: aidlc-devflow v1.12.0 (28 skills + 3 utils, 7주간 운영)

---

## 1. 이 글이 답하는 질문

> "AI 코딩 도구는 이미 있다. 그 위에 왜 굳이 하네스(harness)를 만드는가?"
> "만든다면 어떤 결정을 먼저 해야 하는가?"
> "어떤 함정이 기다리는가?"

aidlc-devflow는 위 질문에 7주간 시행착오로 답한 결과물이다. 이 글은 우리가 내린 **5가지 핵심 설계 결정과 그 근거**, 그리고 **빌더가 빠지기 쉬운 5가지 함정**을 공유한다.

---

## 2. aidlc-devflow는 무엇인가

한 줄: **AI-DLC(AI-Driven Development Life Cycle) 방법론을 Claude Code 위에서 강제 실행하는 오케스트레이터-중심 워크플로우 플러그인**.

```
사용자: "사용자 인증 기능을 만들어줘"
   ↓
[aidlc-using-devflow] (Entry Orchestrator)
   ↓
[INCEPTION Phase] workspace → requirements → planning → (조건부: user-stories, NFR, design, units)
   ↓
[CONSTRUCTION Phase] worktree → code-plan → 승인 → TDD generate → build & test → review
   ↓
완성된 코드 + 모든 결정의 문서화된 흔적 (devflow-docs/)
```

**구성 요소**
- **3계층 orchestrator**: Entry(`using-devflow`) → Phase(`inception-orchestrator`, `construction-orchestrator`) → Stage(순수 실행자 14개).
- **개발 품질 도구 7개**: TDD, debugging, verification, code review (4-stage), parallel agents 등.
- **3-Layer 정적 테스트**: SKILL.md를 상태 머신 명세로 취급, 273 테스트로 흐름 오류를 0토큰에 잡음.
- **Knowledge System**: 6-type taxonomy (Decision/Solution/Pattern/Skill/Evidence/SessionState) + L1 auto ingest hook.
- **Auto Mode (옵트인)**: 초보자용 완전 자동 모드, 분리 비용 0 (단일 SKILL.md 삭제로 완전 회수).

---

## 3. 왜 하네스가 필요한가 — AI 코딩 도구의 4가지 빈틈

직접 사용해보면 보이는 것:

### 3.1 절차 강제력 부재
"테스트 먼저 써줘"는 1회 지시. 다음 요청에서 다시 잊는다. **TDD를 "옵션 R"이 아니라 "default ON"으로 만드는 강제 메커니즘**이 필요하다.

### 3.2 세션 단절 시 맥락 휘발
대화가 끊기면 "어디까지 했더라?"부터 시작. 사람이 다시 설명한다 → 같은 토큰을 두 번 낸다 + 잘못 설명할 위험.

### 3.3 자기 검증 회피
"코드 작성했습니다" → 실제로 빌드/테스트 안 돌림. 이를 강제할 게이트가 도구에 없다.

### 3.4 결정의 흔적 부재
왜 이 라이브러리를 선택했나? 왜 이 구조로 만들었나? 한 달 뒤 본인도 모른다. PR 메시지로는 부족하다.

→ **하네스의 본질은 "강제력 + 연속성 + 자기 검증 + 결정 흔적"의 4가지 가드레일**이다.

---

## 4. 5가지 핵심 설계 결정 (만들 때 가장 먼저 고민해야 할 것)

### 결정 1: Orchestrator-Centric vs 자율 호출

**선택**: Orchestrator-Centric.

**대안과 트레이드오프**:
- **A안 (자율 호출)**: 각 스킬이 description으로 트리거, AI가 자율 판단. → SSoT 충돌, 게이트 누락, 어떤 스킬이 호출됐는지 사용자가 모름.
- **B안 (Orchestrator)**: 단일 진입점이 phase를 라우팅, stage skill은 순수 실행자. → 흐름 추적 가능, 게이트 통합 관리, 새 단계 추가 시 라우팅 테이블만 수정.

**근거**: AI가 자율 판단하는 영역이 넓을수록 "어디서 무엇이 결정됐는지" 추적 비용이 폭증한다. 1인 운영 환경에서 자율성은 비용이지 자산이 아니다.

**적용 패턴**:
```
Entry Orchestrator       — "어느 phase로 갈 것인가" (1개)
  ↓
Phase Orchestrator       — "이 phase의 어느 stage로 갈 것인가" (2개)
  ↓
Stage Skills             — "주어진 입력으로 산출물 생성" (14개, 순수 실행자)
```

**빌더에게**: 자율 호출 모델로 시작했다가 6개 스킬쯤에서 라우팅이 깨진다. 처음부터 orchestrator를 박아라.

---

### 결정 2: Distrust by Default vs Trust by Default

**선택**: Distrust by Default — Standard 이상에서 코드 리뷰 자동 실행.

**대안과 트레이드오프**:
- **Trust by Default**: 리뷰는 사용자가 R 옵션으로 요청해야 실행. → 사용자가 누락한다. "이번엔 빠르게 가야 하니까" 합리화에 약하다.
- **Distrust by Default**: 리뷰는 default ON, 명시적 SKIP만 허용. → 토큰 비용 증가하지만 품질 일관성 보장.

**근거**: Anthropic harness design 인사이트 #I — "리뷰는 옵션이 아닌 기본"이 자동화의 철학적 전제. **검증 실패 전까지는 불신**해야 모델 발전과 무관하게 안정성이 유지된다.

**적용**:
- Standard: Spec → Quality → Security 3-stage 자동.
- Comprehensive: + Maintainability 4-stage 자동.
- 사용자 명시 SKIP만 허용, audit에 기록.

**빌더에게**: "리뷰 토큰이 비싸니까 옵션으로"의 유혹을 이겨라. 옵션이 되는 순간 사용자는 항상 SKIP한다.

---

### 결정 3: Hybrid Gate + Auto-Loop (vs 풀 자동 / 풀 수동)

**선택**: 두 차원을 명시적으로 분리.

```
객관적 검증 (Auto-Loop, max retry N=3)    주관적 판단 (Human Gate)
─────────────────────────────────         ─────────────────────────
Lint / 정적분석                            아키텍처 방향성
타입 체크                                  요구사항 해석
유닛 테스트                                UX/UI 미적 판단
빌드 성공 여부                             보안/컴플라이언스 결정
회귀 테스트                                비즈니스 로직 선택
```

**에스컬레이션 규칙** (반드시 정의):
1. Auto-Loop **N회 실패** (N=3 합의) → Human Gate로 자동 전환.
2. **루브릭 점수 임계치 미달** → Human Gate.
3. **diff 급증** (변경량이 예상의 2배 이상) → Human Gate.
4. 모든 자동 통과 건은 audit 로그에 기록 → 사후 검토 가능.

**근거**: 풀 자동은 무한 시도로 비용/시간 폭발. 풀 수동은 사용자 피로도. **N회 실패 시 escalate**가 안전판이다.

**빌더에게**: 자동 루프를 만들 때 N과 루브릭 임계치를 미리 정해라. 운영 중에 정하면 늦다. 우리는 5회 → 3회로 줄였다 (자율 모드는 빨리 escalate가 더 안전).

---

### 결정 4: SDD + Stub Detection (단순 SDD가 아니다)

**선택**: SDD(Spec-Driven Development)에 사전 스캔 + 사후 검증을 양면으로 추가.

**문제**: SDD가 강한 격리를 주지만 그 자체로 새 맹점을 만든다.
- "spec에 정의됨 = 구현됨" 착각.
- Mock 기반 테스트가 stub(`"not yet implemented"`, `todo!()`, `NotImplementedError`)을 은폐.
- 런타임에서 즉시 실패.

**우리 적용 (BL-082 Phase 1)**:
- **사전 (construction-orchestrator)**: Brownfield 시 stub 스캔 → implementer에 "stub 교체 대상" 리스트 인라인 전달.
- **사후 (build-and-test)**: 변경 파일 내 stub 잔존 검증 게이트.
- Greenfield는 스킵 (관련 없음).

**근거**: 공식 검증 시스템이 강할수록 "이미 검증됨"이라는 착각이 강해진다. **양면 가드(전+후)** 가 필수.

**빌더에게**: SDD를 도입하면 동시에 stub blind spot 가드를 도입해라. 둘은 세트다.

---

### 결정 5: Handoff = Hypothesis (Handoff = Truth가 아니다)

**선택**: 다세션 워크플로우에서 session-summary는 **사실이 아니라 가설**로 전달.

**문제**: 세션 끝에 작성한 "Open Work: X is implemented"가 다음 세션에서 사실로 신뢰되면, 잘못된 추정이 다음 세션을 오염시킨다.

**우리 적용 (BL-093/094/095, 외부 4-Layer 블로그 분석에서 도출)**:
session-summary 작성 규칙 6항:
1. Open Work는 **상태 서술형** ("X is not yet implemented"), 명령형 금지.
2. 파일 참조는 **라인 번호까지** (`path:L10-L45`).
3. **"Traps to Avoid"** 섹션 (실패한 접근 명시).
4. **검증 지시** ("이 문서를 코드와 대조해 검증").
5. CLAUDE.md 중복 회피.
6. **2K 토큰 상한**.

**근거**: Tier 3-4(공식 산출물/SDD/Audit)는 강해도 Tier 1-2(in-session, handoff 작성술)가 비어 있으면 다세션 신뢰성이 무너진다. 이건 외부 비교(공개 블로그) 없이는 자체 진단 불가능했다.

**빌더에게**: handoff 메커니즘을 만들 때 "다음 세션이 검증한다"를 디폴트로. 가설로 명시되지 않은 추정은 모두 다음 세션의 함정.

---

## 5. 빌더가 빠지기 쉬운 5가지 함정 (우리가 빠진 것들)

### 함정 1: Dead State Asset
**증상**: 잘 만든 자산 파일이 어떤 스킬에서도 참조되지 않음.

**우리 사례**:
- `tech-stack-defaults.md` (Phase 5) — 1주간 어떤 스킬도 참조 안 함, 사용자가 모름.
- Solution layer (Phase 11) — STORE owner 미정, 빈 채로 방치.

**예방**:
- 자산 도입 시 **사용 경로(어느 스킬에서 read/write)** 를 동시에 정의.
- 단일 writer 원칙 (누구나 쓸 수 있게 두면 아무도 안 쓴다).

---

### 함정 2: 측정으로 가치 증명하려는 시도
**증상**: "우리 하네스가 효과 있는지 측정 인프라를 만들자"고 시작 → 측정 자체가 yak shaving이 됨.

**우리 사례**: Knowledge System Phase 2 측정 인프라 작업을 4주간 시도하다 stop.
- n=1 환경에서 시간 영향 분리 불가.
- 인과 분리 불가 (모델 업데이트인가 하네스 효과인가).
- proxy 정교화할수록 본업이 밀림.

**예방**:
- 시스템 측정으로 가치 증명은 1인 운영에서 **불가능**임을 인정.
- **"사용 경험 회고"**로 frame 전환 (지표 X, 정성적 만족 O).
- 측정 인프라를 만들기 전에 "이 측정으로 무엇을 결정할 것인가"를 먼저 답하라. 답이 없으면 만들지 마라.

---

### 함정 3: SKILL.md 한도 무한 상향
**증상**: 정합성 fix를 SKILL.md에 누적 → 한도를 4번 상향 → 점점 비대.

**우리 사례 (auto-mode)**: v1.8.0 (489줄) → BL-100 (526) → BL-102 (543) → ... → 한도 520 sustainable 자리 약함 (여유 0).

**예방** (BL-105 외부 분리 패턴):
- "한도 상향" 욕구 = **yak shaving 신호**.
- 정합성 fix는 외부 파일 분리(`_shared/patterns` 또는 부속 파일)로 처리.
- **참조 깊이 1단계 가드**: 부속 파일끼리 cross-reference 차단 (자기완결성 유지).

---

### 함정 4: 자율 호출의 유혹
**증상**: "각 스킬이 알아서 트리거되면 우아하지 않을까?" → 6개 스킬쯤에서 라우팅 충돌.

**예방**: 처음부터 **Entry → Phase → Stage 3계층 orchestrator**로 시작. stage skill은 순수 실행자(`stop-no-gate`)로 작성. 게이트 권한은 orchestrator만 소유.

---

### 함정 5: 외부 AI 다수 모델 운영
**증상**: agent-council에 Claude + Codex + Gemini를 모두 운영 → 1인 운영 부담 폭증.

**우리 사례**: Phase 6에서 Gemini 운영 중단, Codex 단일로 마이그레이션.

**예방**: **외부 AI는 적은 수로 깊게**. 다수 모델 운영의 ROI는 1인 환경에서 마이너스. Codex 1개로 시작, 부족하면 추가.

---

## 6. 어떻게 시작할까 — 실용 로드맵

### 0주: 결정 먼저
빌드 시작 전에 다음 5개 질문에 답을 적어둔다.
1. **Orchestrator 모델**: Entry/Phase/Stage 3계층인가, 더 단순한 구조인가?
2. **리뷰 default**: ON인가 OFF인가? Distrust by Default를 받아들일 것인가?
3. **Auto-Loop 한도**: N=3? N=5? 어떤 escalation 규칙?
4. **Handoff 모델**: 사실 전달인가 가설 전달인가? session-summary 작성 규칙은?
5. **자산 단일 writer**: 새 자산을 누가 쓰고 누가 읽는가?

### 1주: 최소 실행 가능 하네스 (MVP)
- Entry Orchestrator 1개 + Phase Orchestrator 1개 + Stage Skill 3-4개.
- 산출물 디렉터리 강제 생성 (`{tool}-docs/`).
- 명시적 A/B 게이트 (수정/진행).
- 세션 시작 hook (도구가 지원하면).

### 2-3주: 가드레일 추가
- TDD 강제 (`test-driven-development` 스킬).
- 완료 전 검증 (`verification-before-completion`).
- 자동 코드 리뷰 (Distrust by Default).
- 디버깅 루프 N회 escalation.

### 4주~: 차별화
- Brownfield 분석 (기존 코드 진입 시 자동).
- 외부 AI 통합 (Codex 1개만).
- Knowledge System (6-type taxonomy).
- Auto Mode (초보자용 옵트인).

### 인용할 자산 (우리 코드를 가져가도 좋다, MIT 라이선스)
- `_shared/devflow-conventions.md` — 메타데이터 + Complexity/Depth + Return/Review 규약.
- `_shared/patterns/` — 7개 행동 패턴 + 5개 구조 패턴 카탈로그.
- `_shared/reviewers/` — 12개 리뷰어 프롬프트.
- `tests/` — L1/L2/L3 정적 검증 인프라 (273 테스트).

---

## 7. 빌더가 처음에 던질 만한 질문 (FAQ)

### Q1. Cursor/Aider/Cline에도 이식 가능한가?
플러그인 메커니즘이 다르므로 1:1 이식은 불가능. **설계 패턴(orchestrator-centric, Distrust by Default, Handoff=Hypothesis)** 은 도구 무관하게 적용 가능. 메커니즘은 각 도구의 hook/extension 모델로 재작성.

### Q2. 28개 스킬이 너무 많지 않나?
조건부 실행. 한 세션에서 모두 활성화되지 않는다. Minimal depth는 5-6개, Comprehensive depth만 전부 사용. 스킬 수보다 **각 스킬의 invoke_mode + return_behavior가 명확한지**가 중요.

### Q3. 정적 테스트(L1/L2/L3)가 정말 필요한가?
스킬 5개 미만은 불필요, 10개 넘으면 필수. SKILL.md 수정이 다른 스킬에 어떤 영향 가는지 6개째부터 추적 불가능. 우리는 273 테스트로 회귀 0건 유지.

### Q4. Auto Mode 같은 "초보자 모드"는 처음부터 만들어야 하나?
**아니다**. 우리는 v1.8.0(7주차)에 추가했다. 코어가 안정된 후 옵트인으로 추가하라. 처음부터 만들면 코어와 결정 분기가 얽혀 SKILL.md가 비대해진다. **회수 비용 0**(단일 파일 삭제)을 유지하라.

### Q5. agent-council vs 단일 외부 AI?
1인 운영이면 단일. 팀 운영이면 council 가능. 차이는 운영 비용(API 키 관리, 응답 시간, 설정 복잡도). 우리는 Council → Codex 단일로 회귀했다.

### Q6. Knowledge System은 처음부터 만들어야 하나?
**아니다**. v1.10.0(5주차)에 추가. 그전에는 audit.md 단일 파일로 충분. 6-type taxonomy는 자산이 50+ 파일 넘어갈 때 의미 있다.

### Q7. 측정/벤치마크는 어떻게 하나?
**하지 마라**. n=1 환경에서 측정으로 가치 증명은 불가능. 정성적 사용 경험 회고로 충분. 측정 인프라 만들 시간에 SKILL을 더 만들어라.

---

## 8. 이 하네스의 한계 (정직하게)

- **n=1 운영**: 우리 경험은 1인 사용자(Jay) 기준. 팀 운영 검증 없음.
- **모델 의존**: Claude Opus 4.6/4.7 기준 설계. 다른 모델에서 Distrust by Default 같은 default 결정이 동일하게 효과 있을지 미검증.
- **도메인 편향**: SaaS/사내툴/데이터/인프라/빌링 5종 도메인 카드 검증. 게임/임베디드/연구 도메인은 가정 검증 필요.
- **Tier 1 (in-session) 약함**: `/compact focus`, 토큰 임계점 모니터링 가이드 미흡 (BL-096 4주 관측 후 결정).
- **벤치마크 부재**: 위에서 말한 대로, 측정 인프라 의도적으로 미구현.

---

## 9. 메타 학습 — 하네스 빌딩의 본질

7주간의 시행착오에서 추출한 메타 원칙 3가지:

### 9.1 자동화는 가드레일과 함께 산다
"AI가 알아서 잘 하길 바라는" 마음이 드는 곳에 가드레일을 박아라. Distrust by Default + N회 escalation + audit 기록 = 자동화 안정성의 3축.

### 9.2 분리(separation)가 통합(integration)보다 강하다
- Auto Mode를 코어와 분리 → 회수 비용 0.
- SKILL.md 정합성 fix를 외부 파일로 분리 → 핵심 가벼움 유지.
- 외부 AI를 단일로 분리 → 운영 비용 통제.

통합하면 처음엔 우아해 보이지만 6개월 후 SKILL.md가 비대해진다. **분리 가능성을 설계 원칙으로 박아라**.

### 9.3 측정 욕구를 의심하라
"우리가 잘 하고 있는지 어떻게 알지?"라는 질문에 측정 인프라로 답하려는 본능을 의심하라. 1인/소규모 환경에서 시스템 측정은 yak shaving이 된다. **사용 경험 회고**가 답이다.

---

## 10. 시작하기

```bash
# 설치 (Claude Code 사용자)
claude plugins install https://github.com/bluejayA/aidlc-devflow.git

# 첫 실행
"사용자 인증 기능을 만들어줘"
```

직접 만들 사람을 위해:
- **소스**: [bluejayA/aidlc-devflow](https://github.com/bluejayA/aidlc-devflow) (MIT)
- **라이선스 가능 자산**: `skills/_shared/`, `tests/`, `docs/guide/`
- **참조 방법론**: [AWS AI-DLC](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/), [obra/superpowers](https://github.com/obra/superpowers)

질문/피드백: GitHub Issues.

---

## 부록 — 더 깊이 읽을 자료

| 문서 | 무엇을 다루는가 |
|------|---------------|
| [`README.md`](../../README.md) | 전체 기능/구조/스킬 목록 |
| [`docs/guide/how-it-works.md`](../guide/how-it-works.md) | 비기술 청중용 흐름 설명 |
| [`docs/guide/architecture.md`](../guide/architecture.md) | 3단 위임 체인, 리뷰 체계, 스킬 패턴 |
| [`docs/guide/operator-guide.md`](../guide/operator-guide.md) | 기술 카탈로그, 질문 원칙, 워크플로우 기본값 조정 |
| [`docs/guide/auto-mode-guide.md`](../guide/auto-mode-guide.md) | Auto Mode 사용법 |
| [`docs/research/2026-03-30-council-synthesis.md`](2026-03-30-council-synthesis.md) | Anthropic harness design 인사이트 13건 + Council 합의 |
| [`docs/research/2026-04-06-skill-lifecycle-strategy.md`](2026-04-06-skill-lifecycle-strategy.md) | 모델 발전에 따른 스킬 진화 (보상 vs 증폭 프레임워크) |
| [`docs/analysis/2026-04-24-handoff-strategy-comparison.md`](../analysis/2026-04-24-handoff-strategy-comparison.md) | 4-Layer 블로그 vs aidlc-devflow 비교 (Tier 1-4) |
| [`docs/research/2026-05-06-aidlc-evolution-workshop.md`](2026-05-06-aidlc-evolution-workshop.md) | 7주 진화 타임라인 14 phase + 메타 인사이트 7가지 |

---

**한 줄로 요약하면**: 하네스를 만든다는 것은 "AI가 알아서 잘 하길 바라는 마음"을 가드레일로 변환하는 작업이다. 그리고 그 가드레일은 **분리(separation)와 명시(explicit)** 의 원칙으로만 지속 가능하다. 우리 7주 경험이 당신 1주를 줄이길 바란다.
