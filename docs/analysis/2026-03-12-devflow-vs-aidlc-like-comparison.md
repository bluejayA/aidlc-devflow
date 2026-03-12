# devflow vs devflow-aidlc-like 비교 분석

**작성일**: 2026-03-12
**대상**:
- [devflow](https://github.com/bluejayA/devflow) — Enhanced Skills 아키텍처
- [devflow-aidlc-like](https://github.com/bluejayA/devflow-aidlc-like) — Orchestrator-Centric 아키텍처

**배경**: 두 플러그인 모두 AWS AI-DLC 방법론과 superpowers 플러그인을 참고하여 만든 Claude Code 개발 워크플로우 플러그인이다. 최종 목표(AI-DLC 기반 소프트웨어 개발 자동화)는 동일하며, 아키텍처 접근 방식이 다르다.

---

## 1. 기본 수치 비교

| 지표 | devflow | aidlc-like | 비율 |
|------|---------|------------|------|
| 스킬 수 | 29개 | 21개 | 1.4x |
| SKILL.md 총 줄 수 | 7,587줄 | 3,798줄 | 2.0x |
| 지원 파일 (shared/prompts) | 3,776줄 | 550줄 | 6.9x |
| **총 토큰 풋프린트** | **~11,363줄** | **~4,348줄** | **2.6x** |
| 최대 스킬 크기 | 678줄 (writing-skills) | 330줄 (finishing-branch) | 2.1x |
| 스킬 평균 크기 | ~262줄 | ~181줄 | 1.4x |

---

## 2. 기능 우수성

### 2-1. 기능 매핑 (스테이지별)

| 기능 영역 | devflow | aidlc-like | 비고 |
|-----------|---------|------------|------|
| INCEPTION — workspace-detection | ✅ | ✅ | 동등 |
| INCEPTION — requirements-analysis | ✅ | ✅ | 동등 |
| INCEPTION — user-stories | ❌ | ✅ | aidlc-like만 보유 |
| INCEPTION — nfr-requirements | ✅ (nfr-analysis) | ✅ | 동등 |
| INCEPTION — workflow-planning | ✅ | ✅ | 동등 |
| INCEPTION — application-design | ✅ | ✅ | 동등 |
| INCEPTION — units-generation | ✅ | ✅ | 동등 |
| CONSTRUCTION — functional-design | ✅ | ❌ | devflow만 보유 |
| CONSTRUCTION — code-generation | ✅ | ✅ | 동등 |
| CONSTRUCTION — build-and-test | ✅ | ✅ | 동등 |
| CONSTRUCTION — git-worktrees | ✅ | ✅ | 동등 |
| brainstorming | ✅ (472줄, superpowers 참고 자체 작성) | superpowers에 위임 | devflow가 내장, aidlc-like가 토큰 절약 |
| TDD 프로토콜 | ✅ (613줄, superpowers 참고 자체 작성) | ✅ (132줄 shared, superpowers 참고 축약) | 동일 원천, devflow가 상세, aidlc-like가 간결 |
| subagent-driven-development | ✅ (superpowers 참고 자체 작성) | superpowers에 위임 | devflow가 내장, aidlc-like가 토큰 절약 |
| 세션 추적/대시보드 | ✅ (dev-progress, superpowers-tracking) | devflow-state만 | devflow 우위 |
| 코드 리뷰 서브에이전트 | ✅ 3종 | ✅ 3종 | 동등 |

### 2-2. 기능 우수성 판정

**devflow 우위 영역**:
- functional-design 단계 보유 (CONSTRUCTION에서 상세 설계 단계 추가)
- brainstorming, TDD, subagent-driven-development를 superpowers 참고하여 자체 내장 (런타임에 superpowers 플러그인 불필요)
- 세션 추적 도구 풍부 (dev-progress 대시보드, superpowers-tracking)

**aidlc-like 우위 영역**:
- user-stories 스킬 보유 (INVEST 기준 사용자 스토리 변환)
- Pre-Planning 단계가 더 체계적 (user-stories + nfr-requirements 조건부 분기)

**결론**: 기능 범위에서 devflow가 우위. 29개 vs 21개, 자체 완결적 구조. 단, aidlc-like는 Pre-Planning에서 user-stories를 추가로 보유.

---

## 3. 사용자 흐름 장/단점

### 3-1. 흐름 비교

| 관점 | devflow | aidlc-like |
|------|---------|------------|
| 진입 | using-devflow → 자동 감지 → 세션 재개 | 동일 |
| 승인 게이팅 | 각 skill이 자체 A/B gate 제시 | 오케스트레이터가 통합 gate 제시 |
| 게이트 일관성 | skill마다 형식이 다를 수 있음 | 오케스트레이터가 통일 형식 보장 |
| 디버깅/추적 | 각 skill 개별 추적 필요 | 오케스트레이터 하나만 추적 |
| 스킬 독립 호출 | 모든 스킬 standalone 가능 | stage 스킬은 orchestrator-only |
| 워크플로우 변경 | 각 skill에 하드코딩된 다음 단계 수정 | Routing Table 한 곳만 수정 |
| 실패 복구 | skill 내부에서 자체 복구 시도 | 오케스트레이터가 복구 경로 결정 |

### 3-2. 장점

| devflow | aidlc-like |
|---------|------------|
| 스킬 개별 호출 자유도 높음 — debugging만 단독 사용 가능 | 전체 흐름을 한 곳(오케스트레이터)에서 파악 가능 |
| superpowers 참고하여 내장 — 런타임 외부 의존 없음 | 게이트/상태/로깅 형식 일관성 보장 |
| 기능 풍부 (brainstorming, 세션 추적 등) | Stage 추가/변경이 Routing Table만으로 가능 |

### 3-3. 단점

| devflow | aidlc-like |
|---------|------------|
| 게이트 형식이 skill마다 차이 가능 | stage 스킬 단독 호출 불가 (orchestrator-only) |
| 디버깅 시 여러 skill 추적 필요 | brainstorming/TDD를 superpowers에 의존 |
| 워크플로우 변경 시 여러 파일 수정 필요 | superpowers 플러그인 없으면 일부 기능 사용 불가 |

### 3-4. 사용자 흐름 판정

**용도별 무승부**.
- 스킬을 개별적으로 꺼내 쓰는 유연성이 필요하면 devflow
- 일관된 워크플로우 경험과 추적 용이성이 우선이면 aidlc-like

---

## 4. AI-DLC 철학과 정합성

AWS AI-DLC의 핵심 원칙과 각 플러그인의 부합도를 비교한다.

### 4-1. 원칙별 대조

| AI-DLC 원칙 | devflow | aidlc-like | 판정 |
|-------------|---------|------------|------|
| 오케스트레이터가 라이프사이클 소유 | 부분적 — using-devflow가 진입점이나 각 skill이 게이팅/상태 자체 관리 | 완전 — 오케스트레이터가 게이팅/상태/라우팅 전부 소유 | aidlc-like |
| Phase 분리 (INCEPTION/CONSTRUCTION) | 명확 | 명확 — inception/construction 오케스트레이터 분리 | 동등 |
| 적응형 깊이 (Minimal/Standard/Comprehensive) | 지원 | 지원 + conventions에 Complexity↔Depth 관계 명시 | aidlc-like 약간 우위 |
| 산출물 자동 문서화 | devflow-docs/ 구조 | 동일 devflow-docs/ 구조 | 동등 |
| 명시적 승인 게이팅 | 각 skill이 분산 처리 | 오케스트레이터가 중앙 처리 | aidlc-like |
| Stage는 순수 실행자 | 아님 — skill이 게이팅+상태+라우팅도 수행 | 맞음 — skill은 실행 후 STOP | aidlc-like |
| 감사 추적 (Audit) | 각 skill이 직접 audit 기록 | 오케스트레이터만 audit 기록 (단일 책임) | aidlc-like |
| 세션 연속성 | devflow-state로 세션 재개 | 동일 | 동등 |

### 4-2. 정합성 판정

**aidlc-like가 AI-DLC 철학에 더 충실**.

AI-DLC의 핵심은 "오케스트레이터가 전체 라이프사이클을 소유하고, 각 stage는 순수 실행자로 동작한다"이다. aidlc-like는 이 원칙을 구조적으로 강제한다:
- `invoke_mode: orchestrator-only` 메타데이터로 stage 스킬의 직접 호출 차단
- `return_behavior: stop-no-gate`로 skill은 결과만 반환하고 즉시 종료
- 게이팅, 상태 업데이트, 감사 로깅 모두 오케스트레이터 소유

devflow는 각 skill의 자율성이 높아 AI-DLC보다는 마이크로서비스 협력 패턴에 가깝다. 이것이 나쁜 설계는 아니지만, AI-DLC 원래 의도와는 거리가 있다.

---

## 5. 토큰 효율성

### 5-1. 풋프린트 비교

| 지표 | devflow | aidlc-like | 차이 |
|------|---------|------------|------|
| 총 풋프린트 | ~11,363줄 | ~4,348줄 | aidlc-like 2.6배 적음 |
| Shared/지원 파일 | 3,776줄 | 550줄 | aidlc-like 6.9배 적음 |
| TDD 프로토콜 | 613줄 (superpowers 참고 내장) | 132줄 (superpowers 참고 축약) | 동일 원천, aidlc-like 4.6배 적음 |
| brainstorming | 472줄 (superpowers 참고 내장) | 0줄 (superpowers에 위임) | devflow는 내장 비용, aidlc-like는 외부 의존 비용 |

### 5-2. 효율성 패턴 비교

| 패턴 | devflow | aidlc-like |
|------|---------|------------|
| Review 로직 | 각 스킬에 인라인 (10-15줄씩 반복) | conventions에 정의, 스킬은 3줄 참조 |
| Return 형식 | 각 스킬에 코드펜스로 전체 기술 | conventions 표준 형식 + 필드만 나열 |
| 중복 제거 방식 | INTEGRATION_MAP으로 의존성 문서화 (중복 자체는 유지) | conventions.md SSOT + Extract & Reference |
| 패턴 공유 | shared/patterns/ 에 3개 패턴 | _shared/ 에 conventions + 4개 규약 |

### 5-3. 세션당 토큰 추정

단일 INCEPTION→CONSTRUCTION 사이클 기준:

| 구성 요소 | devflow | aidlc-like |
|-----------|---------|------------|
| 오케스트레이터 로드 | ~146줄 | ~143줄 + 294줄 (inception-orch) |
| 스테이지 스킬 로드 (8개 평균) | ~262줄 × 8 = ~2,096줄 | ~150줄 × 8 = ~1,200줄 |
| Shared 파일 로드 | 스킬 내 인라인 (이미 포함) | ~135줄 (conventions) + 필요 시 132줄 (tdd) |
| **세션 예상 총 로드** | **~2,242줄** | **~1,904줄** |

> 참고: 세션당 로드량 차이(~338줄)는 총 풋프린트 차이(~7,015줄)보다 작다. 이는 devflow가 세션 내에서 모든 29개 스킬을 로드하지 않기 때문이다. 세션 내 효율 차이는 약 15%이며, 저장소 수준 효율 차이는 약 62%이다.

### 5-4. 토큰 효율성 판정

**aidlc-like가 효율적**. conventions SSOT 패턴으로 Review/Return/TDD 중복을 체계적으로 제거했다. 단, 두 플러그인 모두 superpowers를 원천으로 공유한다. devflow는 superpowers 스킬을 참고하여 자체 내장(472줄+613줄)했고, aidlc-like는 superpowers 런타임 위임 또는 축약 참조(132줄)를 선택했다. 내장 vs 위임은 "독립성 vs 토큰 효율" 트레이드오프이며, 이를 제외해도 conventions 참조 패턴만으로 스킬당 평균 31% 줄 수를 줄였다.

---

## 6. 종합 판정

| 차원 | 우위 | 핵심 근거 |
|------|------|-----------|
| **기능 우수성** | devflow | 29개 스킬, functional-design/brainstorming/세션추적 내장 (superpowers 참고) |
| **사용자 흐름** | 용도별 무승부 | devflow=독립 호출 자유, aidlc-like=일관성과 추적 용이 |
| **AI-DLC 정합성** | aidlc-like | 오케스트레이터가 LC 소유, stage=순수 실행자 원칙 구조적 강제 |
| **토큰 효율성** | aidlc-like | 총 풋프린트 2.6배 적음, conventions SSOT로 체계적 중복 제거 |

### 선택 기준

**devflow를 선택할 때**:
- 스킬을 개별적으로 꺼내 쓰는 유연성이 중요할 때
- 런타임에 superpowers 플러그인 없이 동작해야 할 때 (superpowers 참고 내장)
- brainstorming, 세션 추적 등 풍부한 내장 기능이 필요할 때

**aidlc-like를 선택할 때**:
- AI-DLC 방법론을 원래 의도대로 충실히 따르고 싶을 때
- 토큰 효율성이 중요할 때 (긴 세션, 비용 관리)
- 워크플로우 전체를 한 곳에서 파악하고 변경하고 싶을 때
- superpowers 플러그인을 이미 사용 중일 때
