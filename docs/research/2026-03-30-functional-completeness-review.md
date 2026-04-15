# AIDLC DevFlow 기능 완성도 리뷰

**일시**: 2026-03-30
**대상**: aidlc-devflow v1.4.1 (30 skills, 2 orchestrators)
**방법**: End-to-End 시뮬레이션 기반 정적 분석

---

## 1. 토큰 소모량 분석

### INCEPTION Phase (스테이지별)

| 스테이지 | SKILL.md | 참조 파일 | 합계 | 비고 |
|----------|----------|-----------|------|------|
| Entry (using-devflow) | 10 KB | — | **10 KB** | 세션 시작 시 즉시 로드 |
| Orchestrator (inception) | 18 KB | conventions(16)+interrupt(2) | **36 KB** | 매 게이트 평가마다 |
| workspace-detection | 8 KB | — | **8 KB** | |
| requirements-analysis | 13 KB | workspace(0.5)+tech-stacks(2~5) | **15~18 KB** | |
| user-stories | 5 KB | requirements(1) | **6 KB** | 조건부 |
| nfr-requirements | 6 KB | requirements(1) | **7 KB** | 조건부 |
| workflow-planning | 5 KB | 선행 산출물(~30) | **35 KB** | 누적 컨텍스트 최대 |
| application-design | 6 KB | requirements(1)+nfr(0.5) | **7.5 KB** | 조건부 |
| units-generation | 2 KB | app-design(1)+requirements(1) | **4 KB** | 최소 |

**INCEPTION 총계**: ~127 KB (Comprehensive 기준, 모든 스테이지 포함)
**피크 지점**: workflow-planning (~35 KB, 선행 산출물 전체 참조)

### CONSTRUCTION Phase (스테이지별)

| 스테이지 | SKILL.md | 참조/리뷰 | 합계 | 비고 |
|----------|----------|-----------|------|------|
| Orchestrator (construction) | 14 KB | context(20~30) | **34~44 KB** | 매 게이트 평가마다 |
| functional-design | 4 KB | 산출물(8) | **12 KB** | Comprehensive만 |
| code-generation Plan | 7 KB | — | **7 KB** | |
| code-plan 리뷰 | — | reviewer(12) | **12 KB** | Standard 이상 자동 |
| code-generation Generate | 7 KB | TDD protocol(15~20) | **22~27 KB** | 핵심 구현 단계 |
| 구현 리뷰 (Distrust by Default) | — | reviewer(15~25) | **15~25 KB** | Standard 이상 자동 |
| build-and-test | 5 KB | code-plans(5~10) | **10~15 KB** | |
| auto-fix (최대 3회) | — | code-gen 재호출 | **8 KB × 횟수** | |
| systematic-debugging | 10 KB | — | **10 KB** | 실패 시에만 |
| K gate + devflow-solutions | — | solutions(10~15) | **10~15 KB** | 디버깅 후 선택 |

**CONSTRUCTION 총계 (단일 unit, Standard)**: ~140~200 KB
**Multi-unit (인라인 N개)**: +40~60 KB × (N-1)
**Multi-unit (SDD N개)**: ~160~220 KB (SDD가 컨텍스트 격리)

### 전체 세션 토큰 소모 예상

| 시나리오 | INCEPTION | CONSTRUCTION | 합계 |
|----------|-----------|--------------|------|
| Minimal, 단일 unit | 60 KB | 80 KB | **~140 KB** |
| Standard, 단일 unit | 90 KB | 160 KB | **~250 KB** |
| Standard, 3 unit (SDD) | 90 KB | 220 KB | **~310 KB** |
| Comprehensive, 5 unit (SDD) | 127 KB | 350 KB | **~477 KB** |

---

## 2. 토큰 소모 분포 차트

```
토큰 소모 분포 (Standard, 단일 unit, ~250 KB)

INCEPTION Phase (90 KB, 36%)
████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

CONSTRUCTION Phase (160 KB, 64%)
████████████████████████████████████░░░░░░░░░░░░░░░

---

INCEPTION 내부 분포:
                         ██████████████████ orchestrator (36 KB, 40%)
                 ████████ requirements (18 KB, 20%)
             ████████████ workflow-planning (35 KB, 39%)
█                          others (1 KB, 1%)

---

CONSTRUCTION 내부 분포:
             ██████████████████ orchestrator (44 KB, 28%)
         ████████████ code-gen Generate (27 KB, 17%)
         ████████████ 구현 리뷰 (25 KB, 16%)
     ████████ code-plan + 리뷰 (19 KB, 12%)
     ████████ build-and-test (15 KB, 9%)
   ██████ functional-design (12 KB, 7%)
   █████ debugging+K (15 KB, 9%)
 ██ others (3 KB, 2%)

---

스테이지별 누적 토큰 (Standard, 단일 unit)

250 KB ┤                                              ╭─── 완료
       │                                         ╭────╯
200 KB ┤                                    ╭────╯ build
       │                              ╭────╯ 구현리뷰
150 KB ┤                         ╭────╯ code-gen
       │                    ╭────╯ code-plan+리뷰
100 KB ┤               ╭────╯ construction 진입
       │          ╭────╯ workflow-planning
 50 KB ┤     ╭────╯ requirements
       │╭────╯ workspace+entry
  0 KB ┤╯
       └──────────────────────────────────────────────
        시작                                      완료
```

