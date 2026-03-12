# New INCEPTION Skills Design

**Complexity:** Standard
**Date:** 2026-03-12
**Version:** v0.6.0

## Goal

비개발자가 상용 운영/플랫폼 최적화에 사용할 수 있는 소프트웨어를 AIDLC 플러그인으로 만들 수 있도록, INCEPTION 단계에 user-stories, nfr-requirements 스킬을 추가하고 application-design을 확장한다.

## Scope

| 항목 | 구현 방식 | 상태 |
|------|----------|------|
| `_shared/import-review-protocol.md` | 신규 공유 프로토콜 | In scope |
| `aidlc-user-stories` | 독립 스킬 (GENERATE only) | In scope |
| `aidlc-nfr-requirements` | 독립 스킬 (GENERATE + IMPORT) | In scope |
| `aidlc-application-design` 확장 | Comprehensive DETAIL에 NFR Design 섹션 | In scope |
| `aidlc-inception-orchestrator` | Pre-Planning Gate + hold/skip | In scope |
| `aidlc-workflow-planning` | Pre-Planning 섹션 추가 | In scope |
| `infrastructure-design` | **Deferred** — 별도 설계 사이클 | Out of scope |

## Assumptions

- nfr-design은 독립 스킬이 아닌 application-design Comprehensive DETAIL 확장으로 구현 (같은 맥락에서 컴포넌트 설계와 NFR 패턴을 동시에 결정)
- infrastructure-design은 application-design 이후에 필요하며, 클라우드/온프렘/비용 등 완전히 다른 질문 영역이므로 별도 설계 사이클로 분리

---

## Section 1: Import-Review Protocol (`_shared/import-review-protocol.md`)

### 목적

사용자가 직접 작성한 문서를 Claude가 검토하는 "IMPORT 모드"와 Claude가 처음부터 생성하는 "GENERATE 모드"를 지원하는 공유 프로토콜.

### 두 가지 모드

| 모드 | 주체 | 흐름 |
|------|------|------|
| **GENERATE** | Claude | 질문 → 수집 → 생성 → 리뷰 |
| **IMPORT** | 사용자 | 파일 수신 → 검증 → 피드백 → 확정 |

### IMPORT Mode 프로세스

```
1. 파일 수신: 사용자가 경로 전달 또는 내용 붙여넣기
2. 형식 검증: 필수 섹션 존재 여부 확인
3. 내용 검토: 누락/모순/모호한 항목 식별
4. 피드백 제시:
   - ✅ 충분한 항목
   - ⚠️ 보완 권장 항목 (이유 포함)
   - ❌ 누락/모순 항목 (이유 포함)
5. 사용자 확정: 피드백 반영 여부는 사용자 결정
```

### Hold/Skip Signal

Pre-Planning 스테이지(user-stories, nfr-requirements)에서 실행 중 중단하거나 건너뛸 수 있다.
오케스트레이터가 H(Hold) 또는 S(Skip) 선택을 감지하면 아래 형식으로 산출물을 저장한다.

**Hold**: 진행 중인 작업을 중단하고 나중에 재개
```markdown
## Status: HELD
**Held at**: [중단 시점]
**Reason**: [사용자 제공 이유]
**Completed sections**: [완료된 부분]
**Remaining**: [남은 부분]
```

**Skip**: 이 스테이지를 완전히 건너뜀
```markdown
## Status: SKIPPED
**Reason**: [사용자 제공 이유]
```

오케스트레이터는 HELD/SKIPPED 상태를 devflow-state에 기록하고 다음 스테이지로 진행한다.

### 적용 대상

| 스킬 | GENERATE | IMPORT | Hold/Skip |
|------|----------|--------|-----------|
| `aidlc-user-stories` | ✅ | ❌ | ✅ |
| `aidlc-nfr-requirements` | ✅ | ✅ | ✅ |

user-stories는 requirements-analysis 결과를 기반으로 Claude가 변환하는 것이 핵심 가치이므로 IMPORT 불필요.

---

## Section 2: `aidlc-user-stories` 스킬

### 위치

INCEPTION 흐름에서 requirements-analysis **이후**, workflow-planning **이전** (Pre-Planning 스테이지).

### 목적

요구사항을 INVEST 기준 사용자 스토리로 변환. 비개발자가 "무엇을 만들지"를 사용자 관점에서 정리.

### 실행 흐름

비대화형 생성 — 사용자 질문 없이 requirements.md를 기반으로 일괄 변환한다.
변경 요청은 오케스트레이터 게이트에서 처리.

