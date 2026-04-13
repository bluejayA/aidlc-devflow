#!/bin/bash
# tests/verify-hook-behavioral.sh
# Behavioral tests for post-tool-file-edit (execution-based, not grep-based).
# Complements verify-change-5.sh (script shape) with actual input/output validation.
set -e

REPO="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$REPO/hooks/post-tool-file-edit"
AUDIT="$REPO/devflow-docs/audit.md"

assert_unchanged() {
  local label="$1"
  local before="$2"
  local after
  after=$(wc -c < "$AUDIT" 2>/dev/null || echo 0)
  if [ "$after" = "$before" ]; then
    echo "PASS: $label (audit.md unchanged)"
  else
    echo "FAIL: $label (audit.md changed: $before → $after)"
    exit 1
  fi
}

assert_grew() {
  local label="$1"
  local before="$2"
  local after
  after=$(wc -c < "$AUDIT" 2>/dev/null || echo 0)
  if [ "$after" -gt "$before" ]; then
    echo "PASS: $label (audit.md grew $before → $after)"
  else
    echo "FAIL: $label (audit.md did not grow)"
    exit 1
  fi
}

run_hook() {
  local input="$1"
  printf '%s' "$input" | "$HOOK"
}

# Baseline
B=$(wc -c < "$AUDIT" 2>/dev/null || echo 0)

# === Test A: non-git cwd no-op ===
# Run hook in /tmp (not a git repo). Expect no write anywhere.
# Even with valid-looking whitelisted path, hook must exit without touching files.
(cd /tmp && run_hook '{"tool_input":{"file_path":"/tmp/not-a-repo/docs/foo.md"}}')
assert_unchanged "non-git cwd no-op" "$B"
[ ! -f /tmp/devflow-docs/audit.md ] && echo "PASS: no /tmp/devflow-docs/ created" \
  || { echo "FAIL: /tmp/devflow-docs/ created"; exit 1; }

# === Test B: outside-root absolute path no-op ===
run_hook '{"tool_input":{"file_path":"/etc/passwd"}}'
assert_unchanged "outside-root no-op" "$B"

# === Test C: newline in REL_PATH → sanitization reject ===
# Path with literal newline: hook should skip to protect audit integrity.
INJECT_JSON=$(printf '{"tool_input":{"file_path":"%s/docs/foo\\nbar.md"}}' "$REPO")
run_hook "$INJECT_JSON"
assert_unchanged "newline in path rejected" "$B"

# === Test D: DEVFLOW_ROOT validation ===
B=$(wc -c < "$AUDIT" 2>/dev/null || echo 0)

# D.1: relative path → reject
(cd /tmp && DEVFLOW_ROOT="relative/path" run_hook '{"tool_input":{"file_path":"/tmp/foo/docs/x.md"}}')
assert_unchanged "DEVFLOW_ROOT relative rejected" "$B"

# D.2: root / → reject
(cd /tmp && DEVFLOW_ROOT="/" run_hook '{"tool_input":{"file_path":"/tmp/foo/docs/x.md"}}')
assert_unchanged "DEVFLOW_ROOT = / rejected" "$B"

# D.3: non-existent dir → reject
(cd /tmp && DEVFLOW_ROOT="/nonexistent/path/xyz" run_hook '{"tool_input":{"file_path":"/tmp/foo/docs/x.md"}}')
assert_unchanged "DEVFLOW_ROOT nonexistent rejected" "$B"

# D.4: empty string in NON-git cwd → git fallback fails, exit 0 (fail-closed)
# (이전 버전은 git cwd에서 테스트해 fall-through 동작이 git success로 가려졌음.
#  non-git cwd에서 테스트해야 `[ -n "" ]` false + git failure = exit 0을 실제 검증)
(cd /tmp && DEVFLOW_ROOT="" run_hook '{"tool_input":{"file_path":"/tmp/foo/docs/x.md"}}')
assert_unchanged "DEVFLOW_ROOT empty in non-git cwd → fail-closed" "$B"

# D.5: DEVFLOW_ROOT file-instead-of-dir → reject
TMPFILE=$(mktemp)
(cd /tmp && DEVFLOW_ROOT="$TMPFILE" run_hook '{"tool_input":{"file_path":"/tmp/foo/docs/x.md"}}')
assert_unchanged "DEVFLOW_ROOT file-instead-of-dir rejected" "$B"
rm -f "$TMPFILE"

# D.6: valid override to existing directory (using $REPO itself as test)
B=$(wc -c < "$AUDIT" 2>/dev/null || echo 0)
(cd /tmp && DEVFLOW_ROOT="$REPO" run_hook "{\"tool_input\":{\"file_path\":\"$REPO/README.md\"}}")
assert_grew "DEVFLOW_ROOT valid override" "$B"

# Clean test pollution
rm -rf /tmp/devflow-docs 2>/dev/null || true

echo ""
echo "=== ALL BEHAVIORAL TESTS PASSED ==="
