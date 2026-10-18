#!/bin/bash
# tests/verify-change-3.sh
set -e

PATTERN_FILES=(
  skills/_shared/patterns/*.md
  skills/_shared/reviewers/*.md
  skills/_shared/devflow-conventions.md
  skills/_shared/gate-patterns.md
  skills/_shared/import-review-protocol.md
  skills/_shared/tdd-protocol.md
)

REQUIRED_FIELDS=(type applies_to status source last_validated)

MISSING=()
for f in "${PATTERN_FILES[@]}"; do
  [ -f "$f" ] || continue
  for field in "${REQUIRED_FIELDS[@]}"; do
    if ! grep -qE "^${field}:" "$f"; then
      MISSING+=("$f:$field")
    fi
  done
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "FAIL: missing frontmatter fields:"
  printf '%s\n' "${MISSING[@]}"
  exit 1
fi

echo "PASS: Change 3 verified (33 files frontmatter complete)"