---

## 3. 발견된 문제점 (우선순위별)

### Critical (즉시 수정 필요) — 3건

| # | 위치 | 문제 | 영향 |
|---|------|------|------|
| C-1 | INCEPTION: Pre-Planning 게이트 | Minimal/Standard/Comprehensive별 자동 결정이 사용자에게 통보되지 않음. Minimal은 user-stories+NFR을 자동 스킵하는데 스킵 사실을 알려주지 않음 | 사용자가 스킵된 줄 모르고 진행 |
| C-2 | CONSTRUCTION: code-plan 리뷰 FAIL | 리뷰어가 FAIL 반환 시 사용자에게 스킵/오버라이드 옵션 없음. B(승인)만 비활성 → 사용자가 리뷰어에 의해 차단됨 | 리뷰어 오탐 시 진행 불가 |
| C-3 | INCEPTION: HELD 상태 회수 없음 | user-stories/NFR에서 H(Hold) 선택 후 다시 돌아가는 게이트가 없음. session-summary에 기록만 되고 재방문 메커니즘 없음 | Hold한 항목이 영구 미처리 |

### Important (혼동 유발) — 5건

| # | 위치 | 문제 | 영향 |
|---|------|------|------|
| I-1 | INCEPTION: 워크트리 브랜치명 | User Intent에서 자동 추출한 브랜치명에 확인 게이트 없음. 비영어 Intent 시 추출 실패 가능 | 잘못된 브랜치명으로 워크트리 생성 |
| I-2 | CONSTRUCTION: SDD 모드 컨텍스트 격리 | SDD에서 unit별 게이트 비활성화 → code-plan 승인 없이 구현 시작. orchestrator가 functional-design을 사전 실행하는데 SDD에 전달 여부 불명확 | 설계-구현 불일치 가능 |
| I-3 | CONSTRUCTION: 재검증 무한 루프 | 세션 재개 시 revalidation 실패 → debugging → revalidation 반복에 최대 횟수 제한 없음 | 사용자 무한 루프 |
| I-4 | CONSTRUCTION: S 게이트 의미 모호 | "이번 unit 리뷰 스킵"의 정확한 의미가 불명확. "나중에 다시" vs "영구 무시" 구분 안 됨 | 사용자 혼동 |
| I-5 | INCEPTION: NFR 모드 선택 소유권 | orchestrator가 보여줘야 할 모드 게이트(GENERATE/IMPORT/SKIP)가 스킬 내부에도 있어 중복 가능 | 게이트 이중 표시 또는 누락 |

### Minor (매끄럽지 않은 흐름) — 5건

| # | 위치 | 문제 |
|---|------|------|
| M-1 | INCEPTION: NFR 기본값 미정의 | domain × profile 조합별 기본 NFR 수치가 SKILL.md에 없음 → 자유 입력으로 전락 |
| M-2 | INCEPTION: units 위상 정렬 검증 없음 | unit 의존성 순서의 정합성을 검증하는 게이트 없음 |
| M-3 | CONSTRUCTION: auto-fix 키워드 오탐 | `permission`, `auth` 키워드로 auto-fix를 스킵하는데 파일 시스템 권한 오류도 매칭됨 |
| M-4 | CONSTRUCTION: 디버깅 루프 무제한 | debugging → build-and-test → debugging 반복에 소프트 리밋 없음 |
| M-5 | INCEPTION: workflow-planning 다이어그램 | A안 기준으로만 생성 → B/C 선택 시 다이어그램이 선택과 불일치 |

---

## 4. 흐름 매끄러움 평가

### 잘 된 부분

1. **3-tier 오케스트레이션** (Entry → Phase → Stage) — 명확한 책임 분리
2. **게이트 패턴 일관성** — A=재시도, B=승인, S=스킵 통일
3. **TDD 프로토콜 강제** — RED-GREEN-REFACTOR 사이클 예외 없음
4. **K 게이트 비침습성** — 기존 Debugging 라우팅에 선택지 추가만, 흐름 변경 없음
5. **Distrust by Default** — Standard 이상 자동 리뷰로 품질 하한선 보장
6. **세션 연속성** — session-summary + devflow-state로 재개 가능

