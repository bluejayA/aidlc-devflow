# AI-DLC (AI-Driven Development Life Cycle) 분석

- **작성일**: 2026-03-10
- **출처**: https://github.com/awslabs/aidlc-workflows

---

## 개요

AWS가 제안한 AI 주도 소프트웨어 개발 생명주기 방법론.
AI를 단순 보조 도구가 아닌 **개발 프로세스의 핵심 드라이버**로 위치시킴.

> "워크플로우가 작업에 맞게 적응한다. 반대가 아니라."

**핵심 원칙**: AI가 워크플로우를 주도하되, 책임은 항상 인간이 진다.
**사용 트리거**: 채팅에서 `"Using AI-DLC, ..."` 로 시작하면 자동 활성화.

---

## 레포지토리 구조

```
aidlc-rules/
├── aws-aidlc-rules/
│   └── core-workflow.md              # 항상 로드되는 핵심 워크플로우
└── aws-aidlc-rule-details/
    ├── common/                       # 공통 규칙 (항상 로드)
    │   ├── process-overview.md
    │   ├── session-continuity.md
    │   ├── content-validation.md
    │   ├── question-format-guide.md
    │   └── welcome-message.md
    ├── inception/                    # Inception 단계 상세 규칙
    │   ├── workspace-detection.md
    │   ├── reverse-engineering.md
    │   ├── requirements-analysis.md
    │   ├── user-stories.md
    │   ├── workflow-planning.md
    │   ├── application-design.md
    │   └── units-generation.md
    ├── construction/                 # Construction 단계 상세 규칙
    │   ├── functional-design.md
    │   ├── nfr-requirements.md
    │   ├── nfr-design.md
    │   ├── infrastructure-design.md
    │   ├── code-generation.md
    │   └── build-and-test.md
    ├── operations/                   # 현재 placeholder
    └── extensions/                   # 확장 규칙
        └── security/
            └── baseline/
                └── security-baseline.md
```

---

## 3단계 워크플로우

### 🔵 INCEPTION PHASE — 무엇을 만들지 결정

| 스테이지 | 실행 조건 | 설명 |
|---------|---------|------|
| Workspace Detection | **항상** | 그린필드/브라운필드 판단, 세션 재개 여부 |
| Reverse Engineering | 조건부 (브라운필드만) | 기존 코드 분석, 아키텍처 문서화 |
| Requirements Analysis | **항상** (깊이 조절) | Minimal / Standard / Comprehensive |
| User Stories | 조건부 (사용자 영향 시) | Plan → Generate 2단계 |
| Workflow Planning | **항상** | 실행할 단계 결정, 시각화 |
| Application Design | 조건부 (신규 컴포넌트 시) | 컴포넌트/서비스 설계 |
| Units Generation | 조건부 (복잡한 분해 시) | 병렬 개발 단위 분해 |

### 🟢 CONSTRUCTION PHASE — 어떻게 만들지 결정

각 Unit별로 루프 실행:

| 스테이지 | 실행 조건 |
|---------|---------|
| Functional Design | 조건부 — 새 데이터 모델 / 복잡한 비즈니스 로직 |
| NFR Requirements | 조건부 — 성능 / 보안 / 확장성 요건 |
| NFR Design | 조건부 — NFR Requirements 실행 시 |
| Infrastructure Design | 조건부 — 인프라 변경 시 |
| Code Generation | **항상** — Plan → Approve → Generate |
| Build and Test | **항상** — 모든 Unit 완료 후 |

### 🟡 OPERATIONS PHASE — 현재 Placeholder

미래 배포/모니터링 자동화 예정.

---

## 산출물 구조

```
aidlc-docs/                     # 문서만 저장 (코드 X)
├── inception/
│   ├── requirements/
│   ├── user-stories/
│   └── application-design/
├── construction/
│   └── {unit-name}/
│       ├── functional-design/
│       └── code/               # 마크다운 요약만
├── aidlc-state.md              # 세션 상태 추적
└── audit.md                    # 모든 사용자 입력/AI 응답 로그 (append-only)
```

실제 코드는 워크스페이스 루트에 저장 (`aidlc-docs/` 바깥).

---

## 지원 도구별 설치 방법

| 도구 | 규칙 파일 위치 |
|------|--------------|
| **Claude Code** | `CLAUDE.md` (프로젝트 루트) 또는 `.claude/CLAUDE.md` |
| Amazon Q | `.amazonq/rules/aws-aidlc-rules/` |
| Kiro | `.kiro/steering/aws-aidlc-rules/` |
| Cursor | `.cursor/rules/ai-dlc-workflow.mdc` |
| Cline | `.clinerules/core-workflow.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |

---

## Extensions 시스템

`extensions/` 디렉토리에 커스텀 규칙 추가 가능.

- 기본 제공: `security/baseline/security-baseline.md`
- 추가 가능: 조직 정책, HIPAA / PCI-DSS / SOC2 컴플라이언스
- 각 Extension은 Inception 단계에서 적용 여부를 묻는 질문 포함
- 활성화 시 **모든 단계의 blocking constraint**로 작동
- `aidlc-docs/aidlc-state.md`의 `## Extension Configuration`에 활성화 상태 기록

---

## 핵심 설계 원칙 (Tenets)

| 원칙 | 설명 |
|------|------|
| No duplication | 소스는 단 하나 |
| Methodology first | 도구보다 방법론이 우선 |
| Reproducible | 모델이 달라도 일관된 결과 |
| Agnostic | 어떤 IDE / 에이전트 / 모델과도 작동 |
| Human in the loop | AI가 제안, 인간이 승인 |

---

## 중요 동작 규칙

- **Rule Details 로딩**: 단계 실행 전 해당 `.md` 파일 반드시 읽기
- **Content Validation**: 파일 생성 전 Mermaid 문법 등 검증 필수
- **Checkbox 추적**: 계획 파일의 체크박스를 완료 즉시 업데이트
- **audit.md**: 항상 append만 가능, 덮어쓰기 금지
- **승인 게이팅**: 각 단계 완료 후 반드시 사용자 승인 대기
- **NO EMERGENT BEHAVIOR**: Construction 단계는 표준 2-option 완료 메시지만 사용