```
Step 1: Load context
  - devflow-docs/inception/requirements.md 읽기

Step 2: Identify actors
  - 요구사항에서 사용자 유형 추출
  - 액터 목록 제시 (예: 관리자, 일반 사용자, 외부 API)

Step 3: Generate user stories
  - 각 액터별 Given-When-Then 형식 스토리 생성
  - INVEST 기준 검증 (Independent, Negotiable, Valuable, Estimable, Small, Testable)

Step 4: Save artifact
  - devflow-docs/inception/user-stories.md 저장
```

### 산출물 형식

```markdown
# User Stories

**Timestamp**: [ISO 8601]
**Source**: devflow-docs/inception/requirements.md

## Actors
- [Actor1]: [역할 설명]
- [Actor2]: [역할 설명]

## Stories

### US-001: [스토리 제목]
**Actor**: [Actor명]
**Story**: As a [actor], I want [goal] so that [benefit]
**Acceptance Criteria**:
- Given [context], When [action], Then [result]
- Given [context], When [action], Then [result]
**Priority**: [Must | Should | Could]
```

### 리뷰

Standard 이상: artifact-reviewer dispatch.
- 산출물 경로: `devflow-docs/inception/user-stories.md`
- 상위 산출물: `devflow-docs/inception/requirements.md`

Minimal: 리뷰 스킵.

### Return to Orchestrator

STOP.

```
[user-stories 결과]
- 액터: [count]명 ([액터명 나열])
- 사용자 스토리: [count]개 (Must: [N], Should: [N], Could: [N])
- 산출물: devflow-docs/inception/user-stories.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

### 메타데이터

```yaml
name: aidlc-user-stories
description: 요구사항을 INVEST 기준 사용자 스토리로 변환. Pre-Planning 스테이지.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/user-stories.md
```

---

## Section 3: `aidlc-nfr-requirements` 스킬

### 위치

INCEPTION 흐름에서 user-stories **이후** (또는 user-stories 스킵 시 requirements-analysis 이후), workflow-planning **이전** (Pre-Planning 스테이지).

### 목적

비개발자가 "이 소프트웨어에 어떤 품질 요구사항이 필요한가"를 체계적으로 수집. NFR 값을 **결정**하는 것이 아니라 **수집**하는 것.

### 두 가지 모드

- **GENERATE**: Claude가 질문하며 수집 (기본)
- **IMPORT**: 사용자가 작성한 NFR 문서를 검토 (`_shared/import-review-protocol.md` 참조)

### GENERATE 모드 실행 흐름

```
Step 1: Load context
  - devflow-docs/inception/requirements.md 읽기
  - devflow-docs/inception/user-stories.md 읽기 (있으면)

Step 2: Domain context 질문
  - "이 소프트웨어의 도메인은?"
    A) 금융/핀테크 — 높은 보안+컴플라이언스, 감사 추적 필수
    B) 헬스케어 — 데이터 프라이버시(HIPAA 등), 높은 가용성
    C) 이커머스 — 트래픽 변동 대응, 결제 보안
    D) 사내 도구 — 낮은 가용성 허용, 보안 내부망 기준
    E) IoT/임베디드 — 저전력, 네트워크 불안정 고려
    F) 기타 (직접 입력)
  - 선택된 도메인을 이후 프로파일 기본값 조정에 사용

Step 3: Profile 선택 (비개발자 친화)
  - "이 소프트웨어의 운영 환경은?"
    A) MVP/프로토타입 — 기본값으로 충분, NFR 최소화
    B) 소규모 운영 — 사용자 100명 이하, 기본 안정성
    C) 중규모 운영 — 사용자 1000명+, 모니터링 필요
    D) 대규모/엔터프라이즈 — 고가용성, 보안 컴플라이언스

Step 4: Profile 기반 맞춤 질문
  - 도메인 × 프로파일 조합에 따라 질문 범위 결정:
    - MVP: 2~3개 (핵심 보안, 데이터 백업)
    - 소규모: 4~5개 (+ 응답 시간, 동시 접속)
    - 중규모: 6~7개 (+ 모니터링, 장애 복구)
    - 대규모: 8개 카테고리 전체 순회
  - 8개 카테고리: 성능, 가용성, 확장성, 보안, 데이터 무결성,
    모니터링, 재해 복구, 컴플라이언스

