# 시나리오 1 채우기 예시 — 고객 사용량 미터링·청구 연동 API v2

> **상태**: Draft v1 (시나리오 채움 예시)
> **작성일**: 2026-04-15
> **목적**: [`ai-project-initiation-docs-v2.md`](ai-project-initiation-docs-v2.md) + [`domain-template-cards.md`](domain-template-cards.md)를 **실제로 채워보는 설계 검증**. 가상 시나리오이나 Jay 조직 맥락(클라우드+B2B)에 근접.
> **적용 카드**: **E (빌링·미터링)** 주 + C (데이터 파이프라인) 보조
> **Tier 판정**: **고위험** (금전·감사·PII 결합, E 카드 권장 그대로)

---

## 시나리오 메타

| 항목 | 값 |
|------|------|
| 과제 이름 | 고객 사용량 미터링·청구 연동 API v2 |
| 배경 | 기존 일 단위 미터링·월별 수동 청구 → **시간 단위 미터링 + 자동 청구 연동**으로 전환 |
| 팀 구성 | ① **빌링·미터링 PM** (도메인 강자, SQL 가능, Python 초중급) <br> ② **미터링 대상 시스템 엔지니어** (도메인 강자, 개발 역량 제한) <br> ③ AI 개발 동반자 (Claude Code + Codex) |
| 기간 예상 | **10-12주** (실 개발자 부재로 일반 8주보다 길게 산정) |
| 사용자 | 사내 청구·CS팀 (일일), 외부 고객 (셀프서비스 청구 조회 월 수천 건) |

---

## 1. Bootstrap Packet (`BOOTSTRAP.md`)

```yaml
---
doc_type: bootstrap_packet
version: 0.1
last_updated: 2026-04-15
project_id: billing-metering-api-v2
tier: high-risk

priority_order:
  - domain_facts       # 미터링 단위·청구 규칙
  - security_policy    # PCI DSS, PII 격리
  - delivery_plan      # DoD·감사 로그
  - charter_narrative

objective: "시간 단위 사용량 미터링 + 자동 청구 연동으로 월 수동 청구 프로세스 대체"
success_criteria:
  - "청구 정확성: 전월 대비 ±0.5% 이내"
  - "자동 청구 비율: 95% 이상 (수동 개입 5% 이하)"
  - "API 응답 시간 p95 < 500ms"
kill_criteria:
  - "알파 4주 후 청구 오차 > 1% 지속"
  - "고객 청구 분쟁 건수 월 20건 초과"
  - "감사 로그 무결성 검증 실패 2회 이상"

forbidden_actions:
  - "청구 금액·환불·할인 정책 AI 자율 결정"
  - "미터링 단위(GB-hour, vCPU-hour) 정의 AI 자율 변경"
  - "PCI DSS 대상 결제 정보(카드번호, 계좌) AI 프롬프트 노출"
  - "고객 식별자 + 금액 결합 데이터 cross-tenant 노출"
  - "기존 청구서 포맷·webhook payload breaking change without 6-month deprecation"

human_approval_required:
  - "프로덕션 배포"
  - "외부 API 스키마 변경"
  - "청구 정책 (요율·할인·환불) 변경"
  - "새 결제 수단 추가"
  - "모델 변경 (비용 추정 영향)"
  - "미터링 대상 리소스 확장 (새 서비스 추가)"

doc_links:
  charter: "docs/project-docs/01-charter.md"
  domain_brief: "docs/project-docs/02-domain-brief.md"
  ai_collab: "docs/project-docs/03-ai-collab.md"
  delivery: "docs/project-docs/04-delivery.md"
  compliance: "docs/project-docs/05-compliance-addendum.md"
glossary_path: "docs/project-docs/domain-glossary.md"
---

# Bootstrap: 고객 사용량 미터링·청구 연동 API v2

## 한 줄 요약
시간 단위 사용량 미터링 + 자동 청구 연동. 청구 정확성과 감사 가능성이 기능 출시보다 우선.

## 도메인 핵심 사실 (3줄)
1. 미터링 단위는 `vCPU-hour`, `GiB-hour`, `GB-egress`, `request-count` 4종. 단위 정의는 재무팀 합의본이며 AI 자율 변경 금지.
2. 청구 주기는 월 1회, 매월 1일 00:00 UTC 기준. 부분월은 비례 배분.
3. 고객별 사용량은 tenant-id로 격리. cross-tenant 조회 절대 금지.

## Glossary (상위 10개)
- **vCPU-hour**: 가상 CPU 1개를 1시간 사용한 단위
- **GiB-hour**: 1 GiB 메모리 또는 스토리지를 1시간 점유
- **GB-egress**: 외부로 송출된 1 GB 트래픽
- **request-count**: API 호출 수 (100만 단위)
- **tenant-id**: 고객 조직 식별자 (UUID)
- **billing cycle**: 청구 주기 (매월 1일 ~ 말일)
- **pro-ration**: 부분월 비례 배분 (가입·해지 시)
- **usage aggregation**: 사용량 집계 (raw → hourly → daily → monthly)
- **invoice**: 확정된 청구서 (PDF + JSON)
- **adjustment**: 사후 조정 (환불·크레딧 발급)

## 회사 표준 핵심 5개
- 청구 관련 모든 코드 변경은 **감사 로그 필수** (누가·언제·무엇을)
- PCI DSS 대상 데이터는 Vault 격리, 코드·로그에 미포함
- 청구 금액 sanity check: 전월 대비 ±5% 초과 시 자동 알람
- API 인증: 내부 mTLS, 외부 OAuth 2.0 + HMAC signature
- 청구서 PDF는 변조 방지 서명 (내부 CA)

## Definition of Done (DoD)
- 단위 테스트 + 통합 테스트 + 감사 로그 무결성 테스트 통과
- 최소 3개월 과거 데이터로 backfill 정합성 검증
- 보안팀·재무팀 리뷰 승인
- 청구서 포맷 호환성 (기존 ERP 연동 깨짐 없음)

## Bootstrap 기본 사용 방법
1. 새 Claude Code 세션 시 이 문서 먼저 로드
2. 상세는 `doc_links`의 해당 Doc 추가 로드
3. 충돌 시 `priority_order` 적용 (domain > security > delivery > charter)
```

