---
name: requirements
description: 프로젝트 크기 작업의 요구사항·비기능요구(NFR) 정리. devflow가 "프로젝트"로 판정했을 때만 호출한다. 결과는 devflow-docs/inception/requirements.md.
user-invocable: false
---

# requirements

**산출물**: `devflow-docs/inception/requirements.md`. 다음 스킬은 `design`.

## 1. Workspace

- 기존 코드가 있으면 `brownfield` 결과(`## Workspace`, `## Coding Patterns (Sampled)`)를 이 문서에 넣는다. 없으면 greenfield라고 적고 끝.
- 기술 스택: 기존 코드의 것을 따른다. 없으면 사용자에게 선택권이 있는지 묻고, 맡기면 기본값을 고르고 **내 결정이라고 표시**한다.

## 2. 요구 — 대화로, 한 번에 질문 하나

질문은 구체적 순간을 묻는 열린 질문이 먼저다. 선택지는 사용자가 막혔을 때만. 다룰 영역(질문으로 읽어 주지 않는다):

- 무엇이고 무엇이 특별한가 · 왜 지금, 성공은 어떤 모습인가
- 목표 / 비목표 / 반목표(되더라도 실패인 것)
- 본 적 있는 것(좋았던·싫었던) · 지금 있는 것·시도한 것
- 사용자가 신경 쓰는 디테일

한 부분을 이해할 때마다 200~300자로 되돌려 말하고(추측은 추측이라고 표시) 틀린 데·빠진 데를 묻는다. 해석이 여러 갈래면 선택지를 보여 주고 확정한다.

## 3. NFR — 도메인 프리셋에서 시작

`${CLAUDE_PLUGIN_ROOT}/_shared/reference/nfr-presets.md`에서 도메인에 맞는 프리셋을 고르고, `reference/domain-cards.md`의 카드가 있으면 그 질문만 던진다. 프리셋을 "이대로 쓸까요? (Y/n)"로 확인하고, 바꾼 것만 적는다. 성능 수치·가용성 목표는 사용자가 말한 것만 적는다 — 지어내지 않는다.

## 4. 문서

```markdown
# Requirements — <topic>
**As of** <date> · **Size** 프로젝트

## Workspace            # brownfield 결과 또는 "greenfield"
## 의도와 이유
## 목표 / 비목표 / 반목표
## 기능 요구            # 번호 매김. 해석 확정 사항은 "확정:"으로
## NFR                  # 프리셋 이름 + 바꾼 것만
## 내가 정한 것          # 사용자가 맡긴 선택. 각각 한 줄 이유
## 열린 질문            # 있으면
```

## 끝

문서 경로를 보고하고 `design`으로 넘긴다. 승인 게이트는 여기 없다 — 설계 문서에서 한 번 받는다.
