# 시나리오 2 채우기 예시 — 클라우드 플랫폼 운영자 CLI + 포탈

> **상태**: Draft v1 (시나리오 채움 예시)
> **작성일**: 2026-04-15
> **목적**: [`ai-project-initiation-docs-v2.md`](ai-project-initiation-docs-v2.md) + [`domain-template-cards.md`](domain-template-cards.md) 실 시나리오 검증 2편.
> **적용 카드**: **D (클라우드 인프라 운영)** 주 + A (포탈 UI 측면) 보조
> **Tier 판정**: **고위험** (내부용이나 **프로덕션 인프라 조작 가능** → 잘못된 명령 시 대규모 영향. Tier 판정 논리가 흥미로운 케이스)

---

## 시나리오 메타

| 항목 | 값 |
|------|------|
| 과제 이름 | 클라우드 플랫폼 운영자 CLI + 포탈 v1 |
| 배경 | 플랫폼 운영자가 다수 툴(kubectl + 사내 API + Grafana + Slack)을 오가며 작업 → 통합 CLI + 웹 포탈로 표준화. AI 어시스턴트 내장 |
| 팀 구성 | ① **PM/플랫폼 운영팀장** (도메인 강자, 8년차, kubectl·쉘 능숙, Go/Python 초급) <br> ② **플랫폼 운영 엔지니어** (개발 초급, 쉘 가능) <br> ③ AI (Claude Code + Codex) |
| 기간 예상 | **10-14주** (CLI + 포탈 두 스택, 개발 초보자) |
| 사용자 | 사내 플랫폼 운영팀 20명, 개발팀 리더 30명 (읽기 권한) |

---

### Tier 판정의 모호성 (본 시나리오의 학습 포인트)

v2 §2 Tier 룰 적용:

| 지표 | 본 과제 | 판정 |
|------|------|------|
| 예상 기간 | 10-14주 | 표준 경계 (≤ 12 표준 / > 12 고위험) |
| 사용자 규모 | 내부 50명 | 표준 |
| 데이터 민감도 | 내부 데이터 | 표준 |
| 월 운영 비용 | 예상 < 100만원 | 경량-표준 |
| 팀 AI 과제 경험 | 첫 AI 과제 | **고위험 트리거** |
| 외부 의존 | 사내 인프라 | 표준 |
| **추가 고려**: 실제 인프라 조작 (프로덕션 변경) | **✓ 있음** | **고위험 트리거 (카드 D 권장)** |

→ v2 룰상 **"고위험 기준 1개 이상 → 고위험"** 자동 판정. 팀 첫 AI 과제 + 인프라 직접 조작이라 **고위험 확정**.

**학습**: v2 Tier 룰이 "모호한 중간 영역"에서 안전하게 고위험으로 수렴시키는 데 작동함. 주관 개입 없음.

---

## 1. Bootstrap Packet (`BOOTSTRAP.md`)

