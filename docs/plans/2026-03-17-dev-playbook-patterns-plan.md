# dev-playbook 공유 패턴 2종 반영 구현 계획

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 질문 설계 원칙(question-format-guide)과 기술 카탈로그(tech-stack-defaults)를 `_shared/patterns/`에 추가하여 비개발자~고급 개발자 대응 질문 품질 향상

**Architecture:** question-format-guide가 질문의 HOW(원칙), tech-stack-defaults가 기술 스택 질문의 WHAT(데이터)을 담당. question-format-guide → tech-stack-defaults 단방향 참조. conventions에 참조 1줄 추가.

**Spec:** `docs/plans/2026-03-17-dev-playbook-patterns-design.md`
**이슈:** #12

**dev-playbook 원본 경로:**
- `~/projects/ai/dev-playbook-ai-coding/.claude/shared/question-format-guide.md` (259줄)
- `~/projects/ai/dev-playbook-ai-coding/.claude/shared/tech-stack-defaults.md` (237줄)

---

## Task 1: `_shared/patterns/question-format-guide.md` 신규 생성

**Files:**
- Create: `skills/_shared/patterns/question-format-guide.md`
- Reference (read-only): `~/projects/ai/dev-playbook-ai-coding/.claude/shared/question-format-guide.md`

**dev-playbook 원본 읽기 지침:**
- 원본의 파일 기반 질문 형식(`{phase-name}-questions.md`, `[Answer]:` 태그)은 **채택하지 않음** — aidlc는 채팅 기반
- 추출할 원칙: 선택지 설계, 자유 입력, 모순 감지, 수준 적응
- dev-playbook 고유 워크플로우("Workflow Integration" 4단계 등)는 제외

- [ ] **Step 1: dev-playbook 원본 읽기 + 원칙 추출**

`~/projects/ai/dev-playbook-ai-coding/.claude/shared/question-format-guide.md`를 읽고 다음을 추출:
- Multiple Choice Guidelines (옵션 개수, 의미 있는 옵션만)
- Contradiction and Ambiguity Detection 패턴
- Error Handling (Missing/Invalid/Ambiguous Answers)
- Best Practices

채택하지 않을 부분 식별:
- 파일 기반 질문 형식 (MANDATORY 규칙, Question File Format)
- Workflow Integration (4단계: Create → Inform → Wait → Read)
- Claude Code Specific 파일 편집 로직

- [ ] **Step 2: 문서 작성 — 선택지 설계 원칙 + 자유 입력 보장**

```markdown
# Question Format Guide

<!-- 사용자 질문 설계 원칙. 비개발자부터 고급 개발자까지 대응. -->

## 이 문서의 목적

스킬이 사용자에게 질문할 때 따라야 할 원칙.
질문의 품질이 산출물의 품질을 결정한다.

## 1. 선택지 설계 원칙

### 선택지 개수
- 최소 2개 + "직접 입력" (Other)
- 최대 5개 + "직접 입력" (Other)
- 1개만 있으면 질문이 아니라 확인 — "이대로 진행할까요? (Y/N)"으로 변경

### 의미 있는 옵션만
- 채우기용/형식적 선택지 금지
- 각 선택지가 실제로 다른 결과를 만들어야 함
- 나쁜 예: A) REST API / B) REST API + 인증 / C) REST API + 인증 + 로깅 (단계적 추가는 선택이 아님)
- 좋은 예: A) REST API / B) GraphQL / C) gRPC / X) 직접 입력

### 비개발자 친화적 표현
- 전문 용어 사용 시 한 줄 설명 병기
- 나쁜 예: A) Next.js B) Remix C) SvelteKit
- 좋은 예: A) Next.js — React 기반, 풀스택 프레임워크 / B) Remix — React 기반, 서버 중심 / C) SvelteKit — Svelte 기반, 경량

## 2. 자유 입력 보장

### 모든 선택지에 "직접 입력" 필수
- 마지막 옵션으로 `X) 직접 입력` 항상 포함
- 선택지는 가이드일 뿐, 사용자의 선택을 제한하지 않음

### 상세 답변 즉시 수용
- 사용자가 선택지 무시하고 상세 답변을 주면 그대로 반영
- "Rust + Axum + SQLx, PostgreSQL로 할게" → 추가 질문 없이 수용
- 선택지로 돌아가라고 강요하지 않음
```

- [ ] **Step 3: 문서 작성 — 모순 감지 + 수준 적응**

