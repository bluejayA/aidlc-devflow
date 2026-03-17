# Claude Code 설정 (devflow 샘플)

> **사용 방법**: 이 파일을 프로젝트 루트 또는 `~/.claude/CLAUDE.md`에 복사한 뒤,
> `## 나에 대해`와 `## 워크스페이스 구조` 섹션을 본인 환경에 맞게 수정하세요.

---

## 나에 대해

- **이름**: (본인 이름 또는 별칭)
- **역할**: (예: 풀스택 개발자, 백엔드 개발자, AI 엔지니어 등)
- **주요 언어**: (예: Python, TypeScript, Go 등)
- **프로젝트 유형**: (예: 웹 서비스/API, AI/LLM 연동 등)
- **대화 언어**: (예: 한국어로 응답, 코드와 변수명은 영어로)

---

## 개발 워크플로우 (devflow)

요청 크기에 따라 세 가지 경로 중 하나를 선택한다.

### 경로 A — 전체 파이프라인 (새 기능 / 컴포넌트 / 서비스)

1. **AI-DLC 파이프라인** (`using-devflow`)
   - 소프트웨어 개발 요청 시 자동 활성화
   - workspace-detection → requirements-analysis → workflow-planning → (using-git-worktrees?) → (application-design?) → (units-generation?) → code-generation (TDD: RED-GREEN-REFACTOR) → build-and-test (빌드+테스트 실행)
   - workflow-planning 완료 후 워크트리 생성 여부를 물음 — **B(워크트리 생성)를 권장: main 브랜치 보호**
   - **각 스테이지 완료 시 반드시 A/B 선택 대기. 응답 없이 다음 단계 진행 금지.**

2. **병렬 구현** (`dispatching-parallel-agents`)
   - 독립적인 태스크가 2개 이상일 때 서브에이전트 병렬 실행
   - 공유 상태가 없는 태스크만 병렬화 가능 — 의존성 있으면 순차 진행

3. **코드 리뷰** (`requesting-code-review`)
   - 2-stage review: spec compliance → code quality (OWASP + 언어별 보안)
   - standalone 호출 또는 subagent-driven-development에서 자동 호출

4. **코드 리뷰 피드백 처리** (`receiving-code-review`)
   - 코드 리뷰 피드백 수신 시 Critical / Important / Minor 분류 후 처리

5. **개발 완료 처리** (`finishing-a-development-branch`)
   - 모든 unit 완료 후 머지 / PR / 유지 / 폐기 4가지 선택지 제시

### 경로 B — 경량 경로 (단일 파일 수정 / 명확한 범위의 버그 픽스)

1. TDD 방식으로 구현 — RED → GREEN → REFACTOR
2. `verification-before-completion` — 완료 주장 전 반드시 검증

### 경로 C — 디버깅 (원인 불명 오류 / 예상 밖 동작)

1. `systematic-debugging` — 4단계 근본 원인 분석
2. 원인 확정 후 경로 A 또는 B로 전환

---

## devflow 규칙

### A/B 게이팅 (최우선 규칙)

devflow 스테이지 완료 메시지에는 항상 A/B 선택이 있다.

```
A) 변경 요청
B) [다음 스테이지]로 진행
```

**사용자가 명시적으로 B를 선택하기 전까지 절대 다음 스테이지로 진행하지 말 것.**

### 세션 재개

세션 시작 시 `devflow-docs/devflow-state.md`가 존재하면:
- 현재 단계, 완료된 스테이지를 확인한 후 재개 여부를 먼저 물을 것
- 상태 확인 없이 새 작업을 시작하지 말 것

### 적응형 깊이

requirements-analysis 깊이는 자동 판단:

| 깊이 | 조건 |
|------|------|
| **Minimal** | 단순하고 명확한 요청, 단일 파일, 저위험 |
| **Standard** | 일반적 복잡도 |
| **Comprehensive** | 멀티 컴포넌트, 고위험, 외부 연동, 요구사항 모호 |

### 산출물 경로

| 종류 | 경로 |
|------|------|
| 설계 문서 | `docs/plans/YYYY-MM-DD-<topic>-design.md` |
| Inception 산출물 | `devflow-docs/inception/` |
| Construction 산출물 | `devflow-docs/construction/<unit-name>/` |
| 상태 파일 | `devflow-docs/devflow-state.md` |
| 감사 로그 | `devflow-docs/audit.md` |

---

## 기본 원칙

