# 사용자 가이드

이 가이드는 aidlc 플러그인을 설치한 후 실제로 사용하는 방법을 안내합니다.

> 전체 흐름이 궁금하면 [AIDLC와 함께 개발하기](how-it-works.md)를 먼저 읽어보세요.
> 커스터마이즈가 필요하면 [운영자 가이드](operator-guide.md)를 참고하세요.

---

## 시작하기

### 세션 시작 시

플러그인이 설치되어 있으면 세션 시작 시 자동으로 안내 메시지가 표시됩니다:

```
🔧 AIDLC devflow 플러그인이 설치되어 있습니다.

시작하려면:
- 새 프로젝트: "devflow 시작해줘"
- 기존 프로젝트 이어하기: "devflow 재개해줘"
```

### 새 프로젝트 시작

"devflow 시작해줘"라고 입력하면 INCEPTION 단계가 시작됩니다:

1. **워크스페이스 감지** — 현재 디렉토리가 새 프로젝트인지, 기존 코드가 있는지 자동 판별
2. **요구사항 분석** — AI가 질문하며 요구사항을 함께 정리
3. **워크플로우 계획** — 어떤 단계를 거칠지 계획 수립
4. **설계** (선택) — 컴포넌트 구조 설계

각 단계마다 결과를 보여주고 승인을 요청합니다. 승인 없이 다음 단계로 넘어가지 않습니다.

### 기존 프로젝트 이어하기

"devflow 재개해줘"라고 입력하면 마지막으로 중단한 지점부터 재개합니다.
`devflow-state.md`와 `session-summary.md`를 읽어 컨텍스트를 복원합니다.
스테이지 진행 중에 세션이 끊겨도, 핵심 결정 시점마다 session-summary에 진행 상황이 기록되어 있어 맥락 유실을 최소화합니다.

---

## 질문에 답하기

AI가 질문할 때 두 가지 방식으로 답할 수 있습니다:

### 선택지에서 고르기
```
A) Next.js — React 기반, 풀스택 프레임워크
B) FastAPI — Python, API 서버
C) Spring Boot — Java, 엔터프라이즈
X) 직접 입력
```
→ "B" 또는 "FastAPI로 할게"

### 직접 상세하게 답하기
```
"Python 3.12 + FastAPI + PostgreSQL + Redis, 
테스트는 pytest, 패키지 관리는 uv로 할게"
```
→ AI가 추가 질문 없이 바로 반영합니다.

어떤 방식이든 자유롭게 선택할 수 있습니다. 선택지는 가이드일 뿐, 제한이 아닙니다.

---

## 승인 게이트

각 단계 완료 시 승인 게이트가 표시됩니다:

```
A) 변경 요청 → 수정 후 다시 표시
B) 승인, 다음 단계 진행
```

일부 게이트에는 추가 옵션이 있습니다:
- `H) 보류` — 나중에 돌아옴
- `S) 스킵` — 이 단계 건너뛰기
- `R) 리뷰 요청` — AI 서브에이전트가 산출물을 리뷰

### 게이트 도중 다른 작업이 필요할 때

게이트에서 A/B 대신 다른 요청을 하면 (예: "버그가 있어", "계획을 바꾸고 싶어"), AI가 자동으로 감지하고 적절한 스킬로 안내합니다:

```
현재 [code-generation] 단계를 진행 중입니다.
요청하신 내용은 [systematic-debugging]에 해당합니다.

A) 현재 작업 중단하고 디버깅 진행 (완료 후 복귀)
B) 현재 게이트에서 계속 진행
```

완료 후에는 원래 진행하던 지점으로 돌아갈 수 있습니다.

---

## 독립 스킬 사용

전체 워크플로우 없이 개별 스킬을 직접 호출할 수 있습니다:

| 스킬 | 호출 방법 | 용도 |
|------|----------|------|
| 브레인스토밍 | `/aidlc:aidlc-brainstorming` | 아이디어를 설계 문서로 |
| TDD | `/aidlc:aidlc-test-driven-development` | RED-GREEN-REFACTOR 사이클 |
| 디버깅 | `/aidlc:aidlc-systematic-debugging` | 버그 원인 조사 + 수정 |
| 코드 리뷰 | `/aidlc:aidlc-requesting-code-review` | 2-stage 코드 리뷰 |
| 브랜치 완료 | `/aidlc:aidlc-finishing-a-development-branch` | 머지/PR/보관 결정 |

또는 자연어로 요청하면 AI가 적절한 스킬을 자동으로 선택합니다.

