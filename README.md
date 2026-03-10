# devflow

devflow는 [AI-DLC(AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows) 방법론을 기반으로 한 Claude Code 개발 워크플로우 플러그인입니다.

AI가 개발 프로세스를 주도하되, 모든 핵심 결정은 인간이 승인합니다. [Superpowers](https://github.com/obra/superpowers)의 Skills 아키텍처를 계승하면서 AI-DLC의 구조화된 워크플로우를 더했습니다.

---

## 작동 방식

소프트웨어 개발을 시작하는 순간, devflow가 자동으로 활성화됩니다.

코드를 바로 작성하는 대신, 먼저 **워크스페이스를 분석**합니다. 신규 프로젝트인지, 기존 코드베이스인지 파악하고 요구사항을 수집합니다. 요청의 복잡도에 따라 분석 깊이를 자동으로 조절합니다(Minimal / Standard / Comprehensive).

요구사항이 정리되면 **어떤 단계를 실행할지 계획을 제시**하고, 승인을 기다립니다. 코드 생성도 마찬가지입니다. 먼저 체크박스 형태의 계획을 보여주고, 승인 후에만 실행합니다.

모든 설계 결정과 상호작용은 `devflow-docs/`에 자동으로 저장됩니다. 세션이 끊겨도 언제든 이어서 작업할 수 있습니다.

---

## 설치

### Claude Code 공식 마켓플레이스

```bash
/plugin install devflow
```

> 현재 준비 중입니다.

### 직접 설치

```bash
git clone https://github.com/bluejayA/devflow.git ~/.claude/plugins/devflow
```

---

## 기본 워크플로우

### 🔵 INCEPTION — 무엇을 만들지 결정

1. **using-devflow** — 세션 시작. 이전 작업이 있으면 재개 여부를 물어봅니다.
2. **workspace-detection** — 그린필드/브라운필드 판단. 기존 코드베이스를 스캔합니다.
3. **requirements-analysis** — 요구사항 분석. 복잡도에 따라 깊이를 자동 조절합니다.
4. **workflow-planning** — 실행할 단계 목록과 깊이를 제안하고, 사용자가 조정합니다. **명시적 승인 필수.**
5. **application-design** _(조건부)_ — 신규 컴포넌트/서비스 설계가 필요할 때.
6. **units-generation** _(조건부)_ — 복잡한 시스템을 병렬 개발 단위로 분해합니다.

### 🟢 CONSTRUCTION — 어떻게 만들지 결정

7. **code-generation** — Plan → 승인 → Generate. 테스트를 먼저 작성합니다(TDD RED → GREEN).
8. **build-and-test** — 전체 빌드/테스트 지침을 생성합니다.

### 일상 개발 도구

나머지 skills는 개발 중 언제든 자동으로 활성화됩니다.

- **test-driven-development** — RED-GREEN-REFACTOR 사이클 강제
- **systematic-debugging** — 근본 원인 없이 수정 금지. 4단계 디버깅 프로세스
- **writing-plans** — 구현 계획 작성. 2-5분 단위로 분할
- **subagent-driven-development** — 태스크별 서브에이전트 디스패치 + 2단계 리뷰
- **requesting-code-review** / **receiving-code-review** — 코드 리뷰 요청 및 수신
- **verification-before-completion** — 완료 주장 전 반드시 검증
- **using-git-worktrees** — 기능별 격리 브랜치 개발
- **finishing-a-development-branch** — 머지/PR/보관 결정

---

## AI-DLC 3대 패턴

devflow가 Superpowers와 다른 핵심 차이입니다.

### 1. 명시적 승인 게이팅

모든 AI-DLC 스테이지는 완료 후 반드시 사용자 승인을 기다립니다.

```
Requirements Analysis 완료 (Standard)
- 산출물: devflow-docs/inception/requirements.md

A) 변경 요청
B) workflow-planning 단계로 진행
```

AI가 제안하고, 인간이 승인합니다.

### 2. 산출물 자동 문서화

모든 설계 결정이 `devflow-docs/`에 자동 저장됩니다.

```
devflow-docs/
├── inception/
│   ├── workspace.md        # 워크스페이스 분석 결과
│   ├── requirements.md     # 요구사항 문서
│   └── workflow-plan.md    # 승인된 실행 계획
├── construction/
│   └── {unit}/
│       └── code-plan.md    # 코드 생성 계획 + 진행 체크박스
├── devflow-state.md        # 현재 단계 상태 (세션 재개용)
└── audit.md                # 전체 상호작용 로그 (append-only)
```

### 3. 적응형 깊이

요청 복잡도에 따라 분석 깊이를 자동 조절합니다. 간단한 요청에 불필요한 문서를 만들지 않습니다.

| 깊이 | 적용 조건 |
|------|----------|
| **Minimal** | 단순/명확한 요청, 저위험 |
| **Standard** | 일반적 복잡도 |
| **Comprehensive** | 다중 컴포넌트, 고위험, 외부 연동 |

---

## Skills 목록 (22개)

### AI-DLC 핵심 스테이지

| Skill | 역할 |
|-------|------|
| `using-devflow` | 진입점. 세션 재개 또는 신규 시작 |
| `workspace-detection` | 그린필드/브라운필드 판단 |
| `requirements-analysis` | 적응형 깊이 요구사항 분석 |
| `workflow-planning` | 실행 계획 수립 + 명시적 승인 |
| `application-design` | 컴포넌트/서비스 설계 (조건부) |
| `units-generation` | 병렬 개발 단위 분해 (조건부) |
| `code-generation` | Plan → Approve → Generate (TDD) |
| `build-and-test` | 빌드/테스트 지침 생성 |

### 일상 개발 도구

| Skill | 역할 |
|-------|------|
| `writing-plans` | 구현 계획 작성 |
| `executing-plans` | 계획 실행 (배치 + 체크포인트) |
| `subagent-driven-development` | 서브에이전트 병렬 실행 |
| `dispatching-parallel-agents` | 독립 태스크 동시 처리 |
| `test-driven-development` | RED-GREEN-REFACTOR 강제 |
| `systematic-debugging` | 4단계 근본 원인 분석 |
| `verification-before-completion` | 완료 전 검증 필수 |
| `requesting-code-review` | 코드 리뷰 요청 |
| `receiving-code-review` | 코드 리뷰 수신 및 평가 |
| `using-git-worktrees` | 격리 브랜치 개발 |
| `finishing-a-development-branch` | 머지/PR/보관 결정 |
| `writing-skills` | 새 skill 작성 가이드 |

### 유틸리티

| Skill | 역할 |
|-------|------|
| `_utils/devflow-state` | `devflow-state.md` 읽기/쓰기 |
| `_utils/devflow-audit` | `audit.md` append-only 로깅 |

---

## 철학

- **Human in the loop** — AI가 제안하고 인간이 승인. 자동화는 반복 작업에만.
- **증거 우선** — 완료 주장 전 반드시 검증. "될 것 같다"는 허용하지 않음.
- **테스트 먼저** — 코드보다 테스트가 먼저. RED 없이 GREEN 없음.
- **추적 가능성** — 모든 설계 결정이 문서로 남음. 세션이 끊겨도 이어서 작업 가능.
- **적응형** — 복잡한 요청은 철저하게, 단순한 요청은 빠르게.

---

## 기여

Skills는 이 레포지토리에 직접 있습니다. 기여 방법:

1. 레포지토리 포크
2. 브랜치 생성
3. `writing-skills` skill의 가이드를 따라 새 skill 작성
4. PR 제출

---

## 참고 자료

- [AWS AI-DLC 방법론 블로그](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows)
- [obra/superpowers](https://github.com/obra/superpowers)
- [설계 문서](docs/plans/2026-03-10-devflow-design.md)
- [구현 계획](docs/plans/2026-03-10-devflow-implementation.md)

---

## 라이선스

MIT License
