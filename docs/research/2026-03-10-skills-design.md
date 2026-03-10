# AI-DLC Skills 세트 설계 아이디어

- **작성일**: 2026-03-10
- **참조**:
  - https://github.com/awslabs/aidlc-workflows
  - https://github.com/obra/superpowers

---

## Superpowers vs AI-DLC 비교

| | Superpowers | AI-DLC |
|--|-------------|--------|
| **구조** | 독립 Skills 세트 | 단일 core-workflow + rule-details |
| **트리거** | AI가 컨텍스트 보고 자동 | `"Using AI-DLC, ..."` 명시적 |
| **상태** | 무상태 (각 skill 독립) | 상태 기반 (`aidlc-state.md`) |
| **산출물** | 없음 (코드만) | `aidlc-docs/` 풍부한 문서 |
| **감사 로그** | 없음 | `audit.md` 완전 추적 |
| **확장** | 새 skill 추가 | `extensions/` 디렉토리 |
| **인간 게이팅** | 암묵적 | 매 단계 명시적 승인 필수 |
| **적응성** | 각 skill이 독립 결정 | core-workflow가 전체 흐름 제어 |

### Superpowers 현재 Skills 목록

- `using-superpowers` — 진입점, 항상 로드
- `brainstorming` — 설계 전 탐구
- `writing-plans` — 구현 계획 작성
- `executing-plans` — 계획 실행
- `subagent-driven-development` — 서브에이전트 병렬 실행
- `dispatching-parallel-agents` — 병렬 에이전트 디스패치
- `test-driven-development` — RED-GREEN-REFACTOR
- `systematic-debugging` — 4단계 근본 원인 분석
- `verification-before-completion` — 완료 전 검증
- `requesting-code-review` — 코드 리뷰 요청
- `receiving-code-review` — 코드 리뷰 수신
- `using-git-worktrees` — 격리 브랜치 개발
- `finishing-a-development-branch` — 머지/PR 결정
- `writing-skills` — 새 skill 작성 가이드

---

## 설계 접근법 비교

### 접근 A: Fine-grained (각 스테이지 = 1 skill)
- **장점**: 유연, 독립 실행, 재사용 가능
- **단점**: 상태 공유 어렵고 오케스트레이션 복잡

### 접근 B: Phase-level (3단계 = 3 skill)
- `aidlc-inception`, `aidlc-construction`, `aidlc-operations`
- **장점**: 단순, AI-DLC 철학 유지
- **단점**: 각 skill이 여전히 거대함

### 접근 C: Hybrid (권장)
오케스트레이터 + 스테이지별 skill + 공통 유틸

---

## 권장 Skills 구조

```
skills/
├── aidlc/
│   │
│   ├── using-aidlc/                  # 진입점 — 상태 확인, 다음 skill 지시
│   │
│   ├── # INCEPTION 스테이지
│   ├── workspace-detection/          # 그린필드/브라운필드 판단, 세션 재개
│   ├── reverse-engineering/          # 기존 코드 분석 (브라운필드 전용)
│   ├── requirements-analysis/        # 요구사항 (Minimal/Standard/Comprehensive)
│   ├── user-stories/                 # Plan → Generate 2단계
│   ├── workflow-planning/            # 실행 단계 결정
│   ├── application-design/           # 컴포넌트/서비스 설계
│   ├── units-generation/             # 병렬 개발 단위 분해
│   │
│   ├── # CONSTRUCTION 스테이지
│   ├── functional-design/            # 데이터 모델, 비즈니스 로직
│   ├── nfr-requirements/             # 성능/보안/확장성 요건
│   ├── nfr-design/                   # NFR 패턴 적용
│   ├── infrastructure-design/        # 인프라/배포 아키텍처
│   ├── code-generation/              # Plan → Approve → Generate
│   ├── build-and-test/               # 빌드/테스트 지침 생성
│   │
│   ├── # 공통 유틸
│   ├── session-state/                # aidlc-state.md 읽기/쓰기
│   ├── audit-logger/                 # audit.md append-only 기록
│   └── content-validator/            # Mermaid/ASCII 검증
│
└── aidlc-extensions/                 # 별도 플러그인 네임스페이스
    ├── security/
    ├── hipaa/
    └── pci-dss/
```

---

## Superpowers에 없는 AI-DLC 고유 패턴 구현 방법

### 1. 상태 관리

Superpowers skill은 무상태 — AI-DLC는 단계 간 상태 공유 필요.

