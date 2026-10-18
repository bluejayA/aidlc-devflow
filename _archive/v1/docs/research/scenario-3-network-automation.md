# 시나리오 3 채우기 예시 — 네트워크 장비·작업 자동화 툴

> **상태**: Draft v1 (시나리오 채움 예시)
> **작성일**: 2026-04-15
> **목적**: v2 + 카드 D (네트워크 자동화 섹션 포함)를 실 시나리오로 검증 3편. **가장 위험한 시나리오** — 네트워크 명령 한 줄 오류 = 망 전체 다운.
> **적용 카드**: **D (클라우드 인프라 운영, 네트워크 자동화 섹션 집중)**
> **Tier 판정**: **고위험 확정** (망 영향·실수 허용 폭 ~0)

---

## 시나리오 메타

| 항목 | 값 |
|------|------|
| 과제 이름 | 네트워크 장비·작업 자동화 툴 v1 |
| 배경 | 네트워크 장비(switch/router/firewall) 설정 변경이 수기 CLI 세션 → 자동화. 반복 작업 표준화 + 실수 감지 |
| 팀 구성 | ① **네트워크 운영팀장** (15년차, 도메인 강자, 네트워크 CLI 능숙, 개발 거의 없음) <br> ② **네트워크 엔지니어** (Python 초급, 네트워크 장비 실무 3년차) <br> ③ AI (Claude + Codex) |
| 기간 예상 | **14-16주** (가장 위험한 시나리오, Shadow·Canary 길게) |
| 사용자 | 네트워크 운영팀 8명 (전원), SRE 리더 (읽기) |

### Tier 판정

v2 §2 Tier 룰:

| 지표 | 본 과제 | 판정 |
|------|------|------|
| 예상 기간 | 14-16주 | **고위험 (> 12주)** |
| 사용자 규모 | 내부 8명 | 경량 |
| 데이터 민감도 | 내부 (설정·토폴로지) | 표준 |
| 월 운영 비용 | < 50만원 | 경량 |
| 팀 AI 과제 경험 | 첫 AI | **고위험** |
| 외부 의존 | 망 물리 장비 | - |
| **망 영향** (비공식 기준) | **1 명령 = 전사 망 다운 가능** | **극고위험** |

→ **고위험 확정** + 내부적으로 "극고위험(critical)"으로 별도 취급. v2 룰의 "고위험 1개 이상"을 2개(기간+첫AI) 초과함.

---

## 1. Bootstrap Packet

