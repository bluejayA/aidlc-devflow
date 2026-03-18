# Tech Stack Defaults

<!-- 기술 스택 질문의 선택지 생성 데이터. question-format-guide.md와 함께 사용한다. -->

## 사용법

1. 사용자의 프로젝트 유형(아키텍처 패턴) 확인
2. 해당 패턴에 맞는 카탈로그 계층만 필터링
3. question-format-guide.md의 선택지 설계 원칙에 따라 선택지 구성
4. 카탈로그에 없는 기술도 "직접 입력"으로 수용

---

## 아키텍처 패턴 → 카탈로그 매핑

사용자의 프로젝트 유형이 결정되면, 아래 매핑을 참고하여 필요한 계층의 기술을 카탈로그에서 조합한다.

| 아키텍처 패턴 | 필요 계층 | 비고 |
|--------------|----------|------|
| 웹 애플리케이션 (API + DB + UI) | Frontend + Backend + DB + API Style + Testing + Infra | SaaS, 대시보드, 쇼핑몰 등 |
| API 서비스 (API + DB) | Backend + DB + API Style + Testing + Infra | REST/gRPC 백엔드, 마이크로서비스 |
| CLI / TUI | CLI + Testing | 명령줄 도구, 터미널 UI |
| 모바일 앱 | Mobile + Backend(선택) + DB(선택) + Testing | iOS/Android 네이티브 또는 크로스플랫폼 |
| 라이브러리 / SDK | 언어별 빌드 + 배포 + Testing | PyPI, Go Modules, crates.io 등 |
| 데이터 파이프라인 | Backend + DB + Infra + Testing | ETL, 스트리밍, 배치 처리 |

> 이 매핑을 참고하여 카탈로그에서 각 계층의 기술을 선택지로 구성한다. 프로젝트 규모(경량/엔터프라이즈/고성능)에 따라 적합한 옵션을 선택한다.

---

## 기술 카탈로그

계층별 기술 비교표. 각 항목은 **기술명 + 한 줄 설명 + 적합한 상황**을 포함한다.

### Frontend

#### SPA / 메타프레임워크

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| React + Vite | 컴포넌트 기반 SPA 프레임워크. 가장 넓은 생태계 | CSR 단독 앱, SSR 불필요할 때 |
| Next.js | React 기반 메타프레임워크. SSR/SSG/ISR 지원 | SEO 중요, 서버 사이드 렌더링 필요할 때 |
| Vue 3 + Vite | 점진적 프레임워크. 학습 곡선 낮음 | 빠른 프로토타이핑, 가벼운 SPA |
| SvelteKit | 컴파일 타임 최적화 메타프레임워크 | 번들 크기 최소화, 고성능 필요할 때 |

#### 디자인 시스템

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| shadcn/ui + Tailwind | 복사-붙여넣기 방식 컴포넌트. 커스텀 자유도 높음 | 고객향 서비스, 브랜딩 중요할 때 |
| Mantine | 올인원 React 컴포넌트 라이브러리. 풍부한 내장 컴포넌트 | 내부 시스템, 어드민 대시보드 |
| MUI | Material Design 기반. 넓은 컴포넌트 세트 | 엔터프라이즈 앱, 빠른 UI 구성 |

### Backend

| 용도 | 기술 | 설명 | 적합한 상황 |
|------|------|------|------------|
| 경량 / 프로토타입 | FastAPI (Python) | 자동 API 문서, 타입 힌트, async 지원 | 빠른 개발, AI/ML 연동, 프로토타입 |
| 경량 / 프로토타입 | Hono (TypeScript) | 경량 웹 프레임워크. Edge 런타임 호환 | Cloudflare Workers, 엣지 배포 |
| 엔터프라이즈 | Spring Boot (Java) | 엔터프라이즈 표준. Gradle + google-java-format | 대규모 팀, 엔터프라이즈 요구사항 |
| 고성능 | Go (Gin / Fiber) | 단일 바이너리, 뛰어난 동시성. gofmt 표준 | 고처리량 서비스, 마이크로서비스 |
| 고성능 | Rust (Axum) | 메모리 안전, 최고 수준 성능. cargo fmt + clippy | 시스템 수준 성능, 안전성 필수 |

### API 스타일

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| REST (OpenAPI) | 자원 기반 API 설계. 표준 HTTP 메서드 | 모든 프로젝트의 기본 API 스타일 |
| tRPC | 엔드투엔드 타입 안전 RPC | TypeScript 풀스택, 내부 서비스 |
| gRPC | 고처리량 스키마 기반 RPC. Protocol Buffers | 서비스 간 통신, 고성능 요구 |
| GraphQL | 클라이언트 주도 쿼리. 유연한 데이터 요청 | 다양한 클라이언트, 복잡한 데이터 그래프 |

### Database