### 개선 필요 부분

1. **게이트 폭발** — INCEPTION에 8+ 중첩 게이트 → 사용자 인지 과부하
2. **컨텍스트 누적** — workflow-planning 시점에 ~35 KB 피크 → 선행 산출물 전체 참조
3. **오류 복구 경로 부족** — 워크트리 실패, tech-stack 카탈로그 부재 등에 대한 폴백 미정의
4. **상태 전환 문서화 부족** — devflow-state 업데이트 시점이 orchestrator에 암시적

---

## 5. 권장 조치 우선순위

### 즉시 (다음 스프린트)
1. **C-2**: code-plan 리뷰 FAIL 시 S(오버라이드) 옵션 추가
2. **C-3**: workflow-planning 후 "HELD 항목 재방문" 게이트 추가
3. **I-1**: 워크트리 브랜치명 확인 게이트 추가

### 단기 (1~2 스프린트)
4. **C-1**: Pre-Planning 자동 결정 시 사용자에게 명시적 안내 추가
5. **I-3**: 재검증 최대 3회 → 에스컬레이션 게이트
6. **I-4**: S 게이트 설명 강화 ("리뷰 이슈를 무시하고 진행")

### 중기 (3+ 스프린트)
7. **I-2**: SDD 모드 functional-design 전달 문서화
8. **I-5**: NFR 모드 게이트 소유권 명확화
9. **M-1~M-5**: Minor 이슈 일괄 처리


---
⏺ Agent Council 결과 종합

  Codex 의견

  ▎ "1M 시대에 감당 가능한 오버헤드, ROI 높음"

  - 250KB = 1M 윈도우의 6~8%, 477KB = 12~16% (token 환산)
  - Opus 기준 세션 비용: Standard $0.31~0.42, Comprehensive $0.60~0.80
  - 손익분기: 작업당 10~30초만 재작업 줄여도 본전
  - 최적화 1순위: 게이트 재로드 요약 카드 + 프롬프트 캐싱

  Gemini 의견

  ▎ "$1.5 보험료로 $50+ 엔지니어링 가치 창출"

  - 250KB = 1M 윈도우의 30~35% (KB 기준), 477KB = 60~65%
  - 시니어 코드 리뷰 1회 대체 = $50+ 인건비 절감
  - 자유 코딩의 hidden cost: Context Drift, Hallucination Tax, Refactoring Amnesia
  - 최적화 1순위: Prompt Caching (공통 conventions 캐시 시 비용 90% 절감)

  의장 종합 (내 분석)

  두 에이전트의 수치 기준이 다릅니다 (Codex: token 환산, Gemini: byte 기준). 정확한 수치를 정리하면:

  토큰 환산 (1 token ≈ 4 chars)
  ─────────────────────────────────────
  Standard 250KB ≈ 62K tokens → 1M의 6.2%
  Comprehensive 477KB ≈ 119K tokens → 1M의 11.9%

  비용 (입력 토큰만, Opus $15/MTok 기준)
  ─────────────────────────────────────
  Standard: 62K × $15/M = $0.93/세션
  Comprehensive: 119K × $15/M = $1.79/세션
  Sonnet 사용 시: 위의 1/5 ($0.19~$0.36)

  결론

  ┌──────────────┬───────────────────────────────────────────────────────────────┐
  │     관점     │                             판단                              │
  ├──────────────┼───────────────────────────────────────────────────────────────┤
  │ 윈도우 점유  │ 6~12% → 충분히 여유 (1M의 88~94% 남음)                        │
  ├──────────────┼───────────────────────────────────────────────────────────────┤
  │ 금전 비용    │ $0.19~$1.79/세션 → 커피 한 잔 미만                            │
  ├──────────────┼───────────────────────────────────────────────────────────────┤
  │ 품질 ROI     │ 버그 1건 방지 = 수시간 절약 → 10~100x 수익                    │
  ├──────────────┼───────────────────────────────────────────────────────────────┤
  │ vs 자유 코딩 │ 하네스 없이는 Context Drift + 환각 디버깅에 더 많은 토큰 소모 │
  └──────────────┴───────────────────────────────────────────────────────────────┘

  두 에이전트 모두 "적절하다"에 합의. 핵심 최적화 제안도 동일: Prompt Caching 도입이 가장 시급.

  다만 Prompt Caching은 Claude Code 플러그인 레벨에서 직접 제어할 수 없고 (API/인프라 레벨), 현실적으로 가능한 최적화는 게이트별 선택적 로딩 (BL-073)과 게이트 폭발 완화 (BL-072)입니다. 이 두
  건이 이미 백로그에 등록되어 있습니다.

