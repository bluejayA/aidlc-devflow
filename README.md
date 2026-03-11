# devflow-aidlc-like

AI-DLC 방법론을 **오케스트레이터 중심 아키텍처**로 구현한 Claude Code 개발 워크플로우 플러그인입니다.

[AI-DLC(AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows)의 컨셉을 최대한 충실하게 반영합니다.
`using-devflow` 하나가 전체 라이프사이클을 소유하고 구동하며, 나머지 stage skill은 순수 실행자로 동작합니다.

> **관련 구현체**: [bluejayA/devflow](https://github.com/bluejayA/devflow) — 동일한 AI-DLC 워크플로우를 분산형(Enhanced Skills) 아키텍처로 구현한 버전

---

## 두 구현체 비교

| | **devflow-aidlc-like** (이 repo) | **devflow** |
|---|---|---|
| **아키텍처** | Orchestrator-Centric (B안) | Enhanced Skills (C안) |
| **승인 게이팅** | `using-devflow`가 통합 관리 | 각 stage skill이 자체 처리 |
| **상태 업데이트** | 오케스트레이터만 | 각 skill이 직접 |
| **Audit 로깅** | 오케스트레이터만 | 각 skill이 직접 |
| **다음 단계 결정** | Stage Routing Table (중앙) | 각 skill에 하드코딩 |
| **Stage skill 역할** | 실행 후 STOP (순수 실행자) | 실행 + 게이팅 + 상태 관리 |
| **Skill 수** | 17개 | 23개 |
| **AI-DLC 컨셉 부합도** | 높음 — 오케스트레이터가 LC 소유 | 중간 — 자율 skill 간 협력 |
| **확장 용이성** | Stage 추가 시 Routing Table만 수정 | 각 skill이 독립적으로 확장 |
| **디버깅** | 오케스트레이터 하나만 추적 | 각 skill 개별 추적 필요 |

### 아키텍처 흐름 비교

**devflow-aidlc-like (B안) — 오케스트레이터가 모든 것을 소유**
```
[using-devflow (Orchestrator)]
  └─ LOOP:
      1. stage skill 호출 → 결과만 받고 STOP
      2. devflow-audit 로깅          ← 오케스트레이터
      3. A/B 승인 게이트 제시        ← 오케스트레이터
      4. devflow-state 업데이트      ← 오케스트레이터
      5. Stage Routing Table로 다음 단계 결정
      6. 반복
```

**devflow (C안) — 각 skill이 자급자족**
```
[using-devflow] → [workspace-detection]
                       ├─ 실행
                       ├─ devflow-state 업데이트  ← skill 내부
                       ├─ devflow-audit 로깅      ← skill 내부
                       └─ A/B gate → [requirements-analysis]  ← skill 내부
```

### 어떤 것을 선택할까?

**devflow-aidlc-like (이 repo)** 선택 기준:
- AI-DLC 컨셉을 학습하거나 연구할 때
- 워크플로우 전체 흐름을 한 곳에서 파악하고 싶을 때
- Stage 추가/변경이 잦아 중앙 라우팅이 편리할 때

**devflow** 선택 기준:
- 일상 개발 도구 (TDD, 디버깅, 코드 리뷰 등)도 함께 쓰고 싶을 때
- 각 skill을 독립적으로 호출하는 자유도가 필요할 때
- Skill을 개별적으로 커스터마이징하고 싶을 때

---

## 작동 방식

소프트웨어 개발을 시작하는 순간, `using-devflow`가 자동으로 활성화됩니다.
세션 시작 훅(`hooks/session-start`)이 Claude에 `using-devflow` 컨텍스트를 주입하여 개발 요청을 자동으로 감지합니다.

오케스트레이터가 Stage Routing Table에 따라 전체 라이프사이클을 순차적으로 구동합니다.
각 stage 완료 후 오케스트레이터가 직접 승인 게이트를 제시합니다. Stage skill은 실행 결과만 반환하고 즉시 종료합니다.

---

## 워크플로우

### 🔵 INCEPTION — 무엇을 만들지 결정

1. **using-devflow** — 진입점. 기존 세션 재개 여부 확인 후 오케스트레이션 시작
2. **workspace-detection** — 그린필드/브라운필드 판단
3. **requirements-analysis** — 적응형 깊이(Minimal / Standard / Comprehensive) 요구사항 분석. 해석이 분기되는 경우 선택지 제시 후 확정
4. **workflow-planning** — 실행할 단계와 깊이를 계획하고 명시적 승인 요청
5. **application-design** _(조건부)_ — 신규 컴포넌트 설계가 필요할 때
6. **units-generation** _(조건부)_ — 복잡한 시스템을 병렬 개발 단위로 분해

### 🟢 CONSTRUCTION — 어떻게 만들지 결정

7. **using-git-worktrees** _(선택적)_ — workflow-planning 승인 직후, main 브랜치 보호를 위한 격리 워크트리 생성
8. **code-generation** — Plan → 오케스트레이터 승인 → Generate (TDD: 테스트 먼저)
9. **build-and-test** — 전체 빌드/테스트 지침 생성

---

## Skills 목록 (17개)

### AI-DLC 핵심 스테이지

| Skill | 역할 |
|-------|------|
| `using-devflow` | 오케스트레이터. 전체 라이프사이클 소유 및 구동 |
| `workspace-detection` | 그린필드/브라운필드 판단 (순수 실행) |
| `requirements-analysis` | 적응형 요구사항 분석. 해석 분기 시 선택지 제시 |
| `workflow-planning` | 실행 계획 수립 (순수 실행) |
| `application-design` | 컴포넌트/서비스 설계 (조건부, 순수 실행) |
| `units-generation` | 병렬 개발 단위 분해 (조건부, 순수 실행) |
| `using-git-worktrees` | workflow-planning 후 격리 개발 워크트리 생성 (선택적) |
| `code-generation` | 2단계 코드 생성 — Plan 후 STOP, 승인 후 Generate |
| `build-and-test` | 빌드/테스트 지침 생성 (순수 실행) |

### 개발 품질 도구

| Skill | 역할 |
|-------|------|
| `systematic-debugging` | 버그/실패 발생 시 근본 원인 조사 강제 |
| `verification-before-completion` | 완료 선언 전 실제 검증 명령 실행 강제 |
| `finishing-a-development-branch` | 개발 완료 후 병합/PR/유지/폐기 처리 |
| `receiving-code-review` | 코드 리뷰 피드백 수신 시 체계적 처리 |
| `dispatching-parallel-agents` | 독립적 태스크를 병렬 서브에이전트로 디스패치 |
| `writing-skills` | 새 스킬 개발 시 TDD 방식 + CSO 원칙 적용 |

### 유틸리티

| Skill | 역할 |
|-------|------|
| `_utils/devflow-state` | `devflow-docs/devflow-state.md` 읽기/쓰기 |
| `_utils/devflow-audit` | `devflow-docs/audit.md` append-only 로깅 |

### 공유 규약 문서

| 파일 | 역할 |
|------|------|
| `_shared/devflow-conventions.md` | YAML 메타데이터 필드 의미 정의 (스킬이 아닌 규약 문서) |

#### YAML 메타데이터 규약

모든 AI-DLC 스테이지 스킬은 아래 메타데이터 필드를 사용합니다.

| 필드 | 값 | 의미 |
|------|----|------|
| `invoke_mode` | `orchestrator-only` | `using-devflow`만 호출 가능. 사용자 직접 호출 불가 |
| `return_behavior` | `stop-no-gate` | 실행 후 결과 표시 및 STOP. 승인 게이트는 오케스트레이터 소유 |
| `output_path` | `devflow-docs/...` | 스테이지 산출물 저장 경로 |

---

## 산출물 구조

모든 설계 결정은 `devflow-docs/`에 자동 저장됩니다.

```
devflow-docs/
├── inception/
│   ├── workspace.md        # 워크스페이스 분석 결과
│   ├── requirements.md     # 요구사항 문서 (해석 확정 포함)
│   ├── workflow-plan.md    # 승인된 실행 계획
│   ├── application-design.md  # 컴포넌트 설계 (조건부)
│   └── units.md            # 개발 단위 목록 (조건부)
├── construction/
│   └── {unit}/
│       └── code-plan.md    # 코드 생성 계획 + 진행 체크박스
├── devflow-state.md        # 현재 단계 상태 (세션 재개용)
└── audit.md                # 전체 상호작용 로그 (append-only)
```

---

## 설치

```bash
git clone https://github.com/bluejayA/devflow-aidlc-like.git ~/.claude/plugins/devflow-aidlc-like
```

---

## AI-DLC 3대 패턴

### 1. 명시적 승인 게이팅

오케스트레이터가 모든 승인 게이트를 통합 관리합니다.

```
## workspace-detection 완료

A) 변경 요청
B) 다음 단계 진행
```

### 2. 산출물 자동 문서화

각 stage의 실행 결과가 `devflow-docs/`에 자동 저장됩니다.

### 3. 적응형 깊이 + 해석 분기 확인

요청 복잡도에 따라 분석 깊이를 자동 조절하고, 동등하게 유효한 해석이 여러 개일 경우 먼저 확정합니다.

| 깊이 | 적용 조건 | 해석 분기 확인 |
|------|----------|--------------|
| **Minimal** | 단순/명확한 요청, 저위험 | 없음 |
| **Standard** | 일반적 복잡도 | 해석이 분기될 때만 |
| **Comprehensive** | 다중 컴포넌트, 고위험, 외부 연동 | 항상 |

---

## 참고 자료

- [AWS AI-DLC 방법론 블로그](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows)
- [obra/superpowers](https://github.com/obra/superpowers)
- [B안 vs C안 비교 분석](docs/analysis/2026-03-10-b-plan-vs-c-plan-analysis.md)
- [Skill Guide 준수 리뷰](docs/analysis/2026-03-10-skill-guide-review.md)

---

## 라이선스

MIT License
