# skill-creator vs aidlc-writing-skills 비교 분석 및 통합 전략

> **작성일**: 2026-03-20
> **목적**: Anthropic 공식 skill-creator 플러그인과 aidlc-writing-skills의 기능 비교, 상호 보완 전략 수립

---

## 1. 개요

두 시스템 모두 "AI 스킬의 품질을 체계적으로 관리"한다는 목표는 같지만, 접근 철학과 강점 영역이 근본적으로 다르다.

| 차원 | **skill-creator** (Anthropic 공식) | **aidlc-writing-skills** |
|------|------|------|
| **핵심 질문** | "이 스킬이 **성능**이 좋은가?" | "이 스킬이 **압박 하에서도 지켜지는가?**" |
| **비유** | QA 엔지니어 (측정 -> 개선) | 군사 교관 (훈련 -> 규율) |
| **검증 방식** | 정량적 벤치마크 (pass_rate, tokens, time) | 정성적 시나리오 (압박 시나리오 + 합리화 방지) |
| **개선 루프** | 자동화된 반복 (Python 스크립트 + train/test 분할) | 수동 리뷰 루프 (서브에이전트 reviewer, 최대 5회) |
| **Iron Law** | 없음 | `NO SKILL WITHOUT DEFINING TRIGGER CONDITIONS FIRST` |

---

## 2. skill-creator 상세 분석

### 2.1 아키텍처

```
skill-creator/
├── SKILL.md                    # 메인 스킬 문서 (480줄)
├── agents/
│   ├── analyzer.md            # 벤치마크 결과 분석 에이전트
│   ├── comparator.md          # 블라인드 비교 에이전트
│   └── grader.md              # 평가/채점 에이전트
├── references/
│   └── schemas.md             # JSON 스키마 정의
├── scripts/                   # Python 자동화 (총 2373줄)
│   ├── run_eval.py           # 트리거 평가 실행
│   ├── run_loop.py           # description 최적화 루프 (train/test 분할)
│   ├── improve_description.py # Claude extended thinking으로 description 개선
│   ├── aggregate_benchmark.py # 통계 집계
│   ├── package_skill.py      # .skill 파일 생성
│   ├── generate_report.py    # HTML 보고서
│   ├── quick_validate.py     # 스킬 유효성 검사
│   └── utils.py              # SKILL.md 파싱
├── eval-viewer/
│   └── generate_review.py    # 웹 기반 리뷰 인터페이스
└── assets/
    └── eval_review.html      # description 평가 UI 템플릿
```

### 2.2 워크플로우

```
1. Intent Capture → Interview & Research → SKILL.md 작성
2. Test Cases (evals.json) 준비 — 2-3개 현실적 프롬프트
3. Eval 실행
   ├── with-skill + without-skill 병렬 스포닝
   ├── 타이밍 데이터 캡처
   ├── Grader 에이전트로 채점 → grading.json
   ├── aggregate_benchmark.py → benchmark.json (mean, stddev, delta)
   ├── Analyzer 에이전트로 패턴 분석
   └── generate_review.py → 웹 기반 viewer
4. 사용자 피드백 수집 (feedback.json)
5. 개선 → iteration-N+1로 재실행 (만족할 때까지)
6. Description 최적화
   ├── 20개 trigger eval 쿼리 생성 (should/should-not trigger)
   ├── HTML UI로 사용자 검토
   ├── run_loop.py — 60% train / 40% test 분할, 과적합 방지
   ├── 각 쿼리 3회 실행 (신뢰도)
   ├── Claude extended thinking으로 개선 제안
   └── 최대 5회 반복 → best_description 선택
7. 패키징 (package_skill.py → .skill zipfile)
```

### 2.3 에이전트 역할

| 에이전트 | 역할 | 입력 | 출력 |
|---------|------|------|------|
| **Grader** | 어설션 채점 | expectations + transcript + outputs | grading.json (pass_rate, evidence) |
| **Comparator** | 블라인드 비교 (A vs B) | 두 출력 + 프롬프트 | comparison.json (winner, rubric, scores) |
| **Analyzer** | 패턴 분석 + 개선 제안 | benchmark.json / comparison.json | notes[] / analysis.json |

### 2.4 핵심 강점

- **정량적 벤치마크**: pass_rate, tokens, time의 mean/stddev/min/max + delta 비교
- **과적합 방지**: train/test 분할로 description 최적화 시 일반화 보장
- **웹 기반 리뷰 UI**: 실행 결과를 시각적으로 비교, 피드백 auto-save
- **블라인드 비교**: 어느 버전인지 모른 채 품질 평가 (편향 제거)
- **JSON 스키마 표준화**: 모든 중간 산출물이 명확한 스키마를 가짐

