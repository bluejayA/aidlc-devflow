# AI Agent Skill Design Patterns

AI 에이전트 스킬을 체계적으로 설계하고 작성하기 위한 패턴 가이드.

이 가이드는 [aidlc-devflow](https://github.com/bluejayA/aidlc-devflow) 프로젝트에서 29개 스킬을 개발하며 축적한 설계 패턴을 정리한 것입니다.

## 문서 구성

| 문서 | 내용 |
|------|------|
| [structural-patterns.md](structural-patterns.md) | 구조 패턴 5종 — 스킬 내부를 어떻게 설계할 것인가 (Tool Wrapper, Generator, Reviewer, Inversion, Pipeline) |
| [behavioral-patterns.md](behavioral-patterns.md) | 행동 패턴 7종 — 스킬이 사용자와 어떻게 상호작용할 것인가 (Iron Law, Gate, Review Loop, Three-Mode, Hold/Skip, Orchestrator-Only, User-Invocable) |
| [persuasion-principles.md](persuasion-principles.md) | 설득 원칙 3종 — 규율 스킬이 압박 하에서도 지켜지도록 하는 언어 설계 (Authority, Commitment, Social Proof) |
| [writing-guide.md](writing-guide.md) | 실전 작성 가이드 — 자유도 설계, 점진적 공개, CSO, 스킬 TDD |

## 두 축의 관계

구조 패턴과 행동 패턴은 **직교**합니다. 하나의 스킬은 구조 패턴과 행동 패턴을 각각 하나씩(또는 복합으로) 가집니다.

- **구조 패턴** = "스킬 내부를 어떻게 설계하는가" (디렉토리 구조, 파일 분리, 데이터 흐름)
- **행동 패턴** = "사용자와 어떻게 상호작용하는가" (게이트, 리뷰 루프, 모드 분기)

## 연구 기반

- Cialdini, R. B. (2021). *Influence: The Psychology of Persuasion.* Harper Business.
- Meincke, L. et al. (2025). *Call Me A Jerk: Persuading AI to Comply.* University of Pennsylvania. (N=28,000)
- [5 Agent Skill Design Patterns Every ADK Developer Should Know](https://lavinigam.com/posts/adk-skill-design-patterns/) — Lavi Nigam
- [Agent Skills Specification](https://agentskills.io/specification) — agentskills.io
