# dev-playbook 공유 패턴 2종 반영 (question-format-guide + tech-stack-defaults)

**이슈**: #12 ([1/13] dev-playbook 공유 패턴)
**날짜**: 2026-03-17
**상태**: 설계 승인됨

## 배경

dev-playbook(`dev-playbook-ai-coding/.claude/shared/`)에서 확인된 갭 파일 중 aidlc에 실제 가치가 있는 2종을 `_shared/patterns/`에 추가.

**원래 이슈**: 3종(tech-stack, terminology, question-format)
**설계 결정**: terminology.md는 스킵 — devflow-conventions.md의 기존 용어 4개가 충분하고, dev-playbook terminology의 대부분이 이미 aidlc에 존재하거나 실제 참조되지 않을 내용.

## 파일 구조

```
skills/_shared/patterns/
├── question-format-guide.md   ← 신규 (질문 설계 원칙)
├── tech-stack-defaults.md     ← 신규 (기술 카탈로그)
└── ... (기존 파일들)

참조 관계:
question-format-guide.md → tech-stack-defaults.md (선택지 생성 데이터)
```

**수정 대상**: `devflow-conventions.md` — "새 스킬 추가 가이드"에 question-format-guide 참조 1줄 추가

## Task 1: `question-format-guide.md` 신규 생성

스킬이 사용자에게 질문할 때 따라야 할 설계 원칙. 비개발자부터 고급 개발자까지 대응.

### 1. 선택지 설계 원칙
- 선택지 개수: 2~5개 + "직접 입력" (Other)
- 의미 있는 옵션만 포함 — 채우기용/형식적 선택지 금지
- 비개발자 친화적 표현: 전문용어 사용 시 한 줄 설명 병기
- 예시: `A) Next.js — React 기반, 풀스택 / B) FastAPI — Python, API 서버 / X) 직접 입력`

### 2. 자유 입력 보장
- 모든 선택지 질문에 "직접 입력" 옵션 필수
- 사용자가 선택지 무시하고 상세 답변을 주면 그대로 반영
- 고급 개발자가 "Rust + Axum + SQLx로 할게"라고 하면 추가 질문 없이 수용

### 3. 모순 감지 + 보충 질문
- 이전 답변과 현재 답변 사이 불일치 발견 시 재확인
- 예: "프로토타입이라고 했는데 엔터프라이즈급 보안을 요구" → 판단하지 않고 질문으로 확인
- 모순이 의도적일 수 있으므로 사용자 결정 존중

### 4. 수준 적응
- 사용자가 짧게 답하면 (A, B 등) → 후속 질문으로 구체화
- 사용자가 상세하게 답하면 → 추가 질문 스킵, 답변을 산출물에 직접 반영
- 첫 1-2개 질문의 답변 스타일로 사용자 수준 감지

**참조 연결**: "기술 스택 관련 선택지 생성 시 `_shared/patterns/tech-stack-defaults.md`의 카탈로그를 활용한다"

## Task 2: `tech-stack-defaults.md` 신규 생성

기술 스택 질문의 선택지 생성 데이터. workspace-detection과 nfr-requirements에서 참조.

### 아키텍처 패턴 → 카탈로그 매핑
사용자가 만들려는 것(웹앱, API, CLI 등)에 따라 관련 기술 카탈로그만 필터링.

### 기술 카탈로그 (계층별)
- Frontend: 디자인 시스템, SPA/메타프레임워크, 폼, 테스트
- Backend: 경량/엔터프라이즈/고성능 분류
- API 스타일: REST, tRPC, gRPC
- Database: RDBMS, NoSQL, 캐시, 검색, 벡터
- CLI/TUI
- Testing & Deployment: 린트 → 단위테스트 → API테스트 → 컨테이너
- Infrastructure: CI/CD, IaC, 옵저버빌리티, 인증

### dev-playbook 원본 적응 포인트
- dev-playbook 237줄을 기본 구조로 하되 복사가 아닌 aidlc 맥락으로 적응
- Jay의 주요 언어(Python, Go, Rust, Swift, Java/Spring)를 반영하여 카탈로그 우선순위 조정
- CLAUDE.md의 언어별 컨벤션과 일관되도록 정렬

### 적용 규칙
- Greenfield: 아키텍처 패턴 질문 → 해당 카탈로그에서 선택지 생성
- Brownfield: workspace-detection 결과와 카탈로그 교차 확인
- 카탈로그에 없는 기술도 사용자가 직접 입력 가능 (question-format-guide의 "자유 입력 보장" 원칙)

## Task 3: `devflow-conventions.md` 수정

"새 스킬 추가 가이드" 섹션에 1줄 추가:
```
7. **사용자 질문 설계**: `_shared/patterns/question-format-guide.md` — 선택지 설계, 수준 적응, 모순 감지
```

기존 구조/내용 변경 없음.

## 실행 순서

```
Task 1 (question-format-guide) → Task 2 (tech-stack-defaults) → Task 3 (conventions 수정)
```

question-format-guide를 먼저 만들어서 원칙을 확립한 뒤, tech-stack-defaults에서 그 원칙에 맞는 카탈로그를 작성.

## 스킬 SKILL.md 수정 — 범위 외

workspace-detection, nfr-requirements 등 개별 스킬에서의 참조 추가는 각 스킬의 개선 이슈(#1 등)에서 처리.

## 관련 이슈

- #13 (BL-014): dev-playbook 보조 패턴 2종 — 이 이슈 이후 구현
- #1 (BL-001): workspace-detection — tech-stack-defaults 활용 시점
