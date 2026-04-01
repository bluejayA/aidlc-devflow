"""Shared constants for SKILL.md test infrastructure.

Centralizes values that change when skills are added or modified,
making the update point explicit and reducing missed-update risk.
"""

# Logical actions: gate-option targets that represent workflow actions
# rather than graph nodes (e.g., 'next-unit', 'INCEPTION-complete').
# Update this set when adding new logical actions to orchestrator SKILL.md files.
LOGICAL_ACTIONS = {
    "next-unit",
    "worktree-create",
    "inception-routing",
    "code-generation-plan",
    "code-generation-generate",
}

# External plugin references: gate-option targets that point to skills
# from external plugins (not part of this plugin's skills/ directory).
# Update this set when adding new external plugin references to orchestrator SKILL.md files.
EXTERNAL_PLUGIN_REFS = {
    "reverse-engineering",
}
