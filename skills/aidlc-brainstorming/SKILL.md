---
name: aidlc-brainstorming
description: 아이디어를 설계로 전환하는 협업 대화 스킬. HARD-GATE — 설계 승인 전 코드 작성 금지.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: user-invocable
---

# Brainstorming

아이디어를 설계 문서로 전환한다.

> **HARD-GATE**: `_shared/devflow-conventions.md` Brainstorming HARD-GATE 참조. 설계 승인 전 코드 작성 금지.

**시작 시 선언**: "aidlc-brainstorming 스킬을 사용하여 설계를 진행합니다."

## 프로세스

### Step 1: 프로젝트 컨텍스트 탐색

- 파일, 문서, 최근 커밋 확인
- 브라운필드인 경우: `_shared/patterns/brownfield-exploration.md` 참조
- 범위 판단: 여러 독립 서브시스템이면 먼저 분해 제안

### Step 2: 명확화 질문

- **한 번에 하나만** 질문
- 객관식 선호 (가능한 경우)
- 각 답변에 **Ambiguity Resolution Loop** 적용 (아래 참조)

### Step 3: 복잡도 선언 + 접근법 제안

**복잡도 선언** (접근법 제안 전 필수):

```
이 작업의 복잡도를 **[Minimal/Standard/Comprehensive]**로 판단했습니다.
이유: [한 줄]

다르게 조정하시겠습니까?
```

| 단계 | 기준 | 설계 분량 | 접근법 |
|------|------|-----------|--------|
| Minimal | 단일 파일/함수, 명확한 경로 | 2-5문장 | 1-2개 |
| Standard | 새 컴포넌트, 복수 고려사항 | 표준 섹션 | 2-3개 |
| Comprehensive | 시스템 설계, 아키텍처 결정 | 전체 섹션 + 다이어그램 | 2-3개 |

사용자 승인 후 2-3개 접근법 제안. 추천안 + 이유 먼저 제시.

### Step 4: 설계 제시

- 섹션별 제시, 각 섹션 승인 후 다음
- 섹션: architecture, components, data flow, error handling, testing
- 각 섹션 분량은 복잡도에 비례

**설계 원칙**:
- 단일 책임 단위로 분해
- 잘 정의된 인터페이스로 소통
- 독립적으로 이해/테스트 가능
- YAGNI — 불필요한 기능 제거

### Step 5: 설계 문서 작성

- 저장 경로: `docs/plans/YYYY-MM-DD-<topic>-design.md`
- 가정이 있으면 `## Assumptions` 섹션 포함
- 문서 상단에 `**Complexity:** [Minimal|Standard|Comprehensive]` 기록
- 커밋

### Step 6: Spec Review + 사용자 리뷰 + 전환

**Spec Review Loop** (conventions 리뷰 루프 규약 참조):

1. **Minimal depth**: 리뷰 스킵, 바로 사용자 리뷰 게이트로
2. **Standard/Comprehensive depth**:
   - `_shared/reviewers/spec-document-reviewer-prompt.md`를 서브에이전트로 dispatch
   - ❌ Issues Found → 수정 후 re-dispatch (최대 5회)
   - Recommendations만 → 루프 종료 (수정 권장)
   - 5회 초과 → 사용자 escalate

**사용자 리뷰 게이트** (리뷰 통과 후):
> "Spec이 `<경로>`에 저장되었습니다. 리뷰 후 변경사항이 있으면 알려주세요."

사용자 승인 후 `aidlc-writing-plans` 스킬로 전환

---

## Ambiguity Resolution Loop

명확화 질문의 답변을 받을 때마다 적용.

### 모호성 신호

- "depends", "maybe", "not sure", "~하거나", "~일 수도", "상황에 따라"
- 키워드 없어도 설계 결정에 불충분하면 모호한 것으로 간주

### 후속 질문 방향

| 유형 | 예시 답변 | 후속 질문 |
|------|-----------|-----------|
| 선택 모호 | "A나 B나 괜찮아요" | "어떤 기준으로 A를, 어떤 기준으로 B를?" |
| 범위 모호 | "적당히 빠르면 됩니다" | "구체적으로 어느 정도? (예: 1초 이내)" |
| 우선순위 모호 | "성능도 비용도 중요" | "둘이 상충할 때 어느 쪽 우선?" |

### 탈출 조건

1. 모든 모호함 해소 → 다음 단계
2. 사용자가 "그냥 진행해" → 가정 목록 정리 → 승인 대기 → Assumptions에 기록

---

## 핵심 원칙

- 한 번에 하나만 질문
- 객관식 선호
- YAGNI 엄격 적용
- 2-3개 대안 제시 후 선택
- 섹션별 점진적 검증
