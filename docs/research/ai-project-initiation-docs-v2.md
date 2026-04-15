# AI 시대 프로젝트 착수 문서 세트 (CTO 요구안 v2)

> **상태**: Draft v2 — 3-persona 리뷰 (실무자/파트타임 리더/CTO) 반영 + Codex 초기 리뷰 반영.
> **작성일**: 2026-04-15
> **v1 → v2 주요 변경**: 역할 태그 / 분기 감사 / CI gate / Doc 2 축소 / Doc 3 default 블록 / Risk Register 흡수 / Tier 룰화 / 작성 시간 현실화 (조건부).
> **구현 의도**: 없음. debate/설계 재료. 조직 배포 결정은 별도.
> **연관 문서**: [`rfdc-next-gen-draft.md`](rfdc-next-gen-draft.md) — 운영 레디니스 관점 (착수 게이트와 분리).

---

## 1. 개요

### 두 가지 동시 기능

1. **CTO 승인 게이트** — 조직 자원 투입 결정
2. **AI Bootstrap Input** — AI에게 프로젝트 맥락 주입, 일관된 방향 유지

### 핵심 원칙

- **가변 tier** (경량/표준/고위험) + 룰 기반 자동 판정
- **Bootstrap Packet 단일 SSOT** + CI gate 강제
- **AI 금지 영역 명시** — 도메인 강자+초보자 조합의 가장 큰 리스크 회피
- **분기 감사 + 이벤트 기반 스캔** — AI 시대 드리프트 대응 (주간 전수 스캔 대신)
- **조직 표준 default 블록 내장** — 조직 AI 표준이 아직 없는 현실 수용

### 역할 태그 범례 (각 항목 옆 표시)

| 태그 | 의미 |
|------|------|
| **[L]** | **리더 필수** — 파트타임 기술 리더가 반드시 검토·승인 |
| **[T]** | **팀 자율** — 실무 엔지니어가 자율 작성, 리더는 샘플링 확인 |
| **[R]** | **3자 리뷰** — 팀 외부 리뷰어 서명 필요 |
| **[C]** | **CTO 관심** — CTO가 5분 승인 판단 시 주목 |
| **[A]** | **AI 초안 가능** — 사람 최종 검토 전제로 AI가 초안 생성 OK |

태그는 중복 가능 (예: `[L][C]` = 리더 필수 + CTO 관심).

### "조직 표준 Default" 패턴 (신규, v2)

현재 조직에 AI 사용 표준이 없는 상태를 수용. Doc 3/4의 많은 섹션에 **`조직 표준 v0.1 (default) 블록`**을 내장:

- 합리적 업계 기본값(OWASP·일반 관행)을 미리 제시
- 프로젝트는 **수용** or **예외 명시**만 하면 됨
- 여러 프로젝트의 수정·예외 패턴이 곧 **조직 표준 진화의 데이터**가 됨
- 조직 표준이 성숙해지면 default 블록을 **외부 링크로 교체**만 하면 구조 유지

---

## 2. Tier 가변 정책

### 3-Tier 분류 (룰 기반 자동 판정)

**판정 룰**:

```
if (고위험 기준 1개 이상 충족):
    tier = high-risk
elif (경량 기준 전부 충족):
    tier = lightweight
else:
    tier = standard

# 예외: CTO 서면 승인 시만 룰 무시 가능 (2-clause)
```

### Tier 기준

| 지표 | 경량 | 표준 | 고위험 |
|------|------|------|------|
| 예상 기간 | ≤ 2주 | 2~12주 | > 12주 또는 단계별 출시 |
| 사용자 규모 | 내부 ≤ 20명 | 내부 or 소규모 외부 | 대외 공개 / 대규모 |
| 데이터 민감도 | PII 없음 | 내부 데이터 | 고객 데이터 / 규제 대상 |
| 월 운영 비용 (예상) | < 50만원 | 50~500만원 | > 500만원 |
| 팀 AI 과제 경험 | 2회 이상 | 1회 이상 | 첫 AI 과제 |
| 외부 의존 | 없음 | 일부 내부 시스템 | 외부 API / 벤더 |

