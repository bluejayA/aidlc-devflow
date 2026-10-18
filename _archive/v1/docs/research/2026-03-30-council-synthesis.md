# Agent Council 합의 결과: Harness Design 인사이트 분석

**Date**: 2026-03-30
**Council Members**: Codex, Gemini
**Chairman**: Claude Opus 4.6
**Input**: `docs/research/2026-03-30-harness-design-insights.md`

---

## 1. 합의된 우선순위 (최종)

원래 분석의 8개 인사이트를 Council 논의를 거쳐 재정렬하고, 누락 인사이트 5개를 추가.

| 순위 | 인사이트 | 난이도 | 영향도 | Council 합의 근거 |
|------|---------|--------|--------|-------------------|
| **1** | **F: 검증 계약 (Verification Contract)** | 낮음 | 높음 | 전원 합의. 자동화의 전제 조건. 템플릿 수정만으로 즉시 구현 가능 |
| **2** | **A: 자동 평가 루프 (Self-Healing Loop)** | 중간 | 높음 | 전원 합의. 사용자 피로도를 극적으로 줄임. F의 검증 계약이 루프의 종료 기준이 됨 |
| **3** | **C: unit별 컨텍스트 리셋** | 중간 | 중간~높음 | Gemini 2순위 주장, Codex 4순위 주장 → 의장 판정으로 3순위. 장기 실행 안정성의 핵심이나, F/A 선행이 효과 극대화 |
| **4** | **B: 정량 루브릭** | 중간 | 높음 | 전원 합의. 자동 루프(A)의 품질 기준으로 작동 |
| **5** | **J: 루프 종료 조건 명시** (신규) | 낮음 | 중간 | Codex 제안. A 구현 시 필수 동반 — max_retry, plateau, 비용 상한 |
| **6** | **K: 구조화된 피드백 포맷** (신규) | 낮음 | 중간 | Codex 제안. 평가기 출력 표준화 → 자동 루프 입력으로 활용 |
| **7** | **H: audit 기반 하네스 최적화** | 높음 | 높음 | 전원 동의하되 장기 과제. F/A/B 데이터가 축적되어야 분석 의미 |
| **8** | **I: Distrust by Default** (신규) | 중간 | 중간 | Gemini 제안. 리뷰를 옵션이 아닌 기본으로 전환하는 철학적 전환 |
| **9** | **E: Playwright E2E** | 중간 | 조건부 | 프론트엔드 프로젝트에만 해당. Codex는 UI 중심이면 4위까지 상향 가능 |
| **10** | **D: 모델별 게이트 프로파일** | 높음 | 중간 | 모델 감지 + 설정 시스템 필요. 현재 Opus 4.6 단일 환경에서는 긴급도 낮음 |
| **11** | **L: 생성기/평가기 비대칭 설계** (신규) | 중간 | 중간 | Gemini 제안. 평가기에 Playwright 등 추가 도구 부여 |
| **12** | **M: 비용-품질 관측치 내장** (신규) | 중간 | 중간 | Codex 제안. H의 데이터 소스. 반복마다 시간/토큰/결함밀도 기록 |
| **13** | **G: 리뷰 ROI 자동화** | 높음 | 중간 | 전원 동의: 충분한 운영 데이터 축적 후. 지금 하면 오판 위험 |

---

## 2. 핵심 합의: Gate vs Auto-Loop 하이브리드 전략

**3개 AI 전원이 하이브리드가 최적이라는 데 강한 합의.**

### 이원화 기준

```
객관적 검증 (Auto-Loop)          주관적 판단 (Human Gate)
─────────────────────────        ─────────────────────────
Lint / 정적분석                   아키텍처 방향성
타입 체크                         요구사항 해석
유닛 테스트                       UX/UI 미적 판단
빌드 성공 여부                    보안/컴플라이언스 결정
E2E 기능 테스트                   비즈니스 로직 선택
```

### 에스컬레이션 규칙 (합의)

1. Auto-Loop **N회 실패** (N=3 합의) → 사용자 Gate로 전환
2. **루브릭 점수 임계치 미달** (예: 0.7 이하) → 사용자 Gate
3. **diff 급증** (변경량이 예상의 2배 이상) → 사용자 Gate
4. 모든 자동 통과 건은 **audit 로그에 기록** → 사후 검토 가능

### 현재 aidlc에 적용 시 변경점

```
현재 Flow:
  Generate → [사용자 게이트] → (R 선택 시) Review → [사용자 게이트]

개선 Flow:
  Generate → Auto-Lint → Auto-Test
    ├─ PASS + 점수 ≥ 임계치 → [사용자 게이트] (높은 품질로 도착)
    ├─ FAIL (자동 수정 가능) → Auto-Fix → 재테스트 (max 3회)
    │   ├─ 성공 → [사용자 게이트]
    │   └─ 3회 실패 → [사용자 게이트 + 실패 보고서]
    └─ FAIL (구조적 문제) → 즉시 [사용자 게이트 + 디버깅 권고]
```