---

## 2. Doc 1: Project Charter

### 메타데이터
- 과제 이름: **고객 사용량 미터링·청구 연동 API v2**
- 제출자: 빌링·미터링 PM (홍길동)
- 제출일: 2026-04-15
- Jira 티켓: RFDC-130 (가상)
- devflow repo: `bluejayA/billing-metering-api-v2` (가상)
- 상태: Review Requested
- **Tier 선언: 고위험** (데이터 민감도·금전 결합·감사 대상)

### 한 줄 요약 **[T][C]**
시간 단위 사용량 미터링 + 자동 청구 연동으로 월 수동 청구 프로세스를 제거하고, 청구 정확성을 ±0.5% 이내로 유지한다.

### 전략적 정당화 **[L][C]**
- 현재 청구 프로세스: **월 수동 집계**에 CS팀 3명 × 월 5일 투입 → 연간 약 1,800시간
- 청구 오차 평균 2-3%, 분쟁 월 30건 → 회계 재조정 비용 + 고객 불만
- 회사 클라우드 전략의 "셀프서비스 대시보드 확장"과 연계 (외부 고객이 실시간 사용량 확인)

### 대상 사용자 · 예상 규모 **[T]**
- 사내 청구·CS팀: 일일 대시보드 + API 사용, 10명
- 외부 고객: 셀프서비스 청구 조회, 월 수천 건 조회 예상
- 내부 운영팀: 미터링 이상 탐지 알람 수신

### 성공 기준 (3개) **[T][C]**
1. **청구 정확성**: 전월 대비 ±0.5% 이내 (Baseline: 현재 ±2-3%)
2. **자동 청구 비율**: 95% 이상 (Baseline: 현재 0%, 전량 수동)
3. **API 응답 시간**: p95 < 500ms (Baseline: 없음, 신규)

### 예상 자원 (인력·기간·비용) **[T][C]**
- 인력: PM 본인 100% + 미터링 시스템 엔지니어 50% + AI (Claude Code + Codex)
- 기간: **10-12주** (실 개발자 부재로 일반 8주보다 길게)
- 비용: AI 호출 월 예상 150만원 + 인프라 월 200만원 = 월 350만원 × 12주 = **약 1,050만원**
- **고위험 Tier 기준**: 월 500만원 초과 예상은 없으나, 고객 데이터·PCI DSS 대상이라 Tier 판정 고위험

### 책임자 · 의사결정권자 · 에스컬레이션 **[L][C]**