### Tier별 요구 문서

| Tier | 문서 세트 |
|------|---------|
| **경량** | Doc 1 + Doc 3 (Doc 2 핵심 5줄을 Doc 1에 inline) |
| **표준** (기본) | Doc 1 + Doc 2 + Doc 3 + Doc 4 |
| **고위험** | Doc 1~4 + Doc 5 Compliance Addendum |

### CTO 예외 2-Clause

CTO가 룰 자동 판정을 override하는 경우 **서면으로만 가능하며 다음 두 문장 포함**:
1. 어느 판정 기준을 override하는지
2. override 사유 + 재검토 시점 (분기 내)

---

## 3. AI Ingest 정책 — Bootstrap Packet 단일 SSOT

**원칙**: 각 Doc에 frontmatter를 중복 주입하지 않는다. **`BOOTSTRAP.md` 1개가 단일 SSOT**. 각 Doc은 본문만 markdown.

**문서 간 충돌 우선순위 규칙** (Bootstrap에 기록):

> `Domain facts > Security policy > Delivery plan > Charter narrative`

### CI Gate 강제 (v2 신규)

Bootstrap Packet의 수동 갱신 규칙은 1년 내 무너진다 (CTO 지적). 따라서 **CI gate로 강제**:

- Doc 1~5 중 어느 하나라도 변경된 PR에서 `BOOTSTRAP.md`의 `last_updated` 필드 갱신 없으면 **머지 차단**
- `version` bump 필요 여부는 사람 판단 (경미한 변경은 last_updated만 갱신)
- CI 예시: GitHub Actions에서 `paths: docs/project-docs/*.md` 트리거 + bootstrap diff 체크

---

## 4. Doc 1: Project Charter (1페이지)

> **질문에 답함**: *"이게 회사를 위한 건가?"*
> **청중**: CTO (5분 승인 판단)
> **Bootstrap 우선순위**: 4 (narrative)
> **예상 작성 시간**: 30-40분

### 필수 항목

- 과제 이름 / 제출자 / 제출일 **[T]**
- **한 줄 요약** **[T][C]**
- **전략적 정당화** — 회사 어느 전략·필요와 연결? **[L][C]**
- **대상 사용자 · 예상 규모** **[T]**
- **성공 기준** (3개 이내, 측정 가능) **[T][C]**
- **성공 기준 Baseline** — 현재 수치 (개선 대비). *추정 허용, 추정임을 명시.* **[T]**
- 예상 자원 (인력·기간·비용) **[T][C]**
- **책임자 · 의사결정권자 · 에스컬레이션** (통합 표) **[L][C]**

  ```markdown
  | 역할 | 이름 | 연락 |
  |-----|-----|-----|
  | PM (과제 담당) | | |
  | 기술 리더 | | |
  | 의사결정권자 | | |
  | 에스컬레이션 2차 | | |
  ```

- **Out-of-scope** — 하지 않을 것 명시 **[L][C]**
- **Kill criteria** — 수치형 중단 트리거 (예: "월 4주 후 MAU < 20명 시 중단") **[L][C]**
- **위험·가정** (Kill criteria 위에 흡수됨, v1의 Risk Register 제거)
  - 주요 가정 3개 이내
  - 가정이 틀렸을 때 발동할 Kill criteria 연결 명시
- Tier 선언 **[L][C]**

---

## 5. Doc 2: Problem & Domain Brief (1~1.5페이지로 축소)

> **질문에 답함**: *"문제를 진짜로 이해하는가?"*
> **청중**: 개발팀 + AI + 리뷰어
> **Bootstrap 우선순위**: 1 (가장 우선 — 도메인 사실이 Ground Truth)
> **예상 작성 시간**: 1-1.5시간 (v2 축소)

### 축소 전략 (v1 → v2)

