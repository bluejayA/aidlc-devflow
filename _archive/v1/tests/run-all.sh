#!/usr/bin/env bash
# run-all.sh — Run the complete AIDLC skill test suite
#
# Usage: bash tests/run-all.sh
# Exit code: 0 = all passed, 1 = failure

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "=== AIDLC Skill Test Suite ==="
echo ""

# Step 1: Parse SKILL.md files → JSON graphs
echo "--- Step 1: Parsing SKILL.md files ---"
if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js is not installed. Install it to run the parser."
    exit 1
fi

node "$SCRIPT_DIR/parse-skills.js"
echo ""

# Step 2: Run pytest (L1 + L2 + L3)
echo "--- Step 2: Running pytest (L1/L2/L3) ---"
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv is not installed. Install it to run pytest."
    exit 1
fi

uv run pytest "$SCRIPT_DIR/" -v
echo ""

echo "=== All tests passed ==="
