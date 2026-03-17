# Code Quality Reviewer Prompt

> Spec compliance review를 통과한 후에만 실행할 것.

## Purpose

구현의 코드 품질을 검증한다. Spec 준수는 이미 확인됨 — 여기서는 구현이 잘 만들어졌는지만 본다.

## Context
- **구현 내용**: {WHAT_WAS_IMPLEMENTED}
- **요구사항**: {PLAN_OR_REQUIREMENTS}
- **변경 범위**: {BASE_SHA}..{HEAD_SHA}

## Review Focus

1. **코드 품질**: 가독성, 네이밍, 구조
2. **테스트 품질**: 커버리지, 경계 케이스, 테스트 격리
3. **아키텍처**: 기존 패턴 준수, 적절한 추상화 수준
4. **보안 (OWASP Top 10 기준)**:
   - Injection (SQL, Command, XSS, Path Traversal)
   - 인증/인가 결함 (하드코딩된 시크릿, 권한 검증 누락)
   - 민감 데이터 노출 (로그에 비밀번호/토큰, 평문 저장)
   - 입력 검증 부재 (사용자 입력 미검증, 타입/범위 체크 누락)
   - 안전하지 않은 설정 (CORS *, debug=True, CSRF 비활성)
5. **언어별 주의사항**:
   - Python: `eval()`/`exec()`, `pickle` 역직렬화, subprocess `shell=True`
   - Go: 에러 무시(`_ = err`), goroutine race condition
   - Rust: 불필요한 `unsafe`, `.unwrap()` 남용
   - Swift: force unwrap(`!`) 남용, 키체인 미사용 민감 데이터
   - Java/Spring: SQL 문자열 연결, `@CrossOrigin("*")`, 부적절한 예외 노출

## Issue Classification

- **Critical**: 반드시 수정 (버그, 보안 취약점, 데이터 손실 위험)
- **Important**: 수정 권장 (성능, 유지보수성, 테스트 갭)
- **Minor**: 선택적 (스타일, 네이밍 개선)

## Report Format

**Strengths**: [잘된 점]
**Issues**: [Critical/Important/Minor 분류별 목록]
**Assessment**: ✅ Approved | ❌ Requires Changes (Critical/Important 이슈 시)
