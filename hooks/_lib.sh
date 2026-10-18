# shared helpers for aidlc v2 hooks. sourced, not executed.
# reads hook JSON from stdin into $HOOK_JSON and exposes a few fields.
HOOK_JSON=$(cat)
field() { printf '%s' "$HOOK_JSON" | python3 -c '
import json,sys
d=json.load(sys.stdin); k=sys.argv[1].split(".")
for p in k:
    d=d.get(p,"") if isinstance(d,dict) else ""
print(d if isinstance(d,str) else json.dumps(d))' "$1" 2>/dev/null; }
CWD=$(field cwd); [ -n "$CWD" ] || CWD=$PWD
SESSION=$(field session_id); [ -n "$SESSION" ] || SESSION=nosession
SCRATCH=$(field scratchpad_dir); [ -n "$SCRATCH" ] || SCRATCH="${TMPDIR:-/tmp}/devflow-$SESSION"
mkdir -p "$SCRATCH" 2>/dev/null || true
TEST_MARKER="$SCRATCH/devflow-tests-ran"
# gate only inside a devflow project
is_devflow_project() { [ -d "$CWD/devflow-docs" ] || [ -d "$CWD/.devflow" ]; }
deny() { # $1 = reason
  python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":sys.argv[1]}},ensure_ascii=False))' "$1"
  exit 0
}