| 역할 | 이름 | 연락 |
|-----|-----|-----|
| PM (과제 담당) | 홍길동 | @hongkd |
| 기술 리더 (파트타임 30%) | 이기술 (플랫폼팀 시니어) | @leekt |
| 의사결정권자 | CTO | @cto |
| 에스컬레이션 2차 | 재무 담당 임원 + 보안 리더 | — |

### Out-of-scope **[L][C]**
- 신규 결제 수단 추가 (카드·계좌 이체 외)
- 다국적 세금 처리 (VAT/GST) — v3
- 해외 통화 지원 (USD/EUR) — v3
- CRM 연동 (Salesforce 등)
- 결제 자체 프로세스 (PG사 결제 로직은 유지, 청구만 자동화)

### Kill criteria (수치형 중단 트리거) **[L][C]**
- **알파 출시 (4주) 후 청구 오차 > 1% 지속 → 중단 재검토**
- **고객 청구 분쟁 건수 월 20건 초과 → 롤백 검토**
- **감사 로그 무결성 검증 실패 2회 이상 → 즉시 중단 + 근본 원인 분석**
- 프로젝트 지연 > 2주 누적 → Tier 재판정

### 위험·가정 (v2에서 Doc 1로 흡수)
- **가정 1**: 기존 ERP 시스템(SAP FI)의 청구 포맷을 유지한다 → 틀리면 *"청구서 포맷 breaking change"* kill 발동
- **가정 2**: 미터링 대상 시스템의 메트릭 API가 안정적이다 → 틀리면 *"미터링 누락 > 1시간"* kill 발동
- **가정 3**: AI (Claude + Codex) 비용이 월 150만원 예상 범위 → 초과 시 Doc 3 §6-9 알람 트리거

---

## 3. Doc 2: Problem & Domain Brief (축소 v2)

### 현장 문제 서술 (숫자 포함) **[T]**
현재 CS팀이 월초 5일을 **수동 청구**에 쓴다. Excel로 집계 → 수기 조정 → PDF 발급. 오차율 평균 2-3%, 월 분쟁 30건, 재작업 1건당 2시간 소요. 고객은 실시간 사용량 조회 불가 (월말에야 청구서 수령).

### As-is Workflow **[T]**

```
[미터링 시스템] → [일 단위 집계 DB] → [월초 Excel export]
   → [CS팀 수기 조정 5일] → [Excel → ERP 입력] → [PDF 생성]
   → [이메일 발송] → [분쟁 접수 시 수기 재계산]
```

### To-be 방향성 (한 단락) **[T]**
시간 단위 미터링 → 일 단위 자동 집계 → 월초 **자동 청구 생성** → 고객이 셀프서비스로 실시간 조회. 분쟁 시 audit log 기반 자동 재계산 증거 제공. *상세 워크플로우는 devflow user-stories가 확장.*

### 대표 페르소나 1명 **[T]**
**김담당 (CS팀 시니어, 8년차)**
- 일상: 매월 1-5일 청구 집계, 일일 고객 문의 응대
- 기존 해결: Excel 매크로 + 수기 조정
- 고민: "고객이 '왜 이 금액이 나왔냐' 물을 때 설명 자료 찾기가 힘들다"

### 핵심 사용자 시나리오 3개 (정상 경로) **[T]**
1. **매월 1일 자동 청구서 발급**: 전월 사용량 집계 완료 → sanity check 통과 → PDF + JSON 생성 → ERP 전송 → 고객 이메일
2. **고객 셀프서비스 조회**: 고객 포털 로그인 → 현재 월 누적 사용량 확인 → 과거 청구서 다운로드
3. **CS팀 분쟁 대응**: 고객 문의 → CS 내부 대시보드에서 tenant-id 입력 → audit log 기반 사용량 breakdown 즉시 확인

### 예외·실패 시나리오 (2-3개) **[T]**
- **미터링 데이터 누락**: 미터링 소스 장애 1시간 → backfill 필요, 청구서 발급 보류
- **sanity check 실패**: 전월 대비 ±5% 초과 → 자동 발급 차단 + CS팀 수동 검토
- **고객 조회 폭주**: 월말 동시 조회 수천 건 → cache layer fallback

### 도메인 용어집 (Glossary, 상위 10개) **[T][R]**
Bootstrap에 기재 — 여기 반복 생략.

### 도메인 제약 **[T][L]**
- **SOX 감사 대상** (연 1회 외부 감사) — 모든 청구 관련 변경 audit log 필수
- **PCI DSS Level 2 준수** (월 거래 1M 이하) — 결제 정보는 Vault 격리
- 내부 ERP (SAP FI) 연동 포맷 유지 필수
- 고객 계약서 명시 청구 주기(월 1회) 불변

