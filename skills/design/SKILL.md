---
name: design
description: 프로젝트 크기 작업의 설계 문서 작성 + builder check 1회 + 설계 승인 게이트. requirements 다음에 devflow가 호출한다. 결과는 devflow-docs/inception/design.md.
user-invocable: false
---

# design

**입력**: `devflow-docs/inception/requirements.md`. **산출물**: `devflow-docs/inception/design.md`. 승인되면 `plan-build`.

## 1. 설계 문서

그 분야의 유능한 빌더가 사용자에게 다시 묻지 않고 계획을 세울 수 있는 평문 문서. 넓게 생각하되(대안 여러 개를 속으로 비교) 보여 주는 건 결정에 도움될 때만.

```markdown
# Design — <topic>
**As of** <date> · **Requirements** devflow-docs/inception/requirements.md

## 의도와 이유                  # requirements에서 한 단락
## 목표 / 비목표 / 반목표
## 제약                         # 기술 스택, 기존 패턴, NFR 중 설계를 좌우하는 것
## 구조                         # 컴포넌트와 책임, 경계, 데이터 흐름. 그림이 나으면 ASCII
## 사용자가 정한 것 / 내가 정한 것   # 구분해서. 내 결정은 한 줄 이유
## 빌더에게 맡기는 것
## Review Focus 후보            # spec이 암시하지만 테스트가 없을 실패 모드 (plan-build가 ≤5개로 확정)
```

- 요구에 없는 구성 요소를 넣지 않는다. 숫자·경로·라이브러리는 requirements나 코드베이스에 있는 것만.
- 독립 하위 시스템이 여럿이면 하위 프로젝트로 나누고 순서를 정한다. 하나씩.

## 2. Builder check (1회)

사용자에게 "리뷰어가 먼저 읽고, 질문 몇 개를 한 번 가져올 수 있다"고 말한 뒤, 신선한 general-purpose 서브에이전트에 `${CLAUDE_PLUGIN_ROOT}/_shared/prompts/builder-check-prompt.md`를 채워 보낸다. 모델은 세션 모델.

돌아온 질문을 세 더미로:

- **이미 답 있음** (대화·프로젝트에) → 문서에 답을 적는다
- **사소함** (빌더가 정해도 결과가 안 바뀜) → 내가 정하고 "내가 정한 것"에 적는다
- **사용자 것** (답이 무엇을 만들지 바꿈) → 한 메시지로, 중요한 것부터

사용자 답을 문서에 반영한다. 이 라운드가 유일한 질문 라운드다. 서브에이전트 도구가 없으면 내가 그 빌더로서 읽는다.

## 3. 설계 승인 — 첫 번째 사람 게이트

문서 경로와 "내가 정한 것" 목록을 보여 주고 승인을 받는다. 승인 전에는 제품 코드·스캐폴딩·의존성 설치·`plan-build` 호출을 하지 않는다. 변경 요청이 오면 반영하고 다시 보여 준다 — 재리뷰 루프는 없다.

승인되면 `handoff`로 session-summary를 갱신하고("폐기한 접근이 있나요?" 1회), `plan-build`로 넘긴다.
