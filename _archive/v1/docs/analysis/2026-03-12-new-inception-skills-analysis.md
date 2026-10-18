# INCEPTION 단계 새 스킬 추가 분석

> 2026-03-12 brainstorming 중간 정리

## 배경

메모리에 기록된 P1 새 스킬 4개:
- `user-stories`, `nfr-requirements`, `nfr-design`, `infrastructure-design`

**목표**: 비개발자가 이 플러그인을 이용해 상용 운영/플랫폼 최적화에 사용할 수 있는 소프트웨어를 만들 수 있도록 한다.

**핵심 과제**: NFR이나 infrastructure design은 정답이 없고, 환경/조건에 따라 맥락을 알아야 정할 수 있다.

---

## 1. 4개 스킬의 성격 분류

### 그룹 A: "구조화 가능" — 프로세스로 해결

| 스킬 | 왜 구조화 가능한가 |
|------|-------------------|
| **user-stories** | 요구사항 → 사용자 스토리 변환은 비교적 기계적. INVEST 기준, Given-When-Then 형식 등 명확한 프레임워크 존재 |
| **nfr-requirements** | "어떤 NFR이 필요한가?"를 **수집**하는 것은 체크리스트로 가능 (성능, 보안, 가용성 등 8개 카테고리). 값을 정하는 게 아니라 질문하는 것 |

### 그룹 B: "맥락 의존" — 가이드 + 선택지로 해결

| 스킬 | 왜 어려운가 | 어떻게 접근해야 하는가 |
|------|-----------|---------------------|
| **nfr-design** | "초당 1000 요청 처리" → 캐싱? 큐? 샤딩? **정답 없고 트레이드오프만 존재** | 카탈로그 방식 — NFR 카테고리별 "이런 조건이면 이 패턴" 매핑을 제시하고 사용자가 선택 |
| **infrastructure-design** | 같은 앱이라도 AWS/GCP/온프렘/비용 제약에 따라 완전히 다른 결과 | 프로파일 방식 — "MVP/소규모/대규모" 같은 템플릿을 먼저 선택하게 하고, 그에 맞는 기본값 제시 |

---

## 2. 비개발자를 위한 핵심 설계 원칙

비개발자에게 "성능 요구사항을 정해주세요"라고 하면 막힌다. 대신:

1. **질문을 구체화** — "동시 사용자가 몇 명 정도 예상되나요?" (O) vs "scalability 요구사항은?" (X)
2. **기본값 + 이유 제시** — "100명 이하라면 단일 서버로 충분합니다. 이유: ..." 로 판단 근거를 함께
3. **결정을 미룰 수 있게** — NFR을 모르겠으면 "기본 프로파일(MVP)"로 진행하고, 나중에 조정 가능하다는 안전장치

---

## 3. 타이밍 분석 — 각 결정이 언제 필요한가

구현 방식(통합 vs 분리)을 결정하려면 **각 결정이 흐름의 어느 시점에 필요한지**가 핵심이다.

### NFR requirements → application-design 이전에 필요

"99.99% 가용성이 필요하다"를 알면 컴포넌트 설계가 완전히 달라진다 (단일 서버 vs 이중화).
즉 NFR 수집은 설계의 **입력**이지, 설계의 **결과**가 아니다.

또한 NFR 요구사항이 workflow-planning의 접근법 선택에도 영향을 준다.
"높은 가용성 요구" → "application-design 포함 + Comprehensive 깊이" 같은 판단의 근거가 된다.

### NFR design → application-design 안에서 필요

반면 "99.99% 가용성을 **어떻게** 달성할 것인가" (액티브-액티브? 페일오버?)는
컴포넌트를 설계하면서 동시에 결정된다.
이걸 별도 스킬로 분리하면 같은 맥락을 두 번 로드하게 된다.

### Infrastructure design → application-design 이후에 필요

"알림 서비스, 사용자 서비스, API 게이트웨이가 있다"
→ 이걸 AWS에 어떻게 배치할지는 컴포넌트를 알아야 결정 가능하다.

---

## 4. 제안: 혼합 접근법

