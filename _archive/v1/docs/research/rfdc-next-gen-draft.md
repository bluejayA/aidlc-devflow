# RFDC (Next-Gen) — Debate Draft

> **상태**: Draft (debate 재료). 조직 배포/구현 계획 없음.
> **작성일**: 2026-04-15
> **원본**: [`TECH-RFDC.pdf`](./TECH-RFDC.pdf) (조직에서 사용하던 전통 RFDC 템플릿)
> **목적**: 전통 RFDC를 AI 시대 조직 프로세스 문서로 진화시킨 초안. 빈 템플릿 + 채워진 시나리오 예시를 나란히 두어 설계 구멍을 드러낸다.

---

## 1. 변화 요약

| 축 | 전통 RFDC | **차기 RFDC** |
|----|-----------|-------------|
| **작성자** | 개발팀 + 기술리더 | PM / 파워 유저 (비개발자) |
| **리뷰어** | 기술리더 (아키텍처 검증) | 조직 리더 (전략 + 규칙 준수) |
| **주 기능** | 기술 결정 승인 게이트 | 과제 시작 승인 + 규칙 인지 환기 |
| **작성 부담** | 고 (아키텍처 상세 요구) | 저 (30분, 1-2페이지) |
| **데이터 원천** | 독자 작성 | devflow INCEPTION 산출물 재활용 |
| **AI 특화 섹션** | 없음 | devflow NFR이 담당, 링크로 대체 |
| **도구** | Confluence + 이메일 | **Confluence + Jira** (조직 표준 워크플로우) |

## 2. 설계 원칙 (debate에서 합의)

1. **가벼움 강제** — 30분 내 작성 가능, 1-2페이지
2. **devflow 산출물 재활용** — 새 데이터 생성 대신 INCEPTION 결과 링크
3. **규칙을 미리 hardcoded 정의하지 않음** — devflow 산출물의 완결성이 곧 최소 정보 충족
4. **체크리스트 + 한 줄 기술** — "이 과제는 어떻게 적용/예외인가"로 인지 담보
5. **전통 섹션 유지 + 약해진 항목은 옵션화** — 완전 폐기 대신 보존

---

## 3. 템플릿 (빈)

### 메타데이터
- 과제 이름:
- 제출자:
- 제출일:
- Jira 티켓:
- devflow repo:
- 상태: Draft | Review Requested | Approved | Completed

### 1) 과제 요약 (brainstorming 최소 가정)
*devflow `aidlc-brainstorming` 전/후 작성. 5분.*

- **문제 정의** (한 단락):
- **대상 사용자**:
- **성공 기준** (측정 가능한 것):
- **핵심 제약 / 가정**:

### 2) INCEPTION 산출물 요약
*devflow INCEPTION 실행 후 경로 링크만. 새 작성 없음.*

- Requirements: `devflow-docs/inception/requirements.md`
- User Stories: `devflow-docs/inception/user-stories.md`
- NFR (보안·성능·Eval·데이터 거버넌스 포함): `devflow-docs/inception/nfr-requirements.md`
- Workflow Plan: `devflow-docs/inception/workflow-plan.md`
- Application Design: `devflow-docs/inception/application-design.md`
- Units: `devflow-docs/inception/units.md`

### 3) 조직 규칙 인지 체크리스트
*각 규칙 ✓ + "이 과제에 어떻게 적용/예외인가" 한 줄. 15분.*

#### General Management
- [ ] **Architecture 표준 준수**: 
- [ ] **Information Security**: 

#### Service Management (상용화 고려)
- [ ] **Capacity / Performance**: 
- [ ] **Service Continuity (RPO/RTO)**: 
- [ ] **Incident / Problem 책임자**: 
- [ ] **Monitoring**: 
- [ ] **Release 프로세스**: 

#### AI 시대 추가 항목 (devflow NFR이 상세 담당 — 요약만)
- [ ] **Eval Plan**: 
- [ ] **Data Governance**: 
- [ ] **Cost 상한** (월 예상): 

#### 옵션 (해당 시만)
- [ ] Service Request 프로세스: 
- [ ] Service Configuration: 

### 4) 로드맵 + 관련 자료
- 예상 기간:
- 마일스톤:
- 관련 자료:

### 5) 승인 이력
- Jira 티켓 flow: `Draft → Review Requested → Approved → Completed`
- 승인자:
- 승인일:
- 리뷰 코멘트:

---

## 4. 시나리오 예시 (채워진)

> **가상 시나리오**: PM A가 "사내 기술문서 AI 검색 서비스"를 제안.
> Confluence / Notion / GitHub Wiki 분산 문서 통합 검색 + LLM 답변.