```yaml
---
doc_type: bootstrap_packet
version: 0.1
last_updated: 2026-04-15
project_id: platform-operator-cli-portal
tier: high-risk

priority_order:
  - domain_facts        # 플랫폼 구조·운영 관행
  - security_policy     # 명령 권한·감사
  - delivery_plan       # Shadow/Canary·롤백
  - charter_narrative

objective: "운영자 도구 통합: CLI + 포탈로 작업 표준화 + AI 어시스턴트 내장"
success_criteria:
  - "주 작업 10종 CLI 커버리지 100% (6개월 사용 데이터 기반)"
  - "포탈 월 활성 운영자 20명 이상"
  - "운영 실수 사고 월 30% 감소 (AI dry-run 덕분)"
kill_criteria:
  - "CLI로 인한 인프라 사고 1건 이상 발생 (단계 무관)"
  - "팀 AI 사용률 < 50% (6주 후)"
  - "사용자 만족도 조사 < 3/5 (베타 종료 시)"

forbidden_actions:
  - "AI가 프로덕션 명령 자율 실행 (dry-run + 사람 최종 승인 필수)"
  - "네트워크·방화벽 규칙 변경 AI 자율 적용"
  - "관리자 자격 증명(kubeconfig, AWS key) AI 프롬프트 노출"
  - "감사 로그 축소 또는 삭제"
  - "롤백 경로 없는 명령 생성"

human_approval_required:
  - "프로덕션 명령 실제 실행 (CLI와 포탈 모두)"
  - "신규 명령 템플릿 추가"
  - "권한 스코프 확장 (RBAC 변경)"
  - "모니터링·알람 임계값 변경"
  - "모델 변경 (Opus ↔ Sonnet)"

doc_links:
  charter: "docs/project-docs/01-charter.md"
  domain_brief: "docs/project-docs/02-domain-brief.md"
  ai_collab: "docs/project-docs/03-ai-collab.md"
  delivery: "docs/project-docs/04-delivery.md"
  compliance: null
glossary_path: "docs/project-docs/domain-glossary.md"
---

# Bootstrap: 플랫폼 운영자 CLI + 포탈

## 한 줄 요약
다수 툴에 흩어진 운영 작업을 통합 CLI + 포탈로 표준화. AI 어시스턴트 내장 (dry-run 필수).

## 도메인 핵심 사실 (3줄)
1. 플랫폼은 K8s 기반 멀티테넌트. 자원: deployment, service, ingress, secret, configmap, GPU nodegroup.
2. 운영 명령은 무조건 `staging → canary → prod` 단계 필수. `prod` 단계는 사람 승인.
3. 모든 명령은 감사 로그 대상. "누가-언제-무엇을-왜" 4개 field 필수.

## Glossary (상위 10개)
- **tenant**: 고객 조직 네임스페이스
- **nodegroup**: K8s 노드 풀 (GPU/CPU/메모리 특화)
- **canary**: 5% 트래픽만 새 버전으로 (점진 배포)
- **rollback window**: 배포 후 롤백 가능 시간 (기본 24시간)
- **dry-run**: 명령 실제 실행 없이 영향 범위만 계산
- **RBAC**: Role-Based Access Control (사용자 권한 체계)
- **audit log**: 모든 명령의 감사 기록 (S3 immutable)
- **runbook**: 장애 대응 절차서
- **maintenance window**: 사전 공지된 작업 시간대
- **blast radius**: 명령이 영향을 주는 범위

## 회사 표준 핵심 5개
- 모든 운영 명령은 감사 로그 전송 (S3 immutable bucket)
- `kubectl`·관리 API 직접 호출 금지 (CLI/포탈 경유 필수)
- prod 변경은 `staging` 단계 통과 + change approval 티켓 필수
- 자격 증명은 Vault에서 JIT 발급 (24h 만료)
- 장애 대응 시 runbook 우선, AI는 참조 자료 제시만

## Definition of Done (DoD)
- CLI·포탈 모두 unit test + e2e test 통과
- Shadow 환경에서 실 운영자 2주 사용 + 피드백 수집
- 감사 로그 무결성 테스트 통과
- 롤백 절차 문서화·훈련 완료

## Bootstrap 기본 사용 방법
1. 새 Claude Code 세션 시 이 문서 먼저 로드
2. 상세는 `doc_links` 해당 Doc 추가 로드
3. 충돌 시 `priority_order` 적용 (domain > security > delivery > charter)
```

---

## 2. Doc 1: Project Charter

### 메타데이터
- 과제 이름: **클라우드 플랫폼 운영자 CLI + 포탈 v1**
- 제출자: 박운영 (플랫폼 운영팀장)
- 제출일: 2026-04-15
- Jira 티켓: RFDC-131 (가상)
- devflow repo: `bluejayA/platform-operator-tools` (가상)
- 상태: Review Requested
- **Tier 선언: 고위험** (첫 AI 과제 + 프로덕션 인프라 조작, 모호 영역은 안전하게 고위험)

### 한 줄 요약 **[T][C]**
흩어진 운영 툴(kubectl + 사내 API + Grafana + Slack)을 통합 CLI와 포탈로 표준화. AI 어시스턴트로 초보 운영자 작업 보조.

