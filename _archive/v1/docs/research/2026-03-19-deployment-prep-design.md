# deployment-prep 독립 스킬 설계 리서치

> **일자**: 2026-03-19
> **관련 이슈**: [#41 — deployment-prep 독립 스킬 MVP](https://github.com/bluejayA/aidlc-devflow/issues/41)
> **상태**: 설계 논의 중 (동료 리뷰 대기)

---

## 1. 배경

특정 회사 환경에서 Kubernetes 기반 배포를 전제로, 로컬 테스트 후 원격 샌드박스에 배포/테스트하는 시나리오.
일반 케이스가 아닌 **사용자 옵트인 특수 케이스**로, 파이프라인 내장이 아닌 독립 스킬로 구현한다.

단, AIDLC 플러그인 전용이 아니라 **조직 내 표준 도구**로 재활용 가능한 형태를 지향한다.

---

## 2. 참조 자료 분석

두 개의 외부 자료를 분석하여 설계에 반영할 인사이트를 추출했다.

### 2.1 MCP + Kubernetes Observability (Medium)

> [원문 링크](https://medium.com/@emmanueleshunjnr/i-connected-claude-ai-to-my-kubernetes-homelabs-observability-stack-using-mcp-here-s-how-9e5b46e9bb5f)

Claude를 MCP로 k8s 클러스터에 연결해 **관찰(observe)**하는 사례. deployment-prep은 **생성(generate)** 방향이지만 다음을 참고한다.

**채택할 인사이트:**

- **생성→검증 피드백 루프**: k8s MCP 서버(kubectl/helm 지원)를 활용하면 생성된 매니페스트를 `dry-run=server`로 즉시 검증 가능
- **통합 검증 게이트 패턴**: Dockerfile lint + manifest validate + security scan을 하나로 묶는 구조
- **보안 경계 명확화**: `--disable-write` 같은 안전장치 — 스킬은 **생성만 하고 배포는 하지 않는** 경계를 엄격히 유지
- **MCP 서버 생태계**: [k8s-mcp-server](https://github.com/alexei-led/k8s-mcp-server)가 strict 모드 + dry-run 조합 지원 → 향후 확장 시 활용 가능

### 2.2 Top 8 Claude Skills for DevOps (Pulumi)

> [원문 링크](https://www.pulumi.com/blog/top-8-claude-skills-devops-2026/)

DevOps 스킬 설계 원칙과 14개 스킬 카테고리를 분류한 글.

**채택할 인사이트:**

- **MCP vs 스킬 역할 분리**: MCP = 도구(망치), 스킬 = 절차적 지식(매뉴얼). deployment-prep은 "어떻게 생성할지"의 판단력을 인코딩
- **프로덕션 체크리스트 자동 적용**: `runAsNonRoot`, CPU/메모리 limits, liveness/readiness probe, PDB, 배포 전략 판단을 생성 시점에 포함
- **시크릿 관리 원칙**: 하드코딩 금지, OIDC 우선, 외부 시크릿 스토어 연동
- **스킬 합성(Composition)**: 배포 준비 + 모니터링 구성 + 보안 리뷰를 연계하는 "스킬 스태킹" 패턴
- **핵심 메시지**: "스킬은 단순 템플릿이 아니라 **시니어 엔지니어의 판단력**을 인코딩하는 것"

### 2.3 교차 시사점 → MVP 설계 반영

| 관점 | deployment-prep 적용 |
|------|---------------------|
| 보안 | 생성 시 RBAC 최소권한 + 비루트 + 시크릿 분리 기본 적용 |
| 검증 | MVP는 `dry-run=client`, 향후 MCP로 `dry-run=server` 확장 |
| 경계 | 생성만, 배포는 사용자 명시 승인 필요 |
| 판단력 | "왜 이 설정인지" 맥락을 주석/가이드로 함께 제공 |

---

## 3. 기존 AIDLC 스킬과의 관계 분석

### 3.1 현재 CONSTRUCTION 파이프라인 흐름

```
각 유닛별:
  functional-design → code-generation(Plan→Generate, TDD) → [반복]
    ↓
build-and-test ──[조건부 게이트]──
    ↓
verification-before-completion
    ↓
finishing-a-development-branch (merge / PR / keep / discard)
```

### 3.2 관련 스킬별 관계

| 스킬 | deployment-prep과의 관계 |
|------|------------------------|
| **build-and-test** | 직접적 선행자. 빌드 성공 + 기술 스택 정보를 입력으로 받음 |
| **construction-orchestrator** | 파이프라인 통합 시 deployment-prep을 호출하는 주체 |
| **code-generation** | TDD가 이미 완료된 상태이므로 deployment-prep에서 TDD 불필요 |
| **verification-before-completion** | docker build + dry-run 검증이 이 역할을 대체 |
| **finishing-a-development-branch** | deployment-prep 이후에 실행. 배포 아티팩트를 PR에 포함 |

### 3.3 파이프라인 통합 옵션 (AIDLC 내 위치)

파이프라인에 넣을 경우, 위치는 build-and-test 성공 후가 자연스럽다.

```
build-and-test ✅ → [NEW] deployment-prep ──[게이트]── → finishing-branch
```

그러나 조직 표준 도구로서의 재활용성을 고려하면, **파이프라인 내장보다 독립 스킬이 적합**하다. (다음 섹션 참조)

---

## 4. 설계 방향: 조직 표준 도구로서의 재활용성

### 4.1 핵심 질문

deployment-prep을 **AIDLC 플러그인 전용 스킬**로 만들 것인가, **조직 내 누구나 쓸 수 있는 독립 도구**로 만들 것인가?

AIDLC를 쓰지 않는 개발자도 "코드 작성 → deployment-prep 호출 → Dockerfile + k8s manifests 생성"을 할 수 있어야 한다면, 독립 배포가 필요하다.

### 4.2 invoke_mode 결정

| 옵션 | 설명 | 장단점 |
|------|------|--------|
| `user-invocable` (독립 스킬) | 사용자가 직접 호출. AIDLC 없이도 사용 가능 | 재활용성 최대. 파이프라인 연동은 수동 |
| `orchestrator-only` | construction-orchestrator만 호출 | AIDLC 종속. 조직 표준으로 부적합 |
| `both` | 파이프라인에서도, 독립적으로도 호출 가능 | 유연하지만, 두 경로 모두 테스트/유지보수 필요 |

**권장: `user-invocable`** — 조직 표준 도구로서의 재활용성 우선. AIDLC 파이프라인에서 필요하면 construction-orchestrator가 사용자에게 "deployment-prep을 호출하시겠습니까?"로 안내하는 방식으로 연동.

---

## 5. 조직 표준 설정 체계

배포 환경은 조직마다 다르다. 설정을 3계층으로 분리하여 유연성을 확보한다.

### 5.1 설정 계층

| 계층 | 위치 | 역할 | 누가 관리하나 |
|------|------|------|-------------|
| **조직 기본값** | 스킬 내장 defaults | 보편적 베스트 프랙티스 | 스킬 작성자 |
| **조직 커스텀** | `~/.claude/deployment-prep.yml` | 조직 공통 설정 | 플랫폼팀 |
| **프로젝트 오버라이드** | 프로젝트 루트 `CLAUDE.md` 또는 `.deployment-prep.yml` | 프로젝트별 예외 | 각 팀 |

**우선순위**: 프로젝트 > 조직 커스텀 > 조직 기본값

### 5.2 조직 커스텀 설정 예시 (`~/.claude/deployment-prep.yml`)

```yaml
registry: harbor.company.internal
namespace_pattern: "{team}-{env}"       # e.g. platform-dev
base_images:
  python: harbor.company.internal/base/python:3.12-slim
  node: harbor.company.internal/base/node:20-alpine
  go: harbor.company.internal/base/go:1.22-alpine
security:
  non_root: true
  read_only_fs: true
  drop_all_capabilities: true
resource_defaults:
  cpu_request: "100m"
  memory_request: "128Mi"
```

### 5.3 운영 시나리오

1. **플랫폼팀**: `deployment-prep.yml` 템플릿을 조직 Wiki/내부 도구로 배포
2. **개발자**: 템플릿을 `~/.claude/`에 복사 → 설정 없이 바로 사용 가능
3. **특수 프로젝트**: `.deployment-prep.yml` 또는 CLAUDE.md에 오버라이드 추가
4. **설정 미존재 시**: 스킬이 대화형으로 필수 항목(레지스트리, 네임스페이스 등)을 질문

---

## 6. 배포 형태 비교: 단일 스킬 vs 별도 저장소

### 6.1 단일 스킬 파일 (경량)

```
배포 형태: SKILL.md 1개 (+ 선택적 템플릿 몇 개)
설치: npx skills add <gist-url> --skill deployment-prep
     또는 수동으로 .claude/skills/에 복사
```

**구조:**
```
deployment-prep/
├── SKILL.md           # 스킬 본체 (프롬프트 + 절차)
└── templates/         # (선택) Dockerfile/k8s 템플릿 스니펫
    ├── dockerfile-python.md
    └── k8s-base.md
```

**장점:**
- 설치/배포가 극도로 간단
- 유지보수 부담 최소 — 파일 하나 수정이면 끝
- 다른 플러그인(AIDLC 포함)에서 참조하기 쉬움
- 조직 내 Slack/Wiki로 공유하기에 적합

**한계:**
- 복잡한 로직(다양한 언어별 분기, 검증 파이프라인)이 SKILL.md 하나에 몰림
- 버전 관리/릴리즈 체계가 약함 (gist 기반이면 히스토리 추적이 불편)
- 테스트/CI를 붙이기 어려움

### 6.2 별도 저장소 (플러그인)

```
배포 형태: Git 저장소 (skills/ + _shared/ + README + CI)
설치: claude plugins add github:bluejayA/deployment-prep-plugin
```

**구조:**
```
deployment-prep-plugin/
├── skills/
│   └── deployment-prep/
│       └── SKILL.md
├── _shared/
│   ├── templates/
│   │   ├── dockerfiles/
│   │   │   ├── python.Dockerfile.tmpl
│   │   │   ├── node.Dockerfile.tmpl
│   │   │   └── go.Dockerfile.tmpl
│   │   └── k8s/
│   │       ├── deployment.yaml.tmpl
│   │       └── service.yaml.tmpl
│   ├── checklists/
│   │   └── security-checklist.md
│   └── config-schema.yml
├── tests/
│   └── ...
├── CLAUDE.md
└── README.md
```

**장점:**
- 구조화된 템플릿 관리 (언어별 Dockerfile, k8s 패턴별)
- 버전 태깅 + CHANGELOG로 조직 내 릴리즈 관리 가능
- CI에서 템플릿 검증 (hadolint, kubeval 등) 자동화
- 기여자 관리, 이슈 트래킹 가능
- 향후 확장(Helm, CI/CD 파이프라인 생성 등)에 자연스러운 공간

**한계:**
- 초기 셋업 비용이 높음
- "Dockerfile 하나 만들어줘"에 저장소 하나는 과할 수 있음
- 설치 단계가 하나 더 생김

### 6.3 판단 기준

| 질문 | 단일 스킬 | 별도 저장소 |
|------|----------|------------|
| 조직 내 5명 이하가 씀 | 적합 | 과함 |
| 조직 표준으로 10명+ 사용 | 부족할 수 있음 | 적합 |
| 언어/프레임워크 3개 이하 지원 | 충분 | 과함 |
| 다양한 스택 + 보안 정책 | 복잡해짐 | 적합 |
| MVP 빠르게 검증 | 바로 시작 | 셋업 필요 |
| AIDLC에서도 호출 필요 | 가능 | 가능 |

### 6.4 권장 전략: 단일 스킬로 시작 → 검증 후 저장소로 승격

MVP는 SKILL.md 하나로 빠르게 만들어서 실제로 써보고, 조직 표준으로 확장할 때 저장소로 분리한다. AIDLC 플러그인에서는 어느 형태든 `user-invocable`로 참조할 수 있으니 나중에 분리해도 호환성 문제가 없다.

---

## 7. MVP 실행 범위 (최종 정리)

1. **Dockerfile 생성** — 멀티스테이지 빌드, 비루트 사용자, 조직 설정의 베이스 이미지 적용
2. **k8s manifests 생성** — deployment.yaml + service.yaml, 프로덕션 최소 체크리스트:
   - `securityContext.runAsNonRoot: true`
   - CPU/메모리 requests + limits
   - liveness/readiness probe
3. **생성물에 인라인 주석 포함** — "왜 이 설정인지" 맥락을 주석으로 제공
4. **docker build 테스트** — 이미지 빌드 성공 확인
5. **dry-run 검증** — `kubectl apply --dry-run=client`

### 보안 경계

- **생성만 하고 배포는 하지 않는다.** 실제 배포는 사용자가 명시적으로 승인한 경우에만 별도 단계로 수행.

### 향후 확장 (MVP 이후)

- Helm chart 생성
- CI/CD 파이프라인 (GitHub Actions) 생성
- 환경 분리 (dev/staging/prod)
- 실제 샌드박스 배포 + smoke test
- PodDisruptionBudget (PDB) 생성
- `kubectl apply --dry-run=server` (MCP 서버 연동 시)

---

## 8. 논의 포인트

동료들과 논의할 때 결정이 필요한 항목:

1. **배포 형태**: 단일 스킬로 시작하는 것에 동의하는가? 처음부터 저장소가 필요한 이유가 있는가?
2. **설정 체계**: 3계층(스킬 기본값 / 조직 커스텀 / 프로젝트 오버라이드) 구조가 적절한가? `~/.claude/deployment-prep.yml`이 좋은 위치인가?
3. **조직 표준 범위**: 어떤 언어/프레임워크를 MVP에서 지원해야 하는가?
4. **보안 정책**: 조직에서 강제해야 할 보안 규칙이 추가로 있는가? (예: 특정 베이스 이미지만 허용, 네트워크 정책 필수 등)
5. **AIDLC 연동**: AIDLC 파이프라인과의 연동이 MVP에 필요한가, 아니면 독립 스킬로 충분한가?
