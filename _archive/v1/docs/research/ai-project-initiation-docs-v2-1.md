# AI 시대 프로젝트 착수 문서 세트 (CTO 요구안 v2.1)

> **상태**: Draft v2.1 — 3-scenario 검증 (빌링·미터링 / 플랫폼 CLI·포탈 / 네트워크 자동화) 반영 + v2 한계 12건 해소.
> **작성일**: 2026-04-15
> **v2 → v2.1 주요 변경**: Critical sub-level / 시뮬레이터 의무 도메인 / Multi-party approval / Tier별 PR 체크리스트 / Shadow·Canary Tier별 / Doc 5 축소 가이드 / AI 명령 검증 파이프라인 / Runbook 연동 / legacy-brief / DoD 도메인 확장 / Tier 근거 자동 표시 / default TBD 가이드.
> **구현 의도**: 없음. debate/설계 재료. 조직 배포 결정은 별도.
> **연관 문서**: [`domain-template-cards.md`](domain-template-cards.md), [`scenario-1-billing-metering.md`](scenario-1-billing-metering.md), [`scenario-2-platform-cli-portal.md`](scenario-2-platform-cli-portal.md), [`scenario-3-network-automation.md`](scenario-3-network-automation.md), [`rfdc-next-gen-draft.md`](rfdc-next-gen-draft.md).

---

## 1. 개요

### 두 가지 동시 기능

1. **CTO 승인 게이트** — 조직 자원 투입 결정
2. **AI Bootstrap Input** — AI에게 프로젝트 맥락 주입, 일관된 방향 유지

### 핵심 원칙

