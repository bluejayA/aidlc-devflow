---
name: devflow
description: 소프트웨어를 만들거나 바꾸는 요청의 진입점. "만들어줘", "추가해줘", "기능", "구현", "리팩토링", "버그 고쳐줘", build, implement, add feature, refactor, fix 같은 요청이 오면 먼저 쓴다. 작업 크기를 정하고 requirements / design / plan-build로 보낸다. 질문·설명·탐색만 하는 요청에는 쓰지 않는다.
user-invocable: true
---

# devflow — 진입과 라우팅

규약은 `${CLAUDE_PLUGIN_ROOT}/_shared/conventions.md`. 이 스킬은 두 가지만 한다: 작업 크기를 정하고, 맞는 스킬로 보낸다.

## 0. 재개인지 확인

`devflow-docs/session-summary.md`가 있으면 `handoff` 스킬의 재개 프로토콜을 먼저 실행한다 (주장을 git과 대조 → Open Work 재해석 → Traps 존중). 그 결과에서 이어 간다. 없으면 1로.

## 1. 알고 있는 것 확인

답하기 전에 자문한다: 무엇을 원하는지, 왜 원하는지 알고 있는가.

- 요청에 중요한 것이 다 들어 있다 ("아이콘을 파란색으로") → 빠른 작업. 하고, 한 줄로 보고한다.
- 사소하지 않은 것이 비어 있다 → 질문 하나로 시작한다. 선택지 목록 없이, 구체적인 순간을 묻는다 ("이게 있었으면 하고 바란 순간이 언제였나요?"). 첫 메시지에 "질문 건너뛰고 바로 시작해도 된다"는 한 줄을 넣는다.

기존 코드가 있고 처음 보는 코드베이스면 `brownfield`를 먼저 돌린다.

## 2. Size the Work

이해가 되면 크기 하나를 정해 소리 내어 말한다. 사용자가 바꿀 수 있다.

| 크기 | 전체 서술 | 다음 |
|------|----------|------|
| 빠른 작업 | 요청 자체 | 바로 한다. `discipline` 요령은 따른다 |
| 작은 변경 | 대화에서 합의한 한 단락 | `plan-build` (계획은 태스크 1~3개) |
| 프로젝트 | 설계 문서 | `requirements` → `design` → `plan-build` |

도중에 커지면 멈추고 말한 뒤 한 단계 올린다. 독립 프로젝트 여럿이면 순서를 정해 하나씩.

## 3. 라우팅

```
빠른 작업  → 직접 수행 → 끝
작은 변경  → [대화 합의 = 설계 승인] → plan-build → review → finishing
프로젝트   → requirements → design [설계 문서 승인] → plan-build → review → finishing
```

- **설계 승인**이 첫 번째 사람 게이트다. 승인 전에는 제품 코드·스캐폴딩·의존성 설치·plan-build 호출을 하지 않는다. 읽고 탐색하는 건 된다.
- plan-build 안에서는 멈추지 않는다 (Rulings, not stalls — conventions 참조).
- **finishing**이 두 번째 게이트: 머지 / PR / 브랜치 유지 / 폐기 중 하나를 사용자가 고른다. `gh pr create`는 body 첫 줄에 `Closes #N`.

## 4. 각 경계에서

- 스킬이 끝날 때마다 `handoff`로 session-summary를 갱신한다 (Traps 회수 질문 1회 포함).
- 커밋 메시지는 Conventional Commits. main/master 직접 push는 훅이 막는다.

## 참조

- `${CLAUDE_PLUGIN_ROOT}/_shared/conventions.md` — 스킬 7개, 게이트 2곳, Rulings, 산출물 경로
- `${CLAUDE_PLUGIN_ROOT}/_shared/handoff.md` — 재개 프로토콜
