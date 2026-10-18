# aidlc v2 Conventions

v1 `devflow-conventions.md`(352줄) + `gate-patterns.md`(112줄)에서 규약만 남긴 것.
설득·리캡·합리화 방지 문구는 뺐다 — 강제가 필요한 것은 훅이 한다.

## 우선순위

1. 사용자 지시 (CLAUDE.md, 직접 요청)
2. 스킬 규칙 (SKILL.md, `_shared/`)
3. 기본 동작

사용자 지시가 스킬 규칙과 충돌하면 사용자 지시를 따른다.

## 스킬 7개와 역할

| 스킬 | 역할 | 호출 |
|------|------|------|
| `devflow` | 진입. Size the Work + 라우팅 | 자동 (개발 요청 감지) |
| `requirements` | workspace 판정 + 요구·NFR (프로젝트 크기만) | devflow |
| `design` | 설계 문서 + builder check 1회 | devflow, 프로젝트 크기만 |
| `plan-build` | 계획(Review Focus 포함) → 태스크별 구현·리뷰 → ledger | devflow |
| `review` | 브랜치 리뷰 1회(최강 모델) + Codex 교차 리뷰 1회 | plan-build 끝 |
| `handoff` | ledger + session-summary 읽기/쓰기 | 세션 시작·종료, 스킬 경계 |
| `brownfield` | 기존 코드베이스 3축 탐색 | requirements, 기존 코드 있을 때 |
| `discipline` (제안형) | TDD + 완료 전 검증 요령 | 코드를 쓰는 모든 스킬이 참조 |

## Size the Work

이해가 끝나면 크기 하나를 정해 소리 내어 말한다. 사용자가 override한다.

| 크기 | 전체 서술 | 그 다음 |
|------|----------|---------|
| 빠른 작업 | 요청 자체 | 바로 한다 |
| 작은 변경 | 대화에서 합의 | plan-build (계획은 짧게) |
| 프로젝트 | 설계 문서 | requirements → design → plan-build |

커지면 멈추고 말한 뒤 한 단계 올린다. 독립 프로젝트 여럿이면 순서를 정해 하나씩.

## 사람 게이트는 두 곳

1. **설계 승인** — 작은 변경은 대화에서, 프로젝트는 설계 문서로. 승인 전엔 제품 코드·스캐폴딩·의존성 설치·구현 스킬 호출을 하지 않는다. 읽고 탐색하는 건 된다.
2. **finishing** — 머지·PR·push·폐기 중 하나를 사용자가 고른다.

그 외는 멈추지 않는다 (Rulings, not stalls):

- 모호함·계획 결함·한도 초과는 `Ruling: 결정 — 이유 — 틀리면 비용`으로 ledger에 적고 계속한다. spec이 권위, 계획은 그 논증, 둘이 답하지 않으면 판단한다.
- 멈추는 건 4가지뿐: 되돌릴 수 없는·파괴적 작업, 보안 민감 작업, worktree 밖 부작용(머지·공유 브랜치 push·배포), 모든 길이 추측인 계획.

## 산출물

```
devflow-docs/
├── inception/{requirements,design}.md     # 프로젝트 크기만
├── plans/YYYY-MM-DD-<topic>.md            # plan-build 계획 (Global Constraints + Review Focus)
├── session-summary.md                     # handoff (가설)
└── audit.md                               # append-only, 훅이 기록
.devflow/sdd/<plan>/                       # git-ignored: progress.md(ledger), 브리프, 보고서, diff 패키지
```

- 사람이 읽거나 승인할 파일은 Markdown. AI만 읽는 중간 상태는 JSON/JSONL.
- 상태의 truth는 `git log` + ledger. session-summary는 가설이고 검증 대상이다.

## 서브에이전트

- 세션 히스토리를 넘기지 않는다. 브리프 파일(`task-brief`), diff 패키지(`review-package`), 프로젝트 루트 절대 경로, 산출물 형식만.
- 디스패치마다 모델을 명시한다. 기계적 구현(명세 명확, 1~2 파일)은 저가, 통합·디버깅은 표준, 설계와 브랜치 리뷰는 최강.
- 구현자·리뷰어는 서브에이전트를 띄우지 않는다.
- 구현자 보고서는 주장이다. 리뷰어가 코드로 검증한다.

## 리뷰

- 태스크마다 1회 (spec + quality, `prompts/review-prompt.md` Part 1~2), 브랜치 끝 1회 (Part 1~4, 최강 모델), Codex 교차 리뷰 1회 (같은 패키지).
- 수정-재리뷰 최대 3회. 넘으면 사람에게.
- Review Focus: 계획에 "spec이 암시하지만 테스트가 없는 실패 모드" ≤5개를 적고 각각 테스트에 핀한다. 리뷰어는 그 테스트가 있는지 본다.

## 메타데이터 (SKILL.md frontmatter)

| 필드 | 값 |
|------|----|
| `name`, `description` | Claude Code 표준. description은 트리거 조건을 한국어·영어 키워드로 |
| `user-invocable` | `devflow`, `brownfield`, `review`, `handoff`는 true. 나머지는 false (devflow가 부른다) |
| `model` | `review`만 최강 모델 지정. 나머지는 세션 모델 |

## 새 스킬 추가

추가 전에 묻는다: Jay의 실제 페인포인트인가, 아니면 Claude가 짠 이상적 답인가. 후자면 추가하지 않는다 (CLAUDE.md 과잉설계 가드 1번).
