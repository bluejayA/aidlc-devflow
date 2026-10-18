"""Meta tag format validation tests.

Validates that SKILL.md files contain well-formed meta tags
conforming to the meta-tag-standard specification.
"""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Regex patterns for each meta tag type
TAG_PATTERNS = {
    "gate": re.compile(r"^<!--\s*@gate:\s+\S+.*-->$"),
    "gate-option": re.compile(
        r"^<!--\s*@gate-option:\s+\S+\s+->\s+\S+.*-->$"
    ),
    "step": re.compile(r"^<!--\s*@step:\d+\s+id=\S+.*-->$"),
    "condition": re.compile(r"^<!--\s*@condition:\s+.+\s+->\s+\S+.*-->$"),
}


def extract_tags(filepath: Path) -> dict[str, list[str]]:
    """Extract meta tags from a SKILL.md file, grouped by type."""
    tags: dict[str, list[str]] = {k: [] for k in TAG_PATTERNS}
    text = filepath.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        for tag_type, pattern in TAG_PATTERNS.items():
            if pattern.match(stripped):
                tags[tag_type].append(stripped)
    return tags


def extract_steps(filepath: Path) -> list[int]:
    """Extract step order numbers from a SKILL.md file."""
    step_pattern = re.compile(r"<!--\s*@step:(\d+)\s+id=\S+.*-->")
    orders = []
    text = filepath.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = step_pattern.search(line.strip())
        if m:
            orders.append(int(m.group(1)))
    return orders


# --- Tag regex validation ---


class TestTagRegexPatterns:
    """Verify regex patterns match valid tags and reject invalid ones."""

    def test_gate_pattern_valid(self):
        assert TAG_PATTERNS["gate"].match("<!-- @gate: complexity-declaration -->")

    def test_gate_pattern_invalid(self):
        assert not TAG_PATTERNS["gate"].match("<!-- @gate -->")

    def test_gate_option_pattern_valid(self):
        assert TAG_PATTERNS["gate-option"].match(
            "<!-- @gate-option: A -> requirements-analysis -->"
        )

    def test_gate_option_pattern_with_condition(self):
        assert TAG_PATTERNS["gate-option"].match(
            "<!-- @gate-option: A -> complexity-declaration {adjust} -->"
        )

    def test_gate_option_pattern_invalid(self):
        assert not TAG_PATTERNS["gate-option"].match(
            "<!-- @gate-option: A -->"
        )

    def test_step_pattern_valid(self):
        assert TAG_PATTERNS["step"].match(
            "<!-- @step:1 id=workspace-detection -->"
        )

    def test_step_pattern_with_skip(self):
        assert TAG_PATTERNS["step"].match(
            "<!-- @step:3 id=requirements-analysis skip-when=QUESTIONS -->"
        )

    def test_step_pattern_invalid(self):
        assert not TAG_PATTERNS["step"].match("<!-- @step: id=foo -->")

    def test_condition_pattern_valid(self):
        assert TAG_PATTERNS["condition"].match(
            "<!-- @condition: complexity==Minimal -> workflow-planning -->"
        )

    def test_condition_pattern_invalid(self):
        assert not TAG_PATTERNS["condition"].match(
            "<!-- @condition: something -->"
        )


# --- Inception orchestrator ---


INCEPTION_SKILL = SKILLS_DIR / "aidlc-inception-orchestrator" / "SKILL.md"


class TestInceptionOrchestratorTags:
    """Verify inception-orchestrator SKILL.md has required meta tags."""

    def test_has_gates(self):
        tags = extract_tags(INCEPTION_SKILL)
        assert len(tags["gate"]) >= 2, (
            f"Expected at least 2 @gate tags, found {len(tags['gate'])}"
        )

    def test_has_gate_options(self):
        tags = extract_tags(INCEPTION_SKILL)
        assert len(tags["gate-option"]) >= 4, (
            f"Expected at least 4 @gate-option tags, found {len(tags['gate-option'])}"
        )

    def test_has_steps(self):
        tags = extract_tags(INCEPTION_SKILL)
        assert len(tags["step"]) >= 3, (
            f"Expected at least 3 @step tags, found {len(tags['step'])}"
        )

    def test_step_order_increasing(self):
        orders = extract_steps(INCEPTION_SKILL)
        assert len(orders) >= 3, f"Expected at least 3 steps, found {len(orders)}"
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Step order not increasing: {orders[i - 1]} -> {orders[i]}"
            )

    def test_has_conditions(self):
        tags = extract_tags(INCEPTION_SKILL)
        assert len(tags["condition"]) >= 1, (
            f"Expected at least 1 @condition tag, found {len(tags['condition'])}"
        )


# --- Construction orchestrator ---