- 페르소나 **2개 → 1개** (가장 대표적 사용자)
- 정상 시나리오 **5개 → 3개**
- Glossary 상위 **10개 제한** (나머지는 devflow가 확장)
- To-be Workflow **상세 → 방향성 한 단락**
- As-is 유지, 상세는 유지

### 필수 항목

- **현장 문제 서술** (숫자 포함): 현재 프로세스, 아픈 지점, 빈도, 영향 **[T]**
- **As-is Workflow** — 현재 어떻게 일하는지 step-by-step **[T]**
- **To-be 방향성 (한 단락)** — 이 과제 후 어떻게 변화할지. *상세는 devflow user-stories가 확장* **[T]**
- **대표 페르소나 1명** — 일상 워크플로우, 기존 해결 시도 **[T]**
- **핵심 사용자 시나리오 3개** — 정상 경로 **[T]**
- **예외·실패 시나리오** — 자주 빠지는 케이스 2-3개 **[T]**
- **도메인 용어집 (Glossary, 상위 10개)** — AI 이해 기반 **[T][R]**
- **도메인 제약** — 규제, 관행, 데이터 특성 **[T][L]**
- **데이터 출처 신뢰도** (간소화 표) **[T][R]**

  ```markdown
  | 데이터 소스 | 신뢰도 | 비고 |
  |----------|------|-----|
  | 공식 DB | 높음 | |
  | 전문가 판단 | 중간 | 검증 필요 |
  | 추정·외부 링크 | 낮음 | 주의 |
  ```

- 성공·실패 구체 예시 (각 1개) **[T]**

---

## 6. Doc 3: AI Collaboration Plan (45분-1시간으로 축소)

> **질문에 답함**: *"AI를 잘 쓸 준비가 됐나?"*
> **청중**: CTO + 팀 자신 + AI
> **Bootstrap 우선순위**: 2
> **예상 작성 시간**: 45분-1시간 (default 블록 덕분에 기존 1-2시간에서 단축)

**v2 핵심 변경**: 각 섹션에 **`조직 표준 v0.1 (default) 블록`** + **`프로젝트 선택/예외 블록`** 2단 구조. 조직 표준이 없는 현실에서 합리적 기본값으로 시작 가능.

### 6-1. AI 도구·모델 선택

**조직 표준 v0.1 (default)**:

| 작업 유형 | 권장 도구 | 권장 모델 |
|---------|--------|---------|
| 코드 생성 | Claude Code | Sonnet 4.6 |
| 설계 리뷰 | Claude Code | Opus 4.6 |
| 문서 요약 | Gemini | Flash |
| 보안 검토 | Codex | - |

**프로젝트 선택/예외** **[L][A]**:
- [ ] 위 기본값 수용
- 예외 (있으면): _____________

### 6-2. 데이터·보안 경계

**조직 표준 v0.1 (default)**:
- 엔터프라이즈 계약: Anthropic ✓ / OpenAI ✓ / Google 검토 중
- PII 원칙: 프롬프트 주입 금지, 마스킹 필수
- 외부 API allowlist: 내부 LLM 엔드포인트만 (확장은 보안팀 승인)
- 프롬프트 injection 방어: Guardrail 레이어 필수 (입력 sanitize)

**프로젝트 선택/예외** **[L][R]**:
- [ ] 위 기본값 수용
- 프로젝트 특수 데이터: _____________
- 추가 allowlist 요청: _____________

### 6-3. Prompt / Context 자산 관리

**조직 표준 v0.1 (default)**:
- 주요 prompt는 `/prompts/` 디렉토리, Git 버전 관리
- 변경 시 PR 리뷰 필수

**프로젝트 선택/예외** **[T]**:
- [ ] 위 기본값 수용
- 프로젝트 고유 prompt 카탈로그 경로: _____________

### 6-4. 인간 최종 승인 경계 (공통 필수)

