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
4. **에러 핸들링**: 적절한 에러 처리, 실패 경로의 명확성, 에러 전파 일관성
5. **DRY**: 불필요한 중복 없음, 적절한 추상화 수준
6. **기본 보안 체크** (명백한 취약점만 — 심층 분석은 Stage 3 전담):
   - Injection (SQL, Command, XSS) — 외부 입력이 쿼리/명령/출력에 직접 들어가는 경우
   - 하드코딩된 시크릿/크레덴셜
   - 안전하지 않은 설정 (debug=True, CORS * 등)

## Issue Classification

- **Critical**: 반드시 수정 (버그, 명백한 보안 취약점, 데이터 손실 위험)
- **Important**: 수정 권장 (성능, 유지보수성, 테스트 갭)
- **Minor**: 선택적 (스타일, 네이밍 개선)

## Report Format

**Strengths**: [잘된 점]
**Issues**: [Critical/Important/Minor 분류별 목록]
**Assessment**: ✅ Approved | ❌ Requires Changes (Critical/Important 이슈 시)