Step 5: Domain × Profile 기반 기본값 제시 + 조정
  - "프로파일 기반으로 다음 NFR을 권장합니다:
     - 응답 시간: 500ms 이내 (이유: [도메인] 기준 사용자 체감 임계점)
     - 가용성: 99.9% (이유: [프로파일] 기준 월 43분 다운타임 허용)
     조정이 필요한 항목이 있나요?"
  - 도메인별 기본값 차이 예시:
    - 금융 + 소규모: 가용성 99.95% (금융은 기본보다 높음)
    - 사내 도구 + 중규모: 가용성 99.5% (내부 사용이므로 낮춤)

Step 6: Save artifact
  - devflow-docs/inception/nfr-requirements.md 저장
```

### IMPORT 모드 실행 흐름

`_shared/import-review-protocol.md`의 IMPORT 프로세스를 따른다.
필수 검증 항목: 8개 NFR 카테고리 중 누락 여부, 수치 없는 정성적 표현 ("빨라야 한다" → 구체적 수치 요청).

### 산출물 형식

```markdown
# NFR Requirements

**Timestamp**: [ISO 8601]
**Mode**: [GENERATE | IMPORT]
**Domain**: [선택된 도메인]
**Profile**: [선택된 프로파일]

## NFR Summary

| 카테고리 | 요구사항 | 근거 |
|---------|---------|------|
| 성능 | 응답 시간 500ms 이내 | [도메인+프로파일] 기준 |
| 가용성 | 99.9% | 월 43분 다운타임 허용 |
| ... | ... | ... |

## 조정 이력
- [항목]: [원래 기본값] → [사용자 조정값] (이유: [사용자 설명])
```

### 리뷰

Standard 이상: artifact-reviewer dispatch.
- 산출물 경로: `devflow-docs/inception/nfr-requirements.md`
- 상위 산출물: `devflow-docs/inception/requirements.md`, `devflow-docs/inception/user-stories.md` (있으면)

Minimal: 리뷰 스킵.

### Return to Orchestrator

STOP.

```
[nfr-requirements 결과]
- 모드: [GENERATE | IMPORT]
- 도메인: [선택된 도메인]
- 프로파일: [선택된 프로파일]
- NFR 항목: [count]개 카테고리
- 사용자 조정: [count]개 항목
- 산출물: devflow-docs/inception/nfr-requirements.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]
```

### 메타데이터

```yaml
name: aidlc-nfr-requirements
description: 도메인 컨텍스트 + 프로파일 기반 비기능 요구사항(NFR) 수집. GENERATE/IMPORT 모드 지원. Pre-Planning 스테이지.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/nfr-requirements.md
```

---

## Section 4: `aidlc-application-design` 확장 — NFR Design

### 변경 범위

`## NFR Design Patterns` 섹션 추가. 활성화 조건 (3가지 모두 충족):
1. depth가 **Comprehensive**
2. **DETAIL** 모드
3. `devflow-docs/inception/nfr-requirements.md`가 **존재**

### NFR Design의 핵심 원칙

Claude는 **정보 정리자**이지 **의사결정자**가 아니다. NFR 설계에는 정답이 없고 트레이드오프만 존재하므로:

1. **옵션 테이블**: 각 패턴의 장단점+비용을 병렬 제시
2. **전문가 상담 권고**: `⚠️ 이 선택은 기술 담당자와 상의를 권장합니다`
3. **권장 없음**: "권장 패턴: X" 형식 사용 금지

### 실행 흐름 (DETAIL 모드 내부)

```
기존 Comprehensive DETAIL 완료 후 추가 실행:

Step N+1: Load NFR context
  - devflow-docs/inception/nfr-requirements.md 읽기
  - 없으면: "NFR 요구사항이 수집되지 않았습니다. 기본 패턴으로 진행합니다." 안내

Step N+2: NFR 카테고리별 패턴 매핑
  - nfr-requirements의 각 항목에 대해 컴포넌트 설계와 연계된 패턴 옵션 제시
  - 형식: 옵션 테이블 (권장 표시 없음)

Step N+3: application-design.md 업데이트
  - ## NFR Design Patterns 섹션 추가
```

### 산출물 형식 (application-design.md 내 추가 섹션)

