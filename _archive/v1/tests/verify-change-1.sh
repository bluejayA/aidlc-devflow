#!/bin/bash
# tests/verify-change-1.sh
set -e

# Check 1: legacy file should NOT exist
if [ -f "devflow-docs/devflow-audit.md" ]; then
  echo "FAIL: devflow-docs/devflow-audit.md still exists"
  exit 1
fi

# Check 2: no stale references in md/py (excluding historical context blocks)
STALE=$(rg 'devflow-audit\.md' --type md --type py --glob '!docs/research/knowledgesystem/**' --glob '!docs/plans/2026-04-13-knowledge-system-phase1-plan.md' || true)
if [ -n "$STALE" ]; then
  echo "FAIL: stale devflow-audit.md references found:"
  echo "$STALE"
  exit 1
fi

echo "PASS: Change 1 verified"
