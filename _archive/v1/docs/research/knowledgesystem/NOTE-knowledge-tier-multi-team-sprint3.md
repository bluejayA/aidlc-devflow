# Knowledge Tier: 다중 팀/다중 repo 운영 모델 — Sprint 3+ 설계 노트

> 작성: 2026-04-11  
> 상태: 미검증 설계 노트. Sprint 1-2 운영 경험 이후 재검토 필요.  
> 주의: 이 문서는 Sprint 3 설계 시 참고 자료이지, 확정된 스펙이 아니다.

---

## 핵심 전제

- 서로 다른 팀이 서로 다른 로컬 머신에서 서로 다른 GitHub repo로 작업한다
- `~/.devflow/` 로컬 경로 모델은 개인 실험에만 유효. 팀 환경에서는 동기화 안 됨
- shared/org knowledge는 "공유되어야 의미가 있는 지식"이므로 중앙 authoritative source 필요

---

## 물리적 구현: 별도 git repo

```
github.com/ktcloud/
├── next-control-plane/        ← Team A repo (.devflow/ = project-local)
├── gpu-scheduler/             ← Team B repo (.devflow/ = project-local)
├── cloud-portal/              ← Team C repo (.devflow/ = project-local)
└── devflow-knowledge/         ← 중앙 공용 repo
    ├── shared/
    │   ├── patterns/
    │   ├── concepts/
    │   └── templates/
    ├── org/
    │   ├── architecture-principles/
    │   └── playbooks/
    ├── schema/
    └── promotion-log/
```

shared와 org는 개념적으로 구분하되, 초기에는 하나의 repo 안에서 디렉토리로 분리.

---

## 프로젝트에서 소비하는 방식 (후보)

1. **git submodule/subtree**: 프로젝트 repo 안에 `.devflow/upstream/`으로 마운트
2. **devflow-box base image**: Lima VM 빌드 시 devflow-knowledge를 `~/.devflow/`에 clone
3. **CLAUDE.md/SCHEMA.md에서 링크 참조**: "이 프로젝트는 shared pattern X를 따른다"

→ Sprint 1-2 운영 경험 후 어떤 방식이 실제로 쓰이는지 보고 결정.

---

## 거버넌스 모델 (후보)

| 모델 | 설명 | 장점 | 단점 |
|------|------|------|------|
| 중앙 관리 | 플랫폼/아키텍처 팀이 관리, PR 승인 | 품질·일관성 | 병목 |
| **Federated (추천)** | 각 팀이 PR 가능, 도메인 대표 + 플랫폼 담당 리뷰 | 속도 + 품질 균형 | 리뷰어 지정 필요 |
| 완전 분산 | 각 팀 자율 | 빠름 | 품질 오염 |

---

## 승격 프로세스

1. 프로젝트 ADR에 `promotion_candidate: true` 플래그
2. lint/review가 승격 후보 목록 표시
3. 사람이 "shared로 올릴 가치 있다" 판단
4. 중앙 knowledge repo에 PR — **일반화된 형태로 재작성** (원본 복사 아님)
5. 리뷰 승인 후 반영
6. 이후 다른 프로젝트가 참조

### 승격 시 재작성 예시

- Project A ADR: "next-control-plane에서 exponential backoff 채택"
- Project B ADR: "gpu-scheduler에서 retry queue backoff 채택"
- → Shared pattern: "distributed control loop에서 retry/backoff standard pattern"

> shared/org는 단순 aggregation이 아니라 **curation**이다.

---

## shared pattern 파일 형태 (예시)

```yaml
# devflow-knowledge/shared/patterns/retry-backoff-pattern.md
---
type: pattern
confidence: confirmed
promoted_from:
  - project: next-control-plane
    adr: ADR-004
  - project: gpu-scheduler
    adr: ADR-008
promoted_at: 2026-05-15
promoted_by: jay
---
```

---

## 소비 경로 (하향 주입)

1. CLAUDE.md/SCHEMA.md에서 중앙 repo의 관련 pattern 링크
2. pre-session에서 관련 shared pattern만 선택적으로 표시
3. ADR 작성 시 "기존 shared pattern을 따르는가, 예외인가?" 체크

> 저장보다 소비가 더 중요. 중앙 repo가 있어도 아무도 안 읽으면 끝.

---

## 이 문서의 사용법

Sprint 3 설계를 시작할 때:
1. 이 문서를 읽는다
2. Sprint 1-2 운영에서 실제로 어떤 지식이 프로젝트를 넘었는지 확인한다
3. 이 문서의 가정이 맞는지 재검증한다
4. 맞으면 SPEC으로 구체화, 틀리면 폐기한다