```yaml
---
doc_type: bootstrap_packet
version: 0.1
last_updated: 2026-04-15
project_id: network-automation-tool
tier: high-risk
# 내부 표기: critical (v2.1 제안 — Tier 내 sub-level)

priority_order:
  - domain_facts        # 네트워크 토폴로지·프로토콜
  - security_policy     # 2-party approval
  - delivery_plan       # 시뮬레이터·Shadow·Canary
  - charter_narrative

objective: "네트워크 장비 설정·작업을 Python 기반 툴로 자동화. 실수 감지·롤백 자동."
success_criteria:
  - "반복 작업 10종 자동화 커버리지 100%"
  - "네트워크 사고 ZERO 유지 (GA 후 12주)"
  - "사용자 작업 시간 평균 -50%"
kill_criteria:
  - "Canary 단계 포함 어느 단계에서도 네트워크 사고 1건 = 즉시 중단 + RCA"
  - "AI 제안 명령의 dry-run 정합도 < 95%"
  - "사용자 거부율 > 30% (제안 명령을 사람이 수정하는 비율)"

forbidden_actions:
  - "AI 자율 네트워크 장비 명령 실행 (모든 명령 dry-run + 2-party 승인 필수)"
  - "BGP·라우팅 정책 AI 자율 변경"
  - "방화벽 규칙 AI 자율 추가/삭제"
  - "장비 관리자 자격 증명(enable password, SSH key) AI 노출"
  - "운영망(management plane)과 데이터망(data plane) 구분 무시"
  - "기존 토폴로지 정보 기반으로 한 명령 생성 없이 직접 명령 (영향 범위 예측 불가)"

human_approval_required:
  - "모든 프로덕션 네트워크 명령 (단 하나 예외 없음)"
  - "dry-run 결과의 영향 범위 표시 후 2-party approval (네트워크 리더 + SRE)"
  - "새 장비 추가·제거"
  - "토폴로지 변경 (인터페이스 전환, 회선 변경)"
  - "ACL·BGP community 변경"

doc_links:
  charter: "docs/project-docs/01-charter.md"
  domain_brief: "docs/project-docs/02-domain-brief.md"
  ai_collab: "docs/project-docs/03-ai-collab.md"
  delivery: "docs/project-docs/04-delivery.md"
  compliance: null
glossary_path: "docs/project-docs/domain-glossary.md"
---

# Bootstrap: 네트워크 장비 자동화 툴

## 한 줄 요약
네트워크 장비 설정·작업을 자동화 툴로 표준화. **실수 제로** 유지 (망 영향 극도로 큼).

## 도메인 핵심 사실 (3줄)
1. 네트워크 장비: Cisco IOS-XE, Juniper Junos, Arista EOS 3종. 각 장비 CLI syntax 다름. 장비 OS 버전별 호환성 고려 필수.
2. **1 명령 오류 = 망 일부 또는 전체 다운 가능**. 복구 시간 평균 15-45분, 고객 영향 발생.
3. 모든 명령 실행은 `simulator → staging → canary → prod` 4단계. 각 단계 사람 승인.

## Glossary (상위 10개)
- **VLAN**: Virtual LAN (논리적 네트워크 분할)
- **BGP**: Border Gateway Protocol (경로 알림)
- **OSPF**: Open Shortest Path First (라우팅 프로토콜)
- **ACL**: Access Control List (트래픽 필터)
- **SPAN**: Port mirroring (트래픽 감청)
- **dry-run**: 명령 실제 적용 없이 syntax 검증
- **rollback config**: 설정 직전 상태로 복원
- **management plane**: 장비 관리용 네트워크 (SSH, SNMP)
- **data plane**: 실 트래픽 전송 네트워크
- **blast radius**: 명령 영향 범위 (노드·세션·트래픽)

## 회사 표준 핵심 5개
- 모든 네트워크 명령은 2-party approval (네트워크 리더 + SRE)
- 장비 관리는 bastion host 경유 필수 (직접 접근 금지)
- 명령 실행 전 **Netbox 토폴로지 DB와 일관성 검증** 필수
- 모든 명령·응답 S3 immutable bucket에 실시간 전송 (감사)
- 장비 접속 자격 증명은 Vault JIT 24h

## Definition of Done (DoD)
- 3종 장비 OS별 단위 테스트 + 시뮬레이터 테스트
- Shadow 환경 4주 사용 + 사고 0건
- Canary 1주 (1개 장비) 사고 0건
- 롤백 절차 자동화 (모든 명령별 reverse 명령 생성)
- 외부 네트워크 감사 가능 수준 audit log

## Bootstrap 기본 사용 방법
1. 새 Claude Code 세션 시 이 문서 로드
2. 상세는 `doc_links` 추가 로드
3. 충돌 시 `priority_order` 적용 (domain > security > delivery > charter)
```

---

## 2. Doc 1: Project Charter

### 메타데이터
- 과제 이름: **네트워크 장비·작업 자동화 툴 v1**
- 제출자: 최네트 (네트워크 운영팀장)
- 제출일: 2026-04-15
- Jira 티켓: RFDC-132 (가상)
- devflow repo: `bluejayA/network-automation-tool` (가상)
- 상태: Review Requested
- **Tier 선언: 고위험 (내부 극고위험 취급)**

### 한 줄 요약 **[T][C]**
네트워크 장비 설정·작업을 자동화하여 반복 작업 시간을 절반으로, 실수 사고를 제로로 유지한다.

