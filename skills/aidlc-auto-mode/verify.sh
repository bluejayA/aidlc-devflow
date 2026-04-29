#!/bin/bash
# auto-mode Layer 1 검증 스크립트
# SKILL.md 수정 후 실행하여 구조적 정합성 확인

set -euo pipefail

SKILL="skills/aidlc-auto-mode/SKILL.md"
ERRORS=0

echo "=== auto-mode Layer 1 Verification ==="

# 1. 줄 수 확인 (skill-writing-guide L60: 500줄은 목표).
# BL-100~104 정합성 fix를 외부 분리 후(BL-105) 520 한도로 sustainable 자리.
# 한도 무한 상향은 안티패턴 (BL-105 issue 참조). 추가 정합 fix는 외부 분리로 처리.
LINES=$(wc -l < "$SKILL")
if [ "$LINES" -gt 520 ]; then
  echo "FAIL: SKILL.md is $LINES lines (max 520 — BL-105 정책)"
  ERRORS=$((ERRORS + 1))
else
  echo "PASS: SKILL.md is $LINES lines"
fi

# 2. 필수 섹션 존재 확인
for SECTION in "## On Activation" "## Phase 1" "## Phase 2" "## State Management" "## Error Handling" "## Session Resume" "## Trigger"; do
  if grep -q "$SECTION" "$SKILL"; then
    echo "PASS: Section '$SECTION' found"
  else
    echo "FAIL: Section '$SECTION' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 3. 리뷰 피드백으로 추가된 섹션 확인
for SECTION in "## Examples" "## Troubleshooting"; do
  if grep -q "$SECTION" "$SKILL"; then
    echo "PASS: Section '$SECTION' found"
  else
    echo "FAIL: Section '$SECTION' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 4. frontmatter 필수 필드
for FIELD in "invoke_mode: user-invocable" "return_behavior: stop-with-gate"; do
  if grep -q "$FIELD" "$SKILL"; then
    echo "PASS: Frontmatter '$FIELD' found"
  else
    echo "FAIL: Frontmatter '$FIELD' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 5. 화이트리스트 필드 언급 확인
for FIELD in "Current Phase" "Current Stage" "Complexity" "Selected Approach" "Approved Stages"; do
  if grep -q "$FIELD" "$SKILL"; then
    echo "PASS: State field '$FIELD' referenced"
  else
    echo "FAIL: State field '$FIELD' not referenced"
    ERRORS=$((ERRORS + 1))
  fi
done

# 6. 서킷 브레이커 언급
if grep -q "서킷 브레이커\|circuit breaker\|리트라이 상한" "$SKILL"; then
  echo "PASS: Circuit breaker defined"
else
  echo "FAIL: Circuit breaker not found"
  ERRORS=$((ERRORS + 1))
fi

# 7. 리뷰 관련 섹션 확인
for SECTION in "INCEPTION 리뷰" "CONSTRUCTION 리뷰" "requesting-code-review"; do
  if grep -q "$SECTION" "$SKILL"; then
    echo "PASS: Review section '$SECTION' found"
  else
    echo "FAIL: Review section '$SECTION' missing"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
echo "=== Results: $ERRORS error(s) ==="
exit $ERRORS