```markdown
## NFR Design Patterns

> ⚠️ NFR 패턴 선택은 운영 환경과 비용에 따라 달라집니다.
> 기술 담당자와 상의를 권장합니다.

### 가용성: 99.9%

| 패턴 | 장점 | 단점 | 비용 영향 |
|------|------|------|----------|
| Active-Standby Failover | 구현 간단, 데이터 일관성 유지 | 전환 시 수 초 다운타임 | 인프라 비용 ~1.5x |
| Active-Active | 무중단, 로드 분산 | 데이터 동기화 복잡 | 인프라 비용 ~2x+ |
| Multi-AZ (클라우드) | 관리형, 자동 전환 | 클라우드 종속 | 리전 간 전송 비용 |

### 성능: 응답 시간 500ms

| 패턴 | 장점 | 단점 | 비용 영향 |
|------|------|------|----------|
| CDN + 캐싱 | 정적 콘텐츠 효과적 | 캐시 무효화 복잡 | CDN 비용 추가 |
| Read Replica | DB 읽기 부하 분산 | 쓰기 반영 지연 | DB 인스턴스 추가 |
| 비동기 처리 (큐) | 피크 부하 흡수 | 응답 지연 가능 | 큐 서비스 비용 |
```

### 기존 DETAIL 모드와의 관계

```
기존 Comprehensive DETAIL:
  - 전체 인터페이스 + 의존성 + 데이터 소유 + 상호작용 다이어그램

확장 (NFR Design):
  - NFR 카테고리별 패턴 옵션 테이블 (Comprehensive DETAIL에서만)
```

Standard DETAIL과 Minimal에는 영향 없음.

---

## Section 5: Orchestrator 변경

### 5.1 INCEPTION 흐름 변경

```
workspace-detection → [Complexity Gate] → requirements-analysis → [Open Questions Gate]
  → [Pre-Planning Gate] → (user-stories) → (nfr-requirements)
  → workflow-planning → [Approach Proposal Gate]
  → (application-design + NFR Design) → 완료
```

### 5.2 Pre-Planning Gate (신규) [조건부 게이트]

requirements-analysis 게이트 통과 후, workflow-planning 호출 **전에** 실행.
Pre-Planning은 INCEPTION 내 스테이지 그룹명이며, workflow-plan.md의 `### PRE-PLANNING` 섹션에 결과가 기록된다.

**Minimal complexity**: 자동 스킵 (user-stories, nfr-requirements 모두 건너뜀)

**Comprehensive complexity**: 자동 포함 (user-stories, nfr-requirements 모두 실행)

**Standard complexity**: 3-option 게이트 제시

```
요구사항 분석이 완료되었습니다. 다음 단계 전에 추가 분석이 가능합니다:

A) User Stories + NFR 수집 → 두 스테이지 모두 실행
B) NFR 수집만 → nfr-requirements만 실행 (상용 배포 시 권장)
C) 바로 워크플로우 계획으로 → 추가 분석 스킵
```

### 5.3 User-Stories 게이트 [표준 게이트 + Hold]

```
[user-stories 결과 표시]
A) 변경 요청 → user-stories 재호출
B) 승인, 다음 단계 진행
H) 보류 (나중에 돌아옴) → HELD 상태 저장, 다음으로 진행
```

### 5.4 NFR-Requirements 게이트 [모드 선택 + 표준 게이트 + Hold]

**모드 선택 (오케스트레이터 소유)**:
```
NFR 요구사항을 어떻게 진행하시겠습니까?

A) Claude가 질문하며 수집 (GENERATE)
B) 이미 작성된 NFR 문서가 있음 (IMPORT)
S) 이 단계 건너뛰기 (SKIP)
```

선택에 따라 nfr-requirements 호출 시 인라인 신호 전달:
- A → `"Mode: GENERATE"`
- B → `"Mode: IMPORT"`

**결과 게이트**:
```
[nfr-requirements 결과 표시]
A) 변경 요청 → nfr-requirements 재호출
B) 승인, 다음 단계 진행
H) 보류 (나중에 돌아옴) → HELD 상태 저장, 다음으로 진행
```

### 5.5 NFR Design 활성화 (게이트 아님, 자동 판단)

application-design DETAIL 호출 시, 3가지 조건을 모두 확인:
1. depth가 Comprehensive
2. DETAIL 모드
3. `devflow-docs/inception/nfr-requirements.md` 존재

모두 충족 시 오케스트레이터가 DETAIL 호출에 인라인 신호 추가:
`"aidlc-application-design: DETAIL — NFR Design 포함"`

하나라도 미충족 시 기존 DETAIL 호출 유지 (NFR Design 없음).

### 5.6 Hold/Skip 처리

오케스트레이터가 HELD/SKIPPED 상태를 감지하면:
1. devflow-state에 상태 기록: `user-stories: HELD` 또는 `nfr-requirements: SKIPPED`
2. devflow-audit에 로깅
3. 다음 스테이지로 진행

---

## Section 6: workflow-planning 변경

### Approved Stages에 Pre-Planning 섹션 추가

