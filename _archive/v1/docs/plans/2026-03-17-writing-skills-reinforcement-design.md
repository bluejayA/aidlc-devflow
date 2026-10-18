# writing-skills 보조 자료 내재화 + 패턴 카탈로그 + 검증 자동화

**이슈**: #16 ([8/14] writing-skills 보조 자료 내재화)
**날짜**: 2026-03-17
**상태**: 설계 승인됨

## 배경

superpowers의 writing-skills는 SKILL.md 외에 6개 보조 자료를 보유.
aidlc-like의 writing-skills는 SKILL.md 단독 (277줄).

**핵심 전제:**
1. superpowers 없이 완전 독립 동작 — 외부 링크/참조 불가
2. 스킬 작성이 사용자의 핵심 업무 — 도구로 강화 필요

## 접근법

**접근법 B: 기반 문서 우선 → 점진 통합** 선택.

- 1차: 기반 3개 (best-practices, persuasion-principles, skill-testing-guide)
- 2차: 패턴 카탈로그 (1차 문서를 실제 활용하면서 작성)
- 3차: skill-reviewer + writing-skills SKILL.md 강화 + conventions 수정

이유: best-practices/persuasion-principles가 다른 문서의 용어와 원칙을 정의하므로 먼저 확립 필요.

## 파일 구조

```
skills/_shared/
├── patterns/
│   ├── skill-best-practices.md      ← Task 1 (신규)
│   ├── persuasion-principles.md     ← Task 2 (신규)
│   ├── skill-testing-guide.md       ← Task 3 (신규)
│   ├── skill-pattern-catalog.md     ← Task 4 (신규)
│   ├── three-mode-selection.md      (기존)
│   ├── hold-mechanism.md            (기존)
│   ├── brownfield-exploration.md    (기존)
│   └── session-continuity.md        (기존)
├── reviewers/
│   ├── skill-reviewer-prompt.md     ← Task 5 (신규)
│   └── ... (기존 7개)
├── devflow-conventions.md           ← Task 7 (수정)
└── ...

skills/aidlc-writing-skills/
└── SKILL.md                         ← Task 6 (수정)
```

설계 원칙:
- 신규 패턴 문서는 기존 `_shared/patterns/`에 배치 — 다른 스킬에서도 참조 가능
- skill-reviewer는 기존 reviewer 패턴을 따라 `_shared/reviewers/`에 배치
- 각 문서는 독립적으로 읽을 수 있어야 함

## Task 상세

### Task 1: `skill-best-practices.md` [Medium]

스킬 SKILL.md 작성 시 따라야 할 실전 원칙.

**핵심 내용:**
- **자유도(Degrees of Freedom) 설계**: 스킬 유형별 에이전트 재량 범위 결정법
  - 고자유도 (가이드형): code-review, brainstorming — 원칙만 제시, 판단은 에이전트
  - 중자유도 (템플릿형): requirements-analysis — 구조 고정, 내용 유동
  - 저자유도 (규율형): TDD, debugging — 단계 순서 강제, 예외 불허
- **점진적 공개(Progressive Disclosure)**: SKILL.md는 목차/라우터 역할, 상세는 `_shared/` 문서로 위임
- **500줄 가이드라인**: SKILL.md가 500줄 넘으면 분리 신호
- **CSO 원칙 심화**: description 작성 안티패턴 추가
- **평가 시나리오 필수**: 스킬 작성 전 실패 시나리오 3개 이상 작성

### Task 2: `persuasion-principles.md` [Small]

규율 강제 스킬에서 에이전트가 규칙을 건너뛰지 못하게 하는 언어 설계 원칙.

**핵심 내용:**
- **설득 원칙 3가지** (aidlc에 효과적인 것만 선별):
  - Authority — "MUST", "NO EXCEPTIONS", Iron Law 패턴
  - Commitment — 공개 선언 강제 (Task 체크리스트, 스킬 사용 선언)
  - Social Proof — 보편적 실패 패턴 문서화
- **합리화 방지 테이블 작성법**: 흔한 합리화 문구 수집법 + 반박 작성 원칙
- **스킬 유형별 적용 가이드**: 규율 강제 / 가이드·기법 / 참고 자료
- **HARD-GATE / Iron Law 패턴의 효과 원리**

### Task 3: `skill-testing-guide.md` [Medium]

스킬 자체를 RED-GREEN-REFACTOR로 테스트하는 방법론.

**핵심 내용:**
- **RED**: 압박 시나리오 설계법 (다중 압력 조합), 서브에이전트 디스패치로 실패 문서화
- **GREEN**: 스킬 적용 후 동일 시나리오 재실행 → 준수 확인
- **REFACTOR**: 실패 패턴에서 합리화 테이블 생성 → 스킬에 반영
- **서브에이전트 디스패치 템플릿**: 테스트 시 사용할 프롬프트 구조
- **검증 완료 형식**: 테스트 결과 기록 템플릿
- **#15 (테스트 인프라)와의 관계**: 이 가이드는 방법론, #15는 자동화 인프라