### 전략적 정당화 **[L][C]**
- 현재 네트워크 작업: 월 150건 수기 CLI 세션, 평균 30분/건 = 월 75시간
- 연 네트워크 사고: 3-5건 (대부분 수기 오류 원인), 사고당 평균 1시간 복구
- 회사 전략: **클라우드 확장 → 네트워크 복잡도 2배 예상** → 자동화 없이는 사고 5-10건/년으로 증가 예측

### 대상 사용자 **[T]**
- 네트워크 운영팀 8명 (전원)
- SRE 리더 (읽기 권한)
- 확장 시 데이터센터 운영팀 4명 (v2)

### 성공 기준 (3개) **[T][C]**
1. **반복 작업 10종 자동화 커버리지 100%** (Baseline: 0%, 수기)
2. **네트워크 사고 ZERO 유지** (GA 후 12주, Baseline: 연 3-5건)
3. **사용자 작업 시간 -50%** (Baseline: 30분/건 → 15분/건)

### 예상 자원 · 기간 · 비용 **[T][C]**
- 인력: 네트워크 팀장 30% + 엔지니어 100% + AI
- 기간: **14-16주** (시뮬레이터 구축 + Shadow 4주 + Canary 1주 포함)
- 비용: AI 호출 월 60만원 + 시뮬레이터 SW 월 30만원 = 월 90만원 × 15주 ≈ **약 340만원**
- Tier 고위험 + 극고위험 취급: 기간 길고 실수 허용 폭 0

### 책임자 · 의사결정권자 · 에스컬레이션 **[L][C]**

| 역할 | 이름 | 연락 |
|-----|-----|-----|
| PM (팀장) | 최네트 | @choinet |
| 기술 리더 (파트타임 30%) | 이기술 | @leekt |
| SRE 공동 승인자 | 김SRE | @kimsre |
| 의사결정권자 | CTO | @cto |
| 에스컬레이션 2차 | 장비 벤더 TAC + 보안 리더 | — |

### Out-of-scope **[L][C]**
- 장비 펌웨어 업데이트 (v2)
- 토폴로지 대규모 변경 (신규 DC 구축 등) — v3
- SDN controller 연동 (v2)
- 모니터링·알람 시스템 (별도 기존 시스템 사용)

### Kill criteria (수치형) **[L][C]**
- **어느 단계에서도 네트워크 사고 1건 = 즉시 중단** (단 1건도 허용 안 함)
- **AI 제안 명령의 dry-run 정합도 < 95%**
- **사용자 거부율 > 30%** (AI 제안을 사람이 수정하는 비율)
- 기간 지연 > 4주 누적 → CTO 재검토

### 위험·가정
- **가정 1**: 시뮬레이터(GNS3·EVE-NG 등)가 실 프로덕션 토폴로지를 99% 재현 가능 → 틀리면 Shadow 단계 무의미
- **가정 2**: AI가 Cisco/Juniper/Arista 3종 CLI syntax 차이 학습 가능 → 틀리면 장비별 fine-tuning 필요
- **가정 3**: 네트워크팀 2명이 AI 도구 학습 가능 → 틀리면 외부 컨설팅 추가

---

## 3. Doc 2: Problem & Domain Brief

### 현장 문제 서술 **[T]**
네트워크 운영팀 8명이 월 150건의 반복 작업(VLAN 생성, ACL 수정, BGP peer 추가 등)을 **수기 CLI 세션**으로 처리. 평균 30분/건 중 절반은 토폴로지 검증·테스트에 소요. 연 네트워크 사고 3-5건, 원인의 70%가 수기 오류(copy-paste, typo).

### As-is Workflow **[T]**
```
요청 접수 → [팀장 검토] → [엔지니어 SSH 접속]
    → [장비 CLI 직접 입력] → [show 명령으로 검증]
    → [실패 시 수기 롤백] → [Slack 공지] → [티켓 종료]
```

