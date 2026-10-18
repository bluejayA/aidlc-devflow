# Anthropic "Harness Design" 분석 및 aidlc-devflow 개선 인사이트

**Date**: 2026-03-30
**Source**: https://www.anthropic.com/engineering/harness-design-long-running-apps
**Author**: Anthropic (Prithvi Rajasekaran)
**Analyzed by**: Claude Opus 4.6

---

## 1. 원문 핵심 요약

### 1.1 발견된 문제점

| 문제 | 설명 |
|------|------|
| 컨텍스트 불안감 | 모델이 장시간 작업 시 컨텍스트 윈도우 채움에 따라 일관성을 잃고, 작업을 조기 종료하려 함 |
| 자체 평가의 한계 | 에이전트에게 자신의 작업을 평가하도록 요청하면 품질이 평범해도 자신 있게 칭찬. 검증 가능한 테스트가 없는 주관적 작업에서 특히 심각 |

### 1.2 해법 아키텍처

**GAN 영감의 생성기/평가기 분리:**
- 생성기 에이전트가 코드/디자인을 생성
- 평가기 에이전트가 Playwright MCP로 실제 앱과 상호작용하며 독립 평가
- 5-15회 반복, 매 사이클마다 평가 피드백이 생성기를 개선

**3단계 에이전트 아키텍처:**

```
계획 에이전트 → 생성 에이전트 → 평가 에이전트
(사양 확장)    (스프린트 구현)   (Playwright 검증)
```

**스프린트 계약:** 생성기와 평가기가 코드 작성 전에 "완료"의 정의에 동의

### 1.3 정량화된 평가 기준 (4축)

| 축 | 기준 |
|----|------|
| 디자인 품질 | 색상, 타이포그래피, 레이아웃, 이미지가 통합된 전체적 느낌 |
| 독창성 | 맞춤형 결정 증거. 템플릿 기본값/AI 생성 패턴 회피 |
| 기술력 | 타이포그래피 계층, 간격 일관성, 색상 조화, 명도 대비 |
| 기능성 | 사용자가 추측 없이 주요 작업을 완료할 수 있는가 |

### 1.4 하네스 진화 원칙

> "하네스의 모든 구성요소는 '모델이 혼자 못한다'는 가정을 인코딩한다. 모델이 개선되면 가정을 재검토하라."

- Opus 4.6 출시 후 스프린트 분해가 불필요해짐 → 하네스 단순화
- 평가기를 단일 최종 패스로 이동
- 비용 대비 가치: 평가기는 작업이 모델의 신뢰 범위를 벗어날 때만 가치 있음

### 1.5 실제 결과

| 구성 | 시간 | 비용 | 결과 |
|------|------|------|------|
| 솔로 실행 | 20분 | $9 | 제한적 기능, 게임플레이 미작동 |
| 완전 하네스 | 6시간 | $200 | 16개 기능, 10개 스프린트, 기본 게임플레이 작동 |
| V2 하네스 (Opus 4.6) | 3시간 50분 | $124.70 | 단순화된 구조로도 동등 품질 |

---

## 2. aidlc-devflow 현재 상태와의 매핑

### 2.1 이미 잘 구현된 부분 (Alignment)

| Anthropic 원칙 | aidlc 현재 구현 | 평가 |
|---|---|---|
| 컨텍스트 리셋 via 구조화된 산출물 | `session-summary.md`, `devflow-state.md`, Phase 전환 시 산출물 기반 핸드오프 | Strong |
| 생성기/평가기 분리 | `code-generation` ↔ `requesting-code-review` + Council 리뷰 | Strong |
| 스프린트 계약 | `code-generation`의 Plan → Gate 승인 → Generate 2단계 | Strong |
| 반복 루프 | Gate 패턴의 A/B 선택으로 수정→재생성 루프 | Strong |
| 단계별 컨텍스트 로딩 | 3-tier 위임 체인 (Entry → Phase Orchestrator → Stage Skill) | Strong |
| 에이전트 튜닝 | 10개 리뷰어 프롬프트, 각각 전문 영역별 채점 | Moderate |

### 2.2 핵심 차이점

