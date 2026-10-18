#!/bin/bash
# tests/verify-change-6.sh
set -e

SKILL="skills/aidlc-systematic-debugging/SKILL.md"

# Check 1: STORE 섹션 존재
if ! grep -q '^## STORE 호출' "$SKILL"; then
  echo "FAIL: '## STORE 호출' section missing in $SKILL"
  exit 1
fi

# Check 2: 5 필드 모두 언급
for field in root_cause fix_summary regression_test test_result error_message; do
  if ! grep -q "$field=" "$SKILL"; then
    echo "FAIL: STORE field '$field' missing"
    exit 1
  fi
done

# Check 3: solution_verdict Return 필드 명시
if ! grep -q 'solution_verdict' "$SKILL"; then
  echo "FAIL: solution_verdict Return field missing"
  exit 1
fi

echo "PASS: Change 6 verified"