### To-be 방향성 **[T]**
툴이 표준 작업 템플릿 제공 → AI가 사용자 입력 기반 명령 생성 → 시뮬레이터 dry-run → 영향 범위 시각화 → 2-party approval → 자동 실행 + 검증 + 롤백 대기 상태. *상세는 devflow user-stories 확장.*

### 대표 페르소나 1명 **[T]**
**김네엔 (네트워크 엔지니어, 3년차)**
- 일상: 일 5-7건 네트워크 작업, 장애 대응 참여
- 기존 해결: 장비별 명령 cheatsheet + 팀장 검토
- 고민: "장비 3종 syntax 다르고, 잘못된 명령 칠까 매번 긴장됨. 특히 prod 장비 접근 시."

### 핵심 사용자 시나리오 3개 **[T]**
1. **VLAN 생성**: 사용자가 "신규 tenant-xyz VLAN 200 생성"이라고 입력 → AI가 Cisco/Juniper 양쪽 명령 생성 → 시뮬레이터 dry-run → 영향 범위 (2 switch, 0 세션) 표시 → 2-party approval → 실행 + 검증
2. **ACL 수정**: "고객 A의 특정 포트 차단" → AI가 기존 ACL 분석 + 신규 rule 생성 → staging 장비에서 dry-run → 트래픽 시뮬레이션 → 승인 → prod 적용
3. **BGP peer 추가**: 가장 위험한 작업 → AI가 **template 기반 strict mode** (자유 입력 최소) → 토폴로지 DB 일관성 검증 → 2-party approval → maintenance window 내 실행

### 예외·실패 시나리오 **[T]**
- **AI가 잘못된 명령 생성**: dry-run 시뮬레이터에서 syntax error → 자동 차단
- **dry-run 통과했으나 실 장비 거부**: 자동 롤백 + 팀 긴급 알람
- **Netbox 토폴로지와 실 장비 불일치**: 실행 전 일관성 검증 단계에서 block

### 도메인 용어집 (상위 10개) **[T][R]**
Bootstrap에 기재.

### 도메인 제약 **[T][L]**
- 3종 장비 OS 지원 필수 (Cisco IOS-XE, Juniper Junos, Arista EOS)
- 장비 OS 버전별 호환성 (최소 3개 버전 지원)
- ISO 27001 감사 대상
- 장비 접속은 bastion 경유 필수
- Netbox 토폴로지 DB가 Ground Truth

### 데이터 출처 신뢰도 **[T][R]**

| 소스 | 신뢰도 | 비고 |
|----|-----|-----|
| Netbox (토폴로지 DB) | **높음** | 네트워크팀 관리, Ground Truth |
| 장비 running-config | **높음** | 실제 장비에서 직접 조회 |
| 시뮬레이터 (GNS3/EVE-NG) | 중간 | 토폴로지 99% 재현, 1% 엣지 케이스 다름 |
| 과거 작업 log | 중간 | 5년 보관, 구 엔지니어 표기법 차이 |
| Wiki 매뉴얼 | 낮음 | 2년+ stale 가능 |

### 성공·실패 구체 예시 **[T]**
- 성공: 김네엔이 VLAN 생성 작업을 1분 입력 → 2분 검토 → 2-party 승인 → 1분 실행 = 총 5분 (기존 30분)
- 실패: AI가 BGP peer 설정에서 remote-AS 번호 hallucination → 시뮬레이터에서는 성공 → 실 장비에서 session establish 실패 → 긴급 롤백 필요

---

## 4. Doc 3: AI Collaboration Plan (카드 D 네트워크 섹션 집중)

### 6-1. AI 도구·모델
- [x] default 수용
- **예외**: **명령 생성 = Opus 필수** (syntax 정확성 critical). Codex 교차 검증 필수.

