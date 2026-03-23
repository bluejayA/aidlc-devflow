# AIDLC DevFlow — Feature History

GitHub Issues 기반 기능 추가 이력. 날짜순 정렬.

---

## 2026-03-17 — 기반 체계 구축

### #8 코드 리뷰 요청 스킬 신설
코드 리뷰를 "받는" 스킬만 있고 "요청하는" 스킬이 없었다. `requesting-code-review` 스킬을 추가하여, 구현 완료 후 Spec Compliance → Code Quality 순서로 2단계 리뷰를 자동 실행할 수 있게 했다. 이 스킬이 코드 리뷰 프로세스의 단일 진입점(Single Source of Truth) 역할을 한다.

### #9 서브에이전트 컨텍스트 격리 원칙
서브에이전트에 세션 히스토리를 통째로 넘기면 불필요한 토큰 소모와 혼선이 생긴다. "태스크에 필요한 최소 컨텍스트만 구성하고, 이전 대화나 다른 태스크 결과는 전달하지 않는다"는 격리 원칙을 conventions에 명시했다.

### #10 세션 시작 훅 — 자동 컨텍스트 주입
매 세션마다 사용자가 수동으로 devflow를 호출해야 했다. SessionStart 훅을 추가하여, 세션이 시작되면 devflow 시스템이 자동으로 활성화되고 안내 메시지를 표시한다.

### #11 Brainstorming에 Spec Review Loop 추가
설계 문서를 작성하고 나면 리뷰 없이 바로 다음 단계로 넘어갔다. 설계 완료 후 서브에이전트가 스펙 문서를 자동 리뷰하고, 이슈가 있으면 수정-재리뷰 루프(최대 5회)를 돌도록 추가했다.

### #12 dev-playbook 공유 패턴 반영 — 질문 가이드 + 기술 스택 카탈로그
사용자에게 질문할 때의 형식 가이드(`question-format-guide`)와, 프로젝트 유형별 기술 스택 추천 카탈로그(`tech-stack-defaults`)를 도입했다. INCEPTION에서 요구사항을 수집할 때 더 구조화된 질문을 하고, 기술 선택을 체계적으로 안내할 수 있게 되었다.

### #13 dev-playbook 보조 패턴 — ASCII 다이어그램 표준 + 엔터프라이즈 체크리스트
설계 산출물에 ASCII 다이어그램 규칙을 적용하여 일관된 시각화를 제공하고, 엔터프라이즈 환경에서 필요한 보안/규정 준수 체크리스트를 추가했다.

### #14 Instruction Priority Hierarchy 명시
사용자 지시, 스킬 규칙, 시스템 프롬프트가 충돌할 때 어떤 것이 우선하는지 불명확했다. "사용자 지시 > 스킬 규칙 > 기본 동작" 우선순위를 conventions에 명시하여, 사용자가 항상 최종 결정권을 갖도록 했다.

### #15 테스트 인프라 도입 (Phase 1)
28개 스킬이 있지만 테스트가 전무했다. `validate-skills.sh` 스크립트로 스킬 파일의 구조적 무결성(필수 필드, frontmatter 형식 등)을 자동 검증하는 기초 테스트 인프라를 구축했다.

### #16 writing-skills 보조 자료 — 패턴 카탈로그 + 설득 원칙
스킬을 작성할 때 참고할 수 있는 7개 행동 패턴 카탈로그(`skill-pattern-catalog`)와, 에이전트가 규율을 우회하려는 합리화를 방지하는 설득 원칙(`persuasion-principles`) 문서를 추가했다.

### #26 devflow 종료 처리 — state 아카이브
개발 브랜치 작업이 끝나도 `devflow-state.md` 파일이 남아서, 다음 세션에서 "이어하기"로 잘못 인식되었다. 완료 시 state 파일을 아카이브하여 깔끔하게 종료되도록 수정했다.

---

## 2026-03-18 — 테스트 강화 + Council 리뷰 + Brownfield 분석

### #29 테스트 인프라 Phase 2 — 정적 그래프 검증 + 시뮬레이션
SKILL.md를 상태 머신 명세로 취급하여 정적 검증하는 3단계 테스트 피라미드를 구축했다. L1(데드엔드/순환 탐지), L2(라우팅 시뮬레이션), L3(스텝 순서 검증)으로 스킬의 흐름 오류를 코드 실행 없이 잡아낸다.

### #33 테스트 인프라 Phase 2 리팩토링
Phase 2에서 테스트 파일 안에 270+ LOC의 시뮬레이션 엔진이 혼재되어 있던 것을 별도 모듈로 분리하고, fixture를 통합하여 유지보수성을 개선했다. 총 95개 테스트로 확장.

### #30 agent-council 리뷰 공통 인프라
외부 AI(Codex, Gemini)를 리뷰에 참여시키기 위한 기반을 구축했다. CLI 자동 감지, risk score 기반 모드 자동 선택(single/council-lite/council-full), 관점별 프롬프트 템플릿, 의장 종합 프로토콜을 정의했다.

### #31 설계 리뷰에 Council 적용
application-design 완료 후 Codex(아키텍처 관점)와 Gemini(트레이드오프/운영 관점)가 설계 문서를 다각도로 검토하는 게이트를 추가했다. Claude 의장이 의견을 종합하고 충돌을 해결한다.

### #32 코드 리뷰에 Council 적용
코드 구현 완료 후 Codex(코드 품질)와 Gemini(보안/논리)가 구현 코드를 다각도로 검토하는 게이트를 추가했다. 동일 모델의 맹점을 외부 AI로 보완하는 구조이다.