| 차원 | Anthropic 하네스 | aidlc-devflow |
|------|-----------------|---------------|
| 평가 트리거 | 매 생성 사이클마다 **자동** | 사용자가 `R` 선택 시에만 (수동) |
| 평가 기준 | 정량 루브릭 (4축 등급) | 정성적 피드백 (Issues/Recommendations) |
| 반복 제어 | 자동 N회 반복 후 사용자 제시 | 매 단계 사용자 게이트 |
| unit 간 격리 | 항상 새 에이전트 spawn | 선택적 (subagent-driven-development) |
| 검증 방법 | Playwright E2E + 유닛 테스트 | 유닛/통합 테스트 중심 |
| 하네스 진화 | 모델 능력에 따라 동적 단순화 | 프로젝트 복잡도 기준 (Minimal/Standard/Comprehensive) |

---

## 3. 개선 인사이트 상세

### Insight A: 자동 평가 루프 도입

**현재 갭**: 평가(코드 리뷰)는 사용자가 `R` 옵션을 명시적으로 선택해야만 발생. Anthropic에서는 매 생성 사이클마다 자동으로 평가기가 실행되고, 기준 미달이면 사용자 개입 없이 재생성.

**개선 방향**:
- `build-and-test` 후 테스트 실패 시: 현재는 사용자에게 A/B 게이트를 제시하지만, **자동 debugging → 자동 재빌드 루프**를 N회(예: 3회)까지 허용하는 옵션
- `code-generation: GENERATE` 후: 기본 정적 분석/린트를 자동 실행하여 명백한 문제는 게이트 전에 자동 수정
- 사용자 게이트 도달 시점의 품질 하한선을 높임

```
현재: Generate → [사용자 게이트] → (R 선택 시) Review
개선: Generate → Auto-Lint/Test → (실패 시 자동 재시도 N회) → [사용자 게이트]
```

**영향 범위**: `construction-orchestrator`, `code-generation`, `build-and-test`

### Insight B: 정량화된 평가 기준 (루브릭)

**현재 갭**: Council 리뷰나 code-reviewer가 정성적 피드백만 제공. Anthropic은 평가 축별 등급 기준을 명시하여 평가기의 판단을 보정.

**개선 방향**:
- 각 리뷰어 프롬프트에 채점 루브릭 추가
  - `security-reviewer`: OWASP 체크리스트 기반 점수
  - `code-quality-reviewer`: 복잡도/중복도/테스트 커버리지 기준
  - `spec-reviewer`: 요구사항 충족률 (체크리스트 매칭)
- `PASS / CONDITIONAL / FAIL` 판정을 루브릭 점수 기반으로 도출
- "발견한 문제를 스스로 괜찮다고 판단해버리는" 문제 억제

**영향 범위**: `_shared/reviewers/*.md` 전체

### Insight C: unit별 컨텍스트 리셋 (기본화)

**현재 갭**: `construction-orchestrator`의 multi-unit 루프는 같은 컨텍스트 내에서 순회. `subagent-driven-development`는 선택적.

**개선 방향**:
- `subagent-driven-development`를 construction-orchestrator의 **기본 실행 모드**로 승격
- 단일 unit인 경우만 인라인 실행
- unit 간 전달 정보를 `session-summary.md` + `units.md`의 구조화된 산출물로 한정
- 3번째 unit 구현 시 1번째 unit의 시행착오 컨텍스트 오염 방지

**영향 범위**: `construction-orchestrator`, `subagent-driven-development`

### Insight D: 하네스 동적 단순화 메커니즘

**현재 갭**: Complexity 3단계는 프로젝트 복잡도 기준이지 모델 능력 기준이 아님.

**개선 방향**:
- 모델별 프로파일 도입
- Opus 4.6에서는 `functional-design`이나 `units-generation` 스킵 임계값을 낮춤
- 모델 능력에 따른 자동 게이트 스킵 고려

**영향 범위**: `workflow-planning`, `inception-orchestrator`

### Insight E: Playwright MCP 기반 E2E 자동 검증

**현재 갭**: `build-and-test`는 유닛/통합 테스트 실행에 집중. 실제 UI 검증 없음.

**개선 방향**:
- `build-and-test` 스킬에 E2E 자동 검증 모드 추가 (프론트엔드 프로젝트 한정)
- 평가기 에이전트가 Playwright MCP로 실제 UI를 조작하며 기능 검증
- tech-stack-defaults에서 프론트엔드 프로젝트 감지 시 자동 활성화