---

## 3. 누락 인사이트 통합 (Council 추가 발견)

### I: Distrust by Default (Gemini)

현재 aidlc는 리뷰를 `R` 옵션으로 제공 — "모델이 잘 할 것"을 가정.
Anthropic의 철학은 반대: "검증 실패 전까지는 불신".

**적용 방안**:
- Standard 이상 Complexity에서 코드 리뷰를 **기본 실행**으로 변경
- 사용자가 명시적으로 스킵할 때만 건너뜀 (현재의 opt-in → opt-out 전환)

### J: 루프 종료 조건 명시 (Codex)

자동 평가 루프(Insight A) 구현 시 반드시 동반되어야 하는 안전장치.

**종료 조건 3가지**:
1. `max_retry`: 최대 재시도 횟수 (기본 3회)
2. `plateau_detection`: 연속 2회 동일 에러 → 구조적 문제로 판단, 사용자 에스컬레이션
3. `cost_cap`: 토큰 사용량 상한 (선택적)

### K: 구조화된 피드백 포맷 (Codex)

평가기(리뷰어) 출력을 기계판독 가능한 형태로 표준화.

**현재**: 자유 텍스트 피드백
**개선**:

```json
{
  "verdict": "CONDITIONAL",
  "score": 0.75,
  "issues": [
    {"severity": "high", "category": "security", "file": "auth.ts", "line": 42, "description": "..."},
    {"severity": "low", "category": "style", "file": "utils.ts", "line": 10, "description": "..."}
  ],
  "pass_criteria_met": ["unit-tests", "lint"],
  "pass_criteria_failed": ["integration-test-auth"]
}
```

→ Auto-Loop가 이 구조를 파싱하여 수정 대상을 정확히 지정 가능

### L: 생성기/평가기 비대칭 설계 (Gemini)

생성기와 평가기에 동일한 도구를 주지 말고, 평가기에 더 많은 검증 도구를 부여.

**현재**: 리뷰어는 Read/Glob/Grep만 사용 (read-only)
**개선 방향**: 평가기에 Bash(read-only 명령), Playwright MCP 추가 → 실제 실행 결과로 검증

### M: 비용-품질 관측치 내장 (Codex)

각 반복/스테이지마다 메트릭을 기록하여 하네스 최적화(Insight H)의 데이터 소스로 활용.

**기록 항목**: 소요 시간, 토큰 사용량, 수정된 파일 수, 결함 밀도(issues/kloc), 재시도 횟수

---

## 4. 즉시 실행 계획 (Council 전원 합의)

### Sprint 1: 검증 계약 + 자동 평가 루프 (F + A)

#### 4.1 검증 계약 (Insight F) — 즉시 착수

**변경 대상**: `code-generation` SKILL.md의 Plan 템플릿

**추가할 Verification Contract 섹션**:
```markdown
## Verification Contract

### 완료 조건
- [ ] [구체적 기능 요건 1]
- [ ] [구체적 기능 요건 2]

### 검증 명령
- `npm test` — 유닛 테스트 전체 통과
- `npm run lint` — 린트 에러 0개
- [프로젝트별 추가 명령]

### 리스크 태그
- [ ] auth/security 관련 변경 → Council 리뷰 권장
- [ ] DB 스키마 변경 → 마이그레이션 검증 필수
```

**`build-and-test`에서 참조**: 계약의 검증 명령을 순서대로 실행, 미충족 시 FAIL

#### 4.2 자동 평가 루프 (Insight A) — 다음 착수

**변경 대상**: `build-and-test` SKILL.md, `construction-orchestrator` SKILL.md

**상태 머신**:
```
GENERATE_DONE → AUTO_LINT
  ├─ LINT_PASS → AUTO_TEST
  │   ├─ TEST_PASS → GATE (사용자 승인)
  │   └─ TEST_FAIL → AUTO_FIX (retry ≤ 3)
  │       ├─ FIX_SUCCESS → AUTO_TEST (재검증)
  │       └─ FIX_PLATEAU → ESCALATE (사용자 게이트)
  └─ LINT_FAIL → AUTO_FIX (retry ≤ 3)
      ├─ FIX_SUCCESS → AUTO_LINT (재검증)
      └─ FIX_PLATEAU → ESCALATE (사용자 게이트)
```

---

## 5. 메타 합의: "하네스는 진화해야 한다"

3개 AI 전원이 동의한 메타 원칙:

> **aidlc의 모든 게이트와 스테이지는 "모델이 혼자 못한다"는 가정의 인코딩이다.
> 모델이 개선될 때마다 각 가정을 재검토하고, 불필요해진 것은 제거하라.
> audit 로그는 이 재검토의 데이터 소스다.**

이는 Anthropic 글의 핵심 메시지이자, aidlc가 장기적으로 반드시 내재화해야 할 설계 철학이다.