- **가변 tier** (경량/표준/고위험/**Critical sub-level**) + 룰 기반 자동 판정
- **Bootstrap Packet 단일 SSOT** + CI gate 강제
- **AI 금지 영역 명시** — 도메인 강자+초보자 조합의 최대 리스크 회피
- **분기 감사 + 이벤트 기반 스캔** — 드리프트 대응 (주간 전수 폐기)
- **조직 표준 default 블록 내장** — 조직 AI 표준 부재 현실 수용
- **Tier 판정 근거 자동 표시** (v2.1 신규) — 모든 Doc 상단에 Tier + 근거 1줄

### 역할 태그 범례

| 태그 | 의미 |
|------|------|
| **[L]** | 리더 필수 (파트타임 기술 리더 검토·승인) |
| **[T]** | 팀 자율 (실무 엔지니어 작성, 리더 샘플링) |
| **[R]** | 3자 리뷰 (팀 외부 또는 AI 교차 리뷰) |
| **[C]** | CTO 관심 (5분 승인 판단 시 주목) |
| **[A]** | AI 초안 가능 (사람 최종 검토 전제) |

### "조직 표준 Default" 패턴 + "링크 부재 TBD" 규칙 (v2.1 강화)

조직 AI 사용 표준이 없는 현실 수용. Doc 3/4 각 섹션에 `조직 표준 v0.1 (default) 블록` + `프로젝트 선택/예외 블록` 2단 구조.

**v2.1 신규 "TBD 명시" 규칙**:

조직 표준 default 블록 중 **실 근거 링크(정책 문서·대시보드·카탈로그 등)가 없는 항목**은 *반드시* `(TBD: 조직 표준 미확정)`로 표기한다. 공란·암묵적 default 금지.

예:
```markdown
- 비용 대시보드: 조직 공통 URL (TBD: 조직 표준 미확정)
- 엔터프라이즈 계약 약관: Anthropic ✓ / OpenAI ✓ / Google (TBD: 법무 검토 중)
```

이유: "default가 있는 척" 형식주의 방지, 조직 표준 진화 데이터 수집.

---

## 2. Tier 가변 정책

### 3-Tier + Critical sub-level (v2.1 신규)

**판정 룰**:

```
if (critical_trigger):         # sub-level: 망 사고 1건도 불허 영역
    tier = high-risk (critical)
elif (고위험 기준 1개 이상 충족):
    tier = high-risk
elif (경량 기준 전부 충족):
    tier = lightweight
else:
    tier = standard
# 예외: CTO 서면 승인 (2-clause)
```

### Tier 기준

| 지표 | 경량 | 표준 | 고위험 | **Critical (고위험 sub)** |
|------|------|------|------|--------|
| 예상 기간 | ≤ 2주 | 2~12주 | > 12주 | — |
| 사용자 규모 | 내부 ≤ 20 | 내부·소규모 외부 | 대외 | — |
| 데이터 민감도 | PII 없음 | 내부 | 고객·규제 | — |
| 월 운영 비용 | < 50만원 | 50~500만원 | > 500만원 | — |
| 팀 AI 경험 | 2회+ | 1회+ | 첫 AI | — |
| 외부 의존 | 없음 | 일부 내부 | 외부 API·벤더 | — |
| **Critical 트리거 (v2.1 신규)** | — | — | — | **1건 실수 = 대규모 영향 (망 다운·금전 오차·생명 안전·법적 책임 등)** |

**Critical 트리거 예시**:
- 네트워크 장비 자동화 (망 전체 영향)
- 금융 결제 핵심 로직 (금전 오차 1원도 불허)
- 의료 기기·진단 (생명 안전)
- 공공 시스템 (법적 책임)

### Tier별 요구 문서

| Tier | 문서 세트 | Shadow | Canary |
|------|---------|--------|--------|
| 경량 | Doc 1 + Doc 3 | 선택 | 선택 |
| 표준 | Doc 1~4 | 선택 (1-2주) | 선택 |
| 고위험 | Doc 1~4 + Doc 5 | **필수 (2-4주)** | **필수 (1주)** |
| Critical | 고위험 전부 + **시뮬레이터 환경 필수** | **필수 (4주+)** | **필수 (1주, 단일 대상)** |

### Shadow·Canary 표준 단계 (v2.1 신규)

**Shadow 운영**: 실제 사용자/데이터로 병렬 실행, **영향은 없고 결과만 수집**.
- 경량: 선택 (1주)
- 표준: 선택 (1-2주)
- 고위험: **필수 2-4주** (시나리오 1·3 기반)
- Critical: **필수 4주+** 시뮬레이터 기반 (시나리오 3 기반)

**Canary**: 전체 중 **작은 비율**만 실 프로덕션 적용.
- 경량·표준: 선택
- 고위험·Critical: **필수** (5% 사용자 or 1개 장비)

### CTO 예외 2-Clause

CTO override 서면 시 2개 문장 필수:
1. 어느 판정 기준을 override하는지
2. override 사유 + 재검토 시점 (분기 내)

---

## 3. AI Ingest 정책 — Bootstrap Packet 단일 SSOT

**원칙**: 각 Doc frontmatter 중복 금지. `BOOTSTRAP.md` 1개 SSOT.

**충돌 우선순위 규칙**:

> `Domain facts > Security policy > Delivery plan > Charter narrative`

### CI Gate 강제

Doc 1~5 변경 PR에서 `BOOTSTRAP.md` `last_updated` 갱신 없으면 머지 차단. GitHub Actions workflow 실물 예시 §9 참조.

---

## 4. Doc 1: Project Charter (1페이지)

> **질문**: *"이게 회사를 위한 건가?"*
> **청중**: CTO (5분 승인)
> **Bootstrap 우선순위**: 4
> **예상 작성 시간**: 30-40분
> **v2.1 신규**: **Tier 판정 결과 + 근거 1줄을 메타데이터에 필수 표기**

### 필수 항목

- 과제 이름 / 제출자 / 제출일 **[T]**
- **Tier 선언 + 근거** (v2.1 신규, 필수) **[L][C]**: 
  - 예: `Tier: high-risk (critical) — 네트워크 명령 1건 오류 = 망 전체 영향 (Critical 트리거)`
- **한 줄 요약** **[T][C]**
- **전략적 정당화** **[L][C]**
- **대상 사용자 · 예상 규모** **[T]**
- **성공 기준** (3개, 측정 가능) **[T][C]**
- **성공 기준 Baseline** (추정 허용, 명시) **[T]**
- 예상 자원 (인력·기간·비용) **[T][C]**
- **책임자 · 의사결정권자 · 에스컬레이션** (통합 표) **[L][C]**
- **Out-of-scope** **[L][C]**
- **Kill criteria** — 수치형 트리거 **[L][C]**
- **위험·가정** — Kill criteria 연결 **[T]**

---

## 5. Doc 2: Problem & Domain Brief (축소 v2)

> **질문**: *"문제를 진짜로 이해하는가?"*
> **청중**: 개발팀 + AI + 리뷰어
> **Bootstrap 우선순위**: 1
> **예상 작성 시간**: 1-1.5시간

### 축소 방침 (v2)
페르소나 1 / 시나리오 3 / Glossary 10 / To-be 방향성만.

### 필수 항목

- **현장 문제 서술** (숫자 포함) **[T]**
- **As-is Workflow** **[T]**
- **To-be 방향성** (한 단락) **[T]**
- **대표 페르소나 1명** **[T]**
- **핵심 사용자 시나리오 3개** (정상) **[T]**
- **예외·실패 시나리오** (2-3개) **[T]**
- **도메인 용어집** (상위 10개) **[T][R]**
- **도메인 제약** (규제·관행·데이터 특성) **[T][L]**
- **데이터 출처 신뢰도** (간소화 표) **[T][R]**
- 성공·실패 구체 예시 **[T]**
- **(신규, v2.1) 레거시 시스템 brief 링크** **[T][L]**:
  - SAP FI, Netbox, 레거시 ERP, 네트워크 장비 OS 등 AI가 잘 모르는 시스템이 있으면 별도 `legacy-system-brief.md` 작성·링크
  - 내용: 시스템 이름 / 주요 개념 / 호출 인터페이스 / 버전·OS 매트릭스 / 주의사항
  - 권장 분량: 1-2페이지

---

## 6. Doc 3: AI Collaboration Plan (45분-1시간)

> **질문**: *"AI를 잘 쓸 준비가 됐나?"*
> **청중**: CTO + 팀 + AI
> **Bootstrap 우선순위**: 2

각 섹션: `조직 표준 v0.1 (default)` + `프로젝트 선택/예외` 2단 구조. Default 링크 부재 시 `(TBD: 조직 표준 미확정)` 명시 (§1 규칙).

### 6-1. AI 도구·모델

**default**:
| 작업 | 도구 | 모델 |
|-----|-----|-----|
| 코드 생성 | Claude Code | Sonnet 4.6 |
| 설계 리뷰 | Claude Code | Opus 4.6 |
| 문서 요약 | Gemini | Flash |
| 보안 검토 | Codex | - |

**프로젝트 선택/예외** **[L][A]**.

### 6-2. 데이터·보안 경계

**default**:
- 엔터프라이즈 계약: Anthropic ✓ / OpenAI ✓ / Google (TBD: 법무 검토)
- PII 마스킹 필수
- 외부 API allowlist: 내부 LLM만
- Guardrail 레이어 (입력 sanitize)

**프로젝트 선택/예외** **[L][R]**.

### 6-3. Prompt / Context 자산

**default**: `/prompts/` 디렉토리, PR 리뷰 필수.
**프로젝트 선택/예외** **[T]**.

### 6-4. 인간 최종 승인 경계 (+ Multi-party Option, v2.1 신규)

**조직 표준 (변경 불가)** **[L][C]**:
- 프로덕션 배포
- 외부 API allowlist 변경
- 비용 상한 변경
- 데이터 소스 확장
- 보안 정책 변경

**v2.1 신규 — Multi-party Approval 옵션**:

Tier와 위험 성격에 따라 **단일·2자·3자** 승인 선택:

| 승인 방식 | 적용 기준 | 예시 |
|---------|--------|-----|
| **단일** (default) | 경량·표준 | 리더 1명 서명 |
| **2-party** | 고위험 | 리더 + SRE (시나리오 2) <br> 리더 + 재무 (시나리오 1) |
| **3-party** | Critical | 리더 + SRE + 보안 (시나리오 3) |

**프로젝트 추가 (승인 방식 포함)** **[L][C]**:
- _____________ (프로젝트 특수 항목 + 승인 방식 명시)

### 6-5. AI 금지 영역 (공통 필수)

**조직 표준 (6개 영역 변경 불가)**:
| 영역 | 금지 사유 |
|------|---------|
| 도메인 핵심 사실 확정 | AI 도메인 지식 얕음 |
| 보안 경계 설계 | injection 우회 위험 |
| 비용 상한·예산 | 토큰·GPU 폭발 위험 |
| 데이터 접근 범위 확장 | PII·기밀 노출 |
| 고객 영향 결정 | UX·약관·계약 책임 |
| 레거시 breaking change | 기존 시스템 영향 |

**프로젝트 구체 사례 (도메인 템플릿 카드 활용)** **[L][R]**:

따라 쓰기 쉽게: 도메인 템플릿 카드(A-E)에서 고르고 1-2줄 수정. 카드 라이브러리: [`domain-template-cards.md`](domain-template-cards.md).

- 도메인 핵심 사실: _____________
- 보안 경계: _____________
- 비용 상한: _____________
- 데이터 접근 범위: _____________
- 고객 영향 결정: _____________
- 레거시 breaking change: _____________

### 6-6. AI 리터러시 AC + 3자 리뷰

**3자 리뷰 3단계 도입** (v2):
1단계 (즉시): AI간 교차 리뷰 (Claude + Codex) 필수화
2단계: + 단일 지정 리뷰어 (기술 리더 or COE)
3단계: COE 풀 로테이션

**1단계 워크플로우**:
1. 자가 증명 PR
2. Claude 리뷰 (증거 링크 검증)
3. Codex 리뷰 (독립 재판정)
4. 양 AI 일치 → pass / 불일치 → 사람 판정

| # | AC | 증명 | 자가 | Claude | Codex |
|---|----|-----|-----|--------|-------|
| 1 | 팀 AI 사용자 ≥ 2명 | 이력·commit 통계 | | | |
| 2 | Hallucination 설명 | 팀장 300자 | | | |
| 3 | AI 코드 리뷰 프로세스 | PR 템플릿 | | | |
| 4 | 자동 회귀 테스트 | 파일·DoD | | | |
| 5 | 에스컬레이션 경로 | Slack·멘토·COE | | | |

### 6-7. 학습 계획

**default**: 2주 단위 커리큘럼 (prompt → 디버깅 → 리뷰).
**프로젝트 채택 선언** **[T]**.

### 6-8. 품질 검증 (v2.1 대폭 확장)

**default**:
- AI 생성 코드 승인: 리뷰 2명 + 자동 테스트
- 환각 검증: 회귀 테스트 세트 주간 실행
- 레퍼런스 구현: 샘플 입출력 3-5개 + pass/fail 예시

**v2.1 신규 — AI 생성 결과 검증 파이프라인**:

도메인 따라 AI가 코드만이 아닌 **명령 / 설정 / 데이터 변환**을 생성할 때 필수 단계:

```
AI 생성 → (1) syntax check → (2) simulator/dry-run
       → (3) 영향 범위 사전 산정 → (4) 사람 승인 (tier 따라 단일/2/3-party)
       → (5) 실행 → (6) 결과 검증 → (7) 감사 로그
```

각 단계 통과 증거를 PR에 첨부 (Screenshot, 로그, diff).

**v2.1 신규 — 시뮬레이터 의무 도메인 (리스트)**:

아래 도메인은 **실 환경 직접 실행 전 시뮬레이터 통과가 의무**:

| 도메인 | 시뮬레이터 예 | 이유 |
|-------|---------|-----|
| 네트워크 장비 (switch/router/firewall) | GNS3 / EVE-NG / Cisco CML | 망 다운 위험 |
| 로봇·IoT·임베디드 | Gazebo / Unity / HIL | 물리 안전 |
| 의료 기기·진단 | 규제 시뮬레이터 | 생명 안전 |
| 금융 결제 핵심 로직 | 결제 샌드박스 | 금전 정확성 |
| 공공 시스템·전력 | 전용 테스트베드 | 법적·공공 영향 |

프로젝트가 이 리스트에 해당 시: Doc 4 DoD에 "시뮬레이터 100% 통과" 필수 기입.

**v2.1 신규 — Runbook 자동 연동**:

AI가 명령·조치 생성 시 **관련 runbook 자동 첨부** 권고:
- AI가 DB 변경 제안 → 관련 DB 롤백 runbook 링크 출력
- AI가 네트워크 변경 제안 → 해당 장비 장애 대응 runbook 링크
- AI가 배포 제안 → 배포 롤백 runbook 링크

**프로젝트 추가** **[L]**.

### 6-9. AI 비용 관리

**default**:
- 알람: 일일 사용량 > 주간 평균 150%
- 자동 스로틀링: 월 예산 초과 임박
- 비용 대시보드: 조직 공통 URL (TBD: 조직 표준 미확정)

**프로젝트 상한** **[L][C]**.

---

## 7. Doc 4: Delivery & Governance Plan

> **질문**: *"공식 프로젝트답게 진행되나?"*
> **청중**: CTO + 조직 스텝
> **Bootstrap 우선순위**: 3
> **예상 작성 시간**: 20-30분

### 필수 항목

- **단계·마일스톤** + **Tier별 Shadow/Canary** (§2 Tier 정책 참조) **[T]**
- **리뷰 게이트** **[L][C]**
- **Definition of Done** (+ v2.1 도메인별 확장 가이드, 아래)
- **테스트 전략** (default: 단위/통합/UAT)
- **릴리스·롤백** **[L]**
- **운영 인수인계** **[L]**
- **PR 체크리스트** (v2.1 Tier별 차등, 아래)
- **회사 표준 준수 체크리스트** **[T][L]**
- **문서-코드 동기화**: 이벤트 기반 + 분기 샘플 감사

### v2.1 신규 — Tier별 PR 체크리스트 차등

| Tier | 필수 체크 항목 |
|------|---------|
| **경량 (3개)** | secret 검사 / 테스트 존재 / 리뷰어 1명 |
| **표준 (5개)** | + CI 통과 / BOOTSTRAP.md last_updated 갱신 |
| **고위험 (8-10개)** | + 감사 로그 필드 확인 / 회귀 테스트 추가 / 시뮬레이터 테스트 (해당 시) / 도메인 리뷰어 승인 / 롤백 명령 포함 |
| **Critical (12개+)** | + 2-party or 3-party approval 증명 / 시뮬레이터 100% 통과 / 영향 범위 사전 산정 첨부 / Runbook 링크 / 장비 OS 매트릭스 확인 (해당 시) |

### v2.1 신규 — 도메인별 DoD 확장 가이드

DoD 기본값(테스트 + 리뷰 + 문서)에 도메인 따라 추가:

| 도메인 | 추가 DoD |
|-------|---------|
| 네트워크·인프라 | 장비 OS × 버전 매트릭스 테스트 (3×3 이상), 시뮬레이터 100% 통과, 롤백 훈련 완료 |
| 금융·빌링 | 과거 N개월 회귀 데이터 shadow, 감사 로그 무결성 테스트, 법무·재무 승인 |
| 데이터 파이프라인 | 데이터 품질 검증 + 다운스트림 영향 테스트 |
| 고객 대면 | Accessibility 준수, i18n 검증, 부하 테스트 |
| 규제 (의료·공공) | 규제 체크리스트 + 외부 감사 대비 증거 |

프로젝트가 여러 도메인에 걸치면 해당 DoD 합집합.

---

## 8. Doc 5: Compliance Addendum (v2.1 Tier별 축소 가이드)

> **질문**: *"규제·고객 데이터 리스크를 어떻게 관리하는가?"*
> **청중**: CTO + 법무 + 보안팀
> **Bootstrap 우선순위**: 1 (규제 = 절대 룰)

### v2.1 신규 — Tier 내 "규제 있음/없음" 분기

고위험 Tier여도 **외부 규제가 없으면** Doc 5 축소 가능:

| 상태 | Doc 5 형태 |
|------|---------|
| 외부 규제 있음 (GDPR, PCI DSS, HIPAA, 금융법 등) | **전체 작성** (필수 항목 6개 전부) |
| 외부 규제 없음, 내부 감사만 | **축소** — "해당 없음" 섹션 + 내부 감사 요건만 기술 (1/3 분량) |
| 규제 없음 + 내부 감사도 없음 | Doc 5 자체 생략 (고위험이라도) |

### 필수 항목 (규제 있을 때) **[L][C][R]**

- 해당 규제
- 데이터 처리 방침 (수집·저장·파기·국외 이전)
- 감사 로그 요건
- 개인정보 처리방침 변경 필요 여부
- 법무팀·보안팀 리뷰 완료 증빙
- 사고 시 대응·통지 절차

### 축소 버전 (규제 없음 + 내부 감사) 템플릿

```markdown
- 해당 규제: 없음
- 내부 감사: 회사 내부 SOX 대응 / ISO 27001 등 (해당만)
- 감사 로그: (기간) 보관
- 보안팀 리뷰: (시점) 필수
```

---

## 9. Bootstrap Packet (필수, AI Ingest SSOT)

**위치**: `BOOTSTRAP.md` (프로젝트 repo 루트) 또는 `CLAUDE.md` 섹션.

### YAML frontmatter 스펙

```yaml
---
doc_type: bootstrap_packet
version: 1.0
last_updated: 2026-04-15
project_id: sample-project-001
tier: standard  # lightweight | standard | high-risk | critical
tier_rationale: "팀 첫 AI 과제 + 인프라 조작 → 고위험 룰 자동 판정"  # v2.1 신규

priority_order:
  - domain_facts
  - security_policy
  - delivery_plan
  - charter_narrative

objective: "한 줄 요약"
success_criteria: [...]
kill_criteria: [...]
forbidden_actions: [...]
human_approval_required: [...]
approval_method: "2-party: 리더 + SRE"  # v2.1 신규 (Multi-party)

doc_links:
  charter: ...
  domain_brief: ...
  ai_collab: ...
  delivery: ...
  compliance: null
  legacy_brief: "docs/project-docs/legacy-system-brief.md"  # v2.1 신규 (해당 시)
glossary_path: ...

shadow_canary:  # v2.1 신규
  shadow_required: true
  shadow_duration_weeks: 4
  canary_required: true
  canary_scope: "1개 장비"

simulator_required:  # v2.1 신규 (해당 도메인만)
  - "GNS3 for Cisco IOS-XE"
  - "EVE-NG for Juniper Junos"
---
```

### CI Gate GitHub Actions 구현 예시

(v2 §9의 workflow 그대로 유지, §9 참조)

### 갱신 규칙

- Doc 1~5 변경 PR에서 `last_updated` 갱신 없으면 머지 차단
- 큰 변경 시 `version` bump

---

## 10. 3가지 운용 순서

| 순서 | 흐름 |
|------|------|
| 작성 (팀) | Doc 2 → Doc 1 → Doc 3 → Doc 4 → Bootstrap |
| 읽는 (CTO) | Doc 1 → Doc 2 → Doc 3 → Doc 4 |
| AI (Bootstrap) | Bootstrap 1개로 시작 → 해당 Doc 추가 로드 |

---

## 11. 작성 부담 (현실 체크)

| Tier | Doc 세트 | 표준 default 활용 시 | 조직 표준 성숙 시 |
|------|---------|---------------|--------------|
| 경량 | Doc 1 + 3 | **1-1.5h** | 45분-1h |
| 표준 | Doc 1~4 + Bootstrap | **2.5-3.5h (반나절)** | 1.5-2h |
| 고위험 | + Doc 5 | **3.5-5h** (규제 유무) | 2.5-3.5h |
| Critical | + 시뮬레이터 부록 | **5-6.5h** (시뮬레이터 설계 포함) | 3.5-4.5h |

**도메인 템플릿 카드** 활용 시 §6-5 시간 제거. 지금 카드 5종 ([`domain-template-cards.md`](domain-template-cards.md)) 사용 가능.

---

## 12. 약점 및 대응

| 약점 | 대응 |
|------|------|
| 아키텍처 깊이 얕음 | 비경량 과제에 Technical Design Note 부록 |
| AI 생산성 과도 낙관 | Week 2 체크포인트 + Tier 재판정 |
| 문서-코드 드리프트 | 이벤트 기반 스캔 + 분기 샘플 감사 |
| 초보자 안전장치 | PR 체크리스트 + secret handling |
| Bootstrap 동시 갱신 의지 의존 | **CI gate 강제** |
| 3자 리뷰어 병목 | **AI간 교차 → 지정 리뷰어 → COE 3단계** |
| 조직 표준 없음 | **default 블록 + TBD 명시** |
| Tier 판정 정치화 | **룰 자동 + Critical sub-level + CTO 2-clause** |
| **도메인 특이 요구 (네트워크·빌링·의료)** | **시뮬레이터 리스트 + 도메인별 DoD + Multi-party approval + 카드** (v2.1 신규) |

---

## 13. v2 → v2.1 반영 내역 (closed)

시나리오 1·2·3 검증에서 드러난 12건 전부 반영:

| # | 변경 | 출처 |
|---|------|------|
| 1 | Tier별 PR 체크리스트 차등 (§7) | 시나리오 1 |
| 2 | 고위험·Critical Shadow/Canary 표준 단계 (§2) | 시나리오 1·2·3 |
| 3 | Doc 5 Tier별 축소 가이드 (§8) | 시나리오 2 |
| 4 | 조직 표준 default "TBD 명시" 규칙 (§1) | 3 시나리오 공통 |
| 5 | 레거시 시스템 legacy-brief 패턴 (§5) | 시나리오 1 |
| 6 | AI 명령 생성 검증 파이프라인 (§6-8) | 시나리오 2 |
| 7 | Tier 판정 근거 자동 표시 (§4 Doc 1) | 시나리오 2 |
| 8 | **Critical sub-level** (§2) | 시나리오 3 |
| 9 | **시뮬레이터 의무 도메인 리스트** (§6-8) | 시나리오 3 |
| 10 | **Multi-party approval 옵션** (§6-4) | 시나리오 3 |
| 11 | **도메인별 DoD 확장 가이드** (§7) | 시나리오 3 |
| 12 | **Runbook 자동 연동** (§6-8) | 시나리오 3 |

---

## 14. Open Questions — 2026-04-15 기준

| # | Question | 상태 / 결정 |
|---|----------|----------|
| 1 | Tier 승격/강등 프로세스 | 운영 중 결정 |
| 2 | Bootstrap 자동 생성 도구 | 추후 판단 (graphify §2.2 연계) |
| 3 | Cross-project Bootstrap 공유 | 운영 후 판단 |
| 4 | CI gate 실제 구현 | ✅ §9 GitHub Actions 실물 예시 |
| 5 | 3자 리뷰어 풀 운영 | ✅ §6-6 3단계 도입 |
| 6 | 시뮬레이터 의무 도메인 확장 기준 | 운영 중 결정 (리스트 보강) |
| 7 | Multi-party approval 기본 조합 | 운영 중 결정 (2-party/3-party 실 패턴 축적) |
| 8 | **AI간 교차 리뷰 실효성 검증** | **다음 단계 (실 PR로 검증)** |

---

## 15. 다음 step 후보

1. 도메인 템플릿 카드 보강 (시나리오 검증에서 드러난 추가 카드 후보 — 모바일·IoT·임베디드·게임 서버 등)
2. **AI간 교차 리뷰 (§6-6) 실제 검증** — 실 PR에 Claude + Codex 리뷰 적용해 효용 측정
3. Confluence 템플릿 변환 (조직 배포는 별도 decision)
4. `rfdc-next-gen-draft.md` (ops readiness)와 통합/분리 유지 결정
5. legacy-system-brief 템플릿 작성 (Doc 2 신규 항목)
6. Tier 판정 근거 자동 표시 CI 체크 (Doc 1 제출 시 메타 포함 강제)