- **계획 먼저 승인 후 진행**: 구현 전 접근 방식 공유, 승인 없이 코드 작성 금지
- **TDD Iron Law**: 실패 테스트 없이 프로덕션 코드 작성 금지. 위반 시 코드 삭제 후 RED부터 재시작
- **증거 우선**: 완료 주장 전 반드시 검증. "될 것 같다"는 허용하지 않음
- **보안 자동 검토**: OWASP Top 10 기준 취약점 확인

### 절대 하지 말 것

- 승인 없이 `git push` 금지
- 테스트 없이 코드 머지 금지
- 불필요한 추상화/오버엔지니어링 금지
- devflow A/B 게이팅 스킵 금지

---

## 워크스페이스 구조

> 본인 환경에 맞게 수정하세요.

```
~/projects/
├── frontend/     # 프론트엔드 프로젝트
├── backend/      # 백엔드/API 서비스
├── infra/        # 인프라/DevOps
└── sandbox/      # 실험 및 프로토타입
```

---

## 언어별 컨벤션

> 사용하는 언어만 남기고 나머지는 삭제하세요.

### Python
- 패키지 관리: `uv` (기본) 또는 `poetry`
- 린터/포매터: `ruff`
- 타입 힌트 필수
- 테스트: `pytest`

### TypeScript / JavaScript
- 런타임: Node.js (기본) 또는 Bun
- 린터/포매터: ESLint + Prettier
- 테스트: Vitest 또는 Jest

### Go
- 포매터: `gofmt`
- 에러 핸들링 명시적으로 처리 (에러 무시 금지)
- 테스트: 표준 `testing` 패키지

### Rust
- 포매터/린터: `cargo fmt` + `cargo clippy`
- 테스트: `#[cfg(test)]` 모듈

### Swift
- SwiftUI 우선 (UIKit 지양)
- Swift 표준 naming convention
- 테스트: XCTest / Swift Testing

### Java (Spring)
- 프레임워크: Spring Boot
- 빌드 툴: Gradle (기본) 또는 Maven
- 포매터: google-java-format
- 테스트: JUnit 5 + Mockito

### Git 보안 (필수)

- **커밋 전 항상 확인**: 아래 파일 유형은 절대 git add 금지
  - `.env`, `*.env`, `.env.*` (환경변수)
  - `*secret*`, `*credential*`, `*token*` (인증 정보)
  - `client_secret_*.json`, `credentials.json`, `token.json` (OAuth)
  - `*.pem`, `*.key`, `*.p12`, `*.pfx` (인증서/키)
  - `session_*` (세션 파일)
- **신규 프로젝트 시작 시**: 위 패턴을 `.gitignore`에 먼저 추가 후 첫 커밋
- **이미 tracked된 경우**: `git rm --cached <file>` + `git filter-repo`로 history 제거 후 시크릿 재발급
- **`.env.example`** 파일로 필요한 환경변수 목록만 문서화 (실제 값 없이)

### Docker
- **멀티스테이지 빌드 필수**: 모든 Dockerfile은 멀티스테이지 빌드로 이미지 크기 최적화
  - `builder` 스테이지: 빌드 도구, 의존성 설치
  - `runner` 스테이지: 실행에 필요한 파일만 복사 (빌드 도구 제외)
- 비루트 사용자 실행 (`useradd` + `USER appuser`)
- `COPY --chown` 으로 소유권 설정 (별도 `RUN chown` 레이어 불필요)

---

## 설치된 플러그인

> devflow는 필수이며, 나머지는 선택 사항입니다.

| 플러그인 | 역할 |
|---------|------|
| `devflow-aidlc-like` | AI-DLC 개발 라이프사이클 전체 (Inception → Construction, 27개 스킬) — **필수** |
| `claude-code-setup` | 프로젝트별 자동화 추천 |
| `agent-council` | 다중 AI 에이전트 의견 수집 |
| `github` | GitHub 연동 |

---

## 프로젝트 프로파일 (선택)

프로젝트 루트의 `CLAUDE.md`에 기술 스택과 설계 원칙을 명시하면 질문 없이 자동 적용됩니다:

```markdown
## 기술 스택
- 언어: Python 3.12
- 프레임워크: FastAPI
- DB: PostgreSQL
- 테스트: pytest
- 패키지: uv

## 설계 원칙
- TDD: 필수
- Complexity: Standard
```

미명시 항목만 질문합니다. 프로파일은 선택사항 — 없어도 워크플로우는 정상 동작합니다.

## 프로젝트별 컨텍스트

- devflow 파이프라인 산출물: `devflow-docs/` (자동 생성)
- 설계 문서: `docs/plans/` (brainstorming 완료 시 저장)
