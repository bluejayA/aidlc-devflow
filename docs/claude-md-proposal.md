# Jay의 Claude Code 설정

## 나에 대해

- **이름**: Jay
- **역할**: 풀스택 개발자
- **주요 언어**: Python, Go, Rust, Swift, Java (Spring)
- **프로젝트 유형**: AI/LLM 연동, 웹 서비스/API, 인프라/DevOps, iOS 앱
- **대화 언어**: 한국어 (응답은 항상 한국어로, 코드와 변수명은 영어로)

---

## 개발 워크플로우 (devflow + Superpowers)

요청 크기에 따라 세 가지 경로 중 하나를 선택한다.

### 경로 A — 전체 파이프라인 (새 기능 / 컴포넌트 / 서비스)

1. **Brainstorming** (`devflow:brainstorming`)
   - 새 기능, 컴포넌트, 동작 수정 시 **항상** 먼저 실행
   - 설계 문서 작성 후 승인 받기 → `docs/plans/YYYY-MM-DD-<topic>-design.md`에 저장
   - 코드 한 줄도 작성 전. 예외 없음.

2. **AI-DLC 파이프라인** (`devflow:using-devflow`)
   - Brainstorming 승인 후 devflow 워크플로우 시작
   - workspace-detection → requirements-analysis → workflow-planning → (application-design?) → (units-generation?) → code-generation (TDD: RED-GREEN-REFACTOR) → build-and-test (빌드+테스트 실행)
   - **각 스테이지 완료 시 반드시 A/B 선택 대기. 응답 없이 다음 단계 진행 금지.**

3. **격리 개발** (`devflow:using-git-worktrees`)
   - code-generation 시작 전 새 브랜치 + 워크트리 생성
   - 각 기능은 독립된 워크트리에서 개발

4. **코드 리뷰 → 완료** (`superpowers:requesting-code-review` → `devflow:finishing-a-development-branch`)
   - 모든 unit 완료 후 리뷰 요청
   - Critical 이슈 해결 후 머지/PR/보관 결정

### 경로 B — 경량 경로 (단일 파일 수정 / 명확한 범위의 버그 픽스)

1. `superpowers:test-driven-development` — RED → GREEN → REFACTOR
2. 구현
3. `superpowers:verification-before-completion` — 완료 주장 전 반드시 검증

### 경로 C — 디버깅 (원인 불명 오류 / 예상 밖 동작)

1. `superpowers:systematic-debugging` — 4단계 근본 원인 분석
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
- **코멘트 한국어**: 코드 내 주석은 한국어로
- **보안 자동 검토**: OWASP Top 10 기준 취약점 확인

### 절대 하지 말 것

- 승인 없이 `git push` 금지
- 테스트 없이 코드 머지 금지
- 불필요한 추상화/오버엔지니어링 금지
- devflow A/B 게이팅 스킵 금지

---

## 워크스페이스 구조

```
~/projects/           ← 신규 프로젝트 (메인)
├── ai/               # AI/LLM 관련 (Claude API, RAG, 에이전트)
├── backend/          # 백엔드/API 서비스 (Python, Go, Rust)
├── infra/            # 인프라/DevOps (Docker, K8s, CI/CD)
├── ios/              # iOS/Swift 프로젝트
└── sandbox/          # 실험 및 프로토타입

~/workspaces/         ← 기존 프로젝트 유지 (레거시)
├── agent-peeper/
├── antigravity/
├── claude/
├── llm-d/
└── ...
```

---

## 언어별 컨벤션

### Python
- 패키지 관리: `uv` (기본) 또는 `poetry`
- 린터/포매터: `ruff`
- 타입 힌트 필수
- 테스트: `pytest`

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
  - `instagram-session`, `session_*` (세션 파일)
- **신규 프로젝트 시작 시**: 위 패턴을 `.gitignore`에 먼저 추가 후 첫 커밋
- **이미 tracked된 경우**: `git rm --cached <file>` + `git filter-repo`로 history 제거 후 시크릿 재발급
- **`.env.example`** 파일로 필요한 환경변수 목록만 문서화 (실제 값 없이)

### Docker
- **멀티스테이지 빌드 필수**: 모든 Dockerfile은 멀티스테이지 빌드로 이미지 크기 최적화
  - `builder` 스테이지: 빌드 도구, 의존성 설치
  - `runner` 스테이지: 실행에 필요한 파일만 복사 (빌드 도구 제외)
- `curl` 항상 설치: `RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*`
- `PYTHONUNBUFFERED=1` 설정 (Python 컨테이너): print() 로그 즉시 출력
- 비루트 사용자 실행 (`useradd` + `USER appuser`)
- `COPY --chown` 으로 소유권 설정 (별도 `RUN chown` 레이어 불필요)

---

## 설치된 플러그인

| 플러그인 | 역할 |
|---------|------|
| `devflow` | AI-DLC 개발 라이프사이클 (Inception → Construction 전체 파이프라인) |
| `superpowers` | 일상 개발 도구 (TDD, 디버깅, 코드 리뷰, 서브에이전트) |
| `claude-code-setup` | 프로젝트별 자동화 추천 |
| `agent-council` | 다중 AI 에이전트 의견 수집 |
| `github` | GitHub 연동 |

---

## 프로젝트별 컨텍스트

각 프로젝트 루트의 `CLAUDE.md`에서 프로젝트별 상세 설정 참고.

- devflow 파이프라인 산출물: `devflow-docs/` (자동 생성)
- 설계 문서: `docs/plans/` (brainstorming 완료 시 저장)
