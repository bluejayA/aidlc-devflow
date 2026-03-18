"""Shared constants for SKILL.md test infrastructure.

Centralizes values that change when skills are added or modified,
making the update point explicit and reducing missed-update risk.
"""

# Logical actions: gate-option targets that represent workflow actions
# rather than graph nodes (e.g., 'next-unit', 'INCEPTION-complete').
# Update this set when adding new logical actions to orchestrator SKILL.md files.
LOGICAL_ACTIONS = {
    "next-unit",
    "branch-name-confirm",
    "inception-routing",
    "code-generation-plan",
    "code-generation-generate",
}