### 6-2. 데이터·보안 경계
- [x] default 수용
- **프로젝트 특수**:
  - **장비 관리자 자격 증명(enable password, SSH key, SNMP community) AI 노출 절대 금지**
  - AI는 `show` 명령 출력 요약만 처리, raw config 원문은 마스킹 후 전달
  - Bastion host 로그도 감사 대상

### 6-3. Prompt 자산
- [x] default 수용
- **추가**: 장비 OS별 템플릿 분리 (`/prompts/cisco-iosxe/`, `/prompts/juniper/`, `/prompts/arista/`)

### 6-4. 인간 최종 승인 (default + 추가)
- default 전체 적용
- **프로젝트 추가** **[L][C]**:
  - **모든 프로덕션 네트워크 명령 (단 하나 예외 없음)**
  - **dry-run 후 영향 범위 표시 + 2-party approval** (네트워크 리더 + SRE)
  - **새 장비 추가·제거**
  - **토폴로지 변경**
  - **ACL·BGP community 변경**
  - **maintenance window 외 변경**

### 6-5. AI 금지 영역 (카드 D 네트워크 특화)

- **도메인 핵심 사실**: 토폴로지·SLA·라우팅 정책 AI 자율 확정 금지. 네트워크팀·SRE 검증 필수.
- **보안 경계**: 방화벽·ACL·security group 변경 AI 자율 적용 금지. dry-run + 2-party approval.
- **비용 상한**: 대역폭·QoS 정책 AI 자율 결정 금지.
- **데이터 접근 범위**: 장비 자격 증명·running-config 원문 AI 출력 절대 금지.
- **고객 영향 결정**: 트래픽 영향 있는 변경(BGP·DNS·LB) maintenance window + 사람 승인.
- **레거시 breaking change**: 네트워크 명령 한 줄 오류 = 망 다운. 모든 변경 `simulator → staging → canary → prod` 4단계 강제.

#### 네트워크 자동화 특화 (카드 D 섹션 강화 적용)
- **모든 AI 생성 명령**: `--dry-run` 자동 부착 + 시뮬레이터 통과 증거 첨부 필수
- **영향 범위 사전 표시**: 영향받는 장비·세션·트래픽 수 AI가 산정, 사람이 확인
- **롤백 명령 동시 생성**: 모든 변경 명령에 reverse 명령 함께 출력 (자동 rollback config 저장)
- **관리망(mgmt) vs 데이터망(data) 분리**: AI는 mgmt 명령만, data plane 명령은 사람 수기
- **장비 OS 체크**: 명령 생성 시 장비 OS + 버전 확인, 호환성 matrix 검증
- **Netbox 토폴로지 일관성**: 명령 실행 전 Netbox DB와 실 장비 상태 일관성 강제 검증

### 6-6. AI 리터러시 AC + 3자 리뷰 (AI간 교차)

| # | AC | 증명 | 자가 | Claude | Codex |
|---|----|-----|-----|--------|-------|
| 1 | 팀 AI 도구 사용자 ≥ 2명 | 팀장·엔지니어 사용 이력 | ✓ | TBD | TBD |
| 2 | Hallucination 설명 | 네트워크 명령 hallucination 사례 포함 300자 | ✓ | TBD | TBD |
| 3 | AI 코드 리뷰 프로세스 | PR 템플릿 + Claude 1차 + 기술 리더 + SRE 리뷰 | ✓ | TBD | TBD |
| 4 | 자동 회귀 테스트 | 시뮬레이터 기반 100+ 명령 fixture 회귀 테스트 | ✓ | TBD | TBD |
| 5 | 에스컬레이션 경로 | 기술 리더 + SRE + 장비 벤더 TAC | ✓ | TBD | TBD |

### 6-7. 학습 계획
- [x] default 채택
- **프로젝트 추가**: Week 1에 **시뮬레이터(GNS3·EVE-NG) 실습 1일** + 장비 OS별 syntax 차이 학습

