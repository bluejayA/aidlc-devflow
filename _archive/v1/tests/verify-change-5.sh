#!/bin/bash
# tests/verify-change-5.sh
set -e

HOOK="hooks/post-tool-file-edit"
CONFIG="hooks/hooks.json"

# Check 1: hook script exists + executable
if [ ! -f "$HOOK" ]; then
  echo "FAIL: $HOOK does not exist"
  exit 1
fi
if [ ! -x "$HOOK" ]; then
  echo "FAIL: $HOOK not executable"
  exit 1
fi

# Check 2: hooks.json에 PostToolUse 블록
if ! grep -q 'PostToolUse' "$CONFIG"; then
  echo "FAIL: PostToolUse block missing in $CONFIG"
  exit 1
fi

# Check 3: hook script에 exclusion + whitelist 로직
if ! grep -q 'tests/' "$HOOK"; then
  echo "FAIL: tests/ exclusion missing"
  exit 1
fi
if ! grep -q 'devflow-docs/.archive/' "$HOOK"; then
  echo "FAIL: .archive/ exclusion missing"
  exit 1
fi
if ! grep -q '## Last Updated' "$HOOK"; then
  echo "FAIL: Last Updated soft-save logic missing"
  exit 1
fi

echo "PASS: Change 5 verified"
