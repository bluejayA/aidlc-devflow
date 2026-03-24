# Review Team Protocol — Agent Teams 협업 리뷰

> requesting-code-review R3 모드에서 참조하는 프로토콜.
> 리뷰어들이 Agent Teams로 협업하여 코드 리뷰를 수행하는 절차를 정의한다.

## 팀 생성

TeamCreate로 리뷰 팀을 생성한다:

```
TeamCreate:
  team_name: "code-review-{unit-name}"
  description: "Code review for {unit-name}"
```

## 리뷰어 Spawn

depth에 따라 리뷰어를 Agent(Explore 타입)로 spawn한다.
Explore 타입은 Read-only — 코드를 읽고 분석만 수행하며, 수정은 팀 리드가 담당한다.

### Standard depth (3인 팀)

| 리뷰어 | 에이전트 정의 | 리뷰 관점 |
|--------|-------------|----------|
| spec-reviewer | `agents/spec-reviewer.md` | Spec compliance (spec 제공 시만) |
| quality-reviewer | `agents/quality-reviewer.md` | Code quality |
| security-reviewer | `agents/security-reviewer.md` | Security/edge-case |

spec 미제공 시 spec-reviewer 스킵 → 2인 팀.

### Comprehensive depth (4인 팀)

Standard + maintainability-reviewer 추가:

| 리뷰어 | 에이전트 정의 | 리뷰 관점 |
|--------|-------------|----------|
| maintainability-reviewer | `agents/maintainability-reviewer.md` | Maintainability/future risk |

### Spawn 방법

각 리뷰어를 Agent tool로 spawn:

```
Agent:
  subagent_type: Explore
  team_name: "code-review-{unit-name}"
  name: "{reviewer-name}"
  prompt: |
    당신은 {reviewer-role}입니다.
    리뷰 대상: {review-target}
    참조 컨텍스트: {context-files}

    {agents/{reviewer-name}.md}의 검토 기준에 따라 리뷰를 수행하세요.
    완료 후 팀 리드에게 결과를 SendMessage로 보고하세요.
    다른 리뷰어의 발견 사항과 관련된 내용이 있으면 해당 리뷰어에게 DM하세요.
```

모든 리뷰어를 **동시에 spawn** (병렬 실행).

## 소통 규칙

### 독립 분석 우선 원칙
각 리뷰어는 **자신의 독립 분석을 먼저 완료**한 후에만 다른 리뷰어에게 DM을 보낸다. 다른 리뷰어의 중간 결과에 의해 자신의 초기 판단이 편향되는 것을 방지한다.

### 리뷰어 → 팀 리드
- 리뷰 완료 시 결과를 SendMessage로 보고
- Critical 이슈 발견 시 즉시 알림 (다른 리뷰어 완료 대기 불필요)

### 리뷰어 → 리뷰어 (DM)
- 자신의 발견이 다른 관점에도 영향을 미칠 때 해당 리뷰어에게 DM
- 예: quality-reviewer가 입력 검증 누락 발견 → security-reviewer에게 DM
- 예: spec-reviewer가 기능 누락 발견 → quality-reviewer에게 "이 기능 테스트도 없음" DM
- DM은 선택적 — 관련성이 명확할 때만

### 팀 리드 → 리뷰어
- 추가 분석 요청 시 해당 리뷰어에게 SendMessage
- 모든 리뷰어가 idle 상태이면 결과 종합 시작

### Critical 이슈 fast-path
- security-reviewer가 Critical 이슈를 즉시 보고한 경우, 팀 리드는 해당 이슈를 기록하되 다른 리뷰어 완료를 대기
- 모든 리뷰어 완료 후 일괄 종합 (Critical이 있어도 다른 이슈를 놓치지 않기 위해)

## 결과 종합

팀 리드(메인 에이전트)가 모든 리뷰어의 결과를 수신한 후:

1. **중복 제거**: 여러 리뷰어가 같은 이슈를 보고한 경우 하나로 병합
   - 동일 file:line + 동일 설명 → 병합
   - 동일 file:line + 다른 관점 → Cross-cutting으로 분류
   - 다른 파일 + 동일 근본 원인 → "Related to: ..." 표기로 연결
2. **크로스 커팅 이슈 강조**: 여러 리뷰어의 관점이 교차하는 이슈를 별도 섹션으로
   - 크로스 커팅 기준: 복수 리뷰어가 동일 코드 위치를 다른 맥락에서 지적하거나, 한 관점(예: spec)의 이슈가 다른 관점(예: security)에도 영향을 미치는 경우
3. **이슈 분류 통합**: Critical > Important > Minor 순으로 정렬
4. **최종 판정**: 모든 리뷰어의 Assessment를 종합하여 최종 판정

### 종합 결과 형식

```
## Agent Teams Code Review 결과

### 팀 구성
- [참여한 리뷰어 목록]

### 종합 판정
**Assessment:** Ready to merge | Needs fixes
**Critical Issues:** [N]건
**Important Issues:** [N]건
**Minor Issues:** [N]건

### Cross-cutting Issues
[리뷰어 간 소통에서 도출된 교차 관심사]

### Issues by Reviewer
#### Spec Compliance
[spec-reviewer 결과]

#### Code Quality
[quality-reviewer 결과]

#### Security/Edge-case
[security-reviewer 결과]

#### Maintainability (Comprehensive만)
[maintainability-reviewer 결과]

### Recommendations
[수정 권장 사항]
```

## 팀 정리

결과 종합 완료 후:

1. 각 리뷰어에게 shutdown 요청: `SendMessage: {type: "shutdown_request"}`
2. 모든 리뷰어 shutdown 확인
3. `TeamDelete`로 팀 제거

## Graceful Degradation

Agent Teams 도구(TeamCreate/SendMessage)를 사용할 수 없는 환경에서는:
- R3 선택 시 "Agent Teams를 사용할 수 없습니다. R1 (독립 서브에이전트)으로 전환합니다." 안내
- 기존 R1 모드로 자동 fallback