### 전략적 정당화 **[L][C]**
- 현재 운영 작업: 툴 4-5개 전환, 1 작업 평균 15분
- 신규 운영자 온보딩: 3개월 (툴·명령 암기)
- 운영 실수 사고 월 8건 (잘못된 명령·복붙 오류 등)
- **조직 전략**: 플랫폼팀 확장 (현 8명 → 연말 15명) 대비 표준화 필수

### 대상 사용자 · 예상 규모 **[T]**
- 플랫폼 운영팀: 20명 (풀 유저, 매일 사용)
- 개발팀 리더: 30명 (읽기 권한, 주간 단위)
- 신규 운영자: 3-5명 예상 (연내 충원)

### 성공 기준 (3개) **[T][C]**
1. **주 작업 10종 CLI 커버리지 100%** (Baseline: 0%)
2. **포탈 월 활성 운영자 20명 이상** (Baseline: 없음, 신규)
3. **운영 실수 사고 월 -30%** (Baseline: 월 8건 → 목표 월 5-6건)

### 예상 자원 · 기간 · 비용 **[T][C]**
- 인력: PM/팀장 50% + 운영 엔지니어 100% + AI
- 기간: **10-14주**
- 비용: AI 호출 월 80만원 + 인프라 월 50만원 = 월 130만원 × 12주 ≈ **약 390만원**
- Tier 고위험 트리거: 첫 AI 과제 + 인프라 조작 영향

### 책임자 · 의사결정권자 · 에스컬레이션 **[L][C]**

| 역할 | 이름 | 연락 |
|-----|-----|-----|
| PM (팀장) | 박운영 | @parkop |
| 기술 리더 (파트타임 30%) | 이기술 (플랫폼 시니어) | @leekt |
| 의사결정권자 | CTO | @cto |
| 에스컬레이션 2차 | 보안 리더 + SRE 리더 | — |

### Out-of-scope **[L][C]**
- 고객 대면 포탈 기능 (내부용 한정)
- 결제·청구 연동 (별도 시나리오 1)
- 다중 클라우드 지원 (사내 K8s만)
- 자동 인시던트 처리 (AI는 진단·제안만, 실행은 사람)

### Kill criteria (수치형) **[L][C]**
- **CLI로 인한 인프라 사고 1건 이상 발생 (단계 무관) → 즉시 중단 + RCA**
- **팀 AI 사용률 < 50% (6주 후) → 사용자 수용성 실패 → 재검토**
- **사용자 만족도 조사 < 3/5 (베타 종료 시) → 재설계**
- 기간 지연 > 3주 누적 → Tier 재판정

### 위험·가정
- **가정 1**: 팀원 전원 CLI 친숙 (쉘 기본기 있음) → 틀리면 학습 곡선 지연
- **가정 2**: 감사 로그 S3 bucket 증설 가능 → 틀리면 감사 공백
- **가정 3**: AI가 kubectl 명령 syntax를 잘 생성함 → 틀리면 dry-run 단계에서 즉시 발견

---

## 3. Doc 2: Problem & Domain Brief (축소)

### 현장 문제 서술 **[T]**
운영자가 매일 `kubectl get pods`, `grafana`, `사내 API`, `Slack 공지` 4-5개 툴을 오가며 작업. 새 기능 배포 시 평균 7단계(빌드·배포·모니터링·공지) 필요. 복붙 오류 월 3-5건, 툴 전환 컨텍스트 전환 손실 평균 10분/작업.

### As-is Workflow **[T]**
```
운영자 → [kubectl 명령 직접] → [Grafana 모니터 수동 확인]
       → [Slack 채널 수동 공지] → [사내 API curl]
       → 결과: 툴 4-5개 전환, 복붙 오류 빈발
```

### To-be 방향성 **[T]**
단일 CLI (`platform-cli`) + 웹 포탈에서 통합 작업. AI 어시스턴트가 명령 추천·dry-run·영향 범위 표시. 실행은 항상 사람 최종 승인. *상세는 devflow user-stories 확장.*