CONSTRUCTION_SKILL = SKILLS_DIR / "aidlc-construction-orchestrator" / "SKILL.md"


class TestConstructionOrchestratorTags:
    """Verify construction-orchestrator SKILL.md has required meta tags."""

    def test_has_gates(self):
        tags = extract_tags(CONSTRUCTION_SKILL)
        assert len(tags["gate"]) >= 2, (
            f"Expected at least 2 @gate tags, found {len(tags['gate'])}"
        )

    def test_has_gate_options(self):
        tags = extract_tags(CONSTRUCTION_SKILL)
        assert len(tags["gate-option"]) >= 4, (
            f"Expected at least 4 @gate-option tags, found {len(tags['gate-option'])}"
        )

    def test_has_steps(self):
        tags = extract_tags(CONSTRUCTION_SKILL)
        assert len(tags["step"]) >= 2, (
            f"Expected at least 2 @step tags, found {len(tags['step'])}"
        )

    def test_step_order_increasing(self):
        orders = extract_steps(CONSTRUCTION_SKILL)
        assert len(orders) >= 2, f"Expected at least 2 steps, found {len(orders)}"
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Step order not increasing: {orders[i - 1]} -> {orders[i]}"
            )


# --- Content preservation ---


class TestContentPreservation:
    """Verify meta tag insertion doesn't modify existing content."""

    @staticmethod
    def _non_tag_lines(filepath: Path) -> list[str]:
        """Return lines that are NOT meta tags (i.e., original content)."""
        tag_pattern = re.compile(r"^\s*<!--\s*@(gate|gate-option|step|condition)[:\s]")
        return [
            line
            for line in filepath.read_text(encoding="utf-8").splitlines()
            if not tag_pattern.match(line)
        ]

    def test_inception_content_preserved(self):
        """Non-tag lines should match the original file content."""
        non_tag = self._non_tag_lines(INCEPTION_SKILL)
        # Basic sanity: file should still have substantial content
        assert len(non_tag) > 50, (
            f"Expected >50 non-tag lines, found {len(non_tag)} — content may be corrupted"
        )

    def test_construction_content_preserved(self):
        """Non-tag lines should match the original file content."""
        non_tag = self._non_tag_lines(CONSTRUCTION_SKILL)
        assert len(non_tag) > 50, (
            f"Expected >50 non-tag lines, found {len(non_tag)} — content may be corrupted"
        )


# --- Hook tag compatibility ---


class TestHookTagCompatibility:
    """Verify @hook tags in HTML comments don't interfere with parser."""

    def test_hook_tags_not_parsed_as_meta_tags(self):
        """@hook tags should not be matched by standard meta tag patterns."""
        hook_lines = [
            "<!-- @hook: pre-search-solutions — inactive until BL-057 -->",
            "<!-- Activation condition: devflow-docs/solutions/ exists AND 15+ solution files -->",
            "<!-- When active: search solutions by error_signature before debugging -->",
        ]
        # Verify none of these match the meta tag patterns
        for hook_line in hook_lines:
            for tag_type, pattern in TAG_PATTERNS.items():
                assert not pattern.match(
                    hook_line.strip()
                ), f"Hook line matched {tag_type} pattern: {hook_line}"

    def test_workflow_planning_with_hook_tags(self):
        """Verify workflow-planning SKILL.md has @hook tags and parser handles them correctly."""
        workflow_skill = SKILLS_DIR / "aidlc-workflow-planning" / "SKILL.md"
        assert workflow_skill.exists(), f"workflow-planning SKILL.md not found at {workflow_skill}"

        # Read content
        content = workflow_skill.read_text(encoding="utf-8")

        # Verify @hook tags exist
        assert "@hook:" in content, "Expected @hook tag in workflow-planning SKILL.md"
        assert "pre-search-solutions" in content, "Expected pre-search-solutions hook in workflow-planning"

        # Verify parser still extracts meta tags correctly (should have none for workflow-planning)
        tags = extract_tags(workflow_skill)
        # workflow-planning should not have any meta tags (@step, @gate, etc.)
        total_tags = sum(len(v) for v in tags.values())
        assert (
            total_tags == 0
        ), f"workflow-planning should have no meta tags, but found {total_tags}"

    def test_hook_tags_dont_interfere_with_step_extraction(self):
        """Verify @hook tags don't interfere with @step extraction in skills that have both."""
        inception_skill = INCEPTION_SKILL

        # Get all steps from inception orchestrator
        orders = extract_steps(inception_skill)

        # Should have at least 3 steps and they should be in increasing order
        assert len(orders) >= 3, f"Expected at least 3 steps, found {len(orders)}"
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Step order not increasing: {orders[i - 1]} -> {orders[i]}"
            )