```markdown
## 3. 모순 감지 + 보충 질문

### 감지 대상
- 이전 답변과 현재 답변 사이 불일치
- 요구사항 간 상충 (예: "빠른 개발" + "모든 엣지 케이스 커버")

### 대응 원칙
- **판단하지 않고 질문한다** — "이건 모순입니다"가 아니라 "확인하고 싶은 게 있습니다"
- **의도적 모순 존중** — 사용자가 이유를 설명하면 그대로 진행
- **구체적으로 질문** — "앞서 프로토타입이라고 하셨는데, 엔터프라이즈급 보안이 필요한 특별한 이유가 있을까요?"

### 보충 질문 형식
```
앞서 [이전 답변 요약]이라고 하셨는데,
지금 [현재 답변 요약]을 선택하셨습니다.

A) [이전 답변 기준으로 조정] — [설명]
B) [현재 답변 유지] — [설명]
C) 둘 다 필요 — [어떤 경우에 가능한지]
X) 직접 설명
```

## 4. 수준 적응

### 감지 방법
- 첫 1-2개 질문의 답변 스타일로 판단
- 짧은 답변 (A, B, 선택지 번호만) → 가이드 모드: 후속 질문으로 구체화
- 상세 답변 (기술명, 이유, 제약조건 포함) → 전문가 모드: 추가 질문 최소화

### 가이드 모드 (비개발자)
- 선택지에 설명 병기
- 한 번에 하나씩만 질문
- 선택 결과가 어떤 영향을 미치는지 간략 안내

### 전문가 모드 (고급 개발자)
- 답변에 포함된 정보로 여러 질문을 한꺼번에 해소
- 불필요한 확인 질문 스킵
- "다음 질문으로 넘어가겠습니다" 대신 바로 다음 단계 진행
```

- [ ] **Step 4: 문서 작성 — 카탈로그 연결 + 적용 범위**

```markdown
## 카탈로그 연결

기술 스택 관련 선택지 생성 시 `_shared/patterns/tech-stack-defaults.md`의 카탈로그를 활용한다.

- 사용자의 아키텍처 유형에 맞는 기술만 필터링하여 선택지에 포함
- 카탈로그에 없는 기술도 "직접 입력"으로 수용

## 적용 범위

이 원칙을 적용하는 스킬:
- 사용자에게 직접 질문하는 모든 INCEPTION 스킬
- 특히 `requirements-analysis`, `nfr-requirements`, `workspace-detection`
- 오케스트레이터의 게이트 선택지도 이 원칙을 따름
```

- [ ] **Step 5: 전체 문서 조립 + 검증**

확인 항목:
- 4가지 원칙이 모두 포함되었는가?
- dev-playbook의 파일 기반 형식이 남아있지 않은가?
- gate-patterns.md의 기존 선택지 형식과 충돌하지 않는가?
- 예시가 구체적이고 실제적인가?

- [ ] **Step 6: 커밋**

```bash
git add skills/_shared/patterns/question-format-guide.md
git commit -m "docs: question-format-guide.md 신규 생성 — 선택지 설계, 수준 적응, 모순 감지 (refs #12)"
```

---

## Task 2: `_shared/patterns/tech-stack-defaults.md` 신규 생성

**Files:**
- Create: `skills/_shared/patterns/tech-stack-defaults.md`
- Reference (read-only): `~/projects/ai/dev-playbook-ai-coding/.claude/shared/tech-stack-defaults.md`

**dev-playbook 원본 읽기 지침:**
- 원본 237줄의 구조(아키텍처 패턴 → 카탈로그 매핑, 계층별 비교표)를 기본 뼈대로 활용
- Jay의 주요 언어(Python, Go, Rust, Swift, Java/Spring)를 반영하여 우선순위 조정
- CLAUDE.md의 언어별 컨벤션과 일관되도록 정렬
- aidlc에서 불필요한 섹션(dev-playbook 전용 적용 규칙 등)은 제외

- [ ] **Step 1: dev-playbook 원본 읽기 + 구조 추출**

`~/projects/ai/dev-playbook-ai-coding/.claude/shared/tech-stack-defaults.md`를 읽고 다음을 추출:
- 아키텍처 패턴 → 카탈로그 매핑 구조
- 각 계층별 기술 비교표
- 적용 규칙

aidlc에 맞게 조정할 부분 식별:
- Jay의 주요 언어 반영 (Python 우선, Go, Rust, Swift, Java/Spring)
- CLAUDE.md 패키지 관리 도구(uv, poetry, gofmt, cargo 등)와 일관성

- [ ] **Step 2: 문서 작성 — 헤더 + 아키텍처 패턴 매핑**