### 6-8. 품질 검증
- [x] default
- **프로젝트 추가**:
  - **AI 명령 검증 파이프라인**: syntax check → 시뮬레이터 dry-run → 영향 범위 산정 → 감사 로그 → 2-party approval
  - 100+ 과거 작업을 fixtures로 변환, 회귀 테스트

### 6-9. AI 비용 관리
- [x] default
- **프로젝트 상한**: 월 60만원. 초과 시 Opus → Sonnet 다운그레이드 (단 정확성 영향 평가 먼저).

---

## 5. Doc 4: Delivery & Governance Plan

### 단계·마일스톤 **[T]**
| Phase | 기간 | 종료 조건 |
|-------|------|--------|
| INCEPTION | Week 1 | devflow INCEPTION + 시뮬레이터 구축 |
| CONSTRUCTION v1 (기본 명령) | Week 2-6 | VLAN·ACL 자동화, 3종 장비 OS 지원 |
| CONSTRUCTION v2 (복잡 명령) | Week 7-10 | BGP·OSPF 자동화, 토폴로지 검증 |
| Shadow 운영 | Week 11-14 | **4주 Shadow** (실 운영자 시뮬레이터에서 사용, 사고 0건) |
| Canary | Week 15 | **1주 Canary** (1개 장비 실 prod 사용) |
| GA | Week 16 | 전체 8명 전환 |

### 리뷰 게이트 **[L][C]**
- INCEPTION 종료: 기술 리더 + SRE + CTO 체크인
- 각 Unit 완료: 기술 리더 + Codex + SRE 교차 리뷰 (3-way)
- Shadow 종료: SRE + 보안팀 + 장비 벤더 consult
- Canary 승인: CTO 서면 + SRE 리더 서면

### DoD **[L]**
- default + **프로젝트 추가**:
  - 시뮬레이터 기반 100+ fixture 회귀 테스트
  - 장비 OS 3종 × 버전 3개 = 9개 조합 매트릭스 테스트
  - Shadow 4주 사고 0건
  - Canary 1주 사고 0건
  - 롤백 절차 자동화 + 팀 훈련 완료

### 테스트 전략
- [x] default
- **프로젝트 예외**: **시뮬레이터 → Shadow 4주 → Canary 1주 → GA** 강제

### 릴리스·롤백 **[L]**
- default: GitHub + ArgoCD (툴 자체)
- **프로젝트 특수**:
  - 네트워크 명령 롤백 = 자동 저장된 rollback config 적용
  - 롤백 실패 시 → 즉시 사람 수기 개입 + 장비 벤더 TAC 연락
  - 롤백 검증 = 5분 내 사용자 트래픽 정상 확인

### 운영 인수인계 **[L]**
- 인수자: 네트워크 운영팀 전원
- 교육: 시뮬레이터 실습 2시간 + 실 장비 shadow 1시간 × 3일
- Runbook 업데이트 필수

### PR 체크리스트 **[T]**
- default + **프로젝트 추가**:
  - [ ] 시뮬레이터 테스트 통과?
  - [ ] 장비 OS별 호환성 확인?
  - [ ] 롤백 명령 동시 생성됨?
  - [ ] BOOTSTRAP.md last_updated 갱신? (CI gate)
  - [ ] 감사 로그 전송 확인?

### 회사 표준 준수 **[T][L]**
- [x] 회사 GitHub + ArgoCD
- [x] 감사 로그 S3 immutable
- [x] Vault JIT 자격 증명 + bastion host
- [x] Netbox 토폴로지 DB 연동
- [x] 보안팀 리뷰: Shadow 전, Canary 전, GA 전 (3회)
- [x] 문서화: Confluence/NETWORK/automation-tool

### 문서-코드 동기화
- **이벤트 기반**: 명령 템플릿 추가·삭제 PR, 장비 OS 버전 추가 PR, Netbox 스키마 변경 시
- **분기 샘플 감사**: 기술 리더 + SRE + CTO 랜덤 5개 명령 감사 (네트워크 특성상 빈도 up)