```markdown
# session-state skill 패턴
모든 aidlc skill은 시작 시:
1. aidlc-docs/aidlc-state.md 읽기
2. 현재 단계 확인 → 재개 or 신규 시작
3. 완료 후 상태 업데이트 기록
```

`aidlc-state.md` 구조:
```markdown
## Current Phase
## Completed Stages
## Skipped Stages
## Extension Configuration
## Unit Progress
```

### 2. 승인 게이팅 패턴

각 스테이지 skill 끝에 표준 2-option 완료 메시지 강제:

```
A) 변경 요청
B) 다음 단계 진행
```

→ Superpowers `checkpoint` 개념과 유사하나 **매 단계 필수**, 건너뛰기 불가

### 3. 적응형 깊이

각 skill 내부에서 복잡도 평가 후 실행 depth 결정:

```markdown
요청 복잡도 자가 평가:
- 단순/명확한 요청 → Minimal 실행
- 보통 복잡도 → Standard 실행
- 복잡/고위험/다중 컴포넌트 → Comprehensive 실행
```

### 4. Extensions → Skill + State 패턴

```markdown
# aidlc-extensions/security skill 동작
1. using-aidlc가 extensions/ 스캔 후 각 extension skill 로드
2. Inception 단계에서 활성화 여부 질문 → 답변을 aidlc-state.md에 기록
3. 이후 Construction skill들이 state 확인 후 해당 extension 검증 실행
4. 미준수 시 blocking finding — 해결 전 다음 단계 진행 불가
```

### 5. audit-logger 유틸 패턴

```markdown
# audit-logger skill 패턴 (모든 skill에서 호출)
- 항상 append 모드로만 기록
- 덮어쓰기 절대 금지 (audit.md 전체 재작성 불가)
- ISO 8601 타임스탬프 필수
- 사용자 입력은 요약 없이 원문 그대로 기록
```

---

## Superpowers에서 가져올 패턴

| Superpowers 패턴 | AI-DLC skill 적용 |
|----------------|-----------------|
| `using-superpowers` 자동 진입 | `using-aidlc`가 상태 확인 후 다음 skill 지시 |
| 2단계 리뷰 (spec → quality) | `code-generation` 내 Plan → Review → Generate |
| subagent 병렬 디스패치 | `units-generation`이 unit별 skill 병렬 실행 |
| `writing-skills` 자기 참조 | `aidlc/writing-aidlc-skill` — extension 작성 가이드 |

---

## 구현 우선순위

### Phase 1: 뼈대 (필수)
- [ ] `using-aidlc` — 진입점, 상태 확인, 다음 skill 지시
- [ ] `session-state` — aidlc-state.md 읽기/쓰기 유틸
- [ ] `audit-logger` — audit.md append 유틸

### Phase 2: Inception 핵심
- [ ] `workspace-detection` — 그린필드/브라운필드, 재개 판단
- [ ] `requirements-analysis` — 적응형 깊이 (Minimal/Standard/Comprehensive)
- [ ] `workflow-planning` — 실행 계획 수립 및 사용자 승인

### Phase 3: Construction 핵심
- [ ] `code-generation` — Plan → Approve → Generate 2단계
- [ ] `build-and-test` — 빌드/테스트 지침

### Phase 4: Inception 나머지
- [ ] `reverse-engineering` (브라운필드)
- [ ] `user-stories`
- [ ] `application-design`
- [ ] `units-generation`

### Phase 5: Construction 나머지
- [ ] `functional-design`
- [ ] `nfr-requirements` + `nfr-design`
- [ ] `infrastructure-design`

### Phase 6: Extensions
- [ ] `aidlc-extensions/security`
- [ ] `content-validator` 유틸

---

## 핵심 차별화 포인트

**Superpowers**: "어떻게 개발할 것인가" (프로세스 중심)

**AI-DLC Skills**: "무엇을 만들 것인가 + 왜 + 어떻게" (산출물 + 프로세스)

Superpowers 대비 AI-DLC만의 강점:
- **`aidlc-docs/` 자동 산출물** — 모든 설계 결정이 추적 가능한 문서로 남음
- **`audit.md` 완전 로그** — 규제/컴플라이언스 환경에서 특히 유용
- **Extensions 시스템** — 조직 정책/컴플라이언스를 blocking constraint로 강제
- **Brownfield 지원** — Reverse Engineering으로 기존 코드베이스 분석 내장
- **NFR 명시화** — 비기능 요구사항을 설계 단계부터 별도 스테이지로 처리
