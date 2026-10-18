---
type: pattern
applies_to: [aidlc-requesting-code-review, aidlc-inception-orchestrator]
status: active
source: manual
last_validated: 2026-04-13
---

# Council Review Protocol

agent-council 기반 다각도 리뷰의 공통 프로토콜.
설계 리뷰(inception)와 코드 리뷰(construction) 모두 이 프로토콜을 따른다.

## Risk Scoring

리뷰 모드 자동 선택(Ra) 시 사용하는 점수 계산.

```
risk_score = 영향도(1~3) + 변경표면(1~3) + 신규성(1~2) + 보안민감(0/2)
```

| 항목 | 1점 | 2점 | 3점 |
|------|-----|-----|-----|
| 영향도 | 단일 컴포넌트 | 2~3 컴포넌트 | cross-cutting 변경 |
| 변경표면 | 1~2 파일 | 3~5 파일 | 6+ 파일 |
| 신규성 | 기존 패턴 확장 | 신규 컴포넌트 | — |
| 보안민감 | 0: 보안 무관 | — | 2: 보안 관련 |

### 모드 매핑

| risk_score | 모드 |
|-----------|------|
| 0~3 | single |
| 4~6 | council-lite |
| 7+ | council-full |

자동 선택된 모드가 CLI 환경에서 불가하면 한 단계 아래로 폴백:
council-full → council-lite → single

---

## 모드별 실행 절차

### 공통 1단계: CLI 감지 + 사용자 확인

모든 council 리뷰(R2/Ra)는 실행 전에 `_shared/patterns/council-cli-detection.md`의 절차를 따른다:

1. CLI 감지 실행 → 가용 AI 목록 표시
2. 사용자에게 참여 AI 확인 (전부/일부/없이)
3. 모드 확정 (council-full/council-lite/single)

모드가 확정된 후 아래 절차를 실행한다.

### single 모드

기존 단일 리뷰(R1)와 동일한 Stage 흐름으로 실행:
- 설계 리뷰: `artifact-reviewer-prompt.md` 서브에이전트 dispatch
- 코드 리뷰: R1 흐름 그대로 — Stage 1(Spec, 제공 시) → Stage 2(Quality) → Stage 3(Security, Standard 이상) → Stage 4(Maintainability, Comprehensive만)

### council-full 모드

1. **프롬프트 생성**: 리뷰 유형(설계/코드)에 따라 관점별 프롬프트 선택
2. **병렬 dispatch**:
   - Codex: agent-council 플러그인을 통해 Codex 관점 프롬프트 + 파일 경로 전달
   - Gemini: agent-council 플러그인을 통해 Gemini 관점 프롬프트 + 파일 경로 전달
3. **결과 저장**: 각 에이전트가 약속된 경로에 결과 md 작성
4. **의장 종합**: Claude 서브에이전트가 개별 결과를 읽고 synthesis.md 작성
5. **사용자 승인**: synthesis 결과를 표시하고 승인 대기

### council-lite 모드

council-full과 동일하되, 사용자가 선택한 외부 AI 1개만 참여:
1. **프롬프트 병합**: 선택된 외부 AI에게 두 관점을 모두 포함한 프롬프트 전달
2. **dispatch**: 외부 AI 1개 + Claude 의장
3. **결과 저장**: 외부 AI 결과 파일 1개 + synthesis.md
4. 나머지는 council-full과 동일

---

## 관점 분리 프롬프트

### 설계 리뷰용 (application-design)

#### Codex 관점

```
## 리뷰 관점: 아키텍처/구현

아래 파일을 읽고 아키텍처 관점에서 리뷰하세요.

리뷰 대상:
- [application-design.md 경로]

참조 컨텍스트:
- [requirements.md 경로]
- [workspace.md 경로]

검토 항목:
1. 컴포넌트 경계가 명확한가 — 책임이 겹치거나 모호한 컴포넌트
2. 의존성 방향이 안정적인가 — 순환 의존, 불안정한 방향
3. 인터페이스 계약이 구현 가능한가 — 모호한 계약, 누락된 에러 케이스
4. 기존 아키텍처와 일관되는가 — workspace.md의 기존 구조와 충돌

결과를 아래 규격으로 [결과 저장 경로]에 작성하세요.
```

#### Gemini 관점