| 스킬 | 구현 방식 | 이유 |
|------|----------|------|
| **user-stories** | **독립 스킬** | requirements-analysis와 입출력이 명확히 구분됨. 조건부 포함 |
| **nfr-requirements** | **독립 스킬** | application-design의 **입력**이므로 반드시 이전에 실행. 질문 전략이 완전히 다름 (비개발자 맞춤) |
| **nfr-design** | **application-design 확장** | 컴포넌트 설계와 NFR 패턴 결정은 같은 맥락에서 이루어짐. Comprehensive 모드에서 활성화 |
| **infrastructure-design** | **독립 스킬** | application-design 이후에 필요 + 클라우드/온프렘/비용 등 완전히 다른 질문 영역 |

### 최종 INCEPTION 흐름

```
workspace-detection
  → requirements-analysis
  → (user-stories)            ← 조건부: 사용자 중심 도메인일 때
  → (nfr-requirements)        ← 조건부: 상용 배포 예정일 때
  → workflow-planning
  → (application-design)      ← Comprehensive 모드에서 NFR 패턴 결정 포함
  → (infrastructure-design)   ← 조건부: 상용 배포 예정일 때
  → (units-generation)
```

---

## 5. 비개발자를 위한 nfr-requirements 설계 방향

가장 어려운 부분이므로 좀 더 구체적으로:

### Phase 1: 프로파일 선택 (비개발자 친화)

```
"이 소프트웨어의 운영 환경은?"

A) MVP/프로토타입 — 기본값으로 충분, NFR 최소화
B) 소규모 운영 — 사용자 100명 이하, 기본 안정성
C) 중규모 운영 — 사용자 1000명+, 모니터링 필요
D) 대규모/엔터프라이즈 — 고가용성, 보안 컴플라이언스
```

### Phase 2: 프로파일 기반 맞춤 질문

선택한 프로파일에 따라 질문 범위가 달라진다:

- **MVP** → 질문 2~3개만 (핵심 보안, 데이터 백업)
- **소규모** → 질문 4~5개 (+ 응답 시간, 동시 접속)
- **중규모** → 질문 6~7개 (+ 모니터링, 장애 복구)
- **대규모** → 8개 카테고리 전체 순회

### Phase 3: 기본값 제시 + 조정

```
"프로파일 기반으로 다음 NFR을 권장합니다:
 - 응답 시간: 500ms 이내 (이유: 소규모 운영 기준 사용자 체감 임계점)
 - 가용성: 99.9% (이유: 월 43분 다운타임 허용, 소규모에 적합)
 - 데이터 백업: 일 1회 (이유: ...)

 조정이 필요한 항목이 있나요?"
```

비개발자는 **프로파일만 선택하면** 나머지는 합리적 기본값이 채워진다.

---

## 6. infrastructure-design 설계 방향

infrastructure-design도 비슷한 프로파일 기반 접근:

### Phase 1: 배포 대상 선택

```
"어디에 배포할 예정인가요?"

A) 클라우드 — AWS / GCP / Azure (자동 감지 또는 선택)
B) 컨테이너 — Docker / Kubernetes
C) 서버리스 — AWS Lambda / Cloud Functions
D) 온프레미스 — 자체 서버
E) 아직 모르겠음 → 컨테이너 기반 추천 (이식성 높음)
```

### Phase 2: NFR 프로파일 연계

nfr-requirements에서 수집한 프로파일(MVP/소규모/대규모)을 자동 참조:
- **MVP + 클라우드** → 단일 인스턴스 + RDS + S3
- **대규모 + 클라우드** → 로드밸런서 + Auto Scaling + 멀티 AZ + CDN

### Phase 3: 인프라 다이어그램 + IaC 참조

```
application-design.md의 컴포넌트 → 인프라 매핑:
- API Gateway → AWS API Gateway / ALB
- 사용자 서비스 → ECS Fargate / EC2
- 데이터베이스 → RDS PostgreSQL / DynamoDB
```

---

## 7. 결정이 필요한 사항

1. **혼합 접근법 동의 여부** — 독립 스킬 3개 (user-stories, nfr-requirements, infrastructure-design) + application-design 확장 1개 (nfr-design)
2. **nfr-requirements와 user-stories의 순서** — 위 흐름대로 user-stories → nfr-requirements? 아니면 병렬?
3. **4개를 한 설계 사이클로 진행할지, 2+2로 나눌지**