### Task 4: `skill-pattern-catalog.md` [Medium]

aidlc 스킬들을 패턴별로 분류한 레퍼런스. 새 스킬 작성 시 패턴 선택의 출발점.

**패턴 분류:**

| 패턴 | 핵심 특성 | 대표 스킬 |
|------|----------|----------|
| Iron Law | "NO X WITHOUT Y" 강제 | `aidlc-test-driven-development`, `aidlc-systematic-debugging` |
| Gate | N지선다 분기, 사용자 선택 필수 | `aidlc-finishing-a-development-branch` |
| Review Loop | 산출물 생성 → 리뷰어 dispatch → 수정 반복 | `aidlc-code-generation` |
| Three-Mode | Minimal/Standard/Comprehensive 분기 | `aidlc-requirements-analysis` |
| Hold/Skip | Import/Generate + 보류/건너뛰기 | `aidlc-nfr-requirements` |
| Orchestrator-Only | 순수 실행자, 게이트 없음 | `aidlc-workspace-detection` |
| User-Invocable | standalone + orchestrator 양용 | `aidlc-brainstorming` |

**각 패턴 섹션 구조:**
- 특성 한 줄 요약
- 대표 스킬 + 이유
- 구조 템플릿 (뼈대)
- 적용 판단 기준
- 현재 적용 스킬 목록 + 확장 포인트 주석

**확장 전략**: 현재 ~20개 스킬 중심, 각 패턴 끝에 `<!-- 새 스킬 추가 시 여기에 등록 -->` 주석

**구현 시 선행 단계**: 카탈로그 작성 전 `skills/` 디렉토리의 전체 스킬 목록을 열거하고, 각 스킬을 패턴에 매핑하는 작업을 먼저 수행. 누락 스킬이 없도록 보장.

### Task 5: `skill-reviewer-prompt.md` [Small]

writing-skills 3단계(REFACTOR)에서 자동 dispatch되는 스킬 검증 리뷰어.

**검증 영역:**

| 영역 | 검증 항목 | 근거 문서 |
|------|----------|----------|
| 구조 검증 | frontmatter 필수 필드, 섹션 존재, 500줄 | `skill-best-practices.md` |
| 내용 검증 | 압박 시나리오 커버리지, 단계 구체성, standalone 동작 | `skill-testing-guide.md` |
| CSO 검증 | "Use when..." 시작, 키워드 풍부성, 1024자 이하 | writing-skills SKILL.md |

**형식**: 기존 리뷰어 패턴 준수 (Agent tool dispatch, Status + Issues + Recommendations 반환). conventions 리뷰 루프 규약 적용 (최대 5회, 초과 시 사용자 escalate).

**Depth 정책**: conventions의 리뷰 규약을 따른다. Minimal depth에서는 리뷰 스킵, Standard/Comprehensive에서만 skill-reviewer dispatch. writing-skills 3단계(REFACTOR)의 자동 dispatch는 Standard 이상일 때만 실행.

### Task 6: `aidlc-writing-skills/SKILL.md` 강화 [Medium]

**수정 범위:**
1. 3단계 각 단계에서 `_shared/patterns/` 문서 참조 추가
   - 1단계(RED): `skill-testing-guide.md` 참조
   - 2단계(GREEN): `skill-best-practices.md` + `persuasion-principles.md` 참조
   - 3단계(REFACTOR): `skill-reviewer-prompt.md` 자동 dispatch 추가
2. Examples 섹션에 패턴 카탈로그 활용 예시 추가
3. superpowers 참조 문구 제거 (있다면)

**수정하지 않는 것**: 기존 TDD 매핑, CSO 원칙, 배포 전 체크리스트 유지

**줄 수 관리**: 현재 277줄. 참조 추가 시 500줄 가이드라인(Task 1에서 정의)을 초과하지 않도록 확인. 초과 시 상세 내용을 `_shared/patterns/`로 위임하여 SKILL.md는 참조 링크만 유지.

### Task 7: `devflow-conventions.md` 수정 [Small]

**수정 범위 (최소 2곳):**
1. 합리화 방지 관련 → `persuasion-principles.md` 참조 추가
2. 새 스킬 추가 가이드 → `skill-best-practices.md` 참조 추가

기존 구조/내용 변경 없음.

## 실행 순서

```
1차 (기반): Task 1 → Task 2 → Task 3
2차 (카탈로그): Task 4
3차 (통합): Task 5 → Task 6 → Task 7
```

각 차수 완료 후 커밋. 이슈 #16에 진행 코멘트.

## 관련 이슈

- #15 (BL-016): 테스트 인프라 — Task 3이 선행 가이드 역할
- #14 (BL-015): Instruction Priority — conventions 동시 수정 가능
- #9 (BL-010): 컨텍스트 격리 — conventions 동시 수정 가능