### 대표 페르소나 1명 **[T]**
**신주임 (플랫폼팀 2년차, 주니어)**
- 일상: 일일 운영, 장애 대응, 신규 기능 배포 보조
- 기존 해결: 매뉴얼 Confluence 참조 + 선임에게 Slack 질문
- 고민: "명령어를 외우기 어려움, 잘못 칠까 무서움"

### 핵심 사용자 시나리오 3개 **[T]**
1. **일상 배포**: `platform-cli deploy --service foo --env staging` → AI가 dry-run 결과 표시 → 사용자 확인 → 실제 실행 → 자동 Slack 공지
2. **장애 진단**: 포탈에서 tenant ID 입력 → AI가 최근 1시간 메트릭 요약 + 가능한 원인 3개 제시 → 운영자가 runbook 연결
3. **권한 요청**: `platform-cli request --role admin --scope tenant-xyz --duration 2h` → 승인자 자동 할당 → 승인 시 Vault에서 JIT 발급

### 예외·실패 시나리오 **[T]**
- **AI가 잘못된 명령 제안**: dry-run 단계에서 영향 범위 이상 감지 → 자동 경고
- **Vault 토큰 만료**: JIT 토큰 24h 만료 → 자동 재발급 플로우
- **포탈 다운**: CLI fallback 모드 (모든 기능 CLI로 가능)

### 도메인 용어집 (상위 10개) **[T][R]**
Bootstrap에 기재.

### 도메인 제약 **[T][L]**
- K8s 1.28+ 필수 (최신 API 사용)
- 모든 명령 감사 로그 S3 immutable 버킷
- RBAC 정책은 보안팀 관리
- prod 변경은 change approval 티켓 필수

### 데이터 출처 신뢰도 **[T][R]**

| 소스 | 신뢰도 | 비고 |
|----|-----|-----|
| K8s API server | 높음 | 직접 조회 |
| Grafana metrics (Prometheus) | 높음 | 운영팀 관리 |
| 사내 플랫폼 API | 높음 | SLA 99.9% |
| Runbook Confluence | 중간 | 수동 업데이트, 6개월+ stale 가능 |
| Slack 과거 대화 | 낮음 | 참고용만 |

### 성공·실패 구체 예시 **[T]**
- 성공: 신주임이 첫 배포를 `platform-cli deploy` 한 줄로 실수 없이 완료. 시간 15분 → 3분.
- 실패: AI가 잘못된 namespace 명령 제안 → dry-run이 영향 범위를 못 잡음 → 타 tenant 영향

---

## 4. Doc 3: AI Collaboration Plan (카드 D 적용)

### 6-1. AI 도구·모델
- [x] default 수용 (Claude Sonnet 코드, Opus 리뷰)
- **예외**: **명령 생성 → Opus 우선** (정확성 critical), Codex로 교차 검증

### 6-2. 데이터·보안 경계
- [x] default 수용
- **프로젝트 특수**:
  - **kubeconfig·AWS key·Vault token AI 프롬프트 노출 절대 금지**
  - 명령 dry-run 결과만 AI 응답 대상 (실제 리소스 정보는 요약만)
  - 감사 로그는 AI가 조회만, 수정 금지

### 6-3. Prompt 자산
- [x] default 수용, `/prompts/commands/`에 명령별 템플릿

### 6-4. 인간 최종 승인 (default + 추가)
- default 전체 적용
- **프로젝트 추가** **[L][C]**:
  - **프로덕션 명령 실제 실행** (CLI·포탈 모두)
  - **신규 명령 템플릿 추가**
  - **RBAC 권한 스코프 확장**
  - **모니터링·알람 임계값 변경**

### 6-5. AI 금지 영역 (카드 D 기반)