**조직 표준 (default, 변경 불가)** **[L][C]**:
- 프로덕션 배포
- 외부 API allowlist 변경
- 비용 상한 변경
- 데이터 소스 확장
- 보안 정책 변경

**프로젝트 추가** **[L][C]**:
- _____________ (프로젝트 특수 승인 필요 항목)

### 6-5. AI 금지 영역 (⭐ 공통 필수)

**조직 표준 (default, 6개 영역 변경 불가)**:

| 영역 | 금지 사유 |
|------|---------|
| 도메인 핵심 사실 확정 | AI는 도메인 지식이 얕음 — 규제 해석, 업계 관행, 내부 용어 정확성 |
| 보안 경계 설계 | 프롬프트 injection 우회 악용 위험 |
| 비용 상한·예산 | 토큰·GPU 자율 결정 시 폭발 위험 |
| 데이터 접근 범위 확장 | PII·기밀 노출 |
| 고객 영향 있는 결정 | UX·약관·계약 — 법적·비즈니스 책임 |
| 레거시 의존성 breaking change | 기존 시스템 영향 |

**프로젝트 구체 사례 (각 영역 1-2줄, 템플릿 카드 참조 가능)** **[L][R]**:

*따라 쓰기 쉽게 하려면 도메인 템플릿 카드(SaaS/내부툴/데이터/금융/의료 등)에서 고르고 수정. 템플릿 카드는 별도 작업(followup).*

- 도메인 핵심 사실: _____________
- 보안 경계: _____________
- 비용 상한: _____________
- 데이터 접근 범위: _____________
- 고객 영향 결정: _____________
- 레거시 breaking change: _____________

### 6-6. 팀 AI 리터러시 AC (Acceptance Criteria) + 3자 리뷰

단순 ✓ 체크 아닌 **검증 가능한 AC 형식**. 작성자 자가점검 후 **3자 리뷰** 서명. **[R]**

**3자 리뷰 운영 방식 (v2 단계적 도입)**:

| 단계 | 방식 | 적용 시점 |
|------|------|---------|
| **1단계 (즉시, default)** | **AI간 3자 교차 리뷰** — Claude + Codex 2개 AI가 각자 AC 증명을 검토하고 상충 의견 제시 시 사람 최종 판정 | 현재 |
| **2단계** | 1단계 + **조직 내 단일 지정 리뷰어 1명** (기술 리더 또는 COE 멤버) 서명 필수 | 운영 시작 후 |
| **3단계** | 리뷰어 풀 부족 시 **COE (Center of Excellence)** 활용 — 조직 내 AI 전문가 로테이션 | 과제 수 증가 시 |

**1단계 워크플로우**:
1. 작성자가 AC 5개 자가 증명 (PR 생성)
2. **Claude가 리뷰**: 증거 링크 열어 AC 통과 여부 판정
3. **Codex가 리뷰**: 동일 AC를 독립 관점에서 재판정
4. 두 AI 판정 일치 → AC pass
5. 판정 불일치 → 사람 최종 판정 (리더 or CTO)

| # | AC | 증명 방법 예시 | 자가 | Claude | Codex |
|---|----|------------|-----|--------|-------|
| 1 | 팀 내 AI 코딩 도구 실무 사용자 ≥ 2명 | 사용 이력 스크린샷 or commit co-author 통계 | ✓/✗ | ✓/✗ | ✓/✗ |
| 2 | Hallucination 개념과 대응 방법 1 paragraph 설명 | 팀장 작성 300자 첨부 | | | |
| 3 | AI 생성 코드 리뷰 프로세스 문서화 | PR 템플릿 링크 | | | |
| 4 | 자동 회귀 테스트 세트 존재 or 구축 계획 | 테스트 파일 or DoD 반영 | | | |
| 5 | AI 사용 중 막힘 시 에스컬레이션 경로 | Slack 채널 / 멘토 / 외부 컨설팅 | | | |