| 용도 | 기술 | 설명 | 적합한 상황 |
|------|------|------|------------|
| RDBMS | PostgreSQL | 확장성 뛰어남. pgvector, PostGIS 등 | 범용 관계형 DB, AI 벡터 검색 통합 |
| RDBMS | MySQL | 가장 넓은 호스팅 지원 | 웹 애플리케이션, 레거시 연동 |
| NoSQL / 문서 | MongoDB | 유연한 스키마, 빠른 프로토타이핑 | 스키마 변경 잦은 서비스, 문서 저장 |
| 캐시 | Redis (Valkey) | 인메모리 데이터 저장소 | 세션, 레이트리밋, 실시간 메시징 |
| 검색 | Elasticsearch | 전문 검색 엔진. 분석 기능 내장 | 대규모 텍스트 검색, 로그 분석 |
| 검색 | Meilisearch | 경량 검색 엔진. 설정 간편 | 소규모 앱 검색, 빠른 도입 |
| 벡터 (AI/ML) | pgvector (PostgreSQL) | PostgreSQL 확장. 기존 DB에 통합 | AI 임베딩 검색, RAG 파이프라인 |
| 벡터 (AI/ML) | Qdrant | 전용 벡터 DB. 고성능 유사도 검색 | 대규모 벡터 데이터, 전용 인프라 |
| 경량 | SQLite | 파일 기반, 별도 서버 불필요 | CLI 도구, 임베디드, 프로토타입 |

### CLI / TUI

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| Go + Cobra + Bubble Tea | 단일 바이너리. Cobra(인자 파싱) + Bubble Tea(TUI) | 배포 편의성 중요, kubectl/gh 스타일 |
| Rust + clap + Ratatui | 최고 성능 CLI. clap(인자 파싱) + Ratatui(TUI) | 성능 극대화, 크로스 컴파일 |
| Python + Click + Textual | 빠른 개발. Click(인자 파싱) + Textual(TUI) | 스크립팅, 빠른 프로토타입, AI/ML 연동 |
| Swift + ArgumentParser | Apple 공식 CLI 라이브러리 | macOS 전용 도구, Apple 생태계 |

### Mobile

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| SwiftUI (iOS) | Apple 선언형 UI 프레임워크. 최신 iOS 표준 | iOS 네이티브 앱, Apple 생태계 |
| Kotlin Multiplatform | 비즈니스 로직 공유, 네이티브 UI | iOS + Android 동시 개발, 네이티브 성능 |
| Flutter | Dart 기반 크로스플랫폼. 단일 코드베이스 | 빠른 크로스플랫폼 출시, 커스텀 UI |
| React Native | React 기반 크로스플랫폼 | 웹 개발자의 모바일 진입, 기존 React 자산 활용 |

### Testing & Deployment

#### 린트 / 포맷 체크

| 언어 | 포맷터 | 린터 | 비고 |
|------|--------|------|------|
| Python | `ruff format` | `ruff check` | black+isort+flake8 통합. uv로 설치 |
| Go | `gofmt` (내장) | `golangci-lint` | 설정 불필요, 표준 |
| Rust | `rustfmt` (내장) | `clippy` (내장) | cargo fmt + cargo clippy |
| Swift | `swift-format` | `SwiftLint` | Apple 공식 포맷터 |
| Java | `google-java-format` | `spotless` | Gradle 플러그인으로 통합 |
| TypeScript | `prettier` | `eslint` | biome이 올인원 대안 |

#### 단위 테스트

| 언어 | 기술 | 설명 | 적합한 상황 |
|------|------|------|------------|
| Python | pytest + pytest-cov | 간결한 문법, 풍부한 플러그인 | 모든 Python 프로젝트 |
| Go | 표준 testing + testify | 내장 테스트 프레임워크 + 어서션 라이브러리 | 모든 Go 프로젝트 |
| Rust | 내장 #[test] + cargo-tarpaulin | 언어 레벨 테스트 지원 | 모든 Rust 프로젝트 |
| Swift | XCTest / Swift Testing | Apple 공식 테스트 프레임워크 | iOS/macOS 앱, Swift 패키지 |
| Java | JUnit 5 + Mockito + JaCoCo | 엔터프라이즈 표준 테스트 스택 | Spring Boot 프로젝트 |
| TypeScript | Vitest | Vite 네이티브 테스트 러너 | 모든 TS/JS 프로젝트 |

#### API / E2E 테스트

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| pytest + httpx | Python HTTP 클라이언트 기반 API 테스트 | FastAPI 프로젝트 |
| REST Assured | Java DSL 기반 REST API 테스트 | Spring Boot 프로젝트 |
| Playwright | 브라우저 자동화 E2E 테스트 | 웹 앱 전체 흐름 검증 |
| supertest | Node.js HTTP 어서션 라이브러리 | Express/NestJS 프로젝트 |

### Infrastructure