### 2.5 약점

- 스킬 "설계" 가이드 부재 — Progressive Disclosure 정도만 언급
- 구조/행동 패턴 개념 없음
- 압박 시나리오 테스트 없음 — 규율 스킬의 실효성 검증 불가
- 설득 원칙 없음
- 기존 스킬 수정 시 영향도 분석 없음

---

## 3. aidlc-writing-skills 상세 분석

### 3.1 핵심 프로세스 (프로세스의 TDD)

| TDD 단계 | 스킬 TDD 대응 |
|---------|-------------|
| **RED** | 압박 시나리오 설계: 스킬 없이 에이전트가 실패하는 상황 문서화 |
| **Verify RED** | 합리화/위반 패턴을 원문 그대로 기록 |
| **GREEN** | 스킬 작성 후, 동일 시나리오에서 스킬 준수 확인 |
| **Verify GREEN** | 압박 하에서도 스킬을 따르는지 검증 |
| **REFACTOR** | 빈틈 메우기 + 합리화 방지 테이블 생성 |
| **Stay GREEN** | 업데이트된 스킬로 재실행 -> 여전히 준수 확인 |

### 3.2 설계 자산

| 자산 | 파일 | 내용 |
|------|------|------|
| **구조 패턴** (5종) | `_shared/patterns/skill-design-patterns.md` | Tool Wrapper, Generator, Reviewer, Inversion, Pipeline + 결정 트리 |
| **행동 패턴** (7종) | `_shared/patterns/skill-pattern-catalog.md` | Iron Law, Gate, Review Loop, Three-Mode, Hold/Skip, User-Invocable, Orchestrator-Only |
| **설득 원칙** | `_shared/patterns/persuasion-principles.md` | Authority, Commitment, Social Proof (Meincke 2025, N=28K) |
| **자유도 설계** | `_shared/patterns/skill-writing-guide.md` | 고/중/저 — 스킬별 최적 엄격도 |
| **CSO 원칙** | writing-skills SKILL.md 내장 | "Use when..." 시작, 키워드 풍부, 1024자 이하 |
| **스킬 리뷰어** | `_shared/reviewers/skill-reviewer-prompt.md` | 5영역 자동 검증 (구조/내용/CSO/패턴/영향도) |

### 3.3 검증 체계

- **Skill Reviewer 서브에이전트**: 구조/내용/CSO/패턴/영향도 5영역 검증
- **리뷰 루프**: 최대 5회 재검토, 초과 시 사용자 escalate
- **Depth 정책**: Minimal (스킵) / Standard (리뷰 포함) / Comprehensive (심화)
- **통합 테스트**: pytest 기반 69개 메타 태그 검증 테스트
- **정합성 체크리스트**: `@gate`, `@step`, `@condition` 메타 태그 동기화

### 3.4 핵심 강점

- 압박 시나리오 기반 검증 (6가지 압력: 시간/매몰비용/피로/자신감/권위/실용주의)
- 합리화 방지 테이블 — 에이전트의 규칙 회피 패턴 차단
- 풍부한 설계 가이드 (구조 패턴 5종 + 행동 패턴 7종)
- 설득 원칙 적용으로 준수율 2배 향상 (연구 기반)
- 오케스트레이터 통합 — devflow 라이프사이클 내 자연스러운 위치

### 3.5 약점

- Description 최적화 자동화 도구 없음 (CSO 원칙은 있으나 수동 체크리스트)
- 트리거 정확도 정량 테스트 없음
- with-skill vs baseline 정량 비교 없음
- 웹 기반 리뷰 UI 없음
- 패키징/배포 도구 없음

---

## 4. 기능 매트릭스