---

## 6. Doc 5: Compliance Addendum

- **해당 규제**: ISO 27001 (네트워크 변경 감사 필수), 내부 정보보안 정책
- **데이터 처리 방침**: 장비 config·log는 내부 S3, 7년 보관 (감사)
- **감사 로그 요건**: 모든 명령·응답·승인자 실시간 전송, 변조 방지 서명
- **보안팀·네트워크팀 리뷰**: Shadow 전, Canary 전, GA 전 3회 필수
- **사고 시 대응**: 24시간 내 CTO + 보안 + SRE 통지, 72시간 내 RCA 문서, ISO 감사 대비 증거 보전

---

## 7. 이 시나리오 채워보며 드러난 설계 구멍

### ✅ v2 잘 작동

1. **카드 D 네트워크 자동화 섹션**: dry-run·롤백·관리망 분리·Netbox 일관성 등이 그대로 활용됨. **카드 E처럼 명확한 도메인 특화** 효과.
2. **Tier 고위험 확정 + 강화**: 기간·첫 AI·망 영향 복수 트리거. 주관 없이 최상위 Tier.
3. **2-party approval**: 카드 D §6-4 추가 승인 경계가 네트워크 시나리오에서 필수 장치로 자연 등장.

### ⚠️ v2.1 보완 권고 (시나리오 3 특유)

1. **"Critical" sub-level 필요**: 고위험 Tier 안에서도 "망 사고 = 1건도 용납 안 됨" 수준은 별도. Tier 4번째 단계 or sub-flag 도입 검토.
2. **시뮬레이터 요구**: 카드 D에 "도메인에 따라 시뮬레이터 필수" 언급 부재. 네트워크·로봇·의료기기 등 특정 도메인은 simulator 의무. 카드 D에 섹션 추가 권고.
3. **2-party / 3-party approval**: v2 §6-4는 "인간 최종 승인" 단일. 네트워크는 2명(네트워크+SRE) 필수. Tier 고위험에 multi-party approval 옵션 명시.
4. **장비 OS 버전 매트릭스**: 네트워크 특유 "OS 3종 × 버전 3개" 같은 매트릭스 테스트 개념이 Doc 4 DoD에 부재. 도메인별 DoD 확장 가이드 필요.
5. **Runbook 연동**: AI가 명령 생성 시 관련 runbook 자동 첨부하는 개념이 v2에 없음. §6-8 품질 검증에 추가 권고.

### 🔧 v2 → v2.1 반영 권고 (시나리오 1·2·3 종합)

**필수 (시나리오 3+ 도메인 특이 사항)**:
- **Critical sub-level** 도입 (고위험 내 1건 사고 불허 영역)
- **시뮬레이터 의무 도메인** 리스트 (네트워크·로봇·의료기기 등)
- **Multi-party approval** 옵션 (2-party, 3-party)
- 도메인별 DoD 확장 가이드 (장비 OS 매트릭스, 환경 조합 등)
- AI 생성 결과에 Runbook 자동 연동 가이드 (§6-8)

**전체 v2.1 권고 총 12건 (시나리오 1·2·3 누적)**:
1. Tier별 PR 체크리스트 차등
2. 고위험 Shadow/Canary 표준 단계
3. Doc 5 Tier별 축소 가이드 (규제 유무 분기)
4. 조직 표준 default "링크 부재 시 TBD" 가이드
5. 레거시 시스템 지식 주입 legacy-brief 패턴
6. AI 명령 생성 검증 파이프라인 섹션 (§6-8 확장)
7. Tier 판정 근거 자동 표시 (문서 상단)
8. **Critical sub-level (고위험 내 극고위험)** 신규
9. **시뮬레이터 의무 도메인 리스트** 신규
10. **Multi-party approval 옵션** 신규
11. **도메인별 DoD 확장 가이드** 신규
12. **Runbook 자동 연동** (§6-8 확장) 신규
