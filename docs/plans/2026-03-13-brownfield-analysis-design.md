# Brownfield 코드베이스 분석 — workspace-detection 확장

**Complexity:** Minimal

## 요약

`aidlc-workspace-detection`의 Brownfield 경로를 확장하여 technology-stack과 code-structure를 수집한다. 별도 스킬(reverse-engineering)을 만들지 않고 기존 스킬 내에서 해결한다.

## 배경

- 현재 workspace-detection은 Brownfield 판정만 하고 끝남
- 이후 requirements-analysis가 코드베이스 정보 없이 시작
- dev-playbook에는 8개 아티팩트 생성하는 reverse-engineering 단계가 있으나, 현실적으로 Claude가 신뢰성 있게 생성할 수 있는 것은 제한적

## 설계 결정

### 왜 별도 스킬이 아닌가

1. 스킬 추가 = 오케스트레이터 라우팅 복잡도 증가 (새 게이트, 새 조건부 분기)
2. 실제 하는 일은 매니페스트 파싱 + 디렉토리 트리 읽기 수준
3. workspace-detection이 이미 Brownfield 판정 후 멈추는 게 아쉬운 지점
4. 산출물도 기존 `workspace.md`에 섹션 추가로 충분
5. 오케스트레이터 수정 불필요

### 왜 8개가 아닌 2개인가

| 아티팩트 | 현실적 신뢰도 | 판단 |
|----------|-------------|------|
| technology-stack | 높음 (매니페스트 파싱) | **포함** |
| code-structure | 중상 (디렉토리 + 진입점) | **포함** |
| architecture | 낮음 (추측 위험, 과신하면 역효과) | 제외 — 패턴 메모로 대체 |
| api-documentation | 중간 (프레임워크 의존) | 제외 |
| component-inventory | 중간 (code-structure와 중복) | 제외 |
| business-overview | 낮음 (requirements-analysis와 중복) | 제외 |
| dependencies | 낮음 (설계 단계 참조 없음) | 제외 |
| code-quality-assessment | 낮음 (새 기능 설계와 무관) | 제외 |

## 변경 사항

### 파일: `skills/aidlc-workspace-detection/SKILL.md`

**Step 2a 추가** (Step 2 "Determine project type"과 Step 3 "Save artifact" 사이):

Brownfield일 때만 실행. 두 가지 수집:

**1) Technology Stack** — 매니페스트 파일 파싱:
- `package.json` → Node.js + 주요 의존성
- `go.mod` → Go + 모듈 경로
- `Cargo.toml` → Rust + dependencies
- `pyproject.toml` / `requirements.txt` → Python + 패키지
- `pom.xml` / `build.gradle` → Java + 프레임워크
- 빌드 도구, 테스트 프레임워크, 린터도 기록

**2) Code Structure** — 디렉토리 트리 + 진입점:
- 1단계 깊이 디렉토리 트리 (대규모 프로젝트 토큰 방지)
- 진입점 파일 식별 (`main.py`, `index.ts`, `cmd/` 등)
- 관찰된 아키텍처 패턴 메모 (MVC, 모놀리스, 레이어 구조 등 — 보이는 것만, 추측 금지)

### 산출물 변경

기존 `workspace.md` 템플릿에 Brownfield일 때 섹션 2개 추가.
기존 `## Project Structure`는 `## Key Files Found`와 함께 유지 (발견된 파일 목록). `## Code Structure`는 구조적 분석 (디렉토리 레이아웃 + 진입점 + 패턴)으로 역할 구분:

```markdown
## Technology Stack
- **Language**: [언어 + 버전]
- **Framework**: [프레임워크]
- **Package Manager**: [패키지 매니저]
- **Test Framework**: [테스트 프레임워크]
- **Key Dependencies**: [주요 의존성 목록]

## Code Structure
- **Directory Layout**: [1단계 트리]
- **Entry Points**: [진입점 파일]
- **Observed Patterns**: [관찰된 패턴 — 보이는 것만]
```

### Return 필드 변경

기존 필드 유지 + 1개 추가:

```
- 프로젝트 유형: [Greenfield | Brownfield]
- 감지된 경로: [절대 경로]
- 경로 확인 필요: [yes | no]
- 발견된 주요 파일: [count]개
- 코드베이스 분석: [포함 | 해당 없음]  ← 추가
- 산출물: devflow-docs/inception/workspace.md
- 리뷰: 해당 없음 (detection 스테이지 — 사실 수집만 수행)
```

### 엣지 케이스: 복수 매니페스트 / 모노레포

- 루트에 `package.json` + `pyproject.toml` 등 복수 매니페스트 존재 시: 모두 나열, 주 언어 판단하지 않음
- 모노레포 구조 (`packages/`, `services/` 하위): 1단계 깊이 제약으로 하위 매니페스트는 탐색하지 않음. Code Structure의 Directory Layout에 모노레포 구조임을 기록

### Observed Patterns 판단 기준

LLM의 추측을 방지하기 위해 디렉토리 이름 기반의 명시적 규칙만 적용:

| 디렉토리 패턴 | 기록할 패턴 |
|--------------|-----------|
| `controllers/` + `models/` + `views/` | MVC |
| `routes/` + `services/` + `repositories/` | 레이어 구조 |
| `cmd/` + `internal/` + `pkg/` | Go 표준 레이아웃 |
| `src/` + `tests/` | src 레이아웃 |
| 위에 해당 없음 | "특정 패턴 미감지" |

### 변경 사항 (스킬 내부)

- 스킬 버전: 0.3.0 → 0.4.0

### 변경하지 않는 것 (스킬 외부)

- 오케스트레이터 라우팅: 변경 없음
- Greenfield 경로: 영향 없음
- 게이트 구조: 변경 없음

## 성공 기준

1. Brownfield 프로젝트에서 workspace.md에 Technology Stack + Code Structure 섹션이 포함됨
2. Greenfield 프로젝트는 기존과 동일하게 동작
3. 오케스트레이터 수정 없이 기존 라우팅 그대로 작동