| 기능 | **skill-creator** | **aidlc** | 격차 |
|------|:---:|:---:|:---:|
| SKILL.md 작성 | O | O | 동등 (접근법 다름) |
| Description 최적화 자동화 | **OO** | X | **aidlc에 큰 격차** |
| 트리거 정확도 테스트 | **OO** | X | **aidlc에 큰 격차** |
| 산출물 품질 벤치마크 | **OO** | 부분 | aidlc에 격차 |
| 웹 기반 리뷰 UI | **OO** | X | aidlc에 격차 |
| 블라인드 비교 | O | X | aidlc에 격차 |
| 패키징/배포 | O | X | 낮은 우선순위 |
| 구조 패턴 가이드 | 부분 | **OO** | skill-creator에 격차 |
| 행동 패턴 가이드 | X | **OO** | skill-creator에 격차 |
| 압박 시나리오 테스트 | X | **OO** | skill-creator에 격차 |
| 합리화 방지 | X | **OO** | skill-creator에 격차 |
| 설득 원칙 (연구 기반) | X | **OO** | skill-creator에 격차 |
| 자유도 설계 가이드 | X | O | skill-creator에 격차 |
| 스킬 리뷰어 에이전트 | X | O | skill-creator에 격차 |
| 수정 시 영향도 분석 | X | O | skill-creator에 격차 |
| 통합 테스트 스위트 | X | O | skill-creator에 격차 |
| 오케스트레이터 통합 | X | **OO** | skill-creator에 격차 |

---

## 5. 통합 전략

### 5.1 핵심 판단

두 시스템은 **경쟁이 아니라 스킬 개발 파이프라인의 전반부(aidlc: 설계)와 후반부(skill-creator: 검증/최적화)**로 조합하면 가장 강력하다.

```
aidlc-writing-skills (설계/작성/리뷰)
  RED: 압박 시나리오 설계
  GREEN: 스킬 작성 (구조 패턴 + 행동 패턴 + 설득 원칙)
  REFACTOR: skill-reviewer 검증
  ──────────────────────────────────
  최적화 게이트 (NEW)
  ──────────────────────────────────
  skill-creator (정량적 검증/최적화)    ← 스킬 체이닝으로 호출
    eval 생성 + 벤치마크
    description 최적화 (train/test)
    결과 반환
```

### 5.2 통합 방식: 스킬 체이닝

**기각된 방식**: 서브에이전트 -> Skill tool -> skill-creator

- 3~4단계 중첩 (aidlc -> sub-agent -> skill-creator -> skill-creator의 sub-agents)
- 컨텍스트 전달 희석, 디버깅 어려움

**채택된 방식**: aidlc-writing-skills의 REFACTOR 단계에서 Skill tool로 skill-creator 직접 호출

- 기존 aidlc 패턴 준수 (SDD -> requesting-code-review와 동일 패턴)
- 중첩 2단계 (aidlc -> skill-creator -> skill-creator의 sub-agents)
- skill-creator를 그대로 활용, 풀 컨텍스트 전달

### 5.3 구현 범위

aidlc-writing-skills SKILL.md의 REFACTOR 단계 완료 후, 게이트 하나 추가:

```markdown
### REFACTOR 완료 후 — 최적화 게이트

스킬 리뷰가 Approved되면:

A) **스킬 완성** — description 수동 검증으로 충분
B) **정량적 최적화** — skill-creator로 eval + description 최적화 실행

> 사용자 선택 없이 진행하지 않는다.

B 선택 시: Skill tool로 `skill-creator` 호출
- skill-creator가 eval 생성 -> 벤치마크 -> description 최적화를 자체 워크플로우로 수행
- 완료 후 aidlc-writing-skills로 돌아와 결과 확인
```

### 5.4 변경 영향 범위

| 파일 | 변경 내용 |
|------|----------|
| `skills/aidlc-writing-skills/SKILL.md` | REFACTOR 단계에 최적화 게이트 추가 |
| `skills/_shared/devflow-conventions.md` | 외부 플러그인 스킬 체이닝 규약 추가 (선택) |
| `skills/_shared/reviewers/skill-reviewer-prompt.md` | CSO 검증 시 "skill-creator 최적화 권장" 문구 추가 (선택) |

### 5.5 전제 조건

- skill-creator 플러그인이 설치되어 있어야 함 (`~/.claude/plugins/`)
- 미설치 시 A) 선택만 가능하도록 graceful degradation
- skill-creator의 Python 스크립트 실행을 위한 Python 환경

---

## 6. 결론

| 관점 | 결론 |
|------|------|
| **설계 품질** | aidlc가 압도적 (패턴 가이드, 압박 테스트, 설득 원칙) |
| **정량적 검증** | skill-creator가 압도적 (벤치마크, description 최적화) |
| **통합 가치** | 높음 — 서로의 약점을 정확히 보완 |
| **통합 비용** | 낮음 — 게이트 1개 추가 + 스킬 체이닝 (기존 패턴) |
| **risk** | 낮음 — 선택적 게이트, graceful degradation |