**합의 규칙**:
- 양 AI 모두 ✓ → pass
- 양 AI 모두 ✗ → 명시적 fail, revision 후 재리뷰
- 한쪽만 ✓ → 해당 근거 기록 후 **사람 1명 최종 판정**

### 6-7. 학습 계획 (2주 단위)

**조직 표준 v0.1 (default)**:
- Week 1-2: 기본 prompt, 테스트 생성
- Week 3-4: 디버깅 prompt, 리팩토링
- Week 5-6: 코드 리뷰 체크리스트 AI 활용

**프로젝트 채택 선언** **[T]**:
- [ ] 위 default 커리큘럼 채택
- 프로젝트 특수 학습 목표: _____________

### 6-8. 품질 검증

**조직 표준 v0.1 (default)**:
- AI 생성 코드 승인: 리뷰 2명 + 자동 테스트 통과 필수
- 환각 검증: 회귀 테스트 세트 (주간 실행)
- 레퍼런스 구현: 샘플 입출력 3-5개 + pass/fail 예시

**프로젝트 추가** **[L]**:
- _____________

### 6-9. AI 비용 관리

**조직 표준 v0.1 (default)**:
- 알람: 일일 사용량 > 주간 평균의 150% 시
- 자동 스로틀링: 월 예산 초과 임박 시
- 비용 대시보드: 조직 공통 URL (TBD)

**프로젝트 상한** **[L][C]**:
- 월 예상 비용: _____________
- 초과 시 대응: _____________

---

## 7. Doc 4: Delivery & Governance Plan (20-30분으로 축소)

> **질문에 답함**: *"공식 프로젝트답게 진행되나?"*
> **청중**: CTO + 조직 스텝 (보안·운영)
> **Bootstrap 우선순위**: 3
> **예상 작성 시간**: 20-30분 (default 블록 덕분)

**v2 변경**: Risk Register 제거 (Doc 1에 흡수). 주간 수동 스캔 → 분기 감사 + 이벤트 기반 스캔.

### 필수 항목

- **단계·마일스톤**: INCEPTION → CONSTRUCTION → 베타 → GA. 각 단계 종료 조건 **[T]**
- **리뷰 게이트**: 누가, 언제, 무엇 승인? CTO 체크인 시점 **[L][C]**
- **Definition of Done** (DoD)
  - **조직 표준 default**: 테스트 통과 + 리뷰 2명 + 문서 갱신
  - **프로젝트 추가**: _____________ **[L]**
- **테스트 전략**
  - **조직 표준 default**: 단위/통합/UAT (devflow NFR이 상세)
  - **프로젝트 예외**: _____________ **[T]**
- **릴리스·롤백** (default: 사내 GitHub + ArgoCD / 프로젝트 예외 명시) **[L]**
- **운영 인수인계** — 인수자·시점·교육 **[L]**
- **PR 체크리스트**
  - **조직 표준 default**: secret 검사, 테스트 존재, 리뷰어 2명, CI 통과
  - **프로젝트 추가**: _____________ **[T]**
- **회사 표준 준수** 체크리스트 **[T][L]**
  - [ ] 회사 GitHub organization 사용
  - [ ] 회사 CI/CD 파이프라인
  - [ ] 회사 모니터링·로그 표준
  - [ ] 보안팀 리뷰 시점 명시
  - [ ] 문서화 위치 (Confluence)
- **문서-코드 동기화 정책** (v2 변경: 주간 전수 스캔 폐기) **[L]**
  - **이벤트 기반 스캔**: 프롬프트 변경 PR, 금지영역 근접 코드 변경 PR에서 Doc 동기화 자동 트리거
  - **분기 1회 샘플 감사**: CTO 또는 위임 리더가 랜덤 3개 과제 감사 (진실성 확보)
  - **자동화 도구 도입은 운영 후 결정** (현재는 이벤트 PR 템플릿만 준비)

---

## 8. Doc 5: Compliance Addendum (고위험 Tier만, 1페이지)