### 메타데이터
- 과제 이름: 사내 기술문서 AI 검색 서비스 (Internal Tech Doc AI Search)
- 제출자: PM A
- 제출일: 2026-04-15
- Jira 티켓: [RFDC-123](#) (가상)
- devflow repo: `bluejayA/internal-doc-ai-search` (가상)
- 상태: Review Requested

### 1) 과제 요약
- **문제 정의**: 개발자가 기술 정보를 찾는 데 평균 15분/건을 소비하며, 답을 못 찾는 경우 20%. 문서가 Confluence / Notion / GitHub Wiki 3개에 분산되고 검색 품질이 낮다.
- **대상 사용자**: 사내 개발자 ~200명, PM ~50명
- **성공 기준**:
  - 검색 후 답변 도달 시간 < 3분 (기존 15분)
  - 답변 신뢰도 사용자 평가 > 4 / 5
  - 월 활성 사용자 > 100명
- **핵심 제약 / 가정**:
  - 외부 인터넷 API 호출 금지 (사내 LLM 엔드포인트만)
  - PII 포함 문서는 검색 대상 제외
  - 월 운영 비용 상한 500만원

### 2) INCEPTION 산출물 요약
(devflow 실행 후 링크. 시나리오용 가상)

- Requirements: `devflow-docs/inception/requirements.md` — 기능 요구 15건, 비기능 8건
- User Stories: `devflow-docs/inception/user-stories.md` — 7 스토리
- NFR: `devflow-docs/inception/nfr-requirements.md` — 응답 < 5초, hallucination rate < 10%, PII 필터링 100%
- Workflow Plan: `devflow-docs/inception/workflow-plan.md` — Minimal depth
- Application Design: `devflow-docs/inception/application-design.md` — 서비스 3개 (인덱싱 / 검색 / 피드백), 벡터 DB + 사내 LLM + 프론트
- Units: `devflow-docs/inception/units.md` — 5 units

### 3) 조직 규칙 인지 체크리스트

#### General Management
- [x] **Architecture 표준 준수**: 사내 K8s 표준 이미지, 내부 API Gateway 경유
- [x] **Information Security**: 사내 SSO, PII 필터링(NFR 명시), 프롬프트 injection 방어 규칙 적용

#### Service Management
- [x] **Capacity / Performance**: GPU 노드 월 2대 예상, 수평 확장. 부하 테스트는 Unit 3에서 수행
- [x] **Service Continuity (RPO/RTO)**: 인덱싱 RPO 1일 / 검색 RTO 30분. 인덱스 재구축 절차 Confluence XXX에 기록 예정
- [x] **Incident / Problem 책임자**: 1차 PM A, 2차 개발팀 B. 장애 대응 매뉴얼은 릴리즈 전 작성
- [x] **Monitoring**: 사내 Watch Tower + Grafana. 품질 지표(hallucination rate, 답변 도달 시간) 대시보드 별도 구축
- [x] **Release 프로세스**: 사내 GitHub + ArgoCD. 내부 알파 (20명) → 베타 → GA

#### AI 시대 추가 항목
- [x] **Eval Plan**: NFR 참조 — 100개 질문 세트 자동 회귀 테스트, 사용자 피드백 실시간 수집
- [x] **Data Governance**: 인덱싱 대상 문서 목록 조직 승인. 사용자 질문 로그 30일 후 자동 삭제. 모델 학습에 사용자 데이터 사용 금지
- [x] **Cost 상한**: 월 500만원 (NFR). 초과 시 알람 + 자동 스로틀링

#### 옵션
- [ ] Service Request 프로세스: (내부 서비스, 해당 없음)
- [x] Service Configuration: 환경별 config는 Vault + ConfigMap 관리

### 4) 로드맵
- 예상 기간: 8주 (INCEPTION 1주 완료, CONSTRUCTION 4주, 베타 2주, GA 1주)
- 마일스톤:
  - 2026-04-29: CONSTRUCTION 시작
  - 2026-05-27: 내부 알파 (20명)
  - 2026-06-10: 베타 (50명)
  - 2026-06-17: GA
- 관련 자료:
  - 초기 brainstorming: Confluence/AI-PROJECTS/doc-search-brainstorm
  - 경쟁 서비스 조사: Confluence/AI-PROJECTS/doc-search-landscape

### 5) 승인 이력
- Jira 티켓: RFDC-123
- 상태: Review Requested (2026-04-15)
- 승인자: TBD
- 리뷰 코멘트: (비어있음, 리뷰 대기)

---

## 5. 열린 이슈 (debate 지속)

### Q1. 체크리스트 항목은 조직별 고정인가?
Jay의 "devflow 산출물 기반" 철학에 따라 **최소 공통 분모**만 유지. 조직별 추가 규칙이 있으면 별도 섹션/링크로.

### Q2. INCEPTION 산출물 링크의 신뢰
devflow-docs는 프로젝트 repo, Confluence는 조직 위키. Confluence ↔ GitHub 인증·가시성 문제. 내부 GitHub라면 해결.

### Q3. 승인 후 산출물이 링크와 달라지면?
INCEPTION은 refinement가 흔함. RFDC 승인 스냅샷 vs 최신본 괴리 처리 방식:
- **옵션 A**: 승인 시점 스냅샷 copy (Confluence 본문에)
- **옵션 B**: 링크만 유지, 최신본 신뢰
- **옵션 C**: 중요 변경 시 RFDC re-review 트리거

### Q4. 작성 부담 실측
30분 가정의 현실성. 첫 2-3건으로 실측 필요.

### Q5. AI 자동 검증의 개입 수준
체크리스트 "한 줄 기술"의 품질을 AI가 판정 가능한가?
- *"Information Security: SSO 연동"* 정도는 불충분 → AI가 "구체 방식 명시하라" 피드백?
- 과도 개입은 작성자 부담 증가 → 균형점 필요.

### Q6. Jira 워크플로우 구체화
상태 전이 조건 + 담당자:
- `Draft → Review Requested`: 작성자 제출 버튼
- `Review Requested → Approved`: 리뷰어 승인 (누구?)
- `Review Requested → Needs Revision`: 피드백 후 작성자에게 반송
- `Approved → Completed`: 실제 GA 후 작성자 수동 업데이트

---

## 6. 다음 step 후보

1. Jay 검토 후 섹션 추가/삭제 의견 반영
2. Jay 조직 실사 시나리오 하나 더 채워보기 (도메인 특화 검증)
3. Confluence 템플릿 변환 여부 결정 (조직 배포 결정은 별도)
4. Jira 워크플로우 상세 설계 (Q6)