### #35 게이트 선택지 용어 통일
오케스트레이터의 게이트에서 "수정 요청"과 "변경 요청"이 혼용되고 있었다. "변경 요청"으로 통일하고, 선택지에 변경 의도를 힌트로 추가하여 사용자가 의미를 빠르게 파악할 수 있게 했다.

### #42 Brownfield 분석 강화
기존 코드베이스를 분석할 때 1-depth 디렉토리 트리만 봤던 것을, git 활동 핫스팟(최근 가장 많이 수정된 파일), 기존 문서(README, docs/) 감지, 핵심 파일 샘플링으로 확장했다. 요구사항 분석과 복잡도 판단에 더 풍부한 컨텍스트를 제공한다.

### #43 기술 스택 정책 모드
기술 스택 카탈로그가 선택지만 제시하고 강제력이 없었다. 조직 운영자가 기술 표준을 관리할 수 있도록 3단계 정책 모드(open: 자유 선택, guided: 사유 기록 후 허용, strict: 카탈로그만 허용)를 도입했다.

---

## 2026-03-19 — 스킬 품질 전면 점검 + GitHub Flow

### #45 구조 디자인 패턴 가이드
스킬의 "내부 구조"를 설계하는 패턴 5종(Pipeline, Decision Tree, Iterative Refinement, Template Method, Composite)을 정리했다. 기존의 행동 패턴(TDD, Gate, Review Loop 등)과 직교하는 구조 패턴 체계로, 새 스킬 설계 시 결정 트리를 따라 적합한 구조를 선택할 수 있다.

### #47 스킬 셀프 리뷰 S1 — 즉시 버그 수정
27개 스킬 전수 검사에서 발견된 명확한 버그 5건을 즉시 수정했다. `git add -p`(인터랙티브 명령) 사용, description의 CSO(첫 문장 규칙) 위반, 스킬 제목 불일치 등.

### #48 스킬 셀프 리뷰 S2 — 리뷰 기준 정립
orchestrator-only 스킬에는 Trigger/Examples/Troubleshooting이 불필요하다는 예외 규칙을 확정하고, skill-reviewer 프롬프트에 반영했다. 이후 S3~S6의 보강 작업 범위를 결정하는 기준이 되었다.

### #49 스킬 셀프 리뷰 S3 — 미완성 스킬 보강
스텁 상태였던 `functional-design`과 `superpowers-tracking` 2개 스킬을 완성했다. Return 형식 표준화, 필수 섹션 추가, INCEPTION/CONSTRUCTION 분류 확정.

### #50 스킬 셀프 리뷰 S4 — Pipeline 게이트 보강
Pipeline 구조 패턴 스킬에서 단계 간 게이트 선언이 누락되어 에이전트가 단계를 건너뛸 위험이 있었다. `receiving-code-review`와 `systematic-debugging`에 명시적 게이트 조건을 추가했다.

### #51 스킬 셀프 리뷰 S5 — user-invocable 스킬 보강 (전반)
사용자가 직접 호출하는 스킬 6개에 Trigger 조건, Examples, Troubleshooting 섹션을 추가했다. brainstorming, writing-plans, executing-plans 등에서 "언제 사용하고, 어떻게 사용하며, 문제가 생기면 어떻게 하는지"를 명확히 했다.

### #52 스킬 셀프 리뷰 S6 — user-invocable 스킬 보강 (후반) + 한국어 키워드
나머지 user-invocable 스킬들을 보강하고, 모든 스킬의 description에 한국어 키워드를 일괄 추가했다. 한국어로 "디버깅해줘", "테스트 작성해줘" 같은 요청에도 올바른 스킬이 트리거되도록 개선했다.

### #25 GitHub Flow 연동
devflow 파이프라인에 GitHub Flow를 옵트인으로 연동했다. INCEPTION 시작 시 이슈 자동 생성, 스테이지별 진행 코멘트, PR 생성/머지 자동화를 지원한다. "GitHub Flow를 같이 진행하시겠습니까?" 질문으로 활성화/비활성화 선택 가능.

---

## 2026-03-23 — 리뷰 체계 고도화 + 오케스트레이터 유연성

### #56 skill-creator 통합 — 정량적 최적화 게이트
Anthropic 공식 `skill-creator` 플러그인과 aidlc의 `writing-skills`를 분석한 결과, 설계(aidlc) → 검증(skill-creator)으로 조합하면 가장 강력했다. writing-skills의 REFACTOR 단계에 skill-creator의 정량적 벤치마크와 description 최적화 게이트를 추가했다.

### #57 글로벌 인터럽트 핸들러
오케스트레이터 게이트가 A/B 선택지만 제공하여, 사용자가 "계획 수정하고 싶어" 같은 파이프라인 밖 요청을 하면 처리할 수 없었다. 모든 오케스트레이터 게이트에 인터럽트 핸들러를 추가하여, 자유 발화를 의도 분류 → 라우팅하는 탈출 경로를 제공한다.

### #58 스킬 설계 패턴 외부 공개
aidlc 내부에서만 참조하던 설계 패턴 문서(persuasion-principles, skill-design-patterns, skill-writing-guide, skill-pattern-catalog)를 외부에서도 참조 가능하도록 공개 구조로 재구성했다.

### #62 4-stage 코드 리뷰 확장
기존 2-stage(Spec → Quality) 리뷰를 관점 분리로 확장했다. Standard에서는 Security 리뷰가 추가되고(3-stage), Comprehensive에서는 Maintainability까지 포함(4-stage)된다. 또한 4-stage(관점 커버리지)와 Council(다모델 편향 보완)이 직교하는 두 차원임을 명시하여, Council 모드에서도 4-stage 관점이 그대로 적용되는 구조를 확립했다.
