#!/bin/bash
# tests/verify-change-4.sh
set -e

# 1. 모든 aidlc-* skill이 skill_nature + lifecycle 보유
MISSING_NATURE=$(grep -L 'skill_nature:' skills/aidlc-*/SKILL.md || true)
if [ -n "$MISSING_NATURE" ]; then
  echo "FAIL: skill_nature missing in:"
  echo "$MISSING_NATURE"
  exit 1
fi

MISSING_LIFECYCLE=$(grep -L 'lifecycle:' skills/aidlc-*/SKILL.md || true)
if [ -n "$MISSING_LIFECYCLE" ]; then
  echo "FAIL: lifecycle missing in:"
  echo "$MISSING_LIFECYCLE"
  exit 1
fi

# 2. compensation + hybrid 15개에 model_dependency 필수
COMP_HYBRID=(
  aidlc-verification-before-completion aidlc-test-driven-development
  aidlc-systematic-debugging aidlc-build-and-test
  aidlc-code-generation aidlc-executing-plans
  aidlc-application-design aidlc-functional-design
  aidlc-units-generation aidlc-user-stories aidlc-nfr-requirements
  aidlc-receiving-code-review aidlc-requesting-code-review
  aidlc-workflow-planning aidlc-subagent-driven-development
)
for skill in "${COMP_HYBRID[@]}"; do
  f="skills/$skill/SKILL.md"
  if ! grep -q 'model_dependency:' "$f"; then
    echo "FAIL: model_dependency missing in $f"
    exit 1
  fi
done

# 3. hybrid 11개에 amplification_notes 필수
HYBRID=(
  aidlc-code-generation aidlc-executing-plans
  aidlc-application-design aidlc-functional-design
  aidlc-units-generation aidlc-user-stories aidlc-nfr-requirements
  aidlc-receiving-code-review aidlc-requesting-code-review
  aidlc-workflow-planning aidlc-subagent-driven-development
)
for skill in "${HYBRID[@]}"; do
  f="skills/$skill/SKILL.md"
  if ! grep -q 'amplification_notes:' "$f"; then
    echo "FAIL: amplification_notes missing in $f"
    exit 1
  fi
done

# 4. _utils 3개에 skill_nature: null + lifecycle
for util in devflow-state devflow-audit devflow-solutions; do
  f="skills/_utils/$util/SKILL.md"
  if ! grep -q 'skill_nature: null' "$f"; then
    echo "FAIL: infrastructure skill_nature: null missing in $f"
    exit 1
  fi
  if ! grep -q 'lifecycle:' "$f"; then
    echo "FAIL: lifecycle missing in $f"
    exit 1
  fi
done

echo "PASS: Change 4 verified"