### 데이터 출처 신뢰도 (간소화 표) **[T][R]**

| 데이터 소스 | 신뢰도 | 비고 |
|----------|------|-----|
| 미터링 Kafka 토픽 (raw) | **높음** | 시스템 엔지니어 관리, 5년 운영 |
| 기존 월별 집계 DB | **중간** | 반올림 오차 누적, 재계산 필요 |
| CS팀 수기 조정 Excel | 낮음 | 참고용, v2에서 제거 대상 |
| ERP SAP FI | 높음 | 회계팀 합의된 Ground Truth |

### 성공·실패 구체 예시 **[T]**
- 성공: 월 1일 09:00 KST에 청구서 1,000건 자동 발급, CS팀 개입 0건. 분쟁 월 5건 이하.
- 실패: 자동 청구 오차 > 2%, CS팀이 수기 재검증 다시 시작 → v1 상태 회귀

---

## 4. Doc 3: AI Collaboration Plan (default + 프로젝트 예외)

### 6-1. AI 도구·모델 선택

**조직 표준 v0.1 (default)**:
- 코드 생성: Claude Code + Sonnet 4.6
- 설계 리뷰: Claude Code + Opus 4.6
- 문서 요약: Gemini Flash

**프로젝트 선택/예외** **[L][A]**:
- [x] 위 기본값 수용
- **예외**: 빌링 로직 코드 생성은 **Opus 4.6 우선** (정확성 critical, Sonnet은 backup). Codex로 교차 검증 필수.

### 6-2. 데이터·보안 경계

**default 수용** + 프로젝트 추가 **[L][R]**:
- [x] default 수용 (엔터프라이즈 계약, PII 마스킹, allowlist)
- **프로젝트 특수**:
  - **PCI DSS 데이터 (카드번호·계좌)는 AI 프롬프트 절대 주입 금지**. Vault에서 id만 참조
  - 고객 식별자 + 금액 결합은 AI 전달 시 **tenant-id 해시 처리** (예: `tenant_abc123` → `tenant_hash_xyz`)
  - 테스트 환경 데이터도 **실 고객 데이터 사용 금지** (synthetic data만)

### 6-3. Prompt / Context 자산 관리
- [x] default 수용 — `/prompts/` 디렉토리, PR 리뷰 필수

### 6-4. 인간 최종 승인 경계 (default + 프로젝트 추가)
- **default (변경 불가)**: 프로덕션 배포, 외부 API allowlist 변경, 비용 상한 변경, 데이터 소스 확장, 모델 변경, 보안 정책 변경
- **프로젝트 추가** **[L][C]**:
  - **청구 정책 (요율·할인·환불) 변경**
  - **청구서 포맷·webhook payload 변경**
  - **새 미터링 대상 리소스 추가** (예: AI 추론 호출당 과금 추가)
  - **sanity check 임계값 변경** (현재 ±5%)
  - **SAP FI 연동 인터페이스 변경**

### 6-5. AI 금지 영역 (카드 E 기반)

**조직 표준 6개 영역** (변경 불가) + **프로젝트 구체 사례**:

- **도메인 핵심 사실**: 미터링 단위(vCPU-hour, GiB-hour 등) 정의, 비례 배분 규칙, 환불·할인 규정은 AI 자율 확정 금지. 재무팀 합의본 고정.
- **보안 경계**: 결제 자격 증명 AI 노출 금지 (PCI DSS). API 인증(OAuth/HMAC) 약화 코드 AI 자율 작성 금지.
- **비용 상한**: 잘못된 청구서 sanity check (전월 대비 ±5% 초과 시 발급 자동 중단) AI 자율 해제 금지.
- **데이터 접근 범위**: 사용량 raw 데이터 + 고객 식별자 결합 상태로 AI 노출 금지. 집계·익명화 후만.
- **고객 영향 결정**: 청구 금액·환불 AI 자율 결정 금지. 기존 청구서 포맷 breaking change는 6개월 deprecation 필수.
- **레거시 breaking change**: SAP FI 연동 인터페이스·webhook payload 변경은 staging 2주 + canary 1주 + deprecation 6개월 준수.

### 6-6. 팀 AI 리터러시 AC + 3자 리뷰

**3자 리뷰 운영 단계 (v2 §6-6)**: 1단계 AI간 교차 리뷰 (Claude + Codex) 필수화.

