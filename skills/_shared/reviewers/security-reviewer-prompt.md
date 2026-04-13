---
type: pattern
applies_to: [aidlc-requesting-code-review]
status: active
source: manual
last_validated: 2026-04-13
---

# Security & Edge-case Reviewer Prompt

> Standard 이상 depth에서 실행. Stage 2 (Code Quality) 통과 후 dispatch. Comprehensive에서는 Stage 4 (Maintainability)와 병렬 실행.

## Purpose

구현 코드의 보안 취약점과 엣지케이스를 심층 분석한다. 표면적 체크리스트가 아닌, 실제 공격 벡터와 경계 상황을 기준으로 검증한다.

## Context
- **구현 내용**: {WHAT_WAS_IMPLEMENTED}
- **요구사항**: {PLAN_OR_REQUIREMENTS}
- **변경 범위**: {BASE_SHA}..{HEAD_SHA}

## Review Focus

### 1. OWASP Top 10 심층 분석
- **Injection**: SQL, Command, XSS, Path Traversal — 입력이 쿼리/명령/출력에 도달하는 경로 추적
- **인증/인가 결함**: 하드코딩된 시크릿, 권한 검증 누락, 세션 관리 취약점
- **민감 데이터 노출**: 로그에 비밀번호/토큰, 평문 저장, 불필요한 데이터 반환
- **입력 검증 부재**: 사용자 입력 미검증, 타입/범위 체크 누락, allowlist vs denylist
- **안전하지 않은 설정**: CORS *, debug=True, CSRF 비활성, 과도한 권한
- **기본 보안 체크** (code-quality에서 이관): Injection, 하드코딩된 시크릿/크레덴셜, 안전하지 않은 설정

### 2. 언어별 보안 주의사항
- **Python**: `eval()`/`exec()`, `pickle` 역직렬화, subprocess `shell=True`, `yaml.load()` without SafeLoader
- **Go**: 에러 무시(`_ = err`), goroutine race condition, unsafe 패키지 사용
- **Rust**: 불필요한 `unsafe`, `.unwrap()` 남용, 검증 없는 외부 입력
- **Swift**: force unwrap(`!`) 남용, 키체인 미사용 민감 데이터, ATS 예외
- **Java/Spring**: SQL 문자열 연결, `@CrossOrigin("*")`, 부적절한 예외 노출, 역직렬화 취약점

### 3. 논리 오류
- 조건문 누락: 특정 상태 조합에서 예상치 못한 경로
- 경계값 처리: off-by-one, 오버플로우, 빈 컬렉션, null/undefined
- Race condition: 공유 상태 동시 접근, TOCTOU (Time-of-Check-to-Time-of-Use)
- 상태 일관성: 부분 실패 시 상태 롤백 여부

### 4. 엣지케이스
- 빈 입력 / 극단적 대량 데이터
- 동시 요청 / 타임아웃 / 네트워크 단절
- 유니코드, 특수문자, 멀티바이트 문자열
- 시간대(timezone), 윤년, 자정 경계

### 5. 데이터 흐름 분석
- 외부 입력 → 내부 처리 → 출력까지 민감 데이터 전파 경로
- 신뢰 경계(trust boundary)를 넘는 데이터에 대한 검증 여부
- 에러 메시지에 내부 구현 정보 노출 여부

## Rubric

Score each item using the Security Reviewer rubric from the schema:

| Item | How to Assess |
|------|--------------|
| OWASP Compliance | Check applicable OWASP items against implementation |
| Auth/Authz Validation | Verify all auth checks are present and correct |
| Input Validation Coverage | Trace external inputs to ensure validation at trust boundaries |

## Issue Classification

- **Critical**: 반드시 수정 (보안 취약점, 데이터 손실/유출 위험, 악용 가능한 논리 오류)
- **Important**: 수정 권장 (잠재적 엣지케이스 미처리, 방어적 프로그래밍 부족)
- **Minor**: 선택적 (보안 강화 제안, 추가 검증 권장)

## Output Format

Read `_shared/patterns/review-feedback-schema.md` and follow the output template exactly. Use the Security Reviewer rubric in the Score table. Include Threat Surface analysis in the Context section. Report Verdict as PASS, CONDITIONAL, or FAIL per the schema criteria.
