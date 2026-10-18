---
name: brownfield
description: 처음 보는 기존 코드베이스를 3축(활동 핫스팟·기존 문서·핵심 파일 샘플)으로 빠르게 파악한다. 기존 프로젝트에서 작업이 시작될 때 devflow/requirements가 호출하고, "이 코드베이스 파악해줘", "구조 봐줘", explore this repo로 직접 부를 수도 있다.
user-invocable: true
---

# brownfield

프로토콜 전문은 `${CLAUDE_PLUGIN_ROOT}/_shared/brownfield.md`. 요지:

1. `devflow-docs/inception/`에 이전 분석이 있으면 그것 + `git log`로 이후 변경만 본다. 끝.
2. 없으면 3축:
   - **핫스팟**: `git log --oneline -20`, 최근 많이 바뀐 디렉터리
   - **문서**: README, CLAUDE.md/AGENTS.md, docs/, ADR — 있는지와 핵심 한 줄
   - **샘플**: 진입점 1~2개(없으면 `src/`의 가장 작은 파일), 200줄 이하 전체·초과 시 100줄. 네이밍·import·에러 처리·주석·구조 패턴을 뽑는다
   - 그리고 의존성(패키지 파일), 테스트 프레임워크·실행법, 변경 영향 범위
3. 전체 코드베이스를 읽지 않는다. 기존 패턴이 있으면 따른다 — 새 패턴은 설계 승인 사항이다.

## 출력

호출한 스킬(requirements)이 쓸 수 있게 두 섹션으로 보고하고, 프로젝트 크기면 `devflow-docs/inception/requirements.md`의 같은 이름 섹션에 넣는다:

```markdown
## Workspace
스택 · 구조 · 진입점 · 테스트 실행법 · 핫스팟 · 기존 문서 · 영향 범위
## Coding Patterns (Sampled)
네이밍 · import · 에러 처리 · 주석 · 구조 — 각 한 줄, 근거 파일
```