**영향 범위**: `build-and-test`, `tech-stack-defaults`

### Insight F: 검증 계약 (Verification Contract)

**현재 갭**: `code-generation`의 Plan은 "어떻게 만들지"에 집중. "어떻게 검증할지"는 암묵적.

**개선 방향**:
- Plan 산출물에 **Verification Contract** 섹션 추가
- "이 unit은 다음을 만족하면 완료: [체크리스트]" 형태
- `build-and-test`가 이 계약을 자동으로 참조하여 pass/fail 판정

**영향 범위**: `code-generation` (Plan 템플릿), `build-and-test`

### Insight G: 리뷰 ROI 자동화

**현재 갭**: `Ra` (자동 선택)가 risk score 기반으로 single/council을 결정하지만, 리뷰 자체의 필요성은 판단하지 않음.

**개선 방향**:
- risk score가 낮으면 리뷰 자체를 스킵하는 옵션
- "보일러플레이트 CRUD라 리뷰 ROI가 낮다" vs "인증 로직이라 Council 필수"
- 누적 데이터로 리뷰 ROI 모델 개선

**영향 범위**: `requesting-code-review`, `construction-orchestrator`

### Insight H: audit 기반 하네스 최적화

**현재 갭**: `devflow-audit`는 이력 보존 목적으로만 사용. 하네스 개선의 데이터 소스로 활용되지 않음.

**개선 방향**:
- 어떤 게이트에서 사용자가 항상 B를 누르는지 분석 → 자동화 후보
- 어떤 스테이지가 실제로 품질에 기여하는지 측정 → 스킵 후보
- audit 로그 분석 유틸리티 스킬 개발

**영향 범위**: `devflow-audit` 유틸리티, 전체 게이트 패턴

---

## 4. 우선순위 매트릭스

| 순위 | 인사이트 | 난이도 | 영향도 | 설명 |
|------|---------|--------|--------|------|
| 1 | **F: 검증 계약** | 낮음 | 높음 | code-plan 템플릿에 섹션 추가만으로 구현 가능 |
| 2 | **A: 자동 평가 루프** | 중간 | 높음 | build-and-test에 자동 재시도 로직 추가 |
| 3 | **B: 정량 루브릭** | 중간 | 높음 | 리뷰어 프롬프트 개선 |
| 4 | **C: unit별 컨텍스트 리셋** | 중간 | 중간 | subagent-driven-development 기본화 |
| 5 | **H: audit 기반 최적화** | 높음 | 높음 | 장기 과제, devflow-audit 분석 도구 필요 |
| 6 | **D: 모델별 게이트 프로파일** | 높음 | 중간 | 모델 감지 + 설정 시스템 필요 |
| 7 | **E: Playwright E2E** | 중간 | 조건부 | 프론트엔드 프로젝트에만 해당 |
| 8 | **G: 리뷰 ROI 자동화** | 높음 | 중간 | Ra 확장, 데이터 축적 후 |

---

## 5. 메타 관찰

### aidlc가 Anthropic 하네스보다 강한 점

1. **인간 참여 게이트**: Anthropic 하네스는 완전 자동 루프 지향이지만, aidlc의 A/B 게이트는 사용자 판단을 핵심 체크포인트로 삼음. 이는 "AI가 잘못된 방향으로 오래 달리는" 리스크를 줄임
2. **세션 연속성**: Anthropic은 단일 실행 기준이지만, aidlc는 세션 끊김/재개를 1등 시민으로 처리
3. **복잡도 적응**: Minimal/Standard/Comprehensive 3단계로 프로젝트에 맞게 하네스 깊이 조절
4. **Council 리뷰**: 다중 AI 평가기 합의 (Anthropic은 단일 평가기)

### Anthropic 하네스가 aidlc보다 강한 점

1. **자동 반복**: 사용자 개입 없이 품질이 올라갈 때까지 자동 루프
2. **실제 앱 검증**: Playwright로 실제 사용자 경험을 테스트
3. **하네스 진화 인식**: 모델 능력 향상에 따른 하네스 단순화를 명시적으로 설계
4. **정량 평가 기준**: 주관적 판단을 수치화하여 평가 일관성 확보