- **도메인 핵심 사실**: K8s 토폴로지·SLA·RBAC 정책은 AI 자율 확정 금지. 보안팀·SRE 검증 필수.
- **보안 경계**: 방화벽·NACL·security group 변경 AI 자율 적용 금지. dry-run + 사람 승인 필수.
- **비용 상한**: 자동 스케일링 상한·인스턴스 타입 변경 AI 자율 결정 금지. 월 인프라 예산 hard cap (현 200만원).
- **데이터 접근 범위**: 프로덕션 DB·secret store는 read-only + 감사 로그. 자격 증명 AI 출력 절대 금지.
- **고객 영향 결정**: 트래픽 영향 변경(BGP·DNS·LB) maintenance window + 사람 승인.
- **레거시 breaking change**: 명령 스키마·포탈 API는 v1 호환 유지, breaking은 deprecation 3개월.

#### D 카드 특화 추가 (네트워크 자동화 대응)
- **모든 AI 생성 명령**: `--dry-run` 자동 부착, 영향 범위 표시 없이 실행 불가
- **롤백 명령 동시 생성**: AI가 명령 제안 시 reverse 명령 함께 출력
- **관리망 vs 데이터망**: AI는 관리망 명령만 (데이터망 직접 접근 금지)

### 6-6. AI 리터러시 AC + 3자 리뷰 (AI간 교차)

| # | AC | 증명 | 자가 | Claude | Codex |
|---|----|-----|-----|--------|-------|
| 1 | 팀 내 AI 코딩 도구 사용자 ≥ 2명 | PM + 엔지니어 사용 이력 | ✓ | TBD | TBD |
| 2 | Hallucination 설명 | 팀장 300자 작성 (명령 hallucination 사례 포함) | ✓ | TBD | TBD |
| 3 | AI 코드 리뷰 프로세스 | PR 템플릿 + Claude 1차 + 기술 리더 2차 | ✓ | TBD | TBD |
| 4 | 자동 회귀 테스트 | CLI 명령 fixtures 50개+ (dry-run 결과 검증) | ✓ | TBD | TBD |
| 5 | 에스컬레이션 경로 | 기술 리더 + COE #ai-help | ✓ | TBD | TBD |

### 6-7. 학습 계획
- [x] default 채택
- **프로젝트 추가**: Week 1에 **kubectl + RBAC 심화** 팀 학습

### 6-8. 품질 검증
- [x] default
- **프로젝트 추가**: **명령 dry-run 커버리지 100%** + 정기 shadow 환경 테스트

### 6-9. AI 비용 관리
- [x] default
- **프로젝트 상한**: 월 80만원 (표준 Tier 평균치). 초과 시 Sonnet 다운그레이드.

---

## 5. Doc 4: Delivery & Governance Plan

### 단계·마일스톤 **[T]**
| Phase | 기간 | 종료 조건 |
|-------|------|--------|
| INCEPTION | Week 1 | devflow INCEPTION 완료 + Bootstrap |
| CONSTRUCTION v1 (CLI) | Week 2-6 | CLI 주 명령 10종 + dry-run 100% |
| CONSTRUCTION v2 (포탈) | Week 7-9 | 웹 포탈 + CLI 통합 |
| Shadow 운영 | Week 10-11 | 실 운영자 2주 사용, 만족도 3/5 이상 |
| Canary | Week 12 | 5명 운영자 실 프로덕션 사용 |
| GA | Week 13-14 | 전체 20명 전환 |

### 리뷰 게이트 **[L][C]**
- INCEPTION 종료: 기술 리더 + CTO 체크인
- 각 Unit 완료: 기술 리더 + Codex 교차 리뷰
- Shadow 종료: SRE팀 + 보안팀 리뷰
- Canary 승인: CTO 서면

### DoD (default + 추가) **[L]**
- default: 테스트 + 리뷰 2명 + 문서
- **프로젝트 추가**:
  - 명령 dry-run 정합성 테스트 (50+ fixture)
  - 감사 로그 무결성 테스트
  - Runbook 통합 체크 (runbook 링크 자동 삽입 검증)

### 테스트 전략
- [x] default
- **프로젝트 예외**: **Shadow 환경 2주 + Canary 5명** 필수

### 릴리스·롤백 **[L]**
- default: GitHub + ArgoCD
- **프로젝트 특수**: CLI 버전 롤백은 binary 교체로 즉시, 포탈은 blue-green