#### CI/CD

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| GitHub Actions | GitHub 네이티브 CI/CD. 넓은 액션 마켓플레이스 | GitHub 기반 프로젝트 (기본) |
| GitLab CI | GitLab 네이티브. 자체 러너 지원 | GitLab 기반, 셀프호스트 필요 |

#### IaC (Infrastructure as Code)

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| Terraform | 선언형 IaC. 가장 넓은 프로바이더 지원 | 멀티클라우드, 범용 인프라 관리 |
| Pulumi | 프로그래밍 언어로 인프라 정의 | 기존 언어(Python, Go, TS)로 IaC |

#### 컨테이너 / 오케스트레이션

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| Docker (멀티스테이지) | 멀티스테이지 빌드 필수. 빌드/런타임 분리 | 모든 컨테이너 프로젝트 |
| Docker Compose | 로컬 멀티 컨테이너 오케스트레이션 | 로컬 개발 환경, 소규모 배포 |
| Kubernetes | 컨테이너 오케스트레이션 표준 | 프로덕션 배포, 스케일링 필요 |

#### 옵저버빌리티

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| LGTM Stack (Loki + Grafana + Tempo + Mimir) | 오픈소스 풀 옵저버빌리티 스택 | 셀프호스트, 비용 효율 |
| Datadog | SaaS 올인원 모니터링 | 빠른 도입, 매니지드 선호 |

#### 인증

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| Keycloak | 오픈소스 IAM. OIDC/SAML/LDAP 지원 | 셀프호스트, 풀 커스텀 |
| Okta | 매니지드 SSO/MFA/OIDC | SaaS, 빠른 도입 |
| NextAuth.js / Auth.js | Next.js 네이티브 인증 라이브러리 | Next.js 프로젝트, OAuth 소셜 로그인 |

---

## 정책 모드

<!-- 운영자 설정. 기본값: open -->
**현재 모드: open**

기술 스택 선택의 자유도를 조직 정책에 따라 3단계로 제어한다.

| 모드 | 카탈로그 외 기술 | "직접 입력" 옵션 | 용도 |
|------|----------------|-----------------|------|
| **open** (기본) | 자유 허용 | ✅ 표시 | 제한 없는 기술 선택 |
| **guided** | 사유 기록 후 허용 | ⚠️ 사유 필수 | 추적 가능한 유연성 — 표준 이탈 시 근거 남김 |
| **strict** | 차단 | ❌ 미표시 | 카탈로그 내 기술만 허용 |

### 모드별 동작

#### open (기본)
- question-format-guide.md의 "직접 입력" 원칙을 그대로 따른다
- 카탈로그는 추천 역할만 수행

#### guided
- 선택지 마지막에 `X) 직접 입력 (사유 필수)`로 표시
- 사용자가 직접 입력을 선택하면 **사유를 질문**한다:
  ```
  카탈로그 외 기술을 선택하셨습니다.
  표준 기술 대신 [입력한 기술]을 사용하는 이유를 간단히 알려주세요:
  ```
- 사유는 `requirements.md`의 `## 기술 스택 결정` 섹션에 기록:
  ```markdown
  | 계층 | 선택 | 카탈로그 여부 | 사유 |
  |------|------|-------------|------|
  | Backend | Ktor | 카탈로그 외 | Kotlin 모노레포 통일 필요 |
  ```

#### strict
- "직접 입력" 옵션을 선택지에 포함하지 않는다
- 사용자가 카탈로그 외 기술을 자유 입력하면 안내:
  ```
  현재 조직 정책(strict)에 따라 카탈로그 내 기술만 선택 가능합니다.
  아래 선택지에서 골라주세요. 카탈로그 변경이 필요하면 운영자에게 요청해주세요.
  ```

### 모드 변경 방법

이 파일 상단의 `현재 모드: open`을 원하는 모드로 변경한다.

---

## 적용 규칙

1. **Greenfield (신규 프로젝트)**: 아키텍처 패턴 질문 → 카탈로그에서 선택지 생성. question-format-guide.md 원칙에 따라 `A) (권장)`, `B/C) 대안`으로 구성. "직접 입력" 포함 여부는 정책 모드에 따름
2. **Brownfield (기존 프로젝트)**: workspace-detection 결과와 카탈로그를 교차 확인. 기존 스택을 존중하되, 개선 가능한 영역을 제안
3. **사용자 명시 지정**: 사용자가 특정 기술을 지정하면 무조건 그것을 따른다 (단, strict 모드에서는 카탈로그 내 기술인지 확인)
4. **카탈로그 외 기술**: 정책 모드에 따라 처리가 다르다:
   - **open**: 카탈로그에 없는 기술도 "직접 입력"으로 수용
   - **guided**: "직접 입력"으로 수용하되 사유를 기록
   - **strict**: 카탈로그 내 기술만 허용. 카탈로그 변경은 운영자에게 요청
5. **선택지 레이블링**: 첫 번째 옵션(권장안)에는 항상 `(권장)`을 붙인다