```
## 리뷰 관점: 트레이드오프/운영

아래 파일을 읽고 트레이드오프와 운영 관점에서 리뷰하세요.

리뷰 대상:
- [application-design.md 경로]

참조 컨텍스트:
- [requirements.md 경로]
- [nfr-requirements.md 경로] (있으면)

검토 항목:
1. 누락된 트레이드오프 — 선택하지 않은 대안과 그 이유
2. 엣지 케이스 — 설계가 다루지 않는 경계 상황
3. 운영 관점 — 모니터링, 디버깅, 장애 복구 고려
4. 확장성 — 요구사항 변경 시 설계의 유연성
5. NFR 충족 여부 — nfr-requirements가 있으면 교차 검증

결과를 아래 규격으로 [결과 저장 경로]에 작성하세요.
```

### 코드 리뷰용 (code-generation)

> **4-stage와 Council의 관계**: 4-stage는 "무엇을 볼 것인가"(관점 커버리지), Council은 "누가 볼 것인가"(다모델 편향 보완). 두 차원은 직교한다. Council 모드에서도 4-stage 관점은 그대로 적용되며, Council이 바꾸는 것은 각 Stage의 실행 주체이다.
>
> | Stage | single (R1) | council (R2) |
> |-------|-------------|--------------|
> | Stage 1 (Spec) | Claude 서브에이전트 | Claude 서브에이전트 (변경 없음) |
> | Stage 2 (Quality) | Claude 서브에이전트 | Claude 의장 + 외부 AI |
> | Stage 3 (Security) | Claude 서브에이전트 | Claude 의장 + 외부 AI |
> | Stage 4 (Maintainability) | Claude 서브에이전트 | Claude 의장 + 외부 AI |
>
> Stage 1은 요구사항 대조(사실 확인)라 외부 AI 없이도 충분. Stage 2-4는 판단적 리뷰라 다모델 관점이 가치가 있다.

#### Codex 관점 — Stage 2 (Quality) + Stage 4 (Maintainability)

```
## 리뷰 관점: 코드 품질 + 유지보수성

아래 파일을 읽고 코드 품질과 유지보수성 관점에서 리뷰하세요.

리뷰 대상:
- [변경 파일 경로 목록]

참조 컨텍스트:
- [requirements.md 경로]
- [테스트 결과 요약]

### 품질 검토 (Stage 2)
1. 관용적 코드 — 언어/프레임워크 관례 준수
2. 성능 — 불필요한 연산, N+1 쿼리, 메모리 누수
3. 중복 로직 — DRY 위반, 추상화 기회
4. 패턴 적용 — 적절한 디자인 패턴 사용 여부

### 유지보수성 검토 (Stage 4) — Comprehensive depth만
5. 결합도 — 불필요한 직접 의존, 변경 전파 리스크, 순환 의존
6. 확장성 — 요구사항 변경 시 수정 범위, Open/Closed 원칙
7. 기술 부채 — TODO/FIXME/HACK, 폐기 예정 API, 복사-붙여넣기 코드

Standard depth에서는 품질 검토(1-4)만 수행하세요.

결과를 아래 규격으로 [결과 저장 경로]에 작성하세요.
```

#### Gemini 관점 — Stage 3 (Security/Edge-case)

```
## 리뷰 관점: 보안/논리/엣지케이스

아래 파일을 읽고 보안, 논리 오류, 엣지케이스 관점에서 리뷰하세요.

리뷰 대상:
- [변경 파일 경로 목록]

참조 컨텍스트:
- [requirements.md 경로]

검토 항목:
1. 보안 취약점 — OWASP Top 10 (인젝션, XSS, 인증 우회 등)
2. 언어별 보안 — eval/exec, unsafe, force unwrap, shell=True 등
3. 논리 오류 — 조건문 누락, 경계값 처리, race condition
4. 엣지케이스 — 빈 입력, 대량 데이터, 동시성, 타임아웃
5. 데이터 흐름 — 민감 데이터 전파 경로, 신뢰 경계 검증
6. 테스트 갭 — 테스트되지 않은 경로, edge case 미검증
7. 회귀 리스크 — 기존 기능에 영향을 줄 수 있는 변경

결과를 아래 규격으로 [결과 저장 경로]에 작성하세요.
```

### council-lite 병합 프롬프트

외부 AI가 1개만 있을 때, 해당 AI에게 모든 관점을 포함한 프롬프트를 전달한다.

```
## 리뷰 관점 (통합 — 모든 관점 수행)

아래 파일을 읽고 아래 관점들에서 리뷰하세요.
각 관점별로 섹션을 나누어 결과를 작성하세요.

### 관점 1: 코드 품질 + 유지보수성
[Codex 프롬프트의 검토 항목 전체 — Standard: 품질만, Comprehensive: 유지보수성 포함]

### 관점 2: 보안/논리/엣지케이스
[Gemini 프롬프트의 검토 항목 전체]

리뷰 대상:
- [경로 목록]

참조 컨텍스트:
- [경로 목록]

결과를 아래 규격으로 [결과 저장 경로]에 작성하세요.
```

