#!/bin/bash
# tests/verify-change-2.sh
set -e

SKILL="skills/aidlc-construction-orchestrator/SKILL.md"

# Check 1: STORE 직접 호출 없음 (devflow-solutions STORE( 패턴)
if grep -qE 'devflow-solutions.*STORE\s*\(' "$SKILL"; then
  echo "FAIL: direct STORE call still present in $SKILL"
  grep -nE 'devflow-solutions.*STORE\s*\(' "$SKILL"
  exit 1
fi

# Check 2: solution_verdict 소비 언급
if ! grep -q 'solution_verdict' "$SKILL"; then
  echo "FAIL: solution_verdict not consumed in K-gate"
  exit 1
fi

echo "PASS: Change 2 verified"