```markdown
## Approved Stages
### PRE-PLANNING
- user-stories: [included | skipped | held] — [reason]
- nfr-requirements: [included | skipped | held] — [reason]

### CONSTRUCTION
- application-design: [included | skipped] — [reason]
- units-generation: [included | skipped] — [reason]
- code-generation: included — always
- build-and-test: included — always
```

**오케스트레이터 파싱 변경**: `### PRE-PLANNING` 섹션은 오케스트레이터가 파싱하지 않는다.
Pre-Planning 스테이지는 오케스트레이터가 직접 게이트로 관리하며, workflow-plan.md의 PRE-PLANNING 섹션은 기록용.
기존 `### CONSTRUCTION` 파싱 로직은 변경 없음.

### 접근법 생성 시 NFR 반영

nfr-requirements.md가 존재하면:
- "안전한/완전" 접근법에 `application-design: Comprehensive` 포함 (NFR Design 활성화)
- "빠른/간결" 접근법에서도 NFR 존재 사실 명시

---

## Section 7: 파일 변경 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `skills/_shared/import-review-protocol.md` | **CREATE** | GENERATE/IMPORT 모드 + Hold/Skip 공유 프로토콜 (~50줄) |
| `skills/aidlc-user-stories/SKILL.md` | **CREATE** | 독립 스킬 v0.6.0: 요구사항 → 사용자 스토리 변환 (~100줄) |
| `skills/aidlc-nfr-requirements/SKILL.md` | **CREATE** | 독립 스킬 v0.6.0: 도메인 컨텍스트 + 프로파일 기반 NFR 수집 (~140줄) |
| `skills/aidlc-application-design/SKILL.md` | **MODIFY** | v0.4.0 → v0.6.0, Comprehensive DETAIL에 NFR Design Patterns 섹션 추가 (~40줄 추가) |
| `skills/aidlc-inception-orchestrator/SKILL.md` | **MODIFY** | v0.4.0 → v0.6.0, Pre-Planning Gate + 모드 선택 + hold/skip 처리 (~60줄 추가) |
| `skills/aidlc-workflow-planning/SKILL.md` | **MODIFY** | v0.4.0 → v0.6.0, Approved Stages에 PRE-PLANNING 섹션 + NFR 반영 (~15줄 추가) |
| `skills/_shared/devflow-conventions.md` | **MODIFY** | v0.2.0 → v0.3.0, import-review-protocol 참조 + Hold/Skip 규약 추가 |
| `skills/_shared/gate-patterns.md` | **MODIFY** | Hold 게이트 변형 + 모드 선택 게이트 패턴 추가 |
| `.claude-plugin/plugin.json` | **MODIFY** | v0.5.0 → v0.6.0 |

---

## Architecture Decision Records

### ADR-1: nfr-design을 독립 스킬이 아닌 application-design 확장으로

**결정**: NFR 설계 패턴을 application-design Comprehensive DETAIL 내부에 통합
**이유**: 컴포넌트 설계와 NFR 패턴 결정은 같은 맥락에서 이루어짐. 분리 시 동일 컨텍스트를 두 번 로드하게 됨.

### ADR-2: user-stories/nfr-requirements를 workflow-planning 이전(Pre-Planning)에 배치

**결정**: requirements-analysis → (user-stories) → (nfr-requirements) → workflow-planning
**이유**: NFR 요구사항이 workflow-planning의 접근법 선택에 영향 ("높은 가용성 요구" → "Comprehensive 깊이"). 설계의 입력이지 결과가 아님.

### ADR-3: infrastructure-design을 별도 설계 사이클로 분리

**결정**: 이번 구현에서 제외, 추후 별도 설계
**이유**: application-design 이후에 필요 + 클라우드/온프렘/비용 등 완전히 다른 질문 영역. 3개 스킬 + 1개 확장만으로도 충분한 가치 제공.

### ADR-4: NFR Design에서 "권장" 대신 "옵션 테이블" 사용

**결정**: Claude는 각 패턴의 장단점+비용을 병렬 제시하되, 특정 패턴을 권장하지 않음
**이유**: NFR 설계에는 정답이 없고 트레이드오프만 존재. 비개발자에게 "권장"이라고 하면 맹목적 수용 위험. 정보 정리자 역할이 적절.

### ADR-5: 도메인 컨텍스트를 프로파일 선택 이전에 수집

**결정**: nfr-requirements에서 도메인 질문 → 프로파일 질문 순서
**이유**: 같은 "소규모 운영"이라도 금융과 사내 도구의 NFR 기본값이 완전히 다름. 도메인 없이 프로파일만으로는 거짓 확신을 줄 수 있음.