```markdown
# Tech Stack Defaults

<!-- 기술 스택 질문의 선택지 생성 데이터. question-format-guide.md와 함께 사용한다. -->

## 사용법

1. 사용자의 프로젝트 유형(아키텍처 패턴)을 확인한다
2. 해당 패턴에 맞는 카탈로그 계층만 필터링한다
3. `question-format-guide.md`의 선택지 설계 원칙에 따라 선택지를 구성한다
4. 카탈로그에 없는 기술도 "직접 입력"으로 수용한다

## 아키텍처 패턴 → 카탈로그 매핑

| 패턴 | 필요 계층 |
|------|----------|
| 웹 애플리케이션 | Frontend + Backend + Database + Deployment |
| API 서버 | Backend + API 스타일 + Database + Deployment |
| CLI 도구 | Backend(언어) + CLI/TUI + Testing |
| 모바일 앱 | Frontend(Mobile) + Backend(API) + Database |
| 라이브러리/패키지 | Backend(언어) + Testing |
| 데이터 파이프라인 | Backend + Database + Infrastructure |
```

- [ ] **Step 3: 문서 작성 — 기술 카탈로그 (Frontend, Backend, API, Database)**

dev-playbook 원본의 비교표를 기반으로, Jay의 주요 언어를 반영하여 작성.
각 항목: 기술명 + 한 줄 설명 + 적합한 상황.

주요 계층:
- Frontend (SPA/메타프레임워크, 디자인 시스템)
- Backend (경량: FastAPI, Gin / 엔터프라이즈: Spring Boot, Django / 고성능: Axum, Actix)
- API 스타일 (REST, tRPC, gRPC)
- Database (RDBMS, NoSQL, 캐시, 검색, 벡터)

- [ ] **Step 4: 문서 작성 — 나머지 계층 (CLI, Testing, Infrastructure) + 적용 규칙**

나머지 계층:
- CLI/TUI
- Testing & Deployment (린트 → 단위테스트 → API테스트 → 컨테이너)
- Infrastructure (CI/CD, IaC, 옵저버빌리티, 인증)

적용 규칙:
```markdown
## 적용 규칙

### Greenfield
1. 아키텍처 패턴 질문 → 매핑 테이블에서 필요 계층 확인
2. 각 계층에서 2~5개 선택지 + "직접 입력" 제시
3. 사용자 선택을 산출물에 기록

### Brownfield
1. workspace-detection 결과에서 감지된 기술 확인
2. 카탈로그와 교차 확인하여 누락/비표준 기술 식별
3. 필요 시 보충 질문

### 공통
- 카탈로그에 없는 기술도 사용자 직접 입력 시 수용
- 선택지 표현은 question-format-guide.md의 비개발자 친화적 원칙 적용
```

- [ ] **Step 5: 전체 문서 조립 + 검증**

확인 항목:
- CLAUDE.md의 언어별 컨벤션(uv, ruff, gofmt, cargo fmt 등)과 일치하는가?
- question-format-guide.md의 선택지 원칙과 일관되는가?
- dev-playbook 원본의 핵심 구조가 유지되었는가?
- 불필요한 기술이 포함되지 않았는가? (YAGNI)

- [ ] **Step 6: 커밋**

```bash
git add skills/_shared/patterns/tech-stack-defaults.md
git commit -m "docs: tech-stack-defaults.md 신규 생성 — 아키텍처별 기술 카탈로그 (refs #12)"
```

---

## Task 3: `devflow-conventions.md` 수정

**Files:**
- Modify: `skills/_shared/devflow-conventions.md`

- [ ] **Step 1: 새 스킬 추가 가이드에 참조 추가**

"새 스킬 추가 가이드" 섹션의 항목 끝에 추가:

```markdown
7. **사용자 질문 설계**: `_shared/patterns/question-format-guide.md` — 선택지 설계, 수준 적응, 모순 감지
```

- [ ] **Step 2: 검증 + 커밋**

기존 항목 번호와 일치하는지 확인. 참조 경로가 실제 파일과 일치하는지 확인.

```bash
git add skills/_shared/devflow-conventions.md
git commit -m "docs: conventions에 question-format-guide 참조 추가 (closes #12)"
```

---

## 최종 마무리

### Task 4: 이슈 코멘트 + 백로그 상태 업데이트

- [ ] **Step 1: GitHub 이슈 #12에 완료 코멘트**

변경 내용 요약 + 커밋 해시 목록.

- [ ] **Step 2: GitHub Project 상태 업데이트**

"Devflow-AIDLC : Backlog Tracking" 프로젝트에서 이슈 #12를 "Done"으로 이동.

- [ ] **Step 3: 백로그 상태 동기화**

`memory/backlog_aidlc.md`에서 BL-013 상태를 `Done`으로 변경.
