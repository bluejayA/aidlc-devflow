---
name: aidlc-nfr-requirements
description: Use when non-functional requirements need to be defined based on domain context and project profile, or when importing existing NFR documents.
metadata:
  version: 0.6.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
  output_path: devflow-docs/inception/nfr-requirements.md
---

# aidlc-nfr-requirements

<!-- 비기능 요구사항 수집: 도메인 + 프로파일 기반 체계적 NFR 수집 -->
<!-- IMPORT 모드: _shared/import-review-protocol.md 참조 -->

## Purpose

비개발자가 "이 소프트웨어에 어떤 품질 요구사항이 필요한가"를 체계적으로 수집한다.
NFR 값을 **결정**하는 것이 아니라 **수집**하는 것.

## Execution Modes

### GENERATE Mode (기본)
호출 텍스트에 `Mode: GENERATE` 또는 모드 지정이 없으면 GENERATE.
Step 1부터 순서대로 실행.

### IMPORT Mode
호출 텍스트에 `Mode: IMPORT` 포함 시 활성화.
`_shared/import-review-protocol.md`의 IMPORT 프로세스를 따른다.

IMPORT 모드 검증 항목:
- 8개 NFR 카테고리 중 누락 여부
- 수치 없는 정성적 표현 ("빨라야 한다" → 구체적 수치 요청)
- 카테고리 간 모순 (예: "최저 비용" + "99.99% 가용성")

검증 후 `devflow-docs/inception/nfr-requirements.md`에 저장하고 Return to Orchestrator.

## Execute (GENERATE Mode)

### Step 1: Load context

Read (if they exist):
- `devflow-docs/inception/requirements.md` — 기능/비기능 요구사항
- `devflow-docs/inception/user-stories.md` — 사용자 스토리 (있으면)

### Step 2: Domain context 질문

```
이 소프트웨어의 도메인은?

A) 금융/핀테크 — 높은 보안+컴플라이언스, 감사 추적 필수
B) 헬스케어 — 데이터 프라이버시(HIPAA 등), 높은 가용성
C) 이커머스 — 트래픽 변동 대응, 결제 보안
D) 사내 도구 — 낮은 가용성 허용, 보안 내부망 기준
E) IoT/임베디드 — 저전력, 네트워크 불안정 고려
F) 기타 (직접 입력)
```

선택된 도메인을 Step 4의 기본값 조정에 사용한다.

### Step 3: Profile 선택

```
이 소프트웨어의 운영 환경은?

A) MVP/프로토타입 — 기본값으로 충분, NFR 최소화
B) 소규모 운영 — 사용자 100명 이하, 기본 안정성
C) 중규모 운영 — 사용자 1000명+, 모니터링 필요
D) 대규모/엔터프라이즈 — 고가용성, 보안 컴플라이언스
```

### Step 4: Profile 기반 맞춤 질문

도메인 × 프로파일 조합에 따라 질문 범위를 결정:

| 프로파일 | 질문 수 | 대상 카테고리 |
|---------|--------|--------------|
| MVP | 2~3개 | 핵심 보안, 데이터 백업 |
| 소규모 | 4~5개 | + 응답 시간, 동시 접속 |
| 중규모 | 6~7개 | + 모니터링, 장애 복구 |
| 대규모 | 8개 전체 | 전체 카테고리 순회 |

**8개 NFR 카테고리:**
1. 성능 (응답 시간, 처리량)
2. 가용성 (업타임, 장애 허용)
3. 확장성 (수평/수직 확장)
4. 보안 (인증, 암호화, 접근 제어)
5. 데이터 무결성 (백업, 일관성)
6. 모니터링 (로깅, 알림, 대시보드)
7. 재해 복구 (RPO, RTO)
8. 컴플라이언스 (규제, 감사)

각 질문은 one at a time. 비개발자 친화 표현 사용.

### Step 5: Domain × Profile 기본값 제시 + 조정

프로파일과 도메인을 조합하여 기본값을 제시한다:

```
프로파일 기반으로 다음 NFR을 제안합니다:
- 응답 시간: [값] (이유: [도메인] 기준 [근거])
- 가용성: [값] (이유: [프로파일] 기준 [근거])
- ...

조정이 필요한 항목이 있나요?
```

**도메인별 기본값 조정 예시:**
- 금융 + 소규모: 가용성 99.95% (금융은 기본보다 높음)
- 사내 도구 + 중규모: 가용성 99.5% (내부 사용이므로 낮춤)
- 헬스케어 + MVP: 보안 등급 상향 (HIPAA 필수)
- IoT + 대규모: 네트워크 지연 허용 상향

사용자가 조정한 항목은 `## 조정 이력`에 기록.

### Step 6: Save artifact

Create `devflow-docs/inception/nfr-requirements.md`:

```markdown
# NFR Requirements

**Timestamp**: [ISO 8601]
**Mode**: [GENERATE | IMPORT]
**Domain**: [선택된 도메인]
**Profile**: [선택된 프로파일]

## NFR Summary

| 카테고리 | 요구사항 | 근거 |
|---------|---------|------|
| 성능 | [값] | [도메인+프로파일 기준 근거] |
| 가용성 | [값] | [근거] |
| ... | ... | ... |

## 조정 이력
- [항목]: [원래 기본값] → [사용자 조정값] (이유: [사용자 설명])
```

## Review

conventions Review Workflow 적용.
- 산출물: devflow-docs/inception/nfr-requirements.md
- 리뷰어: artifact-reviewer-prompt.md

## Return to Orchestrator

conventions 표준 형식. 반환 필드:
- 모드: [GENERATE | IMPORT]
- 도메인: [선택된 도메인]
- 프로파일: [선택된 프로파일]
- NFR 항목: [count]개 카테고리
- 사용자 조정: [count]개 항목
- 산출물: devflow-docs/inception/nfr-requirements.md
- 리뷰: [✅ 승인됨 | ⏭ 스킵 (Minimal)]

## Common Issues

### 사용자가 도메인을 모르거나 "기타" 선택 시
- 요구사항에서 도메인 특성을 추론
- 추론 근거를 사용자에게 제시: "결제 기능이 있으므로 이커머스 기준을 적용하겠습니다. 맞나요?"
- 확인 후 진행

### 프로파일 선택이 모호한 경우
- "현재 사용자가 몇 명인가요?" 추가 질문으로 범위 확인
- 확실하지 않으면 한 단계 높은 프로파일 적용 (안전 방향)