> 새 SKILL.md를 작성하거나 기존 스킬을 편집·검증하려면 별도 플러그인 [`skill-forge`](https://github.com/bluejayA/skill-forge)의 `writing-skills` 스킬을 사용하세요. aidlc v1.14.0부터 이 자원은 분리되었습니다.

---

## 복잡도 (Complexity)

프로젝트 시작 시 복잡도를 선택합니다. 이것이 전체 워크플로우의 깊이를 결정합니다:

| 복잡도 | 적합한 경우 | 설계 분량 | 리뷰 |
|--------|-----------|----------|------|
| **Minimal** | 단일 파일/함수, 명확한 경로 | 2-5문장 | R1 (Stage 2만) |
| **Standard** | 새 컴포넌트, 복수 고려사항 | 표준 섹션 | R1 (Stage 2+3 병렬) |
| **Comprehensive** | 시스템 설계, 아키텍처 결정 | 전체 섹션 | R1 (Stage 2+3+4 병렬) |

AI가 복잡도를 판단하여 제안하지만, 항상 사용자가 조정할 수 있습니다.

---

## 프로젝트 프로파일 (선택)

프로젝트 루트에 `CLAUDE.md`를 생성하면 기술 스택과 설계 원칙을 사전 설정할 수 있습니다:

```markdown
## 기술 스택
- 언어: Python 3.12
- 프레임워크: FastAPI
- DB: PostgreSQL

## 설계 원칙
- TDD: 필수
- Complexity: Standard
```

명시된 항목은 질문 없이 자동 적용되고, 미명시 항목만 질문합니다.
프로파일은 선택사항입니다 — 없어도 워크플로우는 정상 동작합니다.

### 기술 스택 선택 우선순위

기술 스택은 다음 순서로 결정됩니다:

1. **CLAUDE.md 사전 고정** — 프로젝트별. 해당 계층의 질문 자체가 스킵됨
2. **사용자 프리셋** — 플러그인 전역. "이대로 사용? (Y/n)" 확인 1회. 거부 가능
3. **카탈로그 선택** — 위 두 가지로 커버되지 않는 계층만 질문

프리셋은 `tech-stack-defaults.md`에서 설정합니다. 기본 제공 프리셋: `Frontend Default` (Next.js + Tailwind CSS v4 + shadcn/ui). 자세한 운영 설정은 [운영자 가이드](operator-guide.md) §1을 참조하세요.

---

## 산출물

워크플로우 진행 중 생성되는 파일들:

```
devflow-docs/
├── inception/
│   ├── workspace.md          ← 워크스페이스 분석 결과
│   ├── requirements.md       ← 요구사항 문서
│   ├── workflow-plan.md      ← 워크플로우 계획
│   └── application-design.md ← 설계 문서 (선택)
├── construction/
│   └── {unit-name}/
│       ├── functional-design.md ← 기능 설계
│       └── code-plan.md         ← 코드 계획
├── backlog.md                ← 백로그 (Next/Open/Someday)
├── session-summary.md        ← 세션 요약 (재개용)
├── devflow-state.md          ← 상태 추적
└── audit.md                  ← 상호작용 로그
```

### 세션 재개 시

재개 시 devflow-state의 상태에 따라 자동 분기됩니다:
- `finished` → 이전 플로우 아카이브 후 새 작업 시작
- `complete + PR pending` → PR 머지 확인
- `INCEPTION/CONSTRUCTION` → 해당 단계에서 재개

백로그가 있으면 건수만 표시하고, 내용은 요청 시에만 로드합니다 (Lazy Loading).

---

## 워크플로우 검증

오케스트레이터 스킬을 수정한 후 워크플로우의 정확성을 검증할 수 있습니다:

```bash
bash tests/run-all.sh
```

이 명령은 오케스트레이터의 분기 로직, 라우팅 경로, 스텝 순서를 자동으로 검증합니다.
일반적인 개발에서는 실행할 필요 없으며, 플러그인 자체를 수정할 때 사용합니다.

---

## 도움이 필요할 때

| 상황 | 방법 |
|------|------|
| 전체 흐름 이해 | [AIDLC와 함께 개발하기](how-it-works.md) |
| 커스터마이즈 | [운영자 가이드](operator-guide.md) |
| 아키텍처 이해 | [아키텍처 문서](architecture.md) |
| 워크플로우 검증 | `bash tests/run-all.sh` |
| 버그/문제 | GitHub Issues |
