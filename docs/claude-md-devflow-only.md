# Claude Code 설정 (devflow 샘플)

> **사용 방법**: 프로젝트 루트 또는 `~/.claude/CLAUDE.md`에 복사 후,
> `## 나에 대해`와 `## 워크스페이스 구조`를 본인 환경에 맞게 수정하세요.

---

## 나에 대해

- **이름**: (본인 이름)
- **역할**: (예: 풀스택 개발자)
- **주요 언어**: (예: Python, TypeScript, Go)
- **대화 언어**: (예: 한국어 응답, 코드/변수명은 영어)

---

## 개발 워크플로우 (devflow)

| 경로 | 조건 | 진행 방식 |
|------|------|-----------|
| **A — 전체** | 새 기능/컴포넌트/서비스 | `using-devflow` → A/B 게이팅으로 스테이지별 진행 |
| **B — 경량** | 단일 파일 수정/버그 픽스 | TDD (RED→GREEN→REFACTOR) + `verification-before-completion` |
| **C — 디버깅** | 원인 불명 오류 | `systematic-debugging` → 원인 확정 후 A 또는 B로 전환 |

### 경로 A 상세

- **파이프라인**: workspace-detection → requirements-analysis → workflow-planning → (application-design?) → (units-generation?) → code-generation (TDD) → build-and-test
- **병렬 구현**: 독립 태스크 2개 이상 시 `dispatching-parallel-agents`로 서브에이전트 병렬 실행
- **코드 리뷰**: `requesting-code-review` (spec compliance → code quality)
- **리뷰 피드백**: `receiving-code-review` (Critical/Important/Minor 분류 처리)
- **완료 처리**: `finishing-a-development-branch` (머지/PR/유지/폐기 선택)

---

## devflow 규칙

### A/B 게이팅 (최우선)

스테이지 완료 시 항상 A(변경 요청) / B(다음 진행) 선택지 제시.
**사용자가 B를 선택하기 전까지 절대 다음 스테이지로 진행 금지.**

### 세션 재개

`devflow-docs/devflow-state.md` 존재 시 → 재개 여부를 먼저 질문. 상태 확인 없이 새 작업 시작 금지.

### 산출물 경로

| 종류 | 경로 |
|------|------|
| Inception 산출물 | `devflow-docs/inception/` |
| Construction 산출물 | `devflow-docs/construction/<unit-name>/` |
| 상태 파일 | `devflow-docs/devflow-state.md` |

---

## 기본 원칙

- **계획 먼저**: 승인 없이 코드 작성 금지
- **TDD Iron Law**: 실패 테스트 없이 프로덕션 코드 작성 금지
- **증거 우선**: 완료 주장 전 반드시 검증. "될 것 같다" 불허
- **보안**: OWASP Top 10 기준 자동 검토
- 승인 없이 `git push` 금지 / 테스트 없이 머지 금지 / A/B 게이팅 스킵 금지

---

## 워크스페이스 구조

> 본인 환경에 맞게 수정하세요.

```
~/projects/
├── frontend/     # 프론트엔드
├── backend/      # 백엔드/API
├── infra/        # 인프라/DevOps
└── sandbox/      # 실험/프로토타입
```

---

## 언어별 컨벤션

> 사용하는 언어만 남기세요. 기본 도구(gofmt, cargo fmt 등)는 Claude가 이미 알고 있으므로 프로젝트 표준과 다른 선택만 명시.

- **Python**: `uv`, `ruff`, 타입 힌트 필수, `pytest`
- **TypeScript**: Node.js, ESLint + Prettier, Vitest 또는 Jest
- **Go**: 에러 무시 금지
- **Rust**: `cargo clippy` 필수
- **Swift**: SwiftUI 우선 (UIKit 지양)
- **Java**: Spring Boot, Gradle, google-java-format, JUnit 5

### Git 보안 (필수)

- **절대 git add 금지**: `.env*`, `*secret*`, `*credential*`, `*token*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `session_*`, `client_secret_*.json`, `credentials.json`, `token.json`
- 신규 프로젝트: `.gitignore`에 위 패턴 추가 후 첫 커밋
- 이미 tracked: `git rm --cached` + `git filter-repo` + 시크릿 재발급

### Docker

- 멀티스테이지 빌드 필수 (builder → runner)
- 비루트 사용자 실행, `COPY --chown`

---

## 프로젝트 프로파일 (선택)

프로젝트 루트 `CLAUDE.md`에 기술 스택을 명시하면 질문 없이 자동 적용:

```markdown
## 기술 스택
- 언어: Python 3.12
- 프레임워크: FastAPI
- DB: PostgreSQL
- 테스트: pytest
- 패키지: uv
```

미명시 항목만 질문합니다. 프로파일 없어도 워크플로우는 정상 동작합니다.
