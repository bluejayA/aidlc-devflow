# Tech Stack Catalog

<!-- tech-stack-defaults.md에서 참조하는 기술 카탈로그. 필요할 때만 Read. -->

계층별 기술 비교표. 각 항목은 **기술명 + 한 줄 설명 + 적합한 상황**을 포함한다.

### Frontend

#### SPA / 메타프레임워크

| 기술 | 설명 | 적합한 상황 |
|------|------|------------|
| React + Vite | 컴포넌트 기반 SPA 프레임워크. 가장 넓은 생태계 | CSR 단독 앱, SSR 불필요할 때 |
| Next.js | React 기반 메타프레임워크. SSR/SSG/ISR 지원 | SEO 중요, 서버 사이드 렌더링 필요할 때 |
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