> **질문에 답함**: *"규제·고객 데이터 리스크를 어떻게 관리하는가?"*
> **청중**: CTO + 법무 + 보안팀
> **Bootstrap 우선순위**: 1 (Domain facts와 동급 — 규제는 절대 룰)
> **예상 작성 시간**: 1-3시간 (Tier 3만)

### 필수 항목 **[L][C][R]**

- 해당 규제 (개인정보보호법 / GDPR / HIPAA / 금융 규제 등)
- 데이터 처리 방침 (수집·저장·파기·국외 이전)
- 감사 로그 요건
- 개인정보 처리방침 변경 필요 여부
- 법무팀·보안팀 리뷰 완료 여부 (증빙 링크)
- 사고 발생 시 대응 및 통지 절차

---

## 9. Bootstrap Packet (필수, AI Ingest SSOT)

**역할**: Doc 1~5 발췌의 AI 진입점. CI gate로 동시 갱신 강제.
**위치**: 프로젝트 repo 루트 `BOOTSTRAP.md` (또는 `CLAUDE.md`에 포함).
**예상 작성 시간**: 15-20분 (추후 자동 생성 도구로 0분 목표)

### YAML frontmatter 스펙

```yaml
---
doc_type: bootstrap_packet
version: 1.0
last_updated: 2026-04-15
project_id: sample-project-001
tier: standard  # lightweight | standard | high-risk

priority_order:
  - domain_facts       # Doc 2 / Doc 5
  - security_policy    # Doc 3
  - delivery_plan      # Doc 4
  - charter_narrative  # Doc 1

objective: "한 줄 요약"
success_criteria:
  - "응답시간 < 5초"
  - "MAU > 100"
kill_criteria:
  - "4주 후 MAU < 20"
  - "월 비용 상한 초과 2주 연속"

forbidden_actions:  # Doc 3 §6-5 요약
  - "PII 포함 데이터 프롬프트 주입"
  - "도메인 규제 해석 AI 자율 확정"
  - "비용 상한 변경 AI 자율 결정"
  - "데이터 소스 확장 AI 자율 결정"

human_approval_required:  # Doc 3 §6-4
  - "프로덕션 배포"
  - "외부 API allowlist 변경"
  - "모델 변경"
  - "보안 정책 변경"

doc_links:
  charter: "docs/project-docs/01-charter.md"
  domain_brief: "docs/project-docs/02-domain-brief.md"
  ai_collab: "docs/project-docs/03-ai-collab.md"
  delivery: "docs/project-docs/04-delivery.md"
  compliance: null  # (Tier 3일 때만)
glossary_path: "docs/project-docs/domain-glossary.md"
---
```

### Markdown 본문 (short)

- 한 줄 요약
- 도메인 핵심 사실 3줄 (Doc 2 발췌)
- Glossary 주요 용어 10개
- 회사 표준 핵심 5개 (Doc 4 발췌)
- DoD 발췌
- Bootstrap 기본 사용 방법 (세션 시작 시 먼저 로드)

### 갱신 규칙 (v2 신규: CI gate 강제)

- Doc 1~5 변경 PR에서 **`BOOTSTRAP.md` `last_updated` 갱신 없으면 머지 차단** (CI gate)
- 큰 변경은 `version` bump, 경미한 변경은 `last_updated`만

### CI Gate GitHub Actions 구현 예시

**파일 위치**: `.github/workflows/bootstrap-sync-check.yml`

