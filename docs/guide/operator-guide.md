# 운영자 가이드

이 가이드는 aidlc 플러그인을 설치한 운영자가 조직과 프로젝트에 맞게 커스터마이즈하는 방법을 안내합니다.

---

## 1. 기술 스택 정책

기술 스택 선택의 자유도를 조직 정책에 맞게 제어하는 3가지 메커니즘을 제공합니다. 조합하여 사용하면 가장 효과적입니다.

### 1-1. 정책 모드 설정

**파일**: `skills/_shared/patterns/tech-stack-defaults.md` → `## 정책 모드` 섹션

사용자가 기술 스택을 선택할 때 "직접 입력"(카탈로그 외 기술)의 허용 수준을 결정합니다.

| 모드 | 카탈로그 외 기술 | 적합한 조직 |
|------|----------------|-----------|
| **open** (기본) | 자유 허용 | 기술 선택 제한이 없는 조직 |
| **guided** | 사유 기록 후 허용 | 표준은 있지만 예외를 허용하는 조직 |
| **strict** | 차단 | 기술 표준 준수가 필수인 조직 |

**변경 방법**: `tech-stack-defaults.md` 상단의 `현재 모드: open`을 원하는 모드로 변경.

**guided 모드의 추적 흐름**:
1. 사용자가 카탈로그 외 기술을 선택
2. AI가 사유를 질문
3. 사유가 `requirements.md`의 `## 기술 스택 결정` 테이블에 기록
4. 운영자가 주기적으로 requirements.md를 확인하여 카탈로그 갱신 여부 판단

> **권장**: 대부분의 조직에 **guided**를 권장합니다. 표준 이탈을 차단하지 않으면서도 추적할 수 있어, 카탈로그를 점진적으로 개선하는 데이터가 됩니다.

### 1-2. 카탈로그 커스터마이즈

**파일**: `skills/_shared/patterns/tech-stack-defaults.md` → 기술 카탈로그 섹션

정책 모드와 별도로, 카탈로그 자체를 조직 표준에 맞게 조정합니다.

| 항목 | 방법 | 예시 |
|------|------|------|
| 기술 추가 | 해당 계층 테이블에 행 추가 | Backend에 `Ktor — Kotlin, 경량 비동기` 추가 |
| 기술 제거 | 조직에서 금지된 기술 행 삭제 | 보안상 `MongoDB` 제거 |
| 우선순위 변경 | 테이블 내 행 순서 조정 | 조직 표준인 `Go`를 Backend 최상단으로 |
| 카테고리 추가 | 새 계층 섹션 추가 | `ML/AI` 계층 (PyTorch, TensorFlow 등) |

**조정 예시 — 조직 기술 표준 반영**:

조직이 Python + FastAPI + PostgreSQL을 표준으로 사용한다면:

1. Backend 테이블에서 `FastAPI`를 최상단으로 이동
2. Database 테이블에서 `PostgreSQL`을 최상단으로 이동
3. 금지 기술이 있으면 해당 행 삭제 (또는 주석 처리)

**주의사항**:
- 테이블 형식(기술명 + 한 줄 설명 + 적합한 상황)을 유지하세요
- 아키텍처 패턴 → 카탈로그 매핑 테이블도 함께 업데이트하세요
- open 모드에서는 카탈로그에 없어도 직접 입력 가능하므로, 모든 기술을 넣을 필요는 없습니다
- strict 모드에서는 카탈로그 = 허용 목록이므로, 허용할 기술을 빠짐없이 포함하세요

### 1-3. 프로젝트 CLAUDE.md로 기술 사전 고정

가장 강력한 방법입니다. 프로젝트별 `CLAUDE.md`에 기술 스택을 명시하면 **기술 스택 질문 자체가 스킵**됩니다.

조직 전체에 CLAUDE.md 템플릿을 배포하여 프로젝트 생성 시 자동 적용되게 하면, 정책 모드와 무관하게 기술을 고정할 수 있습니다.

**템플릿 예시**:

```markdown
## 기술 스택 (회사 표준)
- 언어: Python 3.12 | Go 1.22
- 프레임워크: FastAPI (Python) | Gin (Go)
- DB: PostgreSQL 16
- 캐시: Redis
- CI/CD: GitHub Actions
- 컨테이너: Docker 멀티스테이지
- IaC: Terraform
- 테스트: pytest (Python) | 표준 testing (Go)

## 설계 원칙
- TDD: 필수
- Complexity: Standard
```

**동작 원리**: workspace-detection이 CLAUDE.md를 읽고, 기술 스택이 명시되어 있으면 tech-stack-defaults.md 카탈로그를 참조하지 않고 바로 수용합니다. 이 경우 정책 모드(open/guided/strict)가 적용되는 상황 자체가 발생하지 않습니다.