| # | AC | 증명 방법 | 자가 | Claude | Codex |
|---|----|--------|-----|--------|-------|
| 1 | 팀 내 AI 코딩 도구 사용자 ≥ 2명 | PM 본인 + 시스템 엔지니어, 월 50+ 세션 로그 | ✓ | TBD | TBD |
| 2 | Hallucination 설명 | PM이 300자 작성 + 첨부 링크 | ✓ | TBD | TBD |
| 3 | AI 생성 코드 리뷰 프로세스 | PR 템플릿 + 리뷰어 2명 규칙 (Claude 1차 + 기술 리더 2차) | ✓ | TBD | TBD |
| 4 | 자동 회귀 테스트 | 100개 과거 월 청구 데이터로 회귀 테스트 세트 구축 예정 | ✓ | TBD | TBD |
| 5 | 에스컬레이션 경로 | 기술 리더 이기술 Slack DM + 막힐 시 COE #ai-help 채널 | ✓ | TBD | TBD |

### 6-7. 학습 계획
- [x] default 채택 (2주 단위 커리큘럼)
- **프로젝트 특수**: Week 1에 **SAP FI 연동 개념** 팀 학습 필수 (AI가 잘 모르는 도메인)

### 6-8. 품질 검증
- [x] default 수용 (리뷰 2명 + 자동 테스트)
- **프로젝트 추가**: 회귀 테스트 세트 = 최근 **12개월 실제 청구 데이터 (100+ 케이스)**로 shadow 실행, 오차 ±0.5% 이내 확인

### 6-9. AI 비용 관리
- [x] default 수용 (일일 사용량 > 주간 평균 150% 알람, 월 예산 초과 스로틀링)
- **프로젝트 상한**: 월 150만원 (고위험 Tier 평균치). 초과 시 Sonnet으로 다운그레이드.

---

## 5. Doc 4: Delivery & Governance Plan

### 단계·마일스톤 **[T]**
| Phase | 기간 | 종료 조건 |
|-------|------|--------|
| INCEPTION | Week 1 | devflow INCEPTION 산출물 완료 + Bootstrap 초안 |
| CONSTRUCTION | Week 2-8 | 5 units 완료 + 회귀 테스트 pass |
| Shadow 운영 | Week 9-10 | 실 청구 데이터로 shadow 1개월, 오차 ±0.5% |
| Canary | Week 11 | 5% 고객 (선정) 실제 자동 청구, CS 모니터 |
| GA | Week 12 | 100% 전환, CS 팀 수동 프로세스 종료 |

### 리뷰 게이트 **[L][C]**
- INCEPTION 종료: 기술 리더 + CTO 5분 체크인
- 각 Unit 완료: 기술 리더 리뷰 + Codex 교차 리뷰
- Shadow 종료: 재무팀·CS팀·보안팀 합동 리뷰
- Canary 승인: CTO 서면

### Definition of Done (default + 프로젝트 추가) **[L]**
- default: 테스트 + 리뷰 2명 + 문서 갱신
- **프로젝트 추가**:
  - 최근 12개월 회귀 테스트 pass (100+ 케이스)
  - 감사 로그 무결성 테스트 pass (변조·누락 감지)
  - 보안팀 penetration 테스트 pass
  - 재무팀 sanity check 로직 승인

### 테스트 전략
- [x] default (단위/통합/UAT)
- **프로젝트 예외**: **회귀 테스트 대신 Shadow 운영 1개월** 필수 (실 데이터 기반 검증)

### 릴리스·롤백 **[L]**
- default: 사내 GitHub + ArgoCD
- **프로젝트 특수**: 청구 발급 후 롤백 = **크레딧 발급으로 보정** (취소 불가). 따라서 Shadow/Canary 단계가 필수 게이트

### 운영 인수인계 **[L]**
- 인수자: CS팀 김담당 + 플랫폼팀 운영
- 시점: GA 1주 후
- 교육: 2시간 × 2회 (CS 기초 + 플랫폼 온콜)

### PR 체크리스트 (default + 프로젝트 추가) **[T]**
- default: secret 검사, 테스트 존재, 리뷰어 2명, CI 통과
- **프로젝트 추가**:
  - [ ] 청구 관련 변경 시 audit log 필드 추가됐는가?
  - [ ] 회귀 테스트에 새 케이스 추가했는가?
  - [ ] SAP FI 연동 스키마 변경 시 deprecation 주석?
  - [ ] BOOTSTRAP.md last_updated 갱신? (CI gate)