```yaml
name: Bootstrap Sync Check

on:
  pull_request:
    paths:
      - 'docs/project-docs/**/*.md'
      - 'BOOTSTRAP.md'

jobs:
  check-bootstrap-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Detect project docs changes
        id: docs
        run: |
          if git diff --name-only origin/${{ github.base_ref }} HEAD -- \
               'docs/project-docs/**/*.md' | grep -q .; then
            echo "changed=true" >> $GITHUB_OUTPUT
          else
            echo "changed=false" >> $GITHUB_OUTPUT
          fi

      - name: Verify BOOTSTRAP.md updated
        if: steps.docs.outputs.changed == 'true'
        run: |
          # (1) BOOTSTRAP.md 파일 자체가 변경됐는가
          if ! git diff --name-only origin/${{ github.base_ref }} HEAD \
                  -- BOOTSTRAP.md | grep -q .; then
            echo "::error::Project docs changed but BOOTSTRAP.md not touched."
            exit 1
          fi

          # (2) last_updated 필드가 실제로 바뀌었는가
          CURRENT=$(grep -E '^last_updated:' BOOTSTRAP.md | awk '{print $2}')
          PREVIOUS=$(git show origin/${{ github.base_ref }}:BOOTSTRAP.md 2>/dev/null \
                     | grep -E '^last_updated:' | awk '{print $2}' || echo "")
          if [ "$CURRENT" = "$PREVIOUS" ]; then
            echo "::error::BOOTSTRAP.md last_updated field not bumped."
            exit 1
          fi

          echo "Bootstrap sync verified"
```

**Branch Protection Rule 설정** (GitHub Repo Settings → Branches):
- `Require status checks to pass before merging` ✓
- 필수 체크 목록에 `check-bootstrap-sync` 추가
- `Require branches to be up to date before merging` ✓

**예상 동작**:
- Doc 1~5 중 하나만 수정한 PR → `BOOTSTRAP.md` last_updated 갱신 안 하면 머지 차단
- Doc 변경 없는 PR (코드만) → 체크 스킵
- Bootstrap만 수정한 PR (의도적 갱신) → 정상 통과

**선택 확장 (추후)**:
- 큰 변경 감지 시 version bump 권고 (라인 추가 > 20 line 등)
- 예외 문서(e.g., `README.md`) 제외 rule
- PR 템플릿에 "Bootstrap 갱신 여부" 체크박스 자동 주입

---

## 10. 3가지 운용 순서

| 순서 | 흐름 |
|------|------|
| **작성 순서 (팀 관점)** | Doc 2 → Doc 1 → Doc 3 → Doc 4 → Bootstrap |
| **읽는 순서 (CTO 관점)** | Doc 1 → Doc 2 → Doc 3 → Doc 4 |
| **AI 주는 순서 (Bootstrap)** | Bootstrap 1개로 시작 → 필요 시 해당 Doc 추가 로드 |

---

## 11. 작성 부담 (조직 표준 진화 단계별)

**조건부 반나절 타겟** — 조직 표준이 default 블록으로 작동하는 가정 하.

### 조직 표준 없음 (현재)

| Doc | 시간 | 비고 |
|-----|------|------|
| Doc 1 Charter | 30-40분 | Baseline 추정 허용, 책임자 통합 |
| Doc 2 Domain Brief | **1-1.5h** | 축소 적용 (페르소나 1, 시나리오 3, Glossary 10) |
| Doc 3 AI Plan | **45분-1h** | default 블록으로 대부분 수용 + 예외만 기입 |
| Doc 4 Delivery | **20-30분** | default 블록 + 프로젝트 특수만 |
| Bootstrap Packet | 15-20분 | Doc 1~4 발췌 |
| **합계 (표준 Tier)** | **2.5-3.5h = 반나절** ✅ |
| 경량 Tier (Doc 1+3) | 1-1.5h | |
| 고위험 Tier | +Doc 5 1-3h = 3.5-6.5h | |

### 조직 표준 성숙 시

Default 블록이 외부 링크로 교체되면 Doc 3/4 작성 시간 **20-30분**으로 추가 단축.

### 주의

**도메인 템플릿 카드 (followup 작업)** 없이는 §6-5 구체 사례 작성에서 여전히 15-30분 추가 소요. 템플릿 카드 도입 시 이 시간도 제거 가능.

---

## 12. 약점 및 대응