### 운영 인수인계 **[L]**
- 인수자: 플랫폼팀 운영 리더
- 교육: CLI 1h + 포탈 1h + AI 사용법 1h (총 3시간)

### PR 체크리스트 **[T]**
- default + **프로젝트 추가**:
  - [ ] 명령 변경 시 dry-run 테스트 추가?
  - [ ] BOOTSTRAP.md last_updated 갱신? (CI gate)
  - [ ] 감사 로그 필드 유지?
  - [ ] runbook 링크 정합성?

### 회사 표준 준수 **[T][L]**
- [x] 회사 GitHub + ArgoCD
- [x] 감사 로그 S3 bucket 연동
- [x] Vault JIT 자격 증명
- [x] 보안팀 리뷰: Shadow 전, GA 전
- [x] 문서화: Confluence/PLATFORM/cli-portal

### 문서-코드 동기화
- **이벤트 기반**: CLI 명령 템플릿 추가·삭제 PR, RBAC 정책 변경 PR
- **분기 샘플 감사**: 기술 리더 + CTO 랜덤 3개 감사

---

## 6. Doc 5: Compliance Addendum

*이 시나리오는 외부 고객 데이터·규제 미적용이라 **Doc 5 생략** 가능. 단, Tier 고위험이라 §규제 항목은 "해당 없음"을 명시.*

- **해당 규제**: 해당 없음 (내부 도구, 외부 고객 데이터 미포함)
- **감사 로그 요건**: 회사 내부 SOX 대응 (재무팀 요청 시 1년치 제공 가능)
- **보안팀 리뷰**: Shadow 전 필수

---

## 7. 이 시나리오 채워보며 드러난 설계 구멍

### ✅ v2 잘 작동

1. **Tier 룰의 모호 영역 안전 수렴**: "10-14주 + 첫 AI + 인프라 조작" 조합을 자동 고위험 판정. 주관 개입 없음.
2. **카드 D + 네트워크 자동화 통합**: D 카드의 추가 섹션(dry-run, 롤백 동시 생성, 관리망 분리)이 그대로 적용됨.
3. **Doc 5 조건부 생략**: 고위험이지만 외부 규제 없으면 Doc 5 핵심만 남기고 생략 가능 — 유연성 확인.

### ⚠️ v2.1 보완 권고 (시나리오 1과 중복·추가)

1. **Doc 5 "해당 없음" 경량화** — 고위험인데 규제 없는 경우 Doc 5를 1/3 축소 가능. v2에 명시 필요.
2. **"명령" 같은 도메인 특수 요소** — CLI/포탈 시나리오는 단순 "기능"보다 "명령 생성 파이프라인"이 핵심. Doc 3 §6-5 외에 **"AI 생성 결과 검증 파이프라인" 섹션**이 있으면 좋겠음.
3. **"Shadow → Canary" 단계가 Tier마다 다름** — 고위험은 필수, 표준은 선택, 경량은 생략. Tier별 템플릿 필요 (시나리오 1에서도 언급).
4. **AI가 운영 명령을 생성할 때 "영향 범위 표시" 형식 표준화 부재** — AI 출력 포맷 가이드가 문서에 없음. 프롬프트 예시 라이브러리 필요.
5. **"내부 도구인데 고위험"의 인지적 저항** — 팀원에게 "우리는 내부용이니 저Tier 아닌가?" 오해 유발. Tier 판정 결과 + 근거 자동 표시 장치 필요.

### 🔧 v2 → v2.1 반영 권고 (시나리오 1·2 종합)

- Tier별 PR 체크리스트 차등
- 고위험 Tier Shadow/Canary 표준 단계 (규제 유무 무관)
- Doc 5 Tier별 축소 가이드 (규제 있음/없음 분기)
- 조직 표준 default의 "링크 부재 시 TBD 명시" 가이드
- 레거시 시스템 지식 주입용 legacy-brief 패턴
- **AI 명령 생성 결과 검증 파이프라인 섹션** (Doc 3 §6-8 확장)
- **Tier 판정 근거 자동 표시** (문서 상단에 필수 표기)