### 회사 표준 준수 체크리스트 **[T][L]**
- [x] 회사 GitHub organization
- [x] 회사 CI/CD (ArgoCD)
- [x] 회사 모니터링 (Watch Tower + Grafana)
- [x] 보안팀 리뷰: Shadow 시작 전, GA 전
- [x] 문서화: Confluence/BILLING/v2

### 문서-코드 동기화 정책 (v2: 주간 전수 스캔 폐기) **[L]**
- **이벤트 기반**: 프롬프트 변경 PR, 청구 로직 변경 PR에서 Doc 2/3 동기화 자동 트리거
- **분기 1회 샘플 감사**: 기술 리더 + CTO가 청구 관련 변경 3건 샘플 감사

---

## 6. Doc 5: Compliance Addendum (고위험 Tier)

- **해당 규제**: SOX (내부통제), PCI DSS Level 2, 개인정보보호법
- **데이터 처리 방침**: 
  - 수집: 미터링 raw + 고객 식별자
  - 저장: tenant-id별 격리, Vault (PCI DSS 데이터), 7년 보관 (회계)
  - 파기: 해지 후 7년 경과 시 자동 삭제
  - 국외 이전: 없음 (KR region 고정)
- **감사 로그 요건**: 청구 관련 모든 변경 who/when/what, 무결성 서명, 외부 감사 시 5년치 제공 가능
- **개인정보 처리방침 변경**: 불필요 (기존 약관 범위 내)
- **법무팀·보안팀 리뷰 완료**: TBD (Week 1 중 접수)
- **사고 발생 시 대응**: 청구 오차 > 1% 또는 PCI DSS 사고 → CTO + 법무 + 보안 24시간 내 통지. 외부 감사 대비 증거 보전.

---

## 7. 이 시나리오 채워보며 드러난 설계 구멍 (본 실습에서 배운 것)

### ✅ v2 설계가 잘 작동한 부분

1. **Tier 룰 자동 판정**: 고위험 기준 1개 이상(PCI DSS) → 자동 고위험 판정. 주관 개입 0.
2. **카드 E의 §6-5 사례**: 거의 그대로 쓰고 1-2줄만 프로젝트 맥락 수정. **20분 내 완료** (실무자 페르소나의 "30분 안에 멈춤" 문제 해소).
3. **Doc 3 default 블록**: §6-1/6-2/6-3 등은 `[x] default 수용`로 10분 절약. 프로젝트 예외만 집중.
4. **Bootstrap priority_order**: domain(미터링 단위) > security(PCI DSS) 가 충돌 판정 기준으로 실제 유용.
5. **Kill criteria 수치화**: "청구 오차 > 1% 지속" 같은 명확한 트리거가 프로젝트 시작 전에 합의됨.

### ⚠️ v2에서 보완 필요한 부분

1. **개발 초보 2명 팀 구성에서 Doc 4 PR 체크리스트가 무거움** — 체크 항목 10개+를 매 PR 적용하기 어려움. Tier별 체크리스트 간소화 필요?
2. **Shadow 운영 1개월**이 Doc 4에 구체 명시 어려움 — 템플릿이 Shadow 단계를 전제 안 함. 고위험 Tier용 Shadow 단계 템플릿 추가?
3. **AI간 3자 리뷰 (§6-6)가 아직 TBD** — 실제 Claude/Codex 검증 프로세스를 돌려봐야 실효성 확인 가능. 별도 실습 필요.
4. **"재무팀 합의본"이 어디 있는지 링크 부재** — 조직 표준 문서(미터링 단위 정의 문서) 링크가 없으면 AI가 맥락 못 잡음. 조직 표준 default 블록에 "링크가 없으면 TBD 명시" 가이드 추가 필요.
5. **SAP FI 같은 레거시 시스템 지식** — AI가 거의 모르는 영역. Doc 2 Glossary만으로는 부족, 별도 "legacy-system-brief.md" 링크 필요.

### 🔧 다음 개정 (v2 → v2.1) 권고

- Tier별 Doc 4 PR 체크리스트 간소화 (경량 3개 / 표준 5개 / 고위험 10개)
- 고위험 Tier에 Shadow/Canary 단계 표준 템플릿 추가
- 조직 표준 default 블록의 "링크 부재 시 TBD 명시" 가이드 강화
- 레거시 시스템 지식 주입용 "legacy-brief" 파일 패턴 제안