| 약점 | 대응 (v2) |
|------|---------|
| 아키텍처 깊이 얕아질 위험 | 비경량 과제에 `Technical Design Note` 부록 필수 (Doc 4 부록) |
| AI 생산성 과도 낙관 | Week 2 체크포인트: 생산성 vs 예상 비교 → Tier 재판정 |
| 문서-코드 드리프트 | **이벤트 기반 스캔 + 분기 샘플 감사** (v2 주간 전수 스캔 폐기) |
| 초보자 안전장치 부족 | PR 체크리스트 + 리뷰어 2명 + secret handling (Doc 4 default) |
| **Bootstrap 동시 갱신 규칙이 의지 의존** | **CI gate로 강제** (v2 신규) |
| **3자 리뷰어 병목** | **AI간 3자 교차 리뷰(Claude+Codex) 필수화 워크어라운드 → 단일 지정 리뷰어 → COE 활용** (§6-6 3단계) |
| **조직 표준 없음** | **default 블록 패턴으로 수용** — 진화 데이터 축적 (v2 신규) |
| **Tier 판정 정치화** | **룰 기반 자동 + CTO 예외 2-clause** (v2 신규) |

---

## 13. v1 → v2 반영 내역 (closed)

| # | 변경 | 출처 |
|---|------|------|
| 1 | 역할 태그 ([L]/[T]/[R]/[C]/[A]) 각 항목에 부여 | 리더 페르소나 제안 |
| 2 | 주간 수동 스캔 → **분기 감사 + 이벤트 기반 스캔** | CTO 페르소나 제안 |
| 3 | Bootstrap 동시 갱신 → **CI gate 강제 명시** | CTO 페르소나 경고 |
| 4 | Doc 2 축소 (페르소나 1, 시나리오 3, Glossary 10, To-be 방향만) | 전 페르소나 + Jay 승인 |
| 5 | Doc 3에 **조직 표준 v0.1 (default) 블록** 내장 | Jay Q3 답변 — 조직 표준 부재 현실 |
| 6 | Risk Register 제거 → Doc 1 Kill criteria에 흡수 | 중복 제거 + Jay 승인 |
| 7 | 작성 시간 현실화 (조직 표준 진화 단계별 병기) | 3 페르소나 공통 지적 |
| 8 | Tier 판정 룰화 + CTO 예외 2-clause | CTO 페르소나 제안 |
| 9 | 책임자·의사결정권자 통합 표 | Doc 1 축소 |
| 10 | §6-5 도메인 템플릿 카드 참조 추가 (카드는 followup 작업) | 실무/리더 페르소나 요청 |

---

## 14. 남은 Open Questions — 2026-04-15 상태 업데이트

| # | Question | 상태 / 결정 |
|---|----------|----------|
| 1 | Tier 승격/강등 프로세스 (경량 → 표준 전환 조건) | **운영하면서 결정** (defer) |
| 2 | Bootstrap Packet 자동 생성 도구 도입 시점 | **추후 판단** (graphify-inspired §2.2와 연관, Phase 2+) |
| 3 | Cross-project Bootstrap 공유 여부 (조직 학습) | **운영 후 판단** (defer) |
| 4 | CI gate 실제 구현 상세 | ✅ **§9에 GitHub Actions 실물 예시 작성 완료** |
| 5 | 3자 리뷰어 풀 운영 방안 | ✅ **3단계 도입 결정** (§6-6): (1) AI간 3자 교차 리뷰(Claude+Codex) 필수화 워크어라운드 → (2) 단일 지정 리뷰어 1명 → (3) COE 활용 |

---

## 15. 다음 step 후보

1. **도메인 템플릿 카드 4-5개** 작성 (§6-5 구체 사례 쉽게 — followup 지정됨)
2. 실제 시나리오로 Doc 1~4 전부 채워보기 (설계 검증)
3. CI gate GitHub Actions workflow 실물 예시
4. Confluence 템플릿 변환 여부 결정 (조직 배포는 별도 decision)
5. `rfdc-next-gen-draft.md` (ops readiness)와 통합/분리 유지 결정