### 권장 조합

| 시나리오 | 정책 모드 | 카탈로그 | CLAUDE.md |
|---------|----------|---------|-----------|
| 스타트업 (자유) | open | 기본 유지 | 선택 |
| 중견 기업 (표준 있음, 예외 허용) | **guided** | 표준으로 축소 + 순서 조정 | 템플릿 배포 권장 |
| 대기업 (엄격한 표준) | strict | 허용 목록만 남김 | 템플릿 필수 배포 |

---

## 2. 질문 설계 원칙 조정

**파일**: `skills/_shared/patterns/question-format-guide.md`

이 파일은 스킬이 사용자에게 질문할 때 따르는 4가지 원칙을 정의합니다.

### 4가지 원칙 요약

| 원칙 | 내용 | 운영자 조정 포인트 |
|------|------|------------------|
| **선택지 설계** | 2~5개 + 직접 입력, 의미 있는 옵션만 | 선택지 표현을 조직 용어로 변경 |
| **자유 입력 보장** | 모든 질문에 직접 입력 옵션 | 기술 스택 질문은 §1 정책 모드에 따라 자동 조정 |
| **모순 감지** | 답변 간 불일치 시 보충 질문 | 보충 질문 톤/표현 조정 |
| **수준 적응** | 답변 스타일로 가이드/전문가 모드 전환 | 기본 모드 설정 |

### 기본 모드 설정

조직의 주 사용자 수준에 따라 기본 모드를 조정할 수 있습니다:

- **비개발자 중심 조직**: 가이드 모드를 기본으로 — 선택지에 항상 설명 병기, 한 번에 하나씩 질문
- **개발자 중심 조직**: 전문가 모드를 기본으로 — 설명 최소화, 다중 질문 해소 허용
- **혼합**: 기본값 변경 없이 수준 적응에 맡김 (권장)

조정 방법: `question-format-guide.md`의 "수준 적응" 섹션에서 기본 동작을 명시.

### 선택지 표현 변경

조직 내부 용어가 있다면 선택지 예시를 조정하세요:

```markdown
# 변경 전 (일반적 표현)
A) REST API — HTTP 기반, 범용적

# 변경 후 (조직 용어)
A) REST API — 우리 팀 표준, API Gateway 연동 가능
```

---

## 3. 워크플로우 기본값 설정

**파일**: `skills/_shared/devflow-conventions.md`

이 파일은 모든 스킬이 따르는 공통 규약입니다. 운영자가 조정할 수 있는 항목:

### 조정 가능 항목

| 항목 | 위치 | 기본값 | 조정 예시 |
|------|------|--------|----------|
| **TDD 필수 여부** | `## TDD Iron Law` | 필수 | 프로토타입 프로젝트에서 선택적으로 변경 |
| **리뷰 depth 기본값** | `## Complexity와 Stage Depth` | Complexity 연동 | 소규모 팀은 Minimal 고정 |
| **리뷰 루프 최대 횟수** | `## 리뷰 규약` | 5회 | 빠른 iteration 필요 시 3회로 축소 |
| **서브에이전트 모델 선택** | `## Subagent Dispatch Rules` | 역할별 분리 | 비용 절감 시 모든 역할에 동일 모델 |
| **Brainstorming 필수 여부** | `## Brainstorming HARD-GATE` | 항상 필수 | 반복 작업에 한해 스킵 허용 |

### 조정 방법

conventions.md를 직접 수정합니다. 변경 시 주의사항:

1. **기존 구조를 유지하세요** — 섹션 제목과 순서를 바꾸면 스킬이 참조를 못 찾을 수 있습니다
2. **값만 변경하세요** — "최대 5회" → "최대 3회" 같은 수준
3. **변경 이유를 주석으로 남기세요** — 나중에 왜 바꿨는지 추적 가능

```markdown
## 리뷰 규약

### 리뷰 루프
<!-- 운영자 변경: 5회 → 3회 (소규모 팀, 빠른 iteration 우선) -->
1. 리뷰어 dispatch → 최대 3회
```

---

## 4. 프로젝트 프로파일

새 프로젝트를 시작할 때 기술 스택과 설계 원칙을 사전에 설정할 수 있습니다.

> **기술 스택 고정**: CLAUDE.md로 기술 스택을 사전 고정하는 방법과 조직 템플릿 배포에 대해서는 §1-3을 참조하세요.

### 설정 방법: 프로젝트 CLAUDE.md

각 프로젝트 루트에 `CLAUDE.md`를 생성하고 프로파일을 명시합니다:

```markdown
# 프로젝트 설정

## 기술 스택
- 언어: Python 3.12
- 프레임워크: FastAPI
- DB: PostgreSQL + Redis (캐시)
- 테스트: pytest
- 패키지: uv

## 설계 원칙
- TDD: 필수
- Complexity: Standard
- 리뷰: Standard depth
```

### 워크플로우 반영 흐름

```
프로젝트 시작
  → aidlc-using-devflow 호출
    → workspace-detection이 CLAUDE.md 읽음
      → 기술 스택이 명시되어 있으면 tech-stack 질문 스킵 (정책 모드 불문)
      → 미명시 항목만 질문 (이때 정책 모드 적용)
    → 설계 원칙이 명시되어 있으면 conventions 기본값 대신 적용
```

### 프로파일 없이 시작하면?

- workspace-detection이 Greenfield/Brownfield를 판별하고
- tech-stack-defaults.md 카탈로그에서 선택지를 생성하여 질문 (정책 모드에 따라 "직접 입력" 동작 결정)
- conventions.md의 기본값이 적용

프로파일은 **선택사항**입니다. 없어도 워크플로우는 정상 동작합니다.

---

## 5. 스킬 추가/수정

### 새 스킬 추가 시 참조 문서 맵

```
1. skill-writing-guide.md      ← 구조 설계 원칙 + TDD 방법론 (자유도, 점진적 공개, 500줄, 압박 시나리오)
   ↓
2. skill-pattern-catalog.md    ← 7개 패턴 중 적합한 것 선택
   ↓
3. writing-skills SKILL.md     ← TDD 프로세스 (RED → GREEN → REFACTOR)
   ↓
4. skill-reviewer-prompt.md    ← 배포 전 자동 검증
```

### 기존 스킬 수정 시 영향 범위 확인

1. **해당 스킬의 `invoke_mode` 확인**
   - `orchestrator-only`: 오케스트레이터가 호출 → 오케스트레이터의 게이트/라우팅에 영향
   - `user-invocable`: 사용자 직접 호출 가능 → standalone 동작도 검증 필요

2. **참조 관계 확인**
   - 이 스킬이 `_shared/` 문서를 참조하는가?
   - 다른 스킬이나 오케스트레이터가 이 스킬을 참조하는가?

3. **리뷰어로 검증**
   - `_shared/reviewers/skill-reviewer-prompt.md`를 서브에이전트로 dispatch
   - 구조 검증 + 내용 검증 + CSO 검증 3영역 자동 확인

### 스킬 삭제 시

1. 오케스트레이터에서 해당 스킬 참조 제거
2. `devflow-conventions.md`에서 관련 언급 제거
3. `skill-pattern-catalog.md`에서 해당 스킬 항목 제거
4. 디렉토리 삭제

---

## 6. 메타 태그 시스템

**규격 문서**: `skills/_shared/patterns/meta-tag-standard.md`
**테스트**: `bash tests/run-all.sh`

오케스트레이터 SKILL.md에 HTML 주석 형태의 메타 태그(`@gate`, `@gate-option`, `@step`, `@condition`)가 삽입되어 있다. 이 태그는 분기/라우팅/스텝 순서를 기계적으로 검증하는 데 사용된다.

### 스킬 수정 시 태그 동기화

게이트 추가/삭제, 옵션 변경, 스텝 순서 변경 등 오케스트레이터의 라우팅 로직을 수정하면 메타 태그도 함께 업데이트해야 한다. 태그가 불일치하면 `tests/run-all.sh` 실행 시 실패한다.

- 태그 변경이 필요한 상황과 동기화 방법: `_shared/patterns/meta-tag-standard.md` → Maintenance 섹션 참조
- Claude로 개발하는 경우 TDD(build-and-test)가 불일치를 자동 검출하므로, 별도 수동 체크 없이 테스트 실패로 인지 가능

---

## 도움이 필요할 때

| 상황 | 참조 문서 |
|------|----------|
| 전체 아키텍처 이해 | `_shared/devflow-conventions.md` |
| 스킬 작성법 | `aidlc-writing-skills/SKILL.md` |
| 패턴 종류 | `_shared/patterns/skill-pattern-catalog.md` |
| 게이트 구조 | `_shared/gate-patterns.md` |
| 질문 설계 | `_shared/patterns/question-format-guide.md` |
| 기술 카탈로그 | `_shared/patterns/tech-stack-defaults.md` |
| TDD 프로토콜 | `_shared/tdd-protocol.md` |
| 메타 태그 규격 | `_shared/patterns/meta-tag-standard.md` |
| 테스트 실행 | `tests/run-all.sh` |