---

## 리뷰 결과 md 규격

각 에이전트(Codex, Gemini)의 결과 파일 형식:

```markdown
# Review: [reviewer-name]

## Summary
[한 줄 요약]

## Issues

### R-001 [P0|P1|P2|P3] [category]
- **Evidence**: [파일:라인 — 구체적 근거]
- **Impact**: [영향]
- **Fix**: [수정 방안]
- **Must fix for gate**: [yes|no]

### R-002 ...

## Recommendations
- [승인 차단 아닌 개선 제안]

## Missing Information
- [추가 정보가 필요한 항목]
```

### 우선순위 정의

| 등급 | 의미 | 게이트 영향 |
|------|------|-----------|
| **P0** | 차단 — 반드시 수정 필요 | FAIL |
| **P1** | 중요 — 수정 강력 권장 | CONDITIONAL |
| **P2** | 개선 — 수정 권장 | PASS |
| **P3** | 참고 — 선택적 개선 | PASS |

---

## 의장 종합 절차

Claude 의장이 개별 에이전트 결과 파일을 읽고 synthesis.md를 작성한다.

### 입력

- 개별 에이전트 결과: `{review-raw}/codex.md`, `{review-raw}/gemini.md`
- council-lite인 경우: 외부 AI 결과 파일 1개

### synthesis.md 구조

```markdown
# Review Synthesis

## Gate Decision: [PASS|CONDITIONAL|FAIL]
**Rationale**: [판정 근거 — 어떤 이슈가 판정을 결정했는지]

## Consensus (양측 합의)
- [양쪽이 동의한 이슈 목록 — 이슈 ID 참조]

## Divergence (의견 충돌)
| 쟁점 | Codex 의견 | Gemini 의견 | 의장 판정 | 근거 |
|------|-----------|------------|----------|------|
| [쟁점] | [의견] | [의견] | [판정] | [근거] |

## Unique Insights
- [특정 에이전트만 발견한 관점]

## Action Items
- [ ] [P0] [수정 항목] — [출처: codex/gemini]
- [ ] [P1] [수정 항목] — [출처: codex/gemini]
- [ ] [P2] [개선 항목] — [출처: codex/gemini]
```

### Gate Decision 기준

| 미해결 이슈 최고 등급 | Gate Decision |
|---------------------|---------------|
| P0 1개 이상 | **FAIL** — 수정 필수 |
| P1만 (P0 없음) | **CONDITIONAL** — 수정 강력 권장, 사용자 판단 |
| P2/P3만 | **PASS** — 승인, 개선 참고 |

---

## 충돌 해결 규칙

두 에이전트의 의견이 상충할 때 의장이 적용하는 4단계 해결 절차.

### 1단계: 증거 우선

- 파일:라인 등 구체적 근거가 있는 주장 > 근거 없는 주장
- 양쪽 모두 근거 있으면 → 2단계로

### 2단계: 분야별 가중치

| 분야 | 우선 에이전트 | 이유 |
|------|------------|------|
| 보안 이슈 | Gemini | 보안/OWASP 관점 전담 |
| 코드 구현/품질 | Codex | 코드 관용성, 성능 전담 |
| 아키텍처/설계 | Codex | 아키텍처 일관성, 컴포넌트 경계 전담 |
| 비즈니스/정합성 | Claude 의장 | 요구사항-설계 정합성 전담 |

가중치로 해소 안 되면 → 3단계로

### 3단계: 1회 재질의

- 충돌 쟁점만 해당 에이전트에게 재질문
- 재질의는 **1회만** 허용
- 재질의 결과를 synthesis의 Divergence 테이블에 반영

### 4단계: 의장 최종 판정

- 재질의 후에도 충돌 시 의장이 근거를 명시하여 최종 결정
- Divergence 테이블에 "의장 최종 판정" 기록

---

## 파일 경로 기반 컨텍스트 전달

**핵심 원칙**: 프롬프트에 파일 내용을 복사하지 않는다.

### 전달 형식

```
리뷰 대상 파일:
- [경로 1]
- [경로 2]
참조 컨텍스트:
- [경로 3]
- [경로 4]
결과 저장 위치:
- [경로]
```

### 이유

- 토큰 절약: 대형 문서/코드를 프롬프트에 임베드하지 않음
- 컨텍스트 무손실: 압축/요약 없이 원본 직접 읽기
- 대용량 대응: 코드베이스 크기와 무관하게 경로 목록만 전달
